"""Cogwise episode: Potholes are made by water, not by trucks.
One idea: the hole is dug from UNDERNEATH before it opens. Rain gets in through a crack, freezes (+9 % volume),
the ice grows (it pulls more water up from below) and lifts the asphalt. When it thaws, the ice melts but the
asphalt stays up: an empty pocket under a thin lid, over soggy base. A tire just snaps the lid.
Freeze-thaw cycles (late winter / early spring) multiply them; a patch in a wet hole fails because the water is still there.

VIEW (screen coordinates, y grows DOWN): CROSS-SECTION of a road seen from the side.
  - air above y 780 (rain falls DOWN, y increasing). Asphalt from y Y_TOP=780 to Y_AS=880.
  - gravel base y 880..1160, soil (subgrade) y 1160..1500.
  - crack at x 540 through the asphalt. The pocket is centred under it (x 540 ± 190).
  - bulge(x) > 0 RAISES the asphalt: drawn y = nominal y - bulge (up on screen).
  - cavity = between the asphalt bottom (raised) and Y_AS + DEPTH*b(x) (below). Ice/water/void fill it.
  - ice pulls water UP from the soil: blue arrows point from y 1120 toward the ice (y decreasing).
  - tire rolls in from the RIGHT, moving LEFT: rotation angle = (x - x0)/R decreases -> counter-clockwise on screen.
  - lid collapse: left chunk hinged at its left end turns +angle (its right end drops, y down),
    right chunk hinged at its right end turns -angle (its left end drops), middle chunk drops straight.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="pothole-water",
    title="Potholes are made by water, not by trucks 🕳️ #Shorts",
    description=("The hole is dug from underneath long before it opens. The tire only breaks the lid.\n\n"
                 "#Shorts #howthingswork #roads #winter #cogwise"),
    hashtags=["Shorts", "howthingswork", "roads", "winter", "cogwise"],
    sources=[
        "https://pavementinteractive.org/?p=10151",
        "https://roads.maryland.gov/mdotsha/pages/index.aspx?PageId=815",
        "https://www.eurekalert.org/news-releases/1046349",
    ],
)

BEATS = [
    dict(dur=5.5, title="POTHOLES", caption="That hole wasn't made by a truck. It was dug from underneath, by water."),
    dict(dur=4.5, title="THE SECRET", caption="The secret: a pothole is hollow long before it opens."),
    dict(dur=5.8, title="1 · CRACK", caption="It starts with a hairline crack. Rain slips through, into the gravel below."),
    dict(dur=6.4, title="2 · FREEZE", caption="Below zero Celsius, thirty-two Fahrenheit, that water freezes and grows by nine percent."),
    dict(dur=5.6, title="3 · LIFT", caption="The ice pushes up and lifts the asphalt, like a fist under a blanket."),
    dict(dur=5.6, title=None, caption="It even pulls more water up from the soil, so the bump keeps growing.", card='lens'),
    dict(dur=5.2, title="4 · THAW", caption="Then it thaws. The ice melts, but the asphalt doesn't fall back."),
    dict(dur=5.8, title="THE POCKET", caption="Now there's an empty pocket under a thin lid of road, over soggy mud."),
    dict(dur=5.4, title="THE TIRE", caption="A tire rolls over. The lid has nothing under it, so it snaps."),
    dict(dur=6.6, title=None, caption="Every freeze and thaw repeats it. That's why potholes bloom in early spring, not deep winter.", card='cycle'),
    dict(dur=6.0, title="THE PATCH", caption="And a patch dropped into a wet hole? The water's still there. It comes back."),
    dict(dur=4.6, title="WATER DIGS", caption="The truck only breaks the lid. The water dug the hole."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

# ---------------------------------------------------------------- palette / geometry
ASPH = hexc('#3a373f'); ASPH_L = hexc('#55515b'); STONE = hexc('#6b6670')
PATCH = hexc('#1f1d23')
BASE = hexc('#d2b27a'); BASE_S = hexc('#a9874f')
SOIL = hexc('#8a6a48'); SOIL_D = hexc('#6d5236')
MUD = hexc('#5c4630')
WATER = hexc('#3d8fd6'); WATER_D = hexc('#1d5f99')
ICE = hexc('#e4f3f7'); ICE_D = hexc('#9fcbd8')
VOID = hexc('#17151b')
RUBBER = hexc('#26232b'); RIM = hexc('#c9c3cf')

Y_TOP, Y_AS, Y_BASE, Y_BOT = 780.0, 880.0, 1160.0, 1500.0
X0, PW, DEPTH = 540.0, 190.0, 62.0
LID = 150.0          # half width of the lid that snaps
R_TIRE = 150.0

def b(x):
    """bump profile 0..1 under the crack."""
    u = (x - X0) / PW
    return 0.5 + 0.5 * math.cos(math.pi * u) if abs(u) < 1 else 0.0

# ---------------------------------------------------------------- story state
def state(t):
    s = {}
    hook = 1 - sstep(t, B(2) + 0.05, 0.7)                    # flash-forward: the hollow, then rewind
    s['hook'] = hook
    water = sstep(t, B(2) + 1.8, 3.2)                        # rain fills the pocket
    freeze = sstep(t, B(3) + 1.6, 1.2)                       # water -> ice
    melt = sstep(t, B(6) + 0.6, 1.0)                         # ice -> water
    drain = sstep(t, B(6) + 1.8, 2.0)                        # water sinks to the bottom, leaves a void
    bulge = 16 * freeze + 22 * sstep(t, B(4) + 0.2, 2.4) + 14 * sstep(t, B(5) + 0.3, 3.0)
    bulge -= 6 * sstep(t, B(6) + 1.2, 1.4)                   # it settles only a little
    s['bulge'] = lerp(bulge, 40.0, hook)
    s['water'] = max(water, hook)
    s['ice'] = freeze * (1 - melt) * (1 - hook)
    s['void'] = max(drain, hook)
    s['mud'] = max(sstep(t, B(6) + 1.8, 2.0), hook * 0.7)
    s['crack'] = max(sstep(t, B(2) + 0.6, 0.5), hook)
    # the tire
    t_in, t_hit = B(8) + 0.2, B(8) + 1.9
    if t < t_in: tx = 1400.0
    elif t < t_hit: tx = lerp(1300.0, X0 + 20, ease(clamp((t - t_in) / (t_hit - t_in))))
    else: tx = lerp(X0 + 20, -400.0, ease(clamp((t - t_hit - 1.4) / 2.4)))
    s['tx'] = tx
    s['collapse'] = sstep(t, t_hit + 0.1, 0.55)
    # the patch
    s['patch'] = sstep(t, B(10) + 0.5, 0.8)
    s['patch_fail'] = sstep(t, B(10) + 4.0, 0.8)
    s['lens'] = win(t, B(5) + 0.3, B(6) + 0.2, 0.3)
    return s

def temp(t):
    T = 4.0
    T += -10.0 * sstep(t, B(3) + 0.3, 1.2)
    T += 11.0 * sstep(t, B(6) + 0.1, 0.8)
    return T

def cam_keys():
    return [(0, 540, 900, 1.3), (B(2) + 0.1, 540, 800, 1.0), (B(3) + 0.6, 540, 900, 1.3),
            (B(8), 540, 820, 1.0), (B(10), 540, 900, 1.25)]
def CAM(t):
    return cam_track(cam_keys(), t, 0.9)

# ---------------------------------------------------------------- drawing helpers
def xs(a, b_, n=60):
    return [a + (b_ - a) * i / n for i in range(n + 1)]

def slab_path(ctx, x0, x1, bulge):
    """asphalt slab between x0 and x1, raised by bulge*b(x)."""
    pts = xs(x0, x1)
    ctx.move_to(pts[0], Y_TOP - bulge * b(pts[0]))
    for x in pts[1:]: ctx.line_to(x, Y_TOP - bulge * b(x))
    for x in reversed(pts): ctx.line_to(x, Y_AS - bulge * b(x))
    ctx.close_path()

def cavity_path(ctx, bulge):
    pts = xs(X0 - PW, X0 + PW)
    ctx.move_to(pts[0], Y_AS)
    for x in pts: ctx.line_to(x, Y_AS - bulge * b(x))
    for x in reversed(pts): ctx.line_to(x, Y_AS + DEPTH * b(x))
    ctx.close_path()

def stones(ctx, rnd, n, x0, x1, y0, y1, rmin, rmax, cols):
    for i in range(n):
        x = rnd.uniform(x0, x1); y = rnd.uniform(y0, y1); r = rnd.uniform(rmin, rmax)
        for k in range(6):
            a = k * math.pi / 3 + rnd.uniform(-0.3, 0.3); rr = r * rnd.uniform(0.7, 1.1)
            (ctx.move_to if k == 0 else ctx.line_to)(x + rr * math.cos(a), y + rr * 0.75 * math.sin(a))
        ctx.close_path(); setc(ctx, cols[i % len(cols)]); ctx.fill()

def ground(ctx, t, s):
    ctx.rectangle(-300, Y_AS, 1680, Y_BASE - Y_AS); setc(ctx, BASE); ctx.fill()
    stones(ctx, random.Random(4), 90, -250, 1330, Y_AS + 14, Y_BASE - 10, 7, 16, [BASE_S, hexc('#bf9a5e')])
    ctx.rectangle(-300, Y_BASE, 1680, Y_BOT - Y_BASE + 20); setc(ctx, SOIL); ctx.fill()
    rnd = random.Random(9)
    for i in range(120):
        ctx.arc(rnd.uniform(-250, 1330), rnd.uniform(Y_BASE + 10, Y_BOT), rnd.uniform(2, 5), 0, 6.28)
        setc(ctx, SOIL_D); ctx.fill()
    ctx.move_to(-300, Y_BASE); ctx.line_to(1380, Y_BASE); setc(ctx, INK2, 0.6); ctx.set_line_width(3); ctx.stroke()
    # soggy base around the pocket after the thaw
    m = s['mud']
    if m > 0:
        ctx.save(); ctx.rectangle(-300, Y_AS, 1680, Y_BASE - Y_AS); ctx.clip()
        g = cairo.RadialGradient(X0, Y_AS + 40, 40, X0, Y_AS + 40, 330)
        g.add_color_stop_rgba(0, *MUD[:3], 0.85 * m); g.add_color_stop_rgba(1, *MUD[:3], 0)
        ctx.save(); ctx.scale(1, 0.55); ctx.translate(0, (Y_AS + 40) / 0.55 - (Y_AS + 40))
        ctx.arc(X0, Y_AS + 40, 330, 0, 6.28); ctx.restore(); ctx.set_source(g); ctx.fill()
        ctx.restore()

def cavity(ctx, t, s):
    bulge = s['bulge']
    if s['water'] <= 0.01 and s['void'] <= 0.01: return
    ctx.save(); cavity_path(ctx, bulge); ctx.clip()
    if s['void'] > 0:
        cavity_path(ctx, bulge); setc(ctx, VOID, s['void']); ctx.fill()
    # liquid: a full pocket before draining, a pool at the bottom after
    wa = s['water'] * (1 - s['ice'])
    if wa > 0:
        full_top = Y_AS - bulge - 2
        pool_top = Y_AS + DEPTH - 24
        y_ws = lerp(full_top, pool_top, s['void'])
        fill_h = lerp(Y_AS + DEPTH, y_ws, ease(clamp(s['water'] * 1.0)))
        ctx.rectangle(X0 - PW, fill_h, 2 * PW, 400); setc(ctx, WATER, 0.92 * wa); ctx.fill()
        ctx.move_to(X0 - PW, fill_h); ctx.line_to(X0 + PW, fill_h)
        setc(ctx, WATER_D, wa); ctx.set_line_width(3); ctx.stroke()
    if s['ice'] > 0:
        cavity_path(ctx, bulge); setc(ctx, ICE, s['ice']); ctx.fill()
        for k in range(-16, 16):
            xx = X0 + k * 22
            ctx.move_to(xx, Y_AS - 80); ctx.line_to(xx + 70, Y_AS + 80)
        setc(ctx, ICE_D, 0.9 * s['ice']); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    cavity_path(ctx, bulge); setc(ctx, INK, max(s['water'], s['void'])); ctx.set_line_width(3); ctx.stroke()

def asphalt(ctx, t, s):
    bulge, c = s['bulge'], s['collapse']
    def paint(path_fn):
        path_fn(); setc(ctx, ASPH); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    if c <= 0:
        paint(lambda: slab_path(ctx, -300, 1380, bulge))
    else:
        paint(lambda: slab_path(ctx, -300, X0 - LID, bulge))
        paint(lambda: slab_path(ctx, X0 + LID, 1380, bulge))
        # three chunks fall into the pocket
        cuts = [X0 - LID, X0 - 45, X0 + 50, X0 + LID]
        spec = [(cuts[0], 1, 16, 62), (None, 0, 0, 78), (cuts[3], -1, -18, 64)]   # hinge x, side, angle deg, drop
        for i in range(3):
            xa, xb = cuts[i], cuts[i + 1]
            hinge, side, ang, drop = spec[i]
            ctx.save()
            if hinge is None:
                ctx.translate(0, drop * c)
            else:
                hy = Y_TOP - bulge * b(hinge)
                ctx.translate(hinge, hy + drop * c * 0.75); ctx.rotate(math.radians(ang) * c); ctx.translate(-hinge, -hy)
            paint(lambda: slab_path(ctx, xa + 3, xb - 3, bulge))
            ctx.restore()
    # aggregate specks in the asphalt (only on the intact parts)
    rnd = random.Random(2)
    for i in range(80):
        x = rnd.uniform(-250, 1330); y = rnd.uniform(Y_TOP + 12, Y_AS - 12)
        if c > 0 and abs(x - X0) < LID + 4: continue
        ctx.arc(x, y - bulge * b(x), rnd.uniform(3, 6), 0, 6.28); setc(ctx, ASPH_L if i % 2 else STONE); ctx.fill()

def crack(ctx, t, s):
    a = s['crack'] * (1 - s['collapse'])
    if a <= 0: return
    bulge = s['bulge']
    y0, y1 = Y_TOP - bulge, Y_AS - bulge
    n = 6
    ctx.move_to(X0, y0)
    for i in range(1, n + 1):
        ctx.line_to(X0 + (8 if i % 2 else -8), y0 + (y1 - y0) * i / n)
    setc(ctx, hexc('#0d0c10'), a); ctx.set_line_width(7); ctx.stroke()
    # water running DOWN the crack while it rains
    r = win(t, B(2) + 1.2, B(3) + 0.4, 0.3)
    if r > 0:
        for k in range(5):
            u = ((t * 1.6 + k / 5) % 1.0)
            y = y0 + (y1 + 30 - y0) * u                   # y increases: downwards
            ctx.arc(X0, y, 6, 0, 6.28); setc(ctx, WATER, r); ctx.fill()

def rain(ctx, t, s):
    a = win(t, B(2) + 0.3, B(3) + 0.4, 0.4)
    if a <= 0: return
    rnd = random.Random(7)
    for i in range(46):
        x = rnd.uniform(40, 1040); sp = rnd.uniform(500, 700); ph = rnd.uniform(0, 460)
        y = 300 + (ph + t * sp) % (Y_TOP - 310)           # falls DOWN
        ctx.move_to(x, y); ctx.line_to(x - 4, y + 26)
        setc(ctx, WATER, 0.8 * a); ctx.set_line_width(4); ctx.stroke()

def suction(ctx, t, s):
    """water drawn UP from the soil toward the ice (arrows point up: y decreasing)."""
    a = s['lens']
    if a <= 0: return
    for k, x in enumerate((430, 540, 650)):
        u = (t * 0.8 + k * 0.33) % 1.0
        y0 = 1130 - 60 * u
        straight_arrow(ctx, x, y0, x, y0 - 120, WATER, a, lw=6, head=12)

def tire(ctx, t, s):
    x = s['tx']
    if x > 1350 or x < -350: return
    c = s['collapse']
    # rides on the surface; dips into the hole once the lid is gone and while over it
    over = clamp(1 - abs(x - X0) / LID)
    yc = Y_TOP - s['bulge'] * b(x) - R_TIRE + 60 * c * over
    rot = (x - 1300.0) / R_TIRE                     # moving left -> angle decreases -> counter-clockwise
    ctx.save(); ctx.translate(x, yc)
    ctx.arc(0, 0, R_TIRE, 0, 6.28); fill_stroke(ctx, RUBBER, lw=5)
    ctx.arc(0, 0, R_TIRE * 0.58, 0, 6.28); fill_stroke(ctx, RIM, lw=5)
    ctx.rotate(rot)
    for k in range(5):
        a = k * 2 * math.pi / 5
        ctx.move_to(0, 0); ctx.line_to(R_TIRE * 0.5 * math.cos(a), R_TIRE * 0.5 * math.sin(a))
    setc(ctx, INK); ctx.set_line_width(9); ctx.stroke()
    for k in range(16):                              # tread blocks rotate with the wheel
        a = k * 2 * math.pi / 16
        ctx.move_to(R_TIRE * 0.86 * math.cos(a), R_TIRE * 0.86 * math.sin(a))
        ctx.line_to(R_TIRE * 0.99 * math.cos(a), R_TIRE * 0.99 * math.sin(a))
    setc(ctx, ASPH_L); ctx.set_line_width(8); ctx.stroke()
    ctx.arc(0, 0, 16, 0, 6.28); fill_stroke(ctx, MUSTARD, lw=4)
    ctx.restore()
    # force arrow (down) when it hits
    a = win(t, B(8) + 1.5, B(8) + 3.0, 0.25)
    if a > 0:
        straight_arrow(ctx, x + 200, yc - 120, x + 200, yc + 40, RED, a, lw=7, head=14)

def patch(ctx, t, s):
    p = s['patch']
    if p <= 0: return
    f = s['patch_fail']
    sink = 22 * f
    bulge = s['bulge']
    top = Y_TOP - bulge * b(X0 - LID)
    hgt = (Y_AS + 20 - top) * p                 # plug stops above the trapped water
    ctx.save()
    ctx.translate(0, sink)
    ctx.move_to(X0 - LID, top); ctx.line_to(X0 + LID, top)
    ctx.line_to(X0 + LID - 10, top + hgt); ctx.line_to(X0 - LID + 10, top + hgt); ctx.close_path()
    setc(ctx, PATCH); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    if f > 0:     # it cracks again
        for x0, d in ((X0 - 70, 1), (X0 + 40, -1), (X0 + 100, 1)):
            ctx.move_to(x0, top); ctx.line_to(x0 + 14 * d, top + 40 * f); ctx.line_to(x0 - 6 * d, top + 80 * f)
        setc(ctx, hexc('#8d8794'), f); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def stage(ctx, t, s):
    rain(ctx, t, s)
    ground(ctx, t, s)
    suction(ctx, t, s)
    cavity(ctx, t, s)
    asphalt(ctx, t, s)
    crack(ctx, t, s)
    patch(ctx, t, s)
    tire(ctx, t, s)

def overlays(ctx, t, s):
    a = win(t, 0.5, B(1) + 0.2, 0.3)
    if a > 0:
        highlight(ctx, X0, Y_AS + 20, PW + 20, 80, RED, a, t)
        tag(ctx, "DUG BY WATER", X0, Y_AS + 150, RED, a, 26)
    a = win(t, B(1) + 0.2, B(2) + 0.1, 0.3)
    tag(ctx, "HOLLOW", X0, Y_AS + 150, RED, a, 30)
    tag(ctx, "THIN LID", X0, Y_TOP - 110, INK, win(t, B(1) + 1.6, B(2) + 0.1, 0.3), 26)
    a = win(t, B(2) + 0.6, B(3), 0.3)
    tag(ctx, "HAIRLINE CRACK", X0 + 210, Y_TOP - 60, INK, a, 24)
    a = win(t, B(2) + 3.0, B(3) + 0.3, 0.3)
    tag(ctx, "WATER", X0, Y_AS + 150, WATER_D, a, 26)
    a = win(t, B(3) + 2.0, B(4) + 0.2, 0.3)
    tag(ctx, "ICE", X0, Y_AS + 150, hexc('#3f8ea3'), a, 28)
    a = win(t, B(4) + 1.0, B(5), 0.3)
    if a > 0:
        for dx in (-95, 95):                       # arrows point UP (y decreasing), from the bump top
            yt = Y_TOP - s['bulge'] * b(X0 + dx) - 12
            straight_arrow(ctx, X0 + dx, yt, X0 + dx, yt - 100, RED, a, lw=7, head=14)
        tag(ctx, "LIFTED", X0, Y_TOP - 190, RED, a, 26)
    a = win(t, B(5) + 0.6, B(6), 0.3)
    tag(ctx, "WATER DRAWN UP", X0, 1270, WATER_D, a, 22)
    a = win(t, B(6) + 1.4, B(7), 0.3)
    tag(ctx, "ASPHALT STAYS UP", X0, Y_TOP - 140, INK, a, 24)
    a = win(t, B(7) + 0.3, B(8), 0.3)
    if a > 0:
        tag(ctx, "THIN LID", X0, Y_TOP - 140, INK, a, 26)
        tag(ctx, "EMPTY POCKET", X0, Y_AS + 150, RED, a * sstep(t, B(7) + 1.2, 0.3), 24)
        tag(ctx, "SOGGY MUD", X0 - 290, Y_AS + 190, hexc('#5c4630'), a * sstep(t, B(7) + 3.0, 0.3), 24)
    a = win(t, B(8) + 2.2, B(9), 0.3)
    tag(ctx, "SNAP", X0 + 270, Y_TOP - 60, RED, a, 30)
    a = win(t, B(10) + 2.4, B(11), 0.3)
    tag(ctx, "STILL WET", X0, Y_AS + 150, WATER_D, a, 26)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    stage(ctx, t, s)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def fmt_c(T):
    F = round(T * 9 / 5 + 32)
    return f"{round(T):+d} °C · {F:d} °F".replace('-', '−')

def _panel(ctx, a, x=60, y=180, w=960, h=250):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def draw_hud(ctx, t, E):
    T = temp(t)
    a = max(win(t, B(2) + 0.2, B(5), 0.3), win(t, B(6), B(8), 0.3))
    if a > 0:
        col = COLD if T < 0 else MUSTARD
        hud(ctx, "ROAD TEMPERATURE", fmt_c(T), None, a, col, x=40, y=190, w=500)
    a = win(t, B(3) + 2.2, B(4) + 0.3, 0.3)
    if a > 0:
        hud(ctx, "WATER → ICE", "+9 % VOLUME", None, a, RED, x=560, y=190, w=480)
    a = win(t, B(11) + 0.2, B(12) + 2, 0.3)
    if a > 0:
        _panel(ctx, a, x=90, y=200, w=900, h=160)
        text_c(ctx, "WATER DIGS THE HOLE", 540, 265, 46, WATER_D, True, 2, a)
        text_c(ctx, "THE TIRE ONLY BREAKS THE LID", 540, 330, 32, RED, True, 2, a * sstep(t, B(11) + 1.0, 0.3))

SFX = [(0.5, 'pop'), (B(1) + 0.2, 'pop'), (B(2) + 0.6, 'pop'), (B(2) + 3.0, 'pop'), (B(3) + 2.0, 'pop'),
       (B(3) + 2.2, 'pop'), (B(4) + 1.0, 'pop'), (B(6) + 1.4, 'pop'), (B(7) + 1.2, 'pop'), (B(7) + 3.0, 'pop'),
       (B(8) + 2.0, 'click'), (B(10) + 2.4, 'pop'), (B(11) + 0.2, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_lens(ctx, t, lt, a):
    card_frame(ctx, "ICE PULLS WATER UP", a, "THE ICE LAYER KEEPS GROWING", TEAL)
    k = ease(clamp((lt - 0.3) / 3.5))
    ice_bot = 420.0
    ice_top = 380.0 - 70 * k                   # the ice grows UP (y decreases) and lifts the road
    # soil with grains (below the ice)
    rrect(ctx, 150, ice_bot, 780, 120, 10); setc(ctx, SOIL, a); ctx.fill()
    rnd = random.Random(3)
    for i in range(46):
        ctx.arc(rnd.uniform(165, 915), rnd.uniform(ice_bot + 12, 532), rnd.uniform(6, 11), 0, 6.28)
        setc(ctx, SOIL_D, a); ctx.fill()
    # water droplets moving UP through the soil into the ice
    for i in range(12):
        x = 200 + i * 62
        u = (lt * 0.7 + i * 0.37) % 1.0
        y = 530 - (530 - ice_bot) * u           # y decreases: going up
        ctx.arc(x, y, 7, 0, 6.28); setc(ctx, WATER, a * (1 - u * 0.3)); ctx.fill()
    # the ice layer
    rrect(ctx, 150, ice_top, 780, ice_bot - ice_top, 6); fill_stroke(ctx, ICE, stroke=ICE_D, lw=4, alpha=a)
    text_c(ctx, "ICE", 540, (ice_top + ice_bot) / 2 + 12, 32, hexc('#3f8ea3'), True, 2, a)
    # the road on top, lifted
    rrect(ctx, 130, ice_top - 34, 820, 34, 6); fill_stroke(ctx, ASPH, lw=4, alpha=a)
    for x in (230, 850):
        straight_arrow(ctx, x, ice_top - 40, x, ice_top - 40 - 40 * k - 10, RED, a * k, lw=6, head=12)

def card_cycle(ctx, t, lt, a):
    card_frame(ctx, "WHY SPRING?", a, "EVERY 0 °C CROSSING = ONE MORE CYCLE", RED)
    x0, x1, y0 = 150, 930, 410                 # zero line; warmer = higher on screen (y smaller)
    ctx.move_to(x0, y0); ctx.line_to(x1, y0); ctx.set_dash([10, 8]); setc(ctx, INK2, a); ctx.set_line_width(3)
    ctx.stroke(); ctx.set_dash([])
    text_c(ctx, "0 °C · 32 °F", 220, y0 - 12, 20, INK2, True, 1, a)
    text_c(ctx, "DEEP WINTER: FROZEN", 330, 530, 22, COLD, True, 1, a)
    text_c(ctx, "EARLY SPRING", 760, 530, 22, RED, True, 1, a)
    def T(x):
        if x < 520: return 480 + 8 * math.sin(x / 30.0)
        u = (x - 520) / 410
        return lerp(480, 420, min(u * 4, 1)) + (-70) * math.sin((x - 520) / 36.0) * min(u * 4, 1)
    k = ease(clamp((lt - 0.2) / 3.0))
    xe = lerp(x0, x1, k)
    ctx.move_to(x0, T(x0)); x = x0
    while x < xe:
        x += 4; ctx.line_to(x, T(x))
    setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    # crossings
    prev = T(x0) > y0
    x = x0
    while x < xe:
        x += 2
        cur = T(x) > y0
        if cur != prev:
            ctx.arc(x, y0, 10, 0, 6.28); fill_stroke(ctx, RED, lw=3, alpha=a)
        prev = cur

CARDS = {'lens': card_lens, 'cycle': card_cycle}
