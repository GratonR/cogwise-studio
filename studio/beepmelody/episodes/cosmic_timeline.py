"""BEEPMELODY — WEBB JUST SAW A GALAXY FROM 280 MILLION YEARS AFTER THE BIG BANG. HERE'S THE REST.
Co-pilot: step 1 = C (Webb angle, deep-field scene), step 2 = B (Cosmic drive, 112 BPM, 16th saw-bass arpeggio,
four-on-the-floor kick, bright pluck lead with dotted-8th echo, Am–F–C–G).
20 moments, 10^-43 s -> today (cosmic_timeline.csv, 2 sources per row). One moment = one pluck note.
Pitch = rank of the moment in the series (each new chapter one step up), A minor pentatonic A2..G5.
Hook: Webb's deep field, zoom on MoM-z14 (280 Myr), then rewind to 10^-43 s and play the whole story.
Background colour follows the universe: white-hot plasma -> orange -> the CMB glow -> dark ages -> starfield.
Bottom: a LOG clock (each tick = 10x more time), announced on screen.
COSMIC_LIGHT=1 -> variant with cream panels (the 'clear' look of the altitude pilot) on the same dark sky.

    python3 cosmic_timeline.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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
LIGHT = os.environ.get("COSMIC_LIGHT", "0") == "1"

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "cosmic_timeline.csv"))))
for r in REC: r["lg"] = math.log10(float(r["t_s"]))
# on-screen wording (<= 38 chars per label; same facts as the CSV)
LABEL = {"the earliest moment physics can describe": "EARLIEST MOMENT PHYSICS CAN DESCRIBE",
         "inflation: space balloons in a blink (model)": "INFLATION: SPACE BALLOONS (MODEL)",
         "matter beats antimatter (1 in a billion survives)": "MATTER BEATS ANTIMATTER",
         "first atoms. light breaks free (the CMB)": "FIRST ATOMS. LIGHT BREAKS FREE (CMB)",
         "expansion starts speeding up (dark energy)": "EXPANSION SPEEDS UP (DARK ENERGY)",
         "today: 13.8 billion years, 2.7 K": "TODAY"}
SHOWN = {"~1 MILLIONTH OF A SECOND": "~0.000001 S"}
N = len(REC)
LG0, LG1 = REC[0]["lg"], REC[-1]["lg"]
I_CMB = next(i for i, r in enumerate(REC) if r["kind"] == "light")
I_STARS = I_CMB + 1
I_WEBB = next(i for i, r in enumerate(REC) if "MoM-z14" in r["label"])
I_ANTI = next(i for i, r in enumerate(REC) if "antimatter" in r["label"])
I_HE = next(i for i, r in enumerate(REC) if "helium" in r["label"])
I_DE = next(i for i, r in enumerate(REC) if "dark energy" in r["label"])
I_SUN = next(i for i, r in enumerate(REC) if "Sun" in r["label"])
# temperatures on screen: SI first, then US (conversions: F = K*1.8 - 459.67)
TEMP = {"~10^15 K": "~10^15 K · ~2×10^15 °F", "10 billion C / 18 billion F": "10 BILLION °C · 18 BILLION °F",
        "~1 billion K": "~1 BILLION K · ~1.8 BILLION °F", "~3,000 K": "~3,000 K · ~4,900 °F",
        "2.725 K (-270.4 C / -454.8 F)": "2.725 K · -270.4 °C · -454.8 °F"}

# ================= palette =================
SKY = (6, 8, 22); INK = (232, 238, 255); INK2 = (132, 146, 190); CYAN = (90, 220, 255); GOLD = (255, 200, 80)
RED = (255, 96, 80); PINK = (255, 120, 200); BLUE = (140, 170, 255); PANEL = (14, 18, 44); RIM = (60, 72, 130)
if LIGHT:
    PANEL = (250, 246, 234); RIM = (40, 44, 70); PINK = (214, 60, 140)
    PINK_T = (214, 60, 140); INK_T = (28, 30, 52); INK2_T = (110, 112, 140); CYAN_T = (20, 130, 190); GOLD_T = (200, 120, 10)
else:
    PINK_T, INK_T, INK2_T, CYAN_T, GOLD_T = PINK, INK, INK2, CYAN, GOLD

# ================= timeline (on the beat) =================
BPM = 112.0
BEAT = 60.0 / BPM
HOOK_B = 14
GAP_B = [6, 8, 6, 6, 6, 6, 8, 10,          # 10^-43 s ... CMB; CMB -> first stars = the dark ages (10 beats, no drums)
         4, 4, 4, 3, 3, 2, 2, 2, 2, 1, 1]  # first stars -> today: the log clock squeezes the finale, notes tighten
HOLD_B = 10
OUTRO_B = 14
assert len(GAP_B) == N - 1
RT = [HOOK_B * BEAT]
for g in GAP_B: RT.append(RT[-1] + g * BEAT)
T_END = RT[-1] + HOLD_B * BEAT
SC = [("hook", RT[0]), ("early", RT[I_CMB + 1] - RT[0]), ("late", T_END - RT[I_CMB + 1]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
TOTAL = acc_
T_REWIND = 9 * BEAT                          # 'here's the rest' -> rewind

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k
def dark_ages(T): return RT[I_CMB] + 2 * BEAT <= T < RT[I_STARS]

# ================= music plan (step-2 B) =================
SCALE = [45, 48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79]   # A minor pentatonic, A2..G5
def pitch(i): return SCALE[int(round(i / (N - 1) * (len(SCALE) - 1)))]
ROOTS = [33, 29, 36, 31]                                                # Am - F - C - G
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT)) + 1; s16 = BEAT / 4
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4); ro = ROOTS[bar % 4]
        if t >= T_END:                                               # outro: bass + pluck chord, fading
            if t < TOTAL - 3 * BEAT and pos == 0:
                ev(t, "bass16", m=ro, open=0.6, v=0.06)
                for j, d in enumerate((12, 19, 24, 28)): ev(t + j * s16 * 2, "pluck", m=ro + 24 + d - 12, v=0.10)
            elif t < TOTAL - 3 * BEAT: ev(t, "bass16", m=ro, open=0.6, v=0.05)
            continue
        hook = t < RT[0]
        if dark_ages(t):                                             # dark ages: drums out, a low drone
            if pos == 0: ev(t, "drone", m=ro, d=4 * BEAT, v=0.16)
            continue
        prog = min(1.0, t / T_END)
        ev(t, "bass16", m=ro, open=(0.15 if hook else 0.25 + 0.6 * prog), v=0.07 if not hook else 0.05)
        if hook and t < T_REWIND:
            ev(t + BEAT / 2, "hat", v=0.025)
            continue
        if hook:                                                     # rewind: snare roll + riser into 10^-43 s
            continue
        ev(t, "kick", v=0.55)
        if pos in (1, 3): ev(t, "clap", v=0.11)
        ev(t + BEAT / 2, "hat", v=0.04)
    ev(0.25, "pluck", m=pitch(I_WEBB), v=0.30); ev(0.25 + 3 * s16, "pluck", m=pitch(I_WEBB), v=0.09)  # hook note: MoM-z14
    ev(T_REWIND, "riser", d=RT[0] - T_REWIND, v=0.14)
    for j in range(int((RT[0] - T_REWIND) / s16)):
        ev(T_REWIND + j * s16, "hat", v=0.015 + 0.04 * j / 24)
    for i, t in enumerate(RT):
        m = pitch(i); big = i in (I_WEBB, N - 1)
        ev(t, "pluck", m=m, v=0.32 + (0.08 if big else 0)); ev(t + 3 * s16, "pluck", m=m, v=0.09)
        if i in (0, I_CMB, I_STARS, I_WEBB, I_DE): ev(t, "crash", v=0.18)
        if i == I_STARS: ev(t, "kick", v=0.6)
    ev(RT[-1], "crash", v=0.26); ev(RT[-1], "sub", v=0.4)
    for k, d in enumerate([0, 7, 12, 19, 24, 19, 12, 7, 0]):        # rising arpeggio on 'today'
        ev(RT[-1] + (k + 1) * s16 * 2, "pluck", m=pitch(N - 1) - 12 + d, v=0.20)
    ev(RT[-1] - 4 * BEAT, "riser", d=4 * BEAT, v=0.08)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= scene =================
def mix(a, b, f): return tuple(int(a[j] + (b[j] - a[j]) * f) for j in range(3))
HOT = [(255, 255, 250), (255, 250, 220), (255, 236, 170), (255, 214, 120), (255, 184, 90), (250, 150, 70), (236, 116, 60), (200, 86, 50)]
def sky_col(T):
    k = rec_index(T)
    if T < RT[0] or k < 0: return SKY
    if k <= I_CMB:
        a = ease((T - RT[k]) / 0.6); c = mix(HOT[max(0, k - 1)] if k else SKY, HOT[k], a)
        if k == I_CMB:                                             # light breaks free, then fades into the dark ages
            f = ease((T - RT[k] - 2 * BEAT) / (6 * BEAT)); c = mix(HOT[k], SKY, f)
        return c
    return SKY
_rng = np.random.default_rng(7)
STARS = [(int(_rng.integers(0, AW)), int(_rng.integers(0, AH)), int(_rng.integers(0, 3))) for _ in range(140)]
CMB = np.random.default_rng(3).random((AH // 4 + 1, AW // 4 + 1))
PART = [(float(_rng.random()), float(_rng.random()), int(_rng.integers(0, 3))) for _ in range(90)]
CX, CY = 90, 150                                                   # scene centre (art px)
LIGHT_STARS = [(int(_rng.integers(8, AW - 8)), int(_rng.integers(70, 218))) for _ in range(40)]

def star(d, x, y, col, s=1):
    d.point((x, y), fill=col)
    if s >= 1:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): d.point((x + dx, y + dy), fill=mix(col, SKY, .4))
    if s >= 2:
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2), (3, 0), (-3, 0)): d.point((x + dx, y + dy), fill=mix(col, SKY, .65))
def galaxy(d, x, y, r, col, ang=0.0):
    for j in range(60):
        th = j * 0.35 + ang; rr = r * j / 60
        for arm in (0, math.pi):
            px, py = x + rr * math.cos(th + arm), y + rr * 0.45 * math.sin(th + arm)
            d.point((int(px), int(py)), fill=mix(col, SKY, rr / r * .6))
    d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=mix(col, (255, 255, 255), .5))

def scene(c, T):
    d = c.a; k = rec_index(T)
    col = sky_col(T); d.rectangle([0, 0, AW, AH], fill=col)
    if T < RT[0]:                                                  # hook: Webb deep field
        z = 1 + 2.2 * ease((T - 1.0) / 2.5) if T < T_REWIND else 3.2 - 2.2 * ease((T - T_REWIND) / (RT[0] - T_REWIND))
        tx, ty = 128, 104
        for (x, y, s) in STARS:
            px, py = tx + (x - tx) * z, ty + (y - ty) * z
            if T >= T_REWIND:                                      # rewind: streaks pulled toward the centre
                q = ease((T - T_REWIND) / (RT[0] - T_REWIND)); px, py = lerp(px, CX, q * .9), lerp(py, CY, q * .9)
            if 0 <= px < AW and 0 <= py < AH: star(d, int(px), int(py), [INK2, BLUE, INK][s], 0)
        for j, (gx, gy) in enumerate([(40, 90), (150, 200), (60, 230), (120, 70)]):
            px, py = tx + (gx - tx) * z, ty + (gy - ty) * z
            if -20 < px < AW + 20: galaxy(d, int(px), int(py), int(8 * z), [BLUE, GOLD, INK2, CYAN][j], j)
        gx, gy = tx, ty                                            # MoM-z14: a tiny red smudge
        rr = int(1 + z)
        d.ellipse([gx - rr, gy - rr // 2, gx + rr, gy + rr // 2], fill=RED)
        if 1.2 < T < T_REWIND:
            b = int(5 + 3 * z); d.rectangle([gx - b, gy - b, gx + b, gy + b], outline=PINK)
        return
    if k <= I_CMB:                                                 # the hot early universe: particles in a glowing plasma
        n_part = [0, 0, 60, 90, 90, 12, 12, 12][min(k, 7)] if k < I_CMB else 0
        f = ease((T - RT[0]) / 0.3)
        if k == 0:
            r = int(1 + 3 * ease((T - RT[0]) / 0.5)); d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=(255, 255, 255))
        if k == 1:                                                 # inflation: a ring blasts outward
            a = (T - RT[1]) / 1.2; r = int(4 + 140 * ease(a))
            d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=mix(HOT[1], (255, 170, 60), .6), width=2)
        if 2 <= k < I_CMB:
            age = T - RT[k]
            for j, (px, py, s) in enumerate(PART[:n_part]):
                x = int(10 + px * (AW - 20) + 3 * math.sin(T * 3 + j)); y = int(70 + py * 150 + 3 * math.cos(T * 2.5 + j))
                pc = [(255, 80, 80), (80, 120, 255), (60, 200, 90)][s]
                if k >= 3: pc = [(220, 60, 60), (70, 90, 220), (220, 60, 60)][s]
                if k == I_ANTI and age < 0.4 and j >= 12:          # annihilation flash
                    d.point((x, y), fill=(255, 255, 255)); continue
                if k >= I_HE and j < 12 and j % 2 == 0:             # helium: pairs bound together
                    d.rectangle([x, y, x + 2, y + 2], fill=(200, 60, 60)); d.rectangle([x + 1, y + 1, x + 3, y + 3], fill=(70, 90, 220)); continue
                d.point((x, y), fill=pc)
                if k >= 3 and s != 2: d.point((x + 1, y), fill=pc)
            if k == 4:                                             # neutrinos stream out
                for j in range(14):
                    th = j * 2 * math.pi / 14; r0 = 10 + 120 * ((age * 0.9 + j * 0.07) % 1)
                    d.line([CX + r0 * math.cos(th), CY + r0 * math.sin(th), CX + (r0 + 6) * math.cos(th), CY + (r0 + 6) * math.sin(th)], fill=(255, 255, 230))
        if k == I_CMB:                                             # the CMB: mottled glow, light breaks free
            age = T - RT[k]; fade = 1 - ease((age - 2 * BEAT) / (6 * BEAT))
            if fade > 0:
                for y in range(0, AH, 4):
                    for x in range(0, AW, 4):
                        v = CMB[y // 4, x // 4]
                        cc = mix(col, (255, 150, 60) if v > .5 else (120, 40, 40), .35 * fade)
                        d.rectangle([x, y, x + 3, y + 3], fill=cc)
            for j in range(10):
                th = j * 2 * math.pi / 10 + .2; r0 = 6 + 160 * min(1, age / 1.5)
                if age < 1.6: d.line([CX, CY, CX + r0 * math.cos(th), CY + r0 * math.sin(th)], fill=(255, 240, 200))
        return
    # stars era: the deep field fills up
    fog = 1.0 if k < 11 else 1 - ease((T - RT[11]) / 1.0)            # 'transparent again': the haze clears
    n = min(len(STARS), 30 + 10 * (k - I_STARS) + (40 if k >= 13 else 0))
    stretch = 1.0 + (0.25 * ease((T - RT[I_DE]) / 1.2) if k >= I_DE else 0)
    for j, (x, y, s) in enumerate(STARS[:n]):
        px, py = CX + (x - CX) * stretch, CY + (y - CY) * stretch
        if 0 <= px < AW and 0 <= py < AH: star(d, int(px), int(py), mix([BLUE, INK, INK2][s], SKY, .45 * fog), 0)
    if fog > 0.02: d.rectangle([0, 0, AW, AH], outline=None)
    for j in range(min(12, 3 + 3 * (k - I_STARS))):                  # first stars: blue giants pop in
        x, y = LIGHT_STARS[j]; a = T - RT[I_STARS] - j * 0.08
        if a > 0: star(d, x, y, (170, 200, 255), 2 if a < 0.3 else 1)
    if k >= I_WEBB:                                                # MoM-z14 marked
        x, y = 140, 92; d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=RED)
        if T - RT[I_WEBB] < 2 * BEAT * 2: d.rectangle([x - 6, y - 6, x + 6, y + 6], outline=PINK)
    if k >= 10:                                                    # the Milky Way's disc forms
        a = ease((T - RT[10]) / 1.0); galaxy(c.a, CX - 10, CY + 20, int(36 * a), (210, 190, 255), T * 0.15)
    if k >= 12:                                                    # Gaia-Enceladus merges into the disc
        a = ease((T - RT[12]) / 1.4); gx, gy = lerp(30, CX - 18, a), lerp(110, CY + 18, a)
        if a < 1: galaxy(d, int(gx), int(gy), 9, GOLD, 0)
    if k >= 13:                                                    # cosmic noon: star birth everywhere
        for j in range(18):
            x, y = STARS[j * 7 % len(STARS)][:2]
            if (int(T * 8) + j) % 5 == 0: star(d, x, y, (255, 230, 255), 1)
    if k >= I_SUN:                                                 # the Sun, Earth, life, us — in the disc
        sx, sy = CX + 8, CY + 26
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=GOLD)
        if k >= I_SUN + 1: d.point((sx + 5, sy), fill=(80, 160, 255))
        if k >= I_SUN + 2: d.point((sx + 5, sy - 1), fill=(90, 220, 120))
        if k >= N - 2:
            d.line([sx + 5, sy - 3, sx + 5, sy - 12], fill=CYAN); d.line([sx + 3, sy - 5, sx + 5, sy - 3], fill=CYAN); d.line([sx + 7, sy - 5, sx + 5, sy - 3], fill=CYAN)

# ================= log clock (bottom) =================
BX0, BX1, BY = 14, 166, 262
def xl(lg): return BX0 + (lg - LG0) / (LG1 - LG0) * (BX1 - BX0)
def cursor_lg(T):
    k = rec_index(T)
    if T < RT[0]:
        if T < T_REWIND: return REC[I_WEBB]["lg"]
        return lerp(REC[I_WEBB]["lg"], LG0, ease((T - T_REWIND) / (RT[0] - T_REWIND)))
    a = ease((T - RT[k]) / 0.35); prev = REC[k - 1]["lg"] if k > 0 else LG0
    return lerp(prev, REC[k]["lg"], a)
def clock(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    d.rectangle([BX0 - 8, BY - 18, BX1 + 8, BY + 18], fill=PANEL, outline=RIM)
    d.rectangle([BX0, BY, BX1, BY + 2], fill=mix(RIM, PANEL, .3))
    x = xl(cursor_lg(T)); d.rectangle([BX0, BY, int(x), BY + 2], fill=CYAN if not LIGHT else CYAN_T)
    for lg in range(-40, 18, 5):
        xx = int(xl(lg)); d.line([xx, BY + 3, xx, BY + 4], fill=RIM)
    for i in range(k + 1):
        xx = int(xl(REC[i]["lg"])); d.line([xx, BY - 4, xx, BY - 1], fill=PINK if i == I_WEBB else GOLD)
    if T < RT[0]:
        xx = int(xl(REC[I_WEBB]["lg"])); d.line([xx, BY - 5, xx, BY - 1], fill=PINK)
    d.rectangle([int(x) - 1, BY - 2, int(x) + 1, BY + 4], fill=INK if not LIGHT else INK_T)
    text(W, BX0 * 2, (BY - 16) * 2, "LOG CLOCK · EACH TICK = 10X MORE TIME", fill=INK2_T)
    for lg, lab, al in ((LG0, "10^-43 S", "l"), (0, "1 S", "c"), (math.log10(3.156e7), "1 YR", "c"), (LG1, "NOW", "r")):
        text(W, int(xl(lg) * 2), (BY + 6) * 2, lab, fill=INK2_T, align=al)

# ================= HUD, banners, footer =================
def hud(c, T):
    W = c.t; k = rec_index(T); r = REC[k]; age = T - RT[k]
    W.rectangle([16, 18, 344, 122], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=RIM); W.rectangle([16, 121, 344, 122], fill=RIM)
    ago = "AGO" in r["shown"]
    text(W, 28, 22, "THE UNIVERSE · " + ("TIME SINCE THE BIG BANG" if not ago else "HOW LONG AGO"), fill=CYAN_T)
    val = r["shown"].upper(); val = SHOWN.get(val, val).replace(" AGO", "")
    hot = age < 0.25
    text(W, 28, 44, val, size=40 if len(val) <= 19 else 20, fill=(GOLD_T if hot else INK_T))
    tp = TEMP.get(r["temp"], "")
    if tp: text(W, 28, 92, tp, fill=INK2_T)
    text(W, 334, 92, f"{k + 1}/{N}", fill=INK2_T, align="r")
    W.rectangle([16, 128, 344, 152], fill=PANEL); W.rectangle([16, 128, 19, 152], fill=PINK if k == I_WEBB else CYAN_T)
    lab = LABEL.get(r["label"], r["label"]).upper()
    assert len(lab) <= 38, lab
    text(W, 28, 131, lab, fill=INK_T)

BANNERS = {I_ANTI: ("1 IN A BILLION", "THE LEFTOVER MATTER IS US"),
           I_HE: ("3 MINUTES IN", "7 BEEPS ALREADY. 13 TO GO."),
           I_CMB: ("380,000 YEARS", "THE OLDEST LIGHT WE CAN STILL SEE"),
           I_WEBB: ("WEBB'S RECORD", "FARTHEST GALAXY EVER SEEN"),
           I_DE: ("IT SPEEDS UP", "THE EXPANSION ACCELERATES"),
           N - 1: ("13.8 BILLION YEARS", "2.725 K OUT THERE · -454.8 °F")}
def box(W, xc, yb, tt, sub, accent, big=True, a=1.0):
    w = max((16 if big else 9) * len(tt) + 30, 8 * len(sub) + 30); hgt = 62 if big else 42
    x0, x1 = xc - w / 2, xc + w / 2
    W.rectangle([x0, yb, x1, yb + hgt], fill=PANEL)
    W.rectangle([x0, yb, x1, yb + 2], fill=accent); W.rectangle([x0, yb + hgt - 1, x1, yb + hgt], fill=RIM)
    text(W, xc, yb + 4, tt, size=40 if big else 20, fill=INK_T, align="c")
    if a > 0.2 and sub: text(W, xc, yb + (40 if big else 22), sub, fill=accent, align="c")
def banner(c, T):
    k = rec_index(T)
    if k < 0: return
    W = c.t; a = T - RT[k]
    if dark_ages(T):
        box(W, 180, 404, "DARK AGES", "~200 MILLION YEARS. NO STARS YET.", INK2_T, True, a); return
    if k not in BANNERS: return
    hold = (HOLD_B if k == N - 1 else min(4, GAP_B[k])) * BEAT * 0.95
    if k == I_CMB: hold = 2 * BEAT * 0.95
    if not (0.06 < a < hold): return
    tt, sub = BANNERS[k]
    box(W, 180, 404, tt, sub, PINK_T if k == I_WEBB else GOLD_T, True, a)

def footer(c, T):
    W = c.t
    W.rectangle([0, 600, 360, 640], fill=PANEL); W.rectangle([0, 600, 360, 601], fill=RIM)
    text(W, 10, 604, "EVERY BEEP", fill=INK2_T); text(W, 10, 620, "= A NEW CHAPTER", fill=CYAN_T)
    text(W, 350, 604, "HIGHER NOTE", fill=INK2_T, align="r"); text(W, 350, 620, "= LATER IN THE STORY", fill=GOLD_T, align="r")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); scene(c, T); clock(c, T)
    return c

def sc_hook(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 160], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=RIM); W.rectangle([16, 159, 344, 160], fill=RIM)
    text(W, 28, 22, "WEBB JUST SAW", size=40, fill=INK_T)
    if t > 0.25: text(W, 28, 58, "A GALAXY FROM", size=40, fill=INK_T)
    if t > 0.5: text(W, 28, 94, "280 MILLION YEARS", size=40, fill=PINK_T)
    if t > 0.8: text(W, 28, 134, "AFTER THE BIG BANG", fill=INK_T)
    if 1.6 < t < T_REWIND:
        text(W, 268, 236, "MoM-z14", fill=PINK_T, align="c")
        text(W, 268, 254, "Z = 14.44", fill=INK2_T, align="c")
    if t >= T_REWIND:
        box(W, 180, 404, "HERE'S THE REST", "REWIND TO 10^-43 SECONDS", CYAN_T, True, t - T_REWIND)
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
    text(W, 180, 52, "13.8 BILLION YEARS · 20 BEEPS", fill=INK2_T, align="c")
    rows = [("7", "BEEPS IN THE FIRST 3 MINUTES", CYAN_T), ("380,000 YR", "OLDEST LIGHT (CMB)", GOLD_T),
            ("280 M YR", "WEBB'S FARTHEST GALAXY", PINK_T), ("2.725 K", "TODAY · -454.8 °F", INK_T)]
    for j, (a, b, col) in enumerate(rows):
        if t > 0.3 + j * 0.45:
            text(W, 28, 84 + j * 56, a, size=40, fill=col); text(W, 332, 116 + j * 56, b, fill=INK_T, align="r")
    if t > 2.2: text(W, 180, 330, "EARLY TIMES ARE MODELS (~)", fill=INK2_T, align="c")
    if t > 2.6:
        W.rectangle([40, 440, 320, 441], fill=INK2_T)
        text(W, 180, 448, "DATA: NASA, ESA PLANCK, ESA/WEBB,", fill=INK2_T, align="c")
        text(W, 180, 466, "ESA GAIA, CERN, PDG, USGS,", fill=INK2_T, align="c")
        text(W, 180, 484, "NAIDU 2025, MADAU & DICKINSON 2014,", fill=INK2_T, align="c")
        text(W, 180, 502, "RIESS 2004, CONNELLY 2012 + PAPERS", fill=INK2_T, align="c")
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
    if name == "hook" and abs(t - 0.25) < 0.08:
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
    def pluck(f, m_=int(.9 * SR)):
        tt = np.arange(m_) / SR
        s = sum((1 / h) * np.sin(2 * np.pi * f * h * 1.002 * tt) * np.exp(-tt * (5 + 3 * h)) for h in range(1, 7))
        return s * env(m_, .002, .35)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "pluck":
            put(t, pluck(mtof(kw["m"])) * v, pan=0.1, send=0.3)
        elif k == "bass16":                                         # one beat of 16th saw arpeggio
            for q in range(4):
                m_ = int(s16 * .9 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"] + [0, 12, 7, 12][q])
                saw = 2 * ((f * tt) % 1) - 1
                put(t + q * s16, lp(saw, 500 + 900 * kw["open"]) * np.exp(-tt * 9) * v * 1.6, pan=-0.15)
        elif k == "drone":
            d = kw["d"]; m_ = int(d * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = lp(np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 1.5 * tt) + .3 * np.sin(2 * np.pi * f * 2.004 * tt), 600)
            put(t, x * np.minimum(1, tt / .4) * np.clip((d - tt) / .4, 0, 1) * v, send=0.3)
        elif k == "kick":
            m_ = int(0.35 * SR); tt = np.arange(m_) / SR
            x = np.sin(2 * np.pi * np.cumsum(80 * np.exp(-tt * 16) + 46) / SR) * np.exp(-tt * 12)
            put(t, np.tanh(1.5 * x) * v * 0.8)
        elif k == "sub":
            m_ = int(1.4 * SR); tt = np.arange(m_) / SR
            put(t, np.sin(2 * np.pi * np.cumsum(55 * np.exp(-tt * 3) + 33) / SR) * np.exp(-tt * 2.5) * v)
        elif k == "clap":
            m_ = int(0.16 * SR); x = lp(rng.standard_normal(m_), 5000) * np.exp(-np.arange(m_) / SR * 18)
            put(t, x * v * 1.2, send=0.15)
        elif k == "hat":
            m_ = int(0.04 * SR)
            x = lfilter(*butter(2, 8000 / (SR / 2), "high"), rng.standard_normal(m_)) * env(m_, 0.001, 0.012)
            put(t, x * v * 2.5, pan=0.3)
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
            r = REC[i]; print(f"{t:6.2f}s  lg {r['lg']:7.2f}  p{pitch(i)}  {r['shown']:<26} {r['label']}")
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
