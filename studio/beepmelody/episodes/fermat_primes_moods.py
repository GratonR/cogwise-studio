"""BeepMelody · Fermat numbers · co-pilot step 2: three 8 s mood excerpts on the key passage (F2 -> F8).
Order = index F0 -> F33 (decision 1/4, option A). One Fermat number = one hit.
Right notes (F0-F4, primes) climb the major chord; from F5 on, every note keeps climbing but lands
OUT of the chord (a wrong note), with its own "crack" sound: the listener hears the 6th note break.
Usage: python3 fermat_primes_moods.py <fermat_primes_draft.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
OUT = sys.argv[2]
rows = list(csv.DictReader(open(sys.argv[1])))
STEP = 1.1                       # s between two Fermat numbers in the excerpt
FIRST, LAST = 2, 8               # F2 .. F8 -> break (F5) lands at ~3.5 s
EV = [(0.3 + (int(r["n"]) - FIRST) * STEP, int(r["n"]), r["kind"] == "prime")
      for r in rows if FIRST <= int(r["n"]) <= LAST]
DUR = 8.2

CHORD = [0, 4, 7, 12, 16, 19, 24, 28, 31, 36]   # major triad stacked: right notes climb it
def pitch(n, base):
    m = base + CHORD[n]
    return m if n <= 4 else m + 1                 # wrong notes: a semitone off the chord

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
def bell(f, d=.9, idx=1.6, ratio=3.5, dur=2.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt + idx*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt)) * env(n, .003, d)
def square(f, dur, duty=.25):
    n = int(dur * SR); ph = (f * np.arange(n) / SR) % 1
    return np.where(ph < duty, 1.0, -1.0)
def piano(f, dec=1.2, dur=3.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum((.8 ** h) * np.sin(2*np.pi*f*h*(1 + .0004*h*h)*tt) * np.exp(-tt * (1 / dec + .6 * h)) for h in range(1, 8))
    return s * env(n, .004, 9)

# A · Boîte à cloches (airy, 66 BPM): right = clear glass bells; wrong = cracked bell (inharmonic, a semitone
# off, wobbling) + a small "crack" click; soft major pad that turns minor after the break.
def mood_a():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    brk = EV[[e[1] for e in EV].index(5)][0]
    maj, mnr = [48, 55, 60, 64, 67], [48, 55, 60, 63, 67]
    pad = np.zeros_like(L)
    for a, b in zip(maj, mnr):
        f = np.where(t < brk, mtof(a), mtof(b))
        for det in (.995, 1.005): pad += np.sin(2*np.pi*np.cumsum(f*det)/SR)
    L += .010 * pad * np.minimum(1, t / 1.0)
    for tm, n, ok in EV:
        f = mtof(pitch(n, 72))
        if ok:
            put(L, tm, .22 * bell(f, .9))
        else:
            nn = int(2.4 * SR); tt = np.arange(nn) / SR
            wob = f * (1 + .012 * np.sin(2*np.pi*5.5*tt))
            s = np.sin(2*np.pi*np.cumsum(wob)/SR + 2.4*np.exp(-tt*3)*np.sin(2*np.pi*np.cumsum(wob*2.76)/SR))
            put(L, tm, .22 * s * env(nn, .002, .6))
            put(L, tm, noise(.05, 8000, 60, n, 2500), .12)
    return reverb(L, .5, 1.4), "A"

# B · Chiptune enquête (punchy, 120 BPM): 8-bit kick/hat/bass; right = bright square ding;
# wrong = "error" buzzer (square sliding down) + noise snare. Groove never stops.
def mood_b():
    L = np.zeros(int(DUR * SR)); beat = .5
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.20, 120, 50) if k % 2 == 0 else noise(.12, 5000, 30, k, 900), 1 if k % 2 == 0 else .10)
        put(L, b + beat / 2, noise(.03, 9000, 140, 90 + k, 6000), .04)
        r = [36, 36, 41, 43][(k // 4) % 4]
        put(L, b, .05 * lowpass(square(mtof(r), beat * .8, .5), 1200) * env(int(beat * .8 * SR), .002, .2))
    for tm, n, ok in EV:
        f = mtof(pitch(n, 72))
        if ok:
            nn = int(.5 * SR); put(L, tm, .13 * square(f, .5, .25) * env(nn, .002, .15))
            put(L, tm + .09, .06 * square(f * 2, .5, .125) * env(nn, .002, .1))
        else:
            nn = int(.45 * SR); tt = np.arange(nn) / SR
            fs = f * np.exp(-tt * 2.2)
            s = np.where(((np.cumsum(fs) / SR) % 1) < .5, 1.0, -1.0)
            put(L, tm, .13 * s * env(nn, .002, .3))
            put(L, tm, .06 * square(f * 1.414, .45, .5) * env(nn, .002, .25))   # tritone grind
            put(L, tm, noise(.18, 6000, 18, 300 + n, 700), .12)
    return reverb(L, .12), "B"

# C · Énigme au piano (dark, slow, 60 BPM): low drone; right = warm piano notes on the chord;
# wrong = dissonant piano cluster + low thud, the drone darkens after the break.
def mood_c():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    brk = EV[[e[1] for e in EV].index(5)][0]
    drone = np.sin(2*np.pi*mtof(36)*t) + .5*np.sin(2*np.pi*mtof(43)*t)
    drone += np.where(t > brk, .45, 0) * np.sin(2*np.pi*mtof(37)*t)              # minor 2nd creeps in
    L += .04 * drone * (.75 + .25*np.sin(2*np.pi*t/4)) * np.minimum(1, t / 1.0)
    for k, b in enumerate(np.arange(0, DUR, 1.0)):
        put(L, b, kick(.09, 50, 36))
    for tm, n, ok in EV:
        m = pitch(n, 60)
        if ok:
            put(L, tm, .20 * piano(mtof(m), 1.4))
        else:
            for dm, g in [(0, .17), (1, .12), (-11, .14)]:
                put(L, tm, g * piano(mtof(m + dm), .9))
            put(L, tm, kick(.22, 60, 30))
    return reverb(L, .42, 1.6), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
for tm, n, ok in EV:
    print("F%d t=%.2f s %s" % (n, tm, "right" if ok else "WRONG"))
