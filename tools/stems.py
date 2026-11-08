#!/usr/bin/env python3
"""Export an episode as separate stems + light previews, for the Control Room "Montage" tab.

    python3 tools/stems.py make --video SILENT_OR_FINAL.mp4 [--track voice=voice.mp3 --track sfx=sfx.wav ...] \
        --out outbox/DATE_slug/stems [--meta slug_meta.json] [--label voice="Voix off"]

If no --track is given, the audio of --video becomes a single "mix" track (works for any old episode).

Writes in --out:
  video.mp4            full-res video, no audio (stream copy)          -> used by tools/montage.py
  <id>.m4a             one AAC 256k file per track                     -> used by tools/montage.py
  preview/proxy.mp4    540x960, ~1 Mbit/s, keyframe every 0.5 s, no audio  -> uploaded to the app
  preview/<id>.webm    Opus 64k per track                               -> uploaded to the app
  stems.json           {duration, size, fps, tracks:[{id, label, file, preview}], beats?}
"""
import argparse, json, os, subprocess, sys

LABELS = {"voice": "Voix off", "sfx": "Bruitages", "music": "Musique", "mix": "Son (mixé)"}

def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path],
                         check=True, capture_output=True, text=True).stdout
    return json.loads(out)

def make(a):
    os.makedirs(os.path.join(a.out, "preview"), exist_ok=True)
    info = probe(a.video)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    dur = float(info["format"]["duration"])
    tracks = dict(t.split("=", 1) for t in a.track)
    labels = dict(l.split("=", 1) for l in a.label)
    if not tracks:
        if not has_audio: sys.exit("no --track and the video has no audio")
        tracks = {"mix": a.video}

    ff("-i", a.video, "-map", "0:v:0", "-c", "copy", "-an", "-movflags", "+faststart", os.path.join(a.out, "video.mp4"))
    # proxy: small, seek-friendly (short GOP) so the scrubber in the browser is responsive
    ff("-i", a.video, "-map", "0:v:0", "-an", "-vf", "scale=540:960:flags=bicubic",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-maxrate", "1200k", "-bufsize", "2400k",
       "-g", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", os.path.join(a.out, "preview", "proxy.mp4"))
    out_tracks = []
    for tid, src in tracks.items():
        sel = ["-map", "0:a:0"] if src == a.video else []
        ff("-i", src, *sel, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", os.path.join(a.out, f"{tid}.m4a"))
        ff("-i", src, *sel, "-vn", "-ac", "2", "-ar", "48000", "-c:a", "libopus", "-b:a", "64k", os.path.join(a.out, "preview", f"{tid}.webm"))
        out_tracks.append({"id": tid, "label": labels.get(tid, LABELS.get(tid, tid)), "file": f"{tid}.m4a", "preview": f"preview/{tid}.webm"})
    doc = {"duration": round(dur, 3), "size": [int(v["width"]), int(v["height"])], "fps": round(int(num) / int(den), 3),
           "video": "video.mp4", "proxy": "preview/proxy.mp4", "tracks": out_tracks}
    if a.meta and os.path.exists(a.meta):
        m = json.load(open(a.meta))
        for k in ("slug", "title", "beat_starts"):
            if k in m: doc[k] = m[k]
    json.dump(doc, open(os.path.join(a.out, "stems.json"), "w"), indent=2, ensure_ascii=False)
    sizes = {f: os.path.getsize(os.path.join(a.out, "preview", f)) for f in os.listdir(os.path.join(a.out, "preview"))}
    print(json.dumps({"stems": a.out, "duration": doc["duration"], "tracks": [t["id"] for t in out_tracks],
                      "preview_bytes": sizes}, ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("--video", required=True); m.add_argument("--out", required=True)
    m.add_argument("--track", action="append", default=[], help="id=path (voice, sfx, music, …)")
    m.add_argument("--label", action="append", default=[], help="id=Label shown in the app")
    m.add_argument("--meta")
    a = ap.parse_args()
    if a.cmd == "make": make(a)

if __name__ == "__main__":
    main()
