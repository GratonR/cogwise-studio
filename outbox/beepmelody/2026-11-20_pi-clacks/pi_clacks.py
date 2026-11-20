"""BEEPMELODY — TWO BLOCKS. 314,159 COLLISIONS. LISTEN.
A small block (1 kg) sits between a wall and a big block sliding towards it. Ideal physics: no friction, no energy lost.
Count every collision (block-block AND small block-wall). Make the big block 100x heavier each level and the count
spells pi: 3 · 31 · 314 · 3,141 · 31,415 · 314,159 (G. Galperin 2003; exact simulation below, clack by clack).
Every collision = one audible click, at its own instant. The clacks of a level all happen within a few physics
seconds, so each level is played in slow motion around its busy moment: tau = asinh((t - 2) / w), w = 1/sqrt(ratio)
(same warp for every clack of a level, order and spacing kept; the screen says "SLOW MOTION").
Music (co-pilot step 2, choice B "Compteur mecanique"): 120 BPM kick/hat/bass bed, every clack = dry metal click,
big hit + crash on the first clack of each level, bed drops out at the end.
Palette: PC_PAL=dark (default, amber counter) | light (clear, like THE RACE TO THE SKY).

    python3 pi_clacks.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.6"))
PAL = os.environ.get("PC_PAL", "dark")

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "pi_clacks.csv"))))[:6]
NL = len(ROWS)

def sim(r):
    """exact event-driven simulation: point blocks, small m=1 at x=1 (still), big M=r at x=2 moving at -1, wall at 0."""
    m, M = 1.0, float(r); x1, x2, v1, v2, t = 1.0, 2.0, 0.0, -1.0, 0.0
    T, K, X1, X2, V1, V2 = [], [], [], [], [], []
    while True:
        tb = (x2 - x1) / (v1 - v2) if v1 > v2 else math.inf
        tw = -x1 / v1 if v1 < 0 else math.inf
        if tb == math.inf and tw == math.inf: break
        if tb < tw:
            dt = tb; x1 += v1 * dt; x2 = x1
            v1, v2 = ((m - M) * v1 + 2 * M * v2) / (m + M), ((M - m) * v2 + 2 * m * v1) / (m + M); k = 0
        else:
            dt = tw; x1 = 0.0; x2 += v2 * dt; v1 = -v1; k = 1
        t += dt; T.append(t); K.append(k); X1.append(x1); X2.append(x2); V1.append(v1); V2.append(v2)
        if v1 >= 0 and v2 >= v1: break
    return dict(T=np.array(T), K=np.array(K, np.int8), X1=np.array(X1), X2=np.array(X2), V1=np.array(V1), V2=np.array(V2))

LV = []
for row in ROWS:
    r = int(row["mass_ratio"]); s = sim(r)
    assert len(s["T"]) == int(row["collisions"]), (r, len(s["T"]), row["collisions"])
    LV.append(dict(r=r, n=len(s["T"]), digits=row["pi_digits"], label=row["mass_ratio_label"], **s))

# ================= timeline (120 BPM: every block is a whole number of beats) =================
BEAT = 0.5
INTRO = 4.0
SETUP, HOLD = 1.5, 2.0
WIN = [2.0, 3.0, 4.0, 5.0, 6.0, 11.0]                  # slow-motion clack window per level (display seconds)
OUTRO = 9.5
SC = [("intro", INTRO)]
for i in range(NL): SC.append((f"l{i + 1}", SETUP + WIN[i] + HOLD))
SC.append(("outro", OUTRO))
DUR = dict(SC); NAMES = [n for n, _ in SC]
START = {}; _a = 0.0
for n, d in SC: START[n] = _a; _a += d
TOTAL = _a

def warp_params(L):
    w = 1 / math.sqrt(L["r"]); A0 = math.asinh((L["T"][0] - 2) / w); A1 = math.asinh((L["T"][-1] - 2) / w)
    return w, A0, A1
for i, L in enumerate(LV):
    w, A0, A1 = warp_params(L); L["w"], L["A0"], L["A1"] = w, A0, A1
    tau = (np.arcsinh((L["T"] - 2) / w) - A0) / (A1 - A0)
    L["start"] = START[f"l{i + 1}"]; L["c0"] = L["start"] + SETUP
    L["disp"] = L["c0"] + tau * WIN[i]                  # display time of every clack (audio uses this)

def phys_t(i, t):
    """display time t inside level i (0..DUR) -> physics time."""
    L = LV[i]
    if t < SETUP: return L["T"][0] * (t / SETUP)        # big block slides in at true speed ratio
    u = (t - SETUP) / WIN[i]
    if u <= 1: return 2 + L["w"] * math.sinh(L["A0"] + u * (L["A1"] - L["A0"]))
    return L["T"][-1] + (t - SETUP - WIN[i]) * 0.15     # after the last clack: both drift right, slowly

def state(i, tp):
    """positions + clack count at physics time tp."""
    L = LV[i]; k = int(np.searchsorted(L["T"], tp, side="right")) - 1
    if k < 0: return 1.0, 2.0 - tp, 0
    dt = tp - L["T"][k]
    return L["X1"][k] + L["V1"][k] * dt, L["X2"][k] + L["V2"][k] * dt, k + 1

def count_at(i, t): return state(i, phys_t(i, t))[2]

# ================= look =================
if PAL == "light":
    BG0, BG1 = (196, 226, 246), (240, 246, 250)
    FLOOR, FLOOR2 = (120, 104, 92), (160, 144, 128)
    WALL, WALL2 = (150, 120, 104), (120, 92, 80)
    SMALL, BIG, BIGD = (240, 104, 84), (64, 92, 140), (44, 66, 104)
    PANEL = (255, 255, 255); INK = (40, 48, 64); INK2 = (110, 120, 136)
    GOLD = (214, 140, 30); CYAN = (40, 140, 190); SPARK = (255, 200, 60); DIM = (200, 206, 214)
else:
    BG0, BG1 = (20, 22, 34), (34, 32, 46)
    FLOOR, FLOOR2 = (86, 74, 66), (60, 52, 48)
    WALL, WALL2 = (110, 92, 80), (80, 66, 58)
    SMALL, BIG, BIGD = (240, 104, 84), (110, 150, 200), (78, 110, 156)
    PANEL = (14, 14, 22); INK = (236, 230, 214); INK2 = (150, 146, 140)
    GOLD = (246, 186, 64); CYAN = (110, 210, 236); SPARK = (255, 236, 160); DIM = (70, 70, 84)

FLOOR_Y = 214                                            # art coords (180 x 320)
WALL_X = 22; SW = 10; PXU = 52                           # small block width, px per physics unit
def big_w(i): return 12 + 5 * i                          # 12 .. 37 px: heavier = bigger (not to scale)

def fmt(n): return f"{n:,}"
def mass_si(r):
    if r < 1000: return f"{r:,} KG"
    t = r // 1000
    return f"{t:,} T"
def mass_us(r):
    lb = r * 2.20462
    if lb < 10: return f"{lb:.1f} LB"
    if lb < 1e6: return f"{lb:,.0f} LB"
    if lb < 1e7: return f"{lb / 1e6:.1f} MILLION LB"
    if lb < 1e9: return f"{lb / 1e6:,.0f} MILLION LB"
    return f"{lb / 1e9:,.0f} BILLION LB"

_BG = {}
def background():
    if PAL in _BG: return _BG[PAL].copy()
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        f = y / AH; a[y, :] = [BG0[j] * (1 - f) + BG1[j] * f for j in range(3)]
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    d.rectangle([0, FLOOR_Y, AW, FLOOR_Y + 3], fill=FLOOR)
    for x in range(0, AW, 6): d.line([x, FLOOR_Y + 4, x - 4, FLOOR_Y + 8], fill=FLOOR2)
    d.rectangle([0, FLOOR_Y - 64, WALL_X - 1, FLOOR_Y + 3], fill=WALL)
    for yy in range(FLOOR_Y - 64, FLOOR_Y, 6):
        off = 0 if (yy // 6) % 2 else 5
        d.line([0, yy, WALL_X - 1, yy], fill=WALL2)
        for xx in range(off, WALL_X, 10): d.line([xx, yy, xx, yy + 5], fill=WALL2)
    _BG[PAL] = img
    return img.copy()

def clacks_between(i, ta, tb):
    L = LV[i]
    a = int(np.searchsorted(L["T"], ta, side="right")); b = int(np.searchsorted(L["T"], tb, side="right"))
    if b <= a: return 0, 0
    k = L["K"][a:b]; return int((k == 0).sum()), int((k == 1).sum())

def draw_scene(c, i, t):
    c.art = background(); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    tp = phys_t(i, t); x1, x2, n = state(i, tp)
    bw = big_w(i)
    pxu = min(PXU, (AW - 8 - bw - WALL_X - SW) / max(x2, 1e-9))   # camera pulls back when the big block recedes
    sx = WALL_X + x1 * pxu; bx = WALL_X + SW + x2 * pxu
    d.rectangle([sx, FLOOR_Y - SW, sx + SW - 1, FLOOR_Y - 1], fill=SMALL)
    d.rectangle([sx, FLOOR_Y - SW, sx + SW - 1, FLOOR_Y - SW], fill=(255, 160, 140))
    d.rectangle([bx, FLOOR_Y - bw, bx + bw - 1, FLOOR_Y - 1], fill=BIG)
    d.rectangle([bx, FLOOR_Y - bw, bx + bw - 1, FLOOR_Y - bw], fill=(190, 214, 240))
    d.rectangle([bx + bw - 2, FLOOR_Y - bw, bx + bw - 1, FLOOR_Y - 1], fill=BIGD)
    # sparks: clacks during the last frame
    tq = phys_t(i, max(0.0, t - 1 / FPS))
    nb, nw = clacks_between(i, tq, tp)
    for cnt, x in ((nw, WALL_X), (nb, sx + SW)):
        if cnt:
            g = min(1.0, 0.35 + 0.18 * math.log10(1 + cnt)); rr = int(3 + 5 * g)
            for k in range(6):
                ang = random.uniform(-1.4, 1.4); L_ = random.uniform(2, rr)
                d.line([x, FLOOR_Y - 5, x + L_ * math.cos(ang) * (1 if x == WALL_X else 1), FLOOR_Y - 5 + L_ * math.sin(ang)], fill=SPARK)
            d.rectangle([x - 1, FLOOR_Y - 8, x + 1, FLOOR_Y - 2], fill=SPARK)
    # labels (text layer is 2x art)
    text(W, (sx + SW / 2) * 2, (FLOOR_Y + 10) * 2, "1 KG", fill=SMALL, align="c")
    bl = mass_si(LV[i]["r"])
    text(W, min(352 - 4 * len(bl), max((sx + SW) * 2 + 4 * len(bl) + 10, (bx + bw / 2) * 2)), (FLOOR_Y - bw - 12) * 2, bl, fill=CYAN, align="c")
    return n

def counter(c, n, flash=False, digits_lit=None):
    W = c.t
    W.rectangle([16, 18, 344, 132], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=GOLD); W.rectangle([16, 131, 344, 132], fill=GOLD)
    text(W, 28, 24, "COLLISIONS", fill=INK2)
    s = fmt(n)
    text(W, 180, 52, s, size=40, fill=GOLD if flash else INK, align="c")
    if digits_lit:
        text(W, 180, 100, digits_lit, size=20, fill=GOLD, align="c")

def strip(c, lv_done, cur=None):
    """bottom panel: the levels so far and the digits of pi they spell."""
    W = c.t
    W.rectangle([0, 520, 360, 640], fill=PANEL); W.rectangle([0, 520, 360, 521], fill=GOLD)
    text(W, 12, 526, "LEVEL  BIG BLOCK          COLLISIONS", fill=INK2)
    for j in range(NL):
        y = 542 + j * 14
        done = j < lv_done; now = cur == j
        col = INK if done else (CYAN if now else DIM)
        text(W, 20, y, str(j + 1), fill=col)
        text(W, 68, y, "x" + fmt(LV[j]["r"]), fill=col)
        text(W, 348, y, fmt(LV[j]["n"]) if done else ("..." if now else "?"), fill=GOLD if done else col, align="r")

def level_hud(c, i, t, n):
    W = c.t; L = LV[i]
    W.rectangle([16, 140, 344, 186], fill=PANEL)
    text(W, 28, 144, f"LEVEL {i + 1} OF {NL}", fill=GOLD)
    text(W, 334, 144, "SLOW MOTION" if SETUP <= t < SETUP + WIN[i] + 0.3 and i > 0 else "", fill=CYAN, align="r")
    text(W, 28, 164, f"BIG = {fmt(L['r'])} x SMALL", fill=INK)
    # mass panel under the floor
    W.rectangle([16, 466, 344, 508], fill=PANEL)
    text(W, 180, 470, f"BIG BLOCK: {fmt(L['r'])} KG", fill=CYAN, align="c")
    text(W, 180, 488, mass_us(L["r"]), fill=INK2, align="c")

def sc_intro(t):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, 0, 0.0); W = c.t
    strip(c, 0)
    W.rectangle([16, 18, 344, 200], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=GOLD); W.rectangle([16, 199, 344, 200], fill=GOLD)
    text(W, 28, 26, "TWO BLOCKS.", size=40, fill=INK)
    if t > 0.4: text(W, 28, 66, "314,159", size=40, fill=GOLD)
    if t > 0.7: text(W, 28, 106, "COLLISIONS. LISTEN.", size=20, fill=INK)
    if t > 1.2: text(W, 28, 140, "EVERY BEEP = ONE COLLISION", fill=CYAN)
    if t > 1.8: text(W, 28, 164, "BLOCK-BLOCK + BLOCK-WALL", fill=INK2)
    if t > 2.4:
        W.rectangle([46, 470, 314, 508], fill=PANEL); W.rectangle([46, 470, 314, 471], fill=CYAN)
        text(W, 180, 474, "IDEAL PHYSICS:", fill=INK, align="c")
        text(W, 180, 490, "NO FRICTION, NO ENERGY LOST", fill=INK2, align="c")
    return c

def sc_level(i):
    def f(t):
        c = Ctx(np.zeros((AH, AW, 3), np.uint8)); n = draw_scene(c, i, t)
        L = LV[i]; end = t >= SETUP + WIN[i]
        fresh = (not end) and n > 0 and n < L["n"]
        counter(c, n, flash=fresh and (count_at(i, max(0, t - 0.07)) < n))
        level_hud(c, i, t, n); strip(c, i + (1 if end else 0), cur=i)
        W = c.t
        if t < SETUP:                                     # level card
            w = 260; yb = 236
            W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 46], fill=PANEL); W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=CYAN)
            text(W, 180, yb + 6, f"MASS RATIO {L['label']}", fill=INK, align="c")
            text(W, 180, yb + 24, "100x HEAVIER" if i else "SAME MASS", fill=CYAN, align="c")
        if end and t - SETUP - WIN[i] > 0.15:              # the digits it spells
            a = t - SETUP - WIN[i]
            w = 300; yb = 230
            W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 70], fill=PANEL); W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=GOLD)
            text(W, 180, yb + 6, fmt(L["n"]), size=40, fill=GOLD, align="c")
            if a > 0.5: text(W, 180, yb + 46, f"PI = {L['digits']}...", fill=INK, align="c")
        return c
    return f

def sc_outro(t):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, NL - 1, DUR[f"l{NL}"]); strip(c, NL)
    W = c.t
    W.rectangle([16, 18, 344, 430], fill=PANEL); W.rectangle([16, 18, 344, 20], fill=GOLD)
    text(W, 180, 30, "LEVEL 6: 10 BILLION KG", fill=INK2, align="c")
    if t > 0.3: text(W, 180, 52, "314,159", size=40, fill=GOLD, align="c")
    if t > 0.6: text(W, 180, 94, "COLLISIONS", fill=INK, align="c")
    if t > 1.4: text(W, 180, 130, "PI = 3.14159...", size=40, fill=INK, align="c")
    if t > 2.6:
        text(W, 180, 186, "100x HEAVIER", fill=CYAN, align="c")
        text(W, 180, 206, "= ONE MORE DIGIT OF PI", fill=CYAN, align="c")
    if t > 3.8:
        text(W, 180, 246, "EVERY TIME. FOREVER.", fill=INK, align="c")
    if t > 5.0: text(W, 180, 300, "HOW MANY FOR LEVEL 7?", fill=GOLD, align="c")
    if t > 5.6:
        text(W, 180, 360, "PROOF: G. GALPERIN, 2003", fill=INK2, align="c")
        text(W, 180, 378, "(REGUL. CHAOTIC DYN. 8:375)", fill=INK2, align="c")
        text(W, 180, 396, "COUNTS: EXACT SIMULATION", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "outro": sc_outro}
for _i in range(NL): SCENEFN[f"l{_i + 1}"] = sc_level(_i)

def compose_layers(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tb = np.repeat(np.repeat(np.array(c.txt), 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

BEATS = [i * BEAT for i in range(int(TOTAL / BEAT) + 1)]
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    c = SCENEFN[name](t)
    fr = compose_layers(c)
    if name != "outro":
        bi = int(np.searchsorted(BEATS, T, side="right")) - 1
        kp = math.exp(-(T - BEATS[bi]) / 0.08) if bi >= 0 else 0.0
        z = 1.0 + 0.008 * kp * FXK
        if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    if name.startswith("l"):                              # big hit on the first clack of each level
        i = int(name[1:]) - 1; a = T - LV[i]["disp"][0]
        if 0 <= a < 0.12:
            fr = np.minimum(255, fr.astype(np.int16) + int(40 * FXK * (1 - a / 0.12))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    return fr

# ================= audio (choice B "Compteur mecanique", from pi_clacks_moods.py mood_b) =================
SR = 44100
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter, fftconvolve
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    n = int((TOTAL + 1.0) * SR); L = np.zeros(n)
    def put(t0, s, g=1.0):
        i = int(t0 * SR); j = min(n, i + len(s))
        if 0 <= i < n: L[i:j] += g * s[:j - i]
    def kick(g):
        m = int(.3 * SR); tt = np.arange(m) / SR
        return g * np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 18) + 45) / SR) * np.exp(-tt * 13)
    rs = np.random.RandomState(3)
    T_OFF = START["outro"] + 2.0
    for k, b in enumerate(BEATS):
        if b >= TOTAL - 0.5: break
        g = 1.0 if b < T_OFF else max(0.0, 1 - (b - T_OFF) / 3.0)
        if g > 0:
            put(b, kick(.30 * g * (0.7 if b < INTRO else 1)))
            put(b + BEAT / 2, .05 * g * highpass(rs.randn(int(.04 * SR)), 6000) * np.exp(-np.arange(int(.04 * SR)) / SR * 90))
            if k % 2: put(b, .06 * g * lowpass(rs.randn(int(.15 * SR)), 5000) * np.exp(-np.arange(int(.15 * SR)) / SR * 25))
        root = [38, 38, 41, 36][(k // 4) % 4]
        gb = 1.0 if b < T_OFF + 2 else max(0.0, 1 - (b - T_OFF - 2) / 4.0)
        m = int(.22 * SR); put(b + BEAT / 2, .08 * gb * np.sign(np.sin(2 * np.pi * mtof(root) * np.arange(m) / SR)) * np.exp(-np.arange(m) / SR * 12))
    def grain(f, dec, dur=.03, harm=(1, 1.7, 2.9), a=.0005):
        m = int(dur * SR); tt = np.arange(m) / SR
        s = sum(np.sin(2 * np.pi * f * h * tt) / (q + 1) for q, h in enumerate(harm))
        return s * np.minimum(1, tt / a) * np.exp(-tt / dec)
    clk = np.zeros(n)
    for Lv in LV:
        idx = np.minimum(n - 1, (Lv["disp"] * SR).astype(np.int64))
        np.add.at(clk, idx, 1.0)
        a = Lv["disp"][0]; put(a, kick(.5)); put(a, .05 * highpass(rs.randn(int(.8 * SR)), 4000) * np.exp(-np.arange(int(.8 * SR)) / SR * 6))
    kk = int(.03 * SR); r = np.convolve(clk, np.ones(kk), "same")
    clk = clk / np.sqrt(np.maximum(1, r))
    L += .25 * fftconvolve(clk, grain(3200, .004), "full")[:n]
    put(0.08, .25 * grain(3200, .004))                    # first click immediately
    # counter "ding" when a level's count is shown
    for i, Lv in enumerate(LV):
        te = Lv["start"] + SETUP + WIN[i] + 0.15; m = int(.6 * SR); tt = np.arange(m) / SR
        put(te, .10 * (np.sin(2 * np.pi * 1568 * tt) + .4 * np.sin(2 * np.pi * 2349 * tt)) * np.exp(-tt * 6))
    out = L.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16)]:
        q = int(dl * SR); out[q:] += g * .6 * L[:-q]
    x = .85 * L + .15 * lowpass(out, 4000)
    x = np.tanh(x * 1.5) / 1.5
    tt = np.arange(len(x)) / SR; x *= np.clip((TOTAL + 0.3 - tt) / 1.5, 0, 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(len(x) / SR, 2), "s")

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    nf = int(round((START[name] + dur) * FPS)) - int(round(START[name] * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    f0 = int(round(START[name] * FPS))
    for f in range(nf): p.stdin.write(render_frame(idx, max(0.0, (f0 + f) / FPS - START[name])).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio":
        render_audio(out); sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}_{PAL}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}_{PAL}.png")
    elif mode == "info":
        print("total", round(TOTAL, 2), "s ·", sum(L["n"] for L in LV), "clacks")
        print({n: round(d, 2) for n, d in SC})
        for i, L in enumerate(LV):
            print(i + 1, L["r"], L["n"], "clacks", round(L["disp"][0], 2), "->", round(L["disp"][-1], 2), "min x2", L["X2"].min())
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(min(6, os.cpu_count() or 3)) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
