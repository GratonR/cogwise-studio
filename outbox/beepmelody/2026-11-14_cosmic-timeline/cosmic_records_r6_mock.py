"""Mockups r6 (visual rework, 3D) for cosmic-timeline. Guillaume (2026-11-14 16:48): "zoom on the galaxy,
think 3D simulation like the planet in This Melody Is Us". Same data / music / timing as cosmic_records.py.
3 directions sharing one 3D point renderer (particle galaxies, perspective camera, pixel-art posterize):
  A  fly-through: the camera flies to each record, the galaxy fills the screen and spins (warp on big jumps)
  B  time tunnel: we look down a tunnel from Earth to the Big Bang; rings = billions of years; we travel down it
  C  universe globe: a 3D sphere of the observable universe turning slowly, Earth in the centre, each record lands
     at its true distance (radius = look-back time; directions are decorative)
python3 cosmic_records_r6_mock.py <out> ABC [T ...]        stills (540x960)
python3 cosmic_records_r6_mock.py <out> anim A T0 T1       animated webp (360x640, 12 fps)"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cosmic_records as M
from cosmic_records import *  # noqa
from v2 import text

WHITE = (255, 245, 225)
CY = 140
M.BY_BANNER = 416

# ---------------- particle models (object space, unit size) ----------------
def model(i):
    rng = np.random.default_rng(100 + i); t = REC[i]["type"]
    tint = np.array(zcol(REC[i]["lz"]), np.float32)
    if t == "quasar":
        n = 900
        a = rng.random(n) * 2 * np.pi; r = 0.25 + 0.35 * rng.random(n) ** 2
        disk = np.c_[r * np.cos(a), r * np.sin(a), rng.normal(0, .02, n)]
        m = 500; s = rng.random(m) * 1.6; sg = np.where(rng.random(m) < .5, 1, -1)
        jet = np.c_[rng.normal(0, .03, m) * (1 + s), rng.normal(0, .03, m) * (1 + s), sg * s]
        core = rng.normal(0, .06, (300, 3))
        P = np.r_[disk, jet, core]
        C = np.r_[np.tile([255, 170, 90], (n, 1)), np.tile([140, 200, 255], (m, 1)), np.tile(WHITE, (300, 1))].astype(np.float32)
        W = np.r_[np.full(n, .5), np.full(m, .35), np.full(300, 2.0)]
    elif t == "gamma-ray burst":
        n = 1400; v = rng.normal(0, 1, (n, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
        P = np.r_[v * (0.5 + .1 * rng.random(n))[:, None], rng.normal(0, .05, (400, 3))]
        C = np.r_[np.tile([255, 120, 220], (n, 1)), np.tile(WHITE, (400, 1))].astype(np.float32)
        W = np.r_[np.full(n, .3), np.full(400, 2.0)]
    else:
        n = 7000; arms = 2 if i % 3 else 3
        r = rng.exponential(.28, n).clip(0, 1.1); arm = rng.integers(0, arms, n)
        th = np.log(r + .05) / math.tan(math.radians(16)) + arm * 2 * np.pi / arms + rng.normal(0, .35, n)
        disk = np.c_[r * np.cos(th), r * np.sin(th), rng.normal(0, .025, n)]
        b = rng.normal(0, .08, (900, 3)); b[:, 2] *= .7
        P = np.r_[disk, b]
        knot = rng.random(n) < .06
        C = np.tile([150, 185, 255], (n, 1)).astype(np.float32)
        C[knot] = [255, 130, 190]
        C = C * .6 + tint * .4
        C = np.r_[C, np.tile([255, 220, 170], (900, 1))].astype(np.float32)
        W = np.r_[np.where(knot, 1.0, .45) * (1.2 - r), np.full(900, 1.0)]
    if "cluster" in t:                                          # a few neighbours = a cluster
        k = [P]; kc = [C]; kw = [W]
        for j in range(5):
            o = rng.normal(0, 1.3, 3); o[2] *= .4
            e = rng.normal(0, .12, (150, 3)) + o
            k.append(e); kc.append(np.tile([255, 215, 160], (150, 1)).astype(np.float32)); kw.append(np.full(150, .8))
        P, C, W = np.concatenate(k), np.concatenate(kc), np.concatenate(kw)
    # orientation: deterministic tilt
    a1, a2 = 0.9 + 0.5 * math.sin(i * 1.7), i * 0.9
    Rx = np.array([[1, 0, 0], [0, math.cos(a1), -math.sin(a1)], [0, math.sin(a1), math.cos(a1)]])
    Rz = np.array([[math.cos(a2), -math.sin(a2), 0], [math.sin(a2), math.cos(a2), 0], [0, 0, 1]])
    return P.astype(np.float32), C, W.astype(np.float32), (Rz @ Rx).astype(np.float32)
MODELS = [model(i) for i in range(N)]
_mw = np.random.default_rng(1)
def milky_way():
    P, C, W, R = model(0)
    return P, np.tile([200, 215, 255], (len(P), 1)).astype(np.float32), W, R

def spin(P, ang):
    c, s = math.cos(ang), math.sin(ang)
    return P @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], np.float32).T

# ---------------- camera + splat ----------------
class Cam:
    def __init__(self, pos, look, up=(0, 1, 0), f=150.0, cx=90, cy=CY):
        self.p = np.array(pos, np.float32); fw = np.array(look, np.float32) - self.p; fw /= np.linalg.norm(fw)
        rt = np.cross(np.array(up, np.float32), fw); rt /= np.linalg.norm(rt); u = np.cross(fw, rt)
        self.R = np.stack([rt, u, fw]); self.f, self.cx, self.cy = f, cx, cy
    def proj(self, X):
        Y = (X - self.p) @ self.R.T
        z = Y[:, 2]; ok = z > 0.05
        x = self.cx + self.f * Y[:, 0] / np.maximum(z, .05); y = self.cy - self.f * Y[:, 1] / np.maximum(z, .05)
        return x, y, z, ok

def splat(acc, cam, X, C, W, gain=1.0):
    x, y, z, ok = cam.proj(X)
    xi, yi = np.round(x).astype(int), np.round(y).astype(int)
    ok &= (xi >= 0) & (xi < AW) & (yi >= 0) & (yi < AH)
    if not ok.any(): return
    w = (W[ok] * gain)[:, None] * C[ok] / 255
    np.add.at(acc, (yi[ok], xi[ok]), w)

def tonemap(acc, base):
    v = 1 - np.exp(-acc * 1.6)
    v = np.floor(v * 8) / 8                                      # posterize = pixel-art bands
    out = np.array(base, np.float32) + v * 255
    return np.clip(out, 0, 255).astype(np.uint8)

def put_galaxy(acc, cam, i, center, size, ang, gain=1.0):
    P, C, W, R = MODELS[i]
    X = spin(P, ang) @ R.T * size + np.array(center, np.float32)
    splat(acc, cam, X, C, W, gain)

_rs = np.random.default_rng(11)
STAR3 = _rs.uniform([-60, -60, 0], [60, 60, 240], (700, 3)).astype(np.float32)
STARC = _rs.integers(0, 3, 700)

def finish(c, acc):
    img = tonemap(acc, SKY)
    c.art.paste(Image.fromarray(img)); c.a = ImageDraw.Draw(c.art)
    return c.a

def depth_gauge(c, T, k):
    """thin look-back gauge on the left: top = Big Bang, bottom = us (keeps the 'how far' readable)"""
    d = c.a; y0, y1 = 86, 240
    d.line([5, y0, 5, y1], fill=RIM); d.rectangle([3, y0 - 3, 7, y0 - 1], fill=(255, 150, 70))
    for g in (5, 10):
        yy = int(y1 - g / AGE * (y1 - y0)); d.line([4, yy, 6, yy], fill=INK2)
    if k >= 0:
        lb = REC[k]["lb"]; pl = REC[k - 1]["lb"] if k else 0
        v = lerp(pl, lb, ease((T - RT[k]) / 0.35)); yy = int(y1 - v / AGE * (y1 - y0))
        d.rectangle([3, yy - 1, 8, yy + 1], fill=GOLD)
        for i in range(k): d.point((7, int(y1 - REC[i]["lb"] / AGE * (y1 - y0))), fill=mix(GOLD, SKY, .4))

def gauge_labels(c):
    W = c.t
    text(W, 20, 2 * 86 - 12, "BIG BANG", fill=(255, 205, 160))
    text(W, 20, 2 * 240 - 8, "US", fill=INK2)

# =========== A : fly-through ===========
ZSTEP = 30.0
def zA(i): return ZSTEP * (i + 1)
def xyA(i): return 3.0 * math.sin(i * 1.3), 2.0 * math.cos(i * 0.9)
FLY = 0.32
def camA(T):
    k = rec_index(T)
    if k < 0: return 0.0, 0.0
    a = ease((T - RT[k]) / FLY); zp = zA(k - 1) if k else 0.0
    z = lerp(zp, zA(k), a) - 6.0 + 1.2 * min(1, (T - RT[k]) / 3)       # slow drift-in after arriving
    return z, a
def scene_A(c, T):
    k = rec_index(T); acc = np.zeros((AH, AW, 3), np.float32)
    if T < HOOK: k = I_MOM if T > 0.2 else -1
    if k < 0:
        finish(c, acc); return
    if T < HOOK: cz, a = zA(k) - 6.0 + 0.4 * T, 1.0
    else: cz, a = camA(T)
    tx, ty = xyA(k)
    cam = Cam((tx * a, ty * a, cz), (tx, ty, zA(k)))
    # stars (wrapped around the camera) with warp streaks on big look-back jumps
    jump = (REC[k]["lb"] - (REC[k - 1]["lb"] if k else 0)) if T >= HOOK else 0
    warp_ = (1 - a) * min(1.0, 0.25 + jump / 3.0)
    S = STAR3.copy(); S[:, 2] = (S[:, 2] - cz) % 240 + 2 + cz
    x, y, z, ok = cam.proj(S)
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    finish(c, acc)  # placeholder, redrawn below
    lines = []
    if warp_ > 0.05:
        S2 = S.copy(); S2[:, 2] -= 40 * warp_
        x2, y2, z2, ok2 = cam.proj(S2)
        lines = [(x[j], y[j], x2[j], y2[j], STARC[j]) for j in range(len(S)) if ok[j] and ok2[j]]
    # galaxies: current (big), previous (flying past), next few far ahead
    put_galaxy(acc, cam, k, (tx, ty, zA(k)), 3.6, 0.25 * T + k, 1.0)
    if k > 0 and a < 1: put_galaxy(acc, cam, k - 1, (*xyA(k - 1), zA(k - 1)), 4.6, 0.25 * T, 1 - a)
    d = finish(c, acc)
    for (x0, y0, x1, y1, s) in lines:
        d.line([x0, y0, x1, y1], fill=mix([INK2, BLUE, INK][s], SKY, .3))
    if not lines:
        for j in range(len(S)):
            if ok[j] and 0 <= x[j] < AW and 0 <= y[j] < AH:
                d.point((x[j], y[j]), fill=mix([INK2, BLUE, INK][STARC[j]], SKY, .4 + .5 * min(1, z[j] / 200)))
    # re-splat galaxy on top of stars
    acc2 = np.zeros((AH, AW, 3), np.float32)
    put_galaxy(acc2, cam, k, (tx, ty, zA(k)), 3.6, 0.25 * T + k, 1.0)
    if k > 0 and a < 1: put_galaxy(acc2, cam, k - 1, (*xyA(k - 1), zA(k - 1)), 4.6, 0.25 * T, 1 - a)
    base = np.array(c.art, np.float32)
    v = np.floor((1 - np.exp(-acc2 * 1.6)) * 8) / 8
    c.art.paste(Image.fromarray(np.clip(base + v * 255, 0, 255).astype(np.uint8))); c.a = ImageDraw.Draw(c.art)
    if T >= HOOK: depth_gauge(c, T, k)

# =========== B : deep field -> zoom on the galaxy, then the camera turns around it (like the globe) ===========
_rb = np.random.default_rng(21)
FIELD = [(_rb.uniform(-40, 40), _rb.uniform(-60, 60), _rb.uniform(90, 260), int(_rb.integers(0, N)), _rb.uniform(.6, 1.6)) for _ in range(70)]
def pB(i):
    a = i * 2.39996; r = 10 + 14 * ((i * 0.618) % 1)
    return np.array([r * math.cos(a), r * math.sin(a) * 1.3, 120.0], np.float32)
WIDE = np.array([0, 0, -30], np.float32)
def camB(T):
    k = rec_index(T)
    if T < HOOK: k, age = I_MOM, T
    elif k < 0: return Cam(WIDE, (0, 0, 120)), 0.0, -1
    else: age = T - RT[k]
    gap = (RT[k + 1] - RT[k]) if (T >= HOOK and k + 1 < N) else 9.0
    zin = min(0.5, max(0.18, gap * 0.6))
    a = ease(age / zin)
    th = 0.35 * age + k                                            # slow orbit around the galaxy (like the globe)
    near = pB(k) + np.array([7 * math.sin(th), 2.5, -7 * math.cos(th)], np.float32)
    start = WIDE if k == 0 or T < HOOK else (pB(k - 1) + np.array([0, 2.5, -7], np.float32)) * .4 + WIDE * .6
    pos = start * (1 - a) + near * a
    look = np.array([0, 0, 120], np.float32) * (1 - a) + pB(k) * a
    return Cam(pos, look, f=150 + 40 * a), a, k
def scene_B(c, T):
    cam, a, k = camB(T)
    acc = np.zeros((AH, AW, 3), np.float32)
    for (x, y, z, m, sz) in FIELD:
        put_galaxy(acc, cam, m, (x, y, z), sz, .1 * T + x, .35)
    lim = (k + 1) if T >= HOOK else 0
    for i in range(lim):
        if i != k: put_galaxy(acc, cam, i, pB(i), 1.3, .2 * T + i, .45)
    if k >= 0: put_galaxy(acc, cam, k, pB(k), 4.0, .25 * T, 1.0)
    d = finish(c, acc)
    S = STAR3 * [1.2, 1.2, 1.5]
    x, y, z, ok = cam.proj(S.astype(np.float32))
    for j in range(len(S)):
        if ok[j] and 0 <= x[j] < AW and 0 <= y[j] < AH:
            d.point((x[j], y[j]), fill=mix([INK2, BLUE, INK][STARC[j]], SKY, .55))
    if k >= 0 and a < 0.9:                                        # target reticle on the record while zooming
        x, y, _, ok = cam.proj(pB(k)[None])
        if ok[0]:
            r = int(16 * (1 - a) + 30 * a)
            for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                d.line([x[0] + sx * r, y[0] + sy * r, x[0] + sx * (r - 6), y[0] + sy * r], fill=PINK if k == I_MOM else GOLD)
                d.line([x[0] + sx * r, y[0] + sy * r, x[0] + sx * r, y[0] + sy * (r - 6)], fill=PINK if k == I_MOM else GOLD)
    if T >= HOOK: depth_gauge(c, T, k)
def labels_B(c): pass

# =========== C : universe globe ===========
RU = 3.4                                      # world units per billion years
def dirC(i):
    rng = np.random.default_rng(500 + i); v = rng.normal(0, 1, 3); return v / np.linalg.norm(v)
SHELL = np.random.default_rng(9).normal(0, 1, (2400, 3)).astype(np.float32)
SHELL /= np.linalg.norm(SHELL, axis=1)[:, None]
def scene_C(c, T):
    k = rec_index(T)
    yaw = 0.12 * T; el = 0.38
    dist = 120 - 18 * min(1, max(0, (T - 26) / 30))
    pos = (dist * math.cos(el) * math.sin(yaw), dist * math.sin(el), -dist * math.cos(el) * math.cos(yaw))
    cam = Cam(pos, (0, 0, 0), f=210)
    acc = np.zeros((AH, AW, 3), np.float32)
    # the edge: light from the Big Bang (sphere shell)
    splat(acc, cam, SHELL * RU * AGE, np.tile([255, 130, 60], (len(SHELL), 1)).astype(np.float32), np.full(len(SHELL), .28, np.float32))
    for gy in (5, 10):                                           # faint shells
        ring = np.c_[np.cos(np.linspace(0, 6.283, 160)), np.zeros(160), np.sin(np.linspace(0, 6.283, 160))] * RU * gy
        splat(acc, cam, ring.astype(np.float32), np.tile(RIM, (160, 1)).astype(np.float32), np.full(160, 1.2, np.float32))
    mwP, mwC, mwW, mwR = milky_way()
    splat(acc, cam, (spin(mwP, .4 * T) @ mwR.T) * 2.2, mwC, mwW * 1.2)
    shown = range(k + 1) if T >= HOOK else [I_MOM]
    beams = []
    for i in shown:
        p = dirC(i) * RU * REC[i]["lb"]; fresh = i == k and (T - RT[i] < 1.5 or T < HOOK)
        put_galaxy(acc, cam, i, p, 2.6 if fresh else .9, .3 * T + i, 1.4 if fresh else .45)
        if fresh: beams.append(p)
    d = finish(c, acc)
    for p in beams:
        q = min(1, (T - RT[k]) / 0.4) if T >= HOOK else 1
        X = np.array([p, p * (1 - q)], np.float32)
        x, y, _, ok = cam.proj(X)
        if ok.all(): d.line([x[0], y[0], x[1], y[1]], fill=mix(GOLD, SKY, .25))
    if T >= HOOK: depth_gauge(c, T, k)
def labels_C(c):
    text(c.t, 180, 2 * 92, "THE EDGE = LIGHT FROM THE BIG BANG", fill=(255, 205, 160), align="c")
    text(c.t, 180, 2 * CY + 12, "US", fill=INK, align="c")

# ---------------- run ----------------
def patch(v):
    orig = (M.scene, M.axis_labels)
    if v == "A": M.scene = scene_A; M.axis_labels = gauge_labels
    elif v == "B": M.scene = scene_B; M.axis_labels = lambda c: (gauge_labels(c), labels_B(c))
    elif v == "C": M.scene = scene_C; M.axis_labels = lambda c: (gauge_labels(c), labels_C(c))
    return orig
def frame(T):
    idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
    return render_frame(idx, T - START[NAMES[idx]])
def run(v, out, Ts):
    orig = patch(v); files = []
    for T in Ts:
        p = f"{out}/{v}_t{T:05.2f}.png"; Image.fromarray(frame(T)).resize((540, 960), Image.LANCZOS).save(p); files.append(p)
    M.scene, M.axis_labels = orig
    return files
def anim(v, out, t0, t1, fps=12):
    orig = patch(v); ims = []
    for j in range(int((t1 - t0) * fps)):
        ims.append(Image.fromarray(frame(t0 + j / fps)).resize((360, 640), Image.LANCZOS))
    M.scene, M.axis_labels = orig
    p = f"{out}/{v}_anim.webp"
    ims[0].save(p, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0, quality=70, method=4)
    return p

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    if sys.argv[2] == "anim":
        print(anim(sys.argv[3], out, float(sys.argv[4]), float(sys.argv[5])))
    else:
        Ts = [float(x) for x in sys.argv[3:]] or [12.6, 28.7, 57.2]
        for v in sys.argv[2]: print(run(v, out, Ts))
