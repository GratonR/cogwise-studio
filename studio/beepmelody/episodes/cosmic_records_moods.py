"""BeepMelody · cosmic-timeline (rework: farthest-object records 1914 -> 2025) · co-pilot step 2 (r2): three 8 s mood excerpts
on the densest passage of the data: 1997 -> 2009, 10 records in 12 years (CL 1358+62 arc z=4.92 ... GRB 090423 z=8.2).
One record = one note, placed at its real date (year + month) on a linear clock (~0.6 s per year), snapped to a 16th grid.
Pitch = log10(1+z) on a 25-step pentatonic (5 octaves) over the FULL series (M104 z=0.003 -> MoM-z14 z=14.44), i.e. how stretched the light is.
Usage: python3 cosmic_records_moods.py cosmic_records.csv <outdir>"""
import sys, csv, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
OUT = sys.argv[2]
ALL = list(csv.DictReader(open(sys.argv[1])))
LZ = [math.log10(1 + float(r["z"])) for r in ALL]
LO, HI = min(LZ), max(LZ)
def yr(r): return int(r["year"]) + ((int(r["month"]) - 0.5) / 12 if r["month"] else 0.5)
EV = [r for r in ALL if 1997 <= int(r["year"]) <= 2009]
def deg(r, steps):
    v = (math.log10(1 + float(r["z"])) - LO) / (HI - LO); return int(round(np.clip(v, 0, 1) * (steps - 1)))
MINP, MAJP = [0, 3, 5, 7, 10], [0, 2, 4, 7, 9]
def PENT(root, ints): return [root + 12 * o + i for o in range(5) for i in ints]   # 25 steps, 5 octaves
def is_hook(r): return r["object"].startswith("GRB")
def is_end(r): return r is EV[-1]
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lowpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += g * sig[:j - i]
def reverb(x, mix=.35, size=1.0):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
        n = int(d * size * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)
def times(bpm):
    s16 = 60 / bpm / 4; y0, y1 = yr(EV[0]), yr(EV[-1]); out, last = [], -1
    for r in EV:
        g = max(last + 1, round((0.35 + (yr(r) - y0) / (y1 - y0) * 6.3) / s16)); out.append(g * s16); last = g
    return out
def kick(b, L, g=.26, f0=80):
    n = int(.35 * SR); tt = np.arange(n) / SR
    put(L, b, g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+46)/SR) * np.exp(-tt*12))
def noise(L, b, dur, fc, dec, g, seed):
    n = int(dur * SR); put(L, b, g * lowpass(np.random.RandomState(seed).randn(n), fc) * np.exp(-np.arange(n)/SR*dec))
def arp(L, f, t0, step, voice, g):
    for j, m in enumerate([0, 7, 12, 19]): put(L, t0 + (j + 1) * step, g * voice(f * 2 ** (m / 12)))


# A · Cosmic drive+ — the v1 mood Guillaume chose, faster: 124 BPM, 16th saw-bass arpeggio, four-on-the-floor, bright pluck (Am-F-C-G)
def mood_a():
    bpm = 124; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; s16 = beat / 4; bar = 4 * beat
    roots = [33, 29, 36, 31]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q in range(16):
            n = int(s16 * .9 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + [0, 12, 7, 12][q % 4])
            put(L, b + q * s16, .07 * lowpass(2 * ((f * tt) % 1) - 1, 900 + 600 * (b / DUR)) * np.exp(-tt * 9))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kick(b, L, .26)
        if k % 2: noise(L, b, .16, 5000, 18, .06, k)
        noise(L, b + beat / 2, .04, 9000, 120, .03, 70 + k)
    scale = PENT(33, MINP)
    def pluck(f):
        n = int(.9 * SR); tt = np.arange(n) / SR
        return sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7)) * env(n, .002, .35)
    for r, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(r, len(scale))])
        put(L, tm, (.20 + (.08 if is_hook(r) else 0)) * pluck(f)); put(L, tm + 3 * s16, .06 * pluck(f))
        if is_end(r): arp(L, f, tm, s16, pluck, .11)
    return reverb(L, .22), "A"

# B · Observatory — 90 BPM half-time, wide airy pad (Dmaj9 - Bm9), ticking hats, glass FM bells with long tails, sub swell
def mood_b():
    bpm = 90; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; beat = 60 / bpm; bar = 4 * beat
    chords = [[38, 50, 54, 57, 61, 64], [35, 50, 54, 57, 61, 62]]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * 1.3 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in chords[k % 2]:
            for det in (.995, 1.0, 1.006): s += np.sin(2*np.pi*mtof(m)*det*tt)
        put(L, b, .012 * s * np.minimum(1, tt / 1.2) * np.clip((bar*1.3 - tt) / .8, 0, 1))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if k % 4 == 0: kick(b, L, .2, 60)
        if k % 4 == 2: noise(L, b, .25, 4000, 10, .05, k)
        for q in range(4): noise(L, b + q * beat / 4, .03, 10000, 160, .018 * (1.4 if q == 2 else 1), 90 + 4*k + q)
    L += .07 * np.sin(2*np.pi*mtof(26)*t) * (t / DUR) ** 2
    scale = PENT(38, MAJP)
    def bell(f, d=1.0):
        n = int(2.4 * SR); tt = np.arange(n) / SR
        return np.sin(2*np.pi*f*tt + 1.5*np.exp(-tt*4)*np.sin(2*np.pi*f*3.5*tt)) * env(n, .003, d)
    for r, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(r, len(scale))])
        put(L, tm, (.16 + (.08 if is_hook(r) else 0)) * bell(f))
        if is_end(r): arp(L, f, tm, beat / 2, lambda x: bell(x, .8), .08)
    return reverb(L, .5, 1.3), "B"

# C · Radio hunt — 128 BPM, dark techno: sonar ping on every record, rolling 16th bass (Em), claps, open hats
def mood_c():
    bpm = 128; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; s16 = beat / 4
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kick(b, L, .3, 70)
        if k % 2: noise(L, b, .12, 2500, 30, .09, k)                      # clap
        noise(L, b + beat / 2, .12, 8000, 25, .035, 30 + k)                # open hat
        for q in (1, 2, 3):
            n = int(s16 * .8 * SR); tt = np.arange(n) / SR; f = mtof(28 + (7 if q == 3 else 0))
            put(L, b + q * s16, .09 * lowpass(np.sign(np.sin(2*np.pi*f*tt)), 500) * np.exp(-tt * 14))
    scale = PENT(40, MINP)
    def ping(f):
        n = int(1.2 * SR); tt = np.arange(n) / SR
        return (np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*f*2.01*tt)) * env(n, .001, .25)
    for r, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(r, len(scale))])
        put(L, tm, (.17 + (.08 if is_hook(r) else 0)) * ping(f))
        for e in (1, 2): put(L, tm + e * 3 * s16, .07 / e * ping(f))
        if is_end(r): arp(L, f, tm, s16, ping, .1)
    return reverb(L, .28, 1.1), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.6 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events:", EV[0]["object"], "->", EV[-1]["object"])
print("times@124:", [round(x, 2) for x in times(124)])
print("degrees:", [deg(r, 25) for r in EV])
