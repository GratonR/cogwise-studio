"""Cogwise episode: How does a tiny pedal stop a whole car?  (hydraulic disc brake)"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="brake",
    title="How does one small pedal stop a whole car? 🛑",
    description=("A fluid you can't squeeze and a disc you can pinch: the disc brakes on your car, explained.\n\n"
                 "#Shorts #howthingswork #brakes #cars #engineering #cogwise"),
    hashtags=["Shorts", "howthingswork", "brakes", "cars", "engineering", "science", "cogwise"],
    sources=[
        "https://us.haynes.com/blogs/tips-tutorials/how-do-car-brakes-work",
        "https://asv.kwik-fit.com/blog/should-brake-discs-get-hot",
        "https://blog.amsoil.com/does-brake-fluid-go-bad",
        "https://www.24h-lemans.com/en/news/jaguar-brakes-with-the-drum-tradition-to-usher-in-the-disc-era-57092",
        "https://classicsworld.co.uk/news/the-history-of-the-disc-brake/",
    ],
)

BEATS = [
    dict(dur=5.0, title="HOW DOES A PEDAL STOP A CAR?", caption="How can one light push of your foot stop a car that weighs over a ton?"),
    dict(dur=5.0, title="THE SECRET: A LIQUID", caption="The secret: a liquid you can't squeeze carries your push to the wheels."),
    dict(dur=5.5, title=None, caption="Push on a fluid in a closed pipe: the pressure is equal everywhere.", card='pascal'),
    dict(dur=5.0, title="1 · PEDAL + BOOSTER", caption="The pedal is a lever, and a booster adds even more force."),
    dict(dur=5.5, title="2 · MASTER CYLINDER", caption="It pushes a small piston in the master cylinder, pressurizing the fluid."),
    dict(dur=5.0, title="3 · BRAKE LINES", caption="Brake lines carry that pressure to each wheel."),
    dict(dur=5.5, title=None, caption="The caliper's piston is much wider, so the force gets multiplied.", card='multiply'),
    dict(dur=5.0, title="4 · THE CALIPER", caption="The caliper squeezes two pads onto the spinning disc, like pinching fingers."),
    dict(dur=5.0, title="5 · THE DISC", caption="The disc is bolted to the wheel, so gripping it slows the whole car."),
    dict(dur=5.5, title=None, caption="Friction turns motion into heat, about 130 degrees Celsius in normal braking.", card='heat'),
    dict(dur=5.0, title="VENTED DISCS", caption="Many discs have inner fins, like a fan, to shed that heat."),
    dict(dur=5.5, title=None, caption="Surprise: disc brakes helped Jaguar win Le Mans in 1953!", card='lemans'),
    dict(dur=5.0, title="LIFT YOUR FOOT", caption="Lift your foot, the pressure drops, and the pads let go."),
    dict(dur=5.0, title="BRAKES = FLUID + FRICTION", caption="So: fluid multiplies your push, friction turns speed into heat."),
    dict(dur=5.5, title="PRO TIP", caption="Tech tip: brake fluid soaks up water, so change it about every two years."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
DC = (560, 760); DR = 250; HUB = 105
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); STEEL_L = hexc('#e3e7ea')
CAL = RED; PAD = hexc('#8a6a3a'); FLUID = MUSTARD; FLUID_P = hexc('#e4472f')
GREEN = hexc('#4c9d6b'); HOT = hexc('#f2902b')
PIVOT = (250, 1060)
LINE = [(620, 1215), (930, 1215), (930, 905), (870, 870)]

def press(t):
    return ease((t - B(3) - 0.5) / 1.0) * (1 - ease((t - B(12) - 0.5) / 1.0))

def speed(t):
    s = 1.0 - 0.95 * ease((t - B(8) - 0.2) / 2.2)
    s = lerp(s, 1.0, ease((t - B(12) - 0.8) / 2.0))
    return s

def angle(t):
    a = 0.0; dt = 0.05; x = 0.0
    while x < t:
        a += speed(x) * dt * 2.4; x += dt
    return a

def path_point(pts, u):
    segs = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]
    L = sum(segs) * (u % 1.0)
    for i, s in enumerate(segs):
        if L <= s:
            f = L / s
            return lerp(pts[i][0], pts[i+1][0], f), lerp(pts[i][1], pts[i+1][1], f)
        L -= s
    return pts[-1]

def draw_disc(ctx, t, st):
    cx, cy = DC
    heat = st['heat']
    body = lerpc(STEEL, HOT, heat * 0.55)
    ctx.arc(cx, cy, DR, 0, 2*math.pi); fill_stroke(ctx, body, lw=6)
    # friction ring
    ctx.arc(cx, cy, DR - 12, 0, 2*math.pi); setc(ctx, STEEL_D, 0.5); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(cx, cy, HUB + 40, 0, 2*math.pi); setc(ctx, STEEL_D, 0.5); ctx.set_line_width(3); ctx.stroke()
    ang = st['ang']
    # drilled holes (show rotation)
    for k in range(12):
        a = ang + k * 2*math.pi/12
        for rr in (175, 210):
            aa = a + (0.13 if rr == 210 else 0)
            ctx.arc(cx + rr*math.cos(aa), cy + rr*math.sin(aa), 8, 0, 2*math.pi)
            setc(ctx, INK2, 0.75); ctx.fill()
    # hub (hat) + bolts
    ctx.arc(cx, cy, HUB, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=5)
    for k in range(5):
        a = ang + k * 2*math.pi/5
        ctx.arc(cx + 62*math.cos(a), cy + 62*math.sin(a), 13, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=3)
    ctx.arc(cx, cy, 30, 0, 2*math.pi); fill_stroke(ctx, WALL2, lw=4)
    # speed marks
    sp = st['spd']
    if sp > 0.2:
        for k in range(3):
            a0 = ang * 1.0 + k * 2*math.pi/3
            ctx.arc(cx, cy, DR + 28, a0, a0 + 0.55 * sp)
            setc(ctx, INK2, 0.55 * sp * st['marks']); ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

def draw_caliper(ctx, t, st):
    cx, cy = DC
    p = st['clamp']
    # pad (annulus sector) visible through cut-away window
    a0, a1 = -0.42, 0.42
    ctx.new_path()
    ctx.arc(cx, cy, DR - 4, a0, a1); ctx.arc_negative(cx, cy, DR - 82, a1, a0); ctx.close_path()
    padc = lerpc(PAD, HOT, st['heat'] * 0.6)
    fill_stroke(ctx, padc, lw=4, alpha=0.35 + 0.65 * p)
    # caliper body (C-shape over the rim)
    rrect(ctx, 760, 640, 150, 240, 26); fill_stroke(ctx, CAL, lw=6)
    rrect(ctx, 790, 672, 60, 176, 14); setc(ctx, hexc('#b8321f')); ctx.fill()
    text_c(ctx, "", 835, 770, 20, WHITE)
    # bleed screw + inlet
    rrect(ctx, 880, 650, 20, 34, 5); fill_stroke(ctx, STEEL, lw=3)

def draw_pedal(ctx, t, st):
    px, py = PIVOT
    a = -0.30 * st['press']           # rotate toward the booster
    ctx.save(); ctx.translate(px, py); ctx.rotate(a)
    # arm
    ctx.move_to(-10, 0); ctx.line_to(-48, 330); ctx.line_to(-24, 332); ctx.line_to(12, 0); ctx.close_path()
    fill_stroke(ctx, STEEL_D, lw=5)
    rrect(ctx, -100, 320, 120, 36, 10); fill_stroke(ctx, INK2, lw=4)  # foot pad
    for i in range(4):
        ctx.move_to(-90 + i*28, 330); ctx.line_to(-90 + i*28, 348); setc(ctx, WALL1, 0.6); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
    ctx.arc(px, py, 14, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=4)
    # push rod from arm point (y +150 along arm) to booster
    ax = px + (-17) * math.cos(a) - 150 * math.sin(a)
    ay = py + (-17) * math.sin(a) + 150 * math.cos(a)
    bx = 312 + 0 * st['press']
    ctx.move_to(ax, ay); ctx.line_to(bx, 1215); setc(ctx, INK); ctx.set_line_width(7); ctx.stroke()

def draw_master(ctx, t, st):
    p = st['press']
    # booster can
    ctx.arc(380, 1215, 72, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=5)
    ctx.arc(380, 1215, 50, 0, 2*math.pi); setc(ctx, STEEL_D, 0.6); ctx.set_line_width(3); ctx.stroke()
    # reservoir
    rrect(ctx, 480, 1110, 110, 70, 10); fill_stroke(ctx, hexc('#fff6dc'), lw=4)
    lvl = 1132
    rrect(ctx, 484, lvl, 102, 1176 - lvl, 6); setc(ctx, FLUID, 0.8); ctx.fill()
    rrect(ctx, 515, 1094, 40, 18, 4); fill_stroke(ctx, INK2, lw=3)
    # cylinder
    rrect(ctx, 450, 1185, 180, 60, 10); fill_stroke(ctx, STEEL, lw=5)
    pcol = lerpc(FLUID, FLUID_P, st['pres'])
    pxp = 470 + 55 * p
    rrect(ctx, pxp + 26, 1195, 600 - pxp - 6, 40, 6); setc(ctx, pcol, 0.9); ctx.fill()
    rrect(ctx, pxp, 1192, 26, 46, 5); fill_stroke(ctx, STEEL_D, lw=3)
    ctx.move_to(452, 1215); ctx.line_to(pxp, 1215); setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()

def draw_line(ctx, t, st):
    pts = LINE
    fillu = st['fill']
    # outer pipe
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    setc(ctx, INK); ctx.set_line_width(18); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    setc(ctx, WALL1); ctx.set_line_width(10); ctx.stroke()
    if fillu > 0:
        pcol = lerpc(FLUID, FLUID_P, st['pres'])
        segs = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]
        total = sum(segs); L = total * fillu
        ctx.move_to(*pts[0]); acc = 0
        for i, s in enumerate(segs):
            if acc + s <= L: ctx.line_to(*pts[i+1]); acc += s
            else:
                f = (L - acc) / s
                ctx.line_to(lerp(pts[i][0], pts[i+1][0], f), lerp(pts[i][1], pts[i+1][1], f)); break
        setc(ctx, pcol, 0.95); ctx.set_line_width(10); ctx.stroke()
    if st['flow'] > 0:
        for k in range(9):
            x, y = path_point(pts, k / 9 + t * 0.35)
            ctx.arc(x, y, 6, 0, 2*math.pi); setc(ctx, WHITE, st['flow']); ctx.fill()

def draw_all(ctx, t, st):
    draw_line(ctx, t, st)
    draw_disc(ctx, t, st)
    draw_caliper(ctx, t, st)
    draw_master(ctx, t, st)
    draw_pedal(ctx, t, st)
    # press arrow on the foot pad
    if st['foot'] > 0:
        straight_arrow(ctx, 70, 1360, 150, 1380, RED, st['foot'])
    # highlights
    highlight(ctx, 250, 1260, 150, 210, ORANGE, st['h_ped'], t)
    highlight(ctx, 540, 1180, 120, 95, TEAL, st['h_mc'], t)
    highlight(ctx, 930, 1060, 70, 200, RED, st['h_line'], t)
    highlight(ctx, 835, 760, 130, 160, RED, st['h_cal'], t)
    highlight(ctx, 560, 760, 280, 280, COLD, st['h_disc'], t)
    highlight(ctx, 535, 1140, 90, 70, COLD, st['h_res'], t)
    # tags
    tag(ctx, "1 · PEDAL + BOOSTER", 300, 1445, ORANGE, st['l_ped'])
    tag(ctx, "2 · MASTER CYLINDER", 560, 1060, TEAL, st['l_mc'])
    tag(ctx, "3 · BRAKE LINES", 860, 1300, RED, st['l_line'])
    tag(ctx, "4 · CALIPER", 860, 590, RED, st['l_cal'])
    tag(ctx, "5 · THE DISC", 400, 460, COLD, st['l_disc'])
    if st['grip'] > 0: tag(ctx, "SQUEEZE!", 860, 960, RED, st['grip'], 28)
    if st['vent'] > 0:
        v = st['vent']
        cx, cy = DC
        for k, a in enumerate((-2.3, -1.6, -0.9)):
            x0, y0 = cx + (DR + 10) * math.cos(a), cy + (DR + 10) * math.sin(a)
            x1, y1 = cx + (DR + 120) * math.cos(a), cy + (DR + 120) * math.sin(a)
            wavy_arrow(ctx, x0, y0, x1, y1, t + k, HOT, v, amp=8, lw=5)
        tag(ctx, "HEAT OUT", 250, 1000, HOT, v, 26)
    if st['rel'] > 0: tag(ctx, "PRESSURE OFF · PADS RELEASED", 560, 460, GREEN, st['rel'], 26)
    if st['recap'] > 0: tag(ctx, "FLUID + FRICTION", 560, 460, INK, st['recap'], 30)
    if st['tip'] > 0:
        a = st['tip']
        rnd = random.Random(3)
        for i in range(6):
            x = 470 + rnd.random() * 130; y = 1000 + ((t * 40 + rnd.random() * 90) % 90)
            ctx.move_to(x, y - 12); ctx.curve_to(x + 9, y, x + 9, y + 10, x, y + 10)
            ctx.curve_to(x - 9, y + 10, x - 9, y, x, y - 12)
            setc(ctx, COLD, a); ctx.fill()
        tag(ctx, "WATER IN = BOILS SOONER", 560, 460, COLD, a, 26)
        tag(ctx, "CHANGE IT ~ EVERY 2 YEARS", 760, 1380, GREEN, a, 24)

# ---------------------------------------------------------------- state machine
def state(t):
    st = {}
    st['press'] = press(t)
    st['foot'] = win(t, B(3) + 0.2, B(4)) * 1.0
    st['fill'] = ease((t - B(1) - 0.3) / 2.0)
    st['pres'] = st['press']
    st['flow'] = bw(t, 1, 2) * 0.9 + win(t, B(5) + 0.1, B(6)) * 0.9
    st['clamp'] = max(st['press'], bw(t, 7, 8) * 0.0)
    st['spd'] = speed(t)
    st['ang'] = angle(t)
    st['marks'] = 1.0
    st['heat'] = ease((t - B(8) - 0.8) / 2.0) * (1 - ease((t - B(12) - 1.0) / 4.0))
    st['h_ped'] = bw(t, 3)
    st['h_mc'] = bw(t, 4)
    st['h_line'] = bw(t, 5)
    st['h_cal'] = bw(t, 7)
    st['h_disc'] = bw(t, 8)
    st['h_res'] = bw(t, 14, 15)
    st['l_ped'] = bw(t, 3) + bw(t, 13, 14)
    st['l_mc'] = bw(t, 4) + bw(t, 13, 14)
    st['l_line'] = bw(t, 5) + bw(t, 13, 14)
    st['l_cal'] = bw(t, 7) + bw(t, 13, 14)
    st['l_disc'] = bw(t, 8) + bw(t, 13, 14) * 0
    st['grip'] = win(t, B(7) + 0.8, B(8))
    st['vent'] = bw(t, 10)
    st['rel'] = win(t, B(12) + 1.0, B(13))
    st['recap'] = bw(t, 13, 14)
    st['tip'] = bw(t, 14, 15)
    return st

SFX = [(B(1) + 0.4, 'whoosh'), (B(3) + 0.2, 'pop'), (B(3) + 0.6, 'click'), (B(4) + 0.2, 'pop'),
       (B(5) + 0.2, 'pop'), (B(7) + 0.2, 'pop'), (B(8) + 0.2, 'pop'), (B(8) + 0.5, 'sizzle'),
       (B(10) + 0.3, 'sizzle'), (B(12) + 0.5, 'click'), (B(13) + 0.2, 'ding'), (B(14) + 0.2, 'pop')]
HUM = [(0.0, B(8) + 1.5), (B(12) + 1.0, B(15))]

def draw_set(ctx):
    window(ctx, 50, 260, 200, 300)

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

# ---------------------------------------------------------------- cards
def gauge(ctx, x, y, v, a):
    ctx.arc(x, y, 34, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    ang = math.pi * (0.8 + 1.4 * v)
    ctx.move_to(x, y); ctx.line_to(x + 26*math.cos(ang), y + 26*math.sin(ang))
    setc(ctx, RED, a); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(x, y, 5, 0, 2*math.pi); setc(ctx, INK, a); ctx.fill()

def card_pascal(ctx, t, lt, a):
    card_frame(ctx, "PASCAL'S PRINCIPLE", a, "SAME PRESSURE EVERYWHERE", TEAL)
    p = ease((lt - 0.8) / 0.8)
    # closed pipe
    rrect(ctx, 150, 400, 780, 90, 20); fill_stroke(ctx, lerpc(FLUID, FLUID_P, p * 0.6), lw=5, alpha=a)
    # piston column on the left
    rrect(ctx, 170, 260, 80, 160, 8); fill_stroke(ctx, lerpc(FLUID, FLUID_P, p * 0.6), lw=5, alpha=a)
    py = 270 + 40 * p
    rrect(ctx, 165, py - 18, 90, 22, 5); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    straight_arrow(ctx, 210, py - 80, 210, py - 22, RED, a * (0.3 + 0.7 * p))
    for x in (420, 610, 800):
        gauge(ctx, x, 330, 0.75 * p, a)
        ctx.move_to(x, 364); ctx.line_to(x, 400); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
        for d in (-1, 1):
            straight_arrow(ctx, x + d*20, 445, x + d*70, 445, RED, a * p, lw=4, head=10)

def card_multiply(ctx, t, lt, a):
    card_frame(ctx, "FORCE MULTIPLIER", a, "WIDE PISTON = MORE FORCE", RED)
    p = ease((lt - 0.8) / 0.8)
    fc = lerpc(FLUID, FLUID_P, p * 0.6)
    # small master cylinder (left)
    rrect(ctx, 160, 360, 200, 50, 8); fill_stroke(ctx, fc, lw=4, alpha=a)
    sx = 175 + 50 * p
    rrect(ctx, sx, 352, 22, 66, 4); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    straight_arrow(ctx, sx - 70, 385, sx - 4, 385, RED, a, lw=5, head=10)
    text_c(ctx, "SMALL PUSH", 230, 460, 24, INK, True, 1, a)
    # pipe
    rrect(ctx, 355, 375, 230, 20, 4); fill_stroke(ctx, fc, lw=3, alpha=a)
    # wide caliper cylinder (right)
    rrect(ctx, 580, 270, 150, 230, 12); fill_stroke(ctx, fc, lw=4, alpha=a)
    wx = 690 + 22 * p
    rrect(ctx, wx, 275, 34, 220, 6); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    # pad + disc edge
    rrect(ctx, wx + 34, 300, 26, 170, 4); fill_stroke(ctx, PAD, lw=3, alpha=a)
    rrect(ctx, 790, 255, 40, 270, 6); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    for k in range(3):
        straight_arrow(ctx, 740, 320 + k*65, 770, 320 + k*65, RED, a * p, lw=7, head=12)
    text_c(ctx, "BIG SQUEEZE", 910, 300, 19, RED, True, 1, a * p)

def card_heat(ctx, t, lt, a):
    card_frame(ctx, "MOTION BECOMES HEAT", a, "≈ 130 °C IN NORMAL DRIVING", HOT)
    h = ease((lt - 0.4) / 2.2)
    cx, cy = 400, 395
    ctx.arc(cx, cy, 130, 0, 2*math.pi); fill_stroke(ctx, lerpc(STEEL, HOT, h * 0.8), lw=5, alpha=a)
    ctx.arc(cx, cy, 50, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=4, alpha=a)
    rrect(ctx, 505, 320, 70, 150, 16); fill_stroke(ctx, CAL, lw=4, alpha=a)
    for k, ang in enumerate((-2.2, -1.57, -0.95)):
        wavy_arrow(ctx, cx + 140*math.cos(ang), cy + 140*math.sin(ang) + 10,
                   cx + 140*math.cos(ang), cy + 140*math.sin(ang) - 60, lt + k, HOT, a * h, amp=6, lw=4, head=10)
    thermometer(ctx, 760, 500, 0.15 + 0.6 * h, a, HOT, 220)
    text_c(ctx, "%d °C" % int(20 + 110 * h), 870, 420, 40, HOT, True, 0, a)

def card_lemans(ctx, t, lt, a):
    card_frame(ctx, "LE MANS, 1953", a, "DISC BRAKES BEAT THE DRUMS", GREEN)
    x = lerp(120, 260, ease(lt / 2.5))
    # generic 1950s race car silhouette
    ctx.move_to(x, 470); ctx.curve_to(x + 30, 400, x + 120, 390, x + 200, 395)
    ctx.curve_to(x + 260, 360, x + 330, 360, x + 380, 400)
    ctx.curve_to(x + 450, 405, x + 500, 420, x + 520, 470); ctx.close_path()
    fill_stroke(ctx, hexc('#3f7a5a'), lw=5, alpha=a)
    for wx in (x + 100, x + 420):
        ctx.arc(wx, 470, 42, 0, 2*math.pi); fill_stroke(ctx, INK2, lw=4, alpha=a)
        ctx.arc(wx, 470, 22, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=3, alpha=a)
    ctx.arc(x + 300, 420, 28, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    text_c(ctx, "1", x + 300, 432, 32, INK, True, 0, a)
    # checkered flag
    fx, fy = 850, 260
    ctx.move_to(fx, fy); ctx.line_to(fx, fy + 230); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    wave = 4 * math.sin(lt * 6)
    for i in range(4):
        for j in range(3):
            if (i + j) % 2 == 0:
                ctx.rectangle(fx + 4 + i*22, fy + j*22 + wave * (i/4), 22, 22); setc(ctx, INK, a); ctx.fill()
    ctx.rectangle(fx + 4, fy + wave * 0, 88, 66); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()

CARDS = {'pascal': card_pascal, 'multiply': card_multiply, 'heat': card_heat, 'lemans': card_lemans}
