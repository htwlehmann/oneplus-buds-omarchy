# Snapshot verification — 2026-11-01

Snapshot: `nord-buds-3-pro-2026-11-01`. The annotated tag identifies the final
prepared commit. Runtime source is `dd3a1032fc802b6aedba2a8045364252c0240966`,
with original upstream ancestry at `abe70f4b6e8f55cc8f6a4888c04ddead8a087e33`.
Only documentation, fork repository metadata and the preview changed during
publication preparation; the installed plugin was not edited or replaced.

## Recorded environment

| Component | Version |
|---|---|
| Omarchy | 4.0.6-1 |
| Quickshell | 0.3.2.r7.g2b4501a-1 |
| Qt declarative / QtTest | 6.12.0 |
| Python | 3.14.8-1 |
| dbus-python | 1.5.0-1 |
| BlueZ | 5.87-2 |
| Node | v26.12.1 |

These are observed versions, not a lockfile for an Arch installation. Future
OS packages may require adaptation. Device firmware 155.155.101 comes from the
owner's earlier measurements; it was not re-read during this packaging step.

## Checks

Baseline before documentation changes: **213 Python tests and 33 Qt tests passed**.
Final verification on the prepared checkout:

| Check | Result |
|---|---|
| Python suite (including Node-backed checks) | 213 passed, no skips |
| Qt offscreen suite | 33 passed, no skips |
| Runtime/source/LICENSE fingerprints | 80 unchanged files match source and clean export |
| Dependency preflight | All six checks passed in checkout and export |
| Omarchy validator | Checkout and clean export passed |
| Exported CLI `--help` | Exit 0, no hardware query |
| Relative links in revised public entry documents | Targets exist |
| `git diff --check` | Passed |
| User preview | Original 767×1200 PNG copied byte-for-byte, empty metadata |

Final tag/bundle verification is performed after the preparation commit. The
bundle restore check is also recorded in the private backup directory so the
final tag need not be moved just to include its own commit hash.

The Python bridge-error sanitization test intentionally logs an internal
AssertionError while asserting the external error remains sanitized. Offscreen
Qt fake-shell fixtures also emit known undefined-color/host warnings; test
failures and real native-shell errors must not be confused with these fixtures.
No Bluetooth write or sound playback was run for publication preparation.

[`snapshot-runtime.json`](snapshot-runtime.json) records SHA256 hashes for the
unchanged Python/QML/JS, launchers and LICENSE, compared with the source commit.
The preview is the owner's unmodified 2026-11-01 native screenshot, including
the Omarchy system bar and background margins as explicitly requested. It shows
the same runtime, with no app graphics, device addresses or unrelated application
windows. PNG metadata is empty.

## Publication/history audit

The original Git history is preserved. All reachable source-history blobs and
commit messages were checked for credential/private-key patterns, the author's
absolute home/private-vault paths, device-address patterns and shipped-artifact
extensions. Changed historical blobs contain only the obvious address examples
`AA:BB:CC:DD:EE:FF` and `11:22:33:44:55:66`, used in documentation/tests; inherited
history also uses synthetic fixture addresses, reviewed separately.
No APK/XAPK/DEX, decompiled Java, pairing key store or packet-capture artifact is
included. The private REA archive is not included; public protocol facts and
hardware observations remain in the device and measurement documentation.
All 649 reachable source-history blobs were scanned, including the 252 added
since upstream. The only distinct credential-pattern match is the deliberately synthetic
alphabet-sequence token in upstream's report-redaction test (`tests/test_report.py`),
not a real access token. No private-key header was found. All address-pattern matches are synthetic fixture/example
addresses. Historical author metadata (including `joerg@localhost`) is retained;
new preparation commits use the GitHub account's public noreply address.

This is a scoped pattern scan plus inspection of the shipped file list, not a
claim of a comprehensive security audit. Existing upstream history remains
attributed to its original authors. Marketplace verification belongs to the
original listed commit and does not transfer to this fork.

## Offline backup

The local preparation creates a Git bundle containing the final snapshot tag
and its complete ancestry, plus a SHA256 sidecar outside this repository. Verify
by cloning that bundle at the snapshot tag, running `git fsck`, validating the
checkout and a clean export, and invoking the exported CLI help/preflight.
The exact restoration commands are in [snapshot.md](snapshot.md).
