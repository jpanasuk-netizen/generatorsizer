"""Run the desk and the Hermes bridge until neither has anything new to post."""

from __future__ import annotations

from leo.bus import Bus
from leo.service import process_new as leo_turn
from hermes.bridge import process_new as hermes_turn
from hermes.gateway import Gateway


def run_until_idle(bus: Bus, gateway: Gateway, config: dict | None = None, max_passes: int = 30) -> dict:
    leo_state: dict = {"since": 0, "sessions": {}}
    hermes_state: dict = {"since": 0}
    for _ in range(max_passes):
        desk = leo_turn(bus, leo_state)
        seats = hermes_turn(bus, gateway, hermes_state, config=config)
        if not desk and not seats:
            return leo_state
    raise RuntimeError("bus did not settle")
