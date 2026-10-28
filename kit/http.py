"""One HTTP lane. It talks to its own base URL and never to a sibling lane."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class LaneDown(Exception):
    def __init__(self, status: int | None) -> None:
        self.status = status
        super().__init__("lane down" if status is None else f"HTTP {status}")


class HttpLane:
    def __init__(self, base_url: str, timeout: float = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def complete(self, seat: str, text: str) -> str:
        payload = json.dumps({"seat": seat, "text": text}).encode()
        request = urllib.request.Request(
            f"{self.base_url}/message",
            data=payload,
            method="POST",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode() or "{}")
        except urllib.error.HTTPError as exc:
            raise LaneDown(exc.code) from exc
        except urllib.error.URLError as exc:
            raise LaneDown(None) from exc
        reply = body.get("text") if isinstance(body, dict) else None
        if not isinstance(reply, str) or not reply:
            raise LaneDown(None)
        return reply
