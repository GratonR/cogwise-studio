"""BEEPMELODY — YELLOWSTONE HAD ZERO WOLVES. THEN 14.
Wolves counted at year end, 1995 -> 2025 (31 counts). Every note = one year; pitch = wolves counted (log scale);
the soft plucks after each note = the packs (one pluck per pack). A drop >= 25 % = a low hit. Record (2003, 174) = accent.
Scene: Lamar Valley in winter, pixel art; every wolf counted = one pixel wolf, grouped in packs.
1995-1999 = Greater Yellowstone counts, 2000+ = inside the park (written on screen).
Music (co-pilot step 2, rework r1 = F "lo-fi wilderness"): 86 BPM swung, Rhodes Fmaj7-Em7-Dm7-Cmaj9, boom-bap drums,
round sub bass, vinyl crackle; glockenspiel = year, little Rhodes plucks = packs, tape-stop low hit = drop >= 25 %.
Data: yellowstone_wolves.csv (NPS Yellowstone Wolf Project annual reports + 2nd source per row).

    python3 yellowstone_wolves.py info out | preview out <scene>:<s> | at out <T>... | audio out/music.wav | render out | final out x.mp4
    PALETTE=day for the light variant (dusk = chosen at co-pilot step 3).
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

FXK = float(os.environ.get("PI_FX", "0.5"))
PAL = os.environ.get("PALETTE", "dusk")  # step 3 decision: dusk

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "yellowstone_wolves.csv"))))
for r in REC:
    r["w"] = int(r["wolves"]); r["y"] = int(r["year"]); r["p"] = int(r["packs"]) if r["packs"] else None
N = len(REC)
WMAX = max(r["w"] for r in REC)
I_REC = next(i for i, r in enumerate(REC) if r["w"] == WMAX)
CRASH = {i for i in range(1, N) if REC[i]["w"] <= 0.75 * REC[i - 1]["w"]}
I_PARK = next(i for i, r in enumerate(REC) if r["area"] == "YNP")
def packs_layout(i):  # pack count used to group the wolves on screen (1997 has no pack total: keep 1996's grouping)
    j = i
    while REC[j]["p"] is None: j -= 1
    return REC[j]["p"]

# ================= palette =================
if PAL == "dusk":
    SKYC = [(0, (38, 40, 78)), (60, (96, 72, 112)), (100, (196, 120, 110))]
    MT_FAR, MT_NEAR, SNOW, SNOW2, RIVER = (70, 66, 104), (52, 56, 86), (206, 212, 230), (172, 180, 208), (90, 110, 150)
    PINE, WOLF, WOLF2 = (30, 48, 52), (40, 38, 46), (88, 84, 96)
    INK, INK2, CREAM, ACC, GOLD, RED = (230, 232, 244), (170, 172, 196), (30, 32, 54), (130, 210, 150), (246, 196, 92), (240, 112, 96)
else:
    SKYC = [(0, (150, 196, 230)), (60, (196, 222, 238)), (100, (236, 240, 232))]
    MT_FAR, MT_NEAR, SNOW, SNOW2, RIVER = (150, 168, 196), (110, 128, 150), (246, 248, 250), (214, 224, 234), (120, 170, 200)
    PINE, WOLF, WOLF2 = (52, 96, 70), (70, 62, 58), (128, 118, 108)
    INK, INK2, CREAM, ACC, GOLD, RED = (30, 52, 40), (88, 110, 96), (250, 250, 244), (40, 140, 80), (220, 150, 40), (210, 72, 56)
WHITE = (255, 255, 255)

# ================= timeline (on the 8th-note grid) =================
BPM = 86.0
BEAT = 60.0 / BPM
INTRO_B = 6.0          # title, empty valley, 14 wolves released (note at 2.5 beats)
YEAR_B = 2.5           # one year = 2.5 beats
EXTRA_B = 2.0          # extra time after the record and after each crash (banner)
HOLD_B, OUTRO_B = 6.0, 9.0
T_RELEASE = 2.5 * BEAT
RT = [INTRO_B * BEAT]
for i in range(1, N):
    RT.append(RT[-1] + (YEAR_B + (EXTRA_B if (i - 1) == I_REC or (i - 1) in CRASH else 0)) * BEAT)
T_FINAL = RT[-1]
TOTAL = T_FINAL + (HOLD_B + OUTRO_B) * BEAT
def iy(y): return next(i for i, r in enumerate(REC) if r["y"] >= y)
SC = [("intro", RT[0]), ("rise", RT[iy(2003)] - RT[0]), ("crashes", RT[iy(2009)] - RT[iy(2003)]),
      ("steady", RT[iy(2020)] - RT[iy(2009)]), ("today", T_FINAL + HOLD_B * BEAT - RT[iy(2020)]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n_, d_ in SC: START[n_] = acc_; acc_ += d_
DUR = dict(SC); NAMES = [n for n, _ in SC]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan (F · lo-fi wilderness) =================
SCALE = [60, 62, 65, 67, 69, 72, 74, 77, 79, 81, 84, 86]     # F major pentatonic (C D F G A), ~2 octaves
LO, HI = math.log(20), math.log(180)
def pitch(w): return SCALE[int(round(np.clip((math.log(w) - LO) / (HI - LO), 0, 1) * (len(SCALE) - 1)))]
ROOTS = [41, 40, 38, 36]                                     # Fmaj7 - Em7 - Dm7 - Cmaj9
CHORDS = [(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (52, 55, 59, 62)]
PACK_NOTES = [65, 69, 72, 77, 81]
SWING = 0.12 * (60.0 / BPM)
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    ev(0.05, "wind", d=INTRO_B * BEAT + 1.0, v=0.10)
    ev(T_RELEASE, "glock", m=pitch(14), v=0.50)                          # 14 wolves released
    for k in range(3): ev(T_RELEASE + (k + 1) * BEAT / 4, "rpluck", m=PACK_NOTES[k], v=0.22)  # 3 release groups
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        ro = ROOTS[bar % 4]; ch = CHORDS[bar % 4]
        groove = RT[0] - 2 * BEAT <= t < T_FINAL + 4 * BEAT
        tail = t >= T_FINAL + 4 * BEAT
        if pos == 0 and (groove or tail): ev(t, "keys", ch=ch, d=4 * BEAT, v=1.0 if groove else 0.8)
        if groove:
            if pos == 0: ev(t, "bass", m=ro, d=3 * BEAT, v=0.30)
            if pos == 2: ev(t + BEAT / 2 + SWING, "bass", m=ro, d=BEAT, v=0.18)
            if t >= RT[0]:
                if pos == 0: ev(t, "kick", v=1.0)
                if pos == 1: ev(t + BEAT / 2 + SWING, "kick", v=0.7)
                if pos in (1, 3): ev(t, "snare", v=1.0)
                ev(t, "hat", v=1.0); ev(t + BEAT / 2 + SWING, "hat", v=0.7)
    for i, t in enumerate(RT):
        r = REC[i]
        ev(t, "glock", m=pitch(r["w"]), v=0.52 + (0.10 if i == I_REC else 0))
        np_ = r["p"] or 0
        step = min(BEAT / 4, (YEAR_B * BEAT * 0.8) / max(1, np_))
        for k in range(np_): ev(t + (k + 1) * step, "rpluck", m=PACK_NOTES[k % 5] + 12 * (k // 10), v=0.17)
        if i in CRASH: ev(t, "tapestop", v=0.45)
    for k, d in enumerate((0, 4, 7, 12)): ev(RT[I_REC] + k * 0.06, "glock", m=pitch(WMAX) - 12 + d, v=0.16)   # record = bell chord
    ev(RT[I_REC], "crash", v=0.20)
    ev(RT[I_REC], "howl", m=64, v=0.10)
    for k, d in enumerate([0, 4, 7, 12, 16]):                            # gentle rising bell arpeggio on the last count
        ev(T_FINAL + (k + 1) * BEAT / 4, "glock", m=60 + d, v=0.26)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= scene =================
def sky_col(y):
    for (y0, c0), (y1, c1) in zip(SKYC, SKYC[1:]):
        if y <= y1:
            f = max(0.0, min(1.0, (y - y0) / (y1 - y0))); return tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
    return SKYC[-1][1]

def ridge(x, base, amps):
    return base - sum(a * math.sin(x / p + ph) for a, p, ph in amps)

Y_FLOOR = 150
def _background():
    img = Image.new("RGB", (AW, AH)); d = ImageDraw.Draw(img)
    for y in range(AH): d.line([0, y, AW, y], fill=sky_col(y))
    for x in range(AW):                                                 # far peaks with snow caps
        h = ridge(x, 112, [(14, 23, 0.4), (7, 9, 1.3), (3, 4.1, 2)])
        d.line([x, h, x, Y_FLOOR], fill=MT_FAR)
        d.line([x, h, x, h + 4 + 2 * math.sin(x / 5)], fill=SNOW2)
    for x in range(AW):                                                 # near hills
        h = ridge(x, 136, [(8, 31, 2.1), (4, 11, 0.2), (1.5, 3.7, 1)])
        d.line([x, h, x, Y_FLOOR + 4], fill=MT_NEAR)
    rng = random.Random(4)
    for _ in range(46):                                                 # pines on the hills
        x = rng.uniform(0, AW); h0 = ridge(x, 136, [(8, 31, 2.1), (4, 11, 0.2), (1.5, 3.7, 1)]) + rng.uniform(2, 12)
        s = rng.choice([3, 4, 5])
        d.polygon([(x, h0 - s * 2), (x - s, h0 + 1), (x + s, h0 + 1)], fill=PINE)
        d.point((int(x), int(h0 - s * 2 + 1)), fill=SNOW)
    d.rectangle([0, Y_FLOOR, AW, AH], fill=SNOW)                        # valley floor (snow)
    rs = random.Random(9)
    for _ in range(260):                                                # wind-blown snow texture
        x = rs.uniform(0, AW); y = rs.uniform(Y_FLOOR + 2, AH); w = rs.choice([2, 3, 5])
        d.line([x, y, x + w, y], fill=SNOW2)
    pts = [(80 + 34 * math.sin(y / 23.0) + 10 * math.sin(y / 7.0), y) for y in range(Y_FLOOR, 300)]  # Lamar River
    for (x, y) in pts: d.line([x - 2, y, x + 2 + (y - Y_FLOOR) // 40, y], fill=RIVER)
    return img
_BG = None
def background():
    global _BG
    if _BG is None: _BG = _background()
    return _BG.copy()

# pack homes on the valley floor (16 max), wolf slots around each home
HOMES = [(34, 174), (90, 168), (146, 178), (58, 204), (120, 206), (28, 236), (88, 238), (152, 236), (52, 268),
         (118, 270), (26, 298), (84, 300), (148, 300), (160, 206), (60, 172), (122, 186)]
def slots(npk, nw):
    """positions of nw wolves split into npk packs (sizes as even as possible, deterministic)"""
    sizes = [nw // npk + (1 if k < nw % npk else 0) for k in range(npk)]
    pos = []
    for k, s in enumerate(sizes):
        hx, hy = HOMES[k]
        for j in range(s):
            a = j * 2.4; rad = 2.9 * math.sqrt(j + 0.5)
            pos.append((hx + rad * 2.2 * math.cos(a), hy + rad * 1.3 * math.sin(a), k))
    return pos

def wolf(d, x, y, col, facing=1, step=0):
    x = int(round(x)); y = int(round(y)); f = facing
    d.rectangle([x - 2, y - 1, x + 2, y], fill=col)                     # body
    d.rectangle([x + 2 * f, y - 3, x + 3 * f, y - 1] if f > 0 else [x + 3 * f, y - 3, x + 2 * f, y - 1], fill=col)  # head
    d.point((x + 4 * f, y - 2), fill=col)                               # snout
    d.point((x + 2 * f, y - 4), fill=col)                               # ear
    d.point((x - 3 * f, y - 2), fill=col)                               # tail
    d.point((x - 2 + step, y + 1), fill=col); d.point((x + 1 - step, y + 1), fill=col)  # legs

def layout_at(i):
    return slots(packs_layout(i), REC[i]["w"]) if i >= 0 else []

MOVE = 0.9 * BEAT
def draw_scene(c, T):
    c.art = background(); c.a = ImageDraw.Draw(c.art); d = c.a
    k = rec_index(T)
    if k < 0:                                                           # intro: the 14 released wolves walk in
        if T >= T_RELEASE:
            a = ease((T - T_RELEASE) / (1.2 * BEAT))
            for j, (x, y, _) in enumerate(slots(3, 14)):
                x0 = -10 - j * 3
                wolf(d, lerp(x0, x, a), y, WOLF, 1, int(T * 8 + j) % 2 if a < 1 else 0)
        return
    cur = layout_at(k); prev = layout_at(k - 1) if k > 0 else slots(3, 14)
    a = ease((T - RT[k]) / MOVE)
    n_cur, n_prev = len(cur), len(prev)
    for j in range(max(n_cur, n_prev)):
        if j < n_cur and j < n_prev:
            x = lerp(prev[j][0], cur[j][0], a); y = lerp(prev[j][1], cur[j][1], a)
            wolf(d, x, y, WOLF, 1 if (j % 3) else -1, int(T * 8 + j) % 2 if a < 1 else 0)
        elif j < n_cur:                                                 # new wolf (born / arrived): pops in with a flash
            x, y, _ = cur[j]
            if a > 0.05:
                wolf(d, x, y, WOLF if a > 0.6 else ACC, 1 if (j % 3) else -1)
        else:                                                           # wolf lost this year: fades out as a grey ghost
            x, y, _ = prev[j]
            if a < 0.95: wolf(d, x, y - 3 * a, WOLF2 if a < 0.5 else SNOW2, 1 if (j % 3) else -1)
    if k == I_REC and T - RT[k] < 1.2:                                 # record: ring around the valley
        rr = 10 + (T - RT[k]) * 120
        d.ellipse([90 - rr, 225 - rr * 0.6, 90 + rr, 225 + rr * 0.6], outline=GOLD)
    if k in CRASH and T - RT[k] < 0.8:
        al = 1 - (T - RT[k]) / 0.8
        c.art = Image.blend(c.art, Image.new("RGB", (AW, AH), RED), 0.22 * al); c.a = ImageDraw.Draw(c.art)

# ================= text layer =================
def area_tag(r): return "GREATER YELLOWSTONE" if r["area"] == "GYA" else "INSIDE THE PARK"
def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    r = REC[k]; age = T - RT[k]
    text(W, 28, 22, "WOLVES COUNTED, DEC 31", fill=INK2)
    col = RED if (k in CRASH and age < 0.6) else GOLD if (k == I_REC and age < 1.0) else ACC if age < 0.22 else INK
    text(W, 28, 44, f"{r['w']}", size=40, fill=col)
    text(W, 28 + 16 * len(str(r["w"])) + 10, 60, "WOLVES", fill=INK2)
    text(W, 334, 44, str(r["y"]), size=40, fill=GOLD, align="r")
    pk = f"{r['p']} PACKS" if r["p"] else "PACKS: N/A"
    if r["y"] == 2025: pk = "7 PACKS + 1 GROUP"
    text(W, 28, 92, pk, fill=INK2)
    text(W, 334, 92, area_tag(r), fill=INK2, align="r")

def graph(c, T):
    """small curve at the bottom: the count so far (0-200 wolves, linear)"""
    W = c.t; k = rec_index(T)
    W.rectangle([0, 560, 360, 640], fill=CREAM); W.rectangle([0, 560, 360, 561], fill=INK2)
    x0, x1, yb, yt = 40, 344, 628, 572
    def gx(i): return x0 + (x1 - x0) * i / (N - 1)
    def gy(w): return yb - (yb - yt) * w / 200
    for w in (100, 200):
        for x in range(x0, x1, 4): W.point((x, int(gy(w))), fill=INK2)
        text(W, x0 - 4, int(gy(w)) - 10, str(w), fill=INK2, align="r")
    text(W, x0 - 4, yb - 10, "0", fill=INK2, align="r")
    W.line([x0, yb, x1, yb], fill=INK2)
    text(W, x0, yb - 4 + 2, "", fill=INK2)
    pts = [(gx(i), gy(REC[i]["w"])) for i in range(k + 1)]
    if len(pts) > 1: W.line(pts, fill=ACC, width=2)
    if pts:
        x, y = pts[-1]; W.rectangle([x - 2, y - 2, x + 2, y + 2], fill=GOLD if k == I_REC else INK)
    if k >= 0:
        xp = gx(I_PARK)
        for y in range(yt, yb, 3): W.point((int(xp), y), fill=INK2)

BANNERS = {I_PARK: ("FROM 2000: INSIDE THE PARK ONLY", "", False),
           I_REC: ("RECORD: 174 WOLVES", "THE MOST EVER COUNTED IN THE PARK", True),
           iy(2005): ("171 -> 118", "PUP DEATHS, DISEASE SUSPECTED", True),
           iy(2008): ("171 -> 124", "-27 % IN ONE YEAR", True),
           N - 1: ("2025: 84 WOLVES", "DOWN FROM 108 IN 2024", True)}
def banner(c, T):
    k = rec_index(T)
    if k not in BANNERS: return
    a = T - RT[k]
    hold = (HOLD_B * BEAT) if k == N - 1 else (YEAR_B + (EXTRA_B if (k == I_REC or k in CRASH) else 0)) * BEAT - 0.1
    if not (0.08 < a < hold): return
    tt, sub, big = BANNERS[k]; W = c.t; yb = 196
    w = max((16 if big else 8) * len(tt), 8 * len(sub)) + 30
    hgt = 62 if big else (42 if sub else 26)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=RED if k in CRASH else GOLD)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=RED if k in CRASH else INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 40, sub, fill=INK2, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 21, sub, fill=INK2, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, T); graph(c, T); return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 24, "YELLOWSTONE HAD", size=40, fill=INK)
    text(W, 28, 62, "ZERO WOLVES.", size=40, fill=RED)
    if T >= T_RELEASE: text(W, 28, 100, "THEN 14.", size=40, fill=ACC)
    if t > 0.5: text(W, 28, 146, "1926: THE LAST PARK WOLVES WERE KILLED", fill=INK2)
    if T >= T_RELEASE + 0.3:
        W.rectangle([50, 196, 310, 238], fill=CREAM); W.rectangle([50, 196, 310, 198], fill=ACC)
        text(W, 180, 199, "1995: 14 WOLVES RELEASED", fill=INK, align="c")
        text(W, 180, 218, "BROUGHT FROM CANADA", fill=INK2, align="c")
    if t > 1.2:
        W.rectangle([30, 512, 330, 552], fill=CREAM)
        text(W, 180, 515, "EVERY NOTE = ONE YEAR", fill=INK, align="c")
        text(W, 180, 532, "EVERY PIXEL WOLF = ONE WOLF COUNTED", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T); W = c.t
    W.rectangle([16, 30, 344, 300], fill=CREAM); W.rectangle([16, 30, 344, 32], fill=ACC)
    text(W, 180, 40, "31 WINTERS IN ONE SONG", fill=INK2, align="c")
    rows = [("1995", "21", "FIRST COUNT"), ("2003", "174", "THE PEAK"), ("2025", "84", "TODAY")]
    for j, (y, v, s) in enumerate(rows):
        if t > 0.4 + j * 0.7:
            yy = 70 + j * 60
            text(W, 34, yy + 6, y, fill=GOLD); text(W, 210, yy - 4, v, size=40, fill=INK, align="r")
            text(W, 222, yy + 6, s, fill=INK2)
    if t > 2.8: text(W, 180, 262, "WHICH NOTE HIT YOU HARDEST?", fill=ACC, align="c")
    if t > 3.4:
        W.rectangle([16, 470, 344, 540], fill=CREAM)
        text(W, 180, 474, "DATA: NPS YELLOWSTONE WOLF PROJECT,", fill=INK2, align="c")
        text(W, 180, 494, "USFWS, INTERNATIONAL WOLF CENTER", fill=INK2, align="c")
        text(W, 180, 514, "1995-99 GREATER YELLOWSTONE, 2000+ PARK", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "rise": sc_main("rise"), "crashes": sc_main("crashes"), "steady": sc_main("steady"),
           "today": sc_main("today"), "outro": sc_outro}

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
    c = SCENEFN[name](t)
    fr = compose_light(c)
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.08) if ki >= 0 else 0.0
    z = 1.0 + 0.008 * kp * FXK
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if k >= 0 and 0 <= T - RT[k] < 0.10:
        fr = np.minimum(255, fr.astype(np.int16) + int(45 * FXK * (1 - (T - RT[k]) / 0.10))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.5) * SR)
    L = np.zeros(n); R = np.zeros(n); fx = np.zeros(n)
    rng = np.random.default_rng(11)
    def lp(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def hp(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def bp(x, lo, hi):
        b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
    def put(t, x, g=1.0, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(x)); y = x[:j - i] * g
        L[i:j] += y * math.sqrt((1 - pan) / 2) * 1.41; R[i:j] += y * math.sqrt((1 + pan) / 2) * 1.41
        if send: fx[i:j] += y * send
    def rhodes(f, dur=1.8, v=1.0):
        m = int(dur * SR); t = np.arange(m) / SR
        I = (1.2 + 1.5 * v) * np.exp(-t / 0.25)
        x = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * t)) + 0.25 * np.sin(2 * np.pi * f * 7.1 * t) * np.exp(-t / 0.05)
        x *= 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
        return x * np.exp(-t / 1.1) * np.minimum(1, t / 0.003) * np.clip((dur - t) / 0.2, 0, 1)
    def glock(f, dur=1.6):
        m = int(dur * SR); t = np.arange(m) / SR
        x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25) + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.08)
        return x * np.exp(-t / 0.7) * np.minimum(1, t / 0.001)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "keys":
            for j, m in enumerate(kw["ch"]):
                put(t + j * 0.012, rhodes(mtof(m), kw["d"] + 0.3, 0.5), 0.07 * v, pan=-0.3 + 0.2 * j, send=0.25)
        elif k == "bass":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            x = np.tanh(1.3 * np.sin(2 * np.pi * mtof(kw["m"] - 12) * tt)) * np.exp(-tt / 1.2) * np.minimum(1, tt / 0.01) * np.clip((kw["d"] - tt) / 0.08, 0, 1)
            put(t, x, v)
        elif k == "kick":
            m_ = int(0.4 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(46 + 90 * np.exp(-tt / 0.035)) / SR
            put(t, np.tanh(1.6 * np.sin(ph) * np.exp(-tt / 0.13)) * v, 0.42)
        elif k == "snare":
            m_ = int(0.25 * SR); tt = np.arange(m_) / SR
            x = bp(rng.standard_normal(m_), 1200, 7000) * np.exp(-tt / 0.06) + 0.6 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / 0.04)
            put(t, x * v, 0.18, send=0.15)
        elif k == "hat":
            m_ = int(0.05 * SR); tt = np.arange(m_) / SR
            put(t, hp(rng.standard_normal(m_), 7000) * np.exp(-tt / 0.012) * v, 0.06, pan=0.35)
        elif k == "glock":
            put(t, glock(mtof(kw["m"]), 1.8), v * 0.6, pan=0.2, send=0.4)
        elif k == "rpluck":
            put(t, rhodes(mtof(kw["m"]), 0.4, 0.3), v * 0.2, pan=-0.5 * (1 if (kw["m"] // 2) % 2 else -1), send=0.3)
        elif k == "tapestop":
            m_ = int(0.9 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * np.cumsum(mtof(41) * np.exp(-tt / 0.5)) / SR) * np.exp(-tt / 0.4), v)
        elif k == "crash":
            m_ = int(2.2 * SR)
            put(t, hp(rng.standard_normal(m_), 5000) * env(m_, 0.002, 0.6) * v * 0.5, send=0.2)
        elif k == "howl":
            dur = 1.6; m_ = int(dur * SR); tt = np.arange(m_) / SR; f0 = mtof(kw["m"])
            glide = f0 * (1 + .5 * np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 1.5) * (1 + .012 * np.sin(2 * np.pi * 5.5 * tt))
            ph = 2 * np.pi * np.cumsum(glide) / SR
            x = (np.sin(ph) + .25 * np.sin(2 * ph)) * np.minimum(1, tt / .25) * np.clip((dur - tt) / .5, 0, 1)
            put(t + 0.1, x * v, pan=-0.3, send=0.5)
        elif k == "wind":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            x = lp(rng.standard_normal(m_), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * tt)) * np.clip((kw["d"] - tt) / 1.0, 0, 1) * np.minimum(1, tt / 0.3)
            put(t, x * v * 2.0)
    vin = hp(rng.standard_normal(n), 1500) * 0.003                      # vinyl crackle bed
    clicks = (rng.random(n) > 0.9996) * rng.standard_normal(n) * 0.08
    L += vin + lp(clicks, 6000); R += vin + lp(np.roll(clicks, 50), 6000)
    def verb(x, off):
        o = np.zeros_like(x)
        for d, g in [(.071, .55), (.113, .47), (.167, .40), (.239, .33), (.311, .27), (.419, .2), (.557, .14), (.743, .09), (.97, .05)]:
            m = int((d + off) * SR); o[m:] += g * x[:-m]
        return lp(o, 4200)
    L += 0.35 * verb(fx, 0.0); R += 0.35 * verb(fx, 0.011)
    tt = np.arange(n) / SR
    fade = np.clip((TOTAL - tt) / 2.0, 0, 1) * np.minimum(1, tt / 0.02)
    st = np.stack([L * fade, R * fade], 1)
    st = np.tanh(st / np.abs(st).max() * 1.15); st = st / np.abs(st).max() * 0.89
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
        print("crash:", [REC[i]["y"] for i in sorted(CRASH)], "record:", REC[I_REC]["y"], "park from:", REC[I_PARK]["y"])
        print([(REC[i]["y"], round(t, 2)) for i, t in enumerate(RT)])
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
