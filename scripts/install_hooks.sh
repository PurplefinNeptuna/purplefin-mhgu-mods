#!/bin/sh
# Turn on the custom pre-commit hooks: the workspace's, and each checked-out mod submodule's.
# Run after cloning and after `git submodule update --init`.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
git -C "$root" config core.hooksPath .githooks
git -C "$root" submodule foreach --quiet \
    'case "$sm_path" in mods/*) git config core.hooksPath "$toplevel/.githooks/mod"; echo "hooks: $sm_path";; esac'
