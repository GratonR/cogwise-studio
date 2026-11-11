"""BeepMelody · Every birth (globe angle) · co-pilot step 2: three 8 s mood excerpts.
Real time: 132.1 M births in 2023 (UN WPP 2024) = 4.19 births/s -> ~34 beeps in 8 s.
Births are drawn as a Poisson process (seeded), each one assigned a region by its share of 2023 births
(approximate regional shares, checked again at step 3). One birth = one hit; region = timbre + register.
Usage: python3 birth_moods.py <outdir>"""
import sys, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
RATE = 132.1e6 / (365 * 86400)          # 4.19 births per second
OUT = sys.argv[1]
REG = [("asia", .50), ("africa", .33), ("latam", .07), ("europe", .05), ("namerica", .03), ("oceania", .02)]
P = np.array([p for _, p in REG]); P /= P.sum()

rs = np.random.RandomState(2023)
T, t = [], .15
while True:
    t += rs.exponential(1 / RATE)
    if t > DUR - .6: break
    T.append(t)
EVR = [REG[i][0] for i in rs.choice(len(REG), len(T), p=P)]
EVD = rs.randint(0, 5, len(T))           # scale degree inside the region's register

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
def snap(t, bpm, div=4):
    s = 60 / bpm / div; return round(t / s) * s
def kick(b, L, g=.26, f0=80, f1=48):
    n = int(.35 * SR); tt = np.arange(n) / SR
    put(L, b, g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+f1)/SR) * np.exp(-tt*12))
def noise(L, b, dur, fc, dec, g, seed):
    n = int(dur * SR); put(L, b, g * lowpass(np.random.RandomState(seed).randn(n), fc) * np.exp(-np.arange(n)/SR*dec))
PENTA = [0, 2, 4, 7, 9]
def pitch(reg, deg, base):
    off = {"asia": 12, "africa": 0, "latam": 19, "europe": 24, "namerica": 21, "oceania": 28}[reg]
    return base + off + PENTA[deg]

# A · Lullaby / warm organic — 84 BPM, music-box + marimba + kalimba per region, soft pad C–Am–F–G, no drums but a shaker
def mood_a():
    bpm = 84; L = np.zeros(int(DUR * SR)); tt0 = np.arange(len(L)) / SR; bar = 4 * 60 / bpm
    chords = [(48, 52, 55), (45, 48, 52), (41, 45, 48), (43, 47, 50)]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * SR); tt = np.arange(n) / SR
        s = sum(np.sin(2*np.pi*mtof(m)*d*tt) for m in chords[k % 4] for d in (.996, 1.004))
        put(L, b, .03 * s * np.minimum(1, tt / .4) * np.minimum(1, (bar - tt) / .3))
    for k, b in enumerate(np.arange(0, DUR, 60 / bpm / 2)):
        noise(L, b, .06, 7000, 70, .018 if k % 2 else .03, k)
    for tm, reg, dg in zip(T, EVR, EVD):
        tm = snap(tm, bpm); f = mtof(pitch(reg, dg, 48)); n = int(1.4 * SR); tt = np.arange(n) / SR
        if reg == "africa":    # marimba
            s = np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*30); d = .35
        elif reg == "asia":    # kalimba
            s = np.sin(2*np.pi*f*tt) + .45*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*8); d = .45
        else:                  # music box / glockenspiel
            s = np.sin(2*np.pi*f*tt) + .5*np.sin(2*np.pi*f*3*tt)*np.exp(-tt*6); d = .7
        put(L, tm, .14 * s * env(n, .002, d))
    return reverb(L, .3), "A"

# B · Heartbeat — 120 BPM, lub-dub kick, soft house hats, round bass Am–F–C–G, bright plucks for births
def mood_b():
    bpm = 120; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat
    roots = [45, 41, 48, 43]
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kick(b, L, .28); kick(b + beat * .28, L, .14, 70, 44)      # lub-dub
        noise(L, b + beat / 2, .05, 9000, 100, .035, k)
        if k % 2: noise(L, b, .12, 4000, 25, .05, 40 + k)
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q in range(8):
            n = int(.22 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] - 12 + (12 if q % 2 else 0))
            put(L, b + q * beat / 2, .12 * np.sin(2*np.pi*f*tt) * np.exp(-tt*9))
    for tm, reg, dg in zip(T, EVR, EVD):
        tm = snap(tm, bpm); f = mtof(pitch(reg, dg, 57)); n = int(.6 * SR); tt = np.arange(n) / SR
        saw = sum(((-1) ** h / h) * np.sin(2*np.pi*f*h*tt) for h in range(1, 8))
        s = lowpass(saw, 1800 + 3000 * (reg in ("europe", "namerica", "oceania")))
        put(L, tm, .13 * s * env(n, .002, .14))
    return reverb(L, .18), "B"

# C · Like the reference ("This Melody Is Us") — 128 BPM chiptune: square bips, triangle bass, noise drums, wide pad
def mood_c():
    bpm = 128; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat; t = np.arange(len(L)) / SR
    pad = sum(np.sin(2*np.pi*mtof(m)*d*t) for m in (48, 55, 60, 63) for d in (.995, 1.005)) * .008
    L += lowpass(pad, 2000)
    roots = [36, 44, 46, 43]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q in range(8):
            n = int(.2 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + 12 * (q % 2))
            tri = 2 / np.pi * np.arcsin(np.sin(2*np.pi*f*tt))
            put(L, b + q * beat / 2, .14 * tri * np.exp(-tt*6))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if k % 2 == 0: noise(L, b, .08, 1200, 40, .16, k)
        else: noise(L, b, .1, 5000, 30, .09, k)
        noise(L, b + beat / 2, .03, 9000, 150, .03, 70 + k)
    for tm, reg, dg in zip(T, EVR, EVD):
        tm = snap(tm, bpm); f = mtof(pitch(reg, dg, 51)); n = int(.35 * SR); tt = np.arange(n) / SR
        duty = .125 if reg in ("asia", "africa") else .25
        sq = np.where((tt * f) % 1 < duty, 1.0, -1.0)
        s = sq * env(n, .001, .09); put(L, tm, .09 * s); put(L, tm + .75 * beat, .035 * s)   # echo
    return reverb(L, .2), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"birth_mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
from collections import Counter
print(len(T), "births in", DUR, "s (rate", round(RATE, 2), "/s):", Counter(EVR))
