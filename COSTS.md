# Production Cost Analysis & Financial Model: "Morning Barakah"

This document provides budgeting estimates, per-shot expenditure models, and tracking standards across multimodal generative pipelines.

---

## 💰 Unit Economics & Model Cost Breakdown

| Component | Service / Model Category | Billing Metric | Estimated Unit Rate | Per-Run Consumption | Estimated Cost per Run |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Video Synthesis** | Video Gen API (T2V / I2V) | Per second generated | ~$0.15 / sec | 72 seconds | $10.80 |
| **Video Re-rolls (QA)** | Video Gen API (2x retries) | Per second generated | ~$0.15 / sec | ~40 seconds | $6.00 |
| **Voice Synthesis** | Amharic Neural TTS / Clone | Per 1k characters | ~$0.015 / 1k chars | ~450 chars | $0.02 |
| **Foley & Music Score** | Generative Audio API | Per audio track | ~$0.05 / generation | 4 tracks | $0.20 |
| **LLM Orchestration** | Prompt Compiler & QA | Per 1M input/output tokens | ~$1.25 / 1M tokens | ~15k tokens | $0.02 |
| **Storage & Egress** | Cloud Object Storage | Per GB / month | ~$0.02 / GB | ~1.5 GB | $0.03 |
| **Compositing / FFmpeg** | CPU / GPU Compute | Compute instance time | ~$0.005 / min | ~6 mins | $0.03 |
| **Total Production Run**| — | — | — | — | **~$17.10 USD** |

---

## 📊 Per-Shot Budget Allocation (72s Master)

| Shot ID | Scene Description | Target Duration | Expected Re-rolls | Baseline Video Cost | Contingency / Re-roll | Subtotal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Shot 1** | Sunrise Highland Courtyard | 9.0s | 1.0x | $1.35 | $0.45 | $1.80 |
| **Shot 2** | Hajja Mariam Lighting Stove | 9.0s | 1.8x | $1.35 | $1.08 | $2.43 |
| **Shot 3** | Roasting Beans Macro | 9.0s | 1.2x | $1.35 | $0.54 | $1.89 |
| **Shot 4** | Wafting Aromatic Smoke | 9.0s | 2.0x | $1.35 | $1.35 | $2.70 |
| **Shot 5** | Clay Jebena Infusion | 9.0s | 1.0x | $1.35 | $0.45 | $1.80 |
| **Shot 6** | High Arc Jebena Pour into Sini | 9.0s | 2.5x | $1.35 | $1.68 | $3.03 |
| **Shot 7** | Hajja Mariam Delivering Proverb | 10.0s | 2.0x | $1.50 | $1.50 | $3.00 |
| **Shot 8** | AI Disclosure End Card | 8.0s | 0.0x (Code-rendered) | $0.00 | $0.00 | $0.00 |
| **Audio** | Amharic VO + Ambience + Mix | 72.0s | 1.5x | $0.25 | $0.20 | $0.45 |
| **Total** | Full Master | **72.0s** | — | **$8.50** | **$8.60** | **$17.10** |

---

## ⚡ Cost Optimization Strategies

1. **Static Pre-Rendering for Shot 8**: The final AI disclosure end card does not require generative video credits. Render programmatically via FFmpeg drawing filters or SVG-to-video for $0.00 cost.
2. **Low-Resolution Fast-Pass Previews**: Generate 480p preview passes at 1/4th token cost before rendering high-bitrate 1080p masters.
3. **Reference Image Freezing**: By using high-fidelity static image anchors for Hajja Mariam in I2V mode, re-roll frequency drops from an average of 4.2 attempts to 1.8 attempts per shot.
4. **Local FFmpeg Post-Processing**: Audio mixing, color LUT application, and subtitle burning run on local CPU/GPU hardware at zero API charge.
