"""Cogwise episode: In 1755, a doctor made ice by boiling something (series "How you accidentally invented...").
SIDE VIEW, cut-away. Screen coordinates: x grows RIGHT, y grows DOWN.
Physics:
  CULLEN (1755): a small glass of ether stands in a bowl of water, under a glass bell jar on a pump plate.
     A hand air pump (right) sucks the air OUT of the jar: arrows go jar -> pipe -> pump -> out of the spout (to the RIGHT).
     Less pressure -> ether boils at room temperature. Boiling takes latent heat: HEAT flows FROM the water INTO the glass
     (wavy arrows point INWARD, toward the glass). The water around the glass freezes. The vapour leaves via the pump: ether runs out.
  FRIDGE (Perkins 1834 closed loop), door on the LEFT, back on the RIGHT:
     evaporator (inside, top) -> suction line (behind the back, down) -> compressor (bottom back)
     -> hot gas riser (up) -> condenser zig-zag on the back (top to bottom, gives heat to the room: arrows point RIGHT, away)
     -> liquid line -> capillary up inside the back wall -> evaporator. Heat from the food goes UP into the evaporator.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="fridge-invented",
    title="In 1755, a doctor made ice by boiling something 🧊",
    description=("William Cullen boiled ether under a vacuum pump and froze the water around it. Your fridge still runs on that trick, in a closed loop.\n\n"
                 "#Shorts #howthingswork #fridge #physics #history #cogwise"),
    hashtags=["Shorts", "howthingswork", "fridge", "physics", "history", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/William_Cullen",
        "https://www.asme.org/About-ASME/Engineering-History/Landmarks/274-Perkins-Vapor-Compression-Cycle-for-Refrigeration",
        "https://science.howstuffworks.com/innovation/inventions/who-invented-the-refrigerator.htm",
        "https://en.wikipedia.org/wiki/Jacob_Perkins",
        "https://biologyinsights.com/why-does-sweating-lower-body-temperature/",
    ],
)

BEATS = [
    dict(dur=5.2, title="1755", caption="In 1755, a Scottish doctor made ice by making a liquid boil."),
    dict(dur=5.0, title="THE SECRET", caption="The secret: boiling doesn't need heat from a flame. It steals heat."),
    dict(dur=5.6, title="1 · PUMP", caption="William Cullen put ether in a glass, then pumped the air out above it."),
    dict(dur=4.8, title=None, caption="With less pressure pushing down, the ether boiled at room temperature.", card='pressure'),
    dict(dur=5.4, title="2 · STEAL", caption="To turn into vapour, every gram drags heat out of whatever it touches."),
    dict(dur=4.6, title="ICE", caption="The glass got so cold that the water around it froze."),
    dict(dur=6.0, title=None, caption="Same as sweat: one gram of water evaporating carries off over two thousand joules.", card='sweat'),
    dict(dur=5.0, title="PROBLEM", caption="Problem: the vapour escaped into the room, and the ether was gone."),
    dict(dur=6.0, title="3 · CLOSE THE LOOP", caption="In 1834, Jacob Perkins closed the loop with a pump that squeezes the vapour."),
    dict(dur=5.8, title=None, caption="Squeezed, it turns back into liquid and dumps the heat outside, behind your fridge."),
    dict(dur=6.2, title="YOUR FRIDGE", caption="Your fridge does this nonstop: its liquid boils at minus twelve Celsius, eleven Fahrenheit."),
    dict(dur=5.0, title="RECAP", caption="Recap: a fridge is a liquid boiling inside it, forever recycled."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.3):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

def track(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]

ANCHOR = (540, 1500)

# ---------------------------------------------------------------- palette extras
STEEL = hexc('#b9c0c6'); STEEL_D = hexc('#7b838a'); STEEL_L = hexc('#dde2e6'); IRON_D = hexc('#4f565c')
WOOD = hexc('#b07a42'); WOOD_D = hexc('#7d5228')
WATER = hexc('#4a90c8'); WATER_D = hexc('#2f6c9e')
ICE = hexc('#dcefF7'); ICE_D = hexc('#9cc9dc')
ETHER = hexc('#eef6d8')
GLASS = hexc('#e3f1f3')
BRASS = hexc('#c9a24a'); BRASS_D = hexc('#8d6f2a')
HEAT = RED
VAP = VAPOR

M0 = B(8)                       # morph Cullen -> fridge

# ---------------------------------------------------------------- Cullen geometry (screen: y DOWN)
TABLE_Y = 1340
PLATE = (210, 1310, 500, 30)     # pump plate under the jar
JX0, JX1, JTOP_SIDE = 255, 665, 930   # bell jar side walls, where the dome starts
JCX, JR = 460, 205               # dome centre x, radius
BOWL = (300, 620, 1170, 1310)    # bowl x0, x1, rim y, bottom y
WAT_Y = 1195                     # water surface
GX0, GX1, GTOP, GBOT = 415, 505, 1060, 1300    # glass of ether
ETH_FULL, ETH_EMPTY = 1130, 1288
PX0, PX1, PTOP, PBOT = 750, 830, 1000, 1335    # pump barrel
SPOUT = (830, 1030)

def ether_y(t):
    return track(t, [(0, ETH_FULL), (B(7) + 0.4, ETH_FULL), (B(8) - 0.3, ETH_EMPTY), (M0 + 2, ETH_EMPTY)])

def state(t):
    s = {}
    s['m'] = clamp((t - M0 - 0.1) / 1.4)
    # ice: preview in beat 1, melts back in beat 2, freezes for real in beat 6
    s['ice'] = track(t, [(0, 0), (0.3, 0), (1.5, 1), (B(1) + 0.1, 1), (B(1) + 0.8, 0), (B(5) + 0.2, 0), (B(5) + 2.4, 1)])
    s['boil'] = track(t, [(0, 0.9), (0.3, 1), (B(1) + 0.1, 1), (B(1) + 0.6, 0.6), (B(2), 0.4), (B(2) + 0.6, 0), (B(2) + 3.6, 0),
                          (B(2) + 4.8, 1), (B(7) + 0.4, 1), (B(8) - 0.3, 0)])
    s['pump'] = win(t, B(2) + 1.2, B(3) + 2.0, 0.3) + win(t, B(7) + 0.1, B(8), 0.3)
    s['air_out'] = win(t, B(2) + 1.2, B(3) - 0.1, 0.3)
    s['vap_out'] = win(t, B(7) + 0.1, B(8) + 0.2, 0.3)
    s['heat_in'] = win(t, B(1) + 0.2, B(2) - 0.1, 0.3) + win(t, B(4) + 0.2, B(5) + 2.0, 0.3)
    s['therm'] = track(t, [(0, 0.55), (B(4) + 0.3, 0.55), (B(5) + 1.8, 0.12)])
    s['therm_a'] = win(t, B(4) + 0.2, B(6), 0.3)
    s['mol'] = win(t, B(4) + 0.1, B(5), 0.3)
    s['ey'] = ether_y(t)
    s['h_glass'] = bw(t, 1)
    s['h_pump'] = bw(t, 2)
    s['h_bowl'] = bw(t, 5)
    s['h_spout'] = bw(t, 7)
    s['l_ether'] = win(t, B(2) + 0.3, B(3), 0.3)
    s['l_air'] = win(t, B(2) + 1.4, B(3), 0.3)
    s['l_heat'] = bw(t, 1) + bw(t, 4)
    s['l_ice'] = win(t, B(5) + 1.0, B(6), 0.3)
    s['l_vap'] = bw(t, 7)
    s['l_gone'] = win(t, B(7) + 2.6, B(8), 0.3)
    # fridge
    s['reveal'] = clamp((t - M0 - 0.6) / 2.6)
    s['flow'] = clamp((t - M0 - 2.4) / 0.8)
    s['h_comp'] = win(t, M0 + 2.6, B(9), 0.3)
    s['h_cond'] = bw(t, 9)
    s['h_evap'] = bw(t, 10)
    s['l_perkins'] = win(t, M0 + 0.8, B(9), 0.3)
    s['l_comp'] = win(t, M0 + 2.6, B(9), 0.3) + win(t, B(11) + 0.2, B(12) + 2, 0.3)
    s['l_cond'] = bw(t, 9) + win(t, B(11) + 0.2, B(12) + 2, 0.3)
    s['l_evap'] = bw(t, 10)
    s['l_boil'] = win(t, B(11) + 0.2, B(12) + 2, 0.3)
    s['heat_out'] = bw(t, 9) + win(t, B(11) + 0.2, B(12) + 2, 0.3)
    s['heat_food'] = bw(t, 10) + win(t, B(11) + 0.2, B(12) + 2, 0.3)
    s['l_recap'] = win(t, B(11) + 0.6, B(12) + 2, 0.3)
    return s

def a_cullen(st): return 1 - ease(clamp(st['m'] * 1.6))
def a_fridge(st): return ease(clamp(st['m'] * 1.6 - 0.6))

# ---------------------------------------------------------------- Cullen apparatus
def jar_path(ctx):
    ctx.move_to(JX0, PLATE[1]); ctx.line_to(JX0, JTOP_SIDE)
    ctx.arc(JCX, JTOP_SIDE, JR, math.pi, 2 * math.pi)
    ctx.line_to(JX1, PLATE[1]); ctx.close_path()

def draw_table(ctx):
    ctx.rectangle(150, TABLE_Y, 780, 28); fill_stroke(ctx, WOOD, lw=5)
    ctx.rectangle(170, TABLE_Y + 28, 740, 18); fill_stroke(ctx, WOOD_D, lw=4)
    for x in (200, 860):
        ctx.rectangle(x, TABLE_Y + 46, 26, 114); fill_stroke(ctx, WOOD, lw=4)

def draw_bowl_contents(ctx, t, st):
    x0, x1, ry, by = BOWL
    ice = clamp(st['ice'])
    # water / ice between the bowl walls and the glass
    ctx.save()
    ctx.move_to(x0 + 6, ry); ctx.line_to(x0 + 30, by - 6); ctx.line_to(x1 - 30, by - 6); ctx.line_to(x1 - 6, ry); ctx.close_path()
    ctx.clip()
    ctx.rectangle(x0, WAT_Y, x1 - x0, by - WAT_Y)
    setc(ctx, lerpc(WATER, ICE, ice), 0.92); ctx.fill()
    if ice > 0.05:
        # frost grows outward FROM the glass (coldest point)
        rnd = random.Random(11)
        for k in range(26):
            side = -1 if k % 2 == 0 else 1
            d = rnd.uniform(0, 1)
            if d > ice: continue
            gx = GX0 if side < 0 else GX1
            x = gx + side * (8 + d * 105); y = rnd.uniform(WAT_Y + 12, by - 16)
            r = 9 + rnd.random() * 7
            for q in range(3):
                ang = q * math.pi / 3 + k
                ctx.move_to(x - r * math.cos(ang), y - r * math.sin(ang)); ctx.line_to(x + r * math.cos(ang), y + r * math.sin(ang))
            setc(ctx, ICE_D, 0.9 * ice); ctx.set_line_width(3); ctx.stroke()
        ctx.rectangle(x0, WAT_Y - 4, x1 - x0, 8); setc(ctx, WHITE, 0.8 * ice); ctx.fill()
    ctx.restore()

def draw_bowl(ctx):
    x0, x1, ry, by = BOWL
    ctx.move_to(x0 - 10, ry); ctx.line_to(x0 + 24, by); ctx.line_to(x1 - 24, by); ctx.line_to(x1 + 10, ry)
    setc(ctx, INK); ctx.set_line_width(7); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.move_to(x0 - 18, ry); ctx.line_to(x0 + 2, ry); ctx.move_to(x1 - 2, ry); ctx.line_to(x1 + 18, ry)
    ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def draw_glass(ctx, t, st):
    ey = st['ey']
    ctx.rectangle(GX0, GTOP, GX1 - GX0, GBOT - GTOP); setc(ctx, GLASS, 0.7); ctx.fill()
    if ey < GBOT - 6:
        ctx.rectangle(GX0 + 5, ey, GX1 - GX0 - 10, GBOT - 5 - ey); setc(ctx, ETHER, 0.98); ctx.fill()
        ctx.move_to(GX0 + 5, ey); ctx.line_to(GX1 - 5, ey); setc(ctx, INK2, 0.8); ctx.set_line_width(3); ctx.stroke()
    b = clamp(st['boil'])
    if b > 0.02 and ey < GBOT - 20:
        for k in range(9):
            u = (t * (1.3 + 0.2 * (k % 3)) + k * 0.37) % 1.0
            bx = GX0 + 16 + (k * 23) % (GX1 - GX0 - 30) + 3 * math.sin(t * 7 + k)
            by = lerp(GBOT - 10, ey + 6, u)
            ctx.arc(bx, by, (4 + 3 * u) * b, 0, 2 * math.pi); setc(ctx, WHITE, 0.95 * b); ctx.fill_preserve()
            setc(ctx, INK2, 0.6 * b); ctx.set_line_width(1.5); ctx.stroke()
    # vapour wisps above the surface
    if b > 0.05 and ey < GBOT - 20:
        for k in range(4):
            u = (t * 0.7 + k * 0.25) % 1.0
            x = GX0 + 20 + k * 18 + 10 * math.sin(t * 3 + k); y = ey - 10 - 120 * u
            ctx.arc(x, y, 10 + 10 * u, 0, 2 * math.pi); setc(ctx, VAP, 0.45 * b * (1 - u)); ctx.fill()
    ctx.move_to(GX0, GTOP); ctx.line_to(GX0, GBOT); ctx.line_to(GX1, GBOT); ctx.line_to(GX1, GTOP)
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.move_to(GX0 + 12, GTOP + 20); ctx.line_to(GX0 + 12, GBOT - 30); setc(ctx, WHITE, 0.8); ctx.set_line_width(5); ctx.stroke()

def draw_molecules(ctx, t, st):
    a = clamp(st['mol'])
    if a <= 0: return
    ey = st['ey']
    for k in range(6):
        u = (t * 0.55 + k / 6) % 1.0
        x = GX0 + 18 + k * 12 + 30 * math.sin(k * 1.7) * u
        y = ey - 20 - 260 * u
        al = a * (1 - u) * clamp(u * 5)
        ctx.arc(x, y, 9, 0, 2 * math.pi); fill_stroke(ctx, VAP, lw=3, alpha=al)
        # each escaping molecule carries a little heat (red spark)
        ctx.arc(x + 9, y - 8, 4, 0, 2 * math.pi); setc(ctx, HEAT, al); ctx.fill()

def draw_heat_in(ctx, t, st):
    a = clamp(st['heat_in'])
    if a <= 0: return
    # FROM the water INTO the glass: arrows point inward (toward x = glass walls)
    for y in (1225, 1275):
        wavy_arrow(ctx, 318, y, GX0 - 6, y - 10, t, HEAT, a, amp=7, wl=34, lw=5, head=12)
        wavy_arrow(ctx, 602, y, GX1 + 6, y - 10, t, HEAT, a, amp=7, wl=34, lw=5, head=12)

def draw_pump(ctx, t, st):
    p = clamp(st['pump'])
    # pipe: from the plate (under the jar) to the bottom of the pump barrel
    ctx.move_to(640, PLATE[1] + 15); ctx.line_to(PX0 + 2, PLATE[1] + 15)
    setc(ctx, INK); ctx.set_line_width(20); ctx.stroke()
    ctx.move_to(640, PLATE[1] + 15); ctx.line_to(PX0 + 2, PLATE[1] + 15)
    setc(ctx, BRASS); ctx.set_line_width(12); ctx.stroke()
    # barrel
    ctx.rectangle(PX0, PTOP, PX1 - PX0, PBOT - PTOP); fill_stroke(ctx, BRASS, lw=5)
    ctx.rectangle(PX0 - 10, PBOT - 8, PX1 - PX0 + 20, 12); fill_stroke(ctx, BRASS_D, lw=4)
    # piston stroke (up = suck air out of the jar)
    stroke = 0.5 + 0.5 * math.sin(t * 6) if p > 0.05 else 0.0
    rod_top = lerp(905, 815, stroke * p)
    ctx.rectangle((PX0 + PX1) / 2 - 7, rod_top, 14, PTOP - rod_top + 30); fill_stroke(ctx, STEEL_L, lw=3)
    ctx.rectangle(PX0 - 40, rod_top - 18, PX1 - PX0 + 80, 20); fill_stroke(ctx, WOOD, lw=4)
    # spout (exhaust valve, top right of the barrel)
    ctx.rectangle(PX1, SPOUT[1] - 10, 34, 20); fill_stroke(ctx, BRASS_D, lw=4)

def draw_jar(ctx, t, st):
    ctx.rectangle(*PLATE); fill_stroke(ctx, STEEL, lw=5)
    jar_path(ctx); setc(ctx, GLASS, 0.30); ctx.fill()
    jar_path(ctx); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.arc(JCX, JTOP_SIDE - JR - 18, 20, 0, 2 * math.pi); fill_stroke(ctx, GLASS, lw=5)
    ctx.move_to(JX0 + 22, 1250); ctx.line_to(JX0 + 22, 960)
    ctx.arc_negative(JCX, JTOP_SIDE, JR - 22, math.pi, 1.3 * math.pi)
    setc(ctx, WHITE, 0.75); ctx.set_line_width(7); ctx.stroke()

def draw_outflow(ctx, t, st):
    """Air (red) or ether vapour (teal) going OUT: jar -> pipe -> pump -> spout -> room (to the right)."""
    for key, col, label in (('air_out', INK2, 'air'), ('vap_out', VAP, 'vap')):
        a = clamp(st[key])
        if a <= 0: continue
        # puffs travelling along the path
        path = [(460, 760), (600, 860), (640, 1290), (650, PLATE[1] + 15), (PX0, PLATE[1] + 15), ((PX0 + PX1) / 2, PBOT - 20),
                ((PX0 + PX1) / 2, SPOUT[1]), (SPOUT[0] + 34, SPOUT[1]), (SPOUT[0] + 160, SPOUT[1] - 40)]
        segs = [math.dist(p, q) for p, q in zip(path, path[1:])]; L = sum(segs)
        for k in range(9):
            d = ((t * 260 + k * L / 9) % L)
            for (p, q), sl in zip(zip(path, path[1:]), segs):
                if d <= sl:
                    u = d / sl; x = lerp(p[0], q[0], u); y = lerp(p[1], q[1], u); break
                d -= sl
            hidden = PX0 - 2 < x < PX1 + 2 and PTOP < y < PBOT
            if hidden: continue
            r = 11 if label == 'vap' else 8
            ctx.arc(x, y, r, 0, 2 * math.pi)
            if label == 'vap': fill_stroke(ctx, VAP, lw=3, alpha=a)
            else: setc(ctx, INK2, 0.75 * a); ctx.fill()
        straight_arrow(ctx, SPOUT[0] + 40, SPOUT[1], SPOUT[0] + 130, SPOUT[1] - 30, col, a, lw=7, head=14)

def draw_cullen(ctx, t, st):
    a = a_cullen(st)
    if a <= 0.01: return
    ctx.push_group()
    draw_table(ctx)
    draw_pump(ctx, t, st)
    draw_jar(ctx, t, st)
    draw_bowl_contents(ctx, t, st)
    draw_bowl(ctx)
    draw_glass(ctx, t, st)
    draw_heat_in(ctx, t, st)
    draw_molecules(ctx, t, st)
    draw_outflow(ctx, t, st)
    if st['therm_a'] > 0:
        thermometer(ctx, 580, 1290, st['therm'], clamp(st['therm_a']), color=lerpc(RED, COLD, 1 - st['therm'] / 0.55), h=190)
    highlight(ctx, (GX0 + GX1) / 2, 1180, 75, 140, HEAT, st['h_glass'], t)
    highlight(ctx, (PX0 + PX1) / 2, 1080, 85, 190, MUSTARD, st['h_pump'], t)
    highlight(ctx, 460, 1250, 175, 75, COLD, st['h_bowl'], t)
    highlight(ctx, SPOUT[0] + 70, SPOUT[1] - 20, 90, 50, VAP, st['h_spout'], t)
    tag(ctx, "ETHER", 300, 1080, INK, st['l_ether'])
    tag(ctx, "AIR OUT", 820, 920, INK2, st['l_air'])
    tag(ctx, "HEAT", 225, 1230, HEAT, st['l_heat'])
    tag(ctx, "0 °C · 32 °F", 460, 1395, COLD, st['l_ice'])
    tag(ctx, "VAPOUR OUT", 860, 920, TEAL, st['l_vap'])
    tag(ctx, "ETHER GONE", 300, 1080, RED, st['l_gone'])
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

# ---------------------------------------------------------------- fridge (side cut-away, door LEFT, back RIGHT)
FX0, FX1, FY0, FY1 = 290, 730, 430, 1470
FW = 34
EV_X0, EV_X1 = 390, 640
EV_Y = [500, 530, 560, 590]
CAP_X = 712                     # capillary inside the back wall
SUC_X = 748                     # suction line behind the back
RISE_X = 885                    # hot gas riser
CD_X0, CD_X1 = 775, 860         # condenser runs
CD_Y = [520 + 62 * k for k in range(12)]   # 520 .. 1202
COMP = (770, 1360, 120, 110)    # compressor dome x, y, w, h

def build_loop():
    pts = []; kinds = []
    def seg(p, k): pts.append(p); kinds.append(k)
    # evaporator serpentine (inlet right, top)
    seg((EV_X1, EV_Y[0]), 'evap')
    for i, y in enumerate(EV_Y):
        xa, xb = (EV_X1, EV_X0) if i % 2 == 0 else (EV_X0, EV_X1)
        seg((xa, y), 'evap'); seg((xb, y), 'evap')
    # suction: out through the back wall, down behind the fridge to the compressor
    seg((SUC_X, EV_Y[-1]), 'suct'); seg((SUC_X, 1405), 'suct'); seg((COMP[0] + 30, 1405), 'comp')
    seg((COMP[0] + 90, 1405), 'comp'); seg((COMP[0] + 90, COMP[1] + 10), 'comp')
    # hot gas up the riser, then the condenser zig-zag from TOP to BOTTOM
    seg((RISE_X, COMP[1] + 10), 'hot'); seg((RISE_X, CD_Y[0]), 'hot')
    for i, y in enumerate(CD_Y):
        xa, xb = (CD_X1, CD_X0) if i % 2 == 0 else (CD_X0, CD_X1)
        seg((xa, y), 'cond'); seg((xb, y), 'cond')
    # liquid line into the back wall, capillary up to the evaporator inlet
    last = pts[-1]
    seg((last[0], 1270), 'liq'); seg((CAP_X, 1270), 'liq'); seg((CAP_X, 470), 'capi'); seg((EV_X1, 470), 'capi')
    seg((EV_X1, EV_Y[0]), 'capi')
    # remove consecutive duplicates
    P, K = [pts[0]], [kinds[0]]
    for p, k in zip(pts[1:], kinds[1:]):
        if p != P[-1]: P.append(p); K.append(k)
    return P, K

LOOP, KINDS = build_loop()
SEGL = [math.dist(p, q) for p, q in zip(LOOP, LOOP[1:])]
LTOT = sum(SEGL)

def point_at(d):
    d %= LTOT
    for i, sl in enumerate(SEGL):
        if d <= sl:
            u = d / sl; p, q = LOOP[i], LOOP[i + 1]
            return lerp(p[0], q[0], u), lerp(p[1], q[1], u), KINDS[i + 1], i
        d -= sl
    p = LOOP[-1]; return p[0], p[1], KINDS[-1], len(SEGL) - 1

def kind_col(k, i):
    if k in ('evap',): return VAP
    if k == 'suct': return VAP
    if k == 'comp': return ORANGE
    if k == 'hot': return RED
    if k == 'cond':
        n0 = KINDS.index('cond'); n1 = len(KINDS) - 1 - KINDS[::-1].index('cond')
        u = clamp((i - n0) / max(1, n1 - n0)); return lerpc(RED, WATER, u)
    return WATER

def draw_pipes(ctx, reveal, a):
    if reveal <= 0: return
    lim = reveal * LTOT; d = 0
    for i, sl in enumerate(SEGL):
        if d >= lim: break
        p, q = LOOP[i], LOOP[i + 1]; u = clamp((lim - d) / sl)
        x1 = lerp(p[0], q[0], u); y1 = lerp(p[1], q[1], u)
        k = KINDS[i + 1]
        w = 6 if k in ('capi',) else 12
        ctx.move_to(*p); ctx.line_to(x1, y1); setc(ctx, INK, a); ctx.set_line_width(w + 6)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ctx.move_to(*p); ctx.line_to(x1, y1); setc(ctx, STEEL_L if k != 'evap' else hexc('#cfe9ea'), a); ctx.set_line_width(w); ctx.stroke()
        d += sl
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def draw_particles(ctx, t, a, n=64):
    if a <= 0: return
    for k in range(n):
        x, y, kind, i = point_at(t * 150 + k * LTOT / n)
        if COMP[0] < x < COMP[0] + COMP[2] and COMP[1] < y < COMP[1] + COMP[3]: continue
        col = kind_col(kind, i)
        r = 6 if kind != 'capi' else 4
        if kind == 'evap':
            # boiling inside the evaporator: bubbles grow along it
            ctx.arc(x, y, r, 0, 2 * math.pi); setc(ctx, WHITE, a); ctx.fill_preserve(); setc(ctx, TEAL, a); ctx.set_line_width(2); ctx.stroke()
        else:
            ctx.arc(x, y, r, 0, 2 * math.pi); setc(ctx, col, a); ctx.fill()

def draw_food(ctx, a):
    # two shelves of food, simple shapes
    for sy in (900, 1180):
        ctx.rectangle(FX0 + FW, sy, FX1 - FX0 - 2 * FW, 8); fill_stroke(ctx, STEEL_L, lw=3, alpha=a)
    rrect(ctx, 360, 790, 90, 110, 10); fill_stroke(ctx, hexc('#f2e2b0'), lw=4, alpha=a)      # milk
    ctx.rectangle(470, 840, 120, 60); fill_stroke(ctx, RED, lw=4, alpha=a)                   # cheese box
    ctx.arc(420, 1135, 42, 0, 2 * math.pi); fill_stroke(ctx, hexc('#7fae4f'), lw=4, alpha=a)  # lettuce
    rrect(ctx, 500, 1080, 130, 100, 12); fill_stroke(ctx, MUSTARD, lw=4, alpha=a)             # leftovers
    rrect(ctx, 380, 1330, 220, 90, 16); fill_stroke(ctx, hexc('#cfe9ea'), lw=4, alpha=a)      # crisper

def draw_fridge(ctx, t, st):
    a = a_fridge(st)
    if a <= 0.01: return
    ctx.push_group()
    # floor shadow + feet
    for x in (FX0 + 30, FX1 - 50):
        ctx.rectangle(x, FY1, 24, 24); fill_stroke(ctx, IRON_D, lw=3)
    # cabinet: insulation walls + interior
    ctx.rectangle(FX0, FY0, FX1 - FX0, FY1 - FY0); fill_stroke(ctx, FILL3, lw=6)
    ctx.rectangle(FX0 + FW, FY0 + FW, FX1 - FX0 - 2 * FW, FY1 - FY0 - 2 * FW); fill_stroke(ctx, hexc('#eaf4f4'), lw=4)
    # door edge on the left
    ctx.rectangle(FX0 - 22, FY0 + 6, 22, FY1 - FY0 - 12); fill_stroke(ctx, PAPER, lw=4)
    rrect(ctx, FX0 - 40, 700, 18, 160, 8); fill_stroke(ctx, STEEL, lw=3)
    draw_food(ctx, 1.0)
    # compressor (bottom back)
    x, y, w, h = COMP
    ctx.move_to(x, y + h); ctx.line_to(x, y + 40); ctx.curve_to(x, y - 6, x + w, y - 6, x + w, y + 40); ctx.line_to(x + w, y + h)
    ctx.close_path(); fill_stroke(ctx, IRON_D, lw=5)
    ctx.rectangle(x - 10, y + h, w + 20, 10); fill_stroke(ctx, INK2, lw=3)
    draw_pipes(ctx, st['reveal'], 1.0)
    draw_particles(ctx, t, clamp(st['flow']))
    # compressor highlight drawn on top of its pipe stubs
    ctx.move_to(x, y + h); ctx.line_to(x, y + 40); ctx.curve_to(x, y - 6, x + w, y - 6, x + w, y + 40); ctx.line_to(x + w, y + h)
    ctx.close_path(); fill_stroke(ctx, IRON_D, lw=5)
    text_c(ctx, "M", x + w / 2, y + 72, 30, WHITE, True, 0, 0.8)
    # heat out of the condenser, to the RIGHT (into the room behind the fridge)
    ho = clamp(st['heat_out'])
    if ho > 0:
        for yy in (620, 800, 980, 1160):
            wavy_arrow(ctx, 900, yy, 1010, yy - 20, t, HEAT, ho, amp=8, wl=34, lw=6, head=14)
    # heat from the food UP into the evaporator
    hf = clamp(st['heat_food'])
    if hf > 0:
        for xx, y0 in ((405, 780), (530, 830), (620, 1060)):
            wavy_arrow(ctx, xx, y0, xx + 10, 625, t, HEAT, hf, amp=7, wl=32, lw=5, head=12)
    highlight(ctx, x + w / 2, y + h / 2, 95, 75, MUSTARD, st['h_comp'], t)
    highlight(ctx, (CD_X0 + RISE_X) / 2, 860, 90, 380, RED, st['h_cond'], t)
    highlight(ctx, (EV_X0 + EV_X1) / 2, 545, 150, 70, COLD, st['h_evap'], t)
    tag(ctx, "PERKINS · 1834", 510, 380, INK, st['l_perkins'])
    tag(ctx, "PUMP · COMPRESSOR", 600, 1300, MUSTARD, st['l_comp'] * (1 - st['l_recap']) + st['l_recap'] * 0)
    tag(ctx, "SQUEEZE", 600, 1300, MUSTARD, st['l_recap'])
    tag(ctx, "HOT · BACK TO LIQUID", 690, 380, RED, st['l_cond'] * (1 - st['l_recap']))
    tag(ctx, "HEAT OUT", 830, 380, RED, st['l_recap'])
    tag(ctx, "BOILS AT -12 °C · 11 °F", 510, 660, COLD, st['l_evap'])
    tag(ctx, "BOILS", 510, 660, COLD, st['l_boil'])
    if st['l_recap'] > 0:
        rrect(ctx, 320, 960, 380, 100, 16); setc(ctx, CREAM, 0.95 * st['l_recap']); ctx.fill_preserve()
        setc(ctx, INK, st['l_recap']); ctx.set_line_width(4); ctx.stroke()
        text_c(ctx, "FRIDGE =", 510, 1002, 30, INK, True, 2, st['l_recap'])
        text_c(ctx, "BOILING, RECYCLED", 510, 1042, 30, TEAL, True, 2, st['l_recap'])
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

# ---------------------------------------------------------------- camera
CUL = (535, 1030, 1.12)
FRI = (620, 940, 1.0)
CAMKEYS = [(0, *CUL), (B(2), 590, 1020, 1.08), (B(4), *CUL), (B(5), 460, 1170, 1.18), (B(6), *CUL),
           (B(7), 600, 1010, 1.06), (M0 + 0.3, *FRI)]
def CAM(t): return cam_track(CAMKEYS, t)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    st = state(t)
    draw_cullen(ctx, t, st)
    draw_fridge(ctx, t, st)

def draw_hud(ctx, t, E):
    pop_word(ctx, "ICE!", t - 1.0, 1.6, COLD, cx=540, cy=400, size=130)
    pop_word(ctx, "FROZEN!", t - (B(5) + 2.4), 1.6, COLD, cx=540, cy=320, size=110)

SFX = [(1.0, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.4, 'pop'), (B(2) + 1.5, 'click'), (B(4) + 0.3, 'pop'),
       (B(5) + 1.1, 'pop'), (B(7) + 0.3, 'pop'), (B(7) + 2.7, 'pop'), (M0 + 0.9, 'pop'), (M0 + 2.7, 'click'),
       (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop'), (B(11) + 0.4, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def mini_jar(ctx, cx, a, n_arrows, boil, t, label):
    x0, x1, y0, y1 = cx - 110, cx + 110, 300, 520
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); setc(ctx, GLASS, 0.5 * a); ctx.fill()
    ctx.rectangle(x0 + 40, 440, x1 - x0 - 80, 75); setc(ctx, ETHER, a); ctx.fill()
    ctx.move_to(x0 + 40, 440); ctx.line_to(x1 - 40, 440); setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(x0, y0); ctx.line_to(x0, y1); ctx.line_to(x1, y1); ctx.line_to(x1, y0)
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    # air pressure arrows pushing DOWN on the surface
    xs = [x0 + 30 + k * (x1 - x0 - 60) / max(1, n_arrows - 1) for k in range(n_arrows)] if n_arrows > 1 else [cx]
    for k, x in enumerate(xs):
        straight_arrow(ctx, x, 320 + 6 * math.sin(t * 5 + k), x, 425, INK2, a, lw=5, head=11)
    if boil > 0:
        for k in range(7):
            u = (t * 1.4 + k * 0.29) % 1.0
            bx = x0 + 52 + k * 20; by = lerp(510, 446, u)
            ctx.arc(bx, by, 4 + 4 * u, 0, 2 * math.pi); setc(ctx, WHITE, a * boil); ctx.fill_preserve()
            setc(ctx, INK2, a * boil); ctx.set_line_width(1.5); ctx.stroke()
    text_c(ctx, label, cx, 280, 22, INK, True, 1.5, a)

def card_pressure(ctx, t, lt, a):
    card_frame(ctx, "LESS AIR ON TOP", a, "LESS PRESSURE = BOILS COOLER", TEAL)
    k1 = a * ease((lt - 0.1) / 0.5); k2 = a * ease((lt - 1.0) / 0.5)
    mini_jar(ctx, 300, k1, 7, 0.0, t, "FULL AIR · CALM")
    mini_jar(ctx, 780, k2, 2, 1.0, t, "AIR PUMPED OUT · BOILS")
    straight_arrow(ctx, 450, 420, 630, 420, TEAL, k2, lw=6, head=14)

def card_sweat(ctx, t, lt, a):
    card_frame(ctx, "SWEAT DOES IT TOO", a, "1 g TAKES 2 260 J · 2.1 BTU", RED)
    k = ease((lt - 0.1) / 0.5) * a
    # skin
    ctx.rectangle(160, 470, 760, 60); fill_stroke(ctx, hexc('#e7b48f'), lw=4, alpha=k)
    text_c(ctx, "SKIN", 230, 512, 22, WOOD_D, True, 1.5, k)
    # drop shrinks as it evaporates
    sh = clamp(1 - (lt - 1.0) / 4.0, 0.25, 1.0)
    cx, by = 540, 470
    r = 46 * sh
    ctx.move_to(cx, by - 2.4 * r); ctx.curve_to(cx + r * 0.4, by - 1.6 * r, cx + r, by - r, cx + r, by - 0.3 * r)
    ctx.curve_to(cx + r, by + 0.1 * r, cx - r, by + 0.1 * r, cx - r, by - 0.3 * r)
    ctx.curve_to(cx - r, by - r, cx - r * 0.4, by - 1.6 * r, cx, by - 2.4 * r); ctx.close_path()
    fill_stroke(ctx, WATER, lw=4, alpha=k)
    # heat leaves the SKIN, goes into the drop and away with the vapour (arrows point UP)
    for dx in (-60, 60):
        wavy_arrow(ctx, cx + dx, 520, cx + dx * 1.6, 290, t, HEAT, k, amp=7, wl=30, lw=5, head=12)
    for j in range(3):
        u = (t * 0.6 + j / 3) % 1.0
        ctx.arc(cx - 30 + j * 30, by - 2.6 * r - 120 * u, 10 + 8 * u, 0, 2 * math.pi); setc(ctx, VAP, 0.6 * k * (1 - u)); ctx.fill()

CARDS = {'pressure': card_pressure, 'sweat': card_sweat}
