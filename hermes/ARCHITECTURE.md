# Hermes for Connecture

## What is wrong

Connecture's bus is the Hermes seat bus, and the seats do not arrive.

Three separate failures stack:

1. The desk name `leo` is answered by Connecture's talk runner. The Windows Hermes profile `leo` on `127.0.0.1:8642` is a different process. The runner has no gateway client, so a hand-off never becomes a profile turn.
2. The last Hermes primary on disk was a hybrid. `model.provider` said `fcc` and the model id was a Sonnet name, while `base_url` and `key_env` still pointed at MiniMax, and `api_mode` was `chat_completions`. The FCC proxy on `:8082` returns 404 for `/v1/chat/completions`. The wire that answered `HERMES_FCC_OK` is `anthropic_messages` to `anthropic/cloudflare/@cf/moonshotai/kimi-k2.7-code` at `http://127.0.0.1:8082/v1`, with `FCC_API_KEY`. The gateway on `:8642` is what Connecture should call. It speaks `/v1/chat/completions` and uses that FCC wire itself.
3. The old starter `D:\Freebuff\hermes-fix\start_aibus_8787.sh` still carries 8787 in its name. That port is the Gmail OAuth callback. The bus listens on 8789. 8788 is already a Windows Hermes python process. Binding the bus on either port takes the wrong service.

WSL `~/.hermes` is a second install. It does not own `:8642`.

## Replacement

```
Connecture bus :8789
    │
    ▼
 port guard ── 8787 / 8788 / 8642 / 8082 / 8650 / 8790 ──► refuse
    │
    ▼
 config check ── hybrid primary ──► tell the desk, do not call
    │
    ▼
 profile map ── hermes-bot, cynthia, eve, …
    │            gemini, grokbot, grok, freebuff, muse, muse.ai ──► kit/lanes.py
    │            mimo ──► file bus :8650, no gateway call
    │            leo   ──► desk dispatcher, no second answer
    ▼
 POST 127.0.0.1:8642/v1/chat/completions   (Hermes seats only)
    │
    ▼
 post the completion text back on the bus, from that seat
```

| Piece | Job |
|---|---|
| `ports` | Default the bus to 8789 and refuse the ports that already belong to something else. |
| `configcheck` | Name the hybrid-primary bugs. `repaired_primary` sets the FCC wire and leaves fallbacks alone. |
| `profiles` | Map a Hermes profile onto the gateway. `seo-bot` is the directory `seobot`. Gemini, Grok, Grokbot, FreeBuff, Muse, and muse.ai are kit lanes, not gateway models. `mimo` stays on the file bus. Jeremy is not answered. |
| `gateway` | `GET /health` and `POST /v1/chat/completions`. A missing gateway raises. It does not fill in a reply. |
| `bridge` | Read the bus. For each seat this bridge owns, post one reply: the completion, the config block, the file-bus line, or `Hermes gateway did not answer`. |

A spend, publish, or email in the note does not reach the gateway.

The Leo desk package routes the human. This package is the worker behind the specialist seats. Run it as `python -m hermes --serve` with `CONNECTURE_BUS_URL`, `CONNECTURE_BUS_TOKEN`, and optionally `HERMES_GATEWAY_URL` and `HERMES_API_KEY`. `hermes/connect.sh` is the starter that used to live in `hermes-fix`, with the port fixed.

## What this does not replace

The Windows gateway at `C:\Users\jpana\AppData\Local\hermes` and the WSL tree at `/home/jpanasuk/.hermes` stay on LightBringer. This package does not write `config.yaml` and does not restart the gateway. `python -m hermes check <file>` prints the problem codes and the repaired primary so that edit can be applied with the Hermes CLI on the machine that owns the file.
