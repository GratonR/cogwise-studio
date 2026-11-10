"""BEEPMELODY · HOW HIGH HAVE HUMANS EVER BEEN? — every human height record, 1783 -> 2026.
Every beep = humans higher than ever before. Pitch = log(height). A fast climb of notes = the size of the jump.
Built on the shared data-sonification engine (studio/this-melody-is/engine), which is imported, never modified."""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, os.path.abspath(ENGINE))
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, CREAM, YEL, RED, DIM, text, panel, ease, eout, lerp)
from pi import Ctx, warp, glitch_frame

FXK = float(os.environ.get("PI_FX", "0.8"))
FINAL = "outro"
DUCK = REVERB = RICH = True
RISE = False
# A minor pentatonic, A3 .. A6 : index = log(height)
SCALE = [50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88, 91, 93]
# amber palette (records / history)
AMB, AMB_HI, AMB_LO = (255, 176, 64), (255, 226, 150), (150, 86, 30)
INK = (14, 8, 6)

# ================= data =================
REC = []
with open(os.path.join(HERE, "altitude.csv")) as f:
    for r in csv.DictReader(f):
        y, m, d = (int(x) for x in r["date"].split("-"))
        REC.append(dict(date=r["date"], year=y + (m - 1) / 12 + (d - 1) / 365, Y=y, M=m, v=float(r["value_m"]),
                        approx=r["approx"] == "1", kind=r["kind"], label=r["label"], detail=r["detail"]))
LMIN, LMAX = math.log10(20), math.log10(4.1e8)
# pitch = log(height) + rank: every record sits a little higher than the last one, big jumps leap
for i, r in enumerate(REC):
    r["L"] = math.log10(r["v"])
    r["n"] = min(len(SCALE) - 1, int(round(0.28 * i + 1.45 * (r["L"] - math.log10(REC[0]["v"])))))

# event landing times (s) — one per record
TIMES = [0.9, 2.1, 3.5,  5.4, 7.4, 9.8,  13.0, 16.2,  19.8, 21.8, 23.2, 24.6, 25.6, 27.0, 28.6,
         30.8, 32.0, 33.2, 34.8, 36.6,  38.8, 40.9, 42.4, 43.9, 45.4,  49.2, 52.8,  60.0]
assert len(TIMES) == len(REC)
for r, t in zip(REC, TIMES): r["t"] = t
BIG = {"VOSTOK 1", "APOLLO 8", "ARTEMIS II"}

SC = [("intro", 4.5), ("balloons", 7.5), ("gas", 7.0), ("strato", 11.0), ("rocketplanes", 8.0),
      ("orbit", 9.0), ("moon", 8.0), ("gap", 5.0), ("outro", 7.0)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
TOTAL = acc_
DUR = dict(SC); NAMES = [n for n, _ in SC]
assert abs(START["outro"] - REC[-1]["t"]) < 1e-6
TITLES = {"intro": "HOW HIGH HAVE WE BEEN?", "balloons": "BALLOONS", "gas": "INTO THIN AIR", "strato": "THE STRATOSPHERE",
          "rocketplanes": "ROCKET PLANES", "orbit": "ORBIT", "moon": "THE MOON", "gap": "...AND THEN", "outro": "TODAY"}
RISER_T = REC[-1]["t"] - 1.7
def scene_at(T):
    for n, d in SC:
        if START[n] <= T < START[n] + d: return n
    return NAMES[-1]

# year shown on the HUD: interpolated between records (held before the first)
YT = [0.0] + TIMES; YY = [REC[0]["year"]] + [r["year"] for r in REC]
def year_at(T): return float(np.interp(T, YT, YY))
def last_rec(T):
    k = -1
    for i, r in enumerate(REC):
        if r["t"] <= T + 1e-9: k = i
    return k
CLIMB = 0.32
def tip_L(T):
    """displayed tip height (log10 m): climbs from the previous record to the next over CLIMB s before landing"""
    for i, r in enumerate(REC):
        if T < r["t"]:
            prev = REC[i - 1]["L"] if i else math.log10(8)
            if T >= r["t"] - CLIMB: return lerp(prev, r["L"], eout((T - (r["t"] - CLIMB)) / CLIMB))
            return prev
    return REC[-1]["L"]

# ================= music (event list read by pi_audio.py) =================
def bpm(T):
    pts = [(0, 112), (START["balloons"], 114), (START["strato"], 120), (START["rocketplanes"], 124), (START["orbit"], 128),
           (START["outro"], 128), (TOTAL, 128)]
    return float(np.interp(T, [a for a, _ in pts], [b for _, b in pts]))
def beat_times(T):
    out, t = [], 0.0
    while t < T: out.append(t); t += 60 / bpm(t)
    return out
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
KICKS, SNARES, GL, FLASH = [], [], [], []
OUTRO_DIGITS = [18, 16, 13, 11, 8]

def build():
    prev_n = 0
    for i, r in enumerate(REC):
        t, n = r["t"], r["n"]
        steps = list(range(prev_n + 1, n)) if n > prev_n + 1 else []
        if len(steps) > 0:        # the climb: one quick note per pentatonic step crossed
            k = len(steps)
            for j, s in enumerate(steps):
                ev(t - CLIMB + CLIMB * j / k, "edigit", d=s, rate=34)
            if k >= 6: ev(t - CLIMB, "whoosh")
        ev(t, "digit", d=n, ok=True)
        ev(t, "chime", lvl=min(5, n // 3))
        if r["label"] in BIG or i == 0:
            ev(t, "kickhit"); FLASH.append(t)
            if r["label"] != "ARTEMIS II": ev(t, "chime", lvl=5)
        prev_n = n
    # Artemis: arpeggio fundamental, fifth, octave, twelfth on the record
    tA = REC[-1]["t"]
    for k, d in enumerate([8, 11, 13, 16, 18]): ev(tA + 0.18 * k, "digit", d=d, ok=True)
    drums()
    GL.append((REC[20]["t"] - 0.22, 0.2, "stutter", 60 / bpm(REC[20]["t"]) / 4))   # just before Gagarin
    GL.append((REC[25]["t"] - 0.22, 0.2, "stutter", 60 / bpm(REC[25]["t"]) / 8))   # just before Apollo 8
    GL.sort()

def drums():
    for bi, bt in enumerate(beat_times(TOTAL - 1.0)):
        sc = scene_at(bt); bl = 60 / bpm(bt); pos = bi % 4
        ch = CHORDS[(bi // 4) % 4]; root = ch[0] - 12
        gap = sc == "gap"
        if sc == "outro":            # afterglow: the record chord rings on, soft pulse under the final card
            if bt < START["outro"] + 2.0: continue
            if pos == 0: ev(bt, "pad", ch=CHORDS[0], d=bl * 4); ev(bt, "kick", v=0.2)
            ev(bt, "bass", m=45, d=bl * 0.9, v=0.08); ev(bt + bl / 2, "hat", v=0.02, open=False)
            if pos % 2 == 0: ev(bt, "edigit", d=[18, 16, 13, 11][(bi // 2) % 4], rate=12)
            continue
        if sc == "intro":
            if pos == 0 and bt > 1.0: ev(bt, "kick", v=0.30)
        elif gap:
            if pos == 0: ev(bt, "kick", v=0.22)
            ev(bt + bl / 2, "hat", v=0.025, open=False)
        else:
            ev(bt, "kick", v=0.45 if sc not in ("balloons", "gas") else 0.36)
            if sc not in ("balloons",) and pos in (1, 3): ev(bt, "snare", v=0.19)
            sub = 4 if sc in ("orbit", "moon") else 2
            for h in range(sub): ev(bt + h * bl / sub, "hat", v=0.035 if h % 2 else 0.045, open=(h == sub // 2))
        for h in range(2):
            if sc == "intro" and h == 1: continue
            m = root + (12 if (pos * 2 + h) % 4 == 3 else 0)
            ev(bt + h * bl / 2, "bass", m=m, d=bl / 2 * 0.9, v=0.11 if sc in ("intro", "gap") else 0.16)
        if pos == 0: ev(bt, "pad", ch=ch, d=bl * 4)
    for t, k, kw in EV:
        if k in ("kick", "kickhit") and (k == "kickhit" or kw["v"] >= 0.36): KICKS.append(t)
        if k == "snare" and kw["v"] > 0.15: SNARES.append(t)
    KICKS.sort(); SNARES.sort()

build()
EV.sort(key=lambda e: e[0])

# ================= formatting (SI first, then US) =================
def sp(n): return f"{int(round(n)):,}".replace(",", " ")
def fmt_si(v, approx=False):
    a = "≈" if approx else ""
    return a + (sp(v / 1000) + " KM" if v >= 1e5 else sp(v) + " M")
def fmt_us(v, approx=False):
    a = "≈" if approx else ""
    return a + (sp(v / 1609.344) + " MI" if v >= 1e5 else sp(v / 0.3048) + " FT")
MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

# ================= scene: the height ladder (log scale, side view) =================
YC = 150                      # art row where the tip sits
def cam(T):
    """(log height at row YC, pixels per decade)"""
    Lc, P = tip_L(T) - 0.15, 66.0
    if T >= START["outro"]:
        q = ease((T - START["outro"] - 2.4) / 2.4)
        Lc = lerp(Lc, 1.15 + (258 - YC) / 23.0, q); P = lerp(P, 23.0, q)
    return Lc, P
def row_of(L, Lc, P): return YC - (L - Lc) * P
def L_of_row(y, Lc, P): return Lc + (YC - y) / P

SKY = [(0.9, (250, 196, 120)), (2.5, (244, 150, 76)), (3.6, (206, 98, 62)), (4.2, (130, 56, 72)), (4.6, (60, 28, 62)),
       (5.0, (20, 12, 32)), (5.6, (6, 5, 14)), (9.5, (4, 4, 10))]
SL = np.array([a for a, _ in SKY]); SCOL = np.array([b for _, b in SKY], float)
_rng = np.random.default_rng(4)
STAR_L = _rng.uniform(4.7, 9.4, 900); STAR_X = _rng.integers(0, AW, 900); STAR_V = _rng.integers(80, 240, 900)
GRASS = _rng.random(AW)
def background(Lc, P):
    ys = np.arange(AH); L = L_of_row(ys, Lc, P)
    col = np.stack([np.interp(L, SL, SCOL[:, k]) for k in range(3)], 1)
    a = np.repeat(col[:, None, :], AW, 1)
    dd = ((np.arange(AH)[:, None] + np.arange(AW)[None, :]) % 2 == 0)
    band = (np.floor(L * 12) % 2 == 0)[:, None] & dd
    a = np.where(band[..., None], a * 0.965, a)
    # stars above ~50 km
    yy = row_of(STAR_L, Lc, P).astype(int); ok = (yy >= 0) & (yy < AH)
    fade = np.clip((STAR_L - 4.7) / 0.6, 0, 1)
    for y, x, v, f in zip(yy[ok], STAR_X[ok], STAR_V[ok], fade[ok]):
        a[y, x] = a[y, x] * (1 - f) + np.array([v, v, min(255, v + 15)]) * f
    # ground below ~8 m
    g = row_of(math.log10(8), Lc, P)
    if g < AH:
        g0 = int(max(0, g))
        a[g0:] = (46, 30, 20)
        for x in range(AW):
            h = int(g + 2 + GRASS[x] * 3)
            if 0 <= h < AH: a[max(0, int(g)):h, x] = (70, 52, 26)
        a[int(max(0, g)):int(max(0, g)) + 1] = (120, 84, 40) if g >= 0 else a[0]
    return np.clip(a, 0, 255).astype(np.uint8)

LANDMARKS = [(330, "EIFFEL TOWER  330 M"), (8849, "EVEREST  8 849 M"), (1e5, "SPACE BEGINS  100 KM"), (3.844e8, "THE MOON ≈384 400 KM")]
DECADES = [(1, "10 M"), (2, "100 M"), (3, "1 KM"), (4, "10 KM"), (5, "100 KM"), (6, "1 000 KM"), (7, "10 000 KM"), (8, "100 000 KM")]
X0, DX = 44, 4.5
def xi(i): return X0 + i * DX

def sprite(d, x, y, kind, T):
    x, y = int(x), int(y)
    if kind == "balloon":
        d.ellipse([x - 4, y - 13, x + 4, y - 4], fill=(214, 70, 52), outline=(255, 214, 150))
        d.line([x - 3, y - 4, x - 1, y - 1], fill=(200, 170, 120)); d.line([x + 3, y - 4, x + 1, y - 1], fill=(200, 170, 120))
        d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(120, 80, 40))
    elif kind == "plane":
        d.polygon([(x - 6, y), (x + 5, y - 2), (x + 7, y), (x + 5, y + 1)], fill=(230, 230, 220))
        d.line([x - 5, y - 3, x - 3, y], fill=(230, 230, 220))
        if int(T * 20) % 2: d.point((x - 7, y), fill=AMB)
    else:
        d.polygon([(x, y - 8), (x - 2, y - 4), (x - 2, y + 3), (x + 2, y + 3), (x + 2, y - 4)], fill=(236, 232, 220))
        d.point((x, y - 2), fill=(60, 120, 200))
        if kind == "rocket":
            fl = 3 + int(T * 30) % 3
            d.line([x - 1, y + 4, x - 1, y + 3 + fl], fill=AMB); d.line([x + 1, y + 4, x + 1, y + 3 + fl], fill=AMB_HI)

def draw_scene(c, T, labels=True):
    Lc, P = cam(T)
    c.art = Image.fromarray(background(Lc, P)); c.a = ImageDraw.Draw(c.art)
    a, W = c.a, c.t
    # Moon disc (average distance)
    ym = row_of(math.log10(3.844e8), Lc, P)
    if -20 < ym < AH + 20:
        rr = 9 if P > 40 else 6
        a.ellipse([150 - rr, ym - rr, 150 + rr, ym + rr], fill=(214, 208, 190))
        a.ellipse([150 - rr // 2, ym - rr // 2, 150 - rr // 2 + 3, ym - rr // 2 + 2], fill=(170, 164, 150))
        a.ellipse([152, ym + 1, 155, ym + 4], fill=(180, 174, 160))
    # decade ruler (left) + landmarks (right)
    for L, lab in DECADES:
        y = row_of(L, Lc, P)
        if 30 < y < 262:
            a.line([0, y, 6, y], fill=(255, 236, 200))
            for x in range(8, AW, 4): a.point((x, y), fill=(140, 110, 90) if L_of_row(y, Lc, P) < 4.6 else (60, 56, 80))
            if labels: text(W, 4, y * 2 - 20, lab, fill=CREAM if L < 4.6 else (190, 180, 210))
    for v, lab in LANDMARKS:
        y = row_of(math.log10(v), Lc, P)
        if 30 < y < 262:
            for x in range(60, AW, 3): a.point((x, y), fill=(255, 220, 160) if v < 1e5 else (150, 190, 255))
            if labels: text(W, 270 if v > 1e8 else 354, y * 2 - 20, lab, fill=(255, 230, 190) if v < 1e5 else (170, 200, 255), align="r")
    # Eiffel tower silhouette for scale
    yg, yt = row_of(math.log10(8), Lc, P), row_of(math.log10(330), Lc, P)
    if yt < AH and yg > 0:
        for y in range(int(max(0, yt)), int(min(AH, yg))):
            k = max(0.0, (y - yt) / max(1, yg - yt)); w = 0.5 + 6 * k ** 2.2
            a.line([24 - w, y, 24 + w, y], fill=(40, 24, 18))
    # the staircase of records
    k = last_rec(T); Lt = tip_L(T)
    pts = []
    for i in range(k + 1):
        pts.append((xi(i), row_of(REC[i]["L"], Lc, P)))
    xt = xi(k + 1) if (k + 1 < len(REC) and T >= REC[k + 1]["t"] - CLIMB) else (xi(k) + 3 if k >= 0 else xi(0))
    if k + 1 < len(REC) and T >= REC[k + 1]["t"] - CLIMB: xt = xi(k + 1)
    yt_ = row_of(Lt, Lc, P)
    for i, (x, y) in enumerate(pts):
        nx = pts[i + 1][0] if i + 1 < len(pts) else xt
        a.line([x, y, nx, y], fill=AMB)
        if i + 1 < len(pts): a.line([nx, y, nx, pts[i + 1][1]], fill=AMB_LO)
        a.rectangle([x - 1, y - 1, x + 1, y + 1], fill=AMB_HI)
    if pts:
        a.line([xt, pts[-1][1], xt, yt_], fill=AMB_HI)
    # tip sprite
    i_next = min(len(REC) - 1, k + 1) if (k + 1 < len(REC) and T >= REC[k + 1]["t"] - CLIMB) else max(0, k)
    if T > 0.3: sprite(a, xt, yt_, REC[i_next]["kind"], T)
    # ring on landing
    if k >= 0 and T - REC[k]["t"] < 0.6:
        q = (T - REC[k]["t"]) / 0.6; rr = 2 + q * 14
        a.ellipse([xt - rr, yt_ - rr, xt + rr, yt_ + rr], outline=(255, 255, 230) if q < 0.5 else AMB)

# ---- bottom chart: record height vs year, 1783 -> 2026 ----
def draw_chart(c, T):
    x0, x1, yb, h = 18, 162, 304, 30
    c.a.rectangle([x0 - 3, yb - h - 14, x1 + 3, yb + 3], fill=INK, outline=(90, 60, 30))
    def X(y): return x0 + (x1 - x0) * (y - 1783) / (2026.3 - 1783)
    def Y(L): return yb - (L - 1.2) / (8.8 - 1.2) * h
    yr = year_at(T); k = last_rec(T)
    if k < 0: return
    px, py = X(REC[0]["year"]), Y(REC[0]["L"])
    for i in range(1, k + 1):
        nx = X(REC[i]["year"]); c.a.line([px, py, nx, py], fill=AMB); ny = Y(REC[i]["L"]); c.a.line([nx, py, nx, ny], fill=AMB); px, py = nx, ny
    cx = X(min(yr, 2026.3)); c.a.line([px, py, cx, py], fill=AMB)
    c.a.rectangle([cx - 1, py - 1, cx + 1, py + 1], fill=(255, 255, 230))
    text(c.t, x0 * 2, (yb - h - 14) * 2 + 1, "HEIGHT RECORD (LOG)  1783-2026", fill=(200, 160, 110))

def hud(c, T, title):
    k = last_rec(T)
    if k < 0: v, us = "0 M", "0 FT"
    else:
        r = REC[k]; v, us = fmt_si(r["v"], r["approx"]), fmt_us(r["v"], r["approx"])
    yr = int(year_at(T))
    age = T - REC[k]["t"] if k >= 0 else None
    panel(c.t, title, v, us, None, right=["YEAR", str(yr)], age=age)

def banner(c, T):
    k = last_rec(T)
    if k < 0: return
    r = REC[k]; a = T - r["t"]
    nxt = REC[k + 1]["t"] if k + 1 < len(REC) else 99
    hold = min(2.2, nxt - r["t"] - 0.15) if r["label"] not in BIG else 3.0
    if a > hold: return
    big = r["label"] in BIG
    l1 = r["label"]; l2 = f"{MON[r['M'] - 1]} {r['Y']} · {r['detail']}"
    n = int(min(len(l1), a * 40))
    yb = 176
    if big:
        w = max(16 * len(l1), 8 * len(l2)) + 24
        c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 64], fill=(30, 16, 6)); c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 1], fill=AMB)
        text(c.t, 180, yb + 2, l1[:n], size=40, fill=AMB_HI, align="c")
        if a > 0.3: text(c.t, 180, yb + 42, l2, fill=CREAM, align="c")
    else:
        w = 8 * max(len(l1), len(l2)) + 24
        c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 40], fill=(24, 12, 6)); c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 1], fill=AMB)
        text(c.t, 180, yb + 1, l1[:n], fill=CREAM, align="c")
        if a > 0.3: text(c.t, 180, yb + 19, l2, fill=(240, 190, 120), align="c")

def sc_generic(name):
    def f(t):
        T = START[name] + t
        c = Ctx(np.zeros((AH, AW, 3), np.uint8))
        draw_scene(c, T); draw_chart(c, T); hud(c, T, TITLES[name]); banner(c, T)
        return c
    return f

def sc_intro(t):
    T = t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T); banner(c, T)
    q = ease((t - 0.1) / 0.4)
    if q > 0:
        W = c.t
        W.rectangle([24, 62, 336, 162], fill=(16, 9, 5)); W.rectangle([24, 62, 336, 63], fill=AMB)
        text(W, 36, 64, "HOW HIGH HAVE", size=40, fill=CREAM)
        if t > 0.5: text(W, 36, 108, "HUMANS BEEN?", size=40, fill=AMB_HI)
    if t > 1.3:
        W = c.t; W.rectangle([20, 552, 340, 600], fill=(16, 9, 5))
        text(W, 180, 556, "EVERY BEEP = HUMANS HIGHER", fill=CREAM, align="c")
        text(W, 180, 576, "THAN EVER BEFORE", fill=AMB_HI, align="c")
    return c

def sc_gap(t):
    T = START["gap"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T); draw_chart(c, T); hud(c, T, TITLES["gap"])
    W = c.t; yrs = int(year_at(T)) - 1970
    if t > 0.4:
        W.rectangle([40, 176, 320, 238], fill=(24, 12, 6)); W.rectangle([40, 176, 320, 177], fill=(150, 86, 30))
        text(W, 180, 178, f"{yrs} YEARS", size=40, fill=CREAM, align="c")
        text(W, 180, 216, "NOBODY WENT HIGHER", fill=(240, 190, 120), align="c")
    return c

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T, labels=t > 4.6 or t < 2.4)
    if t < 3.0: draw_chart(c, T)
    W = c.t
    r = REC[-1]
    W.rectangle([28, 60, 332, 172], fill=(16, 9, 5)); W.rectangle([28, 60, 332, 61], fill=AMB)
    text(W, 180, 62, "6 APR 2026 · ARTEMIS II", fill=(240, 190, 120), align="c")
    text(W, 180, 84, fmt_si(r["v"]), size=40, fill=AMB_HI, align="c")
    text(W, 180, 126, fmt_us(r["v"]) + " FROM EARTH", fill=CREAM, align="c")
    text(W, 180, 146, "THE FARTHEST HUMANS HAVE EVER BEEN", fill=CREAM, align="c")
    if t > 1.4:
        W.rectangle([40, 178, 320, 218], fill=(24, 12, 6))
        text(W, 180, 179, "+6 600 KM", fill=AMB_HI, align="c"); text(W, 180, 197, "AFTER 56 YEARS", fill=CREAM, align="c")
    if t > 3.2:
        W.rectangle([16, 604, 344, 630], fill=(10, 6, 4))
        text(W, 180, 606, "DATA: FAI · NASA · GUINNESS WORLD RECORDS", fill=DIM, align="c")
    return c

SCENEFN = {n: sc_generic(n) for n in NAMES}
SCENEFN["intro"] = sc_intro; SCENEFN["gap"] = sc_gap; SCENEFN["outro"] = sc_outro

# ================= FX (same mechanics as the reference episode) =================
def intensity(T): return 0.08 + 0.6 * ease(T / START["outro"]) ** 1.8
def active_glitch(T):
    for g in GL:
        if g[0] <= T < g[0] + g[1]: return g
    return None
REC_T = np.array([r["t"] for r in REC])
def fx(fr, T, name, t):
    I = intensity(T) * FXK
    if name == "outro": I *= 0.35
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    ri = np.searchsorted(REC_T, T, side="right") - 1
    rp = math.exp(-(T - REC_T[ri]) / 0.09) if ri >= 0 else 0.0
    si = np.searchsorted(SNARES, T, side="right") - 1
    sd = (T - SNARES[si]) if si >= 0 else 9
    squash = math.exp(-sd / 0.09) * math.cos(2 * math.pi * sd / 0.14)
    zoom = 1.01 + kp * (0.008 + 0.02 * I) + rp * 0.025
    zx = zoom * (1 - 0.015 * squash * I); zy = zoom * (1 + 0.03 * squash * I)
    kd = (T - KICKS[ki]) if ki >= 0 else 9
    spring = math.exp(-kd / 0.11) * math.cos(2 * math.pi * kd / 0.17)
    rng = random.Random(int(T * 1000))
    fr = warp(fr, zx, rng.uniform(-1, 1) * rp * 6, -spring * (4 + 30 * I))
    split = int(rp * 5 + kp * 2 * I)
    if split > 0:
        out = fr.copy(); out[:, split:, 0] = fr[:, :-split, 0]; out[:, :-split, 2] = fr[:, split:, 2]; fr = out
    fl = kp * (8 + 22 * I) + rp * 18
    for tm in FLASH:
        if 0 <= T - tm < 0.14: fl += 120 * (1 - (T - tm) / 0.14)
    if fl > 1: fr = np.minimum(255, fr.astype(np.int16) + int(fl)).astype(np.uint8)
    return fr

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    g = active_glitch(T)
    if g and g[2] == "stutter":
        T2 = g[0] + ((T - g[0]) % g[3]); t = T2 - START[name]
        if t < 0: idx -= 1; name = NAMES[idx]; t = T2 - START[name]
    c = SCENEFN[name](t)
    fr = v2.compose(c, t, idx)
    fr = fx(fr, START[name] + t, name, t)
    if g: fr = glitch_frame(fr, T, g)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.0)) / 1.0)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))): p.stdin.write(render_frame(idx, f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((360, 640), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    elif mode == "info":
        from collections import Counter
        print(TOTAL, Counter(k for _, k, _ in EV))
        for r in REC: print(r["date"], r["t"], r["n"], fmt_si(r["v"], r["approx"]), fmt_us(r["v"], r["approx"]), r["label"])
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(2) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
