"""BeepMelody · Life on Earth (extinctions angle) · co-pilot step 2: three 8 s mood excerpts on the
busiest passage: Cambrian explosion (538.8 Ma) -> end-Permian extinction (251.9 Ma), 11 events incl. 3 mass extinctions.
Pitch = a 'life level' that climbs one step per new group of life and falls by % of species lost (1 step per 20 %).
Usage: python3 life_moods.py <life_timeline_draft.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
OUT = sys.argv[2]
ALL = list(csv.DictReader(open(sys.argv[1])))

def pct(label):
    if not label.startswith("EXTINCTION"): return 0
    return int(label.split("·")[1].strip().split("%")[0])

# life level over the full series, so pitches match the final episode
lvl, LV = 0, []
for r in ALL:
    p = pct(r["label"])
    lvl = lvl - int(round(p / 20)) if p else lvl + 1
    LV.append(lvl)
LO, HI = min(LV), max(LV)
EV = [(float(r["mya"]), r["label"], pct(r["label"]), v) for r, v in zip(ALL, LV) if 251.9 <= float(r["mya"]) <= 538.8]

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
def note_of(e, scale): return scale[int(round((e[3] - LO) / max(1, HI - LO) * (len(scale) - 1)))]
def times(bpm):  # 11 events over 0.2..7.2 s, on a 16th grid
    s16 = 60 / bpm / 4; step = 7.0 / (len(EV) - 1)
    return [round((0.2 + i * step) / s16) * s16 for i in range(len(EV))]
def kick(b, L, g=.26):
    n = int(.35 * SR); tt = np.arange(n) / SR
    put(L, b, g * np.sin(2*np.pi*np.cumsum(80*np.exp(-tt*16)+48)/SR) * np.exp(-tt*12))
def noise(L, b, dur, fc, dec, g, seed):
    n = int(dur * SR); put(L, b, g * lowpass(np.random.RandomState(seed).randn(n), fc) * np.exp(-np.arange(n)/SR*dec))
def broken(f, dur, g, drop=12):
    """the 'broken note' of an extinction: pitch falls by `drop` semitones, detuned, with grit"""
    n = int(dur * SR); tt = np.arange(n) / SR
    fr = f * 2 ** (-drop * np.minimum(1, tt / dur) / 12)
    ph = 2*np.pi*np.cumsum(fr)/SR
    s = np.sin(ph) + .6*np.sin(ph*1.013) + .25*np.sign(np.sin(ph*.5))
    s += .3*lowpass(np.random.RandomState(int(f)).randn(n), 900)
    return g * s * env(n, .004, dur * .45)
def mute_windows(tms, length):   # beat bed drops out right after each extinction ("almost ended")
    return [(tm, tm + length) for e, tm in zip(EV, tms) if e[2]]
def in_mute(b, wins): return any(a <= b < z for a, z in wins)

# A · Living world — 92 BPM, marimba new-life notes, shaker + soft kick, round bass, Am–F–C–G; extinction = low thud + falling detuned note, bed stops 1 beat
def mood_a():
    bpm = 92; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat; tms = times(bpm)
    wins = mute_windows(tms, beat * 1.5)
    roots = [45, 41, 36, 43]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * SR); tt = np.arange(n) / SR
        put(L, b, .14 * np.sin(2*np.pi*mtof(roots[k % 4])*tt) * np.exp(-tt*1.3))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if in_mute(b, wins): continue
        if k % 2 == 0: kick(b, L, .2)
        else: noise(L, b, .1, 4000, 30, .045, k)
        noise(L, b + beat/2, .05, 8000, 90, .025, 50+k)
    scale = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88]
    for e, tm in zip(EV, tms):
        f = mtof(note_of(e, scale))
        if e[2]:
            kick(tm, L, .4); put(L, tm, broken(f, 1.2, .16))
            continue
        n = int(1.2 * SR); tt = np.arange(n) / SR
        s = np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25)
        put(L, tm, .2 * s * env(n, .002, .4))
    return reverb(L, .22), "A"

# B · Deep time — 64 BPM, low drone + strings pad, glass bells for new life; extinction = sub boom + falling cello-like note, pad drops out
def mood_b():
    bpm = 64; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; tms = times(bpm)
    drone = sum(np.sin(2*np.pi*mtof(m)*d*t) for m in (33, 40) for d in (.997, 1.003)) * .03
    gate = np.ones(len(L))
    for e, tm in zip(EV, tms):
        if e[2]:
            i = int(tm * SR); j = min(len(L), i + int(1.6 * SR))
            gate[i:j] = np.minimum(gate[i:j], np.linspace(.15, 1, j - i) ** 2)
    pad = sum(np.sin(2*np.pi*mtof(m)*d*t) for m in (45, 52, 57, 60, 64) for d in (.995, 1.005)) * .009
    L += lowpass(drone + pad * gate, 2500)
    scale = [57, 59, 60, 64, 65, 69, 71, 72, 76, 77, 81, 83, 84, 88]   # A phrygian-ish, dark
    for e, tm in zip(EV, tms):
        f = mtof(note_of(e, scale))
        if e[2]:
            n = int(2.5 * SR); tt = np.arange(n) / SR
            put(L, tm, .45 * np.sin(2*np.pi*np.cumsum(55*np.exp(-tt*3)+28)/SR) * np.exp(-tt*1.8))   # sub boom
            put(L, tm, lowpass(broken(f / 2, 2.0, .2, 7), 1500))
            continue
        n = int(2.5 * SR); tt = np.arange(n) / SR
        s = np.sin(2*np.pi*f*tt + 1.6*np.exp(-tt*4)*np.sin(2*np.pi*f*3.5*tt))
        put(L, tm, .15 * s * env(n, .003, 1.0))
    return reverb(L, .55), "B"

# C · Comeback groove — 118 BPM, pizzicato + kalimba, kick/snare, octave bass; extinction = glitch crunch, drums cut half a bar then slam back
def mood_c():
    bpm = 118; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat; tms = times(bpm)
    wins = mute_windows(tms, beat * 2)
    roots = [40, 36, 43, 38]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q in range(8):
            bb = b + q * beat / 2
            if in_mute(bb, wins): continue
            n = int(.25 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + (12 if q % 2 else 0))
            put(L, bb, .09 * np.sign(np.sin(2*np.pi*f*tt)) * .5 * np.exp(-tt*10))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if in_mute(b, wins): continue
        kick(b, L, .27)
        if k % 2: noise(L, b, .14, 3500, 22, .09, k)
        noise(L, b + beat/2, .04, 9000, 120, .03, 90+k)
    scale = [52, 55, 57, 59, 62, 64, 67, 69, 71, 74, 76, 79, 81, 83]
    for e, tm in zip(EV, tms):
        f = mtof(note_of(e, scale))
        if e[2]:
            g = broken(f, .9, .2, 14)
            g = np.round(g * 6) / 6                                     # bit-crush
            put(L, tm, g); noise(L, tm, .3, 6000, 12, .12, 7)
            continue
        n = int(.9 * SR); tt = np.arange(n) / SR
        s = sum((1/h) * np.sin(2*np.pi*f*h*tt) * np.exp(-tt*(6 + 4*h)) for h in range(1, 6))
        s += .4*np.sin(2*np.pi*f*2*tt)*np.exp(-tt*5)                  # kalimba shimmer
        put(L, tm, .2 * s * env(n, .002, .35))
    return reverb(L, .15), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events:", [(e[0], e[1][:20], e[3]) for e in EV], "level range", LO, HI)
