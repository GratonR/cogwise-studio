"""BeepMelody · Polar night · rework (Tromsø only) · co-pilot step 2: three 8 s single-voice mood excerpts.
Window = 6 Nov -> 23 Dec 2026 (48 days at the video pace, 6 days per second = 8 s):
Tromsø's daylight falls from ~5.6 h to 0 h (last sunrise 27 Nov), then 0 h = silence for the rest of the clip.
Every day = one hit (silent when daylight = 0). Pitch = hours of daylight (D major, 0 h -> D3 ... 24 h -> D6);
the note also gets shorter as the day gets shorter. One data voice only (no Quito).
Usage: python3 polar_night_moods_r.py <outdir>"""
import sys, os, csv
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100; DUR = 8.0; OUT = sys.argv[1]
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "polar_night_draft.csv")))
        if "2026-11-06" <= r["date"] <= "2026-12-23"]
DAY = 1 / 6.0
EV = [(0.1 + i * DAY, float(r["tromso_daylight_h"])) for i, r in enumerate(rows)]

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
    return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 5)
            + .15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 9)) * env(n, .002, dec)
def softsynth(f, dur, dec, a=.02):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * d * t) for d in (.997, 1.003)) / 2 + .15 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(n, a, dec)
def pluck(f, dur, dec):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * dec * k * .6) for k in range(1, 6))
    return s * env(n, .002, dec * .5)
def noise(dur, seed, hp=None, lp=None, dec=20):
    n = int(dur * SR); x = np.random.RandomState(seed).randn(n)
    if hp: x = highpass(x, hp)
    if lp: x = lowpass(x, lp)
    return x * np.exp(-np.arange(n) / SR * dec)
def aurora(n, t, start, gain):
    a = sum(np.sin(2 * np.pi * mtof(m) * t + 2 * np.sin(2 * np.pi * .3 * t + m)) for m in (81, 85, 88)) / 3
    return gain * a * (.6 + .4 * np.sin(2 * np.pi * .7 * t)) * np.clip((t - start) / 1.2, 0, 1)
SILENT = next(tm for tm, h in EV if h == 0)

# A · Marimba claire (84 BPM) — the chosen "duo clair" minus Quito: marimba falls and shortens, light hat + soft
# bass carry on through the night, aurora shimmer fills the silence. Midnight sun = the same note held.
def mood_a():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n); beat = 60 / 84
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, .05 * noise(.05, k * 7, hp=5000, dec=60))
        if k % 4 == 0: put(L, b, .06 * lowpass(softsynth(mtof([38, 43, 45, 38][(k // 4) % 4]), beat * 3.6, 1.2, .05), 500))
    for tm, h in EV:
        if h > 0: put(L, tm, .24 * marimba(mtof(pitch(h) + 12), .6, max(3.0, 12 - 1.2 * min(h, 8))))
    L += aurora(n, t, SILENT, .03)
    return reverb(soft(L), .35), "A"

# B · Cloche de verre (60 BPM, sombre et froid) — no beat: low D drone + wind; each day = a glass bell, lower and
# quieter as the day shrinks; the night is real silence (wind only, a faint aurora far away).
def mood_b():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n)
    L += .02 * np.sin(2 * np.pi * mtof(38) * t) + .012 * np.sin(2 * np.pi * mtof(45) * t * 1.002)
    L += .035 * lowpass(highpass(np.random.RandomState(4).randn(n), 200), 900) * (.6 + .4 * np.sin(2 * np.pi * .15 * t))
    for tm, h in EV:
        if h > 0: put(L, tm, (.12 + .03 * h) * bell(mtof(pitch(h) + 12), 1.2, 7 - .6 * min(h, 8)))
    L += aurora(n, t, SILENT, .015)
    return reverb(soft(L), .5, 1.4), "B"

# C · Pouls sous la neige (100 BPM, plus rythmé) — soft kick + pluck lead that falls; when the sun is gone the
# kick keeps beating, muffled (low-passed) like a heartbeat in the dark, and the lead is gone.
def mood_c():
    n = int(DUR * SR); t = np.arange(n) / SR; L = np.zeros(n); beat = 60 / 100
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kk = int(.22 * SR); tt = np.arange(kk) / SR
        kick = np.sin(2 * np.pi * np.cumsum(85 * np.exp(-tt * 25) + 48) / SR) * np.exp(-tt * 15)
        dark = b >= SILENT
        put(L, b, (.16 if dark else .2) * (lowpass(kick, 180) * 1.6 if dark else kick))
        if not dark:
            if k % 2: put(L, b, .07 * noise(.12, k, hp=1500, lp=7000, dec=25))
            put(L, b + beat / 2, .035 * noise(.03, 50 + k, hp=7000, dec=90))
        put(L, b, .05 * lowpass(softsynth(mtof([38, 38, 43, 45][(k // 4) % 4]), beat, 3), 600 if not dark else 300))
    for tm, h in EV:
        if h > 0: put(L, tm, .2 * pluck(mtof(pitch(h) + 12), .4, 14 - 1.2 * min(h, 8)))
    L += aurora(n, t, SILENT, .02)
    return reverb(soft(L), .2), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.4 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_r_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("days:", len(EV), "first", rows[0]["date"], rows[0]["tromso_daylight_h"], "h; silent from",
      round(SILENT, 2), "s; last", rows[-1]["date"])
