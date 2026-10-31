# Remaining Nord feature controls

User requests Camera control, Dual connection and Hi-Res mode on/off, each
with a tooltip; retain the existing verified feedback. Work in installed fork.

Use app P0 switches0d/11/18 via0403, existing8403 status00 plus fresh010d
readback. Camera requires compatible phone integration; Dual supports two
hosts. Hi-Res availability does not establish the codec used by the Linux host.
Its app warns of Bluetooth disconnect/reconnect in either direction.

For Hi-Res and Dual, a lost reply/read can require one session recovery to the
captured physical address/product. Do not replay the write. A matching fresh
read from that same pair can confirm the stored setting after recovery even
when the ACK was lost. Failure/mismatch stays unverified. Explicit rejection
does not become success through recovery. Existing service retries cover a
device that is not connected yet; no new automatic audio-host configuration.

- [x] Add failing coverage for all three UI/bridge controls, tooltips and wire
  payloads, connection-loss recovery without write replay, wrong identity and
  failed recovery. Existing codec-blocked test becomes unsupported-vocal test.
- [x] Enable only these three Nord features; add tooltip descriptions and
  bounded address/product-checked recovery for connection-changing features.
- [x] Run Python/Qt suites, plugin validation and fresh review; reload plugin.
- [x] Test each setting with independent reads, restore initial values, check
  native tooltips, document evidence/limits and commit. No Obsidian edits.


Verification:193 Python tests and22 Qt tests pass; plugin validation and diff
checks pass. Fresh review found one explicit-rejection/read-loss bug: session
now returns immediately for a nonzero8403 status. Its regression was observed
red then green; no remaining material review findings.

Live ACK00 and independent reads confirmed both directions for all three.
Camera and Dual returned to true; Hi-Res returned to false. Hi-Res off was
followed by a delayed reset and transient read failure; a targeted010d18 reply
and two settled full reads confirmed false with a connected session. Native
hover verified all three tooltips, including wrapping and panel colors.
No actual photo, negotiated audio resolution or two-host media test performed.
No Obsidian edits.
