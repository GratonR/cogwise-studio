"""Format long (essai) : compile des épisodes Cogwise verticaux en une vidéo 16:9 avec chapitres.

Chaque chapitre : la vidéo verticale (608x1080) à gauche, un panneau « manuel vintage » à droite (numéro, titre, accroche).
Une carte d'ouverture de 4 s. Sortie : la vidéo + un fichier chapitres.txt prêt pour la description YouTube.

  python3 tools/longform.py plan.json out_dir
plan.json = {"title": "...", "subtitle": "...", "chapters": [{"video": "outbox/...mp4", "title": "...", "hook": "..."}]}
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
INK, INK2, CREAM, WALL, MUST, RED = "#26232b", "#5a5560", "#fbf5e8", "#f4ead6", "#f2b134", "#e4472f"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"

def f(path, size, wght=None):
    ft = ImageFont.truetype(path, size)
    if wght:
        try: ft.set_variation_by_axes([wght])
        except Exception: pass
    return ft

def wrap(d, text, ft, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=ft) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def panel(path, n, total, title, hook):
    im = Image.new("RGB", (W, H), WALL); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 760, H), fill=INK)                      # fond derrière la vidéo
    d.rectangle((760, 0, W, 14), fill=MUST); d.rectangle((760, 14, W, 20), fill=RED)
    logo = Image.open(os.path.join(ROOT, "kit/brand/cogwise_logo.png")).convert("RGBA").resize((96, 96))
    im.paste(logo, (W - 150, H - 150), logo)
    d.text((860, 150), f"CHAPTER {n} / {total}", font=f(INTER, 30), fill=INK2)
    y = 220
    for line in wrap(d, title, f(LORA, 78, 700), 900):
        d.text((860, y), line, font=f(LORA, 78, 700), fill=INK); y += 96
    y += 30; d.rectangle((860, y, 1000, y + 6), fill=RED); y += 50
    for line in wrap(d, hook, f(LORA, 40, 400), 880):
        d.text((860, y), line, font=f(LORA, 40, 400), fill=INK2); y += 56
    im.save(path)

def intro(path, title, subtitle, items):
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 14), fill=MUST); d.rectangle((0, 14, W, 20), fill=RED)
    logo = Image.open(os.path.join(ROOT, "kit/brand/cogwise_logo.png")).convert("RGBA").resize((140, 140))
    im.paste(logo, (W // 2 - 70, 110), logo)
    y = 300
    for line in wrap(d, title, f(LORA, 84, 700), 1500):
        d.text((W // 2, y), line, font=f(LORA, 84, 700), fill=INK, anchor="ma"); y += 104
    d.text((W // 2, y + 10), subtitle, font=f(LORA, 42, 400), fill=INK2, anchor="ma"); y += 110
    for i, t in enumerate(items):
        d.text((W // 2, y + i * 50), f"{i + 1}. {t}", font=f(INTER, 34), fill=INK, anchor="ma")
    im.save(path)

def run(cmd): subprocess.run(cmd, check=True)

def main(plan_path, out):
    P = json.load(open(plan_path)); os.makedirs(out, exist_ok=True); ch = P["chapters"]; parts = []
    intro(os.path.join(out, "intro.png"), P["title"], P.get("subtitle", ""), [c["title"] for c in ch])
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "4", "-i", os.path.join(out, "intro.png"), "-f", "lavfi", "-t", "4", "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-shortest", os.path.join(out, "p00.mp4")])
    parts.append("p00.mp4"); marks = [("0:00", "Intro")]; t = 4.0
    for i, c in enumerate(ch, 1):
        bg = os.path.join(out, f"bg{i}.png"); panel(bg, i, len(ch), c["title"], c.get("hook", ""))
        src = os.path.join(ROOT, c["video"]); dst = f"p{i:02d}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", bg, "-i", src, "-filter_complex",
             "[1:v]scale=-2:1080,fps=30[v];[0:v][v]overlay=76:0:shortest=1,format=yuv420p[o];[1:a]aresample=48000,aformat=channel_layouts=stereo[a]",
             "-map", "[o]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", os.path.join(out, dst)])
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(out, dst)], capture_output=True, text=True).stdout)
        marks.append((f"{int(t // 60)}:{int(t % 60):02d}", c["title"])); t += dur; parts.append(dst)
    open(os.path.join(out, "list.txt"), "w").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(out, "list.txt"), "-c", "copy", os.path.join(out, "longform.mp4")])
    open(os.path.join(out, "chapitres.txt"), "w").write("\n".join(f"{a} {b}" for a, b in marks) + "\n")
    print(f"{t:.1f} s", os.path.join(out, "longform.mp4"))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
