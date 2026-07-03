#!/usr/bin/env python3
"""Compositor agent v3: bookends + per-scene audio mux + burned-in captions -> final.mp4
Every segment is NORMALIZED to identical codecs (h264 + 48kHz stereo aac) so concat is clean.
Order: SceneIntro (silent) -> content scenes (voiced) -> SceneOutro (silent).
Run from the project dir (expects timing_contract.json, templates/theme.json, audio/, media/).
"""
import json, os, subprocess, glob, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--audio-dir", default="audio", help="Audio directory (default: audio/)")
args = parser.parse_args()

# Run from project root
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == "scripts":
    os.chdir(PROJECT)
    
C = json.load(open("timing_contract.json"))
TH = json.load(open("templates/theme.json"))
CAP = TH["captions"]
AUDIO_DIR = args.audio_dir

def vdir():
    f = sorted(glob.glob("media/videos/script/*/Scene1_Hook.mp4"), key=os.path.getmtime)[-1]
    return os.path.dirname(f)
VID = vdir()

def dur(path):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True).stdout.strip()
    return float(out)

def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {' '.join(cmd)}")
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)

os.makedirs("muxed", exist_ok=True)
# PITFALL: silent anullsrc + real AAC tracks have mismatched channel layouts and corrupt
# the concat demuxer. Fix = force identical audio params on EVERY segment, then concat.
AUDIO_OPTS = ["-ar","48000","-ac","2","-c:a","aac","-b:a","192k"]
VIDEO_OPTS = ["-c:v","libx264","-pix_fmt","yuv420p","-r","60"]

clips = []

intro_v = f"{VID}/SceneIntro.mp4"; intro_d = dur(intro_v)
run(["ffmpeg","-y","-loglevel","error","-i",intro_v,
     "-f","lavfi","-t",str(intro_d),"-i","anullsrc=channel_layout=stereo:sample_rate=48000",
     *VIDEO_OPTS, *AUDIO_OPTS, "-shortest","muxed/00_intro.mp4"])
clips.append("muxed/00_intro.mp4")

t_cursor = intro_d
cap_events = []
for i, sc in enumerate(C["scenes"], 1):
    v = f"{VID}/{sc['id']}.mp4"; a = f"{AUDIO_DIR}/{sc['id']}.mp3"
    out = f"muxed/{i:02d}_{sc['id']}.mp4"
    run(["ffmpeg","-y","-loglevel","error","-i",v,"-i",a,
         *VIDEO_OPTS, *AUDIO_OPTS, "-shortest", out])
    d = dur(v)
    cap_events.append((t_cursor, t_cursor + d, sc["narration"]))
    t_cursor += d
    clips.append(out)

outro_v = f"{VID}/SceneOutro.mp4"; outro_d = dur(outro_v)
run(["ffmpeg","-y","-loglevel","error","-i",outro_v,
     "-f","lavfi","-t",str(outro_d),"-i","anullsrc=channel_layout=stereo:sample_rate=48000",
     *VIDEO_OPTS, *AUDIO_OPTS, "-shortest","muxed/99_outro.mp4"])
clips.append("muxed/99_outro.mp4")

def ass_time(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h}:{m:02d}:{s:05.2f}"

def wrap(text, width=22):
    words=text.split(); lines=[]; cur=""
    for w in words:
        if len(cur)+len(w)+1<=width: cur=(cur+" "+w).strip()
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return "\\N".join(lines)

sub_arg = []
if CAP.get("enabled"):
    pw, ph = 1080, 1920
    # BorderStyle 3 + BackColour = opaque band behind text -> always readable over animation.
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {pw}
PlayResY: {ph}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Cap,{TH['font']},{CAP['font_size']*3},{CAP['primary_color']},{CAP['outline_color']},{CAP.get('back_color','&H66000000')},{CAP['bold']},{CAP.get('border_style',3)},{CAP['outline']},0,2,60,60,{CAP['margin_v']}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for st, en, txt in cap_events:
        ass += f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Cap,,0,0,0,,{wrap(txt)}\n"
    open("captions.ass","w").write(ass)
    sub_arg = ["-vf", "ass=captions.ass"]

with open("concat.txt","w") as f:
    for path in clips:
        f.write(f"file '{path}'\n")

if sub_arg:
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","concat.txt",
         *sub_arg, "-c:v","libx264","-pix_fmt","yuv420p","-c:a","copy","final.mp4"])
else:
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","concat.txt",
         "-c","copy","final.mp4"])

total = dur("final.mp4")
print(f"=== DONE === final.mp4  {total:.2f}s  (intro {intro_d:.1f} + content {t_cursor-intro_d:.1f} + outro {outro_d:.1f})")
