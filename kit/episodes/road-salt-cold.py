"""Cogwise episode: Road salt doesn't actually melt ice.
One idea: a dry salt grain does nothing. It must first dissolve in the thin film of liquid water on the ice;
that brine freezes far below 0 °C, so it melts the ice it touches, which makes more water, which takes more salt.
Colder ice = thinner film and slower brine: 1 kg salt melts ~46 kg ice at -1 °C (30 °F) in minutes,
~6 kg at -9 °C (15 °F) in an hour; below -21 °C (-6 °F) even saturated brine (23 %) freezes.

VIEW (screen coordinates, y grows DOWN): macro CROSS-SECTION of a road, seen from the side.
  - asphalt from y 1180 down (dark, stones); ice slab y 900..1180 on top of it (pale blue).
  - liquid water film ON TOP of the ice: from y 900 - fh up to y 900 (fh = 16 px warm, 4 px cold,
    exaggerated ~thousands of times, labelled "ENLARGED").
  - salt grains = cubes resting ON the film (above y 900). Main grain at x 540, two side grains at x 300, 790.
  - brine pit = cavity INTO the ice under each grain (it goes DOWN, y increases), filled with brine (teal).
    The grain sinks into its pit and shrinks as it dissolves. Melting arrows point from the brine OUTWARD
    into the ice (the melting front moves away from the brine).
  - cold: film thins, frost crystals on the ice; at -21 °C the brine turns to ice (white, hatched).
  - snow / grains fall DOWN from above (y increasing).
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="road-salt-cold",
    title="Road salt doesn't actually melt ice 🧂 #Shorts",
    description=("A dry grain of salt does nothing. It needs water first, and when the road gets too cold, that water runs out.\n\n"
                 "#Shorts #howthingswork #winter #roads #cogwise"),
    hashtags=["Shorts", "howthingswork", "winter", "roads", "cogwise"],
    sources=[
        "https://www.cargill.com/at-what-temperature-does-rock-salt-stop-working",
        "https://mnltap.umn.edu/guides/smartwintersalt/property-managers/pavement/deicing-use",
        "https://www1.maine.gov/mdot/mlrc/docs/technical/2023/UnderstandingSalt.pdf",
        "https://www.scientificamerican.com/article/why-does-salting-roads-make-them-safer/",
    ],
)

BEATS = [
    dict(dur=4.5, title="ROAD SALT", caption="Road salt doesn't actually melt ice. It needs water first."),
    dict(dur=5.0, title="THE SECRET", caption="The secret: ice almost always wears a thin film of liquid water."),
    dict(dur=5.0, title="1 · DISSOLVE", caption="The salt dissolves into that film and turns it into brine."),
    dict(dur=6.0, title="2 · BRINE", caption="Salty water won't freeze at zero Celsius, thirty-two Fahrenheit. It stays liquid."),
    dict(dur=5.5, title="3 · IT DRILLS", caption="That brine melts the ice it touches, and drills down under each grain."),
    dict(dur=5.5, title=None, caption="Melted ice is new water, so it dissolves more salt. A chain reaction.", card='chain'),
    dict(dur=6.0, title="THE COLD", caption="But colder ice has a thinner film, and the salt dissolves slower and slower."),
    dict(dur=6.5, title="MINUS ONE", caption="At minus one Celsius, thirty Fahrenheit, one kilo of salt melts forty-six kilos of ice within minutes."),
    dict(dur=6.0, title=None, caption="At minus nine Celsius, fifteen Fahrenheit, it's barely six kilos. And it needs an hour.", card='melt'),
    dict(dur=6.0, title="THE WALL", caption="Below minus twenty-one, minus six Fahrenheit, even the saltiest brine freezes solid."),
    dict(dur=5.5, title="ROAD CREWS", caption="So road crews switch to calcium chloride, or just throw sand for grip."),
    dict(dur=3.5, title="SALTY WATER", caption="Salt doesn't melt ice. Salty water does."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

ICE = hexc('#dceef3'); ICE_D = hexc('#a9d2dd')
WATER = hexc('#3d8fd6'); BRINE = hexc('#1f8a8a')
ASPH = hexc('#3a373f'); STONE = hexc('#5b5760'); STONE_L = hexc('#77727c')
SALT = hexc('#ffffff'); SALT_S = hexc('#d9dde2')
SAND = hexc('#b9853f'); FROST = hexc('#ffffff')

Y_ICE, Y_ASPH = 900.0, 1180.0
GRAINS = [  # x, full size, tilt (deg), pit scale
    (540.0, 92.0, 8.0, 1.0),
    (300.0, 62.0, -14.0, 0.6),
    (790.0, 72.0, 20.0, 0.7),
]

# ---------------------------------------------------------------- temperature story (°C, design time)
def temp(t):
    T = -1.0
    T += -8.4 * sstep(t, B(6) + 0.6, 3.0)          # the cold: -1 -> -9
    T += 8.4 * sstep(t, B(7) + 0.1, 0.6)           # back to -1 for the comparison
    T += -8.4 * sstep(t, B(8) + 0.1, 1.2)          # -9 again
    T += -11.7 * sstep(t, B(9) + 0.3, 2.6)         # -21: the wall
    return T

def coldk(T):   return clamp((-1.0 - T) / 8.0)     # 0 at -1 °C, 1 at -9 °C
def freezek(T): return clamp((-9.0 - T) / 12.0)    # 1 at -21 °C

def melt_rate(T):
    """px of pit growth per second: fast at -1, ~1/8 at -9, zero at -21 (as the melt table)."""
    if T <= -21: return 0.0
    if T >= -1: return 22.0
    if T >= -9: return lerp(22.0, 22.0 * 6.3 / 46.3 / 3, (-1 - T) / 8)   # less ice AND slower
    return lerp(22.0 * 6.3 / 46.3 / 3, 0.0, (-9 - T) / 12)

DT = 1 / 60
T_END = ST[-1] + 6.0
T_START = B(2) + 0.4          # salt starts dissolving with beat 3

def _integrate():
    cum, out = 0.0, []
    n = int(T_END / DT) + 2
    for k in range(n):
        t = k * DT
        out.append(cum)
        if t >= T_START:
            cum += melt_rate(temp(t)) * DT
    return out
CUM = _integrate()
D_MAX = 150.0
def pit_depth(t):
    c = CUM[int(clamp(t / DT, 0, len(CUM) - 1))]
    return D_MAX * (1 - math.exp(-c / D_MAX))

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    T = temp(t)
    s['T'] = T
    s['cold'] = coldk(T)
    s['freeze'] = freezek(T)
    s['fh'] = lerp(16.0, 4.0, s['cold']) * (1 - s['freeze'])
    s['d'] = pit_depth(t)
    s['fall'] = clamp(t / 0.9)                                   # grains drop in during the hook
    s['film'] = max(win(t, 0.9, B(2) + 0.2, 0.25), bw(t, 6))      # film highlighted
    s['melt'] = win(t, B(4) + 0.4, B(5) + 0.2, 0.3)               # melting arrows
    s['crew'] = sstep(t, B(10) + 0.2, 0.8)                        # new pellets / sand fall
    return s

def cam_keys():
    return [(0, 540, 850, 1.9), (B(1) + 3.2, 540, 980, 1.3), (B(4) + 0.2, 540, 1000, 1.55),
            (B(6), 540, 980, 1.3)]
def CAM(t):
    return cam_track(cam_keys(), t, 0.9)

# ---------------------------------------------------------------- drawing
def asphalt(ctx):
    ctx.rectangle(-200, Y_ASPH, 1480, 600); setc(ctx, ASPH); ctx.fill()
    rnd = random.Random(11)
    for i in range(70):
        x = rnd.uniform(-150, 1230); y = rnd.uniform(Y_ASPH + 18, 1500)
        r = rnd.uniform(10, 26)
        n = 6
        for k in range(n):
            a = k * 2 * math.pi / n + rnd.uniform(-0.3, 0.3)
            rr = r * rnd.uniform(0.7, 1.1)
            (ctx.move_to if k == 0 else ctx.line_to)(x + rr * math.cos(a), y + rr * 0.7 * math.sin(a))
        ctx.close_path(); setc(ctx, STONE if i % 2 else STONE_L); ctx.fill()
    ctx.move_to(-200, Y_ASPH); ctx.line_to(1280, Y_ASPH); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()

def pit_path(ctx, x, d, w):
    """cavity into the ice, opening at the ice top (y = Y_ICE), bottom at Y_ICE + d."""
    ctx.move_to(x - w, Y_ICE)
    ctx.curve_to(x - w, Y_ICE + d * 0.7, x - w * 0.55, Y_ICE + d, x, Y_ICE + d)
    ctx.curve_to(x + w * 0.55, Y_ICE + d, x + w, Y_ICE + d * 0.7, x + w, Y_ICE)
    ctx.close_path()

def pit_dims(g, s):
    x, size, tilt, k = g
    d = s['d'] * k
    w = size * 0.55 + d * 0.35
    return x, d, w

def ice(ctx, t, s):
    c, f = s['cold'], s['freeze']
    g = cairo.LinearGradient(0, Y_ICE, 0, Y_ASPH)
    g.add_color_stop_rgba(0, *lerpc(ICE, hexc('#eef7fa'), c)[:3], 1)
    g.add_color_stop_rgba(1, *ICE_D[:3], 1)
    ctx.rectangle(-200, Y_ICE, 1480, Y_ASPH - Y_ICE); ctx.set_source(g); ctx.fill()
    # bubbles / streaks inside the ice
    rnd = random.Random(5)
    for i in range(26):
        x = rnd.uniform(-150, 1230); y = rnd.uniform(Y_ICE + 40, Y_ASPH - 20)
        ctx.arc(x, y, rnd.uniform(3, 7), 0, 6.28); setc(ctx, WHITE, 0.8); ctx.fill_preserve()
        setc(ctx, ICE_D, 0.9); ctx.set_line_width(1.5); ctx.stroke()
    for i in range(8):
        x = rnd.uniform(-100, 1180); y = rnd.uniform(Y_ICE + 60, Y_ASPH - 40)
        ctx.move_to(x, y); ctx.line_to(x + rnd.uniform(30, 70), y + rnd.uniform(-20, 20))
        setc(ctx, WHITE, 0.7); ctx.set_line_width(3); ctx.stroke()
    # brine pits under the grains (or frozen brine)
    for gr in GRAINS:
        x, d, w = pit_dims(gr, s)
        if d < 1: continue
        pit_path(ctx, x, d, w)
        setc(ctx, lerpc(BRINE, hexc('#e9f4f6'), f), 0.85); ctx.fill_preserve()
        setc(ctx, lerpc(hexc('#125f5f'), ICE_D, f)); ctx.set_line_width(4); ctx.stroke()
        if f > 0.05:        # frozen: white hatch
            ctx.save(); pit_path(ctx, x, d, w); ctx.clip()
            for k in range(-20, 20):
                xx = x + k * 16
                ctx.move_to(xx, Y_ICE); ctx.line_to(xx + 60, Y_ICE + 220)
            setc(ctx, WHITE, 0.9 * f); ctx.set_line_width(3); ctx.stroke(); ctx.restore()
    ctx.move_to(-200, Y_ICE); ctx.line_to(1280, Y_ICE); setc(ctx, INK2, 0.5); ctx.set_line_width(2); ctx.stroke()

def ions(ctx, t, s):
    """dissolved salt in the brine: small teal / mustard dots jiggling (fade when frozen)."""
    a = (1 - s['freeze']) * sstep(t, T_START, 0.6)
    if a <= 0: return
    rnd = random.Random(21)
    for gr in GRAINS:
        x, d, w = pit_dims(gr, s)
        n = int(4 + d / 12)
        for i in range(n):
            u = rnd.uniform(-0.8, 0.8); v = rnd.uniform(0.15, 0.85)
            ph = rnd.uniform(0, 6.28)
            px = x + u * w + 5 * math.sin(t * 3 + ph)
            py = Y_ICE + v * d * (1 - abs(u) * 0.6) + 4 * math.cos(t * 2.6 + ph)
            ctx.arc(px, py, 5, 0, 6.28); setc(ctx, MUSTARD if i % 2 else WHITE, a); ctx.fill()

def film(ctx, t, s):
    fh = s['fh']
    if fh <= 0.3: return
    y0 = Y_ICE - fh
    ctx.rectangle(-200, y0, 1480, fh); setc(ctx, WATER, 0.85); ctx.fill()
    ctx.move_to(-200, y0); ctx.line_to(1280, y0); setc(ctx, hexc('#1d5f99')); ctx.set_line_width(2.5); ctx.stroke()
    # brine spreads in the film around each grain (teal band)
    a = sstep(t, T_START, 0.8)
    if a > 0:
        for gr in GRAINS:
            x, d, w = pit_dims(gr, s)
            ww = w + 30 + d * 1.2
            g = cairo.LinearGradient(x - ww, 0, x + ww, 0)
            g.add_color_stop_rgba(0, *BRINE[:3], 0)
            g.add_color_stop_rgba(0.5, *BRINE[:3], 0.95 * a)
            g.add_color_stop_rgba(1, *BRINE[:3], 0)
            ctx.rectangle(x - ww, y0, 2 * ww, fh); ctx.set_source(g); ctx.fill()

def frost(ctx, t, s):
    c = s['cold']
    if c < 0.02: return
    rnd = random.Random(3)
    for i in range(46):
        x = rnd.uniform(-150, 1230)
        if any(abs(x - g[0]) < g[1] for g in GRAINS): continue
        y = Y_ICE - s['fh'] - rnd.uniform(0, 3)
        l = rnd.uniform(6, 13)
        for k in range(3):
            a = k * math.pi / 3
            ctx.move_to(x - l * math.cos(a), y - l * math.sin(a))
            ctx.line_to(x + l * math.cos(a), y + l * math.sin(a))
        setc(ctx, FROST, 0.95 * c); ctx.set_line_width(2.5); ctx.stroke()
        ctx.move_to(x - l, y); ctx.line_to(x + l, y); setc(ctx, ICE_D, 0.5 * c); ctx.set_line_width(1); ctx.stroke()

def grain_size(gr, s):
    x, size, tilt, k = gr
    return size * (1 - 0.5 * s['d'] / D_MAX)

def cube(ctx, cx, cy, sz, tilt, a=1.0):
    """salt crystal: a small cube (front face + top face), resting so its bottom is at cy + sz/2."""
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(math.radians(tilt))
    h = sz / 2
    dpx, dpy = sz * 0.28, -sz * 0.22
    ctx.move_to(-h, -h); ctx.line_to(-h + dpx, -h + dpy); ctx.line_to(h + dpx, -h + dpy); ctx.line_to(h, -h); ctx.close_path()
    fill_stroke(ctx, SALT, lw=4, alpha=a)
    ctx.move_to(h, -h); ctx.line_to(h + dpx, -h + dpy); ctx.line_to(h + dpx, h + dpy); ctx.line_to(h, h); ctx.close_path()
    fill_stroke(ctx, SALT_S, lw=4, alpha=a)
    ctx.rectangle(-h, -h, sz, sz); fill_stroke(ctx, hexc('#f3f5f7'), lw=4, alpha=a)
    ctx.move_to(-h + 8, -h + 10); ctx.line_to(-h + 8, h - 14); setc(ctx, WHITE, a); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()

def grains(ctx, t, s):
    for i, gr in enumerate(GRAINS):
        x, size, tilt, k = gr
        sz = grain_size(gr, s)
        x0, d, w = pit_dims(gr, s)
        rest = Y_ICE - s['fh'] - sz / 2 + d * 0.75          # sinks into its own pit (y grows down)
        fall = clamp((t - 0.12 * i) / 0.8)
        y = lerp(rest - 700, rest, ease(fall) ** 2 if fall < 1 else 1)
        if fall <= 0: continue
        cube(ctx, x, y, sz, tilt * (1 - 0.3 * fall))

def melt_arrows(ctx, t, s):
    a = s['melt']
    if a <= 0: return
    x, d, w = pit_dims(GRAINS[0], s)
    # outward normals of the pit wall (melting front moves AWAY from the brine, into the ice)
    # pit ~ lower half-ellipse centred (x, Y_ICE), semi-axes w (across) and d (down); th in (0, pi) = below (y down)
    for deg in (25, 60, 90, 120, 155):
        th = math.radians(deg)
        px, py = x + w * math.cos(th), Y_ICE + d * math.sin(th)
        nx, ny = math.cos(th) / max(w, 1), math.sin(th) / max(d, 1)
        L = math.hypot(nx, ny); nx, ny = nx / L, ny / L               # outward normal, into the ice
        straight_arrow(ctx, px + 6 * nx, py + 6 * ny, px + 60 * nx, py + 60 * ny, RED, a, lw=5, head=10)

def crew(ctx, t, s):
    k = s['crew']
    if k <= 0: return
    a = 1 - sstep(t, B(11) + 0.4, 0.5)
    if a <= 0: return
    rnd = random.Random(8)
    for i in range(10):          # calcium chloride pellets, left half
        x = rnd.uniform(140, 440); r = rnd.uniform(15, 21)
        yr = Y_ICE - s['fh'] - r
        fall = clamp((t - B(10) - 0.2 - i * 0.05) / 0.7)
        y = lerp(yr - 650, yr, ease(fall) ** 2)
        if fall > 0:
            ctx.arc(x, y, r, 0, 6.28); fill_stroke(ctx, hexc('#f6f4ee'), lw=3, alpha=a)
    for i in range(22):          # sand, right half
        x = rnd.uniform(640, 940); r = rnd.uniform(7, 11)
        yr = Y_ICE - s['fh'] - r
        fall = clamp((t - B(10) - 2.2 - i * 0.03) / 0.7)
        y = lerp(yr - 650, yr, ease(fall) ** 2)
        if fall > 0:
            ctx.arc(x, y, r, 0, 6.28); fill_stroke(ctx, SAND, lw=2, alpha=a)

def snow(ctx, t, s):
    c = max(s['cold'], s['freeze'])
    if c < 0.05: return
    rnd = random.Random(14)
    for i in range(30):
        x0 = rnd.uniform(0, 1080); sp = rnd.uniform(40, 80); ph = rnd.uniform(0, 600)
        y = 300 + (ph + t * sp) % 560            # falls DOWN
        x = x0 + 12 * math.sin(t + i)
        ctx.arc(x, y, rnd.uniform(3, 6), 0, 6.28); setc(ctx, WHITE, 0.9 * c); ctx.fill_preserve()
        setc(ctx, INK2, 0.3 * c); ctx.set_line_width(1); ctx.stroke()

def stage(ctx, t, s):
    snow(ctx, t, s)
    asphalt(ctx)
    ice(ctx, t, s)
    ions(ctx, t, s)
    film(ctx, t, s)
    frost(ctx, t, s)
    grains(ctx, t, s)
    melt_arrows(ctx, t, s)
    crew(ctx, t, s)

def overlays(ctx, t, s):
    # the film (hook + secret)
    a = s['film']
    if a > 0:
        highlight(ctx, 400, Y_ICE - s['fh'] / 2, 150, 26, WATER, a, t)
        tag(ctx, "WATER FILM", 400, 945 if t < B(1) + 3.2 else 830, hexc('#1d5f99'), a, 20 if t < B(1) + 3.2 else 26)
    tag(ctx, "(ENLARGED)", 400, 985, INK2, win(t, B(1) + 0.4, B(1) + 3.2, 0.3), 16)
    a = win(t, B(2) + 1.2, B(3), 0.3)
    tag(ctx, "BRINE", 540, 1000, BRINE, a, 26)
    a = bw(t, 3)
    tag(ctx, "STAYS LIQUID", 540, 1030, BRINE, a, 24)
    a = win(t, B(4) + 1.2, B(5), 0.3)
    tag(ctx, "ICE MELTS", 540, 1150, RED, a, 24)
    a = win(t, B(6) + 1.0, B(7), 0.3)
    tag(ctx, "THINNER FILM", 400, 820, hexc('#1d5f99'), a, 26)
    a = win(t, B(9) + 2.8, B(10), 0.3)
    tag(ctx, "BRINE FREEZES", 540, 1150, INK, a, 26)
    a = win(t, B(10) + 0.8, B(11) + 0.4, 0.3)
    tag(ctx, "CALCIUM CHLORIDE", 300, 770, BRINE, a, 22)
    a = win(t, B(10) + 2.8, B(11) + 0.4, 0.3)
    tag(ctx, "SAND · GRIP ONLY", 790, 770, hexc('#8a5f22'), a, 22)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    stage(ctx, t, s)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def fmt_c(T):
    F = round(T * 9 / 5 + 32) + 0
    return f"{round(T) + 0:d} °C · {F:d} °F".replace('-', '−')

def _panel(ctx, a, x=60, y=175, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def draw_hud(ctx, t, E):
    s = state(t)
    T = s['T']
    # road temperature box (top left) when no panel is up
    a = max(win(t, 0.3, B(3), 0.25), win(t, B(4), B(5), 0.25), win(t, B(6), B(7), 0.25), win(t, B(9), B(11), 0.3))
    if a > 0:
        col = lerpc(TEAL, COLD, s['cold']) if s['freeze'] < 0.5 else INK
        hud(ctx, "ROAD SURFACE", fmt_c(T), None, a, lerpc(MUSTARD, COLD, s['cold']), x=40, y=190, w=520)
    # 2 · brine: plain water vs brine
    a = bw(t, 3)
    if a > 0:
        _panel(ctx, a, x=60, y=180, w=960, h=250)
        text_c(ctx, "PLAIN WATER FREEZES AT", 540, 240, 32, INK, True, 2, a)
        text_c(ctx, "0 °C · 32 °F", 540, 310, 60, WATER, True, 2, a)
        k = a * sstep(t, B(3) + 2.4, 0.3)
        text_c(ctx, "BRINE: MUCH COLDER", 540, 385, 40, BRINE, True, 2, k)
    # minus one: the melt number
    a = bw(t, 7)
    if a > 0:
        _panel(ctx, a, x=60, y=180, w=960, h=270)
        text_c(ctx, "AT −1 °C · 30 °F", 540, 240, 36, MUSTARD, True, 2, a)
        text_c(ctx, "1 kg SALT", 540, 310, 52, INK, True, 2, a * sstep(t, B(7) + 1.8, 0.3))
        text_c(ctx, "MELTS 46 kg ICE", 540, 380, 64, RED, True, 2, a * sstep(t, B(7) + 3.0, 0.3))
        text_c(ctx, "WITHIN MINUTES", 540, 430, 26, INK2, True, 2, a * sstep(t, B(7) + 4.8, 0.3))
    # the wall
    a = win(t, B(9) + 2.6, B(10), 0.3)
    if a > 0:
        hud(ctx, "SATURATED BRINE · 23 % SALT", "FROZEN", None, a, RED, x=520, y=330, w=520)
    # recap
    a = win(t, B(11) + 0.2, B(12) + 2, 0.3)
    if a > 0:
        _panel(ctx, a, x=90, y=200, w=900, h=150)
        text_c(ctx, "SALT + WATER = BRINE", 540, 262, 44, BRINE, True, 2, a)
        text_c(ctx, "BRINE MELTS ICE", 540, 320, 34, RED, True, 2, a * sstep(t, B(11) + 1.2, 0.3))

SFX = [(0.9, 'pop'), (B(1) + 0.4, 'pop'), (B(2) + 1.2, 'pop'), (B(3) + 0.3, 'pop'), (B(3) + 2.4, 'pop'),
       (B(4) + 1.2, 'pop'), (B(6) + 1.0, 'pop'), (B(7) + 3.0, 'pop'), (B(9) + 2.6, 'click'),
       (B(10) + 0.8, 'pop'), (B(10) + 2.8, 'pop'), (B(11) + 0.2, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_chain(ctx, t, lt, a):
    card_frame(ctx, "A CHAIN REACTION", a, None)
    # 4 nodes on a loop, arrows go CLOCKWISE on screen: top -> right -> bottom -> left -> top
    cx, cy, rx, ry = 540, 400, 300, 115
    nodes = [("SALT", -90, INK), ("BRINE", 0, BRINE), ("ICE MELTS", 90, RED), ("NEW WATER", 180, WATER)]
    lit = int(clamp(lt / 0.9, 0, 4.99))
    for i in range(4):          # arrows between consecutive nodes, clockwise (angle increasing, y down)
        a0 = math.radians(nodes[i][1] + 26); a1 = math.radians(nodes[i][1] + 64)
        ka = a * (0.35 + 0.65 * (1 if lt > 0.9 * (i + 1) - 0.4 else 0))
        ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry)
        ctx.arc(0, 0, 1, a0, a1); ctx.restore()
        setc(ctx, INK, ka); ctx.set_line_width(5); ctx.stroke()
        hx, hy = cx + rx * math.cos(a1), cy + ry * math.sin(a1)
        tx, ty = -rx * math.sin(a1), ry * math.cos(a1)                  # tangent, direction of increasing angle
        L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
        straight_arrow(ctx, hx - 20 * tx, hy - 20 * ty, hx + 6 * tx, hy + 6 * ty, INK, ka, lw=5, head=11)
    for i, (lab, deg, col) in enumerate(nodes):
        x = cx + rx * math.cos(math.radians(deg)); y = cy + ry * math.sin(math.radians(deg))
        on = 1.0 if (i <= lit or lt > 3.6) else 0.35
        tag(ctx, lab, x, y, col, a * on, 26)

def card_melt(ctx, t, lt, a):
    card_frame(ctx, "SAME 1 kg OF SALT", a, None)
    base = 520
    k = ease(clamp((lt - 0.3) / 1.6))
    k2 = ease(clamp((lt - 1.6) / 1.2))
    for cx, temp_s, kg, clock, col, kk in ((320, "−1 °C · 30 °F", 46.3, "MINUTES", MUSTARD, k),
                                            (760, "−9 °C · 15 °F", 6.3, "1 HOUR", COLD, k2)):
        h = 190 * (kg / 46.3) * kk
        rrect(ctx, cx - 90, base - h, 180, max(h, 1), 10); fill_stroke(ctx, ICE, stroke=ICE_D, lw=4, alpha=a)
        ctx.move_to(cx - 150, base); ctx.line_to(cx + 150, base); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        text_c(ctx, temp_s, cx, 270, 30, col, True, 1.5, a)
        text_c(ctx, f"{kg:.0f} kg ICE", cx, base - h - 18, 34, INK, True, 1, a * kk)
        text_c(ctx, clock, cx, 572, 28, INK2, True, 1.5, a * kk)
        # small clock face
        ctx.arc(cx + 125, 562, 20, 0, 6.28); fill_stroke(ctx, WHITE, lw=3, alpha=a * kk)
        hand = math.radians(-90) + (lt * (1.2 if cx < 500 else 6.0))
        ctx.move_to(cx + 125, 562); ctx.line_to(cx + 125 + 14 * math.cos(hand), 562 + 14 * math.sin(hand))
        setc(ctx, INK, a * kk); ctx.set_line_width(3); ctx.stroke()

CARDS = {'chain': card_chain, 'melt': card_melt}
