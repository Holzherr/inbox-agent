#!/bin/bash
# Installs the hourly sweep and the 07:45 digest as macOS LaunchAgents.
# Re-run after moving the folder. Remove with: ./scheduler/install.sh --remove
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS="$HOME/Library/LaunchAgents"
mkdir -p "$AGENTS"

for name in sweep digest; do
  dest="$AGENTS/inbox-agent.$name.plist"
  launchctl bootout "gui/$(id -u)" "$dest" 2>/dev/null || true
  if [ "${1:-}" = "--remove" ]; then rm -f "$dest"; echo "removed inbox-agent.$name"; continue; fi
  sed "s|__REPO__|$REPO|g" "$REPO/scheduler/inbox-agent.$name.plist" > "$dest"
  launchctl bootstrap "gui/$(id -u)" "$dest"
  echo "installed inbox-agent.$name"
done
