"""Cogwise episode: Those little holes in brick walls are there on purpose.
One idea: a brick facade is a rain SCREEN, not a waterproof wall. Rain soaks through brick and mortar,
runs down the BACK of the brick inside the air gap (~25 mm · 1 in), lands on a sloped sheet (flashing)
at the foot of the wall, and leaves through the open head joints of the bottom course: weep holes
(IRC: max 33 in · 84 cm apart, right above the flashing). Fill them and the water is trapped.

VIEWS (screen coordinates, y grows DOWN):
  - beats 1-2: the wall seen from the garden (elevation). One empty vertical joint in the BOTTOM course.
  - beat 3 on: cross-section through that empty joint. OUTSIDE on the LEFT (rain comes from the left),
    INSIDE on the RIGHT. Order left -> right: brick skin -> air gap -> inner wall -> plaster / room.
    Water: through the brick (+x), then DOWN the back face of the brick (+y), onto the flashing, which
    slopes DOWN toward the OUTSIDE (from the inner wall at the top-right to the brick at the bottom-left),
    then out through the weep hole (-x) and drips off the drip edge onto the ground.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="brick-weep-holes",
    title="Those little holes in brick walls are there on purpose 🧱 #Shorts",
    description=("That empty gap at the bottom of a brick wall isn't a mistake. It's the way out for the rain.\n\n"
                 "#Shorts #howthingswork #construction #home #cogwise"),
    hashtags=["Shorts", "howthingswork", "construction", "home", "bricks", "cogwise"],
    sources=[
        "https://www.jaspector.com/codes/irc-2018/ch07-wall-covering/brick-veneer-weep-holes-required-irc-2018/",
        "https://www.homebuilding.co.uk/advice/what-is-a-weep-vent",
        "https://www.bobvila.com/articles/weep-holes-in-brick/",
    ],
)

BEATS = [
    dict(dur=5.0, title="A MISTAKE?", caption="That gap between the bricks isn't a mistake. Your wall is supposed to leak."),
    dict(dur=5.0, title="THE SECRET", caption="Brick and mortar soak up rain like a sponge, and some of it gets through."),
    dict(dur=5.0, title="TWO WALLS", caption="Because a brick house wall is really two walls, with air in between."),
    dict(dur=4.8, title="1 · BRICK SKIN", caption="Outside, a single layer of brick. It only keeps off the weather."),
    dict(dur=5.6, title="2 · AIR GAP", caption="Behind it, an empty gap, about two and a half centimetres, one inch, wide."),
    dict(dur=4.2, title="3 · INNER WALL", caption="Then the real wall, the one holding up your house."),
    dict(dur=4.4, title="DRIVING RAIN", caption="In a storm, wind drives water straight through the bricks."),
    dict(dur=6.4, title="DOWN THE BACK", caption="It trickles down the back of the brick, inside the gap, without touching the inner wall."),
    dict(dur=4.8, title=None, caption="At the bottom, a sloped sheet called flashing catches every drop.", card='tray'),
    dict(dur=5.6, title="THE WAY OUT", caption="Then it slides out through these gaps, left empty on purpose. Weep holes."),
    dict(dur=5.2, title=None, caption="Fill them with mortar, and the water stays trapped inside the wall.", card='plug'),
    dict(dur=4.4, title="LEAKS IN · DRIPS OUT", caption="Every brick wall leaks. The weep hole is where it cries."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette
BRICK = hexc('#c4643f'); BRICK_D = hexc('#8f4228'); BRICK_W = hexc('#9c4a2c')   # dry / dark / wet
MORTAR = hexc('#d8cfbf'); BLOCK = hexc('#b9b4aa'); BLOCK_D = hexc('#8d877c')
CONC = hexc('#a9a49a'); SOIL = hexc('#8a6a48'); GRASS = hexc('#7d9a4e')
PLASTER = hexc('#f3ead8'); FLASH = hexc('#3b3842'); SKYC = hexc('#cfdde4')
WATER = TEAL

# ---------------------------------------------------------------- cross-section geometry
BX0, BX1 = 330, 440        # brick skin (outer face x=330, back face x=440)
GX0, GX1 = 440, 510        # air gap (drawn wider than life: real ~25 mm)
IX0, IX1 = 510, 680        # inner wall (block)
PX1 = 708                  # plaster inner face
TOP = 330                  # top of the section
COURSE = 80                # brick course height (incl. mortar)
FL_Y = 1330                # flashing level under the bottom course (brick side)
FL_UP = 1180               # flashing turned up against the inner wall
FL_KNEE = (IX0, 1292)      # flashing leaves the inner wall here and slopes down to the brick
DRIP_X = 304               # drip edge, sticking out past the outer face
GROUND = 1440              # garden level, below the flashing
WEEP = (BX0, FL_Y - COURSE, BX1, FL_Y)   # the bottom course is cut through its open head joint

# front view (beats 1-2)
EW, EH = 200, 70; EM = 10  # brick size / mortar
E_GROUND = 1360
E_WEEP_X = 560             # x of the open head joint in the bottom course

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['ring'] = win(t, 0.2, B(1) + 0.2, 0.25)
    s['soak'] = clamp(ease((t - B(1) - 0.3) / 2.5)) * (1 - clamp((t - B(2) - 0.2) / 0.6))
    s['turn'] = clamp((t - B(2)) / 0.7)                 # 0 = front view, 1 = cross-section
    s['two'] = bw(t, 2)
    s['skin'] = bw(t, 3); s['gap'] = bw(t, 4); s['inner'] = bw(t, 5)
    s['rain'] = 0.35 + 0.65 * clamp(ease((t - B(6)) / 0.6))
    s['storm'] = bw(t, 6, 8)
    s['through'] = clamp(ease((t - B(6) - 0.4) / 1.0))  # water starts crossing the brick
    s['down'] = clamp(ease((t - B(7) - 0.2) / 1.2))     # water runs down the back face
    s['down_tag'] = bw(t, 7)
    s['out'] = clamp(ease((t - B(9) - 0.2) / 1.0))      # water leaves through the weep hole
    s['weep'] = bw(t, 9)
    s['recap'] = bw(t, 11)
    s['wet'] = clamp((t - B(6) - 0.5) / 2.0)
    return s

# ---------------------------------------------------------------- front view (elevation)
def front_view(ctx, t, s):
    k = 1 - ease(s['turn'])
    if k <= 0.01: return
    ctx.save(); ctx.translate(540, 0); ctx.scale(k, 1); ctx.translate(-540, 0)
    # mortar background = the wall
    ctx.rectangle(60, 330, 960, E_GROUND - 330); setc(ctx, MORTAR); ctx.fill()
    rnd = random.Random(3)
    rows = int((E_GROUND - 330) / (EH + EM))
    for r in range(rows):
        y = E_GROUND - (r + 1) * (EH + EM) + EM / 2
        off = 0 if r % 2 == 0 else (EW + EM) / 2
        x = 60 - off
        while x < 1020:
            x0, x1 = max(x, 60), min(x + EW, 1020)
            gap_here = (r == 0 and abs(x - (E_WEEP_X + EM / 2)) < 2)
            if x1 > x0:
                wet = s['soak'] * (0.6 + 0.4 * rnd.random())
                ctx.rectangle(x0, y, x1 - x0, EH)
                fill_stroke(ctx, lerpc(BRICK, BRICK_W, wet), lw=2.5)
            x += EW + EM
    # the open head joint (weep hole) in the bottom course: a dark slot, no mortar
    y0 = E_GROUND - (EH + EM) + EM / 2
    ctx.rectangle(E_WEEP_X - 12, y0, 24, EH); setc(ctx, INK, 0.92); ctx.fill()
    # ground / grass
    ctx.rectangle(40, E_GROUND, 1000, 140); setc(ctx, SOIL); ctx.fill()
    ctx.rectangle(40, E_GROUND, 1000, 18); setc(ctx, GRASS); ctx.fill()
    # rain (beats 1-2), falling DOWN and slightly to the right
    ra = 0.5 + 0.5 * s['soak']
    for i in range(46):
        u = ((t * 1.3) + i * 0.137) % 1
        x = 80 + (i * 211) % 920 + 60 * u; y = 300 + u * 1060
        ctx.move_to(x, y); ctx.line_to(x + 8, y + 34); setc(ctx, WATER, 0.55 * ra); ctx.set_line_width(4); ctx.stroke()
    # red ring on the empty joint
    a = s['ring'] * k
    if a > 0:
        hx, hy = E_WEEP_X, y0 + EH / 2
        r = 58 + 4 * math.sin(t * 6)
        ctx.arc(hx, hy, r, 0, 2 * math.pi); setc(ctx, RED, a); ctx.set_line_width(6); ctx.stroke()
        ctx.move_to(hx + r * 0.6, hy - r * 0.8); ctx.line_to(hx + 150, hy - 190); ctx.set_line_width(5); ctx.stroke()
        tag(ctx, "MISTAKE?", hx + 210, hy - 230, RED, a, 30)
    ctx.restore()

# ---------------------------------------------------------------- cross-section
def flashing_pts():
    """flashing, from its top (against the inner wall) down to the drip edge outside"""
    return [(IX0 + 2, FL_UP), (IX0 + 2, FL_KNEE[1]), (BX1, FL_Y), (BX0, FL_Y + 4),
            (DRIP_X, FL_Y + 6), (DRIP_X - 6, FL_Y + 26)]

def brick_column(ctx, a, wet, plug=False):
    """the brick skin in section: one brick per course, mortar beds between; bottom course = open joint"""
    y = FL_Y - COURSE
    n = 0
    while y > TOP - COURSE:
        y0 = max(y, TOP)
        if n == 0:
            # open head joint: we look through the slot at the end of the next brick, far behind
            ctx.rectangle(BX0, y0 + 6, BX1 - BX0, COURSE - 6)
            setc(ctx, MORTAR if plug else hexc('#2f2a2a'), a); ctx.fill()
            ctx.rectangle(BX0, y0 + 6, BX1 - BX0, COURSE - 6); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
        else:
            h = (y + COURSE - 8) - y0
            if h > 0:
                ctx.rectangle(BX0, y0, BX1 - BX0, h)
                fill_stroke(ctx, lerpc(BRICK, BRICK_W, wet), lw=3, alpha=a)
        # mortar bed under each brick
        ctx.rectangle(BX0, y + COURSE - 8, BX1 - BX0, 8 if n else 6); setc(ctx, MORTAR, a); ctx.fill()
        y -= COURSE; n += 1

def section(ctx, t, s, plug=False):
    a = ease(clamp((s['turn'] - 0.55) / 0.45))
    if a <= 0: return
    ctx.push_group()
    # outside air (left) and room (right)
    ctx.rectangle(40, TOP, BX0 - 40, GROUND - TOP); setc(ctx, SKYC); ctx.fill()
    ctx.rectangle(PX1, TOP, 1040 - PX1, GROUND - TOP + 60); setc(ctx, hexc('#f7efdf')); ctx.fill()
    # foundation + ground
    ctx.rectangle(BX0 - 10, FL_Y + 6, IX1 - BX0 + 10, 1500 - FL_Y); fill_stroke(ctx, CONC, lw=4)
    ctx.rectangle(40, GROUND, BX0 - 50, 1500 - GROUND); setc(ctx, SOIL); ctx.fill()
    ctx.rectangle(40, GROUND, BX0 - 50, 14); setc(ctx, GRASS); ctx.fill()
    # inner wall (concrete blocks) + plaster
    for i, y in enumerate(range(TOP, int(FL_KNEE[1]) + 40, 100)):
        h = min(100, FL_Y + 6 - y)
        ctx.rectangle(IX0, y, IX1 - IX0, h); fill_stroke(ctx, BLOCK, lw=3)
        if h > 60:
            for cx in (IX0 + 45, IX1 - 45):
                rrect(ctx, cx - 26, y + 22, 52, h - 44, 6); setc(ctx, BLOCK_D, 0.7); ctx.fill()
    ctx.rectangle(IX1, TOP, PX1 - IX1, FL_Y + 6 - TOP); fill_stroke(ctx, PLASTER, lw=3)
    # air gap (empty)
    ctx.rectangle(GX0, TOP, GX1 - GX0, FL_Y - TOP); setc(ctx, hexc('#eef3f2')); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    brick_column(ctx, a, 0.85 * s['wet'], plug)
    # flashing
    pts = flashing_pts()
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    setc(ctx, FLASH, a); ctx.set_line_width(9); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    # zone highlights for the three parts
    sk, ga, inn = s['skin'], s['gap'], s['inner']
    if sk > 0: highlight(ctx, (BX0 + BX1) / 2, 830, 80, 520, MUSTARD, sk, t)
    if ga > 0: highlight(ctx, (GX0 + GX1) / 2, 830, 50, 520, TEAL, ga, t)
    if inn > 0: highlight(ctx, (IX0 + PX1) / 2, 830, 120, 520, MUSTARD, inn, t)

def rain(ctx, t, s, a):
    """rain comes from the LEFT, driven by the wind toward the wall (+x, +y)"""
    if a <= 0: return
    storm = s['storm']
    n = int(22 + 30 * s['rain'])
    slant = 0.25 + 0.9 * storm
    for i in range(n):
        u = ((t * (1.1 + 0.8 * storm)) + i * 0.173) % 1
        y0 = TOP + (i * 97) % 900
        x = 50 + u * (BX0 - 70); y = y0 + u * 160 * slant + u * 120
        if y > GROUND - 10: continue
        ctx.move_to(x, y); ctx.line_to(x + 22 * slant + 2, y + 30)
        setc(ctx, WATER, 0.6 * a); ctx.set_line_width(4); ctx.stroke()
    if storm > 0:
        for y in (520, 760, 1000):
            wavy_arrow(ctx, 70, y, BX0 - 30, y, t, INK, storm * a * 0.8, amp=8, wl=40, lw=5, head=14)

def drop(ctx, x, y, a, r=7):
    ctx.arc(x, y, r, 0, 2 * math.pi); setc(ctx, WATER, a); ctx.fill_preserve()
    setc(ctx, INK, 0.5 * a); ctx.set_line_width(1.5); ctx.stroke()

def water_path(ctx, t, s, a):
    """drops: through the brick (+x) -> down the back face (+y) -> flashing -> weep hole (-x) -> drip"""
    if a <= 0: return
    # 1) through the brick, slowly (soaking)
    ta = s['through'] * a
    if ta > 0:
        for k in range(10):
            yy = 470 + k * 78
            u = ((t * 0.35) + k * 0.31) % 1
            drop(ctx, lerp(BX0 + 6, BX1 - 4, u), yy + 10 * math.sin(k + u * 3), ta * 0.8, 5)
    # 2) down the back face of the brick, inside the gap
    da = s['down'] * a
    if da > 0:
        for k in range(9):
            u = ((t * 0.45) + k / 9) % 1
            y = lerp(500, FL_Y - 40, u)
            drop(ctx, GX0 + 9, y, da, 7)
        ctx.move_to(GX0 + 5, 480); ctx.line_to(GX0 + 5, FL_Y - 30)
        setc(ctx, WATER, 0.45 * da); ctx.set_line_width(6); ctx.stroke()
        # puddle on the flashing at the foot of the gap
        ctx.move_to(GX0, FL_Y - 2); ctx.line_to(GX0 + 40, FL_Y - 20); ctx.line_to(GX0, FL_Y - 20); ctx.close_path()
        setc(ctx, WATER, 0.5 * da * (1 - 0.6 * s['out'])); ctx.fill()
    # 3) out through the weep hole, along the flashing (-x), then off the drip edge
    oa = s['out'] * a
    if oa > 0:
        for k in range(6):
            u = ((t * 0.6) + k / 6) % 1
            if u < 0.7:
                x = lerp(GX0 + 6, DRIP_X, u / 0.7); y = FL_Y - 8
            else:
                x = DRIP_X - 6; y = lerp(FL_Y + 26, GROUND - 6, (u - 0.7) / 0.3)
            drop(ctx, x, y, oa, 7)

def overlays(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.5) / 0.5))
    if a <= 0: return
    tag(ctx, "OUTSIDE", 170, 380, TEAL, a, 26)
    tag(ctx, "INSIDE", 870, 380, INK, a, 26)
    if s['two'] > 0:
        tag(ctx, "WALL 1", (BX0 + BX1) / 2, 296, RED, s['two'], 26)
        tag(ctx, "WALL 2", (IX0 + PX1) / 2, 296, RED, s['two'], 26)
        tag(ctx, "AIR", (GX0 + GX1) / 2, 830, TEAL, s['two'], 22)
    if s['skin'] > 0: tag(ctx, "1 · BRICK SKIN", 190, 1000, INK, s['skin'], 24)
    if s['gap'] > 0:
        tag(ctx, "2 · AIR GAP", 870, 560, INK, s['gap'], 24)
        straight_arrow(ctx, 780, 580, GX1 + 6, 640, INK, s['gap'], lw=4, head=12)
        tag(ctx, "≈ 25 mm · 1 in", 870, 660, TEAL, s['gap'], 22)
    if s['inner'] > 0: tag(ctx, "3 · INNER WALL", 870, 1000, INK, s['inner'], 24)
    if s['storm'] > 0: tag(ctx, "WIND + RAIN", 180, 1180, INK, s['storm'], 24)
    if s['down_tag'] > 0:
        tag(ctx, "DOWN THE BACK", 740, 820, TEAL, s['down_tag'], 24)
        straight_arrow(ctx, 660, 845, GX0 + 22, 900, TEAL, s['down_tag'], lw=4, head=12)
        tag(ctx, "INNER WALL STAYS DRY", 760, 1100, INK, s['down_tag'], 20)
    w = s['weep']
    if w > 0:
        highlight(ctx, (BX0 + BX1) / 2, FL_Y - COURSE / 2, 90, 52, RED, w, t)
        tag(ctx, "WEEP HOLE", 190, 1180, RED, w, 26)
        tag(ctx, "FLASHING", 600, 1420, INK, w, 22)
        straight_arrow(ctx, 560, 1400, 480, FL_Y - 12, INK, w, lw=4, head=12)
    r = s['recap']
    if r > 0:
        tag(ctx, "LEAKS IN", 180, 640, TEAL, r, 28)
        tag(ctx, "DRIPS OUT", 180, 1180, RED, r, 28)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    front_view(ctx, t, s)
    a = ease(clamp((s['turn'] - 0.55) / 0.45))
    section(ctx, t, s)
    rain(ctx, t, s, a)
    water_path(ctx, t, s, a)
    overlays(ctx, t, s)

# camera: the empty joint fills the frame in the 1st second, wide for the two walls,
# push in on the gap while the water runs down, then on the weep hole
CAMKEYS = [(0, E_WEEP_X, 1000, 1.15), (B(1) + 0.4, 540, 900, 1.0),
           (B(7) + 0.2, 480, 1000, 1.22), (B(8) - 0.4, 540, 900, 1.0),
           (B(9) + 0.2, 420, 1180, 1.45), (B(10) - 0.4, 540, 900, 1.0)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)

def draw_hud(ctx, t, E):
    a = win(t, B(9) + 1.4, B(10), 0.3)
    if a > 0: hud(ctx, "WEEP HOLES (US CODE)", "≤ 84 cm apart", "33 in", a, RED, x=520, y=196, w=520)

SFX = [(0.3, 'pop'), (B(2) + 0.4, 'pop'), (B(3) + 0.3, 'pop'), (B(4) + 0.3, 'pop'), (B(5) + 0.3, 'pop'),
       (B(7) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_tray(ctx, t, lt, a):
    card_frame(ctx, "THE FLASHING", a, "SLOPES DOWN · TOWARD THE OUTSIDE", TEAL)
    # brick (left), gap, inner wall (right); flashing from the inner wall down under the brick
    ctx.rectangle(250, 262, 140, 200); fill_stroke(ctx, BRICK_W, lw=4, alpha=a)
    ctx.rectangle(560, 262, 160, 268); fill_stroke(ctx, BLOCK, lw=4, alpha=a)
    pts = [(556, 300), (556, 420), (390, 486), (250, 490), (200, 494), (194, 520)]
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    setc(ctx, FLASH, a); ctx.set_line_width(10); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    # drops slide DOWN the slope from the inner wall side toward the brick (-x, +y)
    for k in range(4):
        u = ((lt * 0.5) + k / 4) % 1
        x = lerp(540, 400, u); y = lerp(420, 474, u) - 8
        drop(ctx, x, y, a, 9)
    straight_arrow(ctx, 520, 400, 420, 442, TEAL, a, lw=6, head=16)
    text_c(ctx, "BRICK", 320, 252, 22, INK, True, 1, a)
    text_c(ctx, "INNER WALL", 640, 252, 22, INK, True, 1, a)

def card_plug(ctx, t, lt, a):
    card_frame(ctx, "WEEP HOLE FILLED", a, "WATER TRAPPED · WALL ROTS", RED)
    ctx.rectangle(300, 262, 120, 268); fill_stroke(ctx, BRICK_W, lw=4, alpha=a)
    ctx.rectangle(520, 262, 180, 268); fill_stroke(ctx, BLOCK, lw=4, alpha=a)
    # plugged joint (mortar) at the bottom of the brick
    ctx.rectangle(300, 470, 120, 60); fill_stroke(ctx, MORTAR, lw=4, alpha=a)
    # water rising in the gap
    lvl = 0.25 + 0.6 * ease(clamp(lt / 3.0))
    h = 268 * lvl
    ctx.rectangle(420, 530 - h, 100, h); setc(ctx, WATER, 0.7 * a); ctx.fill()
    # damp creeping into the inner wall
    ctx.rectangle(520, 530 - h * 0.8, 70 * lvl, h * 0.8); setc(ctx, BLOCK_D, 0.8 * a); ctx.fill()
    # red cross over the plug
    for (x0, y0, x1, y1) in ((320, 476, 400, 524), (400, 476, 320, 524)):
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); setc(ctx, RED, a); ctx.set_line_width(7); ctx.stroke()
    text_c(ctx, "MORTAR", 360, 252, 22, INK, True, 1, a)
    text_c(ctx, "WATER", 470, 252, 22, TEAL, True, 1, a)
    text_c(ctx, "DAMP", 610, 252, 22, RED, True, 1, a)

CARDS = {'tray': card_tray, 'plug': card_plug}
