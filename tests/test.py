from unittest import TestCase
from kogniserver.services import SessionHandler


class TestKogniServer(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create(self):
        session = SessionHandler(wamp_session=None)