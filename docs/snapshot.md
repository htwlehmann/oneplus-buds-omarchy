# Restore the Nord Buds 3 Pro snapshot

Snapshot tag: **`nord-buds-3-pro-2026-11-01`**.
This is a fixed personal source snapshot, not a promise of compatibility with
future Omarchy/BlueZ releases or an archive of the operating system packages.
The tested environment is recorded in [snapshot verification](snapshot-verification.md).
Device settings are stored in the earbuds and are not part of the Git backup.

The GitHub fork/tag must first be published; the offline route below works with
the locally prepared bundle before publication. Neither route needs the private
reverse-engineering workspace, an APK or Python packages from PyPI.

## Get the exact source

After publication, choose a destination that does not exist:

```bash
git clone --branch nord-buds-3-pro-2026-11-01 --single-branch \
  https://github.com/htwlehmann/oneplus-buds-omarchy.git \
  "$HOME/oneplus-buds-snapshot-restore"
cd "$HOME/oneplus-buds-snapshot-restore"
git describe --tags --exact-match
git status --short
```

The first check must print the snapshot tag and the status must be empty. A
checkout of the tag is intentionally detached: do not run pull/rebase to update
it. Record `git rev-parse HEAD` to compare it with the prepared commit.

For an offline restore, copy the bundle and its `.sha256` sidecar together.
In the directory containing them, verify and clone to an absent destination:

```bash
sha256sum -c oneplus-buds-nord-buds-3-pro-2026-11-01.bundle.sha256
git bundle list-heads oneplus-buds-nord-buds-3-pro-2026-11-01.bundle
git clone --branch nord-buds-3-pro-2026-11-01 \
  oneplus-buds-nord-buds-3-pro-2026-11-01.bundle \
  "$HOME/oneplus-buds-snapshot-restore"
cd "$HOME/oneplus-buds-snapshot-restore"
git bundle verify /absolute/path/to/oneplus-buds-nord-buds-3-pro-2026-11-01.bundle
git describe --tags --exact-match
git status --short
```

Replace `/absolute/path/to` with the bundle directory. The bundle contains the
snapshot tag and its complete Git ancestry, not local caches or device state.
The checksum detects changes relative to the sidecar; keep both in your backup.

## Check before installation

From the restored source checkout:

```bash
python3 scripts/check_dependencies.py
omarchy plugin validate .
./oneplus-buds --help
systemctl is-active bluetooth
```

The preflight does not establish shell API compatibility: this snapshot uses
Omarchy 4.0.6-era UI components. Check the recorded versions if loading fails.
Do not start a second Quickshell session or a competing Bluetooth control client.

## Install without overwriting a running copy

All commands below are for an existing Omarchy graphical session. Run this Bash
block **from the restored source checkout**, after the checks above pass. It
backs up an existing plugin outside the discovery directory and exports only
source/runtime files. A second copy under `~/.config/omarchy/plugins/` would have
the same ID and must not be used as a backup. Before running the block, note
its current bar section for rollback. The example enables the snapshot on the
right; change `--section right` if you want another section.

The block checks raw manifests (including symlinked plugin directories) before
any disable/move/export, because a catalog may already hide duplicate IDs. A
same-ID copy under another name, an unreadable manifest or a symlink at the
canonical destination requires manual inspection; it is not moved automatically.

```bash
bash <<'SH'
set -eu
snapshot_plugin_dir="$HOME/.config/omarchy/plugins/oneplus-buds.control"
snapshot_backup_root="$HOME/.local/state/oneplus-buds/plugin-backups"
python3 - "$snapshot_plugin_dir" <<'PYGUARD'
import json
from pathlib import Path
import sys

target = Path(sys.argv[1])
if target.is_symlink() or (target.exists() and not target.is_dir()):
    raise SystemExit("Inspect the destination first: it is a symlink or not a directory.")
children = target.parent.iterdir() if target.parent.exists() else []
for child in children:
    manifest = child / "manifest.json"
    if not manifest.is_file():
        if child == target:
            raise SystemExit("Existing destination has no manifest; inspect it before replacing it.")
        continue
    try:
        plugin_id = json.loads(manifest.read_text(encoding="utf-8-sig"))["id"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Cannot inspect {manifest}; fix this before installing.") from error
    if child == target and plugin_id != "oneplus-buds.control":
        raise SystemExit("Existing destination belongs to another plugin; inspect it first.")
    if child != target and plugin_id == "oneplus-buds.control":
        raise SystemExit(f"Existing same-ID plugin at {child}; resolve it before installing.")
PYGUARD
if [ -e "$snapshot_plugin_dir" ]; then
  omarchy plugin disable oneplus-buds.control
  mkdir -p "$snapshot_backup_root"
  snapshot_backup="$snapshot_backup_root/before-$(date +%Y%m%d-%H%M%S)"
  test ! -e "$snapshot_backup"
  mv -- "$snapshot_plugin_dir" "$snapshot_backup"
  printf 'Previous installation: %s\n' "$snapshot_backup"
fi
python3 scripts/export_plugin.py "$snapshot_plugin_dir"
omarchy plugin validate "$snapshot_plugin_dir"
omarchy-shell shell rescanPlugins
omarchy plugin enable oneplus-buds.control --section right
SH
```

Do not continue after an error. If activation fails, retain the failed export
for diagnosis and restore the previous copy as described below. A source export
has no `.git`, so ordinary Git plugin updates cannot silently advance this pinned
snapshot. To adopt a newer version, repeat the explicit backup/restore process.
No dependency installation or Bluetooth settings are changed by the exporter.

## Roll back

Disable `oneplus-buds.control`. Move the newly exported plugin out of the plugins
directory into a **new** directory under the backup root. Move the saved previous
installation back to `~/.config/omarchy/plugins/oneplus-buds.control`, rescan
plugins, then enable it in its previous bar section. Never merge two plugin
directories or use `git reset --hard` on the running copy as a rollback method.
If this was a new installation, removal through `omarchy plugin remove` is enough.
The plugin does not restore an earlier ANC/EQ setting automatically on removal.
