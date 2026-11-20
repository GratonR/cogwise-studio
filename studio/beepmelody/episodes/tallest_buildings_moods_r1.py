"""BeepMelody · Every tallest building · RETRAVAIL r1, co-pilot step 2: three 8 s mood excerpts on the densest passage.
New clock (step 1 r1, Guillaume chose B "every floor = a tick"): empty years are skipped (">> +N YEARS" card),
each record is built floor by floor: 1 floor = 1 thirty-second note at 150 BPM (0.05 s), then the BOOM on the beat.
1,037 floors in all (CTBUH floors above ground, 2 sources each: tallest_buildings.csv).
Window = Burj Khalifa (163 floors): floors 30 -> 163 (6.7 s) then the boom + tail. Pitch climbs with the floor.
Usage: python3 tallest_buildings_moods_r1.py <outdir>"""
import sys, os, math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
BEAT = 0.4; FLOOR = BEAT / 8
DUR = 8.0
OUT = sys.argv[1]
F0, FN = 30, 163
T_BOOM = 6.8
FLOORS = [(T_BOOM - (FN - f + 1) * FLOOR, f) for f in range(F0, FN + 1)]   # floor f lands here
BEATS = [k * BEAT for k in range(int(DUR / BEAT) + 1)]
PENT = [0, 2, 4, 7, 9]
def floor_note(f, base, span=13):
    d = int(f / FN * span); return base + 12 * (d // 5) + PENT[d % 5]
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lowpass(x, fc, o=2):
    b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def highpass(x, fc, o=2):
    b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf): buf[i:j] += g * sig[:j - i]
def reverb(x, mix=.35, size=1.0):
    out = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
        n = int(d * size * SR); out[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lowpass(out, 4000)
def noise(dur, fc, dec, seed, hp=None):
    n = int(dur * SR); s = lowpass(np.random.RandomState(seed).randn(n), fc)
    if hp: s = highpass(s, hp)
    return s * np.exp(-np.arange(n) / SR * dec)
def kick(g=.26, f0=80, f1=46):
    n = int(.35 * SR); tt = np.arange(n) / SR
    return g * np.sin(2*np.pi*np.cumsum(f0*np.exp(-tt*16)+f1)/SR) * np.exp(-tt*12)
def bell(f, d=.9, idx=1.6, ratio=3.5, dur=2.4):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2*np.pi*f*tt + idx*np.exp(-tt*4)*np.sin(2*np.pi*f*ratio*tt)) * env(n, .003, d)
def marimba(f, d=.35):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + .35*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*25)) * env(n, .002, d)
def saw(f, dur, det=(.995, 1.0, 1.005)):
    n = int(dur * SR); tt = np.arange(n) / SR
    return sum(2 * ((f * d * tt) % 1) - 1 for d in det) / len(det)
def piano(f, d=.9):
    n = int(2.0 * SR); tt = np.arange(n) / SR
    s = sum((.8 ** h) * np.sin(2*np.pi*f*(h+1)*(1 + .0004*h*h)*tt) * np.exp(-tt * (1.2 + .9*h)) for h in range(8))
    return s * env(n, .003, d)
def brass(f, dur=.5):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = lowpass(saw(f, dur), 900 + 2600 * np.exp(-0)) * np.minimum(1, tt / .02) * np.exp(-tt * 3)
    return s


# A · Chantier (kept): 150 BPM straight. Floor = rivet hit, brighter as it climbs; kick + offbeat bass on the beat;
# boom = brass stab + crash + low hit.
def mood_a():
    L = np.zeros(int(DUR * SR)); roots = [36, 36, 41, 43]
    for k, b in enumerate(BEATS):
        if b >= T_BOOM: break
        put(L, b, kick(.22, 90, 50))
        r = roots[(k // 4) % 4]; nn = int(BEAT * .45 * SR); tt = np.arange(nn) / SR
        put(L, b + BEAT / 2, .07 * lowpass(saw(mtof(r), BEAT * .45), 600) * np.exp(-tt * 9))
    for tm, f in FLOORS:
        put(L, tm, noise(.025, 4000 + 60 * f, 180, f, 1800 + 15 * f), .05 + .05 * f / FN)
    for iv in (0, 4, 7):
        put(L, T_BOOM, .12 * brass(mtof(72 + iv), .9))
    put(L, T_BOOM, noise(1.2, 8000, 3, 300, 3000), .10); put(L, T_BOOM, kick(.55, 70, 30))
    return reverb(L, .18), "A"

# B · Ascenseur 8-bit: 150 BPM. Floor = square-wave blip climbing the pentatonic (like a lift going up),
# triangle bass on the beat, noise hats; boom = chord arpeggio + crash.
def square(f, dur, duty=.25):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.where((f * tt) % 1 < duty, 1.0, -1.0)
def tri(f, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    return 2 * np.abs(2 * ((f * tt) % 1) - 1) - 1
def mood_b():
    L = np.zeros(int(DUR * SR)); roots = [45, 41, 36, 43]
    for k, b in enumerate(BEATS):
        if b >= T_BOOM: break
        nn = int(BEAT * .9 * SR); tt = np.arange(nn) / SR
        put(L, b, .16 * tri(mtof(roots[(k // 4) % 4] - 12), BEAT * .9) * np.exp(-tt * 3))
        put(L, b, noise(.03, 9000, 140, 70 + k, 6000), .05 if k % 2 else .09)
    for tm, f in FLOORS:
        n = int(.045 * SR); tt = np.arange(n) / SR
        put(L, tm, .05 * square(mtof(floor_note(f, 60)), .045) * np.exp(-tt * 30))
    for j, d in enumerate((0, 7, 12, 16, 19, 24, 28, 31)):
        n = int(.18 * SR); tt = np.arange(n) / SR
        put(L, T_BOOM + j * FLOOR, .09 * square(mtof(72 + d), .18, .125) * np.exp(-tt * 8))
    put(L, T_BOOM, noise(1.0, 9000, 4, 301, 2500), .10); put(L, T_BOOM, kick(.45, 110, 40))
    return reverb(L, .12), "B"

# C · Grand chantier orchestral: 150 BPM, half-time feel. Floor = pizzicato string note climbing,
# timpani on beats 1 and 3, low string drone that swells; boom = timpani roll hit + brass chord + cymbal.
def pizz(f, d=.12):
    n = int(.25 * SR); tt = np.arange(n) / SR
    return sum((.6 ** h) * np.sin(2*np.pi*f*(h+1)*tt) for h in range(5)) * env(n, .002, d)
def timp(g=.4, f=55):
    n = int(.9 * SR); tt = np.arange(n) / SR
    return g * (np.sin(2*np.pi*f*tt*(1 + .05*np.exp(-tt*8))) + .3*noise(.9, 900, 6, 7)) * np.exp(-tt * 3.5)
def mood_c():
    L = np.zeros(int(DUR * SR)); t = np.arange(len(L)) / SR
    dr = sum(lowpass(saw(mtof(m), DUR), 1200) for m in (38, 45))
    L += .05 * dr * np.clip(t / T_BOOM, 0, 1) ** 2 * (t < T_BOOM + .05)
    for k, b in enumerate(BEATS):
        if b >= T_BOOM: break
        if k % 2 == 0: put(L, b, timp(.22 + .1 * b / T_BOOM, 49 if k % 4 else 55))
    for tm, f in FLOORS:
        put(L, tm, .06 * pizz(mtof(floor_note(f, 55))))
    for iv in (0, 7, 12, 16):
        put(L, T_BOOM, .07 * lowpass(brass(mtof(50 + iv), 1.2), 1600))
    put(L, T_BOOM, timp(.7, 44)); put(L, T_BOOM, noise(1.2, 9000, 2.5, 302, 2500), .09)
    return reverb(L, .35, 1.2), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    fade = int(.5 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_r1_{name}.wav"), SR, (st * 32767).astype(np.int16))
print(len(FLOORS), "floors, first at %.2f s, boom %.2f s" % (FLOORS[0][0], T_BOOM))
