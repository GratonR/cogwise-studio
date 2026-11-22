"""BEEPMELODY — THE FIRST ROCKET LANDED ITSELF IN 2015. LISTEN TO IT BECOME ROUTINE.
Every Falcon 9 / Falcon Heavy booster landing attempt, from CRS-5 (10 Jan 2015) to USSF-317 (21 Nov 2026):
691 attempts, 678 landed, 13 crashed (booster_landings.csv, one row per booster, 2 sources per row).
Every note = one booster coming home. A crash = a wrong note, the drums drop out for a bar, red burst + shake.
Clock: one segment per year (YEARD), dates linear INSIDE each year; the busy years get more seconds, never fewer notes.
Scene: side view, light sky. Landing pad on the beach (left), three drone ships at sea (OCISLY, JRTI, ASOG),
the Starship tower in silhouette at the back (it catches a ship on 14 Nov 2026, the one non-Falcon moment).
Music (co-pilot step 2, choice B "Cadence de fusée"): house 128 BPM, kick / clap / hats / saw bass,
each landing = a short pitched "ba-boom" (double sonic boom), crash = drums cut 4 beats + distorted buzz falling.

    python3 booster_landings.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav
                                render out | final out x.mp4          (LV=light|dusk)
"""
import sys, os, math, random, subprocess, csv, datetime as dt
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.8"))
VARIANT = os.environ.get("LV", "light")

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "booster_landings.csv"))))
REC.sort(key=lambda r: (r["date"], int(r["attempt_n"])))
for r in REC:
    r["d"] = dt.date.fromisoformat(r["date"]); r["fail"] = r["outcome"] == "failed"
    s = r["landing_site"]
    r["spot"] = "PAD" if s.startswith("LZ") else s            # OCISLY / JRTI / ASOG
N = len(REC); NFAIL = sum(r["fail"] for r in REC); NLAND = N - NFAIL
TOWER_DAY = dt.date(2026, 11, 14)                           # Starship Flight 15: first ship caught by the tower
LAST = dt.date(2026, 11, 22)                                # clock ends the day after USSF-317

# ================= timeline =================
BPM = 128.0; BEAT = 60.0 / BPM
LEAD = 1.0                                                  # title on screen before the first note
YEARD = {2015: 3.6, 2016: 3.8, 2017: 3.4, 2018: 3.4, 2019: 3.4, 2020: 3.8, 2021: 4.0, 2022: 4.8,
         2023: 6.2, 2024: 8.2, 2025: 9.4, 2026: 7.6}
YS = {}; acc = LEAD
for y in range(2015, 2027): YS[y] = acc; acc += YEARD[y]
HOLD = 1.6                                                  # the last landings + the tower catch breathe before the outro
T_END = acc + HOLD
OUTRO = 12 * BEAT                                           # 5.6 s
TOTAL = T_END + OUTRO
def tdate(d):
    y = d.year; y0 = dt.date(y, 1, 1)
    ylen = ((LAST if y == 2026 else dt.date(y + 1, 1, 1)) - y0).days
    return YS[y] + (d - y0).days / ylen * YEARD[y]
seen = {}
for r in REC:
    j = seen.get(r["date"], 0); seen[r["date"]] = j + 1
    r["t"] = tdate(r["d"]) + 0.08 + j * 0.06                # same-day boosters (Falcon Heavy) a hair apart
RT = [r["t"] for r in REC]
T_TOWER = tdate(TOWER_DAY) + 0.08
def date_at(T):
    if T < LEAD: return dt.date(2015, 1, 1)
    for y in range(2026, 2014, -1):
        if T >= YS[y]:
            y0 = dt.date(y, 1, 1); ylen = ((LAST if y == 2026 else dt.date(y + 1, 1, 1)) - y0).days
            return y0 + dt.timedelta(days=int(min(ylen - 1, (T - YS[y]) / YEARD[y] * ylen)))
    return dt.date(2015, 1, 1)
SC = [("y2015_17", YS[2018]), ("y2018_20", YS[2021] - YS[2018]), ("y2021_22", YS[2023] - YS[2021]),
      ("y2023", YEARD[2023]), ("y2024", YEARD[2024]), ("y2025", YEARD[2025]), ("y2026", YEARD[2026] + HOLD), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
def rec_index(T): return int(np.searchsorted(RT, T, side="right")) - 1

# per-year descent time (fast years: faster boosters, so the scene never clogs)
def gap_of(y):
    n = sum(1 for r in REC if r["d"].year == y); return YEARD[y] / max(n, 1)
DESC = {y: float(np.clip(gap_of(y) * 3.0, 0.45, 1.1)) for y in YEARD}
for r in REC: r["desc"] = DESC[r["d"].year]

# ================= music plan =================
SCALE = [0, 2, 4, 7, 9]
def deg(k, base=57, span=10):
    s = k % span; return base + 12 * (s // 5) + SCALE[s % 5]
ROOTS = [33, 33, 29, 31]                                    # A A F G
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
FAILT = [r["t"] for r in REC if r["fail"]]
def muted(x): return any(0 <= x - c < BEAT * 4 for c in FAILT)
def build():
    nb = int(TOTAL / BEAT) + 1
    ev(0.02, "riser", d=LEAD + 0.3, v=0.08)
    for b in range(nb):
        t = b * BEAT; bar = b // 4
        if t < T_END:
            if muted(t): continue
            ev(t, "kick", v=0.24)
            if b % 2: ev(t, "clap", v=0.07)
            ev(t + BEAT / 2, "hat", v=0.035)
            ev(t + BEAT / 2, "bass", m=ROOTS[(bar // 2) % 4] + 12, v=0.08)
        elif t < TOTAL - 1.2 and (b - int(round(T_END / BEAT))) % 4 == 0:
            ev(t, "pad", m=ROOTS[(bar // 2) % 4], d=4 * BEAT, v=0.05)
    k = 0
    for r in REC:
        if r["fail"]: ev(r["t"], "fail", m=63, v=0.22)
        else: ev(r["t"], "boom", m=deg(k), v=0.16); k += 1
    for j, d in enumerate([0, 4, 7, 12, 16, 19]):           # the tower catch: rising arpeggio
        ev(T_TOWER + j * BEAT / 4, "pluck", m=69 + d, v=0.13)
    ev(T_TOWER, "crash", v=0.09)
    for j, d in enumerate([0, 7, 12, 16, 19, 24]):          # outro: the final count
        ev(T_END + BEAT + j * BEAT / 2, "pluck", m=57 + d, v=0.15)
    ev(T_END + BEAT, "kick", v=0.26); ev(T_END + BEAT, "crash", v=0.10)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= palette =================
if VARIANT == "dusk":
    SKY0 = (34, 30, 74); SKY1 = (226, 120, 84); SEA = (40, 54, 96); SEA2 = (60, 76, 120); LAND = (70, 60, 70); LAND2 = (96, 82, 88)
    INK = (246, 238, 222); INK2 = (196, 176, 170); PANEL = (28, 24, 52); RIM = (230, 150, 90); TOWERC = (24, 20, 44)
    BODY = (236, 232, 226); BODY2 = (150, 146, 150); SHIP = (30, 30, 40); GOLD = (255, 196, 80); RED = (255, 70, 60)
    BAR = (240, 160, 90); BG = (34, 30, 74)
else:
    SKY0 = (150, 200, 240); SKY1 = (236, 244, 250); SEA = (64, 134, 196); SEA2 = (96, 160, 214); LAND = (226, 206, 160); LAND2 = (200, 178, 130)
    INK = (30, 40, 72); INK2 = (92, 104, 140); PANEL = (252, 248, 238); RIM = (150, 180, 214); TOWERC = (150, 170, 196)
    BODY = (250, 250, 250); BODY2 = (120, 128, 146); SHIP = (60, 66, 80); GOLD = (222, 150, 30); RED = (214, 40, 40)
    BAR = (64, 134, 196); BG = (236, 242, 248)
FLAME = [(255, 250, 200), (255, 200, 80), (255, 130, 40)]
WHITE = (255, 255, 255)

# ================= scene geometry (art 180 x 320) =================
HZ = 214                                                    # sea / ground level
SPOTX = {"PAD": 26, "OCISLY": 78, "JRTI": 116, "ASOG": 154}
TOWERX = 8
Y_TOP = 52
def bg_static():
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        f = min(1.0, max(0.0, (y - 40) / (HZ - 40)))
        a[y] = np.array(SKY0) * (1 - f) + np.array(SKY1) * f
    a[HZ:] = SEA
    yy, xx = np.mgrid[0:AH, 0:AW]
    a[(yy >= HZ) & ((xx * 3 + yy * 7) % 23 == 0)] = SEA2
    land = (yy >= HZ - 2) & (xx < 46 - np.maximum(0, yy - HZ) * 0.6)
    a[land] = LAND; a[land & (yy == HZ - 2)] = LAND2
    a[240:] = BG
    return a.astype(np.uint8)
BGA = bg_static()

def draw_tower(d, T):
    x = TOWERX
    d.rectangle([x, 112, x + 5, HZ - 2], fill=TOWERC)        # lattice tower
    for y in range(116, HZ - 2, 6): d.line([x, y, x + 5, y + 6], fill=SKY1 if VARIANT == "light" else SKY0)
    # chopstick arms: open, closing on the caught ship on 14 Nov 2026
    k = 0.0 if T < T_TOWER - 0.2 else ease((T - (T_TOWER - 0.2)) / 0.3)
    ay = 128
    d.line([x + 5, ay, x + 22 - 6 * k, ay - 8 + 8 * k], fill=TOWERC, width=2)
    d.line([x + 5, ay + 4, x + 22 - 6 * k, ay + 12 - 8 * k], fill=TOWERC, width=2)
    if T_TOWER - 1.0 < T:                                   # Starship upper stage coming down to the arms
        f = ease((T - (T_TOWER - 1.0)) / 1.0)
        sy = lerp(40, ay - 14, f); sx = x + 13
        d.rectangle([sx, sy, sx + 4, sy + 22], fill=BODY); d.rectangle([sx, sy, sx + 4, sy + 2], fill=BODY2)
        d.polygon([(sx, sy), (sx + 2, sy - 4), (sx + 4, sy)], fill=BODY)
        if f < 1: d.rectangle([sx + 1, sy + 23, sx + 3, sy + 23 + int(4 + 3 * random.random())], fill=FLAME[1])

def draw_spots(d, T):
    # pad
    x = SPOTX["PAD"]; d.rectangle([x - 8, HZ - 2, x + 8, HZ], fill=(170, 170, 170) if VARIANT == "light" else (90, 86, 96))
    d.line([x - 3, HZ - 2, x + 3, HZ - 2], fill=GOLD)
    for s in ("OCISLY", "JRTI", "ASOG"):
        x = SPOTX[s]; bob = round(math.sin(T * 2.2 + x) * 0.7)
        d.rectangle([x - 12, HZ - 2 + bob, x + 12, HZ + 1 + bob], fill=SHIP)
        d.line([x - 4, HZ - 2 + bob, x + 4, HZ - 2 + bob], fill=GOLD)
        d.rectangle([x - 12, HZ - 6 + bob, x - 11, HZ - 2 + bob], fill=SHIP); d.rectangle([x + 11, HZ - 6 + bob, x + 12, HZ - 2 + bob], fill=SHIP)

def booster(d, x, y, legs, tilt=0.0, burn=False, scale=1.0):
    h = int(20 * scale)
    if tilt:
        ca, sa = math.cos(tilt), math.sin(tilt)
        def P(px, py): return (x + px * ca - py * sa, y + px * sa + py * ca)
        d.polygon([P(-1.5, -h), P(1.5, -h), P(1.5, 0), P(-1.5, 0)], fill=BODY)
        d.line([P(-1.5, -h), P(1.5, -h)], fill=BODY2, width=2)
        return
    d.rectangle([x - 1, y - h, x + 1, y], fill=BODY)
    d.rectangle([x - 1, y - h, x + 1, y - h + 1], fill=BODY2)    # interstage
    d.point([(x - 2, y - h + 2), (x + 2, y - h + 2)], fill=BODY2)  # grid fins
    if legs > 0:
        L = 1 + int(3 * legs)
        d.line([x - 1, y - 2, x - 1 - L, y], fill=BODY2); d.line([x + 1, y - 2, x + 1 + L, y], fill=BODY2)
    if burn:
        fl = 3 + int(4 * random.random())
        d.line([x, y + 1, x, y + fl], fill=FLAME[1]); d.point((x, y + 1), fill=FLAME[0])
        if fl > 4: d.point([(x - 1, y + 2), (x + 1, y + 2)], fill=FLAME[2])

def draw_landings(c, T):
    d = c.a; k = rec_index(T)
    i0 = int(np.searchsorted(RT, T - 3.0))
    # boosters still coming down (their landing time is in the future)
    for i in range(i0, N):
        r = REC[i]
        if RT[i] - r["desc"] > T: break
        _one(d, i, T)

def _one(d, i, T):
    r = REC[i]; t0 = RT[i] - r["desc"]; a = T - t0
    rng = random.Random(i * 7919)
    jit = 0 if r["d"].year < 2022 else rng.randint(-7, 7)
    x = SPOTX[r["spot"]] + jit
    bob = 0 if r["spot"] == "PAD" else round(math.sin(T * 2.2 + SPOTX[r["spot"]]) * 0.7)
    ground = HZ - 2 + bob
    if a < r["desc"]:                                        # descent, landing burn in the last 40 %
        f = a / r["desc"]; y = lerp(Y_TOP, ground, 1 - (1 - f) ** 2)
        booster(d, x, y, legs=max(0.0, (f - 0.7) / 0.3), burn=f > 0.6)
        return
    age = a - r["desc"]
    if r["fail"]:
        if age < 1.4:
            tilt = min(1.4, age * 3.0)
            booster(d, x, ground, legs=1, tilt=tilt if age > 0.1 else 0)
            for q in range(3):
                rr = 2 + (age - q * 0.07) * 30
                if rr > 2 and age - q * 0.07 < 0.6: d.ellipse([x - rr, ground - rr, x + rr, ground + rr], outline=RED if q else FLAME[0])
            for q in range(16):
                ang = rng.random() * 3.2 + 3.1; sp = 10 + rng.random() * 30
                d.point((x + math.cos(ang) * sp * age, ground + math.sin(ang) * sp * age + 20 * age * age), fill=RED if q % 2 else FLAME[1])
        return
    nxt = next((RT[j] for j in range(i + 1, N) if REC[j]["spot"] == r["spot"]), 1e9)
    stay = min(2.4, max(0.25, nxt - RT[i] - 0.05)) if r["d"].year < 2023 else 0.35
    if age < stay:
        booster(d, x, ground, legs=1)
        if age < 0.12: d.line([x - 6, ground + 1, x + 6, ground + 1], fill=WHITE)   # touchdown puff

def frise(c, T):
    d = c.a; W = c.t
    d.rectangle([0, 240, AW, AH], fill=BG)
    X0, X1, Y0, Y1 = 10, 170, 252, 292
    cnt = {y: 0 for y in YEARD}; fl = {y: 0 for y in YEARD}
    for r in REC:
        if r["t"] <= T: cnt[r["d"].year] += 1; fl[r["d"].year] += r["fail"]
    bw = (X1 - X0) / 12; cur = date_at(T).year
    for j, y in enumerate(range(2015, 2027)):
        x0 = int(X0 + j * bw + 1); x1 = int(X0 + (j + 1) * bw - 2)
        land = cnt[y] - fl[y]; h = land / 200 * (Y1 - Y0)
        d.rectangle([x0, Y1, x1, Y1], fill=INK2)
        if land: d.rectangle([x0, int(Y1 - h), x1, Y1], fill=BAR)
        for f in range(fl[y]): d.rectangle([x0, int(Y1 - h) - 2 - 2 * f, x1, int(Y1 - h) - 2 - 2 * f], fill=RED)
        lab = f"{y % 100:02d}"
        text(W, x0 + x1 + 1, 588, lab, fill=INK if y == cur and T < T_END else INK2, align="c")
        if land and (y == cur or T >= T_END) and y >= 2015:
            yy = int((Y1 - h) * 2) - 20 - 4 * fl[y] - (18 if (T >= T_END and j % 2) else 0)
            text(W, x0 + x1 + 1, yy, str(land), fill=INK, align="c")
    text(W, 22, 484, "LANDED PER YEAR", fill=INK2)

def legend(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([0, 612, 360, 640], fill=PANEL); W.rectangle([0, 612, 360, 613], fill=INK2)
    nP = sum(1 for i in range(k + 1) if REC[i]["spot"] == "PAD" and not REC[i]["fail"])
    nS = sum(1 for i in range(k + 1) if REC[i]["spot"] != "PAD" and not REC[i]["fail"])
    text(W, 10, 614, f"ON LAND {nP}", fill=INK)
    text(W, 180, 614, f"ON A SHIP AT SEA {nS}", fill=INK, align="c" if False else "l")

def ship_labels(c, T):
    W = c.t
    for s, lab in (("PAD", "PAD"), ("OCISLY", "SHIP 1"), ("JRTI", "SHIP 2"), ("ASOG", "SHIP 3")):
        text(W, SPOTX[s] * 2, 2 * HZ + 6, lab, fill=(INK if s == "PAD" else WHITE), align="c")
    if T < LEAD + 3.0:
        text(W, (TOWERX + 3) * 2, 2 * 112 - 18, "TOWER", fill=INK2, align="l")

def hud(c, T):
    W = c.t; k = rec_index(T); day = date_at(T)
    W.rectangle([16, 14, 344, 106], fill=PANEL); W.rectangle([16, 14, 344, 15], fill=RIM); W.rectangle([16, 105, 344, 106], fill=RIM)
    nl = sum(1 for i in range(k + 1) if not REC[i]["fail"]); nf = sum(1 for i in range(k + 1) if REC[i]["fail"])
    text(W, 28, 18, "BOOSTERS LANDED", fill=INK2)
    age = T - RT[k] if k >= 0 else 9
    fresh = k >= 0 and age < 0.12
    text(W, 28, 36, f"{nl}", size=40, fill=(RED if REC[k]["fail"] else GOLD) if fresh else INK)
    text(W, 334, 18, f"{day.day} {day.strftime('%b').upper()}", fill=INK2, align="r")
    text(W, 334, 36, str(day.year), size=40, fill=GOLD, align="r")
    text(W, 28, 80, f"CRASHED {nf}", fill=RED if nf else INK2)
    if k >= 0 and age < 1.2:
        r = REC[k]; s = r["mission"].upper()
        if len(s) > 20: s = s[:20]
        text(W, 334, 80, s, fill=RED if r["fail"] else INK2, align="r")

# ================= banners =================
def dstr(d): return f"{d.day} {d.strftime('%b %Y').upper()}"
def idx_of(date, mission=None):
    return next(i for i, r in enumerate(REC) if r["date"] == date and (mission is None or mission in r["mission"]))
WHY = {"2015-01-10": "HIT THE SHIP TOO HARD", "2015-04-14": "TIPPED OVER ON THE SHIP", "2016-01-17": "A LEG DIDN'T LOCK",
       "2016-03-04": "HARD LANDING", "2016-06-15": "ONE ENGINE TOO WEAK", "2018-02-06": "CORE MISSED THE SHIP",
       "2018-12-05": "FIN PUMP STALLED, SPLASH", "2019-06-25": "CORE MISSED THE SHIP",
       "2020-02-17": "MISSED THE SHIP", "2020-03-18": "ENGINE OUT ON THE WAY UP", "2021-02-16": "ENGINE DAMAGE, MISSED SHIP",
       "2024-08-28": "A LEG BROKE AFTER 267", "2025-03-03": "FIRE AFTER TOUCHDOWN"}
BANNERS = {}
for i, r in enumerate(REC):
    if r["fail"]:
        BANNERS[i] = ("CRASH", dstr(r["d"]) + " · " + WHY[r["date"]], "red")
BANNERS[idx_of("2015-01-10")] = ("FIRST TRY: CRASH", "10 JAN 2015 · HIT THE SHIP TOO HARD", "red")
BANNERS[idx_of("2015-12-22")] = ("IT LANDED", "22 DEC 2015 · FIRST ORBITAL BOOSTER BACK", "gold")
BANNERS[idx_of("2016-04-08")] = ("ON A SHIP", "8 APR 2016 · FIRST LANDING AT SEA", "gold")
BANNERS[idx_of("2017-03-30")] = ("SAME BOOSTER, AGAIN", "30 MAR 2017 · FIRST REUSED BOOSTER LANDS", "gold")
for m in (100, 200, 300, 400, 500, 600):
    i = next(j for j, r in enumerate(REC) if r["landed_n"] == str(m))
    BANNERS[i] = (f"#{m}", dstr(REC[i]["d"]) + " · " + REC[i]["mission"].upper(), "big")
BANNERS[idx_of("2024-08-28")] = ("STREAK OVER", "28 AUG 2024 · A LEG BROKE AFTER 267", "red")
BANNERS[idx_of("2026-08-25")] = ("37 FLIGHTS", "25 AUG 2026 · RECORD FOR ONE BOOSTER", "gold")
BANNERS[idx_of("2026-11-21")] = (f"#{NLAND}", "21 NOV 2026 · USSF-317", "big")
BI = sorted(BANNERS)
assert all(len(b[1]) <= 40 for b in BANNERS.values()), [b for b in BANNERS.values() if len(b[1]) > 40]
def banner(c, T):
    k = rec_index(T); W = c.t
    cand = [i for i in BI if i <= k and 0.03 < T - RT[i] < (9 if i == N - 1 else 1.5)]
    if T_TOWER <= T < T_TOWER + 1.9:
        a = T - T_TOWER; yb = 150; tt = "THE TOWER CATCHES A SHIP"; sub = "14 NOV 2026 · STARSHIP FLIGHT 15"
        w = 8 * max(len(tt), len(sub)) + 28
        W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 44], fill=PANEL)
        W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=GOLD); W.rectangle([180 - w / 2, yb + 43, 180 + w / 2, yb + 44], fill=GOLD)
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if a > 0.12: text(W, 180, yb + 22, sub, fill=INK2, align="c")
    if cand:
        i = max(cand); a = T - RT[i]; tt, sub, kind = BANNERS[i]
    else: return
    yb = 318; big = kind == "big" or len(tt) <= 14
    col = RED if kind == "red" else GOLD
    w = max((16 if big else 8) * len(tt), 8 * len(sub)) + 28
    hh = 62 if big else 44
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hh], fill=PANEL)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col); W.rectangle([180 - w / 2, yb + hh - 1, 180 + w / 2, yb + hh], fill=col)
    if big:
        text(W, 180, yb + 3, tt, size=40, fill=col if kind == "red" else INK, align="c")
        if a > 0.12: text(W, 180, yb + 40, sub, fill=INK2, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=col if kind == "red" else INK, align="c")
        if a > 0.12: text(W, 180, yb + 22, sub, fill=INK2, align="c")

def frame_ctx(T):
    c = Ctx(BGA)
    draw_tower(c.a, T); draw_spots(c.a, T); draw_landings(c, T); frise(c, T); legend(c, T); ship_labels(c, T)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); W = c.t
        if T < 3.2:                                        # title card over the first notes
            W.rectangle([16, 14, 344, 150], fill=PANEL); W.rectangle([16, 14, 344, 15], fill=RIM); W.rectangle([16, 149, 344, 150], fill=RIM)
            text(W, 180, 18, "THE FIRST ROCKET", size=40, fill=INK, align="c")
            text(W, 180, 50, "LANDED ITSELF IN 2015", size=40, fill=GOLD, align="c")
            if T > 0.5: text(W, 180, 98, "EVERY NOTE = ONE FALCON BOOSTER", fill=INK2, align="c")
            if T > 0.5: text(W, 180, 120, "COMING HOME · WRONG NOTE = CRASH", fill=RED, align="c")
            if T >= LEAD: banner(c, T)
        else:
            hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T); W = c.t
    W.rectangle([16, 14, 344, 404], fill=PANEL); W.rectangle([16, 14, 344, 16], fill=GOLD)
    text(W, 180, 22, f"{NLAND} LANDED", size=40, fill=INK, align="c")
    text(W, 180, 62, "FALCON BOOSTERS · JAN 2015 TO 21 NOV 2026", fill=INK2, align="c")
    rows = [("CRASHED", str(NFAIL), f"OF {N} TRIES"), ("IN 2015", "1", "OF 3 TRIES"), ("IN 2025", "162", "ONE EVERY 2.3 DAYS"),
            ("IN A ROW NOW", "264", "SINCE MARCH 2025")]
    for j, (a, b, s) in enumerate(rows):
        if t > 0.3 + j * 0.5:
            y = 92 + j * 58
            text(W, 30, y + 6, a, fill=RED if a == "CRASHED" else BAR); text(W, 330, y - 4, b, size=40, fill=INK, align="r")
            text(W, 330, y + 32, s, fill=INK2, align="r")
    if t > 2.4: text(W, 180, 330, "WHAT SHOULD LAND NEXT?", fill=GOLD, align="c")
    if t > 2.8:
        text(W, 180, 352, "DATA: WIKIPEDIA LAUNCH LISTS CHECKED", fill=INK2, align="c")
        text(W, 180, 368, "VS SPACEFLIGHT NOW, SPACE EXPLORED,", fill=INK2, align="c")
        text(W, 180, 384, "GUNTER'S SPACE PAGE (2 SOURCES EACH)", fill=INK2, align="c")
    return c

SCENEFN = {n: sc_main(n) for n in NAMES if n != "outro"}; SCENEFN["outro"] = sc_outro

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
    kp = math.exp(-(T - KICKS[ki]) / 0.06) if ki >= 0 else 0.0
    z = 1.0 + 0.006 * kp * FXK; dx = dy = 0.0
    fi = [f for f in FAILT if 0.0 <= T - f < 0.5]
    if fi:                                                   # the screen shakes when a booster crashes
        a = T - fi[-1]; amp = 24 * FXK * math.exp(-a / 0.14)
        dx = amp * math.sin(a * 90); dy = amp * 0.6 * math.cos(a * 70); z = max(z, 1.02)
    if z > 1.0005 or dx or dy: fr = warp(fr, z, dx, dy, z)
    if fi and T - fi[-1] < 0.22:
        f = 0.30 * FXK * (1 - (T - fi[-1]) / 0.22)
        fr = (fr * (1 - f) + np.array(RED) * f).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.7)) / 0.7)
        if f > 0: fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    if T < 0.2:
        f = 1 - ease(T / 0.2); fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    return fr

# ================= audio =================
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
    def saw(f, dur, det=(.995, 1.0, 1.005)):
        n = int(dur * SR); tt = np.arange(n) / SR
        return sum(2 * ((f * d * tt) % 1) - 1 for d in det) / len(det)
    def pluck(f, dec=.22):
        n = int(.8 * SR); tt = np.arange(n) / SR
        s = sum((1 / h) * np.sin(2 * np.pi * f * h * 1.002 * tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
        return s * env(n, .002, dec)
    n = int((TOTAL + 1.5) * SR); L = np.zeros(n)
    def put(t, sig, g=1.0):
        i = int(t * SR); j = min(n, i + len(sig))
        if 0 <= i < n: L[i:j] += g * sig[:j - i]
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if k == "kick": put(t, kick(v))
        elif k == "clap": put(t, noise(.15, 6000, 25, int(t * 997), 900), v)
        elif k == "hat": put(t, noise(.04, 9000, 120, int(t * 1009), 5000), v)
        elif k == "bass":
            nn = int(BEAT * .45 * SR); tt = np.arange(nn) / SR
            put(t, v * lowpass(saw(mtof(kw["m"]), BEAT * .45), 700) * np.exp(-tt * 6))
        elif k == "boom":                                    # "ba-boom": two pitched thumps + a bright click
            f = mtof(kw["m"])
            put(t, kick(v * .45, f * 1.5, f * .5)); put(t + .045, kick(v * .32, f * 1.5, f * .5))
            nn = int(.12 * SR); put(t, v * .32 * lowpass(saw(f * 2, .12), 3000) * env(nn, .002, .05))
        elif k == "fail":
            nn = int(1.0 * SR); tt = np.arange(nn) / SR
            f = mtof(kw["m"]) * np.exp(-tt * 1.3)
            s = np.tanh(4 * (2 * ((np.cumsum(f) / SR) % 1) - 1))
            put(t, v * lowpass(s, 2500) * env(nn, .002, .5)); put(t, noise(.6, 3000, 5, 911, 200), .09)
        elif k == "pluck": put(t, v * pluck(mtof(kw["m"])))
        elif k == "pad":
            nn = int((kw["d"] + .4) * SR); tt = np.arange(nn) / SR
            e = np.minimum(1, tt / .3) * np.clip((kw["d"] + .4 - tt) / .4, 0, 1)
            s = sum(lowpass(saw(mtof(kw["m"] + 12 + iv), kw["d"] + .4), 1400) for iv in (0, 7, 12, 16))
            put(t, v * s * e)
        elif k == "crash": put(t, noise(1.8, 12000, 1.6, 1234, 3000), v)
        elif k == "riser":
            nn = int(kw["d"] * SR); tt = np.arange(nn) / SR
            put(t, highpass(np.random.RandomState(3).randn(nn), 1500) * (tt / kw["d"]) ** 2 * v)
    out = L.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22)]:
        k_ = int(d * SR); out[k_:] += g * .6 * L[:-k_]
    L = .85 * L + .15 * lowpass(out, 4000)
    tt = np.arange(n) / SR; L *= np.clip((TOTAL + 0.6 - tt) / 1.2, 0, 1)
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
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T + 1e-9)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/{VARIANT}_t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print("TOTAL", round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, "attempts", N, "landed", NLAND, "fail", NFAIL)
        print("tower", round(T_TOWER, 2), "desc", DESC)
        print(Counter(k for _, k, _ in EV)); print(Counter(r["spot"] for r in REC))
        for i in BI: print(i + 1, REC[i]["date"], round(RT[i], 2), BANNERS[i][:2])
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
