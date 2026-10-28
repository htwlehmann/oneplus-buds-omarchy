# Touch Controls Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Configure left/right touch gestures from the plugin panel.
**Architecture:** Parse 0x8108, write one entry using 0x0401, verify with 0x0108.
Carry typed bindings through controller snapshots; serialize allowed choices
from the model profile. QML uses the existing serialized request queue.
**Tech Stack:** Python standard library, Qt Quick Controls, unittest/QtTest.
**Spec:** `docs/superpowers/specs/2026-10-28-touch-controls-design.md`

## Global Constraints

- Work in the requested installed plugin fork; feature branch protects main.
- No additional dependencies. No codec writes. Restore hardware test changes.
- Only product 064414 receives editable touch controls.

## Review Focus

- Truncated, failed, duplicated or malformed binding tables must fail closed.
- Invalid JSON types, unknown gestures and unsupported products cannot write.
- ACK alone does not prove a change; mismatched readback stays visible.
- Disconnects clear stale bindings and disable controls.
- Narrow layouts, unknown function IDs and failed requests remain usable.

### Task 1: Backend

Files: new `src/oneplus_buds/touch.py`, `tests/test_touch.py`; modify
`protocol.py`, `profiles.py`, `session.py`, `models.py`, `controller.py`, `bridge.py`.
Interfaces: `TouchBinding(device_type, button, action, function)`,
`parse_touch_bindings(Frame)`, `OpoSession.touch_bindings()`,
`OpoSession.set_touch_binding(TouchBinding)`, controller `touch_controls()` and
`set_touch_control(side: int, action: int, function: int)`; bridge commands of
the same names, snapshot `touch_controls` containing enriched bindings.

- [x] Write tests for the measured ten-entry frame, invalid tables, one-entry
  payload, model/function/side gates, mismatched readback and bridge validation.
- [x] Run `PYTHONPATH=src python3 -m unittest discover -s tests -p test_touch.py`;
  expect missing touch implementation failures.
- [x] Implement the interfaces, profile choices and snapshot serialization.
- [x] Run `PYTHONPATH=src python3 -m unittest discover -s tests`; expect all pass.

### Task 2: Panel and hardware verification

Files: `Service.qml`, `BarWidget.qml`, `tests/qml/tst_hover.qml`, device record.
Consumes: snapshot `touch_controls`, bridge commands from Task 1.
Produces: a capability-gated full-width Touch controls section with left/right
selectors, fixed hold/call descriptions, refresh and verification feedback.

- [x] Add Qt tests for selectors, allowed options, request parameters, missing
  capabilities, readback mismatch and disconnected controls; run to see failure.
- [x] Implement the section and service calls using existing pending requests.
- [x] Run the Python suite and `python3 tests/run_qml_hover.py`.
- [x] Restart the shell with QML cache cleared, inspect the rendered panel,
  exercise writes/readbacks through the bridge, restore all original bindings.
- [x] Update the device record and handoff with confirmed measurements.
- [x] Review the diff, run plugin validation and commit the finished feature.

## Execution record

- Native execution in the requested installed fork, branch
  `local/touch-controls-2026-10-28`; no external worktree.
- Backend regressions observed failing before implementation; initial suite
  129 passed. Touch parsing, gates, bridge and readback tests then passed.
- Qt5 runner selection and missing pre-existing UI stubs prevented the old Qt
  tests from loading. Corrected the runner to Qt6 and supplied those stubs.
- New Qt selectors/layout/verification tests observed failing, then passed.
- Hardware: all36 assignments ACK00 plus fresh readback; original10 restored.
- Independent review: one Important finding, uncertain writes left stale state.
  Fixed with failing Python and Qt regressions: invalidate/close uncertain
  sessions, publish invalidation, display only confirmed selector values.
- Scope: fixed noise-control hold and call gestures remain display-only.
  Other feature switches and the codec were untouched.
