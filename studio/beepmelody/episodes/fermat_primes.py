"""BEEPMELODY — FERMAT SAID ALL THESE NUMBERS WERE PRIME. ONLY THE FIRST 5 ARE.
Fn = 2^(2^n) + 1, F0 -> F33 (co-pilot decision 1/4: index order). Every Fermat number = one bell on a wall = one note.
F0-F4: prime (Fermat, 1640) -> the bell rings green, right note. F5-F32: proven NOT prime (1732 -> 2001) -> the bell
cracks red, wrong note, the year of the proof and the first factor drop out. F33: nobody knows -> grey bell, silence, "?".
Data: fermat_primes.csv (Keller's Fermat factoring status + 2nd source per row; every factor re-checked here with
pow(2, 2^n, p) == p - 1, digits = floor(2^n log10 2) + 1).
Music (decision 2/4, B "Chiptune enquete"): 120 BPM 8-bit groove; right = bright square ding; wrong = error buzzer
sliding down + noise snare; groove drops out on F33.
Palette: FP_PAL=light (default, clear like THE RACE TO THE SKY) | dark.

    python3 fermat_primes.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv, re
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.6"))
PAL = os.environ.get("FP_PAL", "light")

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "fermat_primes.csv"))))
N = len(ROWS)                                             # 34: F0..F33
def first_factor(r):
    s = r["status"].split(" x ")[0]
    m = re.match(r"(\d+)\*2\^(\d+)\+1", s)
    return int(m.group(1)) * 2 ** int(m.group(2)) + 1 if m else int(s)
D = []
for r in ROWS:
    n = int(r["n"]); k = r["kind"]
    e = dict(n=n, kind=k, year=r["year_wrong"], who=r["who"], digits=int(r["digits"]))
    if k == "factor":
        p = first_factor(r); assert pow(2, 2 ** n, p) == p - 1, n; e["p"] = p
    assert e["digits"] == math.floor(2 ** n * math.log10(2)) + 1, n
    D.append(e)
D[0]["who"] = "Fermat"
WHO = {6: "LANDRY", 7: "MOREHEAD & WESTERN", 8: "MOREHEAD & WESTERN", 12: "PERVUSHIN & LUCAS", 13: "HALLYBURTON & BRILLHART",
       22: "CRANDALL ET AL.", 24: "MAYER ET AL.", 29: "GOSTIN & MCLAUGHLIN", 31: "KRUPPA & FORBES"}
def who(e): return WHO.get(e["n"], e["who"].upper())
NOFACTOR = {20, 24}                                       # composite, no factor known (MathWorld, Yamasaki)
FACT_LATER = {7: 1970, 8: 1980, 14: 2010, 22: 2010}       # composite by Pepin test; first factor found later

# ================= timeline (120 BPM, every hit on a half-second) =================
BEAT = 0.5
HIT = [1.0, 2.5, 4.0, 5.5, 7.0,                           # F0..F4 right notes
       9.5,                                               # F5 Euler
       13.5, 15.5, 17.5, 19.0, 20.5, 22.0, 23.5,          # F6..F12
       25.0, 26.0, 27.5, 28.5, 29.5, 30.5, 31.5, 32.5,    # F13..F20
       34.5, 35.5, 36.5, 37.5,                            # F21..F24
       39.0, 40.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0,    # F25..F32
       48.5]                                              # F33: silence
assert len(HIT) == N
for e, t in zip(D, HIT): e["t"] = t
OUTRO_T = 53.5
TOTAL = 66.0
SC = [("main", OUTRO_T), ("outro", TOTAL - OUTRO_T)]
DUR = dict(SC); NAMES = [n for n, _ in SC]; START = {"main": 0.0, "outro": OUTRO_T}

BANNERS = [  # (t0, t1, line1, line2, color key)
    (7.6, 9.4, "1640: FERMAT BETS", "THEY ARE ALL PRIME", "gold"),
    (9.6, 13.3, "1732: EULER BREAKS IT", "4,294,967,297 = 641 x 6,700,417", "red"),
    (15.6, 17.3, "1905: NOT PRIME.", "BUT NO FACTOR SEEN UNTIL 1970", "red"),
    (32.6, 34.3, "F20: NOT PRIME.", "NOBODY KNOWS ONE FACTOR. STILL.", "red"),
    (46.1, 48.3, "F32 HAS 1,292,913,987 DIGITS", "STILL NOT PRIME (1963)", "red"),
    (48.6, 53.3, "F33: NOBODY KNOWS", "2,585,827,973 DIGITS. TOO BIG TO TEST", "dim"),
]

def fmt(n): return f"{n:,}"

# ================= look =================
if PAL == "dark":
    BG0, BG1 = (22, 24, 38), (36, 34, 50)
    PANEL = (14, 14, 24); INK = (236, 230, 214); INK2 = (150, 146, 140)
    CELL = (52, 54, 70); CELL2 = (40, 42, 56); BELL = (120, 116, 110); BELLD = (90, 86, 82)
    GOLD = (246, 186, 64); GREEN = (96, 214, 120); RED = (240, 84, 76); DIM = (84, 84, 98)
else:
    BG0, BG1 = (238, 232, 216), (222, 214, 196)
    PANEL = (255, 252, 244); INK = (44, 46, 60); INK2 = (120, 116, 110)
    CELL = (210, 202, 186); CELL2 = (194, 186, 168); BELL = (168, 160, 146); BELLD = (140, 132, 120)
    GOLD = (204, 134, 24); GREEN = (46, 158, 84); RED = (210, 58, 52); DIM = (176, 170, 160)
COL = {"gold": GOLD, "red": RED, "dim": INK2, "green": GREEN}

COLS = 7; CW, CH, GAP, VGAP = 22, 30, 2, 3
WX0 = (AW - (COLS * CW + (COLS - 1) * GAP)) // 2; WY0 = 75
def cell_xy(n): return WX0 + (n % COLS) * (CW + GAP), WY0 + (n // COLS) * (CH + VGAP)

_BG = {}
def background():
    if PAL in _BG: return _BG[PAL].copy()
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        f = y / AH; a[y, :] = [BG0[j] * (1 - f) + BG1[j] * f for j in range(3)]
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    for n in range(N):
        x, y = cell_xy(n)
        d.rectangle([x, y, x + CW - 1, y + CH - 1], fill=CELL); d.rectangle([x, y + CH - 2, x + CW - 1, y + CH - 1], fill=CELL2)
    _BG[PAL] = img
    return img.copy()

def bell(d, x, y, col, dark, sway=0, crack=False, glow=0.0):
    cx = x + CW // 2 + sway
    if glow > 0:
        g = tuple(int(c) for c in col)
        d.rectangle([x - 1, y - 1, x + CW, y + CH], outline=g)
    d.rectangle([cx - 1, y + 2, cx, y + 3], fill=dark)                       # hook
    d.rectangle([cx - 3, y + 4, cx + 2, y + 6], fill=col)                    # crown
    d.rectangle([cx - 4, y + 7, cx + 3, y + 10], fill=col)
    d.rectangle([cx - 5, y + 11, cx + 4, y + 13], fill=col)
    d.rectangle([cx - 6, y + 14, cx + 5, y + 15], fill=dark)                 # rim
    d.rectangle([cx - 1 - sway, y + 16, cx - sway, y + 17], fill=dark)       # clapper
    d.rectangle([cx - 2, y + 5, cx - 2, y + 9], fill=tuple(min(255, c + 60) for c in col))  # shine
    if crack:
        pts = [(cx + 1, y + 4), (cx, y + 7), (cx + 2, y + 9), (cx, y + 12), (cx + 1, y + 15)]
        d.line(pts, fill=PANEL if PAL == "dark" else (60, 30, 30))

def played(T): return sum(1 for e in D[:-1] if e["t"] <= T)

def draw_wall(c, T):
    c.art = background(); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    for e in D:
        n = e["n"]; x, y = cell_xy(n); age = T - e["t"]
        on = age >= 0
        if n == N - 1:                                      # F33: grey, "?" once reached
            bell(d, x, y, BELL, BELLD, glow=1 if on else 0)
            if on and int(T * 2) % 2 == 0: d.rectangle([x - 1, y - 1, x + CW, y + CH], outline=GOLD)
            continue
        if not on:
            bell(d, x, y, BELL, BELLD); continue
        if e["kind"] == "prime":
            sway = int(round(2 * math.sin(age * 14) * math.exp(-age * 3))) if age < 1.5 else 0
            bell(d, x, y, GREEN, tuple(int(v * .6) for v in GREEN), sway=sway, glow=1 if age < .6 else 0)
        else:
            sh = int(round(random.uniform(-1.5, 1.5))) if age < .35 else 0
            bell(d, x + sh, y, RED, tuple(int(v * .6) for v in RED), crack=True, glow=1 if age < .4 else 0)
            if age < .5:                                    # chips flying
                for k in range(5):
                    a = random.uniform(0, 2 * math.pi); r = 3 + age * 30
                    px, py = x + CW / 2 + r * math.cos(a), y + 10 + r * math.sin(a) + age * 20
                    d.rectangle([px, py, px + 1, py + 1], fill=RED)
    # labels (text layer is 2x art)
    for e in D:
        n = e["n"]; x, y = cell_xy(n); on = T >= e["t"]
        lab = f"F{n}"
        if n == N - 1:
            col = GOLD if on else INK2
        elif not on: col = INK2
        else: col = GREEN if e["kind"] == "prime" else RED
        text(W, (x + CW / 2) * 2, (y + 19) * 2, lab if not (n == N - 1 and on) else "F33 ?", fill=col, align="c")

def falling_factor(c, T):
    """the first factor drops out of a freshly cracked bell"""
    W = c.t
    for e in D:
        age = T - e["t"]
        if e["kind"] == "prime" or e["n"] == N - 1 or not (0 <= age < 1.1): continue
        if "p" not in e: continue
        x, y = cell_xy(e["n"])
        s = fmt(e["p"]); yy = (y + CH) * 2 + 2 + age * 50
        if yy > 456: continue
        xx = min(352 - 4 * len(s), max(8 + 4 * len(s), (x + CW / 2) * 2))
        W.rectangle([xx - 4 * len(s) - 3, yy + 1, xx + 4 * len(s) + 2, yy + 17], fill=PANEL)
        text(W, xx, yy, s, fill=RED, align="c")

def current(T):
    k = None
    for e in D:
        if e["t"] <= T: k = e
    return k

def hud(c, T):
    W = c.t; e = current(T)
    W.rectangle([12, 10, 348, 140], fill=PANEL); W.rectangle([12, 10, 348, 11], fill=GOLD); W.rectangle([12, 139, 348, 140], fill=GOLD)
    if e is None:
        return
    n = e["n"]; fresh = T - e["t"] < 0.15
    text(W, 22, 16, f"F{n} = 2^(2^{n}) + 1", fill=INK)
    text(W, 338, 16, f"{n + 1}/34", fill=INK2, align="r")
    if e["digits"] <= 20:
        v = 2 ** (2 ** n) + 1; s = fmt(v)
        text(W, 180, 40, s, size=40 if len(s) <= 20 else 20, fill=INK, align="c")
    else:
        text(W, 180, 40, f"{fmt(e['digits'])} DIGITS", size=40, fill=INK, align="c")
    if n == N - 1:
        text(W, 180, 86, "PRIME? NOBODY KNOWS", fill=GOLD, align="c")
        text(W, 180, 108, "SMALLEST UNKNOWN CASE", fill=INK2, align="c")
    elif e["kind"] == "prime":
        text(W, 180, 86, "PRIME  (FERMAT, 1640)", fill=GREEN, align="c")
        text(W, 180, 108, "RIGHT NOTE", fill=INK2, align="c")
    else:
        text(W, 180, 86, f"NOT PRIME  ({e['year']})", fill=RED, align="c")
        if n in NOFACTOR: sub = "NO FACTOR KNOWN, EVEN TODAY"
        elif n in FACT_LATER: sub = f"PEPIN TEST. 1ST FACTOR: {FACT_LATER[n]}"
        elif n == 5: sub = "= 641 x 6,700,417  (EULER)"
        elif n == 6: sub = "= 274,177 x 67,280,421,310,721"
        else: sub = f"DIVISIBLE BY {fmt(e['p'])}" if len(fmt(e['p'])) <= 22 else f"FACTOR: {len(str(e['p']))} DIGITS"
        text(W, 180, 108, sub, fill=INK2, align="c")
        if n > 5: text(W, 338, 16 + 0, "", fill=INK2, align="r")
    who_s = who(e) if n != N - 1 else ""
    if who_s and e["kind"] != "prime": text(W, 22, 124 - 2, "", fill=INK2)

def banner(c, T):
    W = c.t
    for t0, t1, l1, l2, ck in BANNERS:
        if t0 <= T < t1:
            a = min(1, (T - t0) / .15)
            w = 344; yb = 478
            W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 38], fill=PANEL); W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=COL[ck])
            text(W, 180, yb + 3, l1, fill=COL[ck], align="c")
            if a >= 1 or True: text(W, 180, yb + 19, l2, fill=INK, align="c")
            return True
    return False

def bottom(c, T):
    W = c.t
    W.rectangle([0, 520, 360, 640], fill=PANEL); W.rectangle([0, 520, 360, 521], fill=GOLD)
    pl = [e for e in D[:-1] if e["t"] <= T]
    r = sum(1 for e in pl if e["kind"] == "prime"); w = len(pl) - r
    text(W, 14, 528, "RIGHT", fill=GREEN); text(W, 70, 528, str(r), fill=GREEN)
    text(W, 112, 528, "WRONG", fill=RED); text(W, 168, 528, str(w), fill=RED)
    text(W, 214, 528, "UNKNOWN", fill=GOLD if T >= D[-1]["t"] else INK2); text(W, 286, 528, "1" if T >= D[-1]["t"] else "-", fill=GOLD if T >= D[-1]["t"] else INK2)
    # year line 1640 -> 2026 (small marker, not the heart of the image)
    x0, x1, yl = 24, 336, 584
    W.line([x0, yl, x1, yl], fill=INK2)
    for yr in (1640, 1700, 1800, 1900, 2000):
        xx = x0 + (yr - 1640) / (2026 - 1640) * (x1 - x0); W.line([xx, yl - 3, xx, yl + 3], fill=INK2)
    text(W, x0, 594, "1640", fill=INK2); text(W, 180, 594, "YEAR PROVEN", fill=INK2, align="c"); text(W, x1, 594, "2026", fill=INK2, align="r")
    stack = {}
    for e in pl:
        yr = int(e["year"]); xx = x0 + (yr - 1640) / (2026 - 1640) * (x1 - x0)
        k = stack.get(yr, 0); stack[yr] = k + 1
        col = GREEN if e["kind"] == "prime" else RED
        yy = yl - 6 - k * 4
        fresh = T - e["t"] < .3
        W.rectangle([xx - 1 - fresh, yy - 1 - fresh, xx + 1 + fresh, yy + 1 + fresh], fill=col)
    text(W, 180, 614, "EVERY BEEP = ONE FERMAT NUMBER", fill=INK2, align="c")

def sc_main(t):
    T = t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_wall(c, T)
    hud(c, T); falling_factor(c, T); b = banner(c, T); bottom(c, T)
    W = c.t
    if T < 4.2:                                           # title over the wall, first bell already ringing
        W.rectangle([12, 10, 348, 140], fill=PANEL); W.rectangle([12, 10, 348, 11], fill=GOLD); W.rectangle([12, 139, 348, 140], fill=GOLD)
        text(W, 180, 18, "FERMAT SAID ALL", size=40, fill=INK, align="c")
        text(W, 180, 52, "THESE ARE PRIME", size=40, fill=INK, align="c")
        if T > 0.6: text(W, 180, 92, "ONLY THE FIRST 5 ARE", size=20, fill=RED, align="c")
        if T > 1.4: text(W, 180, 114, "Fn = 2^(2^n) + 1", fill=INK2, align="c")
        if T > 1.0 and not b:
            W.rectangle([8, 478, 352, 516], fill=PANEL); W.rectangle([8, 478, 352, 480], fill=GOLD)
            text(W, 180, 481, "EVERY BEEP = ONE FERMAT NUMBER", fill=INK, align="c")
            text(W, 180, 497, "GREEN = PRIME   RED = NOT PRIME", fill=INK2, align="c")
    return c

def sc_outro(t):
    T = OUTRO_T + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_wall(c, T); bottom(c, T)
    W = c.t
    W.rectangle([12, 10, 348, 140], fill=PANEL); W.rectangle([12, 10, 348, 11], fill=GOLD); W.rectangle([12, 139, 348, 140], fill=GOLD)
    text(W, 22, 18, "5 RIGHT NOTES", size=40, fill=GREEN)
    if t > .6: text(W, 22, 56, "28 WRONG NOTES", size=40, fill=RED)
    if t > 1.2: text(W, 22, 96, "1 UNKNOWN (F33)", size=20, fill=GOLD)
    if t > 1.2: text(W, 338, 96, "1640 -> 2001", fill=INK2, align="r")
    if t > 2.5:
        W.rectangle([8, 480, 352, 518], fill=PANEL); W.rectangle([8, 480, 352, 482], fill=GOLD)
        text(W, 180, 483, "IS THERE A 6TH FERMAT PRIME?", fill=INK, align="c")
        if t > 3.5: text(W, 180, 500, "NOBODY HAS FOUND ONE IN 386 YEARS", fill=GOLD, align="c")
    if t > 6.5:
        W.rectangle([0, 520, 360, 640], fill=PANEL); W.rectangle([0, 520, 360, 521], fill=GOLD)
        text(W, 180, 538, "DATA: W. KELLER, FERMAT FACTORING", fill=INK2, align="c")
        text(W, 180, 558, "STATUS · MATHWORLD · PRIME PAGES", fill=INK2, align="c")
        text(W, 180, 578, "MATH. COMP. (1963-1982)", fill=INK2, align="c")
        text(W, 180, 604, "EVERY FACTOR RE-CHECKED", fill=INK2, align="c")
    return c

SCENEFN = {"main": sc_main, "outro": sc_outro}

def compose_layers(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tb = np.repeat(np.repeat(np.array(c.txt), 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

GROOVE_OFF = (D[-1]["t"], D[-1]["t"] + 2.5)              # silence on F33
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    c = SCENEFN[name](t)
    fr = compose_layers(c)
    last = [e for e in D[:-1] if e["t"] <= T]
    if last:
        a = T - last[-1]["t"]
        if a < .12 and name == "main":
            z = 1.0 + (0.012 if last[-1]["kind"] != "prime" else 0.006) * (1 - a / .12) * FXK
            fr = warp(fr, z, 0, 0, z)
        if last[-1]["n"] == 5 and a < .18:                # Euler: the big break flashes red
            k = (1 - a / .18) * .35 * FXK
            fr = (fr * (1 - k) + np.array(RED) * k).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    return fr

# ================= audio (decision 2/4: B "Chiptune enquete", from fermat_primes_moods.py mood_b) =================
SR = 44100
CHORD = [0, 4, 7, 12, 16]
def note_pitch(n):
    if n <= 4: return 72 + CHORD[n]
    return 73 + ((n - 5) * 5) % 14                         # wrong notes: never on the chord
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def env(m, a, dd):
        tt = np.arange(m) / SR; return np.minimum(1, tt / max(a, 1e-4)) * np.exp(-tt / dd)
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    n = int((TOTAL + 0.5) * SR); L = np.zeros(n)
    def put(t0, s, g=1.0):
        i = int(t0 * SR); j = min(n, i + len(s))
        if 0 <= i < n: L[i:j] += g * s[:j - i]
    def noise(dur, fc, dec, seed, hp=None):
        m = int(dur * SR); s = lowpass(np.random.RandomState(seed).randn(m), fc)
        if hp: s = highpass(s, hp)
        return s * np.exp(-np.arange(m) / SR * dec)
    def kick(g=.26, f0=120, f1=50):
        m = int(.35 * SR); tt = np.arange(m) / SR
        return g * np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 16) + f1) / SR) * np.exp(-tt * 12)
    def square(f, dur, duty=.25):
        m = int(dur * SR); ph = (f * np.arange(m) / SR) % 1
        return np.where(ph < duty, 1.0, -1.0)
    for k, b in enumerate(np.arange(0, TOTAL, BEAT)):
        if GROOVE_OFF[0] - 0.01 <= b < GROOVE_OFF[1]: continue
        g = 1.0
        if b < 1.0: g = .6
        if b >= OUTRO_T: g = .75
        if b >= TOTAL - 4: g *= max(0, (TOTAL - 0.5 - b) / 3.5)
        put(b, kick(.20 * g) if k % 2 == 0 else noise(.12, 5000, 30, k, 900), 1 if k % 2 == 0 else .10 * g)
        put(b + BEAT / 2, noise(.03, 9000, 140, 90 + k, 6000), .04 * g)
        r = [36, 36, 41, 43][(k // 4) % 4]
        if b >= 9.5 and b < OUTRO_T: r = [36, 36, 37, 43][(k // 4) % 4]   # after Euler the bass gets a sour b2
        put(b, .05 * g * lowpass(square(mtof(r), BEAT * .8, .5), 1200) * env(int(BEAT * .8 * SR), .002, .2))
    for e in D[:-1]:
        tm, m = e["t"], note_pitch(e["n"]); f = mtof(m)
        if e["kind"] == "prime":
            nn = int(.5 * SR); put(tm, .13 * square(f, .5, .25) * env(nn, .002, .15))
            put(tm + .09, .06 * square(f * 2, .5, .125) * env(nn, .002, .1))
        else:
            big = 1.6 if e["n"] == 5 else 1.0
            nn = int(.45 * SR); tt = np.arange(nn) / SR
            fs = f * np.exp(-tt * 2.2)
            s = np.where(((np.cumsum(fs) / SR) % 1) < .5, 1.0, -1.0)
            put(tm, .13 * big * s * env(nn, .002, .3))
            put(tm, .06 * big * square(f * 1.414, .45, .5) * env(nn, .002, .25))
            put(tm, noise(.18, 6000, 18, 300 + e["n"], 700), .12 * big)
    # F33: one soft open "?" blip after the silence starts (not a note: the number is unknown)
    tt = np.arange(int(.25 * SR)) / SR
    put(D[-1]["t"] + 1.0, .03 * np.sin(2 * np.pi * 1320 * tt) * np.exp(-tt * 14))
    out = L.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28)]:
        q = int(dl * SR); out[q:] += g * .6 * L[:-q]
    x = .88 * L + .12 * lowpass(out, 4000)
    tt = np.arange(len(x)) / SR; x *= np.clip((TOTAL + 0.3 - tt) / 1.5, 0, 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(len(x) / SR, 2), "s")

def render_scene(args):
    idx, out, a, b = args; name = NAMES[idx]
    tmp, fin = f"{out}/{idx:02d}_{name}_{a:05d}.tmp.mp4", f"{out}/{idx:02d}_{name}_{a:05d}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(a, b): p.stdin.write(render_frame(idx, f / FPS - START[name]).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio":
        render_audio(out); sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}_{PAL}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, nm in enumerate(NAMES) if START[nm] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}_{PAL}.png")
    elif mode == "info":
        print("total", TOTAL, "s ·", N, "Fermat numbers ·", sum(e["kind"] == "prime" for e in D), "prime")
        for e in D: print(f"F{e['n']:<2} t={e['t']:5.1f} {e['kind']:8} {e['year']:5} {who(e)}")
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        jobs = []
        for i, nm in enumerate(NAMES):
            f0 = int(round(START[nm] * FPS)); f1 = int(round((START[nm] + DUR[nm]) * FPS))
            for a in range(f0, f1, 240): jobs.append((i, out, a, min(f1, a + 240)))
        with Pool(min(6, os.cpu_count() or 3)) as pool: print(len(pool.map(render_scene, jobs)), "chunks")
