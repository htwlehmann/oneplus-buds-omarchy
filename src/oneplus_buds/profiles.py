from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


CompatibilityState = Literal["verified", "community_tested", "experimental"]


@dataclass(frozen=True)
class AncProfile:
    write_indices: dict[str, int]
    read_modes: dict[int, str]
    read_levels: dict[int, str]
    sequences: dict[str, int]
    # Optional display labels per level. The phone app names the intensity
    # levels differently per model, for example "Hoch", "Mittel" and "Niedrig"
    # on the Nord Buds 3 Pro, so the labels belong to the device profile.
    level_labels: dict[str, str] = field(default_factory=dict)

    def payload_for(self, mode: str) -> bytes:
        try:
            index = self.write_indices[mode]
        except KeyError as error:
            raise ValueError(f"ANC mode {mode!r} is not supported by this device profile") from error
        bitmap = 1 << index
        width = index // 8 + 1
        return b"\x01\x01" + bitmap.to_bytes(width, "little")

    def sequence_for(self, mode: str) -> int:
        return self.sequences.get(mode, 0x42)


@dataclass(frozen=True)
class EqPresetProfile:
    eq_id: int
    key: str
    name: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class EqProfile:
    presets: tuple[EqPresetProfile, ...]
    supports_custom: bool
    write_verified: bool
    custom_write_verified: bool

    def preset_for(self, value: str) -> EqPresetProfile | None:
        normalized = value.strip().lower()
        return next((preset for preset in self.presets
                     if normalized in (preset.key, str(preset.eq_id), *preset.aliases)), None)


PRO_EQ_PRESETS = (
    EqPresetProfile(0, "balanced", "Balanced"),
    EqPresetProfile(1, "deep-sea-bass", "Deep Sea Bass"),
    EqPresetProfile(2, "pure-vocals", "Pure Vocals"),
    EqPresetProfile(3, "bright-and-crisp", "Bright & Crisp"),
)

PRO_2_EQ_PRESETS = (
    EqPresetProfile(0, "balanced", "Balanced"),
    EqPresetProfile(1, "bass", "Bass", ("deep-sea-bass",)),
    EqPresetProfile(2, "serenade", "Serenade", ("pure-vocals",)),
    EqPresetProfile(3, "bold", "Bold", ("bright-and-crisp",)),
    EqPresetProfile(7, "hans-zimmer-soundscape-tuning", "Hans Zimmer Soundscape Tuning"),
)

# The Nord Buds 3 Pro answers the native EQ selection with factory IDs.
# The phone app ("Wireless Earphones", ColorOS) exposes exactly three of
# them; the owner confirmed the mapping by changing every preset in the app
# and reading the device back:
#   id 3 = Ausgewogen (Standard), id 4 = Serenade, id 5 = Bass
# The device accepts the other IDs as well but the app does not offer them.
NORD_BUDS_3_PRO_EQ_PRESETS = (
    EqPresetProfile(3, "balanced", "Ausgewogen (Standard)", ("ausgewogen", "balanced")),
    EqPresetProfile(4, "serenade", "Serenade", ("serenad",)),
    EqPresetProfile(5, "bass", "Bass", ("bass-boost",)),
)


@dataclass(frozen=True)
class DeviceProfile:
    product_id: str
    name: str
    service_uuid: str
    anc: AncProfile
    eq: EqProfile | None
    capabilities: frozenset[str]
    compatibility: CompatibilityState
    # Feature switches that may be written from the plugin. A switch that is
    # not listed stays read-only. Connection-changing switches need recovery
    # and a fresh read; an uncertain write must never be replayed.
    writable_features: frozenset[str] = frozenset()
    # Wire action -> allowed function IDs. Empty means no touch writes.
    touch_functions: dict[int, tuple[int, ...]] = field(default_factory=dict)
    hold_cycle_supported: bool = False
    # None preserves generic discovery for unaudited models. An audited map
    # lists only audited model/device switches and their app labels; generic query
    # replies (including false values) do not establish feature support.
    feature_labels: dict[str, str] | None = None

    @property
    def verified(self) -> bool:
        """Keep hardware write gates explicit and backwards compatible."""
        return self.compatibility == "verified"


PROFILES = {
    "060C14": DeviceProfile(
        product_id="060C14",
        name="OnePlus Buds Pro",
        service_uuid="00001107-d102-11e1-9b23-00025b00a5a5",
        anc=AncProfile(
            write_indices={"off": 0, "transparency": 1, "light": 2, "on": 3, "deep": 3, "smart": 4},
            read_modes={0: "off", 1: "transparency", 2: "on", 3: "on", 4: "on"},
            read_levels={2: "light", 3: "deep", 4: "smart"},
            sequences={"off": 0x40},
        ),
        eq=EqProfile(PRO_EQ_PRESETS, supports_custom=False, write_verified=True,
                     custom_write_verified=False),
        capabilities=frozenset(
            {
                "battery",
                "case_battery",
                "firmware",
                "anc",
                "transparency",
                "anc_levels",
                "smart_anc",
                "eq",
            }
        ),
        compatibility="verified",
    ),
    "062014": DeviceProfile(
        product_id="062014",
        name="OnePlus Buds Pro 2",
        service_uuid="0000079a-d102-11e1-9b23-00025b00a5a5",
        anc=AncProfile(
            write_indices={
                "off": 0,
                "on": 1,
                "transparency": 2,
                "deep": 4,
                "medium": 5,
                "light": 6,
                "smart": 7,
            },
            read_modes={0: "off", 1: "on", 2: "transparency", 3: "off", 8: "transparency"},
            read_levels={4: "deep", 5: "medium", 6: "light", 7: "smart"},
            sequences={"off": 0x40},
        ),
        eq=EqProfile(PRO_2_EQ_PRESETS, supports_custom=True, write_verified=True,
                     custom_write_verified=True),
        capabilities=frozenset(
            {
                "battery",
                "case_battery",
                "firmware",
                "anc",
                "transparency",
                "anc_levels",
                "smart_anc",
                "eq",
                "custom_eq",
            }
        ),
        compatibility="verified",
    ),
    "064414": DeviceProfile(
        product_id="064414",
        name="OnePlus Nord Buds 3 Pro",
        service_uuid="0000079a-d102-11e1-9b23-00025b00a5a5",
        anc=AncProfile(
            write_indices={
                "off": 0,
                "on": 1,
                "transparency": 2,
                "deep": 4,
                "medium": 5,
                "light": 6,
                "auto": 7,
            },
            read_modes={0: "off", 1: "on", 2: "transparency", 3: "off", 8: "transparency"},
            read_levels={4: "deep", 5: "medium", 6: "light", 7: "auto"},
            sequences={"off": 0x40},
            # The phone app labels the four intensities "Auto", "High",
            # "Moderate" and "Low" (German: Auto, Hoch, Mittel, Niedrig).
            level_labels={
                "deep": "High",
                "medium": "Moderate",
                "light": "Low",
                "auto": "Auto",
            },
        ),
        eq=EqProfile(NORD_BUDS_3_PRO_EQ_PRESETS, supports_custom=True, write_verified=True,
                     custom_write_verified=True),
        capabilities=frozenset(
            {
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
            }
        ),
        # Verified on the owner's hardware: writing these switches changed the
        # device state and a fresh read confirmed it. Everything else stays
        # read-only until it has been tested the same way. Hi-Res may reset
        # the Bluetooth link; the controller recovers without replaying writes.
        writable_features=frozenset({
            "bass_engine",
            "personal_noise",
            "wear_detection",
            "click_to_take_photo",
            "multipoint",
            "high_quality_audio",
        }),
        # Wireless Earphones 17.6.6, whitelist 064414, plus the owner's
        # 0100 capability reply 00 ff 27 52 ee c7 14. Golden Sound (bit19)
        # and headset spatial audio (bit43) are absent on this SPP path.
        # Phone/LE-Audio fallbacks do not establish support in this plugin.
        feature_labels={
            "personal_noise": "Personalised noise cancellation",
            "bass_engine": "BassWave",
            "wear_detection": "Auto play/pause",
            "click_to_take_photo": "Camera control",
            "multipoint": "Dual connection",
            "high_quality_audio": "Hi-Res mode",
        },
        # App support masks: 516, 8807, 8803, 536. App action 11 maps
        # to wire action 4 (fixed noise-control hold, not a selector).
        touch_functions={
            1: (0, 1),
            2: (0, 1, 2, 3, 5, 6, 17),
            3: (0, 2, 3, 5, 6, 17),
            6: (0, 11, 12),
        },
        hold_cycle_supported=True,
        # Owner-verified on real hardware: see
        # docs/devices/oneplus-nord-buds-3-pro.md. The ANC bitmap and the seven
        # factory EQ IDs were measured on this unit, not copied from another
        # model.
        compatibility="verified",
    ),
}


def profile_for_product(product_id: str | None) -> DeviceProfile | None:
    return PROFILES.get(product_id or "")


def feature_capabilities(profile: DeviceProfile | None, switches: dict[str, bool]) -> set[str]:
    """Keep raw diagnostic switch replies separate from advertised support."""
    names = set(switches)
    if profile is not None and profile.feature_labels is not None:
        names.intersection_update(profile.feature_labels)
    return names


def compatibility_for_product(product_id: str | None) -> CompatibilityState:
    profile = profile_for_product(product_id)
    return profile.compatibility if profile else "experimental"
