from unittest import TestCase
import mock
from kogniserver.adm import main_entry, check_server
import threading
import subprocess
import time
import thread

from os.path import exists
from os import remove


def terminate():
    while not check_server('localhost', 8181):
        time.sleep(0.5)
    subprocess.call(['crossbar', 'stop'])
    time.sleep(2)
    thread.interrupt_main()


def run_crossbar(args):
    t = threading.Thread(target=terminate)
    t.start()
    with mock.patch('__builtin__.raw_input',  side_effect=['', '.', '']):
        main_entry(args)


# def run_crossbar_tls(args):
#     t = threading.Thread(target=terminate)
#     t.start()
#     with mock.patch('__builtin__.raw_input', side_effect=['', '.', 'server']):
#         main_entry(args)


class TestKogniServerAdm(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestKogniServerAdm, cls).setUpClass()
        if not exists('./server.crt'):
            subprocess.call(['./tests/create-self-signed-cert.sh'])

    def setUp(self):
        if exists('./config.test.json'):
            remove('./config.test.json')

    def tearDown(self):
        if exists('./config.test.json'):
            remove('./config.test.json')

    def test_start(self):
        args = ['-c', './config.test.json', '-f']
        run_crossbar(args)

    # def test_start_tls(self):
    #     args = ['-c', './config.test.json', '-f']
    #     run_crossbar_tls(args)

    def test_generate(self):
        args = ['-c', './config.test.json', '-f', '-g']
        main_entry(args)
        self.assertTrue(exists('./config.test.json'))


