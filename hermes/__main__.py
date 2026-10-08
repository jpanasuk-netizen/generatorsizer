"""Hermes bridge CLI.

Check a config: python -m hermes check path/to/config.yaml
Health:         python -m hermes ping
Live loop:      HERMES_GATEWAY_URL, CONNECTURE_BUS_URL, CONNECTURE_BUS_TOKEN
                python -m hermes --serve
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from leo.bus import HttpBus

from hermes.bridge import process_new
from hermes.configcheck import diagnose, parse_config, repaired_primary
from hermes.gateway import GatewayError, HttpGateway
from hermes.ports import BUS_PORT, GATEWAY_PORT, bus_port


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hermes")
    parser.add_argument("command", nargs="?", choices=("check", "ping"))
    parser.add_argument("path", nargs="?")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=None, help="bus port guard; default 8789")
    args = parser.parse_args(argv)
    try:
        port = bus_port(args.port)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.serve:
        return _serve(port)
    if args.command == "check":
        return _check(args.path)
    if args.command == "ping":
        return _ping()
    parser.print_help()
    return 2


def _check(path: str | None) -> int:
    if not path:
        print("check needs a config path", file=sys.stderr)
        return 2
    with open(path, encoding="utf-8") as handle:
        document = parse_config(handle.read())
    problems = diagnose(document)
    json.dump({"problems": problems, "repaired": repaired_primary(document), "bus_port": BUS_PORT}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 1 if problems else 0


def _ping() -> int:
    base = os.environ.get("HERMES_GATEWAY_URL", f"http://127.0.0.1:{GATEWAY_PORT}").strip()
    key = os.environ.get("HERMES_API_KEY", "").strip()
    try:
        body = HttpGateway(base, key).health()
    except (GatewayError, OSError, ValueError):
        print("Hermes gateway did not answer.", file=sys.stderr)
        return 1
    print(json.dumps({"status": body.get("status"), "platform": body.get("platform")}))
    return 0 if body.get("status") == "ok" else 1


def _serve(_port: int) -> int:
    base = os.environ.get("CONNECTURE_BUS_URL", "").strip()
    token = os.environ.get("CONNECTURE_BUS_TOKEN", "").strip()
    gateway_url = os.environ.get("HERMES_GATEWAY_URL", f"http://127.0.0.1:{GATEWAY_PORT}").strip()
    if not base or not token:
        print("CONNECTURE_BUS_URL and CONNECTURE_BUS_TOKEN are required", file=sys.stderr)
        return 2
    bus = HttpBus(base, token)
    gateway = HttpGateway(gateway_url, os.environ.get("HERMES_API_KEY", "").strip())
    state: dict = {"since": 0}
    while True:
        process_new(bus, gateway, state)
        time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
