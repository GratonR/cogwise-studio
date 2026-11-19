"""Cogwise episode: Your washer eats coins. Here's where they go.
One idea: the little door at the bottom front of a front-loader hides the drain-pump FILTER. All the drain water
passes through it before the impeller, so coins (buttons, pins...) stay in its basket instead of jamming the pump.

VIEW (screen coordinates, y grows DOWN): SIDE SECTION of a front-loader, machine FRONT on the LEFT (x 200).
  - tub x 320-905 / y 560-1040, drum inside (x 360-870, y 600-1000); door glass bulges on the left.
  - the tub drains from its bottom (620, 1040) through a hose DOWN to the pump inlet on top of the filter housing (470, 1250).
  - filter housing: horizontal tube x 250-612, y 1250-1350. The filter (cap at the front, x 205-252, + basket) is screwed
    in from the FRONT, behind the little access flap of the front wall (hinged at the bottom, opens out to the left).
    The basket's RIGHT end is a grille (horizontal slats): water flows LEFT -> RIGHT through the gaps; a coin is too big.
  - pump volute right of the filter, centre (690, 1300): water enters the impeller eye (centre), is flung round and leaves
    tangentially at the RIGHTMOST point going UP -> impeller turns COUNTER-clockwise on screen (angle decreases).
  - outlet pipe up the back (x 930) and out of the cabinet at the top back (y 540) = TO DRAIN.
  - beat 12 HUD: the cap seen from the FRONT, twisted COUNTER-clockwise (as you face the machine) to unscrew.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="washer-coin-trap",
    title="Your washer eats coins. Here's where they go. 🪙 #Shorts",
    description=("Every coin your washer swallows ends up in one tiny pocket, behind the little door at the bottom.\n\n"
                 "#Shorts #howthingswork #washingmachine #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "washingmachine", "appliances", "cogwise"],
    sources=[
        "https://www.samsung.com/au/support/home-appliances/clean-debris-filter/",
        "https://www.whitegoodshelp.co.uk/washing-machine-pump-filter/",
        "https://www.bosch-home.co.uk/customer-service/get-support/washing-machines/cleaning-filter",
        "https://www.beko.co.uk/support/faqs/how-often-to-clean-beko-washing-machine-filter",
    ],
)

BEATS = [
    dict(dur=4.8, title="THE COIN", caption="Every coin your washer swallows ends up in one tiny pocket."),
    dict(dur=5.2, title="THE SECRET", caption="It's behind this little door, down at the bottom of the machine."),
    dict(dur=5.2, title="THE FILTER", caption="Behind the door sits a plastic filter, screwed into the drain pump."),
    dict(dur=5.6, title="1 · THE DRUM", caption="A loose coin slips past the drum and drops into the outer tub."),
    dict(dur=5.6, title="2 · THE HOSE", caption="When the machine drains, the water rushes down a hose, carrying the coin."),
    dict(dur=5.2, title="3 · THE GRILLE", caption="Every drop must pass through this filter before it reaches the pump."),
    dict(dur=5.4, title=None, caption="The water flows through the grille. The coin can't, so it stays.", card='caught'),
    dict(dur=6.0, title="4 · THE IMPELLER", caption="Right behind it spins the impeller, a small plastic fan that pushes water out."),
    dict(dur=5.8, title=None, caption="Without the filter, one coin jams it. The pump hums, but nothing drains.", card='jammed'),
    dict(dur=6.2, title="SURPRISE", caption="Samsung says to clean it five or six times a year. Most people never have."),
    dict(dur=5.2, title="FIX IT · 1", caption="To empty it: unplug, put down a towel and a shallow tray."),
    dict(dur=5.8, title="FIX IT · 2", caption="Drain the little hose first, then twist the filter counterclockwise and rinse it."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

STEEL = hexc('#9aa3ab'); STEEL_D = hexc('#6d757c')
GLASS = hexc('#bfe3df'); DRUM_C = hexc('#c9ccd0')
COIN = hexc('#d9a441'); COIN_D = hexc('#9c6f1c')
WATER = hexc('#8fcfc8'); BLUE = hexc('#2f6fb3')
TOWEL = hexc('#e4472f')

# ---------------------------------------------------------------- geometry
CX0, CX1, CY0, CY1 = 200, 960, 500, 1480        # cabinet
TX0, TX1, TY0, TY1 = 320, 905, 560, 1040        # outer tub
DX0, DX1, DY0, DY1 = 360, 870, 600, 1000        # drum
HX0, HX1, HY0, HY1 = 250, 612, 1250, 1350       # filter housing
FY = 1300                                       # pump axis
BX0, BX1 = 262, 548                             # basket body (grille at BX1..GX1)
GX1 = 570
INLET_X = 470
VX, VY, VR = 690, 1300, 78                      # volute
OUT_X = VX + VR - 10                            # 758: outlet pipe x (rightmost point of the impeller)
FLAP_H = 100                                    # flap: front wall x=200, y 1260..1360, hinge at the bottom
COIN_R = 14

# ---------------------------------------------------------------- paths
def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        u = i / n; v = 1 - u
        out.append((v**3*p0[0] + 3*v*v*u*p1[0] + 3*v*u*u*p2[0] + u**3*p3[0],
                    v**3*p0[1] + 3*v*v*u*p1[1] + 3*v*u*u*p2[1] + u**3*p3[1]))
    return out

HOSE = bez((620, 1040), (620, 1150), (INLET_X, 1140), (INLET_X, HY0))
OUTLET = [(OUT_X, VY)] + bez((OUT_X, 1200), (OUT_X, 1120), (930, 1170), (930, 1060))[0:] + [(930, 540), (1010, 540)]

def arc_pts(cx, cy, r, a0, a1, n=12):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]

# water: hose -> into the basket -> through the grille (y = FY) -> impeller eye -> flung round CCW -> up the outlet
FLOW = (HOSE + [(INLET_X, 1275), (510, FY), (GX1 + 4, FY), (VX - 20, FY), (VX, VY + 30)]
        + arc_pts(VX, VY, 55, math.pi / 2, 0.0) + [(OUT_X, VY)] + OUTLET[1:])

class Path:
    def __init__(self, pts):
        self.p = pts; self.L = [0.0]
        for a, b in zip(pts, pts[1:]): self.L.append(self.L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    def at(self, u):
        d = clamp(u) * self.L[-1]
        for i in range(1, len(self.L)):
            if self.L[i] >= d:
                k = (d - self.L[i - 1]) / max(1e-6, self.L[i] - self.L[i - 1])
                a, b = self.p[i - 1], self.p[i]
                return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
        return self.p[-1]

PFLOW = Path(FLOW)
PHOSE = Path(HOSE + [(INLET_X, 1290), (452, HY1 - 10 - COIN_R)])

def pipe(ctx, pts, w, fill, a=1.0):
    ctx.new_path(); ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    setc(ctx, INK, a); ctx.set_line_width(w + 8); ctx.stroke_preserve()
    setc(ctx, fill, a); ctx.set_line_width(w); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['zoom'] = 1 - ease(clamp((t - B(1) - 0.1) / 1.1))          # beat 1 close-up on the pocket
    s['flap'] = sstep(t, B(1) + 1.2, 0.5)                          # the little door opens (beat 2)
    s['level'] = lerp(930, 1040, clamp((t - B(4) - 0.3) / (B(6) - B(4))))   # tub water drains
    s['flow'] = win(t, B(4) + 0.3, B(8) + 0.6, 0.5)                # drain running (beats 5-8)
    s['drum'] = 1.0 if t < B(4) + 0.3 else 0.3                     # drum turning while washing
    s['gunk'] = sstep(t, B(9) + 0.8, 3.0)                          # basket fills up (surprise)
    s['plug'] = sstep(t, B(10) + 0.5, 0.5)                         # unplugged
    s['tray'] = sstep(t, B(10) + 1.8, 0.5)
    s['hose'] = sstep(t, B(11) + 0.2, 0.6)                         # little drain hose pulled out
    s['drip'] = win(t, B(11) + 0.7, B(11) + 2.6, 0.2)
    s['pull'] = sstep(t, B(11) + 2.6, 1.2)                         # filter unscrewed and pulled out
    s['rinse'] = win(t, B(11) + 4.0, B(12) + 1, 0.3)
    return s

def coin1(t):
    """The preview coin of beat 1: drops from the inlet into the basket and rolls to the front of it."""
    if t < 0.3: return None
    y = lerp(1195, HY1 - 10 - COIN_R, ease(clamp((t - 0.3) / 0.8)))
    x = INLET_X - 150 * ease(clamp((t - 1.1) / 0.9))
    return (x, y)

def coin2(t):
    """The story coin: drum -> gap -> tub bottom (beat 4) -> hose -> basket (beat 5)."""
    t0 = B(3)
    if t < t0 - 0.5: return None
    if t < t0 + 1.2:                      # carried by the drum to its front lip
        k = ease(clamp((t - t0 - 0.1) / 1.1)); return (lerp(520, 375, k), DY1 - 18)
    if t < t0 + 2.2:                      # slips through the gap between drum and tub, falls
        k = clamp((t - t0 - 1.2) / 1.0); return (lerp(375, 342, ease(min(1, k * 2))), lerp(DY1 - 18, TY1 - 4 - COIN_R, k * k))
    if t < B(4) + 0.6:                    # slides along the tub bottom to the drain
        k = ease(clamp((t - t0 - 2.3) / 2.6)); return (lerp(342, 612, k), TY1 - 4 - COIN_R)
    k = ease(clamp((t - B(4) - 0.6) / 3.2))
    return PHOSE.at(k)

def coin(ctx, x, y, a=1.0, r=COIN_R):
    ctx.arc(x, y, r, 0, 2 * math.pi); setc(ctx, COIN, a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(x, y, r * 0.6, 0, 2 * math.pi); setc(ctx, COIN_D, a); ctx.set_line_width(2); ctx.stroke()

# ---------------------------------------------------------------- machine
def cabinet(ctx, t, s):
    rrect(ctx, CX0, CY0, CX1 - CX0, CY1 - CY0, 22); fill_stroke(ctx, PAPER, lw=5)
    for x in (CX0 + 30, CX1 - 30):
        ctx.rectangle(x - 18, CY1, 36, 18); fill_stroke(ctx, INK2, lw=2)
    text_c(ctx, "FRONT", CX0 + 55, CY0 + 90, 22, INK2, True, 2)
    # control panel strip at the top front
    rrect(ctx, CX0 + 15, CY0 + 15, 300, 30, 8); fill_stroke(ctx, FILL2, lw=3)

def tub(ctx, t, s):
    rrect(ctx, TX0, TY0, TX1 - TX0, TY1 - TY0, 60); fill_stroke(ctx, FILL3, lw=5)
    # door glass bulging out of the front
    ctx.save(); ctx.translate(CX0 + 110, 800); ctx.scale(95, 160); ctx.arc(0, 0, 1, math.pi / 2, 3 * math.pi / 2); ctx.restore()
    ctx.close_path(); setc(ctx, GLASS, 0.85); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.rectangle(CX0 + 100, 630, 22, 340); fill_stroke(ctx, FILL3, lw=4)          # door ring
    # bearing / shaft at the back
    ctx.rectangle(DX1, 780, TX1 - DX1 + 30, 40); fill_stroke(ctx, STEEL_D, lw=3)
    # drum with scrolling perforations (= turning)
    rrect(ctx, DX0, DY0, DX1 - DX0, DY1 - DY0, 30); fill_stroke(ctx, DRUM_C, lw=4)
    ctx.save(); rrect(ctx, DX0 + 6, DY0 + 6, DX1 - DX0 - 12, DY1 - DY0 - 12, 26); ctx.clip()
    off = (t * 55 * s['drum']) % 60 if t < B(4) + 0.3 else ((B(4) + 0.3) * 55) % 60
    for i in range(9):
        for j in range(-1, 8):
            x = DX0 + 40 + i * 56 + (j % 2) * 28; y = DY0 + 30 + j * 60 + off
            ctx.arc(x, y, 7, 0, 6.28); setc(ctx, INK2, 0.55); ctx.fill()
    ctx.restore()
    # water left in the tub (drains during beats 5-6)
    lv = s['level']
    if lv < TY1 - 4:
        ctx.save(); rrect(ctx, TX0 + 3, TY0 + 3, TX1 - TX0 - 6, TY1 - TY0 - 6, 58); ctx.clip()
        ctx.rectangle(TX0, lv, TX1 - TX0, TY1 - lv); setc(ctx, WATER, 0.55); ctx.fill()
        ctx.move_to(TX0, lv); ctx.line_to(TX1, lv); setc(ctx, TEAL, 0.8); ctx.set_line_width(3); ctx.stroke()
        ctx.restore()

def flap(ctx, s):
    th = s['flap'] * math.radians(80)
    hx, hy = CX0, HY0 + 10 + FLAP_H
    ctx.rectangle(CX0 - 4, HY0 + 10, 8, FLAP_H); setc(ctx, INK2 if th > 0.05 else PAPER); ctx.fill()
    ex, ey = hx - FLAP_H * math.sin(th), hy - FLAP_H * math.cos(th)
    ctx.move_to(hx, hy); ctx.line_to(ex, ey); setc(ctx, INK); ctx.set_line_width(14); ctx.stroke()
    ctx.move_to(hx, hy); ctx.line_to(ex, ey); setc(ctx, FILL2); ctx.set_line_width(8); ctx.stroke()

def basket(ctx, t, s, dx):
    """Filter = front cap + basket + grille end. dx = how far it is pulled out to the left."""
    ctx.save(); ctx.translate(-dx, 0)
    # basket body (see-through)
    rrect(ctx, BX0, HY0 + 10, GX1 - BX0, HY1 - HY0 - 20, 12)
    setc(ctx, WHITE, 0.35); ctx.fill_preserve(); setc(ctx, INK2); ctx.set_line_width(3); ctx.set_dash([10, 6]); ctx.stroke(); ctx.set_dash([])
    # grille: horizontal slats at the right end, gaps let water through
    for k in range(6):
        y = HY0 + 12 + k * 13.5
        ctx.rectangle(BX1, y, GX1 - BX1, 7); setc(ctx, INK); ctx.fill()
    # cap with grip ridges
    rrect(ctx, 205, HY0 + 2, 50, HY1 - HY0 - 4, 10); fill_stroke(ctx, FILL3, lw=4)
    for k in range(4):
        ctx.move_to(215 + k * 10, HY0 + 18); ctx.line_to(215 + k * 10, HY1 - 18); setc(ctx, INK2); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def gunk(ctx, s, dx):
    g = s['gunk']
    if g <= 0: return
    ctx.save(); ctx.translate(-dx, 0)
    rnd = random.Random(7)
    by = HY1 - 10
    items = [('lint', 300, 0.0), ('button', 345, 0.15), ('coin', 395, 0.3), ('pin', 430, 0.45),
             ('button', 500, 0.6), ('lint', 520, 0.75), ('coin', 280, 0.85)]
    for kind, x, d in items:
        a = clamp((g - d) / 0.15)
        if a <= 0: continue
        if kind == 'coin': coin(ctx, x, by - COIN_R - 22, a)
        elif kind == 'button':
            ctx.arc(x, by - 13, 13, 0, 6.28); setc(ctx, RED, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(2.5); ctx.stroke()
            for o in (-4, 4): ctx.arc(x + o, by - 13, 2.5, 0, 6.28); setc(ctx, INK, a); ctx.fill()
        elif kind == 'pin':
            ctx.move_to(x - 40, by - 30); ctx.line_to(x + 30, by - 8); ctx.line_to(x - 30, by - 10)
            setc(ctx, STEEL_D, a); ctx.set_line_width(4); ctx.stroke()
        else:
            for k in range(14):
                ctx.arc(x + rnd.uniform(-22, 22), by - rnd.uniform(4, 22), rnd.uniform(4, 8), 0, 6.28); setc(ctx, INK2, 0.35 * a); ctx.fill()
    ctx.restore()

def housing(ctx, t, s):
    # tube around the filter, open at the front (cap side)
    ctx.rectangle(HX0, HY0, HX1 - HX0, HY1 - HY0); setc(ctx, FILL2); ctx.fill()
    for y in (HY0, HY1):
        ctx.move_to(HX0, y); ctx.line_to(HX1, y); setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()
    # volute + impeller (face-on), turning counter-clockwise on screen
    ctx.arc(VX, VY, VR, 0, 2 * math.pi); fill_stroke(ctx, FILL3, lw=6)
    ctx.arc(VX, VY, VR - 12, 0, 2 * math.pi); setc(ctx, FILL2); ctx.fill()
    ang = -s['_spin']
    for k in range(5):
        a0 = ang + k * 2 * math.pi / 5
        ctx.move_to(VX + 12 * math.cos(a0), VY + 12 * math.sin(a0))
        a1 = a0 + 0.55      # vanes swept back against the CCW rotation
        ctx.curve_to(VX + 35 * math.cos(a0 + 0.1), VY + 35 * math.sin(a0 + 0.1),
                     VX + 50 * math.cos(a1), VY + 50 * math.sin(a1), VX + 60 * math.cos(a1), VY + 60 * math.sin(a1))
        setc(ctx, TEAL); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.arc(VX, VY, 14, 0, 6.28); fill_stroke(ctx, STEEL_D, lw=3)
    # little emergency drain hose, clipped next to the cap
    h = s['hose']
    end = (lerp(232, 120, h), lerp(1405, 1435, h))
    ctx.new_path(); ctx.move_to(290, HY1)
    ctx.curve_to(290, 1400, lerp(260, 200, h), lerp(1410, 1440, h), *end)
    setc(ctx, INK); ctx.set_line_width(16); ctx.stroke_preserve(); setc(ctx, FILL3); ctx.set_line_width(10); ctx.stroke()
    ctx.arc(end[0], end[1], 9, 0, 6.28); fill_stroke(ctx, RED, lw=3)

def floor_props(ctx, t, s):
    a = s['tray']
    if a > 0:
        ctx.rectangle(15, 1488, 250, 12); fill_stroke(ctx, TOWEL, lw=3, alpha=a)
        for x in range(25, 260, 18):
            ctx.move_to(x, 1490); ctx.line_to(x, 1498); setc(ctx, PAPER, 0.7 * a); ctx.set_line_width(3); ctx.stroke()
        ctx.move_to(35, 1450); ctx.line_to(48, 1487); ctx.line_to(182, 1487); ctx.line_to(195, 1450)
        setc(ctx, STEEL, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        wl = 0.6 * clamp((t - B(11) - 0.8) / 2.0)
        if wl > 0:
            ctx.rectangle(48, 1487 - 30 * wl, 134, 30 * wl); setc(ctx, WATER, 0.8 * a); ctx.fill()
    # power cord + wall socket (back of the machine, right)
    p = s['plug']
    ctx.rectangle(1010, 1250, 50, 70); fill_stroke(ctx, PAPER, lw=3)
    for yy in (1272, 1298): ctx.arc(1035, yy, 5, 0, 6.28); setc(ctx, INK); ctx.fill()
    px, py = lerp(1000, 985, p), lerp(1285, 1360, p)
    ctx.move_to(CX1, 1420); ctx.curve_to(990, 1430, px - 30, py + 50, px - 18, py)
    setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()
    rrect(ctx, px - 30, py - 18, 32, 36, 6); fill_stroke(ctx, INK2, lw=3)

def water(ctx, t, s):
    f = s['flow']
    if f <= 0: return
    n = 46
    for i in range(n):
        u = (i / n + t * 0.16) % 1.0
        x, y = PFLOW.at(u)
        ctx.arc(x, y, 7, 0, 6.28); setc(ctx, WATER, f); ctx.fill_preserve()
        setc(ctx, TEAL, f); ctx.set_line_width(2); ctx.stroke()

def drips(ctx, t, s):
    d = s['drip']
    if d > 0:
        for k in range(3):
            u = (t * 1.6 + k / 3) % 1
            ctx.arc(120, lerp(1448, 1480, u), 5, 0, 6.28); setc(ctx, WATER, d); ctx.fill_preserve(); setc(ctx, TEAL, d); ctx.set_line_width(2); ctx.stroke()
    r = s['rinse']
    if r > 0:
        for k in range(4):
            x = 120 + k * 45
            wavy_arrow(ctx, x, 1150, x, 1235, t, BLUE, r, amp=4, wl=18, lw=3, head=8)

def stage(ctx, t, s):
    s['_spin'] = 0.0
    # impeller angle: integrated speed (fast while draining)
    t1 = B(4) + 0.3; t2 = B(8) + 0.6
    s['_spin'] = 9.0 * clamp(t - t1, 0, t2 - t1)
    cabinet(ctx, t, s)
    pipe(ctx, HOSE, 26, FILL3)
    pipe(ctx, OUTLET, 26, FILL3)
    tub(ctx, t, s)
    housing(ctx, t, s)
    dx = 175 * s['pull']
    basket(ctx, t, s, dx)
    c = coin1(t)
    if c: coin(ctx, c[0] - dx, c[1])
    c = coin2(t)
    if c: coin(ctx, c[0] - (dx if t > B(5) else 0), c[1])
    gunk(ctx, s, dx)
    water(ctx, t, s)
    flap(ctx, s)
    floor_props(ctx, t, s)
    drips(ctx, t, s)

def overlays(ctx, t, s):
    a = bw(t, 2)
    if a > 0:
        highlight(ctx, 400, FY, 200, 70, MUSTARD, a, t)
        tag(ctx, "PLASTIC FILTER", 400, 1440, INK, a, 26)
        tag(ctx, "DRAIN PUMP", VX + 20, 1170, TEAL, a * sstep(t, B(2) + 1.8), 26)
    a = bw(t, 3)
    if a > 0:
        tag(ctx, "DRUM", 615, 700, INK, a, 26)
        tag(ctx, "OUTER TUB", 800, 1080, INK, a * sstep(t, B(3) + 2.2), 24)
    a = bw(t, 4)
    if a > 0:
        tag(ctx, "DRAIN HOSE", 330, 1150, TEAL, a, 26)
    a = bw(t, 5)
    if a > 0:
        highlight(ctx, (BX1 + GX1) / 2, FY, 34, 62, RED, a, t)
        tag(ctx, "EVERY DROP · THROUGH HERE", 470, 1440, RED, a, 24)
    a = bw(t, 7)
    if a > 0:
        highlight(ctx, VX, VY, 95, 95, TEAL, a, t)
        tag(ctx, "IMPELLER", VX, 1440, TEAL, a, 26)
        tag(ctx, "TO THE DRAIN", 830, 465, TEAL, a * sstep(t, B(7) + 1.5), 24)
        straight_arrow(ctx, 975, 540, 1050, 540, TEAL, a * sstep(t, B(7) + 1.5), lw=6, head=14)
    a = bw(t, 9)
    if a > 0:
        tag(ctx, "WHAT PILES UP", 400, 1440, RED, a * sstep(t, B(9) + 0.8), 26)
    a = bw(t, 10)
    if a > 0:
        tag(ctx, "UNPLUG", 985, 1200, RED, a * sstep(t, B(10) + 0.5), 24)
        tag(ctx, "TOWEL + TRAY", 150, 1400, INK, a * sstep(t, B(10) + 1.8), 24)
    a = bw(t, 11)
    if a > 0:
        tag(ctx, "1 · LITTLE HOSE", 150, 1400, TEAL, a * win(t, B(11) + 0.2, B(11) + 2.6, 0.25), 22)
        tag(ctx, "2 · TWIST & PULL", 230, 1180, INK, a * win(t, B(11) + 2.6, B(11) + 4.0, 0.25), 22)
        tag(ctx, "3 · RINSE", 200, 1110, BLUE, a * sstep(t, B(11) + 4.0), 22)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    z = 1 + 0.7 * ease(s['zoom'])
    c = (440, FY - 40)
    ctx.save()
    if z > 1.001:
        ctx.rectangle(0, 180, 1080, 1320); ctx.clip()
        tx, ty = lerp(c[0], 540, (z - 1) / 0.7), lerp(c[1], 1000, (z - 1) / 0.7)
        ctx.translate(tx, ty); ctx.scale(z, z); ctx.translate(-c[0], -c[1])
    stage(ctx, t, s)
    ctx.restore()
    a = win(t, 1.2, B(1) + 0.6, 0.3)
    if a > 0:
        tag(ctx, "ONE TINY POCKET", 540, 1260, RED, a, 32)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=175, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def front_panel(ctx, t, a):
    """Beat 2: the washer seen from the front, the little door bottom-right opens."""
    _panel(ctx, a)
    x0, y0, w, h = 140, 192, 240, 266
    rrect(ctx, x0, y0, w, h, 14); fill_stroke(ctx, PAPER, lw=4, alpha=a)
    rrect(ctx, x0 + 10, y0 + 10, w - 20, 28, 6); fill_stroke(ctx, FILL2, lw=2, alpha=a)
    ctx.arc(x0 + w / 2, y0 + 140, 78, 0, 6.28); fill_stroke(ctx, FILL3, lw=4, alpha=a)
    ctx.arc(x0 + w / 2, y0 + 140, 58, 0, 6.28); setc(ctx, GLASS, 0.8 * a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    o = sstep(t, B(1) + 1.2, 0.5)
    fx, fy, fw, fh = x0 + w - 70, y0 + h - 42, 52, 30
    ctx.rectangle(fx, fy, fw, fh); setc(ctx, INK2, a); ctx.fill()
    ctx.arc(fx + fw / 2, fy + fh / 2, 10, 0, 6.28); setc(ctx, FILL3, a * o); ctx.fill()
    # flap hinged at its bottom edge: tips toward the viewer (squashes downwards)
    rrect(ctx, fx, fy + fh * o, fw, max(2, fh * (1 - 0.85 * o)), 3); fill_stroke(ctx, FILL2, lw=3, alpha=a)
    highlight(ctx, fx + fw / 2, fy + fh / 2, 46, 32, RED, a * o, t)
    # zoom: the round filter cap behind it
    k = a * sstep(t, B(1) + 2.0, 0.4)
    straight_arrow(ctx, fx + fw + 20, fy + 5, 560, 330, RED, k, lw=4, head=10)
    ctx.arc(700, 315, 95, 0, 6.28); fill_stroke(ctx, FILL3, lw=5, alpha=k)
    rrect(ctx, 690 - 60, 300, 140, 30, 10); fill_stroke(ctx, FILL2, lw=4, alpha=k)
    text_c(ctx, "LITTLE DOOR · BOTTOM FRONT", 700, 450, 26, RED, True, 1.5, k)

def calendar(ctx, t, a):
    _panel(ctx, a)
    lt = t - B(9)
    for i in range(12):
        x = 100 + (i % 6) * 90; y = 205 + (i // 6) * 115
        rrect(ctx, x, y, 78, 95, 8); fill_stroke(ctx, PAPER, lw=3, alpha=a)
        ctx.rectangle(x, y, 78, 20); setc(ctx, RED, 0.7 * a); ctx.fill()
        if i % 2 == 0:
            k = a * sstep(t, B(9) + 0.4 + 0.25 * (i // 2), 0.2)
            ctx.move_to(x + 18, y + 58); ctx.line_to(x + 34, y + 76); ctx.line_to(x + 62, y + 36)
            setc(ctx, TEAL, k); ctx.set_line_width(7); ctx.stroke()
    text_c(ctx, "5–6×", 835, 300, 72, TEAL, True, 2, a)
    text_c(ctx, "A YEAR · SAMSUNG", 835, 350, 26, INK, True, 1.5, a)
    text_c(ctx, "MOST PEOPLE: NEVER", 835, 425, 26, RED, True, 1.5, a * sstep(t, B(9) + 3.4, 0.3))

def twist_panel(ctx, t, a):
    """Beat 12: the cap seen from the FRONT, turned counter-clockwise (screen) to unscrew."""
    _panel(ctx, a)
    cx, cy, r = 260, 325, 105
    rot = -1.6 * sstep(t, B(11) + 2.6, 1.2)          # negative angle = counter-clockwise on screen
    ctx.arc(cx, cy, r, 0, 6.28); fill_stroke(ctx, FILL3, lw=5, alpha=a)
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot)
    rrect(ctx, -75, -16, 150, 32, 10); fill_stroke(ctx, FILL2, lw=4, alpha=a)
    ctx.restore()
    # counter-clockwise arrow: from the right side going UP and over to the left
    ra = r + 28
    ctx.new_path(); ctx.arc_negative(cx, cy, ra, math.radians(20), math.radians(-160))
    setc(ctx, RED, a); ctx.set_line_width(7); ctx.stroke()
    ex, ey = cx + ra * math.cos(math.radians(-160)), cy + ra * math.sin(math.radians(-160))
    # tangent of a decreasing angle at -160°: (sin, -cos)
    tx, ty = math.sin(math.radians(-160)), -math.cos(math.radians(-160))
    straight_arrow(ctx, ex - tx * 20, ey - ty * 20, ex + tx * 6, ey + ty * 6, RED, a, lw=7, head=18)
    text_c(ctx, "COUNTER-", 720, 290, 46, RED, True, 2, a)
    text_c(ctx, "CLOCKWISE", 720, 345, 46, RED, True, 2, a)
    text_c(ctx, "THEN RINSE", 720, 425, 30, BLUE, True, 2, a * sstep(t, B(11) + 4.0, 0.3))

def draw_hud(ctx, t, E):
    a = win(t, B(1) + 0.5, B(2), 0.3)
    if a > 0: front_panel(ctx, t, a)
    a = win(t, B(9) + 0.1, B(10), 0.3)
    if a > 0: calendar(ctx, t, a)
    a = win(t, B(11) + 2.3, B(12) + 0.4, 0.3)
    if a > 0: twist_panel(ctx, t, a)

SFX = [(0.3, 'pop'), (1.1, 'click'), (1.2, 'pop'), (B(1) + 1.2, 'click'), (B(2) + 0.3, 'pop'), (B(2) + 1.8, 'pop'),
       (B(3) + 0.3, 'pop'), (B(3) + 2.2, 'click'), (B(4) + 0.3, 'pop'), (B(4) + 3.8, 'click'), (B(5) + 0.3, 'pop'),
       (B(7) + 0.3, 'pop'), (B(9) + 0.8, 'pop'), (B(10) + 0.5, 'click'), (B(10) + 1.8, 'pop'),
       (B(11) + 0.2, 'pop'), (B(11) + 2.6, 'click'), (B(11) + 4.0, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_caught(ctx, t, lt, a):
    stop = lt > 2.0
    card_frame(ctx, "THE COIN TRAP", a, "WATER PASSES · COIN STAYS" if stop else "DRAINING…", TEAL)
    gx = 640
    # flow channel
    ctx.rectangle(130, 300, 820, 200); setc(ctx, WATER, 0.25 * a); ctx.fill()
    # grille: horizontal slats, gaps 14 px
    for k in range(9):
        y = 300 + k * 23
        ctx.rectangle(gx, y, 30, 9); setc(ctx, INK, a); ctx.fill()
    # water drops pass through the gaps, left -> right
    for i in range(24):
        u = (i / 24 + lt * 0.45) % 1
        row = i % 8
        y = 300 + row * 23 + 16
        x = lerp(140, 940, u)
        ctx.arc(x, y, 6, 0, 6.28); setc(ctx, WATER, a); ctx.fill_preserve(); setc(ctx, TEAL, a); ctx.set_line_width(2); ctx.stroke()
    # the coin rolls in and stops against the grille
    cxp = lerp(180, gx - 46, ease(clamp(lt / 2.0)))
    coin(ctx, cxp, 455, a, r=44)

def card_jammed(ctx, t, lt, a):
    card_frame(ctx, "NO FILTER?", a, "HUMS · NOTHING DRAINS", RED)
    cx, cy, r = 380, 395, 130
    ctx.arc(cx, cy, r, 0, 6.28); fill_stroke(ctx, FILL3, lw=5, alpha=a)
    ctx.arc(cx, cy, r - 14, 0, 6.28); setc(ctx, WATER, 0.45 * a); ctx.fill()
    j = 0.04 * math.sin(lt * 60)        # stalled: only trembles
    for k in range(5):
        a0 = -0.6 + j + k * 2 * math.pi / 5
        a1 = a0 + 0.55
        ctx.move_to(cx + 20 * math.cos(a0), cy + 20 * math.sin(a0))
        ctx.curve_to(cx + 60 * math.cos(a0 + 0.1), cy + 60 * math.sin(a0 + 0.1),
                     cx + 85 * math.cos(a1), cy + 85 * math.sin(a1), cx + 100 * math.cos(a1), cy + 100 * math.sin(a1))
        setc(ctx, TEAL, a); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.arc(cx, cy, 22, 0, 6.28); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    coin(ctx, cx + 62, cy + 52, a, r=30)                     # wedged between two vanes
    k = a * sstep(lt, 1.0, 0.3)
    for i in range(3):
        rr = 150 + 22 * i + 6 * math.sin(lt * 30 + i)
        ctx.arc(cx, cy, rr, -0.6, 0.6); setc(ctx, RED, k * (0.8 - 0.2 * i)); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "MMMMM…", 720, 340, 44, RED, True, 3, k)
    # water stays put
    ctx.rectangle(620, 400, 260, 90); setc(ctx, WATER, 0.6 * a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    text_c(ctx, "WATER STAYS", 750, 455, 26, INK, True, 1.5, a * sstep(lt, 2.2, 0.3))

CARDS = {'caught': card_caught, 'jammed': card_jammed}
