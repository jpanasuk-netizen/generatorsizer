"""Turn a Connecture bus message into Hermes gateway calls and post those replies.

The posted text is the completion, a config block, or a down line. It is never
a sentence this process made up on the seat's behalf.
"""

from __future__ import annotations

from leo.bus import Bus
from leo.fleet import display
from leo.gates import external_gate

from hermes.configcheck import diagnose
from hermes.gateway import Completion, Gateway, GatewayError
from hermes.profiles import FILE_BUS_ONLY, gateway_model, targets_for

VIA = "hermes-gateway"
_GATE = "That needs Jeremy's yes before I send, spend, or publish. I did not call Hermes."


def process_new(bus: Bus, gateway: Gateway, state: dict, config: dict | None = None) -> list[str]:
    since = int(state.get("since") or 0)
    posted: list[str] = []
    for message in bus.read(since=since, limit=50):
        state["since"] = max(int(state["since"]), int(message["id"]))
        payload = message.get("payload") if isinstance(message.get("payload"), dict) else {}
        if payload.get("via") == VIA:
            continue
        seats = targets_for(str(message.get("to") or ""))
        if not seats:
            continue
        sender = str(message.get("from") or "")
        owner = str(payload.get("for") or sender)
        text = str(message.get("text") or "")
        topic = str(message.get("topic") or "talk")
        blocked = _blocked(text, config)
        if blocked is not None:
            posted.append(_post(bus, state, seats[0], owner, blocked, topic, ""))
            continue
        for seat in seats:
            reply, model = _answer(seat, text, gateway)
            posted.append(_post(bus, state, seat, owner, reply, topic, model))
    return posted


def _blocked(text: str, config: dict | None) -> str | None:
    if external_gate(text):
        return _GATE
    if config is None:
        return None
    problems = diagnose(config)
    if not problems:
        return None
    return f"Hermes config is inconsistent ({', '.join(problems)}). I did not call the gateway."


def _answer(seat: str, text: str, gateway: Gateway) -> tuple[str, str]:
    if seat in FILE_BUS_ONLY:
        return (f"{display(seat)} has no Hermes profile. It stays on the file bus.", "")
    model = gateway_model(seat)
    if model is None:
        return (f"{display(seat)} has no Hermes profile on the gateway.", "")
    try:
        completion: Completion = gateway.complete(model, text)
    except GatewayError as exc:
        if exc.status is None:
            return ("Hermes gateway did not answer.", model)
        return (f"Hermes gateway did not answer (HTTP {exc.status}).", model)
    return (completion.text, completion.model or model)


def _post(bus: Bus, state: dict, seat: str, owner: str, text: str, topic: str, model: str) -> str:
    sent = bus.send(
        from_=seat,
        to=owner,
        text=text,
        topic=topic,
        payload={"via": VIA, "model": model, "seat": seat},
    )
    state["since"] = max(int(state["since"]), int(sent["id"]))
    return text
