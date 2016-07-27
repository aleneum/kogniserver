from unittest import TestCase
from kogniserver.services import SessionHandler
from mock import MagicMock
from functools import partial
import rsb
import time


def send_primitive(session, data, type):
    passed = MagicMock()

    def message_received(passed, event):
        print event.data
        if event.data in data:
            passed()

    func = partial(message_received, passed)

    with rsb.createListener('/test/scope') as listener:
        listener.addHandler(func)
        session.register_scope('/test/scope', type)
        session.scopes['/test/scope'].send_primitive_data(data)
        time.sleep(0.1)
    return passed.called


class TestKogniServer(TestCase):

    def setUp(self):
        wamp = MagicMock()
        self.session = SessionHandler(wamp_session=wamp)

    def tearDown(self):
        self.session.quit()

    def test_create(self):
        s = SessionHandler(wamp_session=None)

    def test_register_primitive(self):
        self.assertEqual(self.session.register_scope('/test/scope', 'integer'),
                         "Scope registered")
        self.assertEqual(self.session.scopes['/test/scope'].rsb_callback,
                         self.session.scopes['/test/scope'].on_primitive_message)

    def test_register_bytearray(self):
        self.assertEqual(self.session.register_scope('/test/scope', 'rst.generic.Value'),
                         "Scope registered")
        self.assertEqual(self.session.scopes['/test/scope'].rsb_callback,
                         self.session.scopes['/test/scope'].on_bytearray_message)

    def test_already_registered(self):
        self.assertEqual(self.session.register_scope('/test/scope', 'integer'),
                        "Scope registered")
        self.assertEqual(self.session.register_scope('/test/scope', 'integer'),
                        "Scope already exists")

    def test_send_string(self):
        res = send_primitive(self.session, 'Hello', 'string')
        self.assertTrue(res)

    def test_send_float(self):
        res = send_primitive(self.session, 1.0, 'float')
        self.assertTrue(res)
