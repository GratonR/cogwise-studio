"""BEEPMELODY — Mersenne's list (co-pilot: step 1 = « liste », step 2 = A · « De la plume à la machine »).
In 1644 the friar Marin Mersenne listed the exponents p for which he claimed 2^p - 1 is prime (p <= 257): 11 numbers.
5 were wrong (67 and 257 are not prime; 61, 89 and 107 are missing). It took until 1931 to fix the list,
then from 1952 machines found 40 more Mersenne primes, up to M136279841 (Oct 2024, 41,024,320 digits).
Every event of mersenne_list_draft.csv = one note at its own moment:
  act 1  the 11 numbers of the list, one harpsichord note each (the 2 wrong ones are sour notes);
  act 2  the 6 corrections 1876-1931 (wrong note -> resolves), with Cole at the blackboard in 1903
         (one chalk click per written digit);
  act 3  the 40 primes found by computer 1952-2024 on a date-linear clock (0.4 s / year): square-wave chiptune
         on a soft 104 BPM pulse, the machine prints one ticket per prime.
Pitch = log of p (acts 1-2) / log of the digit count (act 3).

    python3 mersenne_list.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
Env: ML_VARIANT=era (parchment, then dark terminal from 1952, default) | parch (light parchment all along)
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

FXK = float(os.environ.get("PI_FX", "0.8"))
VARIANT = os.environ.get("ML_VARIANT", "era")

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "mersenne_list_draft.csv"))))
def frac_year(d):
    parts = d.split("-"); y = int(parts[0])
    m = int(parts[1]) if len(parts) > 1 else 6
    dd = int(parts[2]) if len(parts) > 2 else 15
    return y + (m - 1) / 12 + (dd - 1) / 365
LIST = [r for r in ROWS if r["kind"] == "list"]
FIX = [r for r in ROWS if r["kind"] == "fix"]
FOUND = sorted([r for r in ROWS if r["kind"] == "found"], key=lambda r: r["date"])
for r in ROWS:
    r["p"] = int(r["p"]); r["yf"] = frac_year(r["date"])
    r["dg"] = int(r["digits"]) if r["digits"] else len(str(2 ** r["p"] - 1)) if r["p"] < 400 else 0
WRONG = {67, 257}
MISSING = {61, 89, 107}
SLOTS = sorted({r["p"] for r in LIST} | MISSING)          # 14 cells of the page
assert len(LIST) == 11 and len(FIX) == 6 and len(FOUND) == 40

# ================= clock =================
T_LIST = [0.30 + i * 0.62 for i in range(11)]          # act 1: one note per number of the list
T_REVEAL = 7.10                                          # "5 WERE WRONG"
T2 = 9.60                                                # act 2 starts: the years roll from 1644
COLE0 = 15.30                                            # blackboard scene
CW0 = COLE0 + 0.9                                        # left side written digit by digit
CW1 = CW0 + 21 * 0.075 + 0.5                             # right side
CEQ = CW1 + 21 * 0.075 + 0.35                            # the two sides match
COLE1 = CEQ + 2.9
FIX_T = {1876: 12.60, 1883: 14.30, 1903: CEQ, 1911: COLE1 + 1.4, 1914: COLE1 + 2.9, 1931: COLE1 + 4.9}
T_287 = FIX_T[1931] + 0.6                                # "287 YEARS" banner
T3 = T_287 + 4.1                                         # act 3: 1952
SPY = 0.40                                               # seconds per year in act 3
Y3 = 1952.0
def t_found(yf): return T3 + (yf - Y3) * SPY
FT = []
last = -9
for r in FOUND:
    t = max(t_found(r["yf"]), last + 0.10); FT.append(round(t, 3)); last = t
T_FINAL = FT[-1]
T_HOLD = T_FINAL + 4.0
OUTRO = 5.2
TOTAL = T_HOLD + OUTRO

# year keyframes (time -> year shown in the HUD)
YK = [(0, 1644), (T2 + 0.4, 1644), (FIX_T[1876] - 0.2, 1876), (FIX_T[1876] + 0.5, 1876), (FIX_T[1883] - 0.2, 1883),
      (FIX_T[1883] + 0.4, 1883), (COLE0 - 0.1, 1903), (COLE1 + 0.3, 1903), (FIX_T[1911] - 0.2, 1911),
      (FIX_T[1911] + 0.3, 1911), (FIX_T[1914] - 0.2, 1914), (FIX_T[1914] + 0.4, 1914), (FIX_T[1931] - 0.2, 1931),
      (T_287 + 2.6, 1931), (T3 - 0.15, 1952)]
def year_f(T):
    if T >= T3 - 0.15: return min(Y3 + (T - T3) / SPY, 2024 + 9.4 / 12) if T < T_FINAL else 2024 + 9.4 / 12
    for (t0, y0), (t1, y1) in zip(YK, YK[1:]):
        if t0 <= T < t1: return lerp(y0, y1, ease((T - t0) / (t1 - t0)))
    return YK[-1][1]
def rolling(T):
    if T >= T3 - 0.15: return False
    for (t0, y0), (t1, y1) in zip(YK, YK[1:]):
        if t0 <= T < t1: return y1 != y0
    return False

SC = [("list", T2), ("fixes", COLE0 - T2), ("cole", COLE1 - COLE0), ("fixes2", T3 - COLE1), ("machines", T_HOLD - T3), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

# ================= palette =================
PAPER, PAPER2, PAPER3 = (244, 230, 198), (232, 214, 176), (214, 192, 150)
INK, INK2 = (58, 40, 26), (128, 100, 72)
RED, RED2 = (196, 58, 40), (150, 40, 28)
GREEN, GOLD, GOLD2 = (58, 140, 76), (214, 150, 40), (170, 108, 20)
CREAM, WHITE = (255, 249, 236), (255, 255, 255)
BOARD, BOARD2, CHALK = (40, 62, 52), (30, 48, 40), (232, 236, 224)
if VARIANT == "parch":
    SCR, SCR2, AMB, AMB2, SCRTXT = PAPER, PAPER2, GOLD2, GOLD, INK
else:
    SCR, SCR2, AMB, AMB2, SCRTXT = (22, 26, 30), (34, 40, 46), (255, 184, 70), (255, 214, 130), (236, 228, 206)
def dark(T): return VARIANT != "parch" and T >= T3 - 0.15

# ================= music plan =================
DMIN = [0, 2, 3, 5, 7, 8, 10]
def note_p(p, base=62, span=13):
    u = (math.log(p) - math.log(2)) / (math.log(257) - math.log(2)); k = int(round(u * span))
    return base + 12 * (k // 7) + DMIN[k % 7]
def note_d(dg, base=62, span=14):
    u = (math.log10(dg) - math.log10(157)) / (math.log10(41024320) - math.log10(157)); k = int(round(u * span))
    return base + 12 * (k // 7) + DMIN[k % 7]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
COLE_A = "147573952589676412927"            # 2^67 - 1
COLE_B, COLE_C = "193707721", "761838257287"
assert int(COLE_A) == 2 ** 67 - 1 == int(COLE_B) * int(COLE_C)
def build():
    ev(0.0, "organ", d=T3 - 0.2, v=1.0)
    for i, r in enumerate(LIST):
        ev(T_LIST[i], "pluck", m=note_p(r["p"]) + (1 if r["p"] in WRONG else 0), v=0.42 if r["p"] in WRONG else 0.36)
    ev(T_REVEAL, "cluster", v=0.30)
    for r in FIX:
        t = FIX_T[int(r["year"])]; m = note_p(r["p"])
        if r["p"] in WRONG:
            ev(t, "pluck", m=m + 1, v=0.40); ev(t + 0.42, "pluck", m=m, v=0.42); ev(t + 0.42, "pluck", m=m - 12, v=0.25)
        elif r["p"] in MISSING:
            ev(t, "pluck", m=m - 5, v=0.30); ev(t + 0.16, "pluck", m=m, v=0.42); ev(t + 0.16, "pluck", m=m + 12, v=0.18)
        else:
            ev(t, "pluck", m=m, v=0.42); ev(t, "pluck", m=m + 12, v=0.22)
    for k in range(21):
        ev(CW0 + k * 0.075, "chalk", s=k, v=0.5)
    for k in range(9): ev(CW1 + k * 0.075, "chalk", s=40 + k, v=0.5)
    for k in range(12): ev(CW1 + (9 + k) * 0.075 + 0.12, "chalk", s=60 + k, v=0.5)
    ev(T_287, "cluster", v=0.18)
    beat = 60 / 104.0
    b = T3; k = 0
    while b < T_HOLD + 1.6:
        bar = int((b - T3) / (beat * 4))
        ev(b, "bass", m=[38, 34, 36, 33][bar % 4] + (12 if k % 2 else 0), d=beat * 0.45, v=0.10 if b < T_HOLD else 0.06)
        if k % 2: ev(b, "hat", v=0.05)
        if k % 4 == 0 and b < T_HOLD: ev(b, "kick", v=0.14)
        if k % 8 == 0: ev(b, "pad", m=[50, 46, 48, 45][bar % 4], d=beat * 4, v=0.06)
        b += beat / 2; k += 1
    for i, r in enumerate(FOUND):
        m = note_d(r["dg"]); last = i == len(FOUND) - 1
        ev(FT[i], "sq", m=m + 12, v=0.30 if not last else 0.40)
        ev(FT[i] + beat * 0.75, "sq", m=m + 12, v=0.10)
    for j, iv in enumerate([0, 3, 7, 12, 15, 19, 24]):
        ev(T_FINAL + 0.12 + j * 0.11, "sq", m=note_d(41024320) + iv, v=0.20)
    ev(T_FINAL, "crash", v=0.25); ev(T_FINAL - 1.6, "riser", d=1.6, v=0.10)
    ev(T_HOLD, "pluck", m=50, v=0.35); ev(T_HOLD, "pad", m=50, d=4.0, v=0.10)
    EV.sort(key=lambda e: e[0])
build()
HITS = sorted([FT[i] for i in range(len(FT))])

# ================= drawing helpers =================
def parchment():
    a = np.zeros((AH, AW, 3), np.float32); a[:] = PAPER
    rng = np.random.default_rng(3)
    n = rng.random((AH, AW)); a[n > 0.93] = PAPER2; a[n > 0.993] = PAPER3
    yy, xx = np.mgrid[0:AH, 0:AW]
    v = 1 - 0.10 * (((xx - AW / 2) / (AW / 2)) ** 2 + ((yy - AH / 2) / (AH / 2)) ** 2)
    return Image.fromarray((a * v[..., None]).clip(0, 255).astype(np.uint8))
_PARCH = parchment()
def screen_bg():
    a = np.zeros((AH, AW, 3), np.uint8); a[:] = SCR
    a[::3] = SCR2 if VARIANT != "parch" else PAPER2
    return Image.fromarray(a)
_SCREEN = screen_bg()
def board_bg():
    a = np.zeros((AH, AW, 3), np.float32); a[:] = BOARD
    rng = np.random.default_rng(5); n = rng.random((AH, AW)); a[n > 0.9] = BOARD2
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    d.rectangle([0, 268, AW, AH], fill=(120, 84, 50)); d.rectangle([0, 268, AW, 270], fill=(150, 108, 66))
    return img
_BOARD = board_bg()

def slot_rc(p):
    i = SLOTS.index(p); return i % 7, i // 7          # row, col
def slot_box(p):
    r, c = slot_rc(p); x0 = 26 + c * 158; y0 = 214 + r * 40
    return x0, y0, x0 + 150, y0 + 34

def slot_state(p, T):
    """'hidden' | 'written' | 'wrong' | 'missing' | 'prime' | 'notprime'"""
    if p in MISSING:
        if T < T_REVEAL: return "hidden"
        fy = {61: 1883, 89: 1911, 107: 1914}[p]
        return "prime" if T >= FIX_T[fy] else "missing"
    i = [r["p"] for r in LIST].index(p)
    if T < T_LIST[i]: return "hidden"
    if p == 67: return "notprime" if T >= FIX_T[1903] else "wrong" if T >= T_REVEAL else "written"
    if p == 257: return "notprime" if T >= FIX_T[1931] + 0.42 else "wrong" if T >= T_REVEAL else "written"
    if p == 127 and T >= FIX_T[1876]: return "prime"
    return "written"
def slot_age(p, T):
    if p in MISSING: return T - FIX_T[{61: 1883, 89: 1911, 107: 1914}[p]]
    if p == 67: return T - FIX_T[1903]
    if p == 257: return T - FIX_T[1931]
    if p == 127: return T - FIX_T[1876]
    return 9

def check(W, x, y, col):
    for k, (dx, dy) in enumerate([(0, 6), (2, 8), (4, 10), (6, 8), (8, 6), (10, 4), (12, 2), (14, 0)]):
        W.rectangle([x + dx, y + dy, x + dx + 2, y + dy + 2], fill=col)
def cross(W, x, y, col):
    for k in range(7):
        W.rectangle([x + 2 * k, y + 2 * k, x + 2 * k + 2, y + 2 * k + 2], fill=col)
        W.rectangle([x + 12 - 2 * k, y + 2 * k, x + 14 - 2 * k, y + 2 * k + 2], fill=col)

def draw_page(c, T, alpha=1.0):
    W = c.t
    W.rectangle([18, 192, 342, 498], fill=(250, 240, 214)); W.rectangle([18, 192, 342, 194], fill=INK2)
    text(W, 180, 196, "MERSENNE 1644: \"2^p - 1 IS PRIME FOR\"", fill=INK2, align="c")
    for p in SLOTS:
        st = slot_state(p, T); x0, y0, x1, y1 = slot_box(p); a = slot_age(p, T)
        if st == "hidden": continue
        lab = f"2^{p} - 1"
        if st == "missing":
            on = int(T * 3) % 2 == 0
            W.rectangle([x0, y0, x1, y1], outline=RED if on else INK2)
            text(W, x0 + 8, y0 + 7, "?  MISSING", fill=RED if on else INK2); continue
        flash = 0 <= a < 0.3
        W.rectangle([x0, y0, x1, y1], fill=CREAM if not flash else WHITE)
        col = INK
        if st == "wrong": col = RED
        if st == "notprime": col = RED2
        if st == "prime" and p in MISSING: col = GREEN
        text(W, x0 + 8, y0 + 7, lab, fill=col)
        if st == "prime": check(W, x1 - 22, y0 + 10, GREEN)
        if st == "notprime":
            W.rectangle([x0 + 6, y0 + 17, x0 + 8 + 8 * len(lab), y0 + 18], fill=RED)
            cross(W, x1 - 22, y0 + 10, RED)
        if st == "wrong" and int(T * 3) % 2 == 0: W.rectangle([x0, y0, x1, y1], outline=RED)
        if st == "written":                                       # quill stroke under the newest number
            i = [r["p"] for r in LIST].index(p)
            if 0 <= T - T_LIST[i] < 0.5:
                k = int((T - T_LIST[i]) / 0.5 * 8 * len(lab)); W.rectangle([x0 + 8, y0 + 27, x0 + 8 + k, y0 + 28], fill=INK2)

def draw_quill(c, T):
    """a pixel quill that hops to the newest written cell (act 1)"""
    k = max([i for i in range(11) if T >= T_LIST[i]], default=-1)
    if k < 0 or T > T_REVEAL: return
    p = LIST[k]["p"]; x0, y0, x1, y1 = slot_box(p)
    a = min(1, (T - T_LIST[k]) / 0.5); qx = (x0 + 8 + a * 8 * len(f"2^{p} - 1")) / 2; qy = (y0 + 24) / 2
    d = c.a
    d.line([qx, qy, qx + 10, qy - 16], fill=INK)
    d.polygon([(qx + 6, qy - 10), (qx + 16, qy - 22), (qx + 13, qy - 9)], fill=WHITE, outline=INK2)

def timeline(c, T):
    W = c.t; dk = dark(T)
    x0, x1, y = 30, 330, 600
    W.rectangle([x0, y, x1, y + 1], fill=INK2 if not dk else (120, 120, 110))
    def xx(yf): return x0 + (yf - 1640) / (2026 - 1640) * (x1 - x0)
    for r in LIST:
        if T >= T_LIST[0]: W.rectangle([xx(1644) - 1, y - 7, xx(1644), y - 1], fill=INK if not dk else AMB)
    for r in FIX:
        if T >= FIX_T[int(r["year"])]: W.rectangle([xx(r["yf"]) - 1, y - 7, xx(r["yf"]), y - 1], fill=RED if r["p"] in WRONG else GREEN)
    for i, r in enumerate(FOUND):
        if T >= FT[i]: W.rectangle([xx(r["yf"]) - 1, y - 7, xx(r["yf"]), y - 1], fill=AMB if dk else GOLD2)
    cur = xx(min(year_f(T), 2025)); W.rectangle([cur - 1, y + 3, cur + 1, y + 8], fill=RED)
    tc = INK2 if not dk else (170, 160, 140)
    text(W, x0, y + 10, "1644", fill=tc); text(W, x1, y + 10, "2024", fill=tc, align="r")

def banner_box(W, yb, tt, sub, big, a, col=RED, bg=CREAM, ink=INK):
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    hgt = (62 if big else 42) if sub else (44 if big else 24)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=bg)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=ink, align="c")
        if sub and a > 0.25: text(W, 180, yb + 40, sub, fill=col, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=ink, align="c")
        if sub and a > 0.25: text(W, 180, yb + 21, sub, fill=col, align="c")

BANNERS = [  # t0, t1, title, sub, big, colour
    (T_REVEAL, T2 - 0.1, "5 WERE WRONG", "2 NOT PRIME · 3 MISSING", True, RED),
    (T2 + 0.3, FIX_T[1876] - 0.15, "232 YEARS", "NOBODY CAN CHECK THEM", True, INK2),
    (FIX_T[1876] + 0.05, FIX_T[1876] + 1.5, "LUCAS: M127 IS PRIME", "(THE LIST WAS RIGHT)", False, GREEN),
    (FIX_T[1883] + 0.05, FIX_T[1883] + 0.95, "PERVUSHIN: M61 IS PRIME", "(NOT ON THE LIST)", False, GREEN),
    (COLE1, COLE1 + 1.2, "COLE: M67 IS NOT PRIME", "(ON THE LIST BY MISTAKE)", False, RED),
    (FIX_T[1911] + 0.05, FIX_T[1911] + 1.3, "POWERS: M89 IS PRIME", "(NOT ON THE LIST)", False, GREEN),
    (FIX_T[1914] + 0.05, FIX_T[1914] + 1.5, "POWERS: M107 IS PRIME", "(NOT ON THE LIST)", False, GREEN),
    (FIX_T[1931] + 0.45, T_287, "LEHMER: M257 IS NOT PRIME", "(ON THE LIST BY MISTAKE)", False, RED),
    (T_287, T_287 + 2.6, "287 YEARS", "TO FIX ONE LIST (1644-1931)", True, RED),
    (T_287 + 2.7, T3 - 0.2, "21 YEARS OF NOTHING", "THEN THE MACHINES ARRIVE", False, INK2),
]
def banner(c, T, yb=136):
    for t0, t1, tt, sub, big, col in BANNERS:
        if t0 <= T < t1: banner_box(c.t, yb, tt, sub, big, T - t0, col)

def hud(c, T):
    W = c.t; dk = dark(T)
    bg = CREAM if not dk else (36, 42, 48); ink = INK if not dk else SCRTXT; ink2 = INK2 if not dk else (170, 160, 140)
    W.rectangle([16, 18, 344, 122], fill=bg); W.rectangle([16, 18, 344, 19], fill=ink); W.rectangle([16, 121, 344, 122], fill=ink)
    yr = int(year_f(T)); ro = rolling(T)
    text(W, 334, 46, str(yr), size=40, fill=(RED if ro else GOLD2) if not dk else AMB, align="r")
    if ro: text(W, 334, 24, ">> YEARS GO BY", fill=RED, align="r")
    if T < T3 - 0.15:
        ok = sum(1 for p in SLOTS if slot_state(p, T) in ("prime",)) + sum(1 for p in SLOTS if slot_state(p, T) == "written" and p not in WRONG and T >= T_REVEAL)
        fixed = sum(1 for r in FIX if r["p"] != 127 and T >= FIX_T[int(r["year"])] + (0.42 if r["p"] in WRONG else 0))
        text(W, 28, 24, "MERSENNE'S LIST", fill=ink2)
        if T < T_REVEAL:
            n = sum(1 for t in T_LIST if T >= t)
            text(W, 28, 46, f"{n} / 11", size=40, fill=ink); text(W, 28, 94, "NUMBERS ON THE LIST", fill=ink2)
        else:
            text(W, 28, 46, f"{fixed} / 5", size=40, fill=RED if fixed < 5 else GREEN)
            text(W, 28, 94, "MISTAKES FIXED", fill=ink2)
        return
    i = max([k for k in range(len(FT)) if T >= FT[k]], default=-1)
    text(W, 28, 24, "NEW MERSENNE PRIME", fill=ink2)
    if i < 0:
        text(W, 28, 46, "2^127 - 1", size=40, fill=ink); text(W, 28, 94, "39 DIGITS (SINCE 1876)", fill=ink2); return
    r = FOUND[i]; age = T - FT[i]
    big = len(f"2^{r['p']:,} - 1") <= 12
    text(W, 28, 46 if big else 58, f"2^{r['p']:,} - 1", size=40 if big else 20, fill=AMB2 if age < 0.15 else ink)
    if len(f"2^{r['p']:,} - 1") > 12: pass
    text(W, 28, 94, f"{r['dg']:,} DIGITS", fill=AMB if dk else GOLD2)

def machine_kind(r):
    y = int(r["year"])
    if y <= 1963: return "valve"
    if y <= 1994: return "super"
    if y <= 2018: return "pc"
    return "gpu"
def machine_name(r):
    lab = r["label"]
    if lab.startswith("GIMPS"):
        who = lab.replace("GIMPS ", "").replace(" Pentium 90 MHz", "").replace(" (rank 52 provisional)", "")
        if "Pentium" in lab: return "GIMPS · " + who.upper() + " · PENTIUM PC"
        if r["year"] == "2024": return "GIMPS · " + who.upper() + " · CLOUD GPUS"
        return "GIMPS · " + who.upper() + " · VOLUNTEER PC"
    return lab.upper()

def draw_machine(c, T, kind, flash):
    d = c.a; cx, gy = 90, 262
    body = (70, 78, 86) if dark(T) else (150, 132, 108); hi = AMB if flash else ((120, 130, 120) if dark(T) else (200, 180, 150))
    if kind == "valve":
        for k in range(3):
            x0 = cx - 33 + k * 23; d.rectangle([x0, gy - 46, x0 + 20, gy], fill=body)
            for yy in range(gy - 42, gy - 6, 6):
                for xx in range(x0 + 3, x0 + 18, 4):
                    d.point((xx, yy), fill=hi if (xx + yy + int(T * 8)) % 3 == 0 or flash else (60, 60, 60))
            d.rectangle([x0 + 4, gy - 10, x0 + 16, gy - 6], fill=(40, 40, 44))
    elif kind == "super":
        d.pieslice([cx - 30, gy - 44, cx + 30, gy + 16], 180, 360, fill=body)
        d.rectangle([cx - 30, gy - 14, cx + 30, gy], fill=(120, 60, 60) if not flash else hi)
        d.pieslice([cx - 12, gy - 30, cx + 12, gy - 6], 180, 360, fill=(30, 30, 34))
        for xx in range(cx - 26, cx + 27, 4): d.line([xx, gy - 16, xx, gy - 26 + abs(xx - cx) // 3], fill=(90, 96, 104) if not flash else hi)
    elif kind == "pc":
        d.rectangle([cx - 36, gy - 40, cx - 4, gy - 14], fill=body); d.rectangle([cx - 33, gy - 37, cx - 7, gy - 17], fill=(20, 30, 24) if not flash else hi)
        for k in range(3): d.line([cx - 31, gy - 33 + k * 5, cx - 31 + ((int(T * 20) + k * 7) % 20), gy - 33 + k * 5], fill=(90, 200, 120))
        d.rectangle([cx - 26, gy - 14, cx - 14, gy - 10], fill=body); d.rectangle([cx - 34, gy - 10, cx - 6, gy - 7], fill=body)
        d.rectangle([cx + 6, gy - 44, cx + 26, gy], fill=body); d.rectangle([cx + 9, gy - 40, cx + 23, gy - 36], fill=(60, 60, 60))
        d.point((cx + 22, gy - 8), fill=hi)
    else:
        d.rectangle([cx - 40, gy - 26, cx + 40, gy - 4], fill=(40, 44, 50)); d.rectangle([cx - 40, gy - 4, cx + 40, gy - 1], fill=GOLD2)
        for k in range(2):
            fx = cx - 20 + k * 40; d.ellipse([fx - 10, gy - 25, fx + 10, gy - 5], fill=(60, 66, 74))
            ang = T * 20 + k
            for j in range(3):
                a = ang + j * 2.1; d.line([fx, gy - 15, fx + 8 * math.cos(a), gy - 15 + 8 * math.sin(a)], fill=(110, 118, 128))
        d.rectangle([cx - 40, gy - 28, cx + 40, gy - 26], fill=hi)
    d.rectangle([0, gy, AW, gy + 2], fill=(60, 66, 74) if dark(T) else PAPER3)

def draw_tickets(c, T):
    """one ticket per prime, newest at the bottom (just above the machine), older ones pushed up"""
    W = c.t; dk = dark(T)
    i = max([k for k in range(len(FT)) if T >= FT[k]], default=-1)
    if i < 0: return
    a = T - FT[i]; slide = 1 - ease(min(1, a / 0.12))
    base = 398 + 30 * slide
    for j in range(i, max(-1, i - 9), -1):
        r = FOUND[j]; y = base - (i - j) * 30
        if y < 196: break
        new = j == i and a < 0.4
        bg = (AMB if new else (52, 58, 64)) if dk else (WHITE if new else CREAM)
        W.rectangle([40, y, 320, y + 24], fill=bg)
        W.rectangle([40, y, 43, y + 24], fill=AMB if dk else GOLD2)
        lab = f"M{r['p']:,}"
        ink = (20, 20, 20) if (dk and new) else (SCRTXT if dk else INK)
        rank = r["status"].replace("prime ", "")
        text(W, 50, y + 3, ("NEW " + lab) if j == len(FOUND) - 1 else (rank + "  " + lab), fill=ink)
        text(W, 312, y + 3, f"{r['dg']:,} DIG.", fill=ink, align="r")
    if i >= 0:
        W.rectangle([16, 540, 344, 562], fill=(36, 42, 48) if dk else CREAM)
        text(W, 180, 541, machine_name(FOUND[i])[:40], fill=AMB if dk else INK2, align="c")

BANNERS3 = [
    (FT[0] - 0.05, FT[4] + 0.6, "1952: 5 IN ONE YEAR", "ONE MACHINE (SWAC)", True),
    (FT[22] + 0.05, FT[22] + 1.7, "1996: A HOME PC", "FINDS ONE (PENTIUM 90 MHZ)", False),
    (T_FINAL + 0.05, T_HOLD, "41,024,320 DIGITS", "THE LARGEST PRIME KNOWN", True),
]
def banner3(c, T):
    dk = dark(T)
    for t0, t1, tt, sub, big in BANNERS3:
        if t0 <= T < t1: banner_box(c.t, 136, tt, sub, big, T - t0, AMB if dk else RED,
                                    (36, 42, 48) if dk else CREAM, SCRTXT if dk else INK)

def frame_ctx(T):
    if T >= T3 - 0.15: base = _SCREEN.copy() if dark(T) else _PARCH.copy()
    else: base = _PARCH.copy()
    c = Ctx(np.array(base)); return c

def sc_list(t):
    T = t; c = frame_ctx(T); W = c.t
    draw_page(c, T); draw_quill(c, T); timeline(c, T)
    if T < T_REVEAL:
        W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
        text(W, 28, 24, "IN 1644 A FRIAR", size=40, fill=INK)
        text(W, 28, 62, "LISTED 11 SPECIAL", size=40, fill=INK)
        text(W, 28, 100, "NUMBERS.", size=40, fill=GOLD2)
        if t > 0.9: text(W, 28, 146, "EVERY NOTE = ONE NUMBER ON THE LIST", fill=INK2)
        if t > 3.0: text(W, 180, 504, "HE SAID: ALL OF THESE ARE PRIME", fill=INK2, align="c")
    else:
        hud(c, T); banner(c, T)
    return c

def sc_fixes(name):
    def f(t):
        T = START[name] + t; c = frame_ctx(T)
        draw_page(c, T); timeline(c, T); hud(c, T); banner(c, T)
        return c
    return f

def sc_cole(t):
    T = COLE0 + t
    c = Ctx(np.array(_BOARD.copy())); W = c.t; d = c.a
    # Cole, a small pixel figure at the board
    fx = 140; d.rectangle([fx, 236, fx + 10, 268], fill=(40, 36, 44)); d.ellipse([fx + 1, 224, fx + 9, 234], fill=(232, 196, 160))
    arm = 236 + (int(T * 12) % 3 if CW0 <= T < CEQ else 0)
    d.line([fx, arm, fx - 8, arm - 6], fill=(40, 36, 44)); d.point((fx - 9, arm - 7), fill=CHALK)
    text(W, 180, 30, "OCTOBER 1903, NEW YORK", fill=(200, 210, 196), align="c")
    text(W, 180, 52, "F. N. COLE WALKS TO THE BOARD", fill=(200, 210, 196), align="c")
    def chalk_digits(x, y, s, t0, size=20):
        n = max(0, min(len(s), int((T - t0) / 0.075) + 1)) if T >= t0 else 0
        text(W, x, y, s[:n], size=size, fill=CHALK)
    text(W, 24, 110, "2^67 - 1 =", size=40, fill=CHALK)
    chalk_digits(24, 160, COLE_A, CW0)
    if T >= CW1 - 0.2:
        chalk_digits(24, 230, COLE_B, CW1)
        if T >= CW1 + 9 * 0.075: text(W, 24 + 9 * 8 + 6, 230, "x", fill=CHALK)
        chalk_digits(24 + 10 * 8 + 12, 230, COLE_C, CW1 + 9 * 0.075 + 0.12)
    if T >= CEQ:
        text(W, 24, 262, "= " + COLE_A, fill=(250, 220, 120))
        a = T - CEQ
        if a > 0.3: banner_box(W, 330, "SAME NUMBER.", "SO M67 IS NOT PRIME", True, a - 0.3, RED, CREAM, INK)
        if a > 1.6: text(W, 180, 410, "THE STORY GOES: HE NEVER SAID A WORD.", fill=(200, 210, 196), align="c")
    timeline(c, T)
    return c

def sc_machines(t):
    T = T3 + t; c = frame_ctx(T)
    i = max([k for k in range(len(FT)) if T >= FT[k]], default=0)
    flash = any(0 <= T - x < 0.12 for x in FT)
    draw_machine(c, T, machine_kind(FOUND[i]), flash)
    draw_tickets(c, T); timeline(c, T); hud(c, T); banner3(c, T)
    return c

def sc_outro(t):
    T = T_HOLD + t; c = frame_ctx(T); W = c.t; dk = dark(T)
    bg = (36, 42, 48) if dk else CREAM; ink = SCRTXT if dk else INK; ink2 = (170, 160, 140) if dk else INK2; acc = AMB if dk else GOLD2
    draw_machine(c, T, "gpu", False); timeline(c, T)
    W.rectangle([16, 40, 344, 330], fill=bg); W.rectangle([16, 40, 344, 42], fill=acc)
    text(W, 180, 50, "THE LIST: 11 NUMBERS", fill=ink2, align="c")
    if t > 0.2: text(W, 180, 72, "5 WRONG", size=40, fill=RED, align="c")
    if t > 0.6: text(W, 180, 116, "287 YEARS TO FIX IT", fill=ink, align="c")
    if t > 1.1:
        text(W, 180, 152, "TODAY'S RECORD (OCT 2024):", fill=ink2, align="c")
        text(W, 180, 174, "2^136,279,841 - 1", size=40, fill=acc, align="c")
        text(W, 180, 216, "41,024,320 DIGITS", fill=ink, align="c")
    if t > 1.7: text(W, 180, 250, "52 MERSENNE PRIMES KNOWN", fill=ink2, align="c")
    if t > 2.2: text(W, 180, 286, "GUESS: WHEN DO WE FIND #53?", fill=RED, align="c")
    if t > 2.6:
        W.rectangle([16, 336, 344, 380], fill=bg)
        text(W, 180, 338, "DATA: GIMPS (MERSENNE.ORG), PRIMEPAGES,", fill=ink2, align="c")
        text(W, 180, 358, "R. C. ARCHIBALD, \"MERSENNE'S NUMBERS\".", fill=ink2, align="c")
    return c

SCENEFN = {"list": sc_list, "fixes": sc_fixes("fixes"), "cole": sc_cole, "fixes2": sc_fixes("fixes2"),
           "machines": sc_machines, "outro": sc_outro}

def compose_light(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt); tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

KICKS = sorted([FIX_T[y] + (0.42 if y in (1903, 1931) else 0) for y in FIX_T] + [T_REVEAL, T_FINAL, CEQ])
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(SCENEFN[name](t))
    bi = np.searchsorted(KICKS, T, side="right") - 1
    if bi >= 0 and T - KICKS[bi] < 0.22:
        a = T - KICKS[bi]; s = int(round(8 * FXK * math.exp(-a / 0.06) * math.sin(a * 90)))
        fr = np.roll(fr, s, axis=0)
    hi = np.searchsorted(HITS, T, side="right") - 1
    if name == "machines" and hi >= 0 and T - HITS[hi] < 0.06:
        fr = np.minimum(255, fr.astype(np.int16) + int(30 * FXK)).astype(np.uint8)
    for t0, dd in ((T3 - 0.15, 0.35), (COLE0, 0.25), (COLE1, 0.25)):    # cuts
        if 0 <= T - t0 < dd:
            f = 1 - ease((T - t0) / dd); fr = (fr * (1 - f) + np.array(WHITE) * f).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "list":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio (mood A · from quill to machine) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    rng = np.random.RandomState(5)
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(t, x, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(x)); L[i:j] += x[:j - i] * (1 - pan) ** .5 * .9; R[i:j] += x[:j - i] * (1 + pan) ** .5 * .9
    def pluck(f, dur=1.3, bright=.5):
        m_ = int(dur * SR); N = max(2, int(SR / f)); buf = np.random.RandomState(int(f)).uniform(-1, 1, N); y = np.zeros(m_)
        for i in range(m_):
            y[i] = buf[i % N]; buf[i % N] = bright * buf[i % N] + (1 - bright) * .5 * (buf[i % N] + buf[(i + 1) % N]) * .996
        return y * np.exp(-np.arange(m_) / SR * 1.5)
    def tone(f, dur, wave="sin", dec=4.0, a=.003, duty=.25):
        m_ = int(dur * SR); t = np.arange(m_) / SR
        s = np.sin(2 * np.pi * f * t) if wave == "sin" else np.where((f * t) % 1 < duty, 1.0, -1.0) if wave == "sq" else 2 * np.abs(2 * ((f * t) % 1) - 1) - 1
        return s * np.minimum(1, t / a) * np.exp(-t * dec)
    for t, k, kw in EV:
        v = kw.get("v", .3)
        if k == "organ":
            d = kw["d"]; m_ = int(d * SR); tt = np.arange(m_) / SR
            prog = [[38, 50, 53, 57], [34, 46, 50, 53], [31, 43, 50, 55], [33, 45, 49, 52]]
            x = np.zeros(m_)
            for b in range(int(d / 4.0) + 1):
                i0, i1 = int(b * 4.0 * SR), min(m_, int((b + 1) * 4.0 * SR))
                if i0 >= m_: break
                seg = tt[i0:i1]
                for mm in prog[b % 4]:
                    x[i0:i1] += .012 * np.sin(2 * np.pi * mtof(mm) * seg) * (1 + .25 * np.sin(2 * np.pi * 5 * seg))
            fade = np.minimum(1, tt / 0.3) * np.clip((d - tt) / 0.6, 0, 1)
            sil = np.ones(m_)                                            # thinner during the Cole scene
            sil[int(COLE0 * SR):int(COLE1 * SR)] = .35
            put(t, lowpass(x, 2000) * fade * sil * v * 3.0)
        elif k == "pluck":
            put(t, v * .9 * pluck(mtof(kw["m"])), -.15)
        elif k == "cluster":
            put(t, v * sum(tone(mtof(mm), 1.6, "sin", dec=2.0) for mm in (37, 38, 44, 49)))
        elif k == "chalk":
            m_ = int(.05 * SR); x = highpass(lowpass(np.random.RandomState(kw["s"]).randn(m_), 9000), 2500) * np.exp(-np.arange(m_) / SR * 70)
            put(t, x * v * .5, .3)
        elif k == "sq":
            put(t, v * .55 * lowpass(tone(mtof(kw["m"]), .35, "sq", dec=7, duty=.125), 5000), .15)
        elif k == "bass":
            put(t, v * lowpass(tone(mtof(kw["m"]), kw["d"], "tri", dec=8), 900))
        elif k == "hat":
            m_ = int(.04 * SR); put(t, highpass(rng.randn(m_), 6000) * np.exp(-np.arange(m_) / SR * 80) * v, -.3)
        elif k == "kick":
            m_ = int(.3 * SR); tt = np.arange(m_) / SR
            put(t, v * np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 20) + 45) / SR) * np.exp(-tt * 12))
        elif k == "pad":
            d = kw["d"]; m_ = int((d + .5) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .4) * np.clip((d + .4 - tt) / .4, 0, 1)
            x = sum(np.where((mtof(kw["m"] + iv) * tt) % 1 < .5, 1, -1) for iv in (0, 7, 12))
            put(t, lowpass(x * e, 1400) * v * .3)
        elif k == "crash":
            m_ = int(1.4 * SR); x = highpass(lowpass(rng.randn(m_), 8000), 3000) * np.exp(-np.arange(m_) / SR * 3); put(t, x * v * .35)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR; put(t, highpass(rng.randn(m_), 2500) * (tt / kw["d"]) ** 2 * v)
    def reverb(x, mix=.3):
        out = x.copy()
        for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
            k_ = int(dl * SR); out[k_:] += g * .6 * x[:-k_]
        return (1 - mix) * x + mix * lowpass(out, 4000)
    L = reverb(np.tanh(L * 1.4) / 1.4); R = reverb(np.roll(np.tanh(R * 1.4) / 1.4, int(.011 * SR)))
    tt = np.arange(n) / SR; fade = np.clip((TOTAL - tt) / 1.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max()); st = np.stack([L, R], 1) / mx * .89
    wavfile.write(path, SR, (st * 32767).astype(np.int16)); print(path, round(n / SR, 2), "s")

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
        print("found times", FT[:6], "...", FT[-3:])
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
