# Changelog

## Unreleased — 0.1.0 release candidate

- Add an owner-verified device profile for the OnePlus Nord Buds 3 Pro
  (`064414`): measured ANC bitmap including Auto, seven native factory
  EQ slots without custom curves, plus device record, compatibility entry and
  regression tests that pin the measured wire values.
- Bring the panel to feature parity with the phone app: the app's feature
  switches (personalised noise cancellation, BassWave, low latency game mode,
  wear detection, dual connection and more), a BassWave level slider from -10
  to +10, a find-my-earbuds button, and the app's own ANC intensity names
  (High, Moderate, Low, Auto) and equalizer names (Ausgewogen, Serenade, Bass).
- Read and write the feature switches the way the phone app does: `0x010d`
  with a count byte plus the wanted ids, and `0x0403` with the two byte
  payload `[feature id, status]`, always confirmed by a fresh read.
- Read and write the bass engine level (`0x0124` and `0x041b`), and follow the
  noise mode the device pushes, so the panel also shows changes made in the
  phone app.
- Distinguish Verified, Community Tested and Experimental device evidence in the
  backend and panel; only Buds Pro and Buds Pro 2 remain hardware-verified.
- Add a compact experimental-device notice and user-controlled compatibility
  report workflow, available to every connected device, with backend privacy
  redaction and no automatic upload.
- Propose privacy-safe model/date report filenames and guide successful saves to
  the dedicated GitHub compatibility template for manual attachment.
- Simplify public issue templates around the generated report and plain-language
  physical compatibility checks.
- Clarify marketplace metadata, compatibility documentation and GitHub issue
  intake for untested OnePlus/OPO-compatible models.

- Hardware-verified OnePlus Buds Pro and Buds Pro 2 identity, battery, firmware,
  ANC On/Off/Transparency and supported strengths.
- Generic transport-independent OPO framing, RFCOMM transport, device profiles,
  typed backend, privacy-safe diagnostics and serialized session ownership.
- Persistent authenticated sessions for verified main-mode changes; recorded
  warm transition medians of 260 ms on Pro and 167 ms on Pro 2. Audible response
  time was not measured; explicit strengths retain conservative setup.
- Combined Omarchy service/bar plugin with one backend helper and reconnect logic.
- Compact idle icon, battery hover expansion and delayed collapse.
- Responsive themed panel with full-width device status, balanced noise-control
  and earbud-EQ columns, compact preset/custom-EQ grids, and a narrow scrolling
  fallback.
- Native earbud EQ with model-specific verified presets, fresh read-back, Pro 2
  device-defined six-band custom curves, and capability-driven panel controls.
- Live EQ-panel acceptance on both reference models, including device switching,
  HeyMelody-originated state reload, and closed-case power-cycle persistence.
- Fixed Pro 2 custom-slot selection being reset by routine snapshot replacement;
  current HeyMelody names and protocol ID 7 are hardware-mapped on firmware
  `196.196.101`.
- Restored helper startup on Omarchy 4.0.3 by resolving the bundled executable
  relative to the service component instead of private manifest metadata.
- Added a privacy-reviewed live panel screenshot for the marketplace preview.
- Publication documentation, MIT license, dependency preflight, checkout-local
  CLI launcher and clean plugin exporter.

No public release or marketplace listing has been made.
