"""Cogwise episode: Your dishwasher eats salt, but your plates never see it.
One idea: dishwasher salt never touches the dishes. It only RECHARGES the built-in water softener (a cartridge of
ion-exchange resin beads). Hard water passes through the beads, which trade calcium/magnesium for sodium. Every few
washes the beads are full; a regeneration valve sends water into the salt box, the brine floods the beads, sodium
pushes the limestone off, and that salty, chalky water is pumped down the drain.

VIEW (screen coordinates, y grows DOWN): FRONT cut-away of a dishwasher.
  - tub y 420-1000 with two racks; the salt box CAP sits in the tub floor (x 510), under the lower rack.
  - base zone y 1012-1450 (cut away):
      SALT BOX  x 420-600, y 1012-1152 (salt crystals at the bottom).
      RESIN     cartridge x 220-340, y 1050-1250 (beads).
      INLET     hose comes from OUTSIDE on the RIGHT at y 1230 -> INLET VALVE (850, 1230) -> LEFT along y 1230
                -> enters the resin at its lower right (340, 1230) -> water rises UP through the beads -> leaves the
                top (280, 1050) -> up into the tub floor (280, 1000).
      REGEN VALVE (760, 1140): branch rising from the inlet line at x 760 -> valve -> up to y 1050 -> LEFT into the
                salt box (600, 1050).
      BRINE     leaves the salt box on its LEFT (420, 1110) -> LEFT into the upper resin (340, 1110) -> flows DOWN
                through the beads -> resin bottom (280, 1250) -> down to the DRAIN PUMP (280, 1360) -> drain hose
                out through the LEFT wall (y 1360).
    No pipe crosses another.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="dishwasher-salt",
    title="Your dishwasher eats salt, but your plates never see it 🧂 #Shorts",
    description=("Not one grain touches your dishes. It resets a hidden water softener.\n\n"
                 "#Shorts #howthingswork #dishwasher #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "dishwasher", "appliances", "cogwise"],
    sources=[
        "https://manuals.online/electrolux/dishwasher/evolution/user-manual/21pr5",
        "https://www.which.co.uk/reviews/dishwashers/article/dishwasher-salt-and-rinse-aid-explained",
        "https://automaticwasher.org/threads/dishwasher-in-what-part-of-the-cycle-does-yours-regenerate-it-s-water-softener.32913",
    ],
)

BEATS = [
    dict(dur=4.8, title="EATS SALT", caption="Your dishwasher eats salt, but your plates never see it."),
    dict(dur=6.2, title="THE SECRET", caption="Not one grain touches your dishes. It feeds a tiny water softener under the tub."),
    dict(dur=4.6, title="HARD WATER", caption="Your tap water carries dissolved limestone, mostly calcium and magnesium."),
    dict(dur=5.2, title=None, caption="Heated in your dishwasher, it becomes the white film on your glasses.", card='glass'),
    dict(dur=6.0, title="1 · THE RESIN", caption="So before every wash, the water flows through a cartridge of tiny plastic beads."),
    dict(dur=5.2, title=None, caption="The beads grab the calcium and magnesium, and let go of sodium instead.", card='bead'),
    dict(dur=4.8, title="SATURATED", caption="After a few washes, every single bead is clogged with limestone."),
    dict(dur=6.0, title="2 · THE SALT BOX", caption="That's when the salt comes in. A valve sends water into the salt box."),
    dict(dur=5.6, title="BRINE", caption="Out comes very salty water, called brine, and it rushes through the beads."),
    dict(dur=5.6, title="RESET", caption="So much sodium pushes the limestone off, and the beads are fresh again."),
    dict(dur=4.8, title="3 · THE DRAIN", caption="Then that salty, chalky water is pumped straight down the drain."),
    dict(dur=6.2, title="SALT = RESET", caption="So the salt never cleans a thing. It's just the reset button for the beads."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

WATER = hexc('#5aa9e6'); WATER_D = hexc('#2f6fb3')
STEEL = hexc('#b9c0c6'); STEEL_D = hexc('#7d858c')
COPPER = hexc('#c46d2e')
BEAD_FRESH = hexc('#e8a84a'); BEAD_FRESH_D = hexc('#a8661c')
CHALK = hexc('#f6f4ee'); CHALK_D = hexc('#a9a49a')
BRINE = hexc('#f2b134'); BRINE_D = hexc('#b07a12')
SALT_C = hexc('#ffffff'); NA_C = hexc('#3d7fd1')

# ---------------------------------------------------------------- geometry
CX0, CX1, CY0, CY1 = 170, 910, 360, 1460
TX0, TX1, TY0, TY1 = 215, 865, 420, 1000
SX0, SX1, SY0, SY1 = 420, 600, 1012, 1152           # salt box
CAP_X = 510
RX0, RX1, RY0, RY1 = 220, 340, 1050, 1250           # resin cartridge
RCX = (RX0 + RX1) / 2
IN_Y = 1230
V1 = (850, IN_Y)                                    # inlet valve
V2 = (760, 1140)                                    # regeneration valve
BR_Y = 1110                                         # brine pipe height
PUMP = (280, 1360, 46)

# beads: grid inside the resin
BEADS = []
_rnd = random.Random(11)
for row in range(10):
    for col in range(5):
        x = RX0 + 18 + col * 21 + (10 if row % 2 else 0) * 0.5
        y = RY0 + 18 + row * 19.5
        r = (y - RY0) / (RY1 - RY0)                 # 0 top .. 1 bottom
        BEADS.append((x, y, r, _rnd.random()))

def path_pt(pts, u):
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L)
    d = clamp(u) * tot
    for i, l in enumerate(L):
        if d <= l or i == len(L) - 1:
            k = d / l if l else 0
            return lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)
        d -= l

P_WASH = [(CX1 + 60, IN_Y), (RX1, IN_Y), (RCX, IN_Y), (RCX, RY0), (RCX, TY1 - 14)]
P_REGEN = [(CX1 + 60, IN_Y), (V2[0], IN_Y), (V2[0], 1050), (SX1, 1050)]
P_BRINE = [(SX0, BR_Y), (RX1, BR_Y), (RCX, BR_Y), (RCX, RY1)]
P_DRAIN = [(RCX, RY1), (RCX, PUMP[1]), (CX0 - 50, PUMP[1])]

def state(t):
    s = {}
    # main wash flow (hard water in, soft water out) during beats 3-7, plus a hint in beat 2
    s['wash'] = max(win(t, B(1) + 0.8, B(2), 0.3) * 0.6, win(t, B(2) + 0.1, B(7), 0.4))
    # saturation: a few beads at the bottom go white during 5-6, all of them in beat 7
    s['sat'] = 0.18 * sstep(t, B(4) + 1.0, 3.0) + 0.95 * sstep(t, B(6) + 0.2, 3.6)
    # regeneration valve / water into salt box (beat 8)
    s['v2'] = sstep(t, B(7) + 2.6, 0.3) * (1 - sstep(t, B(9) - 0.2, 0.4))   # inflow pushes the brine out
    s['saltwater'] = sstep(t, B(7) + 2.9, 2.5)
    # brine flows from the salt box into the resin (beats 9-10)
    s['brine'] = win(t, B(8) + 0.2, B(10) + 0.4, 0.4)
    s['brine_front'] = sstep(t, B(8) + 0.6, 3.6)        # how far down the brine has soaked
    s['reset'] = 1.15 * sstep(t, B(9) + 0.3, 4.0)        # fresh front (top -> bottom)
    s['drain'] = win(t, B(10) + 0.1, B(11) + 0.2, 0.3)
    s['salt_level'] = 1 - 0.18 * sstep(t, B(8) + 0.4, 6)
    return s

def bead_state(b, s, t):
    """returns 0 = fresh (amber), 1 = clogged (chalk)"""
    x, y, r, rk = b
    if t >= B(9):
        return 0.0 if (r * 0.85 + rk * 0.15) < s['reset'] else 1.0
    score = (1 - r) * 0.75 + rk * 0.25                 # bottom beads (water enters low) clog first
    return 1.0 if score < s['sat'] else 0.0

CAMKEYS = [(0, 540, 900, 1.0), (B(2) + 0.1, 600, 1180, 1.4), (B(4) + 0.1, 470, 1170, 1.7),
           (B(7) + 0.1, 560, 1150, 1.5), (B(8) + 0.1, 420, 1150, 1.7), (B(10) + 0.1, 470, 1230, 1.5),
           (B(11) + 0.1, 540, 900, 1.0)]

# ---------------------------------------------------------------- drawing pieces
def pipe(ctx, pts, col=FILL3, w=16):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    setc(ctx, INK); ctx.set_line_width(w + 7); ctx.stroke_preserve()
    setc(ctx, col); ctx.set_line_width(w); ctx.stroke()

def dots(ctx, t, pts, a, color, edge, speed=0.9, n=7, r=5.5, specks=False):
    if a <= 0.03: return
    for i in range(n):
        u = (t * speed + i / n) % 1
        x, y = path_pt(pts, u)
        ctx.arc(x, y, r, 0, 6.28); setc(ctx, color, a); ctx.fill_preserve()
        setc(ctx, edge, a); ctx.set_line_width(1.5); ctx.stroke()
        if specks:
            ctx.arc(x + 2, y - 1.5, 2.2, 0, 6.28); setc(ctx, CHALK, a); ctx.fill()

def cabinet(ctx):
    rrect(ctx, CX0, CY0, CX1 - CX0, CY1 - CY0, 20); fill_stroke(ctx, PAPER, lw=6)
    rrect(ctx, CX0, CY0, CX1 - CX0, 62, 18); fill_stroke(ctx, FILL3, lw=4)
    rrect(ctx, 300, 372, 140, 40, 6); fill_stroke(ctx, INK, lw=2)
    ctx.rectangle(CX0 + 8, TY1 + 12, CX1 - CX0 - 16, CY1 - TY1 - 20); setc(ctx, WALL2); ctx.fill()
    for x in (CX0 + 40, CX1 - 80):
        ctx.rectangle(x, CY1, 40, 30); fill_stroke(ctx, FILL3, lw=3)

def tub(ctx, t, s):
    rrect(ctx, TX0, TY0, TX1 - TX0, TY1 - TY0, 18); fill_stroke(ctx, hexc('#e9ecee'), lw=5)
    for ry in (640, 900):
        ctx.move_to(TX0 + 25, ry); ctx.line_to(TX1 - 25, ry); setc(ctx, STEEL_D); ctx.set_line_width(5); ctx.stroke()
        for i in range(10):
            x = TX0 + 60 + i * 58
            ctx.move_to(x, ry); ctx.line_to(x, ry - 70); ctx.set_line_width(3); setc(ctx, STEEL_D); ctx.stroke()
    for i in range(5):                                  # plates on the lower rack
        x = TX0 + 110 + i * 100
        ctx.save(); ctx.translate(x, 830); ctx.scale(0.35, 1); ctx.arc(0, 0, 70, 0, 6.28); ctx.restore()
        fill_stroke(ctx, PAPER, lw=3)
    for i in range(4):                                  # glasses on the upper rack
        x = TX0 + 140 + i * 130
        ctx.move_to(x - 28, 555); ctx.line_to(x + 28, 555); ctx.line_to(x + 22, 635); ctx.line_to(x - 22, 635)
        ctx.close_path(); fill_stroke(ctx, hexc('#eef6fa'), lw=3)
    # salt box cap in the tub floor, under the lower rack
    rrect(ctx, CAP_X - 45, TY1 - 22, 90, 22, 6); fill_stroke(ctx, FILL2, lw=3)
    for k in range(4):
        ctx.move_to(CAP_X - 30 + k * 20, TY1 - 19); ctx.line_to(CAP_X - 30 + k * 20, TY1 - 4)
        setc(ctx, INK2); ctx.set_line_width(2); ctx.stroke()

def salt_box(ctx, t, s):
    ctx.move_to(CAP_X - 30, TY1); ctx.line_to(CAP_X - 30, SY0); ctx.move_to(CAP_X + 30, TY1); ctx.line_to(CAP_X + 30, SY0)
    setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    rrect(ctx, SX0, SY0, SX1 - SX0, SY1 - SY0, 12); fill_stroke(ctx, hexc('#f3efe6'), lw=5)
    # water / brine inside (mustard tint grows)
    w = s['saltwater']
    if w > 0.02:
        h = (SY1 - SY0 - 14) * min(1, w)
        rrect(ctx, SX0 + 6, SY1 - 6 - h, SX1 - SX0 - 12, h, 8); setc(ctx, lerpc(WATER, BRINE, clamp(w * 1.2)), 0.55); ctx.fill()
    # salt crystals (cubes) piled at the bottom
    lvl = s['salt_level']
    rnd = random.Random(3)
    for i in range(46):
        cx = rnd.uniform(SX0 + 14, SX1 - 22); row = rnd.random()
        cy = SY1 - 14 - row * 60 * lvl
        sz = rnd.uniform(9, 13)
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(rnd.uniform(-0.5, 0.5))
        ctx.rectangle(-sz / 2, -sz / 2, sz, sz); setc(ctx, SALT_C); ctx.fill_preserve()
        setc(ctx, CHALK_D); ctx.set_line_width(1.5); ctx.stroke(); ctx.restore()

def resin(ctx, t, s, reset_btn=0.0):
    rrect(ctx, RX0, RY0, RX1 - RX0, RY1 - RY0, 16); fill_stroke(ctx, hexc('#f1ece0'), lw=5)
    # brine soaking down (mustard background)
    if s['brine'] > 0.02:
        h = (RY1 - RY0 - 10) * s['brine_front']
        rrect(ctx, RX0 + 5, RY0 + 5, RX1 - RX0 - 10, h, 12); setc(ctx, BRINE, 0.45 * s['brine']); ctx.fill()
    for b in BEADS:
        x, y = b[0], b[1]
        c = bead_state(b, s, t)
        ctx.arc(x, y, 9, 0, 6.28)
        setc(ctx, lerpc(BEAD_FRESH, CHALK, c)); ctx.fill_preserve()
        setc(ctx, lerpc(BEAD_FRESH_D, CHALK_D, c)); ctx.set_line_width(2); ctx.stroke()
        if c < 0.5:
            ctx.arc(x - 3, y - 3, 2.5, 0, 6.28); setc(ctx, WHITE, 0.7); ctx.fill()
    if reset_btn > 0:
        bx, by = RCX, RY0 + 100
        r = 46 * lerp(0.6, 1.0, reset_btn)
        ctx.arc(bx, by + 5, r, 0, 6.28); setc(ctx, hexc('#9c2a1a'), reset_btn); ctx.fill()
        ctx.arc(bx, by, r, 0, 6.28); setc(ctx, RED, reset_btn); ctx.fill_preserve()
        setc(ctx, INK, reset_btn); ctx.set_line_width(4); ctx.stroke()
        text_c(ctx, "RESET", bx, by + 7, 19, WHITE, True, 1, reset_btn)

def plumbing(ctx, t, s):
    # pipes first (under the parts)
    pipe(ctx, [(CX1 + 60, IN_Y), (RX1, IN_Y)], hexc('#9c8f7a'), 16)          # inlet hose + line to resin
    pipe(ctx, [(RCX, RY0), (RCX, TY1 - 2)], FILL3, 14)                      # resin -> tub
    pipe(ctx, [(V2[0], IN_Y), (V2[0], 1050), (SX1, 1050)], FILL3, 12)       # branch -> regen valve -> salt box
    pipe(ctx, [(SX0, BR_Y), (RX1, BR_Y)], FILL3, 12)                        # salt box -> resin (brine)
    pipe(ctx, [(RCX, RY1), (RCX, PUMP[1])], FILL3, 14)                      # resin -> pump
    pipe(ctx, [(RCX, PUMP[1]), (CX0 - 50, PUMP[1])], INK2, 18)              # drain hose (out LEFT)
    # inlet valve
    vx, vy = V1
    rrect(ctx, vx - 38, vy - 38, 76, 76, 10); fill_stroke(ctx, FILL2, lw=4)
    ctx.arc(vx, vy, 19, 0, 6.28); fill_stroke(ctx, COPPER, lw=3)
    # regeneration valve: red when shut, teal when open
    vx, vy = V2
    rrect(ctx, vx - 30, vy - 30, 60, 60, 9); fill_stroke(ctx, lerpc(FILL2, TEAL_L, s['v2']), lw=4)
    ctx.arc(vx, vy, 15, 0, 6.28); fill_stroke(ctx, COPPER, lw=3)
    # drain pump + motor
    px, py, pr = PUMP
    rrect(ctx, px + pr - 4, py - 25, 90, 50, 10); fill_stroke(ctx, FILL3, lw=3)
    ctx.arc(px, py, pr, 0, 6.28); fill_stroke(ctx, STEEL, lw=4)
    ang = t * 14 * s['drain']
    for k in range(4):
        an = ang + k * math.pi / 2
        ctx.move_to(px, py); ctx.line_to(px + (pr - 8) * math.cos(an), py + (pr - 8) * math.sin(an))
        setc(ctx, INK2); ctx.set_line_width(5); ctx.stroke()

def flows(ctx, t, s):
    a = s['wash']
    if a > 0.03:
        # hard water (white specks) up to the resin, soft water after it
        for i in range(9):
            u = (t * 0.45 + i / 9) % 1
            x, y = path_pt(P_WASH, u)
            inside = x < RX1 + 2 and y > RY0 - 2
            after = y < RY0 - 2
            rr = 4 if inside else 5.5
            ctx.arc(x, y, rr, 0, 6.28); setc(ctx, WATER, a); ctx.fill_preserve()
            setc(ctx, WATER_D, a); ctx.set_line_width(1.5); ctx.stroke()
            if not after and not inside:
                ctx.arc(x + 2, y - 1.5, 2.3, 0, 6.28); setc(ctx, CHALK, a); ctx.fill()
    dots(ctx, t, P_REGEN, s['v2'], WATER, WATER_D, speed=0.8, n=7)
    dots(ctx, t, P_BRINE, s['brine'] * (1 - sstep(t, B(10) - 0.6, 0.4)), BRINE, BRINE_D, speed=0.5, n=6)
    dots(ctx, t, P_DRAIN, s['drain'], BRINE, BRINE_D, speed=0.8, n=8, specks=True)

def scene(ctx, t, s):
    cabinet(ctx)
    tub(ctx, t, s)
    plumbing(ctx, t, s)
    salt_box(ctx, t, s)
    resin(ctx, t, s, reset_btn=sstep(t, B(11) + 1.0, 0.5))
    flows(ctx, t, s)

def falling_grain(ctx, t):
    """Beat 1: a salt grain drops through the cap into the salt box. Beat 12: a grain flies to the RESET button."""
    if t < B(1):
        u = sstep(t, 0.3, 1.6)
        x, y = CAP_X, lerp(700, SY1 - 40, u ** 1.5)
        a = 1 - sstep(t, 2.2, 0.3)
    elif B(11) + 0.1 <= t < B(11) + 1.2:
        u = sstep(t, B(11) + 0.1, 1.0)
        x = lerp(CAP_X, RCX, u); y = lerp(SY1 - 50, RY0 + 100, u) - 120 * math.sin(u * math.pi)
        a = 1.0
    else:
        return
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 3)
    ctx.rectangle(-11, -11, 22, 22); setc(ctx, SALT_C, a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke(); ctx.restore()

def blocked_arrow(ctx, t, a):
    """Beat 1: dashed arrow from the salt box up toward the plates, stopped by a red X before the dishes."""
    if a <= 0: return
    k = sstep(t, 2.0, 0.8)
    y1 = lerp(SY0 - 10, 900, k)
    ctx.set_dash([12, 9]); ctx.move_to(SX1 - 20, SY0 + 10); ctx.line_to(SX1 + 60, y1)
    setc(ctx, INK2, a); ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
    xa = sstep(t, 2.8, 0.25) * a
    if xa > 0:
        cx, cy = SX1 + 62, 890
        for dx in (-1, 1):
            ctx.move_to(cx - 26, cy - 26 * dx); ctx.line_to(cx + 26, cy + 26 * dx)
        setc(ctx, RED, xa); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def labels(ctx, t, s):
    a = win(t, 0.4, B(1), 0.3)
    if a > 0:
        tag(ctx, "SALT", CAP_X, 1180, INK, a * sstep(t, 1.4, 0.3), 26)
        tag(ctx, "NEVER REACHES THE DISHES", 610, 760, RED, a * sstep(t, 3.0, 0.3), 22)
    blocked_arrow(ctx, t, win(t, 1.8, B(1), 0.3))
    a = bw(t, 1)
    if a > 0:
        highlight(ctx, RCX, (RY0 + RY1) / 2, 85, 125, TEAL, a, t)
        tag(ctx, "WATER SOFTENER", 480, 1300, TEAL, a, 24)
    a = bw(t, 2)
    if a > 0:
        tag(ctx, "HARD WATER IN", 690, 1300, WATER_D, a, 20)
        tag(ctx, "CALCIUM + MAGNESIUM", 690, 1350, INK, a * sstep(t, B(2) + 1.2, 0.3), 18)
    a = bw(t, 4)
    if a > 0:
        highlight(ctx, RCX, (RY0 + RY1) / 2, 80, 120, MUSTARD, a, t)
        tag(ctx, "1 · RESIN BEADS", 500, 1300, INK, a, 20)
        tag(ctx, "SOFT WATER UP", 380, 965, TEAL, a * sstep(t, B(4) + 1.6, 0.3), 18)
    a = bw(t, 6)
    if a > 0:
        tag(ctx, "CLOGGED", 470, 1300, CHALK_D, a * sstep(t, B(6) + 2.0, 0.3), 22)
    a = bw(t, 7)
    if a > 0:
        highlight(ctx, (SX0 + SX1) / 2, (SY0 + SY1) / 2, 115, 85, MUSTARD, a, t)
        tag(ctx, "2 · SALT BOX", 510, 1200, INK, a, 20)
        tag(ctx, "VALVE OPENS", V2[0], 1205, TEAL, a * sstep(t, B(7) + 2.6, 0.3), 16)
    a = bw(t, 8)
    if a > 0:
        tag(ctx, "BRINE", 380, 1070, BRINE_D, a, 20)
    a = bw(t, 9)
    if a > 0:
        tag(ctx, "SODIUM PUSHES LIMESTONE OFF", 470, 1300, INK, a, 16)
    a = bw(t, 10)
    if a > 0:
        highlight(ctx, PUMP[0], PUMP[1], 70, 65, TEAL, a, t)
        tag(ctx, "3 · DRAIN PUMP", 480, 1420, TEAL, a, 20)
        tag(ctx, "TO THE DRAIN", 200, 1410, BRINE_D, a * sstep(t, B(10) + 1.0, 0.3), 16)
    a = win(t, B(11) + 1.0, B(12) + 3, 0.3)
    if a > 0:
        tag(ctx, "SALT = RESET", 640, 1300, RED, a, 30)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    fx, fy, z = cam_track(CAMKEYS, t, move=0.8)
    ctx.save()
    ctx.rectangle(0, 178, 1080, 1322); ctx.clip()
    ctx.translate(540, 930); ctx.scale(z, z); ctx.translate(-fx, -fy)
    scene(ctx, t, s)
    falling_grain(ctx, t)
    labels(ctx, t, s)
    ctx.restore()

SFX = [(0.4, 'pop'), (1.5, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.3, 'pop'), (B(4) + 0.3, 'pop'),
       (B(6) + 2.0, 'pop'), (B(7) + 0.3, 'pop'), (B(7) + 2.6, 'click'), (B(8) + 0.3, 'pop'),
       (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop'), (B(11) + 1.0, 'click')]
HUM = []

# ---------------------------------------------------------------- cards
def card_glass(ctx, t, lt, a):
    card_frame(ctx, "HOT WATER DRIES OFF", a, "WATER LEAVES · LIMESTONE STAYS", RED)
    film = sstep(lt, 1.0, 2.5)
    for gx in (380, 700):
        ctx.move_to(gx - 70, 280); ctx.line_to(gx + 70, 280); ctx.line_to(gx + 55, 520); ctx.line_to(gx - 55, 520)
        ctx.close_path()
        setc(ctx, lerpc(hexc('#eef6fa'), hexc('#f4f2ec'), film), a); ctx.fill_preserve()
        setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
        rnd = random.Random(gx)
        for i in range(26):
            x = gx + rnd.uniform(-55, 55); y = rnd.uniform(300, 505)
            ctx.arc(x, y, rnd.uniform(4, 8), 0, 6.28); setc(ctx, WHITE, a * film * 0.9); ctx.fill()
        ctx.move_to(gx - 45, 300); ctx.line_to(gx - 35, 490); setc(ctx, WHITE, a * 0.8); ctx.set_line_width(6); ctx.stroke()
    da = a * (1 - film * 0.6)
    for x in (540,):
        wavy_arrow(ctx, x, 500, x, 300, lt, ORANGE, da, amp=8, wl=34, lw=5, head=12)
    text_c(ctx, "STEAM", 540, 290, 20, ORANGE, True, 1, da)
    text_c(ctx, "WHITE FILM", 700, 270, 22, INK2, True, 1, a * sstep(lt, 2.2, 0.4))

def card_bead(ctx, t, lt, a):
    card_frame(ctx, "ONE BEAD, ZOOMED IN", a, "TRADE: CALCIUM + MAGNESIUM IN · SODIUM OUT", TEAL)
    bx, by, br = 540, 395, 105
    ctx.arc(bx, by, br, 0, 6.28); setc(ctx, BEAD_FRESH, a); ctx.fill_preserve()
    setc(ctx, BEAD_FRESH_D, a); ctx.set_line_width(5); ctx.stroke()
    ctx.arc(bx - 35, by - 35, 18, 0, 6.28); setc(ctx, WHITE, 0.6 * a); ctx.fill()
    def ion(x, y, r, col, txt, al, tc=INK):
        if al <= 0: return
        ctx.arc(x, y, r, 0, 6.28); setc(ctx, col, al); ctx.fill_preserve()
        setc(ctx, INK, al); ctx.set_line_width(3); ctx.stroke()
        text_c(ctx, txt, x, y + r * 0.38, r * 0.95, tc, True, 0, al)
    # two hardness ions come in from the LEFT and stick on the bead
    arrive = [(sstep(lt, 0.3, 1.2), -40, "Ca"), (sstep(lt, 0.9, 1.2), 45, "Mg")]
    for k, (u, dy, txt) in enumerate(arrive):
        x = lerp(180, bx - br - 22, u); y = by + dy
        ion(x, y, 26, CHALK, txt, a)
    # each one frees TWO sodium ions that leave to the RIGHT (one Ca/Mg = two Na: same charge)
    for k, (t0, dy) in enumerate([(1.3, -70), (1.4, -15), (1.9, 30), (2.0, 80)]):
        u = sstep(lt, t0, 1.3)
        x = lerp(bx + br + 18, 880, u); y = by + dy
        ion(x, y, 19, NA_C, "Na", a, WHITE)

CARDS = {'glass': card_glass, 'bead': card_bead}
