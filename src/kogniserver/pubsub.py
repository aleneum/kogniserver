import logging
import base64
import rsb
from rsb import Event
from six import string_types

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class PubSubBridge(object):
    basic_types = {'integer': int, 'float': float, 'string': lambda s: s, 'bool': bool}
    RSB_TO_WAMP = 1
    WAMP_TO_RSB = 2
    BIDIRECTIONAL = 3

    def __init__(self, rsb_scope, rsb_config, wamp, message_type, mode=BIDIRECTIONAL, wamp_scope=None):
        logger.info("register scopes:")
        self.mode = mode
        self.rsb_scope = rsb_scope
        self.wamp_scope = rsb_scope[1:].replace('/', '.') if wamp_scope is None else wamp_scope
        self.converter = None
        self.skipNext = False
        self.rsb_publisher = None
        self.rsb_listener = None
        logger.info("RSB Scope %s" % self.rsb_scope)
        logger.info("WAMP Scope is %s" % self.wamp_scope)
        self.wamp = wamp

        if message_type in PubSubBridge.basic_types:
            self.wamp_callback = self.send_primitive_data
            self.rsb_callback = self.on_primitive_message
            self.rsb_type = PubSubBridge.basic_types[message_type]
        else:
            self.wamp_callback = self.send_rst
            self.rsb_callback = self.on_bytearray_message
            self.rsb_type = str('.' + message_type)

        # RSB_TO_WAMP
        if mode % 2 > 0:
            logger.info('listening on rsb scope %s' % self.rsb_scope)
            self.rsb_listener = rsb.createListener(self.rsb_scope, config=rsb_config)
            self.rsb_listener.addHandler(self.rsb_callback)

        # WAMP_TO_RSB
        if mode > 1:
            logger.info('listening on wamp scope %s' % self.wamp_scope)
            self.wamp_listener = self.wamp.subscribe(self.on_wamp_message, self.wamp_scope)
            self.rsb_publisher = rsb.createInformer(self.rsb_scope, config=rsb_config)

    def on_bytearray_message(self, event):
        if 'wamp' in event.metaData.userInfos:
            logger.debug("received OWN rsb bytearray on %s, skipping..." % self.rsb_scope)
            return
        logger.debug('received rsb bytearray on %s' % self.rsb_scope)
        logger.debug('event length %d' % len(event.data[1]))
        logger.debug('sent to %s' % self.wamp_scope)
        try:
            msg = '\0' + base64.b64encode(event.data[1]).decode('ascii')
            self.wamp.publish(self.wamp_scope, msg)
        except Exception as e:
            logger.error("Error while receiving rst data: %s", repr(e))

    def on_primitive_message(self, event):
        if 'wamp' in event.metaData.userInfos:
            logging.debug("received OWN rsb primitive on %s, skipping..." % self.rsb_scope)
            return
        msg = event.data.decode("utf8") if isinstance(event.data, string_types) else event.data
        logger.info("received primitive message [%s] on scope %s" % (msg, self.rsb_scope))
        logger.debug("sent to %s" % self.wamp_scope)
        try:
            self.wamp.publish(self.wamp_scope, self.rsb_type(event.data))
        except Exception as e:
            logger.error("Error while receiving primitive data: %s" % str(e))

    def send_rst(self, data):
        try:
            logger.info("send rst message to %s" % self.rsb_scope)
            binary_data = bytearray(base64.b64decode(data[1:]))
            event = Event(scope=self.rsb_scope,
                          data=(self.rsb_type, binary_data), type=tuple,
                          userInfos={'wamp': ''})
            self.rsb_publisher.publishEvent(event)
        except Exception as e:
            logger.error("Error while sending rst data: %s", repr(e))

    def send_primitive_data(self, data):
        try:
            logger.info("send primitive message [%s] to %s" % (unicode(data), self.rsb_scope))
            self.rsb_publisher.publishData(self.rsb_type(data), userInfos={'wamp': ''})
        except Exception as e:
            logger.error("Error while sending primitive data: %s" % str(e))

    def on_wamp_message(self, event):
        logger.debug('Received wamp message on %s' % self.wamp_scope)
        self.wamp_callback(event)

    def deactivate(self):
        logger.info("Shutting down bridge...")
        if self.rsb_listener:
            self.rsb_listener.deactivate()
        if self.rsb_publisher:
            self.rsb_publisher.deactivate()
