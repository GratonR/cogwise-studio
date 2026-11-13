"""Cogwise episode: Tower cranes build themselves taller.
One idea (self-climbing / top-climbing tower crane): a climbing cage near the top of the mast holds a hydraulic
jack. The top (slewing unit + cab + jib + counter-jib + winches + counterweight) is unbolted from the mast, balanced
with the trolley, then the jack pushes it up by one section height (up to ~6 m / 20 ft). A new mast section, placed
on the cage's rail by the crane's own hook, rolls into the gap; it is bolted to the mast below and to the top above.

VIEW: side elevation of a flat-top crane, building on the LEFT, jib pointing LEFT over it, counter-jib RIGHT.
Screen y grows DOWN: "up" = smaller y. Jack: barrel fixed to the cage (moves up with the top), rod extends DOWN
onto a step (lug beam) on the mast -> extending the rod lifts cage + top. Cage is open on its LEFT side (rail side).
Balance card: seesaw angle theta = K * (counter-jib moment - jib moment); cairo rotate(+theta) = clockwise on screen
= RIGHT end goes DOWN, i.e. counterweight side heavier -> right end down. Balanced -> level.
"""
import math, cairo
from cogwise.style import *

META = dict(
    slug="tower-crane",
    title="Tower cranes build themselves taller 🏗️ #Shorts",
    description=("Nobody brings a bigger crane: a tower crane jacks up its own top and slides a new piece of tower underneath.\n\n"
                 "#Shorts #howthingswork #crane #construction #engineering #cogwise"),
    hashtags=["Shorts", "howthingswork", "crane", "construction", "engineering", "cogwise"],
    sources=[
        "https://medium.com/@ILMM_Magazine/how-a-tower-crane-works-ilmm-cff390300a58",
        "https://www.scienceabc.com/innovation/how-do-tower-cranes-work.html",
        "https://buildermuse.com/commercial/how-a-tower-crane-climbs-cost-per-month-crew/",
        "https://cranepedia.com/wikipedia/how-tower-crane-work/",
    ],
)

BEATS = [
    dict(dur=4.8, title="BUILT BY ITSELF", caption="Nobody brings a bigger crane. Tower cranes build themselves taller."),
    dict(dur=6.0, title="THE SECRET", caption="It lifts its own head and slides a new piece of tower underneath."),
    dict(dur=6.4, title="1 · THE CAGE", caption="Near the top, a steel cage hugs the tower, with a hydraulic jack inside."),
    dict(dur=5.6, title="UNBOLTED", caption="Workers unbolt the top. Now everything above rests on one jack."),
    dict(dur=6.2, title=None, caption="So it must balance: the trolley rolls out until both arms even out.", card='balance'),
    dict(dur=6.2, title="2 · THE PUSH", caption="Then the jack pushes the whole top upward: cab, arm, motors, counterweight."),
    dict(dur=6.8, title=None, caption="A gap opens in the cage, one section tall: up to six metres, twenty feet.", card='gap'),
    dict(dur=6.2, title="3 · NEW SECTION", caption="The next section waits on a rail, lifted there by the crane's own hook."),
    dict(dur=5.8, title="BOLTED IN", caption="It rolls into the gap, and the top is bolted back onto it."),
    dict(dur=6.4, title="CLIMBING", caption="Section by section, the crane climbs with the building it's helping to build."),
    dict(dur=6.6, title="IT CLIMBED", caption="So that crane didn't arrive that tall. It climbed there, one piece at a time."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
GROUND = 1480
MX, MW = 600, 34          # mast centre x, half width
SH = 100                  # one mast section (drawn)
N0 = 6                    # sections at t=0
RAIL_X = MX - 230         # where the new section waits on the rail (centre x)
BLD_X0, BLD_X1 = 95, 360

CRANE = hexc('#f4ecd8'); CRANE_D = hexc('#d9cdb0')
CAGE = MUSTARD; JACK = RED; NEWC = TEAL
CONC = hexc('#cfc6b4'); CONC_D = hexc('#a99f8c'); GLASS = hexc('#9cc9c4')

# climbing cycles: (push0, push1, slide0, slide1, overshoot)
CYCLES = [
    (0.35, 1.45, 1.55, 2.45, 8),                                   # beat 1: the answer, fast
    (B(1) + 0.7, B(1) + 2.2, B(1) + 2.5, B(1) + 3.9, 8),           # beat 2: preview
    (B(5) + 0.5, B(5) + 4.6, B(8) + 0.3, B(8) + 2.4, 10),          # beats 6-9: the slow, explained cycle
    (B(9) + 0.3, B(9) + 1.3, B(9) + 1.4, B(9) + 2.4, 8),           # beat 10: climbing with the building
    (B(9) + 3.2, B(9) + 4.2, B(9) + 4.3, B(9) + 5.3, 8),
]
SETTLE = 0.55
MAIN = 2

def climb(t):
    """-> n (installed sections), gap (px between mast top and the underside of the top), active cycle info."""
    n = N0; gap = 0.0; act = None
    for i, (p0, p1, s0, s1, os_) in enumerate(CYCLES):
        if t >= s1 + SETTLE: n += 1; continue
        if t < p0 - 0.6: break
        u_push = ease((t - p0) / (p1 - p0)) if t > p0 else 0.0
        gap = (SH + os_) * u_push
        if t > s1: gap = lerp(SH + os_, SH, ease((t - s1) / SETTLE))
        u_slide = ease((t - s0) / (s1 - s0)) if t > s0 else 0.0
        act = dict(i=i, slide=u_slide, os=os_, landed=t > s1 + 0.2)
        break
    return n, gap, act

def tops(t):
    n, gap, act = climb(t)
    mtop = GROUND - n * SH
    sy = mtop - gap                       # underside of the slewing unit
    return n, gap, act, mtop, sy

def trolley_x(t):
    x = MX - 300
    x = lerp(x, MX - 180, ease((t - B(3)) / 1.0))                 # parked in before balancing
    x = lerp(x, MX - 360, ease((t - B(4) - 0.5) / 3.0))           # rolls out until balanced (beat 5)
    x = lerp(x, RAIL_X, ease((t - B(7) + 0.2) / 0.9))             # above the rail (beat 8)
    x = lerp(x, MX - 330, ease((t - B(8) - 2.6) / 1.5))
    return x

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['cage'] = bw(t, 2)
    s['jack'] = max(bw(t, 2), bw(t, 5))
    s['unbolt'] = clamp((t - B(3) - 0.6) / 1.2) if t < B(8) + 2.6 else 0.0   # 0 = bolted, 1 = all bolts out
    s['rest'] = bw(t, 3)
    s['parts'] = bw(t, 5)
    s['push_arrow'] = win(t, B(5) + 0.4, CYCLES[MAIN][1] + 0.2, 0.3)
    s['gapdim'] = bw(t, 6)
    s['hook'] = clamp((t - B(7) - 0.3) / 2.4) if B(7) - 0.5 < t < B(8) else (1.0 if t >= B(8) else 0.0)
    s['newsec'] = bw(t, 7, 9)
    s['bolts_in'] = clamp((t - (CYCLES[MAIN][3] + SETTLE)) / 0.8)
    s['bolted'] = bw(t, 8)
    s['ghost'] = bw(t, 9, 11)
    s['recap'] = bw(t, 10)
    s['answer'] = win(t, 0.3, B(1), 0.3)
    return s

# ---------------------------------------------------------------- drawing helpers
def lattice(ctx, x0, y0, x1, y1, fill, a=1.0, lw=4, diag=True):
    """vertical lattice box (one mast section) from (x0,y0) top-left to (x1,y1)."""
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); setc(ctx, fill, 0.35 * a); ctx.fill()
    ctx.move_to(x0, y0); ctx.line_to(x0, y1); ctx.move_to(x1, y0); ctx.line_to(x1, y1)
    setc(ctx, INK, a); ctx.set_line_width(lw + 2); ctx.stroke()
    ctx.move_to(x0, y0); ctx.line_to(x1, y0); ctx.move_to(x0, y1); ctx.line_to(x1, y1)
    if diag:
        h = y1 - y0
        ctx.move_to(x0, y1); ctx.line_to(x1, y0 + h / 2); ctx.line_to(x0, y0)
    setc(ctx, INK, a); ctx.set_line_width(lw); ctx.stroke()

def bolt(ctx, x, y, a, col=INK):
    if a <= 0: return
    ctx.arc(x, y, 7, 0, 2 * math.pi); setc(ctx, col, a); ctx.fill()

def h_truss(ctx, x0, x1, y, h, fill, a=1.0):
    """horizontal triangular truss (jib) from x0 to x1 (x0 < x1), top chord at y, bottom chord at y+h."""
    ctx.rectangle(x0, y, x1 - x0, h); setc(ctx, fill, 0.35 * a); ctx.fill()
    ctx.move_to(x0, y); ctx.line_to(x1, y); ctx.move_to(x0, y + h); ctx.line_to(x1, y + h)
    setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    n = max(1, int((x1 - x0) / 40))
    for i in range(n):
        xa = lerp(x0, x1, i / n); xb = lerp(x0, x1, (i + 0.5) / n); xc = lerp(x0, x1, (i + 1) / n)
        ctx.move_to(xa, y + h); ctx.line_to(xb, y); ctx.line_to(xc, y + h)
    setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()

# ---------------------------------------------------------------- scene parts
def draw_building(ctx, t, sy):
    top = min(GROUND - 260, sy + 270)
    ctx.rectangle(BLD_X0, top, BLD_X1 - BLD_X0, GROUND - top); fill_stroke(ctx, CONC, lw=5)
    # floors and windows from the ground up (new floors appear at the top)
    y = GROUND
    while y - 70 >= top:
        ctx.move_to(BLD_X0, y - 70); ctx.line_to(BLD_X1, y - 70); setc(ctx, CONC_D); ctx.set_line_width(3); ctx.stroke()
        for k in range(4):
            ctx.rectangle(BLD_X0 + 22 + k * 62, y - 55, 36, 38); fill_stroke(ctx, GLASS, lw=2.5)
        y -= 70
    # rebar sticking out of the slab being built
    for k in range(6):
        xx = BLD_X0 + 20 + k * 46
        ctx.move_to(xx, top); ctx.line_to(xx, top - 26); setc(ctx, INK2); ctx.set_line_width(3); ctx.stroke()

def draw_mast(ctx, t, n, mtop, s, glow_last=False):
    ctx.rectangle(MX - 90, GROUND - 10, 180, 30); fill_stroke(ctx, FILL3, lw=4)          # foundation
    for k in range(n):
        y1 = GROUND - k * SH; y0 = y1 - SH
        lattice(ctx, MX - MW, y0, MX + MW, y1, CRANE_D)
        bolt(ctx, MX - MW, y1, 1); bolt(ctx, MX + MW, y1, 1)

def draw_top(ctx, t, s, sy):
    """slewing unit + cab + jib + counter-jib + winch + counterweight, all hanging on the underside sy."""
    # slewing unit (turntable)
    rrect(ctx, MX - 62, sy - 44, 124, 44, 6); fill_stroke(ctx, CRANE, lw=5)
    ctx.move_to(MX - 62, sy - 22); ctx.line_to(MX + 62, sy - 22); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    jy = sy - 44 - 38                       # jib top chord
    # counter-jib (right) + winch + counterweight blocks
    h_truss(ctx, MX + 40, MX + 300, jy + 6, 32, CRANE_D)
    rrect(ctx, MX + 110, jy - 30, 70, 36, 5); fill_stroke(ctx, INK2, lw=4)                 # hoist winch
    ctx.arc(MX + 145, jy - 12, 12, 0, 2 * math.pi); fill_stroke(ctx, CRANE, lw=3)
    for k in range(3):
        rrect(ctx, MX + 222 + k * 24, jy + 38, 22, 82, 3); fill_stroke(ctx, CONC_D, lw=3.5)   # counterweight
    # jib (left)
    h_truss(ctx, MX - 520, MX + 40, jy, 38, CRANE)
    # cab on the jib side
    rrect(ctx, MX - 128, sy - 92, 64, 70, 8); fill_stroke(ctx, CRANE, lw=5)
    rrect(ctx, MX - 122, sy - 84, 34, 36, 4); fill_stroke(ctx, GLASS, lw=3)
    return jy

def draw_cage(ctx, t, s, sy, mtop):
    """climbing cage: mustard frame around the top of the mast, open on the LEFT above the rail."""
    x0, x1 = MX - MW - 24, MX + MW + 24
    y0, y1 = sy, sy + 2.4 * SH
    rail = sy + SH                      # rail level = bottom of the opening
    hl = s['cage']
    col = CAGE
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); setc(ctx, col, 0.18 + 0.12 * hl); ctx.fill()
    # right side: full posts + diagonals
    ctx.move_to(x1, y0); ctx.line_to(x1, y1)
    ctx.move_to(x1 - 10, y0 + 10); ctx.line_to(x1 - 10, y1)
    # left side: post only BELOW the rail (the opening is above it)
    ctx.move_to(x0, rail); ctx.line_to(x0, y1)
    # top, rail level, bottom beams
    ctx.move_to(x0, y0); ctx.line_to(x1, y0)
    ctx.move_to(x0, y1); ctx.line_to(x1, y1)
    setc(ctx, lerpc(col, INK, 0.25)); ctx.set_line_width(9); ctx.stroke()
    # guide rail sticking out to the left, at the rail level
    rrect(ctx, RAIL_X - 70, rail, x0 - (RAIL_X - 70) + 8, 14, 3); fill_stroke(ctx, col, lw=4)
    ctx.move_to(RAIL_X - 50, rail + 14); ctx.line_to(x0, rail + 70); setc(ctx, lerpc(col, INK, 0.25)); ctx.set_line_width(6); ctx.stroke()
    return rail

def draw_jack(ctx, t, s, sy, mtop):
    """barrel fixed to the cage (right side, inside), rod pushes DOWN on a step of the mast."""
    jx = MX + MW + 12
    foot = mtop + 1.4 * SH              # step on the mast (fixed to the mast)
    b0, b1 = sy + 20, sy + 100          # barrel (moves with the cage)
    glow = s['jack']
    col = lerpc(JACK, ORANGE, 0.4 * glow * (0.5 + 0.5 * math.sin(t * 6)))
    # step beam on the mast
    ctx.rectangle(MX - MW - 6, foot, 2 * MW + 30, 12); fill_stroke(ctx, INK2, lw=3)
    # rod
    ctx.rectangle(jx - 5, b1, 10, max(0, foot - b1)); fill_stroke(ctx, hexc('#c9c2b2'), lw=3)
    # barrel
    rrect(ctx, jx - 12, b0, 24, b1 - b0, 5); fill_stroke(ctx, col, lw=4)
    return jx, b0, foot

def draw_section_on_rail(ctx, t, s, act, rail, jy, tx):
    """new section: on the rail (left of the mast) then rolling into the gap. Main cycle: lowered by the hook first."""
    if act is None: return None
    i = act['i']
    if i == MAIN:
        if t < B(7) - 0.3: return None
        drop = (1 - ease(s['hook'])) * 300                       # hanging higher, lowered onto the rail
        a = clamp((t - B(7) + 0.3) / 0.4)
    else:
        p0 = CYCLES[i][0]
        drop = 0; a = clamp((t - p0 + 0.6) / 0.4)
    x = lerp(RAIL_X, MX, act['slide'])
    y1 = rail - drop; y0 = y1 - SH
    lattice(ctx, x - MW, y0, x + MW, y1, NEWC, a)
    # little wheels on the rail
    if act['slide'] < 0.98 and drop < 1:
        for dx in (-MW + 8, MW - 8):
            ctx.arc(x + dx, y1 - 2, 6, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()
    # hook cable while the main section is being placed
    if i == MAIN and t < B(8) + 0.1:
        ca = clamp((B(8) + 0.1 - t) / 0.4)
        ctx.move_to(tx, jy + 38); ctx.line_to(x, y0 - 30); setc(ctx, INK, a * ca); ctx.set_line_width(3); ctx.stroke()
        ctx.move_to(x, y0 - 30); ctx.line_to(x - MW, y0); ctx.move_to(x, y0 - 30); ctx.line_to(x + MW, y0)
        ctx.set_line_width(2.5); ctx.stroke()
        ctx.arc(x, y0 - 34, 8, 0, 2 * math.pi); setc(ctx, MUSTARD, a * ca); ctx.fill()
    return x, y0, y1

def draw_trolley(ctx, t, jy, tx, busy):
    rrect(ctx, tx - 26, jy + 38, 52, 18, 4); fill_stroke(ctx, INK2, lw=3)
    if not busy:
        L = 150
        ctx.move_to(tx, jy + 56); ctx.line_to(tx, jy + 56 + L); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(tx, jy + 56 + L + 8, 9, 0, 2 * math.pi); fill_stroke(ctx, MUSTARD, lw=3)

def draw(ctx, t, E):
    s = state(t)
    n, gap, act, mtop, sy = tops(t)
    draw_building(ctx, t, sy)
    a = s['ghost']
    if a > 0:      # height on day one
        y = GROUND - N0 * SH - 44 - 38
        ctx.move_to(40, y); ctx.line_to(1040, y); setc(ctx, INK2, a); ctx.set_dash([14, 10]); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
        tag(ctx, "DAY 1", 960, y, INK2, a, 22)
    draw_mast(ctx, t, n, mtop, s)
    jx, b0, foot = draw_jack(ctx, t, s, sy, mtop)
    rail = draw_cage(ctx, t, s, sy, mtop)
    jy = draw_top(ctx, t, s, sy)
    tx = trolley_x(t)
    busy = act is not None and act['i'] == MAIN and B(7) - 0.3 < t < B(8) + 0.1
    draw_trolley(ctx, t, jy, tx, busy)
    sec = draw_section_on_rail(ctx, t, s, act, rail, jy, tx)
    # bolts between the mast top and the slewing unit (4 shown: 2 per side)
    ub = s['unbolt']
    for k, (bx, dy) in enumerate(((MX - MW, 0), (MX + MW, 0), (MX - MW + 14, 0), (MX + MW - 14, 0))):
        aa = 1 - clamp(ub * 4 - k)
        if aa > 0:
            bolt(ctx, bx, sy - 2, aa, RED if s['rest'] > 0 else INK)
        elif s['rest'] > 0:
            ctx.move_to(bx - 7, sy - 32 - k * 4); ctx.line_to(bx + 7, sy - 18 - k * 4)     # bolt flying off
            ctx.move_to(bx + 7, sy - 32 - k * 4); ctx.line_to(bx - 7, sy - 18 - k * 4)
            setc(ctx, RED, s['rest'] * 0.6); ctx.set_line_width(3); ctx.stroke()
    # bolts appearing on the new section (top + bottom)
    bi = s['bolts_in'] * s['bolted']
    if bi > 0:
        for (bx, by) in ((MX - MW, mtop + SH), (MX + MW, mtop + SH), (MX - MW, sy), (MX + MW, sy)):
            ctx.arc(bx, by, 7 + 10 * (1 - bi), 0, 2 * math.pi); setc(ctx, RED, bi); ctx.fill()
    overlays(ctx, t, s, n, gap, mtop, sy, jy, tx, jx, b0, foot, rail, sec)

def overlays(ctx, t, s, n, gap, mtop, sy, jy, tx, jx, b0, foot, rail, sec):
    a = s['answer']
    if a > 0:
        straight_arrow(ctx, MX + 150, sy + 40, MX + 150, sy - 70, RED, a, lw=8, head=16)
        tag(ctx, "+1 PIECE OF TOWER", MX + 200, sy + 150, RED, a, 26)
    a = s['cage']
    if a > 0:
        highlight(ctx, MX, sy + 1.2 * SH, 120, 1.5 * SH, MUSTARD, a, t)
        tag(ctx, "1 · CLIMBING CAGE", MX - 180, sy + 2.2 * SH, INK, a, 22)
        tag(ctx, "HYDRAULIC JACK", jx + 120, b0 + 40, RED, a, 20)
        ctx.move_to(jx + 38, b0 + 40); ctx.line_to(jx + 14, b0 + 40); setc(ctx, RED, a); ctx.set_line_width(3); ctx.stroke()
    a = s['rest']
    if a > 0:
        tag(ctx, "BOLTS OUT", MX - 170, sy - 10, RED, a, 22)
        tag(ctx, "TOP RESTS ON THE JACK", jx + 90, foot + 50, RED, a, 20)
        straight_arrow(ctx, jx + 40, b0 - 70, jx + 40, b0 - 6, INK, a, lw=5, head=10)    # weight down onto the jack
    a = s['parts']
    if a > 0:
        tag(ctx, "CAB", MX - 96, sy - 128, INK, a, 20)
        tag(ctx, "ARM", MX - 380, jy - 30, INK, a, 20)
        tag(ctx, "MOTORS", MX + 145, jy - 62, INK, a, 20)
        tag(ctx, "COUNTERWEIGHT", MX + 240, jy + 150, INK, a, 20)
    a = s['push_arrow']
    if a > 0:
        straight_arrow(ctx, jx + 40, b0 + 90, jx + 40, b0 - 40, RED, a, lw=8, head=16)    # jack pushes the top UP
        straight_arrow(ctx, MX - 10, sy - 140, MX - 10, sy - 230, RED, a * 0.8, lw=7, head=14)
    a = s['gapdim']
    if a > 0 and gap > 20:
        xd = MX + MW + 60
        ctx.rectangle(MX - MW, sy, 2 * MW, mtop - sy); setc(ctx, RED, 0.18 * a); ctx.fill()
        straight_arrow(ctx, xd, (sy + mtop) / 2, xd, sy + 3, RED, a, lw=4, head=9)
        straight_arrow(ctx, xd, (sy + mtop) / 2, xd, mtop - 3, RED, a, lw=4, head=9)
        tag(ctx, "GAP", MX, (sy + mtop) / 2, RED, a, 22)
    a = s['newsec']
    if a > 0 and sec:
        x, y0, y1 = sec
        if t > B(8): tag(ctx, "3 · NEW SECTION", x - 70, y1 + 90, TEAL, a, 22)
        else:
            tag(ctx, "3 · NEW SECTION", x - 20, rail + 110, TEAL, a, 22)
            tag(ctx, "RAIL", RAIL_X - 60, rail + 46, INK, a, 18)
    a = s['bolted'] * s['bolts_in']
    if a > 0:
        tag(ctx, "BOLTED", MX - 160, (sy + mtop) / 2, RED, a, 22)
    a = s['recap']
    if a > 0:
        tag(ctx, "1 · CAGE", MX - 200, sy + 2 * SH, INK, a, 20)
        tag(ctx, "2 · PUSH", MX + 200, sy + 30, RED, a, 20)
        tag(ctx, "3 · NEW SECTION", MX + 230, mtop + 2.8 * SH, TEAL, a, 20)
        tag(ctx, "TODAY", 960, jy - 4, INK, a, 22)

def draw_set(ctx):
    pass

CAMKEYS = [(0, 560, 980, 0.95),
           (B(1) + 0.2, 570, 760, 1.5),
           (B(2), 580, 720, 1.65),
           (B(3), 610, 690, 1.55),
           (B(5) + 0.1, 620, 620, 1.15),
           (B(7), 520, 660, 1.45),
           (B(8), 590, 640, 1.65),
           (B(9), 540, 860, 0.9),
           (B(10), 540, 860, 0.92)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)
ANCHOR = (560, 1350)


SFX = [(0.4, 'pop'), (B(1) + 0.4, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.7, 'click'), (B(5) + 0.3, 'pop'),
       (B(7) + 0.3, 'pop'), (B(8) + 2.5, 'click'), (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_balance(ctx, t, lt, a):
    card_frame(ctx, "BALANCE ON ONE JACK", a, "BOTH ARMS EVEN = SAFE TO PUSH", TEAL)
    px, py = 540, 420
    r = lerp(0.3, 0.75, ease((lt - 0.5) / 3.0))           # trolley reach (0..1 of the jib)
    m_cw = 0.6; m_tr = 0.8 * r                            # counterweight moment (right) vs trolley moment (left)
    theta = 0.14 * (m_cw - m_tr) / 0.6                    # +theta = clockwise on screen = right end DOWN
    # pivot (the jack) under the beam
    ctx.move_to(px, py + 8); ctx.line_to(px - 34, py + 92); ctx.line_to(px + 34, py + 92); ctx.close_path()
    fill_stroke(ctx, JACK, lw=4, alpha=a)
    ctx.save(); ctx.translate(px, py); ctx.rotate(theta)
    L, R = 380, 230
    ctx.rectangle(-L, -14, L + R, 22); fill_stroke(ctx, CRANE, lw=4, alpha=a)
    # counterweight on the right end
    rrect(ctx, R - 60, 8, 54, 70, 4); fill_stroke(ctx, CONC_D, lw=4, alpha=a)
    text_c(ctx, "COUNTERWEIGHT", R - 34, 104, 16, INK2, True, 1, a)
    # trolley + hook on the left arm
    tx = -L * r
    rrect(ctx, tx - 26, 8, 52, 16, 4); fill_stroke(ctx, INK2, lw=3, alpha=a)
    ctx.move_to(tx, 24); ctx.line_to(tx, 70); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(tx, 78, 9, 0, 2 * math.pi); fill_stroke(ctx, MUSTARD, lw=3, alpha=a)
    if lt > 0.6 and r < 0.74: straight_arrow(ctx, tx - 34, -36, tx - 110, -36, TEAL, a, lw=5, head=10)
    text_c(ctx, "TROLLEY", tx, -48 if r >= 0.74 else -62, 16, TEAL, True, 1, a)
    ctx.restore()
    # level gauge: needle hangs straight down when balanced
    gx, gy = 870, 330
    ctx.arc(gx, gy, 46, math.pi * 0.15, math.pi * 0.85); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(gx, gy); ctx.line_to(gx + 46 * math.sin(theta * 4), gy + 46 * math.cos(theta * 4))   # leans toward the heavy (lower) side
    ok = abs(theta) < 0.01
    setc(ctx, TEAL if ok else RED, a); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "LEVEL" if ok else "TILTED", gx, gy + 76, 18, TEAL if ok else RED, True, 1, a)

def card_gap(ctx, t, lt, a):
    card_frame(ctx, "THE GAP IN THE CAGE", a, "ONE SECTION · UP TO 6 m · 20 ft", RED)
    cx, sh = 420, 78
    mt = 400                              # mast top (fixed)
    g = sh * ease((lt - 0.3) / 1.2)
    st = mt - g                           # underside of the lifted top
    ctx.save(); ctx.rectangle(110, 244, 860, 300); ctx.clip()
    for k in range(3):
        lattice(ctx, cx - 34, mt + k * sh, cx + 34, mt + (k + 1) * sh, CRANE_D, a)
    # cage (moves with the top), open on the LEFT above the rail level
    ctx.rectangle(cx - 58, st, 116, 2.4 * sh); setc(ctx, CAGE, 0.2 * a); ctx.fill()
    ctx.move_to(cx + 58, st); ctx.line_to(cx + 58, st + 2.4 * sh)
    ctx.move_to(cx - 58, st + sh); ctx.line_to(cx - 58, st + 2.4 * sh)
    ctx.move_to(cx - 58, st); ctx.line_to(cx + 58, st)
    setc(ctx, CAGE, a); ctx.set_line_width(8); ctx.stroke()
    # top block above
    rrect(ctx, cx - 74, st - 36, 148, 36, 6); fill_stroke(ctx, CRANE, lw=4, alpha=a)
    text_c(ctx, "TOP", cx, st - 11, 18, INK, True, 1, a)
    # the gap
    if g > 4:
        ctx.rectangle(cx - 34, st, 68, g); setc(ctx, RED, 0.25 * a); ctx.fill()
    ctx.restore()
    if g > 30:
        xd = cx + 110
        ctx.move_to(xd - 14, st); ctx.line_to(xd + 14, st); ctx.move_to(xd - 14, mt); ctx.line_to(xd + 14, mt)
        setc(ctx, RED, a); ctx.set_line_width(3); ctx.stroke()
        straight_arrow(ctx, xd, st + g / 2, xd, st + 3, RED, a, lw=4, head=8)
        straight_arrow(ctx, xd, st + g / 2, xd, mt - 3, RED, a, lw=4, head=8)
        text_c(ctx, "GAP", xd + 130, st + g / 2 - 4, 30, RED, True, 1, a)
        text_c(ctx, "6 m · 20 ft", xd + 130, st + g / 2 + 30, 24, INK, True, 1, a)
        straight_arrow(ctx, xd + 220, mt - 4, xd + 220, mt - 70, RED, a * 0.0, lw=1, head=1)

CARDS = {'balance': card_balance, 'gap': card_gap}
