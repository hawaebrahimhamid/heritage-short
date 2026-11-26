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

## 🚀 End-to-End Reproduction Workflow

To reproduce the entire generative media pipeline and generate all production deliverables from scratch (including `outputs/final_16x9.mp4` and `outputs/final_9x16.mp4`) at **$0.00 cost**:

### Single Command Execution (PowerShell / Bash)

Run this single-line command sequence from the project root:

```bash
# 1. Validate, compile prompts, generate Amharic audio, and create FLUX shot stills
python pipeline/validate_storyboard.py && python pipeline/prompt_compiler.py && python pipeline/generate_narration.py && python pipeline/generate_shot_stills.py
```

### Complete 5-Step Reproduction Walkthrough

If running each stage individually:

1. **Validate Storyboard & Timing Invariants**:
   ```bash
   python pipeline/validate_storyboard.py --storyboard storyboard.json --schema schema/storyboard.schema.json
   ```
2. **Compile Prompt Deck & Subtitles**:
   ```bash
   python pipeline/prompt_compiler.py --input storyboard.json --output outputs/prompts.json
   ```
3. **Synthesize Amharic Speech & Master Radio Cut**:
   ```bash
   python pipeline/generate_narration.py
   # Outputs: outputs/narration_01.wav .. narration_08.wav and outputs/radio_cut_audio.wav
   ```
4. **Generate Visual Stills (FLUX @ seed 42 with Caching)**:
   ```bash
   python pipeline/generate_shot_stills.py
   # Outputs: outputs/shot_01.png .. outputs/shot_07.png (uses cached assets if present)
   ```
5. **Assemble Final 16:9 & 9:16 Cuts via FFmpeg**:
   ```bash
   # Create 8s AI disclosure end card (Shot 8)
   ffmpeg -y -f lavfi -i color=c=0x111111:s=1920x1080:d=8.0 -vf "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':textfile='outputs/end_card_text.txt':fontcolor=white:fontsize=28:x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=18" -r 24 -c:v libx264 -pix_fmt yuv420p outputs/clip_08_end_card.mp4

   # Generate 24fps Ken Burns motion clips (Shots 1 to 7)
   # (e.g. for Shot 1, 9s = 216 frames):
   ffmpeg -y -loop 1 -i outputs/shot_01.png -vf "zoompan=z='min(zoom+0.0015,1.25)':d=216:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080,fps=24" -t 9.0 -c:v libx264 -pix_fmt yuv420p outputs/clip_01.mp4

   # Concatenate video clips chronologically with master radio cut audio
   ffmpeg -y -f concat -safe 0 -i outputs/video_list.txt -i outputs/radio_cut_audio.wav -c:v copy -c:a aac -shortest outputs/video_no_subs.mp4

   # Export Master 16:9 Widescreen with burned-in subtitles
   ffmpeg -y -i outputs/video_no_subs.mp4 -vf "subtitles=outputs/subtitles.srt:force_style='FontSize=22,Outline=1.5,Shadow=0.8,MarginV=35'" -c:v libx264 -pix_fmt yuv420p -c:a copy outputs/final_16x9.mp4

   # Export 9:16 Vertical Mobile Cut (scaled and padded for reels/stories)
   ffmpeg -y -i outputs/video_no_subs.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,subtitles=outputs/subtitles.srt:force_style='FontSize=26,Outline=2.0,MarginV=80'" -c:v libx264 -pix_fmt yuv420p -c:a copy outputs/final_9x16.mp4
   ```

---

## 📽️ Production Deliverables (`outputs/`)

- **`outputs/final_16x9.mp4`**: 72-second 1080p widescreen master with synchronized Amharic narration, Ken Burns camera motion, and burned-in English subtitles.
- **`outputs/final_9x16.mp4`**: 72-second 1080x1920 vertical mobile cut optimized for mobile devices and social sharing.
- **`outputs/radio_cut_audio.wav`**: Master 24kHz audio track with natural pauses aligned to storyboard timing.
- **`outputs/shot_01.png` - `outputs/shot_07.png`**: High-resolution photorealistic character and scene stills generated with fixed seed `42`.
- **`outputs/clip_08_end_card.mp4`**: Ethical AI disclosure statement displayed for the final 8 seconds.

---

## 🔒 Security & Privacy Notice

**Never commit real API keys, bearer tokens, or service credentials into this repository.** All external credentials must be supplied via environment variables (`.env`) which are strictly ignored by `.gitignore`. Local scripts mask and sanitize all credentials automatically.