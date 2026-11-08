"""Event-driven chiptune: every visual event in pi.EV makes a sound; backing beat follows an accelerating tempo map."""
import sys, os, wave, math
import numpy as np
from scipy.signal import lfilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
P = importlib.import_module(os.environ.get('MOD', 'pi'))
FINAL = getattr(P, 'FINAL', 'eniac')

SR = 44100
N = int((P.TOTAL + 1.0) * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def mf(m): return 440 * 2 ** ((m - 69) / 12)
def put(sig, t, gl=1.0, gr=1.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]; L[i:i + len(sig)] += sig * gl; R[i:i + len(sig)] += sig * gr
def lp(x, a): return lfilter([a], [1, a - 1], x)
def hp(x, a): return x - lp(x, a)
def T(d): return np.arange(int(d * SR)) / SR
def pulse(f, d, duty=0.25):
    t = T(d); return np.where((t * f) % 1 < duty, 1.0, -1.0), t
def tri(f, d):
    t = T(d); return 2 * np.abs(2 * ((t * f) % 1) - 1) - 1, t
def adsr(t, a=0.003, dec=0.06, s=0.4, d=None, r=0.02):
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / dec))
    if d is not None: e *= np.clip((d - t) / r, 0, 1)
    return e

def scene_at(t):
    for sc_ in P.SC:
        n, d = sc_[0], sc_[1]
        if P.START[n] <= t < P.START[n] + d: return n
    return "outro"

SCALE = getattr(P, "SCALE", [69, 71, 72, 74, 76, 77, 79, 81, 83, 84])   # digit -> note
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]

# ---------------- event sounds ----------------
def s_digit(t, d, ok, dur=0.16, vol=0.17, duty=0.25):
    f = mf(SCALE[d])
    w, tt = pulse(f, dur, duty)
    sig = lp(w * adsr(tt, dec=0.05, s=0.45, d=dur), 0.45) * vol
    if not ok:  # wrong digit: detuned, buzzy, with noise
        w2, _ = pulse(f * 2 ** (-0.6 / 12) * 1.06, dur, 0.5)
        sig = lp((w * 0.6 + w2 * 0.6) * adsr(tt, dec=0.08, s=0.5, d=dur), 0.35) * vol + rng.standard_normal(len(tt)) * 0.03 * np.exp(-tt * 30)
    put(sig, t, 0.9, 0.75); put(sig * 0.25, t + 0.12, 0.4, 0.9)

def s_wedge(t, i):
    tt = T(0.09); f = 150 - 40 * tt / 0.09 + (i % 4) * 12
    body = np.sin(2 * np.pi * np.cumsum(np.full(len(tt), 1.0) * f) / SR) * np.exp(-tt * 45)
    click = lp(rng.standard_normal(len(tt)), 0.5) * np.exp(-tt * 200)
    put((body * 0.5 + click * 0.25), t)
    # tuned blip so the wedges form a little riff
    w, t2 = pulse(mf([57, 60, 64, 67, 69][i % 5] + 12), 0.06, 0.125)
    put(lp(w * adsr(t2, dec=0.02, s=0.1, d=0.06), 0.3) * 0.06, t, 0.6, 1.0)

def s_scrape(t, i):
    n = rng.standard_normal(int(0.12 * SR)); tt = T(0.12)
    put(hp(lp(n, 0.3), 0.05) * np.sin(np.pi * tt / 0.12) * 0.12, t, 1.0, 0.7)

def s_vert(t, lvl, k, n):
    deg = [0, 2, 4, 7, 9][k % 5] + 12 * (k // 5 % 2)
    m = 57 + 12 * min(lvl, 2) // 2 + deg + lvl * 2
    dur = max(0.018, min(0.09, 1.05 / n * 0.9))
    w, tt = tri(mf(m + 12), dur)
    put(w * adsr(tt, dec=0.03, s=0.3, d=dur, r=0.005) * 0.14, t, 0.8 if k % 2 else 1.0, 1.0 if k % 2 else 0.8)
    if n <= 12:
        c = rng.standard_normal(int(0.02 * SR)); put(hp(c, 0.4) * np.exp(-T(0.02) * 200) * 0.08, t)

def s_chime(t, lvl):
    tt = T(0.6)
    for m, g in ((81 + lvl, 0.1), (88 + lvl, 0.06), (93 + lvl, 0.03)):
        put(np.sin(2 * np.pi * mf(m) * tt) * np.exp(-tt * 6) * g, t)

def s_needle(t, cross, rate=10):
    g = min(1.0, (12 / rate) ** 0.5); tt = T(0.03)
    put((hp(rng.standard_normal(len(tt)), 0.6) * np.exp(-tt * 260) * 0.16 + np.sin(2 * np.pi * 2900 * tt) * np.exp(-tt * 180) * 0.05) * g, t, 0.7 + rng.random() * 0.3, 0.7 + rng.random() * 0.3)
    if cross:
        tt = T(0.09); f = mf(81 + int(rng.integers(0, 3)) * 3)
        put((np.sin(2 * np.pi * f * tt) * np.exp(-tt * 40) * 0.09 + np.sin(2 * np.pi * f * 2.01 * tt) * np.exp(-tt * 60) * 0.03) * g, t)

def s_term(t, k, rate=10):
    up = k % 2 == 0
    m = (76 if up else 72) + 12 * (k // 24 % 2)
    dur = max(0.02, min(0.07, 0.8 / rate))
    w, tt = pulse(mf(m), dur, 0.25 if up else 0.5)
    put(lp(w * adsr(tt, dec=0.025, s=0.3, d=dur, r=0.005), 0.4) * 0.12 * min(1, (20 / rate) ** 0.4), t, 1.0 if up else 0.7, 0.7 if up else 1.0)

def s_clack(t, wall, d):
    tt = T(0.025)
    f = (1350 if wall else 1900) + rng.uniform(-60, 60)
    s = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 260) * 0.35 + hp(rng.standard_normal(len(tt)), 0.5) * np.exp(-tt * 500) * 0.25
    put(s * [1.0, 1.0, 0.45, 0.22][d], t, 1.0 if wall else 0.8, 0.8 if wall else 1.0)

def s_edigit(t, d, rate):
    dur = max(0.022, min(0.12, 0.85 / rate))
    w, tt = pulse(mf(SCALE[d] + (12 if rate > 40 else 0)), dur, 0.125)
    put(w * adsr(tt, dec=0.02, s=0.4, d=dur, r=0.004) * 0.11, t, 0.85, 0.85)

def s_pen(t, lvl, j):
    tt = T(0.05); n = hp(rng.standard_normal(len(tt)), 0.3) * np.exp(-tt * 70) * 0.06
    m = [64, 67, 69, 72, 76, 79, 81, 84, 88][min(8, lvl)] + [0, 2, 4, 7, 9][j % 5] - 12
    w, t2 = tri(mf(m), 0.12)
    put(n, t); put(w * adsr(t2, dec=0.04, s=0.25, d=0.12) * 0.13, t, 0.8 + 0.2 * (j % 2), 1.0 - 0.2 * (j % 2))
def s_thud(t, v):
    tt = T(0.16); f = 70 + 90 * np.exp(-tt * 40)
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 22) * v + lp(rng.standard_normal(len(tt)), 0.3) * np.exp(-tt * 60) * v * 0.4, t)
def s_pop(t, m):
    tt = T(0.07); f = mf(72 + [0, 4, 7, 12, 16][m % 5]) * (1 + 0.6 * np.exp(-tt * 60))
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * adsr(tt, dec=0.03, s=0.2, d=0.07) * 0.12, t, 0.7 + 0.3 * rng.random(), 0.7 + 0.3 * rng.random())
def s_chalk(t):
    n = rng.standard_normal(int(0.2 * SR)); tt = T(0.2)
    put(hp(n * (np.sin(2 * np.pi * 30 * tt) > 0), 0.3) * np.sin(np.pi * tt / 0.2) * 0.08, t)
def s_key(t, key, rate):
    tt = T(0.012); put(hp(rng.standard_normal(len(tt)), 0.5) * np.exp(-tt * 400) * 0.12, t)
    m = {"1": 81, "+": 84, "√X": 88}[key]; dur = max(0.025, min(0.09, 0.8 / rate))
    w, t2 = pulse(mf(m), dur, 0.5)
    put(lp(w * adsr(t2, dec=0.02, s=0.4, d=dur, r=0.005), 0.3) * 0.07 * min(1, (12 / rate) ** 0.3), t)
def s_tri(t, col):
    m = (79 if col else 72) + int(rng.integers(0, 3)) * (4 if col else 3)
    w, tt = tri(mf(m), 0.035); put(w * np.exp(-tt * 90) * 0.07, t, 0.6 + 0.4 * col, 1.0 - 0.4 * col)
def s_seed(t, k, good):
    deg = [0, 2, 4, 7, 9, 12, 14, 16][k % 8] if good else [0, 1, 6, 7, 10, 11, 13, 18][k % 8]
    w, tt = pulse(mf(69 + deg), 0.04, 0.25)
    sig = lp(w * np.exp(-tt * 70), 0.35) * 0.07
    if not good: sig += rng.standard_normal(len(tt)) * np.exp(-tt * 120) * 0.02
    put(sig, t, 0.6 + 0.4 * (k % 2), 1.0 - 0.4 * (k % 2))

def s_coin(t, a, rate):
    tt = T(0.09); m = 79 + int((a - 1) * 9)
    f = mf(SCALE[min(9, int((a - 1) * 6))] + 12)
    g = min(1, (10 / rate) ** 0.35)
    put((np.sin(2 * np.pi * f * tt) * 0.6 + np.sin(2 * np.pi * f * 2.76 * tt) * 0.25) * np.exp(-tt * 45) * 0.1 * g, t, 0.8, 1.0)
def s_hat(t, der, i, rate):
    g = min(1, (8 / rate) ** 0.35)
    tt = T(0.02); put(lp(rng.standard_normal(len(tt)), 0.4) * np.exp(-tt * 200) * 0.08 * g, t)
    if der:
        w, t2 = tri(mf(SCALE[[0, 2, 4, 5, 7, 9][i % 6]]), 0.12); put(w * adsr(t2, dec=0.05, s=0.3, d=0.12) * 0.14 * g, t)
    else:
        w, t2 = tri(mf(57), 0.05); put(w * np.exp(-t2 * 60) * 0.06 * g, t)
def s_block(t, n):
    m = SCALE[min(9, n % 10)] + (12 if n >= 10 else 0) - 12
    w, tt = pulse(mf(m), 0.18, 0.25); w2, _ = tri(mf(m - 12), 0.18)
    put(lp(w * 0.6 + w2 * 0.6, 0.3) * adsr(tt, dec=0.07, s=0.35, d=0.18) * 0.15, t)
    s_thud(t, 0.18)
def s_geiger(t):
    tt = T(0.006); put(hp(rng.standard_normal(len(tt)), 0.6) * 0.22, t, 0.6 + 0.4 * rng.random(), 0.6 + 0.4 * rng.random())
def s_stick(t, L):
    m = SCALE[min(9, int(L * 10))]
    w, tt = tri(mf(m), 0.09); put(w * adsr(tt, dec=0.04, s=0.3, d=0.09) * 0.12, t, 0.6 + 0.4 * L, 1.0 - 0.4 * L)
    c = T(0.01); put(hp(rng.standard_normal(len(c)), 0.4) * np.exp(-c * 300) * 0.05, t)

PENTA = [0, 3, 5, 7, 10]
def s_bip(t, r, rate, lon, pl=None):
    g = min(1.0, (6 / max(rate, 1)) ** 0.42)
    if getattr(P, "RISE", False) and pl is not None:
        # pitch = the population curve: log10(pop) 5..10 spans ~3.5 octaves of A minor pentatonic, region adds a chord colour
        k = int((pl - 5.0) / 5.0 * 17) + [0, 2, 1, 3, 4, 2, 1, 3][r % 8]
        f = mf(45 + 12 * (k // 5) + PENTA[k % 5])
    else:
        f = mf(SCALE[r % len(SCALE)] + 12)
    tt = T(0.05); w = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)
    pan = 0.5 + 0.4 * math.sin(math.radians(lon))
    put(w * np.exp(-tt * 70) * np.minimum(1, tt * 400) * 0.16 * g, t, 1.2 - pan, 0.2 + pan)
def s_bomb(t, rate):
    g = min(1.0, (5 / max(rate, 1)) ** 0.3)
    tt = T(0.6); f = 38 + 60 * np.exp(-tt * 12)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6)
    n = lp(rng.standard_normal(len(tt)), 0.08) * np.exp(-tt * 9)
    put((body * 0.5 + n * 0.5) * 0.26 * g, t, 0.8 + 0.3 * rng.random(), 0.8 + 0.3 * rng.random())
def s_crisis(t):
    tt = T(3.0)
    for m, gg in ((33, 0.2), (40, 0.1), (45, 0.06), (46, 0.05)):
        put(np.sin(2 * np.pi * mf(m) * tt) * np.exp(-tt * 1.2) * gg, t)
    s_noise(t, 0.3, 0.06, crush=True)

def s_noise(t, d, vol, rise=False, crush=False):
    n = rng.standard_normal(int(d * SR)); tt = T(d)
    if crush: n = np.repeat(n[::8], 8)[:len(tt)]
    env = (tt / d) ** 2 if rise else np.exp(-tt * 3)
    put(hp(n, 0.1) * env * vol, t)

for t, kind, kw in P.EV:
    if kind == "digit": s_digit(t, kw["d"], kw["ok"])
    elif kind == "wedge": s_wedge(t, kw["i"])
    elif kind == "scrape": s_scrape(t, kw["i"])
    elif kind == "vert": s_vert(t, kw["lvl"], kw["k"], kw["n"])
    elif kind == "chime": s_chime(t, kw["lvl"])
    elif kind == "needle": s_needle(t, kw["cross"], kw.get("rate", 10))
    elif kind == "term": s_term(t, kw["k"], kw.get("rate", 10))
    elif kind == "clack": s_clack(t, kw["wall"], kw["d"])
    elif kind == "edigit": s_edigit(t, kw["d"], kw["rate"])
    elif kind == "pen": s_pen(t, kw["lvl"], kw["j"])
    elif kind == "thud": s_thud(t, kw["v"])
    elif kind == "pop": s_pop(t, kw["m"])
    elif kind == "chalk": s_chalk(t)
    elif kind == "key": s_key(t, kw["key"], kw["rate"])
    elif kind == "tri": s_tri(t, kw["col"])
    elif kind == "seed": s_seed(t, kw["k"], kw["good"])
    elif kind == "coin": s_coin(t, kw["a"], kw["rate"])
    elif kind == "hat_trial": s_hat(t, kw["der"], kw["i"], kw["rate"])
    elif kind == "block": s_block(t, kw["n"])
    elif kind == "geiger": s_geiger(t)
    elif kind == "stick": s_stick(t, kw["L"])
    elif kind == "bip": s_bip(t, kw["r"], kw["rate"], kw["lon"], kw.get("pl"))
    elif kind == "bomb": s_bomb(t, kw["rate"])
    elif kind == "crisis": s_crisis(t)
    elif kind == "riser": s_noise(t, 0.5, 0.12, rise=True)
    elif kind == "whoosh": s_noise(t, 0.4, 0.08)
    elif kind == "error": s_noise(t, 0.12, 0.05, crush=True)
    elif kind == "glitch": s_noise(t, 0.8, 0.22, rise=True, crush=True)
# hard cut crackles
for sc_ in P.SC[1:]: s_noise(P.START[sc_[0]], 0.06, 0.07, crush=True)

# ---------------- backing on accelerating tempo ----------------
def kick(t, v=0.5):
    tt = T(0.2); f = 45 + 120 * np.exp(-tt * 32)
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 16) * v, t)
def snare(t, v=0.22):
    tt = T(0.15); n = lp(rng.standard_normal(len(tt)), 0.6)
    put((n * 0.7 + np.sin(2 * np.pi * 200 * tt) * 0.4) * np.exp(-tt * 26) * v, t)
def hat(t, v=0.05, open_=False):
    d = 0.09 if open_ else 0.03; tt = T(d)
    put(hp(rng.standard_normal(len(tt)), 0.7) * np.exp(-tt * (40 if open_ else 140)) * v, t, 0.7, 1.0)
def bass(t, m, d, v=0.2):
    w, tt = tri(mf(m), d); w2, _ = pulse(mf(m), d, 0.5)
    put((w * 0.8 + lp(w2, 0.1) * 0.3) * adsr(tt, dec=0.08, s=0.7, d=d, r=0.01) * v, t)

KQ = []
for t, kind, kw in P.EV:
    if kind == "kick": (KQ.append((t, kw["v"])) if getattr(P, "DUCK", False) else kick(t, kw["v"]))
    elif kind == "kickhit": (KQ.append((t, 0.6)) if getattr(P, "DUCK", False) else kick(t, 0.6))
    elif kind == "snare": snare(t, kw["v"])
    elif kind == "hat": hat(t, kw["v"], kw["open"])
    elif kind == "bass": bass(t, kw["m"], kw["d"], kw["v"])
    elif kind == "pad":
        for m in kw["ch"]:
            if getattr(P, "RICH", False):
                tt = T(kw["d"]); w = 0
                for det in (-0.12, 0.0, 0.11):
                    w = w + (2 * ((tt * mf(m + 12 + det)) % 1) - 1)
                w = lp(w / 3, 0.06)
                env = np.minimum(1, tt * 1.5) * np.clip((kw["d"] - tt) * 2, 0, 1)
                put(w * env * 0.07, t, 0.7 + 0.3 * (m % 2), 1.0 - 0.3 * (m % 2))
            else:
                w, tt = tri(mf(m + 12), kw["d"])
                put(w * np.minimum(1, tt * 3) * np.clip((kw["d"] - tt) * 3, 0, 1) * 0.035, t)
# finale riser into the glitch
E = P.START[FINAL]
RT = getattr(P, "RISER_T", None) or (E + 3.4)
n = rng.standard_normal(int(1.6 * SR)); tt = T(1.6)
put(hp(n, 0.15) * (tt / 1.6) ** 3 * 0.18, RT)
w, tt = pulse(1.0, 1.6, 0.5); f = mf(45) * 2 ** (tt / 1.6 * 2)
put(lp(np.where((np.cumsum(f) / SR) % 1 < 0.5, 1.0, -1.0), 0.1) * (tt / 1.6) * 0.12, RT)

# outro: big final chord + last digits slowing down
st = P.START["outro"]
kick(st, 0.6)
for m in (45, 57, 60, 64, 69):
    w, tt = pulse(mf(m), 3.4, 0.5 if m < 50 else 0.25)
    put(lp(w, 0.08 if m < 50 else 0.15) * np.exp(-tt * 0.9) * (0.12 if m < 50 else 0.05), st)
for k, dgt in enumerate((getattr(P, "OUTRO_DIGITS", None) if hasattr(P, "OUTRO_DIGITS") else (getattr(P, "ED", None) or getattr(P, "PHD", None) or P.PID))[:5]):
    s_digit(st + 0.15 + k * (0.18 + k * 0.06), dgt, True, dur=0.3, vol=0.14)

def apply_glitches(X):
    for t0, dur, kind, sl in P.GL:
        i0, n = int(t0 * SR), int(dur * SR)
        if kind == "stutter":
            ln = max(64, int(sl * SR)); seg = X[i0:i0 + ln].copy()
            env = np.ones(ln); f = min(64, ln // 4); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
            out = np.zeros(n)
            for k in range(0, n, ln):
                piece = seg * env * (1 - 0.15 * (k // ln) / max(1, n // ln))
                if k // ln % 3 == 2: piece = piece[::-1]
                out[k:k + ln] = piece[: n - k]
            X[i0:i0 + n] = out
        elif kind == "crush":
            seg = X[i0:i0 + n].copy(); hold = 14
            seg = np.repeat(seg[::hold], hold)[:n]; seg = np.round(seg * 6) / 6
            X[i0:i0 + n] = seg * 0.9
        elif kind == "tapestop":
            p = np.arange(n) / n; src = i0 + (n * (p - p * p / 2)).astype(int)
            X[i0:i0 + n] = X[src] * (1 - p ** 2)
    return X
if KQ:   # sidechain: everything ducks under each kick, then the kicks go in on top
    env = np.ones(N); dl = int(0.35 * SR); shape = 1 - 0.5 * np.exp(-np.arange(dl) / SR / 0.11)
    for tk, v in KQ:
        i = int(tk * SR)
        if i < N: seg = shape[: N - i]; env[i:i + len(seg)] = np.minimum(env[i:i + len(seg)], 1 - (1 - seg) * min(1, v / 0.45))
    L *= env; R *= env
    for tk, v in KQ: kick(tk, v)
if getattr(P, "REVERB", False):
    from scipy.signal import fftconvolve
    tt = T(1.4)
    for ch_, sd in ((L, 1), (R, 2)):
        ir = lp(np.random.default_rng(sd).standard_normal(len(tt)), 0.35) * np.exp(-tt / 0.38)
        ir /= np.sqrt((ir ** 2).sum())
        wet = fftconvolve(ch_, ir)[:N]
        ch_ += wet * 0.22
for ch_ in (L, R): apply_glitches(ch_)
# silence gap ("drop") right before the outro hit
g0, g1 = int((P.START["outro"] - 0.12) * SR), int(P.START["outro"] * SR)
L[g0:g1] *= 0.05; R[g0:g1] *= 0.05

end = int(P.TOTAL * SR)
st_ = np.stack([L, R], 1)[:end]
ref = np.percentile(np.abs(st_), 99.7)
st_ = np.tanh(st_ / ref * 0.9) / np.tanh(0.9 * np.abs(st_).max() / ref) * 0.92  # soft limiter
fade = int(0.8 * SR); st_[-fade:] *= np.linspace(1, 0, fade)[:, None]
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st_ * 32767).astype(np.int16).tobytes())
print("ok", P.TOTAL)
