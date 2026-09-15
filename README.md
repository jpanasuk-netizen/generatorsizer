# ⚡ Generator-Sizer Advisor (Local AI App)

The offline, privacy-first AI engineering advisor for HVAC techs, electrical contractors, and MEP firms.

## 🚀 Quick Start

### Windows
1. Double-click `Start-Advisor.bat`
2. Your browser opens **`http://127.0.0.1:8080/`** automatically

### macOS / Linux
```bash
chmod +x start_advisor.sh
./start_advisor.sh
```

### Or run via llama-server directly (fastest)
```bash
llama-server -m models/qwen25-3b-slm-advisor-q4km.gguf --port 8080 --host 0.0.0.0 -c 4096 -t 8
```

---

## 📦 What's Inside

- **`ui/`** — Dark engineering chat interface with example prompts
- **`api/server.py`** — Zero-dependency local server (serves UI + OpenAI-compatible API)
- **`models/`** — Quantized GGUF model files (`qwen25-3b-slm-advisor-q4km.gguf`, ~1.8 GB)
- **`examples/50_prompts.md`** — 50 field-tested prompt templates

---

## 🔌 API Integration

The local server provides a drop-in OpenAI-compatible endpoint:

```python
import openai

client = openai.OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="local"
)

response = client.chat.completions.create(
    model="slm-advisor",
    messages=[
        {"role": "user", "content": "What size wire for 100A subpanel at 200 feet?"}
    ]
)
print(response.choices[0].message.content)
```

---

## 🔒 100% Private & Offline

All calculations run on your hardware. No prompts or client job details ever leave your machine.

---

## 🔧 Technical

| Layer | Choice |
|---|---|
| Base model | Qwen2.5-3B (Apache-2.0) |
| Fine-tune | Unsloth LoRA, bf16, 4-bit quant |
| Export | GGUF (Q4_K_M) + safetensors + MLX recipe |
| Inference | llama.cpp / Ollama / TabbyAPI |
| Hardware lab | Private RTX 4070 workstation |
| License | MIT (personal/shop tiers) |

---

## 🎯 Tiers

| Tier | Price | Seats | Key extras |
|---|---|---|---|
| **Starter** | $99 one-time | 1 | Base + LoRA, GGUF/MLX recipes, README |
| **Pro** | $299 one-time | 5 (one site) | Pre-merged checkpoints, server config, 30 workflow pack, 12 mo quarterly refresh |
| **Firm** | $999 / firm / year | Unlimited | Commercial redistribution, SOC-friendly profile, custom LoRA slot, 8h priority support |

---

## 🧪 Trained on

- Residential load-calc prompts (Manual J)
- NEC ampacity tables (Chapter 9, Table 310.16)
- Generator kW selection & derating curves
- Voltage-drop calculations (Copper & Aluminum, single/three phase)
- HVAC tonnage → BTU → CFM conversions
- Transfer-switch amperage matching
- Fuel-economics (natural gas vs propane)
