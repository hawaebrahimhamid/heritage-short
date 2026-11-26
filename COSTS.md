# Production Cost Analysis & Financial Model: "Morning Barakah"

This document provides financial accounting, cost tracking, and unit economics across the multimodal generative pipeline for *"Morning Barakah & The Proverb"*.

---

## 💰 Actual Production Expenditure: $0.00 USD

By strategically utilizing developer free tiers, optimized preview models, and local post-processing compute, the actual out-of-pocket cost for producing the complete 72-second master film (`outputs/final_16x9.mp4` and `outputs/final_9x16.mp4`) was **$0.00 USD**.

### Actual Spend Ledger (Phase 1 to Phase 3)

| Component | Provider / Tool | Model / Tier | Consumed Units | Rate | Actual Spend |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Visual Still Generation** | Cloudflare Workers AI | `@cf/black-forest-labs/flux-1-schnell` (Free Tier) | 8 shot stills + portrait | 10k neurons/day free tier | **$0.00** |
| **Amharic Voiceover (TTS)** | Google Gemini API | `gemini-2.5-flash-preview-tts` (Free/Preview Tier) | 8 narration clips (~74s audio) | Free rate limits | **$0.00** |
| **Prompt Compilation & QA** | Google Gemini API | `gemini-2.5-flash` (Free Tier) | ~15k prompt/compiler tokens | Free tier allocation | **$0.00** |
| **Ken Burns Pan/Zoom Motion** | Local FFmpeg Engine | Local CPU/GPU compute | 7 shot clips (24 fps, 1080p) | Local execution | **$0.00** |
| **AI Disclosure End Card** | Local FFmpeg Engine | Static canvas (`drawtext` filter) | Shot 8 (8.0s) | Local execution | **$0.00** |
| **Audio Concat & Radio Cut** | Python `wave` Standard Lib | Standard library 24kHz PCM | 74.27s master radio cut | Local execution | **$0.00** |
| **Subtitle Burn-in (16:9 & 9:16)**| Local FFmpeg Engine | Subtitle filter + scale/pad | Master 1080p + 9:16 vertical | Local execution | **$0.00** |
| **Storage & Telemetry Logging**| Local Filesystem & Git | SSD / `runs.jsonl` audit log | ~120 MB total artifacts | Local storage | **$0.00** |
| **Total Production Spend** | — | — | — | — | **$0.00 USD** |

---

## 📊 Estimated Commercial Value vs. Zero-Cost Reality

Had this project been rendered entirely through commercial paid-tier APIs without local compute optimization, estimated commercial pricing would have been:

| Production Category | Hypothetical Commercial Service | Billing Rate | Estimated Commercial Cost | Actual Project Cost |
| :--- | :--- | :--- | :--- | :--- |
| Video Synthesis (72s) | Commercial Video Gen API (Runway/Luma) | ~$0.15 / sec | $10.80 | **$0.00** (Local Ken Burns on FLUX stills) |
| Video Re-rolls & QA | Commercial Video Gen API | ~$0.15 / sec | $6.00 | **$0.00** (Fixed seed 42 single-pass) |
| Voice Synthesis (Amharic) | Commercial Voice Clone API | ~$0.015 / 1k chars | $0.02 | **$0.00** (Gemini Preview TTS Free Tier) |
| LLM Orchestration & Prompt QA | Commercial LLM API | ~$1.25 / 1M tokens | $0.02 | **$0.00** (Gemini 2.5 Flash Free Tier) |
| Video Compositing & Subtitles | Cloud Render Farm (AWS/Modal) | ~$0.05 / min | $0.26 | **$0.00** (Local FFmpeg assembly) |
| **Total Equivalent Value** | — | — | **~$17.10 USD** | **$0.00 USD (100% Free Tiers / Local)** |

---

## ⚡ Cost Optimization Strategies Implemented

1. **Local FFmpeg Ken Burns Assembly**: Instead of paying cloud video credits ($0.10–$0.20 per second), still images were generated once via Cloudflare FLUX Free Tier and animated locally with smooth dynamic pan/zoom (`zoompan`) filters at zero cost.
2. **Fixed Seed Caching (`seed: 42`)**: Single-shot caching ensures that only missing or modified shots are re-generated. Re-running the pipeline checks `outputs/` first, incurring 0 redundant API calls.
3. **Pure Python Audio Assembly**: Concat and timeline synchronization of `outputs/radio_cut_audio.wav` uses Python's built-in `wave` module, requiring zero paid external audio APIs.
4. **Programmatic AI Disclosure End Card**: Shot 8 is rendered directly in code via FFmpeg drawtext for $0.00, rather than spending generative video tokens.
5. **Dual Aspect Ratio Local Export**: Both horizontal 16:9 (`final_16x9.mp4`) and mobile vertical 9:16 (`final_9x16.mp4`) masters are generated locally in a single FFmpeg pass at $0.00.
