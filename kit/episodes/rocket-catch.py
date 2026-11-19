"""Cogwise episode: Why catch a rocket instead of landing it on legs.
One idea: the tower IS the landing gear. Legs would fly to space and back on every flight; on the upper
stage every kilo of legs is a kilo of cargo left behind. So the heavy, strong parts stay on the ground
(the tower and its two "chopsticks" arms) and the ship only carries two small catch pins.
News peg: Starship Flight 15 (14 Nov 2026), Ship 42 came back from orbit and was caught by the tower.

VIEW (screen coordinates, y grows DOWN): we stand in FRONT of the tower and look at it. The ship hovers
between us and the tower, nose UP (small y), engines DOWN (big y). The tower is a lattice column drawn
BEHIND the ship. The two arms come out of the tower towards us, one on each side of the ship: seen from
the front, "swinging closed" = the two arm ends move INWARD (left arm to the right, right arm to the left)
until they sit just outside the ship's skin, right UNDER the two catch pins.
Catch pins stick out LEFT and RIGHT near the top of the ship (just below the forward flaps).
Engines push the ship UP (thrust arrow -y); flames point DOWN (+y). After engine cut-off the weight points
DOWN (+y) on the pins and the arms push back UP (-y).
TIMELINE: beat 1 = teaser (ship comes down, arms close by ~1.6 s). Beat 2 = tower highlighted.
Beats 3-4 = tower fades, ship shown with red landing legs (what it would need otherwise). Beat 5 = ship
hovers again, arms open and low. Beat 6 = carriage slides up to pin height and closes (+ top-view inset).
Beat 7 = pins. Beat 8 = tower/heavy parts. Beat 9 = engines off, ship settles on the arms (forces).
Beat 10 = card: barge trip vs land where you launch. Beat 11 = arms lift the ship (restack).
Beat 12 = recap.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="rocket-catch",
    title="Why catch a rocket instead of landing it on legs 🚀 #Shorts",
    description=("The tower is the landing gear. Legs would fly to space and back every time.\n\n"
                 "#Shorts #howthingswork #starship #spacex #rocket #cogwise"),
    hashtags=["Shorts", "howthingswork", "starship", "spacex", "rocket", "cogwise"],
    sources=[
        "https://www.space.com/space-exploration/launches-spacecraft/spacex-chopsticks-catch-starship-upper-stage-flight-14",
        "https://interestingengineering.com/space/spacex-starship-ship-42-first-upper-stage-catch",
        "https://www.teslarati.com/spacex-catches-starship-first/",
        "https://www.bgr.com/2279871/why-spacex-plans-to-catch-starship-instead-of-landing-legs/",
        "https://www.universetoday.com/articles/musk-confirms-how-mechazilla-will-catch-and-assemble-starship-and-super-heavy-for-rapid-reuse",
    ],
)

BEATS = [
    dict(dur=5.0, title="CAUGHT", caption="Last week, a ship fell back from orbit… and a tower caught it."),
    dict(dur=5.0, title="THE SECRET", caption="Why not just land on legs? Because the tower is the landing gear."),
    dict(dur=4.8, title="LEGS", caption="Legs ride all the way to space and back. Every single flight."),
    dict(dur=5.6, title=None, caption="On the upper stage, every kilo of legs is a kilo of cargo left behind.", card='cargo'),
    dict(dur=5.6, title="1 · HOVER", caption="So the ship comes down tail first, hovering on its engines beside the tower."),
    dict(dur=5.6, title="2 · CHOPSTICKS", caption="Two giant arms, nicknamed the chopsticks, slide to its height and swing closed."),
    dict(dur=5.8, title="3 · CATCH PINS", caption="Two small pins near the top rest on the arms. That's all the landing gear it carries."),
    dict(dur=5.0, title="STAYS DOWN", caption="The heavy, strong parts stay on the ground, where weight costs nothing."),
    dict(dur=5.6, title="ENGINES OFF", caption="The engines shut down, and the arms hold the full weight of the empty ship."),
    dict(dur=5.6, title=None, caption="And it lands right where it launches. No barge, no truck, no long trip home.", card='trip'),
    dict(dur=5.2, title="FLY AGAIN", caption="The same arms can lift it back onto a booster for the next flight."),
    dict(dur=4.8, title="TOWER = LEGS", caption="Legs in space are dead weight. A tower on the ground isn't."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette / geometry
SKY1 = hexc('#d6ebe6'); SKY2 = hexc('#f6ecd6')
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#7d848b'); STEEL_L = hexc('#e6e9ec')
DARK = hexc('#3b3842'); TOWER = hexc('#8a8f96')
RX, HW = 540, 62                      # ship axis, body half-width
Y_TIP, Y_OG = 330, 470                # nose tip / end of the nose cone
Y_BOT = 1240                          # bottom of the ship body (engine skirt)
Y_NOZ = 1305                          # nozzle exits
Y_PIN = 540                           # catch pins (centre)
PIN_W, PIN_H = 30, 20
Y_ARM_HI = Y_PIN + PIN_H / 2 + 6      # arm top touching the pin bottom (ship settled, dy = 0)
Y_ARM_LO = 820                        # arms parked low
Y_GROUND = 1470
TX0, TX1 = 380, 700                   # tower lattice (behind the ship)
ARM_OPEN = 205                        # inner arm end distance from axis when open
ARM_CLOSED = HW + 6                   # ... when closed (just outside the skin)

def ship_dy(t):
    """vertical offset of the ship (negative = higher)."""
    if t < B(1):                                          # teaser: comes down, arms close, settles
        if t < 1.3: return lerp(-300, -14, ease(clamp(t / 1.3)))
        return lerp(-14, 0, ease(clamp((t - 2.6) / 0.4)))
    if t < B(4): return 0.0
    if t < B(5):                                          # hover: comes down again from above
        return lerp(-260, -14, ease(clamp((t - B(4)) / 2.2)))
    if t < B(8) + 1.0: return -14.0                       # hovering just above the arms
    if t < B(10): return lerp(-14, 0, ease(clamp((t - B(8) - 1.0) / 0.4)))
    if t < B(11): return lerp(0, -170, ease(clamp((t - B(10) - 0.5) / 2.6)))   # lifted
    return 0.0

def arms(t):
    """(y of the arm top, half-gap of the arms) ; arms move with the ship when lifting."""
    if t < B(1):
        k = ease(clamp((t - 0.9) / 0.6))
        return Y_ARM_HI, lerp(ARM_OPEN, ARM_CLOSED, k)
    if t < B(4):
        return Y_ARM_HI, ARM_CLOSED
    if t < B(5):
        return Y_ARM_LO, ARM_OPEN
    if t < B(6):
        ky = ease(clamp((t - B(5) - 0.3) / 2.2))
        kx = ease(clamp((t - B(5) - 2.8) / 1.4))
        return lerp(Y_ARM_LO, Y_ARM_HI - 14, ky), lerp(ARM_OPEN, ARM_CLOSED, kx)
    if t < B(10):
        return Y_ARM_HI + min(0, ship_dy(t)), ARM_CLOSED
    if t < B(11):
        return Y_ARM_HI + ship_dy(t), ARM_CLOSED
    return Y_ARM_HI, ARM_CLOSED

def engines(t):
    """0 off .. 1 on (hover)"""
    if t < B(1): return 1.0 - ease(clamp((t - 2.3) / 0.4))
    if t < B(2): return 0.0
    if t < B(4): return 0.0
    if t < B(8) + 0.5: return 1.0
    return 1.0 - ease(clamp((t - B(8) - 0.5) / 0.5)) if t < B(9) else 0.0

def legs_k(t):
    """red landing legs drawn on the ship (beats 3-4 and the recap)"""
    return max(win(t, B(2) + 0.2, B(4), 0.4), 0.0)

def tower_a(t):
    return 1.0 - 0.85 * win(t, B(2) + 0.1, B(4) - 0.1, 0.5)

# ---------------------------------------------------------------- drawing
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

def nozzle(ctx, cx, y0, y1, w0, w1, fill=STEEL_D, a=1.0):
    ctx.move_to(cx - w0 / 2, y0); ctx.line_to(cx + w0 / 2, y0)
    ctx.curve_to(cx + w0 / 2, y0 + (y1 - y0) * 0.5, cx + w1 / 2 - 4, y1 - 10, cx + w1 / 2, y1)
    ctx.line_to(cx - w1 / 2, y1)
    ctx.curve_to(cx - w1 / 2 + 4, y1 - 10, cx - w0 / 2, y0 + (y1 - y0) * 0.5, cx - w0 / 2, y0)
    ctx.close_path(); fill_stroke(ctx, fill, lw=3, alpha=a)

def tower(ctx, a, hot=0.0):
    """lattice column behind the ship, from the ground up to y 250"""
    if a <= 0: return
    ctx.rectangle(TX0, 250, TX1 - TX0, Y_GROUND - 250)
    setc(ctx, lerpc(FILL3, TEAL_L, hot), 0.55 * a); ctx.fill()
    setc(ctx, TOWER, a); ctx.set_line_width(4)
    for x in (TX0, TX1):
        ctx.move_to(x, 250); ctx.line_to(x, Y_GROUND); ctx.stroke()
    ctx.set_line_width(2.5)
    y = 250; step = 80; i = 0
    while y < Y_GROUND:
        ctx.move_to(TX0, y); ctx.line_to(TX1, y); ctx.stroke()
        y2 = min(Y_GROUND, y + step)
        if i % 2: ctx.move_to(TX0, y); ctx.line_to(TX1, y2)
        else: ctx.move_to(TX1, y); ctx.line_to(TX0, y2)
        ctx.stroke(); y = y2; i += 1
    ctx.rectangle(TX0 - 10, 236, TX1 - TX0 + 20, 18); fill_stroke(ctx, TOWER, lw=3, alpha=a)

def carriage(ctx, ya, a):
    """the arm carriage band across the tower, behind the ship (drawn before the ship)"""
    if a <= 0: return
    ctx.rectangle(TX0 - 14, ya - 6, TX1 - TX0 + 28, 46); fill_stroke(ctx, DARK, lw=3, alpha=a)

def arm_beams(ctx, ya, gap, a):
    """the two arms seen from the front: thick beams coming towards us, ends at RX ± gap (drawn in front)"""
    if a <= 0: return
    for sx in (-1, 1):
        xin = RX + sx * gap
        xout = RX + sx * (gap + 150)
        x0, x1 = min(xin, xout), max(xin, xout)
        ctx.rectangle(x0, ya, x1 - x0, 34); fill_stroke(ctx, MUSTARD, lw=4, alpha=a)
        # rail on top where the pin sits
        ctx.rectangle(x0, ya - 6, x1 - x0, 6); setc(ctx, DARK, a); ctx.fill()
        # hinge back to the carriage (perspective strut)
        ctx.move_to(xout, ya + 34); ctx.line_to(RX + sx * 170, ya + 40)
        setc(ctx, DARK, 0.6 * a); ctx.set_line_width(4); ctx.stroke()

def ship(ctx, t, dy, eng, legs, pin_hot=0.0):
    ctx.save(); ctx.translate(0, dy)
    x0, x1 = RX - HW, RX + HW
    # exhaust (behind nozzles)
    for i, dx in enumerate((-30, 0, 30)):
        flame(ctx, RX + dx, Y_NOZ - 2, 34, 200, t, eng, seed=i)
    for dx in (-30, 0, 30):
        nozzle(ctx, RX + dx, Y_BOT, Y_NOZ, 18, 34)
    # aft flaps (behind/beside the body)
    for sx in (-1, 1):
        ctx.move_to(RX + sx * HW, 1070); ctx.line_to(RX + sx * (HW + 34), 1110)
        ctx.line_to(RX + sx * (HW + 34), 1222); ctx.line_to(RX + sx * HW, 1222); ctx.close_path()
        fill_stroke(ctx, DARK, lw=3)
    # body (stainless steel) + nose
    ctx.move_to(x0, Y_BOT); ctx.line_to(x0, Y_OG)
    ctx.curve_to(x0, 400, RX - 26, Y_TIP + 6, RX, Y_TIP)
    ctx.curve_to(RX + 26, Y_TIP + 6, x1, 400, x1, Y_OG)
    ctx.line_to(x1, Y_BOT); ctx.close_path(); fill_stroke(ctx, STEEL, lw=5)
    # shading strip + ring welds
    ctx.rectangle(x0 + 10, Y_OG, 18, Y_BOT - Y_OG); setc(ctx, STEEL_L, 0.9); ctx.fill()
    for y in range(560, Y_BOT, 110):
        ctx.move_to(x0, y); ctx.line_to(x1, y); setc(ctx, STEEL_D, 0.5); ctx.set_line_width(2); ctx.stroke()
    # forward flaps
    for sx in (-1, 1):
        ctx.move_to(RX + sx * (HW - 4), 418); ctx.line_to(RX + sx * (HW + 26), 448)
        ctx.line_to(RX + sx * (HW + 26), 512); ctx.line_to(RX + sx * HW, 512); ctx.close_path()
        fill_stroke(ctx, DARK, lw=3)
    # catch pins (stick out left and right)
    for sx in (-1, 1):
        px = RX + sx * HW - (PIN_W if sx < 0 else 0)
        ctx.rectangle(px, Y_PIN - PIN_H / 2, PIN_W, PIN_H)
        fill_stroke(ctx, lerpc(MUSTARD, RED, pin_hot), lw=3)
    # landing legs (what it would need otherwise), red
    if legs > 0:
        for sx in (-1, 1):
            ctx.move_to(RX + sx * HW, 1080); ctx.line_to(RX + sx * (HW + 110), Y_NOZ + 60)
            setc(ctx, RED, legs); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
            ctx.move_to(RX + sx * (HW + 80), Y_NOZ + 62); ctx.line_to(RX + sx * (HW + 140), Y_NOZ + 62)
            setc(ctx, RED, legs); ctx.set_line_width(10); ctx.stroke()
            ctx.move_to(RX + sx * HW, 1200); ctx.line_to(RX + sx * (HW + 70), 1270)
            setc(ctx, RED, legs); ctx.set_line_width(7); ctx.stroke()
    ctx.restore()

def topview(ctx, cx, cy, k, a):
    """mini diagram seen FROM ABOVE: tower square, ship circle, two arms swinging closed around it"""
    if a <= 0: return
    rrect(ctx, cx - 150, cy - 130, 300, 280, 16); setc(ctx, CREAM, 0.95 * a); ctx.fill_preserve()
    setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
    tx, ty = cx, cy - 70                 # tower (top of the inset = far side)
    ctx.rectangle(tx - 40, ty - 34, 80, 54); fill_stroke(ctx, TOWER, lw=3, alpha=a)
    sx_, sy_ = cx, cy + 50               # ship (near side)
    ang_open, ang_closed = 0.95, 0.30    # arm angle from straight-ahead
    for sgn in (-1, 1):
        ang = lerp(ang_open, ang_closed, k)
        px, py = tx + sgn * 30, ty + 20
        L = 140
        ex, ey = px + sgn * L * math.sin(ang), py + L * math.cos(ang)
        ctx.move_to(px, py); ctx.line_to(ex, ey)
        setc(ctx, MUSTARD, a); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ctx.arc(px, py, 7, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()
    ctx.arc(sx_, sy_, 26, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=3, alpha=a)
    text_c(ctx, "SEEN FROM ABOVE", cx, cy + 135, 20, INK2, True, 1, a)

# ---------------------------------------------------------------- overlays
def overlays(ctx, t, s):
    dy = s['dy']; ya, gap = s['ya'], s['gap']
    # beat 1 teaser
    a = win(t, 1.5, B(1), 0.3)
    tag(ctx, "CAUGHT BY THE TOWER", RX, 1400, RED, a, 28)
    # beat 2: the tower = landing gear
    a = bw(t, 1)
    if a > 0:
        highlight(ctx, RX, 860, 210, 640, TEAL, a, t)
        tag(ctx, "TOWER = LANDING GEAR", RX, 1400, TEAL, a, 28)
    # beat 3: legs to space and back
    a = bw(t, 2)
    if a > 0:
        tag(ctx, "LANDING LEGS", RX + 270, 1240, RED, a, 26)
        straight_arrow(ctx, 880, 980, 880, 560, RED, a, lw=10, head=20)
        straight_arrow(ctx, 960, 560, 960, 980, RED, a, lw=10, head=20)
        tag(ctx, "TO SPACE", 880, 520, RED, a, 22)
        tag(ctx, "AND BACK", 960, 1030, RED, a, 22)
    # beat 5: hover
    a = bw(t, 4)
    if a > 0:
        straight_arrow(ctx, RX + 230, 1180, RX + 230, 900, RED, a, lw=12, head=22)
        tag(ctx, "THRUST", RX + 230, 1230, RED, a, 24)
        tag(ctx, "TAIL FIRST", RX - 250, 1300, INK, a, 24)
    # beat 6: chopsticks
    a = bw(t, 5)
    if a > 0:
        tag(ctx, "CHOPSTICKS", RX, ya + 100, DISC, a, 26)
        k = ease(clamp((t - B(5) - 2.8) / 1.4))
        topview(ctx, 210, 1110, k, a)
        if t < B(5) + 2.8:
            straight_arrow(ctx, RX + 300, ya + 120, RX + 300, ya - 60, DISC, a, lw=8, head=16)
    # beat 7: pins
    a = bw(t, 6)
    if a > 0:
        for sx in (-1, 1):
            highlight(ctx, RX + sx * (HW + 15), Y_PIN + dy, 46, 34, RED, a, t)
        tag(ctx, "CATCH PIN", RX + 250, Y_PIN + dy - 80, RED, a, 26)
        tag(ctx, "NO LEGS", RX - 250, 1180, RED, a, 26)
    # beat 8: heavy parts stay down
    a = bw(t, 7)
    if a > 0:
        highlight(ctx, RX, 1000, 200, 470, TEAL, a, t)
        tag(ctx, "HEAVY · STRONG", RX + 290, 1300, TEAL, a, 24)
        tag(ctx, "STAYS ON THE GROUND", RX + 230, 1380, TEAL, a, 24)
    # beat 9: weight on the pins, arms push back
    a = win(t, B(8) + 1.4, B(9), 0.3)
    if a > 0:
        for sx in (-1, 1):
            x = RX + sx * (HW + 15)
            straight_arrow(ctx, x + sx * 70, Y_PIN - 150, x + sx * 70, ya - 10, RED, a, lw=8, head=16)
            straight_arrow(ctx, x + sx * 70, ya + 160, x + sx * 70, ya + 44, TEAL, a, lw=8, head=16)
        tag(ctx, "WEIGHT", RX + 300, Y_PIN - 190, RED, a, 24)
        tag(ctx, "ARMS HOLD", RX + 300, ya + 200, TEAL, a, 24)
    a = win(t, B(8) + 0.3, B(8) + 1.4, 0.25)
    tag(ctx, "ENGINES OFF", RX, 1400, RED, a, 26)
    # beat 11: lift
    a = bw(t, 10)
    if a > 0:
        straight_arrow(ctx, RX + 300, 760 + dy, RX + 300, 560 + dy, TEAL, a, lw=10, head=20)
        tag(ctx, "LIFT · RESTACK", RX + 300, 810 + dy, TEAL, a, 24)
    # beat 12: recap
    a = bw(t, 11, 12)
    if a > 0:
        tag(ctx, "LEGS IN SPACE = DEAD WEIGHT", RX, 1395, RED, a, 24)
        tag(ctx, "TOWER ON THE GROUND = FREE", RX, 250, TEAL, a, 24)

def state(t):
    s = {}
    s['dy'] = ship_dy(t)
    s['ya'], s['gap'] = arms(t)
    s['eng'] = engines(t)
    s['legs'] = legs_k(t) + bw(t, 11, 12) * 0.0
    return s

def draw_set(ctx):
    g = cairo.LinearGradient(0, 0, 0, Y_GROUND)
    g.add_color_stop_rgb(0, *SKY1[:3]); g.add_color_stop_rgb(1, *SKY2[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, Y_GROUND); ctx.fill()
    ctx.rectangle(0, Y_GROUND, W, 40); setc(ctx, FILL3); ctx.fill()
    ctx.move_to(0, Y_GROUND); ctx.line_to(W, Y_GROUND); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()

def draw(ctx, t, E):
    s = state(t)
    ta = tower_a(t)
    tower(ctx, ta, hot=bw(t, 7) * 0.6)
    arm_a = ta
    carriage(ctx, s['ya'], arm_a)
    ship(ctx, t, s['dy'], s['eng'], s['legs'], pin_hot=bw(t, 6))
    arm_beams(ctx, s['ya'], s['gap'], arm_a)
    overlays(ctx, t, s)

CAMKEYS = [(0, 540, 900, 0.95), (B(1) + 0.2, 540, 900, 1.0),
           (B(2) + 0.1, 540, 920, 1.0), (B(4) + 0.1, 540, 900, 1.0),
           (B(5) + 0.1, 540, 800, 1.05), (B(6) + 0.1, 540, 620, 1.35), (B(7) + 0.1, 540, 900, 1.0),
           (B(8) + 0.1, 540, 720, 1.2), (B(10) + 0.1, 540, 820, 1.0), (B(11) + 0.1, 540, 900, 0.95)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)
ANCHOR = (540, 1500)

def draw_hud(ctx, t, E):
    a = bw(t, 0)
    if a > 0 and t > 2.2: hud(ctx, "STARSHIP FLIGHT 15", "14 NOV", "back from orbit, caught", a, TEAL, x=630, y=196, w=420)

SFX = [(1.0, 'click'), (1.6, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.4, 'pop'), (B(4) + 0.4, 'pop'),
       (B(5) + 0.4, 'pop'), (B(5) + 3.0, 'click'), (B(6) + 0.3, 'pop'), (B(7) + 0.3, 'pop'),
       (B(8) + 1.5, 'click'), (B(10) + 0.5, 'pop'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_cargo(ctx, t, lt, a):
    card_frame(ctx, "THE UPPER STAGE'S BUDGET", a, "1 KG OF LEGS = 1 KG LESS CARGO", RED)
    # a balance: cargo box shrinks as a red leg block grows, total fixed
    k = ease(clamp((lt - 0.4) / 1.2))
    total = 600
    lw_ = lerp(0, 220, k)
    x0 = 190
    rrect(ctx, x0, 330, total - lw_, 130, 10); fill_stroke(ctx, TEAL_L, lw=4, alpha=a)
    text_c(ctx, "CARGO", x0 + (total - lw_) / 2, 408, 34, INK, True, 2, a)
    if lw_ > 4:
        rrect(ctx, x0 + total - lw_ + 10, 330, lw_ - 10, 130, 10); fill_stroke(ctx, lerpc(SHELL_C, RED, 0.3), lw=4, alpha=a)
        text_c(ctx, "LEGS", x0 + total - lw_ / 2 + 5, 408, 30, RED, True, 2, a * k)
    ctx.move_to(x0, 490); ctx.line_to(x0 + total, 490); setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
    for x in (x0, x0 + total):
        ctx.move_to(x, 478); ctx.line_to(x, 502); ctx.stroke()
    text_c(ctx, "WHAT IT CAN LIFT", x0 + total / 2, 530, 22, INK2, True, 1, a)

SHELL_C = hexc('#d9d4cb')

def satellite_icon(ctx, cx, cy, s, a=1.0):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    rrect(ctx, -26, -30, 52, 56, 6); fill_stroke(ctx, MUSTARD, lw=3, alpha=a)
    for sx in (-1, 1):
        ctx.rectangle(sx * 30 - (12 if sx < 0 else 0), -26, 12, 48); fill_stroke(ctx, TEAL, lw=2, alpha=a)
    ctx.restore()

def card_trip(ctx, t, lt, a):
    card_frame(ctx, "LANDS WHERE IT LAUNCHES", a, "NO TRIP HOME", TEAL)
    # left: a barge + a truck, crossed out ; right: tower + pad, ticked
    bx, by = 300, 420
    ctx.move_to(bx - 140, by); ctx.line_to(bx + 140, by); ctx.line_to(bx + 110, by + 50); ctx.line_to(bx - 110, by + 50)
    ctx.close_path(); fill_stroke(ctx, SHELL_C, lw=4, alpha=a)
    for i in range(3):
        ctx.move_to(bx - 170 + i * 40, by + 75); ctx.curve_to(bx - 160 + i * 40, by + 65, bx - 150 + i * 40, by + 85, bx - 140 + i * 40, by + 75)
    setc(ctx, TEAL, a); ctx.set_line_width(3); ctx.stroke()
    rrect(ctx, bx - 40, by - 90, 80, 90, 6); fill_stroke(ctx, STEEL, lw=3, alpha=a)
    text_c(ctx, "BARGE · TRUCK · DAYS", bx, 310, 24, INK2, True, 1, a)
    if lt > 0.9:
        b = ease(clamp((lt - 0.9) / 0.4))
        ctx.move_to(bx - 150, 330); ctx.line_to(bx + 150, 510); ctx.move_to(bx + 150, 330); ctx.line_to(bx - 150, 510)
        setc(ctx, RED, a * b); ctx.set_line_width(8); ctx.stroke()
    # right: tower + ship on the same spot
    tx = 760
    ctx.rectangle(tx - 70, 280, 50, 230); fill_stroke(ctx, TOWER, lw=3, alpha=a)
    ctx.rectangle(tx - 20, 300, 60, 14); fill_stroke(ctx, MUSTARD, lw=2, alpha=a)
    rrect(ctx, tx, 290, 30, 200, 12); fill_stroke(ctx, STEEL, lw=3, alpha=a)
    ctx.move_to(tx - 110, 510); ctx.line_to(tx + 110, 510); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    if lt > 1.4:
        b = ease(clamp((lt - 1.4) / 0.4))
        ctx.move_to(tx + 60, 400); ctx.line_to(tx + 85, 430); ctx.line_to(tx + 130, 360)
        setc(ctx, TEAL, a * b); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

CARDS = {'cargo': card_cargo, 'trip': card_trip}
