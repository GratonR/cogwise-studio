"""Cogwise episode: You can boil water on induction through a sheet of paper.
One idea: an induction hob makes no heat itself. A flat copper coil under the glass makes a magnetic
field that flips direction >20 000 times a second; each flip drives eddy currents (whirlpools of current)
inside the steel base of the pan, steel resists them, so the BASE heats. Glass and paper carry no current,
so the field passes through them; they only warm up by touching the pan (~100 °C / 212 °F with water inside).

VIEW: side cross-section of hob + paper + saucepan. Screen coordinates: y grows DOWN (physical "up" = -y).
Field (phase +): UP through the centre of the coil, OUTWARD along the steel base, DOWN outside the coil,
back INWARD under the coil. Phase -: everything reversed.
Coil current (phase +): left wires = dot (out of screen), right wires = cross (into screen); with x right,
physical y up, z out of screen, that loop has its magnetic moment pointing UP -> consistent with the field.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="induction-hob",
    title="You can boil water on induction through a sheet of paper 📄🔥 #Shorts",
    description=("An induction hob makes no heat at all: the heat is made inside the steel base of your pan.\n\n"
                 "#Shorts #howthingswork #induction #kitchen #cogwise"),
    hashtags=["Shorts", "howthingswork", "induction", "kitchen", "engineering", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Induction_cooking",
        "https://canarymedia.com/articles/electrification/how-do-induction-stoves-actually-work",
        "https://mecs.org.uk/blog/not-all-induction-cookware-is-created-equal/",
    ],
)

BEATS = [
    dict(dur=5.2, title="PAPER UNDER THE PAN", caption="You can boil water on an induction hob through a sheet of paper."),
    dict(dur=6.0, title="IT WON'T BURN", caption="And the paper won't even scorch, because the hob itself makes no heat at all."),
    dict(dur=5.6, title="THE SECRET", caption="The heat is made inside the pan, in the metal of its own base."),
    dict(dur=4.4, title="1 · THE COIL", caption="Under the glass hides a flat coil of copper wire."),
    dict(dur=5.0, title=None, caption="Its magnetic field flips direction over twenty thousand times every second."),
    dict(dur=5.6, title=None, caption="Each flip drags electric current around in little whirlpools inside the steel base.", card='eddy'),
    dict(dur=5.8, title="2 · THE PAN BASE", caption="These are eddy currents, and steel resists them hard, so the metal heats up."),
    dict(dur=5.6, title="RIGHT WHERE THE FOOD IS", caption="So the heat appears directly under your food, not in a burner below it."),
    dict(dur=6.0, title=None, caption="Paper and glass can't carry current, so the field passes straight through them untouched.", card='through'),
    dict(dur=7.4, title="3 · THE PAPER", caption="They only warm up by touching the pan: with water inside, about one hundred Celsius, two hundred twelve Fahrenheit."),
    dict(dur=4.6, title="LIFT THE PAN", caption="Lift the pan away, and the heating stops in an instant."),
    dict(dur=5.8, title="THE PAN IS THE STOVE", caption="So an induction hob never cooks anything. It turns your pan into the stove."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
CX = 540
GLASS_T, GLASS_B = 1060, 1092          # glass-ceramic top
PAPER_T = 1046                          # paper 1046..1060 (lies on the glass; thickness exaggerated)
PX0, PX1 = 200, 840                     # paper extent
BASE_T, BASE_B = 1020, 1046             # steel pan base (sits on the paper)
PAN_X0, PAN_X1 = 300, 780
WALL = 16; RIM = 760
WATER_T = 790
HOB_X0, HOB_X1, HOB_B = 140, 940, 1250
COIL_Y = 1124; COIL_R = 12
COIL_R_X = [590, 622, 654, 686, 718]                  # right half wires
COIL_L_X = [2 * CX - x for x in COIL_R_X]             # left half (mirror)
LIFT = 250

STEEL = hexc('#8d949b'); STEEL_D = hexc('#5e656c'); GLASSC = hexc('#2f2c35'); COPPER = hexc('#c46f33')
PAPERC = hexc('#fffaf0'); WATER = hexc('#9fd0de'); BODY = hexc('#d9cdb4'); BODY_IN = hexc('#efe6d2')

FLIP_HZ = 1.1   # visual flip rate (the real one is > 20 000 Hz: shown on the HUD)
def phase(t):
    """+1 = field UP through the centre, -1 = DOWN. Smooth sign with a quick swap."""
    v = math.sin(2 * math.pi * FLIP_HZ * t)
    return max(-1.0, min(1.0, v * 4))

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    up = clamp(ease((t - B(10) - 0.2) / 0.9)); down = clamp(ease((t - B(11) - 0.1) / 0.9))
    s['lift'] = LIFT * up * (1 - down)
    on = 1 - up * (1 - down)                                # heating on (pan on the hob)
    s['on'] = on
    s['boil'] = on
    s['glow'] = on * max(0.45, bw(t, 2), bw(t, 6, 8), 0.85 * bw(t, 11))
    s['cut'] = clamp(ease((t - B(3) - 0.1) / 0.8))          # hob cut-away revealing the coil (stays)
    s['field'] = on * clamp(ease((t - B(4) - 0.1) / 0.6))   # field lines from beat 5 on
    s['tag_paper'] = win(t, 0.3, B(1) + 0.2, 0.3)
    s['tag_noscorch'] = bw(t, 1)
    s['tag_secret'] = bw(t, 2)
    s['tag_coil'] = bw(t, 3, 5)
    s['tag_base'] = bw(t, 6)
    s['heat_up'] = on * max(bw(t, 7), 0.0)
    s['nob'] = bw(t, 7)
    s['paper_warm'] = bw(t, 9)
    s['tag_off'] = clamp(ease((t - B(10) - 0.9) / 0.4)) * (1 - clamp(ease((t - B(11)) / 0.3)))
    s['recap'] = bw(t, 11)
    return s

# ---------------------------------------------------------------- drawing helpers
def wire_symbol(ctx, x, y, out, a, col=COPPER, r=COIL_R):
    """cross-section of a wire. out=True: dot (current out of the screen); False: cross (into the screen)."""
    ctx.arc(x, y, r, 0, 2 * math.pi); fill_stroke(ctx, col, lw=3, alpha=a)
    if out:
        ctx.arc(x, y, r * 0.32, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()
    else:
        d = r * 0.5
        ctx.move_to(x - d, y - d); ctx.line_to(x + d, y + d); ctx.move_to(x - d, y + d); ctx.line_to(x + d, y - d)
        setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()

def loop_points(up_x, down_x, top_y, bot_y):
    """right-hand field loop, listed in the phase + direction: up at up_x, outward at top_y, down at down_x, back in."""
    return [(up_x, bot_y), (up_x, top_y), (down_x, top_y), (down_x, bot_y), (up_x, bot_y)]

LOOPS = [loop_points(552, 770, 1028, 1196), loop_points(570, 750, 1038, 1178)]

def chevron(ctx, x, y, ang, col, a, size=11):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    ctx.move_to(-size, -size * 0.8); ctx.line_to(size * 0.6, 0); ctx.line_to(-size, size * 0.8)
    setc(ctx, col, a); ctx.set_line_width(4); ctx.stroke(); ctx.restore()

def draw_field(ctx, t, s, lift):
    a = s['field']
    if a <= 0: return
    p = phase(t); sg = 1 if p >= 0 else -1; k = abs(p)
    col = TEAL if sg > 0 else RED
    for mirror in (1, -1):
        for L in LOOPS:
            P = [(CX + mirror * (x - CX), y) for (x, y) in L]
            # the top run follows the pan base only while the pan sits on the hob
            ctx.move_to(*P[0])
            for q in P[1:]: ctx.line_to(*q)
            setc(ctx, col, 0.75 * a * (0.35 + 0.65 * k)); ctx.set_line_width(4); ctx.set_dash([12, 8]); ctx.stroke(); ctx.set_dash([])
            # chevrons: middle of each segment, pointing along the loop (reversed in phase -)
            for i in range(4):
                (x0, y0), (x1, y1) = P[i], P[i + 1]
                ang = math.atan2(y1 - y0, x1 - x0) + (0 if sg > 0 else math.pi)
                chevron(ctx, (x0 + x1) / 2, (y0 + y1) / 2, ang, col, a * (0.4 + 0.6 * k))

def draw_hob(ctx, t, s):
    cut = s['cut']
    # counter cabinet (one prop)
    rrect(ctx, 50, 1080, 980, 420, 10); fill_stroke(ctx, FILL3, lw=5)
    # hob body: inside is revealed by a cut-away
    rrect(ctx, HOB_X0, GLASS_B - 4, HOB_X1 - HOB_X0, HOB_B - GLASS_B + 4, 8)
    fill_stroke(ctx, lerpc(BODY, BODY_IN, cut), lw=5)
    if cut > 0:
        # coil (two rows of wire sections) + a support plate
        rrect(ctx, 340, COIL_Y + 18, 400, 12, 4); fill_stroke(ctx, hexc('#9a8f7a'), lw=3, alpha=cut)
        p = phase(t) if s['field'] > 0 else 1
        sg = p >= 0
        for x in COIL_L_X: wire_symbol(ctx, x, COIL_Y, sg, cut)
        for x in COIL_R_X: wire_symbol(ctx, x, COIL_Y, not sg, cut)
        # supply wires to the electronics box
        rrect(ctx, 760, 1180, 150, 54, 8); fill_stroke(ctx, hexc('#55505d'), lw=3, alpha=cut)
        text_c(ctx, "ELECTRONICS", 835, 1214, 15, CREAM, True, 1, cut)
        ctx.move_to(718, COIL_Y + 12); ctx.line_to(718, 1160); ctx.line_to(780, 1160); ctx.line_to(780, 1180)
        setc(ctx, COPPER, cut); ctx.set_line_width(5); ctx.stroke()
    else:
        pass
    # front controls (when closed)
    if cut < 1:
        for i, x in enumerate((230, 290, 350)):
            ctx.arc(x, 1215, 16, 0, 2 * math.pi); fill_stroke(ctx, hexc('#55505d'), lw=3, alpha=1 - cut)
    # glass-ceramic top (black glass)
    rrect(ctx, HOB_X0 - 10, GLASS_T, HOB_X1 - HOB_X0 + 20, GLASS_B - GLASS_T, 6)
    fill_stroke(ctx, GLASSC, lw=4)
    ctx.move_to(HOB_X0 + 20, GLASS_T + 7); ctx.line_to(HOB_X1 - 20, GLASS_T + 7)
    setc(ctx, WHITE, 0.15); ctx.set_line_width(3); ctx.stroke()
    # cooking-zone ring printed on the glass (cross-section: two small marks)
    for x in (360, 720):
        ctx.move_to(x, GLASS_T + 2); ctx.line_to(x, GLASS_T + 10); setc(ctx, WHITE, 0.4); ctx.set_line_width(3); ctx.stroke()

def draw_paper(ctx, t, s):
    w = s['paper_warm']
    ctx.move_to(PX0, PAPER_T + 2); ctx.line_to(PX1 - 20, PAPER_T)
    ctx.curve_to(PX1 - 6, PAPER_T - 1, PX1 + 4, PAPER_T - 8, PX1 + 10, PAPER_T - 14)   # slight curl at the right edge
    ctx.line_to(PX1 + 16, PAPER_T - 8); ctx.curve_to(PX1 + 6, PAPER_T + 6, PX1 - 6, PAPER_T + 14, PX1 - 20, PAPER_T + 14)
    ctx.line_to(PX0, PAPER_T + 14); ctx.close_path()
    fill_stroke(ctx, lerpc(PAPERC, hexc('#fbd29a'), 0.8 * w), lw=3)
    for x in range(PX0 + 14, PX1 - 30, 46):          # faint ruled lines so it reads as paper
        ctx.move_to(x, PAPER_T + 4); ctx.line_to(x + 22, PAPER_T + 4); setc(ctx, hexc('#9fc3d3'), 0.9); ctx.set_line_width(2); ctx.stroke()

def pan_path(ctx, oy):
    # outer profile of the saucepan (walls + base) as one closed shape
    ctx.move_to(PAN_X0, RIM + oy); ctx.line_to(PAN_X0, BASE_B + oy); ctx.line_to(PAN_X1, BASE_B + oy)
    ctx.line_to(PAN_X1, RIM + oy); ctx.line_to(PAN_X1 - WALL, RIM + oy); ctx.line_to(PAN_X1 - WALL, BASE_T + oy)
    ctx.line_to(PAN_X0 + WALL, BASE_T + oy); ctx.line_to(PAN_X0 + WALL, RIM + oy); ctx.close_path()

def draw_pan(ctx, t, s):
    oy = -s['lift']
    # water
    ctx.rectangle(PAN_X0 + WALL, WATER_T + oy, PAN_X1 - PAN_X0 - 2 * WALL, BASE_T - WATER_T)
    setc(ctx, WATER, 0.9); ctx.fill()
    # surface ripple
    ctx.move_to(PAN_X0 + WALL, WATER_T + oy)
    for i in range(41):
        x = lerp(PAN_X0 + WALL, PAN_X1 - WALL, i / 40)
        ctx.line_to(x, WATER_T + oy + 3 * s['boil'] * math.sin(x / 22 + t * 6))
    setc(ctx, hexc('#4f9fb5'), 1); ctx.set_line_width(3); ctx.stroke()
    # bubbles rising from the hot base
    rnd = random.Random(4)
    for i in range(34):
        x = rnd.uniform(PAN_X0 + 40, PAN_X1 - 40); sp = rnd.uniform(0.35, 0.7); ph = rnd.random()
        u = (t * sp + ph) % 1
        y = lerp(BASE_T - 10, WATER_T + 10, u) + oy
        r = lerp(4, 10, u)
        ba = s['boil'] * (1 - u ** 4)
        if ba > 0.02:
            ctx.arc(x + 6 * math.sin(t * 3 + i), y, r, 0, 2 * math.pi); setc(ctx, WHITE, 0.85 * ba); ctx.fill_preserve()
            setc(ctx, hexc('#4f9fb5'), ba); ctx.set_line_width(2); ctx.stroke()
    # steam
    for i in range(4):
        x = 400 + i * 90; u = (t * 0.4 + i * 0.27) % 1
        y0 = WATER_T - 30 + oy - u * 180
        ctx.move_to(x, y0)
        ctx.curve_to(x + 20, y0 - 30, x - 20, y0 - 60, x, y0 - 90)
        setc(ctx, hexc('#b8b0a2'), 0.5 * s['boil'] * (1 - u)); ctx.set_line_width(6); ctx.stroke()
    # pan body
    pan_path(ctx, oy); fill_stroke(ctx, STEEL, lw=5)
    # base glow (the heat is made HERE)
    g = s['glow']
    if g > 0:
        rrect(ctx, PAN_X0 + 4, BASE_T + oy + 2, PAN_X1 - PAN_X0 - 8, BASE_B - BASE_T - 4, 6)
        setc(ctx, lerpc(ORANGE, RED, 0.5), 0.85 * g); ctx.fill()
        rrect(ctx, PAN_X0 + 20, BASE_T + oy + 8, PAN_X1 - PAN_X0 - 40, 8, 4); setc(ctx, MUSTARD, 0.7 * g); ctx.fill()
    pan_path(ctx, oy); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # handle (left)
    rrect(ctx, 130, RIM + 24 + oy, PAN_X0 - 130, 28, 12); fill_stroke(ctx, hexc('#3b3842'), lw=4)
    # rim lip highlight
    for x in (PAN_X0, PAN_X1 - WALL):
        ctx.rectangle(x + 3, RIM + oy + 6, 4, 200); setc(ctx, WHITE, 0.25); ctx.fill()

def draw_heat(ctx, t, s):
    oy = -s['lift']
    a = s['heat_up']
    for x in (380, 470, 560, 650, 720):
        wavy_arrow(ctx, x, BASE_T + oy - 6, x, BASE_T + oy - 150, t, RED, a, amp=8, wl=30, lw=6, head=14)
    # beat 10: the paper warms only by touching the hot pan (short arrows DOWN from the base into the paper)
    w = s['paper_warm']
    for x in (360, 480, 600, 720):
        wavy_arrow(ctx, x, BASE_B - 2, x, PAPER_T + 10, t, ORANGE, w, amp=3, wl=10, lw=3, head=6)

def draw_overlays(ctx, t, s):
    oy = -s['lift']
    tag(ctx, "A SHEET OF PAPER", 300, 975, INK, s['tag_paper'], 24)
    if s['tag_paper'] > 0:
        straight_arrow(ctx, 260, 1000, 250, 1042, INK, s['tag_paper'], lw=4, head=9)
    a = s['tag_noscorch']
    if a > 0:
        highlight(ctx, 250, 1053, 50, 18, TEAL, a, t)
        tag(ctx, "NOT SCORCHED", 250, 995, TEAL, a, 18)
        tag(ctx, "HOB: NO FLAME, NO HOT PLATE", 330, 1120, INK, a, 13)
    a = s['tag_secret']
    if a > 0:
        highlight(ctx, CX, BASE_T + 13 + oy, 270, 30, RED, a, t)
        tag(ctx, "THE HEAT IS MADE HERE", CX, 1150, RED, a, 26)
        straight_arrow(ctx, CX, 1118, CX, 1062, RED, a, lw=5, head=12)
    a = s['tag_coil']
    if a > 0:
        highlight(ctx, CX, COIL_Y, 220, 26, MUSTARD, a, t)
        tag(ctx, "1 · COPPER COIL", CX, 1222, INK, a, 24)
    a = s['tag_base']
    if a > 0:
        highlight(ctx, CX, BASE_T + 13 + oy, 270, 30, RED, a, t)
        tag(ctx, "2 · STEEL RESISTS = HEAT", CX, 960, RED, a, 24)
    a = s['nob']
    if a > 0:
        tag(ctx, "HEAT INTO THE FOOD", CX, 740, RED, a, 24)
        tag(ctx, "NO BURNER BELOW", CX, 1222, TEAL, a, 22)
    a = s['paper_warm']
    if a > 0:
        tag(ctx, "3 · WARMED BY THE PAN", 330, 975, ORANGE, a, 20)
        highlight(ctx, 330, 1053, 120, 18, ORANGE, a, t)
    a = s['tag_off']
    if a > 0:
        tag(ctx, "HEATING: OFF", CX, 980, TEAL, a, 28)
    a = s['recap']
    if a > 0:
        tag(ctx, "1 · COIL", 300, 1222, INK, a, 24)
        tag(ctx, "2 · PAN BASE = THE STOVE", CX, 960, RED, a, 24)
        tag(ctx, "3 · PAPER", 820, 1000, ORANGE, a, 22)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    draw_hob(ctx, t, s)
    draw_paper(ctx, t, s)
    draw_pan(ctx, t, s)
    draw_field(ctx, t, s, s['lift'])
    draw_heat(ctx, t, s)
    draw_overlays(ctx, t, s)

# camera: wide at 0 s, push on the paper edge (beat 2), wide, push on the coil (beats 4-5), wide again
CAMKEYS = [(0, 540, 985, 1.25),
           (B(1) + 0.1, 330, 1040, 2.1),
           (B(2), 540, 1000, 1.2),
           (B(3) + 0.1, 540, 1090, 1.45),
           (B(5) - 0.4, 540, 1000, 1.2),
           (B(9) + 0.1, 420, 1030, 1.6),
           (B(10), 540, 960, 1.2)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)
ANCHOR = (540, 1300)

def draw_hud(ctx, t, E):
    a = bw(t, 1)
    if a > 0: hud(ctx, "HEAT MADE BY THE HOB", "NONE", "no flame, no hot plate", a, TEAL, x=500, y=196, w=540)
    a = bw(t, 4)
    if a > 0:
        p = phase(t)
        hud(ctx, "MAGNETIC FIELD FLIPS", "> 20 000 ×/s", "UP / DOWN, UP / DOWN", a, TEAL if p >= 0 else RED,
            flash=0.4 * abs(p), x=500, y=196, w=540)
    a = bw(t, 9)
    if a > 0: hud(ctx, "PAPER (WATER INSIDE)", "≈ 100 °C · 212 °F", "paper burns only above ≈ 230 °C", a, ORANGE, x=440, y=196, w=600)

SFX = [(0.3, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'),
       (B(6) + 0.3, 'pop'), (B(7) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(10) + 0.9, 'click'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def circ_arrow(ctx, cx, cy, r, ccw, phase_off, col, a, lw=5):
    """circular arrow (whirlpool). ccw = counter-clockwise ON SCREEN."""
    a0 = phase_off; span = 1.6 * math.pi
    if ccw:
        ctx.arc_negative(cx, cy, r, a0, a0 - span); end = a0 - span; tang = end - math.pi / 2
    else:
        ctx.arc(cx, cy, r, a0, a0 + span); end = a0 + span; tang = end + math.pi / 2
    setc(ctx, col, a); ctx.set_line_width(lw); ctx.stroke()
    ex, ey = cx + r * math.cos(end), cy + r * math.sin(end)
    ctx.save(); ctx.translate(ex, ey); ctx.rotate(tang)
    ctx.move_to(4, 0); ctx.line_to(-12, -8); ctx.line_to(-12, 8); ctx.close_path(); setc(ctx, col, a); ctx.fill(); ctx.restore()

def card_eddy(ctx, t, lt, a):
    card_frame(ctx, "THE STEEL BASE, SEEN FROM ABOVE", a, "EACH FLIP = CURRENT WHIRLPOOLS", RED)
    g = clamp(lt / 3.5)
    # base disc (top view) gets hotter
    ctx.arc(540, 400, 150, 0, 2 * math.pi)
    fill_stroke(ctx, lerpc(STEEL, lerpc(ORANGE, RED, 0.4), g), lw=5, alpha=a)
    ctx.arc(540, 400, 150, 0, 2 * math.pi); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    p = phase(t); ccw = p >= 0; k = abs(p)
    rot = (lt * 2.4) * (-1 if ccw else 1)
    for (dx, dy, r) in ((0, 0, 44), (-82, -52, 30), (82, -52, 30), (-82, 56, 30), (82, 56, 30)):
        circ_arrow(ctx, 540 + dx, 400 + dy, r, ccw, rot + dx * 0.01, MUSTARD if k > 0.3 else INK2, a * (0.4 + 0.6 * k))
    # field indicator (top view: UP = toward you = dot, DOWN = away from you = cross)
    col = TEAL if p >= 0 else RED
    text_c(ctx, "FIELD", 230, 310, 22, INK, True, 1, a)
    ctx.arc(230, 395, 42, 0, 2 * math.pi); fill_stroke(ctx, CREAM, stroke=col, lw=6, alpha=a)
    if p >= 0:
        ctx.arc(230, 395, 12, 0, 2 * math.pi); setc(ctx, col, a); ctx.fill()
    else:
        for d in (1, -1):
            ctx.move_to(230 - 22, 395 - 22 * d); ctx.line_to(230 + 22, 395 + 22 * d)
        setc(ctx, col, a); ctx.set_line_width(7); ctx.stroke()
    text_c(ctx, "UP" if p >= 0 else "DOWN", 230, 470, 24, col, True, 1, a)
    text_c(ctx, "FIELD FLIPS:", 850, 370, 22, INK, True, 1, a)
    text_c(ctx, "SPIN FLIPS", 850, 405, 22, INK, True, 1, a)
    text_c(ctx, "TOO", 850, 440, 22, INK, True, 1, a)

def card_through(ctx, t, lt, a):
    card_frame(ctx, "WHAT THE FIELD MEETS", a, "ONLY THE METAL CARRIES CURRENT", RED)
    p = phase(t); sg = p >= 0; k = abs(p); col = TEAL if sg else RED
    X0, X1 = 130, 560
    g = clamp(lt / 3.0)
    # layers, top -> bottom on screen: steel pan base, paper, glass, (gap), coil
    rrect(ctx, X0, 270, X1 - X0, 44, 6); fill_stroke(ctx, lerpc(STEEL, lerpc(ORANGE, RED, 0.4), g), lw=4, alpha=a)
    ctx.rectangle(X0, 314, X1 - X0, 16); fill_stroke(ctx, PAPERC, lw=3, alpha=a)
    ctx.rectangle(X0, 330, X1 - X0, 42); fill_stroke(ctx, GLASSC, lw=4, alpha=a)
    for i in range(6):
        ctx.arc(170 + i * 70, 470, 15, 0, 2 * math.pi); fill_stroke(ctx, COPPER, lw=3, alpha=a)
    # field arrows pass straight through glass + paper into the steel (and flip)
    for x in (205, 345, 485):
        if sg: straight_arrow(ctx, x, 450, x, 282, col, a * (0.4 + 0.6 * k), lw=6, head=13)
        else: straight_arrow(ctx, x, 282, x, 450, col, a * (0.4 + 0.6 * k), lw=6, head=13)
    # whirlpool marks only inside the steel
    for x in (275, 415):
        circ_arrow(ctx, x, 292, 12, sg, lt * 3, MUSTARD, a * g, lw=3)
    # labels on the right, one per layer
    text_c(ctx, "STEEL: CURRENT = HEAT", 775, 300, 24, RED, True, 0.5, a)
    text_c(ctx, "PAPER: NO CURRENT", 775, 333, 22, TEAL, True, 0.5, a)
    text_c(ctx, "GLASS: NO CURRENT", 775, 366, 22, TEAL, True, 0.5, a)
    text_c(ctx, "COPPER COIL", 775, 478, 22, INK, True, 1, a)

CARDS = {'eddy': card_eddy, 'through': card_through}
