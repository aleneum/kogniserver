import logging
import base64
import rsb
from rsb import Event

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class RPCConverter(object):

    def __init__(self, scope, type_in, type_out):
        self.scope = scope
        self.parse = None
        self.prepare = None
        self.type_in = None
        self.type_out = None

        if type_in in RPCBridge.basic_types:
            self.parse = self.parse_primitive
            self.type_in = RPCBridge.basic_types[type_in]
        else:
            self.parse = self.parse_bytearray
            self.type_in = str('.' + type_in)

        if type_out in RPCBridge.basic_types:
            self.prepare = self.prepare_primitive
            self.type_out = RPCBridge.basic_types[type_out]
        else:
            self.prepare = self.prepare_bytearray
            self.type_out = str('.' + type_out)

    def prepare_bytearray(self, event):
        try:
            msg = '\0' + base64.b64encode(event.data[1]).decode('ascii')
            return msg
        except Exception as e:
            logger.error("Error while receiving rst data: %s" % str(e))

    def prepare_primitive(self, event):
        try:
            return self.type_out(event.data)
        except Exception as e:
            logger.error("Error while receiving primitive data: %s" % str(e))

    def parse_bytearray(self, data):
        try:
            binary_data = bytearray(base64.b64decode(data[1:]))
            event = Event(scope=self.scope,
                          data=(self.type_in, binary_data), type=tuple)
            return event
        except Exception as e:
            logger.error("Error while sending rst data: %s" % str(e))

    def parse_primitive(self, data):
        try:
            payload = self.type_in(data)
            event = Event(scope=self.scope, data=payload, type=type(payload))
            return event
        except Exception as e:
            logger.error("Error while sending primitive data: %s" % str(e))


class RPCBridge(object):
    basic_types = {'integer': int, 'float': float, 'string': lambda s: s, 'bool': bool}

    def __init__(self, scope, config):
        self.scope = scope
        self.remote = rsb.createRemoteServer(scope, config=config)
        self.converters = {}

    def add_method(self, name, type_in, type_out):
        if name not in self.converters:
            self.converters[name] = RPCConverter(self.scope + "/" + name, type_in, type_out)

    def call(self, name, payload):
        if name not in self.converters:
            raise ValueError('Method {0} not known.'.format(name))
        method = getattr(self.remote, name)
        converter = self.converters[name]
        res = method.async(converter.parse(payload)).get(timeout=5)
        return converter.prepare(res)

    def deactivate(self):
        logger.info("Shutting down rpc...")
        self.remote.deactivate()
