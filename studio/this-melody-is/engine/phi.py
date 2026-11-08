"""THIS MELODY IS PHI — event-driven pixel short (same engine as pi.py). Every visual event is also a sound event."""
import sys, os, math, random, subprocess, cmath
from math import isqrt
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, CREAM, YEL, RED, DIM, GREEN, GREEN_HI, text, panel, ease, eout, mix, shade,
                pix_arc, pix_line, lerp, bg, noise)
import pi as PIM
from pi import Ctx, mkbg, upto, last_change, warp, glitch_frame

FXK = float(os.environ.get("PI_FX", "1"))
FINAL = "laptop"

v2._GL["√"] = ["....###", "....#..", "....#..", "...#...", "...#...", "#..#...", ".#.#...", ".##....", "..#...."]
v2._GL_Y["√"] = 5

# ---------- digits of phi ----------
_n = 3000
_s = str((10 ** _n + isqrt(5 * 10 ** (2 * _n))) // 2)
PHI = _s[0] + "." + _s[1:]
PHD = [int(c) for c in PHI if c.isdigit()]
v2.PHI = PHI; v2.DIGITS = PHD

def correct_mask(s):
    out, ok = [], True
    for i, ch in enumerate(s):
        ok = ok and i < len(PHI) and PHI[i] == ch
        out.append(ok)
    return out
def cols_for(s): return [CREAM if ok else RED for ok in correct_mask(s)]

# ---------- timeline ----------
SC = [("intro", 4.0), ("pentagram", 6.4), ("euclid", 6.6), ("rabbits", 8.2), ("kepler", 6.8), ("hurwitz", 7.0),
      ("hp35", 7.6), ("penrose", 8.6), ("vogel", 9.2), ("laptop", 6.2), ("outro", 4.6)]
START, acc = {}, 0.0
for n, d in SC: START[n] = acc; acc += d
TOTAL = acc
DUR = dict(SC)
NAMES = [n for n, _ in SC]

def bpm(t):
    return 140 + 52 * ease(t / START[FINAL]) + 40 * ease((t - START[FINAL]) / 5.2)
def beat_times(T):
    out, t = [], 0.0
    while t < T: out.append(t); t += 60 / bpm(t)
    return out
_G = None
def grid16(t_from, n, every=1):
    global _G
    if _G is None:
        _G = []
        for b in beat_times(TOTAL + 2):
            bl = 60 / bpm(b); _G += [b + k * bl / 4 for k in range(4)]
    g = [x for x in _G if x >= t_from - 1e-6]
    return g[::every][:n]

EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def type_events(s, t_start, every, tag):
    ok = correct_mask(s); gt = grid16(t_start, len(s), every); times = []
    for i, ch in enumerate(s):
        times.append(gt[i])
        if ch.isdigit(): ev(gt[i], "digit", d=int(ch), ok=ok[i], tag=tag)
    return times
def thin(times, maxrate):
    """keep at most maxrate sound events per second"""
    out, last = [], -1
    for t in times:
        if t - last >= 1 / maxrate: out.append(t); last = t
    return out

SCH = {}

# ---- pentagram geometry ----
PC, PR = (90, 196), 72
def pent(c, r, rot):
    return [(c[0] + r * math.cos(rot + 2 * math.pi * i / 5), c[1] + r * math.sin(rot + 2 * math.pi * i / 5)) for i in range(5)]
def pent_lines():
    lines = []
    V = pent(PC, PR, -math.pi / 2)
    lines.append([(V[i], V[(i + 1) % 5]) for i in range(5)])          # level -1: pentagon
    r, rot = PR, -math.pi / 2
    for lvl in range(5):
        V = pent(PC, r, rot)
        lines.append([(V[i], V[(i + 2) % 5]) for i in range(5)] + ([] if lvl == 0 else []))
        r, rot = r / 1.6180339887 ** 2, rot + math.pi / 5
        if lvl < 4:
            V2 = pent(PC, r, rot); lines.append([(V2[i], V2[(i + 1) % 5]) for i in range(5)])
    return lines
PLINES = pent_lines()

# ---- penrose ----
GR = (1 + 5 ** 0.5) / 2
def penrose_levels(n, c=complex(90, 196), R=118):
    tris = []
    for i in range(10):
        B = c + R * cmath.rect(1, (2 * i - 1) * math.pi / 10); C = c + R * cmath.rect(1, (2 * i + 1) * math.pi / 10)
        if i % 2 == 0: B, C = C, B
        tris.append((0, c, B, C))
    levels = [tris]
    for _ in range(n):
        res = []
        for col, A, B, C in tris:
            if col == 0:
                P = A + (B - A) / GR; res += [(0, C, P, B), (1, P, C, A)]
            else:
                Q = B + (A - B) / GR; Rr = B + (C - B) / GR; res += [(1, Rr, C, A), (1, Q, Rr, B), (0, Rr, Q, A)]
        tris = res
        # sort for a radial sweep reveal
        levels.append(sorted(tris, key=lambda t: (cmath.phase((t[1] + t[2] + t[3]) / 3 - c) + math.pi)))
    return levels
PEN = penrose_levels(6)

def build():
    # INTRO
    SCH["intro"] = type_events("1.6180339887498948", START["intro"] + 0.15, 2, "intro")
    ev(START["pentagram"] - 0.5, "riser")
    # PENTAGRAM: lines accelerate, each star level reveals one more digit
    st = START["pentagram"]; t = st + 0.2; SCH["plines"] = []
    dts = [0.17, 0.15, 0.1, 0.08, 0.06, 0.05, 0.04, 0.035, 0.03, 0.025]
    for li, group in enumerate(PLINES):
        dt = dts[min(li, len(dts) - 1)]
        for j, ln in enumerate(group):
            SCH["plines"].append((t, li, j)); ev(t, "pen", lvl=li, j=j); t += dt
        SCH.setdefault("plevel_done", []).append(t)
    reveal = ["1.6", "1.61", "1.618", "1.6180", "1.61803", "1.618033"]
    SCH["pvals"] = []
    stars = [i for i in range(len(PLINES)) if i % 2 == 1]
    for k, li in enumerate(stars):
        if k < len(reveal):
            tt = SCH["plevel_done"][li]; SCH["pvals"].append((tt, reveal[k])); ev(tt, "digit", d=int(reveal[k][-1]), ok=True, tag="pent")
    tt = SCH["plevel_done"][-1] + 0.1
    SCH["ptype"] = type_events("1.61803398", tt, 1, "pent2")
    # EUCLID (timeline mirrors v2.sc_euclid)
    st = START["euclid"]
    for k in range(4): ev(st + 0.2 + k * 0.4, "pen", lvl=0, j=k)
    ev(st + 1.9, "chime", lvl=0)
    for k in range(8): ev(st + 2.5 + k * 0.17, "scrape", i=k)
    ev(st + 4.0, "thud", v=0.5); ev(st + 4.9, "chime", lvl=1)
    SCH["eu_type"] = type_events("1.6", st + 4.9, 1, "eu")
    SCH["eu_rec"] = []
    t = st + 5.1
    for k in range(9):
        SCH["eu_rec"].append(t); ev(t, "pen", lvl=2 + k, j=k); t += 0.32 * 0.8 ** k
    # RABBITS: months accelerate
    st = START["rabbits"]; F = [1, 1]
    while len(F) < 13: F.append(F[-1] + F[-2])
    t = st + 0.3; SCH["months"] = []; SCH["births"] = []
    for m in range(12):
        dur = 0.95 * 0.84 ** m
        newp = F[m] - (F[m - 1] if m else 0)
        SCH["months"].append((t, F[m]))
        bt = [t + dur * 0.8 * (i + 1) / max(1, newp) for i in range(newp)]
        for i, x in enumerate(bt): SCH["births"].append(x)
        for x in thin(bt, 160): ev(x, "pop", m=m)
        if m >= 1: ev(t + dur * 0.85, "digit", d=PHD[min(m, 12)], ok=True, tag="rab") if False else None
        t += dur
    SCH["rab_end"] = t
    # KEPLER tiles (mirrors v2 layout timing)
    st = START["kepler"]; step, t0 = 0.5, 0.25
    SCH["k_tiles"] = [st + t0 + i * step * 0.92 ** i for i in range(8)]
    for i, x in enumerate(SCH["k_tiles"]): ev(x + 0.25, "thud", v=0.25 + 0.04 * i)
    seq = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584]
    vt = [SCH["k_tiles"][i] + 0.3 for i in range(1, 8)]
    t = vt[-1]
    for k in range(8, len(seq)): t += 0.32 * 0.88 ** (k - 8); vt.append(t)
    SCH["k_vals"] = list(zip(vt, range(1, len(seq))))
    for x, k in SCH["k_vals"]: ev(x, "chime", lvl=min(5, k // 3))
    SCH["k_seq"] = seq
    # HURWITZ: chalk levels, then convergents accelerating
    st = START["hurwitz"]
    SCH["h_lv"] = [st + 0.3 + k * 0.42 for k in range(6)]
    for x in SCH["h_lv"]: ev(x, "chalk")
    pts, t = [], st + 0.5
    for i in range(24): pts.append(t); t += 0.36 * 0.9 ** i
    SCH["h_pts"] = pts
    for i, x in enumerate(pts): ev(x, "term", k=i, rate=1 / (0.36 * 0.9 ** i))
    # HP-35: 1 + sqrt loops
    st = START["hp35"]; t = st + 0.35; x = 1.0; SCH["keys"] = []; k = 0
    for it in range(26):
        for key in ("1", "+", "√X"):
            dtk = max(0.03, 0.26 * 0.955 ** k)
            if key == "1": disp = "1."
            elif key == "+": disp = f"{1 + x:.8f}"
            else: x = math.sqrt(1 + x); disp = f"{x:.8f}"
            SCH["keys"].append((t, key, disp, it + 1, x))
            ev(t, "key", key=key, rate=1 / dtk)
            if key == "√X":
                v = f"{x:.8f}"; ok = correct_mask(v); n_ok = sum(ok)
                ev(t + 0.005, "digit", d=int(v[min(len(v) - 1, max(2, n_ok))]), ok=n_ok >= len(v), tag="hp")
            t += dtk; k += 1
    # PENROSE: radial sweeps per subdivision level
    st = START["penrose"]; t = st + 0.3; SCH["pen_lv"] = []
    for L, tris in enumerate(PEN):
        d = [0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0][L]
        SCH["pen_lv"].append((t, d))
        n = len(tris)
        tt = [t + d * (i + 1) / n for i in range(n)]
        for x in thin(tt, 240): ev(x, "tri", col=tris[min(n - 1, int((x - t) / d * n))][0])
        ev(t + d + 0.02, "chime", lvl=min(5, L))
        t += d + 0.15
    # VOGEL: seeds accelerate within each phase
    st = START["vogel"]
    phases = [(0.0, 135.0, 300, 1.8), (2.3, 137.0, 300, 1.8), (4.6, 360 / GR ** 2, 620, 2.9)]
    SCH["v_ph"] = phases
    for p0, ang, N, dg in phases:
        tt = [st + p0 + dg * math.sqrt((k + 1) / N) for k in range(N)]
        for x in thin(tt, 220):
            k = int(((x - st - p0) / dg) ** 2 * N)
            ev(x, "seed", k=k, good=abs(ang - 137.5) < 0.1)
        ev(st + p0, "whoosh")
    # LAPTOP finale
    st = START[FINAL]; t, i = st + 0.3, 0; SCH["stream"] = []
    while t < st + 4.9:
        r = 10 * (12 ** ((t - st) / 4.9)); SCH["stream"].append((t, i)); ev(t, "edigit", d=PHD[i], rate=r); t += 1 / r; i += 1
    ev(st + 5.45, "glitch")
    ev(START["outro"], "final")
    drums_and_glitches()

CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
KICKS, SNARES, GL = [], [], []
def scene_at(t):
    for n, d in SC:
        if START[n] <= t < START[n] + d: return n
    return "outro"
def drums_and_glitches():
    E = START[FINAL]
    for bi, bt in enumerate(beat_times(TOTAL)):
        if bt >= START["outro"] - 0.05: break
        sc = scene_at(bt); bl = 60 / bpm(bt); pos = bi % 4
        ch = CHORDS[(bi // 4) % 4]; root = ch[0] - 12
        quiet = sc in ("hurwitz",)
        light = sc in ("intro", "pentagram")
        fin = sc == FINAL and bt > E + 3.4
        if sc != "intro":
            if quiet:
                if pos == 0: ev(bt, "kick", v=0.42)
            else:
                ev(bt, "kick", v=0.38 if light else 0.5)
                if fin or (sc == FINAL and bt > E + 2.0) or (sc in ("penrose", "vogel") and pos == 3): ev(bt + bl / 2, "kick", v=0.34)
            if not light and not quiet and pos in (1, 3) and not fin: ev(bt, "snare", v=0.22)
            if fin:
                div = 4 if bt < E + 4.4 else 8
                for h in range(div): ev(bt + h * bl / div, "snare", v=0.08 + 0.14 * (h + 1) / div)
        if not quiet or pos % 2 == 0:
            sub = 4 if sc in ("rabbits", "hp35", "penrose", "vogel", FINAL) else 2
            for h in range(sub):
                if sc == "intro" and h % 2: continue
                ev(bt + h * bl / sub, "hat", v=0.045 if h % 2 else 0.06, open=(h == sub // 2 and sc != "intro"))
        for h in range(2):
            if sc == "intro" and h == 1: continue
            m = root + (12 if (pos * 2 + h) % 4 == 3 else 0) + (int(3 * ease((bt - E - 3.4) / 1.6)) * 2 if fin else 0)
            ev(bt + h * bl / 2, "bass", m=m, d=bl / 2 * 0.9, v=0.22 if sc != "intro" else 0.16)
        if pos == 0 and sc in ("hurwitz", "pentagram", "euclid"): ev(bt, "pad", ch=ch, d=bl * 4)
    for t, k, kw in EV:
        if k == "kick": KICKS.append(t)
        if k == "snare" and kw["v"] > 0.15: SNARES.append(t)
    KICKS.sort(); SNARES.sort()
    def bl_at(t): return 60 / bpm(t)
    for n_, kind, div in (("euclid", "stutter", 4), ("rabbits", "stutter", 8), ("kepler", "stutter", 4), ("hp35", "stutter", 8),
                          ("penrose", "stutter", 4), ("vogel", "stutter", 8), (FINAL, "stutter", 8)):
        d = 0.22 if div == 4 else 0.26
        GL.append((START[n_] - d, d, kind, bl_at(START[n_]) / div))
    GL.append((START["rabbits"] + 4.2, 0.2, "crush", 0))
    GL.append((START["penrose"] + 5.0, 0.22, "crush", 0))
    GL.append((E + 2.2, 0.18, "stutter", bl_at(E + 2.2) / 4))
    GL.append((E + 3.2, 0.22, "crush", 0))
    GL.append((E + 3.9, 0.2, "stutter", bl_at(E + 3.9) / 8))
    GL.append((E + 4.45, 0.15, "stutter", bl_at(E + 4.45) / 16))
    GL.append((E + 4.95, 0.5, "tapestop", 0))
    GL.sort()

build()
EV.sort(key=lambda e: e[0])

# ================= visuals =================
def typed(s, times, T):
    n = upto(times, T); v = s[:n]; return v, cols_for(v)

def num_line(c, pos):
    y, x0, u = 200, 30, 60
    c.a.line([16, y, 164, y], fill=(80, 150, 190)); c.a.line([16, y + 1, 164, y + 1], fill=(30, 50, 80))
    for k in range(3):
        c.a.line([x0 + k * u, y - 2, x0 + k * u, y + 2], fill=CREAM); text(c.t, (x0 + k * u) * 2 - 4, y * 2 + 8, str(k), fill=DIM)
    x = x0 + pos * u
    if pos > 0: c.a.line([x0, y, x, y], fill=YEL); c.a.line([x0, y - 1, x, y - 1], fill=(170, 130, 40))
    # golden rectangle riding the line, growing with pos
    w = max(2, pos * 26); h = w / GR
    c.a.rectangle([x - w, y - 2 - h, x, y - 2], outline=YEL)
    if w > 8: c.a.line([x - w + h, y - 2 - h, x - w + h, y - 2], fill=(170, 130, 40))
    if pos > 1.6:
        X = int(x * 2); c.t.rectangle([X - 7, y * 2 + 30, X + 7, y * 2 + 46], fill=YEL); text(c.t, X - 3, y * 2 + 28, "φ", fill=(30, 20, 10))

def sc_intro(t):
    c = Ctx(bg("grid")); T = START["intro"] + t
    c.t.rectangle([30, 76, 252, 158], fill=(6, 7, 12))
    text(c.t, 40, 74, "THIS MELODY", size=40); text(c.t, 40, 112, "IS φ", size=40)
    s = "1.6180339887498948"; v = s[:upto(SCH["intro"], T)]
    text(c.t, 40, 226, v[:10], size=40)
    if len(v) > 10: text(c.t, 40, 264, v[10:], size=40)
    num_line(c, GR * eout((t - 0.15) / 3.2))
    return c

def pottery_bg():
    if "pottery" in PIM._B: return PIM._B["pottery"]
    a = np.zeros((AH, AW, 3), np.float32); a[:] = (196, 96, 48)
    a *= (0.92 + 0.12 * noise((AH, AW), 41, 6))[..., None]
    a *= (0.97 + 0.04 * noise((AH, AW), 42))[..., None]
    for y0 in (86, 296):
        a[y0:y0 + 14] = (30, 18, 12)
        for x in range(0, AW, 12):   # greek key (meander) in terracotta on black
            col = np.array((196, 96, 48)) * 0.95
            a[y0 + 2, x:x + 9] = col; a[y0 + 2:y0 + 10, x + 8] = col; a[y0 + 9, x + 2:x + 9] = col
            a[y0 + 5:y0 + 10, x + 2] = col; a[y0 + 5, x + 2:x + 6] = col; a[y0 + 5:y0 + 8, x + 5] = col
            a[y0 + 11, x:x + 12] = col
    PIM._B["pottery"] = np.clip(a, 0, 255).astype(np.uint8); return PIM._B["pottery"]

def sc_pentagram(t):
    c = Ctx(pottery_bg()); T = START["pentagram"] + t
    ink, sh = (24, 14, 10), (130, 50, 24)
    done_lines = [(x, li, j) for (x, li, j) in SCH["plines"] if x <= T]
    for x, li, j in SCH["plines"]:
        if x > T + 0.2: break
        q = ease((T - x) / 0.12)
        if q <= 0: continue
        a, b = PLINES[li][j]
        pix_line(c.a, (a[0], a[1] + 1), (b[0], b[1] + 1), sh, q); pix_line(c.a, a, b, ink, q)
    # fill innermost done star center with gold
    nst = sum(1 for x in SCH["plevel_done"] if x <= T)
    if nst >= 2:
        r = PR / GR ** 2 * 0.98
        c.a.polygon(pent(PC, r, -math.pi / 2 + math.pi / 5), fill=(220, 170, 70)) if nst == 2 else None
    vals = [v for (x, v) in SCH["pvals"] if x <= T]
    ty = SCH["ptype"]
    if T >= ty[0]: v, cols = typed("1.61803398", ty, T); v = v if len(v) > len(vals[-1]) else vals[-1]; cols = cols_for(v)
    elif vals: v = vals[-1]; cols = cols_for(v)
    else: v, cols = "-", [DIM]
    stars = (nst + 1) // 2
    ages = [x for (x, _) in SCH["pvals"] if x <= T] + [x for x in ty if x <= T]
    panel(c.t, "PYTHAGOREANS ~500 BC", v, "DIAGONAL / SIDE", cols, right=["STARS", str(stars)], age=(T - max(ages)) if ages else None)
    return c

def sc_euclid(t):
    # reuse v2 construction, faster recursion driven by our event times
    c = v2.sc_euclid(t, DUR["euclid"])
    cc = Ctx.__new__(Ctx); cc.art, cc.txt = c.art, Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    cc.a = ImageDraw.Draw(cc.art); cc.t = ImageDraw.Draw(cc.txt); cc.t.fontmode = "1"
    T = START["euclid"] + t
    # extra recursion lines past v2's 5 levels (inside the last small rectangle)
    x0, y0, s = v2.EU["x0"], v2.EU["y0"], v2.EU["s"]
    xe = x0 + s / 2 + math.hypot(s / 2, s)
    rx0, ry0, rx1, ry1 = x0 + s, y0, xe, y0 + s
    ink = (52, 34, 22)
    for k, x in enumerate(SCH["eu_rec"]):
        if T < x: break
        q = ease((T - x) / 0.15); w, h = rx1 - rx0, ry1 - ry0; dr = "dlur"[k % 4]
        if dr == "d": sq = w; pix_line(cc.a, (rx0, ry0 + sq), (rx1, ry0 + sq), ink, q); ry0 += sq
        elif dr == "l": sq = h; pix_line(cc.a, (rx1 - sq, ry0), (rx1 - sq, ry1), ink, q); rx1 -= sq
        elif dr == "u": sq = w; pix_line(cc.a, (rx0, ry1 - sq), (rx1, ry1 - sq), ink, q); ry1 -= sq
        else: sq = h; pix_line(cc.a, (rx0 + sq, ry0), (rx0 + sq, ry1), ink, q); rx0 += sq
    # copy v2's text layer (labels) but redraw header with our typed value
    tx = c.txt.copy(); d = ImageDraw.Draw(tx); d.rectangle([0, 60, TW, 162], fill=(0, 0, 0, 0)); cc.txt = tx; cc.t = d; d.fontmode = "1"
    v, cols = typed("1.6", SCH["eu_type"], T)
    panel(cc.t, "EUCLID ≈300 BC", v or "?", "EXTREME AND MEAN RATIO", cols or [DIM], right=["ELEMENTS", "II.11"], age=last_change(SCH["eu_type"], T))
    return cc

def rabbit(d, x, y, adult, hop=0, white=True):
    y -= hop
    body = (240, 236, 228) if white else (178, 128, 84)
    dark, lite = shade(body, 0.7), mix(body, (255, 255, 255), 0.4)
    k = 1 if adult else 0
    if adult:
        d.rectangle([x, y + 3, x + 5, y + 6], fill=body)                  # body
        d.rectangle([x + 4, y + 1, x + 7, y + 4], fill=body)              # head
        d.line([x + 5, y - 2, x + 5, y], fill=body); d.line([x + 6, y - 2, x + 6, y], fill=lite)   # ears
        d.point((x + 6, y + 2), fill=(40, 20, 20)); d.point((x + 7, y + 3), fill=(220, 120, 140))
        d.line([x, y + 6, x + 5, y + 6], fill=dark); d.point((x - 1, y + 3), fill=(255, 255, 255))
        d.point((x + 1, y + 7), fill=dark); d.point((x + 4, y + 7), fill=dark)
    else:
        d.rectangle([x + 1, y + 4, x + 4, y + 6], fill=body); d.rectangle([x + 3, y + 3, x + 5, y + 5], fill=body)
        d.point((x + 4, y + 2), fill=body); d.point((x + 4, y + 4), fill=(40, 20, 20))

def meadow_bg():
    if "meadow" in PIM._B: return PIM._B["meadow"]
    a = bg("garden").astype(np.float32).copy()
    a[150:] = (84, 150, 66)
    rng = np.random.default_rng(5)
    for _ in range(1400):
        x, y = rng.integers(0, AW), rng.integers(150, AH)
        a[y:y + rng.integers(1, 3), x] = rng.choice([(64, 124, 52), (110, 176, 80), (130, 196, 96)])
    for x in range(4, AW, 14):   # fence
        a[140:160, x:x + 2] = (150, 106, 64); a[140, x:x + 2] = (190, 150, 100)
    a[144:146, :] = (160, 116, 72); a[152:154, :] = (160, 116, 72)
    PIM._B["meadow"] = np.clip(a, 0, 255).astype(np.uint8); return PIM._B["meadow"]

def sc_rabbits(t):
    c = Ctx(meadow_bg()); T = START["rabbits"] + t
    months = SCH["months"]; m = upto([x for x, _ in months], T) - 1
    nb = upto(SCH["births"], T)
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kd = T - KICKS[ki] if ki >= 0 else 9
    # pair i born at SCH["births"][i]; pair is adult if born before current month start
    mstart = months[m][0] if m >= 0 else 0
    for i in range(nb):
        col, row = i % 12, i // 12
        x, y = 8 + col * 14, 166 + row * 12
        born = SCH["births"][i]; age = T - born
        adult = born < mstart - 1e-6
        hop = int(3 * math.exp(-age / 0.08)) + (int(2 * math.exp(-kd / 0.08)) if (i + int(T * 2)) % 3 == 0 else 0)
        rabbit(c.a, int(x), int(y), adult, hop, white=(i % 3 != 2))
        if age < 0.06: c.a.line([x + 2, y - 4, x + 6, y - 4], fill=(255, 255, 200)); c.a.line([x + 4, y - 6, x + 4, y - 2], fill=(255, 255, 200))
    if m >= 1:
        F = [p for _, p in months]; val = f"{F[m] / F[m - 1]:.5f}"
        panel(c.t, "FIBONACCI 1202", val, f"{F[m]} / {F[m-1]} PAIRS", cols_for(val), right=["MONTH", str(m + 1)], age=T - months[m][0])
    else:
        panel(c.t, "FIBONACCI 1202", "-", "RABBIT PAIRS", [DIM], right=["MONTH", str(m + 1)])
    return c

def sc_kepler(t):
    T = START["kepler"] + t
    c = Ctx(bg("wood")); U = 4; FB = v2.FBOX
    bw, bh = (FB[2] - FB[0]) * U, (FB[3] - FB[1]) * U
    ox, oy = (AW - bw) // 2 - FB[0] * U, 196 - bh // 2 - FB[1] * U
    c.a.rectangle([ox + FB[0] * U - 4, oy + FB[1] * U - 4, ox + FB[2] * U + 4, oy + FB[3] * U + 4], fill=(74, 44, 26), outline=(176, 120, 72))
    for r in v2.FSQ:
        c.a.rectangle([ox + r[0] * U, oy + r[1] * U, ox + r[2] * U - 1, oy + r[3] * U - 1], outline=(92, 58, 34))
    landed = 0
    for i, r in enumerate(v2.FSQ):
        ti = SCH["k_tiles"][i]
        if T < ti: break
        q = (T - ti) / 0.25; fall = (1 - v2.bounce(q)) * 70
        x0, y0, x1, y1 = ox + r[0] * U, oy + r[1] * U, ox + r[2] * U - 1, oy + r[3] * U - 1
        v2.tile(c.a, x0, y0 - fall, x1, y1 - fall, v2.TILE_COLS[i], i)
        if q >= 1:
            landed = i + 1
            if v2.FIB[i] >= 3: text(c.t, (x0 + x1) + 1 - 4 * len(str(v2.FIB[i])), (y0 + y1) - 10, str(v2.FIB[i]), fill=shade(v2.TILE_COLS[i], 0.45))
    for i in range(landed):
        q = ease((T - SCH["k_tiles"][i] - 0.25) / 0.3)
        if q <= 0: continue
        cen, a, b = v2.FARC[i]; rr = v2.FIB[i] * U; cx, cy = ox + cen[0] * U, oy + cen[1] * U
        aa = math.atan2(a[1] - cen[1], a[0] - cen[0]); ab = math.atan2(b[1] - cen[1], b[0] - cen[0])
        diff = (ab - aa + 3 * math.pi) % (2 * math.pi) - math.pi
        pix_arc(c.a, cx - 0.5, cy - 0.5, rr, aa, aa + diff, (252, 214, 110), q, shadow=(70, 40, 18))
    kv = [(x, k) for x, k in SCH["k_vals"] if x <= T]
    seq = SCH["k_seq"]
    if kv:
        x, k = kv[-1]; val = f"{seq[k + 1] / seq[k]:.6f}" if k + 1 < len(seq) else f"{seq[k] / seq[k - 1]:.6f}"
        val = f"{seq[k] / seq[k - 1]:.6f}"
        panel(c.t, "KEPLER 1611", val, f"{seq[k]} / {seq[k-1]}", cols_for(val), right=["F(N+1)", "/ F(N)"], age=T - x)
    else:
        panel(c.t, "KEPLER 1611", "-", "F(N+1) / F(N)", [DIM], right=["F(N+1)", "/ F(N)"])
    return c

def sc_hurwitz(t):
    T = START["hurwitz"] + t
    c = Ctx(bg("chalk")); W = c.t; chalk = (232, 236, 226)
    nlv = upto(SCH["h_lv"], T)
    x1 = 44 + 5 * 30 + 60
    for k in range(min(5, nlv)):
        x, y = 44 + k * 30, 184 + k * 28
        q = ease((T - SCH["h_lv"][k]) / 0.25)
        text(W, x, y + 10, "1 +", fill=chalk)
        W.rectangle([x + 30, y + 21, x + 30 + int((x1 - x - 30) * q), y + 22], fill=chalk)
        if q > 0.6: text(W, x + 30 + (x1 - x - 30) / 2 - 4, y + 2, "1", fill=chalk)
    if nlv >= 6: text(W, 44 + 5 * 30, 184 + 5 * 28 + 10, "1 + ...", fill=chalk)
    F = [1, 1]
    while len(F) < 30: F.append(F[-1] + F[-2])
    conv = [F[i + 1] / F[i] for i in range(25)]
    gx0, gy, gs = 22, 246, 34
    for x in range(14, 166, 4): c.a.line([x, gy, x + 1, gy], fill=(220, 120, 110))
    text(W, 336, gy * 2 - 10, "φ", fill=(220, 120, 110), align="r")
    np_ = upto(SCH["h_pts"], T)
    pts = [(gx0 + i * 6.0, gy - max(-1, min(1, (conv[i] - GR) * 2.2)) * gs) for i in range(np_)]
    for i in range(1, len(pts)): c.a.line([pts[i - 1], pts[i]], fill=(214, 218, 206))
    for p in pts: c.a.rectangle([p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1], fill=(250, 250, 240))
    if t > 4: text(W, 180, 560, "SLOWEST CONVERGENCE OF ALL", fill=(200, 210, 196), align="c")
    c.txt = v2.chalkify(c.txt, (30, 170, 340, 600), int(t * 4)); c.t = ImageDraw.Draw(c.txt); c.t.fontmode = "1"
    if np_:
        val = f"{conv[np_ - 1]:.8f}"
        panel(c.t, "HURWITZ 1891", val, "THE MOST IRRATIONAL NUMBER", cols_for(val), right=["ALL ONES", f"{np_} TERMS"],
              age=T - SCH["h_pts"][np_ - 1], style="dark")
    else:
        panel(c.t, "HURWITZ 1891", "-", "THE MOST IRRATIONAL NUMBER", [DIM], right=["ALL ONES", "0 TERMS"], style="dark")
    return c

KEYS = [["X^Y", "LOG", "LN", "E^X", "CLR"], ["√X", "ARC", "SIN", "COS", "TAN"], ["ENT", "", "CHS", "EEX", "CLX"],
        ["-", "7", "8", "9", ""], ["+", "4", "5", "6", ""], ["×", "1", "2", "3", ""]]
def sc_hp35(t):
    c = Ctx(bg("desk")); T = START["hp35"] + t; d = c.a
    x0, y0, x1, y1 = 28, 92, 152, 300
    d.rounded_rectangle([x0 + 4, y0 + 4, x1 + 4, y1 + 4], 6, fill=(20, 12, 8))
    d.rounded_rectangle([x0, y0, x1, y1], 6, fill=(52, 50, 52), outline=(20, 20, 22))
    d.line([x0 + 4, y0 + 1, x1 - 4, y0 + 1], fill=(96, 94, 96))
    d.rectangle([x0 + 8, y0 + 8, x1 - 8, y0 + 34], fill=(16, 8, 8), outline=(90, 88, 90))
    d.rectangle([x0 + 4, y0 + 40, x1 - 4, y1 - 6], fill=(150, 140, 120))
    d.rectangle([x0 + 5, y0 + 41, x1 - 5, y1 - 7], fill=(40, 38, 40))
    ks = [k for k in SCH["keys"] if k[0] <= T]
    cur = ks[-1] if ks else None
    pressed = cur[1] if cur and T - cur[0] < 0.07 else None
    W = c.t
    for r, row in enumerate(KEYS):
        for k, lab in enumerate(row):
            kx, ky = x0 + 9 + k * 22, y0 + 50 + r * 25
            num = lab.isdigit() or lab in ("+", "-", "×")
            base = (210, 204, 192) if num else ((70, 110, 180) if lab == "ENT" else (70, 64, 60))
            if lab == "√X": base = (200, 120, 50)
            pr = lab == pressed and lab != ""
            dy = 1 if pr else 0
            d.rectangle([kx, ky + 2, kx + 17, ky + 15], fill=shade(base, 0.5))
            d.rectangle([kx, ky + dy, kx + 17, ky + 13 + dy], fill=shade(base, 1.15) if pr else base)
            d.line([kx + 1, ky + dy, kx + 16, ky + dy], fill=shade(base, 1.3))
            if lab: text(W, (kx + 9) * 2, (ky + dy) * 2 + 4, lab, fill=(30, 26, 22) if num else CREAM, align="c")
    disp = cur[2] if cur else "0."
    led = (255, 64, 40)
    text(W, (x1 - 10) * 2, (y0 + 8) * 2 + 6, disp, size=40, fill=led, align="r")
    if cur:
        x = cur[4]; val = f"{x:.8f}"
        sq = [k for k in ks if k[1] == "√X"]
        if sq:
            val = f"{sq[-1][4]:.8f}"
            panel(c.t, "HP-35 1972", val, "√(1+√(1+√(1+...)))", cols_for(val), right=["LOOPS", str(sq[-1][3])], age=T - sq[-1][0])
        else:
            panel(c.t, "HP-35 1972", "1", "√(1+√(1+√(1+...)))", [CREAM], right=["LOOPS", "0"])
    else:
        panel(c.t, "HP-35 1972", "-", "√(1+√(1+√(1+...)))", [DIM], right=["LOOPS", "0"])
    return c

def tri_draw(d, tr, outline=True):
    col, A, B, C = tr
    fill = (232, 178, 66) if col else (58, 148, 160)
    pts = [(A.real, A.imag), (B.real, B.imag), (C.real, C.imag)]
    d.polygon(pts, fill=fill)
    if outline: d.line([pts[2], pts[0], pts[1]], fill=(26, 24, 34))

def sc_penrose(t):
    c = Ctx(bg("grid")); T = START["penrose"] + t
    lv = [(i, a, d) for i, (a, d) in enumerate(SCH["pen_lv"]) if a <= T]
    if lv:
        L, a, dd = lv[-1]
        if L > 0:
            for tr in PEN[L - 1]: tri_draw(c.a, tr)
        n = len(PEN[L]); k = int(n * min(1, (T - a) / dd))
        for tr in PEN[L][:k]: tri_draw(c.a, tr, outline=L < 6)
        if L == 6 and k == n:
            pass
        done = [i for i, (a2, d2) in enumerate(SCH["pen_lv"]) if a2 + d2 <= T]
        if done:
            D = done[-1]; t1 = sum(1 for tr in PEN[D] if tr[0] == 1); t0 = len(PEN[D]) - t1
            val = f"{t1 / t0:.5f}" if t1 else "-"
            panel(c.t, "PENROSE 1974", val, "THICK / THIN TILES", cols_for(val) if t1 else [DIM], right=["TILES", str(len(PEN[D]) // 2)],
                  age=T - (SCH["pen_lv"][D][0] + SCH["pen_lv"][D][1]))
        else:
            panel(c.t, "PENROSE 1974", "-", "THICK / THIN TILES", [DIM], right=["TILES", "0"])
    else:
        panel(c.t, "PENROSE 1974", "-", "THICK / THIN TILES", [DIM], right=["TILES", "0"])
    return c

def sunflower(c, t, ang_deg, n, nmax):
    cx, cy = 90, 176; d = c.a; sway = t * 1.3
    for y in range(cy + 30, AH):
        xo = int(2 * math.sin((y - cy) / 40 + sway))
        d.line([cx - 2 + xo, y, cx + 2 + xo, y], fill=(64, 120, 48)); d.point((cx - 2 + xo, y), fill=(40, 84, 30)); d.point((cx + 2 + xo, y), fill=(120, 180, 80))
    for sgn, ly in ((-1, 262), (1, 286)):
        pts = [(cx, ly), (cx + sgn * 16, ly - 10), (cx + sgn * 34, ly - 6), (cx + sgn * 20, ly + 4)]
        d.polygon(pts, fill=(76, 140, 56), outline=(40, 84, 30)); d.line([pts[0], pts[2]], fill=(120, 180, 80))
    for ring, cnt, col, r0, r1, off in ((0, 21, (214, 148, 24), 44, 64, 0.07), (1, 34, (250, 200, 40), 44, 62, 0)):
        for k in range(cnt):
            a = 2 * math.pi * k / cnt + off + 0.02 * math.sin(t * 2 + k); w = 0.09 if ring else 0.11
            p = [(cx + r0 * math.cos(a - w), cy + r0 * math.sin(a - w)), (cx + (r0 + r1) / 2 * math.cos(a - w * 0.9), cy + (r0 + r1) / 2 * math.sin(a - w * 0.9)),
                 (cx + r1 * math.cos(a), cy + r1 * math.sin(a)), (cx + (r0 + r1) / 2 * math.cos(a + w * 0.9), cy + (r0 + r1) / 2 * math.sin(a + w * 0.9)),
                 (cx + r0 * math.cos(a + w), cy + r0 * math.sin(a + w))]
            d.polygon(p, fill=col, outline=shade(col, 0.72))
            if ring: d.line([p[0], p[2]], fill=(255, 232, 120))
    d.ellipse([cx - 47, cy - 47, cx + 47, cy + 47], fill=(70, 40, 18), outline=(120, 74, 30))
    cc = 44 / math.sqrt(nmax); ga = math.radians(ang_deg)
    for k in range(1, n + 1):
        r = cc * math.sqrt(k); a = k * ga
        x, y = int(round(cx + r * math.cos(a))), int(round(cy + r * math.sin(a)))
        d.rectangle([x, y, x + 1, y + 1], fill=(150, 98, 42) if k % 3 else (120, 76, 30)); d.point((x, y), fill=(206, 150, 70))

def sc_vogel(t):
    c = Ctx(bg("garden")); T = START["vogel"] + t
    for i, (cx, cy, w) in enumerate(((30, 40, 26), (140, 26, 34), (100, 70, 20))):
        x = (cx + t * (2 + i)) % (AW + 40) - 20
        for dx, dy, r in ((0, 0, 1), (w * 0.3, -4, 1.2), (w * 0.6, 0, 1)):
            c.a.ellipse([x + dx - 6 * r, cy + dy - 4 * r, x + dx + 6 * r, cy + dy + 4 * r], fill=(240, 246, 250))
    ph = [p for p in SCH["v_ph"] if t >= p[0]][-1]
    p0, ang, N, dg = ph; lt = t - p0
    n = int(N * min(1, lt / dg) ** 2)
    sunflower(c, t, ang, n, 620 if N > 400 else 420)
    good = abs(ang - 137.5) < 0.1
    lab = "137.5°" if good else f"{ang:.1f}°"
    cols = [CREAM] * 6 if good else [CREAM if a == b else RED for a, b in zip(lab[:-1], "137.5")] + [RED]
    panel(c.t, "VOGEL 1979", lab, "360° / φ² = 137.5°" if good else "SEED ANGLE", cols, right=["SEEDS", str(n)], age=lt)
    cap = None
    if not good and n > 200: cap, cc = ("GAPS!" if ang == 137.0 else "SPOKES!"), RED
    if good and lt > dg: cap, cc = "PERFECT PACKING", CREAM
    if cap:
        w = 8 * len(cap) + 16
        c.t.rectangle([180 - w / 2, 486, 180 + w / 2, 508], fill=(40, 26, 18)); c.t.rectangle([180 - w / 2, 486, 180 + w / 2, 487], fill=(110, 76, 50))
        text(c.t, 180, 486, cap, fill=cc, align="c")
    return c

def sc_laptop(t):
    c = Ctx(bg("term")); T = START[FINAL] + t
    n = upto([x for x, _ in SCH["stream"]], T)
    v2.monitor(c, t, n)
    W = c.t
    W.rectangle([30, 500, 330, 548], fill=(4, 10, 6)); W.rectangle([30, 500, 330, 548], outline=(50, 130, 80))
    s = PHI.replace(".", "")
    for j in range(18):
        i = n - 14 + j
        if 0 <= i < len(s): text(W, 38 + j * 16, 502, s[i], size=40, fill=CREAM if j == 14 else (70, 170, 100) if j < 14 else (24, 70, 40))
    count = max(n, min(10000, int(10000 * ease((t - 0.3) / 5.0) ** 1.6))) if t > 0.3 else 0
    panel(c.t, "ANY LAPTOP 2026", f"{count} DIGITS", "IN UNDER A SECOND", [CREAM] * 14, style="green", sub_col=GREEN)
    g = (t - 5.45) / 0.75
    if g > 0:
        rng = np.random.default_rng(int(t * 1000)); a = np.array(c.art); m = rng.random((AH, AW)) < ease(g * 1.4)
        pal = np.array([(40, 90, 110), (60, 130, 120), (30, 60, 100), (100, 160, 120)], np.uint8)
        a[m] = pal[rng.integers(0, 4, m.sum())]; c.art = Image.fromarray(a)
    return c

def sc_outro(t):
    c = Ctx(bg("grid"))
    lines = ["1.61803398", "87498948", "48204586", "83436563", "81177203"]
    for i, l in enumerate(lines):
        q = (t - i * 0.12) / 0.2
        if q > 0: text(c.t, 40, 96 + i * 40, l, size=40, fill=CREAM if i == 0 else mix((40, 50, 80), CREAM, min(1, q) * (1 - i * 0.16)))
    num_line(c, GR)
    if t > 1.2: text(c.t, 180, 520, "...AND IT NEVER ENDS", fill=DIM, align="c")
    return c

SCENEFN = {"intro": sc_intro, "pentagram": sc_pentagram, "euclid": sc_euclid, "rabbits": sc_rabbits, "kepler": sc_kepler,
           "hurwitz": sc_hurwitz, "hp35": sc_hp35, "penrose": sc_penrose, "vogel": sc_vogel, "laptop": sc_laptop, "outro": sc_outro}

# ---------- FX (same recipe as pi.py) ----------
def intensity(T): return 0.35 + 0.65 * ease(T / START[FINAL]) ** 1.3 + 0.6 * ease((T - START[FINAL]) / 5.0)
HOPS = None
def panel_hop(T):
    global HOPS
    if HOPS is None: HOPS = np.array(sorted([e[0] for e in EV if e[1] in ("digit", "edigit", "chime")] + KICKS))
    i = np.searchsorted(HOPS, T, side="right") - 1
    if i < 0: return 0
    d = T - HOPS[i]
    return int(round(-7 * FXK * math.exp(-d / 0.08) * abs(math.cos(2 * math.pi * d / 0.2))))
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
    if name == "outro": I *= 0.25
    push = 1.02 + 0.04 * I * ease(t / DUR[name])
    kd = (T - KICKS[ki]) if ki >= 0 else 9
    spring = math.exp(-kd / 0.11) * math.cos(2 * math.pi * kd / 0.17)
    zoom = push + kp * (0.015 + 0.035 * I)
    sd = (T - SNARES[si]) if si >= 0 else 9
    squash = math.exp(-sd / 0.09) * math.cos(2 * math.pi * sd / 0.14)
    zx = zoom * (1 - 0.025 * squash * I); zy = zoom * (1 + 0.05 * squash * I)
    rng = random.Random(int(T * 1000)); sh = sp * 14 * I
    sway = math.sin(T * 2 * math.pi / (60 / bpm(T)) / 2) * 10 * I
    dx = rng.uniform(-sh, sh) + sway; dy = -spring * (34 + 70 * I) + rng.uniform(-sh, sh)
    fr = warp(fr, zx, dx, dy, zy)
    split = int(sp * 14 * I + kp * 4 * I)
    if split > 0:
        out = fr.copy(); out[:, split:, 0] = fr[:, :-split, 0]; out[:, :-split, 2] = fr[:, split:, 2]; fr = out
    fl = kp * (14 + 34 * I)
    if fl > 1: fr = np.minimum(255, fr.astype(np.int16) + int(fl)).astype(np.uint8)
    return fr
def strobe(fr, T):
    E = START[FINAL]
    if FXK >= 0.8 and E + 4.4 < T < E + 4.95:
        bl = 60 / bpm(T)
        if int((T - E) / (bl / 4)) % 2: fr = 255 - fr
    return fr

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    g = active_glitch(T)
    if g and g[2] == "stutter":
        T2 = g[0] + ((T - g[0]) % g[3]); t = T2 - START[name]
        if t < 0: idx -= 1; name = NAMES[idx]; t = T2 - START[name]
    if g and g[2] == "tapestop":
        p = (T - g[0]) / g[1]; T2 = g[0] + g[1] * (p - p * p / 2); t = T2 - START[name]
    c = SCENEFN[name](t)
    hop = panel_hop(START[name] + t)
    if hop:
        band = c.txt.crop((0, 60, TW, 162)); c.t.rectangle([0, 60, TW, 162], fill=(0, 0, 0, 0)); c.txt.alpha_composite(band, (0, 60 + hop))
    fr = v2.compose(c, t, idx)
    fr = fx(fr, T, name, t); fr = strobe(fr, T)
    if g: fr = glitch_frame(fr, T, g)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.0)) / 1.0)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
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
