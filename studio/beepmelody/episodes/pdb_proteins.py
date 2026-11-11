"""BEEPMELODY — 17,557 NEW MOLECULES SEEN IN ONE YEAR. IT STARTED WITH 13.
Every year of the Protein Data Bank, 1976 -> 2025: one note per year, pitch = log(structures released that year).
Scene: a microscope field that fills with structures, a log bar chart of the yearly count below.
Mood chosen by Guillaume (co-pilot step 2, option C 'Cell machinery'): 116 BPM, pizzicato strings for the data,
wood-block 16ths whose density follows the yearly count, kick on every beat, square bass Em–C–G–D.
Data: pdb_proteins.csv (RCSB growth stats; wwPDB release stats cross-check from 2000; PDB-250k news for the total).

    python3 pdb_proteins.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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

FXK = float(os.environ.get("PI_FX", "0.8"))
DARK = os.environ.get("PDB_DARK", "0") == "1"

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "pdb_proteins.csv"))))
for r in REC:
    r["y"] = int(r["year"]); r["v"] = int(r["released"])
tot = 0
for r in REC:
    tot += r["v"]; r["tot"] = tot                                 # cumulative from 1976 (pre-1976 entries not counted)
N = len(REC)
def ik(v): return f"{int(v):,}"

# ================= palette: light 'bio green' (lab bench) / dark variant (fluorescence) =================
if not DARK:
    BG0, BG1 = (226, 242, 228), (246, 250, 240)
    INK = (28, 52, 40); INK2 = (96, 122, 104); CREAM = (250, 251, 244); WHITE = (255, 255, 255)
    GOLD = (214, 140, 24); GREEN = (34, 150, 84); GREEN2 = (120, 196, 140)
    FIELD = (238, 248, 236); RIM = (60, 84, 70); CHARTBG = (250, 252, 248); GRID = (220, 234, 222)
else:
    BG0, BG1 = (10, 24, 20), (16, 34, 28)
    INK = (226, 246, 230); INK2 = (130, 170, 146); CREAM = (14, 30, 24); WHITE = (255, 255, 255)
    GOLD = (255, 196, 70); GREEN = (90, 230, 140); GREEN2 = (50, 140, 90)
    FIELD = (6, 16, 12); RIM = (120, 150, 132); CHARTBG = (12, 26, 20); GRID = (30, 54, 42)
PCOL = [(34, 150, 84), (40, 120, 200), (214, 140, 24), (200, 70, 110), (120, 90, 200)]
if DARK: PCOL = [(90, 230, 140), (90, 180, 255), (255, 196, 70), (255, 110, 160), (180, 140, 255)]

# ================= timeline (on the beat) =================
BPM = 116.0
BEAT = 60.0 / BPM
INTRO_B = 8
STEP_B = 2                                                       # one year = 2 beats, constant: time stays honest
HOLD_B = 10
OUTRO_B = 14
RT = [INTRO_B * BEAT + i * STEP_B * BEAT for i in range(N)]
T_FINAL = RT[-1]
T_REC_END = T_FINAL + HOLD_B * BEAT
def iy(y): return next(i for i, r in enumerate(REC) if r["y"] == y)
SC = [("intro", RT[0]), ("early", RT[iy(1993)] - RT[0]), ("boom", RT[iy(2010)] - RT[iy(1993)]),
      ("modern", T_REC_END - RT[iy(2010)]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
TOTAL = acc_

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan =================
SCALE = [52, 55, 57, 59, 62, 64, 67, 69, 71, 74, 76, 79, 81, 83]   # E minor pentatonic (same as the step-2 excerpt)
LO, HI = math.log10(6), math.log10(17557)
def deg(v): return int(round(min(1, max(0, (math.log10(v) - LO) / (HI - LO))) * (len(SCALE) - 1)))
def pitch(i): return SCALE[deg(REC[i]["v"])]
ROOTS = [40, 36, 43, 38]                                         # Em–C–G–D
MILE = {}
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))

BANNERS = {iy(1976): ("13 STRUCTURES", "RELEASED IN 1976", False),
           iy(1990): ("100+ A YEAR", "142 IN 1990", True),
           iy(1994): ("1,000+ A YEAR", "1,289 IN 1994", True),
           iy(2004): ("5,000+ A YEAR", "5,149 IN 2004", True),
           iy(2014): ("100,000 IN THE BANK", "SINCE 1976", False),
           iy(2016): ("10,000+ A YEAR", "10,803 IN 2016", True),
           iy(2020): ("13,985", "NEW RECORD YEAR", False),
           iy(2023): ("200,000 IN THE BANK", "SINCE 1976", False),
           N - 1: ("17,557", "ALL-TIME HIGH · 2025", True)}
def build():
    nb = int(round(TOTAL / BEAT)) + 1
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4); ro = ROOTS[bar % 4]
        main = RT[0] <= t < T_REC_END
        if t < RT[0]:
            if pos == 0: ev(t, "kick", v=0.6)
            if b >= 4: ev(t + BEAT / 2, "wood", v=0.04)
            if pos == 0: ev(t, "bass", m=ro, d=BEAT * 1.8, v=0.20)
        elif main:
            ev(t, "kick", v=0.62)
            if pos in (1, 3): ev(t, "snare", v=0.30)
            for h in (0, 0.5): ev(t + h * BEAT, "bass", m=ro + (12 if h else 0), d=BEAT * 0.45, v=0.24)
        elif t < TOTAL - 2 * BEAT and pos == 0:
            ev(t, "bass", m=ro, d=BEAT * 3.5, v=0.18)
            ev(t, "pizz", m=ro + 24, v=0.18); ev(t + BEAT, "pizz", m=ro + 31, v=0.14); ev(t + 2 * BEAT, "pizz", m=ro + 36, v=0.12)
    s16 = BEAT / 4
    for i, t in enumerate(RT):
        r = REC[i]
        ev(t, "pizz", m=pitch(i), v=0.46 + (0.12 if i in BANNERS and BANNERS[i][2] else 0))
        k16 = 1 + int(math.log10(r["v"]))                        # 1..5 : wood-block density follows the yearly count
        nxt = RT[i + 1] if i + 1 < N else T_REC_END
        for j in range(1, int(round((nxt - t) / s16))):
            if j % max(1, 5 - k16) == 0: ev(t + j * s16, "wood", v=0.05 + 0.006 * k16)
        if i in BANNERS and BANNERS[i][2]:
            ev(t + BEAT / 2, "pizz", m=pitch(i), v=0.30); ev(t, "crash", v=0.18)
    for k, d in enumerate([0, 7, 12, 15, 19, 24]):               # rising arpeggio on 2025
        ev(T_FINAL + (k + 1) * BEAT / 2, "pizz", m=pitch(N - 1) - 24 + d, v=0.30)
    ev(T_FINAL - 4 * BEAT, "riser", d=4 * BEAT, v=0.10)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= drawing =================
def bg():
    a = np.zeros((AH, AW, 3), np.uint8)
    for y in range(AH):
        f = min(1.0, y / 320); a[y, :] = tuple(int(BG0[j] + (BG1[j] - BG0[j]) * f) for j in range(3))
    return Image.fromarray(a)
_BG = bg()

MX, MY, MR = 90, 138, 46                                         # microscope field (art px)
_rng = np.random.default_rng(7)
SLOTS = []                                                       # deterministic positions for structures in the field
while len(SLOTS) < 260:
    a = _rng.uniform(0, 2 * math.pi); rr = MR * 0.9 * math.sqrt(_rng.uniform(0, 1))
    SLOTS.append((MX + rr * math.cos(a), MY + rr * math.sin(a), int(_rng.integers(0, 5)), int(_rng.integers(0, 4))))
def nblobs(i):                                                   # structures drawn ~ log of the cumulative total
    return 0 if i < 0 else int(round(8 + 232 * math.sqrt(REC[i]["tot"] / REC[-1]["tot"])))
def blob(d, x, y, col, shape, s=1):
    x, y = int(x), int(y)
    pts = [[(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)], [(0, 1), (1, 0), (2, 0), (3, 1), (2, 2), (1, 2)],
           [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0)], [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (3, 2)]][shape]
    for px, py in pts: d.rectangle([x + px * s, y + py * s, x + px * s + s - 1, y + py * s + s - 1], fill=col)

def microscope(c, T):
    d = c.a; k = rec_index(T)
    d.ellipse([MX - MR - 6, MY - MR - 6, MX + MR + 6, MY + MR + 6], fill=RIM)
    d.ellipse([MX - MR, MY - MR, MX + MR, MY + MR], fill=FIELD)
    n = min(len(SLOTS), nblobs(k))
    for j in range(n):
        x, y, cc, sh = SLOTS[j]
        wob = math.sin(T * 2.2 + j) * 0.8
        blob(d, x + wob, y, PCOL[cc], sh)
    if k >= 0:
        age = T - RT[k]; n0 = min(len(SLOTS), nblobs(k - 1))
        for j in range(n0, n):                                   # the new ones pop with a ring
            x, y, cc, sh = SLOTS[j]
            if 0 <= age < 0.4:
                rr = min(1 + age * 14, MR - math.hypot(x - MX, y - MY)); d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=WHITE if age < 0.1 else PCOL[cc])
        if 0 <= age < 0.12:
            d.ellipse([MX - MR, MY - MR, MX + MR, MY + MR], outline=GREEN2, width=2)
    if k < 0:                                                    # intro: the beam sweeps the empty field
        a = T * 2.4
        d.line([MX, MY, MX + MR * math.cos(a), MY + MR * math.sin(a)], fill=GREEN2, width=1)
        d.ellipse([MX - 2, MY - 2, MX + 2, MY + 2], fill=GREEN2)
    for yy in range(MY - MR - 6, MY + MR + 7):                    # crosshair ticks
        if yy % 8 == 0: d.point((MX + MR + 8, yy), fill=INK2)

CX0, CX1, CY0, CY1 = 26, 172, 210, 286                           # yearly bar chart (art px)
def cy(v): return CY1 - (math.log10(max(1, v)) - 0) / (math.log10(30000)) * (CY1 - CY0)
def chart(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    d.rectangle([CX0 - 2, CY0 - 4, CX1 + 2, CY1 + 2], fill=CHARTBG, outline=GRID)
    for v in (10, 100, 1000, 10000):
        y = cy(v); d.line([CX0, y, CX1, y], fill=GRID)
        text(W, CX0 * 2 - 6, int(y * 2) - 10, {10: "10", 100: "100", 1000: "1K", 10000: "10K"}[v], fill=INK2, align="r")
    bw = (CX1 - CX0) / N
    for i in range(k + 1):
        x0 = CX0 + i * bw; y = cy(REC[i]["v"])
        hot = i == k and 0 <= T - RT[k] < 0.3
        d.rectangle([int(x0), int(y), int(x0 + bw) - 1, CY1], fill=WHITE if hot else (GREEN if i == k else GREEN2))
    for yy in (1976, 1990, 2000, 2010, 2025):
        x = CX0 + (iy(yy) + 0.5) * bw
        text(W, int(x * 2), int(CY1 * 2) + 8, str(yy), fill=INK2, align="c")
    text(W, CX0 * 2, int(CY0 * 2) - 24, "STRUCTURES PER YEAR (LOG)", fill=INK2)

def hud(c, T):
    W = c.t; k = rec_index(T); r = REC[k]; age = T - RT[k]
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    text(W, 28, 22, "NEW 3D STRUCTURES THIS YEAR", fill=GREEN)
    text(W, 28, 44, ik(r["v"]), size=40, fill=GREEN if age < 0.22 else INK)
    text(W, 28, 92, "PROTEIN DATA BANK", fill=INK2)
    text(W, 334, 44, r["year"], size=40, fill=GOLD, align="r")
    W.rectangle([16, 128, 344, 152], fill=CREAM); W.rectangle([16, 128, 19, 152], fill=GREEN)
    text(W, 28, 131, f"IN THE BANK SINCE 1976: {ik(r['tot'])}", fill=INK)

def footer(c, T, k=None):
    W = c.t; k = rec_index(T) if k is None else k
    W.rectangle([0, 600, 360, 640], fill=CREAM); W.rectangle([0, 600, 360, 601], fill=INK2)
    text(W, 10, 604, "1976", fill=INK2); text(W, 10, 620, "13 A YEAR", fill=INK)
    text(W, 180, 604, "VS 1976", fill=GOLD, align="c")
    ratio = REC[k]["v"] / REC[0]["v"] if k >= 0 else 1
    text(W, 180, 620, f"{ik(ratio)}X MORE" if k > 0 else "--", fill=INK, align="c")
    text(W, 350, 604, "EVERY BEEP", fill=INK2, align="r"); text(W, 350, 620, "= ONE YEAR", fill=INK, align="r")

def banner(c, T):
    k = rec_index(T)
    if k not in BANNERS: return
    a = T - RT[k]; hold = HOLD_B * BEAT if k == N - 1 else STEP_B * BEAT * 1.6
    if not (0.06 < a < hold): return
    tt, sub, big = BANNERS[k]; W = c.t
    w = max((16 if big else 9) * len(tt) + 30, 8 * len(sub) + 30); hgt = 62 if big else 42
    xc = 180; x0, x1 = xc - w / 2, xc + w / 2; yb = 336
    W.rectangle([x0, yb, x1, yb + hgt], fill=CREAM)
    W.rectangle([x0, yb, x1, yb + 2], fill=GOLD); W.rectangle([x0, yb + hgt - 1, x1, yb + hgt], fill=INK2)
    if big:
        text(W, xc, yb + 4, tt, size=40, fill=INK, align="c")
        if a > 0.2: text(W, xc, yb + 40, sub, fill=GOLD, align="c")
    else:
        text(W, xc, yb + 3, tt, fill=INK, align="c")
        if a > 0.2: text(W, xc, yb + 21, sub, fill=INK2, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _BG.copy(); c.a = ImageDraw.Draw(c.art)
    microscope(c, T); chart(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 160], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 159, 344, 160], fill=INK)
    text(W, 28, 24, "PROTEIN DATA BANK", size=40, fill=INK)
    if t > 0.3:
        text(W, 28, 64, "13", size=40, fill=GREEN); text(W, 80, 64, "->", size=40, fill=INK2)
        text(W, 132, 64, "17,557 A YEAR", size=40, fill=GOLD)
    if t > 0.8: text(W, 28, 110, "EVERY BEEP = ONE YEAR, 1976 -> 2025", fill=INK2)
    if t > 1.3: text(W, 28, 132, "MORE STRUCTURES = HIGHER NOTE", fill=GREEN)
    if t > 2.0:
        W.rectangle([60, 336, 300, 378], fill=CREAM); W.rectangle([60, 336, 300, 338], fill=GOLD)
        text(W, 180, 339, "3D MAPS OF LIFE'S MACHINES", fill=INK, align="c")
        text(W, 180, 357, "ATOM BY ATOM", fill=INK2, align="c")
    footer(c, T, 0)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T); footer(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T_REC_END); W = c.t
    W.rectangle([0, 0, 360, 600], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "50 YEARS · 50 BEEPS", fill=INK2, align="c")
    if t > 0.3:
        text(W, 40, 82, "1976", size=40, fill=GREEN); text(W, 320, 82, "13", size=40, fill=INK, align="r")
    if t > 0.9:
        text(W, 40, 132, "2025", size=40, fill=GOLD); text(W, 320, 132, "17,557", size=40, fill=INK, align="r")
    if t > 1.5:
        text(W, 180, 190, "NEW 3D STRUCTURES PER YEAR", fill=INK2, align="c")
        text(W, 180, 212, "1,350X MORE", fill=GREEN, align="c")
    if t > 2.0:
        text(W, 180, 262, "FOUNDED IN 1971 WITH 7", fill=INK2, align="c")
        text(W, 180, 284, "250,441 ENTRIES BY MARCH 2026", fill=INK, align="c")
    if t > 2.8: text(W, 180, 360, "WHAT'S NEXT TO SEE?", size=40, fill=GOLD, align="c")
    if t > 3.0:
        W.rectangle([40, 462, 320, 463], fill=INK2)
        text(W, 180, 476, "STRUCTURES RELEASED PER YEAR.", fill=INK2, align="c")
        text(W, 180, 496, "DATA: RCSB PDB, wwPDB,", fill=INK2, align="c")
        text(W, 180, 516, "PDBe / EMDB (MARCH 2026)", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "boom": sc_main("boom"), "modern": sc_main("modern"), "outro": sc_outro}

def compose_light(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt)
    tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(SCENEFN[name](t))
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    z = 1.0 + 0.010 * kp * FXK
    if abs(T - T_FINAL) < 0.4: z += 0.03 * FXK * math.exp(-abs(T - T_FINAL) / 0.12)
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if name != "outro" and k >= 0 and 0 <= T - RT[k] < 0.08:
        fr = np.minimum(255, fr.astype(np.int16) + int(40 * FXK * (1 - (T - RT[k]) / 0.08))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio: 'cell machinery' (step-2 option C) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n); fx = np.zeros(n)
    rng = np.random.default_rng(11)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fx, i, x * send)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "pizz":
            m_ = int(0.8 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = sum((1 / h) * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (6 + 4 * h)) for h in range(1, 6))
            x = x * env(m_, 0.002, 0.3)
            put(t, x * v * 0.7, pan=-0.1, send=0.18); put(t + BEAT * 0.75, x * v * 0.14, pan=0.4)
        elif k == "wood":
            m_ = int(0.05 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 120) * v * 1.2, pan=0.35)
        elif k == "bass":
            d = kw["d"]; m_ = int((d + 0.03) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = 0.5 * np.sign(np.sin(2 * np.pi * f * tt)) + 0.6 * np.sin(2 * np.pi * f * tt)
            x = lfilter(*butter(2, 1200 / (SR / 2)), x) * np.exp(-tt * 6) * np.clip((d + 0.02 - tt) / 0.02, 0, 1)
            put(t, x * v)
        elif k == "kick":
            m_ = int(0.35 * SR); tt = np.arange(m_) / SR
            x = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 16) + 48) / SR) * np.exp(-tt * 12)
            put(t, np.tanh(1.5 * x) * v * 0.8)
        elif k == "snare":
            m_ = int(0.14 * SR)
            x = lfilter(*butter(2, 3500 / (SR / 2)), rng.standard_normal(m_)) * env(m_, 0.0005, 0.045)
            put(t, x * v, send=0.12)
        elif k == "crash":
            m_ = int(1.6 * SR)
            put(t, lfilter(*butter(2, 5000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.002, 0.45) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            put(t, lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    out = fx.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16)]:
        k_ = int(dl * SR); out[k_:] += g * .6 * fx[:-k_]
    b, a = butter(2, 4000 / (SR / 2)); out = lfilter(b, a, out)
    L += out * 0.5; R += np.roll(out, 400) * 0.5
    tt = np.arange(n) / SR
    fade = np.clip((TOTAL - tt) / 1.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.tanh(np.stack([L, R], 1) / mx * 1.3) / np.tanh(1.3) * 0.9
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(n / SR, 2), "s")

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
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print([(REC[i]["year"], REC[i]["v"], REC[i]["tot"], round(t, 2), pitch(i), nblobs(i)) for i, t in enumerate(RT)])
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
