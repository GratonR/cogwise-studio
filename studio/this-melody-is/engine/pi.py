"""THIS MELODY IS PI — event-driven pixel short. Every visual event is also a sound event."""
import sys, os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, CREAM, YEL, RED, DIM, GREEN, GREEN_HI, text, panel, ease, eout, mix, shade,
                pix_arc, pix_line, lerp, bg, noise)

v2._GL["π"] = [".......", "#######", ".#...#.", ".#...#.", ".#...#.", ".#...#.", ".#...#.", ".#...##"]
v2._GL_Y["π"] = 8

# ---------- digits of pi (Machin) ----------
def pi_digits(n):
    def arccot(x, unity):
        s = term = unity // x; x2 = x * x; k = 3; sign = -1
        while term: term //= x2; s += sign * (term // k); sign = -sign; k += 2
        return s
    u = 10 ** (n + 10)
    p = 4 * (4 * arccot(5, u) - arccot(239, u))
    s = str(p // 10 ** 10)
    return s[0] + "." + s[1:n]
PI = pi_digits(2100)
PID = [int(c) for c in PI if c.isdigit()]

LONG = os.environ.get("PI_LONG") == "1"
FXK = float(os.environ.get("PI_FX", "1"))
# ---------- tempo map (accelerating) ----------
def bpm(t):
    return 148 + 44 * ease(t / START["eniac"]) + 40 * ease((t - START["eniac"]) / 5.2)
def beat_times(T):
    out, t = [], 0.0
    while t < T: out.append(t); t += 60 / bpm(t)
    return out

# ---------- scene timing ----------
SC = [("intro", 4.0), ("babylon", 5.2), ("archimedes", 6.6), ("buffon", 10.2 if LONG else 6.6), ("madhava", 7.4 if LONG else 5.4),
      ("galperin", 14.2 if LONG else 8.8), ("eniac", 6.2), ("outro", 4.6)]
START, acc = {}, 0.0
for n, d in SC: START[n] = acc; acc += d
TOTAL = acc
DUR = dict(SC)

EV = []  # (t_abs, kind, dict)
_BEATS = None
def grid16(t_from, n, every=1):
    """n times on the 16th-note grid of the accelerating tempo, starting at first slot >= t_from"""
    global _BEATS
    if _BEATS is None: _BEATS = beat_times(TOTAL + 2)
    g = []
    for b in _BEATS:
        bl = 60 / bpm(b)
        g += [b + k * bl / 4 for k in range(4)]
    g = [x for x in g if x >= t_from - 1e-6]
    return g[::every][:n]
def ev(t, kind, **kw): EV.append((t, kind, kw))

def correct_mask(s):
    out, ok = [], True
    for i, ch in enumerate(s):
        ok = ok and i < len(PI) and PI[i] == ch
        out.append(ok)
    return out

def type_events(s0, s, t_start, dt, tag):
    """type string s char by char; each digit is a note (wrong digits sound wrong)"""
    ok = correct_mask(s); times = []
    every = max(1, round(dt / 0.1))
    gt = grid16(t_start, len(s), every)
    for i, ch in enumerate(s):
        t = gt[i]; times.append(t)
        if ch.isdigit(): ev(t, "digit", d=int(ch), ok=ok[i], tag=tag)
    return times

# ---- build schedule ----
SCH = {}
def build():
    # INTRO: type 3.14159265358979 on 8ths, wheel rolls
    s = "3.14159265358979"
    st = START["intro"]
    SCH["intro_type"] = type_events("", s, st + 0.15, 0.2, "intro")
    ev(START["babylon"] - 0.5, "riser")

    # BABYLON: 20 wedges, hexagon carve, value 3.125
    st = START["babylon"]
    SCH["wedges"] = grid16(st + 0.15, 20)
    for i, t in enumerate(SCH["wedges"]): ev(t, "wedge", i=i)
    SCH["carve"] = (st + 2.4, st + 3.3)
    for k in range(7): ev(st + 2.4 + k * 0.13, "scrape", i=k)
    SCH["bab_type"] = type_events("", "3.125", st + 3.6, 0.13, "bab")
    ev(st + 3.6 + 5 * 0.13 + 0.05, "error")

    # ARCHIMEDES: circle, then polygons 6..96 with vertex ticks accelerating
    st = START["archimedes"]
    ev(st + 0.1, "whoosh")
    SCH["arch_poly"] = []
    t = st + 0.7
    for lvl, n in enumerate([6, 12, 24, 48, 96]):
        span = [1.1, 1.0, 0.9, 0.75, 0.65][lvl]
        vt = [t + span * (k + 1) / n for k in range(n)]
        for k, x in enumerate(vt): ev(x, "vert", lvl=lvl, k=k, n=n)
        ev(t + span + 0.02, "chime", lvl=lvl)
        SCH["arch_poly"].append((n, t, t + span))
        t += span + 0.08
    SCH["arch_type"] = type_events("", "3.1418", t + 0.1, 0.1, "arch")

    # BUFFON: needles drop, rate 4/s -> 48/s
    st = START["buffon"]
    times, t = [], st + 0.25
    BW = DUR["buffon"] - 0.9
    while t < st + BW:
        r = 4 * ((150 if LONG else 14) ** ((t - st) / BW)); times.append((t, r)); t += 1 / r
    best = None
    for seed in range(20000):
        rng = random.Random(seed); C = 0; ests = []
        nd = []
        for i in range(len(times)):
            cy, ang, cx = rng.uniform(96, 300), rng.uniform(0, math.pi), rng.uniform(22, 158)
            y1, y2 = cy - 12 * math.sin(ang), cy + 12 * math.sin(ang)
            cross = math.floor(y1 / 24) != math.floor(y2 / 24)
            C += cross; nd.append((cx, cy, ang, cross))
        if C == round(2 * len(times) / math.pi):
            best = (seed, nd); break
    SCH["needles"] = [(t, *n) for (t, r), n in zip(times, best[1])]
    for (t, r), n in zip(times, best[1]): ev(t, "needle", cross=n[3], rate=r)
    SCH["buf_end"] = st + BW + 0.1

    # MADHAVA: series terms rate 4/s -> 44/s
    st = START["madhava"]
    terms, t = [], st + 0.3
    MW = DUR["madhava"] - 0.7
    while t < st + MW:
        r = 4 * ((70 if LONG else 13) ** ((t - st) / MW)); terms.append(t); ev(t, "term", k=len(terms) - 1, rate=r); t += 1 / r
    SCH["terms"] = terms

    # GALPERIN: 3 runs with mass ratio 1, 100, 10000
    st = START["galperin"]
    runs = []
    t = st + 0.2
    for d, win in (((0, 1.7), (1, 2.3), (2, 3.6), (3, 5.6)) if LONG else ((0, 1.7), (1, 2.5), (2, 4.0))):
        sim = clack_sim(100 ** d)
        last = sim[-1][0] if len(sim) > 1 else 1
        k = (win * 0.62) / max(last, 1e-9)
        runs.append(dict(d=d, t0=t, win=win, k=k, sim=sim))
        for e in sim[1:]: ev(t + e[0] * k, "clack", wall=e[5], d=d)
        cnt = len(sim) - 1
        val = str(cnt)[0] + ("." + str(cnt)[1:] if d else "")
        ev(t + win * 0.72, "chime", lvl=d + 2)
        t += win + 0.15
    SCH["runs"] = runs

    # ENIAC: digit stream rate 10 -> 90/s (notes), counter to 2037
    st = START["eniac"]
    dts, t, i = [], st + 0.3, 0
    EW = 4.9
    while t < st + EW:
        r = 10 * (12 ** ((t - st) / EW))
        dts.append((t, i)); ev(t, "edigit", d=PID[i], rate=r)
        t += 1 / r; i += 1
    SCH["eniac"] = dts
    ev(st + 5.45, "glitch")
    drums_and_glitches()
    # OUTRO
    st = START["outro"]
    ev(st, "final")

CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
KICKS, SNARES = [], []
GL = []  # (t0, dur, kind, slice)
def scene_at(t):
    for n, d in SC:
        if START[n] <= t < START[n] + d: return n
    return "outro"
def drums_and_glitches():
    beats = beat_times(TOTAL)
    E = START["eniac"]
    for bi, bt in enumerate(beats):
        if bt >= START["outro"] - 0.05: break
        sc = scene_at(bt); bl = 60 / bpm(bt); pos = bi % 4
        ch = CHORDS[(bi // 4) % 4]; root = ch[0] - 12
        full = sc in ("archimedes", "buffon", "madhava", "eniac")
        fin = sc == "eniac" and bt > E + 3.4          # finale: everything doubles
        if sc != "intro":
            if sc == "galperin":
                if pos == 0: ev(bt, "kick", v=0.42)
            else:
                ev(bt, "kick", v=0.5 if full else 0.38)
                if fin or (sc == "eniac" and bt > E + 2.0): ev(bt + bl / 2, "kick", v=0.36)
            if full and pos in (1, 3) and not fin: ev(bt, "snare", v=0.22)
            if fin:  # snare roll 16ths -> 32nds
                div = 4 if bt < E + 4.4 else 8
                for h in range(div): ev(bt + h * bl / div, "snare", v=0.08 + 0.14 * (h + 1) / div)
        if sc != "galperin" or pos % 2 == 0:
            sub = 4 if sc in ("madhava", "eniac", "buffon") else 2
            for h in range(sub):
                if sc == "intro" and h % 2: continue
                ev(bt + h * bl / sub, "hat", v=0.045 if h % 2 else 0.06, open=(h == sub // 2 and sc != "intro"))
        for h in range(2):
            if sc == "intro" and h == 1: continue
            m = root + (12 if (pos * 2 + h) % 4 == 3 else 0) + (int(3 * ease((bt - E - 3.4) / 1.6)) * 2 if fin else 0)
            ev(bt + h * bl / 2, "bass", m=m, d=bl / 2 * 0.9, v=0.22 if sc != "intro" else 0.16)
        if pos == 0 and sc in ("galperin", "babylon"): ev(bt, "pad", ch=ch, d=bl * 4)
    for t, k, kw in EV:
        if k == "kick": KICKS.append(t)
        if k == "snare" and kw["v"] > 0.15: SNARES.append(t)
    KICKS.sort(); SNARES.sort()
    # glitches (audio stutter/crush/tapestop mirrored in video) — denser toward the end
    def bl_at(t): return 60 / bpm(t)
    GL.append((START["archimedes"] - 0.22, 0.22, "stutter", bl_at(START["archimedes"]) / 4))
    GL.append((SCH["arch_poly"][4][1] + 0.1, 0.25, "crush", 0))
    GL.append((START["madhava"] - 0.28, 0.28, "stutter", bl_at(START["madhava"]) / 8))
    GL.append((START["galperin"] - 0.3, 0.3, "stutter", bl_at(START["galperin"]) / 4))
    r1 = SCH["runs"][1]; GL.append((r1["t0"] + r1["win"] * 0.72 + 0.05, 0.22, "crush", 0))
    GL.append((START["eniac"] - 0.25, 0.25, "stutter", bl_at(START["eniac"]) / 8))
    GL.append((E + 2.2, 0.18, "stutter", bl_at(E + 2.2) / 4))
    GL.append((E + 3.2, 0.22, "crush", 0))
    GL.append((E + 3.9, 0.2, "stutter", bl_at(E + 3.9) / 8))
    GL.append((E + 4.45, 0.15, "stutter", bl_at(E + 4.45) / 16))
    GL.append((E + 4.95, 0.5, "tapestop", 0))
    if FXK < 0.8:   # soft: keep only transitions + finale
        GL[:] = [g for g in GL if g[2] != "crush" or g[0] > E]
    if FXK > 1.2:   # hard: extra stutters/crushes mid-scene
        for n_ in ("babylon", "archimedes", "buffon", "madhava", "galperin"):
            m = START[n_] + DUR[n_] * 0.55
            b = [x for x in KICKS if x >= m][0]
            GL.append((b, 0.16, "stutter" if n_ != "archimedes" else "crush", bl_at(b) / 8))
        GL.sort()

def clack_sim(ratio):
    """exact event sim; returns list of (t, xs, vs, xb, vb, wall_flag). widths: small 10, big depends"""
    ws, wb = 10, BIGW[ratio]
    xs, vs, xb, vb = 46.0, 0.0, 96.0, -1.0
    m, M = 1.0, float(ratio)
    t = 0.0; out = [(0, xs, vs, xb, vb, False)]
    for _ in range(100000):
        tb = (xb - (xs + ws)) / (vs - vb) if vs - vb > 1e-12 else math.inf
        tw = (xs - 16) / (-vs) if vs < -1e-12 else math.inf
        dt = min(tb, tw)
        if dt == math.inf: break
        t += dt; xs += vs * dt; xb += vb * dt
        if tb <= tw:
            vs, vb = ((m - M) * vs + 2 * M * vb) / (m + M), ((M - m) * vb + 2 * m * vs) / (m + M); xb = xs + ws
            out.append((t, xs, vs, xb, vb, False))
        else:
            vs = -vs; xs = 16; out.append((t, xs, vs, xb, vb, True))
    return out
BIGW = {1: 12, 100: 22, 10000: 34, 1000000: 48}

build()
EV.sort(key=lambda e: e[0])

# ================= visuals =================
class Ctx(v2.Ctx):
    def __init__(self, arr):
        self.art = Image.fromarray(arr.copy()); self.a = ImageDraw.Draw(self.art)
        self.txt = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); self.t = ImageDraw.Draw(self.txt); self.t.fontmode = "1"

_B = {}
def mkbg(name):
    if name in _B: return _B[name]
    a = np.zeros((AH, AW, 3), np.float32)
    rng = np.random.default_rng(hash(name) % 1000)
    if name == "sand":
        a[:] = (214, 184, 128)
        yy, xx = np.mgrid[0:AH, 0:AW]
        rip = np.sin(yy / 3.2 + np.sin(xx / 17) * 2.2)
        a *= (0.96 + 0.05 * (rip > 0.75))[..., None]
        a[(rip < -0.92)] *= 0.9
        sp = rng.random((AH, AW)); a[sp < 0.03] *= 0.86; a[sp > 0.985] = (236, 214, 166)
        a[:26] = (66, 128, 170); a[26:29] = (230, 240, 236); a[24:26] = (110, 170, 196)  # sea strip
    elif name == "planks24":
        y = 0
        while y < AH:
            c = np.array((158, 104, 62)) * rng.uniform(0.86, 1.1)
            a[y:y + 24] = c
            for _ in range(8):
                gy, gx, gl = y + rng.integers(2, 22), rng.integers(0, AW), rng.integers(8, 34)
                if gy < AH: a[gy, gx:gx + gl] = c * 0.9
            a[y] = (60, 36, 20); a[min(AH - 1, y + 1)] = c * 1.12
            x = rng.integers(-40, 0)
            while x < AW:
                x += rng.integers(60, 120)
                if 0 <= x < AW: a[y:y + 24, x] = c * 0.62
            y += 24
    elif name == "palm":
        a[:] = (48, 30, 20)
        for x0 in range(0, AW, 16): a[:, x0] *= 0.8
        a *= (0.94 + 0.08 * noise((AH, AW), 9, 4))[..., None]
    elif name == "lab":
        a[:] = (34, 40, 56)
        yy, xx = np.mgrid[0:AH, 0:AW]
        a[(xx % 20 == 0) | (yy % 20 == 0)] = (40, 48, 66)
        a[248:] = (96, 64, 40); a[248] = (150, 104, 66); a[249] = (120, 80, 48)
        for x in range(0, AW, 18): a[250:, x] = (70, 44, 26)
        a[120:249, 8:16] = (120, 124, 132); a[120:249, 15] = (70, 72, 80); a[120:249, 8] = (160, 164, 172)
        for y in range(122, 248, 6): a[y, 8:15] = (90, 94, 100)
    elif name == "eniac":
        a[:] = (10, 14, 16)
        a[::2] *= 0.85
    _B[name] = np.clip(a, 0, 255).astype(np.uint8)
    return _B[name]

def upto(times, t): return sum(1 for x in times if x <= t)

def last_change(times, t):
    p = [x for x in times if x <= t]; return (t - p[-1]) if p else None

def typed_value(s, times, t):
    n = upto(times, t); v = s[:n]
    return v, [CREAM if ok else RED for ok in correct_mask(v)]

def big_wheel(d, cx, cy, r, ang):
    cx, cy = int(round(cx)), int(round(cy))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(110, 74, 20))
    d.ellipse([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], outline=(236, 184, 60))
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], outline=(176, 128, 40))
    pix_arc(d, cx, cy, r - 1, math.pi * 1.05, math.pi * 1.45, (255, 236, 150))
    for k in range(4):
        a = ang + k * math.pi / 4
        d.line([cx - (r - 3) * math.cos(a), cy - (r - 3) * math.sin(a), cx + (r - 3) * math.cos(a), cy + (r - 3) * math.sin(a)], fill=(210, 160, 50))
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 226, 130), outline=(110, 74, 20))
    mx, my = cx + (r - 1) * math.cos(ang + math.pi / 2), cy + (r - 1) * math.sin(ang + math.pi / 2)
    d.rectangle([mx - 1, my - 1, mx + 1, my + 1], fill=RED)

def pi_line(c, pos, tag=True):
    y, x0, u = 200, 20, 36
    c.a.line([10, y, 172, y], fill=(80, 150, 190)); c.a.line([10, y + 1, 172, y + 1], fill=(30, 50, 80))
    for k in range(5):
        c.a.line([x0 + k * u, y - 2, x0 + k * u, y + 2], fill=CREAM)
        text(c.t, (x0 + k * u) * 2 - 4, y * 2 + 8, str(k), fill=DIM)
    x = x0 + pos * u
    if pos > 0:
        c.a.line([x0, y, x, y], fill=RED); c.a.line([x0, y - 1, x, y - 1], fill=(160, 40, 30))
    r = u / 2
    big_wheel(c.a, x, y - r - 1, int(r), pos * u / r)
    if tag and pos > 3.1:
        X = int(x * 2)
        c.t.rectangle([X - 7, y * 2 + 30, X + 7, y * 2 + 46], fill=YEL)
        text(c.t, X - 3, y * 2 + 28, "π", fill=(30, 20, 10))

def flash(c, t, times, x, y, col=(255, 250, 220), dur=0.06, r=3):
    for x0 in times:
        if 0 <= t - x0 < dur:
            c.a.line([x - r, y, x + r, y], fill=col); c.a.line([x, y - r, x, y + r], fill=col)

# ---- scenes (t = local time) ----
def sc_intro(t):
    c = Ctx(bg("grid"))
    c.t.rectangle([30, 76, 252, 158], fill=(6, 7, 12))
    text(c.t, 40, 74, "THIS MELODY", size=40); text(c.t, 40, 112, "IS π", size=40)
    s = "3.14159265358979"
    n = upto(SCH["intro_type"], START["intro"] + t)
    v = s[:n]
    text(c.t, 40, 226, v[:10], size=40)
    if len(v) > 10: text(c.t, 40, 264, v[10:], size=40)
    lc = last_change(SCH["intro_type"], START["intro"] + t)
    if lc is not None and lc < 0.08:  # key hit flash under last digit
        k = len(v) - 1; xx = 40 + 16 * (k if k < 10 else k - 10); yy = 226 if k < 10 else 264
        c.t.rectangle([xx, yy + 34, xx + 14, yy + 36], fill=YEL)
    pi_line(c, math.pi * eout((t - 0.15) / 3.2))
    return c

def tablet(c):
    d = c.a
    x0, y0, x1, y1 = 30, 104, 150, 262
    d.rounded_rectangle([x0 + 4, y0 + 5, x1 + 4, y1 + 5], 10, fill=(30, 18, 10))
    d.rounded_rectangle([x0, y0, x1, y1], 10, fill=(172, 120, 76))
    d.rounded_rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], 9, fill=(186, 134, 88))
    d.rounded_rectangle([x0 + 5, y0 + 5, x1 - 4, y1 - 4], 7, fill=(194, 144, 96))
    rng = random.Random(4)
    for _ in range(140):
        x, y = rng.randint(x0 + 6, x1 - 6), rng.randint(y0 + 6, y1 - 6)
        d.point((x, y), fill=rng.choice([(176, 126, 80), (208, 160, 110)]))
    for (a, b) in (((x1 - 18, y0 + 2), (x1 - 26, y0 + 22)), ((x1 - 26, y0 + 22), (x1 - 22, y0 + 34)), ((x0 + 2, y1 - 30), (x0 + 16, y1 - 22))):
        d.line([a, b], fill=(110, 72, 40)); d.line([(a[0] + 1, a[1]), (b[0] + 1, b[1])], fill=(214, 168, 118))

def carve_line(d, p, q, prog=1):
    pix_line(d, p, q, (112, 74, 42), prog); pix_line(d, (p[0], p[1] + 1), (q[0], q[1] + 1), (216, 172, 122), prog)

def wedge(d, x, y, depth=1.0):
    dark, lite = (104, 66, 36), (222, 178, 128)
    d.polygon([(x, y), (x + 4, y + 2), (x, y + 4)], fill=dark)
    d.line([x + 4, y + 2, x + 9, y + 2], fill=dark); d.line([x, y + 5, x + 4, y + 3], fill=lite)

def sc_babylon(t):
    c = Ctx(bg("desk")); T = START["babylon"] + t
    tablet(c)
    cx, cy, r = 90, 150, 30
    a0, a1 = SCH["carve"]
    q = ease((T - a0) / (a1 - a0))
    if q > 0:
        pix_arc(c.a, cx, cy + 1, r, 0, 2 * math.pi, (216, 172, 122), q)
        pix_arc(c.a, cx, cy, r, 0, 2 * math.pi, (112, 74, 42), q)
        hx = [(cx + r * math.cos(k * math.pi / 3), cy + r * math.sin(k * math.pi / 3)) for k in range(7)]
        for k in range(6):
            qq = max(0, min(1, q * 6 - k))
            if qq > 0: carve_line(c.a, hx[k], hx[k + 1], qq)
        if q >= 1: carve_line(c.a, (cx - r, cy), (cx + r, cy))
    rows = [(46, 196), (46, 212), (46, 228), (46, 244)]
    n = upto(SCH["wedges"], T)
    for i in range(n):
        rx, ry = rows[i // 5]; wedge(c.a, rx + (i % 5) * 18 + (i // 5 % 2) * 6, ry)
    if n < 20 and T > SCH["wedges"][0] - 0.1:  # stylus
        i = n; rx, ry = rows[min(3, i // 5)]
        sx, sy = rx + (i % 5) * 18 + (i // 5 % 2) * 6, ry
        nxt = SCH["wedges"][min(19, n)]; press = 1 - min(1, (nxt - T) / 0.1)
        sy -= int((1 - press) * 5)
        c.a.line([sx + 1, sy + 1, sx + 16, sy - 22], fill=(70, 50, 24), width=3); c.a.line([sx + 1, sy, sx + 15, sy - 22], fill=(196, 170, 110))
    if q > 0 and q < 1:
        ang = 2 * math.pi * q; sx, sy = cx + r * math.cos(ang), cy + r * math.sin(ang)
        c.a.line([sx, sy, sx + 15, sy - 22], fill=(70, 50, 24), width=3); c.a.line([sx, sy - 1, sx + 14, sy - 23], fill=(196, 170, 110))
    v, cols = typed_value("3.125", SCH["bab_type"], T)
    panel(c.t, "BABYLON ~1900 BC", v or "-", "π ≈ 25 / 8", cols or [DIM], right=["SUSA", "TABLET"], age=last_change(SCH["bab_type"], T))
    return c

def sc_arch(t):
    c = Ctx(mkbg("sand")); T = START["archimedes"] + t
    cx, cy, R = 90, 186, 58
    groove, lite = (176, 142, 92), (234, 212, 166)
    q = ease((T - START["archimedes"] - 0.1) / 0.5)
    pix_arc(c.a, cx, cy + 1, R, -math.pi / 2, 1.5 * math.pi, lite, q)
    pix_arc(c.a, cx, cy, R, -math.pi / 2, 1.5 * math.pi, groove, q)
    c.a.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=groove)
    cur = None
    for lvl, (n, t0, t1) in enumerate(SCH["arch_poly"]):
        if T < t0: break
        k = min(n, int((T - t0) / (t1 - t0) * n + 1e-9))
        old = T > t1 + 0.08 and lvl < 4 and SCH["arch_poly"][lvl + 1][1] <= T
        cin = (70, 42, 20) if not old else (150, 112, 70)
        cout = (200, 48, 30) if not old else (206, 128, 96)
        Ro = R / math.cos(math.pi / n)
        for j in range(k):
            a, b = -math.pi / 2 + 2 * math.pi * j / n, -math.pi / 2 + 2 * math.pi * (j + 1) / n
            pix_line(c.a, (cx + R * math.cos(a), cy + R * math.sin(a)), (cx + R * math.cos(b), cy + R * math.sin(b)), cin)
            if not old and n <= 24: c.a.rectangle([cx + R * math.cos(b) - 1, cy + R * math.sin(b) - 1, cx + R * math.cos(b) + 1, cy + R * math.sin(b) + 1], fill=(40, 24, 10))
            am, bm = a - math.pi / n + math.pi / n, b
            pix_line(c.a, (cx + Ro * math.cos(a - math.pi / n + math.pi / n - math.pi / n), cy + Ro * math.sin(a - math.pi / n)) if False else
                     (cx + Ro * math.cos(a - math.pi / n), cy + Ro * math.sin(a - math.pi / n)),
                     (cx + Ro * math.cos(b - math.pi / n), cy + Ro * math.sin(b - math.pi / n)), cout)
        if not old: cur = (n, k, lvl)
        if k < n and not old:
            a = -math.pi / 2 + 2 * math.pi * k / n
            sx, sy = cx + R * math.cos(a), cy + R * math.sin(a)
            c.a.line([sx, sy, sx + 14, sy - 30], fill=(80, 52, 26), width=3); c.a.line([sx, sy - 1, sx + 13, sy - 31], fill=(150, 108, 60))
            c.a.point((sx, sy), fill=(60, 40, 20))
    n = cur[0] if cur else 0
    vals = {6: "3.2320", 12: "3.1606", 24: "3.1461", 48: "3.1427", 96: "3.1418"}
    vt = SCH["arch_type"]
    if T >= vt[0]:
        v, cols = typed_value("3.1418", vt, T)
        panel(c.t, "ARCHIMEDES ~250 BC", v, "223/71 < π < 22/7", cols, right=["SIDES", "96"], age=last_change(vt, T))
    elif cur and cur[1] == cur[0]:
        v = vals[n]
        panel(c.t, "ARCHIMEDES ~250 BC", v, "POLYGON BOUNDS", [CREAM if ok else RED for ok in correct_mask(v)], right=["SIDES", str(n)],
              age=T - SCH["arch_poly"][cur[2]][2])
    else:
        panel(c.t, "ARCHIMEDES ~250 BC", "-", "POLYGON BOUNDS", [DIM], right=["SIDES", str(n) if n else "-"])
    return c

def needle(d, cx, cy, ang, lift=0.0, cross=False):
    dx, dy = 12 * math.cos(ang), 12 * math.sin(ang)
    cy -= lift
    p, q = (cx - dx, cy - dy), (cx + dx, cy + dy)
    if lift == 0: d.line([(p[0] + 1, p[1] + 2), (q[0] + 1, q[1] + 2)], fill=(80, 50, 28))
    body, hi = ((226, 182, 70), (255, 230, 140)) if cross else ((196, 204, 212), (244, 248, 252))
    d.line([p, q], fill=body); d.line([(p[0], p[1] - 1), ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 - 1)], fill=hi)
    d.point(q, fill=(90, 96, 104)); d.point(p, fill=(255, 255, 255))

def sc_buffon(t):
    c = Ctx(mkbg("planks24")); T = START["buffon"] + t
    N = C = 0; last = None
    for (tt, cx, cy, ang, cr) in SCH["needles"]:
        if tt > T: break
        age = T - tt
        lift = max(0, 1 - age / 0.07) * 14
        needle(c.a, cx, cy, ang + (lift / 14) * 0.6, lift, cr)
        if 0 <= age < 0.06 and cr: flash(c, age, [0], cx, cy, col=(255, 230, 120))
        N += 1; C += cr; last = tt
    if C:
        v = f"{2 * N / C:.4f}"
        panel(c.t, "BUFFON 1777", v, "π ≈ 2N / C", [CREAM if ok else RED for ok in correct_mask(v)], right=["NEEDLES", str(N)], age=None)
    else:
        panel(c.t, "BUFFON 1777", "-", "π ≈ 2N / C", [DIM], right=["NEEDLES", str(N)])
    return c

def palm_leaf(d, y0, h, seed):
    rng = random.Random(seed)
    d.rounded_rectangle([8, y0 + 2, AW - 8, y0 + h + 2], 6, fill=(28, 16, 8))
    d.rounded_rectangle([6, y0, AW - 10, y0 + h], 6, fill=(204, 168, 96))
    for k in range(2, h - 1, 3): d.line([12, y0 + k, AW - 16, y0 + k], fill=(194, 156, 86))
    d.line([10, y0 + 1, AW - 14, y0 + 1], fill=(228, 198, 132)); d.line([10, y0 + h - 1, AW - 14, y0 + h - 1], fill=(160, 120, 60))
    for hx in ((16, AW - 26) if h < 40 else ()): d.ellipse([hx - 2, y0 + h / 2 - 2, hx + 2, y0 + h / 2 + 2], fill=(40, 24, 12))

def sc_madhava(t):
    c = Ctx(mkbg("palm")); T = START["madhava"] + t
    palm_leaf(c.a, 92, 22, 1)
    W = c.t
    text(W, 180, 192, "π/4 = 1 - 1/3 + 1/5 - 1/7 + ...", fill=(70, 40, 18), align="c")
    # plot area leaf
    palm_leaf(c.a, 124, 150, 2)
    gx0, gx1, gy = 18, 160, 199
    for x in range(gx0, gx1, 4): c.a.line([x, gy, x + 1, gy], fill=(196, 60, 40))
    text(W, 330, gy * 2 - 10, "π", fill=(196, 60, 40), align="r")
    terms = SCH["terms"]; n = upto(terms, T)
    S, pts = 0.0, []
    Ntot = len(terms)
    for k in range(n):
        S += 4 * (-1) ** k / (2 * k + 1)
        x = gx0 + (gx1 - gx0) * (k / (Ntot - 1)) ** 0.45
        y = gy - max(-1.1, min(1.1, (S - math.pi) * 0.9)) * 60
        pts.append((x, y))
    for i in range(1, len(pts)): c.a.line([pts[i - 1], pts[i]], fill=(70, 40, 18))
    if pts:
        p = pts[-1]; c.a.rectangle([p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1], fill=(196, 60, 40))
    if n:
        v = f"{S:.5f}"
        panel(c.t, "MADHAVA ~1400", v, "INFINITE SERIES", [CREAM if ok else RED for ok in correct_mask(v)], right=["TERMS", str(n)])
    else:
        panel(c.t, "MADHAVA ~1400", "-", "INFINITE SERIES", [DIM], right=["TERMS", "0"])
    return c

def block(d, x, w, col, y=247):
    x = int(round(x)); top = y - w + 1
    d.rectangle([x, top, x + w - 1, y], fill=col)
    d.line([x, top, x + w - 1, top], fill=shade(col, 1.25)); d.line([x, top, x, y], fill=shade(col, 1.15))
    d.line([x, y, x + w - 1, y], fill=shade(col, 0.6)); d.line([x + w - 1, top, x + w - 1, y], fill=shade(col, 0.7))
    if w > 14:
        d.rectangle([x + 3, top + 3, x + w - 4, y - 3], outline=shade(col, 0.85))

def sim_state(sim, s):
    i = 0
    while i + 1 < len(sim) and sim[i + 1][0] <= s: i += 1
    e = sim[i]; dt = s - e[0]
    return e[1] + e[2] * dt, e[3] + e[4] * dt, i

def sc_galperin(t):
    c = Ctx(mkbg("lab")); T = START["galperin"] + t
    run = [r for r in SCH["runs"] if T >= r["t0"]]
    run = run[-1] if run else SCH["runs"][0]
    s = max(0, (T - run["t0"]) / run["k"])
    sim = run["sim"]; ratio = 100 ** run["d"]
    xs, xb, i = sim_state(sim, s)
    block(c.a, xs, 10, (220, 90, 64)); block(c.a, xb, BIGW[ratio], (80, 130, 196))
    # sparks at recent clacks
    for e in sim[1:i + 1][-6:]:
        age = (s - e[0]) * run["k"]
        if age < 0.05:
            x = 16 if e[5] else e[1] + 10
            c.a.line([x - 3, 241, x + 3, 241], fill=(255, 250, 200)); c.a.line([x, 238, x, 244], fill=(255, 250, 200))
    text(c.t, xs * 2 + 10, 247 * 2 - 40, "1", fill=CREAM, align="c")
    mass = {1: "1", 100: "100", 10000: "10K", 1000000: "1M"}[ratio]
    text(c.t, (xb + BIGW[ratio] / 2) * 2, (247 - BIGW[ratio]) * 2 - 20, mass, fill=CREAM, align="c")
    cnt = i
    W = c.t
    text(W, 180, 330, "COUNT THE CLACKS", fill=DIM, align="c")
    text(W, 180, 350, str(cnt), size=40, fill=YEL, align="c")
    # header value from completed runs
    vals, rev = [], None
    for r in SCH["runs"]:
        if T >= r["t0"] + r["win"] * 0.72:
            n = len(r["sim"]) - 1; vals.append(str(n)[0] + ("." + str(n)[1:] if r["d"] else "")); rev = r["t0"] + r["win"] * 0.72
    v = vals[-1] if vals else "-"
    age = (T - rev) if vals else None
    panel(c.t, "GALPERIN 2003", v, "MASS RATIO 100^N", [CREAM] * 6 if vals else [DIM], right=["RATIO", f"1:{ratio}"], age=age)
    return c

def eniac_rack(d, x0, y0, w, h, T, seed, idx):
    d.rectangle([x0 + 3, y0 + 3, x0 + w + 3, y0 + h + 3], fill=(0, 0, 0))
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(52, 56, 60), outline=(20, 22, 24))
    d.line([x0 + 1, y0 + 1, x0 + w - 1, y0 + 1], fill=(90, 96, 100))
    rng = random.Random(seed)
    for r in range(8):
        for k in range((w - 6) // 5):
            x, y = x0 + 4 + k * 5, y0 + 6 + r * 9
            on = ((idx * 7 + r * 13 + k * 31 + seed) % 5) < 2
            d.rectangle([x, y, x + 2, y + 2], fill=(255, 196, 80) if on else (70, 50, 30))
    for k in range(4):
        x1, x2 = x0 + rng.randint(4, w - 4), x0 + rng.randint(4, w - 4)
        col = rng.choice([(200, 60, 50), (60, 120, 200), (220, 200, 80)])
        sag = rng.randint(8, 20)
        pts = [(lerp(x1, x2, u / 12), y0 + 80 + sag * 4 * (u / 12) * (1 - u / 12)) for u in range(13)]
        d.line(pts, fill=col); d.line([(p[0], p[1] + 1) for p in pts], fill=shade(col, 0.5))
        for p in (pts[0], pts[-1]): d.rectangle([p[0] - 1, p[1] - 2, p[0] + 1, p[1]], fill=(200, 200, 200))
    for r in range(3):
        for k in range((w - 8) // 8):
            d.ellipse([x0 + 5 + k * 8, y0 + 112 + r * 10, x0 + 9 + k * 8, y0 + 116 + r * 10], fill=(150, 150, 150), outline=(30, 30, 30))

def sc_eniac(t):
    c = Ctx(mkbg("eniac")); T = START["eniac"] + t
    ds = SCH["eniac"]; n = upto([x[0] for x in ds], T)
    for k in range(3): eniac_rack(c.a, 8 + k * 56, 92, 50, 150, T, k * 17, n)
    count = min(2037, int(2037 * ease((t - 0.3) / 5.0) ** 1.4)) if t > 0.3 else 0
    count = max(count, n)
    W = c.t
    W.rectangle([30, 500, 330, 548], fill=(4, 10, 6)); W.rectangle([30, 500, 330, 548], outline=(50, 130, 80))
    s = PI.replace(".", "")
    for j in range(18):
        i = n - 14 + j
        if 0 <= i < len(s): text(W, 38 + j * 16, 502, s[i], size=40, fill=CREAM if j == 14 else (70, 170, 100) if j < 14 else (24, 70, 40))
    panel(c.t, "ENIAC 1949", f"{count} DIGITS", "IN ABOUT 70 HOURS", [CREAM] * 12, style="green", sub_col=GREEN)
    g = (t - 5.45) / 0.75
    if g > 0:
        rng = np.random.default_rng(int(t * 1000))
        a = np.array(c.art); m = rng.random((AH, AW)) < ease(g * 1.4)
        pal = np.array([(40, 90, 110), (60, 130, 120), (30, 60, 100), (100, 160, 120)], np.uint8)
        a[m] = pal[rng.integers(0, 4, m.sum())]; c.art = Image.fromarray(a)
    return c

def sc_outro(t):
    c = Ctx(bg("grid"))
    lines = ["3.14159265", "35897932", "38462643", "38327950", "28841971"]
    for i, l in enumerate(lines):
        q = (t - i * 0.12) / 0.2
        if q > 0: text(c.t, 40, 96 + i * 40, l, size=40, fill=CREAM if i == 0 else mix((40, 50, 80), CREAM, min(1, q) * (1 - i * 0.16)))
    pi_line(c, math.pi)
    if t > 1.2: text(c.t, 180, 520, "...AND IT NEVER ENDS", fill=DIM, align="c")
    return c

SCENEFN = {"intro": sc_intro, "babylon": sc_babylon, "archimedes": sc_arch, "buffon": sc_buffon, "madhava": sc_madhava,
           "galperin": sc_galperin, "eniac": sc_eniac, "outro": sc_outro}
NAMES = [n for n, _ in SC]

def beat_pulse(T):
    """subtle zoom-ish flash on kicks: returns brightness add"""
    return 0

HOPS = None
def panel_hop(T):
    """header panel jumps up on each kick and on every discovered digit, then falls back with a bounce"""
    global HOPS
    if HOPS is None:
        HOPS = np.array(sorted([e[0] for e in EV if e[1] in ("digit", "edigit", "chime")] + KICKS))
    i = np.searchsorted(HOPS, T, side="right") - 1
    if i < 0: return 0
    d = T - HOPS[i]
    return int(round(-7 * FXK * math.exp(-d / 0.08) * abs(math.cos(2 * math.pi * d / 0.2))))

def active_glitch(T):
    for g in GL:
        if g[0] <= T < g[0] + g[1]: return g
    return None

_IDX = {}
def warp(fr, zoom, dx, dy, zy=None):
    zq = zoom; zyq = zy if zy else zoom
    cy, cx = OH / 2 + dy, OW / 2 + dx
    ri = np.clip((np.arange(OH) - OH / 2) / zyq + cy, 0, OH - 1).astype(np.int32)
    ci = np.clip((np.arange(OW) - OW / 2) / zq + cx, 0, OW - 1).astype(np.int32)
    return fr[ri][:, ci]

def intensity(T):
    return 0.35 + 0.65 * ease(T / START["eniac"]) ** 1.3 + 0.6 * ease((T - START["eniac"]) / 5.0)

def fx(fr, T, name, t):
    I = intensity(T) * FXK
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    si = np.searchsorted(SNARES, T, side="right") - 1
    sp = math.exp(-(T - SNARES[si]) / 0.06) if si >= 0 else 0.0
    if name == "outro": I *= 0.25
    push = 1.02 + 0.04 * I * ease(t / DUR[name])          # slow push-in per scene, stronger later
    kd = (T - KICKS[ki]) if ki >= 0 else 9
    spring = math.exp(-kd / 0.11) * math.cos(2 * math.pi * kd / 0.17)   # damped bounce after each kick
    zoom = push + kp * (0.015 + 0.035 * I)
    sd = (T - SNARES[si]) if si >= 0 else 9
    squash = math.exp(-sd / 0.09) * math.cos(2 * math.pi * sd / 0.14)
    zx = zoom * (1 - 0.025 * squash * I); zy = zoom * (1 + 0.05 * squash * I)
    rng = random.Random(int(T * 1000))
    sh = sp * 14 * I
    sway = math.sin(T * 2 * math.pi / (60 / bpm(T)) / 2) * 10 * I            # side-to-side on the half-bar
    dx = rng.uniform(-sh, sh) + sway
    dy = -spring * (34 + 70 * I) + rng.uniform(-sh, sh)                       # vertical punch on every kick
    fr = warp(fr, zx, dx, dy, zy)
    split = int(sp * 14 * I + kp * 4 * I)
    if split > 0:
        out = fr.copy(); out[:, split:, 0] = fr[:, :-split, 0]; out[:, :-split, 2] = fr[:, split:, 2]; fr = out
    fl = kp * (14 + 34 * I)
    if fl > 1: fr = np.minimum(255, fr.astype(np.int16) + int(fl)).astype(np.uint8)
    return fr

def glitch_frame(fr, T, g):
    kind = g[2]; rng = np.random.default_rng(int(T * 997))
    if kind == "crush":
        b = 24
        small = fr[::b, ::b]; fr = np.repeat(np.repeat(small, b, 0), b, 1)[:OH, :OW]
        fr = (fr // 64 * 64 + 32).astype(np.uint8)
    for _ in range(5):
        y = rng.integers(0, OH - 120); h = rng.integers(20, 120)
        fr[y:y + h] = np.roll(fr[y:y + h], rng.integers(-160, 160), axis=1)
    if kind == "stutter" and rng.random() < 0.5: fr = fr[:, :, ::-1].copy()
    if kind == "tapestop":
        p = (T - g[0]) / g[1]
        fr = (fr * (1 - 0.6 * p)).astype(np.uint8)
    return fr

def strobe(fr, T):
    E = START["eniac"]
    if FXK >= 0.8 and E + 4.4 < T < E + 4.95:
        bl = 60 / bpm(T); k = int((T - E) / (bl / 4))
        if k % 2: fr = 255 - fr
    return fr

def render_frame(idx, t):
    name = NAMES[idx]
    T = START[name] + t
    g = active_glitch(T)
    if g and g[2] == "stutter":   # freeze-repeat the slice like the audio
        T2 = g[0] + ((T - g[0]) % g[3]); t = T2 - START[name]
        if t < 0: name = NAMES[idx - 1]; idx -= 1; t = T2 - START[name]
    if g and g[2] == "tapestop":
        p = (T - g[0]) / g[1]; T2 = g[0] + g[1] * (p - p * p / 2); t = T2 - START[name]
    c = SCENEFN[name](t)
    hop = panel_hop(START[name] + t)
    if hop:
        band = c.txt.crop((0, 60, TW, 162)); c.t.rectangle([0, 60, TW, 162], fill=(0, 0, 0, 0))
        c.txt.alpha_composite(band, (0, 60 + hop))
    fr = v2.compose(c, t, idx)
    fr = fx(fr, T, NAMES[NAMES.index(name)], t)
    fr = strobe(fr, T)
    if g: fr = glitch_frame(fr, T, g)
    if NAMES[idx] == "outro":
        f = ease((t - (DUR[name] - 1.0)) / 1.0)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx}_{name}.tmp.mp4", f"{out}/{idx}_{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))): p.stdin.write(render_frame(idx, f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((360, 640), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    elif mode == "info":
        from collections import Counter
        print(TOTAL, Counter(k for _, k, _ in EV))
        for r in SCH["runs"]: print("run", r["d"], len(r["sim"]) - 1, r["k"])
        print("needles", len(SCH["needles"]), "terms", len(SCH["terms"]), "eniac", len(SCH["eniac"]))
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(2) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
