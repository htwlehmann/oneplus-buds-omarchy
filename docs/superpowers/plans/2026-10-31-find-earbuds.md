# Find my earbuds implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved Play/Stop search button with truthful device confirmation and the app's 50-second stop.

**Architecture:** The existing controller owns search state and deadlines per physical device. Snapshots share confirmed/uncertain state across QML widgets; normal polling sends one stop when the deadline expires. QML renders Play/Stop and a short remove-earbuds hint, stops on panel close, and never optimistically changes the state.

**Tech Stack:** Existing Python controller/bridge, OPOv1 RFCOMM, QML/QtTest.

**Spec:** Approved conversation proposal: Play starts, Stop ends; correctly parse `0x8400`; handle rejected/uncertain writes; automatic stop after about50s; retain stop-on-close. Reference shipped Wireless Earphones17.6.6: `FindDevicePreference.onClick`, `cb.d$f.Q`, `cb.d$g.q`, `HeadsetCoreService.O0`. No HeyMelody117 APK supplied.

## Global Constraints

- Work in the installed fork explicitly selected by the user; preserve existing changes.
- Start/stop are `0x0400` with one-byte `01`/`00`; ACK is `0x8400` with one status byte, successful only at00.
- No automatic replay of uncertain starts. An unconfirmed result retains a Stop option.
- A failed stop does not claim that ringing ended. Deadline stop is attempted once.
- State and deadline belong to the physical device/product; another device cannot inherit them.
- A live sound test requires buds removed from the ears; do not sound them without readiness confirmation.
- Do not edit Obsidian without consent.

## Review Focus

- Timeout/malformed ACK after start: unknown state, Stop available.
- Rejected stop: no false Play/confirmed-stopped state.
- Expiry and menu-close race: controller serializes writes and cancels deadlines after confirmed stop.
- Reconnect/device replacement: no start replay and no stop sent to a different device.
- Shell/helper shutdown: best-effort stop on the owned session; lost connectivity cannot establish remote silence.

### Task1: Confirmed backend and lifecycle

**Files:** `session.py`, `controller.py`, `models.py`, `bridge.py`, new `tests/test_find_earbuds.py`.

- [x] Add failing tests for exact wire/ACK, unknown/rejected results, bridge snapshots, expiry, disconnect and identity isolation.
- [x] Run targeted tests and observe failures.
- [x] Implement command-specific status parsing, controller-owned state/deadline, one-shot auto-stop, stop-on-shutdown, and snapshot emission.
- [x] Run targeted tests and the Python suite. Expected: all pass.

### Task2: Play/Stop panel and verification

**Files:** `BarWidget.qml`, `tests/qml/tst_hover.qml`, relevant project docs.

- [x] Add failing real-widget tests for Play→pending→Stop, unknown outcomes, confirmed Stop, panel close, disconnect and shared state.
- [x] Implement state-derived button and short hint/status. Expected: no optimistic success, no repeated start after unknown response.
- [x] Run Qt and Python suites, plugin validation and diff checks. Expected: all pass.
- [x] Request one fresh review; fix material issues with regression tests.
- [x] Reload shell and visually verify. Owner confirmed buds in open case/outside ears; both native Play/Stop clicks acknowledged00, finalstopped.
- [x] Record measurements/limits and commit the local fork. Ask about Obsidian only after completion.

Review fix: the intended device is captured before recovery, and GUI commands
carry an opaque snapshot token. A pending start retains its token for close
cancellation even if another pair appears. Regressions for direct post-loss
Stop and queued GUI cancellation were observed red then green. Final suites:
185Python tests and17Qt tests pass. No deferred material findings.

Execution: inline under the user's explicit “Setze das gerne um”; no additional plan approval required.
