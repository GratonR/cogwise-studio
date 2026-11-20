"""BeepMelody · Every tallest building · co-pilot step 2: three 8 s mood excerpts on the densest passage.
Clock (step 1): 1 year = 1 tick = 0.4 s (a quarter note at 150 BPM). Each record lands at its year (+ month if known).
Window = mid-1912 -> 1933 (20.5 years): Woolworth (1913), then 17 years of ticks only, then the 1930-31 burst
(40 Wall Street Apr 1930, Chrysler May 1930, Empire State May 1931).
Pitch = log(height) on a major pentatonic over the whole series (94 m -> 828 m = 2 1/2 octaves): taller = higher.
Usage: python3 tallest_buildings_moods.py <tallest_buildings_draft.csv> <outdir>"""
import sys, csv, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
YEAR = 0.4
Y0 = 1912.5
NY = 20.5
DUR = NY * YEAR + 0.6            # 8.8 s
OUT = sys.argv[2]
MONTH = {"40 Wall Street": 4, "Chrysler Building": 5, "Empire State Building": 5, "Woolworth Building": 4}

rows = list(csv.DictReader(open(sys.argv[1])))
HMIN, HMAX = 94.0, 828.0
PENT = [0, 2, 4, 7, 9]
def height_note(h, base):
    x = (math.log(h) - math.log(HMIN)) / (math.log(HMAX) - math.log(HMIN))
    d = int(round(x * 12))                                     # 13 pentatonic steps over the series
    return base + 12 * (d // 5) + PENT[d % 5]

EV = []
for r in rows:
    y = int(r["year"]) + (MONTH.get(r["name"], 6) - 1) / 12
    if Y0 <= y < Y0 + NY:
        EV.append(((y - Y0) * YEAR + .05, float(r["height_m"]), r["name"]))
EV.sort()
for i in range(1, len(EV)):                                    # same-year records: keep them a 1/8 note apart
    if EV[i][0] - EV[i - 1][0] < YEAR / 2:
        EV[i] = (EV[i - 1][0] + YEAR / 2,) + EV[i][1:]
TICKS = [(k + .5) * YEAR + .05 for k in range(int(NY))]       # one tick per Jan 1 inside the window

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
def bell(f, d=.9, idx=1.6, ratio=3.5, dur=2.4):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt + idx*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt)) * env(n, .003, d)
def marimba(f, d=.35):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25)) * env(n, .002, d)
def saw(f, dur, det=(.995, 1.0, 1.005)):
    n = int(dur * SR); tt = np.arange(n) / SR
    return sum(2 * ((f * d * tt) % 1) - 1 for d in det) / len(det)
def piano(f, d=.9):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    s = sum((.8 ** h) * np.sin(2*np.pi*f*(h+1)*(1 + .0004*h*h)*tt) * np.exp(-tt * (1.2 + .9*h)) for h in range(8))
    return s * env(n, .003, d)
def brass(f, dur=.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = lowpass(saw(f, dur), 900 + 2600 * np.exp(-0)) * np.minimum(1, tt / .02) * np.exp(-tt * 3)
    return s

# A · Chantier (construction) — 150 BPM straight, punchy. Ticks = rivet hits on the beat; offbeat hats;
# a record = brass stab chord (pitch = height) + crash + low boom (the old tower is crushed).
def mood_a():
    L = np.zeros(int(DUR * SR))
    roots = [36, 36, 41, 43]
    for k, b in enumerate(TICKS):
        put(L, b, kick(.20, 90, 50))
        put(L, b, noise(.03, 9000, 160, 10 + k, 2500), .09)                     # the rivet
        put(L, b + YEAR / 2, noise(.04, 9000, 120, 60 + k, 5000), .03)
        r = roots[(k // 4) % 4]; nn = int(YEAR * .45 * SR); tt = np.arange(nn) / SR
        put(L, b + YEAR / 2, .06 * lowpass(saw(mtof(r), YEAR * .45), 600) * np.exp(-tt * 9))
    for tm, h, name in EV:
        m = height_note(h, 60)
        for iv in (0, 4, 7):
            put(L, tm, .08 * brass(mtof(m + iv), .55))
        put(L, tm, noise(1.2, 8000, 3, 300, 3000), .06)
        put(L, tm, kick(.40, 70, 32))
    return reverb(L, .18), "A"

# B · Course au ciel (as the pilot) — 75 BPM half-time feel, light. Ticks = soft wood-block clock;
# a record = marimba + bell (pitch = height) over a soft synth pad that brightens with every record.
def mood_b():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    pad = np.zeros_like(L)
    for m in [48, 55, 60, 64, 67]:
        for det in (.995, 1.0, 1.005): pad += np.sin(2*np.pi*mtof(m)*det*t)
    bright = np.ones_like(L) * .6
    for tm, _, _ in EV: bright[int(tm * SR):] += .25
    L += .006 * lowpass(pad, 3000) * bright * np.minimum(1, t / 1.0)
    for k, b in enumerate(TICKS):
        n = int(.08 * SR); tt = np.arange(n) / SR
        put(L, b, .05 * np.sin(2*np.pi*1100*tt) * np.exp(-tt * 60))             # wood-block tick
        if k % 2 == 0: put(L, b, kick(.10, 60, 42))
    for tm, h, name in EV:
        m = height_note(h, 72)
        put(L, tm, .20 * marimba(mtof(m), .4))
        put(L, tm, .10 * bell(mtof(m + 12), .8))
    return reverb(L, .45, 1.2), "B"

# C · Manhattan 1930 — swing at 150 BPM (art-deco jazz). Ticks = brushed snare on the beat, walking upright bass;
# a record = piano chord (pitch = height) + muted brass answer.
def mood_c():
    L = np.zeros(int(DUR * SR))
    walk = [43, 45, 47, 48, 50, 48, 47, 45]
    for k, b in enumerate(TICKS):
        put(L, b, noise(.18, 6000, 18, 100 + k, 1500), .04)                     # brush
        put(L, b + YEAR * .66, noise(.05, 8000, 80, 200 + k, 5000), .02)        # swung ride
        nn = int(YEAR * .9 * SR); tt = np.arange(nn) / SR
        f = mtof(walk[k % 8] - 12)
        put(L, b, .16 * (np.sin(2*np.pi*f*tt) + .3*np.sin(4*np.pi*f*tt)) * np.minimum(1, tt/.01) * np.exp(-tt * 4))
    for tm, h, name in EV:
        m = height_note(h, 60)
        for iv in (0, 4, 7, 11):
            put(L, tm, .07 * piano(mtof(m + iv), .8))
        put(L, tm + YEAR * .66, .05 * lowpass(brass(mtof(m + 12), .35), 1400))
    return reverb(L, .3, 1.0), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("window %.1f -> %.1f: %d ticks, %d records, %.2f s" % (Y0, Y0 + NY, len(TICKS), len(EV), DUR))
for tm, h, name in EV: print("REC", name, h, "m", "t=%.2f s" % tm, "note", height_note(h, 60))
