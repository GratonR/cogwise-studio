"""BEEPMELODY — 100 M: MEN VS WOMEN. Every official 100 m world record that lowered the mark (men 1912 -> 2009,
women 1922 -> 1988), two lanes like 'the race to the sky'. Every note = a record in its lane; faster = higher note.
Live gap between the two records in the footer (3.2 s in 1922 -> 0.91 s today). 1977 = electronic timing only.
Climax: a 100 m race in real time between the first and the current record holders, at their average speed.
Guillaume 2026-11-09: 'plus dynamique et un son different de d'habitude' -> 128 BPM stadium house/funk
(four-on-the-floor, claps, funk synth bass, chord stabs), brass stab = men, steel drum = women.
Data: sprint100.csv (2 sources per row).

    python3 sprint100.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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
REC = list(csv.DictReader(open(os.path.join(HERE, "sprint100.csv"))))
def yfrac(d):
    y, m, dd = (int(x) for x in d.split("-")); return y + (m - 1) / 12 + (dd - 1) / 365
for r in REC:
    r["s"] = float(r["time"]); r["year"] = r["date"][:4]; r["yf"] = yfrac(r["date"]); r["sw"] = r["note"].startswith("ELECTRONIC")
N = len(REC)
LANES = ["men", "women"]
LNAME = {"men": "MEN", "women": "WOMEN"}

def fmt_t(r): return f"{r['time']} S"                                  # as written in the record (10.6 hand / 9.95 auto)
def kmh(s): return 100 / s * 3.6
def mph(s): return 100 / s * 3600 / 1609.344
def spd(r): return f"AVG {kmh(r['s']):.1f} KM/H · {mph(r['s']):.1f} MPH"

# ================= palette (clear stadium day) =================
INK = (30, 38, 70)
INK2 = (96, 106, 140)
CREAM = (252, 249, 240)
WHITE = (255, 255, 255)
GOLD = (238, 170, 40)
LCOL = {"men": (36, 104, 214), "women": (226, 58, 118)}
SKY0, SKY1 = (214, 236, 250), (246, 250, 252)
TRACK = (206, 92, 64)
TRACK2 = (188, 78, 54)
GRASS = (110, 178, 96)

# ================= timeline (on the beat) =================
BPM = 128.0
BEAT = 60.0 / BPM
INTRO_B = 6
def gap_beats(i):
    a, b = REC[i - 1], REC[i]
    if b["sw"] and a["sw"]: return 0
    dy = b["yf"] - a["yf"]
    if i == N - 1: return 4
    if dy < 0.05: return 1
    if dy <= 2: return 1.5
    if dy <= 6: return 2.5
    if dy <= 15: return 3
    return 4
GAPS_B = [gap_beats(i) for i in range(1, N)]
HOLD_B = 10
RT = [INTRO_B * BEAT]
for g in GAPS_B: RT.append(RT[-1] + g * BEAT)
T_FINAL = RT[-1]
T_REC_END = T_FINAL + HOLD_B * BEAT
PRE_B = 4                                       # "on your marks / set" before the gun
RACE0 = T_REC_END + PRE_B * BEAT                # gun
RUN = [("USAIN BOLT", "men", 9.58, "2009"), ("FLORENCE GRIFFITH JOYNER", "women", 10.49, "1988"),
       ("DONALD LIPPINCOTT", "men", 10.6, "1912"), ("MARIE MEJZLIKOVA", "women", 13.6, "1922")]
RUN_SHORT = ["BOLT", "FLO-JO", "LIPPINCOTT", "MEJZLIKOVA"]
T_FIN = RACE0 + 9.58
RACE_HOLD = 4.6
OUTRO_D = 14 * BEAT
def first_year(y): return next(i for i, r in enumerate(REC) if r["yf"] >= y)
I1940, ISW = first_year(1940), next(i for i, r in enumerate(REC) if r["sw"])
SC = [("intro", RT[0]), ("early", RT[I1940] - RT[0]), ("mid", RT[ISW] - RT[I1940]), ("auto", T_REC_END - RT[ISW]),
      ("race", T_FIN + RACE_HOLD - T_REC_END), ("outro", OUTRO_D)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
TOTAL = acc_

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k
def lane_last(k, ln):
    for i in range(k, -1, -1):
        if REC[i]["lane"] == ln: return i
    return -1
def gap_at(k):
    a, b = lane_last(k, "men"), lane_last(k, "women")
    if a < 0 or b < 0: return None
    return REC[b]["s"] - REC[a]["s"]

# playhead year
def year_at(T):
    if T < RT[0]: return 1910 + 2.0 * T / RT[0]
    k = rec_index(T)
    if k >= N - 1: return lerp(REC[-1]["yf"], 2026.85, ease((T - RT[-1]) / (HOLD_B * BEAT * 0.8)))
    t0, t1 = RT[k], RT[k + 1]
    return lerp(REC[k]["yf"], REC[k + 1]["yf"], (T - t0) / max(1e-6, t1 - t0))

# y range (seconds) follows the data: early 10.1..13.9, late 9.4..10.8
def rng_for(k):
    vals = [REC[i]["s"] for i in (lane_last(k, "men"), lane_last(k, "women")) if i >= 0] or [10.6]
    lo, hi = min(vals) - 0.25, max(vals) + 0.45
    if hi - lo < 1.2: hi = lo + 1.2
    return lo, hi
def yrange(T):
    k = rec_index(T)
    if k < 0: return 10.1, 13.9
    a = rng_for(k - 1) if k >= 1 else (10.1, 13.9)
    if k == 0: a = (10.1, 13.9)
    b = rng_for(k); f = ease((T - RT[k]) / 0.5)
    return lerp(a[0], b[0], f), lerp(a[1], b[1], f)

# ================= music plan (shared by picture + audio) =================
SCALE = [64, 67, 69, 71, 74, 76, 79, 81, 83, 86, 88, 91, 93]          # E minor pentatonic from E4
LANE_RANGE = {"men": (2, 12), "women": (0, 10)}
def pitch(i):
    ln = REC[i]["lane"]; idx = [j for j in range(N) if REC[j]["lane"] == ln and not REC[j]["sw"]]
    if REC[i]["sw"]:
        i = max(j for j in idx if j < i)
    r = idx.index(i); lo, hi = LANE_RANGE[ln]
    return SCALE[lo + int(round(r * (hi - lo) / max(1, len(idx) - 1)))]
CHORDS = [(55, 59, 62, 66), (55, 59, 60, 64), (55, 57, 60, 64), (54, 57, 59, 63)]   # Em9 Cmaj7 Am7 B7
ROOTS = [40, 36, 45, 35]
VOICE = {"men": "brass", "women": "steel"}
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT)) + 1
    ev(0.05, "gun", v=0.55)
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        ch = CHORDS[bar % 4]; ro = ROOTS[bar % 4]
        prerace = T_REC_END <= t < RACE0
        late = t >= T_FIN + 2 * BEAT
        full = RT[0] <= t < T_FIN + 2 * BEAT and not prerace
        # funk bass (16ths)
        if (RT[0] - 2 * BEAT <= t < T_FIN + 2 * BEAT) and not prerace:
            pat = [(0, 0, 0.55), (0.75, 12, 0.3), (1.5, 0, 0.4), (2.5, 7, 0.4), (3.25, 10, 0.32), (3.5, 12, 0.3)]
            if pos == 0:
                for off, iv, d in pat:
                    if t + off * BEAT < TOTAL: ev(t + off * BEAT, "fbass", m=ro + iv, d=d * BEAT * 0.9, v=0.36 if iv == 0 else 0.28)
        if late and pos == 0: ev(t, "pad", ch=ch, d=4 * BEAT, v=0.16)
        if full or prerace:
            if pos in (1, 3) and not prerace: ev(t + BEAT / 2, "stab", ch=ch, d=0.22 * BEAT, v=0.13)
            if pos == 2 and bar % 2 == 1 and not prerace: ev(t + BEAT * 0.75, "stab", ch=ch, d=0.18 * BEAT, v=0.10)
        if full:
            ev(t, "kick", v=0.70)
            if pos in (1, 3): ev(t, "clap", v=0.36)
            ev(t + BEAT / 2, "ohat", v=0.10)
            for h in (0.25, 0.75): ev(t + h * BEAT, "hat", v=0.06)
        elif prerace:
            ev(t, "tick", v=0.30 if pos else 0.4)
        elif t < RT[0]:
            if pos in (0,) and b > 0: ev(t, "kick", v=0.5)
            ev(t + BEAT / 2, "hat", v=0.07)
    for i, t in enumerate(RT):
        r = REC[i]
        if r["sw"]:
            if REC[i - 1]["sw"]: continue
            ev(t, "glitch", v=0.40); ev(t, "crash", v=0.18)
            continue
        ev(t, VOICE[r["lane"]], m=pitch(i), v=0.52 + 0.20 * i / (N - 1))
    for k, d in enumerate([0, 7, 12, 15, 19, 24]):               # rising arpeggio on the final record (Bolt 9.58)
        ev(T_FINAL + (k + 1) * BEAT / 4, "brass", m=pitch(N - 1) - 12 + d, v=0.30)
    ifl = next(i for i, r in enumerate(REC) if r["s"] == 10.49)
    for t in (RT[ifl], RT[first_year(1960)], RT[first_year(1988.7)]):
        ev(t, "crash", v=0.20)
    ev(T_FINAL, "crash", v=0.30)
    ev(T_FINAL - 4 * BEAT, "riser", d=4 * BEAT, v=0.12)
    # the race: gun, riser into Bolt's finish, then one note per runner at the freeze
    ev(RACE0, "gun", v=0.70)
    ev(T_FIN - 3.0, "riser", d=3.0, v=0.16)
    ev(T_FIN, "boom", v=0.6); ev(T_FIN, "crash", v=0.34)
    ev(T_FIN, "brass", m=pitch(N - 1), v=0.75)
    for j, (nm, ln, s, y) in enumerate(RUN[1:]):
        ev(T_FIN + 0.5 + j * 0.5, VOICE[ln], m=SCALE[8 - 3 * j], v=0.45)
    ev(T_FIN + RACE_HOLD, "steel", m=76, v=0.4); ev(T_FIN + RACE_HOLD, "brass", m=83, v=0.35)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k in ("kick", "boom"))

# ================= drawing =================
CX0, CX1, CY0, CY1 = 34, 172, 94, 236           # chart box (art px)
Y0, Y1 = 1910, 2030
def cx(year): return CX0 + (year - Y0) / (Y1 - Y0) * (CX1 - CX0)
def cy(s, rg): lo, hi = rg; return CY0 + (s - lo) / (hi - lo) * (CY1 - CY0)    # fast (small) at the top

def sky():
    a = np.zeros((AH, AW, 3), np.uint8)
    for y in range(AH):
        f = min(1.0, y / 240); a[y, :] = tuple(int(SKY0[j] + (SKY1[j] - SKY0[j]) * f) for j in range(3))
    return Image.fromarray(a)
_SKY = sky()

def runner(d, x, y, col, ph, run=True, sc=1.0):
    """tiny side-view sprinter, feet at y, facing right. ph = stride phase (radians)"""
    s = sc
    hip = (x, y - 7 * s); sh = (x + 1.5 * s, y - 12 * s)
    lean = 1.0 if run else 0.0
    d.line([hip, sh], fill=col, width=max(1, int(2 * s)))
    d.ellipse([sh[0] + lean - 1.6 * s, sh[1] - 4.2 * s, sh[0] + lean + 1.6 * s, sh[1] - 1.0 * s], fill=(120, 80, 56))
    for k, sign in ((0, 1), (1, -1)):
        a = math.sin(ph + k * math.pi) * (0.9 if run else 0.15)
        kx, ky = hip[0] + 3.5 * s * math.sin(a), hip[1] + 3.5 * s * math.cos(a)
        fx, fy = kx + 3.5 * s * math.sin(a - 0.6 * (1 + math.sin(ph + k * math.pi + 1))), ky + 3.5 * s * math.cos(a - 0.6)
        d.line([hip, (kx, ky), (fx, min(fy, y))], fill=INK if k else col, width=1)
        aa = -a
        ex, ey = sh[0] + 2.8 * s * math.sin(aa), sh[1] + 2.8 * s * math.cos(aa)
        d.line([sh, (ex, ey), (ex + 2.2 * s * math.sin(aa + 1.2), ey - 1.5 * s)], fill=INK if k else col, width=1)

def chart(c, T):
    d = c.a; W = c.t
    rg = yrange(T); k = rec_index(T); yr = year_at(T)
    d.rectangle([CX0, CY0 - 4, CX1, CY1 + 4], fill=(250, 252, 254), outline=(200, 208, 222))
    span = rg[1] - rg[0]; stp = 0.5 if span > 2.2 else 0.2
    v = math.ceil(rg[0] / stp) * stp
    while v <= rg[1] + 1e-6:
        y = cy(v, rg)
        if CY0 - 2 <= y <= CY1 + 2:
            d.line([CX0 + 1, y, CX1 - 1, y], fill=(226, 232, 240))
            text(W, CX0 * 2 - 6, int(y * 2) - 10, f"{v:.1f}", fill=INK2, align="r")
        v += stp
    for yy in (1920, 1960, 2000):
        x = cx(yy); d.line([x, CY0 - 3, x, CY1 + 3], fill=(232, 236, 244))
        text(W, int(x * 2), int(CY1 * 2) + 10, str(yy), fill=INK2, align="c")
    text(W, CX1 * 2 - 6, int(CY0 * 2) - 2, "FASTER ^", fill=INK2, align="r")
    keep = c.art.copy()
    # playhead
    x = cx(yr); d.line([x, CY0 - 3, x, CY1 + 3], fill=(176, 188, 210))
    for ln in LANES:
        idx = [i for i in range(k + 1) if REC[i]["lane"] == ln]
        if not idx: continue
        col = LCOL[ln]; pts = []
        for j, i in enumerate(idx):
            x0 = cx(REC[i]["yf"]); y0 = cy(REC[i]["s"], rg)
            x1 = cx(REC[idx[j + 1]]["yf"]) if j + 1 < len(idx) else cx(yr)
            d.line([x0, y0, x1, y0], fill=col, width=1)
            if j + 1 < len(idx):
                y1 = cy(REC[idx[j + 1]]["s"], rg); d.line([x1, y0, x1, y1], fill=col, width=1)
        for i in idx:
            x0, y0 = cx(REC[i]["yf"]), cy(REC[i]["s"], rg)
            d.rectangle([x0 - 1, y0 - 1, x0 + 1, y0 + 1], fill=col)
        i = idx[-1]; age = T - RT[i]
        if 0 <= age < 0.5:
            x0, y0 = cx(REC[i]["yf"]), cy(REC[i]["s"], rg); rr = 2 + age * 22
            d.ellipse([x0 - rr, y0 - rr, x0 + rr, y0 + rr], outline=col if age > 0.15 else WHITE)
    # gap bracket at the playhead
    g = gap_at(k)
    if g is not None:
        a, b = REC[lane_last(k, "men")]["s"], REC[lane_last(k, "women")]["s"]
        xa = min(CX1 - 3, cx(yr) + 3); ya, yb = cy(a, rg), cy(b, rg)
        d.line([xa, ya, xa, yb], fill=GOLD); d.line([xa - 1, ya, xa + 1, ya], fill=GOLD); d.line([xa - 1, yb, xa + 1, yb], fill=GOLD)
    for box in ((0, 0, AW, CY0 - 3), (0, CY1 + 4, AW, AH), (0, 0, CX0 + 1, AH), (CX1, 0, AW, AH)):
        c.art.paste(keep.crop(box), box[:2])

def track_strip(c, T, speeds):
    """two lanes under the chart; runners at the current record pace, ground scrolls with speed"""
    d = c.a; W = c.t
    d.rectangle([0, 248, AW, 256], fill=GRASS)
    d.rectangle([0, 256, AW, 300], fill=TRACK)
    for yl in (256, 278, 300): d.line([0, yl, AW, yl], fill=WHITE)
    k = rec_index(T)
    for j, ln in enumerate(LANES):
        s = speeds.get(ln)
        base = 256 + 22 * j
        if s is None:
            text(W, 180, (base + 7) * 2, "WAITING FOR A RECORD", fill=WHITE, align="c"); continue
        v = 100 / s                                   # m/s
        off = (T * v * 9) % 24
        for xx in range(-24, AW + 24, 24):
            d.line([xx - off, base + 3, xx - off + 6, base + 3], fill=TRACK2)
            d.line([xx - off + 10, base + 17, xx - off + 13, base + 17], fill=TRACK2)
        i = lane_last(k, ln); hot = i >= 0 and 0 <= T - RT[i] < 0.6
        x = 70 + (14 * ease(1 - (T - RT[i]) / 0.6) if hot else 0)
        for q in range(3 if hot else 1):
            if hot: d.line([x - 10 - q * 6, base + 8 + q * 3, x - 4 - q * 6, base + 8 + q * 3], fill=WHITE)
        runner(d, int(x), base + 20, LCOL[ln], T * v * 1.3, True, 1.0)
        text(W, 352, (base + 6) * 2, f"{LNAME[ln]}  {kmh(s):.1f} KM/H", fill=WHITE, align="r")

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if k < 0:
        text(W, 28, 22, "100 M WORLD RECORD", fill=INK2); text(W, 28, 44, "ON YOUR MARKS", size=40, fill=INK); return
    r = REC[k]; age = T - RT[k]; col = LCOL[r["lane"]]
    if r["sw"]:
        text(W, 28, 22, "1977: ELECTRONIC TIMING ONLY", fill=INK)
        text(W, 28, 44, "9.95  ·  11.01", size=40, fill=INK if age > 0.3 else GOLD)
        text(W, 28, 92, "HAND-TIMED RECORDS RETIRED", fill=INK2)
        text(W, 334, 44, "1977", size=40, fill=GOLD, align="r")
    else:
        text(W, 28, 22, f"NEW {LNAME[r['lane']]}'S RECORD", fill=col)
        text(W, 28, 44, fmt_t(r), size=40, fill=col if age < 0.22 else INK)
        text(W, 28, 92, spd(r), fill=INK2)
        text(W, 334, 44, r["year"], size=40, fill=GOLD, align="r")
    W.rectangle([16, 128, 344, 172], fill=(250, 250, 252)); W.rectangle([16, 128, 19, 172], fill=col if not r["sw"] else GOLD)
    if r["sw"]:
        text(W, 28, 131, "MEN: HINES 9.95 (MEXICO CITY 1968)", fill=LCOL["men"])
        text(W, 28, 151, "WOMEN: RICHTER 11.01 (MONTREAL 1976)", fill=LCOL["women"])
        return
    n = int(min(60, age * 70))
    text(W, 28, 131, (r["athlete"] + " · " + r["nat"])[:max(0, n)], fill=INK)
    sub = r["venue"].upper() + ("  · " + r["note"] if r["note"] else "") + ("" if r["timing"] == "auto" else "  · HAND")
    if age > 0.12: text(W, 28, 151, sub[:40], fill=INK2 if not r["note"] else col)

def footer(c, T, k=None):
    W = c.t; k = rec_index(T) if k is None else k
    W.rectangle([0, 600, 360, 640], fill=CREAM); W.rectangle([0, 600, 360, 601], fill=INK2)
    for ln, x, al in (("men", 10, "l"), ("women", 350, "r")):
        i = lane_last(k, ln)
        text(W, x, 604, LNAME[ln], fill=LCOL[ln], align=al)
        hot = i >= 0 and 0 <= T - RT[i] < 0.3
        text(W, x, 620, f"{REC[i]['time']} S" if i >= 0 else "--", fill=LCOL[ln] if hot else INK, align=al)
    g = gap_at(k)
    text(W, 180, 604, "GAP", fill=GOLD, align="c")
    text(W, 180, 620, f"{g:.2f} S" if g is not None else "--", fill=INK, align="c")

def ifind(s, ln): return next(i for i, r in enumerate(REC) if r["s"] == s and r["lane"] == ln)
BANNERS = {ifind(13.6, "women"): ("WOMEN JOIN THE RECORDS", "3.20 S BEHIND THE MEN", True),
           ifind(10.2, "men"): ("JESSE OWENS", "10.2 HOLDS FOR 20 YEARS", False),
           ifind(10.0, "men"): ("10.0 SECONDS", "ARMIN HARY, ZURICH", False),
           ifind(9.9, "men"): ("UNDER 10 SECONDS", "FIRST TIME, BY HAND", True),
           ISW: ("STOPWATCHES OUT", "ELECTRONIC TIMING ONLY", True),
           ifind(10.79, "women") + 1: ("SAME DAY, SAME TRACK", "TWO RECORDS, ONE MEET", False),
           ifind(10.49, "women"): ("10.49!", "STILL THE RECORD TODAY", True),
           ifind(9.92, "men"): ("JOHNSON'S 9.79 ANNULLED", "DOPING. LEWIS GETS IT", False),
           ifind(9.69, "men"): ("USAIN BOLT", "BEIJING 2008", False),
           N - 1: ("9.58!", "UNBEATEN SINCE 2009", True)}
def banner(c, T):
    k = rec_index(T)
    if k not in BANNERS: return
    a = T - RT[k]
    hold = HOLD_B * BEAT if k == N - 1 else max(2 * BEAT, (GAPS_B[k] if k < N - 1 else 2) * BEAT)
    if not (0.1 < a < hold): return
    tt, sub, big = BANNERS[k]; W = c.t; yb = 352
    w = max((16 if big else 8) * len(tt) + 30, 8 * len(sub) + 30)
    hgt = 62 if big else 42
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=GOLD)
    W.rectangle([180 - w / 2, yb + hgt - 1, 180 + w / 2, yb + hgt], fill=INK2)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if a > 0.3: text(W, 180, yb + 40, sub, fill=GOLD if k != ISW else INK2, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if a > 0.3: text(W, 180, yb + 21, sub, fill=INK2, align="c")

def speeds_at(T):
    k = rec_index(T); out = {}
    for ln in LANES:
        i = lane_last(k, ln)
        if i >= 0: out[ln] = REC[i]["s"]
    return out

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _SKY.copy(); c.a = ImageDraw.Draw(c.art)
    chart(c, T); track_strip(c, T, speeds_at(T)); footer(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 26, "100 M WORLD RECORD", size=40, fill=INK)
    if t > 0.35:
        text(W, 28, 66, "MEN", size=40, fill=LCOL["men"]); text(W, 100, 66, "VS", size=40, fill=INK2)
        text(W, 150, 66, "WOMEN", size=40, fill=LCOL["women"])
    if t > 0.9: text(W, 28, 114, "EVERY NOTE = A RECORD FALLS", fill=INK2)
    if t > 1.4: text(W, 28, 140, "FASTER RECORD = HIGHER NOTE", fill=GOLD)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

# ---- the race (real time) ----
RX0, RX1 = 22, 166                                 # start / finish (art px) = 100 m
def sc_race(t):
    T = START["race"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _SKY.copy(); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    rt = max(0.0, T - RACE0); fin = T >= T_FIN; rtc = min(rt, 9.58)
    # stands + track
    d.rectangle([0, 92, AW, 120], fill=(200, 210, 226))
    rnd = random.Random(5)
    for yy in range(94, 118, 4):
        for xx in range(2, AW, 4):
            d.point((xx + rnd.randint(0, 1), yy), fill=rnd.choice([(232, 90, 90), (60, 100, 200), (240, 200, 60), (250, 250, 250), (90, 90, 110)]))
    d.rectangle([0, 120, AW, 130], fill=GRASS)
    LY = [138, 166, 194, 222]
    d.rectangle([0, 130, AW, 250], fill=TRACK)
    for j in range(5): d.line([0, 130 + 28 * j - (0 if j else 0), AW, 130 + 28 * j], fill=WHITE)
    d.rectangle([RX0, 130, RX0 + 1, 242], fill=WHITE)
    for yy in range(130, 242, 4):
        d.rectangle([RX1, yy, RX1 + 1, yy + 1], fill=INK); d.rectangle([RX1 + 2, yy + 2, RX1 + 3, yy + 3], fill=INK)
        d.rectangle([RX1, yy + 2, RX1 + 1, yy + 3], fill=WHITE); d.rectangle([RX1 + 2, yy, RX1 + 3, yy + 1], fill=WHITE)
    for m in (25, 50, 75):
        x = RX0 + (RX1 - RX0) * m / 100; d.line([x, 240, x, 243], fill=WHITE)
        text(W, int(x * 2), 492, f"{m} M", fill=WHITE, align="c")
    text(W, int(RX1 * 2), 492, "100 M", fill=WHITE, align="c")
    d.rectangle([0, 250, AW, 300], fill=GRASS)
    for j, (nm, ln, s, yr) in enumerate(RUN):
        dist = min(100.0, 100.0 * rtc / s)
        x = RX0 + (RX1 - RX0) * dist / 100
        yb = 156 + 28 * j
        lab = f"{RUN_SHORT[j]} {('%g' % s) if s != 9.58 else '9.58'} ({yr})"
        text(W, RX0 * 2 + 8, (131 + 28 * j) * 2 + 2, lab, fill=CREAM)
        runner(d, int(x), yb, LCOL[ln], rt * (100 / s) * 1.3, rt > 0 and not fin, 1.3)
        if fin and j > 0 and T - T_FIN > 0.5 + (j - 1) * 0.5:
            gap = 100.0 - dist; ft = gap / 0.3048
            text(W, int(x * 2) - 12, yb * 2 - 26, f"-{gap:.1f} M · {ft:.0f} FT", fill=WHITE, align="r")
    # HUD: race clock
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if T < RACE0:
        text(W, 28, 22, "IF THE RECORDS RACED TODAY", fill=INK2)
        text(W, 28, 44, "ON YOUR MARKS" if T < RACE0 - 2 * BEAT else "SET...", size=40, fill=INK)
        text(W, 28, 92, "EACH AT THEIR RECORD'S AVERAGE SPEED", fill=INK2)
    else:
        text(W, 28, 22, "REAL TIME" if not fin else "BOLT WINS", fill=INK2 if not fin else LCOL["men"])
        text(W, 28, 44, f"{rtc:05.2f} S", size=40, fill=INK if not fin else LCOL["men"])
        text(W, 28, 92, "AT AVERAGE SPEED (NO REACTION TIME)", fill=INK2)
    if fin and T - T_FIN > 2.0:
        W.rectangle([30, 560, 330, 596], fill=CREAM); W.rectangle([30, 560, 330, 562], fill=GOLD)
        text(W, 180, 569, "1922 VS 2009: 29.6 M APART", fill=INK, align="c")
    footer(c, T, N - 1)
    return c

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _SKY.copy(); c.a = ImageDraw.Draw(c.art)
    chart(c, T_REC_END); track_strip(c, T, {"men": 9.58, "women": 10.49}); footer(c, T, N - 1)
    W = c.t
    W.rectangle([16, 40, 344, 548], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "THE GAP", fill=INK2, align="c")
    if t > 0.3:
        text(W, 40, 82, "1922", size=40, fill=INK2); text(W, 320, 82, "3.20 S", size=40, fill=INK, align="r")
    if t > 1.0:
        text(W, 40, 132, "TODAY", size=40, fill=GOLD); text(W, 320, 132, "0.91 S", size=40, fill=INK, align="r")
    if t > 1.8:
        text(W, 180, 190, "BOLT 9.58 (2009)", fill=LCOL["men"], align="c")
        text(W, 180, 212, "GRIFFITH JOYNER 10.49 (1988)", fill=LCOL["women"], align="c")
    if t > 2.8: text(W, 180, 262, "WHICH ONE FALLS FIRST?", size=20, fill=GOLD, align="c")
    if t > 3.4:
        W.rectangle([40, 462, 320, 463], fill=INK2)
        text(W, 180, 476, "SELECTED RECORDS THAT LOWERED THE MARK.", fill=INK2, align="c")
        text(W, 180, 496, "DATA: WORLD ATHLETICS (IAAF/FSFI)", fill=INK2, align="c")
        text(W, 180, 516, "PROGRESSIONS, OLYMPICS.COM", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "mid": sc_main("mid"), "auto": sc_main("auto"),
           "race": sc_race, "outro": sc_outro}

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
    z = 1.0 + 0.012 * kp * FXK
    if name == "race" and abs(T - T_FIN) < 0.4: z += 0.03 * FXK * math.exp(-abs(T - T_FIN) / 0.12)
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if name not in ("race", "outro") and k >= 0 and 0 <= T - RT[k] < 0.10:
        fr = np.minimum(255, fr.astype(np.int16) + int(55 * FXK * (1 - (T - RT[k]) / 0.10))).astype(np.uint8)
    if name == "race" and 0 <= T - T_FIN < 0.15:
        fr = np.minimum(255, fr.astype(np.int16) + int(80 * FXK * (1 - (T - T_FIN) / 0.15))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio: stadium house / funk =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def saw(ph): return 2 * ((ph / (2 * np.pi)) % 1.0) - 1
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.0) * SR)
    L = np.zeros(n); R = np.zeros(n); fxL = np.zeros(n); fxR = np.zeros(n)
    rng = np.random.default_rng(23)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fxL, i, x * send); add(fxR, i, x * send)
    def sweep_lp(x, f0, f1, tau):
        """one-pole lowpass whose cutoff decays from f0 to f1 (filter envelope)"""
        y = np.zeros_like(x); s = 0.0; m = len(x)
        fc = f1 + (f0 - f1) * np.exp(-np.arange(m) / SR / tau)
        a = 1 - np.exp(-2 * np.pi * fc / SR)
        for i in range(m):
            s += a[i] * (x[i] - s); y[i] = s
        return y
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "stab":                                          # house chord stab: detuned saws, filter snap
            d = kw["d"]; m_ = int((d + 0.12) * SR); tt = np.arange(m_) / SR
            x = np.zeros(m_)
            for m in kw["ch"]:
                f = mtof(m + 12)
                for det in (-0.006, 0.0, 0.007): x += saw(2 * np.pi * f * (1 + det) * tt)
            x = sweep_lp(x / 12, 5200, 700, 0.05) * env(m_, 0.002, 0.25) * np.clip((d + 0.06 - tt) / 0.06, 0, 1)
            put(t, x * v * 1.3, pan=0.15, send=0.18)
        elif k == "pad":
            d = kw["d"]; m_ = int((d + 0.5) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / 0.5) * np.clip((d + 0.4 - tt) / 0.4, 0, 1); x = np.zeros(m_)
            for j, m in enumerate(kw["ch"]):
                f = mtof(m); x += (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 1.004 * tt))
            put(t, x * e * v * 0.18, send=0.3)
        elif k == "fbass":                                       # funk synth bass: saw + filter envelope + drive
            d = kw["d"]; m_ = int((d + 0.05) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = 0.7 * saw(2 * np.pi * f * tt) + 0.6 * np.sin(2 * np.pi * f * tt)
            x = sweep_lp(x, 1800, 260, 0.04)
            x = np.tanh(2.2 * x) * env(m_, 0.003, 0.4) * np.clip((d + 0.02 - tt) / 0.03, 0, 1)
            put(t, x * v * 0.85)
        elif k in ("kick", "boom"):
            m_ = int((0.32 if k == "kick" else 1.2) * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum((50 if k == "kick" else 38) + 130 * np.exp(-tt / 0.03)) / SR
            x = np.sin(ph) * env(m_, 0.001, 0.12 if k == "kick" else 0.45)
            x[: int(0.003 * SR)] += rng.standard_normal(int(0.003 * SR)) * 0.3
            put(t, np.tanh(1.5 * x) * v)
        elif k == "clap":
            m_ = int(0.25 * SR); b, a = butter(2, [900 / (SR / 2), 6000 / (SR / 2)], "band")
            nz = lfilter(b, a, rng.standard_normal(m_)); e = np.zeros(m_)
            for o in (0, 0.009, 0.019): e += env(m_, 0.0005, 0.006 if o < 0.019 else 0.07) * (np.arange(m_) >= int(o * SR))
            put(t, nz * e * v * 1.3, send=0.25)
        elif k in ("hat", "ohat", "tick"):
            m_ = int((0.05 if k != "ohat" else 0.22) * SR); b, a = butter(2, (8500 if k != "tick" else 5000) / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.001, 0.014 if k != "ohat" else 0.07) * v,
                pan=-0.3 if k == "ohat" else 0.3)
        elif k == "brass":                                       # men: bright brass stab (saw ensemble, filter swell)
            m_ = int(0.9 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"]); x = np.zeros(m_)
            for det in (-0.008, -0.003, 0.003, 0.009): x += saw(2 * np.pi * f * (1 + det) * tt + det * 40)
            x = x / 4
            fc_env = sweep_lp(x, 6500, 1400, 0.09)
            x = fc_env * np.minimum(1, tt / 0.012) * np.exp(-tt / 0.35)
            put(t, x * v * 1.5, pan=-0.2, send=0.22)
            put(t + BEAT * 0.75, x * v * 0.16, pan=0.35)
        elif k == "steel":                                       # women: steel drum
            m_ = int(1.4 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"]) * (1 + 0.012 * np.exp(-tt / 0.02))
            ph = 2 * np.pi * np.cumsum(f) / SR
            x = (np.sin(ph) * np.exp(-tt / 0.55) + 0.55 * np.sin(2 * ph) * np.exp(-tt / 0.3)
                 + 0.25 * np.sin(3.01 * ph) * np.exp(-tt / 0.12) + 0.15 * np.sin(4.2 * ph) * np.exp(-tt / 0.05))
            x *= np.minimum(1, tt / 0.002)
            put(t, x * v * 0.55, pan=0.25, send=0.25)
            put(t + BEAT * 0.5, x * v * 0.13, pan=-0.35)
        elif k == "glitch":                                      # 1977 rule change: stutter + pitch dive
            m_ = int(0.9 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(880 * np.exp(-tt / 0.25)) / SR
            x = np.sign(np.sin(ph)) * (np.floor(tt * 24) % 2) * np.exp(-tt / 0.4)
            b, a = butter(2, 3500 / (SR / 2)); put(t, lfilter(b, a, x) * v * 0.35, send=0.2)
        elif k == "gun":                                         # starting pistol: crack + tail
            m_ = int(0.9 * SR); tt = np.arange(m_) / SR
            b, a = butter(2, 1500 / (SR / 2), "high")
            x = lfilter(b, a, rng.standard_normal(m_)) * (env(m_, 0.0003, 0.012) + 0.15 * env(m_, 0.002, 0.25))
            put(t, x * v, send=0.45)
        elif k == "crash":
            m_ = int(2.0 * SR); b, a = butter(2, 5000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.002, 0.55) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR; b, a = butter(2, 2500 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    def reverb(x):
        out = np.zeros_like(x)
        for dl, g in ((1557, 0.74), (1617, 0.73), (1491, 0.75), (1422, 0.74)):
            y = x.copy()
            for i in range(dl, len(y), dl): y[i:i + dl] += g * y[i - dl:i][:len(y[i:i + dl])]
            out += y * 0.25
        return out
    b, a = butter(1, 5000 / (SR / 2))
    L += lfilter(b, a, reverb(fxL)) * 0.28; R += lfilter(b, a, reverb(np.roll(fxR, 300))) * 0.28
    b, a = butter(2, 13000 / (SR / 2)); L = lfilter(b, a, L); R = lfilter(b, a, R)
    tt = np.arange(n) / SR; duck = np.ones(n)
    for kt in KICKS:                                             # house sidechain pump
        i0 = int(kt * SR); i1 = min(n, i0 + int(0.3 * SR))
        if i0 < n: duck[i0:i1] = np.minimum(duck[i0:i1], 1 - 0.35 * np.exp(-np.arange(i1 - i0) / SR / 0.09))
    L *= duck; R *= duck
    fade = np.clip((TOTAL - tt) / 1.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.tanh(np.stack([L, R], 1) / mx * 1.25) / np.tanh(1.25) * 0.9
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
        print([(REC[i]["year"], REC[i]["lane"][0], REC[i]["time"], round(t, 2), pitch(i)) for i, t in enumerate(RT)])
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
