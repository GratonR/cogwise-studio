"""Cogwise episode: This plastic plug grabs your wall from behind.
One idea: a hollow-wall plug does not grip the plasterboard (soft gypsum, "chalk"); turning the screw drags the
threaded tail toward the room, the slotted legs buckle outward and fold into a "fist" wider than the hole,
so the board is pinched between the screw head (front) and the fist (back).
Numbers (spoken): bare screw in 12.5 mm board ~6 kg / 13 lb pull-out; plug ~30 kg / 65 lb before the board breaks
(ultimate; working load ~1/4 of that, not spoken).

VIEW (screen coordinates, y grows DOWN): SIDE cross-section of a VERTICAL plasterboard wall.
  - Room ("you") on the LEFT (small x); cavity behind the board on the RIGHT (large x).
  - Board = vertical slab x BX0..BX1 (front face BX0, back face BX1), paper skins on both faces.
  - Screw axis horizontal at y = CY; head on the LEFT against the collar, tip pointing RIGHT (+x).
  - Turning the screw: it does NOT move axially; the threaded tail is pulled toward the head = toward -x ("toward you").
    The thread pattern drifts toward +x while it turns (right-hand screw, clockwise seen from the head).
  - Legs: upper leg bulges UP (-y), lower leg bulges DOWN (+y) = outward; folded, they press on the BACK face (BX1)
    with forces pointing -x (toward the board). The head presses the FRONT face with a force pointing +x.
  - Pull-out card: the bare screw leaves toward -x (the room) with a cone of gypsum, wider at the front face.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="wall-plug",
    title="This plastic plug grabs your wall from behind ✊ #Shorts",
    description=("Your wall is basically chalk. So how does a little plastic plug hold a shelf?\n\n"
                 "#Shorts #howthingswork #diy #home #cogwise"),
    hashtags=["Shorts", "howthingswork", "diy", "home", "physics", "cogwise"],
    sources=[
        "https://engineerfix.com/how-much-weight-can-drywall-screws-hold/",
        "https://www.rapid.com/en-gw/blog/rapid-tools/plasterboard-fixing/how-hollow-wall-anchors-work-and-how-to-use-them/",
        "https://finehomebuilding.com/1999/05/01/hollow-wall-anchors",
        "https://www.fischer-international.com/en/products/innovations/duoline/duopower",
    ],
)

def _d(c, extra=0.0):
    return round(0.42 * len(c.split()) + 0.7 + extra, 1)

_B = [
    ("YOUR WALL IS CHALK", "Your wall is basically chalk. This plug doesn't grip it. It makes a fist.", None),
    ("THE SECRET", "Turn the screw, and the plug folds up behind the board, wider than the hole.", None),
    ("1 · THE BOARD", "Plasterboard is gypsum between two paper sheets, twelve and a half millimetres, half an inch.", None),
    ("BARE SCREW", "A bare screw only cuts a thread in that chalk.", None),
    (None, "Hang six kilos, thirteen pounds, and it pulls the chalk out.", 'pullout'),
    ("2 · THE LEGS", "The plug is a plastic sleeve with slotted legs. Its tail grabs the screw.", None),
    ("3 · THE PULL", "Turning, the screw drags the tail toward you.", None),
    (None, "The legs can't go anywhere, so they buckle outward and squash against the board.", 'buckle'),
    ("THE FIST", "Now the board is pinched between the screw head and that plastic fist.", None),
    ("SPREAD", "Your shelf no longer tugs one thread. It presses a whole patch of board.", None),
    ("THE NUMBERS", "It holds around thirty kilos, sixty-five pounds, before the board gives up.", None),
    ("A FIST", "So your shelf doesn't hang on chalk. It hangs on a fist behind the wall.", None),
]
BEATS = [dict(dur=_d(c), title=ti, caption=c, card=k) for ti, c, k in _B]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette
GYP = hexc('#ece6da'); GYP_D = hexc('#c9bfae')
PAPERSK = hexc('#c9a56b')
PLASTIC = hexc('#f7f3ea'); PLASTIC_E = hexc('#26232b')
STEEL = hexc('#8b8f96'); STEEL_D = hexc('#5d6168'); STEEL_L = hexc('#c4c8ce')
WOOD = hexc('#c9a26b'); WOOD_D = hexc('#8a6a3e')
BLUE = hexc('#2f6fb3')

# ---------------------------------------------------------------- geometry
CY = 1000                    # screw axis
BX0, BX1 = 360, 450          # board front / back face (90 px = 12.5 mm)
BY0, BY1 = 560, 1470         # board visible span
HOLE_R = 26                  # hole half height
SLEEVE_IN = 12               # inner half height of the plug wall (screw passes inside)
COLLAR_X0 = 344
LEG_L = 270                  # leg length (back face -> tail)
TAIL_W = 38
D_END = 40                   # leg span when fully folded
SHAFT_R = 10
TIP_X = 800
HEAD_X1 = COLLAR_X0          # head touches the collar
HEAD_W = 46; HEAD_R = 40

def state(t):
    s = {}
    # fold progress p: hook (beat 0), kept folded through beat 2; unfolded again from beat 5, folds on beats 6-7
    if t < B(3):
        p = ease(clamp((t - 0.25) / 1.3))
    elif t < B(6):
        p = 0.0
    elif t < B(7):
        p = 0.5 * ease(clamp((t - B(6) - 0.3) / (BEATS[6]['dur'] - 0.5)))
    else:
        p = 0.5 + 0.5 * ease(clamp((t - B(7) - 0.2) / 2.6))
    s['p'] = p
    s['turning'] = 1.0 if (0.25 < t < 1.55) or (B(6) + 0.3 < t < B(7) + 2.8) else 0.0
    s['plug'] = 1 - win(t, B(3), B(5), 0.4)          # plug hidden while the bare screw is shown
    s['bare'] = win(t, B(3) + 0.2, B(5), 0.4)
    s['fist_tag'] = win(t, 1.5, B(1), 0.3)
    s['sides'] = win(t, 0.2, B(2), 0.3)
    s['holecmp'] = bw(t, 1)
    s['board_tag'] = bw(t, 2)
    s['legs_tags'] = bw(t, 5)
    s['pull'] = win(t, B(6) + 0.3, B(7) + 2.8, 0.3)
    s['pinch'] = bw(t, 8)
    s['shelf'] = ease(clamp((t - B(9) - 0.2) / 0.6))
    s['spread'] = win(t, B(9) + 0.6, B(11), 0.3)
    s['recap'] = win(t, B(11) + 0.6, B(12) + 2, 0.3)
    return s

def tail_x(p):
    return BX1 + lerp(LEG_L, D_END, p)

def leg_apex(p):
    """Inextensible leg pinned at both ends: half-span d/2, bulge h (outward from the hole edge)."""
    d = tail_x(p) - BX1
    h = math.sqrt(max((LEG_L / 2) ** 2 - (d / 2) ** 2, 0))
    return BX1 + d / 2, h

# ---------------------------------------------------------------- board
def board(ctx, t, bare=0.0):
    ctx.rectangle(BX0, BY0, BX1 - BX0, BY1 - BY0); setc(ctx, GYP); ctx.fill()
    rnd = random.Random(11)
    for _ in range(260):
        x = rnd.uniform(BX0 + 8, BX1 - 8); y = rnd.uniform(BY0 + 6, BY1 - 6)
        ctx.arc(x, y, rnd.uniform(1.2, 2.6), 0, 2 * math.pi); setc(ctx, GYP_D, 0.8); ctx.fill()
    for x in (BX0, BX1 - 6):                         # paper skins on both faces
        ctx.rectangle(x, BY0, 6, BY1 - BY0); setc(ctx, PAPERSK); ctx.fill()
    ctx.rectangle(BX0, BY0, BX1 - BX0, BY1 - BY0); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    # torn edges top/bottom (it continues)
    for y0, sg in ((BY0, -1), (BY1, 1)):
        ctx.move_to(BX0 - 4, y0)
        for i in range(7):
            ctx.line_to(BX0 + (i + 0.5) * (BX1 - BX0) / 7, y0 + sg * (10 if i % 2 == 0 else 0))
        ctx.line_to(BX1 + 4, y0); ctx.line_to(BX1 + 4, y0 + sg * 30); ctx.line_to(BX0 - 4, y0 + sg * 30); ctx.close_path()
        setc(ctx, WALL1); ctx.fill()

def hole(ctx):
    ctx.rectangle(BX0 - 1, CY - HOLE_R, BX1 - BX0 + 2, 2 * HOLE_R); setc(ctx, hexc('#d8cdb6')); ctx.fill()

# ---------------------------------------------------------------- screw
def shaft(ctx, x0, x1, phase, a=1.0):
    ctx.rectangle(x0, CY - SHAFT_R, x1 - x0, 2 * SHAFT_R); fill_stroke(ctx, STEEL, lw=3, alpha=a)
    # thread crests: slanted ticks; they drift toward +x while the screw turns (right-hand, clockwise)
    pitch = 16
    off = (phase * pitch) % pitch
    x = x0 + off
    while x < x1 - 4:
        ctx.move_to(x, CY - SHAFT_R - 5); ctx.line_to(x + 6, CY + SHAFT_R + 5)
        x += pitch
    setc(ctx, STEEL_D, a); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(x1, CY - SHAFT_R); ctx.line_to(x1 + 22, CY); ctx.line_to(x1, CY + SHAFT_R); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=3, alpha=a)

def head(ctx, x1, a=1.0):
    x0 = x1 - HEAD_W
    ctx.move_to(x1, CY - HEAD_R)
    ctx.curve_to(x0 - 6, CY - HEAD_R, x0 - 6, CY + HEAD_R, x1, CY + HEAD_R); ctx.close_path()
    g = cairo.LinearGradient(0, CY - HEAD_R, 0, CY + HEAD_R)
    g.add_color_stop_rgb(0, *STEEL_L[:3]); g.add_color_stop_rgb(1, *STEEL_D[:3])
    ctx.set_source(g); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(x0 + 2, CY); ctx.line_to(x0 + 20, CY); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()

def turn_arrow(ctx, t, x, a):
    """Curved 'turn' arrow around the head (drawn as an ellipse seen edge-on)."""
    if a <= 0: return
    ph = t * 4
    ctx.save(); ctx.translate(x, CY); ctx.scale(0.35, 1.0)
    ctx.arc(0, 0, 78, -math.pi * 0.85 + ph % 0.6, math.pi * 0.55 + ph % 0.6)
    ctx.restore(); setc(ctx, RED, a); ctx.set_line_width(7); ctx.stroke()
    tag(ctx, "TURN", x - 10, CY - 130, RED, a, 26)

# ---------------------------------------------------------------- plug
def plug(ctx, t, s, a):
    p = s['p']; tx = tail_x(p); ax, h = leg_apex(p)
    ctx.push_group()
    # collar against the front face
    rrect(ctx, COLLAR_X0, CY - 48, BX0 - COLLAR_X0 + 2, 96, 4); fill_stroke(ctx, PLASTIC, PLASTIC_E, lw=4)
    # sleeve walls in the hole (hollow: the screw shows between them)
    for sg in (-1, 1):
        y0 = CY + sg * SLEEVE_IN; y1 = CY + sg * HOLE_R
        ctx.rectangle(BX0, min(y0, y1), BX1 - BX0, abs(y1 - y0)); fill_stroke(ctx, PLASTIC, PLASTIC_E, lw=3)
    # legs: hinged at the back face and at the tail, bulging OUTWARD (up for the top leg, down for the bottom one)
    for sg in (-1, 1):
        yb = CY + sg * (SLEEVE_IN + HOLE_R) / 2
        ya = CY + sg * ((SLEEVE_IN + HOLE_R) / 2 + h)
        ctx.move_to(BX1, yb); ctx.line_to(ax, ya); ctx.line_to(tx + 2, yb)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(ctx, PLASTIC_E); ctx.set_line_width(HOLE_R - SLEEVE_IN + 8); ctx.stroke_preserve()
        setc(ctx, PLASTIC); ctx.set_line_width(HOLE_R - SLEEVE_IN); ctx.stroke()
    # tail (threaded nut part) that grabs the screw
    rrect(ctx, tx, CY - HOLE_R - 2, TAIL_W, 2 * HOLE_R + 4, 6); fill_stroke(ctx, PLASTIC, PLASTIC_E, lw=4)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

def tail_teeth(ctx, s, a):
    """Inner thread of the tail, drawn over the shaft so it reads as 'grabbing' it."""
    tx = tail_x(s['p'])
    for i in range(3):
        x = tx + 8 + i * 10
        ctx.move_to(x, CY - SHAFT_R - 2); ctx.line_to(x + 5, CY + SHAFT_R + 2)
    setc(ctx, INK, 0.8 * a); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(tx, CY - HOLE_R - 2, TAIL_W, HOLE_R - SHAFT_R); fill_stroke(ctx, PLASTIC, PLASTIC_E, lw=3, alpha=a)
    ctx.rectangle(tx, CY + SHAFT_R + 2, TAIL_W, HOLE_R - SHAFT_R); fill_stroke(ctx, PLASTIC, PLASTIC_E, lw=3, alpha=a)

# ---------------------------------------------------------------- bare screw (beats 3-4)
def bare_screw(ctx, t, a):
    if a <= 0: return
    ctx.push_group()
    tip = 560
    shaft(ctx, BX0 - 4, tip, 0)
    head(ctx, BX0 - 2)
    rnd = random.Random(4)
    for _ in range(26):                            # crumbs of gypsum around the thread, inside the board
        x = rnd.uniform(BX0 + 10, BX1 - 10); y = CY + rnd.choice((-1, 1)) * rnd.uniform(SHAFT_R + 6, SHAFT_R + 22)
        ctx.arc(x, y, rnd.uniform(2, 4.5), 0, 2 * math.pi); setc(ctx, hexc('#b3a68e')); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ba = bw(t, 3)
    highlight(ctx, (BX0 + BX1) / 2, CY, 70, 52, RED, ba * a, t)
    tag(ctx, "THREAD IN CHALK", 680, CY - 150, RED, ba * a, 26)

# ---------------------------------------------------------------- shelf (beat 9 on)
def shelf(ctx, a, dx):
    if a <= 0: return
    x1 = HEAD_X1 + dx + 2          # bracket plate between head and collar
    ctx.push_group()
    ctx.rectangle(x1 - 2, CY - 70, 16, 190); fill_stroke(ctx, STEEL_L, lw=3)
    ctx.rectangle(150, CY + 100, x1 - 148, 36); fill_stroke(ctx, WOOD, WOOD_D, lw=4)
    ctx.move_to(x1, CY + 100); ctx.line_to(x1 - 70, CY + 100); ctx.line_to(x1, CY + 30); ctx.close_path()
    fill_stroke(ctx, STEEL_L, lw=3)
    for i, (w, hh) in enumerate(((54, 90), (46, 120), (52, 70))):  # a few books
        x = 165 + i * 58
        rrect(ctx, x, CY + 100 - hh, w - 6, hh, 4); fill_stroke(ctx, (MUSTARD, TEAL_L, RED)[i], lw=3)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    straight_arrow(ctx, 240, CY + 170, 240, CY + 260, INK, a, lw=8, head=16)
    tag(ctx, "LOAD", 240, CY + 300, INK, a, 24)

def draw_set(ctx):
    pass

def CAM(t):
    # gentle zoom on the plug; (cx, cy) lands at screen (540, 900)
    return 520, 960, 1.32

def draw(ctx, t, E):
    s = state(t)
    board(ctx, t)
    if s['plug'] > 0.01: hole(ctx)
    pa = s['plug']
    dx = -16 * s['shelf']
    if pa > 0.01:
        phase = 0.0
        # phase grows while turning: thread marks drift toward +x
        if t < B(3): phase = 6 * s['p']
        else: phase = 12 * s['p']
        shaft(ctx, HEAD_X1 + dx - 2, TIP_X, phase, pa)
        plug(ctx, t, s, pa)
        tail_teeth(ctx, s, pa)
        shelf(ctx, s['shelf'] * pa, dx)
        head(ctx, HEAD_X1 + dx, pa)
    bare_screw(ctx, t, s['bare'])
    overlays(ctx, t, s)

def overlays(ctx, t, s):
    p = s['p']; ax, h = leg_apex(p); tx = tail_x(p)
    a = s['sides']
    if a > 0:
        tag(ctx, "ROOM", 250, 700, INK, a, 26)
        tag(ctx, "BEHIND THE BOARD", 720, 700, INK, a, 26)
    a = s['fist_tag'] * s['plug']
    if a > 0:
        highlight(ctx, BX1 + 40, CY, 70, 175, RED, a, t)
        tag(ctx, "FIST", BX1 + 170, CY + 210, RED, a, 30)
    a = s['holecmp']
    if a > 0:
        # dotted bracket: hole height (small) vs fist height (big)
        def bracket(x, y0, y1, col, lab, side):
            ctx.set_dash([10, 8]); setc(ctx, col, a); ctx.set_line_width(4)
            ctx.move_to(x, y0); ctx.line_to(x, y1); ctx.stroke()
            for y in (y0, y1):
                ctx.move_to(x - 14, y); ctx.line_to(x + 14, y); ctx.stroke()
            ctx.set_dash([])
            ty = (y0 + y1) / 2 if side < 0 else y0 + 30
            tag(ctx, lab, x + side * 90, ty, col, a, 26)
        bracket(BX0 - 70, CY - HOLE_R, CY + HOLE_R, TEAL, "HOLE", -1)
        top = CY - (HOLE_R + SLEEVE_IN) / 2 - h - 12; bot = CY + (HOLE_R + SLEEVE_IN) / 2 + h + 12
        bracket(BX1 + 110, top, bot, RED, "FIST", 1)
    a = s['board_tag']
    if a > 0:
        tag(ctx, "PLASTERBOARD", 680, 1330, INK, a, 26)
    a = s['legs_tags'] * s['plug']
    if a > 0:
        tag(ctx, "COLLAR", 230, CY - 120, INK, a, 24)
        tag(ctx, "SLOTTED LEGS", 600, CY - 120, INK, a, 24)
        highlight(ctx, tx + TAIL_W / 2, CY, 46, 52, RED, a, t)
        tag(ctx, "TAIL", tx + 20, CY + 120, RED, a, 26)
    turn_arrow(ctx, t, HEAD_X1 - HEAD_W - 30 - 16 * s['shelf'], s['turning'] * s['plug'] * 0.95)
    a = s['pull']
    if a > 0:
        y = CY - HOLE_R - 46
        straight_arrow(ctx, tx + 120, y, tx + 6, y, RED, a, lw=10, head=18)
        tag(ctx, "TOWARD YOU", tx + 80, y - 60, RED, a * bw(t, 6), 26)
    a = s['pinch']
    if a > 0:
        straight_arrow(ctx, 170, CY, HEAD_X1 - HEAD_W - 8, CY, RED, a, lw=12, head=20)
        for sg in (-1, 1):
            y = CY + sg * 95
            straight_arrow(ctx, BX1 + 150, y, BX1 + 8, y, RED, a, lw=12, head=20)
        tag(ctx, "PINCHED", (BX0 + BX1) / 2, CY - 260, RED, a, 30)
    a = s['spread']
    if a > 0:
        # whole patch: many short arrows from the fist onto the back face, all pointing -x (onto the board)
        ys = [CY + k * 22 for k in range(-7, 8) if abs(k) >= 2]
        for y in ys:
            straight_arrow(ctx, BX1 + 60, y, BX1 + 6, y, RED, a, lw=5, head=10)
        ctx.rectangle(BX1 - 2, CY - 160, 8, 320); setc(ctx, RED, 0.35 * a); ctx.fill()
        tag(ctx, "WHOLE PATCH", 690, CY - 230, RED, a * bw(t, 9), 26)
    a = s['recap']
    if a > 0:
        highlight(ctx, BX1 + 40, CY, 70, 175, RED, a, t)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=175, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def slice_panel(ctx, t, a):
    """Beat 2: the board's sandwich, paper / gypsum / paper, with its thickness."""
    _panel(ctx, a)
    x0, x1 = 130, 760; y0, y1 = 245, 405
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); setc(ctx, GYP, a); ctx.fill()
    rnd = random.Random(2)
    for _ in range(140):
        ctx.arc(rnd.uniform(x0 + 6, x1 - 6), rnd.uniform(y0 + 16, y1 - 16), rnd.uniform(1.5, 3), 0, 2 * math.pi)
        setc(ctx, GYP_D, a); ctx.fill()
    for y in (y0, y1 - 12):
        ctx.rectangle(x0, y, x1 - x0, 12); setc(ctx, PAPERSK, a); ctx.fill()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "GYPSUM", (x0 + x1) / 2, 338, 34, INK, True, 2, a)
    text_c(ctx, "PAPER", (x0 + x1) / 2, 236, 22, WOOD_D, True, 2, a)
    text_c(ctx, "PAPER", (x0 + x1) / 2, 438, 22, WOOD_D, True, 2, a)
    straight_arrow(ctx, 830, 330, 830, y0 + 2, RED, a, lw=5, head=10)
    straight_arrow(ctx, 830, 320, 830, y1 - 2, RED, a, lw=5, head=10)
    text_c(ctx, "12.5 mm", 920, 320, 30, RED, True, 1, a)
    text_c(ctx, "½ in", 920, 360, 28, RED, True, 1, a)

def numbers_panel(ctx, t, a):
    """Beat 10: pull-out load, bare screw vs plug."""
    _panel(ctx, a)
    k = ease(clamp((t - B(10) - 0.3) / 1.2))
    full = 640
    rows = ((285, "BARE SCREW", 6 / 30, "6 kg · 13 lb", INK2, False), (395, "PLUG", 1.0, "~30 kg · 65 lb", RED, True))
    for y, lab, f, val, col, inside in rows:
        text_c(ctx, lab, 200, y + 10, 26, INK, True, 1, a)
        w = full * f * k + 4
        rrect(ctx, 300, y - 28, w, 50, 10); fill_stroke(ctx, col, lw=3, alpha=a)
        va = a * clamp(k * 3 - 0.2)
        if inside: text_c(ctx, val, 300 + w / 2, y + 10, 28, WHITE, True, 1, va * clamp(k * 2 - 1))
        else: text_c(ctx, val, 300 + w + 120, y + 10, 26, col, True, 1, va)

def recap_panel(ctx, t, a):
    _panel(ctx, a, y=215, h=200)
    text_c(ctx, "SHELF = FIST", 540, 300, 58, INK, True, 3, a)
    text_c(ctx, "BEHIND THE WALL", 540, 375, 40, RED, True, 3, a)

def draw_hud(ctx, t, E):
    a = win(t, B(2) + 0.3, B(3), 0.3)
    if a > 0: slice_panel(ctx, t, a)
    a = win(t, B(10) + 0.2, B(11), 0.3)
    if a > 0: numbers_panel(ctx, t, a)
    a = win(t, B(11) + 0.6, B(12) + 2, 0.3)
    if a > 0: recap_panel(ctx, t, a)

SFX = [(0.3, 'click'), (1.5, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.4, 'pop'), (B(3) + 0.3, 'pop'),
       (B(5) + 0.3, 'pop'), (B(5) + 1.4, 'pop'), (B(6) + 0.3, 'click'), (B(8) + 0.3, 'pop'),
       (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop'), (B(11) + 0.6, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_pullout(ctx, t, lt, a):
    """Bare screw + 6 kg: it leaves toward the room (-x) with a cone of gypsum, wider at the front face."""
    card_frame(ctx, "BARE SCREW + 6 kg · 13 lb", a, "IT PULLS THE CHALK OUT", RED)
    bx0, bx1, cy = 560, 620, 380
    m = ease(clamp((lt - 1.4) / 1.6))           # pull-out progress
    off = -150 * m
    # board with a crater where the cone was
    ctx.rectangle(bx0, 250, bx1 - bx0, 290); setc(ctx, GYP, a); ctx.fill()
    for x in (bx0, bx1 - 5):
        ctx.rectangle(x, 250, 5, 290); setc(ctx, PAPERSK, a); ctx.fill()
    if m > 0.02:
        ctx.move_to(bx0, cy - 46); ctx.line_to(bx1, cy - 12); ctx.line_to(bx1, cy + 12); ctx.line_to(bx0, cy + 46); ctx.close_path()
        setc(ctx, hexc('#d8cdb6'), a); ctx.fill()
    ctx.rectangle(bx0, 250, bx1 - bx0, 290); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    # cone of gypsum stuck on the screw (wide at the front face = room side)
    ctx.move_to(bx0 + off, cy - 46); ctx.line_to(bx1 + off, cy - 12); ctx.line_to(bx1 + off, cy + 12); ctx.line_to(bx0 + off, cy + 46); ctx.close_path()
    fill_stroke(ctx, GYP_D, lw=3, alpha=a)
    # screw
    sx0, sx1 = bx0 - 40 + off, bx1 + 20 + off
    ctx.rectangle(sx0, cy - 7, sx1 - sx0, 14); fill_stroke(ctx, STEEL, lw=2, alpha=a)
    ctx.move_to(sx0, cy - 30); ctx.curve_to(sx0 - 36, cy - 30, sx0 - 36, cy + 30, sx0, cy + 30); ctx.close_path()
    fill_stroke(ctx, STEEL_L, lw=3, alpha=a)
    # weight hanging from the head by a cord
    hx = sx0 - 20
    ctx.move_to(hx, cy + 28); ctx.line_to(hx, 440); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    rrect(ctx, hx - 55, 440, 110, 80, 10); fill_stroke(ctx, INK2, lw=3, alpha=a)
    text_c(ctx, "6 kg", hx, 490, 28, WHITE, True, 1, a)
    if m > 0.05:
        straight_arrow(ctx, 330, 300, 230, 300, RED, a * m, lw=8, head=16)
    rnd = random.Random(9)
    for i in range(10):
        u = clamp(m * 1.4 - i * 0.04)
        if u <= 0: continue
        ctx.arc(bx0 - 10 - u * rnd.uniform(40, 140), cy + rnd.uniform(-40, 40) + u * u * 90, 4, 0, 2 * math.pi)
        setc(ctx, GYP_D, a); ctx.fill()

def card_buckle(ctx, t, lt, a):
    """Close-up of the legs: the tail comes toward the board (-x), both legs bow OUTWARD and squash flat on it."""
    card_frame(ctx, "THE LEGS BUCKLE", a, "NOWHERE TO GO · SO THEY FOLD OUT", RED)
    cy = 395; L = 230; e = 16
    bx = 300
    ctx.rectangle(bx - 70, 255, 70, 280); fill_stroke(ctx, GYP, lw=3, alpha=a)
    text_c(ctx, "BOARD", bx - 35, 245, 20, INK, True, 1, a)
    q = ease(clamp((lt - 0.5) / 2.8))
    d = lerp(L - 4, 40, q)
    h = math.sqrt(max((L / 2) ** 2 - (d / 2) ** 2, 0))
    h = min(h, 128)
    tx = bx + d
    ctx.rectangle(bx + 2, cy - 4, 640, 8); setc(ctx, STEEL, a); ctx.fill()
    for sg in (-1, 1):
        ctx.move_to(bx, cy + sg * e); ctx.line_to(bx + d / 2, cy + sg * (e + h)); ctx.line_to(tx, cy + sg * e)
        setc(ctx, PLASTIC_E, a); ctx.set_line_width(20); ctx.stroke_preserve()
        setc(ctx, PLASTIC, a); ctx.set_line_width(13); ctx.stroke()
        if 0.05 < q < 0.97 and h < 85:
            straight_arrow(ctx, bx + d / 2, cy + sg * (e + h + 8), bx + d / 2, cy + sg * (e + h + 50), RED, a, lw=6, head=12)
    rrect(ctx, tx, cy - 26, 34, 52, 6); fill_stroke(ctx, PLASTIC, PLASTIC_E, lw=3, alpha=a)
    straight_arrow(ctx, tx + 130, cy, tx + 44, cy, RED, a, lw=9, head=18)
    text_c(ctx, "TAIL", tx + 17, cy + 62, 22, RED, True, 1, a)

CARDS = {'pullout': card_pullout, 'buckle': card_buckle}
