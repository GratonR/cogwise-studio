"""Cogwise episode: Your oven has no flame, just up to three glowing tubes.
One idea (Guillaume, 16 nov., étape 3): how an electric oven makes its heat. Every heater is the same thing
(steel sheath + resistance wire + magnesium-oxide powder). 1 = BOTTOM element (sole), often hidden under the
enamelled floor; 2 = TOP element (voute / grill / broil) along the ceiling; 3 = on some ovens, a coiled RING
element around the rear fan (fan oven, "chaleur tournante", true / European convection).

VIEW (screen coordinates, y grows DOWN): SIDE VIEW / SECTION of a built-in oven. The FRONT faces LEFT.
  - door on the LEFT (x 210-290) with three glass panes; handle further left.
  - cavity x 300-830, y 620-1230. Insulation (hatched): top, back (right), bottom (y 1290-1340).
  - FLOOR = enamelled steel sheet y 1230-1242. BOTTOM element = tube UNDER the floor (centre y 1266);
    its terminals bend DOWN at the back and go out through the back wall (right).
  - TOP element = tube just under the ceiling (centre y 662); terminals bend UP at the back, out through the back wall.
  - FAN COVER: vertical plate x 772 in front of the back wall, y 800-1060, intake hole in its centre (y 900-960).
    Fan blades (edge-on) at x 812 between cover and back wall; motor behind the back wall (x 880-905).
    RING element: a ring around the fan in a plane parallel to the back wall; the section cuts it at the
    top and bottom -> two round cross-sections at (806, 930 +- 92).
  - heat directions: floor -> UP (decreasing y); top element -> DOWN (increasing y).
  - fan air: sucked IN at the centre (moving RIGHT into the hole), blown OUT at the top and bottom edges of the
    cover (moving LEFT), along ceiling / floor to the door, back RIGHT through the middle to the fan.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="oven-elements",
    title="Your oven has no flame. Just up to 3 glowing tubes 🔥 #Shorts",
    description=("No fire in there: a bottom heater, a top heater, and sometimes a ring behind the fan.\n\n"
                 "#Shorts #howthingswork #appliances #oven #cogwise"),
    hashtags=["Shorts", "howthingswork", "appliances", "oven", "cogwise"],
    sources=[
        "https://www.kitchenaid.com/pinch-of-help/major-appliances/how-do-ovens-work.html",
        "https://products.geappliances.com/appliance/gea-support-search-content?contentId=18231",
        "https://blog.yaleappliance.com/what-does-convection-mean-different-types-of-convection-cooking-explained",
        "https://www.appliancepartspros.com/b/?p=5946",
        "https://inspectandtest.net/guides/oven-heating-element/",
    ],
)

BEATS = [
    dict(dur=4.8, title="NO FLAME?", caption="Your oven has no flame. It heats with up to three glowing tubes."),
    dict(dur=5.0, title="THE SECRET", caption="Each one works like a toaster wire, just much bigger and tougher."),
    dict(dur=5.4, title="THE TUBE", caption="It's a steel tube, with a resistance wire packed in mineral powder."),
    dict(dur=5.8, title=None, caption="Current heats the wire. The powder lets heat out, but never the electricity.", card='tube'),
    dict(dur=5.6, title="1 · BOTTOM", caption="The first one sits at the bottom, often hidden right under the oven floor."),
    dict(dur=5.8, title="BOTTOM HEAT", caption="It warms the floor, which radiates upward and sets warm air rising."),
    dict(dur=5.4, title="2 · TOP", caption="The second one runs along the ceiling. That's the top heater, or grill."),
    dict(dur=5.4, title="GRILL", caption="It beams intense heat straight down, browning the top of your food."),
    dict(dur=5.8, title="TOP + BOTTOM", caption="Bottom alone crisps a base. Top alone browns. Together, they bake evenly."),
    dict(dur=5.8, title="3 · THE RING", caption="Some ovens hide a third one at the back: a coiled ring, like a snail."),
    dict(dur=6.0, title=None, caption="It circles a fan, which pushes the hot air all around the food.", card='ring'),
    dict(dur=5.4, title="WIRE = FIRE", caption="No flame anywhere. Just wires glowing hot, in exactly the right places."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sst(t, t0, d=0.18):
    return ease(clamp((t - t0) / d))

STEEL = hexc('#9aa3ab'); STEEL_D = hexc('#6d757c')
GLASS = hexc('#bfe3df'); HOT = hexc('#ff5a2a'); GLOW = hexc('#ff8a3a')
CAV = hexc('#3a3640'); CAV_WARM = hexc('#4e3530')
ENAMEL = hexc('#2f4a63'); ENAMEL_HI = hexc('#7fa3c4')
INSUL = hexc('#f3d98a'); COPPER = hexc('#c46d2e')
POWDER = hexc('#f1ede4')
CRUST = hexc('#d9952f'); PALE = hexc('#efe0b0'); FILLING = hexc('#9c3a3a')

# ---------------------------------------------------------------- geometry
BX0, BX1, BY0, BY1 = 200, 910, 400, 1380      # oven body
CX0, CX1, CY0, CY1 = 300, 830, 620, 1230      # cavity (inside); CY1 = top face of the floor
FL_T = 12                                      # floor sheet thickness
TUBE_Y, TUBE_R = 1266, 11                      # bottom element (centre line, radius)
TOP_Y = 662                                    # top element centre line
TUBE_X0, TUBE_X1 = 330, 800                    # front bend .. back bend
TOP_X1 = 740                                   # top element back bend (in front of the fan cover)
INS = 50
IB0 = 1290                                     # bottom insulation top
DX0, DX1, DY0, DY1 = 210, 290, 520, 1330      # door
SHELF_Y = 980
PIE = (520, SHELF_Y - 26, 120, 26)             # cx, cy, half width, half height
FAN_X, FAN_Y = 812, 930                        # fan blades (edge-on), axis horizontal
COV_X, COV_Y0, COV_Y1 = 772, 800, 1060         # fan cover plate
RING_R = 92                                    # ring element radius (around the fan axis)

def state(t):
    s = {}
    # hook: under-floor space opens, then the three heaters light up one after the other (all before 2 s)
    s['reveal'] = sst(t, 0.2, 0.5)
    k1, k2, k3 = sst(t, 0.4, 0.4), sst(t, 0.9, 0.4), sst(t, 1.4, 0.4)
    off_b1 = 1 - 0.6 * win(t, B(1) + 0.2, B(4) + 0.3, 0.4)        # dims while we explain the tube
    # bottom element: on in the hook, during 2-6 and 9, recap
    bot = k1 * (1 - sst(t, B(1), 0.4))
    bot = max(bot, win(t, B(2) + 0.2, B(6) + 0.2, 0.4), win(t, B(8) + 0.1, B(9) + 0.2, 0.4), sst(t, B(11) + 0.4, 0.4))
    s['bot'] = bot
    top = k2 * (1 - sst(t, B(1), 0.4))
    top = max(top, win(t, B(6) + 0.3, B(9) + 0.2, 0.4), sst(t, B(11) + 0.9, 0.4))
    s['top'] = top
    ring = k3 * (1 - sst(t, B(1), 0.4))
    ring = max(ring, win(t, B(9) + 0.6, B(11) + 0.3, 0.4), sst(t, B(11) + 1.4, 0.4))
    s['ring'] = ring
    s['fan_on'] = max(win(t, B(10) + 0.0, B(11) + 0.3, 0.4), 0.0)
    # floor glow (bottom heat) beats 5-6 and 9
    fl = max(win(t, B(5) + 0.4, B(6) + 0.3, 1.2), 0.8 * win(t, B(8) + 0.4, B(9) + 0.2, 0.6))
    s['floor_glow'] = fl
    s['air'] = win(t, B(5) + 2.0, B(6) + 0.2, 0.4)
    s['fanair'] = win(t, B(10) + 0.3, B(11) + 0.3, 0.4)
    s['pie'] = win(t, B(7) + 0.1, B(9) + 0.1, 0.35)
    s['downheat'] = max(win(t, B(7) + 0.3, B(8) + 0.1, 0.4), win(t, B(8) + 0.2, B(9), 0.4))
    s['upheat_pie'] = win(t, B(8) + 0.3, B(9), 0.4)
    # zoom on the floor + bottom tube for beats 3 and 5
    s['z'] = max(win(t, B(2) + 0.05, B(3) + 0.3, 0.6), win(t, B(4) + 0.05, B(5) + 0.3, 0.6))
    return s

def CAM(t):
    """Camera (engine clips the stage to y < 1500): beats 3 and 5 zoom on the floor + bottom tube."""
    z = ease(state(t)['z'])
    return lerp(540, 560, z), lerp(900, 1180, z), lerp(1, 1.7, z)

# ---------------------------------------------------------------- pieces
def hatch(ctx, x, y, w, h, a=1):
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    ctx.rectangle(x, y, w, h); setc(ctx, INSUL, a); ctx.fill()
    for k in range(-int(h), int(w) + int(h), 18):
        ctx.move_to(x + k, y + h); ctx.line_to(x + k + h, y)
    setc(ctx, hexc('#c9a24a'), a); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    ctx.rectangle(x, y, w, h); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()

def bottom_path(ctx, y=TUBE_Y):
    """Bottom element seen from the side: front bend (left), straight run, back bend DOWN then RIGHT
    through the back wall (terminals at the rear)."""
    ctx.move_to(TUBE_X1 + 70, y + 14)
    ctx.line_to(TUBE_X1 + 10, y + 14)
    ctx.curve_to(TUBE_X1 - 10, y + 14, TUBE_X1 - 10, y, TUBE_X1 - 26, y)
    ctx.line_to(TUBE_X0, y)

def top_path(ctx):
    """Top element: runs under the ceiling, back bend goes UP then RIGHT through the back wall (above the fan cover)."""
    ctx.move_to(CX1 + 40, CY0 + 14)
    ctx.line_to(TOP_X1 + 30, CY0 + 14)
    ctx.curve_to(TOP_X1 + 10, CY0 + 14, TOP_X1 + 10, TOP_Y, TOP_X1 - 10, TOP_Y)
    ctx.line_to(TUBE_X0, TOP_Y)

def draw_tube(ctx, pathf, hot, a=1.0):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    pathf(ctx); setc(ctx, INK, a); ctx.set_line_width(2 * TUBE_R + 6); ctx.stroke()
    pathf(ctx); setc(ctx, lerpc(STEEL_D, HOT, hot), a); ctx.set_line_width(2 * TUBE_R); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def fan_angle(t):
    return 9.0 * max(0.0, t - B(10))

def fan_unit(ctx, t, s):
    """Fan cover plate (in front of the back wall), fan blades edge-on, ring cross-sections, motor outside."""
    # motor behind the back wall (right) + shaft
    rrect(ctx, 880, FAN_Y - 26, 24, 52, 6); fill_stroke(ctx, STEEL_D, lw=3)
    ctx.move_to(FAN_X, FAN_Y); ctx.line_to(884, FAN_Y); setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()
    # blades edge-on: a thin vertical paddle whose visible height pulses as it spins
    ph = abs(math.cos(fan_angle(t))) if s['fan_on'] > 0.05 else 1.0
    h = 18 + 52 * ph
    rrect(ctx, FAN_X - 5, FAN_Y - h, 10, 2 * h, 4); fill_stroke(ctx, STEEL, lw=3)
    # ring element: two cross-sections (top and bottom of the ring)
    for sg in (-1, 1):
        ctx.arc(806, FAN_Y + sg * RING_R, TUBE_R, 0, 2 * math.pi)
        fill_stroke(ctx, lerpc(STEEL_D, HOT, s['ring']), lw=3)
    # cover plate with a centre intake hole
    for y0, y1 in ((COV_Y0, 900), (960, COV_Y1)):
        ctx.rectangle(COV_X - 4, y0, 8, y1 - y0); fill_stroke(ctx, STEEL, lw=2)

def oven(ctx, t, s):
    rrect(ctx, BX0, BY0, BX1 - BX0, BY1 - BY0, 14); fill_stroke(ctx, FILL2, lw=6)
    rrect(ctx, BX0 - 16, BY0 + 4, 26, 110, 6); fill_stroke(ctx, FILL3, lw=3)
    hatch(ctx, CX0, CY0 - INS, CX1 + INS - CX0, INS)
    hatch(ctx, CX1, CY0, INS, IB0 + INS - CY0)
    hatch(ctx, CX0, IB0, CX1 - CX0, INS)
    ctx.rectangle(CX0, CY1, CX1 - CX0, IB0 - CY1); setc(ctx, CAV); ctx.fill()
    fg = s['floor_glow']
    ctx.rectangle(CX0, CY0, CX1 - CX0, CY1 - CY0); fill_stroke(ctx, lerpc(CAV, CAV_WARM, 0.8 * fg), lw=4)
    if fg > 0.05:
        g = cairo.LinearGradient(0, CY1, 0, CY1 - 380)
        g.add_color_stop_rgba(0, 1.0, 0.5, 0.18, 0.35 * fg); g.add_color_stop_rgba(1, 1.0, 0.5, 0.18, 0.0)
        ctx.rectangle(CX0, CY1 - 380, CX1 - CX0, 380); ctx.set_source(g); ctx.fill()
    pa = s['pie']
    if pa > 0:
        ctx.move_to(CX0 + 30, SHELF_Y); ctx.line_to(COV_X - 14, SHELF_Y); setc(ctx, STEEL, pa); ctx.set_line_width(5); ctx.stroke()
    fan_unit(ctx, t, s)
    # top element (terminals through the back wall, top right) + wires
    draw_tube(ctx, top_path, s['top'])
    for dy in (6, 18):
        ctx.move_to(CX1 + 40, CY0 + dy); ctx.line_to(BX1 - 10, CY0 + dy - 40)
        setc(ctx, COPPER); ctx.set_line_width(3); ctx.stroke()
    # bottom element + wires
    draw_tube(ctx, bottom_path, s['bot'])
    for dy in (8, 20):
        ctx.move_to(TUBE_X1 + 70, TUBE_Y + dy); ctx.line_to(BX1 - 10, TUBE_Y + dy + 30)
        setc(ctx, COPPER); ctx.set_line_width(3); ctx.stroke()
    rv = 1 - s['reveal']
    if rv > 0:
        ctx.rectangle(CX0, CY1 + FL_T, CX1 - CX0, IB0 - CY1 - FL_T); setc(ctx, FILL3, rv); ctx.fill()
    ctx.rectangle(CX0, CY1, CX1 - CX0, FL_T); fill_stroke(ctx, lerpc(ENAMEL, GLOW, 0.85 * fg), lw=3)
    ctx.move_to(CX0 + 20, CY1 + 3); ctx.line_to(CX1 - 60, CY1 + 3); setc(ctx, ENAMEL_HI, 0.8 * (1 - fg)); ctx.set_line_width(2); ctx.stroke()
    rrect(ctx, DX0, DY0, DX1 - DX0, DY1 - DY0, 10); fill_stroke(ctx, FILL3, lw=5)
    for x in (228, 250, 272):
        ctx.rectangle(x - 4, 600, 8, 660); fill_stroke(ctx, GLASS, lw=2)
    ctx.move_to(DX0, 560); ctx.line_to(170, 560); ctx.line_to(170, 640); ctx.line_to(DX0, 640)
    setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()

def heat_up(ctx, t, s):
    """Bottom: tube -> floor (short arrows UP), floor -> cavity (wavy arrows UP, decreasing y)."""
    a = s['floor_glow']
    tube_a = s['bot'] * win(t, B(4) + 0.8, B(5) + 0.6, 0.4)
    for i in range(5):
        x = CX0 + 70 + i * 90
        if tube_a > 0:
            straight_arrow(ctx, x, TUBE_Y - 14, x, CY1 + FL_T + 2, ORANGE, tube_a, lw=4, head=7)
        if a > 0.1:
            wavy_arrow(ctx, x + 20, CY1 - 14, x + 20, CY1 - 150, t, ORANGE, 0.85 * a * (1 - s['air']), amp=5, wl=24, lw=4, head=10)

def heat_down(ctx, t, s):
    """Top element beams heat DOWN (increasing y) onto the pie; beat 9 also from below (UP onto the dish)."""
    a = s['downheat']
    cx, cy, hw, hh = PIE
    for i in range(4):
        x = cx - 90 + i * 60
        if a > 0:
            wavy_arrow(ctx, x, TOP_Y + 22, x, cy - hh - 26, t, RED, 0.85 * a, amp=5, wl=22, lw=4, head=10)
        u = s['upheat_pie']
        if u > 0:
            wavy_arrow(ctx, x + 20, CY1 - 14, x + 20, SHELF_Y + 20, t, ORANGE, 0.85 * u, amp=5, wl=22, lw=4, head=10)

LOOP_L = [(520, 1200), (520, 760), (330, 720), (325, 1180), (500, 1205)]
LOOP_R = [(520, 1200), (520, 760), (740, 720), (745, 1180), (540, 1205)]
# fan oven: out at the top edge of the cover (going LEFT), along the ceiling, down the door, back RIGHT to the hole
FAN_TOP = [(COV_X - 10, COV_Y0 - 8), (360, 712), (325, 890), (560, 925), (COV_X - 6, 930)]
FAN_BOT = [(COV_X - 10, COV_Y1 + 8), (360, 1195), (325, 975), (560, 940), (COV_X - 6, 935)]
def _poly(pts, u):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(seg) * (u % 1)
    for i, d in enumerate(seg):
        if L <= d or i == len(seg) - 1:
            k = clamp(L / d); p, q = pts[i], pts[i + 1]
            return lerp(p[0], q[0], k), lerp(p[1], q[1], k), math.atan2(q[1] - p[1], q[0] - p[0])
        L -= d

def _loop(ctx, t, pts, a, ph, speed, n, colf):
    ctx.new_path(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.set_dash([6, 12]); setc(ctx, TEAL_L, 0.6 * a); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    for k in range(n):
        u = (t * speed + k / n + ph / n) % 1
        x, y, an = _poly(pts, u)
        ctx.save(); ctx.translate(x, y); ctx.rotate(an)
        ctx.move_to(12, 0); ctx.line_to(-8, -9); ctx.line_to(-8, 9); ctx.close_path()
        setc(ctx, colf(u), a); ctx.fill()
        ctx.restore()

def air_loops(ctx, t, s):
    a = s['air']
    if a > 0:   # bottom heat: rises in the middle, sinks along the door and the back
        for pts, ph in ((LOOP_L, 0.0), (LOOP_R, 0.5)):
            _loop(ctx, t, pts, a, ph, 0.18, 5, lambda u: ORANGE if u < 0.45 else TEAL)
    a = s['fanair']
    if a > 0:   # fan oven: hot leaving the ring, cooler coming back to the intake
        for pts, ph in ((FAN_TOP, 0.0), (FAN_BOT, 0.5)):
            _loop(ctx, t, pts, a, ph, 0.32, 6, lambda u: RED if u < 0.5 else ORANGE)

def pie(ctx, t, s):
    a = s['pie']
    if a <= 0: return
    cx, cy, hw, hh = PIE
    k = sst(t, B(7) + 1.0, 1.6)                     # top browns under the grill
    kb = sst(t, B(8) + 1.0, 1.6)                    # bottom crust browns once the bottom heater joins
    ctx.move_to(cx - hw - 12, cy - hh); ctx.line_to(cx - hw + 6, cy + hh); ctx.line_to(cx + hw - 6, cy + hh); ctx.line_to(cx + hw + 12, cy - hh)
    setc(ctx, STEEL_D, a); ctx.set_line_width(5); ctx.stroke()
    ctx.rectangle(cx - hw + 6, cy + hh - 14, 2 * hw - 12, 14); setc(ctx, lerpc(PALE, CRUST, kb), a); ctx.fill()
    ctx.rectangle(cx - hw + 2, cy - hh + 12, 2 * hw - 4, 2 * hh - 26); setc(ctx, FILLING, a); ctx.fill()
    ctx.move_to(cx - hw - 8, cy - hh + 12); ctx.curve_to(cx - 40, cy - hh - 18, cx + 40, cy - hh - 18, cx + hw + 8, cy - hh + 12)
    ctx.close_path(); setc(ctx, lerpc(PALE, CRUST, k), a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    ctx.save()
    cx, cy, z = CAM(t)
    if z > 1.001:
        ytop = (420 - 900) / z + cy
        ctx.rectangle(-2000, ytop, 5000, 5000); ctx.clip()
    oven(ctx, t, s)
    heat_up(ctx, t, s)
    air_loops(ctx, t, s)
    pie(ctx, t, s)
    heat_down(ctx, t, s)
    ctx.restore()

# ---------------------------------------------------------------- labels (screen space)
def labels(ctx, t, s):
    a = win(t, 0.4, B(1) + 0.1, 0.25)
    if a > 0:
        tag(ctx, "1 · BOTTOM", 540, 1430, RED, a * sst(t, 0.4), 28)
        tag(ctx, "2 · TOP", 520, 735, RED, a * sst(t, 0.9), 28)
        tag(ctx, "3 · RING", 640, 1010, RED, a * sst(t, 1.4), 28)
    a = bw(t, 2)
    if a > 0:
        tag(ctx, "STEEL TUBE", 540, 1430, RED, a * sst(t, B(2) + 0.4), 30)
    a = bw(t, 4)
    if a > 0:
        tag(ctx, "ENAMELLED STEEL FLOOR", 540, 980, TEAL, a * sst(t, B(4) + 0.4), 28)
        tag(ctx, "1 · BOTTOM HEATER", 540, 1430, RED, a * sst(t, B(4) + 1.4), 28)
    a = bw(t, 5)
    if a > 0:
        highlight(ctx, 545, CY1 + 6, 280, 30, ORANGE, a * (1 - s['air']), t)
        tag(ctx, "HOT FLOOR GLOWS UP", 545, 1430, ORANGE, a * (1 - s['air']), 28)
        tag(ctx, "WARM AIR RISES", 545, 1430, TEAL, a * s['air'], 28)
    a = bw(t, 6)
    if a > 0:
        highlight(ctx, 535, TOP_Y, 240, 30, RED, a * sst(t, B(6) + 0.3), t)
        tag(ctx, "2 · TOP HEATER (GRILL)", 540, 760, RED, a * sst(t, B(6) + 0.6), 28)
    a = bw(t, 7)
    if a > 0:
        tag(ctx, "BROWNS THE TOP", 540, 1430, RED, a * sst(t, B(7) + 1.2), 28)
    a = bw(t, 9)
    if a > 0:
        highlight(ctx, 800, FAN_Y, 70, 150, RED, a * sst(t, B(9) + 0.6), t)
        tag(ctx, "3 · RING HEATER", 600, 1100, RED, a * sst(t, B(9) + 0.8), 28)
        tag(ctx, "SOME OVENS ONLY", 540, 1430, INK, a * sst(t, B(9) + 1.6), 26)
    a = bw(t, 10)
    if a > 0:
        tag(ctx, "FAN SPREADS THE HEAT", 540, 1430, RED, a * sst(t, B(10) + 0.6), 28)

# ---------------------------------------------------------------- HUD (top zone, y 175-375)
def _panel(ctx, a, x=60, y=180, w=960, h=195):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def hud_toaster(ctx, t, a):
    _panel(ctx, a)
    k = sst(t, B(1) + 1.8, 0.4)
    text_c(ctx, "TOASTER WIRE", 290, 245, 30, INK, True, 2, a)
    ctx.move_to(170, 315)
    for i in range(12):
        ctx.line_to(180 + i * 20, 300 if i % 2 == 0 else 330)
    setc(ctx, HOT, a); ctx.set_line_width(4); ctx.stroke()
    straight_arrow(ctx, 470, 315, 600, 315, INK, a * k, lw=6, head=14)
    text_c(ctx, "OVEN HEATER", 800, 245, 30, RED, True, 2, a * k)
    ctx.move_to(680, 315); ctx.line_to(920, 315)
    setc(ctx, INK, a * k); ctx.set_line_width(30); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.move_to(680, 315); ctx.line_to(920, 315)
    setc(ctx, HOT, a * k); ctx.set_line_width(22); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    text_c(ctx, "SAME IDEA · BIGGER · SEALED", 540, 362, 20, INK2, True, 2, a * k)

def _mode(ctx, cx, label, sub, top, bot, a):
    ctx.rectangle(cx - 90, 262, 180, 80); fill_stroke(ctx, CAV, lw=3, alpha=a)
    for on, y in ((top, 274), (bot, 330)):
        ctx.move_to(cx - 70, y); ctx.line_to(cx + 70, y)
        setc(ctx, HOT if on else STEEL_D, a); ctx.set_line_width(8); ctx.stroke()
    text_c(ctx, label, cx, 238, 24, RED, True, 2, a)
    text_c(ctx, sub, cx, 368, 20, INK, True, 1, a)

def hud_modes(ctx, t, a):
    _panel(ctx, a)
    k1, k2, k3 = (sst(t, B(8) + d, 0.3) for d in (0.2, 1.6, 3.0))
    _mode(ctx, 230, "BOTTOM", "CRISPS A BASE", False, True, a * k1)
    _mode(ctx, 540, "TOP", "BROWNS", True, False, a * k2)
    _mode(ctx, 850, "BOTH", "BAKES EVENLY", True, True, a * k3)

def hud_recap(ctx, t, a):
    _panel(ctx, a)
    k1, k2, k3 = (sst(t, B(11) + d, 0.25) for d in (0.3, 0.9, 1.5))
    text_c(ctx, "NO FLAME", 540, 240, 30, INK, True, 3, a)
    for i, (k, lab) in enumerate(((k1, "BOTTOM"), (k2, "TOP"), (k3, "RING"))):
        cx = 250 + i * 290
        ctx.move_to(cx - 90, 300); ctx.line_to(cx + 90, 300)
        setc(ctx, INK, a * k); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ctx.move_to(cx - 90, 300); ctx.line_to(cx + 90, 300)
        setc(ctx, HOT, a * k); ctx.set_line_width(18); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        text_c(ctx, lab, cx, 356, 24, RED, True, 2, a * k)

def draw_hud(ctx, t, E):
    s = state(t)
    labels(ctx, t, s)
    a = win(t, B(1) + 0.2, B(2) + 0.05, 0.3)
    if a > 0: hud_toaster(ctx, t, a)
    a = win(t, B(8) + 0.1, B(9) + 0.05, 0.3)
    if a > 0: hud_modes(ctx, t, a)
    a = win(t, B(11) + 0.2, B(12) + 0.1, 0.3)   # gone before the end card (owl + wordmark)
    if a > 0: hud_recap(ctx, t, a)

SFX = [(0.4, 'pop'), (0.9, 'pop'), (1.4, 'pop'), (B(1) + 1.8, 'pop'), (B(2) + 0.4, 'pop'),
       (B(4) + 0.4, 'pop'), (B(4) + 1.4, 'pop'), (B(5) + 0.4, 'pop'), (B(6) + 0.6, 'pop'), (B(7) + 1.2, 'pop'),
       (B(8) + 0.2, 'pop'), (B(8) + 1.6, 'pop'), (B(8) + 3.0, 'pop'), (B(9) + 0.8, 'pop'), (B(9) + 1.6, 'pop'),
       (B(10) + 0.6, 'click'), (B(11) + 0.3, 'pop'), (B(11) + 0.9, 'pop'), (B(11) + 1.5, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards (draw inside x 110..970, y 250..540)
def card_tube(ctx, t, lt, a):
    card_frame(ctx, "INSIDE THE TUBE", a, "HEAT GETS OUT · CURRENT STAYS IN", RED)
    x0, x1, yc, h = 200, 880, 400, 120
    rrect(ctx, x0, yc - h / 2, x1 - x0, h, 20); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    ctx.rectangle(x0 + 14, yc - h / 2 + 14, x1 - x0 - 28, h - 28); setc(ctx, POWDER, a); ctx.fill()
    rnd = random.Random(4)
    for i in range(160):
        ctx.arc(x0 + 20 + rnd.random() * (x1 - x0 - 40), yc - h / 2 + 18 + rnd.random() * (h - 36), 2, 0, 6.28)
        setc(ctx, INK2, 0.35 * a); ctx.fill()
    hot = sst(lt, 0.6, 1.2)
    ctx.move_to(x0 + 30, yc)
    n = 40
    for i in range(n + 1):
        x = lerp(x0 + 30, x1 - 30, i / n)
        ctx.line_to(x, yc + 20 * math.sin(i * math.pi / 2))
    setc(ctx, lerpc(COPPER, HOT, hot), a); ctx.set_line_width(5); ctx.stroke()
    for k in range(10):
        u = (lt * 0.25 + k / 10) % 1
        x = lerp(x0 + 30, x1 - 30, u)
        i = u * n
        ctx.arc(x, yc + 20 * math.sin(i * math.pi / 2), 6, 0, 6.28); setc(ctx, MUSTARD, a); ctx.fill_preserve()
        setc(ctx, INK, a); ctx.set_line_width(2); ctx.stroke()
    ha = a * sst(lt, 1.6, 0.6)
    for i in range(5):
        x = x0 + 90 + i * 125
        wavy_arrow(ctx, x, yc - 30, x, yc - h / 2 - 50, t, ORANGE, ha, amp=4, wl=18, lw=4, head=9)
        wavy_arrow(ctx, x + 40, yc + 30, x + 40, yc + h / 2 + 48, t, ORANGE, ha, amp=4, wl=18, lw=4, head=9)
    tag(ctx, "POWDER", 300, yc + h / 2 + 2, INK2, a * sst(lt, 2.4), 20)
    tag(ctx, "HOT WIRE", 540, yc - h / 2 - 2, RED, a * sst(lt, 1.0), 20)

def card_ring(ctx, t, lt, a):
    """Front view of the back wall: fan in the centre, coiled ring heater around it; air IN at the centre,
    OUT at the edges (arrows pointing away from the centre)."""
    card_frame(ctx, "BEHIND THE BACK WALL", a, "RING HEATS · FAN BLOWS", RED)
    cx, cy = 540, 400
    rrect(ctx, cx - 150, cy - 140, 300, 280, 20); fill_stroke(ctx, CAV, lw=4, alpha=a)
    # coiled ring (2 turns, like a snail shell / spiral)
    hot = sst(lt, 0.3, 1.0)
    ctx.new_path()
    for i in range(241):
        th = i / 240 * 4 * math.pi
        r = 82 + 26 * (i / 240)
        (ctx.line_to if i else ctx.move_to)(cx + r * math.cos(th), cy + r * math.sin(th))
    setc(ctx, INK, a); ctx.set_line_width(20); ctx.stroke_preserve()
    setc(ctx, lerpc(STEEL_D, HOT, hot), a); ctx.set_line_width(13); ctx.stroke()
    # fan blades (rotate clockwise on screen: angle grows)
    ang = lt * 6.0
    for k in range(6):
        th = ang + k * math.pi / 3
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(th)
        ctx.move_to(10, -8); ctx.curve_to(40, -26, 62, -14, 66, 0); ctx.line_to(10, 8); ctx.close_path()
        setc(ctx, STEEL, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(2.5); ctx.stroke()
        ctx.restore()
    ctx.arc(cx, cy, 13, 0, 6.28); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    # air: out at the edges (left and right of the panel), heated
    oa = a * sst(lt, 1.2, 0.5)
    for sg in (-1, 1):
        for dy in (-60, 0, 60):
            wavy_arrow(ctx, cx + sg * 160, cy + dy, cx + sg * 280, cy + dy, t, RED, oa, amp=4, wl=18, lw=4, head=9)

CARDS = {'tube': card_tube, 'ring': card_ring}
