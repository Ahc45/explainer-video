# explainer-video

A Claude Code plugin that turns a topic into a finished, voiced, synced
**portrait 9:16 (1080×1920)** explainer video — script → voiceover → optional
SFX → Manim animation → composited MP4. Multi-agent pipeline, free TTS
(edge-tts), no API keys.

## Install

```bash
# 1. Add this repo as a plugin marketplace
/plugin marketplace add YOUR_GITHUB_USER/explainer-video

# 2. Install the plugin
/plugin install explainer-video@explainer-video-marketplace
```

Then install the runtime prerequisites (Python, ffmpeg, manim, edge-tts) —
see **[run.md](./run.md)**. In Claude Code you can just say
*"follow run.md to install the prerequisites."*

Invoke with `/explainer-video`.

### Simpler alternative (no marketplace)

Clone the skill straight into your skills dir:

```bash
git clone https://github.com/YOUR_GITHUB_USER/explainer-video /tmp/ev \
  && cp -r /tmp/ev/plugins/explainer-video/skills/explainer-video ~/.claude/skills/
```

## What's inside

```
plugins/explainer-video/skills/explainer-video/
├── SKILL.md            # the pipeline instructions
├── scripts/            # voiceover, sfx_mixer, icon_fetch, compositor, run.sh
├── templates/          # theme + script scaffold
└── references/         # worked examples + sample timing contract
```

## Prerequisites

Core: `python3`, `ffmpeg`, `manim`, `edge-tts`.
Optional: `pydub` (SFX), Node + `tech-stack-icons` (brand icons), LaTeX (equations).
Full setup in **[run.md](./run.md)**.

## License

MIT
