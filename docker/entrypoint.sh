#!/usr/bin/env sh
set -eu

mkdir -p "${BIOSTACK_WORKSPACE:-/workspace}"

exec "$@"
