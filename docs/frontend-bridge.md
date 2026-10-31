# Frontend bridge contract

Status: pre-QML bridge boundary, schema version 1, 2026-09-06.

`BudsFrontendBridge` is the UI-toolkit-neutral boundary between the hardware-verified service runner and a future Omarchy frontend. It does not create a process, thread, socket, D-Bus name, or QML object. Those deployment choices remain deliberately open until current Omarchy integration requirements are inspected.

The bridge owns one `BudsServiceRunner`, and the runner and all routed commands share one `BudsController`. The controller remains the sole RFCOMM session owner and serializes polling, refreshes, and verified writes.

## Lifecycle and event dispatch

`run(cancelled)` blocks until the supplied `threading.Event` is set. The bridge accepts two frontend integration callbacks:

- `emit(event)` receives schema-versioned, JSON-compatible dictionaries.
- `dispatch(callback)` schedules delivery onto the consumer's event loop. If omitted, delivery is synchronous. A QML integration must supply a queued dispatcher rather than touching UI state from the service thread.

Events have `schema_version: 1` and one of these shapes:

```json
{
  "schema_version": 1,
  "type": "connection",
  "connection": "connected",
  "attempt": 0,
  "retry_delay": null,
  "error": null
}
```

```json
{
  "schema_version": 1,
  "type": "snapshot",
  "snapshot": { "generation": 3 }
}
```

Connection values are `connecting`, `connected`, `disconnected`, `reconnecting`, and `stopped`. Errors are address-redacted.

## Snapshot contract

`serialize_snapshot()` includes device/status data, compatibility, static and device-observed capabilities, supported ANC modes, named feature-switch state, session state, safe numeric event-code history, reconnect/ignored-frame counters, and generation. Tuples are converted to JSON arrays and mappings are copied.

Bluetooth addresses, raw OPO frames, pairing data, and raw notification payloads are never included. Unknown products are marked `experimental` and receive no inferred write modes or static capabilities.

For profiles advertising `case_battery`, `status.battery.case` may include
`last_known: true`. This means the current sample omitted the case or returned
an unusable level, so `percentage` is the last valid 1..100 reading for that
physical device and product. Its `charging` is always false. The default bridge
persists these levels in the user's XDG cache directory; cache failures do not
interrupt control. Without a previous valid level, the case field is omitted.

## Commands

`execute(command, parameters, request_id=...)` currently accepts only:

- `snapshot` with no parameters: returns the cached state without Bluetooth I/O.
- `refresh` with no parameters: performs a serialized one-shot refresh and emits the resulting snapshot.
- `set_anc` with exactly `{"mode": "..."}`: uses the existing authenticated, profile-gated, query-after-write verified controller path and emits the resulting snapshot.
- `eq_status` with no parameters: freshly reads native EQ state and device-declared
  custom capabilities on the existing authenticated session.
- `set_eq` with exactly `{"preset": "..."}`: selects only a verified factory key
  or device-declared custom ID and refreshes the emitted state after read-back.
- `set_custom_eq` with exactly `{"entry_id": number, "gains_db": [integers...]}`:
  delegates strict band-count/range validation to the device capability layer,
  sends once, and emits only freshly verified state.
- `create_custom_eq` with exactly `{"name": "..."}`: creates one new custom
  profile in the next free device slot. The band layout and gain limits are
  taken from the device, the slot id is read back from the device catalogue,
  and the profile that was active before the write is re-selected afterwards.
- `rename_custom_eq` with exactly `{"entry_id": number, "name": "..."}`: renames
  one device-declared custom profile without changing its curve and re-selects
  the previously active profile.
- `delete_custom_eq` with exactly `{"entry_id": number}`: removes one
  device-declared custom profile. It exists to restore a test state and is not
  exposed in the panel.
- `save_diagnostic_report` with exactly `{"path": local-file-url}`: builds a
  privacy-safe report from the cached snapshot and bounded recent errors, then
  writes it to the user-selected local path. It performs no device query or write
  and never uploads the report.

Every call returns a `command_response` dictionary containing the schema version, request ID, command, `ok`, `result`, and `error`. Unknown commands and malformed parameter objects are rejected without hardware access. Runtime command errors are address-redacted. The bridge does not add unverified controls or bypass backend capability/profile checks.

The custom profile commands optionally accept `{"device_id": "<opaque token>"}`
from snapshot field `find_device_id`. The token rejects a command when the
connected pair changed since the panel read the state.

Report sanitisation lives in `oneplus_buds.report`, not QML. Reports omit device
aliases, Bluetooth addresses, usernames, hostnames, home paths, credentials,
unrelated devices and raw protocol frames. Only bounded numeric protocol counters
and event codes are included for protocol diagnostics.

## Process adapter

`python -m oneplus_buds.bridge_host` carries the same contract over newline-delimited JSON for the future Omarchy QML service. Asynchronous connection/snapshot events and command responses share stdout and are distinguished by `type`; requests arrive on stdin. EOF, `SIGINT`, and `SIGTERM` cancel the runner and wait for controller shutdown.

The deployment rationale and Omarchy lifecycle are documented in [omarchy-integration.md](omarchy-integration.md). This is a private child-process protocol owned by the plugin, not a public system-wide IPC service.

ANC responses now carry additive `result.timings_ms` on success and
`error.timings_ms` on expected timed failures. See [ANC phase timing](backend-api.md#anc-phase-timing)
for units, nested totals, privacy scope, and the completed two-model hardware measurements.
Timing values do not imply successful verification; consumers must still check
`ok` and `result.verified`.

All profile-supported ANC requests reuse the running controller's authenticated
session and existing subscriptions, including explicit strength and Auto.
Success requires a fresh, correlated state query; on Nord Auto, a selected-mode
notification can confirm Auto when the query reports its concrete active
intensity or times out. A SET acknowledgement alone never verifies Auto.
The result and matching snapshot are captured atomically, and no
monitoring restoration blocks successful response delivery. Cold/legacy paths
retain conservative authentication; see the timing documentation for scope.

## Local fork: find my earbuds

`find_earbuds` accepts `{"ringing": boolean}` and optional `device_id` from
snapshot field `find_device_id` (an opaque hash, never a Bluetooth address).
The GUI captures that token with the request, including cancellation of a
pending start. Recovery and token validation reject a changed pair before I/O.
It uses `0x0400` with
`01` to start or `00` to stop. Like the phone app, it reads the first status
byte of a nonempty `0x8400` reply; only status00 acknowledges the request.
An ANC acknowledgement is not a search acknowledgement. This confirms the
command was accepted, not that a microphone detected an audible sound.

The result includes `ringing` (requested value), `sent`, `set_status`,
`acknowledged`, and `state`. Snapshot field `find_state` is `stopped`, `ringing`,
or `unknown`. Missing/malformed replies or transport loss after a possible
start leave Stop available; rejected stops never establish silence. A rejected
idle start remains stopped. The bridge immediately publishes the matching
snapshot, shared by all widgets.

The controller owns a 50-second deadline for each physical device/product,
including unconfirmed starts. Normal polling attempts one stop on expiry.
An unconfirmed automatic stop remains unknown and is not repeatedly replayed.
Disconnect does not establish silence; the same helper retains unknown state
for that pair across reconnects and does not send it to another pair. Graceful
shutdown attempts to stop an owned search before closing the session. A lost
link or forcibly killed helper cannot guarantee remote silence.

The panel renders `▶ Find my earbuds` / `■ Stop`, follows snapshot state rather
than optimistically toggling, and sends Stop on close (also during a pending
start and when an open widget is destroyed). It shows a short remove-earbuds
hint; the backend does not currently know the physical wearing state.

## Local fork: touch controls

For the verified Nord Buds 3 Pro, snapshot capability `touch_controls` enables
the panel section. Snapshot field `touch_controls` is an array of bindings:
`side`, `button`, `action`, `function`, display labels, `options` (`value`,
`label`) and `writable`. Only known profile choices are writable.

- `touch_controls` with `{}` refreshes and publishes the complete table.
- `set_touch_control` with integer parameters `side`, `action`, `function`
  writes one button-1 entry and returns `set_status` and `verified`, then
  publishes actual readback. Only sides 1/2 are allowed. Failure to confirm
  yields `verified: false`; transport or malformed-response failures return
  an error and publish an unavailable/empty table. Writes are never retried.

The same refresh reads `hold_cycle` for the verified Nord profile. This is null
when unavailable, otherwise `{modes, options, min_selected:2, shared:true,
writable}`. `set_hold_cycle` takes a string array `modes`, e.g.
`{"modes":["anc","transparency"]}`. At least two distinct known modes are
required (`anc`, `off`, `transparency`). It writes action2/type1 using the ANC
command, then publishes actual cycle readback. A rejected/ignored change has
`verified:false`; malformed/uncertain replies emit unavailable state and return
an error without retrying the write. This does not change the current ANC mode.
