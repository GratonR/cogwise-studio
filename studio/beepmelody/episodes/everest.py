"""BEEPMELODY — THE QUEUE TO THE TOP. Summits of Mount Everest per year, 1953 -> 2025 (Himalayan Database).
One calendar year = 1.5 beats. Every year with summits = one note (pitch = log of the year's summits) plus
soft footsteps (more footsteps = more summits). Years with zero summits stay silent: the silence is data.
Three eras, three voices (like THE RACE TO THE SKY): bell 1953-1989, marimba 1990-2009, soft synth 2010-2025.
Picture: clear-sky palette, side view of Everest, a queue of climbers on the ridge (1 dot = 10 summits, rounded up),
bar chart of summits per year at the bottom (linear).
Data: everest.csv (Himalayan Database + 2 cross-checks per row).

    python3 everest.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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

FXK = float(os.environ.get("PI_FX", "0.5"))

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "everest.csv"))))
S = {int(r["year"]): int(r["summits"]) for r in ROWS}
APPROX = {int(r["year"]) for r in ROWS if r["approx"] == "1"}
Y0, Y1 = 1953, 2025
YEARS = list(range(Y0, Y1 + 1))
NY = len(YEARS)
EVY = [y for y in YEARS if S.get(y, 0) > 0]           # years that make a note
NE = len(EVY)
SMAX = max(S.values())
def s_of(y): return S.get(y, 0)
def fmt_n(y):
    s = s_of(y); return ("~" if y in APPROX else "") + f"{s:,}"
CUM = {}
_acc = 0
for y in YEARS: _acc += s_of(y); CUM[y] = _acc
def era(y): return "pioneers" if y < 1990 else ("guided" if y < 2010 else "crowds")
ERAS = ["pioneers", "guided", "crowds"]
ERA_NAME = {"pioneers": "1953-89", "guided": "1990-2009", "crowds": "2010-25"}

# ================= palette (clear sky, light) =================
INK = (34, 44, 78)
INK2 = (92, 104, 140)
CORAL = (232, 92, 70)
GOLD = (236, 168, 52)
CREAM = (252, 248, 238)
WHITE = (255, 255, 255)
ECOL = {"pioneers": CORAL, "guided": (18, 128, 116), "crowds": (112, 70, 196)}
ROCK = (122, 128, 150)
ROCK2 = (98, 104, 128)
SNOW = (246, 248, 252)
SNOW2 = (214, 224, 238)

# ================= timeline (all on the beat) =================
BPM = 120.0
BEAT = 60.0 / BPM
YB = 1.5                                              # beats per calendar year
INTRO_B, HOLD_B, OUTRO_B = 7, 6, 14
def t_year(y): return (INTRO_B + (y - Y0) * YB) * BEAT
T_LAST = t_year(Y1)
T_END_MAIN = T_LAST + HOLD_B * BEAT
TOTAL = T_END_MAIN + OUTRO_B * BEAT
SC = [("intro", t_year(Y0)), ("pioneers", t_year(1990) - t_year(Y0)), ("guided", t_year(2010) - t_year(1990)),
      ("crowds", T_END_MAIN - t_year(2010)), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

def year_at(T):
    if T < t_year(Y0): return None
    return min(Y1, Y0 + int((T - t_year(Y0)) / (YB * BEAT)))
def last_event(T):
    k = None
    for y in EVY:
        if t_year(y) <= T: k = y
    return k

# ================= music plan (shared by picture + audio) =================
SCALE = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86, 88, 90, 93]       # D major pentatonic from D4
LMIN, LMAX = math.log10(2), math.log10(SMAX)
def lev(y): return (math.log10(s_of(y)) - LMIN) / (LMAX - LMIN)
def pitch(y): return SCALE[int(round(lev(y) * (len(SCALE) - 1)))]
def nsteps(y): return 1 + int(round(5 * lev(y)))              # 1..6 footsteps on the 16ths
CHORDS = [(55, 59, 62, 66), (57, 61, 64, 67), (54, 57, 61, 64), (50, 54, 57, 59)]   # Gmaj7 A7 F#m7 Bm7/D
ROOTS = [43, 45, 42, 47]
VOICE = {"pioneers": "bell", "guided": "mallet", "crowds": "lead"}
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    ev(0.10, "bell", m=74, v=0.40)
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        ch = CHORDS[bar % 4]; ro = ROOTS[bar % 4]
        groove = t_year(Y0) - 2 * BEAT <= t < T_END_MAIN
        late = t >= T_END_MAIN
        if pos == 0: ev(t, "keys", ch=ch, d=1.4 * BEAT, v=0.20 if not late else 0.15)
        if pos == 1 and not late: ev(t + BEAT / 2, "keys", ch=ch, d=0.45 * BEAT, v=0.13)
        if pos == 3 and not late: ev(t + BEAT / 2, "keys", ch=ch, d=0.45 * BEAT, v=0.11)
        if late and pos == 0: ev(t, "pad", ch=ch, d=4 * BEAT, v=0.12)
        if groove:
            if pos == 0: ev(t, "bass", m=ro, d=BEAT * 0.8, v=0.32)
            if pos == 1: ev(t + BEAT / 2, "bass", m=ro + 12, d=BEAT * 0.35, v=0.22)
            if pos == 2: ev(t, "bass", m=ro + 7, d=BEAT * 0.6, v=0.26)
            if pos == 3: ev(t + BEAT / 2, "bass", m=ro, d=BEAT * 0.4, v=0.24)
            if t >= t_year(Y0):
                if pos in (0, 2): ev(t, "kick", v=0.62)
                if pos == 1: ev(t + BEAT / 2, "kick", v=0.38)
                if pos in (1, 3): ev(t, "snare", v=0.34)
                for h in range(2): ev(t + h * BEAT * 0.54, "hat", v=0.10 if h == 0 else 0.07)
                if pos == 3 and bar % 2 == 1: ev(t + BEAT * 0.54, "ohat", v=0.08)
            elif pos in (1, 3):
                ev(t, "hat", v=0.06)
    for y in EVY:
        t = t_year(y)
        ev(t, VOICE[era(y)], m=pitch(y), v=0.48 + 0.26 * lev(y))
        for k in range(1, nsteps(y)):
            ev(t + k * BEAT / 4, "step", v=0.10 + 0.12 * lev(y))
    for k, d in enumerate([0, 7, 12, 16, 19, 24]):                  # rising arpeggio on the last year
        ev(T_LAST + 2 * BEAT + k * BEAT / 4, "bell", m=74 + d - 12, v=0.40)
    for y in (1990, 2010, 2019):
        ev(t_year(y), "crash", v=0.24)
    ev(T_LAST, "crash", v=0.30)
    ev(t_year(2019) - BEAT * 4, "riser", d=BEAT * 4, v=0.12)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= drawing =================
SUMMIT = (112, 132)
RIDGE = [(112, 132), (100, 141), (90, 147), (78, 158), (66, 166), (52, 178), (38, 188), (22, 200), (6, 212), (-6, 220)]
def _ridge_pts(step=1.5):
    pts, acc = [], 0.0
    for (x0, y0), (x1, y1) in zip(RIDGE, RIDGE[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = 0.0
        while n < L:
            f = n / L; pts.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)); n += step
    return pts
QPTS = _ridge_pts()[2:]
def ndots(y): return math.ceil(s_of(y) / 10)
assert ndots(2019) <= len(QPTS), (ndots(2019), len(QPTS))

CH_X0, CH_BASE, CH_H = 17, 288, 40
def bar_h(y): return 0 if s_of(y) == 0 else max(1, int(round(CH_H * s_of(y) / SMAX)))

_SNOWF = [(random.Random(s).uniform(0, AW), random.Random(s + 5).uniform(0, 1), random.Random(s + 9).uniform(0.4, 1)) for s in range(70)]
def background(T):
    img = Image.new("RGB", (AW, AH)); d = ImageDraw.Draw(img)
    for y in range(AH):
        f = max(0.0, min(1.0, (y - 80) / 200))
        c = tuple(int(lerp(a, b, f)) for a, b in zip((178, 208, 240), (232, 242, 249)))
        d.line([0, y, AW, y], fill=c)
    # far peaks (Lhotse / Nuptse silhouettes, generic)
    d.polygon([(100, 236), (150, 164), (166, 176), (180, 168), (180, 236)], fill=(196, 206, 226))
    d.polygon([(-4, 236), (30, 196), (48, 206), (70, 236)], fill=(204, 214, 232))
    # Everest
    poly = [(-10, 236), (-6, 220)] + RIDGE[::-1][1:] + [(124, 140), (134, 150), (146, 156), (160, 172), (172, 184), (190, 196), (190, 236)]
    d.polygon(poly, fill=ROCK)
    d.polygon([(112, 132), (124, 140), (134, 150), (128, 168), (118, 190), (114, 236), (104, 236), (110, 180)], fill=ROCK2)
    snow = [(112, 132), (100, 141), (90, 147), (78, 158), (82, 160), (94, 154), (104, 150), (110, 158), (116, 148), (124, 140)]
    d.polygon(snow, fill=SNOW)
    d.polygon([(66, 166), (52, 178), (58, 180), (70, 172)], fill=SNOW2)
    d.polygon([(134, 150), (146, 156), (142, 164), (136, 160)], fill=SNOW2)
    # summit plume (wind) drifting right
    for k in range(5):
        x = 114 + k * 5 + (T * 6 + k * 3) % 4
        d.line([x, 131 - k % 2, x + 3, 131 - k % 2], fill=(244, 248, 252))
    return img

def chart(c, T, yr):
    d = c.a; W = c.t
    d.rectangle([0, 238, AW, 300], fill=CREAM)
    d.line([0, 238, AW, 238], fill=INK2)
    y500 = CH_BASE - CH_H * 500 / SMAX
    for x in range(CH_X0, CH_X0 + 2 * NY, 3): d.point((x, int(y500)), fill=SNOW2)
    text(W, 2 * CH_X0 - 4, int(y500 * 2) - 10, "500", fill=INK2, align="r")
    for y in YEARS:
        if yr is None or y > yr: break
        x = CH_X0 + 2 * (y - Y0); h = bar_h(y)
        col = GOLD if y == yr else ECOL[era(y)]
        if h: d.rectangle([x, CH_BASE - h + 1, x, CH_BASE], fill=col)
        elif y == yr: d.point((x, CH_BASE), fill=CORAL)
    d.line([CH_X0 - 1, CH_BASE + 1, CH_X0 + 2 * NY, CH_BASE + 1], fill=INK2)
    for y, al in ((1953, "l"), (1990, "c"), (2010, "c"), (2025, "r")):
        x = CH_X0 + 2 * (y - Y0)
        d.line([x, CH_BASE + 2, x, CH_BASE + 3], fill=INK2)
        text(W, 2 * x + (-4 if al == "l" else 4 if al == "r" else 0), 2 * CH_BASE + 6, str(y), fill=INK2, align=al)
    text(W, 352, 480, "SUMMITS PER YEAR", fill=INK2, align="r")
    if yr is not None and T < T_END_MAIN: text(W, 8, 480, "QUEUE: 1 DOT = 10 SUMMITS", fill=INK2)

def climber(d, x, y, col):
    x, y = int(round(x)), int(round(y))
    d.point((x, y - 2), fill=INK); d.line([x, y - 1, x, y], fill=col)

def draw_scene(c, T):
    c.art = background(T); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    yr = year_at(T)
    if yr is not None and yr >= 1953:
        d.line([SUMMIT[0], SUMMIT[1] - 1, SUMMIT[0], SUMMIT[1] - 7], fill=INK2)
        d.polygon([(SUMMIT[0] + 1, SUMMIT[1] - 7), (SUMMIT[0] + 6, SUMMIT[1] - 5), (SUMMIT[0] + 1, SUMMIT[1] - 3)], fill=CORAL)
    if yr is not None:
        a = T - t_year(yr); n = ndots(yr)
        fill = ease(min(1.0, a / (1.0 * BEAT)))
        shown = int(round(n * fill))
        col = ECOL[era(yr)]
        for j in range(shown):
            px, py = QPTS[j]
            bob = 1 if (j + int(T * 8)) % 7 == 0 else 0
            climber(d, px, py - bob, col if j % 3 else GOLD)
        if s_of(yr) and 0 <= a < 0.45:
            rr = 4 + a * 40
            d.ellipse([SUMMIT[0] - rr, SUMMIT[1] - 4 - rr, SUMMIT[0] + rr, SUMMIT[1] - 4 + rr], outline=WHITE if a < 0.18 else GOLD)
        if s_of(yr) == 0:
            for x, ph, sp in _SNOWF:
                yy = 90 + ((ph + T * 0.35 * sp) % 1.0) * 146
                d.point((int(x + 3 * math.sin(T * 2 + ph * 9)), int(yy)), fill=WHITE)
    if T < T_END_MAIN:
        text(W, 10, 266, "EVEREST", fill=INK, align="l")
        text(W, 10, 284, "8,849 M · 29,032 FT", fill=INK2, align="l")
    chart(c, T, yr)

NOTE = {1953: "HILLARY + TENZING, FIRST ASCENT", 1975: "JUNKO TABEI, FIRST WOMAN", 1978: "MESSNER + HABELER, NO BOTTLED O2",
        2014: "AVALANCHE: 16 GUIDES KILLED", 2015: "NEPAL EARTHQUAKE, SEASON OVER", 2019: "RECORD YEAR",
        2020: "PANDEMIC: NORTH SIDE ONLY", 2025: "ESTIMATE (SEASON TALLY)"}
ERA_LINE = {"pioneers": "THE PIONEER YEARS", "guided": "GUIDED CLIMBS GROW", "crowds": "THE CROWD YEARS"}
def hud(c, T):
    W = c.t; yr = year_at(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if yr is None:
        text(W, 28, 22, "SUMMITS OF EVEREST", fill=INK2); text(W, 28, 44, "...", size=40, fill=INK); return
    s = s_of(yr); age = T - t_year(yr); col = ECOL[era(yr)]
    text(W, 28, 22, "PEOPLE ON TOP IN", fill=INK2)
    if s:
        text(W, 28, 44, fmt_n(yr), size=40, fill=col if age < 0.22 else INK)
        text(W, 28 + 22 * len(fmt_n(yr)) + 4, 62, "SUMMITS", fill=INK2)
    else:
        text(W, 28, 44, "0", size=40, fill=CORAL)
        text(W, 54, 62, "NOBODY", fill=CORAL)
    text(W, 334, 44, str(yr), size=40, fill=GOLD, align="r")
    tot = ("~" if yr >= 2025 else "") + f"{CUM[yr]:,}"
    text(W, 28, 92, f"ALL-TIME: {tot}", fill=INK2)
    W.rectangle([16, 128, 344, 160], fill=(250, 250, 252)); W.rectangle([16, 128, 19, 160], fill=col if s else CORAL)
    line = NOTE.get(yr, ERA_LINE[era(yr)] if s else "NOBODY REACHED THE TOP")
    n = int(min(60, 3 + age * 200))
    text(W, 28, 134, line[:max(0, n)], fill=INK if (yr in NOTE or not s) else col)

def legend(c, T):
    W = c.t; yr = year_at(T)
    W.rectangle([0, 604, 360, 640], fill=CREAM); W.rectangle([0, 604, 360, 605], fill=INK2)
    for j, e in enumerate(ERAS):
        tot = sum(s_of(y) for y in YEARS if era(y) == e and yr is not None and y <= yr)
        x = 60 + j * 120
        hot = yr is not None and era(yr) == e and s_of(yr) > 0 and T - t_year(yr) < 0.3
        text(W, x, 607, ERA_NAME[e], fill=ECOL[e], align="c")
        text(W, x, 622, ("~" if e == "crowds" and yr == 2025 else "") + f"{tot:,}", fill=ECOL[e] if hot else INK, align="c")

BANNERS = {1953: ("FIRST SUMMIT", "29 MAY 1953", True, 3),
           1957: ("SILENCE = NOBODY", "MADE IT THAT YEAR", False, 3),
           2003: ("50 YEARS ON", "264 SUMMITS IN ONE YEAR", False, 3),
           2015: ("ZERO SUMMITS", "AVALANCHE, THEN EARTHQUAKE", True, 3),
           2019: ("RECORD YEAR", "871 SUMMITS", True, 3),
           2025: ("2 PEOPLE  ->  ~846", "1953 TO 2025", True, 7)}
def banner(c, T):
    yr = year_at(T)
    if yr not in BANNERS: return
    tt, sub, big, hb = BANNERS[yr]; a = T - t_year(yr)
    if not (0.1 < a < hb * BEAT): return
    W = c.t; yb = 196
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + (62 if big else 42)], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=CORAL)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 40, sub, fill=CORAL, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 21, sub, fill=CORAL, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T); legend(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 26, "THE QUEUE", size=40, fill=INK)
    if t > 0.4: text(W, 28, 64, "TO THE TOP", size=40, fill=CORAL)
    if t > 1.0: text(W, 28, 112, "EVERY NOTE = A YEAR OF SUMMITS", fill=INK2)
    if t > 1.6: text(W, 28, 140, "MORE PEOPLE = HIGHER NOTE", fill=INK2)
    if t > 2.2:
        W.rectangle([60, 196, 300, 238], fill=CREAM); W.rectangle([60, 196, 300, 198], fill=GOLD)
        text(W, 180, 199, "MOUNT EVEREST", fill=INK, align="c")
        text(W, 180, 218, "1953 TO 2025", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, T); legend(c, T)
    W = c.t
    W.rectangle([16, 40, 344, 330], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=CORAL)
    text(W, 180, 50, "SUMMITS OF EVEREST", fill=INK2, align="c")
    rows = [("1953", "2", "THE FIRST TWO", "pioneers"), ("2019", "871", "THE RECORD YEAR", "crowds"),
            ("ALL-TIME", f"~{round(CUM[Y1], -1):,}", "1953 TO 2025", "guided")]
    for j, (a, b, s, e) in enumerate(rows):
        if t > 0.5 + j * 0.8:
            y = 78 + j * 64
            text(W, 30, y, a, fill=ECOL[e]); text(W, 330, y - 6, b, size=40, fill=INK, align="r")
            text(W, 330, y + 32, s, fill=INK2, align="r")
    if t > 3.4: text(W, 180, 278, "HOW LONG IS THE QUEUE NEXT YEAR?", fill=GOLD, align="c")
    if t > 4.4:
        W.rectangle([0, 470, 360, 600], fill=CREAM)
        text(W, 180, 526, "DATA: THE HIMALAYAN DATABASE,", fill=INK2, align="c")
        text(W, 180, 546, "CHECKED VS HA EXPEDITIONS AND", fill=INK2, align="c")
        text(W, 180, 566, "ALAN ARNETTE (2025 = ESTIMATE)", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "pioneers": sc_main("pioneers"), "guided": sc_main("guided"), "crowds": sc_main("crowds"), "outro": sc_outro}

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
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    yr = year_at(T)
    if yr is not None and s_of(yr) and 0 <= T - t_year(yr) < 0.10 and name != "outro":
        fr = np.minimum(255, fr.astype(np.int16) + int(40 * FXK * (1 - (T - t_year(yr)) / 0.10))).astype(np.uint8)
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
        elif k == "bell":                                        # balloon voice: kalimba-like bell
            m_ = int(3.5 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt / 0.3)
                 + 0.12 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / 0.06)) * env(m_, 0.002, 1.1)
            put(t, x * v * 0.55, pan=-0.3, send=0.3)
            put(t + BEAT * 0.75, x * v * 0.12, pan=0.3)
        elif k == "mallet":                                      # plane voice: marimba
            m_ = int(1.2 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt / 0.03)
                 + 0.2 * np.sin(2 * np.pi * f * 10.0 * tt) * np.exp(-tt / 0.01)) * env(m_, 0.001, 0.32)
            put(t, x * v * 0.6, pan=0.3, send=0.18)
            put(t + BEAT * 0.5, x * v * 0.14, pan=-0.3)
        elif k == "lead":                                        # spacecraft voice: soft pulse lead with vibrato
            m_ = int(1.6 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            ph = 2 * np.pi * np.cumsum(f * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * tt) * np.minimum(1, tt / 0.3))) / SR
            sq = np.sign(np.sin(ph)) * 0.5 + 0.5 * np.sin(ph)
            b, a = butter(1, 3200 / (SR / 2)); x = lfilter(b, a, sq) * env(m_, 0.01, 0.6)
            put(t, x * v * 0.42, pan=0.0, send=0.35)
            for e_ in (1, 2): put(t + e_ * BEAT * 0.75, x * v * 0.42 * 0.35 ** e_, pan=0.4 * (-1) ** e_)
        elif k == "step":                                        # footstep in snow: short filtered crunch
            m_ = int(0.07 * SR); b, a = butter(2, [900 / (SR / 2), 4200 / (SR / 2)], "band")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.002, 0.018) * v * 1.6, pan=-0.25 + 0.5 * rng.random())
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
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV), "notes", NE)
        print([(y, s_of(y), round(t_year(y), 2), pitch(y), nsteps(y), ndots(y)) for y in EVY])
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
