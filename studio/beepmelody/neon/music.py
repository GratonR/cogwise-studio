"""Musique « d'abord » pour le moteur néon : grille de tempo, suite d'accords, instruments par rôle, batterie.
La donnée décide QUAND (quantifié à la double-croche) et QUI joue ; la grille décide QUELLE note (toujours dans l'accord)."""
import numpy as np
from neon import SR, mf

class Song:
    def __init__(self, bpm=120, prog=((57, "m"), (53, ""), (48, ""), (55, "")), bars_per_chord=2, dur=30.0):
        self.bpm = bpm; self.beat = 60 / bpm; self.step = self.beat / 4
        self.prog = prog; self.bpc = bars_per_chord; self.dur = dur
        self.buf = np.zeros((int((dur + 4) * SR), 2))
    def q(self, t): return round(t / self.step) * self.step                 # quantification à la double-croche
    def chord_at(self, t):
        i = int(t / (self.beat * 4 * self.bpc)) % len(self.prog); root, kind = self.prog[i]
        return root, [0, 3 if kind == "m" else 4, 7]
    def tone(self, t, octave=0, idx=0):
        root, iv = self.chord_at(t); return root + 12 * octave + iv[idx % 3] + 12 * (idx // 3)
    def add(self, sig, t, pan=0.0, gain=1.0):
        i = int(t * SR); j = min(len(self.buf), i + len(sig))
        if j <= i: return
        l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
        self.buf[i:j, 0] += sig[:j - i] * l * gain; self.buf[i:j, 1] += sig[:j - i] * r * gain

def _t(d): return np.arange(int(d * SR)) / SR
def lowpass(x, cut):
    a = np.exp(-2 * np.pi * cut / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def lp_fast(x, cut):
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * cut / SR); return lfilter([1 - a], [1, -a], x)

def pluck(f, d=0.5, bright=3000):
    t = _t(d); saw = 2 * ((f * t) % 1) - 1
    return lp_fast(saw, bright) * np.exp(-t * 7) * 0.5
def mallet(f, d=0.9):
    t = _t(d); return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)) * np.exp(-t * 5) * 0.45
def lead(f, d=0.6):
    t = _t(d); s = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4))
    return s * np.minimum(1, t / 0.01) * np.exp(-t * 3) * 0.35
def bass(f, d=0.45):
    t = _t(d); s = np.sin(2 * np.pi * f * t) + 0.3 * np.sign(np.sin(2 * np.pi * f * t))
    return lp_fast(s, 600) * np.exp(-t * 4) * 0.6
def gong(f, d=6.0):
    t = _t(d); parts = [(1, 1, .5), (2.0, .6, .8), (2.76, .4, 1.1), (5.4, .2, 2.0), (0.5, .5, .4)]
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for r, a, k in parts) * np.minimum(1, t / 0.01) * 0.35
def kick(d=0.35):
    t = _t(d); f = 50 + 90 * np.exp(-t * 30); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.9
def hat(d=0.06, rng=np.random.default_rng(3)):
    t = _t(d); n = rng.standard_normal(len(t)); n = n - lp_fast(n, 7000)
    return n * np.exp(-t * 60) * 0.18
def snare(d=0.2, rng=np.random.default_rng(5)):
    t = _t(d); n = rng.standard_normal(len(t)); n = n - lp_fast(n, 1500)
    return (n * 0.5 + np.sin(2 * np.pi * 190 * t) * 0.4) * np.exp(-t * 22) * 0.5
def pad_chords(song, amp=0.06):
    seg = song.beat * 4 * song.bpc; t0 = 0.0
    while t0 < song.dur:
        root, iv = song.chord_at(t0); t = _t(seg + 0.6)
        s = sum(np.sin(2 * np.pi * mf(root - 12 + k) * t) + 0.5 * np.sin(2 * np.pi * mf(root + k) * 1.003 * t) for k in iv) / 6
        env = np.minimum(1, t / 0.8) * np.minimum(1, (seg + 0.6 - t) / 0.6)
        song.add(lp_fast(s, 1800) * env * amp, t0); t0 += seg
def reverb(x, wet=0.3):
    out = x.copy()
    for d, g in [(0.029, .6), (0.043, .52), (0.067, .45), (0.101, .38), (0.149, .3), (0.211, .22), (0.293, .15)]:
        k = int(d * SR); out[k:] += x[:-k] * g * wet
    return out
def master(buf):
    y = reverb(buf); y = np.tanh(y * 1.4) / np.tanh(1.4)
    return y / max(1e-9, np.abs(y).max()) * 0.92
