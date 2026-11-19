"""BEEPMELODY — EVERY SUPERMOON SINCE 1900, AS MUSIC.
506 supermoons, 1900 -> 24 Nov 2026 (Espenak / Nolle rule: full moon within 90 % of its orbit's perigee).
Scene: Earth, sunlight from the left, the Moon shown at EVERY full moon (one full moon ~ one frame) on a schematic
oval orbit (not to scale). The oval turns once per 411.8 days (full moon / perigee beat): each time its near end swings
onto the full-moon point -> supermoon -> flash + note (closer = higher). Timeline strip at the bottom fills with ticks.
End: 24 Nov 2026 flashes, 3 ghost notes (Dec 2026, Jan 2027, Feb 2027) -> "1ST OF 4 IN A ROW".
Clock: 1 year = 0.45 s. Music (co-pilot step 2, choice B "Maree"): 118.3 BPM locked to the 411.8-day cycle,
kick on every packet, offbeat hats, rolling bass, supermoons = bright plucks, closest ones add a sub drop.
Data: supermoons_draft.csv (JPL DE421 via Skyfield, cross-checked PyEphem <= 2.9 km and Espenak tables <= 4 km).
Palette: SM_PAL=night (default) | light.

    python3 supermoons.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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

FXK = float(os.environ.get("PI_FX", "0.6"))
PAL = os.environ.get("SM_PAL", "night")

# ================= data =================
def yfrac(s):
    t = dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
    return t.year + ((t - dt.datetime(t.year, 1, 1)).total_seconds() / 86400) / 365.25
ALL = list(csv.DictReader(open(os.path.join(HERE, "supermoons_draft.csv"))))
for r in ALL:
    r["y"] = yfrac(r["full_moon_utc"]); r["d"] = float(r["dist_km"]); r["rel"] = float(r["rel_dist"])
    r["sm"] = r["espenak90"] == "1"; r["close"] = r["close3568"] == "1"
END_DATE = "2026-11-24 14:54"
FM = [r for r in ALL if r["full_moon_utc"] <= END_DATE]           # every full moon shown on screen
SM = [r for r in FM if r["sm"]]                                  # the notes
GHOST = [r for r in ALL if r["full_moon_utc"] > END_DATE and r["sm"]][:3]
N = len(SM)
assert N == 506 and SM[-1]["full_moon_utc"] == END_DATE and len(GHOST) == 3
MI = 1.609344
MON = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
def fdate(r):
    y, m, d = r["full_moon_utc"][:10].split("-"); return f"{MON[int(m) - 1]} {int(d)}, {y}"
def km(d): return f"{int(round(d)):,} KM"
def mi(d): return f"{int(round(d / MI)):,} MI"

# ================= palette =================
if PAL == "light":
    BG0, BG1 = (238, 242, 250), (214, 224, 242)
    INK, INK2 = (34, 44, 78), (98, 110, 146)
    PANEL, PANEL2 = (252, 248, 238), (246, 246, 250)
    ORBIT, STAR = (150, 162, 196), None
    MOONC, MOONS = (250, 246, 228), (214, 210, 196)
else:
    BG0, BG1 = (14, 18, 44), (30, 26, 70)
    INK, INK2 = (236, 238, 250), (150, 158, 200)
    PANEL, PANEL2 = (22, 26, 60), (28, 32, 72)
    ORBIT, STAR = (84, 92, 150), (200, 206, 240)
    MOONC, MOONS = (250, 246, 228), (206, 200, 182)
GOLD = (246, 186, 64)
FLASH = (255, 255, 255) if PAL != "light" else (240, 104, 84)
CORAL = (240, 104, 84)
CYAN = (110, 210, 236)
EARTH, EARTH2, LAND = (60, 120, 210), (30, 62, 120), (90, 170, 110)

# ================= timeline =================
YEAR_S = 0.45
Y0 = 1900.0
T0 = 3.5                                                         # data clock starts after the intro
def T_of(y): return T0 + (y - Y0) * YEAR_S
def y_of_T(T): return Y0 + (T - T0) / YEAR_S
SYN = 411.78                                                     # days: full moon / perigee beat period
BEAT = SYN / 365.25 * YEAR_S                                     # 0.5073 s -> 118.3 BPM
for r in SM: r["T"] = T_of(r["y"])
RT = [r["T"] for r in SM]
T_END = RT[-1]
HOLD_B, OUTRO_B = 7, 11
TOTAL = T_END + (HOLD_B + OUTRO_B) * BEAT
GT = [T_END + (k + 1) * BEAT for k in range(3)]                  # ghost notes on the next three beats

# packet phase: fit the 411.78-day cycle to the data (max of sum rel*cos)
_ys = np.array([r["y"] for r in FM]); _rel = np.array([r["rel"] for r in FM])
_P = SYN / 365.25
_ph = np.linspace(0, 2 * np.pi, 720, endpoint=False)
_score = [(_rel * np.cos(2 * np.pi * _ys / _P - p)).sum() for p in _ph]
PH0 = _ph[int(np.argmax(_score))]                                # packet centres where 2*pi*y/P - PH0 = 0 mod 2pi
def cyc(y): return 2 * np.pi * y / _P - PH0                       # angle of the perigee vs the full-moon point
_k0 = math.ceil((cyc(Y0) - 0) / (2 * np.pi))
Y_BEAT0 = (PH0 + 2 * np.pi * _k0) * _P / (2 * np.pi)             # first packet centre >= 1900
T_BEAT0 = T_of(Y_BEAT0) - BEAT * math.ceil((T_of(Y_BEAT0) - 0.1) / BEAT)

def per(name):
    y0, y1 = {"d1": (1900, 1932), "d2": (1932, 1964), "d3": (1964, 1996), "d4": (1996, None)}[name]
    return T_of(y0), (T_of(y1) if y1 else T_END + HOLD_B * BEAT)
SC = [("intro", T0)] + [(n, per(n)[1] - per(n)[0]) for n in ("d1", "d2", "d3", "d4")] + [("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
assert abs(acc_ - TOTAL) < 1e-6

def sm_index(T):
    return int(np.searchsorted(RT, T, side="right")) - 1

FM_Y = np.array([r["y"] for r in FM]); FM_D = np.array([r["d"] for r in FM])
def fm_state(T):
    """distance (km) and perigee angle of the latest full moon at time T (one full moon ~ one frame, no interpolation,
    so the Moon on screen is exactly the supermoon when its note plays)"""
    y = y_of_T(T)
    i = max(0, min(len(FM) - 1, int(np.searchsorted(FM_Y, y + 1e-9, side="right")) - 1))
    return FM_D[i], cyc(FM_Y[i])

# ================= geometry (art layer 180 x 320) =================
EX, EY, ER = 66, 176, 9                                          # Earth
D_LO, D_HI = 356000.0, 407000.0
RP, RA = 46.0, 100.0                                             # schematic perigee / apogee radius (px)
def rpx(dkm): return RP + (dkm - D_LO) / (D_HI - D_LO) * (RA - RP)
A_ = (RP + RA) / 2; E_ = (RA - RP) / (RA + RP); P_ = A_ * (1 - E_ * E_)
def orbit_r(theta, phi): return P_ / (1 + E_ * math.cos(theta - phi))
def phi_for(dkm, c):
    """orientation of the oval so that its full-moon point (theta = 0) sits exactly at the real distance"""
    r = max(RP + 0.01, min(RA - 0.01, rpx(dkm)))
    a = math.acos(max(-1, min(1, (P_ / r - 1) / E_)))
    s = math.sin(c)
    return a if s >= 0 else -a

_STARS = [(random.Random(s).uniform(0, AW), random.Random(s + 9).uniform(90, 262), random.Random(s + 77).random()) for s in range(140)]
_BG = {}
def background():
    if PAL in _BG: return _BG[PAL].copy()
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        f = y / AH; a[y, :] = [BG0[j] * (1 - f) + BG1[j] * f for j in range(3)]
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    if STAR:
        for x, y, r in _STARS:
            q = 0.25 + 0.6 * r; col = tuple(int(a[int(y), int(x), j] * (1 - q) + STAR[j] * q) for j in range(3))
            d.point((int(x), int(y)), fill=col)
    # sunlight from the left
    for k in range(5):
        y = 120 + k * 26
        for x in range(4, 16, 3): d.point((x, y), fill=GOLD)
        d.polygon([(16, y - 2), (19, y), (16, y + 2)], fill=GOLD)
    _BG[PAL] = img
    return img.copy()

def earth(d):
    d.ellipse([EX - ER, EY - ER, EX + ER, EY + ER], fill=EARTH2)
    d.chord([EX - ER, EY - ER, EX + ER, EY + ER], 90, 270, fill=EARTH)
    d.rectangle([EX - 5, EY - 4, EX - 2, EY - 1], fill=LAND); d.rectangle([EX - 3, EY + 2, EX, EY + 5], fill=LAND)
    d.point((EX + 3, EY - 3), fill=(60, 110, 90))

def moon(d, x, y, r, col=MOONC):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    d.ellipse([x - r * 0.5, y - r * 0.4, x - r * 0.1, y], fill=MOONS)
    d.ellipse([x + r * 0.15, y + r * 0.2, x + r * 0.45, y + r * 0.5], fill=MOONS)

def draw_scene(c, T, ghosts=0):
    c.art = background(); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    dkm, cy_ = fm_state(T)
    phi = phi_for(dkm, cy_)
    # the oval orbit (schematic), the supermoon arc (within 90 % of perigee) in gold
    r90 = RA - 0.9 * (RA - RP)
    pts = []
    for k in range(0, 360, 2):
        th = math.radians(k); r = orbit_r(th, phi)
        x, y = EX + r * math.cos(th), EY - r * math.sin(th) * 0.62
        pts.append((x, y, r <= r90 + 0.5))
    for x, y, hot in pts:
        if 88 < y < 262 and 0 <= x < AW: d.point((int(x), int(y)), fill=GOLD if hot else ORBIT)
    # perigee marker
    xp, yp = EX + RP * math.cos(phi), EY - RP * math.sin(phi) * 0.62
    d.rectangle([int(xp) - 1, int(yp) - 1, int(xp) + 1, int(yp) + 1], fill=GOLD)
    # Earth-Moon line
    xm = EX + rpx(dkm); ym = EY
    for x in range(EX + ER + 2, int(xm) - 10, 3): d.point((x, EY), fill=ORBIT)
    earth(d)
    k = sm_index(T)
    age = T - RT[k] if k >= 0 else 9
    rmoon = 6.0 + 4.0 * (RA - rpx(dkm)) / (RA - RP)                 # exaggerated apparent size
    hot = k >= 0 and age < 0.22 and ghosts == 0
    moon(d, xm, ym, rmoon, MOONC if not hot else (255, 252, 236))
    if k >= 0 and age < 0.5 and ghosts == 0:
        rr = rmoon + 2 + age * 46; col = GOLD if SM[k]["close"] else (255, 255, 255)
        d.ellipse([xm - rr, ym - rr * 0.9, xm + rr, ym + rr * 0.9], outline=col if age < 0.3 else ORBIT)
        if SM[k]["close"] and age < 0.35:
            rr2 = rr * 0.6; d.ellipse([xm - rr2, ym - rr2, xm + rr2, ym + rr2], outline=GOLD)
    # scene labels (text layer 360 x 640)
    text(W, 8, 196, "SUN", fill=GOLD)
    text(W, EX * 2, EY * 2 + 22, "EARTH", fill=INK2, align="c")
    text(W, 352, 186, "NOT TO SCALE", fill=INK2, align="r")
    lab = "FULL MOON"
    text(W, int(xm * 2), int((ym + rmoon) * 2) + 6, lab, fill=INK2 if not hot else INK, align="c")
    text(W, int(xm * 2), int((ym + rmoon) * 2) + 24, km(dkm), fill=INK2, align="c")

# ================= timeline strip (text layer) =================
FX0, FX1, FY = 24, 336, 596
def fx(y): return FX0 + (y - Y0) / (2027.3 - Y0) * (FX1 - FX0)
def strip(c, T, ghosts=0):
    W = c.t; k = sm_index(T)
    W.rectangle([0, 526, 360, 640], fill=PANEL); W.rectangle([0, 526, 360, 527], fill=ORBIT)
    for yy, lab in ((1900, "1900"), (1950, "1950"), (2000, "2000")):
        x = fx(yy); W.line([x, FY + 2, x, FY + 6], fill=INK2); text(W, x, FY + 8, lab, fill=INK2, align="c")
    W.line([FX0, FY + 1, FX1, FY + 1], fill=INK2)
    for i in range(k + 1):
        r = SM[i]; x = int(fx(r["y"]))
        h = 4 + 34 * max(0.0, (363500 - r["d"]) / (363500 - 356300))
        fresh = T - RT[i] < 0.25 and ghosts == 0
        W.line([x, FY, x, FY - h], fill=FLASH if fresh else (GOLD if r["close"] else CYAN))
    for g in range(ghosts):
        r = GHOST[g]; x = int(fx(r["y"])) + 2 * (g + 1)
        h = 4 + 34 * max(0.0, (363500 - r["d"]) / (363500 - 356300))
        for yy in range(int(FY - h), FY, 3): W.point((x, yy), fill=INK)
    if ghosts == 0 and k < N - 1:
        x = fx(min(y_of_T(T), SM[-1]["y"])); W.line([x, FY - 44, x, FY + 1], fill=CORAL)
    text(W, 12, 532, f"SUPERMOONS: {k + 1}", fill=INK)
    text(W, 180, 620, "TALLER TICK = CLOSER MOON = HIGHER NOTE", fill=INK2, align="c")

def hud(c, T):
    W = c.t; k = sm_index(T)
    W.rectangle([16, 18, 344, 122], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=GOLD); W.rectangle([16, 121, 344, 122], fill=GOLD)
    yr = int(min(y_of_T(T), SM[-1]["y"]))
    if k < 0:
        text(W, 28, 22, "WAITING FOR A SUPERMOON", fill=INK2); text(W, 334, 44, str(yr), size=40, fill=GOLD, align="r"); return
    r = SM[k]; age = T - RT[k]
    col = GOLD if r["close"] else INK
    text(W, 28, 22, f"SUPERMOON #{k + 1}", fill=GOLD if r["close"] else CYAN)
    text(W, 28, 44, km(r["d"]), size=40, fill=col if age > 0.2 else FLASH)
    text(W, 28, 92, mi(r["d"]) + "  · AT FULL MOON", fill=INK2)
    text(W, 334, 44, str(yr), size=40, fill=GOLD, align="r")
    text(W, 334, 22, fdate(r)[:-6], fill=INK2, align="r")
    text(W, 334, 92, f"OF {N}", fill=INK2, align="r")

def firstk(pred): return next(i for i, r in enumerate(SM) if pred(r))
K1912 = firstk(lambda r: r["full_moon_utc"].startswith("1912-01-04"))
K1948 = firstk(lambda r: r["full_moon_utc"].startswith("1948-01-26"))
K2016 = firstk(lambda r: r["full_moon_utc"].startswith("2016-11-14"))
KPACK = firstk(lambda r: r["y"] > 1903.5)
BANNERS = {KPACK: ("THEY COME IN PACKETS", "ONE EVERY 411.8 DAYS = THE BEAT", False),
           K1912: ("CLOSEST SINCE 1900", "JAN 4, 1912 · 356,375 KM", True),
           K1948: ("CLOSEST UNTIL 2034", "JAN 26, 1948", False),
           K2016: ("CLOSEST SINCE 1948", "NOV 14, 2016", True)}
def banner(c, T, ghosts=0):
    W = c.t
    if T >= T_END:
        a = T - T_END
        if a < 0.1: return
        tt, sub = "NOV 24, 2026", ""
        if a > 1.0 * BEAT: tt = "1ST OF 4 IN A ROW"
        if a > 1.0 * BEAT: sub = "NEXT: DEC 24 · JAN 22 · FEB 20"
        w = 16 * len(tt) + 30; yb = 446
        W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 62], fill=PANEL); W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=GOLD)
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if sub: text(W, 180, yb + 40, sub, fill=GOLD, align="c")
        return
    k = sm_index(T)
    best = None
    for kb in BANNERS:
        if kb <= k and 0.1 < T - RT[kb] < 2.2: best = kb
    if best is None: return
    tt, sub, big = BANNERS[best]; a = T - RT[best]; yb = 446
    w = max((16 if big else 8) * len(tt), 8 * len(sub)) + 30
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + (62 if big else 42)], fill=PANEL)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=GOLD if big else CYAN)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if a > 0.3: text(W, 180, yb + 40, sub, fill=GOLD, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if a > 0.3: text(W, 180, yb + 21, sub, fill=CYAN, align="c")

def ghosts_at(T):
    return sum(1 for g in GT if T >= g)

def sc_intro(t):
    T = t; c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, T0); strip(c, T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=GOLD); W.rectangle([16, 171, 344, 172], fill=GOLD)
    text(W, 28, 26, "EVERY SUPERMOON", size=40, fill=INK)
    if t > 0.35: text(W, 28, 64, "SINCE 1900", size=40, fill=GOLD)
    if t > 0.9: text(W, 28, 112, "EVERY BEEP = ONE SUPERMOON", fill=INK)
    if t > 1.5: text(W, 28, 140, "CLOSER MOON = HIGHER NOTE", fill=CYAN)
    if t > 2.1:
        W.rectangle([46, 420, 314, 482], fill=PANEL); W.rectangle([46, 420, 314, 422], fill=CYAN)
        text(W, 180, 424, "SUPERMOON = A FULL MOON", fill=INK, align="c")
        text(W, 180, 444, "WITHIN 90 % OF ITS CLOSEST", fill=INK, align="c")
        text(W, 180, 462, "POINT TO EARTH", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t; g = ghosts_at(T)
        c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, min(T, T_END), g); strip(c, min(T, T_END) if g == 0 else T_END, g)
        hud(c, min(T, T_END)); banner(c, T, g)
        if T >= T_END:                                            # ghost moons on the orbit
            W = c.t
            for j in range(g):
                x = 250 + j * 34; yv = 290
                c.a.ellipse([x / 2 - 5, yv / 2 - 5, x / 2 + 5, yv / 2 + 5], outline=INK)
                text(W, x, yv + 14, ["DEC", "JAN", "FEB"][j], fill=INK, align="c")
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, T_END, 3); strip(c, T_END, 3)
    W = c.t
    W.rectangle([16, 40, 344, 330], fill=PANEL); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "SINCE 1900", fill=INK2, align="c")
    if t > 0.3: text(W, 180, 74, f"{N} SUPERMOONS", size=40, fill=INK, align="c")
    c1 = SM[K1912]
    if t > 1.2:
        text(W, 180, 132, "CLOSEST: JAN 4, 1912", fill=GOLD, align="c")
        text(W, 180, 152, f"{km(c1['d'])} · {mi(c1['d'])}", fill=INK, align="c")
    if t > 2.2:
        text(W, 180, 190, "CLOSEST COMING UP: NOV 25, 2034", fill=INK2, align="c")
        text(W, 180, 210, f"{km(356445.7)} · {mi(356445.7)}", fill=INK, align="c")
    if t > 3.2: text(W, 180, 270, "WHICH ONE WAS YOUR BIRTHDAY?", fill=CYAN, align="c")
    if t > 3.6:
        W.rectangle([16, 400, 344, 470], fill=PANEL)
        text(W, 180, 406, "RULE: F. ESPENAK / R. NOLLE (90 %).", fill=INK2, align="c")
        text(W, 180, 426, "DATA: NASA JPL DE421 EPHEMERIS,", fill=INK2, align="c")
        text(W, 180, 446, "CHECKED WITH ESPENAK TABLES", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "d1": sc_main("d1"), "d2": sc_main("d2"), "d3": sc_main("d3"), "d4": sc_main("d4"), "outro": sc_outro}

def compose_layers(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tb = np.repeat(np.repeat(np.array(c.txt), 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

BEATS = [T_BEAT0 + i * BEAT for i in range(int((TOTAL - T_BEAT0) / BEAT) + 1)]
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    c = SCENEFN[name](t)
    fr = compose_layers(c)
    if T < T_END + HOLD_B * BEAT:
        bi = int(np.searchsorted(BEATS, T, side="right")) - 1
        kp = math.exp(-(T - BEATS[bi]) / 0.08) if bi >= 0 else 0.0
        z = 1.0 + 0.008 * kp * FXK
        if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = sm_index(T)
    if k >= 0 and SM[k]["close"] and 0 <= T - RT[k] < 0.10:
        fr = np.minimum(255, fr.astype(np.int16) + int(45 * FXK * (1 - (T - RT[k]) / 0.10))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    return fr

# ================= audio (choice B "Maree", from supermoons_moods.py mood_b) =================
SR = 44100
PENT = [0, 2, 4, 7, 9]
def pitch(dkm, base=69, scale=PENT):
    x = np.clip((362500 - dkm) / (362500 - 356400), 0, 1)
    k = int(round(x * (2 * len(scale) - 1)))
    return base + 12 * (k // len(scale)) + scale[k % len(scale)]
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def env(n, a, d):
        t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    L = np.zeros(int((TOTAL + 1.0) * SR))
    def put(t, sig, g=1.0):
        i = int(t * SR); j = min(len(L), i + len(sig))
        if 0 <= i < len(L): L[i:j] += g * sig[:j - i]
    def noise(dur, fc, dec, seed, hp=None):
        n = int(dur * SR); s = lowpass(np.random.RandomState(seed).randn(n), fc)
        if hp: s = highpass(s, hp)
        return s * np.exp(-np.arange(n) / SR * dec)
    def kick(g=.22, f0=80, f1=46):
        n = int(.35 * SR); tt = np.arange(n) / SR
        return g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+f1)/SR) * np.exp(-tt*12)
    def pluck(f, dec=.25):
        n = int(.8 * SR); tt = np.arange(n) / SR
        s = sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
        return s * env(n, .002, dec)
    s8 = BEAT / 2; roots = [38, 38, 34, 36]
    T_DRUMS_OFF = T_END + HOLD_B * BEAT + 2 * BEAT
    for k, b in enumerate(BEATS):
        if b > TOTAL: break
        g = 1.0 if b < T_DRUMS_OFF else max(0.0, 1 - (b - T_DRUMS_OFF) / (4 * BEAT))
        intro = b < T0 - 2 * BEAT
        if g > 0:
            put(b, kick(.22 * g * (0.6 if intro else 1)))
            put(b + s8, noise(.05, 9000, 90, 70 + k, 5000), .04 * g)
            if k % 2 and not intro: put(b, noise(.15, 6000, 25, 40 + k, 900), .05 * g)
        r = roots[(k // 4) % 4]; nn = int(s8 * .9 * SR); tt = np.arange(nn) / SR
        gb = 1.0 if b < T_END + HOLD_B * BEAT else max(0.0, 1 - (b - T_END - HOLD_B * BEAT) / (OUTRO_B * BEAT))
        put(b + s8, .09 * gb * lowpass(np.sin(2*np.pi*mtof(r)*tt) + .3*np.sign(np.sin(2*np.pi*mtof(r)*tt)), 500) * np.exp(-tt * 5))
    put(0.10, .15 * pluck(mtof(81), .4))                          # first note immediately
    for r in SM:
        put(r["T"], .15 * pluck(mtof(pitch(r["d"])), .25))
        if r["close"]:
            nn = int(.7 * SR); tt = np.arange(nn) / SR
            put(r["T"], .18 * np.sin(2*np.pi*np.cumsum(mtof(38)*(1 + .6*np.exp(-tt*9)))/SR) * np.exp(-tt * 3))
    for g, r in zip(GT, GHOST):                                    # ghost notes: softer, echoed
        put(g, .09 * pluck(mtof(pitch(r["d"])), .45)); put(g + .19, .04 * pluck(mtof(pitch(r["d"])), .45))
    for j, d_ in enumerate([0, 4, 7, 12]):                         # little rising arp on the final note
        put(T_END + (j + 1) * BEAT / 4, .10 * pluck(mtof(pitch(SM[-1]["d"]) + d_), .35))
    out = L.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
        n = int(dl * SR); out[n:] += g * .6 * L[:-n]
    x = .8 * L + .2 * lowpass(out, 4000)
    tt = np.arange(len(x)) / SR; x *= np.clip((TOTAL + 0.3 - tt) / 1.5, 0, 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(len(x) / SR, 2), "s")

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
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}_{PAL}.png")
    elif mode == "info":
        print("total", round(TOTAL, 2), "s ·", N, "supermoons · beat", round(BEAT, 4), "s =", round(60 / BEAT, 1), "BPM")
        print({n: round(d, 2) for n, d in SC})
        print("T 1912", round(RT[K1912], 2), "T 1948", round(RT[K1948], 2), "T 2016", round(RT[K2016], 2), "T end", round(T_END, 2), "ghosts", [round(g, 2) for g in GT])
        print("closest-list", sum(r["close"] for r in SM), "packet phase year", round(Y_BEAT0, 3))
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
