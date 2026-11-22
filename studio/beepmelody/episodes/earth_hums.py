"""BEEPMELODY — HALF OF EVERYTHING WE LAUNCHED WENT UP AFTER 2021.
Objects launched into space per year, 1957-2025 (UNOOSA via Our World in Data, cross-checked with GCAT / J. McDowell):
24,865 objects; 12,741 of them (51.2 %) in 2022-2025.
Rule: EVERY BEEP = 20 OBJECTS LAUNCHED. Beep n sounds exactly when the running total passes 20 x n (linear inside the year),
so the beeps of a year are spread over its slot: 1959 = first beep, 2025 = 225 beeps in 0.8 s -> a hum.
1 year = 0.8 s. Sputnik 1's own radio beep opens and closes the video.
Scene: neon pixel globe; every beep = a new dot that lights up on its orbit (cyan before 2022, gold from 2022): the shell fills,
and by the end half the dots are gold. Bottom: launches per year (linear). HUD: year, launched that year, running total + share.
Music (co-pilot step 2, choice B "retro telemetry"): 120 BPM, 8-bit drums, triangle bass, square chiptune bleeps
(one per beep, rising inside each year), the bleeps turn into a buzzing carrier wave; a crash + arpeggio on the half mark.

    python3 earth_hums.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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
VARIANT = os.environ.get("LV", "neon")          # neon (dark) | light

# ================= data =================
DATA = {int(r["year"]): int(r["value"]) for r in csv.DictReader(open(os.path.join(HERE, "earth_hums.csv")))}
Y0, Y1 = 1957, 2025
YEARS = list(range(Y0, Y1 + 1)); NY = len(YEARS)
TOTAL_OBJ = sum(DATA.values())                          # 24,865
HALF = TOTAL_OBJ / 2.0                                  # 12,432.5
CUM = {}; acc = 0
for y in YEARS: acc += DATA[y]; CUM[y] = acc
BEFORE = CUM[2021]; AFTER = TOTAL_OBJ - BEFORE          # 12,124 / 12,741
PER = 20

# ================= timeline =================
BPM = 120.0; BEAT = 60.0 / BPM                          # 0.5 s
YEAR = 0.8                                              # same pace as the step-2 excerpt Guillaume chose
INTRO = 4.0
T_END = INTRO + NY * YEAR                               # 59.2
OUTRO = 8.0
TOTAL = T_END + OUTRO                                   # 67.2
def ystart(y): return INTRO + (y - Y0) * YEAR

BEEPS = []                                              # (t, year, i_in_year, n_in_year, n_global)
for y in YEARS:
    c0 = CUM[y] - DATA[y]; c1 = CUM[y]
    ns = list(range(c0 // PER + 1, c1 // PER + 1))
    for i, n in enumerate(ns):
        frac = (PER * n - c0) / DATA[y]
        BEEPS.append((ystart(y) + frac * YEAR, y, i, len(ns), n))
BT = np.array([b[0] for b in BEEPS]); NB = len(BEEPS)
T_HALF = ystart(2022) + (HALF - CUM[2021]) / DATA[2022] * YEAR

SC = [("intro", INTRO), ("early", ystart(1970) - INTRO), ("plateau", ystart(2013) - ystart(1970)),
      ("boom", T_END - ystart(2013)), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

def year_at(T):
    if T < INTRO: return None
    return min(Y1, Y0 + int((T - INTRO) / YEAR))
def cum_at(T):
    """Running total at time T (linear inside the year, exactly like the beeps)."""
    if T < INTRO: return 0.0
    if T >= T_END: return float(TOTAL_OBJ)
    y = year_at(T); f = (T - ystart(y)) / YEAR
    return CUM[y] - DATA[y] + f * DATA[y]
def nbeeps(T): return int(np.searchsorted(BT, T, side="right"))

# ================= music plan =================
PENT = [0, 2, 4, 7, 9]
def deg(i, n, y, base, span=10):
    d = int(i / max(n, 1) * span) + (y - Y0) % 3
    return base + 12 * (d // 5) + PENT[d % 5]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
SPUT_IN = 0.25                                          # Sputnik beep in the intro
SPUT_OUT = T_END + 1.0                                  # ... and alone at the end, after the silence
def build():
    for q in range(2): ev(SPUT_IN + q * 0.6, "sput", v=0.20)
    for q in range(4): ev(SPUT_OUT + q * 0.6, "sput", v=0.20 if q < 2 else 0.12)
    nb = int(round(T_END / BEAT))
    for b in range(nb):
        t = b * BEAT
        if t < 2.0: continue
        if t < INTRO - 1e-6:                            # count-in
            ev(t, "kick", v=0.10 + 0.04 * (b - 4)); continue
        ev(t, "kick", v=0.16)
        if b % 2: ev(t, "snare", v=0.05)
        ev(t + BEAT / 2, "hat", v=0.02)
        root = [36, 36, 41, 43][(b // 2) % 4]
        ev(t, "tri", m=root, v=0.08)
    ev(INTRO, "crash", v=0.07)
    for t, y, i, n, _ in BEEPS:
        ev(t, "bleep", m=deg(i, n, y, 76), v=0.09 / max(1, n / 12) ** .2, d=.06 if n < 60 else .03)
    ev(T_HALF, "crash", v=0.12)
    for k, dd in enumerate([0, 7, 12, 16, 19, 24]): ev(T_HALF + k * 0.06, "arp", m=72 + dd, v=0.10)
    ev(ystart(2025), "carrier", d=YEAR, v=0.05)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= palette =================
if VARIANT == "light":
    BG = (236, 242, 248); OCEAN = (196, 220, 238); OCEAN2 = (184, 210, 232); LANDC = (236, 222, 186); LAND2 = (214, 196, 150)
    INK = (34, 44, 78); INK2 = (92, 104, 140); RIM = (150, 180, 214); PANEL = (252, 248, 238)
    OLD = (40, 120, 220); NEW = (230, 140, 20); WHITE = (20, 30, 60); STARC = None; BAR = (120, 150, 200)
else:
    BG = (6, 8, 26); OCEAN = (12, 26, 66); OCEAN2 = (16, 32, 78); LANDC = (34, 150, 170); LAND2 = (60, 210, 220)
    INK = (230, 244, 255); INK2 = (130, 150, 200); RIM = (70, 120, 230); PANEL = (10, 12, 34)
    OLD = (90, 220, 255); NEW = (255, 210, 70); WHITE = (255, 255, 255); STARC = (180, 200, 255); BAR = (50, 120, 200)
GOLD = NEW; RED = (255, 60, 70)

# ================= globe + orbit shell =================
GX, GY, GR = 90.0, 177.0, 44.0
LAT_V = math.radians(22.0)
SPIN = 360.0 / 14.0
def view_lon(T): return 20.0 + SPIN * T
_land = np.load(os.path.join(ENGINE, "..", "geo", "land_clean.npy"))
YY, XX = np.mgrid[0:AH, 0:AW]
DX = (XX + 0.5 - GX) / GR; DY = -(YY + 0.5 - GY) / GR
INDISK = DX ** 2 + DY ** 2 < 1.0
DZ = np.sqrt(np.clip(1 - DX ** 2 - DY ** 2, 0, 1))
_LATG = np.degrees(np.arcsin(np.clip(DY * math.cos(LAT_V) + DZ * math.sin(LAT_V), -1, 1)))
_LONG0 = np.degrees(np.arctan2(DX, DZ * math.cos(LAT_V) - DY * math.sin(LAT_V)))
_rng = np.random.default_rng(7)
STARS = [(int(_rng.integers(0, AW)), int(_rng.integers(0, AH)), float(_rng.random())) for _ in range(90)]

# one orbit per beep (illustrative: inclination, node, phase, height are random; colour = era)
_r = np.random.default_rng(1957)
ORB_R = np.where(_r.random(NB) < 0.88, 1.18 + 0.38 * _r.random(NB) ** 1.5, 1.80 + 0.06 * _r.random(NB))
ORB_I = np.radians(np.where(_r.random(NB) < 0.7, 40 + 60 * _r.random(NB), 100 * _r.random(NB)))
ORB_I = np.where(ORB_R > 1.7, np.radians(2.0), ORB_I)            # outer ring ~ equatorial (geostationary-like)
ORB_O = _r.random(NB) * 2 * math.pi
ORB_P = _r.random(NB) * 2 * math.pi
ORB_W = 0.9 / ORB_R ** 1.5                                       # rad/s, lower = faster
ORB_W = np.where(ORB_R > 1.7, 0.0, ORB_W)
BYEAR = np.array([b[1] for b in BEEPS])
SPUT = (1.25, math.radians(65.1), 0.7, 0.3)                      # Sputnik 1 inclination 65.1 deg

def orbit_xyz(R, I, O, P, W, T):
    u = P + W * T
    x0, y0 = R * np.cos(u), R * np.sin(u)                         # orbit plane
    # tilt by inclination around x, then rotate node around the polar axis (y up)
    xe, ze = x0, y0                                              # equatorial plane = x-z
    yi = ze * np.sin(I); zi = ze * np.cos(I)
    xr = xe * np.cos(O) + zi * np.sin(O); zr = -xe * np.sin(O) + zi * np.cos(O)
    y = yi * math.cos(LAT_V) - zr * math.sin(LAT_V); z = yi * math.sin(LAT_V) + zr * math.cos(LAT_V)
    return xr, y, z

def draw_globe(c, T):
    a = np.zeros((AH, AW, 3), np.uint8); a[:] = BG
    if STARC:
        for x, y, b in STARS:
            if not INDISK[y, x]: a[y, x] = tuple(int(v * (0.3 + 0.5 * b)) for v in STARC)
    lon = (_LONG0 + view_lon(T) + 180.0) % 360.0
    iy = np.clip(((90.0 - _LATG) * 4).astype(int), 0, 719); ix = np.clip((lon * 4).astype(int), 0, 1439)
    land = _land[iy, ix] > 0.4
    sea = INDISK & ~land; ld = INDISK & land
    a[sea] = OCEAN; a[sea & ((XX + YY) % 5 == 0)] = OCEAN2
    a[ld] = LANDC
    edge = ld & ~(np.roll(ld, 1, 0) & np.roll(ld, -1, 0) & np.roll(ld, 1, 1) & np.roll(ld, -1, 1))
    a[edge] = LAND2
    shade = (0.55 + 0.45 * np.clip(DZ * 0.8 + DX * -0.3 + DY * 0.3, 0, 1))[..., None]
    a = np.where(INDISK[..., None], (a * shade).astype(np.uint8), a)
    a[np.abs(np.sqrt(DX ** 2 + DY ** 2) - 1.0) < 1.2 / GR] = RIM
    c.art = Image.fromarray(a); c.a = ImageDraw.Draw(c.art)

def draw_shell(c, T):
    a = np.array(c.art)
    k = nbeeps(T)
    def plot(x, y, z, col, flash=None):
        px = np.round(GX + x * GR).astype(int); py = np.round(GY - y * GR).astype(int)
        vis = ~((z < 0) & (x ** 2 + y ** 2 < 1.0)) & (px >= 0) & (px < AW) & (py >= 0) & (py < AH)
        a[py[vis], px[vis]] = col if flash is None else col[vis]
    # Sputnik 1 (always there as the first dot: it re-entered in Jan 1958, but it is the "one beep")
    if T < INTRO + 1.6 * YEAR or T >= SPUT_OUT - 0.2:
        x, y, z = orbit_xyz(np.array([SPUT[0]]), SPUT[1], SPUT[2], SPUT[3], 0.6, T)
        plot(x, y, z, WHITE)
    if k == 0: return a
    x, y, z = orbit_xyz(ORB_R[:k], ORB_I[:k], ORB_O[:k], ORB_P[:k], ORB_W[:k], T)
    age = T - BT[:k]
    cols = np.where((BYEAR[:k] >= 2022)[:, None], np.array(NEW), np.array(OLD)).astype(np.float32)
    dim = np.clip(0.78 + 0.22 * np.exp(-age / 3.0), 0, 1)[:, None]
    cols = cols * dim + np.array(BG) * (1 - dim)
    fresh = age < 0.15
    cols[fresh] = WHITE
    plot(x, y, z, cols.astype(np.uint8), flash=True)
    return a

def frise(c, T):
    W = c.t; d = c.a
    X0, X1, YB, YT = 12, 168, 290, 262
    d.rectangle([0, YT - 6, AW, AH], fill=BG)
    yy = year_at(T)
    bw = (X1 - X0) / NY
    vmax = max(DATA.values())
    for j, y in enumerate(YEARS):
        if yy is None or y > yy: break
        v = DATA[y] if y < yy else cum_at(T) - (CUM[y] - DATA[y])
        h = max(1.0, v / vmax * (YB - YT))
        x0 = X0 + j * bw; x1 = x0 + bw - 0.6
        d.rectangle([int(x0), int(YB - h), max(int(x0), int(x1)), YB], fill=NEW if y >= 2022 else BAR)
    d.line([X0, YB + 1, X1, YB + 1], fill=INK2)
    text(W, X0 * 2, 586, "1957", fill=INK2); text(W, X1 * 2, 586, "2025", fill=INK2, align="r")
    text(W, 180, 586, "LAUNCHED PER YEAR", fill=INK2, align="c")

def meter(c, T):
    """Running total as a share of everything launched 1957-2025, with the 50 % line."""
    W = c.t; cu = cum_at(T)
    X0, X1, Y = 24, 336, 168
    W.rectangle([16, 118, 344, 202], fill=PANEL)
    text(W, 28, 122, "TOTAL SINCE 1957", fill=INK2)
    text(W, 334, 122, f"{int(round(cu)):,}", fill=INK, align="r")
    W.rectangle([X0, Y, X1, Y + 12], outline=INK2)
    xb = X0 + (X1 - X0) * min(cu, BEFORE) / TOTAL_OBJ
    if cu > 0: W.rectangle([X0 + 1, Y + 1, max(X0 + 1, int(xb)), Y + 11], fill=OLD)
    if cu > BEFORE:
        xa = X0 + (X1 - X0) * cu / TOTAL_OBJ
        W.rectangle([int(xb), Y + 1, int(xa), Y + 11], fill=NEW)
    xm = (X0 + X1) / 2
    W.rectangle([xm - 1, Y - 4, xm, Y + 16], fill=WHITE if cu >= HALF else INK2)
    text(W, 28, 144, f"{100 * cu / TOTAL_OBJ:4.1f}% OF ALL 24,865", fill=INK2)
    text(W, xm, 182, "HALF", fill=WHITE if cu >= HALF else INK2, align="c")

def hud(c, T):
    W = c.t; yy = year_at(T)
    W.rectangle([16, 14, 344, 112], fill=PANEL); W.rectangle([16, 14, 344, 15], fill=RIM); W.rectangle([16, 111, 344, 112], fill=RIM)
    text(W, 28, 18, "OBJECTS LAUNCHED INTO SPACE", fill=INK2)
    v = int(round(cum_at(T) - (CUM[yy] - DATA[yy]))) if T < T_END else DATA[Y1]
    k = nbeeps(T); fresh = k > 0 and T - BT[k - 1] < 0.1
    text(W, 28, 40, f"{v:,}", size=40, fill=(NEW if yy >= 2022 else OLD) if fresh else INK)
    text(W, 160, 58, "THIS YEAR", fill=INK2)
    text(W, 334, 40, str(yy), size=40, fill=GOLD, align="r")
    text(W, 28, 86, "EVERY BEEP = 20 OBJECTS", fill=INK2)

def fmt(n): return f"{n:,}"
BANNERS = [  # (time, title, sub, big, colour)
    (ystart(1959) + 0.02, "FIRST 20 OBJECTS", "1959 · FIRST BEEP", False, OLD),
    (ystart(1990) + 0.05, f"{min(DATA[y] for y in range(1965, 2013))} TO {max(DATA[y] for y in range(1965, 2013))} A YEAR",
     "1965-2012 · ALMOST 50 YEARS", False, OLD),
    (ystart(2020) + 0.05, fmt(DATA[2020]) + " IN 2020", f"2019: {DATA[2019]} · MORE THAN DOUBLE", False, NEW),
    (T_HALF, "HALF", f"{fmt(int(HALF + 0.5))} OF {fmt(TOTAL_OBJ)} · 2022", True, NEW),
    (ystart(2025) + 0.05, fmt(DATA[2025]), "IN 2025 · RECORD", True, NEW),
]
def banner(c, T):
    cand = [b for b in BANNERS if 0 <= T - b[0] < 1.5]
    if not cand: return
    t0, tt, sub, big, col = cand[-1]; a = T - t0
    W = c.t; yb = 476
    w = max((16 if big else 8) * len(tt), 8 * len(sub)) + 30
    hh = 60 if big else 42
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hh], fill=PANEL)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    W.rectangle([180 - w / 2, yb + hh - 1, 180 + w / 2, yb + hh], fill=col)
    if big:
        text(W, 180, yb + 3, tt, size=40, fill=col, align="c")
        if a > 0.12: text(W, 180, yb + 38, sub, fill=INK2, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if a > 0.12: text(W, 180, yb + 21, sub, fill=col, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_globe(c, T)
    c.art = Image.fromarray(draw_shell(c, T)); c.a = ImageDraw.Draw(c.art)
    if T < INTRO + 1.6 * YEAR or T >= SPUT_OUT - 0.2:
        _sput_ring(c, T)
    frise(c, T)
    return c

def _sput_ring(c, T):
    x, y, z = orbit_xyz(np.array([SPUT[0]]), SPUT[1], SPUT[2], SPUT[3], 0.6, T)
    if z[0] < 0 and x[0] ** 2 + y[0] ** 2 < 1: return
    px, py = GX + x[0] * GR, GY - y[0] * GR
    t0 = SPUT_IN if T < INTRO + 2 else SPUT_OUT
    ph = T - t0
    if 0 <= ph < 1.2 and (ph % 0.6) < 0.3:
        r = 2 + (ph % 0.6) * 12
        c.a.ellipse([px - r, py - r, px + r, py + r], outline=WHITE)

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 14, 344, 196], fill=PANEL); W.rectangle([16, 14, 344, 15], fill=RIM); W.rectangle([16, 195, 344, 196], fill=RIM)
    text(W, 28, 20, "4 OCT 1957 · SPUTNIK 1: BEEP", fill=INK2)
    if t > 0.5:
        text(W, 28, 44, "HALF OF EVERYTHING", size=40, fill=INK)
        text(W, 28, 80, "WE LAUNCHED WENT UP", size=40, fill=INK)
    if t > 0.9: text(W, 28, 116, "AFTER 2021", size=40, fill=GOLD)
    if t > 1.8: text(W, 28, 162, "EVERY BEEP = 20 OBJECTS LAUNCHED", fill=OLD)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); meter(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T); W = c.t
    if t < 0.9:                                          # the hum stops: silence, the shell keeps turning
        hud(c, T_END - 0.001); meter(c, T); return c
    W.rectangle([16, 14, 344, 196], fill=PANEL); W.rectangle([16, 14, 344, 16], fill=GOLD)
    text(W, 180, 20, f"{fmt(TOTAL_OBJ)} OBJECTS", size=40, fill=INK, align="c")
    text(W, 180, 58, "LAUNCHED 1957 TO 2025", fill=INK2, align="c")
    if t > 1.5:
        text(W, 30, 86, "1957-2021 · 65 YEARS", fill=OLD); text(W, 330, 82, fmt(BEFORE), size=40, fill=OLD, align="r")
    if t > 2.3:
        text(W, 30, 124, "2022-2025 · 4 YEARS", fill=NEW); text(W, 330, 120, fmt(AFTER), size=40, fill=NEW, align="r")
    if t > 3.1:
        text(W, 180, 164, f"{100 * AFTER / TOTAL_OBJ:.1f}% OF EVERYTHING, IN 4 YEARS", fill=INK, align="c")
    if t > 4.0: W.rectangle([16, 470, 344, 560], fill=PANEL)
    if t > 4.0: text(W, 180, 476, "WHAT WILL 2026 ADD?", size=40, fill=GOLD, align="c")
    if t > 4.6:
        text(W, 180, 516, "DATA: UNOOSA VIA OUR WORLD IN DATA", fill=INK2, align="c")
        text(W, 180, 536, "CHECKED WITH GCAT (J. McDOWELL)", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "plateau": sc_main("plateau"), "boom": sc_main("boom"), "outro": sc_outro}

def compose(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tb = np.repeat(np.repeat(np.array(c.txt), 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose(SCENEFN[name](t))
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.06) if ki >= 0 and T < T_END else 0.0
    z = 1.0 + 0.008 * kp * FXK; dx = dy = 0.0
    if ystart(2025) <= T < T_END:                       # the hum: the screen trembles
        dx = 3 * FXK * math.sin(T * 173); dy = 2 * FXK * math.cos(T * 151); z = max(z, 1.006)
    if 0 <= T - T_HALF < 0.3: z = max(z, 1.0 + 0.03 * FXK * (1 - (T - T_HALF) / 0.3))
    if z > 1.0005 or dx or dy: fr = warp(fr, z, dx, dy, z)
    if 0 <= T - T_HALF < 0.2:
        f = 0.35 * FXK * (1 - (T - T_HALF) / 0.2)
        fr = (fr * (1 - f) + np.array(NEW) * f).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.6)) / 0.6)
        if f > 0: fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.15)
        if f > 0: fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    return fr

# ================= audio (mood B "retro telemetry", co-pilot step 2) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def env(n, a, d):
        t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def noise(dur, fc, dec, seed, hp=None):
        n = int(dur * SR); s = lowpass(np.random.RandomState(seed % 2 ** 31).randn(n), fc)
        if hp: s = highpass(s, hp)
        return s * np.exp(-np.arange(n) / SR * dec)
    def kick(g=.26, f0=80, f1=46):
        n = int(.35 * SR); tt = np.arange(n) / SR
        return g * np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 16) + f1) / SR) * np.exp(-tt * 12)
    def square(f, dur, duty=.5):
        n = int(dur * SR); tt = np.arange(n) / SR
        return np.where((f * tt) % 1 < duty, 1.0, -1.0)
    n = int((TOTAL + 1.0) * SR); L = np.zeros(n)
    def put(t, sig, g=1.0):
        i = int(t * SR); j = min(n, i + len(sig))
        if 0 <= i < n: L[i:j] += g * sig[:j - i]
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if k == "kick": put(t, kick(v))
        elif k == "snare": put(t, noise(.12, 6000, 30, int(t * 997), 900), v)
        elif k == "hat": put(t, noise(.03, 9000, 140, int(t * 1009), 5000), v)
        elif k == "tri":
            nn = int(.45 * SR); tt = np.arange(nn) / SR
            put(t, v * (2 * np.abs(2 * ((mtof(kw["m"]) * tt) % 1) - 1) - 1) * env(nn, .005, .3))
        elif k == "bleep":
            d = kw["d"]; put(t, v * lowpass(square(mtof(kw["m"]), d, .25), 5000) * env(int(d * SR), .001, d / 2))
        elif k == "arp":
            put(t, v * lowpass(square(mtof(kw["m"]), .25, .125), 5000) * env(int(.25 * SR), .002, .12))
        elif k == "sput":
            nn = int(.3 * SR); g = np.minimum(1, np.minimum(np.arange(nn), nn - np.arange(nn)) / (.01 * SR))
            put(t, v * lowpass(square(mtof(81), .3, .5), 3000) * g)
        elif k == "crash": put(t, noise(1.6, 12000, 1.8, 1234, 3000), v)
        elif k == "carrier":                            # the hum turns into a buzzing radio carrier
            nn = int(kw["d"] * SR); tt = np.arange(nn) / SR
            s = lowpass(square(mtof(52), kw["d"], .5), 1800) + 0.5 * highpass(np.random.RandomState(9).randn(nn), 3000)
            put(t, v * s * (tt / kw["d"]) * (1 - np.exp(-(kw["d"] - tt) / .02)))
    out = L.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28)]:
        k_ = int(d * SR); out[k_:] += g * .6 * L[:-k_]
    L = .85 * L + .15 * lowpass(out, 4000)
    tt = np.arange(n) / SR; L *= np.clip((TOTAL + 0.4 - tt) / 1.0, 0, 1)
    L = L / (np.max(np.abs(L)) + 1e-9) * 0.89
    st = np.stack([L, np.roll(L, int(.011 * SR)) * .97], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(n / SR, 2), "s")

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    f0 = int(round(START[name] * FPS)); nf = int(round((START[name] + dur) * FPS)) - f0
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
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
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/{VARIANT}_t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print("TOTAL", round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, "objects", TOTAL_OBJ, "beeps", NB,
              "before", BEFORE, "after", AFTER, "T_HALF", round(T_HALF, 2))
        print(Counter(k for _, k, _ in EV))
        for b in BANNERS: print(round(b[0], 2), b[1], "|", b[2])
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
