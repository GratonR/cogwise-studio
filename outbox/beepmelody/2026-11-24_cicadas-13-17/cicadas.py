"""BEEPMELODY — These cicadas wait 13 years. Those wait 17. They only sing together every 221.  (cicadas-13-17)
Pitch p-mwtnz28e0 (Rédac), mode autonome. Central Illinois, the narrow strip where two periodical cicada broods meet:
Brood XIX (13-year, Great Southern) and Brood XIII (17-year, Northern Illinois). Both emerged in 1803 and in 2024;
next time 2245 (13 x 17 = 221 years).
Every note = one swarm coming out of the ground. Clock: 1 year = one 8th note at 120 BPM (0.25 s), 1803 -> 2024.
The 13 vs 17 polyrhythm comes from the data itself (13 and 17 eighths over a 4/4 loop).
Open on the 2024 chord (both swarms), rewind to 1803, play forward to the 2024 drop.

Music (rule 2026-11-23, musicality first):
  loop D - Bm - G - A, 120 BPM, 1 bar per chord: kick/clap/hat (hat = one tick per year) + 8th bass.
  data -> degree: each emergence plays a 3-note rising call ending on a chord tone chosen by how close the OTHER brood is
  (gap 1 year = top of 1.5 octaves, gap 8 years = root). Brood XIX = square voice, Brood XIII = triangle voice (octave below).
  arrangement: layers grow over time (offbeat chord pluck after 1871, 16th shaker after 1939); break = drums out on the
  bars of the two near misses (1854/1855, 1972/1973) and 2016 -> 2024; drop = 2024, both voices + arpeggio.
Data: cicadas.csv (UConn Periodical Cicada Project brood table; Smithsonian, National Geographic, MU Extension for 1803/2024/2245).

    python3 cicadas.py info out | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx

FXK = float(os.environ.get("PI_FX", "0.5"))

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "cicadas.csv"))))
EMERG = {"XIX": [int(r["date"]) for r in ROWS if r["brood"] == "XIX"],
         "XIII": [int(r["date"]) for r in ROWS if r["brood"] == "XIII"]}
GAP = {(r["brood"], int(r["date"])): int(r["gap_to_other_brood_years"]) for r in ROWS}
PER = {"XIX": 13, "XIII": 17}
assert len(EMERG["XIX"]) == 18 and len(EMERG["XIII"]) == 14
assert set(EMERG["XIX"]) & set(EMERG["XIII"]) == {1803, 2024}
assert all(b - a == 13 for a, b in zip(EMERG["XIX"], EMERG["XIX"][1:]))
assert all(b - a == 17 for a, b in zip(EMERG["XIII"], EMERG["XIII"][1:]))
Y0Y, Y1Y = 1803, 2024
NEXT = 2024 + 13 * 17
assert NEXT == 2245

# ================= clock =================
BPM = 120; BEAT = 60 / BPM; BAR = 4 * BEAT
Y = BEAT / 2                      # one year = one 8th note
T_RW = 4.8                        # rewind starts
T0 = 6.0                          # 1803 (bar line)
def tyr(y): return T0 + (y - Y0Y) * Y
T_DROP = tyr(Y1Y)                 # 61.25
T_END = T_DROP + 3.0
OUTRO = 5.75
TOTAL = T_END + OUTRO
def year_f(T):
    if T < T_RW: return float(Y1Y)
    if T < T0:
        f = ease((T - T_RW) / (T0 - T_RW)); return Y1Y - (Y1Y - Y0Y) * f
    return min(float(Y1Y), Y0Y + (T - T0) / Y)
CUTS = [0, T0, tyr(1860), tyr(1915), tyr(1970), T_END, TOTAL]
NAMES = ["intro", "a", "b", "c", "d", "outro"]
START = {n: CUTS[k] for k, n in enumerate(NAMES)}
DUR = {n: CUTS[k + 1] - CUTS[k] for k, n in enumerate(NAMES)}

# ================= palette (light, summer evening) =================
CREAM, WHITE = (255, 249, 236), (255, 255, 255)
INK, INK2 = (40, 44, 62), (110, 116, 140)
CORAL, CORAL2 = (226, 92, 66), (186, 66, 46)       # Brood XIX, 13 years
TEAL, TEAL2 = (28, 150, 132), (18, 112, 98)         # Brood XIII, 17 years
GOLD, GOLD2 = (240, 170, 50), (196, 130, 30)        # both
FRAME = (238, 232, 220); HUDBG = CREAM; HUDINK = INK; HUDINK2 = INK2
COL = {"XIX": CORAL, "XIII": TEAL}; COL2 = {"XIX": CORAL2, "XIII": TEAL2}
def mixc(a, b, t): t = max(0, min(1, t)); return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))

# ================= music plan =================
CHORDS = [(62, 4), (59, 3), (55, 4), (57, 4)]       # D, Bm, G, A  (root midi of the square voice, third)
def chord_at(t):
    if t < T0: return CHORDS[0]
    return CHORDS[int((t - T0 + 1e-6) // BAR) % 4]
def tones(ch):
    r, th = ch; return [r + o + i for o in (0, 12, 24) for i in (0, th, 7)][:6]
def idx_gap(g): return max(0, min(5, 6 - g))
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
BREAKS = [(T0 + BAR * int((tyr(1854) - T0) // BAR), T0 + BAR * (int((tyr(1854) - T0) // BAR) + 1)),
          (T0 + BAR * int((tyr(1972) - T0) // BAR), T0 + BAR * (int((tyr(1972) - T0) // BAR) + 1)),
          (tyr(2016), T_DROP)]
def in_break(t): return any(a - 1e-6 <= t < b - 1e-6 for a, b in BREAKS)
VOICE = {"XIX": ("square", 0), "XIII": ("tri", -12)}
def call(t, b, g, v=0.22):
    voice, sh = VOICE[b]; tn = tones(chord_at(t)); k = idx_gap(g)
    seq = [tn[max(0, k - 2)], tn[max(0, k - 1)], tn[k]]
    for j, m in enumerate(seq):
        ev(t + j * Y / 2, voice, m=m + sh, d=(0.18 if j < 2 else 0.7), v=v * (0.75 if j < 2 else 1.0))
    ev(t, "buzz", d=1.6, v=0.022, pan=(-0.35 if b == "XIX" else 0.35))

def build():
    # --- intro: 2024, both swarms, the full chord (first note at 0.05 s) ---
    ev(0.05, "pad", ms=[50, 57, 62, 66, 69], d=T_RW - 0.1, v=0.07)
    for t0 in (0.05, 2.45):
        call(t0, "XIX", 0, 0.2); call(t0 + 0.02, "XIII", 0, 0.2)
    ev(0.05, "bass", m=38, d=2.2, v=0.06); ev(2.45, "bass", m=38, d=2.2, v=0.06)
    ev(T_RW, "rewind", d=T0 - T_RW, v=0.12)
    # --- loop 1803 -> 2024 ---
    t = T0; k = 0
    while t < T_DROP - 1e-6:
        r = chord_at(t)[0]; br = in_break(t); yr = Y0Y + (t - T0) / Y
        ev(t, "hat", v=0.035 if not br else 0.05)                       # one tick per year
        if not br:
            if k % 4 == 0: ev(t, "kick", v=0.30)
            if k % 4 == 2: ev(t, "clap", v=0.07)
            ev(t, "bass", m=r - 24 + [0, 0, 12, 0, 0, 7, 12, 0][k % 8], d=Y * 0.9, v=0.10)
            if yr >= 1871 and k % 2 == 1:
                ev(t, "pluck", ms=[r - 12 + i for i in (0, chord_at(t)[1], 7)], v=0.035)
            if yr >= 1939: ev(t + Y / 2, "shaker", v=0.018)
        t += BEAT / 2; k += 1
    ev(tyr(2016), "riser", d=T_DROP - tyr(2016), v=0.14)
    for b in ("XIX", "XIII"):
        for y in EMERG[b]:
            if y == Y1Y: continue
            call(tyr(y) + (0.0 if b == "XIX" else 0.004), b, GAP[(b, y)])
    # --- drop 2024: both voices, arpeggio, full chord ---
    ev(T_DROP, "kick", v=0.36); ev(T_DROP, "crash", v=0.06)
    call(T_DROP, "XIX", 0, 0.24); call(T_DROP + 0.004, "XIII", 0, 0.24)
    ev(T_DROP, "pad", ms=[50, 57, 62, 66, 69], d=TOTAL - T_DROP - 0.6, v=0.08)
    arp = [62, 66, 69, 74, 78, 81, 78, 74]
    for j in range(24):
        tt = T_DROP + 0.75 + j * Y / 2
        ev(tt, "square" if j % 2 == 0 else "tri", m=arp[j % 8] - (0 if j % 2 == 0 else 12), d=0.16, v=0.12 * (1 - j / 40))
    t = T_DROP + BEAT; k = 2
    while t < T_END + 2 * BAR:
        fade = max(0.25, 1 - max(0, t - T_END) / (2 * BAR))
        if k % 4 == 0: ev(t, "kick", v=0.26 * fade)
        if k % 4 == 2: ev(t, "clap", v=0.06 * fade)
        ev(t, "hat", v=0.03 * fade)
        ev(t, "bass", m=38 + [0, 0, 12, 0, 0, 7, 12, 0][k % 8], d=Y * 0.9, v=0.09 * fade)
        t += BEAT / 2; k += 1
    ev(T_END + 2 * BAR, "square", m=74, d=1.4, v=0.12); ev(T_END + 2 * BAR + 0.004, "tri", m=62, d=1.4, v=0.12)
    EV.sort(key=lambda e: e[0])
build()

# ================= drawing =================
YS = 22; HZ = 150; YSOIL = 222
SKY_T, SKY_B = (132, 190, 232), (255, 226, 184)
TREES = [(4 + k * 13 + (k * 5) % 4, 18 + (k * 7) % 9, k) for k in range(14)]
NYMPH = {"XIX": [(10 + (k * 23) % 74, (k * 37) % 13) for k in range(11)],
         "XIII": [(96 + (k * 29) % 74, (k * 31) % 13) for k in range(11)]}

def last_emerg(b, y):
    c = [e for e in EMERG[b] if e <= y]; return c[-1] if c else EMERG[b][0]

def draw_scene(img, T):
    yf = year_f(T); a = np.array(img)
    for y in range(YS, HZ + 1):
        a[y, :] = mixc(SKY_T, SKY_B, (y - YS) / (HZ - YS))
    img = Image.fromarray(a); d = ImageDraw.Draw(img)
    d.ellipse([132, 98, 150, 116], fill=(255, 236, 170))                     # low summer sun
    for cx, cy in [(30, 48), (110, 36)]:
        d.ellipse([cx, cy, cx + 26, cy + 8], fill=(255, 248, 236)); d.ellipse([cx + 8, cy - 4, cx + 22, cy + 6], fill=(255, 248, 236))
    for x, hgt, k in TREES:                                                   # the forest edge
        tr = (110, 78, 52); d.rectangle([x + 4, HZ - 10, x + 6, HZ], fill=tr)
        cc = [(64, 132, 70), (82, 150, 78), (52, 116, 64)][k % 3]
        d.ellipse([x - 2, HZ - 10 - hgt, x + 12, HZ - 6], fill=cc)
        d.ellipse([x + 1, HZ - 14 - hgt, x + 9, HZ - 6 - hgt // 2], fill=mixc(cc, (200, 230, 150), 0.25))
    d.rectangle([0, HZ, AW, HZ + 3], fill=(96, 156, 74))                       # grass
    d.rectangle([0, HZ + 4, AW, YSOIL], fill=(150, 108, 72))                   # soil
    for yy in (HZ + 22, HZ + 46):
        for x in range(0, AW, 3): d.point((x, yy + (x // 3) % 2), fill=(132, 92, 60))
    for yy in range(HZ + 6, YSOIL, 4): d.point((90, yy), fill=(120, 84, 56))  # where the two ranges touch
    # nymphs: they climb toward the surface as their year comes
    for b in ("XIX", "XIII"):
        if T < T0: prog = 0.0 if T >= T_RW else 1.0
        else:
            le = last_emerg(b, int(yf + 1e-6)); prog = (yf - le) / PER[b]
        for x, o in NYMPH[b]:
            y = int(lerp(YSOIL - 10 - o, HZ + 10 + o // 3, prog ** 1.4))
            d.rectangle([x, y, x + 3, y + 1], fill=COL[b]); d.point((x + 4, y), fill=COL2[b])
    return img

def swarm(img, T, b, te, n=36, life=2.6):
    a_ = T - te
    if a_ < 0 or a_ > life: return
    d = ImageDraw.Draw(img); rnd = random.Random(hash((b, te)) % 99991)
    for k in range(n):
        sx = rnd.uniform(6, 86) if b == "XIX" else rnd.uniform(94, 174)
        tx = sx + rnd.uniform(-28, 28); ty = rnd.uniform(34, HZ - 14)
        dl = rnd.uniform(0, 0.35); f = ease(min(1, max(0, (a_ - dl) / 0.7)))
        if a_ < dl: continue
        if a_ > life - 0.6 and rnd.random() < (a_ - (life - 0.6)) / 0.6: continue
        x = sx + (tx - sx) * f + 1.5 * math.sin(a_ * 9 + k); y = HZ + (ty - HZ) * f + 1.2 * math.cos(a_ * 11 + k)
        d.rectangle([x, y, x + 3, y + 1], fill=COL[b]); d.point((x + 3, y), fill=COL2[b])
        if int(a_ * 20 + k) % 2: d.rectangle([x + 1, y - 1, x + 2, y - 1], fill=(250, 250, 255))
        else: d.rectangle([x - 1, y + 2, x + 1, y + 2], fill=(236, 240, 250))

def swarms(img, T):
    if T < T_RW:                                       # 2024: both swarms already out
        swarm(img, T + 1.0, "XIX", 0.0, 60, 99); swarm(img, T + 1.0, "XIII", 0.0, 60, 99); return
    if T < T0:                                         # rewind: the swarms go back down
        f = (T - T_RW) / (T0 - T_RW); aa = max(0.0, 1.0 - f * 1.3)
        swarm(img, aa, "XIX", 0.0, 60, 99); swarm(img, aa, "XIII", 0.0, 60, 99); return
    for b in ("XIX", "XIII"):
        for y in EMERG[b]:
            if y == Y1Y: swarm(img, T, b, tyr(y), 70, 99)
            else: swarm(img, T, b, tyr(y), 56 if y == Y0Y else 46)

def gauges(c, T):
    W = c.t; yf = year_f(T)
    for b, x0 in (("XIX", 16), ("XIII", 184)):
        W.rectangle([x0, 448, x0 + 160, 532], fill=HUDBG); W.rectangle([x0, 448, x0 + 160, 451], fill=COL[b])
        text(W, x0 + 8, 454, f"BROOD {b}", fill=COL2[b])
        text(W, x0 + 152, 454, f"{PER[b]} YRS", fill=HUDINK2, align="r")
        if T < T_RW: k, out = 0, True
        else:
            yi = int(yf + 1e-6); le = last_emerg(b, yi); k = yi - le; out = (k == 0 and T >= T0)
        if out: text(W, x0 + 8, 476, "OUT! SINGING", size=20, fill=COL[b])
        else: text(W, x0 + 8, 476, f"UNDERGROUND {k}/{PER[b]}", fill=HUDINK)
        gx0, gx1, gy = x0 + 8, x0 + 152, 504
        W.rectangle([gx0, gy, gx1, gy + 8], fill=mixc(HUDBG, HUDINK2, 0.3))
        fr = 1.0 if out else k / PER[b]
        if fr > 0: W.rectangle([gx0, gy, gx0 + (gx1 - gx0) * fr, gy + 8], fill=COL[b])
        for j in range(1, PER[b]):
            xx = gx0 + (gx1 - gx0) * j / PER[b]; W.rectangle([xx, gy, xx, gy + 8], fill=HUDBG)

def graph(c, T):
    W = c.t; x0, x1 = 52, 328; yf = year_f(T)
    W.rectangle([16, 540, 344, 636], fill=HUDBG)
    text(W, 180, 545, "EVERY NOTE = ONE CICADA SWARM", fill=HUDINK, align="c")
    def X(y): return x0 + (x1 - x0) * (y - Y0Y) / (Y1Y - Y0Y)
    for b, yy in (("XIX", 574), ("XIII", 598)):
        text(W, 46, yy - 4, str(PER[b]), fill=COL2[b], align="r")
        W.rectangle([x0, yy + 6, x1, yy + 6], fill=mixc(HUDBG, HUDINK2, 0.35))
        for e in EMERG[b]:
            if e <= yf + 1e-6 or T < T_RW:
                both = e in (Y0Y, Y1Y); col = GOLD2 if both else COL[b]
                W.rectangle([X(e) - 1, yy, X(e) + 1, yy + 12], fill=col)
    text(W, x0, 616, "1803", fill=HUDINK2); text(W, x1, 616, "2024", fill=HUDINK2, align="r")
    if T >= T_RW:
        x = X(yf); W.rectangle([x, 568, x + 1, 614], fill=HUDINK)

def hud(c, T):
    W = c.t; yf = year_f(T)
    W.rectangle([16, 14, 344, 40], fill=HUDBG); W.rectangle([16, 40, 344, 41], fill=HUDINK)
    text(W, 24, 17, "CENTRAL ILLINOIS, USA", fill=HUDINK2)
    text(W, 336, 17, f"YEAR {int(yf + 1e-6)}", fill=HUDINK, align="r")

def banner_box(W, yb, tt, sub, big, a, col):
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    hgt = (62 if big else 42) if sub else (44 if big else 24)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=HUDBG)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=HUDINK, align="c")
        if sub and a > 0.2: text(W, 180, yb + 40, sub, fill=col, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=HUDINK, align="c")
        if sub and a > 0.2: text(W, 180, yb + 21, sub, fill=col, align="c")

BY = 60
BANNERS = [   # t0, t1, title, sub, big, colour
    (tyr(1803), tyr(1803) + 2.4, "1803: BOTH SING", "THOMAS JEFFERSON IS PRESIDENT", True, GOLD2),
    (tyr(1816), tyr(1816) + 0.95, "13 YEARS LATER", "BROOD XIX IS BACK", False, CORAL2),
    (tyr(1820), tyr(1820) + 1.4, "17 YEARS LATER", "BROOD XIII IS BACK", False, TEAL2),
    (tyr(1854), tyr(1854) + 2.2, "1854 / 1855", "ONE YEAR APART. SO CLOSE", True, GOLD2),
    (tyr(1905), tyr(1905) + 1.6, "1905 / 1907", "TWO YEARS APART", False, GOLD2),
    (tyr(1920), tyr(1920) + 1.6, "1920 / 1922", "TWO YEARS APART", False, GOLD2),
    (tyr(1972), tyr(1972) + 2.2, "1972 / 1973", "ONE YEAR APART. AGAIN", True, GOLD2),
    (tyr(2016), T_DROP, "2024 IS COMING", "", False, GOLD2),
    (T_DROP, T_END, "2024: TOGETHER", "221 YEARS LATER", True, GOLD2),
]
def banner(c, T):
    for t0, t1, tt, sub, big, col in BANNERS:
        if t0 <= T < t1: banner_box(c.t, BY, tt, sub, big, T - t0, col)

def frame(T):
    a = np.zeros((AH, AW, 3), np.uint8); a[:] = FRAME
    img = draw_scene(Image.fromarray(a), T); swarms(img, T)
    c = Ctx(np.array(img)); gauges(c, T); graph(c, T)
    return c

def sc_intro(t):
    T = t; c = frame(T); W = c.t
    hud(c, T)
    if T < T_RW:
        W.rectangle([16, 52, 344, 150], fill=HUDBG); W.rectangle([16, 52, 344, 54], fill=GOLD2)
        if T < 2.4:
            text(W, 180, 60, "THESE WAIT 13 YEARS.", size=40, fill=CORAL2, align="c")
            if T > 0.7: text(W, 180, 102, "THOSE WAIT 17.", size=40, fill=TEAL2, align="c")
        else:
            text(W, 180, 60, "TOGETHER ONLY", size=40, fill=HUDINK, align="c")
            text(W, 180, 102, "EVERY 221 YEARS", size=40, fill=GOLD2, align="c")
    else:
        banner_box(W, BY, "<< REWIND TO 1803", "", True, T - T_RW, GOLD2)
    return c

def sc_years(name):
    def f(t):
        T = START[name] + t; c = frame(T); hud(c, T); banner(c, T); return c
    return f

def sc_outro(t):
    T = T_END + t; c = frame(T_END); W = c.t
    W.rectangle([16, 14, 344, 330], fill=HUDBG); W.rectangle([16, 14, 344, 16], fill=GOLD2)
    text(W, 180, 24, "BROOD XIX + BROOD XIII", fill=HUDINK2, align="c")
    if t > 0.2: text(W, 180, 48, "13 X 17 = 221", size=40, fill=HUDINK, align="c")
    if t > 0.8:
        text(W, 180, 98, "NEXT TIME TOGETHER:", fill=HUDINK, align="c")
        text(W, 180, 120, "2245", size=40, fill=GOLD2, align="c")
    if t > 1.5: text(W, 180, 172, "WHERE WILL YOU BE IN 2245?", fill=CORAL2, align="c")
    if t > 2.0:
        text(W, 180, 216, "DATA: UCONN PERIODICAL CICADA PROJECT,", fill=HUDINK2, align="c")
        text(W, 180, 234, "SMITHSONIAN, NATIONAL GEOGRAPHIC,", fill=HUDINK2, align="c")
        text(W, 180, 252, "MU EXTENSION. YEARS BEFORE 1990 FROM", fill=HUDINK2, align="c")
        text(W, 180, 270, "THE 13- AND 17-YEAR CYCLES.", fill=HUDINK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "outro": sc_outro}
for n in NAMES[1:-1]: SCENEFN[n] = sc_years(n)

def compose_light(c):
    art = np.array(c.art); big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt); tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

MOMENTS = [tyr(1803), tyr(1854), tyr(1855), tyr(1972), tyr(1973), T_DROP]
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(SCENEFN[name](t))
    for m in MOMENTS:
        if 0 <= T - m < 0.2:
            a = T - m; s = int(round(6 * FXK * math.exp(-a / 0.06) * math.sin(a * 90))); fr = np.roll(fr, s, axis=0)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(FRAME) * f).astype(np.uint8)
    return fr

# ================= audio =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def bandpass(x, f1, f2):
        b, a = butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band"); return lfilter(b, a, x)
    def env(n, a, dec):
        t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t * dec)
    def wave(f, dur, kind):
        n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
        for h in range(1, 12, 2):
            if h * f > 6000: break
            s += (np.sin(2 * np.pi * h * f * t) / h) if kind == "square" else ((-1) ** (h // 2) * np.sin(2 * np.pi * h * f * t) / h ** 2)
        return s
    def softsynth(f, dur, dec, a=.02):
        n = int(dur * SR); t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * d * t) for d in (.997, 1.003)) / 2 + .15 * np.sin(2 * np.pi * 2 * f * t)
        return s * env(n, a, dec)
    rng = np.random.RandomState(13)
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(t, x, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(x)); L[i:j] += x[:j - i] * (1 - pan) ** .5 * .9; R[i:j] += x[:j - i] * (1 + pan) ** .5 * .9
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if k in ("square", "tri"):
            d = kw["d"]; dur = d + 0.35; m_ = int(dur * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .004) * np.exp(-tt * (5 if d > .3 else 9)) * np.clip((dur - tt) / .3, 0, 1)
            x = wave(mtof(kw["m"]), dur, k) * e
            x = lowpass(x, 2600 if k == "square" else 4000)
            put(t, v * x * (0.55 if k == "square" else 1.0), -.28 if k == "square" else .28)
            put(t + 3 * Y / 2, v * 0.25 * x, .28 if k == "square" else -.28)      # dotted-8th echo
        elif k == "buzz":
            d = kw["d"]; m_ = int(d * SR); tt = np.arange(m_) / SR
            x = bandpass(rng.randn(m_), 1400, 2800) * (0.55 + 0.45 * np.sin(2 * np.pi * 28 * tt))
            e = np.clip(tt / .35, 0, 1) * np.clip((d - tt) / .7, 0, 1)
            put(t, v * x * e, kw.get("pan", 0))
        elif k == "hat":
            m_ = int(.04 * SR); put(t, v * highpass(rng.randn(m_), 6000) * np.exp(-np.arange(m_) / SR * 70), -.2)
        elif k == "shaker":
            m_ = int(.05 * SR); put(t, v * highpass(rng.randn(m_), 4000) * np.exp(-np.arange(m_) / SR * 50), .3)
        elif k == "kick":
            m_ = int(.32 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(48 + 80 * np.exp(-tt * 30)) / SR
            put(t, v * np.sin(ph) * np.exp(-tt * 9))
        elif k == "clap":
            m_ = int(.16 * SR); tt = np.arange(m_) / SR
            put(t, v * bandpass(rng.randn(m_), 900, 3000) * np.exp(-tt * 22), .1)
        elif k == "crash":
            m_ = int(2.2 * SR); tt = np.arange(m_) / SR
            put(t, v * highpass(rng.randn(m_), 5000) * np.exp(-tt * 2.2))
        elif k == "bass":
            put(t, v * lowpass(softsynth(mtof(kw["m"]), kw["d"] + .05, 3.0, .006), 420))
        elif k == "pluck":
            for i, m in enumerate(kw["ms"]):
                put(t, v * lowpass(softsynth(mtof(m), .25, 14, .003), 2500), (i - 1) * .3)
        elif k == "pad":
            d = kw["d"]; m_ = int((d + .5) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .3) * np.clip((d + .4 - tt) / .8, 0, 1)
            put(t, v * lowpass(sum(softsynth(mtof(m), d + .5, 0, .3) for m in kw["ms"]) / 2 * e, 2200))
        elif k in ("rewind", "riser"):
            d = kw["d"]; m_ = int(d * SR); tt = np.arange(m_) / SR
            x = lowpass(rng.randn(m_), 2500 if k == "riser" else 1800)
            e = (tt / d) ** 2 if k == "riser" else np.sin(np.pi * tt / d)
            put(t, v * x * e)
    def reverb(x, mix=.28):
        out = x.copy()
        for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
            k_ = int(dl * SR); out[k_:] += g * .6 * x[:-k_]
        return (1 - mix) * x + mix * lowpass(out, 4000)
    L = reverb(np.tanh(L * 1.3) / 1.3); R = reverb(np.roll(np.tanh(R * 1.3) / 1.3, int(.011 * SR)))
    tt = np.arange(n) / SR; fade = np.clip((TOTAL - tt) / 1.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max()); st = np.stack([L, R], 1) / mx * .89
    wavfile.write(path, SR, (st * 32767).astype(np.int16)); print(path, round(n / SR, 2), "s")

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
    if mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(DUR[n], 2) for n in NAMES}, Counter(k for _, k, _ in EV))
        print("drop", round(T_DROP, 2), "breaks", [(round(a, 2), round(b, 2)) for a, b in BREAKS])
        for b in ("XIX", "XIII"):
            print(b, [(y, round(tyr(y), 2), GAP[(b, y)]) for y in EMERG[b]])
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
