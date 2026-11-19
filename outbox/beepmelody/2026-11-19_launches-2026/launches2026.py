"""BEEPMELODY — EVERY ROCKET OF 2026. Every orbital launch attempt from 1 Jan to 18 Nov 2026 (265 attempts, 8 failures,
Starship suborbital tests excluded). Every note = one launch, on its real day: 1 day = one 8th note at 160 BPM (0.1875 s).
Pitch = country of the launch site. A failure = a WRONG note (tritone buzz) + red burst + the drums drop out for half a bar.
Scene: neon pixel globe that spins; every launch is a rocket rising from its spaceport (site = main spaceport of that rocket,
approximate to a few hundred km), far-side launches climb out from behind the limb.
Music (co-pilot step 2, choice B): "countdown electro", 160 BPM, four-on-the-floor kick, 8th hats, rolling saw bass, bright plucks.
Data: launches2026_research.csv (keeptrack.space + orbitalradar.com line by line; Jan-Jun totals = Wikipedia 2026 in spaceflight).

    python3 launches2026.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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
VARIANT = os.environ.get("LV", "neon")          # neon (dark) | light (paper, Race to the Sky family)

# ================= data =================
REC = [r for r in csv.DictReader(open(os.path.join(HERE, "launches2026_research.csv"))) if not r["check"].startswith("EXCLUDE")]
REC.sort(key=lambda r: r["date"])
D0 = dt.date(2026, 1, 1); DLAST = dt.date(2026, 11, 18)
NDAYS = (DLAST - D0).days + 1                   # 322
for r in REC:
    r["d"] = dt.date.fromisoformat(r["date"]); r["k"] = (r["d"] - D0).days
    r["fail"] = r["outcome"] != "success"
N = len(REC); NFAIL = sum(r["fail"] for r in REC)

PADS = {"CCSFS": (28.5, -80.6), "VSFB": (34.7, -120.6), "MAHIA": (-39.3, 177.9), "WEN": (19.6, 110.9), "XIC": (28.2, 102.0),
        "TAI": (38.8, 111.6), "JIU": (41.0, 100.3), "SEA": (35.0, 121.5), "PLE": (62.9, 40.6), "BAI": (45.9, 63.3),
        "VOS": (51.9, 128.3), "KOU": (5.2, -52.8), "AND": (69.3, 16.0), "SHAR": (13.7, 80.2), "TNSC": (30.4, 131.0),
        "KII": (33.5, 135.9), "NARO": (34.4, 127.5)}
def site(r):
    v, m, c = r["vehicle"], r["mission"], r["country"]
    if c == "US":
        if v.startswith("Falcon 9") and any(s in m for s in ("Starlink 11-", "Starlink 15-", "Starlink 17-", "SDA", "T1TL", "Transporter", "NRO")):
            return "VSFB"
        return "CCSFS"
    if c == "NZ": return "MAHIA"
    if c == "CN":
        if any(s in v for s in ("Long March 5", "Long March 7", "Long March 8", "Long March 12", "Long March 10")): return "WEN"
        if "3B" in v: return "XIC"
        if any(s in v for s in ("Long March 6", "Long March 4B", "Long March 2C")): return "TAI"
        if any(s in v for s in ("Jielong", "Gravity")): return "SEA"
        return "JIU"
    if c == "RU":
        if "Vostochny" in m: return "VOS"
        if any(s in m for s in ("Progress", "Soyuz crew")) or "Proton" in v: return "BAI"
        return "PLE"
    if c == "EU": return "AND" if v == "Spectrum" else "KOU"
    if c == "IN": return "SHAR"
    if c == "JP": return "KII" if v == "Kairos" else "TNSC"
    return "NARO"
for r in REC:
    r["la"], r["lo"] = PADS[site(r)]

CNAME = {"US": "USA", "CN": "CHINA", "NZ": "NEW ZEALAND", "RU": "RUSSIA", "EU": "EUROPE", "IN": "INDIA", "JP": "JAPAN", "KR": "S. KOREA"}

# ================= timeline: 1 day = one 8th note at 160 BPM =================
BPM = 160.0; BEAT = 60.0 / BPM; DAY = BEAT / 2          # 0.1875 s
INTRO = 8 * BEAT                                          # 3.0 s
T_END = INTRO + NDAYS * DAY                               # end of the data
OUTRO = 14 * BEAT                                         # 5.25 s
TOTAL = T_END + OUTRO
seen = {}
for r in REC:
    j = seen.get(r["k"], 0); seen[r["k"]] = j + 1
    r["t"] = INTRO + r["k"] * DAY + j * DAY / 4
RT = [r["t"] for r in REC]
def kday(m, d): return (dt.date(2026, m, d) - D0).days
SC = [("intro", INTRO), ("q1", kday(4, 1) * DAY), ("q2", (kday(7, 1) - kday(4, 1)) * DAY),
      ("q3", (kday(10, 1) - kday(7, 1)) * DAY), ("q4", (NDAYS - kday(10, 1)) * DAY), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
def rec_index(T):
    return int(np.searchsorted(RT, T, side="right")) - 1
def day_at(T): return int(np.clip((T - INTRO) / DAY, 0, NDAYS - 1))

# ================= music plan =================
DEG = {"US": 0, "CN": 2, "NZ": 4, "RU": -2, "EU": 3, "IN": 5, "JP": 6, "KR": 7}
PENT = [0, 3, 5, 7, 10]
def note(country, base=69):
    d = DEG.get(country, 1); return base + 12 * (d // 5) + PENT[d % 5]
ROOTS = [33, 33, 29, 31]                                 # A A F G (bass), 2 bars each
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
FAILT = [r["t"] for r in REC if r["fail"]]
def muted(x): return any(0 <= x - c < BEAT * 2 for c in FAILT)
def build():
    nb = int(round(TOTAL / BEAT))
    ev(0.02, "riser", d=INTRO - 0.05, v=0.10)
    for b in range(nb):
        t = b * BEAT; bar = b // 4
        if t < INTRO - 1e-6:
            if b % 2 == 0: ev(t, "hat", v=0.02)
            if b >= 4: ev(t, "kick", v=0.12 + 0.03 * (b - 4))
            continue
        r = ROOTS[(bar // 2) % 4]
        if t < T_END:
            if muted(t): continue
            ev(t, "kick", v=0.22)
            if b % 2: ev(t, "clap", v=0.07)
            ev(t, "hat", v=0.015); ev(t + DAY, "hat", v=0.03)
            ev(t + DAY, "bass", m=r + 12, v=0.07)
        elif t < TOTAL - 1.0:
            if (b - int(round(T_END / BEAT))) % 4 == 0: ev(t, "pad", m=r, d=4 * BEAT, v=0.05)
    ev(INTRO, "crash", v=0.10)
    for r_ in REC:
        if r_["fail"]: ev(r_["t"], "fail", m=note(r_["country"], 57) + 6, v=0.20)
        else: ev(r_["t"], "pluck", m=note(r_["country"]), v=0.15)
    for k, d in enumerate([0, 7, 12, 15, 19, 24]):      # outro arpeggio: the year's total
        ev(T_END + BEAT * 2 + k * BEAT / 2, "pluck", m=57 + d, v=0.16)
    ev(T_END + BEAT * 2, "kick", v=0.25); ev(T_END + BEAT * 2, "crash", v=0.10)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= palette =================
if VARIANT == "light":
    BG = (236, 242, 248); SPACE2 = (220, 230, 242); OCEAN = (196, 220, 238); OCEAN2 = (184, 210, 232); LANDC = (236, 222, 186)
    LAND2 = (214, 196, 150); INK = (34, 44, 78); INK2 = (92, 104, 140); RIM = (150, 180, 214); PANEL = (252, 248, 238)
    CCOL = {"US": (40, 110, 220), "CN": (226, 150, 30), "NZ": (40, 160, 90), "RU": (170, 70, 190), "EU": (30, 160, 180),
            "IN": (230, 110, 40), "JP": (220, 80, 140), "KR": (90, 90, 110)}
    RED = (210, 40, 40); GOLD = (220, 150, 30); WHITE = (255, 255, 255); STARC = None
else:
    BG = (6, 8, 26); SPACE2 = (12, 14, 40); OCEAN = (12, 26, 66); OCEAN2 = (16, 32, 78); LANDC = (34, 150, 170)
    LAND2 = (60, 210, 220); INK = (230, 244, 255); INK2 = (130, 150, 200); RIM = (70, 120, 230); PANEL = (10, 12, 34)
    CCOL = {"US": (90, 220, 255), "CN": (255, 210, 70), "NZ": (110, 255, 150), "RU": (230, 120, 255), "EU": (120, 160, 255),
            "IN": (255, 160, 80), "JP": (255, 130, 190), "KR": (230, 230, 230)}
    RED = (255, 50, 60); GOLD = (255, 210, 70); WHITE = (255, 255, 255); STARC = (180, 200, 255)

# ================= globe =================
GX, GY, GR = 90.0, 166.0, 54.0
LAT_V = math.radians(22.0)
SPIN = 360.0 / 12.0                                      # one turn every 12 s
def view_lon(T): return -100.0 + SPIN * T                # starts over the Americas
_land = np.load(os.path.join(ENGINE, "..", "geo", "land_clean.npy"))
YY, XX = np.mgrid[0:AH, 0:AW]
DX = (XX + 0.5 - GX) / GR; DY = -(YY + 0.5 - GY) / GR
INDISK = DX ** 2 + DY ** 2 < 1.0
DZ = np.sqrt(np.clip(1 - DX ** 2 - DY ** 2, 0, 1))
# inverse orthographic, view centre lat = LAT_V, lon = 0 (rotation added per frame)
_LATG = np.degrees(np.arcsin(np.clip(DY * math.cos(LAT_V) + DZ * math.sin(LAT_V), -1, 1)))
_LONG0 = np.degrees(np.arctan2(DX, DZ * math.cos(LAT_V) - DY * math.sin(LAT_V)))
_rng = np.random.default_rng(7)
STARS = [(int(_rng.integers(0, AW)), int(_rng.integers(0, AH)), float(_rng.random())) for _ in range(90)]
def to_view(la, lo, T, alt=0.0):
    """3D in view coords: x right, y up, z toward the viewer (unit globe)."""
    la, lo = math.radians(la), math.radians(lo - view_lon(T))
    x = math.cos(la) * math.sin(lo); y0 = math.sin(la); z0 = math.cos(la) * math.cos(lo)
    y = y0 * math.cos(LAT_V) - z0 * math.sin(LAT_V); z = y0 * math.sin(LAT_V) + z0 * math.cos(LAT_V)
    s = 1.0 + alt
    return x * s, y * s, z * s
def proj(p): return GX + p[0] * GR, GY - p[1] * GR
def hidden(p): return p[2] < 0 and p[0] ** 2 + p[1] ** 2 < 1.0

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
    rim = (np.abs(np.sqrt(DX ** 2 + DY ** 2) - 1.0) < 1.2 / GR)
    a[rim] = RIM
    c.art = Image.fromarray(a); c.a = ImageDraw.Draw(c.art)

def draw_rockets(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    i0 = int(np.searchsorted(RT, T - 2.2))
    for i in range(i0, k + 1):
        r = REC[i]; age = T - RT[i]; col = CCOL[r["country"]]
        stop = 0.30 if r["fail"] else 1.2
        s1 = min(age, stop) / 1.2
        pts = []
        for j in range(13):
            s = s1 * j / 12
            p = to_view(r["la"], r["lo"] + 16 * s, T, alt=0.55 * s ** 1.4)
            pts.append((p, proj(p)))
        fade = max(0.0, 1 - max(0.0, age - stop) / (0.5 if r["fail"] else 0.9))
        if fade <= 0: continue
        tc = tuple(int(v * fade + BG[q] * (1 - fade)) for q, v in enumerate(col))
        for (p0, a0), (p1, a1) in zip(pts, pts[1:]):
            if not hidden(p0) and not hidden(p1): d.line([a0, a1], fill=tc)
        p, (hx, hy) = pts[-1]
        if not hidden(p) and age < stop + 0.05:
            d.rectangle([hx - 1, hy - 1, hx + 1, hy + 1], fill=WHITE if age < 0.12 else col)
        pad = pts[0]
        if not hidden(pad[0]) and age < 0.25:
            x, y = pad[1]; rr = 1 + age * 14
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=col)
        if r["fail"] and stop <= age < stop + 1.2:           # red burst where it died
            p = to_view(r["la"], r["lo"] + 16 * stop / 1.2, T, alt=0.55 * (stop / 1.2) ** 1.4)
            x, y = proj(p); b = age - stop
            for q in range(3):
                rr = 2 + (b - q * 0.08) * 40
                if rr > 2 and b - q * 0.08 < 0.7: d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=RED if q else WHITE)
            rng = random.Random(i)
            for q in range(14):
                ang = rng.random() * 6.283; sp = 8 + rng.random() * 26
                d.point((x + math.cos(ang) * sp * b, y + math.sin(ang) * sp * b + 10 * b * b), fill=RED)
    if k >= 0 and T - RT[k] < 0.9 and not REC[k]["fail"]:     # label of the newest launch on the globe
        pass

def frise(c, T):
    d = c.a; W = c.t; dy = day_at(T) if T >= INTRO else -1
    X0, X1, Y0, Y1 = 14, 170, 262, 290
    d.rectangle([0, Y0 - 6, AW, AH], fill=BG)
    cnt = np.zeros(11, int); fl = np.zeros(11, int)
    for r in REC:
        if r["t"] <= T: cnt[r["d"].month - 1] += 1; fl[r["d"].month - 1] += r["fail"]
    bw = (X1 - X0) / 11
    for m in range(11):
        x0 = int(X0 + m * bw + 1); x1 = int(X0 + (m + 1) * bw - 2)
        h = cnt[m] / 32 * (Y1 - Y0)
        d.rectangle([x0, Y1, x1, Y1], fill=INK2)
        if cnt[m]: d.rectangle([x0, int(Y1 - h), x1, Y1], fill=CCOL["US"] if VARIANT == "light" else (50, 120, 200))
        for f in range(fl[m]): d.rectangle([x0, int(Y1 - h) - 2 - 2 * f, x1, int(Y1 - h) - 2 - 2 * f], fill=RED)
        cur = (D0 + dt.timedelta(days=dy)).month - 1 if dy >= 0 else -1
        text(W, int((x0 + x1) + 1), 584, "JFMAMJJASON"[m], fill=INK if m == cur else INK2, align="c")
        if cnt[m] and (m == cur or T >= T_END):
            text(W, int(x0 + x1 + 1), int((Y1 - h) * 2) - 22 - 4 * fl[m], str(cnt[m]), fill=INK, align="c")
    if 0 <= dy:
        x = X0 + (dy / NDAYS) * (X1 - X0)
        d.line([x, Y1 + 2, x, Y1 + 4], fill=GOLD)

def legend(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([0, 606, 360, 640], fill=PANEL); W.rectangle([0, 606, 360, 607], fill=INK2)
    cs = [("US", "USA"), ("CN", "CHINA"), ("NZ", "NZ"), ("RU", "RU"), ("EU", "EU")]
    x = 6
    for cc, lab in cs:
        n = sum(1 for i in range(k + 1) if REC[i]["country"] == cc)
        W.rectangle([x, 618, x + 5, 623], fill=CCOL[cc]); s = f"{lab} {n}"
        text(W, x + 9, 610, s, fill=INK); x += 9 + 8 * len(s) + 4
    n = sum(1 for i in range(k + 1) if REC[i]["country"] in ("IN", "JP", "KR"))
    text(W, 354, 610, f"+{n}", fill=INK2, align="r")

def hud(c, T):
    W = c.t; k = rec_index(T); dy = day_at(T)
    W.rectangle([16, 14, 344, 112], fill=PANEL); W.rectangle([16, 14, 344, 15], fill=RIM); W.rectangle([16, 111, 344, 112], fill=RIM)
    day = D0 + dt.timedelta(days=dy)
    nf = sum(1 for i in range(k + 1) if REC[i]["fail"])
    text(W, 28, 18, "ORBITAL LAUNCHES", fill=INK2)
    age = T - RT[k] if k >= 0 else 9
    fresh = k >= 0 and age < 0.12
    text(W, 28, 38, f"{k + 1}", size=40, fill=(RED if REC[k]["fail"] else (WHITE if VARIANT == "neon" else GOLD)) if fresh else INK)
    text(W, 334, 18, "2026", fill=INK2, align="r")
    text(W, 334, 38, day.strftime("%d %b").upper(), size=40, fill=GOLD, align="r")
    text(W, 28, 86, f"FAILED {nf}", fill=RED if nf else INK2)
    W.rectangle([16, 118, 344, 156], fill=PANEL); W.rectangle([16, 118, 19, 156], fill=CCOL[REC[k]["country"]] if k >= 0 else INK2)
    if k >= 0 and age < 1.5:
        r = REC[k]; s = f"{r['vehicle'].upper()} · {CNAME[r['country']]}"
        text(W, 28, 122, s[:38], fill=RED if r["fail"] else INK)
        text(W, 28, 138, ("FAILED · " if r["fail"] else "") + r["mission"].upper()[:30], fill=RED if r["fail"] else INK2)

def ifind(date, fail=None): return next(i for i, r in enumerate(REC) if r["date"] == date and (fail is None or r["fail"] == fail))
BANNERS = {}
for i, r in enumerate(REC):
    if r["fail"]:
        BANNERS[i] = (f"{r['vehicle'].upper()} FAILED", r["d"].strftime("%d %b").upper() + " · " + CNAME[r["country"]], True)
BANNERS[0] = ("FIRST OF THE YEAR", "3 JAN · FALCON 9", False)
BANNERS[99] = ("#100", REC[99]["d"].strftime("%d %b").upper(), True)
BANNERS[199] = ("#200", REC[199]["d"].strftime("%d %b").upper(), True)
BANNERS[ifind("2026-02-12")] = ("4 LAUNCHES IN ONE DAY", "12 FEB", False)
def banner(c, T):
    k = rec_index(T)
    cand = [i for i in BANNERS if i <= k and 0.05 < T - RT[i] < 1.6]
    if not cand: return
    i = max(cand); a = T - RT[i]
    tt, sub, big = BANNERS[i]; W = c.t; yb = 470
    col = RED if REC[i]["fail"] else GOLD
    w = max((16 if big else 8) * len(tt), 8 * len(sub)) + 30
    hh = 60 if big else 42
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hh], fill=PANEL)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    W.rectangle([180 - w / 2, yb + hh - 1, 180 + w / 2, yb + hh], fill=col)
    if big:
        text(W, 180, yb + 3, tt, size=40, fill=col if REC[i]["fail"] else INK, align="c")
        if a > 0.15: text(W, 180, yb + 38, sub, fill=INK2, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if a > 0.15: text(W, 180, yb + 21, sub, fill=col, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_globe(c, T); draw_rockets(c, T); frise(c, T); legend(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 14, 344, 156], fill=PANEL); W.rectangle([16, 14, 344, 15], fill=RIM); W.rectangle([16, 155, 344, 156], fill=RIM)
    text(W, 28, 20, "EVERY ROCKET", size=40, fill=INK)
    if t > 0.3: text(W, 28, 56, "OF 2026", size=40, fill=GOLD)
    if t > 0.9: text(W, 28, 104, "EVERY NOTE = ONE ORBITAL LAUNCH", fill=INK2)
    if t > 1.5: text(W, 28, 128, "WRONG NOTE = IT FAILED", fill=RED)
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
    W.rectangle([16, 14, 344, 372], fill=PANEL); W.rectangle([16, 14, 344, 16], fill=GOLD)
    text(W, 180, 22, f"{N} LAUNCHES", size=40, fill=INK, align="c")
    text(W, 180, 62, "1 JAN TO 18 NOV 2026", fill=INK2, align="c")
    busiest = max(range(11), key=lambda m: sum(1 for r in REC if r["d"].month - 1 == m))
    nb = sum(1 for r in REC if r["d"].month - 1 == busiest)
    rows = [("REACHED ORBIT", str(N - NFAIL), ""), ("FAILED", str(NFAIL), "8 WRONG NOTES"),
            ("BUSIEST MONTH", str(nb), dt.date(2026, busiest + 1, 1).strftime("%B").upper())]
    for j, (a, b, s) in enumerate(rows):
        if t > 0.4 + j * 0.7:
            y = 96 + j * 62
            text(W, 30, y + 6, a, fill=RED if a == "FAILED" else CCOL["US"]); text(W, 330, y - 4, b, size=40, fill=INK, align="r")
            if s: text(W, 330, y + 32, s, fill=INK2, align="r")
    if t > 2.6: text(W, 180, 290, "HOW MANY BY 31 DEC?", fill=GOLD, align="c")
    if t > 3.2:
        text(W, 180, 310, "DATA: KEEPTRACK.SPACE, ORBITALRADAR.COM", fill=INK2, align="c")
        text(W, 180, 330, "ORBITAL ATTEMPTS ONLY (STARSHIP", fill=INK2, align="c")
        text(W, 180, 348, "SUBORBITAL TESTS NOT COUNTED)", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "q1": sc_main("q1"), "q2": sc_main("q2"), "q3": sc_main("q3"), "q4": sc_main("q4"), "outro": sc_outro}

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
    z = 1.0 + 0.008 * kp * FXK; dx = dy = 0.0
    fi = [f for f in FAILT if 0.30 <= T - f < 0.8]
    if fi:                                                   # the screen shakes when a rocket dies
        a = T - fi[-1] - 0.30; amp = 26 * FXK * math.exp(-a / 0.15)
        dx = amp * math.sin(a * 90); dy = amp * 0.6 * math.cos(a * 70); z = max(z, 1.02)
    if z > 1.0005 or dx or dy: fr = warp(fr, z, dx, dy, z)
    if fi:
        a = T - fi[-1] - 0.30
        if a < 0.25:
            f = 0.35 * FXK * (1 - a / 0.25)
            fr = (fr * (1 - f) + np.array(RED) * f).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.7)) / 0.7)
        if f > 0: fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    return fr

# ================= audio (mood B, co-pilot step 2) =================
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
    def pluck(f, dec=.22):
        n = int(.8 * SR); tt = np.arange(n) / SR
        s = sum((1 / h) * np.sin(2 * np.pi * f * h * 1.002 * tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
        return s * env(n, .002, dec)
    def saw(f, dur, det=(.995, 1.0, 1.005)):
        n = int(dur * SR); tt = np.arange(n) / SR
        return sum(2 * ((f * d * tt) % 1) - 1 for d in det) / len(det)
    n = int((TOTAL + 1.5) * SR); L = np.zeros(n)
    def put(t, sig, g=1.0):
        i = int(t * SR); j = min(n, i + len(sig))
        if 0 <= i < n: L[i:j] += g * sig[:j - i]
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if k == "kick": put(t, kick(v))
        elif k == "clap": put(t, noise(.16, 6000, 25, int(t * 997), 800), v)
        elif k == "hat": put(t, noise(.04, 9000, 120, int(t * 1009), 5000), v)
        elif k == "bass":
            nn = int(DAY * .9 * SR); tt = np.arange(nn) / SR
            put(t, v * lowpass(saw(mtof(kw["m"]), DAY * .9), 800) * np.exp(-tt * 8))
        elif k == "pluck": put(t, v * pluck(mtof(kw["m"])))
        elif k == "fail":
            nn = int(1.0 * SR); tt = np.arange(nn) / SR
            f = mtof(kw["m"]) * np.exp(-tt * 1.2)
            s = np.tanh(4 * (2 * ((np.cumsum(f) / SR) % 1) - 1))
            put(t, v * lowpass(s, 2500) * env(nn, .002, .5)); put(t, noise(.6, 3000, 5, 911, 200), .08)
        elif k == "pad":
            nn = int((kw["d"] + .4) * SR); tt = np.arange(nn) / SR
            e = np.minimum(1, tt / .3) * np.clip((kw["d"] + .4 - tt) / .4, 0, 1)
            s = sum(lowpass(saw(mtof(kw["m"] + 12 + iv), kw["d"] + .4), 1400) for iv in (0, 7, 12, 15))
            put(t, v * s * e)
        elif k == "crash": put(t, noise(1.8, 12000, 1.6, 1234, 3000), v)
        elif k == "riser":
            nn = int(kw["d"] * SR); tt = np.arange(nn) / SR
            put(t, highpass(np.random.RandomState(3).randn(nn), 1500) * (tt / kw["d"]) ** 2 * v)
    out = L.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22)]:
        k_ = int(d * SR); out[k_:] += g * .6 * L[:-k_]
    L = .84 * L + .16 * lowpass(out, 4000)
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
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/{VARIANT}_t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print("TOTAL", round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, "launches", N, "fail", NFAIL)
        print(Counter(k for _, k, _ in EV)); print(Counter(site(r) for r in REC))
        for i in sorted(BANNERS): print(i + 1, REC[i]["date"], round(RT[i], 2), BANNERS[i][:2])
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
