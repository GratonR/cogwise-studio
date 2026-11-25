"""BEEPMELODY — 7 planets, one star, and their orbits form a chord.
TRAPPIST-1 seen from above. EVERY BEEP = ONE TRANSIT (a planet crossing in front of its star, seen from Earth).
Data: trappist_chord.csv — periods (Agol et al. 2021, PSJ 2:1, Table 2; checked vs Gillon 2017 / Luger 2017) and one
transit time per planet (t0, BJD_TDB-2450000, Agol 2021 Table 2; checked: b vs Gillon 2017 T0 7322.51736 -> 0.0014 d,
h vs Gillon/Luger single transit ~7662.55 -> 0.06 d). Linear ephemeris t0 + n P (TTVs of minutes are far below the 16th grid).
Window: 72 days starting BJD 7271.33 (2015), placed so that the real 5-planet pile-up (b c e g h within 1 day, BJD 7343.2)
lands on the drop.

Music (co-pilot 2/4: B · synthwave orbitale, 112 BPM; rule 2026-11-23 musicality first):
  loop C – G/B – Am7 – G (bass C, B, A, G), 8th-note octave bass, gated kick/snare, 16th grid.
  data -> each planet owns ONE pitch from its period-ratio chain stacked from h (ratios rounded, octaves folded):
          h C3 · g G3 · f C4 · e G4 · d D5 · c B4 · b G5. Chord of the data = C·D·G·B, fits every chord of the loop.
  curve (time speed, days per second) -> arrangement: kick+bass, then snare+hats, then 16th arp in the drop.
  (a) motif = the planets' own rhythm on the loop, (b) faster time = the same voices, denser, (c) break = bar 21,
  drums out, (d) drop = the 5-planet pile-up + C·D·G·B arpeggio, then the whole chord held.
  Subject element: the harmony IS the data (the period ratios), each voice's rhythm is its real orbit.
    python3 trappist_chord.py info out | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx

FXK = float(os.environ.get("PI_FX", "0.5"))

# ================= data =================
ROWS = {r["planet"]: r for r in csv.DictReader(open(os.path.join(HERE, "trappist_chord.csv")))}
PL = ["h", "g", "f", "e", "d", "c", "b"]                      # order of entry (low voice -> high voice)
P = {p: float(ROWS[p]["period_d"]) for p in PL}
A_AU = {p: float(ROWS[p]["semi_major_axis_au"]) for p in PL}
T0B = {p: float(ROWS[p]["t0_bjd"]) for p in PL}
PITCH = {"h": 48, "g": 55, "f": 60, "e": 67, "d": 74, "c": 71, "b": 79}
NOTE = {"h": "C3", "g": "G3", "f": "C4", "e": "G4", "d": "D5", "c": "B4", "b": "G5"}
RATIO = {"c": "8:5", "d": "5:3", "e": "3:2", "f": "3:2", "g": "4:3", "h": "3:2"}
PILEUP_BJD = 7343.2                                            # just before the b c e g h pile-up (checked in info)

# ================= clock =================
BPM = 112; BEAT = 60 / BPM; S16 = BEAT / 4; BAR = 4 * BEAT       # 2.143 s
def B(n): return n * BAR
T_TUNE, T_PLAY, T_BREAK, T_DROP, T_CHORD, T_OUT, TOTAL = B(2), B(6), B(21), B(22), B(27), B(29), B(32)   # 68.57 s
# time speed (days per second) knots: smooth ramp, the curve that drives the arrangement
KN = [(T_PLAY, 0.75), (B(13), 0.95), (B(14), 1.5), (B(20.5), 1.7), (T_DROP, 2.9), (T_CHORD, 2.9), (T_CHORD + BAR, 0.0), (TOTAL, 0.0)]
_TT = np.arange(0, TOTAL + 1, 0.001)
_V = np.interp(_TT, [k[0] for k in KN], [k[1] for k in KN]) * (_TT >= T_PLAY)
_DAY = np.concatenate([[0], np.cumsum((_V[1:] + _V[:-1]) / 2 * 0.001)])
def day_of(T): return float(np.interp(T, _TT, _DAY))
def speed(T): return float(np.interp(T, _TT, _V))
def T_of_day(d): return float(np.interp(d, _DAY[_TT >= T_PLAY], _TT[_TT >= T_PLAY]))
# start epoch: the pile-up begins exactly on the drop
D0 = PILEUP_BJD - day_of(T_DROP + S16 * 0.5)
DAY_END_BEEPS = day_of(TOTAL)                                  # time brakes to a stop under the held chord; every transit still beeps

# ================= transits =================
TRANS = []                                                       # (T snapped, planet, sim day)
for p in PL:
    n = math.ceil((D0 - T0B[p]) / P[p]); d = T0B[p] + n * P[p] - D0
    while d < DAY_END_BEEPS:
        t = T_of_day(d); ts = round(t / S16) * S16
        TRANS.append((ts, p, d)); n += 1; d = T0B[p] + n * P[p] - D0
TRANS.sort()
NTR = len(TRANS)
TR_T = np.array([t for t, _, _ in TRANS])
# the pile-up (checked): first transit at/after the drop and the distinct planets within 1 day
_pu0 = min(x[2] for x in TRANS if x[0] >= T_DROP - 1e-6)
PU = [x for x in TRANS if _pu0 - 1e-9 <= x[2] <= _pu0 + 1.0]
PU_SET = sorted({p for _, p, _ in PU}, key=PL.index)

# ================= music plan =================
CHORDS = [("C", 36), ("G/B", 35), ("Am7", 33), ("G", 31)]
def chord_at(T): return CHORDS[int(max(0, T) // BAR + 1e-9) % 4]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    # tuning: each planet's note, one per half bar (h -> b)
    for k, p in enumerate(PL):
        ev(T_TUNE + k * BAR / 2, "pluck", m=PITCH[p], v=0.16, p=p, echo=True)
    # data: every transit = its planet's note
    for t, p, d in TRANS:
        ev(t, "pluck", m=PITCH[p], v=0.15 if t < T_DROP else 0.17, p=p, echo=t < T_DROP)
        if T_DROP <= t < T_CHORD and PITCH[p] <= 60: ev(t, "pluck", m=PITCH[p] + 12, v=0.06, p=p, echo=False)
    # arpeggio on the pile-up (C D G B up)
    for j, m in enumerate([60, 62, 67, 71, 72, 74, 79, 83]):
        ev(T_DROP + j * S16, "arp", m=m, v=0.06)
    # backing loop
    b = 0; t = 0.0
    while t < TOTAL - 1e-6:
        name, root = chord_at(t); v = speed(t)
        brk = T_BREAK <= t < T_DROP; held = t >= T_CHORD; intro = t < T_PLAY
        if t >= T_CHORD and t < T_OUT: root = 36                                      # held chord on C
        if b % 16 == 0: ev(t, "pad", root=root, d=BAR + .2, v=0.045 if not held else 0.0, cut=900 + 900 * min(1, v / 2.9))
        if not brk and not (t >= T_OUT + BAR):
            if b % 2 == 0 and (t >= B(1) or intro and t >= T_TUNE):                   # 8th-note octave bass
                ev(t, "bass", m=root + (12 if b % 4 == 2 else 0), v=0.10 if t >= T_PLAY else 0.07)
            if t >= T_PLAY and t < T_OUT:
                if b % 4 == 0: ev(t, "kick", v=0.26 if t >= T_DROP else 0.20)
                if b % 8 == 4 and t >= B(10): ev(t, "snare", v=0.13 if t >= T_DROP else 0.10)
                if b % 2 == 0 and t >= B(14): ev(t, "hat", v=0.03 if b % 4 else 0.045)
                if T_DROP <= t < T_CHORD:
                    arp = [60, 62, 67, 71]; ev(t, "arp", m=arp[b % 4] + (12 if (b // 4) % 2 else 0), v=0.025)
        b += 1; t = b * S16
    ev(T_BREAK, "swell", d=BAR, v=0.07)
    ev(T_CHORD, "chord", ms=[PITCH[p] for p in PL], d=B(2) + 0.6, v=0.09)                 # the whole data chord, held
    ev(T_OUT, "chord", ms=[36, 48, 55, 60, 62, 67, 71], d=B(3), v=0.05)
    for tt_, mm in ((0.0, 48), (0.27, 55), (0.54, 60), (0.80, 67)): ev(tt_, "pluck", m=mm, v=0.12, p="h", echo=True)   # title sting
    EV.sort(key=lambda e: e[0])
build()

# ================= scene (top view, neon) =================
CX, CY = 90, 150                                   # star (art px)
RMAX = 78
SC = RMAX / A_AU["h"]
RAD = {p: A_AU[p] * SC for p in PL}
COL = {"b": (255, 110, 190), "c": (196, 120, 255), "d": (110, 150, 255), "e": (80, 220, 255),
       "f": (90, 240, 150), "g": (250, 220, 90), "h": (255, 150, 80)}
SIZE = {"b": 2, "c": 2, "d": 1, "e": 2, "f": 2, "g": 2, "h": 1}   # pixel half-size (d, h are the smallest planets)
BG = (5, 6, 16); INK, INK2 = (236, 234, 246), (140, 146, 190); HUDBG = (14, 14, 34); STAR = (255, 196, 150)
_r = np.random.RandomState(1)
NST = 160; SX = _r.uniform(0, AW, NST); SY = _r.uniform(0, AH, NST); SB = _r.uniform(.1, 1, NST) ** 2

def mix(a, b, t): t = max(0, min(1, t)); return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))
def phase_c(p, day): return (day + D0 - T0B[p]) / P[p]          # orbits counted from t0 (integer = mid-transit)
# Each planet crosses the Earth line exactly on its (16th-snapped) note: phase is interpolated between the snapped transit
# times (shift <= half a 16th = 0.07 s of screen time), continuous elsewhere.
NODES = {}
for p in PL:
    ts = [(T_PLAY, phase_c(p, 0.0))]
    for t, q, d in TRANS:
        if q == p: ts.append((t, round(phase_c(p, d))))
    for tt in np.arange(ts[-1][0] + 2 * S16, TOTAL + 1, 0.05): ts.append((tt, max(ts[-1][1], phase_c(p, day_of(tt)))))
    NODES[p] = (np.array([a for a, _ in ts]), np.array([b for _, b in ts], float))
def ang(p, T):
    ph = phase_c(p, 0.0) if T <= T_PLAY else float(np.interp(T, *NODES[p]))
    return math.pi / 2 + 2 * math.pi * ph                         # pi/2 = pointing down = toward Earth
def pos(p, T):
    a = ang(p, T); return CX + RAD[p] * math.cos(a), CY + RAD[p] * math.sin(a)

def last_hit(p, T):
    """seconds since this planet's last transit note (inf if none)"""
    best = 1e9
    for t, q, _ in TRANS:
        if t > T + 1e-6: break
        if q == p: best = T - t
    return best

def visible(p, T):
    if T < T_TUNE: return 0.0
    k = PL.index(p); return ease((T - (T_TUNE + k * BAR / 2)) / 0.25)

def draw_scene(T):
    a = np.zeros((AH, AW, 3), np.uint8); a[:] = BG
    img = Image.fromarray(a); d = ImageDraw.Draw(img)
    tw = int(T * 6)
    for k in range(NST):
        if (k * 5 + tw) % 23 == 0: continue
        d.point((SX[k], SY[k]), fill=mix(BG, (200, 205, 255), .15 + .5 * SB[k]))
    day = day_of(min(T, TOTAL))
    # line of sight to Earth (down)
    for y in range(CY + 4, 236, 3): d.point((CX, y), fill=(70, 80, 130))
    # star pulse on any transit
    i = int(np.searchsorted(TR_T, T + 1e-6)) - 1
    pulse = math.exp(-(T - TR_T[i]) / 0.15) if i >= 0 else 0.0
    if T < T_TUNE: pulse = 0.0
    for p in PL:
        vis = visible(p, T)
        if vis <= 0: continue
        h = last_hit(p, T) if T >= T_PLAY else (T - (T_TUNE + PL.index(p) * BAR / 2))
        hit = math.exp(-max(0, h) / 0.22) if h >= 0 else 0.0
        oc = mix(BG, COL[p], (0.28 + 0.55 * hit) * vis)
        r = RAD[p]; d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=oc)
    # star
    for rr, w in ((9, .10), (6, .22), (4, .45)):
        d.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], fill=mix(BG, STAR, w + .35 * pulse * w))
    d.ellipse([CX - 2, CY - 2, CX + 2, CY + 2], fill=mix(STAR, (255, 255, 240), .5 + .5 * pulse))
    # planets
    for p in PL:
        vis = visible(p, T)
        if vis <= 0: continue
        x, y = pos(p, T)
        h = last_hit(p, T) if T >= T_PLAY else (T - (T_TUNE + PL.index(p) * BAR / 2))
        hit = math.exp(-max(0, h) / 0.25) if h >= 0 else 0.0
        s = SIZE[p] + (1 if hit > .4 else 0)
        if hit > 0.05:
            g = 3 + 5 * hit; d.ellipse([x - g, y - g, x + g, y + g], outline=mix(BG, COL[p], hit))
        d.rectangle([x - s, y - s, x + s, y + s], fill=mix(BG, mix(COL[p], (255, 255, 255), .6 * hit), vis))
    return img, pulse

# piano roll (art px): 7 lanes, notes scroll right -> left into the playhead
ROLL_Y0, LANE = 240, 8
PLAYX = 150; PX_S = 34          # px per second
ROLL_ORDER = ["b", "d", "c", "e", "f", "g", "h"]   # top = highest pitch (G5 D5 B4 G4 C4 G3 C3)
def draw_roll(img, T):
    d = ImageDraw.Draw(img)
    d.rectangle([4, ROLL_Y0 - 3, AW - 5, ROLL_Y0 + 7 * LANE + 2], fill=(10, 10, 26))
    for k, p in enumerate(ROLL_ORDER):
        y = ROLL_Y0 + k * LANE + LANE // 2
        d.line([16, y, AW - 8, y], fill=mix((10, 10, 26), COL[p], .18 * visible(p, T)))
    d.line([PLAYX, ROLL_Y0 - 3, PLAYX, ROLL_Y0 + 7 * LANE + 2], fill=(120, 120, 170))
    if T < T_PLAY: return
    lo, hi = T - (PLAYX - 16) / PX_S, T + (AW - 8 - PLAYX) / PX_S
    i0 = int(np.searchsorted(TR_T, lo)); i1 = int(np.searchsorted(TR_T, hi))
    for t, p, _ in TRANS[i0:i1]:
        x = PLAYX + (t - T) * PX_S; y = ROLL_Y0 + ROLL_ORDER.index(p) * LANE + LANE // 2
        played = t <= T + 1e-6; age = T - t
        c = COL[p] if played else mix((10, 10, 26), COL[p], .45)
        if played and age < 0.2: c = mix(COL[p], (255, 255, 255), .6 * (1 - age / .2))
        d.rectangle([x - 1, y - 2, x + 3, y + 1], fill=c)

def frame(T):
    img, pulse = draw_scene(T); draw_roll(img, T)
    return Ctx(np.array(img)), pulse

# ================= text =================
def box(W, y0, y1, col):
    W.rectangle([16, y0, 344, y1], fill=HUDBG); W.rectangle([16, y0, 344, y0 + 1], fill=col)

def roll_labels(W, T):
    for k, p in enumerate(ROLL_ORDER):
        y = (ROLL_Y0 + k * LANE) * 2 - 1
        if visible(p, T) > 0: text(W, 14, y, p, fill=COL[p])

def hud(W, T):
    box(W, 12, 74, (90, 240, 150))
    dd = day_of(T)
    text(W, 26, 18, f"DAY {int(dd)}", size=40, fill=INK)
    sp = speed(T)
    text(W, 26, 54, f"1 SECOND = {sp:.1f} DAYS" if T < T_CHORD else "TIME STOPS", fill=INK2)
    n = int(np.searchsorted(TR_T, T + 1e-6))
    text(W, 336, 18, f"{n}", size=40, fill=(250, 220, 90), align="r")
    text(W, 336, 54, "TRANSITS", fill=INK2, align="r")

def legend(W, T):
    W.rectangle([16, 604, 344, 632], fill=HUDBG)
    text(W, 180, 610, "EVERY BEEP = A PLANET CROSSING ITS STAR", fill=INK, align="c")
    text(W, 214, 458, "TO EARTH", fill=(110, 120, 170))

def banner_box(W, y, tt, sub, big, a, col):
    w = max((16 if big else 8) * len(tt), 8 * len(sub or "")) + 24
    hgt = (60 if big else 40) if sub else (44 if big else 24)
    W.rectangle([180 - w / 2, y, 180 + w / 2, y + hgt], fill=HUDBG); W.rectangle([180 - w / 2, y, 180 + w / 2, y + 1], fill=col)
    text(W, 180, y + 3, tt, size=40 if big else 20, fill=INK, align="c")
    if sub and a > 0.2: text(W, 180, y + (40 if big else 20), sub, fill=col, align="c")

GOLD, BLUE, PINK, GREEN = (250, 220, 90), (110, 170, 255), (255, 110, 190), (90, 240, 150)
BY = 82
BANNERS = [
    (T_PLAY + 0.1, B(8.2), "TRAPPIST-1, A SMALL RED STAR", "≈ 40 LIGHT-YEARS AWAY", False, BLUE),
    (B(8.5), B(10.6), "b: 1 YEAR = 36 HOURS", "1.51 DAYS PER ORBIT", False, PINK),
    (B(11), B(13.4), "h ORBITS 9.3 M KM OUT · 5.8 M MI", "MERCURY: 58 M KM · 36 M MI FROM THE SUN", False, GOLD),
    (B(14), B(15.6), "FASTER", None, True, GREEN),
    (B(16.5), B(19.4), "h: 1 ORBIT  ·  b: 12.4 ORBITS", "IN THE SAME 18.8 DAYS", False, GOLD),
    (T_BREAK, T_DROP - 0.02, "NEIGHBOURS MOVE IN STEP", "ORBIT RATIOS ≈ 3:2 4:3 3:2 3:2 5:3 8:5", False, BLUE),
    (T_DROP, T_DROP + B(2.2), f"{len(PU_SET)} PLANETS IN 1 DAY", "h g e c b · REAL TRANSIT TIMES", True, PINK),
]
def banners(W, T):
    for t0, t1, tt, sub, big, col in BANNERS:
        if t0 <= T < t1: banner_box(W, BY, tt, sub, big, T - t0, col)

def tuning(W, T):
    k = int((T - T_TUNE) // (BAR / 2))
    if T >= T_TUNE + 3.5 * BAR:
        box(W, 82, 140, GREEN); text(W, 180, 88, "NOW SPEED UP TIME", size=40, fill=INK, align="c")
        text(W, 180, 120, "AND LISTEN TO THEM PLAY", fill=GREEN, align="c"); return
    k = max(0, min(6, k)); p = PL[k]
    box(W, 82, 140, COL[p])
    text(W, 180, 88, f"{p}  ·  {P[p]:.2f} DAYS", size=40, fill=INK, align="c")
    text(W, 180, 120, f"ITS NOTE: {NOTE[p]}" + (f"   ({RATIO[p]} WITH THE NEXT ONE IN)" if p in RATIO else "   (THE FASTEST)"), fill=COL[p], align="c")

def chord_card(W, T):
    t = T - T_CHORD
    box(W, 82, 200, GOLD)
    text(W, 180, 88, "ONE CHORD", size=40, fill=INK, align="c")
    if t > .3:
        xs = [180 - 3 * 44 + j * 44 for j in range(7)]
        for j, p in enumerate(PL):
            text(W, xs[j], 128, p, fill=COL[p], align="c"); text(W, xs[j], 146, NOTE[p], fill=INK, align="c")
        for j, p in enumerate(PL[:-1]):
            text(W, (xs[j] + xs[j + 1]) / 2, 164, RATIO[p], fill=INK2, align="c")
    if t > .9: text(W, 180, 182, "PERIOD RATIOS, ROUNDED · OCTAVES FOLDED", fill=GOLD, align="c")

def sc_main(t):
    T = t; c, pulse = frame(T); W = c.t
    if T < T_TUNE:
        box(W, 12, 170, GREEN)
        text(W, 28, 20, "7 PLANETS.", size=40, fill=INK)
        if T > 0.27: text(W, 28, 56, "ONE STAR.", size=40, fill=INK)
        if T > 0.8: text(W, 28, 92, "THEIR ORBITS", size=40, fill=GOLD)
        if T > 1.1: text(W, 28, 128, "FORM A CHORD.", size=40, fill=GOLD)
    elif T < T_PLAY:
        tuning(W, T)
    else:
        hud(W, T)
        if T >= T_CHORD: chord_card(W, T)
        else: banners(W, T)
    if T >= T_PLAY: legend(W, T)
    elif T >= T_TUNE: text(W, 214, 458, "TO EARTH", fill=(110, 120, 170))
    roll_labels(W, T)
    return c

def sc_outro(t):
    T = T_OUT + t; c, _ = frame(T); W = c.t
    box(W, 40, 372, GOLD)
    text(W, 180, 52, "TRAPPIST-1", fill=INK2, align="c")
    if t > .15:
        text(W, 180, 74, "7 PLANETS", size=40, fill=INK, align="c")
        text(W, 180, 110, "1 STAR · 1 CHORD", size=40, fill=GOLD, align="c")
    if t > .7:
        text(W, 180, 156, f"{NTR} TRANSITS IN {int(round(DAY_END_BEEPS))} DAYS", fill=INK, align="c")
        text(W, 180, 176, "EACH ONE, ONE NOTE", fill=INK2, align="c")
    if t > 1.3:
        text(W, 180, 208, "WHICH PLANET IS YOUR VOICE?", size=20, fill=PINK, align="c")
    if t > 1.8:
        for k, ln in enumerate(["DATA: AGOL ET AL. 2021 (PSJ)", "CHECKED: GILLON 2017, LUGER 2017",
                                "REAL PERIODS + TRANSIT TIMES (2015)", "NOTES: RATIOS ROUNDED, OCTAVES FOLDED",
                                "ORBITS TO SCALE, BODIES ENLARGED"]):
            text(W, 180, 262 + 18 * k, ln, fill=INK2, align="c")
    return c

NAMES = ["a", "b", "c", "d", "outro"]
CUTS = [0, T_PLAY, B(14), T_DROP, T_OUT, TOTAL]
START = {n: CUTS[k] for k, n in enumerate(NAMES)}
DUR = {n: CUTS[k + 1] - CUTS[k] for k, n in enumerate(NAMES)}
def scene(name, t): return sc_outro(t) if name == "outro" else sc_main(START[name] + t)

def compose_light(c):
    art = np.array(c.art); big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt); tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

MOMENTS = [T_DROP]
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(scene(name, t))
    for m in MOMENTS:
        if 0 <= T - m < 0.2:
            a = T - m; s = int(round(6 * FXK * math.exp(-a / 0.06) * math.sin(a * 90))); fr = np.roll(fr, s, axis=0)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.6)) / 0.6)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    if name == "a":
        f = 1 - ease(t / 0.15)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

# ================= audio =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
PAN = {"h": 0, "g": -.5, "f": .5, "e": -.3, "d": .3, "c": -.6, "b": .6}
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def env(n, a, dec):
        t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
    def saw(f, n, dets=(.995, 1.005)):
        t = np.arange(n) / SR; return sum(2 * ((f * d * t) % 1) - 1 for d in dets) / len(dets)
    rng = np.random.RandomState(4)
    n = int((TOTAL + 3) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(t, x, pan=0.0, g=1.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(x)); L[i:j] += g * x[:j - i] * math.sqrt(.5 * (1 - pan)); R[i:j] += g * x[:j - i] * math.sqrt(.5 * (1 + pan))
    cache = {}
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if v <= 0: continue
        if k == "pluck":
            key = ("pl", kw["m"])
            if key not in cache:
                m_ = int(.7 * SR); cache[key] = lowpass(saw(mtof(kw["m"]), m_), 2600) * env(m_, .002, .22)
            s = cache[key]; pan = PAN[kw["p"]]
            put(t, s, pan, v)
            if kw.get("echo"): put(t + 3 * S16, s, -pan, v * .33)
        elif k == "arp":
            m_ = int(.25 * SR); put(t, lowpass(saw(mtof(kw["m"]), m_, (1.0,)), 3000) * env(m_, .002, .08), .2, v)
        elif k == "pad":
            d = kw["d"]; m_ = int((d + .4) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .3) * np.clip((d + .3 - tt) / .4, 0, 1)
            x = sum(saw(mtof(mm), m_, (.993, 1.007)) for mm in (kw["root"] + 24, kw["root"] + 31, kw["root"] + 36)) / 3
            put(t, lowpass(x, kw["cut"]) * e, 0, v)
        elif k == "bass":
            m_ = int(BEAT / 2 * .9 * SR); put(t, lowpass(saw(mtof(kw["m"]), m_, (1.0,)), 900) * env(m_, .003, .18), 0, v)
        elif k == "kick":
            m_ = int(.35 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 16) + 45) / SR) * np.exp(-tt * 12), 0, v)
        elif k == "snare":
            m_ = int(.22 * SR); tt = np.arange(m_) / SR
            x = lowpass(rng.randn(m_), 7000); x = highpass(x, 600) * np.exp(-tt * 14) * (tt < .16)   # gated
            put(t, x, -.1, v)
        elif k == "hat":
            m_ = int(.03 * SR); put(t, highpass(rng.randn(m_), 7000) * np.exp(-np.arange(m_) / SR * 150), .3, v)
        elif k == "swell":
            d = kw["d"]; m_ = int((d + .3) * SR); tt = np.arange(m_) / SR
            e = np.clip(tt / d, 0, 1) ** 2 * np.clip((d + .2 - tt) / .2, 0, 1)
            put(t, lowpass(rng.randn(m_), 2200) * e, 0, v)
        elif k == "chord":
            d = kw["d"]; m_ = int((d + .5) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .25) * np.clip((d - tt) / 1.4, 0, 1)
            x = sum(saw(mtof(mm), m_, (.994, 1.006)) for mm in kw["ms"]) / len(kw["ms"])
            put(t, lowpass(x, 2400) * e, 0, v * 2.2)
    def reverb(x, mix=.22):
        out = x.copy()
        for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
            k_ = int(dl * SR); out[k_:] += g * .6 * x[:-k_]
        return (1 - mix) * x + mix * lowpass(out, 4500)
    L = reverb(np.tanh(L * 1.4) / 1.4); R = reverb(np.tanh(R * 1.4) / 1.4)
    tt = np.arange(n) / SR; fade = np.clip((TOTAL - tt) / 1.0, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max()); st = np.stack([L, R], 1) / mx * .89
    st = st[:int(TOTAL * SR)]
    wavfile.write(path, SR, (st * 32767).astype(np.int16)); print(path, round(len(st) / SR, 2), "s")

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
    if mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print("total", round(TOTAL, 2), "s ·", {n: round(DUR[n], 2) for n in NAMES})
        print("D0 (BJD-2450000)", round(D0, 3), "window days", round(DAY_END_BEEPS, 2), "transits", NTR, Counter(p for _, p, _ in TRANS))
        print("pile-up", [(round(t, 2), p, round(d + D0, 3)) for t, p, d in PU], PU_SET)
        dt = np.diff(TR_T); print("min gap between distinct notes (s)", round(float(dt[dt > 1e-6].min()), 3), "same-slot pairs", int((dt < 1e-6).sum()))
        print("events", Counter(k for _, k, _ in EV))
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
