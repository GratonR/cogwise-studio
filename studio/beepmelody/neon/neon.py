"""Moteur NÉON expérimental pour Beep Melody (essais du 19/11/2026).

Différent du moteur pixel art (v2/pi) : on dessine directement en 1080x1920, traits lissés,
puis on ajoute un halo (bloom) : la couche « lumineuse » est réduite 1/4, floutée, ré-agrandie
et additionnée à l'image. Audio synthétisé en numpy (cloches = sinus partiels à décroissance expo).
"""
import subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 48000
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
_fonts = {}
def font(size, medium=False):
    k = (size, medium)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(FONT_M if medium else FONT, size)
    return _fonts[k]

def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

class Frame:
    """Deux calques : base (net) et glow (ce qui brille). compose() = base + bloom(glow)."""
    def __init__(self, bg=(4, 6, 12)):
        self.base = Image.new("RGB", (W, H), bg)
        self.glow = Image.new("RGB", (W, H), (0, 0, 0))
        self.db = ImageDraw.Draw(self.base); self.dg = ImageDraw.Draw(self.glow)
    def line(self, pts, col, w=4, glow=True):
        self.db.line(pts, fill=col, width=w, joint="curve")
        if glow: self.dg.line(pts, fill=col, width=w * 3, joint="curve")
    def circle(self, c, r, col, w=2, glow=False):
        x, y = c; self.db.ellipse((x - r, y - r, x + r, y + r), outline=col, width=w)
        if glow: self.dg.ellipse((x - r, y - r, x + r, y + r), outline=col, width=w * 3)
    def dot(self, c, r, col, glow=1.0):
        x, y = c; self.db.ellipse((x - r, y - r, x + r, y + r), fill=col)
        if glow > 0:
            g = tuple(int(v * glow) for v in col); R = r * 2.2
            self.dg.ellipse((x - R, y - R, x + R, y + R), fill=g)
    def text(self, xy, s, size, col, anchor="mm", medium=False, glow=False):
        self.db.text(xy, s, font=font(size, medium), fill=col, anchor=anchor)
        if glow: self.dg.text(xy, s, font=font(size, medium), fill=col, anchor=anchor)
    def compose(self, bloom=1.0):
        b = np.asarray(self.base, dtype=np.float32)
        g = self.glow.resize((W // 4, H // 4), Image.BILINEAR)
        g1 = np.asarray(g.filter(ImageFilter.GaussianBlur(4)), dtype=np.float32)
        g2 = np.asarray(g.filter(ImageFilter.GaussianBlur(14)), dtype=np.float32)
        gg = Image.fromarray(np.clip(g1 * 0.9 + g2 * 1.1, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        out = b + np.asarray(gg, dtype=np.float32) * bloom
        return np.clip(out, 0, 255).astype(np.uint8)

class Writer:
    def __init__(self, path):
        self.path = path
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                   "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                                   "-pix_fmt", "yuv420p", path + ".video.mp4"], stdin=subprocess.PIPE)
    def add(self, arr): self.p.stdin.write(arr.tobytes())
    def close(self, audio):
        self.p.stdin.close(); self.p.wait()
        import wave
        a = np.clip(audio, -1, 1); pcm = (a * 32767).astype("<i2")
        with wave.open(self.path + ".wav", "wb") as w:
            w.setnchannels(2 if a.ndim == 2 else 1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", self.path + ".video.mp4", "-i", self.path + ".wav",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", self.path], check=True)

# ---------- audio ----------
def mf(m): return 440 * 2 ** ((m - 69) / 12)
def bell(f, dur=2.0, amp=0.25, bright=1.0):
    t = np.arange(int(dur * SR)) / SR
    parts = [(1, 1, 1.0), (2.0, 0.5, 1.6), (3.01, 0.25 * bright, 2.4), (4.2, 0.12 * bright, 3.5)]
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d * 2.2 / dur * 3) for r, a, d in parts)
    att = np.minimum(1, t / 0.004)
    return amp * s * att
def place(buf, sig, t0, pan=0.0):
    i = int(t0 * SR); j = min(len(buf), i + len(sig))
    if j <= i: return
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    buf[i:j, 0] += sig[:j - i] * l; buf[i:j, 1] += sig[:j - i] * r
def pad(dur, notes, amp=0.05):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * mf(n) * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) for n in notes) / len(notes)
    env = np.minimum(1, t / 2.5) * np.minimum(1, (dur - t) / 1.5)
    return amp * s * env
def reverb(x, decay=0.35):
    out = x.copy()
    for d, g in [(0.031, .5), (0.047, .42), (0.071, .35), (0.113, .28), (0.173, .2), (0.251, .14)]:
        k = int(d * SR); out[k:] += x[:-k] * g * decay * 2
    return out
