# -*- coding: utf-8 -*-

from unittest import TestCase
from kogniserver.services import create_rsb_config
from kogniserver.pubsub import PubSubBridge
from mock import MagicMock


class TestKogniServerBridge(TestCase):

    def setUp(self):
        self.config = create_rsb_config()

    def tearDown(self):
        self.b.deactivate()

    #def __init__(self, rsb_scope, rsb_config, wamp, message_type, mode=BIDIRECTIONAL, wamp_scope=None):

    def test_to_wamp(self):
        self.b = PubSubBridge('/foo/bar', self.config, MagicMock(), 'string', PubSubBridge.RSB_TO_WAMP)
        self.assertIsNone(self.b.rsb_publisher)
        self.assertEqual(self.b.rsb_scope, '/foo/bar')
        self.assertEqual(self.b.wamp_scope, 'foo.bar')
        self.assertIsNotNone(self.b.rsb_listener)

    def test_from_wamp(self):
        self.b = PubSubBridge('/foo/bar', self.config, MagicMock(), 'string', PubSubBridge.WAMP_TO_RSB)
        self.assertIsNone(self.b.rsb_listener)
        self.assertEqual(self.b.rsb_scope, '/foo/bar')
        self.assertEqual(self.b.wamp_scope, 'foo.bar')
        self.assertIsNotNone(self.b.rsb_publisher)

    def test_bidirectional(self):
        self.b = PubSubBridge('/foo/bar', self.config, MagicMock(), 'string', PubSubBridge.BIDIRECTIONAL)
        self.assertIsNotNone(self.b.rsb_listener)
        self.assertEqual(self.b.rsb_scope, '/foo/bar')
        self.assertEqual(self.b.wamp_scope, 'foo.bar')
        self.assertIsNotNone(self.b.rsb_publisher)