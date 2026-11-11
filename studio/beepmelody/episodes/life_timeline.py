"""BEEPMELODY — LIFE ON EARTH ALMOST ENDED 5 TIMES. LISTEN TO IT COME BACK.
31 events, 4,540 million years ago -> today: each new kind of life = one marimba note, each of the 'Big Five' mass
extinctions = one broken note + the groove cuts out, then comes back. A 24 h clock shows where each event falls if
Earth's history were one day; below, the full 4.54-billion-year line and a zoom on the last 540 million years.
Mood (co-pilot step 2, Guillaume: 'Mix A C'): warm A (marimba, shaker, soft kick, round bass Am–F–C–G) for the
3 billion years of microbes, then C's groove (kick/snare, octave bass, kalimba shimmer) from the Cambrian on. 104 BPM.
Pitch = a 'life level': +1 per new group of life, -1 per 20 % of species lost (same rule as the step-2 excerpts).
Data: life_timeline.csv (2 sources per row; ICS 2024, Barnosky et al. 2011 via OWID for the extinctions).

    python3 life_timeline.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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
DARK = os.environ.get("LIFE_DARK", "0") == "1"

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "life_timeline.csv"))))
AGE0 = 4540.0
lvl = 0; nx = 0
for r in REC:
    r["m"] = float(r["mya"]); r["p"] = int(r["pct"]) if r["pct"] else 0
    r["ext"] = r["kind"] == "extinction"
    if r["ext"]: nx += 1; lvl -= int(round(r["p"] / 20))
    elif r["kind"] == "life": lvl += 1
    r["lvl"] = lvl; r["nx"] = nx
    r["clock"] = (AGE0 - r["m"]) / AGE0 * 86400.0                  # seconds into the 24 h day
N = len(REC)
EXT_NAME = {1: "END ORDOVICIAN", 2: "LATE DEVONIAN", 3: "END PERMIAN", 4: "END TRIASSIC", 5: "END CRETACEOUS"}
def clk(s, dec=None):
    s = min(s, 86400.0)
    if dec is None: dec = s > 86340
    s = round(s, 1) if dec else float(round(s))
    h, rem = divmod(s, 3600); m, sec = divmod(rem, 60)
    if s >= 86400: return "24:00:00"
    return f"{int(h):02d}:{int(m):02d}:{sec:04.1f}" if dec else f"{int(h):02d}:{int(m):02d}:{int(sec):02d}"

# ================= palette: light 'bio green' =================
if not DARK:
    BG0, BG1 = (222, 240, 226), (246, 250, 238)
    INK = (28, 52, 40); INK2 = (96, 122, 104); CREAM = (250, 251, 244); WHITE = (255, 255, 255)
    GOLD = (214, 140, 24); GREEN = (34, 150, 84); GREEN2 = (150, 206, 160); RED = (206, 52, 52); RED2 = (240, 170, 160)
    DIAL = (252, 253, 248); RIM = (60, 84, 70); CHARTBG = (250, 252, 248); GRID = (214, 230, 216); NIGHT = (200, 222, 230)
else:
    BG0, BG1 = (10, 24, 20), (16, 34, 28)
    INK = (226, 246, 230); INK2 = (130, 170, 146); CREAM = (14, 30, 24); WHITE = (255, 255, 255)
    GOLD = (255, 196, 70); GREEN = (90, 230, 140); GREEN2 = (40, 110, 70); RED = (255, 90, 90); RED2 = (120, 40, 40)
    DIAL = (8, 20, 16); RIM = (120, 150, 132); CHARTBG = (12, 26, 20); GRID = (30, 54, 42); NIGHT = (20, 40, 50)

# ================= timeline (on the beat) =================
BPM = 104.0
BEAT = 60.0 / BPM
INTRO_B = 8
STEP_B = 2                                     # one event = 2 beats
DEEP_B = 4                                     # before the Cambrian, 4 beats: 3 billion years of microbes sound sparse
EXT_B = 4                                      # an extinction holds 4: the groove cuts out for 2, then slams back
HOLD_B = 10
OUTRO_B = 14
RT = []; t_ = INTRO_B * BEAT
for i, r in enumerate(REC):
    RT.append(t_); t_ += (EXT_B if r["ext"] else DEEP_B if r["m"] > 538.8 else STEP_B) * BEAT
T_FINAL = RT[-1]
T_REC_END = T_FINAL + HOLD_B * BEAT
I_CAMB = next(i for i, r in enumerate(REC) if r["m"] == 538.8)
I_PERM = next(i for i, r in enumerate(REC) if r["m"] == 251.9)
I_K = next(i for i, r in enumerate(REC) if r["m"] == 66)
SC = [("intro", RT[0]), ("deep", RT[I_CAMB] - RT[0]), ("boom", RT[I_PERM + 1] - RT[I_CAMB]),
      ("dinos", RT[I_K + 1] - RT[I_PERM + 1]), ("us", T_REC_END - RT[I_K + 1]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
TOTAL = acc_

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k
def cut_window(T):                                # inside an extinction's 2-beat silence?
    k = rec_index(T)
    return k >= 0 and REC[k]["ext"] and T - RT[k] < 2 * BEAT

# ================= music plan =================
SCALE = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88]   # A minor pentatonic (step-2 A)
LVS = [r["lvl"] for r in REC]; LO, HI = min(LVS), max(LVS)
def pitch(i): return SCALE[int(round((REC[i]["lvl"] - LO) / max(1, HI - LO) * (len(SCALE) - 1)))]
def pre_pitch(i): return pitch(i - 1) if i > 0 else pitch(i)
ROOTS = [45, 41, 36, 43]                                           # Am–F–C–G
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT)) + 1
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4); ro = ROOTS[bar % 4]
        if t >= T_REC_END:                                         # outro: bass + soft marimba chord
            if t < TOTAL - 2 * BEAT and pos == 0:
                ev(t, "bass", m=ro, d=BEAT * 3.6, v=0.18)
                for j, d in enumerate((12, 19, 24)): ev(t + j * BEAT * 0.5, "mar", m=ro + 12 + d, v=0.12)
            continue
        if cut_window(t + 0.001): continue
        groove = t >= RT[I_CAMB]
        if not groove:                                             # A: warm, sparse (intro + 3 billion years of microbes)
            if pos in (0, 2): ev(t, "kick", v=0.42)
            ev(t + BEAT / 2, "shaker", v=0.05)
            if b >= 4 and pos % 2: ev(t, "shaker", v=0.035)
            if pos == 0: ev(t, "bass", m=ro, d=BEAT * 3.8, v=0.20, bt="round")
        else:                                                      # C: the groove
            ev(t, "kick", v=0.6)
            if pos in (1, 3): ev(t, "snare", v=0.28)
            ev(t + BEAT / 2, "shaker", v=0.045)
            for h in (0, 0.5): ev(t + h * BEAT, "bass", m=ro + (12 if h else 0), d=BEAT * 0.42, v=0.22, bt="oct")
    for i, t in enumerate(RT):
        r = REC[i]
        if r["ext"]:
            ev(t, "thud", v=0.75); ev(t, "broken", m=pre_pitch(i), drop=int(round(r["p"] / 20)) * 3 + 3, v=0.30)
            ev(t, "crunch", v=0.16)
            ev(t + 2 * BEAT, "crash", v=0.22); ev(t + 2 * BEAT, "kick", v=0.7)   # ...and back
            continue
        groove = t >= RT[I_CAMB]
        ev(t, "mar", m=pitch(i), v=0.46)
        if groove: ev(t, "kal", m=pitch(i) + 12, v=0.16)
        if i == I_CAMB: ev(t, "crash", v=0.2)
    for k, d in enumerate([0, 7, 12, 15, 19, 24]):                # rising arpeggio on 'today'
        ev(T_FINAL + (k + 1) * BEAT / 2, "mar", m=pitch(N - 1) - 12 + d, v=0.32)
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

DX, DY, DR = 90, 134, 40                                           # 24 h dial (art px)
def ang(sec): return -math.pi / 2 + 2 * math.pi * sec / 86400.0     # 00:00 at the top, clockwise
def hand_sec(T):
    k = rec_index(T)
    if k < 0: return 0.0
    a = ease((T - RT[k]) / 0.35)
    prev = REC[k - 1]["clock"] if k > 0 else 0.0
    return lerp(prev, REC[k]["clock"], a)
def dial(c, T):
    d = c.a; k = rec_index(T)
    d.ellipse([DX - DR - 5, DY - DR - 5, DX + DR + 5, DY + DR + 5], fill=RIM)
    d.ellipse([DX - DR, DY - DR, DX + DR, DY + DR], fill=DIAL)
    s = hand_sec(T)
    if s > 1:                                                      # elapsed day: filled pie
        d.pieslice([DX - DR + 2, DY - DR + 2, DX + DR - 2, DY + DR - 2], -90, -90 + 360 * s / 86400, fill=GREEN2)
    for h in range(24):
        a = ang(h * 3600); r0 = DR - (5 if h % 6 == 0 else 2)
        d.line([DX + r0 * math.cos(a), DY + r0 * math.sin(a), DX + DR * math.cos(a), DY + DR * math.sin(a)], fill=INK2 if h % 6 else INK)
    for i in range(k + 1):                                         # events as dots on the rim
        r = REC[i]; a = ang(r["clock"]); rr = DR + 2
        x, y = DX + rr * math.cos(a), DY + rr * math.sin(a)
        col = RED if r["ext"] else GOLD
        sz = 2 if r["ext"] else 1
        d.rectangle([x - sz, y - sz, x + sz, y + sz], fill=col)
    a = ang(s)
    d.line([DX, DY, DX + (DR - 4) * math.cos(a), DY + (DR - 4) * math.sin(a)], fill=INK, width=2)
    d.ellipse([DX - 3, DY - 3, DX + 3, DY + 3], fill=INK)
    if k >= 0 and REC[k]["ext"]:                                   # extinction: the dial flashes red, then recovers
        age = T - RT[k]
        if age < 2 * BEAT:
            q = 1 - age / (2 * BEAT)
            if q > 0.05:
                d.ellipse([DX - DR - 5, DY - DR - 5, DX + DR + 5, DY + DR + 5], outline=RED, width=1 + int(3 * q))
    W = c.t
    for h, lab in ((0, "00:00"), (6, "06:00"), (12, "12:00"), (18, "18:00")):
        a = ang(h * 3600); rr = DR + (21 if h % 12 else 11)
        x, y = DX + rr * math.cos(a), DY + rr * math.sin(a)
        text(W, int(x * 2), int(y * 2) - 9, lab, fill=INK2, align="c")

# bottom: the full 4.54 billion years, and a zoom on the last 540 million
BX0, BX1 = 18, 172
Y1, Y2 = 228, 272
def xa(m): return BX0 + (AGE0 - m) / AGE0 * (BX1 - BX0)
def xz(m): return BX0 + (540 - m) / 540 * (BX1 - BX0)
def chart(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    d.rectangle([BX0 - 6, Y1 - 16, BX1 + 6, Y2 + 26], fill=CHARTBG, outline=GRID)
    # full line
    d.rectangle([BX0, Y1, BX1, Y1 + 3], fill=GRID)
    s = hand_sec(T); xnow = BX0 + s / 86400 * (BX1 - BX0)
    d.rectangle([BX0, Y1, int(xnow), Y1 + 3], fill=GREEN2)
    d.rectangle([int(xa(540)), Y1 - 1, BX1, Y1 + 4], outline=GOLD)
    for i in range(k + 1):
        r = REC[i]; x = int(xa(r["m"]))
        d.line([x, Y1 - (5 if r["ext"] else 3), x, Y1 - 1], fill=RED if r["ext"] else GOLD)
    text(W, BX0 * 2, (Y1 - 15) * 2, "ALL 4.54 BILLION YEARS", fill=INK2)
    for m, lab in ((4540, "4.5 BN"), (3000, "3 BN"), (1500, "1.5 BN"), (0, "NOW")):
        text(W, int(xa(m) * 2), (Y1 + 6) * 2, lab, fill=INK2, align="l" if m == 4540 else ("r" if m == 0 else "c"))
    # zoom: last 540 Myr
    d.rectangle([BX0, Y2, BX1, Y2 + 3], fill=GRID)
    if s >= (AGE0 - 540) / AGE0 * 86400:
        mnow = AGE0 - s / 86400 * AGE0
        d.rectangle([BX0, Y2, int(xz(max(0, mnow))), Y2 + 3], fill=GREEN2)
    for i in range(k + 1):
        r = REC[i]
        if r["m"] > 540: continue
        x = int(xz(r["m"]))
        if r["ext"]:
            d.rectangle([x - 1, Y2 - 8, x, Y2 + 3], fill=RED)
            text(W, x * 2, (Y2 - (18 if r["nx"] % 2 else 28)) * 2, f"{r['p']}%", fill=RED, align="c")
        else:
            d.line([x, Y2 - 4, x, Y2 - 1], fill=GOLD)
    for m, lab in ((540, "540 M"), (250, "250 M"), (0, "NOW")):
        text(W, int(xz(m) * 2), (Y2 + 6) * 2, lab, fill=INK2, align="l" if m == 540 else ("r" if m == 0 else "c"))
    text(W, BX1 * 2, (Y2 + 14) * 2, "ZOOM: LAST 540 MILLION YEARS", fill=GOLD, align="r")

def hud(c, T):
    W = c.t; k = rec_index(T); r = REC[k]; age = T - RT[k]
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    text(W, 28, 22, "IF EARTH'S HISTORY WERE ONE DAY", fill=GREEN)
    hot = age < 0.25
    text(W, 28, 44, clk(r["clock"]), size=40, fill=(RED if r["ext"] else GREEN) if hot else INK)
    text(W, 28, 92, r["shown"], fill=INK2)
    surv = r["nx"]
    text(W, 334, 92, f"EXTINCTIONS {surv}/5", fill=RED if surv else INK2, align="r")
    W.rectangle([16, 128, 344, 152], fill=CREAM); W.rectangle([16, 128, 19, 152], fill=RED if r["ext"] else GREEN)
    lab = (f"MASS EXTINCTION · {EXT_NAME[r['nx']]}" if r["ext"] else r["label"]).upper()
    text(W, 28, 131, lab, fill=RED if r["ext"] else INK)

def footer(c, T, k=None):
    W = c.t
    W.rectangle([0, 600, 360, 640], fill=CREAM); W.rectangle([0, 600, 360, 601], fill=INK2)
    text(W, 10, 604, "EVERY BEEP", fill=INK2); text(W, 10, 620, "= NEW LIFE", fill=GREEN)
    text(W, 350, 604, "BROKEN NOTE", fill=INK2, align="r"); text(W, 350, 620, "= MASS EXTINCTION", fill=RED, align="r")

BANNERS = {I_CAMB: ("CAMBRIAN EXPLOSION", "ANIMALS SHOW UP AT 9 PM", False),
           next(i for i, r in enumerate(REC) if r["m"] == 0.3): ("HOMO SAPIENS", "6 SECONDS BEFORE MIDNIGHT", True),
           N - 1: ("~8.7 MILLION", "SPECIES TODAY (EST.)", True)}
def banner(c, T):
    k = rec_index(T)
    if k < 0: return
    W = c.t; a = T - RT[k]; r = REC[k]; xc = 180; yb = 356
    if r["ext"]:
        if a < 0.06: return
        if a < 2 * BEAT:
            tt, sub = f"{r['p']}% OF SPECIES GONE", f"EXTINCTION {r['nx']} OF 5 · {EXT_NAME[r['nx']]}"
            w = max(16 * len(tt) + 24, 8 * len(sub) + 30)
            W.rectangle([xc - w / 2, yb, xc + w / 2, yb + 62], fill=CREAM)
            W.rectangle([xc - w / 2, yb, xc + w / 2, yb + 2], fill=RED); W.rectangle([xc - w / 2, yb + 61, xc + w / 2, yb + 62], fill=INK2)
            text(W, xc, yb + 4, tt, size=40, fill=RED, align="c")
            if a > 0.2: text(W, xc, yb + 40, sub, fill=INK2, align="c")
        elif a < 4 * BEAT - 0.05:
            tt = "...AND LIFE CAME BACK"; w = 9 * len(tt) + 30
            W.rectangle([xc - w / 2, yb, xc + w / 2, yb + 26], fill=CREAM); W.rectangle([xc - w / 2, yb, xc + w / 2, yb + 2], fill=GREEN)
            text(W, xc, yb + 3, tt, fill=GREEN, align="c")
        return
    if k not in BANNERS: return
    hold = HOLD_B * BEAT if k == N - 1 else STEP_B * BEAT * 0.95
    if not (0.06 < a < hold): return
    tt, sub, big = BANNERS[k]
    w = max((16 if big else 9) * len(tt) + 30, 8 * len(sub) + 30); hgt = 62 if big else 42
    x0, x1 = xc - w / 2, xc + w / 2
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
    dial(c, T); chart(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 160], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 159, 344, 160], fill=INK)
    text(W, 28, 22, "LIFE ON EARTH", size=40, fill=INK)
    if t > 0.25: text(W, 28, 58, "ALMOST ENDED 5 TIMES", size=40, fill=RED)
    if t > 0.8: text(W, 28, 104, "EVERY BEEP = A NEW KIND OF LIFE", fill=GREEN)
    if t > 1.3: text(W, 28, 126, "BROKEN NOTE = MASS EXTINCTION", fill=RED)
    if t > 2.0:
        W.rectangle([50, 356, 310, 398], fill=CREAM); W.rectangle([50, 356, 310, 358], fill=GOLD)
        text(W, 180, 359, "4.54 BILLION YEARS = ONE DAY", fill=INK, align="c")
        text(W, 180, 377, "LISTEN TO IT COME BACK", fill=INK2, align="c")
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
    c = frame_ctx(T_REC_END); W = c.t
    W.rectangle([0, 0, 360, 600], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "4.54 BILLION YEARS · ONE DAY", fill=INK2, align="c")
    rows = [("5", "TIMES LIFE ALMOST ENDED", RED), ("96%", "OF SPECIES GONE AT WORST", RED),
            ("21:09", "ANIMALS SHOW UP", GOLD), ("23:59:54", "HUMANS SHOW UP", GREEN)]
    for j, (a, b, col) in enumerate(rows):
        if t > 0.3 + j * 0.45:
            text(W, 40, 84 + j * 50, a, size=40, fill=col); text(W, 320, 98 + j * 50, b, fill=INK, align="r")
    if t > 2.4: text(W, 180, 316, "LIFE CAME BACK EVERY TIME", fill=GREEN, align="c")
    if t > 3.0:
        W.rectangle([40, 452, 320, 453], fill=INK2)
        text(W, 180, 464, "AGES ARE ESTIMATES (~)", fill=INK2, align="c")
        text(W, 180, 482, "DATA: ICS CHART 2024,", fill=INK2, align="c")
        text(W, 180, 500, "BARNOSKY ET AL. 2011 (NATURE) VIA OWID,", fill=INK2, align="c")
        text(W, 180, 518, "SMITHSONIAN, NHM, USGS + PAPERS", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "deep": sc_main("deep"), "boom": sc_main("boom"), "dinos": sc_main("dinos"),
           "us": sc_main("us"), "outro": sc_outro}

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
    if name != "outro" and k >= 0:
        a = T - RT[k]
        if REC[k]["ext"] and a < 0.18:                             # extinction: red flash + shake
            q = 1 - a / 0.18
            fr = (fr * (1 - 0.35 * q * FXK) + np.array(RED) * 0.35 * q * FXK).astype(np.uint8)
            fr = np.roll(fr, int(8 * q * FXK) * (1 if int(T * 60) % 2 else -1), axis=1)
        elif not REC[k]["ext"] and a < 0.08:
            fr = np.minimum(255, fr.astype(np.int16) + int(36 * FXK * (1 - a / 0.08))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio: mix of step-2 A (warm) and C (groove) =================
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
        if k == "mar":                                             # marimba (A)
            m_ = int(1.2 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt * 25)
            put(t, x * env(m_, 0.002, 0.4) * v * 0.6, pan=-0.1, send=0.25)
        elif k == "kal":                                           # kalimba / pizz shimmer (C)
            m_ = int(0.9 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = sum((1 / h) * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (6 + 4 * h)) for h in range(1, 6))
            x += 0.4 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt * 5)
            put(t, x * env(m_, 0.002, 0.35) * v * 0.6, pan=0.35, send=0.15)
        elif k == "broken":                                        # the extinction note: falls, detuned, gritty, bit-crushed
            m_ = int(1.3 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            fr = f * 2 ** (-kw["drop"] * np.minimum(1, tt / 1.0) / 12)
            ph = 2 * np.pi * np.cumsum(fr) / SR
            x = np.sin(ph) + .6 * np.sin(ph * 1.013) + .25 * np.sign(np.sin(ph * .5))
            x += .3 * lfilter(*butter(2, 900 / (SR / 2)), rng.standard_normal(m_))
            x = np.round(x * env(m_, 0.004, 0.55) * 5) / 5
            put(t, x * v, send=0.2)
        elif k == "thud":
            m_ = int(1.2 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * np.cumsum(60 * np.exp(-tt * 5) + 32) / SR) * np.exp(-tt * 3) * v)
        elif k == "crunch":
            m_ = int(0.35 * SR)
            x = lfilter(*butter(2, 6000 / (SR / 2)), rng.standard_normal(m_)) * np.exp(-np.arange(m_) / SR * 12)
            put(t, np.round(x * 4) / 4 * v)
        elif k == "bass":
            d = kw["d"]; m_ = int((d + 0.03) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            if kw.get("bt") == "round":
                x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.3)
            else:
                x = 0.5 * np.sign(np.sin(2 * np.pi * f * tt)) + 0.6 * np.sin(2 * np.pi * f * tt)
                x = lfilter(*butter(2, 1000 / (SR / 2)), x) * np.exp(-tt * 6)
            put(t, x * np.clip((d + 0.02 - tt) / 0.02, 0, 1) * v)
        elif k == "kick":
            m_ = int(0.35 * SR); tt = np.arange(m_) / SR
            x = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 16) + 48) / SR) * np.exp(-tt * 12)
            put(t, np.tanh(1.5 * x) * v * 0.8)
        elif k == "snare":
            m_ = int(0.14 * SR)
            x = lfilter(*butter(2, 3500 / (SR / 2)), rng.standard_normal(m_)) * env(m_, 0.0005, 0.045)
            put(t, x * v, send=0.12)
        elif k == "shaker":
            m_ = int(0.06 * SR)
            x = lfilter(*butter(2, 7000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.003, 0.015)
            put(t, x * v * 2, pan=0.3)
        elif k == "crash":
            m_ = int(1.6 * SR)
            put(t, lfilter(*butter(2, 5000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.002, 0.45) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            put(t, lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    out = fx.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
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
        for i, t in enumerate(RT):
            r = REC[i]; print(f"{t:6.2f}s  {r['mya']:>6} Ma  {clk(r['clock'], True)}  lvl {r['lvl']:>3}  p{pitch(i)}  {r['label']}")
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
