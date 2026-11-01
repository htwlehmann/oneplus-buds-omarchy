# Publication snapshot implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this approved preparation inline.

**Goal:** Prepare a documented, locally tested, reconstructable community snapshot without publishing it.
**Architecture:** Independent Git checkout, unchanged runtime, documentation/metadata updates, tagged snapshot and offline bundle.
**Tech stack:** Git, Python, Qt/QML, Omarchy validator.
**Spec:** ../specs/2026-11-01-publication-snapshot-design.md

## Global constraints

- No push, GitHub fork creation, PR creation or Marketplace submission.
- Installed plugin remains byte-for-byte unchanged; no Bluetooth writes.
- Keep `oneplus-buds.control`, package version `0.1.0` and MIT attribution.
- A dated snapshot tag identifies the fork; no invented official release.
- Public instructions must work without the author's private research directory.

## Review focus

- Snapshot restore must not overwrite an existing installation or expose a duplicate plugin ID in the discovery directory.
- A future fork URL must be marked as unpublished until it exists.
- Nord hardware evidence must not be represented as maintainer tests or as new tests on Pro/Pro 2.
- Local research assets, device identities and credentials must not enter the public snapshot or bundle.
- The tag, exported runtime, offline bundle and documented source revision must agree.

## Tasks

- [x] 1. Capture source/upstream commits, independent checkout and clean baseline; inspect current files and all added history blobs for sensitive material.
- [x] 2. Correct README, CHANGELOG, compatibility, fork/publication docs and repository metadata. Add pinned restore instructions, factual research provenance and local contribution scopes. Keep runtime unchanged.
- [x] 3. Use the owner-provided native preview unmodified, including the system bar as explicitly requested. Run full Python/Qt suites, dependency check, validator, clean export and CLI checks; record exact environment and audit scope.
- [ ] 4. Obtain one fresh final review, address material findings, commit and annotate the snapshot tag. Verify an offline bundle by cloning and validating it; confirm installed source is unchanged. Leave all publication actions pending.

Documentation changes do not require new implementation-mirroring tests; existing
behaviour/packaging tests and explicit restoration checks are the acceptance gates.
