# Personal Nord snapshot

Original project: https://github.com/GazzasaurusRex/oneplus-buds-omarchy
Intended contribution fork: https://github.com/htwlehmann/oneplus-buds-omarchy
Snapshot tag: `nord-buds-3-pro-2026-11-01`.

The fork preserves the tested Nord Buds 3 Pro work for personal use and community
contributions. No ongoing maintenance is promised. Upstream ancestry and the
original MIT notice are retained; package version `0.1.0` is not a unique snapshot
identifier. Use the dated tag instead.

- [Install/restore the pinned snapshot, including an existing installation](docs/snapshot.md).
- [Environment, verification and publication audit](docs/snapshot-verification.md).
- [Publication state and exact proposed first-push refs](docs/publication.md).
- [Reviewable upstream contribution scopes](docs/upstream-contribution.md).
- [Nord protocol and measured limitations](docs/devices/oneplus-nord-buds-3-pro.md).

No external research directory is needed to install or test this source tree.
APKs and decompiled app sources are not included. Historical agent plans remain
as development records, not instructions to run their hardware writes.

## Updates

The pinned export is deliberately not Git-managed inside the plugin directory,
so ordinary `omarchy plugin update` does not advance it to mutable fork HEAD.
A newer snapshot requires an explicit backup and replacement. Never rebase or
hard-reset the running installation to "update" this personal snapshot.
For contribution work use a separate checkout, fetch `upstream`, and create
focused branches from the maintainer's current main. Do not force-push shared
history or carry fork repository metadata into an upstream PR unchanged.
