# Compatibility

Compatibility describes evidence on particular hardware and firmware.

| Product | Product ID | Evidence origin | Recorded firmware |
|---|---|---|---|
| OnePlus Buds Pro | `060C14` | Upstream maintainer | 541.541.510 |
| OnePlus Buds Pro 2 | `062014` | Upstream maintainer | 196.196.101 |
| OnePlus Nord Buds 3 Pro | `064414` | Fork owner, October 2026 | 155.155.101 |
| Other recognised OnePlus/OPO products | Unknown | Experimental discovery only | Unknown |

Pro/Pro 2 evidence is inherited from their [device records](oneplus-buds-pro.md)
and [Pro 2 record](oneplus-buds-pro-2.md). They were not physically retested for
this snapshot; unit/UI tests are not substitute hardware verification.
The [Nord record](oneplus-nord-buds-3-pro.md) contains owner measurements.
In this fork its backend status remains `verified` to retain the tested write
permissions. That does not mean Gaz tested it, or that Marketplace verification
covers the fork. Upstream's separate Community Tested/write-permission policy
must be resolved when contributing this profile; unknown models get no new writes.

Discovery uses connected BlueZ devices with `oneplus` or `oppo` in their names
and a known OPO UUID. Renaming can prevent discovery. An OPPO name is only a
candidate, not a compatibility claim. Realme/BLE-only devices are not supported
by this RFCOMM implementation. The bar requires one compatible connected device;
the CLI has explicit address selection.

## Controls by evidence

- Pro: ANC On/Off/Transparency, Light/Deep/Smart, four native EQ presets.
- Pro 2: ANC On/Off/Transparency, Light/Medium/Deep/Smart, model-specific EQ
  presets and two device-declared six-band custom curves. These are upstream
  hardware results, not a test of the new profile-management UI on Pro 2.
- Nord: ANC On/Off/Transparency, **Low/Moderate/High/Auto**; Balanced (Default),
  Serenade, Bass; six-band custom curves and three create/rename/delete slots.
  Owner-tested feature writes: Personalised noise cancellation, BassWave,
  Auto play/pause, Camera control, Dual connection, Hi-Res mode. Also tested:
  touch assignments, the shared noise-control hold cycle and Find Play/Stop.
- Other recognised devices: existing read-only discovery may run over RFCOMM
  channel 15; a generic response is not proof of model support.

Nord labels and feature visibility were compared with Wireless Earphones
17.6.6 (`com.oplus.melody`) and checked against the physical device. HeyMelody
117.6.6 was not analysed. Only the Nord receives the new feature/touch write
allowlists. Connection-changing switches recover on the same physical pair
without replaying an uncertain write. A confirmed Boolean state does not prove
camera capture, player behaviour, actual codec resolution or acoustic effect.

The case may omit its battery. Valid values are cached per device; `*` and
"last known" mark cached values and an old charging flag is not retained. The
Nord returned case values while the buds were inside the open case and connected.
Charging-bit measurements describe the observed sample, not a general proof
that an open lid always prevents charging.

Phone-side OnePlus 3D Audio, Golden Sound, ANC calibration and configurable call
gestures are not implemented. Earbud-side spatial/hearing capabilities were not
established on the measured Nord SPP path. Raw generic switch replies are kept
for diagnostics and do not automatically become visible capabilities.

Reports are local, user-reviewed files with no automatic upload. Verified and
Community Tested devices offer **Report a problem**; Experimental devices offer
**Report compatibility**. Current runtime links point to upstream. Review the
[contribution guide](../../CONTRIBUTING.md) before opening a report there.
Automatic selection reruns after transport loss, while explicit CLI `--device`
selection stays pinned; old device data is cleared before another pair is used.
