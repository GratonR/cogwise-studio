"""Cogwise episode: Why cars struggle to start in the cold  (lead-acid battery + starter motor + cold oil)

Stage (face-on view from the gearbox side, simplified):
  BATTERY bottom-left  -> big red cable up the left -> SOLENOID (on top of the STARTER MOTOR)
  KEY top-left         -> thin wire -> solenoid "S" terminal
  STARTER pinion (tiny gear, right end of the starter) slides RIGHT into the FLYWHEEL ring gear.
  Flywheel / crankshaft centre-right, engine block behind it, OIL PAN below, ALTERNATOR bottom-right.
Screen frame: y grows DOWNWARD; cairo angles increase CLOCKWISE on screen.
  - pinion turns CLOCKWISE  (theta increases)
  - ring gear / crankshaft turn COUNTER-CLOCKWISE (seen from the flywheel side, engines turn CCW)
  - resistance arrows on the crank point CLOCKWISE (they oppose the CCW cranking)
  - key turns CLOCKWISE to START
Units: SI first, US equivalent next to it (-18 °C = 0 °F, 0 °C = 32 °F, 20 °C = 68 °F).
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="cold-start-battery-starter",
    title="Why your car struggles to start in the cold ❄️",
    description=("At -18 °C (0 °F) your battery has lost about half its power, and cold oil makes the engine "
                 "harder to turn. The double squeeze, explained.\n\n#Shorts #howthingswork #cars #winter #battery #cogwise"),
    hashtags=["Shorts", "howthingswork", "cars", "winter", "battery", "mechanic", "cogwise"],
    sources=[
        "https://www.alldata.com/diy-us/en/why-batteries-die-in-winter",
        "https://uniquecarsandparts.com.au/how_it_works_starter_motor",
    ],
)

BEATS = [
    dict(dur=7.0, title="WHY WON'T IT START?", caption="At minus eighteen Celsius, zero Fahrenheit, your battery has lost half its punch. And your engine wants more."),
    dict(dur=5.0, title="THE SECRET: A DOUBLE SQUEEZE", caption="Starting a car is a tug of war: power supplied versus power demanded."),
    dict(dur=5.0, title=None, caption="A battery makes current by a chemical reaction, and cold slows it down.", card='chem'),
    dict(dur=6.5, title="1 · THE BATTERY", caption="At zero Celsius, thirty-two Fahrenheit, it gives about twenty percent less. At minus eighteen, nearly half."),
    dict(dur=4.5, title="2 · THE KEY", caption="Turn the key, and a small current wakes the starter's solenoid."),
    dict(dur=5.5, title="3 · THE SOLENOID", caption="The solenoid pushes a tiny gear into the flywheel, then closes the big contact."),
    dict(dur=4.5, title="4 · THE STARTER MOTOR", caption="Now the starter motor gulps around four hundred and fifty amps."),
    dict(dur=5.5, title=None, caption="The little gear spins ten to fifteen times for each engine turn, multiplying its force.", card='gears'),
    dict(dur=5.0, title="5 · THICK OIL", caption="But cold oil turns thick, like honey, so the crankshaft fights back."),
    dict(dur=4.5, title=None, caption="Less power in, more effort needed. That's the double squeeze.", card='squeeze'),
    dict(dur=4.5, title="VOLTAGE DIP", caption="A weak battery sags so low that the solenoid only clicks."),
    dict(dur=5.5, title="IT STARTS!", caption="Once the engine fires, a one-way clutch lets go, and the little gear springs back."),
    dict(dur=4.0, title="THE ALTERNATOR", caption="Then the alternator refills the battery while you drive."),
    dict(dur=4.5, title="COLD = WEAK BATTERY + THICK OIL", caption="So cold weakens the battery, and thickens the oil it has to fight."),
    dict(dur=5.0, title="TECH TIP", caption="Tech tip: crank ten seconds max, then let the battery rest thirty seconds."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette extras
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); STEEL_L = hexc('#e3e7ea')
COPPER = hexc('#c87533'); GREEN = hexc('#4c9d6b'); ICE = hexc('#cfe9f2'); ICE_D = hexc('#7fb9cc')
OIL_W = hexc('#e8a93a'); OIL_C = hexc('#6b4a1e'); CASE = hexc('#3d3a42'); BLOCK = hexc('#ddd0b4')
CABLE = RED; GROUND = INK

# ---------------------------------------------------------------- geometry
FW = (690, 780)                   # flywheel / crankshaft centre
RING_RO, RING_RI, RING_T = 226, 214, 100
PIN_RO, PIN_RI, PIN_T = 28, 16, 10   # 10 x fewer teeth -> 10:1, same tooth pitch
MESH_A = math.radians(130)        # direction from flywheel centre to the engaged pinion (down-left)
CDIST = (RING_RO + RING_RI) / 2 + (PIN_RO + PIN_RI) / 2   # 242
PIN_ENG = (FW[0] + CDIST * math.cos(MESH_A), FW[1] + CDIST * math.sin(MESH_A))   # (534, 965)
AXIS_Y = PIN_ENG[1]
PIN_X_OUT = PIN_ENG[0] - 40       # retracted (clear of the ring teeth)
STARTER = (262, AXIS_Y - 40, 208, 80)      # x, y, w, h
SOL = (292, AXIS_Y - 98, 178, 56)         # solenoid on top of the starter
BAT = (70, 1215, 260, 235)
POS = (125, 1192); NEG = (275, 1192)
KEY = (310, 712)
THERMO = (112, 560)               # bulb centre
ALT = (942, 1088)
RED_PATH = [(POS[0], POS[1]), (POS[0], SOL[1] + SOL[3] / 2), (SOL[0], SOL[1] + SOL[3] / 2)]
KEY_PATH = [(KEY[0], KEY[1] + 42), (KEY[0], 780), (400, 780), (400, SOL[1])]
ALT_PATH = [(ALT[0], ALT[1] + 45), (ALT[0], 1145), (POS[0], 1145), (POS[0], POS[1])]
GND_PATH = [(NEG[0], NEG[1]), (NEG[0], 1172), (530, 1172), (530, 1160)]

# ---------------------------------------------------------------- timeline helpers
def temp_c(t):
    """Air temperature shown on the thermometer (°C)."""
    T = lerp(20, -18, ease((t - 0.6) / 2.2))
    if t >= B(3):   # beat 3 replays the curve: 0 °C, then -18 °C
        u1 = ease((t - B(3) - 0.2) / 0.7); u2 = ease((t - B(3) - 3.0) / 0.9)
        T = lerp(lerp(-18, 0, u1), -18, u2)
    return T

def c_to_f(c): return c * 9 / 5 + 32

def capacity(T):
    """Share of the battery's warm power available (ALLDATA: ~-20 % at 0 °C, ~-40/50 % at -18 °C)."""
    if T >= 0: return lerp(0.8, 1.0, min(T, 20) / 20)
    return lerp(0.8, 0.55, min(-T, 18) / 18)

def engaged(t):
    e = ease((t - B(5) - 0.4) / 0.9)
    return e * (1 - ease((t - B(11) - 2.0) / 0.7))

def contact(t):
    return ease((t - B(5) - 2.6) / 0.3) * (1 - ease((t - B(11) - 1.8) / 0.3))

def pin_speed(t):
    """Pinion angular speed (rad/s, + = clockwise)."""
    w = 0.0
    w += 9.0 * ease((t - B(6) - 0.2) / 0.6)                 # starter spins
    w -= 4.0 * ease((t - B(8) - 0.6) / 1.2)                 # thick oil fights back
    w -= 5.0 * ease((t - B(10) - 0.3) / 0.4)                # voltage dip: only a click
    w += 7.0 * ease((t - B(11) - 0.1) / 0.4)                # cranks again
    w -= 9.0 * ease((t - B(11) - 2.0) / 0.8)                # released, spins down
    return max(w, 0.0)

def ring_speed(t):
    """Ring/crank angular speed (rad/s, + = counter-clockwise)."""
    driven = pin_speed(t) / 10.0 * engaged(t)
    fired = ease((t - B(11) - 1.2) / 0.5) * 3.2
    return max(driven, fired)

def _integrate(fn, t, dt=0.04):
    a, x = 0.0, 0.0
    while x < t:
        a += fn(x) * dt; x += dt
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

def polyline(ctx, pts):
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)

# ---------------------------------------------------------------- state
def state(t):
    st = {}
    T = temp_c(t); st['T'] = T
    st['cold'] = clamp((10 - T) / 28)
    st['cap'] = capacity(T)
    st['key'] = 0.62 * ease((t - B(4) - 0.3) / 0.5) - 0.27 * ease((t - B(11) - 1.8) / 0.4)   # CW = +
    st['keyw'] = ease((t - B(4) - 0.6) / 0.4) * (1 - ease((t - B(11) - 1.8) / 0.3))
    st['eng'] = engaged(t)
    st['plunger'] = st['eng']
    st['contact'] = contact(t)
    st['pin_a'] = _integrate(pin_speed, t)
    st['ring_a'] = _integrate(ring_speed, t)
    st['pin_w'] = pin_speed(t)
    st['ring_w'] = ring_speed(t)
    flick = 0.55 + 0.45 * math.sin(t * 23)
    cur = st['contact'] * ease((t - B(6) - 0.1) / 0.4)
    cur *= 1 - 0.85 * win(t, B(10) + 0.3, B(11) + 0.1, 0.3)
    st['current'] = cur
    st['amps'] = bw(t, 6)
    st['oil_thick'] = st['cold'] * (0.4 + 0.6 * ease((t - B(8) - 0.3) / 1.2)) if t > B(8) else st['cold'] * 0.4
    st['resist'] = bw(t, 8, 10) + bw(t, 13, 14)
    st['volt'] = 1.0 - 0.35 * ease((t - B(6) - 0.3) / 0.6) * (1 - ease((t - B(11) + 0.0) / 1.5)) \
                 - 0.40 * win(t, B(10) + 0.3, B(11) + 0.1, 0.4) * flick
    st['vm'] = bw(t, 10, 11)
    st['click'] = win(t, B(10) + 0.9, B(11))
    st['fired'] = ease((t - B(11) - 1.2) / 0.5)
    st['charge'] = bw(t, 12) * st['fired']
    st['alt'] = ease((t - B(12) - 0.1) / 0.5)
    # highlights
    st['h_bat'] = bw(t, 3) + bw(t, 1) * 0.0 + bw(t, 13) + bw(t, 14)
    st['h_key'] = bw(t, 4)
    st['h_sol'] = bw(t, 5)
    st['h_sta'] = bw(t, 6)
    st['h_oil'] = bw(t, 8) + bw(t, 13)
    st['h_pin'] = win(t, B(11) + 1.3, B(12))
    st['h_alt'] = bw(t, 12)
    st['h_vm'] = bw(t, 10)
    st['sup'] = bw(t, 1); st['dem'] = bw(t, 1)
    return st

# ---------------------------------------------------------------- drawing
def snowflake(ctx, x, y, r, a, rot=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    for k in range(3):
        ctx.save(); ctx.rotate(k * math.pi / 3)
        ctx.move_to(-r, 0); ctx.line_to(r, 0)
        for s in (-1, 1):
            ctx.move_to(s * r * 0.55, 0); ctx.line_to(s * r * 0.8, -r * 0.22)
            ctx.move_to(s * r * 0.55, 0); ctx.line_to(s * r * 0.8, r * 0.22)
        ctx.restore()
    setc(ctx, ICE_D, a); ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.restore()

def draw_snow(ctx, t, st):
    a = st['cold']
    if a <= 0.05: return
    rnd = random.Random(7)
    for i in range(16):
        x = rnd.random() * 1080; sp = 25 + rnd.random() * 25
        y = 300 + ((rnd.random() * 1150 + t * sp) % 1150)
        snowflake(ctx, x + 12 * math.sin(t + i), y, 7 + rnd.random() * 6, a * 0.45, t * 0.5 + i)

def draw_thermo(ctx, t, st):
    x, yb = THERMO; h = 230; T = st['T']
    lvl = clamp((T + 30) / 60)      # scale -30..+30 °C
    col = lerpc(RED, COLD, st['cold'])
    rrect(ctx, x - 14, yb - h, 28, h, 14); fill_stroke(ctx, WHITE, lw=4)
    ctx.arc(x, yb + 8, 24, 0, 2*math.pi); fill_stroke(ctx, col, lw=4)
    hh = 20 + (h - 40) * lvl
    rrect(ctx, x - 6, yb - hh, 12, hh + 6, 6); setc(ctx, col); ctx.fill()
    for tc in (20, 0, -18):
        y = yb - (20 + (h - 40) * (tc + 30) / 60)
        ctx.move_to(x + 14, y); ctx.line_to(x + 26, y); ctx.move_to(x - 14, y); ctx.line_to(x - 26, y)
        setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
        font(ctx, 19, True); setc(ctx, INK)
        s = "%d °F" % round(c_to_f(tc)); ctx.move_to(x + 31, y + 7); ctx.show_text(s)
        s = "%d °C" % tc; w = ctx.text_extents(s).x_advance; ctx.move_to(x - 31 - w, y + 7); ctx.show_text(s)
    ctx.new_path()
    s = "%d °C · %d °F" % (round(T), round(c_to_f(T)))
    tag(ctx, s, x + 30, yb + 66, col, 1.0, 24)

def draw_battery(ctx, t, st):
    x, y, w, h = BAT
    rrect(ctx, x, y, w, h, 12); fill_stroke(ctx, CASE, lw=6)
    rrect(ctx, x - 6, y - 18, w + 12, 26, 8); fill_stroke(ctx, hexc('#55515b'), lw=5)
    for k in range(6):
        ctx.arc(x + 30 + k * 40, y - 5, 7, 0, 2*math.pi); setc(ctx, INK2); ctx.fill()
    # terminals
    for (px, py), c, s in ((POS, RED, "+"), (NEG, INK2, "–")):
        rrect(ctx, px - 16, py - 8, 32, 22, 4); fill_stroke(ctx, c, lw=4)
        text_c(ctx, s, px, y + 50, 34, WHITE)
    # power gauge
    cap = st['cap']
    gx, gy, gw, gh = x + 22, y + 72, w - 44, 40
    rrect(ctx, gx, gy, gw, gh, 8); fill_stroke(ctx, hexc('#55515b'), stroke=WHITE, lw=3)
    gc = GREEN if cap > 0.85 else (MUSTARD if cap > 0.68 else RED)
    rrect(ctx, gx + 5, gy + 5, (gw - 10) * cap, gh - 10, 5); setc(ctx, gc); ctx.fill()
    text_c(ctx, "POWER %d %%" % round(cap * 100), x + w / 2, gy + 82, 30, WHITE, True, 1.5)
    # frost on the lid
    fa = st['cold']
    if fa > 0.05:
        for k in range(9):
            fx = x - 4 + k * (w + 8) / 8
            ctx.move_to(fx - 14, y - 18); ctx.line_to(fx, y - 18 + 14 + 6 * (k % 2)); ctx.line_to(fx + 14, y - 18)
            ctx.close_path(); setc(ctx, ICE, fa * 0.95); ctx.fill()
        snowflake(ctx, x + w - 30, y + h - 34, 16, fa * 0.9)
    # voltmeter (beat 10)
    if st['vm'] > 0:
        a = st['vm']; vx, vy = x + w + 75, y + 120
        for tx_ in (POS[0], NEG[0]):
            ctx.move_to(vx, vy + 48); ctx.curve_to(vx, vy + 110, tx_ + 40, y + 20, tx_ + 12, POS[1] + 6)
            setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(vx, vy, 48, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=4, alpha=a)
        ctx.arc(vx, vy, 38, math.pi * 1.05, math.pi * 1.35); setc(ctx, RED, a); ctx.set_line_width(8); ctx.stroke()
        ctx.arc(vx, vy, 38, math.pi * 1.35, math.pi * 1.95); setc(ctx, GREEN, a); ctx.set_line_width(8); ctx.stroke()
        ang = math.pi * (1.05 + 0.9 * clamp(st['volt']))
        ctx.move_to(vx, vy); ctx.line_to(vx + 34*math.cos(ang), vy + 34*math.sin(ang))
        setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        ctx.arc(vx, vy, 5, 0, 2*math.pi); setc(ctx, INK, a); ctx.fill()
        text_c(ctx, "V", vx, vy + 32, 20, INK, True, 0, a)

def draw_cables(ctx, t, st):
    # ground strap
    polyline(ctx, GND_PATH); setc(ctx, GROUND); ctx.set_line_width(12); ctx.stroke()
    # alternator charge wire (appears with the alternator)
    if st['alt'] > 0:
        polyline(ctx, ALT_PATH); setc(ctx, RED, st['alt'] * 0.8); ctx.set_line_width(6)
        ctx.set_dash([16, 10]); ctx.stroke(); ctx.set_dash([])
    # main battery cable
    glow = st['current']
    polyline(ctx, RED_PATH); setc(ctx, INK); ctx.set_line_width(22); ctx.stroke()
    polyline(ctx, RED_PATH); setc(ctx, lerpc(hexc('#a8321f'), ORANGE, glow)); ctx.set_line_width(13); ctx.stroke()
    if glow > 0.05:
        for k in range(10):     # current: battery (+) -> solenoid -> motor
            px, py = path_point(RED_PATH, k / 10 + t * 0.9)
            ctx.arc(px, py, 5, 0, 2*math.pi); setc(ctx, WHITE, glow); ctx.fill()
    # key wire (thin)
    kw = st['keyw']
    polyline(ctx, KEY_PATH); setc(ctx, INK); ctx.set_line_width(7); ctx.stroke()
    polyline(ctx, KEY_PATH); setc(ctx, lerpc(INK2, MUSTARD, kw)); ctx.set_line_width(3); ctx.stroke()
    if kw > 0.05:
        for k in range(6):
            px, py = path_point(KEY_PATH, k / 6 + t * 0.6)
            ctx.arc(px, py, 4, 0, 2*math.pi); setc(ctx, MUSTARD, kw); ctx.fill()
    if st['charge'] > 0:
        for k in range(12):     # charge: alternator -> battery (+)
            px, py = path_point(ALT_PATH, k / 12 + t * 0.5)
            ctx.arc(px, py, 6, 0, 2*math.pi); setc(ctx, GREEN, st['charge']); ctx.fill()

def draw_key(ctx, t, st):
    x, y = KEY
    ctx.arc(x, y, 46, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=5)
    ctx.arc(x, y, 30, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=3)
    for lab, ang in (("OFF", -2.4), ("ON", -1.4), ("START", -0.6)):
        font(ctx, 17, True); w = ctx.text_extents(lab).x_advance
        ctx.move_to(x + 66*math.cos(ang) - w/2, y + 66*math.sin(ang) + 6); setc(ctx, INK); ctx.show_text(lab)
    ctx.new_path()
    ctx.save(); ctx.translate(x, y); ctx.rotate(-2.4 + math.pi/2 + st['key'] * (1.8 / 0.62))
    # key blade along local -y (points to the position label), bow at +y side
    rrect(ctx, -6, -40, 12, 50, 3); fill_stroke(ctx, MUSTARD, lw=3)
    ctx.arc(0, 18, 14, 0, 2*math.pi); fill_stroke(ctx, MUSTARD, lw=3)
    ctx.restore()

def draw_block(ctx, t, st):
    rrect(ctx, 520, 450, 490, 715, 24); fill_stroke(ctx, BLOCK, lw=6)
    for bx, by in ((560, 490), (970, 490), (560, 1125), (970, 1125)):
        ctx.arc(bx, by, 11, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=3)
    # oil pan + oil
    ctx.move_to(600, 1165); ctx.line_to(920, 1165); ctx.line_to(900, 1300); ctx.line_to(620, 1300); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=6)
    th = st['oil_thick']
    oc = lerpc(OIL_W, OIL_C, th)
    amp = 7 * (1 - th) + 1; spd = 4 * (1 - th) + 0.3
    ctx.save()
    ctx.move_to(600, 1165); ctx.line_to(920, 1165); ctx.line_to(900, 1300); ctx.line_to(620, 1300); ctx.close_path(); ctx.clip()
    ctx.move_to(590, 1300)
    for i in range(41):
        xx = 590 + i * 8.5
        ctx.line_to(xx, 1225 + amp * math.sin(xx / 30 + t * spd))
    ctx.line_to(930, 1310); ctx.line_to(590, 1310); ctx.close_path(); setc(ctx, oc); ctx.fill()
    if th > 0.3:   # thick, honey-like folds
        for k in range(3):
            xx = 650 + k * 90
            ctx.move_to(xx, 1245); ctx.curve_to(xx + 20, 1255, xx + 40, 1255, xx + 60, 1245)
            setc(ctx, hexc('#4a3214'), th); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def draw_flywheel(ctx, t, st):
    cx, cy = FW
    ra = -st['ring_a']           # CCW on screen
    c_r = MESH_A - 2*math.pi*0.375/RING_T
    gear(ctx, cx, cy, RING_RO, RING_RI, RING_T, 0.01, STEEL_D, lw=3, rot=ra + c_r)
    ctx.arc(cx, cy, RING_RI - 8, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=5)
    for k in range(6):
        a = ra + k * math.pi / 3
        ctx.arc(cx + 140*math.cos(a), cy + 140*math.sin(a), 18, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=3)
    # crank hub
    ctx.arc(cx, cy, 78, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=5)
    for k in range(6):
        a = ra + k * math.pi / 3 + 0.5
        ctx.arc(cx + 52*math.cos(a), cy + 52*math.sin(a), 8, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=2)
    ctx.arc(cx, cy, 22, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=4)
    # paint mark (shows the rotation)
    ctx.arc(cx + 185*math.cos(ra - 1.2), cy + 185*math.sin(ra - 1.2), 10, 0, 2*math.pi); setc(ctx, MUSTARD); ctx.fill()
    # motion arcs, counter-clockwise (arrow head at the decreasing-angle end)
    w = st['ring_w']
    if w > 0.15:
        a_ = clamp(w / 1.0)
        for k in range(2):
            a0 = ra * 0.0 - 0.6 + k * math.pi
            ctx.arc_negative(cx, cy, 252, a0 + 0.9, a0)
            setc(ctx, INK2, 0.6 * a_); ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
            hx, hy = cx + 252*math.cos(a0), cy + 252*math.sin(a0)
            tx, ty = math.sin(a0), -math.cos(a0)     # tangent for decreasing angle
            ctx.move_to(hx + tx*16, hy + ty*16)
            ctx.line_to(hx - ty*10, hy + tx*10); ctx.line_to(hx + ty*10, hy - tx*10); ctx.close_path()
            setc(ctx, INK2, 0.6 * a_); ctx.fill()
    # resistance (clockwise, opposing the crank)
    r = st['resist']
    if r > 0:
        for k in range(2):
            a0 = -2.4 + k * math.pi
            a1 = a0 + 1.3
            ctx.arc(cx, cy, 104, a0, a1)
            setc(ctx, RED, r); ctx.set_line_width(8); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
            hx, hy = cx + 104*math.cos(a1), cy + 104*math.sin(a1)
            tx, ty = -math.sin(a1), math.cos(a1)       # tangent for increasing angle (clockwise)
            ctx.move_to(hx + tx*22, hy + ty*22)
            ctx.line_to(hx - ty*14, hy + tx*14); ctx.line_to(hx + ty*14, hy - tx*14); ctx.close_path()
            setc(ctx, RED, r); ctx.fill()

def draw_starter(ctx, t, st):
    x, y, w, h = STARTER
    e = st['eng']
    px = lerp(PIN_X_OUT, PIN_ENG[0], e)
    # shaft
    ctx.move_to(x + w, AXIS_Y); ctx.line_to(px, AXIS_Y); setc(ctx, INK); ctx.set_line_width(10); ctx.stroke()
    # motor body
    rrect(ctx, x, y, w, h, 14); fill_stroke(ctx, hexc('#7d8a96'), lw=5)
    ctx.save(); rrect(ctx, x + 30, y + 8, w - 60, h - 16, 6); ctx.clip()
    setc(ctx, COPPER); ctx.paint()
    off = (st['pin_a'] * 14) % 22
    for k in range(-1, 10):
        xx = x + 30 + k * 22 + off
        ctx.move_to(xx, y); ctx.line_to(xx - 10, y + h); setc(ctx, hexc('#8a4d1d')); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()
    rrect(ctx, x + 30, y + 8, w - 60, h - 16, 6); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    # solenoid
    sx, sy, sw, sh = SOL
    rrect(ctx, sx, sy, sw, sh, 12); fill_stroke(ctx, STEEL_L, lw=5)
    ctx.save(); rrect(ctx, sx + 14, sy + 8, 80, sh - 16, 4); ctx.clip()
    setc(ctx, COPPER); ctx.paint()
    for k in range(9):
        ctx.move_to(sx + 14 + k * 10, sy); ctx.line_to(sx + 14 + k * 10, sy + sh); setc(ctx, hexc('#8a4d1d')); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()
    pl = st['plunger']
    plx = sx + 60 + 26 * pl
    rrect(ctx, plx, sy + 14, 50, sh - 28, 4); fill_stroke(ctx, STEEL_D, lw=3)
    # main contact: copper bridge closes onto the two studs at the right end
    c = st['contact']
    for yy in (sy + 8, sy + sh - 14):
        rrect(ctx, sx + sw - 18, yy, 12, 6, 2); setc(ctx, COPPER); ctx.fill()
    bx = lerp(sx + sw - 40, sx + sw - 30, c)
    rrect(ctx, bx, sy + 6, 10, sh - 12, 3); fill_stroke(ctx, lerpc(COPPER, ORANGE, c), lw=2)
    if c > 0.5:
        for k in range(4):
            a = t * 9 + k * 1.6
            ctx.move_to(sx + sw - 12, sy + sh / 2)
            ctx.line_to(sx + sw - 12 + 14*math.cos(a), sy + sh / 2 + 14*math.sin(a))
            setc(ctx, MUSTARD, 0.8 * (c - 0.5) * 2); ctx.set_line_width(3); ctx.stroke()
    # S terminal (key wire) on top
    rrect(ctx, 393, sy - 10, 14, 12, 3); setc(ctx, INK); ctx.fill()
    # shift fork: from plunger down to the pinion collar
    fx_top = plx + 50
    ctx.move_to(fx_top, sy + sh / 2); ctx.line_to(sx + sw + 4, sy + sh / 2 + 4)
    ctx.line_to(px - 22, AXIS_Y - 20)
    setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()
    # one-way clutch collar
    rrect(ctx, px - 30, AXIS_Y - 18, 14, 36, 4); fill_stroke(ctx, MUSTARD, lw=3)
    # pinion (clockwise)
    c_p = MESH_A + math.pi - 2*math.pi*0.875/PIN_T
    gear(ctx, px, AXIS_Y, PIN_RO, PIN_RI, PIN_T, 5, STEEL_L, lw=3, rot=st['pin_a'] + c_p)
    if st['pin_w'] > 1.0:
        ctx.arc(px, AXIS_Y, 40, -0.4, 0.8)
        setc(ctx, INK2, 0.6); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        hx, hy = px + 40*math.cos(0.8), AXIS_Y + 40*math.sin(0.8)
        tx, ty = -math.sin(0.8), math.cos(0.8)
        ctx.move_to(hx + tx*12, hy + ty*12); ctx.line_to(hx - ty*8, hy + tx*8); ctx.line_to(hx + ty*8, hy - tx*8)
        ctx.close_path(); setc(ctx, INK2, 0.6); ctx.fill()

def draw_alternator(ctx, t, st):
    a = st['alt']
    if a <= 0: return
    x, y = ALT
    ang = _integrate(ring_speed, t) * 2.5
    ctx.push_group()
    ctx.arc(x, y, 46, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=5)
    for k in range(10):
        aa = ang + k * math.pi / 5
        ctx.move_to(x + 18*math.cos(aa), y + 18*math.sin(aa)); ctx.line_to(x + 38*math.cos(aa + 0.3), y + 38*math.sin(aa + 0.3))
        setc(ctx, INK2); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(x, y, 14, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=3)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

def draw(ctx, t, E):
    st = state(t)
    draw_snow(ctx, t, st)
    draw_block(ctx, t, st)
    draw_cables(ctx, t, st)
    draw_flywheel(ctx, t, st)
    draw_alternator(ctx, t, st)
    draw_starter(ctx, t, st)
    draw_battery(ctx, t, st)
    draw_key(ctx, t, st)
    draw_thermo(ctx, t, st)
    # highlights
    highlight(ctx, 200, 1330, 175, 165, TEAL, max(st['h_bat'], st['sup']), t)
    highlight(ctx, *KEY, 85, 85, MUSTARD, st['h_key'], t)
    highlight(ctx, 410, SOL[1] + SOL[3]/2 + 10, 125, 60, ORANGE, st['h_sol'], t)
    highlight(ctx, 410, AXIS_Y - 10, 150, 95, RED, st['h_sta'], t)
    highlight(ctx, 760, 1235, 190, 95, OIL_C, st['h_oil'], t)
    highlight(ctx, 690, 780, 270, 270, RED, st['dem'], t)
    highlight(ctx, *PIN_ENG, 70, 60, GREEN, st['h_pin'], t)
    highlight(ctx, *ALT, 80, 80, GREEN, st['h_alt'], t)
    # tags
    tag(ctx, "POWER SUPPLIED", 200, 1095, TEAL, st['sup'])
    tag(ctx, "POWER DEMANDED", 765, 405, RED, st['dem'])
    tag(ctx, "1 · BATTERY", 200, 1095, TEAL, bw(t, 3))
    tag(ctx, "2 · KEY", 450, 712, MUSTARD, st['h_key'])
    tag(ctx, "3 · SOLENOID", 410, 1045, ORANGE, st['h_sol'])
    tag(ctx, "4 · STARTER MOTOR", 420, 1045, RED, st['h_sta'])
    tag(ctx, "≈ 450 A", 205, 975, RED, st['amps'], 28)
    tag(ctx, "5 · THICK OIL", 760, 1355, OIL_C, bw(t, 8))
    tag(ctx, "CRANKSHAFT FIGHTS BACK", 690, 620, RED, win(t, B(8) + 1.4, B(9)))
    tag(ctx, "CLICK… NO CRANK", 690, 620, RED, st['click'], 28)
    tag(ctx, "ENGINE RUNS ON ITS OWN", 690, 620, GREEN, win(t, B(11) + 1.3, B(12)))
    tag(ctx, "ONE-WAY CLUTCH LETS GO", 420, 1045, GREEN, win(t, B(11) + 1.6, B(12)), 24)
    tag(ctx, "ALTERNATOR", 900, 1010, GREEN, st['h_alt'])
    tag(ctx, "CHARGING", 200, 1095, GREEN, st['charge'])
    tag(ctx, "WEAK BATTERY", 200, 1095, TEAL, bw(t, 13))
    tag(ctx, "THICK OIL", 760, 1355, OIL_C, bw(t, 13))
    tag(ctx, "CRANK 10 s MAX", 690, 620, INK, bw(t, 14), 28)
    tag(ctx, "THEN REST 30 s", 690, 690, GREEN, win(t, B(14) + 1.6, B(15)), 28)

SFX = [(B(1) + 0.3, 'whoosh'), (B(3) + 0.2, 'pop'), (B(4) + 0.3, 'click'), (B(4) + 0.4, 'pop'),
       (B(5) + 0.2, 'pop'), (B(5) + 2.6, 'click'), (B(6) + 0.2, 'pop'), (B(8) + 0.2, 'pop'),
       (B(10) + 0.9, 'click'), (B(11) + 1.6, 'click'), (B(12) + 0.2, 'pop'), (B(13) + 0.2, 'pop'), (B(14) + 0.2, 'pop')]
HUM = [(B(6) + 0.2, B(10) + 0.3), (B(11) + 0.1, B(15))]

def draw_set(ctx):
    pass

# ---------------------------------------------------------------- cards
def card_chem(ctx, t, lt, a):
    card_frame(ctx, "LEAD + ACID = CURRENT", a, "COLD = SLOWER REACTION = LESS CURRENT", COLD)
    for i, (lab, spd, col) in enumerate((("WARM · 25 °C / 77 °F", 1.0, ORANGE), ("COLD · -18 °C / 0 °F", 0.3, COLD))):
        ox = 150 + i * 420
        rrect(ctx, ox, 260, 360, 230, 14); fill_stroke(ctx, hexc('#fff6dc'), lw=4, alpha=a)
        rrect(ctx, ox + 40, 285, 26, 180, 4); fill_stroke(ctx, hexc('#7d7a84'), lw=3, alpha=a)     # Pb plate
        rrect(ctx, ox + 294, 285, 26, 180, 4); fill_stroke(ctx, hexc('#8a5a3a'), lw=3, alpha=a)    # PbO2 plate
        rnd = random.Random(4 + i)
        for k in range(14):
            u = (rnd.random() + lt * 0.35 * spd) % 1.0
            xx = ox + 75 + u * 210; yy = 295 + rnd.random() * 160
            ctx.arc(xx, yy, 7, 0, 2*math.pi); setc(ctx, col, a); ctx.fill()
        if i == 1:
            snowflake(ctx, ox + 180, 300, 18, a)
        text_c(ctx, lab, ox + 180, 520, 24, col, True, 1, a)

def card_gears(ctx, t, lt, a):
    card_frame(ctx, "GEAR REDUCTION", a, "PINION ≈ 10–15 TURNS = 1 ENGINE TURN", RED)
    ctx.push_group(); ctx.save(); rrect(ctx, 100, 240, 880, 300, 10); ctx.clip()
    # flywheel ring (only its top-left arc shows): counter-clockwise, slow
    cx, cy, R = 905, 455, 300
    ma = math.pi                                   # direction ring centre -> pinion
    px, py = cx + 333*math.cos(ma), cy + 333*math.sin(ma)
    wpin = lt * 3.0
    gear(ctx, cx, cy, R + 9, R - 9, 100, 0.01, STEEL_D, lw=3, rot=-wpin/10 + ma - 2*math.pi*0.375/100)
    ctx.arc(cx, cy, R - 20, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=4)
    mk = -wpin/10 + 3.4
    ctx.arc(cx + 230*math.cos(mk), cy + 230*math.sin(mk), 14, 0, 2*math.pi); setc(ctx, MUSTARD); ctx.fill()
    # pinion: clockwise, fast (10 teeth vs 100 -> 10:1)
    gear(ctx, px, py, 42, 24, 10, 7, STEEL_L, lw=4, rot=wpin + ma + math.pi - 2*math.pi*0.875/10)
    ctx.arc(px, py, 6, 0, 2*math.pi); setc(ctx, INK); ctx.fill()
    ctx.restore(); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    # rotation arrows: pinion clockwise (left side, going up), ring counter-clockwise
    def arc_arrow(x, y, r, a0, a1, col):
        if a1 > a0: ctx.arc(x, y, r, a0, a1)
        else: ctx.arc_negative(x, y, r, a0, a1)
        setc(ctx, col, a); ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        sgn = 1 if a1 > a0 else -1
        hx, hy = x + r*math.cos(a1), y + r*math.sin(a1)
        tx, ty = -math.sin(a1)*sgn, math.cos(a1)*sgn
        ctx.move_to(hx + tx*14, hy + ty*14); ctx.line_to(hx - ty*9, hy + tx*9); ctx.line_to(hx + ty*9, hy - tx*9)
        ctx.close_path(); setc(ctx, col, a); ctx.fill()
    arc_arrow(px, py, 64, 2.2, 4.1, RED)            # clockwise over the left/top of the pinion
    arc_arrow(cx, cy, 340, math.pi + 0.62, math.pi + 0.32, INK2)   # counter-clockwise: left edge moves down
    text_c(ctx, "PINION · FAST", 330, 350, 26, RED, True, 1, a)
    text_c(ctx, "FLYWHEEL · SLOW, STRONG", 800, 520, 22, INK, True, 1, a)

def card_squeeze(ctx, t, lt, a):
    card_frame(ctx, "THE DOUBLE SQUEEZE", a, "LESS POWER IN · MORE EFFORT NEEDED", RED)
    u = ease((lt - 0.4) / 1.6)
    # supply bar shrinks, demand bar grows
    for i, (lab, v0, v1, col) in enumerate((("BATTERY POWER", 1.0, 0.55, TEAL), ("ENGINE DEMAND", 0.6, 1.0, RED))):
        y = 290 + i * 120
        text_c(ctx, lab, 300, y + 32, 26, col, True, 1, a)
        rrect(ctx, 450, y, 460, 50, 10); fill_stroke(ctx, WHITE, lw=4, alpha=a)
        rrect(ctx, 456, y + 6, 448 * lerp(v0, v1, u), 38, 7); setc(ctx, col, a); ctx.fill()

CARDS = {'chem': card_chem, 'gears': card_gears, 'squeeze': card_squeeze}
