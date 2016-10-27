from unittest import TestCase
from kogniserver.client import main_entry, Client
from mock import MagicMock
import threading
import subprocess
import time
import thread

from os.path import exists
from os import remove


def terminate():
    time.sleep(8)
    subprocess.call(['crossbar', 'stop'])
    time.sleep(2)
    thread.interrupt_main()


def start_crossbar():
    subprocess.call(['crossbar', 'start'])


def run_crossbar(args):
    s = threading.Thread(target=start_crossbar)
    s.start()
    time.sleep(8)
    t = threading.Thread(target=terminate)
    t.start()
    main_entry(args)


class TestKogniServerClient(TestCase):

    def setUp(self):
        if exists('./config.test.json'):
            remove('./config.test.json')

    def tearDown(self):
        if exists('./config.test.json'):
            remove('./config.test.json')
        self.c.onLeave(None)

    def test_start(self):
        args = ['ws://127.0.0.1:8181/ws', '/foo/bar <string> * ; /foo/baz <string> /foo/baz2']
        run_crossbar(args)

    def test_scopes_splitting(self):
        self.c = Client(config=MagicMock(), scopes="/foo/bar <string> *")
        self.assertEqual(len(self.c._scopes), 1)
        self.c = Client(config=MagicMock(), scopes="/foo/bar <string> * ; /bar/baz <mooh> bar.baz")
        self.assertEqual(len(self.c._scopes), 2)


