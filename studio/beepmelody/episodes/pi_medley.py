"""BEEPMELODY — CHOCS DE PI, retravail r1 : trois expériences, un seul pi (piste « medley »).
Acte 1 (0-22 s)  : deux blocs, niveaux 1..5, chaque choc (bloc-bloc + bloc-mur) = un clic ; 3 · 31 · 314 · 3,141 · 31,415.
                   Simulation exacte choc par choc (Galperin 2003). Ralenti asinh par niveau (« SLOW MOTION »).
Acte 2 (22-44 s) : 1 400 aiguilles de Buffon (longueur = écart des lattes) ; pi ≈ 2N / croisements (Buffon 1777).
Acte 3 (44-66 s) : 6 000 fléchettes dans un carré ; pi ≈ 4 × dedans / total (Monte-Carlo, Metropolis & Ulam 1949).
Tous les événements (et leurs instants) viennent de pi_medley_data.py (graines fixes 27 et 7) : un événement = un son.
Les actes 2 et 3 sont des tirages aléatoires : l'écran dit « SIMULATION ».
Musique (co-pilote r1 étape 2, choix B « Labo électro ») : 140 BPM, kick 4/4 + sub, clics métal (blocs),
pluck synthé (aiguilles qui croisent), tic étouffé (les autres), zap aigu (fléchette dedans) / coup grave (dehors).
Palette : PM_PAL=light (défaut, retenue au co-pilote r3 « variante claire ») | dark.

    python3 pi_medley.py info out | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE); sys.path.insert(0, HERE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease)
from pi import Ctx, warp
import pi_medley_data as D

FXK = float(os.environ.get("PI_FX", "0.6"))
PAL = os.environ.get("PM_PAL", "light")
PI = math.pi

# ================= data =================
EV = D.events()
A1 = [e for e in EV if e["act"] == 1]; A2 = [e for e in EV if e["act"] == 2]; A3 = [e for e in EV if e["act"] == 3]
T2 = np.array([e["t"] for e in A2]); X2 = np.array([e["kind"] == "x" for e in A2])
C2 = np.cumsum(X2)
T3 = np.array([e["t"] for e in A3]); I3 = np.array([e["kind"] == "in" for e in A3])
C3 = np.cumsum(I3)
P3x = np.array([e["x"] for e in A3]); P3y = np.array([e["y"] for e in A3])
N2, N3 = len(A2), len(A3)
EST2 = 2 * N2 / C2[-1]; EST3 = 4 * C3[-1] / N3

def sim(r):
    """exact event-driven simulation, same set-up as pi_medley_data: small m=1 at x=1, big M=r at x=2 moving at -1, wall at 0."""
    m, M = 1.0, float(r); x1, x2, v1, v2, t = 1.0, 2.0, 0.0, -1.0, 0.0
    T, K, X1, X2_, V1, V2 = [], [], [], [], [], []
    while True:
        tb = (x2 - x1) / (v1 - v2) if v1 > v2 else math.inf
        tw = -x1 / v1 if v1 < 0 else math.inf
        if tb == math.inf and tw == math.inf: break
        if tb < tw:
            dt = tb; x1 += v1 * dt; x2 = x1
            v1, v2 = ((m - M) * v1 + 2 * M * v2) / (m + M), ((M - m) * v2 + 2 * m * v1) / (m + M); k = 0
        else:
            dt = tw; x1 = 0.0; x2 += v2 * dt; v1 = -v1; k = 1
        t += dt; T.append(t); K.append(k); X1.append(x1); X2_.append(x2); V1.append(v1); V2.append(v2)
        if v1 >= 0 and v2 >= v1: break
    return dict(T=np.array(T), K=np.array(K, np.int8), X1=np.array(X1), X2=np.array(X2_), V1=np.array(V1), V2=np.array(V2))

DIG = ["3", "3.1", "3.14", "3.141", "3.1415"]
LV = []
for j, (lv, a, b) in enumerate(D.BLOCK_LEVELS):
    r = 100 ** (lv - 1); s = sim(r)
    disp = np.array([e["t"] for e in A1 if e["level"] == lv])
    assert len(s["T"]) == len(disp), (lv, len(s["T"]), len(disp))
    assert int(str(len(s["T"]))) == int(DIG[j].replace(".", "")), (lv, len(s["T"]))
    w = 1 / math.sqrt(r)
    A0 = math.asinh((s["T"][0] - 2) / w); A1_ = math.asinh((s["T"][-1] - 2) / w)
    LV.append(dict(lv=lv, r=r, n=len(s["T"]), a=a, b=b, w=w, A0=A0, A1=A1_, disp=disp, digits=DIG[j], **s))
NL = len(LV)

ACT2_0, ACT3_0 = D.ACT[1][0], D.ACT[2][0]
OUTRO0 = 65.8; OUTRO = 5.2
TOTAL = OUTRO0 + OUTRO
CHUNKS = [("act1", 0.0, ACT2_0), ("act2", ACT2_0, ACT3_0), ("act3", ACT3_0, OUTRO0), ("outro", OUTRO0, TOTAL)]

def level_at(T):
    """index of the block level shown at global time T (act 1)."""
    for j in range(NL - 1, -1, -1):
        prev_b = LV[j - 1]["b"] if j else 0.0
        if T >= prev_b: return j
    return 0

def phys_t(j, T):
    L = LV[j]; prev_b = LV[j - 1]["b"] if j else 0.0
    if T < L["a"]:                                       # big block slides in
        f = (T - prev_b) / max(1e-6, L["a"] - prev_b); return L["T"][0] * max(0.0, f)
    if T <= L["b"]:
        u = (T - L["a"]) / (L["b"] - L["a"])
        return 2 + L["w"] * math.sinh(L["A0"] + u * (L["A1"] - L["A0"]))
    return L["T"][-1] + (T - L["b"]) * 0.6

def bstate(j, tp):
    L = LV[j]; k = int(np.searchsorted(L["T"], tp, side="right")) - 1
    if k < 0: return 1.0, 2.0 - tp, 0
    dt = tp - L["T"][k]
    return L["X1"][k] + L["V1"][k] * dt, L["X2"][k] + L["V2"][k] * dt, k + 1

def n_at(arr, T): return int(np.searchsorted(arr, T, side="right"))

# ================= look =================
if PAL == "light":
    BG0, BG1 = (196, 226, 246), (240, 246, 250)
    FLOOR, FLOOR2 = (120, 104, 92), (160, 144, 128)
    WALL, WALL2 = (150, 120, 104), (120, 92, 80)
    SMALL, BIG, BIGD = (240, 104, 84), (64, 92, 140), (44, 66, 104)
    PANEL = (255, 255, 255); INK = (40, 48, 64); INK2 = (110, 120, 136)
    GOLD = (214, 140, 30); CYAN = (40, 140, 190); SPARK = (255, 200, 60); DIM = (180, 188, 198)
    LINE = (150, 130, 110); NEEDLE = (150, 160, 176); OUT = (232, 96, 80); BOARD = (232, 218, 196)
else:
    BG0, BG1 = (20, 22, 34), (34, 32, 46)
    FLOOR, FLOOR2 = (86, 74, 66), (60, 52, 48)
    WALL, WALL2 = (110, 92, 80), (80, 66, 58)
    SMALL, BIG, BIGD = (240, 104, 84), (110, 150, 200), (78, 110, 156)
    PANEL = (14, 14, 22); INK = (236, 230, 214); INK2 = (150, 146, 140)
    GOLD = (246, 186, 64); CYAN = (110, 210, 236); SPARK = (255, 236, 160); DIM = (70, 70, 84)
    LINE = (120, 100, 84); NEEDLE = (96, 100, 116); OUT = (240, 104, 84); BOARD = (44, 38, 40)
WHITE = (255, 255, 255)
def _mixc(a, b, f): return tuple(int(x * (1 - f) + y * f) for x, y in zip(a, b))
GOLD_O = _mixc(GOLD, BOARD, 0.55); NEEDLE_O = _mixc(NEEDLE, BOARD, 0.5)

FLOOR_Y = 214; WALL_X = 22; SW = 10; PXU = 52
def big_w(j): return 12 + 5 * j
def fmt(n): return f"{n:,}"
def mass_us(r):
    lb = r * 2.20462
    if lb < 10: return f"{lb:.1f} LB"
    if lb < 1e6: return f"{lb:,.0f} LB"
    if lb < 1e7: return f"{lb / 1e6:.1f} MILLION LB"
    return f"{lb / 1e6:,.0f} MILLION LB"
def mass_si(r): return f"{r:,} KG" if r < 1000 else f"{r // 1000:,} T"

def gradient():
    a = np.zeros((AH, AW, 3), np.float32)
    for y in range(AH):
        f = y / AH; a[y, :] = [BG0[k] * (1 - f) + BG1[k] * f for k in range(3)]
    return a.astype(np.uint8)
_G = gradient()

# --- act 1: blocks ---
_B1 = None
def bg_blocks():
    global _B1
    if _B1 is None:
        img = Image.fromarray(_G.copy()); d = ImageDraw.Draw(img)
        d.rectangle([0, FLOOR_Y, AW, FLOOR_Y + 3], fill=FLOOR)
        for x in range(0, AW, 6): d.line([x, FLOOR_Y + 4, x - 4, FLOOR_Y + 8], fill=FLOOR2)
        d.rectangle([0, FLOOR_Y - 64, WALL_X - 1, FLOOR_Y + 3], fill=WALL)
        for yy in range(FLOOR_Y - 64, FLOOR_Y, 6):
            off = 0 if (yy // 6) % 2 else 5
            d.line([0, yy, WALL_X - 1, yy], fill=WALL2)
            for xx in range(off, WALL_X, 10): d.line([xx, yy, xx, yy + 5], fill=WALL2)
        _B1 = img
    return _B1.copy()

def draw_blocks(c, j, T):
    c.art = bg_blocks(); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    tp = phys_t(j, T); x1, x2, n = bstate(j, tp); bw = big_w(j)
    pxu = min(PXU, (AW - 8 - bw - WALL_X - SW) / max(x2, 1e-9))
    sx = WALL_X + x1 * pxu; bx = WALL_X + SW + x2 * pxu
    d.rectangle([sx, FLOOR_Y - SW, sx + SW - 1, FLOOR_Y - 1], fill=SMALL)
    d.rectangle([sx, FLOOR_Y - SW, sx + SW - 1, FLOOR_Y - SW], fill=(255, 160, 140))
    d.rectangle([bx, FLOOR_Y - bw, bx + bw - 1, FLOOR_Y - 1], fill=BIG)
    d.rectangle([bx, FLOOR_Y - bw, bx + bw - 1, FLOOR_Y - bw], fill=(190, 214, 240))
    d.rectangle([bx + bw - 2, FLOOR_Y - bw, bx + bw - 1, FLOOR_Y - 1], fill=BIGD)
    tq = phys_t(j, max(0.0, T - 1 / FPS)); L = LV[j]
    a_ = int(np.searchsorted(L["T"], tq, side="right")); b_ = int(np.searchsorted(L["T"], tp, side="right"))
    k = L["K"][a_:b_]; nb, nw = int((k == 0).sum()), int((k == 1).sum())
    for cnt, x in ((nw, WALL_X), (nb, sx + SW)):
        if cnt:
            g = min(1.0, 0.35 + 0.18 * math.log10(1 + cnt)); rr = int(3 + 5 * g)
            for _ in range(6):
                ang = random.uniform(-1.4, 1.4); l_ = random.uniform(2, rr)
                d.line([x, FLOOR_Y - 5, x + l_ * math.cos(ang), FLOOR_Y - 5 + l_ * math.sin(ang)], fill=SPARK)
            d.rectangle([x - 1, FLOOR_Y - 8, x + 1, FLOOR_Y - 2], fill=SPARK)
    text(W, (sx + SW / 2) * 2, (FLOOR_Y + 10) * 2, "1 KG", fill=SMALL, align="c")
    bl = mass_si(L["r"])
    text(W, min(352 - 4 * len(bl), max((sx + SW) * 2 + 4 * len(bl) + 10, (bx + bw / 2) * 2)), (FLOOR_Y - bw - 12) * 2, bl, fill=CYAN, align="c")
    W.rectangle([16, 466, 344, 508], fill=PANEL)
    text(W, 180, 470, f"BIG BLOCK: {fmt(L['r'])} KG", fill=CYAN, align="c")
    text(W, 180, 488, mass_us(L["r"]), fill=INK2, align="c")
    return n

# --- act 2: Buffon's needles ---
BX0, BX1, BY0, NS, DPX = 12, 168, 104, 7, 20          # board: 7 strips of 20 px between 8 lines; needle = 20 px
_rs = np.random.RandomState(1234)                       # display only: which strip and where along it (does not change crossing)
STRIP = _rs.randint(0, NS, N2); XPOS = _rs.uniform(BX0 + 10, BX1 - 10, N2)
NEED = []
for e, s_, xx in zip(A2, STRIP, XPOS):
    cy = BY0 + DPX * (s_ + e["y"]); dx, dy = 0.5 * DPX * math.cos(e["th"]), 0.5 * DPX * math.sin(e["th"])
    NEED.append((xx - dx, cy - dy, xx + dx, cy + dy))
_B2 = None
def bg_board():
    global _B2
    if _B2 is None:
        img = Image.fromarray(_G.copy()); d = ImageDraw.Draw(img)
        d.rectangle([BX0 - 4, BY0 - 6, BX1 + 4, BY0 + NS * DPX + 6], fill=BOARD)
        for k in range(NS + 1): d.line([BX0 - 4, BY0 + k * DPX, BX1 + 4, BY0 + k * DPX], fill=LINE)
        _B2 = img
    return _B2.copy()

def draw_needles(c, T):
    c.art = bg_board(); c.a = ImageDraw.Draw(c.art); d = c.a
    n = n_at(T2, T); kold = n_at(T2, T - 1.5)              # needles older than 1.5 s fade back, the new ones stay bright
    for k in range(n):
        if not X2[k]: d.line(NEED[k], fill=NEEDLE_O if k < kold else NEEDLE)
    for k in range(kold):
        if X2[k]: d.line(NEED[k], fill=GOLD_O)
    for k in range(kold, n):
        if X2[k]: d.line(NEED[k], fill=GOLD)
    for k in range(n_at(T2, T - 0.12), n): d.line(NEED[k], fill=WHITE)
    return n

# --- act 3: darts ---
SX0, SY1, SS = 15, 252, 150                             # square: x 15..165, y 102..252 (art px); quarter disc centred bottom-left
_B3 = None
def bg_square():
    global _B3
    if _B3 is None:
        img = Image.fromarray(_G.copy()); d = ImageDraw.Draw(img)
        d.rectangle([SX0 - 1, SY1 - SS - 1, SX0 + SS + 1, SY1 + 1], fill=BOARD, outline=LINE)
        a = np.array(img)
        yy, xx = np.mgrid[0:AH, 0:AW]
        rr = np.hypot(xx - SX0, SY1 - yy)
        ring = (np.abs(rr - SS) < 0.7) & (xx >= SX0) & (yy <= SY1)
        a[ring] = LINE; _B3 = a
    return _B3.copy()

DPXX = np.clip((SX0 + P3x * SS).astype(int), SX0, SX0 + SS - 1); DPXY = np.clip((SY1 - P3y * SS).astype(int), SY1 - SS + 1, SY1)
def draw_darts(c, T):
    a = bg_square(); n = n_at(T3, T)
    ii = I3[:n]
    a[DPXY[:n][ii], DPXX[:n][ii]] = CYAN
    a[DPXY[:n][~ii], DPXX[:n][~ii]] = OUT
    k0 = n_at(T3, T - 0.1)
    for k in range(k0, n):
        y, x = DPXY[k], DPXX[k]; a[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = WHITE
    c.art = Image.fromarray(a); c.a = ImageDraw.Draw(c.art)
    return n

# --- HUD ---
def top(c, act, name, right, big, sub, big_col=None, sub_col=None):
    W = c.t
    W.rectangle([16, 18, 344, 150], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=GOLD); W.rectangle([16, 149, 344, 150], fill=GOLD)
    text(W, 28, 24, f"EXPERIMENT {act} OF 3", fill=GOLD)
    if right: text(W, 334, 24, right, fill=CYAN, align="r")
    text(W, 28, 44, name, fill=INK)
    text(W, 180, 68, big, size=40, fill=big_col or INK, align="c")
    text(W, 180, 116, sub, fill=sub_col or INK2, align="c")

def rule(c, s, s2=None):
    W = c.t
    W.rectangle([16, 156, 344, 178 if not s2 else 196], fill=PANEL)
    text(W, 180, 158, s, fill=CYAN, align="c")
    if s2: text(W, 180, 176, s2, fill=INK2, align="c")

def strip(c, T):
    W = c.t
    W.rectangle([0, 520, 360, 640], fill=PANEL); W.rectangle([0, 520, 360, 521], fill=GOLD)
    text(W, 12, 526, "3 WAYS TO FIND PI", fill=INK2)
    rows = []
    # act 1
    if T < LV[0]["b"]: v1, c1 = "...", CYAN
    else:
        done = [L for L in LV if T >= L["b"]]
        v1, c1 = done[-1]["digits"], (INK if T >= LV[-1]["b"] else CYAN)
    Lc = LV[level_at(min(T, ACT2_0 - 0.01))]
    nb = min(Lc["n"], n_at(Lc["disp"], T))
    rows.append(("1 BLOCKS", fmt(nb) + " HITS", v1, c1))
    if T < T2[0]: rows.append(("2 NEEDLES", "", "?", DIM))
    else:
        n = n_at(T2, T); cx = int(C2[n - 1]) if n else 0
        rows.append(("2 NEEDLES", fmt(n) + " DROPS", f"{2 * n / cx:.4f}" if cx else "...", INK if n == N2 else CYAN))
    if T < T3[0]: rows.append(("3 DARTS", "", "?", DIM))
    else:
        n = n_at(T3, T); ci = int(C3[n - 1]) if n else 0
        rows.append(("3 DARTS", fmt(n) + " THROWS", f"{4 * ci / n:.4f}" if n else "...", INK if n == N3 else CYAN))
    for k, (a, b, v, col) in enumerate(rows):
        y = 544 + k * 18
        text(W, 16, y, a, fill=col if col != DIM else DIM)
        text(W, 120, y, b, fill=INK2 if col != DIM else DIM)
        text(W, 344, y, v, fill=GOLD if col == INK else col, align="r")
    text(W, 16, 600, "TRUE PI", fill=INK2); text(W, 344, 600, "3.14159...", fill=INK2, align="r")

def banner(c, big, small, col=None):
    W = c.t; yb = 228; w = 310
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 72], fill=PANEL); W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col or GOLD)
    text(W, 180, yb + 8, big, size=40, fill=col or GOLD, align="c")
    text(W, 180, yb + 50, small, fill=INK, align="c")

def frame_c():
    return Ctx(np.zeros((AH, AW, 3), np.uint8))

def scene(T):
    c = frame_c()
    if T < ACT2_0:                                       # ---------- act 1
        j = level_at(T); L = LV[j]
        n = draw_blocks(c, j, T)
        if T < 2.4:                                      # title in the top panel
            W = c.t
            W.rectangle([16, 18, 344, 150], fill=PANEL); W.rectangle([16, 18, 344, 19], fill=GOLD); W.rectangle([16, 149, 344, 150], fill=GOLD)
            text(W, 180, 26, "3 EXPERIMENTS.", size=40, fill=INK, align="c")
            if T > 0.3: text(W, 180, 66, "1 NUMBER.", size=40, fill=GOLD, align="c")
            if T > 0.8: text(W, 180, 112, "LISTEN TO PI", fill=CYAN, align="c")
        else:
            done = T > L["b"]
            sub = f"COLLISIONS · PI = {L['digits']}..." if done else f"COLLISIONS · LEVEL {j + 1} OF {NL}"
            fresh = (not done) and 0 < n and n_at(L["disp"], T - 0.07) < n
            top(c, 1, "COLLIDING BLOCKS", "SLOW MOTION" if j > 0 and L["a"] <= T <= L["b"] + 0.1 else "",
                fmt(n), sub, big_col=GOLD if (fresh or done) else INK, sub_col=GOLD if done else None)
        rule(c, "EVERY BEEP = ONE COLLISION", f"BIG BLOCK = {fmt(L['r'])} x SMALL")
        if T >= LV[-1]["b"] + 0.05:
            banner(c, "31,415 HITS", "= 3.1415... THE DIGITS OF PI")
    elif T < ACT3_0:                                     # ---------- act 2
        n = draw_needles(c, T); cx = int(C2[n - 1]) if n else 0
        est = f"PI ≈ {2 * n / cx:.4f}" if cx else "PI ≈ ?"
        top(c, 2, "BUFFON'S NEEDLES (1777)", "SIMULATION", est, f"{fmt(n)} NEEDLES · {fmt(cx)} CROSS A LINE", big_col=GOLD)
        rule(c, "EVERY BEEP = ONE NEEDLE", "PI ≈ 2 x NEEDLES / CROSSINGS")
        if T < T2[0] + 0.2:
            banner(c, "DROP NEEDLES", "ON LINES ONE NEEDLE APART", col=CYAN)
        if T >= T2[-1] + 0.05:
            banner(c, f"{EST2:.4f}", f"{fmt(N2)} NEEDLES, {fmt(int(C2[-1]))} CROSSINGS")
    elif T < OUTRO0:                                     # ---------- act 3
        n = draw_darts(c, T); ci = int(C3[n - 1]) if n else 0
        est = f"PI ≈ {4 * ci / n:.4f}" if n else "PI ≈ ?"
        top(c, 3, "RANDOM DARTS (MONTE CARLO)", "SIMULATION", est, f"{fmt(n)} DARTS · {fmt(ci)} INSIDE THE ARC", big_col=GOLD)
        rule(c, "EVERY BEEP = ONE DART", "PI ≈ 4 x INSIDE / ALL DARTS")
        if T < T3[0] + 0.2:
            banner(c, "THROW DARTS", "AT A SQUARE WITH A QUARTER CIRCLE", col=CYAN)
    else:                                                # ---------- outro
        t = T - OUTRO0
        draw_darts(c, OUTRO0); W = c.t
        W.rectangle([16, 18, 344, 470], fill=PANEL); W.rectangle([16, 18, 344, 20], fill=GOLD)
        text(W, 180, 30, "3 EXPERIMENTS", fill=INK2, align="c")
        text(W, 180, 52, "1 NUMBER", size=40, fill=INK, align="c")
        if t > 0.4: text(W, 180, 100, "PI = 3.14159...", size=40, fill=GOLD, align="c")
        if t > 1.0:
            text(W, 28, 160, "BLOCKS", fill=INK); text(W, 332, 160, "3.1415 (EXACT)", fill=GOLD, align="r")
            text(W, 28, 182, "NEEDLES", fill=INK); text(W, 332, 182, f"{EST2:.4f}", fill=GOLD, align="r")
            text(W, 28, 204, "DARTS", fill=INK); text(W, 332, 204, f"{EST3:.4f}", fill=GOLD, align="r")
        if t > 2.0: text(W, 180, 252, "WHICH ONE WOULD YOU TRUST?", fill=CYAN, align="c")
        if t > 2.6:
            text(W, 180, 318, "BLOCKS: G. GALPERIN, 2003", fill=INK2, align="c")
            text(W, 180, 336, "NEEDLES: BUFFON, 1777", fill=INK2, align="c")
            text(W, 180, 354, "DARTS: METROPOLIS & ULAM, 1949", fill=INK2, align="c")
            text(W, 180, 380, "NEEDLES + DARTS: SIMULATED DROPS", fill=INK2, align="c")
            text(W, 180, 398, "BLOCKS: EXACT, NO FRICTION", fill=INK2, align="c")
    if T < OUTRO0: strip(c, T)
    else: strip(c, OUTRO0)
    return c

def compose_layers(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tb = np.repeat(np.repeat(np.array(c.txt), 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

BPM = 140; BEAT = 60 / BPM
BEATS = np.arange(0, TOTAL + BEAT, BEAT)
HITS = [L["disp"][0] for L in LV] + [T2[0], T3[0]]
def render_frame(T):
    random.seed(int(T * 1000))
    fr = compose_layers(scene(T))
    if T < OUTRO0 + 1.5:
        bi = int(np.searchsorted(BEATS, T, side="right")) - 1
        kp = math.exp(-(T - BEATS[bi]) / 0.08)
        z = 1.0 + 0.008 * kp * FXK
        if z > 1.0005: fr = warp(fr, z, 0, 0, z)
    for h in HITS:
        a = T - h
        if 0 <= a < 0.12: fr = np.minimum(255, fr.astype(np.int16) + int(40 * FXK * (1 - a / 0.12))).astype(np.uint8)
    f = ease((T - (TOTAL - 0.8)) / 0.8)
    if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    f = 1 - ease(T / 0.25)
    if f > 0: fr = (fr * (1 - f) + np.array(BG0) * f).astype(np.uint8)
    return fr

# ================= audio (choice B « Labo électro », from pi_medley_moods.py mood_b, full length) =================
SR = 44100
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter, fftconvolve
    N = int((TOTAL + 0.5) * SR); T = np.arange(N) / SR
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def put(L, t0, s, g=1.0):
        i = int(t0 * SR); j = min(N, i + len(s))
        if 0 <= i < N: L[i:j] += g * s[:j - i]
    rs = np.random.RandomState(5)
    def noise(d, dec, f=None, hi=True):
        n = int(d * SR); s = rs.randn(n) * np.exp(-np.arange(n) / SR * dec)
        return (hp(s, f) if hi else lp(s, f)) if f else s
    def kick(g, f0=80, f1=45, dec=13):
        m = int(.3 * SR); tt = np.arange(m) / SR
        return g * np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * 18) + f1) / SR) * np.exp(-tt * dec)
    def grain(f, dec, dur=.15, harm=(1,), a=.0005):
        n = int(dur * SR); tt = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * h * tt) / (i + 1) for i, h in enumerate(harm))
        return s * np.minimum(1, tt / a) * np.exp(-tt / dec)
    def conv(tr, g): return fftconvolve(tr, g, "full")[:N]
    def train(times):
        x = np.zeros(N); np.add.at(x, np.minimum(N - 1, (np.asarray(times) * SR).astype(np.int64)), 1.0)
        k = int(.03 * SR); r = np.convolve(np.abs(x) > 0, np.ones(k), "same")
        return x / np.sqrt(np.maximum(1, r))
    def density_gain(times):
        x = np.zeros(N); np.add.at(x, np.minimum(N - 1, (np.asarray(times) * SR).astype(np.int64)), 1.0)
        r = np.convolve(x, np.ones(int(.05 * SR)), "same") / .05
        return 1 / np.sqrt(np.maximum(1, lp(r, 20) / 40))
    PENT = [0, 2, 4, 7, 9]
    def pent(i, base): return base + 12 * (i // 5) + PENT[i % 5]
    L = np.zeros(N)
    T_OFF = OUTRO0 + 1.0                                  # drums drop in the outro
    for k, b in enumerate(BEATS):
        if b >= TOTAL - 0.3: break
        g = 1.0 if b < T_OFF else 0.0
        if g:
            put(L, b, kick(.38 * (0.75 if b < 2.4 else 1)))
            put(L, b + BEAT / 2, .06 * noise(.04, 90, 6000))
            if k % 2: put(L, b, .07 * noise(.15, 25, 3000))
        root = [33, 33, 36, 31][(k // 4) % 4]; m = int(.25 * SR)
        gb = 1.0 if b < T_OFF + 1.5 else max(0.0, 1 - (b - T_OFF - 1.5) / 2.0)
        if gb > 0: put(L, b + BEAT / 2, .12 * gb * lp(np.sign(np.sin(2 * np.pi * mtof(root) * np.arange(m) / SR)), 400) * np.exp(-np.arange(m) / SR * 10))
    # act 1: every clack = dry metal click ; big hit on the first clack of each level
    t1 = np.concatenate([Lv["disp"] for Lv in LV])
    L += .26 * conv(train(t1), grain(3200, .004, .03, (1, 1.7, 2.9)))
    for Lv in LV: put(L, Lv["disp"][0], kick(.45)); put(L, Lv["disp"][0], .05 * noise(.8, 6, 4000))
    # act 2: crossing needle = synth pluck (pitch from its offset between the lines), the others = muted tick
    g2 = density_gain(T2)
    L2 = np.zeros(N)
    ys = np.array([e["y"] for e in A2])
    for m in set(pent(int(y * 10), 57) for y in ys[X2]):
        sel = X2 & (np.array([pent(int(y * 10), 57) for y in ys]) == m)
        x = np.zeros(N); np.add.at(x, np.minimum(N - 1, (T2[sel] * SR).astype(np.int64)), 1.0)
        L2 += conv(x, lp(grain(mtof(m), .05, .25, (1, 2, 3, 4, 5), .001), 3500))
    L += .20 * L2 * g2
    L += .06 * conv(train(T2[~X2]), noise(.02, 200, 5000))
    # act 3: dart inside = high zap, outside = low thud
    L += .16 * conv(train(T3[I3]), grain(2400, .008, .04, (1, 1.5)))
    L += .20 * conv(train(T3[~I3]), grain(110, .03, .1))
    # act starts + results: ding (the number on screen)
    for h in (T2[0], T3[0]): put(L, h, kick(.45)); put(L, h, .05 * noise(.8, 6, 4000))
    def ding(t0, g=.12):
        m = int(.8 * SR); tt = np.arange(m) / SR
        put(L, t0, g * (np.sin(2 * np.pi * 1568 * tt) + .4 * np.sin(2 * np.pi * 2349 * tt)) * np.exp(-tt * 5))
    for Lv in LV: ding(Lv["b"] + 0.05, .08)
    ding(T2[-1] + 0.1); ding(OUTRO0 + 0.4, .14)
    # outro: final chord (A minor add9, low → high) under the recap
    for q, m in enumerate([45, 52, 57, 59, 60, 64]):
        n = int(4.0 * SR); tt = np.arange(n) / SR
        put(L, OUTRO0 + 0.4 + q * 0.06, .05 * lp(np.sign(np.sin(2 * np.pi * mtof(m) * tt)), 1800) * np.minimum(1, tt / .02) * np.exp(-tt * .9))
    out = L.copy()
    for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11)]:
        q = int(dl * SR); out[q:] += g * .6 * L[:-q]
    x = .85 * L + .15 * lp(out, 4000)
    x = np.tanh(x * 1.5) / 1.5
    x *= np.clip((TOTAL + 0.2 - T) / 1.2, 0, 1)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(len(x) / SR, 2), "s")

def render_chunk(args):
    idx, out = args; name, a, b = CHUNKS[idx]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    f0, f1 = int(round(a * FPS)), int(round(b * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(render_frame(f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio": render_audio(out); sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "at":
        for x in sys.argv[3:]:
            T = float(x); Image.fromarray(render_frame(T)).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.2f}_{PAL}.png")
    elif mode == "info":
        print("total", round(TOTAL, 2), "s · events", len(EV), "· blocks", len(A1), "needles", N2, "cross", int(C2[-1]), "darts", N3, "in", int(C3[-1]))
        print("est needles", EST2, "darts", EST3)
        for L in LV: print("level", L["lv"], L["r"], L["n"], round(L["disp"][0], 2), "->", round(L["disp"][-1], 2))
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        with Pool(min(4, os.cpu_count() or 2)) as pool: print(pool.map(render_chunk, [(i, out) for i in range(len(CHUNKS))]))
