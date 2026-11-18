"""BeepMelody · The race to the deep · co-pilot step 2: three 8 s mood excerpts on the densest passage
(1959 Trieste dives -> 1960 Challenger Deep -> 1960s breath-hold and diving-gas records).
Same data clock in all three: one unit = 0.75 s, gap rule as the pilot (same year 1 unit, <= 6 years 1.5,
<= 25 years 2, more 4). One record = one hit placed exactly on its time; each lane walks DOWN its own
ladder (deeper record = lower or equal note). Breath-hold = high voice, diving gas / suit = middle, subs = low.
Tempos chosen so every hit sits on the grid: A 80 BPM (1 unit = 1 beat), B 120 BPM (1 unit = 1.5 beats,
16th grid), C 160 BPM (1 unit = 2 beats).
Usage: python3 deep_race_moods.py <deep_race_draft.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 8.0
UNIT = 0.75
OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
REC = list(csv.DictReader(open(sys.argv[1])))
N = len(REC)
Y = [int(r["date"][:4]) for r in REC]
def gap(i):
    dy = Y[i] - Y[i - 1]
    return 1 if dy == 0 else 1.5 if dy <= 6 else 2 if dy <= 25 else 4
RT = [0.0]
for i in range(1, N): RT.append(RT[-1] + gap(i) * UNIT)
I0 = next(i for i in range(N) if Y[i] == 1959)
T0 = RT[I0] - 0.75                                  # window start (s on the data clock)
WIN = [(RT[i] - T0, i) for i in range(N) if 0 <= RT[i] - T0 < DUR - 0.4]

PENTA = [0, 3, 5, 7, 10]                            # D minor pentatonic
def deg(k): o, s = divmod(k, 5); return 50 + 12 * o + PENTA[s]   # degree 0 = D3
LANE_TOP = {"breath": 13, "suit": 9, "sub": 6}       # starting degree, then one step down per record
LANE_SPAN = {"breath": 8, "suit": 5, "sub": 7}
def pitch(i):
    ln = REC[i]["lane"]; idx = [j for j in range(N) if REC[j]["lane"] == ln]; r = idx.index(i)
    return deg(LANE_TOP[ln] - int(round(r * LANE_SPAN[ln] / max(1, len(idx) - 1))))
TRIESTE = max(range(N), key=lambda i: float(REC[i]["metres"]) if Y[i] == 1960 else 0)

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, f1, f2): b, a = butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band"); return lfilter(b, a, x)
RNG = np.random.default_rng(7)
def put(buf, t, sig, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[0] or i < 0: return
    j = min(buf.shape[0], i + len(sig)); s = sig[:j - i] * g
    buf[i:j, 0] += s * np.sqrt((1 - pan) / 2) * 1.41; buf[i:j, 1] += s * np.sqrt((1 + pan) / 2) * 1.41
def reverb(x, mix=.35, size=1.0, damp=4000):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
        n = int(d * size * SR); out[n:] += g * .6 * np.roll(x, 7 if d > .2 else 0, axis=0)[:-n]
    return (1 - mix) * x + mix * lp(out.T, damp).T
def tt(d): return np.arange(int(d * SR)) / SR

# ---- voices ----
def glass(f, d=1.6):           # breath-hold: glassy bell
    t = tt(3.0); return (np.sin(2*np.pi*f*t + 1.2*np.exp(-t*5)*np.sin(2*np.pi*f*3.0*t)) + .25*np.sin(2*np.pi*f*2*t)*np.exp(-t*2)) * env(len(t), .002, d)
def marimba(f, d=.35):         # diving gas / suit
    t = tt(1.4); return (np.sin(2*np.pi*f*t) + .45*np.sin(2*np.pi*f*4*t)*np.exp(-t*30) + .15*np.sin(2*np.pi*f*10*t)*np.exp(-t*90)) * env(len(t), .001, d)
def softsyn(f, d=.7):          # subs: soft pulse lead
    t = tt(2.0); ph = 2*np.pi*np.cumsum(f*(1+.006*np.sin(2*np.pi*5*t)*np.minimum(1, t/.3)))/SR
    return lp(np.sign(np.sin(ph))*.5 + .5*np.sin(ph), 2200) * env(len(t), .01, d)
def sonar(f, d=1.4):           # subs (mood A): sonar ping, pure sine with a slow tail
    t = tt(3.5); return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*f*2.01*t)*np.exp(-t*3)) * env(len(t), .004, d)
def bubble(f, d=.18):          # mood C: water-drop pluck, pitch sweeps up
    t = tt(.6); ph = 2*np.pi*np.cumsum(f*(1+.35*(1-np.exp(-t*25))))/SR
    return np.sin(ph) * env(len(t), .001, d)
def pluck(f, d=.22):           # mood C: short saw pluck
    t = tt(.8); ph = (f*t) % 1; return lp(2*ph - 1, 2600) * env(len(t), .001, d)
def boom(f=36.7, d=2.5):       # deepest record: sub boom
    t = tt(5.0); ph = 2*np.pi*np.cumsum(f*(1+1.5*np.exp(-t*8)))/SR
    return np.tanh(1.6*np.sin(ph)) * env(len(t), .003, d)
def kick(g=1, f1=48, dec=.14):
    t = tt(.4); return g*np.sin(2*np.pi*np.cumsum(f1+110*np.exp(-t/.035))/SR)*env(len(t), .001, dec)
def snare():
    t = tt(.28); return bp(RNG.standard_normal(len(t)), 1200, 7000)*env(len(t), .001, .08)*1.4 + .4*np.sin(2*np.pi*190*t)*env(len(t), .001, .04)
def hat(d=.016): t = tt(.08 if d < .05 else .3); return hp(RNG.standard_normal(len(t)), 8000)*env(len(t), .001, d)
def chord_pad(ms, d, g=1.0):
    t = tt(d + 1.0); e = np.minimum(1, t/.8)*np.clip((d + .8 - t)/.8, 0, 1)
    return sum(np.sin(2*np.pi*mtof(m)*t) + .5*np.sin(2*np.pi*mtof(m)*1.004*t) for m in ms) * e * g
def ep_chord(ms, d):
    t = tt(d + .4); e = env(len(t), .004, .9)*np.clip((d + .1 - t)/.1, 0, 1); s = 0
    for m in ms:
        f = mtof(m); s = s + (np.sin(2*np.pi*f*t + 1.3*np.sin(2*np.pi*f*t)*np.exp(-t/.15)))
    return s * e
def bassnote(m, d, drive=2.0):
    t = tt(d + .05); f = mtof(m); return np.tanh(drive*np.sin(2*np.pi*f*t) + .4*np.sin(4*np.pi*f*t))*env(len(t), .004, .5)*np.clip((d + .03 - t)/.04, 0, 1)

def master(buf, name, wet):
    buf = reverb(buf, **wet)
    tt_ = np.arange(buf.shape[0]) / SR
    buf *= np.clip(tt_ / .05, 0, 1)[:, None] * np.clip((DUR - tt_) / .6, 0, 1)[:, None]
    buf = buf / np.abs(buf).max() * .89
    p = os.path.join(OUT, name + ".wav"); wavfile.write(p, SR, (buf * 32767).astype(np.int16)); print(p)

# ---- A · Abyss: dark & slow, 80 BPM, no drums, drone + sonar + glass bell ----
def mood_a():
    B = 60 / 80; buf = np.zeros((int(DUR * SR), 2))
    t = tt(DUR); dr = (np.sin(2*np.pi*mtof(26)*t) + .6*np.sin(2*np.pi*mtof(33)*t*1.002) + .3*np.sin(2*np.pi*mtof(38)*t*.998)) * (1 + .25*np.sin(2*np.pi*.12*t))
    put(buf, 0, lp(dr, 300) * np.minimum(1, t/1.5), .16)
    put(buf, 0, lp(hp(RNG.standard_normal(len(t)), 200), 700) * (.5 + .5*np.sin(2*np.pi*.17*t)), .025)          # deep water hiss
    for b in range(int(DUR / B) + 1):                                                                          # heartbeat, very soft
        put(buf, b * B, kick(.5, 42, .18), .35 if b % 2 == 0 else .18)
    for k in range(0, int(DUR / B), 4): put(buf, k * B, chord_pad([50, 53, 57], 4 * B), .05)
    for tw, i in WIN:
        f = mtof(pitch(i)); ln = REC[i]["lane"]
        if i == TRIESTE: put(buf, tw, boom(), .55); put(buf, tw, sonar(mtof(pitch(i)), 2.5), .4)
        elif ln == "sub": put(buf, tw, sonar(f), .42, -.1); put(buf, tw + B, sonar(f), .12, .3)
        elif ln == "suit": put(buf, tw, lp(marimba(f, .5), 1800), .45, .25)
        else: put(buf, tw, glass(f, 2.2), .32, -.3); put(buf, tw + .75 * B, glass(f, 2.2), .08, .3)
    master(buf, "A_abyss_80", dict(mix=.5, size=1.8, damp=2500))

# ---- B · Sequel of the pilot: chill-pop 120 BPM, D minor, bell / marimba / soft synth ----
def mood_b():
    B = 60 / 120; buf = np.zeros((int(DUR * SR), 2))
    CH = [(50, 53, 57, 60), (46, 50, 53, 57), (48, 52, 55, 58), (45, 49, 52, 55)]                         # Dm7 Bbmaj7 C7 A7
    RO = [38, 34, 36, 33]
    for b in range(int(DUR / B) + 1):
        tb = b * B; bar, pos = divmod(b, 4); ch, ro = CH[bar % 4], RO[bar % 4]
        if pos == 0: put(buf, tb, ep_chord(ch, 1.4 * B), .07, -.1)
        if pos in (1, 3): put(buf, tb + B / 2, ep_chord(ch, .45 * B), .045, .1)
        put(buf, tb, bassnote(ro + (7 if pos == 2 else 0), .7 * B), .18)
        if pos in (0, 2): put(buf, tb, kick(), .55)
        if pos in (1, 3): put(buf, tb, snare(), .22)
        put(buf, tb, hat(), .07, .35); put(buf, tb + .54 * B, hat(), .05, .35)
    for tw, i in WIN:
        f = mtof(pitch(i) + 12); ln = REC[i]["lane"]
        if ln == "breath": put(buf, tw, glass(f, 1.1), .26, -.3); put(buf, tw + .75 * B, glass(f, 1.1), .07, .3)
        elif ln == "suit": put(buf, tw, marimba(f), .38, .3); put(buf, tw + .5 * B, marimba(f), .09, -.3)
        else:
            put(buf, tw, softsyn(f), .28)
            if i == TRIESTE: put(buf, tw, boom(), .4); put(buf, tw, hp(RNG.standard_normal(int(2.2*SR)), 5000)*env(int(2.2*SR), .002, .6), .12)
    master(buf, "B_pilot_120", dict(mix=.25, size=1.0, damp=4500))

# ---- C · Fast & percussive: 160 BPM breakbeat, sub bass, bubbles / plucks / stabs ----
def mood_c():
    B = 60 / 160; buf = np.zeros((int(DUR * SR), 2))
    RO = [38, 38, 34, 36]
    pat_k = [0, 2.5]; pat_s = [1, 3]
    for bar in range(int(DUR / (4 * B)) + 1):
        tb = bar * 4 * B; ro = RO[bar % 4]
        for p in pat_k: put(buf, tb + p * B, kick(1, 50, .12), .6)
        for p in pat_s: put(buf, tb + p * B, snare(), .3)
        put(buf, tb + 3.75 * B, snare(), .1)
        for h in range(8): put(buf, tb + h * B / 2, hat(.012 if h % 2 else .03), .08 if h % 2 else .05, .4)
        for k, p in enumerate([0, .75, 1.5, 2.5, 3]):
            put(buf, tb + p * B, lp(bassnote(ro + (12 if k == 2 else 0), .4 * B, 3.0), 700), .26)
    for tw, i in WIN:
        f = mtof(pitch(i) + 12); ln = REC[i]["lane"]
        if ln == "breath": put(buf, tw, bubble(f * 2), .3, -.35); put(buf, tw + B, bubble(f * 2), .1, .35)
        elif ln == "suit": put(buf, tw, pluck(f), .32, .3); put(buf, tw + B / 2, pluck(f), .1, -.3)
        else:
            for k, m in enumerate((0, 3, 7)): put(buf, tw, pluck(mtof(pitch(i) + m), .3), .22, -.2 + .2 * k)   # minor stab
            if i == TRIESTE: put(buf, tw, boom(), .5); put(buf, tw, hp(RNG.standard_normal(int(2.2*SR)), 4000)*env(int(2.2*SR), .002, .7), .16)
    master(buf, "C_breakbeat_160", dict(mix=.18, size=.8, damp=5000))

if __name__ == "__main__":
    print("window", round(T0, 2), "s ->", [(REC[i]["date"], REC[i]["lane"], round(t, 2), pitch(i)) for t, i in WIN])
    mood_a(); mood_b(); mood_c()
