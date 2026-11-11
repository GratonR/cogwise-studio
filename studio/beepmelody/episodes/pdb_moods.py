"""BeepMelody · Protein Data Bank · co-pilot step 2: three 8 s mood excerpts on the take-off passage
(one note per year, 1987 -> 2001: 25 -> 2,811 structures released). Pitch = log(structures released that year).
Usage: python3 pdb_moods.py <pdb_proteins.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
OUT = sys.argv[2]
rows = [r for r in csv.DictReader(open(sys.argv[1])) if 1987 <= int(r["year"]) <= 2001]
EV = [(int(r["year"]), int(r["released"])) for r in rows]
LO, HI = np.log10(6), np.log10(17557)          # full-series range, so pitches match the final episode
def deg(v, steps): return int(round(np.clip((np.log10(v) - LO) / (HI - LO), 0, 1) * (steps - 1)))
def is_peak(e): return e[0] == 1994             # first year over 1,000

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lowpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += g * sig[:j - i]
def reverb(x, mix=.35):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
        n = int(d * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)
def times(bpm):  # 15 years over 0.2..7.2 s, on a 16th grid
    s16 = 60 / bpm / 4
    return [round((0.2 + i * 0.5) / s16) * s16 for i in range(len(EV))]
def kick(b, L, g=.26):
    n = int(.35 * SR); tt = np.arange(n) / SR
    put(L, b, g * np.sin(2*np.pi*np.cumsum(80*np.exp(-tt*16)+48)/SR) * np.exp(-tt*12))
def noise(L, b, dur, fc, dec, g, seed):
    n = int(dur * SR); put(L, b, g * lowpass(np.random.RandomState(seed).randn(n), fc) * np.exp(-np.arange(n)/SR*dec))

# A · Warm lab — 90 BPM, marimba data notes, kalimba sparkle on the 1,000 mark, shaker, round bass, Am7–Fmaj7–Cmaj7–G
def mood_a():
    bpm = 90; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat
    roots = [45, 41, 36, 43]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4])
        put(L, b, .15 * np.sin(2*np.pi*f*tt) * np.exp(-tt*1.3))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if k % 2 == 0: kick(b, L, .22)
        else: noise(L, b, .1, 4000, 30, .05, k)
        noise(L, b + beat/2, .05, 8000, 90, .025, 50+k)                # shaker
    scale = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88]   # A minor pentatonic
    for e, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(e[1], len(scale))]); n = int(1.2 * SR); tt = np.arange(n) / SR
        s = np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25)   # marimba
        put(L, tm, (.18 + (.08 if is_peak(e) else 0)) * s * env(n, .002, .4))
        if is_peak(e):
            for j, m in enumerate([0, 7, 12, 19]):
                fk = f * 2 ** (m / 12); s2 = np.sin(2*np.pi*fk*tt) + .3*np.sin(2*np.pi*fk*5.9*tt)*np.exp(-tt*20)
                put(L, tm + (j + 1) * beat / 4, .09 * s2 * env(n, .002, .5))
    return reverb(L, .22), "A"

# B · Under the microscope — 66 BPM, wide airy pad, glassy FM bells, low swell that grows with the data
def mood_b():
    bpm = 66; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; bar = 4 * 60 / bpm
    chords = [[38, 45, 50, 57, 62, 64], [41, 48, 53, 57, 60, 67]]   # Dsus–Fadd9
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * 1.3 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in chords[k % 2]:
            for det in (.995, 1.0, 1.006): s += np.sin(2*np.pi*mtof(m)*det*tt)
        put(L, b, .014 * s * np.minimum(1, tt / 1.5) * np.clip((bar*1.3 - tt) / .8, 0, 1))
    L += lowpass(np.random.RandomState(3).randn(len(L)), 1800) * (t / DUR) ** 2 * .03
    scale = [62, 64, 67, 69, 71, 74, 76, 79, 81, 83, 86, 88, 91, 93]   # D major pentatonic-ish
    for e, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(e[1], len(scale))]); n = int(2.5 * SR); tt = np.arange(n) / SR
        s = np.sin(2*np.pi*f*tt + 1.8*np.exp(-tt*4)*np.sin(2*np.pi*f*3.5*tt))   # glass bell (FM)
        put(L, tm, (.14 + (.08 if is_peak(e) else 0)) * s * env(n, .003, 1.0))
    return reverb(L, .55), "B"

# C · Cell machinery — 116 BPM, pizzicato strings + wood blocks, 16th pulse that gets denser with the count
def mood_c():
    bpm = 116; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; s16 = beat / 4; bar = 4 * beat
    roots = [40, 36, 43, 38]                                         # Em–C–G–D
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q in range(8):
            n = int(.25 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + (12 if q % 2 else 0))
            put(L, b + q * beat / 2, .10 * np.sign(np.sin(2*np.pi*f*tt)) * .5 * np.exp(-tt*10))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kick(b, L, .27)
        if k % 2: noise(L, b, .14, 3500, 22, .09, k)                   # snare-ish
    tms = times(bpm)
    for i, (e, tm) in enumerate(zip(EV, tms)):                          # wood-block pulse: density ~ log(count)
        nxt = tms[i + 1] if i + 1 < len(tms) else DUR - .3
        k16 = 1 + int(np.log10(e[1]))
        for j in range(int(round((nxt - tm) / s16))):
            if j % max(1, 5 - k16) == 0:
                n = int(.05 * SR); tt = np.arange(n) / SR
                put(L, tm + j * s16, .05 * np.sin(2*np.pi*1800*tt) * np.exp(-tt*120))
    scale = [52, 55, 57, 59, 62, 64, 67, 69, 71, 74, 76, 79, 81, 83]   # E minor pentatonic
    for e, tm in zip(EV, tms):
        f = mtof(scale[deg(e[1], len(scale))]); n = int(.8 * SR); tt = np.arange(n) / SR
        s = sum((1/h) * np.sin(2*np.pi*f*h*tt) * np.exp(-tt*(6 + 4*h)) for h in range(1, 6))   # pizzicato
        put(L, tm, (.22 + (.08 if is_peak(e) else 0)) * s * env(n, .002, .3))
        if is_peak(e): put(L, tm + beat/2, .14 * s * env(n, .002, .3))
    return reverb(L, .15), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events", EV[0], EV[-1])
