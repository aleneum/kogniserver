import logging
import os
from threading import Thread

from twisted.internet.defer import inlineCallbacks
from time import sleep

from autobahn.twisted.wamp import ApplicationSession

from services import SessionHandler


class Ping(Thread):
    def __init__(self, wamp):
        Thread.__init__(self)
        self.running = True
        self.wamp = wamp

    def run(self):
        try:
            while self.running:
                logging.debug("ping")
                self.wamp.publish(u'com.wamp.ping', "ping")
                sleep(1)
        except Exception as e:
            logging.debug(e)
            raise e


class Component(ApplicationSession):

    @staticmethod
    def on_ping(event):
        logging.debug(event)

    @inlineCallbacks
    def onJoin(self, details):
        if os.environ.get('DEBUG') in ['1','True','true','TRUE']:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logging.basicConfig()
        logging.getLogger().setLevel(log_level)
        self.session = SessionHandler(self, log_level)

        # register RPC
        reg = yield self.register(self.session.register_scope, u'service.displayserver.register')
        rpc = yield self.register(self.session.call_rpc, u'service.displayserver.call')

        # setup ping
        sub = yield self.subscribe(self.on_ping, u'com.wamp.ping')

        self.ping = Ping(self)
        self.ping.start()

        print 'kogniserver(twisted) started...'

    def onLeave(self, details):
        print('Leave Reason:', details.reason)
        print('Leave Message:', details.message)
        self.ping.running = False
        while self.ping.isAlive():
            sleep(0.1)
        self.session.quit()
        print "kogniserver session left..."


def main_entry(ssl_cert=None):
    from autobahn.twisted.wamp import ApplicationRunner
    proto = "wss" if ssl_cert else "ws"
    options = None
    if ssl_cert:
        from OpenSSL import crypto
        import six
        from twisted.internet._sslverify import OpenSSLCertificateAuthorities
        from twisted.internet.ssl import CertificateOptions
        from OpenSSL import crypto

        cert = crypto.load_certificate(
            crypto.FILETYPE_PEM,
            six.u(open(ssl_cert, 'r').read())
        )
        # tell Twisted to use just the one certificate we loaded to verify connections
        options = CertificateOptions(
            trustRoot=OpenSSLCertificateAuthorities([cert]),
        )
    runner = ApplicationRunner(url=u"{0}://localhost:8181/ws".format(proto),
                               realm=u"realm1", ssl=options)

    try:
        runner.run(Component, auto_reconnect=True)
    except Exception as e:
        print ("Exit App Reason: ", e)
        raise KeyboardInterrupt

if __name__ == '__main__':
    main_entry()
