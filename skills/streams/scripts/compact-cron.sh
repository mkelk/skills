#!/usr/bin/env bash
# Run the idle tidy from the system cron (the streams skill's `compact` door, references/compact.md).
# Twice a day, at the human's quiet times, e.g.:
#   7 10,21 * * * /path/to/skills/streams/scripts/compact-cron.sh /path/to/main/checkout
# The repository is the first argument, or $STREAMS_REPO. Each run is appended to
# <git common dir>/coord/compact.log. Thresholds pass through: COMPACT_MIN_TOKENS, COMPACT_QUIET_MINUTES.
set -uo pipefail
repo="${1:-${STREAMS_REPO:-}}"
if [ -z "$repo" ]; then
  echo "usage: compact-cron.sh <main checkout>   (or set STREAMS_REPO)" >&2
  exit 2
fi
# cron starts with a bare PATH: add the usual user bin directories (herdr, git, python3), and any
# extra the crontab line passes as STREAMS_CRON_PATH.
export PATH="${STREAMS_CRON_PATH:+$STREAMS_CRON_PATH:}$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
scripts="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$repo" || exit 1
common="$(git rev-parse --path-format=absolute --git-common-dir)" || exit 1
mkdir -p "$common/coord"
log="$common/coord/compact.log"
{ echo "== $(date -u +%FT%TZ)"; python3 "$scripts/compact-idle.py" --apply 2>&1; } >> "$log"
