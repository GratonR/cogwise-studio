"""Mockups r4 (visual rework) for cosmic-timeline: 3 visual directions, same data/music/timing.
python3 mock.py <out>"""
import sys, os, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cosmic_records as M
from cosmic_records import *  # noqa
from v2 import text

# ---------- shared: nebula backdrop ----------
def nebula(seed, cols, k=0.55):
    rng = np.random.default_rng(seed); a = np.zeros((AH, AW, 3), np.float32)
    yy, xx = np.mgrid[0:AH, 0:AW]
    base = np.zeros((AH, AW), np.float32)
    for s in (40, 20, 10):
        g = rng.random((AH // s + 2, AW // s + 2)).astype(np.float32)
        g = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((AW + 2 * s, AH + 2 * s), Image.BICUBIC))[s:s + AH, s:s + AW] / 255
        base += g * (s / 70)
    base = (base - base.min()) / (base.max() - base.min())
    hue = np.array(Image.fromarray((rng.random((5, 4)) * 255).astype(np.uint8)).resize((AW, AH), Image.BICUBIC)) / 255
    c0, c1 = np.array(cols[0], np.float32), np.array(cols[1], np.float32)
    col = c0[None, None] * (1 - hue[..., None]) + c1[None, None] * hue[..., None]
    a[:] = np.array(SKY, np.float32)
    f = np.clip((base - 0.45) * 2.2, 0, 1)[..., None] * k
    a = a * (1 - f) + col * f
    q = (np.floor(a / 6) * 6)                                       # posterize = pixel-art bands
    return q.astype(np.uint8)
NEB = {}
def bg(c, key, seed, cols, k=0.55):
    if key not in NEB: NEB[key] = nebula(seed, cols, k)
    c.art.paste(Image.fromarray(NEB[key]))
    c.a = __import__("PIL.ImageDraw", fromlist=["x"]).Draw(c.art)
    return c.a

def glow(d, x, y, r, col):
    for j in range(r, 0, -1):
        d.ellipse([x - j, y - j, x + j, y + j], outline=mix(SKY, col, 0.12 + 0.5 * (1 - j / r) ** 2))

def big_galaxy(d, x, y, r, col, ang=0.0, tilt=0.45):
    glow(d, x, y, int(r * 0.6), col)
    for j in range(int(r * 14)):
        th = j * 0.22 + ang; rr = r * j / (r * 14)
        for arm in (0, math.pi):
            px, py = x + rr * math.cos(th + arm), y + rr * tilt * math.sin(th + arm)
            d.point((int(px), int(py)), fill=mix(mix(col, (255, 255, 255), .3 * (1 - rr / r)), SKY, rr / r * .5))
    d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=(255, 245, 220))

def scope(d, yr, cx, cy, s=1):
    """the telescope of the era (pixel sprites): ground dome < 1990, Hubble 1990-2021, Webb >= 2022"""
    if yr < 1990:
        d.rectangle([cx - 12 * s, cy - 2 * s, cx + 12 * s, cy + 8 * s], fill=(70, 78, 110))
        d.pieslice([cx - 12 * s, cy - 12 * s, cx + 12 * s, cy + 8 * s], 180, 360, fill=(190, 196, 215))
        d.rectangle([cx - 2 * s, cy - 12 * s, cx + 2 * s, cy - 2 * s], fill=SKY)
        d.line([cx, cy - 4 * s, cx + 3 * s, cy - 11 * s], fill=INK, width=max(1, s))
    elif yr < 2022:
        d.rectangle([cx - 4 * s, cy - 10 * s, cx + 4 * s, cy + 6 * s], fill=(200, 205, 215))
        d.rectangle([cx - 4 * s, cy - 12 * s, cx + 4 * s, cy - 10 * s], fill=(90, 95, 110))
        d.rectangle([cx - 14 * s, cy - 4 * s, cx - 6 * s, cy + 2 * s], fill=(60, 90, 170))
        d.rectangle([cx + 6 * s, cy - 4 * s, cx + 14 * s, cy + 2 * s], fill=(60, 90, 170))
        d.line([cx - 6 * s, cy - 1 * s, cx - 4 * s, cy - 1 * s], fill=INK); d.line([cx + 4 * s, cy - 1 * s, cx + 6 * s, cy - 1 * s], fill=INK)
    else:
        d.polygon([(cx - 16 * s, cy + 6 * s), (cx + 16 * s, cy + 6 * s), (cx + 12 * s, cy + 10 * s), (cx - 12 * s, cy + 10 * s)], fill=(200, 120, 200))
        for q in range(-2, 3):
            for p in range(-1, 2):
                hx, hy = cx + q * 4 * s + (2 * s if p % 2 else 0), cy - 4 * s + p * 4 * s
                d.regular_polygon((hx, hy, 2 * s), 6, fill=(255, 196, 70), outline=(180, 130, 40))
        d.line([cx, cy - 10 * s, cx, cy - 16 * s], fill=INK2)

# =========== A : same well, filled sky (nebula, big glowing objects, era telescope) ===========
def scene_A(c, T):
    k = rec_index(T); yr = year_at(T)
    d = bg(c, "A", 5, [(90, 40, 140), (30, 90, 170)], 0.7)
    for (x, y, s) in STARS: d.point((x, y), fill=mix([INK2, BLUE, INK][s], SKY, .3))
    for x in range(0, AW, 2):
        for j in range(10):
            v = WALL[j % 8, x // 2]; f = (1 - j / 10) * (0.6 + 0.4 * v)
            d.rectangle([x, TOPY - 12 + j, x + 1, TOPY - 12 + j], fill=mix(SKY, (255, 150, 70), f * .8))
    d.line([8, TOPY, 8, EY - 6], fill=RIM)
    for g in ticks():
        yy = int(ly(g)); d.line([6, yy, 10, yy], fill=INK2)
    d.rectangle([0, EY - 4, AW, AH], fill=(10, 14, 34))
    d.ellipse([-40, EY - 6, AW + 40, EY + 60], fill=(26, 52, 104)); d.ellipse([-40, EY - 6, AW + 40, EY + 10], fill=(46, 100, 66))
    scope(d, yr, EX, EY - 10, 1)
    if k >= 0:
        prev = ly(REC[k - 1]["lb"]) if k > 0 else EY - 6
        a = ease((T - RT[k]) / 0.3); yy = int(lerp(prev, ly(REC[k]["lb"]), a))
        d.line([12, yy, AW, yy], fill=mix(SKY, GOLD, .5))
        for x in range(12, AW, 4): d.line([x, yy, x + 1, yy], fill=GOLD)
    for i in range(k + 1):
        x, y = POSX[i], int(ly(REC[i]["lb"])); col = zcol(REC[i]["lz"]); age = T - RT[i]
        fresh = i == k
        if y > EY - 12 and not fresh: continue
        y = min(y, EY - 14)
        if fresh:
            q = min(1, age / 0.25)
            for w, f in ((3, .7), (1, .1)):
                d.line([x, y, lerp(x, EX, q), lerp(y, EY - 22, q)], fill=mix(col, SKY, f), width=w)
        t_ = REC[i]["type"]
        if t_ in ("quasar", "gamma-ray burst"):
            glow(d, x, y, 9 if fresh else 4, col if t_ == "quasar" else PINK); star(d, x, y, (255, 255, 255) if fresh else col, 2 if fresh else 1)
        else:
            big_galaxy(d, x, y, 12 if fresh else 5, col if fresh else mix(col, SKY, .25), i)

# =========== B : the time fan (Earth at the centre bottom, rings = billions of years) ===========
FCX, FCY, FR = 90, 238, 140
RX = 0.6
def fr(lb):
    lm = CAM[0]; return 14 + (lb - lm) / (AGE - lm) * (FR - 14) if lb >= lm else 10
def fan_pos(i):
    ang = math.radians(200 + ((i * 0.618034) % 1) * 140)
    r = fr(REC[i]["lb"]); return int(FCX + RX * r * math.cos(ang)), int(FCY + r * math.sin(ang))
def scene_B(c, T):
    k = rec_index(T)
    d = bg(c, "B", 9, [(20, 60, 140), (120, 40, 110)], 0.5)
    # Big Bang arc
    for j in range(8):
        d.arc([FCX - RX * (FR + 8 - j), FCY - FR - 8 + j, FCX + RX * (FR + 8 - j), FCY + FR + 8 - j], 180, 360, fill=mix(SKY, (255, 150, 70), .25 + .08 * j))
    for g in ticks():
        r = fr(g); d.arc([FCX - RX * r, FCY - r, FCX + RX * r, FCY + r], 180, 360, fill=mix(SKY, RIM, .8))
    if k >= 0:
        r = fr(REC[k]["lb"]) if T - RT[k] > 0.3 else lerp(fr(REC[k - 1]["lb"]) if k else 14, fr(REC[k]["lb"]), ease((T - RT[k]) / 0.3))
        
        for a_ in range(180, 361, 3):
            x0 = FCX + RX * r * math.cos(math.radians(a_)); y0 = FCY + r * math.sin(math.radians(a_)); d.point((x0, y0), fill=GOLD)
        # explored zone tint
        for rr in range(14, int(r), 3):
            d.arc([FCX - RX * rr, FCY - rr, FCX + RX * rr, FCY + rr], 180, 360, fill=mix(SKY, CYAN, .06))
    for i in range(k + 1):
        x, y = fan_pos(i); col = zcol(REC[i]["lz"]); fresh = i == k; age = T - RT[i]
        if y > FCY - 2: continue
        if fresh:
            q = min(1, age / 0.25); d.line([x, y, lerp(x, FCX, q), lerp(y, FCY - 6, q)], fill=mix(col, SKY, .2), width=2)
            glow(d, x, y, 8, col)
        obj(d, i, x, y, col if fresh else mix(col, SKY, .35), fresh)
    d.rectangle([0, FCY, AW, AH], fill=(10, 14, 34))
    d.pieslice([FCX - 12, FCY - 12, FCX + 12, FCY + 12], 180, 360, fill=(46, 100, 66))
    d.line([0, FCY, AW, FCY], fill=RIM)

# =========== C : the record staircase (year x look-back) + eyepiece close-up ===========
GX0, GX1, GY0, GY1 = 18, 172, 96, 236
def gx(y): return GX0 + (y - Y0) / (Y1 - Y0) * (GX1 - GX0)
def gy(lb): return GY1 - lb / AGE * (GY1 - GY0)
def scene_C(c, T):
    k = rec_index(T); yr = year_at(T)
    d = bg(c, "C", 13, [(40, 30, 110), (20, 80, 120)], 0.45)
    d.rectangle([GX0, GY0 - 6, GX1, GY0 - 3], fill=mix(SKY, (255, 150, 70), .6))
    for g in (5, 10):
        yy = int(gy(g))
        for x in range(GX0, GX1, 3): d.point((x, yy), fill=RIM)
    d.line([GX0, GY0, GX0, GY1], fill=RIM); d.line([GX0, GY1, GX1, GY1], fill=RIM)
    if k >= 0:
        pts = [(GX0, GY1)]
        for i in range(k + 1):
            pts += [(gx(REC[i]["yr"]), pts[-1][1]), (gx(REC[i]["yr"]), gy(REC[i]["lb"]))]
        pts.append((gx(yr), pts[-1][1]))
        poly = pts + [(gx(yr), GY1)]
        d.polygon(poly, fill=mix(SKY, CYAN, .14))
        d.line(pts, fill=GOLD, width=1)
        for i in range(k + 1):
            col = zcol(REC[i]["lz"]); star(d, int(gx(REC[i]["yr"])), int(gy(REC[i]["lb"])), col if i == k else mix(col, SKY, .3), 1)
        # eyepiece close-up of the newest record (bottom area)
        cx, cy, R = 136, 270, 30
    else:
        cx, cy, R = 136, 270, 30
    d.rectangle([0, 246, AW, AH], fill=(8, 10, 26))
    d.ellipse([cx - R - 3, cy - R - 3, cx + R + 3, cy + R + 3], fill=(40, 46, 80))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(4, 4, 14))
    if k >= 0:
        col = zcol(REC[k]["lz"]); t_ = REC[k]["type"]
        if t_ == "galaxy" or "galaxy" in t_:
            big_galaxy(d, cx, cy, 22, col, k * 0.7, 0.55)
        else:
            glow(d, cx, cy, 16, col); star(d, cx, cy, (255, 255, 255), 2)
    d.line([cx - R, cy, cx - R + 6, cy], fill=INK2); d.line([cx + R - 6, cy, cx + R, cy], fill=INK2)
    scope(d, yr, 40, 282, 1)

def labels_C(c, T):
    W = c.t; k = rec_index(T)
    text(W, 180, 2 * GY0 - 30, "BIG BANG · 13.8 BN YEARS AGO", fill=(255, 205, 160), align="c")
    for g in (5, 10): text(W, 2 * GX0 + 4, int(gy(g)) * 2 - 18, f"{g} BN YR", fill=INK2)
    for y in (1914, 1965, 2025): text(W, int(gx(y) * 2), 2 * GY1 + 2, str(y), fill=INK2, align="c")
    text(W, 80, 2 * 246 + 8, "IN THE EYEPIECE", fill=CYAN, align="c")
    yr = year_at(T); lab = "GROUND TELESCOPE" if yr < 1990 else ("HUBBLE" if yr < 2022 else "WEBB")
    text(W, 80, 2 * 300, lab, fill=INK, align="c")

def labels_B(c):
    W = c.t; text(W, 180, 2 * (FCY - FR) - 34, "BIG BANG · 13.8 BILLION YEARS AGO", fill=(255, 205, 160), align="c")
    for g in ticks():
        r = fr(g); text(W, 2 * FCX, int(2 * (FCY - r)) + 2, f"{g:g} BN YR", fill=INK2, align="c")
    text(W, 180, 2 * FCY - 20, "US", fill=INK, align="c")

def run(variant, out, Ts):
    orig_scene, orig_axis, orig_clock = M.scene, M.axis_labels, M.clock
    if variant == "A":
        M.scene = scene_A
    elif variant == "B":
        M.scene = scene_B; M.axis_labels = lambda c: labels_B(c)
    elif variant == "C":
        M.scene = scene_C; M.axis_labels = lambda c: None; M.clock = lambda c, T: labels_C(c, T)
    files = []
    for T in Ts:
        idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
        im = Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS)
        p = f"{out}/{variant}_t{T:05.2f}.png"; im.save(p); files.append(p)
    M.scene, M.axis_labels, M.clock = orig_scene, orig_axis, orig_clock
    return files

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    Ts = [float(x) for x in sys.argv[3:]] or [14.0, 30.0, 60.0]
    for v in sys.argv[2]:
        print(run(v, out, Ts))
