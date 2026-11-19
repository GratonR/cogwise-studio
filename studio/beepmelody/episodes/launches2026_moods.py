"""BeepMelody · Every orbital launch of 2026 · co-pilot step 2: three 8 s mood excerpts on the densest passage.
Clock: 1 day = 0.1875 s (= one 8th note at 160 BPM), so every launch sits on its real day and the grid is the calendar.
Window = 16 Mar -> 27 Apr 2026 (42 days, 44 launches, 2 failures: Tianlong-3 on 3 Apr, New Glenn on 19 Apr).
Same-day launches are spread by a 1/32 note so each one stays audible. Pitch = launch country (one note per country).
A failure = a WRONG note (out of the chord) + its own sound.
Usage: python3 launches2026_moods.py <launches2026_research.csv> <outdir>"""
import sys, csv, os, datetime as dt
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DAY = 0.1875
D0 = dt.date(2026, 3, 16)
NDAYS = 42
DUR = NDAYS * DAY + 0.4          # 8.275 s
OUT = sys.argv[2]

rows = [r for r in csv.DictReader(open(sys.argv[1])) if not r["check"].startswith("EXCLUDE")]
EV = []
seen = {}
for r in rows:
    k = (dt.date.fromisoformat(r["date"]) - D0).days
    if 0 <= k < NDAYS:
        j = seen.get(k, 0); seen[k] = j + 1
        EV.append((k * DAY + j * DAY / 4 + 0.05, r["country"], r["outcome"] != "success", r))

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
def pluck(f, dec=.3):
    n = int(.8 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
    return s * env(n, .002, dec)
def saw(f, dur, det=(.995, 1.0, 1.005)):
    n = int(dur * SR); tt = np.arange(n) / SR
    return sum(2 * ((f * d * tt) % 1) - 1 for d in det) / len(det)
def ping(f, d=.5):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt) * env(n, .002, d)

# Country -> chord tone (A minor pentatonic family, US + China, the two big voices, sit in the middle)
DEG = {"US": 0, "CN": 2, "NZ": 4, "RU": -2, "EU": 3, "IN": 5, "JP": 6, "KR": 7}
PENT = [0, 3, 5, 7, 10]
def note(country, base):
    d = DEG.get(country, 1)
    return base + 12 * (d // 5) + PENT[d % 5]

# A · Néon orbital — airy, 80 BPM half-time, wide pad, glass bells; failure = detuned bell sliding down + low thud
def mood_a():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    pad = np.zeros_like(L)
    for m in [45, 52, 57, 60, 64, 67]:
        for det in (.994, 1.0, 1.006): pad += np.sin(2*np.pi*mtof(m)*det*t)
    L += .009 * pad * np.minimum(1, t / 1.2)
    L += .06 * np.sin(2*np.pi*mtof(33)*t)
    beat = DAY * 4                                            # 80 BPM half-time pulse
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.12, 70, 40) if k % 2 == 0 else noise(.05, 7000, 70, k, 3000), 1 if k % 2 == 0 else .03)
    for tm, c, fail, _ in EV:
        if fail:
            n = int(1.6 * SR); tt = np.arange(n) / SR
            f = mtof(note(c, 69) + 1) * np.exp(-tt * .35)       # a semitone off, then sinking
            put(L, tm, .30 * np.sin(2*np.pi*np.cumsum(f)/SR + 1.2*np.exp(-tt*3)*np.sin(2*np.pi*np.cumsum(f*3.5)/SR)) * env(n, .003, .9))
            put(L, tm, kick(.30, 60, 30))
        else:
            put(L, tm, .15 * bell(mtof(note(c, 69)), .55))
    return reverb(L, .5, 1.3), "A"

# B · Compte à rebours électro — 160 BPM, kick every 2 days, 8th hats, rolling bass; launches = bright plucks;
# failure = drums drop out for half a bar + distorted buzz falling
def mood_b():
    L = np.zeros(int(DUR * SR)); beat = DAY * 2
    cut = [tm for tm, c, f, _ in EV if f]
    def muted(x): return any(0 <= x - c < beat * 2 for c in cut)
    roots = [33, 33, 29, 31]
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if muted(b): continue
        put(L, b, kick(.22))
        if k % 2: put(L, b, noise(.16, 6000, 25, 40 + k, 800), .07)
        for q in range(2): put(L, b + q * DAY, noise(.04, 9000, 120, 70 + 2*k + q, 5000), .03 if q else .015)
        r = roots[(k // 8) % 4]; nn = int(DAY * .9 * SR); tt = np.arange(nn) / SR
        put(L, b + DAY, .07 * lowpass(saw(mtof(r + 12), DAY * .9), 800) * np.exp(-tt * 8))
    for tm, c, fail, _ in EV:
        if fail:
            n = int(1.0 * SR); tt = np.arange(n) / SR
            f = mtof(note(c, 57) + 6) * np.exp(-tt * 1.2)       # tritone, then a dive
            s = np.tanh(4 * (2 * ((np.cumsum(f) / SR) % 1) - 1))
            put(L, tm, .20 * lowpass(s, 2500) * env(n, .002, .5))
            put(L, tm, noise(.6, 3000, 5, 911, 200), .08)
        else:
            put(L, tm, .15 * pluck(mtof(note(c, 69)), .22))
    return reverb(L, .16), "B"

# C · Salle de contrôle — tense, 80 BPM, low drone + heartbeat sub; launches = sonar/radio pings;
# failure = two-tone alarm + static burst
def mood_c():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    L += .05 * (np.sin(2*np.pi*mtof(28)*t) + .5*np.sin(2*np.pi*mtof(35)*t)) * (.7 + .3*np.sin(2*np.pi*t/3))
    L += highpass(lowpass(np.random.RandomState(5).randn(len(L)), 2500), 600) * .006
    beat = DAY * 4
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.16, 55, 38)); put(L, b + DAY, kick(.08, 55, 38))
        put(L, b + DAY * 2, noise(.02, 9000, 200, 500 + k, 4000), .03)
    for tm, c, fail, _ in EV:
        if fail:
            for q in range(4):
                put(L, tm + q * .16, .10 * np.sign(np.sin(2*np.pi*(mtof(76) if q % 2 == 0 else mtof(71))*np.arange(int(.15*SR))/SR)) * env(int(.15*SR), .003, .2))
            put(L, tm, noise(.5, 5000, 6, 77, 800), .10)
        else:
            put(L, tm, .17 * ping(mtof(note(c, 72)), .35))
            put(L, tm, noise(.03, 6000, 150, int(tm * 1000), 2000), .04)
    return reverb(L, .4, 1.5), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("window", D0, "+", NDAYS, "days ->", len(EV), "launches,", sum(1 for e in EV if e[2]), "failures")
for tm, c, f, r in EV:
    if f: print("FAIL", r["date"], r["vehicle"], "t=%.2f s" % tm)
