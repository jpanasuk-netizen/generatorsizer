"""Hermes is one lane. Routing for the rest of the kit lives in kit.dispatch."""

from __future__ import annotations

from leo.bus import Bus

from hermes.gateway import Gateway
from kit.dispatch import process_new as dispatch


def process_new(
    bus: Bus,
    gateway: Gateway,
    state: dict,
    config: dict | None = None,
    lanes: dict | None = None,
    grok_open: bool = False,
) -> list[str]:
    return dispatch(bus, gateway, state, config=config, lanes=lanes, grok_open=grok_open)
