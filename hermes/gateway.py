"""Hermes gateway client. The text posted back is the gateway's text."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class GatewayError(Exception):
    def __init__(self, status: int | None, detail: str = "") -> None:
        self.status = status
        self.detail = detail
        super().__init__(detail or f"HTTP {status}")


@dataclass(frozen=True)
class Completion:
    text: str
    model: str


class Gateway(Protocol):
    def complete(self, model: str, text: str) -> Completion: ...

    def health(self) -> dict: ...


class ScriptedGateway:
    """Test double. It returns only the replies it was given."""

    def __init__(self, replies: dict[str, str] | None = None, error: GatewayError | None = None) -> None:
        self.replies = dict(replies or {})
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def complete(self, model: str, text: str) -> Completion:
        self.calls.append((model, text))
        if self.error is not None:
            raise self.error
        if model not in self.replies:
            raise GatewayError(None, "no scripted reply")
        return Completion(text=self.replies[model], model=model)

    def health(self) -> dict:
        if self.error is not None:
            raise self.error
        return {"status": "ok", "platform": "hermes-agent"}


class HttpGateway:
    def __init__(self, base_url: str, api_key: str = "", timeout: float = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def health(self) -> dict:
        body = self._request("GET", f"{self.base_url}/health")
        if not isinstance(body, dict):
            raise GatewayError(None, "health was not an object")
        return body

    def complete(self, model: str, text: str) -> Completion:
        body = self._request(
            "POST",
            f"{self.base_url}/v1/chat/completions",
            {"model": model, "messages": [{"role": "user", "content": text}]},
        )
        content, reported = _completion_text(body)
        if not content:
            raise GatewayError(None, "completion had no text")
        return Completion(text=content, model=reported or model)

    def _request(self, method: str, url: str, data: dict | None = None) -> dict | list:
        payload = None if data is None else json.dumps(data).encode()
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(url, data=payload, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode()
        except urllib.error.HTTPError as exc:
            raise GatewayError(exc.code, "gateway http error") from exc
        except urllib.error.URLError as exc:
            raise GatewayError(None, "gateway unreachable") from exc
        if not raw:
            return {}
        return json.loads(raw)


def _completion_text(body: dict | list) -> tuple[str, str]:
    if not isinstance(body, dict):
        return "", ""
    choices = body.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"], str(body.get("model") or "")
    content = body.get("content")
    if isinstance(content, list) and content and isinstance(content[0], dict):
        text = content[0].get("text")
        if isinstance(text, str):
            return text, str(body.get("model") or "")
    return "", ""
