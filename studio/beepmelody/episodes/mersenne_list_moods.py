"""BeepMelody · Mersenne's list · co-pilot step 2: three 8 s mood excerpts on the busiest passage.
Window = the hinge of the video: the last correction of the list (1931, Lehmer: M257 is NOT prime, a wrong note
that resolves), 38 silent years squeezed into a short gap, then the machines (1952 SWAC burst of 5 primes,
1957 BESK, 1961 IBM 7090 x2, 1963 ILLIAC II x3, ... up to 1985 Cray X-MP) = 17 hits.
Every event of mersenne_list_draft.csv in the window = one audible hit at its own instant (date-linear clock).
Pitch = log of the exponent p (bigger prime = higher note).
Usage: python3 mersenne_list_moods.py <outdir>"""
import sys, os, csv, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
DUR = 8.0
OUT = sys.argv[1]

rows = list(csv.DictReader(open(os.path.join(HERE, "mersenne_list_draft.csv"))))

def frac_year(d):
    parts = d.split("-"); y = int(parts[0])
    m = int(parts[1]) if len(parts) > 1 else 6
    dd = int(parts[2]) if len(parts) > 2 else 15
    return y + (m - 1) / 12 + (dd - 1) / 365

# clock: 1931 hit at 0.35 s, gap 1931->1952 squeezed into 1.15 s, then 1952->1986 linear over 6.3 s
EV = []
for r in rows:
    y = frac_year(r["date"])
    if r["kind"] == "fix" and r["year"] == "1931":
        EV.append((0.35, int(r["p"]), "fix"))
    elif r["kind"] == "found" and y < 1986:
        EV.append((1.5 + (y - 1952.0) / (1986 - 1952.0) * 6.3, int(r["p"]), "found"))
EV.sort()

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
def soft(s): return np.tanh(s * 1.4) / 1.4
def put(L, t0, s):
    i = int(t0 * SR); j = min(len(L), i + len(s))
    if i < len(L): L[i:j] += s[:j - i]

def pitch(p, scale, base, span):
    """log(p) -> degree of `scale` from `base` over `span` degrees (p from 61 to 216091 in the window)."""
    u = (math.log(p) - math.log(61)) / (math.log(216091) - math.log(61))
    k = int(round(u * span))
    return base + 12 * (k // len(scale)) + scale[k % len(scale)]

def pluck(f, dur=1.2, bright=.5):
    """Karplus-Strong: harpsichord-ish."""
    n = int(dur * SR); N = max(2, int(SR / f))
    buf = np.random.RandomState(int(f)).uniform(-1, 1, N); y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % N]
        buf[i % N] = bright * buf[i % N] + (1 - bright) * .5 * (buf[i % N] + buf[(i + 1) % N]) * .996 / 1.0
    return y * np.exp(-np.arange(n) / SR * 1.5)
def tone(f, dur, wave="sin", dec=4.0, a=.003, duty=.25):
    n = int(dur * SR); t = np.arange(n) / SR
    if wave == "sin": s = np.sin(2 * np.pi * f * t)
    elif wave == "sq": s = np.where((f * t) % 1 < duty, 1.0, -1.0)
    elif wave == "tri": s = 2 * np.abs(2 * ((f * t) % 1) - 1) - 1
    elif wave == "bell": s = np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)
    return s * np.minimum(1, t / a) * np.exp(-t * dec)
def noise(dur, seed, hp=None, lp=None, dec=20):
    n = int(dur * SR); x = np.random.RandomState(seed).randn(n)
    if hp: x = highpass(x, hp)
    if lp: x = lowpass(x, lp)
    return x * np.exp(-np.arange(n) / SR * dec)
def chalk(seed):
    """a short dry chalk scratch (click)."""
    return .5 * noise(.05, seed, hp=2500, lp=9000, dec=70)

DMIN = [0, 2, 3, 5, 7, 8, 10]       # D natural minor
DPENT = [0, 2, 4, 7, 9]             # D major pentatonic

# A · Quill to machine — baroque harpsichord on a slow organ chord (Dm), the 1931 note is a harpsichord note
# that slips off by a semitone then resolves; at 1952 the harpsichord becomes a square-wave chiptune lead,
# a soft 8th-note pulse comes in (104 BPM): the music changes era like the data does.
def mood_a():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n)
    org = sum(.012 * np.sin(2 * np.pi * mtof(m) * t) * (1 + .3 * np.sin(2 * np.pi * 5 * t)) for m in [38, 50, 53, 57])
    L += org * np.clip(1 - (t - 1.3) / .4, 0, 1)
    pad = sum(.007 * np.where((mtof(m) * t) % 1 < .5, 1, -1) for m in [50, 57, 62])
    L += lowpass(pad, 1400) * np.clip((t - 1.5) / .5, 0, 1)
    beat = 60 / 104
    for b in np.arange(1.5, DUR, beat / 2):
        put(L, b, .05 * tone(mtof(38 if int((b - 1.5) / (beat * 4)) % 2 == 0 else 41), .2, "tri", dec=10))
        if int(round((b - 1.5) / (beat / 2))) % 2: put(L, b, .03 * noise(.04, int(b * 100), hp=6000, dec=80))
    for tm, p, kind in EV:
        m = pitch(p, DMIN, 62, 13)
        if kind == "fix":
            put(L, tm, .35 * pluck(mtof(m + 1), 1.0))          # the wrong note...
            put(L, tm + .45, .35 * pluck(mtof(m), 1.2))        # ...resolves
        else:
            put(L, tm, .14 * tone(mtof(m + 12), .35, "sq", dec=7, duty=.125))
            put(L, tm + beat * .75, .05 * tone(mtof(m + 12), .3, "sq", dec=9, duty=.125))  # echo
    return reverb(soft(L), .3), "A"

# B · Chalk and silence — dark, slow, sparse (68 BPM): low D drone, every hit = a muted low bell + a chalk click;
# the 1931 note is a dissonant bell (tritone) that resolves; the machine era thickens with a soft heartbeat kick.
def mood_b():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n)
    L += .02 * np.sin(2 * np.pi * mtof(26) * t) + .012 * np.sin(2 * np.pi * mtof(33) * t * 1.001)
    L += .01 * lowpass(np.random.RandomState(1).randn(n), 300)
    beat = 60 / 68
    for b in np.arange(1.5, DUR, beat):
        k = int(.35 * SR); tt = np.arange(k) / SR
        put(L, b, .18 * np.sin(2 * np.pi * np.cumsum(55 * np.exp(-tt * 20) + 40) / SR) * np.exp(-tt * 9))
    for i, (tm, p, kind) in enumerate(EV):
        m = pitch(p, DMIN, 50, 13)
        if kind == "fix":
            put(L, tm, .22 * tone(mtof(m + 6), 1.2, "bell", dec=2.2)); put(L, tm, chalk(1))
            put(L, tm + .5, .22 * tone(mtof(m), 1.8, "bell", dec=1.6))
        else:
            put(L, tm, .16 * lowpass(tone(mtof(m), 1.4, "bell", dec=2.5), 2500)); put(L, tm, .8 * chalk(10 + i))
    return reverb(soft(L), .45, 1.3), "B"

# C · The race of the machines — fast and punchy (140 BPM): kick/snare/hat, octave bass, every hit = a bright
# pulse-wave stab + a short rising arpeggio when two primes land close together (1952, 1961, 1963).
def mood_c():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n); beat = 60 / 140
    roots = [38, 34, 36, 33]
    for k, b in enumerate(np.arange(0, DUR, beat / 2)):
        on = b >= 1.5
        bar = int(b / (beat * 4))
        if k % 2 == 0:
            kk = int(.25 * SR); tt = np.arange(kk) / SR
            put(L, b, (.28 if on else .12) * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 25) + 45) / SR) * np.exp(-tt * 14))
            if k % 4 == 2 and on: put(L, b, .12 * noise(.15, k, hp=1200, lp=7000, dec=22))
        put(L, b, (.04 if on else .015) * noise(.03, 100 + k, hp=7000, dec=90))
        if on: put(L, b, .07 * lowpass(tone(mtof(roots[bar % 4] + (12 if k % 2 else 0)), beat / 2, "sq", dec=6, duty=.5), 900))
    prev = -9
    for tm, p, kind in EV:
        m = pitch(p, DPENT, 62, 11)
        if kind == "fix":
            put(L, tm, .2 * tone(mtof(m + 1), .3, "sq", dec=8)); put(L, tm + .25, .2 * tone(mtof(m), .5, "sq", dec=5))
        else:
            put(L, tm, .17 * tone(mtof(m + 12), .28, "sq", dec=9, duty=.25))
            if tm - prev < .25:
                for j, iv in enumerate([0, 7, 12, 19]): put(L, tm + .05 + j * .05, .07 * tone(mtof(m + 12 + iv), .12, "sq", dec=20, duty=.125))
        prev = tm
    return reverb(soft(L), .15), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.4 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("hits in window:", len(EV), [(round(a, 2), p) for a, p, _ in EV])
