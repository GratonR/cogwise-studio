"""Cogwise episode: This nail pulls two boards together  (toenailing: a slanted nail's push splits into
'down' + 'sideways', and the sideways part drags the top board along -> framers start the stud 3 mm off its line).

Screen frame: x to the right, y DOWN. The nail enters the stud's LEFT face and points down-right (+x, +y),
so the hammer's push along the nail has a +x part: the stud slides RIGHT, toward the fixed board / the mark."""
import math, cairo
from cogwise.style import *

META = dict(
    slug="toenail",
    title="This nail pulls two boards together 🔨",
    description=("A slanted nail splits every hammer blow in two: down, and sideways. The sideways part drags the board.\n\n"
                 "#Shorts #howthingswork #carpentry #woodworking #framing #physics #cogwise"),
    hashtags=["Shorts", "howthingswork", "carpentry", "woodworking", "framing", "physics", "cogwise"],
    sources=[
        "https://www.thisoldhouse.com/woodworking/the-right-way-to-toenail",
        "https://kiwix.lema.org/wikipedia_en_all_mini_2024-02/A/Toenailing",
        "https://www.finehomebuilding.com/project-guides/framing/how-it-works-nails",
        "https://scienceinsights.org/what-is-blind-nailing-in-flooring-and-siding/",
    ],
)

BEATS = [
    dict(dur=5.6, title=None, caption="One slanted nail can close this gap between two boards, all by itself."),           # 0
    dict(dur=5.6, title="WATCH THE GAP", caption="Watch closely: with every hammer blow, the top board slides a little closer."),  # 1
    dict(dur=5.2, title="THE SECRET: ALONG THE NAIL", caption="The secret: a hammer only pushes a nail along its own length."),  # 2
    dict(dur=5.6, title="STRAIGHT = ALL DOWN", caption="Drive it straight down, and all of that push goes into the wood."),      # 3
    dict(dur=4.8, title=None, caption="But tilt the nail, and the push splits into two parts.", card='split'),                  # 4
    dict(dur=4.8, title="1 · DOWN", caption="One part drives the nail deeper, down into the board underneath."),                # 5
    dict(dur=5.2, title="2 · SIDEWAYS", caption="The other part shoves sideways, in the direction the nail is pointing."),      # 6
    dict(dur=6.0, title="3 · THE BOARD RIDES ALONG", caption="The nail is gripped tight by the top board, so the board rides along."),  # 7
    dict(dur=6.0, title=None, caption="At forty-five degrees, the two parts are equal, so every blow sinks and slides.", card='angle'),  # 8
    dict(dur=6.8, title="THE FRAMER'S TRICK", caption="That's why framers set a stud three millimetres, an eighth of an inch, off its line."),  # 9
    dict(dur=6.4, title="ONTO THE MARK", caption="Blow after blow, it creeps right onto the pencil mark, and the gap shuts tight."),  # 10
    dict(dur=4.8, title="SLANT = DOWN + TOGETHER", caption="Slanted nail: one push, split two ways — down, and together."),    # 11
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.3):
    return win(t, B(i) + 0.08, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry (screen px, y down)
WOOD = hexc('#e9c98f'); WOOD_D = hexc('#c99a55'); WOOD_L = hexc('#f3dcb0'); GRAIN = hexc('#b98744')
STEEL = hexc('#9aa3ab'); STEEL_D = hexc('#5f6870'); STEEL_L = hexc('#d5dadf')
DOWNC = TEAL; SIDEC = MUSTARD; PUSHC = RED; GREEN = hexc('#4c9d6b'); PENCIL = hexc('#4a4650')

PLATE_Y0, PLATE_Y1 = 1150, 1290         # bottom plate (horizontal board), front face visible
PLATE_X0, PLATE_X1 = 70, 1010
STUD_W = 150; STUD_TOP = 560
GAP0 = 72                               # drawn gap (exaggerated; "3 mm · 1/8 in" in reality)
X_MARK = 400                            # pencil mark = where the stud's LEFT face must land
FIX_X0 = X_MARK + STUD_W                # fixed neighbour board (left face) = target of the stud's right face
ANG = math.radians(45)                  # nail angle below horizontal
AX, AY = math.cos(ANG), math.sin(ANG)   # nail axis head->tip: +x (right) and +y (DOWN on screen)
ENTRY_H = 80                            # nail enters the stud's left face this high above the plate
NAIL_L = 260
D0, D1 = 120, 260                       # driven length along the axis (start -> head flush)

# hammer blows: (design time, driven length after the blow)
BLOWS = [(0.55, 142), (B(1) + 0.7, 156), (B(1) + 1.9, 170), (B(1) + 3.1, 184),
         (B(7) + 1.6, 198), (B(10) + 0.5, 214), (B(10) + 1.6, 230), (B(10) + 2.7, 245), (B(10) + 3.8, 260)]
IMPACT = 0.10

def driven(t):
    d = D0
    for (tb, dn) in BLOWS:
        if t >= tb: d = lerp(d, dn, ease((t - tb) / IMPACT))
    return d

def shift(d):
    """stud slide (px, +x = right) for a driven length d: proportional to the nail's sideways travel."""
    return (d - D0) / (D1 - D0) * GAP0

def stud_x(t):
    return X_MARK - GAP0 + shift(driven(t))

def nail_pts(t):
    """entry point on the stud's left face, head and tip positions."""
    d = driven(t); sx = stud_x(t)
    ex, ey = sx, PLATE_Y0 - ENTRY_H
    head = (ex - (NAIL_L - d) * AX, ey - (NAIL_L - d) * AY)
    tip = (ex + d * AX, ey + d * AY)
    return (ex, ey), head, tip, d

def hammer_phase(t):
    """0 = resting far, 1 = on the nail head. Wind-up 0.45 s before each blow, quick strike, rebound."""
    v = 0.0
    for (tb, _) in BLOWS:
        u = t - tb
        if -0.45 <= u < 0: v = max(v, ease((u + 0.45) / 0.45))
        elif 0 <= u < 0.35: v = max(v, 1 - ease(u / 0.35))
    return v

def hammer_on(t):
    return max(win(t, 0.0, B(2) - 0.1, 0.25), win(t, B(7) + 0.6, B(8) - 0.1, 0.25), win(t, B(10), B(11) - 0.2, 0.25))

# ---------------------------------------------------------------- drawing
def wood_grain(ctx, x0, y0, x1, y1, vertical, seed, a=1.0):
    ctx.save(); ctx.rectangle(x0, y0, x1 - x0, y1 - y0); ctx.clip()
    n = 5
    for k in range(n):
        f = (k + 0.5) / n
        if vertical:
            x = lerp(x0, x1, f)
            ctx.move_to(x, y0)
            for i in range(1, 21):
                y = lerp(y0, y1, i / 20); ctx.line_to(x + 5 * math.sin(i * 0.9 + seed + k), y)
        else:
            y = lerp(y0, y1, f)
            ctx.move_to(x0, y)
            for i in range(1, 31):
                x = lerp(x0, x1, i / 30); ctx.line_to(x, y + 4 * math.sin(i * 0.8 + seed + k))
        setc(ctx, GRAIN, 0.45 * a); ctx.set_line_width(2.5); ctx.stroke()
    ctx.restore()

def draw_plate(ctx, st):
    ctx.rectangle(PLATE_X0, PLATE_Y0, PLATE_X1 - PLATE_X0, PLATE_Y1 - PLATE_Y0); fill_stroke(ctx, WOOD, lw=5)
    wood_grain(ctx, PLATE_X0, PLATE_Y0, PLATE_X1, PLATE_Y1, False, 1.3)
    # subfloor / floor line under the plate
    ctx.rectangle(30, PLATE_Y1, 1020, 22); fill_stroke(ctx, FILL3, lw=4)

def draw_board(ctx, x, seed, fill=WOOD_L):
    ctx.rectangle(x, STUD_TOP, STUD_W, PLATE_Y0 - STUD_TOP); fill_stroke(ctx, fill, lw=5)
    wood_grain(ctx, x, STUD_TOP, x + STUD_W, PLATE_Y0, True, seed)
    # end grain hint on top
    ctx.rectangle(x, STUD_TOP - 14, STUD_W, 14); fill_stroke(ctx, WOOD_D, lw=4)

def draw_nail(ctx, t, st):
    (ex, ey), head, tip, d = nail_pts(t)
    # shank (visible part from head to entry, then hidden part drawn as dashed "x-ray")
    ctx.move_to(*head); ctx.line_to(ex, ey)
    setc(ctx, STEEL_D); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.move_to(*head); ctx.line_to(ex, ey)
    setc(ctx, STEEL_L); ctx.set_line_width(5); ctx.stroke()
    # hidden part inside the wood (x-ray)
    ctx.move_to(ex, ey); ctx.line_to(*tip)
    setc(ctx, STEEL_D, 0.85); ctx.set_line_width(10); ctx.set_dash([16, 9]); ctx.stroke(); ctx.set_dash([])
    # head: a short bar perpendicular to the axis
    nx, ny = -AY, AX
    ctx.move_to(head[0] + nx * 22, head[1] + ny * 22); ctx.line_to(head[0] - nx * 22, head[1] - ny * 22)
    setc(ctx, STEEL_D); ctx.set_line_width(12); ctx.stroke()
    # point
    ctx.arc(tip[0], tip[1], 6, 0, 2 * math.pi); setc(ctx, STEEL_D); ctx.fill()

def draw_hammer(ctx, t, st):
    a = st['hammer']
    if a <= 0: return
    _, head, _, _ = nail_pts(t)
    ph = hammer_phase(t)
    back = lerp(230, 18, ph)                     # distance from the nail head, measured back along the axis
    fx, fy = head[0] - AX * back, head[1] - AY * back   # striking face centre
    ctx.save(); ctx.translate(fx, fy); ctx.rotate(ANG)  # local +x = along the nail, toward the tip
    ctx.push_group()
    # head: steel block whose face (local x = 0) strikes along +x
    rrect(ctx, -110, -40, 110, 80, 10); fill_stroke(ctx, STEEL, lw=5)
    ctx.rectangle(-14, -40, 14, 80); setc(ctx, STEEL_D); ctx.fill()
    # handle, perpendicular to the head, going up-left on screen (local -y)
    rrect(ctx, -76, -330, 36, 300, 14); fill_stroke(ctx, WOOD_D, lw=5)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()
    # impact flash
    for (tb, _) in BLOWS:
        u = t - tb
        if 0 <= u < 0.25:
            k = 1 - u / 0.25
            for i in range(5):
                an = ANG + math.pi + (i - 2) * 0.45
                r0, r1 = 34, 34 + 40 * (1 - k * 0.3)
                ctx.move_to(head[0] + r0 * math.cos(an + math.pi / 2), head[1] + r0 * math.sin(an + math.pi / 2))
                ctx.line_to(head[0] + r1 * math.cos(an + math.pi / 2), head[1] + r1 * math.sin(an + math.pi / 2))
            setc(ctx, MUSTARD, a * k); ctx.set_line_width(6); ctx.stroke()

def gap_dim(ctx, x0, x1, y, a, label=None, col=RED):
    if a <= 0 or x1 - x0 < 2: return
    ctx.move_to(x0, y - 18); ctx.line_to(x0, y + 18); ctx.move_to(x1, y - 18); ctx.line_to(x1, y + 18)
    setc(ctx, col, a); ctx.set_line_width(3); ctx.stroke()
    if x1 - x0 > 30:
        straight_arrow(ctx, (x0 + x1) / 2, y, x0 + 2, y, col, a, lw=3, head=7)
        straight_arrow(ctx, (x0 + x1) / 2, y, x1 - 2, y, col, a, lw=3, head=7)
    if label: tag(ctx, label, (x0 + x1) / 2, y - 52, col, a, 24)

def draw_forces(ctx, t, st):
    (ex, ey), head, tip, d = nail_pts(t)
    L = 230
    # push along the nail, drawn from the head forward (beside the shank, offset up-right)
    ox, oy = AY * 44, -AX * 44               # perpendicular offset (up-right of the nail)
    if st['push'] > 0:
        x0, y0 = head[0] + ox - AX * 40, head[1] + oy - AY * 40
        straight_arrow(ctx, x0, y0, x0 + AX * L, y0 + AY * L, PUSHC, st['push'], lw=13, head=22)
        if st['push_tag'] > 0: tag(ctx, "PUSH = ALONG THE NAIL", 300, 830, PUSHC, st['push_tag'], 26)
    # components at the tip region: DOWN (+y) and SIDEWAYS (+x)
    cx, cy = ex + 10, ey - 150
    if st['down'] > 0:
        straight_arrow(ctx, tip[0] + 34, tip[1] - 110, tip[0] + 34, tip[1] + 50, DOWNC, st['down'], lw=12, head=20)
    if st['side'] > 0:
        sx = stud_x(t)
        straight_arrow(ctx, sx + 20, 860, sx + 20 + 190, 860, SIDEC, st['side'], lw=13, head=22)

def draw_grip(ctx, t, st):
    a = st['grip']
    if a <= 0: return
    (ex, ey), head, tip, d = nail_pts(t)
    # wood fibres hugging the shank inside the stud (short ticks on both sides)
    for k in range(5):
        u = 10 + k * 24
        px, py = ex + AX * u, ey + AY * u
        nx, ny = -AY, AX
        for s in (1, -1):
            ctx.move_to(px + nx * s * 9, py + ny * s * 9)
            ctx.line_to(px + nx * s * 26 + AX * 10, py + ny * s * 26 + AY * 10)
        setc(ctx, RED, a); ctx.set_line_width(4); ctx.stroke()

def draw_mark(ctx, t, st):
    a = st['mark']
    if a <= 0: return
    # pencil line on the plate's front face + the framer's "X" on the stud's side of the line
    ctx.move_to(X_MARK, PLATE_Y0 + 4); ctx.line_to(X_MARK, PLATE_Y0 + 64)
    setc(ctx, PENCIL, a); ctx.set_line_width(5); ctx.stroke()
    cx, cy = X_MARK + 75, PLATE_Y0 + 36
    for s in (1, -1):
        ctx.move_to(cx - 22, cy - 22 * s); ctx.line_to(cx + 22, cy + 22 * s)
    setc(ctx, PENCIL, a); ctx.set_line_width(4); ctx.stroke()

def draw_all(ctx, t, st):
    draw_plate(ctx, st)
    draw_mark(ctx, t, st)
    draw_board(ctx, FIX_X0, 4.1, WOOD)          # fixed neighbour board (already nailed)
    sx = stud_x(t)
    draw_board(ctx, sx, 2.2)                    # the stud being toenailed
    draw_nail(ctx, t, st)
    draw_grip(ctx, t, st)
    draw_hammer(ctx, t, st)
    # gap between the stud and the fixed board
    gap_dim(ctx, sx + STUD_W, FIX_X0, 680, st['gapdim'])
    draw_forces(ctx, t, st)
    # highlights + tags
    (ex, ey), head, tip, d = nail_pts(t)
    highlight(ctx, tip[0] - 20, PLATE_Y0 + 60, 120, 80, DOWNC, st['h_down'], t)
    highlight(ctx, sx + STUD_W / 2, 860, 150, 90, SIDEC, st['h_side'], t)
    highlight(ctx, ex + 50, ey + 40, 95, 80, RED, st['h_grip'], t)
    tag(ctx, "1 · DOWN", tip[0] + 150, PLATE_Y0 + 70, DOWNC, st['l_down'])
    tag(ctx, "2 · SIDEWAYS", sx + 120, 770, SIDEC, st['l_side'])
    tag(ctx, "3 · GRIPPED BY THE STUD", 560, 1380, RED, st['l_grip'], 26)
    if st['offset'] > 0:
        gap_dim(ctx, sx, X_MARK, PLATE_Y0 + 100, st['offset'], "3 mm · 1/8 in", RED)
        tag(ctx, "PENCIL MARK", X_MARK - 20, 1360, PENCIL, st['offset'], 26)
    if st['onmark'] > 0:
        tag(ctx, "ON THE MARK · GAP SHUT", 560, 480, GREEN, st['onmark'], 28)

# ---------------------------------------------------------------- state machine
def state(t):
    st = {}
    st['hammer'] = hammer_on(t)
    st['gapdim'] = max(win(t, 0.0, B(2), 0.3), win(t, B(10), B(11) + 0.2, 0.3)) * (1 if stud_x(t) < X_MARK - 1 else 0)
    st['push'] = bw(t, 2, 4) + bw(t, 11, 12)
    st['push_tag'] = bw(t, 2, 3)
    st['down'] = bw(t, 5, 8) + win(t, B(11) + 0.6, B(12), 0.3)
    st['side'] = bw(t, 6, 8) + win(t, B(11) + 1.2, B(12), 0.3)
    st['grip'] = bw(t, 7, 8)
    st['h_down'] = bw(t, 5)
    st['h_side'] = bw(t, 6)
    st['h_grip'] = bw(t, 7)
    st['l_down'] = bw(t, 5, 8) + win(t, B(11) + 0.6, B(12), 0.3)
    st['l_side'] = bw(t, 6, 8) + win(t, B(11) + 1.2, B(12), 0.3)
    st['l_grip'] = bw(t, 7)
    st['mark'] = ease((t - B(9) - 0.3) / 0.6)
    st['offset'] = win(t, B(9) + 0.9, B(10) + 0.4, 0.3)
    st['onmark'] = win(t, B(10) + 4.1, B(11), 0.3)
    return st

OVER = (540, 900, 1.0)
CAMKEYS = [(0, *OVER),
           (B(2), 470, 950, 1.3),      # the nail and its push
           (B(4), *OVER),
           (B(5), 470, 1010, 1.3),     # down into the plate / sideways / grip
           (B(8), *OVER)]
def CAM(t): return cam_track(CAMKEYS, t)
ANCHOR = (540, 1500)

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

# ---------------------------------------------------------------- HUD: straight-nail inset (beat 3), screen space
def mini_scene(ctx, cx, top, ang_deg, a, sideways):
    """little stud-on-plate with a nail at ang_deg below horizontal (90 = straight down)."""
    ctx.rectangle(cx - 150, top + 230, 300, 60); fill_stroke(ctx, WOOD, lw=4, alpha=a)
    ctx.rectangle(cx - 40, top + 30, 80, 200); fill_stroke(ctx, WOOD_L, lw=4, alpha=a)
    an = math.radians(ang_deg); ax, ay = math.cos(an), math.sin(an)
    if ang_deg >= 89:
        hx, hy = cx, top + 30 - 70
    else:
        hx, hy = cx - 40 - 70 * ax, top + 190 - 70 * ay
    ctx.move_to(hx, hy); ctx.line_to(hx + 190 * ax, hy + 190 * ay)
    setc(ctx, STEEL_D, a); ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    return hx, hy, ax, ay

def draw_hud(ctx, t, E):
    a = bw(t, 3, 4)
    if a <= 0: return
    x0, y0, w, h = 620, 200, 400, 470
    rrect(ctx, x0, y0, w, h, 22); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, CARD_B, a); ctx.set_line_width(4); ctx.stroke()
    cx = x0 + w / 2
    hx, hy, ax, ay = mini_scene(ctx, cx, y0 + 90, 90, a, False)
    p = ease((t - B(3) - 0.5) / 0.8)
    straight_arrow(ctx, cx + 70, y0 + 60, cx + 70, y0 + 60 + 200 * p, PUSHC, a, lw=11, head=18)
    text_c(ctx, "ALL DOWN", cx, y0 + 440, 30, PUSHC, True, 2, a)

# ---------------------------------------------------------------- cards
def card_split(ctx, t, lt, a):
    card_frame(ctx, "ONE PUSH, TWO PARTS", a, "DOWN  +  SIDEWAYS", INK)
    p = ease((lt - 0.5) / 1.0)
    ox, oy, L = 330, 270, 300
    tx, ty = ox + L * AX, oy + L * AY            # push vector: down-right (y down)
    # sideways part (+x) then down part (+y): the triangle closes on the push arrow
    straight_arrow(ctx, ox, oy, tx, ty, PUSHC, a, lw=12, head=20)
    text_c(ctx, "PUSH", ox - 60, oy + 20, 28, PUSHC, True, 2, a)
    if p > 0:
        straight_arrow(ctx, ox, oy, ox + (tx - ox) * p, oy, SIDEC, a * p, lw=11, head=18)
        text_c(ctx, "SIDEWAYS", ox + (tx - ox) / 2, oy - 18, 26, hexc('#a8740f'), True, 2, a * p)
        straight_arrow(ctx, tx, oy, tx, oy + (ty - oy) * p, DOWNC, a * p, lw=11, head=18)
        text_c(ctx, "DOWN", tx + 85, (oy + ty) / 2 + 10, 28, DOWNC, True, 2, a * p)
    # little nail icon on the right
    ctx.move_to(720, 300); ctx.line_to(720 + 150 * AX, 300 + 150 * AY)
    setc(ctx, STEEL_D, a); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def card_angle(ctx, t, lt, a):
    card_frame(ctx, "AT 45°", a, "EQUAL PARTS: SINK + SLIDE", GREEN)
    p = ease((lt - 0.4) / 1.0)
    ox, oy, L = 380, 270, 300
    tx, ty = ox + L * AX, oy + L * AY
    # horizontal reference + 45° arc (angle measured DOWN from horizontal, y down)
    ctx.move_to(ox, oy); ctx.line_to(ox + 330, oy); ctx.set_dash([10, 8]); setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    ctx.new_path(); ctx.arc(ox, oy, 110, 0, ANG * p); setc(ctx, ORANGE, a); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "45°", ox + 150, oy + 70, 32, ORANGE, True, 0, a * p)
    straight_arrow(ctx, ox, oy, tx, ty, PUSHC, a, lw=11, head=18)
    q = ease((lt - 1.2) / 0.8)
    straight_arrow(ctx, ox, oy + 2, ox + (tx - ox) * q, oy + 2, SIDEC, a * q, lw=10, head=16)
    straight_arrow(ctx, tx, oy, tx, oy + (ty - oy) * q, DOWNC, a * q, lw=10, head=16)
    if q > 0.9:
        # equal-length ticks on both parts
        for (x, y, vert) in ((ox + (tx - ox) / 2, oy + 2, False), (tx, (oy + ty) / 2, True)):
            for k in (-6, 6):
                if vert: ctx.move_to(x - 14, y + k); ctx.line_to(x + 14, y + k)
                else: ctx.move_to(x + k, y - 14); ctx.line_to(x + k, y + 14)
            setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
        text_c(ctx, "SAME LENGTH", 850, 420, 26, INK, True, 1.5, a)

CARDS = {'split': card_split, 'angle': card_angle}

def draw_set(ctx):
    pass

# SFX: 'pop' = pencil tick sample (tags, pencil mark). Hammer blows stay silent (no real hammer sample chosen).
SFX = [(B(2) + 0.3, 'pop'), (B(5) + 0.2, 'pop'), (B(6) + 0.2, 'pop'), (B(7) + 0.2, 'pop'),
       (B(9) + 0.3, 'pop'), (B(9) + 1.0, 'pop'), (B(10) + 4.1, 'pop'), (B(11) + 0.2, 'pop')]
