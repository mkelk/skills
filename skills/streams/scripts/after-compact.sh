#!/usr/bin/env bash
# SessionStart hook, matcher "compact" (the streams skill's `compact` door, references/compact.md).
# Runs in a stream's worktree right after its session was compacted. Whatever it prints is added to the
# compacted context, so a stream comes back knowing who it is and where its state lives, not only what the
# summary kept. Never fails the session: a missing table or coord prints less, not an error.
set -uo pipefail
here="$(pwd -P)"
scripts="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
common="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || exit 0
table="$common/coord/streams.md"
echo "You were just compacted. Before acting on anything, re-read what follows and the files it names."
echo
if [ -f "$table" ]; then
  # The table writes a worktree as `~/…` or as an absolute path. In bash, a `~` in a substitution's
  # replacement expands back to $HOME, so the tilde goes through a variable.
  tilde="~"; short="${here/#$HOME/$tilde}"
  row="$(grep -F "\`$short\`" "$table" | head -1)"
  [ -z "$row" ] && row="$(grep -F "\`$here\`" "$table" | head -1)"
  if [ -n "$row" ]; then
    echo "Your row in the live streams table ($table):"
    echo "$row"
    brief="$(printf '%s' "$row" | grep -o 'Brief `[^`]*`' | head -1 | sed 's/Brief `//; s/`$//')"
    [ -n "$brief" ] && echo && echo "Your brief: $brief (re-read it now)."
  fi
fi
if [ -f .devmeta/current-increment.md ]; then
  echo
  echo "Your Active line (.devmeta/current-increment.md):"
  sed -n '1,8p' .devmeta/current-increment.md
fi
if [ -f "$scripts/coord.py" ]; then
  echo
  echo "Open holds, what the seat owes, and the newest coord log lines (python3 $scripts/coord.py show):"
  python3 "$scripts/coord.py" show 2>/dev/null | sed 's/^/  /'
fi
echo
echo "Your state lives in files, not in this conversation: the coord log ($common/coord/log.md; read the"
echo "lines naming you since yesterday), your own pages and commits, tk. Read them before you continue. If"
echo "you were waiting for something (a table, a reply, a time), it is in the coord log or the seat will"
echo "resend it: ask the seat (SendMessage to seat) rather than guess. The standing rules in your brief still hold."
exit 0
