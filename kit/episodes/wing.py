"""Cogwise episode: How does a plane wing make lift?  (airfoil, angle of attack, pressure, downwash)"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="wing",
    title="How does a wing hold up a 400-ton plane? ✈️",
    description=("A curved, tilted wing throws air down, and the air pushes it up. How lift really works.\n\n"
                 "#Shorts #howthingswork #aviation #airplane #physics #cogwise"),
    hashtags=["Shorts", "howthingswork", "aviation", "airplane", "physics", "science", "cogwise"],
    sources=[
        "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/bernoulli-and-newton",
        "https://www.eng.cam.ac.uk/news/how-wings-really-work",
        "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation",
        "https://migflug.com/afterburner/angle-of-attack-and-the-stall-explained/",
    ],
)

BEATS = [
    dict(dur=5.0, title="HOW DOES A PLANE FLY?", caption="How can a metal plane weighing hundreds of tons just hang in the sky?"),
    dict(dur=5.0, title="THE SECRET: TURN THE AIR", caption="The secret: its wings throw a huge amount of air downward, every second."),
    dict(dur=5.0, title=None, caption="Push air down, and the air pushes the wing up. That's Newton's third law.", card='newton'),
    dict(dur=5.5, title="1 · THE AIRFOIL", caption="Look at a wing from the side: a rounded nose, a curved top, a sharp tail."),
    dict(dur=5.0, title="2 · ANGLE OF ATTACK", caption="It meets the air tilted slightly up. Pilots call this the angle of attack."),
    dict(dur=5.0, title="3 · LOW PRESSURE ON TOP", caption="Air bending over the curved top speeds up, and its pressure drops."),
    dict(dur=4.5, title="4 · HIGH PRESSURE BELOW", caption="Underneath, the air piles up a little, so the pressure rises."),
    dict(dur=5.0, title=None, caption="Low pressure pulling, high pressure pushing: together they lift the wing.", card='pressure'),
    dict(dur=5.0, title="5 · DOWNWASH", caption="Behind the wing, the whole airflow leaves angled down. That's the lift!"),
    dict(dur=5.0, title=None, caption="Surprise: the top air doesn't wait for the bottom air. It arrives first!", card='myth'),
    dict(dur=4.5, title=None, caption="And fly twice as fast, and you get four times the lift.", card='speed'),
    dict(dur=5.5, title="STALL!", caption="Tilt too far, about sixteen degrees, and the air tears off the top. Lift collapses."),
    dict(dur=5.0, title="FLAPS", caption="That's why flaps slide out for takeoff and landing, adding curve at low speed."),
    dict(dur=5.0, title="LIFT = CURVE + TILT + SPEED", caption="So: a curved, tilted wing turns air down, and the air holds it up."),
    dict(dur=5.0, title="PRO TIP", caption="Tip: on your next flight, sit by the wing and watch the flaps before landing."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
LE = (210, 860)          # leading edge
CH = 640                 # chord length
WALL_T, WALL_B = 400, 1330
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); STEEL_L = hexc('#e3e7ea')
WINGC = hexc('#d8dde2'); LOWP = hexc('#3b7fd0'); HIGHP = RED
GREEN = hexc('#4c9d6b'); AIR = hexc('#5f8fb0')

def naca(m=0.045, p=0.4, th=0.13, n=60):
    up, lo = [], []
    for i in range(n + 1):
        b = math.pi * i / n; x = 0.5 * (1 - math.cos(b))
        yt = 5 * th * (0.2969*math.sqrt(x) - 0.126*x - 0.3516*x**2 + 0.2843*x**3 - 0.1036*x**4)
        if x < p: yc = m / p**2 * (2*p*x - x*x); dy = 2*m/p**2 * (p - x)
        else: yc = m / (1-p)**2 * ((1 - 2*p) + 2*p*x - x*x); dy = 2*m/(1-p)**2 * (p - x)
        a = math.atan(dy)
        up.append((x - yt*math.sin(a), yc + yt*math.cos(a)))
        lo.append((x + yt*math.sin(a), yc - yt*math.cos(a)))
    return up, lo
UP, LO = naca()
FLAP_X = 0.74

def aoa(t):
    a = 2.0 + 4.0 * ease((t - B(4) - 0.3) / 1.2)               # 2 -> 6 degrees
    a = lerp(a, 16.0, ease((t - B(11) - 0.3) / 1.6))            # stall
    a = lerp(a, 6.0, ease((t - B(12) - 0.1) / 1.0))             # recover
    return a

def flap(t):
    return ease((t - B(12) - 0.6) / 1.2) * (1 - ease((t - B(13) - 0.2) / 1.0)) + bw(t, 14, 15) * 1.0

def to_screen(x, y, alpha_deg, fl=0.0):
    """wing coords (x 0..1 along chord, y up) -> screen. Flap rotates the aft part down."""
    if fl > 0 and x > FLAP_X:
        hx, hy = FLAP_X, -0.01
        d = math.radians(25 * fl)
        dx, dyy = x - hx, y - hy
        x = hx + dx * math.cos(d) + dyy * math.sin(d)
        y = hy - dx * math.sin(d) + dyy * math.cos(d)
    a = math.radians(alpha_deg)
    px = (x - 0.3) * CH; py = -y * CH
    # positive alpha = nose UP into the oncoming air (screen y grows downward)
    rx = px * math.cos(a) - py * math.sin(a)
    ry = px * math.sin(a) + py * math.cos(a)
    return LE[0] + 0.3 * CH + rx, LE[1] + ry

def wing_path(ctx, ad, fl):
    pts = [to_screen(x, y, ad, fl) for x, y in UP[::-1]] + [to_screen(x, y, ad, fl) for x, y in LO[1:]]
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    ctx.close_path()

# ---- stream lines (stylised, not CFD)
OFFS = [-330, -230, -150, -80, -30, 50, 115, 195, 290, 380]
def stream_y(x, y0, st):
    """screen y of the streamline whose far-upstream height is LE.y + y0."""
    ad = st['aoa']; c0 = LE[0]; c1 = LE[0] + CH
    lift = st['circ']
    k = abs(y0)
    u = (x - c0) / CH
    up = y0 < 0
    # bump over the wing (upper lines squeezed up and over, lower lines nudged down)
    bump = math.exp(-((u - 0.35) / 0.42) ** 2)
    disp = (-55 if up else 18) * bump * math.exp(-k / 220)
    # upwash ahead, downwash behind (scaled by lift)
    s = math.tanh((u - 0.55) * 2.6)
    down = lift * (60 + 10 * ad) * (0.5 + 0.5 * s) * math.exp(-k / 420)
    up_ahead = -lift * 18 * math.exp(-((u + 0.1) / 0.35) ** 2) * math.exp(-k / 300)
    y = LE[1] + y0 + disp + down + up_ahead
    return y

def envelope(ad, fl):
    xs = [60 + 12 * i for i in range(85)]
    pts = [to_screen(x, y, ad, fl) for x, y in UP + LO]
    env = []
    for X in xs:
        ys = [py for (px, py) in pts if abs(px - X) < 14]
        env.append((min(ys), max(ys)) if ys else None)
    return env

def stall_jitter(x, y0, t, st):
    if st['stall'] <= 0 or y0 >= 0 or abs(y0) > 160: return 0
    u = (x - LE[0] - 0.25 * CH) / CH
    if u < 0: return 0
    return st['stall'] * (40 * u + 10) * math.sin(x / 26 + t * 9 + y0) * math.exp(-abs(y0) / 140)

XS = [60 + 12 * i for i in range(85)]
def line_ys(y0, st):
    ys = [stream_y(x, y0, st) for x in XS]
    env = st['_env']; up = y0 < 0; gap = 18 + 0.35 * abs(y0)
    v = [0.0] * len(XS)
    for i, e in enumerate(env):
        if e is None: continue
        top, bot = e
        v[i] = max(0.0, ys[i] - (top - gap)) if up else max(0.0, (bot + gap) - ys[i])
    n = len(XS); sm = [0.0] * n
    for j in range(n):
        if v[j] <= 0: continue
        for i in range(n):
            d = (i - j) * 12
            f = math.exp(-d / 220) if d >= 0 else math.exp(d / 60)
            sm[i] = max(sm[i], v[j] * f)
    return [y - m if up else y + m for y, m in zip(ys, sm)]

def ys_at(ys, x):
    f = (x - 60) / 12; i = int(clamp(f, 0, len(ys) - 2)); r = f - i
    return lerp(ys[i], ys[i + 1], clamp(r))

def draw_streams(ctx, t, st):
    a = st['lines']
    if a <= 0: return
    for y0 in OFFS:
        up = y0 < 0
        col = LOWP if (up and st['pcol'] > 0) else (HIGHP if (not up and st['pcol'] > 0) else AIR)
        col = lerpc(AIR, col, st['pcol'])
        ys = line_ys(y0, st)
        for i, x in enumerate(XS):
            y = ys[i] + stall_jitter(x, y0, t, st)
            if i == 0: ctx.move_to(x, y)
            else: ctx.line_to(x, y)
        setc(ctx, col, a * (0.55 if abs(y0) > 200 else 0.8)); ctx.set_line_width(3.5); ctx.stroke()
        # moving dashes: faster on top, near the wing
        v = 230 * (1.45 if (up and abs(y0) < 200) else (0.9 if not up and abs(y0) < 200 else 1.0))
        for k in range(6):
            xx = 60 + ((t * v + k * 170 + y0 * 3) % 980)
            yy = ys_at(ys, xx) + stall_jitter(xx, y0, t, st)
            ctx.arc(xx, yy, 6, 0, 2*math.pi); setc(ctx, col, a); ctx.fill()

def draw_tunnel(ctx, st):
    for y in (WALL_T, WALL_B):
        rrect(ctx, 30, y - 14, 1020, 28, 6); fill_stroke(ctx, FILL3, lw=4)
        for xx in range(60, 1040, 60):
            ctx.move_to(xx, y - 14); ctx.line_to(xx - 18, y + 14); setc(ctx, INK2, 0.35); ctx.set_line_width(2); ctx.stroke()
    # mounting strut to the floor
    cx, cy = to_screen(0.3, 0.0, st['aoa'])
    rrect(ctx, cx - 12, cy, 24, WALL_B - cy, 4); fill_stroke(ctx, STEEL_D, lw=4)
    rrect(ctx, cx - 70, WALL_B + 14, 140, 150, 10); fill_stroke(ctx, PAPER, lw=5)
    # lift gauge on the balance
    v = st['liftv']
    ctx.arc(cx, WALL_B + 95, 46, math.pi, 2*math.pi); fill_stroke(ctx, WHITE, lw=4)
    ang = math.pi * (1.05 + 0.9 * v)
    ctx.move_to(cx, WALL_B + 95); ctx.line_to(cx + 38*math.cos(ang), WALL_B + 95 + 38*math.sin(ang))
    setc(ctx, RED); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "LIFT", cx, WALL_B + 135, 22, INK, True, 2)
    # fan arrows on the left (incoming wind)
    for y in (560, 860, 1160):
        straight_arrow(ctx, 40, y, 120, y, INK2, 0.5 * st['wind'], lw=5, head=12)

def draw_wing(ctx, t, st):
    ad, fl = st['aoa'], st['flap']
    # pressure glow
    if st['low'] > 0:
        cx, cy = to_screen(0.33, 0.16, ad)
        g = cairo.RadialGradient(cx, cy, 10, cx, cy, 300)
        g.add_color_stop_rgba(0, *LOWP[:3], 0.35 * st['low']); g.add_color_stop_rgba(1, *LOWP[:3], 0)
        ctx.set_source(g); ctx.arc(cx, cy, 300, 0, 2*math.pi); ctx.fill()
    if st['high'] > 0:
        cx, cy = to_screen(0.4, -0.12, ad)
        g = cairo.RadialGradient(cx, cy, 10, cx, cy, 240)
        g.add_color_stop_rgba(0, *HIGHP[:3], 0.30 * st['high']); g.add_color_stop_rgba(1, *HIGHP[:3], 0)
        ctx.set_source(g); ctx.arc(cx, cy, 240, 0, 2*math.pi); ctx.fill()
    wing_path(ctx, ad, fl); fill_stroke(ctx, WINGC, lw=6)
    # spar + ribs hint
    for xs in (0.18, 0.45):
        a0 = to_screen(xs, 0.07, ad); a1 = to_screen(xs, -0.03, ad)
        ctx.move_to(*a0); ctx.line_to(*a1); setc(ctx, STEEL_D); ctx.set_line_width(4); ctx.stroke()
    if fl > 0.02:
        h = to_screen(FLAP_X, 0.0, ad)
        ctx.arc(h[0], h[1], 7, 0, 2*math.pi); setc(ctx, INK); ctx.fill()

def draw_all(ctx, t, st):
    draw_tunnel(ctx, st)
    draw_streams(ctx, t, st)
    draw_wing(ctx, t, st)
    ad = st['aoa']
    # angle-of-attack protractor
    if st['h_aoa'] > 0:
        a = st['h_aoa']
        te = to_screen(1.0, 0.0, ad); le = to_screen(0.0, 0.0, ad)
        # dashed line = direction of the oncoming air, through the leading edge
        ctx.move_to(le[0] - 40, le[1]); ctx.line_to(le[0] + 740, le[1]); ctx.set_dash([12, 9])
        setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
        ctx.move_to(le[0] - 40 * math.cos(math.radians(ad)), le[1] - 40 * math.sin(math.radians(ad)))
        ctx.line_to(te[0] + 60 * math.cos(math.radians(ad)), te[1] + 60 * math.sin(math.radians(ad)))
        setc(ctx, ORANGE, a); ctx.set_line_width(3); ctx.stroke()
        ctx.new_path(); ctx.arc(le[0], le[1], 560, 0, math.radians(ad)); setc(ctx, ORANGE, a); ctx.set_line_width(5); ctx.stroke()
        text_c(ctx, "%d°" % round(ad), 860, le[1] + 60 + 9 * ad, 34, ORANGE, True, 0, a)
    # lift arrow
    if st['lift'] > 0:
        cx, cy = to_screen(0.3, 0.1, ad)
        L = 260 * st['liftv']
        if L > 20: straight_arrow(ctx, cx, cy - 20, cx, cy - 20 - L, GREEN, st['lift'], lw=12, head=24)
        tag(ctx, "LIFT", cx + 110, cy - 60 - L * 0.6, GREEN, st['lift'] * (1 if L > 40 else 0), 28)
    # highlights + tags
    highlight(ctx, 530, 840, 380, 120, TEAL, st['h_foil'], t)
    hx, hy = to_screen(0.4, 0.2, ad)
    highlight(ctx, hx, hy - 30, 300, 110, LOWP, st['h_low'], t)
    lx, ly = to_screen(0.45, -0.12, ad)
    highlight(ctx, lx, ly + 50, 300, 90, HIGHP, st['h_high'], t)
    highlight(ctx, 960, 1020, 100, 200, GREEN, st['h_down'], t)
    tag(ctx, "1 · AIRFOIL", 530, 1040, TEAL, st['l_foil'])
    tag(ctx, "2 · ANGLE OF ATTACK", 330, 1100, ORANGE, st['l_aoa'])
    tag(ctx, "3 · LOW PRESSURE · FAST AIR", 540, 470, LOWP, st['l_low'], 26)
    tag(ctx, "4 · HIGH PRESSURE", 430, 1250, HIGHP, st['l_high'])
    tag(ctx, "5 · DOWNWASH", 860, 1250, GREEN, st['l_down'])
    if st['down'] > 0:
        for k, y in enumerate((980, 1080)):
            straight_arrow(ctx, 900, y - 40, 990, y + 30, GREEN, st['down'], lw=7, head=16)
    if st['stalltag'] > 0:
        tag(ctx, "AIR TEARS OFF · LIFT COLLAPSES", 540, 470, RED, st['stalltag'], 26)
    if st['flaptag'] > 0:
        fx, fy = to_screen(0.88, -0.06, ad, st['flap'])
        tag(ctx, "FLAP OUT = MORE CURVE", 640, 1250, TEAL, st['flaptag'], 26)
        highlight(ctx, fx, fy, 90, 70, TEAL, st['flaptag'], t)
    if st['recap'] > 0:
        tag(ctx, "CURVE + TILT + SPEED", 540, 470, INK, st['recap'], 30)
    if st['tip'] > 0:
        tag(ctx, "WATCH THE FLAPS ON LANDING", 540, 470, GREEN, st['tip'], 28)

# ---------------------------------------------------------------- state machine
def state(t):
    st = {}
    st['aoa'] = aoa(t)
    st['flap'] = flap(t)
    st['_env'] = envelope(st['aoa'], st['flap'])
    st['wind'] = 1.0
    st['lines'] = ease((t - 0.3) / 1.0)
    stall = ease((t - B(11) - 1.2) / 1.0) * (1 - ease((t - B(12) - 0.3) / 1.0))
    st['stall'] = stall
    st['circ'] = (0.35 + 0.65 * ease((t - B(1) - 0.3) / 1.5)) * (1 - 0.7 * stall)
    st['pcol'] = ease((t - B(5) - 0.3) / 1.0) * (1 - ease((t - B(9) - 0.2) / 1.0)) + bw(t, 13, 14)
    st['low'] = ease((t - B(5) - 0.3) / 1.0) * (1 - stall)
    st['high'] = ease((t - B(6) - 0.3) / 1.0)
    st['lift'] = ease((t - B(1) - 0.5) / 1.0)
    lv = (0.45 + 0.55 * ease((t - B(4) - 0.3) / 1.2))
    lv = lv * (1 - 0.75 * stall) * (1 + 0.25 * st['flap'])
    st['liftv'] = clamp(lv, 0, 1.15)
    st['h_foil'] = bw(t, 3)
    st['h_aoa'] = bw(t, 4) + bw(t, 11, 12)
    st['h_low'] = bw(t, 5)
    st['h_high'] = bw(t, 6)
    st['h_down'] = bw(t, 8)
    st['l_foil'] = bw(t, 3)
    st['l_aoa'] = bw(t, 4)
    st['l_low'] = bw(t, 5)
    st['l_high'] = bw(t, 6) + bw(t, 13, 14)
    st['l_down'] = bw(t, 8) + bw(t, 13, 14)
    st['down'] = bw(t, 8) + bw(t, 1, 2)
    st['stalltag'] = win(t, B(11) + 1.3, B(12))
    st['flaptag'] = win(t, B(12) + 1.0, B(13))
    st['recap'] = bw(t, 13, 14)
    st['tip'] = bw(t, 14, 15)
    return st

SFX = [(B(1) + 0.4, 'whoosh'), (B(3) + 0.2, 'pop'), (B(4) + 0.2, 'pop'), (B(4) + 0.5, 'click'),
       (B(5) + 0.2, 'pop'), (B(6) + 0.2, 'pop'), (B(8) + 0.2, 'pop'), (B(8) + 0.4, 'whoosh'),
       (B(11) + 1.3, 'click'), (B(12) + 0.6, 'click'), (B(13) + 0.2, 'ding'), (B(14) + 0.2, 'pop')]
HUM = [(0.0, B(15))]

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

# ---------------------------------------------------------------- cards
def mini_wing(ctx, x0, y0, ch, ad, a, fill=WINGC):
    ar = math.radians(ad)
    pts = []
    for (x, y) in UP[::-1] + LO[1:]:
        px, py = (x - 0.3) * ch, -y * ch
        pts.append((x0 + px * math.cos(ar) - py * math.sin(ar), y0 + px * math.sin(ar) + py * math.cos(ar)))
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    ctx.close_path(); fill_stroke(ctx, fill, lw=4, alpha=a)

def card_newton(ctx, t, lt, a):
    card_frame(ctx, "NEWTON'S THIRD LAW", a, "AIR DOWN = WING UP", GREEN)
    p = ease((lt - 0.4) / 1.0)
    mini_wing(ctx, 470, 360, 360, 6, a)
    # air parcels pushed down behind the wing
    for k in range(4):
        u = ((lt * 0.6 + k * 0.25) % 1.0)
        x = 640 + 260 * u; y = 360 + 150 * u * p
        ctx.arc(x, y, 14, 0, 2*math.pi); setc(ctx, AIR, a * (1 - u * 0.6)); ctx.fill()
    straight_arrow(ctx, 720, 380, 820, 500, AIR, a * p, lw=8, head=16)
    text_c(ctx, "AIR DOWN", 860, 530 - 10, 24, AIR, True, 1, a * p)
    straight_arrow(ctx, 470, 350, 470, 350 - 110 * p, GREEN, a * p, lw=10, head=20)
    text_c(ctx, "WING UP", 330, 280, 26, GREEN, True, 1, a * p)

def card_pressure(ctx, t, lt, a):
    card_frame(ctx, "PRESSURE DIFFERENCE", a, "PULL ON TOP + PUSH BELOW", LOWP)
    p = ease((lt - 0.4) / 1.0)
    mini_wing(ctx, 470, 400, 460, 5, a)
    for k, x in enumerate((340, 450, 560, 670)):
        straight_arrow(ctx, x, 360 - 8 * (k == 1), x, 360 - 90 * p, LOWP, a * p, lw=6, head=12)
        straight_arrow(ctx, x, 520, x, 520 - 60 * p, HIGHP, a * p, lw=6, head=12)
    text_c(ctx, "LOW", 200, 330, 30, LOWP, True, 2, a * p)
    text_c(ctx, "HIGH", 200, 500, 30, HIGHP, True, 2, a * p)

def card_myth(ctx, t, lt, a):
    card_frame(ctx, "THE EQUAL-TIME MYTH", a, "TOP AIR ARRIVES FIRST", RED)
    mini_wing(ctx, 480, 400, 520, 4, a)
    u = clamp(lt / 3.0)
    # two puffs released together at the nose
    xt = lerp(200, 900, ease(u * 1.5)); yt = 330 - 30 * math.sin(math.pi * clamp((xt - 300) / 520))
    xb = lerp(200, 840, ease(u)); yb = 470 + 6 * math.sin(math.pi * clamp((xb - 300) / 520))
    for (x, y, c) in ((xt, yt, LOWP), (xb, yb, HIGHP)):
        ctx.arc(x, y, 16, 0, 2*math.pi); fill_stroke(ctx, c, lw=3, alpha=a)
    ctx.move_to(800, 280); ctx.line_to(800, 520); ctx.set_dash([8, 8]); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    if xt > 800: text_c(ctx, "FIRST!", 900, 300, 26, LOWP, True, 1, a)

def card_speed(ctx, t, lt, a):
    card_frame(ctx, "SPEED SQUARED", a, "2× SPEED = 4× LIFT", GREEN)
    p = ease((lt - 0.6) / 1.0)
    for i, (x, sp, L) in enumerate(((330, "1×", 1), (720, "2×", 4))):
        mini_wing(ctx, x, 470, 220, 5, a)
        text_c(ctx, "SPEED " + sp, x - 130, 540 - 30, 22, INK, True, 1, a)
        for k in range(L if i == 1 else 1):
            ax = x - 30 + (k - (L - 1) / 2) * 34 if i == 1 else x - 30
            straight_arrow(ctx, ax, 440, ax, 440 - 140 * (p if i == 1 else 1), GREEN, a, lw=8, head=14)
    for k in range(3):
        straight_arrow(ctx, 130, 330 + k * 50, 190, 330 + k * 50, AIR, a * 0.7, lw=4, head=10)

CARDS = {'newton': card_newton, 'pressure': card_pressure, 'myth': card_myth, 'speed': card_speed}
