"""BEEPMELODY — KYOTO'S CHERRY TREES NOW BLOOM 2 WEEKS EARLY. Full-flowering date of the cherry trees in Kyoto,
812 -> 2026 (Aono, Kazui & Saito series, 838 years; cross-checked: Our World in Data / R. Olson 2026, JMA for 2021-26).
One decade = one koto note (decade mean, 810s -> 2010s; 3 decades without any record stay silent), then every spring
2020 -> 2026 one by one. Earlier bloom = higher note (Japanese "in" scale on A).
Mood chosen in co-pilot step 2 ("Instrument japonais"): koto garden, 72 BPM, soft taiko, bamboo-flute drone.
Picture (co-pilot step 3: "night" + "une scene en mouvement"): night hanami, a cherry tree by the river under the moon,
paper lanterns, a drifting boat, falling petals, swaying canopy; calendar card, chart of bloom date by year (earlier = up).

    python3 kyoto_cherry.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import datetime as dt
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.5"))

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "kyoto_cherry.csv"))))
def cal_day(s):                      # calendar day in a non-leap year: Apr 14 = 104 (dates compared as calendar dates)
    y, m, d = map(int, s.split("-")[:3]); return (dt.date(2001, m, d) - dt.date(2001, 1, 1)).days + 1
YD = {int(r["year"]): cal_day(r["bloom_date"]) for r in ROWS}
DECS = list(range(810, 2020, 10))                       # 121 decades, 810s -> 2010s
DM, DN, DMIN = {}, {}, {}
for d in DECS:
    v = [(YD[y], y) for y in range(d, d + 10) if y in YD]
    if v:
        DM[d] = sum(a for a, _ in v) / len(v); DN[d] = len(v); DMIN[d] = min(v)
SPR = list(range(2020, 2027))                           # each spring, 2020 -> 2026
AVG_ALL = sum(YD.values()) / len(YD)                    # 104.1 -> Apr 14
AVG_D = int(round(AVG_ALL))
OLD_REC = min(v for y, v in YD.items() if y < 2021)     # Mar 27 (1236, 1409, 1612)
MON = ["JAN", "FEB", "MAR", "APR", "MAY"]
MONL = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY"]
def ddate(doy):
    x = dt.date(2001, 1, 1) + dt.timedelta(days=int(round(doy)) - 1); return x.month, x.day
def fdate(doy, long=False):
    m, d = ddate(doy); return f"{(MONL if long else MON)[m - 1]} {d}"
def era(y): return "heian" if y < 1190 else "medieval" if y < 1600 else "edo" if y < 1870 else "modern"
ERAS = ["heian", "medieval", "edo", "modern"]
ERA_NAME = {"heian": "HEIAN", "medieval": "MEDIEVAL", "edo": "EDO", "modern": "MODERN"}
ERA_LINE = {"heian": "HEIAN PERIOD", "medieval": "KAMAKURA + MUROMACHI", "edo": "EDO PERIOD", "modern": "MODERN JAPAN"}

# ================= palette (night hanami, dark) =================
INK = (244, 236, 248)
INK2 = (156, 148, 196)
PINK = (255, 122, 164)
GOLD = (255, 202, 96)
CREAM = (22, 20, 44)          # panel background (dark)
NIGHT = (12, 10, 28)          # fades
CARD = (34, 30, 62)
WHITE = (255, 255, 255)
ECOL = {"heian": (190, 146, 236), "medieval": (104, 196, 214), "edo": (244, 156, 92), "modern": (255, 122, 164), "spring": (255, 122, 164)}
BLOS = [(255, 214, 230), (246, 178, 204), (255, 238, 244), (232, 146, 182)]
GREEN = (36, 52, 58)

# ================= timeline (all on the beat) =================
BPM = 72.0
BEAT = 60.0 / BPM
INTRO_B, DEC_B, GAP_B, SPR_B, HOLD_B, OUTRO_B = 4, 0.5, 1.0, 1.25, 2.5, 7
def t_dec(d): return (INTRO_B + (d - 810) / 10 * DEC_B) * BEAT
T_SPR0 = t_dec(2010) + (DEC_B + GAP_B) * BEAT
def t_spr(y): return T_SPR0 + (y - 2020) * SPR_B * BEAT
T_LAST = t_spr(2026)
T_END_MAIN = T_LAST + HOLD_B * BEAT
TOTAL = T_END_MAIN + OUTRO_B * BEAT
SC = [("intro", t_dec(810)), ("heian", t_dec(1190) - t_dec(810)), ("medieval", t_dec(1600) - t_dec(1190)),
      ("edo", t_dec(1870) - t_dec(1600)), ("modern", T_SPR0 - t_dec(1870)), ("springs", T_END_MAIN - T_SPR0), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

# every step of the series: (time, kind, key, value)  kind = "dec" | "spr"
STEPS = [(t_dec(d), "dec", d, DM.get(d)) for d in DECS] + [(t_spr(y), "spr", y, YD[y]) for y in SPR]
def step_at(T):
    k = None
    for s in STEPS:
        if s[0] <= T + 1e-9: k = s
        else: break
    return k
def is_rec(s): return s[1] == "spr" and s[2] in (2021, 2023)

# ================= music plan (shared by picture + audio) =================
SCALE = [57, 58, 62, 64, 65, 69, 70, 74, 76, 77, 81, 82, 86, 88, 89]     # A "in" scale (A Bb D E F), A3 -> F6
LATE, EARLY = 116.0, 84.0
def lev(v): return float(np.clip((LATE - v) / (LATE - EARLY), 0, 1))
def pitch(v): return SCALE[int(round(lev(v) * (len(SCALE) - 1)))]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    ev(0.10, "koto", m=69, v=0.50); ev(0.10, "taiko", v=0.55)
    ev(0.0, "drone", d=TOTAL, v=1.0)
    for b in range(nb):
        t = b * BEAT
        main = t_dec(810) - 2 * BEAT <= t < T_END_MAIN
        modern = t_dec(1870) <= t < T_END_MAIN
        if main:
            if b % 2 == 0: ev(t, "taiko", v=0.42 if not modern else 0.50)
            else: ev(t, "rim", v=0.10)
            if modern:
                for h in range(2): ev(t + h * BEAT / 2, "shaker", v=0.05 if h else 0.07)
                if b % 4 == 3: ev(t + BEAT / 2, "taiko", v=0.28)
        elif t >= T_END_MAIN and b % 4 == 0 and t < TOTAL - 2 * BEAT:
            ev(t, "taiko", v=0.26)
    for s in STEPS:
        t, kind, key, v = s
        if v is None: continue                           # decade without any record: silence
        rec = is_rec(s)
        ev(t, "koto", m=pitch(v), v=0.40 + 0.22 * lev(v) + (0.12 if kind == "spr" else 0), echo=rec or kind == "spr")
        if t >= t_dec(1870): ev(t, "koto2", m=pitch(v) - 5, v=0.14)    # soft fourth below once the curve starts to climb
        if rec:
            ev(t, "taiko", v=0.80); ev(t, "rin", m=pitch(v) + 12, v=0.30)
    for k, d in enumerate([0, 5, 7, 12, 17, 19, 24]):                  # rising koto run after the last spring
        ev(T_LAST + 1.0 * BEAT + k * BEAT / 4, "koto", m=57 + d + 12, v=0.34, echo=False)
    ev(T_END_MAIN + 0.5 * BEAT, "rin", m=81, v=0.26)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, kw in EV if k == "taiko" and kw["v"] >= 0.4)
NOTES = [(t, kw) for t, k, kw in EV if k == "koto"]

# ================= drawing =================
CH_X0, CH_X1, CH_TOP, CH_H = 30, 172, 244, 44
DTOP, DBOT = 82.0, 118.0
def chx(y): return CH_X0 + (y - 800) / (2030 - 800) * (CH_X1 - CH_X0)
def chy(v): return CH_TOP + (v - DTOP) / (DBOT - DTOP) * CH_H
TREE = (52, 150)
_rnd = random.Random(7)
CANOPY = []
for _ in range(900):
    a = _rnd.uniform(0, 2 * math.pi); r = 34 * math.sqrt(_rnd.random())
    x = TREE[0] + r * math.cos(a) * 1.25; y = TREE[1] + r * math.sin(a) * 0.78
    CANOPY.append((int(x), int(y), _rnd.randrange(4)))
_HILL_BLOS = [(random.Random(s).uniform(0, AW), random.Random(s + 3).uniform(0, 1)) for s in range(60)]

def far_h(x): return 168 - 22 * math.sin(x / 34 + 0.6) - 9 * math.sin(x / 13)
def mid_h(x): return 190 - 10 * math.sin(x / 22 + 2) - 4 * math.sin(x / 7)
def _sky():
    img = Image.new("RGB", (AW, AH)); d = ImageDraw.Draw(img)
    for y in range(AH):
        f = max(0.0, min(1.0, (y - 60) / 150))
        d.line([0, y, AW, y], fill=tuple(int(lerp(a, b, f)) for a, b in zip((10, 10, 34), (48, 34, 78))))
    return img
def _hills():
    img = Image.new("RGBA", (AW, AH), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.polygon([(0, 214)] + [(x, far_h(x)) for x in range(0, AW + 1, 2)] + [(AW, 214)], fill=(28, 30, 58, 255))
    for x, f in _HILL_BLOS:
        d.point((int(x), int(far_h(x) + 4 + f * 36)), fill=(120, 90, 130, 255))
    d.polygon([(0, 214)] + [(x, mid_h(x)) for x in range(0, AW + 1, 2)] + [(AW, 214)], fill=GREEN + (255,))
    return img
SKY_IMG, HILL_IMG = _sky(), _hills()
_r2 = random.Random(11)
STARS = [(x, y, _r2.uniform(0, 6.3), _r2.uniform(1.5, 4.0)) for x, y in ((_r2.randrange(AW), _r2.randrange(62, 175)) for _ in range(90)) if y < far_h(x) - 2]
CLOUDS = [(_r2.uniform(0, AW + 60), _r2.uniform(70, 130), _r2.randrange(18, 34), _r2.uniform(1.0, 2.2)) for _ in range(5)]
LANTERNS = [(94, 201), (106, 201), (118, 201), (130, 201), (142, 201), (154, 201), (166, 201), (24, 172), (78, 166)]
AMBIENT = [(_r2.uniform(-10, AW), _r2.uniform(0, 1), _r2.uniform(5, 9), _r2.uniform(0, 6.3), _r2.randrange(4)) for _ in range(26)]

def moon_pos(T): return 146, 132 - 16 * min(1.0, T / TOTAL)

def draw_bg(T):
    img = SKY_IMG.copy(); d = ImageDraw.Draw(img)
    for x, y, ph, sp in STARS:                                    # twinkling stars
        b = 0.5 + 0.5 * math.sin(T * sp + ph)
        if b > 0.25: d.point((x, y), fill=tuple(int(c * b) for c in (230, 226, 255)))
    mx, my = moon_pos(T)                                         # slowly rising moon + halo
    for r, col in ((14, (44, 40, 86)), (11, (64, 58, 112))): d.ellipse([mx - r, my - r, mx + r, my + r], fill=col)
    d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(250, 240, 214)); d.point((mx - 3, my - 2), fill=(226, 214, 190)); d.rectangle([mx + 2, my + 2, mx + 3, my + 3], fill=(230, 218, 192))
    for x0, y, w, sp in CLOUDS:                                  # thin clouds drifting right
        x = (x0 + T * sp) % (AW + 80) - 40
        d.rectangle([x, y, x + w, y + 1], fill=(58, 50, 96)); d.rectangle([x + 5, y - 1, x + w - 6, y - 1], fill=(52, 46, 90))
    img.paste(HILL_IMG, (0, 0), HILL_IMG); d = ImageDraw.Draw(img)
    # river: moving ripples, moon + lantern reflections
    d.rectangle([0, 214, AW, 238], fill=(22, 30, 64))
    for k in range(0, AW + 12, 9):
        x = (k + T * 4) % (AW + 12) - 6; yy = 218 + (k // 9) % 4 * 5
        d.line([x, yy, x + 4, yy], fill=(48, 62, 104))
    for j in range(10):
        yy = 216 + j * 2; w = 5 - j // 3 + int(1.5 * math.sin(T * 3 + j))
        d.line([mx - w + math.sin(T * 2 + j) * 1.5, yy, mx + w + math.sin(T * 2 + j) * 1.5, yy], fill=(214, 202, 170) if j % 2 == 0 else (120, 116, 128))
    # bridge with paper lanterns (swaying, flickering) + their reflections
    d.rectangle([84, 209, AW, 211], fill=(60, 40, 40))
    for x in range(88, AW, 10): d.line([x, 211, x, 218], fill=(60, 40, 40))
    d.line([84, 197, AW, 197], fill=(70, 50, 50))
    # boat crossing the river over the whole video
    bx = -16 + (AW + 30) * (T / TOTAL); by = 229 + 0.6 * math.sin(T * 2.2)
    d.polygon([(bx, by), (bx + 16, by), (bx + 13, by + 3), (bx + 3, by + 3)], fill=(16, 12, 24))
    d.line([bx + 8, by, bx + 8, by - 6], fill=(16, 12, 24))
    fl = 0.8 + 0.2 * math.sin(T * 11)
    d.rectangle([bx + 7, by - 9, bx + 9, by - 7], fill=tuple(int(c * fl) for c in (255, 170, 80)))
    d.line([bx + 8, by + 4, bx + 8, by + 7], fill=(150, 100, 60))
    # bank + tree (canopy sways in the wind)
    d.polygon([(0, 238), (0, 206), (40, 204), (92, 212), (110, 238)], fill=(26, 38, 42))
    d.polygon([(46, 238), (50, 180), (56, 180), (62, 238)], fill=(44, 30, 34))
    for (x0, y0, x1, y1) in [(52, 186, 30, 158), (54, 184, 78, 152), (53, 182, 52, 140), (40, 172, 22, 166), (66, 170, 86, 168)]:
        d.line([x0, y0, x1 + round(1.2 * math.sin(T * 1.1 + x1)), y1], fill=(44, 30, 34), width=2)
    for x, y, c in CANOPY:
        sw = round((1.0 + (186 - y) / 30) * math.sin(T * 1.1 + y * 0.09 + x * 0.02))
        d.point((x + sw, y), fill=BLOS[c])
    for i, (lx, ly) in enumerate(LANTERNS):
        sw = 1.4 * math.sin(T * 1.6 + i * 0.9); f = 0.82 + 0.18 * math.sin(T * (7 + i) + i)
        x = lx + sw; y = ly
        d.line([lx, ly - 4, x, y - 1], fill=(90, 70, 60))
        d.point((x - 3, y + 1), fill=(120, 60, 50)); d.point((x + 3, y + 1), fill=(120, 60, 50))
        d.rectangle([x - 1, y, x + 1, y + 3], fill=tuple(int(c * f) for c in (255, 150, 90)))
        d.point((x, y + 1), fill=tuple(int(c * f) for c in (255, 226, 160)))
        if ly > 190:
            for j in range(4): d.point((x + math.sin(T * 3 + j + i), 216 + j * 4), fill=(150, 90, 60) if j % 2 == 0 else (90, 60, 60))
    return img

def petals(d, T):
    for x0, ph, sp, wob, c in AMBIENT:                            # petals always drifting down
        f = (ph + T / sp) % 1.0
        x = x0 + f * 40 + 3 * math.sin(T * 1.5 + wob); y = 62 + f * 176
        if y < 236: d.point((int(x), int(y)), fill=BLOS[c])
    for i, (t, kw) in enumerate(NOTES):                          # a burst of petals on every note
        a = T - t
        if a < 0: break
        if a > 2.6: continue
        n = 3 + int(round(7 * lev_of(kw["m"])))
        rg = random.Random(i * 31 + 5)
        for k in range(n):
            x0, y0, _ = CANOPY[rg.randrange(len(CANOPY))]
            x = x0 + a * rg.uniform(8, 22) + 2.5 * math.sin(a * 5 + k)
            y = y0 + a * rg.uniform(14, 30)
            if y < 236: d.point((int(x), int(y)), fill=BLOS[(k % 2) * 3] if k % 3 else WHITE)
def lev_of(m): return (SCALE.index(m) / (len(SCALE) - 1)) if m in SCALE else 0.6

def chart(c, T, st):
    d = c.a; W = c.t
    d.rectangle([0, 238, AW, 300], fill=CREAM); d.line([0, 238, AW, 238], fill=INK2)
    for v, col in ((AVG_D, INK2), (OLD_REC, PINK)):
        y = int(round(chy(v)))
        for x in range(CH_X0, CH_X1 + 1, 3): d.point((x, y), fill=col)
    text(W, 2 * CH_X0 - 4, int(chy(OLD_REC) * 2) - 8, "MAR 27", fill=PINK, align="r")
    text(W, 2 * CH_X0 - 4, int(chy(AVG_D) * 2) - 20, "AVG", fill=INK2, align="r")
    text(W, 2 * CH_X0 - 4, int(chy(AVG_D) * 2) - 4, "APR 14", fill=INK2, align="r")
    text(W, 2 * CH_X0 - 4, int(chy(115) * 2) - 8, "APR 25", fill=INK2, align="r")
    text(W, 2 * CH_X1 - 22, int(chy(OLD_REC) * 2) - 18, "OLD RECORD", fill=PINK, align="r")
    if st is not None:
        prev = None
        for s in STEPS:
            if s[0] > T + 1e-9: break
            if s[3] is None: prev = None; continue
            x, y = chx(s[2] + (5 if s[1] == "dec" else 0)), chy(s[3])
            col = ECOL[era(s[2])] if s[1] == "dec" else ECOL["spring"]
            if s[1] == "dec" and prev is not None: d.line([prev[0], prev[1], x, y], fill=col)
            else: d.point((int(round(x)), int(round(y))), fill=col)
            prev = (x, y) if s[1] == "dec" else prev
        if st[3] is not None:
            x, y = chx(st[2] + (5 if st[1] == "dec" else 0)), chy(st[3]); a = T - st[0]
            d.rectangle([int(x) - 1, int(y) - 1, int(x) + 1, int(y) + 1], fill=GOLD)
            if a < 0.4: r = 2 + a * 14; d.ellipse([x - r, y - r, x + r, y + r], outline=GOLD)
    d.line([CH_X0, CH_TOP + CH_H + 2, CH_X1, CH_TOP + CH_H + 2], fill=INK2)
    for y, al in ((812, "l"), (1200, "c"), (1600, "c"), (2026, "r")):
        x = chx(y); d.line([x, CH_TOP + CH_H + 3, x, CH_TOP + CH_H + 4], fill=INK2)
        text(W, 2 * x + (-4 if al == "l" else 4 if al == "r" else 0), 2 * (CH_TOP + CH_H) + 6, str(y), fill=INK2, align=al)
    text(W, 2 * CH_X0, 478, "^ EARLIER", fill=INK, align="l")

def calendar(c, T, st):
    W = c.t
    x0, y0, x1, y1 = 236, 332, 340, 438
    W.rectangle([x0 + 4, y0 + 4, x1 + 4, y1 + 4], fill=(6, 4, 14))
    W.rectangle([x0, y0, x1, y1], fill=CARD); W.rectangle([x0, y0, x1, y0 + 26], fill=PINK)
    if st is None or st[3] is None:
        text(W, (x0 + x1) / 2, y0 + 3, "NO DATE" if st else "SPRING", fill=WHITE, align="c")
        text(W, (x0 + x1) / 2, y0 + 40, "?" if st else "...", size=40, fill=INK2, align="c"); return
    m, dd = ddate(st[3]); a = T - st[0]
    text(W, (x0 + x1) / 2, y0 + 3, MONL[m - 1], fill=WHITE, align="c")
    text(W, (x0 + x1) / 2, y0 + 36, str(dd), size=40, fill=GOLD if a < 0.25 else INK, align="c")
    text(W, (x0 + x1) / 2, y0 + 80, "AVG" if st[1] == "dec" else "FULL BLOOM", fill=INK2, align="c")

NOTE = {1230: "1236: MARCH 27, EARLIEST YET", 1400: "1409: MARCH 27 AGAIN", 1610: "1612: MARCH 27, A THIRD TIME",
        820: "NO BLOOM DATE SURVIVES", 840: "NO BLOOM DATE SURVIVES", 870: "NO BLOOM DATE SURVIVES",
        2021: "MARCH 26: BEATS MARCH 27", 2023: "MARCH 25: BEATS 2021"}
def hud(c, T):
    W = c.t; st = step_at(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if st is None:
        text(W, 28, 22, "FULL BLOOM IN KYOTO", fill=INK2); text(W, 28, 44, "...", size=40, fill=INK); return
    t0, kind, key, v = st; a = T - t0
    col = ECOL[era(key)] if kind == "dec" else ECOL["spring"]
    text(W, 28, 22, "AVG FULL BLOOM IN THE" if kind == "dec" else "FULL BLOOM IN", fill=INK2)
    lab = f"{key}s" if kind == "dec" else str(key)
    text(W, 28, 44, lab, size=40, fill=col if a < 0.22 else INK)
    if v is None:
        text(W, 334, 44, "-", size=40, fill=INK2, align="r"); text(W, 28, 92, "NO RECORD THIS DECADE", fill=INK2)
    else:
        text(W, 334, 44, fdate(v), size=40, fill=GOLD, align="r")
        dd = int(round(v)) - AVG_D
        txt = "ON THE 1,200-YR AVERAGE" if dd == 0 else (f"{-dd} DAY{'S' if dd != -1 else ''} EARLIER THAN AVG" if dd < 0 else f"{dd} DAY{'S' if dd != 1 else ''} LATER THAN AVG")
        text(W, 28, 92, txt, fill=PINK if dd <= -7 else INK2)
    W.rectangle([16, 128, 344, 160], fill=CARD); W.rectangle([16, 128, 19, 160], fill=col)
    line = NOTE.get(key, ERA_LINE[era(key)] if kind == "dec" else "SPRINGS ONE BY ONE")
    n = int(min(60, 3 + a * 200))
    text(W, 28, 134, line[:max(0, n)], fill=INK if key in NOTE else col)

def legend(c, T):
    W = c.t
    W.rectangle([0, 604, 360, 640], fill=CREAM); W.rectangle([0, 604, 360, 605], fill=INK2)
    for j, e in enumerate(ERAS):
        vals = [s[3] for s in STEPS if s[1] == "dec" and s[3] is not None and era(s[2]) == e and s[0] <= T + 1e-9]
        x = 45 + j * 90
        text(W, x, 607, ERA_NAME[e], fill=ECOL[e], align="c")
        if vals:
            allv = [YD[y] for y in YD if era(y) == e and y < 2020 and any(s[0] <= T + 1e-9 and s[1] == "dec" and s[2] == y // 10 * 10 for s in STEPS)]
            text(W, x, 622, fdate(sum(allv) / len(allv)), fill=INK, align="c")
        else:
            text(W, x, 622, "...", fill=INK2, align="c")

def _bkey(T):
    for key, (tt, sub, big, hb) in BANNERS.items():
        t0 = t_dec(key) if key < 2020 else t_spr(key)
        if 0.1 < T - t0 < hb * BEAT: return key, T - t0
    return None, 0
BANNERS = {810: ("812 · APRIL 1", "THE FIRST BLOOM ON RECORD", False, 2.5),
           1230: ("1236 · MARCH 27", "THE EARLIEST BLOOM YET", False, 4),
           1400: ("1409 · MARCH 27", "STILL UNBEATEN 600 YEARS LATER", False, 4),
           1990: ("THE NOTES CLIMB", f"1990s AVG: {fdate(DM[1990], True)}", False, 4),
           2020: ("NOW ONE NOTE", "PER SPRING", False, 1.2),
           2021: ("NEW RECORD", "MARCH 26 · EARLIEST IN 1,200 YEARS", True, 1.6),
           2023: ("AGAIN.", "MARCH 25 · TWO SPRINGS LATER", True, 2.4)}
def banner(c, T):
    key, a = _bkey(T)
    if key is None: return
    tt, sub, big, hb = BANNERS[key]
    W = c.t; yb = 176
    w = max((16 if big else 8) * len(tt) + 30, 8 * len(sub) + 30)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + (62 if big else 42)], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=PINK)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if a > 0.2: text(W, 180, yb + 40, sub, fill=PINK, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if a > 0.3: text(W, 180, yb + 21, sub, fill=PINK, align="c")

def draw_scene(c, T):
    c.art = draw_bg(T); c.a = ImageDraw.Draw(c.art)
    petals(c.a, T)
    st = step_at(T)
    if st is not None and st[3] is not None and 0 <= T - st[0] < 0.4 and is_rec(st):
        r = 10 + (T - st[0]) * 90
        c.a.ellipse([TREE[0] - r * 1.25, TREE[1] - r * .8, TREE[0] + r * 1.25, TREE[1] + r * .8], outline=GOLD)
    chart(c, T, st)
    calendar(c, T, st)

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, T); legend(c, T); return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 26, "1,200 SPRINGS", size=40, fill=INK)
    if t > 0.4: text(W, 28, 64, "IN KYOTO", size=40, fill=PINK)
    if t > 1.0: text(W, 28, 112, "EVERY NOTE = A DECADE OF BLOOMS", fill=INK2)
    if t > 1.6: text(W, 28, 140, "EARLIER BLOOM = HIGHER NOTE", fill=INK2)
    if t > 2.0:
        W.rectangle([70, 196, 290, 238], fill=CREAM); W.rectangle([70, 196, 290, 198], fill=GOLD)
        text(W, 180, 199, "CHERRY TREES, FULL BLOOM", fill=INK, align="c")
        text(W, 180, 218, "812 TO 2026", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t; c = frame_ctx(T); hud(c, T); banner(c, T); return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T); W = c.t
    W.rectangle([16, 40, 344, 330], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=PINK)
    text(W, 180, 50, "FULL BLOOM IN KYOTO", fill=INK2, align="c")
    old = [v for y, v in YD.items() if y < 1900]; new = [YD[y] for y in SPR]
    rows = [("812-1899", fdate(sum(old) / len(old)), "AVERAGE", "heian"), ("2020-2026", fdate(sum(new) / len(new)), "AVERAGE", "modern"),
            ("RECORD", fdate(YD[2023]), "2023", "edo")]
    for j, (a, b, s, e) in enumerate(rows):
        if t > 0.4 + j * 0.7:
            y = 78 + j * 64
            text(W, 30, y, a, fill=ECOL[e]); text(W, 330, y - 6, b, size=40, fill=INK, align="r")
            text(W, 330, y + 32, s, fill=INK2, align="r")
    if t > 2.6: text(W, 180, 270, "ABOUT 2 WEEKS EARLIER", fill=PINK, align="c")
    if t > 3.3: text(W, 180, 296, "WILL 2027 BEAT MARCH 25?", fill=GOLD, align="c")
    if t > 3.6:
        W.rectangle([0, 470, 360, 600], fill=CREAM)
        text(W, 180, 510, "DATA: AONO ET AL. (OSAKA PREF. UNIV.)", fill=INK2, align="c")
        text(W, 180, 530, "VIA OUR WORLD IN DATA, CHECKED VS", fill=INK2, align="c")
        text(W, 180, 550, "JAPAN METEOROLOGICAL AGENCY", fill=INK2, align="c")
        text(W, 180, 570, "DECADES = AVERAGE OF KNOWN YEARS", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "heian": sc_main("heian"), "medieval": sc_main("medieval"), "edo": sc_main("edo"),
           "modern": sc_main("modern"), "springs": sc_main("springs"), "outro": sc_outro}

def compose_light(c):
    art = np.array(c.art); big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tb = np.repeat(np.repeat(np.array(c.txt), 3, 0), 3, 1); al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(SCENEFN[name](t))
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.10) if ki >= 0 else 0.0
    z = 1.0 + 0.008 * kp * FXK
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    st = step_at(T)
    if st is not None and is_rec(st) and 0 <= T - st[0] < 0.12:
        fr = np.minimum(255, fr.astype(np.int16) + int(50 * FXK * (1 - (T - st[0]) / 0.12))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(NIGHT) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f) + np.array(NIGHT) * f).astype(np.uint8)
    return fr

# ================= audio =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.5) * SR)
    L = np.zeros(n); R = np.zeros(n); fxL = np.zeros(n); fxR = np.zeros(n)
    rng = np.random.default_rng(12)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fxL, i, x * send); add(fxR, i, x * send)
    def koto(m, dur=1.8):
        f = mtof(m); m_ = int(dur * SR); tt = np.arange(m_) / SR
        s = sum((1 / h) * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (3 + 2.5 * h)) for h in range(1, 7))
        return s * env(m_, 0.002, 1.2)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "drone":                                           # bamboo-flute drone on A + E, slow breath
            tt = np.arange(int(kw["d"] * SR)) / SR
            br = 0.75 + 0.25 * np.sin(2 * np.pi * tt / (8 * BEAT))
            x = (np.sin(2 * np.pi * mtof(57) * tt + 0.3 * np.sin(2 * np.pi * 5 * tt)) + 0.3 * np.sin(2 * np.pi * mtof(64) * tt)) * br
            x *= np.minimum(1, tt / 2.0) * np.clip((kw["d"] - tt) / 2.0, 0, 1)
            b, a = butter(2, 1500 / (SR / 2)); put(t, lfilter(b, a, x) * 0.035, send=0.2)
        elif k == "koto":
            x = koto(kw["m"]); pan = -0.3 + 0.6 * lev_of(kw["m"])
            put(t, x * v * 0.42, pan=pan, send=0.30)
            if kw.get("echo"): put(t + BEAT / 2, x * v * 0.18, pan=-pan)
        elif k == "koto2":
            put(t + 0.012, koto(kw["m"], 1.2) * v * 0.42, pan=0.35, send=0.25)
        elif k == "taiko":
            m_ = int(0.5 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 10) + 55) / SR) * np.exp(-tt * 7) * v * 0.75, send=0.12)
        elif k == "rim":
            m_ = int(0.04 * SR); b, a = butter(2, 3000 / (SR / 2))
            put(t, lfilter(b, a, rng.standard_normal(m_)) * np.exp(-np.arange(m_) / SR * 90) * v, pan=0.2)
        elif k == "shaker":
            m_ = int(0.05 * SR); b, a = butter(2, 6000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.004, 0.012) * v, pan=0.4)
        elif k == "rin":                                           # small temple bell on the records
            m_ = int(4.0 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt / 0.8)
                 + 0.25 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / 0.3)) * env(m_, 0.002, 1.6)
            put(t, x * v * 0.35, pan=0.1, send=0.4)
    def reverb(x):
        out = x.copy()
        for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
            k = int(d * SR); out[k:] += g * .6 * x[:-k]
        return out
    b, a = butter(1, 4000 / (SR / 2))
    L += lfilter(b, a, reverb(fxL)) * 0.6; R += lfilter(b, a, reverb(np.roll(fxR, 400))) * 0.6
    tt = np.arange(n) / SR
    fade = np.clip((TOTAL - tt) / 2.0, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.stack([L, R], 1) / mx * 0.89
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
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print("notes", sum(1 for s in STEPS if s[3] is not None), "silent", [s[2] for s in STEPS if s[3] is None])
        print("avg", round(AVG_ALL, 2), fdate(AVG_ALL), "old rec", fdate(OLD_REC), [y for y, v in YD.items() if v == OLD_REC])
        print([(s[2], None if s[3] is None else fdate(s[3]), round(s[0], 2)) for s in STEPS if s[2] in BANNERS or s[1] == "spr" or s[2] in (1870, 2010)])
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
