# Auto play/pause implementation plan

**Goal:** Enable the requested Nord Auto play/pause switch with a hover tooltip.
**Spec:** User requests on/off and a suitable tooltip. Existing label stays.
**Architecture:** Reuse feature04 and0403 writes, command-specific8403 ACK,
fresh010d readback, controller-owned confirmed state, immediate bridge snapshot.
**Tech stack:** Existing Python session/controller/bridge and QML feature rows.

Inline work in the explicitly selected installed fork; no other feature unlocks.
Tooltip: Remove either earbud to pause playback; put it back in to resume.
This explains the app's intended behavior; a hardware setting test does not
establish media-player behavior. Preserve the original device setting after
off/on hardware verification. No Obsidian edits without consent.

- [x] Confirm SmartPlayItem setter P0(4,boolean,address) with REA.
- [x] Add regressions for real wire payloads, ACK/status and missing readback;
  bridge snapshots and real-widget pending/confirmed/rejected behavior.
- [x] Correct feature ACK/readback handling; allow wear_detection for Nord;
  add tooltip and truthful unsuccessful outcome. Observe tests red then green.
- [x] Run suites and plugin validation, fresh review, reload; test off/on with
  independent reads and restore the original setting. Record limits and commit.

Review focus: rejected/malformed ACK must not succeed; missing readback is not
false; click must not optimistically flip state; other read-only features stay
blocked; tooltip hover must not intercept toggle clicks.


Verification: 189 Python/19 Qt tests pass; plugin validation and diff check pass.
Fresh review found no blocking defects. Native hover displays the tooltip in
panel colors; real clicks verified both directions with status00 and matching
snapshots. Independent reads verified false/true in298.8/296.4ms. Original true
restored. Media playback/removal behavior was not exercised. No Obsidian edits.
