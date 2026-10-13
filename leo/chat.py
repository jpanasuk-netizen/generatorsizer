"""Per-seat chat. A seat sees a message it sent, a message sent to it, or a broadcast."""

from __future__ import annotations

from leo.bus import Bus
from hermes.profiles import CREW, seat_of


def party(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        return ""
    return seat_of(cleaned) or cleaned


def read_all(bus: Bus, page: int = 50) -> list[dict]:
    since = 0
    rows: list[dict] = []
    while True:
        batch = bus.read(since=since, limit=page)
        if not batch:
            break
        rows.extend(batch)
        since = max(int(message["id"]) for message in batch)
        if len(batch) < page:
            break
    rows.sort(key=lambda message: int(message["id"]))
    return rows


def chat(messages: list[dict], seat: str) -> list[dict]:
    me = party(seat)
    visible: list[dict] = []
    for message in messages:
        target = str(message.get("to") or "")
        people = {party(str(message.get("from") or "")), party(target)}
        broadcast = target.strip() in {"*", "all"}
        crew = target.strip().lower() == "crew" and me in CREW
        if me in people or broadcast or crew:
            visible.append(message)
    return visible


def seat_chat(bus: Bus, seat: str) -> list[dict]:
    return chat(read_all(bus), seat)


def texts(bus: Bus, seat: str) -> list[str]:
    return [str(message.get("text") or "") for message in seat_chat(bus, seat)]
