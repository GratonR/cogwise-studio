"""BeepMelody · Chocs de pi · co-pilot step 2: three 8 s mood excerpts on the densest passage.
Window = level 4 (mass ratio 1:1,000,000 -> 3,141 clacks) then level 5 (1:100,000,000 -> 31,415 clacks).
Every clack of the exact simulation (pi_clacks_sim.sim) = one audible hit, at its own instant.
Clock: the clacks of a level all happen near t = 2 (physics units), so each level is played in slow motion
around that moment: tau = asinh((t - 2) / w), w = 1/sqrt(ratio) (same warp for every clack of the level,
order and spacing preserved; the screen will say "slow motion").
Usage: python3 pi_clacks_moods.py <outdir>"""
import sys, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "pi_clacks_sim.py")).read().split("for n in range")[0]
exec(src)                                    # defines sim(ratio)

SR = 44100
OUT = sys.argv[1]
LEVELS = [(4, 0.15, 3.25), (5, 3.55, 7.55)]  # (level, start s, end s)
DUR = 8.0

def events():
    ev = []
    for lv, a, b in LEVELS:
        r = 100 ** (lv - 1); w = 1 / math.sqrt(r)
        e = sim(r)
        tau = np.array([math.asinh((t - 2.0) / w) for t, _ in e])
        tau = (tau - tau[0]) / (tau[-1] - tau[0])
        for (t, k), u in zip(e, tau): ev.append((a + u * (b - a), k, lv))
    return ev
EV = events()

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lowpass(x, fc, o=2):
    b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def highpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def reverb(x, mix=.35, size=1.0):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
        n = int(d * size * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)
def train(sel):
    """impulse train: one sample = one clack (several clacks on one sample add up)."""
    x = np.zeros(int(DUR * SR))
    for tm, k, lv in EV:
        if sel(k, lv): x[min(len(x) - 1, int(tm * SR))] += 1.0
    return x
def grain(f, dec, dur=.12, harm=(1,), a=.0005):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * h * tt) / (i + 1) for i, h in enumerate(harm))
    return s * np.minimum(1, tt / a) * np.exp(-tt / dec)
def density_gain(x, win=.03):
    """keep the fused tone from exploding: gain ~ 1/sqrt(local rate), the hit is still there."""
    k = int(win * SR); r = np.convolve(x, np.ones(k), "same")
    return x / np.sqrt(np.maximum(1, r))
def soft(sig): return np.tanh(sig * 1.5) / 1.5

# A · Billard de verre — no beat, the physics is the rhythm. Block hit = glass tick (high), wall hit = wood tick (lower).
# Sparse airy pad in D. When clacks fuse, the two ticks become a bright hum.
def mood_a():
    t = np.arange(int(DUR * SR)) / SR
    L = np.zeros_like(t)
    for m in [50, 57, 62, 66, 69]:
        for d in (.995, 1.005): L += .006 * np.sin(2 * np.pi * mtof(m) * d * t)
    L *= np.minimum(1, t / 1.5)
    tb = density_gain(train(lambda k, lv: k == "b")); tw = density_gain(train(lambda k, lv: k == "w"))
    L += .22 * fftconvolve(tb, grain(mtof(93), .012, harm=(1, 2.76)), "full")[:len(t)]
    L += .22 * fftconvolve(tw, grain(mtof(81), .018, harm=(1, 3.9)), "full")[:len(t)]
    return reverb(soft(L), .45, 1.2), "A"

# B · Compteur mécanique — 120 BPM, kick/hat bed, every clack = a dry metal click (counter wheel);
# a new level = big hit + crash; the bed drops a beat as the clicks fuse.
def mood_b():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n); beat = .5
    def kick(g):
        m = int(.3 * SR); tt = np.arange(m) / SR
        return g * np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 18) + 45) / SR) * np.exp(-tt * 13)
    def put(t0, s):
        i = int(t0 * SR); j = min(n, i + len(s)); L[i:j] += s[:j - i]
    rs = np.random.RandomState(3)
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(b, kick(.30))
        put(b + beat / 2, .05 * highpass(rs.randn(int(.04 * SR)), 6000) * np.exp(-np.arange(int(.04 * SR)) / SR * 90))
        if k % 2: put(b, .06 * lowpass(rs.randn(int(.15 * SR)), 5000) * np.exp(-np.arange(int(.15 * SR)) / SR * 25))
        root = [38, 38, 41, 36][(k // 4) % 4]
        m = int(.22 * SR); put(b + beat / 2, .08 * np.sign(np.sin(2 * np.pi * mtof(root) * np.arange(m) / SR)) * np.exp(-np.arange(m) / SR * 12))
    for lv, a, _ in LEVELS:
        put(a, kick(.5)); put(a, .04 * highpass(rs.randn(int(.8 * SR)), 4000) * np.exp(-np.arange(int(.8 * SR)) / SR * 6))
    clk = density_gain(train(lambda k, lv: True))
    L += .25 * fftconvolve(clk, grain(3200, .004, dur=.03, harm=(1, 1.7, 2.9)), "full")[:n]
    return reverb(soft(L), .15), "B"

# C · Accord de pi — soft and bright like THE RACE TO THE SKY: marimba + bell + soft synth pad.
# Clack number i plays the i-th digit of pi on a D major pentatonic scale (digit 0..9 -> 10 notes):
# slow = a melody of pi, fused = a shimmering chord of all its digits.
PI = "31415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
def mood_c():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n)
    for m in [50, 54, 57, 62]:
        L += .007 * np.sin(2 * np.pi * mtof(m) * t) * (.8 + .2 * np.sin(2 * np.pi * t / 4))
    PENT = [0, 2, 4, 7, 9]
    notes = [62 + 12 * (d // 5) + PENT[d % 5] for d in range(10)]
    # digit stream: restart at "3" at the start of each level, so the count spells pi each time
    trains = [np.zeros(n) for _ in range(10)]
    cnt = {}
    for tm, k, lv in EV:
        i = cnt.get(lv, 0); cnt[lv] = i + 1
        d = int(PI[i % len(PI)])
        trains[d][min(n - 1, int(tm * SR))] += 1
    tot = sum(trains); k = int(.03 * SR); rate = np.convolve(tot, np.ones(k), "same")
    g = 1 / np.sqrt(np.maximum(1, rate))
    for d in range(10):
        f = mtof(notes[d])
        mar = grain(f, .09, dur=.5, harm=(1, 3.93, 9.2), a=.001)     # marimba-ish
        L += .16 * fftconvolve(trains[d] * g, mar, "full")[:n]
    return reverb(soft(L), .4, 1.1), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.4 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
from collections import Counter
print("clacks per level in window:", dict(Counter(lv for _, _, lv in EV)))
