"""Fleet handler words. Source of truth shape: BRAIN/FLEET.md routing table."""

from __future__ import annotations

import re

# Longest alias first so "gemini spark" wins over "gemini".
ALIASES: tuple[tuple[str, str], ...] = (
    ("gemini spark", "gemini-spark"),
    ("gemini", "gemini-spark"),
    ("spark", "gemini-spark"),
    ("seo bot", "seo-bot"),
    ("grok build", "grok-build"),
    ("grok swarm", "grok-swarm"),
    ("proposal closer", "proposalcloser"),
    ("proposalcloser", "proposalcloser"),
    ("hermes bot", "hermes-bot"),
    ("free models", "freemodelsbot"),
    ("freebot", "freemodelsbot"),
    ("money bot", "moneybot"),
    ("moneybot", "moneybot"),
    ("thetubebot", "thetubebot"),
    ("tubebot", "thetubebot"),
    ("tube", "thetubebot"),
    ("bizdev", "bizdevideabot"),
    ("cynthia", "cynthia"),
    ("taproot", "taproot"),
    ("headshot", "headshot"),
    ("horobot", "horobot"),
    ("gaddesk", "gaddesk"),
    ("hermes", "hermes-bot"),
    ("swarm", "grok-swarm"),
    ("annie", "annie"),
    ("muse", "muse"),
    ("mimo", "mimo"),
    ("btcc", "btcc"),
    ("seo", "seo-bot"),
    ("eve", "eve"),
    ("jeremy", "jeremy"),
    ("leo-bot", "leo"),
    ("leo", "leo"),
)

DISPLAY = {
    "gemini-spark": "Gemini Spark",
    "seo-bot": "SEO Bot",
    "grok-build": "Grok Build",
    "grok-swarm": "Grok Swarm",
    "proposalcloser": "ProposalCloser",
    "hermes-bot": "Hermes Bot",
    "freemodelsbot": "FreeModelsBot",
    "moneybot": "MoneyBot",
    "thetubebot": "thetubebot",
    "bizdevideabot": "BizDevIdeaBot",
    "cynthia": "Cynthia",
    "taproot": "TapRoot",
    "headshot": "Headshot",
    "horobot": "Horobot",
    "gaddesk": "GadDesk",
    "annie": "Annie",
    "muse": "Muse",
    "mimo": "MiMo",
    "btcc": "BTCC",
    "eve": "Eve",
    "jeremy": "Jeremy",
    "leo": "Leo",
}

SELF_SEATS = frozenset({"leo"})
LEO_NAMES = frozenset({"leo", "leo-bot"})
BOTS = tuple(seat for seat in DISPLAY if seat not in {"leo", "jeremy"})


def address(seat: str) -> str:
    """A handler phrase the desk router maps back to this seat."""
    phrases = [alias for alias, mapped in ALIASES if mapped == seat]
    phrases.sort(key=len, reverse=True)
    for phrase in phrases:
        found, start, end = find_seat(phrase)
        if found == seat and start == 0 and end == len(phrase):
            return phrase
    raise KeyError(seat)


def display(seat: str) -> str:
    return DISPLAY.get(seat, seat)


def find_seat(text: str) -> tuple[str | None, int, int]:
    """Return (seat, start, end) for the earliest alias match in text."""
    low = text.lower()
    found: tuple[str, int, int] | None = None
    for alias, seat in ALIASES:
        match = re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", low)
        if not match:
            continue
        span = (seat, match.start(), match.end())
        if found is None or span[1] < found[1] or (span[1] == found[1] and span[2] > found[2]):
            found = span
    if found is None:
        return None, -1, -1
    return found


def seat_of_sender(name: str) -> str | None:
    key = name.strip().lower()
    if key in DISPLAY:
        return key
    seat, start, _end = find_seat(name.strip())
    if start != 0:
        return None
    return seat
