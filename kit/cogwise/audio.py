"""Synthesized SFX (royalty-free by construction) + final mix with the voice-over."""
import numpy as np, wave, subprocess
from scipy.signal import butter, sosfilt

SR = 44100
_rng = np.random.default_rng(4)

def _bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def _lp(x, fc): return sosfilt(butter(2, fc, 'low', fs=SR, output='sos'), x)
def db(v): return 10 ** (v / 20)

def whoosh(dur=0.45, up=True):
    n = int(dur * SR); noise = _rng.standard_normal(n)
    lo = _bp(noise, 300, 1200); hi = _bp(noise, 1500, 6000)
    k = np.linspace(0, 1, n) if up else np.linspace(1, 0, n)
    x = lo * (1 - k) + hi * k
    x *= np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return x / (np.abs(x).max() + 1e-9)

def pop(f0=900, f1=320, dur=0.09):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38)

def click():
    n = int(0.04 * SR); t = np.arange(n) / SR
    x = _rng.standard_normal(n) * np.exp(-t * 400) * 0.6 + np.sin(2*np.pi*2400*t) * np.exp(-t * 120) * 0.5
    return _bp(x, 800, 8000)

def sizzle(dur=0.7):
    n = int(dur * SR); t = np.arange(n) / SR
    e = np.minimum(t / 0.15, 1) * np.exp(-np.maximum(t - 0.15, 0) / 0.25)
    return _bp(_rng.standard_normal(n), 2000, 7000) * e

def bell(f=1568, dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for ratio, amp, dec in [(1, 1, 1.2), (2.0, .45, .7), (2.76, .35, .5), (5.4, .18, .25), (8.93, .1, .15)]:
        x += amp * np.sin(2*np.pi*f*ratio*t) * np.exp(-t / dec)
    x *= np.minimum(t / 0.003, 1)
    return x / np.abs(x).max()

def hum(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2*np.pi*55*t) + .5*np.sin(2*np.pi*110*t) + .25*np.sin(2*np.pi*165*t)
    x *= 1 + .15*np.sin(2*np.pi*3.1*t)
    x += _lp(_rng.standard_normal(n), 400) * .6
    f = min(int(.25*SR), n//2); e = np.ones(n); e[:f] = np.linspace(0, 1, f); e[-f:] = np.linspace(1, 0, f)
    return x * e / np.abs(x).max()

KINDS = {  # name -> (generator, gain dB)
    'pop': (lambda: pop(), -17), 'click': (click, -14), 'whoosh': (lambda: whoosh(.4), -19),
    'sizzle': (sizzle, -30), 'ding': (lambda: bell(2093, 1.2), -18),
}

def build_sfx(ep, out_wav):
    """Auto cues (intro pop, card whooshes, outro whoosh + bell) + episode SFX/HUM, mapped to real time."""
    N = int((ep.length + 0.5) * SR); buf = np.zeros(N)
    def put(sig, t, g):
        i = int(max(t, 0) * SR)
        if i >= N: return
        j = min(N, i + len(sig)); buf[i:j] += sig[:j-i] * db(g)
    put(pop(1200, 500, .12), 0.0, -14)
    for i, b in enumerate(ep.beats):
        if b.get('card'): put(whoosh(.4), ep.R[i] - .05, -19)
    for (td, kind) in getattr(ep.mod, 'SFX', []):
        gen, g = KINDS[kind]; put(gen(), ep.to_real(td), g)
    for (a, b) in getattr(ep.mod, 'HUM', []):
        ra, rb = ep.to_real(a), ep.to_real(b)
        if rb - ra > .6: put(hum(rb - ra), ra, -33)
    tb = ep.R[-2]
    put(whoosh(.5, False), tb + .1, -20)
    put(bell(1568), tb + .45, -13); put(bell(2093), tb + .61, -16)
    buf = np.clip(buf, -1, 1)
    with wave.open(out_wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())

def mux(video, voice, sfx_wav, out, length):
    """Voice + SFX, loudness-normalised to about -14 LUFS (YouTube/TikTok target), stereo AAC."""
    fc = (f"[1:a]aresample=44100,apad[v];[2:a]aresample=44100[s];"
          f"[v][s]amix=inputs=2:normalize=0:duration=longest,atrim=0:{length:.2f},"
          f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100,pan=stereo|c0=c0|c1=c0[a]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', voice, '-i', sfx_wav,
                    '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
