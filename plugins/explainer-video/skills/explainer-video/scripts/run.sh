#!/usr/bin/env bash
# One-shot pipeline: voiceover -> Manim render -> composite -> final.mp4
# Run from anywhere; it cd's to the project root (the parent of scripts/).
# Expects: timing_contract.json, script.py, scripts/, templates/ in the project root.
#
# Usage:
#   scripts/run.sh                        # voice-only, draft quality
#   QUALITY=-qh scripts/run.sh            # final quality render
#   scripts/run.sh --audio-dir audio_mixed   # use SFX-mixed audio
#   SFX=1 scripts/run.sh                  # run sfx_mixer first, then composite from audio_mixed/
#
# Env overrides: PY=python, MANIM=manim, QUALITY=-ql
set -euo pipefail
cd "$(dirname "$0")/.."   # project root

PY="${PY:-python}"
MANIM="${MANIM:-manim}"
QUALITY="${QUALITY:--ql}"

AUDIO_DIR=""
if [ "${1:-}" = "--audio-dir" ]; then AUDIO_DIR="--audio-dir $2"; fi

echo "== [1/4] voiceover =="
"$PY" scripts/voiceover.py

if [ "${SFX:-0}" = "1" ]; then
  echo "== [1.5] sfx mixer =="
  "$PY" scripts/sfx_mixer.py timing_contract.json audio/ sfx/ audio_mixed/
  AUDIO_DIR="--audio-dir audio_mixed"
fi

echo "== [2/4] render ($QUALITY) =="
SCENES=$("$PY" -c "import json;print(' '.join(s['id'] for s in json.load(open('timing_contract.json'))['scenes']))")
# shellcheck disable=SC2086
"$MANIM" $QUALITY script.py SceneIntro $SCENES SceneOutro

echo "== [3/4] composite =="
# shellcheck disable=SC2086
"$PY" scripts/compositor_v3.py $AUDIO_DIR

echo "== [4/4] done -> final.mp4 =="
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 final.mp4
