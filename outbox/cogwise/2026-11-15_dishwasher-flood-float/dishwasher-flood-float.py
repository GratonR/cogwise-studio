"""Cogwise episode: Your dishwasher has a tiny boat under it.
One idea: the anti-flood FLOAT. A foam float sits in the lowest corner of the base tray; any leak runs down into
the tray, lifts the float, the float pushes a microswitch, and the control board goes into emergency mode:
inlet valve shut, drain pump nonstop. The pump empties the TUB (sump), never the TRAY, so the float stays up
(alarm latched on many models) until the tray dries.

VIEW (screen coordinates, y grows DOWN): FRONT cut-away of the dishwasher.
  - control panel strip on top (y 360-420) with the control board display.
  - tub y 430-1150 (cut open), sump at the bottom centre (x 540) -> pipe down to the DRAIN PUMP (x 540, y 1285).
    Drain hose leaves the pump to the RIGHT and exits through the right wall (y 1285).
  - inlet: hose comes in from OUTSIDE on the RIGHT (y 1345) into the INLET VALVE (x 800), then up the right side
    into the tub (enters at y 1080). Water flows right -> left into the valve, then UP into the tub.
  - base tray: floor slopes DOWN toward the LEFT corner: floor y = 1430 at x 200, 1405 at x 880
    (larger y = lower). Leaks fall straight down, then run LEFT along the floor to the low corner.
  - float (foam block) in the LEFT corner, in a guide cage, rod pointing UP to the microswitch lever (y ~1300).
    Puddle depth lifts the float UP (y decreases); the rod then pushes the lever UP into the switch.
  - wire from the switch runs up the left side to the control board.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="dishwasher-flood-float",
    title="Your dishwasher has a tiny boat under it ⛵ #Shorts",
    description=("A floating piece of foam is quietly guarding your kitchen floor.\n\n"
                 "#Shorts #howthingswork #dishwasher #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "dishwasher", "appliances", "cogwise"],
    sources=[
        "https://wiki.bsh-group.com/de/wiki/AquaStop_–_der_sichere_Schutz_vor_Wasserschäden/en",
        "https://www.servicemag.org/guides/bosch-dishwasher-e15-error",
        "https://www.ifixit.com/WIKI/Bosch_Dishwasher_E15_Code",
        "https://www.mieleusa.com/e/waterproof-system-wps-zpv000000000000000020000144600-f",
    ],
)

BEATS = [
    dict(dur=5.6, title="A TINY BOAT", caption="There's a tiny boat hiding under your dishwasher. Its only job is to float."),
    dict(dur=5.6, title="THE SECRET", caption="It's a flood alarm, and when it floats, your dishwasher goes into emergency mode."),
    dict(dur=4.9, title="1 · THE TRAY", caption="Under the tub sits a plastic tray, sloped down toward one corner."),
    dict(dur=6.3, title="LEAKS", caption="Any leak, from a hose, a door seal or a cracked pump, runs down into it."),
    dict(dur=5.6, title="2 · THE FLOAT", caption="In that low corner sits a little foam float, right under a tiny switch."),
    dict(dur=5.2, title=None, caption="Foam is much lighter than water, so even a shallow puddle lifts it.", card='buoy'),
    dict(dur=6.0, title="3 · THE SWITCH", caption="As it rises, it presses the switch, and the control board knows there's a leak."),
    dict(dur=5.6, title="WATER OFF", caption="First, the board shuts the inlet valve, so not one more drop comes in."),
    dict(dur=4.5, title="PUMP ON", caption="Then it runs the drain pump nonstop to empty the tub."),
    dict(dur=6.0, title=None, caption="But that pump drains the tub, not the tray, so the little boat stays afloat.", card='tubtray'),
    dict(dur=6.0, title="STUCK", caption="On many models, the alarm won't clear until the tray dries out."),
    dict(dur=4.9, title="FOAM = GUARD", caption="So a floating piece of foam is quietly guarding your kitchen floor."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

WATER = hexc('#5aa9e6'); WATER_D = hexc('#2f6fb3')
FOAM = hexc('#f6f0dc'); FOAM_D = hexc('#d9cfae')
STEEL = hexc('#b9c0c6'); STEEL_D = hexc('#7d858c')
TRAY_C = hexc('#d6cdbd'); COPPER = hexc('#c46d2e')
BOARD_G = hexc('#3f7a4f')

# ---------------------------------------------------------------- geometry
CX0, CX1, CY0, CY1 = 170, 910, 360, 1460          # cabinet
PANEL = (CX0, CY0, CX1 - CX0, 62)
TX0, TX1, TY0, TY1 = 215, 865, 420, 960          # tub
SUMP_X = 540
FL_X0, FL_X1, FL_Y0, FL_Y1 = 200, 880, 1440, 1380  # tray floor (left end is LOWER)
def floor_y(x): return FL_Y0 + (x - FL_X0) * (FL_Y1 - FL_Y0) / (FL_X1 - FL_X0)
PUMP = (SUMP_X, 1110, 58)
VALVE = (790, 1250)
FLX, FW, FH = 300, 120, 62                          # float centre x, width, height
SW = (240, 1222, 150, 54)                         # microswitch body (x, y, w, h)
LEVER_Y = 1300                                    # lever rest height (bottom of switch)
BOARD = (590, 372, 230, 40)

def state(t):
    s = {}
    # puddle depth at the low corner (px). Teaser in beats 1-2, dry at beat 3, leaks fill from beat 4,
    # stays during 5-10, dries slowly in beat 11.
    teaser = (20 * sstep(t, 0.3, 1.0) + 30 * sstep(t, B(1) + 0.1, 0.5)) * (1 - sstep(t, B(2) - 0.2, 0.6))
    fill = 50 * sstep(t, B(3) + 2.0, 3.5)
    dry = 1 - sstep(t, B(10) + 1.0, 4.2)
    s['depth'] = max(teaser, fill * dry)
    # float lift: draft 10 px, max lift 24 px (then the rod is pushing the lever)
    s['lift'] = clamp(s['depth'] - 14, 0, 30)
    # in beat 5 the float is shown sitting (puddle still shallow) -> lift comes in beat 7
    if B(4) <= t < B(6):
        s['lift'] = min(s['lift'], 3)
        s['depth'] = min(s['depth'], 17)
    if B(6) <= t < B(7):
        k = sstep(t, B(6) + 0.3, 1.2)
        s['depth'] = lerp(17, s['depth'], k); s['lift'] = clamp(s['depth'] - 14, 0, 30)
    s['bob'] = 2.5 * math.sin(t * 3.1) * (1 if s['lift'] > 3 else 0)
    s['pressed'] = 1.0 if s['lift'] > 26 else 0.0
    # alarm (red) after the switch closes
    s['alarm'] = max(win(t, B(1) + 0.5, B(2) - 0.1, 0.2) if t < B(2) else 0, sstep(t, B(6) + 1.8, 0.2) * (1 - sstep(t, B(11) + 0.2, 0.6)))
    # inlet valve: open (water flowing in) until beat 8 shuts it (and closed in the teaser after the alarm)
    shut_teaser = sstep(t, B(1) + 0.9, 0.2) * (1 - sstep(t, B(2), 0.3))
    s['valve_open'] = 1 - max(shut_teaser, sstep(t, B(7) + 1.4, 0.4))
    if t >= B(11) + 0.5: s['valve_open'] = 0
    # tub water level (px of water at the bottom of the tub): full until beat 9 drains it
    s['tub'] = 46 * (1 - sstep(t, B(8) + 0.6, 3.0))
    s['pump_on'] = max(win(t, B(1) + 1.2, B(2) - 0.1, 0.2) if t < B(2) else 0, sstep(t, B(8) + 0.3, 0.3) * (1 - sstep(t, B(10) - 0.2, 0.4)))
    s['err'] = sstep(t, B(10) + 0.4, 0.3) * (1 - sstep(t, B(11) - 1.2, 0.5))
    return s

# camera: (time, focus x, focus y, zoom)
CAMKEYS = [(0, 540, 930, 1.0), (B(2) + 0.1, 540, 1230, 1.4), (B(4) + 0.1, 330, 1300, 2.1),
       (B(7) + 0.1, 540, 930, 1.0), (B(10) + 0.1, 330, 1250, 1.6), (B(11) + 0.1, 540, 930, 1.0)]

# ---------------------------------------------------------------- drawing pieces
def puddle(ctx, depth, a=1.0):
    if depth <= 0.5: return
    surf = FL_Y0 - depth
    # floor rises to the right: water reaches x where floor_y(x) == surf
    xe = FL_X0 + (FL_Y0 - surf) * (FL_X1 - FL_X0) / (FL_Y0 - FL_Y1)
    xe = min(xe, FL_X1)
    ctx.move_to(FL_X0 + 6, surf); ctx.line_to(xe, surf); ctx.line_to(xe, floor_y(xe))
    ctx.line_to(FL_X0 + 6, FL_Y0); ctx.close_path()
    setc(ctx, WATER, 0.75 * a); ctx.fill_preserve(); setc(ctx, WATER_D, a); ctx.set_line_width(2.5); ctx.stroke()

def float_and_switch(ctx, t, s, a=1.0, flash=0.0):
    lift = s['lift'] + s['bob'] * 0.4
    fy1 = floor_y(FLX) - lift          # bottom of float
    fy0 = fy1 - FH
    # guide cage (two posts)
    for x in (FLX - FW / 2 - 10, FLX + FW / 2 + 4):
        ctx.rectangle(x, 1318, 6, floor_y(x) - 1318); fill_stroke(ctx, FILL3, lw=2, alpha=a)
    # float body: foam block, slightly rounded like a hull
    ctx.new_path()
    ctx.move_to(FLX - FW / 2, fy0); ctx.line_to(FLX + FW / 2, fy0)
    ctx.line_to(FLX + FW / 2 - 8, fy1); ctx.line_to(FLX - FW / 2 + 8, fy1); ctx.close_path()
    fill_stroke(ctx, lerpc(FOAM, hexc('#ff8a70'), flash), lw=4, alpha=a)
    rnd = random.Random(7)
    for i in range(9):
        ctx.arc(FLX + rnd.uniform(-45, 45), fy0 + rnd.uniform(10, FH - 10), 3.5, 0, 6.28); setc(ctx, FOAM_D, a); ctx.fill()
    # rod up from the float to the lever
    rod_top = fy0 - (floor_y(FLX) - FH - LEVER_Y - 14)   # 14 px gap at rest
    ctx.rectangle(FLX - 7, rod_top, 14, fy0 - rod_top); fill_stroke(ctx, STEEL_D, lw=2, alpha=a)
    # lever: hinged on the left of the switch body, pushed UP by the rod
    lv_y = min(LEVER_Y, rod_top)
    sx, sy, sw, sh = SW
    ctx.move_to(sx + 6, LEVER_Y - 2); ctx.line_to(FLX + 30, lv_y); setc(ctx, INK2, a); ctx.set_line_width(7); ctx.stroke()
    rrect(ctx, sx, sy, sw, sh, 6); fill_stroke(ctx, lerpc(INK2, RED, s['pressed'] * (0.5 + 0.5 * s['alarm'])), lw=3, alpha=a)
    # small plunger under the switch
    ctx.rectangle(FLX - 8, sy + sh, 16, max(2, lv_y - sy - sh - 4)); setc(ctx, INK, a); ctx.fill()
    return fy0, fy1

def tub(ctx, t, s):
    # tub walls (steel), dish racks, water at the bottom, door seal (red-brown gasket) along the front edge
    rrect(ctx, TX0, TY0, TX1 - TX0, TY1 - TY0, 18); fill_stroke(ctx, hexc('#e9ecee'), lw=5)
    for ry in (640, 900):
        ctx.move_to(TX0 + 25, ry); ctx.line_to(TX1 - 25, ry); setc(ctx, STEEL_D); ctx.set_line_width(5); ctx.stroke()
        for i in range(10):
            x = TX0 + 60 + i * 58
            ctx.move_to(x, ry); ctx.line_to(x, ry - 70); ctx.set_line_width(3); setc(ctx, STEEL_D); ctx.stroke()
    # plates and cups (props)
    for i in range(5):
        x = TX0 + 110 + i * 100
        ctx.save(); ctx.translate(x, 830); ctx.scale(0.35, 1); ctx.arc(0, 0, 70, 0, 6.28); ctx.restore()
        fill_stroke(ctx, PAPER, lw=3)
    for i in range(4):
        x = TX0 + 140 + i * 130
        rrect(ctx, x - 30, 555, 60, 80, 10); fill_stroke(ctx, FILL2, lw=3)
    # water at the bottom of the tub
    h = s['tub']
    if h > 0.5:
        ctx.rectangle(TX0 + 6, TY1 - 6 - h, TX1 - TX0 - 12, h); setc(ctx, WATER, 0.7); ctx.fill()
    # sump
    rrect(ctx, SUMP_X - 50, TY1 - 10, 100, 45, 10); fill_stroke(ctx, STEEL, lw=4)
    # door seal (gasket) drawn as the front edge of the tub
    rrect(ctx, TX0 - 8, TY0 - 8, TX1 - TX0 + 16, TY1 - TY0 + 16, 24)
    setc(ctx, hexc('#8a4b3a'), 0.9); ctx.set_line_width(5); ctx.stroke()

def base(ctx, t, s):
    # tray: walls + sloped floor
    ctx.move_to(FL_X0, 1320); ctx.line_to(FL_X0, FL_Y0 + 8); ctx.line_to(FL_X1, FL_Y1 + 8); ctx.line_to(FL_X1, 1320)
    setc(ctx, TRAY_C); ctx.line_to(FL_X1 - 10, 1320); ctx.line_to(FL_X1 - 10, FL_Y1); ctx.line_to(FL_X0 + 10, FL_Y0)
    ctx.line_to(FL_X0 + 10, 1320); ctx.close_path(); fill_stroke(ctx, TRAY_C, lw=3)
    puddle(ctx, s['depth'])
    # pump: pipe from sump, round housing, impeller, motor on the left
    px, py, pr = PUMP
    ctx.rectangle(px - 14, TY1 + 35, 28, py - pr - TY1 - 35 + 4); fill_stroke(ctx, STEEL, lw=3)
    ctx.move_to(px + pr - 4, py); ctx.line_to(CX1 + 40, py); setc(ctx, INK); ctx.set_line_width(26); ctx.stroke()
    ctx.move_to(px + pr - 4, py); ctx.line_to(CX1 + 40, py); setc(ctx, FILL3); ctx.set_line_width(18); ctx.stroke()
    rrect(ctx, px - pr - 90, py - 26, 92, 52, 10); fill_stroke(ctx, FILL3, lw=3)
    ctx.arc(px, py, pr, 0, 6.28); fill_stroke(ctx, STEEL, lw=4)
    ang = t * 14 * s['pump_on']
    for k in range(4):
        an = ang + k * math.pi / 2
        ctx.move_to(px, py); ctx.line_to(px + (pr - 8) * math.cos(an), py + (pr - 8) * math.sin(an))
        setc(ctx, INK2); ctx.set_line_width(5); ctx.stroke()
    # drain flow (out to the right) while the pump runs and the tub has water
    fa = s['pump_on'] * clamp(s['tub'] / 10 + 0.15)
    if fa > 0.05:
        for i in range(6):
            u = (t * 1.3 + i / 6) % 1
            ctx.arc(lerp(px + pr + 4, CX1 + 30, u), py, 6, 0, 6.28); setc(ctx, WATER_D, fa); ctx.fill()
    # inlet hose from OUTSIDE (right) into the valve, then up the right side into the tub
    vx, vy = VALVE
    ctx.move_to(CX1 + 60, vy); ctx.line_to(vx, vy); setc(ctx, INK); ctx.set_line_width(24); ctx.stroke()
    ctx.move_to(CX1 + 60, vy); ctx.line_to(vx, vy); setc(ctx, hexc('#9c8f7a')); ctx.set_line_width(16); ctx.stroke()
    ctx.move_to(vx, vy - 30); ctx.line_to(vx, 880); ctx.line_to(TX1, 880); setc(ctx, INK); ctx.set_line_width(18); ctx.stroke()
    ctx.move_to(vx, vy - 30); ctx.line_to(vx, 880); ctx.line_to(TX1, 880); setc(ctx, FILL3); ctx.set_line_width(11); ctx.stroke()
    rrect(ctx, vx - 40, vy - 40, 80, 80, 10); fill_stroke(ctx, lerpc(FILL2, RED, 1 - s['valve_open']), lw=4)
    # coil on the valve
    ctx.arc(vx, vy, 20, 0, 6.28); fill_stroke(ctx, COPPER, lw=3)
    oa = s['valve_open']
    if oa > 0.05:
        for i in range(5):
            u = (t * 1.1 + i / 5) % 1
            ctx.arc(lerp(CX1 + 50, vx + 36, u), vy, 5, 0, 6.28); setc(ctx, WATER_D, oa); ctx.fill()
            u2 = (t * 0.9 + i / 5) % 1
            if u2 < 0.6:
                ctx.arc(vx, lerp(vy - 40, 885, u2 / 0.6), 4, 0, 6.28)
            else:
                ctx.arc(lerp(vx, TX1, (u2 - 0.6) / 0.4), 880, 4, 0, 6.28)
            setc(ctx, WATER_D, oa); ctx.fill()

def cabinet(ctx, t, s):
    rrect(ctx, CX0, CY0, CX1 - CX0, CY1 - CY0, 20); fill_stroke(ctx, PAPER, lw=6)
    x, y, w, h = PANEL
    rrect(ctx, x, y, w, h, 18); fill_stroke(ctx, FILL3, lw=4)
    bx, by, bw_, bh = BOARD
    rrect(ctx, bx, by, bw_, bh, 6); fill_stroke(ctx, lerpc(BOARD_G, RED, 0.85 * s['alarm']), lw=3)
    for i in range(5):
        ctx.rectangle(bx + 14 + i * 26, by + 12, 16, 16); setc(ctx, INK, 0.8); ctx.fill()
    # display
    rrect(ctx, 300, 372, 140, 40, 6); fill_stroke(ctx, INK, lw=2)
    if s['err'] > 0:
        text_c(ctx, "LEAK", 370, 404, 30, RED, True, 3, s['err'] * (0.65 + 0.35 * math.sin(t * 8) ** 2))
    # cut-away base zone (darker paper)
    ctx.rectangle(CX0 + 8, TY1 + 12, CX1 - CX0 - 16, CY1 - TY1 - 20); setc(ctx, WALL2); ctx.fill()
    # feet
    for x in (CX0 + 40, CX1 - 80):
        ctx.rectangle(x, CY1, 40, 30); fill_stroke(ctx, FILL3, lw=3)
    # wire from switch to the board (up the left side)
    sx, sy, sw, sh = SW
    ctx.move_to(sx + 6, sy + 10); ctx.line_to(190, sy + 10); ctx.line_to(190, 395); ctx.line_to(bx, 395)
    setc(ctx, COPPER); ctx.set_line_width(4); ctx.stroke()

def signal(ctx, t, a):
    """A red pulse travelling from the switch up the wire to the board."""
    if a <= 0: return
    sx, sy, _, _ = SW
    pts = [(sx + 6, sy + 10), (190, sy + 10), (190, 395), (BOARD[0], 395)]
    L = [math.dist(pts[i], pts[i + 1]) for i in range(3)]; tot = sum(L)
    for k in range(3):
        d = ((t * 700) + k * tot / 3) % tot
        for i in range(3):
            if d <= L[i]:
                u = d / L[i]; x = lerp(pts[i][0], pts[i + 1][0], u); y = lerp(pts[i][1], pts[i + 1][1], u); break
            d -= L[i]
        ctx.arc(x, y, 9, 0, 6.28); setc(ctx, RED, a); ctx.fill()

def leak_drops(ctx, t, a):
    """Beat 4: drops fall straight DOWN from 3 sources, then run LEFT (downhill) along the floor to the corner."""
    if a <= 0: return
    srcs = [(VALVE[0] - 34, VALVE[1] + 40, 0.0), (TX0 + 70, TY1 + 14, 0.33), (PUMP[0] - 10, PUMP[1] + PUMP[2], 0.66)]
    for (x, y, ph) in srcs:
        for k in range(2):
            u = ((t - B(3)) * 0.55 + ph + k * 0.5) % 1
            yf = floor_y(x) - 6
            fall = 0.4
            if u < fall:
                dx, dy = x, lerp(y, yf, (u / fall) ** 1.6)
            else:
                v = (u - fall) / (1 - fall)
                dx = lerp(x, FL_X0 + 40, v); dy = floor_y(dx) - 6
            ctx.move_to(dx, dy - 12); ctx.curve_to(dx + 7, dy - 2, dx + 7, dy + 6, dx, dy + 6)
            ctx.curve_to(dx - 7, dy + 6, dx - 7, dy - 2, dx, dy - 12)
            setc(ctx, WATER, a); ctx.fill_preserve(); setc(ctx, WATER_D, a); ctx.set_line_width(2); ctx.stroke()

def scene(ctx, t, s):
    cabinet(ctx, t, s)
    tub(ctx, t, s)
    base(ctx, t, s)
    flash = s['alarm'] * (0.5 + 0.5 * math.sin(t * 9)) if t < B(2) + 0.2 else 0
    float_and_switch(ctx, t, s, flash=flash)
    leak_drops(ctx, t, bw(t, 3, 5) * (1 - sstep(t, B(4) + 1.0, 0.5)))
    signal(ctx, t, win(t, B(6) + 1.6, B(7), 0.25))

def labels(ctx, t, s):
    """Tags drawn in world space (inside the camera transform) so they stay on their parts."""
    fy = floor_y(FLX)
    a = win(t, 0.5, B(1), 0.3)
    if a > 0:
        highlight(ctx, FLX, fy - 32, 95, 60, MUSTARD, a, t)
        tag(ctx, "A TINY BOAT", 470, 1170, INK, a, 26)
    a = win(t, B(1) + 0.1, B(2), 0.3)
    if a > 0:
        highlight(ctx, FLX, fy - 32, 95, 60, RED, a, t)
        tag(ctx, "FLOOD ALARM", 470, 1170, RED, a, 28)
    a = bw(t, 2)
    if a > 0:
        tag(ctx, "1 · BASE TRAY", 600, 1310, INK, a, 20)
        straight_arrow(ctx, 820, 1370, 380, 1415, WATER_D, a, lw=4, head=9)
        tag(ctx, "LOW CORNER", 300, 1470, WATER_D, a, 16)
    a = bw(t, 3)
    if a > 0:
        tag(ctx, "HOSE", VALVE[0], 1170, WATER_D, a, 16)
        tag(ctx, "DOOR SEAL", TX0 + 90, TY1 + 45, WATER_D, a, 16)
        tag(ctx, "PUMP", PUMP[0] + 110, PUMP[1] + 75, WATER_D, a, 16)
    a = bw(t, 4)
    if a > 0:
        highlight(ctx, FLX, fy - 30, 80, 44, MUSTARD, a, t)
        tag(ctx, "2 · FOAM FLOAT", 470, 1390, INK, a, 14)
        tag(ctx, "SWITCH", 470, SW[1] + 26, RED, a, 14)
    a = bw(t, 6)
    if a > 0:
        tag(ctx, "3 · SWITCH PRESSED", 330, 1185, RED, a * sstep(t, B(6) + 1.1, 0.2), 15)
        tag(ctx, "TO THE BOARD", 275, 1120, INK, a * sstep(t, B(6) + 1.8, 0.2), 13)
    a = bw(t, 7)
    if a > 0:
        highlight(ctx, VALVE[0], VALVE[1], 70, 70, RED, a, t)
        tag(ctx, "INLET VALVE · SHUT", 700, 1360, RED, a * sstep(t, B(7) + 1.4, 0.2), 22)
        tag(ctx, "LEAK!", BOARD[0] + BOARD[2] / 2, 460, RED, a, 24)
    a = bw(t, 8)
    if a > 0:
        highlight(ctx, PUMP[0], PUMP[1], 80, 75, TEAL, a, t)
        tag(ctx, "DRAIN PUMP · NONSTOP", 560, 1215, TEAL, a, 22)
    a = bw(t, 10)
    if a > 0:
        tag(ctx, "TRAY STILL WET", 470, 1180, WATER_D, a * (1 - sstep(t, B(11) - 1.2, 0.4)), 18)
        tag(ctx, "DRY · FLOAT DOWN", 470, 1180, INK, a * sstep(t, B(11) - 1.2, 0.4), 18)
        da = a * (1 - sstep(t, B(11) - 1.0, 0.5))
        for i in range(3):
            x = 240 + i * 90
            wavy_arrow(ctx, x, 1400, x, 1330, t, ORANGE, da * 0.8, amp=4, wl=18, lw=3, head=8)
    a = win(t, B(11) + 0.6, B(12) + 3, 0.3)
    if a > 0:
        tag(ctx, "FOAM = FLOOR GUARD", 540, 1530, RED, a, 30)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    fx, fy, z = cam_track(CAMKEYS, t, move=0.8)
    ctx.save()
    ctx.rectangle(0, 178, 1080, 1322); ctx.clip()
    ctx.translate(540, 930); ctx.scale(z, z); ctx.translate(-fx, -fy)
    scene(ctx, t, s)
    labels(ctx, t, s)
    ctx.restore()

def draw_hud(ctx, t, E):
    # beat 11: drying (evaporation) arrows are in world space; here only the "emergency" banner in the teaser
    a = win(t, B(1) + 0.6, B(2) - 0.05, 0.25)
    if a > 0:
        rrect(ctx, 210, 190, 660, 90, 18); setc(ctx, CREAM, 0.96 * a); ctx.fill_preserve()
        setc(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
        text_c(ctx, "EMERGENCY MODE", 540, 252, 46, RED, True, 3, a * (0.7 + 0.3 * math.sin(t * 8) ** 2))

def _alarm(ctx, t, a):
    rrect(ctx, 290, 185, 500, 140, 18); setc(ctx, INK, 0.95 * a); ctx.fill_preserve()
    setc(ctx, MUSTARD, a); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "ALARM ON", 540, 280, 70, RED, True, 6, a * (0.7 + 0.3 * math.sin(t * 6) ** 2))

_hud_old = draw_hud
def draw_hud(ctx, t, E):
    _hud_old(ctx, t, E)
    a = win(t, B(10) + 0.4, B(11) - 1.2, 0.3)
    if a > 0: _alarm(ctx, t, a)

SFX = [(0.5, 'pop'), (B(1) + 0.2, 'pop'), (B(1) + 0.5, 'click'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'),
       (B(4) + 0.3, 'pop'), (B(6) + 1.1, 'click'), (B(6) + 2.4, 'pop'), (B(7) + 1.4, 'click'),
       (B(8) + 0.3, 'pop'), (B(10) + 0.4, 'pop'), (B(11) + 0.6, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_buoy(ctx, t, lt, a):
    card_frame(ctx, "FOAM VS WATER", a, "LIGHTER THAN WATER = IT FLOATS", TEAL)
    # shallow tank, water rises a little, the foam block lifts off the bottom (UP = smaller y)
    floor = 500
    depth = 60 * sstep(lt, 0.4, 1.6)
    ctx.move_to(200, 330); ctx.line_to(200, floor); ctx.line_to(880, floor); ctx.line_to(880, 330)
    setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    if depth > 0.5:
        ctx.rectangle(203, floor - depth, 674, depth); setc(ctx, WATER, 0.7 * a); ctx.fill()
    lift = clamp(depth - 12, 0, 48)
    bx, bw_, bh = 540, 170, 70
    y1 = floor - lift; y0 = y1 - bh
    rrect(ctx, bx - bw_ / 2, y0, bw_, bh, 8); fill_stroke(ctx, FOAM, lw=4, alpha=a)
    text_c(ctx, "FOAM", bx, y0 + 46, 26, INK2, True, 2, a)
    up = sstep(lt, 1.6, 0.4) * a
    straight_arrow(ctx, 330, floor - 10, 330, 300, TEAL, up, lw=8, head=16)
    text_c(ctx, "PUSH UP", 330, 285, 22, TEAL, True, 1, up)
    straight_arrow(ctx, 750, y0 - 40, 750, y0 + 10, RED, up, lw=4, head=9)
    text_c(ctx, "LIGHT", 750, y0 - 50, 20, RED, True, 1, up)

def card_tubtray(ctx, t, lt, a):
    card_frame(ctx, "TUB ≠ TRAY", a, "PUMP: TUB ONLY · FLOAT STAYS UP", RED)
    # left: tub (drains), right: tray (stays wet); pump pipe connected to the tub only
    u = sstep(lt, 0.4, 2.2)
    rrect(ctx, 150, 280, 320, 220, 14); fill_stroke(ctx, hexc('#e9ecee'), lw=4, alpha=a)
    h = 120 * (1 - u)
    if h > 0.5:
        ctx.rectangle(156, 494 - h, 308, h); setc(ctx, WATER, 0.7 * a); ctx.fill()
    text_c(ctx, "TUB", 310, 270, 26, INK, True, 2, a)
    ctx.move_to(310, 500); ctx.line_to(310, 530); ctx.line_to(140, 530); setc(ctx, INK, a); ctx.set_line_width(10); ctx.stroke()
    text_c(ctx, "EMPTY", 310, 380, 26, TEAL, True, 1, a * sstep(lt, 2.4, 0.3))
    # tray: sloped floor (low on the LEFT), puddle, float lifted
    ctx.move_to(600, 400); ctx.line_to(600, 500); ctx.line_to(930, 470); ctx.line_to(930, 400)
    setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    ctx.move_to(604, 470); ctx.line_to(930 - 4, 470); ctx.line_to(604, 500); ctx.close_path()
    # water surface y 470, floor from (600,500) to (930,470) -> fills the left triangle
    setc(ctx, WATER, 0.7 * a); ctx.fill()
    bob = 3 * math.sin(lt * 3)
    rrect(ctx, 625, 425 + bob, 60, 38, 6); fill_stroke(ctx, FOAM, lw=3, alpha=a)
    ctx.rectangle(650, 360 + bob, 10, 65); fill_stroke(ctx, STEEL_D, lw=2, alpha=a)
    text_c(ctx, "TRAY", 765, 270, 26, INK, True, 2, a)
    text_c(ctx, "STILL WET", 790, 380, 24, WATER_D, True, 1, a)

CARDS = {'buoy': card_buoy, 'tubtray': card_tubtray}
