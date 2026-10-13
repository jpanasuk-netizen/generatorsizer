"""One turn of the desk. Never invents another seat's words."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from leo.fleet import ALIASES, SELF_SEATS, display, find_seat
from leo.gates import external_gate
from leo.session import Session

_STATUS = re.compile(
    r"\b(?:did|do|have|has|any)\b.{0,48}\b(?:respond|reply|replied|answer|answered)\b"
    r"|\b(?:respond|reply) yet\b"
    r"|\bwhat did i (?:just )?(?:ask|tell|send)\b",
    re.IGNORECASE,
)
_VERB = re.compile(r"\b(send|tell|ask|message|ping|note)\b", re.IGNORECASE)
_FILLER = re.compile(
    r"^(?:(?:another|a|the)\s+)?(?:message|note)\s*,?\s*"
    r"(?:say(?:ing)?|asking(?:\s+(?:it|him|her|them))?(?:\s+to)?|to|:)?\s*"
    r"|^(?:say(?:ing)?|asking(?:\s+(?:it|him|her|them))?(?:\s+to)?|to|:)\s*",
    re.IGNORECASE,
)
_QUOTED = re.compile(r"^[\"“'](.+?)[\"”']\s*(.*)$", re.DOTALL)
_PRONOUN = re.compile(r"\b(they|them|he|him|she|her|it)\b", re.IGNORECASE)


@dataclass
class Action:
    to: str
    text: str
    dispatch_id: str


@dataclass
class TurnResult:
    reply: str
    actions: list[Action] = field(default_factory=list)
    gate: str | None = None


def handle(session: Session, text: str) -> TurnResult:
    """Apply one desk message to the session and return the reply plus bus actions."""
    raw = text.strip()
    session.add_turn("desk", raw)
    result = _decide(session, raw)
    session.add_turn("leo", result.reply)
    return result


def _decide(session: Session, text: str) -> TurnResult:
    gate = external_gate(text)
    if gate:
        return TurnResult(
            reply="That needs Jeremy's yes before I send, spend, or publish. I did not do it.",
            gate=gate,
        )

    if _STATUS.search(text) and not _is_dispatch(text):
        return TurnResult(reply=_status_reply(session, text))

    seat, _start, end = find_seat(text)
    verb = _VERB.search(text)
    if verb and seat:
        if seat in SELF_SEATS:
            return TurnResult(reply="That's me. Name the seat that should get the note.")
        body = _body(text[end:], verb.group(1))
        if not body:
            return TurnResult(reply=f"What should I send {display(seat)}?")
        item = session.new_dispatch(seat, body)
        stop = "" if body[-1:] in ".?" else "."
        return TurnResult(
            reply=f"Sent to {display(seat)}: {body}{stop} No reply yet.",
            actions=[Action(to=seat, text=body, dispatch_id=item.id)],
        )

    if seat and _only_seat(text, seat):
        waiting = session.open_to(seat) or (
            session.last_dispatch() if session.last_dispatch() and session.last_dispatch().seat == seat else None
        )
        if waiting and waiting.status == "open":
            return TurnResult(reply=f"Still waiting on {display(seat)}. The note was: {waiting.text}.")
        if waiting and waiting.reply:
            return TurnResult(reply=f"{display(seat)} replied: {waiting.reply}")
        return TurnResult(reply=f"{display(seat)} is a seat. Tell me the note to send.")

    if session.turns[:-1]:
        return TurnResult(reply="Say which seat and the note. I won't answer for them.")
    return TurnResult(reply="I'm here. Say which seat and the note.")


def _is_dispatch(text: str) -> bool:
    seat, _start, _end = find_seat(text)
    return bool(seat and seat not in SELF_SEATS and _VERB.search(text) and not _STATUS.search(text))


def _status_reply(session: Session, text: str) -> str:
    if re.search(r"what did i", text, re.IGNORECASE):
        last = session.last_dispatch()
        if last is None:
            return "You haven't asked me to send anything in this thread."
        return f"You asked me to send {display(last.seat)}: {last.text}."

    seat, _start, _end = find_seat(text)
    if seat is None and _PRONOUN.search(text):
        last = session.last_dispatch()
        seat = last.seat if last else None
    if seat is None:
        return "Nothing is waiting on a reply."
    item = next((d for d in reversed(session.dispatches) if d.seat == seat), None)
    if item is None:
        return f"Nothing is waiting on {display(seat)}."
    if item.reply:
        return f"{display(seat)} replied: {item.reply}"
    return f"No reply from {display(seat)} yet. The note was: {item.text}."


def _body(after_seat: str, verb: str) -> str:
    body = after_seat.strip()
    body = _FILLER.sub("", body).strip()
    quoted = _QUOTED.match(body)
    if quoted:
        rest = quoted.group(2).strip()
        body = quoted.group(1) if not rest else f"{quoted.group(1)} {rest}"
    body = body.strip()
    if not body and verb.lower() == "ping":
        return "ping"
    return body


def _only_seat(text: str, seat: str) -> bool:
    found, _start, _end = find_seat(text)
    if found != seat:
        return False
    stripped = text.lower()
    for alias, mapped in ALIASES:
        if mapped != seat:
            continue
        stripped = re.sub(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", " ", stripped)
    leftover = re.sub(r"[^a-z0-9]+", "", stripped)
    return leftover == ""
