"""BeepMelody · Jupiter's moons · RETRAVAIL r1 (Guillaume 17 nov.: « Trop bien mais améliore la musique. Les visuels 3d sont bons »).
Same episode, same data, same visuals: only the music is reworked. Three full-length scores built on the REAL hits of
jupiter_moons.py (one completed lap = one hit, exactly on the crossing, no grid snapping), now with harmony and melody:
  - the chord turns on each Ganymede lap (before Ganymede joins: every 2nd Europa lap, before Europa: every 4th Io lap),
    progression Dm - Bb - F - C (i - VI - III - VII);
  - Io plays a melody: each lap = the next note of an arpeggio contour on the current chord;
  - Europa / Ganymede / Callisto keep their own instrument (rhythm section / bass / big accent).
Moods:  R1 « Tambours chantants » (the drums of C kept + marimba melody, kalimba, warm pad, bass)
        R2 « Funk orbital » (2 beats per Io lap ≈ 136 BPM: kick, hats, synth bass, pluck lead, rhodes stabs)
        R3 « Odyssée orchestrale » (strings, harp, celesta, timpani, brass swell — wide and cinematic)
Usage: python3 jupiter_moons_moods_r1.py <outdir> [--full]   (8 s excerpts on the densest passage, T = 31 -> 39 s;
       --full also writes the full-length music_R*.wav)"""
import sys, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import jupiter_moons as J

SR = 44100
OUT = sys.argv[1]
FULL = "--full" in sys.argv
X0, XD = 31.0, 8.0                       # excerpt window (densest: all four moons, 17 hits)

HT = J.HT; T_END = J.T_END; TOTAL = J.TOTAL
N = int((TOTAL + 1.0) * SR); T = np.arange(N) / SR

# ---------- harmony anchored on the data ----------
CHORDS = [  # (bass root, chord tones for pads, melody pool)
    ("Dm", 38, [50, 53, 57, 60, 64], [62, 65, 69, 72, 74, 77, 81]),
    ("Bb", 34, [50, 53, 58, 62, 65], [62, 65, 70, 74, 77, 82, 86]),
    ("F",  41, [53, 57, 60, 64, 67], [65, 69, 72, 76, 77, 81, 84]),
    ("C",  36, [52, 55, 60, 62, 67], [64, 67, 72, 74, 76, 79, 84]),
]
def boundaries():
    io, eu, ga = HT["Io"], HT["Europa"], HT["Ganymede"]
    b = [0.0]
    b += [t for k, t in enumerate(io) if k % 4 == 3 and (not eu or t < eu[0])]
    b += [t for k, t in enumerate(eu) if k % 2 == 1 and (not ga or t < ga[0])]
    b += [t for t in ga if t < T_END - 0.5]
    b = sorted(set(round(x, 4) for x in b))
    return b
BND = boundaries()
def chord_at(t):
    k = max(i for i, x in enumerate(BND) if x <= t + 1e-6)
    return CHORDS[k % 4], k
FINAL = CHORDS[0]
CONTOUR = [0, 2, 1, 3, 2, 4, 3, 5, 4, 2, 3, 1]

# ---------- synth helpers ----------
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
def noise(dur, fc, dec, seed, hp=None):
    n = int(dur * SR); s = lowpass(np.random.RandomState(seed % 100000).randn(n), fc)
    if hp: s = highpass(s, hp)
    return s * np.exp(-np.arange(n) / SR * dec)
def reverb(x, mix=.35, size=1.0):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05), (1.45, .035)]:
        n = int(d * size * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4500)
def saw(f, n, harm=14, det=1.0):
    tt = np.arange(n) / SR; s = np.zeros(n)
    for h in range(1, harm + 1):
        if f * h * det > 9000: break
        s += ((-1) ** (h + 1)) / h * np.sin(2 * np.pi * f * h * det * tt)
    return s
def marimba(f, d=.35):
    n = int(1.3 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25) + .1*np.sin(2*np.pi*f*10*tt)*np.exp(-tt*60)) * env(n, .001, d)
def kalimba(f):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .25*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*18)) * env(n, .002, .5)
def pluck(f, dec=.35, bright=7):
    n = int(1.0 * SR); tt = np.arange(n) / SR
    s = sum((1 / h) * np.sin(2*np.pi*f*h*1.001*tt) * np.exp(-tt * (4 + bright * h * .5)) for h in range(1, 9))
    return s * env(n, .002, dec)
def harp(f):
    n = int(2.2 * SR); tt = np.arange(n) / SR
    s = sum((.9 ** h) / h * np.sin(2*np.pi*f*h*tt) * np.exp(-tt * (1.2 + .9 * h)) for h in range(1, 8))
    return s * env(n, .003, 1.2)
def celesta(f):
    n = int(1.8 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .4*np.sin(2*np.pi*f*2*tt)*np.exp(-tt*6) + .15*np.sin(2*np.pi*f*3.01*tt)*np.exp(-tt*12)) * env(n, .001, .7)
def rhodes(f, d=.6):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt + .8*np.exp(-tt*6)*np.sin(2*np.pi*f*tt)) + .15*np.sin(2*np.pi*f*7*tt)*np.exp(-tt*30)) * env(n, .002, d)
def tom(f0, g, d=.45):
    n = int(.9 * SR); tt = np.arange(n) / SR
    return g * np.sin(2*np.pi*np.cumsum(f0*(1+.6*np.exp(-tt*20)))/SR) * np.exp(-tt / d)
def gong(f, d=2.5):
    n = int(4.5 * SR); tt = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*r*tt) * np.exp(-tt * k) for a, r, k in [(1, 1, .5), (.6, 1.48, .9), (.45, 2.13, 1.3), (.3, 2.71, 1.8), (.2, 3.9, 2.6)])
    return s * env(n, .01, d)
def kick(g=.3, f0=90, f1=45):
    n = int(.4 * SR); tt = np.arange(n) / SR
    return g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*18)+f1)/SR) * np.exp(-tt*10)
def wood(f):
    n = int(.25 * SR); tt = np.arange(n) / SR; return np.sin(2*np.pi*f*tt) * np.exp(-tt * 40)

def pad_track(voicing, kind, gain, att=.6):
    """continuous pad following the chord boundaries (crossfaded segments)."""
    out = np.zeros(N); edges = BND + [T_END]
    for k in range(len(edges) - 1):
        a, b = edges[k], edges[k + 1] + (TOTAL - T_END if k == len(edges) - 2 else 0) + .6
        ch = CHORDS[k % 4] if k < len(edges) - 2 else (CHORDS[k % 4])
        n = int((b - a) * SR); tt = np.arange(n) / SR; s = np.zeros(n)
        for m in voicing(ch):
            if kind == "saw":
                for det in (.996, 1.0, 1.004): s += saw(mtof(m), n, 10, det) / 3
            else:
                for det in (.995, 1.0, 1.005): s += np.sin(2 * np.pi * mtof(m) * det * tt) / 3
        e = np.minimum(1, tt / att) * np.minimum(1, np.maximum(0, (b - a - tt) / .6))
        put(out, a, s * e, gain)
    return out
def io_note(i, t, pool_shift=0):
    (_, _, _, pool), _ = chord_at(t)
    return pool[min(len(pool) - 1, CONTOUR[i % len(CONTOUR)] + pool_shift)]
def end_env():
    return np.clip(T / 1.0, 0, 1) * np.clip((TOTAL - T) / 2.0, 0, 1)
def layer():
    return np.clip((T - J.T0) * J.DPS / 60.0, 0, 1)

# ================= R1 · Tambours chantants (~102 BPM: 3 beats per Io lap) =================
def mood_r1():
    L = np.zeros(N); beat = J.PER["Io"] / J.DPS / 3
    L += pad_track(lambda ch: ch[2][:4], "sine", .022, .9) * end_env()
    tb = HT["Io"][0] - 3 * beat; k = 0                                     # shaker, locked on Io
    while tb < T_END + 2 * beat:
        if tb >= 0: put(L, tb, noise(.07, 8000, 60, 300 + k, 3000), .03 if k % 3 == 0 else .017)
        tb += beat; k += 1
    for i, tm in enumerate(HT["Io"]):                                      # marimba melody + soft woodblock tick
        put(L, tm, .17 * marimba(mtof(io_note(i, tm) - 12)))
        put(L, tm, .05 * wood(mtof(84)))
    for i, tm in enumerate(HT["Europa"]):                                  # conga + kalimba third above
        put(L, tm, tom(mtof(57), .22, .18))
        (_, _, tones, _), _ = chord_at(tm); put(L, tm, .10 * kalimba(mtof(tones[1 + i % 3] + 12)))
    for tm in HT["Ganymede"]:                                              # taiko + new bass note (chord turns here)
        put(L, tm, tom(mtof(38), .40, .5)); put(L, tm, noise(.3, 900, 9, 77), .08)
        (_, root, _, _), _ = chord_at(tm + .01); n = int(3.0 * SR); tt = np.arange(n) / SR
        put(L, tm, .16 * lowpass(saw(mtof(root), n, 8), 500) * env(n, .01, 1.6))
    for tm in HT["Callisto"]:                                              # gong + low choir swell
        put(L, tm, .22 * gong(mtof(38), 3.0))
        (_, root, _, _), _ = chord_at(tm); n = int(3.5 * SR); tt = np.arange(n) / SR
        sw = sum(np.sin(2*np.pi*mtof(root + 12 + d)*tt*(1 + .002*np.sin(2*np.pi*5*tt))) for d in (0, 7, 12))
        put(L, tm, .035 * sw * np.sin(np.pi * np.minimum(1, tt / 3.5)))
    put(L, T_END, .30 * gong(mtof(26), 4.0)); put(L, T_END, tom(mtof(31), .5, .8))
    for m in (62, 65, 69, 74): put(L, T_END, .07 * marimba(mtof(m), .9))
    L += .045 * np.sin(2*np.pi*mtof(26)*T) * (.7 + .3*np.sin(2*np.pi*T/4)) * end_env()
    return reverb(L, .3, 1.2)

# ================= R2 · Funk orbital (~136 BPM: 2 beats per Io lap) =================
def mood_r2():
    L = np.zeros(N); beat = J.PER["Io"] / J.DPS / 2; s16 = beat / 4
    L += lowpass(pad_track(lambda ch: ch[2][:4], "saw", .010, .3), 1400) * end_env()
    tb = HT["Io"][0] - 2 * beat; k = 0
    while tb < T_END + beat:
        if tb >= 0:
            put(L, tb, kick(.30 if k % 2 == 0 else .22))
            for q in range(4): put(L, tb + q * s16, noise(.04, 10000, 120, 70 + 4*k + q, 6000), .026 if q % 2 else .014)
            (_, root, _, _), _ = chord_at(tb)
            for q, (o, g) in enumerate([(0, 0), (12, .9), (0, .7), (10, .6)]):   # syncopated synth bass (16ths 0, 1.5, 2, 3)
                if g == 0 and q > 0: continue
                at = tb + [0, 1.5, 2, 3][q] * s16; n = int(s16 * .9 * SR); tt = np.arange(n) / SR
                put(L, at, (.11 if q == 0 else .07) * lowpass(saw(mtof(root + o + 12), n, 10), 900) * np.exp(-tt * 9))
        tb += beat; k += 1
    for i, tm in enumerate(HT["Io"]):                                      # bright pluck lead
        put(L, tm, .14 * pluck(mtof(io_note(i, tm)), .3, 5))
        put(L, tm + .33 * beat * 3 / 2, .05 * pluck(mtof(io_note(i, tm)), .2, 5))   # dotted echo
    for i, tm in enumerate(HT["Europa"]):                                  # clap + rhodes chord stab
        put(L, tm, noise(.16, 7000, 24, int(tm * 100), 1000), .10)
        (_, _, tones, _), _ = chord_at(tm)
        for m in tones[1:4]: put(L, tm, .045 * rhodes(mtof(m + 12), .35))
    for tm in HT["Ganymede"]:                                              # sub drop on the chord change
        n = int(.9 * SR); tt = np.arange(n) / SR; (_, root, _, _), _ = chord_at(tm + .01)
        put(L, tm, .22 * lowpass(np.sin(2*np.pi*np.cumsum(mtof(root)*(1+.6*np.exp(-tt*9)))/SR), 400) * np.exp(-tt * 2.5))
    for tm in HT["Callisto"]:                                              # crash + rising filter swell
        put(L, tm, noise(2.2, 12000, 2.0, 999, 5000), .045)
        n = int(1.2 * SR); tt = np.arange(n) / SR
        put(L, tm - 1.2, .03 * highpass(np.random.RandomState(7).randn(n), 2000) * (tt / 1.2) ** 2)
    put(L, T_END, noise(3.0, 12000, 1.0, 5, 3000), .10); put(L, T_END, kick(.35))
    for m in (62, 65, 69, 74): put(L, T_END, .06 * rhodes(mtof(m), 1.5))
    return reverb(L, .18, .9)

# ================= R3 · Odyssée orchestrale (~68 BPM: 1 beat per Io lap) =================
def mood_r3():
    L = np.zeros(N); ly = layer()
    strings = lowpass(pad_track(lambda ch: [ch[1] + 12] + ch[2][:4], "saw", .012, 1.4), 2200)
    L += strings * (.55 + .45 * ly) * end_env()
    for i, tm in enumerate(HT["Io"]):                                      # harp arpeggio
        put(L, tm, .16 * harp(mtof(io_note(i, tm))))
    for i, tm in enumerate(HT["Europa"]):                                  # celesta, one octave up
        put(L, tm, .09 * celesta(mtof(io_note(i * 2 + 1, tm, 1) + 12)))
    for tm in HT["Ganymede"]:                                              # timpani + contrabass on the chord change
        (_, root, _, _), _ = chord_at(tm + .01)
        put(L, tm, tom(mtof(root + 12), .32, .7)); put(L, tm, noise(.5, 600, 6, 31), .05)
        n = int(3.2 * SR); tt = np.arange(n) / SR
        put(L, tm, .10 * lowpass(saw(mtof(root), n, 10), 600) * np.minimum(1, tt / .15) * np.exp(-tt / 2.0))
    for tm in HT["Callisto"]:                                              # brass swell + cymbal
        (_, root, tones, _), _ = chord_at(tm); n = int(3.0 * SR); tt = np.arange(n) / SR
        br = sum(saw(mtof(m), n, 12) for m in (root + 12, root + 19, root + 24))
        put(L, tm - .25, .045 * lowpass(br, 1800) * np.sin(np.pi * np.minimum(1, tt / 3.0)) ** 1.5)
        put(L, tm, noise(3.0, 9000, 1.8, 404, 4000), .018)
    put(L, T_END, tom(mtof(38), .45, 1.2))
    n = int(5 * SR); tt = np.arange(n) / SR
    put(L, T_END, .05 * lowpass(sum(saw(mtof(m), n, 10) for m in (38, 50, 57, 62, 65)), 1600) * np.minimum(1, tt / .3) * np.exp(-tt / 2.2))
    for m in (62, 65, 69, 74, 77): put(L, T_END + (m - 62) * .02, .08 * harp(mtof(m)))
    return reverb(L, .45, 1.5)

def norm_stereo(x):
    x = x / (np.max(np.abs(x)) + 1e-9) * .89
    return np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
os.makedirs(OUT, exist_ok=True)
for name, fn in (("R1", mood_r1), ("R2", mood_r2), ("R3", mood_r3)):
    st = norm_stereo(fn())
    if FULL: wavfile.write(os.path.join(OUT, f"music_{name}.wav"), SR, (st * 32767).astype(np.int16))
    ex = st[int(X0 * SR):int((X0 + XD) * SR)].copy()
    f = int(.25 * SR); ex[:f] *= np.linspace(0, 1, f)[:, None]; g = int(.6 * SR); ex[-g:] *= np.linspace(1, 0, g)[:, None]
    ex = ex / (np.max(np.abs(ex)) + 1e-9) * .89
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (ex * 32767).astype(np.int16))
print("chord changes at", [round(b, 2) for b in BND])
print("excerpt", X0, "->", X0 + XD, "s;", sum(1 for t, m, _ in J.HITS if X0 <= t < X0 + XD), "hits")
