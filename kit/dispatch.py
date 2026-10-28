"""Deliver a bus note on the lane that owns the seat, and post that lane's reply."""

from __future__ import annotations

from leo.bus import Bus
from leo.fleet import display
from leo.gates import external_gate

from hermes.configcheck import diagnose
from hermes.gateway import Completion, Gateway, GatewayError
from hermes.profiles import FILE_BUS_ONLY, gateway_model, targets_for
from kit.http import LaneDown
from kit.lanes import closed_reason, lane_for

_GATE = "That needs Jeremy's yes before I send, spend, or publish. I did not do it."


def process_new(
    bus: Bus,
    gateway: Gateway,
    state: dict,
    config: dict | None = None,
    lanes: dict | None = None,
    grok_open: bool = False,
) -> list[str]:
    since = int(state.get("since") or 0)
    posted: list[str] = []
    batch = bus.read(since=since, limit=50)
    for message in batch:
        payload = message.get("payload") if isinstance(message.get("payload"), dict) else {}
        if payload.get("via"):
            continue
        seats = targets_for(str(message.get("to") or ""))
        if not seats:
            continue
        sender = str(message.get("from") or "")
        owner = str(payload.get("for") or sender)
        text = str(message.get("text") or "")
        topic = str(message.get("topic") or "talk")
        if external_gate(text):
            posted.append(_post(bus, seats[0], owner, _GATE, topic, ""))
            continue
        for seat in seats:
            reply, lane = _answer(seat, text, gateway, lanes or {}, config, grok_open)
            posted.append(_post(bus, seat, owner, reply, topic, lane))
    if batch:
        state["since"] = max(int(message["id"]) for message in batch)
    return posted


def _answer(seat, text, gateway, lanes, config, grok_open) -> tuple[str, str]:
    if seat in FILE_BUS_ONLY:
        return (f"{display(seat)} has no Hermes profile. It stays on the file bus.", "")
    lane = lane_for(seat)
    if lane is None:
        return (f"{display(seat)} has no Hermes profile on the gateway.", "")
    reason = closed_reason(lane, grok_open)
    if reason:
        return (reason, lane)
    if lane == "hermes":
        problems = diagnose(config) if config is not None else []
        if problems:
            return (f"Hermes config is inconsistent ({', '.join(problems)}). I did not call the gateway.", lane)
        model = gateway_model(seat)
        if model is None:
            return (f"{display(seat)} has no Hermes profile on the gateway.", lane)
        try:
            completion: Completion = gateway.complete(model, text)
        except GatewayError as exc:
            if exc.status is None:
                return ("Hermes gateway did not answer.", lane)
            return (f"Hermes gateway did not answer (HTTP {exc.status}).", lane)
        return (completion.text, completion.model or model)
    client = lanes.get(lane)
    if client is None:
        return (f"{display(seat)} did not answer.", lane)
    try:
        reply = client.complete(seat, text)
    except LaneDown as exc:
        if exc.status is None:
            return (f"{display(seat)} did not answer.", lane)
        return (f"{display(seat)} did not answer (HTTP {exc.status}).", lane)
    if not isinstance(reply, str) or not reply:
        return (f"{display(seat)} did not answer.", lane)
    return (reply, lane)


def _post(bus: Bus, seat: str, owner: str, text: str, topic: str, lane: str) -> str:
    bus.send(
        from_=seat,
        to=owner,
        text=text,
        topic=topic,
        payload={"via": lane or "kit", "lane": lane, "seat": seat},
    )
    return text
