"""BeepMelody · Kyoto cherry blossoms · co-pilot step 2: three 8 s mood excerpts on the key passage
(decade means 1870s -> 2020s, then each spring 2021 -> 2026). Earlier bloom = higher note.
Usage: python3 kyoto_moods.py <kyoto.csv (year,bloom_date)> <outdir>"""
import sys, csv, os, datetime as dt
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
OUT = sys.argv[2]
rows = list(csv.DictReader(open(sys.argv[1])))

def doy(s):  # calendar day in a non-leap year (Apr 14 = 104)
    y, m, d = map(int, s.split("-")[:3]); return (dt.date(2001, m, d) - dt.date(2001, 1, 1)).days + 1

dec = {}
for r in rows: dec.setdefault(int(r["year"]) // 10 * 10, []).append(doy(r["bloom_date"]))
EV = [("dec", k, float(np.mean(dec[k]))) for k in range(1870, 2030, 10)]
EV += [("year", int(r["year"]), float(doy(r["bloom_date"]))) for r in rows if int(r["year"]) >= 2021]
LATE, EARLY = 108.0, 84.0
def deg(v, steps): return int(round(np.clip((LATE - v) / (LATE - EARLY), 0, 1) * (steps - 1)))

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec_):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec_)
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

def times(bpm):  # 16 decades over 0.2..5.6 s, then 6 springs faster over 5.9..7.4 s, on a 16th grid
    s16 = 60 / bpm / 4; res = []
    for i, e in enumerate(EV):
        t = 0.2 + i * (5.4 / 15) if i < 16 else 5.9 + (i - 16) * 0.3
        res.append(round(t / s16) * s16)
    return res

def is_record(e): return e[0] == "year" and e[1] in (2021, 2023)

# A · Koto garden — 72 BPM, Japanese "in" scale, plucked koto, soft taiko, bamboo flute drone
def mood_a():
    bpm = 72; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; beat = 60 / bpm
    fl = 0.035 * (np.sin(2*np.pi*mtof(57)*t + .3*np.sin(2*np.pi*5*t)) + .3*np.sin(2*np.pi*mtof(64)*t))
    L += lowpass(fl * np.minimum(1, t / 2), 1500)
    for k, b in enumerate(np.arange(0, DUR, beat * 2)):  # taiko on 1, light rim on 3
        n = int(.5 * SR); tt = np.arange(n) / SR
        put(L, b, .30 * np.sin(2*np.pi*np.cumsum(90*np.exp(-tt*10)+55)/SR) * np.exp(-tt*7))
        nn = int(.04 * SR); put(L, b + beat, .05 * lowpass(np.random.RandomState(k).randn(nn), 3000) * np.exp(-np.arange(nn)/SR*90))
    scale = [57, 58, 62, 64, 65, 69, 70, 74, 76, 77, 81, 82]  # A in-scale (A Bb D E F)
    for e, tm in zip(EV, times(bpm)):
        m = scale[deg(e[2], len(scale))]; f = mtof(m); n = int(1.8 * SR); tt = np.arange(n) / SR
        s = sum((1/h) * np.sin(2*np.pi*f*h*tt) * np.exp(-tt*(3 + 2.5*h)) for h in range(1, 7))  # koto pluck
        g = .16 + (.08 if is_record(e) else 0)
        put(L, tm, g * s * env(n, .002, 1.2))
        if is_record(e): put(L, tm + beat / 2, .10 * s * env(n, .002, 1.2))  # echo on records
    return reverb(L, .35), "A"

# B · Slow-build ambient — 60 BPM, warm pad that brightens over time, music-box notes, rising swell
def mood_b():
    bpm = 60; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; bar = 4 * 60 / bpm
    chords = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 64]]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * 1.3 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in chords[k % 2]:
            for det in (.996, 1.0, 1.005): s += np.sin(2*np.pi*mtof(m)*det*tt) + .3*np.sin(2*np.pi*mtof(m)*2*det*tt)
        e = np.minimum(1, tt / 1.2) * np.clip((bar * 1.3 - tt) / .8, 0, 1)
        put(L, b, .018 * s * e)
    sw = lowpass(np.random.RandomState(1).randn(len(L)), 2500) * (t / DUR) ** 2 * .035  # swell
    L += sw
    scale = [69, 72, 74, 76, 79, 81, 84, 86, 88, 91, 93]
    for e, tm in zip(EV, times(bpm)):
        m = scale[deg(e[2], len(scale))]; f = mtof(m); n = int(2.4 * SR); tt = np.arange(n) / SR
        s = np.sin(2*np.pi*f*tt) + .25*np.sin(2*np.pi*f*4.2*tt)*np.exp(-tt*9)  # music box
        put(L, tm, (.13 + (.07 if is_record(e) else 0)) * s * env(n, .002, .9))
    return reverb(L, .55), "B"

# C · Warm spring groove — 96 BPM, marimba + kalimba, soft brushed drums, round bass, Fmaj7–Em7–Dm7–Cmaj7
def mood_c():
    bpm = 96; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat
    roots = [41, 40, 38, 36]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4])
        put(L, b, .16 * np.sin(2*np.pi*f*tt) * np.exp(-tt*1.2)); put(L, b + 2.5*beat, .10 * np.sin(2*np.pi*f*tt[: n//2]) * np.exp(-tt[: n//2]*3))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        n = int(.35 * SR); tt = np.arange(n) / SR
        if k % 2 == 0: put(L, b, .26 * np.sin(2*np.pi*np.cumsum(80*np.exp(-tt*16)+48)/SR) * np.exp(-tt*12))
        else: nn = int(.12*SR); put(L, b, .05 * lowpass(np.random.RandomState(k).randn(nn), 5000) * np.exp(-np.arange(nn)/SR*25))
        nh = int(.03*SR); put(L, b + beat/2, .02 * np.random.RandomState(99+k).randn(nh) * np.exp(-np.arange(nh)/SR*150))
    scale = [60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84]
    for e, tm in zip(EV, times(bpm)):
        m = scale[deg(e[2], len(scale))]; f = mtof(m); n = int(1.2 * SR); tt = np.arange(n) / SR
        if e[0] == "dec":  # marimba
            s = np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25)
            put(L, tm, .17 * s * env(n, .002, .35))
        else:              # kalimba for single springs
            s = np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*f*5.9*tt)*np.exp(-tt*20)
            put(L, tm, (.17 + (.08 if is_record(e) else 0)) * s * env(n, .002, .6))
    return reverb(L, .2), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events")
