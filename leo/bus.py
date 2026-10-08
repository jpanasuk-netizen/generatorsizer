"""Bus port. The live client talks to the hermes-aibus HTTP API."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Protocol


class Bus(Protocol):
    def read(self, since: int | None = None, limit: int = 50) -> list[dict]: ...

    def send(self, *, from_: str, to: str, text: str, topic: str = "talk", payload: dict | None = None) -> dict: ...


class MemoryBus:
    def __init__(self) -> None:
        self.messages: list[dict] = []
        self._seq = 0

    def read(self, since: int | None = None, limit: int = 50) -> list[dict]:
        rows = self.messages
        if since is not None:
            rows = [row for row in rows if row["id"] > since]
        return rows[:limit]

    def send(self, *, from_: str, to: str, text: str, topic: str = "talk", payload: dict | None = None) -> dict:
        self._seq += 1
        message = {"id": self._seq, "from": from_, "to": to, "text": text, "topic": topic, "payload": payload}
        self.messages.append(message)
        return message


class HttpBus:
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    def read(self, since: int | None = None, limit: int = 50) -> list[dict]:
        params = {"limit": str(limit), "format": "json"}
        if since is not None:
            params["since"] = str(since)
        url = f"{self.base_url}/bus/messages?{urllib.parse.urlencode(params)}"
        body = self._request("GET", url)
        if isinstance(body, list):
            return body
        return list(body.get("messages") or [])

    def send(self, *, from_: str, to: str, text: str, topic: str = "talk", payload: dict | None = None) -> dict:
        url = f"{self.base_url}/bus/messages"
        data = {"from": from_, "to": to, "text": text, "topic": topic}
        if payload is not None:
            data["payload"] = payload
        body = self._request("POST", url, data)
        if isinstance(body, dict) and "id" in body:
            return body
        if isinstance(body, dict) and isinstance(body.get("message"), dict):
            return body["message"]
        raise RuntimeError("bus post did not return a message id")

    def _request(self, method: str, url: str, data: dict | None = None) -> dict | list:
        payload = None if data is None else json.dumps(data).encode()
        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read().decode()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            raise RuntimeError(f"bus {method} failed: HTTP {exc.code} {detail}") from exc
        if not raw:
            return {}
        return json.loads(raw)
