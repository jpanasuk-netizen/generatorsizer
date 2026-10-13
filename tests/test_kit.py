"""Each kit lane has its own chat. A note does not cross into a sibling lane."""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from leo.bus import MemoryBus
from leo.chat import texts
from leo.product import run_until_idle
from hermes.gateway import ScriptedGateway
from kit.http import HttpLane

KIT_NOTES = (
    ("hermes", "hermes-bot", "send hermes a message, say [hermes]"),
    ("gemini", "gemini-spark", "send gemini a message, say [gemini]"),
    ("grokbot", "grokbot", "send grokbot a message, say [grokbot]"),
    ("grok", "grok", "send grok a message, say [grok]"),
    ("freebuff", "freebuff", "send freebuff a message, say [freebuff]"),
    ("muse", "muse", "send muse a message, say [muse]"),
    ("muse-ai", "muse-ai", 'send muse.ai a message, say [muse.ai]'),
)


class Recording:
    def __init__(self, lane: str) -> None:
        self.lane = lane
        self.calls: list[tuple[str, str]] = []

    def complete(self, seat: str, text: str) -> str:
        self.calls.append((seat, text))
        return f"{self.lane}:{text}"


class KitTests(unittest.TestCase):
    def test_each_kit_chat_sees_only_its_note(self):
        bus = MemoryBus()
        for _lane, _seat, text in KIT_NOTES:
            bus.send(from_="desk", to="leo", text=text, topic="talk")
        gateway = ScriptedGateway({"hermes-bot": "hermes:[hermes]"})
        lanes = {name: Recording(name) for name in ("gemini", "grokbot", "grok", "freebuff", "muse", "muse-ai")}
        run_until_idle(bus, gateway, lanes=lanes)

        self.assertEqual(gateway.calls, [("hermes-bot", "[hermes]")])
        self.assertEqual(lanes["gemini"].calls, [("gemini-spark", "[gemini]")])
        self.assertEqual(lanes["grokbot"].calls, [("grokbot", "[grokbot]")])
        self.assertEqual(lanes["grok"].calls, [])
        self.assertEqual(lanes["freebuff"].calls, [("freebuff", "[freebuff]")])
        self.assertEqual(lanes["muse"].calls, [("muse", "[muse]")])
        self.assertEqual(lanes["muse-ai"].calls, [("muse-ai", "[muse.ai]")])

        self.assertIn("hermes:[hermes]", texts(bus, "hermes-bot"))
        self.assertIn("gemini:[gemini]", texts(bus, "gemini-spark"))
        self.assertIn("grokbot:[grokbot]", texts(bus, "grokbot"))
        self.assertTrue(any("usage is gone" in line for line in texts(bus, "grok")))
        self.assertIn("[grok]", "\n".join(texts(bus, "grok")))
        self.assertIn("freebuff:[freebuff]", texts(bus, "freebuff"))
        self.assertIn("muse:[muse]", texts(bus, "muse"))
        self.assertIn("muse-ai:[muse.ai]", texts(bus, "muse-ai"))
        self.assertNotIn("[muse.ai]", "\n".join(texts(bus, "muse")))
        self.assertNotIn("[muse]", "\n".join(texts(bus, "muse-ai")))
        self.assertNotIn("gemini-spark", {model for model, _text in gateway.calls})

    def test_open_grok_uses_the_grok_lane(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="leo", text="send grok a message, say [grok-open]", topic="talk")
        grok = Recording("grok")
        run_until_idle(bus, ScriptedGateway({}), lanes={"grok": grok}, grok_open=True)
        self.assertEqual(grok.calls, [("grok", "[grok-open]")])
        self.assertIn("grok:[grok-open]", texts(bus, "grok"))
        self.assertFalse(any("usage is gone" in line for line in texts(bus, "grok")))

    def test_gemini_and_muse_use_different_ports(self):
        hits: dict[str, list[str]] = {"gemini": [], "muse": [], "muse-ai": []}

        def serve(name: str):
            class Handler(BaseHTTPRequestHandler):
                def do_POST(self):
                    length = int(self.headers.get("Content-Length") or 0)
                    incoming = json.loads(self.rfile.read(length).decode())
                    hits[name].append(incoming["text"])
                    raw = json.dumps({"text": f"{name}-saw:{incoming['text']}"}).encode()
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
            return server, thread

        servers = {name: serve(name) for name in hits}
        try:
            lanes = {name: HttpLane(f"http://127.0.0.1:{server.server_address[1]}") for name, (server, _thread) in servers.items()}
            bus = MemoryBus()
            bus.send(from_="desk", to="gemini-spark", text="hi-gemini", topic="talk")
            bus.send(from_="desk", to="muse", text="hi-muse", topic="talk")
            bus.send(from_="desk", to="muse-ai", text="hi-muse-ai", topic="talk")
            run_until_idle(bus, ScriptedGateway({}), lanes=lanes)
        finally:
            for server, thread in servers.values():
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

        self.assertEqual(hits["gemini"], ["hi-gemini"])
        self.assertEqual(hits["muse"], ["hi-muse"])
        self.assertEqual(hits["muse-ai"], ["hi-muse-ai"])
        self.assertIn("gemini-saw:hi-gemini", texts(bus, "gemini-spark"))
        self.assertIn("muse-saw:hi-muse", texts(bus, "muse"))
        self.assertIn("muse-ai-saw:hi-muse-ai", texts(bus, "muse-ai"))
        self.assertNotIn("hi-gemini", "\n".join(texts(bus, "muse")))
        self.assertNotIn("hi-muse-ai", "\n".join(texts(bus, "muse")))
