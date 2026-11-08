"""Cogwise episode: The first steam engine was pushed by air (Newcomen atmospheric engine, 1712).
SIDE VIEW. Screen coordinates: x grows RIGHT, y grows DOWN.
Physics: steam fills an OPEN-TOP cylinder under the piston (the heavy pump rods pull the beam's right end
DOWN, so the left end and the piston go UP). A cold-water jet condenses the steam -> vacuum under the piston.
Atmospheric pressure on the open top pushes the piston DOWN -> left end of the beam DOWN, right end UP
-> pump rod UP -> water lifted out of the mine shaft. Steam never pushes; air does the work.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="steam-engine-invented",
    title="The first steam engine was pushed by air 💨",
    description=("The first working steam engine didn't push with steam: steam made a vacuum, and the air did the work.\n\n"
                 "#Shorts #howthingswork #steamengine #history #engineering #cogwise"),
    hashtags=["Shorts", "howthingswork", "steamengine", "history", "engineering", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Newcomen_atmospheric_engine",
        "https://collection.sciencemuseumgroup.org.uk/objects/co50900/newcomen-atmospheric-engine-atmospheric-steam-engine",
        "https://www.asme.org/wwwasmeorg/media/ResourceFiles/AboutASME/Who We Are/Engineering History/Landmarks/70-Newcomen-Engine.pdf",
        "https://www.britannica.com/biography/Thomas-Newcomen",
    ],
)

BEATS = [
    dict(dur=5.2, title="THE FIRST STEAM ENGINE", caption="The first working steam engine didn't run on steam. It ran on air."),
    dict(dur=4.4, title="THE TRICK", caption="The trick? Steam only fills the cylinder. Then you cool it."),
    dict(dur=4.2, title="A VACUUM", caption="It collapses into a few drops of water, leaving a vacuum."),
    dict(dur=3.8, title="AIR PUSHES", caption="Now the air outside shoves the piston down. Hard."),
    dict(dur=4.2, title=None, caption="First, low-pressure steam fills the cylinder as the piston rises."),
    dict(dur=4.4, title=None, caption="Then a jet of cold water condenses the steam in an instant."),
    dict(dur=4.2, title="3 · AIR STROKE", caption="The air slams the piston down and rocks a giant beam."),
    dict(dur=3.6, title=None, caption="That beam pumps water out of flooded mines."),
    dict(dur=7.0, title=None, caption="Air presses about one kilo on every square centimetre: on this piston, two tonnes. Forty-four hundred pounds.", card='force'),
    dict(dur=4.4, title="RECAP", caption="Newcomen, 1712. Steam makes the vacuum. Air does the work."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.3):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

ANCHOR = (540, 1500)

# ---------------------------------------------------------------- palette extras
WOOD = hexc('#b07a42'); WOOD_D = hexc('#7d5228')
BRICK = hexc('#c9876a'); BRICK_D = hexc('#a5654b')
IRON = hexc('#8f969c'); IRON_D = hexc('#5f666c'); IRON_L = hexc('#c9ced3')
COPPER = hexc('#d29b62'); COPPER_D = hexc('#a8703c')
STEAM = hexc('#e9eef0'); WATER = hexc('#4a90c8'); WATER_D = hexc('#2f6c9e')
AIR = RED

# ---------------------------------------------------------------- geometry (screen: y DOWN)
PIV = (620, 470)                  # beam pivot (on top of the brick pier)
RL, RR = 320, 310                 # arch-head radii, left (cylinder) / right (pump)
AMAX = 0.281                      # beam swing (rad); positive = clockwise on screen = LEFT end UP
CX = PIV[0] - RL                  # 300: cylinder axis (left chain hangs vertically here)
PX = PIV[0] + RR                  # 930: pump-rod axis
CYL_X0, CYL_X1 = 210, 390         # cylinder outer walls (wall 20 px)
CYL_TOP, CYL_BOT = 700, 1080      # OPEN top at 700, bottom plate at 1080
P_TOP0, TRAVEL, P_H = 760, 180, 28  # piston top y at s=0 (up) .. +TRAVEL at s=1 (down)
BOIL = (170, 430, 1180, 1400)     # haystack boiler x0, x1, top, bottom
CIST = (55, 195, 600, 668)        # injection cistern
INJ_X = 125                       # injection pipe x
SHAFT = (890, 970, 900)           # mine shaft x0, x1, top y
SPOUT_Y = 975
TROUGH = (740, 880, 1095, 1135)

def beam_angle(s):
    return AMAX * (1 - 2 * s)     # s=0 -> left end up (a>0), s=1 -> left end down (a<0)

def piston_y(s):
    return P_TOP0 + TRAVEL * s

def pump_rod_top(s):
    return 647 + RR * beam_angle(s)   # right side DOWN when a>0 (piston up), UP when piston down

# ---------------------------------------------------------------- tracks
def track(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]

T_CYC = B(7) + 0.2      # from here the engine runs on its own cycle
PERIOD = 3.4

def cycle(t):
    """One stroke: steam in (piston up) -> cold jet (condense) -> air stroke (piston down) -> rest."""
    u = ((t - T_CYC) / PERIOD) % 1.0
    c = {}
    c['s'] = track(u, [(0, 1), (0.05, 1), (0.38, 0), (0.55, 0), (0.85, 1), (1, 1)])
    c['steam'] = track(u, [(0, 0), (0.05, 0), (0.15, 1), (0.42, 1), (0.53, 0), (1, 0)])
    c['valve'] = win(u, 0.04, 0.40, 0.04)
    c['jet'] = win(u, 0.40, 0.53, 0.03)
    c['cold'] = track(u, [(0, 0), (0.40, 0), (0.46, 1), (0.70, 1), (0.95, 0), (1, 0)])
    c['arrows'] = win(u, 0.52, 0.92, 0.05)
    c['drops'] = track(u, [(0, 1), (0.08, 0), (0.42, 0), (0.55, 1), (1, 1)])
    return c

def manual(t):
    c = {}
    c['s'] = track(t, [(0, 0), (0.55, 0), (1.7, 1), (5.6, 1), (7.6, 0), (12.6, 0), (13.6, 0.06), (14.0, 0.06),
                       (15.2, 1), (B(4) + 0.6, 1), (B(5) - 1.0, 0), (B(6) - 0.8, 0), (B(6) + 0.6, 1), (T_CYC, 1)])
    c['steam'] = track(t, [(0, 0.85), (0.25, 0.85), (0.75, 0), (5.5, 0), (6.4, 1), (9.8, 1), (11.0, 0),
                           (B(4) + 0.3, 0), (B(4) + 1.2, 1), (B(5) + 0.5, 1), (B(5) + 1.5, 0), (T_CYC, 0)])
    c['cold'] = track(t, [(0, 0), (0.2, 0), (0.45, 0.9), (1.6, 0.9), (2.8, 0), (8.3, 0), (8.9, 1), (B(3), 1),
                          (B(3) + 1.6, 0), (B(5) + 0.3, 0), (B(5) + 0.8, 1), (B(6) + 0.6, 1), (B(6) + 2.0, 0), (T_CYC, 0)])
    c['jet'] = win(t, 0.12, 0.75, 0.1) + win(t, 8.4, 9.9, 0.2) + win(t, B(5) + 0.3, B(5) + 1.7, 0.2)
    c['valve'] = win(t, 5.3, 7.8, 0.2) + win(t, B(4) + 0.2, B(5) - 0.8, 0.2)
    c['arrows'] = win(t, 0.35, 3.8, 0.25) + win(t, B(3) + 0.05, B(4) - 0.2, 0.3) + win(t, B(6) - 0.9, B(7) - 0.2, 0.3)
    c['drops'] = track(t, [(0, 0), (0.5, 0), (0.9, 0.6), (5.4, 0.6), (6.0, 0), (10.0, 0), (11.2, 1),
                           (B(4) + 0.2, 1), (B(4) + 1.0, 0), (B(5) + 0.6, 0), (B(5) + 1.6, 1), (T_CYC, 1)])
    return c

def core(t):
    return manual(t) if t < T_CYC else cycle(t)

def state(t):
    st = dict(core(t))
    # water is lifted while the piston goes DOWN (pump rod goes UP)
    ds = core(t)['s'] - core(t - 0.18)['s']
    st['water'] = clamp(ds / 0.18 * 1.2) if t > 0.3 else 0.0
    st['a'] = beam_angle(st['s'])
    st['vac'] = win(t, 10.5, B(3) + 0.2, 0.3)
    st['h_valve'] = bw(t, 4)
    st['h_jet'] = bw(t, 5)
    st['h_beam'] = bw(t, 6)
    st['h_pump'] = bw(t, 7)
    st['l_steam'] = bw(t, 4) + win(t, B(9) + 0.3, B(10) + 2, 0.3)
    st['l_jet'] = bw(t, 5)
    st['l_air'] = bw(t, 6) + win(t, B(9) + 1.0, B(10) + 2, 0.3)
    st['l_pump'] = bw(t, 7)
    st['l_date'] = win(t, B(9) + 0.1, B(10) + 2, 0.3)
    return st

# ---------------------------------------------------------------- drawing
def bricks(ctx, x0, y0, w, h, a=1.0, bh=26, bw_=56):
    ctx.rectangle(x0, y0, w, h); fill_stroke(ctx, BRICK, lw=5, alpha=a)
    ctx.save(); ctx.rectangle(x0, y0, w, h); ctx.clip()
    row = 0; y = y0 + bh
    while y < y0 + h:
        ctx.move_to(x0, y); ctx.line_to(x0 + w, y)
        off = (bw_ / 2) * (row % 2)
        x = x0 + off
        while x < x0 + w:
            ctx.move_to(x, y - bh); ctx.line_to(x, y); x += bw_
        y += bh; row += 1
    setc(ctx, BRICK_D, 0.7 * a); ctx.set_line_width(2.5); ctx.stroke()
    ctx.restore()

def draw_house(ctx, t, st):
    # brick pier carrying the beam
    bricks(ctx, 585, 500, 70, 1000)
    # pivot block
    rrect(ctx, 570, 482, 100, 26, 6); fill_stroke(ctx, IRON_D, lw=4)

def draw_boiler(ctx, t, st):
    x0, x1, y0, y1 = BOIL
    # furnace
    bricks(ctx, x0 - 10, y1, x1 - x0 + 20, 100)
    rrect(ctx, 250, 1420, 100, 60, 8); setc(ctx, INK); ctx.fill()
    rnd = random.Random(int(t * 12))
    for k in range(5):
        fx = 262 + k * 19; fh = 22 + rnd.random() * 18
        ctx.move_to(fx - 9, 1478); ctx.curve_to(fx - 6, 1478 - fh * 0.6, fx, 1478 - fh, fx + 1, 1478 - fh)
        ctx.curve_to(fx + 4, 1478 - fh * 0.6, fx + 9, 1470, fx + 9, 1478); ctx.close_path()
        setc(ctx, ORANGE if k % 2 else MUSTARD, 0.95); ctx.fill()
    # haystack boiler (copper dome)
    ctx.move_to(x0, y1); ctx.line_to(x0, y0 + 90)
    ctx.curve_to(x0, y0 - 10, x1, y0 - 10, x1, y0 + 90); ctx.line_to(x1, y1); ctx.close_path()
    fill_stroke(ctx, COPPER, lw=6)
    for yy in (1260, 1330):
        ctx.move_to(x0 + 4, yy); ctx.line_to(x1 - 4, yy); setc(ctx, COPPER_D, 0.8); ctx.set_line_width(3); ctx.stroke()
    # boiling water inside (cut-away window)
    rrect(ctx, 205, 1300, 190, 80, 10); fill_stroke(ctx, hexc('#a9cbe6'), lw=3)
    for k in range(6):
        bx = 220 + k * 30; by = 1370 - ((t * 60 + k * 23) % 60)
        ctx.arc(bx, by, 5, 0, 2 * math.pi); setc(ctx, WHITE, 0.8); ctx.fill()
    text_c(ctx, "BOILER", 300, 1240, 26, INK, True, 2)

def draw_steam_pipe(ctx, t, st):
    # short pipe boiler -> cylinder bottom, with the steam valve
    ctx.rectangle(CX - 18, CYL_BOT + 20, 36, BOIL[2] - CYL_BOT - 10); fill_stroke(ctx, IRON_L, lw=4)
    v = st['valve']
    # valve body + sliding plate (shut = across the pipe, open = slid aside)
    rrect(ctx, CX - 34, 1124, 68, 26, 6); fill_stroke(ctx, IRON, lw=4)
    ctx.rectangle(CX - 18 + 38 * v, 1129, 36, 16); fill_stroke(ctx, RED if v > 0.5 else IRON_D, lw=3)
    if v > 0.05:
        for k in range(4):
            u = (t * 1.4 + k / 4) % 1.0
            y = lerp(1175, 1095, u)
            ctx.arc(CX - 6 + 10 * math.sin(k * 2.1 + t * 3), y, 7, 0, 2 * math.pi); setc(ctx, STEAM, 0.9 * v); ctx.fill()

def draw_injection(ctx, t, st):
    x0, x1, y0, y1 = CIST
    # cistern (open tank of cold water)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); fill_stroke(ctx, WOOD, lw=5)
    ctx.rectangle(x0 + 8, y0 + 14, x1 - x0 - 16, y1 - y0 - 22); setc(ctx, WATER, 0.85); ctx.fill()
    text_c(ctx, "COLD WATER", (x0 + x1) / 2, y0 - 14, 20, WATER_D, True, 1.5)
    # pipe down and into the bottom of the cylinder
    ctx.move_to(INJ_X, y1); ctx.line_to(INJ_X, 1062); ctx.line_to(CYL_X0 + 40, 1062)
    setc(ctx, INK); ctx.set_line_width(16); ctx.stroke()
    ctx.move_to(INJ_X, y1); ctx.line_to(INJ_X, 1062); ctx.line_to(CYL_X0 + 40, 1062)
    j = st['jet']
    setc(ctx, WATER if j > 0.05 else WALL1); ctx.set_line_width(8); ctx.stroke()
    # injection cock
    ctx.arc(INJ_X, 900, 15, 0, 2 * math.pi); fill_stroke(ctx, IRON, lw=4)
    ang = (math.pi / 2) * j
    ctx.move_to(INJ_X - 14 * math.cos(ang), 900 - 14 * math.sin(ang)); ctx.line_to(INJ_X + 14 * math.cos(ang), 900 + 14 * math.sin(ang))
    setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    if j > 0.05:
        for k in range(7):
            u = (k / 7 + t * 0.9) % 1.0
            y = lerp(y1, 1062, u) if u < 0.8 else 1062
            x = INJ_X if u < 0.8 else lerp(INJ_X, CYL_X0 + 40, (u - 0.8) / 0.2)
            ctx.arc(x, y, 4, 0, 2 * math.pi); setc(ctx, WHITE, j * 0.9); ctx.fill()

def draw_cylinder(ctx, t, st):
    s = st['s']; py = piston_y(s)
    ix0, ix1 = CYL_X0 + 20, CYL_X1 - 20
    # interior (paper) + cold tint
    ctx.rectangle(ix0, CYL_TOP, ix1 - ix0, CYL_BOT - CYL_TOP); setc(ctx, WALL1); ctx.fill()
    if st['cold'] > 0:
        ctx.rectangle(ix0, py + P_H, ix1 - ix0, CYL_BOT - py - P_H); setc(ctx, COLD, 0.22 * st['cold']); ctx.fill()
    # steam under the piston
    sv = st['steam']
    if sv > 0.01:
        ctx.save(); ctx.rectangle(ix0, py + P_H, ix1 - ix0, CYL_BOT - py - P_H); ctx.clip()
        setc(ctx, STEAM, 0.55 * sv); ctx.paint()
        rnd = random.Random(7)
        for k in range(14):
            bx = rnd.uniform(ix0 + 10, ix1 - 10); by = rnd.uniform(py + P_H + 10, CYL_BOT - 10)
            r = (16 + rnd.random() * 14) * (0.35 + 0.65 * sv)
            ctx.arc(bx + 6 * math.sin(t * 2 + k), by, r, 0, 2 * math.pi); setc(ctx, WHITE, 0.7 * sv); ctx.fill()
        ctx.restore()
    # condensate drops pooled on the bottom
    d = st['drops']
    if d > 0.01:
        ctx.rectangle(ix0, CYL_BOT - 9 * d, ix1 - ix0, 9 * d); setc(ctx, WATER, 0.9); ctx.fill()
        for k in range(5):
            ctx.arc(ix0 + 18 + k * 26, CYL_BOT - 9 * d - 7, 6 * d, 0, 2 * math.pi); setc(ctx, WATER, 0.9); ctx.fill()
    # cold jet spraying UP from the nozzle at the bottom
    j = st['jet']
    if j > 0.05:
        nx, ny = CYL_X0 + 42, CYL_BOT - 12
        for k in range(9):
            ang = -math.pi / 2 + (k - 4) * 0.13
            u = (t * 2.2 + k * 0.37) % 1.0
            L = 40 + 200 * u
            x = nx + 30 + L * math.cos(ang); y = ny + L * math.sin(ang)
            if y > py + P_H + 4:
                ctx.arc(x, y, 5, 0, 2 * math.pi); setc(ctx, WATER, j); ctx.fill()
        ctx.move_to(nx, ny); ctx.line_to(nx + 30, ny - 4); setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()
    # VACUUM label (empty space under the piston)
    if st['vac'] > 0:
        text_c(ctx, "VACUUM", CX, (py + P_H + CYL_BOT) / 2 + 10, 26, INK, True, 1, st['vac'])
    # walls (open top: no lid) + bottom plate
    ctx.rectangle(CYL_X0, CYL_TOP, 20, CYL_BOT - CYL_TOP + 20); fill_stroke(ctx, IRON, lw=4)
    ctx.rectangle(CYL_X1 - 20, CYL_TOP, 20, CYL_BOT - CYL_TOP + 20); fill_stroke(ctx, IRON, lw=4)
    ctx.rectangle(CYL_X0, CYL_BOT, CYL_X1 - CYL_X0, 20); fill_stroke(ctx, IRON_D, lw=4)
    # piston + rod
    ctx.rectangle(ix0 + 2, py, ix1 - ix0 - 4, P_H); fill_stroke(ctx, IRON_D, lw=4)
    ctx.move_to(ix0 + 4, py + 6); ctx.line_to(ix1 - 4, py + 6); setc(ctx, WATER, 0.6); ctx.set_line_width(3); ctx.stroke()  # water seal
    rod_top = py - 200
    ctx.rectangle(CX - 8, rod_top, 16, 200); fill_stroke(ctx, IRON_L, lw=3)
    chain(ctx, CX, PIV[1], rod_top)

def chain(ctx, x, y0, y1):
    y = y0; k = 0
    while y < y1 - 4:
        h = min(18, y1 - y)
        if k % 2 == 0:
            rrect(ctx, x - 7, y, 14, h + 4, 6)
        else:
            ctx.move_to(x, y); ctx.line_to(x, y + h + 4)
        setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
        y += 16; k += 1

def draw_beam(ctx, t, st):
    a = st['a']
    ctx.save(); ctx.translate(*PIV); ctx.rotate(a)
    # timber beam
    ctx.rectangle(-RL + 8, -22, RL + RR - 16, 44); fill_stroke(ctx, WOOD, lw=6)
    for xx in (-200, -80, 80, 200):
        ctx.move_to(xx, -18); ctx.line_to(xx + 40, 18); setc(ctx, WOOD_D, 0.5); ctx.set_line_width(3); ctx.stroke()
    # arch heads (chains wrap on them, so they hang straight down)
    for (r, base) in ((RL, math.pi), (RR, 0.0)):
        ctx.new_path()
        ctx.arc(0, 0, r, base - 0.36, base + 0.36); ctx.arc_negative(0, 0, r - 26, base + 0.36, base - 0.36); ctx.close_path()
        fill_stroke(ctx, WOOD_D, lw=5)
        for sgn in (-1, 1):
            ctx.move_to(0.55 * r * math.cos(base), 0); ctx.line_to((r - 20) * math.cos(base + sgn * 0.30), (r - 20) * math.sin(base + sgn * 0.30))
            setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()
    ctx.arc(*PIV, 16, 0, 2 * math.pi); fill_stroke(ctx, IRON_L, lw=4)

def draw_pump(ctx, t, st):
    x0, x1, ytop = SHAFT
    # shaft going down into the mine
    ctx.rectangle(x0, ytop, x1 - x0, 1500 - ytop); fill_stroke(ctx, WOOD, lw=5)
    ctx.rectangle(x0 + 12, ytop + 8, x1 - x0 - 24, 1500 - ytop); setc(ctx, hexc('#3e3a42')); ctx.fill()
    ctx.rectangle(x0 + 12, 1300, x1 - x0 - 24, 200); setc(ctx, WATER, 0.9); ctx.fill()
    text_c(ctx, "MINE", x0 - 40, 1470, 20, WATER_D, True, 2)
    # pump rod hanging from the right arch head
    rt = pump_rod_top(st['s'])
    chain(ctx, PX, PIV[1], rt)
    ctx.rectangle(PX - 9, rt, 18, 1500 - rt); fill_stroke(ctx, WOOD_D, lw=3)
    # water rising in the pump pipe with the rod
    w = st['water']
    # spout (left side) + trough
    ctx.rectangle(840, SPOUT_Y - 14, x0 - 840 + 12, 28); fill_stroke(ctx, IRON, lw=4)
    tx0, tx1, ty0, ty1 = TROUGH
    ctx.move_to(tx0, ty0); ctx.line_to(tx0 + 8, ty1); ctx.line_to(tx1 - 8, ty1); ctx.line_to(tx1, ty0)
    fill_stroke(ctx, WOOD, lw=5)
    ctx.rectangle(tx0 + 10, ty0 + 14, tx1 - tx0 - 20, ty1 - ty0 - 18); setc(ctx, WATER, 0.85); ctx.fill()
    if w > 0.02:
        ctx.move_to(846, SPOUT_Y); ctx.curve_to(822, SPOUT_Y + 10, 812, SPOUT_Y + 60, 810, ty0 + 10)
        setc(ctx, WATER, w); ctx.set_line_width(14 * w + 2); ctx.stroke()
        for k in range(5):
            u = (t * 2 + k / 5) % 1.0
            ctx.arc(lerp(840, 810, u), lerp(SPOUT_Y + 4, ty0 + 6, u), 5, 0, 2 * math.pi); setc(ctx, WHITE, 0.8 * w); ctx.fill()

def draw_air(ctx, t, st):
    a = st['arrows']
    if a <= 0: return
    py = piston_y(st['s'])
    for (x, L) in ((245, 1.0), (355, 1.0), (272, 0.8), (328, 0.8)):
        y1 = py - 6; y0 = min(y1 - 60, CYL_TOP - 130 * L)
        straight_arrow(ctx, x, y0, x, y1, AIR, a, lw=9 if L == 1.0 else 6, head=18 if L == 1.0 else 13)
    # outside air pressing on the outside too (small marks)
    text_c(ctx, "AIR", 445, 612, 30, AIR, True, 3, a)

def draw_all(ctx, t, st):
    draw_house(ctx, t, st)
    draw_pump(ctx, t, st)
    draw_boiler(ctx, t, st)
    draw_steam_pipe(ctx, t, st)
    draw_injection(ctx, t, st)
    draw_cylinder(ctx, t, st)
    draw_beam(ctx, t, st)
    draw_air(ctx, t, st)
    # highlights
    highlight(ctx, CX, 1137, 80, 50, RED, st['h_valve'], t)
    highlight(ctx, INJ_X + 40, 1010, 110, 80, COLD, st['h_jet'], t)
    highlight(ctx, PIV[0] - 10, PIV[1], 360, 90, MUSTARD, st['h_beam'], t)
    highlight(ctx, 860, 1040, 120, 120, COLD, st['h_pump'], t)
    # tags
    tag(ctx, "1 · STEAM IN", 560, 1260, RED, st['l_steam'] * (1 - st['l_date']))
    tag(ctx, "STEAM = VACUUM", 540, 1260, INK, st['l_date'])
    tag(ctx, "2 · COLD JET", 190, 470, COLD, st['l_jet'])
    tag(ctx, "3 · AIR STROKE", 490, 690, AIR, st['l_air'] * (1 - st['l_date']))
    tag(ctx, "AIR = WORK", 490, 690, AIR, st['l_date'])
    tag(ctx, "PUMP", 930, 1350, COLD, st['l_pump'])
    tag(ctx, "NEWCOMEN · 1712", 770, 760, INK, st['l_date'])

OVER = (540, 940, 0.98)
CAMKEYS = [(0, 330, 880, 1.25),
           (B(3) - 0.2, *OVER),
           (B(4), 330, 1040, 1.3),       # boiler + steam valve + cylinder
           (B(5), 280, 900, 1.25),       # cistern + injection pipe + cylinder
           (B(6), *OVER),                # beam rocking
           (B(7), 760, 960, 1.25),        # pump + spout
           (B(8), *OVER)]
def CAM(t): return cam_track(CAMKEYS, t)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

def draw_hud(ctx, t, E):
    pop_word(ctx, "AIR!", t - 0.6, 1.6, RED, cx=830, cy=760, size=130)

SFX = [(0.6, 'pop'), (5.4, 'click'), (8.4, 'click'), (B(4) + 0.3, 'pop'), (B(5) + 0.3, 'pop'),
       (B(6) + 0.3, 'pop'), (B(7) + 0.3, 'pop'), (B(9) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- card
def card_force(ctx, t, lt, a):
    card_frame(ctx, "AIR IS HEAVY", a, None)
    # left: one square centimetre with ~1 kg pressing on it
    k1 = ease((lt - 0.1) / 0.6)
    sx, sy = 270, 470
    ctx.rectangle(sx - 45, sy, 90, 18); fill_stroke(ctx, IRON_L, lw=4, alpha=a * k1)
    text_c(ctx, "1 cm²", sx, sy + 52, 26, INK, True, 1, a * k1)
    wy = lerp(250, sy - 70, ease((lt - 0.2) / 0.5))
    rrect(ctx, sx - 40, wy, 80, 70, 8); fill_stroke(ctx, INK2, lw=4, alpha=a * k1)
    text_c(ctx, "1 kg", sx, wy + 45, 26, WHITE, True, 1, a * k1)
    straight_arrow(ctx, sx + 70, 300, sx + 70, sy - 6, AIR, a * k1, lw=6, head=12)
    text_c(ctx, "≈ 14.7 lb per in²", sx, 300, 22, INK2, True, 1, a * k1 * 0)
    # right: the whole piston, 50 cm (20 in) across
    k2 = ease((lt - 1.6) / 0.6)
    px, pyc = 720, 420
    ctx.save(); ctx.translate(px, pyc); ctx.scale(1, 0.32); ctx.arc(0, 0, 170, 0, 2 * math.pi); ctx.restore()
    fill_stroke(ctx, IRON_D, lw=4, alpha=a * k2)
    for i in range(7):
        ax = px - 150 + i * 50
        straight_arrow(ctx, ax, 270, ax, pyc - 30 + abs(i - 3) * 4, AIR, a * k2, lw=5, head=11)
    ctx.move_to(px - 170, pyc + 78); ctx.line_to(px + 170, pyc + 78); setc(ctx, INK, a * k2); ctx.set_line_width(3); ctx.stroke()
    text_c(ctx, "Ø 50 cm · 20 in", px, pyc + 112, 24, INK, True, 1, a * k2)
    k3 = ease((lt - 3.0) / 0.5)
    text_c(ctx, "≈ 2 t · 4,400 lb", 540, 580, 40, AIR, True, 1.5, a * k3)
    text_c(ctx, "≈ 1 kg / cm² · 14.7 lb / in²", 540, 580, 30, TEAL, True, 1.5, a * k1 * (1 - k3))

CARDS = {'force': card_force}
