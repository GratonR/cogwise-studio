"""BEEPMELODY — HOW HIGH HAVE WE GONE? Selected records of the highest (farthest) humans have been,
1783 hot-air balloon -> 2026 Artemis II. Every bell note = a new height; the pitch climbs one step per record.
Light 'clear sky' palette, side view on a log altitude axis, zoom on the last three (lunar) records.
Music: chill lo-fi bed (e-piano chords, soft swung drums, sub bass, vinyl) written here, not pi_audio.py.
Data: altitude_lofi.csv + altitude_landmarks.csv (FAI, NASA, Smithsonian, Centennial of Flight, ...).

    python3 altitude_lofi.py info out | preview out <scene>:<s> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv, re
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, eout, lerp)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.5"))

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "altitude_lofi.csv"))))
LM = {r["key"]: float(r["metres"]) for r in csv.DictReader(open(os.path.join(HERE, "altitude_landmarks.csv")))}
for r in REC: r["L"] = math.log10(float(r["metres"]))
N = len(REC)

def commas(s):
    return re.sub(r"\d{4,}", lambda m: f"{int(m.group()):,}", s)

# ================= palette (clear sky, light) =================
INK = (34, 44, 78)
INK2 = (92, 104, 140)
CORAL = (232, 92, 70)
GOLD = (236, 168, 52)
CREAM = (252, 248, 238)
WHITE = (255, 255, 255)
SKY = [(1.5, (240, 246, 246)), (3.0, (214, 236, 248)), (4.0, (178, 214, 242)), (4.7, (146, 188, 234)),
       (5.2, (126, 160, 222)), (6.0, (112, 138, 204)), (9.5, (104, 126, 192))]

# ================= timeline (all on the beat) =================
BPM = 88.0
BEAT = 60.0 / BPM
INTRO_B = 6
GAPS_B = [6, 6, 6, 6, 6, 5, 5, 5, 5, 5, 4, 4, 4, 4]          # beats between records (events squeeze)
HOLD_B, OUTRO_B = 10, 14
assert len(GAPS_B) == N - 1
RT = [INTRO_B * BEAT]
for g in GAPS_B: RT.append(RT[-1] + g * BEAT)
T_FINAL = RT[-1]
TOTAL = T_FINAL + (HOLD_B + OUTRO_B) * BEAT
SC = [("intro", RT[0]), ("balloons", RT[7] - RT[0]), ("planes", RT[10] - RT[7]), ("space", RT[12] - RT[10]),
      ("moon", T_FINAL + HOLD_B * BEAT - RT[12]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
CLIMB_B = 2.0                                              # the craft climbs during the 2 beats before each record

def rec_index(T):
    """index of the last record reached at T (-1 before the first)"""
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

def craft_L(T):
    k = rec_index(T)
    if k >= N - 1: return REC[-1]["L"]
    nxt = k + 1
    L0 = REC[k]["L"] if k >= 0 else 1.15
    L1 = REC[nxt]["L"]
    tc = RT[nxt] - CLIMB_B * BEAT
    if T < tc: return L0
    return lerp(L0, L1, ease((T - tc) / (CLIMB_B * BEAT)))

def craft_kind(T):
    k = rec_index(T)
    return REC[min(N - 1, max(0, k + 1 if k < N - 1 and T >= RT[k + 1] - CLIMB_B * BEAT else k))]["kind"]

Z_T0, Z_T1 = RT[12] + 0.5 * BEAT, RT[12] + 2.6 * BEAT
PPD0, PPD1 = 70.0, 3200.0
def ppd(T):
    if T <= Z_T0: return PPD0
    return PPD0 * (PPD1 / PPD0) ** ease((T - Z_T0) / (Z_T1 - Z_T0))
YC = 170.0                                                # craft screen y (art px)
def cam(T):
    return max(2.2, craft_L(T))
def y_of(L, T):
    return YC - (L - cam(T)) * ppd(T)

# ================= music plan (shared by picture + audio) =================
PENTA = [55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88]   # C major pentatonic from G3: one step per record
CHORDS = [(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (48, 52, 55, 59)]   # Fmaj7 Em7 Dm7 Cmaj7
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    ev(0.12, "bell", m=PENTA[0] + 12, v=0.35)                         # first note before 0.5 s
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        ch = CHORDS[bar % 4]
        drums = RT[0] <= t < T_FINAL + 4 * BEAT
        late = t >= T_FINAL + 4 * BEAT
        if pos == 0: ev(t, "keys", ch=ch, d=4 * BEAT, v=0.20 if not late else 0.16)
        if t >= RT[0] - 2 * BEAT and not late:
            if pos == 0 or (pos == 2 and bar % 2 == 1): ev(t, "bass", m=ch[0] - 12, d=BEAT * 1.6, v=0.30)
            if pos == 3 and bar % 2 == 0: ev(t + BEAT / 2, "bass", m=ch[0] - 12 + 7, d=BEAT * 0.45, v=0.22)
        if drums:
            if pos in (0,) or (pos == 2 and b % 8 == 6): ev(t, "kick", v=0.55)
            if pos == 1 and b % 8 == 1: ev(t + BEAT * 0.62, "kick", v=0.35)
            if pos in (1, 3): ev(t, "snare", v=0.30)
            for h in range(2): ev(t + h * BEAT * 0.58, "hat", v=0.10 if h == 0 else 0.065)
        elif t < RT[0] and pos in (1, 3):
            ev(t, "hat", v=0.05)
    for i, t in enumerate(RT):
        ev(t, "bell", m=PENTA[i], v=0.55 + 0.25 * i / (N - 1))
        if i > 0:                                                  # soft rising pluck while the craft climbs
            a, z = PENTA[i - 1], PENTA[i]
            steps = 3 if GAPS_B[i - 1] >= 5 else 4
            for s in range(steps):
                ev(t - CLIMB_B * BEAT + s * CLIMB_B * BEAT / steps, "pluck", m=a + (z - a) * s / steps + 12, v=0.10 + 0.02 * s)
    for k, d in enumerate([0, 7, 12, 19, 24]):                      # rising arpeggio on the final record
        ev(T_FINAL + (k + 1) * BEAT / 4, "bell", m=PENTA[-1] - 12 + d, v=0.40)
    ev(T_FINAL, "crash", v=0.30); ev(RT[10], "crash", v=0.22); ev(RT[12], "crash", v=0.22)
    ev(T_FINAL - BEAT * 2, "riser", d=BEAT * 2, v=0.12)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= drawing =================
def sky_col(L):
    for (l0, c0), (l1, c1) in zip(SKY, SKY[1:]):
        if L <= l1:
            f = max(0.0, min(1.0, (L - l0) / (l1 - l0))); return tuple(c0[j] + (c1[j] - c0[j]) * f for j in range(3))
    return SKY[-1][1]

_STARS = [(random.Random(s).uniform(0, AW), random.Random(s + 999).uniform(4.8, 9.2), random.Random(s + 77).random()) for s in range(500)]
def background(T):
    a = np.zeros((AH, AW, 3), np.float32)
    P = ppd(T); c = cam(T); yo = y_of(c, T) - YC
    for y in range(AH):
        L = c + (YC + yo - y) / P
        a[y, :] = sky_col(L)
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    for x, L, r in _STARS:                                          # pale stars above ~60 km
        y = y_of(L, T)
        if 0 <= y < 262 and L > 4.8 + 0.4 * r:
            q = min(1.0, (L - 4.8) / 0.8) * (0.5 + 0.5 * r)
            col = tuple(int(sky_col(L)[j] * (1 - q) + (236, 242, 255)[j] * q) for j in range(3))
            d.point((int(x), int(y)), fill=col)
    yg = y_of(1.0, T)                                               # ground (hills) below ~10 m
    if yg < AH:
        for x in range(AW):
            h = yg + 3 * math.sin(x / 13.0) + 2 * math.sin(x / 5.3 + 1)
            d.line([x, h, x, AH], fill=(132, 190, 112))
            d.line([x, h + 6 + 2 * math.sin(x / 9.0), x, AH], fill=(104, 160, 96))
    return img

def dashed(d, y, x0, x1, col, on=2, off=2):
    x = x0
    while x < x1: d.line([x, y, min(x1, x + on - 1), y], fill=col); x += on + off

def balloon(d, x, y, col=CORAL):
    d.ellipse([x - 6, y - 15, x + 6, y - 3], fill=col)
    d.line([x - 2, y - 15, x - 2, y - 4], fill=GOLD); d.line([x + 2, y - 15, x + 2, y - 4], fill=GOLD)
    d.point((x - 3, y - 13), fill=WHITE)
    d.line([x - 4, y - 4, x - 2, y], fill=INK2); d.line([x + 4, y - 4, x + 2, y], fill=INK2)
    d.rectangle([x - 2, y, x + 2, y + 3], fill=(150, 100, 60))

def plane(d, x, y, flame):
    d.polygon([(x, y - 9), (x + 2, y - 5), (x + 2, y + 5), (x - 2, y + 5), (x - 2, y - 5)], fill=WHITE, outline=INK2)
    d.polygon([(x - 2, y), (x - 7, y + 5), (x - 2, y + 4)], fill=CORAL); d.polygon([(x + 2, y), (x + 7, y + 5), (x + 2, y + 4)], fill=CORAL)
    d.point((x, y - 5), fill=INK)
    if flame: d.polygon([(x - 1, y + 6), (x + 1, y + 6), (x, y + 10 + random.random() * 4)], fill=GOLD)

def rocket(d, x, y, flame):
    d.rectangle([x - 2, y - 7, x + 2, y + 6], fill=WHITE, outline=INK2)
    d.polygon([(x - 2, y - 7), (x + 2, y - 7), (x, y - 12)], fill=CORAL)
    d.polygon([(x - 2, y + 2), (x - 5, y + 7), (x - 2, y + 6)], fill=INK2); d.polygon([(x + 2, y + 2), (x + 5, y + 7), (x + 2, y + 6)], fill=INK2)
    if flame:
        d.polygon([(x - 2, y + 7), (x + 2, y + 7), (x, y + 13 + random.random() * 5)], fill=GOLD)
        d.point((x, y + 9), fill=WHITE)

def capsule(d, x, y, flame):
    d.polygon([(x - 5, y + 4), (x + 5, y + 4), (x + 2, y - 5), (x - 2, y - 5)], fill=(226, 230, 238), outline=INK2)
    d.rectangle([x - 5, y + 4, x + 5, y + 6], fill=INK2)
    d.point((x - 1, y - 1), fill=INK)
    if flame: d.polygon([(x - 2, y + 7), (x + 2, y + 7), (x, y + 11 + random.random() * 3)], fill=GOLD)

XC = 112
def draw_scene(c, T):
    c.art = background(T); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    P = ppd(T)
    # axis + ticks
    d.line([20, 0, 20, 262], fill=INK2)
    if P < 600:
        for e in range(1, 10):
            y = y_of(e, T)
            if 6 < y < 258:
                d.line([17, y, 23, y], fill=INK)
                for m in (2, 5):
                    y2 = y_of(e + math.log10(m), T)
                    if 0 < y2 < 260: d.line([19, y2, 21, y2], fill=INK2)
                lab = {1: "10 M", 2: "100 M", 3: "1 KM", 4: "10 KM", 5: "100 KM", 6: "1,000 KM", 7: "10,000 KM", 8: "100,000 KM", 9: "1M KM"}[e]
                text(W, 52, int(y * 2) - 10, lab, fill=INK)
    else:
        for km in range(340000, 431000, 10000):
            y = y_of(math.log10(km * 1000), T)
            if 6 < y < 258:
                d.line([17, y, 23, y], fill=INK); text(W, 52, int(y * 2) - 10, f"{km:,} KM", fill=INK)
    # landmarks
    for key, lab in (("everest", "EVEREST 8,849 M"), ("karman", "SPACE STARTS: 100 KM")):
        y = y_of(math.log10(LM[key]), T)
        if 4 < y < 258:
            dashed(d, int(y), 22, 176, INK2 if key == "everest" else CORAL)
            text(W, 350, int(y * 2) - 20, lab, fill=INK2 if key == "everest" else CORAL, align="r")
            if key == "everest":
                d.polygon([(150, int(y)), (138, int(y) + 14), (162, int(y) + 14)], fill=(150, 170, 196))
                d.polygon([(150, int(y)), (146, int(y) + 5), (154, int(y) + 5)], fill=WHITE)
    ym = y_of(math.log10(LM["moon_avg"]), T)
    if -40 < ym < 300:
        r = max(5.0, min(26.0, 1737.4e3 / LM["moon_avg"] / math.log(10) * P))
        d.ellipse([60 - r, ym - r, 60 + r, ym + r], fill=(238, 238, 230), outline=INK2)
        d.ellipse([60 - r * 0.4, ym - r * 0.3, 60 - r * 0.1, ym], fill=(214, 214, 206))
        d.ellipse([60 + r * 0.1, ym + r * 0.2, 60 + r * 0.45, ym + r * 0.5], fill=(214, 214, 206))
        if 8 < ym < 250: text(W, 120 + int(r * 2) + 8, int(ym * 2) - 10, "MOON (AVG)", fill=INK2)
    # past records: markers on the axis
    k = rec_index(T)
    lasty = 999
    for i in range(k + 1):
        y = y_of(REC[i]["L"], T)
        if 4 < y < 258:
            d.rectangle([22, int(y) - 1, 27, int(y)], fill=CORAL)
            if abs(y - lasty) > 9 and i != k: text(W, 2, int(y * 2) - 10, REC[i]["year"], fill=CORAL); lasty = y
    # climb trail + craft
    Lc = craft_L(T); yc = y_of(Lc, T)
    Lp = REC[k]["L"] if k >= 0 else 1.15
    yp = y_of(Lp, T)
    climbing = k < N - 1 and T >= RT[k + 1] - CLIMB_B * BEAT
    if climbing:
        for yy in range(int(yc) + 8, int(min(262, yp)), 3): d.point((XC, yy), fill=WHITE)
    bob = 0 if climbing else int(round(1.2 * math.sin(T * 2.4)))
    kind = craft_kind(T)
    x, y = XC, int(yc) + bob
    if kind == "balloon": balloon(d, x, y)
    elif kind == "plane": plane(d, x, y, climbing)
    elif kind == "rocket": rocket(d, x, y, climbing)
    else: capsule(d, x, y, climbing)
    if k >= 0 and T - RT[k] < 0.5:                                  # ring on each record
        a = T - RT[k]; rr = 6 + a * 40
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=WHITE if a < 0.2 else GOLD)
    if Z_T0 < T and P > 200: text(W, 350, 178, f"ZOOM x{int(P / PPD0)}", fill=INK2, align="r")

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([20, 22, 340, 120], fill=CREAM); W.rectangle([20, 22, 340, 23], fill=INK); W.rectangle([20, 119, 340, 120], fill=INK)
    text(W, 30, 24, "HIGHEST HUMANS HAVE BEEN", fill=INK2)
    if k < 0:
        text(W, 30, 44, "GROUND", size=40, fill=INK); return
    r = REC[k]; age = T - RT[k]
    text(W, 30, 44, commas(r["display_si"]), size=40, fill=CORAL if age < 0.25 else INK)
    text(W, 30, 92, commas(r["display_us"]), fill=INK2)
    text(W, 330, 52, r["year"], size=40, fill=GOLD, align="r")
    # record card
    W.rectangle([20, 128, 340, 170], fill=(250, 250, 252)); W.rectangle([20, 128, 22, 170], fill=CORAL)
    n = int(min(len(r["who"]) + 7, age * 50))
    text(W, 30, 130, (r["year"] + " · " + r["who"])[:n], fill=INK)
    if age > 0.2: text(W, 30, 150, r["vehicle"], fill=CORAL)

BANNERS = {3: ("HIGHER THAN EVEREST", "(ESTIMATE)", False), 5: ("INTO THE STRATOSPHERE", "SEALED CABIN, FIRST TIME", False),
           10: ("FIRST HUMAN IN SPACE", "", True), 12: ("AROUND THE MOON", "FIRST HUMANS TO DO IT", True),
           13: ("THIS RECORD HELD", "FOR 56 YEARS", False), 14: ("NEW RECORD!", "6 APRIL 2026", True)}
def banner(c, T):
    k = rec_index(T)
    if k not in BANNERS: return
    a = T - RT[k]
    hold = HOLD_B * BEAT if k == N - 1 else GAPS_B[k] * BEAT - CLIMB_B * BEAT if k < N - 1 else 3
    if not (0.15 < a < hold): return
    tt, sub, big = BANNERS[k]; W = c.t; yb = 410
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + (62 if big else 42)], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=CORAL)
    if big:
        text(W, 180, yb + 2, tt, size=40, fill=INK, align="c")
        if sub and a > 0.4: text(W, 180, yb + 40, sub, fill=CORAL, align="c")
    else:
        text(W, 180, yb + 2, tt, fill=INK, align="c")
        if sub and a > 0.4: text(W, 180, yb + 21, sub, fill=CORAL, align="c")

def chart(c, T):
    d = c.a; x0, x1, yb, h = 22, 168, 306, 30
    d.rectangle([x0 - 4, yb - h - 6, x1 + 4, yb + 3], fill=CREAM, outline=INK2)
    k = rec_index(T)
    Lmin, Lmax = 2.8, 8.8
    pts = []
    for i in range(k + 1):
        x = x0 + (x1 - x0) * i / (N - 1); y = yb - (REC[i]["L"] - Lmin) / (Lmax - Lmin) * h
        if pts: pts.append((x, pts[-1][1]))
        pts.append((x, y))
    if len(pts) >= 2: d.line(pts, fill=CORAL)
    for i in range(k + 1):
        x = x0 + (x1 - x0) * i / (N - 1); y = yb - (REC[i]["L"] - Lmin) / (Lmax - Lmin) * h
        d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=INK if i < k else CORAL)
    text(c.t, (x0 - 2) * 2, (yb - h - 6) * 2 - 20, "HEIGHT (LOG)", fill=INK2)
    text(c.t, x0 * 2, yb * 2 + 6, "1783", fill=INK2); text(c.t, x1 * 2, yb * 2 + 6, "2026", fill=INK2, align="r")

def sc_intro(t):
    T = t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T); chart(c, T)
    W = c.t
    W.rectangle([20, 22, 340, 150], fill=CREAM); W.rectangle([20, 22, 340, 23], fill=INK); W.rectangle([20, 149, 340, 150], fill=INK)
    text(W, 32, 30, "HOW HIGH", size=40, fill=INK)
    if t > 0.5: text(W, 32, 70, "HAVE WE GONE?", size=40, fill=CORAL)
    if t > 1.2: text(W, 32, 116, "EVERY NOTE = A NEW HEIGHT", fill=INK2)
    if t > 2.2:
        W.rectangle([60, 300, 300, 342], fill=CREAM); W.rectangle([60, 300, 300, 302], fill=GOLD)
        text(W, 180, 302, "1783 TO 2026", fill=INK, align="c")
        text(W, 180, 321, "SELECTED RECORDS", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = Ctx(np.zeros((AH, AW, 3), np.uint8))
        draw_scene(c, T); chart(c, T); hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T)
    W = c.t; q = ease(t / 0.6)
    W.rectangle([20, 60, 340, 300], fill=CREAM); W.rectangle([20, 60, 340, 62], fill=CORAL)
    text(W, 180, 70, "1783: ~1 KM", fill=INK2, align="c")
    text(W, 180, 92, "2026: 406,771 KM", size=40, fill=INK, align="c")
    if t > 1.0: text(W, 180, 140, "252,756 MI FROM EARTH", fill=CORAL, align="c")
    if t > 2.2: text(W, 180, 180, "~400,000 TIMES HIGHER", fill=INK, align="c")
    if t > 3.2: text(W, 180, 204, "IN 243 YEARS", fill=INK, align="c")
    if t > 4.6: text(W, 180, 250, "WHAT'S THE NEXT NOTE?", fill=GOLD, align="c")
    if t > 5.6:
        W.rectangle([20, 540, 340, 600], fill=CREAM)
        text(W, 180, 544, "SELECTED RECORDS. DATA: FAI, NASA,", fill=INK2, align="c")
        text(W, 180, 564, "SMITHSONIAN, CENTENNIAL OF FLIGHT", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "balloons": sc_main("balloons"), "planes": sc_main("planes"), "space": sc_main("space"),
           "moon": sc_main("moon"), "outro": sc_outro}

def compose_light(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt)
    tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    c = SCENEFN[name](t)
    fr = compose_light(c)
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.09) if ki >= 0 else 0.0
    z = 1.0 + 0.012 * kp * FXK
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if k >= 0 and 0 <= T - RT[k] < 0.12:
        fr = np.minimum(255, fr.astype(np.int16) + int(70 * FXK * (1 - (T - RT[k]) / 0.12))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.3)) / 1.3)
        if f > 0: fr = (fr * (1 - f) + 255 * f * 0.0).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.3)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio (lo-fi chill bed + data bells) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 2.5) * SR)
    L = np.zeros(n); R = np.zeros(n); fxL = np.zeros(n); fxR = np.zeros(n)
    rng = np.random.default_rng(7)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fxL, i, x * send); add(fxR, i, x * send)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "keys":                                           # e-piano: sine + soft FM bell, tremolo
            d = kw["d"]; m_ = int(d * SR) + SR
            tt = np.arange(m_) / SR
            for j, m in enumerate(kw["ch"]):
                f = mtof(m); st = j * 0.012
                e = env(m_, 0.008, 1.8) * np.minimum(1, np.maximum(0, (d + 0.4 - tt) / 0.4))
                mod = np.sin(2 * np.pi * f * tt) * 1.2 * np.exp(-tt / 0.25)
                x = (np.sin(2 * np.pi * f * tt + mod) + 0.25 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.5)) * e
                x *= 1 + 0.12 * np.sin(2 * np.pi * 4.2 * tt)
                put(t + st, x * v * 0.5, pan=-0.3 + 0.2 * j, send=0.10)
        elif k == "bass":
            d = kw["d"]; m_ = int((d + 0.1) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = np.tanh(1.6 * np.sin(2 * np.pi * f * tt)) * env(m_, 0.01, 0.9) * np.minimum(1, np.maximum(0, (d + 0.05 - tt) / 0.06))
            put(t, x * v * 0.8)
        elif k == "kick":
            m_ = int(0.42 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(45 + 80 * np.exp(-tt / 0.04)) / SR
            put(t, np.sin(ph) * env(m_, 0.002, 0.16) * v)
        elif k == "snare":
            m_ = int(0.3 * SR); tt = np.arange(m_) / SR
            b, a = butter(2, [900 / (SR / 2), 5000 / (SR / 2)], "band")
            nz = lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.002, 0.07)
            x = nz * 1.3 + 0.35 * np.sin(2 * np.pi * 185 * tt) * env(m_, 0.002, 0.05)
            put(t + 0.012, x * v * 0.8, send=0.18)
        elif k == "hat":
            m_ = int(0.06 * SR); b, a = butter(2, 7000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.001, 0.018) * v, pan=0.35)
        elif k in ("bell", "pluck"):                               # kalimba-like bell: the data note
            dec = 1.6 if k == "bell" else 0.35
            m_ = int((dec * 3) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt / 0.3)
                 + 0.12 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / 0.06)) * env(m_, 0.002, dec)
            pan = 0.25 if k == "bell" else -0.25
            put(t, x * v * (0.55 if k == "bell" else 0.6), pan=pan, send=0.35 if k == "bell" else 0.15)
            if k == "bell":                                      # dotted-8th echo
                for e_ in range(1, 3): put(t + e_ * BEAT * 0.75, x * v * 0.3 * 0.45 ** e_, pan=-pan * (e_ % 2 * 2 - 1))
        elif k == "crash":
            m_ = int(2.5 * SR); b, a = butter(2, 4000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.003, 0.7) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR; b, a = butter(2, 2500 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    # simple room reverb on the send (comb + allpass, Schroeder style)
    def reverb(x):
        out = np.zeros_like(x)
        for dl, g in ((1557, 0.80), (1617, 0.79), (1491, 0.81), (1422, 0.80)):
            y = x.copy()
            for i in range(dl, len(y), dl): y[i:i + dl] += g * y[i - dl:i][:len(y[i:i + dl])]
            out += y * 0.25
        return out
    b, a = butter(1, 3500 / (SR / 2))
    L += lfilter(b, a, reverb(fxL)) * 0.35; R += lfilter(b, a, reverb(np.roll(fxR, 300))) * 0.35
    # lo-fi: gentle lowpass + vinyl crackle + slow wow
    b, a = butter(2, 9000 / (SR / 2))
    L = lfilter(b, a, L); R = lfilter(b, a, R)
    cr = np.zeros(n); idx = rng.integers(0, n, int(TOTAL * 9)); cr[idx] = rng.uniform(-1, 1, len(idx)) * 0.05
    b, a = butter(1, 2000 / (SR / 2), "high"); cr = lfilter(b, a, cr) + rng.standard_normal(n) * 0.0012
    L += cr; R += cr
    # fades
    tt = np.arange(n) / SR
    fade = np.clip((TOTAL - tt) / 2.2, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.stack([L, R], 1) / mx * 0.89
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
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((360, 640), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print("records at", [(REC[i]["year"], round(t, 2), round(t - START[[n for n in NAMES if START[n] <= t][-1]], 2)) for i, t in enumerate(RT)])
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(3) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
