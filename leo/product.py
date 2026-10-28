"""Run the desk and the Hermes bridge until neither has anything new to post."""

from __future__ import annotations

from leo.bus import Bus
from leo.service import process_new as leo_turn
from hermes.gateway import Gateway
from kit.dispatch import process_new as kit_turn


def run_until_idle(
    bus: Bus,
    gateway: Gateway,
    config: dict | None = None,
    lanes: dict | None = None,
    grok_open: bool = False,
    max_passes: int = 30,
) -> dict:
    leo_state: dict = {"since": 0, "sessions": {}}
    kit_state: dict = {"since": 0}
    for _ in range(max_passes):
        desk = leo_turn(bus, leo_state)
        seats = kit_turn(bus, gateway, kit_state, config=config, lanes=lanes, grok_open=grok_open)
        if not desk and not seats:
            return leo_state
    raise RuntimeError("bus did not settle")
