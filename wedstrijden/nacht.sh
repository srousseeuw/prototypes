#!/usr/bin/env bash
# Wrapper voor cron: draait de nachtelijke ronde en houdt een logje bij.
# Zet in crontab (elke nacht om 3u15):
#   15 3 * * * /Users/seb/Documents/GitHub/prototypes/wedstrijden/nacht.sh
set -uo pipefail
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$HIER/data"
LOG="$HIER/data/nacht.log"
{
  echo "===== $(date '+%Y-%m-%d %H:%M') ====="
  /usr/bin/env python3 "$HIER/wedstrijden.py" nacht
  echo "einde status=$?"
} >> "$LOG" 2>&1
# Log inkorten tot de laatste 2000 regels.
tail -n 2000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
