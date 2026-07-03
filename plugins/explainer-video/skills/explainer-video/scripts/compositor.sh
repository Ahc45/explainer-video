#!/usr/bin/env bash
# Compositor agent: mux per-scene audio+video, then concat -> final.mp4
set -e
cd "$(dirname "$0")"

VID=$(dirname "$(ls -t media/videos/script/*/Scene1_Hook.mp4 | head -1)")
mkdir -p muxed
> concat.txt

# Read scene IDs in order from the timing contract
SCENES=$(python -c "import json;print(' '.join(s['id'] for s in json.load(open('timing_contract.json'))['scenes']))")

for s in $SCENES; do
  # Mux audio onto video; -shortest keeps them aligned (video padded == audio len)
  ffmpeg -y -loglevel error -i "$VID/$s.mp4" -i "audio/$s.mp3" \
    -c:v copy -c:a aac -shortest "muxed/$s.mp4"
  echo "file 'muxed/$s.mp4'" >> concat.txt
done

# Concatenate all muxed scenes. Re-encode for clean concat across streams.
ffmpeg -y -loglevel error -f concat -safe 0 -i concat.txt \
  -c:v libx264 -pix_fmt yuv420p -c:a aac final.mp4

echo "=== DONE ==="
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 final.mp4
ls -la final.mp4
