# Morning Barakah & The Proverb (የጧት በረከት እና ምሳሌው)

An AI-assisted 72-second heritage short film celebrating Ethiopian morning traditions, coffee ceremony rituals (*jebena buna*), and intergenerational wisdom. The story follows **Hajja Mariam**, a fictional elder, as she prepares morning coffee and shares a timeless Amharic proverb with her community.

---

## 📽️ Film Synopsis

- **Title**: *Morning Barakah & The Proverb*
- **Duration**: ~72 seconds (8 sequential shots)
- **Language**: Amharic (አማርኛ) voiceover with synchronized English subtitles
- **Protagonist**: Hajja Mariam (ሐጃ ማርያም) — fictional character
- **Key Theme**: Morning blessing (*barakah* / በረከት), patience, cultural hospitality, and community harmony
- **End Card**: Dedicated AI disclosure and ethical provenance statement

---

## 📂 Project Structure

```text
heritage-short/
├── .gitignore               # Ignores secrets (.env) and bulky build outputs
├── ARCHITECTURE.md          # End-to-end pipeline architecture and data flow
├── COSTS.md                 # Compute, token, and API cost estimations & tracking
├── DESIGN.md                # Narrative design, visual style guides, and audio palette
├── ETHICS.md                # Cultural authenticity, synthetic character ethics, AI disclosure
├── EXPERIMENTS.md           # Model iterations, prompt experiments, and AB evals
├── FAILURES.md              # Incident logs, generation artifacts, failure taxonomy
├── Makefile                 # Automation targets for build, test, and render
├── README.md                # Project documentation and quickstart
├── runs.jsonl               # Machine-readable pipeline execution logs
├── storyboard.json          # Master 8-shot storyboard definition
├── schema/                  # JSON validation schemas
│   └── storyboard.schema.json
├── pipeline/                # Production scripts and prompt compiler
│   └── prompt_compiler.py
└── outputs/                 # Rendered video, audio, and subtitle assets
```

---

## 🚀 Quickstart

### 1. Requirements
- Python 3.10+
- FFmpeg (for final composite and subtitle burning)
- GNU Make (or execute pipeline scripts directly)

### 2. Environment Setup
Copy the example environment file and configure model endpoints and provider keys (never commit secrets to version control):

```bash
cp .env.example .env
# Edit .env with your provider credentials
```

### 3. Validate Storyboard
Validate that `storyboard.json` matches the strict production schema:

```bash
make validate
```

### 4. Compile Prompts
Export prompt decks for visual generation and speech synthesis:

```bash
make generate-prompts
```

### 5. Run Render Pipeline
Run automated generation or assemble manually via FFmpeg:

```bash
make run-pipeline
```

---

## 🔒 Security Notice

**Never commit real API keys, bearer tokens, or service credentials into this repository.** All external credentials must be supplied via environment variables (`.env`) which are strictly ignored by `.gitignore`.

## Kaggle ACE-Step 1.5 `pip install -e .` Hang & GPU Queue Delay (2026-11-25)
- **Symptom:** Running `!pip install -e .` inside the `ACE-Step-1.5` Kaggle notebook cell hung for ~40 minutes. Restarting via `Restart & Clear Output` placed the session into a long GPU queue (`GPU T4 x2`, with `Internet on`), starting around position 972 and moving down through 866, 824, and 690.
- **Cause / Workaround:** Heavy ML/audio editable installs can stall on dependency resolution/building in Kaggle sessions, and dual-GPU (`GPU T4 x2`) queues are slow. Removed `!pip install -e .` from the code cell before execution so only `git clone` and `%cd` run first, while keeping the queued session active without resetting queue progress.
- **Status:** Logged; waiting for the Kaggle GPU session queue to finish while keeping `!pip install -e .` removed.