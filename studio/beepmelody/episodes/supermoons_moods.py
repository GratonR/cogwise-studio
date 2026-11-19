"""BeepMelody · Every supermoon since 1900 · co-pilot step 2: three 8 s mood excerpts on the densest passage.
Clock: 1 year = 0.45 s (127 years ~ 57 s of data). Supermoons (Espenak 90 % rule) come in packets every ~411.8 days
(full moon / perigee beat period); at this clock one packet = 0.507 s, so the backing tempo is LOCKED to the Moon:
118.3 BPM, one packet per beat. Each supermoon = one hit on its exact instant; pitch = distance (closer = higher).
Window: 1986.0 -> 2003.8 (17.8 years = 8 s), the densest stretch: 75 supermoons.
Usage: python3 supermoons_moods.py <supermoons_draft.csv> <outdir>"""
import sys, csv, os, datetime as dt
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
YEAR_S = 0.45
Y0, YEARS = 1986.0, 17.8
DUR = YEARS * YEAR_S + 0.5
BEAT = 411.78 / 365.25 * YEAR_S          # 0.5073 s -> 118.3 BPM
OUT = sys.argv[2]

def yfrac(s):
    t = dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
    return t.year + ((t - dt.datetime(t.year, 1, 1)).total_seconds() / 86400) / 365.25
EV = []
for r in csv.DictReader(open(sys.argv[1])):
    if r["espenak90"] != "1": continue
    y = yfrac(r["full_moon_utc"])
    if Y0 <= y < Y0 + YEARS:
        EV.append(((y - Y0) * YEAR_S + .1, float(r["dist_km"]), r["tad360"] == "1", r["close3568"] == "1", r["full_moon_utc"]))

# pitch: 362,500 km -> low, 356,400 km -> high, quantised to a scale
def pitch(dkm, base, scale):
    x = np.clip((362500 - dkm) / (362500 - 356400), 0, 1)
    k = int(round(x * (2 * len(scale) - 1)))
    return base + 12 * (k // len(scale)) + scale[k % len(scale)]
LYD = [0, 2, 4, 6, 7, 9, 11]
PENT = [0, 2, 4, 7, 9]

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
def celesta(f, d=.7):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*6) + .15*np.sin(2*np.pi*4.01*f*tt)*np.exp(-tt*12)) * env(n, .002, d)
def marimba(f):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25) + .1*np.sin(2*np.pi*f*10*tt)*np.exp(-tt*60)) * env(n, .001, .32)
def softsyn(f, d=.9):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*tt) for h in range(1, 6))
    return lowpass(s, 1200) * env(n, .02, d)
def pluck(f, dec=.3):
    n = int(.8 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
    return s * env(n, .002, dec)

# A · Nocturne lunaire — calm and airy: half-time (59 BPM) brushed pulse, wide Lydian pad, celesta notes
def mood_a():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    pad = np.zeros_like(L)
    for m in [50, 57, 62, 66, 69, 73]:
        for det in (.994, 1.0, 1.006): pad += np.sin(2*np.pi*mtof(m)*det*t)
    L += .009 * pad * np.minimum(1, t / 1.5)
    L += .05 * np.sin(2*np.pi*mtof(38)*t) * (.75 + .25*np.sin(2*np.pi*t/(BEAT*4)))
    for k, b in enumerate(np.arange(0, DUR, BEAT * 2)):
        put(L, b + .1, noise(.25, 5000, 10, 300 + k, 1500), .025)
    for tm, dkm, tad, close, _ in EV:
        put(L, tm, .16 * celesta(mtof(pitch(dkm, 74, LYD))))
        if close: put(L, tm, .10 * bell(mtof(pitch(dkm, 62, LYD)), 1.4))
    return reverb(L, .55, 1.5), "A"

# B · Marée (groove) — 118 BPM locked to the packet cycle: deep kick on each packet, offbeat hats, rolling sub;
# supermoons = bright plucks, the closest ones add a sub drop
def mood_b():
    L = np.zeros(int(DUR * SR)); s8 = BEAT / 2
    roots = [38, 38, 34, 36]
    for k, b in enumerate(np.arange(0, DUR, BEAT)):
        put(L, b + .1, kick(.22))
        put(L, b + .1 + s8, noise(.05, 9000, 90, 70 + k, 5000), .04)
        if k % 2: put(L, b + .1, noise(.15, 6000, 25, 40 + k, 900), .05)
        r = roots[(k // 4) % 4]; nn = int(s8 * .9 * SR); tt = np.arange(nn) / SR
        put(L, b + .1 + s8, .09 * lowpass(np.sin(2*np.pi*mtof(r)*tt) + .3*np.sign(np.sin(2*np.pi*mtof(r)*tt)), 500) * np.exp(-tt * 5))
    for tm, dkm, tad, close, _ in EV:
        put(L, tm, .15 * pluck(mtof(pitch(dkm, 69, PENT)), .25))
        if close:
            nn = int(.7 * SR); tt = np.arange(nn) / SR
            put(L, tm, .18 * np.sin(2*np.pi*np.cumsum(mtof(38)*(1 + .6*np.exp(-tt*9)))/SR) * np.exp(-tt * 3))
    return reverb(L, .2), "B"

# C · Famille Race to the Sky — bell / marimba / soft synth, clear and gentle. Bell = every supermoon (90 % rule),
# marimba joins when it is also under 360,000 km, soft synth when it is in the 'closest' list (<= 356,800 km)
def mood_c():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    pad = np.zeros_like(L)
    for m in [48, 55, 60, 64, 67]:
        for det in (.995, 1.0, 1.005): pad += np.sin(2*np.pi*mtof(m)*det*t)
    L += .008 * pad * np.minimum(1, t / 1.2)
    for k, b in enumerate(np.arange(0, DUR, BEAT)):
        put(L, b + .1, kick(.10, 70, 42))
        put(L, b + .1 + BEAT / 2, noise(.04, 8000, 100, 900 + k, 4000), .02)
    for tm, dkm, tad, close, _ in EV:
        put(L, tm, .14 * bell(mtof(pitch(dkm, 72, PENT)), .6))
        if tad: put(L, tm, .18 * marimba(mtof(pitch(dkm, 60, PENT))))
        if close: put(L, tm, .20 * softsyn(mtof(pitch(dkm, 48, PENT))))
    return reverb(L, .4, 1.2), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.6 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("tempo %.1f BPM" % (60 / BEAT), "window", Y0, "+", YEARS, "y ->", len(EV), "supermoons,",
      sum(e[2] for e in EV), "under 360k,", sum(e[3] for e in EV), "closest-list")
