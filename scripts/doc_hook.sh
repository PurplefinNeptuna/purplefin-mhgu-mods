#!/bin/sh
# "Writing project docs" in AGENTS.md for the docs a commit stages, one path per line on stdin.
# Shared by the workspace hook and each mod repo's hook. shortcut: reads the working tree, not the
# index; use the index if partial staging ever matters.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
docs=$(grep -v -e /vendor/ -e '^vendor/' || true)
[ -n "$docs" ] || exit 0
if echo "$docs" | grep -E '^(mods/[^/]+/)?DEVELOPMENT\.md$|^docs/[^/]+\.md$' | xargs -r grep -nE '^#+ .*\br[0-9]{1,3}\b'; then
    echo 'Doc rule: state the fact in its section, not under a per-run heading.' >&2
    exit 1
fi
over=$(echo "$docs" | xargs wc -l | awk '$2 != "total" && $1 >= ($2 ~ /(^|\/)DEVELOPMENT\.md$/ ? 500 : 350)')
if [ -n "$over" ]; then
    echo "$over" >&2
    echo 'Doc rule: under 500 lines for DEVELOPMENT.md, 350 for other docs. Merge facts and drop narrative.' >&2
    exit 1
fi
echo "$docs" | xargs python3 "$root/scripts/doc_rules.py"
