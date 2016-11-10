# -*- coding: utf-8 -*-

from unittest import TestCase
from kogniserver.services import SessionHandler
from mock import MagicMock
from functools import partial
import rsb
import time
from Value_pb2 import Value
import base64
import threading


def send_primitive(session, data, type):
    passed = MagicMock()

    def message_received(passed, event):
        print event.data
        if event.data == data:
            passed()

    func = partial(message_received, passed)

    with rsb.createListener('/test/scope') as listener:
        listener.addHandler(func)
        session.register_scope('/test/scope', type)
        session.scopes['/test/scope'].send_primitive_data(data)
        time.sleep(0.1)
    return passed.called


class TestKogniServerSessionHandler(TestCase):

    def setUp(self):
        wamp = MagicMock()
        self.session = SessionHandler(wamp_session=wamp)
        self.lock = threading.Lock()
        self.lock.acquire()
        self.passed = MagicMock()

    def tearDown(self):
        self.session.quit()
        self.lock.release()

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

    def test_send_int(self):
        res = send_primitive(self.session, 1, 'integer')
        self.assertTrue(res)

    def test_send_protobuf_raw(self):
        def raw_received(passed, lock, event):
            if type(event.data) == tuple:
                passed()
            lock.release()

        rsb.converter.registerGlobalConverter(
            rsb.converter.ProtocolBufferConverter(messageClass=Value), True)
        self.session.register_scope('/test/scope', 'rst.generic.Value')
        with rsb.createListener('/test/scope', config=self.session.rsb_conf) as listener:
            listener.addHandler(partial(raw_received, self.passed, self.lock))
            with rsb.createInformer('/test/scope', dataType=Value) as informer:
                v = Value()
                v.type = Value.STRING
                v.string = "hello"
                informer.publishData(v)
            self.lock.acquire()
        self.assertTrue(self.passed.called)

    def test_send_protobuf(self):
        def protobuf_received(passed, lock, event):
            if hasattr(event.data, 'type'):
                passed()
            lock.release()

        rsb.converter.registerGlobalConverter(
            rsb.converter.ProtocolBufferConverter(messageClass=Value), True)
        self.session.register_scope('/test/scope', 'rst.generic.Value')
        with rsb.createListener('/test/scope') as listener:
            listener.addHandler(partial(protobuf_received, self.passed, self.lock))
            with rsb.createInformer('/test/scope', dataType=Value) as informer:
                v = Value()
                v.type = Value.STRING
                v.string = "hello"
                informer.publishData(v)
            self.lock.acquire()
        self.assertTrue(self.passed.called)

    def test_wamp_string(self):
        self.session.register_scope('/test/scope', 'string')
        self.session.scopes['/test/scope'].on_wamp_message('hello')

    def test_wamp_float(self):
        self.session.register_scope('/test/scope', 'float')
        self.session.scopes['/test/scope'].on_wamp_message(0.1)

    def test_wamp_unicode(self):
        self.session.register_scope('/test/scope', 'string')
        self.session.scopes['/test/scope'].on_wamp_message(u'hellö')

    def test_wamp_protobuf(self):
        def raw_received(session, event):
            msg = '\0' + base64.b64encode(event.data[1]).decode('ascii')
            session.scopes['/test/out'].on_wamp_message(msg)

        def protobuf_received(passed, lock, event):
            if hasattr(event.data, 'type'):
                passed()
            lock.release()

        rsb.converter.registerGlobalConverter(
            rsb.converter.ProtocolBufferConverter(messageClass=Value), True)
        self.session.register_scope('/test/scope', 'rst.generic.Value')
        self.session.register_scope('/test/out', 'rst.generic.Value')
        with rsb.createListener('/test/scope', config=self.session.rsb_conf) as listener:
            listener.addHandler(partial(raw_received, self.session))
            with rsb.createListener('/test/out') as out:
                out.addHandler(partial(protobuf_received, self.passed, self.lock))
                with rsb.createInformer('/test/scope', dataType=Value) as informer:
                    v = Value()
                    v.type = Value.STRING
                    v.string = "hello"
                    informer.publishData(v)
                self.lock.acquire()
        self.assertTrue(self.passed.called)

    def test_rpc(self):

        def echo(x):
            return x

        def squared(x):
            return x*x

        with rsb.createLocalServer('/test/rpc') as server:
            server.addMethod('echo', echo, str, str)
            server.addMethod('squared', squared, int, int)
            res = self.session.call_rpc('/test/rpc', 'echo', "foo")
            self.assertEqual(res, "foo")
            res = self.session.call_rpc('/test/rpc', 'squared', 5)
            self.assertEqual(res, 25)

    # Future Feature
    # def test_rst_rpc(self):
    #     def echo_type(val):
    #
    #     with rsb.createLocalServer('/test/rpc') as server:
    #         server.addMethod('echo', echo_type, Value, int)
    #         v = Value()
    #         v.type = Value.STRING
    #         v.string = "foo"
    #         res = self.session.call_rpc('/test/rpc', 'echo', v)
    #         self.assertEqual(res, 4)
