"""BEEPMELODY — A GEYSER THAT KEEPS TIME.
Old Faithful, August 1985: 80 consecutive eruptions (#1 -> #80 of the 299 recorded by Azzalini & Bowman 1990).
Every note = one eruption, placed at its REAL start time (time compressed: 1 min of geyser = K s, 1 hour = 0.56 s).
Jet height on screen = eruption DURATION (said on screen), not the measured height. Night durations were only
coded short/medium/long (2/3/4 min) in the source: shown "EST." and the sky goes dark around them.
Scene: Upper Geyser Basin in light pixel art; the crowd on the boardwalk grows while the geyser makes people wait.
Music (co-pilot step 2c = C1a "tout bois"): 124 BPM clock groove, wood-block tick-tock, bass marimba, soft drums;
marimba hit = eruption (long = low + roll, short = high), steam hiss; drums drop during the 108 min wait, #61 relaunches.
Data: old_faithful_draft.csv (series) + old_faithful_facts.csv (today's interval: NPS + USGS + Hurwitz et al. 2014).

    python3 old_faithful.py info out | preview out <scene>:<s> | at out <T>... | audio out/music.wav | render out | final out x.mp4
    PALETTE=day (default, light DA) | warm (variant: golden-hour basin)
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
PAL = os.environ.get("PALETTE", "day")
DECOR = os.environ.get("DECOR", "toy")   # toy (step 3 v1) | doc | mesure | brume  (step 3b) | saisons (3b answer: toy + seasons) ; 3c answer: toy (summer only, matches AUG 1985) = FINAL
TOYISH = DECOR in ("toy", "saisons")

# ================= data =================
ALL = list(csv.DictReader(open(os.path.join(HERE, "old_faithful_draft.csv"))))
for r in ALL:
    r["n"] = int(r["n"]); r["w"] = int(r["wait_before_min"]); r["d"] = float(r["duration_min"])
    r["est"] = r["duration_note"].startswith("night")
NSHOW = 80
REC = ALL[:NSHOW]
N = len(REC)
W_ALL = [r["w"] for r in ALL]
AVG_ALL = sum(W_ALL) / len(W_ALL)                       # 72.3 min over the 299
I_MIN = min(range(N), key=lambda i: REC[i]["w"] if i else 999)   # #54, 43 min (min of the 299 too)
I_MAX = max(range(N), key=lambda i: REC[i]["w"] if i else 0)     # #61, 108 min (max of the 299 too)
assert REC[I_MIN]["w"] == min(W_ALL) and REC[I_MAX]["w"] == max(W_ALL)
def is_long(r): return r["d"] >= 3.0
def f1(x): return f"{math.floor(x * 10 + 0.5 + 1e-9) / 10:.1f}"   # round half up (1.95 -> 2.0)
SHORT_NEXT = [ALL[i + 1]["w"] for i in range(len(ALL) - 1) if not is_long(ALL[i])]
LONG_NEXT = [ALL[i + 1]["w"] for i in range(len(ALL) - 1) if is_long(ALL[i])]
AVG_AFTER_SHORT = sum(SHORT_NEXT) / len(SHORT_NEXT)      # 55.6
AVG_AFTER_LONG = sum(LONG_NEXT) / len(LONG_NEXT)         # 81.2
ELAPSED = [0]
for i in range(1, N): ELAPSED.append(ELAPSED[-1] + REC[i]["w"])   # minutes since eruption #1
HOURS_TOTAL = ELAPSED[-1] / 60.0

# ================= palette =================
if PAL == "warm":
    SKY_D = [(0, (120, 170, 214)), (90, (238, 196, 150)), (150, (250, 222, 170))]
else:
    SKY_D = [(0, (122, 184, 232)), (90, (186, 222, 244)), (150, (226, 240, 246))]
SKY_N = [(0, (22, 28, 62)), (90, (44, 50, 96)), (150, (78, 76, 120))]
HILL, PINE, PINE2 = (96, 140, 120), (40, 92, 70), (58, 116, 84)
SINTER, SINTER2, SINTER3 = (232, 226, 210), (210, 202, 184), (186, 176, 158)
POOL, POOL2, RIM = (64, 178, 196), (120, 214, 220), (214, 150, 70)
WOOD, WOOD2 = (150, 104, 66), (112, 76, 46)
STEAM, STEAM2 = (250, 252, 255), (206, 216, 228)
INK, INK2, CREAM = (34, 44, 60), (96, 108, 124), (250, 248, 240)
ACC, GOLD, RED, TEAL, ORNG = (40, 150, 170), (222, 150, 40), (210, 72, 56), (40, 160, 160), (226, 128, 48)
BLDG, ROOF = (196, 150, 104), (120, 72, 52)
if DECOR in ("doc", "brume"):
    SKY_D = ([(0, (150, 176, 196)), (90, (196, 210, 216)), (150, (220, 224, 220))] if DECOR == "doc"
             else [(0, (96, 116, 140)), (90, (150, 164, 178)), (150, (186, 192, 196))])
    HILL, PINE, PINE2 = ((112, 132, 150), (34, 52, 46), (46, 64, 54)) if DECOR == "doc" else ((86, 100, 118), (26, 36, 40), (34, 44, 48))
    SINTER, SINTER2, SINTER3 = ((206, 200, 186), (184, 176, 160), (156, 148, 134)) if DECOR == "doc" else ((176, 174, 168), (156, 154, 150), (132, 130, 128))
    POOL, POOL2, RIM = (70, 130, 140), (96, 160, 166), (168, 104, 52)
    WOOD, WOOD2 = (92, 78, 66), (66, 56, 48)
if DECOR == "mesure":
    SKY_D = [(0, (236, 238, 236)), (150, (236, 238, 236))]
    SINTER, SINTER2, SINTER3 = (226, 228, 224), (210, 212, 208), (186, 188, 184)
PEOPLE = [(210, 72, 56), (40, 120, 200), (230, 180, 40), (60, 150, 80), (150, 80, 160), (240, 240, 240), (40, 40, 50), (230, 120, 160)]

# ================= timeline (124 BPM, 16th-note grid) =================
BPM = 124.0
S16 = 60.0 / BPM / 4
K = 0.0093                    # s of video per minute of geyser time (1 h = 0.558 s)
T0 = 1.0                      # eruption #1
def q(t): return round(t / S16) * S16
RT = [q(T0 + K * e) for e in ELAPSED]
T_FINAL = RT[-1]
HOLD = 4.0
OUTRO = 8.0
TOTAL = T_FINAL + HOLD + OUTRO
INTRO_END = 3.6
def at_n(n): return RT[n - 1]
SC = [("intro", INTRO_END), ("day1", at_n(22) - INTRO_END), ("day2", at_n(44) - at_n(22)),
      ("day3", at_n(62) - at_n(44)), ("day4", T_FINAL + HOLD - at_n(62)), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n_, d_ in SC: START[n_] = acc_; acc_ += d_
DUR = dict(SC); NAMES = [n for n, _ in SC]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# night factor: around the eruptions whose duration is a night estimate (source = no daylight observation)
_NIGHT_PTS = [RT[i] for i in range(N) if REC[i]["est"]]
def night(T):
    if not _NIGHT_PTS: return 0.0
    dmin = min(abs(T - t) for t in _NIGHT_PTS)
    return float(np.clip(1.0 - (dmin - 0.35) / 0.9, 0, 1)) * 0.85

# ================= music events (C1a · tout bois) =================
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
HI_N, LO_N = [76, 79, 81, 84, 88], [57, 60, 64, 67, 69]
BASS = [33, 33, 36, 31]
QUIET = (RT[I_MAX - 1] + 0.5, RT[I_MAX])      # the 108 min wait: drums and bass drop
def build():
    nb = int((TOTAL + 0.5) / S16)
    for k in range(nb):
        b = k * S16
        if b > T_FINAL + HOLD + 2.0: break
        quiet = QUIET[0] <= b < QUIET[1]
        groove_on = b >= T0 - 4 * S16 and b < T_FINAL + HOLD
        if k % 2 == 0: ev(b, "wood", f=1900 if k % 4 == 0 else 1400, v=.06 if k % 4 == 0 else .04)
        else: ev(b, "wood", f=2600, v=.012)
        if quiet or not groove_on: continue
        chord = int(b // 1.935) % 4
        if k % 4 == 0: ev(b, "kick", v=.26)
        if k % 8 == 4: ev(b, "snare", v=.06)
        if k % 2 == 1: ev(b, "bass", m=BASS[chord] + 12, v=.22)
    for i, t in enumerate(RT):
        r = REC[i]; lg = is_long(r)
        m = (LO_N if lg else HI_N)[i % 5]
        ev(t, "erupt", m=m, long=lg, d=r["d"], v=.2 + (.06 if i == I_MAX else 0), n=r["n"])
        if i == I_MAX: ev(t, "relaunch", v=1.0)
    for k, mm in enumerate((57, 64, 69, 76, 81)): ev(T_FINAL + HOLD * .25 + (k + 1) * 2 * S16, "erupt", m=mm, long=False, d=2.0, v=.14, n=0)
    EV.sort(key=lambda e: e[0])
build()
KICKS = sorted(t for t, k, _ in EV if k == "kick")

# ================= scene =================
def mix(c0, c1, f): return tuple(int(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
def grad(stops, y):
    for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
        if y <= y1: return mix(c0, c1, max(0.0, min(1.0, (y - y0) / (y1 - y0))))
    return stops[-1][1]

Y_HILL = 150
VX, VY = 90, 214                 # vent of the cone
def ridge(x): return Y_HILL - 10 - 7 * math.sin(x / 21 + 0.7) - 3 * math.sin(x / 7.3 + 2)

def _ground():
    if TOYISH: return _ground_toy()
    return _ground_sober()

def _ground_sober():
    """doc / brume / mesure: real-looking basin, no cottage, no toy pools"""
    img = Image.new("RGBA", (AW, AH), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rng = random.Random(3)
    if DECOR != "mesure":
        far = (150, 166, 184) if DECOR == "doc" else (120, 134, 150)
        for x in range(AW):                                # distant plateau (Madison/Central plateau rims)
            y = Y_HILL - 34 - 10 * math.sin(x / 47 + 1.3) - 4 * math.sin(x / 13 + .4)
            d.line([x, y, x, Y_HILL], fill=far)
        for x in range(AW): d.line([x, ridge(x) + 2, x, Y_HILL + 10], fill=HILL)
        for _ in range(230):                               # dense lodgepole wall, thin and dark
            x = rng.uniform(-2, AW + 2); y0 = Y_HILL + rng.uniform(-8, 12); h = rng.choice([9, 11, 13, 15, 17])
            col = PINE if rng.random() < .65 else PINE2
            d.line([x, y0 - h, x, y0], fill=col)
            for k in range(2, h, 2):
                w = 1 + (k * 2) // h
                d.line([x - w, y0 - h + k, x + w, y0 - h + k], fill=col)
        for _ in range(12):                                # snags (dead trees, 1988 fire style)
            x = rng.uniform(0, AW); y0 = Y_HILL + rng.uniform(-4, 10)
            d.line([x, y0 - rng.choice([10, 14]), x, y0], fill=(120, 112, 104))
    d.rectangle([0, Y_HILL + 12, AW, AH], fill=SINTER)
    rs = random.Random(5)
    for _ in range(420):
        x = rs.uniform(0, AW); y = rs.uniform(Y_HILL + 14, AH); w = rs.choice([2, 3, 5, 8])
        d.line([x, y, x + w, y], fill=SINTER2 if rs.random() < .7 else SINTER3)
    # irregular sinter mound with terraces (not a perfect cake)
    for k in range(22):
        rw = 44 - k * 1.7 + 3 * math.sin(k * 1.9); y = VY + 12 - k * 0.7
        lo = VX - rw + 2 * math.sin(k); hi = VX + rw + 3 * math.cos(k * .7)
        d.polygon([(lo, y), (lo + 6, y - 4), (hi - 5, y - 4), (hi, y), (hi - 4, y + 3), (lo + 3, y + 3)],
                  fill=SINTER2 if k % 3 else SINTER3)
    d.ellipse([VX - 3, VY - 2, VX + 3, VY + 1], fill=(96, 88, 80))
    if DECOR != "mesure":
        mat1, mat2 = ((178, 124, 74), (150, 118, 86)) if DECOR == "doc" else ((140, 116, 96), (124, 110, 98))
        for (x0, y0, ln, dx) in ((VX - 10, VY + 10, 70, -1.0), (VX + 12, VY + 10, 80, 0.9), (VX + 2, VY + 14, 50, 0.2)):
            x, y = x0, y0                                  # runoff channels with bacterial mats (real orange/brown)
            for j in range(ln):
                x += dx * .8 + rs.uniform(-.6, .6); y += .45
                x += 1.2 * math.sin(j / 6.0)
                d.point((x, y), fill=mat1 if j % 5 else mat2); d.point((x + 1, y), fill=mat2)
        for (px, py, rw, rh) in ((22, 226, 12, 3), (156, 234, 9, 2)):   # flat irregular pools, low-key
            d.polygon([(px - rw, py), (px - rw * .4, py - rh), (px + rw * .6, py - rh + 1), (px + rw, py + 1),
                       (px + rw * .3, py + rh), (px - rw * .7, py + rh - 1)], fill=POOL)
            d.line([px - rw * .4, py, px + rw * .3, py], fill=POOL2)
        for x in range(-2, AW + 2):                        # boardwalk: straight, low, at the very front
            y = 262
            d.line([x, y, x, y + 3], fill=WOOD)
            if x % 10 == 0: d.line([x, y + 3, x, y + 6], fill=WOOD2)
    return img

SEASONS = ("spring", "summer", "autumn", "winter")
SEA = {   # hill, flats (sinter, sinter2, sinter3), sky stops — summer = the original toy decor
    "spring": dict(hill=(104, 184, 96), flat=((222, 232, 196), (188, 212, 150), (158, 196, 120)),
                   sky=[(0, (130, 196, 236)), (90, (196, 230, 240)), (150, (232, 246, 236))]),
    "summer": dict(hill=None, flat=None, sky=None),
    "autumn": dict(hill=(176, 150, 92), flat=((232, 220, 196), (214, 196, 166), (190, 168, 136)),
                   sky=[(0, (120, 166, 214)), (90, (220, 204, 176)), (150, (244, 222, 184))]),
    "winter": dict(hill=(226, 234, 244), flat=((242, 246, 252), (220, 230, 242), (198, 212, 230)),
                   sky=[(0, (150, 176, 204)), (90, (204, 218, 232)), (150, (232, 238, 244))]),
}
def _ground_toy(season="summer"):
    """everything below the sky, on a transparent layer"""
    S_ = SEA[season]
    hill = S_["hill"] or HILL; sinter, sinter2, sinter3 = S_["flat"] or (SINTER, SINTER2, SINTER3)
    img = Image.new("RGBA", (AW, AH), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for x in range(AW): d.line([x, ridge(x), x, Y_HILL + 10], fill=hill)
    rng = random.Random(3)
    for j in range(70):                                   # lodgepole pines (+ aspens that change with the season)
        x = rng.uniform(-2, AW + 2); y0 = Y_HILL + rng.uniform(-6, 12); h = rng.choice([8, 10, 12, 14])
        col = PINE if rng.random() < .6 else PINE2
        aspen = j % 4 == 1
        if aspen:
            col = {"spring": (150, 206, 110), "summer": (96, 160, 80), "autumn": (236, 176, 48) if j % 8 == 1 else (222, 122, 46),
                   "winter": None}[season]
            if col is None:                               # bare aspen: white trunk, thin branches
                d.line([x, y0 - h, x, y0 + 2], fill=(214, 206, 196)); d.line([x - 2, y0 - h + 3, x, y0 - h + 5], fill=(150, 140, 130))
                d.line([x + 2, y0 - h + 4, x, y0 - h + 6], fill=(150, 140, 130)); continue
            d.ellipse([x - 3, y0 - h, x + 3, y0 - 2], fill=col); d.line([x, y0 - 2, x, y0 + 2], fill=(214, 206, 196))
            if season == "spring" and j % 8 == 5: d.point((x, y0 - h + 3), fill=(250, 250, 250))
            continue
        d.polygon([(x, y0 - h), (x - 3, y0), (x + 3, y0)], fill=col); d.line([x, y0, x, y0 + 2], fill=WOOD2)
        if season == "winter":                            # snow on the branches
            d.polygon([(x, y0 - h), (x - 1.5, y0 - h + 4), (x + 1.5, y0 - h + 4)], fill=(250, 252, 255))
            d.line([x - 3, y0 - 1, x + 3, y0 - 1], fill=(240, 246, 252)); d.line([x - 2, y0 - h * .5, x + 1, y0 - h * .5], fill=(240, 246, 252))
    d.rectangle([0, Y_HILL + 12, AW, AH], fill=sinter)    # sinter flats
    rs = random.Random(5)
    for _ in range(320):
        x = rs.uniform(0, AW); y = rs.uniform(Y_HILL + 14, AH); w = rs.choice([2, 3, 4, 6])
        d.line([x, y, x + w, y], fill=sinter2 if rs.random() < .7 else sinter3)
    rf = random.Random(17)
    if season == "spring":                                # wildflowers on the hill and the edges of the flats
        for _ in range(110):                              # grass tufts on the flats
            x = rf.uniform(0, AW); y = rf.uniform(Y_HILL + 14, AH)
            if abs(x - VX) > 36 or y > VY + 16: d.line([x, y, x + 2, y], fill=(126, 184, 92))
        for _ in range(200):
            x = rf.uniform(0, AW); y = rf.choice([rf.uniform(Y_HILL - 6, Y_HILL + 10), rf.uniform(Y_HILL + 14, AH)])
            if abs(x - VX) < 36 and y > Y_HILL + 14: continue
            d.point((x, y), fill=rf.choice([(250, 220, 70), (236, 120, 170), (250, 250, 250), (170, 140, 230)]))
    if season == "autumn":                                # fallen leaves
        for _ in range(70):
            x = rf.uniform(0, AW); y = rf.uniform(Y_HILL + 14, AH)
            if abs(x - VX) > 34 or y > VY + 16: d.point((x, y), fill=rf.choice([(226, 140, 50), (236, 180, 60), (196, 96, 52)]))
    for k in range(18):                                   # the cone: low wide mound (stays snow-free: it is hot)
        rw = 30 - k * 1.3; y = VY + 10 - k * 0.6
        d.ellipse([VX - rw, y - 4, VX + rw, y + 4], fill=SINTER2 if k % 3 else SINTER3)
    if season == "winter":                                # rime frost ring at the foot of the cone
        d.arc([VX - 34, VY + 2, VX + 34, VY + 18], 0, 180, fill=(250, 252, 255))
    d.ellipse([VX - 3, VY - 2, VX + 3, VY + 1], fill=(120, 110, 96))
    for (px, py, rw, rh) in ((26, 222, 20, 8), (150, 230, 14, 6)):   # hot spring pools beside the cone
        d.ellipse([px - rw - 2, py - rh - 1, px + rw + 2, py + rh + 1], fill=RIM)
        d.ellipse([px - rw, py - rh, px + rw, py + rh], fill=POOL)
        d.ellipse([px - rw * .5, py - rh * .5, px + rw * .5, py + rh * .5], fill=POOL2)
    for (px, py, rw) in ((40, 268, 16), (130, 272, 22)):  # runoff channels in front of the boardwalk
        d.line([px - rw, py, px + rw, py + 2], fill=RIM); d.line([px - rw + 3, py + 1, px + rw - 3, py + 3], fill=(196, 170, 120))
    d.rectangle([132, 150, 176, 176], fill=BLDG)           # visitor center + clock
    d.polygon([(128, 151), (154, 136), (180, 151)], fill=ROOF)
    if season == "winter":                                # snow on the roof
        d.polygon([(128, 151), (154, 136), (180, 151), (176, 149), (154, 139), (132, 149)], fill=(250, 252, 255))
        d.line([128, 151, 180, 151], fill=(236, 242, 250))
    for wx in (138, 148, 160, 170): d.rectangle([wx - 2, 162, wx + 1, 168], fill=(110, 140, 170))
    d.rectangle([150, 168, 157, 176], fill=WOOD2)
    for x in range(-2, AW + 2):                           # boardwalk (arc in front of the cone)
        y = 252 + 0.0016 * (x - VX) ** 2
        d.line([x, y, x, y + 6], fill=WOOD)
        if x % 4 == 0: d.point((x, y + 3), fill=WOOD2)
        d.point((x, y - 4), fill=WOOD2)
        if x % 8 == 0: d.line([x, y - 4, x, y], fill=WOOD2)
    return img
_G = None
def ground():
    global _G
    if _G is None: _G = _ground()
    return _G
_GS = {}
def ground_s(season):
    if season not in _GS: _GS[season] = _ground_toy(season)
    return _GS[season]

# seasons (decor only, chosen by Guillaume at step 3b): one per "day" scene, 1.2 s cross-fade at each change
SEASON_AT = None
def season_at(T):
    """returns (season_a, season_b, f): blend f from a to b"""
    marks = [START["day2"], START["day3"], START["day4"]]
    k = sum(1 for m in marks if T >= m - 0.6)
    if k == 0: return SEASONS[0], SEASONS[0], 0.0
    f = float(np.clip((T - (marks[k - 1] - 0.6)) / 1.2, 0, 1))
    return SEASONS[k - 1], SEASONS[k], f

def _sky_stops(season): return SEA[season]["sky"] or SKY_D
def _bg_season(T, season):
    nf = night(T)
    img = Image.new("RGB", (AW, AH)); d = ImageDraw.Draw(img)
    for y in range(Y_HILL + 14):
        d.line([0, y, AW, y], fill=mix(grad(_sky_stops(season), y), grad(SKY_N, y), nf))
    if nf > 0.2:
        rs = random.Random(7)
        for _ in range(40):
            x, y = rs.randrange(AW), rs.randrange(130)
            if rs.random() < nf: d.point((x, y), fill=(230, 230, 250))
    g = ground_s(season); img.paste(g, (0, 0), g)
    return img

def _particles(img, T, season, alpha):
    """falling snow (winter), drifting leaves (autumn), petals (spring)"""
    if season == "summer" or alpha <= 0: return
    d = ImageDraw.Draw(img); rs = random.Random(23)
    cnt = {"winter": 90, "autumn": 16, "spring": 12}[season]
    for j in range(cnt):
        if rs.random() > alpha: rs.random(); rs.random(); rs.random(); continue
        x0 = rs.uniform(0, AW); y0 = rs.uniform(0, AH); sp = rs.uniform(.7, 1.3)
        if season == "winter":
            y = (y0 + T * 22 * sp) % (Y_HILL + 130); x = (x0 + 3 * math.sin(T * 1.3 + j)) % AW
            d.point((x, y), fill=(255, 255, 255))
            if j % 3 == 0: d.point((x + 1, y), fill=(255, 255, 255))
        else:
            y = (y0 + T * 12 * sp) % (Y_HILL + 120); x = (x0 + T * 6 * sp + 6 * math.sin(T * 2 + j)) % AW
            col = (226, 140, 50) if season == "autumn" and j % 2 else (236, 180, 60) if season == "autumn" else (246, 190, 210)
            d.point((x, y), fill=col); d.point((x + 1, y + (j % 2)), fill=col)

def background(T):
    if DECOR == "saisons":
        a, b, f = season_at(T); nf = night(T)
        img = _bg_season(T, a)
        if f > 0: img = Image.blend(img, _bg_season(T, b), f)
        _particles(img, T, a, 1 - f); _particles(img, T, b, f)
        if nf > 0:
            img = Image.blend(img, Image.new("RGB", (AW, AH), (20, 26, 60)), 0.45 * nf)
            d = ImageDraw.Draw(img)
            if nf > 0.3:
                for wx in (138, 148, 160, 170): d.rectangle([wx - 2, 162, wx + 1, 168], fill=(250, 220, 120))
        return img
    nf = night(T)
    img = Image.new("RGB", (AW, AH)); d = ImageDraw.Draw(img)
    for y in range(Y_HILL + 14):
        d.line([0, y, AW, y], fill=mix(grad(SKY_D, y), grad(SKY_N, y), nf))
    if nf > 0.2:
        rs = random.Random(7)
        for _ in range(40):
            x, y = rs.randrange(AW), rs.randrange(130)
            if rs.random() < nf: d.point((x, y), fill=(230, 230, 250))
    img.paste(ground(), (0, 0), ground())
    if DECOR in ("doc", "brume"):                          # other vents steaming in the basin: thin wisps
        d = ImageDraw.Draw(img)
        vents = ((22, 168, 18), (64, 164, 10), (126, 170, 14), (166, 162, 22)) if DECOR == "doc" else \
                ((14, 168, 30), (50, 164, 16), (122, 170, 24), (160, 164, 34), (176, 170, 18))
        for vi, (fx, fy, hh) in enumerate(vents):
            for y in range(hh):
                ph = T * 2.5 + vi * 1.7 - y * .18
                xx = fx + y * .25 + 1.5 * math.sin(ph); w = .6 + y * .07
                if (y + int(T * 20) + vi) % 9 < 7:
                    d.line([xx - w, fy - y, xx + w, fy - y], fill=STEAM2 if DECOR == "doc" else (206, 212, 218))
    if DECOR == "brume":                                   # low mist band over the flats
        mist = Image.new("RGB", (AW, AH), (214, 218, 222)); m = Image.new("L", (AW, AH), 0); md = ImageDraw.Draw(m)
        for y in range(Y_HILL - 10, Y_HILL + 40):
            md.line([0, y, AW, y], fill=int(150 * math.exp(-((y - Y_HILL - 6) / 14) ** 2)))
        img.paste(mist, (0, 0), m)
    if nf > 0:
        dark = Image.new("RGB", (AW, AH), (20, 26, 60))
        img = Image.blend(img, dark, 0.45 * nf)
        d = ImageDraw.Draw(img)
        if nf > 0.3 and DECOR == "toy":
            for wx in (138, 148, 160, 170): d.rectangle([wx - 2, 162, wx + 1, 168], fill=(250, 220, 120))
    return img

def clock_hand(d, T):
    """visitor-center clock: the hand turns with geyser time (one turn = 12 h)"""
    k = rec_index(T)
    if k < 0: mins = 0.0
    elif k >= N - 1: mins = ELAPSED[-1]
    else: mins = ELAPSED[k] + (T - RT[k]) / (RT[k + 1] - RT[k]) * REC[k + 1]["w"]
    cx, cy = 154, 145
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=CREAM, outline=INK)
    a = 2 * math.pi * (mins / 720.0) - math.pi / 2
    d.line([cx, cy, cx + 4 * math.cos(a), cy + 4 * math.sin(a)], fill=RED)
    a2 = 2 * math.pi * (mins / 60.0) - math.pi / 2
    d.line([cx, cy, cx + 3 * math.cos(a2), cy + 3 * math.sin(a2)], fill=INK)
    return mins

def ruler(d):
    """mesure: a scale beside the jet, graduated in eruption minutes (jet height = duration)"""
    x = VX + 26
    d.line([x, VY, x, VY - jet_h(5.5)], fill=INK2)
    for m in (2, 3, 4, 5):
        y = VY - jet_h(m); d.line([x, y, x + 4, y], fill=INK2)
        text_small(d, x + 6, y - 3, f"{m}")
    text_small(d, x - 4, VY - jet_h(5.5) - 7, "MIN")

def text_small(d, x, y, s):
    G = {"2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
         "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
         "M": ["10001", "11011", "10101", "10001", "10001"], "I": ["111", "010", "010", "010", "111"],
         "N": ["1001", "1101", "1011", "1001", "1001"]}
    for ch_ in s:
        g = G[ch_]
        for j, row in enumerate(g):
            for i, ch in enumerate(row):
                if ch == "1": d.point((x + i, y + j), fill=INK2)
        x += len(g[0]) + 1

def jet_h(dur): return 26 + 23 * (dur - 1.5)      # px: 1.6 min -> 28, 5.45 min -> 117
def draw_jet(d, T, i):
    """eruption i drawn at age a (s since its note)"""
    a = T - RT[i]; r = REC[i]
    if a < 0: return
    H = jet_h(r["d"]); live = 0.35 + 0.12 * r["d"]
    if i + 1 < N: live = min(live, RT[i + 1] - RT[i] - 0.05)
    rs = random.Random(int(T * 30) * 31 + i)
    if a < live:                                          # water column
        h = H * ease(a / 0.14) * (1 - 0.15 * max(0, (a - 0.7 * live) / (0.3 * live)))
        for y in range(int(h)):
            yy = VY - y; wdt = 1.5 + y * 0.05 + rs.uniform(0, 1.2)
            d.line([VX - wdt, yy, VX + wdt, yy], fill=STEAM if (y + int(T * 60)) % 7 else STEAM2)
        for _ in range(int(14 + H / 4)):                  # spray
            y = rs.uniform(0, h); x = VX + rs.gauss(0, 2 + y * 0.09)
            d.point((x, VY - y), fill=STEAM)
        top = VY - h
        d.ellipse([VX - 7 - h * .05, top - 6, VX + 7 + h * .05, top + 4], fill=STEAM)
        d.ellipse([VX - 9, VY - 4, VX + 9, VY + 3], fill=STEAM2)   # splash at the base
    fade = 2.2
    if a < live + fade:                                   # steam cloud drifting right, fading
        b = max(0.0, a - live * 0.6); f = 1 - b / (fade + live * 0.4)
        if f > 0:
            cy = VY - H * 0.85 - b * 10; cx = VX + b * 14
            for k in range(6):
                rr = (6 + H * 0.06) * (0.7 + 0.15 * k) * (1 + b * 0.4)
                ox = (k - 2.5) * rr * 0.55; oy = math.sin(k * 1.7) * rr * 0.3
                col = mix(STEAM, STEAM2, 1 - f)
                if rs.random() < 0.6 + 0.4 * f:
                    d.ellipse([cx + ox - rr, cy + oy - rr * .7, cx + ox + rr, cy + oy + rr * .7], fill=col)

SPOTS = []
_rp = random.Random(11)
for j in range(60):
    x = _rp.uniform(8, 172)
    if abs(x - VX) < 6: x += 12
    SPOTS.append((x, 252 + 0.0016 * (x - VX) ** 2 - 1, PEOPLE[j % len(PEOPLE)], _rp.random()))
def crowd(d, T):
    """people on the boardwalk: they arrive while the geyser makes them wait, and leave after the eruption"""
    k = rec_index(T)
    if k < 0: waited, since = 30.0, 9.0
    else:
        since = T - RT[k]
        waited = since / K                                # minutes since the last eruption
    n = int(min(60, 6 + waited * 0.55))
    if k >= 0 and since < 0.6: n = int(min(60, 6 + (REC[k]["w"]) * 0.55) * (1 - since / 0.6 * 0.8))
    cheer = k >= 0 and since < 0.5
    if DECOR == "mesure": return
    if not TOYISH:
        sil = (44, 48, 54) if DECOR == "doc" else (36, 40, 46)
        for j in range(n):
            x, _, _, ph = SPOTS[j]; y = 262
            hh = 4 + int(ph * 2)
            d.line([int(x), y - hh, int(x), y - 1], fill=sil); d.point((int(x), y - hh - 1), fill=sil)
            if ph > .5: d.point((int(x) + 1, y - hh + 1), fill=sil)
        return
    for j in range(n):
        x, y, col, ph = SPOTS[j]
        hop = 1 if (cheer and int(T * 12 + ph * 10) % 2) else 0
        y = int(y) - hop
        d.rectangle([int(x), y - 4, int(x) + 1, y - 2], fill=col)
        d.point((int(x), y - 5), fill=(236, 196, 160)); d.point((int(x) + 1, y - 5), fill=(236, 196, 160))
        d.point((int(x), y - 1), fill=INK); d.point((int(x) + 1, y - 1), fill=INK)
        if cheer and hop: d.point((int(x) + 2, y - 6), fill=(236, 196, 160))

def draw_scene(c, T):
    c.art = background(T); c.a = ImageDraw.Draw(c.art); d = c.a
    k = rec_index(T)
    wisp = random.Random(int(T * 8))
    for j in range(4):                                    # small resting steam at the vent
        y = VY - 3 - j * 4 - (T * 9 % 4); d.point((VX + wisp.randint(-2, 2), y), fill=STEAM2)
    if k >= 1: draw_jet(d, T, k - 1)
    if k >= 0: draw_jet(d, T, k)
    if TOYISH: clock_hand(d, T)
    if DECOR == "mesure": ruler(d)
    crowd(d, T)
    if k == I_MAX and T - RT[k] < 0.5:                    # #61 after 108 min: golden ring
        rr = 10 + (T - RT[k]) * 160
        d.ellipse([VX - rr, VY - rr * 0.5, VX + rr, VY + rr * 0.5], outline=GOLD)

# ================= text layer =================
def panel(W, y0, y1, top=INK):
    W.rectangle([16, y0, 344, y1], fill=CREAM); W.rectangle([16, y0, 344, y0 + 1], fill=top); W.rectangle([16, y1 - 1, 344, y1], fill=INK)

def hud(c, T):
    W = c.t; k = rec_index(T)
    if k < 0: return
    r = REC[k]; age = T - RT[k]
    panel(W, 18, 128)
    text(W, 28, 22, "OLD FAITHFUL WAITED", fill=INK2)
    text(W, 334, 22, f"ERUPTION #{r['n']}", fill=INK2, align="r")
    col = GOLD if (k in (I_MIN, I_MAX) and age < 1.2) else ACC if age < 0.2 else INK
    if k == 0:
        text(W, 28, 44, "...", size=40, fill=INK)
    else:
        text(W, 28, 44, f"{r['w']}", size=40, fill=col)
        text(W, 28 + 16 * len(str(r["w"])) + 10, 60, "MIN", fill=INK2)
    lab = ("LONG" if is_long(r) else "SHORT") + " BURST"
    text(W, 334, 44, lab, size=40 if False else 20, fill=ORNG if is_long(r) else TEAL, align="r")
    dur = f"~{r['d']:.0f} MIN (NIGHT, EST.)" if r["est"] else f"{f1(r['d'])} MIN"
    text(W, 334, 64, dur, fill=INK2, align="r")
    h = int(ELAPSED[k] // 60); m = int(ELAPSED[k] % 60)
    text(W, 28, 102, f"TIME SINCE #1: {h} H {m:02d} MIN", fill=INK2)
    text(W, 334, 102, "AUG 1985", fill=INK2, align="r")

def graph(c, T):
    """bottom: one bar per eruption = the wait before it (40-110 min); teal = after a short burst, orange = after a long one"""
    W = c.t; k = rec_index(T)
    W.rectangle([0, 560, 360, 640], fill=CREAM); W.rectangle([0, 560, 360, 561], fill=INK2)
    x0, x1, yb, yt = 44, 348, 608, 568
    def gy(w): return yb - (yb - yt) * (w - 40) / 70
    for w in (60, 90):
        for x in range(x0, x1, 4): W.point((x, int(gy(w))), fill=INK2)
        text(W, x0 - 6, int(gy(w)) - 9, str(w), fill=INK2, align="r")
    W.line([x0, yb, x1, yb], fill=INK2)
    bw = (x1 - x0) / N
    for i in range(1, k + 1):
        x = x0 + i * bw; col = ORNG if is_long(REC[i - 1]) else TEAL
        if i == k and T - RT[k] < 0.25: col = GOLD
        W.rectangle([x, gy(REC[i]["w"]), x + bw - 1, yb], fill=col)
    text(W, 180, 612, "WAIT BEFORE EACH ERUPTION (MIN)", fill=INK2, align="c")

BANNERS = {
    11: ("SHORT BURST -> SHORT WAIT", f"{f1(REC[10]['d'])} MIN OF WATER, THEN {REC[11]['w']} MIN", False),
    14: ("LONG BURST -> LONG WAIT", f"{f1(REC[13]['d'])} MIN OF WATER, THEN {REC[14]['w']} MIN", False),
    I_MIN: (f"{REC[I_MIN]['w']} MIN", "SHORTEST WAIT OF ALL 299", True),
    I_MAX: (f"{REC[I_MAX]['w']} MIN", "LONGEST WAIT OF ALL 299", True),
}
def banner_hold(k):
    if k + 1 < N: return max(1.6, RT[k + 1] - RT[k] - 0.1) if k in (I_MIN, I_MAX) else 1.8
    return HOLD
def banner(c, T):
    k = rec_index(T); W = c.t
    # also keep showing a banner from a previous eruption while it is still on hold
    for kk in sorted(BANNERS, reverse=True):
        if kk <= k and 0.06 < T - RT[kk] < (2.2 if kk in (I_MIN, I_MAX) else 1.9):
            a = T - RT[kk]; tt, sub, big = BANNERS[kk]; yb = 150
            w = max((16 if big else 8) * len(tt), 8 * len(sub)) + 30
            hgt = 62 if big else 44
            W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=CREAM)
            W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=GOLD if big else ACC)
            if big:
                text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
                if a > 0.25: text(W, 180, yb + 40, sub, fill=INK2, align="c")
            else:
                text(W, 180, yb + 4, tt, fill=INK, align="c")
                if a > 0.25: text(W, 180, yb + 22, sub, fill=INK2, align="c")
            return
    if T >= T_FINAL + 0.4:                                 # final: today
        a = T - T_FINAL; yb = 150
        W.rectangle([40, yb, 320, yb + 84], fill=CREAM); W.rectangle([40, yb, 320, yb + 2], fill=RED)
        text(W, 180, yb + 4, "TODAY: ~90 MIN", size=40, fill=RED, align="c")
        if a > 0.8: text(W, 180, yb + 42, "SLOWER, AND MORE REGULAR", fill=INK, align="c")
        if a > 1.4: text(W, 180, yb + 62, "NPS ~90 MIN · USGS 94 +/- 10 MIN", fill=INK2, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); draw_scene(c, T); graph(c, T); return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    panel(W, 18, 172)
    text(W, 28, 24, "A GEYSER", size=40, fill=INK)
    text(W, 28, 62, "THAT KEEPS", size=40, fill=INK)
    text(W, 28, 100, "TIME.", size=40, fill=ACC)
    if t > 0.5: text(W, 28, 146, "OLD FAITHFUL, YELLOWSTONE · AUG 1985", fill=INK2)
    if t > 1.0:
        W.rectangle([24, 452, 336, 552], fill=CREAM); W.rectangle([24, 452, 336, 453], fill=ACC)
        text(W, 180, 456, "EVERY NOTE = ONE ERUPTION", fill=INK, align="c")
        text(W, 180, 476, "THE GAP = THE REAL WAIT", fill=INK, align="c")
        text(W, 180, 496, "1 HOUR OF WAITING = 0.56 S OF SONG", fill=INK2, align="c")
        text(W, 180, 516, "TALLER JET = LONGER ERUPTION", fill=INK2, align="c")
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
    panel(W, 30, 330, ACC)
    text(W, 180, 40, f"{N} ERUPTIONS · {HOURS_TOTAL:.0f} HOURS · ONE SONG", fill=INK2, align="c")
    rows = [(f"{AVG_ALL:.0f}", "MIN", "AVERAGE WAIT, 1985"), (f"{REC[I_MIN]['w']}", "MIN", "SHORTEST"),
            (f"{REC[I_MAX]['w']}", "MIN", "LONGEST"), ("~90", "MIN", "TODAY")]
    for j, (v, u, s) in enumerate(rows):
        if t > 0.4 + j * 0.6:
            yy = 66 + j * 52
            text(W, 150, yy - 4, v, size=40, fill=RED if s == "TODAY" else INK, align="r")
            text(W, 158, yy + 6, u, fill=INK2); text(W, 196, yy + 6, s, fill=INK2)
    if t > 3.0: text(W, 180, 290, "COULD YOU GUESS THE NEXT ONE?", fill=ACC, align="c")
    if t > 3.6:
        W.rectangle([16, 470, 344, 540], fill=CREAM)
        text(W, 180, 474, "DATA: AZZALINI & BOWMAN 1990,", fill=INK2, align="c")
        text(W, 180, 494, "299 ERUPTIONS, 1-15 AUG 1985", fill=INK2, align="c")
        text(W, 180, 514, "TODAY: NPS, USGS", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "day1": sc_main("day1"), "day2": sc_main("day2"), "day3": sc_main("day3"),
           "day4": sc_main("day4"), "outro": sc_outro}

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
    z = 1.0 + 0.006 * kp * FXK
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    k = rec_index(T)
    if k >= 0 and 0 <= T - RT[k] < 0.08:
        fr = np.minimum(255, fr.astype(np.int16) + int(30 * FXK * (1 - (T - RT[k]) / 0.08))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio (C1a) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 1.5) * SR); L = np.zeros(n)
    def lowpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
    def bandpass(x, lo, hi):
        b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
    def put(t, sig, g=1.0):
        i = int(t * SR); j = min(n, i + len(sig))
        if 0 <= i < n: L[i:j] += g * sig[:j - i]
    def marimba(f, m, decay=9.0, bright=1.0):
        x = np.arange(m) / SR
        return (np.sin(2*np.pi*f*x) + .3*bright*np.sin(2*np.pi*f*4*x)*np.exp(-x*30)
                + .1*bright*np.sin(2*np.pi*f*9.9*x)*np.exp(-x*60)) * np.minimum(1, x/.002) * np.exp(-x*decay)
    def woodblock(m, f):
        x = np.arange(m) / SR
        return (np.sin(2*np.pi*f*x) + .4*np.sin(2*np.pi*f*2.3*x)) * np.exp(-x*90)
    def steam(length, seed, gain):
        m = int(length * SR); tt = np.arange(m) / SR
        s = bandpass(np.random.RandomState(seed).randn(m), 2000, 9000)
        return gain * s * np.minimum(1, tt / (.25 * length)) * np.clip((length - tt) / (.6 * length), 0, 1)
    def note_len(d, a, b): return a + (b - a) * (d - 1.5) / 3.8
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if k == "wood": put(t, v * woodblock(int(.06 * SR), kw["f"]))
        elif k == "kick":
            m = int(.28 * SR); x = np.arange(m) / SR
            put(t, v * np.sin(2 * np.pi * np.cumsum(120 * np.exp(-x * 22) + 50) / SR) * np.exp(-x * 9))
        elif k == "snare":
            m = int(.15 * SR); x = np.arange(m) / SR
            put(t, v * bandpass(np.random.RandomState(int(t * 100)).randn(m), 900, 6000) * np.exp(-x * 25))
        elif k == "bass": put(t, v * marimba(mtof(kw["m"]), int(.35 * SR), 7, .6))
        elif k == "erupt":
            f = mtof(kw["m"]); lg = kw["long"]; m = int((1.0 if lg else .6) * SR)
            put(t, v * marimba(f, m, 5 if lg else 9))
            if lg:
                for j, dt in enumerate(np.arange(S16, note_len(kw["d"], .2, .6), S16)):
                    put(t + dt, .07 * (1 - j * .2) * marimba(f, m, 5))
            if kw["n"]: put(t, steam(note_len(kw["d"], .25, .7), kw["n"], .06 if lg else .035))
        elif k == "relaunch":
            for mm in (45, 52, 57, 64): put(t, .12 * marimba(mtof(mm), int(1.4 * SR), 3))
            m = int(.8 * SR); x = np.arange(m) / SR
            put(t, .3 * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-x * 6) + 40) / SR) * np.exp(-x * 3))
    out = L.copy()
    for d_, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
        m = int(d_ * SR); out[m:] += g * .6 * L[:-m]
    x = .78 * L + .22 * lowpass(out, 4000)
    tt = np.arange(n) / SR
    x *= np.clip((TOTAL - tt) / 1.5, 0, 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * .89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
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
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print("min:", REC[I_MIN]["n"], REC[I_MIN]["w"], "max:", REC[I_MAX]["n"], REC[I_MAX]["w"], "avg299:", round(AVG_ALL, 2),
              "after short:", round(AVG_AFTER_SHORT, 1), "after long:", round(AVG_AFTER_LONG, 1), "hours:", round(HOURS_TOTAL, 2))
        print([(REC[i]["n"], round(t, 2)) for i, t in enumerate(RT)])
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
