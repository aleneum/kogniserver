from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

import sys
import logging

from services import SessionHandler

class AppSession(ApplicationSession):

    @staticmethod
    def on_ping(event):
        print event

    @inlineCallbacks
    def onJoin(self, details):

        # init members
        logging.basicConfig()
        session = SessionHandler(self)

        # register RPCs
        reg = yield self.register(session.register_scope, 'service.displayserver.register')
        sub = yield self.subscribe(self.on_ping, "com.wamp.ping")
        try:
            while True:
                try:
                    print "ping"
                    self.publish("com.wamp.ping", "ping")
                except ApplicationError as e:
                    print e
                    sys.exit(1)
                yield sleep(1)

        except Exception:
            print "shut down server..."
            for scope in self.scopes.values():
                scope.release()

def main_entry():
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner(url = u"ws://127.0.0.1:8181/ws", realm = u"realm1")
    runner.run(AppSession)

if __name__ == '__main__':
    main_entry()