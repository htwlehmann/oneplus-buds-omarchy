# Changelog

## Personal snapshot — nord-buds-3-pro-2026-11-01

This fork preserves the owner-tested Nord work on top of upstream `abe70f4`.
Package metadata remains `0.1.0`; this is not an official upstream release.
The dated snapshot tag is prepared locally; see `docs/publication.md`.

- Add the owner-tested Nord profile with Low/Moderate/High/Auto, three named
  presets, custom curves, six audited feature switches, touch assignment and
  the shared hold cycle; unknown products gain no write permissions.
- Reuse the ANC session for strengths, handle Auto confirmation, and remember
  the last valid case battery without retaining an old charging flag.
- Add Find Play/Stop, uncertain-state Stop, a 50-second best-effort stop and
  same-pair identity protection for queued writes/recovery.
- Replace gain fields with a themed curve editor that saves on changed release.
- Use Omarchy Dropdown for EQ/touch, retain device-confirmed touch selection,
  and balance feature switches across two columns.
- Prepare pinned restoration, offline backup and contribution documentation;
  correct earlier Nord support claims and retain original MIT attribution.

### Earlier local development entries

These entries retain intermediate development states. The snapshot summary above
and current compatibility matrix supersede their earlier capability assumptions.

- Create and rename custom EQ profiles like the phone app: the profile
  dropdown is shortened and gets a pencil button (rename) and a plus button
  (new profile) on the right; both turn the dropdown into a name field. The
  new profile is stored in the next free device slot with the device's own
  band layout, and the profile that was active before the write is
  re-selected. The `0x0418` action byte (1 create, 2 update, 3 delete) was
  verified on the Nord Buds 3 Pro, including a delete that restores the
  previous catalogue state.
- Use the shell's `KeyboardPanel` instead of `PopupCard` so the panel owns the
  keyboard while it is open. The old xdg-popup never delivered key events to
  the name field, which made the new profile name impossible to type and the
  profile impossible to create. The device rename field benefits as well.
- Respect the three custom EQ slots the earbuds provide: the plugin uses the
  first free id of the measured range, greys out the plus button with the hint
  "All custom EQ slots are in use" and refuses the create with a clear
  message instead of sending a write the device rejects.
- Add a trash button for the selected custom profile with a confirmation
  dialog, so a slot can be freed for a new profile.
- Keep the name of the selected profile in the profile dropdown: the control
  drops the index binding when the user picks an entry, so the index is now
  set explicitly.
- Hide the compatibility notice while no device is connected: without a known
  product the backend reported "experimental", so the panel claimed an
  experimental device while showing the generic "OnePlus earbuds" name.

- Add an app-like Play/Stop earbud search control with correct `0x8400`
  acknowledgement handling, shared uncertain/confirmed state, per-device
  50-second stop, close/shutdown cleanup, and device-bound queued commands.
- Reuse the authenticated session for ANC strengths as well as main modes;
  Nord Buds 3 Pro Low/Moderate/High/Auto selection was observed after
  0.15–0.30 seconds instead of roughly 15 seconds. Verify Auto against its
  selected-mode notification when the query reports adaptive intensity,
  rejecting stale query responses and newer contradictory mode notifications.
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

The original plugin is already listed in the Marketplace. The fork snapshot is
not a separate listing and is not covered by the original snapshot verification.
