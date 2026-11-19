"""Cogwise episode: Your tire light comes on with the first frost.
One idea: nothing leaks. The same air molecules slow down in the cold, hit the rubber softer and less often,
so the pressure drops (~12 kPa / ~1.8 psi per 10 °C colder; 240 kPa at 20 °C -> ~210 kPa at -5 °C, about 12 %).
Add the slow monthly seep and the pressure can cross the TPMS warning line. Driving warms the tire back up.

VIEW (screen coordinates, y grows DOWN): a car wheel seen from the SIDE, outer sidewall CUT AWAY so the air
chamber shows.
  - wheel centre C = (540, 1095). Tread outer radius 380 (touches the road at y 1475), inner face of the
    rubber 338. Rim flange radius 236. Air chamber = ring between r 236 (rim) and r 338 (rubber).
  - air molecules bounce inside that ring; every hit on the RUBBER (outer wall) draws a short red arrow pointing
    OUTWARD (away from C) = the push that makes the pressure. Arrow length ~ molecule speed.
  - warm = orange, fast molecules; cold = teal, slow molecules (speed x 0.55, simplified/exaggerated so it shows).
    The number of molecules never changes (nothing leaks).
  - TPMS sensor on the rim at the valve, angle -60 deg (upper right), inside the air ring.
  - car rolls to the RIGHT in beat 11 -> the wheel turns CLOCKWISE on screen (angle increases, y down).
  - frost: white crystals on the road and on top of the tread when cold.
  - dashboard tire-pressure light (horseshoe + "!") top right, amber when on.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="tire-light-frost",
    title="Your tire light comes on with the first frost ❄️ #Shorts",
    description=("Nothing leaked. The same air just got cold, and cold air pushes on the rubber softer.\n\n"
                 "#Shorts #howthingswork #tires #cars #cogwise"),
    hashtags=["Shorts", "howthingswork", "tires", "cars", "cogwise"],
    sources=[
        "https://cluballiance.aaa.com/the-extra-mile/advice/car/how-temperature-changes-affect-your-tire-pressure",
        "https://www.brakeandfrontend.com/cold-weather-tpms-operation/",
        "https://www.motor1.com/features/802717/why-tire-pressure-light-comes-on-when-cold/",
        "https://www.nhtsa.gov/sites/nhtsa.dot.gov/files/fmvss/tirepressure-fmvss-138.pdf",
    ],
)

BEATS = [
    dict(dur=5.0, title="FIRST FROST", caption="First frost, and your tire light is on. Yet nothing leaked."),
    dict(dur=5.0, title="THE SECRET", caption="The secret: it's the same air. It just got cold."),
    dict(dur=6.5, title="INSIDE THE TIRE", caption="Inside the tire, billions of air molecules race around and bang into the rubber."),
    dict(dur=6.0, title="1 · PRESSURE", caption="Each tiny hit pushes outward. All those hits together are the pressure."),
    dict(dur=6.5, title="2 · THE COLD", caption="Cool the air, and the molecules slow down. They hit softer, and less often."),
    dict(dur=6.0, title=None, caption="Like a ball left outside overnight: same air, but soft by morning.", card='ball'),
    dict(dur=5.5, title="3 · THE NUMBERS", caption="Every ten Celsius colder costs about twelve kilopascals. Almost two psi."),
    dict(dur=6.0, title="FROSTY MORNING", caption="Pumped at twenty Celsius, sixty-eight Fahrenheit. Next morning, minus five, twenty-three Fahrenheit."),
    dict(dur=5.0, title=None, caption="About thirty kilopascals, four psi, are gone. Roughly twelve percent.", card='gauge'),
    dict(dur=7.0, title="THE SENSOR", caption="Add the slow seep every tire has, and you can cross the sensor's warning line."),
    dict(dur=7.0, title="WARM AGAIN", caption="Drive ten minutes, the rubber warms, the molecules speed up, and the light often goes out."),
    dict(dur=4.5, title="SAME AIR, SOFTER HITS", caption="Nothing leaked. Cold air just hits the rubber softer."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

RUBBER = hexc('#3b3842'); RUBBER_L = hexc('#57535e')
STEEL = hexc('#b9c0c6'); STEEL_D = hexc('#7d858c')
FROST = hexc('#ffffff'); ICE = hexc('#d8ecf0')
AMBER = hexc('#f5a623'); BLUE = hexc('#2f6fb3')
AIRBG = hexc('#f6efe2')

C = (540.0, 1095.0)
R_TREAD, R_IN, R_RIM, R_HUB = 380.0, 338.0, 236.0, 70.0
VALVE_A = -math.pi / 3          # upper right

# ---------------------------------------------------------------- temperature story (0 = warm 20 °C, 1 = cold -5 °C)
def cold(t):
    c = 1.0
    c -= sstep(t, B(2) + 0.2, 0.9)                       # flashback: last evening, 20 °C
    c += sstep(t, B(4) + 0.6, 2.2)                       # cool the air
    c -= sstep(t, B(7) + 0.1, 0.5)                       # evening again (pumped at 20 °C)
    c += sstep(t, B(7) + 2.8, 1.6)                       # next morning, -5 °C
    c -= 0.7 * sstep(t, B(10) + 1.0, 4.0)                # driving warms the rubber
    return clamp(c)

def speed_factor(t):
    return lerp(1.0, 0.55, cold(t))

def roll(t):
    """wheel angle (rad): rolls to the right = clockwise on screen = angle increases."""
    a0, a1 = B(10) + 0.4, B(11) + 0.2
    if t <= a0: return 0.0
    u = min(t, a1) - a0
    return 2.6 * u - 0.0 * u

# ---------------------------------------------------------------- molecules (precomputed, deterministic)
N_MOL = 34
DT = 1 / 120
T_END = ST[-1] + 6.0
BASE_V = 330.0

def _simulate():
    rnd = random.Random(7)
    ps = []
    for i in range(N_MOL):
        r = math.sqrt(rnd.uniform((R_RIM + 12) ** 2, (R_IN - 12) ** 2))
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0, 2 * math.pi)
        ps.append([C[0] + r * math.cos(a), C[1] + r * math.sin(a), math.cos(d), math.sin(d)])
    frames, hits = [], []
    n = int(T_END / DT) + 2
    for k in range(n):
        t = k * DT
        frames.append([(p[0], p[1]) for p in ps])
        v = BASE_V * speed_factor(t) * DT
        for p in ps:
            p[0] += p[2] * v; p[1] += p[3] * v
            dx, dy = p[0] - C[0], p[1] - C[1]
            r = math.hypot(dx, dy)
            nx, ny = dx / r, dy / r
            if r > R_IN - 8 and (p[2] * nx + p[3] * ny) > 0:
                dot = p[2] * nx + p[3] * ny
                p[2] -= 2 * dot * nx; p[3] -= 2 * dot * ny
                hits.append((t, math.atan2(ny, nx), speed_factor(t)))
            elif r < R_RIM + 8 and (p[2] * nx + p[3] * ny) < 0:
                dot = p[2] * nx + p[3] * ny
                p[2] -= 2 * dot * nx; p[3] -= 2 * dot * ny
    return frames, hits

FRAMES, HITS = _simulate()

def mol_positions(t):
    k = int(clamp(t / DT, 0, len(FRAMES) - 1))
    return FRAMES[k]

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['cold'] = cold(t)
    s['cut'] = sstep(t, 0.2, 0.8)                                     # sidewall cut away
    s['hits'] = max(win(t, B(2) + 2.2, B(5), 0.4), win(t, B(6), B(8), 0.4), win(t, B(10) + 1.0, B(12) + 2, 0.4))
    s['light'] = max(win(t, 0.4, B(2) + 0.2, 0.15), win(t, B(9) + 4.2, B(10) + 5.2, 0.25))
    s['heat'] = win(t, B(10) + 0.8, B(11) + 0.5, 0.4)
    s['sensor'] = bw(t, 9, 10)
    return s

def cam_keys():
    return [(0, 540, 900, 1.0), (B(2) + 0.1, 540, 960, 1.12), (B(5) - 0.4, 540, 900, 1.0)]
def CAM(t):
    return cam_track(cam_keys(), t, 0.8)

# ---------------------------------------------------------------- drawing
def road(ctx, t, s):
    c = s['cold']
    if c > 0.02:
        rnd = random.Random(3)
        for i in range(60):
            x = rnd.uniform(0, 1080); y = rnd.uniform(1480, 1497)
            l = rnd.uniform(5, 12)
            for k in range(3):
                a = k * math.pi / 3
                ctx.move_to(x - l * math.cos(a), y - l * math.sin(a) * 0.5)
                ctx.line_to(x + l * math.cos(a), y + l * math.sin(a) * 0.5)
            setc(ctx, FROST, 0.85 * c); ctx.set_line_width(2); ctx.stroke()

def fender(ctx, t, s):
    # car body edge with the wheel arch (body above, arch around the top of the wheel)
    ctx.move_to(0, 690); ctx.line_to(1080, 690); ctx.line_to(1080, 1030)
    ctx.line_to(C[0] + 430, 1030)
    ctx.arc_negative(C[0], C[1], 432, math.radians(-8.6), math.radians(-171.4))
    ctx.line_to(0, 1030); ctx.close_path()
    fill_stroke(ctx, hexc('#c94a3a'), lw=5)
    ctx.move_to(0, 760); ctx.line_to(1080, 760); setc(ctx, INK, 0.35); ctx.set_line_width(3); ctx.stroke()
    # inner arch shadow
    ctx.arc(C[0], C[1], 412, math.radians(188), math.radians(352)); setc(ctx, INK, 0.9); ctx.set_line_width(16); ctx.stroke()
    c = s['cold']
    if c > 0.02:
        rnd = random.Random(9)
        for i in range(40):
            x = rnd.uniform(10, 1070); y = rnd.uniform(696, 712)
            ctx.arc(x, y, rnd.uniform(3, 7), 0, 6.28); setc(ctx, FROST, 0.9 * c); ctx.fill()

def tire(ctx, t, s):
    cx, cy = C
    ang = roll(t)
    # rubber ring
    ctx.arc(cx, cy, R_TREAD, 0, 2 * math.pi); ctx.arc_negative(cx, cy, R_IN, 2 * math.pi, 0)
    setc(ctx, RUBBER); ctx.fill()
    ctx.arc(cx, cy, R_TREAD, 0, 2 * math.pi); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.arc(cx, cy, R_IN, 0, 2 * math.pi); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    # tread blocks (turn with the wheel)
    for k in range(36):
        a = ang + k * 2 * math.pi / 36
        ctx.move_to(cx + (R_TREAD - 2) * math.cos(a), cy + (R_TREAD - 2) * math.sin(a))
        ctx.line_to(cx + (R_TREAD - 16) * math.cos(a + 0.03), cy + (R_TREAD - 16) * math.sin(a + 0.03))
        setc(ctx, RUBBER_L); ctx.set_line_width(7); ctx.stroke()
    # frost on top of the tread
    c = s['cold']
    if c > 0.02:
        rnd = random.Random(4)
        for i in range(26):
            a = rnd.uniform(math.radians(205), math.radians(335))
            r = R_TREAD + rnd.uniform(-2, 4)
            ctx.arc(cx + r * math.cos(a), cy + r * math.sin(a), rnd.uniform(3, 6), 0, 6.28)
            setc(ctx, FROST, 0.9 * c); ctx.fill()
    # air chamber (sidewall cut away)
    ctx.arc(cx, cy, R_IN - 2, 0, 2 * math.pi); ctx.arc_negative(cx, cy, R_RIM, 2 * math.pi, 0)
    setc(ctx, lerpc(AIRBG, ICE, c)); ctx.fill()
    # uncut sidewall fades away in the hook
    k = 1 - s['cut']
    if k > 0:
        ctx.arc(cx, cy, R_IN, 0, 2 * math.pi); ctx.arc_negative(cx, cy, R_RIM, 2 * math.pi, 0)
        setc(ctx, RUBBER_L, k); ctx.fill()
    # cut edge (hatched ring line)
    ctx.set_dash([10, 8]); ctx.arc(cx, cy, R_IN - 1, 0, 2 * math.pi); setc(ctx, INK2, 0.6 * s['cut'])
    ctx.set_line_width(2); ctx.stroke(); ctx.set_dash([])

def rim(ctx, t, s):
    cx, cy = C
    ang = roll(t)
    ctx.arc(cx, cy, R_RIM, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=5)
    ctx.arc(cx, cy, R_RIM - 22, 0, 2 * math.pi); fill_stroke(ctx, hexc('#cfd5da'), lw=3)
    # five spokes
    for k in range(5):
        a = ang + k * 2 * math.pi / 5 - math.pi / 2
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(a)
        ctx.move_to(R_HUB - 10, -26); ctx.line_to(R_RIM - 24, -40); ctx.line_to(R_RIM - 24, 40); ctx.line_to(R_HUB - 10, 26)
        ctx.close_path(); ctx.restore(); fill_stroke(ctx, STEEL_D, lw=3)
    ctx.arc(cx, cy, R_HUB, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=4)
    for k in range(5):
        a = ang + k * 2 * math.pi / 5 - math.pi / 2 + math.pi / 5
        ctx.arc(cx + 42 * math.cos(a), cy + 42 * math.sin(a), 9, 0, 6.28); fill_stroke(ctx, INK2, lw=2)
    ctx.arc(cx, cy, 16, 0, 2 * math.pi); setc(ctx, INK); ctx.fill()
    # valve stem + TPMS sensor (inside the air ring, fixed to the rim)
    va = ang + VALVE_A
    ux, uy = math.cos(va), math.sin(va)
    px, py = -uy, ux
    # stem pokes out of the rim towards the hub side (visible on the rim face)
    ctx.move_to(cx + (R_RIM - 2) * ux, cy + (R_RIM - 2) * uy); ctx.line_to(cx + (R_RIM - 40) * ux, cy + (R_RIM - 40) * uy)
    setc(ctx, INK); ctx.set_line_width(10); ctx.stroke()
    # sensor body in the air ring
    sx, sy = cx + (R_RIM + 16) * ux, cy + (R_RIM + 16) * uy
    ctx.save(); ctx.translate(sx, sy); ctx.rotate(va)
    rrect(ctx, -14, -24, 28, 48, 7); ctx.restore()
    fill_stroke(ctx, lerpc(INK2, AMBER, s['sensor']), lw=3)

def molecules(ctx, t, s):
    c = s['cold']
    col = lerpc(ORANGE, COLD, c)
    for (x, y) in mol_positions(t):
        ctx.arc(x, y, 8, 0, 6.28); setc(ctx, col); ctx.fill_preserve()
        setc(ctx, INK, 0.7); ctx.set_line_width(2); ctx.stroke()
    # hits on the rubber: short red arrows pointing OUTWARD (away from the wheel centre)
    a = s['hits']
    if a > 0:
        for (th, ang, sf) in HITS:
            if th > t: break
            age = t - th
            if age > 0.45: continue
            k = 1 - age / 0.45
            L = 70 * sf
            x0 = C[0] + (R_IN - 6) * math.cos(ang); y0 = C[1] + (R_IN - 6) * math.sin(ang)
            x1 = C[0] + (R_IN - 6 + L) * math.cos(ang); y1 = C[1] + (R_IN - 6 + L) * math.sin(ang)
            straight_arrow(ctx, x0, y0, x1, y1, RED, a * k, lw=5, head=10)

def heat(ctx, t, s):
    h = s['heat']
    if h <= 0: return
    # the flexing rubber warms: heat goes from the tread INTO the air ring
    for i, deg in enumerate((200, 240, 270, 300, 340, 90)):
        a = math.radians(deg)
        x0 = C[0] + (R_TREAD - 14) * math.cos(a); y0 = C[1] + (R_TREAD - 14) * math.sin(a)
        x1 = C[0] + (R_IN - 60) * math.cos(a); y1 = C[1] + (R_IN - 60) * math.sin(a)
        wavy_arrow(ctx, x0, y0, x1, y1, t + i * 0.3, RED, h * 0.85, amp=5, wl=22, lw=4, head=10)
    # motion lines behind the wheel (it rolls to the right)
    for i in range(3):
        y = 1300 + i * 60
        ph = (t * 2 + i * 0.3) % 1
        ctx.move_to(60 + 40 * ph, y); ctx.line_to(140 + 40 * ph, y); setc(ctx, INK2, h * (1 - ph)); ctx.set_line_width(5); ctx.stroke()

def thermo(ctx, t, s):
    thermometer(ctx, 1020, 1440, lerp(0.78, 0.22, s['cold']), 1.0, lerpc(RED, COLD, s['cold']), h=180)

def stage(ctx, t, s):
    road(ctx, t, s)
    fender(ctx, t, s)
    tire(ctx, t, s)
    molecules(ctx, t, s)
    rim(ctx, t, s)
    heat(ctx, t, s)
    thermo(ctx, t, s)

def overlays(ctx, t, s):
    a = win(t, 2.6, B(1), 0.3)
    tag(ctx, "NO LEAK", 540, 640, TEAL, a, 30)
    a = bw(t, 1)
    tag(ctx, "SAME AIR", 540, 640, TEAL, a, 30)
    a = bw(t, 2)
    tag(ctx, "AIR MOLECULES", 540, 640, ORANGE, a, 28)
    a = bw(t, 3)
    tag(ctx, "EACH HIT PUSHES OUT", 540, 640, RED, a, 26)
    a = win(t, B(4) + 2.4, B(5), 0.3)
    tag(ctx, "SLOWER · SOFTER HITS", 540, 640, COLD, a, 26)
    tag(ctx, "SAME NUMBER", 540, 1395, INK, win(t, B(4) + 3.8, B(5), 0.3), 22)
    # the sensor
    a = s['sensor']
    va = roll(t) + VALVE_A
    sx, sy = C[0] + (R_RIM + 16) * math.cos(va), C[1] + (R_RIM + 16) * math.sin(va)
    highlight(ctx, sx, sy, 44, 52, AMBER, a, t)
    tag(ctx, "PRESSURE SENSOR", 780, 640, hexc('#b07a10'), a, 24)
    a = win(t, B(10) + 0.8, B(11), 0.3)
    tag(ctx, "RUBBER WARMS", 540, 640, RED, a, 26)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    stage(ctx, t, s)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def tpms_light(ctx, t, on, x=900, y=255):
    rrect(ctx, x - 110, y - 70, 220, 140, 18); setc(ctx, INK, 0.94); ctx.fill_preserve()
    setc(ctx, lerpc(INK2, AMBER, on)); ctx.set_line_width(3); ctx.stroke()
    col = lerpc(hexc('#4a4650'), AMBER, on)
    if on > 0.3:
        g = cairo.RadialGradient(x, y, 10, x, y, 90)
        g.add_color_stop_rgba(0, *AMBER[:3], 0.45 * on); g.add_color_stop_rgba(1, *AMBER[:3], 0)
        ctx.set_source(g); ctx.arc(x, y, 90, 0, 6.28); ctx.fill()
    # horseshoe tire symbol, open at the top
    ctx.arc(x, y - 4, 40, math.radians(-40), math.radians(220)); setc(ctx, col); ctx.set_line_width(9); ctx.stroke()
    for i in range(5):
        xx = x - 30 + i * 15
        ctx.move_to(xx, y + 44); ctx.line_to(xx, y + 54); setc(ctx, col); ctx.set_line_width(6); ctx.stroke()
    ctx.select_font_face(CAPTION_FONT, 0, 0); ctx.set_font_size(52); setc(ctx, col)
    e = ctx.text_extents("!"); ctx.move_to(x - e.x_advance / 2, y + 14); ctx.show_text("!"); ctx.new_path()

def psi_of(p):
    """240 kPa = 35 psi (pumped), 210 kPa = 31 psi (morning): linear between, as on a dual gauge."""
    return 35 - (240 - p) * 4 / 30

def fmt_c(T):
    F = T * 9 / 5 + 32
    return f"{T:.0f} °C · {F:.0f} °F".replace('-', '−')

def _panel(ctx, a, x=60, y=175, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def bar_gauge(ctx, t, a, p):
    """horizontal pressure bar with the sensor's warning line."""
    x, y, w, h = 40, 190, 720, 150
    rrect(ctx, x, y, w, h, 14); setc(ctx, INK, 0.92 * a); ctx.fill_preserve()
    setc(ctx, AMBER, a); ctx.set_line_width(3); ctx.stroke()
    ctx.select_font_face(SANS, 0, 1); ctx.set_font_size(24); setc(ctx, CREAM, a)
    ctx.move_to(x + 22, y + 38); ctx.show_text("TIRE PRESSURE")
    psi = psi_of(p)
    ctx.select_font_face(CAPTION_FONT, 0, 0); ctx.set_font_size(40)
    below = p < 198
    setc(ctx, RED if below else CREAM, a); ctx.move_to(x + 330, y + 40); ctx.show_text(f"{p:.0f} kPa · {psi:.0f} psi")
    bx0, bx1, by = x + 24, x + w - 24, y + 90
    lo, hi = 150, 260
    def X(v): return lerp(bx0, bx1, (v - lo) / (hi - lo))
    rrect(ctx, bx0, by - 16, bx1 - bx0, 32, 16); setc(ctx, hexc('#4a4650'), a); ctx.fill()
    rrect(ctx, bx0, by - 16, X(p) - bx0, 32, 16); setc(ctx, RED if below else TEAL_L, a); ctx.fill()
    wl = X(198)
    ctx.move_to(wl, by - 30); ctx.line_to(wl, by + 30); setc(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
    ctx.select_font_face(SANS, 0, 1); ctx.set_font_size(20); setc(ctx, RED, a)
    ctx.move_to(wl - 50, by + 52); ctx.show_text("WARNING LINE")
    ctx.new_path()

def draw_hud(ctx, t, E):
    s = state(t)
    # dashboard light (not during the cards / big panels)
    show_light = max(win(t, 0.0, B(2) + 0.2, 0.2), win(t, B(9) + 0.2, B(11) + 0.2, 0.3))
    if show_light > 0:
        ctx.push_group(); tpms_light(ctx, t, s['light']); ctx.pop_group_to_source(); ctx.paint_with_alpha(show_light)
    # hook: outside temperature
    a = win(t, 0.3, B(1), 0.25)
    if a > 0:
        hud(ctx, "OUTSIDE", fmt_c(-5), None, a, COLD, x=40, y=190, w=560)
    # the secret: same air, it just got cold (20 -> -5)
    a = bw(t, 1)
    if a > 0:
        T = lerp(20, -5, sstep(t, B(1) + 0.8, 2.6))
        hud(ctx, "AIR IN THE TIRE", fmt_c(T), "SAME AIR · NOTHING ADDED OR LOST", a, lerpc(RED, COLD, sstep(t, B(1) + 0.8, 2.6)),
            x=40, y=190, w=640)
    a = bw(t, 2)
    if a > 0:
        hud(ctx, "LAST EVENING", fmt_c(20), None, a, ORANGE, x=40, y=190, w=560)
    # pressure
    a = bw(t, 3, 5)
    if a > 0:
        p = lerp(240, 210, sstep(t, B(4) + 0.6, 2.4))
        hud(ctx, "TIRE PRESSURE", f"{p:.0f} kPa · {psi_of(p):.0f} psi", None, a,
            RED if t < B(4) else COLD, x=40, y=190, w=640)
    # the numbers
    a = bw(t, 6)
    if a > 0:
        _panel(ctx, a, x=60, y=180, w=960, h=260)
        text_c(ctx, "EVERY 10 °C · 18 °F COLDER", 540, 245, 36, COLD, True, 2, a)
        k = a * sstep(t, B(6) + 1.6, 0.3)
        text_c(ctx, "−12 kPa", 540, 330, 72, RED, True, 2, k)
        text_c(ctx, "≈ −1.8 psi", 540, 400, 40, INK, True, 2, a * sstep(t, B(6) + 3.2, 0.3))
    # frosty morning
    a = bw(t, 7)
    if a > 0:
        m = sstep(t, B(7) + 2.8, 0.3)
        T = lerp(20, -5, sstep(t, B(7) + 2.8, 1.6))
        hud(ctx, "MORNING" if m > 0.5 else "PUMPED IN THE EVENING", fmt_c(T), None, a,
            lerpc(ORANGE, COLD, m), x=40, y=190, w=640)
    # the sensor: slow seep crosses the warning line
    a = bw(t, 9, 11)
    if a > 0:
        p = lerp(210, 194, sstep(t, B(9) + 1.2, 3.0))
        p = lerp(p, 212, sstep(t, B(10) + 1.0, 4.0))
        bar_gauge(ctx, t, a, p)
    # recap
    a = win(t, B(11) + 0.2, B(12) + 2, 0.3)
    if a > 0:
        _panel(ctx, a, x=90, y=200, w=900, h=130)
        text_c(ctx, "SAME AIR", 540, 262, 52, TEAL, True, 2, a)
        text_c(ctx, "SOFTER HITS", 540, 310, 32, RED, True, 2, a * sstep(t, B(11) + 1.6, 0.3))

SFX = [(0.4, 'click'), (2.6, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(4) + 2.4, 'pop'),
       (B(6) + 1.6, 'pop'), (B(7) + 2.8, 'pop'), (B(9) + 0.3, 'pop'), (B(9) + 4.2, 'click'), (B(10) + 0.8, 'pop'),
       (B(10) + 5.0, 'click'), (B(11) + 0.2, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_ball(ctx, t, lt, a):
    card_frame(ctx, "SAME BALL, SAME AIR", a, None)
    gy = 520
    for cx, label, hgt, col, frost in ((330, "EVENING · 20 °C", 165, ORANGE, 0), (750, "MORNING · −5 °C", 45, COLD, 1)):
        ctx.move_to(cx - 150, gy); ctx.line_to(cx + 150, gy); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        ph = abs(math.sin(math.pi * lt * 0.9))
        r = 44
        y = gy - r - hgt * ph
        squash = 1 + (0.25 if frost else 0.08) * (1 - ph) ** 6
        ctx.save(); ctx.translate(cx, y + r * (squash - 1) * 0.5); ctx.scale(squash, 1 / squash)
        ctx.arc(0, 0, r, 0, 6.28); ctx.restore(); fill_stroke(ctx, lerpc(hexc('#f2c6a0'), ICE, frost), lw=4, alpha=a)
        ctx.save(); ctx.translate(cx, y + r * (squash - 1) * 0.5); ctx.scale(squash, 1 / squash)
        ctx.move_to(-r, 0); ctx.curve_to(-r / 2, -r / 2, r / 2, r / 2, r, 0); ctx.restore()
        setc(ctx, col, a); ctx.set_line_width(4); ctx.stroke()
        text_c(ctx, label, cx, 572, 28, col, True, 1.5, a)
        if frost:
            rnd = random.Random(2)
            for i in range(10):
                x = cx + rnd.uniform(-140, 140); yy = gy - rnd.uniform(2, 8)
                ctx.arc(x, yy, rnd.uniform(3, 6), 0, 6.28); setc(ctx, FROST, a); ctx.fill_preserve()
                setc(ctx, INK2, 0.4 * a); ctx.set_line_width(1); ctx.stroke()

def card_gauge(ctx, t, lt, a):
    card_frame(ctx, "THE GAUGE", a, "−30 kPa · −4 psi  ≈  −12 %", RED)
    cx, cy, R = 540, 395, 122
    ctx.arc(cx, cy, R + 14, 0, 6.28); fill_stroke(ctx, WHITE, lw=5, alpha=a)
    # scale 0..300 kPa over 240 deg, from lower left (150 deg) clockwise over the top to lower right (390 deg)
    def ang(v): return math.radians(150 + 240 * v / 300)
    for v in range(0, 301, 25):
        big = v % 100 == 0
        aa = ang(v)
        ctx.move_to(cx + (R - (22 if big else 12)) * math.cos(aa), cy + (R - (22 if big else 12)) * math.sin(aa))
        ctx.line_to(cx + R * math.cos(aa), cy + R * math.sin(aa))
        setc(ctx, INK, a); ctx.set_line_width(4 if big else 2); ctx.stroke()
        if big:
            text_c(ctx, str(v), cx + (R - 48) * math.cos(aa), cy + (R - 48) * math.sin(aa) + 8, 22, INK, True, 0, a)
    # zone 210..240 highlighted
    ctx.arc(cx, cy, R - 4, ang(210), ang(240)); setc(ctx, RED, 0.5 * a); ctx.set_line_width(8); ctx.stroke()
    text_c(ctx, "kPa", cx, cy + 70, 22, INK2, True, 1, a)
    v = lerp(240, 210, ease(clamp((lt - 0.6) / 2.4)))
    aa = ang(v)
    ctx.move_to(cx, cy); ctx.line_to(cx + (R - 18) * math.cos(aa), cy + (R - 18) * math.sin(aa))
    setc(ctx, RED, a); ctx.set_line_width(6); ctx.stroke()
    ctx.arc(cx, cy, 12, 0, 6.28); setc(ctx, INK, a); ctx.fill()
    text_c(ctx, f"{v:.0f} kPa", 830, 400, 40, RED, True, 1, a)
    text_c(ctx, f"{psi_of(v):.0f} psi", 830, 450, 32, INK, True, 1, a)
    text_c(ctx, "WAS 240 kPa", 250, 400, 26, INK2, True, 1, a)
    text_c(ctx, "35 psi", 250, 440, 26, INK2, True, 1, a)

CARDS = {'ball': card_ball, 'gauge': card_gauge}
