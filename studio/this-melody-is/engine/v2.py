"""PHI melody v2 — pixel-art short, 1080x1920 @30fps.
Art layer 180x320 (x6), text layer 360x640 (x3)."""
import sys, math, os, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

AW, AH, TW, TH, OW, OH, FPS = 180, 320, 360, 640, 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
F20 = ImageFont.truetype(f"{HERE}/vt323.ttf", 20)
F40 = ImageFont.truetype(f"{HERE}/vt323.ttf", 40)
PHI = ("1.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374847540880"
       "753868917521266338622235369317931800607667263544333890865959395829056383226613199282902678806752087668925017116962070322210432162695486262963136144")
DIGITS = [int(c) for c in PHI if c.isdigit()]
NOTE = 0.25

CREAM, YEL, RED, DIM = (236, 228, 206), (240, 196, 80), (232, 74, 60), (150, 140, 120)
GREEN, GREEN_HI = (90, 200, 120), (170, 240, 180)

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def eout(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def bounce(x):
    x = max(0.0, min(1.0, x))
    if x < 0.7: return (x / 0.7) ** 2
    u = (x - 0.85) / 0.15; return 1 - 0.08 * (1 - u * u)
def lerp(a, b, t): return a + (b - a) * t
def mix(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))
def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)

# ---------------- text ----------------
_GL = {
    "φ": ["...#...", "...#...", "...#...", ".#####.", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#", "#..#..#",
          ".#####.", "...#...", "...#...", "...#..."],
    "≈": [".##....", "#..#..#", "....##.", ".......", ".##....", "#..#..#", "....##."],
}
_GL_Y = {"φ": 5, "≈": 8}

def text(d, x, y, s, size=20, fill=CREAM, cols=None, align="l", chalk=None):
    f = F20 if size == 20 else F40; k = 1 if size == 20 else 2; adv = 8 * k
    if align == "r": x -= adv * len(s)
    elif align == "c": x -= adv * len(s) / 2
    x = int(round(x)); y = int(round(y))
    for i, ch in enumerate(s):
        c = cols[i] if cols else fill
        if ch in _GL:
            for r, row in enumerate(_GL[ch]):
                for cx, p in enumerate(row):
                    if p == "#": d.rectangle([x + cx * k, y + (_GL_Y[ch] + r) * k, x + cx * k + k - 1, y + (_GL_Y[ch] + r) * k + k - 1], fill=c)
        elif ch != " ":
            d.text((x, y), ch, font=f, fill=c)
        x += adv

def chalkify(layer, box, seed):
    """punch random holes into text pixels to look like chalk"""
    a = np.array(layer)
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    sub = a[y0:y1, x0:x1]
    m = (sub[..., 3] > 0) & (rng.random(sub.shape[:2]) < 0.22)
    sub[m, 3] = 90
    a[y0:y1, x0:x1] = sub
    return Image.fromarray(a)

# ---------------- panel ----------------
def glitch_str(s, age, seed):
    if age is None or age > 0.14: return s, 0
    r = random.Random(int(seed * 1000) + int(age * 300))
    pool = "0123456789#%&@?/<>"
    return "".join(r.choice(pool) if ch not in " ." and r.random() < 0.6 else ch for ch in s), r.randint(-6, 6)

def panel(d, label, value=None, sub=None, cols=None, right=None, age=None, style="warm", sub_col=CREAM, value_size=40):
    if style == "warm": bg, br = (40, 26, 18), (110, 76, 50)
    elif style == "green": bg, br = (4, 12, 8), (50, 130, 80)
    else: bg, br = (10, 12, 12), (110, 116, 112)
    d.rectangle([40, 66, 320, 156], fill=bg)
    d.rectangle([40, 66, 320, 67], fill=br); d.rectangle([40, 155, 320, 156], fill=br)
    text(d, 50, 66, label)
    if value is not None:
        v, dx = glitch_str(value, age, hash(label) % 97)
        text(d, 50 + dx, 82, v, size=value_size, cols=cols if v == value else None, fill=cols[0] if cols else CREAM)
        if v != value:  # glitch bars
            r = random.Random(int(age * 1000))
            for _ in range(3):
                yy = r.randint(90, 120); d.rectangle([50, yy, 50 + r.randint(40, 200), yy + 1], fill=r.choice([RED, CREAM, YEL]))
    if sub: text(d, 50, 128, sub, fill=sub_col)
    if right:
        for i, s in enumerate(right): text(d, 312, 92 + i * 18, s, fill=YEL, align="r")

def digit_cols(s, target):
    out, ok = [], True
    for i, ch in enumerate(s):
        ok = ok and i < len(target) and target[i] == ch
        out.append(CREAM if ok else RED)
    return out

# ---------------- art helpers ----------------
def noise(shape, seed, scale=1):
    rng = np.random.default_rng(seed)
    h, w = shape
    n = rng.random((h // scale + 2, w // scale + 2))
    n = np.kron(n, np.ones((scale, scale)))[:h, :w]
    return n

def pix_arc(d, cx, cy, r, a0, a1, fill, prog=1.0, width=1, shadow=None):
    a1 = a0 + (a1 - a0) * prog
    n = max(2, int(abs(a1 - a0) * r * 1.5) + 2)
    pts = set()
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.add((int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a)))))
    if shadow:
        d.point([(x, y + 1) for x, y in pts], fill=shadow)
    d.point(list(pts), fill=fill)
    if width > 1:
        d.point([(x + 1, y) for x, y in pts], fill=fill)

def pix_line(d, p, q, fill, prog=1.0):
    q = (lerp(p[0], q[0], prog), lerp(p[1], q[1], prog))
    d.line([(round(p[0]), round(p[1])), (round(q[0]), round(q[1]))], fill=fill)

def wheel(d, cx, cy, ang, r=7):
    cx, cy = int(round(cx)), int(round(cy))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=None, outline=(120, 80, 20), width=1)
    d.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], outline=(236, 184, 60))
    pix_arc(d, cx, cy, r - 1, math.pi * 1.05, math.pi * 1.5, (255, 236, 150))
    for k in range(3):
        a = ang + k * math.pi / 3
        d.line([cx - (r - 2) * math.cos(a), cy - (r - 2) * math.sin(a), cx + (r - 2) * math.cos(a), cy + (r - 2) * math.sin(a)], fill=(220, 168, 50))
    d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 230, 140))
    d.point((cx, cy), fill=(120, 80, 20))

# ---------------- backgrounds (cached) ----------------
_BG = {}
def bg(name):
    if name in _BG: return _BG[name]
    a = np.zeros((AH, AW, 3), np.float32)
    if name == "grid":
        a[:] = (16, 20, 38)
        yy, xx = np.mgrid[0:AH, 0:AW]
        vig = 1 - 0.35 * (((xx - AW / 2) / AW) ** 2 + ((yy - AH / 2) / AH) ** 2) * 2
        a[(xx % 10 == 0) | (yy % 10 == 0)] = (24, 31, 58)
        a[(xx % 50 == 0) | (yy % 50 == 0)] = (32, 42, 78)
        a *= vig[..., None]
    elif name == "desk":
        rng = np.random.default_rng(3)
        for x0 in range(0, AW, 22):
            c = np.array((70, 44, 28)) * rng.uniform(0.85, 1.12)
            a[:, x0:x0 + 22] = c
            a[:, x0] = c * 0.6; a[:, x0 + 1] = c * 1.15
        g = noise((AH, AW), 4)
        a *= (0.92 + 0.12 * (np.kron(noise((AH // 6 + 1, AW), 5), np.ones((6, 1)))[:AH] > 0.8))[..., None]
        a *= (0.96 + 0.06 * g)[..., None]
    elif name == "wood":
        rng = np.random.default_rng(7)
        y = 0
        while y < AH:
            c = np.array((150, 96, 58)) * rng.uniform(0.86, 1.1)
            a[y:y + 10] = c
            a[y] = c * 1.13; a[min(AH - 1, y + 9)] = c * 0.62
            for _ in range(rng.integers(3, 6)):
                gy, gx, gl = y + rng.integers(2, 8), rng.integers(0, AW), rng.integers(8, 30)
                if gy < AH: a[gy, gx:gx + gl] = c * 0.88
            x = rng.integers(-30, 20)
            while x < AW:
                x += rng.integers(45, 90)
                if 0 <= x < AW: a[y:y + 9, x] = c * 0.6; a[y:y + 9, min(AW - 1, x + 1)] = c * 1.1
            y += 10
    elif name == "chalk":
        a[:] = (36, 62, 46)
        n = noise((AH, AW), 11, 12); n2 = noise((AH, AW), 12, 3)
        a *= (0.9 + 0.16 * n + 0.05 * n2)[..., None]
        rng = np.random.default_rng(13)
        for _ in range(16):  # smudges
            x, y, w = rng.integers(0, AW), rng.integers(0, AH), rng.integers(10, 40)
            a[y:y + 2, x:x + w] = a[y:y + 2, x:x + w] * 1.08
        for side in (0, AW - 7):
            a[:, side:side + 7] = (110, 70, 40)
            a[:, side + (0 if side == 0 else 6)] = (70, 42, 24)
            a[:, side + (6 if side == 0 else 0)] = (150, 100, 60)
        a[AH - 10:, :] = (96, 60, 34); a[AH - 10, :] = (150, 100, 60); a[AH - 9, :] = (120, 78, 44)
        a[AH - 13:AH - 10, 30:44] = (230, 230, 220); a[AH - 13:AH - 10, 120:128] = (220, 200, 120)
    elif name == "garden":
        yy = np.arange(AH)[:, None]
        top, bot = np.array((70, 128, 196)), np.array((176, 214, 232))
        t = np.clip(yy / 230, 0, 1)
        bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16
        steps = 6
        q = np.floor(t * steps + np.tile(bayer, (AH // 4 + 1, AW // 4 + 1))[:AH, :AW]) / steps
        a[:] = top + (bot - top) * np.clip(q, 0, 1)[..., None]
        xs = np.arange(AW)
        h1 = (232 + 8 * np.sin(xs / 23) + 5 * np.sin(xs / 9 + 1)).astype(int)
        h2 = (250 + 6 * np.sin(xs / 17 + 2)).astype(int)
        for x in range(AW):
            a[h1[x]:, x] = (92, 140, 110); a[h1[x], x] = (120, 168, 130)
            a[h2[x]:, x] = (70, 128, 60); a[h2[x], x] = (110, 170, 80)
        rng = np.random.default_rng(21)
        for _ in range(500):
            x, y = rng.integers(0, AW), rng.integers(256, AH)
            a[y:y + rng.integers(1, 4), x] = rng.choice([(50, 100, 44), (96, 160, 70), (130, 190, 90)])
    elif name == "term":
        a[:] = (6, 14, 10)
        a[::2] *= 0.8
    _BG[name] = a.astype(np.uint8)
    return _BG[name]

def papyrus_img():
    if "papyrus" in _BG: return _BG["papyrus"]
    w, h = 140, 186
    rng = np.random.default_rng(31)
    base = np.array((218, 196, 146), np.float32)
    a = np.ones((h, w, 3), np.float32) * base
    rows = np.kron(rng.random((h, w // 4 + 1)), np.ones((1, 4)))[:, :w]
    a *= (0.93 + 0.1 * rows)[..., None]
    for x in range(0, w, 7): a[:, x] *= 0.94
    sp = rng.random((h, w)) < 0.025; a[sp] *= 0.82
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, w - 1 - xx]) / 10
    a *= (0.82 + 0.18 * np.clip(edge, 0, 1))[..., None]
    _BG["papyrus"] = np.clip(a, 0, 255).astype(np.uint8)
    return _BG["papyrus"]

def roll(d, x0, x1, y):
    cols = [(120, 92, 56), (170, 136, 88), (214, 186, 132), (232, 210, 160), (200, 168, 116), (150, 116, 72), (96, 70, 40)]
    for i, c in enumerate(cols): d.line([x0, y + i, x1, y + i], fill=c)
    for xe in (x0, x1):
        d.ellipse([xe - 2, y, xe + 2, y + 6], fill=(150, 116, 72), outline=(80, 56, 32))
        d.point((xe, y + 3), fill=(60, 40, 22))

# ---------------- scene base ----------------
class Ctx:
    def __init__(self, bgname):
        self.art = Image.fromarray(bg(bgname).copy()) if bgname else Image.new("RGB", (AW, AH))
        self.a = ImageDraw.Draw(self.art)
        self.txt = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
        self.t = ImageDraw.Draw(self.txt); self.t.fontmode = "1"

def number_line(c, pos, show_tag=True):
    y, x0, u = 180, 30, 55
    c.a.line([18, y, 162, y], fill=(80, 150, 190))
    c.a.line([18, y + 1, 162, y + 1], fill=(30, 50, 80))
    for k in range(3):
        c.a.line([x0 + k * u, y - 2, x0 + k * u, y + 2], fill=CREAM)
        text(c.t, (x0 + k * u) * 2 - 4, y * 2 + 8, str(k), fill=DIM)
    x = x0 + pos * u
    if pos > 0: c.a.line([x0, y, x, y], fill=YEL)
    wheel(c.a, x, y - 8, pos * u / 7)
    if show_tag and pos > 1.6:
        X = int(x * 2)
        c.t.rectangle([X - 6, y * 2 + 8, X + 8, y * 2 + 24], fill=YEL)
        text(c.t, X - 3, y * 2 + 6, "φ", fill=(30, 20, 10))

# ---------------- scenes ----------------
def sc_intro(t, T):
    c = Ctx("grid")
    c.t.rectangle([34, 76, 250, 158], fill=(6, 7, 12))
    text(c.t, 44, 74, "THIS MELODY", size=40); text(c.t, 44, 112, "IS φ", size=40)
    n = int(t / NOTE) + 1
    s = PHI[:n + (1 if n > 1 else 0)]
    l1, l2 = s[:10], s[10:18]
    text(c.t, 44, 228, l1, size=40)
    if l2: text(c.t, 44, 266, l2, size=40)
    if int(t * 3) % 2 == 0 and len(s) < 18:
        cx = 44 + 16 * (len(l1) if not l2 else len(l2)); cy = 228 if not l2 else 266
        c.t.rectangle([cx + 2, cy + 30, cx + 14, cy + 32], fill=CREAM)
    number_line(c, 1.6180339887 * eout((t - 0.2) / 3.0))
    return c

EU = dict(x0=36, y0=166, s=56)
def sc_euclid(t, T):
    c = Ctx("desk")
    px, py = 20, 98
    # shadow + papyrus + rolls
    c.a.rectangle([px + 3, py + 3, px + 140 + 3, py + 186 + 3], fill=(36, 22, 14))
    c.art.paste(Image.fromarray(papyrus_img()), (px, py))
    roll(c.a, px - 4, px + 143, py - 6); roll(c.a, px - 4, px + 143, py + 184)
    ink, ink2 = (52, 34, 22), (120, 88, 56)
    x0, y0, s = EU["x0"], EU["y0"], EU["s"]
    corners = [(x0, y0 + s), (x0 + s, y0 + s), (x0 + s, y0), (x0, y0), (x0, y0 + s)]
    pen = None
    p = (t - 0.2) / 1.6
    for i in range(4):
        q = max(0, min(1, p * 4 - i))
        if q > 0:
            pix_line(c.a, corners[i], corners[i + 1], ink, q)
            if q < 1: pen = (lerp(corners[i][0], corners[i + 1][0], q), lerp(corners[i][1], corners[i + 1][1], q))
    mx, my = x0 + s / 2, y0 + s
    r = math.hypot(s / 2, s)
    if t > 1.9:
        c.a.line([mx, my - 2, mx, my + 2], fill=ink)
        q = ease((t - 1.9) / 0.5)
        # dashed half-diagonal
        for k in range(0, 40):
            if k % 2 == 0 and k / 40 < q:
                a = (lerp(mx, x0 + s, k / 40), lerp(my, y0, k / 40)); b = (lerp(mx, x0 + s, (k + 1) / 40), lerp(my, y0, (k + 1) / 40))
                c.a.line([a, b], fill=ink2)
    a0 = math.atan2(-s, s / 2)
    qa = ease((t - 2.5) / 1.4)
    xe = mx + r
    qr = ease((t - 4.0) / 0.9)
    if qr > 0:  # rectangle extension (wash + lines)
        w = (xe - (x0 + s))
        if w * qr >= 1: c.a.rectangle([x0 + s + 1, y0 + 1, x0 + s + w * qr, y0 + s - 1], fill=(206, 168, 106))
        pix_line(c.a, (x0 + s, y0 + s), (xe, y0 + s), ink, qr)
        pix_line(c.a, (x0 + s, y0), (xe, y0), ink, qr)
        if qr >= 1: pix_line(c.a, (xe, y0 + s), (xe, y0), ink)
        pix_line(c.a, corners[1], corners[2], ink)
    if qa > 0:
        pix_arc(c.a, mx, my, r, a0, 0, (170, 40, 30), qa)
    if 2.3 < t < 4.2:  # compass
        ang = lerp(a0, 0, qa)
        P = (mx + r * math.cos(ang), my + r * math.sin(ang))
        L = 38; hd = math.sqrt(max(0, L * L - (r / 2) ** 2))
        midx, midy = (mx + P[0]) / 2, (my + P[1]) / 2
        nx, ny = -(P[1] - my) / r, (P[0] - mx) / r
        if nx < 0: nx, ny = -nx, -ny
        H = (midx + nx * hd, midy + ny * hd)
        lift = ease((t - 3.9) / 0.3) * 6
        H = (H[0], H[1] - lift); M2 = (mx, my - lift); P2 = (P[0], P[1] - lift)
        for leg, col in ((M2, (150, 156, 160)), (P2, (196, 160, 70))):
            c.a.line([H, leg], fill=(40, 40, 44), width=4); c.a.line([H, leg], fill=col, width=2)
            c.a.line([H, ((H[0]+leg[0])/2, (H[1]+leg[1])/2)], fill=shade(col, 1.25), width=1)
        c.a.point(P2, fill=(30, 20, 10))
        c.a.ellipse([H[0] - 3, H[1] - 3, H[0] + 3, H[1] + 3], fill=(200, 170, 80), outline=(60, 44, 20))
        c.a.line([H[0], H[1] - 3, H[0], H[1] - 8], fill=(60, 44, 20), width=2)
    elif pen is not None:  # reed pen
        c.a.line([pen[0], pen[1], pen[0] + 9, pen[1] - 14], fill=(90, 60, 30), width=2)
        c.a.line([pen[0] + 9, pen[1] - 14, pen[0] + 14, pen[1] - 22], fill=(160, 120, 70), width=2)
        c.a.point(pen, fill=(20, 12, 6))
    # recursive golden rectangles
    if t > 5.1:
        rx0, ry0, rx1, ry1 = x0 + s, y0, xe, y0 + s
        k = 0; dirs = ["d", "l", "u", "r"]
        while k < 5 and t > 5.1 + k * 0.45:
            q = ease((t - 5.1 - k * 0.45) / 0.3)
            w, h = rx1 - rx0, ry1 - ry0
            dr = dirs[k % 4]
            if dr == "d": sq = w; pix_line(c.a, (rx0, ry0 + sq), (rx1, ry0 + sq), ink, q); ry0 += sq
            elif dr == "l": sq = h; pix_line(c.a, (rx1 - sq, ry0), (rx1 - sq, ry1), ink, q); rx1 -= sq
            elif dr == "u": sq = w; pix_line(c.a, (rx0, ry1 - sq), (rx1, ry1 - sq), ink, q); ry1 -= sq
            else: sq = h; pix_line(c.a, (rx0 + sq, ry0), (rx0 + sq, ry1), ink, q); rx0 += sq
            k += 1
    if t > 4.9:
        T2 = c.t
        text(T2, (x0 + s / 2) * 2 - 4, (y0 + s) * 2 + 4, "A", fill=(52, 34, 22))
        text(T2, ((x0 + s + xe) / 2) * 2 - 4, (y0 + s) * 2 + 4, "B", fill=(52, 34, 22))
        text(T2, 58, 486, "(A+B) : A = A : B", fill=(52, 34, 22))
    done = t > 4.9
    panel(c.t, "EUCLID ≈300 BC", "1.6" if done else "?", "EXTREME AND MEAN RATIO", [CREAM] * 3 if done else [DIM],
          right=["ELEMENTS", "II.11"], age=(t - 4.9) if done else None)
    return c

# Fibonacci tiling
FIB = [1, 1, 2, 3, 5, 8, 13, 21]
def fib_layout():
    sq = [(0, 0, 1, 1)]; x0, y0, x1, y1 = 0, 0, 1, 1
    for i, s in enumerate(FIB[1:]):
        dr = ["right", "down", "left", "up"][i % 4]
        r = {"right": (x1, y0, x1 + s, y0 + s), "down": (x0, y1, x0 + s, y1 + s),
             "left": (x0 - s, y0, x0, y0 + s), "up": (x0, y0 - s, x0 + s, y0)}[dr]
        sq.append(r); x0, y0, x1, y1 = min(x0, r[0]), min(y0, r[1]), max(x1, r[2]), max(y1, r[3])
    def opts(r):
        cs = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
        return [(cs[k], cs[(k + 1) % 4], cs[(k + 3) % 4]) for k in range(4)]
    def onbox(p, i):
        if i == 0: return True
        b = (min(q[0] for q in sq[:i]), min(q[1] for q in sq[:i]), max(q[2] for q in sq[:i]), max(q[3] for q in sq[:i]))
        return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]
    def dfs(i, pe, acc):
        if i == len(sq): return acc
        for cen, e1, e2 in opts(sq[i]):
            if not onbox(cen, i): continue
            for a, b in ((e1, e2), (e2, e1)):
                if pe is None or a == pe:
                    r = dfs(i + 1, b, acc + [(cen, a, b)])
                    if r: return r
        return None
    return sq, (x0, y0, x1, y1), dfs(0, None, [])
FSQ, FBOX, FARC = fib_layout()
TILE_COLS = [(222, 184, 120), (196, 146, 86), (124, 80, 48), (178, 104, 64), (226, 202, 156), (160, 112, 66), (104, 66, 40), (206, 160, 98)]

def tile(d, x0, y0, x1, y1, col, seed):
    x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
    d.rectangle([x0, y0, x1, y1], fill=col)
    if x1 - x0 >= 6:
        rng = random.Random(seed)
        for _ in range((y1 - y0) // 3):
            gy = rng.randint(y0 + 2, max(y0 + 2, y1 - 2)); gx = rng.randint(x0 + 1, x1 - 2)
            d.line([gx, gy, min(x1 - 2, gx + rng.randint(3, 14)), gy], fill=shade(col, 0.9))
    d.line([x0, y0, x1, y0], fill=mix(col, (255, 236, 200), 0.25)); d.line([x0, y0, x0, y1], fill=mix(col, (255, 236, 200), 0.15))
    d.line([x0, y1, x1, y1], fill=shade(col, 0.68)); d.line([x1, y0, x1, y1], fill=shade(col, 0.74))

def sc_fib(t, T):
    c = Ctx("wood")
    U = 4
    bw, bh = (FBOX[2] - FBOX[0]) * U, (FBOX[3] - FBOX[1]) * U
    ox, oy = (AW - bw) // 2 - FBOX[0] * U, 196 - bh // 2 - FBOX[1] * U
    # board shadow/frame
    c.a.rectangle([ox + FBOX[0] * U - 3, oy + FBOX[1] * U - 3, ox + FBOX[2] * U + 3, oy + FBOX[3] * U + 3], fill=(60, 36, 20))
    c.a.rectangle([ox + FBOX[0] * U - 2, oy + FBOX[1] * U - 2, ox + FBOX[2] * U + 2, oy + FBOX[3] * U + 2], fill=(74, 44, 26))
    c.a.line([ox + FBOX[0] * U - 1, oy + FBOX[1] * U - 1, ox + FBOX[2] * U + 1, oy + FBOX[1] * U - 1], fill=(44, 26, 14))
    c.a.line([ox + FBOX[0] * U - 1, oy + FBOX[1] * U - 1, ox + FBOX[0] * U - 1, oy + FBOX[3] * U + 1], fill=(44, 26, 14))
    c.a.rectangle([ox + FBOX[0] * U - 4, oy + FBOX[1] * U - 4, ox + FBOX[2] * U + 4, oy + FBOX[3] * U + 4], outline=(176, 120, 72))
    for r in FSQ:  # engraved ghost slots
        gx0, gy0, gx1, gy1 = ox + r[0] * U, oy + r[1] * U, ox + r[2] * U - 1, oy + r[3] * U - 1
        c.a.rectangle([gx0, gy0, gx1, gy1], outline=(92, 58, 34))
        c.a.line([gx0 + 1, gy1, gx1, gy1], fill=(58, 34, 20))
    step, t0 = 0.62, 0.3
    landed = 0
    for i, r in enumerate(FSQ):
        ti = t0 + i * step
        if t < ti: break
        q = (t - ti) / 0.38
        fall = (1 - bounce(q)) * 70
        x0, y0, x1, y1 = ox + r[0] * U, oy + r[1] * U, ox + r[2] * U - 1, oy + r[3] * U - 1
        if q < 1:
            sh = int(lerp(0, 1, ease(q)) * 3)
            if sh: c.a.rectangle([x0 + sh, y0 + sh, x1 + sh, y1 + sh], fill=(50, 30, 16))
        tile(c.a, x0, y0 - fall, x1, y1 - fall, TILE_COLS[i], i)
        if q >= 1:
            landed = i + 1
            if FIB[i] >= 3:
                text(c.t, (x0 + x1) + 1 - 4 * len(str(FIB[i])), (y0 + y1) - 10, str(FIB[i]), fill=shade(TILE_COLS[i], 0.45))
            dq = (q - 1) / 0.25 * 0.38
            if 0 <= dq < 1:  # dust
                rng = random.Random(i)
                for _ in range(10):
                    sx = rng.uniform(x0, x1); dx = rng.uniform(-1, 1) * 10 * dq; dy = -rng.uniform(1, 6) * dq
                    c.a.point((sx + dx, y1 + 1 + dy), fill=(214, 190, 150))
    # spiral
    for i in range(landed):
        ti = t0 + i * step + 0.38
        q = ease((t - ti) / 0.4)
        if q <= 0: continue
        cen, a, b = FARC[i]; rr = FIB[i] * U
        cx, cy = ox + cen[0] * U, oy + cen[1] * U
        aa = math.atan2(a[1] - cen[1], a[0] - cen[0]); ab = math.atan2(b[1] - cen[1], b[0] - cen[0])
        diff = (ab - aa + 3 * math.pi) % (2 * math.pi) - math.pi
        pix_arc(c.a, cx - 0.5, cy - 0.5, rr, aa, aa + diff, (252, 214, 110), q, shadow=(70, 40, 18))
    seq = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    extra = max(0, int((t - (t0 + 8 * step + 0.3)) / 0.45) + 1) if t > t0 + 8 * step + 0.3 else 0
    k = max(1, min(len(seq) - 1, landed + extra - 1)) if landed >= 2 else None
    if k:
        val = f"{seq[k] / seq[k - 1]:.5f}"
        tchg = t0 + (k) * step + 0.38 if extra == 0 else t0 + 8 * step + 0.3 + (extra - 1) * 0.45
        panel(c.t, "FIBONACCI 1202", val, f"{seq[k]} / {seq[k-1]}", digit_cols(val, PHI), right=["RABBITS", f"{seq[k]} PAIR" + ("S" if seq[k] > 1 else "")], age=t - tchg)
    else:
        panel(c.t, "FIBONACCI 1202", "-", "F(N+1) / F(N)", [DIM], right=["RABBITS", f"{landed} PAIR" + ("S" if landed > 1 else "")])
    if t > t0 + 8 * step + 0.5:
        text(c.t, 180, 520, "SPIRAL OF SQUARES", fill=(250, 224, 170), align="c")
    return c

def sc_hurwitz(t, T):
    c = Ctx("chalk")
    lv_dt, lv0 = 0.5, 0.3
    nlv = min(5, int((t - lv0) / lv_dt) + 1) if t > lv0 else 0
    W = c.t
    chalk = (232, 236, 226)
    for k in range(nlv):
        x, y = 44 + k * 30, 184 + k * 28
        q = ease((t - lv0 - k * lv_dt) / 0.25)
        text(W, x, y + 10, "1 +", fill=chalk)
        x1 = 44 + 5 * 30 + 60
        barw = int((x1 - (x + 30)) * q)
        W.rectangle([x + 30, y + 21, x + 30 + barw, y + 22], fill=chalk)
        if q > 0.6: text(W, x + 30 + (x1 - x - 30) / 2 - 4, y + 2, "1", fill=chalk)
    if nlv == 5 and t > lv0 + 5 * lv_dt:
        text(W, 44 + 5 * 30, 184 + 5 * 28 + 10, "1 + ...", fill=chalk)
    # convergence plot
    conv = [1, 2, 1.5, 5 / 3, 1.6, 1.625, 13 / 8.0 * 0 + 21 / 13, 34 / 21, 55 / 34, 89 / 55, 144 / 89, 233 / 144, 377 / 233, 610 / 377]
    phi = 1.6180339887
    gx0, gy, gs = 22, 246, 34
    for x in range(14, 166, 4): c.a.line([x, gy, x + 1, gy], fill=(220, 120, 110))
    text(W, 336, gy * 2 - 10, "φ", fill=(220, 120, 110), align="r")
    np_ = min(len(conv), 1 + max(0, int((t - 0.6) / 0.42)))
    pts = [(gx0 + i * 10.5, gy - max(-1, min(1, (conv[i] - phi) * 2.2)) * gs) for i in range(np_)]
    for i in range(1, len(pts)): c.a.line([pts[i - 1], pts[i]], fill=(214, 218, 206))
    for p in pts: c.a.rectangle([p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1], fill=(250, 250, 240))
    text(W, 180, 560, "SLOWEST CONVERGENCE OF ALL", fill=(200, 210, 196), align="c") if t > 4 else None
    c.txt = chalkify(c.txt, (30, 170, 340, 600), int(t * 4))
    c.t = ImageDraw.Draw(c.txt); c.t.fontmode = "1"
    val = f"{conv[np_ - 1]:.5f}"
    panel(c.t, "HURWITZ 1891", val, "THE MOST IRRATIONAL NUMBER", digit_cols(val, PHI), right=["ALL ONES", f"{np_} TERMS"],
          age=t - (0.6 + (np_ - 1) * 0.42), style="dark")
    return c

def sunflower(c, t, ang_deg, n, sway):
    cx, cy = 90, 176
    d = c.a
    # stem & leaves
    for y in range(cy + 30, AH):
        xo = int(2 * math.sin((y - cy) / 40 + sway))
        d.line([cx - 2 + xo, y, cx + 2 + xo, y], fill=(64, 120, 48)); d.point((cx - 2 + xo, y), fill=(40, 84, 30)); d.point((cx + 2 + xo, y), fill=(120, 180, 80))
    for sgn, ly in ((-1, 262), (1, 286)):
        pts = [(cx, ly), (cx + sgn * 16, ly - 10), (cx + sgn * 34, ly - 6), (cx + sgn * 20, ly + 4)]
        d.polygon(pts, fill=(76, 140, 56), outline=(40, 84, 30)); d.line([pts[0], pts[2]], fill=(120, 180, 80))
    # petals: back ring then front ring
    for ring, cnt, col, r0, r1, off in ((0, 21, (214, 148, 24), 38, 58, 0.07), (1, 34, (250, 200, 40), 38, 56, 0)):
        for k in range(cnt):
            a = 2 * math.pi * k / cnt + off + 0.02 * math.sin(t * 2 + k)
            w = 0.09 if ring else 0.12
            p = [(cx + r0 * math.cos(a - w), cy + r0 * math.sin(a - w)), (cx + (r0 + r1) / 2 * math.cos(a - w * 0.9), cy + (r0 + r1) / 2 * math.sin(a - w * 0.9)),
                 (cx + r1 * math.cos(a), cy + r1 * math.sin(a)), (cx + (r0 + r1) / 2 * math.cos(a + w * 0.9), cy + (r0 + r1) / 2 * math.sin(a + w * 0.9)),
                 (cx + r0 * math.cos(a + w), cy + r0 * math.sin(a + w))]
            d.polygon(p, fill=col, outline=shade(col, 0.72))
            if ring: d.line([p[0], p[2]], fill=(255, 232, 120))
    d.ellipse([cx - 41, cy - 41, cx + 41, cy + 41], fill=(70, 40, 18), outline=(120, 74, 30))
    d.ellipse([cx - 39, cy - 39, cx + 39, cy + 39], outline=(54, 30, 14))
    cc = 38 / math.sqrt(420)
    ga = math.radians(ang_deg)
    for k in range(1, n + 1):
        r = cc * math.sqrt(k); a = k * ga
        x, y = int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a)))
        base = (150, 98, 42) if k % 3 else (120, 76, 30)
        d.rectangle([x, y, x + 1, y + 1], fill=base)
        d.point((x, y), fill=(206, 150, 70))

def sc_vogel(t, T):
    c = Ctx("garden")
    # clouds
    for i, (cx, cy, w) in enumerate(((30, 40, 26), (140, 26, 34), (100, 70, 20))):
        x = (cx + t * (2 + i)) % (AW + 40) - 20
        for dx, dy, r in ((0, 0, 1), (w * 0.3, -4, 1.2), (w * 0.6, 0, 1)):
            c.a.ellipse([x + dx - 6 * r, cy + dy - 4 * r, x + dx + 6 * r, cy + dy + 4 * r], fill=(240, 246, 250))
        c.a.line([x - 6, cy + 4, x + w * 0.6 + 6, cy + 4], fill=(200, 216, 230))
    phases = [(0.0, 135.0, "135.0°"), (2.6, 137.0, "137.0°"), (5.2, 360 / 1.6180339887 ** 2, "137.5°")]
    ph = [p for p in phases if t >= p[0]][-1]
    lt = t - ph[0]
    n = int(420 * eout(lt / (1.9 if ph[1] != phases[-1][1] else 2.6)))
    sunflower(c, t, ph[1], n, t * 1.3)
    good = ph[2] == "137.5°"
    cols = digit_cols(ph[2][:-1], "137.5") + [CREAM if good else RED]
    if good: cols = [CREAM] * 6
    panel(c.t, "VOGEL 1979", ph[2], "360° / φ² = 137.5°" if good else "SEED ANGLE", cols, right=["SEEDS", str(n)], age=lt)
    cap = None
    if not good and n > 300: cap, cc = ("GAPS!" if ph[1] == 137.0 else "SPOKES!"), RED
    if good and lt > 2.8: cap, cc = "PERFECT PACKING", CREAM
    if cap:
        w = 8 * len(cap) + 16
        c.t.rectangle([180 - w / 2, 486, 180 + w / 2, 508], fill=(40, 26, 18)); c.t.rectangle([180 - w / 2, 486, 180 + w / 2, 487], fill=(110, 76, 50))
        text(c.t, 180, 486, cap, fill=cc, align="c")
    return c

def monitor(c, t, nidx):
    d = c.a
    x0, y0, x1, y1 = 26, 92, 154, 206
    d.rectangle([x0 + 3, y0 + 3, x1 + 3, y1 + 3], fill=(0, 4, 2))
    d.rectangle([x0, y0, x1, y1], fill=(196, 186, 156), outline=(90, 84, 70))
    d.line([x0 + 1, y0 + 1, x1 - 1, y0 + 1], fill=(232, 226, 200)); d.line([x0 + 1, y0 + 1, x0 + 1, y1 - 1], fill=(220, 212, 186))
    d.line([x0 + 1, y1 - 1, x1 - 1, y1 - 1], fill=(140, 132, 108))
    sx0, sy0, sx1, sy1 = x0 + 8, y0 + 8, x1 - 8, y1 - 18
    d.rectangle([sx0 - 2, sy0 - 2, sx1 + 2, sy1 + 2], fill=(110, 104, 86))
    d.rectangle([sx0, sy0, sx1, sy1], fill=(8, 26, 14))
    for y in range(sy0, sy1, 2): d.line([sx0, y, sx1, y], fill=(6, 20, 11))
    d.rectangle([x1 - 22, y1 - 12, x1 - 10, y1 - 8], fill=(60, 56, 46)); d.point((x1 - 30, y1 - 10), fill=(90, 230, 120))
    # stand + keyboard
    d.rectangle([76, y1 + 1, 104, y1 + 8], fill=(150, 142, 118)); d.rectangle([60, y1 + 8, 120, y1 + 11], fill=(170, 162, 136))
    kx0, ky0 = 22, y1 + 16
    d.rectangle([kx0, ky0, 158, ky0 + 22], fill=(186, 176, 146), outline=(90, 84, 70))
    for r in range(3):
        for k in range(14):
            kx, ky = kx0 + 4 + k * 9, ky0 + 4 + r * 6
            pressed = (DIGITS[nidx % len(DIGITS)] + r * 3) % 14 == k and r == 0
            d.rectangle([kx, ky + (1 if pressed else 0), kx + 6, ky + 4], fill=(230, 222, 196) if not pressed else (200, 190, 160), outline=(120, 112, 92))
    # screen digits (text layer, 2x coords)
    W = c.t
    per = 14
    rows_vis = 7
    shown = nidx + 2
    first_row = max(0, shown // per - rows_vis + 1)
    for rr in range(rows_vis):
        row = first_row + rr
        s = PHI.replace(".", "")[row * per:(row + 1) * per]
        for j, ch in enumerate(s):
            i = row * per + j
            if i >= shown: break
            col = GREEN_HI if i == shown - 1 else GREEN
            text(W, sx0 * 2 + 8 + j * 8 + (0 if j < per // 2 else 4), sy0 * 2 + 6 + rr * 20, ch, fill=col)
    if int(t * 4) % 2 == 0:
        i = shown % per; rr = min(rows_vis - 1, shown // per - first_row)
        W.rectangle([sx0 * 2 + 8 + i * 8, sy0 * 2 + 22 + rr * 20, sx0 * 2 + 14 + i * 8, sy0 * 2 + 23 + rr * 20], fill=GREEN_HI)

def sc_digits(t, T, t_abs, total_notes):
    c = Ctx("term")
    nidx = int(t_abs / NOTE)
    monitor(c, t, nidx)
    W = c.t
    # ticker
    W.rectangle([40, 494, 320, 540], fill=(4, 10, 6)); W.rectangle([40, 494, 320, 540], outline=(50, 130, 80))
    W.rectangle([42, 496, 318, 538], outline=(20, 60, 36))
    s = PHI.replace(".", "")
    for j in range(16):
        i = nidx - 12 + j
        if 0 <= i < len(s):
            text(W, 52 + j * 16, 496, s[i], size=40, fill=CREAM if j == 12 else (70, 170, 100) if j < 12 else (24, 70, 40))
    cnt = min(total_notes, nidx + 1)
    panel(c.t, "THIS VIDEO 2026", f"{cnt} DIGITS", "OF φ = EVERY NOTE YOU HEARD", [CREAM] * 20, style="green", sub_col=GREEN)
    # noise-out glitch at the end
    g = (t - (T - 0.7)) / 0.7
    if g > 0:
        rng = np.random.default_rng(int(t * 1000))
        a = np.array(c.art)
        m = rng.random((AH, AW)) < ease(g)
        pal = np.array([(40, 90, 110), (60, 130, 120), (30, 60, 100), (100, 160, 120)], np.uint8)
        a[m] = pal[rng.integers(0, 4, m.sum())]
        c.art = Image.fromarray(a)
        if g > 0.6: c.txt = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); c.t = ImageDraw.Draw(c.txt); c.t.fontmode = "1"; panel(c.t, "THIS VIDEO 2026", f"{cnt} DIGITS", "OF φ", [CREAM] * 20, style="green", sub_col=GREEN, age=0.05)
    return c

def sc_outro(t, T):
    c = Ctx("grid")
    lines = ["1.61803398", "87498948", "48204586", "83436563"]
    for i, l in enumerate(lines):
        q = (t - i * 0.25) / 0.25
        if q > 0: text(c.t, 44, 120 + i * 40, l, size=40, fill=CREAM if i == 0 else mix((40, 50, 80), CREAM, min(1, q) * (1 - i * 0.18)))
    number_line(c, 1.6180339887)
    text(c.t, 180, 470, "φ  =  (1 + √5) / 2".replace("√", "V"), fill=DIM, align="c") if False else None
    return c

# ---------------- timeline ----------------
SCENES = [("intro", sc_intro, 4.0), ("euclid", sc_euclid, 8.0), ("fib", sc_fib, 9.0), ("hurwitz", sc_hurwitz, 7.0),
          ("vogel", sc_vogel, 9.0), ("digits", sc_digits, 6.0), ("outro", sc_outro, 4.5)]
TOTAL = sum(s[2] for s in SCENES)
TOTAL_NOTES = int((TOTAL - 1.5) / NOTE)

def starts():
    out, acc = {}, 0.0
    for name, fn, dur in SCENES: out[name] = acc; acc += dur
    return out
START = starts()

def compose(c, t, scene_idx):
    art = np.array(c.art)
    if scene_idx > 0 and t < 0.12:  # cut glitch
        rng = np.random.default_rng(int(t * 1000) + scene_idx)
        for _ in range(6):
            y = rng.integers(0, AH - 10); h = rng.integers(2, 12)
            art[y:y + h] = np.roll(art[y:y + h], rng.integers(-20, 20), axis=1)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt)
    tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    out = big * (1 - al) + tb[..., :3] * al
    return out.astype(np.uint8)

def render_frame(idx, t):
    name, fn, dur = SCENES[idx]
    if name == "digits": c = fn(t, dur, START[name] + t, TOTAL_NOTES)
    else: c = fn(t, dur)
    fr = compose(c, t, idx)
    if name == "outro":
        f = ease((t - (dur - 0.9)) / 0.9)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

def render_scene(args):
    idx, out = args
    name, fn, dur = SCENES[idx]
    tmp, fin = f"{out}/{idx}_{name}.tmp.mp4", f"{out}/{idx}_{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))):
        p.stdin.write(render_frame(idx, f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin)
    return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "preview":
        shots = [tuple(x.split(":")) for x in sys.argv[3:]]
        for name, tt in shots:
            idx = [s[0] for s in SCENES].index(name)
            Image.fromarray(render_frame(idx, float(tt))).resize((540, 960), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, s in enumerate(SCENES) if not only or s[0] in only]
        with Pool(min(6, os.cpu_count() or 2)) as pool:
            print(pool.map(render_scene, [(i, out) for i in idxs]))
