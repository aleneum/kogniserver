from unittest import TestCase
from kogniserver.client import main_entry, Client
from kogniserver.adm import main_entry as admin_main
from kogniserver.adm import check_server
from mock import MagicMock
import threading
import subprocess
import time
import thread

from os.path import exists
from os import remove


def terminate():
    thread.interrupt_main()
    time.sleep(2)
    subprocess.call(['crossbar', 'stop'])


def start_crossbar():
    subprocess.call(['crossbar', 'start', '--config', './config.test.json'])


def run_crossbar(args):
    s = threading.Thread(target=start_crossbar)
    s.start()
    while not check_server('localhost', 8181):
        time.sleep(0.5)
    t = threading.Thread(target=terminate)
    t.start()
    main_entry(args)


class TestKogniServerClient(TestCase):

    def setUp(self):
        if exists('./config.test.json'):
            remove('./config.test.json')
        args = ['-c', './config.test.json', '-f', '-g']
        admin_main(args)

    def tearDown(self):
        if exists('./config.test.json'):
            remove('./config.test.json')

    def test_start(self):
        args = ['ws://127.0.0.1:8181/ws', '/foo/bar <string> * ; /foo/baz <string> /foo/baz2']
        run_crossbar(args)

    def test_scopes_splitting(self):
        self.c = Client(config=MagicMock(), scopes="/foo/bar <string> *")
        self.assertEqual(len(self.c._scopes), 1)
        self.c.onLeave(None)
        self.c = Client(config=MagicMock(), scopes="/foo/bar <string> * ; /bar/baz <mooh> bar.baz")
        self.assertEqual(len(self.c._scopes), 2)
        self.c.onLeave(None)




