"""Feature04 writes must be confirmed rather than inferred from missing data."""
from dataclasses import replace
import unittest

from oneplus_buds.bridge import BudsFrontendBridge
from oneplus_buds.controller import BudsController
from oneplus_buds.models import EventBatch
from oneplus_buds.profiles import PROFILES
from oneplus_buds.protocol import Frame
from oneplus_buds.session import OpoSession
from test_controller import DEVICE, STATUS


class FeatureTransport:
    def __init__(self, reply, readback):
        self.reply = reply
        self.readback = readback
        self.requests = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        pass

    def request(self, command, payload, response_command):
        self.requests.append((command, payload, response_command))
        return self.reply if command == 0x0403 else self.readback


class FeatureSwitchTests(unittest.TestCase):
    def test_wear_switch_both_directions_use_feature_ack_and_fresh_read(self):
        for enabled, payload, read in ((False, b"\x04\x00", b"\x00\x01\x04\x00"),
                                       (True, b"\x04\x01", b"\x00\x01\x04\x01")):
            with self.subTest(enabled=enabled):
                wire = FeatureTransport(Frame(0x8403, 1, b"\x00"), Frame(0x810D, 2, read))
                with OpoSession(DEVICE, PROFILES["064414"], transport=wire) as session:
                    self.assertEqual(session.set_feature_switch(4, enabled), (0, True))
                self.assertEqual(wire.requests, [(0x0403, payload, 0x8403),
                                               (0x010D, b"\x01\x04", 0x810D)])

    def test_rejection_malformed_ack_missing_or_contradictory_readback_never_verify(self):
        for ack, read in ((Frame(0x8403, 1, b"\x0e"), b"\x00\x01\x04\x00"),
                          (Frame(0x8403, 1, b""), b"\x00\x01\x04\x00"),
                          (Frame(0x8404, 1, b"\x00"), b"\x00\x01\x04\x00"),
                          (Frame(0x8403, 1, b"\x00"), b"\x00\x00"),
                          (Frame(0x8403, 1, b"\x00"), b"\x00\x01\x04\x01")):
            with self.subTest(ack=ack, read=read):
                wire = FeatureTransport(ack, Frame(0x810D, 2, read))
                with OpoSession(DEVICE, PROFILES["064414"], transport=wire) as session:
                    self.assertFalse(session.set_feature_switch(4, False)[1])

    def test_frontend_can_set_wear_and_gets_confirmed_snapshot_without_unlocking_codec(self):
        wire = FeatureTransport(Frame(0x8403, 1, b"\x00"),
                                Frame(0x810D, 2, b"\x00\x01\x04\x00"))
        with OpoSession(DEVICE, PROFILES["064414"], transport=wire) as session:
            class Backend:
                def start_session(self, _address):
                    return session, replace(STATUS, product_id="064414"), EventBatch((), 0)
            controller = BudsController(backend=Backend())
            controller.start()
            emitted = []
            bridge = BudsFrontendBridge(emitted.append, controller=controller)
            reply = bridge.execute("set_feature_switch", {"feature":"wear_detection", "enabled":False})
            self.assertTrue(reply["ok"], reply)
            self.assertTrue(reply["result"]["verified"])
            self.assertFalse(emitted[-1]["snapshot"]["feature_switches"]["wear_detection"])
            self.assertIn("wear_detection", emitted[-1]["snapshot"]["writable_features"])
            blocked = bridge.execute("set_feature_switch", {"feature":"high_quality_audio", "enabled":True})
            self.assertFalse(blocked["ok"])
            self.assertEqual(len(wire.requests), 2)

