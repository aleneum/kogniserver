import logging
import os
import argparse
import sys
from functools import partial

from .services import Bridge, create_rsb_config

try:
    import asyncio
except ImportError:
    # Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn.asyncio.wamp import ApplicationSession


class Client(ApplicationSession):

    def __init__(self, config, scopes):
        self._scopes = [s.strip() for s in scopes.split(' ; ')]
        self.bridges = []
        self.config = create_rsb_config()
        super(Client, self).__init__(config)

    @asyncio.coroutine
    def onJoin(self, details):
        # init members
        if os.environ.get('DEBUG') in ['1', 'True', 'true', 'TRUE']:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logging.basicConfig()
        logging.getLogger().setLevel(log_level)
        for mapping in self._scopes:
            self.bridges.append(Bridge(**self.parse_mapping(mapping)))
        print 'client(asyncio) connected...'

    def parse_mapping(self, mapping):
        source, direction, destination = mapping.split(' ')
        destination = None if '*' in destination else destination
        d = 0
        if direction.startswith('<'):
            d += Bridge.WAMP_TO_RSB
        if direction.endswith('>'):
            d += Bridge.RSB_TO_WAMP

        message_type = direction.translate(None, '<->')
        return {'rsb_scope': source, 'rsb_config': self.config, 'wamp': self, 'message_type': message_type,
                'mode': d, 'destination': destination}

    def onLeave(self, details):
        for bridge in self.bridges:
            bridge.shutdown()
        print "client session left..."


def main_entry(args=None):
    from autobahn.asyncio.wamp import ApplicationRunner

    parser = argparse.ArgumentParser()
    parser.add_argument('url', metavar='URL', type=unicode, help="URL to websocket of WAMP server")
    parser.add_argument('scopes', metavar='SCOPE', type=str,
                        help="scope mappings: /rsb/scope [<][-]message_type[-][>] wamp.scope")
    args = sys.argv[1:] if args is None else args
    args = parser.parse_args(args)
    runner = ApplicationRunner(url=args.url, realm=u"realm1")
    try:
        runner.run(partial(Client, scopes=args.scopes))
    except KeyboardInterrupt or Exception:
        raise KeyboardInterrupt
    print "shutting down client..."


if __name__ == '__main__':
    main_entry()