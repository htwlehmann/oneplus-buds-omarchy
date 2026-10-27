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
| ANC On (preserve level) | 1 / `02` | active level index | Verified |
| Transparency | 2 / `04` | 2 | Verified |
| Deep | 4 / `10` | 4 | Verified |
| Medium | 5 / `20` | 5 | Verified |
| Light | 6 / `40` | 6 | Verified |
| Smart | 7 / `80` | unchanged | Not supported |

Two behaviours differ from the Buds Pro 2 and are worth keeping in mind:

- The main ANC On command (`02`) does not report the parent mode. The device
  answers with the level it actually applied (`10`, `20` or `40`). The first
  measurement after a cold start reported Deep; a later measurement kept the
  previously selected Light level.
- Byte `80` (Smart on the Buds Pro 2) is acknowledged with status `00` but is
  never applied: the read-back still reports the previous level. Smart is
  therefore not offered for this model.

## Native EQ

The device accepts the seven factory IDs 0 to 6 and ignores 7 and 8: a selection
is acknowledged with status `00` and confirmed by a fresh `0x010f` read, while
unknown IDs leave the current selection untouched.

The native EQ catalogue query (`0x0122`) answers `00 00`, so the device publishes
no preset names, band definitions or custom entries of its own - unlike the
Buds Pro 2, which returns two writable custom curves. The plugin therefore
offers preset selection only, and names the seven factory slots generically
until the phone app's labels are confirmed for this firmware.

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

## Still to verify later

- Case battery behaviour with the case deliberately opened and closed
- Whether the seven EQ factory slots keep their names across firmware updates
- Repeated-operation timing across firmware revisions and longer stress runs
