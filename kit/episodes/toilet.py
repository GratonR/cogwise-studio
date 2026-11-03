"""Cogwise episode: How does a toilet flush?  (gravity tank toilet + siphon trapway)"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="toilet",
    title="How does a toilet flush with no pump? 🚽",
    description=("No motor, no pump: a curved tube turns into a siphon and a float resets everything.\n\n"
                 "#Shorts #howthingswork #toilet #plumbing #cogwise"),
    hashtags=["Shorts", "howthingswork", "toilet", "plumbing", "engineering", "cogwise"],
    sources=[
        "https://assist.kohler.com/en/toilets-and-seats/How-a-Toilet-Flushes",
        "https://home.howstuffworks.com/toilet.htm",
        "https://www.familyhandyman.com/list/how-a-toilet-works/",
        "https://www.howitworksdaily.com/how-does-a-toilet-work/",
    ],
)

BEATS = [
    dict(dur=5.5, title="HOW DOES A TOILET FLUSH?", caption="Press the handle and the bowl empties in seconds. No pump. How?"),
    dict(dur=4.5, title="THE SECRET: A SIPHON", caption="The secret: a hidden, curved tube that becomes a siphon."),
    dict(dur=5.5, title=None, caption="A siphon: once a bent tube is full, falling water pulls the rest along.", card='siphon'),
    dict(dur=5.0, title="1 · THE TANK", caption="It starts in the tank: about a gallon of water, waiting up high."),
    dict(dur=5.0, title="2 · THE FLAPPER", caption="The handle's chain lifts a rubber flapper off the drain."),
    dict(dur=5.0, title="3 · THE BOWL", caption="Water rushes into the bowl through little holes under the rim."),
    dict(dur=5.0, title="4 · THE TRAPWAY", caption="The water rises over the hump of the curved trapway."),
    dict(dur=5.0, title="WHOOSH!", caption="The tube fills, the siphon kicks in, and the bowl is sucked empty."),
    dict(dur=5.0, title="GURGLE!", caption="That final gurgle? Air rushing in, breaking the siphon."),
    dict(dur=5.0, title="5 · THE FLOAT", caption="Then the flapper drops shut, and a float sinks with the water."),
    dict(dur=5.0, title="6 · THE FILL VALVE", caption="The sunken float opens the fill valve, and fresh water refills the tank."),
    dict(dur=5.5, title=None, caption="A small tube refills the bowl, leaving a water plug against sewer smells.", card='seal'),
    dict(dur=5.5, title=None, caption="Surprise: a bucket of water dumped in fast flushes it, no tank needed!", card='bucket'),
    dict(dur=5.0, title="FLUSH = GRAVITY + SIPHON", caption="So: gravity, a curved tube, and a float that resets it all."),
    dict(dur=6.0, title="REPAIR TECH TIP", caption="Tech tip: running toilet? Dye in the tank. Color in the bowl? Replace the flapper."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

ANCHOR = (560, 1480)

# ---------------------------------------------------------------- geometry
TANK = (500, 430, 360, 430)          # x, y, w, h -> 500..860, 430..860
TB = 860                             # tank bottom
T_FULL, T_EMPTY = 640, 846
HOLE = (580, 660)                    # flush hole x range
FV_X = 800                           # fill valve shaft x
OVF_X = 685                          # overflow tube centre x
RIM_Y0, RIM_Y1 = 960, 995
B_REST, B_HIGH, B_LOW = 1150, 1098, 1258
TUBE_W = 56
PORC = hexc('#fffaf0'); CAV = hexc('#e9dfca'); WATER = hexc('#8fcfc8'); WATER_D = hexc('#1f8a8a')
DYE = hexc('#e4472f')

def bez(p0, p1, p2, p3, n=40):
    pts = []
    for i in range(n + 1):
        u = i / n; a = (1-u)**3; b = 3*(1-u)**2*u; c = 3*(1-u)*u**2; d = u**3
        pts.append((a*p0[0]+b*p1[0]+c*p2[0]+d*p3[0], a*p0[1]+b*p1[1]+c*p2[1]+d*p3[1]))
    return pts

TRAP = bez((440, 1245), (560, 1275), (600, 1170), (640, 1128)) \
     + bez((640, 1128), (675, 1092), (730, 1115), (735, 1210))[1:] \
     + [(735, 1210 + k * 30) for k in range(1, 12)]
SEG = [0.0]
for _i in range(1, len(TRAP)):
    SEG.append(SEG[-1] + math.dist(TRAP[_i-1], TRAP[_i]))
S_LEN = SEG[-1]
S_REST = next(SEG[i] for i in range(len(TRAP)) if TRAP[i][1] <= B_REST + 4 and TRAP[i][0] > 560)
S_LOW = next(SEG[i] for i in range(len(TRAP)) if TRAP[i][1] <= B_LOW - 6 and TRAP[i][0] > 480)

def at_s(s):
    s = clamp(s, 0, S_LEN)
    for i in range(1, len(TRAP)):
        if SEG[i] >= s:
            u = (s - SEG[i-1]) / max(1e-6, SEG[i] - SEG[i-1])
            return lerp(TRAP[i-1][0], TRAP[i][0], u), lerp(TRAP[i-1][1], TRAP[i][1], u)
    return TRAP[-1]

def trap_path(ctx, s0, s1):
    p = at_s(s0); ctx.move_to(*p)
    for i in range(len(TRAP)):
        if s0 < SEG[i] < s1: ctx.line_to(*TRAP[i])
    ctx.line_to(*at_s(s1))

def bowl_path(ctx):
    ctx.move_to(195, RIM_Y1)
    ctx.curve_to(185, 1130, 300, 1262, 420, 1272)
    ctx.line_to(470, 1272); ctx.line_to(480, 1218)
    ctx.curve_to(540, 1150, 565, 1060, 560, RIM_Y1)
    ctx.close_path()

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    f_open = ease((t - B(4) - 1.2) / 0.4) * (1 - ease((t - B(9) - 0.8) / 0.5))
    s['flap'] = f_open
    drain = ease((t - B(4) - 1.6) / (B(9) + 0.6 - B(4) - 1.6))
    refill = ease((t - B(10) - 0.6) / 4.5)
    s['tank'] = lerp(lerp(T_FULL, T_EMPTY, drain), T_FULL, refill)
    s['inflow'] = win(t, B(4) + 1.4, B(9) + 0.8, 0.3)
    s['fillflow'] = win(t, B(10) + 0.5, B(11) + 3.4, 0.3)
    s['refilltube'] = win(t, B(11) + 0.3, B(11) + 4.2, 0.3)
    rise = ease((t - B(5) - 0.5) / 2.2)
    sip = ease((t - B(7) - 0.8) / 2.6)
    back = ease((t - B(11) - 0.6) / 3.2)
    s['bowl'] = lerp(lerp(lerp(B_REST, B_HIGH, rise), B_LOW, sip), B_REST, back)
    fill = ease((t - B(6) - 1.2) / 2.2)
    brk = ease((t - B(8) - 0.3) / 2.2)
    s['trap'] = lerp(lerp(lerp(S_REST, S_LEN, fill), S_LOW, brk), S_REST, back)
    s['siphon'] = win(t, B(7) + 0.4, B(8) + 0.6, 0.3)
    s['bubbles'] = win(t, B(8) + 0.2, B(9) - 0.2, 0.3)
    s['jets'] = win(t, B(5) + 0.1, B(7) + 2.5, 0.3)
    dye = ease((t - B(14) - 0.6) / 1.0)
    s['dye_tank'] = dye
    s['dye_bowl'] = ease((t - B(14) - 2.6) / 1.4)
    s['drip'] = win(t, B(14) + 1.6, B(15), 0.3)
    s['h_tank'] = bw(t, 3); s['h_flap'] = bw(t, 4); s['h_bowl'] = bw(t, 5)
    s['h_trap'] = max(bw(t, 1), bw(t, 6)); s['h_float'] = bw(t, 9); s['h_fv'] = bw(t, 10)
    rc = bw(t, 13, 14)
    s['l_tank'] = max(bw(t, 3), rc); s['l_flap'] = max(bw(t, 4), rc); s['l_bowl'] = max(bw(t, 5), rc)
    s['l_trap'] = max(bw(t, 6), rc); s['l_float'] = max(bw(t, 9), rc); s['l_fv'] = max(bw(t, 10), rc)
    s['whoosh'] = win(t, B(7) + 1.0, B(8)); s['gurgle'] = win(t, B(8) + 0.4, B(9))
    s['sewer'] = max(bw(t, 6), rc)
    s['leak'] = win(t, B(14) + 2.8, B(15), 0.3)
    s['q'] = bw(t, 1)
    return s

def dots_along(ctx, pts_fn, n, t, speed, a, col=WHITE, r=5):
    for i in range(n):
        u = ((i / n) + t * speed) % 1.0
        x, y = pts_fn(u)
        ctx.arc(x, y, r, 0, 2*math.pi); setc(ctx, col, a); ctx.fill()

# ---------------------------------------------------------------- stage
def draw_toilet(ctx, t, s):
    wc_tank = lerpc(WATER, hexc('#e9897a'), s['dye_tank'])
    wc_bowl = lerpc(WATER, hexc('#efaaa0'), s['dye_bowl'])
    # drain pipe into the floor
    ctx.rectangle(735 - TUBE_W/2 - 6, 1470, TUBE_W + 12, 120); setc(ctx, INK2); ctx.fill()
    ctx.rectangle(735 - TUBE_W/2, 1470, TUBE_W, 120); setc(ctx, CAV); ctx.fill()
    if s['sewer'] > 0:
        text_c(ctx, "TO SEWER", 900, 1585, 26, CREAM, True, 2, s['sewer'])
        straight_arrow(ctx, 735, 1540, 735, 1600, CREAM, s['sewer'] * 0.8, lw=5, head=10)
    # porcelain body
    ctx.move_to(150, 945); ctx.curve_to(140, 1150, 250, 1270, 300, 1330)
    ctx.line_to(285, 1480); ctx.line_to(800, 1480); ctx.line_to(805, 1010); ctx.line_to(780, 945); ctx.close_path()
    fill_stroke(ctx, PORC, lw=6)
    # neck from tank to rim channel
    rrect(ctx, 560, 850, 130, 120, 6); fill_stroke(ctx, PORC, lw=5)
    ctx.rectangle(HOLE[0], 858, HOLE[1] - HOLE[0], 110); setc(ctx, CAV); ctx.fill()
    # rim channel
    rrect(ctx, 175, RIM_Y0, 490, RIM_Y1 - RIM_Y0, 10); setc(ctx, CAV); ctx.fill_preserve()
    setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    # bowl cavity + water
    bowl_path(ctx); setc(ctx, CAV); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.save(); bowl_path(ctx); ctx.clip()
    ctx.rectangle(150, s['bowl'], 500, 400); setc(ctx, wc_bowl); ctx.fill()
    ctx.move_to(150, s['bowl']); ctx.line_to(650, s['bowl']); setc(ctx, WATER_D); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    # trapway tube
    trap_path(ctx, 0, S_LEN); setc(ctx, INK); ctx.set_line_width(TUBE_W + 10)
    ctx.set_line_cap(cairo.LINE_CAP_BUTT); ctx.stroke()
    trap_path(ctx, 0, S_LEN); setc(ctx, CAV); ctx.set_line_width(TUBE_W); ctx.stroke()
    # re-open the bowl outlet (tube joins the bowl)
    ctx.save(); bowl_path(ctx); ctx.clip()
    ctx.rectangle(150, s['bowl'], 500, 400); setc(ctx, wc_bowl); ctx.fill(); ctx.restore()
    ctx.rectangle(420, 1222, 40, 46); setc(ctx, wc_bowl if s['bowl'] < 1222 else CAV); ctx.fill()
    if s['trap'] > 1:
        trap_path(ctx, 0, s['trap']); setc(ctx, wc_bowl); ctx.set_line_width(TUBE_W); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if s['siphon'] > 0:
        dots_along(ctx, lambda u: at_s(u * S_LEN), 14, t, 0.55, s['siphon'])
        straight_arrow(ctx, 380, 1150, 440, 1225, WATER_D, s['siphon'] * 0.9, lw=6)
        straight_arrow(ctx, 735, 1330, 735, 1440, WATER_D, s['siphon'] * 0.9, lw=6)
    if s['bubbles'] > 0:
        rnd = random.Random(3)
        for i in range(10):
            u = ((rnd.random() + t * 0.35) % 1.0)
            x, y = at_s(S_LEN * (1 - u))
            ctx.arc(x + rnd.uniform(-12, 12), y, 7 + 5 * rnd.random(), 0, 2*math.pi)
            setc(ctx, WHITE, s['bubbles']); ctx.fill_preserve(); setc(ctx, INK2, s['bubbles']); ctx.set_line_width(2); ctx.stroke()
    # rim jets
    if s['jets'] > 0:
        for x in (230, 310, 390, 470):
            straight_arrow(ctx, x, RIM_Y1 + 4, x + (8 if x < 400 else -8), RIM_Y1 + 70, WATER_D, s['jets'], lw=5, head=10)
        dots_along(ctx, lambda u: (lerp(640, 200, u), 978), 8, t, 0.9, s['jets'], WATER_D, 5)
    # seat
    rrect(ctx, 140, 930, 440, 22, 10); fill_stroke(ctx, MUSTARD, lw=4)

    # ---------------- tank
    x, y, w, h = TANK
    rrect(ctx, x, y, w, h, 14); fill_stroke(ctx, PORC, lw=6)
    rrect(ctx, x + 14, y + 14, w - 28, h - 24, 8); setc(ctx, CAV); ctx.fill()
    ctx.save(); rrect(ctx, x + 14, y + 14, w - 28, h - 24, 8); ctx.clip()
    ctx.rectangle(x, s['tank'], w, TB - s['tank']); setc(ctx, wc_tank); ctx.fill()
    ctx.move_to(x, s['tank']); ctx.line_to(x + w, s['tank']); setc(ctx, WATER_D); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    rrect(ctx, x - 10, y - 18, w + 20, 26, 8); fill_stroke(ctx, PORC, lw=5)        # lid
    # flush hole water stream into the neck
    if s['inflow'] > 0:
        ctx.rectangle(HOLE[0] + 6, TB - 4, HOLE[1] - HOLE[0] - 12, 105); setc(ctx, WATER, s['inflow']); ctx.fill()
        dots_along(ctx, lambda u: (lerp(600, 640, (u * 7) % 1), lerp(850, 960, u)), 6, t, 1.2, s['inflow'])
    # overflow tube
    rrect(ctx, OVF_X - 13, 615, 26, TB - 615, 6); fill_stroke(ctx, hexc('#d9dde0'), lw=4)
    # flapper (hinged at the right edge of the hole)
    ang = -1.1 * s['flap']
    ctx.save(); ctx.translate(HOLE[1] + 4, TB - 6); ctx.rotate(ang)
    rrect(ctx, -(HOLE[1] - HOLE[0]) - 14, -10, HOLE[1] - HOLE[0] + 18, 20, 8); fill_stroke(ctx, hexc('#c0392b'), lw=4)
    fx, fy = ctx.user_to_device(-(HOLE[1] - HOLE[0]) - 4, -10)
    ctx.restore()
    fx, fy = ctx.device_to_user(fx, fy)
    if s['drip'] > 0:
        dots_along(ctx, lambda u: (HOLE[0] + 10, lerp(TB, 960, u)), 3, t, 0.8, s['drip'], DYE, 5)
    # handle, lever and chain
    la = -0.35 * s['flap']
    rrect(ctx, x - 50, 470, 56, 22, 8); fill_stroke(ctx, hexc('#c9ced3'), lw=4)
    ctx.save(); ctx.translate(x + 6, 482); ctx.rotate(la)
    ctx.move_to(0, 0); ctx.line_to(140, 0); setc(ctx, INK); ctx.set_line_width(7); ctx.stroke()
    cx_, cy_ = ctx.user_to_device(130, 0)
    ctx.restore()
    cx_, cy_ = ctx.device_to_user(cx_, cy_)
    ctx.move_to(cx_, cy_); ctx.line_to(fx, fy); ctx.set_dash([7, 5]); setc(ctx, INK2); ctx.set_line_width(4)
    ctx.stroke(); ctx.set_dash([])
    # fill valve + float cup
    rrect(ctx, FV_X - 12, 600, 24, TB - 600, 5); fill_stroke(ctx, hexc('#d9dde0'), lw=4)
    rrect(ctx, FV_X - 26, 578, 52, 32, 8); fill_stroke(ctx, hexc('#9aa3ab'), lw=4)
    fl = min(s['tank'], 800) - 22
    rrect(ctx, FV_X - 34, fl, 68, 60, 10); fill_stroke(ctx, MUSTARD, lw=4)
    if s['fillflow'] > 0:
        dots_along(ctx, lambda u: (FV_X + 18, lerp(620, 850, u)), 5, t, 1.0, s['fillflow'], WATER_D, 5)
    if s['refilltube'] > 0:
        def rt(u):
            return (lerp(FV_X - 26, OVF_X, u), 590 - 40 * math.sin(math.pi * u)) if u < 0.6 else \
                   (OVF_X, lerp(600, TB, (u - 0.6) / 0.4))
        dots_along(ctx, rt, 8, t, 0.7, s['refilltube'], WATER_D, 5)
    ctx.move_to(FV_X - 26, 592); ctx.curve_to(760, 545, 700, 560, OVF_X, 612)
    setc(ctx, INK2); ctx.set_line_width(5); ctx.stroke()

    # ---------------- highlights + tags
    highlight(ctx, 680, 650, 210, 250, TEAL, s['h_tank'], t)
    highlight(ctx, 620, 855, 90, 45, RED, s['h_flap'], t)
    highlight(ctx, 375, 1130, 220, 160, ORANGE, s['h_bowl'], t)
    highlight(ctx, 640, 1250, 160, 180, RED, s['h_trap'], t)
    highlight(ctx, FV_X, fl + 30, 70, 60, ORANGE, s['h_float'], t)
    highlight(ctx, FV_X, 720, 60, 170, TEAL, s['h_fv'], t)
    if s['q'] > 0: text_c(ctx, "?", 650, 1200, 90, RED, True, 0, s['q'])
    tag(ctx, "1 · TANK", 680, 380, TEAL, s['l_tank'])
    tag(ctx, "2 · FLAPPER", 395, 828, RED, s['l_flap'])
    tag(ctx, "3 · BOWL", 330, 896, ORANGE, s['l_bowl'])
    tag(ctx, "4 · TRAPWAY", 925, 1180, RED, s['l_trap'])
    tag(ctx, "5 · FLOAT", 960, 770, ORANGE, s['l_float'])
    tag(ctx, "6 · FILL VALVE", 935, 545, TEAL, s['l_fv'])
    if s['whoosh'] > 0: tag(ctx, "SIPHON!", 925, 1330, WATER_D, s['whoosh'], 30)
    if s['gurgle'] > 0: tag(ctx, "AIR IN = SIPHON OFF", 900, 1330, INK, s['gurgle'], 24)
    if s['leak'] > 0: tag(ctx, "LEAKY FLAPPER!", 380, 1400, RED, s['leak'], 28)

SFX = [(B(3) + 0.2, 'pop'), (B(4) + 0.2, 'pop'), (B(4) + 1.2, 'click'), (B(5) + 0.2, 'pop'),
       (B(6) + 0.2, 'pop'), (B(7) + 0.8, 'whoosh'), (B(9) + 0.2, 'pop'), (B(9) + 0.8, 'click'),
       (B(10) + 0.2, 'pop'), (B(13) + 0.2, 'ding'), (B(14) + 2.8, 'pop')]
HUM = []

def draw_set(ctx):
    window(ctx, 40, 300, 190, 290)

def draw(ctx, t, E):
    draw_toilet(ctx, t, state(t))

# ---------------------------------------------------------------- cards
def card_siphon(ctx, t, lt, a):
    card_frame(ctx, "THE SIPHON", a, "FALLING WATER PULLS THE REST ALONG", TEAL)
    flow = ease((lt - 0.6) / 4.0)
    # high container
    rrect(ctx, 150, 300, 250, 170, 10); fill_stroke(ctx, CREAM, lw=4, alpha=a)
    lv = lerp(330, 445, flow)
    ctx.rectangle(154, lv, 242, 466 - lv); setc(ctx, WATER, a); ctx.fill()
    # low container
    rrect(ctx, 690, 400, 250, 135, 10); fill_stroke(ctx, CREAM, lw=4, alpha=a)
    lv2 = lerp(510, 430, flow)
    ctx.rectangle(694, lv2, 242, 531 - lv2); setc(ctx, WATER, a); ctx.fill()
    # hose
    HOSE = bez((330, 450), (330, 210), (560, 220), (560, 300), 20) + bez((560, 300), (560, 380), (780, 260), (790, 515), 20)[1:]
    def hose(u):
        return HOSE[min(len(HOSE) - 1, int(u * (len(HOSE) - 1)))]
    ctx.move_to(330, 450); ctx.curve_to(330, 210, 560, 220, 560, 300); ctx.curve_to(560, 380, 780, 260, 790, 515)
    setc(ctx, INK, a); ctx.set_line_width(26); ctx.stroke()
    ctx.move_to(330, 450); ctx.curve_to(330, 210, 560, 220, 560, 300); ctx.curve_to(560, 380, 780, 260, 790, 515)
    setc(ctx, WATER, a); ctx.set_line_width(16); ctx.stroke()
    on = a * (1 - ease((lt - 4.6) / 0.4))
    dots_along(ctx, hose, 10, t, 0.6, on, WATER_D, 4)

def card_seal(ctx, t, lt, a):
    card_frame(ctx, "THE WATER SEAL", a, "WATER PLUG = NO SEWER SMELL", TEAL)
    ctx.move_to(240, 270); ctx.line_to(240, 420); ctx.curve_to(240, 540, 480, 540, 480, 420)
    ctx.line_to(480, 340); ctx.line_to(900, 340)
    setc(ctx, INK, a); ctx.set_line_width(64); ctx.set_line_cap(cairo.LINE_CAP_BUTT); ctx.stroke()
    ctx.move_to(240, 270); ctx.line_to(240, 420); ctx.curve_to(240, 540, 480, 540, 480, 420)
    ctx.line_to(480, 340); ctx.line_to(900, 340)
    setc(ctx, CAV, a); ctx.set_line_width(52); ctx.stroke()
    lvl = lerp(470, 400, ease((lt - 0.3) / 1.4))
    ctx.save(); ctx.rectangle(200, lvl, 320, 200); ctx.clip()
    ctx.move_to(240, 270); ctx.line_to(240, 420); ctx.curve_to(240, 540, 480, 540, 480, 420); ctx.line_to(480, 340)
    setc(ctx, WATER, a); ctx.set_line_width(52); ctx.stroke(); ctx.restore()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ga = a * ease((lt - 1.8) / 0.6)
    wavy_arrow(ctx, 880, 340, 560, 340, t, hexc('#7a8a3a'), ga, amp=8)
    text_c(ctx, "SEWER GAS", 760, 300, 24, hexc('#7a8a3a'), True, 1, ga)
    xa = a * ease((lt - 2.8) / 0.4)
    ctx.move_to(500, 380); ctx.line_to(540, 420); ctx.move_to(540, 380); ctx.line_to(500, 420)
    setc(ctx, RED, xa); ctx.set_line_width(7); ctx.stroke()
    text_c(ctx, "BOWL", 240, 255, 22, INK, True, 1, a)

def card_bucket(ctx, t, lt, a):
    card_frame(ctx, "NO TANK NEEDED", a, "FAST WATER STARTS THE SIPHON", ORANGE)
    tip = ease((lt - 0.4) / 0.8)
    pour = win(lt, 0.9, 3.0, 0.3)
    sip = ease((lt - 2.4) / 1.6)
    # mini bowl
    bx = 470
    ctx.move_to(bx, 380); ctx.curve_to(bx, 500, bx + 120, 520, bx + 170, 520); ctx.line_to(bx + 230, 520)
    ctx.curve_to(bx + 260, 470, bx + 260, 420, bx + 250, 380); ctx.close_path()
    fill_stroke(ctx, CAV, lw=4, alpha=a)
    lv = lerp(lerp(450, 400, ease((lt - 1.0) / 1.2)), 505, sip)
    ctx.save()
    ctx.move_to(bx, 380); ctx.curve_to(bx, 500, bx + 120, 520, bx + 170, 520); ctx.line_to(bx + 230, 520)
    ctx.curve_to(bx + 260, 470, bx + 260, 420, bx + 250, 380); ctx.close_path(); ctx.clip()
    ctx.rectangle(bx - 10, lv, 280, 200); setc(ctx, WATER, a); ctx.fill(); ctx.restore()
    # trap stub
    ctx.move_to(bx + 230, 505); ctx.curve_to(bx + 330, 505, bx + 330, 420, bx + 380, 420); ctx.line_to(bx + 400, 540)
    setc(ctx, INK, a); ctx.set_line_width(30); ctx.stroke()
    ctx.move_to(bx + 230, 505); ctx.curve_to(bx + 330, 505, bx + 330, 420, bx + 380, 420); ctx.line_to(bx + 400, 540)
    setc(ctx, lerpc(CAV, WATER, win(lt, 1.8, 4.2, 0.3)), a); ctx.set_line_width(20); ctx.stroke()
    # bucket
    ctx.save(); ctx.translate(290, 360); ctx.rotate(1.1 * tip)
    ctx.move_to(-60, -55); ctx.line_to(60, -55); ctx.line_to(45, 55); ctx.line_to(-45, 55); ctx.close_path()
    fill_stroke(ctx, hexc('#c9ced3'), lw=4, alpha=a)
    ctx.arc(0, -55, 60, math.pi, 2*math.pi); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    if pour > 0:
        ctx.move_to(360, 360); ctx.curve_to(450, 350, 500, 370, 520, 420)
        setc(ctx, WATER, a * pour); ctx.set_line_width(26); ctx.stroke()
    if sip > 0.05:
        straight_arrow(ctx, bx + 400, 470, bx + 400, 550, WATER_D, a * win(lt, 2.4, 5.5, 0.3), lw=6)
        text_c(ctx, "WHOOSH!", bx + 120, 300, 34, WATER_D, True, 2, a * win(lt, 2.6, 5.5, 0.3))

CARDS = {'siphon': card_siphon, 'seal': card_seal, 'bucket': card_bucket}
