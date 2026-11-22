"""BeepMelody · Shanks pi · co-pilot step 2: three 8 s mood excerpts on the key passage.
Decision 1/4: title A, Shanks' desk, the paper roll turns red at digit 528.
Excerpt = decimals 471 -> 527 at the act-1 speed (15 digits/s, both voices in unison),
then digit 528 alone (Shanks writes 5, true pi says 4: the two voices split), a short held silence,
then decimals 529 -> 550 at the act-2 speed (~8.2 digits/s): Shanks' voice is sour, true pi stays clean;
the lucky digits (531, 533, 540, 543) land back in unison, with a gold shimmer.
Pitch = digit (0-9) on a major scale, 1.5 octaves. One digit = one hit per voice, on its instant.
Usage: python3 shanks_pi_moods.py <shanks_pi.csv> <outdir>"""
import sys, csv, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100; DUR = 8.0; N = int(DUR * SR); T = np.arange(N) / SR
rows = {int(r["decimal"]): (int(r["shanks"]), int(r["true"])) for r in csv.DictReader(open(sys.argv[1]))}
OUT = sys.argv[2]
EV = []                                    # (t, decimal, shanks, true, phase)
for k, d in enumerate(range(471, 528)): EV.append((0.10 + k / 15, d, *rows[d], 1))
T528 = 0.10 + 57 / 15 + 0.20               # ~4.10 s
EV.append((T528, 528, *rows[528], 2))
for k, d in enumerate(range(529, 551)): EV.append((T528 + 1.0 + k / 8.2, d, *rows[d], 3))
assert EV[-1][0] < DUR - 0.2

SCALE = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]          # digit -> major-scale degree
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def reverb(x, mix=.3, size=1.0):
    o = x.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
        n = int(d * size * SR); o[n:] += g * .6 * x[:-n]
    return (1 - mix) * x + mix * lp(o, 4500)
def mix(*ss):
    n = max(len(x) for x in ss); o = np.zeros(n)
    for x in ss: o[:len(x)] += x
    return o
def put(L, t0, s):
    i = int(t0 * SR)
    if i >= N: return
    j = min(N, i + len(s)); L[i:j] += s[:j - i]
def env(n, a, dec): tt = np.arange(n) / SR; return np.minimum(1, tt / a) * np.exp(-tt / dec)
def tone(f, dur, dec, harm=((1, 1),), a=.002, cents=0.0, vib=0.0):
    n = int(dur * SR); tt = np.arange(n) / SR; f = f * 2 ** (cents / 1200)
    ph = 2 * np.pi * f * (tt + vib * np.sin(2 * np.pi * 5.5 * tt) / (2 * np.pi * 5.5))
    return sum(g * np.sin(h * ph) for h, g in harm) * env(n, a, dec)
rs = np.random.RandomState(7)
def noise(dur, dec, f=None, hi=True):
    n = int(dur * SR); s = rs.randn(n) * np.exp(-np.arange(n) / SR * dec)
    return (hp(s, f) if hi else lp(s, f)) if f else s
def kick(g, f0=80, f1=45, dec=13):
    m = int(.3 * SR); tt = np.arange(m) / SR
    return g * np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 18) + f1) / SR) * np.exp(-tt * dec)
def soft(s): return np.tanh(s * 1.4) / 1.4
def bed_mask(): # backing drops out around 528 (silence), comes back for the wrong notes
    m = np.ones(N); a, b = int((T528 - .15) * SR), int((T528 + .95) * SR)
    m[a:b] = 0.0; r = int(.08 * SR); m[a - r:a] = np.linspace(1, 0, r); m[b:b + r] = np.linspace(0, 1, r); return m

def voices(L, root, shanks_snd, true_snd, wrong_snd, lucky_snd, split_snd):
    for t, d, s, tr, ph in EV:
        ms, mt = root + SCALE[s], root + SCALE[tr]
        if ph == 1:                                   # unison: both voices, same note
            put(L, t, mix(shanks_snd(mtof(ms)), true_snd(mtof(mt))))
        elif ph == 2:
            put(L, t, split_snd(mtof(ms), mtof(mt)))
        elif s == tr:                                 # right by luck
            put(L, t, mix(shanks_snd(mtof(ms)), true_snd(mtof(mt)), lucky_snd(mtof(mt))))
        else:
            put(L, t, mix(wrong_snd(mtof(ms)), true_snd(mtof(mt))))

# A · Bureau victorien — clair, de chambre, 112 BPM. Clavecin (plume de Shanks) + célesta (vrai pi) à l'unisson,
#   nappe de cordes en ré majeur, pizzicato de basse. Après 528 : le clavecin se désaccorde (+45 cents), cloche dorée sur les chiffres justes par hasard.
def mood_a():
    L = np.zeros(N); beat = 60 / 112; mask = bed_mask(); B = np.zeros(N)
    chords = [[50, 54, 57, 62], [47, 50, 54, 59], [43, 47, 50, 55], [45, 49, 52, 57]]
    for k, b in enumerate(np.arange(0, DUR, beat)):
        ch = chords[(k // 4) % 4]
        put(B, b, .16 * tone(mtof(ch[0] - 12), .4, .18, ((1, 1), (2, .3)), .003))     # pizz bass
        if k % 4 == 0:
            for m in ch: put(B, b, .022 * tone(mtof(m), 4 * beat + .3, 3.0, ((1, 1), (2, .25), (3, .1)), .35, vib=.002))
        put(B, b + beat / 2, .02 * noise(.03, 120, 7000))
    hcd = lambda f: .11 * tone(f, .35, .12, ((1, 1), (2, .6), (3, .45), (4, .3), (5, .2)), .0008)
    cel = lambda f: .10 * tone(f * 2, .5, .25, ((1, 1), (4, .12)), .001)
    wrong = lambda f: .13 * tone(f, .4, .14, ((1, 1), (2, .6), (3, .45), (4, .3), (5, .2)), .0008, cents=45)
    lucky = lambda f: .07 * tone(f * 4, 1.0, .5, ((1, 1), (2.76, .3)), .001)
    split = lambda fs, ft: mix(.16 * tone(fs, 1.0, .4, ((1, 1), (2, .6), (3, .45), (4, .3)), .0008, cents=45),
                            .14 * tone(ft * 2, 1.0, .5, ((1, 1), (4, .12)), .001), .10 * tone(mtof(38), 1.0, .6, ((1, 1), (2, .4))))
    voices(L, 62, hcd, cel, wrong, lucky, split)
    return reverb(soft(L + B * mask), .32, 1.0), "A"

# B · Encre et doute — sombre, 72 BPM. Piano feutré à l'unisson sur un bourdon grave et une horloge qui tique ;
#   à 528 tout s'arrête sur un accord dissonant (5 contre 4), puis le piano de Shanks sonne faux (désaccordé, plus sourd), violoncelle en mineur.
def mood_b():
    L = np.zeros(N); beat = 60 / 72; mask = bed_mask(); B = np.zeros(N)
    B += .03 * np.sin(2 * np.pi * mtof(38) * T) + .015 * np.sin(2 * np.pi * mtof(45) * T)
    for k, b in enumerate(np.arange(0, DUR, beat / 2)):
        put(B, b, (.05 if k % 2 == 0 else .03) * noise(.02, 300, 2500))      # tic-tac
    cello = np.zeros(N); i0 = int((T528 + 1.0) * SR)
    for m, t0 in [(38, T528 + 1.0), (41, T528 + 2.6)]:
        put(cello, t0, .06 * tone(mtof(m), 2.0, 1.2, ((1, 1), (2, .5), (3, .3), (4, .15)), .15, vib=.004))
    piano = lambda f: .12 * tone(f, .6, .22, ((1, 1), (2, .35), (3, .12)), .002)
    right = lambda f: .07 * tone(f * 2, .5, .25, ((1, 1),), .002)
    wrong = lambda f: .13 * lp(tone(f, .6, .2, ((1, 1), (2, .5), (3, .3)), .002, cents=-38) + tone(f, .6, .2, ((1, .6),), .002, cents=22), 2500)
    lucky = lambda f: .06 * tone(f * 4, 1.0, .6, ((1, 1), (2.76, .25)), .001)
    split = lambda fs, ft: .15 * (tone(fs, 1.0, .6, ((1, 1), (2, .4)), .002, cents=-38) + tone(ft, 1.0, .6, ((1, 1), (2, .4)), .002)
                                  + tone(mtof(26), 1.0, .7, ((1, 1), (2, .5))))
    voices(L, 57, piano, right, wrong, lucky, split)
    return reverb(soft(L + B * mask + cello), .42, 1.3), "B"

# C · Machine à calculer — rapide et percussif, 128 BPM. Clic mécanique + pluck synthé (Shanks) et pluck clair (vrai pi),
#   kick 4/4, charleston ; à 528 la batterie se coupe sur un « buzz » ; les fausses notes = buzz carré saturé, le vrai pi reste propre.
def mood_c():
    L = np.zeros(N); beat = 60 / 128; mask = bed_mask(); B = np.zeros(N)
    roots = [38, 38, 34, 36]
    for k, b in enumerate(np.arange(0, DUR, beat)):
        put(B, b, kick(.34)); put(B, b + beat / 2, .05 * noise(.04, 90, 6500))
        if k % 2: put(B, b, .06 * noise(.14, 26, 2800))
        r = roots[(k // 4) % 4]; n = int(.22 * SR); tt = np.arange(n) / SR
        put(B, b + beat / 2, .09 * lp(np.sign(np.sin(2 * np.pi * mtof(r) * tt)), 500) * np.exp(-tt * 9))
    click = lambda: .05 * noise(.012, 400, 3000)
    pl = lambda f: mix(.09 * lp(tone(f, .22, .07, ((1, 1), (2, .5), (3, .33), (4, .25)), .001), 4000), click())
    tru = lambda f: .07 * tone(f * 2, .25, .08, ((1, 1), (2, .2)), .001)
    def wrong(f):
        n = int(.2 * SR); tt = np.arange(n) / SR
        return mix(.07 * np.tanh(3 * np.sign(np.sin(2 * np.pi * f * 2 ** (50 / 1200) * tt))) * np.exp(-tt * 14), click())
    lucky = lambda f: .06 * tone(f * 4, .6, .3, ((1, 1), (2.76, .3)), .001)
    split = lambda fs, ft: mix(.9 * wrong(fs), .12 * tone(ft * 2, .8, .3, ((1, 1),), .001), kick(.3, 60, 35, 6))
    voices(L, 62, pl, tru, wrong, lucky, split)
    return reverb(soft(L + B * mask), .15, .9), "C"

os.makedirs(OUT, exist_ok=True)
for fn in (mood_a, mood_b, mood_c):
    x, name = fn()
    f = int(.35 * SR); x[-f:] *= np.linspace(1, 0, f)
    x = x / (np.max(np.abs(x)) + 1e-9) * .89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(os.path.join(OUT, f"mood_{name}.wav"), SR, (st * 32767).astype(np.int16))
print("digits in excerpt:", len(EV), "| 528 at %.2f s | last at %.2f s" % (T528, EV[-1][0]),
      "| lucky:", [d for t, d, s, tr, ph in EV if ph == 3 and s == tr])
