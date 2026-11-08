"""BeepMelody soft lead: renders the data notes of a module (P.LEAD events) with a rounded, non-strident tone and
mixes them over the backing rendered by the shared engine (pi_audio.py, unmodified).
  python3 soft_lead.py <module> <backing.wav> <music.wav> [--lead-only lead.wav]
Tone: sine + soft triangle + light 2nd harmonic, 8 ms attack, ~0.35 s decay, low-pass ~2.5 kHz, small room echo.
"""
import sys, os, wave, importlib
import numpy as np
from scipy.signal import lfilter, butter, sosfilt, fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
P = importlib.import_module(sys.argv[1])
SR = 44100

def read(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32767
    return x.reshape(-1, 2)

B = read(sys.argv[2]); N = len(B)
L = np.zeros(N); R = np.zeros(N)
SH = getattr(P, "LEAD_SHIFT", -12)
def mf(m): return 440 * 2 ** ((m - 69) / 12)
def T(d): return np.arange(int(d * SR)) / SR
def put(sig, t, gl=1.0, gr=1.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]; L[i:i + len(sig)] += sig * gl; R[i:i + len(sig)] += sig * gr

def tone(f, dur, dec):
    t = T(dur + 0.25)
    tri = 2 * np.abs(2 * ((t * f) % 1) - 1) - 1
    w = np.sin(2 * np.pi * f * t) * 0.7 + tri * 0.25 + np.sin(4 * np.pi * f * t) * 0.08
    env = np.minimum(1, t / 0.008) * np.exp(-t / dec)
    env *= np.clip((dur + 0.25 - t) / 0.05, 0, 1)
    return w * env

def note(t, m, vol, dur=0.18, dec=0.35, pan=(0.9, 0.8)):
    m = m + SH
    while m > 81: m -= 12            # never above A5 (880 Hz)
    put(tone(mf(m), dur, dec) * vol, t, *pan)

def chime(t, lvl):                    # low, short glockenspiel instead of the bright 3-partial chime
    tt = T(0.45); m = 69 + lvl
    put((np.sin(2 * np.pi * mf(m) * tt) * 0.06 + np.sin(2 * np.pi * mf(m + 12) * tt) * 0.015) * np.exp(-tt * 9)
        * np.minimum(1, tt / 0.004), t, 0.8, 0.9)

for t, k, kw in P.LEAD:
    if k == "digit": note(t, P.SCALE[kw["d"]], 0.17)
    elif k == "edigit":
        rate = kw["rate"]; dur = max(0.03, min(0.12, 0.85 / rate))
        note(t, P.SCALE[kw["d"]], 0.075, dur=dur, dec=0.09, pan=(0.8, 0.9))
    elif k == "chime": chime(t, kw["lvl"])
st = P.START["outro"]
for k, d in enumerate(getattr(P, "LEAD_OUTRO", [])[:5]):
    note(st + 0.15 + k * (0.18 + k * 0.06), P.SCALE[d], 0.14, dur=0.3, dec=0.6)

X = np.stack([L, R], 1)
sos = butter(2, 2500, "low", fs=SR, output="sos"); X = sosfilt(sos, X, axis=0)
tt = T(0.9); ir = np.random.default_rng(3).standard_normal(len(tt)) * np.exp(-tt / 0.22)
ir = lfilter([0.3], [1, -0.7], ir); ir /= np.sqrt((ir ** 2).sum())
for c in range(2): X[:, c] += fftconvolve(X[:, c], ir)[:N] * 0.18

if "--lead-only" in sys.argv:
    out = sys.argv[sys.argv.index("--lead-only") + 1]
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(X, -1, 1) * 32767).astype(np.int16).tobytes())

GAIN = float(os.environ.get("LEAD_GAIN", "2.5"))   # lead level vs the (already limited) backing
M = B * 0.82 + X * GAIN
pk = np.abs(M).max()
M = np.tanh(M / pk * 1.2) / np.tanh(1.2) * 0.92                  # gentle limiter
fade = int(0.8 * SR); M[-fade:] *= np.linspace(1, 0, fade)[:, None]
with wave.open(sys.argv[3], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((M * 32767).astype(np.int16).tobytes())
print("ok", N / SR)
