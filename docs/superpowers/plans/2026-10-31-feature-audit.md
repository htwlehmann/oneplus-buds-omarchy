# Feature labels and Find tooltip

Approved scope: move the idle Find warning to the Play button tooltip, then
check the read-only feature list against the shipped app and Nord model table.
Work inline in the installed fork. No feature writes or live sound tests.

- [x] Move the warning to the tooltip; observe failing/passing Qt regression.
- [x] Audit whitelist 064414, app defaults, UI gates and label resources with REA.
- [x] Add a model-specific feature allowlist with app labels; keep raw diagnostic
  values available, but do not infer support from generic switch replies.
- [x] Verify serialization, real QML rendering, full suites and plugin validation.
- [x] Reload and check the installed plugin; record audit limitations and commit.

The model table advertises camera control, wear detection, dual connection,
Hi-Res, Golden Sound and OnePlus 3D Audio. A subsequent live 0100 reply lacks
Golden Sound bit19 and headset spatial bit43. Hide both on the audited SPP
path; alternate phone/LE-Audio paths are not exercised by this plugin.
Low-latency, vocal enhancement and the PEL equalizer have disabled/missing app
flags for this model and must not appear based on generic raw replies alone.


Verification: 186 Python tests and18 Qt tests pass, plugin validation and
`git diff --check` pass. New filtering regressions failed before implementation.
Read-only review found no material defects. After reload, live IPC showed a
connected session, stopped search and filtered capabilities. Native panel
screenshot confirmed four correctly named read-only rows and no idle warning.
No additional hardware writes, sound test, or Obsidian edits were performed.
