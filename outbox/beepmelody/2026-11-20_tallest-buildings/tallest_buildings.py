"""BEEPMELODY — every world's tallest building, 1890 -> 2026 (14 records, CTBUH height to architectural top).
Scene: a pixel skyline seen from the side. Each new record is built FLOOR BY FLOOR from the ground and takes the gold
crown from the last one; the camera zooms out to keep the tallest thing in frame, so the old towers shrink.
RETRAVAIL r1 (Guillaume 2026-11-20, « Rythme trop lent ») -> B « every floor = a tick »: 1 floor = 1 thirty-second note
at 150 BPM (0.05 s), 1,037 floors (CTBUH floors above ground, 2 sources each), every record = a BOOM held 2 beats,
empty years are skipped (">> +17 YRS" in the HUD).
Mood (co-pilot step 2, kept in r2): A · "Chantier", 150 BPM: floor = rivet hit, brighter as it climbs.
Data: tallest_buildings.csv (2 sources per row).

    python3 tallest_buildings.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
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
VARIANT = os.environ.get("TB_VARIANT", "day")          # day | dusk (palette variant for the step-3 card)

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "tallest_buildings.csv"))))
for r in REC:
    r["h"] = float(r["height_m"]); r["ft"] = int(r["height_ft"]); r["y"] = int(r["year"]); r["mo"] = int(r["month"])
N = len(REC)

# ================= clock (1 floor = 1/32 note) =================
BPM = 150.0
BEAT = 60.0 / BPM                       # 0.4 s
FLOOR = BEAT / 8                        # 0.05 s per floor
HOLD = BEAT * 2                         # each record's boom rings 2 beats before the next build starts
for r in REC: r["fl"] = int(r["floors"])
T_START = 3.2                            # first record (Dec 1890) lands here (its floors start under the title)
S0 = T_START - REC[0]["fl"] * FLOOR      # 2.2 s
BS, RT = [], []                          # build start / boom time of each record
t_ = S0
for r in REC:
    BS.append(round(t_, 4)); t_ += r["fl"] * FLOOR; RT.append(round(t_, 4)); t_ += HOLD
T_FINAL = RT[-1]
TAIL = 2.8                               # after Burj Khalifa: "+320 M" then the clock runs to 2026, "STILL #1"
T_NOW = T_FINAL + TAIL
OUTRO = 4.6
TOTAL = T_NOW + OUTRO
GRID0 = T_START % BEAT
YF = [r["y"] + (r["mo"] - 0.5) / 12 for r in REC]
Y_NOW = 2026 + 10.6 / 12                 # the clock stops on 20 Nov 2026
def year_f(T):
    """the year shown: fixed during a build (the record's completion), rolls fast during the hold that follows"""
    if T < RT[0]: return YF[0]
    for i in range(N):
        nxt = YF[i + 1] if i + 1 < N else Y_NOW
        if i + 1 < N and T < BS[i + 1]:
            return lerp(YF[i], nxt, ease(min(1, max(0, (T - RT[i] - 0.25) / (HOLD - 0.3)))))
        if i == N - 1:
            return lerp(YF[i], nxt, ease(min(1, max(0, (T - RT[i] - 1.6) / 0.9))))
    return YF[-1]
def y_of_t(T): return year_f(T)
def skip_label(T):
    """>> +N YRS while the clock rolls over the empty years"""
    for i in range(N):
        a = T - RT[i]
        if i + 1 < N and 0.2 <= a < HOLD + 0.6:
            dy = REC[i + 1]["y"] - REC[i]["y"]
            if dy >= 2: return f">> +{dy} YRS"
            if dy == 1: return ">> +1 YR"
            return ">> +1 MONTH"
        if i == N - 1 and 1.6 <= a < TAIL: return f">> +{2026 - REC[i]['y']} YRS"
    return ""
SPLIT = [RT[0], RT[5] + HOLD, RT[9] + HOLD, RT[12] + HOLD, T_NOW, TOTAL]
SC = [("intro", SPLIT[0])] + [(n, SPLIT[j + 1] - SPLIT[j]) for j, n in enumerate(["early", "burst", "modern", "burj", "outro"])]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t - 1e-6: k = i
    return k
def building(T):
    """(record index, floors done) of the tower under construction, or (None, 0)"""
    for i in range(N):
        if BS[i] - 1e-6 <= T < RT[i] - 1e-6:
            return i, min(REC[i]["fl"], int((T - BS[i]) / FLOOR + 1e-6) + 1)
    return None, 0

# ================= palette =================
if VARIANT == "dusk":
    SKY_TOP, SKY_BOT = (62, 52, 96), (236, 142, 92)
    CITY = (98, 78, 104); GROUND = (58, 46, 62); GROUND2 = (44, 36, 50)
    OLD = (132, 116, 138); OLD2 = (106, 92, 116); WIN = (250, 214, 130)
else:
    SKY_TOP, SKY_BOT = (246, 214, 158), (255, 246, 226)
    CITY = (232, 212, 178); GROUND = (176, 150, 116); GROUND2 = (150, 126, 98)
    OLD = (150, 140, 132); OLD2 = (124, 114, 108); WIN = (255, 236, 190)
INK = (52, 40, 30)
INK2 = (122, 100, 80)
GOLD = (232, 150, 30)
GOLD2 = (186, 108, 20)
CORAL = (222, 84, 58)
CREAM = (255, 249, 236)
WHITE = (255, 255, 255)

# ================= camera =================
Y_GROUND = 288.0
TOP_Y = 124.0                            # champion's top sits here (below the banner zone)
def view_h(T):
    """metres that fit between the ground and TOP_Y: the champion, or the rising tower once it passes it"""
    k = rec_index(T)
    h = REC[k]["h"] if k >= 0 else REC[0]["h"]
    j, f = building(T)
    if j is not None: h = max(h, REC[j]["h"] * f / REC[j]["fl"])
    return h * 1.08
def ppm(T): return (Y_GROUND - TOP_Y) / view_h(T)

# ================= music plan (shared by picture + audio) =================
HMIN, HMAX = 94.0, 828.0
PENT = [0, 2, 4, 7, 9]
def height_note(h, base=60):
    x = (math.log(h) - math.log(HMIN)) / (math.log(HMAX) - math.log(HMIN))
    d = int(round(x * 12)); return base + 12 * (d // 5) + PENT[d % 5]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
ROOTS = [36, 36, 41, 43]
def build():
    ev(0.10, "stab", m=height_note(REC[0]["h"]) + 12, v=0.35)           # first sound before 0.2 s
    ev(0.10, "rivet", f=1, v=0.10)
    nb = int(TOTAL / BEAT) + 1
    for k in range(nb):
        b = GRID0 + k * BEAT
        if b > TOTAL: break
        bar = k // 4
        if b < S0 - 0.01:                                               # intro, before the first floor: sparse rivets
            if k % 2 == 0 or b > S0 - 0.9: ev(b, "rivet", f=1, v=0.06 + 0.04 * b / S0)
            continue
        if b <= T_FINAL + 0.01:
            ev(b, "kick", v=0.20)
            ev(b + BEAT / 2, "bass", m=ROOTS[bar % 4], d=BEAT * 0.45, v=0.11)
        elif b < TOTAL - 2.0:
            if k % 4 == 0: ev(b, "pad", m=ROOTS[bar % 4] + 24, d=BEAT * 4, v=0.10)
            if k % 2 == 0: ev(b, "rivet", f=40, v=0.05)
    for i, r in enumerate(REC):                                         # one rivet per floor, brighter as it climbs
        for fl in range(1, r["fl"] + 1):
            ev(BS[i] + (fl - 1) * FLOOR, "rivet", f=fl, v=0.05 + 0.05 * fl / 163)
    for i, t in enumerate(RT):
        m = height_note(REC[i]["h"])
        ev(t, "stab", m=m, v=0.62 + 0.25 * i / (N - 1))
        ev(t, "crash", v=0.22 if i < N - 1 else 0.34)
        ev(t, "boom", v=0.55 + 0.2 * REC[i]["h"] / HMAX)
    for k, d in enumerate([0, 7, 12, 16, 19, 24]):                     # rising arpeggio on Burj Khalifa
        ev(T_FINAL + (k + 1) * BEAT / 4, "stab", m=height_note(828) - 12 + d, v=0.32)
    ev(T_FINAL - BEAT * 3, "riser", d=BEAT * 3, v=0.14)
    ev(T_NOW, "stab", m=height_note(828), v=0.45); ev(T_NOW, "crash", v=0.25)
    EV.sort(key=lambda e: e[0])
build()
BOOMS = sorted(t for t, k, _ in EV if k == "boom")

# ================= drawing =================
_CITY = []
_rr = random.Random(7)
x = -4
while x < AW + 4:
    w = _rr.randint(5, 11); _CITY.append((x, w, _rr.uniform(18, 70), _rr.random())); x += w + _rr.randint(0, 2)

def background(T):
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        f = y / Y_GROUND
        a[y, :] = [SKY_TOP[j] + (SKY_BOT[j] - SKY_TOP[j]) * min(1, f) for j in range(3)]
    img = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(img)
    P = ppm(T)
    for x0, w, h, r in _CITY:                                            # generic low city behind (scaled too)
        hp = max(1, int(h * P))
        d.rectangle([x0, Y_GROUND - hp, x0 + w, Y_GROUND], fill=CITY)
    d.rectangle([0, Y_GROUND, AW, AH], fill=GROUND)
    d.rectangle([0, Y_GROUND + 3, AW, AH], fill=GROUND2)
    return img

def banner_on(T): return any(t0 <= T < t1 for t0, t1, *_ in BANNERS)
def gridlines(c, T):
    d = c.a; W = c.t; P = ppm(T); bon = banner_on(T) or 1.9 < T < T_START
    vh = (Y_GROUND - 92) / P
    step = next(s for s in (25, 50, 100, 200, 250, 500) if vh / s <= 6)
    m = step
    while m < vh:
        y = Y_GROUND - m * P
        if 92 < y < Y_GROUND - 4:
            for xx in range(0, AW, 4): d.point((xx, int(y)), fill=INK2 if VARIANT == "day" else (180, 150, 160))
            lab = f"{m} M · {round(m * 3.28084):,} FT"
            if not (bon and 170 < y * 2 < 270):
                W.rectangle([2, int(y * 2) - 20, 8 * len(lab) + 8, int(y * 2) - 2], fill=CREAM)
                text(W, 5, int(y * 2) - 20, lab, fill=INK2)
        m += step

def windows(d, x0, x1, y0, y1, col):
    if y1 - y0 < 6 or x1 - x0 < 3: return
    for yy in range(int(y0) + 2, int(y1) - 1, 3):
        for xx in range(int(x0) + 1, int(x1), 2): d.point((xx, yy), fill=col)

def tower(d, cx, h, shape, body, shade, win):
    """cx = centre x, h = height in px (to architectural top). Silhouettes are stylised, heights are to scale."""
    g = Y_GROUND
    def blk(w, f0, f1):
        x0, x1 = cx - w / 2, cx + w / 2; y0, y1 = g - h * f1, g - h * f0
        d.rectangle([x0, y0, x1, y1], fill=body); d.rectangle([x1 - max(1, w * 0.25), y0, x1, y1], fill=shade)
        windows(d, x0, x1 - max(1, w * 0.25), y0, y1, win)
    def pyr(w, f0, f1):
        d.polygon([(cx - w / 2, g - h * f0), (cx + w / 2, g - h * f0), (cx, g - h * f1)], fill=body)
    def needle(f0, f1):
        d.line([cx, g - h * f0, cx, g - h * f1], fill=shade)
    if shape == "dome":
        blk(9, 0, .86); d.ellipse([cx - 3, g - h - 1, cx + 3, g - h * .86 + 3], fill=shade); needle(.98, 1)
    elif shape == "twin":
        blk(10, 0, .88)
        for s in (-3, 3): d.ellipse([cx + s - 2, g - h, cx + s + 2, g - h * .88 + 2], fill=shade)
    elif shape == "cupola":
        blk(10, 0, .35); blk(6, .35, .86); pyr(6, .86, 1.0)
    elif shape == "gothic":
        blk(11, 0, .42); blk(7, .42, .80); blk(5, .80, .90); pyr(5, .90, 1.0)
    elif shape == "spire":
        blk(10, 0, .55); blk(7, .55, .80); pyr(7, .80, .92); needle(.92, 1.0)
    elif shape == "deco":
        blk(9, 0, .66)
        for k, f in enumerate((.66, .71, .76, .81)):
            w = 7 - k * 1.5; d.rectangle([cx - w / 2, g - h * (f + .05), cx + w / 2, g - h * f], fill=WHITE if k % 2 else body)
        pyr(2, .86, .90); needle(.90, 1.0)
    elif shape == "mast":
        blk(11, 0, .18); blk(8, .18, .80); blk(5, .80, .86); blk(2, .86, .93); needle(.93, 1.0)
    elif shape == "box":
        blk(8, 0, 1.0)
    elif shape == "stepped":
        blk(10, 0, .5); blk(8, .5, .67); blk(6, .67, .89); blk(4, .89, 1.0)
    elif shape == "petronas":
        for s in (-3, 3):
            x0 = cx + s
            d.rectangle([x0 - 2, g - h * .82, x0 + 2, g], fill=body); windows(d, x0 - 2, x0 + 1, g - h * .82, g, win)
            d.polygon([(x0 - 2, g - h * .82), (x0 + 2, g - h * .82), (x0, g - h * .90)], fill=body)
            d.line([x0, g - h * .90, x0, g - h], fill=shade)
        d.line([cx - 1, g - h * .38, cx + 1, g - h * .38], fill=shade)
    elif shape == "taipei":
        blk(8, 0, .30)
        for k in range(8):
            f0 = .30 + k * .075; d.polygon([(cx - 3, g - h * f0), (cx + 3, g - h * f0), (cx + 4, g - h * (f0 + .075)), (cx - 4, g - h * (f0 + .075))], fill=body if k % 2 else shade)
        blk(3, .90, .93); needle(.93, 1.0)
    elif shape == "burj":
        for k, (w, f0, f1) in enumerate([(12, 0, .14), (10, .14, .28), (8, .28, .42), (6, .42, .56), (4, .56, .70), (3, .70, .79)]):
            blk(w, f0, f1)
        blk(1.5, .79, .88); needle(.88, 1.0)

def slot_x(i, n):
    """built towers spread across the width, centred; i = record index, n = how many are on screen"""
    sp = min(14.0, 168.0 / max(n, 1))
    return AW / 2 - (n - 1) * sp / 2 + i * sp

def draw_scene(c, T):
    c.art = background(T); c.a = ImageDraw.Draw(c.art); d = c.a
    gridlines(c, T)
    P = ppm(T); k = rec_index(T)
    j, fdone = building(T)
    nvis = k + 1 + (1 if j is not None else 0)
    nlay = float(nvis)
    if j is not None and nvis >= 2:                         # slide the row as a new slot opens
        nlay = (nvis - 1) + ease(min(1, (T - BS[j]) / 0.4))
    for i in range(max(0, k + 1)):
        r = REC[i]; cx = slot_x(i, nlay)
        if i == k: tower(d, cx, r["h"] * P, r["shape"], GOLD, GOLD2, WIN)
        else: tower(d, cx, r["h"] * P, r["shape"], OLD, OLD2, (178, 170, 162) if VARIANT == "day" else (150, 136, 150))
    if j is not None:                                       # the tower under construction, floor by floor
        r = REC[j]; cx = slot_x(j, nlay); hp = r["h"] * P
        layer = Image.new("RGBA", (AW, AH), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        tower(ld, cx, hp, r["shape"], CORAL, (170, 56, 40), (255, 190, 170))
        cut = int(round(Y_GROUND - hp * fdone / r["fl"]))
        if cut > 0: layer.paste((0, 0, 0, 0), (0, 0, AW, cut))
        c.art.paste(layer, (0, 0), layer); d = c.a = ImageDraw.Draw(c.art)
        ty = cut                                            # crane on the top floor + rivet sparks
        d.line([cx + 2, ty - 1, cx + 2, ty - 9], fill=INK); d.line([cx - 5, ty - 9, cx + 9, ty - 9], fill=INK)
        d.line([cx + 7, ty - 9, cx + 7, ty - 5], fill=INK2); d.rectangle([cx + 6, ty - 5, cx + 8, ty - 4], fill=GOLD2)
        for _ in range(3): d.point((cx + random.randint(-4, 4), ty - random.randint(0, 3)), fill=WHITE)
    if k >= 0:
        r = REC[k]; cx = slot_x(k, nlay); top = Y_GROUND - r["h"] * P
        a = T - RT[k]
        if a < 0.5:                                         # impact: shock ring + dust at the base
            rr = 4 + a * 60
            d.ellipse([cx - rr, top - rr, cx + rr, top + rr], outline=WHITE if a < 0.15 else GOLD)
            for s_ in range(-14, 15, 3):
                dy = int(a * 10 * (1 + abs(s_) % 3))
                d.point((cx + s_ + int(a * 20 * (1 if s_ > 0 else -1)), int(Y_GROUND) - 1 - dy % 4), fill=CREAM)
        cy = top - 7                                        # crown over the champion
        d.polygon([(cx - 4, cy + 4), (cx - 4, cy), (cx - 2, cy + 2), (cx, cy - 1), (cx + 2, cy + 2), (cx + 4, cy), (cx + 4, cy + 4)], fill=GOLD)
        d.rectangle([cx - 4, cy + 4, cx + 4, cy + 5], fill=GOLD2)
        if k >= 1 and a < 0.8:                              # the old champion's crown falls off
            p = REC[k - 1]; px = slot_x(k - 1, nlay); ptop = Y_GROUND - p["h"] * P - 7 + a * a * 120
            if ptop < Y_GROUND - 4:
                d.rectangle([px - 3 + int(a * 10), int(ptop), px + 3 + int(a * 10), int(ptop) + 3], fill=GOLD2)

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 121, 344, 122], fill=INK)
    yr = min(int(year_f(T)), 2026)
    sk = skip_label(T)
    text(W, 334, 44, str(yr), size=40, fill=GOLD2 if sk else GOLD, align="r")
    if sk: text(W, 334, 22, sk, fill=CORAL, align="r")
    j, fdone = building(T)
    W.rectangle([16, 128, 344, 172], fill=(255, 253, 248)); W.rectangle([16, 128, 19, 172], fill=CORAL if j is not None else GOLD)
    if j is not None:                                       # second box = the tower going up
        r = REC[j]
        text(W, 28, 131, "RISING: " + r["short"], fill=INK)
        text(W, 28, 151, f"FLOOR {fdone} / {r['fl']}", fill=CORAL)
        text(W, 334, 151, r["city"].upper(), fill=INK2, align="r")
    if k < 0:
        text(W, 28, 22, "WORLD'S TALLEST BUILDING", fill=INK2)
        text(W, 28, 44, "...", size=40, fill=INK2); return
    r = REC[k]; age = T - RT[k]
    text(W, 28, 22, "WORLD'S TALLEST" if sk else "WORLD'S TALLEST BUILDING", fill=CORAL if age < 0.3 else INK2)
    text(W, 28, 44, f"{int(r['h'])} M", size=40, fill=CORAL if age < 0.22 else INK)
    text(W, 28, 92, f"{r['ft']:,} FT", fill=INK2)
    text(W, 334, 92, f"#{k + 1} / {N}", fill=INK2, align="r")
    if j is None:                                           # second box = the champion
        n = int(min(40, age * 70))
        text(W, 28, 131, r["short"][:max(0, n)], fill=INK)
        held = max(0, int(year_f(T) - (r["y"] + (r["mo"] - 1) / 12)))
        if age > 0.12:
            text(W, 28, 151, f"{r['city'].upper()} · {r['fl']} FLOORS", fill=INK2)
            lab = "NEW #1!" if held == 0 else f"#1 FOR {held} YR" + ("S" if held != 1 else "")
            text(W, 334, 151, lab, fill=CORAL if held == 0 else GOLD2 if held >= 10 else INK2, align="r")

def legend(c, T):
    """small timeline strip on the ground: 1890 -> 2026, one tick per record, cursor = the clock"""
    W = c.t; k = rec_index(T)
    x0, x1, y = 36, 324, 612
    W.rectangle([x0, y, x1, y + 1], fill=CREAM)
    def xx(yf): return x0 + (yf - 1890) / (2027 - 1890) * (x1 - x0)
    for i, r in enumerate(REC):
        X = xx(r["y"] + (r["mo"] - 0.5) / 12)
        W.rectangle([X - 1, y - 6, X, y - 1], fill=GOLD if i <= k else (200, 180, 150))
    cur = xx(min(year_f(T), Y_NOW)); W.rectangle([cur - 1, y + 3, cur + 1, y + 8], fill=WHITE)
    text(W, x0, y + 10, "1890", fill=CREAM)
    text(W, x1, y + 10, "2026", fill=CREAM, align="r")

def banner_box(W, yb, tt, sub, big, a, col=CORAL):
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    hgt = (62 if big else 42) if sub else (44 if big else 24)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=CREAM)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 40, sub, fill=col, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 21, sub, fill=col, align="c")

def by(i): return RT[i]
I = {r["short"]: i for i, r in enumerate(REC)}
BANNERS = [   # (t0, t1, title, sub, big)
    (by(I["WOOLWORTH BUILDING"]) + 0.5, RT[I["40 WALL STREET"]] - 0.3, "17 YEARS, NO NEW RECORD", "THEN NEW YORK GOES WILD", False),
    (by(I["EMPIRE STATE"]) + 0.1, by(I["EMPIRE STATE"]) + 2.4, "3 RECORDS", "IN 13 MONTHS (1930-31)", True),
    (by(I["EMPIRE STATE"]) + 2.6, RT[I["WORLD TRADE CENTER"]] - 0.2, "EMPIRE STATE: #1", "FOR 40 YEARS", False),
    (by(I["SEARS TOWER"]) + 0.1, by(I["SEARS TOWER"]) + 2.0, "FIRST RECORD OUTSIDE", "NEW YORK", False),
    (by(I["PETRONAS TOWERS"]) + 0.1, by(I["PETRONAS TOWERS"]) + 2.0, "THE TITLE LEAVES", "THE USA", False),
    (BS[N - 1] + 103 * FLOOR, BS[N - 1] + 125 * FLOOR, "MORE FLOORS THAN", "THE EMPIRE STATE (102)", False),
    (by(N - 1) + 0.1, by(N - 1) + 1.7, "+320 M IN ONE JUMP", "+1,050 FT", True),
    (by(N - 1) + 1.8, T_NOW + 0.01, "STILL #1", "", True),
]
def banner(c, T):
    for t0, t1, tt, sub, big in BANNERS:
        if t0 <= T < t1: banner_box(c.t, 184, tt, sub, big, T - t0)

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_scene(c, T); legend(c, T)
    return c

def sc_intro(t):
    c = frame_ctx(t); W = c.t
    W.rectangle([16, 18, 344, 172], fill=CREAM); W.rectangle([16, 18, 344, 19], fill=INK); W.rectangle([16, 171, 344, 172], fill=INK)
    text(W, 28, 26, "EVERY TALLEST", size=40, fill=INK)
    if t > 0.35: text(W, 28, 64, "BUILDING", size=40, fill=GOLD)
    if t > 0.8: text(W, 28, 112, "EVERY TICK = ONE FLOOR", fill=INK2)
    if t > 1.3: text(W, 28, 140, "EVERY BOOM = A NEW WORLD RECORD", fill=CORAL)
    if t > 1.9: banner_box(W, 184, f"{N} RECORDS", "1890 TO 2026", False, 1.0, GOLD)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(min(T, T_NOW)); W = c.t
    W.rectangle([16, 40, 344, 300], fill=CREAM); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 50, "THE CHAMPION SINCE 2010", fill=INK2, align="c")
    if t > 0.2:
        text(W, 180, 74, "BURJ KHALIFA", size=40, fill=GOLD, align="c")
        text(W, 180, 114, "828 M · 2,717 FT · 163 FLOORS", fill=INK, align="c")
    if t > 0.8:
        text(W, 180, 150, "10 OF 14 RECORDS:", fill=INK2, align="c")
        text(W, 180, 170, "NEW YORK", size=40, fill=INK, align="c")
    if t > 1.4:
        text(W, 180, 222, f"{sum(r['fl'] for r in REC):,} FLOORS, ONE TICK EACH", fill=INK2, align="c")
    if t > 2.0: text(W, 180, 260, "WHO BREAKS 1 KM FIRST?", fill=CORAL, align="c")
    if t > 2.4:
        W.rectangle([16, 500, 344, 572], fill=CREAM)
        text(W, 180, 506, "DATA: CTBUH SKYSCRAPER CENTER,", fill=INK2, align="c")
        text(W, 180, 526, "THE SKYSCRAPER MUSEUM (NYC).", fill=INK2, align="c")
        text(W, 180, 546, "HEIGHT TO ARCHITECTURAL TOP.", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "burst": sc_main("burst"), "modern": sc_main("modern"),
           "burj": sc_main("burj"), "outro": sc_outro}

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
    bi = np.searchsorted(BOOMS, T, side="right") - 1
    if bi >= 0 and T - BOOMS[bi] < 0.25:                     # the boom shakes the frame
        a = T - BOOMS[bi]; s = int(round(10 * FXK * math.exp(-a / 0.06) * math.sin(a * 90)))
        fr = np.roll(fr, s, axis=0)
        if a < 0.08: fr = np.minimum(255, fr.astype(np.int16) + int(50 * FXK * (1 - a / 0.08))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.25)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio (mood A · Chantier) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def env(n, a, d):
        t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    def saw(f, dur):
        n = int(dur * SR); tt = np.arange(n) / SR
        return sum(2 * ((f * dd * tt) % 1) - 1 for dd in (.995, 1.0, 1.005)) / 3
    rng = np.random.RandomState(5)
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(t, x, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(x))
        L[i:j] += x[:j - i] * (1 - pan) ** .5 * .9; R[i:j] += x[:j - i] * (1 + pan) ** .5 * .9
    for t, k, kw in EV:
        v = kw.get("v", .3)
        if k == "rivet":
            fl = kw.get("f", 1); m_ = int(.025 * SR)
            x = highpass(lowpass(rng.randn(m_), 4000 + 60 * fl), 1800 + 15 * fl) * np.exp(-np.arange(m_) / SR * 180)
            put(t, x * v, .2)
        elif k == "hat":
            m_ = int(.04 * SR); x = highpass(rng.randn(m_), 5000) * np.exp(-np.arange(m_) / SR * 120)
            put(t, x * v * .7, -.3)
        elif k in ("kick", "boom"):
            m_ = int(.45 * SR); tt = np.arange(m_) / SR
            f0, f1, dec = (90, 50, 12) if k == "kick" else (70, 32, 7)
            put(t, v * np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 16) + f1) / SR) * np.exp(-tt * dec))
        elif k == "bass":
            d = kw["d"]; m_ = int(d * SR); tt = np.arange(m_) / SR
            put(t, v * lowpass(saw(mtof(kw["m"]), d), 600) * np.exp(-tt * 9))
        elif k == "stab":
            m_ = int(.6 * SR); tt = np.arange(m_) / SR
            for j, iv in enumerate((0, 4, 7)):
                x = lowpass(saw(mtof(kw["m"] + iv), .6), 3200) * np.minimum(1, tt / .02) * np.exp(-tt * 3)
                put(t + j * .004, x * v * .16, -.3 + .3 * j)
        elif k == "crash":
            m_ = int(1.4 * SR); x = highpass(lowpass(rng.randn(m_), 8000), 3000) * np.exp(-np.arange(m_) / SR * 3)
            put(t, x * v * .35, .1)
        elif k == "pad":
            d = kw["d"]; m_ = int((d + .6) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .5) * np.clip((d + .5 - tt) / .5, 0, 1)
            x = sum(np.sin(2 * np.pi * mtof(kw["m"] + iv) * tt) for iv in (0, 7, 12, 16)) * e
            put(t, x * v * .25)
        elif k == "riser":
            m_ = int(kw["d"] * SR); tt = np.arange(m_) / SR
            put(t, highpass(rng.randn(m_), 2500) * (tt / kw["d"]) ** 2 * v)
    def reverb(x, mix=.18):
        out = x.copy()
        for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
            k_ = int(dl * SR); out[k_:] += g * .6 * x[:-k_]
        return (1 - mix) * x + mix * lowpass(out, 4000)
    L = reverb(L); R = reverb(np.roll(R, int(.011 * SR)))
    tt = np.arange(n) / SR; fade = np.clip((TOTAL - tt) / 2.0, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.stack([L, R], 1) / mx * .89
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
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV), "floors", sum(r["fl"] for r in REC))
        print([(REC[i]["y"], REC[i]["short"], round(t, 2), height_note(REC[i]["h"])) for i, t in enumerate(RT)])
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
