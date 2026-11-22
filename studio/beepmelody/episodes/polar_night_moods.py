"""BeepMelody · Polar night · co-pilot step 2: three 8 s mood excerpts on the strongest passage.
Window = 3 Nov -> 16 Dec 2026 (44 days, same pace as the full video: ~5.6 days per second):
Tromsø's daylight falls from 6.22 h to 0.33 h (27 Nov), then 0 h = silence, while Quito keeps ~12.1 h.
Every day = one hit per city (Tromsø silent when daylight = 0). Pitch = hours of daylight (same scale for both
cities, D major, 0 h -> D3 ... 24 h -> D6); Tromsø's note also gets shorter as its day gets shorter.
Usage: python3 polar_night_moods.py <outdir>"""
import sys, os, csv
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100; DUR = 8.0; OUT = sys.argv[1]
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "polar_night_draft.csv")))
        if "2026-11-03" <= r["date"] <= "2026-12-16"]
DAY = 1 / 5.6
EV = [(0.15 + i * DAY, float(r["tromso_daylight_h"]), float(r["quito_daylight_h"])) for i, r in enumerate(rows)]

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
MAJ = [0, 2, 4, 5, 7, 9, 11]
def pitch(h):
    k = int(round(h / 24 * 21)); return 50 + 12 * (k // 7) + MAJ[k % 7]
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
def env(n, a, dec):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t * dec)
def marimba(f, dur, dec):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 25)) * env(n, .001, dec)
def bell(f, dur, dec):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 5)) * env(n, .002, dec)
def softsynth(f, dur, dec):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * d * t) for d in (.997, 1.003)) / 2 + .15 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(n, .02, dec)
def noise(dur, seed, hp=None, lp=None, dec=20):
    n = int(dur * SR); x = np.random.RandomState(seed).randn(n)
    if hp: x = highpass(x, hp)
    if lp: x = lowpass(x, lp)
    return x * np.exp(-np.arange(n) / SR * dec)
def aurora(n, t, start, gain):
    """shimmering high pad that fades in once Tromsø goes silent."""
    a = sum(np.sin(2 * np.pi * mtof(m) * t + 2 * np.sin(2 * np.pi * .3 * t + m)) for m in (81, 85, 88)) / 3
    return gain * a * (.6 + .4 * np.sin(2 * np.pi * .7 * t)) * np.clip((t - start) / 1.2, 0, 1)
SILENT = next(tm for tm, h, _ in EV if h == 0)

# A · Duo clair (DA altitude-race): Tromsø = marimba that falls and shortens, Quito = soft warm synth on the
# same steady note; light 84 BPM pulse; aurora shimmer during the silence.
def mood_a():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n)
    for b in np.arange(0, DUR, 60 / 84):
        put(L, b, .05 * noise(.05, int(b * 99), hp=5000, dec=60))
    for tm, ht, hq in EV:
        put(L, tm, .07 * softsynth(mtof(pitch(hq)), .3, 8))
        if ht > 0: put(L, tm, .22 * marimba(mtof(pitch(ht) + 12), .6, 12 - 1.2 * ht))
    L += aurora(n, t, SILENT, .025)
    return reverb(soft(L), .35), "A"

# B · Nuit arctique: dark, slow, sparse (60 BPM). Low D drone + wind; Tromsø = glass bell going lower and
# quieter; Quito = a low soft pulse each day; silence = wind and a faint aurora.
def mood_b():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n)
    L += .018 * np.sin(2 * np.pi * mtof(38) * t) + .01 * np.sin(2 * np.pi * mtof(45) * t * 1.002)
    L += .03 * lowpass(highpass(np.random.RandomState(4).randn(n), 200), 900) * (.6 + .4 * np.sin(2 * np.pi * .15 * t))
    for tm, ht, hq in EV:
        put(L, tm, .05 * lowpass(softsynth(mtof(pitch(hq) - 12), .25, 10), 700))
        if ht > 0: put(L, tm, (.1 + .03 * ht) * bell(mtof(pitch(ht) + 12), 1.0, 7 - .6 * ht))
    L += aurora(n, t, SILENT, .02)
    return reverb(soft(L), .5, 1.4), "B"

# C · Pulsation (110 BPM): brighter and rhythmic. Quito = soft kick + kalimba-ish tick every day (the steady
# heartbeat), Tromsø = plucked lead falling; when Tromsø stops, the beat stays alone with the aurora.
def mood_c():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n); beat = 60 / 110
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kk = int(.22 * SR); tt = np.arange(kk) / SR
        put(L, b, .2 * np.sin(2 * np.pi * np.cumsum(85 * np.exp(-tt * 25) + 48) / SR) * np.exp(-tt * 15))
        if k % 2: put(L, b, .08 * noise(.12, k, hp=1500, lp=7000, dec=25))
        put(L, b + beat / 2, .04 * noise(.03, 50 + k, hp=7000, dec=90))
        put(L, b, .05 * lowpass(softsynth(mtof([38, 38, 43, 45][(k // 4) % 4]), beat, 3), 600))
    for tm, ht, hq in EV:
        put(L, tm, .06 * marimba(mtof(pitch(hq) + 12), .2, 30))
        if ht > 0: put(L, tm, .16 * np.where(np.sin(2 * np.pi * mtof(pitch(ht) + 12) * np.arange(int(.3 * SR)) / SR) > .3, 1., -1.) * env(int(.3 * SR), .002, 14 - 1.3 * ht))
    L += aurora(n, t, SILENT, .02)
    return reverb(soft(L), .2), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.4 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("days:", len(EV), "Tromsø silent from", round(SILENT, 2), "s", rows[0]["date"], "->", rows[-1]["date"])
