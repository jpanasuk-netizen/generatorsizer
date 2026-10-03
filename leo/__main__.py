"""Desk CLI.

One shot: python -m leo "send gemini a message, say hi"
Live loop: CONNECTURE_BUS_URL and CONNECTURE_BUS_TOKEN must be set, then python -m leo --serve
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from leo.bus import HttpBus
from leo.desk import handle
from leo.service import process_new
from leo.session import Session


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="leo")
    parser.add_argument("text", nargs="*", help="one desk message to answer locally")
    parser.add_argument("--serve", action="store_true", help="poll the bus and answer Leo")
    args = parser.parse_args(argv)
    if args.serve:
        return _serve()
    text = " ".join(args.text).strip()
    if not text:
        parser.print_help()
        return 2
    result = handle(Session(), text)
    json.dump(
        {
            "reply": result.reply,
            "gate": result.gate,
            "actions": [{"to": action.to, "text": action.text} for action in result.actions],
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def _serve() -> int:
    base = os.environ.get("CONNECTURE_BUS_URL", "").strip()
    token = os.environ.get("CONNECTURE_BUS_TOKEN", "").strip()
    if not base or not token:
        print("CONNECTURE_BUS_URL and CONNECTURE_BUS_TOKEN are required", file=sys.stderr)
        return 2
    bus = HttpBus(base, token)
    state: dict = {"since": 0, "sessions": {}}
    while True:
        process_new(bus, state)
        time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
