"""BEEPMELODY — HUMANS FOUND 147 OCTAVES OF WAVES. LISTEN TO ALL OF THEM.
Co-pilot: step 1 = A (every wave we ever found: light + sound + gravity), step 2 = B (Discovery drive, 118 BPM,
16th synth-bass arpeggio Am-F-C-G, four-on-the-floor, plucks = light, marimba = sound, soft synth = gravity).
29 discoveries, 1666 -> 2023 (wave_spectrum.csv, 2 sources per row). One discovery = one note.
Pitch = log10(frequency) of the wave, 147 octaves squeezed into ~2.5 octaves (A minor pentatonic A2..G5).
LIGO 2015 is the one note played at its REAL pitch: a 35 -> 250 Hz chirp.
Scene: a scope shows the wave (light = coloured sine, sound = pressure rings, gravity = rippling space grid);
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
BPM = 118.0
BEAT = 60.0 / BPM
HOOK_B = 8
GAP_B = [6, 3, 4, 4, 4, 6, 4, 4, 5, 4, 4, 3, 3, 3, 3, 3, 4, 2, 3, 3, 3, 4, 6, 4, 6, 3, 2, 2]
HOLD_B = 10
OUTRO_B = 12
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
HOOK_LO, HOOK_HI = 0.25, 0.25 + 4 * BEAT                       # hook: lowest note, then highest note

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan (step-2 B) =================
SCALE = [45, 48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79]
def pitch(i): return SCALE[int(round(np.clip(pos(i), 0, 1) * (len(SCALE) - 1)))]
ROOTS = [33, 29, 36, 31]                                        # Am - F - C - G
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT)) + 1; s16 = BEAT / 4
    for b in range(nb):
        t = b * BEAT; bar, p = divmod(b, 4); ro = ROOTS[bar % 4]
        if t >= T_END:
            if t < TOTAL - 3 * BEAT:
                ev(t, "bass16", m=ro, open=0.5, v=0.05)
                if p == 0:
                    for j, d in enumerate((12, 19, 24, 28)): ev(t + j * s16 * 2, "pluck", m=ro + 24 + d - 12, v=0.09)
            continue
        hook = t < RT[0]
        prog = min(1.0, t / T_END)
        ev(t, "bass16", m=ro, open=(0.15 if hook else 0.2 + 0.7 * prog), v=0.05 if hook else 0.07)
        if hook:
            ev(t + BEAT / 2, "hat", v=0.025); continue
        ev(t, "kick", v=0.55)
        if p in (1, 3): ev(t, "clap", v=0.10)
        ev(t + BEAT / 2, "hat", v=0.04)
    ev(HOOK_LO, "note", i=I_BH, v=0.30); ev(HOOK_HI, "note", i=I_TOP, v=0.30)
    ev(RT[0] - 4 * BEAT, "riser", d=4 * BEAT, v=0.10)
    for i, t in enumerate(RT):
        big = i in (I_BH, I_TOP, N - 1)
        if i == I_LIGO: ev(t, "chirp", v=0.34); ev(t, "crash", v=0.16); continue
        ev(t, "note", i=i, v=0.30 + (0.08 if big else 0)); ev(t + 3 * s16, "note", i=i, v=0.09)
        if i in (0, I_IR, I_KRAK, I_CMB, I_BH, I_TOP): ev(t, "crash", v=0.16)
    ev(RT[-1], "crash", v=0.26); ev(RT[-1], "sub", v=0.4)
    for k, d in enumerate([0, 7, 12, 19, 24, 31, 36, 31, 24, 19, 12, 7]):   # the 147-octave sweep: low to high and back
        ev(RT[-1] + (k + 1) * s16 * 2, "pluck", m=45 + d, v=0.18)
    ev(RT[-1] - 4 * BEAT, "riser", d=4 * BEAT, v=0.08)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")
NOTES = sorted([(t, kw["i"]) for t, k, kw in EV if k == "note" and kw["v"] > 0.2] + [(RT[I_LIGO], I_LIGO)])

# ================= scene =================
_rng = np.random.default_rng(7)
STARS = [(int(_rng.integers(0, AW)), int(_rng.integers(0, AH)), int(_rng.integers(0, 3))) for _ in range(90)]
SX0, SX1, SY0, SY1 = 14, 166, 84, 228                           # scope window (art px)
SCX, SCY = (SX0 + SX1) // 2, (SY0 + SY1) // 2

def draw_light(d, i, T, age):
    col = wave_col(i); cyc = 1.2 + 10 * pos(i)                   # more cycles across the scope = faster wave
    amp = 26 * (1 + 0.5 * math.exp(-age / 0.25)); ph = T * 4
    pts = []
    for x in range(SX0 + 2, SX1 - 1):
        u = (x - SX0) / (SX1 - SX0)
        pts.append((x, SCY + amp * math.sin(2 * math.pi * cyc * u - ph)))
    for a, b in zip(pts, pts[1:]): d.line([a, b], fill=col, width=2)
    if REC[i]["year"] == "1666":                                 # Newton: the rainbow fan
        for j, c in enumerate([(255, 70, 60), (255, 150, 50), (255, 230, 70), (90, 230, 110), (80, 140, 255), (150, 110, 255)]):
            d.line([SX0 + 6, SY1 - 10, SX1 - 6, SY1 - 40 + j * 5], fill=c)
    if i == I_EHT:                                               # the black-hole ring
        rr = 16; d.ellipse([SCX - rr, SCY - rr, SCX + rr, SCY + rr], outline=(255, 150, 50), width=4)
        d.ellipse([SCX - 9, SCY - 9, SCX + 9, SCY + 9], fill=SKY if not LIGHT else (20, 20, 30))

def draw_sound(d, i, T, age):
    col = FAMC["sound"]; sp = 4 + 22 * (1 - pos(i))               # slower wave = rings further apart
    cx, cy = SX0 + 18, SCY
    d.rectangle([cx - 5, cy - 7, cx - 1, cy + 7], fill=col); d.polygon([(cx - 1, cy - 7), (cx + 5, cy - 12), (cx + 5, cy + 12), (cx - 1, cy + 7)], fill=col)
    off = (T * 18) % sp
    r = 8 + off
    while r < SX1 - cx - 3:
        fade = max(0.0, 1 - r / 150)
        ang = min(55.0, math.degrees(math.asin(min(1.0, (SCY - SY0 - 4) / r))))
        d.arc([cx - r, cy - r, cx + r, cy + r], -ang, ang, fill=mix(SKY, col, 0.25 + 0.75 * fade), width=2 if r < 40 else 1)
        r += sp

def draw_gravity(d, i, T, age):
    col = FAMC["gravity"]
    lig = i == I_LIGO
    om = 2.0 + (8.0 * ease(age / 1.8) if lig else 0)              # LIGO: the pair spirals in
    rad = 14 * (1 - 0.85 * ease(age / 1.8)) if lig else 12
    if lig and age > 1.9: rad = 0
    amp = 3.5 * (1 + (2 * math.exp(-max(0, age - 1.9) / 0.4) if lig and age > 1.9 else 0))
    for gy in range(SY0 + 6, SY1 - 2, 8):
        for gx in range(SX0 + 4, SX1 - 2, 8):
            dist = math.hypot(gx - SCX, gy - SCY)
            dz = amp * math.sin(dist / 6 - T * 6) * max(0.2, 1 - dist / 110)
            ux, uy = (gx - SCX) / (dist + 1e-6), (gy - SCY) / (dist + 1e-6)
            px, py = int(gx + ux * dz), int(gy + uy * dz)
            d.rectangle([px, py, px + 1, py + 1], fill=mix(GRID, col, min(1.0, 0.55 + 0.1 * abs(dz))))
    if rad > 0:
        a = T * om
        for s in (1, -1):
            x, y = SCX + s * rad * math.cos(a), SCY + s * rad * 0.6 * math.sin(a)
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 255, 255) if not LIGHT else (40, 40, 60))
    elif lig:
        d.ellipse([SCX - 4, SCY - 4, SCX + 4, SCY + 4], fill=(255, 255, 255) if not LIGHT else (40, 40, 60))

def scope(c, i, T, age):
    d = c.a
    d.rectangle([SX0, SY0, SX1, SY1], fill=mix(SKY, PANEL, 0.5), outline=RIM)
    for gx in range(SX0 + 19, SX1, 19): d.line([gx, SY0 + 1, gx, SY1 - 1], fill=mix(SKY, GRID, 0.6))
    d.line([SX0 + 1, SCY, SX1 - 1, SCY], fill=GRID)
    {"light": draw_light, "sound": draw_sound, "gravity": draw_gravity}[REC[i]["family"]](d, i, T, age)

def scene(c, T):
    d = c.a; d.rectangle([0, 0, AW, AH], fill=SKY)
    if not LIGHT:
        for (x, y, s) in STARS: d.point((x, y), fill=[GRID, INK2, (60, 70, 120)][s])
    k = rec_index(T)
    if T < RT[0]:                                               # hook: lowest then highest wave
        i = I_BH if T < HOOK_HI else I_TOP
        scope(c, i, T, T - (HOOK_LO if i == I_BH else HOOK_HI)); return
    scope(c, k, T, T - RT[k])

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

# ================= audio (step-2 B, full length) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n); fx = np.zeros(n)
    rng = np.random.default_rng(11); s16 = BEAT / 4
    def lp(x, fc): return lfilter(*butter(2, min(fc, SR / 2 - 100) / (SR / 2)), x)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fx, i, x * send)
    def pluck(f):
        m_ = int(.9 * SR); tt = np.arange(m_) / SR
        return sum((1 / h) * np.sin(2 * np.pi * f * h * 1.002 * tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7)) * env(m_, .002, .35)
    def marimba(f):
        m_ = int(1.2 * SR); tt = np.arange(m_) / SR
        return (np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * f * 3.93 * tt) * np.exp(-tt * 25)) * env(m_, .002, .35)
    def softsyn(f):
        m_ = int(1.4 * SR); tt = np.arange(m_) / SR
        return lp(sum((1 / h) * np.sin(2 * np.pi * f * h * tt) for h in (1, 2, 3)), 2200) * env(m_, .03, .5)
    VOICE = {"light": (pluck, 0.9, 0.1), "sound": (marimba, 1.0, -0.2), "gravity": (softsyn, 0.85, 0.2)}
    def chirp(f0=35, f1=250, d=0.6):                              # GW150914 at real pitch, f ~ (tc - t)^-3/8
        m_ = int((d + .25) * SR); tt = np.arange(m_) / SR; tc = d + .002
        f = np.clip(np.where(tt < d, f0 * (tc / np.maximum(tc - tt, 1e-3)) ** (3 / 8), f1), f0, f1)
        a = np.where(tt < d, (f / f1) ** .7, np.exp(-(tt - d) * 30))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * a
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "note":
            fam = REC[kw["i"]]["family"]; fn, g, pan = VOICE[fam]
            put(t, fn(mtof(pitch(kw["i"]))) * v * g, pan=pan, send=0.3)
        elif k == "chirp":
            put(t, chirp() * v * 1.4, send=0.25)
        elif k == "pluck":
            put(t, pluck(mtof(kw["m"])) * v, pan=0.1, send=0.3)
        elif k == "bass16":
            for q in range(4):
                m_ = int(s16 * .9 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"] + [0, 12, 7, 12][q])
                put(t + q * s16, lp(2 * ((f * tt) % 1) - 1, 500 + 900 * kw["open"]) * np.exp(-tt * 9) * v * 1.6, pan=-0.15)
        elif k == "kick":
            m_ = int(0.35 * SR); tt = np.arange(m_) / SR
            put(t, np.tanh(1.5 * np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 16) + 46) / SR) * np.exp(-tt * 12)) * v * 0.8)
        elif k == "sub":
            m_ = int(1.4 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * np.cumsum(55 * np.exp(-tt * 3) + 33) / SR) * np.exp(-tt * 2.5) * v)
        elif k == "clap":
            m_ = int(0.16 * SR); put(t, lp(rng.standard_normal(m_), 5000) * np.exp(-np.arange(m_) / SR * 18) * v * 1.2, send=0.15)
        elif k == "hat":
            m_ = int(0.04 * SR)
            put(t, lfilter(*butter(2, 8000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.001, 0.012) * v * 2.5, pan=0.3)
        elif k == "crash":
            m_ = int(1.6 * SR)
            put(t, lfilter(*butter(2, 5000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.002, 0.45) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            put(t, lfilter(*butter(2, 2500 / (SR / 2), "high"), rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    out = fx.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
        k_ = int(dl * SR); out[k_:] += g * .6 * fx[:-k_]
    out = lp(out, 4000)
    L += out * 0.45; R += np.roll(out, 400) * 0.45
    tt = np.arange(n) / SR
    fade = np.clip((TOTAL - tt) / 1.5, 0, 1); L *= fade; R *= fade
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
