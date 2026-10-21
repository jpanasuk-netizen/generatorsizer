"""Catch the hybrid Hermes primary that made FCC calls hit MiniMax or a 404.

The gateway on :8642 speaks OpenAI chat completions. The FCC proxy on :8082
does not: its chat-completions path is 404, and the working wire is
anthropic_messages to kimi-k2.7-code.
"""

from __future__ import annotations

FCC_BASE = "http://127.0.0.1:8082/v1"
FCC_MODEL = "anthropic/cloudflare/@cf/moonshotai/kimi-k2.7-code"

_SCALAR = {
    "provider",
    "default",
    "base_url",
    "api_mode",
    "key_env",
    "transport",
    "default_model",
}


def diagnose(document: dict) -> list[str]:
    """Return stable problem codes. An empty list means the primary is consistent."""
    model = document.get("model") or {}
    fcc = ((document.get("providers") or {}).get("fcc")) or {}
    provider = str(model.get("provider") or "")
    base = str(model.get("base_url") or "")
    mode = str(model.get("api_mode") or "")
    key_env = str(model.get("key_env") or "")
    transport = str(fcc.get("transport") or "")
    problems: list[str] = []
    if provider == "fcc" and "minimax" in base.lower():
        problems.append("fcc-base-url-minimax")
    if provider == "fcc" and key_env == "MINIMAX_API_KEY":
        problems.append("fcc-key-minimax")
    if provider == "fcc" and mode == "chat_completions":
        problems.append("fcc-api-mode-chat")
    if provider == "fcc" and transport == "codex_responses":
        problems.append("fcc-transport-codex")
    if provider == "fcc" and not base:
        problems.append("fcc-base-url-missing")
    if provider == "fcc" and base and "minimax" not in base.lower() and base.rstrip("/") != FCC_BASE:
        problems.append("fcc-base-url-unexpected")
    return problems


def repaired_primary(document: dict) -> dict:
    """Return a copy whose primary matches the FCC wire. Fallbacks stay as given."""
    model = dict(document.get("model") or {})
    providers = dict(document.get("providers") or {})
    fcc = dict(providers.get("fcc") or {})
    model["provider"] = "fcc"
    model["default"] = FCC_MODEL
    model["base_url"] = FCC_BASE
    model["api_mode"] = "anthropic_messages"
    model["key_env"] = "FCC_API_KEY"
    fcc["transport"] = "anthropic_messages"
    fcc["default_model"] = FCC_MODEL
    providers["fcc"] = fcc
    repaired = {"model": model, "providers": providers}
    if "fallback_providers" in document:
        repaired["fallback_providers"] = document["fallback_providers"]
    return repaired


def parse_config(text: str) -> dict:
    """Read the model and providers blocks. This is not a general YAML parser."""
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if line.startswith("- "):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = _unquote(value.strip())
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root
        if value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = value
    return _keep(root)


def _keep(document: dict) -> dict:
    kept: dict = {}
    model = document.get("model")
    if isinstance(model, dict):
        kept["model"] = {key: model[key] for key in _SCALAR if key in model}
    providers = document.get("providers")
    if isinstance(providers, dict) and isinstance(providers.get("fcc"), dict):
        fcc = providers["fcc"]
        kept["providers"] = {"fcc": {key: fcc[key] for key in _SCALAR if key in fcc}}
    if "fallback_providers" in document:
        kept["fallback_providers"] = document["fallback_providers"]
    return kept


def _unquote(value: str) -> str:
    if value.startswith("#"):
        return ""
    if " #" in value:
        value = value.split(" #", 1)[0].rstrip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value
