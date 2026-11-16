"""BeepMelody · wave-spectrum · RETRAVAIL r2, sound card (decision-wave-spectrum-r4).
Guillaume (15 Nov, 23:05): "... et pousser aussi le son, en restant le plus réaliste possible, ondes comprises."
Visuals chosen on r3 = A (camera travels along the spectrum). Every option keeps the channel rule: one discovery = one
audible hit, on its REAL note (pitch class of the real frequency, moved by whole octaves into hearing). What changes is
the TIMBRE (each wave sounds like its real source) and the bed:
  A · SOURCES + SYNTHWAVE : the 98 BPM synthwave bed already chosen (r1-2 = C), each wave voiced by its real source:
      radio = hiss + carrier, Sputnik = its real on/off beep, pulsar = ticks, CMB = TV-snow hiss, laser/visible = pure
      tone, X/gamma = Geiger crackle + bright tone, whale/elephant/bat = their real call shapes, gravity = chirp / swell.
  B · B-FLAT SPACE (no drums): everything sits on a low B-flat drone (the Perseus black hole's real note); each voice
      bends with a Doppler glide and pans left -> right as the camera flies past it; huge space reverb.
  C · CINEMA PULSE : 98 BPM low-string ostinato + timpani on the downbeat, the same source voices doubled by a celesta.
usage: python3 wave_spectrum_r4_sound.py <out_dir> [t0] [dur]   -> A.wav B.wav C.wav (+ .webm)
"""
import sys, os, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_spectrum as ws
from wave_spectrum import REC, RT, EV, BEAT, pitch, rpos, band, mtof, root_at

SR = 44100
rng = np.random.default_rng(7)
def lp(x, fc): return lfilter(*butter(2, min(fc, SR / 2 - 100) / (SR / 2)), x)
def hp(x, fc): return lfilter(*butter(2, fc / (SR / 2), "high"), x)
def bp(x, a, b): return hp(lp(x, b), a)
def tt(d): return np.arange(int(d * SR)) / SR
def att(x, a=0.008): return np.minimum(1, x / a)
def sine_f(f): return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, f.shape if np.ndim(f) else (1,))) / SR)

def voice(i, doppler=False):
    """The real-source sound of discovery i, on its real note (moved by whole octaves)."""
    r = REC[i]; b = band(i); lab = r["label"]; f = mtof(pitch(i)); x = tt(1.8)
    fr = np.full_like(x, f)
    if doppler: fr = f * 2 ** ((0.8 * np.tanh((0.35 - x) * 4)) / 12)   # approaching -> passing (about +-0.8 semitone)
    tone = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    if "SPUTNIK" in lab:                                  # real Sputnik signal: ~0.3 s pulses, on/off
        gate = lp(((x % 0.3) < 0.15).astype(float), 300) * (x < 1.2)
        sq = np.sign(tone) * 0.5 + tone * 0.5
        return lp(sq, 3000) * gate * 0.55
    if "PULSAR" in lab and b == "RADIO":                  # lighthouse ticks
        tk = sum(np.exp(-np.maximum(x - k * 0.33, 0) * 60) * (x >= k * 0.33) for k in range(5))
        return (tone * 0.5 + bp(rng.standard_normal(len(x)), 800, 4000) * 0.4) * tk * 0.8
    if b == "RADIO":                                      # radio: hiss + carrier (Jansky's "steady hiss", Jupiter's bursts)
        hiss = bp(rng.standard_normal(len(x)), 600, 5000) * 0.35
        if "JUPITER" in lab: hiss *= 0.4 + 0.6 * (np.sin(2 * np.pi * 7 * x) > 0.3)
        return (tone * 0.6 + hiss) * att(x, .02) * np.exp(-x * 1.6) * 0.8
    if b == "MICROWAVE":                                  # CMB / 21 cm: TV-snow hiss under a soft tone
        snow = hp(rng.standard_normal(len(x)), 2500) * 0.18
        return (tone * 0.6 + snow) * att(x, .04) * np.exp(-x * 1.4) * 0.8
    if b in ("VISIBLE LIGHT", "INFRARED", "ULTRAVIOLET"):  # light: pure tone (laser = purest, longest)
        dec = 0.7 if "LASER" in lab else 1.6
        s = tone + (0 if "LASER" in lab else 0.25 * np.sin(2 * np.pi * np.cumsum(2 * fr) / SR))
        return s * att(x) * np.exp(-x * dec) * 0.55
    if b in ("X-RAY", "GAMMA RAY"):                       # Geiger crackle + bright tone
        cl = (rng.random(len(x)) < (900 if b == "GAMMA RAY" else 400) / SR * np.exp(-x * 3)).astype(float)
        cl = hp(cl, 2000) * 3
        return (tone * np.exp(-x * 3) * 0.5 + cl) * att(x) * 0.6
    if "WHALE" in lab:                                    # humpback: slow sung glide up then down (real 400 Hz)
        g = f * 2 ** ((np.sin(np.pi * np.minimum(x / 1.4, 1)) * 3 - 1) / 12)
        s = np.sin(2 * np.pi * np.cumsum(g) / SR); s += 0.3 * np.sin(2 * np.pi * np.cumsum(2 * g) / SR)
        return s * np.minimum(1, x / .15) * np.exp(-x * 1.2) * 0.5
    if "ELEPHANT" in lab:                                 # elephant rumble: low growl, rough
        s = np.sin(2 * np.pi * np.cumsum(fr * (1 + 0.01 * np.sin(2 * np.pi * 9 * x))) / SR)
        return np.tanh(2.5 * s) * np.minimum(1, x / .1) * np.exp(-x * 1.3) * 0.5
    if "BATS" in lab:                                     # bat echolocation: FM sweeps down, fast repeats
        ph = x % 0.12; g = f * 2 ** (1 - ph / 0.06)
        return np.sin(2 * np.pi * np.cumsum(g) / SR) * np.exp(-ph * 40) * (x < 0.9) * 0.6
    if "KRAKATOA" in lab:                                 # the boom + the note
        boom = lp(rng.standard_normal(len(x)), 120) * np.exp(-x * 2.5) * 4
        return (boom + tone * 0.4) * att(x, .003) * np.exp(-x * 1.2) * 0.7
    if b == "SOUND IN SPACE GAS":                         # black hole: deep B-flat drone swell
        s = sum(np.sin(2 * np.pi * np.cumsum(fr * k) / SR) / k for k in (1, 2, 3))
        return s * np.sin(np.pi * np.minimum(x / 1.8, 1)) * 0.5
    if r["family"] == "gravity":                          # gravity: slow swell; LIGO = real chirp (35 -> 250 Hz)
        if "LIGO" in lab: return chirp() * 0.9
        return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * np.minimum(x / 1.6, 1)) * 0.6
    return tone * att(x) * np.exp(-x * 1.5) * 0.5

def chirp(f0=35, f1=250, d=0.6):                          # GW150914 at its real pitch, f ~ (tc - t)^-3/8
    x = tt(d + .3); tc = d + .002
    f = np.clip(np.where(x < d, f0 * (tc / np.maximum(tc - x, 1e-3)) ** (3 / 8), f1), f0, f1)
    a = np.where(x < d, (f / f1) ** .7, np.exp(-(x - d) * 30))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * a
    return s + 0.35 * np.tanh(3 * s)

def render(opt, t0, dur, path):
    n = int((dur + 1.5) * SR); L = np.zeros(n); R = np.zeros(n); fx = np.zeros(n)
    def put(t, x, pan=0.0, send=0.0, v=1.0):
        i = int((t - t0) * SR)
        if i >= n or i + len(x) <= 0: return
        if i < 0: x = x[-i:]; i = 0
        j = min(n, i + len(x)); x = x[:j - i] * v
        L[i:j] += x * (1 - pan) ** .5 * .9; R[i:j] += x * (1 + pan) ** .5 * .9
        if send: fx[i:j] += x * send
    win = [(t, k, kw) for t, k, kw in EV if t0 - 2 <= t < t0 + dur]
    discoveries = [(t, i) for i, t in enumerate(RT) if t0 - 1.5 <= t < t0 + dur]
    # ---- the bed ----
    if opt == "A":                                        # the 98 BPM synthwave bed already chosen (r1-2 = C)
        for t, k, kw in win:
            v = kw.get("v", .3)
            if k == "kick":
                x = tt(.35); put(t, np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 20) + 42) / SR) * np.exp(-x * 9), v=v * 1.2)
            elif k == "snare":
                x = tt(.4); put(t, lp(rng.standard_normal(len(x)), 5000) * np.exp(-x * 10), send=.6, v=v * 1.1)
            elif k == "hat":
                x = tt(.04); put(t, hp(rng.standard_normal(len(x)), 8000) * np.exp(-x * 80), pan=.3, v=v * 2.5)
            elif k == "bass":
                x = tt(BEAT / 2 * .95); f = mtof(kw["m"]); put(t, lp(2 * ((f * x) % 1) - 1, 900) * np.exp(-x * 6), pan=-.1, v=v * 2.4)
            elif k == "pad":
                d = kw["d"] + .4; x = tt(d); m0 = kw["m"] + 24
                s = sum(2 * ((mtof(m0 + iv) * x) % 1) - 1 for iv in (0, 3, 7)) / 3
                put(t, lp(s, 1000) * np.minimum(1, x / .25) * np.clip((d - x) / .4, 0, 1), send=.4, v=v)
    elif opt == "B":                                      # low B-flat drone (Perseus black hole), slow breathing
        x = tt(dur + 1.5)
        dr = sum(np.sin(2 * np.pi * mtof(m) * x + k) / (k + 1) for k, m in enumerate((34, 46, 53, 58)))
        dr *= 0.6 + 0.4 * np.sin(2 * np.pi * x / 6.0)
        dr += lp(rng.standard_normal(len(x)), 400) * 0.25                # deep-space air
        put(t0, dr * np.minimum(1, x / 1.0), send=.3, v=.12)
    elif opt == "C":                                      # cinema: low-string 8th ostinato + timpani on beat 1
        nb0 = int(np.floor(t0 / BEAT)); nb1 = int(np.ceil((t0 + dur) / BEAT))
        for b in range(nb0, nb1 + 1):
            t = b * BEAT; m = root_at(t) + 12
            for q in range(2):
                x = tt(BEAT / 2 * .98); f = mtof(m + (0 if q == 0 else 7 * (b % 2 == 1)))
                s = sum(2 * ((f * dt * x) % 1) - 1 for dt in (1, 1.004, .996)) / 3
                put(t + q * BEAT / 2, lp(s, 700) * np.minimum(1, x / .02) * np.exp(-x * 3), send=.3, v=.16)
            if b % 4 == 0:
                x = tt(1.2); put(t, np.sin(2 * np.pi * np.cumsum(mtof(root_at(t)) * (1 + .1 * np.exp(-x * 12))) / SR) *
                                  np.exp(-x * 3) + lp(rng.standard_normal(len(x)), 300) * np.exp(-x * 20), send=.4, v=.45)
    # ---- the discoveries (one hit each, on its real note) ----
    for t, i in discoveries:
        pan = rpos(i) * 1.2 - .6
        if opt == "B":
            v = voice(i, doppler=True)
            put(t, v, pan=0, send=.9, v=.9)                               # centre part
            put(t, v * 0.6, pan=float(np.clip(pan + .3, -1, 1)), send=.5)  # trail drifts toward the travel direction
        else:
            put(t, voice(i), pan=pan, send=.6, v=.95)
        if opt == "C":                                    # celesta doubles the real note
            x = tt(1.2); f = mtof(pitch(i) + 12)
            put(t, (np.sin(2 * np.pi * f * x) + .3 * np.sin(2 * np.pi * 4 * f * x) * np.exp(-x * 9)) * np.exp(-x * 3.5) * att(x, .002),
                pan=-pan * .5, send=.7, v=.18)
    # ---- space / room reverb ----
    taps = [(.031, .5), (.047, .45), (.071, .4), (.113, .35), (.167, .3), (.263, .25), (.347, .2), (.461, .15), (.613, .1)]
    if opt == "B": taps += [(.83, .12), (1.1, .1), (1.45, .07), (1.9, .05)]
    out = np.zeros(n)
    for dl, g in taps:
        k = int(dl * SR); out[k:] += g * fx[:-k]
    wet = lp(out, 4000) * (0.8 if opt == "B" else 0.5)
    L += wet; R += np.roll(wet, 300)
    x = np.arange(n) / SR; fade = np.clip(x / .25, 0, 1) * np.clip((dur + .5 - x) / .8, 0, 1)
    L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.tanh(np.stack([L, R], 1) / mx * 1.3) / np.tanh(1.3) * .9
    st = st[:int((dur + .5) * SR)]
    wavfile.write(path, SR, (st * 32767).astype(np.int16)); return path

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 27.3
    dur = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
    print("window", t0, "->", t0 + dur, [REC[i]["label"] for i, t in enumerate(RT) if t0 <= t < t0 + dur])
    for o in "ABC":
        w = render(o, t0, dur, f"{out}/sound_{o}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w, "-vn", "-c:a", "libopus", "-b:a", "64k", w[:-4] + ".webm"], check=True)
        print(w)
