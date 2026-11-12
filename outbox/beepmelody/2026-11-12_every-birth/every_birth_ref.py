"""BeepMelody · EVERY BIRTH · music v3 — "inspired by the original video" (Guillaume, co-pilot r1, 2026-11-12:
"Inspire toi de la vidéo originale pour le thème, le rythme et les sons").
The reference "This Melody Is Us" was scored by the shared engine pi_audio.py driven by pop4.py. This module is a pop4-shaped
event list for the SAME 272 births of every_birth.py, so the unmodified pi_audio.py renders it with the reference's own sounds:
  - every birth = the reference "bip" (short sine + 2nd harmonic, panned by longitude), at its exact real-time instant;
  - same harmony as the reference: A minor, Am–F–C–G, detuned-saw pads (RICH), triangle/pulse bass in 8ths with octave jumps;
  - same rhythm idea: tempo that climbs scene after scene (84 -> 124 BPM, 134 just before the outro), kick with sidechain
    ducking (DUCK), snare on 2 and 4, hats doubling up, reverb (REVERB), crackle at each hard cut;
  - same drama: chime + kick hit on each banner (India, China, Nigeria, USA, 362 000/day), stutter glitch into each banner,
    noise riser + tape-stop + silence gap into the outro, big A-minor chord on the last scene.
Only change vs. the reference bips: the pitch is a note of the A-minor pentatonic that belongs to the current chord
(region = register), so the births sing over the changes instead of landing at random.
Usage (from studio/this-melody-is/engine):  PYTHONPATH=../../beepmelody/episodes MOD=every_birth_ref python3 pi_audio.py <wav>"""
import math
import numpy as np
import every_birth as E

TOTAL, START = E.TOTAL, E.START
SC = [(n, d) for n, d in E.SC]
FINAL = "world"
DUCK = REVERB = RICH = True
RISE = False
SCALE = [57, 60, 62, 64, 67, 69, 72, 74]        # pop4's A minor pentatonic (bip = SCALE[r] + 12)
OUTRO_DIGITS = (0, 2, 4, 5, 7)                  # A C E A C : the closing notes, same gesture as the reference
RISER_T = START["outro"] - 1.6

def bpm(T):
    pts = [(0, 84), (START["india"], 92), (START["china"], 100), (START["africa"], 108), (START["americas"], 116),
           (START["world"], 124), (START["outro"] - 0.5, 134), (START["outro"], 84), (TOTAL, 84)]
    return float(np.interp(T, [a for a, _ in pts], [b for _, b in pts]))
def beat_times(T):
    out, t = [], 0.0
    while t < T: out.append(t); t += 60 / bpm(t)
    return out

CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]      # Am F C G (pop4)
EV, GL = [], []
def ev(t, kind, **kw): EV.append((t, kind, kw))

BEATS = beat_times(START["outro"])
def chord_at(t):
    bi = max(0, int(np.searchsorted(BEATS, t, side="right")) - 1)
    return CHORDS[(bi // 4) % 4]

# register per region: africa low, asia/americas mid, europe/oceania high (indices into SCALE)
REGIDX = {"africa": (0, 1, 2, 3, 4), "asia": (1, 2, 3, 4, 5), "americas": (2, 3, 4, 5, 6), "europe": (3, 4, 5, 6, 7), "oceania": (3, 4, 5, 6, 7)}
rs = np.random.RandomState(2023)
last = 3
for t, i, j, reg, _ in E.BIRTHS:
    pcs = {m % 12 for m in chord_at(t)}
    cand = [k for k in REGIDX[reg] if SCALE[k] % 12 in pcs] or list(REGIDX[reg])
    # small steps make a line: prefer the chord tone nearest to the previous bip, sometimes leap
    cand.sort(key=lambda k: abs(k - last))
    r = cand[0] if rs.rand() < 0.55 else cand[rs.randint(len(cand))]
    last = r
    ev(t, "bip", r=r, rate=E.RATE, lon=float(E.LON[i, j]))

for k, (n, tm) in enumerate(sorted(E.MILE_T.items(), key=lambda x: x[1])):
    ev(tm, "chime", lvl=min(5, k)); ev(tm, "kickhit")

for bi, bt in enumerate(BEATS):
    sc = E.scene_at(bt); bl = 60 / bpm(bt); pos = bi % 4
    ch = CHORDS[(bi // 4) % 4]; root = ch[0] - 12
    if sc == "intro":                          # like the reference's first eras: soft broken kick, no snare
        if pos % 2 == 0: ev(bt, "kick", v=0.30); ev(bt + bl * 0.28, "kick", v=0.20)
    else:
        ev(bt, "kick", v=0.45 if sc != "india" else 0.38)
        if sc not in ("india",) and pos in (1, 3): ev(bt, "snare", v=0.19)
        sub = 4 if sc in ("americas", "world") else 2
        for h in range(sub): ev(bt + h * bl / sub, "hat", v=0.035 if h % 2 else 0.045, open=(h == sub // 2))
        if sc == "world" and bt > START["outro"] - 2.0:          # build: snare roll into the drop
            for h in range(4): ev(bt + h * bl / 4, "snare", v=0.06 + 0.12 * h / 3)
    for h in range(2):
        if sc == "intro" and h == 1: continue
        m = root + (12 if (pos * 2 + h) % 4 == 3 else 0)
        ev(bt + h * bl / 2, "bass", m=m, d=bl / 2 * 0.9, v=0.17 if sc != "intro" else 0.11)
    if pos == 0: ev(bt, "pad", ch=ch, d=bl * 4)

# outro: the births keep coming over a soft held pad (Am -> F -> Am), no drums — "every bip was someone"
_to = START["outro"] + 1.2
for ch, d in (((57, 60, 64), 2.9), ((53, 57, 60), 2.9), ((57, 60, 64), TOTAL - _to - 5.8 + 0.4)):
    ev(_to, "pad", ch=ch, d=d); ev(_to, "bass", m=ch[0] - 12, d=d * 0.9, v=0.07); _to += 2.9

def bl_at(t): return 60 / bpm(t)
for n, tm in E.MILE_T.items():
    if n != "world": GL.append((tm - 0.2, 0.2, "stutter", bl_at(tm) / 4))
GL.append((START["world"] + 0.6 + 0.35, 0.15, "crush", 0))
GL.append((START["outro"] - 0.45, 0.45, "tapestop", 0))
GL.sort()
EV.sort(key=lambda e: e[0])
