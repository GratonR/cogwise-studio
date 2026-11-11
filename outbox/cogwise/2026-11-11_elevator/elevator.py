"""Cogwise episode: Your elevator motor barely lifts anything (traction elevator + counterweight)."""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="elevator",
    title="Your elevator motor barely lifts anything 🛗",
    description=("A stack of iron on the other end of the cable does the lifting. The motor only moves the difference.\n\n"
                 "#Shorts #howthingswork #elevator #engineering #cogwise"),
    hashtags=["Shorts", "howthingswork", "elevator", "engineering", "physics", "cogwise"],
    sources=[
        "https://tkelevator.com/us-en/tools/classroom-on-demand/counterweights.html",
        "https://www.explainthatstuff.com/how-elevators-work.html",
        "https://habitatmag.com/Publication-Content/Green-Ideas/2014/2014-November/Ask-Habitat-Elevator-Regen-Drives",
    ],
)

BEATS = [
    dict(dur=5.0, title="YOUR ELEVATOR", caption="Your elevator motor barely lifts anything. The iron behind the wall does."),
    dict(dur=4.6, title="THE SECRET", caption="It's a stack of iron blocks on the other end of the cable."),
    dict(dur=5.6, title="THE WHEEL", caption="The cable runs over a grooved wheel: car on one side, iron on the other."),
    dict(dur=5.4, title="1 · COUNTERWEIGHT", caption="That counterweight equals the empty car, plus about half the load it can carry."),
    dict(dur=6.0, title=None, caption="Take a one-thousand-kilo car, twenty-two hundred pounds, built to carry a thousand more.", card='numbers'),
    dict(dur=5.4, title="THE IRON", caption="Its counterweight is about fourteen hundred fifty kilos, thirty-two hundred pounds."),
    dict(dur=6.2, title=None, caption="Like a seesaw, the two sides almost cancel. The motor only lifts the difference.", card='seesaw'),
    dict(dur=6.0, title="HALF FULL", caption="Half full, that difference is just fifty kilos, a hundred ten pounds. One passenger."),
    dict(dur=6.0, title="FULL", caption="Even packed, it only hauls the extra five hundred fifty kilos, twelve hundred pounds."),
    dict(dur=5.6, title="3 · EMPTY CAR", caption="And empty? The iron is heavier, so the car wants to rise on its own."),
    dict(dur=5.8, title="GOING UP", caption="Going up empty, the motor holds it back, and newer drives turn that into electricity."),
    dict(dur=5.8, title="ELEVATOR = SEESAW", caption="Elevator equals seesaw. The iron does the lifting; the motor just tips the balance."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

ANCHOR = (560, 1500)

# ---------------------------------------------------------------- geometry (screen coords, y down)
SHV = (560, 440); SR = 100                 # grooved wheel (sheave) centre + radius
XL, XR = SHV[0] - SR, SHV[0] + SR          # rope x: car side (left) / counterweight side (right)
CAR_W, CAR_H = 260, 280
CW_W, CW_H = 90, 240
CAR_TOP0, TRAVEL = 1190, 560               # car top at p=0 (bottom landing); p=1 -> top 630
ROPE_SUM = (CAR_TOP0 - SHV[1]) + (630 - SHV[1])   # car rope + cw rope = constant (cable length)
SLAB = 570                                 # machine-room floor slab top
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); STEEL_L = hexc('#e3e7ea')
IRON = hexc('#6f6a72'); IRON_L = hexc('#8c8790')
CRATE = MUSTARD; GREEN = hexc('#4c9d6b'); CONC = hexc('#e2d3b5')

def car_top(p): return CAR_TOP0 - TRAVEL * p
def cw_top(p):  return SHV[1] + ROPE_SUM - (car_top(p) - SHV[1])

# car position p (0 = bottom, 1 = top): it always moves UP (never down) in this episode
PKEYS = [(0.0, 0.0), (B(3), 0.35), (B(7) + 0.6, 0.35), (B(8), 0.50), (B(8) + 0.4, 0.50), (B(9), 0.62),
         (B(10) + 0.2, 0.62), (B(11), 0.97), (B(12) + 10, 0.97)]
def pos(t):
    for i in range(1, len(PKEYS)):
        t0, p0 = PKEYS[i-1]; t1, p1 = PKEYS[i]
        if t <= t1:
            u = clamp((t - t0) / max(1e-6, t1 - t0))
            return lerp(p0, p1, u)         # linear = steady speed, like a real car
    return PKEYS[-1][1]

def vel(t): return (pos(t + 0.05) - pos(t - 0.05)) / 0.1

def load(t):
    """Number of 100 kg crates in the car: 0 -> 5 (half) -> 10 (full) -> 0 (empty)."""
    if t < B(7) + 0.1: return 0
    if t < B(8) + 0.1: return min(5, int((t - B(7) - 0.1) / 0.1) + 1)
    if t < B(9) + 0.1: return min(10, 5 + int((t - B(8) - 0.1) / 0.1) + 1)
    return 0

# ---------------------------------------------------------------- drawing
def hatch(ctx, x, y, w, h, a=1.0):
    rrect(ctx, x, y, w, h, 2); setc(ctx, CONC, a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    for k in range(-int(h), int(w), 22):
        ctx.move_to(x + k, y + h); ctx.line_to(x + k + h, y)
    setc(ctx, INK2, 0.35 * a); ctx.set_line_width(2); ctx.stroke(); ctx.restore()

def draw_building(ctx, t):
    # machine room
    rrect(ctx, 200, 320, 720, 250, 4); setc(ctx, FILL2); ctx.fill()
    hatch(ctx, 190, 300, 740, 22)                      # roof
    hatch(ctx, 190, 320, 26, 1158); hatch(ctx, 904, 320, 26, 260)   # outer walls
    # shaft walls
    hatch(ctx, 280, 595, 28, 883); hatch(ctx, 740, 595, 28, 883)
    ctx.rectangle(308, 595, 432, 883); setc(ctx, WALL2); ctx.fill()
    # floor slabs of the building (left of shaft) + landing marks
    for y in (1198, 918):
        hatch(ctx, 216, y - 18, 64, 18)
    for k, y in enumerate((1470, 1190, 910)):
        text_c(ctx, str(k + 1), 248, y - 120, 30, INK2, True, 0)
    # machine-room floor slab with rope holes
    hatch(ctx, 216, SLAB, 688, 25)
    for x in (XL, XR):
        ctx.rectangle(x - 9, SLAB - 1, 18, 27); setc(ctx, WALL2); ctx.fill()
    # counterweight guide rails
    for x in (612, 708):
        ctx.move_to(x, 595); ctx.line_to(x, 1478); setc(ctx, STEEL_D); ctx.set_line_width(4); ctx.stroke()
    # pit buffers
    for x in (460, 660):
        rrect(ctx, x - 16, 1446, 32, 32, 4); fill_stroke(ctx, STEEL_D, lw=3)

def draw_motor(ctx, t, st):
    # machine housing behind the wheel (coaxial gearless machine), visible on the right
    rrect(ctx, 590, 368, 230, 150, 14); fill_stroke(ctx, STEEL, lw=5)
    for k in range(4):
        ctx.move_to(700 + k * 26, 384); ctx.line_to(700 + k * 26, 502)
        setc(ctx, STEEL_D); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "MOTOR", 760, 545, 22, INK, True, 2)
    rrect(ctx, 600, 518, 210, 52, 4); fill_stroke(ctx, STEEL_D, lw=4)   # bed plate

def draw_sheave(ctx, t, st):
    cx, cy = SHV
    ang = st['p'] * TRAVEL / SR             # rope moving up on the left = clockwise (+ angle in cairo)
    ctx.arc(cx, cy, SR + 6, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=6)
    for r in (SR - 4, SR - 12, SR - 20):    # grooves
        ctx.arc(cx, cy, r, 0, 2*math.pi); setc(ctx, INK2, 0.7); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(cx, cy, SR - 28, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=4)
    for k in range(5):                      # spokes rotate with the wheel
        a = ang + k * 2*math.pi/5
        ctx.move_to(cx + 22*math.cos(a), cy + 22*math.sin(a)); ctx.line_to(cx + (SR-30)*math.cos(a), cy + (SR-30)*math.sin(a))
        setc(ctx, INK); ctx.set_line_width(9); ctx.stroke()
    ctx.arc(cx + (SR - 16)*math.cos(ang), cy + (SR - 16)*math.sin(ang), 7, 0, 2*math.pi); setc(ctx, RED); ctx.fill()
    ctx.arc(cx, cy, 22, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=4)
    # ropes wrapped over the top half
    ctx.new_path(); ctx.arc(cx, cy, SR, math.pi, 2*math.pi)
    setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()

def draw_ropes(ctx, t, st):
    p = st['p']; ct = car_top(p); wt = cw_top(p)
    for x, y1 in ((XL, ct - 26), (XR, wt)):
        ctx.move_to(x, SHV[1]); ctx.line_to(x, y1); setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()
    # marks fixed on the cable: they travel with the car (left) and with the iron (right)
    for x, y0 in ((XL, ct - 26), (XR, wt)):
        for k in range(1, 30):
            y = y0 - k * 70
            if y < SHV[1] + 8: break
            ctx.rectangle(x - 5, y, 10, 14); setc(ctx, MUSTARD); ctx.fill()

def draw_car(ctx, t, st):
    p = st['p']; y = car_top(p); x = XL - CAR_W/2
    # crosshead + hitch
    ctx.move_to(XL - 70, y - 4); ctx.line_to(XL, y - 30); ctx.line_to(XL + 70, y - 4)
    setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()
    rrect(ctx, XL - 14, y - 40, 28, 18, 4); fill_stroke(ctx, STEEL_D, lw=3)
    rrect(ctx, x, y, CAR_W, CAR_H, 8); fill_stroke(ctx, PAPER, lw=6)
    rrect(ctx, x + 14, y + 16, CAR_W - 28, CAR_H - 30, 4); setc(ctx, FILL2); ctx.fill()
    ctx.move_to(x + 14, y + 60); ctx.line_to(x + CAR_W - 14, y + 60); setc(ctx, INK2, 0.5); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(XL, y + 38, 9, 0, 2*math.pi); setc(ctx, MUSTARD); ctx.fill()        # ceiling light
    # crates: 1 crate = 100 kg
    n = st['load']
    for i in range(n):
        row, col = divmod(i, 5)
        cx = x + 22 + col * 44; cy = y + CAR_H - 16 - (row + 1) * 42
        rrect(ctx, cx, cy, 40, 40, 4); fill_stroke(ctx, CRATE, lw=3)
        ctx.move_to(cx + 4, cy + 4); ctx.line_to(cx + 36, cy + 36); setc(ctx, INK, 0.5); ctx.set_line_width(2); ctx.stroke()
    rrect(ctx, x - 6, y + CAR_H - 8, CAR_W + 12, 16, 4); fill_stroke(ctx, INK2, lw=3)   # car floor

def draw_cw(ctx, t, st):
    p = st['p']; y = cw_top(p); x = XR - CW_W/2
    ctx.move_to(XR, y); ctx.line_to(XR, y + 14); setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()
    rrect(ctx, x - 6, y + 10, CW_W + 12, CW_H + 8, 6); fill_stroke(ctx, STEEL_D, lw=5)   # frame
    hl = st['iron_glow']
    for k in range(6):
        rrect(ctx, x + 4, y + 18 + k * 39, CW_W - 8, 35, 3)
        fill_stroke(ctx, lerpc(IRON, RED, 0.45 * hl), lw=3)
        ctx.move_to(x + 12, y + 26 + k * 39); ctx.line_to(x + CW_W - 12, y + 26 + k * 39)
        setc(ctx, IRON_L, 0.8); ctx.set_line_width(3); ctx.stroke()

def torque_arrow(ctx, color, a, clockwise=True, lab=None, t=0):
    if a <= 0: return
    cx, cy = SHV; r = SR + 38
    a0, a1 = -2.5, -0.65
    ctx.new_path(); ctx.arc(cx, cy, r, a0, a1)
    setc(ctx, color, a); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    end = a1 if clockwise else a0
    ex, ey = cx + r*math.cos(end), cy + r*math.sin(end)
    tang = end + (math.pi/2 if clockwise else -math.pi/2)          # direction of travel at the tip
    hx, hy = math.cos(tang), math.sin(tang)
    ctx.move_to(ex + hx*22, ey + hy*22)
    ctx.line_to(ex - hy*16, ey + hx*16); ctx.line_to(ex + hy*16, ey - hx*16); ctx.close_path()
    setc(ctx, color, a); ctx.fill()

def bolt(ctx, x, y, s, a):
    if a <= 0: return
    ctx.move_to(x, y); ctx.line_to(x + 30*s, y - 10*s); ctx.line_to(x + 22*s, y + 6*s); ctx.line_to(x + 60*s, y - 4*s)
    ctx.line_to(x + 26*s, y + 22*s); ctx.line_to(x + 34*s, y + 6*s); ctx.close_path()
    fill_stroke(ctx, MUSTARD, lw=4, alpha=a)

def state(t):
    s = {}
    s['p'] = pos(t); s['v'] = vel(t); s['load'] = load(t)
    s['iron_glow'] = max(win(t, 0.8, B(2), 0.4), bw(t, 5), bw(t, 11))
    s['h_cw'] = max(win(t, 0.8, B(2), 0.4), bw(t, 3), bw(t, 5))
    s['h_shv'] = bw(t, 2)
    s['h_mot'] = max(bw(t, 7, 9), bw(t, 10))
    s['l_iron'] = win(t, 1.2, B(2), 0.3)
    s['l_cw'] = bw(t, 3) + bw(t, 11) * 0
    s['l_formula'] = win(t, B(3) + 1.6, B(4), 0.3)
    s['l_whl'] = bw(t, 2)
    s['l_kg'] = bw(t, 5)
    s['l_box'] = bw(t, 7, 9)
    s['drive'] = bw(t, 7, 9)
    s['rise'] = win(t, B(9) + 1.4, B(10) + 0.4, 0.3)
    s['brake'] = bw(t, 10)
    s['volt'] = win(t, B(10) + 2.4, B(11), 0.3)
    s['recap'] = bw(t, 11)
    return s

def draw_stage(ctx, t, s):
    draw_building(ctx, t)
    draw_motor(ctx, t, s)
    draw_ropes(ctx, t, s)
    draw_sheave(ctx, t, s)
    draw_car(ctx, t, s)
    draw_cw(ctx, t, s)
    p = s['p']; ct = car_top(p); wt = cw_top(p)
    # highlights
    highlight(ctx, XR, wt + 130, 80, 160, RED, s['h_cw'], t)
    highlight(ctx, SHV[0], SHV[1], 150, 150, TEAL, s['h_shv'], t)
    highlight(ctx, 705, 445, 140, 100, TEAL, s['h_mot'], t)
    # tags (right of the shaft, in the empty strip x 790..1060)
    tag(ctx, "IRON BLOCKS", 900, wt + 120, RED, s['l_iron'], 26)
    tag(ctx, "COUNTERWEIGHT", 900, wt + 120, RED, s['l_cw'], 24)
    tag(ctx, "= CAR + ½ LOAD", 900, wt + 190, INK, s['l_formula'], 24)
    tag(ctx, "1 450 kg", 900, wt + 100, RED, s['l_kg'], 28)
    tag(ctx, "3 200 lb", 900, wt + 160, RED, s['l_kg'], 24)
    tag(ctx, "1 000 kg", XL, ct + 150, INK, s['l_kg'], 28)
    tag(ctx, "GROOVED WHEEL", 560, 640, TEAL, s['l_whl'], 26)
    tag(ctx, "CAR", XL - 210 + 210, ct - 70, INK, s['l_whl'], 22)
    tag(ctx, "IRON", XR + 0, wt - 30, RED, s['l_whl'] * (1 if wt > 640 else 0), 22)
    tag(ctx, "1 BOX = 100 kg · 220 lb", 560, ct + CAR_H + 50, MUSTARD, s['l_box'] * (1 if ct + CAR_H + 50 < 1440 else 0), 22)
    # motor torque: drives (same way as the wheel turns) when loaded, brakes (opposite) when empty
    torque_arrow(ctx, TEAL, s['drive'], clockwise=True)
    torque_arrow(ctx, RED, s['brake'], clockwise=False)
    tag(ctx, "2 · THE MOTOR", 900, 640, TEAL, s['drive'], 24)
    # empty car: it wants to go UP (iron is heavier)
    if s['rise'] > 0 or s['brake'] > 0:
        a = max(s['rise'], s['brake'])
        straight_arrow(ctx, XL, ct + 200, XL, ct + 80, GREEN, a, lw=10, head=18)
        straight_arrow(ctx, XR, wt + 120, XR, wt + 250, RED, a, lw=10, head=18)
    tag(ctx, "WANTS TO RISE", XL, ct + 240, GREEN, s['rise'], 24)
    tag(ctx, "MOTOR BRAKES", 900, 640, RED, s['brake'], 24)
    if s['volt'] > 0:
        bolt(ctx, 836, 420, 1.2, s['volt'])
        tag(ctx, "POWER BACK", 880, 490, MUSTARD, s['volt'], 22)
    tag(ctx, "IRON LIFTS", 900, wt + 120, RED, s['recap'], 24)
    tag(ctx, "MOTOR TIPS", 880, 640, TEAL, s['recap'], 24)

def draw(ctx, t, E):
    draw_stage(ctx, t, state(t))

OVER = (575, 900, 1.0)
CAMKEYS = [(0, *OVER), (B(2), 590, 640, 1.35), (B(3), *OVER), (B(10), 640, 760, 1.15), (B(11), *OVER)]
def CAM(t): return cam_track(CAMKEYS, t)

# ---------------------------------------------------------------- HUD
def draw_hud(ctx, t, E):
    a7 = win(t, B(7) + 0.3, B(9), 0.3)
    if a7 > 0:
        full = t >= B(8) + 0.2
        flash = max(0.0, 1 - (t - (B(8) + 0.2)) / 0.6) if full else max(0.0, 1 - (t - B(7) - 0.3) / 0.6)
        hud(ctx, "MOTOR LIFTS ONLY", "550 kg" if full else "50 kg",
            "≈ 1 200 LB · FULL CAR" if full else "≈ 110 LB · HALF FULL", a7, TEAL, flash, x=600, y=150, w=460)
    a9 = win(t, B(9) + 0.3, B(11), 0.3)
    if a9 > 0:
        hud(ctx, "EMPTY · IRON HEAVIER BY", "450 kg", "≈ 990 LB", a9, RED, 0.0, x=600, y=150, w=460)

# ---------------------------------------------------------------- cards
def mini_car(ctx, x, y, w, h, a, crates=0):
    rrect(ctx, x, y, w, h, 6); fill_stroke(ctx, PAPER, lw=4, alpha=a)
    for i in range(crates):
        row, col = divmod(i, 5)
        cx = x + 8 + col * ((w - 16) / 5); cy = y + h - 8 - (row + 1) * 26
        rrect(ctx, cx + 2, cy, (w - 16) / 5 - 4, 24, 3); fill_stroke(ctx, CRATE, lw=2, alpha=a)

def card_numbers(ctx, t, lt, a):
    card_frame(ctx, "THE NUMBERS", a, "BUILT TO CARRY 1 000 kg MORE", TEAL)
    mini_car(ctx, 170, 270, 170, 210, a)
    text_c(ctx, "CAR", 255, 510, 26, INK, True, 2, a)
    text_c(ctx, "1 000 kg", 600, 330, 54, INK, True, 1, a)
    text_c(ctx, "2 200 lb", 600, 380, 34, INK2, True, 1, a)
    b = a * ease((lt - 2.6) / 0.5)
    n = int(clamp((lt - 2.6) / 0.08, 0, 10))
    for i in range(n):
        row, col = divmod(i, 5)
        cx = 178 + col * 31; cy = 472 - (row + 1) * 26
        rrect(ctx, cx + 2, cy, 27, 24, 3); fill_stroke(ctx, CRATE, lw=2, alpha=b)
    text_c(ctx, "+ LOAD 1 000 kg", 640, 460, 40, MUSTARD, True, 1, b)
    text_c(ctx, "2 200 lb", 640, 500, 28, INK2, True, 1, b)

def card_seesaw(ctx, t, lt, a):
    card_frame(ctx, "LIKE A SEESAW", a, "THE MOTOR LIFTS ONLY THE DIFFERENCE", TEAL)
    px, py = 540, 440
    tilt = -0.05 * math.sin(lt * 2.2) * (1 - ease((lt - 3.0) / 1.0)) - 0.025   # left (car + load) slightly heavier
    L = 330
    ctx.move_to(px, py); ctx.line_to(px - 46, py + 90); ctx.line_to(px + 46, py + 90); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=4, alpha=a)
    ctx.save(); ctx.translate(px, py); ctx.rotate(tilt)
    rrect(ctx, -L, -8, 2 * L, 16, 6); fill_stroke(ctx, INK2, lw=3, alpha=a)
    # left: car + load
    mini_car(ctx, -L + 10, -128, 150, 120, a, 5)
    text_c(ctx, "CAR + LOAD", -L + 85, -142, 24, INK, True, 1, a)
    # right: iron stack
    for k in range(4):
        rrect(ctx, L - 140, -8 - (k + 1) * 30, 120, 28, 3); fill_stroke(ctx, IRON, lw=3, alpha=a)
    text_c(ctx, "IRON", L - 80, -142, 24, RED, True, 1, a)
    ctx.restore()
    ctx.arc(px, py, 10, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    d = a * ease((lt - 2.8) / 0.5)
    straight_arrow(ctx, 210, 530, 210, 470, TEAL, d, lw=8, head=14)
    text_c(ctx, "MOTOR", 300, 520, 24, TEAL, True, 1, d)

CARDS = {'numbers': card_numbers, 'seesaw': card_seesaw}

SFX = [(0.9, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.2, 'pop'), (B(3) + 0.2, 'pop'), (B(3) + 1.6, 'pop'),
       (B(5) + 0.2, 'pop'), (B(7) + 0.3, 'pop'), (B(8) + 0.2, 'pop'), (B(9) + 0.3, 'pop'), (B(10) + 0.2, 'click'),
       (B(10) + 2.4, 'pop'), (B(11) + 0.2, 'pop')]
HUM = []

def draw_set(ctx):
    pass
