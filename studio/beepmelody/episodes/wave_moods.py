"""BeepMelody · Wave spectrum · co-pilot step 2: three 8 s mood excerpts on the densest passage
(1960 laser -> 2023 nanohertz background: 13 discoveries packed together, then the climax).
One discovery = one note. Pitch = log10(frequency) of the wave, squeezed from 147 octaves into ~2.5 octaves
(low wave = low note). Each family has its own voice (light / sound / gravity), like the three lanes of the altitude pilot.
The 2015 LIGO event is the one note played at its REAL pitch: an audible 35 -> 250 Hz chirp.
Usage: python3 wave_moods.py <wave_spectrum_draft.csv> <outdir>"""
import sys, csv, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
OUT = sys.argv[2]
ALL = list(csv.DictReader(open(sys.argv[1])))
EV = [r for r in ALL if int(r["year"]) >= 1960]
LO, HI = -15.0, 29.6                                      # log10 Hz of the whole series
def pos(r): return (math.log10(float(r["freq_hz"])) - LO) / (HI - LO)
def deg(r, steps): return int(round(np.clip(pos(r), 0, 1) * (steps - 1)))
fam = lambda r: r["family"]
is_ligo = lambda r: r["family"] == "gravity" and r["year"] == "2015"
is_end = lambda r: r is EV[-1]

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
    s16 = 60 / bpm / 4; n = len(EV)
    w = np.array([0.9 ** i for i in range(n - 1)]); cum = np.concatenate([[0], np.cumsum(w)]) / w.sum()
    out, last = [], -1
    for c in cum:
        g = max(last + 1, round((0.3 + c * 6.3) / s16)); out.append(g * s16); last = g
    return out
def kick(b, L, g=.26, f0=80):
    n = int(.35 * SR); tt = np.arange(n) / SR
    put(L, b, g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+46)/SR) * np.exp(-tt*12))
def noise(L, b, dur, fc, dec, g, seed):
    n = int(dur * SR); put(L, b, g * lowpass(np.random.RandomState(seed).randn(n), fc) * np.exp(-np.arange(n)/SR*dec))
def chirp(g=.22, f0=35, f1=250, d=0.6):
    """LIGO GW150914 at real pitch: frequency sweeps up fast at the end (f ~ (tc - t)^-3/8)."""
    n = int((d + .25) * SR); tt = np.arange(n) / SR; tc = d + .002
    f = np.where(tt < d, f0 * ((tc) / np.maximum(tc - tt, 1e-3)) ** (3 / 8), f1)
    f = np.clip(f, f0, f1)
    a = np.where(tt < d, (f / f1) ** .7, np.exp(-(tt - d) * 30))
    return g * np.sin(2 * np.pi * np.cumsum(f) / SR) * a
def arp(L, f, t0, step, voice, g):
    for j, m in enumerate([0, 7, 12, 19]): put(L, t0 + (j + 1) * step, g * voice(f * 2 ** (m / 12)))
def bell(f, d=1.2, idx=1.6):
    n = int(2.6 * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt + idx*np.exp(-tt*4)*np.sin(2*np.pi*f*3.5*tt)) * env(n, .003, d)
def marimba(f):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*3.93*tt)*np.exp(-tt*25)) * env(n, .002, .35)
def softsyn(f):
    n = int(1.4 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*tt) for h in (1, 2, 3))
    return lowpass(s, 2200) * env(n, .03, .5)
def pluck(f):
    n = int(.9 * SR); tt = np.arange(n) / SR
    return sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7)) * env(n, .002, .35)
def bowed(f):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*tt + .3*np.sin(2*np.pi*5*tt)) for h in range(1, 6))
    return lowpass(s, 1500) * np.minimum(1, tt / .12) * np.exp(-tt * 1.8)

def play(L, bpm, scale, voices, gains, s16echo=None):
    for r, tm in zip(EV, times(bpm)):
        if is_ligo(r):
            put(L, tm, chirp()); continue
        f = mtof(scale[deg(r, len(scale))])
        put(L, tm, gains[fam(r)] * (1.3 if is_end(r) else 1) * voices[fam(r)](f))
        if s16echo: put(L, tm + s16echo, .3 * gains[fam(r)] * voices[fam(r)](f))
        if is_end(r): arp(L, f, tm, 60 / bpm / 2, voices["light"], .08)

# A · Deep spectrum — 66 BPM, wide pad Dsus2 -> Bbmaj7, glass bells (light), bowed low string (sound), sine sub swell
def mood_a():
    bpm = 66; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; bar = 4 * 60 / bpm
    chords = [[38, 45, 50, 52, 57, 64], [34, 41, 46, 50, 57, 62]]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * 1.35 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in chords[k % 2]:
            for det in (.994, 1.0, 1.007): s += np.sin(2*np.pi*mtof(m)*det*tt)
        put(L, b, .013 * s * np.minimum(1, tt / 1.8) * np.clip((bar*1.35 - tt) / .9, 0, 1))
    L += .10 * np.sin(2*np.pi*mtof(26)*t) * (t / DUR) ** 2
    scale = [45, 47, 50, 52, 54, 57, 59, 62, 64, 66, 69, 71, 74, 76, 78]
    play(L, bpm, scale, {"light": bell, "sound": bowed, "gravity": lambda f: bell(f / 2, 2, .6)},
         {"light": .15, "sound": .12, "gravity": .15})
    return reverb(L, .55, 1.4), "A"

# B · Discovery drive — 118 BPM, 16th synth-bass arpeggio, four-on-the-floor, plucks (light), marimba (sound)
def mood_b():
    bpm = 118; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; s16 = beat / 4; bar = 4 * beat
    roots = [33, 29, 36, 31]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q in range(16):
            n = int(s16 * .9 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + [0, 12, 7, 12][q % 4])
            put(L, b + q * s16, .07 * lowpass(2 * ((f * tt) % 1) - 1, 900 + 600 * (b / DUR)) * np.exp(-tt * 9))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kick(b, L, .26)
        if k % 2: noise(L, b, .16, 5000, 18, .06, k)
        noise(L, b + beat / 2, .04, 9000, 120, .03, 70 + k)
    scale = [45, 48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79]
    play(L, bpm, scale, {"light": pluck, "sound": marimba, "gravity": softsyn},
         {"light": .20, "sound": .22, "gravity": .18}, s16echo=3 * s16)
    return reverb(L, .22), "B"

# C · Lab music box — 96 BPM, family of the altitude pilot: bell (light), marimba (sound), soft synth (gravity),
#     soft pad Fmaj7 - G - Em7 - Am + brushed drums, light and clear
def mood_c():
    bpm = 96; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat
    chords = [[41, 53, 57, 60, 64], [43, 55, 59, 62], [40, 52, 55, 59, 62], [45, 57, 60, 64]]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in chords[k % 4]: s += np.sin(2*np.pi*mtof(m)*tt) + .3*np.sin(2*np.pi*mtof(m)*2.003*tt)
        put(L, b, .018 * lowpass(s, 1800) * np.minimum(1, tt / .3) * np.clip((bar - tt) / .3, 0, 1))
        put(L, b, .12 * np.sin(2*np.pi*mtof(chords[k % 4][0] - 12)*tt) * np.exp(-tt * 1.2))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if k % 2 == 0: kick(b, L, .18, 70)
        else: noise(L, b, .18, 3000, 14, .05, k)
        noise(L, b + beat / 2, .06, 7000, 70, .02, 40 + k)
    scale = [48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]
    play(L, bpm, scale, {"light": lambda f: bell(f, .7, 1.0), "sound": marimba, "gravity": softsyn},
         {"light": .15, "sound": .22, "gravity": .18})
    return reverb(L, .3), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.6 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events:", [(r["year"], r["family"], deg(r, 15)) for r in EV])
print("times@96:", [round(x, 2) for x in times(96)])
