---
name: explainer-video
description: "Automated explainer-video pipeline: topic -> script -> voiceover -> optional SFX -> Manim animation -> synced portrait MP4. Multi-agent, free TTS."
version: 2.0.0
platforms: [macos, linux, windows]
---

# Automated Explainer-Video Pipeline

## When to use

User wants an automated motion-design explainer video for ANY teachable concept
(machine learning, vector databases, arrays, sorting, networking, etc.) with synced
narration. Input: a topic + target length. Output: a finished, voiced, synced
**portrait 9:16 (1080x1920)** MP4.

This is a MULTI-AGENT pipeline. Treat each stage as a role. The key to quality is
the **timing contract** — a shared JSON that keeps voice and visuals locked in sync.

## Architecture (7 roles)

```
Director (you)  -> owns timing_contract.json (the glue)
  Script Writer -> narration broken into scenes + visual_spec (+ optional sfx/icons) per scene
  Voiceover     -> edge-tts audio + MEASURED duration per scene  (writes durations back)
  SFX Mixer     -> (optional) layers sound effects onto voice per scene
  Icon Fetcher  -> (optional) tech-stack-icons → transparent PNGs in assets/icons/
  Animator      -> Manim scenes, each PADDED to its narration duration
  Compositor    -> ffmpeg mux audio+video per scene, normalize, concat -> final.mp4
```

Dependency chain (NOT fully parallel): Script -> Voiceover -> (SFX) -> Animator -> Compositor.
The Icon Fetcher is independent of Voiceover; run it any time before the Animator.
The animator MUST consume voiceover durations or visuals won't match narration (#1 failure mode).
Scenes WITHIN the animator stage can render in parallel.

## Project layout

The pipeline runs from a **project directory** (copy `scripts/` and `templates/` into it).
Scripts self-locate: run them from either the project root or from `scripts/` — they
`chdir` to the project root automatically.

```
project/
├── scripts/
│   ├── voiceover.py        ← edge-tts → audio/ + measured durations
│   ├── sfx_mixer.py         ← (optional) layer SFX → audio_mixed/
│   ├── icon_fetch.mjs       ← (optional) tech-stack-icons → assets/icons/*.png
│   ├── compositor_v3.py     ← normalize + mux + optional captions → final.mp4
│   └── run.sh               ← one-shot: voiceover → render → composite → final.mp4
├── templates/
│   ├── theme.json           ← brand config (palette, font, intro/outro, watermark, captions)
│   ├── theme.py             ← Manim intro/outro cards + watermark() + icon()/icon_node()
│   └── script_template.py   ← copy to script.py; scene-vocabulary scaffold
├── assets/
│   ├── watermark.jpg|png     ← (optional) image watermark; falls back to text brand
│   └── icons/*.png           ← (optional) fetched brand icons for ImageMobject
├── script.py                ← Manim scenes (generated per topic; imports theme from templates/)
├── timing_contract.json     ← the sync map (source of truth)
├── audio/                    ← per-scene voice MP3s (written by voiceover.py)
├── audio_mixed/             ← per-scene voice+SFX MP3s (written by sfx_mixer.py)
├── media/videos/script/…/    ← Manim render output (Scene*.mp4)
├── muxed/                    ← per-scene normalized audio+video
└── final.mp4                ← output
```

## Prerequisites

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install manim edge-tts        # ffmpeg must already be on PATH
pip install pydub                  # only if using the SFX stage
npm i tech-stack-icons react react-dom @resvg/resvg-js   # only if using image ICONS
```
- **Skip LaTeX** unless equations are needed — use `Text()` boxes/arrows for CS topics.
  Install MacTeX/texlive only if `MathTex` is required.
- **Free TTS**: edge-tts (Microsoft neural voices, no key/subscription). Prefer the newer
  **conversational/multilingual** voices — they sound far less robotic than the old read-aloud
  ones. Default: **`en-US-AndrewMultilingualNeural`** (warm, natural) at `rate="+6%"`,
  `pitch="+12Hz"` for a little energy. Other good picks: `en-US-BrianMultilingualNeural` (casual M),
  `en-US-AvaMultilingualNeural` (smooth F), `en-US-EmmaMultilingualNeural` (animated F). Avoid the
  flat `en-US-GuyNeural`/`en-US-AriaNeural` for hype/tech content. Tune via `rate`/`pitch` in the
  contract; pitch adds excitement (don't exceed ~+15Hz or it sounds chipmunky).

## The timing contract (timing_contract.json)

The single source of truth. Script Writer creates it; Voiceover adds `duration`;
Animator reads durations. See `references/timing_contract.sample.json` for a real,
complete example. Shape:
```json
{
  "title": "What is Machine Learning?",
  "series": "30 Days of AI", "day": 1,
  "voice": "en-US-AndrewMultilingualNeural", "rate": "+6%", "pitch": "+12Hz",
  "palette": {"bg":"#0A0A0A","primary":"#00F5FF","secondary":"#FF00FF","accent":"#39FF14","dim":"#555555","text":"#FFFFFF"},
  "icons": ["nextjs", "nginx", "redis", "postgresql"],
  "scenes": [
    {
      "id": "Scene1_Hook",
      "narration": "...",
      "visual_spec": "...",
      "sfx": [{"sound": "whoosh.mp3", "offset": 0.0}, {"sound": "pop.mp3", "offset": 0.8}],
      "icons": ["nextjs", "redis"],
      "duration": 11.376
    }
  ],
  "total_duration": 42.1
}
```
Rules:
- Scene `id` must be a valid Python class name (used directly as the Manim Scene class + CLI arg).
- `sfx` is optional per scene; `offset` is seconds from the scene's start.
- `icons` is optional (top-level list and/or per-scene); names come from the tech-stack-icons
  catalog (`node scripts/icon_fetch.mjs --list` prints all 690+). The Icon Fetcher gathers every
  name it finds and writes `assets/icons/<name>.png`.
- Voiceover fills in `duration` and `total_duration` — never hand-author those.

## Steps

### 1. Script Writer
Write `timing_contract.json` with 4-6 scenes. Each scene: a `narration` line (1-2 sentences),
a `visual_spec` describing what animates, and optional `sfx` cues. End with a payoff line.
Keep ~150 words/min of speech for the target length.

**The hook is the whole ballgame.** On Reels/Shorts, ~80% of viewers leave in the first 3s, so
Scene1's FIRST sentence + FIRST frame decide whether the video is watched. Do not open with a
slow build or a bland restatement of the title ("Let's learn about X", "A neural network is…").
Write the opening line as a deliberate **hook pattern** — see the library below — then make the
first 1-2s of the visual *show the payoff*, not ramp up to it.

Rules for a strong hook:
- **Front-load the payoff frame.** Second 1 should already show the impressive thing (the result,
  the number, the finished diagram flashing), then explain. Don't animate in slowly from empty.
- **Be specific.** Numbers, constraints, named tech beat vague claims. "Find the driver closest to
  you in under 2 seconds" >> "how ride-hailing works". Specificity signals it's real and
  self-selects the audience who'll engage.
- **One idea, said with tension.** A question, a gap, a bold claim — something the viewer needs
  resolved. The rest of the video is the resolution.
- **Don't bury it behind branding.** The intro card is a ~2s brand flash; the hook must land right
  after (or the card itself can carry the hook line). Never spend 4s on a logo before the hook.

#### Hook pattern library (pick one, make it specific)
- **Question / knowledge-gap** — "What's actually happening when you type `git push`?"
- **Curiosity gap / the real reason** — "This is why your Postgres query takes 3 seconds."
- **Contrarian / you're-doing-it-wrong** — "Stop using useEffect for this." / "You don't need Redux."
- **Number / listicle** — "3 VS Code shortcuts that feel illegal."
- **Callout / POV** — "POV: you just found out about this after 5 years."
- **Result / proof / build-in-public** — "How I cut my API costs 90% with a local LLM on my M1."
- **Demo cold open** — open mid-action, thing already running: "Watch this build a video from one prompt."
- **Bold claim / shock** — "You'll never write boilerplate again."
- **Problem-agitate** — "Debugging CORS at 2am again? Let's fix it forever."

For a concept explainer, curiosity-gap and question hooks fit best; for anything you built,
result/demo hooks are strongest (least fakeable). Example rewrite: instead of
"How Ride-Hailing Apps Work" → *"Under two seconds. That's how fast a ride-hailing app finds the
driver closest to you, out of a million on the road. Here's how."* (number + curiosity gap, specific).

### 2. Voiceover (scripts/voiceover.py)
Generates per-scene MP3 into `audio/` with edge-tts (default voice `en-US-AndrewMultilingualNeural`,
`rate="+6%"`, `pitch="+12Hz"` — override via `voice`/`rate`/`pitch` in the contract), measures each
with ffprobe, writes `duration` + `total_duration` back into the contract.
```bash
python scripts/voiceover.py
```
Confirm total_duration ~= target.

### 3. SFX Mixer (scripts/sfx_mixer.py) — optional
If scenes carry `sfx` cues, layer them onto the voice (SFX ducked ~15 dB under voice) into
`audio_mixed/`. Scenes with no `sfx` are copied through unchanged.
```bash
python scripts/sfx_mixer.py timing_contract.json audio/ sfx/ audio_mixed/
```
Then hand `audio_mixed/` to the compositor via `--audio-dir` (step 5). Requires `pydub`.

### 3b. Icon Fetcher (scripts/icon_fetch.mjs) — optional
For tech-stack / system-design videos, render real brand icons instead of text boxes.
Add the names to the contract (top-level `icons` and/or per-scene `icons`), then:
```bash
npm i tech-stack-icons react react-dom @resvg/resvg-js   # once per project
node scripts/icon_fetch.mjs                # reads the contract, writes assets/icons/*.png
node scripts/icon_fetch.mjs --list         # print the 690+ available names to search
```
Icons are 512px transparent PNGs, `variant: "dark"` by default (light-on-dark, pop on #0A0A0A).
In `script.py` use `icon("redis", width=1.4)` (an `ImageMobject`) or `icon_node("redis","cache")`
(icon + caption `Group`). Missing names fall back to a labeled box, so a typo won't crash the render.

### 4. Animator (script.py)
Copy `templates/script_template.py` → `script.py` and swap in your scenes; it ships the
`fill()`/`box()` helpers, portrait config, bookends, and a scene-vocabulary recipe block
(hook pile, vertical flow, indexed lookup, clustering, two-column compare, payoff).
One `Scene` subclass per scene id. Import theme from `templates/` and set portrait config:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "templates"))
from theme import BG, PRIMARY, SECONDARY, ACCENT, DIM, TXT, FONT, watermark, IntroCard, OutroCard
config.frame_width = 9; config.frame_height = 16
config.pixel_width = 1080; config.pixel_height = 1920
```
CRITICAL pattern — pad each scene to its audio length:
```python
def pad(scene, target, used):
    remain = target - used
    if remain > 0.05: scene.wait(remain)
```
Track `used` by summing every `run_time` + `wait`. End each scene with
`self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)` (count it in `used`).
Add `self.add(watermark())` at the top of every content scene. Define
`SceneIntro(IntroCard)` and `SceneOutro(OutroCard)` as SILENT bookends.
Follow manim-video skill standards: monospace font (Menlo), neon-tech palette, breathing room.
Render draft: `manim -ql script.py SceneIntro Scene1_Hook … SceneOutro`

### 5. Compositor (scripts/compositor_v3.py)
The production compositor. Normalizes EVERY segment to identical codecs
(`h264 + 48kHz stereo aac`), muxes per-scene audio, optionally burns captions, then concats.
Order: `SceneIntro` (silent) -> content scenes (voiced) -> `SceneOutro` (silent).
```bash
python scripts/compositor_v3.py                       # uses audio/
python scripts/compositor_v3.py --audio-dir audio_mixed   # uses SFX-mixed audio
```
Reads `templates/theme.json` for caption styling. Emits `muxed/`, `concat.txt`, `captions.ass`
(if enabled), and `final.mp4`. Prints ffmpeg stderr on failure.

> A legacy shell compositor (`scripts/compositor.sh`) does the simple mux+concat without
> normalization/captions/bookends. Prefer `compositor_v3.py`; keep the shell version only for
> quick smoke tests.

### 6. Verify
Extract frames with `ffmpeg -ss <t> -i final.mp4 -frames:v 1 f.png` and inspect with vision
for clutter/overlap/readability BEFORE declaring done. Check final duration matches the contract.
Grab the frame AFTER a scene's animations settle; for a cheap check, 1–2 frames of the riskiest
scenes is usually enough (each vision read costs tokens — don't inspect all of them by reflex).

### One-shot runner (scripts/run.sh)
Once `timing_contract.json` and `script.py` exist, chain steps 2, 4, 5 in a single call
(run from the activated project venv):
```bash
scripts/run.sh                        # voice-only, draft (-ql)
QUALITY=-qh scripts/run.sh            # final-quality render
SFX=1 scripts/run.sh                  # run sfx_mixer, composite from audio_mixed/
scripts/run.sh --audio-dir audio_mixed   # use pre-mixed audio
```
It derives the scene list from the contract, renders `SceneIntro <ids> SceneOutro`, then
composites. Env overrides: `PY`, `MANIM`, `QUALITY`.

## Pitfalls

- **Sync drift**: if you don't pad scenes to audio length, video and voice desync. Always pad.
- **edge-tts voice/prosody**: the old read-aloud voices (Guy/Aria) sound robotic — use a
  conversational voice (default `en-US-AndrewMultilingualNeural`). A slight `rate="+6%"` +
  `pitch="+12Hz"` adds energy; too much pitch (>~+15Hz) sounds chipmunky, and heavy negative rate
  drags. Style/express-as tags are NOT supported by the free endpoint — prosody is voice + rate +
  pitch only.
- **Audio concat corruption**: mixing silent `anullsrc` bookends with real AAC scene audio
  breaks the concat demuxer ("Rematrix… not enough information", channel-element errors).
  FIX: normalize EVERY segment to identical params (`-ar 48000 -ac 2 -c:a aac`) before concat —
  this is exactly what `compositor_v3.py` does. Plain `-c copy` concat fails across mixed encodes.
- **No LaTeX installed** -> `MathTex` crashes. Use `Text()` unless you installed texlive/MacTeX.
- **Scene id must be a Python identifier** (no spaces) — it's used as the class name and CLI arg.
- **Proportional fonts break kerning** in Manim Pango — use monospace (Menlo) for all `Text()`.
- Render `-ql` (480p15) for iteration; only `-qh` for the final deliverable. `compositor_v3.py`
  auto-detects the newest render dir via `media/videos/script/*/Scene1_Hook.mp4`.
- **QA frame timing**: `Write()`/`Create()` animate text in progressively. Grab the verification
  frame AFTER the scene's run_time + a beat, or you'll chase phantom "clipping" bugs.
- **Portrait re-layout**: landscape scenes spread content on X; in 9:16 that runs off-frame.
  Restack vertically (Y offsets) and bump font sizes — phones are viewed up close.
- **Captions over animation**: use ASS `BorderStyle: 3` + a semi-transparent `BackColour`
  (e.g. `&H66000000`) so the caption band stays readable; anchor bottom-center (Alignment 2)
  with a modest `MarginV` to sit in the lower third above platform UI.
- **SFX volume**: SFX are ducked ~15 dB under voice by default; louder cues will bury narration.
- **Buried hook = dead video**: a long silent brand IntroCard before the hook tanks retention.
  Keep `SceneIntro` short (the shipped card lands in ~2s) and make Scene1's first 1-2s show the
  payoff. If a topic needs it, put the hook line *on* the intro card instead of a plain title.
  See "The hook is the whole ballgame" in Step 1 — the opening is the highest-leverage edit.
- **Icons are `ImageMobject`, not `VMobject`**: they can't go in a `VGroup` and don't accept
  `Write()`/`Create()`/`set_color()`/`Indicate(scale_factor=…)`. Use `FadeIn`, `.animate.move_to`,
  `.animate.scale`, and put them in a `Group` (what `icon_node()` returns). To "highlight" an icon,
  animate a `SurroundingRectangle`/`Circle` around it rather than recoloring the icon.
- **Fetch icons before rendering**: `script.py` reads PNGs from `assets/icons/`. Run
  `node scripts/icon_fetch.mjs` first; otherwise `icon()` silently falls back to labeled boxes.
- **Icon variant vs background**: use `variant: "dark"` (default) on the dark theme — those glyphs
  carry light outlines. `"light"` icons disappear on #0A0A0A. Flip only if you switch to a light theme.

## Theming (reusable brand look)

A **theme** decouples brand style from content so every video looks consistent. Two files in
`templates/`:

- **theme.json** — palette, font, font_sizes, intro (kicker), outro (cta/tagline),
  watermark (opacity/corner), captions (ASS style). Swap this file -> whole video restyles.
  Shipped preset: **KnowWat** neon-tech brand (captions off by default).
- **theme.py** — loads theme.json; exposes color/font constants + `watermark()`,
  `IntroCard`, `OutroCard` Manim components.

Wire-up:
- `script.py` imports from `templates/theme.py` (no hardcoded colors). Add
  `self.add(watermark())` at the top of every content scene.
- Define `SceneIntro(IntroCard)` / `SceneOutro(OutroCard)` calling
  `super().construct(title_text=C["title"], duration=…)`. These are SILENT bookends.
- Render order: `SceneIntro <content scenes> SceneOutro`.

### Watermark
`watermark()` uses an image if `assets/watermark.jpg` (or `.png`) exists, scaled to ~1.2 units
wide for portrait; otherwise it renders the `brand` text. Controlled by `watermark.enabled`,
`.opacity`, `.corner` in theme.json.

### Captions (burned-in for Reels)
Set `captions.enabled: true` in theme.json. `compositor_v3.py` generates an ASS file from the
timing contract (offsetting caption start times by the intro duration) and burns it with
`-vf ass=captions.ass` on the final concat (requires re-encode).

## References
- `references/timing_contract.sample.json` — a real, complete contract (ML explainer, with SFX).
- `references/hash_table_script.md` + `references/hash_table_manim.py` — a worked example
  (script → Manim) for a different topic.

## Scaling to production
- Parallelize the animator (one subagent per scene) for long videos.
- For 1-min+ videos, raise to 8-12 scenes; keep each scene 4-10s.
- Swap edge-tts for a premium TTS only if explicitly requested.

## Related skills
- `manim-video` — the animation engine, full reference for mobjects/animations/design.
