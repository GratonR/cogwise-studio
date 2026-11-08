#!/usr/bin/env python3
"""Render an edited episode from its stems and an edit spec (the "liste de retouches" written by the Control Room).

    python3 tools/montage.py render --stems outbox/DATE_slug/stems --spec spec.json --out slug_edit.mp4 [--dry-run]

The spec is non-destructive: the stems never change, the spec can be re-applied or reset at any time.
All times in the spec are seconds on the OUTPUT timeline (t = 0 at the trim start), except `trim` (source time).

spec = {
  "trim":   [start, end] | null,
  "tracks": {"<id>": {"gain": dB, "mute": bool}},
  "video":  {"rotate": deg, "zoom": 1..3, "cx": 0..1, "cy": 0..1, "flip": bool,
             "brightness": -1..1, "contrast": 0..2, "saturation": 0..3},
  "fade":   {"in": s, "out": s},
  "blur":   [{"a": s, "b": s, "amount": px at 1080 wide}],
  "texts":  [{"a": s, "b": s, "text": str, "x": 0..1, "y": 0..1 (centre of the block), "size": px at 1080 wide,
              "color": "#rrggbb", "font": "Poppins"|"VT323", "box": bool, "box_color": "#rrggbb", "box_opacity": 0..1}],
  "loudnorm": true   (−14 LUFS, like the original builds)
}
The Control Room preview reproduces the same maths (CSS transforms + Web Audio), so what you see is what renders.
"""
import argparse, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FONTS = {
    "Poppins": ["/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", os.path.join(HERE, "fonts", "Poppins-Bold.ttf")],
    "VT323": [os.path.join(REPO, "studio", "this-melody-is", "engine", "vt323.ttf")],
}

def font_file(name):
    for p in FONTS.get(name, []) + FONTS["Poppins"]:
        if os.path.exists(p): return p
    sys.exit("no font file found for " + name)

def num(x, d):
    try: return float(x)
    except (TypeError, ValueError): return d

def col(c, alpha=1.0):
    c = (c or "#ffffff").lstrip("#")
    if len(c) != 6: c = "ffffff"
    return f"0x{c}@{max(0.0, min(1.0, alpha)):.3f}"

def build(stems_dir, spec, out, tmp):
    meta = json.load(open(os.path.join(stems_dir, "stems.json")))
    W, H = meta["size"]; dur = float(meta["duration"])
    a, b = (spec.get("trim") or [0, dur])[:2]
    a = max(0.0, num(a, 0)); b = min(dur, num(b, dur))
    if b - a < 0.5: sys.exit("trim too short")
    D = b - a
    v = spec.get("video") or {}
    chain = [f"trim=start={a:.3f}:end={b:.3f}", "setpts=PTS-STARTPTS"]
    rot = num(v.get("rotate"), 0)
    if abs(rot) > 0.01:
        chain.append(f"rotate={rot:.3f}*PI/180:ow=iw:oh=ih:c=black")
    z = max(1.0, num(v.get("zoom"), 1))
    if z > 1.001:
        cx = min(1, max(0, num(v.get("cx"), .5))); cy = min(1, max(0, num(v.get("cy"), .5)))
        chain.append(f"scale=iw*{z:.4f}:ih*{z:.4f}:flags=bicubic")
        chain.append(f"crop={W}:{H}:(iw-{W})*{cx:.4f}:(ih-{H})*{cy:.4f}")
    if v.get("flip"): chain.append("hflip")
    br, ct, sa = num(v.get("brightness"), 0), num(v.get("contrast"), 1), num(v.get("saturation"), 1)
    if abs(br) > 1e-3 or abs(ct - 1) > 1e-3 or abs(sa - 1) > 1e-3:
        chain.append(f"eq=brightness={br:.3f}:contrast={ct:.3f}:saturation={sa:.3f}")
    for bl in spec.get("blur") or []:
        r = max(1, int(round(num(bl.get("amount"), 10))))
        chain.append(f"boxblur=luma_radius={r}:luma_power=2:chroma_radius={max(1, r//2)}:enable='between(t,{num(bl.get('a'),0):.3f},{num(bl.get('b'),D):.3f})'")
    for i, t in enumerate(spec.get("texts") or []):
        txt = str(t.get("text") or "").strip()
        if not txt: continue
        tf = os.path.join(tmp, f"text{i}.txt"); open(tf, "w").write(txt)
        size = int(round(num(t.get("size"), 72)))
        x, y = num(t.get("x"), .5), num(t.get("y"), .2)
        opts = [f"fontfile='{font_file(t.get('font') or 'Poppins')}'", f"textfile='{tf}'", f"fontsize={size}",
                f"fontcolor={col(t.get('color'))}", "text_align=C", f"line_spacing={int(size*0.18)}",
                f"x={W}*{x:.4f}-text_w/2", f"y={H}*{y:.4f}-text_h/2",
                f"enable='between(t,{num(t.get('a'),0):.3f},{num(t.get('b'),D):.3f})'"]
        if t.get("box"):
            opts += ["box=1", f"boxcolor={col(t.get('box_color') or '#000000', num(t.get('box_opacity'), .55))}",
                     f"boxborderw={int(size*0.35)}"]
        chain.append("drawtext=" + ":".join(opts))
    f = spec.get("fade") or {}
    fi, fo = num(f.get("in"), 0), num(f.get("out"), 0)
    if fi > 0: chain.append(f"fade=t=in:st=0:d={fi:.3f}")
    if fo > 0: chain.append(f"fade=t=out:st={max(0, D-fo):.3f}:d={fo:.3f}")
    chain.append("format=yuv420p")
    graph = ["[0:v]" + ",".join(chain) + "[v]"]

    inputs = ["-i", os.path.join(stems_dir, meta.get("video", "video.mp4"))]
    tracks = spec.get("tracks") or {}
    labels = []
    for tr in meta["tracks"]:
        st = tracks.get(tr["id"]) or {}
        if st.get("mute"): continue
        k = len(inputs) // 2
        inputs += ["-i", os.path.join(stems_dir, tr["file"])]
        g = num(st.get("gain"), 0)
        graph.append(f"[{k}:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,aresample=48000,volume={g:.2f}dB[a{k}]")
        labels.append(f"[a{k}]")
    if labels:
        mix = "".join(labels) + (f"amix=inputs={len(labels)}:normalize=0:duration=longest" if len(labels) > 1 else "anull")
        post = [f"atrim=0:{D:.3f}"]
        if fi > 0: post.append(f"afade=t=in:st=0:d={fi:.3f}")
        if fo > 0: post.append(f"afade=t=out:st={max(0, D-fo):.3f}:d={fo:.3f}")
        if spec.get("loudnorm", True): post.append("loudnorm=I=-14:TP=-1.5:LRA=11")
        post.append("aresample=48000")
        graph.append(mix + "," + ",".join(post) + "[a]")
    else:
        graph.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{D:.3f}[a]")
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(graph),
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", "-t", f"{D:.3f}", out]
    return cmd, D

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("--stems", required=True); r.add_argument("--spec", required=True); r.add_argument("--out", required=True)
    r.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    with tempfile.TemporaryDirectory() as tmp:
        cmd, D = build(a.stems, spec, a.out, tmp)
        if a.dry_run:
            print(" ".join(cmd)); return
        subprocess.run(cmd, check=True)
    print(json.dumps({"out": a.out, "duration": round(D, 2), "bytes": os.path.getsize(a.out)}))

if __name__ == "__main__":
    main()
