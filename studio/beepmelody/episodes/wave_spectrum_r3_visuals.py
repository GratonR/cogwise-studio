"""BeepMelody · wave-spectrum · RETRAVAIL r2, step 3 (visuals) — 3 truly different directions for the SAME data.
Guillaume (15 Nov, 23:05): "innover sur les angles et mouvements de caméra, sur la façon de représenter les différentes
ondes ... en restant le plus réaliste possible, ondes comprises."
Rule kept in all three: faster wave = tighter crests on screen; colour = band; HUD / ruler / banners unchanged.
  A · VOYAGE   : a 3D spectrum road (slow -> fast). The camera travels along it from one discovery to the next, then
                 orbits the source: low angle for sound, eye level for light, top-down plunge for gravity.
  B · PHYSIQUE : each family drawn with its real physics. Sound = air particles squeezed / stretched (longitudinal),
                 light = electric and magnetic fields at right angles (3D, slow orbit), gravity = a ring of particles
                 stretched in "+" and "x" polarisation.
  C · ECHELLE  : one wavelength drawn at true scale next to a reference object (bus, Earth, atom, proton); the camera
                 zooms by powers of ten from one wave to the next.
usage: python3 wave_spectrum_r3_visuals.py <out_dir> [A B C] [--anim]
"""
import sys, os, math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_spectrum as ws
from wave_spectrum import AW, AH, REC, N, pos, mix, text, ease, PANEL, INK_T, INK2_T, GOLD_T, CYAN_T, FAMC_T

VIS = "A"
MAG = (255, 60, 200)
CX, CY, F = 90, 158, 120                       # scene centre in art px (HUD above y 76, ruler below y 238)

def cyc(i): return 1.5 + 9 * pos(i)            # crests in view: slow wave = few, fast wave = many
def col_of(i): return ws.wave_col(i)

# ---------------- small 3D camera ----------------
class Cam:
    def __init__(self, eye, tgt, f=F, cx=CX, cy=CY):
        self.e = np.array(eye, float); t = np.array(tgt, float); fw = t - self.e; fw /= np.linalg.norm(fw)
        rt = np.cross([0, 1, 0], fw); rt /= np.linalg.norm(rt) + 1e-9; up = np.cross(fw, rt)
        self.R = np.array([rt, up, fw]); self.f, self.cx, self.cy = f, cx, cy
    def cam(self, p): return self.R @ (np.asarray(p, float) - self.e)
    def scr(self, q): return self.cx + self.f * q[0] / q[2], self.cy - self.f * q[1] / q[2]
    def line(self, d, a, b, fill, width=1, near=0.15):
        qa, qb = self.cam(a), self.cam(b)
        if qa[2] < near and qb[2] < near: return
        if qa[2] < near: qa = qa + (qb - qa) * (near - qa[2]) / (qb[2] - qa[2])
        if qb[2] < near: qb = qb + (qa - qb) * (near - qb[2]) / (qa[2] - qb[2])
        d.line([self.scr(qa), self.scr(qb)], fill=fill, width=width)
    def poly(self, d, pts, fill, width=1):
        for a, b in zip(pts, pts[1:]): self.line(d, a, b, fill, width)
    def dot(self, d, p, r, fill):
        q = self.cam(p)
        if q[2] < 0.2: return None
        x, y = self.scr(q); rr = max(0.6, r * self.f / q[2]); d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=fill); return x, y

def sky(d, top=(4, 8, 26), bot=(30, 10, 60)):
    for y in range(AH): d.line([0, y, AW, y], fill=mix(top, bot, min(1, y / 240)))
    for (x, y, s) in ws.STARS: d.point((x, y), fill=[(50, 60, 110), (180, 200, 255), (90, 100, 160)][s])

def caption(c, s, colr):                       # one line of "what you are seeing", just above the ruler
    W = c.t; w = 8 * len(s) + 20
    W.rectangle([180 - w / 2, 414, 180 + w / 2, 432], fill=PANEL); text(W, 180, 416, s, fill=colr, align="c")

# ================= A · VOYAGE (camera travels the spectrum, then orbits the source) =================
ZL = 70.0
def zp(i): return pos(i) * ZL
def camA(i, age, T, prev):
    tgt = np.array([0, 1.2, zp(i)]); fam = REC[i]["family"]
    h = {"sound": 0.25, "light": 1.6, "gravity": 7.5}[fam]           # low angle / eye level / plunge
    R = {"sound": 5.6, "light": 6.4, "gravity": 3.6}[fam]
    th = -0.9 + 0.45 * age                                            # slow orbit around the source
    eye = tgt + np.array([R * math.sin(th), h, -R * math.cos(th)])
    if prev is not None and age < 0.55:                               # travelling shot from the previous find
        u = ease(age / 0.55); pt = np.array([0, 1.2, zp(prev)])
        mid_t = pt + (tgt - pt) * u; mid_e = mid_t + np.array([0.6, 2.2, -6.0])
        w = 1 - ease((age - 0.3) / 0.25) if age > 0.3 else 1.0
        eye = mid_e * w + eye * (1 - w); tgt = mid_t * w + tgt * (1 - w)
    return Cam(eye, tgt)

def scene_A(c, i, T, age, prev):
    d = c.a; sky(d); cam = camA(i, age, T, prev)
    fam = REC[i]["family"]; col = col_of(i); grav = fam == "gravity"
    for xk in np.arange(-6, 6.1, 1.5):                                # the spectrum road
        cam.line(d, (xk, 0, -5), (xk, 0, ZL + 5), (60, 24, 110) if abs(xk) > 0.1 else (120, 50, 170))
    for zk in np.arange(-5, ZL + 5, 2.5):
        if grav and abs(zk - zp(i)) < 9:
            pts = []
            for xk in np.linspace(-6, 6, 25):
                r = math.hypot(xk, zk - zp(i)); y = 0.45 * math.sin(r * 2.2 - T * 6) * math.exp(-r * 0.18)
                if i == ws.I_LIGO: y -= 1.2 / (r + 0.8) * (1 - ease(max(0, age - 1.4)))
                pts.append((xk, y, zk))
            cam.poly(d, pts, mix((60, 24, 110), col, 0.7))
        else: cam.line(d, (-6, 0, zk), (6, 0, zk), (50, 20, 96))
    if grav:                                                          # radial threads of the space-time sheet
        for xk in np.linspace(-6, 6, 13):
            pts = []
            for zk in np.linspace(zp(i) - 8, zp(i) + 8, 30):
                r = math.hypot(xk, zk - zp(i)); y = 0.45 * math.sin(r * 2.2 - T * 6) * math.exp(-r * 0.18)
                if i == ws.I_LIGO: y -= 1.2 / (r + 0.8) * (1 - ease(max(0, age - 1.4)))
                pts.append((xk, y, zk))
            cam.poly(d, pts, mix((60, 24, 110), col, 0.5))
    for j in range(N):                                                # one beacon per discovery
        if j > i and T >= ws.RT[0]: continue
        if T < ws.RT[0] and j not in (ws.I_BH, ws.I_TOP): continue
        cc = ws.FAMC[REC[j]["family"]]; x0 = 2.6 if j % 2 else -2.6
        cam.line(d, (x0, 0, zp(j)), (x0, 1.4, zp(j)), mix((40, 20, 80), cc, 0.8))
        cam.dot(d, (x0, 1.5, zp(j)), 0.12, cc if j != i else (255, 255, 255))
    if not grav:                                                      # the wave itself, crests packed by speed
        L = 5.0; n = cyc(i); amp = 0.75 * (1 + 0.5 * math.exp(-age / 0.3))
        pts = [(0, 1.2 + amp * math.sin(2 * math.pi * n * q / 160 - T * 6), zp(i) - L / 2 + L * q / 160) for q in range(161)]
        cam.poly(d, pts, col, 2)
        if fam == "sound":
            for q in range(0, 161, 4):
                z = zp(i) - L / 2 + L * q / 160; s = math.sin(2 * math.pi * n * q / 160 - T * 6)
                cam.line(d, (-1.4, 1.2, z), (1.4, 1.2, z), mix((40, 20, 80), col, 0.25 + 0.4 * (s > 0.3)))
    else:
        tg = (0, 1.0, zp(i))
        if i == ws.I_LIGO and age < 1.5:
            rad = 0.9 * (1 - 0.85 * ease(age / 1.5)); a = T * (3 + 14 * ease(age / 1.5))
            for s_ in (1, -1): cam.dot(d, (s_ * rad * math.cos(a), 0.6, zp(i) + s_ * rad * math.sin(a)), 0.22, (255, 255, 255))
        else: cam.dot(d, tg, 0.25, (255, 255, 255))
    caption(c, {"sound": "LOW ANGLE · SOUND", "light": "EYE LEVEL · LIGHT", "gravity": "TOP-DOWN · GRAVITY"}[fam], FAMC_T[fam])

# ================= B · PHYSIQUE (each family drawn with its real physics) =================
def scene_B(c, i, T, age, prev):
    d = c.a; fam = REC[i]["family"]; col = col_of(i); n = cyc(i)
    sky(d, (3, 6, 18), (12, 8, 34))
    w = 6.0; amp_k = 1 + 0.5 * math.exp(-age / 0.3)
    if fam == "sound":                                                # air particles pushed and pulled along the wave
        x0, x1, y0, y1 = 8, 172, 90, 228
        k = 2 * math.pi * n / (x1 - x0); A = 0.45 / k * amp_k
        gx, gy = np.meshgrid(np.arange(x0, x1, 2.2), np.arange(y0, y1, 3.0))
        jit = (np.sin(gx * 12.9898 + gy * 78.233) * 43758.5453) % 1 - 0.5
        X = gx + jit * 0.8; Y = gy + jit * 1.6
        ph = k * (X - x0) - w * T
        Xd = X - A * np.sin(ph); dens = np.cos(ph)                       # particles bunch where cos > 0
        for x, y, s_ in zip(Xd.ravel(), Y.ravel(), dens.ravel()):
            d.point((x, y), fill=mix((50, 30, 24), col, 0.25 + 0.75 * max(0.0, s_)))
        for q in range(int(n) + 2):                                   # compression fronts
            xc = x0 + ((q * 2 * math.pi + w * T) / k) % (x1 - x0 + 2 * math.pi / k)
            if x0 < xc < x1: d.line([xc, y0 - 4, xc, y0 - 1], fill=col)
        d.ellipse([2, 150, 14, 168], fill=mix((40, 20, 10), col, 0.6 + 0.4 * math.sin(w * T)))
        caption(c, "SOUND = AIR SQUEEZED AND STRETCHED", FAMC_T["sound"])
    elif fam == "light":                                              # E (vertical) and B (horizontal) at right angles
        th = 0.55 + 0.35 * math.sin(T * 0.4)
        cam = Cam((7.5 * math.sin(th), 2.6, -7.5 * math.cos(th) + 0.3), (0, 0, 0), f=150)
        L = 9.0; A = 1.6 * min(1.3, amp_k)
        cam.line(d, (-L / 2 - 0.5, 0, 0), (L / 2 + 0.8, 0, 0), (110, 120, 170))
        cam.line(d, (L / 2 + 0.8, 0, 0), (L / 2 + 0.4, 0.15, 0), (110, 120, 170)); cam.line(d, (L / 2 + 0.8, 0, 0), (L / 2 + 0.4, -0.15, 0), (110, 120, 170))
        bc = (90, 150, 255) if col != (80, 140, 255) else (150, 110, 255)
        M = 240; E, B = [], []
        for q in range(M + 1):
            x = -L / 2 + L * q / M; s = math.sin(2 * math.pi * n * q / M - w * T)
            E.append((x, A * s, 0)); B.append((x, 0, A * s))
            if q % 3 == 0:
                cam.line(d, (x, 0, 0), (x, A * s, 0), mix((10, 10, 30), col, 0.55))
                cam.line(d, (x, 0, 0), (x, 0, A * s), mix((10, 10, 30), bc, 0.45))
        cam.poly(d, B, bc, 1); cam.poly(d, E, col, 2)
        caption(c, "LIGHT = ELECTRIC + MAGNETIC, AT 90°", FAMC_T["light"])
        W = c.t; text(W, 22, 170, "E", fill=col); text(W, 40, 170, "ELECTRIC", fill=INK2_T)
        text(W, 22, 186, "B", fill=bc); text(W, 40, 186, "MAGNETIC", fill=INK2_T)
    else:                                                             # a ring of particles: "+" and "x" polarisation
        lig = i == ws.I_LIGO
        h = 0.32 * amp_k * (min(1, 0.3 + age) if not lig else 0.25 + 0.75 * ease(max(0, age - 0.9) / 0.6))
        ph = w * T * (1 + (3 * ease(age / 1.6) if lig else 0))
        for gx in range(0, AW + 1, 12):                               # space-time grid stretched by the wave (+)
            pts = [(90 + (gx - 90) * (1 + h * 0.6 * math.sin(ph)), y) for y in range(84, 236, 4)]
            d.line(pts, fill=(40, 26, 70))
        for gy in range(84, 237, 12):
            d.line([(0, 160 + (gy - 160) * (1 - h * 0.6 * math.sin(ph))), (AW, 160 + (gy - 160) * (1 - h * 0.6 * math.sin(ph)))], fill=(40, 26, 70))
        for (ox, rot, lab) in ((48, 0.0, "+"), (132, math.pi / 4, "X")):
            e = h * math.sin(ph); R0 = 30
            for q in range(28):
                a = 2 * math.pi * q / 28; x, y = R0 * math.cos(a), R0 * math.sin(a)
                xr, yr = x * math.cos(-rot) - y * math.sin(-rot), x * math.sin(-rot) + y * math.cos(-rot)
                xr, yr = xr * (1 + e), yr * (1 - e)
                X, Y = xr * math.cos(rot) - yr * math.sin(rot), xr * math.sin(rot) + yr * math.cos(rot)
                d.ellipse([ox + X - 1.6, 150 + Y - 1.6, ox + X + 1.6, 150 + Y + 1.6], fill=col)
            text(c.t, ox * 2, 282, lab, size=40, fill=PINK_T(), align="c")
        if lig:
            a = T * (3 + 14 * ease(age / 1.5)); rr = 9 * (1 - 0.85 * ease(age / 1.5))
            if age < 1.5:
                for s_ in (1, -1): d.ellipse([90 + s_ * rr * math.cos(a) - 2.5, 108 + s_ * rr * 0.5 * math.sin(a) - 2.5, 90 + s_ * rr * math.cos(a) + 2.5, 108 + s_ * rr * 0.5 * math.sin(a) + 2.5], fill=(255, 255, 255))
        caption(c, "GRAVITY = SPACE STRETCHED + AND X", FAMC_T["gravity"])
def PINK_T(): return ws.PINK_T

# ================= C · ECHELLE (one wavelength at true scale next to a reference object) =================
C0 = 299792458.0
def wavelength(i):
    r = REC[i]; f = float(r["freq_hz"])
    if r["family"] == "sound":
        v = 1500.0 if "WHALE" in r["label"] else 343.0               # water for whales, air otherwise
        return v / f if r["year"] != "2003" else None                 # black hole: gas in a galaxy cluster (not drawn)
    return C0 / f
REF = [  # (size m, name, drawer)
    (1.7e-15, "A PROTON", "proton"), (1e-10, "AN ATOM", "atom"), (7e-5, "A HAIR (WIDTH)", "hair"),
    (1.7, "A PERSON", "person"), (12.0, "A CITY BUS", "bus"), (1.27e7, "PLANET EARTH", "earth")]
def ref_for(lam):
    return min(REF, key=lambda r: abs(math.log10(lam / r[0])))
def draw_obj(d, kind, x0, y1, s, colr):
    """x0,y1 = bottom-left, s = size in px"""
    if kind == "bus":
        d.rectangle([x0, y1 - s * 0.28, x0 + s, y1 - s * 0.06], fill=(240, 190, 60))
        for k in range(6): d.rectangle([x0 + s * (0.06 + 0.15 * k), y1 - s * 0.25, x0 + s * (0.16 + 0.15 * k), y1 - s * 0.17], fill=(60, 90, 140))
        for xx in (0.18, 0.8): d.ellipse([x0 + s * xx - s * 0.06, y1 - s * 0.11, x0 + s * xx + s * 0.06, y1 + s * 0.01], fill=(30, 30, 40))
    elif kind == "earth":
        r = s / 2; d.ellipse([x0, y1 - s, x0 + s, y1], fill=(40, 90, 200))
        d.ellipse([x0 + r * 0.4, y1 - s * 0.8, x0 + r * 1.0, y1 - s * 0.45], fill=(70, 170, 90))
        d.ellipse([x0 + r * 1.1, y1 - s * 0.5, x0 + r * 1.6, y1 - s * 0.2], fill=(70, 170, 90))
    elif kind == "atom":
        cx, cy = x0 + s / 2, y1 - s / 2
        for k in range(3):
            a = k * math.pi / 3; pts = [(cx + s / 2 * math.cos(t) * math.cos(a) - s / 6 * math.sin(t) * math.sin(a),
                                         cy + s / 2 * math.cos(t) * math.sin(a) + s / 6 * math.sin(t) * math.cos(a)) for t in np.linspace(0, 2 * math.pi, 40)]
            d.line(pts, fill=(140, 200, 255))
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 140, 90))
    elif kind == "proton":
        cx, cy = x0 + s / 2, y1 - s / 2; d.ellipse([x0, y1 - s, x0 + s, y1], fill=(220, 80, 80))
        for k, cc in enumerate([(255, 60, 60), (60, 200, 90), (70, 120, 255)]):
            a = k * 2.1; d.ellipse([cx + s * 0.22 * math.cos(a) - s * 0.1, cy + s * 0.22 * math.sin(a) - s * 0.1, cx + s * 0.22 * math.cos(a) + s * 0.1, cy + s * 0.22 * math.sin(a) + s * 0.1], fill=cc)
    elif kind == "hair":
        d.rectangle([x0, y1 - s * 3, x0 + s, y1], fill=(120, 80, 50))
    elif kind == "person":
        d.ellipse([x0 + s * 0.38, y1 - s, x0 + s * 0.62, y1 - s * 0.78], fill=colr)
        d.rectangle([x0 + s * 0.4, y1 - s * 0.78, x0 + s * 0.6, y1 - s * 0.35], fill=colr)
        d.line([x0 + s * 0.45, y1 - s * 0.35, x0 + s * 0.4, y1], fill=colr, width=2); d.line([x0 + s * 0.55, y1 - s * 0.35, x0 + s * 0.6, y1], fill=colr, width=2)
def fmt_len(m):
    for lim, div, u in ((1e3, 1e3, "KM"), (1, 1, "M"), (1e-2, 1e-2, "CM"), (1e-3, 1e-3, "MM"), (1e-6, 1e-6, "MICRONS"), (1e-9, 1e-9, "NM")):
        if m >= lim: v = m / div; return (f"{v:,.0f}" if v >= 10 else f"{v:.1f}") + " " + u
    return f"{m:.0e}".replace("e-", "×10^-").upper() + " M"
def us_len(m):
    mi = m / 1609.344; ft = m / 0.3048; inch = m / 0.0254
    if mi >= 1: return f"{mi:,.0f} MI"
    if ft >= 3: return f"{ft:,.0f} FT"
    if inch >= 0.01: return f"{inch:.2f} IN"
    return None
def scene_C(c, i, T, age, prev):
    d = c.a; sky(d, (3, 6, 18), (16, 10, 40)); col = col_of(i); lam = wavelength(i)
    W = c.t
    z = ease(age / 0.6)                                               # powers-of-ten zoom between finds
    for k in range(6):
        rr = (k + 1 - z * 0.999) * 18 + 6
        if rr > 2: d.rectangle([90 - rr * 0.56, 158 - rr, 90 + rr * 0.56, 158 + rr], outline=mix((6, 8, 24), (60, 50, 110), max(0, 1 - k / 6)))
    if lam is None:
        text(W, 180, 300, "A SOUND WAVE IN HOT GAS", fill=INK2_T, align="c"); return
    rs, rname, kind = ref_for(lam)
    span = 130; n = max(1.0, min(6.0, 1.5 + 4.5 * pos(i)))          # rule kept: fast wave = more crests in view
    lam_px = span / n; px_per_m = lam_px / lam                       # true scale between the wave and the object
    pts = [(25 + span * q / 200, 128 - 18 * math.sin(2 * math.pi * n * q / 200 - T * 6)) for q in range(201)]
    d.line(pts, fill=col, width=2)
    x_a = 25 + span * 0.25 / n; x_b = x_a + lam_px                   # one wavelength, crest to crest
    for xx in (x_a, x_b): d.line([xx, 100, xx, 106], fill=(255, 255, 255))
    d.line([x_a, 103, x_b, 103], fill=(255, 255, 255))
    s_obj = rs * px_per_m; s_draw = max(8.0, min(40.0, s_obj)); exact = s_draw == s_obj
    draw_obj(d, kind, 90 - s_draw / 2, 188 if kind != "hair" else 188, s_draw if kind != "hair" else s_draw / 3, (220, 220, 240))
    if not exact: text(W, 180, 380, "(OBJECT NOT TO SCALE)", fill=INK2_T, align="c")
    ratio = lam / rs
    us = us_len(lam)
    text(W, 180, 168, "1 WAVE = " + fmt_len(lam) + (" · " + us if us else ""), fill=GOLD_T, align="c")
    rel = (f"{ratio:,.0f}× " if ratio >= 2 else (f"1/{1 / ratio:,.0f} OF " if ratio <= 0.5 else "≈ ")) + rname
    text(W, 180, 186, rel, fill=INK_T, align="c")
    caption(c, "ONE WAVELENGTH VS A KNOWN OBJECT", CYAN_T)

SCN = {"A": scene_A, "B": scene_B, "C": scene_C}
def scene(c, T):
    if T < ws.RT[0]:
        i = ws.I_BH if T < ws.HOOK_HI else ws.I_TOP; a = T - (ws.HOOK_LO if i == ws.I_BH else ws.HOOK_HI)
        SCN[VIS](c, i, T, a, ws.I_BH if i == ws.I_TOP else None)
    else:
        k = ws.rec_index(T); SCN[VIS](c, k, T, T - ws.RT[k], k - 1 if k > 0 else None)
ws.scene = scene

SHOTS = [ws.RT[ws.I_SPUT] + 0.35, ws.RT[ws.I_SPUT] + 1.0, ws.RT[ws.I_LIGO] + 1.2, ws.RT[ws.I_TOP] + 0.6,
         ws.RT[next(j for j, r in enumerate(REC) if "WHALE" in r["label"])] + 0.6, ws.RT[next(j for j, r in enumerate(REC) if "RONTGEN" in r["label"])] + 0.6]
def frame_at(T):
    idx = max(q for q, nm in enumerate(ws.NAMES) if ws.START[nm] <= T)
    return ws.render_frame(idx, T - ws.START[ws.NAMES[idx]])
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); anim = "--anim" in sys.argv
    for v in [a for a in sys.argv[2:] if not a.startswith("--")] or ["A", "B", "C"]:
        VIS = v
        for j, T in enumerate(SHOTS):
            Image.fromarray(frame_at(T)).resize((540, 960), Image.LANCZOS).save(f"{out}/{v}_{j}.png")
        if anim:                                                      # short clip: Sputnik -> next finds (camera moves)
            t0 = ws.RT[ws.I_SPUT] - 0.1; fr = []
            for q in range(int(4.2 * 12)):
                fr.append(Image.fromarray(frame_at(t0 + q / 12)).resize((432, 768), Image.LANCZOS))
            fr[0].save(f"{out}/{v}_clip.webp", save_all=True, append_images=fr[1:], duration=83, loop=0, quality=62, method=4)
        print(v, "ok")
