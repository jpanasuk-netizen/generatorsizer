"""Which fleet seats the Windows Hermes gateway can actually run."""

from __future__ import annotations

from leo.fleet import find_seat

# Profile directory names on the multiplexed gateway. seo-bot's directory is seobot.
PROFILES = {
    "annie": "annie",
    "bizdevideabot": "bizdevideabot",
    "btcc": "btcc",
    "cynthia": "cynthia",
    "eve": "eve",
    "freemodelsbot": "freemodelsbot",
    "gaddesk": "gaddesk",
    "grok-build": "grok-build",
    "headshot": "headshot",
    "hermes-bot": "hermes-bot",
    "horobot": "horobot",
    "leo": "leo",
    "moneybot": "moneybot",
    "muse": "muse",
    "proposalcloser": "proposalcloser",
    "seo-bot": "seobot",
    "taproot": "taproot",
    "thetubebot": "thetubebot",
}

# Same gateway, model id rather than a profile directory.
GATEWAY_MODELS = {
    "gemini-spark": "gemini-spark",
}

# Documented crew broadcast: muse, mimo, gemini-spark, hermes-bot.
CREW = ("muse", "mimo", "gemini-spark", "hermes-bot")

# Desk routing owns these names. The gateway must not also answer them.
DESK = frozenset({"leo", "leo-bot"})

FILE_BUS_ONLY = frozenset({"mimo"})

# The gateway directory is seobot. The fleet seat is seo-bot.
_DIRECTORY_NAMES = {"seobot": "seo-bot"}


def seat_of(name: str) -> str | None:
    key = name.strip().lower()
    if key in _DIRECTORY_NAMES:
        return _DIRECTORY_NAMES[key]
    seat, start, _end = find_seat(name.strip())
    if start != 0:
        return None
    return seat


def gateway_model(seat: str) -> str | None:
    if seat in DESK:
        return None
    if seat in PROFILES:
        return PROFILES[seat]
    if seat in GATEWAY_MODELS:
        return GATEWAY_MODELS[seat]
    return None


def targets_for(name: str) -> list[str] | None:
    """Seats this address should reach. None means this bridge does not own it."""
    cleaned = name.strip().lower()
    if cleaned in DESK:
        return None
    if cleaned == "crew":
        return list(CREW)
    seat = seat_of(name)
    if seat is None or seat in DESK:
        return None
    if gateway_model(seat) is not None or seat in FILE_BUS_ONLY:
        return [seat]
    return None
