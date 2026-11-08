"""BEEPMELODY — ONE ATOM SPLITS. A single uranium-235 fission, then an idealized chain reaction
(each split triggers 2 more) until the splits add up to 1 joule. Every beep = one atom splitting.
Data: fission.csv (World Nuclear Association, nuclear-power.com, Euronuclear, Wikipedia/U-235)."""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, CREAM, YEL, RED, DIM, text, panel, ease, eout, lerp)
from pi import Ctx, warp, glitch_frame

FXK = float(os.environ.get("PI_FX", "0.8"))
FINAL = "climax"
DUCK = REVERB = RICH = True
RISE = True                                   # bip pitch follows log10(splits so far)
SCALE = [57, 60, 62, 64, 67, 69, 72, 74]      # A minor pentatonic
OUTRO_DIGITS = [0, 2, 4, 7]

# ================= data (fission.csv) =================
DATA = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "fission.csv")))}
E_SPLIT_J = float(DATA["energy_per_fission_J"]["value"])           # 3.2e-11 J  (~200 MeV)
SPLITS_PER_J = 1.0 / E_SPLIT_J                                      # 3.125e10
TARGET = SPLITS_PER_J

# ================= palette (neon / tech) =================
BGC = (4, 6, 16)
LAT_C = (22, 30, 62)
PROT = (240, 70, 130)
NEUT = (110, 190, 230)
CYAN = (80, 230, 255)
MAG = (255, 80, 220)
WHITE = (255, 255, 255)

# ================= timeline =================
NGEN = 34
GD = [2.1 * 0.958 ** (g - 1) for g in range(1, NGEN + 1)]   # duration of generation g (1..34): events squeeze
INTRO, NUC, OUTRO, HOLD = 4.5, 9.0, 10.0, 3.2
SPLIT0 = 4.2                                               # the first split, in the nucleus scene
G_CHAIN, G_SWARM = 7, 20                                   # last generation of each scene
# record: cumulative splits reach 1 J during generation 34
F_REC = (TARGET - (2 ** NGEN - 1)) / 2 ** NGEN
SC = [("intro", INTRO), ("nucleus", NUC),
      ("chain", sum(GD[:G_CHAIN])), ("swarm", sum(GD[G_CHAIN:G_SWARM])),
      ("climax", sum(GD[G_SWARM:NGEN - 1]) + GD[NGEN - 1] * F_REC + HOLD), ("outro", OUTRO)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
TOTAL = acc_
DUR = dict(SC); NAMES = [n for n, _ in SC]
G0 = {}                                                    # start time of generation g
t_ = START["chain"]
for g in range(1, NGEN + 1): G0[g] = t_; t_ += GD[g - 1]
T_SPLIT0 = START["nucleus"] + SPLIT0
T_REC = G0[NGEN] + GD[NGEN - 1] * F_REC
RISER_T = T_REC - 1.6
TITLES = {"intro": "", "nucleus": "ONE NUCLEUS", "chain": "CHAIN REACTION", "swarm": "THE SWARM", "climax": "ROAD TO 1 JOULE", "outro": ""}

def scene_at(T):
    for n, d in SC:
        if START[n] <= T < START[n] + d: return n
    return NAMES[-1]
def gen_at(T):
    """(generation, fraction elapsed) ; generation 0 before the chain starts"""
    if T < START["chain"]: return 0, 1.0 if T >= T_SPLIT0 else 0.0
    for g in range(NGEN, 0, -1):
        if T >= G0[g]: return g, min(1.0, (T - G0[g]) / GD[g - 1])
    return 0, 1.0
def splits(T):
    """cumulative splits at time T (idealized doubling: generation g has 2^g splits)"""
    if T >= T_REC: return TARGET
    g, f = gen_at(T)
    if g == 0: return 1.0 if f >= 1 else 0.0
    return (2 ** g - 1) + 2 ** g * f

# ================= tempo =================
def bpm(T):
    pts = [(0, 96), (START["nucleus"], 100), (START["chain"], 112), (START["swarm"], 120), (START["climax"], 126),
           (T_REC, 140), (T_REC + 0.01, 90), (TOTAL, 84)]
    return float(np.interp(T, [a for a, _ in pts], [b for _, b in pts]))
def beat_times(T):
    out, t = [], 0.0
    while t < T: out.append(t); t += 60 / bpm(t)
    return out

EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
SPL = []          # visible + audible splits: (T, x, y, g)
NODES = {}        # tree layout for early generations: (g, i) -> (x, y, T)
BANNERS = []      # (T, title, sub, big)
MILES = []        # (T, label)
KICKS, SNARES, GL = [], [], []
CX, CY, RMAX = 90.0, 170.0, 58.0

def pl_of(n):     # log10(splits) 0..10.5 -> 5..10 for pi_audio RISE pitch
    return 5.0 + 5.0 * math.log10(max(1.0, n)) / math.log10(TARGET)

def build():
    rng = np.random.default_rng(23)
    # --- generation 0: the first split
    NODES[(0, 0)] = (CX, CY, T_SPLIT0, -math.pi / 2)
    SPL.append((T_SPLIT0, CX, CY, 0))
    ev(T_SPLIT0, "bip", r=0, rate=1, lon=0.0, pl=pl_of(1)); ev(T_SPLIT0, "kickhit"); ev(T_SPLIT0, "chime", lvl=3)
    # --- generations 1..34
    for g in range(1, NGEN + 1):
        n = 2 ** g; d = GD[g - 1]
        cap = int(d * 40)
        m = min(n, cap)
        for k in range(m):
            fr = (k + 0.5 + rng.uniform(-0.35, 0.35)) / m
            T = G0[g] + d * fr
            if T >= T_REC: break
            if g <= 6:
                a = -math.pi / 2 + 2 * math.pi * (k + 0.5) / n          # radial tree: each node sits mid-way in its subtree's angle
                r_ = 9.0 * g
                x, y = CX + r_ * math.cos(a), CY + r_ * math.sin(a)
                NODES[(g, k)] = (x, y, T, a)
            else:
                R = min(RMAX, 30 + 3.2 * (g - 6))
                while True:
                    x, y = rng.normal(0, R * 0.55, 2)
                    if x * x + y * y < R * R: break
                x, y = CX + x, CY + y
            SPL.append((T, x, y, g))
            ev(T, "bip", r=int(rng.integers(0, 8)), rate=m / d, lon=float((x - CX) / RMAX * 90), pl=pl_of(splits(T)))
    SPL.sort()
    # --- banners (title, sub) and milestones
    N0 = START["nucleus"]
    BANNERS.extend([(N0 + 0.2, "URANIUM-235", "92 PROTONS + 143 NEUTRONS", False),
                    (N0 + 2.0, "A NEUTRON HITS", "U-235 BECOMES U-236", False),
                    (T_SPLIT0, "SPLIT!", "BA-144 + KR-90 + 2 NEUTRONS", False),
                    (N0 + 6.4, "~200 MEV RELEASED", "= 0.000 000 000 032 J", False),
                    (G0[1] + 0.1, "IDEALIZED CHAIN", "EACH SPLIT TRIGGERS 2 MORE", False),
                    (G0[4] + 0.1, "2 OR 3 NEUTRONS", "ARE FREED BY EACH SPLIT", False)])
    for lab, v, sub in (("1,000 SPLITS", 1e3, "STILL ONLY 0.000 000 032 J"), ("1 MILLION SPLITS", 1e6, "STILL ONLY 0.000 032 J"),
                        ("1 BILLION SPLITS", 1e9, "0.032 J ... KEEP GOING")):
        g = int(math.ceil(math.log2(v + 1))) - 1
        f = (v - (2 ** g - 1)) / 2 ** g
        T = G0[g] + GD[g - 1] * f
        MILES.append((T, lab)); BANNERS.append((T, lab, sub, True)); ev(T, "chime", lvl=4); ev(T, "kickhit")
    BANNERS.append((T_REC, "1 JOULE!", "~31 BILLION SPLITS", True))
    BANNERS.sort()
    MILES.append((T_REC, "1 JOULE"))
    ev(T_REC, "kickhit"); ev(T_REC, "chime", lvl=5)
    for k, dg in enumerate([0, 2, 4, 7, 7, 4, 2, 0][:4] + [0, 2, 4, 7]):          # rising arpeggio on the record
        ev(T_REC + 0.06 + k * 0.085, "digit", d=dg, ok=True)
    for k in range(10): ev(START["intro"] + 0.4 + k * 0.37 + 0.1 * math.sin(k * 7), "geiger")     # counter ticks under the title
    for k in range(6): ev(N0 + 0.3 + k * 0.28, "geiger")
    ev(0.15, "bip", r=0, rate=1, lon=0.0, pl=5.0)            # first note before 0.5 s
    ev(N0 + 2.0, "thud", v=0.25)
    for T, *_ in BANNERS:
        if not any(abs(T - m[0]) < 0.01 for m in MILES): ev(T, "chime", lvl=2)
    drums()

CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
def drums():
    for bi, bt in enumerate(beat_times(START["outro"])):
        sc = scene_at(bt); bl = 60 / bpm(bt); pos = bi % 4
        ch = CHORDS[(bi // 4) % 4]; root = ch[0] - 12
        hold = bt >= T_REC
        if pos == 0: ev(bt, "pad", ch=ch, d=bl * 4)
        if hold: continue
        if sc == "intro":
            if pos == 0: ev(bt, "kick", v=0.28)
        elif sc == "nucleus":
            if pos % 2 == 0: ev(bt, "kick", v=0.34)
            ev(bt + bl / 2, "hat", v=0.03, open=False)
        else:
            ev(bt, "kick", v=0.45)
            if pos in (1, 3): ev(bt, "snare", v=0.19)
            sub = 2 if sc == "chain" else 4
            for h in range(sub): ev(bt + h * bl / sub, "hat", v=0.035 if h % 2 else 0.045, open=(h == sub // 2))
            if sc == "climax" and bt > T_REC - 2.2:
                for h in range(4): ev(bt + h * bl / 4, "snare", v=0.06 + 0.12 * h / 3)
        if sc != "intro":
            for h in range(2):
                ev(bt + h * bl / 2, "bass", m=root + (12 if (pos * 2 + h) % 4 == 3 else 0), d=bl / 2 * 0.9, v=0.16)
    for t, k, kw in EV:
        if k in ("kick", "kickhit") and (k == "kickhit" or kw["v"] >= 0.36): KICKS.append(t)
        if k == "snare" and kw["v"] > 0.15: SNARES.append(t)
    KICKS.sort(); SNARES.sort()
    GL.append((T_REC - 0.22, 0.2, "stutter", 60 / bpm(T_REC) / 8))
    GL.append((MILES[2][0] - 0.15, 0.15, "stutter", 60 / bpm(MILES[2][0]) / 4))
    GL.append((START["outro"] - 0.45, 0.45, "tapestop", 0))
    GL.sort()

build()
EV.sort(key=lambda e: e[0])
SPLT = np.array([s[0] for s in SPL])

# ================= formatting =================
def fmt_count(n):
    n = int(n)
    if n < 1e6: return f"{n:,}"
    if n < 1e9: return f"{n / 1e6:.1f} MILLION"
    if n < 1e10: return f"{n / 1e9:.1f} BILLION"
    return f"{n / 1e9:.0f} BILLION"
def fmt_J(J):
    if J <= 0: return "0 J"
    if J >= 0.995: return "1 J"
    e = math.floor(math.log10(J)); dec = -e + 1
    s = f"{J:.{dec}f}"; a, b = s.split(".")
    return a + "." + " ".join(b[i:i + 3] for i in range(0, len(b), 3)) + " J"

# ================= drawing =================
_BGA = None
def base_bg():
    global _BGA
    if _BGA is None:
        a = np.zeros((AH, AW, 3), np.uint8); a[:] = BGC
        yy, xx = np.mgrid[0:AH, 0:AW]
        a[(xx % 12 == 0) & (yy % 2 == 0)] = (10, 14, 30); a[(yy % 12 == 0) & (xx % 2 == 0)] = (10, 14, 30)
        _BGA = a
    return _BGA

def lattice(c, T):
    """field of uranium nuclei; spacing shrinks generation after generation = we zoom out"""
    g, f = gen_at(T); gg = g + f
    s = max(2.2, 15 * 0.9 ** gg)
    ox, oy = CX % s, CY % s
    fade = min(1.0, (T - START["chain"]) / 0.6 + 0.0) if T >= START["chain"] else 0.0
    col = tuple(int(v * fade) for v in LAT_C)
    y = oy
    while y < 262:
        x = ox
        while x < AW:
            if (x - CX) ** 2 + (y - CY) ** 2 < (RMAX + 16) ** 2: c.a.point((int(x), int(y)), fill=col)
            x += s
        y += s

def nucleus_blob(d, cx, cy, R, seed, sx=1.0, alpha=1.0):
    rng = random.Random(seed)
    pts = []
    for _ in range(int(R * R * 0.55)):
        while True:
            u, v = rng.uniform(-1, 1), rng.uniform(-1, 1)
            if u * u + v * v < 1: break
        z = math.sqrt(max(0, 1 - u * u - v * v))
        pts.append((z, u, v, rng.random() < 92 / 235))
    pts.sort()
    for z, u, v, p in pts:
        x, y = cx + u * R * sx, cy + v * R / max(0.8, sx ** 0.5)
        base = PROT if p else NEUT; k = (0.45 + 0.55 * z) * alpha
        col = tuple(int(cc * k) for cc in base)
        d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=col)
        if z > 0.75: d.point((int(x) - 1, int(y) - 1), fill=tuple(min(255, int(cc * 1.3 * alpha)) for cc in base))

def draw_nucleus(c, t, intro=False):
    """single fission, local time t of the nucleus scene (intro: t<0, idle)"""
    d = c.a
    if t < SPLIT0:
        wob = 0.0 if t < 2.0 else (t - 2.0) / (SPLIT0 - 2.0)
        sx = 1 + 0.32 * wob * (1 + 0.25 * math.sin(t * 40)) if t >= 2.0 else 1 + 0.02 * math.sin(t * 6)
        if 2.0 <= t < 2.25:   # absorption flash
            r = 30 + (t - 2.0) * 60; d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=CYAN)
        nucleus_blob(d, CX, CY, 24, 3, sx)
        if wob > 0.6:         # neck forming
            d.rectangle([CX - 1, CY - 26, CX + 1, CY - 18], fill=BGC); d.rectangle([CX - 1, CY + 18, CX + 1, CY + 26], fill=BGC)
        if not intro and t < 2.0:   # incoming neutron
            k = ease(t / 2.0); x = lerp(-6, CX - 22, k); y = lerp(CY + 70, CY + 6, k)
            for j in range(10): d.point((int(x - j * 3), int(y + j * 3.2)), fill=tuple(int(v * (1 - j / 10)) for v in CYAN))
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=NEUT); d.point((int(x) - 1, int(y) - 1), fill=WHITE)
    else:
        a = t - SPLIT0; k = eout(min(1, a / 2.2))
        alpha = max(0.25, 1 - max(0, a - 2.5) / 2.0)
        nucleus_blob(d, CX - 10 - 52 * k, CY - 6 - 30 * k, 19, 5, 1.0, alpha)   # Ba-144
        nucleus_blob(d, CX + 10 + 50 * k, CY + 6 + 32 * k, 16, 7, 1.0, alpha)   # Kr-90
        if a < 0.5:   # flash
            r = 8 + a * 160; d.ellipse([CX - r, CY - r, CX + r, CY + r], outline=WHITE if a < 0.15 else MAG)
            q = int(255 * (1 - a / 0.5)); d.ellipse([CX - 10, CY - 10, CX + 10, CY + 10], fill=(q, q, q))
        if a < 2.2:   # two free neutrons
            for ang in (-0.35, math.pi - 0.2):
                x = CX + math.cos(ang) * (8 + a * 70); y = CY + math.sin(ang) * (8 + a * 70)
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=NEUT); d.point((int(x), int(y)), fill=WHITE)
        lab = alpha > 0.5
        return lab, (CX - 10 - 52 * k, CY - 6 - 30 * k), (CX + 10 + 50 * k, CY + 6 + 32 * k)
    return False, None, None

def draw_chain(c, T):
    d = c.a
    lattice(c, T)
    g, _ = gen_at(T)
    # neutron paths of the early tree
    if g <= 8:
        for (gg, i), (x, y, tn, _) in NODES.items():
            if gg == 0 or gg > 6: continue
            px, py, tp, _ = NODES[(gg - 1, i // 2)]
            if T < tp: continue
            k = min(1.0, (T - tp) / max(1e-3, tn - tp))
            fadek = max(0.0, 1 - (T - tn) / 2.5) if T > tn else 1.0
            col = tuple(int(v * 0.45 * fadek) for v in CYAN)
            if fadek > 0: d.line([px, py, lerp(px, x, k), lerp(py, y, k)], fill=col)
            if k < 1:
                nx, ny = lerp(px, x, k), lerp(py, y, k)
                d.rectangle([nx - 1, ny - 1, nx + 1, ny + 1], fill=NEUT)
        x0, y0, _, _ = NODES[(0, 0)]
        d.ellipse([x0 - 3, y0 - 3, x0 + 3, y0 + 3], outline=(60, 40, 90))
    # remnants of earlier splits (embers), then live flashes
    i1 = int(np.searchsorted(SPLT, T + 1e-9))
    i0 = int(np.searchsorted(SPLT, T - 1.6))
    for s in SPL[i0:i1]:
        a = T - s[0]; x, y = int(s[1]), int(s[2])
        if a < 0.05:
            r = 3 if s[3] <= 6 else 2
            d.line([x - r, y, x + r, y], fill=WHITE); d.line([x, y - r, x, y + r], fill=WHITE)
        elif a < 0.35:
            r = 1 + a * (16 if s[3] <= 6 else 8)
            d.ellipse([x - r, y - r, x + r, y + r], outline=MAG if a < 0.2 else (120, 40, 110))
            d.point((x, y), fill=CYAN)
        else:
            k = max(0.0, 1 - (a - 0.35) / 1.25)
            d.point((x, y), fill=(int(90 * k) + 20, int(60 * k) + 10, int(140 * k) + 30))
    # heat glow grows with log(splits)
    n = splits(T); h = math.log10(max(1, n)) / math.log10(TARGET)
    if h > 0.45:
        arr = np.array(c.art).astype(np.float32)
        yy, xx = np.mgrid[0:AH, 0:AW]
        r2 = ((xx - CX) ** 2 + (yy - CY) ** 2) / (RMAX * RMAX)
        glow = np.exp(-r2 * 1.6)[..., None] * ((h - 0.45) / 0.55) ** 1.5
        arr += glow * np.array([120, 50, 160], np.float32) * 0.9
        c.art = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); c.a = ImageDraw.Draw(c.art)

CH_T = np.arange(START["chain"], START["outro"], 1 / FPS)
CH_N = np.array([math.log10(max(1, splits(t))) for t in CH_T])
def draw_chart(c, T):
    x0, x1, yb, h = 18, 162, 304, 30
    top = math.log10(TARGET) * 1.04
    c.a.rectangle([x0 - 3, yb - h - 4, x1 + 3, yb + 3], fill=(6, 8, 20), outline=(40, 46, 90))
    for k in range(0, 11, 2):
        yy = yb - k / top * h; c.a.line([x0, yy, x1, yy], fill=(16, 20, 44))
    yj = yb - math.log10(TARGET) / top * h
    for xx in range(x0, x1, 4): c.a.line([xx, yj, xx + 1, yj], fill=(170, 60, 150))
    n = int(np.searchsorted(CH_T, T, side="right"))
    if n >= 2:
        xs = x0 + (x1 - x0) * (CH_T[:n] - CH_T[0]) / (CH_T[-1] - CH_T[0])
        ys = yb - CH_N[:n] / top * h
        c.a.line(list(zip(xs.tolist(), ys.tolist())), fill=CYAN)
        c.a.rectangle([xs[-1] - 1, ys[-1] - 1, xs[-1] + 1, ys[-1] + 1], fill=WHITE)
    if T < T_REC: text(c.t, x0 * 2, (yb - h - 4) * 2 - 18, "SPLITS SO FAR (LOG)", fill=DIM)
    if T < T_REC: text(c.t, x1 * 2, int(yj * 2) - 20, "1 JOULE", fill=MAG, align="r")

def hud(c, T, title):
    n = splits(T); g, _ = gen_at(T)
    val = fmt_count(n) + (" SPLIT" if int(n) == 1 else " SPLITS")
    if len(val) > 14: val = fmt_count(n)
    panel(c.t, title, val, "ENERGY " + fmt_J(n * E_SPLIT_J), [CREAM] * 20, right=["GEN", str(g), ""] if T >= START["chain"] else None,
          style="cool", sub_col=CYAN)
    c.t.rectangle([40, 66, 320, 67], fill=MAG); c.t.rectangle([40, 155, 320, 156], fill=MAG)

def banner(c, T):
    cur = None
    for b in BANNERS:
        if b[0] <= T < b[0] + (HOLD + 0.2 if b[1] == "1 JOULE!" else 2.4 if b[3] else 2.0): cur = b
    if cur is None: return
    a = T - cur[0]; tt, sub, big = cur[1], cur[2], cur[3]
    yb = 470
    if big:
        w = max(16 * len(tt), 8 * len(sub)) + 28
        c.t.rectangle([180 - w / 2, yb - 8, 180 + w / 2, yb + 52], fill=(24, 6, 30)); c.t.rectangle([180 - w / 2, yb - 8, 180 + w / 2, yb - 7], fill=MAG)
        text(c.t, 180, yb - 6, tt, size=40, fill=WHITE if a < 0.1 else CREAM, align="c")
        if a > 0.25: text(c.t, 180, yb + 32, sub, fill=CYAN, align="c")
        if tt == "1 JOULE!" and a > 0.9:
            c.t.rectangle([24, yb + 52, 336, yb + 72], fill=(24, 6, 30))
            text(c.t, 180, yb + 52, "= LIFTING AN APPLE 1 M (3.3 FT)", fill=CREAM, align="c")
    else:
        n = int(min(len(tt), a * 40))
        w = 8 * max(len(tt), len(sub)) + 24
        c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 40], fill=(8, 6, 24)); c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 1], fill=MAG)
        text(c.t, 180, yb + 1, tt[:n], fill=CREAM, align="c")
        if a > 0.35: text(c.t, 180, yb + 19, sub, fill=CYAN, align="c")

def sc_intro(t):
    c = Ctx(base_bg())
    draw_nucleus(c, -1 + t * 0.0, intro=True)
    q = ease((t - 0.1) / 0.4)
    if q > 0:
        c.t.rectangle([30, 70, 300, 160], fill=(6, 6, 16)); c.t.rectangle([30, 70, 300, 71], fill=MAG)
        text(c.t, 40, 74, "ONE ATOM", size=40); text(c.t, 40, 112, "SPLITS." if t > 0.7 else "", size=40, fill=CYAN)
    if t > 1.3: text(c.t, 180, 520, "EVERY BEEP =", fill=CREAM, align="c")
    if t > 1.7: text(c.t, 180, 542, "ONE ATOM SPLITTING", fill=MAG, align="c")
    if t > 2.6: text(c.t, 180, 590, "HOW MANY TO MAKE 1 JOULE?", fill=DIM, align="c")
    return c

def sc_nucleus(t):
    c = Ctx(base_bg())
    lab, pa, pb = draw_nucleus(c, t)
    T = START["nucleus"] + t
    if t >= SPLIT0: hud(c, T, TITLES["nucleus"])
    else: panel(c.t, TITLES["nucleus"], "U-235", "92 P + 143 N", [CREAM] * 8, style="cool", sub_col=CYAN); c.t.rectangle([40, 66, 320, 67], fill=MAG); c.t.rectangle([40, 155, 320, 156], fill=MAG)
    if lab and pa:
        text(c.t, pa[0] * 2, pa[1] * 2 - 70, "BA-144", fill=PROT, align="c"); text(c.t, pb[0] * 2, pb[1] * 2 + 44, "KR-90", fill=NEUT, align="c")
    banner(c, T)
    return c

def sc_chain_gen(name):
    def f(t):
        T = START[name] + t
        c = Ctx(base_bg())
        draw_chain(c, T)
        draw_chart(c, T)
        hud(c, T, TITLES[name])
        banner(c, T)
        return c
    return f

def sc_outro(t):
    c = Ctx(base_bg())
    W = c.t
    q = ease(t / 0.5)
    W.rectangle([24, 70, 336, 220], fill=(6, 6, 16)); W.rectangle([24, 70, 336, 71], fill=MAG)
    text(W, 180, 76, "1 GRAM OF URANIUM-235", fill=DIM, align="c")
    text(W, 180, 98, "2.6 SEXTILLION", size=40, fill=CREAM, align="c")
    text(W, 180, 138, "ATOMS", fill=CREAM, align="c")
    if t > 1.2:
        text(W, 180, 168, "ALL SPLIT: ~82 GJ", fill=CYAN, align="c"); text(W, 180, 188, "~23,000 KWH OF HEAT", fill=CYAN, align="c")
    # a calm, steady chain: one split triggers exactly one more
    if t > 3.4:
        a = t - 3.4
        W.rectangle([24, 300, 336, 420], fill=(6, 6, 16)); W.rectangle([24, 300, 336, 301], fill=(110, 116, 112))
        text(W, 180, 306, "IN A POWER REACTOR:", fill=YEL, align="c")
        text(W, 180, 330, "EACH SPLIT TRIGGERS", fill=CREAM, align="c"); text(W, 180, 350, "EXACTLY ONE MORE.", fill=CREAM, align="c")
        if a > 1.6: text(W, 180, 384, "STEADY. NOT 2, 4, 8...", fill=MAG, align="c")
        k = int(a / 0.62)
        for j in range(min(k + 1, 9)):
            x = 22 + j * 17; y = 236
            col = WHITE if j == k and (a % 0.62) < 0.08 else (90, 60, 140)
            c.a.ellipse([x - 3, y - 3, x + 3, y + 3], outline=col)
            if j > 0: c.a.line([x - 14, y, x - 4, y], fill=(50, 120, 150))
    if t > 6.2: text(W, 180, 560, "DATA: WORLD NUCLEAR ASSOCIATION,", fill=DIM, align="c"); text(W, 180, 580, "NUCLEAR-POWER.COM, EURONUCLEAR", fill=DIM, align="c")
    return c

SCENEFN = {"intro": sc_intro, "nucleus": sc_nucleus, "chain": sc_chain_gen("chain"), "swarm": sc_chain_gen("swarm"),
           "climax": sc_chain_gen("climax"), "outro": sc_outro}
# the outro steady chain: one beep per link (each flash has its note)
for j in range(9): ev(START["outro"] + 3.4 + j * 0.62, "bip", r=j % 3, rate=1.6, lon=float(-60 + j * 15), pl=7.0)
EV.sort(key=lambda e: e[0])

# ================= FX =================
def intensity(T): return 0.06 + 0.7 * ease(T / T_REC) ** 2.0
def active_glitch(T):
    for g in GL:
        if g[0] <= T < g[0] + g[1]: return g
    return None
def fx(fr, T, name, t):
    I = intensity(T) * FXK
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    si = np.searchsorted(SNARES, T, side="right") - 1
    sp = math.exp(-(T - SNARES[si]) / 0.06) if si >= 0 else 0.0
    if name == "outro": I *= 0.3
    push = 1.01 + 0.03 * I * ease(t / DUR[name])
    kd = (T - KICKS[ki]) if ki >= 0 else 9
    spring = math.exp(-kd / 0.11) * math.cos(2 * math.pi * kd / 0.17)
    zoom = push + kp * (0.01 + 0.03 * I)
    sd = (T - SNARES[si]) if si >= 0 else 9
    squash = math.exp(-sd / 0.09) * math.cos(2 * math.pi * sd / 0.14)
    rng = random.Random(int(T * 1000)); sh = sp * 10 * I
    fr = warp(fr, zoom * (1 - 0.02 * squash * I), rng.uniform(-sh, sh), -spring * (6 + 50 * I) + rng.uniform(-sh, sh), zoom * (1 + 0.04 * squash * I))
    split = int((sp * 12 + kp * 3) * max(0.0, I - 0.35))
    if split > 0:
        out = fr.copy(); out[:, split:, 0] = fr[:, :-split, 0]; out[:, :-split, 2] = fr[:, split:, 2]; fr = out
    fl = kp * (10 + 30 * I)
    if fl > 1: fr = np.minimum(255, fr.astype(np.int16) + int(fl)).astype(np.uint8)
    for tm, _ in MILES:
        if 0 <= T - tm < 0.12: fr = np.minimum(255, fr.astype(np.int16) + int(110 * (1 - (T - tm) / 0.12))).astype(np.uint8)
    if 0 <= T - T_SPLIT0 < 0.15: fr = np.minimum(255, fr.astype(np.int16) + int(140 * (1 - (T - T_SPLIT0) / 0.15))).astype(np.uint8)
    return fr

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    g = active_glitch(T)
    if g and g[2] == "stutter":
        T2 = g[0] + ((T - g[0]) % g[3]); t = T2 - START[name]
        if t < 0: idx -= 1; name = NAMES[idx]; t = T2 - START[name]
    if g and g[2] == "tapestop":
        p = (T - g[0]) / g[1]; T2 = g[0] + g[1] * (p - p * p / 2); t = T2 - START[name]
        if t >= DUR[name]: t = DUR[name] - 1e-3
    c = SCENEFN[name](t)
    fr = v2.compose(c, t, idx)
    fr = fx(fr, START[name] + t, name, t)
    if g: fr = glitch_frame(fr, T, g)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.2)) / 1.2)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.3)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

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
    mode, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((360, 640), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print("splits drawn", len(SPL), "T_REC", round(T_REC, 2), "miles", [(round(a, 2), b) for a, b in MILES])
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
