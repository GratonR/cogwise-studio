"""BeepMelody · Chocs de pi · retravail r1, étape 2 : trois ambiances pour la piste « trois expériences ».
Extrait de 8 s = le passage le plus chargé de chaque acte (≈ 2,7 s chacun, enchaînés) :
acte 1 blocs (niveau 4 → 5), acte 2 aiguilles (fin de la rafale), acte 3 fléchettes (fin, ~700/s).
Chaque événement de pi_medley_data = un son, à son instant. Usage : python3 pi_medley_moods.py <outdir>"""
import sys, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pi_medley_data as D

SR = 44100; OUT = sys.argv[1]; DUR = 8.0; SEG = DUR / 3
WIN = [(11.6, 1), (39.0, 2), (61.0, 3)]          # (début dans la vidéo, acte)
EV = []
for k, (t0, act) in enumerate(WIN):
    for e in D.events():
        if e["act"] == act and t0 <= e["t"] < t0 + SEG:
            e = dict(e); e["tm"] = k * SEG + e["t"] - t0; EV.append(e)
N = int(DUR * SR); T = np.arange(N) / SR

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def reverb(x, mix=.3, size=1.0):
    o = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
        n = int(d * size * SR); o[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lp(o, 4000)
def train(sel, w=None):
    x = np.zeros(N)
    for e in EV:
        if sel(e): x[min(N - 1, int(e["tm"] * SR))] += 1.0 if w is None else w(e)
    k = int(.03 * SR); r = np.convolve(np.abs(x) > 0, np.ones(k), "same")
    return x / np.sqrt(np.maximum(1, r))            # le son fusionné n'explose pas, chaque coup reste là
def grain(f, dec, dur=.15, harm=(1,), a=.0005, wave="sin"):
    n = int(dur * SR); tt = np.arange(n) / SR
    if wave == "sq": s = sum(np.sign(np.sin(2 * np.pi * f * h * tt)) / (i + 1) for i, h in enumerate(harm)) * .5
    elif wave == "tri": s = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * f * tt))
    else: s = sum(np.sin(2 * np.pi * f * h * tt) / (i + 1) for i, h in enumerate(harm))
    return s * np.minimum(1, tt / a) * np.exp(-tt / dec)
def conv(tr, g): return fftconvolve(tr, g, "full")[:N]
def pitched(sel, notes_of, mk):
    """une voix par hauteur : notes_of(e) -> note MIDI ; mk(f) -> grain."""
    L = np.zeros(N); groups = {}
    for e in EV:
        if sel(e): groups.setdefault(notes_of(e), []).append(e)
    for m, es in groups.items():
        x = np.zeros(N)
        for e in es: x[min(N - 1, int(e["tm"] * SR))] += 1
        L += conv(x, mk(mtof(m)))
    k = int(.03 * SR); allx = train(lambda e: sel(e))
    return L
def gain_all(L, sel):
    x = np.zeros(N)
    for e in EV:
        if sel(e): x[min(N - 1, int(e["tm"] * SR))] += 1
    r = np.convolve(x, np.ones(int(.05 * SR)), "same") / .05
    g = 1 / np.sqrt(np.maximum(1, lp(r, 20) / 40)); return L * g
def soft(s): return np.tanh(s * 1.5) / 1.5
def put(L, t0, s):
    i = int(t0 * SR); j = min(N, i + len(s)); L[i:j] += s[:j - i]
rs = np.random.RandomState(5)
def noise(d, dec, f=None, hi=True):
    n = int(d * SR); s = rs.randn(n) * np.exp(-np.arange(n) / SR * dec)
    return (hp(s, f) if hi else lp(s, f)) if f else s
def kick(g, f0=80, f1=45, dec=13):
    m = int(.3 * SR); tt = np.arange(m) / SR
    return g * np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 18) + f1) / SR) * np.exp(-tt * dec)
PENT = [0, 2, 4, 7, 9]
def pent(i, base): return base + 12 * (i // 5) + PENT[i % 5]
A1 = lambda e: e["act"] == 1; A2x = lambda e: e["act"] == 2 and e["kind"] == "x"; A2o = lambda e: e["act"] == 2 and e["kind"] == "o"
A3i = lambda e: e["act"] == 3 and e["kind"] == "in"; A3o = lambda e: e["act"] == 3 and e["kind"] == "out"

# A · Course au ciel — clair et doux comme le pilote : cloche (blocs), marimba (aiguilles), synthé doux (fléchettes). 120 BPM, shaker + kick léger.
def mood_a():
    L = np.zeros(N); beat = .5
    for m in [62, 66, 69, 74]: L += .006 * np.sin(2 * np.pi * mtof(m) * T) * (.8 + .2 * np.sin(2 * np.pi * T / 4))
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.18, 70, 50, 16)); put(L, b + beat / 2, .03 * noise(.05, 80, 7000))
    L += .22 * conv(train(A1), grain(mtof(86), .05, .4, (1, 2.76, 5.4), .001))
    L += gain_all(.20 * pitched(A2x, lambda e: pent(int(e["y"] * 10), 62), lambda f: grain(f, .08, .4, (1, 3.93, 9.2), .001)), lambda e: e["act"] == 2)
    L += .05 * conv(train(A2o), grain(mtof(50), .01, .05))
    L += gain_all(.14 * pitched(A3i, lambda e: pent(int((e["x"] ** 2 + e["y"] ** 2) * 8), 74), lambda f: grain(f, .06, .3, (1, 2), .004)), lambda e: e["act"] == 3)
    L += .10 * conv(train(A3o), grain(mtof(50), .05, .2, (1, 2), .004))
    return reverb(soft(L), .4, 1.1), "A"

# B · Labo électro — 140 BPM, kick 4/4 + sub, clics métal (blocs), pluck synthé (aiguilles), zaps aigus/graves (fléchettes).
def mood_b():
    L = np.zeros(N); beat = 60 / 140
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(L, b, kick(.38)); put(L, b + beat / 2, .06 * noise(.04, 90, 6000))
        if k % 2: put(L, b, .07 * noise(.15, 25, 3000))
        root = [33, 33, 36, 31][(k // 4) % 4]; m = int(.25 * SR)
        put(L, b + beat / 2, .12 * lp(np.sign(np.sin(2 * np.pi * mtof(root) * np.arange(m) / SR)), 400) * np.exp(-np.arange(m) / SR * 10))
    L += .26 * conv(train(A1), grain(3200, .004, .03, (1, 1.7, 2.9)))
    L += gain_all(.20 * pitched(A2x, lambda e: pent(int(e["y"] * 10), 57), lambda f: lp(grain(f, .05, .25, (1, 2, 3, 4, 5), .001), 3500)), lambda e: e["act"] == 2)
    L += .06 * conv(train(A2o), noise(.02, 200, 5000))
    L += .16 * conv(train(A3i), grain(2400, .008, .04, (1, 1.5)))
    L += .20 * conv(train(A3o), grain(110, .03, .1))
    return reverb(soft(L), .15), "B"

# C · Arcade 8-bit — 160 BPM chiptune : blip carré (blocs), pulse 25 % (aiguilles), triangle grave / carré aigu (fléchettes).
def mood_c():
    L = np.zeros(N); beat = 60 / 160
    for k, b in enumerate(np.arange(0, DUR, beat)):
        if k % 2 == 0: put(L, b, kick(.22, 120, 60, 25)); put(L, b, .2 * noise(.06, 50, 300, hi=False))
        else: put(L, b, .09 * noise(.08, 40, 2500))
        put(L, b + beat / 2, .03 * noise(.02, 150, 8000))
        root = [45, 45, 41, 43][(k // 4) % 4]; m = int(.16 * SR)
        put(L, b, .10 * grain(mtof(root), .2, .16, wave="tri"))
    L += .16 * conv(train(A1), grain(mtof(88), .02, .06, (1,), wave="sq"))
    L += gain_all(.14 * pitched(A2x, lambda e: pent(int(e["y"] * 10), 69), lambda f: grain(f, .06, .18, (1, 2), wave="sq")), lambda e: e["act"] == 2)
    L += .04 * conv(train(A2o), noise(.015, 300, 6000))
    L += .10 * conv(train(A3i), grain(mtof(93), .015, .04, wave="sq"))
    L += .18 * conv(train(A3o), grain(mtof(45), .03, .08, wave="tri"))
    return reverb(soft(L), .12, .8), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    f = int(.4 * SR); x[-f:] *= np.linspace(1, 0, f)
    x = x / (np.max(np.abs(x)) + 1e-9) * .89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
from collections import Counter
print("événements dans l'extrait par acte :", dict(Counter(e["act"] for e in EV)))
