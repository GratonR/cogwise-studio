"""BEEPMELODY — 3 MOONS LOCKED IN A 1:2:4 GROOVE. LISTEN.
jupiter-moons (co-pilot: step 1 = layer-by-layer build, step 2 = C "Tambours de Jupiter", step 3 = this scene).
Real positions of Io, Europa, Ganymede, Callisto from 16 Nov 2026 to 16 Mar 2027 (jupiter_moons_hits.py ->
jupiter_moons_hits.csv + _pos.npz). Clock: 1 s = 2 days. One completed lap (crossing the START LINE, fixed in space) =
one hit, placed exactly on the crossing (no grid snapping). Layers: Io alone, + Europa (day 20), + Ganymede (day 40),
+ Callisto (day 60); the camera pulls back each time a moon joins.
Scene: 3D pixel-art Jupiter system (distances to scale, sizes enlarged), groove sequencer strip at the bottom.

    python3 jupiter_moons.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
    JM_PAL=light for the light variant.
"""
import sys, os, math, random, subprocess, csv
from datetime import date, timedelta
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.8"))
PAL = os.environ.get("JM_PAL", "dark")

# ================= data =================
MOONS = ["Io", "Europa", "Ganymede", "Callisto"]
SHORT = {"Io": "IO", "Europa": "EUROPA", "Ganymede": "GANYMEDE", "Callisto": "CALLISTO"}
INFO = {r["moon"]: r for r in csv.DictReader(open(os.path.join(HERE, "jupiter_moons_draft.csv")))}
PER = {m: float(INFO[m]["sidereal_period_d"]) for m in MOONS}
AKM = {m: int(INFO[m]["semimajor_axis_km"]) for m in MOONS}
HITS_ALL = [(float(r["day"]), r["moon"], int(r["lap"])) for r in csv.DictReader(open(os.path.join(HERE, "jupiter_moons_hits.csv")))]
POS = np.load(os.path.join(HERE, "jupiter_moons_hits_pos.npz"))
D0 = date(2026, 11, 16)
DPS = 2.0                                       # days per second
T0 = 0.5                                        # the clock starts (day 0)
DAYS = 120.0                                    # 16 Nov 2026 -> 16 Mar 2027
ENTRY = {"Io": 0.0, "Europa": 20.0, "Ganymede": 40.0, "Callisto": 60.0}
def T_of(day): return T0 + day / DPS
def day_at(T): return max(0.0, min(DAYS, (T - T0) * DPS))
T_END = T_of(DAYS)
HITS = [(T_of(d), m, n) for d, m, n in HITS_ALL if ENTRY[m] <= d <= DAYS]     # audible hits
HT = {m: [t for t, mm, _ in HITS if mm == m] for m in MOONS}
OUTRO = 6.5
TOTAL = T_END + OUTRO
SC = [("hook", 4.0), ("a", 20.0), ("b", 20.0), ("c", T_END - 44.0), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]
RATIO = {m: PER[m] / PER["Io"] for m in MOONS}

def moon_xyz(m, day):
    k = MOONS.index(m); t = POS["t"]
    a = np.interp(day, t, POS["ang"][:, k]); r = np.interp(day, t, POS["r"][:, k]); h = np.interp(day, t, POS["h"][:, k])
    return np.array([r * math.cos(a), h, r * math.sin(a)], np.float32), a
def laps_done(m, day): return sum(1 for d, mm, _ in HITS_ALL if mm == m and ENTRY[m] <= d <= day)
def last_hit(m, T):
    v = [t for t in HT[m] if t <= T]; return v[-1] if v else None
def date_str(day): return (D0 + timedelta(days=int(day))).strftime("%b %d %Y").upper()

# ================= palette =================
if PAL == "light":
    SKY = (236, 232, 222); SKY2 = (214, 222, 236); INK = (34, 38, 60); INK2 = (110, 116, 140); PANEL = (250, 247, 240); RIM = (180, 170, 150)
    STARCOL = (196, 200, 214)
else:
    SKY = (5, 6, 18); SKY2 = (14, 10, 34); INK = (236, 236, 250); INK2 = (140, 140, 178); PANEL = (12, 12, 32); RIM = (64, 58, 110)
    STARCOL = (170, 176, 220)
GOLD = (255, 196, 70); LINEC = (255, 120, 90)
MCOL = {"Io": (255, 204, 70), "Europa": (120, 220, 255), "Ganymede": (190, 140, 255), "Callisto": (255, 110, 150)}
SURF = {"Io": (236, 200, 96), "Europa": (226, 214, 190), "Ganymede": (168, 150, 128), "Callisto": (118, 104, 96)}
MPX = {"Io": 2.6, "Europa": 2.4, "Ganymede": 3.4, "Callisto": 3.2}            # drawn radius (px) at reference depth
def mix(a, b, f): f = max(0.0, min(1.0, f)); return tuple(int(a[j] + (b[j] - a[j]) * f) for j in range(3))

# ================= camera =================
RJV = 2.0                                        # Jupiter drawn at 2x its radius (sizes not to scale)
CY = 132
DIST = [(0.0, 18.0), (ENTRY["Europa"], 28.0), (ENTRY["Ganymede"], 44.0), (ENTRY["Callisto"], 66.0)]
class Cam:
    def __init__(self, pos, f=170.0, cx=90, cy=CY):
        self.p = np.array(pos, np.float32); fw = -self.p / np.linalg.norm(self.p)
        rt = np.cross(np.array((0, 1, 0), np.float32), fw); rt /= np.linalg.norm(rt); u = np.cross(fw, rt)
        self.R = np.stack([rt, u, fw]); self.f, self.cx, self.cy = f, cx, cy
    def proj(self, X):
        Y = (np.atleast_2d(X) - self.p) @ self.R.T
        z = Y[:, 2]
        return self.cx + self.f * Y[:, 0] / np.maximum(z, .05), self.cy - self.f * Y[:, 1] / np.maximum(z, .05), z
def cam_at(T):
    day = day_at(T); D = DIST[0][1]
    for d0, dd in DIST[1:]:
        D = lerp(D, dd, ease((day - d0) / 3.0))
    if T > T_END: D = lerp(D, 74.0, ease((T - T_END) / 3.0))
    el = math.radians(lerp(16.0, 36.0, min(1.0, T / T_END)))
    az = math.radians(-58.0 + 3.2 * T)
    cy = lerp(CY, 196, ease((T - T_END) / 1.2))
    return Cam((D * math.cos(el) * math.cos(az), D * math.sin(el), D * math.cos(el) * math.sin(az)), cy=cy), D

# ================= sprites =================
_rng = np.random.default_rng(4)
STARS = _rng.normal(0, 1, (420, 3)).astype(np.float32); STARS /= np.linalg.norm(STARS, axis=1)[:, None]; STARS *= 900
STARB = _rng.random(420)
def sphere(acc_img, cx, cy, rad, base, cam, bands=False, light=(-0.55, 0.45, -0.7)):
    rr = int(math.ceil(rad)) + 1
    ys, xs = np.mgrid[-rr:rr + 1, -rr:rr + 1].astype(np.float32)
    nx, ny = xs / max(rad, .5), -ys / max(rad, .5); q = 1 - nx * nx - ny * ny; m = q > 0
    nz = -np.sqrt(np.clip(q, 0, 1))
    Lw = np.array(light, np.float32); Lw /= np.linalg.norm(Lw)
    Lc = cam.R @ Lw
    sh = np.clip(nx * Lc[0] + ny * Lc[1] + nz * Lc[2], 0, 1)
    amb = 0.45 if PAL == "light" else 0.18
    sh = np.floor((amb + (1 - amb) * sh) * 6) / 6
    col = np.ones(xs.shape + (3,), np.float32) * np.array(base, np.float32)
    if bands:                                    # latitude bands: world-up component of the normal
        nw = np.stack([nx, ny, nz], -1) @ cam.R
        lat = nw[..., 1]
        b = (np.sin(lat * 15.0) > 0.25)
        col = np.where(b[..., None], col * np.array([0.78, 0.62, 0.5], np.float32), col)
        eq = np.abs(lat) < 0.12; col = np.where(eq[..., None], col * 1.05, col)
    out = col * sh[..., None]
    H, W = acc_img.shape[:2]
    x0, y0 = int(round(cx)) - rr, int(round(cy)) - rr
    for j in range(2 * rr + 1):
        yy = y0 + j
        if not (0 <= yy < H): continue
        for i in np.nonzero(m[j])[0]:
            xx = x0 + i
            if 0 <= xx < W: acc_img[yy, xx] = out[j, i]

def glow(acc, x, y, col, r, g):
    x0, x1 = int(max(0, x - r)), int(min(AW, x + r + 1)); y0, y1 = int(max(0, y - r)), int(min(AH, y + r + 1))
    if x0 >= x1 or y0 >= y1: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    w = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * (r / 2.2) ** 2)) * g
    acc[y0:y1, x0:x1] += w[..., None] * (np.array(col, np.float32) / 255)

def vis(m, T):
    if m == "Io": return 1.0                      # Io is on screen from the first frame
    return ease((day_at(T) - ENTRY[m]) / 1.2) if T >= T0 else (1.0 if m == "Io" else 0.0)

# ================= scene =================
def scene(c, T):
    cam, D = cam_at(T); day = day_at(T)
    img = np.zeros((AH, AW, 3), np.float32)
    g = np.linspace(0, 1, AH)[:, None, None]
    img[:] = np.array(SKY, np.float32) * (1 - g * .5) + np.array(SKY2, np.float32) * (g * .5)
    acc = np.zeros((AH, AW, 3), np.float32)
    # stars (direction only)
    Y = STARS @ cam.R.T
    ok = Y[:, 2] > 0
    sx = cam.cx + cam.f * Y[:, 0] / np.maximum(Y[:, 2], 1); sy = cam.cy - cam.f * Y[:, 1] / np.maximum(Y[:, 2], 1)
    for j in np.nonzero(ok)[0]:
        if 0 <= sx[j] < AW and 0 <= sy[j] < AH:
            img[int(sy[j]), int(sx[j])] = mix(SKY, STARCOL, .25 + .6 * STARB[j])
    # orbits (dotted), back half first; the START LINE (fixed direction, +X)
    items = []
    for m in MOONS:
        v = vis(m, T)
        if v <= 0: continue
        r = float(np.interp(day, POS["t"], POS["r"][:, MOONS.index(m)]))
        th = np.linspace(0, 2 * np.pi, 160, endpoint=False)
        P = np.stack([r * np.cos(th), np.zeros_like(th), r * np.sin(th)], 1).astype(np.float32)
        x, y, z = cam.proj(P)
        for j in range(0, len(th), 2):
            if 0 <= x[j] < AW and 0 <= y[j] < AH:
                f = .30 * v if z[j] > D else .55 * v
                img[int(y[j]), int(x[j])] = mix(img[int(y[j]), int(x[j])], MCOL[m], f)
        # trail: the last 35 % of the lap, glowing
        _, a_now = moon_xyz(m, day)
        for s in np.linspace(0, 0.35, 28):
            a = a_now - s * 2 * np.pi
            x1, y1, _ = cam.proj(np.array([r * math.cos(a), 0, r * math.sin(a)], np.float32))
            glow(acc, x1[0], y1[0], MCOL[m], 1.6, .55 * v * (1 - s / 0.35) ** 1.5)
    rmax = max(float(np.interp(day, POS["t"], POS["r"][:, MOONS.index(m)])) for m in MOONS if vis(m, T) > 0) + 3
    x, y, z = cam.proj(np.array([[RJV + .5, 0, 0], [rmax, 0, 0]], np.float32))
    pulse = 0.0
    for m in MOONS:
        lh = last_hit(m, T)
        if lh is not None and T - lh < .35: pulse = max(pulse, 1 - (T - lh) / .35)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    n = 40
    for j in range(n):
        px, py = lerp(x[0], x[1], j / n), lerp(y[0], y[1], j / n)
        if 0 <= px < AW and 0 <= py < AH:
            img[int(py), int(px)] = mix(img[int(py), int(px)], LINEC, .55 + .45 * pulse)
        if pulse > 0: glow(acc, px, py, LINEC, 2.2, .25 * pulse)
    # bodies, depth-sorted
    jx, jy, jz = cam.proj(np.zeros((1, 3), np.float32))
    items.append((jz[0], "J", jx[0], jy[0], cam.f * RJV / jz[0]))
    for m in MOONS:
        v = vis(m, T)
        if v <= 0: continue
        Pm, _ = moon_xyz(m, day)
        mx_, my_, mz_ = cam.proj(Pm)
        items.append((mz_[0], m, mx_[0], my_[0], MPX[m] * (40.0 / mz_[0]) ** 0.25 * (0.4 + 0.6 * v)))
    items.sort(key=lambda it: -it[0])
    for z_, m, px, py, rad in items:
        if m == "J":
            glow(acc, px, py, (255, 190, 120) if PAL == "dark" else (240, 170, 90), rad * 1.8, .16)
            sphere(img, px, py, rad, (236, 196, 150), cam, bands=True)
        else:
            sphere(img, px, py, max(1.2, rad), SURF[m], cam)
            glow(acc, px, py, MCOL[m], rad * 2.6, .35)
            lh = last_hit(m, T)
            if lh is not None and T - lh < .45:               # lap: flash ring
                a = (T - lh) / .45; rr = rad + 2 + 12 * ease(a)
                th = np.linspace(0, 2 * np.pi, 48)
                for tt in th:
                    qx, qy = px + rr * math.cos(tt), py + rr * math.sin(tt) * .6
                    if 0 <= qx < AW and 0 <= qy < AH: img[int(qy), int(qx)] = mix(img[int(qy), int(qx)], MCOL[m], 1 - a)
                glow(acc, px, py, MCOL[m], rad * 4 + 4, 1.2 * (1 - a))
    v = 1 - np.exp(-acc * 1.5); v = np.floor(v * 7) / 7
    if PAL == "light":
        w = v.max(-1, keepdims=True); colr = acc / (acc.max(-1, keepdims=True) + 1e-6)
        out = img * (1 - .7 * w) + .7 * w * colr * 235
    else: out = img + v * 255
    c.art.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))); c.a = ImageDraw.Draw(c.art)

# ================= groove strip (bottom): the polyrhythm as a sequencer =================
GY0, LANEH = 474, 22
WIN = 6.0                                        # seconds shown
def groove(c, T):
    W = c.t
    W.rectangle([10, GY0 - 22, 350, GY0 + 4 * LANEH + 4], fill=PANEL); W.rectangle([10, GY0 - 22, 350, GY0 - 21], fill=RIM)
    text(W, 18, GY0 - 20, "THE GROOVE", fill=INK2)
    text(W, 342, GY0 - 20, "1 SECOND = 2 DAYS", fill=INK2, align="r")
    x0, x1 = 96, 340
    for k, m in enumerate(MOONS):
        y = GY0 + k * LANEH; on = vis(m, T) > 0.5
        text(W, 18, y + 1, SHORT[m], fill=MCOL[m] if on else mix(INK2, PANEL, .5))
        W.rectangle([x0, y + 10, x1, y + 10], fill=mix(RIM, PANEL, .3))
        for t in HT[m]:
            if T - WIN <= t <= T:
                xx = x1 - (T - t) / WIN * (x1 - x0); fresh = T - t < .2
                W.rectangle([xx - (4 if fresh else 2), y + 3, xx + (4 if fresh else 2), y + 17], fill=(255, 255, 255) if fresh else MCOL[m])
        n = laps_done(m, day_at(T))
        if on: text(W, 352, y + 1, "", fill=INK2, align="r")
    W.rectangle([x1, GY0 - 2, x1 + 1, GY0 + 4 * LANEH], fill=INK)

# ================= HUD, banners, footer =================
def fmt_mi(km): return f"{round(km * 0.621371, -2):,.0f}"
def current(T):
    day = day_at(T); cur = "Io"
    for m in MOONS:
        if day >= ENTRY[m]: cur = m
    return cur
def hud(c, T):
    W = c.t; day = day_at(T); m = current(T)
    W.rectangle([10, 14, 350, 136], fill=PANEL); W.rectangle([10, 14, 350, 15], fill=RIM); W.rectangle([10, 135, 350, 136], fill=RIM)
    text(W, 20, 18, f"DAY {int(day):3d} · {date_str(day)}", fill=INK2)
    tot = sum(laps_done(mm, day) for mm in MOONS)
    text(W, 340, 18, f"{tot} BEEPS", fill=GOLD, align="r")
    text(W, 20, 36, SHORT[m], size=40, fill=MCOL[m])
    text(W, 340, 40, "1 LAP =", fill=INK2, align="r")
    text(W, 340, 58, f"{PER[m]:.2f} DAYS", fill=INK, align="r")
    text(W, 340, 76, f"{PER[m] * 24:.1f} H", fill=INK2, align="r")
    text(W, 20, 84, f"{AKM[m]:,} KM · {fmt_mi(AKM[m])} MI OUT", fill=INK2)
    text(W, 20, 108, "LAPS  " + "  ".join(f"{SHORT[mm][:2]} {laps_done(mm, day)}" for mm in MOONS if day >= ENTRY[mm]), fill=INK)

def box(W, xc, yb, tt, sub, accent, a=1.0):
    w = max(16 * len(tt) + 30, 8 * len(sub) + 30); hgt = 62
    x0, x1 = xc - w / 2, xc + w / 2
    W.rectangle([x0, yb, x1, yb + hgt], fill=PANEL)
    W.rectangle([x0, yb, x1, yb + 2], fill=accent); W.rectangle([x0, yb + hgt - 1, x1, yb + hgt], fill=RIM)
    text(W, xc, yb + 4, tt, size=40, fill=INK, align="c")
    if a > 0.15 and sub: text(W, xc, yb + 40, sub, fill=accent, align="c")
BY_BANNER = 382
BANNERS = [(ENTRY["Europa"], 3.2, "+ EUROPA", f"1 LAP = {RATIO['Europa']:.3f} IO LAPS", "Europa"),
           (ENTRY["Ganymede"], 3.2, "+ GANYMEDE", f"1 LAP = {RATIO['Ganymede']:.3f} IO LAPS", "Ganymede"),
           (ENTRY["Callisto"], 3.2, "+ CALLISTO", "NOT IN THE LOCK · PLAYS FREE", "Callisto"),
           (84.0, 3.4, "THE LOCK", "IO, EUROPA, GANYMEDE NEVER ALL LINE UP", None),
           (104.0, 3.0, "THE SLIP", "2.007 AND 4.044, NOT 2 AND 4", None)]
def banner(c, T):
    W = c.t; day = day_at(T)
    for d0, dur, tt, sub, m in BANNERS:
        a = (day - d0) / DPS
        if 0.05 < a < dur:
            box(W, 180, BY_BANNER, tt, sub, MCOL[m] if m else GOLD, a); return

def footer(c, T):
    W = c.t
    W.rectangle([0, 600, 360, 640], fill=PANEL); W.rectangle([0, 600, 360, 601], fill=RIM)
    text(W, 10, 604, "EVERY BEEP = ONE MOON", fill=INK2); text(W, 10, 620, "FINISHES A LAP", fill=GOLD)
    text(W, 350, 604, "DISTANCES TO SCALE", fill=INK2, align="r"); text(W, 350, 620, "SIZES ENLARGED", fill=INK2, align="r")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8)); scene(c, T)
    return c

def sc_hook(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([10, 14, 350, 160], fill=PANEL); W.rectangle([10, 14, 350, 15], fill=RIM); W.rectangle([10, 159, 350, 160], fill=RIM)
    text(W, 22, 20, "3 MOONS LOCKED", size=40, fill=INK)
    if t > 0.3: text(W, 22, 58, "IN A 1:2:4 GROOVE.", size=40, fill=GOLD)
    if t > 0.8: text(W, 22, 98, "LISTEN.", size=40, fill=MCOL["Io"])
    if t > 2.0: box(W, 180, BY_BANNER, "IO GOES FIRST", f"1 LAP = {PER['Io']:.2f} DAYS = 1 BEEP", MCOL["Io"], t - 2.0)
    groove(c, T); footer(c, T)
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T); groove(c, T); footer(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T); W = c.t
    W.rectangle([10, 14, 350, 300], fill=PANEL); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 18, f"120 DAYS · {len(HITS)} BEEPS", fill=INK2, align="c")
    rows = [("Io", f"{PER['Io']:.2f} DAYS", "THE BEAT"), ("Europa", f"{PER['Europa']:.2f} DAYS", f"{RATIO['Europa']:.3f} X IO"),
            ("Ganymede", f"{PER['Ganymede']:.2f} DAYS", f"{RATIO['Ganymede']:.3f} X IO"), ("Callisto", f"{PER['Callisto']:.2f} DAYS", "FREE")]
    for j, (m, a, b) in enumerate(rows):
        if t > 0.3 + j * 0.4:
            text(W, 24, 50 + j * 62, SHORT[m], fill=MCOL[m]); text(W, 24, 66 + j * 62, a, size=40, fill=INK)
            text(W, 336, 78 + j * 62, b, fill=INK2, align="r")
    if t > 2.2:
        W.rectangle([10, 520, 350, 596], fill=PANEL)
        text(W, 180, 526, "PERIODS: IMCCE · NASA NSSDC · JPL", fill=INK2, align="c")
        text(W, 180, 544, "POSITIONS: LIESKE THEORY (MEEUS)", fill=INK2, align="c")
        text(W, 180, 562, "NOV 16 2026 - MAR 16 2027", fill=INK2, align="c")
    footer(c, T)
    return c

SCENEFN = {"hook": sc_hook, "a": sc_main("a"), "b": sc_main("b"), "c": sc_main("c"), "outro": sc_outro}

def compose(c):
    art = np.array(c.art); big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt); tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

BIG = sorted(t for t, m, _ in HITS if m in ("Ganymede", "Callisto"))
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose(SCENEFN[name](t))
    ki = np.searchsorted(BIG, T, side="right") - 1
    kp = math.exp(-(T - BIG[ki]) / 0.09) if ki >= 0 else 0.0
    z = 1.0 + 0.012 * kp * FXK
    if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(SKY) * f).astype(np.uint8)
    return fr

# ================= audio: C · Tambours de Jupiter (step 2), full length =================
SR = 44100
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def env(n, a, d):
        t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    def lowpass(x, fc): b, a = butter(2, fc / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc): b, a = butter(2, fc / (SR / 2), "high"); return lfilter(b, a, x)
    n = int((TOTAL + 1.0) * SR); L = np.zeros(n); t = np.arange(n) / SR
    def put(tm, sig, g=1.0):
        i = int(tm * SR); j = min(n, i + len(sig))
        if 0 <= i < n: L[i:j] += g * sig[:j - i]
    def noise(dur, fc, dec, seed, hp=None):
        m_ = int(dur * SR); s = lowpass(np.random.RandomState(seed % 100000).randn(m_), fc)
        if hp: s = highpass(s, hp)
        return s * np.exp(-np.arange(m_) / SR * dec)
    def tom(f0, g, d=.45):
        m_ = int(.9 * SR); tt = np.arange(m_) / SR
        return g * np.sin(2*np.pi*np.cumsum(f0*(1+.6*np.exp(-tt*20)))/SR) * np.exp(-tt / d)
    def gong(f, d=2.5):
        m_ = int(4.5 * SR); tt = np.arange(m_) / SR
        s = sum(a * np.sin(2*np.pi*f*r*tt) * np.exp(-tt * k) for a, r, k in [(1, 1, .5), (.6, 1.48, .9), (.45, 2.13, 1.3), (.3, 2.71, 1.8), (.2, 3.9, 2.6)])
        return s * env(m_, .01, d)
    def wood(f):
        m_ = int(.25 * SR); tt = np.arange(m_) / SR; return np.sin(2*np.pi*f*tt) * np.exp(-tt * 40)
    # drone builds with the layers
    layer = np.clip((t - T0) * DPS / 60.0, 0, 1)
    dr = (np.sin(2*np.pi*mtof(26)*t) + .5*np.sin(2*np.pi*mtof(33)*t) + .25*layer*np.sin(2*np.pi*mtof(38)*t)) * (.7 + .3*np.sin(2*np.pi*t/4))
    fade_in = np.clip(t / 1.0, 0, 1); end = np.clip((TOTAL - t) / 2.0, 0, 1)
    L += .05 * dr * fade_in * end
    L += lowpass(np.random.RandomState(5).randn(n), 300) * .02 * end
    # shaker pulse: 3 per Io lap, locked to Io's first audible hit (mean period on screen)
    beat = PER["Io"] / DPS / 3; tb = HT["Io"][0] - 3 * beat; k = 0
    while tb < T_END + 2 * beat:
        if tb >= 0: put(tb, noise(.07, 8000, 60, 300 + k, 3000), .035 if k % 3 == 0 else .02)
        tb += beat; k += 1
    for tm in HT["Io"]: put(tm, .20 * wood(mtof(81)))
    for tm in HT["Europa"]: put(tm, tom(mtof(57), .26, .18))
    for tm in HT["Ganymede"]: put(tm, tom(mtof(38), .40, .5)); put(tm, noise(.3, 900, 9, 77), .08)
    for tm in HT["Callisto"]: put(tm, .24 * gong(mtof(38), 3.0))
    put(T_END, .30 * gong(mtof(26), 4.0)); put(T_END, tom(mtof(31), .5, .8))
    out = L.copy()
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07), (1.1, .05)]:
        m_ = int(d * 1.2 * SR); out[m_:] += g * .6 * L[:-m_]
    x = .7 * L + .3 * lowpass(out, 4000)
    x = x / (np.max(np.abs(x)) + 1e-9) * .89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
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
        print("total %.2f s" % TOTAL, {n: round(d, 2) for n, d in SC}, "hits", len(HITS), {m: len(HT[m]) for m in MOONS})
        print("first hit %.2f s" % HITS[0][0], "ratios", {m: round(RATIO[m], 4) for m in MOONS})
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
