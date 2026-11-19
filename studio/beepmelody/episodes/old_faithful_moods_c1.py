"""BeepMelody · Old Faithful · co-pilot step 2c: three marimba iterations of the C groove (8 s) on the busiest passage
(eruptions 51 -> 61, Aug 1985: the regular short-long limp, the 43 min shortest wait (#54), then the
108 min longest wait before #61). One eruption = one hit, placed at its REAL start time (time compressed:
1 min of geyser = K s, same scale as the planned episode). Eruption duration drives the note:
long eruption = lower, longer note + bigger steam; short eruption = higher, shorter note.
Usage: python3 old_faithful_moods_c1.py <old_faithful_draft.csv> <outdir>"""
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



# Step 2c (Guillaume: "C1 mais itère encore"): marimba kept as the eruption voice, 124 BPM clock groove kept,
# drums drop during the 108 min wait, #61 relaunches everything. Three iterations of the marimba idea.
def marimba(f, n, decay=9.0, bright=1.0):
    x = np.arange(n) / SR
    return (np.sin(2*np.pi*f*x) + .3*bright*np.sin(2*np.pi*f*4*x)*np.exp(-x*30)
            + .1*bright*np.sin(2*np.pi*f*9.9*x)*np.exp(-x*60)) * np.minimum(1, x/.002) * np.exp(-x*decay)
def woodblock(n, f=1800):
    x = np.arange(n) / SR
    return (np.sin(2*np.pi*f*x) + .4*np.sin(2*np.pi*f*2.3*x)) * np.exp(-x*90)
def vibe(f, n):
    x = np.arange(n) / SR
    trem = 1 + .25*np.sin(2*np.pi*5.5*x)
    return (np.sin(2*np.pi*f*x) + .25*np.sin(2*np.pi*f*4*x)*np.exp(-x*8)) * trem * np.minimum(1, x/.01) * np.exp(-x*1.1)
def kick(L, b, g=.3):
    n = int(.28 * SR); x = np.arange(n) / SR
    put(L, b, g * np.sin(2 * np.pi * np.cumsum(120 * np.exp(-x * 22) + 50) / SR) * np.exp(-x * 9))
BASS = [33, 33, 36, 31]
HI, LO = [76, 79, 81, 84, 88], [57, 60, 64, 67, 69]

def groove(tick="hat", bass="square", vib=False):
    bpm = 124; L = np.zeros(int(DUR * SR)); s16 = 60 / bpm / 4
    last = EV[-1]["t"]; quiet0 = EV[-2]["t"] + .5
    for k, b in enumerate(np.arange(0, DUR, s16)):
        quiet = quiet0 <= b < last
        if tick == "hat":
            nh = int(.025 * SR); x = np.arange(nh) / SR
            put(L, b, (.05 if k % 2 == 0 else .03) * bandpass(np.random.RandomState(k).randn(nh), 4000, 12000) * np.exp(-x * 160))
        else:  # wooden clock: woodblock tick-tock (tick on 8ths, tock pitch lower)
            if k % 2 == 0: put(L, b, (.06 if k % 4 == 0 else .04) * woodblock(int(.06 * SR), 1900 if k % 4 == 0 else 1400))
            else: put(L, b, .012 * woodblock(int(.04 * SR), 2600))
        chord = int(b // 1.935) % 4
        if vib and k % 16 == 0:  # vibraphone chord bed, keeps ringing through the long wait
            for m in [[57, 60, 64, 71], [53, 57, 60, 64], [48, 52, 55, 62], [55, 59, 62, 66]][chord]:
                put(L, b, .035 * vibe(mtof(m), int(2.2 * SR)))
        if quiet: continue
        if k % 4 == 0: kick(L, b, .26 if tick == "wood" else .3)
        if k % 8 == 4:
            n = int(.15 * SR); x = np.arange(n) / SR
            put(L, b, (.06 if tick == "wood" else .09) * bandpass(np.random.RandomState(500 + k).randn(n), 900, 6000) * np.exp(-x * 25))
        if k % 2 == 1:
            n = int(s16 * SR); x = np.arange(n) / SR; f = mtof(BASS[chord])
            if bass == "square": put(L, b, .07 * np.sign(np.sin(2 * np.pi * f * x)) * np.exp(-x * 14))
            else: put(L, b, .22 * marimba(f * 2, int(.35 * SR), 7, .6))  # bass marimba, low wooden bars
    return L, s16

def eruptions(L, s16, style):
    for k, e in enumerate(EV):
        tq = round(e["t"] / s16) * s16
        m = (LO if is_long(e) else HI)[k % 5]; f = mtof(m)
        g = .2 + (.06 if e["longest"] else 0)
        n = int((1.0 if is_long(e) else .6) * SR)
        if style == "two_mallets":  # second mallet a sixth below (short) / tremolo on two bars for the whole long eruption
            put(L, tq, g * marimba(f, n)); put(L, tq, .6 * g * marimba(mtof(m - 9 if not is_long(e) else m + 4), n))
            if is_long(e):
                for j, dt in enumerate(np.arange(s16 / 2, note_len(e, .3, .9), s16 / 2)):
                    put(L, tq + dt, .09 * (1 - j / 14) * marimba(mtof(m + (4 if j % 2 == 0 else 0)), n, 12))
        else:
            put(L, tq, g * marimba(f, n, 9 if not is_long(e) else 5))
            if is_long(e):
                for j, dt in enumerate(np.arange(s16, note_len(e, .2, .6), s16)):
                    put(L, tq + dt, .07 * (1 - j * .2) * marimba(f, n, 5))
        put(L, tq, steam(note_len(e, .25, .7), e["n"], 2000, 9000, .06 if is_long(e) else .035))
        if e["longest"]:  # #61 after 108 min: low marimba chord + boom
            for mm in (45, 52, 57, 64): put(L, tq, .12 * marimba(mtof(mm), int(1.4 * SR), 3))
            nn = int(.8 * SR); x = np.arange(nn) / SR
            put(L, tq, .3 * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-x * 6) + 40) / SR) * np.exp(-x * 3))
    return L

VARIANTS = [("C1a_tout_bois", dict(tick="wood", bass="marimba"), "single"),
            ("C1b_deux_baguettes", dict(tick="hat", bass="square"), "two_mallets"),
            ("C1c_marimba_vibraphone", dict(tick="hat", bass="square", vib=True), "single")]
os.makedirs(OUT, exist_ok=True)
for tag, gk, style in VARIANTS:
    L, s16 = groove(**gk); x = reverb(eruptions(L, s16, style), .22)
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{tag}.wav"), SR, (st * 32767).astype(np.int16))
