"""Human gates. A bus hand-off is not an external send."""

from __future__ import annotations

import re

# External world only. "send gemini a message" is a dispatch, not this gate.
_EXTERNAL = re.compile(
    r"\b("
    r"spend|purchase|wire money|transfer money|gofundme|"
    r"wallet|publish|tweet|"
    r"post (?:it |this )?(?:on|to) (?:x|twitter|youtube|instagram|tiktok)|"
    r"send (?:an |the |this )?e-?mail|email this|mail this|"
    r"pay \$|spend \$"
    r")\b",
    re.IGNORECASE,
)


def external_gate(text: str) -> str | None:
    if _EXTERNAL.search(text):
        return "jeremy-yes"
    return None
