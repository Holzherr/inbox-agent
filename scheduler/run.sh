#!/bin/bash
# Runs /email-triage headless.
#   run.sh          -> hourly sweep
#   run.sh digest   -> sweep + daily digest sent to Slack

set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$REPO/logs/run.log"
LOCK="$REPO/logs/.lock"
mkdir -p "$REPO/logs"
cd "$REPO"

export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# One run at a time, so the digest never overlaps an hourly sweep.
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "=== $(date -u +%FT%TZ) · skipped, previous run still going ===" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK"' EXIT

ARGS=""
[ "${1:-}" = "digest" ] && ARGS=" --digest --slack"

echo "=== $(date -u +%FT%TZ) · email-triage${ARGS} ===" >> "$LOG"
claude -p "/email-triage${ARGS}" >> "$LOG" 2>&1 || echo "[ERROR] exited $?" >> "$LOG"
