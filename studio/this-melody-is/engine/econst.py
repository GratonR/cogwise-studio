"""THIS MELODY IS e — event-driven pixel short (engine shared with pi.py / phi.py)."""
import sys, os, math, random, subprocess
from fractions import Fraction
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, CREAM, YEL, RED, DIM, GREEN, GREEN_HI, text, panel, ease, eout, mix, shade,
                pix_arc, pix_line, lerp, bg, noise)
import pi as PIM
from pi import Ctx, mkbg, upto, last_change, warp, glitch_frame

FXK = float(os.environ.get("PI_FX", "1"))
FINAL = "eniac"
SCALE = [69, 72, 74, 76, 79, 81, 84, 86, 88, 91]   # A minor pentatonic: every digit is consonant

# ---------- digits of e (series with big ints) ----------
def e_digits(n):
    u = 10 ** (n + 10); s = 0; term = u; k = 0
    while term: s += term; k += 1; term //= k
    d = str(s // 10 ** 10); return d[0] + "." + d[1:n]
EC = e_digits(2600)
ED = [int(c) for c in EC if c.isdigit()]
EV_ = math.e

def correct_mask(s):
    out, ok = [], True
    for i, ch in enumerate(s):
        ok = ok and i < len(EC) and EC[i] == ch
        out.append(ok)
    return out
def cols_for(s): return [CREAM if ok else RED for ok in correct_mask(s)]

SC = [("intro", 4.0), ("bernoulli", 8.6), ("montmort", 8.6), ("euler37", 6.8), ("euler48", 7.4), ("rutherford", 8.8),
      ("montecarlo", 9.2), ("eniac", 6.2), ("outro", 4.6)]
START, acc = {}, 0.0
for n, d in SC: START[n] = acc; acc += d
TOTAL = acc
DUR = dict(SC)
NAMES = [n for n, _ in SC]

def bpm(t): return 136 + 56 * ease(t / START[FINAL]) ** 1.3 + 40 * ease((t - START[FINAL]) / 5.2)
def beat_times(T):
    out, t = [], 0.0
    while t < T: out.append(t); t += 60 / bpm(t)
    return out
_G = None
def grid16(t_from, n, every=1):
    global _G
    if _G is None:
        _G = []
        for b in beat_times(TOTAL + 2):
            bl = 60 / bpm(b); _G += [b + k * bl / 4 for k in range(4)]
    g = [x for x in _G if x >= t_from - 1e-6]
    return g[::every][:n]

EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def type_events(s, t_start, every, tag):
    ok = correct_mask(s); gt = grid16(t_start, len(s), every); times = []
    for i, ch in enumerate(s):
        times.append(gt[i])
        if ch.isdigit(): ev(gt[i], "digit", d=int(ch), ok=ok[i], tag=tag)
    return times
def thin(times, maxrate):
    out, last = [], -1
    for t in times:
        if t - last >= 1 / maxrate: out.append(t); last = t
    return out
def accel_times(t0, t1, r0, r1):
    """event times between t0 and t1 with rate growing exponentially r0 -> r1"""
    out, t = [], t0
    while t < t1:
        out.append(t); r = r0 * (r1 / r0) ** ((t - t0) / (t1 - t0)); t += 1 / r
    return out

SCH = {}
def build():
    SCH["intro"] = type_events("2.71828182845904", START["intro"] + 0.15, 2, "intro")
    ev(START["bernoulli"] - 0.5, "riser")
    # BERNOULLI: compound interest sweeps
    st = START["bernoulli"]; t = st + 0.25; SCH["sweeps"] = []
    for n, d in ((1, 0.8), (2, 0.8), (4, 0.85), (12, 0.9), (52, 0.95), (365, 1.0), (8760, 1.05)):
        ts = [t + d * (k + 1) / n for k in range(n)]
        SCH["sweeps"].append((n, t, d))
        amt = 1.0
        for k, x in enumerate(ts):
            amt *= 1 + 1 / n
            if n <= 52 or k % max(1, n // 200) == 0: ev(x, "coin", a=amt, rate=n / d)
        ev(t + d + 0.03, "chime", lvl=min(5, len(SCH["sweeps"]) - 1))
        t += d + 0.12
    # MONTMORT: hats, trials accelerate
    st = START["montmort"]
    times = accel_times(st + 0.3, st + DUR["montmort"] - 0.6, 2.2, 130)
    N = len(times); best = None
    for seed in range(30000):
        rng = random.Random(seed); perms = []; D = 0
        for _ in range(N):
            p = list(range(8)); rng.shuffle(p); der = all(p[i] != i for i in range(8)); D += der; perms.append((p, der))
        if D == round(N / math.e) and abs(N / D - math.e) < 0.004: best = perms; break
    if best is None:
        rng = random.Random(1); best = []
        for _ in range(N):
            p = list(range(8)); rng.shuffle(p); best.append((p, all(p[i] != i for i in range(8))))
    SCH["hats"] = [(x, p, der) for x, (p, der) in zip(times, best)]
    keep = set(thin(times, 140))
    for i, (x, p, der) in enumerate(SCH["hats"]):
        if x in keep: ev(x, "hat_trial", der=der, i=i, rate=1 / max(1e-3, (times[i + 1] - x) if i + 1 < N else 0.1))
    # EULER 1737: continued fraction
    st = START["euler37"]
    SCH["cf_lv"] = [st + 0.3 + k * 0.38 for k in range(7)]
    for x in SCH["cf_lv"]: ev(x, "chalk")
    pts, t = [], st + 0.5
    for i in range(22): pts.append(t); t += 0.34 * 0.88 ** i
    SCH["cf_pts"] = pts
    for i, x in enumerate(pts): ev(x, "term", k=i, rate=1 / (0.34 * 0.88 ** i))
    # EULER 1748: series 1/n!
    st = START["euler48"]; t = st + 0.3; SCH["terms48"] = []
    for n in range(19):
        SCH["terms48"].append(t); ev(t, "block", n=n); t += max(0.09, 0.48 * 0.86 ** n)
    SCH["e48_end"] = t
    # RUTHERFORD: three decay runs, Geiger clicks
    st = START["rutherford"]; t = st + 0.25; SCH["runs"] = []
    for N0, side, win in ((400, 20, 2.0), (2500, 50, 2.4), (10000, 100, 3.0)):
        best = None
        for seed in range(4000):
            rng = np.random.default_rng(seed)
            life = rng.exponential(1.0, N0)
            left = int((life > 1.0).sum())
            if abs(N0 / left - math.e) < (0.02 if N0 < 1000 else 0.004): best = life; break
        SCH["runs"].append(dict(N0=N0, side=side, t0=t, win=win, life=best, left=int((best > 1).sum())))
        dts = np.sort(best[best <= 1.0]) * (win * 0.8) + t
        for x in thin(list(dts), 260): ev(float(x), "geiger")
        ev(t + win * 0.82, "chime", lvl=len(SCH["runs"]) + 1)
        t += win + 0.2
    # MONTE CARLO: sticks
    st = START["montecarlo"]
    stimes = accel_times(st + 0.3, st + DUR["montecarlo"] - 0.6, 5, 220)
    best = None
    for seed in range(30000):
        rng = random.Random(seed); sticks = []; trials = []; s = 0; k = 0
        for _ in stimes:
            L = rng.random(); s += L; k += 1; sticks.append(L)
            if s > 1: trials.append(k); s = 0; k = 0
        if len(trials) > 20 and abs(sum(trials) / len(trials) - math.e) < 0.003: best = (sticks, trials); break
    SCH["sticks"] = list(zip(stimes, best[0]))
    keep = set(thin(stimes, 200))
    for x, L in SCH["sticks"]:
        if x in keep: ev(x, "stick", L=L)
    # ENIAC finale
    st = START[FINAL]; t, i = st + 0.3, 0; SCH["stream"] = []
    while t < st + 4.9:
        r = 10 * (12 ** ((t - st) / 4.9)); SCH["stream"].append((t, i)); ev(t, "edigit", d=ED[i], rate=r); t += 1 / r; i += 1
    ev(st + 5.45, "glitch")
    ev(START["outro"], "final")
    drums_and_glitches()

CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
KICKS, SNARES, GL = [], [], []
def scene_at(t):
    for n, d in SC:
        if START[n] <= t < START[n] + d: return n
    return "outro"
def drums_and_glitches():
    E = START[FINAL]
    for bi, bt in enumerate(beat_times(TOTAL)):
        if bt >= START["outro"] - 0.05: break
        sc = scene_at(bt); bl = 60 / bpm(bt); pos = bi % 4
        ch = CHORDS[(bi // 4) % 4]; root = ch[0] - 12
        quiet = sc in ("euler37",)
        light = sc in ("intro", "bernoulli")
        fin = sc == FINAL and bt > E + 3.4
        if sc != "intro":
            if quiet:
                if pos == 0: ev(bt, "kick", v=0.42)
            else:
                ev(bt, "kick", v=0.36 if light else 0.5)
                if fin or (sc == FINAL and bt > E + 2.0) or (sc in ("montecarlo",) and pos == 3): ev(bt + bl / 2, "kick", v=0.34)
            if not light and not quiet and pos in (1, 3) and not fin: ev(bt, "snare", v=0.22)
            if fin:
                div = 4 if bt < E + 4.4 else 8
                for h in range(div): ev(bt + h * bl / div, "snare", v=0.08 + 0.14 * (h + 1) / div)
        if not quiet or pos % 2 == 0:
            sub = 4 if sc in ("rutherford", "montecarlo", FINAL) else 2
            for h in range(sub):
                if sc == "intro" and h % 2: continue
                ev(bt + h * bl / sub, "hat", v=0.04 if h % 2 else 0.055, open=(h == sub // 2 and sc != "intro"))
        for h in range(2):
            if sc == "intro" and h == 1: continue
            m = root + (12 if (pos * 2 + h) % 4 == 3 else 0) + (int(3 * ease((bt - E - 3.4) / 1.6)) * 2 if fin else 0)
            ev(bt + h * bl / 2, "bass", m=m, d=bl / 2 * 0.9, v=0.2 if sc != "intro" else 0.15)
        if pos == 0: ev(bt, "pad", ch=ch, d=bl * 4)    # pad everywhere: glue + harmony under the digits
    for t, k, kw in EV:
        if k == "kick": KICKS.append(t)
        if k == "snare" and kw["v"] > 0.15: SNARES.append(t)
    KICKS.sort(); SNARES.sort()
    def bl_at(t): return 60 / bpm(t)
    # crescendo: no glitches early, a few transitions mid, a storm at the end
    for n_, div in (("rutherford", 4), ("montecarlo", 8), (FINAL, 8)):
        d = 0.22 if div == 4 else 0.26
        GL.append((START[n_] - d, d, "stutter", bl_at(START[n_]) / div))
    GL.append((START["montecarlo"] + 6.0, 0.18, "crush", 0))
    GL.append((E + 2.2, 0.18, "stutter", bl_at(E + 2.2) / 4))
    GL.append((E + 3.2, 0.22, "crush", 0))
    GL.append((E + 3.9, 0.2, "stutter", bl_at(E + 3.9) / 8))
    GL.append((E + 4.45, 0.15, "stutter", bl_at(E + 4.45) / 16))
    GL.append((E + 4.95, 0.5, "tapestop", 0))
    GL.sort()

build()
EV.sort(key=lambda e: e[0])

# ================= visuals =================
def typed(s, times, T):
    n = upto(times, T); v = s[:n]; return v, cols_for(v)

def exp_graph(c, prog, tag=True):
    ox, oy, sx, sy = 70, 230, 50, 32          # origin (x=0,y=0), px per unit
    c.a.line([14, oy, 170, oy], fill=(80, 150, 190)); c.a.line([ox, 236, ox, 108], fill=(80, 150, 190))
    for k in (-1, 1, 2):
        c.a.line([ox + k * sx, oy - 2, ox + k * sx, oy + 2], fill=CREAM); text(c.t, (ox + k * sx) * 2 - 4, oy * 2 + 8, str(k), fill=DIM)
    for k in (1, 2, 3):
        c.a.line([ox - 2, oy - k * sy, ox + 2, oy - k * sy], fill=CREAM); text(c.t, ox * 2 - 16, (oy - k * sy) * 2 - 10, str(k), fill=DIM)
    xs = np.linspace(-1.1, 1.0 + 0.32 * (prog > 0.99), 200)
    xm = -1.1 + (2.1) * prog
    pts = [(ox + x * sx, oy - math.exp(x) * sy) for x in xs if x <= xm and oy - math.exp(x) * sy > 100]
    if len(pts) > 1:
        c.a.line(pts, fill=(170, 120, 30), width=1); c.a.line([(p[0], p[1] - 1) for p in pts], fill=YEL)
    if prog >= 0.99:
        X, Y = ox + sx, oy - math.e * sy
        for y in range(int(Y), oy, 3): c.a.point((X, y), fill=RED)
        for x in range(ox, int(X), 3): c.a.point((x, Y), fill=RED)
        c.a.rectangle([X - 2, Y - 2, X + 2, Y + 2], fill=RED)
        if tag:
            c.t.rectangle([ox * 2 - 34, Y * 2 - 9, ox * 2 - 20, Y * 2 + 7], fill=YEL); text(c.t, ox * 2 - 31, Y * 2 - 11, "e", fill=(30, 20, 10))

def sc_intro(t):
    c = Ctx(bg("grid")); T = START["intro"] + t
    c.t.rectangle([30, 76, 252, 158], fill=(6, 7, 12))
    text(c.t, 40, 74, "THIS MELODY", size=40); text(c.t, 40, 112, "IS e", size=40)
    s = "2.71828182845904"; v = s[:upto(SCH["intro"], T)]
    text(c.t, 40, 506, v[:10], size=40)
    if len(v) > 10: text(c.t, 40, 544, v[10:], size=40)
    exp_graph(c, eout((t - 0.1) / 3.0))
    return c

def coin(d, x, y, shine=0):
    d.ellipse([x - 9, y - 2, x + 9, y + 2], fill=(150, 104, 20), outline=(90, 60, 10))
    d.ellipse([x - 9, y - 4, x + 9, y], fill=(236, 186, 60) if not shine else (255, 236, 150), outline=(140, 96, 20))
    d.line([x - 5, y - 3, x + 3, y - 3], fill=(255, 230, 140))

def sc_bernoulli(t):
    c = Ctx(bg("desk")); T = START["bernoulli"] + t
    base, unit = 286, 50          # stack: 1.0 -> 50 px
    gx = 112
    # ladder of previous results + e line
    eY = base - math.e * unit
    for x in range(14, 172, 4): c.a.line([x, eY, x + 1, eY], fill=RED)
    text(c.t, 340, eY * 2 - 18, "e", fill=RED, align="r")
    sw = [s for s in SCH["sweeps"] if s[1] <= T]
    amt, n_cur, prog = 1.0, None, 0
    for (n, t0, d) in sw:
        done = T >= t0 + d
        k = n if done else int((T - t0) / d * n)
        a = (1 + 1 / n) ** k
        if done:
            y = base - a * unit
            c.a.line([20, y, 70, y], fill=(150, 120, 80))
            if n <= 12: text(c.t, 40, y * 2 - 18, f"N={n}", fill=(200, 170, 120))
        amt, n_cur, prog = a, n, min(1, (T - t0) / d)
    # coin stack
    ncoins = int(amt * unit / 3)
    for k in range(ncoins):
        coin(c.a, gx, base - k * 3, shine=(k == ncoins - 1 and t % 0.2 < 0.1))
    # year bar with period ticks and a running marker
    if n_cur:
        y0 = 96
        c.a.rectangle([14, y0, 166, y0 + 6], fill=(40, 26, 16), outline=(150, 110, 60))
        if n_cur <= 52:
            for k in range(1, n_cur): x = 14 + 152 * k / n_cur; c.a.line([x, y0 + 1, x, y0 + 5], fill=(150, 110, 60))
        c.a.rectangle([14, y0 + 1, 14 + 152 * prog, y0 + 5], fill=(236, 186, 60))
        text(c.t, 28, (y0 + 7) * 2, "1 YEAR AT 100%", fill=(200, 170, 120))
    sweeps_done = [s for s in SCH["sweeps"] if s[1] + s[2] <= T]
    if n_cur:
        val = f"{amt:.5f}"
        lastdone = sweeps_done[-1] if sweeps_done else None
        panel(c.t, "BERNOULLI 1683", val, "(1 + 1/N)^N", cols_for(val), right=["PERIODS", str(n_cur)],
              age=(T - lastdone[1] - lastdone[2]) if lastdone else None)
    else:
        panel(c.t, "BERNOULLI 1683", "1.00000", "(1 + 1/N)^N", [DIM] * 7, right=["PERIODS", "-"])
    return c

HAT_COLS = [(220, 70, 60), (240, 170, 50), (90, 180, 80), (70, 140, 220), (160, 90, 200), (230, 120, 170), (80, 200, 200), (240, 240, 230)]
def gentleman(d, x, y, col):
    d.rectangle([x - 4, y + 8, x + 4, y + 22], fill=(40, 40, 52))          # coat
    d.rectangle([x - 1, y + 8, x + 1, y + 12], fill=(236, 232, 222))       # shirt
    d.point((x, y + 10), fill=col)                                          # bow tie colour = his hat
    d.rectangle([x - 3, y, x + 3, y + 7], fill=(236, 196, 160)); d.point((x - 1, y + 3), fill=(40, 30, 30)); d.point((x + 2, y + 3), fill=(40, 30, 30))
    d.line([x - 1, y + 5, x + 1, y + 5], fill=(170, 110, 90))
    d.rectangle([x - 4, y + 22, x - 1, y + 24], fill=(20, 20, 24)); d.rectangle([x + 1, y + 22, x + 4, y + 24], fill=(20, 20, 24))
def tophat(d, x, y, col):
    d.rectangle([x - 5, y, x + 5, y + 1], fill=shade(col, 0.6)); d.rectangle([x - 3, y - 7, x + 3, y], fill=col)
    d.line([x - 3, y - 2, x + 3, y - 2], fill=shade(col, 0.5)); d.line([x - 3, y - 7, x - 3, y], fill=mix(col, (255, 255, 255), 0.4))

def sc_montmort(t):
    c = Ctx(mkbg("planks24")); T = START["montmort"] + t
    hats = SCH["hats"]; n = upto([h[0] for h in hats], T)
    D = sum(1 for h in hats[:n] if h[2])
    c.a.rectangle([0, 96, AW, 172], fill=(70, 40, 26)); c.a.line([0, 172, AW, 172], fill=(40, 22, 12))
    for k in range(8):
        x = 13 + k * 22; gentleman(c.a, x, 136, HAT_COLS[k])
    if n:
        x0, p, der = hats[n - 1]; age = T - x0
        drop = int(max(0, 1 - age / 0.06) * 10)
        for k in range(8):
            x = 13 + k * 22; tophat(c.a, x, 135 - drop, HAT_COLS[p[k]])
            if p[k] == k: text(c.t, x * 2, 330, "X", fill=RED, align="c")
        if der and age < 0.25:
            text(c.t, 180, 350, "NOBODY GOT HIS HAT!", fill=(120, 230, 120), align="c")
    # tally bars
    W = c.t
    text(W, 50, 400, "TRIALS", fill=CREAM); text(W, 310, 400, str(n), fill=YEL, align="r")
    text(W, 50, 424, "NO MATCH", fill=CREAM); text(W, 310, 424, str(D), fill=YEL, align="r")
    w = 260
    W.rectangle([50, 452, 50 + w, 462], fill=(40, 26, 18)); W.rectangle([50, 452, 50 + int(w * (D / n if n else 0)), 462], fill=(120, 230, 120))
    x1e = 50 + w / math.e; W.rectangle([x1e, 446, x1e + 1, 468], fill=RED); text(W, x1e, 470, "1/e", fill=RED, align="c")
    if D:
        val = f"{n / D:.5f}"
        panel(c.t, "MONTMORT 1708", val, "TRIALS / NO-MATCH", cols_for(val), right=["HATS", "8"])
    else:
        panel(c.t, "MONTMORT 1708", "-", "TRIALS / NO-MATCH", [DIM], right=["HATS", "8"])
    return c

CFQ = [2, 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10, 1, 1, 12, 1, 1, 14, 1, 1, 16]
def cf_convergents(q, n):
    out = []
    for k in range(1, n + 1):
        x = Fraction(q[k - 1])
        for a in reversed(q[:k - 1]): x = a + 1 / x
        out.append(float(x))
    return out
CFV = cf_convergents(CFQ, 22)

def sc_euler37(t):
    c = Ctx(bg("chalk")); T = START["euler37"] + t; W = c.t; chalk = (232, 236, 226)
    nlv = upto(SCH["cf_lv"], T)
    x1 = 44 + 5 * 30 + 60
    for k in range(min(6, nlv)):
        x, y = 44 + k * 30, 176 + k * 26
        q = ease((T - SCH["cf_lv"][k]) / 0.25)
        text(W, x, y + 10, f"{CFQ[k]} +", fill=chalk if k not in (2, 5) else YEL)
        if k < 5:
            W.rectangle([x + 30, y + 21, x + 30 + int((x1 - x - 30) * q), y + 22], fill=chalk)
            if q > 0.6: text(W, x + 30 + (x1 - x - 30) / 2 - 4, y + 2, "1", fill=chalk)
    if nlv >= 7: text(W, 44 + 5 * 30 + 30, 176 + 5 * 26 + 10, "...", fill=chalk)
    gx0, gy, gs = 22, 252, 34
    for x in range(14, 166, 4): c.a.line([x, gy, x + 1, gy], fill=(220, 120, 110))
    text(W, 336, gy * 2 - 10, "e", fill=(220, 120, 110), align="r")
    np_ = upto(SCH["cf_pts"], T)
    pts = [(gx0 + i * 6.4, gy - max(-1, min(1, (CFV[i] - math.e) * 2.0)) * gs) for i in range(np_)]
    for i in range(1, len(pts)): c.a.line([pts[i - 1], pts[i]], fill=(214, 218, 206))
    for p in pts: c.a.rectangle([p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1], fill=(250, 250, 240))
    if t > 3.4: text(W, 180, 570, "2; 1,2,1, 1,4,1, 1,6,1 ...", fill=YEL, align="c")
    c.txt = v2.chalkify(c.txt, (30, 170, 340, 600), int(t * 4)); c.t = ImageDraw.Draw(c.txt); c.t.fontmode = "1"
    if np_:
        val = f"{CFV[np_ - 1]:.8f}"
        panel(c.t, "EULER 1737", val, "CONTINUED FRACTION", cols_for(val), right=["TERMS", str(np_)], age=T - SCH["cf_pts"][np_ - 1], style="dark")
    else:
        panel(c.t, "EULER 1737", "-", "CONTINUED FRACTION", [DIM], right=["TERMS", "0"], style="dark")
    return c

BLK = [(220, 90, 70), (240, 170, 60), (90, 180, 90), (70, 140, 220), (170, 100, 210), (230, 120, 170), (80, 200, 200)]
def sc_euler48(t):
    c = Ctx(PIM.mkbg("palm")); T = START["euler48"] + t; d = c.a
    # parchment strip with the series
    d.rounded_rectangle([8, 92, AW - 8, 110], 4, fill=(214, 186, 132)); d.line([10, 93, AW - 10, 93], fill=(236, 214, 166))
    n = upto(SCH["terms48"], T)
    s = "1 + 1 + 1/2 + 1/6 + 1/24 + 1/120 + ..."
    text(c.t, 180, 186, s[:max(0, min(len(s), 4 + n * 5))], fill=(70, 40, 18), align="c")
    base, unit, x0, w = 296, 64, 26, 40
    eY = base - math.e * unit
    for x in range(14, 96, 4): d.line([x, eY, x + 1, eY], fill=RED)
    text(c.t, 22, eY * 2 - 20, "e", fill=RED)
    S = 0.0
    for k in range(n):
        h = unit / math.factorial(k); y1 = base - S * unit; y0 = y1 - h
        col = BLK[k % len(BLK)]
        grow = ease((T - SCH["terms48"][k]) / 0.12)
        if h * grow >= 1:
            d.rectangle([x0, y1 - h * grow, x0 + w, y1], fill=col)
            d.line([x0, y1 - h * grow, x0 + w, y1 - h * grow], fill=mix(col, (255, 255, 255), 0.4))
        else:
            d.line([x0, y1, x0 + w, y1], fill=col)
        S += 1 / math.factorial(k)
    # magnifier on the top of the stack
    if n >= 4:
        mx0, my0, mx1, my1 = 92, 120, 172, 286
        d.rectangle([mx0 - 2, my0 - 2, mx1 + 2, my1 + 2], fill=(150, 120, 60)); d.rectangle([mx0, my0, mx1, my1], fill=(26, 18, 12))
        Z = unit * 6 * 4 ** (n - 4)
        cy = (my0 + my1) / 2
        ey = cy - 20
        S2, stop = 0.0, None
        for k in range(n):
            lo, hi = S2, S2 + 1 / math.factorial(k); S2 = hi
            ylo, yhi = ey + (math.e - lo) * Z, ey + (math.e - hi) * Z
            a, b = max(my0, min(my1, yhi)), max(my0, min(my1, ylo))
            if b - a >= 1: d.rectangle([mx0 + 16, a, mx1 - 16, b], fill=BLK[k % len(BLK)])
        for x in range(mx0, mx1, 4): d.line([x, ey, x + 1, ey], fill=RED)
        text(c.t, mx0 * 2 + 4, my0 * 2 + 2, f"ZOOM x{int(Z / unit)}", fill=YEL)
        # connector
        d.line([x0 + w, base - S * unit, mx0 - 2, my0], fill=(150, 120, 60)); d.line([x0 + w, base - S * unit, mx0 - 2, my1], fill=(150, 120, 60))
    if n:
        val = f"{S:.10f}"
        panel(c.t, "EULER 1748", val, "1/0! + 1/1! + 1/2! + ...", cols_for(val), right=["TERMS", str(n)], age=T - SCH["terms48"][n - 1])
    else:
        panel(c.t, "EULER 1748", "-", "1/0! + 1/1! + 1/2! + ...", [DIM], right=["TERMS", "0"])
    return c

def sc_rutherford(t):
    c = Ctx(PIM.mkbg("eniac")); T = START["rutherford"] + t; d = c.a
    runs = [r for r in SCH["runs"] if r["t0"] <= T]
    r = runs[-1] if runs else SCH["runs"][0]
    side = r["side"]; px = 120 // side
    gx0, gy0 = (AW - side * px) // 2, 120
    d.rectangle([gx0 - 4, gy0 - 4, gx0 + side * px + 3, gy0 + side * px + 3], fill=(60, 66, 70), outline=(20, 22, 24))
    d.rectangle([gx0 - 2, gy0 - 2, gx0 + side * px + 1, gy0 + side * px + 1], fill=(6, 10, 8))
    sim = min(1.0, max(0.0, (T - r["t0"]) / (r["win"] * 0.8)))
    life = r["life"]
    alive = life > sim
    arr = np.array(c.art)
    g = alive.reshape(side, side)
    flash = (life <= sim) & (life > sim - 0.03)
    col = np.zeros((side, side, 3), np.uint8)
    col[g] = (90, 240, 120); col[~g] = (40, 52, 46); col[flash.reshape(side, side)] = (255, 255, 220)
    big = np.repeat(np.repeat(col, px, 0), px, 1)
    if px >= 3: big[px - 1::px, :] = big[px - 1::px, :] // 2; big[:, px - 1::px] = big[:, px - 1::px] // 2
    arr[gy0:gy0 + side * px, gx0:gx0 + side * px] = big
    c.art = Image.fromarray(arr); c.a = ImageDraw.Draw(c.art)
    left = int(alive.sum())
    W = c.t
    text(W, 180, 506, f"ATOMS LEFT  {left}", fill=CREAM, align="c")
    # geiger counter dial
    rate = int(((life > sim - 0.05) & (life <= sim)).sum() / 0.05 * 1) if sim < 1 else 0
    text(W, 180, 530, f"CLICKS/S  {rate}", fill=GREEN, align="c")
    done = [x for x in SCH["runs"] if T >= x["t0"] + x["win"] * 0.82]
    if done:
        x = done[-1]; val = f"{x['N0'] / x['left']:.4f}"
        panel(c.t, "RUTHERFORD 1902", val, "N0 / N(LIFETIME)", cols_for(val), right=["ATOMS", str(r["N0"])], age=T - x["t0"] - x["win"] * 0.82)
    else:
        panel(c.t, "RUTHERFORD 1902", "-", "N0 / N(LIFETIME)", [DIM], right=["ATOMS", str(r["N0"])])
    return c

def felt_bg():
    if "felt" in PIM._B: return PIM._B["felt"]
    a = np.zeros((AH, AW, 3), np.float32); a[:] = (120, 24, 34)
    a *= (0.9 + 0.14 * noise((AH, AW), 61, 3))[..., None]
    a[:, :6] = (90, 56, 26); a[:, AW - 6:] = (90, 56, 26); a[:, 5] = (200, 160, 70); a[:, AW - 6] = (200, 160, 70)
    PIM._B["felt"] = np.clip(a, 0, 255).astype(np.uint8); return PIM._B["felt"]

def sc_montecarlo(t):
    c = Ctx(felt_bg()); T = START["montecarlo"] + t; d = c.a
    sticks = SCH["sticks"]; n = upto([x for x, _ in sticks], T)
    trials, cur, s, k = [], [], 0, 0
    for x, L in sticks[:n]:
        cur.append(L); s += L; k += 1
        if s > 1: trials.append(k); last_full = list(cur); s = 0; k = 0; cur = []
    bx0, bw, by = 22, 120, 128
    d.rectangle([bx0, by - 1, bx0 + bw, by + 7], outline=(230, 210, 150))
    d.line([bx0 + bw, by - 6, bx0 + bw, by + 12], fill=YEL); text(c.t, (bx0 + bw) * 2, (by + 14) * 2, "1", fill=YEL, align="c")
    show = cur if cur else (last_full if trials else [])
    x = bx0; cols = [(236, 210, 140), (210, 170, 90), (250, 230, 170), (190, 150, 80)]
    for j, L in enumerate(show):
        w = L * bw
        if w >= 1: d.rectangle([x, by, x + w - 1, by + 6], fill=cols[j % 4]); d.line([x, by, x + w - 1, by], fill=(255, 245, 210))
        x += w
    if not cur and trials: text(c.t, 180, (by + 12) * 2, f"{trials[-1]} STICKS!", fill=(120, 230, 120), align="c")
    # histogram of sticks-per-trial
    hx0, hy = 30, 290
    cnts = [sum(1 for v in trials if (v == kk if kk < 7 else v >= 7)) for kk in range(2, 8)]
    mxc = max(8, max(cnts) if cnts else 1)
    for kk in range(2, 8):
        cnt = cnts[kk - 2]
        h = cnt / mxc * 110
        bx = hx0 + (kk - 2) * 22
        d.rectangle([bx, hy - h, bx + 16, hy], fill=(236, 186, 60), outline=(120, 80, 20))
        text(c.t, (bx + 8) * 2, hy * 2 + 4, str(kk) if kk < 7 else "7+", fill=CREAM, align="c")
    if trials:
        val = f"{sum(trials) / len(trials):.5f}"
        panel(c.t, "MONTE CARLO 1949", val, "AVG STICKS TO PASS 1", cols_for(val), right=["TRIALS", str(len(trials))])
    else:
        panel(c.t, "MONTE CARLO 1949", "-", "AVG STICKS TO PASS 1", [DIM], right=["TRIALS", "0"])
    return c

def sc_eniac(t):
    c = Ctx(PIM.mkbg("eniac")); T = START[FINAL] + t
    n = upto([x for x, _ in SCH["stream"]], T)
    for k in range(3): PIM.eniac_rack(c.a, 8 + k * 56, 92, 50, 150, T, k * 17, n)
    count = max(n, min(2010, int(2010 * ease((t - 0.3) / 5.0) ** 1.4))) if t > 0.3 else 0
    W = c.t
    W.rectangle([30, 500, 330, 548], fill=(4, 10, 6)); W.rectangle([30, 500, 330, 548], outline=(50, 130, 80))
    s = EC.replace(".", "")
    for j in range(18):
        i = n - 14 + j
        if 0 <= i < len(s): text(W, 38 + j * 16, 502, s[i], size=40, fill=CREAM if j == 14 else (70, 170, 100) if j < 14 else (24, 70, 40))
    panel(c.t, "ENIAC 1949", f"{count} DIGITS", "IN ABOUT 11 HOURS", [CREAM] * 12, style="green", sub_col=GREEN)
    g = (t - 5.45) / 0.75
    if g > 0:
        rng = np.random.default_rng(int(t * 1000)); a = np.array(c.art); m = rng.random((AH, AW)) < ease(g * 1.4)
        pal = np.array([(40, 90, 110), (60, 130, 120), (30, 60, 100), (100, 160, 120)], np.uint8)
        a[m] = pal[rng.integers(0, 4, m.sum())]; c.art = Image.fromarray(a)
    return c

def sc_outro(t):
    c = Ctx(bg("grid"))
    lines = ["2.71828182", "84590452", "35360287", "47135266", "24977572"]
    for i, l in enumerate(lines):
        q = (t - i * 0.12) / 0.2
        if q > 0: text(c.t, 40, 96 + i * 40, l, size=40, fill=CREAM if i == 0 else mix((40, 50, 80), CREAM, min(1, q) * (1 - i * 0.16)))
    # small graph at the bottom
    cc = Ctx(bg("grid")); exp_graph(cc, 1.0, tag=False)
    a = np.array(c.art); b = np.array(cc.art); a[200:300] = b[130:230]; c.art = Image.fromarray(a); c.a = ImageDraw.Draw(c.art)
    if t > 1.2: text(c.t, 180, 610, "...AND IT NEVER ENDS", fill=DIM, align="c")
    return c

SCENEFN = {"intro": sc_intro, "bernoulli": sc_bernoulli, "montmort": sc_montmort, "euler37": sc_euler37, "euler48": sc_euler48,
           "rutherford": sc_rutherford, "montecarlo": sc_montecarlo, "eniac": sc_eniac, "outro": sc_outro}

# ---------- FX (same recipe as pi.py) ----------
def intensity(T): return 0.1 + 0.9 * ease(T / START[FINAL]) ** 2.2 + 0.5 * ease((T - START[FINAL]) / 5.0)
HOPS = None
def panel_hop(T):
    global HOPS
    if HOPS is None: HOPS = np.array(sorted([e[0] for e in EV if e[1] in ("digit", "edigit", "chime")] + KICKS))
    i = np.searchsorted(HOPS, T, side="right") - 1
    if i < 0: return 0
    d = T - HOPS[i]
    return int(round(-7 * FXK * math.exp(-d / 0.08) * abs(math.cos(2 * math.pi * d / 0.2))))
def active_glitch(T):
    for g in GL:
        if g[0] <= T < g[0] + g[1]: return g
    return None
def fx(fr, T, name, t):
    I = intensity(T) * FXK
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    si = np.searchsorted(SNARES, T, side="right") - 1
    sp = math.exp(-(T - SNARES[si]) / 0.06) if si >= 0 else 0.0
    if name == "outro": I *= 0.25
    push = 1.02 + 0.04 * I * ease(t / DUR[name])
    kd = (T - KICKS[ki]) if ki >= 0 else 9
    spring = math.exp(-kd / 0.11) * math.cos(2 * math.pi * kd / 0.17)
    zoom = push + kp * (0.015 + 0.035 * I)
    sd = (T - SNARES[si]) if si >= 0 else 9
    squash = math.exp(-sd / 0.09) * math.cos(2 * math.pi * sd / 0.14)
    zx = zoom * (1 - 0.025 * squash * I); zy = zoom * (1 + 0.05 * squash * I)
    rng = random.Random(int(T * 1000)); sh = sp * 14 * I
    sway = math.sin(T * 2 * math.pi / (60 / bpm(T)) / 2) * 10 * I * I
    dx = rng.uniform(-sh, sh) + sway; dy = -spring * (8 + 70 * I) + rng.uniform(-sh, sh)
    fr = warp(fr, zx, dx, dy, zy)
    split = int((sp * 14 + kp * 4) * max(0.0, I - 0.3))
    if split > 0:
        out = fr.copy(); out[:, split:, 0] = fr[:, :-split, 0]; out[:, :-split, 2] = fr[:, split:, 2]; fr = out
    fl = kp * (14 + 34 * I)
    if fl > 1: fr = np.minimum(255, fr.astype(np.int16) + int(fl)).astype(np.uint8)
    return fr
def strobe(fr, T):
    E = START[FINAL]
    if FXK >= 0.8 and E + 4.4 < T < E + 4.95:
        bl = 60 / bpm(T)
        if int((T - E) / (bl / 4)) % 2: fr = 255 - fr
    return fr

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    g = active_glitch(T)
    if g and g[2] == "stutter":
        T2 = g[0] + ((T - g[0]) % g[3]); t = T2 - START[name]
        if t < 0: idx -= 1; name = NAMES[idx]; t = T2 - START[name]
    if g and g[2] == "tapestop":
        p = (T - g[0]) / g[1]; T2 = g[0] + g[1] * (p - p * p / 2); t = T2 - START[name]
    c = SCENEFN[name](t)
    hop = panel_hop(START[name] + t)
    if hop:
        band = c.txt.crop((0, 60, TW, 162)); c.t.rectangle([0, 60, TW, 162], fill=(0, 0, 0, 0)); c.txt.alpha_composite(band, (0, 60 + hop))
    fr = v2.compose(c, t, idx)
    fr = fx(fr, T, name, t); fr = strobe(fr, T)
    if g: fr = glitch_frame(fr, T, g)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.0)) / 1.0)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))): p.stdin.write(render_frame(idx, f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((360, 640), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    elif mode == "info":
        from collections import Counter
        print(TOTAL, Counter(k for _, k, _ in EV))
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(2) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
