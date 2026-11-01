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
the same ID and must not be used as a backup.

```bash
bash <<'SH'
set -eu
snapshot_plugin_dir="$HOME/.config/omarchy/plugins/oneplus-buds.control"
snapshot_backup_root="$HOME/.local/state/oneplus-buds/plugin-backups"
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
