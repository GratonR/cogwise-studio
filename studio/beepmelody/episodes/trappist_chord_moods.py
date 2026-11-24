"""BeepMelody · TRAPPIST-1 chord · co-pilot step 2: three 8 s mood excerpts on the busiest passage
(the drop: all 7 planets transiting together, time accelerated).
Data -> music (decision 1/4, angle "chord"): one transit = one note; each planet owns ONE pitch taken from the
period-ratio chain stacked from h (ratios rounded, Gillon 2017): h C3, g G3, f C4, e G4, d D5, c B5 -> folded to B4,
b G6 -> folded to G5 (kept within ~2.5 octaves, nothing shrill). Chord = C·D·G·B.
Loop (fixed, 4 bars): C – G/B – Am7 – G (bass C, B, A, G): every planet note fits every chord.
Transit times use the real periods (trappist_chord.csv); start phases are provisional for these excerpts
(real transit epochs set at render). Notes snapped to the 16th grid.
Usage: python3 trappist_chord_moods.py <trappist_chord.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
rows = {r["planet"]: float(r["period_d"]) for r in csv.DictReader(open(sys.argv[1]))}
OUT = sys.argv[2]
DUR = 8.0
PITCH = {"h": 48, "g": 55, "f": 60, "e": 67, "d": 74, "c": 71, "b": 79}
PAN = {"h": 0, "g": -.5, "f": .5, "e": -.3, "d": .3, "c": -.6, "b": .6}
PHASE = {"b": .10, "c": .35, "d": .62, "e": .20, "f": .80, "g": .45, "h": .05}   # provisional (fraction of period)
BASS = [36, 35, 33, 31]                                                         # C – G/B – Am7 – G

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lowpass(x, fc, o=2):
    b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def highpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def put(buf, t, sig, g=1.0, pan=0.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf):
        buf[i:j, 0] += g * np.sqrt(.5 * (1 - pan)) * sig[:j - i]
        buf[i:j, 1] += g * np.sqrt(.5 * (1 + pan)) * sig[:j - i]
def reverb(x, mix=.35, size=1.0):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
        n = int(d * size * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * np.stack([lowpass(out[:, k], 4500) for k in (0, 1)], 1)
def noise(dur, fc, dec, seed, hp=None):
    n = int(dur * SR); s = lowpass(np.random.RandomState(seed).randn(n), fc)
    if hp: s = highpass(s, hp)
    return s * np.exp(-np.arange(n) / SR * dec)
def kick(g=.3, f0=90, f1=45):
    n = int(.35 * SR); tt = np.arange(n) / SR
    return g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+f1)/SR) * np.exp(-tt*12)

def transits(days_per_s, grid):
    """real periods, accelerated; snapped to the 16th grid"""
    ev = []
    span = DUR * days_per_s
    for p, P in rows.items():
        k = 0
        while True:
            day = (PHASE[p] + k) * P
            if day >= span - .3 * days_per_s: break
            t = round(day / days_per_s / grid) * grid
            ev.append((t, p)); k += 1
    return sorted(ev)

# A · Boîte à musique céleste (airy, 76 BPM): glass bells / celesta per planet, soft pad on the loop, a shaker.
def mood_a():
    bpm = 76; beat = 60 / bpm; grid = beat / 4
    L = np.zeros((int((DUR + 3) * SR), 2)); t = np.arange(int(DUR * SR)) / SR
    for i, b in enumerate(np.arange(0, DUR, beat * 4)):
        root = BASS[i % 4]; n = int(beat * 4 * SR); tt = np.arange(n) / SR
        pad = sum(np.sin(2*np.pi*mtof(m)*det*tt) for m in (root + 12, root + 19, root + 24) for det in (.996, 1.004))
        put(L, b, .022 * pad * np.minimum(1, tt / .4) * np.minimum(1, (n / SR - tt) / .4))
        put(L, b, .10 * np.sin(2*np.pi*mtof(root)*tt) * env(n, .02, 1.6))
    for k, b in enumerate(np.arange(0, DUR, beat / 2)):
        put(L, b, noise(.06, 9000, 70, k, 5000), .035 if k % 2 else .02)
    for tm, p in transits(1.9, grid):
        f = mtof(PITCH[p] + 12); n = int(2.4 * SR); tt = np.arange(n) / SR
        s = np.sin(2*np.pi*f*tt + 1.4*np.exp(-tt*5)*np.sin(2*np.pi*f*3.5*tt)) * env(n, .003, .8)
        put(L, tm, .16 * s, pan=PAN[p])
    return reverb(L, .5, 1.4), "A"

# B · Synthwave orbitale (punchy, 112 BPM): gated drums, 8th-note octave bass, plucked saw voices,
# the scene's neon colours in sound.
def mood_b():
    bpm = 112; beat = 60 / bpm; grid = beat / 4
    L = np.zeros((int((DUR + 3) * SR), 2))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.30))
        if k % 2: put(L, b, noise(.22, 7000, 14, k, 600), .16)
        for h in (0, .5): put(L, b + h * beat, noise(.03, 10000, 150, 50 + k, 7000), .05)
    for k, b in enumerate(np.arange(0, DUR, beat / 2)):
        root = BASS[int(b / (beat * 4)) % 4] + (12 if k % 2 else 0)
        n = int(beat / 2 * .9 * SR); tt = np.arange(n) / SR
        saw = 2 * ((mtof(root) * tt) % 1) - 1
        put(L, b, .11 * lowpass(saw, 900) * env(n, .003, .18))
    for tm, p in transits(2.6, grid):
        f = mtof(PITCH[p]); n = int(.7 * SR); tt = np.arange(n) / SR
        saw = sum(2 * ((f * det * tt) % 1) - 1 for det in (.995, 1.005)) / 2
        s = lowpass(saw, 2600) * env(n, .002, .22)
        put(L, tm, .14 * s, pan=PAN[p]); put(L, tm + 3 * grid, .05 * s, pan=-PAN[p])   # dotted-8th echo
    return reverb(L, .2, .8), "B"

# C · Orgue lent (contemplative, 60 BPM): each transit swells a held organ tone that rings ~1.5 s,
# so the overlapping voices build the real chord; deep sub + soft clock tick.
def mood_c():
    bpm = 60; beat = 60 / bpm; grid = beat / 4
    L = np.zeros((int((DUR + 3) * SR), 2))
    for i, b in enumerate(np.arange(0, DUR, beat * 2)):
        root = BASS[i % 4]; n = int(beat * 2 * SR); tt = np.arange(n) / SR
        put(L, b, .13 * np.sin(2*np.pi*mtof(root - 12 + 12)*tt) * np.minimum(1, tt / .3) * np.minimum(1, (n / SR - tt) / .3))
    for k, b in enumerate(np.arange(0, DUR, beat / 2)):
        put(L, b, noise(.02, 6000, 200, k, 3000), .05 if k % 2 == 0 else .025)
    for tm, p in transits(1.4, grid):
        f = mtof(PITCH[p]); n = int(1.8 * SR); tt = np.arange(n) / SR
        s = sum(g * np.sin(2*np.pi*f*h*tt) for h, g in ((1, 1), (2, .5), (3, .25), (4, .12)))
        e = np.minimum(1, tt / .12) * np.exp(-tt / 1.0)
        put(L, tm, .085 * s * e, pan=PAN[p])
    return reverb(L, .45, 1.8), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    x = x[:int(DUR * SR) + int(.6 * SR)]
    fade = int(.6 * SR); x[-fade:] *= np.linspace(1, 0, fade)[:, None]
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (x * 32767).astype(np.int16))
for dps, name in ((1.9, "A"), (2.6, "B"), (1.4, "C")):
    ev = transits(dps, 1)
    print(name, "days/s", dps, "window", round(DUR * dps, 1), "d, transits", len(transits(dps, .01)))
