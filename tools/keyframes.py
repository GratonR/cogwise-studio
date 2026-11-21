"""Planche d'images clés d'un épisode, pour que Claude « voie » la vidéo quand il juge un commentaire.

Une image par phrase de la voix off (au milieu de la phrase, lue dans le .srt), avec le temps et la phrase en
légende. Sans .srt (Beep Melody), une image toutes les 5 s. Grille de 4 colonnes, JPEG ~200-400 Ko.

  python3 tools/keyframes.py outbox/cogwise/2026-11-19_blunt-nail      -> <dossier>/<slug>_keyframes.jpg
"""
import glob, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

COLS, TW = 4, 270                       # largeur d'une vignette ; 1080/4
FONT = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

def ts(s):
    h, m, rest = s.split(":"); sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

def cues(srt):
    out = []
    for block in re.split(r"\n\s*\n", open(srt, encoding="utf-8").read().strip()):
        lines = block.strip().splitlines()
        tl = next((l for l in lines if "-->" in l), None)
        if not tl: continue
        a, b = [ts(x.strip()) for x in tl.split("-->")]
        txt = " ".join(l for l in lines[lines.index(tl) + 1:]).strip()
        out.append(((a + b) / 2, txt))
    return out

def duration(mp4):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                                capture_output=True, text=True).stdout)

def wrap(d, text, ft, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=ft) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def main(folder):
    folder = folder.rstrip("/")
    slug = os.path.basename(folder).split("_", 1)[-1]
    mp4 = os.path.join(folder, slug + ".mp4")
    if not os.path.exists(mp4):
        mp4 = sorted(glob.glob(os.path.join(folder, "*.mp4")))[0]
    srt = os.path.join(folder, slug + ".srt")
    pts = cues(srt) if os.path.exists(srt) else []
    if not pts:
        d = duration(mp4); pts = [(t + 0.5, "") for t in range(0, int(d), 5)]
    pts = pts[:24]
    ft, fb = ImageFont.truetype(FONT, 15), ImageFont.truetype(FONT_B, 17)
    th = TW * 16 // 9; cap = 78
    rows = (len(pts) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * TW, rows * (th + cap)), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    with tempfile.TemporaryDirectory() as tmp:
        for i, (t, txt) in enumerate(pts):
            p = os.path.join(tmp, f"{i}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", mp4, "-frames:v", "1", "-vf", f"scale={TW}:{th}", p], check=True)
            x, y = (i % COLS) * TW, (i // COLS) * (th + cap)
            sheet.paste(Image.open(p).convert("RGB"), (x, y))
            d.text((x + 6, y + th + 4), f"{int(t // 60)}:{int(t % 60):02d}", font=fb, fill=(242, 177, 52))
            for k, line in enumerate(wrap(d, txt, ft, TW - 12)[:3]):
                d.text((x + 6, y + th + 24 + k * 17), line, font=ft, fill=(225, 225, 230))
    out = os.path.join(folder, slug + "_keyframes.jpg")
    sheet.save(out, quality=80, optimize=True)
    print(out, os.path.getsize(out) // 1024, "Ko", len(pts), "images")
    return out

if __name__ == "__main__":
    for f in sys.argv[1:]: main(f)
