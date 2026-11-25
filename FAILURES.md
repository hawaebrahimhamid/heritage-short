# Failure Taxonomy & Incident Postmortems: "Morning Barakah"

This document catalogs observed failure modes during generative synthesis, detailing root causes, detection protocols, and verified mitigations.

---

## ⚠️ Known Failure Modes & Mitigations

### 1. Cultural Object Hallucination (Coffee Pot Substitution)
- **Severity**: High (Cultural authenticity breach)
- **Symptom**: Model generates a Turkish *cezve*, Moroccan tea pot, or Italian espresso machine instead of a traditional Ethiopian spherical clay *jebena*.
- **Root Cause**: Overfitting in pre-trained image/video models to dominant Mediterranean or Western coffee brewing iconography.
- **Detection**: Automated visual detector flagged incorrect silhouette / manual review checklist.
- **Mitigation**:
  - Strictly enforce in prompt: `black spherical clay jebena, slender flared spout, woven straw ring base, authentic Ethiopian coffee pot`.
  - Negative prompt: `cezve, moka pot, metal kettle, porcelain teapot, espresso machine, mug with handle`.

### 2. Ge'ez / Amharic Script Distortion
- **Severity**: Medium
- **Symptom**: Background posters, decorative fabrics, or wall carvings attempt to generate pseudo-Ge'ez characters, producing garbled alien glyphs.
- **Root Cause**: Video generation models struggle with low-resource non-Latin typography.
- **Mitigation**:
  - Mandate neutral stone, plastered mud brick, or embroidered geometric *tibeb* motifs without written script in scene prompts.
  - Negative prompt: `text, watermark, pseudo-script, gibberish letters, neon signs, typography`.
  - Render all authentic Amharic text and subtitles exclusively via post-production graphics overlay (FFmpeg/ASS subtitle track).

### 3. Anatomical & Dexterity Anomalies (Fingers & Hands)
- **Severity**: Medium-High
- **Symptom**: Additional fingers or melting knuckles when Hajja Mariam handles the hot roasting pan (*menkeshkesha*) or pours the *jebena*.
- **Root Cause**: High complexity in small-joint physics and occlusion during object manipulation.
- **Mitigation**:
  - Use wider framing (medium-close up) rather than extreme macro on fingers.
  - Invert camera focus onto the steaming vessel or roasting pan with shallow depth of field (DoF).
  - Negative prompt: `extra fingers, fused fingers, deformed hands, missing thumb, mutated knuckles`.

### 4. Consonant De-ejection in Amharic Voice Synthesis
- **Severity**: High (Linguistic distortion)
- **Symptom**: The ejective consonant [ቀ] (*q*) in *"ቀስ በቀስ"* pronounced as a plain velar plosive [k] (*käs bäkäs*), altering the native timbre and meaning.
- **Root Cause**: Generic multilingual speech models trained primarily on Latin phoneme representations without ejective consonant conditioning.
- **Mitigation**:
  - Route Amharic audio through native Ge'ez phonetic alignment models.
  - Employ reference audio conditioning from a native elder speaker to preserve ejective bursts and vowel durations.

### 5. Identity Drift of Fictional Character (Hajja Mariam)
- **Severity**: High (Narrative cohesion failure)
- **Symptom**: Character appears 40 years old in Shot 2, then 70 years old with different eye color in Shot 4.
- **Root Cause**: Independent random sampling seeds in text-to-video generators.
- **Mitigation**:
  - Image-to-Video (I2V) workflow seeded from a single canonical multi-angle reference portrait sheet.
  - Fix seed parameters and reuse clothing style descriptors across all shot definitions in `storyboard.json`.

---

## 🛠️ Observed Pipeline & API Incidents

### 6. Deprecated Gemini Model ID (`HTTP 404` on `v1beta`)
- **Date**: 2026-11-25
- **Run IDs**: `smoke-20261125-073811` (FAILED) → `smoke-20261125-074318` (PASSED)
- **Severity**: Medium (Pipeline blocker during initial connectivity check)
- **Symptom**: `pipeline/smoke_test.py` failed with `HTTP 404: Model is not found: models/gemini-1.5-flash for api version v1beta`.
- **Root Cause**: Default configuration in `.env` referenced `gemini-1.5-flash`, which is no longer available on the active Google AI Studio `v1beta` endpoint.
- **Mitigation & Verification**:
  - Updated `GEMINI_MODEL=gemini-2.5-flash` in `.env` and `.env.example`.
  - Re-ran `python pipeline/smoke_test.py` (`smoke-20261125-074318`), confirming `Status : PASSED` (`Gemini 2.5 Flash`).

### 7. Editable Install Hang (~30 Min) & Kaggle `GPU T4 x2` Queue Delay
- **Date**: 2026-11-25 to 2026-11-26
- **Severity**: High (Workflow & schedule bottleneck)
- **Symptom**: Running `!pip install -e .` inside the `ACE-Step-1.5` Kaggle notebook cell hung for ~30 minutes. Restarting via `Restart & Clear Output` placed the session into a long `GPU T4 x2` queue (`Internet on`), starting around position `972` and moving down through `866`, `824`, `690`, `625`, and `299`.
- **Root Cause**: Heavy ML/audio editable installs can stall on dependency resolution/building in notebook sessions, and dual-GPU (`GPU T4 x2`) queues experience high contention.
- **Mitigation & Verification**:
  - Removed `!pip install -e .` from the cell before execution so only `git clone` and `%cd` ran first, and kept `outputs/character_sheet.png` / `outputs/hajja_mariam_portrait.jpg` (`seed: 42`) and `storyboard.json` (`72.0s`, 8 shots) prepared locally.
  - Adopted local FFmpeg (Ken Burns zoom/pan, music ducking, English subtitles, and Shot 8 end card) as the primary motion/assembly path so queue delays do not threaten the Nov 26, 2026 23:59 EAT deadline.

### 8. Kaggle `ace-step` Python 3.13 Version Incompatibility (2026-11-26)
- **Symptom:** Running `pip install -e .` inside `ACE-Step-1.5` on Kaggle failed with `ERROR: Package 'ace-step' requires a different Python: 3.13.16 not in '<3.13,>=3.11'`.
- **Cause / Decision:** The Kaggle runtime uses Python `3.13.16`, which does not satisfy `<3.13,>=3.11`. Decided not to spend more time troubleshooting Python versions on Kaggle and moved forward with local FFmpeg for motion (Ken Burns zoom/pan), audio mixing/ducking, subtitle burning, and video export to protect the Nov 26, 2026 23:59 EAT deadline.