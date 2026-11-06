"""Cogwise R&D (2026-11-06): micro-beat remake of the brake episode.
Format test: ~2 s beats, camera moves to each part, a permanent FORCE counter (HUD), big word pops,
no outro (loops back to the first frame). Version A = Jesse voice; version B = same picture, music only."""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="brake-micro",
    title="How does one small pedal stop a whole car? 🛑",
    description="R&D prototype (micro-beats).",
    hashtags=["Shorts", "howthingswork", "brakes", "cars", "engineering"],
    sources=[
        "https://us.haynes.com/blogs/tips-tutorials/how-do-car-brakes-work",
        "https://www.brakeandfrontend.com/brake-pedal-ratio/",
        "https://asv.kwik-fit.com/blog/should-brake-discs-get-hot",
    ],
)
OUTRO = False

BEATS = [
    dict(dur=2.2, title=None, caption="One light push of your foot"),                 # 0
    dict(dur=2.2, title=None, caption="stops over a ton of car."),                    # 1
    dict(dur=2.6, title=None, caption="How? Your push gets multiplied. Three times."), # 2
    dict(dur=2.2, title=None, caption="First, the pedal is a lever:"),                # 3
    dict(dur=1.8, title=None, caption="four times the force."),                       # 4
    dict(dur=1.8, title=None, caption="Then the booster helps:"),                     # 5
    dict(dur=1.8, title=None, caption="three times again."),                          # 6
    dict(dur=2.2, title=None, caption="Now your push hits a liquid."),                # 7
    dict(dur=2.2, title=None, caption="Brake fluid can't be squeezed,"),              # 8
    dict(dur=2.4, title=None, caption="so the pressure races to every wheel."),       # 9
    dict(dur=2.6, title=None, caption="There, the caliper piston is six times wider:"),# 10
    dict(dur=1.8, title=None, caption="six times the force."),                        # 11
    dict(dur=2.2, title=None, caption="Over a ton, pinching the disc."),              # 12
    dict(dur=2.8, title=None, caption="The disc slows, and the motion becomes heat."),# 13
    dict(dur=2.8, title=None, caption="Lift your foot: the pressure drops, the pads let go."), # 14
    dict(dur=2.0, title=None, caption="Lever, booster, liquid."),                     # 15
    dict(dur=2.0, title=None, caption="That's how one light push..."),                # 16
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.3):
    return win(t, B(i) + 0.05, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
DC = (560, 760); DR = 250; HUB = 105
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); STEEL_L = hexc('#e3e7ea')
CAL = RED; PAD = hexc('#8a6a3a'); FLUID = MUSTARD; FLUID_P = hexc('#e4472f')
GREEN = hexc('#4c9d6b'); HOT = hexc('#f2902b')
PIVOT = (250, 1060)
LINE = [(620, 1215), (930, 1215), (930, 905), (870, 870)]

def press(t):
    return ease((t - 0.25) / 0.9) * (1 - ease((t - B(14) - 0.3) / 0.8))

def speed(t):
    s = 1.0 - 0.9 * ease((t - B(12) - 0.2) / 2.6)
    s = lerp(s, 1.0, ease((t - B(14) - 0.6) / 2.4))
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
    st['foot'] = win(t, 0.0, B(2), 0.3) + win(t, B(16) - 0.2, B(17) + 1, 0.3) * 0
    st['fill'] = max(ease((t - B(7) - 0.2) / 0.8) * 0.25, ease((t - B(9)) / 1.2)) * (1 - ease((t - B(15) - 0.6) / 0.8))
    st['pres'] = st['press'] * ease((t - B(7)) / 0.8)
    st['flow'] = bw(t, 9) * 0.9
    st['clamp'] = st['press'] * ease((t - B(10)) / 1.0)
    st['spd'] = speed(t)
    st['ang'] = angle(t)
    st['marks'] = 1.0
    st['heat'] = ease((t - B(13) - 0.3) / 1.6) * (1 - ease((t - B(15)) / 2.0))
    st['h_ped'] = bw(t, 3, 5)
    st['h_mc'] = bw(t, 5, 9)
    st['h_line'] = bw(t, 9)
    st['h_cal'] = bw(t, 10, 13)
    st['h_disc'] = bw(t, 13)
    st['h_res'] = 0
    rec = bw(t, 15, 16)
    st['l_ped'] = bw(t, 3, 5) + win(t, B(15), B(16), 0.2)
    st['l_mc'] = bw(t, 5, 9) + win(t, B(15) + 0.5, B(16), 0.2)
    st['l_line'] = bw(t, 9) + win(t, B(15) + 1.0, B(16), 0.2)
    st['l_cal'] = bw(t, 10, 13)
    st['l_disc'] = bw(t, 13)
    st['grip'] = win(t, B(12) + 0.2, B(13))
    st['vent'] = bw(t, 13) * 0.8
    st['rel'] = 0
    st['recap'] = 0
    st['tip'] = 0
    return st

# camera: (from design time, centre x, centre y, zoom)
OVER = (560, 900, 1.0)
CAMKEYS = [(0, *OVER),
           (B(3), 300, 1230, 1.6),    # pedal
           (B(5), 420, 1215, 1.6),    # booster
           (B(7), 530, 1170, 1.6),    # master cylinder + fluid
           (B(9), 790, 1010, 1.25),   # brake line to the wheel
           (B(10), 800, 780, 1.55),   # caliper
           (B(12), 680, 790, 1.25),   # caliper + disc
           (B(14), *OVER)]
def CAM(t): return cam_track(CAMKEYS, t)

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

# ---------------------------------------------------------------- HUD + pops
STEPS = [(0, "20 kg", "≈ 44 LB · YOUR FOOT"), (B(4), "80 kg", "×4 LEVER · ≈ 176 LB"),
         (B(6), "240 kg", "×3 BOOSTER · ≈ 530 LB"), (B(11), "1.4 t", "×6 PISTON · ≈ 3,200 LB"),
         (B(15), "20 kg", "≈ 44 LB · YOUR FOOT")]
POPS = [(B(1) + 0.3, "1 TON+", INK2, 120), (B(4) + 0.05, "×4", RED, 190), (B(6) + 0.05, "×3", RED, 190),
        (B(8) + 0.2, "NO SQUEEZE", TEAL, 104), (B(11) + 0.05, "×6", RED, 190), (B(13) + 1.0, "≈130 °C", HOT, 130),
        (B(13) + 1.9, "≈266 °F", HOT, 96)]

def draw_hud(ctx, t, E):
    val, sub, t0 = STEPS[0][1], STEPS[0][2], 0
    for (ts, v, s_) in STEPS:
        if t >= ts: val, sub, t0 = v, s_, ts
    flash = max(0.0, 1 - (t - t0) / 0.6) if t0 > 0 else 0.0
    hud(ctx, "FORCE ON THE BRAKE", val, sub, 1.0, RED, flash)
    for (ts, w, col, size) in POPS:
        pop_word(ctx, w, t - ts, 1.3, col, cy=470, size=size)

SFX = [(0.25, 'pop'), (B(4) + 0.05, 'pop'), (B(6) + 0.05, 'pop'), (B(11) + 0.05, 'pop'),
       (B(3) + 0.1, 'whoosh'), (B(5) + 0.1, 'whoosh'), (B(7) + 0.1, 'whoosh'), (B(9) + 0.1, 'whoosh'),
       (B(10) + 0.1, 'whoosh'), (B(14) + 0.1, 'whoosh'), (B(14) + 0.4, 'click')]
