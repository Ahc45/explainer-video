#!/usr/bin/env python3
"""
SFX Mixer - Layer sound effects onto scene audio based on timing contract.

Usage:
    python sfx_mixer.py timing_contract.json audio/ sfx/ audio_mixed/

Requires: pydub (pip install pydub), ffmpeg on PATH
"""

import json
import sys
from pathlib import Path

try:
    from pydub import AudioSegment
except ImportError:
    print("ERROR: pydub not installed. Run: pip install pydub")
    sys.exit(1)


def load_audio(path: Path) -> AudioSegment:
    """Load audio file, auto-detecting format."""
    suffix = path.suffix.lower()
    if suffix == ".mp3":
        return AudioSegment.from_mp3(path)
    elif suffix == ".wav":
        return AudioSegment.from_wav(path)
    elif suffix in (".m4a", ".aac"):
        return AudioSegment.from_file(path, format="m4a")
    else:
        return AudioSegment.from_file(path)


def mix_sfx_into_scene(
    voice_path: Path,
    sfx_dir: Path,
    sfx_entries: list[dict],
    output_path: Path,
    sfx_volume_reduction_db: float = -15.0,
) -> None:
    """
    Overlay SFX onto voice audio for a single scene.

    Args:
        voice_path: Path to the scene's voice-only audio
        sfx_dir: Directory containing SFX files
        sfx_entries: List of {"sound": "whoosh.mp3", "offset": 0.5}
        output_path: Where to write the mixed audio
        sfx_volume_reduction_db: How much quieter SFX should be vs voice
    """
    # Load voice as base
    mixed = load_audio(voice_path)

    for entry in sfx_entries:
        sfx_file = sfx_dir / entry["sound"]
        offset_ms = int(entry["offset"] * 1000)

        if not sfx_file.exists():
            print(f"  WARNING: SFX not found: {sfx_file}, skipping")
            continue

        sfx = load_audio(sfx_file)
        # Reduce SFX volume so voice remains clear
        sfx = sfx + sfx_volume_reduction_db

        # Overlay at offset
        # If offset is negative or beyond audio length, pydub handles gracefully
        mixed = mixed.overlay(sfx, position=offset_ms)

    # Export as MP3 (same format as input for consistency)
    mixed.export(output_path, format="mp3", bitrate="192k")
    print(f"  Mixed: {output_path.name}")


def main():
    if len(sys.argv) < 5:
        print("Usage: python sfx_mixer.py <timing_contract.json> <audio_dir> <sfx_dir> <output_dir>")
        print("\nExample:")
        print("  python sfx_mixer.py timing_contract.json audio/ sfx/ audio_mixed/")
        sys.exit(1)

    contract_path = Path(sys.argv[1])
    audio_dir = Path(sys.argv[2])
    sfx_dir = Path(sys.argv[3])
    output_dir = Path(sys.argv[4])

    # Validate paths
    if not contract_path.exists():
        print(f"ERROR: timing contract not found: {contract_path}")
        sys.exit(1)
    if not audio_dir.exists():
        print(f"ERROR: audio directory not found: {audio_dir}")
        sys.exit(1)
    if not sfx_dir.exists():
        print(f"WARNING: SFX directory not found: {sfx_dir}")
        print("  Create it and add SFX files, or scenes will have voice only.")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load timing contract
    with open(contract_path) as f:
        contract = json.load(f)

    scenes = contract.get("scenes", [])
    if not scenes:
        print("ERROR: No scenes in timing contract")
        sys.exit(1)

    print(f"Mixing SFX for {len(scenes)} scenes...")
    print(f"  Audio source: {audio_dir}")
    print(f"  SFX source: {sfx_dir}")
    print(f"  Output: {output_dir}")
    print()

    for scene in scenes:
        scene_id = scene["id"]
        sfx_entries = scene.get("sfx", [])

        # Find voice audio (try common patterns)
        voice_path = None
        for pattern in [f"{scene_id}.mp3", f"{scene_id}.wav", f"{scene_id}.m4a"]:
            candidate = audio_dir / pattern
            if candidate.exists():
                voice_path = candidate
                break

        if voice_path is None:
            print(f"  SKIP: No audio found for {scene_id}")
            continue

        output_path = output_dir / f"{scene_id}.mp3"

        if not sfx_entries:
            # No SFX for this scene - just copy the voice audio
            print(f"  {scene_id}: no SFX, copying voice only")
            import shutil
            shutil.copy(voice_path, output_path)
        else:
            print(f"  {scene_id}: layering {len(sfx_entries)} SFX")
            mix_sfx_into_scene(voice_path, sfx_dir, sfx_entries, output_path)

    print("\nDone! Use audio_mixed/ as input to compositor.")


if __name__ == "__main__":
    main()
