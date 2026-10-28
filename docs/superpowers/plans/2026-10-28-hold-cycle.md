# Hold Cycle and EQ Placement Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline.

**Goal:** Put Custom EQ below presets and above BassWave; configure the shared
Touch & hold cycle like the phone app, keeping both disclosures closed by default.
**Architecture:** Extend existing touch session/controller/snapshot contracts
with a model-gated hold-cycle bitmap. Query `0x010c [02 01]`, write
`0x0404 [02 01 bitmap]`; ACK is `0x8404 [00]`, fresh readback is required.
Expose one shared three-checkbox editor with explicit Apply and minimum two modes.
**Tech Stack:** Python standard library, QML Controls, unittest and QtTest.
**Spec:** Active user Goal in this thread; details below are evidence-backed.

## Global Constraints / Evidence

- Only verified product 064414 gets this editor; no dependencies or codec writes.
- App `control/a.java:w()` creates NoiseReductionInfoDTO(2,1,bitmap) when
  longPressType=0. Shared showEar=1; `z0.java` requires two choices for OnePlus.
- `NoiseReductionInfo.getData()` encodes action/type plus LE bitmap;
  HeadsetCoreService.i1 sends it via command 1028 (0x0404).
- App protocolIndex mapping: Off0, ANC1, Transparency2, hence bits01/02/04.
- Fresh hardware read `0x810c 00 02 01 06` confirms ANC+Transparency.
- Never retry a write; unknown/malformed/uncertain state is unavailable.
- Save original cycle and full ordinary touch table before hardware trials;
  restore cycle in finally and compare both tables afterwards.

## Review Focus

- Current ANC responses share command 0x810c: action/type must be checked.
- Duplicate/unknown/fewer-than-two modes and wrong JSON types must never write.
- Failed readback or malformed ACK must invalidate/publish state, not imply success.
- Phone-app reads must not erase in-progress checkbox choices.
- Hidden/disconnected editors cannot take input; fixed width/narrow layouts work.

### Task1: Backend and protocol

Files: `touch.py`, `session.py`, `controller.py`, `models.py`, `profiles.py`,
`bridge.py`, `tests/test_hold_cycle.py`, existing touch fake and Nord profile tests.
Interfaces: `read_hold_cycle() -> int`, `set_hold_cycle(modes: tuple[str,...])`
on session; controller `set_hold_cycle` and extended `touch_controls`; snapshot
`hold_cycle` with modes/options/min_selected/shared/writable or null.
Bridge `set_hold_cycle` takes `{modes: ["anc","transparency"]}`; returns verified.

- [x] Write failing tests for exact bytes, shared mode choices, model gates,
  malformed/current ANC responses, invalid lists, ACK/readback failures.
- [x] Implement, then run full Python suite.

### Task2: Panel, real device and completion

Files: `BarWidget.qml`, `Service.qml`, Qt tests, device record and handoff.
Custom EQ gets a lightly indented Column after presets and before BassWave.
Hold editor lives inside Touch controls once for both earbuds. Keep ordinary
left/right gesture selectors; suppress duplicate fixed hold rows when this
editor is available. Draft changes are local until Apply; cancel resets draft.

- [x] Add failing Qt checks for placement, shared choices, min-two validation,
  explicit Apply, preserved draft, confirmed readback and disclosure defaults.
- [x] Implement UI and service method; run Qt suite and plugin validator.
- [x] Clear QML cache/restart shell. Test all four valid cycle combinations
  through bridge with fresh readback, then restore original in finally.
- [x] Inspect live collapsed/expanded panel and evidence; review independently.
- [x] Update hardware record/handoff, verify final suites and commit locally.
- [x] Audit every Goal requirement against evidence before marking complete.

## Execution and completion audit

- Backend and Qt tests were first run red (missing implementation), then green.
- Independent review: invalid read masks with fewer than two bits were initially
  accepted. Regression failed for0/1/2/4, then parser was tightened to3/5/6/7;
  invalid state now closes session, publishes unavailability and sends no write.
- Review test-coverage gaps were filled: malformed ACK, ignored-write UI feedback
  and checkbox focus release on collapse. No deferred findings.
- Hardware evidence: four valid combinations, each ACK00 plus fresh correlated
  readback. Finally restored original ANC+Transparency and compared all ten
  ordinary assignments, identical before/after.
- Placement: Qt geometry checks prove presets precede indented Custom EQ and
  BassWave follows. Live collapsed panel screenshot confirms placement.
- Editor: Qt tests prove shared choices, minimum two, explicit Apply/Cancel,
  preserved draft, actual-state reset on ignored write and disconnected lockout.
  Live expanded screenshot confirms readable labels and current checked modes.
- Disclosure defaults: existing close/reopen Qt regression passes, and both
  collapsed headers were visually inspected in the running shell.
- Verification:157 Python tests,12 Qt tests, plugin validator and diff check pass.
- No dependency installations or persistent desktop configuration changes were
  needed for UI automation; temporary Wayland test client lives only in /tmp.
- Remaining uncertainty: physical press-and-hold was not automated. Stored
  configuration/protocol replies are measured; gesture meaning follows app code.
