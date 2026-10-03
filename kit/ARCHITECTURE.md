# The kit

Hermes is one connector. A note for Gemini, Grokbot, Grok, FreeBuff, Muse, or muse.ai is not a Hermes gateway call.

| Lane | Seat | Where a note goes |
|---|---|---|
| hermes | `hermes-bot` and the Hermes profiles (Cynthia, Eve, Annie, …) | `POST 127.0.0.1:8642/v1/chat/completions` |
| gemini | `gemini-spark` | The Gemini lane. Not the Hermes gateway. |
| grokbot | `grokbot`, `grok-build`, `grok-swarm` | The Grokbot lane. |
| grok | `grok` | The chat keeps the note. Usage is gone, so nothing is called until that lane is opened. |
| freebuff | `freebuff` | The FreeBuff lane. FreeBuff owns Connecture. |
| muse | `muse` | The local Muse gateway on `:8788`. |
| muse.ai | `muse-ai` | The Meta Muse connector. It is not the local video gateway, and it is not `muse.ai/api`. |

MiMo stays on the file bus. Jeremy is not answered. The desk name `leo` stays with the desk dispatcher.

A lane that is down posts `did not answer`. It does not borrow another lane's client and it does not invent that seat's words.
