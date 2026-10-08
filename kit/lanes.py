"""Connecture connectors. Hermes is one lane. The others are not Hermes profiles."""

from __future__ import annotations

from hermes.profiles import DESK, PROFILES

# Seat -> lane. Grok Build and Grok Swarm are Grokbot seats.
# Muse the local gateway and muse.ai the Meta connector are different seats.
LANE_OF = {
    "hermes-bot": "hermes",
    "gemini-spark": "gemini",
    "grokbot": "grokbot",
    "grok-build": "grokbot",
    "grok-swarm": "grokbot",
    "grok": "grok",
    "freebuff": "freebuff",
    "muse": "muse",
    "muse-ai": "muse-ai",
}

KIT = ("hermes", "gemini", "grokbot", "grok", "freebuff", "muse", "muse-ai")

_GROK_CLOSED = "Grok usage is gone. The note stays in this chat until it is back."


def lane_for(seat: str) -> str | None:
    if seat in DESK:
        return None
    if seat in LANE_OF:
        return LANE_OF[seat]
    if seat in PROFILES:
        return "hermes"
    return None


def closed_reason(lane: str, grok_open: bool = False) -> str | None:
    if lane == "grok" and not grok_open:
        return _GROK_CLOSED
    return None
