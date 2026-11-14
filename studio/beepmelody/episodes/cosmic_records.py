"""BEEPMELODY — IN 1929 THE FARTHEST GALAXY WE KNEW WAS NEXT DOOR. NOW: 13.5 BILLION YEARS AGO.
cosmic-timeline, REWORK (r1 = C: the farthest-object record, r2 = A: "Cosmic drive+", 124 BPM).
36 records of the farthest object ever seen, 1914 -> 2025 (cosmic_records.csv, 2 sources per row).
One record = one pluck note, placed at its real date on a LINEAR year clock (0.47 s per year), snapped to the 16th grid.
Pitch = log10(1+z) (how stretched the light is) on an A minor pentatonic, A2..D6.
Scene (dark deep-field palette kept from v1): a vertical "look-back" well. Earth's telescope at the bottom, the Big Bang
wall at the top (13.8 billion years). Each record = a new object higher up + its light beam down to us; the gold record
line climbs like a ceiling. 1936 -> 1951: 15 years without a record -> the music stops (drums out, drone), the clock runs.

    python3 cosmic_records.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "cosmic_records.csv"))))
for r in REC:
    r["yr"] = int(r["year"]) + ((int(r["month"]) - 0.5) / 12 if r["month"] else 0.5)
    r["lb"] = float(r["lookback_gyr"]); r["lz"] = math.log10(1 + float(r["z"]))
N = len(REC)
AGE = 13.787                                   # Planck 2018 (age of the universe, Gyr)
I = {r["object"]: i for i, r in enumerate(REC)}
I_1929, I_HYDRA, I_3C9 = I["NGC 7619"], I["Hydra cluster galaxy"], I["3C 9"]
I_3C147 = I["3C 147"]; I_BOOTES = I["Bootes cluster galaxy"]
I_GRB, I_GNZ11, I_JADES, I_MOM = I["GRB 090423"], I["GN-z11"], I["JADES-GS-z13-0"], I["MoM-z14"]
I_87 = [i for i, r in enumerate(REC) if r["year"] == "1987"]
TYPE = {"galaxy": "GALAXY", "cluster galaxy": "GALAXY IN A CLUSTER", "radio galaxy": "RADIO GALAXY",
        "quasar": "QUASAR", "gamma-ray burst": "GAMMA-RAY BURST"}
NAME = {"M104 (Sombrero)": "M104 SOMBRERO", "Ursa Major cluster galaxy": "URSA MAJOR CLUSTER", "Leo cluster galaxy": "LEO CLUSTER",
        "Bootes cluster galaxy": "BOOTES CLUSTER", "Hydra cluster galaxy": "HYDRA CLUSTER", "CL 1358+62 arc": "CL 1358+62 ARC",
        "SDF J132418.3+271455": "SDF J132418+271455"}
def zfmt(z):
    z = float(z)
    return f"{z:.3f}".rstrip("0").rstrip(".") if z < 0.1 else (f"{z:.2f}".rstrip("0").rstrip(".") if z < 10 else f"{z:.2f}")

# ================= palette (dark deep field, kept from v1) =================
SKY = (6, 8, 22); INK = (232, 238, 255); INK2 = (132, 146, 190); CYAN = (90, 220, 255); GOLD = (255, 200, 80)
RED = (255, 96, 80); PINK = (255, 120, 200); BLUE = (140, 170, 255); PANEL = (14, 18, 44); RIM = (60, 72, 130)
def mix(a, b, f): return tuple(int(a[j] + (b[j] - a[j]) * f) for j in range(3))
def zcol(lz):                                   # light colour: bluer nearby -> redder far away
    f = min(1, lz / 1.19); return mix((170, 200, 255), (255, 70, 60), f) if f > .5 else mix((200, 220, 255), (255, 210, 140), f * 2)

# ================= timeline (124 BPM, 16th grid) =================
BPM = 124.0; BEAT = 60.0 / BPM; S16 = BEAT / 4
SPY = 0.47                                      # seconds per year (linear clock)
Y0, Y1 = 1913.5, 2026.0
HOOK = 8 * BEAT
def t_of(y): return HOOK + (y - Y0) * SPY
RT, last = [], -1
for r in REC:
    g = max(last + 1, round(t_of(r["yr"]) / S16)); RT.append(g * S16); last = g
HOLD = 8 * BEAT
T_END = RT[-1] + HOLD
OUTRO = 14 * BEAT
SC = [("hook", HOOK), ("a", RT[I_HYDRA] - HOOK), ("b", T_END - RT[I_HYDRA]), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
TOTAL = acc_
T_REWIND = 5 * BEAT
SIL0, SIL1 = RT[I_BOOTES] + 2 * BEAT, RT[I_HYDRA]          # the long silence 1936 -> 1951
def silent(T): return SIL0 <= T < SIL1
def year_at(T):
    if T < HOOK: return Y0
    return min(Y1, Y0 + (T - HOOK) / SPY)
def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan (r2 A: Cosmic drive+) =================
MINP = [0, 3, 5, 7, 10]
SCALE = [45 + 12 * o + i for o in range(4) for i in MINP][:18]          # A2 .. D6
LZ0, LZ1 = min(r["lz"] for r in REC), max(r["lz"] for r in REC)
def pitch(i): return SCALE[int(round((REC[i]["lz"] - LZ0) / (LZ1 - LZ0) * (len(SCALE) - 1)))]
ROOTS = [33, 29, 36, 31]                                                # Am - F - C - G
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT)) + 1
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4); ro = ROOTS[bar % 4]
        if t >= T_END:
            if t < TOTAL - 3 * BEAT:
                ev(t, "bass16", m=ro, open=0.5, v=0.055)
                if pos == 0:
                    for j, d in enumerate((12, 19, 24, 28)): ev(t + j * S16 * 2, "pluck", m=ro + 24 + d - 12, v=0.09)
            continue
        if silent(t):                                                    # 15 years without a record: drums out, a low drone
            if pos == 0 and t + 4 * BEAT <= SIL1 + 1e-6: ev(t, "drone", m=ro, d=4 * BEAT, v=0.15)
            continue
        hook = t < HOOK; prog = min(1.0, t / T_END)
        ev(t, "bass16", m=ro, open=(0.15 if hook else 0.25 + 0.6 * prog), v=0.05 if hook else 0.07)
        if hook and t < T_REWIND:
            ev(t + BEAT / 2, "hat", v=0.025); continue
        if hook: continue
        ev(t, "kick", v=0.55)
        if pos in (1, 3): ev(t, "clap", v=0.11)
        ev(t + BEAT / 2, "hat", v=0.04)
        if prog > 0.55: ev(t + BEAT / 4, "hat", v=0.02); ev(t + 3 * BEAT / 4, "hat", v=0.02)
    ev(0.25, "pluck", m=pitch(I_MOM), v=0.30); ev(0.25 + 3 * S16, "pluck", m=pitch(I_MOM), v=0.09)     # hook note: today's record
    ev(T_REWIND, "riser", d=HOOK - T_REWIND, v=0.14)
    for j in range(int((HOOK - T_REWIND) / S16)): ev(T_REWIND + j * S16, "hat", v=0.015 + 0.04 * j / 12)
    for i, t in enumerate(RT):
        m = pitch(i); big = i in (I_3C9, I_GRB, I_MOM, I_1929)
        ev(t, "pluck", m=m, v=0.32 + (0.08 if big else 0)); ev(t + 3 * S16, "pluck", m=m, v=0.09)
        if i in (0, I_HYDRA, I_3C9, I_GRB, I_JADES): ev(t, "crash", v=0.18)
        if i == I_HYDRA: ev(t, "kick", v=0.6); ev(t, "sub", v=0.3)
    ev(RT[-1], "crash", v=0.26); ev(RT[-1], "sub", v=0.4)
    for k, d in enumerate([0, 7, 12, 19, 24, 19, 12, 7, 0]):
        ev(RT[-1] + (k + 1) * S16 * 2, "pluck", m=pitch(N - 1) - 12 + d, v=0.20)
    ev(RT[-1] - 4 * BEAT, "riser", d=4 * BEAT, v=0.08)
    ev(SIL1 - 4 * BEAT, "riser", d=4 * BEAT, v=0.10)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= scene: the look-back well =================
EX, EY = 90, 244                                # Earth / telescope (art px)
TOPY = 84                                       # Big Bang wall
def ly(lb): return EY - 6 - (lb / AGE) * (EY - 6 - TOPY)
_rng = np.random.default_rng(7)
STARS = [(int(_rng.integers(0, AW)), int(_rng.integers(TOPY - 6, EY)), int(_rng.integers(0, 3))) for _ in range(150)]
POSX = []
for i, r in enumerate(REC):                     # spread objects left/right, deterministic
    POSX.append(int(26 + ((i * 0.618034) % 1) * (AW - 52)))
WALL = np.random.default_rng(3).random((8, AW // 2 + 1))

def star(d, x, y, col, s=1):
    d.point((x, y), fill=col)
    if s >= 1:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): d.point((x + dx, y + dy), fill=mix(col, SKY, .4))
    if s >= 2:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2), (3, 0), (-3, 0), (0, 3), (0, -3)): d.point((x + dx, y + dy), fill=mix(col, SKY, .6))
def galaxy(d, x, y, r, col, ang=0.0):
    if r < 1: return
    for j in range(40):
        th = j * 0.4 + ang; rr = r * j / 40
        for arm in (0, math.pi):
            d.point((int(x + rr * math.cos(th + arm)), int(y + rr * 0.45 * math.sin(th + arm))), fill=mix(col, SKY, rr / r * .6))
    d.point((x, y), fill=mix(col, (255, 255, 255), .5))
def obj(d, i, x, y, col, fresh):
    t = REC[i]["type"]
    if t == "quasar":
        star(d, x, y, col, 2 if fresh else 1)
    elif t == "gamma-ray burst":
        star(d, x, y, (255, 160, 255), 2)
        if fresh:
            for th in range(8):
                a = th * math.pi / 4; d.line([x + 4 * math.cos(a), y + 4 * math.sin(a), x + 8 * math.cos(a), y + 8 * math.sin(a)], fill=PINK)
    else:
        galaxy(d, x, y, 5 if fresh else 3, col, i)

def scene(c, T):
    d = c.a; k = rec_index(T)
    d.rectangle([0, 0, AW, AH], fill=SKY)
    for (x, y, s) in STARS: d.point((x, y), fill=mix([INK2, BLUE, INK][s], SKY, .55))
    # the Big Bang wall (the oldest light) at the top
    for x in range(0, AW, 2):
        for j in range(6):
            v = WALL[j, x // 2]; f = (1 - j / 6) * (0.55 + 0.45 * v)
            d.rectangle([x, TOPY - 8 + j, x + 1, TOPY - 8 + j], fill=mix(SKY, (255, 150, 70), f * .55))
    d.line([0, TOPY - 2, AW, TOPY - 2], fill=mix(SKY, (255, 170, 90), .6))
    # look-back axis on the left
    d.line([8, TOPY, 8, EY - 6], fill=RIM)
    for g in (1, 5, 10):
        yy = int(ly(g)); d.line([6, yy, 10, yy], fill=INK2)
    # Earth + telescope
    d.ellipse([EX - 30, EY - 2, EX + 30, EY + 22], fill=(30, 60, 120)); d.ellipse([EX - 30, EY - 2, EX + 30, EY + 4], fill=(50, 110, 70))
    d.polygon([(EX - 2, EY - 1), (EX + 2, EY - 1), (EX + 5, EY - 8), (EX + 1, EY - 9)], fill=INK)
    if T < HOOK:                                                  # hook: today's record flashes at the top
        if T > 0.2:
            x, y = POSX[I_MOM], int(ly(REC[I_MOM]["lb"])); a = T - 0.25
            obj(d, I_MOM, x, y, zcol(REC[I_MOM]["lz"]), True)
            if a < 1.6:
                q = min(1, a / 0.5); d.line([x, y, lerp(x, EX + 3, q), lerp(y, EY - 9, q)], fill=mix(RED, SKY, .2))
            if T < T_REWIND: d.rectangle([x - 7, y - 7, x + 7, y + 7], outline=PINK)
        return
    # record line (the ceiling) climbs to the current record
    if k >= 0:
        prev = ly(REC[k - 1]["lb"]) if k > 0 else EY - 6
        a = ease((T - RT[k]) / 0.3); yy = int(lerp(prev, ly(REC[k]["lb"]), a))
        for x in range(12, AW, 4): d.line([x, yy, x + 1, yy], fill=GOLD)
    # all records so far; the newest is bright with its light beam down to us
    for i in range(k + 1):
        x, y = POSX[i], int(ly(REC[i]["lb"])); col = zcol(REC[i]["lz"]); age = T - RT[i]
        fresh = i == k and age < 1.2
        if fresh:
            q = min(1, age / 0.25)
            d.line([x, y, lerp(x, EX + 3, q), lerp(y, EY - 9, q)], fill=mix(col, SKY, .15 + .6 * ease(age / 1.2)))
        obj(d, i, x, y, col if (fresh or i == k) else mix(col, SKY, .45), fresh)
    if silent(T):                                                  # the silence: a slow sweep, nothing found
        a = (T - SIL0) / (SIL1 - SIL0); yy = int(EY - 10 - (EY - TOPY - 10) * ((a * 3) % 1))
        d.line([12, yy, AW - 4, yy], fill=mix(SKY, CYAN, .25))

# ================= year clock (bottom) =================
BX0, BX1, BY = 14, 166, 268
def xy(y): return BX0 + (y - Y0) / (Y1 - Y0) * (BX1 - BX0)
def clock(c, T):
    d = c.a; W = c.t; k = rec_index(T); yr = year_at(T)
    d.rectangle([BX0 - 8, BY - 14, BX1 + 8, BY + 16], fill=PANEL, outline=RIM)
    d.rectangle([int(xy(REC[I_BOOTES]["yr"])) + 1, BY - 1, int(xy(REC[I_HYDRA]["yr"])) - 1, BY + 3], fill=mix(PANEL, RED, .25))
    d.rectangle([BX0, BY, BX1, BY + 2], fill=mix(RIM, PANEL, .3))
    d.rectangle([BX0, BY, int(xy(yr)), BY + 2], fill=CYAN)
    for i in range(k + 1):
        xx = int(xy(REC[i]["yr"])); d.line([xx, BY - 4, xx, BY - 1], fill=PINK if i == I_MOM else GOLD)
    d.rectangle([int(xy(yr)) - 1, BY - 2, int(xy(yr)) + 1, BY + 4], fill=INK)
    text(W, BX0 * 2, (BY - 13) * 2, "YEAR", fill=INK2)
    text(W, BX1 * 2, (BY - 13) * 2, str(min(2025, int(yr))) if T >= HOOK else "", fill=INK, align="r")
    for y, lab, al in ((1914, "1914", "l"), (1950, "1950", "c"), (2000, "2000", "c"), (2025, "2025", "r")):
        text(W, int(xy(y) * 2), (BY + 5) * 2, lab, fill=INK2, align=al)

def axis_labels(c):
    W = c.t
    text(W, 180, 153, "BIG BANG · 13.8 BILLION YEARS AGO", fill=(255, 205, 160), align="c")
    for g in (1, 5, 10):
        text(W, 26, int(ly(g)) * 2 - 9, f"{g} BN YR", fill=INK2)
    text(W, EX * 2 + 66, (EY - 7) * 2, "US", fill=INK2)

# ================= HUD, banners, footer =================
def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=RIM); W.rectangle([16, 121, 344, 122], fill=RIM)
    if k < 0: return
    r = REC[k]; age = T - RT[k]
    text(W, 28, 22, f"FARTHEST THING EVER SEEN · {r['year']}", fill=CYAN)
    text(W, 28, 44, r["shown"], size=40 if len(r["shown"]) <= 19 else 20, fill=(GOLD if age < 0.25 else INK))
    text(W, 28, 92, "ITS LIGHT TRAVELLED THAT LONG", fill=INK2)
    text(W, 334, 92, f"{k + 1}/{N}", fill=INK2, align="r")
    W.rectangle([16, 128, 344, 152], fill=PANEL); W.rectangle([16, 128, 19, 152], fill=PINK if k == I_MOM else CYAN)
    lab = f"{NAME.get(r['object'], r['object']).upper()} · {TYPE[r['type']]}"
    if len(lab) > 30: lab = NAME.get(r["object"], r["object"]).upper()
    text(W, 28, 131, lab, fill=INK)
    text(W, 334, 131, "Z " + r["z"], fill=INK2, align="r")

BANNERS = {I_1929: ("3,779 KM/S", "8.5 MILLION MPH · FLYING AWAY FROM US"),
           I_3C9: ("+5 BILLION YEARS", "IN ONE YEAR · QUASARS!"),
           I_87[1]: ("3 RECORDS IN 1987", "QUASAR HUNTERS"),
           I_GRB: ("A STAR EXPLODES", "SEEN 13.2 BILLION YEARS LATER"),
           I_GNZ11: ("HUBBLE'S RECORD", "GN-Z11 · 13.4 BILLION YEARS"),
           I_JADES: ("WEBB ARRIVES", "THE RECORD MOVES AGAIN"),
           I_MOM: ("WEBB · MOM-Z14", "280 MILLION YEARS AFTER THE BIG BANG")}
def box(W, xc, yb, tt, sub, accent, a=1.0):
    w = max(16 * len(tt) + 30, 8 * len(sub) + 30); hgt = 62
    x0, x1 = xc - w / 2, xc + w / 2
    W.rectangle([x0, yb, x1, yb + hgt], fill=PANEL)
    W.rectangle([x0, yb, x1, yb + 2], fill=accent); W.rectangle([x0, yb + hgt - 1, x1, yb + hgt], fill=RIM)
    text(W, xc, yb + 4, tt, size=40, fill=INK, align="c")
    if a > 0.2 and sub: text(W, xc, yb + 40, sub, fill=accent, align="c")
BY_BANNER = 330
def banner(c, T):
    k = rec_index(T); W = c.t
    if k < 0: return
    if silent(T):
        n = int(year_at(T)) - int(REC[I_BOOTES]["year"])
        box(W, 180, BY_BANNER, f"{max(1, n)} YEARS", "NO NEW RECORD", INK2, T - SIL0); return
    if I_GNZ11 <= k < I_JADES and RT[I_GNZ11] + 4 * BEAT < T:
        box(W, 180, BY_BANNER, "WAITING FOR WEBB", "NO NEW RECORD SINCE 2016", INK2, 1); return
    a = T - RT[k]
    if k not in BANNERS: return
    nxt = RT[k + 1] if k + 1 < N else T_END
    hold = min(nxt - RT[k], 6 * BEAT) * 0.95
    if k == I_MOM: hold = HOLD * 0.95
    if not (0.06 < a < hold): return
    tt, sub = BANNERS[k]
    box(W, 180, BY_BANNER, tt, sub, PINK if k == I_MOM else GOLD, a)

def footer(c, T):
    W = c.t
    W.rectangle([0, 600, 360, 640], fill=PANEL); W.rectangle([0, 600, 360, 601], fill=RIM)
    text(W, 10, 604, "EVERY BEEP = A NEW", fill=INK2); text(W, 10, 620, "FARTHEST THING SEEN", fill=CYAN)
    text(W, 350, 604, "HIGHER NOTE", fill=INK2, align="r"); text(W, 350, 620, "= FARTHER BACK", fill=GOLD, align="r")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); scene(c, T); clock(c, T); axis_labels(c)
    return c

def sc_hook(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 160], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=RIM); W.rectangle([16, 159, 344, 160], fill=RIM)
    text(W, 28, 22, "IN 1929 THE FARTHEST", size=40, fill=INK)
    if t > 0.25: text(W, 28, 58, "GALAXY WAS NEXT DOOR.", size=40, fill=INK)
    if t > 0.6: text(W, 28, 94, "NOW: 13.5 BILLION", size=40, fill=PINK)
    if t > 0.9: text(W, 28, 134, "YEARS AGO.", fill=INK)
    if t >= T_REWIND: box(W, 180, BY_BANNER, "BACK TO 1914", "EVERY RECORD, ONE BEEP EACH", CYAN, t - T_REWIND)
    footer(c, T)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T); footer(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T_END); W = c.t
    W.rectangle([0, 0, 360, 600], fill=PANEL); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, f"{N} RECORDS · 1914-2025", fill=INK2, align="c")
    rows = [("180 M YR", "1929 · HUBBLE & HUMASON", CYAN), ("+5 BN YR", "1965 · ONE QUASAR, ONE YEAR", GOLD),
            ("15 YEARS", "1936-1951 · NO RECORD", INK2), ("13.5 BN YR", "2025 · WEBB, MOM-Z14", PINK)]
    for j, (a, b, col) in enumerate(rows):
        if t > 0.3 + j * 0.45:
            text(W, 28, 84 + j * 56, a, size=40, fill=col); text(W, 332, 116 + j * 56, b, fill=INK, align="r")
    if t > 2.2:
        text(W, 180, 330, "LIGHT TRAVEL TIME, FROM THE REDSHIFT", fill=INK2, align="c")
        text(W, 180, 348, "(PLANCK 2018 COSMOLOGY)", fill=INK2, align="c")
    if t > 2.6:
        W.rectangle([40, 440, 320, 441], fill=INK2)
        text(W, 180, 448, "DATA: DISCOVERY PAPERS (PNAS, APJ,", fill=INK2, align="c")
        text(W, 180, 466, "NATURE...) + NASA, ESA, ESO, STSCI,", fill=INK2, align="c")
        text(W, 180, 484, "SUBARU, CALTECH · 2 SOURCES PER RECORD", fill=INK2, align="c")
    return c

SCENEFN = {"hook": sc_hook, "a": sc_main("a"), "b": sc_main("b"), "outro": sc_outro}

def compose(c):
    art = np.array(c.art); big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt); tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose(SCENEFN[name](t))
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    z = 1.0 + 0.008 * kp * FXK
    if abs(T - RT[-1]) < 0.4: z += 0.03 * FXK * math.exp(-abs(T - RT[-1]) / 0.12)
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if name in ("a", "b") and k >= 0 and T - RT[k] < 0.08:
        fr = np.minimum(255, fr.astype(np.int16) + int(40 * FXK * (1 - (T - RT[k]) / 0.08))).astype(np.uint8)
    if name == "hook" and abs(t - 0.25) < 0.08:
        fr = np.minimum(255, fr.astype(np.int16) + int(30 * FXK)).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(SKY) * f).astype(np.uint8)
    return fr

# ================= audio (r2 A, full length) =================
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
    def lp(x, fc): return lfilter(*butter(2, min(fc, SR / 2 - 100) / (SR / 2)), x)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fx, i, x * send)
    def pluck(f, m_=int(.9 * SR)):
        tt = np.arange(m_) / SR
        s = sum((1 / h) * np.sin(2 * np.pi * f * h * 1.002 * tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
        return s * env(m_, .002, .35)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "pluck":
            put(t, pluck(mtof(kw["m"])) * v, pan=0.1, send=0.3)
        elif k == "bass16":
            for q in range(4):
                m_ = int(S16 * .9 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"] + [0, 12, 7, 12][q])
                put(t + q * S16, lp(2 * ((f * tt) % 1) - 1, 500 + 900 * kw["open"]) * np.exp(-tt * 9) * v * 1.6, pan=-0.15)
        elif k == "drone":
            d = kw["d"]; m_ = int(d * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = lp(np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 1.5 * tt) + .3 * np.sin(2 * np.pi * f * 2.004 * tt), 600)
            put(t, x * np.minimum(1, tt / .4) * np.clip((d - tt) / .4, 0, 1) * v, send=0.3)
        elif k == "kick":
            m_ = int(0.35 * SR); tt = np.arange(m_) / SR
            x = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 16) + 46) / SR) * np.exp(-tt * 12)
            put(t, np.tanh(1.5 * x) * v * 0.8)
        elif k == "sub":
            m_ = int(1.4 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * np.cumsum(55 * np.exp(-tt * 3) + 33) / SR) * np.exp(-tt * 2.5) * v)
        elif k == "clap":
            m_ = int(0.16 * SR); x = lp(rng.standard_normal(m_), 5000) * np.exp(-np.arange(m_) / SR * 18)
            put(t, x * v * 1.2, send=0.15)
        elif k == "hat":
            m_ = int(0.04 * SR)
            x = lfilter(*butter(2, 8000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.001, 0.012)
            put(t, x * v * 2.5, pan=0.3)
        elif k == "crash":
            m_ = int(1.6 * SR)
            put(t, lfilter(*butter(2, 5000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.002, 0.45) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            put(t, lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    out = fx.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
        k_ = int(dl * SR); out[k_:] += g * .6 * fx[:-k_]
    out = lp(out, 4000)
    L += out * 0.45; R += np.roll(out, 400) * 0.45
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
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV), "silence", round(SIL0, 2), round(SIL1, 2))
        for i, t in enumerate(RT):
            r = REC[i]; print(f"{t:6.2f}s  {r['yr']:8.2f}  p{pitch(i)}  {r['shown']:<20} {r['object']}")
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
