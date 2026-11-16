"""BeepMelody · Jupiter's moons · co-pilot step 2: three 8 s mood excerpts on the densest passage
(all four Galilean moons playing, clock 1 s = 2 days, window = 16 days that holds a Callisto lap).
One completed orbit = one hit, placed EXACTLY on the orbit (no grid snapping): the backing tempo is locked
to Io's period (0.8846 s per lap -> 67.8 BPM), so Io sits on the beat and Europa / Ganymede slide a little
(1 : 2.007 : 4.044) — the slip is the real data.
Usage: python3 jupiter_moons_moods.py <jupiter_moons_draft.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
DAYS_PER_S = 2.0
OUT = sys.argv[2]
ROWS = {r["moon"]: float(r["sidereal_period_d"]) for r in csv.DictReader(open(sys.argv[1]))}
P = {m: ROWS[m] / DAYS_PER_S for m in ("Io", "Europa", "Ganymede", "Callisto")}   # seconds per lap on screen
IO_BPM = 60 / P["Io"]
# illustrative phases for the demo (real phases from JPL Horizons at render time): fraction of the lap done at t=0
PHASE = {"Io": 0.0, "Europa": 0.15, "Ganymede": 0.55, "Callisto": 0.40}

def hits(m):
    t0 = (1 - PHASE[m]) * P[m] % P[m]
    return [t for t in np.arange(t0, DUR - .3, P[m])]

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lowpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def highpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += g * sig[:j - i]
def reverb(x, mix=.35, size=1.0):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
        n = int(d * size * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)
def noise(dur, fc, dec, seed, hp=None):
    n = int(dur * SR); s = lowpass(np.random.RandomState(seed).randn(n), fc)
    if hp: s = highpass(s, hp)
    return s * np.exp(-np.arange(n) / SR * dec)
def kick(g=.26, f0=80, f1=46):
    n = int(.35 * SR); tt = np.arange(n) / SR
    return g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+f1)/SR) * np.exp(-tt*12)
def bell(f, d=1.2, idx=1.6, ratio=3.5, dur=2.8):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt + idx*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt)) * env(n, .003, d)
def marimba(f):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25) + .1*np.sin(2*np.pi*f*10*tt)*np.exp(-tt*60)) * env(n, .001, .32)
def softsyn(f, d=.9):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*tt) for h in range(1, 6))
    return lowpass(s, 1200) * env(n, .02, d)
def gong(f, d=2.5):
    n = int(4.5 * SR); tt = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*r*tt) * np.exp(-tt * k) for a, r, k in [(1, 1, .5), (.6, 1.48, .9), (.45, 2.13, 1.3), (.3, 2.71, 1.8), (.2, 3.9, 2.6)])
    return s * env(n, .01, d)
def pluck(f, dec=.35):
    n = int(.9 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
    return s * env(n, .002, dec)
def tom(f0, g, d=.45):
    n = int(.9 * SR); tt = np.arange(n) / SR
    return g * np.sin(2*np.pi*np.cumsum(f0*(1+.6*np.exp(-tt*20)))/SR) * np.exp(-tt / d)

# A · Orbite aérienne — 67.8 BPM (1 beat = 1 Io lap), wide Emaj9 pad, glass bell / marimba / soft synth / gong (pilot family)
def mood_a():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    n = len(L); s = np.zeros(n)
    for m in [40, 47, 52, 56, 59, 63, 66]:
        for det in (.994, 1.0, 1.006): s += np.sin(2*np.pi*mtof(m)*det*t)
    L += .010 * s * np.minimum(1, t / 1.5)
    L += .07 * np.sin(2*np.pi*mtof(28)*t) * (.6 + .4*np.sin(2*np.pi*t/P["Callisto"]))
    for tm in hits("Io"): put(L, tm, .16 * bell(mtof(76), .7))                 # E5 glass bell
    for tm in hits("Europa"): put(L, tm, .20 * marimba(mtof(71)))             # B4 marimba
    for tm in hits("Ganymede"): put(L, tm, .20 * softsyn(mtof(52)))           # E3 soft synth
    for tm in hits("Callisto"): put(L, tm, .22 * gong(mtof(40)))              # E2 gong
    return reverb(L, .5, 1.3), "A"

# B · Groove orbital — 135.7 BPM (2 beats = 1 Io lap), kick + 16th hats + sub; moons = pluck / clap-stab / bass drop / crash
def mood_b():
    L = np.zeros(int(DUR * SR)); beat = P["Io"] / 2; s16 = beat / 4
    roots = [33, 33, 29, 31]                                                   # A - A - F - G, one bar = 2 Io laps
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.24))
        for q in range(4): put(L, b + q * s16, noise(.04, 9000, 120, 70 + 4*k + q, 5000), .028 if q % 2 else .016)
        r = roots[(k // 4) % 4]
        for q in (1, 3):
            nn = int(s16 * .9 * SR); tt = np.arange(nn) / SR; f = mtof(r + 12)
            put(L, b + q * s16, .06 * lowpass(2 * ((f * tt) % 1) - 1, 700) * np.exp(-tt * 10))
    for tm in hits("Io"): put(L, tm, .17 * pluck(mtof(69)))                   # A4 pluck on the beat
    for tm in hits("Europa"):                                                 # clap + minor chord stab
        put(L, tm, noise(.18, 6000, 22, int(tm * 100), 900), .11)
        for m in (57, 60, 64): put(L, tm, .06 * pluck(mtof(m), .25))
    for tm in hits("Ganymede"):                                               # bass drop
        nn = int(.8 * SR); tt = np.arange(nn) / SR
        put(L, tm, .22 * lowpass(np.sin(2*np.pi*np.cumsum(mtof(33)*(1+.5*np.exp(-tt*8)))/SR), 400) * np.exp(-tt * 3))
    for tm in hits("Callisto"): put(L, tm, noise(2.0, 11000, 1.6, 999, 3000), .10)   # crash
    return reverb(L, .18), "B"

# C · Tambours de Jupiter — 101.7 BPM (3 beats = 1 Io lap, the moons play against a triple pulse),
# low D drone, woodblock / conga / taiko / gong
def mood_c():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; beat = P["Io"] / 3
    L += .05 * (np.sin(2*np.pi*mtof(26)*t) + .5*np.sin(2*np.pi*mtof(33)*t)) * (.7 + .3*np.sin(2*np.pi*t/4))
    L += lowpass(np.random.RandomState(5).randn(len(L)), 300) * .02
    for k, b in enumerate(np.arange(0, DUR, beat)):                          # shaker pulse
        put(L, b, noise(.07, 8000, 60, 300 + k, 3000), .035 if k % 3 == 0 else .02)
    def wood(f):
        nn = int(.25 * SR); tt = np.arange(nn) / SR
        return np.sin(2*np.pi*f*tt) * np.exp(-tt * 40)
    for tm in hits("Io"): put(L, tm, .20 * wood(mtof(81)))                   # woodblock
    for tm in hits("Europa"): put(L, tm, tom(mtof(57), .26, .18))            # conga
    for tm in hits("Ganymede"): put(L, tm, tom(mtof(38), .40, .5));
    for tm in hits("Ganymede"): put(L, tm, noise(.3, 900, 9, 77), .08)       # taiko skin
    for tm in hits("Callisto"): put(L, tm, .24 * gong(mtof(38), 3.0))        # D2 gong
    return reverb(L, .3, 1.2), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.6 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("Io tempo %.2f BPM" % IO_BPM)
for m in P: print(m, "lap %.3f s" % P[m], "hits:", [round(x, 2) for x in hits(m)])
