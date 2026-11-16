"""BeepMelody · Yellowstone wolves · REWORK (phase R) of co-pilot step 2 — Guillaume: "Pas terrible le son".
Three new 8 s mood excerpts on the busiest passage (1995 -> 2008), richer instruments than round 1
(plucked strings by physical model, layered piano, stereo strings, real chord voicings).
Same data mapping: one year = one note (pitch = wolves counted, log scale), packs = soft plucks after the note
(one per pack), drop >= 25 % = a low hit, record 2003 = accent.
Usage: python3 yellowstone_moods_r1.py <yellowstone_wolves.csv> <outdir>"""
import sys, csv, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
N = int(DUR * SR)
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
rows = [r for r in csv.DictReader(open(sys.argv[1])) if 1995 <= int(r["year"]) <= 2008]
EV, prev = [], None
for r in rows:
    w = int(r["wolves"]); p = int(r["packs"]) if r["packs"] else (EV[-1]["packs"] if EV else 0)
    EV.append(dict(year=int(r["year"]), wolves=w, packs=p, crash=prev is not None and w <= prev * 0.75))
    prev = w
WMAX = max(e["wolves"] for e in EV)
for e in EV: e["record"] = e["wolves"] == WMAX
LO, HI = math.log(20), math.log(180)
def deg(w, steps): return int(round(np.clip((math.log(w) - LO) / (HI - LO), 0, 1) * (steps - 1)))
RNG = np.random.default_rng(5)

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, fc, o=2):
    b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)

class Mix:
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N); s.fx = np.zeros(N)
    def put(s, t, x, g=1.0, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= N or i < 0: return
        j = min(N, i + len(x)); y = x[:j - i] * g
        s.L[i:j] += y * math.sqrt((1 - pan) / 2) * 1.41; s.R[i:j] += y * math.sqrt((1 + pan) / 2) * 1.41
        if send: s.fx[i:j] += y * send
    def out(s, room=0.35, tone=5000):
        def verb(x, off):
            o = np.zeros_like(x)
            for d, g in [(.071, .55), (.113, .47), (.167, .40), (.239, .33), (.311, .27), (.419, .2), (.557, .14), (.743, .09), (.97, .05)]:
                n = int((d + off) * SR); o[n:] += g * x[:-n]
            return lp(o, tone)
        L = s.L + room * verb(s.fx, 0.0); R = s.R + room * verb(s.fx, 0.011)
        fade = np.clip((DUR - np.arange(N) / SR) / 0.6, 0, 1); fade *= np.minimum(1, np.arange(N) / SR / 0.02)
        st = np.stack([L * fade, R * fade], 1)
        st = np.tanh(st / np.abs(st).max() * 1.15) ; st = st / np.abs(st).max() * 0.89
        return st

def times(bpm):  # 14 years over 0.3..7.0 s, snapped to an 8th grid
    s8 = 60 / bpm / 2
    return [round((0.3 + i * (6.7 / (len(EV) - 1))) / s8) * s8 for i in range(len(EV))]

# ---------- instruments ----------
def pluck(f, dur=1.2, bright=0.6, damp=0.996):
    """Karplus-Strong plucked string (block-vectorised)."""
    P = max(2, int(round(SR / f))); n = int(dur * SR)
    y = np.zeros(n + P + 1)
    exc = RNG.uniform(-1, 1, P + 1); exc = lp(exc, 800 + 9000 * bright, 1)
    y[:P + 1] = exc
    s = P + 1
    while s < len(y):
        L_ = min(P, len(y) - s)
        y[s:s + L_] = damp * 0.5 * (y[s - P:s - P + L_] + y[s - P - 1:s - P - 1 + L_])
        s += L_
    x = y[P + 1:P + 1 + n]
    return hp(x, 60, 1) * np.clip((dur - np.arange(n) / SR) / 0.08, 0, 1)

def piano(f, dur=2.5, v=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n); B = 0.0004
    for k in range(1, 9):
        fk = f * k * math.sqrt(1 + B * k * k)
        if fk > SR / 2.2: break
        a = (1.0 / k ** 1.1) * (0.6 + 0.4 * v)
        dec = 1.8 / (1 + 0.35 * k) * (440 / f) ** 0.25
        x += a * (np.sin(2 * np.pi * fk * t) + 0.5 * np.sin(2 * np.pi * fk * 1.0015 * t)) * np.exp(-t / dec)
    ham = lp(RNG.standard_normal(n), 3000) * np.exp(-t / 0.006) * 0.3
    return (x + ham) * np.minimum(1, t / 0.002) * np.clip((dur - t) / 0.15, 0, 1)

def strings(ms, dur, att=0.8, rel=0.8, cutoff=2200):
    n = int((dur + rel) * SR); t = np.arange(n) / SR; xl = np.zeros(n); xr = np.zeros(n)
    for m in ms:
        f = mtof(m)
        for j, d in enumerate((-0.11, -0.04, 0.03, 0.09, 0.14)):
            fd = f * 2 ** (d / 12) * (1 + 0.002 * np.sin(2 * np.pi * (4.8 + j * .3) * t + j))
            ph = np.cumsum(fd) / SR + RNG.random()
            saw = 2 * (ph % 1) - 1
            (xl if j % 2 else xr)[:] += saw
    e = np.minimum(1, t / att) * np.clip((dur + rel - t) / rel, 0, 1)
    return lp(xl, cutoff) * e, lp(xr, cutoff) * e

def horn(f, dur=1.8):
    n = int(dur * SR); t = np.arange(n) / SR
    e = np.minimum(1, t / 0.35) * np.clip((dur - t) / 0.5, 0, 1)
    fv = f * (1 + 0.004 * np.sin(2 * np.pi * 5 * t) * np.minimum(1, t / 0.6))
    ph = 2 * np.pi * np.cumsum(fv) / SR
    x = sum(np.sin(k * ph) * (e ** (1 + 0.6 * k)) / k for k in range(1, 9))
    return lp(x, 1800) * 0.8

def timp(f=49, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(mtof(f) * (1 + 0.25 * np.exp(-t / 0.05))) / SR
    body = (np.sin(ph) + 0.4 * np.sin(1.5 * ph) * np.exp(-t / 0.2)) * np.exp(-t / 0.55)
    return body + 0.4 * lp(RNG.standard_normal(n), 1200) * np.exp(-t / 0.03)

def rhodes(f, dur=1.8, v=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    I = (1.2 + 1.5 * v) * np.exp(-t / 0.25)
    x = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * t)) + 0.25 * np.sin(2 * np.pi * f * 7.1 * t) * np.exp(-t / 0.05)
    x *= 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    return x * np.exp(-t / 1.1) * np.minimum(1, t / 0.003) * np.clip((dur - t) / 0.2, 0, 1)

def glock(f, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25) + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.08)
    return x * np.exp(-t / 0.7) * np.minimum(1, t / 0.001)

def kick(v=1.0, dur=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(46 + 90 * np.exp(-t / 0.035)) / SR
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t / 0.13)) * v
def snare(v=1.0, soft=False):
    n = int(0.25 * SR); t = np.arange(n) / SR
    nz = bp(RNG.standard_normal(n), 1500 if soft else 1200, 7000) * np.exp(-t / (0.09 if soft else 0.06))
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04)
    return (nz * (0.9 if soft else 1) + (0.2 if soft else 0.6) * tone) * v
def hat(v=1.0, open_=False):
    n = int((0.25 if open_ else 0.05) * SR); t = np.arange(n) / SR
    return hp(RNG.standard_normal(n), 7000) * np.exp(-t / (0.08 if open_ else 0.012)) * v
def shaker(v=1.0):
    n = int(0.09 * SR); t = np.arange(n) / SR
    e = np.minimum(1, t / 0.02) * np.exp(-t / 0.03)
    return bp(RNG.standard_normal(n), 4000, 11000) * e * v
def lowhit(f=33, dur=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(mtof(f) * (1 + 1.2 * np.exp(-t / 0.06))) / SR) * np.exp(-t / 0.35)

def write(name, st):
    p = f"{OUT}/mood_{name}.wav"; wavfile.write(p, SR, (st * 32767).astype(np.int16)); print(p)

# ============ D · Big sky (Americana / western) — 84 BPM ============
# fingerpicked acoustic guitar (D–A–Bm–G), upright bass, shaker, soft kick; each year = a bright high guitar note,
# packs = muted harmonics; crash = low floor-tom + bass slide down; record = slide-guitar / harmonica-like long note.
def mood_d():
    bpm = 84; b = 60 / bpm; M = Mix()
    prog = [(50, [50, 57, 62, 66, 69]), (45, [45, 52, 57, 61, 64]), (47, [47, 54, 59, 62, 66]), (43, [43, 50, 55, 59, 62])]
    pattern = [0, 3, 2, 4, 1, 3, 2, 4]   # travis-like 8th pattern over the voicing
    for bar in range(int(DUR / (4 * b)) + 1):
        root, vo = prog[bar % 4]; t0 = bar * 4 * b
        M.put(t0, pluck(mtof(root - 12), 1.6, 0.35, 0.997), 0.55, pan=0.0)                       # upright bass
        M.put(t0 + 2 * b, pluck(mtof(root - 12 + 7), 1.2, 0.35, 0.997), 0.45)
        for k, idx in enumerate(pattern):
            M.put(t0 + k * b / 2, pluck(mtof(vo[idx]), 1.4, 0.55, 0.9965), 0.22 if k % 2 else 0.27, pan=-0.35, send=0.18)
        for k in range(8): M.put(t0 + k * b / 2 + (0.02 if k % 2 else 0), shaker(0.5 if k % 2 else 0.3), 0.18, pan=0.4)
        M.put(t0, kick(0.8), 0.32); M.put(t0 + 2 * b, kick(0.6), 0.25)
        M.put(t0 + b, snare(0.7, soft=True), 0.12, pan=0.1, send=0.2); M.put(t0 + 3 * b, snare(0.7, soft=True), 0.12, pan=0.1, send=0.2)
    scale = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86]  # D major pentatonic
    for e, tm in zip(EV, times(bpm)):
        m = scale[deg(e["wolves"], len(scale))]
        M.put(tm, pluck(mtof(m), 1.8, 0.85, 0.9975), 0.5 + (0.12 if e["record"] else 0), pan=0.3, send=0.3)
        M.put(tm, pluck(mtof(m + 12), 1.0, 0.9, 0.995), 0.10, pan=0.3, send=0.3)
        step = min(b / 4, 0.42 / max(1, e["packs"]))
        for k in range(min(e["packs"], 14)):
            M.put(tm + (k + 1) * step, glock(mtof(scale[(k * 2) % len(scale)] + 12), 0.5), 0.035, pan=0.6 * (-1) ** k, send=0.35)
        if e["crash"]:
            M.put(tm, timp(38, 1.4), 0.45, send=0.25)
            M.put(tm + 0.05, pluck(mtof(38), 1.4, 0.3, 0.997), 0.5)
        if e["record"]:
            M.put(tm + 0.05, horn(mtof(m), 1.6) * (1 + 0.3 * np.sin(np.arange(int(1.6 * SR)) / SR * 2 * np.pi * 5.5)), 0.13, pan=-0.2, send=0.5)
    write("d", M.out(0.3, 5000))

# ============ E · Nature documentary (cinematic) — 76 BPM ============
# stereo string section Dm–Bb–F–C, piano note per year (warm, layered), pizzicato = packs,
# timpani on crashes, French-horn swell on the 2003 record.
def mood_e():
    bpm = 76; b = 60 / bpm; M = Mix()
    prog = [[38, 50, 57, 62, 65], [34, 46, 53, 58, 62], [41, 48, 53, 57, 60], [36, 48, 55, 60, 64]]
    for bar in range(int(DUR / (4 * b)) + 1):
        t0 = bar * 4 * b
        l, r = strings(prog[bar % 4][1:], 4 * b, att=0.6, rel=0.7, cutoff=1900 + 500 * min(bar, 2))
        i = int(t0 * SR); j = min(N, i + len(l))
        if i < N:
            M.L[i:j] += 0.050 * l[:j - i]; M.R[i:j] += 0.050 * r[:j - i]; M.fx[i:j] += 0.02 * (l + r)[:j - i]
        M.put(t0, lp(strings([prog[bar % 4][0]], 4 * b, 0.3, 0.6, 600)[0], 400), 0.14)   # celli/basses
        for k in range(4): M.put(t0 + k * b, kick(0.5, 0.3), 0.10 if k % 2 == 0 else 0.0)
    scale = [62, 64, 65, 67, 69, 72, 74, 76, 77, 79, 81, 84]  # D minor/F major colours
    for e, tm in zip(EV, times(bpm)):
        m = scale[deg(e["wolves"], len(scale))]
        M.put(tm, piano(mtof(m), 2.6, 0.9), 0.30 + (0.08 if e["record"] else 0), pan=0.15, send=0.35)
        M.put(tm, piano(mtof(m - 12), 2.6, 0.6), 0.12, pan=-0.1, send=0.3)
        step = min(b / 4, 0.45 / max(1, e["packs"]))
        for k in range(min(e["packs"], 14)):
            M.put(tm + (k + 1) * step, pluck(mtof(scale[(k * 3) % 7] + 12), 0.35, 0.45, 0.985), 0.12, pan=0.55 * (-1) ** k, send=0.3)
        if e["crash"]:
            M.put(tm, timp(38, 1.8), 0.55, send=0.3); M.put(tm + 0.12, timp(38, 1.2), 0.25, send=0.3)
        if e["record"]:
            M.put(tm, horn(mtof(57), 2.2), 0.20, pan=-0.25, send=0.6); M.put(tm, horn(mtof(62), 2.2), 0.16, pan=0.25, send=0.6)
            M.put(tm, hat(0.6, True), 0.15, send=0.4)
    write("e", M.out(0.5, 4500))

# ============ F · Lo-fi wilderness (chill, swung) — 86 BPM ============
# Rhodes chords Fmaj7–Em7–Dm7–Cmaj9, swung boom-bap drums, round sub bass, vinyl crackle + soft wind;
# each year = a glockenspiel bell, packs = little Rhodes plucks, crash = tape-stop low hit, record = bell chord + swell.
def mood_f():
    bpm = 86; b = 60 / bpm; M = Mix(); sw = 0.12 * b
    prog = [(41, [53, 57, 60, 64]), (40, [52, 55, 59, 62]), (38, [50, 53, 57, 60]), (36, [52, 55, 59, 62])]
    for bar in range(int(DUR / (4 * b)) + 1):
        root, ch = prog[bar % 4]; t0 = bar * 4 * b
        for k, m in enumerate(ch): M.put(t0 + k * 0.012, rhodes(mtof(m), 4 * b + 0.3, 0.5), 0.07, pan=-0.3 + 0.2 * k, send=0.25)
        n = int(3 * b * SR); t = np.arange(n) / SR
        M.put(t0, np.tanh(1.3 * np.sin(2 * np.pi * mtof(root - 12) * t)) * np.exp(-t / 1.2) * np.minimum(1, t / 0.01), 0.30)
        M.put(t0 + 2.5 * b + sw, np.sin(2 * np.pi * mtof(root - 12) * t[:n // 3]) * np.exp(-t[:n // 3] / 0.4), 0.18)
        for k in range(8):
            off = sw if k % 2 else 0
            M.put(t0 + k * b / 2 + off, hat(0.7 if k % 2 else 1.0), 0.06, pan=0.35)
        M.put(t0, kick(1.0), 0.42); M.put(t0 + 1.5 * b + sw, kick(0.7), 0.3)
        M.put(t0 + b, snare(1.0), 0.18, send=0.15); M.put(t0 + 3 * b, snare(1.0), 0.18, send=0.15)
    vin = hp(RNG.standard_normal(N), 1500) * 0.003
    clicks = (RNG.random(N) > 0.9996) * RNG.standard_normal(N) * 0.08
    M.L += vin + lp(clicks, 6000); M.R += vin + lp(np.roll(clicks, 50), 6000)
    scale = [65, 67, 69, 72, 74, 77, 79, 81, 84, 86, 89]  # F major pentatonic
    for e, tm in zip(EV, times(bpm)):
        m = scale[deg(e["wolves"], len(scale))]
        M.put(tm, glock(mtof(m), 1.8), 0.30 + (0.06 if e["record"] else 0), pan=0.2, send=0.4)
        step = min(b / 4, 0.42 / max(1, e["packs"]))
        for k in range(min(e["packs"], 14)):
            M.put(tm + (k + 1) * step, rhodes(mtof(scale[(k * 2) % 6]), 0.4, 0.3), 0.035, pan=-0.5 * (-1) ** k, send=0.3)
        if e["crash"]:
            n = int(0.9 * SR); t = np.arange(n) / SR
            M.put(tm, np.sin(2 * np.pi * np.cumsum(mtof(41) * np.exp(-t / 0.5)) / SR) * np.exp(-t / 0.4), 0.45)
        if e["record"]:
            for k, d in enumerate((0, 4, 7, 12)): M.put(tm + k * 0.06, glock(mtof(m - 12 + d), 1.8), 0.10, send=0.6)
    write("f", M.out(0.35, 4200))

if __name__ == "__main__":
    for k in (sys.argv[3:] or ["d", "e", "f"]): globals()[f"mood_{k}"]()
