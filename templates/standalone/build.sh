#!/bin/sh
set -eu
MOD_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "${PYTHON:-python3}" "$MOD_DIR/scripts/build.py" "$@"
