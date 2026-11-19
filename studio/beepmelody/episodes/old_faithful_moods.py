"""BeepMelody · Old Faithful · co-pilot step 2: three 8 s mood excerpts on the busiest passage
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

# A · Clear morning — airy, ~76 BPM feel, no drums: glass bell per eruption over a soft Cmaj9/Am9 pad,
#     steam swell sized by the eruption, the 108 min wait = the pad thins out, low rumble before #61
def mood_a():
    L = np.zeros(int(DUR * SR)); tt = np.arange(len(L)) / SR
    chords = [(48, 55, 62, 64, 71), (45, 52, 59, 60, 67)]
    pad = np.zeros(len(L))
    for k, ch in enumerate(chords):
        seg = (tt >= k * 3.16) & (tt < (k + 1) * 3.16) if k == 0 else (tt >= 3.16)
        pad += seg * sum(np.sin(2 * np.pi * mtof(m) * d * tt) for m in ch for d in (.997, 1.003))
    last = EV[-1]["t"]; prev = EV[-2]["t"]
    duck = np.clip(1 - .7 * np.clip((tt - prev - .4) / .8, 0, 1) + .7 * (tt >= last), .3, 1)
    L += .012 * lowpass(pad, 1600) * np.minimum(1, tt / 1.2) * duck
    hi, lo = [79, 81, 84, 86, 88], [67, 69, 72, 74, 76]
    for k, e in enumerate(EV):
        m = (lo if is_long(e) else hi)[k % 5]; f = mtof(m); n = int(2.4 * SR); x = np.arange(n) / SR
        bell = np.sin(2 * np.pi * f * x) + .35 * np.sin(2 * np.pi * f * 3.01 * x) * np.exp(-x * 8) + .15 * np.sin(2 * np.pi * f * 5.2 * x) * np.exp(-x * 14)
        put(L, e["t"], (.16 + (.05 if e["longest"] else 0)) * bell * env(n, .002, note_len(e, .35, 1.1)))
        put(L, e["t"] + .03, steam(note_len(e, .4, 1.3) * 1.4, e["n"], 1500, 8000, .028))
    n = int(1.4 * SR); x = np.arange(n) / SR   # rumble building under the record wait
    put(L, last - 1.4, .08 * lowpass(np.random.RandomState(5).randn(n), 140) * (x / 1.4) ** 2)
    return reverb(L, .5), "A"

# B · Heartbeat — warm, organic, 60 BPM heart pulse (soft hand drum lub-dub); marimba per eruption:
#     short eruption = one high note, long eruption = low note rolled (tremolo) for its duration; kalimba echo
def mood_b():
    L = np.zeros(int(DUR * SR)); beat = 1.0
    for k, b in enumerate(np.arange(.1, DUR, beat)):
        for dt, f0, g in ((0, 62, .22), (.22, 70, .13)):
            n = int(.3 * SR); x = np.arange(n) / SR
            put(L, b + dt, g * np.sin(2 * np.pi * np.cumsum(f0 * 1.6 * np.exp(-x * 20) + f0) / SR) * np.exp(-x * 11))
    for k, b in enumerate(np.arange(0, DUR, 2.0)):  # round bass F - Dm - Bb - C
        n = int(2.0 * SR); x = np.arange(n) / SR; f = mtof([41, 38, 34, 36][k % 4])
        put(L, b, .10 * np.sin(2 * np.pi * f * x) * np.exp(-x * .9))
    def marimba(f, n):
        x = np.arange(n) / SR
        return (np.sin(2 * np.pi * f * x) + .3 * np.sin(2 * np.pi * f * 4 * x) * np.exp(-x * 30)) * np.exp(-x * 7)
    hi, lo = [77, 79, 81, 84, 86], [57, 60, 62, 65, 67]
    for k, e in enumerate(EV):
        n = int(.5 * SR)
        if is_long(e):
            f = mtof(lo[k % 5]); roll = note_len(e, .3, .8); step = .075
            for j, tt in enumerate(np.arange(0, roll, step)):
                put(L, e["t"] + tt, (.17 if j == 0 else .07 * (1 - tt / roll) + .03) * marimba(f, n))
        else:
            f = mtof(hi[k % 5]); put(L, e["t"], .19 * marimba(f, n))
            x = np.arange(n) / SR
            put(L, e["t"] + .19, .05 * (np.sin(2 * np.pi * f * 2 * x) + .3 * np.sin(2 * np.pi * f * 11.8 * x) * np.exp(-x * 25)) * np.exp(-x * 9))
        if e["longest"]: put(L, e["t"], .1 * steam(1.4, 9, 300, 3000))
    return reverb(L, .25), "B"

# C · Geyser clock — fast, percussive, 124 BPM: ticking 16th hats (the Visitor Center clock), kick on the beat,
#     eruption = synth stab + steam burst snapped to the 16th grid; during the 108 min wait the drums drop out,
#     only the clock ticks, then #61 slams back with the full beat
def mood_c():
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
        saw = sum((1 / h) * np.sin(2 * np.pi * f * h * d * x) for h in range(1, 7) for d in (.996, 1.004))
        put(L, tq, (.12 + (.05 if e["longest"] else 0)) * lowpass(saw, 3500) * env(n, .003, .12 + note_len(e, 0, .25)))
        put(L, tq, steam(note_len(e, .25, .7), e["n"], 2000, 9000, .06 if is_long(e) else .035))
        if e["longest"]:
            nn = int(.8 * SR); x = np.arange(nn) / SR
            put(L, tq, .3 * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-x * 6) + 40) / SR) * np.exp(-x * 3))
    return reverb(L, .15), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
for e in EV:
    print(e["n"], f'{e["t"]:.2f}s', "wait", e["wait"], "dur", round(e["dur"], 2), "est" if e["est"] else "", "LONGEST" if e["longest"] else "")
