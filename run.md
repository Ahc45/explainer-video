# run.md — Install prerequisites for the explainer-video skill

> **For Claude Code users:** open this repo in Claude Code and say
> *"follow run.md to install the prerequisites"*. Claude will detect your OS,
> check what's already installed, install what's missing, and verify.
> You can also just run the commands below yourself.

The `explainer-video` skill installs the *pipeline files*, but rendering needs a
few runtime tools that a plugin can't install for you. This file covers them.

---

## Required (core pipeline)

| Tool       | Why                                                    |
|------------|--------------------------------------------------------|
| `python3`  | Runs the whole pipeline (voiceover, compositor)        |
| `ffmpeg`   | Muxes audio+video, normalizes codecs, burns captions   |
| `manim`    | The animation engine                                   |
| `edge-tts` | Free Microsoft neural TTS for the voiceover            |

### macOS

```bash
# System tools (Homebrew)
brew install python ffmpeg

# Python packages (in a project venv)
python3 -m venv .venv && source .venv/bin/activate
pip install manim edge-tts
```

### Linux (Debian/Ubuntu)

```bash
sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip ffmpeg
python3 -m venv .venv && source .venv/bin/activate
pip install manim edge-tts
```

### Windows

```powershell
winget install Python.Python.3.12
winget install Gyan.FFmpeg
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install manim edge-tts
```

> Manim has its own system dependencies (Cairo, Pango) that `pip install manim`
> usually pulls in as wheels. If a build fails, see
> https://docs.manim.community/en/stable/installation.html

---

## Optional stages

Only install these if you use the matching feature.

### SFX mixing (`sfx_mixer.py`)

```bash
pip install pydub          # ffmpeg (already required) provides the codecs
```

### Brand icons (`icon_fetch.mjs`) — tech-stack / system-design videos

Requires Node.js. Then, once per project:

```bash
npm i tech-stack-icons react react-dom @resvg/resvg-js
```

### Equations (`MathTex`)

Only if a video needs real math. Install a LaTeX distribution
(MacTeX / TeX Live). Most CS explainers use `Text()` boxes and can skip this.

---

## Verify

```bash
python3 --version
ffmpeg -version | head -1
manim --version
edge-tts --list-voices | head -1     # confirms TTS works (no API key needed)
```

If all four print without error, you're ready. Start a project and invoke the
skill with `/explainer-video` (or `/explainer-video:explainer-video` when
installed as a plugin).
