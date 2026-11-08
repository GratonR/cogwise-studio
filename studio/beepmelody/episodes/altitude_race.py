"""BEEPMELODY — THE RACE TO THE SKY. 53 height records in three lanes (balloons, planes, spacecraft),
1783 tethered balloon -> 2026 Artemis II. Every note = a new record in its lane; pitch = height (log scale),
each lane has its own instrument. Light 'clear sky' palette, full log altitude axis, zoom on the Moon at the end.
Pilot v3 (Guillaume 2026-11-08: more records, faster rhythm, different music / chords).
Music: upbeat chill-pop bed, 116 BPM, D major, IV-V-iii-vi (Gmaj7 A7 F#m7 Bm7), written here (not pi_audio.py).
Data: altitude_race.csv (2 sources per row) + altitude_landmarks.csv.

    python3 altitude_race.py info out | preview out <scene>:<s> ... | audio out/music.wav | render out | final out x.mp4
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

FXK = float(os.environ.get("PI_FX", "0.5"))

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "altitude_race.csv"))))
LM = {r["key"]: float(r["metres"]) for r in csv.DictReader(open(os.path.join(HERE, "altitude_landmarks.csv")))}
for r in REC:
    r["m"] = float(r["metres"]); r["L"] = math.log10(r["m"]); r["year"] = r["date"][:4]
N = len(REC)
LANES = ["balloon", "plane", "space"]
LANE_NAME = {"balloon": "BALLOON", "plane": "PLANE", "space": "SPACE"}

def fmt_si(r):
    m = r["m"]; p = "~" if r["approx"] == "1" else ""
    if m >= 200000: return f"{p}{round(m / 1000):,} KM"
    if m >= 100000: return f"{p}{m / 1000:.2f} KM"
    return f"{p}{int(m):,} M"
def fmt_us(r):
    p = "~" if r["approx"] == "1" else ""
    u = int(r["us"])
    return f"{p}{u:,} MI" if r["m"] >= 200000 else f"{p}{u:,} FT"

TAG = {"1927-11-04": "NOT RATIFIED", "1962-07-17": "NOT AN FAI RECORD", "1963-08-22": "UNOFFICIAL",
       "2012-10-14": "RODE UP, THEN JUMPED", "2014-10-24": "RODE UP, THEN JUMPED", "1957-06-02": "ESTIMATE",
       "1783-11-21": "ESTIMATE", "1783-12-01": "ESTIMATE", "1784-06-23": "ESTIMATE", "1862-09-05": "ESTIMATE"}

# ================= palette (clear sky, light) =================
INK = (34, 44, 78)
INK2 = (92, 104, 140)
CORAL = (232, 92, 70)
GOLD = (236, 168, 52)
CREAM = (252, 248, 238)
WHITE = (255, 255, 255)
LCOL = {"balloon": CORAL, "plane": (18, 128, 116), "space": (112, 70, 196)}
SKY = [(0.5, (242, 247, 246)), (3.0, (224, 240, 249)), (4.0, (200, 226, 246)), (4.7, (178, 208, 240)),
       (5.5, (160, 190, 232)), (7.0, (146, 174, 224)), (9.5, (136, 162, 216))]

# ================= timeline (all on the beat) =================
BPM = 116.0
BEAT = 60.0 / BPM
INTRO_B = 7
def gap_beats(i):
    dy = int(REC[i]["year"]) - int(REC[i - 1]["year"])
    if i == N - 1: return 10                               # zoom to the Moon before the last record
    if dy == 0: return 1
    if dy <= 6: return 1.5
    if dy <= 25: return 2
    return 4
GAPS_B = [gap_beats(i) for i in range(1, N)]
HOLD_B, OUTRO_B = 10, 20
RT = [INTRO_B * BEAT]
for g in GAPS_B: RT.append(RT[-1] + g * BEAT)
T_FINAL = RT[-1]
TOTAL = T_FINAL + (HOLD_B + OUTRO_B) * BEAT
def first_year(y): return next(i for i, r in enumerate(REC) if int(r["year"]) >= y)
I1900, I1950, I1961 = first_year(1900), first_year(1950), first_year(1962)
SC = [("intro", RT[0]), ("early", RT[I1900] - RT[0]), ("interwar", RT[I1950] - RT[I1900]), ("rockets", RT[I1961] - RT[I1950]),
      ("moon", T_FINAL + HOLD_B * BEAT - RT[I1961]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

def lane_state(T, lane):
    """(L, climbing, kind, last index) of the lane's craft at T"""
    idx = [i for i in range(N) if REC[i]["lane"] == lane]
    done = [i for i in idx if RT[i] <= T]
    nxt = [i for i in idx if RT[i] > T]
    L0 = REC[done[-1]]["L"] if done else 0.9
    kind = REC[done[-1]]["kind"] if done else REC[idx[0]]["kind"]
    if nxt:
        j = nxt[0]; cb = min(1.0, GAPS_B[j - 1]) * BEAT
        if j == N - 1: cb = 2 * BEAT
        if T >= RT[j] - cb:
            return lerp(L0, REC[j]["L"], ease((T - (RT[j] - cb)) / cb)), True, REC[j]["kind"], (done[-1] if done else -1)
    return L0, False, kind, (done[-1] if done else -1)

# camera: full log axis, then zoom on the Moon before the last record
Y_GROUND, L_GROUND, PPD0 = 292.0, 0.9, 25.6
L_ANCH = 8.6
Z_T0, Z_T1 = RT[-2] + 1.0 * BEAT, RT[-2] + 4.5 * BEAT
PPD1, YA1 = 3000.0, 165.0
def zoomf(T):
    if T <= Z_T0: return 0.0
    return ease(min(1.0, (T - Z_T0) / (Z_T1 - Z_T0)))
def ppd(T): return PPD0 * (PPD1 / PPD0) ** zoomf(T)
def y_of(L, T):
    z = zoomf(T); ya0 = Y_GROUND - (L_ANCH - L_GROUND) * PPD0
    return lerp(ya0, YA1, z) - (L - L_ANCH) * ppd(T)

# ================= music plan (shared by picture + audio) =================
SCALE = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86, 88, 90, 93]       # D major pentatonic from D4
LANE_RANGE = {"balloon": (0, 12), "plane": (1, 12), "space": (7, 13)}
def pitch(i):
    """each lane climbs its own ladder: one more record in a lane = a higher (or equal) step"""
    ln = REC[i]["lane"]; idx = [j for j in range(N) if REC[j]["lane"] == ln]; r = idx.index(i)
    lo, hi = LANE_RANGE[ln]
    return SCALE[lo + int(round(r * (hi - lo) / max(1, len(idx) - 1)))]
CHORDS = [(55, 59, 62, 66), (57, 61, 64, 67), (54, 57, 61, 64), (50, 54, 57, 59)]   # Gmaj7 A7 F#m7 Bm7/D
ROOTS = [43, 45, 42, 47]
VOICE = {"balloon": "bell", "plane": "mallet", "space": "lead"}
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    ev(0.10, "bell", m=74, v=0.40)
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        ch = CHORDS[bar % 4]; ro = ROOTS[bar % 4]
        groove = RT[0] - 2 * BEAT <= t < T_FINAL + 6 * BEAT
        late = t >= T_FINAL + 6 * BEAT
        if pos == 0: ev(t, "keys", ch=ch, d=1.4 * BEAT, v=0.20 if not late else 0.15)
        if pos == 1 and not late: ev(t + BEAT / 2, "keys", ch=ch, d=0.45 * BEAT, v=0.13)
        if pos == 3 and not late: ev(t + BEAT / 2, "keys", ch=ch, d=0.45 * BEAT, v=0.11)
        if late and pos == 0: ev(t, "pad", ch=ch, d=4 * BEAT, v=0.12)
        if groove:
            if pos == 0: ev(t, "bass", m=ro, d=BEAT * 0.8, v=0.32)
            if pos == 1: ev(t + BEAT / 2, "bass", m=ro + 12, d=BEAT * 0.35, v=0.22)
            if pos == 2: ev(t, "bass", m=ro + 7, d=BEAT * 0.6, v=0.26)
            if pos == 3: ev(t + BEAT / 2, "bass", m=ro, d=BEAT * 0.4, v=0.24)
            if t >= RT[0]:
                if pos in (0, 2): ev(t, "kick", v=0.62)
                if pos == 1: ev(t + BEAT / 2, "kick", v=0.38)
                if pos in (1, 3): ev(t, "snare", v=0.34)
                for h in range(2): ev(t + h * BEAT * 0.54, "hat", v=0.10 if h == 0 else 0.07)
                if pos == 3 and bar % 2 == 1: ev(t + BEAT * 0.54, "ohat", v=0.08)
            elif pos in (1, 3):
                ev(t, "hat", v=0.06)
    for i, t in enumerate(RT):
        r = REC[i]
        ev(t, VOICE[r["lane"]], m=pitch(i), v=0.50 + 0.22 * i / (N - 1))
    for k, d in enumerate([0, 7, 12, 16, 19, 24]):                  # rising arpeggio on the final record
        ev(T_FINAL + (k + 1) * BEAT / 4, "bell", m=74 + d - 12, v=0.40)
    for t in (RT[first_year(1951)], RT[next(i for i, r in enumerate(REC) if r["lane"] == "space")], RT[-3]):
        ev(t, "crash", v=0.22)
    ev(T_FINAL, "crash", v=0.32)
    ev(T_FINAL - BEAT * 4, "riser", d=BEAT * 4, v=0.13)
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
    P = ppd(T); y0 = y_of(0.0, T)
    for y in range(AH):
        a[y, :] = sky_col((y0 - y) / P)
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    for x, L, r in _STARS:
        y = y_of(L, T)
        if 88 <= y < 296 and L > 4.8 + 0.4 * r:
            q = min(1.0, (L - 4.8) / 0.8) * (0.5 + 0.5 * r)
            col = tuple(int(sky_col(L)[j] * (1 - q) + (240, 244, 255)[j] * q) for j in range(3))
            d.point((int(x), int(y)), fill=col)
    yg = y_of(L_GROUND, T)
    if yg < AH:
        for x in range(AW):
            h = yg + 2 * math.sin(x / 13.0) + 1.5 * math.sin(x / 5.3 + 1)
            d.line([x, h, x, AH], fill=(132, 190, 112))
            d.line([x, h + 5 + 2 * math.sin(x / 9.0), x, AH], fill=(104, 160, 96))
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

def plane(d, x, y, flame, col):
    d.polygon([(x, y - 9), (x + 2, y - 5), (x + 2, y + 5), (x - 2, y + 5), (x - 2, y - 5)], fill=WHITE, outline=INK2)
    d.polygon([(x - 2, y), (x - 7, y + 5), (x - 2, y + 4)], fill=col); d.polygon([(x + 2, y), (x + 7, y + 5), (x + 2, y + 4)], fill=col)
    d.point((x, y - 5), fill=INK)
    if flame: d.polygon([(x - 1, y + 6), (x + 1, y + 6), (x, y + 10 + random.random() * 4)], fill=GOLD)

def rocket(d, x, y, flame, col):
    d.rectangle([x - 2, y - 7, x + 2, y + 6], fill=WHITE, outline=INK2)
    d.polygon([(x - 2, y - 7), (x + 2, y - 7), (x, y - 12)], fill=col)
    d.polygon([(x - 2, y + 2), (x - 5, y + 7), (x - 2, y + 6)], fill=INK2); d.polygon([(x + 2, y + 2), (x + 5, y + 7), (x + 2, y + 6)], fill=INK2)
    if flame:
        d.polygon([(x - 2, y + 7), (x + 2, y + 7), (x, y + 13 + random.random() * 5)], fill=GOLD)
        d.point((x, y + 9), fill=WHITE)

def capsule(d, x, y, flame, col):
    d.polygon([(x - 5, y + 4), (x + 5, y + 4), (x + 2, y - 5), (x - 2, y - 5)], fill=(226, 230, 238), outline=INK2)
    d.rectangle([x - 5, y + 4, x + 5, y + 6], fill=col)
    d.point((x - 1, y - 1), fill=INK)
    if flame: d.polygon([(x - 2, y + 7), (x + 2, y + 7), (x, y + 11 + random.random() * 3)], fill=GOLD)

AXX = 38
LX = {"balloon": 70, "plane": 110, "space": 148}
MOONX = 170
def draw_scene(c, T):
    c.art = background(T); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    P = ppd(T)
    d.line([AXX, 88, AXX, 296], fill=INK2)
    if P < 300:
        for e in range(1, 9):
            y = y_of(e, T)
            if 90 < y < 294:
                d.line([AXX - 3, y, AXX + 2, y], fill=INK)
                for m in (2, 5):
                    y2 = y_of(e + math.log10(m), T)
                    if 88 < y2 < 296: d.line([AXX - 1, y2, AXX + 1, y2], fill=INK2)
                lab = {1: "10 M", 2: "100 M", 3: "1 KM", 4: "10 KM", 5: "100 KM", 6: "1,000 KM", 7: "10,000 KM", 8: "100,000 KM"}[e]
                text(W, AXX * 2 - 8, int(y * 2) - 10, lab if len(lab) <= 8 else lab.replace(",000 KM", "K KM"), fill=INK, align="r")
    else:
        for km in range(350000, 431000, 10000):
            y = y_of(math.log10(km * 1000), T)
            if 90 < y < 294:
                d.line([AXX - 3, y, AXX + 2, y], fill=INK); text(W, AXX * 2 - 8, int(y * 2) - 10, f"{km // 1000}K KM", fill=INK, align="r")
    # lanes
    for ln in LANES:
        x = LX[ln]
        for yy in range(88, 296, 4): d.point((x, yy), fill=tuple(int(v * 0.5 + 255 * 0.5) for v in LCOL[ln]))
    # landmarks
    for key, lab in (("everest", "EVEREST"), ("karman", "SPACE: 100 KM")):
        y = y_of(math.log10(LM[key]), T)
        if 90 < y < 294:
            dashed(d, int(y), AXX + 2, 178, INK2 if key == "everest" else CORAL)
            text(W, 356, int(y * 2) - 20, lab, fill=INK2 if key == "everest" else CORAL, align="r")
    ym = y_of(math.log10(LM["moon_avg"]), T)
    if 60 < ym < 320:
        r = max(4.0, min(24.0, 1737.4e3 / LM["moon_avg"] / math.log(10) * P))
        mx = MOONX if P < 300 else 128
        d.ellipse([mx - r, ym - r, mx + r, ym + r], fill=(238, 238, 230), outline=INK2)
        d.ellipse([mx - r * 0.4, ym - r * 0.3, mx - r * 0.1, ym], fill=(214, 214, 206))
        if P > 300 and 92 < ym < 290: text(W, int(mx * 2), int((ym + r) * 2) + 4, "MOON (AVG)", fill=INK2, align="c")
        elif P < 300 and ym > 92: text(W, int(mx * 2) - 2, int(ym * 2) + 12, "MOON", fill=INK2, align="c")
    k = rec_index(T)
    # past records: ticks on each lane
    for i in range(k + 1):
        r = REC[i]; y = y_of(r["L"], T); x = LX[r["lane"]]
        if 88 < y < 296: d.rectangle([x - 4, int(y), x + 4, int(y)], fill=LCOL[r["lane"]])
    # crafts
    for ln in LANES:
        L, climbing, kind, last = lane_state(T, ln)
        x = LX[ln]; y = y_of(L, T)
        if climbing:
            yp = y_of(REC[last]["L"], T) if last >= 0 else y_of(L_GROUND, T)
            for yy in range(int(y) + 8, int(min(296, yp)), 3): d.point((x, yy), fill=WHITE)
        bob = 0 if climbing else int(round(1.0 * math.sin(T * 2.4 + x)))
        if not (80 < y < 304): continue
        y = int(y) + bob
        col = LCOL[ln]
        if kind == "balloon": balloon(d, x, y, col)
        elif kind == "plane": plane(d, x, y, climbing, col)
        elif kind == "rocket": rocket(d, x, y, climbing, col)
        else: capsule(d, x, y, climbing, col)
        if last >= 0 and 0 <= T - RT[last] < 0.45:
            a = T - RT[last]; rr = 5 + a * 40
            d.ellipse([x - rr, y - 8 - rr, x + rr, y - 8 + rr], outline=WHITE if a < 0.18 else GOLD)
    if zoomf(T) > 0.3: text(W, 352, 182, f"ZOOM x{int(P / PPD0)}", fill=INK2, align="r")

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if k < 0:
        text(W, 28, 22, "THE RACE TO THE SKY", fill=INK2); text(W, 28, 44, "GROUND", size=40, fill=INK); return
    r = REC[k]; age = T - RT[k]; col = LCOL[r["lane"]]
    text(W, 28, 22, f"NEW {LANE_NAME[r['lane']]} RECORD", fill=col)
    text(W, 28, 44, fmt_si(r), size=40, fill=col if age < 0.22 else INK)
    text(W, 28, 92, fmt_us(r), fill=INK2)
    text(W, 334, 44, r["year"], size=40, fill=GOLD, align="r")
    text(W, 334, 92, f"#{k + 1} / {N}", fill=INK2, align="r")
    W.rectangle([16, 128, 344, 172], fill=(250, 250, 252)); W.rectangle([16, 128, 19, 172], fill=col)
    n = int(min(60, age * 70))
    text(W, 28, 131, r["who"][:max(0, n)], fill=INK)
    sub = r["vehicle"] + ("  · " + TAG[r["date"]] if r["date"] in TAG else "")
    if age > 0.12: text(W, 28, 151, sub[:40], fill=col if r["date"] not in TAG else INK2)

def legend(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([0, 604, 360, 640], fill=CREAM); W.rectangle([0, 604, 360, 605], fill=INK2)
    for j, ln in enumerate(LANES):
        cnt = sum(1 for i in range(k + 1) if REC[i]["lane"] == ln)
        x = LX[ln] * 2
        hot = k >= 0 and REC[k]["lane"] == ln and T - RT[k] < 0.3
        text(W, x, 608, LANE_NAME[ln], fill=LCOL[ln], align="c")
        text(W, x, 622, str(cnt), fill=INK if not hot else LCOL[ln], align="c")
    text(W, 6, 615, "(LOG)", fill=INK2)

def ifirst(lane): return next(i for i, r in enumerate(REC) if r["lane"] == lane)
BANNERS = {first_year(1862): ("HIGHER THAN EVEREST?", "(ESTIMATE)", False),
           ifirst("plane"): ("PLANES JOIN THE RACE", "1910", False),
           first_year(1951): ("PLANES PASS BALLOONS", "FOR GOOD", True),
           ifirst("space"): ("FIRST HUMAN IN SPACE", "YURI GAGARIN", True),
           first_year(1968): ("AROUND THE MOON", "FIRST HUMANS TO DO IT", True),
           first_year(2012): ("BALLOON + PARACHUTE", "HIGHEST JUMP EVER", False),
           N - 1: ("NEW RECORD!", "AFTER 56 YEARS", True)}
def banner(c, T):
    k = rec_index(T)
    if k not in BANNERS: return
    a = T - RT[k]
    hold = HOLD_B * BEAT if k == N - 1 else max(2 * BEAT, GAPS_B[k] * BEAT) if k < N - 1 else 3
    if k < N - 1 and GAPS_B[k] < 2: hold = 2.2 * BEAT
    if not (0.1 < a < hold): return
    tt, sub, big = BANNERS[k]; W = c.t; yb = 380 if k != N - 1 else 470
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + (62 if big else 42)], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=CORAL)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 40, sub, fill=CORAL, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 21, sub, fill=CORAL, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T); legend(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 26, "THE RACE", size=40, fill=INK)
    if t > 0.4: text(W, 28, 64, "TO THE SKY", size=40, fill=CORAL)
    if t > 1.0: text(W, 28, 112, "EVERY NOTE = A NEW RECORD", fill=INK2)
    if t > 1.6:
        text(W, 28, 140, "BALLOON", fill=LCOL["balloon"]); text(W, 108, 140, "VS", fill=INK2)
        text(W, 140, 140, "PLANE", fill=LCOL["plane"]); text(W, 196, 140, "VS", fill=INK2)
        text(W, 228, 140, "SPACECRAFT", fill=LCOL["space"])
    if t > 2.2:
        W.rectangle([70, 400, 290, 442], fill=CREAM); W.rectangle([70, 400, 290, 402], fill=GOLD)
        text(W, 180, 403, f"{N} RECORDS", fill=INK, align="c")
        text(W, 180, 422, "1783 TO 2026", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, T); legend(c, T)
    W = c.t
    W.rectangle([16, 40, 344, 330], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=CORAL)
    text(W, 180, 50, "HIGHEST EACH WAY", fill=INK2, align="c")
    rows = [("BALLOON", "41,422 M", "2014 (THEN JUMPED)", "balloon"), ("PLANE", "112.01 KM", "2004 SPACESHIPONE", "plane"),
            ("SPACE", "406,771 KM", "2026 ARTEMIS II", "space")]
    for j, (a, b, s, ln) in enumerate(rows):
        if t > 0.5 + j * 0.8:
            y = 78 + j * 64
            text(W, 30, y, a, fill=LCOL[ln]); text(W, 330, y - 6, b, size=40, fill=INK, align="r")
            text(W, 330, y + 32, s, fill=INK2, align="r")
    if t > 3.4: text(W, 180, 278, "WHAT'S THE NEXT NOTE?", fill=GOLD, align="c")
    if t > 4.4:
        W.rectangle([16, 520, 344, 590], fill=CREAM)
        text(W, 180, 526, "SELECTED RECORDS. DATA: FAI, NASA,", fill=INK2, align="c")
        text(W, 180, 546, "SMITHSONIAN, CENTENNIAL OF FLIGHT,", fill=INK2, align="c")
        text(W, 180, 566, "GUINNESS WORLD RECORDS", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "interwar": sc_main("interwar"), "rockets": sc_main("rockets"),
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
    kp = math.exp(-(T - KICKS[ki]) / 0.08) if ki >= 0 else 0.0
    z = 1.0 + 0.010 * kp * FXK
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if k >= 0 and 0 <= T - RT[k] < 0.10:
        fr = np.minimum(255, fr.astype(np.int16) + int(55 * FXK * (1 - (T - RT[k]) / 0.10))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio =================
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
    rng = np.random.default_rng(11)
    def add(buf, i, x):
        j = min(n, i + len(x)); buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        if i >= n: return
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fxL, i, x * send); add(fxR, i, x * send)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k in ("keys", "pad"):
            d = kw["d"]; m_ = int((d + 0.6) * SR); tt = np.arange(m_) / SR
            for j, m in enumerate(kw["ch"]):
                f = mtof(m)
                if k == "keys":
                    e = env(m_, 0.004, 0.9) * np.clip((d + 0.12 - tt) / 0.12, 0, 1)
                    mod = np.sin(2 * np.pi * f * tt) * 1.4 * np.exp(-tt / 0.15)
                    x = (np.sin(2 * np.pi * f * tt + mod) + 0.2 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.3)) * e
                    put(t + j * 0.006, x * v * 0.5, pan=-0.35 + 0.23 * j, send=0.10)
                else:
                    e = np.minimum(1, tt / 0.6) * np.clip((d + 0.5 - tt) / 0.5, 0, 1)
                    x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.003 * tt)) * e
                    put(t, x * v * 0.4, pan=-0.4 + 0.27 * j, send=0.2)
        elif k == "bass":
            d = kw["d"]; m_ = int((d + 0.08) * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = np.tanh(2.0 * np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * env(m_, 0.004, 0.5) * np.clip((d + 0.04 - tt) / 0.05, 0, 1)
            put(t, x * v * 0.8)
        elif k == "kick":
            m_ = int(0.38 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(48 + 110 * np.exp(-tt / 0.035)) / SR
            put(t, np.sin(ph) * env(m_, 0.001, 0.14) * v)
        elif k == "snare":
            m_ = int(0.28 * SR); tt = np.arange(m_) / SR
            b, a = butter(2, [1200 / (SR / 2), 7000 / (SR / 2)], "band")
            nz = lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.001, 0.08)
            x = nz * 1.4 + 0.4 * np.sin(2 * np.pi * 200 * tt) * env(m_, 0.001, 0.04)
            put(t, x * v * 0.8, send=0.2)
        elif k in ("hat", "ohat"):
            m_ = int((0.06 if k == "hat" else 0.3) * SR); b, a = butter(2, 8000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.001, 0.016 if k == "hat" else 0.12) * v, pan=0.35)
        elif k == "bell":                                        # balloon voice: kalimba-like bell
            m_ = int(3.5 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt / 0.3)
                 + 0.12 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt / 0.06)) * env(m_, 0.002, 1.1)
            put(t, x * v * 0.55, pan=-0.3, send=0.3)
            put(t + BEAT * 0.75, x * v * 0.12, pan=0.3)
        elif k == "mallet":                                      # plane voice: marimba
            m_ = int(1.2 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 4.0 * tt) * np.exp(-tt / 0.03)
                 + 0.2 * np.sin(2 * np.pi * f * 10.0 * tt) * np.exp(-tt / 0.01)) * env(m_, 0.001, 0.32)
            put(t, x * v * 0.6, pan=0.3, send=0.18)
            put(t + BEAT * 0.5, x * v * 0.14, pan=-0.3)
        elif k == "lead":                                        # spacecraft voice: soft pulse lead with vibrato
            m_ = int(1.6 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"])
            ph = 2 * np.pi * np.cumsum(f * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * tt) * np.minimum(1, tt / 0.3))) / SR
            sq = np.sign(np.sin(ph)) * 0.5 + 0.5 * np.sin(ph)
            b, a = butter(1, 3200 / (SR / 2)); x = lfilter(b, a, sq) * env(m_, 0.01, 0.6)
            put(t, x * v * 0.42, pan=0.0, send=0.35)
            for e_ in (1, 2): put(t + e_ * BEAT * 0.75, x * v * 0.42 * 0.35 ** e_, pan=0.4 * (-1) ** e_)
        elif k == "crash":
            m_ = int(2.2 * SR); b, a = butter(2, 5000 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * env(m_, 0.002, 0.6) * v * 0.5, send=0.2)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR; b, a = butter(2, 2500 / (SR / 2), "high")
            put(t, lfilter(b, a, rng.standard_normal(m_)) * (tt / kw["d"]) ** 2 * v)
    def reverb(x):
        out = np.zeros_like(x)
        for dl, g in ((1557, 0.78), (1617, 0.77), (1491, 0.79), (1422, 0.78)):
            y = x.copy()
            for i in range(dl, len(y), dl): y[i:i + dl] += g * y[i - dl:i][:len(y[i:i + dl])]
            out += y * 0.25
        return out
    b, a = butter(1, 4500 / (SR / 2))
    L += lfilter(b, a, reverb(fxL)) * 0.32; R += lfilter(b, a, reverb(np.roll(fxR, 300))) * 0.32
    b, a = butter(2, 12000 / (SR / 2)); L = lfilter(b, a, L); R = lfilter(b, a, R)
    # gentle sidechain pump on the kick
    tt = np.arange(n) / SR; duck = np.ones(n)
    for kt in KICKS:
        i0 = int(kt * SR); i1 = min(n, i0 + int(0.25 * SR))
        if i0 < n: duck[i0:i1] = np.minimum(duck[i0:i1], 1 - 0.22 * np.exp(-np.arange(i1 - i0) / SR / 0.08))
    L *= duck; R *= duck
    fade = np.clip((TOTAL - tt) / 2.0, 0, 1); L *= fade; R *= fade
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
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}.png")
    elif mode == "at":                                             # preview at absolute times
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print([(REC[i]["year"], REC[i]["lane"][0], round(t, 2), pitch(i)) for i, t in enumerate(RT)])
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
