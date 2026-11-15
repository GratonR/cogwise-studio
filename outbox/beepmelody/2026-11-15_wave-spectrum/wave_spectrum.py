"""BEEPMELODY — HUMANS FOUND 147 OCTAVES OF WAVES. LISTEN TO ALL OF THEM.
Co-pilot: step 1 = A (every wave we ever found: light + sound + gravity). Rework r1 (Guillaume 15 Nov: "match the sound
with the wave", "funky 3D"): step 2 = C (synthwave 98 BPM, each wave plays its REAL note moved by whole octaves, tremolo
speed set by its frequency, octave bass follows it), step 3 = C (wireframe 3D terrain rippling at the wave's speed).
29 discoveries, 1666 -> 2023 (wave_spectrum.csv, 2 sources per row). One discovery = one note.
Note = pitch class of the real frequency; octave = place on the log ruler (A2..A5). Audible waves keep their real
octave; LIGO 2015 plays its real 35 -> 250 Hz chirp.
Scene: wireframe terrain (crests = wave speed, colour = band; gravity = space-time sheet);
bottom: the whole spectrum on a LOG frequency ruler, each find lights up its spot.
WAVE_LIGHT=1 -> clear variant (light sky, cream panels), like the altitude pilot.

    python3 wave_spectrum.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.8"))
LIGHT = os.environ.get("WAVE_LIGHT", "0") == "1"

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "wave_spectrum.csv"))))
for r in REC: r["lg"] = math.log10(float(r["freq_hz"]))
N = len(REC)
LO, HI = -15.0, 29.6                                   # log10 Hz ruler (lowest find ~1.8e-15, highest ~3.4e29)
def pos(i): return (REC[i]["lg"] - LO) / (HI - LO)
I_IR = 1; I_KRAK = 5; I_CMB = next(i for i, r in enumerate(REC) if "AFTERGLOW" in r["label"])
I_BH = next(i for i, r in enumerate(REC) if "B-FLAT" in r["label"])
I_LIGO = next(i for i, r in enumerate(REC) if "LIGO" in r["label"])
I_EHT = next(i for i, r in enumerate(REC) if "PHOTO" in r["label"])
I_TOP = next(i for i, r in enumerate(REC) if "HIGHEST" in r["label"])
I_SPUT = next(i for i, r in enumerate(REC) if "SPUTNIK" in r["label"])

def band(i):
    r = REC[i]; f = float(r["freq_hz"])
    if r["family"] == "gravity": return "GRAVITY WAVE"
    if r["family"] == "sound":
        if r["year"] == "2003": return "SOUND IN SPACE GAS"
        return "INFRASOUND" if f < 20 else ("ULTRASOUND" if f > 2e4 else "SOUND")
    if f < 1e9: return "RADIO"
    if f < 3e11: return "MICROWAVE"
    if f < 4.0e14: return "INFRARED"
    if f < 7.9e14: return "VISIBLE LIGHT"
    if f < 3e16: return "ULTRAVIOLET"
    if f < 3e19: return "X-RAY"
    return "GAMMA RAY"

# ================= palette =================
SKY = (8, 10, 26); INK = (232, 238, 255); INK2 = (132, 146, 190); CYAN = (90, 220, 255); GOLD = (255, 200, 80)
PINK = (255, 110, 200); ORNG = (255, 150, 70); PANEL = (14, 18, 44); RIM = (60, 72, 130); GRID = (34, 42, 84)
FAMC = {"light": CYAN, "sound": ORNG, "gravity": PINK}
if LIGHT:
    SKY = (214, 232, 248); PANEL = (250, 246, 234); RIM = (40, 44, 70); GRID = (170, 196, 222)
    INK_T, INK2_T, CYAN_T, GOLD_T, PINK_T = (28, 30, 52), (100, 104, 134), (20, 120, 180), (196, 120, 10), (204, 50, 140)
    FAMC = {"light": (20, 130, 200), "sound": (226, 106, 30), "gravity": (200, 50, 150)}
else:
    INK_T, INK2_T, CYAN_T, GOLD_T, PINK_T = INK, INK2, CYAN, GOLD, PINK
FAMC_T = {"light": CYAN_T, "sound": FAMC["sound"] if LIGHT else ORNG, "gravity": PINK_T}
def mix(a, b, f): return tuple(int(a[j] + (b[j] - a[j]) * f) for j in range(3))

def wave_col(i):
    """colour of the drawn wave: real hue for visible light, conventional tints elsewhere"""
    r = REC[i]; f = float(r["freq_hz"])
    if r["family"] != "light": return FAMC[r["family"]]
    if 4.0e14 <= f < 7.9e14:
        nm = 3e17 / f
        for lim, c in ((450, (150, 110, 255)), (495, (80, 140, 255)), (570, (90, 230, 110)), (590, (255, 230, 70)), (620, (255, 150, 50))):
            if nm < lim: return c
        return (255, 70, 60)
    if f < 4.0e14: return (200, 70, 60) if f > 3e11 else (255, 196, 90)       # infrared / radio-microwave
    if f < 3e16: return (190, 120, 255)                                       # UV
    return (210, 240, 255)                                                    # X / gamma

# ================= timeline (on the beat) =================
BPM = 98.0                                                      # rework r1: synthwave 98 BPM (step 2 = C)
BEAT = 60.0 / BPM
HOOK_B = 6
GAP_B = [5, 2, 2, 3, 3, 5, 3, 3, 4, 3, 3, 3, 2, 4, 2, 3, 4, 2, 3, 2, 3, 2, 5, 3, 5, 3, 2, 3]
HOLD_B = 8
OUTRO_B = 10
assert len(GAP_B) == N - 1
RT = [HOOK_B * BEAT]
for g in GAP_B: RT.append(RT[-1] + g * BEAT)
T_END = RT[-1] + HOLD_B * BEAT
I_SPLIT = 14
SC = [("hook", RT[0]), ("early", RT[I_SPLIT] - RT[0]), ("late", T_END - RT[I_SPLIT]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
TOTAL = acc_
HOOK_LO, HOOK_HI = 0.25, 0.25 + 3 * BEAT                       # hook: lowest note, then highest note

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan (rework r1, step 2 = C: "the wave sets the rhythm", synthwave 98 BPM) =================
# Each wave plays its REAL note: the pitch class of its real frequency, moved by whole octaves into hearing; the octave
# follows its place on the ruler (slow wave = low register, fast = high). Waves already audible (whale 400 Hz, neutron
# stars ~100 Hz) keep their real octave; LIGO plays its real 35 -> 250 Hz chirp. Each note flutters (tremolo) at a
# speed set by its frequency: slow wave = slow pulse, fast wave = fast flutter. Octave bass follows the last wave's note.
LGMIN, LGMAX = min(r["lg"] for r in REC), max(r["lg"] for r in REC)
PCN = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def real_midi(f): return 69 + 12 * math.log2(f / 440.0)
def note_for(i):
    m = round(real_midi(float(REC[i]["freq_hz"])))
    if 40 <= m <= 90: return m, 0
    target = 45 + (REC[i]["lg"] - LGMIN) / (LGMAX - LGMIN) * 36
    k = round((target - m) / 12); return m + 12 * k, k
def pitch(i): return note_for(i)[0]
def rpos(i): return (REC[i]["lg"] - LGMIN) / (LGMAX - LGMIN)
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def root_at(t):
    k = rec_index(t)
    i = k if k >= 0 else (I_BH if t < HOOK_HI else I_TOP)
    return 33 + (pitch(i) % 12)
def build():
    nb = int(round(TOTAL / BEAT)) + 1; s8 = BEAT / 2
    for b in range(nb):
        t = b * BEAT; p = b % 4; hook = t < RT[0]
        if t >= TOTAL - 2 * BEAT: break
        for q in range(2):
            tq = t + q * s8
            ev(tq, "bass", m=root_at(tq) + (12 if q else 0), v=0.05 if hook else (0.06 if t >= T_END else 0.08))
        if hook: continue
        if t >= T_END:
            if p == 0: ev(t, "kick", v=0.35)
            continue
        ev(t, "kick", v=0.6)
        if p in (1, 3): ev(t, "snare", v=0.22)
        ev(t + s8, "hat", v=0.035)
    ev(HOOK_LO, "wave", i=I_BH, v=0.34); ev(HOOK_HI, "wave", i=I_TOP, v=0.34)
    ev(0.0, "pad", m=root_at(0.0), d=RT[0], v=0.05)
    ev(RT[0] - 3 * BEAT, "riser", d=3 * BEAT, v=0.10)
    for i, t in enumerate(RT):
        nxt = RT[i + 1] if i + 1 < N else T_END
        ev(t, "pad", m=root_at(t), d=nxt - t, v=0.05)
        if i == I_LIGO: ev(t, "chirp", v=0.38); ev(t, "crash", v=0.16); continue
        ev(t, "wave", i=i, v=0.34 + (0.06 if i in (I_BH, I_TOP, N - 1) else 0))
        if i in (0, I_IR, I_KRAK, I_SPUT, I_CMB, I_BH, I_TOP): ev(t, "crash", v=0.14)
    ev(RT[-1], "crash", v=0.24); ev(RT[-1], "sub", v=0.4)
    for k, d in enumerate([0, 7, 12, 19, 24, 31, 36, 31, 24, 19, 12, 7]):   # the 147-octave sweep: low to high and back
        ev(RT[-1] + (k + 1) * s8, "saw", m=45 + d, v=0.14)
    ev(RT[-1] - 3 * BEAT, "riser", d=3 * BEAT, v=0.08)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")
NOTES = sorted([(t, kw["i"]) for t, k, kw in EV if k == "wave"] + [(RT[I_LIGO], I_LIGO)])

# ================= scene (rework r1, step 3 = C: wireframe 3D terrain) =================
# A wireframe sea seen in perspective ripples at the wave's speed: crests across the frame = place on the log ruler
# (slow wave = few wide crests, fast wave = many tight ones). Colour = band. Gravity waves: the sheet becomes
# space-time, rings spread out from the source (LIGO: two black holes spiral in, then the sheet rings).
# The sheet breathes on the kick (98 BPM).
_rng = np.random.default_rng(7)
STARS = [(int(_rng.integers(0, AW)), int(_rng.integers(0, AH)), int(_rng.integers(0, 3))) for _ in range(90)]
MAG = (255, 60, 200)
GX = np.linspace(-3.0, 3.0, 25); GZ = np.linspace(1.6, 7.4, 20)
BG = [mix((4, 10, 30), (40, 10, 70), min(1, y / 230)) for y in range(AH)]
def proj(x, y, z, cx=90, cy=104, f=115):
    z = max(z, 0.05); return cx + f * x / z, cy + f * y / z
def kick_pulse(T):
    ki = np.searchsorted(KICKS, T, side="right") - 1
    return math.exp(-(T - KICKS[ki]) / 0.12) if ki >= 0 else 0.0

def terrain(c, i, T, age):
    d = c.a
    for y in range(AH): d.line([0, y, AW, y], fill=BG[y])
    for (x, y, s) in STARS:
        if y < 110: d.point((x, y), fill=[(50, 60, 110), (180, 200, 255), (90, 100, 160)][s])
    r = REC[i]; col = wave_col(i); grav = r["family"] == "gravity"; lig = i == I_LIGO
    amp = 0.45 * (1 + 0.6 * math.exp(-age / 0.3)) * (1 + 0.18 * kick_pulse(T))
    if lig: amp *= 0.5 + 1.6 * ease(max(0.0, age - 1.0) / 0.5) * math.exp(-max(0.0, age - 1.6) / 1.5)
    ncyc = 1 + 4 * pos(i)
    if grav:
        R = np.hypot(GX[None, :], GZ[:, None] - 3.6)
        H = amp * 1.2 * np.sin(R * 4 - T * 6) * np.exp(-R * 0.25)
        if lig: H -= 0.5 / (R + 0.4) * (1 - ease(max(0.0, age - 1.4) / 1.0))
    else:
        H = amp * np.sin(2 * np.pi * ncyc * (GZ[:, None] - 1.6) / 5.8 * 1.5 - T * 5) * (0.7 + 0.3 * np.cos(GX[None, :] * 1.3))
    P = [[proj(x, 1.1 - H[zi, xi], z) for xi, x in enumerate(GX)] for zi, z in enumerate(GZ)]
    for zi in range(len(GZ) - 1, -1, -1):
        sh = min(1, 2.6 / GZ[zi]); cl = mix((20, 10, 50), col, min(1, sh * 1.25))
        for xi in range(len(GX) - 1): d.line([P[zi][xi], P[zi][xi + 1]], fill=cl)
        if zi > 0:
            for xi in range(len(GX)): d.line([P[zi][xi], P[zi - 1][xi]], fill=mix((20, 10, 50), MAG, sh * 0.45))
    if lig:                                                      # the two black holes spiral in, then merge
        sx, sy = proj(0, 0.55, 3.6)
        if age < 1.5:
            rad = 12 * (1 - 0.85 * ease(age / 1.5)); a = T * (3 + 14 * ease(age / 1.5))
            for s_ in (1, -1):
                x, y = sx + s_ * rad * math.cos(a), sy + s_ * rad * 0.45 * math.sin(a)
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 255))
        else:
            d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 255, 255))
    if i == I_EHT:                                               # the black-hole ring over the horizon
        cx, cy = 90, 94; d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=(255, 150, 50), width=4)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(4, 6, 20))

def scene(c, T):
    if T < RT[0]:                                               # hook: lowest then highest wave
        i = I_BH if T < HOOK_HI else I_TOP
        terrain(c, i, T, T - (HOOK_LO if i == I_BH else HOOK_HI)); return
    k = rec_index(T)
    terrain(c, k, T, T - RT[k])

# ================= spectrum ruler (bottom) =================
BX0, BX1, BY = 14, 166, 262
def xl(lg): return BX0 + (lg - LO) / (HI - LO) * (BX1 - BX0)
EM = [(-15, 2.0, None), (2.0, 9.0, (255, 196, 90)), (9.0, 11.5, (240, 160, 80)), (11.5, 14.6, (200, 70, 60)),
      (14.6, 14.9, "rainbow"), (14.9, 16.5, (190, 120, 255)), (16.5, 19.5, (170, 220, 255)), (19.5, 29.6, (230, 250, 255))]
RAIN = [(255, 70, 60), (255, 150, 50), (255, 230, 70), (90, 230, 110), (80, 140, 255), (150, 110, 255)]
def ruler(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    d.rectangle([BX0 - 8, BY - 22, BX1 + 8, BY + 20], fill=PANEL, outline=RIM)
    for a, b, col in EM:                                        # the electromagnetic part, coloured
        xa, xb = int(xl(a)), int(xl(b))
        if col is None: continue
        if col == "rainbow":
            for j in range(xb - xa + 1): d.line([xa + j, BY - 1, xa + j, BY + 2], fill=RAIN[min(5, j * 6 // max(1, xb - xa + 1))])
        else: d.rectangle([xa, BY - 1, xb, BY + 2], fill=mix(PANEL, col, 0.55))
    d.rectangle([BX0, BY + 3, BX1, BY + 3], fill=RIM)
    for lg in range(-15, 30, 5):
        xx = int(xl(lg)); d.line([xx, BY + 4, xx, BY + 5], fill=RIM)
    shown = [j for j in range(k + 1)]
    if T < RT[0]: shown = [I_BH] + ([I_TOP] if T >= HOOK_HI else [])
    for j in shown:
        xx = int(xl(REC[j]["lg"])); col = FAMC[REC[j]["family"]]
        hi = (j == k and T >= RT[0] and T - RT[k] < 0.5) or (T < RT[0])
        d.rectangle([xx - 1, BY - 6, xx, BY - 3], fill=(255, 255, 255) if hi and not LIGHT else col)
        if hi: d.line([xx, BY - 14, xx, BY - 7], fill=col)
    if k == N - 1 and T >= RT[-1]:                              # the full span: 147 octaves
        a = ease((T - RT[-1]) / 1.0); x0, x1 = int(xl(REC[I_BH]["lg"])), int(xl(REC[I_TOP]["lg"]))
        d.line([x0, BY - 10, int(lerp(x0, x1, a)), BY - 10], fill=GOLD_T)
    text(W, BX0 * 2 - 6, (BY - 21) * 2, "WAVES PER SECOND (LOG)", fill=INK2_T)
    text(W, BX1 * 2 + 6, (BY - 21) * 2, "SLOW TO FAST", fill=INK2_T, align="r")
    for lg, lab, al in ((-15, "10^-15 HZ", "l"), (0, "1 HZ", "c"), (14.7, "LIGHT", "c"), (29.6, "10^29 HZ", "r")):
        text(W, int(xl(lg) * 2), (BY + 6) * 2, lab, fill=INK2_T, align=al)

# ================= HUD, banners, footer =================
def hud(c, T, i=None):
    W = c.t; k = rec_index(T) if i is None else i; r = REC[k]; age = T - RT[k] if i is None else 1
    W.rectangle([16, 18, 344, 122], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=RIM); W.rectangle([16, 121, 344, 122], fill=RIM)
    fc = FAMC_T[r["family"]]
    text(W, 28, 22, r["year"] + " · " + band(k), fill=fc)
    text(W, 334, 22, f"{k + 1}/{N}", fill=INK2_T, align="r")
    val = r["shown"]; assert len(val) <= 19, val
    text(W, 28, 44, val, size=40, fill=(GOLD_T if age < 0.25 else INK_T))
    text(W, 28, 92, r["note"], fill=INK2_T)
    W.rectangle([16, 128, 344, 152], fill=PANEL); W.rectangle([16, 128, 19, 152], fill=fc)
    assert len(r["label"]) <= 38, r["label"]
    text(W, 28, 131, r["label"], fill=INK_T)

BANNERS = {I_IR: ("INVISIBLE LIGHT", "THE FIRST WAVE OUR EYES CAN'T SEE"),
           I_KRAK: ("ONE BOOM, 7 PASSES", "BAROMETERS WORLDWIDE LOGGED IT"),
           I_SPUT: ("BEEP", "THE FIRST SOUND OF THE SPACE AGE"),
           I_CMB: ("THE BIG BANG'S GLOW", "LIGHT FROM 13.8 BILLION YEARS AGO"),
           I_BH: ("DEEPEST NOTE EVER", "B-FLAT, 57 OCTAVES BELOW MIDDLE C"),
           I_LIGO: ("SPACE ITSELF RINGS", "THIS NOTE IS ITS REAL PITCH"),
           I_TOP: ("HIGHEST NOTE EVER", "1.4 PEV GAMMA RAY (LHAASO)"),
           N - 1: ("147 OCTAVES", "A PIANO HAS 7. WE FOUND 147.")}
BY_T = 384                                                      # banner top (text px): between scope and ruler
def box(W, xc, yb, tt, sub, accent, big=True, a=1.0):
    w = max((16 if big else 9) * len(tt) + 30, 8 * len(sub) + 30); hgt = 62 if big else 42
    x0, x1 = xc - w / 2, xc + w / 2
    W.rectangle([x0, yb, x1, yb + hgt], fill=PANEL)
    W.rectangle([x0, yb, x1, yb + 2], fill=accent); W.rectangle([x0, yb + hgt - 1, x1, yb + hgt], fill=RIM)
    text(W, xc, yb + 4, tt, size=40 if big else 20, fill=INK_T, align="c")
    if a > 0.2 and sub: text(W, xc, yb + (40 if big else 22), sub, fill=accent, align="c")
def banner(c, T):
    k = rec_index(T)
    if k < 0 or k not in BANNERS: return
    W = c.t; a = T - RT[k]
    hold = (HOLD_B if k == N - 1 else min(5, GAP_B[k])) * BEAT * 0.95
    if not (0.06 < a < hold): return
    tt, sub = BANNERS[k]
    box(W, 180, BY_T, tt, sub, FAMC_T[REC[k]["family"]] if k != N - 1 else GOLD_T, True, a)

def footer(c, T):
    W = c.t
    W.rectangle([0, 600, 360, 640], fill=PANEL); W.rectangle([0, 600, 360, 601], fill=RIM)
    text(W, 10, 604, "EVERY BEEP", fill=INK2_T); text(W, 10, 620, "= A WAVE WE FOUND", fill=CYAN_T)
    text(W, 350, 604, "HIGHER NOTE", fill=INK2_T, align="r"); text(W, 350, 620, "= FASTER WAVE", fill=GOLD_T, align="r")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); scene(c, T); ruler(c, T)
    return c

def sc_hook(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 160], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=RIM); W.rectangle([16, 159, 344, 160], fill=RIM)
    text(W, 28, 22, "HUMANS FOUND", size=40, fill=INK_T)
    if t > 0.2: text(W, 28, 58, "147 OCTAVES", size=40, fill=GOLD_T)
    if t > 0.45: text(W, 28, 94, "OF WAVES", size=40, fill=INK_T)
    if t > 0.8: text(W, 28, 134, "LISTEN TO ALL OF THEM", fill=CYAN_T)
    i = I_BH if T < HOOK_HI else I_TOP
    if t > 0.25:
        lab = "LOWEST: " + REC[i]["shown"] if i == I_BH else "HIGHEST: " + REC[i]["shown"]
        box(W, 180, BY_T, lab, REC[i]["label"], FAMC_T[REC[i]["family"]], False, 1)
    footer(c, T)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T); footer(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T_END); W = c.t
    W.rectangle([0, 0, 360, 600], fill=PANEL); W.rectangle([16, 40, 344, 42], fill=GOLD_T)
    text(W, 180, 52, "1666 TO 2023 · 29 BEEPS", fill=INK2_T, align="c")
    rows = [("147 OCTAVES", "LOWEST TO HIGHEST WAVE", GOLD_T), ("~2×10^-15 HZ", "BLACK HOLE B-FLAT · 2003", FAMC_T["sound"]),
            ("~3×10^29 HZ", "LHAASO GAMMA RAY · 2021", CYAN_T), ("35 TO 250 HZ", "LIGO CHIRP · REAL PITCH", PINK_T)]
    for j, (a, b, col) in enumerate(rows):
        if t > 0.3 + j * 0.45:
            text(W, 28, 84 + j * 56, a, size=40, fill=col); text(W, 332, 116 + j * 56, b, fill=INK_T, align="r")
    if t > 2.2: text(W, 180, 330, "(EST.) = ESTIMATED FREQUENCY", fill=INK2_T, align="c")
    if t > 2.6:
        W.rectangle([40, 440, 320, 441], fill=INK2_T)
        text(W, 180, 448, "DATA: NASA, NIST, NRAO, NOBELPRIZE.ORG,", fill=INK2_T, align="c")
        text(W, 180, 466, "LIGO/CALTECH, CHANDRA, ESO/EHT,", fill=INK2_T, align="c")
        text(W, 180, 484, "LHAASO (NATURE 2021), NANOGRAV 2023", fill=INK2_T, align="c")
        text(W, 180, 502, "+ ORIGINAL PAPERS", fill=INK2_T, align="c")
    return c

SCENEFN = {"hook": sc_hook, "early": sc_main("early"), "late": sc_main("late"), "outro": sc_outro}

def compose(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt)
    tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose(SCENEFN[name](t))
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    z = 1.0 + 0.008 * kp * FXK
    if abs(T - RT[-1]) < 0.4: z += 0.03 * FXK * math.exp(-abs(T - RT[-1]) / 0.12)
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if name in ("early", "late") and k >= 0 and T - RT[k] < 0.08:
        fr = np.minimum(255, fr.astype(np.int16) + int(40 * FXK * (1 - (T - RT[k]) / 0.08))).astype(np.uint8)
    if name == "hook" and (abs(t - HOOK_LO) < 0.08 or abs(t - HOOK_HI) < 0.08):
        fr = np.minimum(255, fr.astype(np.int16) + int(30 * FXK)).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(SKY) * f).astype(np.uint8)
    return fr

# ================= audio (rework r1, step 2 = C: synthwave 98 BPM, full length) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n); fx = np.zeros(n)
    rng = np.random.default_rng(11)
    def lp(x, fc): return lfilter(*butter(2, min(fc, SR / 2 - 100) / (SR / 2)), x)
    def hp(x, fc): return lfilter(*butter(2, fc / (SR / 2), "high"), x)
    def tt(d): return np.arange(int(d * SR)) / SR
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fx, i, x * send)
    def saw3(f, x): return sum(2 * ((f * dt * x) % 1) - 1 for dt in (1, 1.006, .994)) / 3
    def wave_note(i):
        f = mtof(pitch(i)); r = rpos(i); x = tt(1.6)
        if REC[i]["family"] == "sound":                         # sound waves: a sung glide (the whale is its real pitch)
            s = np.sin(2 * np.pi * np.cumsum(f * (0.85 + .15 * np.minimum(1, x / .5))) / SR)
            s = (s + 0.3 * np.sin(2 * np.pi * np.cumsum(2 * f * (0.85 + .15 * np.minimum(1, x / .5))) / SR)) * np.exp(-x * 1.6) * .5
            return s * np.minimum(1, x / .01)
        rate = 2 + 22 * r                                       # slow wave = slow pulse, fast wave = fast flutter
        gate = .5 + .5 * np.sign(np.sin(2 * np.pi * rate * x))
        g = lp(gate, 200)                                       # soften clicks
        return lp(saw3(f, x), 2500 + 4000 * r) * g * np.minimum(1, x / .01) * np.exp(-x * 1.5) * .35
    def chirp(f0=35, f1=250, d=0.6):                              # GW150914 at real pitch, f ~ (tc - t)^-3/8
        m_ = int((d + .25) * SR); x = np.arange(m_) / SR; tc = d + .002
        f = np.clip(np.where(x < d, f0 * (tc / np.maximum(tc - x, 1e-3)) ** (3 / 8), f1), f0, f1)
        a = np.where(x < d, (f / f1) ** .7, np.exp(-(x - d) * 30))
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * a
        return s + 0.35 * np.tanh(3 * s)                        # a bit of grit so phones hear the low start
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "wave":
            put(t, wave_note(kw["i"]) * v * 2.2, pan=rpos(kw["i"]) * 1.2 - .6, send=0.6)
        elif k == "chirp":
            put(t, chirp() * v * 1.5, send=0.35)
        elif k == "saw":
            x = tt(0.7); put(t, lp(saw3(mtof(kw["m"]), x), 3500) * np.exp(-x * 4) * v, pan=0.1, send=0.5)
        elif k == "bass":
            x = tt(BEAT / 2 * 0.95); f = mtof(kw["m"])
            put(t, lp(2 * ((f * x) % 1) - 1, 900) * np.exp(-x * 6) * v * 2.6, pan=-0.1)
        elif k == "pad":
            d = kw["d"] + 0.4; x = tt(d); m0 = kw["m"] + 24
            s = sum(saw3(mtof(m0 + iv), x) for iv in (0, 3, 7)) / 3
            e = np.minimum(1, x / 0.25) * np.clip((d - x) / 0.4, 0, 1)
            put(t, lp(s, 1100) * e * v, send=0.4)
        elif k == "kick":
            x = tt(0.35); put(t, np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x * 20) + 42) / SR) * np.exp(-x * 9) * v * 1.2)
        elif k == "sub":
            x = tt(1.4); put(t, np.sin(2 * np.pi * np.cumsum(55 * np.exp(-x * 3) + 33) / SR) * np.exp(-x * 2.5) * v)
        elif k == "snare":
            x = tt(0.5); put(t, lp(rng.standard_normal(len(x)), 5000) * np.exp(-x * 9) * v * 1.2, send=0.8)
        elif k == "hat":
            m_ = int(0.04 * SR); put(t, hp(rng.standard_normal(m_), 8000) * env(m_, 0.001, 0.012) * v * 2.5, pan=0.3)
        elif k == "crash":
            m_ = int(1.6 * SR); put(t, hp(rng.standard_normal(m_), 5000) * env(m_, 0.002, 0.45) * v * 0.5, send=0.2)
        elif k == "riser":
            x = tt(kw["d"]); put(t, hp(rng.standard_normal(len(x)), 2500) * (x / kw["d"]) ** 2 * v)
    out = fx.copy()                                              # big synthwave reverb + 8th-note delay
    for dl, g in [(.031, .5), (.047, .45), (.071, .4), (.113, .35), (.167, .3), (.263, .25), (.347, .2), (.461, .15), (.613, .1)]:
        k_ = int(dl * SR); out[k_:] += g * fx[:-k_]
    k_ = int(BEAT / 2 * SR); dly = np.zeros(n); dly[k_:] += fx[:-k_] * .35; dly[2 * k_:] += fx[:-2 * k_] * .15
    out = lp(out, 4000) * 0.5 + lp(dly, 3000)
    L += out; R += np.roll(out, 300)
    x = np.arange(n) / SR
    fade = np.clip((TOTAL - x) / 1.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.tanh(np.stack([L, R], 1) / mx * 1.3) / np.tanh(1.3) * 0.9
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(n / SR, 2), "s")

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    nf = int(round((START[name] + dur) * FPS)) - int(round(START[name] * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    f0 = int(round(START[name] * FPS))
    for f in range(nf): p.stdin.write(render_frame(idx, max(0.0, (f0 + f) / FPS - START[name])).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio":
        render_audio(out); sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        for i, t in enumerate(RT):
            r = REC[i]; print(f"{t:6.2f}s  lg {r['lg']:7.2f}  p{pitch(i)}  {band(i):<18} {r['shown']:<20} {r['label']}")
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(min(6, os.cpu_count() or 3)) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
