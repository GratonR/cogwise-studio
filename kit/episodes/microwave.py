"""Cogwise episode: Why your leftovers are still frozen in the middle.
One idea: a microwave oven does NOT cook from the inside. Its 2.45 GHz waves are absorbed layer by layer, so they
only reach ~2-3 cm (about an inch) into food; deeper parts heat by conduction from that hot outer shell.
Frozen food is worse: ice absorbs microwaves far less than liquid water, so thawed edges grab the energy (runaway).

VIEW: front cross-section of a countertop microwave (door removed). Screen y grows DOWN.
Cavity on the left, magnetron in the right-hand compartment; a short waveguide feeds the cavity through the
RIGHT cavity wall (side-feed). A thick block of leftovers sits on a plate on the glass turntable, shown in section
with a heat map: hot outer shell (red/orange), frozen core (ice blue, crystals).
Scale of the food section: PEN = 80 px = 2.5 cm (~1 in) -> 32 px/cm; block 380 x 280 px = 11.9 x 8.75 cm.
Water dipole: O end is negative, H end positive -> the H side turns to point ALONG the electric field arrow.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="microwave",
    title="Why your leftovers are still frozen in the middle 🍲❄️ #Shorts",
    description=("Burning edges, frozen middle: microwaves only reach a few centimetres into your food.\n\n"
                 "#Shorts #howthingswork #microwave #kitchen #cogwise"),
    hashtags=["Shorts", "howthingswork", "microwave", "kitchen", "science", "cogwise"],
    sources=[
        "https://culinarylore.com/food-science:do-microwaves-cook-from-the-inside-out",
        "https://cyberphysics.co.uk/topics/heat/microwave_oven/microwave.htm",
        "https://www.todayifoundout.com/index.php/2010/10/microwaves-dont-cook-from-the-inside-out/",
    ],
)

BEATS = [
    dict(dur=4.4, title="FROZEN MIDDLE", caption="Burning edges, frozen middle. Your microwave isn't broken."),
    dict(dur=4.8, title="THE SECRET", caption="Its waves simply can't reach the center of your food."),
    dict(dur=5.4, title="1 · MAGNETRON", caption="A tube called a magnetron fires microwaves into the metal box."),
    dict(dur=7.6, title=None, caption="They flip water molecules back and forth billions of times a second, and that jiggling is heat.", card='water'),
    dict(dur=7.2, title="2 · THE CATCH", caption="But every layer of food absorbs some energy, so the waves fade as they go."),
    dict(dur=5.4, title="2 CM · 1 IN", caption="After two or three centimetres, about an inch, they're almost gone."),
    dict(dur=6.4, title=None, caption="Everything deeper heats the slow way: warmth creeping inward from the hot outer shell.", card='conduct'),
    dict(dur=5.0, title="3 · ICE", caption="Frozen food makes it worse: ice barely absorbs microwaves at all."),
    dict(dur=5.6, title="RUNAWAY EDGES", caption="So the thawed edges grab all the energy and keep getting hotter."),
    dict(dur=5.6, title="THIN VS THICK", caption="That's why a thin plate heats evenly, and a thick block doesn't."),
    dict(dur=8.2, title="THE SHELL", caption="Your microwave doesn't cook from the inside. It cooks the shell, and the shell cooks the rest."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
OV_X0, OV_X1, OV_Y0, OV_Y1 = 110, 970, 560, 1220      # oven body
CAV_X0, CAV_X1, CAV_Y0, CAV_Y1 = 150, 760, 610, 1170  # cooking cavity (metal box)
FX0, FX1, FY0, FY1 = 265, 645, 840, 1120              # food block section
FCX, FCY = (FX0 + FX1) / 2, (FY0 + FY1) / 2           # 455, 980
PEN = 80                                              # 2.5 cm reach, in px
MAG = (850, 690)                                      # magnetron centre
WG_Y0, WG_Y1 = 668, 712                               # waveguide opening in the right cavity wall

ICE = hexc('#a9d6ea'); ICE_D = hexc('#5f9fc0'); NEUTRAL = hexc('#e8dcc4'); DEEP = hexc('#a82516')
METAL = hexc('#d8d3c8'); METAL_D = hexc('#b5aea0'); GLASS = hexc('#bfe0dc')
O_COL = hexc('#e4472f'); H_COL = hexc('#fbf5e8')

def tcol(T):
    """heat-map colour: -1 ice, 0 neutral, 0.7 orange, 1.1 red, 1.6 deep red."""
    stops = [(-1.0, ICE), (-0.15, hexc('#cfe3e6')), (0.15, NEUTRAL), (0.7, ORANGE), (1.1, RED), (1.6, DEEP)]
    T = clamp(T, stops[0][0], stops[-1][0])
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if T <= t1: return lerpc(c0, c1, (T - t0) / (t1 - t0))
    return stops[-1][1]

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['edge_T'] = 1.1 + 0.4 * ease((t - B(8) - 0.2) / 2.5)
    s['spread'] = 1.0 + 0.35 * ease((t - B(10)) / 3.0)        # recap: heat front creeps a little further in
    s['oven'] = 1 - win(t, B(9) + 0.1, B(10) + 0.05, 0.5)      # oven view (off during thin vs thick)
    s['compare'] = win(t, B(9) + 0.1, B(10) + 0.05, 0.5)
    s['hotcold'] = bw(t, 0)
    s['enter'] = bw(t, 1)
    s['rays'] = max(bw(t, 2), 0.6 * bw(t, 3))
    s['mag'] = bw(t, 2)
    s['catch'] = bw(t, 4)
    s['reach'] = bw(t, 5)
    s['ice'] = bw(t, 7)
    s['runaway'] = bw(t, 8)
    s['recap'] = bw(t, 10)
    s['crystals'] = 1.0
    return s

# ---------------------------------------------------------------- food
def depth_T(d, s):
    """temperature at depth d (px from the nearest surface)."""
    Dh = 105 * s['spread']
    g = 1 - ease(d / Dh)
    return -1 + (s['edge_T'] + 1) * g

def draw_food_section(ctx, x0, y0, x1, y1, Tfun, a=1.0, crystals=0.0, t=0.0, seed=3):
    w, h = x1 - x0, y1 - y0
    step = 4
    n = int(min(w, h) / 2 / step) + 1
    for k in range(n):
        ins = k * step
        if 2 * ins >= min(w, h): break
        ctx.rectangle(x0 + ins, y0 + ins, w - 2 * ins, h - 2 * ins)
        setc(ctx, tcol(Tfun(ins + step / 2)), a); ctx.fill()
    if crystals > 0:
        rnd = random.Random(seed)
        for _ in range(22):
            cx = rnd.uniform(x0 + 20, x1 - 20); cy = rnd.uniform(y0 + 20, y1 - 20)
            d = min(cx - x0, x1 - cx, cy - y0, y1 - cy)
            T = Tfun(d)
            if T > -0.55: continue
            r = rnd.uniform(7, 12)
            for k in range(3):
                ang = k * math.pi / 3 + rnd.uniform(0, 1)
                ctx.move_to(cx - r * math.cos(ang), cy - r * math.sin(ang)); ctx.line_to(cx + r * math.cos(ang), cy + r * math.sin(ang))
            setc(ctx, WHITE, a * crystals * 0.95); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(x0, y0, w, h); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()

def decaying_wave(ctx, p_out, p_surf, depth, t, a, col=INK, amp=16, wl=40, lw=5, decay=PEN / 2.3, ice=False):
    """wave travelling from p_out to the food surface p_surf, then `depth` px inside with exponential fade."""
    if a <= 0: return
    (x0, y0), (x1, y1) = p_out, p_surf
    Lo = math.dist(p_out, p_surf); L = Lo + depth
    ang = math.atan2(y1 - y0, x1 - x0)
    ctx.save(); ctx.translate(x0, y0); ctx.rotate(ang)
    N = 120; prev = None
    for i in range(N + 1):
        sx = L * i / N
        din = max(0.0, sx - Lo)
        k = math.exp(-din / decay) if not ice else 1.0
        y = amp * k * math.sin(2 * math.pi * sx / wl - t * 9)
        if prev is not None:
            ctx.move_to(*prev); ctx.line_to(sx, y)
            setc(ctx, col, a * (0.45 + 0.55 * k)); ctx.set_line_width(lw * (0.6 + 0.4 * k)); ctx.stroke()
        prev = (sx, y)
    ctx.restore()

# ---------------------------------------------------------------- oven
def draw_oven(ctx, t, s):
    # feet + body
    for fx in (170, 910):
        rrect(ctx, fx - 30, OV_Y1 - 6, 60, 26, 6); fill_stroke(ctx, INK2, lw=3)
    rrect(ctx, OV_X0, OV_Y0, OV_X1 - OV_X0, OV_Y1 - OV_Y0, 18); fill_stroke(ctx, FILL2, lw=6)
    # cavity (metal box)
    ctx.rectangle(CAV_X0, CAV_Y0, CAV_X1 - CAV_X0, CAV_Y1 - CAV_Y0); fill_stroke(ctx, METAL, lw=6)
    # control compartment
    ctx.rectangle(780, 600, 170, 580); fill_stroke(ctx, FILL3, lw=4)
    # display + dial
    rrect(ctx, 815, 830, 100, 46, 6); fill_stroke(ctx, INK, lw=3)
    text_c(ctx, "1:30", 865, 864, 26, MUSTARD, True, 1)
    ctx.arc(865, 960, 34, 0, 2 * math.pi); fill_stroke(ctx, PAPER, lw=4)
    ctx.move_to(865, 960); ctx.line_to(865 + 26 * math.cos(-1.1 + t * 0.4), 960 + 26 * math.sin(-1.1 + t * 0.4)); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    for i in range(3):
        rrect(ctx, 820, 1030 + i * 42, 90, 28, 6); fill_stroke(ctx, PAPER, lw=3)
    # waveguide: duct from the magnetron to the opening in the right cavity wall
    ctx.rectangle(CAV_X1 - 3, WG_Y0, MAG[0] - CAV_X1 - 20, WG_Y1 - WG_Y0); fill_stroke(ctx, METAL_D, lw=4)
    ctx.move_to(CAV_X1, WG_Y0 + 3); ctx.line_to(CAV_X1, WG_Y1 - 3); setc(ctx, METAL_D); ctx.set_line_width(8); ctx.stroke()
    # magnetron: cylinder with cooling fins + antenna into the waveguide
    mx, my = MAG
    for i in range(7):
        ctx.rectangle(mx - 52, my - 54 + i * 17, 104, 8); fill_stroke(ctx, METAL, lw=2.5)
    rrect(ctx, mx - 34, my - 62, 68, 124, 10); fill_stroke(ctx, hexc('#9b8a6d'), lw=4)
    ctx.arc(mx, my, 20, 0, 2 * math.pi); fill_stroke(ctx, MUSTARD, lw=3)
    ctx.move_to(mx - 34, my); ctx.line_to(mx - 58, my); setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()
    # turntable glass + plate
    rrect(ctx, 215, 1134, 480, 14, 7); fill_stroke(ctx, GLASS, lw=3)
    for rx in (300, 610):
        ctx.arc(rx, 1158, 9, 0, 2 * math.pi); fill_stroke(ctx, INK2, lw=2)
    rrect(ctx, 235, FY1, 440, 14, 7); fill_stroke(ctx, WHITE, lw=4)

def draw_rays(ctx, t, s):
    a = s['rays']
    if a <= 0: return
    # wave packets: out of the waveguide, bounce off the left wall and the ceiling, into the food
    segs = [((CAV_X1 - 10, 690), (CAV_X0 + 12, 690)),
            ((CAV_X0 + 14, 700), (FX0 - 6, FCY - 40)),
            ((CAV_X1 - 30, 700), (600, CAV_Y0 + 12)),
            ((600, CAV_Y0 + 14), (530, FY0 - 6)),
            ((CAV_X1 - 14, 720), (FX1 + 6, FCY))]
    for i, (p, q) in enumerate(segs):
        wavy_arrow(ctx, *p, *q, t, INK2, a * 0.85, amp=9, wl=34, lw=4, head=12)
    # bounce marks
    for (bx, by) in ((CAV_X0 + 10, 692), (600, CAV_Y0 + 10)):
        ctx.arc(bx, by, 10 + 4 * math.sin(t * 8), 0, 2 * math.pi); setc(ctx, MUSTARD, a); ctx.set_line_width(3); ctx.stroke()

def draw_food(ctx, t, s):
    draw_food_section(ctx, FX0, FY0, FX1, FY1, lambda d: depth_T(d, s), 1.0, s['crystals'], t)
    # beat 2: waves enter from 3 sides and die out before the centre
    a = s['enter']
    if a > 0:
        decaying_wave(ctx, (FX0 - 150, FCY), (FX0, FCY), 140, t, a)
        decaying_wave(ctx, (FX1 + 150, FCY), (FX1, FCY), 140, t, a)
        decaying_wave(ctx, (FCX, FY0 - 170), (FCX, FY0), 140, t, a)
        tag(ctx, "WAVES FADE BEFORE THE CENTER", FCX, 1205, INK, a, 22)
    # beat 5: one wave entering from the left, layer by layer
    a = s['catch']
    if a > 0:
        for k in range(1, 6):
            xx = FX0 + k * 22
            ctx.move_to(xx, FCY - 60); ctx.line_to(xx, FCY + 60); setc(ctx, INK, a * 0.8); ctx.set_dash([6, 6]); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
        decaying_wave(ctx, (FX0 - 200, FCY), (FX0, FCY), 230, t, a, amp=30, wl=44, lw=6)
        tag(ctx, "EACH LAYER TAKES ITS SHARE", FCX, 1205, INK, a, 22)
    # beat 6: reach line 2-3 cm inside every face + ruler
    a = s['reach']
    if a > 0:
        ctx.rectangle(FX0 + PEN, FY0 + PEN, FX1 - FX0 - 2 * PEN, FY1 - FY0 - 2 * PEN)
        setc(ctx, INK, a); ctx.set_dash([10, 7]); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
        rx = FX1 + 40
        ctx.rectangle(rx, FY0, 30, PEN); fill_stroke(ctx, hexc('#f2e2b0'), lw=3, alpha=a)
        for i in range(0, PEN + 1, 8):
            ctx.move_to(rx, FY0 + i); ctx.line_to(rx + (14 if i % 32 == 0 else 8), FY0 + i)
        setc(ctx, INK, a); ctx.set_line_width(2); ctx.stroke()
        ctx.move_to(FX1, FY0 + PEN); ctx.line_to(rx + 30, FY0 + PEN); setc(ctx, INK, a); ctx.set_dash([5, 5]); ctx.set_line_width(2); ctx.stroke(); ctx.set_dash([])
        tag(ctx, "2–3 cm · ~1 in", FX1 + 20, FY0 - 40, INK, a, 22)
        tag(ctx, "NOT REACHED", FCX, FCY, ICE_D, a, 20)
    # beat 9: steam over the runaway edges
    a = s['runaway']
    if a > 0:
        for i in range(6):
            u = (t * 0.6 + i / 6) % 1
            x = FX0 + 30 + i * 64 + 10 * math.sin(t * 3 + i)
            y = FY0 - 10 - u * 120
            ctx.arc(x, y, 7 + 6 * u, 0, 2 * math.pi); setc(ctx, WHITE, a * (1 - u) * 0.9); ctx.fill_preserve()
            setc(ctx, INK2, a * (1 - u) * 0.6); ctx.set_line_width(2); ctx.stroke()
    # recap
    a = s['recap']
    if a > 0:
        # conduction arrows creeping inward from the shell
        u = (t * 0.25) % 1
        for (px, py, dx, dy) in ((FX0 + 50, FCY, 1, 0), (FX1 - 50, FCY, -1, 0), (FCX, FY0 + 50, 0, 1), (FCX, FY1 - 50, 0, -1),
                                 (FX0 + 50, FCY - 70, 1, 0), (FX1 - 50, FCY + 70, -1, 0)):
            o = 18 * u
            straight_arrow(ctx, px + dx * o, py + dy * o, px + dx * (o + 40), py + dy * (o + 40), INK, a * 0.9, lw=5, head=9)
        tag(ctx, "2 · HOT SHELL", FX0 + 80, FY0 - 30, RED, a, 20)
        tag(ctx, "3 · CONDUCTION", FCX, 1205, INK, a, 22)

def draw_compare(ctx, t, a):
    if a <= 0: return
    # thin plate: whole depth within reach -> even
    tx0, tx1, ty0, ty1 = 110, 470, 990, 1070
    rrect(ctx, tx0 - 20, ty1, tx1 - tx0 + 40, 14, 7); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    draw_food_section(ctx, tx0, ty0, tx1, ty1, lambda d: 0.85, a)
    # thick block: same reach, frozen core
    kx0, kx1, ky0, ky1 = 570, 950, 790, 1070
    rrect(ctx, kx0 - 20, ky1, kx1 - kx0 + 40, 14, 7); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    draw_food_section(ctx, kx0, ky0, kx1, ky1, lambda d: -1 + 2.1 * (1 - ease(d / 105)), a, 1.0 * a, t)
    for (x0, y0, x1, y1) in ((kx0, ky0, kx1, ky1),):
        ctx.rectangle(x0 + PEN, y0 + PEN, x1 - x0 - 2 * PEN, y1 - y0 - 2 * PEN)
        setc(ctx, INK, a); ctx.set_dash([10, 7]); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    tag(ctx, "THIN · EVEN", (tx0 + tx1) / 2, 1140, ORANGE, a, 24)
    tag(ctx, "THICK · FROZEN CORE", (kx0 + kx1) / 2, 1140, ICE_D, a, 24)
    tag(ctx, "SAME 2–3 cm REACH", 540, 700, INK, a, 22)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    ov = s['oven']
    if ov > 0:
        ctx.push_group()
        draw_oven(ctx, t, s)
        draw_rays(ctx, t, s)
        draw_food(ctx, t, s)
        a = s['mag']
        if a > 0:
            highlight(ctx, MAG[0], MAG[1], 90, 95, RED, a, t)
            tag(ctx, "1 · MAGNETRON", MAG[0] - 20, 540, RED, a, 22)
        a = s['recap']
        if a > 0: tag(ctx, "1 · MAGNETRON", MAG[0] - 20, 540, INK, a, 20)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(ov)
    draw_compare(ctx, t, s['compare'])

# camera: start close on the food (answer visible at once), wide for the magnetron, close again for the layers
FOOD = (FCX, 985, 1.45)
CAMKEYS = [(0, *FOOD),
           (B(2), 540, 880, 0.98),
           (B(4), FCX - 40, 985, 1.4),
           (B(5), FCX + 40, 985, 1.4),
           (B(7), *FOOD),
           (B(8), FCX, 960, 1.3),
           (B(9), 530, 950, 1.2),
           (B(10), 540, 880, 0.98)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)
ANCHOR = (540, 1300)

def molecule(ctx, x, y, ang, r, a):
    """water molecule: O (red, -) at centre, two H (cream, +) on the side the angle points to."""
    for k in (-1, 1):
        hx = x + r * 1.05 * math.cos(ang + k * 0.91); hy = y + r * 1.05 * math.sin(ang + k * 0.91)
        ctx.arc(hx, hy, r * 0.55, 0, 2 * math.pi); fill_stroke(ctx, H_COL, lw=3, alpha=a)
    ctx.arc(x, y, r, 0, 2 * math.pi); fill_stroke(ctx, O_COL, lw=3, alpha=a)

def draw_hud(ctx, t, E):
    a = bw(t, 0, 2)
    if a > 0:
        hud(ctx, "EDGES", "85 °C", "185 °F", a, RED, x=60, y=196, w=300)
        hud(ctx, "CENTER", "−4 °C", "25 °F", a, ICE_D, x=720, y=196, w=300)
    a = bw(t, 5)
    if a > 0: hud(ctx, "MICROWAVES REACH", "2–3 cm", "≈ 1 in deep", a, MUSTARD, x=300, y=196, w=480)
    # beat 8: magnifier, water spins vs ice locked
    a = bw(t, 7)
    if a > 0:
        f = math.sin(2 * math.pi * 1.1 * t); sg = 1 if f >= 0 else -1
        for (cx, label, locked) in ((300, "WATER: SPINS", False), (780, "ICE: LOCKED", True)):
            cy, r = 400, 150
            ctx.arc(cx, cy, r, 0, 2 * math.pi); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
            setc(ctx, INK, a); ctx.set_line_width(7); ctx.stroke()
            ctx.save(); ctx.arc(cx, cy, r - 4, 0, 2 * math.pi); ctx.clip()
            if locked:
                ctx.rectangle(cx - r, cy - r, 2 * r, 2 * r); setc(ctx, ICE, 0.5 * a); ctx.fill()
            rnd = random.Random(7)
            for i in range(3):
                for j in range(3):
                    x = cx - 80 + i * 80; y = cy - 70 + j * 70
                    if locked:
                        ang = (i + j) % 2 * math.pi + math.pi / 2 + 0.06 * f
                    else:
                        tgt = 0 if sg > 0 else math.pi
                        ang = tgt + 0.5 * math.sin(t * 7 + i * 2 + j) + rnd.uniform(-0.3, 0.3)
                    molecule(ctx, x, y, ang, 16, a)
            ctx.restore()
            text_c(ctx, label, cx, cy + r + 44, 26, ICE_D if locked else RED, True, 1.5, a)
        straight_arrow(ctx, 540 - 60 * sg, 250, 540 + 60 * sg, 250, MUSTARD, a, lw=8, head=13)
        text_c(ctx, "FIELD", 540, 300, 22, INK, True, 1.5, a)
    a = bw(t, 8)
    if a > 0:
        k = ease((t - B(8)) / 3.0)
        e = 70 + 30 * k
        hud(ctx, "EDGES", f"{e:.0f} °C", f"{e * 9 / 5 + 32:.0f} °F", a, RED, flash=0.4 * k, x=60, y=196, w=300)
        hud(ctx, "CENTER", "−4 °C", "25 °F", a, ICE_D, x=720, y=196, w=300)

SFX = [(0.3, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.3, 'pop'), (B(4) + 0.3, 'pop'), (B(5) + 0.3, 'pop'),
       (B(7) + 0.3, 'pop'), (B(8) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_water(ctx, t, lt, a):
    card_frame(ctx, "WATER MOLECULES", a, "2.45 GHz · 2.45 BILLION CYCLES / s", RED)
    f = math.sin(2 * math.pi * 0.9 * t); sg = 1 if f >= 0 else -1
    col = TEAL if sg > 0 else RED
    # field arrow: flips sign; H side (+) of each molecule turns to point along it
    if sg > 0: straight_arrow(ctx, 330, 280, 750, 280, col, a, lw=7, head=14)
    else: straight_arrow(ctx, 750, 280, 330, 280, col, a, lw=7, head=14)
    text_c(ctx, "FIELD FLIPS", 880, 290, 20, col, True, 1, a)
    tgt = 0 if sg > 0 else math.pi
    for i in range(5):
        x = 230 + i * 155; y = 420 + (i % 2) * 40
        # the molecule lags slightly behind the flip (that friction = heat)
        ang = tgt + 0.35 * math.sin(t * 9 + i)
        molecule(ctx, x, y, ang, 24, a)
        # jiggle marks
        for k in (-1, 1):
            ctx.arc(x, y, 46, -0.5 + k * 1.6, 0.0 + k * 1.6); setc(ctx, ORANGE, a * 0.7); ctx.set_line_width(3); ctx.stroke()
    text_c(ctx, "− O", 150, 520, 18, O_COL, True, 1, a)
    text_c(ctx, "H +", 150, 545, 18, INK2, True, 1, a)

def card_conduct(ctx, t, lt, a):
    card_frame(ctx, "THE SLOW WAY", a, "HEAT CREEPS IN · CONDUCTION", ORANGE)
    x0, y0, x1, y1 = 340, 260, 740, 540
    grow = 1 + 0.3 * ease(lt / 5.0)
    draw_food_section(ctx, x0, y0, x1, y1, lambda d: -1 + 2.1 * (1 - ease(d / (95 * grow))), a, a, t, seed=5)
    ctx.rectangle(x0 + 60, y0 + 60, x1 - x0 - 120, y1 - y0 - 120); setc(ctx, INK, a); ctx.set_dash([8, 6]); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    u = (lt * 0.3) % 1
    for (px, py, dx, dy) in ((x0 + 40, 400, 1, 0), (x1 - 40, 400, -1, 0), (540, y0 + 35, 0, 1), (540, y1 - 35, 0, -1)):
        o = 22 * u
        straight_arrow(ctx, px + dx * o, py + dy * o, px + dx * (o + 46), py + dy * (o + 46), INK, a, lw=5, head=9)
    text_c(ctx, "HOT SHELL", 215, 330, 20, RED, True, 1, a)
    text_c(ctx, "(MICROWAVES)", 215, 356, 16, INK2, True, 1, a)
    text_c(ctx, "COLD CORE", 870, 330, 20, ICE_D, True, 1, a)
    text_c(ctx, "(NO WAVES)", 870, 356, 16, INK2, True, 1, a)

CARDS = {'water': card_water, 'conduct': card_conduct}
