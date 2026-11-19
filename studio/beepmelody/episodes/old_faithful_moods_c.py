"""BeepMelody · Old Faithful · co-pilot step 2: C-groove instrument variants (8 s) on the busiest passage
(eruptions 51 -> 61, Aug 1985: the regular short-long limp, the 43 min shortest wait (#54), then the
108 min longest wait before #61). One eruption = one hit, placed at its REAL start time (time compressed:
1 min of geyser = K s, same scale as the planned episode). Eruption duration drives the note:
long eruption = lower, longer note + bigger steam; short eruption = higher, shorter note.
Usage: python3 old_faithful_moods.py <old_faithful_draft.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
K = 0.0093          # seconds of video per minute of geyser time (~80 eruptions in ~54 s)
OUT = sys.argv[2]
rows = {int(r["n"]): r for r in csv.DictReader(open(sys.argv[1]))}
FIRST, LAST = 51, 61
EV, t = [], 0.35
for n in range(FIRST, LAST + 1):
    r = rows[n]
    if n > FIRST: t += float(r["wait_before_min"]) * K
    EV.append(dict(n=n, t=t, wait=int(r["wait_before_min"]), dur=float(r["duration_min"]),
                   est=r["duration_note"].startswith("night"), longest=int(r["wait_before_min"]) == 108))

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    tt = np.arange(n) / SR; return np.minimum(1, tt / max(a, 1e-4)) * np.exp(-tt / d)
def lowpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def bandpass(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += g * sig[:j - i]
def reverb(x, mix=.35):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
        n = int(d * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)
def is_long(e): return e["dur"] >= 3.0
def steam(length, seed, lo=800, hi=7000, gain=1.0):  # hiss that swells then fades, length ~ eruption duration
    n = int(length * SR); tt = np.arange(n) / SR
    s = bandpass(np.random.RandomState(seed).randn(n), lo, hi)
    return gain * s * np.minimum(1, tt / (.25 * length)) * np.clip((length - tt) / (.6 * length), 0, 1)
def note_len(e, a=.25, b=.85): return a + (b - a) * (e["dur"] - 1.5) / 3.8


# Step 2 redo (Guillaume: "C, autre instrument"): same C groove (124 BPM clock ticks, kick, pulsed bass,
# drums drop during the 108 min wait, #61 slams back); only the eruption voice changes.
def voice_marimba(f, n, e):
    x = np.arange(n) / SR
    return (np.sin(2*np.pi*f*x) + .3*np.sin(2*np.pi*f*4*x)*np.exp(-x*30) + .1*np.sin(2*np.pi*f*9.9*x)*np.exp(-x*60)) * np.exp(-x*(9 if not is_long(e) else 5))
def voice_bell(f, n, e):
    x = np.arange(n) / SR
    return (np.sin(2*np.pi*f*x) + .4*np.sin(2*np.pi*f*2.76*x)*np.exp(-x*6) + .2*np.sin(2*np.pi*f*5.4*x)*np.exp(-x*12)) * np.exp(-x*(3.5 if not is_long(e) else 2))
def voice_steel(f, n, e):  # steel-pan-like: inharmonic partials, quick bloom
    x = np.arange(n) / SR
    s = np.sin(2*np.pi*f*x) + .5*np.sin(2*np.pi*f*2.0*x)*np.exp(-x*5) + .35*np.sin(2*np.pi*f*3.02*x)*np.exp(-x*9) + .2*np.sin(2*np.pi*f*4.1*x)*np.exp(-x*14)
    return s * np.minimum(1, x/.006) * np.exp(-x*(6 if not is_long(e) else 3.2))
# C — fast, percussive, 124 BPM: ticking 16th hats (the Visitor Center clock), kick on the beat,
#     eruption = synth stab + steam burst snapped to the 16th grid; during the 108 min wait the drums drop out,
#     only the clock ticks, then #61 slams back with the full beat
def mood_c(voice, octave, tag):
    bpm = 124; L = np.zeros(int(DUR * SR)); s16 = 60 / bpm / 4
    last = EV[-1]["t"]; quiet0 = EV[-2]["t"] + .5
    for k, b in enumerate(np.arange(0, DUR, s16)):
        quiet = quiet0 <= b < last
        nh = int(.025 * SR); x = np.arange(nh) / SR
        put(L, b, (.05 if k % 2 == 0 else .03) * bandpass(np.random.RandomState(k).randn(nh), 4000, 12000) * np.exp(-x * 160))
        if quiet: continue
        if k % 4 == 0:
            n = int(.28 * SR); x = np.arange(n) / SR
            put(L, b, .3 * np.sin(2 * np.pi * np.cumsum(120 * np.exp(-x * 22) + 50) / SR) * np.exp(-x * 9))
        if k % 8 == 4:
            n = int(.15 * SR); x = np.arange(n) / SR
            put(L, b, .09 * bandpass(np.random.RandomState(500 + k).randn(n), 900, 6000) * np.exp(-x * 25))
        if k % 2 == 1:
            n = int(s16 * SR); x = np.arange(n) / SR; f = mtof([33, 33, 36, 31][int(b // 1.935) % 4])
            put(L, b, .07 * np.sign(np.sin(2 * np.pi * f * x)) * np.exp(-x * 14))
    hi, lo = [76, 79, 81, 84, 88], [57, 60, 64, 67, 69]
    for k, e in enumerate(EV):
        tq = round(e["t"] / s16) * s16
        f = mtof((lo if is_long(e) else hi)[k % 5]); n = int(note_len(e, .18, .5) * SR); x = np.arange(n) / SR
        f *= 2 ** octave; n = int((1.2 if is_long(e) else .7) * SR)
        put(L, tq, (.2 + (.06 if e["longest"] else 0)) * voice(f, n, e))
        if is_long(e):  # long eruption: the note repeats on 16ths for its duration (roll), like the steam keeps going
            for j, dt in enumerate(np.arange(s16, note_len(e, .2, .6), s16)):
                put(L, tq + dt, .07 * (1 - j * .2) * voice(f, n, e))
        put(L, tq, steam(note_len(e, .25, .7), e["n"], 2000, 9000, .06 if is_long(e) else .035))
        if e["longest"]:
            nn = int(.8 * SR); x = np.arange(nn) / SR
            put(L, tq, .3 * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-x * 6) + 40) / SR) * np.exp(-x * 3))
    return reverb(L, .22), tag


os.makedirs(OUT, exist_ok=True)
for voice, octv, tag in ((voice_marimba, 0, "C1_marimba"), (voice_bell, 0, "C2_cloche"), (voice_steel, 0, "C3_steeldrum")):
    x, name = mood_c(voice, octv, tag)
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
