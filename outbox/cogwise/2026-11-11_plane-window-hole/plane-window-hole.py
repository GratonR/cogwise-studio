"""Cogwise episode: Your plane window has a tiny hole in it. On purpose.
One idea: the breather (bleed) hole in the MIDDLE pane lets cabin air into the gap between the middle
and outer panes, so the middle pane has the same pressure on both faces and carries no load, while the
OUTER pane takes the whole cabin-vs-outside push (~55 kPa · 8 psi, ≈ 450 kg · 1 000 lb on one window).
If the outer pane ever cracks, the middle pane takes the load: a fail-safe spare already in place.

VIEWS (screen coordinates, y grows DOWN):
  - beats 1-2: the window seen FROM THE SEAT (front view); the hole is near the BOTTOM of the middle pane.
  - beat 3 on: cross-section through the window, CABIN on the LEFT, SKY on the RIGHT.
    Order left -> right: scratch pane (thin, in the cabin wall panel) -> gap A (cabin air)
    -> middle pane (hole near its bottom) -> gap B (sealed top & bottom by the rubber seal) -> outer pane
    -> fuselage skin / sky. Pressure push = cabin -> sky = +x (arrows point RIGHT).
    The outer pane bows OUTWARD = toward the sky = +x.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="plane-window-hole",
    title="Your plane window has a hole in it — on purpose ✈️ #Shorts",
    description=("That tiny hole in your plane window decides which pane does all the work.\n\n"
                 "#Shorts #howthingswork #aviation #planes #cogwise"),
    hashtags=["Shorts", "howthingswork", "aviation", "planes", "engineering", "cogwise"],
    sources=[
        "https://time.com/3903109/airplane-window-holes",
        "https://migflug.com/afterburner/why-aircraft-windows-have-a-tiny-bleed-hole/",
    ],
)

BEATS = [
    dict(dur=4.6, title="A HOLE?", caption="Your plane window has a tiny hole in it. On purpose."),
    dict(dur=4.6, title="THE SECRET", caption="That little hole decides which pane does all the hard work."),
    dict(dur=5.0, title="THREE PANES", caption="Because a plane window isn't one window. It's three, stacked together."),
    dict(dur=5.6, title="1 · SCRATCH PANE", caption="The one you can touch is a thin plastic shield. It only stops scratches."),
    dict(dur=5.0, title="2 · MIDDLE PANE", caption="Behind it sits the middle pane. That's the one with the hole."),
    dict(dur=6.4, title="3 · OUTER PANE", caption="Then the outer pane, facing thin air eleven kilometres up, thirty-six thousand feet."),
    dict(dur=7.6, title="THE PUSH", caption="Up there, cabin air pushes outward with about four hundred fifty kilograms, a thousand pounds, on every window."),
    dict(dur=5.2, title="THROUGH THE HOLE", caption="The hole lets cabin air slip past the middle pane, into the gap."),
    dict(dur=4.8, title=None, caption="Same pressure on both sides, so the middle pane just rests.", card='rest'),
    dict(dur=5.4, title="OUTER PANE WORKS", caption="The outer pane takes the whole push on its own, flexing very slightly."),
    dict(dur=5.8, title=None, caption="If it ever cracks, the middle pane takes over. A spare, already in place.", card='spare'),
    dict(dur=4.0, title="1 WORKING · 1 WAITING", caption="Tiny hole: one pane working, one pane waiting."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette
ACRYL = hexc('#bcd7e3'); ACRYL_E = hexc('#7fa9bb')
PANEL = hexc('#efe4cd'); PANEL_E = hexc('#d9c9a8')
SEAL = hexc('#3b3842'); SKIN = hexc('#9aa3ab'); SKIN_D = hexc('#6e767d')
INSUL = hexc('#f2d58a')
SKY_T = hexc('#3f7fae'); SKY_B = hexc('#8fc0dc')

# ---------------------------------------------------------------- cross-section geometry
PT, PB = 570, 1230                 # pane span (top / bottom y)
SC0, SC1 = 352, 364                # scratch pane x (thin)
MI0, MI1 = 496, 524                # middle pane x
OU0, OU1 = 590, 632                # outer pane x
SK0, SK1 = 632, 660                # fuselage skin x
HOLE_Y, HOLE_R = 1150, 7           # breather hole: near the BOTTOM of the middle pane
SEAL_T = (488, PT - 34, OU1 + 10 - 488, 34)    # rubber seal block above the panes (x, y, w, h)
SEAL_B = (488, PB, OU1 + 10 - 488, 34)
CABIN = (70, 340)                  # cabin air x range
GAPA = (SC1 + 6, MI0 - 6)          # gap A: scratch -> middle (cabin air, open around the scratch pane)
GAPB = (MI1 + 6, OU0 - 6)          # gap B: middle -> outer (sealed, fed only by the hole)
SKY = (SK1 + 10, 1040)

# front view (beats 1-2)
FX, FY, FW, FH = 540, 880, 360, 520    # window centre / size, seen from the seat
F_HOLE = (540, FY + FH / 2 - 62)       # hole near the bottom of the middle pane

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['turn'] = clamp((t - B(2)) / 0.7)                 # 0 = front view, 1 = cross-section
    s['hole_ring'] = win(t, 0.2, B(2) + 0.2, 0.25)
    s['scratch'] = bw(t, 3)
    s['middle'] = max(bw(t, 4), 0.0)
    s['outer'] = bw(t, 5)
    s['thin'] = clamp(ease((t - B(5) - 0.3) / 0.8))     # sparse outside air from beat 6 on
    s['cabin_air'] = clamp(ease((t - B(6) - 0.2) / 0.8))
    s['push'] = bw(t, 6)
    s['flow'] = clamp(ease((t - B(7) - 0.3) / 2.6))     # gap B fills through the hole during beat 8
    s['flow_on'] = win(t, B(7) + 0.2, B(8) + 0.4, 0.3)
    s['bulge'] = clamp(ease((t - B(9) - 0.4) / 1.4)) * (1 - 0.5 * clamp((t - B(11)) / 0.6))
    s['work'] = bw(t, 9)
    s['recap'] = bw(t, 11)
    return s

# ---------------------------------------------------------------- front view
def front_view(ctx, t, s):
    k = 1 - ease(s['turn'])                             # horizontal squash = the window turns sideways
    if k <= 0.01: return
    ctx.save(); ctx.translate(FX, 0); ctx.scale(k, 1); ctx.translate(-FX, 0)
    # cabin wall panel
    rrect(ctx, FX - 330, FY - 430, 660, 860, 60); fill_stroke(ctx, PANEL, lw=5)
    # window reveal (the deep frame)
    rrect(ctx, FX - FW / 2 - 40, FY - FH / 2 - 40, FW + 80, FH + 80, 150); fill_stroke(ctx, PANEL_E, lw=4)
    # sky through the window
    ctx.save(); rrect(ctx, FX - FW / 2, FY - FH / 2, FW, FH, 130); ctx.clip()
    g = cairo.LinearGradient(0, FY - FH / 2, 0, FY + FH / 2)
    g.add_color_stop_rgb(0, *SKY_T[:3]); g.add_color_stop_rgb(1, *SKY_B[:3]); ctx.set_source(g); ctx.paint()
    rnd = random.Random(4)
    for i in range(5):                                  # clouds below, drifting
        x = FX - 220 + ((i * 120 + t * 22) % 480); y = FY + 120 + rnd.uniform(-20, 60)
        for dx, r in ((-30, 26), (0, 36), (34, 28)):
            ctx.arc(x + dx, y, r, 0, 2 * math.pi); setc(ctx, WHITE, 0.85); ctx.fill()
    ctx.restore()
    # pane edges: scratch pane (front), middle pane just behind
    rrect(ctx, FX - FW / 2, FY - FH / 2, FW, FH, 130); setc(ctx, INK, 1); ctx.set_line_width(5); ctx.stroke()
    rrect(ctx, FX - FW / 2 + 16, FY - FH / 2 + 16, FW - 32, FH - 32, 118)
    setc(ctx, ACRYL_E, 1); ctx.set_line_width(3); ctx.stroke()
    # reflection
    ctx.move_to(FX + 60, FY - FH / 2 + 30); ctx.line_to(FX + 110, FY - FH / 2 + 30)
    ctx.line_to(FX - 30, FY + FH / 2 - 40); ctx.line_to(FX - 80, FY + FH / 2 - 40); ctx.close_path()
    setc(ctx, WHITE, 0.14); ctx.fill()
    # THE HOLE (in the middle pane, near the bottom)
    hx, hy = F_HOLE
    ctx.arc(hx, hy, 9, 0, 2 * math.pi); setc(ctx, INK, 0.9); ctx.fill()
    ctx.arc(hx - 2, hy - 2, 3, 0, 2 * math.pi); setc(ctx, WHITE, 0.8); ctx.fill()
    a = s['hole_ring'] * k
    if a > 0:
        r = 34 + 4 * math.sin(t * 6)
        ctx.arc(hx, hy, r, 0, 2 * math.pi); setc(ctx, RED, a); ctx.set_line_width(6); ctx.stroke()
        ctx.move_to(hx + r * 0.7, hy + r * 0.7); ctx.line_to(hx + 120, hy + 120)
        ctx.set_line_width(5); ctx.stroke()
        tag(ctx, "TINY HOLE", hx + 170, hy + 150, RED, a, 26)
    ctx.restore()

# ---------------------------------------------------------------- cross-section
def outer_pane_path(ctx, bulge):
    """outer pane, bowing toward the SKY (+x) by `bulge` px at mid-height"""
    n = 24
    for i in range(n + 1):
        y = lerp(PT, PB, i / n); dx = bulge * math.sin(math.pi * i / n)
        (ctx.move_to if i == 0 else ctx.line_to)(OU0 + dx, y)
    for i in range(n, -1, -1):
        y = lerp(PT, PB, i / n); dx = bulge * math.sin(math.pi * i / n)
        ctx.line_to(OU1 + dx, y)
    ctx.close_path()

def dots(ctx, x0, x1, y0, y1, n, seed, t, a, col=None, r=5):
    if a <= 0: return
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1) + 6 * math.sin(t * 2.0 + i)
        y = rnd.uniform(y0, y1) + 6 * math.cos(t * 1.7 + i * 1.3)
        ctx.arc(clamp(x, x0, x1), clamp(y, y0, y1), r, 0, 2 * math.pi); setc(ctx, col or TEAL, a); ctx.fill()

def section(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.55) / 0.45))
    if a <= 0: return
    ctx.push_group()
    # sky (right of the skin)
    g = cairo.LinearGradient(0, 320, 0, 1480)
    g.add_color_stop_rgb(0, *SKY_T[:3]); g.add_color_stop_rgb(1, *SKY_B[:3])
    ctx.rectangle(SK1, 320, 1040 - SK1, 1160); ctx.set_source(g); ctx.fill()
    # cabin side (left): warm air
    ctx.rectangle(40, 320, SC0 - 40, 1160); setc(ctx, hexc('#f7efdf')); ctx.fill()
    # insulation blankets above / below the window, between wall panel and skin
    for y0, y1 in ((320, SEAL_T[1]), (SEAL_B[1] + SEAL_B[3], 1480)):
        ctx.rectangle(SC1, y0, SK0 - SC1, y1 - y0); setc(ctx, INSUL); ctx.fill()
        for k in range(int((y1 - y0) / 26)):
            yy = y0 + 13 + k * 26
            ctx.move_to(SC1 + 10, yy)
            for j in range(10): ctx.line_to(SC1 + 10 + (j + 0.5) * 24, yy + (6 if j % 2 == 0 else -6))
            setc(ctx, hexc('#d9b45a')); ctx.set_line_width(2); ctx.stroke()
    # cabin wall panel (above / below the scratch pane) — the scratch pane sits in it, NOT sealed:
    # a small gap at its bottom edge lets cabin air reach gap A
    for y0, y1 in ((320, PT - 10), (PB + 22, 1480)):
        ctx.rectangle(SC0 - 18, y0, 30, y1 - y0); fill_stroke(ctx, PANEL, lw=4)
    # fuselage skin
    for y0, y1 in ((320, SEAL_T[1] + 8), (SEAL_B[1] + SEAL_B[3] - 8, 1480)):
        ctx.rectangle(SK0, y0, SK1 - SK0, y1 - y0); fill_stroke(ctx, SKIN, lw=4)
        for yy in range(int(y0) + 30, int(y1) - 10, 60):
            ctx.arc((SK0 + SK1) / 2, yy, 4, 0, 2 * math.pi); setc(ctx, SKIN_D); ctx.fill()
    # rubber seal holding the middle + outer panes (closes gap B top and bottom)
    for (x, y, w, h) in (SEAL_T, SEAL_B):
        rrect(ctx, x, y, w, h, 8); fill_stroke(ctx, SEAL, lw=3)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

    # ---- air
    dots(ctx, CABIN[0], CABIN[1], 340, 1460, 70, 1, t, a * s['cabin_air'])
    dots(ctx, GAPA[0], GAPA[1], PT + 10, PB - 10, 26, 2, t, a * s['cabin_air'])
    dots(ctx, GAPB[0], GAPB[1], PT + 10, PB - 10, int(14 * s['flow']), 3, t, a * min(1, s['flow'] * 2))
    dots(ctx, SKY[0], SKY[1], 340, 1460, 9, 4, t, a * s['thin'], col=WHITE)
    # stream through the hole (gap A -> hole -> gap B), beat 8
    fa = s['flow_on'] * a
    if fa > 0:
        for k in range(8):
            u = ((t * 0.9) + k / 8) % 1
            x = lerp(GAPA[1] - 60, GAPB[0] + 30, u)
            y = HOLE_Y + (0 if MI0 - 10 < x < MI1 + 10 else 8 * math.sin(u * 9 + k))
            ctx.arc(x, y, 7, 0, 2 * math.pi); setc(ctx, TEAL, fa); ctx.fill_preserve()
            setc(ctx, INK, 0.6 * fa); ctx.set_line_width(1.5); ctx.stroke()

    # ---- panes
    sa = s['scratch']; ma = s['middle']; oa = s['outer']
    # scratch pane (thin)
    ctx.rectangle(SC0, PT, SC1 - SC0, PB - PT); fill_stroke(ctx, lerpc(ACRYL, MUSTARD, 0.5 * sa), stroke=INK, lw=3, alpha=a)
    # middle pane, with the hole drilled through near the bottom
    mcol = lerpc(ACRYL, MUSTARD, 0.5 * ma)
    ctx.rectangle(MI0, PT, MI1 - MI0, HOLE_Y - HOLE_R - PT); fill_stroke(ctx, mcol, lw=4, alpha=a)
    ctx.rectangle(MI0, HOLE_Y + HOLE_R, MI1 - MI0, PB - HOLE_Y - HOLE_R); fill_stroke(ctx, mcol, lw=4, alpha=a)
    # outer pane (bows toward the sky under load)
    bul = 16 * s['bulge']
    outer_pane_path(ctx, bul)
    fill_stroke(ctx, lerpc(ACRYL, RED, 0.35 * max(oa, s['work'])), lw=4, alpha=a)

    # ---- force on the outer pane (beat 10): arrows in gap B pointing RIGHT (cabin -> sky)
    wa = s['work'] * a
    if wa > 0:
        for y in (700, 840, 980, 1120):
            straight_arrow(ctx, GAPB[0] + 2, y, OU0 + bul * math.sin(math.pi * (y - PT) / (PB - PT)) - 4, y,
                           RED, wa, lw=6, head=12)

def overlays(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.5) / 0.5))
    if a <= 0: return
    tag(ctx, "CABIN", 200, 380, INK, a * (1 - s['push']), 26)
    tag(ctx, "SKY", 860, 380, TEAL, a, 26)
    # parts
    if s['scratch'] > 0:
        highlight(ctx, (SC0 + SC1) / 2, (PT + PB) / 2, 30, 360, MUSTARD, s['scratch'], t)
        tag(ctx, "1 · SCRATCH PANE", 250, 500, INK, s['scratch'], 24)
    if s['middle'] > 0:
        highlight(ctx, (MI0 + MI1) / 2, HOLE_Y, 46, 46, RED, s['middle'], t)
        tag(ctx, "2 · MIDDLE PANE", 510, 1330, INK, s['middle'], 24)
        tag(ctx, "HOLE", 420, HOLE_Y, RED, s['middle'], 22)
    if s['outer'] > 0:
        highlight(ctx, (OU0 + OU1) / 2, (PT + PB) / 2, 40, 370, MUSTARD, s['outer'], t)
        tag(ctx, "3 · OUTER PANE", 820, 500, INK, s['outer'], 24)
    # beat 7: the push, cabin -> sky (+x)
    pa = s['push']
    if pa > 0:
        for y in (720, 900, 1080):
            straight_arrow(ctx, 90, y, 320, y, RED, pa, lw=14, head=26)
        tag(ctx, "≈ 450 kg · 1 000 lb", 200, 1290, RED, pa, 26)
        tag(ctx, "CABIN AIR", 200, 560, TEAL, pa, 24)
        tag(ctx, "THIN AIR", 860, 1290, TEAL, pa, 24)
    fa = s['flow_on']
    if fa > 0:
        tag(ctx, "THE GAP", (GAPB[0] + GAPB[1]) / 2, 700, TEAL, fa, 24)
    if s['work'] > 0:
        tag(ctx, "TAKES THE WHOLE PUSH", 820, 1330, RED, s['work'], 22)
    ra = s['recap']
    if ra > 0:
        tag(ctx, "WAITING", 510, 1330, TEAL, ra, 26)
        tag(ctx, "WORKING", 820, 500, RED, ra, 26)
        tag(ctx, "TINY HOLE", 400, HOLE_Y, RED, ra, 22)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    front_view(ctx, t, s)
    section(ctx, t, s)
    overlays(ctx, t, s)

# camera: the hole is circled in the 1st second; push in on it for "the secret"; push in on the hole
# again (cross-section) while the air slips through in beat 8
CAMKEYS = [(0, 540, 900, 1.0), (B(1) + 0.1, F_HOLE[0], F_HOLE[1] - 60, 1.7), (B(2) - 0.2, 540, 900, 1.0),
           (B(7) + 0.2, 520, 830, 1.35), (B(8) - 0.5, 540, 900, 1.0)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)

def draw_hud(ctx, t, E):
    a = win(t, B(5) + 0.6, B(6), 0.3)
    if a > 0: hud(ctx, "OUTSIDE", "11 km", "36 000 ft · thin air", a, TEAL, x=520, y=196, w=520)
    a = win(t, B(6) + 0.8, B(7), 0.3)
    if a > 0: hud(ctx, "PUSH ON ONE WINDOW", "≈ 450 kg", "1 000 lb", a, RED, x=520, y=196, w=520)

SFX = [(0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(4) + 0.3, 'pop'), (B(5) + 0.3, 'pop'),
       (B(6) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def _pane(ctx, x0, x1, y0, y1, col, a, hole_y=None):
    if hole_y is None:
        ctx.rectangle(x0, y0, x1 - x0, y1 - y0); fill_stroke(ctx, col, lw=4, alpha=a)
    else:
        ctx.rectangle(x0, y0, x1 - x0, hole_y - 6 - y0); fill_stroke(ctx, col, lw=4, alpha=a)
        ctx.rectangle(x0, hole_y + 6, x1 - x0, y1 - hole_y - 6); fill_stroke(ctx, col, lw=4, alpha=a)

def card_rest(ctx, t, lt, a):
    card_frame(ctx, "THE MIDDLE PANE", a, "SAME PUSH BOTH SIDES = NO LOAD", TEAL)
    x0, x1, y0, y1 = 526, 554, 262, 530
    dots(ctx, 150, 500, 270, 520, 34, 7, t, a)
    dots(ctx, 580, 930, 270, 520, 34, 8, t, a)
    _pane(ctx, x0, x1, y0, y1, ACRYL, a, hole_y=500)
    # equal arrows, both pushing ON the pane (left one points right, right one points left)
    for y in (330, 430):
        straight_arrow(ctx, 330, y, x0 - 8, y, TEAL, a, lw=8, head=16)
        straight_arrow(ctx, 750, y, x1 + 8, y, TEAL, a, lw=8, head=16)
    text_c(ctx, "CABIN AIR", 280, 290, 22, INK, True, 1, a)
    text_c(ctx, "CABIN AIR", 800, 290, 22, INK, True, 1, a)

def card_spare(ctx, t, lt, a):
    card_frame(ctx, "IF THE OUTER PANE CRACKS", a, "THE MIDDLE PANE TAKES OVER", RED)
    y0, y1 = 262, 530
    k = ease(clamp((lt - 0.6) / 1.2))                    # crack appears, then the middle pane takes the load
    _pane(ctx, 440, 468, y0, y1, lerpc(ACRYL, MUSTARD, 0.7 * k), a, hole_y=500)
    _pane(ctx, 650, 688, y0, y1, ACRYL, a)
    # crack on the outer pane
    if lt > 0.4:
        pts = [(669, 300), (656, 340), (680, 372), (660, 410), (684, 448), (668, 490)]
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        setc(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
    # gap air leaks out through the crack (toward the sky, +x)
    for y in (360, 440):
        wavy_arrow(ctx, 700, y, 900, y, t, TEAL, a * k, amp=6, wl=26, lw=5, head=12)
    text_c(ctx, "LEAK", 800, 330, 22, TEAL, True, 1, a * k)
    # cabin push now lands on the middle pane (arrows pointing right, onto its cabin face)
    for y in (330, 430):
        straight_arrow(ctx, 170, y, 432, y, RED, a * k, lw=10, head=18)
    text_c(ctx, "CABIN", 260, 290, 22, INK, True, 1, a)
    text_c(ctx, "SPARE", 454, 252, 22, MUSTARD, True, 1, a * k)
    text_c(ctx, "CRACKED", 669, 252, 22, RED, True, 1, a)

CARDS = {'rest': card_rest, 'spare': card_spare}
