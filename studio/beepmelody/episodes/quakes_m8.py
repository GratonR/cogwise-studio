"""BEEPMELODY — THE PLANET SNAPPED 100 TIMES. Every magnitude 8+ earthquake since 1900 (USGS ComCat, 100 events,
1903 Tonga -> 2025 Kamchatka). Every note = one quake; pitch = magnitude; voice by size (marimba < 8.5, bell 8.5-8.9,
soft lead + boom >= 9). Light 'paper map' palette from the race-to-the-sky pilot, coral quakes.
Music: chill-pop bed (as altitude_race.py), 120 BPM, D major, vi-IV-I-V (Bm7 Gmaj7 Dmaj7 A).
Data: quakes_m8.csv (USGS + second source per row).

    python3 quakes_m8.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv, datetime as dt
from decimal import Decimal, ROUND_HALF_UP
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
REC = list(csv.DictReader(open(os.path.join(HERE, "quakes_m8.csv"))))
for r in REC:
    r["m"] = float(r["mag"]); r["year"] = r["date"][:4]
    r["d"] = dt.date.fromisoformat(r["date"])
    r["fy"] = r["d"].year + (r["d"].timetuple().tm_yday - 0.5) / 366.0
    r["la"] = float(r["lat"]); r["lo"] = float(r["lon"]); r["dep"] = float(r["depth_km"])
N = len(REC)

def mag1(m): return str(Decimal(str(m)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
def depth_txt(r):
    km = r["dep"]; mi = km * 0.621371
    return f"DEPTH {round(km):,} KM · {round(mi):,} MI"

# ================= palette (paper map, light) =================
INK = (34, 44, 78)
INK2 = (92, 104, 140)
CORAL = (232, 92, 70)
RED = (196, 52, 48)
GOLD = (236, 168, 52)
CREAM = (252, 248, 238)
WHITE = (255, 255, 255)
OCEAN = (214, 233, 244)
OCEAN2 = (200, 224, 240)
LAND = (238, 226, 196)
LAND2 = (216, 200, 160)
def vcol(m):
    return GOLD if m >= 9.0 else RED if m >= 8.5 else CORAL

# ================= timeline (all on the beat) =================
BPM = 120.0
BEAT = 60.0 / BPM
INTRO_B = 7
def gap_beats(i):
    dd = (REC[i]["d"] - REC[i - 1]["d"]).days
    if i == N - 1: return 6                                  # 2021 -> 2025: the wait before #100
    if dd < 45: return 0.5
    if dd < 900: return 1
    if dd < 1500: return 1.5
    if dd < 2400: return 2
    return 4                                                 # 1977 -> 1985 silence
GAPS_B = [gap_beats(i) for i in range(1, N)]
HOLD_B, OUTRO_B = 8, 16
RT = [INTRO_B * BEAT]
for g in GAPS_B: RT.append(RT[-1] + g * BEAT)
T_FINAL = RT[-1]
TOTAL = T_FINAL + (HOLD_B + OUTRO_B) * BEAT
def first_year(y): return next(i for i, r in enumerate(REC) if int(r["year"]) >= y)
I1930, I1960, I2000 = first_year(1930), first_year(1960), first_year(2000)
SC = [("intro", RT[0]), ("early", RT[I1930] - RT[0]), ("mid", RT[I1960] - RT[I1930]), ("giants", RT[I2000] - RT[I1960]),
      ("modern", T_FINAL + HOLD_B * BEAT - RT[I2000]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan (shared by picture + audio) =================
SCALE = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86, 88]       # D major pentatonic from D4
def pitch(i):
    """magnitude 8.0 -> D4 ... 9.5 -> E6: bigger quake = higher note"""
    m = REC[i]["m"]
    return SCALE[max(0, min(len(SCALE) - 1, int(round((m - 8.0) / 1.5 * (len(SCALE) - 1)))))]
def voice(i):
    m = REC[i]["m"]
    return "lead" if m >= 9.0 else "bell" if m >= 8.5 else "mallet"
CHORDS = [(50, 54, 57, 61), (55, 59, 62, 66), (54, 57, 61, 62), (52, 57, 61, 64)]   # Bm7/D Gmaj7 Dmaj7 A
ROOTS = [47, 43, 50, 45]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    ev(0.10, "bell", m=74, v=0.40)
    ev(0.10, "boom", v=0.30)
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        ch = CHORDS[bar % 4]; ro = ROOTS[bar % 4]
        groove = RT[0] - 2 * BEAT <= t < T_FINAL + 6 * BEAT
        late = t >= T_FINAL + 6 * BEAT
        if pos == 0: ev(t, "keys", ch=ch, d=1.4 * BEAT, v=0.20 if not late else 0.15)
        if pos == 1 and not late: ev(t + BEAT / 2, "keys", ch=ch, d=0.45 * BEAT, v=0.13)
        if pos == 3 and not late: ev(t + BEAT / 2, "keys", ch=ch, d=0.45 * BEAT, v=0.11)
        if late and pos == 0: ev(t, "pad", ch=ch, d=4 * BEAT, v=0.12)
        if groove:
            if pos == 0: ev(t, "bass", m=ro, d=BEAT * 0.8, v=0.32)
            if pos == 1: ev(t + BEAT / 2, "bass", m=ro + 12, d=BEAT * 0.35, v=0.22)
            if pos == 2: ev(t, "bass", m=ro + 7, d=BEAT * 0.6, v=0.26)
            if pos == 3: ev(t + BEAT / 2, "bass", m=ro, d=BEAT * 0.4, v=0.24)
            if t >= RT[0]:
                if pos in (0, 2): ev(t, "kick", v=0.62)
                if pos == 1: ev(t + BEAT / 2, "kick", v=0.38)
                if pos in (1, 3): ev(t, "snare", v=0.34)
                for h in range(2): ev(t + h * BEAT * 0.54, "hat", v=0.10 if h == 0 else 0.07)
                if pos == 3 and bar % 2 == 1: ev(t + BEAT * 0.54, "ohat", v=0.08)
            elif pos in (1, 3):
                ev(t, "hat", v=0.06)
    for i, t in enumerate(RT):
        r = REC[i]
        ev(t, voice(i), m=pitch(i), v=0.50 + 0.20 * min(1.0, (r["m"] - 8.0) / 1.0))
        if r["m"] >= 8.5: ev(t, "boom", v=0.18 + 0.25 * min(1.0, (r["m"] - 8.5) / 1.0))
        if r["m"] >= 9.0: ev(t, "crash", v=0.26)
    for k, d in enumerate([0, 7, 12, 16, 19, 24]):                  # rising arpeggio on quake #100
        ev(T_FINAL + (k + 1) * BEAT / 4, "bell", m=74 + d - 12, v=0.40)
    ev(T_FINAL, "crash", v=0.32)
    ev(T_FINAL - BEAT * 4, "riser", d=BEAT * 4, v=0.13)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= map =================
LON0, LON1, LAT0, LAT1 = 20.0, 340.0, 72.0, -66.0          # Pacific-centred: 20°E -> 340°E (= 20°W)
MX0, MX1, MY0 = 0, AW, 96
PXD = (MX1 - MX0) / (LON1 - LON0)
MY1 = MY0 + (LAT0 - LAT1) * PXD
def lon360(lo): return lo % 360.0
def map_xy(la, lo):
    return MX0 + (lon360(lo) - LON0) * PXD, MY0 + (LAT0 - la) * PXD
_land = np.load(os.path.join(ENGINE, "..", "geo", "land_clean.npy"))     # 720 x 1440, 0.25°, lat 90..-90, lon -180..180
def _land_at(la, lo):
    iy = int(np.clip((90.0 - la) * 4, 0, 719)); ix = int(np.clip(((lo + 180.0) % 360.0) * 4, 0, 1439))
    return _land[max(0, iy - 1):iy + 2, max(0, ix - 1):ix + 2].mean() > 0.4
def _map_img():
    a = np.zeros((AH, AW, 3), np.uint8); a[:] = CREAM
    for y in range(int(MY0), int(math.ceil(MY1))):
        la = LAT0 - (y + 0.5 - MY0) / PXD
        for x in range(MX0, MX1):
            lo = LON0 + (x + 0.5 - MX0) / PXD
            a[y, x] = LAND if _land_at(la, lo) else (OCEAN if (x + y) % 7 else OCEAN2)
    # coastline shade
    L = (a == np.array(LAND)).all(-1)
    edge = L & ~(np.roll(L, 1, 0) & np.roll(L, -1, 0) & np.roll(L, 1, 1) & np.roll(L, -1, 1))
    a[edge] = LAND2
    return a
MAP = _map_img()

# ================= chart (year x magnitude) =================
CX0, CX1, CY0, CY1 = 22, 174, 194, 284
def cx(fy): return CX0 + (fy - 1900.0) / (2027.0 - 1900.0) * (CX1 - CX0)
def cy(m): return CY1 - (m - 7.9) / (9.6 - 7.9) * (CY1 - CY0)

# ================= drawing =================
def ring(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], outline=col)

def draw_map(c, T):
    c.art = Image.fromarray(MAP.copy()); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    d.line([0, int(MY0) - 1, AW, int(MY0) - 1], fill=INK2); d.line([0, int(MY1), AW, int(MY1)], fill=INK2)
    k = rec_index(T)
    for i in range(k + 1):
        r = REC[i]; x, y = map_xy(r["la"], r["lo"]); age = T - RT[i]
        rad = 0.6 + (r["m"] - 8.0) * 2.2
        col = vcol(r["m"]) if age < 2.0 or r["m"] >= 8.5 else (210, 120, 104)
        if rad < 1.2: d.point((int(x), int(y)), fill=col); d.point((int(x) + 1, int(y)), fill=col)
        else: d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col)
        if 0 <= age < 1.1:                                   # ripples, bigger for bigger quakes
            span = 6 + (r["m"] - 8.0) * 22
            for j in range(3):
                a = age - j * 0.12
                if 0 <= a < 0.8: ring(d, x, y, 2 + a / 0.8 * span, WHITE if a < 0.25 else vcol(r["m"]))
    if k >= 0 and T - RT[k] < 2.0:
        r = REC[k]; x, y = map_xy(r["la"], r["lo"])
        lab = r["label"]; tx = int(x * 2); ty = int(y * 2) - 26
        w = 8 * len(lab); tx = max(4 + w // 2, min(356 - w // 2, tx))
        if ty < int(MY0 * 2) + 2: ty = int(y * 2) + 10
        W.rectangle([tx - w // 2 - 3, ty - 1, tx + w // 2 + 2, ty + 19], fill=CREAM)
        text(W, tx, ty, lab, fill=INK, align="c")

def draw_chart(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    d.rectangle([0, int(MY1) + 1, AW, AH], fill=CREAM)
    for m in (8.0, 8.5, 9.0, 9.5):
        y = cy(m)
        for x in range(CX0, CX1, 3): d.point((x, int(y)), fill=(214, 210, 200))
        text(W, CX0 * 2 - 6, int(y * 2) - 10, f"{m:.1f}", fill=INK2, align="r")
    d.line([CX0, CY1 + 2, CX1, CY1 + 2], fill=INK2)
    for yr in (1900, 1950, 2000):
        x = cx(yr); d.line([x, CY1 + 2, x, CY1 + 4], fill=INK2)
        text(W, int(x * 2), int((CY1 + 5) * 2), str(yr), fill=INK2, align="c")
    text(W, CX0 * 2 - 6, int(CY0 * 2) - 34, "MAGNITUDE", fill=INK2)
    for i in range(k + 1):
        r = REC[i]; x = int(round(cx(r["fy"]))); y = cy(r["m"]); age = T - RT[i]
        col = vcol(r["m"]) if (age < 1.2 or r["m"] >= 8.5) else (222, 150, 136)
        d.line([x, CY1, x, int(y)], fill=col)
        d.rectangle([x - 1, int(y) - 1, x + 1, int(y) + 1], fill=col if age > 0.15 else WHITE)
    if k >= 0:                                              # cursor
        x = cx(REC[k]["fy"]); d.line([x, CY0 - 4, x, CY0 - 2], fill=INK)

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if k < 0: return
    r = REC[k]; age = T - RT[k]; col = vcol(r["m"])
    text(W, 28, 22, "MAGNITUDE", fill=col if r["m"] >= 8.5 else INK2)
    text(W, 28, 44, f"M {mag1(r['m'])}", size=40, fill=col if age < 0.22 else INK)
    text(W, 28, 92, depth_txt(r), fill=INK2)
    text(W, 334, 44, r["year"], size=40, fill=GOLD, align="r")
    text(W, 334, 92, f"#{k + 1} / {N}", fill=INK2, align="r")
    W.rectangle([16, 128, 344, 172], fill=(250, 250, 252)); W.rectangle([16, 128, 19, 172], fill=col)
    n = int(min(60, age * 70))
    text(W, 28, 131, r["label"][:max(0, n)], fill=INK)
    if age > 0.12: text(W, 28, 151, r["d"].strftime("%d %b %Y").upper(), fill=INK2)

def legend(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([0, 598, 360, 640], fill=CREAM); W.rectangle([0, 598, 360, 599], fill=INK2)
    text(W, 10, 600, "EVERY NOTE = ONE M8+ EARTHQUAKE", fill=INK2)
    for j, (lab, lo, hi, col) in enumerate((("8-8.4", 8.0, 8.5, CORAL), ("8.5-8.9", 8.5, 9.0, RED), ("9+", 9.0, 10, GOLD))):
        cnt = sum(1 for i in range(k + 1) if lo <= REC[i]["m"] < hi)
        x = 22 + j * 112
        W.rectangle([x - 6, 625, x - 1, 630], fill=col)
        text(W, x + 2, 617, f"{lab}: {cnt}", fill=INK)

def idate(s): return next(i for i, r in enumerate(REC) if r["date"] == s)
BANNERS = {idate("1906-01-31"): ("BIGGEST SO FAR", "M 8.8 · ECUADOR-COLOMBIA", False),
           idate("1952-11-04"): ("FIRST M 9", "KAMCHATKA 1952", True),
           idate("1960-05-22"): ("BIGGEST EVER RECORDED", "M 9.5 · CHILE", True),
           idate("1964-03-28"): ("3 GIANTS IN UNDER 12 YEARS", "M 9.0 · 9.5 · 9.2", False),
           idate("1985-03-03"): ("7.5 YEARS WITHOUT AN M8", "THEN IT CAME BACK", False),
           idate("2004-12-26"): ("M 9.1 · SUMATRA", "THE BOXING DAY TSUNAMI", True),
           idate("2011-03-11"): ("M 9.1 · JAPAN", "TOHOKU", True),
           N - 1: ("#100", "KAMCHATKA · M 8.8", True)}
def banner(c, T):
    k = rec_index(T)
    if k not in BANNERS: return
    a = T - RT[k]
    hold = HOLD_B * BEAT if k == N - 1 else max(2.4 * BEAT, min(4 * BEAT, (GAPS_B[k] + 1.5) * BEAT))
    if not (0.1 < a < hold): return
    tt, sub, big = BANNERS[k]; W = c.t; yb = 466
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + (62 if big else 42)], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=CORAL)
    W.rectangle([180 - w / 2, yb + (61 if big else 41), 180 + w / 2, yb + (62 if big else 42)], fill=INK2)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 40, sub, fill=CORAL, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 21, sub, fill=CORAL, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_map(c, T); draw_chart(c, T); legend(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 26, "THE PLANET SNAPPED", size=40, fill=INK)
    if t > 0.4: text(W, 28, 64, f"{N} TIMES", size=40, fill=CORAL)
    if t > 1.0: text(W, 28, 112, "EVERY NOTE = ONE M8+ EARTHQUAKE", fill=INK2)
    if t > 1.6: text(W, 28, 140, "BIGGER QUAKE = HIGHER NOTE", fill=RED)
    if t > 2.2:
        W.rectangle([70, 466, 290, 508], fill=CREAM); W.rectangle([70, 466, 290, 468], fill=GOLD)
        text(W, 180, 469, "EVERY ONE SINCE 1900", fill=INK, align="c")
        text(W, 180, 488, "MAGNITUDE 8.0 OR MORE", fill=INK2, align="c")
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
    W.rectangle([16, 18, 344, 330], fill=CREAM); W.rectangle([16, 18, 344, 20], fill=CORAL)
    text(W, 180, 28, f"{N} QUAKES OF M8+", size=40, fill=INK, align="c")
    text(W, 180, 70, "1900 TO 2026", fill=INK2, align="c")
    rows = [("BIGGEST", "M 9.5", "VALDIVIA, CHILE · 1960"), ("M 9 OR MORE", str(sum(1 for r in REC if r["m"] >= 9.0)), "1952 · 1960 · 1964 · 2004 · 2011"),
            ("EACH +1.0", "32X", "MORE ENERGY (APPROX.)")]
    for j, (a, b, s) in enumerate(rows):
        if t > 0.5 + j * 0.8:
            y = 104 + j * 64
            text(W, 30, y + 6, a, fill=CORAL); text(W, 330, y - 4, b, size=40, fill=INK, align="r")
            text(W, 330, y + 34, s, fill=INK2, align="r")
    if t > 3.4: text(W, 180, 300, "WHERE WILL #101 HIT?", fill=GOLD, align="c")
    if t > 4.4:
        W.rectangle([10, 512, 350, 597], fill=CREAM)
        text(W, 180, 526, "DATA: USGS COMCAT (MAGNITUDES),", fill=INK2, align="c")
        text(W, 180, 546, "NOAA NCEI, ISC-GEM. ENERGY: USGS.", fill=INK2, align="c")
        text(W, 180, 566, "ALL M8+ TO 9 NOV 2026", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "mid": sc_main("mid"), "giants": sc_main("giants"),
           "modern": sc_main("modern"), "outro": sc_outro}

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
    z = 1.0 + 0.010 * kp * FXK
    k = rec_index(T)
    dx = dy = 0.0
    if k >= 0 and REC[k]["m"] >= 8.5 and 0 <= T - RT[k] < 0.6:      # the screen shakes on the big ones
        a = T - RT[k]; amp = (REC[k]["m"] - 8.3) * 22 * FXK * math.exp(-a / 0.18)
        dx = amp * math.sin(a * 90); dy = amp * 0.6 * math.cos(a * 70); z = max(z, 1.02)
    if z > 1.0005 or dx or dy: fr = warp(fr, z, dx, dy, z)
    if k >= 0 and 0 <= T - RT[k] < 0.10:
        fr = np.minimum(255, fr.astype(np.int16) + int(40 * FXK * (1 - (T - RT[k]) / 0.10))).astype(np.uint8)
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
    L = np.zeros(n); R = np.zeros(n); fxL = np.zeros(n); fxR = np.zeros(n)
    rng = np.random.default_rng(11)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fxL, i, x * send); add(fxR, i, x * send)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k in ("keys", "pad"):
            d = kw["d"]; m_ = int((d + 0.6) * SR); tt = np.arange(m_) / SR
            for j, m in enumerate(kw["ch"]):
                f = mtof(m)
                if k == "keys":
                    e = env(m_, 0.004, 0.9) * np.clip((d + 0.12 - tt) / 0.12, 0, 1)
                    mod = np.sin(2 * np.pi * f * tt) * 1.4 * np.exp(-tt / 0.15)
                    x = (np.sin(2 * np.pi * f * tt + mod) + 0.2 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.3)) * e
                    put(t + j * 0.006, x * v * 0.5, pan=-0.35 + 0.23 * j, send=0.10)
                else:
                    e = np.minimum(1, tt / 0.6) * np.clip((d + 0.5 - tt) / 0.5, 0, 1)
                    x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)) * e
                    put(t, x * v * 0.4, pan=-0.4 + 0.27 * j, send=0.2)
        elif k == "bass":
            d = kw["d"]; m_ = int((d + 0.08) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = np.tanh(2.0 * np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * env(m_, 0.004, 0.5) * np.clip((d + 0.04 - tt) / 0.05, 0, 1)
            put(t, x * v * 0.8)
        elif k == "kick":
            m_ = int(0.38 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(48 + 110 * np.exp(-tt / 0.035)) / SR
            put(t, np.sin(ph) * env(m_, 0.001, 0.14) * v)
        elif k == "snare":
            m_ = int(0.28 * SR); tt = np.arange(m_) / SR
            b, a = butter(2, [1200 / (SR / 2), 7000 / (SR / 2)], "band")
            nz = lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.001, 0.08)
            x = nz * 1.4 + 0.4 * np.sin(2 * np.pi * 200 * tt) * env(m_, 0.001, 0.04)
            put(t, x * v * 0.8, send=0.2)
        elif k in ("hat", "ohat"):
            m_ = int((0.06 if k == "hat" else 0.3) * SR); b, a = butter(2, 8000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.001, 0.016 if k == "hat" else 0.12) * v, pan=0.35)
        elif k == "bell":                                        # 8.5-8.9: kalimba-like bell
            m_ = int(3.5 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt / 0.3)
                 + 0.12 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / 0.06)) * env(m_, 0.002, 1.1)
            put(t, x * v * 0.55, pan=-0.3, send=0.3)
            put(t + BEAT * 0.75, x * v * 0.12, pan=0.3)
        elif k == "mallet":                                      # 8.0-8.4: marimba
            m_ = int(1.2 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt / 0.03)
                 + 0.2 * np.sin(2 * np.pi * f * 10.0 * tt) * np.exp(-tt / 0.01)) * env(m_, 0.001, 0.32)
            put(t, x * v * 0.6, pan=0.3, send=0.18)
            put(t + BEAT * 0.5, x * v * 0.14, pan=-0.3)
        elif k == "lead":                                        # 9+: soft pulse lead with vibrato
            m_ = int(1.6 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            ph = 2 * np.pi * np.cumsum(f * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * tt) * np.minimum(1, tt / 0.3))) / SR
            sq = np.sign(np.sin(ph)) * 0.5 + 0.5 * np.sin(ph)
            b, a = butter(1, 3200 / (SR / 2)); x = lfilter(b, a, sq) * env(m_, 0.01, 0.6)
            put(t, x * v * 0.42, pan=0.0, send=0.35)
            for e_ in (1, 2): put(t + e_ * BEAT * 0.75, x * v * 0.42 * 0.35 ** e_, pan=0.4 * (-1) ** e_)
        elif k == "boom":                                        # low thud under the big quakes
            m_ = int(1.4 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(32 + 40 * np.exp(-tt / 0.12)) / SR
            b, a_ = butter(2, 180 / (SR / 2)); nz = lfilter(b, a_, rng.standard_normal(m_)) * env(m_, 0.003, 0.25) * 0.6
            put(t, (np.sin(ph) * env(m_, 0.004, 0.45) + nz) * v)
        elif k == "crash":
            m_ = int(2.2 * SR); b, a = butter(2, 5000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.002, 0.6) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR; b, a = butter(2, 2500 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    def reverb(x):
        out = np.zeros_like(x)
        for dl, g in ((1557, 0.78), (1617, 0.77), (1491, 0.79), (1422, 0.78)):
            y = x.copy()
            for i in range(dl, len(y), dl): y[i:i + dl] += g * y[i - dl:i][:len(y[i:i + dl])]
            out += y * 0.25
        return out
    b, a = butter(1, 4500 / (SR / 2))
    L += lfilter(b, a, reverb(fxL)) * 0.32; R += lfilter(b, a, reverb(np.roll(fxR, 300))) * 0.32
    b, a = butter(2, 12000 / (SR / 2)); L = lfilter(b, a, L); R = lfilter(b, a, R)
    # gentle sidechain pump on the kick
    tt = np.arange(n) / SR; duck = np.ones(n)
    for kt in KICKS:
        i0 = int(kt * SR); i1 = min(n, i0 + int(0.25 * SR))
        if i0 < n: duck[i0:i1] = np.minimum(duck[i0:i1], 1 - 0.22 * np.exp(-np.arange(i1 - i0) / SR / 0.08))
    L *= duck; R *= duck
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
    elif mode == "at":                                             # preview at absolute times
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print([(REC[i]["date"], REC[i]["mag"], round(t, 2), pitch(i)) for i, t in enumerate(RT)])
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
