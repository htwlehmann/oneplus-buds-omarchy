"""An EQ gesture belongs to the pair that was selected when it started."""
from dataclasses import replace
import unittest

from oneplus_buds.bridge import BudsFrontendBridge, serialize_snapshot
from oneplus_buds.controller import BudsController
from oneplus_buds.models import EqControlResult, EventBatch
from test_controller import STATUS, FakeSession


class EqSession(FakeSession):
    def __init__(self):
        super().__init__()
        self.writes = []

    def set_custom_eq(self, entry_id, gains):
        self.writes.append((entry_id,gains))
        return EqControlResult("Buds","062014",entry_id,"Curve",entry_id,"Curve",0,True), EventBatch((),0)


class EqBackend:
    def __init__(self, entries):
        self.entries = list(entries)

    def start_session(self, _address):
        session,status = self.entries.pop(0)
        session.__enter__()
        return session,status,EventBatch((),0)


class EqIdentityTests(unittest.TestCase):
    def test_selected_pair_accepts_valid_token_and_other_token_never_writes(self):
        session=EqSession()
        controller=BudsController(EqBackend([(session,STATUS)]))
        controller.start()
        token=serialize_snapshot(controller.snapshot())["find_device_id"]
        with self.assertRaisesRegex(ValueError,"changed"):
            controller.set_custom_eq(4,(1,0),device_id="f"*64)
        self.assertEqual(session.writes,[])
        result=controller.set_custom_eq(4,(1,0),device_id=token)
        self.assertTrue(result.verified)
        self.assertEqual(session.writes,[(4,(1,0))])
        controller.shutdown()

    def test_recovery_does_not_redirect_even_legacy_eq_call_to_another_pair(self):
        for with_token in (False,True):
            with self.subTest(with_token=with_token):
                first,second=EqSession(),EqSession()
                other=replace(STATUS,device=replace(STATUS.device,address="11:22:33:44:55:66"))
                controller=BudsController(EqBackend([(first,STATUS),(second,other)]))
                controller.start()
                token=serialize_snapshot(controller.snapshot())["find_device_id"]
                controller._close_session()  # Transport failed while the queued gesture still targets this pair.
                with self.assertRaisesRegex(ValueError,"changed"):
                    controller.set_custom_eq(4,(1,0),**({"device_id":token} if with_token else {}))
                self.assertEqual(second.writes,[])
                controller.shutdown()

    def test_bridge_rejects_malformed_eq_token_without_dispatching(self):
        class NeverController:
            def set_custom_eq(self,*_args,**_kwargs):
                raise AssertionError("invalid token reached write")
        for token in (False,"broken"):
            reply=BudsFrontendBridge(lambda _event:None,controller=NeverController()).execute(
                "set_custom_eq",{"entry_id":4,"gains_db":[1,0],"device_id":token})
            self.assertFalse(reply["ok"])
            self.assertIn("device_id",reply["error"]["message"])
