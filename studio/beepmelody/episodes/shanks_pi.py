"""BEEPMELODY — SHANKS PI : « A man spent years on 707 digits of pi. The last 180 were wrong. »
Co-pilote : étape 1 = titre A (bureau de Shanks, rouleau qui vire au rouge à 528) ; étape 2 = C « Machine à calculer »
(128 BPM, clic mécanique + pluck synthé = la plume de Shanks, pluck clair = le vrai pi, kick 4/4 ; à 528 la batterie
se coupe sur un buzz ; ensuite les chiffres faux = buzz carré saturé, le vrai pi reste propre ; chiffres justes par hasard = cloche dorée).
Données : shanks_pi.csv (707 décimales, Shanks 1873 vs vrai pi). Une décimale = un coup par voix, sur son instant.
Acte 1 : décimales 1-527 à 15 / s (unisson). 528 : arrêt (1 s). Acte 2 : 529-707 à ~8,2 / s. Outro : bilan + 1946 + sources.

    python3 shanks_pi.py info out | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE); sys.path.insert(0, HERE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.6"))

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "shanks_pi.csv"))))
SH = [int(r["shanks"]) for r in ROWS]; TR = [int(r["true"]) for r in ROWS]
ND = len(ROWS); assert ND == 707

def machin(n):                      # true pi, integer Machin formula, n decimals (+guard)
    g = 10; s = 10 ** (n + g)
    def at(x):
        t = s // x; tot = t; k = 1; x2 = x * x; sg = -1
        while t:
            t //= x2; tot += sg * (t // (2 * k + 1)); sg = -sg; k += 1
        return tot
    p = 4 * (4 * at(5) - at(239)); return str(p)[1:n + 1]
assert "".join(map(str, TR)) == machin(ND), "true-pi column mismatch"
FIRST_WRONG = next(i for i in range(ND) if SH[i] != TR[i]) + 1
assert FIRST_WRONG == 528 and SH[527] == 5 and TR[527] == 4
LUCKY = [i + 1 for i in range(527, ND) if SH[i] == TR[i]]
assert len(LUCKY) == 17 and ND - 527 - len(LUCKY) == 163

TD0, R1, R2 = 0.6, 15.0, 8.2
T = np.zeros(ND)
for i in range(527): T[i] = TD0 + i / R1
T528 = T[526] + 1 / R1 + 0.2
T[527] = T528
for i in range(528, ND): T[i] = T528 + 1.0 + (i - 528) / R2
OUTRO0 = T[-1] + 0.55; OUTRO = 8.0
TOTAL = OUTRO0 + OUTRO
CHUNKS = [("a", 0.0, 12.0), ("b", 12.0, 24.0), ("c", 24.0, T528 - 0.5), ("d", T528 - 0.5, 48.0), ("e", 48.0, OUTRO0), ("outro", OUTRO0, TOTAL)]

def n_at(Tt): return int(np.searchsorted(T, Tt, side="right"))

# ================= look (clear amber / parchment) =================
BG0, BG1 = (232, 214, 182), (204, 176, 136)
WOOD, WOOD2, WOOD3 = (128, 84, 52), (104, 66, 40), (150, 102, 64)
PAPER, PAPER_RED = (246, 236, 212), (246, 196, 184)
PAPERL = (220, 204, 176)
SCREEN, SCREEN2 = (22, 30, 34), (40, 54, 58)
PANEL = (255, 250, 240); INK = (44, 36, 30); INK2 = (120, 104, 88)
GOLD = (204, 136, 24); RED = (214, 52, 44); GREEN = (40, 150, 80); SGREEN = (120, 236, 150)
DIM = (186, 172, 150); WHITE = (255, 255, 255)
def mixc(a, b, f): return tuple(int(x * (1 - f) + y * f) for x, y in zip(a, b))
PAL = os.environ.get("SP_PAL", "day")                     # day (default, clear parchment) | night (candle-lit study)
if PAL == "night":
    BG0, BG1 = (30, 26, 40), (52, 40, 44)
    WOOD, WOOD2, WOOD3 = (72, 46, 30), (56, 34, 22), (96, 64, 40)
    PAPER, PAPER_RED = (214, 196, 160), (220, 150, 136); PAPERL = (180, 160, 128)
    PANEL = (22, 20, 30); INK = (240, 228, 204); INK2 = (170, 156, 136)
    GOLD = (246, 186, 64); RED = (250, 92, 80); GREEN = (110, 214, 130); DIM = (90, 84, 96)

PER = 20; NROWS = 8
ROW_Y0 = 268; ROW_DY = 26; COL_X0 = 60; COL_DX = 14.2
PX0, PX1, PY0, PY1 = 12, 172, 126, 238      # paper in art px (text = x2)

def gradient():
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        f = y / AH; a[y, :] = [BG0[k] * (1 - f) + BG1[k] * f for k in range(3)]
    return a.astype(np.uint8)
_G = gradient()

def red_f(Tt):
    if Tt < T528: return 0.0
    return min(1.0, 0.25 + 0.75 * (Tt - T528) / (T[-1] - T528))

def draw_desk(c, Tt):
    img = Image.fromarray(_G.copy()); d = ImageDraw.Draw(img)
    d.rectangle([0, 236, AW, AH], fill=WOOD)
    for y in range(240, AH, 7): d.line([0, y, AW, y + 2], fill=WOOD2)
    d.rectangle([0, 236, AW, 238], fill=WOOD3)
    # paper (tints red after 528)
    pc = mixc(PAPER, PAPER_RED, 0.75 * red_f(Tt))
    d.rectangle([PX0, PY0, PX1, PY1 + 8], fill=pc)
    d.rectangle([PX0 - 2, PY1 + 6, PX1 + 2, PY1 + 12], fill=PAPERL)          # roll at the bottom
    d.line([PX0 - 2, PY1 + 9, PX1 + 2, PY1 + 9], fill=mixc(PAPERL, INK, .2))
    for y in range(PY0 + 4, PY1, 13): d.line([PX0 + 2, y + 9, PX1 - 2, y + 9], fill=mixc(pc, PAPERL, .5))
    # screen with the true pi
    d.rectangle([8, 98, 172, 122], fill=SCREEN2); d.rectangle([10, 100, 170, 120], fill=SCREEN)
    # inkwell + candle on the desk
    d.rectangle([150, 252, 166, 266], fill=(40, 40, 56)); d.rectangle([154, 248, 162, 252], fill=(60, 60, 80))
    d.rectangle([18, 248, 24, 270], fill=(236, 228, 200)); d.rectangle([14, 270, 28, 274], fill=(170, 140, 60))
    fl = 2 + int(2 * abs(math.sin(Tt * 9.1)))
    d.ellipse([19, 242 - fl, 23, 248], fill=(255, 196, 70)); d.point((21, 245), fill=(255, 250, 220))
    c.art = img; c.a = ImageDraw.Draw(img)

def row_scroll(n):
    """index of the first visible row + sub-row scroll offset (smooth after a new row starts)."""
    cur = max(0, (n - 1) // PER) if n else 0
    first = max(0, cur - NROWS + 1)
    off = 0.0
    if first > 0:
        i0 = cur * PER                                    # first digit of current row
        age = (TNOW[0] - T[i0]) if i0 < ND else 1
        if age < 0.18: off = ROW_DY * (1 - ease(age / 0.18))
    return cur, first, off
TNOW = [0.0]

PINK = (44, 36, 30)
def dcol(i):
    if i < 527: return PINK
    return GOLD if SH[i] == TR[i] else RED

def draw_paper(c, Tt, n):
    W = c.t; cur, first, off = row_scroll(n)
    for r in range(first, cur + 1):
        y = ROW_Y0 + (r - first) * ROW_DY + off
        if y > ROW_Y0 + (NROWS - 1) * ROW_DY + 2: continue
        lab = "3." if r == 0 else str(r * PER + 1)
        text(W, COL_X0 - 10, y, lab, fill=DIM, align="r")
        for k in range(PER):
            i = r * PER + k
            if i >= n: break
            text(W, COL_X0 + k * COL_DX, y, str(SH[i]), fill=dcol(i))
    # quill at the last written digit
    if 0 < n <= ND and Tt < OUTRO0:
        i = n - 1; r = i // PER; k = i % PER
        x = (COL_X0 + k * COL_DX + 10) / 2; y = (ROW_Y0 + (r - first) * ROW_DY + off + 14) / 2
        bob = 1.5 * math.exp(-(Tt - T[i]) / 0.05)
        d = c.a; y -= bob
        d.line([x, y, x + 12, y - 16], fill=(70, 60, 60))
        d.polygon([(x + 5, y - 7), (x + 16, y - 24), (x + 20, y - 22), (x + 10, y - 6)], fill=(250, 250, 244))
        d.line([x + 7, y - 8, x + 17, y - 22], fill=(200, 196, 190))
        d.point((x, y), fill=(20, 20, 30))
    return cur

def draw_screen(c, Tt, n, cur):
    W = c.t
    text(W, 28, 202, "TRUE PI", fill=(110, 160, 130))
    if n == 0: return
    r = (n - 1) // PER
    for k in range(PER):
        i = r * PER + k
        if i >= n: break
        col = SGREEN
        if i >= 527 and SH[i] != TR[i]: col = (255, 120, 110) if i == n - 1 and Tt - T[i] < 0.12 else SGREEN
        x = COL_X0 + k * COL_DX
        if i == n - 1 and Tt - T[i] < 0.12: W.rectangle([x - 2, 218, x + 9, 236], fill=(50, 90, 70))
        text(W, x, 218, str(TR[i]), fill=col)
    flash = (T528 <= Tt < T528 + 1.0)
    if flash and int((Tt - T528) * 8) % 2 == 0:
        W.rectangle([20, 200, 340, 240], outline=RED, width=2)

def top(c, Tt, n):
    W = c.t
    W.rectangle([16, 18, 344, 150], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=GOLD); W.rectangle([16, 149, 344, 150], fill=GOLD)
    if Tt < 2.9:                                          # hook
        text(W, 180, 26, "707 DIGITS OF PI", size=40, fill=INK, align="c")
        if Tt > 0.25: text(W, 180, 66, "BY HAND.", size=40, fill=INK, align="c")
        if Tt > 0.9: text(W, 180, 110, "THE LAST 180 WERE WRONG.", fill=RED, align="c")
        return
    text(W, 28, 24, "WILLIAM SHANKS", fill=GOLD); text(W, 334, 24, "1873", fill=GOLD, align="r")
    text(W, 28, 44, "PI, WORKED OUT BY HAND", fill=INK)
    fresh = n and Tt - T[n - 1] < 0.07
    wrong_now = n > 527
    big = f"DIGIT {min(n, ND)}" if n else "DIGIT 0"
    text(W, 180, 68, big, size=40, fill=(RED if (wrong_now and fresh and SH[n-1] != TR[n-1]) else (GOLD if fresh else INK)), align="c")
    if n < 528: sub, col = "ALL CORRECT SO FAR", GREEN
    else:
        sub, col = "OFF TRACK SINCE DIGIT 528", RED
    text(W, 180, 116, sub, fill=col, align="c")

def rule(c):
    W = c.t
    W.rectangle([16, 156, 344, 196], fill=PANEL)
    text(W, 180, 158, "EVERY BEEP = ONE DIGIT", fill=GOLD, align="c")
    text(W, 180, 176, "PAPER: SHANKS · SCREEN: TRUE PI", fill=INK2, align="c")

def strip(c, Tt, n):
    W = c.t
    W.rectangle([0, 520, 360, 640], fill=PANEL); W.rectangle([0, 520, 360, 521], fill=GOLD)
    text(W, 16, 528, "HIS 707 DIGITS", fill=INK2)
    nr = min(n, 527); nw = sum(1 for i in range(527, n) if SH[i] != TR[i]); nl = sum(1 for i in range(527, n) if SH[i] == TR[i])
    x0, x1, y0, y1 = 16, 344, 552, 568
    W.rectangle([x0, y0, x1, y1], fill=(236, 226, 206))
    for i in range(n):
        xa = x0 + (x1 - x0) * i / ND; xb = x0 + (x1 - x0) * (i + 1) / ND
        col = GREEN if i < 527 else (GOLD if SH[i] == TR[i] else RED)
        W.rectangle([int(xa), y0, max(int(xa), int(xb) - 0), y1], fill=col)
    xm = x0 + (x1 - x0) * 527 / ND
    W.line([xm, y0 - 4, xm, y1 + 2], fill=INK)
    text(W, x0, 572, "1", fill=INK2); text(W, xm, 572, "528", fill=INK, align="c"); text(W, x1, 572, "707", fill=INK2, align="r")
    text(W, 16, 600, f"RIGHT {nr}", fill=GREEN)
    text(W, 180, 600, f"WRONG {nw + nl}", fill=RED if nw else DIM, align="c")
    text(W, 344, 600, f"BY LUCK {nl}", fill=GOLD if nl else DIM, align="r")

def banner(c, big, small, col=None, small2=None):
    W = c.t; yb = 300; w = 316; h = 72 if not small2 else 90
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + h], fill=PANEL); W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col or GOLD)
    W.rectangle([180 - w / 2, yb + h - 1, 180 + w / 2, yb + h], fill=col or GOLD)
    text(W, 180, yb + 8, big, size=40, fill=col or GOLD, align="c")
    text(W, 180, yb + 50, small, fill=INK, align="c")
    if small2: text(W, 180, yb + 68, small2, fill=INK2, align="c")

BANNERS = [  # (t0, t1, big, small, col, small2)
    (T[99] + 0.05, T[99] + 1.6, "100 DIGITS", "ALL CORRECT", GREEN, None),
    (T[219], T[219] + 2.4, "20+ YEARS", "OF WORK, PEN AND PAPER", GOLD, None),
    (T[379], T[379] + 2.4, "1853: 607 DIGITS", "1873: HE PUSHED ON TO 707", GOLD, None),
    (T[499] + 0.05, T[499] + 1.5, "500 DIGITS", "STILL PERFECT", GREEN, None),
    (T528, T528 + 1.7, "DIGIT 528", "HE WROTE 5. PI SAYS 4.", RED, None),
    (T[540] + 0.1, T[540] + 2.6, "OFF TRACK", "EVERY DIGIT FROM HERE ON", RED, "GOLD = MATCHES PI BY PURE LUCK"),
    (T[620], T[620] + 2.8, "THE CAUSE", "ONE SKIPPED TERM", RED, "IN HIS SUM, NEAR DIGIT 530"),
]

def outro(c, Tt):
    t = Tt - OUTRO0; W = c.t
    W.rectangle([16, 18, 344, 512], fill=PANEL); W.rectangle([16, 18, 344, 20], fill=GOLD); W.rectangle([16, 510, 344, 512], fill=GOLD)
    text(W, 180, 30, "707 DIGITS BY HAND", size=40, fill=INK, align="c")
    if t > 0.3: text(W, 180, 82, "527 RIGHT", size=40, fill=GREEN, align="c")
    if t > 0.8: text(W, 180, 126, "180 WRONG", size=40, fill=RED, align="c")
    if t > 1.2: text(W, 180, 170, "(17 OF THEM MATCH PI BY LUCK)", fill=GOLD, align="c")
    if t > 2.0:
        text(W, 180, 214, "NOBODY NOTICED FOR 73 YEARS.", fill=INK, align="c")
        text(W, 180, 236, "1946: D. F. FERGUSON CHECKS IT", fill=INK, align="c")
        text(W, 180, 254, "ON A DESK CALCULATOR", fill=INK, align="c")
    if t > 3.2: text(W, 180, 300, "WOULD YOU HAVE CAUGHT IT?", fill=GOLD, align="c")
    if t > 2.6:                                           # the spot where it broke: decimals 521-535
        text(W, 40, 336, "SHANKS", fill=INK2); text(W, 40, 360, "PI", fill=INK2)
        for k, i in enumerate(range(520, 535)):
            x = 112 + k * 14; hl = (i == 527)
            if hl: W.rectangle([x - 3, 332, x + 10, 380], outline=RED, width=1)
            text(W, x, 336, str(SH[i]), fill=INK if i < 527 else dcol(i)); text(W, x, 360, str(TR[i]), fill=GREEN)
        text(W, 112 + 7 * 14 + 3, 384, "528", fill=RED, align="c")
    if t > 3.8:
        text(W, 180, 424, "DATA: W. SHANKS, PROC. R. SOC. 21 (1873)", fill=INK2, align="c")
        text(W, 180, 442, "D. F. FERGUSON, MATH. GAZETTE (1946)", fill=INK2, align="c")
        text(W, 180, 460, "WRENCH, MTAC 2 (1947) · MACTUTOR", fill=INK2, align="c")
        text(W, 180, 478, "B. HAYES, AMERICAN SCIENTIST (2014)", fill=INK2, align="c")

def scene(Tt):
    TNOW[0] = Tt
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    n = n_at(min(Tt, OUTRO0))
    draw_desk(c, Tt)
    if Tt < OUTRO0:
        cur = draw_paper(c, Tt, n)
        draw_screen(c, Tt, n, cur)
        top(c, Tt, n); rule(c)
        for t0, t1, b, s, col, s2 in BANNERS:
            if t0 <= Tt < t1: banner(c, b, s, col, s2)
    else:
        draw_paper(c, Tt, ND); outro(c, Tt)
    strip(c, Tt, n)
    return c

def compose_layers(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tb = np.repeat(np.repeat(np.array(c.txt), 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

BPM = 128; BEAT = 60 / BPM
BEATS = np.arange(0, TOTAL + BEAT, BEAT)
def in_gap(t): return T528 - 0.15 <= t < T528 + 0.95
def render_frame(Tt):
    random.seed(int(Tt * 1000))
    fr = compose_layers(scene(Tt))
    if Tt < OUTRO0 and not in_gap(Tt):
        bi = int(np.searchsorted(BEATS, Tt, side="right")) - 1
        kp = math.exp(-(Tt - BEATS[bi]) / 0.08)
        z = 1.0 + 0.008 * kp * FXK
        if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    a = Tt - T528
    if 0 <= a < 0.5:                                      # digit 528: red flash + shake
        k = 1 - a / 0.5
        fr = warp(fr, 1.0, int(18 * k * math.sin(a * 90) * FXK), 0)
        tint = np.array([255, 40, 30], np.float32)
        fr = (fr * (1 - 0.35 * k * FXK) + tint * 0.35 * k * FXK).astype(np.uint8)
    f = ease((Tt - (TOTAL - 0.8)) / 0.8)
    if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    f = 1 - ease(Tt / 0.2)
    if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    return fr

# ================= audio (choice C « Machine à calculer », from shanks_pi_moods.py mood_c, full length) =================
SR = 44100
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    N = int((TOTAL + 0.3) * SR)
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def mix(*ss):
        n = max(len(x) for x in ss); o = np.zeros(n)
        for x in ss: o[:len(x)] += x
        return o
    def put(L, t0, s, g=1.0):
        i = int(t0 * SR)
        if i >= N or i < 0: return
        j = min(N, i + len(s)); L[i:j] += g * s[:j - i]
    def env(n, a, dec): tt = np.arange(n) / SR; return np.minimum(1, tt / a) * np.exp(-tt / dec)
    def tone(f, dur, dec, harm=((1, 1),), a=.002, cents=0.0):
        n = int(dur * SR); tt = np.arange(n) / SR; f = f * 2 ** (cents / 1200)
        return sum(g * np.sin(h * 2 * np.pi * f * tt) for h, g in harm) * env(n, a, dec)
    rs = np.random.RandomState(7)
    def noise(dur, dec, f=None, hi=True):
        n = int(dur * SR); s = rs.randn(n) * np.exp(-np.arange(n) / SR * dec)
        return (hp(s, f) if hi else lp(s, f)) if f else s
    def kick(g, f0=80, f1=45, dec=13):
        m = int(.3 * SR); tt = np.arange(m) / SR
        return g * np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 18) + f1) / SR) * np.exp(-tt * dec)
    SCALE = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]
    ROOT = 62
    L = np.zeros(N); B = np.zeros(N)
    roots = [38, 38, 34, 36]
    T_OFF = OUTRO0 + 0.1
    for k, b in enumerate(BEATS):
        if b >= T_OFF: break
        put(B, b, kick(.34 * (0.8 if b < 2.9 else 1))); put(B, b + BEAT / 2, .05 * noise(.04, 90, 6500))
        if k % 2: put(B, b, .06 * noise(.14, 26, 2800))
        r = roots[(k // 4) % 4]; n = int(.22 * SR); tt = np.arange(n) / SR
        put(B, b + BEAT / 2, .09 * lp(np.sign(np.sin(2 * np.pi * mtof(r) * tt)), 500) * np.exp(-tt * 9))
    m = np.ones(N); a_, b_ = int((T528 - .15) * SR), int((T528 + .95) * SR)
    m[a_:b_] = 0.0; rr = int(.08 * SR); m[a_ - rr:a_] = np.linspace(1, 0, rr); m[b_:b_ + rr] = np.linspace(0, 1, rr)
    B *= m
    click = lambda: .05 * noise(.012, 400, 3000)
    pl = lambda f: mix(.09 * lp(tone(f, .22, .07, ((1, 1), (2, .5), (3, .33), (4, .25)), .001), 4000), click())
    tru = lambda f: .07 * tone(f * 2, .25, .08, ((1, 1), (2, .2)), .001)
    def wrong(f):
        n = int(.2 * SR); tt = np.arange(n) / SR
        return mix(.07 * np.tanh(3 * np.sign(np.sin(2 * np.pi * f * 2 ** (50 / 1200) * tt))) * np.exp(-tt * 14), click())
    lucky = lambda f: .06 * tone(f * 4, .6, .3, ((1, 1), (2.76, .3)), .001)
    split = lambda fs, ft: mix(.9 * wrong(fs), .12 * tone(ft * 2, .8, .3, ((1, 1),), .001), kick(.3, 60, 35, 6))
    cache = {}
    def get(key, fn, *a):
        if key not in cache: cache[key] = fn(*a)
        return cache[key]
    for i in range(ND):
        s, tr = SH[i], TR[i]; fs, ft = mtof(ROOT + SCALE[s]), mtof(ROOT + SCALE[tr])
        if i < 527:
            put(L, T[i], mix(pl(fs), get(("t", tr), tru, ft)))
        elif i == 527:
            put(L, T[i], split(fs, ft))
        elif s == tr:
            put(L, T[i], mix(pl(fs), get(("t", tr), tru, ft), get(("l", tr), lucky, ft)))
        else:
            put(L, T[i], mix(wrong(fs), get(("t", tr), tru, ft)))
    # outro: drums stop, a calm chord (D major add9) + a ding on « 1946 »
    for q, mm in enumerate([38, 50, 54, 57, 64, 66]):
        n = int(4.5 * SR); tt = np.arange(n) / SR
        put(L, OUTRO0 + 0.05 + q * 0.06, .045 * lp(np.sign(np.sin(2 * np.pi * mtof(mm) * tt)), 1600) * np.minimum(1, tt / .02) * np.exp(-tt * .7))
    def ding(t0, g=.12):
        n = int(1.0 * SR); tt = np.arange(n) / SR
        put(L, t0, g * (np.sin(2 * np.pi * 1568 * tt) + .4 * np.sin(2 * np.pi * 2349 * tt)) * np.exp(-tt * 4))
    ding(OUTRO0 + 2.0, .1); ding(OUTRO0 + 3.2, .07)
    x = L + B
    x = np.tanh(x * 1.4) / 1.4
    o = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
        q = int(d * .9 * SR); o[q:] += g * .6 * x[:-q]
    x = .85 * x + .15 * lp(o, 4500)
    tt = np.arange(N) / SR
    x *= np.clip((TOTAL + 0.1 - tt) / 1.2, 0, 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(N / SR, 2), "s")

def render_chunk(args):
    idx, out = args; name, a, b = CHUNKS[idx]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    f0, f1 = int(round(a * FPS)), int(round(b * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(render_frame(f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio": render_audio(out); sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "at":
        for x in sys.argv[3:]:
            Tt = float(x); Image.fromarray(render_frame(Tt)).resize((540, 960), Image.LANCZOS).save(f"{out}/t{Tt:05.2f}.png")
    elif mode == "info":
        print("total", round(TOTAL, 2), "s · digits", ND, "· first wrong", FIRST_WRONG, "· wrong", ND - 527 - len(LUCKY), "· lucky", LUCKY)
        print("528 at", round(T528, 2), "· 707 at", round(T[-1], 2), "· outro", round(OUTRO0, 2))
        for b in BANNERS: print("banner", round(b[0], 2), "->", round(b[1], 2), b[2], "/", b[3])
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        with Pool(min(3, os.cpu_count() or 2)) as pool: print(pool.map(render_chunk, [(i, out) for i in range(len(CHUNKS))]))
