from unittest import TestCase
import mock
from kogniserver.adm import main_entry
import threading
import subprocess
import time
import thread

from os.path import exists
from os import remove

def terminate():
    time.sleep(7)
    subprocess.call(['crossbar', 'stop'])
    time.sleep(2)
    thread.interrupt_main()


def run_crossbar(args):
    t = threading.Thread(target=terminate)
    t.start()
    with mock.patch('__builtin__.raw_input',  side_effect=['', '.']):
        main_entry(args)


class TestKogniServerAdm(TestCase):

    def setUp(self):
        if exists('./config.test.json'):
            remove('./config.test.json')

    def tearDown(self):
        if exists('./config.test.json'):
            remove('./config.test.json')

    def test_start(self):
        args = ['-c', './config.test.json', '-f']
        run_crossbar(args)