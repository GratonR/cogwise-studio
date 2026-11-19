"""Cogwise episode: Your fridge door is held shut by a fridge magnet.
One idea: no latch, the door gasket hides a flexible multipole magnet strip that grabs the steel cabinet;
since the 1956 Refrigerator Safety Act (fridges built after 31 Oct 1958) a push from inside must open the door.

VIEWS (screen coordinates, y grows DOWN):
  - beat 1: TOP VIEW. Cabinet above (y 520-1060), door below it, hinge pivot at the door's outer LEFT corner
    (250, 1150). Opening = positive rotation (free end moves DOWN, away from the cabinet); it closes to 0.
  - beat 2: the open door seen on its INSIDE face; the gasket runs all around, the red strip traces the loop.
  - beats 3-8, 10, 11: SECTION through the latch-side edge, same orientation as the top view:
      cabinet side wall above (liner left at x 520, outer steel skin right at x 880), its front face = steel
      flange at y 760-780 (YF = 780). Fridge INSIDE is LEFT of the wall, the ROOM is RIGHT.
      Door below (inner face at YD, outer steel at the bottom). Gasket on the door's inner face at GX = 745:
      base -> hollow bellows -> pocket with the red magnet strip at the TOP, facing the flange.
      Magnet pull on the strip points UP (toward the flange). A push from inside pushes the door DOWN (away).
      Ajar YD = 1090 (60 px air gap), closed YD = 950 (seal squashed to 170 px from 250).
  - beat 9: front view of a 1950s fridge with a lever latch; detail circle = latch seen like the section:
      cabinet above with a striker pin, door below, hook curls OVER the pin, so pulling the door down is blocked.
  - beat 12: front view of a closed modern fridge with two fridge magnets.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="fridge-door-magnet",
    title="Your fridge door is held shut by a fridge magnet 🧲 #Shorts",
    description=("No latch, no lock. A flexible magnet hides in the rubber seal.\n\n"
                 "#Shorts #howthingswork #fridge #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "fridge", "appliances", "cogwise"],
    sources=[
        "https://www.kjmagnetics.com/blog/remagnetizing-fridge-seals",
        "https://en.wikipedia.org/wiki/Refrigerator_death",
        "https://www.law.cornell.edu/cfr/text/16/1750.5",
        "https://www.cpsc.gov/Newsroom/News-Releases/1984/CPSC-Warns-About-Children-Suffocating-In-Old-Unused-Referigerators",
    ],
)

BEATS = [
    dict(dur=5.6, title="NO LATCH", caption="No latch. No lock. Your fridge door is held shut by a fridge magnet."),
    dict(dur=4.9, title="THE SECRET", caption="Inside the rubber seal, a flexible magnet runs all around the door."),
    dict(dur=4.9, title="1 · THE SEAL", caption="The seal is a hollow rubber tube that squashes like an accordion."),
    dict(dur=4.9, title="2 · THE STRIP", caption="In its pocket sits a strip of rubber packed with magnetic powder."),
    dict(dur=5.2, title="3 · THE FRAME", caption="The fridge cabinet is steel, so the strip grabs it on every side."),
    dict(dur=5.9, title=None, caption="Its poles run in thin stripes, so almost all the pull is on one face.", card='onesided'),
    dict(dur=4.9, title="SQUASHED SHUT", caption="That pull crushes the hollow seal flat against the frame. No gaps."),
    dict(dur=5.6, title="THE PROOF", caption="Shut the door on a sheet of paper, tug, and you'll feel it grip."),
    dict(dur=5.6, title="WHY NOT A LATCH", caption="Old fridges had latches that only opened from outside. Kids hiding inside got trapped."),
    dict(dur=6.9, title=None, caption="Since 1958, US law says a push from inside must open the door: sixty-seven newtons, about fifteen pounds.", card='law'),
    dict(dur=5.6, title="HOLDS, THEN LETS GO", caption="A magnet does both: it holds tight, then lets go to a firm shove."),
    dict(dur=5.2, title="MAGNET = LATCH", caption="So your door isn't locked. It's stuck, like the magnets on the front."),
]


ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3): return ease(clamp((t - t0) / d))

STEEL = hexc('#9aa3ab'); STEEL_D = hexc('#6d757c')
RUB = hexc('#d9d4c7'); FOAM = hexc('#f1e3b8')
COLDT = hexc('#8fcfc8')

# ---------------------------------------------------------------- section geometry
YF = 780            # flange (cabinet front face), underside
GX = 745            # gasket centre
H0 = 250            # gasket rest height
Y_AJAR, Y_SHUT = 1090, 950
DOOR_X1 = 920

def door_y(t):
    y = Y_AJAR
    # beat 3: accordion demo (press, hold, release)
    l3 = t - B(2)
    if 0 <= l3 < B(3) - B(2):
        y = lerp(Y_AJAR, Y_SHUT, sstep(l3, 1.0, 0.7)) if l3 < 2.6 else lerp(Y_SHUT, Y_AJAR, sstep(l3, 2.9, 0.7))
    if t >= B(6):
        y = lerp(Y_AJAR, Y_SHUT, sstep(t, B(6) + 0.6, 0.7))
    if t >= B(10):
        l = t - B(10)
        if l < 1.85: y = lerp(Y_SHUT, 1060, sstep(l, 0.9, 0.95))
        else: y = lerp(1060, 1150, sstep(l, 1.85, 0.7))
    return y

def stuck(t):
    return sstep(t, B(6) + 0.3, 0.15) * (1 - sstep(t, B(10) + 1.85, 0.12))

def gasket_h(t, yd):
    gap = yd - YF
    return lerp(min(H0, gap), gap, stuck(t))

# ---------------------------------------------------------------- views
def view_alphas(t):
    return dict(
        top=1 - sstep(t, B(1) - 0.25, 0.5),
        inner=win(t, B(1) - 0.25, B(2) + 0.25, 0.45),
        sec=max(win(t, B(2) - 0.15, B(8) + 0.2, 0.4), win(t, B(9) - 0.2, B(11) + 0.2, 0.4)),
        old=win(t, B(8) - 0.15, B(9) + 0.15, 0.4),
        front=sstep(t, B(11) - 0.2, 0.5),
    )

def group(ctx, a, fn, *args):
    if a <= 0.001: return
    ctx.push_group(); fn(ctx, *args); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

# ---- beat 1: top view
def theta(t):
    th0 = 0.55
    if t < 0.85: return th0 * (1 - (t / 0.85) ** 2)
    return 0.03 * abs(math.sin((t - 0.85) * 14)) * math.exp(-(t - 0.85) * 6)

def top_view(ctx, t):
    text_c(ctx, "TOP VIEW", 540, 490, 26, INK2, True, 3)
    rrect(ctx, 250, 520, 580, 540, 14); fill_stroke(ctx, PAPER, lw=6)
    rrect(ctx, 300, 570, 480, 440, 10); ctx.set_dash([12, 10]); setc(ctx, INK2); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    text_c(ctx, "CABINET", 540, 800, 30, INK2, True, 3)
    ctx.save(); ctx.translate(250, 1150); ctx.rotate(theta(t))
    rrect(ctx, 0, -70, 580, 70, 10); fill_stroke(ctx, FILL2, lw=6)
    rrect(ctx, 520, 0, 44, 22, 6); fill_stroke(ctx, STEEL, lw=4)           # handle, outside face
    rrect(ctx, 12, -90, 556, 20, 6); fill_stroke(ctx, RUB, lw=4)          # gasket on the inside face
    g = sstep(t, 1.0, 0.3)
    ctx.rectangle(24, -85, 532, 9); setc(ctx, lerpc(INK2, RED, max(0.35, g))); ctx.fill()
    text_c(ctx, "DOOR", 290, -24, 28, INK, True, 3)
    ctx.restore()
    ctx.arc(250, 1150, 9, 0, 6.28); fill_stroke(ctx, STEEL_D, lw=3)
    a = sstep(t, 1.1, 0.3)
    if a > 0:
        highlight(ctx, 540, 1070, 320, 34, RED, a, t)
        tag(ctx, "FRIDGE MAGNET", 540, 1250, RED, a, 32)
        tag(ctx, "NO LATCH", 860, 1330, INK, sstep(t, 2.2, 0.3), 26)

# ---- beat 2: inside face of the open door
def rr_points(x, y, w, h, r, n=240):
    """Points around a rounded rectangle, clockwise from the top-left straight edge."""
    segs = []
    per = 2 * (w + h - 4 * r) + 2 * math.pi * r
    pts = []
    for i in range(n + 1):
        s = per * i / n
        # walk: top edge, TR arc, right edge, BR arc, bottom edge, BL arc, left edge, TL arc
        L = [w - 2*r, math.pi*r/2, h - 2*r, math.pi*r/2, w - 2*r, math.pi*r/2, h - 2*r, math.pi*r/2]
        k = 0
        while k < 7 and s > L[k]: s -= L[k]; k += 1
        if k == 0: p = (x + r + s, y)
        elif k == 1: a = -math.pi/2 + s / r; p = (x + w - r + r*math.cos(a), y + r + r*math.sin(a))
        elif k == 2: p = (x + w, y + r + s)
        elif k == 3: a = s / r; p = (x + w - r + r*math.cos(a), y + h - r + r*math.sin(a))
        elif k == 4: p = (x + w - r - s, y + h)
        elif k == 5: a = math.pi/2 + s / r; p = (x + r + r*math.cos(a), y + h - r + r*math.sin(a))
        elif k == 6: p = (x, y + h - r - s)
        else: a = math.pi + s / r; p = (x + r + r*math.cos(a), y + r + r*math.sin(a))
        pts.append(p)
    return pts

GPTS = rr_points(324, 404, 432, 1012, 30)

def inner_view(ctx, t):
    text_c(ctx, "DOOR · INSIDE FACE", 540, 350, 26, INK2, True, 3)
    rrect(ctx, 300, 380, 480, 1060, 34); fill_stroke(ctx, PAPER, lw=6)
    for yy in (450, 1350):
        rrect(ctx, 286, yy, 22, 70, 5); fill_stroke(ctx, STEEL, lw=3)       # hinges on the left
    for yy in (560, 960, 1220):
        rrect(ctx, 370, yy, 340, 80, 10); fill_stroke(ctx, FILL3, lw=4)     # door bins
    rrect(ctx, 308, 388, 464, 1044, 32); setc(ctx, RUB); ctx.set_line_width(30); ctx.stroke()
    rrect(ctx, 308, 388, 464, 1044, 32)
    rrect(ctx, 293, 373, 494, 1074, 40); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    rrect(ctx, 323, 403, 434, 1014, 26); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    p = sstep(t, B(1) + 0.4, 2.6)
    if p > 0:
        n = max(2, int(len(GPTS) * p))
        ctx.move_to(*GPTS[0])
        for q in GPTS[1:n]: ctx.line_to(*q)
        setc(ctx, RED); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ctx.arc(*GPTS[n - 1], 13, 0, 6.28); setc(ctx, RED); ctx.fill()
    tag(ctx, "MAGNET · ALL AROUND", 540, 790, RED, sstep(t, B(1) + 0.6, 0.3), 30)
    c = sstep(t, B(2) - 1.4, 0.3)
    if c > 0:
        ctx.move_to(660, 1120); ctx.line_to(840, 1120); ctx.set_dash([14, 9]); setc(ctx, INK, c); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
        tag(ctx, "CUT", 900, 1120, INK, c, 24)

# ---- section
_rnd = random.Random(7)
FOAM_DOTS = [(_rnd.uniform(0, 1), _rnd.uniform(0, 1)) for _ in range(110)]
GRAINS = [(_rnd.uniform(0, 1), _rnd.uniform(0, 1)) for _ in range(70)]

def foam(ctx, x, y, w, h, a=1.0):
    ctx.rectangle(x, y, w, h); setc(ctx, FOAM, a); ctx.fill()
    for u, v in FOAM_DOTS:
        ctx.arc(x + u * w, y + v * h, 3.5, 0, 6.28); setc(ctx, hexc('#d8c487'), a); ctx.fill()

def zig(ctx, x, y0, y1, amp, sgn):
    """Bellows wall: two outward folds between y0 (bottom) and y1 (top)."""
    pts = []
    for i in range(5):
        y = lerp(y0, y1, i / 4)
        pts.append((x + (sgn * amp if i % 2 else 0), y))
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    return pts

def gasket(ctx, t, yd, h, zoom_grains=0.0):
    top = yd - h
    base_top = yd - 20; pocket_bot = top + 50
    bh = base_top - pocket_bot
    if bh < 180: amp = 12 + 42 * clamp((180 - bh) / 80)
    else: amp = max(3, 12 - (bh - 180) * 0.25)
    # dart into the door liner + base
    ctx.rectangle(GX - 16, yd - 2, 32, 42); fill_stroke(ctx, RUB, lw=3)
    rrect(ctx, GX - 98, base_top, 196, 22, 6); fill_stroke(ctx, RUB, lw=4)
    # hollow chamber (air) between the walls
    for sgn in (-1, 1):
        zig(ctx, GX + sgn * 88, base_top, pocket_bot, amp, sgn)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        setc(ctx, INK); ctx.set_line_width(16); ctx.stroke()
        zig(ctx, GX + sgn * 88, base_top, pocket_bot, amp, sgn)
        setc(ctx, RUB); ctx.set_line_width(9); ctx.stroke()
    # pocket + magnet strip
    rrect(ctx, GX - 100, top, 200, 52, 10); fill_stroke(ctx, RUB, lw=4)
    ctx.rectangle(GX - 82, top + 11, 164, 30); fill_stroke(ctx, RED, lw=3)
    for u, v in GRAINS:
        ctx.arc(GX - 78 + u * 156, top + 14 + v * 24, 2.2, 0, 6.28); setc(ctx, INK, 0.35 + 0.5 * zoom_grains); ctx.fill()
    return top

def section_view(ctx, t):
    yd = door_y(t); h = gasket_h(t, yd)
    # inside of the fridge (left of the wall, above the door): cold
    ctx.rectangle(0, 300, 520, yd - 300); setc(ctx, COLDT, 0.22); ctx.fill()
    la = 1 - clamp((CAM(t)[2] - 1.0) / 0.25)        # labels hide while the camera zooms on the strip
    text_c(ctx, "INSIDE · COLD", 260, 470, 30, TEAL, True, 2, la)
    text_c(ctx, "ROOM", 985, 470, 26, INK2, True, 2, la)
    # cabinet side wall: liner | foam | steel skin ; front face = steel flange
    foam(ctx, 540, 300, 315, 460)
    ctx.rectangle(520, 300, 20, 480); fill_stroke(ctx, PAPER, lw=3)
    ctx.rectangle(520, 760, 90, 20); fill_stroke(ctx, FILL3, lw=3)
    ctx.rectangle(855, 300, 25, 480); fill_stroke(ctx, STEEL, lw=3)
    ctx.rectangle(610, 760, 270, 20); fill_stroke(ctx, STEEL, lw=3)
    text_c(ctx, "CABINET", 700, 420, 28, INK2, True, 3, la)
    # door: liner on top, foam, steel skin at the bottom, rounded free edge on the right
    ctx.save(); rrect(ctx, -40, yd, DOOR_X1 + 40, 230, 22); ctx.clip()
    foam(ctx, -40, yd, DOOR_X1 + 40, 230)
    ctx.rectangle(-40, yd, DOOR_X1 + 40, 20); fill_stroke(ctx, PAPER, lw=3)
    ctx.rectangle(-40, yd + 210, DOOR_X1 + 40, 20); fill_stroke(ctx, STEEL, lw=3)
    ctx.restore()
    rrect(ctx, -40, yd, DOOR_X1 + 40, 230, 22); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "DOOR", 300, yd + 135, 30, INK2, True, 3)
    top = gasket(ctx, t, yd, h, zoom_grains=bw(t, 3))
    # cold air leaking through the gap while the door is ajar
    leak = clamp((top - YF - 10) / 40)
    if leak > 0:
        wavy_arrow(ctx, 420, top - (top - YF) / 2, 1000, top - (top - YF) / 2, t, TEAL, leak * 0.9, amp=6, wl=36, lw=4, head=11)
    sec_overlays(ctx, t, yd, top)

def sec_overlays(ctx, t, yd, top):
    a = bw(t, 2)
    if a > 0:
        highlight(ctx, GX, (top + yd) / 2, 150, (yd - top) / 2 + 30, INK, a, t)
        tag(ctx, "1 · HOLLOW RUBBER SEAL", GX - 110, yd + 290, INK, a, 28)
    a = bw(t, 4)
    if a > 0:
        highlight(ctx, 745, 770, 170, 34, STEEL_D, a, t)
        tag(ctx, "3 · STEEL FRAME", 700, 640, INK, a, 28)
        for dx in (-60, 0, 60):
            straight_arrow(ctx, GX + dx, top - 4, GX + dx, YF + 4, MUSTARD, a * sstep(t, B(4) + 0.8, 0.3), lw=6, head=10)
        tag(ctx, "PULL", 990, 905, MUSTARD, a * sstep(t, B(4) + 0.8, 0.3), 24)
    a = bw(t, 6)
    if a > 0:
        for dx in (-60, 60):
            straight_arrow(ctx, GX + dx, yd + 60, GX + dx, yd + 10, RED, a * sstep(t, B(6) + 0.6, 0.3), lw=7, head=12)
        tag(ctx, "SQUASHED · NO GAP", GX - 110, yd + 290, RED, a * sstep(t, B(6) + 1.2, 0.3), 28)
    a = bw(t, 7)
    if a > 0:
        # a sheet of paper shut in the seal, sticking out into the room, tugged to the right
        slip = 6 * sstep(t, B(7) + 1.4, 0.4)
        ctx.move_to(GX - 70 + slip, YF + 1); ctx.line_to(905 + slip, YF + 1)
        ctx.curve_to(960 + slip, YF + 2, 990 + slip, YF + 30, 1060 + slip, YF + 40)
        setc(ctx, INK, a); ctx.set_line_width(9); ctx.stroke_preserve()
        ctx.move_to(GX - 70 + slip, YF + 1)
        setc(ctx, WHITE, a); ctx.set_line_width(4)
        ctx.line_to(905 + slip, YF + 1); ctx.curve_to(960 + slip, YF + 2, 990 + slip, YF + 30, 1060 + slip, YF + 40); ctx.stroke()
        tag(ctx, "PAPER", 990, 700, INK, a, 24)
        k = a * sstep(t, B(7) + 1.2, 0.3)
        straight_arrow(ctx, 900, 880, 1050, 880, INK, k, lw=6, head=12)
        tag(ctx, "TUG", 975, 940, INK, k, 24)
        g = a * sstep(t, B(7) + 1.9, 0.3)
        for dx in (-40, 30):
            straight_arrow(ctx, GX + dx + 50, YF + 26, GX + dx, YF + 26, RED, g, lw=5, head=10)
        tag(ctx, "GRIP", GX - 110, yd + 290, RED, g, 28)
    a = bw(t, 10)
    if a > 0:
        k = a * sstep(t, B(10) + 0.5, 0.3)
        straight_arrow(ctx, 300, 760, 300, yd - 8, RED, k, lw=9, head=16)
        tag(ctx, "SHOVE FROM INSIDE", 260, 640, RED, k, 26)
        tag(ctx, "HOLDS…", 1000, yd + 290, INK, a * win(t, B(10) + 0.9, B(10) + 1.85, 0.2), 26)
        tag(ctx, "LETS GO!", GX - 110, yd + 300, TEAL, a * sstep(t, B(10) + 1.85, 0.2), 30)

# ---- beat 9: 1950s fridge with a latch
def old_view(ctx, t):
    rrect(ctx, 300, 420, 480, 1030, 110); fill_stroke(ctx, PAPER, lw=6)
    rrect(ctx, 318, 470, 444, 900, 80); fill_stroke(ctx, FILL2, lw=4)
    rrect(ctx, 330, 1385, 420, 50, 8); fill_stroke(ctx, FILL3, lw=4)
    for i in range(6):
        ctx.move_to(360 + i * 65, 1398); ctx.line_to(395 + i * 65, 1398); ctx.move_to(360 + i * 65, 1420); ctx.line_to(395 + i * 65, 1420)
    setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    for fx in (340, 740):
        ctx.rectangle(fx - 14, 1450, 28, 28); fill_stroke(ctx, INK2, lw=3)
    ctx.move_to(340, 520); ctx.line_to(740, 520); setc(ctx, STEEL); ctx.set_line_width(6); ctx.stroke()
    # lever handle (pivot on the right)
    rrect(ctx, 610, 744, 150, 34, 17); fill_stroke(ctx, STEEL, lw=4)
    ctx.arc(742, 761, 12, 0, 6.28); fill_stroke(ctx, STEEL_D, lw=3)
    tag(ctx, "LATCH HANDLE", 560, 690, INK, sstep(t, B(8) + 0.4, 0.3), 26)
    # detail circle: the latch, seen like the section (cabinet above, door below)
    a = sstep(t, B(8) + 1.0, 0.4)
    if a <= 0: return
    cx, cy, r = 870, 1090, 115
    ctx.move_to(735, 785); ctx.line_to(820, 985); ctx.set_dash([10, 8]); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    ctx.arc(cx, cy, r, 0, 6.28); fill_stroke(ctx, CREAM, lw=5, alpha=a)
    ctx.save(); ctx.arc(cx, cy, r - 3, 0, 6.28); ctx.clip()
    ctx.rectangle(cx - 130, cy - 130, 260, 80); fill_stroke(ctx, FILL3, lw=4, alpha=a)      # cabinet
    ctx.rectangle(cx + 2, cy - 52, 16, 38); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)       # bracket
    ctx.arc(cx + 10, cy - 8, 15, 0, 6.28); fill_stroke(ctx, STEEL, lw=4, alpha=a)          # striker pin
    ctx.rectangle(cx - 130, cy + 50, 260, 80); fill_stroke(ctx, FILL2, lw=4, alpha=a)      # door
    ctx.move_to(cx - 30, cy + 52); ctx.line_to(cx - 30, cy - 8)
    ctx.arc(cx + 10, cy - 8, 40, math.pi, 2 * math.pi); ctx.line_to(cx + 50, cy + 18)
    setc(ctx, INK, a); ctx.set_line_width(20); ctx.stroke_preserve(); setc(ctx, MUSTARD, a); ctx.set_line_width(12); ctx.stroke()
    ctx.restore()
    tag(ctx, "OPENS FROM OUTSIDE ONLY", 540, 360, RED, a * sstep(t, B(8) + 1.6, 0.3), 28)

# ---- beat 12: modern fridge, closed, with fridge magnets
def front_view(ctx, t):
    rrect(ctx, 300, 400, 480, 1060, 26); fill_stroke(ctx, PAPER, lw=6)
    rrect(ctx, 312, 412, 456, 1036, 20); fill_stroke(ctx, PAPER, lw=4)
    g = sstep(t, B(11) + 0.6, 0.4) * (1 - sstep(t, B(12) + 0.4, 0.4))
    if g > 0:
        rrect(ctx, 312, 412, 456, 1036, 20); ctx.set_dash([16, 10]); setc(ctx, RED, g); ctx.set_line_width(8); ctx.stroke(); ctx.set_dash([])
    rrect(ctx, 722, 560, 22, 360, 11); fill_stroke(ctx, STEEL, lw=4)
    for fx in (330, 750):
        ctx.rectangle(fx - 14, 1460, 28, 18); fill_stroke(ctx, INK2, lw=3)
    # two fridge magnets holding a note
    ctx.save(); ctx.translate(470, 700); ctx.rotate(-0.06)
    ctx.rectangle(-90, -40, 180, 220); fill_stroke(ctx, WHITE, lw=3)
    for i in range(4):
        ctx.move_to(-60, 20 + i * 36); ctx.line_to(60 - (i % 2) * 30, 20 + i * 36)
    setc(ctx, INK2); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
    ctx.arc(470, 660, 30, 0, 6.28); fill_stroke(ctx, RED, lw=4)
    rrect(ctx, 520, 1000, 110, 70, 10); fill_stroke(ctx, MUSTARD, lw=4)
    tag(ctx, "STUCK · NOT LOCKED", 540, 1250, RED, sstep(t, B(11) + 1.0, 0.3), 30)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    v = view_alphas(t)
    group(ctx, v['top'], top_view, t)
    group(ctx, v['inner'], inner_view, t)
    group(ctx, v['sec'], section_view, t)
    group(ctx, v['old'], old_view, t)
    group(ctx, v['front'], front_view, t)

CAM_KEYS = [(0, 540, 900, 1.0), (B(3) + 0.15, GX, 900, 1.8), (B(4) - 0.1, 540, 900, 1.0)]
def CAM(t):
    return cam_track(CAM_KEYS, t, 0.8)

def draw_hud(ctx, t, E):
    a = win(t, B(3) + 0.5, B(4) - 0.2, 0.3)
    tag(ctx, "2 · RUBBER + MAGNET POWDER", 540, 1430, RED, a, 30)

# ---------------------------------------------------------------- cards
def card_onesided(ctx, t, lt, a):
    card_frame(ctx, "POLES IN STRIPES", a, "ONE-SIDED PULL", RED)
    x0, y0, w, h, n = 200, 400, 680, 56, 8
    sw = w / n
    for i in range(n):
        ctx.rectangle(x0 + i * sw, y0, sw, h); setc(ctx, RED if i % 2 == 0 else TEAL, a); ctx.fill()
        text_c(ctx, "N" if i % 2 == 0 else "S", x0 + (i + 0.5) * sw, y0 + 38, 26, WHITE, True, 0, a)
    ctx.rectangle(x0, y0, w, h); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    k = sstep(lt, 0.8, 0.8)
    for i in range(n - 1):
        bx = x0 + (i + 1) * sw
        for r in (16, 30, 42):
            ctx.new_sub_path(); ctx.arc(bx, y0, r, math.pi, 2 * math.pi)
        setc(ctx, INK, a * k * 0.85); ctx.set_line_width(3); ctx.stroke()
        ctx.new_sub_path(); ctx.arc(bx, y0 + h, 9, 0, math.pi)
        ctx.set_dash([4, 4]); setc(ctx, INK2, a * k * 0.35); ctx.set_line_width(2); ctx.stroke(); ctx.set_dash([])
    tag(ctx, "FRAME SIDE · STRONG", 540, 300, RED, a * k, 24)
    text_c(ctx, "other side: almost nothing", 540, 522, 22, INK2, False, 0, a * k)

def card_law(ctx, t, lt, a):
    card_frame(ctx, "US LAW · FRIDGES FROM 1958", a, "MUST OPEN FROM INSIDE", TEAL)
    # mini top view: cabinet with the door on its right, hinge at the door's top end
    ctx.rectangle(420, 280, 200, 240); fill_stroke(ctx, PAPER, lw=4, alpha=a)
    text_c(ctx, "INSIDE", 520, 410, 22, TEAL, True, 1, a)
    k = sstep(lt, 1.6, 0.6)
    ctx.save(); ctx.translate(636, 280); ctx.rotate(-0.55 * k)          # negative: bottom end swings to the RIGHT (out)
    ctx.rectangle(-16, 0, 16, 240); fill_stroke(ctx, FILL3, lw=4, alpha=a)
    ctx.restore()
    straight_arrow(ctx, 450, 460, 600, 460, RED, a * sstep(lt, 0.8, 0.3), lw=7, head=12)
    text_c(ctx, "≤ 67 N", 820, 390, 60, INK, True, 1, a)
    text_c(ctx, "15 lb", 820, 450, 40, INK2, True, 1, a)
    text_c(ctx, "PUSH", 250, 410, 44, RED, True, 2, a)
CARDS = {'onesided': card_onesided, 'law': card_law}

SFX = [(0.85, 'click'), (1.15, 'pop'), (B(1) + 0.6, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.5, 'pop'),
       (B(4) + 0.3, 'pop'), (B(6) + 0.3, 'click'), (B(6) + 1.2, 'pop'), (B(7) + 1.2, 'pop'),
       (B(8) + 0.4, 'pop'), (B(8) + 1.6, 'pop'), (B(10) + 0.5, 'pop'), (B(10) + 1.85, 'click'), (B(11) + 1.0, 'pop')]
HUM = []
