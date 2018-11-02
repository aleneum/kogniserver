import logging
import os
from threading import Thread
import time

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn.asyncio.wamp import ApplicationSession
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
                time.sleep(1)
        except Exception as e:
            logging.debug(e)
            raise e


class Component(ApplicationSession):

    @staticmethod
    def on_ping(event):
        logging.debug(event)

    @asyncio.coroutine
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

        print 'kogniserver(asyncio) started...'

    def onLeave(self, details):
        self.ping.running = False
        while self.ping.isAlive():
            time.sleep(0.1)
        self.session.quit()
        print "kogniserver session left..."


def main_entry(ssl_cert=None):
    from autobahn.asyncio.wamp import ApplicationRunner
    proto = "wss" if ssl_cert else "ws"
    options = None
    if ssl_cert:
        raise RuntimeError("asyncio backend does not support ssl")
    runner = ApplicationRunner(url=u"{0}://127.0.0.1:8181/ws".format(proto),
                               realm=u"realm1", ssl=options)
    try:
        runner.run(Component)
    except KeyboardInterrupt or Exception:
        raise KeyboardInterrupt
    print "shutting down kogniserver..."


if __name__ == '__main__':
    main_entry()
