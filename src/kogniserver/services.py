import sys
import base64
import logging
import copy

import rsb
from rsb.converter import PredicateConverterList, SchemaAndByteArrayConverter
from rsb import Event

from rsb.protocol.introspection.Hello_pb2 import Hello
from rsb.protocol.introspection.Bye_pb2 import Bye


class Bridge(object):
    basic_types = {'integer': int, 'float': float, 'string': str, 'bool': bool}

    def __init__(self, rsb_scope, wamp, message_type):
        logging.info("register scopes:")
        self.rsb_scope = rsb_scope
        self.wamp_scope = rsb_scope[1:].replace('/', '.')
        self.converter = None
        self.skipNext = False;
        logging.info("RSB Scope %s" % self.rsb_scope)
        logging.info("WAMP Scope is %s" % self.wamp_scope)
        self.wamp = wamp
        self.wamp_listener = self.wamp.subscribe(self.on_wamp_message, self.wamp_scope)
        if message_type in Bridge.basic_types:
            self.wamp_callback = self.send_primitive_data
            self.rsb_callback = self.on_primitive_message
            self.rsb_type = Bridge.basic_types[message_type]
        else:
            self.wamp_callback = self.send_rst
            self.rsb_callback = self.on_bytearray_message
            self.rsb_type = str('.' + message_type)
        self.rsb_listener = rsb.createListener(self.rsb_scope)
        self.rsb_listener.addHandler(self.rsb_callback)
        self.rsb_publisher = rsb.createInformer(self.rsb_scope)

    def on_bytearray_message(self, event):
        if 'wamp' in event.metaData.userInfos:
            logging.debug("received OWN rsb bytearray on %s, skipping..." % self.rsb_scope)
            return
        logging.debug('received rsb bytearray on %s' % self.rsb_scope)
        logging.debug('event length %d' % len(event.data))
        logging.debug('sent to %s' %self.wamp_scope)
        try:
            msg = '\0' + base64.b64encode(event.data).decode('ascii')
            self.wamp.publish(self.wamp_scope, msg)
        except Exception as e:
            logging.error(e)
            sys.exit(1)

    def on_primitive_message(self, event):
        if 'wamp' in event.metaData.userInfos:
            logging.debug("received OWN rsb primitive on %s, skipping..." % self.rsb_scope)
            return
        logging.debug("received rsb primtive [%s] on %s" % (str(event.data[1]), self.rsb_scope))
        logging.debug("sent to %s" % self.wamp_scope)
        self.wamp.publish(self.wamp_scope, self.rsb_type(event.data[1]))

    def send_rst(self, event):
        try:
            logging.info("send rst message to %s" % self.rsb_scope)
            binary_data = bytearray(base64.b64decode(event[1:]))
            ev = Event(scope=self.rsb_publisher.getScope(),
                       data=(self.rsb_type, binary_data),
                       type=tuple,
                       userInfos={'wamp': ''})
            self.rsb_publisher.publishEvent(ev)
        except Exception as e:
            logging.error(e)
            sys.exit(1)

    def send_primitive_data(self, event):
        try:
            logging.info("send primitive message [%s] message to %s" % (str(event),self.rsb_scope))
            self.rsb_publisher.publishData(self.rsb_type(event),
                                           userInfos={'wamp':''})
        except Exception as e:
            logging.error(e)
            sys.exit(1)

    def on_wamp_message(self, event):
        logging.debug('Received wamp message on %s' % self.wamp_scope)
        self.wamp_callback(event)

    def shutdown(self):
        logging.info("Shutting down bridge...")
        self.rsb_listener.deactivate()
        if self.rsb_publisher is not False:
            self.rsb_publisher.deactivate()


class SessionHandler(object):

    def __init__(self, wamp_session, log_level=logging.WARNING):
        logging.basicConfig()
        logging.getLogger().setLevel(log_level)
        logging.getLogger("rsb").setLevel(logging.ERROR)

        self.wamp_session = wamp_session
        self.scopes = {}
        rsb_conf = copy.deepcopy(rsb.getDefaultParticipantConfig())
        trans = rsb_conf.getTransports()
        conv = SchemaAndByteArrayConverter()
        conv_list = PredicateConverterList(bytearray)
        conv_list.addConverter(conv,
                               wireSchemaPredicate=lambda wireSchema: not wireSchema.startswith('rsb.protocol.introspection')
                               )

        # register introspection types
        for clazz in [Hello, Bye]:
            converter = rsb.converter.ProtocolBufferConverter(messageClass=clazz)
            conv_list.addConverter(converter)

        for t in trans:
            t.converters = conv_list

        rsb.setDefaultParticipantConfig(rsb_conf)

    def register_scope(self, rsb_scope, message_type):
        logging.info("trying to register on scope %s with message type %s" %
                     (rsb_scope, message_type))

        if rsb_scope not in self.scopes:
            b = Bridge(rsb_scope, self.wamp_session, message_type)
            self.scopes[rsb_scope] = b
            return "Scope registered"
        return "Scope already exists"

    def quit(self):
        logging.info("quitting session...")
        for bridge in self.scopes.values():
            bridge.shutdown()
