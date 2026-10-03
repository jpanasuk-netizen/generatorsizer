"""Apply desk turns to a bus. Posts as Leo-Bot unless LEO_FROM overrides it."""

from __future__ import annotations

import os

from leo.bus import Bus
from leo.desk import handle
from leo.fleet import LEO_NAMES, display, seat_of_sender
from leo.session import Session


def identity() -> str:
    return os.environ.get("LEO_FROM", "Leo-Bot")


def process_new(bus: Bus, state: dict) -> list[str]:
    """Read messages newer than state['since'] and answer the ones for Leo.

    state keys: since (int), sessions (dict[str, Session]).
    Returns the reply texts that were posted.
    """
    since = int(state.get("since") or 0)
    sessions: dict[str, Session] = state.setdefault("sessions", {})
    posted: list[str] = []
    me = identity()

    for message in bus.read(since=since, limit=50):
        state["since"] = max(int(state["since"]), int(message["id"]))
        sender = str(message.get("from") or "")
        target = str(message.get("to") or "")
        if sender.lower() == me.lower() or sender.lower() in LEO_NAMES:
            continue

        seat = seat_of_sender(sender)
        owner = _owner_waiting_on(sessions, seat) if seat else None
        if owner is None and seat is not None and target in sessions and sessions[target].open_to(seat):
            owner = target
        if owner is not None and seat is not None and owner != sender:
            session = sessions[owner]
            noted = session.note_reply(seat, str(message.get("text") or ""))
            if noted is not None:
                reply = f"{display(seat)} replied: {noted.reply}"
                sent = bus.send(from_=me, to=owner, text=reply, topic=str(message.get("topic") or "talk"))
                state["since"] = max(int(state["since"]), int(sent["id"]))
                posted.append(reply)
                continue

        if target.lower() not in LEO_NAMES:
            continue

        session = sessions.setdefault(sender, Session())
        result = handle(session, str(message.get("text") or ""))
        topic = str(message.get("topic") or "talk")
        for action in result.actions:
            sent = bus.send(
                from_=me,
                to=action.to,
                text=action.text,
                topic="talk",
                payload={"dispatch": action.dispatch_id, "for": sender},
            )
            state["since"] = max(int(state["since"]), int(sent["id"]))
        sent = bus.send(from_=me, to=sender, text=result.reply, topic=topic)
        state["since"] = max(int(state["since"]), int(sent["id"]))
        posted.append(result.reply)
    return posted


def _owner_waiting_on(sessions: dict[str, Session], seat: str | None) -> str | None:
    if not seat:
        return None
    for owner, session in sessions.items():
        if session.open_to(seat) is not None:
            return owner
    return None
