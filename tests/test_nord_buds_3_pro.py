"""Owner-verified profile for the OnePlus Nord Buds 3 Pro (product 064414).

The ANC bitmap and the native EQ IDs in this file were measured on the owner's
device, not copied from another model. The tests below pin the measured values
so a later profile edit cannot silently change the wire format.
"""
from __future__ import annotations

import unittest

from oneplus_buds.profiles import PROFILES

PRODUCT_ID = "064414"


class NordBuds3ProProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = PROFILES[PRODUCT_ID]

    def test_profile_is_owner_verified(self) -> None:
        self.assertEqual(self.profile.product_id, PRODUCT_ID)
        self.assertEqual(self.profile.name, "OnePlus Nord Buds 3 Pro")
        self.assertEqual(self.profile.compatibility, "verified")
        self.assertTrue(self.profile.verified)
        self.assertEqual(self.profile.service_uuid,
                         "0000079a-d102-11e1-9b23-00025b00a5a5")

    def test_anc_write_indices_match_the_measured_bitmap(self) -> None:
        self.assertEqual(
            self.profile.anc.write_indices,
            {"off": 0, "on": 1, "transparency": 2, "deep": 4, "medium": 5,
             "light": 6, "auto": 7},
        )
        # The phone app's device table lists Auto at index 7 for this model.
        self.assertEqual(self.profile.anc.payload_for("auto"), b"\x01\x01\x80")

    def test_anc_payload_bytes_match_the_measured_frames(self) -> None:
        expected = {
            "off": b"\x01\x01\x01",
            "on": b"\x01\x01\x02",
            "transparency": b"\x01\x01\x04",
            "deep": b"\x01\x01\x10",
            "medium": b"\x01\x01\x20",
            "light": b"\x01\x01\x40",
        }
        for mode, payload in expected.items():
            self.assertEqual(self.profile.anc.payload_for(mode), payload, mode)

    def test_anc_read_aliases_cover_the_measured_reports(self) -> None:
        self.assertEqual(self.profile.anc.read_modes[0], "off")
        self.assertEqual(self.profile.anc.read_modes[1], "on")
        self.assertEqual(self.profile.anc.read_modes[2], "transparency")
        self.assertEqual(self.profile.anc.read_levels[4], "deep")
        self.assertEqual(self.profile.anc.read_levels[5], "medium")
        self.assertEqual(self.profile.anc.read_levels[6], "light")

    def test_anc_levels_use_the_phone_app_names(self) -> None:
        # The owner changed every level in the phone app and read the device
        # back: 0x10 is "Hoch", 0x20 is "Mittel" and 0x40 is "Niedrig".
        from oneplus_buds.protocol import BASS_LEVEL_MAX, BASS_LEVEL_MIN
        self.assertEqual(BASS_LEVEL_MIN, -10)
        self.assertEqual(BASS_LEVEL_MAX, 10)
        self.assertEqual(self.profile.anc.payload_for("deep"), b"\x01\x01\x10")
        self.assertEqual(self.profile.anc.payload_for("medium"), b"\x01\x01\x20")
        self.assertEqual(self.profile.anc.payload_for("light"), b"\x01\x01\x40")

    def test_native_eq_exposes_the_three_app_presets_and_custom_curves(self) -> None:
        eq = self.profile.eq
        self.assertIsNotNone(eq)
        assert eq is not None
        # The phone app offers exactly three factory presets; the owner
        # confirmed id 3 = Ausgewogen, 4 = Serenade and 5 = Bass by changing
        # every preset in the app and reading the device back.
        self.assertEqual([preset.eq_id for preset in eq.presets], [3, 4, 5])
        self.assertEqual(
            [preset.name for preset in eq.presets],
            ["Ausgewogen (Standard)", "Serenade", "Bass"],
        )
        self.assertTrue(eq.write_verified)
        self.assertTrue(eq.supports_custom)
        self.assertTrue(eq.custom_write_verified)

    def test_capabilities_match_the_measured_features(self) -> None:
        self.assertEqual(
            self.profile.capabilities,
            frozenset({
                "battery",
                "case_battery",
                "firmware",
                "anc",
                "transparency",
                "anc_levels",
                "eq",
                "custom_eq",
                "bass_engine",
                "feature_switches",
                "find_earbuds",
                "touch_controls",
                "hold_cycle",
            }),
        )

    def test_touch_choices_pin_the_36_hardware_verified_round_trips(self) -> None:
        self.assertEqual(self.profile.touch_functions, {
            1: (0, 1), 2: (0, 1, 2, 3, 5, 6, 17),
            3: (0, 2, 3, 5, 6, 17), 6: (0, 11, 12),
        })

    def test_shared_hold_cycle_pins_the_four_hardware_verified_masks(self) -> None:
        from oneplus_buds.touch import hold_cycle_mask, parse_hold_cycle
        from oneplus_buds.protocol import Frame
        self.assertTrue(self.profile.hold_cycle_supported)
        self.assertEqual(hold_cycle_mask(("anc", "off")), 3)
        self.assertEqual(hold_cycle_mask(("off", "transparency")), 5)
        self.assertEqual(hold_cycle_mask(("anc", "transparency")), 6)
        self.assertEqual(hold_cycle_mask(("anc", "off", "transparency")), 7)
        self.assertEqual(parse_hold_cycle(Frame(0x810C, 1, bytes.fromhex("00 02 01 06"))), 6)


if __name__ == "__main__":
    unittest.main()
