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
