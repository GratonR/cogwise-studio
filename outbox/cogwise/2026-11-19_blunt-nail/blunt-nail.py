"""Cogwise episode: Carpenters blunt their nails on purpose.
One idea: a sharp point is a WEDGE: it slips between the wood fibres and pushes them apart, and near the end of a
board that push runs along the grain -> the board splits. A blunted point is a PUNCH: it can't slip between fibres,
it crushes and cuts them where it lands, nothing is forced sideways -> no split.

VIEWS (screen y grows DOWN):
- ANVIL: nail lying flat on an anvil, head LEFT, point RIGHT; the hammer comes straight DOWN on the point.
- BOARD: oblique view of a plank. Top face = parallelogram (front edge low, back edge up-right),
  grain (fibres) runs along the LENGTH = left-right. End face (end grain) at the RIGHT end.
  The nail goes straight DOWN into the top face near the right end. A split runs from the nail ALONG the grain
  to the right end, then down the end face.
- LOUPE: zoom SEEN FROM ABOVE on the top face: fibres = horizontal tubes (grain left-right).
  Sharp: the point (circle growing as it goes deeper) pushes the fibres UP and DOWN on screen = apart, across
  the grain; the gap runs RIGHT along the grain. Blunt: fibres stay straight, the ones under the point are cut
  (cut ends at the rim), crumbs, and the force is INTO the board only (crossed circle = arrow into the screen).
"""
import math, cairo
from cogwise.style import *

META = dict(
    slug="blunt-nail",
    title="Carpenters blunt their nails on purpose 🔨 #Shorts",
    description=("A sharp nail is a wedge: it pushes wood fibres apart and splits the board. A blunt one cuts its way in.\n\n"
                 "#Shorts #howthingswork #woodworking #carpentry #diy #cogwise"),
    hashtags=["Shorts", "howthingswork", "woodworking", "carpentry", "diy", "cogwise"],
    sources=[
        "https://www.ipm.org/show/amomentofscience/2019-09-13/dull-nails",
        "https://finehomebuilding.com/1982/09/02/split-free-nailing",
        "https://www.woodworkingnetwork.com/knowledge-center/wood-dr/splits-caused-nails-and-screws",
        "https://old.cwc.ca/wp-content/uploads/2019/04/Types_of_Nails_PDF.pdf",
    ],
)

BEATS = [
    dict(dur=3.9, title="ON PURPOSE", caption="Carpenters smash the point of a nail. On purpose."),
    dict(dur=4.7, title="THE SECRET", caption="The secret: a sharp point splits wood. A blunt one doesn't."),
    dict(dur=5.8, title="THE GRAIN", caption="Wood is a bundle of long fibres, like dry spaghetti glued side by side."),
    dict(dur=5.8, title="1 · SHARP POINT", caption="A sharp point slides between those fibres and pushes them apart, like a wedge."),
    dict(dur=7.0, title="THE CRACK", caption="Near the end of a board, that push runs along the grain, and the board cracks open."),
    dict(dur=5.1, title=None, caption="Like an axe: the thin edge opens the log along its fibres.", card='axe'),
    dict(dur=4.3, title="2 · BLUNT POINT", caption="Now flatten the point with two taps of the hammer."),
    dict(dur=6.6, title="THE PUNCH", caption="The blunt tip can't slip between fibres. It crushes and cuts them right where it lands."),
    dict(dur=5.1, title=None, caption="Like a hole punch: a clean plug pushed down, nothing forced sideways.", card='punch'),
    dict(dur=5.8, title="NO WEDGE", caption="The fibres around the nail barely move, so there's nothing to start a crack."),
    dict(dur=4.3, title="SAME SPOT", caption="Same board, same spot. Sharp nail: split. Blunt nail: solid."),
    dict(dur=5.5, title="CUT, DON'T WEDGE", caption="A blunt nail cuts its way in, instead of wedging the wood apart."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.05, B(j if j is not None else i + 1), f)

WOOD = hexc('#e9cf98'); WOOD_D = hexc('#c9a566'); WOOD_E = hexc('#d8b77a')
METAL = hexc('#cfd3d6'); METAL_D = hexc('#9aa1a6'); IRON = hexc('#4a4750')

def rnd(i, k=0):
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return x - math.floor(x)

# ---------------------------------------------------------------- board geometry (oblique)
X0, X1, FY, OX, OY, TH = 120.0, 900.0, 1200.0, 70.0, -170.0, 120.0
NU, NV = 0.72, 0.5                       # nail spot on the top face (along length, depth)
def top_pt(u, v): return (X0 + (X1 - X0) * u + OX * v, FY + OY * v)
NX, NY = top_pt(NU, NV)                  # (~716, 1115)
EX, EY = top_pt(1.0, NV)                 # where the split reaches the end of the board
BOARD_C = (545.0, 1175.0)

# ---------------------------------------------------------------- nail
def nail_local(ctx, L, w, p, a, head_r=None):
    """Nail along local +x: head at x=0, point at x=L. p = 0 sharp .. 1 blunt (flattened, slightly mushroomed)."""
    if a <= 0: return
    hr = head_r or w * 2.4
    Lt = lerp(w * 4.2, w * 1.0, p)        # length of the tapered tip
    xs = L - Lt
    tip_w = w * 1.05 * p                  # half width of the flat end
    ctx.move_to(4, -w); ctx.line_to(xs, -w)
    ctx.line_to(L, -tip_w); ctx.line_to(L, tip_w); ctx.line_to(xs, w); ctx.line_to(4, w); ctx.close_path()
    fill_stroke(ctx, METAL, lw=3.5, alpha=a)
    ctx.move_to(10, -w * 0.35); ctx.line_to(xs - 4, -w * 0.35); setc(ctx, WHITE, 0.7 * a); ctx.set_line_width(max(2, w * 0.35)); ctx.stroke()
    rrect(ctx, -w * 0.9, -hr, w * 1.5, 2 * hr, w * 0.4); fill_stroke(ctx, METAL_D, lw=3.5, alpha=a)

# ---------------------------------------------------------------- anvil scene (beats 0 and 6)
AV_NAIL = (300.0, 905.0)                 # head of the lying nail
AV_L = 440.0                             # nail length -> point at x = 740
AV_W = 13.0

def taps(t, t0):
    """two hammer taps starting at t0: returns (lift 0..1 (1 = raised), flatten progress 0..1)."""
    hits = (t0 + 0.55, t0 + 1.35)
    lift = 1.0; p = 0.0
    for k, h in enumerate(hits):
        d = t - h
        if -0.32 < d < 0:  lift = min(lift, clamp(-d / 0.32))           # coming down
        elif 0 <= d < 0.35: lift = min(lift, clamp(d / 0.35))          # bounce back up
        if d >= 0: p = (k + 1) / 2.0
    return lift, p

def anvil_scene(ctx, t, a, t0, p0):
    if a <= 0: return
    # anvil block
    ctx.move_to(250, 922); ctx.line_to(830, 922); ctx.line_to(830, 990); ctx.line_to(720, 1010)
    ctx.line_to(700, 1150); ctx.line_to(790, 1190); ctx.line_to(290, 1190); ctx.line_to(380, 1150); ctx.line_to(360, 1010)
    ctx.line_to(250, 990); ctx.close_path(); fill_stroke(ctx, IRON, lw=5, alpha=a)
    ctx.rectangle(262, 930, 556, 10); setc(ctx, WHITE, 0.25 * a); ctx.fill()
    lift, pp = taps(t, t0)
    p = max(p0, pp)
    ctx.save(); ctx.translate(*AV_NAIL)
    nail_local(ctx, AV_L, AV_W, p, a, head_r=30)
    ctx.restore()
    # hammer: head is a vertical block, its flat face (bottom) lands on the point; handle goes up-right
    px = AV_NAIL[0] + AV_L - 22                       # strike just at the point
    face_y = AV_NAIL[1] - AV_W - lift * 210           # bottom face of the hammer head
    ang = -0.25 * lift
    ctx.save(); ctx.translate(px, face_y); ctx.rotate(ang)
    ctx.move_to(20, -70); ctx.line_to(330, -230); ctx.line_to(346, -204); ctx.line_to(36, -46); ctx.close_path()
    fill_stroke(ctx, WOOD_D, lw=4, alpha=a)
    rrect(ctx, -40, -150, 80, 150, 10); fill_stroke(ctx, IRON, lw=4, alpha=a)
    ctx.rectangle(-36, -12, 72, 12); setc(ctx, METAL_D, a); ctx.fill()
    ctx.restore()
    # impact flash
    for h in (t0 + 0.55, t0 + 1.35):
        d = t - h
        if 0 <= d < 0.3:
            k = d / 0.3
            for j in range(6):
                an = math.pi + j * math.pi / 5
                r0, r1 = 40 + 30 * k, 70 + 40 * k
                ctx.move_to(px + r0 * math.cos(an), AV_NAIL[1] + r0 * math.sin(an) * 0.8)
                ctx.line_to(px + r1 * math.cos(an), AV_NAIL[1] + r1 * math.sin(an) * 0.8)
            setc(ctx, MUSTARD, a * (1 - k)); ctx.set_line_width(6); ctx.stroke()

# ---------------------------------------------------------------- board scene
def jag(i, k): return (rnd(i, k) - 0.5)

def board(ctx, t, a, p, drive, crack, show_grain=1.0):
    """The plank in oblique view, a nail (p sharp->blunt) going down at (NX, NY).
    drive 0..1 (0 = point just above the surface), crack 0..1 (split running to the end)."""
    if a <= 0: return
    fl, fr = top_pt(0, 0), top_pt(1, 0)
    bl, br = top_pt(0, 1), top_pt(1, 1)
    # front face
    ctx.move_to(*fl); ctx.line_to(*fr); ctx.line_to(fr[0], fr[1] + TH); ctx.line_to(fl[0], fl[1] + TH); ctx.close_path()
    fill_stroke(ctx, WOOD_E, lw=5, alpha=a)
    # end face (end grain, right)
    ctx.move_to(*fr); ctx.line_to(*br); ctx.line_to(br[0], br[1] + TH); ctx.line_to(fr[0], fr[1] + TH); ctx.close_path()
    fill_stroke(ctx, WOOD_D, lw=5, alpha=a)
    # top face
    ctx.move_to(*fl); ctx.line_to(*fr); ctx.line_to(*br); ctx.line_to(*bl); ctx.close_path()
    fill_stroke(ctx, WOOD, lw=5, alpha=a)
    # grain lines along the length (top + front), end-grain dots on the end face
    ga = a * show_grain
    for k in range(1, 9):
        v = k / 9.0
        x0, y0 = top_pt(0.0, v); x1, y1 = top_pt(1.0, v)
        ctx.move_to(x0 + 8, y0)
        n = 12
        for j in range(1, n + 1):
            u = j / n
            ctx.line_to(lerp(x0 + 8, x1 - 6, u), lerp(y0, y1, u) + 2.2 * math.sin(u * 9 + k * 1.7))
        setc(ctx, WOOD_D, 0.9 * ga); ctx.set_line_width(2.5); ctx.stroke()
    for k in range(1, 4):
        y = FY + TH * k / 4
        ctx.move_to(X0 + 10, y); ctx.line_to(X1 - 8, y + 2 * math.sin(k)); setc(ctx, WOOD_D, 0.9 * ga); ctx.set_line_width(2.5); ctx.stroke()
    for k in range(18):
        v = rnd(k, 1); h = rnd(k, 2)
        x = fr[0] + OX * v; y = fr[1] + OY * v + 14 + (TH - 28) * h
        ctx.arc(x, y, 3.2, 0, 2 * math.pi); setc(ctx, hexc('#a7834a'), ga); ctx.fill()
    # the split (sharp nail only): along the grain to the end, then down the end face
    if crack > 0:
        xe = lerp(NX, EX, crack)
        pts = []
        n = 14
        for j in range(n + 1):
            u = j / n
            x = lerp(NX, xe, u); y = lerp(NY, NY + (EY - NY) * crack, u) + 5 * jag(j, 3)
            pts.append((x, y, 2 + 7 * u * crack))
        ctx.move_to(pts[0][0], pts[0][1] - pts[0][2])
        for x, y, g in pts: ctx.line_to(x, y - g)
        for x, y, g in reversed(pts): ctx.line_to(x, y + g)
        ctx.close_path(); setc(ctx, INK, a); ctx.fill()
        down = clamp((crack - 0.85) / 0.15)
        if down > 0:
            ctx.move_to(EX - 9, EY)
            for j in range(1, 7):
                ctx.line_to(EX - 9 + 4 * jag(j, 5), EY + TH * down * j / 6)
            for j in range(6, -1, -1):
                ctx.line_to(EX + 9 - 6 * (j / 6) + 4 * jag(j, 6), EY + TH * down * j / 6)
            ctx.close_path(); setc(ctx, INK, a); ctx.fill()
    # nail: hole + visible part above the surface
    L, w = 240.0, 8.0
    py = NY - 26 + drive * (L * 0.88)            # point position
    if drive > 0.02:
        ctx.save(); ctx.translate(NX, NY); ctx.scale(1.0, 0.45); ctx.arc(0, 0, w + 3, 0, 2 * math.pi); ctx.restore()
        setc(ctx, INK, a); ctx.fill()
    ctx.save(); ctx.rectangle(0, 0, 1080, NY); ctx.clip()
    ctx.translate(NX, py - L); ctx.rotate(math.pi / 2)     # local +x -> screen DOWN (head up, point down)
    nail_local(ctx, L, w, p, a, head_r=20)
    ctx.restore()

def board_at(ctx, t, a, cx, cy, sc, p, drive, crack):
    if a <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(sc, sc); ctx.translate(-BOARD_C[0], -BOARD_C[1])
    board(ctx, t, a, p, drive, crack)
    ctx.restore()

def board_xy(cx, cy, sc, x, y):
    return (cx + (x - BOARD_C[0]) * sc, cy + (y - BOARD_C[1]) * sc)

# ---------------------------------------------------------------- loupe (seen from above)
LC = (540.0, 610.0); LR = 235.0

def loupe(ctx, t, a, mode, k):
    """mode 'plain' | 'sharp' | 'blunt'.  k = progress of the point into the wood (0..1)."""
    if a <= 0: return
    cx, cy = LC
    # leader line to the nail spot on the board
    ctx.move_to(cx + LR * 0.55, cy + LR * 0.83); ctx.line_to(NX - 45, NY + 4)
    setc(ctx, INK2, a); ctx.set_line_width(3); ctx.set_dash([10, 8]); ctx.stroke(); ctx.set_dash([])
    ctx.arc(cx, cy, LR, 0, 2 * math.pi); setc(ctx, CREAM, 0.98 * a); ctx.fill()
    ctx.save(); ctx.arc(cx, cy, LR - 4, 0, 2 * math.pi); ctx.clip()
    setc(ctx, hexc('#a7834a'), a * 0.55); ctx.paint()            # glue / gaps between fibres
    rr = 0.0; gapk = 0.0
    if mode == 'sharp':
        rr = 38 * ease(clamp(k / 0.6)); gapk = ease(clamp((k - 0.35) / 0.65))
    if mode == 'blunt':
        rr = 40.0
    H = 30.0                                                     # fibre pitch
    rows = [cy + H * (j + 0.5) for j in range(-9, 9)]
    for yo in rows:
        dyc = yo - cy; sgn = 1 if dyc > 0 else -1
        fall = math.exp(-(abs(dyc) - H / 2) / 70.0)
        pts_t, pts_b = [], []
        for j in range(0, 61):
            x = cx - LR + j * (2 * LR) / 60
            d = 0.0
            if mode == 'sharp':
                d += rr * 1.05 * math.exp(-((x - cx) / 70.0) ** 2) * fall
                if x > cx: d += gapk * 15 * fall * max(0.0, 1 - (x - cx) / (LR * 1.05))
                else: d += gapk * 6 * fall * math.exp((x - cx) / 60.0)
            y = yo + sgn * d
            pts_t.append((x, y - H * 0.40)); pts_b.append((x, y + H * 0.40))
        ctx.move_to(*pts_t[0])
        for q in pts_t[1:]: ctx.line_to(*q)
        for q in reversed(pts_b): ctx.line_to(*q)
        ctx.close_path(); fill_stroke(ctx, WOOD, WOOD_D, lw=2.5, alpha=a)
    if mode == 'sharp' and rr > 1:
        ctx.arc(cx, cy, rr, 0, 2 * math.pi); setc(ctx, hexc('#a7834a'), a); ctx.fill()
        ctx.arc(cx, cy, rr * 0.82, 0, 2 * math.pi); fill_stroke(ctx, METAL, lw=3, alpha=a)
        ctx.arc(cx, cy, 4, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()       # the tip, pointing at us
    if mode == 'blunt':
        g = clamp(k / 0.5)
        ctx.arc(cx, cy, rr + 6, 0, 2 * math.pi); setc(ctx, hexc('#7a5a2a'), a * g); ctx.fill()
        for j in range(16):                                  # crushed crumbs on the rim
            an = j * 2 * math.pi / 16 + 0.2 * rnd(j, 4)
            rx, ry = cx + (rr + 9) * math.cos(an), cy + (rr + 9) * math.sin(an)
            ctx.arc(rx, ry, 3 + 2 * rnd(j, 5), 0, 2 * math.pi); setc(ctx, WOOD_D, a * g); ctx.fill()
        ctx.arc(cx, cy, rr, 0, 2 * math.pi); fill_stroke(ctx, METAL, lw=3, alpha=a)
        # crossed circle = force pointing INTO the board (away from us)
        ctx.arc(cx, cy, 16, 0, 2 * math.pi); setc(ctx, RED, a); ctx.set_line_width(4); ctx.stroke()
        for s in (-1, 1):
            ctx.move_to(cx - 11, cy - 11 * s); ctx.line_to(cx + 11, cy + 11 * s)
        setc(ctx, RED, a); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
    ctx.arc(cx, cy, LR, 0, 2 * math.pi); setc(ctx, INK, a); ctx.set_line_width(9); ctx.stroke()
    text_c(ctx, "SEEN FROM ABOVE", cx, cy - LR - 18, 20, INK2, True, 1.5, a)
    # force arrows
    if mode == 'sharp' and k > 0.2:
        fa = a * clamp((k - 0.2) / 0.3)
        straight_arrow(ctx, cx, cy - 55, cx, cy - 150, RED, fa, lw=8, head=15)
        straight_arrow(ctx, cx, cy + 55, cx, cy + 150, RED, fa, lw=8, head=15)

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['anvil0'] = win(t, -1, B(1) + 0.2, 0.3)
    s['split1'] = win(t, B(1), B(2), 0.3)
    s['main'] = max(win(t, B(2), B(6) + 0.1, 0.3), win(t, B(7) - 0.1, B(10), 0.3))
    s['anvil6'] = win(t, B(6), B(7) + 0.1, 0.3)
    s['split10'] = win(t, B(10), B(12) + 4, 0.3)
    s['loupe_plain'] = win(t, B(2) + 0.6, B(3) + 0.1, 0.3)
    s['loupe_sharp'] = win(t, B(3), B(4) + 0.9, 0.3)
    s['loupe_blunt'] = max(win(t, B(7) + 0.2, B(8) + 0.2, 0.3), win(t, B(9) - 0.2, B(10), 0.3))
    return s

def main_board(t):
    """(p, drive, crack) of the single board."""
    if t < B(6):
        if t < B(3): return 0.0, 0.0, 0.0
        drive = 0.18 * ease(clamp((t - B(3) - 0.4) / 2.0)) + 0.82 * ease(clamp((t - B(4) - 0.2) / 2.2))
        crack = ease(clamp((t - B(4) - 1.2) / 3.2))
        return 0.0, drive, crack
    drive = 0.18 * ease(clamp((t - B(7) - 0.4) / 1.6)) + 0.82 * ease(clamp((t - B(9) - 0.1) / 2.2))
    return 1.0, drive, 0.0

def draw(ctx, t, E):
    s = state(t)
    # 0 / 6: the hammer taps on the anvil
    anvil_scene(ctx, t, s['anvil0'], 0.0, 0.0)
    anvil_scene(ctx, t, s['anvil6'], B(6) + 0.6, 0.0)
    a = s['anvil0']
    if a > 0 and t > 1.55:
        k = clamp((t - 1.55) / 0.3)
        px = AV_NAIL[0] + AV_L
        highlight(ctx, px - 6, AV_NAIL[1], 50, 40, RED, a * k, t)
        tag(ctx, "BLUNT, ON PURPOSE", px - 140, 1250, RED, a * k, 28)
        ctx.move_to(px - 70, 1222); ctx.line_to(px - 12, AV_NAIL[1] + 30); setc(ctx, RED, a * k); ctx.set_line_width(3); ctx.stroke()
    a = s['anvil6']
    if a > 0:
        lift, pp = taps(t, B(6) + 0.6)
        if pp >= 1.0:
            px = AV_NAIL[0] + AV_L
            highlight(ctx, px - 6, AV_NAIL[1], 50, 40, TEAL, a, t)
            tag(ctx, "FLAT TIP", px - 100, 1250, TEAL, a, 26)
    # 1 / 10-11: split screen, two boards (sharp on top, blunt below)
    for key in ('split1', 'split10'):
        a = s[key]
        if a <= 0: continue
        if key == 'split1':
            dr = ease(clamp((t - B(1) - 0.2) / 1.2)); cr = ease(clamp((t - B(1) - 0.9) / 1.6))
        else:
            dr = 1.0; cr = 1.0
        board_at(ctx, t, a, 540, 650, 0.68, 0.0, dr, cr)
        board_at(ctx, t, a, 540, 1170, 0.68, 1.0, dr, 0.0)
        ex, ey = board_xy(540, 650, 0.68, EX, EY)
        tag(ctx, "SHARP = SPLIT", 300, 470, RED, a * clamp((t - (B(1) + 1.6 if key == 'split1' else B(10))) / 0.3), 26)
        tag(ctx, "BLUNT = SOLID", 300, 990, TEAL, a * clamp((t - (B(1) + 1.6 if key == 'split1' else B(10) + 0.4)) / 0.3), 26)
        if key == 'split10':
            highlight(ctx, ex - 20, ey + 30, 110, 75, RED, a, t)
        if key == 'split10' and t > B(11):
            k = clamp((t - B(11) - 0.2) / 0.4)
            tag(ctx, "CUT", 380, 1430, TEAL, a * k, 40)
            text_c(ctx, ">", 540, 1446, 52, INK, True, 0, a * k)
            tag(ctx, "WEDGE", 700, 1430, RED, a * k, 40)
    # main board (beats 2-5 sharp, 7-9 blunt)
    a = s['main']
    if a > 0:
        p, drive, crack = main_board(t)
        # swap sharp board -> fresh board with a blunt nail during the anvil beat (board hidden then)
        board(ctx, t, a, p, drive, crack)
        ga = bw(t, 2)
        if ga > 0:
            for k in range(1, 9, 2):
                x0, y0 = top_pt(0.05, k / 9); x1, y1 = top_pt(0.95, k / 9)
                ctx.move_to(x0, y0); ctx.line_to(x1, y1)
            setc(ctx, MUSTARD, ga * 0.9); ctx.set_line_width(5); ctx.stroke()
            tag(ctx, "FIBRES", 300, 1400, INK, ga, 26)
            straight_arrow(ctx, 470, 1400, 880, 1400, INK2, ga, lw=4, head=10)
            text_c(ctx, "GRAIN", 675, 1440, 22, INK2, True, 1.5, ga)
        ca = bw(t, 4)
        if ca > 0 and crack > 0.6:
            k = clamp((crack - 0.6) / 0.3)
            highlight(ctx, (NX + EX) / 2 + 20, NY + 40, 170, 95, RED, ca * k, t)
            tag(ctx, "SPLIT", (NX + EX) / 2 + 20, NY + 230, RED, ca * k, 28)
            # the push: across the grain, toward the front and the back of the board
            straight_arrow(ctx, NX - 4, NY + 24, NX - 4 - OX * 0.55, NY + 24 - OY * 0.55, RED, ca * k, lw=6, head=12)
            straight_arrow(ctx, NX + 4, NY - 24, NX + 4 + OX * 0.55, NY - 24 + OY * 0.55, RED, ca * k, lw=6, head=12)
        na = bw(t, 9)
        if na > 0 and drive > 0.9:
            k = clamp((drive - 0.9) / 0.1)
            highlight(ctx, (NX + EX) / 2 + 20, NY + 40, 170, 95, TEAL, na * k, t)
            tag(ctx, "NO CRACK", (NX + EX) / 2 + 20, NY + 230, TEAL, na * k, 28)
    loupe(ctx, t, s['loupe_plain'], 'plain', 0.0)
    loupe(ctx, t, s['loupe_sharp'], 'sharp', clamp((t - B(3) - 0.3) / 3.2))
    loupe(ctx, t, s['loupe_blunt'], 'blunt', clamp((t - B(7) - 0.6) / 1.2))
    a = bw(t, 3)
    if a > 0 and t > B(3) + 2.0:
        tag(ctx, "WEDGE", LC[0] + 175, LC[1] - 175, RED, a * clamp((t - B(3) - 2.0) / 0.3), 28)
    a = win(t, B(7) + 0.2, B(8), 0.3)
    if a > 0 and t > B(7) + 1.6:
        tag(ctx, "CUT + CRUSHED", LC[0] + 150, LC[1] - 190, TEAL, a * clamp((t - B(7) - 1.6) / 0.3), 26)
    a = bw(t, 9)
    if a > 0:
        tag(ctx, "FIBRES STAY STRAIGHT", LC[0], LC[1] + LR + 40, TEAL, a, 24)

def draw_set(ctx):
    pass

ANCHOR = (540, 1450)

SFX = [(0.55, 'click'), (1.35, 'click'), (1.6, 'pop'), (B(1) + 1.6, 'pop'), (B(2) + 0.8, 'pop'), (B(3) + 2.0, 'pop'),
       (B(4) + 3.5, 'pop'), (B(6) + 1.15, 'click'), (B(6) + 1.95, 'click'), (B(7) + 1.6, 'pop'), (B(9) + 2.3, 'pop'),
       (B(10) + 0.1, 'pop'), (B(11) + 0.2, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_axe(ctx, t, lt, a):
    card_frame(ctx, "LIKE AN AXE", a, "A WEDGE SPLITS ALONG THE FIBRES", RED)
    # log standing up, fibres vertical (seen from the side); the axe comes DOWN into its top
    lx0, lx1, ly0, ly1 = 400, 680, 330, 540
    k = ease(clamp((lt - 0.5) / 1.2))          # axe going down
    op = ease(clamp((lt - 1.3) / 1.5))         # the split opening
    gap = 34 * op; depth = (ly1 - ly0) * (0.25 + 0.75 * op)
    cx = (lx0 + lx1) / 2
    for side in (-1, 1):
        ctx.save(); ctx.translate(side * gap / 2, 0)
        if side < 0:
            ctx.move_to(lx0, ly0); ctx.line_to(cx, ly0); ctx.line_to(cx, ly0 + depth); ctx.line_to(cx, ly1); ctx.line_to(lx0, ly1)
        else:
            ctx.move_to(cx, ly0); ctx.line_to(lx1, ly0); ctx.line_to(lx1, ly1); ctx.line_to(cx, ly1); ctx.line_to(cx, ly0 + depth)
        ctx.close_path(); fill_stroke(ctx, WOOD, lw=4, alpha=a)
        for j in range(1, 5):
            x = (lx0 if side < 0 else cx) + j * (cx - lx0) / 5
            ctx.move_to(x, ly0 + 8); ctx.line_to(x, ly1 - 8)
        setc(ctx, WOOD_D, a); ctx.set_line_width(3); ctx.stroke()
        ctx.restore()
    # V-shaped crack between the halves (open at the top, closing downward)
    ctx.move_to(cx - gap / 2, ly0); ctx.line_to(cx + gap / 2, ly0); ctx.line_to(cx, ly0 + depth); ctx.close_path()
    setc(ctx, INK, a); ctx.fill()
    # axe blade: thin edge pointing DOWN
    by = lerp(250, ly0 + 46 * op, k)
    ctx.move_to(cx, by + 40); ctx.line_to(cx - 30, by - 30); ctx.line_to(cx + 30, by - 30); ctx.close_path()
    fill_stroke(ctx, METAL, lw=4, alpha=a)
    ctx.rectangle(cx - 30, by - 70, 60, 40); fill_stroke(ctx, IRON, lw=4, alpha=a)
    if op > 0.2:
        straight_arrow(ctx, cx - 60, ly0 + 70, cx - 200, ly0 + 70, RED, a * op, lw=7, head=13)
        straight_arrow(ctx, cx + 60, ly0 + 70, cx + 200, ly0 + 70, RED, a * op, lw=7, head=13)

def card_punch(ctx, t, lt, a):
    card_frame(ctx, "LIKE A HOLE PUNCH", a, "STRAIGHT DOWN, NOTHING SIDEWAYS", TEAL)
    sy = 430                                   # paper sheet (side view)
    k = ease(clamp((lt - 0.5) / 1.0))          # punch going down
    plug = ease(clamp((lt - 1.4) / 1.0))       # plug falling out
    cx, hw = 540, 42
    ctx.rectangle(180, sy, cx - hw - 180, 14); fill_stroke(ctx, WHITE, lw=3, alpha=a)
    ctx.rectangle(cx + hw, sy, 900 - cx - hw, 14); fill_stroke(ctx, WHITE, lw=3, alpha=a)
    if plug < 1:
        ctx.rectangle(cx - hw, sy + 60 * plug, 2 * hw, 14); fill_stroke(ctx, WHITE, lw=3, alpha=a * (1 - 0.3 * plug))
    else:
        ctx.rectangle(cx - hw, sy + 60, 2 * hw, 14); fill_stroke(ctx, WHITE, lw=3, alpha=a * 0.7)
    # die under the sheet
    ctx.rectangle(180, sy + 14, cx - hw - 180, 30); fill_stroke(ctx, METAL_D, lw=3, alpha=a)
    ctx.rectangle(cx + hw, sy + 14, 900 - cx - hw, 30); fill_stroke(ctx, METAL_D, lw=3, alpha=a)
    # flat-ended punch coming down
    py = lerp(300, sy + 60 * plug, k) if plug > 0 else lerp(300, sy, k)
    ctx.rectangle(cx - hw + 2, py - 120, 2 * hw - 4, 120); fill_stroke(ctx, METAL, lw=4, alpha=a)
    straight_arrow(ctx, cx + 110, 280, cx + 110, 380, RED, a, lw=7, head=13)
    # sheet edges stay flat: small teal check marks
    if plug > 0.6:
        for x in (300, 780):
            text_c(ctx, "FLAT", x, sy - 20, 22, TEAL, True, 1, a * clamp((plug - 0.6) / 0.3))

CARDS = {'axe': card_axe, 'punch': card_punch}
