"""BeepMelody · Ebola · co-pilot step 2: three 8 s mood excerpts on the busiest passage (2012 -> 2026).
One outbreak = one hit, pitch = log(cases), species = timbre. Usage: python3 ebola_moods.py <csv> <outdir>"""
import sys, csv, math, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
rows = list(csv.DictReader(open(sys.argv[1])))
OUT = sys.argv[2]
ev = [r for r in rows if int(r["year"]) >= 2012]

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def T(d): return np.arange(int(d * SR)) / SR
def env(n, a, dec):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
    return e
def lowpass(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2)); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if i < len(buf): buf[i:j] += g * sig[:j - i]
def reverb(x, mix=0.35, fb=0.6):
    # cheap: sum of decaying echoes (multi-tap)
    out = x.copy()
    for k, (d, g) in enumerate([(0.083, .5), (0.127, .42), (0.191, .35), (0.263, .28), (0.347, .22), (0.461, .16), (0.613, .11), (0.83, .07)]):
        n = int(d * SR); out[n:] += g * fb * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 3500)

# --- timeline: years 2012..2026.9 spread over 0.25..7.4 s, same-year events spaced on a 16th grid
def times(bpm):
    s16 = 60 / bpm / 4
    by = {}
    res = []
    for r in ev:
        y = int(r["year"]); k = by.get(y, 0); by[y] = k + 1
        t = 0.25 + (y - 2012) / (2026 - 2012) * 6.6 + k * s16
        t = round(t / s16) * s16
        res.append(t)
    return res

LO, HI = math.log10(1), math.log10(30000)
def deg(cases, steps):  # 0..steps-1
    return int(round((math.log10(max(1, int(cases))) - LO) / (HI - LO) * (steps - 1)))

SPECIES = ["Zaire", "Sudan", "Bundibugyo", "Taï Forest"]

# ---------- A: dark & slow — 64 BPM, D minor drone, muted bell, low heartbeat
def mood_a():
    bpm = 64; L = np.zeros(int(DUR * SR))
    t = T(DUR)
    drone = 0.06 * (np.sin(2 * np.pi * mtof(38) * t) + 0.5 * np.sin(2 * np.pi * mtof(45) * t + 1) + 0.3 * np.sin(2 * np.pi * mtof(38) * 1.003 * t))
    drone *= np.minimum(1, t / 1.5) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.15 * t))
    L += lowpass(drone, 600)
    beat = 60 / bpm
    for b in np.arange(0, DUR, beat):  # heartbeat: lub-dub
        for off, g in ((0, .35), (0.22, .22)):
            n = int(0.25 * SR); tt = np.arange(n) / SR
            f = 55 * np.exp(-tt * 9) + 38
            put(L, b + off, g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14))
    scale = [50, 53, 55, 57, 60, 62, 65, 67, 69, 72, 74, 77]  # D minor pentatonic-ish
    for r, tm in zip(ev, times(bpm)):
        m = scale[deg(r["cases"], len(scale))]; sp = r["species"]
        n = int(2.2 * SR); tt = np.arange(n) / SR; f = mtof(m)
        if sp == "Zaire":      # muted bell
            s = np.sin(2*np.pi*f*tt) + .4*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*6) + .2*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*12)
        elif sp == "Sudan":    # low hollow tone
            s = np.sin(2*np.pi*f/2*tt) + .5*np.sin(2*np.pi*f*tt)
        else:                  # Bundibugyo / Taï: glassy
            s = np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*f*3*tt)*np.exp(-tt*8)
        g = 0.10 + 0.10 * deg(r["cases"], 10) / 9
        put(L, tm, g * s * env(n, .004, .7))
    return reverb(L, .45), "A"

# ---------- B: pulsing tension — 92 BPM, 8th-note low ostinato + ticking, plucked hits
def mood_b():
    bpm = 92; L = np.zeros(int(DUR * SR)); s8 = 60 / bpm / 2
    pat = [38, 38, 41, 38, 36, 38, 43, 41]
    for k, b in enumerate(np.arange(0, DUR, s8)):
        n = int(s8 * .95 * SR); tt = np.arange(n) / SR; f = mtof(pat[k % 8])
        saw = 2 * ((f * tt) % 1) - 1
        put(L, b, 0.09 * lowpass(saw, 700) * env(n, .005, .18))
        nn = int(.03 * SR)  # tick
        put(L, b, (0.05 if k % 2 else 0.08) * lowpass(np.random.RandomState(k).randn(nn), 6000) * np.exp(-np.arange(nn) / SR * 160))
    for k, b in enumerate(np.arange(0, DUR, 60 / bpm * 2)):  # low thud every 2 beats
        n = int(.3 * SR); tt = np.arange(n) / SR
        put(L, b, .32 * np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 12) + 40) / SR) * np.exp(-tt * 10))
    scale = [62, 65, 67, 69, 72, 74, 77, 79, 81, 84]
    for r, tm in zip(ev, times(bpm)):
        m = scale[deg(r["cases"], len(scale))]; f = mtof(m); sp = r["species"]
        n = int(1.0 * SR); tt = np.arange(n) / SR
        duty = {"Zaire": .5, "Sudan": .25}.get(sp, .125)
        sq = np.where((f * tt) % 1 < duty, 1.0, -1.0)
        s = lowpass(sq, 2400) * env(n, .002, .22)
        put(L, tm, (0.07 + 0.06 * deg(r["cases"], 10) / 9) * s)
    return reverb(L, .25), "B"

# ---------- C: airy requiem — 70 BPM, choir-like pad Dm - Bb - F - C, celesta hits
def mood_c():
    bpm = 70; L = np.zeros(int(DUR * SR)); t = T(DUR); bar = 60 / bpm * 2
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [41, 48, 53, 57], [48, 55, 60, 64]]
    pad = np.zeros_like(t)
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * 1.3 * SR); tt = np.arange(n) / SR
        s = np.zeros(n)
        for m in chords[k % 4]:
            for det in (0.997, 1.0, 1.004):
                f = mtof(m) * det; s += (2 * ((f * tt + det) % 1) - 1)
        e = np.minimum(1, tt / 0.6) * np.minimum(1, np.maximum(0, (bar * 1.3 - tt) / 0.5))
        put(pad, b, 0.012 * lowpass(s, 1100) * e)
    L += pad
    scale = [69, 72, 74, 77, 79, 81, 84, 86, 89, 91]
    for r, tm in zip(ev, times(bpm)):
        m = scale[deg(r["cases"], len(scale))]; f = mtof(m); sp = r["species"]
        n = int(2.5 * SR); tt = np.arange(n) / SR
        ratio = {"Zaire": 4.0, "Sudan": 3.0}.get(sp, 2.0)
        s = np.sin(2 * np.pi * f * tt + 1.2 * np.exp(-tt * 5) * np.sin(2 * np.pi * f * ratio * tt))
        put(L, tm, (0.08 + 0.07 * deg(r["cases"], 10) / 9) * s * env(n, .003, .9))
    return reverb(L, .55), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(ev), "events")
