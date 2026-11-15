"""Cogwise episode: This bottle leak fix shouldn't hold — but it does.
One idea: a thin cable tie pulled tight around a small pipe squeezes it far harder than the water pushes out.
Hoop formula: squeeze p = T / (r * w). T ~ 100 N (about 10 kg pull, estimate), r = 11 mm (22 mm pipe),
w = 4.8 mm (standard tie) -> p ~ 1.9 MPa ~ 19 bar (275 psi), vs tap water ~ 3 bar (43 psi): ~6 to 1.

VIEWS (screen coordinates, y grows DOWN):
  - beats 1-2: SIDE view of a horizontal pipe; the pinhole is on TOP (smaller y); the jet goes UP (-y).
    The bottle strip covers the hole, two ties close over the strip. Squeeze arrows: on the TOP of a tie they
    point DOWN (+y, toward the pipe axis); on the BOTTOM they point UP (-y). Water push at the hole points UP.
  - beat 3 on: END-ON cross-section, centre C. Layers from the centre outward:
    water -> copper wall -> bottle strip -> cable tie. Hole at the top of the wall (angle -90 deg on screen).
    Water push = radial OUTWARD (blue, arrows point away from C). Tie squeeze = radial INWARD (red, toward C).
    Tie head (locking box) on the right (angle 0); the free tail leaves it going DOWN, the pull arrow points DOWN
    (away from the head), which tightens the loop.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="bottle-leak-fix",
    title="This bottle leak fix shouldn't hold — but it does 🔧 #Shorts",
    description=("A strip of plastic bottle and two cable ties against a leaking pipe. Why it holds.\n\n"
                 "#Shorts #howthingswork #plumbing #diy #cogwise"),
    hashtags=["Shorts", "howthingswork", "plumbing", "diy", "physics", "cogwise"],
    sources=[
        "https://www.hunker.com/12590646/what-is-the-normal-water-pressure-for-a-house",
        "https://plumbnation.co.uk/blog/the-complete-guide-to-water-pressure",
        "https://www.awcwire.com/cable-ties/standard-cable-ties/standard-cable-ties-50-lbs",
        "https://securecableties.com/nylon-cable-tie-strengths",
        "https://www.eng-tips.com/threads/clamp-pressure.251003",
        "https://blog.normagroup.com/en/why-is-clamp-load-so-important/",
    ],
)

BEATS = [
    dict(dur=5.4, title="HOLD?", caption="A strip of plastic bottle and two cable ties. This leak fix shouldn't hold."),
    dict(dur=5.6, title="THE SECRET", caption="The secret: those ties squeeze the pipe harder than the water pushes out."),
    dict(dur=5.2, title="THE PUSH", caption="Inside, tap water pushes outward at about three bar, forty-three psi."),
    dict(dur=6.0, title="1 · THE PATCH", caption="First, the bottle strip wraps the pipe and covers the hole like a soft gasket."),
    dict(dur=6.2, title="2 · THE TIES", caption="Then each tie is pulled tight, about ten kilograms of pull, twenty-two pounds."),
    dict(dur=6.4, title="THE CURVE", caption="Wrapped around a curve, that pull turns into a squeeze pointing inward, all the way round."),
    dict(dur=5.0, title=None, caption="The tighter the curve, the harder the same pull presses in.", card='curve'),
    dict(dur=4.8, title="3 · THIN BAND", caption="And a thin tie puts all that force on a narrow strip."),
    dict(dur=6.6, title="THE SQUEEZE", caption="On a twenty-two millimetre pipe, that's about nineteen bar, two hundred seventy-five psi."),
    dict(dur=4.0, title="SIX TO ONE", caption="Six times harder than the water pushing out."),
    dict(dur=5.0, title=None, caption="So the plastic stays pinned shut, and the water never lifts it.", card='pinned'),
    dict(dur=4.4, title="SQUEEZE > PUSH", caption="Leak fix: the squeeze beats the push, six to one."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette
COPPER = hexc('#d9894a'); COPPER_D = hexc('#a35d2a')
WATER = hexc('#8fcfc8'); WATER_D = hexc('#1f8a8a')
PET = hexc('#dfeef2'); PET_E = hexc('#8fb3bd')
TIE = hexc('#3b3842'); TIE_L = hexc('#5a5560')
BLUE = hexc('#2f6fb3')

# ---------------------------------------------------------------- geometry
# side view (beats 1-2)
SY = 880; SR = 78; SX0, SX1 = 70, 1010           # pipe axis y, outer half height, x span
HOLE_X = 540
STRIP_X0, STRIP_X1 = 430, 650
TIES_X = (478, 602); TIE_W = 20
# end-on section (beat 3 on)
CX, CY = 540, 900
R_IN, R_OUT = 200, 226          # copper wall
R_PET = 244                     # bottle strip outer radius
R_TIE = 266                     # tie outer radius
HOLE_A = -math.pi / 2           # hole at the top (screen: y up = negative)
HOLE_HALF = 0.07                # half angle of the hole

def state(t):
    s = {}
    # intro (side view)
    s['jet'] = 1 - clamp((t - 0.9) / 0.25)                       # jet sprays until the strip covers it
    s['strip_side'] = ease(clamp((t - 0.35) / 0.6))
    s['tie1'] = ease(clamp((t - 1.0) / 0.25)); s['tie2'] = ease(clamp((t - 1.35) / 0.25))
    s['secret'] = bw(t, 1)
    s['turn'] = clamp((t - B(2)) / 0.8)                          # 0 side view -> 1 section
    # section
    s['push'] = clamp(ease((t - B(2) - 0.4) / 0.8))
    s['squirt'] = win(t, B(2) + 0.6, B(3) + 0.9, 0.3)
    s['wrap'] = ease(clamp((t - B(3) - 0.3) / 1.8))             # strip angle fraction
    s['patch_hi'] = bw(t, 3)
    s['tie_wrap'] = ease(clamp((t - B(4) - 0.2) / 1.6))
    s['pull'] = win(t, B(4) + 1.6, B(5) + 0.2, 0.3)
    s['tie_hi'] = bw(t, 4)
    s['squeeze'] = clamp(ease((t - B(5) - 0.4) / 1.6))           # inward arrows grow around
    s['thin'] = bw(t, 7)
    s['six'] = bw(t, 9)
    s['recap'] = bw(t, 11)
    return s

# ---------------------------------------------------------------- side view
def side_view(ctx, t, s):
    k = 1 - ease(s['turn'])
    if k <= 0.01: return
    ctx.push_group()
    # wall bracket hints
    for x in (150, 930):
        rrect(ctx, x - 22, SY - SR - 40, 44, 2 * SR + 80, 8); fill_stroke(ctx, FILL3, lw=4)
    # pipe
    ctx.rectangle(SX0, SY - SR, SX1 - SX0, 2 * SR)
    g = cairo.LinearGradient(0, SY - SR, 0, SY + SR)
    g.add_color_stop_rgb(0, *COPPER_D[:3]); g.add_color_stop_rgb(0.3, *COPPER[:3]); g.add_color_stop_rgb(1, *COPPER_D[:3])
    ctx.set_source(g); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.move_to(SX0 + 10, SY - SR + 22); ctx.line_to(SX1 - 10, SY - SR + 22); setc(ctx, WHITE, 0.35); ctx.set_line_width(8); ctx.stroke()
    # hole on top
    ctx.arc(HOLE_X, SY - SR + 3, 7, math.pi, 2 * math.pi); setc(ctx, INK); ctx.fill()
    # jet (goes UP)
    ja = s['jet']
    if ja > 0:
        rnd = random.Random(3)
        for i in range(26):
            u = ((t * 1.8) + i / 26) % 1
            x = HOLE_X + rnd.uniform(-1, 1) * 40 * u
            y = SY - SR - 10 - u * 420
            ctx.arc(x, y, 9 - 4 * u, 0, 2 * math.pi); setc(ctx, WATER_D, ja * (1 - u * 0.6)); ctx.fill()
        ctx.move_to(HOLE_X - 5, SY - SR); ctx.line_to(HOLE_X, SY - SR - 170); ctx.line_to(HOLE_X + 5, SY - SR)
        setc(ctx, WATER_D, ja); ctx.fill()
    # bottle strip: wraps from the top down
    sa = s['strip_side']
    if sa > 0:
        h = 2 * (SR + 10) * sa
        ctx.rectangle(STRIP_X0, SY - SR - 10, STRIP_X1 - STRIP_X0, h)
        setc(ctx, PET, 0.92); ctx.fill_preserve(); setc(ctx, PET_E); ctx.set_line_width(4); ctx.stroke()
        for x in range(STRIP_X0 + 30, STRIP_X1, 50):
            ctx.move_to(x, SY - SR - 6); ctx.line_to(x - 18, SY - SR - 6 + h * 0.9)
            setc(ctx, WHITE, 0.6); ctx.set_line_width(4); ctx.stroke()
    # ties (snap on)
    for x, a in zip(TIES_X, (s['tie1'], s['tie2'])):
        if a <= 0: continue
        sc = 1 + 0.25 * math.sin(a * math.pi)
        hh = (SR + 18) * sc
        rrect(ctx, x - TIE_W / 2, SY - hh, TIE_W, 2 * hh, 6); fill_stroke(ctx, TIE, lw=3, alpha=a)
        rrect(ctx, x - 20, SY - hh - 26, 40, 30, 5); fill_stroke(ctx, TIE_L, lw=3, alpha=a)  # locking head on top
    ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
    # the secret: squeeze (red, toward the axis) beats push (blue, up through the hole)
    a = s['secret'] * k
    if a > 0:
        for x in TIES_X:
            straight_arrow(ctx, x, SY - SR - 200, x, SY - SR - 50, RED, a, lw=12, head=22)   # top: DOWN
            straight_arrow(ctx, x, SY + SR + 170, x, SY + SR + 38, RED, a, lw=12, head=22)   # bottom: UP
        straight_arrow(ctx, HOLE_X, SY - SR + 30, HOLE_X, SY - SR - 30, BLUE, a, lw=6, head=12)  # water: UP
        tag(ctx, "SQUEEZE", 540, SY + SR + 230, RED, a, 30)
        tag(ctx, "PUSH", 540, SY - SR - 250, BLUE, a, 26)

# ---------------------------------------------------------------- section
def polar(r, a): return CX + r * math.cos(a), CY + r * math.sin(a)

def section(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.45) / 0.55))
    if a <= 0: return
    ctx.push_group()
    # water
    ctx.arc(CX, CY, R_IN, 0, 2 * math.pi); setc(ctx, WATER); ctx.fill()
    rnd = random.Random(5)
    for i in range(40):
        r = math.sqrt(rnd.random()) * (R_IN - 16); an = rnd.uniform(0, 2 * math.pi) + t * 0.15
        ctx.arc(CX + r * math.cos(an), CY + r * math.sin(an), 3, 0, 2 * math.pi); setc(ctx, WATER_D, 0.35); ctx.fill()
    # copper wall with the hole at the top
    ctx.new_path()
    ctx.arc(CX, CY, R_OUT, HOLE_A + HOLE_HALF, HOLE_A - HOLE_HALF + 2 * math.pi)
    ctx.arc_negative(CX, CY, R_IN, HOLE_A - HOLE_HALF * 1.1 + 2 * math.pi, HOLE_A + HOLE_HALF * 1.1)
    ctx.close_path(); fill_stroke(ctx, COPPER, lw=4)
    # water inside the hole
    ctx.new_path()
    ctx.arc(CX, CY, R_OUT, HOLE_A - HOLE_HALF, HOLE_A + HOLE_HALF)
    ctx.arc_negative(CX, CY, R_IN, HOLE_A + HOLE_HALF * 1.1, HOLE_A - HOLE_HALF * 1.1)
    ctx.close_path(); setc(ctx, WATER); ctx.fill()
    # bottle strip (wraps clockwise on screen, starting just before the hole so it covers it first)
    w = s['wrap']
    if w > 0:
        a0 = HOLE_A - 0.5; a1 = a0 + w * (2 * math.pi + 0.35)
        ctx.new_path(); ctx.arc(CX, CY, R_PET, a0, a1); ctx.arc_negative(CX, CY, R_OUT + 1, a1, a0); ctx.close_path()
        fill_stroke(ctx, PET, stroke=PET_E, lw=3)
    # cable tie
    tw = s['tie_wrap']
    if tw > 0:
        a0 = 0.12; a1 = a0 + tw * (2 * math.pi - 0.24)
        ctx.new_path(); ctx.arc(CX, CY, R_TIE, a0, a1); ctx.arc_negative(CX, CY, R_PET + 1, a1, a0); ctx.close_path()
        fill_stroke(ctx, TIE, lw=3)
        if tw > 0.98:
            # locking head on the right (angle 0) + free tail going DOWN
            hx = CX + R_PET - 2
            rrect(ctx, hx, CY - 34, 50, 68, 8); fill_stroke(ctx, TIE_L, lw=3)
            ctx.rectangle(hx + 14, CY + 34, 22, 150); fill_stroke(ctx, TIE, lw=3)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

    # water push: radial OUTWARD (blue)
    pa = s['push'] * a * (1 - 0.45 * s['squeeze'])
    if pa > 0:
        for i in range(8):
            an = i * math.pi / 4 + math.pi / 8
            x0, y0 = polar(50, an); x1, y1 = polar(150, an)
            straight_arrow(ctx, x0, y0, x1, y1, BLUE, pa, lw=7, head=13)
    # squirt through the hole before the patch (UP)
    sq = s['squirt'] * a * (1 - clamp(w * 4))
    if sq > 0:
        hx, hy = polar(R_OUT, HOLE_A)
        rnd = random.Random(8)
        for i in range(18):
            u = ((t * 1.6) + i / 18) % 1
            ctx.arc(hx + rnd.uniform(-1, 1) * 30 * u, hy - 10 - u * 240, 8 - 3 * u, 0, 2 * math.pi)
            setc(ctx, WATER_D, sq * (1 - 0.6 * u)); ctx.fill()
    # pull on the tie tail: DOWN (away from the head)
    pl = s['pull'] * a
    if pl > 0:
        x = CX + R_PET + 23; y0 = CY + 190 + 8 * math.sin(t * 6)
        straight_arrow(ctx, x, y0, x, y0 + 130, RED, pl, lw=10, head=20)
        tag(ctx, "PULL ≈ 10 kg · 22 lb", x - 40, y0 + 190, RED, pl, 26)
    # squeeze: radial INWARD (red), growing around the ring
    q = s['squeeze'] * a
    if q > 0:
        n = 16; big = 1 + 0.35 * s['six']
        for i in range(n):
            if i / n > q * 1.02: break
            an = HOLE_A + i * 2 * math.pi / n
            x0, y0 = polar(R_TIE + 110 * big, an); x1, y1 = polar(R_TIE + 12, an)
            straight_arrow(ctx, x0, y0, x1, y1, RED, a, lw=8 * big, head=15 * big)

def overlays(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.5) / 0.5))
    if a <= 0: return
    ap = s['push'] * (1 - s['patch_hi']) * (1 - s['tie_hi']) * (1 - s['squeeze'])
    if ap > 0:
        tag(ctx, "3 bar · 43 psi", CX, CY + 40, BLUE, ap * a, 28)
        tag(ctx, "HOLE", CX + 150, CY - R_OUT - 90, INK, ap * a * s['squirt'], 24)
    if s['patch_hi'] > 0:
        highlight(ctx, *polar(R_PET - 8, HOLE_A), 90, 40, MUSTARD, s['patch_hi'] * a, t)
        tag(ctx, "BOTTLE STRIP", CX - 250, CY - R_TIE - 70, INK, s['patch_hi'] * a, 26)
    if s['tie_hi'] > 0:
        tag(ctx, "CABLE TIE", CX - 270, CY + R_TIE + 70, INK, s['tie_hi'] * a, 26)
    sq = bw(t, 5)
    if sq > 0:
        tag(ctx, "SQUEEZE · ALL THE WAY ROUND", CX, CY + R_TIE + 175, RED, sq * a, 26)
    ra = s['recap']
    if ra > 0:
        tag(ctx, "SQUEEZE ≈ 19 bar", CX, CY + R_TIE + 175, RED, ra * a, 30)
        tag(ctx, "PUSH 3 bar", CX, CY + 40, BLUE, ra * a, 26)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    side_view(ctx, t, s)
    section(ctx, t, s)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def thin_panel(ctx, t, a):
    """Side close-up: the force sits under a narrow band only."""
    x, y, w, h = 60, 175, 960, 300
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    py, pr = 315, 40
    ctx.rectangle(140, py - pr, 800, 2 * pr); fill_stroke(ctx, COPPER, lw=4, alpha=a)
    ctx.rectangle(400, py - pr - 10, 280, 2 * pr + 20); fill_stroke(ctx, PET, stroke=PET_E, lw=3, alpha=a)
    bx = 540
    ctx.rectangle(bx - 10, py - pr - 22, 20, 2 * pr + 44); fill_stroke(ctx, TIE, lw=3, alpha=a)
    for sy in (-1, 1):
        y0 = py + sy * (pr + 78); y1 = py + sy * (pr + 26)
        straight_arrow(ctx, bx, y0, bx, y1, RED, a, lw=10, head=18)
    # band width dimension
    for sx in (-1, 1):
        ctx.move_to(bx + sx * 12, py - pr - 34); ctx.line_to(bx + sx * 70, py - pr - 34)
    setc(ctx, INK, a); ctx.set_line_width(2); ctx.stroke()
    text_c(ctx, "≈ 5 mm · 0.2 in", 770, 250, 30, RED, True, 1, a)
    text_c(ctx, "ALL THE FORCE, ONE NARROW BAND", 540, 462, 26, INK, True, 1.5, a)

def draw_hud(ctx, t, E):
    a = win(t, B(7) + 0.3, B(8), 0.3)
    if a > 0: thin_panel(ctx, t, a)
    a = win(t, B(8) + 0.5, B(10), 0.3)
    if a > 0:
        hud(ctx, "TIE SQUEEZE", "≈ 19 bar", "275 psi", a, RED, x=40, y=180, w=480)
        hud(ctx, "WATER PUSH", "3 bar", "43 psi", a, TEAL, x=560, y=180, w=480)
    a = win(t, B(9) + 0.2, B(10), 0.3)
    if a > 0:
        # 6 red blocks vs 1 blue block
        for i in range(6):
            k = ease(clamp((t - B(9) - 0.3 - i * 0.12) / 0.2))
            rrect(ctx, 60 + i * 76, 360, 64, 64, 8); fill_stroke(ctx, RED, lw=3, alpha=a * k)
        rrect(ctx, 600, 360, 64, 64, 8); fill_stroke(ctx, BLUE, lw=3, alpha=a)
        text_c(ctx, "6 : 1", 860, 410, 60, INK, True, 2, a)

SFX = [(0.4, 'pop'), (1.0, 'click'), (1.35, 'click'), (B(1) + 0.3, 'pop'), (B(2) + 0.4, 'pop'),
       (B(3) + 0.3, 'pop'), (B(4) + 0.3, 'pop'), (B(4) + 1.6, 'click'), (B(5) + 0.4, 'pop'),
       (B(7) + 0.3, 'pop'), (B(8) + 0.5, 'pop'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def _ring(ctx, cx, cy, r, a, t, arrow_len):
    ctx.arc(cx, cy, r, 0, 2 * math.pi); fill_stroke(ctx, COPPER, lw=4, alpha=a)
    ctx.arc(cx, cy, r - 12, 0, 2 * math.pi); setc(ctx, WATER, a); ctx.fill()
    ctx.arc(cx, cy, r + 8, 0, 2 * math.pi); setc(ctx, TIE, a); ctx.set_line_width(8); ctx.stroke()
    for i in range(8):
        an = i * math.pi / 4
        x0, y0 = cx + (r + 14 + arrow_len) * math.cos(an), cy + (r + 14 + arrow_len) * math.sin(an)
        x1, y1 = cx + (r + 12) * math.cos(an), cy + (r + 12) * math.sin(an)
        straight_arrow(ctx, x0, y0, x1, y1, RED, a, lw=4 + arrow_len / 14, head=8 + arrow_len / 8)

def card_curve(ctx, t, lt, a):
    card_frame(ctx, "SAME PULL, TWO PIPES", a, "SMALLER PIPE = HARDER SQUEEZE", RED)
    _ring(ctx, 330, 390, 95, a, t, 22)     # big pipe: short arrows
    _ring(ctx, 760, 390, 48, a, t, 62)     # small pipe: long arrows

def card_pinned(ctx, t, lt, a):
    card_frame(ctx, "AT THE HOLE", a, "SQUEEZE PINS THE STRIP SHUT", RED)
    # pipe wall (bottom), hole in the middle, strip on top, tie on top of strip
    ctx.rectangle(150, 450, 340, 60); fill_stroke(ctx, COPPER, lw=4, alpha=a)
    ctx.rectangle(590, 450, 340, 60); fill_stroke(ctx, COPPER, lw=4, alpha=a)
    ctx.rectangle(490, 450, 100, 60); setc(ctx, WATER, a); ctx.fill()
    ctx.rectangle(150, 510, 780, 22); setc(ctx, WATER, a); ctx.fill()
    ctx.rectangle(200, 426, 680, 24); fill_stroke(ctx, PET, stroke=PET_E, lw=3, alpha=a)
    ctx.rectangle(260, 400, 560, 26); fill_stroke(ctx, TIE, lw=3, alpha=a)
    # water pushes UP at the hole (small), tie squeezes DOWN (big)
    straight_arrow(ctx, 540, 528, 540, 458, BLUE, a, lw=6, head=12)
    for x in (380, 540, 700):
        straight_arrow(ctx, x, 262, x, 392, RED, a, lw=12, head=20)

CARDS = {'curve': card_curve, 'pinned': card_pinned}
