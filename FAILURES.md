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

### 9. Amharic TTS Native Prosody & Tone Limitation (Peer Review Finding)
- **Date**: 2026-11-26
- **Severity**: Medium (Aesthetic & cultural nuance)
- **Symptom**: During peer review, reviewer Haylemichael Tsega Gebrekidan noted that while the Amharic narration is fully intelligible and grammatically accurate, the neural TTS voice tone does not sound completely natural or colloquial to native speakers, lacking the lived vocal timbre and elder warmth of a real grandmother.
- **Root Cause**: Commercial multilingual TTS engines (Gemini Preview TTS / neural models) generalize across broad phonetic datasets and lack colloquial Ethiopian elder prosody and micro-intonations without extensive fine-tuning.
- **Mitigation & Phase 3 Decision**:
  - Burned-in clear, high-contrast English subtitles (`outputs/subtitles.srt`) to ensure complete comprehension across international and non-native audiences.
  - Documented as an identified aesthetic limitation for Phase 3 submission; future iterations will record authenticated native elder voice actors.

### 10. FFmpeg `drawtext` Filter Colon & Path Escaping on Windows
- **Severity**: Medium (CLI build failure)
- **Symptom**: Generating the Shot 8 AI disclosure card failed with filter parse errors: `[Parsed_drawtext_0 @ ...] Option not found: '/Windows/Fonts/arial.ttf'`.
- **Root Cause**: FFmpeg treats colons (`:`) as delimiter flags between filter arguments. On Windows, absolute file paths containing drive letters (e.g., `C:\Windows\...`) break the argument parser.
- **Mitigation**:
  - Double-escape colons in paths (`C\\:/Windows/Fonts/arial.ttf` or forward-slash normalized paths).
  - Externalized multi-line text into a dedicated text file (`outputs/end_card_text.txt`) passed via `textfile='outputs/end_card_text.txt'` rather than inline CLI strings, completely avoiding shell quote/newline conflicts.

### 11. `video_list.txt` Lexicographical Sorting & Demuxer Ordering
- **Severity**: High (Narrative sequence corruption)
- **Symptom**: Automated directory globbing could place `clip_08_end_card.mp4` or unordered clips out of sequence during the FFmpeg concat pass.
- **Root Cause**: Default filesystem sort orders or unordered directory iterators can concatenate clips non-chronologically.
- **Mitigation**:
  - Enforced an explicit, strictly ordered manifest in `outputs/video_list.txt` with zero-padded shot indices (`clip_01.mp4` through `clip_08_end_card.mp4`).
  - Added verification in build workflows to assert all 8 shots appear in exact order (1 through 8) before executing `ffmpeg -f concat -safe 0 -i outputs/video_list.txt`.

### 12. Local FFmpeg `zoompan` Filter Buffer & Subtitle Burn-in Assembly
- **Severity**: Medium (Frame drop & filter graph syntax error)
- **Symptom**: Applying Ken Burns pan-and-zoom directly to raw high-resolution still images (`shot_01.png` - `shot_07.png`) caused stuttering, aspect ratio distortion, or memory spikes, while subtitle filter paths failed on Windows backslashes.
- **Root Cause**: FFmpeg `zoompan` operates on internal pixel buffers and requires explicit frame rates (`fps=24`) and uniform output resolutions (`s=1920x1080`). Additionally, the `subtitles` filter requires forward slashes or escaped backslashes.
- **Mitigation**:
  - Standardized the zoompan filter chain: `zoompan=z='min(zoom+0.0015,1.25)':d=216:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080,fps=24`.
  - Implemented single-shot caching: only missing clips are rendered; existing clips are preserved.
  - Subtitles burned reliably using forward slashes (`subtitles=outputs/subtitles.srt`) for the 16:9 master, and cropped/padded via `scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2` for the 9:16 vertical version.

### 9. Amharic TTS Native Prosody & Tone Limitation (Peer Review Finding)
- **Date**: 2026-11-26
- **Severity**: Medium (Aesthetic & cultural nuance)
- **Symptom**: During peer review, reviewer Haylemichael Tsega Gebrekidan noted that while the Amharic narration is fully intelligible and grammatically accurate, the neural TTS voice tone does not sound completely natural or colloquial to native speakers, lacking the lived vocal timbre and elder warmth of a real grandmother.
- **Root Cause**: Commercial multilingual TTS engines (Gemini Preview TTS / neural models) generalize across broad phonetic datasets and lack colloquial Ethiopian elder prosody and micro-intonations without extensive fine-tuning.
- **Mitigation & Phase 3 Decision**:
  - Burned-in clear, high-contrast English subtitles (`outputs/subtitles.srt`) to ensure complete comprehension across international and non-native audiences.
  - Documented as an identified aesthetic limitation for Phase 3 submission; future iterations will record authenticated native elder voice actors.

### 10. FFmpeg `drawtext` Filter Colon & Path Escaping on Windows
- **Severity**: Medium (CLI build failure)
- **Symptom**: Generating the Shot 8 AI disclosure card failed with filter parse errors: `[Parsed_drawtext_0 @ ...] Option not found: '/Windows/Fonts/arial.ttf'`.
- **Root Cause**: FFmpeg treats colons (`:`) as delimiter flags between filter arguments. On Windows, absolute file paths containing drive letters (e.g., `C:\Windows\...`) break the argument parser.
- **Mitigation**:
  - Double-escape colons in paths (`C\\:/Windows/Fonts/arial.ttf` or forward-slash normalized paths).
  - Externalized multi-line text into a dedicated text file (`outputs/end_card_text.txt`) passed via `textfile='outputs/end_card_text.txt'` rather than inline CLI strings, completely avoiding shell quote/newline conflicts.

### 11. `video_list.txt` Lexicographical Sorting & Demuxer Ordering
- **Severity**: High (Narrative sequence corruption)
- **Symptom**: Automated directory globbing could place `clip_08_end_card.mp4` or unordered clips out of sequence during the FFmpeg concat pass.
- **Root Cause**: Default filesystem sort orders or unordered directory iterators can concatenate clips non-chronologically.
- **Mitigation**:
  - Enforced an explicit, strictly ordered manifest in `outputs/video_list.txt` with zero-padded shot indices (`clip_01.mp4` through `clip_08_end_card.mp4`).
  - Added verification in build workflows to assert all 8 shots appear in exact order (1 through 8) before executing `ffmpeg -f concat -safe 0 -i outputs/video_list.txt`.

### 12. Local FFmpeg `zoompan` Filter Buffer & Subtitle Burn-in Assembly
- **Severity**: Medium (Frame drop & filter graph syntax error)
- **Symptom**: Applying Ken Burns pan-and-zoom directly to raw high-resolution still images (`shot_01.png` - `shot_07.png`) caused stuttering, aspect ratio distortion, or memory spikes, while subtitle filter paths failed on Windows backslashes.
- **Root Cause**: FFmpeg `zoompan` operates on internal pixel buffers and requires explicit frame rates (`fps=24`) and uniform output resolutions (`s=1920x1080`). Additionally, the `subtitles` filter requires forward slashes or escaped backslashes.
- **Mitigation**:
  - Standardized the zoompan filter chain: `zoompan=z='min(zoom+0.0015,1.25)':d=216:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080,fps=24`.
  - Implemented single-shot caching: only missing clips are rendered; existing clips are preserved.
  - Subtitles burned reliably using forward slashes (`subtitles=outputs/subtitles.srt`) for the 16:9 master, and cropped/padded via `scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2` for the 9:16 vertical version.
