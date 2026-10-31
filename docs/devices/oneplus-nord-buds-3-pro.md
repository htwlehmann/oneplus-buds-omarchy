# OnePlus Nord Buds 3 Pro (owner test device)

Compatibility status: **Verified on real hardware** by the plugin owner, 2026-10-27.
This record was produced by measuring one unit locally, not by copying another
model's profile. Upstream has no maintainer verification for this product.

## Verified locally

- BlueZ name: `OnePlus Nord Buds 3 Pro`
- Bluetooth modalias: `bluetooth:v02B0p0000d001F`
- Paired, bonded, trusted and connected
- BlueZ 5.87 reports an aggregate battery percentage
- Services include the OPO vendor service `0000079a-d102-11e1-9b23-00025b00a5a5`,
  the extended vendor service `0000079c-...`, HID, A/V remote control and the
  vendor UUIDs `66666666-...`, `99999999-...` and `df21fe2c-2515-4fdb-8886-f12c4d67927c`
- RFCOMM channel 15 accepts a connection
- OPO product query returns `064414`
- Firmware `155.155.101` (component records 111/155/101)
- Standard 0xAA framing, capability primer, HELLO/REGISTER authentication and the
  authenticated SET flow behave as documented for the other OPOv1 models
- Component battery query returned left and right percentage plus a case entry
- The device pushes unsolicited state notifications (`0x0204`) including its model
  strings ("WI-NB7450-1", "OnePlus Nord 3")

The Bluetooth address is deliberately not recorded.

## Case battery (correction, 2026-10-31)

The owner confirmed that the phone shows the case level when the buds are
inside the open case and connected. The earlier removal in `99bc02a` inferred
missing hardware support from an unavailable zero reading; that inference
was incorrect. A read-only `0x0106` query on the owner's unit now returned
`0x8106: 00 03 01 64 02 64 03 32`: both buds at 100%, case at 50%.
The open/closed transition itself has not yet been captured in this session.

The decompiled app's `btsdk/api/data/BatteryInfo.java` decodes the same
component/value pairs (low seven bits = level, high bit = charging), declares
the minimum level as 1, and `ui/widget/MelodyBatteryViews.java:a()` hides
levels <= 0. Case support is restored in the Nord profile. The plugin queries
battery state every ten seconds while connected and accepts case levels
1..100. Missing, zero, or invalid case samples keep the last valid level.

The bridge saves the last level separately for each product and physical
device in `$XDG_CACHE_HOME/oneplus-buds/case-battery/` (default `~/.cache/…`),
using hashed filenames and atomic replacement. Remembered values carry
`last_known: true`, show `C 50%*` with "last known" in the tooltip, and never
retain an old charging indicator. With no valid reading yet, the case stays
hidden. A disconnected plugin still follows the existing disconnected UI;
the cached case reappears when that device reconnects.

## Verified ANC profile

The device uses the same little-endian bitmap convention as the Buds Pro 2.
Every mode below was written with the authenticated `0x0404` flow, acknowledged
with status `00`, and confirmed by an independent fresh-session query.

| Function | Write index/bitmap | Observed read index | Result |
|---|---:|---:|---|
| Off | 0 / `01` | 0 | Verified |
| ANC On (parent mode) | 1 / `02` | active level index | Verified |
| Transparency | 2 / `04` | 2 | Verified |
| High | 4 / `10` | 4 | Verified |
| Moderate | 5 / `20` | 5 | Verified |
| Low | 6 / `40` | 6 | Verified |
| Auto | 7 / `80` | pushed notification | Verified |

Two behaviours differ from the Buds Pro 2 and are worth keeping in mind:

- The main ANC On command (`02`) does not report the parent mode. The device
  answers with the level it actually applied (`10`, `20` or `40`).
- The Auto mode (`80`) is confirmed by the pushed mode notification
  (`0x0204 03 01 01 80`), because the following status query reports the
  intensity the device settled on rather than the Auto mode itself.

The mapping above is not a guess: it is the device's own entry in the phone
app's model table. The app stores that table encrypted in
`resources/res/raw/melody_app_whitelist.json` and decrypts it with AES/GCM
using the SHA-256 of the app's signing certificate. Decrypted, the entry for
`064414` lists exactly these indices, including Auto at index 7, and the
plugin's independent measurements match it entry for entry.

### ANC latency correction (2026-10-31)

The controller accidentally restricted session reuse to On/Off/Transparency.
All four strength buttons therefore closed the monitoring socket, rediscovered
the device, authenticated, wrote, opened another socket for verification, then
reconnected and resubscribed before returning the result. Live plugin measurements
for Low and the restoration to Moderate took 15.52/15.30 seconds at the frontend;
the backend consumed 8.45/8.47 seconds and monitoring restoration another
6.88/6.74 seconds. The device's actual audible application time was not measured.

All supported strengths now use the existing authenticated session. Measured
controller verification times for Low/Moderate/High/Auto were 60.7/118.3/72.9/60.2 ms;
the frontend's confirmed selection appeared after 149.7/302.7/152.0/151.2 ms.
The IPC harness samples every 80 ms plus process overhead, so frontend values
are observed bounds rather than exact render times. The original Moderate
state was restored and confirmed after every test sequence.

Auto had a second bug: a final query timeout bypassed its notification fallback,
and repeated queries kept waiting for a fixed level despite receiving the
selected Auto notification. A matching selected-mode notification now ends
verification after the first readback, or survives a readback timeout. Neither
an acknowledgement alone nor an intelligent-intensity notification can verify
Auto. The live Auto selection stayed stable for a ten-second observation.

The REA audit of the shipped `com.oplus.melody` 17.6.6 APK confirms every mapping
in the table above. The app sends the same one-hot `CurrentNoiseModeInfo`
type-1 payload through `0x0404`. It distinguishes selected-mode notifications
`03 01 01 bitmap` from adaptive-intensity notifications `03 04 01 bitmap`.
Its five-second future is a failure timeout, not a deliberate switching delay.
Live while Auto was selected: query `0x010c 01 01` returned `00 01 01 40`, query
`0x010c 04 01` returned `00 04 01 40`, while the selected notification remained
`03 01 01 80`. The app's static parser expects the first query to reflect selected
mode; the owner's firmware instead returns the active intensity in this case.

App sources: `model/repository/earphone/G.java:t0/u0`,
`btsdk/api/data/CurrentNoiseModeInfo.java:getData`,
`btsdk/protocol/commands/k.java:h/s/M`, and `commands/f.java:b`.
REA serialization Evidence: `ev_21005fcdf65e6dda1bc26c9b20786664d8cd4f668ed6439b8a0227faa3ff917d`;
notification parser: `ev_24393d69618b7bf35d0357ccd9e1f5b068ec58369462de6bf1e3c82d99d69574`.
The local export is `~/src/oneplus-buds-research/rea-anc-app-audit-2026-10-31-evidence.json`.
HeyMelody 117.6.6 was not supplied and has not been compared.
Sanitized hardware records: [ANC latency measurement](../measurements/2026-10-31-nord-anc-latency.json).

The normal app UI exposes strength choices only after selecting the ANC parent:
Off → On (`01 01 02`) → strength. It also guards against both buds being unworn
or in the case (`NoiseReductionItem.java`). A later final-check attempt started
from an externally changed Off state and Low did not apply; Off was restored.
After the owner reinserted both buds, the final provenance-hardened version
passed Off → Low → On → Moderate → High → Auto, then restored Moderate.
Direct Off → Low succeeded, so an ANC-On prerequisite is not required on this
unit. The previous refusal is consistent with the unworn/case condition.
Low/Moderate/High/Auto were confirmed in 82.7/185.8/143.7/124.0 ms, with the
QML selection observed at 303.7/298.0/296.5/297.5 ms. Every SET returned status
00 and every transaction used one verification query; Auto's separate selected
notification provided confirmation while its query returned concrete Low.
Auto stayed selected during the additional ten-second observation. Tests also
reject stale query responses and newer contradictory selected-mode pushes.

## Native EQ

The device accepts the seven factory IDs 0 to 6 and ignores 7 and 8: a selection
is acknowledged with status `00` and confirmed by a fresh `0x010f` read, while
unknown IDs leave the current selection untouched.

The phone app offers exactly three of them, and the owner confirmed the
mapping by changing every preset in the app and reading the device back:

| App label | Factory ID | Result |
|---|---:|---|
| Ausgewogen (Standard) / Balanced | 3 | Verified |
| Serenade / Clear Vocals | 4 | Verified |
| Bass | 5 | Verified |

The same mapping appears in the app's decrypted model table for `064414`
(`equalizerMode`: protocolIndex 3/4/5 for modeType 11/14/12).

The native EQ catalogue query (`0x0122`) answers `00 00`, so the device publishes
no preset names, band definitions or custom entries of its own - unlike the
Buds Pro 2, which returns two writable custom curves. The plugin therefore
offers preset selection only.

## Feature switches

The app's model table marks this model as supporting twelve feature switches.
All twelve were read back from the device with the app's own request shape
(`0x010d` with a count byte followed by the wanted ids) and can be written with
`0x0403` and the two byte payload `[feature id, status]`:

| Feature | ID | State on the owner's unit |
|---|---:|---|
| Wear detection | `04` | on |
| Low latency game mode | `06` | off |
| Vocal enhancement | `09` | off |
| Hearing enhancement | `0b` | off |
| Personalised noise cancellation | `0c` | on |
| Tap to take photo | `0d` | on |
| Dual connection | `11` | on |
| High quality audio | `18` | off |
| Spatial sound | `1b` | off |
| Bass engine | `1d` | on |
| Diagnostic logs | `1e` | on |
| Game equalizer | `21` | on |

## BassWave (bass engine)

The bass engine is a feature switch (`1d`) plus a level. The level travels as
three bytes `[min, max, value]`, the same shape the app sends, and the device
echoes them back. The owner's unit reports the range `-10` to `+10`.

| Direction | Command | Payload |
|---|---|---|
| Read | `0x0124` | empty; answer `[status, min, max, current]` |
| Write | `0x041b` | `[f6, 0a, value]`, value signed |

## Find my earbuds

`0x0400` with the payload `[01]` rings the earbuds, `[00]` stops the tone.

The app's Play control becomes a stop action while playing (its graphic uses
a pause symbol). `HeadsetCoreService.O0` sends the boolean as one byte; the
app accepts status00 from `0x8400`, and `cb.d$f.Q` schedules a Stop after50s.
REA wire Evidence: `ev_d75c730c05579cde8388db0785bfe978267338ef64d7fe81f2e4cdee057665a6`;
Stop-state Evidence: `ev_c6e50983a7a76e5ae1c14028465acb85f26771650b67d9916da1ba6c61e0483e`.

The plugin now renders `▶ Find my earbuds` / `■ Stop` from shared backend
state, parses the find acknowledgement itself (the previous ANC-only parser
discarded it), and keeps Stop available after an unconfirmed start/stop.
The controller's per-device50s deadline attempts one automatic Stop. Closing
or destroying an open panel also stops, including cancellation during a pending
start. Graceful helper shutdown stops its owned search if the link is available.
Queued commands carry a device token so recovery cannot redirect them to
another pair. No uncertain start is automatically replayed.

Live test on2026-10-31, with the owner confirming buds were in the open case
and outside the ears: Start accepted with status00, frontend `ringing` after
144.9ms; Stop sent0.35s later, accepted00 and `stopped` after142.7ms.
No acoustic recording was made. Timeout, rejection,50s expiry and device
replacement are covered by automated tests. The interface displays a short
remove-earbuds hint; it does not yet read actual wearing status.
The final device-bound version was additionally tested through actual native
Play/Stop clicks: both returned status00, the panel showed Stop while active,
and the final state was stopped without using the fallback stop command.
The local REA export is
`~/src/oneplus-buds-research/rea-find-earbuds-2026-10-31-evidence.json`.

## Touch controls (2026-10-28)

The authenticated, payloadless query `0x0108` returns `0x8108` with
`[status=00, count, (deviceType, button, action, function)…]`. The owner's unit
reports ten entries: five for each earbud. Device type 1 is left, 2 is right;
button 1 is touch. A single assignment is written with `0x0401`, payload
`[01, deviceType, 01, action, function]`; its `0x8401` ACK contains status `00`.
Each write is verified with a fresh correlated `0x0108`, never just the ACK.

| Gesture | Wire action | Original function, both sides | Writable function IDs |
|---|---:|---|---|
| Single tap | 1 | None (0) | 0, 1 |
| Double tap | 2 | Next track (6) | 0, 1, 2, 3, 5, 6, 17 |
| Triple tap | 3 | Previous track (5) | 0, 2, 3, 5, 6, 17 |
| Touch & hold | 4 | Switch noise control (8) | Shared cycle editor below |
| Long hold | 6 | None (0) | 0, 11, 12 |

Functions: 0 none, 1 play/pause, 2 play music, 3 voice assistant, 5 previous
track, 6 next track, 11 volume up, 12 volume down, 17 game mode. Function
labels come from `A9/d.java` in the phone app. Acceptance of an assignment
does not prove its action is implemented by every connected audio host.

The model table's support masks are 516 (single), 8807 (double), 8803 (triple)
and 536 (long hold). They describe app function bits, **not** wire function
IDs. `EarphoneUtils` (`model/repository/earphone/I.java`) maps app action 11
to wire action 4. Its function stays noise control; the modes included in its
shared cycle are configurable separately (see below). Call gestures are unchanged.

All 36 allowed side/action/function combinations were written, acknowledged
with status `00`, and confirmed by a fresh query through the running plugin
bridge. Each gesture was restored after testing; a final comparison confirmed
the complete original ten-entry table was restored. The address-free evidence
is in `docs/measurements/2026-10-28-nord-touch.json` and regressions are in
`tests/test_nord_buds_3_pro.py` and `tests/test_touch.py`.

The panel reads assignments on opening and offers Refresh for changes made
in the phone app. Failed or uncertain reads invalidate the table and require
a successful fresh read before editing again. No write is retried.

### Shared Touch & hold noise-mode cycle

The decrypted model table has no `longPressType` override (default 0), and its
hold entry has `showEar=1`. `control/a.java:w()` in the decompiled phone app
constructs `NoiseReductionInfoDTO(2, 1, bitmap)` for that case. The OnePlus
branch in `p079fb/z0.java` sets the minimum selection count to two.
`NoiseReductionInfo.getData()` encodes action/type followed by the bitmap;
`HeadsetCoreService.i1()` sends that object using command 1028 (`0x0404`).

| Operation | Command | Payload |
|---|---|---|
| Query saved cycle | `0x010c` | `02 01` |
| Query response | `0x810c` | `00 02 01 <mask>` |
| Write saved cycle | `0x0404` | `02 01 <mask>` |
| Write acknowledgement | `0x8404` | `00` |

This is **not** command `0x0402`, and it must not be confused with the current
ANC command: that uses action 1 (`01 01 <current mode>`). Cycle action 2 does
not select a current ANC level.

Off is bit0 (`01`), noise cancellation bit1 (`02`), transparency bit2 (`04`).
All four app-valid combinations were written through the running plugin,
acknowledged with status 00 and confirmed with a fresh correlated query:

| Included modes | Mask |
|---|---|
| Noise cancellation + Off | `03` |
| Off + Transparency | `05` |
| Noise cancellation + Transparency | `06` |
| All three | `07` |

The original mask `06` was restored in a finally block, then read back. All ten
ordinary touch assignments were compared before/after and remained identical.
Address-free evidence: `docs/measurements/2026-10-28-nord-hold-cycle.json`.
The physical press-and-hold gesture was not automated; these measurements
verify stored configuration and protocol replies, with gesture semantics
corroborated by the phone app.

The panel offers one shared checkbox editor for both earbuds inside the
collapsed Touch controls section, with explicit Apply/Cancel and minimum two
choices. Unsaved changes survive ordinary snapshot updates and folding;
failed verification restores the actual readback. Invalid read masks (including
fewer than two bits), malformed ACKs and lost readbacks invalidate the state.

Custom EQ is a full-width subsection under Earbud EQ, after presets and
before BassWave. Both disclosures start closed every time the panel opens.

## Comparison with the upstream reference models

The protocol layer is the shared OPOv1 family: 0xAA framing, RFCOMM channel 15,
HELLO/REGISTER authentication, `0x0103` product query, `0x0106` battery query,
`0x010c` ANC query and `0x0404` ANC set. The ANC bitmap and the write payload
`01 01 <bitmap>` are identical to the Buds Pro 2, which is why the same transport
and session code works unchanged.

Public reverse engineering of the ColorOS "Wireless Earphones" app
(`com.oplus.melody`) confirms the payload shape: `CurrentNoiseModeInfo.getData()`
emits `01 <type> <bitmap bytes>` for the bitmask mode type, which is exactly the
frame this backend sends. The app's own preset names are fetched per device from
the manufacturer's server configuration, so they are not part of the APK.

The app also keeps an encrypted copy of the whole device table in
`resources/res/raw/melody_app_whitelist.json`, encrypted with AES/GCM under the
SHA-256 of the app's signing certificate. Decrypted, it lists the noise modes,
the equalizer presets, the feature switches and the gesture layout for every
supported model. For `064414` it agrees with every measurement taken here.

## Still to verify later

- Case battery behaviour with the case deliberately opened and closed
- Whether the seven EQ factory slots keep their names across firmware updates
- Repeated-operation timing across firmware revisions and longer stress runs
