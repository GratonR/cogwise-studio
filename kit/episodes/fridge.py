"""Cogwise episode: How does a fridge make cold?  (reference episode for the kit)

Pattern to copy for new episodes:
  * BEATS: one narration line per beat (~12-16 words), design durations ~4.5-6.5 s.
  * draw(ctx, t, E): ONE persistent illustrated object (here a fridge in cut-away), animated by a
    state(t) function that turns design-time windows into alphas (win(t, a, b)).
  * CARDS: 3-4 inset "zoom" cards explaining the key principle of a component.
  * Labels/tags numbered "1 · PART" in order, recap beat shows all of them.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="fridge",
    title="How does a fridge actually make cold? 🧊",
    description=("A fridge doesn't make cold: it moves heat out. Evaporator, compressor, condenser and "
                 "capillary tube explained in 60 seconds.\n\n#howthingswork #fridge #science #engineering #cogwise"),
    hashtags=["howthingswork", "fridge", "science", "engineering", "explained", "cogwise"],
)

BEATS = [
    dict(dur=5.5, title="HOW DOES A FRIDGE MAKE COLD?", caption="Ever wondered how your fridge keeps your food cold?"),
    dict(dur=5.5, title="IT MOVES HEAT", caption="Here's the secret: a fridge doesn't make cold. It moves heat out."),
    dict(dur=6.0, title=None, caption="The trick? When a liquid evaporates, it soaks up the heat around it.", card='evap'),
    dict(dur=5.5, title="THE REFRIGERANT", caption="So a special fluid, the refrigerant, flows in a closed loop of pipes."),
    dict(dur=6.5, title="1 · THE EVAPORATOR", caption="Inside, it evaporates at low pressure and pulls heat out of your food."),
    dict(dur=6.0, title=None, caption="The compressor sucks in that vapor and squeezes it. Squeezed gas gets hot!", card='comp'),
    dict(dur=6.0, title="3 · THE CONDENSER", caption="At the back, the hot gas gives its heat to the kitchen and turns liquid again."),
    dict(dur=5.0, title="WHY IS THE BACK WARM?", caption="That's why the back of your fridge feels warm: it's your food's heat!"),
    dict(dur=6.0, title=None, caption="Then a tiny tube drops the pressure. The liquid turns ice cold again.", card='capi'),
    dict(dur=6.0, title="AND AGAIN, AND AGAIN…", caption="And the loop restarts: heat in on the inside, heat out at the back."),
    dict(dur=6.5, title=None, caption="When it's cold enough, the thermostat stops the compressor. Silence!", card='thermo'),
    dict(dur=5.5, title="A FRIDGE = A HEAT PUMP", caption="Well done! You now know how a fridge really makes cold."),
]

SFX = [(5.9, 'whoosh'), (22.8, 'pop'), (29.4, 'pop'), (35.4, 'pop'), (41.2, 'sizzle'), (46.4, 'pop'),
       (61.6, 'click'), (65.0, 'pop'), (65.2, 'pop'), (65.4, 'pop'), (65.6, 'pop')]
HUM = [(19.5, 61.5), (64.5, 70.0)]

def draw_set(ctx):
    window(ctx)
    counter(ctx)

# ---------------------------------------------------------------- refrigerant loop
def build_path():
    pts = []; kinds = []
    def seg(p, k): pts.append(p); kinds.append(k)
    # evaporator serpentine (inside, back wall) start top
    seg((744, 466), 'capi')
    seg((700, 466), 'evap')
    y = 480; left = True
    seg((700, 480), 'evap')
    while y < 1000:
        seg((726 if left else 700, y), 'evap')
        y += 36
        seg((726 if left else 700, y), 'evap')
        left = not left
    # suction line down to compressor
    seg((754, y), 'suct'); seg((754, 1372), 'suct'); seg((720, 1372), 'suct')
    # through compressor (hidden)
    seg((690, 1410), 'hide'); seg((735, 1418), 'hide')
    # discharge
    seg((870, 1418), 'disc'); seg((870, 1252), 'disc')
    # condenser serpentine going up
    yy = 1252; right = True
    seg((845, yy), 'cond')
    while yy > 540:
        yy -= 33
        seg((845 if right else 785, yy), 'cond')
        right = not right
        seg((845 if right else 785, yy), 'cond')
    # capillary back to evaporator
    seg((744, yy), 'capi'); seg((744, 466), 'capi')
    return pts, kinds

PATH, KINDS = build_path()
CUM = [0.0]
for i in range(1, len(PATH)):
    CUM.append(CUM[-1] + math.dist(PATH[i-1], PATH[i]))
PLEN = CUM[-1]

def point_at(s):
    s %= PLEN
    lo, hi = 0, len(CUM) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if CUM[m] <= s: lo = m
        else: hi = m
    seglen = CUM[hi] - CUM[lo]
    u = (s - CUM[lo]) / seglen if seglen else 0
    p0, p1 = PATH[lo], PATH[hi]
    return (lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)), KINDS[hi], u

# arc-length ranges per kind, to make colour gradients
def kind_range(k):
    idx = [i for i in range(1, len(PATH)) if KINDS[i] == k]
    return CUM[idx[0]-1], CUM[idx[-1]]
R_COND = kind_range('cond')

def fluid_color(s):
    p, k, u = point_at(s)
    if k == 'evap': return COLD
    if k == 'suct': return VAPOR
    if k in ('disc', 'hide'): return RED
    if k == 'cond':
        f = (s % PLEN - R_COND[0]) / (R_COND[1] - R_COND[0])
        return lerpc(RED, ORANGE, clamp(f))
    if k == 'capi':
        ss = s % PLEN
        if ss < 50: return COLD
        f = (ss - (PLEN - 800)) / 800
        return lerpc(ORANGE, COLD, clamp(f))
    return COLD

def draw_pipes(ctx, reveal=1.0, alpha=1.0):
    if reveal <= 0: return
    target = PLEN * reveal
    # outline pass and inner pass
    for pass_ in (0, 1):
        for i in range(1, len(PATH)):
            if CUM[i-1] >= target: break
            k = KINDS[i]
            if k == 'hide': continue
            p0 = PATH[i-1]; p1 = PATH[i]
            if CUM[i] > target:
                u = (target - CUM[i-1]) / (CUM[i] - CUM[i-1])
                p1 = (lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u))
            thin = (k == 'capi')
            ctx.move_to(*p0); ctx.line_to(*p1)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            if pass_ == 0:
                ctx.set_line_width(7 if thin else 14); setc(ctx, SLATE, alpha)
            else:
                ctx.set_line_width(3 if thin else 8)
                base = {'evap': hexc('#bfe0dc'), 'suct': hexc('#bfe0dc'), 'disc': hexc('#f3c7b8'),
                        'cond': hexc('#f3c7b8'), 'capi': hexc('#efe4cd')}[k]
                setc(ctx, base, alpha)
            ctx.stroke()

def draw_particles(ctx, t_flow, alpha=1.0, n=70):
    if alpha <= 0: return
    for i in range(n):
        s = (i / n) * PLEN + t_flow
        p, k, _ = point_at(s)
        if k == 'hide': continue
        c = fluid_color(s)
        r = 3.2 if k == 'capi' else 5.5
        ctx.arc(p[0], p[1], r, 0, 2*math.pi)
        setc(ctx, c, alpha); ctx.fill()


# ---------------------------------------------------------------- foods
def draw_food(ctx, tint):
    # milk bottle on top shelf
    ctx.move_to(380, 640); ctx.line_to(380, 560); ctx.line_to(395, 535); ctx.line_to(395, 515)
    ctx.line_to(425, 515); ctx.line_to(425, 535); ctx.line_to(440, 560); ctx.line_to(440, 640); ctx.close_path()
    fill_stroke(ctx, WHITE, lw=4)
    rrect(ctx, 392, 505, 36, 14, 4); fill_stroke(ctx, TEAL, lw=3)
    rrect(ctx, 384, 580, 52, 34, 3); setc(ctx, TEAL_L); ctx.fill()
    # cheese wedge
    ctx.move_to(470, 640); ctx.line_to(560, 640); ctx.line_to(560, 590); ctx.close_path()
    fill_stroke(ctx, hexc('#f6d36b'), lw=4)
    for (cx, cy, r) in [(540, 620, 7), (552, 606, 5)]:
        ctx.arc(cx, cy, r, 0, 2*math.pi); setc(ctx, hexc('#e3b94a')); ctx.fill()
    # jar
    rrect(ctx, 590, 572, 60, 68, 8); fill_stroke(ctx, hexc('#e98f8f'), lw=4)
    rrect(ctx, 586, 560, 68, 16, 4); fill_stroke(ctx, SLATE2, lw=3)
    # apples on shelf 2
    for ax in (395, 455):
        ctx.arc(ax, 800, 27, 0, 2*math.pi); fill_stroke(ctx, hexc('#e66b5b'), lw=4)
        ctx.move_to(ax, 773); ctx.line_to(ax+4, 760); setc(ctx, SLATE); ctx.set_line_width(4); ctx.stroke()
    # cake
    ctx.move_to(520, 830); ctx.line_to(520, 770); ctx.line_to(640, 770); ctx.line_to(640, 830); ctx.close_path()
    fill_stroke(ctx, hexc('#f4e3c8'), lw=4)
    rrect(ctx, 516, 758, 128, 18, 8); fill_stroke(ctx, hexc('#f2a9b9'), lw=4)
    ctx.arc(580, 748, 9, 0, 2*math.pi); fill_stroke(ctx, RED, lw=3)
    # bowl on shelf 3
    ctx.move_to(380, 980); ctx.curve_to(390, 1035, 500, 1035, 510, 980); ctx.close_path()
    fill_stroke(ctx, TEAL_L, lw=4)
    for i in range(4):
        ctx.arc(405 + i*28, 975, 12, 0, 2*math.pi); setc(ctx, hexc('#8fc77a')); ctx.fill()
    rrect(ctx, 540, 960, 100, 70, 8); fill_stroke(ctx, hexc('#fbf5e8'), lw=4)
    ctx.move_to(552, 980); ctx.line_to(628, 980); setc(ctx, SLATE2); ctx.set_line_width(3); ctx.stroke()
    # crisper drawer
    rrect(ctx, 350, 1130, 330, 150, 10); fill_stroke(ctx, hexc('#eaf4f0', 0.7), lw=4)
    # carrot + lettuce
    ctx.move_to(390, 1150); ctx.line_to(480, 1170); ctx.line_to(390, 1190); ctx.close_path()
    fill_stroke(ctx, ORANGE, lw=4)
    for i in range(3):
        ctx.arc(530 + i*36, 1160 - (i % 2)*10, 30, 0, 2*math.pi); fill_stroke(ctx, hexc('#9ccf86'), lw=4)
    rrect(ctx, 470, 1222, 90, 22, 11); setc(ctx, SLATE2); ctx.fill()

# ---------------------------------------------------------------- fridge (foreground group)
def draw_fridge(ctx, t, st):
    cut = st['cut']          # 0 closed .. 1 cut-away
    # feet
    for fx in (330, 720):
        rrect(ctx, fx-14, 1486, 28, 14, 4); setc(ctx, SLATE); ctx.fill()
    # body
    rrect(ctx, 300, 430, 460, 1060, 22); fill_stroke(ctx, hexc('#fbf5e8'), lw=6)
    # interior
    cool = st['cool']
    inside = lerpc(hexc('#f6dcc4'), hexc('#cfe7e4'), cool)
    rrect(ctx, 340, 456, 394, 834, 10); setc(ctx, inside); ctx.fill()
    # cold shimmer
    if cool > 0.3:
        g = cairo.LinearGradient(734, 0, 340, 0)
        g.add_color_stop_rgba(0, *hexc('#5fb3ad')[:3], 0.35*cool)
        g.add_color_stop_rgba(1, *hexc('#5fb3ad')[:3], 0.0)
        rrect(ctx, 340, 456, 394, 834, 10); ctx.set_source(g); ctx.fill()
    # evaporator plate
    rrect(ctx, 690, 468, 46, 548, 6); setc(ctx, hexc('#b9dcd6')); ctx.fill()
    # shelves
    for sy in (640, 830, 1030):
        rrect(ctx, 340, sy, 345, 10, 3); setc(ctx, hexc('#b9dcd6')); ctx.fill_preserve()
        setc(ctx, SLATE2); ctx.set_line_width(3); ctx.stroke()
    draw_food(ctx, cool)
    # lamp
    rrect(ctx, 500, 456, 60, 14, 4); setc(ctx, hexc('#f2b134')); ctx.fill()
    # bottom compartment
    rrect(ctx, 340, 1312, 394, 170, 8); setc(ctx, hexc('#efe4cd')); ctx.fill()
    rrect(ctx, 600, 1312, 160, 170, 8); setc(ctx, hexc('#e2d3b5')); ctx.fill()
    # inner outline / insulation
    rrect(ctx, 340, 456, 394, 834, 10); setc(ctx, SLATE); ctx.set_line_width(4); ctx.stroke()
    # door slab
    rrect(ctx, 290, 436, 52, 1048, 12); fill_stroke(ctx, hexc('#fbf5e8'), lw=5)
    for sy in (600, 800, 1000):   # door bins
        rrect(ctx, 338, sy, 28, 46, 4); fill_stroke(ctx, hexc('#b9dcd6'), lw=3)
    rrect(ctx, 270, 690, 20, 220, 8); fill_stroke(ctx, hexc('#e2d3b5'), lw=4)
    # thermostat dial (inside top)
    th_on = st['comp_on']
    ctx.arc(390, 488, 16, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=3)
    ctx.move_to(390, 488); ctx.line_to(390 + 11*math.cos(-2.2), 488 + 11*math.sin(-2.2))
    setc(ctx, SLATE); ctx.set_line_width(3); ctx.stroke()

    # pipes & fluid
    draw_pipes(ctx, st['pipes'])
    draw_particles(ctx, st['flow'], st['particles'])

    # compressor
    vib = (math.sin(t * 70) * 2.2) if th_on > 0.5 else 0
    ctx.save(); ctx.translate(vib, 0)
    ctx.move_to(632, 1480); ctx.line_to(632, 1405); ctx.curve_to(632, 1350, 738, 1350, 738, 1405)
    ctx.line_to(738, 1480); ctx.close_path()
    hot = st['comp_hot']
    fill_stroke(ctx, lerpc(hexc('#3b3842'), hexc('#e4472f'), hot), lw=5)
    rrect(ctx, 620, 1472, 130, 14, 4); setc(ctx, SLATE); ctx.fill()
    ctx.arc(685, 1420, 10, 0, 2*math.pi); setc(ctx, hexc('#8d8792')); ctx.fill()
    ctx.restore()
    if th_on > 0.5 and st['comp_lines'] > 0:
        a = st['comp_lines']
        for i, (dx, dy) in enumerate([(-70, -40), (-78, 0), (80, -10)]):
            ph = (t*3 + i*0.3) % 1
            ctx.move_to(685 + dx, 1420 + dy - 12); ctx.line_to(685 + dx*(1.05+0.1*ph), 1420 + dy + 12)
            setc(ctx, SLATE2, a * (1 - ph)); ctx.set_line_width(4); ctx.stroke()

    # closed side panel (fades away for the cut-away)
    if cut < 1:
        rrect(ctx, 300, 430, 460, 1060, 22); setc(ctx, hexc('#fbf5e8'), 1 - cut); ctx.fill()
        rrect(ctx, 300, 430, 460, 1060, 22); setc(ctx, SLATE, 1 - cut); ctx.set_line_width(6); ctx.stroke()
        rrect(ctx, 290, 436, 52, 1048, 12); setc(ctx, hexc('#fbf5e8'), 1 - cut); ctx.fill_preserve()
        setc(ctx, SLATE, 1 - cut); ctx.set_line_width(5); ctx.stroke()
        rrect(ctx, 270, 690, 20, 220, 8); setc(ctx, hexc('#e2d3b5'), 1-cut); ctx.fill_preserve()
        setc(ctx, SLATE, 1-cut); ctx.set_line_width(4); ctx.stroke()
        # brand sticker / vents
        for i in range(4):
            rrect(ctx, 620, 1400 + i*18, 110, 6, 3); setc(ctx, SLATE2, 1-cut); ctx.fill()
        rrect(ctx, 470, 560, 120, 26, 13); setc(ctx, TEAL_L, 1-cut); ctx.fill()

    # heat flows
    a_in = st['heat_in']
    for i, yy in enumerate((570, 760, 950, 1180)):
        wavy_arrow(ctx, 450 + (i % 2)*30, yy, 680, yy - 20 + (i == 3)*(-110), t + i*0.4, ORANGE, a_in)
    a_out = st['heat_out']
    for i, yy in enumerate((640, 850, 1060)):
        wavy_arrow(ctx, 892, yy, 1030, yy - 60, t + i*0.5, RED, a_out, amp=11, lw=7)

    # highlights + labels
    for key, (cx, cy, rx, ry), (lx, ly), label, col in [
        ('h_evap', (713, 740, 52, 300), (560, 420), "EVAPORATOR", COLD),
        ('h_comp', (685, 1420, 85, 85), (700, 1290), "COMPRESSOR", RED),
        ('h_cond', (828, 900, 70, 380), (900, 470), "CONDENSER", ORANGE),
        ('h_capi', (744, 500, 30, 60), (850, 1320), "CAPILLARY", TEAL),
    ]:
        a = st.get(key, 0)
        if a <= 0: continue
        pulse = 0.5 + 0.5 * math.sin(t * 5)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry)
        ctx.arc(0, 0, 1, 0, 2*math.pi); ctx.restore()
        setc(ctx, col, a * (0.10 + 0.08*pulse)); ctx.fill_preserve()
        ctx.set_dash([14, 10]); setc(ctx, col, a); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    for key, pos, label, col in [
        ('l_evap', (560, 1100 - 690), "1 · EVAPORATOR", COLD),
        ('l_comp', (530, 1585 - 160), "2 · COMPRESSOR", RED),
        ('l_cond', (900, 1300), "3 · CONDENSER", ORANGE),
        ('l_capi', (880, 410), "4 · CAPILLARY", TEAL),
    ]:
        tag(ctx, label, pos[0], pos[1], col, st.get(key, 0))
    if st.get('warm', 0) > 0:
        a = st['warm']
        g = cairo.RadialGradient(830, 900, 20, 830, 900, 260)
        g.add_color_stop_rgba(0, *ORANGE[:3], 0.35*a); g.add_color_stop_rgba(1, *ORANGE[:3], 0)
        ctx.set_source(g); ctx.rectangle(560, 600, 520, 640); ctx.fill()
        tag(ctx, "WARM!", 960, 1180, RED, a, 30)
    if st.get('hum', 0) > 0:
        tag(ctx, "Mmmmm…", 880, 1380, SLATE2, st['hum'], 26)
    if st.get('snow', 0) > 0:
        a = st['snow']
        for i in range(10):
            x = 380 + (i * 37) % 300; y = 480 + ((t*40 + i*83) % 760)
            ctx.arc(x, y, 4, 0, 2*math.pi); setc(ctx, WHITE, a*0.9); ctx.fill()

# ---------------------------------------------------------------- inset cards

def card_evap(ctx, t, lt, a):
    card_frame(ctx, "THE TRICK: EVAPORATION", a, "EVAPORATING LIQUID = ABSORBS HEAT", TEAL)
    # plate + drop shrinking
    shrink = 1 - 0.45 * ease(lt / 5.0)
    rrect(ctx, 400, 470, 280, 18, 9); setc(ctx, hexc('#e2d3b5'), a); ctx.fill()
    ctx.save(); ctx.translate(540, 470); ctx.scale(shrink, shrink)
    ctx.move_to(0, -150); ctx.curve_to(40, -80, 80, -40, 80, -10)
    ctx.curve_to(80, 30, -80, 30, -80, -10); ctx.curve_to(-80, -40, -40, -80, 0, -150)
    ctx.close_path(); fill_stroke(ctx, COLD, lw=5, alpha=a)
    ctx.arc(-30, -30, 12, 0, 2*math.pi); setc(ctx, WHITE, 0.7*a); ctx.fill()
    ctx.restore()
    # vapor wisps
    for i in range(3):
        ph = (lt*0.6 + i/3) % 1
        x = 500 + i*40; y = 400 - ph*130
        ctx.move_to(x, y + 40); ctx.curve_to(x - 18, y + 20, x + 18, y, x, y - 20)
        setc(ctx, VAPOR, a * (1-ph) * 0.9); ctx.set_line_width(6); ctx.stroke()
    # heat arrows into the drop
    wavy_arrow(ctx, 170, 330, 430, 410, t, ORANGE, a, lw=6)
    wavy_arrow(ctx, 850, 330, 650, 410, t, ORANGE, a, lw=6)
    # thermometer
    thermo(ctx, 925, 470, 1 - 0.5*ease(lt/5), a)

def thermo(ctx, x, y, level, a, h=170):
    rrect(ctx, x - 14, y - h, 28, h, 14); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    ctx.arc(x, y + 6, 22, 0, 2*math.pi); fill_stroke(ctx, COLD, lw=4, alpha=a)
    hh = (h - 20) * level
    rrect(ctx, x - 6, y - hh, 12, hh + 6, 6); setc(ctx, COLD, a); ctx.fill()

def card_comp(ctx, t, lt, a):
    card_frame(ctx, "2 · THE COMPRESSOR", a, "SQUEEZED GAS = HOT GAS", RED)
    p = 0.5 - 0.5*math.cos(lt * 2.2)          # piston phase 0..1
    cx, top, bot = 540, 270, 520
    ctx.rectangle(cx - 120, top, 240, bot - top); fill_stroke(ctx, hexc('#fbf5e8'), lw=5, alpha=a)
    py = lerp(top + 20, top + 150, p)
    # gas particles inside the chamber
    hotness = p
    col = lerpc(VAPOR, RED, hotness)
    import random
    rnd = random.Random(3)
    for i in range(24):
        fx = rnd.random(); fy = rnd.random()
        jx = math.sin(t*9 + i) * 4; jy = math.cos(t*11 + i*2) * 4
        x = cx - 100 + fx*200 + jx; y = py + 30 + fy*(bot - py - 45) + jy
        ctx.arc(x, y, 7, 0, 2*math.pi); setc(ctx, col, a); ctx.fill()
    rrect(ctx, cx - 116, py, 232, 26, 4); fill_stroke(ctx, SLATE2, lw=4, alpha=a)
    rrect(ctx, cx - 12, top - 40, 24, py - top + 40, 4); setc(ctx, SLATE2, a); ctx.fill()
    straight_arrow(ctx, cx + 190, py - 20, cx + 190, py + 60, SLATE, a * (1 if math.sin(lt*2.2) > 0 else 0.25))
    thermo_hot(ctx, 820, 500, 0.25 + 0.7*hotness, a)
    tag(ctx, "LOW PRESSURE", 260, 330, COLD, a * (1 - hotness), 24)
    tag(ctx, "HIGH PRESSURE", 260, 470, RED, a * hotness, 24)

def thermo_hot(ctx, x, y, level, a, h=200):
    rrect(ctx, x - 14, y - h, 28, h, 14); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    ctx.arc(x, y + 6, 22, 0, 2*math.pi); fill_stroke(ctx, RED, lw=4, alpha=a)
    hh = (h - 20) * level
    rrect(ctx, x - 6, y - hh, 12, hh + 6, 6); setc(ctx, RED, a); ctx.fill()

def card_capi(ctx, t, lt, a):
    card_frame(ctx, "4 · THE CAPILLARY TUBE", a, "PRESSURE DROPS = ICE COLD", COLD)
    # wide pipe -> narrow -> wide
    y = 400
    def shape():
        ctx.move_to(130, y - 50); ctx.line_to(420, y - 50); ctx.line_to(470, y - 9)
        ctx.line_to(640, y - 9); ctx.line_to(690, y - 70); ctx.line_to(950, y - 70)
        ctx.line_to(950, y + 70); ctx.line_to(690, y + 70); ctx.line_to(640, y + 9)
        ctx.line_to(470, y + 9); ctx.line_to(420, y + 50); ctx.line_to(130, y + 50); ctx.close_path()
    shape(); fill_stroke(ctx, hexc('#fbf5e8'), lw=5, alpha=a)
    ctx.save(); shape(); ctx.clip()
    import random
    rnd = random.Random(7)
    for i in range(40):
        u = (rnd.random() + lt * 0.18) % 1
        x = 130 + u * 820
        if x < 440:
            yy = y + (rnd.random() - 0.5) * 80; c = ORANGE; r = 8
        elif x < 660:
            yy = y + (rnd.random() - 0.5) * 10; c = lerpc(ORANGE, COLD, (x-440)/220); r = 5
        else:
            yy = y + (rnd.random() - 0.5) * 120; c = COLD; r = 6
        ctx.arc(x, yy, r, 0, 2*math.pi); setc(ctx, c, a); ctx.fill()
    ctx.restore()
    shape(); setc(ctx, SLATE, a); ctx.set_line_width(5); ctx.stroke()
    tag(ctx, "WARM LIQUID", 270, 290, ORANGE, a, 24)
    tag(ctx, "ICE-COLD MIST", 820, 290, COLD, a, 24)
    for i in range(3):   # frost sparkle
        ph = (lt*1.5 + i*0.33) % 1
        x, yy = 760 + i*60, 470 + math.sin(i)*10
        setc(ctx, COLD, a*(1-ph)); ctx.set_line_width(4)
        for ang in range(3):
            an = ang * math.pi/3
            ctx.move_to(x - 12*math.cos(an), yy - 12*math.sin(an)); ctx.line_to(x + 12*math.cos(an), yy + 12*math.sin(an))
        ctx.stroke()

def card_thermo(ctx, t, lt, a):
    card_frame(ctx, "THE THERMOSTAT", a, None)
    k = ease((lt - 0.5) / 3.0)
    level = lerp(0.75, 0.25, k)
    # big thermometer
    x, y, h = 300, 500, 250
    rrect(ctx, x - 20, y - h, 40, h, 20); fill_stroke(ctx, WHITE, lw=5, alpha=a)
    ctx.arc(x, y + 10, 32, 0, 2*math.pi); fill_stroke(ctx, COLD, lw=5, alpha=a)
    hh = (h - 30) * level
    rrect(ctx, x - 9, y - hh, 18, hh + 10, 9); setc(ctx, COLD, a); ctx.fill()
    # target mark
    ty = y - (h - 30) * 0.25
    ctx.move_to(x + 26, ty); ctx.line_to(x + 60, ty); setc(ctx, TEAL, a); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "4 °C", x + 110, ty + 12, 34, TEAL, True, 0, a)
    temp = lerp(12, 4, k)
    text_c(ctx, f"{temp:.0f} °C", 180, 390, 38, SLATE, True, 0, a)
    # switch
    on = lt < 3.6
    sx, sy = 660, 380
    rrect(ctx, sx - 110, sy - 55, 220, 110, 55)
    fill_stroke(ctx, hexc('#7fb7a4') if on else hexc('#e2d3b5'), lw=5, alpha=a)
    kx = sx + 55 if on else sx - 55
    ctx.arc(kx, sy, 42, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    text_c(ctx, "COMPRESSOR", sx, 490, 30, SLATE, True, 1.5, a)
    text_c(ctx, "ON" if on else "OFF", sx, 545, 38, hexc('#4c9d6b') if on else RED, True, 2, a)

CARDS = {'evap': card_evap, 'comp': card_comp, 'capi': card_capi, 'thermo': card_thermo}


# ---------------------------------------------------------------- state machine
def state(t):
    st = dict(cut=0, cool=0, pipes=0, particles=0, flow=0, comp_on=0, comp_hot=0, comp_lines=0,
              heat_in=0, heat_out=0)
    st['cut'] = ease((t - 6.0) / 1.2)
    st['pipes'] = 1.0 if t >= 22 else ease((t - 17.4) / 4.0) if t > 17.4 else 0.0
    # pipes faintly visible before full intro (none)
    st['particles'] = ease((t - 19.5) / 1.5) * (1 - 0.0)
    on = not (61.5 <= t < 64.5)
    st['comp_on'] = 1 if (t >= 19.5 and on) else 0
    # flow position integrates speed (stop during thermostat pause)
    def flow_dist(tt):
        speed = 170
        d = max(0, tt - 19.5) * speed
        # pause between 61.5 and 64.5
        if tt > 61.5: d -= (min(tt, 64.5) - 61.5) * speed
        # faster during the loop beat
        if tt > 52: d += (min(tt, 58) - 52) * 160
        return d
    st['flow'] = flow_dist(t)
    st['comp_lines'] = win(t, 29, 41) + win(t, 52, 61.5) * 0.7
    st['comp_lines'] = clamp(st['comp_lines'])
    st['comp_hot'] = 0.6 * win(t, 29.5, 35)
    st['heat_in'] = max(win(t, 7.5, 11), win(t, 23.5, 29), win(t, 52.5, 61.5), win(t, 65, 70) * 0.8)
    st['heat_out'] = max(win(t, 8.5, 11), win(t, 36, 46), win(t, 52.5, 61.5), win(t, 65, 70) * 0.8)
    st['cool'] = clamp(0.25 + 0.75 * ease((t - 23) / 6)) if t > 6 else 0.25
    st['h_evap'] = win(t, 22.6, 29)
    st['h_comp'] = win(t, 29.2, 35)
    st['h_cond'] = win(t, 35.2, 41)
    st['h_capi'] = win(t, 46.2, 52)
    st['l_evap'] = win(t, 22.8, 29) + win(t, 65, 70)
    st['l_comp'] = win(t, 29.4, 35) + win(t, 65.2, 70)
    st['l_cond'] = win(t, 35.4, 41) + win(t, 65.4, 70)
    st['l_capi'] = win(t, 46.4, 52) + win(t, 65.6, 70)
    st['warm'] = win(t, 41.2, 46)
    st['hum'] = win(t, 59, 61.4)
    st['snow'] = win(t, 25, 29) * 0.8
    return st


CARDS = {'evap': card_evap, 'comp': card_comp, 'capi': card_capi, 'thermo': card_thermo}

def draw(ctx, t, E):
    draw_fridge(ctx, t, state(t))
