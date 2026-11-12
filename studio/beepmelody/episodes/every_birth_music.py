"""BeepMelody · EVERY BIRTH · rework of the music (PHASE R, Guillaume 2026-11-12: "la musique produite est pas terrible").
What was weak in v1: random pentatonic square bips over a static Cm loop -> no melody, no warmth, harsh timbre.
New rule for all three moods: every birth is still one hit at its own time (snapped to a 16th note, <= 1/32 note off),
but its pitch is taken from the CURRENT CHORD (region = octave/instrument), so the births form melodies over real changes.
Same 272 births as the video (imported from every_birth.py). Three really different moods:
  A · lullaby pop      — 92 BPM, F major I–V–vi–IV, Rhodes chords, soft kick/clap/shaker, births = kalimba/celesta
  B · afro-house       — 122 BPM, A minor i–VI–III–VII, four-on-floor + shaker + log-drum bass, births = marimba/balafon
  C · cinematic wonder — 100 BPM, D major I–vi–IV–V, string pad + piano births + soft taiko on each milestone, slow build
Usage (from studio/this-melody-is/engine, PYTHONPATH=../../beepmelody/episodes):
  python3 every_birth_music.py excerpts <outdir> [t0]      # 8 s of each mood on the densest passage
  python3 every_birth_music.py full <A|B|C> <wav>           # whole 66.5 s track for the chosen mood"""
import sys, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import every_birth as E

SR = 44100
TOTAL = E.TOTAL
BIRTHS = E.BIRTHS                   # (t, i, j, region, country)
MILE = sorted(E.MILE_T.values())
T_OUT = E.START["outro"]

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def ts(n): return np.arange(n) / SR

class Bus:
    def __init__(s): s.x = np.zeros(int((TOTAL + 2) * SR))
    def put(s, t, sig, g=1.0):
        i = int(t * SR); j = min(len(s.x), i + len(sig))
        if 0 <= i < len(s.x): s.x[i:j] += g * sig[:j - i]

def snap(t, bpm, div=4):
    st = 60 / bpm / div; return round(t / st) * st

def chord_at(t, bpm, prog):
    bar = 4 * 60 / bpm; return prog[int(t // bar) % len(prog)]

def pick(chord, reg, rs, base):
    """chord tone for a birth: region = octave, index = random chord tone (+ 9th sometimes)."""
    octv = {"africa": 0, "asia": 12, "americas": 12, "europe": 24, "oceania": 24}[reg]
    tones = list(chord) + [chord[0] + 14]
    return base + octv + tones[rs.randint(len(tones))]

# ---------- instruments ----------
def kalimba(f, d=.9):
    t = ts(int(d * SR)); return (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*25)) * np.exp(-t*4.5) * np.minimum(1, t/.002)
def celesta(f, d=1.2):
    t = ts(int(d * SR)); return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*f*4*t)*np.exp(-t*9) + .15*np.sin(2*np.pi*f*2*t)) * np.exp(-t*3) * np.minimum(1, t/.002)
def marimba(f, d=.7):
    t = ts(int(d * SR)); return (np.sin(2*np.pi*f*t) + .5*np.sin(2*np.pi*f*3.93*t)*np.exp(-t*28) + .2*np.sin(2*np.pi*f*9.2*t)*np.exp(-t*60)) * np.exp(-t*7) * np.minimum(1, t/.001)
def balafon(f, d=.5):
    t = ts(int(d * SR)); buzz = 1 + .25*np.sign(np.sin(2*np.pi*f*.5*t))*np.exp(-t*20)
    return (np.sin(2*np.pi*f*t) + .4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*30)) * buzz * np.exp(-t*10) * np.minimum(1, t/.001)
def rhodes(f, d):
    t = ts(int(d * SR)); idx = 1.6 * np.exp(-t*6)
    s = np.sin(2*np.pi*f*t + idx*np.sin(2*np.pi*f*t)) * (1 + .12*np.sin(2*np.pi*4.5*t))
    return s * np.exp(-t*1.1) * np.minimum(1, t/.004) * np.minimum(1, (d - t) / .08)
def piano(f, d=1.6):
    t = ts(int(d * SR)); s = sum((1/h**1.3) * np.sin(2*np.pi*f*h*np.sqrt(1+.0004*h*h)*t) * np.exp(-t*(1.5 + h*.9)) for h in range(1, 8))
    return s * np.minimum(1, t/.002)
def strings(freqs, d, att=.6):
    t = ts(int(d * SR)); s = 0
    for f in freqs:
        for dt in (.996, 1.0, 1.004):
            ph = (t * f * dt + np.random.RandomState(int(f)).rand()) % 1; s = s + (2*ph - 1)
    s = lp(s, 1500) / (3 * len(freqs))
    return s * np.minimum(1, t/att) * np.minimum(1, (d - t)/.5)
def kick(g=1., f0=110, f1=45, dec=9):
    t = ts(int(.4 * SR)); return g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-t*25) + f1)/SR) * np.exp(-t*dec)
def nz(d, fc, dec, seed, hi=None):
    t = ts(int(d * SR)); x = np.random.RandomState(seed).randn(len(t)); x = lp(x, fc)
    if hi: x = hp(x, hi)
    return x * np.exp(-t*dec)
def clap(seed):
    s = nz(.25, 3000, 18, seed, 900); t = ts(len(s))
    return s * (1 + .8*((t < .01) | ((t > .015) & (t < .025))))
def logdrum(f, d=.45):
    t = ts(int(d * SR)); fr = f * (1 + .35*np.exp(-t*30))
    return np.tanh(1.6*np.sin(2*np.pi*np.cumsum(fr)/SR)) * np.exp(-t*7) * np.minimum(1, t/.002)
def taiko():
    t = ts(int(1.2 * SR)); return (np.sin(2*np.pi*np.cumsum(60*np.exp(-t*8)+42)/SR) + .3*lp(np.random.RandomState(9).randn(len(t)), 600)*np.exp(-t*20)) * np.exp(-t*3.5)

def room(x, mix, damp=4000, big=False):
    taps = [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]
    if big: taps += [(1.07, .05), (1.33, .035)]
    out = x.copy()
    for d, g in taps:
        n = int(d * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lp(out, damp)

def finish(x):
    x = x[:int(TOTAL * SR)]
    fade = int(1.2 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = np.tanh(1.2 * x / (np.max(np.abs(x)) + 1e-9)) ; x = x / (np.max(np.abs(x)) + 1e-9) * .89
    return np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)

def ending(bus, bpm, notes, inst, g):
    """last birth -> rising arpeggio on the tonic chord, then a held chord."""
    ta = BIRTHS[-1][0] + .3; beat = 60 / bpm
    for q, m in enumerate(notes): bus.put(snap(ta, bpm) + q * beat / 2, inst(mtof(m)), g)

# ---------- A · lullaby pop ----------
def mood_a():
    bpm = 92; beat = 60 / bpm; bar = 4 * beat
    prog = [(5, 9, 12), (0, 4, 7), (2, 5, 9), (-2, 2, 5)]      # F  C  Dm  Bb   (relative to C)
    B = Bus(); D = Bus(); rs = np.random.RandomState(2023)
    for k, b in enumerate(np.arange(0, TOTAL - .5, bar)):
        c = prog[k % 4]
        for m in c: B.put(b, rhodes(mtof(48 + m), bar * 1.02), .05)      # chord, whole bar
        B.put(b, rhodes(mtof(36 + c[0]), bar), .09)                      # bass
        B.put(b + 2.5 * beat, rhodes(mtof(36 + c[0] + 7), beat * 1.4), .05)
    for k, b in enumerate(np.arange(0, T_OUT + 2, beat)):
        on = b >= E.START["india"] - .05
        if k % 2 == 0: D.put(b, kick(.9 if on else .5, 90, 42, 11))
        elif on: D.put(b, clap(k), .22)
        for q in (0, 2): D.put(b + q * beat / 4, nz(.05, 9000, 70, 50 + k + q, 4000), .05 if q else .035)
    for tm, _, _, reg, _ in BIRTHS:
        t = snap(tm, bpm); m = pick(chord_at(t, bpm, prog), reg, rs, 60)
        B.put(t, (celesta if reg in ("europe", "oceania", "americas") else kalimba)(mtof(m)), .16)
    for t in MILE: D.put(snap(t, bpm), nz(1.6, 8000, 2.5, int(t), 3000), .05)   # soft swell on each milestone
    ending(B, bpm, (65, 72, 77, 84), celesta, .14)
    return finish(room(B.x, .3) + room(D.x, .12))

# ---------- B · afro-house ----------
def mood_b():
    bpm = 122; beat = 60 / bpm; bar = 4 * beat
    prog = [(9, 12, 16), (5, 9, 12), (0, 4, 7), (7, 11, 14)]     # Am  F  C  G
    B = Bus(); D = Bus(); rs = np.random.RandomState(2023)
    pat = [0, 0, 1, 0, 0, 1, 0, 1]                                # log-drum syncopation (8ths)
    for k, b in enumerate(np.arange(0, T_OUT + 2, bar)):
        c = prog[k % 4]; on = b >= E.START["india"] - .05
        if on:
            for q, p in enumerate(pat):
                if p or q == 0: B.put(b + q * beat / 2, logdrum(mtof(33 + c[0] % 12 + (12 if q == 5 else 0))), .2)
        for m in c: B.put(b, strings([mtof(60 + m)], bar, .3), .25)      # light pad
    for k, b in enumerate(np.arange(0, T_OUT + 2, beat)):
        on = b >= E.START["india"] - .05
        D.put(b, kick(1.0, 120, 48, 10), .9)
        if on: D.put(b + beat / 2, nz(.12, 8000, 25, k, 5000), .08)            # open hat on the off-beat
        for q in range(4): D.put(b + q * beat / 4, nz(.04, 10000, 90, 90 + 4*k + q, 6000), .035 if q % 2 else .02)  # shaker 16ths
        if k % 4 == 3 and on: D.put(b + 3 * beat / 4, nz(.06, 3000, 40, 7 + k, 300), .12)   # rim
    for tm, _, _, reg, _ in BIRTHS:
        t = snap(tm, bpm); m = pick(chord_at(t, bpm, prog), reg, rs, 60)
        B.put(t, (balafon if reg == "africa" else marimba)(mtof(m)), .2)
    for t in MILE: D.put(snap(t, bpm), nz(1.4, 9000, 3, int(t), 3000), .07)
    ending(B, bpm, (57, 64, 69, 76), marimba, .2)
    return finish(room(B.x, .2) + room(D.x, .08))

# ---------- C · cinematic wonder ----------
def mood_c():
    bpm = 100; beat = 60 / bpm; bar = 4 * beat
    prog = [(2, 6, 9), (-1, 2, 6), (-5, -1, 2), (-3, 1, 4)]    # D  Bm  G  A
    B = Bus(); D = Bus(); rs = np.random.RandomState(2023)
    for k, b in enumerate(np.arange(0, TOTAL - .5, bar)):
        c = prog[k % 4]; lift = min(1, b / T_OUT)                         # slow build towards the outro
        B.put(b, strings([mtof(48 + m) for m in c] + [mtof(36 + c[0])], bar + .4, .9), .5 + .4 * lift)
        if b >= E.START["china"]:                                         # cellos pulse in 8ths from the 2nd act
            for q in range(8): B.put(b + q * beat / 2, strings([mtof(36 + c[0])], beat / 2, .02), .35 * lift)
    for k, b in enumerate(np.arange(0, T_OUT + 2, beat)):
        if b >= E.START["africa"] and k % 2 == 0: D.put(b, kick(.6, 70, 40, 7))
        if b >= E.START["world"]: D.put(b + beat / 2, nz(.05, 9000, 70, k, 5000), .03)
    for t in MILE: D.put(snap(t, bpm), taiko(), .5); D.put(snap(t, bpm), nz(2.0, 8000, 2, int(t), 3000), .04)
    for tm, _, _, reg, _ in BIRTHS:
        t = snap(tm, bpm); m = pick(chord_at(t, bpm, prog), reg, rs, 60)
        B.put(t, piano(mtof(m)), .16)
    ending(B, bpm, (62, 69, 74, 78, 81), piano, .17)
    return finish(room(B.x, .35, 5000, True) + room(D.x, .2, 3000, True))

MOODS = {"A": mood_a, "B": mood_b, "C": mood_c}

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "full":
        wavfile.write(sys.argv[3], SR, (MOODS[sys.argv[2]]() * 32767).astype(np.int16))
    elif mode == "excerpts":
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 31.75
        for k, fn in MOODS.items():
            x = fn()[int(t0 * SR):int((t0 + 8) * SR)].copy()
            n = int(.05 * SR); x[:n] *= np.linspace(0, 1, n)[:, None]; n = int(.6 * SR); x[-n:] *= np.linspace(1, 0, n)[:, None]
            wavfile.write(f"{out}/birth_r1_{k}.wav", SR, (x * 32767).astype(np.int16))
        print("births in excerpt:", sum(1 for b in BIRTHS if t0 <= b[0] < t0 + 8))
