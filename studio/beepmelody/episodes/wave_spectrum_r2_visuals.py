"""BeepMelody · wave-spectrum · RETRAVAIL r1, step 3 (visuals) — 3 "funky 3D" looks for the SAME data.
Guillaume (15 Nov): "les visuels go funky 3d maybe?" ; sound chosen = C (synthwave 98 BPM, each wave its real note).
Rule kept in all three: faster wave = tighter crests on screen (cycles drawn = place on the log ruler), colour = band.
  A · OUTRUN   : neon perspective grid to a striped sun; the wave is a 3D ribbon flying over the road toward you.
  B · TUNNEL   : you fly through a tunnel of rings; one ring = one crest, so a fast wave = rings packed tight.
  C · TERRAIN  : a wireframe 3D sea that ripples at the wave's speed, seen in perspective (LIGO = space-time sheet).
HUD, banners, ruler and footer stay those of wave_spectrum.py (same data, same checks).
usage: python3 wave_spectrum_r2_visuals.py <out_dir> [A B C]
"""
import sys, os, math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wave_spectrum as ws
from wave_spectrum import AW, AH, REC, N, pos, mix

VIS = "A"
MAG = (255, 60, 200); CYN = (60, 240, 255); YEL = (255, 230, 90); VIO = (120, 60, 200); NIGHT = (14, 6, 34)

def proj(x, y, z, cx=90, cy=150, f=120):
    z = max(z, 0.05); return cx + f * x / z, cy + f * y / z

def cyc(i): return 1.5 + 9 * pos(i)                     # crests across the frame: slow wave = few, fast wave = many

# ---------- A · OUTRUN ----------
def scene_A(c, i, T, age):
    d = c.a; HZ = 150
    for y in range(AH):                                   # sky gradient night -> magenta at horizon
        u = min(1, max(0, y / HZ)); d.line([0, y, AW, y], fill=mix(NIGHT, (120, 20, 110), u ** 2.2) if y < HZ else (10, 4, 26))
    for (x, y, s) in ws.STARS:
        if y < HZ - 30: d.point((x, y), fill=[(70, 60, 120), (200, 190, 255), (120, 100, 180)][s])
    R = 34; cx = 90                                       # striped sun
    for yy in range(-R, 1):
        w = int(math.sqrt(R * R - yy * yy)); y = HZ - 6 + yy
        if yy > -R * 0.55 and (yy // 3) % 2 == 0 and yy > -R * 0.55 + (R + yy) * 0:
            if (int((yy + R) * 0.35 + T * 6)) % 3 == 0: continue
        d.line([cx - w, y, cx + w, y], fill=mix((255, 220, 80), MAG, (yy + R) / R))
    for k in range(-9, 10):                               # perspective grid
        x0, y0 = proj(k * 0.9, 1.0, 12, cy=HZ); x1, y1 = proj(k * 0.9, 1.0, 0.6, cy=HZ)
        d.line([x0, y0, x1, y1], fill=(200, 40, 190))
    sp = 0.8; off = (T * 3.2) % sp
    for k in range(18):
        z = 0.6 + k * sp - off
        if z < 0.6: continue
        _, y = proj(0, 1.0, z, cy=HZ); d.line([0, y, AW, y], fill=mix((10, 4, 26), (230, 60, 210), min(1, 2.2 / z)))
    col = ws.wave_col(i) if REC[i]["family"] == "light" else ws.FAMC[REC[i]["family"]]
    n = cyc(i); amp = 0.55 * (1 + 0.5 * math.exp(-age / 0.25))   # 3D ribbon: crests run toward the viewer
    for k in range(7, -1, -1):                            # the wave, drawn across the road, echoing back to the sun
        z = 1.7 + k * 0.9 - (T * 1.6) % 0.9; pts = []
        for q in range(121):
            x = -1.5 + 3.0 * q / 120
            pts.append(proj(x, 0.15 - 0.42 * amp * math.sin(2 * math.pi * n * q / 120 - T * 5 + k * 0.6), z, cy=HZ - 22))
        cl = mix((40, 8, 50), col, min(1, 2.0 / z)); w = 2 if k == 0 else 1
        for a_, b_ in zip(pts, pts[1:]): d.line([a_, b_], fill=cl, width=w)

# ---------- B · TUNNEL ----------
def scene_B(c, i, T, age):
    d = c.a; d.rectangle([0, 0, AW, AH], fill=(6, 4, 18)); cx, cy = 90, 156
    col = ws.wave_col(i) if REC[i]["family"] == "light" else ws.FAMC[REC[i]["family"]]
    gap = 2.4 / cyc(i)                                    # one ring = one crest: fast wave = rings packed tight
    off = (T * 2.2) % gap; z = 0.35 - off
    rings = []
    while z < 9:
        if z > 0.3: rings.append(z)
        z += gap
    for z in reversed(rings):
        r = 70 / z; wob = 3 * math.sin(T * 2 + z)
        ex, ey = cx + 18 * math.sin(T * 0.7 + z * 0.4) / z, cy + 10 * math.cos(T * 0.5 + z * 0.3) / z + wob / z
        shade = min(1, 1.8 / z)
        d.ellipse([ex - r, ey - r * 0.92, ex + r, ey + r * 0.92], outline=mix((6, 4, 18), col, shade), width=max(1, int(3 / z)))
    for a in range(0, 360, 30):                           # speed lines
        ang = math.radians(a + T * 20); r0, r1 = 20, 120
        d.line([cx + r0 * math.cos(ang), cy + r0 * math.sin(ang), cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)], fill=(30, 20, 60))
    if i == ws.I_LIGO:
        a = T * (2 + 8 * ws.ease(age / 1.8)); rr = 8 * (1 - 0.85 * ws.ease(age / 1.8))
        for s in (1, -1): d.ellipse([cx + s * rr * math.cos(a) - 3, cy + s * rr * math.sin(a) - 3, cx + s * rr * math.cos(a) + 3, cy + s * rr * math.sin(a) + 3], fill=(255, 255, 255))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=mix(col, (255, 255, 255), 0.6))

# ---------- C · TERRAIN ----------
def scene_C(c, i, T, age):
    d = c.a
    for y in range(AH): d.line([0, y, AW, y], fill=mix((4, 10, 30), (40, 10, 70), min(1, y / 230)))
    for (x, y, s) in ws.STARS:
        if y < 110: d.point((x, y), fill=[(50, 60, 110), (180, 200, 255), (90, 100, 160)][s])
    col = ws.wave_col(i) if REC[i]["family"] == "light" else ws.FAMC[REC[i]["family"]]
    n = cyc(i); amp = 0.45 * (1 + 0.6 * math.exp(-age / 0.3)); grav = REC[i]["family"] == "gravity"
    xs = np.linspace(-3.0, 3.0, 25); zs = np.linspace(1.6, 7.4, 20)
    def h(x, z):
        if grav:                                          # space-time sheet: rings out from the source
            r = math.hypot(x, z - 3.6); return amp * 1.2 * math.sin(r * 4 - T * 6) * math.exp(-r * 0.25) - (0.5 / (r + 0.4) if i == ws.I_LIGO else 0)
        return amp * math.sin(2 * math.pi * (1 + 4 * pos(i)) * (z - 1.6) / 5.8 * 1.5 - T * 5) * (0.7 + 0.3 * math.cos(x * 1.3))
    P = [[proj(x, 1.1 - h(x, z), z, cy=112, f=100) for x in xs] for z in zs]
    for zi in range(len(zs) - 1, -1, -1):
        sh = min(1, 2.6 / zs[zi]); cl = mix((20, 10, 50), col, sh)
        for xi in range(len(xs) - 1): d.line([P[zi][xi], P[zi][xi + 1]], fill=cl)
        if zi > 0:
            for xi in range(len(xs)): d.line([P[zi][xi], P[zi - 1][xi]], fill=mix((20, 10, 50), MAG, sh * 0.7))

SCN = {"A": scene_A, "B": scene_B, "C": scene_C}
def scene(c, T):
    k = ws.rec_index(T)
    if T < ws.RT[0]:
        i = ws.I_BH if T < ws.HOOK_HI else ws.I_TOP; a = T - (ws.HOOK_LO if i == ws.I_BH else ws.HOOK_HI)
    else: i, a = k, T - ws.RT[k]
    SCN[VIS](c, i, T, a)
ws.scene = scene

SHOTS = [("hook", ws.HOOK_HI + 0.6), ("t", ws.RT[ws.I_SPUT] + 0.6), ("t", ws.RT[ws.I_LIGO] + 1.2), ("t", ws.RT[ws.I_TOP] + 0.5)]
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for v in (sys.argv[2:] or ["A", "B", "C"]):
        VIS = v
        for j, (kind, T) in enumerate(SHOTS):
            idx = max(q for q, nm in enumerate(ws.NAMES) if ws.START[nm] <= T)
            fr = ws.render_frame(idx, T - ws.START[ws.NAMES[idx]])
            Image.fromarray(fr).resize((540, 960), Image.LANCZOS).save(f"{out}/{v}_{j}.png")
        print(v, "ok")
