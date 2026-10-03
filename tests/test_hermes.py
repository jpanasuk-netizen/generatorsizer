"""Hermes answers Connecture with the gateway's text, or it says the gateway did not answer."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from leo.bus import MemoryBus
from leo.service import process_new as leo_process

from hermes.bridge import process_new
from hermes.configcheck import diagnose, parse_config, repaired_primary
from hermes.gateway import GatewayError, HttpGateway, ScriptedGateway
from hermes.ports import BUS_PORT, bus_port

BROKEN = {
    "model": {
        "provider": "fcc",
        "default": "claude-sonnet-4-20250514",
        "base_url": "https://api.minimax.io/v1",
        "api_mode": "chat_completions",
        "key_env": "MINIMAX_API_KEY",
    },
    "providers": {"fcc": {"transport": "codex_responses", "default_model": "gemini-flash"}},
    "fallback_providers": ["minimax", "vyce"],
}

BROKEN_YAML = """
model:
  provider: fcc
  default: claude-sonnet-4-20250514
  base_url: https://api.minimax.io/v1
  api_mode: chat_completions
  key_env: MINIMAX_API_KEY
providers:
  fcc:
    transport: codex_responses
    default_model: gemini-flash
"""


class ConfigTests(unittest.TestCase):
    def test_hybrid_primary_is_named_and_the_repair_clears_it(self):
        problems = diagnose(BROKEN)
        self.assertEqual(
            problems,
            ["fcc-base-url-minimax", "fcc-key-minimax", "fcc-api-mode-chat", "fcc-transport-codex"],
        )
        repaired = repaired_primary(BROKEN)
        self.assertEqual(diagnose(repaired), [])
        self.assertEqual(repaired["model"]["base_url"], "http://127.0.0.1:8082/v1")
        self.assertEqual(repaired["model"]["api_mode"], "anthropic_messages")
        self.assertEqual(repaired["model"]["key_env"], "FCC_API_KEY")
        self.assertEqual(repaired["model"]["default"], "anthropic/cloudflare/@cf/moonshotai/kimi-k2.7-code")
        self.assertEqual(repaired["providers"]["fcc"]["transport"], "anthropic_messages")
        self.assertEqual(repaired["fallback_providers"], ["minimax", "vyce"])

    def test_yaml_block_parses_the_same_hybrid(self):
        parsed = parse_config(BROKEN_YAML)
        self.assertEqual(diagnose(parsed), diagnose(BROKEN))


class PortTests(unittest.TestCase):
    def test_bus_defaults_to_8789_and_refuses_taken_ports(self):
        self.assertEqual(bus_port(None), BUS_PORT)
        self.assertEqual(BUS_PORT, 8789)
        for port in (8787, 8788, 8642, 8082, 8650, 8790):
            with self.assertRaises(ValueError):
                bus_port(port)


class BridgeTests(unittest.TestCase):
    def test_posts_the_gateway_text_for_a_profile(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="hermes-bot", text="ping the gateway", topic="talk")
        gateway = ScriptedGateway({"hermes-bot": "HERMES_FCC_OK"})
        posted = process_new(bus, gateway, {"since": 0})
        self.assertEqual(posted, ["HERMES_FCC_OK"])
        self.assertEqual(gateway.calls, [("hermes-bot", "ping the gateway")])
        reply = bus.messages[-1]
        self.assertEqual(reply["from"], "hermes-bot")
        self.assertEqual(reply["to"], "desk")
        self.assertEqual(reply["text"], "HERMES_FCC_OK")
        again = process_new(bus, gateway, {"since": reply["id"] - 1})
        self.assertEqual(again, [])
        self.assertEqual(len(gateway.calls), 1)

    def test_seo_directory_name_maps_onto_the_fleet_seat(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="seobot", text="review the page", topic="talk")
        gateway = ScriptedGateway({"seobot": "page reviewed"})
        posted = process_new(bus, gateway, {"since": 0})
        self.assertEqual(posted, ["page reviewed"])
        self.assertEqual(gateway.calls, [("seobot", "review the page")])
        self.assertEqual(bus.messages[-1]["from"], "seo-bot")

    def test_down_gateway_does_not_invent_a_reply(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="cynthia", text="draft the niche", topic="talk")
        gateway = ScriptedGateway(error=GatewayError(404, "secret-token-value"))
        posted = process_new(bus, gateway, {"since": 0})
        self.assertEqual(posted, ["Hermes gateway did not answer (HTTP 404)."])
        self.assertNotIn("secret-token-value", posted[0])
        self.assertNotIn("niche", posted[0])

    def test_mimo_stays_on_the_file_bus(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="mimo", text="are you there", topic="talk")
        gateway = ScriptedGateway({"mimo": "should not be used"})
        posted = process_new(bus, gateway, {"since": 0})
        self.assertEqual(gateway.calls, [])
        self.assertIn("file bus", posted[0])
        self.assertNotIn("should not be used", posted[0])

    def test_spend_does_not_call_the_gateway(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="moneybot", text="spend $50 on ads", topic="talk")
        gateway = ScriptedGateway({"moneybot": "bought them"})
        posted = process_new(bus, gateway, {"since": 0})
        self.assertEqual(gateway.calls, [])
        self.assertIn("Jeremy", posted[0])
        self.assertNotIn("bought", posted[0])

    def test_broken_config_blocks_the_call(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="eve", text="run the hunt", topic="talk")
        gateway = ScriptedGateway({"eve": "hunt done"})
        posted = process_new(bus, gateway, {"since": 0}, config=BROKEN)
        self.assertEqual(gateway.calls, [])
        self.assertIn("fcc-base-url-minimax", posted[0])
        self.assertIn("fcc-api-mode-chat", posted[0])

    def test_desk_name_leo_is_not_answered_here(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="leo", text="send hermes a message, say ping", topic="talk")
        gateway = ScriptedGateway({"leo": "I am a new conversation", "hermes-bot": "pong"})
        self.assertEqual(process_new(bus, gateway, {"since": 0}), [])
        self.assertEqual(gateway.calls, [])

    def test_crew_fans_out_and_skips_a_profile_mimo_does_not_have(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="crew", text="status", topic="talk")
        gateway = ScriptedGateway({"muse": "muse up", "gemini-spark": "spark up", "hermes-bot": "hermes up"})
        posted = process_new(bus, gateway, {"since": 0})
        self.assertEqual(gateway.calls, [("muse", "status"), ("gemini-spark", "status"), ("hermes-bot", "status")])
        self.assertEqual(posted, ["muse up", "MiMo has no Hermes profile. It stays on the file bus.", "spark up", "hermes up"])

    def test_leo_handoff_comes_back_as_the_gateway_reply(self):
        bus = MemoryBus()
        bus.send(from_="desk", to="leo", text="send hermes a message, say ping", topic="talk")
        leo_state = {"since": 0, "sessions": {}}
        leo_process(bus, leo_state)
        gateway = ScriptedGateway({"hermes-bot": "gateway pong"})
        process_new(bus, gateway, {"since": 0})
        self.assertEqual(gateway.calls, [("hermes-bot", "ping")])
        forwarded = leo_process(bus, leo_state)
        self.assertIn("Hermes Bot replied: gateway pong", forwarded)


class HttpGatewayTests(unittest.TestCase):
    def test_chat_completions_and_a_404_body_stay_on_the_wire(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self._send(200, {"status": "ok", "platform": "hermes-agent", "version": "0.21.3"})

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                incoming = json.loads(self.rfile.read(length).decode())
                if self.path.startswith("/missing"):
                    self._send(404, {"error": "secret-token-value", "model": incoming.get("model")})
                    return
                self._send(
                    200,
                    {
                        "model": "anthropic/cloudflare/@cf/moonshotai/kimi-k2.7-code",
                        "choices": [{"message": {"role": "assistant", "content": "API_FCC_OK"}}],
                    },
                )

            def _send(self, status, body):
                raw = json.dumps(body).encode()
                self.send_response(status)
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
            base = f"http://127.0.0.1:{server.server_address[1]}"
            gateway = HttpGateway(base, "test-key")
            health = gateway.health()
            self.assertEqual(health["status"], "ok")
            self.assertEqual(health["platform"], "hermes-agent")
            completion = gateway.complete("hermes-bot", "ping")
            self.assertEqual(completion.text, "API_FCC_OK")
            self.assertIn("kimi-k2.7-code", completion.model)
            with self.assertRaises(GatewayError) as caught:
                HttpGateway(base + "/missing", "test-key").complete("hermes-bot", "ping")
            self.assertEqual(caught.exception.status, 404)
            self.assertNotIn("secret-token-value", str(caught.exception))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


class CliTests(unittest.TestCase):
    def test_check_and_port_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = os.path.join(tmp, "broken.yaml")
            with open(broken, "w", encoding="utf-8") as handle:
                handle.write(BROKEN_YAML)
            checked = subprocess.run(
                [sys.executable, "-m", "hermes", "check", broken],
                cwd="/workspace",
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 1, checked.stderr)
            body = json.loads(checked.stdout)
            self.assertIn("fcc-base-url-minimax", body["problems"])
            self.assertEqual(body["bus_port"], 8789)
            self.assertEqual(diagnose(body["repaired"]), [])

        refused = subprocess.run(
            [sys.executable, "-m", "hermes", "--port", "8787"],
            cwd="/workspace",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(refused.returncode, 2)
        self.assertIn("8787", refused.stderr)

        script = subprocess.run(
            ["sh", "hermes/connect.sh"],
            cwd="/workspace",
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "AIBUS_PORT": "8787"},
        )
        self.assertEqual(script.returncode, 2)
        self.assertIn("8787", script.stderr)


if __name__ == "__main__":
    unittest.main()
