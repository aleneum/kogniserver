from unittest import TestCase
from kogniserver.services import SessionHandler, Bridge
from mock import MagicMock
import inspect


class TestKogniServer(TestCase):

    def setUp(self):
        wamp = MagicMock()
        self.session = SessionHandler(wamp_session=wamp)

    def tearDown(self):
        del self.session

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
