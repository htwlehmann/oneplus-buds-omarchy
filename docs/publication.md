# Fork publication preparation

Prepared locally on **2026-11-01**. No remote fork, push, GitHub release, pull
request or Marketplace submission is created by this preparation.

| Item | Prepared value |
|---|---|
| Original project | https://github.com/GazzasaurusRex/oneplus-buds-omarchy |
| Intended GitHub fork | https://github.com/htwlehmann/oneplus-buds-omarchy |
| Working branch | `prepare/publication` |
| Snapshot tag | `nord-buds-3-pro-2026-11-01` |
| Runtime source | `dd3a1032fc802b6aedba2a8045364252c0240966` |
| Upstream base | `abe70f4b6e8f55cc8f6a4888c04ddead8a087e33` |
| Plugin ID / package version | `oneplus-buds.control` / `0.1.0` (unchanged) |
| License | Original MIT notice, Copyright (c) 2026 Gaz and contributors |

The purpose is personal restoration and optional upstream contributions, not a
second independently maintained product. The tag names the tested source;
package version `0.1.0` alone does not distinguish it from upstream.
Fork metadata identifies its own repository, while runtime issue links remain
upstream to preserve behaviour. No new upstream release number is invented.

## What is ready for review

- Current model/function descriptions with owner evidence distinguished from
  upstream maintainer hardware tests; physical Pro/Pro 2 retesting is not claimed.
- [Pinned online/offline restoration](snapshot.md), with backups outside plugin
  discovery and no overwrite of an existing installation.
- [Verification and publication audit](snapshot-verification.md), the owner-provided
  preview including the system bar, original history, unchanged runtime and a local offline Git bundle.
- [Contribution scopes](upstream-contribution.md), including the open Buds 4
  write-permission policy that must be coordinated before proposing a Nord PR.

## Proposed external actions — not executed

Only after review, create the public GitHub fork without changing the local
remotes, then publish the prepared branch as its default `main` and the single
snapshot tag:

```bash
gh repo fork GazzasaurusRex/oneplus-buds-omarchy --clone=false --remote=false
git push origin prepare/publication:main
git push origin refs/tags/nord-buds-3-pro-2026-11-01
```

Before executing, confirm `gh api user --jq .login` is `htwlehmann`, that `origin`
is the intended fork and `upstream` is the original, and fetch/check the actual
fork main. A new fork should still have the recorded upstream ancestry. The
pushes are ordinary fast-forwards; if someone has changed the fork, inspect that
change rather than using force. Do not use `--all`, `--mirror` or `--tags`:
older development refs need not be published. Keep the dated snapshot tag fixed.

Opening a pull request is a later action, with focused branches based on current
upstream. Do not send the full development history as one unstructured change,
and restore upstream repository metadata in contribution branches.

## Existing Marketplace listing

The original `oneplus-buds.control` is already listed at
https://plugins.omarchy.org/plugin.html?id=oneplus-buds.control . Its recorded
snapshot on the preparation date is `abe70f4`, with maintainer-reviewed
verification. That record is not verification of this fork.
No second listing is planned; the existing ID remains with the original listing.

If upstream accepts the work, its maintainer can choose a release and request
**Verify and publish a newer upstream commit** with the exact 40-character SHA.
The marketplace keeps the existing snapshot until the update passes its
commit-bound validation/approval workflow. Git installs still follow mutable
repository HEAD rather than the old verified snapshot. Source references:
[verification policy](https://github.com/omacom/omarchy-plugin-marketplace/blob/main/VERIFICATION.md),
[submission guide](https://github.com/omacom/omarchy-plugin-marketplace/blob/main/SUBMISSION.md).
No Marketplace action is required merely to preserve/share the fork.
