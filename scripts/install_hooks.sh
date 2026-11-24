#!/bin/sh
# Turn on the custom pre-commit hooks: the workspace's, and each checked-out mod submodule's.
# Each mod repo also commits under the workspace's local user.email, because a cloned repo starts
# without one and would fall back to the global address. A private mod is `update = none` in
# .gitmodules so a clone without access skips it; a mod checked out here is set back to checkout.
# Run after cloning and after `git submodule update --init`.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
git -C "$root" config core.hooksPath .githooks
WORKSPACE_EMAIL=$(git -C "$root" config --local --get user.email || true)
export WORKSPACE_EMAIL
git -C "$root" submodule foreach --quiet \
    'case "$sm_path" in mods/*)
        git config core.hooksPath "$toplevel/.githooks/mod"
        git -C "$toplevel" config "submodule.$name.update" checkout
        if [ -n "$WORKSPACE_EMAIL" ]; then git config user.email "$WORKSPACE_EMAIL"; fi
        echo "hooks: $sm_path";; esac'
