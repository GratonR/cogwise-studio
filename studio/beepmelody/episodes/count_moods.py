"""BeepMelody · life-timeline rework (angle « count ») · co-pilot step 2: three 8 s mood excerpts
on the busiest passage of the data: the final climb, humans (8.2e9) -> viruses (~1e31), events packed closer and closer.
One event = one count of living things; pitch = its power of ten, one step up per power, 4 octaves in total.
Usage: python3 count_moods.py <life_count.csv> <outdir>"""
import sys, csv, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
ROWS = list(csv.DictReader(open(sys.argv[1])))
OUT = sys.argv[2]
EXP_ALL = [math.log10(float(r["value"])) for r in ROWS]
EMAX = max(EXP_ALL)
EV = [e for e in EXP_ALL if e >= 9.0]                      # humans -> viruses

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
PENTA = [0, 2, 4, 7, 9]
def pitch(e, base):                                         # 1 -> 10^31 spread on 4 octaves of major pentatonic
    k = int(round(e / EMAX * 20)); return base + 12 * (k // 5) + PENTA[k % 5]
def lowpass(x, fc, o=2):
    b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def highpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += g * sig[:j - i]
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def reverb(x, mix=.3):
    out = x.copy()
    for d, g in [(.071, .5), (.113, .44), (.173, .37), (.241, .3), (.331, .24), (.449, .17), (.607, .12), (.83, .08), (1.1, .05)]:
        n = int(d * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 5000)
def times(bpm):
    """events accelerate (gaps shrink by 12 % each), snapped to a 16th grid, from 0.25 s to ~6.6 s"""
    n = len(EV); gaps = np.array([0.88 ** i for i in range(n - 1)]); gaps *= 6.35 / gaps.sum()
    t = np.concatenate([[0.25], 0.25 + np.cumsum(gaps)]); s16 = 60 / bpm / 4
    return [round(x / s16) * s16 for x in t]
def kick(L, b, g=.3, f0=52):
    n = int(.4 * SR); tt = np.arange(n) / SR
    put(L, b, g * np.sin(2 * np.pi * np.cumsum(110 * np.exp(-tt * 22) + f0) / SR) * np.exp(-tt * 9))
def noise(L, b, dur, fc, dec, g, seed, hp=None):
    n = int(dur * SR); x = np.random.RandomState(seed).randn(n)
    x = highpass(x, hp) if hp else lowpass(x, fc)
    put(L, b, g * x * np.exp(-np.arange(n) / SR * dec))
def celesta(f, dur=1.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * tt + 1.1 * np.exp(-tt * 6) * np.sin(2 * np.pi * f * 4 * tt))
    return s * env(n, .002, .55)
def marimba(f, dur=.7):
    n = int(dur * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * f * 3.93 * tt) * np.exp(-tt * 30)) * env(n, .001, .22)
def pluck(f, dur=.9, damp=.996, seed=0):                    # Karplus-Strong pizzicato
    n = int(dur * SR); p = max(2, int(SR / f)); buf = np.random.RandomState(seed).uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = damp * .5 * (buf[i % p] + buf[(i + 1) % p])
    return lowpass(out, 3500) * env(n, .001, .5)
def saw_pad(freqs, n, cutoff):
    t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for d in (.996, 1.0, 1.004):
            s += 2 * ((t * f * d) % 1) - 1
    return lowpass(s / (3 * len(freqs)), cutoff)

# A · « L'échelle » — 96 BPM. Celesta alone at first; each new power of ten adds a voice (sub, pad, hats);
# under each note, a swarm of tiny clicks whose density grows with the exponent: you hear the numbers explode.
def mood_a():
    bpm = 96; L = np.zeros(int(DUR * SR)); tms = times(bpm); beat = 60 / bpm
    for i, (e, tm) in enumerate(zip(EV, tms)):
        f = mtof(pitch(e, 60))
        put(L, tm, celesta(f), .22)
        nclicks = int(4 + (e - 9) * 9)                     # 4 clicks at 10^9 ... ~200 at 10^31
        rs = np.random.RandomState(i)
        for c in rs.uniform(0, 1.2, nclicks):
            n = int(.012 * SR); x = rs.randn(n) * np.exp(-np.arange(n) / SR * 400)
            put(L, tm + c, highpass(x, 3000 + rs.uniform(0, 5000)), .05 * (1 - c / 1.4))
        if i >= 3:                                          # sub voice from the 4th rung
            n = int(1.2 * SR); tt = np.arange(n) / SR
            put(L, tm, .15 * np.sin(2 * np.pi * mtof(pitch(e, 36)) * tt) * env(n, .01, .6))
    start = tms[5]; n = len(L) - int(start * SR)               # pad joins at the 6th rung
    pad = saw_pad([mtof(m) for m in (60, 64, 67, 72)], n, 1800) * np.linspace(0, 1, n) ** 1.5
    put(L, start, pad, .10)
    for b in np.arange(tms[7], DUR, beat / 2):                 # hats join at the 8th rung
        noise(L, b, .04, 0, 120, .035, int(b * 100), hp=7000)
    return reverb(L, .35), "A"

# B · « Organic house » — 122 BPM. Four-on-the-floor kick, shaker, rolling log-drum bass, marimba = the counts;
# a filter opens a little more on every power of ten, the drop lands on the last number.
def mood_b():
    bpm = 122; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; tms = times(bpm)
    roots = [45, 41, 36, 43]                                  # Am F C G
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kick(L, b, .3)
        noise(L, b + beat / 2, .06, 0, 70, .05, k, hp=6000)
        if k % 2: noise(L, b, .16, 2800, 20, .07, 200 + k)  # clap-ish
        for s in (1, 3):
            noise(L, b + s * beat / 4, .03, 0, 160, .02, 400 + k + s, hp=8000)
    bar = 4 * beat
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q, off in enumerate((0, .75, 1.5, 2.5, 3.25)):
            n = int(.35 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + (12 if q == 3 else 0))
            put(L, b + off * beat, .2 * np.sin(2 * np.pi * np.cumsum(f * (1 + .5 * np.exp(-tt * 40))) / SR) * np.exp(-tt * 7))
    chords = np.zeros_like(L)
    for k, b in enumerate(np.arange(0, DUR, bar)):
        r = roots[k % 4] + 24; n = int(bar * SR)
        put(chords, b, saw_pad([mtof(r), mtof(r + (3 if k % 4 == 0 else 4)), mtof(r + 7)], n, 6000), .07)
    # filter opens step by step with the data
    cut = np.full(len(L), 400.0)
    for i, tm in enumerate(tms):
        cut[int(tm * SR):] = 400 + 260 * (i + 1)
    out = np.zeros_like(chords)
    for i0 in range(0, len(L), 2048):
        out[i0:i0 + 2048] = lowpass(chords[max(0, i0 - 4096):i0 + 2048], cut[i0])[-len(chords[i0:i0 + 2048]):]
    L += out
    for e, tm in zip(EV, tms):
        f = mtof(pitch(e, 60)); put(L, tm, marimba(f), .3); put(L, tm + 3 * beat / 4, marimba(f), .09)
    noise(L, tms[-1], 1.4, 7000, 2.2, .12, 999)               # drop crash on the last count
    return reverb(L, .14), "B"

# C · « Cinematic rise » — 80 BPM. Pizzicato strings = the counts; a string section swells under them,
# timpani on every new power of ten past 10^12, a full orchestral hit on the last number.
def mood_c():
    bpm = 80; L = np.zeros(int(DUR * SR)); tms = times(bpm); beat = 60 / bpm
    for i, (e, tm) in enumerate(zip(EV, tms)):
        f = mtof(pitch(e, 55)); put(L, tm, pluck(f, .9, seed=i), .45); put(L, tm, pluck(f / 2, .9, seed=50 + i), .2)
        if e >= 12:
            n = int(1.0 * SR); tt = np.arange(n) / SR
            put(L, tm, .28 * np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 5) + 62) / SR) * np.exp(-tt * 3.5))
    n = len(L); t = np.arange(n) / SR
    swell = saw_pad([mtof(m) for m in (43, 50, 55, 59, 62)], n, 900) * 0.6
    swell += saw_pad([mtof(m) for m in (67, 71, 74)], n, 2600) * np.clip((t - 3) / 4, 0, 1)
    L += .16 * swell * (0.2 + 0.8 * (t / DUR) ** 1.6)
    for b in np.arange(0, DUR, beat):                          # low ostinato
        nn = int(beat * SR); tt = np.arange(nn) / SR
        put(L, b, .07 * np.sign(np.sin(2 * np.pi * mtof(31) * tt)) * np.exp(-tt * 6))
    hit = tms[-1]
    for m in (31, 43, 55, 62, 67, 71, 74, 79):
        put(L, hit, pluck(mtof(m), 1.8, .998, seed=m), .22)
    noise(L, hit, 2.0, 5000, 1.8, .16, 77); kick(L, hit, .5, 38)
    return reverb(L, .45), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.6 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9)
    drive = {"A": 1.8, "B": 1.6, "C": 4.0}[name]                # soft limiter so quiet openings stay audible
    x = np.tanh(drive * x) / np.tanh(drive) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"count_mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events in excerpt:", [round(e, 1) for e in EV])
