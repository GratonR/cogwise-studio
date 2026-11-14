"""BeepMelody · Cosmic timeline · co-pilot step 2: three 8 s mood excerpts on the densest passage
(the log-clock finale: first stars ~200 Myr -> today 13.8 Gyr, 12 events packed together).
One event = one note; pitch = rank of the moment in the FULL series (each new big moment one step up the story),
kept in a ~2.5-octave mid register (the log clock squeezes the finale, so log(time) would give a monotone).
Usage: python3 cosmic_moods.py <cosmic_timeline_draft.csv> <outdir>"""
import sys, csv, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
OUT = sys.argv[2]
ALL = list(csv.DictReader(open(sys.argv[1])))
LO, HI = math.log10(float(ALL[0]["t_s"])), math.log10(float(ALL[-1]["t_s"]))
EV = [r for r in ALL if float(r["t_s"]) >= 6e15]          # first stars -> today
RANK = {id(r): i for i, r in enumerate(ALL)}
def pos(r): return RANK[id(r)] / (len(ALL) - 1)
def deg(r, steps): return int(round(np.clip(pos(r), 0, 1) * (steps - 1)))
def is_hook(r): return "MoM-z14" in r["label"]
def is_end(r): return r["kind"] == "end"

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
    """12 events over 0.3..7.0 s, gaps shrinking (the finale tightens), snapped to a 16th grid."""
    s16 = 60 / bpm / 4; n = len(EV)
    w = np.array([0.86 ** i for i in range(n - 1)]); cum = np.concatenate([[0], np.cumsum(w)]) / w.sum()
    out, last = [], -1
    for c in cum:
        g = max(last + 1, round((0.3 + c * 6.4) / s16)); out.append(g * s16); last = g
    return out
def kick(b, L, g=.26, f0=80):
    n = int(.35 * SR); tt = np.arange(n) / SR
    put(L, b, g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+46)/SR) * np.exp(-tt*12))
def noise(L, b, dur, fc, dec, g, seed):
    n = int(dur * SR); put(L, b, g * lowpass(np.random.RandomState(seed).randn(n), fc) * np.exp(-np.arange(n)/SR*dec))
def arp(L, f, t0, step, voice, g):
    for j, m in enumerate([0, 7, 12, 19]): put(L, t0 + (j + 1) * step, g * voice(f * 2 ** (m / 12)))

# A · Deep field — 64 BPM, wide detuned pad (Dsus2 -> Bbmaj7), glass FM bells, sub swell rising to the end
def mood_a():
    bpm = 64; L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR; bar = 4 * 60 / bpm
    chords = [[38, 45, 50, 52, 57, 64], [34, 41, 46, 50, 57, 62]]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * 1.35 * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in chords[k % 2]:
            for det in (.994, 1.0, 1.007): s += np.sin(2*np.pi*mtof(m)*det*tt)
        put(L, b, .013 * s * np.minimum(1, tt / 1.8) * np.clip((bar*1.35 - tt) / .9, 0, 1))
    L += .10 * np.sin(2*np.pi*mtof(26)*t) * (t / DUR) ** 2                      # sub swell
    L += lowpass(np.random.RandomState(3).randn(len(L)), 1500) * (t / DUR) ** 2 * .025
    scale = [45, 47, 50, 52, 54, 57, 59, 62, 64, 66, 69, 71, 74, 76, 78]  # D major pentatonic, A2..F#5
    def bell(f, d=1.2):
        n = int(2.8 * SR); tt = np.arange(n) / SR
        return np.sin(2*np.pi*f*tt + 1.6*np.exp(-tt*4)*np.sin(2*np.pi*f*3.5*tt)) * env(n, .003, d)
    for r, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(r, len(scale))])
        put(L, tm, (.15 + (.07 if is_hook(r) or is_end(r) else 0)) * bell(f))
        if is_end(r): arp(L, f, tm, 60 / bpm / 2, lambda x: bell(x, .9), .08)
    return reverb(L, .55, 1.4), "A"

# B · Cosmic drive — 112 BPM, 16th synth-bass arpeggio, soft four-on-the-floor, bright pluck lead (Am - F - C - G)
def mood_b():
    bpm = 112; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; s16 = beat / 4; bar = 4 * beat
    roots = [33, 29, 36, 31]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        for q in range(16):
            n = int(s16 * .9 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + [0, 12, 7, 12][q % 4])
            saw = 2 * ((f * tt) % 1) - 1
            put(L, b + q * s16, .07 * lowpass(saw, 900 + 500 * (b / DUR)) * np.exp(-tt * 9))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        kick(b, L, .26)
        if k % 2: noise(L, b, .16, 5000, 18, .06, k)
        noise(L, b + beat / 2, .04, 9000, 120, .03, 70 + k)
    scale = [45, 48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79]  # A minor pentatonic, A2..G5
    def pluck(f):
        n = int(.9 * SR); tt = np.arange(n) / SR
        s = sum((1 / h) * np.sin(2*np.pi*f*h*1.002*tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
        return s * env(n, .002, .35)
    for r, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(r, len(scale))])
        put(L, tm, (.20 + (.07 if is_hook(r) or is_end(r) else 0)) * pluck(f))
        put(L, tm + 3 * s16, .06 * pluck(f))                                     # dotted-8th echo
        if is_end(r): arp(L, f, tm, s16, pluck, .11)
    return reverb(L, .22), "B"

# C · Star music box — 92 BPM (family of the altitude pilot): celesta + soft synth pad + brushed drums, Fmaj7 - G - Em7 - Am
def mood_c():
    bpm = 92; L = np.zeros(int(DUR * SR)); beat = 60 / bpm; bar = 4 * beat
    chords = [[41, 53, 57, 60, 64], [43, 55, 59, 62], [40, 52, 55, 59, 62], [45, 57, 60, 64]]
    for k, b in enumerate(np.arange(0, DUR, bar)):
        n = int(bar * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in chords[k % 4]: s += np.sin(2*np.pi*mtof(m)*tt) + .3*np.sin(2*np.pi*mtof(m)*2.003*tt)
        put(L, b, .018 * lowpass(s, 1800) * np.minimum(1, tt / .3) * np.clip((bar - tt) / .3, 0, 1))
        n2 = int(bar * SR); put(L, b, .13 * np.sin(2*np.pi*mtof(chords[k % 4][0] - 12)*tt[:n2]) * np.exp(-tt[:n2] * 1.2))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if k % 2 == 0: kick(b, L, .18, 70)
        else: noise(L, b, .18, 3000, 14, .05, k)                                  # brush
        noise(L, b + beat / 2, .06, 7000, 70, .02, 40 + k)
    scale = [48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]  # C major pentatonic, C3..A5 (soft timbre)
    def celesta(f):
        n = int(1.8 * SR); tt = np.arange(n) / SR
        s = np.sin(2*np.pi*f*tt) + .25*np.sin(2*np.pi*f*4.0*tt)*np.exp(-tt*12) + .12*np.sin(2*np.pi*f*2*tt)
        return s * env(n, .002, .6)
    for r, tm in zip(EV, times(bpm)):
        f = mtof(scale[deg(r, len(scale))])
        put(L, tm, (.17 + (.07 if is_hook(r) or is_end(r) else 0)) * celesta(f))
        if is_end(r): arp(L, f / 2, tm, beat / 2, celesta, .09)
    return reverb(L, .3), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.6 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(EV), "events:", EV[0]["label"], "->", EV[-1]["label"])
print("times@92:", [round(x, 2) for x in times(92)])
print("degrees:", [deg(r, 15) for r in EV])
