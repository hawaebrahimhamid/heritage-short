# Technical & Creative Report: Morning Barakah & The Proverb (የጠዋት በረካ እና ምሳሌው)

## 1. Executive Summary & Creative Concept
**Morning Barakah & The Proverb** (*የጠዋት በረካ እና ምሳሌው*) is a 72-second AI-assisted heritage short film structured across 8 sequential shots (`0–72s`). Inspired by Ethiopian morning traditions and coffee ceremony culture (*jebena buna*), the story centers on **Hajja Mariam**, a fictional 68-year-old elder (`seed: 42`), who roasts coffee calmly and shares the Amharic proverb *"ቀስ በቀስ እንቁላል በእግሩ ይሄዳል"* (*"Step by step, an egg learns to walk"*).

The narrative frames patience, morning blessing (*barakah* / በረከት), communal warmth, and steady effort as an antidote to modern rush. Rather than prioritizing flashy spectacle, the project prioritizes narrative clarity, cultural respect, deterministic reproducibility, transparent AI disclosure, and disciplined engineering logs.

## 2. Phase-by-Phase Execution Methodology

### Phase 1: Storyboard, Ethics & Radio Cut First
- **Single Fictional Character & Focused Setting:** To avoid privacy or consent risks and simplify visual continuity, the story uses one fictional character (**Hajja Mariam**, `seed: 42`) and a cohesive domestic morning setting rather than real people's faces or voices.
- **Schema & Storyboard Validation:** Shot structure, timing (`0–9s`, `9–18s`, `18–27s`, `27–36s`, `36–45s`, `45–54s`, `54–64s`, `64–72s`), Amharic narration lines, and English subtitle lines were defined in `storyboard.json` and validated against `schema/storyboard.schema.json`.
- **Radio Cut Before Visuals:** Amharic narration lines were synthesized and sequenced into `outputs/radio_cut_audio.wav` before locking final visual renders, allowing pacing and timing to be tested early.

### Phase 2: Character Consistency, Visuals, Audio & Caching
- **Character Sheet & Fixed Seed:** A dedicated character reference (`outputs/character_sheet.png`) and fixed `seed: 42` were used across shot prompts so **Hajja Mariam** remains visually consistent across shots.
- **Motion & Media Assembly:** Shot stills (`outputs/shot_01.png`–`outputs/shot_07.png`) were animated at `24 fps` using FFmpeg `zoompan` (`d=216`, `-t 9` for 9-second shots) alongside the Shot 8 disclosure end card (`outputs/clip_08_end_card.mp4`, `64–72s`), concatenated via `outputs/video_list.txt` into `outputs/video_no_subs.mp4`, paired with `outputs/radio_cut_audio.wav`, and exported with burned-in English subtitles (`outputs/subtitles.srt`) into both:
  - `outputs/final_16x9.mp4` (`1920x1080` widescreen master)
  - `outputs/final_9x16.mp4` (`1080x1920` vertical mobile cut)
- **Caching & Single-Shot Rerun Design:** Pipeline execution and run metadata are tracked in `runs.jsonl` and documented in `EXPERIMENTS.md` and `ARCHITECTURE.md`. Checking for existing outputs/hashes allows individual shots or stages to be updated without needlessly regenerating the entire 8-shot film, saving time and API quota.

### Phase 3: Peer Review, Finalization & Submission Readiness
- **Peer Feedback Integration:** Prior to final submission, two peers reviewed the film:
  - **Aisha Hussein:** Expressed genuine appreciation for the short film.
  - **Haylemichael Tsega Gebrekidan:** Highlighted three concrete observations: (1) the connection between coffee roasting and the proverb landed well, (2) the burned-in English subtitles were easy to read while the Amharic TTS tone felt less natural to native speakers, and (3) the final AI disclosure end card should ideally be text-based.
- **Pragmatic Scope Decision:** Because the submission deadline approached (`November 26, 2026, 23:59 EAT`) and non-technical responsibilities required time management, the full video was not re-rendered solely for minor prosody polish. Instead, both feedback items were transparently recorded in `DESIGN.md` and `FAILURES.md` as documented trade-offs and future improvements.

## 3. Failure Analysis, Ethics & Cost Discipline
- **Failure Taxonomy (`FAILURES.md`):** Documented native Amharic TTS prosody/tone limitations alongside practical implementation hurdles encountered during assembly—such as `video_list.txt` ordering prior to FFmpeg concatenation, filter/font/path escaping in FFmpeg, and avoiding long GPU queue delays by using deterministic local FFmpeg motion (`zoompan`).
- **Ethics & AI Provenance (`ETHICS.md`):** Confirmed that **Hajja Mariam** (`seed: 42`) is 100% fictional with no real human faces, identities, or voices used. Explicit AI disclosure is included both on the Shot 8 end card (`64–72s`) and in public social distribution.
- **Cost Tracking (`COSTS.md`):** Total expenditure across the project is **$0.00**, utilizing free tiers and local open-source/CLI tooling (`FFmpeg`, `Python`, `Git`). Secrets remain isolated in `.env` (excluded via `.gitignore`).

## 4. Final Deliverables & Verification
- **GitHub Repository:** `https://github.com/hawaebrahimhamid/heritage-short.git` (containing code, `storyboard.json`, `schema/`, `runs.jsonl`, `README.md`, `DESIGN.md`, `ARCHITECTURE.md`, `EXPERIMENTS.md`, `FAILURES.md`, `COSTS.md`, `ETHICS.md`, and `REPORT.md`)
- **Video Exports:** `outputs/final_16x9.mp4` and `outputs/final_9x16.mp4`
- **Public Post:** Published on LinkedIn with AI and fictional character disclosure
- **Technical Walkthrough:** ≤5-minute screen recording demonstrating the repository, documentation, single-shot caching/rerun behavior, and final outputs.