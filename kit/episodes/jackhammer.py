"""Cogwise episode: How does a jackhammer hit so fast?  (pneumatic breaker)"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="jackhammer",
    title="How does a jackhammer hit 18 times a second? 🔨",
    description=("No motor inside: just squeezed air, a valve and a flying piston. The jackhammer, explained.\n\n"
                 "#Shorts #howthingswork #jackhammer #construction #engineering #cogwise"),
    hashtags=["Shorts", "howthingswork", "jackhammer", "construction", "engineering", "science", "cogwise"],
    sources=[
        "https://dealers.doosanportablepower.com/emea/documents/Marketing/03.Product/06_Construction%20Tools/Pneumatic%20tools%20encyclopedia%20DII%20Rev.201303.pptx.pdf",
        "https://engineerfix.com/how-a-pneumatic-jack-hammer-works-and-when-to-use-one/",
        "https://atlascopco.com/en-us/construction-equipment/products/tools-us/breakers/heavy-breakers/pneumatic-tex-40pe",
        "https://www.firgelliauto.com/blogs/mechanisms/pneumatic-hammer",
    ],
)

BEATS = [
    dict(dur=5.5, title="HOW DOES IT HIT SO FAST?", caption="How does a jackhammer hit concrete so fast, with no motor inside?"),
    dict(dur=5.0, title="THE SECRET: AIR", caption="The secret: squeezed air, and a heavy piston bouncing inside a tube."),
    dict(dur=5.0, title=None, caption="Air at six bar pushes about six kilos on every square centimeter.", card='pressure'),
    dict(dur=4.5, title="1 · AIR HOSE", caption="A compressor feeds the air in through the hose and trigger."),
    dict(dur=4.5, title="2 · THE VALVE", caption="A small valve sends the air to the top of the cylinder first."),
    dict(dur=4.5, title="3 · THE PISTON", caption="The air drives the steel piston down, faster and faster."),
    dict(dur=5.0, title="4 · THE CHISEL", caption="It slams into the chisel, and the chisel smashes the concrete."),
    dict(dur=5.5, title=None, caption="The piston never touches concrete: the blow travels through the steel as a shock wave.", card='shock'),
    dict(dur=5.0, title="5 · EXHAUST + VALVE FLIP", caption="At the bottom, exhaust holes open and the valve flips the air below."),
    dict(dur=5.0, title="BOUNCE BACK", caption="Now air pushes the piston back up, and it all starts again."),
    dict(dur=4.5, title=None, caption="That's about eighteen blows a second, over a thousand per minute!", card='rate'),
    dict(dur=5.0, title=None, caption="Surprise: the expanding exhaust air gets so cold it can ice up!", card='ice'),
    dict(dur=5.0, title="PROTECT YOUR EARS", caption="It's brutally loud, about a hundred decibels up close: wear ear protection."),
    dict(dur=5.0, title="AIR + PISTON + CHISEL", caption="So: the valve flips the air, the piston hammers, the chisel breaks."),
    dict(dur=5.5, title="REPAIR TECH TIP", caption="Tech tip: oil the air inlet with pneumatic tool oil, never diesel."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
CX = 560
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); STEEL_L = hexc('#e3e7ea')
BODY = hexc('#e2b33a'); BODY_D = hexc('#b8862a')
AIR = hexc('#8fcfc8'); AIR_P = hexc('#3fa6a0')
CONC = hexc('#bdb6a8'); CONC_D = hexc('#958d7e')
GREEN = hexc('#4c9d6b'); ICE = hexc('#cfeef5')

BORE_X0, BORE_X1 = 500, 620          # cylinder bore
BORE_Y0, BORE_Y1 = 500, 1030
PIST_H = 150
SHANK_Y = 1030                       # top of chisel shank
TIP_Y = 1420                         # chisel tip (in concrete)
SLAB_Y = 1360
EXH_Y = 820                          # exhaust ports
HOSE = [(800, 372), (900, 372), (960, 420), (975, 600), (975, 1250), (1040, 1300)]
FAST = 4.2                           # visual blows per second (real tool ~18/s)

def fast_mode(t):
    return (t < B(3)) or (B(10) <= t < B(14))

def cycle(t):
    """returns piston pos p (0 top .. 1 bottom), top pressure, bottom pressure, valve (0 top-feed, 1 bottom-feed), impact flash"""
    if fast_mode(t):
        ph = (t * FAST) % 1.0
        if ph < 0.42:
            p = (ph / 0.42) ** 2; top, bot, val = 1.0, 0.15, 0.0
        else:
            p = 1 - ease((ph - 0.42) / 0.58); top, bot, val = 0.15, 1.0, 1.0
        imp = max(0.0, 1 - abs(ph - 0.42) / 0.12)
        return p, top, bot, val, imp
    if t < B(4):                       # trigger: air arrives, piston at rest at top
        return 0.0, 0.25 * ease((t - B(3)) / 2), 0.1, 0.0, 0.0
    if t < B(5):                       # valve feeds the top
        return 0.0, 0.25 + 0.75 * ease((t - B(4) - 0.6) / 1.6), 0.1, 0.0, 0.0
    if t < B(6):                       # piston accelerates down
        u = clamp((t - B(5) - 0.4) / 3.2)
        return min(u * u, 0.985), 1.0, 0.1, 0.0, 0.0
    if t < B(8):                       # impact + hold (incl. shock card)
        imp = max(0.0, 1 - (t - B(6)) / 0.5)
        return 1.0, 1.0, 0.1, 0.0, imp
    if t < B(9):                       # exhaust + valve flip
        e = ease((t - B(8) - 0.5) / 1.4)
        v = ease((t - B(8) - 2.0) / 0.9)
        return 1.0, 1.0 - 0.9 * e, 0.1 + 0.9 * ease((t - B(8) - 2.6) / 1.2), v, 0.0
    if t < B(10):                      # piston pushed back up
        u = ease((t - B(9) - 0.3) / 2.8)
        return 1.0 - u, 0.1, 1.0, 1.0, 0.0
    return 0.0, 0.1, 0.1, 0.0, 0.0     # tip beat: tool resting

def chisel_dy(t, imp):
    return 10 * imp

def path_point(pts, u):
    segs = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]
    L = sum(segs) * (u % 1.0)
    for i, s in enumerate(segs):
        if L <= s:
            f = L / s
            return lerp(pts[i][0], pts[i+1][0], f), lerp(pts[i][1], pts[i+1][1], f)
        L -= s
    return pts[-1]

# ---------------------------------------------------------------- drawing
def draw_slab(ctx, t, st):
    rrect(ctx, 150, SLAB_Y, 820, 130, 10); fill_stroke(ctx, CONC, lw=5)
    rnd = random.Random(7)
    for i in range(26):                                   # aggregate speckles
        x = 175 + rnd.random() * 770; y = SLAB_Y + 18 + rnd.random() * 95
        ctx.arc(x, y, 4 + rnd.random() * 7, 0, 2*math.pi); setc(ctx, CONC_D, 0.7); ctx.fill()
    # crater + cracks grow with work done
    c = st['crack']
    if c > 0:
        ctx.move_to(CX - 40 * c, SLAB_Y); ctx.line_to(CX, SLAB_Y + 70 * c); ctx.line_to(CX + 40 * c, SLAB_Y)
        ctx.close_path(); setc(ctx, CONC_D); ctx.fill()
        for (dx, dy, ang) in ((-1, 1, 2.5), (1, 1, 0.6), (-1, 0.5, 3.0), (1, 0.6, 0.15)):
            x, y = CX + dx * 20, SLAB_Y + 40 * c * dy
            ctx.move_to(x, y)
            L = 160 * c
            for k in range(1, 5):
                x += math.cos(ang) * L / 4 + (6 if k % 2 else -6); y += math.sin(ang) * L / 4 + (8 if k % 2 else -4)
                ctx.line_to(x, y)
            setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()

def draw_debris(ctx, t, st):
    a = st['imp']
    if a <= 0.02: return
    rnd = random.Random(int(t * FAST) if fast_mode(t) else 99)
    age = 1 - a
    for i in range(9):
        ang = math.pi + rnd.random() * math.pi
        sp = 60 + rnd.random() * 120
        x = CX + math.cos(ang) * sp * (0.3 + age)
        y = SLAB_Y - 5 + math.sin(ang) * sp * (0.3 + age) * 0.8 + 60 * age * age
        ctx.rectangle(x - 6, y - 6, 12, 10); setc(ctx, CONC_D, a); ctx.fill()

def draw_chisel(ctx, t, st):
    dy = st['cdy']
    # blade
    ctx.move_to(CX - 26, SHANK_Y + 90 + dy); ctx.line_to(CX + 26, SHANK_Y + 90 + dy)
    ctx.line_to(CX + 22, TIP_Y - 60 + dy); ctx.line_to(CX, TIP_Y + dy); ctx.line_to(CX - 22, TIP_Y - 60 + dy)
    ctx.close_path(); fill_stroke(ctx, STEEL_D, lw=5)
    # collar + shank
    rrect(ctx, CX - 44, SHANK_Y + 70 + dy, 88, 26, 6); fill_stroke(ctx, STEEL, lw=4)
    rrect(ctx, CX - 24, SHANK_Y + dy, 48, 80, 4); fill_stroke(ctx, STEEL_L, lw=4)

def draw_body(ctx, t, st):
    # front head / retainer
    rrect(ctx, 470, 1000, 180, 130, 18); fill_stroke(ctx, BODY_D, lw=6)
    rrect(ctx, CX - 30, 1000, 60, 130, 4); setc(ctx, WALL2); ctx.fill()
    # cylinder casing
    rrect(ctx, 450, 430, 220, 610, 22); fill_stroke(ctx, BODY, lw=6)
    # cut-away bore
    ctx.rectangle(BORE_X0, BORE_Y0, BORE_X1 - BORE_X0, BORE_Y1 - BORE_Y0); fill_stroke(ctx, WALL1, lw=4)
    p = st['p']
    ptop = BORE_Y0 + p * (BORE_Y1 - PIST_H - BORE_Y0)
    # air in top / bottom chambers
    if ptop > BORE_Y0 + 3:
        ctx.rectangle(BORE_X0 + 2, BORE_Y0 + 2, BORE_X1 - BORE_X0 - 4, ptop - BORE_Y0 - 2)
        setc(ctx, lerpc(AIR, AIR_P, st['top']), 0.25 + 0.7 * st['top']); ctx.fill()
    pb = ptop + PIST_H
    if pb < BORE_Y1 - 3:
        ctx.rectangle(BORE_X0 + 2, pb, BORE_X1 - BORE_X0 - 4, BORE_Y1 - pb - 2)
        setc(ctx, lerpc(AIR, AIR_P, st['bot']), 0.25 + 0.7 * st['bot']); ctx.fill()
    # side channel to the bottom chamber (left wall)
    rrect(ctx, 466, 470, 18, 560, 6); setc(ctx, WALL1); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    if st['bot'] > 0.2:
        rrect(ctx, 468, 472, 14, 556, 5); setc(ctx, AIR_P, st['bot'] * 0.8); ctx.fill()
    ctx.rectangle(466, 1012, 36, 14); setc(ctx, lerpc(AIR, AIR_P, st['bot']), 0.4 + 0.5 * st['bot']); ctx.fill()
    # exhaust ports (right wall)
    for yy in (EXH_Y - 20, EXH_Y + 20):
        ctx.rectangle(BORE_X1, yy - 7, 50, 14); setc(ctx, WALL1); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    # piston
    rrect(ctx, BORE_X0 + 4, ptop, BORE_X1 - BORE_X0 - 8, PIST_H, 10); fill_stroke(ctx, STEEL, lw=5)
    for k in (1, 2):
        ctx.move_to(BORE_X0 + 4, ptop + k * 22); ctx.line_to(BORE_X1 - 4, ptop + k * 22)
        setc(ctx, STEEL_D); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(BORE_X0 + 30, ptop + PIST_H - 30); ctx.line_to(BORE_X1 - 30, ptop + PIST_H - 30)
    setc(ctx, STEEL_L); ctx.set_line_width(6); ctx.stroke()
    # valve chest on top with sliding valve
    rrect(ctx, 440, 380, 240, 70, 14); fill_stroke(ctx, BODY_D, lw=6)
    rrect(ctx, 470, 395, 180, 40, 8); fill_stroke(ctx, WALL1, lw=3)
    vx = lerp(560, 490, st['val'])
    rrect(ctx, vx, 398, 70, 34, 6); fill_stroke(ctx, RED, lw=3)
    # feed arrows from valve
    if st['feed_top'] > 0:
        straight_arrow(ctx, 600, 440, 600, 510, AIR_P, st['feed_top'], lw=6, head=12)
    if st['feed_bot'] > 0:
        straight_arrow(ctx, 475, 445, 475, 520, AIR_P, st['feed_bot'], lw=6, head=12)

def draw_handle(ctx, t, st):
    # D-handles + T bar
    rrect(ctx, 300, 345, 520, 50, 22); fill_stroke(ctx, INK2, lw=5)
    for x in (300, 720):
        rrect(ctx, x, 335, 100, 70, 26); fill_stroke(ctx, INK, lw=4)
    rrect(ctx, 520, 330, 80, 70, 8); fill_stroke(ctx, BODY_D, lw=5)
    # trigger lever on right grip
    a = st['trig']
    ctx.save(); ctx.translate(735, 405); ctx.rotate(-0.35 * a)
    rrect(ctx, 0, -6, 80, 16, 6); fill_stroke(ctx, RED, lw=3)
    ctx.restore()

def draw_hose(ctx, t, st):
    pts = HOSE
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    setc(ctx, INK); ctx.set_line_width(30); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    setc(ctx, lerpc(hexc('#3a3640'), AIR_P, st['air'] * 0.6)); ctx.set_line_width(20); ctx.stroke()
    if st['flow'] > 0:
        for k in range(10):
            x, y = path_point(pts[::-1], k / 10 + t * 0.4)
            ctx.arc(x, y, 6, 0, 2*math.pi); setc(ctx, WHITE, st['flow']); ctx.fill()

def draw_exhaust(ctx, t, st):
    e = st['exh']
    if e <= 0: return
    for k, yy in enumerate((EXH_Y - 20, EXH_Y + 20)):
        for j in range(3):
            u = ((t * 1.5 + j / 3 + k * 0.17) % 1.0)
            x = BORE_X1 + 60 + u * 150; y = yy + (k * 2 - 1) * u * 50
            ctx.arc(x, y, 10 + 18 * u, 0, 2*math.pi); setc(ctx, AIR, e * (1 - u) * 0.9); ctx.fill()

def draw_sound(ctx, t, st):
    s = st['loud']
    if s <= 0: return
    for k in range(3):
        r = 60 + ((t * 120 + k * 60) % 180)
        al = s * (1 - (r - 60) / 180)
        for sgn in (-1, 1):
            ctx.arc(CX + sgn * 250, 700, r, -0.6 if sgn > 0 else math.pi - 0.6, 0.6 if sgn > 0 else math.pi + 0.6)
            ctx.new_sub_path()
        ctx.new_path()
        ctx.arc(CX + 250, 700, r, -0.6, 0.6); setc(ctx, RED, al); ctx.set_line_width(5); ctx.stroke()
        ctx.arc_negative(CX - 250, 700, r, math.pi + 0.6, math.pi - 0.6); setc(ctx, RED, al); ctx.stroke()

def draw_oil(ctx, t, st):
    a = st['tip']
    if a <= 0: return
    # oil can pouring at the hose inlet
    ox, oy = 880, 250
    ctx.save(); ctx.translate(ox, oy); ctx.rotate(0.5)
    rrect(ctx, -50, -40, 100, 80, 14); fill_stroke(ctx, RED, lw=4, alpha=a)
    ctx.move_to(40, -10); ctx.line_to(110, -40); ctx.line_to(112, -30); ctx.line_to(45, 10); ctx.close_path()
    fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    ctx.restore()
    for i in range(3):
        u = (t * 1.2 + i / 3) % 1.0
        x, y = 905, 330 + u * 30
        ctx.move_to(x, y - 10); ctx.curve_to(x + 8, y, x + 8, y + 9, x, y + 9)
        ctx.curve_to(x - 8, y + 9, x - 8, y, x, y - 10); setc(ctx, MUSTARD, a * (1 - u)); ctx.fill()

def draw_all(ctx, t, st):
    jx = st['shake'] * (3 * math.sin(t * 90))
    draw_slab(ctx, t, st)
    ctx.save(); ctx.translate(jx, 0)
    draw_hose(ctx, t, st)
    draw_chisel(ctx, t, st)
    draw_body(ctx, t, st)
    draw_handle(ctx, t, st)
    ctx.restore()
    draw_exhaust(ctx, t, st)
    draw_debris(ctx, t, st)
    draw_sound(ctx, t, st)
    draw_oil(ctx, t, st)
    # highlights
    highlight(ctx, 975, 900, 70, 300, TEAL, st['h_hose'], t)
    highlight(ctx, 560, 415, 150, 60, RED, st['h_val'], t)
    highlight(ctx, 560, st['pcy'], 110, 110, ORANGE, st['h_pis'], t)
    highlight(ctx, 560, 1230, 90, 200, MUSTARD, st['h_chi'], t)
    highlight(ctx, 690, EXH_Y, 110, 80, TEAL, st['h_exh'], t)
    # tags
    tag(ctx, "1 · AIR HOSE", 860, 1440, TEAL, st['l_hose'])
    tag(ctx, "2 · VALVE", 300, 470, RED, st['l_val'])
    tag(ctx, "3 · PISTON", 300, 700, ORANGE, st['l_pis'])
    tag(ctx, "4 · CHISEL", 320, 1230, BODY_D, st['l_chi'])
    tag(ctx, "5 · EXHAUST", 850, 700, TEAL, st['l_exh'])
    if st['bang'] > 0: tag(ctx, "BANG!", 330, 1040, RED, st['bang'], 30)
    if st['up'] > 0: tag(ctx, "AIR BELOW = PISTON UP", 560, 1560, AIR_P, st['up'], 26)
    if st['down'] > 0: tag(ctx, "AIR ABOVE = PISTON DOWN", 560, 1560, AIR_P, st['down'], 26)
    if st['ears'] > 0: tag(ctx, "≈ 100 dB · EAR PROTECTION", 560, 1560, RED, st['ears'], 26)
    if st['recap'] > 0: tag(ctx, "AIR · PISTON · CHISEL", 560, 1560, INK, st['recap'], 28)
    if st['tip'] > 0:
        tag(ctx, "PNEUMATIC TOOL OIL", 300, 290, GREEN, st['tip'], 24)
        tag(ctx, "NEVER DIESEL", 560, 1560, RED, st['tip'], 26)

# ---------------------------------------------------------------- state machine
def state(t):
    st = {}
    p, top, bot, val, imp = cycle(t)
    st.update(p=p, top=top, bot=bot, val=val, imp=imp)
    st['pcy'] = BORE_Y0 + p * (BORE_Y1 - PIST_H - BORE_Y0) + PIST_H / 2
    st['cdy'] = chisel_dy(t, imp)
    run = 1.0 if fast_mode(t) else 0.0
    st['shake'] = run
    st['trig'] = 1.0 if t < B(14) else 1 - ease((t - B(14)) / 0.6)
    st['air'] = 1.0 if t < B(14) else 0.3
    st['flow'] = max(bw(t, 3) , 0.7 * run * (1 if t < B(3) else 0), bw(t, 1, 2) * 0.9)
    st['feed_top'] = bw(t, 4, 6) if not fast_mode(t) else 0
    st['feed_bot'] = win(t, B(8) + 2.6, B(10)) if not fast_mode(t) else 0
    st['exh'] = win(t, B(8) + 0.5, B(9) + 0.5) + run * 0.6
    st['crack'] = clamp(0.3 + 0.7 * ease((t - B(6)) / 0.6) + 0.0) if t >= B(6) else 0.3 * ease(t / 3)
    st['loud'] = bw(t, 12)
    st['h_hose'] = bw(t, 3); st['h_val'] = bw(t, 4); st['h_pis'] = bw(t, 5)
    st['h_chi'] = bw(t, 6); st['h_exh'] = bw(t, 8)
    recap = bw(t, 13, 14)
    st['l_hose'] = bw(t, 3) + recap
    st['l_val'] = bw(t, 4) + bw(t, 8) + recap
    st['l_pis'] = bw(t, 5) + bw(t, 9) + recap
    st['l_chi'] = bw(t, 6) + recap
    st['l_exh'] = bw(t, 8) + recap
    st['bang'] = win(t, B(6) + 0.1, B(6) + 1.6)
    st['down'] = win(t, B(5) + 0.3, B(6))
    st['up'] = bw(t, 9)
    st['ears'] = bw(t, 12)
    st['recap'] = recap
    st['tip'] = bw(t, 14, 15)
    return st

SFX = [(0.25 * k, 'click') for k in range(1, 20)] + [
       (B(1) + 0.4, 'whoosh'), (B(3) + 0.2, 'pop'), (B(3) + 0.4, 'click'), (B(4) + 0.2, 'pop'),
       (B(5) + 0.2, 'pop'), (B(6) + 0.05, 'click'), (B(6) + 0.2, 'pop'), (B(8) + 0.2, 'pop'),
       (B(8) + 0.6, 'sizzle'), (B(9) + 0.2, 'pop'), (B(13) + 0.2, 'ding'), (B(14) + 0.2, 'pop')]
HUM = [(0.0, B(3)), (B(10), B(14))]

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

# ---------------------------------------------------------------- cards
def card_pressure(ctx, t, lt, a):
    card_frame(ctx, "AIR PRESSURE", a, "6 BAR ≈ 6 KG ON EVERY CM²", TEAL)
    p = ease((lt - 0.5) / 0.8)
    # piston face seen from the side, with a grid of square centimetres
    rrect(ctx, 200, 440, 680, 70, 10); fill_stroke(ctx, STEEL, lw=5, alpha=a)
    for i in range(6):
        x = 250 + i * 110
        ctx.rectangle(x - 34, 410, 68, 28); fill_stroke(ctx, AIR, lw=3, alpha=a)
        straight_arrow(ctx, x, 262, x, 404 - 10 * (1 - p), AIR_P, a * (0.3 + 0.7 * p), lw=6, head=12)
        text_c(ctx, "6 kg", x, 300, 24, INK, True, 0, a * p)
    text_c(ctx, "1 cm²", 250, 432, 16, INK, True, 0, a)

def card_shock(ctx, t, lt, a):
    card_frame(ctx, "SHOCK WAVE", a, "THE STEEL CARRIES THE BLOW", RED)
    hit = 0.8
    px = lerp(130, 250, ease(lt / hit)) if lt < hit else 250
    rrect(ctx, px - 120, 345, 120, 90, 10); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    rrect(ctx, 255, 365, 520, 50, 6); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)
    ctx.move_to(775, 365); ctx.line_to(830, 390); ctx.line_to(775, 415); ctx.close_path(); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)
    rrect(ctx, 830, 300, 120, 180, 8); fill_stroke(ctx, CONC, lw=4, alpha=a)
    if lt > hit:
        u = clamp((lt - hit) / 1.0)
        wx = lerp(260, 820, u)
        ctx.rectangle(wx - 20, 362, 40, 56); setc(ctx, ORANGE, a * (1 - 0.3 * u)); ctx.fill()
        if u >= 1:
            k = ease((lt - hit - 1.0) / 0.5)
            for (dx, dy) in ((60, -60), (80, 10), (55, 70)):
                ctx.move_to(832, 390); ctx.line_to(832 + dx * k, 390 + dy * k); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "PISTON", 190, 470, 22, INK, True, 1, a)
    text_c(ctx, "CHISEL", 515, 460, 22, INK, True, 1, a)

def card_rate(ctx, t, lt, a):
    card_frame(ctx, "BLOW RATE", a, "≈ 1,100 BLOWS PER MINUTE", ORANGE)
    # stopwatch sweeping one second
    cx, cy = 300, 400
    ctx.arc(cx, cy, 110, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=5, alpha=a)
    rrect(ctx, cx - 18, cy - 140, 36, 26, 5); fill_stroke(ctx, INK2, lw=3, alpha=a)
    u = clamp((lt - 0.4) / 1.6)
    ang = -math.pi / 2 + 2 * math.pi * u
    ctx.move_to(cx, cy); ctx.line_to(cx + 90 * math.cos(ang), cy + 90 * math.sin(ang))
    setc(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
    text_c(ctx, "1 s", cx, cy + 60, 26, INK, True, 0, a)
    n = int(round(18 * u))
    text_c(ctx, "%d" % n, 690, 450, 150, RED, True, 0, a)
    text_c(ctx, "BLOWS", 690, 300, 30, INK, True, 2, a)

def card_ice(ctx, t, lt, a):
    card_frame(ctx, "EXPANDING AIR COOLS", a, "THE EXHAUST CAN ICE UP", COLD)
    e = ease((lt - 0.4) / 1.8)
    rrect(ctx, 150, 350, 120, 100, 10); fill_stroke(ctx, AIR_P, lw=4, alpha=a)
    text_c(ctx, "6 bar", 210, 410, 26, WHITE, True, 0, a)
    for k in range(3):
        wavy_arrow(ctx, 280, 360 + k * 40, 330 + 260 * e, 330 + k * 60, lt + k, AIR, a, amp=6, lw=4, head=10)
    rnd = random.Random(4)
    for i in range(7):
        x = 380 + rnd.random() * 280; y = 290 + rnd.random() * 220
        r = 10 + 6 * rnd.random()
        for k in range(3):
            an = k * math.pi / 3 + lt * 0.5
            ctx.move_to(x - r * math.cos(an), y - r * math.sin(an)); ctx.line_to(x + r * math.cos(an), y + r * math.sin(an))
        setc(ctx, COLD, a * e); ctx.set_line_width(3); ctx.stroke()
    thermometer(ctx, 820, 500, 0.75 - 0.6 * e, a, COLD, 220)
    text_c(ctx, "COLD!", 900, 330, 30, COLD, True, 0, a * e)

CARDS = {'pressure': card_pressure, 'shock': card_shock, 'rate': card_rate, 'ice': card_ice}
