"""Every bot can be sent a note and can see that note in its own chat."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from leo.bus import HttpBus, MemoryBus
from leo.chat import texts
from leo.fleet import BOTS, address, display
from leo.product import run_until_idle
from hermes.gateway import Completion, GatewayError
from hermes.profiles import gateway_model
from kit.lanes import lane_for


class EchoGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def complete(self, model: str, text: str) -> Completion:
        self.calls.append((model, text))
        return Completion(text=f"echo:{model}:{text}", model=model)

    def health(self) -> dict:
        return {"status": "ok", "platform": "hermes-agent"}


def _token(seat: str) -> str:
    return f"[{seat}]"


class EchoLane:
    def __init__(self, lane: str, book: list) -> None:
        self.lane = lane
        self.book = book

    def complete(self, seat: str, text: str) -> str:
        self.book.append((self.lane, seat, text))
        return f"echo:{seat}:{text}"


def _lanes() -> tuple[dict, list]:
    book: list = []
    lanes = {name: EchoLane(name, book) for name in ("gemini", "grokbot", "grok", "freebuff", "muse", "muse-ai")}
    return lanes, book


def _load(bus, gateway: EchoGateway, lanes: dict | None = None) -> None:
    bus.send(from_="desk", to="*", text="house-check", topic="talk")
    for seat in BOTS:
        bus.send(
            from_="desk",
            to="leo",
            text=f"send {address(seat)} a message, say {_token(seat)}",
            topic="talk",
        )
    bus.send(from_="desk", to="leo", text="send jeremy a message, say hello-jeremy", topic="talk")
    run_until_idle(bus, gateway, lanes=lanes)


def _assert_chats(test: unittest.TestCase, bus, gateway: EchoGateway, book: list) -> None:
    called = {model for model, _text in gateway.calls}
    for seat in BOTS:
        seen = texts(bus, seat)
        blob = "\n".join(seen)
        test.assertIn("house-check", seen, seat)
        test.assertTrue(any(_token(seat) in line for line in seen), f"{seat} chat missing its note: {seen}")
        for other in BOTS:
            if other == seat:
                continue
            test.assertNotIn(_token(other), blob, f"{seat} can see {other}")
        lane = lane_for(seat)
        if lane == "hermes":
            model = gateway_model(seat)
            test.assertIn(model, called, seat)
            test.assertTrue(any(line == f"echo:{model}:{_token(seat)}" for line in seen), seen)
        elif lane == "grok":
            test.assertTrue(any("usage is gone" in line for line in seen), seen)
            test.assertFalse(any(item[0] == "grok" for item in book))
        elif lane:
            test.assertIn((lane, seat, _token(seat)), book, seat)
            test.assertTrue(any(line == f"echo:{seat}:{_token(seat)}" for line in seen), seen)
            test.assertNotIn(seat, called)
        elif seat == "mimo":
            test.assertTrue(any("file bus" in line for line in seen), seen)
            test.assertNotIn("mimo", called)
        else:
            test.assertTrue(any("no Hermes profile" in line for line in seen), seen)

        desk = texts(bus, "desk")
        test.assertTrue(
            any(line.startswith(f"{display(seat)} replied:") for line in desk),
            f"desk did not show {seat}: {desk}",
        )
        if lane == "hermes":
            test.assertTrue(any(_token(seat) in line and line.startswith(f"{display(seat)} replied:") for line in desk))

    jeremy = texts(bus, "jeremy")
    test.assertIn("hello-jeremy", "\n".join(jeremy))
    test.assertTrue(all(message_from != "jeremy" for message_from in _senders(bus, "jeremy")))
    test.assertFalse(any(line.startswith("Jeremy replied:") for line in texts(bus, "desk")))

    leo = "\n".join(texts(bus, "leo"))
    for seat in BOTS:
        test.assertIn(display(seat), leo)
        test.assertIn(_token(seat), leo)
    test.assertIn("hello-jeremy", leo)
    test.assertIn("house-check", texts(bus, "leo"))
    test.assertIn("house-check", texts(bus, "desk"))
    test.assertIn("house-check", texts(bus, "jeremy"))


def _senders(bus, seat: str) -> list[str]:
    from leo.chat import seat_chat

    return [str(message.get("from") or "") for message in seat_chat(bus, seat)]


class FleetChatTests(unittest.TestCase):
    def test_every_handler_phrase_and_seat_id_map_to_that_bot(self):
        from leo.fleet import find_seat, seat_of_sender

        self.assertEqual(len(BOTS), 24)
        for seat in BOTS:
            found, start, _end = find_seat(f"send {address(seat)} a message")
            self.assertEqual(found, seat)
            self.assertEqual(start > 0, True, seat)
            self.assertEqual(seat_of_sender(seat), seat)

    def test_memory_bus_delivers_every_bot_chat(self):
        bus = MemoryBus()
        gateway = EchoGateway()
        lanes, book = _lanes()
        _load(bus, gateway, lanes)
        _assert_chats(self, bus, gateway, book)

    def test_http_bus_delivers_every_bot_chat(self):
        served: list[dict] = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                query = parse_qs(urlparse(self.path).query)
                since = int(query.get("since", ["0"])[0])
                limit = int(query.get("limit", ["50"])[0])
                rows = [message for message in served if message["id"] > since][:limit]
                self._send(rows)

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                incoming = json.loads(self.rfile.read(length).decode())
                message = {
                    "id": len(served) + 1,
                    "from": incoming["from"],
                    "to": incoming["to"],
                    "text": incoming["text"],
                    "topic": incoming.get("topic") or "talk",
                    "payload": incoming.get("payload"),
                }
                served.append(message)
                self._send(message)

            def _send(self, body):
                raw = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, fmt, *args):
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            bus = HttpBus(f"http://127.0.0.1:{server.server_address[1]}", "test-token")
            gateway = EchoGateway()
            lanes, book = _lanes()
            _load(bus, gateway, lanes)
            _assert_chats(self, bus, gateway, book)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_a_direct_note_is_in_both_chats(self):
        bus = MemoryBus()
        bus.send(from_="annie", to="eve", text="bring the board", topic="talk")
        gateway = EchoGateway()
        run_until_idle(bus, gateway)
        self.assertIn("bring the board", texts(bus, "eve"))
        self.assertIn("bring the board", texts(bus, "annie"))
        self.assertTrue(any(line.startswith("echo:eve:") for line in texts(bus, "annie")))
        self.assertNotIn("bring the board", texts(bus, "cynthia"))

    def test_crew_note_is_visible_in_each_crew_chat(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="crew", text="crew-status", topic="talk")
        run_until_idle(bus, EchoGateway())
        for seat in ("muse", "mimo", "gemini-spark", "hermes-bot"):
            self.assertIn("crew-status", texts(bus, seat), seat)
        self.assertNotIn("crew-status", texts(bus, "cynthia"))

    def test_down_gateway_is_what_the_bot_chat_shows(self):
        class Down:
            def complete(self, model: str, text: str) -> Completion:
                raise GatewayError(404, "secret-token-value")

            def health(self) -> dict:
                return {}

        bus = MemoryBus()
        bus.send(from_="desk", to="leo", text="send cynthia a message, say niche-note", topic="talk")
        run_until_idle(bus, Down())
        seen = texts(bus, "cynthia")
        self.assertTrue(any("niche-note" in line for line in seen))
        self.assertTrue(any(line == "Hermes gateway did not answer (HTTP 404)." for line in seen))
        self.assertNotIn("secret-token-value", "\n".join(seen))
        self.assertTrue(any("Cynthia replied: Hermes gateway did not answer (HTTP 404)." in line for line in texts(bus, "desk")))


if __name__ == "__main__":
    unittest.main()
