"""Cogwise episode: How does a commercial ice machine make clear cubes?
(vertical evaporator plate, falling water curtain, thickness probe, hot-gas harvest)  -- SIDE VIEW
Screen coordinates: x grows RIGHT, y grows DOWN. Water flows DOWN the front (right) face of the plate.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="ice-machine",
    title="It makes ice… then heats it 🧊",
    description=("A pro ice machine freezes a waterfall, layer by layer, then melts the cubes loose with hot gas.\n\n"
                 "#Shorts #howthingswork #icemachine #refrigeration #cogwise"),
    hashtags=["Shorts", "howthingswork", "icemachine", "refrigeration", "engineering", "cogwise"],
    sources=[
        "https://www.manualslib.com/manual/318009/Scotsman-Cse60.html?page=9",
        "https://www.katom.com/learning-center/water-to-ice-how-a-commercial-ice-machine-refrigeration-system-works.html",
        "https://www.appliancepartspros.com/b/?p=25439",
    ],
)

BEATS = [
    dict(dur=4.8, title="ICE… THEN HEAT", caption="This machine makes ice by freezing water, then blasting it with heat."),
    dict(dur=4.6, title="THE SECRET: A WATERFALL", caption="The secret: it never fills a tray. It freezes a waterfall."),
    dict(dur=4.8, title="WATER ON A COLD PLATE", caption="A pump lifts water and pours it over an ice-cold metal plate."),
    dict(dur=5.0, title="1 · EVAPORATOR", caption="Inside the plate, refrigerant boils and pulls the heat out of the water."),
    dict(dur=4.2, title=None, caption="Ice grows in each little cell, one thin layer at a time.", card='layers'),
    dict(dur=4.2, title="AIR + MINERALS WASH AWAY", caption="Air and minerals stay in the moving water and wash away."),
    dict(dur=3.6, title=None, caption="That's why the cubes come out crystal clear.", card='clear'),
    dict(dur=4.4, title="2 · PROBE", caption="When the ice is thick enough, a probe ends the freeze."),
    dict(dur=6.4, title="3 · HOT GAS VALVE", caption="A valve sends hot refrigerant gas into the plate. The cubes slip off and drop."),
    dict(dur=4.8, title="WATERFALL + COLD + HEAT", caption="Running water, a cold plate, then a blast of heat: clear ice."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

ANCHOR = (540, 1460)

# ---------------------------------------------------------------- geometry (screen: y DOWN)
CAB = (120, 380, 860, 1110)                 # x 120..980, y 380..1490
PL_X0, FACE = 392, 440                      # evaporator plate (back x0 .. front face)
PL_Y0, PL_Y1 = 470, 1010
NCELL = 10
CELL_H = (PL_Y1 - PL_Y0) / NCELL            # 54 px
RIB = 40                                    # rib depth (cell walls stick out of the face)
TH_MAX = 48                                 # final ice thickness = probe distance
PROBE_Y = PL_Y0 + 5.5 * CELL_H              # probe sits at the middle of cell 6
PROBE_TIP = FACE + TH_MAX + 2
DIST = (470, 452)                           # water distributor tube above the plate
TR = (330, 640, 1075, 1150)                 # trough x0, x1, top, bottom
TR_LVL = 1098
RAMP = ((FACE, 1022), (690, 1072))          # perforated ice deflector: water drips through, cubes slide right
BIN = (620, 960, 1190, 1480)                # ice bin x0, x1, top, bottom
PUMP = (292, 1112, 26)
RISER_X = 292; TOP_Y = 418
REF_X1, REF_X2 = 176, 214                   # refrigerant lines (vertical runs)
REF_Y1, REF_Y2 = 700, 780                   # where they enter the plate
COMP = (130, 1340, 140, 100)
HGV = (REF_X2, 1010)                        # hot gas valve on the hot line
ICE = hexc('#d9f1f4'); ICE_E = hexc('#7fc3cc'); WATER = hexc('#8fcfc8'); WATER_D = hexc('#1f8a8a')
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); HOTC = hexc('#e4472f'); MIN = hexc('#7d7a72')

def cell_y(i): return PL_Y0 + i * CELL_H

def ramp_y(x):
    (x0, y0), (x1, y1) = RAMP
    return lerp(y0, y1, (x - x0) / (x1 - x0))

def poly_at(pts, u):
    seg = [0.0]
    for i in range(1, len(pts)): seg.append(seg[-1] + math.dist(pts[i-1], pts[i]))
    s = clamp(u) * seg[-1]
    for i in range(1, len(pts)):
        if seg[i] >= s:
            k = (s - seg[i-1]) / max(1e-6, seg[i] - seg[i-1])
            return lerp(pts[i-1][0], pts[i][0], k), lerp(pts[i-1][1], pts[i][1], k)
    return pts[-1]

def plen(pts): return sum(math.dist(pts[i-1], pts[i]) for i in range(1, len(pts)))

# cubes already lying in the bin + where new cubes land
def pile_pos(k):
    rnd = random.Random(100 + k)
    col, row = k % 7, k // 7
    return (650 + col * 44 + rnd.uniform(-6, 6) + (row % 2) * 20, 1452 - row * 32 + rnd.uniform(-3, 3), rnd.uniform(-0.4, 0.4))
PILE0 = 14                                  # cubes in the bin at the start

# ---------------------------------------------------------------- state
T_PRE_H = 2.3                               # hook: quick freeze, then quick harvest
T_MAIN_H = B(8) + 2.6                       # main harvest: "The cubes slip off and drop."
T_REC = B(9) + 0.3                          # recap: a new freeze starts

def state(t):
    s = {}
    # ice thickness on the plate
    if t < T_PRE_H + 0.1:
        th = TH_MAX * ease(t / 2.0)
    elif t < B(3) + 0.4:
        th = 0.0
    elif t < T_MAIN_H + 0.1:
        th = TH_MAX * ease((t - B(3) - 0.4) / (B(7) + 1.4 - B(3) - 0.4))
    elif t < T_REC:
        th = 0.0
    else:
        th = TH_MAX * 0.7 * ease((t - T_REC) / 4.0)
    s['th'] = th
    s['on_plate'] = not (T_PRE_H <= t < B(3) + 0.4 or T_MAIN_H <= t < T_REC)
    # refrigerant mode: 0 = cold (boiling liquid), 1 = hot gas
    s['hot'] = max(win(t, 1.9, 3.3, 0.3), win(t, B(8) + 0.5, T_MAIN_H + 2.6, 0.4))
    s['cold'] = max(win(t, 0.0, 2.0, 0.2), win(t, B(3) + 0.1, B(8) + 0.6, 0.3), win(t, T_REC - 0.2, B(10), 0.3))
    # water curtain (pump on)
    s['water'] = max(win(t, 0.0, 2.0, 0.2), win(t, B(1) + 2.2, B(7) + 1.6, 0.4), win(t, T_REC, B(10), 0.4))
    s['trickle'] = win(t, B(1) + 2.2, B(2) + 0.6, 0.3)          # beat 2: the waterfall appears
    s['pump'] = max(win(t, 0.0, 2.0, 0.2), win(t, B(2) + 0.2, B(7) + 1.6, 0.3), win(t, T_REC, B(10), 0.4))
    s['tray'] = win(t, B(1) + 0.1, B(1) + 2.6, 0.3)
    s['tray_x'] = win(t, B(1) + 1.0, B(1) + 2.6, 0.2)
    s['icons'] = win(t, 0.2, 4.6, 0.3)
    s['heat_arrows'] = bw(t, 3)
    s['minerals'] = win(t, B(5) + 0.2, B(7), 0.4)
    s['trough_grey'] = ease((t - B(5) - 0.4) / 3.0) * (1 - ease((t - B(8)) / 1.0))
    s['probe_hit'] = win(t, B(7) + 1.4, B(8) + 0.4, 0.15)
    s['h_plate'] = bw(t, 3); s['h_probe'] = bw(t, 7); s['h_valve'] = bw(t, 8)
    rc = bw(t, 9, 10)
    s['l_evap'] = max(bw(t, 3, 4), rc); s['l_probe'] = max(bw(t, 7, 8), rc); s['l_valve'] = max(bw(t, 8), rc)
    s['l_pump'] = bw(t, 2); s['l_bin'] = win(t, T_MAIN_H + 0.6, B(9) + 0.1, 0.3)
    s['loop'] = rc
    return s

# ---------------------------------------------------------------- cubes falling (one per cell)
def cube_path(i, th):
    x = FACE + th / 2
    y = cell_y(i) + CELL_H / 2
    px, py, _ = pile_pos(PILE0 + i)
    return [(x, y), (x, ramp_y(x) - 18), (RAMP[1][0], RAMP[1][1] - 18), (px, py)]

def draw_cube(ctx, x, y, w, h, rot, a=1.0, cloudy=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    rrect(ctx, -w/2, -h/2, w, h, 5); setc(ctx, ICE, a); ctx.fill_preserve()
    setc(ctx, ICE_E, a); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(-w/2 + 7, -h/2 + 7); ctx.line_to(-w/2 + 7 + w * 0.3, -h/2 + 7)
    setc(ctx, WHITE, a * 0.9); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def falling(ctx, t, t0, th, base):
    """cubes released at t0: slide down 8 px, then fall onto the ramp, slide right, drop in the bin.
    returns how many have landed."""
    landed = 0
    for i in range(NCELL):
        delay = 0.25 + (NCELL - 1 - i) * 0.04          # lower cells leave first
        px, py, rot = pile_pos(base + i)
        x = FACE + th / 2; y = cell_y(i) + CELL_H / 2
        pts = [(x, y + 8), (x, ramp_y(x) - 20), (RAMP[1][0] - 4, RAMP[1][1] - 20), (px, py)]
        el = t - t0 - delay
        if el < 0:
            yy = y + 8 * ease((t - t0) / 0.25)
            draw_cube(ctx, x, yy, th, CELL_H - 10, 0); continue
        dist = 420 * el + 700 * el * el                # accelerating (gravity-ish)
        L = plen(pts)
        if dist >= L: landed += 1; continue
        cx, cy = poly_at(pts, dist / L)
        draw_cube(ctx, cx, cy, max(th, 30), CELL_H - 10, rot * dist / L)
    return landed

# ---------------------------------------------------------------- stage
def pipe(ctx, pts, outer, inner, col):
    for lw, c in ((outer, INK), (inner, col)):
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        setc(ctx, c); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()

def ref_line(ctx, x, y_in, col):
    """refrigerant line: from the compressor up at x, then right into the plate at y_in,
    with a little hop over the water riser (they do not connect)."""
    for lw, c in ((14, INK), (8, col)):
        ctx.move_to(x, COMP[1]); ctx.line_to(x, y_in); ctx.line_to(RISER_X - 22, y_in)
        ctx.arc(RISER_X, y_in, 22, math.pi, 2 * math.pi)
        ctx.line_to(PL_X0, y_in)
        setc(ctx, c); ctx.set_line_width(lw); ctx.stroke()

def draw_machine(ctx, t, s):
    x, y, w, h = CAB
    rrect(ctx, x, y, w, h, 18); fill_stroke(ctx, hexc('#efe8da'), lw=6)
    ctx.move_to(x, BIN[2] - 20); ctx.line_to(x + w, BIN[2] - 20); setc(ctx, INK2); ctx.set_line_width(3); ctx.stroke()

    th = s['th']; hot = s['hot']; cold = s['cold']
    rcol = lerpc(lerpc(STEEL_D, TEAL, cold), HOTC, hot)
    # compressor + refrigerant lines
    rrect(ctx, *COMP, 14); fill_stroke(ctx, STEEL_D, lw=5)
    text_c(ctx, "COMPRESSOR", COMP[0] + COMP[2]/2, COMP[1] + 60, 17, INK, True, 1)
    ref_line(ctx, REF_X1, REF_Y1, lerpc(STEEL_D, TEAL, cold))   # suction line (vapor back to the compressor)
    ref_line(ctx, REF_X2, REF_Y2, rcol)                          # feed line: cold liquid, or hot gas at harvest
    # hot gas valve
    vx, vy = HGV
    rrect(ctx, vx - 26, vy - 26, 52, 52, 8); fill_stroke(ctx, HOTC if hot > 0.5 else STEEL, lw=4)
    ctx.move_to(vx - 14, vy - 14); ctx.line_to(vx + 14, vy + 14); ctx.move_to(vx + 14, vy - 14); ctx.line_to(vx - 14, vy + 14)
    setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    if hot > 0:
        for k in range(5):
            u = (t * 1.3 + k / 5) % 1.0
            px, py = poly_at([(REF_X2, vy - 30), (REF_X2, REF_Y2), (PL_X0, REF_Y2)], u)
            ctx.arc(px, py, 5, 0, 2 * math.pi); setc(ctx, WHITE, hot * 0.9); ctx.fill()

    # water riser + distributor
    pipe(ctx, [(PUMP[0], PUMP[1]), (RISER_X, TOP_Y), (DIST[0], TOP_Y), (DIST[0], DIST[1])], 22, 13, hexc('#dfe3e6'))
    ctx.arc(DIST[0], DIST[1], 16, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=4)

    # trough (water reservoir)
    x0, x1, ty, by = TR
    ctx.move_to(x0, ty); ctx.line_to(x0, by); ctx.line_to(x1, by); ctx.line_to(x1, ty)
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    wcol = lerpc(WATER, hexc('#b5b2a6'), 0.7 * s['trough_grey'])
    ctx.rectangle(x0 + 3, TR_LVL, x1 - x0 - 6, by - TR_LVL - 3); setc(ctx, wcol); ctx.fill()
    ctx.move_to(x0 + 3, TR_LVL); ctx.line_to(x1 - 3, TR_LVL); setc(ctx, WATER_D); ctx.set_line_width(3); ctx.stroke()
    # pump
    pa = s['pump']
    ctx.move_to(x0, PUMP[1]); ctx.line_to(PUMP[0] + PUMP[2], PUMP[1]); setc(ctx, INK); ctx.set_line_width(12); ctx.stroke()
    ctx.arc(PUMP[0], PUMP[1], PUMP[2], 0, 2 * math.pi); fill_stroke(ctx, TEAL if pa > 0.5 else STEEL_D, lw=5)
    ctx.save(); ctx.translate(PUMP[0], PUMP[1]); ctx.rotate(t * 9 * pa)
    for k in range(4):
        ctx.move_to(0, 0); ctx.line_to(18, 0); ctx.rotate(math.pi / 2)
    setc(ctx, CREAM); ctx.set_line_width(5); ctx.stroke(); ctx.restore()

    # bin + pile
    bx0, bx1, bty, bby = BIN
    ctx.move_to(bx0, bty); ctx.line_to(bx0, bby); ctx.line_to(bx1, bby); ctx.line_to(bx1, bty)
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "ICE BIN", (bx0 + bx1) / 2, bty + 40, 22, INK2, True, 3)

    # ---- evaporator plate (section): back plate + refrigerant tubes + ribs
    pcol = lerpc(lerpc(STEEL, hexc('#a9d6db'), cold), hexc('#f0a08f'), hot)
    ctx.rectangle(PL_X0, PL_Y0, FACE - PL_X0, PL_Y1 - PL_Y0); fill_stroke(ctx, pcol, lw=5)
    for i in range(NCELL):
        cy = cell_y(i) + CELL_H / 2
        ctx.arc(PL_X0 + 22, cy, 13, 0, 2 * math.pi); fill_stroke(ctx, rcol, lw=3)
        if cold > 0.3 and hot < 0.5:       # refrigerant boiling inside the tube
            for k in range(2):
                u = (t * 1.7 + k * 0.5 + i * 0.13) % 1.0
                ctx.arc(PL_X0 + 16 + 12 * k, cy + 7 - 14 * u, 3.5, 0, 2 * math.pi)
                setc(ctx, WHITE, cold * (1 - u)); ctx.fill()
    for i in range(NCELL + 1):
        ry = cell_y(i)
        ctx.rectangle(FACE, ry - 4, RIB, 8); fill_stroke(ctx, STEEL_D, lw=2.5)

    # ---- ice in the cells (grows outward from the face, toward +x)
    if s['on_plate'] and th > 0.5:
        for i in range(NCELL):
            iy = cell_y(i) + 5
            ctx.rectangle(FACE, iy, th, CELL_H - 10); setc(ctx, ICE); ctx.fill_preserve()
            setc(ctx, ICE_E); ctx.set_line_width(2.5); ctx.stroke()
        if th > RIB:                         # past the ribs the cells bridge into one slab
            ctx.rectangle(FACE + RIB, PL_Y0 + 2, th - RIB, PL_Y1 - PL_Y0 - 4); setc(ctx, ICE); ctx.fill()
            ctx.move_to(FACE + th, PL_Y0 + 2); ctx.line_to(FACE + th, PL_Y1 - 2); setc(ctx, ICE_E); ctx.set_line_width(2.5); ctx.stroke()

    # ---- water curtain: down the front of the ice, off the bottom, through the ramp, into the trough
    wa = s['water']
    surf = FACE + (th if s['on_plate'] else 0) + 5
    if wa > 0:
        film_len = 1.0 if s['trickle'] <= 0 else clamp(s['trickle'] * 1.2)
        y_end = lerp(PL_Y0, PL_Y1 + 70, film_len) if s['trickle'] > 0 and t < B(2) else PL_Y1 + 70
        ctx.move_to(surf, PL_Y0 - 6); ctx.line_to(surf, min(y_end, PL_Y1))
        setc(ctx, WATER, wa * 0.85); ctx.set_line_width(9); ctx.stroke()
        path = [(DIST[0] - 4, DIST[1] + 14), (surf, PL_Y0), (surf, PL_Y1), (surf + 6, TR_LVL + 4), (x0 + 20, TR_LVL + 26)]
        for k in range(22):
            u = (k / 22 + t * 0.32) % 1.0
            px, py = poly_at(path, u)
            if py > y_end: continue
            ctx.arc(px, py, 5, 0, 2 * math.pi); setc(ctx, WATER_D, wa); ctx.fill()
        # minerals + air bubbles stay in the moving water and go down to the trough
        if s['minerals'] > 0:
            for k in range(12):
                u = (k / 12 + t * 0.32 + 0.02) % 1.0
                px, py = poly_at(path, u)
                if k % 2:
                    ctx.arc(px + 8, py, 5, 0, 2 * math.pi); setc(ctx, MIN, s['minerals']); ctx.fill()
                else:
                    ctx.arc(px + 9, py, 6, 0, 2 * math.pi); setc(ctx, WHITE, s['minerals']); ctx.fill_preserve()
                    setc(ctx, INK2, s['minerals']); ctx.set_line_width(2); ctx.stroke()
    # pumped water up the riser (trough -> pump -> up -> across -> distributor)
    if s['pump'] > 0:
        rp = [(x0, PUMP[1]), (PUMP[0], PUMP[1]), (RISER_X, TOP_Y), (DIST[0], TOP_Y), (DIST[0], DIST[1])]
        for k in range(14):
            u = (k / 14 + t * 0.35) % 1.0
            px, py = poly_at(rp, u)
            ctx.arc(px, py, 5, 0, 2 * math.pi); setc(ctx, WATER_D, s['pump']); ctx.fill()

    # ramp (perforated deflector, drawn dashed)
    ctx.move_to(*RAMP[0]); ctx.line_to(*RAMP[1]); ctx.set_dash([14, 8]); setc(ctx, INK); ctx.set_line_width(6)
    ctx.stroke(); ctx.set_dash([])

    # ---- probe (rod held by a bracket; tip sits TH_MAX in front of the face)
    hit = s['probe_hit']
    ctx.move_to(PROBE_TIP, PROBE_Y); ctx.line_to(600, PROBE_Y); ctx.line_to(600, PROBE_Y - 70)
    setc(ctx, INK); ctx.set_line_width(10); ctx.stroke()
    ctx.move_to(PROBE_TIP, PROBE_Y); ctx.line_to(600, PROBE_Y); setc(ctx, lerpc(MUSTARD, RED, hit)); ctx.set_line_width(5); ctx.stroke()
    ctx.arc(PROBE_TIP, PROBE_Y, 7 + 5 * hit, 0, 2 * math.pi); setc(ctx, lerpc(MUSTARD, RED, hit)); ctx.fill()

    # ---- harvest falls + pile
    landed = 0
    if T_PRE_H <= t < T_PRE_H + 3.0:
        landed = falling(ctx, t, T_PRE_H, TH_MAX * ease(T_PRE_H / 2.0), PILE0)
        n_pile = PILE0 + landed
    elif t >= T_PRE_H + 3.0:
        n_pile = PILE0 + NCELL
    else:
        n_pile = PILE0
    if T_MAIN_H <= t < T_MAIN_H + 3.0:
        landed = falling(ctx, t, T_MAIN_H, TH_MAX, PILE0 + NCELL)
        n_pile = PILE0 + NCELL + landed
    elif t >= T_MAIN_H + 3.0:
        n_pile = PILE0 + 2 * NCELL
    for k in range(n_pile):
        px, py, rot = pile_pos(k); draw_cube(ctx, px, py, 40, 30, rot)

    # ---- heat arrows: heat leaves the WATER (right) and goes INTO the plate (left)
    if s['heat_arrows'] > 0:
        for yy in (590, 870, 960):
            wavy_arrow(ctx, 600, yy, FACE + 10, yy, t, HOTC, s['heat_arrows'], amp=7, wl=28, lw=4, head=10)
        text_c(ctx, "HEAT OUT OF WATER", 690, 680, 22, HOTC, True, 1, s['heat_arrows'])

    # hook icons: snowflake (freeze) then flame (heat)
    ia = s['icons']
    if ia > 0:
        c = 1 - hot
        snow(ctx, 760, 620, 34, TEAL, ia * c)
        flame(ctx, 760, 620, 36, HOTC, ia * hot)

    # tray (the misconception), crossed out
    if s['tray'] > 0:
        a = s['tray']
        rrect(ctx, 700, 560, 210, 70, 10); fill_stroke(ctx, CREAM, lw=4, alpha=a)
        for k in range(4):
            rrect(ctx, 712 + k * 50, 572, 40, 46, 6); fill_stroke(ctx, ICE, ICE_E, 3, a)
        text_c(ctx, "ICE TRAY", 805, 545, 22, INK2, True, 2, a)
        if s['tray_x'] > 0:
            ax = s['tray_x']
            ctx.move_to(690, 540); ctx.line_to(920, 650); ctx.move_to(920, 540); ctx.line_to(690, 650)
            setc(ctx, RED, ax); ctx.set_line_width(12); ctx.stroke()

    # ---- highlights + labels
    highlight(ctx, (PL_X0 + FACE) / 2 + 20, (PL_Y0 + PL_Y1) / 2, 90, 300, TEAL, s['h_plate'], t)
    highlight(ctx, PROBE_TIP + 20, PROBE_Y, 70, 46, MUSTARD, s['h_probe'], t)
    highlight(ctx, HGV[0], HGV[1], 56, 56, HOTC, s['h_valve'], t)
    def lead(x0_, y0_, x1_, y1_, a):
        if a > 0:
            ctx.move_to(x0_, y0_); ctx.line_to(x1_, y1_); ctx.set_dash([6, 6]); setc(ctx, INK2, a)
            ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    lead(FACE + 4, PL_Y0 + 20, 600, 470, s['l_evap'])
    tag(ctx, "1 · EVAPORATOR", 680, 455, TEAL, s['l_evap'])
    lead(604, PROBE_Y - 70, 680, 655, s['l_probe'])
    tag(ctx, "2 · PROBE", 730, 640, ORANGE, s['l_probe'])
    lead(HGV[0] + 30, HGV[1] + 20, 300, 1300, s['l_valve'])
    tag(ctx, "3 · HOT GAS VALVE", 380, 1320, HOTC, s['l_valve'])
    tag(ctx, "PUMP", 292, 1180, TEAL, s['l_pump'])
    if s['loop'] > 0:
        a = s['loop']
        for k, (lab, col) in enumerate((("WATER", WATER_D), ("COLD", TEAL), ("HEAT", HOTC))):
            text_c(ctx, lab, 800, 870 + k * 70, 34, col, True, 2, a)
        straight_arrow(ctx, 800, 882, 800, 910, INK2, a, lw=4, head=8)
        straight_arrow(ctx, 800, 952, 800, 980, INK2, a, lw=4, head=8)

def snow(ctx, cx, cy, r, col, a):
    if a <= 0: return
    for k in range(6):
        ang = k * math.pi / 3
        ctx.move_to(cx, cy); ctx.line_to(cx + r * math.cos(ang), cy + r * math.sin(ang))
        mx, my = cx + 0.6 * r * math.cos(ang), cy + 0.6 * r * math.sin(ang)
        for d in (-0.6, 0.6):
            ctx.move_to(mx, my); ctx.line_to(mx + 0.3 * r * math.cos(ang + d), my + 0.3 * r * math.sin(ang + d))
    setc(ctx, col, a); ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def flame(ctx, cx, cy, r, col, a):
    if a <= 0: return
    ctx.move_to(cx, cy - r * 1.3)
    ctx.curve_to(cx + r * 1.1, cy - r * 0.2, cx + r * 0.9, cy + r, cx, cy + r)
    ctx.curve_to(cx - r * 0.9, cy + r, cx - r * 1.1, cy - r * 0.2, cx, cy - r * 1.3)
    setc(ctx, col, a); ctx.fill()
    ctx.move_to(cx, cy - r * 0.2)
    ctx.curve_to(cx + r * 0.5, cy + r * 0.3, cx + r * 0.4, cy + r * 0.8, cx, cy + r * 0.8)
    ctx.curve_to(cx - r * 0.4, cy + r * 0.8, cx - r * 0.5, cy + r * 0.3, cx, cy - r * 0.2)
    setc(ctx, MUSTARD, a); ctx.fill()

CAMKEYS = [(0, 550, 935, 1.12),
           (B(3) + 0.1, 520, 780, 1.45),       # evaporator: plate + heat arrows
           (B(5) + 0.1, 500, 900, 1.35),       # minerals running down into the trough
           (B(7) + 0.1, 520, 770, 1.5),        # probe
           (B(8) + 0.1, 550, 935, 1.12)]       # harvest: valve, ramp and bin all in view
def CAM(t): return cam_track(CAMKEYS, t)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_machine(ctx, t, state(t))

SFX = [(0.3, 'pop'), (T_PRE_H + 0.3, 'click'), (B(2) + 0.2, 'click'), (B(3) + 0.3, 'pop'),
       (B(7) + 0.3, 'pop'), (B(7) + 1.4, 'click'), (B(8) + 0.3, 'pop'), (T_MAIN_H + 0.4, 'click'), (B(9) + 0.2, 'ding')]
HUM = []

# ---------------------------------------------------------------- cards
def card_layers(ctx, t, lt, a):
    """Zoom on ONE cell, side view (same orientation as the stage): plate on the LEFT,
    water running DOWN the right; ice grows to the right in thin layers."""
    card_frame(ctx, "ONE CELL, SEEN FROM THE SIDE", a, "PURE WATER FREEZES FIRST, LAYER BY LAYER", TEAL)
    px0, px1, y0, y1 = 200, 260, 250, 540
    ctx.rectangle(px0, y0, px1 - px0, y1 - y0); fill_stroke(ctx, hexc('#a9d6db'), lw=4, alpha=a)
    for ry in (268, 522):
        ctx.rectangle(px1, ry - 6, 200, 12); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    nl = int(clamp(lt / 3.4) * 9) + 1
    for k in range(nl):
        lx = px1 + k * 18
        ctx.rectangle(lx, 276, 18, 240); setc(ctx, ICE if k % 2 == 0 else hexc('#c6e8ec'), a); ctx.fill()
    edge = px1 + nl * 18
    ctx.move_to(edge, 276); ctx.line_to(edge, 516); setc(ctx, ICE_E, a); ctx.set_line_width(3); ctx.stroke()
    # water film running down the ice surface
    ctx.move_to(edge + 8, 250); ctx.line_to(edge + 8, 540); setc(ctx, WATER, a * 0.8); ctx.set_line_width(10); ctx.stroke()
    for k in range(6):
        u = (k / 6 + lt * 0.6) % 1.0
        ctx.arc(edge + 8, lerp(250, 540, u), 5, 0, 2 * math.pi); setc(ctx, WATER_D, a); ctx.fill()
    straight_arrow(ctx, edge + 40, 300, edge + 40, 480, WATER_D, a, lw=5, head=11)
    text_c(ctx, "WATER", edge + 100, 400, 24, WATER_D, True, 1, a)
    text_c(ctx, f"LAYER {nl}", 800, 330, 30, INK, True, 2, a)
    straight_arrow(ctx, 720, 400, 880, 400, ICE_E, a, lw=6, head=12)
    text_c(ctx, "ICE GROWS", 800, 460, 24, ICE_E, True, 1, a)

def card_clear(ctx, t, lt, a):
    card_frame(ctx, "SAME WATER, TWO CUBES", a, "AIR TRAPPED  vs  AIR WASHED AWAY", TEAL)
    k = ease((lt - 0.2) / 0.8)
    for (cx, lab, cloudy) in ((330, "FREEZER TRAY", True), (750, "ICE MACHINE", False)):
        rrect(ctx, cx - 100, 270, 200, 200, 18); setc(ctx, ICE, a); ctx.fill_preserve()
        setc(ctx, ICE_E, a); ctx.set_line_width(4); ctx.stroke()
        if cloudy:
            ctx.save(); ctx.translate(cx, 370); ctx.scale(70, 60); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
            setc(ctx, WHITE, a * 0.85 * k); ctx.fill()
            rnd = random.Random(3)
            for _ in range(16):
                ctx.arc(cx + rnd.uniform(-60, 60), 370 + rnd.uniform(-50, 50), rnd.uniform(3, 7), 0, 2 * math.pi)
                setc(ctx, INK2, a * 0.35 * k); ctx.fill()
        else:
            ctx.move_to(cx - 70, 300); ctx.line_to(cx - 20, 300); setc(ctx, WHITE, a); ctx.set_line_width(6); ctx.stroke()
            text_c(ctx, "clear", cx, 385, 30, ICE_E, False, 1, a * k)
        text_c(ctx, lab, cx, 515, 26, INK, True, 2, a)

CARDS = {'layers': card_layers, 'clear': card_clear}
