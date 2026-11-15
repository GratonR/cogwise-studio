"""BeepMelody · wave-spectrum · RETRAVAIL r1, step 2 (sound).
Guillaume (15 Nov): "change le son et les visuels. pourquoi pas essayer de faire matcher le son avec l'onde ?"
Rule for all three demos: each wave plays its REAL note (pitch class of its real frequency, moved by whole octaves
into hearing); the octave follows its place on the ruler (slow wave = low register, fast wave = high register).
LIGO and the humpback whale are already audible: they play at their real pitch, octave included.
Demo window = the busiest passage (1955 -> 1971, 8 discoveries), 8 s each.
usage: python3 wave_spectrum_r1_demos.py <out_dir>
"""
import sys, os, csv, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = list(csv.DictReader(open(os.path.join(HERE, "wave_spectrum.csv"))))
LG = [math.log10(float(r["freq_hz"])) for r in ROWS]
LO, HI = min(LG), max(LG)
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def real_midi(f): return 69 + 12 * math.log2(f / 440.0)
def note_for(i):
    f = float(ROWS[i]["freq_hz"]); m = round(real_midi(f))
    if 40 <= m <= 90: return m, 0                              # already audible: real pitch, real octave
    target = 45 + (LG[i] - LO) / (HI - LO) * 36                  # register from place on the ruler (A2..A5)
    k = round((target - m) / 12); return m + 12 * k, k
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc): return lfilter(*butter(2, min(fc, SR / 2 - 100) / (SR / 2)), x)
def hp(x, fc): return lfilter(*butter(2, fc / (SR / 2), 'high'), x)
def tt(d): return np.arange(int(d * SR)) / SR

WIN = list(range(12, 20))                                       # 1955 .. 1971
DUR = 8.0

def chirp(d=0.6, f0=35, f1=250):
    t = tt(d + .25); tc = d + .002
    f = np.clip(f0 * ((tc - np.minimum(t, d)) / tc) ** (-3 / 8), f0, f1)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / .05) * np.exp(-np.maximum(0, t - d) * 18)

class Mix:
    def __init__(s): s.L = np.zeros(int((DUR + 2) * SR)); s.R = s.L.copy(); s.fx = s.L.copy()
    def put(s, t, x, pan=0.0, send=0.0, v=1.0):
        i = int(t * SR); x = x[:max(0, len(s.L) - i)] * v
        s.L[i:i + len(x)] += x * (1 - pan) / 2 ** .5 * 1.2; s.R[i:i + len(x)] += x * (1 + pan) / 2 ** .5 * 1.2
        s.fx[i:i + len(x)] += x * send
    def out(s, path, verb=0.35, delay=0.0):
        e = s.fx.copy()
        for d, g in ((0.031, .5), (0.047, .45), (0.071, .4), (0.113, .35), (0.167, .3)):
            k = int(d * SR); e[k:] += s.fx[:-k] * g
        e = lp(e, 4000) * verb
        if delay:
            k = int(delay * SR); dl = np.zeros_like(s.fx); dl[k:] += s.fx[:-k] * .35; e += lp(dl, 3000)
        L, R = s.L + e, s.R + np.roll(e, 300)
        n = int(DUR * SR); L, R = L[:n], R[:n]
        fade = np.ones(n); fade[-int(.4 * SR):] = np.linspace(1, 0, int(.4 * SR)); L *= fade; R *= fade
        pk = max(np.abs(L).max(), np.abs(R).max()); L, R = L / pk * .89, R / pk * .89
        wavfile.write(path, SR, (np.stack([L, R], 1) * 32767).astype(np.int16))

def times(bpm, beats_first=1.0, gaps=None):
    b = 60 / bpm; t = [beats_first * b]
    for g in gaps: t.append(t[-1] + g * b)
    return t

# ---------- A · "La vraie note" : pure tones, cosmic, 76 BPM, no drums ----------
def demo_a(path):
    m = Mix(); bpm = 76; b = 60 / bpm
    T = times(bpm, 0.5, [1.25, 1.25, 1.0, 1.25, 1.0, 0.75, 1.25])
    t = tt(DUR + 2); pad = np.zeros_like(t)
    for k, f in enumerate((55.0, 82.4, 110.0)):                 # open fifths drone, no key clash
        pad += np.sin(2 * np.pi * f * t + k) * (.5 + .5 * np.sin(2 * np.pi * .11 * t + k)) * .05
    m.put(0, lp(pad + np.random.default_rng(1).normal(0, .02, len(t)), 900), send=.3)
    for i, ti in zip(WIN, T):
        mi, _ = note_for(i); f = mtof(mi); fam = ROWS[i]["family"]
        if fam == "sound":                                       # whale: real 400 Hz glide
            x = tt(1.6); s = np.sin(2 * np.pi * np.cumsum(f * (0.85 + .15 * np.minimum(1, x / .5))) / SR)
            s *= np.minimum(1, x / .15) * np.exp(-x * 1.6) * .5
        else:
            x = tt(2.2); s = (np.sin(2 * np.pi * f * x) + .25 * np.sin(2 * np.pi * 2 * f * x) + .1 * np.sin(2 * np.pi * 3.01 * f * x))
            s *= np.minimum(1, x / .006) * np.exp(-x * 1.4) * .45
        m.put(ti, s, pan=(LG[i] - LO) / (HI - LO) * 1.2 - .6, send=.7)
    m.out(path, verb=.6, delay=b * .75)

# ---------- B · "Chaque onde a sa voix" : funk 104 BPM, each family its own sound, bass jumps to the wave's note ----------
def demo_b(path):
    m = Mix(); bpm = 104; b = 60 / bpm; s16 = b / 4
    T = times(bpm, 1.0, [2, 2, 1.5, 2, 1.5, 1.0, 2])
    nb = int(DUR / b) + 1
    for k in range(nb):
        t0 = k * b
        x = tt(.32); kick = np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-x * 18) + 45) / SR) * np.exp(-x * 11))
        if k % 2 == 0 or k % 4 == 3: m.put(t0, kick, v=.7)
        if k % 2 == 1:
            x = tt(.2); sn = lp(np.random.default_rng(k).normal(0, 1, len(x)), 6000) * np.exp(-x * 22) * .35
            m.put(t0, sn + np.sin(2 * np.pi * 190 * x) * np.exp(-x * 30) * .2, send=.2)
        for q in range(4):
            x = tt(.05); hh = hp(np.random.default_rng(99 + q).normal(0, 1, len(x)), 7000) * np.exp(-x * 90) * (.12 if q % 2 else .06)
            m.put(t0 + q * s16 + (s16 * .12 if q % 2 else 0), hh, pan=.3)
    # slap bass: follows the note of the last wave heard (funk 16th pattern)
    pat = [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0]; oc = [0, 0, 0, 12, 0, 0, 0, 0, 7, 0, 0, 12, 0, 10, 0, 0]
    cur = 36
    for k in range(int(DUR / s16)):
        t0 = k * s16
        for i, ti in zip(WIN, T):
            if ti <= t0 + 1e-6: cur = 31 + (note_for(i)[0] % 12)
        if pat[k % 16]:
            x = tt(s16 * 1.6); f = mtof(cur + oc[k % 16])
            s = np.tanh(2.2 * (np.sin(2 * np.pi * f * x) + .4 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 9)) * .3
            m.put(t0, lp(s, 1400))
    for i, ti in zip(WIN, T):
        mi, _ = note_for(i); f = mtof(mi); lab = ROWS[i]["label"]; lg = LG[i]
        if ROWS[i]["family"] == "sound":                         # whale: real song glide at 400 Hz
            x = tt(1.4); s = np.sin(2 * np.pi * np.cumsum(f * (0.8 + .2 * np.sin(np.pi * np.minimum(1, x / 1.2)))) / SR)
            s *= np.minimum(1, x / .1) * np.exp(-x * 1.8) * .55
        elif "SPUTNIK" in lab:                                   # the real beep-beep (0.3 s on / off)
            s = np.zeros(int(1.2 * SR)); x = tt(.3)
            for o in (0, .6): i0 = int(o * SR); s[i0:i0 + len(x)] += np.sign(np.sin(2 * np.pi * f * x)) * .22
        elif "PULSAR" in lab:                                    # lighthouse ticks (CP 1919 period 1.337 s, sped x8)
            s = np.zeros(int(1.4 * SR)); x = tt(.04)
            for o in np.arange(0, 1.3, 1.337 / 8): i0 = int(o * SR); s[i0:i0 + len(x)] += np.sin(2 * np.pi * f * x) * np.exp(-x * 80) * .6
        elif lg < 12:                                            # radio: buzzy tone through static
            x = tt(1.0); s = (np.sign(np.sin(2 * np.pi * f * x)) * .12 + np.random.default_rng(3).normal(0, .05, len(x)))
            s = lp(s, 3500) * np.exp(-x * 3)
        elif lg < 16:                                            # visible light: glassy shimmer
            x = tt(1.4); s = sum(np.sin(2 * np.pi * f * h * x) / h for h in (1, 2, 3, 4.01)) * np.exp(-x * 2.5) * .3
        else:                                                    # x / gamma: crunchy bright hit
            x = tt(.6); s = np.tanh(4 * np.sin(2 * np.pi * f * x)) * .25 * np.exp(-x * 6) + hp(np.random.default_rng(5).normal(0, .2, len(x)), 5000) * np.exp(-x * 14)
        m.put(ti, s, pan=(lg - LO) / (HI - LO) * 1.2 - .6, send=.45, v=1.1)
    m.out(path, verb=.35, delay=b * .75)

# ---------- C · "L'onde donne le rythme" : synthwave 98 BPM; each note flutters at a speed set by its frequency ----------
def demo_c(path):
    m = Mix(); bpm = 98; b = 60 / bpm; s16 = b / 4
    T = times(bpm, 1.0, [2, 1.5, 1.5, 2, 1.5, 1.0, 2])
    nb = int(DUR / b) + 1
    for k in range(nb):
        t0 = k * b; x = tt(.35)
        m.put(t0, np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 20) + 42) / SR) * np.exp(-x * 9) * .75)
        if k % 2 == 1:
            x = tt(.5); sn = lp(np.random.default_rng(k).normal(0, 1, len(x)), 5000) * np.exp(-x * 9) * .3
            m.put(t0, sn, send=.8)
    cur = 45
    for k in range(int(DUR / s16)):                                # 8th-note octave bass (synthwave)
        t0 = k * s16
        for i, ti in zip(WIN, T):
            if ti <= t0 + 1e-6: cur = 33 + (note_for(i)[0] % 12)
        if k % 2 == 0:
            x = tt(s16 * 1.8); f = mtof(cur + (12 if k % 4 == 2 else 0))
            saw = 2 * ((f * x) % 1) - 1; m.put(t0, lp(saw, 900) * np.exp(-x * 6) * .22)
    for i, ti in zip(WIN, T):
        mi, _ = note_for(i); f = mtof(mi); r = (LG[i] - LO) / (HI - LO)
        x = tt(1.6); rate = 2 + 22 * r                          # slow wave = slow pulse, fast wave = fast flutter
        gate = .5 + .5 * np.sign(np.sin(2 * np.pi * rate * x))
        saw = sum(2 * ((f * dt * x) % 1) - 1 for dt in (1, 1.006, .994)) / 3
        s = lp(saw, 2500 + 4000 * r) * gate * np.minimum(1, x / .01) * np.exp(-x * 1.5) * .35
        if ROWS[i]["family"] == "sound":
            s = np.sin(2 * np.pi * np.cumsum(f * (0.85 + .15 * np.minimum(1, x / .5))) / SR) * np.exp(-x * 1.6) * .5
        m.put(ti, s, pan=r * 1.2 - .6, send=.6)
    m.out(path, verb=.5, delay=b * .5)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for k, fn in (("A", demo_a), ("B", demo_b), ("C", demo_c)): fn(os.path.join(out, f"r1_demo_{k}.wav"))
    for i in WIN:
        mi, k = note_for(i); print(ROWS[i]["year"], ROWS[i]["label"], NAMES[mi % 12], f"{k:+d} oct")
