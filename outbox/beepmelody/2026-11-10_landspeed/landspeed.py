"""BEEPMELODY — FROM 63 KM/H TO MACH 1. Every land speed record that raised the absolute mark, 1898 -> 1997,
three lanes like 'the race to the sky': electric + steam / piston engine / jet + rocket.
Every note = a new record in its lane; faster = higher note (log of the speed).
Climax: 1 km in real time between ThrustSSC (1997), Blue Bird (1935), La Jamais Contente (1899) and Jeantaud (1898).
Guillaume 2026-11-10 (co-pilot): 'plus dynamique, beep agressif, high tempo' -> 172 BPM breakbeat chiptune:
driven square/pulse beeps with a pitch rev, reese bass, two-step kick, snare on 2 and 4, sonic boom at Mach 1.
Data: landspeed.csv (2 sources per row; FIA + Guinness for the final record).

    python3 landspeed.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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
REC = list(csv.DictReader(open(os.path.join(HERE, "landspeed.csv"))))
def yfrac(d):
    y, m, dd = (int(x) for x in d.split("-")); return y + (m - 1) / 12 + (dd - 1) / 365
for r in REC:
    r["k"] = float(r["kmh"]); r["m"] = float(r["mph"]); r["year"] = r["date"][:4]; r["yf"] = yfrac(r["date"])
N = len(REC)
LANES = ["electric", "piston", "jet"]
LNAME = {"electric": "ELECTRIC + STEAM", "piston": "PISTON ENGINE", "jet": "JET + ROCKET"}
LSHORT = {"electric": "ELEC/STEAM", "piston": "PISTON", "jet": "JET/ROCKET"}
def ik(v): return f"{int(v):,}"                                  # floor, thousands comma
def fk(r): return f"{ik(r['k'])} KM/H"
def fm(r): return f"{ik(r['m'])} MPH"

# ================= palette (clear salt-flat day) =================
INK = (34, 36, 58)
INK2 = (100, 102, 128)
CREAM = (252, 249, 240)
WHITE = (255, 255, 255)
GOLD = (226, 150, 20)
LCOL = {"electric": (24, 150, 128), "piston": (222, 104, 28), "jet": (210, 40, 70)}
SKY0, SKY1 = (198, 226, 248), (248, 246, 238)
SALT = (238, 232, 216)
SALT2 = (222, 214, 194)
MOUNT = (176, 168, 186)

# ================= timeline (on the beat) =================
BPM = 172.0
BEAT = 60.0 / BPM
INTRO_B = 8
def gap_beats(i):
    a, b = REC[i - 1], REC[i]
    dy = b["yf"] - a["yf"]
    if dy < 0.04: return 1
    if dy <= 2.5: return 2
    if dy <= 8: return 3
    return 8                                                    # 13-16 years without a record
GAPS_B = [gap_beats(i) for i in range(1, N)]
HOLD_B = 10
RT = [INTRO_B * BEAT]
for g in GAPS_B: RT.append(RT[-1] + g * BEAT)
T_FINAL = RT[-1]
T_REC_END = T_FINAL + HOLD_B * BEAT
PRE_B = 4
RACE0 = T_REC_END + PRE_B * BEAT
RUN = [("THRUSTSSC", "jet", 1227.985, "1997"), ("BLUE BIRD", "piston", 484.62, "1935"),
       ("JAMAIS CONTENTE", "electric", 105.88, "1899"), ("JEANTAUD", "electric", 63.15, "1898")]
T_FIN = RACE0 + 1000 / (1227.985 / 3.6)                       # 2.93 s for 1 km
RACE_HOLD = 4.8
OUTRO_D = 16 * BEAT
def first_year(y): return next(i for i, r in enumerate(REC) if r["yf"] >= y)
I1922, I1963 = first_year(1922), first_year(1963)
SC = [("intro", RT[0]), ("early", RT[I1922] - RT[0]), ("mid", RT[I1963] - RT[I1922]), ("jet", T_REC_END - RT[I1963]),
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
def year_at(T):
    if T < RT[0]: return 1896 + 2.8 * T / RT[0]
    k = rec_index(T)
    if k >= N - 1: return lerp(REC[-1]["yf"], 2000.0, ease((T - RT[-1]) / (HOLD_B * BEAT * 0.8)))
    t0, t1 = RT[k], RT[k + 1]
    return lerp(REC[k]["yf"], REC[k + 1]["yf"], (T - t0) / max(1e-6, t1 - t0))

# ================= music plan (shared by picture + audio) =================
SCALE = [62, 65, 67, 69, 72, 74, 77, 79, 81, 84, 86, 89, 91, 93, 96]   # D minor pentatonic from D4
LK0, LK1 = math.log(60), math.log(1230)
def pitch(i):
    f = (math.log(REC[i]["k"]) - LK0) / (LK1 - LK0)
    return SCALE[min(len(SCALE) - 1, int(round(f * (len(SCALE) - 1))))]
CHORDS = [(50, 57, 62), (46, 53, 58), (48, 55, 60), (45, 52, 57)]     # D5 Bb5 C5 A5 power chords
ROOTS = [38, 34, 36, 33]
VOICE = {"electric": "zap", "piston": "rev", "jet": "jetl"}
def long_gap(i): return i < N - 1 and GAPS_B[i] >= 8
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT)) + 1
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        ch = CHORDS[bar % 4]; ro = ROOTS[bar % 4]
        k = rec_index(t + 1e-6)
        quiet = k >= 0 and long_gap(k) and t >= RT[k] + 2 * BEAT       # long gaps: drums thin out
        prerace = T_REC_END <= t < RACE0
        racing = RACE0 <= t < T_FIN + 2 * BEAT
        full = RT[0] <= t < T_REC_END and not quiet
        late = t >= T_FIN + 2 * BEAT
        if full or racing:
            # two-step breakbeat: kick 1 + 'and' of 3, snare 2 + 4, 16th hats
            if pos == 0: ev(t, "kick", v=0.72)
            if pos == 2: ev(t + BEAT / 2, "kick", v=0.62)
            if pos in (1, 3): ev(t, "snare", v=0.42)
            if pos == 3 and bar % 2 == 1: ev(t + BEAT * 0.75, "snare", v=0.16)
            for h in (0, 0.25, 0.5, 0.75): ev(t + h * BEAT, "hat", v=0.07 if h else 0.09)
            # reese bass, 8ths
            for h in (0, 0.5):
                ev(t + h * BEAT, "reese", m=ro + (12 if (pos == 3 and h) else 0), d=BEAT * 0.48, v=0.34)
            if pos in (1, 3): ev(t + BEAT / 2, "stab", ch=ch, d=0.22 * BEAT, v=0.12)
        elif quiet:
            if pos == 0: ev(t, "reese", m=ro, d=BEAT * 3.6, v=0.22)
            ev(t + BEAT / 2, "hat", v=0.06)
            if pos == 0 and bar % 2 == 0: ev(t, "pad", ch=ch, d=4 * BEAT, v=0.14)
        elif prerace:
            ev(t, "tick", v=0.30 if pos else 0.42)
            if pos == 0: ev(t, "reese", m=ro, d=BEAT * 3.6, v=0.22)
        elif t < RT[0]:
            if pos == 0: ev(t, "kick", v=0.55)
            if pos == 2: ev(t + BEAT / 2, "kick", v=0.45)
            ev(t + BEAT / 2, "hat", v=0.07)
            if b >= INTRO_B - 4: ev(t, "hat", v=0.06); ev(t + BEAT / 4, "hat", v=0.05); ev(t + 3 * BEAT / 4, "hat", v=0.05)
        elif late and pos == 0:
            ev(t, "pad", ch=ch, d=4 * BEAT, v=0.16)
    for i, t in enumerate(RT):
        r = REC[i]
        ev(t, VOICE[r["lane"]], m=pitch(i), v=0.50 + 0.18 * i / (N - 1))
        if i < N - 1 and GAPS_B[i] >= 2:                         # aggressive double beep: bi-BIP up a step
            up = SCALE[min(len(SCALE) - 1, SCALE.index(pitch(i)) + 1 + (i % 2))]
            ev(t + BEAT / 4, VOICE[r["lane"]], m=up, v=0.36 + 0.12 * i / (N - 1))
    ev(RT[0] - 4 * BEAT, "riser", d=4 * BEAT, v=0.10)
    for i in range(N - 1):
        if long_gap(i): ev(RT[i + 1] - 2 * BEAT, "riser", d=2 * BEAT, v=0.12); ev(RT[i + 1], "crash", v=0.26)
    for k, d in enumerate([0, 7, 12, 15, 19, 24]):               # rising arpeggio on the final record
        ev(T_FINAL + (k + 1) * BEAT / 4, "jetl", m=pitch(N - 1) - 24 + d, v=0.28)
    for i, r in enumerate(REC):
        if r["note"].startswith("FIRST OVER") or r["note"] == "FIRST JET": ev(RT[i], "crash", v=0.20)
    ev(T_FINAL - 4 * BEAT, "riser", d=4 * BEAT, v=0.14)
    ev(T_FINAL, "sboom", v=0.75); ev(T_FINAL, "crash", v=0.32)
    # the race: 1 km, real time
    ev(RACE0, "flag", v=0.6)
    ev(RACE0, "whoosh", d=T_FIN - RACE0, v=0.5)
    ev(T_FIN, "sboom", v=0.8); ev(T_FIN, "crash", v=0.34)
    for j, (nm, ln, s, y) in enumerate(RUN[1:]):
        ev(T_FIN + 0.6 + j * 0.5, VOICE[ln], m=SCALE[9 - 3 * j], v=0.45)
    ev(T_FIN + RACE_HOLD, "jetl", m=74, v=0.35); ev(T_FIN + RACE_HOLD, "zap", m=86, v=0.3)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k in ("kick", "sboom"))

# ================= drawing =================
CX0, CX1, CY0, CY1 = 36, 172, 94, 232           # chart box (art px)
Y0, Y1 = 1895, 2001
YK0, YK1 = 50, 1500                             # km/h, log
def cx(year): return CX0 + (year - Y0) / (Y1 - Y0) * (CX1 - CX0)
def cy(k): return CY1 - (math.log(k) - math.log(YK0)) / (math.log(YK1) - math.log(YK0)) * (CY1 - CY0)

def sky():
    a = np.zeros((AH, AW, 3), np.uint8)
    for y in range(AH):
        f = min(1.0, y / 240); a[y, :] = tuple(int(SKY0[j] + (SKY1[j] - SKY0[j]) * f) for j in range(3))
    return Image.fromarray(a)
_SKY = sky()

def car(d, x, y, ln, sc=1.0, flame=0.0):
    """tiny side-view record car facing right, wheels on y"""
    col = LCOL[ln]; s = sc
    if ln == "electric":                         # boxy carriage, big wheels
        d.rectangle([x - 7 * s, y - 8 * s, x + 4 * s, y - 3 * s], fill=col)
        d.rectangle([x - 5 * s, y - 11 * s, x - 1 * s, y - 8 * s], fill=INK)
        for wx in (x - 5 * s, x + 2 * s): d.ellipse([wx - 2.5 * s, y - 5 * s, wx + 2.5 * s, y], fill=INK)
    elif ln == "piston":                         # long cigar body, exposed wheels
        d.polygon([(x - 10 * s, y - 3 * s), (x - 9 * s, y - 7 * s), (x + 6 * s, y - 6 * s), (x + 10 * s, y - 3 * s)], fill=col)
        d.rectangle([x - 3 * s, y - 9 * s, x, y - 7 * s], fill=INK)
        for wx in (x - 6 * s, x + 6 * s): d.ellipse([wx - 2.2 * s, y - 4.4 * s, wx + 2.2 * s, y], fill=INK)
    else:                                        # needle with fin + flame
        d.polygon([(x - 12 * s, y - 2 * s), (x - 11 * s, y - 6 * s), (x + 4 * s, y - 5 * s), (x + 13 * s, y - 2 * s)], fill=col)
        d.polygon([(x - 12 * s, y - 6 * s), (x - 10 * s, y - 11 * s), (x - 7 * s, y - 6 * s)], fill=col)
        d.rectangle([x - 1 * s, y - 7 * s, x + 2 * s, y - 5 * s], fill=INK)
        for wx in (x - 7 * s, x + 7 * s): d.ellipse([wx - 1.6 * s, y - 3.2 * s, wx + 1.6 * s, y], fill=INK)
        if flame > 0:
            L = (4 + 4 * flame) * s
            d.polygon([(x - 12 * s, y - 5 * s), (x - 12 * s - L, y - 3.5 * s), (x - 12 * s, y - 2 * s)], fill=(255, 196, 60))

def chart(c, T):
    d = c.a; W = c.t
    k = rec_index(T); yr = year_at(T)
    d.rectangle([CX0, CY0 - 4, CX1, CY1 + 4], fill=(250, 252, 254), outline=(200, 208, 222))
    for v in (100, 200, 500, 1000):
        y = cy(v); d.line([CX0 + 1, y, CX1 - 1, y], fill=(226, 232, 240))
        text(W, CX0 * 2 - 6, int(y * 2) - 10, f"{v:,}" if v < 1000 else "1K", fill=INK2, align="r")
    for yy in (1900, 1925, 1950, 1975, 2000):
        x = cx(yy); d.line([x, CY0 - 3, x, CY1 + 3], fill=(232, 236, 244))
        text(W, int(x * 2), int(CY1 * 2) + 10, str(yy), fill=INK2, align="c")
    text(W, CX0 * 2 + 6, int(CY0 * 2) - 2, "KM/H (LOG) · FASTER ^", fill=INK2)
    keep = c.art.copy()
    x = cx(yr); d.line([x, CY0 - 3, x, CY1 + 3], fill=(176, 188, 210))
    # overall record staircase (thin, grey) + lane dots
    idx = list(range(k + 1))
    for j, i in enumerate(idx):
        x0 = cx(REC[i]["yf"]); y0 = cy(REC[i]["k"])
        x1 = cx(REC[i + 1]["yf"]) if j + 1 < len(idx) else cx(yr)
        col = LCOL[REC[i]["lane"]]
        d.line([x0, y0, x1, y0], fill=col, width=1)
        if j + 1 < len(idx): d.line([x1, y0, x1, cy(REC[i + 1]["k"])], fill=col, width=1)
    for i in idx:
        x0, y0 = cx(REC[i]["yf"]), cy(REC[i]["k"])
        d.rectangle([x0 - 1, y0 - 1, x0 + 1, y0 + 1], fill=LCOL[REC[i]["lane"]])
    if k >= 0:
        age = T - RT[k]
        if 0 <= age < 0.45:
            x0, y0 = cx(REC[k]["yf"]), cy(REC[k]["k"]); rr = 2 + age * 26
            d.ellipse([x0 - rr, y0 - rr, x0 + rr, y0 + rr], outline=LCOL[REC[k]["lane"]] if age > 0.12 else WHITE)
    for box in ((0, 0, AW, CY0 - 3), (0, CY1 + 4, AW, AH), (0, 0, CX0 + 1, AH), (CX1, 0, AW, AH)):
        c.art.paste(keep.crop(box), box[:2])

LANE_Y = {"electric": 262, "piston": 278, "jet": 294}
def strip(c, T, speeds):
    """three lanes on the salt flat; each car at its lane's record, ground scrolls with log(speed)"""
    d = c.a; W = c.t
    d.rectangle([0, 242, AW, 248], fill=MOUNT)
    d.rectangle([0, 248, AW, 300], fill=SALT)
    for yl in (264, 280): d.line([0, yl, AW, yl], fill=SALT2)
    k = rec_index(T)
    for ln in LANES:
        s = speeds.get(ln); base = LANE_Y[ln]
        if s is None:
            text(W, 180, (base - 12) * 2, LNAME[ln] + ": NOT YET", fill=INK2, align="c"); continue
        v = 6 + 26 * (math.log(s) - math.log(50)) / (math.log(1300) - math.log(50))
        off = (T * v * 6) % 30
        for xx in range(-30, AW + 30, 30):
            d.line([xx - off, base - 1, xx - off + 8, base - 1], fill=SALT2)
        i = lane_last(k, ln); hot = i >= 0 and 0 <= T - RT[i] < 0.6
        x = 60 + (16 * ease(1 - (T - RT[i]) / 0.6) if hot else 0)
        if hot:
            for q in range(3): d.line([x - 16 - q * 7, base - 4 - q * 2, x - 10 - q * 7, base - 4 - q * 2], fill=LCOL[ln])
        car(d, int(x), base, ln, 1.0, flame=0.6 + 0.4 * math.sin(T * 40))
        text(W, 352, (base - 13) * 2, f"{LSHORT[ln]}  {ik(s)} KM/H", fill=LCOL[ln], align="r")

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    r = REC[k]; age = T - RT[k]; col = LCOL[r["lane"]]
    text(W, 28, 22, f"NEW RECORD · {LNAME[r['lane']]}", fill=col)
    text(W, 28, 44, fk(r), size=40, fill=col if age < 0.22 else INK)
    text(W, 28, 92, fm(r), fill=INK2)
    text(W, 334, 44, r["year"], size=40, fill=GOLD, align="r")
    W.rectangle([16, 128, 344, 172], fill=(250, 250, 252)); W.rectangle([16, 128, 19, 172], fill=col)
    n = int(min(60, age * 80))
    who = r["driver"] + " · " + r["car"]
    if len(who) > 39: who = r["driver"].split()[-1] + " · " + r["car"]
    text(W, 28, 131, who[:min(n, 39)], fill=INK)
    sub = r["place"] + ("  · " + r["note"] if r["note"] else "")
    if age > 0.12: text(W, 28, 151, sub[:40], fill=INK2 if not r["note"] else col)

def footer(c, T, k=None):
    W = c.t; k = rec_index(T) if k is None else k
    W.rectangle([0, 600, 360, 640], fill=CREAM); W.rectangle([0, 600, 360, 601], fill=INK2)
    text(W, 10, 604, "1898", fill=INK2); text(W, 10, 620, "63 KM/H", fill=INK)
    text(W, 180, 604, "TODAY VS 1898", fill=GOLD, align="c")
    ratio = REC[k]["k"] / REC[0]["k"] if k >= 0 else 1.0
    text(W, 180, 620, f"{ratio:.1f}X FASTER" if k > 0 else "--", fill=INK, align="c")
    if k >= 0:
        hot = 0 <= T - RT[k] < 0.3
        text(W, 350, 604, "RECORD", fill=INK2, align="r")
        text(W, 350, 620, fk(REC[k]), fill=LCOL[REC[k]["lane"]] if hot else INK, align="r")

def iat(d): return next(i for i, r in enumerate(REC) if r["date"] == d)
BANNERS = {iat("1899-04-29"): ("100 KM/H!", "AN ELECTRIC CAR, 1899", True),
           iat("1902-04-13"): ("STEAM TAKES THE LEAD", "SERPOLLET, NICE", False),
           iat("1902-08-05"): ("PETROL ARRIVES", "VANDERBILT, MORS Z", False),
           iat("1904-07-21"): ("100 MPH", "RIGOLLY, OSTEND", True),
           iat("1906-01-26"): ("A STEAM CAR!", "205 KM/H · 127 MPH", True),
           iat("1927-03-29"): ("200 MPH", "SEGRAVE, DAYTONA BEACH", True),
           iat("1935-03-07"): ("LAST RECORD ON A BEACH", "DAYTONA, 1935", False),
           iat("1935-09-03"): ("300 MPH", "BONNEVILLE SALT FLATS", True),
           iat("1947-09-16"): ("394 MPH", "LAST PISTON RECORD", False),
           iat("1963-08-05"): ("JETS ARRIVE", "BREEDLOVE, 407 MPH", True),
           iat("1964-10-27"): ("5 RECORDS IN 25 DAYS", "BONNEVILLE, OCTOBER 1964", False),
           iat("1965-11-15"): ("600 MPH", "BREEDLOVE, SONIC 1", True),
           iat("1970-10-23"): ("1,000 KM/H", "A ROCKET: BLUE FLAME", True),
           N - 1: ("MACH 1.02", "FASTER THAN SOUND", True)}
def banner(c, T):
    k = rec_index(T)
    if k < 0: return
    a = T - RT[k]; W = c.t
    gap = (GAPS_B[k] if k < N - 1 else HOLD_B) * BEAT
    if long_gap(k) and a > min(3 * BEAT, gap * 0.4):
        yrs = int(REC[k + 1]["year"]) - int(REC[k]["year"])
        tt, sub, big = f"{yrs} YEARS", "NO NEW RECORD", True
    elif k in BANNERS:
        hold = HOLD_B * BEAT if k == N - 1 else (min(3 * BEAT, gap * 0.4) if long_gap(k) else max(2 * BEAT, gap))
        if not (0.08 < a < hold): return
        tt, sub, big = BANNERS[k]
    else:
        return
    w = max((16 if big else 8) * len(tt) + 30, 8 * len(sub) + 30)
    hgt = 62 if big else 42
    x1 = CX1 * 2 - 6; x0 = x1 - w; xc = (x0 + x1) / 2          # bottom-right of the chart: always empty (late years, low speeds)
    yb = CY1 * 2 - 8 - hgt
    W.rectangle([x0, yb, x1, yb + hgt], fill=CREAM)
    W.rectangle([x0, yb, x1, yb + 2], fill=GOLD)
    W.rectangle([x0, yb + hgt - 1, x1, yb + hgt], fill=INK2)
    if big:
        text(W, xc, yb + 4, tt, size=40, fill=INK, align="c")
        if a > 0.25: text(W, xc, yb + 40, sub, fill=GOLD, align="c")
    else:
        text(W, xc, yb + 3, tt, fill=INK, align="c")
        if a > 0.25: text(W, xc, yb + 21, sub, fill=INK2, align="c")

def speeds_at(T):
    k = rec_index(T); out = {}
    for ln in LANES:
        i = lane_last(k, ln)
        if i >= 0: out[ln] = REC[i]["k"]
    return out

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _SKY.copy(); c.a = ImageDraw.Draw(c.art)
    chart(c, T); strip(c, T, speeds_at(T)); footer(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 26, "LAND SPEED RECORD", size=40, fill=INK)
    if t > 0.3:
        text(W, 28, 66, "63 KM/H", size=40, fill=LCOL["electric"]); text(W, 156, 66, "TO", size=40, fill=INK2)
        text(W, 204, 66, "MACH 1", size=40, fill=LCOL["jet"])
    if t > 0.8: text(W, 28, 114, "EVERY BEEP = A NEW RECORD", fill=INK2)
    if t > 1.3: text(W, 28, 140, "FASTER = HIGHER NOTE", fill=GOLD)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

# ---- the race: 1 km in real time ----
RX0, RX1 = 22, 166
def sc_race(t):
    T = START["race"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _SKY.copy(); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    rt = max(0.0, T - RACE0); fin = T >= T_FIN; rtc = min(rt, T_FIN - RACE0)
    for xx in range(0, AW, 1):                                   # far mountains
        h = 8 + 6 * math.sin(xx * 0.07) + 4 * math.sin(xx * 0.19 + 1)
        d.line([xx, 126 - h, xx, 126], fill=MOUNT)
    d.rectangle([0, 126, AW, 250], fill=SALT)
    for j in range(5): d.line([0, 130 + 28 * j, AW, 130 + 28 * j], fill=SALT2)
    d.rectangle([RX0, 130, RX0 + 1, 242], fill=INK2)
    for yy in range(130, 242, 4):
        d.rectangle([RX1, yy, RX1 + 1, yy + 1], fill=INK); d.rectangle([RX1 + 2, yy + 2, RX1 + 3, yy + 3], fill=INK)
        d.rectangle([RX1, yy + 2, RX1 + 1, yy + 3], fill=WHITE); d.rectangle([RX1 + 2, yy, RX1 + 3, yy + 1], fill=WHITE)
    for m in (250, 500, 750):
        x = RX0 + (RX1 - RX0) * m / 1000; d.line([x, 240, x, 243], fill=INK2)
        text(W, int(x * 2), 492, f"{m} M", fill=INK2, align="c")
    text(W, int(RX1 * 2), 492, "1 KM", fill=INK, align="c")
    d.rectangle([0, 250, AW, 300], fill=SALT2)
    for j, (nm, ln, s, yr) in enumerate(RUN):
        v = s / 3.6; dist = min(1000.0, v * rtc)
        x = RX0 + (RX1 - RX0) * dist / 1000
        yb = 154 + 28 * j
        lab = f"{nm} {ik(s)} KM/H ({yr})"
        text(W, RX0 * 2 + 8, (131 + 28 * j) * 2 + 2, lab, fill=LCOL[ln])
        if rt > 0 and not fin and ln == "jet":
            for q in range(4): d.line([x - 20 - q * 10, yb - 3 - q, x - 14 - q * 10, yb - 3 - q], fill=SALT2)
        car(d, int(x), yb, ln, 1.25, flame=1.0 if (rt > 0 and not fin) else 0.0)
        if fin and j > 0 and T - T_FIN > 0.6 + (j - 1) * 0.5:
            gap = 1000.0 - dist; ft = gap / 0.3048
            text(W, int(x * 2) + 34, yb * 2 - 30, f"-{ik(gap)} M · {ik(ft)} FT", fill=INK, align="l")
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if T < RACE0:
        text(W, 28, 22, "IF THE RECORDS RACED TODAY", fill=INK2)
        text(W, 28, 44, "1 KILOMETRE" if T < RACE0 - 2 * BEAT else "READY...", size=40, fill=INK)
        text(W, 28, 92, "EACH AT ITS RECORD SPEED", fill=INK2)
    else:
        text(W, 28, 22, "REAL TIME" if not fin else "THRUSTSSC: 1 KM", fill=INK2 if not fin else LCOL["jet"])
        text(W, 28, 44, f"{rtc:.2f} S", size=40, fill=INK if not fin else LCOL["jet"])
        text(W, 28, 92, "AT RECORD SPEED, FLYING START", fill=INK2)
    if fin and T - T_FIN > 2.2:
        W.rectangle([30, 560, 330, 596], fill=CREAM); W.rectangle([30, 560, 330, 562], fill=GOLD)
        text(W, 180, 569, "1898 VS 1997: 19.4X FASTER", fill=INK, align="c")
    footer(c, T, N - 1)
    return c

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _SKY.copy(); c.a = ImageDraw.Draw(c.art)
    chart(c, T_REC_END); strip(c, T, speeds_at(T_REC_END)); footer(c, T, N - 1)
    W = c.t
    W.rectangle([0, 0, 360, 600], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "99 YEARS · 57 RECORDS", fill=INK2, align="c")
    if t > 0.3:
        text(W, 40, 82, "1898", size=40, fill=LCOL["electric"]); text(W, 320, 82, "63 KM/H", size=40, fill=INK, align="r")
    if t > 0.9:
        text(W, 40, 132, "1997", size=40, fill=LCOL["jet"]); text(W, 320, 132, "1,227 KM/H", size=40, fill=INK, align="r")
    if t > 1.5:
        text(W, 180, 190, "39 MPH -> 763 MPH", fill=INK2, align="c")
        text(W, 180, 212, "STILL THE RECORD TODAY", fill=GOLD, align="c")
    if t > 2.0:
        text(W, 180, 262, "ANDY GREEN · THRUSTSSC", fill=LCOL["jet"], align="c")
        text(W, 180, 284, "BLACK ROCK DESERT, 15 OCT 1997", fill=INK2, align="c")
        text(W, 180, 306, "MACH 1.02: FASTER THAN SOUND", fill=INK2, align="c")
    if t > 2.8: text(W, 180, 360, "WHO BREAKS IT NEXT?", size=40, fill=GOLD, align="c")
    if t > 3.0:
        W.rectangle([40, 462, 320, 463], fill=INK2)
        text(W, 180, 476, "RECORDS THAT RAISED THE ABSOLUTE MARK.", fill=INK2, align="c")
        text(W, 180, 496, "DATA: FIA, GUINNESS WORLD RECORDS,", fill=INK2, align="c")
        text(W, 180, 516, "ACF/AIACR HISTORICAL LISTS", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "mid": sc_main("mid"), "jet": sc_main("jet"),
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
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    z = 1.0 + 0.014 * kp * FXK
    for tb in (T_FINAL, T_FIN):
        if abs(T - tb) < 0.4: z += 0.035 * FXK * math.exp(-abs(T - tb) / 0.12)
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if name not in ("race", "outro") and k >= 0 and 0 <= T - RT[k] < 0.09:
        fr = np.minimum(255, fr.astype(np.int16) + int(55 * FXK * (1 - (T - RT[k]) / 0.09))).astype(np.uint8)
    for tb, dd in ((T_FINAL, 0.18), (T_FIN, 0.15)):
        if 0 <= T - tb < dd:
            fr = np.minimum(255, fr.astype(np.int16) + int(90 * FXK * (1 - (T - tb) / dd))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio: 172 BPM breakbeat chiptune, aggressive beeps =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def saw(ph): return 2 * ((ph / (2 * np.pi)) % 1.0) - 1
def pulse(ph, duty): return np.where((ph / (2 * np.pi)) % 1.0 < duty, 1.0, -1.0)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.0) * SR)
    L = np.zeros(n); R = np.zeros(n); fxL = np.zeros(n); fxR = np.zeros(n)
    rng = np.random.default_rng(31)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fxL, i, x * send); add(fxR, i, x * send)
    lp6 = butter(2, 6500 / (SR / 2))
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k in ("zap", "rev", "jetl"):
            m_ = int(0.42 * SR); tt = np.arange(m_) / SR; f0 = mtof(kw["m"])
            if k == "zap":                                       # electric: thin pulse, pitch flick down
                f = f0 * (1 + 0.5 * np.exp(-tt / 0.012)); ph = 2 * np.pi * np.cumsum(f) / SR
                x = pulse(ph, 0.125) * 0.8 + 0.3 * pulse(ph * 2, 0.25)
                e = env(m_, 0.001, 0.12)
            elif k == "rev":                                     # piston: driven square revving up into the note
                f = f0 * 2 ** ((-4 * np.exp(-tt / 0.025)) / 12); ph = 2 * np.pi * np.cumsum(f) / SR
                x = np.tanh(3.0 * (pulse(ph, 0.25) * 0.7 + 0.5 * saw(ph * 1.005)))
                e = env(m_, 0.002, 0.16)
            else:                                                # jet/rocket: detuned saws + square, octave glide
                f = f0 * 2 ** ((-7 * np.exp(-tt / 0.03)) / 12); ph = 2 * np.pi * np.cumsum(f) / SR
                x = sum(saw(ph * (1 + dt)) for dt in (-0.01, 0, 0.011)) / 2 + 0.5 * pulse(ph * 0.5, 0.5)
                x = np.tanh(2.2 * x); e = env(m_, 0.002, 0.2)
                nz = lfilter(*butter(2, 3000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.004, 0.06) * 0.25
                x = x + nz
            x = lfilter(*lp6, x * e)
            put(t, x * v * 0.62, pan=-0.15 if k == "rev" else (0.2 if k == "zap" else 0.0), send=0.12)
            put(t + BEAT * 0.75, x * v * 0.14, pan=0.4)
        elif k == "reese":                                       # reese bass: detuned saws + sub, driven, lowpassed
            d = kw["d"]; m_ = int((d + 0.03) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = 0.5 * saw(2 * np.pi * f * 0.996 * tt) + 0.5 * saw(2 * np.pi * f * 1.004 * tt) + 0.8 * np.sin(2 * np.pi * f * tt)
            x = lfilter(*butter(2, 900 / (SR / 2)), np.tanh(1.8 * x))
            x *= np.minimum(1, tt / 0.004) * np.clip((d + 0.02 - tt) / 0.02, 0, 1)
            put(t, x * v * 0.9)
        elif k == "stab":
            d = kw["d"]; m_ = int((d + 0.08) * SR); tt = np.arange(m_) / SR; x = np.zeros(m_)
            for m in kw["ch"]: x += pulse(2 * np.pi * mtof(m + 12) * tt, 0.25)
            x = lfilter(*butter(2, 3200 / (SR / 2)), np.tanh(x / 2)) * env(m_, 0.002, 0.12) * np.clip((d + 0.05 - tt) / 0.05, 0, 1)
            put(t, x * v, pan=0.2, send=0.15)
        elif k == "pad":
            d = kw["d"]; m_ = int((d + 0.5) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / 0.4) * np.clip((d + 0.4 - tt) / 0.4, 0, 1); x = np.zeros(m_)
            for m in kw["ch"]:
                f = mtof(m + 12); x += np.sin(2 * np.pi * f * tt) + 0.4 * saw(2 * np.pi * f * 1.003 * tt)
            x = lfilter(*butter(2, 1800 / (SR / 2)), x)
            put(t, x * e * v * 0.22, send=0.3)
        elif k in ("kick", "sboom"):
            m_ = int((0.28 if k == "kick" else 1.6) * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum((52 if k == "kick" else 34) + 150 * np.exp(-tt / 0.025)) / SR
            x = np.sin(ph) * env(m_, 0.001, 0.10 if k == "kick" else 0.55)
            x[: int(0.003 * SR)] += rng.standard_normal(int(0.003 * SR)) * 0.35
            if k == "sboom":                                     # sonic boom: two cracks (N-wave) over the low boom
                for o in (0.0, 0.11):
                    i0 = int(o * SR); cr = lfilter(*butter(2, 800 / (SR / 2), "high"), rng.standard_normal(int(0.25 * SR)))
                    cr *= env(len(cr), 0.0005, 0.03); x[i0:i0 + len(cr)] += cr * 0.9
                put(t, np.tanh(1.6 * x) * v, send=0.4)
            else:
                put(t, np.tanh(1.8 * x) * v)
        elif k == "snare":
            m_ = int(0.22 * SR); tt = np.arange(m_) / SR
            nz = lfilter(*butter(2, [1200 / (SR / 2), 8000 / (SR / 2)], "band"), rng.standard_normal(m_))
            x = nz * env(m_, 0.0005, 0.06) + 0.5 * np.sin(2 * np.pi * 190 * tt) * env(m_, 0.0005, 0.03)
            put(t, np.tanh(1.6 * x) * v * 1.2, send=0.18)
        elif k in ("hat", "tick"):
            m_ = int(0.05 * SR)
            put(t, lfilter(*butter(2, (9000 if k == "hat" else 5000) / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.001, 0.012) * v,
                pan=0.3)
        elif k == "crash":
            m_ = int(1.8 * SR)
            put(t, lfilter(*butter(2, 5000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.002, 0.5) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            put(t, lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
        elif k == "whoosh":                                      # jet roar across the race
            m_ = int((kw["d"] + 0.4) * SR); tt = np.arange(m_) / SR
            x = lfilter(*butter(2, [300 / (SR / 2), 4000 / (SR / 2)], "band"), rng.standard_normal(m_))
            e = np.minimum(1, tt / 0.3) * np.clip((kw["d"] + 0.3 - tt) / 0.3, 0, 1)
            put(t, x * e * v * 0.5)
        elif k == "flag":
            m_ = int(0.5 * SR); tt = np.arange(m_) / SR
            x = pulse(2 * np.pi * 880 * tt, 0.5) * env(m_, 0.001, 0.1)
            put(t, lfilter(*lp6, x) * v * 0.3, send=0.3)
    def reverb(x):
        out = np.zeros_like(x)
        for dl, g in ((1557, 0.70), (1617, 0.69), (1491, 0.71), (1422, 0.70)):
            y = x.copy()
            for i in range(dl, len(y), dl): y[i:i + dl] += g * y[i - dl:i][:len(y[i:i + dl])]
            out += y * 0.25
        return out
    b, a = butter(1, 5000 / (SR / 2))
    L += lfilter(b, a, reverb(fxL)) * 0.25; R += lfilter(b, a, reverb(np.roll(fxR, 300))) * 0.25
    b, a = butter(2, 13000 / (SR / 2)); L = lfilter(b, a, L); R = lfilter(b, a, R)
    tt = np.arange(n) / SR; duck = np.ones(n)
    for kt in KICKS:
        i0 = int(kt * SR); i1 = min(n, i0 + int(0.25 * SR))
        if i0 < n: duck[i0:i1] = np.minimum(duck[i0:i1], 1 - 0.30 * np.exp(-np.arange(i1 - i0) / SR / 0.07))
    L *= duck; R *= duck
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
        print([(REC[i]["year"], REC[i]["lane"][0], int(REC[i]["k"]), round(t, 2), pitch(i)) for i, t in enumerate(RT)])
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
