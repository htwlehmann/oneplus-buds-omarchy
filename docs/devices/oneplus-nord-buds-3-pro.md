# OnePlus Nord Buds 3 Pro (owner test device)

Compatibility status: **Verified on real hardware** by the plugin owner, 2026-10-27.
This record was produced by measuring one unit locally, not by copying another
model's profile. Upstream has no maintainer verification for this product.

## Current snapshot summary (2026-11-01)

The dated sections below preserve the investigation history; later corrections
supersede earlier conclusions. Current support is Low/Moderate/High/Auto, three
named factory presets, six-band custom EQ with three profile slots, six audited
feature switches, touch assignments/hold cycle, Find Play/Stop and cached case
battery. See the [current matrix](compatibility.md) for scope and limitations.
No physical Pro/Pro 2 retest is implied. Private REA exports referenced below are
not shipped; installation and offline tests need only this repository.

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

### Charging with the buds in the open case (2026-10-31)

Measured live on the owner's unit with both buds in the case and the lid
open: the buds stay powered, so the RFCOMM session remains open and the
plugin reads fresh values instead of the cache. The raw `0x0106` answer was
`00 03 01 46 02 46 03 e4`: left and right at 70% **without** a charging
contact, the case at 100% **with** one (0xe4 = 100% + charging bit).

This sample reports the case as charging and neither earbud as charging. It
does not by itself prove a general lid-dependent charging rule. The panel shows
the charging bit reported by the device (as the upstream Buds Pro 2 screenshot
does with its lightning marks). In the owner's observed closed-lid state the
connection dropped and the panel fell back to its last known values.

### App-side battery and charging semantics (REA/JADX, 2026-10-31)

The phone app's own interpretation of the battery answer was checked against
the shipped APK (Wireless Earphones 17.6.6, `com.oplus.melody`, SHA256
`ed75c8f4…768641`). Export: `rea-battery-charging-2026-10-31-evidence.json`
(9 records, JADX headless 0.7.1; the MCP server of that session had no
`REA_JADX_MCP_JAR`, so the commands ran through the REA CLI with the same
provider and artifact).

- `btsdk/api/data/BatteryInfo` decodes every pair exactly like the plugin:
  `mLevel = value & 127` (`MASK_BATTERY_LEVEL`), `mCharging = (value & 128) != 0`
  (`MASK_CHARGING_STATE`), component id taken verbatim from the answer.
  `btsdk/protocol/commands/d` parses `count` plus that many
  `(component, value)` pairs. Evidence `ev_3beda959ea282bf88cb6567ed0911dff46f22a4cec84b5a4fba903ac7f7dcfb8`.
- `BatteryInfo.fixBattery(level, radix, component)` is new compared with the
  plugin: the app rounds the level **up** to the next multiple of the model's
  `batteryRadix` (10 when the model table has none), maps 0 to invalid (a case
  level of 1 stays 1) and caps at 100. The Nord's model table defines no
  `batteryRadix`, so a device value such as 72% is shown as 80% by the app
  while the plugin shows the raw value. Evidence
  `ev_fc1752a522f01fd0734943931801a055dbbc90141ec128438fd6170092c6aebd` and
  `ev_e42c33e3a00f0e7906a3741a1fea1ff117b9a222d788bdbf6a5f01eaea323c2e`.
- The app knows no "buds in the case" state for this model: the model table
  has an `inBoxStatus` flag per device, which switches the app from the
  battery path to the ear-status path when deciding whether the earbuds are
  connected (`model/repository/earphone/G`). The decrypted model table for
  `064414` does not set `inBoxStatus`, so the app only ever shows the
  charging bit per component - it cannot tell an open case from a closed one.
- `ui/widget/MelodyBatteryViews` renders the battery: a level of 0 hides the
  whole row, a charging flag shows the lightning image, otherwise the
  percentage is shown, and at 20% or below a red progress bar replaces it.
  Evidence `ev_d277e9b4b592b90d9a20d005b12593a68153ec50f5a6ea9a77a73601cb359c8b`.

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

### English ANC label recheck (2026-10-31)

The current labels **Low, Moderate, High, Auto** match the English resources
actually selected for064414 in Wireless Earphones17.6.6. No UI change is needed.
The whitelist pairs protocol indices6/5/4/7 with mode types3/8/4/7;
`wa.i.b(Context,Integer)` selects these resource keys:

| Internal key | App mode type | Resource | English label |
|---|---:|---|---|
| light |3| melody_common_lite_noise_reduction_title | Low |
| medium |8| melody_common_middle_noise_reduction_title | Moderate |
| deep |4| melody_common_depth_noise_reduction_title | High |
| auto |7| melody_common_intelligent_noise_reduction_title_v2 | Auto |

The APK also contains Smart in legacy/other UI contexts and Adaptive for a
separate mode type10. Neither replaces the Nord strength label Auto in this
selector. Light/Medium/Deep remain internal/plugin fallback names. The source
mapping is used by `wa.m` (NoiseReductionSelectItem); no wire payloads changed.

REA: `ev_d34f0396c6c326955330c626991544f95627e4453ce140bfa99a4bb65e2b32db`
(resource selection) and
`ev_120e3e24782b9308900f565e67f928c16f7f882650ee5d08ace63abadaae1203`
(protocol-index to model-mode-type lookup). Export and machine comparison in
research folder: `rea-anc-english-labels-2026-10-31-evidence.json` and
`anc-english-labels-2026-10-31.json`. The comparison also executed the real
BarModel.ancGroups with current profile data and confirmed all four UI labels.
APK SHA256 remains ed75c8f4ad06ebdb2100477b6db75c49931c2514127f390b259b6bff8c768641.

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
The local export is `rea-anc-app-audit-2026-10-31-evidence.json`.
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

The previous twelve-feature claim was incorrect: a generic `0x010d` switch
reply does not establish support. The audit on 2026-10-31 used Wireless
Earphones **17.6.6** (`com.oplus.melody`), whitelist entry `064414`, app defaults,
UI gates, resource labels, and a read-only capability query on the owner's unit.
No HeyMelody 117 APK was supplied.

The panel now offers only these audited entries:

| App label | ID | Plugin access |
|---|---:|---|
| Personalised noise cancellation | `0c` | verified writes |
| BassWave | `1d` | verified writes |
| Auto play/pause | `04` | verified on/off writes |
| Camera control | `0d` | verified on/off writes; camera integration depends on the phone |
| Dual connection | `11` | verified on/off writes |
| Hi-Res mode | `18` | verified on/off writes; codec/host support remains relevant |

`wearDetection=1` selects **Auto play/pause**, not the app's other label,
“In-ear detection”. **Camera control** and **Hi-Res mode** are resource titles
from this app build. The audit initially left these switches read-only.
Auto play/pause was subsequently enabled at the owner's request and tested
off/on with ACK00 plus independent readback (~0.3s each), restoring its
original enabled state. See [measurement](../measurements/2026-10-31-nord-auto-play-pause.json).
Hovering its row explains removal to pause and reinsertion to resume. Actual
media-player behavior was not tested. Feature writes now parse8403, require
status00 and matching explicit readback; absent state cannot confirm off.

Camera, Dual connection and Hi-Res were subsequently enabled at the owner's
request too. App setters use P0(13/17/24,boolean,address), then0403[id,bool].
Each was tested both ways with ACK00 and independent reads: camera~0.66s,
dual~0.66s, Hi-Res~0.45s (includes the additional verification query). Original
camera/dual=on and Hi-Res=off were restored. A delayed reset followed Hi-Res
off; the next read failed transiently. Two settled full reads confirmed all
original values on a connected session. See
[measurement](../measurements/2026-10-31-nord-remaining-features.json).

Both Hi-Res directions may disconnect/reconnect according to the app resources.
For connection-changing11/18, the controller attempts one recovery to the
captured address and product, then reads the setting without replaying the
write. A matching value from the same pair can confirm the stored setting even
if the original ACK was lost. Explicit rejection stops immediately; it cannot
be converted into success by recovery. Wrong identity, missing readback or
failed recovery stay unverified. Later resets use normal service recovery.

The three row tooltips explain compatible phone camera operation, two-device
connection, and high-resolution host support with possible reconnection.
A setting readback does not establish actual Linux camera integration, codec
resolution or simultaneous media behavior. The existing Verified feedback stays.
REA exports in the research folder: rea-camera-dual-controls-2026-10-31-evidence.json
and rea-hires-controls-2026-10-31-evidence.json. Hi-Res setter Evidence:
ev_54dbaf2014c0eeb4317908aa25d9a05e121e39ca0a8ff03bd2cb8e23c4bed6db.


Hidden entries:

- `06`: separate **Game mode** switch lacks `gameMode`/`gameModeList` support in
  this model configuration. This does not remove the existing gesture action.
- `09`: **Vocal enhancement** defaults to disabled/unavailable (`-1`).
- `21`: **Enhanced PEL audio**, a Peacekeeper Elite option, lacks its required
  `gameEqPkgList`; “Game equalizer” was misleading.
- `0b`: model configuration names this **Golden Sound**, but the device lacks
  its SPP capability `277` (bitmap bit19).
- `1b`: model configuration names this **OnePlus 3D Audio**, but the device lacks
  headset spatial capability `61187` (bit43). Phone-side and LE-Audio app paths
  can expose alternatives; neither proves support in this plugin's SPP path.

The measured `0x8100` reply was `00 ff 27 52 ee c7 14`: success byte followed by
LSB-first capability bits, decoded with app methods `k.G` and table `B6.a`.
Camera capability `1039` (bit20) is present. See
[measurement](../measurements/2026-10-31-nord-feature-audit.json).

The audited feature-label map filters UI entries and reported capabilities.
Raw switch replies stay available in frontend diagnostics. Other profiles retain
their previous discovery behavior. This audit applies to the tested firmware;
future firmware can require another audit. Historical “Diagnostic logs” (`1e`)
was not part of the current displayed list and is not claimed as supported.

REA exports in the research folder: `rea-readonly-features-2026-10-31-evidence.json`
and `rea-readonly-main-2026-10-31-evidence.json`. Key Evidence:
`ev_fb43c28250ab2b8891b6daf049b3baf3d30851c27faed845cd4dba34d8aafe3e`
(capability parser), `ev_f4919d53828367e407783b625470f7af9bec9114b2196800679f488414a357a5`
(UI gates), `ev_02581a646ea51dc8d64b4a751ffff7346540a9947cd46f9d74bb8c209c16d56e`
(Auto play/pause title), `ev_8d09246abff5666913e175caf5574c9693098d4be422c81c183ca1f7a251e9f3`
(Hi-Res title).

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

The idle remove-earbuds hint is a tooltip on Play, with no permanent warning
row. Pending, playing and uncertain status remain visible.

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
`rea-find-earbuds-2026-10-31-evidence.json`.

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


## Custom EQ curve editor (2026-10-31)

Custom EQ now shows the six device bands as draggable points and a smooth
bounded curve. Range and step come from the device entry (Nord-6..+6dB,1dB).
The shell accent controls stroke, point borders, numbers and the filled area,
which fades down to transparent. No new audio filter or wire mapping is used.

Changed release saves once, then the backend independently verifies the curve;
there are no writes while dragging. Up/Down supports the focused point. Selecting
an existing custom slot activates it without an Apply button. Pending saves
block interaction. Failed/unconfirmed responses settle from actual device state.
Cancelling a gesture or changing device/slot does not save.

A native pointer test changed62Hz4->5->4 with ACK00 and verified readback.
An independent query during each held drag showed the previous62Hz value.
The original full curve and entry7 were restored after the test. See
[measurement](../measurements/2026-10-31-nord-eq-curve.json).

### Custom EQ profiles: create, rename, delete (2026-10-31)

The phone app (Wireless Earphones 17.6.6) creates and renames custom profiles
with the same `0x0418` command that edits a curve. The first payload byte is
the action: `1` creates a profile, `2` updates it (curve **or** name) and `3`
deletes it. The remaining payload is the entry definition
`[min, max, eq_id, name_length, name, band_count, (frequency_u16le, gain_i8)…]`
and is identical for all three actions.

Measured on the owner's unit through the running plugin bridge:

| Operation | Action | Result |
|---|---:|---|
| Create `Plugin Test` | 1 | ACK `00`; new profile stored as id 9 with a flat curve |
| Rename id 9 to `Plugin Test 2` | 2 | ACK `00`; new name stored, curve unchanged |
| Delete id 9 | 3 | ACK `00`; profile removed from the catalogue |

The device accepted the requested next free slot id (9) directly; the phone
app sends `0` and lets the device choose the slot. The plugin asks for the next
free id (factory presets occupy 0..6, the existing custom profiles 7 and 8)
and learns the stored id from a fresh `0x0122` catalogue read. Band layout and
gain limits are always copied from a device-declared profile, never invented.

Writing a custom entry also selects it on this firmware. Creating or renaming
a profile therefore re-selects the profile that was active before the write,
so the sound does not change silently. A rejected or unconfirmed write is
never repeated; the panel keeps the typed name and shows the error.

The test profile was deleted afterwards and the catalogue was identical to the
starting state (id 7 `Test eq` `[4,6,2,0,4,6]`, id 8 `Benutzerdefiniert1`
`[-5,0,-6,0,0,0]`, id 8 active). See
[measurement](../measurements/2026-10-31-nord-eq-profiles.json).

The panel shows the profile dropdown shortened with a pencil button (rename),
a plus button (new profile) and a trash button (delete profile) on the right.
The pencil and the plus turn the dropdown into a name field; the plus button
stores a new profile in the next free slot, the pencil renames the selected
profile. The trash button asks for confirmation and then removes the selected
profile, which frees a slot for a new one.

The earbuds hold exactly three custom profiles (ids 7, 8 and 9); a create with
id 10 was refused by the device. The plugin therefore uses the first free id
of that range, refuses a create with a clear message when every slot is in
use and greys out the plus button with the hint "All custom EQ slots are in
use. Delete a profile to add another."

The delete action exists in the backend and the CLI as well, so a test state
can be restored. The profile dropdown keeps the name of the profile that was
selected: the Omarchy `Dropdown` writes its own string value when the user
picks an entry, so the value is explicitly synchronized with the existing slot
index. Touch selections use the same themed component and immediately restore
their binding to the device-confirmed function. Backend commands are unchanged.

The name field needs the keyboard, so the panel uses the shell's
`KeyboardPanel` (layer-shell with a keyboard focus prime) instead of the
xdg-popup based `PopupCard`. With the popup, the field never received key
events; with the keyboard panel the typed name reaches the field, Enter
stores it and the profile appears in the catalogue. This was verified live on
the owner's unit: typing `Rock` in the panel and pressing Enter created the
profile as id 9 with a verified readback; the test profile was deleted
afterwards.
