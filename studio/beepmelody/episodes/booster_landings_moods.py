"""BeepMelody · Booster landings (Falcon only) · co-pilot step 2: three 8 s mood excerpts on the busiest passage.
Window = 1 Aug 2024 -> 31 Mar 2025 (243 days), the "drum roll" years, with the two real failures inside:
28 Aug 2024 (Starlink 8-6, a leg gives way: the 267-landing streak ends) and 3 Mar 2025 (Starlink 12-20, fire after touchdown).
Clock: date-linear, 1 day = 8/243 s. Landings in the window follow the REAL yearly counts of booster_landings_draft.csv
(2024: 132 attempts, 2025: 163), spread evenly inside each year: the exact landing-by-landing dates are compiled before the
final render (step 3). One landing = one audible hit; a crash = one wrong note + its own sound.
Usage: python3 booster_landings_moods.py <outdir>"""
import sys, os, csv, datetime as dt
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
D0, D1 = dt.date(2024, 8, 1), dt.date(2025, 3, 31)
NDAYS = (D1 - D0).days + 1
DAY = 8.0 / NDAYS
DUR = 8.0 + 0.4
OUT = sys.argv[1]

rows = list(csv.DictReader(open(os.path.join(HERE, "booster_landings_draft.csv"))))
attempts = {int(r["date"]): int(r["outcome"].split("/")[0].split()[1]) for r in rows if r["kind"] == "year"}
fails = [dt.date.fromisoformat(r["date"]) for r in rows if r["kind"] == "fail"]
EV = []                                    # (t, failed)
for y in (2024, 2025):
    start, n = dt.date(y, 1, 1), attempts[y]
    ylen = (dt.date(y + 1, 1, 1) - start).days
    for k in range(n):
        d = start + dt.timedelta(days=(k + .5) * ylen / n)
        if D0 <= d <= D1:
            EV.append([((d - D0).days) * DAY + .05, False])
for f in fails:                            # each real failure replaces the nearest evenly-spread attempt
    if D0 <= f <= D1:
        t = (f - D0).days * DAY + .05
        i = min(range(len(EV)), key=lambda j: abs(EV[j][0] - t) + (99 if EV[j][1] else 0))
        EV[i] = [t, True]
EV.sort()

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
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
        n = int(d * size * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)
def noise(dur, fc, dec, seed, hp=None):
    n = int(dur * SR); s = lowpass(np.random.RandomState(seed).randn(n), fc)
    if hp: s = highpass(s, hp)
    return s * np.exp(-np.arange(n) / SR * dec)
def kick(g=.26, f0=80, f1=46):
    n = int(.35 * SR); tt = np.arange(n) / SR
    return g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+f1)/SR) * np.exp(-tt*12)
def marimba(f, d=.25):
    n = int(1.0 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*30)) * env(n, .002, d)
def bell(f, d=.9, idx=1.6, ratio=3.5, dur=2.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt + idx*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt)) * env(n, .003, d)
def saw(f, dur, det=(.995, 1.0, 1.005)):
    n = int(dur * SR); tt = np.arange(n) / SR
    return sum(2 * ((f * d * tt) % 1) - 1 for d in det) / len(det)
def ping(f, d=.4):
    n = int(1.4 * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt) * env(n, .002, d)

SCALE = [0, 2, 4, 7, 9]                     # major pentatonic: landings climb a little phrase that loops
def deg(k, base, span=10):
    s = k % span; return base + 12 * (s // 5) + SCALE[s % 5]

# A · Clair et léger (comme « The Race to the Sky ») — 112 BPM, marimba = each landing, soft bell on every 10th,
# crash = a sour bell a semitone off + low wooden thud, the groove holds
def mood_a():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    beat = 60 / 112
    chords = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.10, 70, 44) if k % 2 == 0 else noise(.08, 5000, 30, k, 1500), 1 if k % 2 == 0 else .025)
        put(L, b + beat / 2, noise(.03, 9000, 140, 90 + k, 6000), .018)
        if k % 4 == 0:
            for m in chords[(k // 4) % 4]:
                n = int(beat * 4 * SR); tt = np.arange(n) / SR
                put(L, b, .010 * np.sin(2*np.pi*mtof(m)*tt) * np.minimum(1, tt / .3) * np.exp(-tt * .6))
    k = 0
    for tm, fail in EV:
        if fail:
            put(L, tm, .26 * bell(mtof(73), .7))           # C#: out of the C pentatonic
            put(L, tm, kick(.26, 55, 32)); put(L, tm, noise(.4, 1500, 8, 31, 100), .08)
        else:
            put(L, tm, .11 * marimba(mtof(deg(k, 72)), .2)); k += 1
            if k % 10 == 0: put(L, tm, .08 * bell(mtof(84), .5))
    return reverb(L, .3, 1.0), "A"

# B · Cadence de fusée — 128 BPM house, landings = a short "ba-boom" (the double sonic boom of a returning booster)
# pitched on the chord; crash = drums drop out for a bar + distorted buzz falling
def mood_b():
    L = np.zeros(int(DUR * SR)); beat = 60 / 128
    cut = [tm for tm, f in EV if f]
    def muted(x): return any(0 <= x - c < beat * 4 for c in cut)
    roots = [33, 33, 29, 31]
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if muted(b): continue
        put(L, b, kick(.24))
        if k % 2: put(L, b, noise(.15, 6000, 25, 40 + k, 900), .07)
        put(L, b + beat / 2, noise(.04, 9000, 120, 70 + k, 5000), .035)
        r = roots[(k // 8) % 4]; nn = int(beat * .45 * SR); tt = np.arange(nn) / SR
        put(L, b + beat / 2, .08 * lowpass(saw(mtof(r + 12), beat * .45), 700) * np.exp(-tt * 6))
    k = 0
    for tm, fail in EV:
        if fail:
            n = int(1.0 * SR); tt = np.arange(n) / SR
            f = mtof(63) * np.exp(-tt * 1.3)
            s = np.tanh(4 * (2 * ((np.cumsum(f) / SR) % 1) - 1))
            put(L, tm, .22 * lowpass(s, 2500) * env(n, .002, .5)); put(L, tm, noise(.6, 3000, 5, 911, 200), .09)
        else:
            f = mtof(deg(k, 57)); k += 1
            put(L, tm, kick(.07, f * 1.5, f * .5)); put(L, tm + .045, kick(.05, f * 1.5, f * .5))
            nn = int(.12 * SR); put(L, tm, .05 * lowpass(saw(f * 2, .12), 3000) * env(nn, .002, .05))
    return reverb(L, .15), "B"

# C · Ciel ouvert — airy, 90 BPM half-time, wide pad, glass pings (landings), crash = detuned ping sinking + soft thud
def mood_c():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    pad = np.zeros_like(L)
    for m in [48, 55, 60, 64, 67, 71]:
        for det in (.994, 1.0, 1.006): pad += np.sin(2*np.pi*mtof(m)*det*t)
    L += .008 * pad * np.minimum(1, t / 1.0)
    L += .05 * np.sin(2*np.pi*mtof(36)*t)
    beat = 60 / 90 * 2
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.11, 65, 40)); put(L, b + beat / 2, noise(.05, 7000, 60, k, 3000), .03)
    k = 0
    for tm, fail in EV:
        if fail:
            n = int(1.6 * SR); tt = np.arange(n) / SR
            f = mtof(80) * np.exp(-tt * .4)
            put(L, tm, .26 * np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, .003, .9)); put(L, tm, kick(.24, 55, 30))
        else:
            put(L, tm, .10 * ping(mtof(deg(k, 76)), .3)); k += 1
    return reverb(L, .5, 1.3), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("window", D0, "->", D1, ":", len(EV), "landing attempts,", sum(1 for e in EV if e[1]), "failures")
for tm, f in EV:
    if f: print("FAIL t=%.2f s" % tm)
