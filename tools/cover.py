"""Profile-grid cover for a short: picks a frame, writes the title on it, and puts it as the very FIRST frame of the video.

Why: Instagram, TikTok and Facebook use the first frame as the default cover of a Reel/short, and the profile grid shows
that cover (center-cropped to 3:4). BeepMelody videos fade in from an empty screen, so every cover was a blank tile
and nobody could find an episode on the profile (Guillaume, 14 Nov). One frame = 1/30 s: invisible when watching.

Usage:
  python3 tools/cover.py make  --video X.mp4 --title "4 babies are born every second" --out cover.jpg [--at 0.7]
  python3 tools/cover.py apply --video X.mp4 --title "..." [--at 0.7] [--font F.ttf]     # rewrites X.mp4 in place, keeps X.cover.jpg
--at = position of the background frame (fraction of the duration if <= 1, else seconds). Default 0.7 (data well under way).
"""
import argparse, json, os, subprocess, tempfile, textwrap, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "studio", "this-melody-is", "engine", "vt323.ttf")


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", video],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out); s = j["streams"][0]; n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d), float(j["format"]["duration"])


def make(video, title, out, at=0.7, font=FONT):
    w, h, fps, dur = probe(video)
    t = at * dur if at <= 1 else at
    tmp = out + ".frame.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB"); os.remove(tmp)
    d = ImageDraw.Draw(im, "RGBA")
    # the grid shows the centre 3:4 of a 9:16 video -> keep the title inside the middle band
    size = int(w * 0.105); f = ImageFont.truetype(font, size)
    lines = textwrap.wrap(title.upper(), width=16)[:5]
    lh = int(size * 1.02); block = lh * len(lines)
    y0 = int(h * 0.5 - block / 2); pad = int(w * 0.045)
    d.rectangle([0, y0 - pad, w, y0 + block + pad], fill=(10, 12, 20, 205))
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f); x = (w - tw) / 2; y = y0 + i * lh
        d.text((x + 4, y + 4), ln, font=f, fill=(0, 0, 0, 255))
        d.text((x, y), ln, font=f, fill=(255, 214, 64, 255) if i == 0 else (255, 255, 255, 255))
    im.save(out, quality=92)
    return out, (w, h, fps)


def apply(video, title, at=0.7, font=FONT):
    cover = os.path.splitext(video)[0] + ".cover.jpg"
    _, (w, h, fps) = make(video, title, cover, at, font)
    tmpd = tempfile.mkdtemp(prefix="cover-")
    try:
        out = os.path.join(tmpd, "out.mp4")
        # 1 frame of cover (+ matching silence), then the original video; one re-encode, same size/fps
        subprocess.run(["ffmpeg", "-v", "error", "-y",
                        "-loop", "1", "-framerate", f"{fps}", "-t", f"{1 / fps:.5f}", "-i", cover,
                        "-f", "lavfi", "-t", f"{1 / fps:.5f}", "-i", "anullsrc=r=48000:cl=stereo",
                        "-i", video,
                        "-filter_complex",
                        f"[0:v]scale={w}:{h},setsar=1,fps={fps},format=yuv420p[c];[2:v]setsar=1,format=yuv420p[v];"
                        "[2:a]aresample=48000,aformat=channel_layouts=stereo[a];[c][1:a][v][a]concat=n=2:v=1:a=1[ov][oa]",
                        "-map", "[ov]", "-map", "[oa]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
        shutil.move(out, video)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)
    return cover


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["make", "apply"]); ap.add_argument("--video", required=True)
    ap.add_argument("--title", required=True); ap.add_argument("--out"); ap.add_argument("--at", type=float, default=0.7)
    ap.add_argument("--font", default=FONT)
    a = ap.parse_args()
    if a.cmd == "make": print(make(a.video, a.title, a.out or "cover.jpg", a.at, a.font)[0])
    else: print(apply(a.video, a.title, a.at, a.font))


if __name__ == "__main__":
    main()
