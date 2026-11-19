"""Cogwise episode: This truck is most dangerous when it's half empty.
One idea: in a part-filled tank, braking stops the truck but not the liquid. It surges forward as one wave, slams
the front wall and shoves the truck forward (on ice, a stopped truck can be pushed into an intersection), then
rocks it back and forth. Full = no room to move, empty = nothing to push. Baffles (walls with holes) chop the wave.

VIEW (screen coordinates, y grows DOWN): side view, the truck drives to the RIGHT (cab on the right).
  - Braking = deceleration: the liquid keeps going RIGHT, piles up at the FRONT wall (right end of the tank).
  - Surface tilt A: A > 0 means the liquid is HIGHER at the front (right): y_surface(x) = YC - A*S*(x - XM)/HL
    (x > XM and A > 0 -> smaller y -> higher on screen). Volume is kept because the tilt pivots at the middle.
  - Wave push on the front wall = force to the RIGHT (forward). Truck offset dx > 0 = pushed forward.
  - Brake friction on the road acts on the truck to the LEFT (backward).
  - Road dashes / posts move LEFT while the truck drives right.
Sources: Oregon CDL manual section 8; Pennsylvania CDL manual pub 223 section 8; SafeRack tank-truck surge.
"""
import math, cairo
from cogwise.style import *

META = dict(
    slug="tanker-baffles",
    title="This truck is most dangerous when it's half empty 🚚 #Shorts",
    description=("When the truck stops, the liquid inside doesn't.\n\n"
                 "#Shorts #howthingswork #trucks #physics #cogwise"),
    hashtags=["Shorts", "howthingswork", "trucks", "physics", "cogwise"],
    sources=[
        "https://oregon.gov/odot/dmv/pages/online_cdl_manual/section_8.aspx",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dmv/documents/driver-services/commercial-drivers/pub%20223%20-%20section%208.pdf",
        "https://www.saferack.com/road-tanker-safety-design-equipment-human-factor/tank-truck-surge-provention/",
    ],
)

def _d(c, extra=0.0):
    return round(0.42 * len(c.split()) + 0.7 + extra, 1)

_B = [
    ("HALF FULL", "A full tanker is safe. An empty one too. Half full is the problem.", None),
    ("THE SECRET", "When the driver brakes, the truck slows down, but the liquid inside keeps going.", None),
    ("THE WAVE", "It rushes forward as one heavy wave and slams into the front wall.", None),
    (None, "That hit shoves the whole truck forward, even with the brakes on.", 'push'),
    ("BACK AND FORTH", "Then the wave bounces back, hits the rear wall, and returns. The truck rocks.", None),
    ("ON ICE", "On an icy road, that wave can push a stopped tanker out into an intersection.", None),
    ("WHY HALF?", "Full, the liquid has no room to move. Empty, there's nothing to push. Half full, it's a battering ram.", None),
    ("HIDDEN WALLS", "That's why most tankers hide walls inside, called baffles.", None),
    (None, "Each baffle is full of holes. Liquid still gets through, but only slowly.", 'holes'),
    ("SMALL WAVES", "The big wave is chopped into small ones, and each wall takes its own little hit.", None),
    ("MOVING WEIGHT", "So the danger isn't the weight. It's weight that keeps moving after you stop.", None),
]
BEATS = [dict(dur=_d(c), title=ti, caption=c, card=k) for ti, c, k in _B]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette
STEEL = hexc('#c9ced6'); STEEL_D = hexc('#7d838c'); STEEL_L = hexc('#e6e9ee')
LIQ = hexc('#2f6fb3'); LIQ_L = hexc('#8fb8e0'); LIQ_D = hexc('#1f4f86')
TYRE = hexc('#2b2830'); HUB = hexc('#b9bec6')
ICE = hexc('#cfe8f2'); GREEN = hexc('#3d8b4f')

# ---------------------------------------------------------------- geometry (side view)
GROUND = 1478
TX0, TX1 = 50, 740        # tank outer x
TY0, TY1 = 940, 1320     # tank outer y
TR = 150                  # end radius
IN = 14                   # wall thickness
XM = (TX0 + TX1) / 2; HL = (TX1 - TX0) / 2 - IN
YC = (TY0 + TY1) / 2 + 10  # liquid level at rest (half full)
S = 150                   # max surface rise at the wall (px) for A = 1
BAFX = [TX0 + IN + (TX1 - TX0 - 2 * IN) * k / 5 for k in range(1, 5)]
WHEELS = [(180, 'r'), (320, 'r'), (920, 'f')]
WR = 60

# ---------------------------------------------------------------- the slosh (unbaffled tank)
OM = 2 * math.pi / 3.2    # sloshing period ~3.2 s (design time)
def osc(u, a0=1.0, k=0.32):
    return a0 * math.cos(OM * u) * math.exp(-k * u) if u >= 0 else a0

def tilt(t):
    """A(t): +1 = piled up at the FRONT (right)."""
    if t < B(1):                                  # hook: brake at 0.3, the wave slams the front by ~1.2 s
        u = t - 0.3
        if u < 0: return 0.0
        if u < 0.9: return 0.95 * ease(u / 0.9)
        return osc(u - 0.9, 0.95)
    if t < B(2):                                  # drive, brake at +1.6, liquid "keeps going" (starts to lean)
        u = t - (B(1) + 1.6)
        return 0.0 if u < 0 else 0.35 * ease(u / 2.0)
    if t < B(4):                                  # the wave rushes forward and slams, then held through the card
        u = t - B(2)
        return 0.35 + 0.65 * ease(u / 1.8)
    if t < B(5):                                  # back and forth
        return osc(t - B(4), 1.0, 0.18)
    if t < B(6):                                  # on ice: a fresh stop, the wave shoves the stopped truck
        u = t - B(5) - 0.3
        if u < 0: return 0.0
        if u < 0.8: return ease(u / 0.8)
        return osc(u - 0.8, 1.0, 0.15)
    if t < B(7):
        return osc(t - B(6) + 3.0, 0.5, 0.3)      # dying slosh behind the panel
    return 0.0

def baf_tilt(t):
    """Baffled tank: brake again at B(9)+0.3, each compartment gets a small, fast, quickly damped wave."""
    u = t - B(9) - 0.3
    if u < 0: return 0.0
    if u < 0.5: return ease(u / 0.5)
    v = u - 0.5
    return math.cos(2 * math.pi * v / 1.1) * math.exp(-1.1 * v)

def driving(t):
    """Road speed (0..1) for the motion cues."""
    if t < B(1): return 1.0 - ease(clamp((t - 0.1) / 0.6))
    if t < B(2): return 1.0 - ease(clamp((t - B(1) - 1.6) / 1.4))
    if B(9) <= t < B(10): return 1.0 - ease(clamp((t - B(9) - 0.2) / 0.8))
    return 0.0

def road_pos(t):
    """Integrated road travel (px) for dashes."""
    acc, dt, x = 0.0, 0.05, 0.0
    while x < t:
        acc += driving(x) * 900 * dt; x += dt
    return acc

def truck_dx(t):
    """Truck offset (px, + = forward/right)."""
    if t < B(1):
        u = t - 1.2
        return 0.0 if u < 0 else 20 * ease(u / 0.5) - 8 * ease(clamp((u - 0.8) / 1.0))
    if B(2) + 1.4 <= t < B(4):
        return 22 * ease(clamp((t - B(2) - 1.4) / 0.6))
    if B(4) <= t < B(5):
        return 22 + 14 * tilt(t) - 14
    if B(5) <= t < B(6):
        u = t - B(5) - 1.1
        if u < 0: return -110.0
        # ratchet forward on every forward surge, barely back on the rear hits (ice)
        steps = 0.0
        for k in range(4):
            steps += (1.0 / (k + 1)) * ease(clamp((u - k * 3.2) / 0.9))
        return -110 + 90 * steps
    if t >= B(6) and t < B(7):
        return 0.0
    return 0.0

# ---------------------------------------------------------------- drawing helpers
def tank_path(ctx, x0, y0, x1, y1, r):
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, r)

def liquid(ctx, t, x0, y0, x1, y1, r, yc, amp, A, ripple=1.0, a=1.0):
    """Liquid in a stadium-shaped tank, surface tilted by A (A>0: higher on the RIGHT)."""
    xm = (x0 + x1) / 2; hl = (x1 - x0) / 2
    ctx.save()
    tank_path(ctx, x0, y0, x1, y1, r); ctx.clip()
    n = 60
    ctx.move_to(x0 - 5, y1 + 5)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = yc - A * amp * (x - xm) / hl + ripple * 4 * math.sin(x / 26 - t * 5)
        ctx.line_to(x, y)
    ctx.line_to(x1 + 5, y1 + 5); ctx.close_path()
    g = cairo.LinearGradient(0, yc - amp, 0, y1)
    g.add_color_stop_rgb(0, *LIQ_L[:3]); g.add_color_stop_rgb(1, *LIQ[:3])
    ctx.set_source(g); ctx.fill()
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = yc - A * amp * (x - xm) / hl + ripple * 4 * math.sin(x / 26 - t * 5)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    setc(ctx, LIQ_D, a); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def wheel(ctx, x, y, rot):
    ctx.arc(x, y, WR, 0, 2 * math.pi); fill_stroke(ctx, TYRE, lw=4)
    ctx.arc(x, y, WR * 0.5, 0, 2 * math.pi); fill_stroke(ctx, HUB, lw=3)
    for k in range(5):
        a = rot + k * 2 * math.pi / 5
        ctx.arc(x + WR * 0.32 * math.cos(a), y + WR * 0.32 * math.sin(a), 3.5, 0, 2 * math.pi)
        setc(ctx, INK); ctx.fill()

def truck(ctx, t, dx, baffles=0.0, A=0.0, Ab=0.0, show_liq=True, level=None):
    ctx.save(); ctx.translate(dx, 0)
    # chassis
    ctx.rectangle(30, 1322, 1010, 30); fill_stroke(ctx, INK2, lw=4)
    # mudguards
    for x, _ in WHEELS:
        ctx.arc(x, GROUND - WR, WR + 12, math.pi, 2 * math.pi); setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()
    # wheels (rotate clockwise when driving right = increasing angle)
    rot = road_pos(t) / WR
    for x, _ in WHEELS:
        wheel(ctx, x, GROUND - WR, rot)
    # cab (front on the right)
    ctx.move_to(760, 1352); ctx.line_to(760, 1060); ctx.line_to(930, 1060)
    ctx.line_to(1025, 1180); ctx.line_to(1040, 1352); ctx.close_path()
    fill_stroke(ctx, RED, lw=5)
    ctx.move_to(840, 1085); ctx.line_to(918, 1085); ctx.line_to(985, 1175); ctx.line_to(840, 1175); ctx.close_path()
    fill_stroke(ctx, hexc('#cfe3ea'), lw=4)
    ctx.rectangle(1028, 1270, 18, 34); fill_stroke(ctx, MUSTARD, lw=3)     # headlight
    ctx.rectangle(775, 1210, 50, 8); setc(ctx, INK); ctx.fill()           # door handle
    # tank shell (cutaway): outer shell, interior
    tank_path(ctx, TX0, TY0, TX1, TY1, TR); fill_stroke(ctx, STEEL, lw=5)
    tank_path(ctx, TX0 + IN, TY0 + IN, TX1 - IN, TY1 - IN, TR - IN); fill_stroke(ctx, hexc('#f7f3ea'), INK2, lw=2)
    yc = YC if level is None else level
    if show_liq:
        if baffles >= 0.99 and Ab != 0.0:
            xs = [TX0 + IN] + BAFX + [TX1 - IN]
            for k in range(5):
                ctx.save()
                ctx.rectangle(xs[k], TY0, xs[k + 1] - xs[k], TY1 - TY0); ctx.clip()
                xm = (xs[k] + xs[k + 1]) / 2; hl = (xs[k + 1] - xs[k]) / 2
                # each compartment pivots on its own middle: small, separate waves
                ctx.save(); tank_path(ctx, TX0 + IN, TY0 + IN, TX1 - IN, TY1 - IN, TR - IN); ctx.clip()
                n = 20
                ctx.move_to(xs[k], TY1);
                for i in range(n + 1):
                    x = xs[k] + (xs[k + 1] - xs[k]) * i / n
                    y = yc - Ab * 36 * (x - xm) / hl + 3 * math.sin(x / 20 - t * 6)
                    ctx.line_to(x, y)
                ctx.line_to(xs[k + 1], TY1); ctx.close_path()
                g = cairo.LinearGradient(0, yc - 40, 0, TY1)
                g.add_color_stop_rgb(0, *LIQ_L[:3]); g.add_color_stop_rgb(1, *LIQ[:3])
                ctx.set_source(g); ctx.fill()
                for i in range(n + 1):
                    x = xs[k] + (xs[k + 1] - xs[k]) * i / n
                    y = yc - Ab * 36 * (x - xm) / hl + 3 * math.sin(x / 20 - t * 6)
                    (ctx.move_to if i == 0 else ctx.line_to)(x, y)
                setc(ctx, LIQ_D); ctx.set_line_width(4); ctx.stroke()
                ctx.restore(); ctx.restore()
        else:
            liquid(ctx, t, TX0 + IN, TY0 + IN, TX1 - IN, TY1 - IN, TR - IN, yc, S, A)
    if baffles > 0:
        baffle_plates(ctx, t, baffles)
    # shell outline on top + top hatch
    tank_path(ctx, TX0, TY0, TX1, TY1, TR); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.rectangle(360, TY0 - 28, 70, 28); fill_stroke(ctx, STEEL_D, lw=4)
    ctx.restore()

def baffle_plates(ctx, t, p):
    """Vertical walls with holes (holes = gaps in the plate), drawn growing from the top."""
    top, bot = TY0 + IN, TY1 - IN
    holes = [(YC - 90, 16), (YC + 30, 26), (YC + 110, 16)]
    for k, x in enumerate(BAFX):
        q = clamp(p * 1.6 - k * 0.15)
        if q <= 0: continue
        yend = top + (bot - top) * ease(q)
        segs = []; y = top
        for hy, hr in holes:
            if hy - hr > y: segs.append((y, min(hy - hr, yend)))
            y = hy + hr
        segs.append((y, yend))
        for a0, a1 in segs:
            if a1 <= a0: continue
            ctx.rectangle(x - 5, a0, 10, a1 - a0); fill_stroke(ctx, MUSTARD, lw=2.5)

def road(ctx, t, ice=0.0):
    pos = road_pos(t)
    # lane dashes on the dark floor, moving LEFT as the truck drives right
    for k in range(-1, 8):
        x = (k * 180 - pos) % 1260 - 120
        ctx.rectangle(x, 1568, 90, 12); setc(ctx, CREAM, 0.85); ctx.fill()
    if ice > 0:
        for x0, w in ((0, 330), (400, 380), (830, 250)):
            rrect(ctx, x0, 1503, w, 34, 10); setc(ctx, ICE, 0.9 * ice); ctx.fill()
            for j in range(3):
                ctx.move_to(x0 + 30 + j * w / 3, 1512); ctx.line_to(x0 + 80 + j * w / 3, 1512)
                setc(ctx, WHITE, ice); ctx.set_line_width(3); ctx.stroke()

STOPX = 985
def stop_line(ctx, a):
    if a <= 0: return
    ctx.rectangle(STOPX, 1500, 26, 140); setc(ctx, WHITE, a); ctx.fill()
    tag(ctx, "STOP LINE", STOPX - 60, 1606, INK, a, 24)

# ---------------------------------------------------------------- state & draw
def state(t):
    s = {}
    s['half'] = win(t, 0.2, B(1), 0.3)
    s['push0'] = win(t, 1.0, B(1), 0.25)
    s['brakes'] = max(win(t, B(1) + 1.5, B(2), 0.3), win(t, B(9) + 0.2, B(9) + 2.2, 0.3))
    s['keeps'] = win(t, B(1) + 1.8, B(2) + 0.6, 0.3)
    s['wave'] = bw(t, 2)
    s['slam'] = win(t, B(2) + 1.4, B(3), 0.25)
    s['rock'] = bw(t, 4)
    s['ice'] = win(t, B(5) - 0.2, B(6) + 0.2, 0.4)
    s['iceTag'] = bw(t, 5)
    s['baff'] = clamp((t - B(7) - 0.3) / 2.2) if t >= B(7) else 0.0
    s['baffTag'] = bw(t, 7)
    s['small'] = bw(t, 9)
    return s

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    road(ctx, t, s['ice'])
    stop_line(ctx, s['ice'])
    A = tilt(t)
    Ab = baf_tilt(t) if t >= B(9) else 0.0
    dx = truck_dx(t)
    truck(ctx, t, dx, baffles=s['baff'], A=A, Ab=Ab)
    overlays(ctx, t, s, A, dx)

def front_wall_x(dx): return TX1 - IN + dx

def push_arrow(ctx, dx, a, y=1000):
    straight_arrow(ctx, 790 + dx, y, 990 + dx, y, RED, a, lw=12, head=20)

def overlays(ctx, t, s, A, dx):
    a = s['half']
    if a > 0:
        tag(ctx, "HALF FULL", 395, 870, LIQ_D, a, 30)
    a = s['push0']
    if a > 0:
        push_arrow(ctx, dx, a)
        tag(ctx, "PUSHED", 890, 935, RED, a, 30)
    a = s['brakes']
    if a > 0:
        for x, _ in WHEELS:
            straight_arrow(ctx, x + 45 + truck_dx(t), GROUND + 22, x - 55 + truck_dx(t), GROUND + 22, MUSTARD, a, lw=8, head=13)
        tag(ctx, "BRAKES", 250, 1606, MUSTARD, a, 26)
    a = s['keeps']
    if a > 0:
        u = (t * 160) % 240
        for y in (YC + 60, YC + 130):
            straight_arrow(ctx, 160 + u, y, 270 + u, y, WHITE, a, lw=9, head=15)
        tag(ctx, "KEEPS GOING", 395, 870, LIQ_D, a, 30)
    a = s['wave']
    if a > 0:
        tag(ctx, "ONE HEAVY WAVE", 395, 870, LIQ_D, a, 30)
    a = s['slam']
    if a > 0:
        highlight(ctx, front_wall_x(dx) - 25, YC - 60, 60, 150, RED, a, t)
        push_arrow(ctx, dx, a)
        tag(ctx, "SLAM", 890, 935, RED, a, 30)
        for k in range(6):
            ph = (t * 1.8 + k / 6) % 1.0
            x = front_wall_x(dx) - 40 - 30 * k * ph
            y = YC - S + 20 - 70 * math.sin(math.pi * ph)
            ctx.arc(x, y, 8, 0, 2 * math.pi); setc(ctx, LIQ_L, a * (1 - ph)); ctx.fill()
    a = s['rock']
    if a > 0:
        if A > 0.25:
            push_arrow(ctx, dx, a * min(1, A * 1.5), y=880)
        elif A < -0.25:
            straight_arrow(ctx, 260 + dx, 880, 60 + dx, 880, RED, a * min(1, -A * 1.5), lw=12, head=20)
        tag(ctx, "REAR", 150, 800, INK, a, 26); tag(ctx, "FRONT", 890, 800, INK, a, 26)
    a = s['iceTag']
    if a > 0:
        tag(ctx, "ICE", 170, 1606, TEAL, a, 26)
        tag(ctx, "BRAKES ON · STILL SLIDING", 540, 820, RED, a * clamp((t - B(5) - 1.2) / 0.4), 28)
        if A > 0.3:
            push_arrow(ctx, dx, a)
    a = s['baffTag']
    if a > 0:
        tag(ctx, "BAFFLES", 395, 860, MUSTARD, a, 32)
        for x in BAFX[1:3]:
            straight_arrow(ctx, 395 + (x - 395) * 0.4, 885, x, TY0 + 30, MUSTARD, a, lw=5, head=11)
    a = s['small']
    if a > 0:
        tag(ctx, "SMALL WAVES", 395, 860, LIQ_D, a, 30)
        tag(ctx, "TRUCK STAYS PUT", 880, 990, GREEN, a * clamp((t - B(9) - 1.5) / 0.5), 24)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=180, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def mini_tank(ctx, t, cx, cy, fill, A, a, label, col, arrow=0.0):
    w, h = 250, 110
    x0, y0 = cx - w / 2, cy - h / 2
    ctx.push_group()
    tank_path(ctx, x0, y0, x0 + w, y0 + h, 50); fill_stroke(ctx, hexc('#f7f3ea'), INK2, lw=2)
    if fill > 0:
        yc = y0 + h * (1 - fill)
        amp = 34 * (1 - abs(2 * fill - 1)) ** 0.5 if 0 < fill < 1 else 0
        liquid(ctx, t, x0, y0, x0 + w, y0 + h, 50, yc, max(amp, 0.01), A, ripple=0.4 if fill < 0.97 else 0.0)
    tank_path(ctx, x0, y0, x0 + w, y0 + h, 50); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    text_c(ctx, label, cx, cy + h / 2 + 46, 24, col, True, 1, a)
    if arrow > 0:
        straight_arrow(ctx, cx + w / 2 + 6, cy, cx + w / 2 + 6 + 50 * arrow, cy, RED, a, lw=4 + 6 * arrow, head=8 + 8 * arrow)

def why_panel(ctx, t, a):
    _panel(ctx, a, y=180, h=320)
    lt = t - B(6)
    a1 = a * clamp((lt - 0.2) / 0.4)
    a2 = a * clamp((lt - 1.8) / 0.4)
    a3 = a * clamp((lt - 3.4) / 0.4)
    sl = osc((lt - 3.4) % 3.2, 1.0, 0.0)
    mini_tank(ctx, t, 205, 300, 1.0, 0.0, a1, "FULL: NO ROOM", INK, 0.0)
    mini_tank(ctx, t, 520, 300, 0.0, 0.0, a2, "EMPTY: NO WEIGHT", INK, 0.0)
    mini_tank(ctx, t, 835, 300, 0.5, sl, a3, "HALF: BIG WAVE", RED, max(0.0, sl) if lt > 3.4 else 0.0)

def recap_panel(ctx, t, a):
    _panel(ctx, a, y=185, h=190)
    text_c(ctx, "NOT THE WEIGHT...", 540, 262, 44, INK, True, 3, a)
    text_c(ctx, "THE WEIGHT THAT MOVES", 540, 335, 46, RED, True, 3, a)

def draw_hud(ctx, t, E):
    a = win(t, B(6) + 0.1, B(7), 0.3)
    if a > 0: why_panel(ctx, t, a)
    a = win(t, B(10) + 0.4, B(11) + 2, 0.3)
    if a > 0: recap_panel(ctx, t, a)

SFX = [(0.3, 'click'), (1.0, 'pop'), (B(1) + 1.6, 'click'), (B(2) + 1.4, 'pop'), (B(4) + 0.3, 'pop'),
       (B(5) + 1.2, 'pop'), (B(6) + 0.2, 'pop'), (B(6) + 1.8, 'pop'), (B(6) + 3.4, 'pop'),
       (B(7) + 0.5, 'pop'), (B(9) + 0.3, 'click'), (B(10) + 0.4, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_push(ctx, t, lt, a):
    """Forces at the stop: the wave pushes the FRONT wall forward (right); the brakes pull the wheels back (left)."""
    card_frame(ctx, "AT THE FRONT WALL", a, "THE WAVE SHOVES THE TRUCK FORWARD", RED)
    x0, y0, x1, y1 = 180, 270, 760, 480
    tank_path(ctx, x0, y0, x1, y1, 90); fill_stroke(ctx, hexc('#f7f3ea'), INK, lw=5, alpha=a)
    A = 0.85 + 0.1 * math.sin(lt * 3)
    ctx.push_group()
    liquid(ctx, t, x0 + 8, y0 + 8, x1 - 8, y1 - 8, 82, (y0 + y1) / 2 + 10, 85, A)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    tank_path(ctx, x0, y0, x1, y1, 90); setc(ctx, INK, a); ctx.set_line_width(6); ctx.stroke()
    # impact on the front wall (right), arrow forward
    p = 0.5 + 0.5 * math.sin(lt * 6)
    ctx.arc(x1 - 20, (y0 + y1) / 2 - 30, 40 + 6 * p, -1.0, 1.0); setc(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
    straight_arrow(ctx, x1 + 10, 360, x1 + 170, 360, RED, a, lw=12, head=20)
    text_c(ctx, "WAVE PUSH", x1 + 95, 330, 22, RED, True, 1, a)
    # brakes: friction at the road, backward
    ctx.move_to(130, 520); ctx.line_to(950, 520); setc(ctx, INK2, a); ctx.set_line_width(4); ctx.stroke()
    for wx in (300, 640):
        ctx.arc(wx, 500, 20, 0, 2 * math.pi); fill_stroke(ctx, TYRE, lw=3, alpha=a)
    straight_arrow(ctx, 410, 510, 330, 510, MUSTARD, a, lw=7, head=12)
    text_c(ctx, "BRAKES", 470, 500, 20, MUSTARD, True, 1, a)
    text_c(ctx, "DRIVING", 870, 270, 20, INK2, True, 1, a)
    straight_arrow(ctx, 820, 285, 920, 285, INK2, a, lw=4, head=8)

def card_holes(ctx, t, lt, a):
    """Zoom on one baffle (side view): the wave arrives from the left (rear side) heading forward (right);
    only thin jets pass through the holes, the rest of the wave hits the plate."""
    card_frame(ctx, "INSIDE · ONE BAFFLE", a, "THROUGH THE HOLES, SLOWLY", MUSTARD)
    x0, x1, y0, y1 = 130, 950, 255, 540
    xb = 560
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); fill_stroke(ctx, hexc('#f7f3ea'), INK2, lw=2, alpha=a)
    # left side: liquid piled against the plate; right side: lower, slowly rising
    rise = clamp(lt / 4.0)
    yl = 340 + 6 * math.sin(lt * 4)
    yr = 470 - 40 * rise
    ctx.move_to(x0, y1); ctx.line_to(x0, yl + 60)
    for i in range(21):
        x = x0 + (xb - x0) * i / 20
        ctx.line_to(x, yl + 60 * (1 - i / 20) + 4 * math.sin(x / 20 - lt * 5))
    ctx.line_to(xb, y1); ctx.close_path(); setc(ctx, LIQ, a); ctx.fill()
    ctx.rectangle(xb, yr, x1 - xb, y1 - yr); setc(ctx, LIQ, a); ctx.fill()
    # plate with holes (gaps)
    holes = [(330, 14), (420, 18), (490, 14)]
    yy = y0
    for hy, hr in holes:
        ctx.rectangle(xb - 10, yy, 20, hy - hr - yy); fill_stroke(ctx, MUSTARD, lw=3, alpha=a)
        yy = hy + hr
    ctx.rectangle(xb - 10, yy, 20, y1 - yy); fill_stroke(ctx, MUSTARD, lw=3, alpha=a)
    # thin jets through the holes (only the ones under the left surface)
    for hy, hr in holes:
        if hy < yl - 10: continue
        for k in range(4):
            ph = (lt * 0.9 + k / 4) % 1.0
            x = xb + 12 + 110 * ph
            y = hy + 30 * ph * ph
            ctx.arc(x, y, 6, 0, 2 * math.pi); setc(ctx, LIQ_L, a * (1 - 0.6 * ph)); ctx.fill()
    straight_arrow(ctx, 200, 300, 400, 300, RED, a, lw=9, head=16)
    text_c(ctx, "WAVE", 300, 285, 22, RED, True, 1, a)
    text_c(ctx, "FRONT", 860, 290, 20, INK2, True, 1, a)
    straight_arrow(ctx, 900, 284, 940, 284, INK2, a, lw=3, head=7)

CARDS = {'push': card_push, 'holes': card_holes}
