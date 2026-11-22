"""BeepMelody · Earth hums (objects launched into space, 1957-2025) · co-pilot step 2: three 8 s mood excerpts
on the densest passage of the data: 2016 -> 2025 (10 years, 0.8 s per year here).
Rule kept from step 1: 1 beep = 20 objects launched (UNOOSA via OWID, earth_hums_draft.csv); beeps of a year are
spread evenly over that year's slot, so 2016 = 11 beeps, 2020 = 64, 2025 = 226: notes turn into a continuous hum.
Each excerpt ends with the lone Sputnik-like beep (the 1957 motif) after a short silence.
Usage: python3 earth_hums_moods.py <earth_hums_draft.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
YEAR = 0.8
Y0, Y1 = 2016, 2025
PER = 20
OUT = sys.argv[2]
rows = {int(r["year"]): int(r["value"]) for r in csv.DictReader(open(sys.argv[1]))}
NY = Y1 - Y0 + 1
TEND = NY * YEAR                       # 8.0 s of data
DUR = TEND + 1.6                       # + silence and the lone 1957 beep

EV = []                                # (time, year, index in year, n in year)
for k, y in enumerate(range(Y0, Y1 + 1)):
    n = max(1, round(rows[y] / PER))
    for i in range(n):
        EV.append((k * YEAR + (i + .5) * YEAR / n, y, i, n))

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lowpass(x, fc, o=2):
    b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
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
def ping(f, d=.25, dur=.9):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt) * env(n, .002, d)
def bell(f, d=.6, idx=1.4, ratio=3.5, dur=1.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt + idx*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt)) * env(n, .003, d)
def square(f, dur, duty=.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.where((f * tt) % 1 < duty, 1.0, -1.0)
def pluck(f, dec=.18):
    n = int(.6 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (6 + 3 * h)) for h in range(1, 7))
    return s * env(n, .002, dec)
def sputnik(L, t0, g=.16):
    """Lone 1957 beep: two short ~0.3 s square tones, like the 20 MHz telemetry heard on a receiver."""
    for q, m in enumerate((81, 81)):
        n = int(.3 * SR)
        put(L, t0 + q * .6, g * lowpass(square(mtof(m), .3, .5), 3000) * np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (.01 * SR)))

PENT = [0, 2, 4, 7, 9]                 # major pentatonic: bright, open (space = airy)
def deg(i, n, y, base, span=10):
    """Pitch inside a year: rises across the year's beeps, so each year is a little upward sweep."""
    d = int(i / n * span) + (y - Y0) % 3
    return base + 12 * (d // 5) + PENT[d % 5]

# A · Aérien néon — 72 BPM, wide slow pad, glass pings; the pings pile up into a shimmering cloud
def mood_a():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    pad = np.zeros_like(L)
    for m in [48, 55, 60, 64, 67, 71]:
        for det in (.994, 1.0, 1.006): pad += np.sin(2*np.pi*mtof(m)*det*t)
    L += .008 * pad * np.minimum(1, t / 1.5) * (t < TEND + .3)
    L += .05 * np.sin(2*np.pi*mtof(36)*t) * (t < TEND + .3)
    for k in range(NY):                                     # one soft low pulse per year (72 BPM ≈ 0.83 s)
        put(L, k * YEAR, kick(.10, 60, 38))
    for tm, y, i, n in EV:
        g = .16 / max(1, n / 12) ** .2                     # keep loudness bounded as density explodes
        put(L, tm, g * ping(mtof(deg(i, n, y, 79)), .18 if n < 60 else .08))
    sputnik(L, TEND + .5)
    return reverb(L, .5, 1.3), "A"

# B · Télémétrie rétro — 120 BPM, chiptune bleeps (square, like a ground station receiver), triangle bass;
# the bleeps become a buzzing carrier wave
def mood_b():
    L = np.zeros(int(DUR * SR)); beat = .5
    for k, b in enumerate(np.arange(0, TEND, beat)):
        put(L, b, kick(.16))
        if k % 2: put(L, b, noise(.12, 6000, 30, 40 + k, 900), .05)
        put(L, b + .25, noise(.03, 9000, 140, 70 + k, 5000), .02)
        root = [36, 36, 41, 43][(k // 2) % 4]; n = int(.45 * SR); tt = np.arange(n) / SR
        tri = 2 * np.abs(2 * ((mtof(root) * tt) % 1) - 1) - 1
        put(L, b, .08 * tri * env(n, .005, .3))
    for tm, y, i, n in EV:
        g = .09 / max(1, n / 12) ** .2
        d = .06 if n < 60 else .03
        put(L, tm, g * lowpass(square(mtof(deg(i, n, y, 76)), d, .25), 5000) * env(int(d * SR), .001, d / 2))
    sputnik(L, TEND + .5, .18)
    return reverb(L, .18), "B"

# C · Pulsation orbitale — 110 BPM, deep sub pulse + marimba-like plucks + soft synth bed (close to the altitude-race palette)
def mood_c():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; beat = 60 / 110
    L += .006 * sum(np.sin(2*np.pi*mtof(m)*t + np.sin(2*np.pi*.2*t)) for m in [52, 57, 59, 64]) * (t < TEND + .3)
    for k, b in enumerate(np.arange(0, TEND, beat)):
        put(L, b, kick(.18, 70, 42))
        put(L, b + beat / 2, noise(.05, 8000, 80, 300 + k, 4000), .025)
    for tm, y, i, n in EV:
        g = .15 / max(1, n / 12) ** .2
        put(L, tm, g * pluck(mtof(deg(i, n, y, 72)), .15 if n < 60 else .06))
    for k, y in enumerate(range(Y0, Y1 + 1)):               # a bell on every new year
        put(L, k * YEAR, .07 * bell(mtof(84 + PENT[k % 5]), .5))
    sputnik(L, TEND + .5)
    return reverb(L, .35, 1.1), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.3 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("years", Y0, "->", Y1, ":", len(EV), "beeps (1 beep = %d objects), %.1f s" % (PER, DUR))
