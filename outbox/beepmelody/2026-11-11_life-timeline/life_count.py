"""BEEPMELODY — LIFE ON EARTH, COUNTED: FROM ~10 VAQUITAS TO ~10^31 VIRUSES.
Rework of life-timeline (co-pilot, angle « count », Guillaume 2026-11-11): 28 counts of living things, rarest to most
numerous, one marimba note per count, pitch = its power of ten (major pentatonic, 4 octaves). The number is written out
in full in the middle of the screen: it gets too long for the screen. Below, the log staircase of the 28 counts.
Mood (step 2, Guillaume chose B): organic house, 122 BPM — four-on-the-floor kick, shaker, rolling log-drum bass
Am–F–C–G, marimba = the counts; a filter opens a little more on every count, the drop lands on the last number.
Counts get closer and closer: 4 beats, then 2, then 1 — the music speeds up with the numbers.
Data: life_count.csv (2 sources per row).  LIFE_DARK=1 -> night palette (visual variant).

    python3 life_count.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, ease, lerp)
def text(d, x, y, s, **kw): v2.text(d, x, y, s.replace("~", "≈"), **kw)     # the font's tilde reads badly: use the ≈ glyph
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.8"))
DARK = os.environ.get("LIFE_DARK", "0") == "1"

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "life_count.csv"))))
for r in REC:
    r["v"] = float(r["value"]); r["e"] = math.log10(r["v"])
N = len(REC)
EMAX = max(r["e"] for r in REC)
def full_number(v):
    """the count written out in full: 10000 -> '10,000' ; 2.9e27 -> '2,900,...,000' (exact integer of the CSV value)"""
    from decimal import Decimal
    return f"{int(Decimal(v)):,}"
for r in REC:
    r["full"] = full_number(r["value"]); r["digits"] = len(r["full"].replace(",", ""))
def idx(label): return next(i for i, r in enumerate(REC) if r["label"] == label)

# ================= palette =================
if not DARK:      # light 'bio green' (channel default, like the altitude pilot's clear palette)
    BG0, BG1 = (222, 240, 226), (246, 250, 238)
    INK = (28, 52, 40); INK2 = (96, 122, 104); CREAM = (250, 251, 244)
    GOLD = (204, 128, 16); GREEN = (30, 146, 80); GREEN2 = (150, 206, 160); DOT = (60, 150, 96)
    CHARTBG = (250, 252, 248); GRID = (214, 230, 216); HOT = (226, 96, 40)
else:             # night: neon green on dark
    BG0, BG1 = (8, 20, 16), (14, 32, 26)
    INK = (226, 246, 230); INK2 = (130, 170, 146); CREAM = (12, 28, 22)
    GOLD = (255, 196, 70); GREEN = (90, 230, 140); GREEN2 = (40, 110, 70); DOT = (90, 230, 140)
    CHARTBG = (10, 24, 18); GRID = (30, 54, 42); HOT = (255, 140, 80)

# ================= timeline (on the beat) =================
BPM = 122.0
BEAT = 60.0 / BPM
INTRO_B = 8
I_SHEEP = idx("SHEEP"); I_CELLS = idx("HUMAN CELLS (ONE BODY)"); I_SAR = idx("SAR11 (PELAGIBACTER)")
HOLD8 = {idx("HUMANS"), idx("TREES")}                       # two big 'wait—' moments get 8 beats
def step_beats(i):
    if i == N - 1: return 12                                  # the last number rings (drop)
    if i in HOLD8: return 8
    if i < I_CELLS: return 4                                  # rare animals -> livestock -> trees: one count per bar
    if i < I_SAR: return 2                                    # cells -> microbes: twice as fast
    return 1                                                  # last climb: one per beat
OUTRO_B = 16
RT = []; t_ = INTRO_B * BEAT
for i in range(N):
    RT.append(t_); t_ += step_beats(i) * BEAT
T_END = t_
SC = [("intro", RT[0]), ("rare", RT[I_SHEEP] - RT[0]), ("many", RT[I_CELLS] - RT[I_SHEEP]),
      ("micro", T_END - RT[I_CELLS]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
TOTAL = acc_
T_DROP = RT[-1]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan (step-2 B) =================
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
PENTA = [0, 2, 4, 7, 9]
def pitch(i, base=48):                                        # v4: 10^0 -> 10^31 on C3..E5 only (no shrill top)
    k = int(round(REC[i]["e"] / EMAX * 12)); return base + 12 * (k // 5) + PENTA[k % 5]
PMAX = 76
ROOTS = [45, 41, 36, 43]                                      # Am F C G
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    t_riser = T_DROP - 4 * BEAT
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4); ro = ROOTS[bar % 4]
        outro = t >= T_END
        if abs(t - (T_DROP - BEAT)) < 1e-6: continue           # one beat of silence before the drop
        if t < T_END - 1e-6 and t >= T_DROP - BEAT and t < T_DROP: continue
        if b >= 2 or outro: ev(t, "kick", v=0.66 if t >= T_DROP else 0.6)
        ev(t + BEAT / 2, "shaker", v=0.06)
        if t >= RT[0] - 1e-6:                                     # v4: more pulse from the first count
            ev(t + BEAT / 2, "ohat", v=0.07)
            for s in (1, 3): ev(t + s * BEAT / 4, "hat", v=0.045 if t >= RT[I_CELLS] else 0.03)
            if pos in (1, 3): ev(t, "clap", v=0.2)
            for off in {0: (.75,), 1: (.5,), 2: (.75,), 3: (.25, .5)}[pos]:   # syncopated wood perc
                ev(t + off * BEAT, "perc", m=(76 if off == .75 else 69), v=0.09)
        if t >= RT[I_CELLS] - 1e-6 and pos == 3: ev(t + .75 * BEAT, "clap", v=0.1)
        if pos == 0 and b >= 4 and not (t_riser <= t < T_DROP):
            for q, off in enumerate((0, .75, 1.5, 2.5, 3.25)):   # rolling log-drum bass
                ev(t + off * BEAT, "logb", m=ro + (12 if q == 3 else 0), v=0.26)
        if pos == 0: ev(t, "chord", m=ro + 24, minor=(bar % 4 == 0), d=4 * BEAT, v=0.07)
    for i, t in enumerate(RT):
        m = pitch(i)
        ev(t, "mar", m=m, v=0.46); ev(t + BEAT / 2, "mar", m=m, v=0.14)          # note + 8th echo
        if step_beats(i) >= 2: ev(t + 3 * BEAT / 4, "mar", m=m, v=0.08)
        if i in HOLD8: ev(t, "crash", v=0.12)
    ev(t_riser, "riser", d=4 * BEAT - 0.05, v=0.14)
    ev(T_DROP, "crash", v=0.35); ev(T_DROP, "boom", v=0.5)
    for k, d in enumerate([0, 7, 12, 16, 19, 24]):            # rising arpeggio on the last count
        ev(T_DROP + (k + 1) * BEAT / 2, "mar", m=min(PMAX, pitch(N - 1) - 24 + d), v=0.26)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")
def cutoff(T):                                                # filter on the chords opens with every count
    k = rec_index(T); return 500 + 280 * (k + 1) if T < T_DROP else 9000

# ================= drawing =================
def bg():
    a = np.zeros((AH, AW, 3), np.uint8)
    for y in range(AH):
        f = min(1.0, y / 320); a[y, :] = tuple(int(BG0[j] + (BG1[j] - BG0[j]) * f) for j in range(3))
    return Image.fromarray(a)
_BG = bg()

# bottom: log staircase of the counts
CX0, CX1 = 28, 172
CY0, CY1 = 286, 228                                            # 10^0 at the bottom, 10^31 at the top
def cy(e): return CY0 + (CY1 - CY0) * e / 31
def cx(i): return CX0 + (CX1 - CX0) * (i + 0.5) / N
def chart(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    d.rectangle([CX0 - 10, CY1 - 14, CX1 + 4, CY0 + 6], fill=CHARTBG, outline=GRID)
    for e in (0, 10, 20, 30):
        y = int(cy(e)); d.line([CX0, y, CX1, y], fill=GRID)
        text(W, (CX0 - 2) * 2, y * 2 - 8, "1" if e == 0 else f"10^{e}", fill=INK2, align="r")
    bw = max(1, int((CX1 - CX0) / N) - 1)
    for i in range(k + 1):
        a = T - RT[i]; f = ease(min(1, a / 0.3))
        y = cy(REC[i]["e"] * f); x = int(cx(i) - bw / 2)
        col = HOT if (i == k and a < 0.3) else (GOLD if i == N - 1 else GREEN)
        d.rectangle([x, int(y), x + bw - 1, CY0], fill=col)
    text(W, (CX0 - 8) * 2, (CY1 - 12) * 2, "HOW MANY? (LOG SCALE)", fill=INK2)

def hud(c, T):
    W = c.t; k = rec_index(T); r = REC[k]; age = T - RT[k]
    W.rectangle([16, 18, 344, 124], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 123, 344, 124], fill=INK)
    text(W, 28, 22, "LIFE ON EARTH, COUNTED", fill=GREEN)
    text(W, 334, 22, f"{k + 1}/{N}", fill=INK2, align="r")
    hot = age < 0.2
    text(W, 28, 44, r["big"], size=40, fill=HOT if hot else INK)
    text(W, 28, 96, r["label"], fill=INK2)
    text(W, 334, 96, f"{r['digits']} DIGITS", fill=GOLD, align="r")

# the swarm: dots that pile up, more with every power of ten
_rs = np.random.RandomState(7)
SWARM = _rs.uniform(0, 1, (2600, 2))
def swarm(c, T):
    d = c.a; k = rec_index(T)
    if k < 0: return
    e = REC[k]["e"] if T - RT[k] > 0.25 else lerp(REC[k - 1]["e"] if k else 0, REC[k]["e"], ease((T - RT[k]) / 0.25))
    n = int(80 * e)                                            # ~80 dots per power of ten
    pts = SWARM[:n]
    for j, (u, v) in enumerate(pts):
        x = 14 + u * 152; y = 70 + v * 138
        d.point((int(x), int(y)), fill=DOT if j < n - 60 else HOT if T - RT[k] < 0.4 else DOT)

def label_lines(lb, per=20):
    if len(lb) <= per: return [lb]
    cut = lb.find(" (") if " (" in lb else lb.rfind(" ", 0, per + 1)
    return [lb[:cut], lb[cut + 1:]]

def number_wall(c, T):
    W = c.t; k = rec_index(T); r = REC[k]; age = T - RT[k]
    s = ("~" if r["big"].startswith(("~", "UP", "30-")) else "") + r["full"]
    per = 20; lines = []
    while s:
        if len(s) <= per: lines.append(s); break
        cut = s.rfind(",", 0, per + 1); cut = cut + 1 if cut > 0 else per
        lines.append(s[:cut]); s = s[cut:]
    y0 = 292 - len(lines) * 22
    h = len(lines) * 44 + 12
    lab = label_lines(r["label"]); lh = len(lab) * 40 + 10        # v4: the name, BIG, right above the number
    W.rectangle([12, y0 - 8 - lh, 348, y0 - 8 + h], fill=CREAM)
    W.rectangle([12, y0 - 8 - lh, 348, y0 - 7 - lh], fill=GOLD); W.rectangle([12, y0 - 9 + h, 348, y0 - 8 + h], fill=GOLD)
    for j, ln in enumerate(lab):
        text(W, 180, y0 - 4 - lh + j * 40, ln, size=40, fill=HOT if age < 0.2 else GREEN, align="c")
    W.rectangle([60, y0 - 10, 300, y0 - 9], fill=GRID)
    shown = int(len("".join(lines)) * ease(age / 0.35)) if age < 0.35 else 10 ** 6
    cnt = 0
    for j, ln in enumerate(lines):
        vis = ln[:max(0, shown - cnt)]; cnt += len(ln)
        text(W, 180, y0 + j * 44, vis, size=40, fill=GOLD if k == N - 1 else INK, align="c")

BANNERS = {idx("VAQUITAS"): ("THE RAREST", "ONE OF THE LAST ~10 (2024 SURVEY)"),
           idx("HUMANS"): ("THAT'S US", "8,200,000,000 PEOPLE (UN 2024)"),
           idx("CHICKENS"): ("3 CHICKENS", "FOR EVERY HUMAN"),
           idx("TREES"): ("~370 TREES", "FOR EVERY HUMAN"),
           idx("GUT BACTERIA (ONE BODY)"): ("1 FOR 1", "YOUR GUT BACTERIA ~ YOUR OWN CELLS"),
           idx("ANTS"): ("~2.4 MILLION", "ANTS FOR EVERY HUMAN"),
           N - 1: ("MORE VIRUSES", "THAN ALL CELLS ON EARTH COMBINED")}
def banner(c, T):
    k = rec_index(T)
    if k not in BANNERS: return
    a = T - RT[k]; hold = step_beats(k) * BEAT * 0.95
    if not (0.15 < a < hold): return
    W = c.t; tt, sub = BANNERS[k]; xc = 180; yb = 368
    w = max(16 * len(tt) + 30, 8 * len(sub) + 30)
    W.rectangle([xc - w / 2, yb, xc + w / 2, yb + 62], fill=CREAM)
    W.rectangle([xc - w / 2, yb, xc + w / 2, yb + 2], fill=HOT); W.rectangle([xc - w / 2, yb + 61, xc + w / 2, yb + 62], fill=INK2)
    text(W, xc, yb + 4, tt, size=40, fill=HOT, align="c")
    if a > 0.3: text(W, xc, yb + 40, sub, fill=INK, align="c")

def footer(c):
    W = c.t
    W.rectangle([0, 600, 360, 640], fill=CREAM); W.rectangle([0, 600, 360, 601], fill=INK2)
    text(W, 10, 604, "EVERY BEEP", fill=INK2); text(W, 10, 620, "= ONE COUNT", fill=GREEN)
    text(W, 350, 604, "HIGHER NOTE", fill=INK2, align="r"); text(W, 350, 620, "= MORE ZEROS", fill=GOLD, align="r")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); c.art = _BG.copy(); c.a = ImageDraw.Draw(c.art)
    swarm(c, T); chart(c, T)
    return c

def sc_intro(t):
    c = frame_ctx(t); W = c.t
    W.rectangle([16, 18, 344, 166], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 165, 344, 166], fill=INK)
    text(W, 28, 24, "~10 VAQUITAS LEFT.", size=40, fill=INK)
    if t > 0.35: text(W, 28, 64, "~10^31 VIRUSES.", size=40, fill=HOT)
    if t > 1.0: text(W, 28, 112, "LIFE ON EARTH, COUNTED", fill=GREEN)
    if t > 1.4: text(W, 28, 134, "28 NUMBERS · RAREST TO MOST", fill=INK2)
    if t > 2.0:
        W.rectangle([40, 368, 320, 410], fill=CREAM); W.rectangle([40, 368, 320, 370], fill=GOLD)
        text(W, 180, 371, "EVERY BEEP = ONE COUNT", fill=INK, align="c")
        text(W, 180, 389, "LISTEN TO THE ZEROS PILE UP", fill=INK2, align="c")
    footer(c)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); number_wall(c, T); banner(c, T); footer(c)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T_END); W = c.t
    W.rectangle([0, 0, 360, 600], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "LIFE ON EARTH, COUNTED", fill=INK2, align="c")
    rows = [("~10", "VAQUITAS", INK), ("8.2 BN", "HUMANS", GREEN), ("~3 TRILLION", "TREES", GREEN),
            ("~20 QUADR.", "ANTS", GOLD), ("~10^31", "VIRUSES", HOT)]
    for j, (a, b, col) in enumerate(rows):
        if t > 0.3 + j * 0.4:
            text(W, 34, 84 + j * 50, a, size=40, fill=col); text(W, 326, 98 + j * 50, b, fill=INK, align="r")
    if t > 2.4: text(W, 180, 350, "FROM 2 DIGITS TO 32 DIGITS", fill=GREEN, align="c")
    if t > 2.8:
        W.rectangle([30, 410, 330, 411], fill=INK2)
        lines = ["COUNTS ARE ESTIMATES (~) · DATA:", "IUCN RED LIST, IRF 2025, NZ DOC 2026,",
                 "FAOSTAT, UN WPP 2024, CALLAGHAN 2021,", "CROWTHER 2015, SENDER 2016,", "SCHULTHEISS 2022, VAN DEN HOOGEN 2019,",
                 "FLOMBAUM 2013, FLEMMING & WUERTZ 2019,", "SUTTLE 2005 · FULL LIST IN DESCRIPTION"]
        for j, ln in enumerate(lines): text(W, 180, 418 + j * 18, ln, fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "rare": sc_main("rare"), "many": sc_main("many"), "micro": sc_main("micro"), "outro": sc_outro}

def compose_light(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt)
    tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx_, t):
    name = NAMES[idx_]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(SCENEFN[name](t))
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    z = 1.0 + 0.010 * kp * FXK
    if abs(T - T_DROP) < 0.5: z += 0.035 * FXK * math.exp(-abs(T - T_DROP) / 0.12)
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if name != "outro" and k >= 0 and T - RT[k] < 0.08:
        fr = np.minimum(255, fr.astype(np.int16) + int(36 * FXK * (1 - (T - RT[k]) / 0.08))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio =================
SR = 44100
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n); fx = np.zeros(n); pad = np.zeros(n)
    rng = np.random.default_rng(11)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fx, i, x * send)
    def saw(freqs, m_):
        tt = np.arange(m_) / SR; s = np.zeros(m_)
        for f in freqs:
            for dd in (.996, 1.0, 1.004): s += 2 * ((tt * f * dd) % 1) - 1
        return s / (3 * len(freqs))
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "mar":
            m_ = int(0.9 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            hi = min(1.0, max(0.0, (kw["m"] - 60) / 16))              # v4: higher note -> softer, rounder
            x = np.sin(2 * np.pi * f * tt) + 0.35 * (1 - 0.8 * hi) * np.sin(2 * np.pi * f * 3.93 * tt) * np.exp(-tt * 30)
            x = x + 0.25 * np.sin(np.pi * f * tt) * hi                 # sub-octave body on the high ones
            put(t, x * env(m_, 0.004 + 0.006 * hi, 0.25) * v * (1 - 0.3 * hi), pan=-0.1, send=0.25)
        elif k == "ohat":
            m_ = int(0.12 * SR)
            x = lfilter(*butter(2, 7000 / (SR / 2), "high"), rng.standard_normal(m_)) * np.exp(-np.arange(m_) / SR * 30)
            put(t, x * v, pan=0.2)
        elif k == "perc":
            m_ = int(0.12 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            put(t, v * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 40), pan=0.45)
        elif k == "kick":
            m_ = int(0.4 * SR); tt = np.arange(m_) / SR
            put(t, v * 0.55 * np.sin(2 * np.pi * np.cumsum(110 * np.exp(-tt * 22) + 52) / SR) * np.exp(-tt * 9))
        elif k == "boom":
            m_ = int(1.4 * SR); tt = np.arange(m_) / SR
            put(t, v * np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 5) + 36) / SR) * np.exp(-tt * 2.5))
        elif k == "logb":
            m_ = int(0.35 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            put(t, v * np.sin(2 * np.pi * np.cumsum(f * (1 + .5 * np.exp(-tt * 40))) / SR) * np.exp(-tt * 7))
        elif k == "shaker":
            m_ = int(0.06 * SR)
            x = lfilter(*butter(2, 6000 / (SR / 2), "high"), rng.standard_normal(m_)) * np.exp(-np.arange(m_) / SR * 70)
            put(t, x * v, pan=0.3)
        elif k == "hat":
            m_ = int(0.03 * SR)
            x = lfilter(*butter(2, 8000 / (SR / 2), "high"), rng.standard_normal(m_)) * np.exp(-np.arange(m_) / SR * 160)
            put(t, x * v, pan=-0.3)
        elif k == "clap":
            m_ = int(0.16 * SR)
            x = lfilter(*butter(2, 2800 / (SR / 2)), rng.standard_normal(m_)) * np.exp(-np.arange(m_) / SR * 20)
            put(t, x * v, send=0.15)
        elif k == "chord":
            r = kw["m"]; m_ = int(kw["d"] * SR)
            add(pad, int(t * SR), saw([mtof(r), mtof(r + (3 if kw["minor"] else 4)), mtof(r + 7)], m_) * v)
        elif k == "crash":
            m_ = int(1.4 * SR)
            put(t, lfilter(*butter(2, 7000 / (SR / 2)), rng.standard_normal(m_)) * np.exp(-np.arange(m_) / SR * 2.2) * v, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            put(t, lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    # chords through a low-pass that opens with the data
    out = np.zeros(n); blk = 2048
    for i0 in range(0, n, blk):
        fc = min(cutoff(i0 / SR), SR / 2 - 200)
        seg = pad[max(0, i0 - 4096):i0 + blk]
        out[i0:i0 + blk] = lfilter(*butter(2, fc / (SR / 2)), seg)[-len(pad[i0:i0 + blk]):]
    pump = np.ones(n)                                             # v4: sidechain pump on the chords
    for tk in KICKS:
        i0 = int(tk * SR); m_ = min(n - i0, int(BEAT * SR))
        if m_ > 0: pump[i0:i0 + m_] = np.minimum(pump[i0:i0 + m_], 1 - 0.7 * np.exp(-np.arange(m_) / SR / 0.09))
    out *= pump
    L += out; R += out
    rv = fx.copy()
    for dl, g in [(.071, .5), (.113, .44), (.173, .37), (.241, .3), (.331, .24), (.449, .17), (.607, .12)]:
        k_ = int(dl * SR); rv[k_:] += g * .6 * fx[:-k_]
    rv = lfilter(*butter(2, 5000 / (SR / 2)), rv)
    L += rv * 0.5; R += np.roll(rv, 400) * 0.5
    tt = np.arange(n) / SR
    fade = np.clip((TOTAL - tt) / 1.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.tanh(np.stack([L, R], 1) / mx * 1.6) / np.tanh(1.6) * 0.89
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(n / SR, 2), "s")

def render_scene(args):
    i, out = args; name = NAMES[i]; dur = DUR[name]
    tmp, fin = f"{out}/{i:02d}_{name}.tmp.mp4", f"{out}/{i:02d}_{name}.mp4"
    nf = int(round((START[name] + dur) * FPS)) - int(round(START[name] * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    f0 = int(round(START[name] * FPS))
    for f in range(nf): p.stdin.write(render_frame(i, max(0.0, (f0 + f) / FPS - START[name])).tobytes())
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
            T = float(x); i = max(j for j, nm in enumerate(NAMES) if START[nm] <= T)
            Image.fromarray(render_frame(i, T - START[NAMES[i]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        for i, t in enumerate(RT):
            r = REC[i]; print(f"{t:6.2f}s  e={r['e']:5.2f}  p{pitch(i)}  {r['label']:<24} {r['big']:<16} {r['full']}")
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
