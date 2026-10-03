#!/bin/sh
# Connect the Hermes gateway to the Connecture bus.
# Replaces D:\Freebuff\hermes-fix\start_aibus_8787.sh.
# The filename there can stay. The port it binds cannot: 8787 is Gmail OAuth.
# Default bus port is 8789. Default gateway is http://127.0.0.1:8642.

set -eu

port="${AIBUS_PORT:-8789}"
case "$port" in
  8787|8788|8642|8082|8650|8790)
    echo "refusing to bind the Connecture bus on port $port" >&2
    exit 2
    ;;
esac

if [ -z "${CONNECTURE_BUS_URL:-}" ] || [ -z "${CONNECTURE_BUS_TOKEN:-}" ]; then
  echo "CONNECTURE_BUS_URL and CONNECTURE_BUS_TOKEN are required" >&2
  exit 2
fi

export HERMES_GATEWAY_URL="${HERMES_GATEWAY_URL:-http://127.0.0.1:8642}"
exec python3 -m hermes --serve --port "$port"
