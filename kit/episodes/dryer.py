"""Cogwise episode: This dryer dries your clothes with cold metal.
One idea: warm air can hold far more water than cold air (≈17 g/m³ at 20 °C vs ≈83 g/m³ at 50 °C),
so a heat-pump dryer heats the air (thirsty air), then a cold coil makes the water rain out.
The same air goes round and round (closed loop, no vent); the heat pump moves the heat taken
at the cold coil back into the hot coil.

FRONT VIEW, cut away. Screen coordinates: y grows DOWN.
Air loop (simplified, arrows follow it): hot coil -> fan -> right duct UP -> into the drum (top right)
-> through the clothes -> out of the drum (bottom left) -> left duct DOWN -> COLD coil -> HOT coil.
Water: drops form on the cold coil fins and fall DOWN into the tray / tank, then out by a hose.
Refrigerant: cold coil (evaporator) -> compressor -> hot coil (condenser) -> valve -> cold coil.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="dryer",
    title="This heat pump dryer dries your clothes with cold metal ❄️",
    description=("Warm air can hold about five times more water than cold air. A heat pump dryer heats the air, "
                 "then a cold coil makes the water rain out.\n\n#Shorts #howthingswork #dryer #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "dryer", "appliances", "engineering", "cogwise"],
    sources=[
        "https://energy.ec.europa.eu/news/new-measures-more-energy-efficient-household-tumble-dryers-1-july-2025-07-01_en",
        "https://www.elektroda.com/qa,bosch-heat-pump-dryer-working.html",
        "https://www.engineeringtoolbox.com/maximum-moisture-content-air-d_1403.html",
        "https://pressbooks.online.ucf.edu/phy2053bc/chapter/humidity-evaporation-and-boiling/",
    ],
)

BEATS = [
    dict(dur=4.6, title="HEAT PUMP DRYER", caption="This heat pump dryer dries your clothes… with a cold metal coil."),
    dict(dur=5.0, title="THE SECRET", caption="The trick: warm air can hold far more water than cold air."),
    dict(dur=7.5, title=None, caption="Warm air from twenty to fifty Celsius, sixty-eight to one twenty-two Fahrenheit: it holds five times more water.", card='cubes'),
    dict(dur=6.0, title="1 · HOT COIL", caption="First, a hot coil warms the air, and a fan blows it through your clothes."),
    dict(dur=7.0, title="THIRSTY AIR", caption="The warm air soaks up the water. Without heat, it would fill up fast and drying would stall."),
    dict(dur=4.2, title="2 · COLD COIL", caption="Then that soggy air is pushed across a cold coil."),
    dict(dur=5.4, title=None, caption="Cold air can't hold all that water, so it rains out as droplets.", card='rain'),
    dict(dur=5.6, title="NO VENT", caption="The drops run into a tank or a drain hose. No air goes outside."),
    dict(dur=5.0, title="3 · HEAT PUMP", caption="Both coils form that heat pump, the same loop as your fridge."),
    dict(dur=5.6, title="HEAT RECYCLED", caption="Heat pulled out at the cold coil goes straight back into the hot one."),
    dict(dur=4.8, title="GENTLER", caption="So your clothes stay cooler, and it uses much less electricity."),
    dict(dur=6.0, title="RECAP", caption="Heat makes the air thirsty. Cold wrings it out. Same air, round and round."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
CAB = (200, 400, 680, 1060)            # x 200..880, y 400..1460
DC, DR = (540, 760), 262               # drum centre / radius (x 278..802, y 498..1022)
CC = (310, 1182, 140, 106)             # cold coil box x 310..450, y 1182..1288
HC = (560, 1182, 140, 106)             # hot coil box  x 560..700, y 1182..1288
FAN = (772, 1235, 40)
TRAY = (296, 1318, 172, 46)            # tray / tank under the cold coil
COMP = (520, 1400)                     # compressor centre (base)
AIRY = 1235                            # base duct centre line
LDX, RDX = 244, 846                    # left / right duct x

STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); CABC = hexc('#f4f1ea'); DUCT = hexc('#e3ddd0')
CLOTH = [hexc('#8fcfc8'), hexc('#f2b134'), hexc('#e98f8f'), hexc('#b9c7e8')]
WATER = hexc('#3a8fd0'); HOTC = hexc('#e4472f'); COLDC = hexc('#1f8a8a')

# ---------------------------------------------------------------- air path (direction = list order)
def _ang(a): return (DC[0] + DR * math.cos(math.radians(a)), DC[1] + DR * math.sin(math.radians(a)))
_IN = _ang(-40)     # inlet, top right of the drum
_OUT = _ang(140)    # outlet, bottom left of the drum
AIR = [
    ((450, AIRY), 'cool'), ((560, AIRY), 'cool'),                    # between the coils (cool, dry)
    ((700, AIRY), 'heat'),                                           # through the hot coil
    ((RDX, AIRY), 'hot'), ((RDX, 560), 'hot'), ((_IN[0] + 20, 560), 'hot'), (_IN, 'hot'),
    ((640, 700), 'drum'), ((540, 790), 'drum'), ((430, 880), 'drum'), (_OUT, 'drum'),
    ((LDX, 990), 'wet'), ((LDX, AIRY), 'wet'), ((310, AIRY), 'wet'),
    ((450, AIRY), 'chill'),                                          # through the cold coil
]
PTS = [p for p, _ in AIR]; KIND = [k for _, k in AIR]
CUM = [0.0]
for i in range(1, len(PTS)): CUM.append(CUM[-1] + math.dist(PTS[i - 1], PTS[i]))
PLEN = CUM[-1]

def air_at(s):
    s %= PLEN
    for i in range(1, len(PTS)):
        if CUM[i] >= s:
            u = (s - CUM[i - 1]) / max(1e-6, CUM[i] - CUM[i - 1])
            return (lerp(PTS[i - 1][0], PTS[i][0], u), lerp(PTS[i - 1][1], PTS[i][1], u)), KIND[i], u
    return PTS[-1], KIND[-1], 1.0

def air_col(k, u):
    warm = ORANGE; cool = VAPOR
    if k == 'cool': return cool
    if k == 'heat': return lerpc(cool, warm, u)
    if k in ('hot', 'drum', 'wet'): return warm
    if k == 'chill': return lerpc(warm, cool, u)
    return cool

def wet_amount(k, u):
    """how much water the air carries (0 dry .. 1 soggy) along the loop"""
    if k == 'drum': return 0.3 + 0.7 * u
    if k == 'wet': return 1.0
    if k == 'chill': return 1 - u
    return 0.0

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['flow'] = 210 * t + (120 * max(0, t - B(11)))
    s['spin'] = t * 1.3
    s['drip'] = 1.0
    s['tag_coldmetal'] = win(t, 0.3, B(1) + 0.4, 0.3)
    s['h_hot'] = bw(t, 3); s['l_hot'] = max(bw(t, 3, 5), bw(t, 8, 10), bw(t, 11, 12))
    s['h_cold'] = max(win(t, 0.2, B(1) + 0.4, 0.25), bw(t, 5), bw(t, 7)); s['l_cold'] = max(bw(t, 5, 8), bw(t, 8, 10), bw(t, 11, 12))
    s['h_fan'] = bw(t, 3)
    s['evap_w'] = max(bw(t, 4), 0.6 * bw(t, 11))           # water leaving the clothes
    s['tray'] = bw(t, 7); s['novent'] = bw(t, 7)
    s['ref'] = clamp(ease((t - B(8)) / 0.8))                  # refrigerant loop revealed
    s['h_hp'] = bw(t, 8); s['l_hp'] = max(bw(t, 8, 10), bw(t, 11, 12))
    s['heatmove'] = max(bw(t, 9), 0.8 * bw(t, 11))
    s['recap'] = bw(t, 11)
    s['water_lvl'] = 0.25 + 0.5 * clamp((t - B(5)) / (B(8) - B(5)))
    return s

# ---------------------------------------------------------------- parts
def coil(ctx, x, y, w, h, col, light, t, a=1.0):
    rrect(ctx, x, y, w, h, 8); fill_stroke(ctx, light, lw=5, alpha=a)
    for i in range(1, 11):
        xx = x + i * w / 11
        ctx.move_to(xx, y + 6); ctx.line_to(xx, y + h - 6)
        setc(ctx, col, 0.75 * a); ctx.set_line_width(3); ctx.stroke()
    for j in range(3):          # tube passes (front ends)
        ctx.arc(x + 14 + j * 0.0, y + 22 + j * 31, 7, 0, 2 * math.pi); setc(ctx, col, a); ctx.fill()
        ctx.arc(x + w - 14, y + 22 + j * 31, 7, 0, 2 * math.pi); setc(ctx, col, a); ctx.fill()

def fan(ctx, cx, cy, r, ang, a=1.0):
    ctx.arc(cx, cy, r + 8, 0, 2 * math.pi); fill_stroke(ctx, hexc('#efe9dc'), lw=4, alpha=a)
    for k in range(4):
        aa = ang + k * math.pi / 2
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(aa)
        ctx.move_to(0, 0); ctx.curve_to(r * 0.4, -r * 0.35, r * 0.95, -r * 0.2, r * 0.9, r * 0.12)
        ctx.curve_to(r * 0.6, r * 0.2, r * 0.3, r * 0.1, 0, 0); ctx.restore()
        fill_stroke(ctx, STEEL, lw=3, alpha=a)
    ctx.arc(cx, cy, 8, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()

def drop(ctx, x, y, r, a, col=WATER):
    ctx.move_to(x, y - 2.2 * r); ctx.curve_to(x + r * 0.6, y - r, x + r, y - r * 0.3, x + r, y + r * 0.2)
    ctx.curve_to(x + r, y + r * 1.3, x - r, y + r * 1.3, x - r, y + r * 0.2)
    ctx.curve_to(x - r, y - r * 0.3, x - r * 0.6, y - r, x, y - 2.2 * r); ctx.close_path()
    setc(ctx, col, a); ctx.fill_preserve(); setc(ctx, INK, 0.6 * a); ctx.set_line_width(2); ctx.stroke()

def draw_ducts(ctx):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    segs = [[(LDX, 990), (LDX, AIRY), (RDX, AIRY), (RDX, 560), (_IN[0] + 20, 560)], [_OUT, (LDX, 990)]]
    for lw, col in ((62, INK2), (52, DUCT)):
        for sg in segs:
            ctx.move_to(*sg[0])
            for p in sg[1:]: ctx.line_to(*p)
            setc(ctx, col); ctx.set_line_width(lw); ctx.stroke()
    # direction chevrons (follow the air loop)
    for (x, y, ang) in [(LDX, 1100, 90), (RDX, 900, -90), (RDX, 700, -90), (790, 560, 180), (500, AIRY, 0)]:
        ctx.save(); ctx.translate(x, y); ctx.rotate(math.radians(ang))
        ctx.move_to(-8, -13); ctx.line_to(6, 0); ctx.line_to(-8, 13)
        setc(ctx, INK2, 0.55); ctx.set_line_width(4); ctx.stroke(); ctx.restore()

def draw_drum(ctx, t, s):
    cx, cy = DC
    ctx.arc(cx, cy, DR + 16, 0, 2 * math.pi); fill_stroke(ctx, hexc('#dfe3e1'), lw=6)
    ctx.arc(cx, cy, DR, 0, 2 * math.pi); fill_stroke(ctx, hexc('#eef0ee'), lw=4)
    ph = s['spin']
    for k in range(36):
        aa = ph + k * 2 * math.pi / 36
        ctx.arc(cx + (DR - 18) * math.cos(aa), cy + (DR - 18) * math.sin(aa), 3.5, 0, 2 * math.pi)
        setc(ctx, STEEL_D); ctx.fill()
    # tumbling clothes (pile low in the drum, lifted a little by the turn)
    ctx.save(); ctx.arc(cx, cy, DR - 6, 0, 2 * math.pi); ctx.clip()
    rnd = random.Random(5)
    for i in range(18):
        base = rnd.uniform(-1, 1)
        x = cx + base * 175 + 18 * math.sin(t * 1.7 + i)
        y = cy + 150 - abs(base) * 30 - rnd.uniform(0, 90) + 14 * math.cos(t * 1.9 + i * 1.3)
        ctx.arc(x, y, rnd.uniform(32, 46), 0, 2 * math.pi)
        setc(ctx, CLOTH[i % 4]); ctx.fill_preserve(); setc(ctx, INK2, 0.5); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    for k in range(3):       # lifters
        aa = ph + k * 2 * math.pi / 3
        ctx.save(); ctx.translate(cx + (DR - 22) * math.cos(aa), cy + (DR - 22) * math.sin(aa)); ctx.rotate(aa)
        rrect(ctx, -18, -14, 36, 28, 7); fill_stroke(ctx, STEEL, lw=3); ctx.restore()
    # water leaving the clothes (blue specks rising into the warm air)
    if s['evap_w'] > 0:
        rnd = random.Random(9)
        for i in range(16):
            ph2 = (t * 0.7 + rnd.random()) % 1
            x0 = cx + rnd.uniform(-150, 150); y0 = cy + 130
            x = x0 - 40 * ph2; y = y0 - 160 * ph2
            ctx.arc(x, y, 6, 0, 2 * math.pi); setc(ctx, WATER, s['evap_w'] * (1 - ph2)); ctx.fill()
    # door ring (front face cut away)
    ctx.arc(cx, cy, 170, 0, 2 * math.pi); ctx.set_dash([8, 8]); setc(ctx, INK2, 0.6); ctx.set_line_width(3)
    ctx.stroke(); ctx.set_dash([])

def draw_air(ctx, t, s, n=46):
    for i in range(n):
        p, k, u = air_at(i * PLEN / n + s['flow'])
        c = air_col(k, u)
        ctx.arc(p[0], p[1], 8, 0, 2 * math.pi); setc(ctx, c, 0.95); ctx.fill_preserve()
        setc(ctx, INK, 0.35); ctx.set_line_width(1.5); ctx.stroke()
        w = wet_amount(k, u)
        if w > 0.05:                     # water carried by the air: small blue dots riding along
            for j in range(2):
                ctx.arc(p[0] + 9 * math.cos(i + j * 2.6), p[1] + 9 * math.sin(i + j * 2.6), 4, 0, 2 * math.pi)
                setc(ctx, WATER, w); ctx.fill()

def draw_refrigerant(ctx, t, s):
    a = s['ref']
    if a <= 0: return
    # cold coil bottom -> compressor (suction), compressor -> hot coil bottom (discharge),
    # hot coil top -> over the duct -> valve -> cold coil top
    loop = [(430, 1290), (430, 1300), (478, 1300), (478, 1368),          # suction down to compressor
            (562, 1368), (562, 1300), (600, 1300), (600, 1290),          # discharge up to hot coil
            (680, 1180), (680, 1150), (530, 1150), (380, 1150), (380, 1180)]   # liquid back over the top
    cols = [COLDC, COLDC, COLDC, COLDC, HOTC, HOTC, HOTC, HOTC, HOTC, ORANGE, ORANGE, COLDC, COLDC]   # cold after the valve
    for lw, kind in ((9, 0), (4, 1)):
        for i in range(1, len(loop)):
            if (loop[i - 1] == (478, 1368)): continue          # hidden inside the compressor
            ctx.move_to(*loop[i - 1]); ctx.line_to(*loop[i])
            setc(ctx, INK if kind == 0 else cols[i], a); ctx.set_line_width(lw); ctx.stroke()
    # expansion valve on the top pipe
    rrect(ctx, 516, 1138, 28, 24, 5); fill_stroke(ctx, MUSTARD, lw=3, alpha=a)
    # compressor dome
    x, y = COMP
    vib = math.sin(t * 60) * 1.5
    ctx.save(); ctx.translate(vib, 0)
    ctx.move_to(x - 52, 1450); ctx.line_to(x - 52, 1392); ctx.curve_to(x - 52, 1336, x + 52, 1336, x + 52, 1392)
    ctx.line_to(x + 52, 1450); ctx.close_path(); fill_stroke(ctx, hexc('#3b3842'), lw=5, alpha=a)
    ctx.arc(x, 1395, 9, 0, 2 * math.pi); setc(ctx, hexc('#8d8792'), a); ctx.fill()
    ctx.restore()

def draw_machine(ctx, t, s):
    x, y, w, h = CAB
    for fx in (x + 60, x + w - 60):
        rrect(ctx, fx - 30, y + h - 4, 60, 34, 6); fill_stroke(ctx, hexc('#5f6a73'), lw=4)
    rrect(ctx, x, y, w, h, 18); fill_stroke(ctx, CABC, lw=6)
    rrect(ctx, x + 18, y + 18, w - 36, h - 36, 10); setc(ctx, hexc('#e9e4d8')); ctx.fill()
    # control strip
    rrect(ctx, x + 30, y + 26, w - 60, 42, 10); fill_stroke(ctx, hexc('#e2dccf'), lw=3)
    ctx.arc(x + w - 80, y + 47, 14, 0, 2 * math.pi); fill_stroke(ctx, WHITE, lw=3)
    # base shelf line
    ctx.move_to(x + 18, 1150); ctx.line_to(x + w - 18, 1150); setc(ctx, INK2, 0.25); ctx.set_line_width(3); ctx.stroke()

    draw_ducts(ctx)
    draw_drum(ctx, t, s)
    # tray / tank under the cold coil + hose out through the side
    tx, ty, tw, th = TRAY
    lvl = s['water_lvl']
    rrect(ctx, tx, ty, tw, th, 8); fill_stroke(ctx, hexc('#f1ece0'), lw=4)
    rrect(ctx, tx + 5, ty + th - 5 - (th - 10) * lvl, tw - 10, (th - 10) * lvl, 4); setc(ctx, WATER, 0.75); ctx.fill()
    ctx.move_to(tx, ty + th - 10); ctx.curve_to(240, ty + th - 10, 190, 1380, 160, 1440)
    setc(ctx, INK2); ctx.set_line_width(14); ctx.stroke()
    ctx.move_to(tx, ty + th - 10); ctx.curve_to(240, ty + th - 10, 190, 1380, 160, 1440)
    setc(ctx, hexc('#cfc8b8')); ctx.set_line_width(8); ctx.stroke()

    draw_refrigerant(ctx, t, s)
    # coils
    coil(ctx, *CC, COLDC, hexc('#cfe9e6'), t)
    coil(ctx, *HC, HOTC, hexc('#f6cfc2'), t)
    # frost sparkle on the cold coil + drops forming and falling DOWN into the tray
    cx0, cy0, cw, ch = CC
    rnd = random.Random(2)
    for i in range(7):
        ph = (t * 0.9 + rnd.random()) % 1
        xx = cx0 + 14 + i * (cw - 28) / 6
        if ph < 0.55:                                 # bead grows under the coil
            drop(ctx, xx, cy0 + ch + 2, 2 + 7 * ph / 0.55, 1.0)
        else:                                          # falls (y increases = down)
            fy = cy0 + ch + 2 + (ph - 0.55) / 0.45 * (TRAY[1] + 8 - cy0 - ch)
            drop(ctx, xx, fy, 6, 1 - (ph - 0.55) / 0.45 * 0.3)
    # glow on the hot coil
    g = cairo.RadialGradient(HC[0] + 70, AIRY, 10, HC[0] + 70, AIRY, 120)
    g.add_color_stop_rgba(0, *ORANGE[:3], 0.25); g.add_color_stop_rgba(1, *ORANGE[:3], 0)
    ctx.set_source(g); ctx.rectangle(HC[0] - 60, AIRY - 120, 260, 240); ctx.fill()

    fan(ctx, *FAN, s['spin'] * 6)
    draw_air(ctx, t, s)

    # heat moved by the heat pump: cold coil -> compressor -> hot coil (wavy = heat)
    a = s['heatmove']
    if a > 0:
        wavy_arrow(ctx, 380, 1300, 470, 1390, t, ORANGE, a, amp=8, wl=34, lw=6, head=14)
        wavy_arrow(ctx, 572, 1390, 650, 1300, t, RED, a, amp=8, wl=34, lw=6, head=14)
        wavy_arrow(ctx, 630, 1180, 630, 1080, t + 0.3, RED, a, amp=8, wl=34, lw=6, head=14)

    # "no vent": ghost vent hose at the back-right, crossed out
    a = s['novent']
    if a > 0:
        ctx.move_to(880, 640); ctx.curve_to(960, 640, 990, 600, 1030, 560)
        ctx.set_dash([14, 10]); setc(ctx, INK2, a); ctx.set_line_width(26); ctx.stroke(); ctx.set_dash([])
        for d in (1, -1):
            ctx.move_to(950 - 34, 610 - 34 * d); ctx.line_to(950 + 34, 610 + 34 * d)
            setc(ctx, RED, a); ctx.set_line_width(10); ctx.stroke()

    # highlights
    highlight(ctx, HC[0] + 70, AIRY, 100, 80, RED, s['h_hot'], t)
    highlight(ctx, FAN[0], FAN[1], 60, 60, RED, s['h_fan'], t)
    highlight(ctx, CC[0] + 70, AIRY + 30, 100, 100, COLDC, s['h_cold'], t)
    highlight(ctx, COMP[0], 1300, 210, 190, MUSTARD, s['h_hp'], t)

    # tags
    tag(ctx, "COLD METAL", 380, 1110, COLDC, s['tag_coldmetal'], 30)
    tag(ctx, "1 · HOT COIL", 640, 1105, RED, s['l_hot'])
    tag(ctx, "2 · COLD COIL", 360, 1060, COLDC, s['l_cold'])
    tag(ctx, "3 · HEAT PUMP", 745, 1425, MUSTARD, s['l_hp'])
    tag(ctx, "FAN", 840, 1330, RED, s['h_fan'], 24)
    tag(ctx, "WATER TANK", 330, 1505, WATER, s['tray'], 24)
    tag(ctx, "NO VENT", 960, 500, RED, s['novent'])
    tag(ctx, "HOT = THIRSTY", 760, 1040, RED, s['recap'], 26)
    tag(ctx, "COLD = WRING", 300, 990, COLDC, s['recap'], 26)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_machine(ctx, t, state(t))

# camera (co-pilot decision 3): open WIDE on the whole machine, cold coil circled from the 1st second, slow push-in
CAMKEYS = [(0, 540, 990, 1.0), (4.0, 540, 960, 1.08)]
def CAM(t): return cam_track(CAMKEYS, t, move=1.4)

def draw_hud(ctx, t, E):
    a = win(t, B(4) + 3.2, B(5), 0.3)
    if a > 0: hud(ctx, "WITHOUT HEAT", "AIR FULL", "drying stalls", a, RED, x=520, y=196, w=520)
    a = bw(t, 10)
    if a > 0: hud(ctx, "ELECTRICITY", "≈ HALF", "of a vented dryer", a, TEAL, x=520, y=196, w=520)

SFX = [(0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(5) + 0.3, 'pop'), (B(7) + 0.3, 'pop'),
       (B(8) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(11) + 0.3, 'pop'), (B(11) + 0.6, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def _cube(ctx, cx, cy, s, col, a):
    d = s * 0.32
    ctx.move_to(cx - s / 2, cy - s / 2); ctx.line_to(cx - s / 2 + d, cy - s / 2 - d)
    ctx.line_to(cx + s / 2 + d, cy - s / 2 - d); ctx.line_to(cx + s / 2, cy - s / 2); ctx.close_path()
    fill_stroke(ctx, lerpc(col, WHITE, 0.45), lw=4, alpha=a)
    ctx.move_to(cx + s / 2, cy - s / 2); ctx.line_to(cx + s / 2 + d, cy - s / 2 - d)
    ctx.line_to(cx + s / 2 + d, cy + s / 2 - d); ctx.line_to(cx + s / 2, cy + s / 2); ctx.close_path()
    fill_stroke(ctx, lerpc(col, INK, 0.15), lw=4, alpha=a)
    ctx.rectangle(cx - s / 2, cy - s / 2, s, s); fill_stroke(ctx, lerpc(col, WHITE, 0.2), lw=4, alpha=a)

def card_cubes(ctx, t, lt, a):
    card_frame(ctx, "WATER 1 m³ OF AIR CAN HOLD", a, "WARM AIR HOLDS ≈ 5× MORE WATER", RED)
    _cube(ctx, 300, 425, 140, VAPOR, a)
    _cube(ctx, 760, 425, 140, ORANGE, a)
    # drops inside: 17 g -> 2 drops, 83 g -> 10 drops (to scale), appearing one by one
    k = ease(lt / 3.0)
    for i in range(2):
        drop(ctx, 275 + i * 50, 440, 13, a * clamp(k * 5 - i))
    for i in range(10):
        r, c = divmod(i, 5)
        drop(ctx, 712 + c * 24, 410 + r * 46, 10, a * clamp(k * 10 - i))
    text_c(ctx, "20 °C · 68 °F", 300, 290, 26, COLDC, True, 1, a)
    text_c(ctx, "50 °C · 122 °F", 760, 290, 26, RED, True, 1, a)
    text_c(ctx, "≈ 17 g", 300, 540, 34, INK, True, 1, a)
    text_c(ctx, "≈ 83 g", 760, 540, 34, INK, True, 1, a)
    straight_arrow(ctx, 440, 410, 610, 410, INK2, a, lw=5, head=12)

def card_rain(ctx, t, lt, a):
    card_frame(ctx, "ON THE COLD COIL", a, "COLD METAL = THE WATER RAINS OUT", COLDC)
    # air goes left -> right through cold fins
    for i in range(8):
        x = 470 + i * 34
        rrect(ctx, x, 270, 12, 230, 4); fill_stroke(ctx, hexc('#cfe9e6'), stroke=COLDC, lw=3, alpha=a)
    rnd = random.Random(4)
    for i in range(34):
        u = (rnd.random() + lt * 0.22) % 1
        x = 130 + u * 820; y = 285 + rnd.random() * 200
        if 455 <= x <= 755: continue
        col = ORANGE if x < 470 else VAPOR
        ctx.arc(x, y, 13, 0, 2 * math.pi); setc(ctx, col, a); ctx.fill_preserve()
        setc(ctx, INK, 0.4 * a); ctx.set_line_width(2); ctx.stroke()
        if x < 470:
            for j in range(2):
                ctx.arc(x + 12 * math.cos(i + j * 2.6), y + 12 * math.sin(i + j * 2.6), 6, 0, 2 * math.pi)
                setc(ctx, WATER, a); ctx.fill()
    straight_arrow(ctx, 160, 520, 420, 520, ORANGE, a, lw=5, head=12)
    straight_arrow(ctx, 790, 520, 960, 520, COLDC, a, lw=5, head=12)
    # beads grow on the fins, then fall (down)
    for i in range(8):
        x = 476 + i * 34
        ph = (lt * 0.8 + i * 0.37) % 1
        if ph < 0.6:
            drop(ctx, x, 320 + (i % 3) * 55, 4 + 8 * ph / 0.6, a)
        else:
            drop(ctx, x, 320 + (i % 3) * 55 + (ph - 0.6) / 0.4 * 160, 11, a)
    text_c(ctx, "SOGGY AIR", 290, 495, 24, ORANGE, True, 1, a)
    text_c(ctx, "DRY AIR", 875, 495, 24, COLDC, True, 1, a)

CARDS = {'cubes': card_cubes, 'rain': card_rain}
