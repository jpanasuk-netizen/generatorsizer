# Leo architecture

## What is wrong

The desk addresses `leo`. That name is not the registered seat. Connecture's talk runner answers it in about a second with a fresh chat completion:

- no session, so the next turn is "a new conversation"
- no bus client, so it cannot hand work to another seat
- no charter, so it role-plays Gemini, quotes encyclopedia text, and recites key paths

`Leo-Bot` is the registered chief of staff. It is a different process. Replies from the talk runner are not that seat.

## Replacement

Leo is a desk dispatcher with four parts and one rule: never speak for a seat that did not post.

```
desk message
    │
    ▼
 gates ── jeremy-yes ──► refuse, no bus write
    │
    ▼
 router ── seat + note ──► bus post to that seat
    │                 └──► remember the dispatch
    ▼
 session ── "did they respond?" ──► only a reply that seat actually posted
    │
    ▼
 Leo-Bot reply to the sender
```

| Piece | Job |
|---|---|
| `gates` | Stop send, spend, publish, post, bank, and wallet moves. Bus hand-offs are Leo's job and are not that gate. |
| `router` | Map handler words (`gemini`, `tubebot`, `grok build`, …) onto fleet seats. Extract the note. Do not invent one. |
| `session` | Remember the thread, the open dispatch, and a reply only after that seat posts. |
| `bus` | Read and post. Tests use an in-memory bus. A live loop needs `CONNECTURE_BUS_URL` and `CONNECTURE_BUS_TOKEN`. |

The service posts as `Leo-Bot`. It does not also answer as `leo` while the talk runner is still on, or the desk gets two replies. Cutover is: turn that runner off for `leo`, then set `LEO_FROM=leo` if the desk must keep typing that name.

## What this does not replace

The Windows Hermes profile and the Connecture source tree stay on LightBringer. This package is the desk behavior those processes were failing to perform. It does not hold house secrets, and it does not mark work Done without a bus id.
