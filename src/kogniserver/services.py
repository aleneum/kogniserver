import logging
import copy

import rsb
from rsb.converter import PredicateConverterList, Converter
from threading import Lock
from numbers import Integral, Real

from .pubsub import PubSubBridge
from .rpc import RPCBridge


class Forwarder(Converter):
    def __init__(self):
        super(Forwarder, self).__init__(bytearray, tuple, '.*')

    def serialize(self, data):
        return bytearray(data[1]), data[0]

    def deserialize(self, data, wireSchema):
        return wireSchema, data


def get_mapping(ob):
    if isinstance(ob, rsb.converter.DoubleConverter):
        return lambda data_type: issubclass(data_type, Real) and not issubclass(data_type, Integral)
    elif isinstance(ob, rsb.converter.Int64Converter):
        return lambda data_type: issubclass(data_type, Integral) and not issubclass(data_type, bool)
    else:
        return lambda data_type, d_type=ob.getDataType(): data_type == d_type


def create_rsb_config():
    rsb_conf = copy.deepcopy(rsb.getDefaultParticipantConfig())
    trans = rsb_conf.getTransports()

    conv = Forwarder()
    conv_list = PredicateConverterList(bytearray)
    conv_list.addConverter(conv,
                           dataTypePredicate=lambda data_type: data_type == tuple,
                           wireSchemaPredicate=lambda wire_schema: wire_schema.startswith('.'))

    for t in trans:
        convs = rsb.convertersFromTransportConfig(t)
        for c in convs.getConverters().values():
            conv_list.addConverter(c, dataTypePredicate=get_mapping(c))

        c = rsb.converter.StringConverter()
        conv_list.addConverter(c, get_mapping(c))
        t.converters = conv_list
    return rsb_conf


class SessionHandler(object):

    def __init__(self, wamp_session, log_level=logging.WARNING):
        logging.basicConfig()
        logging.getLogger().setLevel(log_level)
        logging.getLogger("rsb").setLevel(logging.ERROR)

        self.wamp_session = wamp_session
        self.scopes = {}
        self.lock = Lock()
        self.rsb_conf = create_rsb_config()

    def register_scope(self, rsb_scope, message_type):
        logging.info("trying to register on scope %s with message type %s" %
                     (rsb_scope, message_type))

        with self.lock:
            if rsb_scope not in self.scopes:
                b = PubSubBridge(rsb_scope, self.rsb_conf, self.wamp_session, message_type)
                self.scopes[rsb_scope] = b
                logging.debug('Scope %s has been registered' % rsb_scope)
                msg = "Scope registered"
            else:
                logging.debug('Scope %s exists' % rsb_scope)
                msg = "Scope already exists"
        return msg

    # This will only work for primitive types!
    def call_rpc(self, rsb_scope, method, payload, type_in, type_out):
        if rsb_scope not in self.scopes:
            self.scopes[rsb_scope] = RPCBridge(rsb_scope, self.rsb_conf)
        if method not in self.scopes[rsb_scope].converters:
            self.scopes[rsb_scope].add_method(method, type_in, type_out)
        logging.info("calling {0} on server {1}".format(method, rsb_scope))
        return self.scopes[rsb_scope].call(method, payload)

    def quit(self):
        logging.info("quitting session...")
        for bridge in self.scopes.values():
            bridge.deactivate()
