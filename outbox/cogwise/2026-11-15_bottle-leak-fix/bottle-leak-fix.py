"""Cogwise episode: This pipe still has a hole. So why did the water stop?  (v2, mystery cut)
One idea: a thin cable tie pulled tight around a small pipe squeezes it ~6x harder than the water pushes out,
so the hole stays OPEN but the plastic is pinned shut over it.
Hoop formula (not spoken): p = T / (r * w); T ~ 100 N, r = 11 mm, w = 4.8 mm -> ~19 bar vs ~3 bar tap water.

VIEWS (screen coordinates, y grows DOWN):
  - beat 1 and beat 12: SIDE view of a horizontal pipe; the pinhole is on TOP (smaller y); the jet goes UP (-y).
    The bottle strip (translucent) covers the hole, two ties close over it; the hole stays visible under it.
  - beats 2-11: END-ON cross-section, centre C. Layers from the centre outward:
    water -> copper wall -> bottle strip -> cable tie. Hole at the top of the wall (angle -90 deg on screen).
    Water push = radial OUTWARD (blue, arrows point away from C). Tie squeeze = radial INWARD (red, toward C).
    Tension = ALONG the band (tangential double arrows). Tie head on the right (angle 0); the free tail leaves it
    going DOWN, the pull arrow points DOWN (away from the head), which tightens the loop.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="bottle-leak-fix",
    title="This pipe still has a hole. So why did the water stop? 🔧 #Shorts",
    description=("The hole is still open under the plastic. So what is holding the water back?\n\n"
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
    dict(dur=5.2, title="HOLE?", caption="This pipe still has a hole. So why did the water stop?"),
    dict(dur=5.7, title="NOT PLUGGED", caption="The hole isn't plugged. Something is pressing on it harder than the water."),
    dict(dur=4.8, title="THE PUSH", caption="Inside, the water pushes outward, trying to lift the plastic away."),
    dict(dur=5.7, title="GLUE?", caption="Glue? There's none. Is the plastic melted on? No, it peels right off."),
    dict(dur=5.7, title="CLUE 1 · THE TIES", caption="Clue one: the ties. Pulled tight, a tie only pulls along its length."),
    dict(dur=5.7, title="THE WRAP", caption="But wrapped around a pipe, that pull bends inward, pressing from every side."),
    dict(dur=6.1, title="CLUE 2 · SMALL PIPE", caption="Clue two: the pipe is small. The tighter the curve, the harder it presses."),
    dict(dur=5.2, title=None, caption="The same tie barely grips a tree, but crushes a thin pipe.", card='tree'),
    dict(dur=6.1, title="CLUE 3 · THIN BAND", caption="Clue three: the tie is thin, so the force lands on a narrow strip."),
    dict(dur=6.1, title="SIX TO ONE", caption="The answer: on this pipe, the ties squeeze six times harder than water pushes."),
    dict(dur=5.2, title=None, caption="So the hole stays open, but the plastic stays pinned against it.", card='pinned'),
    dict(dur=4.8, title="SQUEEZE > PUSH", caption="The water is still there. It just can't lift the lid."),
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
    # beat 1 (side view): jet sprays, strip + ties go on, jet stops by ~1.2 s, the hole is still visible
    s['jet'] = 1 - clamp((t - 1.0) / 0.25)
    s['strip_side'] = ease(clamp((t - 0.25) / 0.55))
    s['tie1'] = ease(clamp((t - 0.75) / 0.25)); s['tie2'] = ease(clamp((t - 1.0) / 0.25))
    s['loupe'] = win(t, 1.4, B(1) + 0.3, 0.45)   # variante « loupe » (étape 3, choix de Guillaume)
    # turn to the section (beat 2), and back to the side view (beat 12)
    s['turn'] = clamp((t - B(1) - 0.2) / 0.8) * (1 - clamp((t - B(11) - 0.1) / 0.8))
    s['qmark'] = win(t, B(1) + 1.0, B(2) + 0.2, 0.3)
    s['push'] = clamp(ease((t - B(2) - 0.3) / 0.8))
    s['tension'] = bw(t, 4)
    s['pull'] = win(t, B(4) + 0.6, B(5) + 0.3, 0.3)
    s['tie_hi'] = bw(t, 4)
    s['squeeze'] = clamp(ease((t - B(5) - 0.3) / 1.6))
    s['six'] = ease(clamp((t - B(9) - 0.3) / 0.6))
    s['recap'] = win(t, B(11) + 0.9, B(12) + 2, 0.3)
    return s

# ---------------------------------------------------------------- side view
def side_view(ctx, t, s):
    k = 1 - ease(s['turn'])
    if k <= 0.01: return
    ctx.push_group()
    _side_body(ctx, t, s)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
    # beat 1 (variante « loupe ») : a magnifying glass zooms on the hole — still open under the clear plastic
    a = s['loupe'] * k
    if a > 0:
        loupe(ctx, t, s, a)
    # final beat: dry pipe, hole open, water stays in
    a = s['recap'] * k
    if a > 0:
        highlight(ctx, HOLE_X, SY - SR + 2, 46, 34, RED, a, t)
        tag(ctx, "HOLE: OPEN", HOLE_X, SY - SR - 150, RED, a, 28)
        tag(ctx, "WATER: STILL IN", HOLE_X, SY + SR + 120, TEAL, a, 28)

LX, LY, LR, LZ = 540, 520, 165, 3.2     # loupe centre, radius, zoom (hole drawn at the lens centre)
def loupe(ctx, t, s, a):
    g = ease(clamp(a))
    r = LR * (0.35 + 0.65 * g)
    hx, hy = HOLE_X, SY - SR + 2
    # zoom cone: from the hole up to the lens (faint)
    ctx.move_to(hx - 14, hy); ctx.line_to(LX - r * 0.93, LY + r * 0.37)
    ctx.move_to(hx + 14, hy); ctx.line_to(LX + r * 0.93, LY + r * 0.37)
    setc(ctx, INK, 0.35 * a); ctx.set_line_width(3); ctx.set_dash([10, 8]); ctx.stroke(); ctx.set_dash([])
    # handle, up-right (behind the rim)
    ca, sa_ = math.cos(-math.pi / 4), math.sin(-math.pi / 4)
    x0, y0 = LX + ca * (r + 4), LY + sa_ * (r + 4)
    x1, y1 = LX + ca * (r + 150 * g), LY + sa_ * (r + 150 * g)
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); setc(ctx, INK, a); ctx.set_line_width(34); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); setc(ctx, hexc('#7a4a2a'), a); ctx.set_line_width(24); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    # magnified view of the hole (same drawing, scaled around the hole)
    ctx.save()
    ctx.arc(LX, LY, r, 0, 2 * math.pi); ctx.clip()
    ctx.push_group()
    ctx.arc(LX, LY, r, 0, 2 * math.pi); setc(ctx, hexc('#f4ecd8')); ctx.fill()
    ctx.translate(LX, LY); ctx.scale(LZ, LZ); ctx.translate(-hx, -hy)
    _side_body(ctx, t, s)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()
    # glass sheen + rim
    ctx.arc(LX - r * 0.35, LY - r * 0.35, r * 0.35, math.pi * 1.05, math.pi * 1.55)
    setc(ctx, WHITE, 0.55 * a); ctx.set_line_width(7); ctx.stroke()
    ctx.arc(LX, LY, r, 0, 2 * math.pi); setc(ctx, INK, a); ctx.set_line_width(14); ctx.stroke()
    ctx.arc(LX, LY, r - 9, 0, 2 * math.pi); setc(ctx, hexc('#b8b0a0'), a); ctx.set_line_width(4); ctx.stroke()
    # the hole itself, ringed in red inside the lens
    highlight(ctx, LX, LY + 4, 52, 34, RED, a * clamp((g - 0.6) / 0.4), t)
    tag(ctx, "STILL A HOLE", LX - 260, LY + r - 10, RED, a * clamp((g - 0.6) / 0.4), 30)

def _side_body(ctx, t, s):
    for x in (150, 930):          # wall brackets
        rrect(ctx, x - 22, SY - SR - 40, 44, 2 * SR + 80, 8); fill_stroke(ctx, FILL3, lw=4)
    ctx.rectangle(SX0, SY - SR, SX1 - SX0, 2 * SR)
    g = cairo.LinearGradient(0, SY - SR, 0, SY + SR)
    g.add_color_stop_rgb(0, *COPPER_D[:3]); g.add_color_stop_rgb(0.3, *COPPER[:3]); g.add_color_stop_rgb(1, *COPPER_D[:3])
    ctx.set_source(g); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.move_to(SX0 + 10, SY - SR + 22); ctx.line_to(SX1 - 10, SY - SR + 22); setc(ctx, WHITE, 0.35); ctx.set_line_width(8); ctx.stroke()
    # hole on top (always open)
    ctx.arc(HOLE_X, SY - SR + 3, 9, math.pi, 2 * math.pi); setc(ctx, INK); ctx.fill()
    # jet (goes UP) — only at the start of the episode
    ja = s['jet'] if t < B(2) else 0
    if ja > 0:
        rnd = random.Random(3)
        for i in range(26):
            u = ((t * 1.8) + i / 26) % 1
            ctx.arc(HOLE_X + rnd.uniform(-1, 1) * 40 * u, SY - SR - 10 - u * 420, 9 - 4 * u, 0, 2 * math.pi)
            setc(ctx, WATER_D, ja * (1 - u * 0.6)); ctx.fill()
        ctx.move_to(HOLE_X - 5, SY - SR); ctx.line_to(HOLE_X, SY - SR - 170); ctx.line_to(HOLE_X + 5, SY - SR)
        setc(ctx, WATER_D, ja); ctx.fill()
    # translucent bottle strip (wraps from the top down) — the hole shows through it
    sa = s['strip_side'] if t < B(2) else 1
    if sa > 0:
        h = 2 * (SR + 10) * sa
        ctx.rectangle(STRIP_X0, SY - SR - 10, STRIP_X1 - STRIP_X0, h)
        setc(ctx, PET, 0.55); ctx.fill_preserve(); setc(ctx, PET_E); ctx.set_line_width(4); ctx.stroke()
        for x in range(STRIP_X0 + 30, STRIP_X1, 50):
            if abs(x - HOLE_X) < 30: continue
            ctx.move_to(x, SY - SR - 6); ctx.line_to(x - 18, SY - SR - 6 + h * 0.9)
            setc(ctx, WHITE, 0.6); ctx.set_line_width(4); ctx.stroke()
        # the hole shows through the clear plastic
        ctx.arc(HOLE_X, SY - SR + 3, 9, math.pi, 2 * math.pi); setc(ctx, INK, 0.75); ctx.fill()
    for x, a in zip(TIES_X, (s['tie1'], s['tie2']) if t < B(2) else (1, 1)):
        if a <= 0: continue
        sc = 1 + 0.25 * math.sin(a * math.pi)
        hh = (SR + 18) * sc
        rrect(ctx, x - TIE_W / 2, SY - hh, TIE_W, 2 * hh, 6); fill_stroke(ctx, TIE, lw=3, alpha=a)
        rrect(ctx, x - 20, SY - hh - 26, 40, 30, 5); fill_stroke(ctx, TIE_L, lw=3, alpha=a)

# ---------------------------------------------------------------- section
def polar(r, a): return CX + r * math.cos(a), CY + r * math.sin(a)

def tangent_pair(ctx, an, r, a, col=RED):
    """Tension along the band: two arrowheads pulling away from each other along the circle."""
    d = 0.26
    for sgn in (-1, 1):
        a0 = an + sgn * 0.04; a1 = an + sgn * d
        ctx.new_path()
        if sgn > 0: ctx.arc(CX, CY, r, a0, a1)
        else: ctx.arc_negative(CX, CY, r, a0, a1)
        setc(ctx, col, a); ctx.set_line_width(8); ctx.stroke()
        # arrow head at a1, pointing along the tangent (direction of increasing angle * sgn)
        hx, hy = polar(r, a1)
        tx, ty = -math.sin(a1) * sgn, math.cos(a1) * sgn
        nx, ny = -ty, tx
        ctx.move_to(hx + tx * 18, hy + ty * 18); ctx.line_to(hx + nx * 11, hy + ny * 11); ctx.line_to(hx - nx * 11, hy - ny * 11)
        ctx.close_path(); setc(ctx, col, a); ctx.fill()

def section(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.45) / 0.55))
    if a <= 0: return
    ctx.push_group()
    ctx.arc(CX, CY, R_IN, 0, 2 * math.pi); setc(ctx, WATER); ctx.fill()
    rnd = random.Random(5)
    for i in range(40):
        r = math.sqrt(rnd.random()) * (R_IN - 16); an = rnd.uniform(0, 2 * math.pi) + t * 0.15
        ctx.arc(CX + r * math.cos(an), CY + r * math.sin(an), 3, 0, 2 * math.pi); setc(ctx, WATER_D, 0.35); ctx.fill()
    # copper wall with the (open) hole at the top
    ctx.new_path()
    ctx.arc(CX, CY, R_OUT, HOLE_A + HOLE_HALF, HOLE_A - HOLE_HALF + 2 * math.pi)
    ctx.arc_negative(CX, CY, R_IN, HOLE_A - HOLE_HALF * 1.1 + 2 * math.pi, HOLE_A + HOLE_HALF * 1.1)
    ctx.close_path(); fill_stroke(ctx, COPPER, lw=4)
    ctx.new_path()
    ctx.arc(CX, CY, R_OUT, HOLE_A - HOLE_HALF, HOLE_A + HOLE_HALF)
    ctx.arc_negative(CX, CY, R_IN, HOLE_A + HOLE_HALF * 1.1, HOLE_A - HOLE_HALF * 1.1)
    ctx.close_path(); setc(ctx, WATER); ctx.fill()
    # bottle strip, full ring (it lies ON the hole, not in it)
    ctx.new_path(); ctx.arc(CX, CY, R_PET, 0, 2 * math.pi); ctx.arc_negative(CX, CY, R_OUT + 1, 2 * math.pi, 0); ctx.close_path()
    fill_stroke(ctx, PET, stroke=PET_E, lw=3)
    # cable tie, head on the right, tail DOWN
    a0 = 0.12; a1 = 2 * math.pi - 0.12
    ctx.new_path(); ctx.arc(CX, CY, R_TIE, a0, a1); ctx.arc_negative(CX, CY, R_PET + 1, a1, a0); ctx.close_path()
    fill_stroke(ctx, TIE, lw=3)
    hx = CX + R_PET - 2
    rrect(ctx, hx, CY - 34, 50, 68, 8); fill_stroke(ctx, TIE_L, lw=3)
    ctx.rectangle(hx + 14, CY + 34, 22, 150); fill_stroke(ctx, TIE, lw=3)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

    # the "?" : something presses on the strip at the hole
    qa = s['qmark'] * a
    if qa > 0:
        highlight(ctx, *polar(R_OUT - 12, HOLE_A), 40, 30, RED, qa, t)
        text_c(ctx, "?", CX, CY - R_TIE - 60, 120, RED, True, 0, qa)
        tag(ctx, "HOLE: OPEN", CX + 250, CY - R_TIE - 40, INK, qa, 24)
    # water push: radial OUTWARD (blue); at the hole one arrow pushes UP into the strip
    pa = s['push'] * a * (1 - 0.45 * s['squeeze'])
    if pa > 0:
        for i in range(8):
            an = i * math.pi / 4 + math.pi / 8
            x0, y0 = polar(50, an); x1, y1 = polar(150, an)
            straight_arrow(ctx, x0, y0, x1, y1, BLUE, pa, lw=7, head=13)
        x0, y0 = polar(R_IN - 70, HOLE_A); x1, y1 = polar(R_PET - 6, HOLE_A)
        straight_arrow(ctx, x0, y0, x1, y1, BLUE, pa, lw=9, head=17)
    # tension along the band (clue 1)
    ta = s['tension'] * a
    if ta > 0:
        for an in (-2.4, -0.9, 2.2, 1.0):
            tangent_pair(ctx, an, R_TIE + 30, ta)
    pl = s['pull'] * a
    if pl > 0:
        x = CX + R_PET + 23; y0 = CY + 190 + 8 * math.sin(t * 6)
        straight_arrow(ctx, x, y0, x, y0 + 130, RED, pl, lw=10, head=20)
        tag(ctx, "PULL", x + 90, y0 + 70, RED, pl, 28)
    # squeeze: radial INWARD (red), growing around the ring, bigger at "six to one"
    q = s['squeeze'] * a
    if q > 0:
        n = 16; big = 1 + 0.35 * s['six']
        for i in range(n):
            if i / n > q * 1.02: break
            an = HOLE_A + i * 2 * math.pi / n
            if abs(math.cos(an) - 1) < 0.02: continue    # skip the tie head (angle 0)
            x0, y0 = polar(R_TIE + 110 * big, an); x1, y1 = polar(R_TIE + 12, an)
            straight_arrow(ctx, x0, y0, x1, y1, RED, q, lw=8 * big, head=15 * big)

def overlays(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.5) / 0.5))
    if a <= 0: return
    ap = bw(t, 2)
    if ap > 0: tag(ctx, "WATER PUSH", CX, CY + 40, BLUE, ap * a, 28)
    if s['tie_hi'] > 0:
        tag(ctx, "PULLS ALONG ITS LENGTH", CX, CY + R_TIE + 175, RED, s['tie_hi'] * a, 26)
    sq = bw(t, 5)
    if sq > 0:
        tag(ctx, "PRESSES FROM EVERY SIDE", CX, CY + R_TIE + 175, RED, sq * a, 26)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    side_view(ctx, t, s)
    section(ctx, t, s)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=175, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def _cross(ctx, cx, cy, r, a):
    ctx.move_to(cx - r, cy - r); ctx.line_to(cx + r, cy + r); ctx.move_to(cx + r, cy - r); ctx.line_to(cx - r, cy + r)
    setc(ctx, RED, a); ctx.set_line_width(12); ctx.stroke()

def false_leads(ctx, t, a):
    """Glue? no. Melted? no. It peels off."""
    _panel(ctx, a)
    lt = t - B(3)
    # glue tube
    a1 = a
    rrect(ctx, 130, 260, 150, 70, 14); fill_stroke(ctx, MUSTARD, lw=4, alpha=a1)
    rrect(ctx, 280, 280, 40, 30, 6); fill_stroke(ctx, FILL3, lw=4, alpha=a1)
    text_c(ctx, "GLUE", 205, 305, 26, INK, True, 1, a1)
    if lt > 1.0: _cross(ctx, 225, 295, 70, a * ease(clamp((lt - 1.0) / 0.25)))
    # flame
    if lt > 1.6:
        a2 = a * ease(clamp((lt - 1.6) / 0.3))
        fx, fy = 540, 330
        ctx.move_to(fx, fy - 90); ctx.curve_to(fx + 60, fy - 30, fx + 50, fy + 30, fx, fy + 30)
        ctx.curve_to(fx - 50, fy + 30, fx - 60, fy - 30, fx, fy - 90); fill_stroke(ctx, RED, lw=4, alpha=a2)
        ctx.move_to(fx, fy - 30); ctx.curve_to(fx + 25, fy, fx + 20, fy + 25, fx, fy + 25)
        ctx.curve_to(fx - 20, fy + 25, fx - 25, fy, fx, fy - 30); setc(ctx, MUSTARD, a2); ctx.fill()
        text_c(ctx, "MELTED?", fx, 440, 24, INK, True, 1, a2)
        if lt > 2.6: _cross(ctx, fx, fy - 20, 70, a * ease(clamp((lt - 2.6) / 0.25)))
    # strip peeling off a short pipe stub
    if lt > 3.2:
        a3 = a * ease(clamp((lt - 3.2) / 0.3)); p = ease(clamp((lt - 3.4) / 1.2))
        ctx.rectangle(720, 330, 240, 50); fill_stroke(ctx, COPPER, lw=4, alpha=a3)
        # flat part of the strip on the pipe, the left end curls UP as it is peeled
        x_lift = 740 + 160 * p
        ctx.rectangle(x_lift, 316, 940 - x_lift, 14); fill_stroke(ctx, PET, stroke=PET_E, lw=3, alpha=a3)
        if p > 0.02:
            ctx.move_to(x_lift, 323); ctx.curve_to(x_lift - 30, 323, x_lift - 50, 300 - 50 * p, x_lift - 40, 280 - 60 * p)
            setc(ctx, PET_E, a3); ctx.set_line_width(14); ctx.stroke()
            straight_arrow(ctx, x_lift - 40, 280 - 60 * p, x_lift - 40, 245 - 60 * p, INK, a3 * p, lw=5, head=12)
        text_c(ctx, "PEELS OFF", 840, 440, 24, INK, True, 1, a3)

def small_pipe(ctx, t, a):
    """Same tie: the ring shrinks, the inward arrows grow."""
    _panel(ctx, a)
    p = ease(clamp((t - B(6) - 0.8) / 2.5))
    r = lerp(105, 42, p); L = lerp(18, 70, p)
    _ring(ctx, 330, 325, r * 0.95 if r > 100 else r, a, t, L)
    text_c(ctx, "TIGHTER CURVE", 760, 300, 34, INK, True, 1.5, a)
    text_c(ctx, "= HARDER PRESS", 760, 350, 34, RED, True, 1.5, a)

def thin_panel(ctx, t, a):
    """Side close-up: the force sits under a narrow band only."""
    _panel(ctx, a)
    py, pr = 315, 40
    ctx.rectangle(140, py - pr, 800, 2 * pr); fill_stroke(ctx, COPPER, lw=4, alpha=a)
    ctx.rectangle(400, py - pr - 10, 280, 2 * pr + 20); fill_stroke(ctx, PET, stroke=PET_E, lw=3, alpha=a)
    bx = 540
    ctx.rectangle(bx - 10, py - pr - 22, 20, 2 * pr + 44); fill_stroke(ctx, TIE, lw=3, alpha=a)
    for sy in (-1, 1):
        y0 = py + sy * (pr + 78); y1 = py + sy * (pr + 26)
        straight_arrow(ctx, bx, y0, bx, y1, RED, a, lw=10, head=18)
    text_c(ctx, "ALL THE FORCE, ONE NARROW BAND", 540, 462, 26, INK, True, 1.5, a)

def six_to_one(ctx, t, a):
    _panel(ctx, a)
    for i in range(6):
        k = ease(clamp((t - B(9) - 0.5 - i * 0.15) / 0.2))
        rrect(ctx, 100 + i * 76, 250, 64, 64, 8); fill_stroke(ctx, RED, lw=3, alpha=a * k)
    text_c(ctx, "TIES SQUEEZE", 307, 380, 26, RED, True, 1, a)
    text_c(ctx, "×6", 640, 310, 70, INK, True, 2, a)
    rrect(ctx, 790, 250, 64, 64, 8); fill_stroke(ctx, BLUE, lw=3, alpha=a)
    text_c(ctx, "WATER PUSH", 822, 380, 26, BLUE, True, 1, a)

def draw_hud(ctx, t, E):
    a = win(t, B(3) + 0.3, B(4), 0.3)
    if a > 0: false_leads(ctx, t, a)
    a = win(t, B(6) + 0.3, B(7), 0.3)
    if a > 0: small_pipe(ctx, t, a)
    a = win(t, B(8) + 0.3, B(9), 0.3)
    if a > 0: thin_panel(ctx, t, a)
    a = win(t, B(9) + 0.2, B(10), 0.3)
    if a > 0: six_to_one(ctx, t, a)

SFX = [(0.3, 'pop'), (0.75, 'click'), (1.0, 'click'), (1.9, 'pop'), (B(1) + 1.0, 'pop'), (B(2) + 0.3, 'pop'),
       (B(3) + 1.0, 'pop'), (B(3) + 2.6, 'pop'), (B(4) + 0.3, 'pop'), (B(4) + 0.6, 'click'), (B(5) + 0.3, 'pop'),
       (B(6) + 0.3, 'pop'), (B(8) + 0.3, 'pop'), (B(9) + 0.5, 'pop'), (B(11) + 0.9, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def _ring(ctx, cx, cy, r, a, t, arrow_len, wall=COPPER, inner=WATER):
    ctx.arc(cx, cy, r, 0, 2 * math.pi); fill_stroke(ctx, wall, lw=4, alpha=a)
    ctx.arc(cx, cy, max(r - 12, 4), 0, 2 * math.pi); setc(ctx, inner, a); ctx.fill()
    ctx.arc(cx, cy, r + 8, 0, 2 * math.pi); setc(ctx, TIE, a); ctx.set_line_width(8); ctx.stroke()
    for i in range(8):
        an = i * math.pi / 4
        x0, y0 = cx + (r + 14 + arrow_len) * math.cos(an), cy + (r + 14 + arrow_len) * math.sin(an)
        x1, y1 = cx + (r + 12) * math.cos(an), cy + (r + 12) * math.sin(an)
        straight_arrow(ctx, x0, y0, x1, y1, RED, a, lw=4 + arrow_len / 14, head=8 + arrow_len / 8)

WOOD = hexc('#c9a26b'); BARK = hexc('#7a5a3a')

def card_tree(ctx, t, lt, a):
    card_frame(ctx, "SAME TIE, TWO SIZES", a, "TREE: BARELY · PIPE: HARD", RED)
    # tree trunk (big ring of wood with growth rings), weak short arrows
    cx, cy, r = 330, 390, 120
    ctx.arc(cx, cy, r, 0, 2 * math.pi); fill_stroke(ctx, BARK, lw=4, alpha=a)
    ctx.arc(cx, cy, r - 14, 0, 2 * math.pi); setc(ctx, WOOD, a); ctx.fill()
    for rr in (80, 52, 26):
        ctx.arc(cx, cy, rr, 0, 2 * math.pi); setc(ctx, BARK, 0.6 * a); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(cx, cy, r + 6, 0, 2 * math.pi); setc(ctx, TIE, a); ctx.set_line_width(8); ctx.stroke()
    for i in range(8):
        an = i * math.pi / 4
        straight_arrow(ctx, cx + (r + 34) * math.cos(an), cy + (r + 34) * math.sin(an),
                       cx + (r + 12) * math.cos(an), cy + (r + 12) * math.sin(an), RED, a, lw=3, head=7)
    _ring(ctx, 790, 390, 48, a, t, 62)

def card_pinned(ctx, t, lt, a):
    card_frame(ctx, "AT THE HOLE", a, "HOLE OPEN · STRIP PINNED", RED)
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

CARDS = {'tree': card_tree, 'pinned': card_pinned}
