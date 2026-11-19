"""Cogwise episode: Your freezer turns on a heater, a few times a day.
One idea: a frost-free freezer keeps making frost on its hidden evaporator; a few times a day a timer stops the cold,
a ~500 W heater under the coil melts the frost, a thermostat on the coil cuts it at ~5 °C, and the water drains to a
tray on the warm compressor where it evaporates.

VIEW (screen coordinates, y grows DOWN): SIDE SECTION of an upright freezer, FRONT (door) on the LEFT, back on the RIGHT.
  - door slab x 240-300; food compartment x 320-690, y 400-1290.
  - back wall panel x 690-712 hides the evaporator compartment x 712-840, y 400-1060.
  - fan at the TOP of that compartment (776, 478): it pulls air UP through the coil and blows it LEFT through the top
    grille into the food compartment; the air sinks along the food and comes back through the bottom return vent
    (y 1000-1050) -> air through the coil goes BOTTOM -> TOP.
  - coil (evaporator) x 726-826, y 545-945: tubes seen end-on (circles) between vertical fins; frost coats fins + tubes.
  - heater (glass tube) UNDER the coil y 966-984: heat rises UP into the coil.
  - defrost thermostat clipped on the coil outlet tube at the top right (812, 522).
  - drain trough under the heater (y 1000-1030) -> tube DOWN the back insulation (x 860) -> ends above the drain tray
    that sits ON the compressor dome (machine compartment bottom right, y 1310-1470). Water only goes DOWN.
  - defrost timer in the machine compartment (610, 1405).
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="freezer-defrost",
    title="Your freezer turns on a heater, a few times a day 🧊 #Shorts",
    description=("Behind the back wall of a frost-free freezer, a heater melts the frost a few times a day.\n\n"
                 "#Shorts #howthingswork #freezer #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "freezer", "appliances", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Auto-defrost",
        "https://products.geappliances.com/appliance/gea-support-search-content?contentId=16679",
        "https://www.manualslib.com/manual/1203663/Whirlpool-1997-F.html?page=12",
    ],
)

BEATS = [
    dict(dur=6.0, title="ON PURPOSE", caption="Your freezer turns on a heater. A few times a day. On purpose."),
    dict(dur=5.6, title="THE SECRET", caption="It hides behind the back wall, under a coil covered in frost."),
    dict(dur=5.6, title="THE COIL", caption="That coil is the evaporator, the part that actually makes the cold."),
    dict(dur=6.4, title="THE FROST", caption="Every time you open the door, moist air rushes in and freezes onto it."),
    dict(dur=6.8, title=None, caption="Frost insulates the coil and clogs its gaps. The fan can't push cold air through.", card='blocked'),
    dict(dur=5.6, title="1 · THE TIMER", caption="So a timer steps in. It stops the compressor and the fan."),
    dict(dur=5.6, title="2 · THE HEATER", caption="Then the heater under the coil switches on: around five hundred watts."),
    dict(dur=6.0, title="THE CUTOFF", caption="A small thermostat on the coil cuts it at five Celsius, forty-one Fahrenheit."),
    dict(dur=6.4, title="3 · THE DRAIN", caption="The melted frost runs down a tube into a tray sitting on the compressor."),
    dict(dur=4.8, title=None, caption="The compressor's warmth evaporates it, back into your kitchen air.", card='evaporate'),
    dict(dur=6.4, title="SURPRISE", caption="The whole defrost takes well under an hour, too short to thaw your food."),
    dict(dur=5.6, title="FROST-FREE", caption="Frost-free just means your freezer melts its own frost, on a schedule."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

STEEL = hexc('#9aa3ab'); STEEL_D = hexc('#6d757c')
FROST = hexc('#ffffff'); MOIST = hexc('#9fb3c8')
WATER = hexc('#8fcfc8'); BLUE = hexc('#2f6fb3')
INNER = hexc('#e6f1ef'); INSUL = hexc('#f2e6c9')
GLASS = hexc('#e9e4dc')

# ---------------------------------------------------------------- geometry
CX0, CX1, CY0, CY1 = 240, 880, 360, 1480     # cabinet
FX0, FX1, FY0, FY1 = 320, 690, 400, 1290     # food compartment
PX0, PX1 = 690, 712                          # back wall panel
EX0, EX1, EY0, EY1 = 712, 840, 400, 1060     # evaporator compartment
KX0, KX1, KY0, KY1 = 726, 826, 545, 945      # coil
FANC = (776, 478)
HY = 966                                     # heater top
THERMO = (812, 522)
TIMER = (610, 1405)
COMP = (720, 1415)                           # compressor dome centre
PAN = (668, 1330, 104, 24)                   # drain tray x, y, w, h (sits on the dome top y 1356)
DRAIN = [(776, 1034), (776, 1066), (860, 1086), (860, 1300), (800, 1312), (760, 1318)]
TUBES = [((752 if k % 2 == 0 else 800), 566 + 40 * k) for k in range(10)]

def polylen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
def along(pts, u):
    L = polylen(pts) * clamp(u)
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        if L <= d or i == len(pts) - 2:
            v = clamp(L / d) if d else 0
            return (lerp(pts[i][0], pts[i + 1][0], v), lerp(pts[i][1], pts[i + 1][1], v))
        L -= d
    return pts[-1]

# cold-air loop: fan -> top grille (left) -> across the top -> down the front -> back along the bottom
# -> return vent -> UP through the coil -> fan
AIR = [(776, 478), (700, 448), (560, 438), (360, 450), (346, 700), (346, 1000), (360, 1240), (560, 1250),
       (670, 1100), (700, 1030), (776, 1020), (776, 960), (776, 560), (776, 478)]
AIRLEN = polylen(AIR)

# ---------------------------------------------------------------- state
def frost_level(t):
    f = 0.55
    f += 0.30 * sstep(t, B(3) + 1.6, 4.0)          # moist air freezes onto the coil
    f += 0.13 * sstep(t, B(4) + 0.2, 4.0)
    f -= 0.98 * sstep(t, B(6) + 1.0, B(7) + 2.8 - (B(6) + 1.0))   # heater melts it
    return clamp(f)

def coil_temp(t):
    # -25 °C while cooling; heater warms it up to +5 °C at the cutoff
    k = sstep(t, B(6) + 0.8, B(7) + 3.0 - (B(6) + 0.8))
    return lerp(-25, 5, k)

def state(t):
    s = {}
    s['panel'] = 1 - sstep(t, B(1) + 0.4, 1.0)                 # back wall panel, see-through in beat 1
    s['panel'] = 0.55 if t < B(1) + 0.4 else s['panel'] * 0.55
    s['frost'] = frost_level(t)
    on = not (B(5) + 1.4 <= t < B(10) + 0.8)
    s['comp_on'] = 1.0 if on else 0.0
    s['fan_on'] = s['comp_on']
    # heater: teaser glow in the hook, then the real defrost (beat 6 -> cutoff in beat 7)
    s['heater'] = max(win(t, 0.25, B(1) - 0.2, 0.3), win(t, B(6) + 0.6, B(7) + 3.2, 0.25))
    s['door'] = win(t, B(3) + 0.5, B(3) + 4.0, 0.5)
    s['moist'] = win(t, B(3) + 0.6, B(4) + 0.6, 0.4)
    s['drips'] = win(t, B(6) + 1.6, B(8) + 4.5, 0.4)
    s['drain'] = win(t, B(8) + 0.4, B(9) + 1.0, 0.4)
    s['pan'] = clamp(sstep(t, B(8) + 1.8, 3.0) - 0.8 * sstep(t, B(9) + 0.5, 4.0))
    s['cold_air'] = max(bw(t, 2, 4), win(t, B(10) + 1.0, B(12) + 2, 0.4)) * s['fan_on']
    s['blocked'] = bw(t, 4, 5)
    return s

def spin(t):
    """integrated fan/compressor angle (stops during the defrost)."""
    a0, a1 = B(5) + 1.4, B(10) + 0.8
    run = min(t, a0) + max(0.0, t - a1)
    return run * 9.0

def cam_keys():
    return [(0, 540, 900, 1.0), (B(2) - 0.2, 600, 820, 1.12), (B(4), 600, 820, 1.12), (B(5) - 0.3, 540, 900, 1.0),
            (B(6) - 0.2, 660, 800, 1.18), (B(8) - 0.3, 540, 900, 1.0)]
def CAM(t):
    return cam_track(cam_keys(), t, 0.8)

# ---------------------------------------------------------------- drawing
def cabinet(ctx, t, s):
    for fx in (300, 820):
        rrect(ctx, fx - 16, 1478, 32, 14, 4); setc(ctx, INK); ctx.fill()
    rrect(ctx, CX0, CY0, CX1 - CX0, CY1 - CY0, 22); fill_stroke(ctx, PAPER, lw=6)
    # insulation between shell and liners
    rrect(ctx, CX0 + 14, CY0 + 14, CX1 - CX0 - 28, CY1 - CY0 - 28, 14); setc(ctx, INSUL); ctx.fill()
    for i in range(26):                                   # foam speckle
        rnd = random.Random(i)
        x = rnd.uniform(CX0 + 20, CX1 - 20); y = rnd.uniform(CY0 + 20, CY1 - 20)
        ctx.arc(x, y, 3, 0, 6.28); setc(ctx, FILL3, 0.8); ctx.fill()
    # food compartment
    rrect(ctx, FX0, FY0, FX1 - FX0, FY1 - FY0, 10); fill_stroke(ctx, INNER, lw=4)
    # evaporator compartment
    ctx.rectangle(EX0, EY0, EX1 - EX0, EY1 - EY0); fill_stroke(ctx, hexc('#dce9ea'), lw=4)
    # machine compartment (bottom back)
    rrect(ctx, 560, 1310, 304, 160, 8); fill_stroke(ctx, FILL2, lw=4)
    for i in range(4):
        rrect(ctx, 846, 1330 + i * 30, 26, 8, 3); setc(ctx, INK2); ctx.fill()

def food(ctx, t, s):
    # three drawers with frozen food
    for y0, y1 in ((560, 790), (820, 1040), (1070, 1270)):
        rrect(ctx, 336, y0, 330, y1 - y0, 10); fill_stroke(ctx, hexc('#f4f9f8', 0.9), lw=3)
        rrect(ctx, 336, y0, 330, 26, 8); fill_stroke(ctx, FILL2, lw=3)
    # top shelf: ice cream tub
    rrect(ctx, 340, 520, 330, 8, 3); fill_stroke(ctx, STEEL, lw=2)
    ctx.move_to(370, 516); ctx.line_to(380, 448); ctx.line_to(480, 448); ctx.line_to(490, 516); ctx.close_path()
    fill_stroke(ctx, hexc('#f2c6cf'), lw=4)
    rrect(ctx, 372, 440, 116, 16, 5); fill_stroke(ctx, hexc('#e98f8f'), lw=3)
    # drawer 1: bag of peas
    ctx.move_to(370, 770); ctx.curve_to(360, 690, 380, 630, 420, 610); ctx.line_to(540, 616)
    ctx.curve_to(560, 660, 560, 730, 548, 770); ctx.close_path(); fill_stroke(ctx, hexc('#9ccf86'), lw=4)
    for i in range(5):
        ctx.arc(420 + i * 24, 700 + (i % 2) * 14, 9, 0, 6.28); setc(ctx, hexc('#6fae58')); ctx.fill()
    rrect(ctx, 572, 700, 74, 70, 6); fill_stroke(ctx, WHITE, lw=3)
    # drawer 2: fish box + ice cubes
    rrect(ctx, 360, 880, 170, 140, 8); fill_stroke(ctx, hexc('#bfe0dc'), lw=4)
    ctx.move_to(385, 950); ctx.curve_to(420, 915, 470, 915, 495, 950); ctx.curve_to(470, 985, 420, 985, 385, 950)
    ctx.close_path(); setc(ctx, BLUE, 0.6); ctx.fill()
    for i in range(3):
        for j in range(2):
            rrect(ctx, 560 + i * 30, 950 + j * 30, 24, 24, 4); fill_stroke(ctx, WHITE, lw=2)
    # drawer 3: pizza box
    rrect(ctx, 356, 1180, 290, 80, 6); fill_stroke(ctx, hexc('#f6d36b'), lw=4)
    rrect(ctx, 376, 1200, 120, 22, 4); setc(ctx, RED, 0.8); ctx.fill()

def coil(ctx, t, s):
    f = s['frost']
    # fins (vertical plates)
    xs = list(range(730, 826, 10))
    for x in xs:
        ctx.move_to(x, KY0); ctx.line_to(x, KY1); setc(ctx, STEEL_D); ctx.set_line_width(2); ctx.stroke()
    # tubes seen end-on
    for (x, y) in TUBES:
        ctx.arc(x, y, 11, 0, 6.28); fill_stroke(ctx, hexc('#c9844a'), lw=3)
    # outlet tube up to the top right (thermostat sits on it), inlet top left
    ctx.move_to(800, 566); ctx.line_to(812, 540); ctx.line_to(812, 410)
    setc(ctx, INK); ctx.set_line_width(10); ctx.stroke()
    ctx.move_to(800, 566); ctx.line_to(812, 540); ctx.line_to(812, 410)
    setc(ctx, hexc('#c9844a')); ctx.set_line_width(5); ctx.stroke()
    # frost: coats every fin (gap 10 px -> closed at f = 1) and blobs on the tubes
    if f > 0.01:
        rnd = random.Random(5)
        for x in xs:
            w = 2 + 7.5 * f
            for y in range(KY0, KY1, 14):
                j = rnd.uniform(-1.2, 1.2) * f
                rrect(ctx, x - w / 2 + j, y, w, 15, w / 2); setc(ctx, FROST, 0.92); ctx.fill()
        for (x, y) in TUBES:
            ctx.arc(x, y, 11 + 6 * f, 0, 6.28); setc(ctx, FROST, 0.9); ctx.fill()
        ctx.rectangle(KX0 - 4, KY0 - 4 - 10 * f, KX1 - KX0 + 8, 6 + 10 * f); setc(ctx, FROST, 0.8 * f); ctx.fill()
    rrect(ctx, KX0, KY0, KX1 - KX0, KY1 - KY0, 4); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    # defrost thermostat clipped on the outlet tube
    tx, ty = THERMO
    rrect(ctx, tx - 13, ty - 18, 26, 36, 6); fill_stroke(ctx, INK2, lw=3)
    ctx.move_to(tx + 13, ty - 8); ctx.curve_to(830, 500, 834, 470, 834, 420); setc(ctx, BLUE); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(tx + 13, ty + 4); ctx.curve_to(834, 500, 838, 470, 838, 420); setc(ctx, RED); ctx.set_line_width(3); ctx.stroke()

def heater(ctx, t, s):
    h = s['heater']
    if h > 0:
        g = cairo.RadialGradient(776, HY + 9, 10, 776, HY + 9, 120)
        g.add_color_stop_rgba(0, *ORANGE[:3], 0.55 * h); g.add_color_stop_rgba(1, *ORANGE[:3], 0)
        ctx.set_source(g); ctx.rectangle(EX0, HY - 120, EX1 - EX0, 220); ctx.fill()
    rrect(ctx, 722, HY, 108, 18, 9); fill_stroke(ctx, lerpc(GLASS, hexc('#ff6a3d'), h), lw=3)
    ctx.move_to(730, HY + 9)
    for i in range(16):
        ctx.line_to(734 + i * 6, HY + 9 + (4 if i % 2 else -4))
    setc(ctx, lerpc(INK2, hexc('#ffd27a'), h)); ctx.set_line_width(2); ctx.stroke()
    # heat rises UP into the coil
    if h > 0.05 and t > B(6):
        for i, x in enumerate((744, 776, 808)):
            wavy_arrow(ctx, x, HY - 6, x, HY - 150, t + i * 0.3, RED, h * 0.9, amp=5, wl=26, lw=4, head=10)

def trough(ctx, t, s):
    ctx.move_to(716, 1000); ctx.line_to(770, 1030); ctx.line_to(782, 1030); ctx.line_to(836, 1000)
    setc(ctx, STEEL_D); ctx.set_line_width(6); ctx.stroke()
    # drain tube: trough -> down the back -> above the tray
    for w, c in ((14, INK), (8, hexc('#d9d2c3'))):
        ctx.move_to(*DRAIN[0])
        for p in DRAIN[1:]: ctx.line_to(*p)
        setc(ctx, c); ctx.set_line_width(w); ctx.stroke()

def fan(ctx, t, s):
    cx, cy = FANC
    ctx.arc(cx, cy, 36, 0, 6.28); fill_stroke(ctx, FILL2, lw=4)
    ang = spin(t)
    for k in range(3):
        a0 = ang + k * 2 * math.pi / 3
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(a0)
        ctx.move_to(0, 0); ctx.curve_to(10, -8, 28, -10, 30, 0); ctx.curve_to(26, 8, 10, 8, 0, 0)
        ctx.restore(); fill_stroke(ctx, STEEL, lw=2)
    ctx.arc(cx, cy, 6, 0, 6.28); setc(ctx, INK); ctx.fill()

def panel(ctx, t, s):
    # top grille + bottom return vent are always open
    a = s['panel']
    if a > 0:
        ctx.rectangle(PX0, EY0, EX1 - PX0, 980 - EY0 + 40); setc(ctx, FILL2, a); ctx.fill()
        ctx.rectangle(PX0, EY0, EX1 - PX0, 980 - EY0 + 40); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(PX0, 490, PX1 - PX0, 510); setc(ctx, FILL3); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    for y in range(420, 482, 12):     # top grille slats
        ctx.rectangle(PX0, y, PX1 - PX0, 5); setc(ctx, INK2); ctx.fill()
    for y in range(1006, 1052, 12):   # return vent slats
        ctx.rectangle(PX0, y, PX1 - PX0, 5); setc(ctx, INK2); ctx.fill()

def compressor(ctx, t, s):
    cx, cy = COMP
    on = s['comp_on']
    vib = math.sin(t * 70) * 2.0 * on
    ctx.save(); ctx.translate(vib, 0)
    ctx.move_to(cx - 52, 1468); ctx.line_to(cx - 52, 1400); ctx.curve_to(cx - 52, 1350, cx + 52, 1350, cx + 52, 1400)
    ctx.line_to(cx + 52, 1468); ctx.close_path(); fill_stroke(ctx, lerpc(hexc('#3b3842'), hexc('#7a3a30'), 0.5), lw=5)
    rrect(ctx, cx - 64, 1462, 128, 10, 3); setc(ctx, INK); ctx.fill()
    # drain tray sitting on the dome
    x, y, w, h = PAN
    lvl = s['pan']
    if lvl > 0:
        ctx.rectangle(x + 4, y + h - 2 - 16 * lvl, w - 8, 16 * lvl); setc(ctx, WATER, 0.9); ctx.fill()
    ctx.move_to(x, y); ctx.line_to(x + 4, y + h); ctx.line_to(x + w - 4, y + h); ctx.line_to(x + w, y)
    setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
    if on > 0.5:
        for i, (dx, dy) in enumerate([(-74, -20), (74, -10)]):
            ph = (t * 3 + i * 0.4) % 1
            ctx.move_to(cx + dx, 1420 + dy - 12); ctx.line_to(cx + dx * (1.05 + 0.1 * ph), 1420 + dy + 12)
            setc(ctx, INK2, 0.8 * (1 - ph)); ctx.set_line_width(4); ctx.stroke()

def timer(ctx, t, s):
    x, y = TIMER
    rrect(ctx, x - 38, y - 34, 76, 68, 8); fill_stroke(ctx, PAPER, lw=4)
    ctx.arc(x, y, 22, 0, 6.28); fill_stroke(ctx, WHITE, lw=3)
    # pointer turns CLOCKWISE (angle increases on screen); jumps at the two clicks
    ang = -math.pi / 2 + 0.6 * t * 0.05 + 1.2 * sstep(t, B(5) + 1.3, 0.12) + 1.2 * sstep(t, B(10) + 0.7, 0.12)
    ctx.move_to(x, y); ctx.line_to(x + 17 * math.cos(ang), y + 17 * math.sin(ang)); setc(ctx, RED); ctx.set_line_width(4); ctx.stroke()
    for i in range(12):
        a = i * math.pi / 6
        ctx.move_to(x + 18 * math.cos(a), y + 18 * math.sin(a)); ctx.line_to(x + 22 * math.cos(a), y + 22 * math.sin(a))
        setc(ctx, INK2); ctx.set_line_width(2); ctx.stroke()

def door(ctx, t, s):
    o = s['door']
    dx = -46 * o
    ctx.save(); ctx.translate(dx, 0)
    rrect(ctx, 228, 368, 76, 1104, 14); fill_stroke(ctx, PAPER, lw=5)
    for y in (560, 820, 1080):
        rrect(ctx, 300, y, 22, 60, 4); fill_stroke(ctx, hexc('#bfe0dc'), lw=3)
    rrect(ctx, 208, 640, 20, 260, 8); fill_stroke(ctx, FILL3, lw=4)
    ctx.restore()

def air(ctx, t, s):
    a = s['cold_air']
    if a > 0:
        speed = 120 * (1 - 0.75 * s['blocked'])
        n = 34
        for i in range(n):
            d = (i / n * AIRLEN + t * speed) % AIRLEN
            p = along(AIR, d / AIRLEN)
            if KY0 - 10 < p[1] < KY1 + 10 and KX0 < p[0] < KX1: continue      # hidden inside the coil
            ctx.arc(p[0], p[1], 6, 0, 6.28); setc(ctx, COLD, 0.85 * a); ctx.fill()
        # a few direction chevrons
        for u in (0.12, 0.32, 0.55, 0.73):
            p0 = along(AIR, u); p1 = along(AIR, u + 0.02)
            straight_arrow(ctx, p0[0], p0[1], p1[0], p1[1], COLD, a, lw=5, head=14)
    m = s['moist']
    if m > 0:
        lt = t - B(3)
        rnd = random.Random(11)
        for i in range(16):
            y0 = rnd.uniform(560, 1150); delay = rnd.uniform(0.0, 2.6)
            u = clamp((lt - 0.6 - delay) / 2.2)
            if u <= 0: continue
            path = [(318, y0), (lerp(318, 650, 0.6), lerp(y0, 1180, 0.5)), (690, 1030), (776, 1020), (776, 960),
                    (776, rnd.uniform(620, 900))]
            p = along(path, u)
            fade = 1 - sstep(u, 0.85, 0.15)
            r = 9 - 4 * u
            ctx.arc(p[0], p[1], r, 0, 6.28); setc(ctx, MOIST, 0.9 * m * fade); ctx.fill_preserve()
            setc(ctx, INK2, 0.5 * m * fade); ctx.set_line_width(2); ctx.stroke()
        # puffs at the door gap
        for i in range(3):
            ph = (lt * 0.8 + i / 3) % 1
            x = 300 - 10 + 40 * ph; y = 640 + i * 180
            ctx.move_to(x - 30, y); ctx.curve_to(x - 10, y - 20, x + 10, y + 20, x + 30, y)
            setc(ctx, MOIST, s['door'] * (1 - ph)); ctx.set_line_width(6); ctx.stroke()

def water(ctx, t, s):
    d = s['drips']
    if d > 0:
        for i in range(8):
            ph = (t * 0.9 + i / 8) % 1
            x = 736 + (i * 13) % 84
            y = lerp(KY1 + 4, 1024, ph)
            ctx.move_to(x, y - 9); ctx.curve_to(x + 6, y, x + 6, y + 6, x, y + 6); ctx.curve_to(x - 6, y + 6, x - 6, y, x, y - 9)
            setc(ctx, BLUE, 0.85 * d); ctx.fill()
    g = s['drain']
    if g > 0:
        for i in range(9):
            u = (t * 0.32 + i / 9) % 1
            p = along(DRAIN, u)
            ctx.arc(p[0], p[1], 5, 0, 6.28); setc(ctx, BLUE, g); ctx.fill()
        # drops falling from the tube end into the tray
        for i in range(2):
            ph = (t * 1.6 + i * 0.5) % 1
            ctx.arc(760, lerp(1322, 1346, ph), 4, 0, 6.28); setc(ctx, BLUE, g * (1 - ph)); ctx.fill()

def stage(ctx, t, s):
    cabinet(ctx, t, s)
    food(ctx, t, s)
    coil(ctx, t, s)
    heater(ctx, t, s)
    trough(ctx, t, s)
    fan(ctx, t, s)
    panel(ctx, t, s)
    compressor(ctx, t, s)
    timer(ctx, t, s)
    air(ctx, t, s)
    water(ctx, t, s)
    door(ctx, t, s)

def overlays(ctx, t, s):
    # hook: the heater glows through the back wall
    a = win(t, 0.3, B(1) - 0.2, 0.3)
    highlight(ctx, 776, HY + 9, 80, 34, RED, a, t)
    tag(ctx, "HEATER · ON", 560, 1020, RED, a, 30)
    # the secret: frost-covered coil
    a = bw(t, 1)
    highlight(ctx, 776, 745, 80, 225, COLD, a, t)
    tag(ctx, "FROST", 560, 700, COLD, a, 32)
    a = bw(t, 2)
    highlight(ctx, 776, 745, 80, 225, COLD, a, t)
    tag(ctx, "EVAPORATOR", 560, 700, COLD, a, 30)
    tag(ctx, "COLD AIR", 500, 395, COLD, a * sstep(t, B(2) + 2.0, 0.3), 24)
    a = win(t, B(3) + 0.8, B(4), 0.3)
    tag(ctx, "MOIST AIR", 470, 1120, INK2, a, 26)
    tag(ctx, "FROST GROWS", 560, 700, COLD, win(t, B(3) + 3.2, B(4), 0.3), 26)
    # 1 · timer
    a = bw(t, 5, 6) + win(t, B(11) + 1.0, B(12) + 2, 0.3)
    highlight(ctx, TIMER[0], TIMER[1], 56, 50, MUSTARD, bw(t, 5, 6), t)
    tag(ctx, "1 · TIMER", 440, 1405, hexc('#b07a10'), a, 26)
    tag(ctx, "COMPRESSOR OFF", 720, 1290, RED, win(t, B(5) + 1.6, B(6), 0.3), 22)
    tag(ctx, "FAN OFF", 560, 478, RED, win(t, B(5) + 2.0, B(6), 0.3), 22)
    # 2 · heater
    a = win(t, B(6) + 0.6, B(7), 0.3) + win(t, B(11) + 1.3, B(12) + 2, 0.3)
    tag(ctx, "2 · HEATER", 560, 1010, RED, a, 26)
    tag(ctx, "~500 W", 560, 1068, RED, win(t, B(6) + 2.0, B(7), 0.3), 26)
    # cutoff thermostat
    a = bw(t, 7)
    highlight(ctx, THERMO[0], THERMO[1], 36, 40, BLUE, a, t)
    tag(ctx, "THERMOSTAT", 560, 560, BLUE, a, 24)
    tag(ctx, "HEATER OFF", 560, 1010, INK, win(t, B(7) + 3.3, B(8), 0.3), 24)
    # 3 · drain
    a = bw(t, 8) + win(t, B(11) + 1.6, B(12) + 2, 0.3)
    highlight(ctx, PAN[0] + PAN[2] / 2, PAN[1] + 10, 74, 34, BLUE, bw(t, 8), t)
    tag(ctx, "3 · DRAIN TRAY", 440, 1340, BLUE, a, 26)
    # restart
    tag(ctx, "COLD AGAIN", 560, 478, COLD, win(t, B(10) + 1.0, B(11), 0.3), 22)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    stage(ctx, t, s)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=175, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def draw_hud(ctx, t, E):
    # how often: hook
    a = win(t, 2.4, B(1) - 0.1, 0.3)
    if a > 0:
        hud(ctx, "DEFROSTS", "1–4× A DAY", None, a, RED, x=40, y=190, w=470)
    # cutoff: coil temperature climbing to +5 °C, then the heater is cut
    a = win(t, B(6) + 0.8, B(8), 0.3)
    if a > 0:
        T = coil_temp(t)
        cut = sstep(t, B(7) + 3.0, 0.2)
        f = T * 9 / 5 + 32
        val = f"{T:+.0f} °C · {f:.0f} °F".replace('-', '−')
        hud(ctx, "COIL TEMPERATURE", val, "CUTOFF AT 5 °C · 41 °F", a, BLUE if cut < 0.5 else RED, flash=cut,
            x=40, y=190, w=560)
    # surprise: duration + food stays frozen
    a = win(t, B(10) + 0.3, B(11), 0.3)
    if a > 0:
        hud(ctx, "WHOLE DEFROST", "< 1 HOUR", None, a, MUSTARD, x=40, y=190, w=430)
        hud(ctx, "YOUR FOOD", "−18 °C · 0 °F", None, a * sstep(t, B(10) + 2.6, 0.3), COLD, x=500, y=190, w=540)
    a = win(t, B(11) + 0.6, B(12) + 2, 0.3)
    if a > 0:
        _panel(ctx, a, x=90, y=200, w=900, h=120)
        text_c(ctx, "MELTS ITS OWN FROST", 540, 262, 50, RED, True, 2, a)
        text_c(ctx, "ON A SCHEDULE", 540, 304, 28, INK, True, 2, a * sstep(t, B(11) + 2.4, 0.3))

SFX = [(0.3, 'pop'), (2.4, 'pop'), (B(1) + 0.6, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.6, 'click'), (B(3) + 3.2, 'pop'),
       (B(5) + 0.3, 'pop'), (B(5) + 1.3, 'click'), (B(6) + 0.6, 'click'), (B(6) + 2.0, 'pop'), (B(7) + 0.3, 'pop'),
       (B(7) + 3.0, 'click'), (B(8) + 0.3, 'pop'), (B(10) + 0.7, 'click'), (B(10) + 2.6, 'pop'),
       (B(11) + 1.0, 'pop'), (B(11) + 1.3, 'pop'), (B(11) + 1.6, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_blocked(ctx, t, lt, a):
    f = ease(clamp(lt / 3.5))
    card_frame(ctx, "FROST = A BLANKET", a, "GAPS CLOGGED · NO AIRFLOW" if f > 0.75 else "COLD AIR GOES UP BETWEEN THE FINS",
               RED if f > 0.75 else TEAL)
    xs = [250 + i * 70 for i in range(9)]
    top, bot = 270, 520
    for x in xs:
        rrect(ctx, x - 6, top, 12, bot - top, 4); fill_stroke(ctx, STEEL, lw=2, alpha=a)
    # frost thickens on both faces of each fin; gap 58 px -> closed at f = 1
    for x in xs:
        w = 12 + 58 * f
        rrect(ctx, x - w / 2, top - 6 * f, w, bot - top + 12 * f, 10); setc(ctx, FROST, 0.95 * a); ctx.fill_preserve()
        setc(ctx, INK2, 0.4 * a); ctx.set_line_width(2); ctx.stroke()
    # air going UP through the gaps, stopped by the frost
    flow = 1 - f
    for i in range(len(xs) - 1):
        gx = (xs[i] + xs[i + 1]) / 2
        for k in range(3):
            ph = (lt * 0.9 + k / 3 + i * 0.13) % 1
            y = lerp(bot + 10, top - 10, ph * max(0.15, flow))
            ctx.arc(gx, y, 6, 0, 6.28); setc(ctx, COLD, a * (0.9 if flow > 0.25 else 0.5)); ctx.fill()
    if f > 0.75:
        k = a * sstep(lt, 2.8, 0.3)
        for x in (420, 660):
            ctx.move_to(x - 30, 360); ctx.line_to(x + 30, 420); ctx.move_to(x + 30, 360); ctx.line_to(x - 30, 420)
            setc(ctx, RED, k); ctx.set_line_width(9); ctx.stroke()

def card_evaporate(ctx, t, lt, a):
    card_frame(ctx, "WHERE THE WATER GOES", a, "WARM COMPRESSOR · WATER EVAPORATES", RED)
    cx = 540
    # compressor dome (warm)
    ctx.move_to(cx - 170, 545); ctx.line_to(cx - 170, 470); ctx.curve_to(cx - 170, 400, cx + 170, 400, cx + 170, 470)
    ctx.line_to(cx + 170, 545); ctx.close_path(); fill_stroke(ctx, lerpc(hexc('#3b3842'), RED, 0.45), lw=5, alpha=a)
    # tray on top with water going down
    lvl = 1 - 0.7 * ease(clamp(lt / 4.5))
    ctx.rectangle(cx - 150, 400 - 34 * lvl, 300, 34 * lvl); setc(ctx, WATER, 0.9 * a); ctx.fill()
    ctx.move_to(cx - 160, 350); ctx.line_to(cx - 150, 402); ctx.line_to(cx + 150, 402); ctx.line_to(cx + 160, 350)
    setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    # heat from the compressor into the tray (UP)
    for i, x in enumerate((cx - 220, cx + 220)):
        wavy_arrow(ctx, x, 520, x + (60 if x < cx else -60), 420, t + i * 0.4, RED, a, amp=6, wl=30, lw=5, head=12)
    # vapour rising out to the kitchen
    for i in range(5):
        ph = (lt * 0.55 + i / 5) % 1
        x = cx - 110 + i * 55; y = 350 - ph * 110
        ctx.move_to(x, y + 30); ctx.curve_to(x - 16, y + 14, x + 16, y, x, y - 16)
        setc(ctx, VAPOR, a * (1 - ph)); ctx.set_line_width(6); ctx.stroke()
    text_c(ctx, "TO THE KITCHEN AIR", 820, 290, 24, TEAL, True, 1.5, a * sstep(lt, 1.6, 0.3))

CARDS = {'blocked': card_blocked, 'evaporate': card_evaporate}
