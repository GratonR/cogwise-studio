"""Cogwise episode: How does a dishwasher work?  (one small puddle, pumped in a loop, heated and filtered)"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="dishwasher",
    title="Your dishwasher never fills up 🍽️",
    description=("It cleans a full load with one hot puddle: pumped, sprayed, filtered, again and again.\n\n"
                 "#Shorts #howthingswork #dishwasher #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "dishwasher", "appliances", "engineering", "cogwise"],
    sources=[
        "https://www.whirlpool.com/blog/kitchen/how-does-a-dishwasher-work.html",
        "https://reviewed.com/dishwashers/features/what-actually-happens-inside-a-dishwasher",
        "https://www.epa.gov/system/files/documents/2023-08/ws-homes-TRM-6-DishwashersTechSheet.pdf",
        "https://patents.google.com/patent/US8905053B2/en",
    ],
)

BEATS = [
    dict(dur=4.5, title="IT NEVER FILLS UP", caption="Your dishwasher never fills up. It cleans everything with one puddle."),
    dict(dur=5.5, title="THE SECRET: A PUDDLE", caption="Just four liters, one gallon, in the bottom. A float stops the valve."),
    dict(dur=5.5, title="1 · THE PUMP", caption="A pump sucks that puddle up and blasts it through the spray arms."),
    dict(dur=5.5, title=None, caption="The arms have no motor: angled jets push them around, like a sprinkler.", card='arms'),
    dict(dur=5.5, title="2 · THE HEATER", caption="A heater warms it to about sixty Celsius, a hundred forty Fahrenheit."),
    dict(dur=5.5, title="3 · THE FILTER", caption="On every pass, a filter catches the food, so the water stays usable."),
    dict(dur=4.5, title="THE LOOP", caption="Same water: sprayed, caught, pumped again, for many minutes."),
    dict(dur=5.0, title="DRAIN · RINSE · DRY", caption="Then it drains, rinses with fresh water, drains again, and dries."),
    dict(dur=6.0, title=None, caption="Whole cycle: about thirteen liters, three and a half gallons. By hand: up to a hundred liters.", card='compare'),
    dict(dur=5.0, title="DISHWASHER = PUDDLE + LOOP", caption="So: one hot puddle, pumped in a loop, filtered on every pass."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

ANCHOR = (540, 1480)

# ---------------------------------------------------------------- geometry (screen: y grows DOWN)
CAB = (190, 420, 700, 1070)              # cabinet x, y, w, h -> 190..890, 420..1490
TUB_L, TUB_R, TUB_T = 222, 858, 450
FLOOR_SIDE, FLOOR_MID = 1352, 1384       # floor is higher at the walls, slopes down to the sump
SUMP = (460, 620, 1440)                  # x0, x1, bottom y
PUMP = (540, 1462, 30)                   # circulation pump under the sump
DPUMP = (372, 1462, 22)                  # drain pump
RISER_X = 826
UP_Y, LO_Y = 880, 1300                   # spray-arm heights
UP_L, LO_L = 200, 250
L_FULL, L_EMPTY, L_RUN = 1370, 1442, 1378
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); TUB = hexc('#eef0ee'); CAV = hexc('#e9dfca')
WATER = hexc('#8fcfc8'); WATER_D = hexc('#1f8a8a'); FOOD = hexc('#8a6a3a'); GREEN = hexc('#4c9d6b')
PLATE = hexc('#fffaf0'); HOTC = hexc('#e4472f')

def tub_path(ctx):
    ctx.move_to(TUB_L, TUB_T); ctx.line_to(TUB_R, TUB_T); ctx.line_to(TUB_R, FLOOR_SIDE)
    ctx.line_to(SUMP[1], FLOOR_MID); ctx.line_to(SUMP[1], SUMP[2]); ctx.line_to(SUMP[0], SUMP[2])
    ctx.line_to(SUMP[0], FLOOR_MID); ctx.line_to(TUB_L, FLOOR_SIDE); ctx.close_path()

def floor_y(x):
    if x < SUMP[0]: return lerp(FLOOR_SIDE, FLOOR_MID, (x - TUB_L) / (SUMP[0] - TUB_L))
    if x > SUMP[1]: return lerp(FLOOR_MID, FLOOR_SIDE, (x - SUMP[1]) / (TUB_R - SUMP[1]))
    return SUMP[2]

def poly_at(pts, u):
    seg = [0.0]
    for i in range(1, len(pts)): seg.append(seg[-1] + math.dist(pts[i-1], pts[i]))
    s = clamp(u) * seg[-1]
    for i in range(1, len(pts)):
        if seg[i] >= s:
            k = (s - seg[i-1]) / max(1e-6, seg[i] - seg[i-1])
            return lerp(pts[i-1][0], pts[i][0], k), lerp(pts[i-1][1], pts[i][1], k)
    return pts[-1]

# water paths (flow direction = list order)
P_UPPER = [(540, 1410), (PUMP[0], PUMP[1]), (RISER_X, PUMP[1]), (RISER_X, UP_Y - 22), (540, UP_Y - 22), (540, UP_Y)]
P_LOWER = [(540, 1410), (PUMP[0], PUMP[1]), (540, LO_Y)]
P_DRAIN = [(470, 1430), (DPUMP[0], DPUMP[1]), (150, DPUMP[1]), (110, 1300), (70, 1300), (60, 1560)]
P_INLET = [(20, 1250), (110, 1250), (110, 1150), (TUB_L + 4, 1150), (TUB_L + 14, 1345)]

def dots(ctx, pts, n, t, speed, a, col=WATER_D, r=6):
    if a <= 0: return
    for i in range(n):
        x, y = poly_at(pts, ((i / n) + t * speed) % 1.0)
        ctx.arc(x, y, r, 0, 2*math.pi); setc(ctx, col, a); ctx.fill()

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    fill1 = ease((t - B(1) - 0.4) / 2.6)
    drain1 = ease((t - B(7) + 0.0) / 1.2)
    fill2 = ease((t - B(7) - 1.3) / 1.0)
    drain2 = ease((t - B(7) - 2.6) / 1.0)
    lvl = lerp(L_EMPTY, L_FULL, fill1)
    lvl = lerp(lvl, L_RUN, ease((t - B(2) - 0.6) / 1.0))      # some water is in the pipes while spraying
    lvl = lerp(lvl, L_EMPTY, drain1)
    lvl = lerp(lvl, L_FULL, fill2)
    lvl = lerp(lvl, L_EMPTY, drain2)
    lvl = lerp(lvl, L_RUN, ease((t - B(9) - 0.2) / 1.0))      # recap: the puddle runs again
    s['lvl'] = lvl
    s['dirty'] = 1 - ease((t - B(7) - 1.3) / 1.0)              # water tint (food) until the fresh rinse
    s['ghost'] = win(t, 0.0, 3.4, 0.3)
    s['ghost_h'] = ease(t / 1.8)
    s['ghost_x'] = win(t, 1.9, 3.4, 0.25)
    s['inflow'] = win(t, B(1) + 0.3, B(1) + 3.0, 0.25) + win(t, B(7) + 1.3, B(7) + 2.3, 0.2)
    s['float'] = ease((t - B(1) - 2.2) / 0.6) * (1 - drain1) + (ease((t - B(7) - 2.0) / 0.3) * (1 - drain2) if t > B(7) else 0)
    s['valve_shut'] = win(t, B(1) + 3.0, B(2) - 0.1, 0.25)
    s['spray'] = max(win(t, B(2) + 0.6, B(7) + 0.1, 0.4), win(t, B(9) + 0.4, B(10), 0.4))
    s['pump_on'] = s['spray']
    s['drain'] = win(t, B(7) + 0.0, B(7) + 1.3, 0.2) + win(t, B(7) + 2.6, B(7) + 3.6, 0.2)
    s['heat'] = win(t, B(4) + 0.4, B(7), 0.4)
    s['temp'] = ease((t - B(4) - 0.6) / 3.0)
    s['crumbs'] = ease((t - B(5) - 0.3) / 2.6)
    s['steam'] = win(t, B(7) + 3.6, B(8) + 1.0, 0.3)
    s['h_puddle'] = bw(t, 1); s['h_pump'] = bw(t, 2); s['h_heat'] = bw(t, 4); s['h_filter'] = bw(t, 5)
    rc = bw(t, 9, 10)
    s['l_valve'] = max(bw(t, 1), rc * 0); s['l_float'] = bw(t, 1)
    s['l_pump'] = max(bw(t, 2, 4), rc); s['l_heat'] = max(bw(t, 4), rc); s['l_filter'] = max(bw(t, 5), rc)
    s['l_drain'] = win(t, B(7) + 0.1, B(7) + 3.8, 0.3)
    s['l_arms'] = bw(t, 2)
    s['loop'] = max(bw(t, 6), rc)
    return s

# ---------------------------------------------------------------- dishes
def plate(ctx, cx, cy, r, food):
    ctx.arc(cx, cy, r, 0, 2*math.pi); fill_stroke(ctx, PLATE, lw=4)
    ctx.arc(cx, cy, r * 0.62, 0, 2*math.pi); setc(ctx, INK2); ctx.set_line_width(2); ctx.stroke()
    if food > 0:
        rnd = random.Random(int(cx))
        for _ in range(6):
            a_ = rnd.uniform(0, 2*math.pi); d = rnd.uniform(0, r * 0.5)
            ctx.arc(cx + d*math.cos(a_), cy + d*math.sin(a_), rnd.uniform(5, 9), 0, 2*math.pi)
            setc(ctx, FOOD, food); ctx.fill()

def cup(ctx, x, y_bottom, w, h):
    """cup upside-down on the rack: open mouth DOWN (facing the jets), base up."""
    ctx.move_to(x - w/2, y_bottom); ctx.line_to(x - w*0.38, y_bottom - h)
    ctx.line_to(x + w*0.38, y_bottom - h); ctx.line_to(x + w/2, y_bottom)
    fill_stroke(ctx, hexc('#d8ecea'), lw=4)

def spray_arm(ctx, cy, L, ang, t, spray, a_hl=0):
    """front view of an arm spinning about a vertical axis: apparent length = L*cos(angle)."""
    lv = L * math.cos(ang)
    ctx.move_to(540 - lv, cy); ctx.line_to(540 + lv, cy)
    setc(ctx, INK); ctx.set_line_width(22); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.move_to(540 - lv, cy); ctx.line_to(540 + lv, cy)
    setc(ctx, STEEL); ctx.set_line_width(14); ctx.stroke()
    ctx.arc(540, cy, 15, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=4)
    if spray > 0:
        rnd = random.Random(int(cy))
        for k in range(-3, 4):
            if k == 0: continue
            x0 = 540 + lv * k / 3.0
            for j in range(3):
                u = (t * 2.2 + rnd.random()) % 1.0
                lean = 0.18 * (1 if k > 0 else -1)
                ln = 70 + 160 * u
                x1, y1 = x0 + lean * ln, cy - 14 - ln
                ctx.move_to(x0 + lean * (ln - 40), cy - 14 - (ln - 40)); ctx.line_to(x1, y1)
                setc(ctx, WATER_D, spray * (1 - u) * 0.9); ctx.set_line_width(4); ctx.stroke()

def falling_drops(ctx, t, a, y0, y1, seed):
    if a <= 0: return
    rnd = random.Random(seed)
    for _ in range(26):
        x = rnd.uniform(TUB_L + 20, TUB_R - 20); ph = rnd.random()
        u = (ph + t * 0.9) % 1.0
        y = lerp(y0, y1, u)
        ctx.move_to(x, y); ctx.line_to(x, y + 16); setc(ctx, WATER_D, a * 0.55); ctx.set_line_width(4); ctx.stroke()

# ---------------------------------------------------------------- stage
def draw_dishwasher(ctx, t, s):
    x, y, w, h = CAB
    # cabinet + tub
    rrect(ctx, x, y, w, h, 16); fill_stroke(ctx, STEEL, lw=6)
    tub_path(ctx); setc(ctx, TUB); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # control strip
    rrect(ctx, x + 20, y - 34, w - 40, 30, 8); fill_stroke(ctx, hexc('#9aa3ab'), lw=4)
    for i in range(4):
        ctx.arc(x + 70 + i * 40, y - 19, 7, 0, 2*math.pi); setc(ctx, CREAM); ctx.fill()
    # ghost: the misconception (a tub filled to the top) -> crossed out
    if s['ghost'] > 0:
        gtop = lerp(FLOOR_SIDE, TUB_T + 30, s['ghost_h'])
        ctx.save(); tub_path(ctx); ctx.clip()
        ctx.rectangle(TUB_L, gtop, TUB_R - TUB_L, 1500 - gtop); setc(ctx, WATER, 0.35 * s['ghost']); ctx.fill()
        ctx.move_to(TUB_L, gtop); ctx.line_to(TUB_R, gtop); ctx.set_dash([16, 10])
        setc(ctx, WATER_D, s['ghost']); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
        ctx.restore()
        if s['ghost_x'] > 0:
            ctx.move_to(320, 600); ctx.line_to(760, 1180); ctx.move_to(760, 600); ctx.line_to(320, 1180)
            setc(ctx, RED, s['ghost_x']); ctx.set_line_width(14); ctx.stroke()
            tag(ctx, "NOT A FULL TUB", 540, 540, RED, s['ghost_x'], 30)

    # ---- plumbing under/around the tub (drawn first so the tub floor sits on top)
    for pts, col in ((P_UPPER, STEEL_D), (P_LOWER, STEEL_D)):
        ctx.move_to(*pts[1])
        for p in pts[2:]: ctx.line_to(*p)
        setc(ctx, INK); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_BUTT); ctx.stroke()
        ctx.move_to(*pts[1])
        for p in pts[2:]: ctx.line_to(*p)
        setc(ctx, hexc('#dfe3e6')); ctx.set_line_width(16); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    # drain hose (out to the left, with a high loop)
    ctx.move_to(*P_DRAIN[1])
    for p in P_DRAIN[2:]: ctx.line_to(*p)
    setc(ctx, INK); ctx.set_line_width(20); ctx.stroke()
    ctx.move_to(*P_DRAIN[1])
    for p in P_DRAIN[2:]: ctx.line_to(*p)
    setc(ctx, hexc('#7d8a8a')); ctx.set_line_width(12); ctx.stroke()
    # inlet hose + valve (left)
    ctx.move_to(*P_INLET[0])
    for p in P_INLET[1:4]: ctx.line_to(*p)
    setc(ctx, INK); ctx.set_line_width(18); ctx.stroke()
    ctx.move_to(*P_INLET[0])
    for p in P_INLET[1:4]: ctx.line_to(*p)
    setc(ctx, hexc('#e9dfca')); ctx.set_line_width(10); ctx.stroke()
    vopen = clamp(s['inflow'])
    rrect(ctx, 82, 1222, 56, 56, 8); fill_stroke(ctx, RED if s['valve_shut'] > 0.5 else TEAL, lw=4)
    text_c(ctx, "V", 110, 1260, 30, CREAM, True, 0)

    # ---- water (clipped to the tub)
    wcol = lerpc(WATER, hexc('#b9b48a'), 0.6 * s['dirty'] * s['crumbs'])
    ctx.save(); tub_path(ctx); ctx.clip()
    ctx.rectangle(TUB_L, s['lvl'], TUB_R - TUB_L, 1500 - s['lvl']); setc(ctx, wcol); ctx.fill()
    ctx.move_to(TUB_L, s['lvl']); ctx.line_to(TUB_R, s['lvl']); setc(ctx, WATER_D); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    tub_path(ctx); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()

    # inlet stream down the wall
    if s['inflow'] > 0:
        dots(ctx, P_INLET, 10, t, 0.8, clamp(s['inflow']), WATER_D, 6)
    # float (sits in a little cage on the right of the sump; rises with the water)
    fx = 700; fy = lerp(floor_y(fx) - 16, floor_y(fx) - 34, s['float'])
    ctx.rectangle(fx - 30, floor_y(fx) - 60, 60, 60); ctx.set_dash([6, 6]); setc(ctx, INK2); ctx.set_line_width(3)
    ctx.stroke(); ctx.set_dash([])
    rrect(ctx, fx - 22, fy - 14, 44, 28, 10); fill_stroke(ctx, MUSTARD, lw=4)
    # filter: mesh cup in the sump
    fl = (468, 1356, 144, 80)
    rrect(ctx, *fl, 8); setc(ctx, WHITE, 0.25); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    ctx.save(); rrect(ctx, *fl, 8); ctx.clip()
    for k in range(-10, 20):
        ctx.move_to(fl[0] + k * 14, fl[1]); ctx.line_to(fl[0] + k * 14 + 80, fl[1] + 80)
    setc(ctx, INK2, 0.6); ctx.set_line_width(2); ctx.stroke(); ctx.restore()
    # crumbs collected on the filter
    if s['crumbs'] > 0:
        rnd = random.Random(9)
        for i in range(14):
            k = clamp(s['crumbs'] * 1.4 - i * 0.05)
            if k <= 0: continue
            sx = rnd.uniform(260, 820); ex = rnd.uniform(480, 600)
            sy = rnd.uniform(1120, 1240)
            u = ease(k)
            px = lerp(sx, ex, ease(clamp((u - 0.5) * 2)))
            py = lerp(sy, floor_y(sx) - 6, ease(clamp(u * 2))) if u < 0.5 else lerp(floor_y(sx) - 6, 1350, ease(clamp((u - 0.5) * 2)))
            ctx.arc(px, py, 7, 0, 2*math.pi); setc(ctx, FOOD); ctx.fill()
    # pumps
    pa = s['pump_on']
    ctx.arc(PUMP[0], PUMP[1], PUMP[2], 0, 2*math.pi); fill_stroke(ctx, TEAL if pa > 0.5 else STEEL_D, lw=5)
    ctx.save(); ctx.translate(PUMP[0], PUMP[1]); ctx.rotate(t * 9 * pa)
    for k in range(4):
        ctx.move_to(0, 0); ctx.line_to(20, 0); ctx.rotate(math.pi / 2)
    setc(ctx, CREAM); ctx.set_line_width(5); ctx.stroke(); ctx.restore()
    da = clamp(s['drain'])
    ctx.arc(DPUMP[0], DPUMP[1], DPUMP[2], 0, 2*math.pi); fill_stroke(ctx, ORANGE if da > 0.5 else STEEL_D, lw=4)
    ctx.move_to(SUMP[0], 1430); ctx.line_to(DPUMP[0] + DPUMP[2], DPUMP[1]); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # heater element on the floor (left + right of the sump)
    hcol = lerpc(STEEL_D, HOTC, s['heat'] * (0.6 + 0.4 * math.sin(t * 6) ** 2))
    for (a_, b_) in ((TUB_L + 30, SUMP[0] - 16), (SUMP[1] + 16, TUB_R - 30)):
        ctx.move_to(a_, floor_y(a_) - 12); ctx.line_to(b_, floor_y(b_) - 12)
        setc(ctx, INK); ctx.set_line_width(14); ctx.stroke()
        ctx.move_to(a_, floor_y(a_) - 12); ctx.line_to(b_, floor_y(b_) - 12)
        setc(ctx, hcol); ctx.set_line_width(8); ctx.stroke()
    if s['heat'] > 0:
        for hx in (300, 400, 680, 780):
            wavy_arrow(ctx, hx, floor_y(hx) - 30, hx, floor_y(hx) - 130, t, HOTC, s['heat'], amp=7, wl=30, lw=4, head=10)

    # ---- racks and dishes
    ctx.move_to(TUB_L + 10, 1268); ctx.line_to(TUB_R - 10, 1268); setc(ctx, INK2); ctx.set_line_width(5); ctx.stroke()
    for k in range(9):
        xx = 270 + k * 68; ctx.move_to(xx, 1268); ctx.line_to(xx, 1240); ctx.stroke()
    food = 1 - s['crumbs']
    for i, cx in enumerate((300, 430, 560, 690, 800)):
        plate(ctx, cx, 1170, 82 if i % 2 == 0 else 74, food)
    ctx.move_to(TUB_L + 10, 840); ctx.line_to(TUB_R - 10, 840); setc(ctx, INK2); ctx.set_line_width(5); ctx.stroke()
    for cx in (300, 400, 520, 640, 760):
        cup(ctx, cx, 836, 78, 92)
    # spray arms (spin about a vertical axis)
    ang = t * 5.0 * s['spray']
    spray_arm(ctx, LO_Y, LO_L, ang, t, s['spray'])
    spray_arm(ctx, UP_Y, UP_L, ang * 1.3 + 0.7, t, s['spray'])
    falling_drops(ctx, t, s['spray'], 700, 1350, 4)
    # pumped water path (sump -> pump -> pipes -> arms)
    loop_a = s['spray']
    dots(ctx, P_UPPER, 12, t, 0.45, loop_a, WATER_D, 6)
    dots(ctx, P_LOWER, 5, t, 0.8, loop_a, WATER_D, 6)
    if da > 0: dots(ctx, P_DRAIN, 12, t, 0.7, da, hexc('#7a8a3a'), 6)
    # steam (dry)
    if s['steam'] > 0:
        for sx in (330, 470, 610, 750):
            wavy_arrow(ctx, sx, 1060, sx, 900, t, STEEL_D, s['steam'] * 0.8, amp=8, wl=34, lw=5, head=10)

    # ---- highlights + tags
    highlight(ctx, 540, 1395, 210, 60, TEAL, s['h_puddle'], t)
    highlight(ctx, PUMP[0], PUMP[1], 60, 50, TEAL, s['h_pump'], t)
    highlight(ctx, 540, 1350, 330, 50, HOTC, s['h_heat'], t)
    highlight(ctx, 540, 1395, 100, 60, ORANGE, s['h_filter'], t)
    tag(ctx, "INLET VALVE", 140, 1110, TEAL, s['l_valve'])
    tag(ctx, "FLOAT", 760, 1300, ORANGE, s['l_float'])
    def lead(x0, y0, x1, y1, a):
        if a > 0:
            ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.set_dash([6, 6]); setc(ctx, INK2, a)
            ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    lead(890, 1452, PUMP[0] + 34, PUMP[1], s['l_pump'])
    lead(890, 1345, 790, 1350, s['l_heat'])
    lead(890, 1398, 612, 1400, s['l_filter'])
    tag(ctx, "1 · PUMP", 985, 1452, TEAL, s['l_pump'])
    tag(ctx, "SPRAY ARMS", 860, 960, TEAL, s['l_arms'])
    tag(ctx, "2 · HEATER", 985, 1345, HOTC, s['l_heat'])
    tag(ctx, "3 · FILTER", 985, 1398, ORANGE, s['l_filter'])
    lead(150, 1100, DPUMP[0] - 16, DPUMP[1] - 16, s['l_drain'])
    tag(ctx, "DRAIN PUMP", 150, 1080, ORANGE, s['l_drain'])
    if s['loop'] > 0:
        # big loop arrow on the right: down the tub, up the riser
        ctx.arc(960, 1150, 70, -math.pi/2, math.pi * 1.1)
        setc(ctx, WATER_D, s['loop']); ctx.set_line_width(8); ctx.stroke()
        straight_arrow(ctx, 930, 1080, 962, 1080, WATER_D, s['loop'], lw=8, head=14)
        text_c(ctx, "LOOP", 960, 1160, 28, WATER_D, True, 2, s['loop'])

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_dishwasher(ctx, t, state(t))

CAMKEYS = [(0, 540, 960, 1.0),
           (B(1) + 0.2, 470, 1180, 1.25),
           (B(2) + 0.3, 540, 960, 1.0),
]
def CAM(t): return cam_track(CAMKEYS, t)

def draw_hud(ctx, t, E):
    a1 = bw(t, 1)
    if a1 > 0: hud(ctx, "WATER IN THE TUB", "4 L · 1 GAL", "just a puddle", a1, TEAL, x=520, y=200, w=520)
    a4 = bw(t, 4)
    if a4 > 0:
        c = round(lerp(20, 60, state(t)['temp'])); f = round(c * 9 / 5 + 32)
        hud(ctx, "WATER TEMPERATURE", f"{c} °C · {f} °F", None, a4, HOTC, x=520, y=200, w=520)
    a6 = bw(t, 6)
    if a6 > 0: hud(ctx, "SAME WATER, AGAIN", "4 L · 1 GAL", "sprayed → caught → pumped", a6, WATER_D, x=520, y=200, w=520)

SFX = [(B(1) + 0.3, 'click'), (B(1) + 2.8, 'pop'), (B(1) + 3.0, 'click'), (B(2) + 0.3, 'pop'),
       (B(4) + 0.3, 'pop'), (B(5) + 0.3, 'pop'), (B(7) + 0.2, 'pop'), (B(9) + 0.2, 'ding')]
HUM = []

# ---------------------------------------------------------------- cards
def card_arms(ctx, t, lt, a):
    """TOP view of a spray arm. Jets leave each tip backwards; the reaction pushes the tip forward.
    Screen y grows down, so a positive cairo rotation = CLOCKWISE on screen."""
    card_frame(ctx, "SPRAY ARM, SEEN FROM ABOVE", a, "JETS PUSH BACK = THE ARM SPINS", TEAL)
    cx, cy, L = 380, 400, 105
    ang = 1.6 * lt                                     # clockwise on screen
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(ang)
    ctx.move_to(-L, 0); ctx.line_to(L, 0); setc(ctx, INK, a); ctx.set_line_width(30); ctx.stroke()
    ctx.move_to(-L, 0); ctx.line_to(L, 0); setc(ctx, STEEL, a); ctx.set_line_width(20); ctx.stroke()
    ctx.arc(0, 0, 18, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)
    # right tip: arm moves toward +y (clockwise) -> jet must leave toward -y; left tip mirrored
    for sx in (1, -1):
        tipx = sx * (L - 10)
        jy = -sx                                        # jet direction (y) at this tip
        for k in range(4):
            u = (lt * 2.5 + k / 4) % 1.0
            ctx.arc(tipx + sx * 10 * u, jy * (20 + 90 * u), 6 * (1 - u) + 2, 0, 2*math.pi)
            setc(ctx, WATER_D, a * (1 - u)); ctx.fill()
        straight_arrow(ctx, tipx, jy * 18, tipx + sx * 14, jy * 95, WATER_D, a, lw=5, head=11)   # jet
        straight_arrow(ctx, tipx, -jy * 18, tipx, -jy * 80, RED, a, lw=6, head=12)              # push
    ctx.restore()
    # rotation sense arrow (clockwise)
    ctx.arc(cx, cy, L + 36, -2.2, -0.9); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    ex, ey = cx + (L + 36) * math.cos(-0.9), cy + (L + 36) * math.sin(-0.9)
    straight_arrow(ctx, ex - 12 * math.cos(-0.9 + math.pi/2), ey - 12 * math.sin(-0.9 + math.pi/2), ex, ey, INK, a, lw=5, head=12)
    # legend
    straight_arrow(ctx, 680, 320, 760, 320, WATER_D, a, lw=6, head=12)
    text_c(ctx, "WATER JET", 860, 330, 26, WATER_D, True, 1, a)
    straight_arrow(ctx, 680, 400, 760, 400, RED, a, lw=6, head=12)
    text_c(ctx, "PUSH BACK", 860, 410, 26, RED, True, 1, a)
    text_c(ctx, "no motor", 810, 480, 26, INK2, False, 1, a)

def card_compare(ctx, t, lt, a):
    card_frame(ctx, "WATER FOR ONE FULL LOAD", a, "≈ 13 L DISHWASHER  vs  UP TO 100 L BY HAND", TEAL)
    g = ease((lt - 0.4) / 1.4); g2 = ease((lt - 1.8) / 2.2)
    for (gx, frac, k, lab, val, col) in ((240, 0.13, g, "DISHWASHER", "13 L · 3.5 GAL", TEAL),
                                         (840, 1.0, g2, "BY HAND", "100 L · 26 GAL", RED)):
        rrect(ctx, gx - 60, 280, 120, 240, 10); fill_stroke(ctx, CREAM, lw=4, alpha=a)
        hh = 232 * frac * k
        ctx.rectangle(gx - 56, 516 - hh, 112, hh); setc(ctx, WATER, a); ctx.fill()
        text_c(ctx, lab, gx, 262, 26, INK, True, 1.5, a)
        text_c(ctx, val, gx + (180 if gx < 540 else -190), 500 if gx < 540 else 320, 30, col, True, 1, a * k)

CARDS = {'arms': card_arms, 'compare': card_compare}
