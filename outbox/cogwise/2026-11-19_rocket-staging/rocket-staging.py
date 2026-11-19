"""Cogwise episode: Rockets throw away half of themselves on purpose.
One idea: an empty fuel tank is dead weight. Every kilo still on board must be accelerated, which costs
fuel, so once the first stage has drunk its propellant (Falcon 9: ~2 min 30 s), the whole bottom part
(25.6 t dry, tank + 9 engines + interstage) is dropped and the light second stage carries on.

VIEW (screen coordinates, y grows DOWN): a Falcon 9-like rocket seen from the SIDE, in cross-section,
nose UP (smaller y), engines DOWN (bigger y). It flies UP: the rocket stays in frame and the clouds /
speed lines move DOWN (+y) past it. Thrust points UP (-y), flames and weight point DOWN (+y).
Stack, top to bottom: fairing (payload inside) 330-520 · stage 2 (LOX tank above RP-1) 520-740 ·
interstage (black, belongs to stage 1, hides the stage-2 vacuum nozzle) 740-810 · stage 1 LOX tank
(upper) 820-1050 · stage 1 RP-1 tank (lower) 1060-1290 · engine bay 1290-1360 · 3 of the 9 nozzles
visible side-on 1360-1420.
SEPARATION: stage 1 (with the interstage) moves DOWN (+y) and tilts away; stage 2 stays, its single
engine lights below it. Liquids: LOX pale teal, RP-1 kerosene mustard.
TIMELINE: beats 1-2 = teaser (stage 1 already empty, drifting off). Beat 3 = back to liftoff, full.
Beat 6 = burn, levels drop. Beat 7 = empty. Beat 9 = latches open, stage 1 falls. Beat 10 = stage 2
lights. Beat 12 = recap (stage 2 up, stage 1 left behind).
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="rocket-staging",
    title="Rockets throw away half of themselves on purpose 🚀 #Shorts",
    description=("An empty fuel tank is just dead weight. So rockets drop it.\n\n"
                 "#Shorts #howthingswork #rocket #space #cogwise"),
    hashtags=["Shorts", "howthingswork", "rocket", "space", "spacex", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Falcon_9",
        "https://www.grc.nasa.gov/www/K-12/rocket/TRCRocket/balloon_staging.html",
        "https://discovermagazine.com/the-sciences/the-how-and-why-of-rockets-staging",
    ],
)

BEATS = [
    dict(dur=5.1, title="HALF?", caption="Every rocket you've seen throws away half of itself. On purpose."),
    dict(dur=4.4, title="THE SECRET", caption="Because an empty fuel tank is just dead weight."),
    dict(dur=5.9, title="DEAD WEIGHT", caption="Every kilo the rocket carries must be pushed faster, and pushing costs fuel."),
    dict(dur=7.1, title="1 · FIRST STAGE", caption="On a Falcon 9, the bottom part is the first stage: a giant tank, nine engines."),
    dict(dur=6.8, title="2 · THE TANK", caption="Filled up, fuel is ninety-four percent of its weight. The metal is a thin shell."),
    dict(dur=6.3, title="BURN", caption="For two and a half minutes, the engines drink that fuel. The levels drop."),
    dict(dur=6.4, title="THE PROBLEM", caption="Now the rocket hauls twenty-five tonnes, fifty-six thousand pounds, of empty tank and engines."),
    dict(dur=5.5, title=None, caption="Keep it, and every bit of thrust wastes effort pushing empty metal.", card='waste'),
    dict(dur=5.5, title="SEPARATION", caption="Latches release, and the whole bottom falls away. Tank and engines, gone."),
    dict(dur=6.3, title="3 · SECOND STAGE", caption="The small top stage lights a single engine. It has far less to push."),
    dict(dur=5.5, title=None, caption="Now every drop of fuel speeds up the payload, not an empty tank.", card='payload'),
    dict(dur=4.8, title="HALF = FASTER", caption="Throwing half away is how a rocket gets all the way up."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette / geometry
SKY1 = hexc('#d6ebe6'); SKY2 = hexc('#f6ecd6')
BODY = hexc('#fbf5e8'); SHELL = hexc('#d9d4cb'); DARK = hexc('#3b3842')
LOX = hexc('#a9dcd5'); RP1 = hexc('#f4c86a')
STEEL = hexc('#b9bec4'); STEEL_D = hexc('#7d848b')
RX, HW = 540, 62                     # rocket axis, body half-width
Y_TIP, Y_FB = 330, 520               # fairing tip / fairing base
Y_S2B = 740                          # bottom of stage 2 = top of interstage (separation plane)
Y_IS = 810                           # bottom of interstage = top of stage-1 tanks
S1_LOX = (820, 1050); S1_RP = (1060, 1290)
Y_EB = 1360                          # bottom of engine bay
S2_LOX = (528, 626); S2_RP = (634, 732)
MV_TOP, MV_BOT = 742, 806            # stage-2 vacuum nozzle (inside the interstage)

def sep_k(t):
    """0 = attached, >0 = stage 1 gone; returns (dy, rot) of stage 1"""
    if t < B(2):                                         # teaser: drifts down a little, tilts
        k = ease(clamp((t - 0.9) / 2.2))
        return 170 * k, 0.10 * k
    if t < B(8) + 0.9:
        return 0.0, 0.0
    if t < B(11):                                        # real separation: falls out of frame
        u = t - (B(8) + 0.9)
        return 40 * u + 60 * u * u, 0.05 * u
    lt = t - B(11)                                       # recap: far below, still falling
    return 400 + 40 * lt, 0.30 + 0.03 * lt

def fuel1(t):
    if t < B(2): return 0.04                             # teaser: already empty
    if t < B(5) + 0.4: return 1.0
    return lerp(1.0, 0.04, ease(clamp((t - B(5) - 0.4) / (B(6) - B(5) - 0.8))))

def fuel2(t):
    if t < B(9) + 0.6: return 1.0
    return lerp(1.0, 0.62, clamp((t - B(9) - 0.6) / (B(12) - B(9))))

def flame1(t):
    """stage-1 engines: 0 off .. 1 normal .. 1.3 big"""
    if t < B(2): return 0.0
    if t < B(5): return 1.0
    if t < B(6) - 0.2: return 1.3
    return 1.0 - ease(clamp((t - (B(6) - 0.2)) / 0.5)) if t < B(8) else 0.0

def flame2(t):
    if t < B(2): return ease(clamp((t - 1.9) / 0.4))     # teaser: stage 2 lights after the drop
    if t < B(9) + 0.5: return 0.0
    return ease(clamp((t - B(9) - 0.5) / 0.4))

def speed(t):
    """how fast clouds / speed lines stream down (= the rocket climbs)"""
    if t < B(2): return 1.4
    if t < B(5): return 0.7
    if t < B(6): return lerp(0.7, 1.6, clamp((t - B(5)) / 4))
    return 1.6

def state(t):
    s = {}
    s['dy'], s['rot'] = sep_k(t)
    s['f1'] = fuel1(t); s['f2'] = fuel2(t)
    s['fl1'] = flame1(t); s['fl2'] = flame2(t)
    # latches: 0 closed .. 1 open (only at the real separation; already open in the teaser)
    s['latch'] = 1.0 if t < B(2) else (ease(clamp((t - B(8) - 0.2) / 0.5)) if t >= B(8) else 0.0)
    return s

# ---------------------------------------------------------------- background motion (stage space)
_rnd = random.Random(7)
CLOUDS = [(_rnd.uniform(120, 960), _rnd.uniform(0, 2400), _rnd.uniform(40, 80)) for _ in range(9)]
STREAKS = [(_rnd.uniform(80, 1000), _rnd.uniform(0, 2400), _rnd.uniform(60, 160)) for _ in range(22)]

def scroll(t):
    # integral of speed(t) (piecewise, sampled) -> distance travelled by the scenery, in px
    n = int(t * 10) + 1; d = 0.0
    for i in range(n):
        d += speed(i / 10) * 0.1
    return d * 260

def scenery(ctx, t):
    off = scroll(t)
    for x, y0, r in CLOUDS:
        y = (y0 + off * 0.6) % 2400 - 450
        if abs(x - RX) < HW + r + 30: x = x + (1 if x > RX else -1) * (HW + r + 40)
        for dx, dy, rr in ((0, 0, 1.0), (r * 0.8, 6, 0.75), (-r * 0.8, 8, 0.7)):
            ctx.arc(x + dx, y + dy, r * rr, 0, 2 * math.pi); setc(ctx, WHITE, 0.75); ctx.fill()
    for x, y0, L in STREAKS:
        y = (y0 + off * 1.3) % 2400 - 450
        if abs(x - RX) < HW + 60: continue
        ctx.move_to(x, y); ctx.line_to(x, y + L)
        setc(ctx, INK2, 0.22); ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

# ---------------------------------------------------------------- rocket parts
def tank(ctx, x0, x1, y0, y1, level, liquid, a=1.0, wall_hot=0.0):
    """tank seen in cross-section: rounded domes, liquid filled from the BOTTOM up to `level`"""
    r = min(26, (y1 - y0) / 2)
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, r); setc(ctx, BODY, a); ctx.fill()
    if level > 0:
        ctx.save(); rrect(ctx, x0, y0, x1 - x0, y1 - y0, r); ctx.clip()
        top = y1 - (y1 - y0) * level
        ctx.rectangle(x0, top, x1 - x0, y1 - top); setc(ctx, liquid, a); ctx.fill()
        ctx.move_to(x0, top); ctx.line_to(x1, top); setc(ctx, INK2, 0.6 * a); ctx.set_line_width(2); ctx.stroke()
        ctx.restore()
    rrect(ctx, x0, y0, x1 - x0, y1 - y0, r)
    setc(ctx, lerpc(INK, RED, wall_hot), a); ctx.set_line_width(4 + 3 * wall_hot); ctx.stroke()

def nozzle(ctx, cx, y0, y1, w0, w1, fill=STEEL_D, a=1.0):
    ctx.move_to(cx - w0 / 2, y0); ctx.line_to(cx + w0 / 2, y0)
    ctx.curve_to(cx + w0 / 2, y0 + (y1 - y0) * 0.5, cx + w1 / 2 - 4, y1 - 10, cx + w1 / 2, y1)
    ctx.line_to(cx - w1 / 2, y1)
    ctx.curve_to(cx - w1 / 2 + 4, y1 - 10, cx - w0 / 2, y0 + (y1 - y0) * 0.5, cx - w0 / 2, y0)
    ctx.close_path(); fill_stroke(ctx, fill, lw=3, alpha=a)

def flame(ctx, cx, y, w, L, t, k, seed=0):
    """exhaust pointing DOWN (+y) from a nozzle exit at y"""
    if k <= 0: return
    fl = 1 + 0.08 * math.sin(t * 31 + seed) + 0.05 * math.sin(t * 17 + seed * 2)
    L = L * k * fl
    for col, sw, sl, al in ((RED, 1.0, 1.0, 0.85), (ORANGE, 0.75, 0.78, 0.95), (MUSTARD, 0.5, 0.55, 1.0), (WHITE, 0.25, 0.3, 0.9)):
        ww = w * sw
        ctx.move_to(cx - ww / 2, y)
        ctx.curve_to(cx - ww / 2, y + L * sl * 0.5, cx - ww * 0.12, y + L * sl * 0.85, cx, y + L * sl)
        ctx.curve_to(cx + ww * 0.12, y + L * sl * 0.85, cx + ww / 2, y + L * sl * 0.5, cx + ww / 2, y)
        ctx.close_path(); setc(ctx, col, al * min(1, k * 1.5)); ctx.fill()

def stage1(ctx, t, s, hot=0.0, wall=0.0):
    x0, x1 = RX - HW, RX + HW
    # exhaust first (behind the nozzles)
    for i, dx in enumerate((-40, 0, 40)):
        flame(ctx, RX + dx, 1418, 40, 230, t, s['fl1'], seed=i)
    # landing legs (folded against the body), grid fins
    for sx in (-1, 1):
        ctx.move_to(RX + sx * (HW + 2), 1150); ctx.line_to(RX + sx * (HW + 9), 1356)
        setc(ctx, DARK); ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ctx.rectangle(RX + sx * HW - (18 if sx < 0 else 0), 826, 18, 12); fill_stroke(ctx, STEEL, lw=2)
    # interstage (black ring) + body shell
    ctx.rectangle(x0, Y_S2B, 2 * HW, Y_IS - Y_S2B); fill_stroke(ctx, DARK, lw=4)
    ctx.rectangle(x0, Y_IS, 2 * HW, Y_EB - Y_IS); fill_stroke(ctx, SHELL, lw=5)
    if hot > 0:
        ctx.rectangle(x0, Y_S2B, 2 * HW, Y_EB - Y_S2B); setc(ctx, RED, 0.18 * hot); ctx.fill()
    # tanks (cross-section): LOX upper, RP-1 lower
    tank(ctx, x0 + 7, x1 - 7, *S1_LOX, s['f1'], LOX, wall_hot=wall)
    tank(ctx, x0 + 7, x1 - 7, *S1_RP, s['f1'], RP1, wall_hot=wall)
    # engine bay + 3 of the 9 nozzles (side view)
    ctx.rectangle(x0 + 4, 1294, 2 * HW - 8, Y_EB - 1294); fill_stroke(ctx, DARK, lw=3)
    for dx in (-40, 0, 40):
        nozzle(ctx, RX + dx, Y_EB, 1420, 20, 40)

def stage2(ctx, t, s):
    x0, x1 = RX - HW, RX + HW
    flame(ctx, RX, MV_BOT - 2, 84, 190, t, s['fl2'], seed=5)
    nozzle(ctx, RX, MV_TOP, MV_BOT, 24, 96, fill=STEEL)
    ctx.rectangle(x0, Y_FB, 2 * HW, Y_S2B - Y_FB); fill_stroke(ctx, SHELL, lw=5)
    tank(ctx, x0 + 7, x1 - 7, *S2_LOX, s['f2'], LOX)
    tank(ctx, x0 + 7, x1 - 7, *S2_RP, s['f2'], RP1)
    # fairing (wider than the body), cut away to show the payload
    fw = 74
    ctx.move_to(RX - fw, Y_FB); ctx.line_to(RX - fw, 450)
    ctx.curve_to(RX - fw, 390, RX - 30, Y_TIP + 8, RX, Y_TIP)
    ctx.curve_to(RX + 30, Y_TIP + 8, RX + fw, 390, RX + fw, 450)
    ctx.line_to(RX + fw, Y_FB); ctx.close_path(); fill_stroke(ctx, WHITE, lw=5)
    ctx.move_to(RX, Y_TIP + 4); ctx.line_to(RX, Y_FB); setc(ctx, INK2, 0.5); ctx.set_line_width(2); ctx.stroke()
    satellite(ctx, RX, 470, 1.0)

def satellite(ctx, cx, cy, s, a=1.0):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    rrect(ctx, -26, -30, 52, 56, 6); fill_stroke(ctx, MUSTARD, lw=3, alpha=a)
    for sx in (-1, 1):
        ctx.rectangle(sx * 30 - (12 if sx < 0 else 0), -26, 12, 48); fill_stroke(ctx, TEAL, lw=2, alpha=a)
    ctx.arc(0, -36, 7, math.pi, 2 * math.pi); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

def latches(ctx, k):
    """two hooks on the separation plane; k=0 closed, k=1 swung open (outward)"""
    for sx in (-1, 1):
        ctx.save(); ctx.translate(RX + sx * (HW - 2), Y_S2B); ctx.rotate(sx * 1.2 * k)
        ctx.rectangle(-10, -22, 20, 44); fill_stroke(ctx, MUSTARD, lw=3)
        ctx.restore()

def draw_rocket(ctx, t, s, hot=0.0, wall=0.0):
    dy, rot = s['dy'], s['rot']
    ctx.save()
    ctx.translate(RX, Y_S2B + dy); ctx.rotate(rot); ctx.translate(-RX, -Y_S2B)
    stage1(ctx, t, s, hot, wall)
    ctx.restore()
    stage2(ctx, t, s)
    if dy < 2: latches(ctx, s['latch'])

# ---------------------------------------------------------------- overlays
def bracket(ctx, x, y0, y1, col, a):
    if a <= 0: return
    ctx.move_to(x - 14, y0); ctx.line_to(x, y0); ctx.line_to(x, y1); ctx.line_to(x - 14, y1)
    setc(ctx, col, a); ctx.set_line_width(5); ctx.stroke()

def octaweb(ctx, cx, cy, a, t):
    """bottom view of the 9 engines: 8 in a ring + 1 in the centre"""
    if a <= 0: return
    ctx.arc(cx, cy, 92, 0, 2 * math.pi); fill_stroke(ctx, SHELL, lw=5, alpha=a)
    for i in range(9):
        if i == 8: x, y = cx, cy
        else:
            ang = i * math.pi / 4
            x, y = cx + 60 * math.cos(ang), cy + 60 * math.sin(ang)
        ctx.arc(x, y, 20, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
        ctx.arc(x, y, 9, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()
    text_c(ctx, "SEEN FROM BELOW", cx, cy + 130, 22, INK2, True, 1, a)

def overlays(ctx, t, s):
    dy = s['dy']
    # teaser
    a = win(t, 1.2, B(1) + 0.2, 0.3)
    tag(ctx, "STAGE 1 · DROPPED", RX + 210, 1050 + dy, RED, a, 26)
    a = bw(t, 1)
    if a > 0:
        highlight(ctx, RX, 1060 + dy, 110, 270, RED, a, t)
        tag(ctx, "EMPTY TANK", RX - 230, 1000 + dy, RED, a, 26)
        tag(ctx, "= DEAD WEIGHT", RX - 230, 1070 + dy, RED, a, 26)
    # beat 3: back to liftoff, push vs weight
    a = win(t, B(2) + 0.1, B(2) + 2.4, 0.3)
    tag(ctx, "BACK TO LIFTOFF", RX, 260, INK, a, 26)
    a = win(t, B(2) + 0.8, B(3), 0.3)
    if a > 0:
        straight_arrow(ctx, RX + 220, 1240, RX + 220, 880, RED, a, lw=14, head=26)
        tag(ctx, "PUSH", RX + 220, 1290, RED, a, 26)
        straight_arrow(ctx, RX - 220, 880, RX - 220, 1180, INK, a, lw=14, head=26)
        tag(ctx, "WEIGHT · kg", RX - 220, 830, INK, a, 26)
    a = win(t, B(2) + 2.6, B(3), 0.3)
    tag(ctx, "PUSH = FUEL", RX + 220, 820, RED, a, 26)
    # beat 4: first stage, 9 engines
    a = bw(t, 3)
    bracket(ctx, RX + HW + 46, Y_S2B, 1420, TEAL, a)
    tag(ctx, "1 · FIRST STAGE", RX + 250, 1000, TEAL, a, 26)
    a = win(t, B(3) + 2.8, B(4), 0.3)
    tag(ctx, "9 ENGINES", RX + 200, 1400, RED, a, 26)
    octaweb(ctx, 250, 1270, a, t)
    # beat 5: tank = 94 % fuel, thin shell
    a = bw(t, 4)
    if a > 0:
        tag(ctx, "LIQUID OXYGEN", RX - 240, 930, TEAL, a, 22)
        tag(ctx, "KEROSENE", RX - 220, 1180, DISC, a, 22)
    a = win(t, B(4) + 3.4, B(5), 0.3)
    tag(ctx, "THIN SHELL", RX + 220, 1060, RED, a, 24)
    if a > 0:
        straight_arrow(ctx, RX + 220, 1035, RX + HW + 6, 990, RED, a, lw=5, head=12)
    # beat 7: the empty stage
    a = bw(t, 6)
    if a > 0:
        highlight(ctx, RX, 1080, 120, 360, RED, a, t)
        tag(ctx, "EMPTY", RX - 200, 1050, RED, a, 28)
    # beat 9: latches + falling bottom
    a = win(t, B(8) + 0.1, B(8) + 2.6, 0.3)
    tag(ctx, "LATCHES", RX + 200, Y_S2B - 10, DISC, a, 24)
    if a > 0:
        straight_arrow(ctx, RX + 120, Y_S2B - 10, RX + HW + 14, Y_S2B, DISC, a, lw=5, head=12)
    a = win(t, B(8) + 1.4, B(9), 0.3)
    tag(ctx, "TANK + ENGINES · GONE", RX, 1000 + dy * 0.5, RED, a, 26)
    # beat 10: single engine
    a = win(t, B(9) + 0.7, B(10), 0.3)
    tag(ctx, "1 ENGINE", RX + 190, 830, RED, a, 26)
    # beat 12: recap
    a = bw(t, 11, 12)
    if a > 0:
        straight_arrow(ctx, RX + 200, 640, RX + 200, 420, TEAL, a, lw=12, head=22)
        tag(ctx, "KEEPS GOING", RX + 200, 680, TEAL, a, 24)
        tag(ctx, "LEFT BEHIND", RX - 240, 1180, RED, a, 24)

def draw_set(ctx):
    g = cairo.LinearGradient(0, 0, 0, 1478)
    g.add_color_stop_rgb(0, *SKY1[:3]); g.add_color_stop_rgb(1, *SKY2[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1478); ctx.fill()

def draw(ctx, t, E):
    s = state(t)
    scenery(ctx, t)
    hot = bw(t, 6)
    wall = win(t, B(4) + 3.4, B(5), 0.3)
    draw_rocket(ctx, t, s, hot, wall)
    overlays(ctx, t, s)

# camera: wide for the teaser, then first stage, tank close-up, follow stage 2 after separation, wide recap
CAMKEYS = [(0, 540, 960, 0.9), (B(2) - 0.2, 540, 890, 1.0),
           (B(3) + 0.1, 520, 1060, 1.1), (B(4) + 0.1, 540, 960, 1.15), (B(5) + 0.2, 540, 960, 1.05),
           (B(6) + 0.1, 540, 960, 1.0), (B(8) + 2.4, 540, 640, 1.35),
           (B(11) - 0.1, 540, 900, 1.0)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)
ANCHOR = (540, 1500)

def draw_hud(ctx, t, E):
    a = win(t, B(4) + 0.4, B(5), 0.3)
    if a > 0: hud(ctx, "FULL FIRST STAGE", "94 % FUEL", "6 % metal: tank + engines", a, TEAL, x=630, y=196, w=420)
    a = bw(t, 5)
    if a > 0:
        u = clamp((t - B(5) - 0.4) / (B(6) - B(5) - 0.8)); sec = int(round(150 * u))
        hud(ctx, "BURN TIME", f"{sec // 60}:{sec % 60:02d}", "engines drinking fuel", a, ORANGE, x=630, y=196, w=420)
    a = win(t, B(6) + 0.4, B(7), 0.3)
    if a > 0: hud(ctx, "EMPTY FIRST STAGE", "25 t", "56,000 lb · tank + 9 engines", a, RED, x=630, y=196, w=420)
    a = win(t, B(9) + 2.6, B(10), 0.3)
    if a > 0: hud(ctx, "MASS TO PUSH NOW", "~130 t", "290,000 lb · at liftoff: 549 t", a, TEAL, x=630, y=196, w=420)

SFX = [(0.3, 'pop'), (1.0, 'click'), (B(1) + 0.3, 'pop'), (B(2) + 0.9, 'pop'), (B(3) + 0.3, 'pop'),
       (B(3) + 2.9, 'pop'), (B(4) + 0.5, 'pop'), (B(4) + 3.5, 'pop'), (B(6) + 0.4, 'pop'),
       (B(8) + 0.25, 'click'), (B(9) + 0.6, 'click'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_waste(ctx, t, lt, a):
    card_frame(ctx, "KEEP THE EMPTY STAGE?", a, "PART OF EVERY PUSH IS WASTED", RED)
    # a push (arrow from the left) shoves a train: empty stage (red) + useful load (teal)
    k = ease(clamp(lt / 1.2))
    x = 150 + 30 * math.sin(lt * 3) * 0.3
    straight_arrow(ctx, x, 400, x + 150, 400, ORANGE, a, lw=16, head=26)
    text_c(ctx, "THRUST", x + 70, 360, 24, ORANGE, True, 1, a)
    rrect(ctx, 330, 330, 260, 140, 10); fill_stroke(ctx, lerpc(SHELL, RED, 0.35 * k), lw=4, alpha=a)
    text_c(ctx, "EMPTY METAL", 460, 395, 28, RED, True, 1, a)
    text_c(ctx, "25 t", 460, 440, 30, INK, True, 1, a)
    rrect(ctx, 610, 330, 300, 140, 10); fill_stroke(ctx, TEAL_L, lw=4, alpha=a)
    text_c(ctx, "STAGE 2", 760, 385, 28, INK, True, 1, a)
    text_c(ctx, "+ PAYLOAD", 760, 430, 28, INK, True, 1, a)
    if lt > 1.4:
        b = ease(clamp((lt - 1.4) / 0.5))
        ctx.move_to(340, 340); ctx.line_to(580, 460); ctx.move_to(580, 340); ctx.line_to(340, 460)
        setc(ctx, RED, a * b * 0.8); ctx.set_line_width(7); ctx.stroke()

def card_payload(ctx, t, lt, a):
    card_frame(ctx, "AFTER SEPARATION", a, "EVERY DROP PUSHES THE PAYLOAD", TEAL)
    # fuel drop -> arrow -> satellite ; the empty tank is crossed out below the arrow
    k = ease(clamp(lt / 0.8))
    cx, cy = 230, 400
    ctx.move_to(cx, cy - 70); ctx.curve_to(cx + 50, cy - 10, cx + 50, cy + 50, cx, cy + 50)
    ctx.curve_to(cx - 50, cy + 50, cx - 50, cy - 10, cx, cy - 70); ctx.close_path()
    fill_stroke(ctx, RP1, lw=4, alpha=a)
    text_c(ctx, "FUEL", cx, cy + 100, 24, DISC, True, 1, a)
    straight_arrow(ctx, 320, 400, lerp(330, 660, k), 400, ORANGE, a, lw=14, head=24)
    satellite(ctx, 770, 395, 2.0, a)
    text_c(ctx, "PAYLOAD", 770, 520, 24, TEAL, True, 1, a)
    if lt > 1.0:
        b = ease(clamp((lt - 1.0) / 0.5))
        rrect(ctx, 450, 285, 70, 56, 10); fill_stroke(ctx, SHELL, lw=3, alpha=a * b)
        ctx.move_to(440, 275); ctx.line_to(530, 351); ctx.move_to(530, 275); ctx.line_to(440, 351)
        setc(ctx, RED, a * b); ctx.set_line_width(6); ctx.stroke()
        text_c(ctx, "NOT AN EMPTY TANK", 490, 470, 22, RED, True, 1, a * b)

CARDS = {'waste': card_waste, 'payload': card_payload}
