# Local fork notes

This checkout is a fork of
<https://github.com/GazzasaurusRex/oneplus-buds-omarchy.git> with one local
addition: an owner-verified device profile for the **OnePlus Nord Buds 3 Pro**
(product `064414`).

> **Handoff for a fresh session:** read
> `~/src/oneplus-buds-research/HANDOFF.md` first. It carries the verified
> protocol cheat sheet, the device state, the open tasks and the pitfalls of
> this environment (QML cache, `keepLoaded`, exclusive RFCOMM channel). The
> research artifacts live next to it: the decrypted device table of the phone
> app (`whitelist.json`) and the decompiled app itself (`decompiled-app/`).


- Local commit: `8706d2e` on `main`, also tagged `nord-buds-3-pro-2026-10-27`
  and kept on the branch `local/nord-buds-3-pro`.
- `origin` still points at the upstream repository, so the plugin stays a
  git-managed Omarchy plugin.

## Updating from upstream

`omarchy plugin update` fetches `origin` and then fast-forwards. Because this
checkout has a local commit on top of upstream, the fast-forward refuses and
leaves the working tree untouched:

    omarchy-plugin-update: cannot fast-forward 'oneplus-buds.control';
    you have local changes in $dir

That is the intended, safe behaviour. To take upstream changes anyway:

    cd ~/.config/omarchy/plugins/oneplus-buds.control
    git fetch origin
    git rebase origin/main
    PYTHONPATH=src python3 -m unittest discover -s tests
    omarchy-plugin-validate .
    omarchy-shell shell rescanPlugins

If the rebase conflicts in `src/oneplus_buds/profiles.py`, keep the `064414`
entry and re-apply the upstream changes around it.

## What the local commit changes

| File | Change |
|---|---|
| `src/oneplus_buds/profiles.py` | New `064414` device profile |
| `tests/test_nord_buds_3_pro.py` | Regression tests pinning the measured wire values |
| `tests/test_bridge.py` | Verification invariant extended to the third verified model |
| `docs/devices/oneplus-nord-buds-3-pro.md` | Device record with the measurements |
| `docs/devices/compatibility.md` | Compatibility table and feature scope |
| `README.md`, `CHANGELOG.md` | Model listed with its evidence and firmware |

The measured values were taken on the owner's unit with firmware `155.155.101`.
They are hardware observations, not guesses: every ANC mode was written with
the authenticated `0x0404` flow, acknowledged with status `00` and confirmed by
an independent fresh-session query.

## Reverting to the unmodified upstream plugin

    cd ~/.config/omarchy/plugins/oneplus-buds.control
    git reset --hard origin/main
    omarchy-shell shell rescanPlugins

The device then falls back to the Experimental state and offers no ANC or EQ
write controls, because no upstream profile exists for `064414`.
