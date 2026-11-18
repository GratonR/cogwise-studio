"""BEEPMELODY — 1930: 435 M DOWN. 1960: 10,916 M. (the race to the deep)
45 human depth records in three lanes (one breath, divers on suits / breathing gas, crewed subs), 1930 -> 2019.
Every note = a new record in its lane; each lane walks DOWN its own ladder (deeper = lower note).
Co-pilot decisions (Guillaume, 2026-11-18): step 1 = option A (camera follows the deepest lane, the two others
stay at the top as landmarks), step 2 = mood C (breakbeat 160 BPM, saturated sub bass, bubbles / plucks / minor stabs,
sub boom on 10,916 m). Same data clock as the mood excerpts (deep_race_moods.py): 1 unit = 0.75 s = 2 beats.
Data: deep_race_draft.csv (2 sources per row) + deep_race_landmarks.csv.

    python3 deep_race.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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

FXK = float(os.environ.get("PI_FX", "0.6"))

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "deep_race_draft.csv"))))
LM = list(csv.DictReader(open(os.path.join(HERE, "deep_race_landmarks.csv"))))
for r in REC:
    r["m"] = float(r["metres"]); r["L"] = math.log10(r["m"]); r["year"] = r["date"][:4]
N = len(REC)
LANES = ["breath", "suit", "sub"]
LANE_NAME = {"breath": "ONE BREATH", "suit": "DIVER", "sub": "SUB"}
HUD_NAME = {"breath": "ONE-BREATH", "suit": "DIVER", "sub": "SUB"}

def fmt_si(r):
    m = r["m"]
    return f"{m:,.1f} M" if m != int(m) else f"{int(m):,} M"
def fmt_us(r): return f"{int(r['us']):,} FT"

TAG_FIX = {"1960-01-23": "US NAVY: 10,911 M", "2019-04-28": "GUINNESS, ±3 M"}
def tag(r):
    if r["date"] in TAG_FIX: return TAG_FIX[r["date"]]
    n = r["note"].lower()
    if "ratified=0" in n or "not recognized" in n or "training dive" in n: return "NOT RATIFIED"
    if "disputed" in n and r["lane"] == "breath": return "DISPUTED"
    if r["approx"] == "1": return "EST."
    return ""
WHO_FIX = {"1956-10-12": "George Wookey, Royal Navy", "2006-08-01": "Daniel P. Jackson, US Navy",
           "1975-06-06": "William R. Rhodes, US Navy", "1948-08-28": "Wilfred Bollard, Royal Navy",
           "1945-08-07": "Arne Zetterström, Swedish Navy"}
def who(r):
    if r["date"] in WHO_FIX: return WHO_FIX[r["date"]]
    w = r["who"].split(" (")[0].replace("&", "+").replace("; ", " + ")
    return w if len(w) <= 38 else w[:37].rstrip() + "."
def vehicle(r):
    v = r["vehicle"].split(" (")[0]
    return {"HELIOX HELMET": "HELMET, HELIUM MIX", "HYDROX HELMET": "HELMET, HYDROGEN MIX", "VARIABLE WEIGHT": "WEIGHTED DESCENT",
            "NO LIMITS SLED": "NO-LIMITS SLED", "MIXED-GAS OPEN CIRCUIT": "MIXED GAS", "BELL BOUNCE": "DIVING BELL",
            "BELL BOUNCE / SATURATION AT SEA": "DIVING BELL", "SATURATION AT SEA": "SATURATION DIVE",
            "ADS 2000 SUIT": "HARD SUIT (ADS 2000)"}.get(v, v.upper())

def kind(r):
    v = r["vehicle"]
    if r["lane"] == "breath": return "freediver"
    if r["lane"] == "suit": return "hardsuit" if "ADS" in v else "helmet"
    if "Bathysphere" in v or "Benthoscope" in v: return "sphere"
    if "Trieste" in v or "FNRS" in v: return "scaphe"
    return "modern"

# ================= palette (light surface -> deep navy) =================
INK = (30, 40, 70)
INK2 = (88, 100, 134)
CORAL = (236, 96, 72)
GOLD = (238, 174, 56)
CREAM = (252, 248, 238)
WHITE = (255, 255, 255)
FOAM = (226, 240, 246)
LCOL = {"breath": CORAL, "suit": GOLD, "sub": (110, 226, 204)}      # on the water
HCOL = {"breath": CORAL, "suit": (196, 128, 20), "sub": (18, 128, 116)}  # on the cream HUD
WATER = [(1.0, (204, 234, 242)), (1.8, (150, 204, 228)), (2.3, (92, 156, 204)), (2.8, (48, 98, 158)),
         (3.3, (26, 58, 112)), (3.8, (14, 30, 72)), (4.5, (8, 14, 40))]

# ================= timeline (160 BPM, all on the beat) =================
BPM = 160.0
BEAT = 60.0 / BPM
INTRO_B = 12
def gap_beats(i):
    dy = int(REC[i]["year"]) - int(REC[i - 1]["year"])
    if dy == 0: return 2
    if dy <= 6: return 3
    if dy <= 25: return 4
    return 8
GAPS_B = [gap_beats(i) for i in range(1, N)]
HOLD_B, OUTRO_B = 16, 22
RT = [INTRO_B * BEAT]
for g in GAPS_B: RT.append(RT[-1] + g * BEAT)
T_FINAL = RT[-1]
TOTAL = T_FINAL + (HOLD_B + OUTRO_B) * BEAT
def first_year(y): return next(i for i, r in enumerate(REC) if int(r["year"]) >= y)
def by_date(d): return next(i for i, r in enumerate(REC) if r["date"] == d)
I1950, I1960, I1963 = first_year(1950), first_year(1960), first_year(1963)
SC = [("intro", RT[0]), ("early", RT[I1950] - RT[0]), ("trieste", RT[I1963] - RT[I1950]),
      ("long", T_FINAL - RT[I1963]), ("final", HOLD_B * BEAT), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

L_START = 1.25                                   # every craft waits at ~18 m before its first record
def lane_state(T, lane):
    """(L, moving, kind, last index) of the lane's craft at T"""
    idx = [i for i in range(N) if REC[i]["lane"] == lane]
    done = [i for i in idx if RT[i] <= T]
    nxt = [i for i in idx if RT[i] > T]
    L0 = REC[done[-1]]["L"] if done else L_START
    kd = kind(REC[done[-1]]) if done else kind(REC[idx[0]])
    if nxt:
        j = nxt[0]; cb = min(4, GAPS_B[j - 1]) * BEAT * 0.9
        if T >= RT[j] - cb:
            return lerp(L0, REC[j]["L"], ease((T - (RT[j] - cb)) / cb)), True, kind(REC[j]), (done[-1] if done else -1)
    return L0, False, kd, (done[-1] if done else -1)

# camera: top fixed at L_TOP, bottom follows the deepest lane (subs) -> zooms out as they go down
Y_TOP, Y_BOT, L_TOP = 96.0, 292.0, 1.25
def l_bottom(T):
    Ls, _, _, _ = lane_state(T, "sub")
    return max(2.75, Ls + 0.30)
def ppd(T): return (Y_BOT - Y_TOP) / (l_bottom(T) - L_TOP)
def y_of(L, T): return Y_TOP + (L - L_TOP) * ppd(T)
def L_at(y, T): return L_TOP + (y - Y_TOP) / ppd(T)

# ================= music plan (shared by picture + audio) =================
PENTA = [0, 3, 5, 7, 10]                                         # D minor pentatonic
def deg(k): o, s = divmod(k, 5); return 50 + 12 * o + PENTA[s]   # degree 0 = D3
LANE_TOP = {"breath": 13, "suit": 9, "sub": 6}
LANE_SPAN = {"breath": 8, "suit": 5, "sub": 7}
def pitch(i):
    ln = REC[i]["lane"]; idx = [j for j in range(N) if REC[j]["lane"] == ln]; r = idx.index(i)
    return deg(LANE_TOP[ln] - int(round(r * LANE_SPAN[ln] / max(1, len(idx) - 1))))
TRIESTE = by_date("1960-01-23")
EV = []
def ev(t, k, **kw): EV.append((t, k, kw))
def build():
    nb = int(round(TOTAL / BEAT))
    RO = [38, 38, 34, 36]
    ev(0.08, "sonar", m=62, v=0.45)
    groove_end = T_FINAL + HOLD_B * BEAT
    for bar in range(nb // 4 + 1):
        tb = bar * 4 * BEAT; ro = RO[bar % 4]
        if tb >= TOTAL: break
        if tb < groove_end:
            full = tb >= RT[0] - 0.01
            for h in range(8): ev(tb + h * BEAT / 2, "hat", v=(0.08 if h % 2 else 0.05) * (1 if full else 0.7), d=0.012 if h % 2 else 0.03)
            for k, p in enumerate([0, .75, 1.5, 2.5, 3]):
                ev(tb + p * BEAT, "bass", m=ro + (12 if k == 2 else 0), d=0.4 * BEAT, v=0.26 if full else 0.16)
            if full:
                for p in (0, 2.5): ev(tb + p * BEAT, "kick", v=0.6)
                for p in (1, 3): ev(tb + p * BEAT, "snare", v=0.3)
                ev(tb + 3.75 * BEAT, "snare", v=0.1)
        else:
            ev(tb, "pad", ch=(50, 53, 57) if bar % 2 == 0 else (46, 50, 53), d=4 * BEAT, v=0.07)
            ev(tb, "bass", m=ro, d=3 * BEAT, v=0.14)
    for i, t in enumerate(RT):
        ln = REC[i]["lane"]; f = pitch(i) + 12
        ev(t, {"breath": "bubble", "suit": "pluck", "sub": "stab"}[ln], m=f, v=1.0, i=i)
    ev(RT[TRIESTE], "boom", v=0.5); ev(RT[TRIESTE], "noise", v=0.16)
    ev(T_FINAL, "boom", v=0.42); ev(T_FINAL, "noise", v=0.14)
    for k, d in enumerate([0, 3, 7, 12, 15, 19]):                     # falling-then-rising arpeggio on the final record
        ev(T_FINAL + (k + 1) * BEAT / 2, "bubble", m=62 + d, v=0.6)
    ev(T_FINAL - 4 * BEAT, "riser", d=4 * BEAT, v=0.12)
    ev(RT[TRIESTE] - 4 * BEAT, "riser", d=4 * BEAT, v=0.12)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= drawing =================
def water_col(L):
    for (l0, c0), (l1, c1) in zip(WATER, WATER[1:]):
        if L <= l1:
            f = max(0.0, min(1.0, (L - l0) / (l1 - l0))); return tuple(c0[j] + (c1[j] - c0[j]) * f for j in range(3))
    return WATER[-1][1]
def is_dark(L): return L > 2.55

_SNOW = [(random.Random(s).uniform(0, AW), random.Random(s + 999).uniform(0, 1), random.Random(s + 77).random()) for s in range(260)]
def background(T):
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        a[y, :] = water_col(L_at(y, T))
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    # light rays near the top, marine snow deeper
    for k in range(5):
        x0 = 20 + k * 38 + 6 * math.sin(T * 0.6 + k)
        for y in range(88, 150, 2):
            q = 1 - (y - 88) / 62
            if random.random() < 0.5 * q: d.point((int(x0 + (y - 88) * 0.35), y), fill=(232, 246, 250))
    for x, u, r in _SNOW:
        y = 88 + ((u * 210 + T * (3 + 4 * r)) % 210)
        if is_dark(L_at(y, T)) and r > 0.3:
            d.point((int(x + 2 * math.sin(T + r * 9)), int(y)), fill=(150, 176, 210) if r > 0.7 else (90, 120, 170))
    # sea floor appears once the subs reach the trench
    yf = y_of(math.log10(10994), T)
    if yf < AH:
        for x in range(AW):
            h = yf + 2 * math.sin(x / 11.0) + 1.5 * math.sin(x / 4.7 + 1)
            d.line([x, h, x, AH], fill=(40, 36, 52))
    return img

def dashed(d, y, x0, x1, col, on=2, off=2):
    x = x0
    while x < x1: d.line([x, y, min(x1, x + on - 1), y], fill=col); x += on + off

def freediver(d, x, y, col):            # head down, long fins up
    d.ellipse([x - 2, y + 2, x + 2, y + 6], fill=(250, 214, 184))            # head (bottom)
    d.rectangle([x - 2, y - 5, x + 2, y + 2], fill=(30, 36, 50))             # suit
    d.line([x - 1, y - 6, x - 2, y - 12], fill=col); d.line([x + 1, y - 6, x + 2, y - 12], fill=col)   # fins
    d.point((x - 2, y + 4), fill=INK)
def helmet(d, x, y, col):
    d.ellipse([x - 4, y - 8, x + 4, y], fill=(196, 160, 90), outline=INK)
    d.rectangle([x - 2, y - 6, x + 2, y - 3], fill=(170, 210, 230))
    d.rectangle([x - 3, y, x + 3, y + 7], fill=(150, 130, 100))
    d.line([x - 3, y + 7, x - 3, y + 10], fill=(150, 130, 100)); d.line([x + 3, y + 7, x + 3, y + 10], fill=(150, 130, 100))
    d.line([x, y - 8, x, y - 14], fill=FOAM)                                  # air hose
def hardsuit(d, x, y, col):
    d.ellipse([x - 4, y - 9, x + 4, y - 1], fill=col, outline=INK)
    d.rectangle([x - 2, y - 7, x + 2, y - 4], fill=(30, 50, 80))
    d.rectangle([x - 4, y - 1, x + 4, y + 6], fill=col, outline=INK)
    d.rectangle([x - 6, y, x - 5, y + 5], fill=col); d.rectangle([x + 5, y, x + 6, y + 5], fill=col)
    d.rectangle([x - 3, y + 7, x - 1, y + 10], fill=col); d.rectangle([x + 1, y + 7, x + 3, y + 10], fill=col)
def sphere(d, x, y, col):
    d.line([x, y - 6, x, 86], fill=(200, 210, 220))                            # the cable
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(70, 80, 96), outline=(20, 24, 34))
    d.ellipse([x - 2, y - 2, x + 1, y + 1], fill=(250, 220, 120))
def scaphe(d, x, y, col):
    d.rounded_rectangle([x - 9, y - 7, x + 9, y + 1], radius=3, fill=(214, 220, 228), outline=INK)
    d.rectangle([x - 1, y - 9, x + 3, y - 7], fill=(214, 220, 228), outline=INK)
    d.ellipse([x - 3, y + 1, x + 3, y + 7], fill=(60, 70, 86), outline=(20, 24, 34))
    d.point((x, y + 4), fill=(250, 220, 120))
def modern(d, x, y, col):
    d.rounded_rectangle([x - 8, y - 5, x + 8, y + 4], radius=2, fill=WHITE, outline=INK)
    d.rectangle([x - 8, y - 5, x + 8, y - 3], fill=(40, 110, 200))
    d.ellipse([x - 3, y - 1, x + 2, y + 4], fill=(60, 70, 86))
    d.point((x - 6, y + 5), fill=(250, 220, 120)); d.point((x + 6, y + 5), fill=(250, 220, 120))
SPRITE = {"freediver": freediver, "helmet": helmet, "hardsuit": hardsuit, "sphere": sphere, "scaphe": scaphe, "modern": modern}

AXX = 34
LX = {"breath": 56, "suit": 92, "sub": 126}
LAB_X = 134                                             # landmark labels live in a right-hand column
def draw_scene(c, T):
    c.art = background(T); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    d.line([AXX, 88, AXX, 296], fill=INK2)
    for e in (2, 3, 4):
        for m in (1, 2, 5):
            L = e + math.log10(m); y = y_of(L, T)
            if not (90 < y < 294): continue
            light = is_dark(L)
            if m == 1:
                d.line([AXX - 3, y, AXX + 2, y], fill=CREAM if light else INK)
                text(W, AXX * 2 - 8, int(y * 2) - 10, {2: "100 M", 3: "1 KM", 4: "10 KM"}[e], fill=CREAM if light else INK, align="r")
            else:
                d.line([AXX - 1, y, AXX + 1, y], fill=(170, 186, 210) if light else INK2)
    # landmarks: dashed line across, two-line label in the right column (name above, value below)
    for lm in LM:
        L = math.log10(float(lm["metres"])); y = y_of(L, T)
        if 96 < y < 280:
            col = (176, 200, 228) if is_dark(L) else INK2
            dashed(d, int(y), AXX + 2, 178, col)
            vals = [lm["label"], f"{int(float(lm['metres'])):,} M", f"{int(lm['us_ft']):,} FT"]
            ys = {"titanic": (-57, -39, -21), "everest": (3, 21, 39)}.get(lm["key"], (-21, 2, 20))
            for v_, dy in zip(vals, ys): text(W, 352, int(y * 2) + dy, v_, fill=col, align="r")
            if lm["key"] == "everest":                       # the mountain, hanging upside down from the line
                yi = int(y) + 1
                d.polygon([(137, yi), (147, yi), (142, yi + 8)], fill=(150, 160, 180))
                d.polygon([(140, yi), (144, yi), (142, yi + 3)], fill=WHITE)
    for ln in LANES:
        x = LX[ln]
        for yy in range(88, 296, 4): d.point((x, yy), fill=tuple(int(v * 0.45 + 200 * 0.25) for v in LCOL[ln]))
    k = rec_index(T)
    for i in range(k + 1):                                  # past records = ticks on each lane
        r = REC[i]; y = y_of(r["L"], T); x = LX[r["lane"]]
        if 88 < y < 296: d.rectangle([x - 4, int(y), x + 4, int(y)], fill=LCOL[r["lane"]])
    for ln in LANES:
        L, moving, kd, last = lane_state(T, ln)
        x = LX[ln]; y = y_of(L, T)
        if moving:                                          # bubbles rising from the craft
            for b in range(6):
                by = y - 10 - ((T * 40 + b * 9) % 50)
                if by > 88: d.point((int(x + 3 * math.sin(T * 7 + b)), int(by)), fill=FOAM)
        bob = 0 if moving else int(round(1.0 * math.sin(T * 2.2 + x)))
        if not (80 < y < 304): continue
        y = int(y) + bob
        SPRITE[kd](d, x, y, LCOL[ln])
        if last >= 0 and 0 <= T - RT[last] < 0.45:
            a = T - RT[last]; rr = 5 + a * 40
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=WHITE if a < 0.18 else LCOL[ln])

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    if k < 0:
        text(W, 28, 22, "THE RACE TO THE DEEP", fill=INK2); text(W, 28, 44, "SURFACE", size=40, fill=INK); return
    r = REC[k]; age = T - RT[k]; col = HCOL[r["lane"]]
    text(W, 28, 22, f"NEW {HUD_NAME[r['lane']]} RECORD", fill=col)
    text(W, 28, 44, fmt_si(r), size=40, fill=col if age < 0.22 else INK)
    text(W, 28, 92, fmt_us(r) + " DOWN", fill=INK2)
    text(W, 334, 44, r["year"], size=40, fill=GOLD, align="r")
    text(W, 334, 92, f"#{k + 1} / {N}", fill=INK2, align="r")
    W.rectangle([16, 128, 344, 172], fill=(250, 250, 252)); W.rectangle([16, 128, 19, 172], fill=col)
    n = int(min(60, age * 70))
    text(W, 28, 131, who(r)[:max(0, n)], fill=INK)
    tg = tag(r); sub = vehicle(r) + ("  · " + tg if tg else "")
    if age > 0.12: text(W, 28, 151, sub[:40], fill=col if not tg else INK2)

def legend(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([0, 604, 360, 640], fill=CREAM); W.rectangle([0, 604, 360, 605], fill=INK2)
    for ln in LANES:
        cnt = sum(1 for i in range(k + 1) if REC[i]["lane"] == ln)
        x = LX[ln] * 2
        hot = k >= 0 and REC[k]["lane"] == ln and T - RT[k] < 0.3
        text(W, x, 608, LANE_NAME[ln], fill=HCOL[ln], align="c")
        text(W, x, 622, str(cnt), fill=INK if not hot else HCOL[ln], align="c")
    text(W, 6, 615, "(LOG)", fill=INK2)

BANNERS = {by_date("1934-08-15"): ("ALMOST 1 KM DOWN", "IN A STEEL BALL ON A CABLE", False),
           TRIESTE: ("THE VERY BOTTOM", "CHALLENGER DEEP · 10,916 M", True),
           by_date("1976-11-23"): ("100 M ON ONE BREATH", "JACQUES MAYOL", False),
           by_date("2006-08-01"): ("2,000 FT IN A HARD SUIT", "610 M · US NAVY", False),
           by_date("2012-06-06"): ("DEEPEST BREATH-HOLD EVER", "253.2 M · NOT RATIFIED", False),
           N - 1: ("NEW RECORD!", "+18 M, 59 YEARS LATER", True)}
def banner(c, T):
    k = None
    for kb in BANNERS:
        hold = HOLD_B * BEAT if kb == N - 1 else 2.6
        if 0.1 < T - RT[kb] < hold: k = kb
    if k is None: return
    a = T - RT[k]
    tt, sub, big = BANNERS[k]; W = c.t; yb = 330
    w = (16 if big else 8) * len(tt) + 30; w = min(340, max(w, 8 * len(sub) + 30))
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
    text(W, 28, 26, "1930: 435 M DOWN.", size=40, fill=INK)
    if t > 0.5: text(W, 28, 64, "1960: 10,916 M.", size=40, fill=HCOL["sub"])
    if t > 1.1: text(W, 28, 112, "EVERY NOTE = A NEW DEPTH RECORD", fill=INK2)
    if t > 1.7:
        text(W, 28, 140, "ONE BREATH", fill=HCOL["breath"]); text(W, 116, 140, "VS", fill=INK2)
        text(W, 142, 140, "DIVER", fill=HCOL["suit"]); text(W, 190, 140, "VS", fill=INK2)
        text(W, 216, 140, "SUB", fill=HCOL["sub"])
    if t > 2.3:
        W.rectangle([70, 330, 290, 372], fill=CREAM); W.rectangle([70, 330, 290, 332], fill=GOLD)
        text(W, 180, 333, f"{N} RECORDS", fill=INK, align="c")
        text(W, 180, 352, "1930 TO 2019", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T); W = c.t
    W.rectangle([16, 40, 344, 330], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=CORAL)
    text(W, 180, 50, "DEEPEST EACH WAY", fill=INK2, align="c")
    rows = [("ONE BREATH", "253.2 M", "831 FT · 2012 · NOT RATIFIED", "breath"),
            ("DIVER", "610 M", "2,000 FT · 2006 · HARD SUIT", "suit"),
            ("SUB", "10,934 M", "35,872 FT · 2019 · LIMITING FACTOR", "sub")]
    for j, (a, b, s, ln) in enumerate(rows):
        if t > 0.5 + j * 0.8:
            y = 78 + j * 64
            text(W, 30, y, a, fill=HCOL[ln]); text(W, 330, y - 6, b, size=40, fill=INK, align="r")
            text(W, 330, y + 32, s, fill=INK2, align="r")
    if t > 3.4: text(W, 180, 278, "WHAT'S THE NEXT NOTE?", fill=GOLD, align="c")
    if t > 4.4:
        W.rectangle([16, 520, 344, 590], fill=CREAM)
        text(W, 180, 526, "SELECTED RECORDS. DATA: GUINNESS,", fill=INK2, align="c")
        text(W, 180, 546, "US NAVY, BRITANNICA, NAT GEO, AIDA,", fill=INK2, align="c")
        text(W, 180, 566, "COMEX, AILARA (FREEDIVING HISTORY)", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "trieste": sc_main("trieste"), "long": sc_main("long"),
           "final": sc_main("final"), "outro": sc_outro}

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
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    z = 1.0 + 0.008 * kp * FXK
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if k >= 0 and 0 <= T - RT[k] < 0.10:
        fr = np.minimum(255, fr.astype(np.int16) + int(50 * FXK * (1 - (T - RT[k]) / 0.10))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio (mood C, same voices as deep_race_moods.py) =================
SR = 44100
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    RNG = np.random.default_rng(7)
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def env(n, a, d): t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
    def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def bp(x, f1, f2): b, a = butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band"); return lfilter(b, a, x)
    def tt(d): return np.arange(int(d * SR)) / SR
    n = int((TOTAL + 2.0) * SR); buf = np.zeros((n, 2))
    def put(t, sig, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(sig)); s = sig[:j - i] * g
        buf[i:j, 0] += s * np.sqrt((1 - pan) / 2) * 1.41; buf[i:j, 1] += s * np.sqrt((1 + pan) / 2) * 1.41
    def bubble(f, d=.18):
        t = tt(.6); ph = 2*np.pi*np.cumsum(f*(1+.35*(1-np.exp(-t*25))))/SR; return np.sin(ph) * env(len(t), .001, d)
    def pluck(f, d=.22):
        t = tt(.8); ph = (f*t) % 1; return lp(2*ph - 1, 2600) * env(len(t), .001, d)
    def boom(f=36.7, d=2.5):
        t = tt(5.0); ph = 2*np.pi*np.cumsum(f*(1+1.5*np.exp(-t*8)))/SR; return np.tanh(1.6*np.sin(ph)) * env(len(t), .003, d)
    def sonar(f, d=1.4):
        t = tt(3.5); return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*f*2.01*t)*np.exp(-t*3)) * env(len(t), .004, d)
    def kick(g=1, f1=50, dec=.12):
        t = tt(.4); return g*np.sin(2*np.pi*np.cumsum(f1+110*np.exp(-t/.035))/SR)*env(len(t), .001, dec)
    def snare():
        t = tt(.28); return bp(RNG.standard_normal(len(t)), 1200, 7000)*env(len(t), .001, .08)*1.4 + .4*np.sin(2*np.pi*190*t)*env(len(t), .001, .04)
    def hat(d=.016): t = tt(.08); return hp(RNG.standard_normal(len(t)), 8000)*env(len(t), .001, d)
    def bassnote(m, d, drive=3.0):
        t = tt(d + .05); f = mtof(m); return np.tanh(drive*np.sin(2*np.pi*f*t) + .4*np.sin(4*np.pi*f*t))*env(len(t), .004, .5)*np.clip((d + .03 - t)/.04, 0, 1)
    def pad(ms, d):
        t = tt(d + 1.0); e = np.minimum(1, t/.8)*np.clip((d + .8 - t)/.8, 0, 1)
        return sum(np.sin(2*np.pi*mtof(m)*t) + .5*np.sin(2*np.pi*mtof(m)*1.004*t) for m in ms) * e
    for t, k, kw in EV:
        v = kw.get("v", .3)
        if k == "hat": put(t, hat(kw.get("d", .016)), v, .4)
        elif k == "kick": put(t, kick(), v)
        elif k == "snare": put(t, snare(), v)
        elif k == "bass": put(t, lp(bassnote(kw["m"], kw["d"]), 700), v)
        elif k == "pad": put(t, pad(kw["ch"], kw["d"]), v)
        elif k == "sonar": put(t, sonar(mtof(kw["m"])), v)
        elif k == "boom": put(t, boom(), v)
        elif k == "noise": put(t, hp(RNG.standard_normal(int(2.2*SR)), 4000)*env(int(2.2*SR), .002, .7), v)
        elif k == "riser": d = kw["d"]; put(t, hp(RNG.standard_normal(int(d*SR)), 2500) * (tt(d)/d)**2, v)
        elif k == "bubble":
            f = mtof(kw["m"]) * 2; put(t, bubble(f), .3 * v, -.35); put(t + BEAT, bubble(f), .1 * v, .35)
        elif k == "pluck":
            f = mtof(kw["m"]); put(t, pluck(f), .32 * v, .3); put(t + BEAT / 2, pluck(f), .1 * v, -.3)
        elif k == "stab":
            for j, m in enumerate((0, 3, 7)): put(t, pluck(mtof(kw["m"] - 12 + m), .3), .22 * v, -.2 + .2 * j)
    # light reverb
    out = buf.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
        k = int(d * .8 * SR); out[k:] += g * .6 * np.roll(buf, 7 if d > .2 else 0, axis=0)[:-k]
    buf = .82 * buf + .18 * lp(out.T, 5000).T
    tm = np.arange(n) / SR
    duck = np.ones(n)
    for kt in KICKS:
        i0 = int(kt * SR); i1 = min(n, i0 + int(.2 * SR))
        if i0 < n: duck[i0:i1] = np.minimum(duck[i0:i1], 1 - .2 * np.exp(-np.arange(i1 - i0) / SR / .07))
    buf *= duck[:, None]
    buf *= np.clip(tm / .03, 0, 1)[:, None] * np.clip((TOTAL - tm) / 2.0, 0, 1)[:, None]
    buf = buf / np.abs(buf).max() * .89
    wavfile.write(path, SR, (buf * 32767).astype(np.int16)); print(path, round(n / SR, 2), "s")

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
            name, tt_ = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt_))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt_}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).save(f"{out}/t{T:05.2f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print([(REC[i]["year"], REC[i]["lane"][0], round(t, 2), pitch(i), tag(REC[i])) for i, t in enumerate(RT)])
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
