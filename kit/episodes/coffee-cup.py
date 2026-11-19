"""Cogwise episode: Paper falls apart in water. So why doesn't your coffee cup leak?
One idea: the coffee never touches the paper. A polyethylene film (~15 um) is melted onto the inside face
of the paperboard, and that same plastic replaces glue: side seam and bottom are heat-sealed.

VIEWS (screen coordinates, y grows DOWN):
  - beats 1-2, 12: CUP SECTION (front cut). Coffee inside, walls = beige paperboard band, BLUE film on
    the INSIDE face of each wall (the coffee side). Beat 2 zooms on the RIGHT wall: coffee LEFT, film, paper,
    outside RIGHT. Bottom disc raised above the bottom rim, film on its TOP face.
  - beats 3-4: wood-fibre mat (dry), the card shows water breaking the bonds.
  - beats 5-7: WALL SECTION, same orientation as the beat-2 zoom: coffee LEFT (x < 430), blue film
    430-460, paperboard 460-760 (fibres), outside RIGHT. Water pushes RIGHT and stops at the film.
  - beats 8-9: TOP VIEW of the cup (looking down into it): a ring. Film on the INNER face of the ring.
    Side seam at the RIGHT (angle 0): end A runs INSIDE, end B laps OVER it on the outside; the film of
    end B (its inner face) is sandwiched between the two layers -> that is what melts and welds.
  - beats 10-11: BOTTOM CORNER SECTION (right corner): cup inside LEFT/ABOVE, outside RIGHT/BELOW.
    Wall vertical (paper 700-728, film 692-700 on its inside/left face). Disc horizontal (paper y 1000-1028,
    film on TOP), its edge bends DOWN into a skirt (paper 656-684) whose film ends up on its RIGHT face
    (against the wall). Beat 11: the wall's lower end folds INWARD 180 deg under the skirt (rotation 0 -> +pi
    about (674, 1215): down -> left -> up, screen-clockwise), ending at x 620-656, its film facing the skirt.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="coffee-cup",
    title="Paper falls apart in water. So why doesn't your coffee cup leak? ☕ #Shorts",
    description=("Your coffee never touches the paper. A plastic skin thinner than a hair does the job, and replaces the glue too.\n\n"
                 "#Shorts #howthingswork #coffee #packaging #cogwise"),
    hashtags=["Shorts", "howthingswork", "coffee", "packaging", "cogwise"],
    sources=[
        "https://bioresources.cnr.ncsu.edu/resources/effect-of-material-properties-on-the-paper-cup-manufacturing-process/",
        "https://insights.basf.com/ed/article/read/anatomy-of-a-cup",
        "https://www.huhtamaki.com/en/highlights/sustainability/how-paper-cups-are-made/",
        "https://www.sciencetimes.com/articles/48942/20240227/why-paper-weaker-when-wet-unraveling-chemistry-behind-vulnerability-moisture.htm",
    ],
)

BEATS = [
    dict(dur=5.4, title="NO LEAK?", caption="Paper falls apart in water. So why doesn't your coffee cup leak?"),
    dict(dur=4.9, title="THE SECRET", caption="Because your coffee never touches the paper. It sits in plastic."),
    dict(dur=5.4, title="WET PAPER", caption="Paper is a mat of wood fibres, stuck together by tiny hydrogen bonds."),
    dict(dur=5.6, title=None, caption="Water slips between the fibres, breaks those bonds, and the mat falls apart.", card='wet'),
    dict(dur=5.4, title="1 · THE FILM", caption="So the inside of the cup is coated with a film of polyethylene."),
    dict(dur=4.8, title=None, caption="It's melted onto the paperboard, thinner than a human hair.", card='hair'),
    dict(dur=5.2, title="DRY BEHIND", caption="Water can't pass through it, so the fibres behind it stay dry."),
    dict(dur=5.4, title="2 · THE SEAM", caption="And there's no glue. The side seam is sealed with that same plastic."),
    dict(dur=6.0, title="HOT AIR", caption="Hot air melts the film in a fraction of a second, welding the overlap shut."),
    dict(dur=5.0, title="3 · THE BOTTOM", caption="The bottom is a separate paper disc, coated on its top side."),
    dict(dur=6.0, title="FOLD AND CRUSH", caption="The wall folds under its edge, is crushed tight, and the film welds it shut."),
    dict(dur=5.6, title="PAPER + PLASTIC", caption="Paper gives the cup its shape. An almost invisible plastic skin keeps it dry."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3): return ease(clamp((t - t0) / d))

BOARD = hexc('#e3c99a'); BOARD_D = hexc('#b8955c')     # paperboard
FILM = hexc('#2f6fc0')                                  # polyethylene film (blue)
COFFEE = hexc('#6b4226'); COFFEE_L = hexc('#8a5a36')
WATER = hexc('#7cc4e8')
HOT = ORANGE
STEEL = hexc('#9aa3ab')

def group(ctx, a, fn, *args):
    if a <= 0.001: return
    ctx.push_group(); fn(ctx, *args); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

def view_alphas(t):
    return dict(
        cup=max(1 - sstep(t, B(2) - 0.25, 0.5), sstep(t, B(11) - 0.25, 0.5)),
        fibre=win(t, B(2) - 0.25, B(4) + 0.25, 0.45),
        wall=win(t, B(4) - 0.25, B(7) + 0.25, 0.45),
        top=win(t, B(7) - 0.25, B(9) + 0.25, 0.45),
        bot=win(t, B(9) - 0.25, B(11) + 0.25, 0.45),
    )

# ================================================================ view 1: cup section
CUP_TOP, CUP_BOT = 560, 1400
XL_T, XR_T = 290, 790          # outer edges at the rim
XL_B, XR_B = 375, 705          # outer edges at the bottom rim
WT = 20                        # drawn wall thickness (exaggerated)
DISC_Y = 1345

def wall_x(side, y):
    """Outer edge x of the left (-1) / right (+1) wall at height y."""
    u = (y - CUP_TOP) / (CUP_BOT - CUP_TOP)
    return lerp(XL_T, XL_B, u) if side < 0 else lerp(XR_T, XR_B, u)

def cup_view(ctx, t):
    # coffee: pours in during the first 0.6 s, so the frame moves from frame one
    lvl = lerp(DISC_Y - 8, 640, sstep(t, 0.0, 0.7)) if t < B(2) else 640
    ctx.move_to(wall_x(-1, lvl) + WT + 6, lvl); ctx.line_to(wall_x(1, lvl) - WT - 6, lvl)
    ctx.line_to(wall_x(1, DISC_Y) - WT - 6, DISC_Y - 6); ctx.line_to(wall_x(-1, DISC_Y) + WT + 6, DISC_Y - 6); ctx.close_path()
    setc(ctx, COFFEE); ctx.fill()
    ctx.move_to(wall_x(-1, lvl) + WT + 6, lvl); ctx.line_to(wall_x(1, lvl) - WT - 6, lvl)
    setc(ctx, COFFEE_L); ctx.set_line_width(8); ctx.stroke()
    # steam
    if t > 0.8:
        for i, x in enumerate((470, 560, 640)):
            wavy_arrow(ctx, x, 530, x + 10, 380, t + i, INK2, 0.35 * sstep(t, 0.8, 0.5), amp=8, wl=40, lw=4, head=0.1)
    # walls (paper band + film on the inside face)
    film_a = sstep(t, 0.9, 0.5)
    flash = 0.0
    if t > B(11): flash = 0.5 + 0.5 * math.sin((t - B(11)) * 7) if t < B(11) + 1.8 else 0.0
    for side in (-1, 1):
        xo_t, xo_b = wall_x(side, CUP_TOP), wall_x(side, CUP_BOT)
        xi_t, xi_b = xo_t - side * WT, xo_b - side * WT
        ctx.move_to(xo_t, CUP_TOP); ctx.line_to(xo_b, CUP_BOT); ctx.line_to(xi_b, CUP_BOT); ctx.line_to(xi_t, CUP_TOP); ctx.close_path()
        fill_stroke(ctx, BOARD, lw=4)
        # film: grows from the rim downward at 0.9 s
        yb = lerp(CUP_TOP, CUP_BOT, film_a)
        if film_a > 0:
            u = film_a
            ctx.move_to(xi_t - side * 4, CUP_TOP); ctx.line_to(lerp(xi_t, xi_b, u) - side * 4, yb)
            setc(ctx, lerpc(FILM, WHITE, 0.0)); ctx.set_line_width(8 + 6 * flash); ctx.stroke()
        # rolled rim
        ctx.arc(xo_t - side * WT / 2, CUP_TOP - 8, 15, 0, 6.28); fill_stroke(ctx, BOARD, lw=4)
    # bottom disc (film on top)
    xl, xr = wall_x(-1, DISC_Y) + WT, wall_x(1, DISC_Y) - WT
    ctx.rectangle(xl, DISC_Y, xr - xl, 14); fill_stroke(ctx, BOARD, lw=4)
    if film_a > 0:
        ctx.move_to(xl, DISC_Y - 3); ctx.line_to(lerp(xl, xr, film_a), DISC_Y - 3)
        setc(ctx, FILM); ctx.set_line_width(8 + 6 * flash); ctx.stroke()
    # bottom fold (little U under each side)
    for side in (-1, 1):
        x = wall_x(side, CUP_BOT) - side * WT
        ctx.move_to(x, CUP_BOT); ctx.line_to(x - side * 26, CUP_BOT); ctx.line_to(x - side * 26, DISC_Y + 14)
        setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    a = sstep(t, 1.2, 0.3) * (1 - sstep(t, B(1) + 0.2, 0.3))
    if a > 0:
        highlight(ctx, wall_x(1, 950) - WT - 4, 950, 50, 360, FILM, a, t)
        tag(ctx, "PLASTIC", 905, 1180, FILM, a, 32)
        tag(ctx, "COFFEE", 540, 980, COFFEE, a, 30)
    a = sstep(t, B(11) + 0.4, 0.3)
    if a > 0:
        tag(ctx, "PAPER = SHAPE", 540, 1470, BOARD_D, a, 30)
        tag(ctx, "PLASTIC = DRY", 540, 470, FILM, sstep(t, B(11) + 1.6, 0.3), 30)

# ================================================================ view 2: fibre mat
_r = random.Random(11)
FIBRES = []
for _ in range(26):
    x0, y0 = _r.uniform(230, 850), _r.uniform(560, 1300)
    ang = _r.uniform(0, math.pi); L = _r.uniform(260, 420); bend = _r.uniform(-60, 60)
    FIBRES.append((x0, y0, ang, L, bend, _r.uniform(-1, 1), _r.uniform(-1, 1)))

def fibre_pts(f, spread=0.0):
    x0, y0, ang, L, bend, dx, dy = f
    x0 += dx * 120 * spread; y0 += dy * 120 * spread
    pts = []
    for i in range(9):
        s = i / 8 - 0.5
        px = x0 + math.cos(ang) * L * s - math.sin(ang) * bend * (1 - 4 * s * s)
        py = y0 + math.sin(ang) * L * s + math.cos(ang) * bend * (1 - 4 * s * s)
        pts.append((px, py))
    return pts

def _seg_x(p1, p2, p3, p4):
    d = (p2[0]-p1[0])*(p4[1]-p3[1]) - (p2[1]-p1[1])*(p4[0]-p3[0])
    if abs(d) < 1e-9: return None
    u = ((p3[0]-p1[0])*(p4[1]-p3[1]) - (p3[1]-p1[1])*(p4[0]-p3[0])) / d
    v = ((p3[0]-p1[0])*(p2[1]-p1[1]) - (p3[1]-p1[1])*(p2[0]-p1[0])) / d
    if 0 <= u <= 1 and 0 <= v <= 1: return (p1[0] + u*(p2[0]-p1[0]), p1[1] + u*(p2[1]-p1[1]))
    return None

BONDS = []
_P = [fibre_pts(f) for f in FIBRES]
for i in range(len(_P)):
    for j in range(i + 1, len(_P)):
        for a in range(8):
            for b in range(8):
                q = _seg_x(_P[i][a], _P[i][a+1], _P[j][b], _P[j][b+1])
                if q and 300 < q[0] < 780 and 600 < q[1] < 1260: BONDS.append(q)
BONDS = BONDS[:60]

def fibre_view(ctx, t):
    # beat 4 (card): the mat soaks and drifts apart
    wet = sstep(t, B(3) + 1.0, 2.5)
    rrect(ctx, 200, 520, 680, 820, 30); fill_stroke(ctx, lerpc(PAPER, hexc('#d9ecf4'), wet), lw=5)
    ctx.save(); rrect(ctx, 200, 520, 680, 820, 30); ctx.clip()
    for k, f in enumerate(FIBRES):
        pts = fibre_pts(f, 0.35 * wet)
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); setc(ctx, INK); ctx.set_line_width(20); ctx.stroke_preserve()
        setc(ctx, BOARD); ctx.set_line_width(13); ctx.stroke()
    ba = sstep(t, B(2) + 1.6, 0.4) * (1 - wet)
    for (x, y) in BONDS:
        ctx.arc(x, y, 8, 0, 6.28); setc(ctx, RED, ba); ctx.fill()
    ctx.restore()
    tag(ctx, "WOOD FIBRES", 540, 470, INK, sstep(t, B(2) + 0.6, 0.3), 30)
    tag(ctx, "HYDROGEN BONDS", 540, 1400, RED, sstep(t, B(2) + 1.8, 0.3) * (1 - wet), 30)
    tag(ctx, "FALLS APART", 540, 1400, TEAL, sstep(t, B(3) + 3.2, 0.3), 30)

# ================================================================ view 3: wall section
_r2 = random.Random(5)
WFIB = [(_r2.uniform(470, 750), _r2.uniform(330, 1460), _r2.uniform(-0.5, 0.5)) for _ in range(70)]
DROPS = [(_r2.uniform(0, 1), _r2.uniform(360, 1440)) for _ in range(26)]
FX0, FX1 = 430, 460            # film
PX1 = 760                      # paperboard outer face

def wall_view(ctx, t):
    # coffee (LEFT)
    ctx.rectangle(0, 300, FX0, 1200); setc(ctx, COFFEE); ctx.fill()
    text_c(ctx, "COFFEE", 215, 420, 34, WHITE, True, 3)
    text_c(ctx, "INSIDE", 215, 465, 24, WHITE, True, 2, 0.8)
    # paperboard: fibres
    ctx.rectangle(FX1, 300, PX1 - FX1, 1200); fill_stroke(ctx, BOARD, lw=4)
    ctx.save(); ctx.rectangle(FX1, 300, PX1 - FX1, 1200); ctx.clip()
    for (x, y, a) in WFIB:
        ctx.move_to(x - 70 * math.cos(a), y - 70 * math.sin(a)); ctx.line_to(x + 70 * math.cos(a), y + 70 * math.sin(a))
        setc(ctx, BOARD_D); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()
    text_c(ctx, "OUTSIDE", 920, 420, 28, INK2, True, 3)
    # film: draws top -> bottom during beat 5
    g = sstep(t, B(4) + 0.6, 1.6)
    if g > 0:
        y1 = lerp(300, 1500, g)
        ctx.rectangle(FX0, 300, FX1 - FX0, y1 - 300); setc(ctx, FILM); ctx.fill()
    ctx.move_to(FX0, 300); ctx.line_to(FX0, 1500); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    a = bw(t, 4, 6)
    tag(ctx, "1 · POLYETHYLENE FILM", 445, 1430, FILM, a * sstep(t, B(4) + 1.2, 0.3), 28)
    tag(ctx, "PAPERBOARD", 610, 640, BOARD_D, bw(t, 4, 7) * sstep(t, B(4) + 1.6, 0.3), 26)
    # beat 7: water pushes RIGHT, stops at the film; fibres behind stay dry
    a = bw(t, 6)
    if a > 0:
        lt = t - B(6)
        for k, (u, y) in enumerate(DROPS):
            x = (40 + u * 300 + lt * 260) % 390 + 20         # drift right ...
            x = min(x, FX0 - 14)                              # ... and stop at the film
            ctx.arc(x, y, 9, 0, 6.28); setc(ctx, WATER, a * 0.9); ctx.fill()
        for y in (560, 900, 1240):
            straight_arrow(ctx, 250, y, FX0 - 20, y, WATER, a * sstep(t, B(6) + 0.4, 0.3), lw=8, head=14)
        k = a * sstep(t, B(6) + 1.4, 0.3)
        tag(ctx, "BLOCKED", 280, 1080, RED, k, 28)
        tag(ctx, "DRY", 610, 1080, BOARD_D, a * sstep(t, B(6) + 2.2, 0.3), 34)

# ================================================================ view 4: top view, side seam
TCX, TCY, TR = 540, 920, 330
PT, FT = 22, 6                 # paper / film thickness (drawn)
OV = 0.32                      # overlap angle (rad)
def ring_rc(phi):
    """Centre radius of the wall strip; phi runs from -OV/2 (end A, inside) to 2pi+OV/2 (end B, outside)."""
    ramp = 0.35
    if phi < OV / 2: return TR - PT / 2 - 1
    if phi < OV / 2 + ramp: return lerp(TR - PT / 2 - 1, TR, ease((phi - OV / 2) / ramp))
    e = 2 * math.pi - OV / 2
    if phi < e - ramp: return TR
    if phi < e: return lerp(TR, TR + PT / 2 + FT + 1, ease((phi - e + ramp) / ramp))
    return TR + PT / 2 + FT + 1

def band(ctx, r_in_f, r_out_f, n=360):
    a0, a1 = -OV / 2, 2 * math.pi + OV / 2
    pts_o = [(a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    for i, p in enumerate(pts_o):
        r = r_out_f(p); x, y = TCX + r * math.cos(p), TCY + r * math.sin(p)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    for p in reversed(pts_o):
        r = r_in_f(p); ctx.line_to(TCX + r * math.cos(p), TCY + r * math.sin(p))
    ctx.close_path()

def melt(t):
    return sstep(t, B(8) + 1.0, 1.0) * (1 - sstep(t, B(8) + 3.0, 0.8))

def top_view(ctx, t):
    text_c(ctx, "TOP VIEW · LOOKING IN", 540, 500, 26, INK2, True, 3)
    n = 240
    for i in range(n + 1):
        p = -OV / 2 + (2 * math.pi) * i / n
        r = ring_rc(p) - PT / 2 - FT + 1
        (ctx.move_to if i == 0 else ctx.line_to)(TCX + r * math.cos(p), TCY + r * math.sin(p))
    ctx.close_path(); setc(ctx, COFFEE); ctx.fill()
    text_c(ctx, "COFFEE", TCX - 40, TCY + 12, 34, WHITE, True, 3)
    band(ctx, lambda p: ring_rc(p) - PT / 2, lambda p: ring_rc(p) + PT / 2); fill_stroke(ctx, BOARD, lw=3)
    m = melt(t)
    band(ctx, lambda p: ring_rc(p) - PT / 2 - FT, lambda p: ring_rc(p) - PT / 2)
    setc(ctx, FILM); ctx.fill()
    # melting film between the layers (end B's film, inside the overlap)
    if m > 0:
        ctx.new_path()
        for i in range(31):
            p = -OV / 2 + OV * i / 30
            r = TR + 1 + FT / 2
            (ctx.move_to if i == 0 else ctx.line_to)(TCX + r * math.cos(p), TCY + r * math.sin(p))
        setc(ctx, HOT, m); ctx.set_line_width(FT + 4); ctx.stroke()
    a = bw(t, 7)
    if a > 0:
        highlight(ctx, TCX + TR + 6, TCY, 60, 90, RED, a * sstep(t, B(7) + 0.5, 0.3), t)
        tag(ctx, "2 · SIDE SEAM", 860, 1340, RED, a * sstep(t, B(7) + 0.5, 0.3), 28)
        tag(ctx, "NO GLUE", 860, 1410, INK, a * sstep(t, B(7) + 1.5, 0.3), 26)
    # beat 9: hot air from a nozzle on the right, aimed LEFT at the overlap
    a = bw(t, 8)
    if a > 0:
        rrect(ctx, 960, TCY - 34, 120, 68, 10); fill_stroke(ctx, STEEL, lw=4, alpha=a)
        k = a * (1 - sstep(t, B(8) + 2.6, 0.4))
        for dy in (-22, 0, 22):
            wavy_arrow(ctx, 955, TCY + dy, TCX + TR + PT + 14, TCY + dy, t, HOT, k, amp=5, wl=24, lw=4, head=9)

def draw_seam_hud(ctx, t):
    a = bw(t, 8)
    tag(ctx, "HOT AIR", 860, 610, HOT, a * (1 - sstep(t, B(8) + 2.6, 0.4)), 28)
    tag(ctx, "FILM MELTS", 540, 1420, HOT, a * melt(t), 30)
    tag(ctx, "WELDED", 540, 1420, RED, a * sstep(t, B(8) + 3.4, 0.3), 32)

# ================================================================ view 5: bottom corner section
PX, PY = 674, 1215             # fold pivot
def fold_th(t):
    return math.pi * sstep(t, B(10) + 0.3, 1.8)

def disc_y_off(t):
    return -420 * (1 - sstep(t, B(9) + 0.2, 1.2))

def bot_view(ctx, t):
    dy = disc_y_off(t)
    # coffee above the disc, left of the wall film (appears once the joint is sealed)
    ca = sstep(t, B(10) + 4.2, 0.6)
    if ca > 0:
        ctx.rectangle(0, 300, 692, 692 - 0); setc(ctx, COFFEE, ca); ctx.fill()
        text_c(ctx, "COFFEE", 330, 620, 34, WHITE, True, 3, ca)
    text_c(ctx, "OUTSIDE", 900, 1420, 26, INK2, True, 3)
    # wall (fixed part): film 692-700, paper 700-728, from the top down to the fold pivot height
    ctx.rectangle(700, 300, 28, PY - 300); fill_stroke(ctx, BOARD, lw=3)
    ctx.rectangle(692, 300, 8, PY - 300); setc(ctx, FILM); ctx.fill()
    # disc + skirt (slides down into place in beat 10)
    ctx.save(); ctx.translate(0, dy)
    ctx.move_to(-20, 1000); ctx.line_to(684, 1000); ctx.line_to(684, 1200); ctx.line_to(656, 1200); ctx.line_to(656, 1028); ctx.line_to(-20, 1028); ctx.close_path()
    fill_stroke(ctx, BOARD, lw=3)
    ctx.move_to(-20, 996); ctx.line_to(688, 996); ctx.line_to(688, 1200)
    setc(ctx, FILM); ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_BUTT); ctx.stroke()
    ctx.restore()
    # folding part: U-bend (annular sector) + straight piece, rotated by th about the pivot
    th = fold_th(t)
    m = sstep(t, B(10) + 3.2, 0.5) * (1 - sstep(t, B(10) + 4.6, 0.6))
    if th > 0.001:
        ctx.new_path(); ctx.arc(PX, PY, 54, 0, th); ctx.arc_negative(PX, PY, 26, th, 0); ctx.close_path()
        fill_stroke(ctx, BOARD, lw=3)
        ctx.new_path(); ctx.arc(PX, PY, 26, 0, th); ctx.arc_negative(PX, PY, 18, th, 0); ctx.close_path()
        setc(ctx, FILM); ctx.fill()
    ctx.save(); ctx.translate(PX, PY); ctx.rotate(th)
    # pivot frame: at th = 0 the piece hangs DOWN (x 18..54 right of the pivot, y 0..170)
    ctx.rectangle(26, 0, 28, 170); fill_stroke(ctx, BOARD, lw=3)
    ctx.rectangle(18, 0, 8, 170); setc(ctx, lerpc(FILM, HOT, m)); ctx.fill()
    ctx.restore()
    # wall film near the joint glows while welding
    if m > 0:
        ctx.rectangle(684, 1000, 16, 200); setc(ctx, HOT, m); ctx.fill()
    a = bw(t, 9)
    if a > 0:
        highlight(ctx, 340, 996, 300, 40, FILM, a * sstep(t, B(9) + 1.4, 0.3), t)
        tag(ctx, "3 · PAPER DISC", 340, 900, INK, a * sstep(t, B(9) + 1.0, 0.3), 28)
        tag(ctx, "FILM ON TOP", 340, 1100, FILM, a * sstep(t, B(9) + 1.8, 0.3), 26)
    a = bw(t, 10)
    if a > 0:
        tag(ctx, "FOLD", 470, 1330, INK, a * sstep(t, B(10) + 0.8, 0.3) * (1 - sstep(t, B(10) + 2.6, 0.2)), 28)
        k = a * sstep(t, B(10) + 2.4, 0.3) * (1 - sstep(t, B(10) + 4.4, 0.3))
        for y in (1080, 1150):
            straight_arrow(ctx, 470, y, 606, y, RED, k, lw=8, head=14)
            straight_arrow(ctx, 880, y, 742, y, RED, k, lw=8, head=14)
        tag(ctx, "CRUSHED", 470, 1330, RED, k, 28)
        tag(ctx, "SEALED", 470, 1330, TEAL, a * sstep(t, B(10) + 4.6, 0.3), 30)

# ================================================================ assembly
def draw_set(ctx):
    pass

def draw(ctx, t, E):
    v = view_alphas(t)
    group(ctx, v['cup'], cup_view, t)
    group(ctx, v['fibre'], fibre_view, t)
    group(ctx, v['wall'], wall_view, t)
    group(ctx, v['top'], top_view, t)
    group(ctx, v['bot'], bot_view, t)

ZX = wall_x(1, 980) - WT / 2
CAM_KEYS = [(0, 540, 900, 1.0), (B(1) + 0.3, ZX, 960, 2.6), (B(2) - 0.4, 540, 900, 1.0),
            (B(8) + 0.1, TCX + TR, TCY, 2.2), (B(9) - 0.5, 540, 900, 1.0)]
def CAM(t):
    return cam_track(CAM_KEYS, t, 0.8)

def draw_hud(ctx, t, E):
    a = win(t, B(1) + 1.0, B(2) - 0.3, 0.3)
    if a > 0:
        cx, cy, z = CAM(t)
        def scr(x, y): return ((x - cx) * z + 540, (y - cy) * z + 900)
        tag(ctx, "COFFEE", 250, 1250, COFFEE, a, 30)
        k = a * sstep(t, B(1) + 1.5, 0.3)
        fx, fy = scr(wall_x(1, 900) - WT - 4, 900)
        straight_arrow(ctx, fx + 230, fy - 300, fx + 12, fy - 20, FILM, k, lw=5, head=11)
        tag(ctx, "PLASTIC FILM", fx + 230, fy - 340, FILM, k, 30)
        k = a * sstep(t, B(1) + 2.0, 0.3)
        px, py = scr(wall_x(1, 1040) - WT / 2, 1040)
        straight_arrow(ctx, px + 240, py + 200, px + 14, py + 10, BOARD_D, k, lw=5, head=11)
        tag(ctx, "PAPER", px + 250, py + 240, BOARD_D, k, 30)
    draw_seam_hud(ctx, t)

# ================================================================ cards
def card_wet(ctx, t, lt, a):
    card_frame(ctx, "WATER VS PAPER", a, "BONDS BREAK", TEAL)
    # two fibres crossing, joined by a bond; water creeps in and pushes them apart
    sep = 50 * sstep(lt, 1.6, 1.2)
    for (y, s) in ((380 - sep / 2, -1), (420 + sep / 2, 1)):
        ctx.move_to(220, y + s * 10); ctx.curve_to(400, y - s * 20, 680, y + s * 20, 860, y - s * 10)
        setc(ctx, INK, a); ctx.set_line_width(26); ctx.stroke_preserve(); setc(ctx, BOARD, a); ctx.set_line_width(18); ctx.stroke()
    b = 1 - sstep(lt, 1.6, 0.4)
    for x in (380, 540, 700):
        ctx.arc(x, 400, 9, 0, 6.28); setc(ctx, RED, a * b); ctx.fill()
    k = sstep(lt, 0.6, 1.0)
    for i, x in enumerate((300, 460, 620, 780)):
        xx = lerp(x - 120, x, k)
        ctx.arc(xx, 400, 12 * k, 0, 6.28); setc(ctx, WATER, a * k); ctx.fill()
    text_c(ctx, "H₂O", 160, 410, 30, TEAL, True, 1, a * k)

def card_hair(ctx, t, lt, a):
    card_frame(ctx, "THINNER THAN A HAIR", a, "≈ 15 µm · 0.0006 in", FILM)
    # same scale: 1 um = 2.6 px. Film 15 um, hair ~70 um, paperboard ~300 um (clipped)
    s = 2.6
    k = sstep(lt, 0.3, 0.6)
    x0 = 200
    ctx.rectangle(x0, 300, 15 * s, 200); setc(ctx, FILM, a * k); ctx.fill()
    ctx.rectangle(x0 + 15 * s, 300, 300 * s * 0.5, 200); fill_stroke(ctx, BOARD, lw=3, alpha=a * k)
    text_c(ctx, "FILM", x0 + 8, 285, 22, FILM, True, 1, a * k)
    text_c(ctx, "PAPERBOARD", x0 + 15 * s + 195, 410, 24, INK2, True, 2, a * k)
    h = sstep(lt, 1.2, 0.5)
    ctx.arc(820, 400, 70 * s / 2, 0, 6.28); fill_stroke(ctx, hexc('#4a3a2a'), lw=3, alpha=a * h)
    text_c(ctx, "HAIR ≈ 70 µm", 820, 520, 22, INK, True, 1, a * h)

CARDS = {'wet': card_wet, 'hair': card_hair}

SFX = [(1.2, 'pop'), (B(1) + 1.0, 'pop'), (B(2) + 0.6, 'pop'), (B(2) + 1.8, 'pop'),
       (B(4) + 1.2, 'pop'), (B(6) + 1.4, 'pop'), (B(7) + 0.5, 'pop'), (B(8) + 3.4, 'click'),
       (B(9) + 1.0, 'pop'), (B(10) + 2.4, 'click'), (B(10) + 4.6, 'pop'), (B(11) + 0.4, 'pop')]
HUM = []
