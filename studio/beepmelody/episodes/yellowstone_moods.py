"""BeepMelody · Yellowstone wolves · co-pilot step 2: three 8 s mood excerpts on the busiest passage
(1995 -> 2008: the climb 21 -> 174, the 2005 crash, the 2007 rebound, the 2008 crash).
One year = one note (pitch = wolves counted), packs = soft accompanying plucks (one per pack, capped),
a big drop (>= 25 %) = a low hit. Usage: python3 yellowstone_moods.py <yellowstone_wolves_draft.csv> <outdir>"""
import sys, csv, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
OUT = sys.argv[2]
rows = [r for r in csv.DictReader(open(sys.argv[1])) if 1995 <= int(r["year"]) <= 2008]

def npacks(s):
    try: return int(str(s).split("-")[0].split("+")[0])
    except ValueError: return 0
EV = []
prev = None
for r in rows:
    w = int(r["wolves"]); p = npacks(r["packs"])
    EV.append(dict(year=int(r["year"]), wolves=w, packs=p, crash=prev is not None and w <= prev * 0.75,
                   record=w == max(int(x["wolves"]) for x in rows)))
    prev = w
LO, HI = math.log(20), math.log(180)
def deg(w, steps): return int(round(np.clip((math.log(w) - LO) / (HI - LO), 0, 1) * (steps - 1)))

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lowpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def bandpass(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += g * sig[:j - i]
def reverb(x, mix=.35):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
        n = int(d * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)

def times(bpm):  # 14 years over 0.25..7.0 s, snapped to an 8th grid
    s8 = 60 / bpm / 2
    return [round((0.25 + i * (6.75 / (len(EV) - 1))) / s8) * s8 for i in range(len(EV))]

def howl(f0, dur=1.6):  # sine voice gliding up then down, breathy formant
    n = int(dur * SR); tt = np.arange(n) / SR
    glide = f0 * (1 + .5 * np.sin(np.pi * np.clip(tt / dur, 0, 1)) ** 1.5) * (1 + .012 * np.sin(2 * np.pi * 5.5 * tt))
    ph = 2 * np.pi * np.cumsum(glide) / SR
    s = np.sin(ph) + .25 * np.sin(2 * ph) + .08 * bandpass(np.random.RandomState(3).randn(n), 600, 2400)
    return s * np.minimum(1, tt / .25) * np.clip((dur - tt) / .5, 0, 1)

def low_hit(n=.9, f=48):
    nn = int(n * SR); tt = np.arange(nn) / SR
    return np.sin(2 * np.pi * np.cumsum(f * 1.8 * np.exp(-tt * 8) + f) / SR) * np.exp(-tt * 4)

def pack_plucks(L, tm, e, scale, gain, step, timbre):
    for k in range(min(e["packs"], 8)):
        m = scale[k % len(scale)]; f = mtof(m); n = int(.5 * SR); tt = np.arange(n) / SR
        put(L, tm + step * (k + 1), gain * timbre(f, tt) * env(n, .002, .18))

# A · Night valley — 66 BPM, dark and sparse: low string drone, muted bell per year, a howl on the 2003 record,
#     deep hits on the crashes, faint pack plucks
def mood_a():
    bpm = 66; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    dr = sum(np.sin(2 * np.pi * mtof(m) * d * t) for m in (38, 45, 50) for d in (.997, 1.003))
    L += .030 * lowpass(dr + .4 * np.sign(np.sin(2 * np.pi * mtof(38) * t)), 500) * np.minimum(1, t / 1.5)
    L += .010 * lowpass(np.random.RandomState(7).randn(len(L)), 800)  # wind
    scale = [50, 53, 55, 57, 60, 62, 65, 67, 69, 72, 74]  # D minor pentatonic
    for e, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(e["wolves"], len(scale))]); n = int(2.2 * SR); tt = np.arange(n) / SR
        bell = np.sin(2 * np.pi * f * tt) + .45 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 6) + .2 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 12)
        put(L, tm, .15 * lowpass(bell, 2500) * env(n, .003, .9))
        pack_plucks(L, tm, e, [62, 65, 69, 72], .025, .045, lambda f, tt: np.sin(2 * np.pi * f * tt))
        if e["crash"]: put(L, tm, .32 * low_hit())
        if e["record"]: put(L, tm + .1, .11 * howl(mtof(64)))
    return reverb(L, .5), "A"

# B · Living valley — 92 BPM, warm and organic: marimba per year, kalimba plucks = packs, brushed drums, round bass
def mood_b():
    bpm = 92; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat
    roots = [41, 43, 38, 36]  # F – G – Dm – C
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4])
        put(L, b, .15 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 1.2)); put(L, b + 2.5 * beat, .09 * np.sin(2 * np.pi * f * tt[: n // 2]) * np.exp(-tt[: n // 2] * 3))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        n = int(.35 * SR); tt = np.arange(n) / SR
        if k % 2 == 0: put(L, b, .24 * np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 16) + 48) / SR) * np.exp(-tt * 12))
        else:
            nn = int(.14 * SR); put(L, b, .05 * lowpass(np.random.RandomState(k).randn(nn), 5000) * np.exp(-np.arange(nn) / SR * 22))
        nh = int(.03 * SR); put(L, b + beat / 2, .018 * np.random.RandomState(99 + k).randn(nh) * np.exp(-np.arange(nh) / SR * 150))
    scale = [60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84]
    for e, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(e["wolves"], len(scale))]); n = int(1.2 * SR); tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt * 25)
        put(L, tm, (.18 + (.06 if e["record"] else 0)) * s * env(n, .002, .4))
        pack_plucks(L, tm, e, [72, 76, 79, 84], .035, 60 / bpm / 4 / 2,
                    lambda f, tt: np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 5.9 * tt) * np.exp(-tt * 20))
        if e["crash"]: put(L, tm, .22 * low_hit(.6, 55))
    return reverb(L, .22), "B"

# C · Wild return — 112 BPM, driving frame drum and toms, plucked harp arpeggio = packs, airy pad, howl at the record
def mood_c():
    bpm = 112; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; beat = 60 / bpm
    pad = sum(np.sin(2 * np.pi * mtof(m) * d * t) for m in (57, 64, 69, 72) for d in (.995, 1.005))
    L += .012 * lowpass(pad, 1800) * np.minimum(1, t / 2) * (.6 + .4 * t / DUR)
    for k, b in enumerate(np.arange(0, DUR, beat / 2)):
        n = int(.3 * SR); tt = np.arange(n) / SR
        if k % 4 == 0: put(L, b, .28 * np.sin(2 * np.pi * np.cumsum(110 * np.exp(-tt * 18) + 70) / SR) * np.exp(-tt * 10))
        elif k % 4 == 3: put(L, b, .12 * np.sin(2 * np.pi * np.cumsum(60 * np.exp(-tt * 14) + 140) / SR) * np.exp(-tt * 14))
        else:
            nn = int(.05 * SR); put(L, b, .035 * bandpass(np.random.RandomState(k).randn(nn), 1500, 6000) * np.exp(-np.arange(nn) / SR * 60))
    scale = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]  # A minor pentatonic
    for e, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(e["wolves"], len(scale))]); n = int(1.4 * SR); tt = np.arange(n) / SR
        s = sum((1 / h) * np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (2.5 + 2 * h)) for h in range(1, 6))  # nylon pluck
        put(L, tm, (.2 + (.06 if e["record"] else 0)) * s * env(n, .002, .8))
        pack_plucks(L, tm, e, [69, 72, 76, 81], .03, 60 / bpm / 4 / 2,
                    lambda f, tt: sum((1 / h) * np.sin(2 * np.pi * f * h * tt) for h in (1, 2, 3)))
        if e["crash"]: put(L, tm, .3 * low_hit(.7, 50))
        if e["record"]: put(L, tm + .05, .10 * howl(mtof(69), 1.4))
    return reverb(L, .3), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events;", "crashes:", [e["year"] for e in EV if e["crash"]], "record:", [e["year"] for e in EV if e["record"]])
