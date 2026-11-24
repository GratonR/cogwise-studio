"""Mockups r1 (visual rework « les cigales peuvent être plus mignonnes ») for cicadas-13-17.
3 cute-cicada directions, same data / music / timing / HUD. Only the insects change.
python3 cicadas_r1_mock.py <out_dir>"""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cicadas as M
from cicadas import (AW, HZ, YSOIL, T0, T_RW, PER, COL, COL2, EMERG, Y1Y, Y0Y, tyr, year_f, last_emerg,
                     lerp, ease, mixc, INK)

WING, WING2 = (246, 250, 255), (196, 214, 236)
HI, BLUSH = (255, 255, 255), (255, 150, 160)

def put(d, x, y, rows, pal, s=1):
    x, y = int(round(x)), int(round(y))
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != "." and ch in pal:
                if s == 1: d.point((x + i, y + j), fill=pal[ch])
                else: d.rectangle([x + i * s, y + j * s, x + i * s + s - 1, y + j * s + s - 1], fill=pal[ch])

# ---------- sprites (front view, flapping) ----------
CHIBI = [
    ["WW.....WW", "WwW...WwW", ".WBBBBBW.", ".BBBBBBB.", "BKHBBBKHB", "BBBBDBBBB", ".BBBBBBB.", "..D...D.."],
    [".........", ".........", "WWBBBBBWW", "wBBBBBBBw", "BKHBBBKHB", "BBBBDBBBB", ".BBBBBBB.", "..D...D.."],
]
KAWAII = [
    ["WWW.....WWW", "WwwW...WwwW", ".WwWBBBWwW.", "..BBBBBBB..", ".BBBBBBBBB.", "BKKBBBBBKKB", "BKHBBBBBKHB", "BPPBBDBBPPB",
     ".BBBBBBBBB.", "..BD...DB.."],
    ["...........", "...........", "WW.BBBBB.WW", "WwWBBBBBWwW", "wBBBBBBBBBw", "BKKBBBBBKKB", "BKHBBBBBKHB", "BPPBBDBBPPB",
     ".BBBBBBBBB.", "..BD...DB.."],
]
NOTE = ["..KK", "..KK", "..K.", "KKK.", "KKK."]
GRUB = ["..BBB.", ".BBBBB", "BKHBBB", "BBBBBB", ".D.D.."]

def pal(b, extra=None):
    p = {"B": COL[b], "D": COL2[b], "K": INK, "H": HI, "W": WING, "w": WING2, "P": BLUSH}
    if extra: p.update(extra)
    return p

# ---------- generic swarm with a sprite ----------
def make_swarm(frames, n_scale, notes=False):
    sw, sh = len(frames[0][0]), len(frames[0])
    def swarm(img, T, b, te, n=36, life=2.6):
        a_ = T - te
        if a_ < 0 or a_ > life: return
        d = ImageDraw.Draw(img); rnd = random.Random(hash((b, te)) % 99991)
        n = max(4, int(n * n_scale))
        for k in range(n):
            sx = rnd.uniform(6, 86 - sw) if b == "XIX" else rnd.uniform(94, 174 - sw)
            tx = sx + rnd.uniform(-22, 22); ty = rnd.uniform(30, HZ - sh - 6)
            tx = max(2, min(AW - sw - 2, tx))
            dl = rnd.uniform(0, 0.35); f = ease(min(1, max(0, (a_ - dl) / 0.7)))
            if a_ < dl: continue
            if a_ > life - 0.6 and rnd.random() < (a_ - (life - 0.6)) / 0.6: continue
            x = sx + (tx - sx) * f + 1.5 * math.sin(a_ * 6 + k); y = HZ + (ty - HZ) * f + 1.2 * math.cos(a_ * 7 + k)
            fr = frames[int(a_ * 16 + k) % 2]
            put(d, x, y, fr, pal(b))
            if notes and k % 3 == 0 and 0.4 < a_ < 2.0:
                ny = y - 7 - (a_ - 0.4) * 6; put(d, x + sw - 2, ny, NOTE, {"K": COL2[b]})
    return swarm

# ---------- cute nymphs underground ----------
def draw_scene_cute(img, T):
    saved = M.NYMPH; M.NYMPH = {"XIX": [], "XIII": []}
    img = ORIG_SCENE(img, T); M.NYMPH = saved
    d = ImageDraw.Draw(img); yf = year_f(T)
    for b in ("XIX", "XIII"):
        if T < T0: prog = 0.0 if T >= T_RW else 1.0
        else:
            le = last_emerg(b, int(yf + 1e-6)); prog = (yf - le) / PER[b]
        for j, (x, o) in enumerate(saved[b][::2]):
            y = int(lerp(YSOIL - 12 - o, HZ + 8 + o // 3, prog ** 1.4))
            put(d, min(x, AW - 8) if b == "XIII" else min(x, 82), y, GRUB, pal(b))
    return img

# ---------- variant C: two big mascots on the grass ----------
MASCOT = [
    "....WWW.........WWW....",
    "...WwwwW.......WwwwW...",
    "..WwwwwwW.....WwwwwwW..",
    "..WwwwwwwW...WwwwwwwW..",
    "...WwwwwwWBBBWwwwwwW...",
    "....WWwwBBBBBBBwwWW....",
    "......BBBBBBBBBBB......",
    ".....BBBBBBBBBBBBB.....",
    "....BBKKKBBBBBKKKBB....",
    "....BKKHKBBBBBKKHKB....",
    "....BKKKKBBBBBKKKKB....",
    "....BPPBBBBBBBBBPPB....",
    "....BBBBBBMMMBBBBBB....",
    ".....BBBBBBMBBBBBB.....",
    "......BBBBBBBBBBB......",
    ".......BDDDDDDDB.......",
    "......D..D...D..D......",
]
def mascot_rows(awake, sing):
    rows = [r for r in MASCOT]
    if not awake:   # eyes closed, wings folded down
        rows = [r.replace("W", ".").replace("w", ".") for r in rows[:5]] + rows[5:]
        rows[5] = "....WWwwBBBBBBBwwWW...."
        rows[8] = "....BBBBBBBBBBBBBBB...."; rows[9] = "....BKKKKBBBBBKKKKB...."; rows[10] = "....BBBBBBBBBBBBBBB...."
        rows[12] = "....BBBBBBBDBBBBBBB...."; rows[13] = ".....BBBBBBBBBBBBB....."
    elif not sing:
        rows[12] = "....BBBBBBDDDBBBBBB...."; rows[13] = ".....BBBBBBBBBBBBB....."
    return rows

def mascots(img, T):
    d = ImageDraw.Draw(img); yf = year_f(T)
    for b, x in (("XIX", 0), ("XIII", AW - 46)):
        if T < T0: out_age = 0.5 if T < T_RW else 9
        else:
            yi = int(yf + 1e-6); le = last_emerg(b, yi)
            out_age = T - tyr(le) if yi - le == 0 or (T - tyr(le)) < 2.4 else 9
        awake = out_age < 2.4 or T < T_RW; sing = awake and int(T * 8) % 2 == 0
        bob = -2 if awake and int(T * 8) % 2 else 0
        put(d, x, HZ - 33 + bob, mascot_rows(awake, sing),
            {"B": COL[b], "D": COL2[b], "K": INK, "H": HI, "W": WING, "w": WING2, "P": BLUSH, "M": (120, 40, 50)}, 2)
        if not awake and int(T * 2) % 2 == 0:
            ImageDraw.Draw(img); put(d, x + 36, HZ - 44 - (T * 3) % 4, ["KKK", "..K", ".K.", "KKK"], {"K": M.INK2})
        if awake and sing:
            put(d, x + (34 if b == "XIX" else 2), HZ - 48 - (T * 10) % 6, NOTE, {"K": COL2[b]})

ORIG_SCENE = M.draw_scene; ORIG_SWARM = M.swarm
VARIANTS = {
    "A": dict(swarm=make_swarm(CHIBI, 0.45), scene=draw_scene_cute, extra=None),
    "B": dict(swarm=make_swarm(KAWAII, 0.30, notes=True), scene=draw_scene_cute, extra=None),
    "C": dict(swarm=make_swarm(CHIBI, 0.30), scene=draw_scene_cute, extra=mascots),
    "orig": dict(swarm=ORIG_SWARM, scene=ORIG_SCENE, extra=None),
}
def use(v):
    cfg = VARIANTS[v]; M.swarm = cfg["swarm"]
    if cfg["extra"]:
        sc = cfg["scene"]; ex = cfg["extra"]
        def scene(img, T): img = sc(img, T); ex(img, T); return img
        M.draw_scene = scene
    else: M.draw_scene = cfg["scene"]

def at(T):
    for k, n in enumerate(M.NAMES):
        if M.CUTS[k] <= T < M.CUTS[k + 1]: return M.render_frame(k, T - M.START[n])
    return M.render_frame(len(M.NAMES) - 1, T - M.START["outro"] - 1e-3)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    MOM = {"intro": 1.6, "1854": tyr(1854) + 0.9, "1855": tyr(1855) + 0.9, "drop": M.T_DROP + 1.3, "under": tyr(1960)}
    for v in VARIANTS:
        use(v)
        for k, T in MOM.items():
            Image.fromarray(at(T)).save(os.path.join(out, f"{v}_{k}.png"))
    print("ok")
