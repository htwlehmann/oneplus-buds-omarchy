# Collapsible Controls Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline.

**Goal:** Reduce panel clutter with independent Custom EQ and Touch controls disclosures.
**Architecture:** Keep the existing controls instantiated; hide them from the
Column layout until their heading button is expanded. Reset both on panel
opening. Preserve preset selection, the active EQ label and the fixed width.
**Tech Stack:** QML and existing QtTest harness; no dependencies.
**Spec:** Owner approved the preceding proposal: two independent sections,
closed by default, existing controls inside, presets and current EQ outside.

## Global Constraints

- Change presentation only; no device writes during validation.
- Work in the installed plugin fork; keep the current feature branch.
- Panel width stays fixed; existing scrolling handles expanded content.

## Review Focus

- Hidden controls must release layout height and keyboard focus.
- Expanding either section must not open the other or send a setting write.
- Collapse/reopen within the panel must preserve unsaved EQ edits.
- Fresh panel opening resets both sections, including after data arrives.
- Missing capabilities keep headings hidden; narrow layout stays usable.

### Task 1: Implement and verify the disclosures

Files: `BarWidget.qml`, `tests/qml/tst_hover.qml`, `HANDOFF.md` in research folder.
Interface: heading buttons toggle `customEqExpanded` and `touchControlsExpanded`;
all existing write/read command contracts remain unchanged.

- [x] Add Qt checks for default collapse, independent toggles, height/width,
  preserved edits, panel reopening and absent capabilities; observe failure.
- [x] Replace section headings with focusable disclosure buttons; gate child
  visibility on the corresponding expanded property.
- [x] Run `python3 tests/run_qml_hover.py` and the Python unittest suite.
- [x] Review, validate the plugin, clear QML cache/restart shell and inspect the
  compact live panel without sending device writes.
- [x] Update handoff and commit locally.

## Execution record

- Added Qt regression, observed missing disclosure failures, then implemented
  the two headings with expanded-state visibility guards.
- Geometry assertions wait for Qt layout polish; folded content releases height.
- Focus regression exposed retained input focus in invisible controls; enabling
  controls only when expanded fixes it without discarding EQ draft values.
- Independent review: no remaining Critical, Important or Minor findings.
- Validation:144 Python tests and11 Qt tests passed; plugin validation passed.
- Live shell inspection:600px width,852px height with both sections collapsed,
  current EQ and presets visible, connected and no pending/error state.
- No device setting writes during this presentation change.
