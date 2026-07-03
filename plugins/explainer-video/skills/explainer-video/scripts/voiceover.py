#!/usr/bin/env python3
"""Voiceover agent: edge-tts per-scene audio + measured durations -> timing_contract.json"""
import asyncio, json, subprocess, os
import edge_tts

# Run from project root, not scripts/
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == "scripts":
    ROOT = PROJECT
else:
    ROOT = os.path.dirname(os.path.abspath(__file__))
    
CONTRACT = os.path.join(ROOT, "timing_contract.json")
AUDIO_DIR = os.path.join(ROOT, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True).stdout.strip()
    return round(float(out), 3)

async def main():
    data = json.load(open(CONTRACT))
    # Default to Microsoft's newer CONVERSATIONAL voice, tuned for a little energy — it sounds
    # far less robotic than the old read-aloud voices (Guy/Aria). Override per-contract with
    # "voice"/"rate"/"pitch". Rate "+6%" + pitch "+12Hz" adds excitement without going chipmunk.
    voice = data.get("voice", "en-US-AndrewMultilingualNeural")
    rate = data.get("rate", "+6%")
    pitch = data.get("pitch", "+12Hz")
    for sc in data["scenes"]:
        mp3 = os.path.join(AUDIO_DIR, f"{sc['id']}.mp3")
        comm = edge_tts.Communicate(sc["narration"], voice, rate=rate, pitch=pitch)
        await comm.save(mp3)
        sc["duration"] = duration(mp3)
        print(f"{sc['id']}: {sc['duration']}s")
    data["total_duration"] = round(sum(s["duration"] for s in data["scenes"]), 2)
    json.dump(data, open(CONTRACT, "w"), indent=2)
    print(f"\nTOTAL: {data['total_duration']}s")

asyncio.run(main())
