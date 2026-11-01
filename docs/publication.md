# Fork publication

Prepared and published on **2026-11-01** as the public fork
https://github.com/htwlehmann/oneplus-buds-omarchy . The initial `main` and the
annotated snapshot tag both identify `2433c3fe57faf790f741ea1ae8a3b60e61a0670c`.
Later publication-status documentation on `main` does not move that fixed tag.
No GitHub release, pull request or Marketplace submission was created.

| Item | Prepared value |
|---|---|
| Original project | https://github.com/GazzasaurusRex/oneplus-buds-omarchy |
| Published GitHub fork | https://github.com/htwlehmann/oneplus-buds-omarchy |
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

## Published snapshot contents

- Current model/function descriptions with owner evidence distinguished from
  upstream maintainer hardware tests; physical Pro/Pro 2 retesting is not claimed.
- [Pinned online/offline restoration](snapshot.md), with backups outside plugin
  discovery and no overwrite of an existing installation.
- [Verification and publication audit](snapshot-verification.md), the owner-provided
  preview including the system bar, original history, unchanged runtime and a local offline Git bundle.
- [Contribution scopes](upstream-contribution.md), including the open Buds 4
  write-permission policy that must be coordinated before proposing a Nord PR.

## Publication commands

The public fork was created without changing local remotes, and the prepared
branch and single snapshot tag were published together. Equivalent commands for
a new fork are shown below; they are not instructions to republish or move the
existing snapshot tag:

```bash
gh repo fork GazzasaurusRex/oneplus-buds-omarchy --clone=false
git push --atomic origin prepare/publication:main refs/tags/nord-buds-3-pro-2026-11-01
```

The installed GitHub CLI rejects `--remote=false` when an explicit repository
argument is supplied; `--clone=false` is sufficient here. Git also needs an HTTPS
credential helper. The publication used the existing `gh auth git-credential`
helper for that command only, without changing global Git configuration.

Before executing any future push, confirm `gh api user --jq .login` is `htwlehmann`, that `origin`
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
