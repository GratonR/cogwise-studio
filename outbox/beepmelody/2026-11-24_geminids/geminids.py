"""BEEPMELODY — This meteor shower comes from a rock, not a comet. Listen to one night.
Geminids 2026, the peak night 13 -> 14 Dec 2026, seen from 40 N 75 W (US East, EST), 6 PM -> 6 AM, 1 hour = 5 s = 2 bars.
Data: geminids.csv (geminids_data.py) = MODEL of expected meteors per hour for a perfect dark sky:
HR = ZHR(t) x sin(radiant altitude), ZHR 150 at 14 Dec 14h UT (IMO 2026 calendar + IGN), radiant 7h28 +33 (IMO), PyEphem.
EVERY BEEP = 5 SHOOTING STARS (one beep each time the model's running total passes a multiple of 5); the other
meteors are drawn as faint streaks.

Music (rule 2026-11-23, musicality first): loop Dm9 - Bbmaj7 - Fmaj7 - C(add9), 96 BPM, 16th grid.
  - data -> how many notes of a fixed 2-bar motif sound in each hour (the busier the hour, the more of the tune you hear);
    each beep takes the next motif slot by priority, its pitch = the motif's degree in the current chord (1.5 octave max).
  - curve (radiant altitude) -> arrangement: pad filter opens as Gemini climbs; kick, bass, hats, brush snare come in by height.
  - (a) motif, (b) answer variation every odd hour, (c) break = 2 AM bar (Gemini at its highest): drums + bass drop,
    (d) drop = the peak hour 3-4 AM, full kit + octave lead + arpeggio at 3:30 AM. Dawn 5:36: kit stops, D major sunrise chord.
  - subject element: each hour of the night is exactly two bars, and the clock chimes on the hour.

  Rework 24/11 (Guillaume: check every number, explain the set-up at the start, check the visuals: sky rotation, angles):
    - intro explainer card (where we are, 1 hour = 5 s, every beep = 5 shooting stars, the camera follows Gemini);
    - sky: conformal Mercator alt/az view that pans with the radiant (ground and compass turn with it), true constellation
      shapes, meteors on great circles from the radiant, crescent lit on the Sun's side; moonset 8:48 PM (almanac convention).
  Rework r1 24/11 (Guillaume: « les visuels ne collent pas » -> choice « trop compliqué à lire »): fixed view, one sky,
    the radiant in the middle; every beep = one bright meteor out of the radiant + flash + counter; HUD = clock + counter.
    Same data, same music, same timing.
    python3 geminids.py info out | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv, datetime as dt
import numpy as np
from PIL import Image, ImageDraw
import ephem

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx

FXK = float(os.environ.get("PI_FX", "0.5"))

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "geminids.csv"))))
assert len(ROWS) == 145
HL = [18 + i * 5 / 60 for i in range(len(ROWS))]                 # local hour (18.0 .. 30.0)
RATE = [float(r["expected_per_hour"]) for r in ROWS]
CUM = [float(r["cumulative"]) for r in ROWS]
ALT = [float(r["radiant_alt_deg"]) for r in ROWS]
TOTAL_MET = CUM[-1]
LAT, LON, TZ = "40", "-75", -5
DUSK_H, DAWN_H, MOONSET_H = 18 + 12 / 60, 29 + 36 / 60, 20 + 48 / 60   # moonset: almanac convention (upper limb, refraction)
HIGH_H, PEAK_H = 25 + 55 / 60, 27.5
PEAK_RATE = max(RATE)

def interp(arr, h):
    f = (h - 18) * 12; i = int(max(0, min(len(arr) - 2, math.floor(f)))); u = max(0.0, min(1.0, f - i))
    return arr[i] + (arr[i + 1] - arr[i]) * u

# ================= clock =================
BPM = 96; BEAT = 60 / BPM; S16 = BEAT / 4; BAR = 4 * BEAT       # 2.5 s
T0 = BAR                                                         # 6:00 PM at bar 1
def T_of(h): return T0 + (h - 18) * 2 * BAR                     # 1 hour = 2 bars = 5 s
def h_of(T): return 18 + (T - T0) / (2 * BAR)
T_END = T_of(30)                                                 # 6:00 AM
OUTRO = 2 * BAR
TOTAL = T_END + OUTRO                                            # 67.5 s
CUTS = [0, T_of(20), T_of(22.5), T_of(25), T_of(27.5), T_END, TOTAL]
NAMES = ["a", "b", "c", "d", "e", "outro"]
START = {n: CUTS[k] for k, n in enumerate(NAMES)}
DUR = {n: CUTS[k + 1] - CUTS[k] for k, n in enumerate(NAMES)}

def clock(h):
    hh = int(h) % 24; mm = int(round((h - int(h)) * 60))
    if mm == 60: hh, mm = (hh + 1) % 24, 0
    ap = "PM" if 12 <= hh < 24 else "AM"; h12 = hh % 12 or 12
    return f"{h12}:{mm:02d} {ap}"

# ================= beeps (every 5 meteors) =================
BEEP_H = []                                  # local hour at which the running total passes 5, 10, 15 ...
k = 5
for i in range(1, len(ROWS)):
    while CUM[i] >= k - 1e-9:
        f = (k - CUM[i - 1]) / max(1e-9, CUM[i] - CUM[i - 1]); BEEP_H.append(HL[i - 1] + f * 5 / 60); k += 5
NBEEP = len(BEEP_H)

# ================= music plan =================
CHORDS = [  # name, bass root, lead pool (chord tones, 1.5 octave), pad voicing
    ("Dm9", 38, [62, 65, 69, 72, 74, 76, 77, 81], [50, 57, 60, 64, 65]),
    ("Bbmaj7", 34, [62, 65, 69, 70, 72, 74, 77, 81], [46, 53, 57, 62, 60]),
    ("Fmaj7", 41, [65, 67, 69, 72, 76, 77, 79, 81], [53, 57, 60, 64, 67]),
    ("Cadd9", 36, [62, 64, 67, 72, 74, 76, 79, 81], [48, 55, 62, 64, 67]),
]
def chord_at(T): return CHORDS[int(max(0, T) // BAR) % 4]
# 2-bar motif (32 sixteenths): slot -> degree in the chord pool; PRIORITY = order in which slots fill up
MOTIF = {0: 4, 3: 3, 6: 2, 8: 5, 10: 4, 12: 2, 14: 3,
         16: 2, 19: 3, 22: 4, 24: 6, 27: 5, 28: 4, 30: 2,
         2: 1, 5: 2, 9: 4, 11: 3, 13: 1, 15: 2, 18: 1, 21: 2, 25: 6, 26: 5, 29: 3, 31: 1, 4: 2, 7: 3, 17: 2, 20: 3, 23: 5, 1: 4}
PRIORITY = [0, 16, 8, 24, 6, 22, 3, 19, 12, 28, 10, 27, 14, 30, 2, 18, 9, 25, 5, 21, 11, 26, 13, 29, 15, 31, 4, 20, 7, 23, 17, 1]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
BEEPS_T = []                                  # (T, midi, index) of every data beep
def layer_alt(T): return interp(ALT, min(30, max(18, h_of(T))))
BREAK = (T_of(26), T_of(26) + BAR)            # 2:00-2:30 AM, Gemini at its highest (1:55 AM)
DROP = (T_of(27), T_of(28))                   # 3:00-4:00 AM, peak hour
KIT_END = T_of(29.5)                          # last bar before dawn (5:30 AM)
def build():
    # data beeps, hour by hour
    by_hour = {}
    for j, hb in enumerate(BEEP_H): by_hour.setdefault(int(hb), []).append(j)
    for hr, idx in by_hour.items():
        w0 = T_of(hr); slots = sorted(PRIORITY[:len(idx)])
        assert len(idx) <= 32, (hr, len(idx))
        for j, s in zip(idx, slots):
            t = w0 + s * S16; pool = chord_at(t)[2]; deg = MOTIF[s]
            if hr % 2 == 1 and s >= 16: deg = min(7, deg + 1)                  # (b) the answer: one step up
            m = pool[deg]
            ev(t, "bell", m=m, v=0.20, j=j); BEEPS_T.append((t, m, j))
            if DROP[0] <= t < DROP[1]: ev(t, "bell", m=m + 12, v=0.07, j=j)   # (d) octave lead in the peak hour
    # backing loop
    b = 0; t = 0.0
    while t < TOTAL - 0.01:
        name, root, pool, pad = chord_at(t); a = layer_alt(t)
        brk = BREAK[0] <= t < BREAK[1]; kit = t < KIT_END and t >= T0
        if b % 16 == 0:
            ev(t, "pad", ms=pad, d=BAR + 0.3, v=0.05 if t < T_END else 0.0, cut=600 + 3200 * min(1, a / 70))
            if kit and not brk and a >= 15: ev(t, "bass", m=root, d=BEAT * 1.8, v=0.10)
        if b % 16 == 10 and kit and not brk and a >= 15: ev(t, "bass", m=root + 12 if b % 64 >= 48 else root, d=BEAT * 1.2, v=0.08)
        if kit and not brk:
            if b % 8 == 0 and a >= 6: ev(t, "kick", v=0.16 if DROP[0] <= t < DROP[1] else 0.12)
            if b % 2 == 0 and a >= 35: ev(t, "hat", v=0.035 if b % 4 else 0.05)
            if DROP[0] <= t < DROP[1] and b % 2 == 1: ev(t, "hat", v=0.025)
            if b % 8 == 4 and a >= 55: ev(t, "snare", v=0.07)
        b += 1; t = b * S16
    for hh in range(19, 30):                                                 # the clock chimes on the hour
        ev(T_of(hh), "chime", m=74 if hh != 26 else 81, v=0.05)
    ev(BREAK[0], "swell", d=BAR, v=0.06)
    for tt_, mm in ((0.05, 74), (0.30, 81), (0.75, 77)): ev(tt_, "chime", m=mm + 12, v=0.06)   # title sting (not data)
    for j, iv in enumerate([0, 3, 7, 10, 12, 15, 19, 24]):                   # arpeggio on the peak (3:30 AM)
        ev(T_of(PEAK_H) + j * S16, "bell", m=62 + iv, v=0.10, j=-1)
    ev(T_END, "sunrise", ms=[50, 54, 57, 62, 66, 69], d=OUTRO + 0.5, v=0.07)  # D major at dawn
    EV.sort(key=lambda e: e[0])
build()

# ================= sky (rework r1 24/11 : « Trop compliqué à lire ») =================
# Fixed view, one simple sky: no camera pan, no constellation figures. The radiant sits in the middle of the
# picture and every beep is ONE bright meteor bursting out of it (+ a flash at the radiant and the counter ticking up),
# exactly on its note. The other meteors of the model are faint streaks from the same point.
# The sky colour follows the Sun (PyEphem): dusk glow at the start, dawn glow at the end.
OBS = ephem.Observer(); OBS.lat, OBS.lon, OBS.pressure = LAT, LON, 0
SUN = ephem.Sun()
def ut_of(h): return ephem.Date(ephem.Date("2026/12/13 00:00") + (h - TZ) / 24)
_SUNC = {}
def sun_alt(h):
    key = round(h, 2)
    if key not in _SUNC:
        OBS.date = ut_of(h); SUN.compute(OBS); _SUNC[key] = math.degrees(SUN.alt)
    return _SUNC[key]

RX, RY = AW / 2, 126            # radiant (art px): centre of the sky
HZ = 262                         # horizon (art px)
NIGHT_TOP, NIGHT_BOT = (8, 12, 34), (24, 34, 74)
DUSK_TOP, DUSK_BOT = (40, 60, 120), (236, 150, 110)
def mixc(a, b, t): t = max(0, min(1, t)); return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))
def sky_cols(sa):
    f = ease((sa + 18) / 14)          # 0 at -18 (astronomical night), 1 at -4
    return mixc(NIGHT_TOP, DUSK_TOP, f), mixc(NIGHT_BOT, DUSK_BOT, f), f

_r = np.random.RandomState(13)
NSTAR = 230
ST_X = _r.uniform(2, AW - 2, NSTAR); ST_Y = _r.uniform(4, HZ - 8, NSTAR) ** 1.0; ST_B = _r.uniform(0.15, 1.0, NSTAR) ** 2
ST_BIG = _r.rand(NSTAR) < 0.05

# meteors: (T, bright, angle, d0 px, length px)
METEORS = []
_rm = random.Random(14)
for t, m, j in BEEPS_T:
    METEORS.append((t, 1, _rm.uniform(0, 2 * math.pi), _rm.uniform(6, 14), _rm.uniform(48, 78)))
hours = {}
for hb in BEEP_H: hours[int(hb)] = hours.get(int(hb), 0) + 1
for hh in range(18, 30):
    tot = int(round(interp(CUM, hh + 1) - interp(CUM, hh))); faint = max(0, tot - hours.get(hh, 0))
    for _ in range(faint):
        METEORS.append((T_of(hh + _rm.random()), 0, _rm.uniform(0, 2 * math.pi), _rm.uniform(10, 60), _rm.uniform(8, 18)))
METEORS.sort()
MET_T = np.array([m[0] for m in METEORS])
MLIFE = 0.55
BEEP_TS = np.array(sorted(t for t, _, _ in BEEPS_T))

def landscape(d, sunf):
    hill = mixc((14, 18, 30), (60, 52, 70), sunf * 0.6)
    pts = [(x, HZ - 2.5 - 2.5 * math.sin(x * 0.05) - 1.5 * math.sin(x * 0.19)) for x in range(0, AW + 1, 2)]
    d.polygon([(0, HZ)] + pts + [(AW, HZ), (AW, AH), (0, AH)], fill=hill)
    tree = mixc((6, 10, 18), (30, 30, 44), sunf * 0.6)
    for tx, th in ((14, 11), (21, 14), (27, 9), (150, 12), (157, 16), (164, 10)):
        for k in range(th):
            w = (k * 5) // th + 1; y = HZ + 3 - th + k; d.line([tx - w, y, tx + w, y], fill=tree)

def draw_sky(T):
    h = min(30.0, max(18.0, h_of(T))); sa = sun_alt(h)
    top, bot, sunf = sky_cols(sa)
    a = np.zeros((AH, AW, 3), np.uint8)
    for y in range(0, HZ + 1): a[y, :] = mixc(top, bot, (y / HZ) ** 1.6)
    img = Image.fromarray(a); d = ImageDraw.Draw(img)
    vis = 1 - sunf; tw = int(T * 5)
    for k in range(NSTAR):
        b = ST_B[k] * vis
        if b < 0.05: continue
        if (k * 7 + tw) % 19 == 0: b *= 0.55
        c = mixc(top, (255, 250, 230), 0.25 + 0.75 * b); xi, yi = int(ST_X[k]), int(ST_Y[k]); d.point((xi, yi), fill=c)
        if ST_BIG[k]:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): d.point((xi + dx, yi + dy), fill=mixc(top, c, 0.5))
    # radiant: soft glow that pulses on every beep
    i = int(np.searchsorted(BEEP_TS, T + 1e-6)) - 1
    pulse = math.exp(-(T - BEEP_TS[i]) / 0.18) if i >= 0 and T - BEEP_TS[i] >= 0 else 0.0
    if T >= T0:
        for r, w in ((9, 0.10), (6, 0.18), (4, 0.30)):
            d.ellipse([RX - r, RY - r, RX + r, RY + r], fill=mixc(top, (255, 214, 130), (w + 0.5 * pulse * w) * vis + 0.02))
        d.rectangle([RX - 1, RY - 1, RX + 1, RY + 1], fill=mixc(top, (255, 240, 200), 0.6 + 0.4 * pulse))
        if pulse > 0.05:
            rr = 4 + 10 * (1 - pulse)
            d.ellipse([RX - rr, RY - rr, RX + rr, RY + rr], outline=mixc(top, (255, 230, 170), pulse * 0.8))
    # meteors flying straight out of the radiant
    i0 = int(np.searchsorted(MET_T, T - MLIFE)); i1 = int(np.searchsorted(MET_T, T + 1e-6))
    for (tm, br, ang, d0, ln) in METEORS[i0:i1]:
        age = (T - tm) / MLIFE
        if not (0 <= age < 1): continue
        prog = min(1, age / 0.4); fade = 1 - max(0, (age - 0.4) / 0.6)
        ca, sn = math.cos(ang), math.sin(ang)
        head = d0 + ln * prog; tail = max(d0, head - (ln * (0.75 if br else 0.6)))
        n = 10; prev = None
        for s in range(n + 1):
            rr = tail + (head - tail) * s / n; p = (RX + ca * rr, RY + sn * rr)
            if prev is not None:
                kk = ((s / n) ** 1.4) * fade * (1.0 if br else 0.45)
                if br: d.line([prev, p], fill=mixc(top, (255, 200, 120), kk * 0.5), width=3)
                d.line([prev, p], fill=mixc(top, (255, 248, 222) if br else (190, 205, 255), kk), width=2 if br and s > n // 3 else 1)
            prev = p
        if br and prog < 1:
            ex, ey = prev; d.rectangle([ex - 1.5, ey - 1.5, ex + 1.5, ey + 1.5], fill=mixc(top, (255, 255, 240), fade))
    landscape(d, sunf)
    return img, sunf, pulse

# ================= HUD (clock + counter only) =================
INK, INK2 = (236, 232, 220), (150, 160, 196)
HUDBG = (16, 22, 48)
GOLD = (240, 196, 96); BLUE = (140, 180, 255); ROSE = (240, 140, 130)

def hud(c, T, pulse):
    W = c.t; h = min(30.0, max(18.0, h_of(T)))
    W.rectangle([16, 12, 344, 74], fill=HUDBG); W.rectangle([16, 74, 344, 75], fill=GOLD)
    text(W, 26, 22, clock(h), size=40, fill=INK)
    n = int(np.searchsorted(BEEP_TS, T + 1e-6)) * 5
    text(W, 336, 18, f"{n}", size=40, fill=GOLD if pulse < 0.5 else (255, 240, 190), align="r")
    text(W, 336, 54, "SHOOTING STARS", fill=INK2, align="r")
    W.rectangle([16, 600, 344, 632], fill=HUDBG); W.rectangle([16, 600, 344, 601], fill=GOLD)
    text(W, 180, 606, "EVERY BEEP = 5 SHOOTING STARS (EXPECTED)", fill=INK, align="c")

def banner_box(W, yb, tt, sub, big, a, col=GOLD):
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    hgt = (62 if big else 42) if sub else (44 if big else 24)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=HUDBG)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if sub and a > 0.25: text(W, 180, yb + 40, sub, fill=col, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if sub and a > 0.25: text(W, 180, yb + 21, sub, fill=col, align="c")

BY = 430          # under the radiant (radiant at y 252 on the text layer), above the hills
BANNERS = [   # t0, t1, title, sub, big, colour, y
    (9.4, 13.6, "THE RADIANT, IN GEMINI", "EVERY METEOR FLIES OUT FROM THIS POINT", False, GOLD, BY),
    (T_of(MOONSET_H) - 0.4, T_of(21.3) - 0.05, "8:48 PM · THE MOON SETS", "DARK SKY FROM NOW ON", False, BLUE, BY),
    (T_of(21.3), T_of(21.3) + 5.0, "THEIR SOURCE: 3200 PHAETHON", "A ROCKY ASTEROID, NOT A COMET", False, ROSE, BY),
    (T_of(22.5), T_of(22.5) + 4.6, "35 KM/S · 22 MI/S", "EVERY GRAIN HITS THE AIR AT THIS SPEED", False, GOLD, BY),
    (T_of(HIGH_H), T_of(HIGH_H) + 3.2, "1:55 AM", "GEMINI ALMOST OVERHEAD (83°)", True, GOLD, BY),
    (T_of(PEAK_H), T_of(PEAK_H) + 3.6, f"{int(round(PEAK_RATE))} / HOUR", "3:30 AM · THE BUSIEST HOUR", True, GOLD, BY),
    (T_of(DAWN_H), T_END + 0.01, "5:36 AM · DAWN", "THE SKY WINS", False, ROSE, BY),
]
def banner(c, T):
    for t0, t1, tt, sub, big, col, y in BANNERS:
        if t0 <= T < t1: banner_box(c.t, y, tt, sub, big, T - t0, col)

def frame(T):
    img, sunf, pulse = draw_sky(T)
    return Ctx(np.array(img)), pulse

EXPL_END = 9.2
EXPLAIN = [  # line by line while the sky is still almost empty (6-7 PM): how to read the video
    (T0 + 0.0, "ONE PERFECT DARK SKY, US EAST COAST", INK),
    (T0 + 0.0, "THE WHOLE PEAK NIGHT, DUSK TO DAWN", INK2),
    (T0 + 1.6, "1 HOUR = 5 SECONDS", GOLD),
    (T0 + 3.2, "EVERY BEEP = 5 SHOOTING STARS", GOLD),
    (T0 + 3.2, "(THE NUMBER EXPECTED, HOUR BY HOUR)", INK2),
]
def explainer(c, T):
    W = c.t; y0 = 404
    W.rectangle([16, y0, 344, y0 + 120], fill=HUDBG); W.rectangle([16, y0, 344, y0 + 2], fill=GOLD)
    for k, (t0, ln, col) in enumerate(EXPLAIN):
        if T >= t0: text(W, 180, y0 + 10 + k * 20 + (4 if k >= 2 else 0) + (4 if k >= 3 else 0), ln, fill=col, align="c")

def sc_night(name):
    def f(t):
        T = START[name] + t; c, pulse = frame(min(T, T_END)); W = c.t
        if T < T0:
            W.rectangle([16, 12, 344, 170], fill=HUDBG); W.rectangle([16, 12, 344, 14], fill=GOLD)
            text(W, 28, 20, "IT COMES FROM", size=40, fill=INK)
            if T > 0.25: text(W, 28, 56, "A ROCK,", size=40, fill=GOLD)
            if T > 0.7: text(W, 28, 92, "NOT A COMET.", size=40, fill=INK)
            if T > 1.3: text(W, 28, 138, "THE GEMINIDS. ONE NIGHT OF THEM.", fill=BLUE)
        else:
            hud(c, T, pulse)
        if T0 <= T < EXPL_END: explainer(c, T)
        banner(c, T)
        return c
    return f

def sc_outro(t):
    T = T_END + t; c, _ = frame(T_END); W = c.t
    W.rectangle([16, 40, 344, 372], fill=HUDBG); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "ONE NIGHT OF GEMINIDS", fill=INK2, align="c")
    if t > 0.15:
        text(W, 180, 74, f"≈ {int(round(TOTAL_MET, -1))}", size=40, fill=GOLD, align="c")
        text(W, 180, 112, "SHOOTING STARS, DUSK TO DAWN", fill=INK, align="c")
    if t > 0.7:
        text(W, 180, 144, "FROM GRAINS OF ROCK", fill=INK, align="c")
        text(W, 180, 162, "SHED BY ASTEROID 3200 PHAETHON", fill=ROSE, align="c")
    if t > 1.3:
        text(W, 180, 196, "NEXT PEAK: NIGHT OF DEC 13-14", size=20, fill=GOLD, align="c")
        text(W, 180, 216, "WHERE WILL YOU WATCH FROM?", fill=INK, align="c")
    if t > 1.8:
        for k, ln in enumerate(["MODEL: ZHR 150, PEAK DEC 14 14:00 UT", "(IMO 2026 CALENDAR, IGN), X SIN(RADIANT", "HEIGHT) AT 40°N 75°W, PERFECT DARK", "SKY, DUSK TO DAWN. REAL COUNTS VARY."]):
            text(W, 180, 262 + 18 * k, ln, fill=INK2, align="c")
    return c

SCENEFN = {n: sc_night(n) for n in NAMES[:-1]}; SCENEFN["outro"] = sc_outro

def compose_light(c):
    art = np.array(c.art); big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt); tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

MOMENTS = [T_of(PEAK_H)]
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(SCENEFN[name](t))
    for m in MOMENTS:
        if 0 <= T - m < 0.2:
            a = T - m; s = int(round(6 * FXK * math.exp(-a / 0.06) * math.sin(a * 90))); fr = np.roll(fr, s, axis=0)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.6)) / 0.6)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    if name == "a":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

# ================= audio =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def env(n, a, dec):
        t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t * dec)
    def bell(f, dur):           # glassy FM bell, soft attack, no harsh top
        n = int(dur * SR); t = np.arange(n) / SR
        mod = 1.2 * np.exp(-t * 6) * np.sin(2 * np.pi * f * 3.5 * t)
        x = np.sin(2 * np.pi * f * t + mod) * env(n, .004, 3.2) + .25 * np.sin(2 * np.pi * f * 2 * t) * env(n, .002, 9)
        return lowpass(x, 3500)
    def softsynth(f, dur, dec, a=.02):
        n = int(dur * SR); t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * d * t) for d in (.996, 1.004)) / 2 + .2 * np.sin(2 * np.pi * 2 * f * t)
        return s * env(n, a, dec)
    rng = np.random.RandomState(4)
    n = int((TOTAL + 2.5) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(t, x, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(x)); L[i:j] += x[:j - i] * (1 - pan) ** .5 * .9; R[i:j] += x[:j - i] * (1 + pan) ** .5 * .9
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if v <= 0: continue
        if k == "bell":
            pan = ((kw["j"] * 37) % 11 - 5) / 9 if kw["j"] >= 0 else 0
            put(t, v * bell(mtof(kw["m"]), 1.4), pan)
        elif k == "pad":
            d = kw["d"]; m_ = int((d + .4) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .35) * np.clip((d + .3 - tt) / .5, 0, 1)
            x = sum(softsynth(mtof(mm), d + .4, 0, .3) for mm in kw["ms"]) / 3 * e
            put(t, v * lowpass(x, kw["cut"]))
        elif k == "bass":
            put(t, v * lowpass(softsynth(mtof(kw["m"]), kw["d"], 1.5, .01), 400))
        elif k == "kick":
            m_ = int(.3 * SR); tt = np.arange(m_) / SR; f = 50 + 70 * np.exp(-tt * 30)
            put(t, v * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9))
        elif k == "hat":
            m_ = int(.05 * SR); put(t, v * highpass(rng.randn(m_), 6000) * np.exp(-np.arange(m_) / SR * 70), .3)
        elif k == "snare":
            m_ = int(.22 * SR); tt = np.arange(m_) / SR
            put(t, v * lowpass(highpass(rng.randn(m_), 900), 5000) * np.exp(-tt * 18), -.15)
        elif k == "chime":
            m_ = int(2.5 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"] - 24)
            x = (np.sin(2 * np.pi * f * tt) + .5 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 3)) * np.exp(-tt * 1.6)
            put(t, v * x)
        elif k == "swell":
            d = kw["d"]; m_ = int((d + .5) * SR); tt = np.arange(m_) / SR
            e = np.clip(tt / d, 0, 1) ** 2 * np.clip((d + .4 - tt) / .4, 0, 1)
            put(t, v * lowpass(rng.randn(m_), 1800) * e)
        elif k == "sunrise":
            d = kw["d"]; m_ = int((d + .5) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .6) * np.clip((d - tt) / 1.6, 0, 1)
            put(t, v * lowpass(sum(softsynth(mtof(mm), d + .5, 0, .5) for mm in kw["ms"]) / 3 * e, 2600))
    def reverb(x, mix=.38):
        out = x.copy()
        for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
            k_ = int(dl * SR); out[k_:] += g * .6 * x[:-k_]
        return (1 - mix) * x + mix * lowpass(out, 3800)
    L = reverb(np.tanh(L * 1.3) / 1.3); R = reverb(np.roll(np.tanh(R * 1.3) / 1.3, int(.013 * SR)))
    tt = np.arange(n) / SR; fade = np.clip((TOTAL - tt) / 1.2, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max()); st = np.stack([L, R], 1) / mx * .89
    st = st[:int(TOTAL * SR)]
    wavfile.write(path, SR, (st * 32767).astype(np.int16)); print(path, round(len(st) / SR, 2), "s")

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
    if mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(DUR[n], 2) for n in NAMES}, Counter(k for _, k, _ in EV))
        print("beeps", NBEEP, "meteors drawn", len(METEORS), "total model", TOTAL_MET, "peak", PEAK_RATE)
        per = Counter(int(h) for h in BEEP_H); print("beeps per hour", sorted(per.items()))
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
