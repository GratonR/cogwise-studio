"""Cogwise episode: Your oven's bottom heater is hidden under the floor.
One idea: in most modern ovens the bake ("bottom") element sits UNDER the enamelled steel floor. The element
(steel sheath + resistance wire + magnesium-oxide powder) heats the floor, the floor radiates upward like a
baking stone. Consequence: when it dies the floor still looks spotless, and pies come out pale underneath.

VIEW (screen coordinates, y grows DOWN): SIDE VIEW / SECTION of a built-in oven. The FRONT faces LEFT.
  - door on the LEFT (x 210-290) with three glass panes; handle further left.
  - cavity x 300-830, y 620-1230. Insulation (hatched): top, back (right), bottom (y 1290-1340).
  - the cavity FLOOR is an enamelled steel sheet, y 1230-1242 (top face y 1230 = the side food sees).
  - the hidden element is a tube running front-to-back UNDER the floor, centre y 1266; its two terminals
    bend down at the back and pass through the back wall (x 830-880) to the rear: wires leave on the RIGHT.
  - grill element: zigzag just under the ceiling (y 650-672); OFF in bake mode except the symptom beat.
  - heat from the floor goes UP (arrows pointing toward smaller y). Air loop: rises in the middle,
    spreads under the ceiling, comes DOWN along the door (left) and the back wall (right).
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="oven-elements",
    title="Your oven's bottom heater is hidden under the floor 🔥 #Shorts",
    description=("That smooth oven floor isn't just a floor. It's the lid over your bottom heater.\n\n"
                 "#Shorts #howthingswork #appliances #oven #cogwise"),
    hashtags=["Shorts", "howthingswork", "appliances", "oven", "cogwise"],
    sources=[
        "https://producthelp.maytag.com/Cooking/Wall_Ovens_and_Ranges/Oven_Product_Assistance/Long_Pre-Heat_Times_for_Oven",
        "https://www.appliancepartspros.com/b/?p=5946",
        "https://patents.google.com/patent/US6121584",
        "https://easybear-appliancerepair.com/blog/whirlpool-oven-heating-element-replacement-guide",
        "https://inspectandtest.net/guides/oven-heating-element/",
    ],
)

BEATS = [
    dict(dur=4.6, title="WAIT, WHERE?", caption="Your oven's bottom heater is hiding right under the floor."),
    dict(dur=5.4, title="THE SECRET", caption="Older ovens showed a bare coil down there. Newer ones tuck it underneath."),
    dict(dur=5.4, title="1 · THE ELEMENT", caption="It's a steel tube with a thin resistance wire packed in mineral powder."),
    dict(dur=5.8, title=None, caption="Current heats the wire. The powder lets heat out, but never the electricity.", card='tube'),
    dict(dur=5.4, title="2 · THE FLOOR", caption="The tube sits just under the oven floor: steel, coated in glossy enamel."),
    dict(dur=6.0, title="3 · THE GLOW", caption="The floor soaks up that heat, then radiates it upward, like a baking stone."),
    dict(dur=5.6, title="RISING AIR", caption="Air touching the hot floor warms, rises, and rolls around the whole oven."),
    dict(dur=6.0, title=None, caption="That steel is a buffer: preheat takes a little longer, but heat spreads more evenly.", card='buffer'),
    dict(dur=5.8, title="WHY HIDE IT?", caption="Spills land on smooth enamel instead of burning onto the coil. One wipe."),
    dict(dur=4.8, title="THE CLUE", caption="When the hidden heater dies, the floor still looks spotless."),
    dict(dur=5.0, title="THE SYMPTOM", caption="But pies come out golden on top and pale, soggy underneath."),
    dict(dur=5.6, title="FLOOR = HEATER", caption="So your oven floor isn't just a floor. It's the heater's lid."),
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
POWDER = hexc('#f1ede4'); SAUCE = hexc('#a5432a')
CRUST = hexc('#d9952f'); PALE = hexc('#efe0b0'); FILLING = hexc('#9c3a3a')

# ---------------------------------------------------------------- geometry
BX0, BX1, BY0, BY1 = 200, 910, 400, 1380      # oven body
CX0, CX1, CY0, CY1 = 300, 830, 620, 1230      # cavity (inside); CY1 = top face of the floor
FL_T = 12                                      # floor sheet thickness
TUBE_Y, TUBE_R = 1266, 11                      # hidden element (centre line, radius)
TUBE_X0, TUBE_X1 = 330, 800                    # front bend .. back bend
INS = 50
IB0 = 1290                                     # bottom insulation top
DX0, DX1, DY0, DY1 = 210, 290, 520, 1330      # door
SHELF_Y = 980
PIE = (565, SHELF_Y - 26, 120, 26)             # cx, cy, half width, half height

def state(t):
    s = {}
    # beat 1: the space under the floor opens up, the tube lights up red (before 2 s)
    s['reveal'] = sst(t, 0.3, 0.6)
    s['tube_hot'] = sst(t, 0.5, 0.5)
    # beat 2: ghost of an old bare coil ABOVE the floor, then it slides down under the floor
    s['ghost'] = win(t, B(1) + 0.3, B(2) + 0.1, 0.35)
    s['ghost_drop'] = sst(t, B(1) + 2.4, 1.6)
    # glow of the floor: beats 6-8 (and the recap)
    fl = sst(t, B(5) + 0.4, 2.0)
    fl *= 1 - sst(t, B(8) + 0.2, 0.8)
    fl = max(fl, 0.75 * sst(t, B(11) + 1.2, 0.8))
    s['floor_glow'] = fl
    s['air'] = win(t, B(6) + 0.2, B(7) + 0.3, 0.4)
    # beat 9: spill + wipe
    s['drop'] = clamp((t - B(8) - 0.4) / 1.0)            # 0..1 falling
    s['splat'] = sst(t, B(8) + 1.4, 0.2) * (1 - sst(t, B(9), 0.2))
    s['wipe'] = clamp((t - B(8) - 2.8) / 1.8)            # cloth sweeps left -> right
    # beat 10-11: the element breaks and goes cold; floor stays clean
    s['broken'] = sst(t, B(9) + 1.0, 0.2) * (1 - sst(t, B(11) + 0.6, 0.3))
    # grill element: on only for the symptom (top heat only)
    s['grill'] = win(t, B(10) + 0.2, B(11) + 0.4, 0.4)
    s['pie'] = win(t, B(10) + 0.1, B(11) + 0.5, 0.35)
    # tube temperature: hot from beat 1, cold once broken
    hot = s['tube_hot'] * (1 - s['broken'])
    if B(1) <= t < B(2): hot *= 0.5
    s['tube'] = hot
    # zoom on the floor for beats 3 and 5
    s['z'] = max(win(t, B(2) + 0.05, B(3) + 0.3, 0.6), win(t, B(4) + 0.05, B(5) + 0.3, 0.6))
    return s

def CAM(t):
    """Camera (engine clips the stage to y < 1500): beats 3 and 5 zoom on the floor + tube."""
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

def tube_path(ctx, x0=TUBE_X0, x1=TUBE_X1, y=TUBE_Y):
    """Element seen from the side: front bend (left), straight run, back bend going DOWN then RIGHT
    through the back wall (terminals at the rear)."""
    ctx.move_to(x1 + 70, y + 14)            # terminal outside the back wall
    ctx.line_to(x1 + 10, y + 14)
    ctx.curve_to(x1 - 10, y + 14, x1 - 10, y, x1 - 26, y)
    ctx.line_to(x0 + 12, y)
    ctx.curve_to(x0 - 4, y, x0 - 4, y - 0.01, x0, y)

def element(ctx, t, s):
    hot = s['tube']
    col = lerpc(STEEL_D, HOT, hot)
    # tube body
    tube_path(ctx); setc(ctx, INK); ctx.set_line_width(2 * TUBE_R + 6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    tube_path(ctx); setc(ctx, col); ctx.set_line_width(2 * TUBE_R); ctx.stroke()
    # terminals + wires at the back (right)
    for dy in (8, 20):
        ctx.move_to(TUBE_X1 + 70, TUBE_Y + dy); ctx.line_to(BX1 - 10, TUBE_Y + dy + 30)
        setc(ctx, COPPER); ctx.set_line_width(3); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    # break (beats 10-11): a gap with a spark, the rest goes cold
    b = s['broken']
    if b > 0:
        gx = 560
        ctx.rectangle(gx - 9, TUBE_Y - TUBE_R - 4, 18, 2 * TUBE_R + 8); setc(ctx, CAV, b); ctx.fill()
        for sg in (-1, 1):
            ctx.move_to(gx + sg * 9, TUBE_Y - TUBE_R - 3); ctx.line_to(gx + sg * 4, TUBE_Y - 2)
            ctx.line_to(gx + sg * 11, TUBE_Y + 3); ctx.line_to(gx + sg * 6, TUBE_Y + TUBE_R + 3)
        setc(ctx, INK, b); ctx.set_line_width(3); ctx.stroke()
        sp = win(t, B(9) + 1.0, B(9) + 1.7, 0.15)
        if sp > 0:
            for k in range(8):
                an = k * math.pi / 4
                ctx.move_to(gx + 12 * math.cos(an), TUBE_Y + 12 * math.sin(an))
                ctx.line_to(gx + 30 * math.cos(an), TUBE_Y + 30 * math.sin(an))
            setc(ctx, MUSTARD, sp); ctx.set_line_width(4); ctx.stroke()

def oven(ctx, t, s):
    rrect(ctx, BX0, BY0, BX1 - BX0, BY1 - BY0, 14); fill_stroke(ctx, FILL2, lw=6)
    # control panel band (front = left, top)
    rrect(ctx, BX0 - 16, BY0 + 4, 26, 110, 6); fill_stroke(ctx, FILL3, lw=3)
    # insulation: top, back, bottom
    hatch(ctx, CX0, CY0 - INS, CX1 + INS - CX0, INS)
    hatch(ctx, CX1, CY0, INS, IB0 + INS - CY0)
    hatch(ctx, CX0, IB0, CX1 - CX0, INS)
    # under-floor space (dark), where the element lives
    ctx.rectangle(CX0, CY1, CX1 - CX0, IB0 - CY1); setc(ctx, CAV); ctx.fill()
    # cavity, warmed by the floor
    fg = s['floor_glow']
    ctx.rectangle(CX0, CY0, CX1 - CX0, CY1 - CY0); fill_stroke(ctx, lerpc(CAV, CAV_WARM, 0.8 * fg), lw=4)
    if fg > 0.05:
        g = cairo.LinearGradient(0, CY1, 0, CY1 - 380)
        g.add_color_stop_rgba(0, 1.0, 0.5, 0.18, 0.35 * fg); g.add_color_stop_rgba(1, 1.0, 0.5, 0.18, 0.0)
        ctx.rectangle(CX0, CY1 - 380, CX1 - CX0, 380); ctx.set_source(g); ctx.fill()
    # shelf supports + wire shelf
    for yy in (SHELF_Y, 800):
        ctx.move_to(CX1 - 4, yy); ctx.line_to(CX1 - 24, yy); setc(ctx, STEEL); ctx.set_line_width(6); ctx.stroke()
    pa = s['pie']
    if pa > 0:
        ctx.move_to(CX0 + 30, SHELF_Y); ctx.line_to(CX1 - 10, SHELF_Y); setc(ctx, STEEL, pa); ctx.set_line_width(5); ctx.stroke()
    # grill element (zigzag under the ceiling)
    gcol = lerpc(STEEL_D, HOT, s['grill'])
    ctx.move_to(CX0 + 50, 650)
    for i in range(12):
        ctx.line_to(CX0 + 50 + (i + 0.5) * 36, 672 if i % 2 == 0 else 650)
    ctx.line_to(CX1 - 40, 650)
    setc(ctx, gcol); ctx.set_line_width(9); ctx.stroke()
    # hidden element
    element(ctx, t, s)
    # cover over the under-floor space at the very start (removed by the reveal)
    rv = 1 - s['reveal']
    if rv > 0:
        ctx.rectangle(CX0, CY1 + FL_T, CX1 - CX0, IB0 - CY1 - FL_T); setc(ctx, FILL3, rv); ctx.fill()
    # the floor: enamelled steel sheet (glossy line on its top face)
    ctx.rectangle(CX0, CY1, CX1 - CX0, FL_T); fill_stroke(ctx, lerpc(ENAMEL, GLOW, 0.85 * fg), lw=3)
    ctx.move_to(CX0 + 20, CY1 + 3); ctx.line_to(CX1 - 60, CY1 + 3); setc(ctx, ENAMEL_HI, 0.8 * (1 - fg)); ctx.set_line_width(2); ctx.stroke()
    # door (left)
    rrect(ctx, DX0, DY0, DX1 - DX0, DY1 - DY0, 10); fill_stroke(ctx, FILL3, lw=5)
    for x in (228, 250, 272):
        ctx.rectangle(x - 4, 600, 8, 660); fill_stroke(ctx, GLASS, lw=2)
    ctx.move_to(DX0, 560); ctx.line_to(170, 560); ctx.line_to(170, 640); ctx.line_to(DX0, 640)
    setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()

def ghost_coil(ctx, t, s):
    """Old style: a bare coil lying ON the floor; slides down UNDER it."""
    a = s['ghost']
    if a <= 0: return
    y = lerp(CY1 - 22, TUBE_Y, s['ghost_drop'])
    ctx.save(); ctx.set_dash([10, 7])
    tube_path(ctx, y=y); setc(ctx, RED, a); ctx.set_line_width(2 * TUBE_R + 4); ctx.stroke()
    ctx.restore()
    tube_path(ctx, y=y); setc(ctx, CREAM, 0.5 * a); ctx.set_line_width(2 * TUBE_R - 6); ctx.stroke()
    if s['ghost_drop'] < 0.3:
        straight_arrow(ctx, 565, CY1 - 80, 565, CY1 + 26, RED, a * (1 - s['ghost_drop'] / 0.3) * sst(t, B(1) + 1.6, 0.4), lw=6, head=14)

def heat_up(ctx, t, s):
    """Tube -> floor (short arrows) then floor -> food zone (long arrows), all pointing UP (decreasing y)."""
    a = s['floor_glow']
    tube_a = s['tube'] * win(t, B(4) + 0.6, B(6), 0.4)
    for i in range(5):
        x = CX0 + 70 + i * 100
        if tube_a > 0:
            straight_arrow(ctx, x, TUBE_Y - 14, x, CY1 + FL_T + 2, ORANGE, tube_a, lw=4, head=7)
        if a > 0.1:
            wavy_arrow(ctx, x + 20, CY1 - 14, x + 20, CY1 - 150, t, ORANGE, 0.85 * a * (1 - s['air']), amp=5, wl=24, lw=4, head=10)

LOOP_L = [(565, 1200), (565, 760), (330, 720), (325, 1180), (540, 1205)]
LOOP_R = [(565, 1200), (565, 760), (800, 720), (805, 1180), (590, 1205)]
def _poly(pts, u):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(seg) * (u % 1)
    for i, d in enumerate(seg):
        if L <= d or i == len(seg) - 1:
            k = clamp(L / d); p, q = pts[i], pts[i + 1]
            return lerp(p[0], q[0], k), lerp(p[1], q[1], k), math.atan2(q[1] - p[1], q[0] - p[0])
        L -= d

def air_loop(ctx, t, s):
    """Warm air rises in the middle (upward = decreasing y), spreads under the ceiling,
    sinks along the door (left) and the back wall (right), returns over the floor."""
    a = s['air']
    if a <= 0: return
    for pts, ph in ((LOOP_L, 0.0), (LOOP_R, 0.5)):
        ctx.new_path()
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        ctx.set_dash([6, 12]); setc(ctx, TEAL_L, 0.6 * a); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
        for k in range(5):
            x, y, an = _poly(pts, t * 0.18 + k / 5 + ph / 5)
            warm = clamp(1 - (y - 720) / 480) if False else 0
            col = lerpc(TEAL, ORANGE, 0.0)
            ctx.save(); ctx.translate(x, y); ctx.rotate(an)
            ctx.move_to(12, 0); ctx.line_to(-8, -9); ctx.line_to(-8, 9); ctx.close_path()
            setc(ctx, ORANGE if pts is LOOP_L and k % 2 == 0 or pts is LOOP_R and k % 2 == 1 else TEAL, a); ctx.fill()
            ctx.restore()

def spill(ctx, t, s):
    """Beat 9: a drop falls on the enamel, splats, a cloth wipes it away (left to right)."""
    if not (B(8) <= t < B(9) + 0.3): return
    d = s['drop']
    x0 = 600
    if 0 < d < 1:
        y = lerp(SHELF_Y - 120, CY1 - 10, d * d)
        ctx.save(); ctx.translate(x0, y); ctx.scale(10, 14); ctx.arc(0, 0, 1, 0, 6.28); ctx.restore()
        setc(ctx, SAUCE); ctx.fill()
    sp = s['splat']
    w = s['wipe']
    if sp > 0:
        ctx.save(); ctx.rectangle(lerp(CX0, CX1, w) if w > 0 else CX0, CY1 - 20, CX1 - CX0, 30); ctx.clip()
        ctx.save(); ctx.translate(x0, CY1 - 4); ctx.scale(80, 12); ctx.arc(0, 0, 1, math.pi, 2 * math.pi); ctx.restore()
        setc(ctx, SAUCE, sp); ctx.fill()
        ctx.restore()
    if 0 < w < 1:
        cx = lerp(CX0 + 40, CX1 - 40, w)
        rrect(ctx, cx - 60, CY1 - 46, 120, 44, 12); fill_stroke(ctx, TEAL_L, lw=4)

def pie(ctx, t, s):
    a = s['pie']
    if a <= 0: return
    cx, cy, hw, hh = PIE
    k = sst(t, B(10) + 1.4, 1.2)   # top browns over the beat
    # dish
    ctx.move_to(cx - hw - 12, cy - hh); ctx.line_to(cx - hw + 6, cy + hh); ctx.line_to(cx + hw - 6, cy + hh); ctx.line_to(cx + hw + 12, cy - hh)
    setc(ctx, STEEL_D, a); ctx.set_line_width(5); ctx.stroke()
    # bottom crust (pale), filling, top crust (golden)
    ctx.rectangle(cx - hw + 6, cy + hh - 14, 2 * hw - 12, 14); setc(ctx, PALE, a); ctx.fill()
    ctx.rectangle(cx - hw + 2, cy - hh + 12, 2 * hw - 4, 2 * hh - 26); setc(ctx, FILLING, a); ctx.fill()
    ctx.move_to(cx - hw - 8, cy - hh + 12); ctx.curve_to(cx - 40, cy - hh - 18, cx + 40, cy - hh - 18, cx + hw + 8, cy - hh + 12)
    ctx.close_path(); setc(ctx, lerpc(PALE, CRUST, k), a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    # heat only from the top (grill), pointing DOWN onto the pie
    g = s['grill']
    for i in range(4):
        x = cx - 90 + i * 60
        wavy_arrow(ctx, x, 690, x, cy - hh - 26, t, RED, 0.85 * g, amp=5, wl=22, lw=4, head=10)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    ctx.save()
    cx, cy, z = CAM(t)
    if z > 1.001:   # zoomed: keep the stage below the title zone (screen y >= 420)
        ytop = (420 - 900) / z + cy
        ctx.rectangle(-2000, ytop, 5000, 5000); ctx.clip()
    oven(ctx, t, s)
    ghost_coil(ctx, t, s)
    heat_up(ctx, t, s)
    air_loop(ctx, t, s)
    spill(ctx, t, s)
    pie(ctx, t, s)
    ctx.restore()

# ---------------------------------------------------------------- labels (screen space)
def labels(ctx, t, s):
    # beat 1: hidden heater revealed
    a = win(t, 0.6, B(1) + 0.1, 0.25)
    tag(ctx, "HIDDEN HEATER", 565, 1430, RED, a * sst(t, 0.6), 30)
    highlight(ctx, 565, TUBE_Y, 300, 34, RED, a * sst(t, 0.6), t)
    # beat 2
    a = bw(t, 1)
    if a > 0:
        tag(ctx, "OLD: BARE COIL", 420, 1100, RED, a * sst(t, B(1) + 0.4) * (1 - sst(t, B(1) + 2.4, 0.4)), 26)
        tag(ctx, "NEW: UNDER THE FLOOR", 565, 1430, RED, a * sst(t, B(1) + 3.2), 28)
    # beat 3 (zoomed on the floor: screen coords)
    a = bw(t, 2)
    if a > 0:
        tag(ctx, "1 · HEATING ELEMENT", 540, 1430, RED, a * sst(t, B(2) + 0.4), 30)
    # beat 5 (zoomed)
    a = bw(t, 4)
    if a > 0:
        tag(ctx, "2 · ENAMELLED STEEL FLOOR", 540, 980, TEAL, a * sst(t, B(4) + 0.3), 28)
        tag(ctx, "ELEMENT UNDERNEATH", 540, 1430, RED, a * sst(t, B(4) + 1.4), 26)
    # beat 6
    a = bw(t, 5)
    if a > 0:
        highlight(ctx, 565, CY1 + 6, 280, 30, ORANGE, a, t)
        tag(ctx, "3 · HOT FLOOR GLOWS UP", 565, 1430, ORANGE, a, 28)
    # beat 7
    a = bw(t, 6)
    if a > 0:
        tag(ctx, "WARM AIR RISES", 565, 1430, TEAL, a, 28)
    # beat 9
    a = bw(t, 8)
    if a > 0:
        tag(ctx, "SMOOTH ENAMEL", 565, 1430, TEAL, a * sst(t, B(8) + 1.4), 28)
        tag(ctx, "ONE WIPE", 565, 1140, INK, a * sst(t, B(8) + 3.0), 26)
    # beat 10
    a = bw(t, 9)
    if a > 0:
        tag(ctx, "BROKEN, OUT OF SIGHT", 560, 1430, RED, a * sst(t, B(9) + 1.0), 28)
        tag(ctx, "FLOOR STILL SPOTLESS", 565, 1150, TEAL, a * sst(t, B(9) + 2.2), 26)
    # beat 11
    a = bw(t, 10)
    if a > 0:
        tag(ctx, "GOLDEN TOP", 565, 870, ORANGE, a * sst(t, B(10) + 1.6), 26)
        tag(ctx, "PALE BOTTOM", 565, 1070, INK, a * sst(t, B(10) + 2.6), 26)
        tag(ctx, "NO HEAT FROM BELOW", 560, 1430, RED, a * sst(t, B(10) + 2.6), 26)
    # beat 12
    a = win(t, B(11) + 0.6, B(12) + 2.0, 0.3)
    if a > 0:
        tag(ctx, "FLOOR = HEATER'S LID", 560, 1430, RED, a, 30)

# ---------------------------------------------------------------- HUD (top zone, y 175-375)
def _panel(ctx, a, x=60, y=180, w=960, h=195):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def _mini(ctx, x, y, w, under, a, hot=1.0):
    """Mini floor icon: enamel sheet with a coil above (old) or below (new)."""
    yy = y + (16 if under else -16)
    ctx.move_to(x, yy); ctx.line_to(x + w, yy)
    setc(ctx, INK, a); ctx.set_line_width(18); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.move_to(x, yy); ctx.line_to(x + w, yy)
    setc(ctx, lerpc(STEEL_D, HOT, hot), a); ctx.set_line_width(12); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.rectangle(x - 20, y - 6, w + 40, 12); fill_stroke(ctx, ENAMEL, lw=3, alpha=a)

def hud_secret(ctx, t, a):
    _panel(ctx, a)
    k = sst(t, B(1) + 2.6, 0.4)
    text_c(ctx, "OLD OVENS", 290, 245, 32, INK, True, 3, a)
    _mini(ctx, 180, 300, 220, False, a)
    text_c(ctx, "NEW OVENS", 790, 245, 32, RED, True, 3, a * k)
    _mini(ctx, 680, 300, 220, True, a * k)
    straight_arrow(ctx, 480, 300, 600, 300, INK, a * k, lw=6, head=14)

def hud_stone(ctx, t, a):
    _panel(ctx, a)
    text_c(ctx, "LIKE A BAKING STONE", 540, 250, 40, ORANGE, True, 3, a)
    rrect(ctx, 330, 300, 420, 34, 8); fill_stroke(ctx, lerpc(FILL3, GLOW, 0.8), lw=4, alpha=a)
    for i in range(5):
        x = 370 + i * 85
        wavy_arrow(ctx, x, 296, x, 268 - 0, t, ORANGE, a * 0.0, amp=3, wl=14, lw=3, head=7)
    text_c(ctx, "HEATS UP · GIVES HEAT BACK", 540, 360, 22, INK2, True, 2, a)

def hud_recap(ctx, t, a):
    _panel(ctx, a)
    k1, k2, k3 = (sst(t, B(11) + d, 0.25) for d in (0.3, 1.0, 1.7))
    text_c(ctx, "FLOOR", 230, 255, 34, TEAL, True, 3, a * k1)
    ctx.rectangle(120, 290, 220, 14); fill_stroke(ctx, ENAMEL, lw=3, alpha=a * k1)
    text_c(ctx, "=", 450, 310, 70, INK, True, 0, a * k2)
    text_c(ctx, "HEATER'S LID", 770, 255, 34, RED, True, 3, a * k3)
    ctx.rectangle(640, 290, 260, 14); fill_stroke(ctx, lerpc(ENAMEL, GLOW, 0.7), lw=3, alpha=a * k3)
    ctx.move_to(660, 326); ctx.line_to(880, 326)
    setc(ctx, HOT, a * k3); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def draw_hud(ctx, t, E):
    s = state(t)
    labels(ctx, t, s)
    a = win(t, B(1) + 0.2, B(2) + 0.05, 0.3)
    if a > 0: hud_secret(ctx, t, a)
    a = win(t, B(5) + 1.6, B(6) + 0.05, 0.3)
    if a > 0: hud_stone(ctx, t, a)
    a = win(t, B(11) + 0.2, B(12) + 2.0, 0.3)
    if a > 0: hud_recap(ctx, t, a)

SFX = [(0.6, 'pop'), (B(1) + 0.4, 'pop'), (B(1) + 3.2, 'pop'), (B(2) + 0.4, 'pop'),
       (B(4) + 0.3, 'pop'), (B(4) + 1.4, 'pop'), (B(5) + 0.2, 'pop'), (B(5) + 1.6, 'pop'), (B(6) + 0.2, 'pop'),
       (B(8) + 1.4, 'pop'), (B(8) + 3.0, 'pop'), (B(9) + 1.0, 'click'), (B(9) + 2.2, 'pop'),
       (B(10) + 1.6, 'pop'), (B(10) + 2.6, 'pop'), (B(11) + 0.3, 'pop'), (B(11) + 1.7, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards (draw inside x 110..970, y 250..540)
def card_tube(ctx, t, lt, a):
    card_frame(ctx, "INSIDE THE TUBE", a, "HEAT GETS OUT · CURRENT STAYS IN", RED)
    x0, x1, yc, h = 200, 880, 400, 120
    # steel sheath (cut lengthwise)
    rrect(ctx, x0, yc - h / 2, x1 - x0, h, 20); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    ctx.rectangle(x0 + 14, yc - h / 2 + 14, x1 - x0 - 28, h - 28); setc(ctx, POWDER, a); ctx.fill()
    rnd = random.Random(4)
    for i in range(160):
        ctx.arc(x0 + 20 + rnd.random() * (x1 - x0 - 40), yc - h / 2 + 18 + rnd.random() * (h - 36), 2, 0, 6.28)
        setc(ctx, INK2, 0.35 * a); ctx.fill()
    # coiled resistance wire along the axis
    hot = sst(lt, 0.6, 1.2)
    ctx.move_to(x0 + 30, yc)
    n = 40
    for i in range(n + 1):
        x = lerp(x0 + 30, x1 - 30, i / n)
        ctx.line_to(x, yc + 20 * math.sin(i * math.pi / 2))
    setc(ctx, lerpc(COPPER, HOT, hot), a); ctx.set_line_width(5); ctx.stroke()
    # current: yellow dots moving ALONG the wire (they never leave it)
    for k in range(10):
        u = (lt * 0.25 + k / 10) % 1
        x = lerp(x0 + 30, x1 - 30, u)
        i = u * n
        ctx.arc(x, yc + 20 * math.sin(i * math.pi / 2), 6, 0, 6.28); setc(ctx, MUSTARD, a); ctx.fill_preserve()
        setc(ctx, INK, a); ctx.set_line_width(2); ctx.stroke()
    # heat: wavy arrows going OUT through the powder and the sheath (up and down)
    ha = a * sst(lt, 1.6, 0.6)
    for i in range(5):
        x = x0 + 90 + i * 125
        wavy_arrow(ctx, x, yc - 30, x, yc - h / 2 - 50, t, ORANGE, ha, amp=4, wl=18, lw=4, head=9)
        wavy_arrow(ctx, x + 40, yc + 30, x + 40, yc + h / 2 + 48, t, ORANGE, ha, amp=4, wl=18, lw=4, head=9)
    tag(ctx, "POWDER", 300, yc + h / 2 + 2, INK2, a * sst(lt, 2.4), 20)
    tag(ctx, "HOT WIRE", 540, yc - h / 2 - 2, RED, a * sst(lt, 1.0), 20)

def card_buffer(ctx, t, lt, a):
    card_frame(ctx, "THE STEEL BUFFER", a, "SLOWER PREHEAT · EVENER HEAT", TEAL)
    # left: bare coil -> spiky temperature profile; right: under steel -> flat profile
    for side, (cx, under, title, col) in enumerate(((320, False, "BARE COIL", RED), (760, True, "UNDER STEEL", TEAL))):
        text_c(ctx, title, cx, 290, 28, col, True, 2, a)
        base = 480
        # surface
        ctx.rectangle(cx - 170, base, 340, 12); fill_stroke(ctx, ENAMEL if under else FILL3, lw=3, alpha=a)
        for j in range(4):
            x = cx - 135 + j * 90
            yy = base + 30 if under else base - 14
            ctx.arc(x, yy, 10, 0, 6.28); fill_stroke(ctx, HOT, lw=3, alpha=a)
        # temperature curve above the surface
        k = sst(lt, 0.8, 1.6)
        ctx.new_path()
        for i in range(61):
            x = cx - 170 + i * 340 / 60
            if under:
                y = 400 - 40 * k
            else:
                d = min(abs(x - (cx - 135 + j * 90)) for j in range(4))
                y = 420 - k * 70 * math.exp(-(d / 18) ** 2)
            (ctx.line_to if i else ctx.move_to)(x, y)
        setc(ctx, col, a); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "HOT SPOTS", 320, 326, 20, RED, True, 1, a * sst(lt, 2.0))
    text_c(ctx, "EVEN", 760, 326, 20, TEAL, True, 1, a * sst(lt, 2.0))

CARDS = {'tube': card_tube, 'buffer': card_buffer}
