"""One desk thread. Replies exist only after the seat posts them."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Dispatch:
    id: str
    seat: str
    text: str
    status: str = "open"  # open | replied | blocked
    reply: str | None = None


@dataclass
class Session:
    turns: list[tuple[str, str]] = field(default_factory=list)
    dispatches: list[Dispatch] = field(default_factory=list)
    _seq: int = 0

    def add_turn(self, role: str, text: str) -> None:
        self.turns.append((role, text))

    def new_dispatch(self, seat: str, text: str) -> Dispatch:
        self._seq += 1
        item = Dispatch(id=f"d{self._seq}", seat=seat, text=text)
        self.dispatches.append(item)
        return item

    def last_dispatch(self) -> Dispatch | None:
        return self.dispatches[-1] if self.dispatches else None

    def open_to(self, seat: str) -> Dispatch | None:
        for item in reversed(self.dispatches):
            if item.seat == seat and item.status == "open":
                return item
        return None

    def note_reply(self, seat: str, text: str) -> Dispatch | None:
        item = self.open_to(seat)
        if item is None:
            return None
        item.reply = text
        item.status = "replied"
        return item
