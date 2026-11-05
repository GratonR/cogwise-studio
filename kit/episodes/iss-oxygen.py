"""Cogwise episode: Where does the ISS get its air?  (electrolysis, zeolite CO2 scrubber, Sabatier reactor)

Stage: one ISS module in cut-away, floating over Earth.  Loop, clockwise:
  1 WATER tank (bottom-left) -> 2 ELECTROLYZER (left) -> O2 into the cabin -> crew breathes ->
  CO2 -> 3 CO2 SCRUBBER (zeolite bed, right) -> CO2 down -> 4 SABATIER reactor (bottom-right)
  (+ H2 from the electrolyzer) -> water back to the tank, methane vented to space.
Screen frame: y grows DOWNWARD. Gas/bubbles rise = y decreases.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="iss-oxygen",
    title="How the ISS makes the air astronauts breathe 🚀",
    description=("No windows to open, 400 km up. The station splits water into oxygen, scrubs CO2 with zeolite "
                 "and turns it back into water.\n\n#Shorts #howthingswork #space #ISS #science #cogwise"),
    hashtags=["Shorts", "howthingswork", "space", "ISS", "science", "engineering", "cogwise"],
    sources=[
        "https://www.nasa.gov/wp-content/uploads/2020/10/g-281237_eclss_0.pdf",
        "https://ntrs.nasa.gov/api/citations/20190033322/downloads/20190033322.pdf",
        "https://nasa.gov/wp-content/uploads/2015/05/design_iss_environment_control_and_life_support_systems.pdf",
        "https://www.britannica.com/science/zeolite",
    ],
)

BEATS = [
    dict(dur=5.2, title="HOW DOES THE ISS GET AIR?", caption="No windows to open, 400 kilometers up. So where does the air come from?"),
    dict(dur=5.0, title="IT MAKES ITS OWN", caption="The station makes its own oxygen, out of plain water."),
    dict(dur=5.5, title=None, caption="Run electricity through water, and it splits into oxygen and hydrogen.", card='elec'),
    dict(dur=5.5, title="1 · THE WATER", caption="The water is recycled from humidity, sweat, even the crew's urine."),
    dict(dur=5.5, title="2 · THE ELECTROLYZER", caption="Solar power runs the electrolyzer. Oxygen bubbles out into the cabin."),
    dict(dur=5.0, title="3 · THE CO2 SCRUBBER", caption="Every breath adds carbon dioxide. Zeolite beads trap it."),
    dict(dur=6.0, title=None, caption="Zeolite is a mineral crystal, full of molecule-sized tunnels.", card='zeo'),
    dict(dur=5.5, title="CO2 STICKS, AIR PASSES", caption="Carbon dioxide sticks to the walls. Oxygen and nitrogen slip through."),
    dict(dur=5.5, title=None, caption="Heat the beads, and they release the carbon dioxide.", card='heat'),
    dict(dur=5.5, title="4 · THE SABATIER REACTOR", caption="In a hot reactor, it meets the leftover hydrogen."),
    dict(dur=5.0, title=None, caption="Out come water and methane. The water goes back to the start.", card='eq'),
    dict(dur=5.0, title="WHERE'S THE METHANE?", caption="The methane is useless on board, so it's vented into space."),
    dict(dur=5.0, title="NOT QUITE PERFECT", caption="That methane carries hydrogen away, so only half the oxygen comes back."),
    dict(dur=5.5, title=None, caption="So cargo ships still bring water and oxygen, plus backup oxygen candles.", card='backup'),
    dict(dur=5.0, title="ISS AIR = RECYCLED WATER", caption="The station's air is mostly yesterday's water, split by sunlight."),
    dict(dur=5.5, title="NOW YOU KNOW", caption="Now you know where every breath up there comes from. Pretty clever, right?"),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]                     # start of beat i (0-based)
def bw(t, i, j=None, f=0.35):              # window = beat i .. start of beat j
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
END = ST[-1] + 4.0

SFX = [(B(1) + 0.3, 'whoosh'), (B(3) + 0.3, 'pop'), (B(4) + 0.2, 'click'), (B(4) + 0.4, 'pop'),
       (B(5) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(9) + 0.6, 'sizzle'), (B(11) + 0.4, 'whoosh'),
       (B(12) + 0.4, 'pop'), (B(14) + 0.2, 'pop'), (B(14) + 0.4, 'pop'), (B(14) + 0.6, 'pop'), (B(14) + 0.8, 'pop')]
HUM = [(B(4) + 0.2, END)]

# ---------------------------------------------------------------- palette extras
SPACE  = hexc('#1f2b45'); SPACE2 = hexc('#2c3b5c')
EARTH  = hexc('#3f7fa0'); EARTH2 = hexc('#7fb7a4')
HULLC  = hexc('#e6e1d6'); CABIN = hexc('#f6eedd')
O2C    = TEAL;  H2C = ORANGE; CO2C = hexc('#8a8592'); CH4C = hexc('#9a7bb3'); WATERC = hexc('#3d9fc4')
ELEC   = MUSTARD
PANEL  = hexc('#2f6f8f')

# hull geometry
HX0, HX1, HY0, HY1 = 170, 850, 560, 1320
E_BOX = (210, 830, 160, 180)     # electrolyzer x, y, w, h  (left = O2 cell / anode, right = H2 cell / cathode)
T_BOX = (210, 1120, 160, 160)    # water tank
Z_BOX = (640, 830, 160, 180)     # zeolite CO2 scrubber
S_BOX = (640, 1120, 160, 160)    # Sabatier reactor
CREW = (500, 700)
PORT = (680, 640)

# ---------------------------------------------------------------- flow paths (screen coords)
P_WATER_IN = [(290, 1120), (290, 1010)]                                   # tank -> electrolyzer (UP)
P_CABLE    = [(230, 440), (230, 560), (230, 830)]                         # solar panel -> electrolyzer
P_O2       = [(250, 830), (250, 740), (300, 715), (450, 715)]            # anode cell top -> cabin
P_BREATH   = [(535, 705), (610, 700), (720, 745), (720, 830)]            # crew -> scrubber inlet (top)
P_CLEAN    = [(640, 930), (590, 930), (560, 880)]                         # scrubber -> back to cabin
P_CO2_DOWN = [(720, 1010), (720, 1120)]                                   # scrubber -> Sabatier
P_H2       = [(370, 975), (505, 975), (505, 1170), (640, 1170)]          # cathode cell -> Sabatier
P_WATER_RET= [(640, 1245), (370, 1245)]                                   # Sabatier -> tank
P_CH4      = [(800, 1200), (850, 1200), (905, 1180)]                      # Sabatier -> out of the hull

def _plen(path):
    return sum(math.dist(path[i], path[i+1]) for i in range(len(path) - 1))

def _pt(path, s):
    for i in range(len(path) - 1):
        d = math.dist(path[i], path[i+1])
        if s <= d or i == len(path) - 2:
            u = clamp(s / d if d else 0)
            return (lerp(path[i][0], path[i+1][0], u), lerp(path[i][1], path[i+1][1], u))
        s -= d
    return path[-1]

def pipe(ctx, path, a, lw=12, inner=None):
    if a <= 0: return
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for k, (w, c) in enumerate(((lw, INK), (lw - 6, inner or FILL2))):
        ctx.move_to(*path[0])
        for p in path[1:]: ctx.line_to(*p)
        setc(ctx, c, a); ctx.set_line_width(w); ctx.stroke()

def flow(ctx, path, t, col, a, n=8, speed=90, r=6):
    if a <= 0: return
    L = _plen(path)
    for i in range(n):
        s = ((i / n) * L + t * speed) % L
        edge = clamp(min(s, L - s) / 25)
        x, y = _pt(path, s)
        ctx.arc(x, y, r, 0, 2*math.pi); setc(ctx, col, a * edge); ctx.fill()

# ---------------------------------------------------------------- static set: space plate + Earth
def draw_set(ctx):
    rrect(ctx, 40, 236, 1000, 1236, 28)
    ctx.save(); ctx.clip_preserve()
    g = cairo.LinearGradient(0, 236, 0, 1470)
    g.add_color_stop_rgb(0, *SPACE[:3]); g.add_color_stop_rgb(1, *SPACE2[:3])
    ctx.set_source(g); ctx.fill()
    rnd = random.Random(11)
    for i in range(90):
        x, y = 50 + rnd.random()*980, 246 + rnd.random()*1100
        r = rnd.choice((1.6, 2.2, 3.0))
        ctx.arc(x, y, r, 0, 2*math.pi); setc(ctx, CREAM, 0.55 + 0.4*rnd.random()); ctx.fill()
    # Earth limb at the bottom
    ctx.arc(540, 2650, 1290, 0, 2*math.pi); setc(ctx, EARTH); ctx.fill()
    for cx, cy, rx, ry in [(250, 1420, 120, 26), (700, 1395, 160, 22), (980, 1445, 90, 20)]:
        ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry); ctx.arc(0, 0, 1, 0, 2*math.pi); ctx.restore()
        setc(ctx, EARTH2); ctx.fill()
    ctx.arc(540, 2650, 1290, 0, 2*math.pi); setc(ctx, hexc('#8fcfe8', 0.8)); ctx.set_line_width(8); ctx.stroke()
    ctx.restore()
    rrect(ctx, 40, 236, 1000, 1236, 28); setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()

# ---------------------------------------------------------------- parts
def solar_panel(ctx, t, glow):
    # truss from the hull top up to the array
    ctx.move_to(230, 560); ctx.line_to(230, 440); setc(ctx, INK); ctx.set_line_width(10); ctx.stroke()
    ctx.move_to(230, 560); ctx.line_to(230, 440); setc(ctx, FILL3); ctx.set_line_width(4); ctx.stroke()
    rrect(ctx, 80, 330, 440, 110, 6); fill_stroke(ctx, PANEL, lw=5)
    for i in range(1, 8):
        x = 80 + i * 55
        ctx.move_to(x, 330); ctx.line_to(x, 440)
    ctx.move_to(80, 385); ctx.line_to(520, 385)
    setc(ctx, hexc('#8fcfe8', 0.8)); ctx.set_line_width(2.5); ctx.stroke()
    if glow > 0:
        rrect(ctx, 80, 330, 440, 110, 6); setc(ctx, MUSTARD, 0.25 * glow * (0.7 + 0.3*math.sin(t*4))); ctx.fill()
        for i in range(3):   # sunlight rays hitting the panel (coming from above)
            x = 150 + i * 140
            straight_arrow(ctx, x - 40, 260, x, 318, MUSTARD, glow, lw=5, head=11)

def hull(ctx, cut):
    # outer shell
    rrect(ctx, HX0, HY0, HX1 - HX0, HY1 - HY0, 46); fill_stroke(ctx, MUSTARD, lw=8)       # insulation layer
    rrect(ctx, HX0 + 18, HY0 + 18, HX1 - HX0 - 36, HY1 - HY0 - 36, 32); fill_stroke(ctx, CABIN, lw=5)
    # docking ring on the left end
    rrect(ctx, HX0 - 34, 880, 34, 200, 8); fill_stroke(ctx, HULLC, lw=5)
    # sealed porthole on the back wall
    px, py = PORT
    ctx.arc(px, py, 40, 0, 2*math.pi); fill_stroke(ctx, HULLC, lw=5)
    ctx.arc(px, py, 28, 0, 2*math.pi); fill_stroke(ctx, SPACE, lw=4)
    ctx.arc(px - 8, py - 6, 3, 0, 2*math.pi); setc(ctx, CREAM); ctx.fill()
    for k in range(6):
        an = k * math.pi / 3
        ctx.arc(px + 34*math.cos(an), py + 34*math.sin(an), 3, 0, 2*math.pi); setc(ctx, INK); ctx.fill()

def hull_closed(ctx, a):
    """Exterior panel that fades away for the cut-away (beat 2)."""
    if a <= 0: return
    rrect(ctx, HX0, HY0, HX1 - HX0, HY1 - HY0, 46); setc(ctx, HULLC, a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(8); ctx.stroke()
    for y in range(HY0 + 110, HY1 - 40, 120):
        ctx.move_to(HX0 + 10, y); ctx.line_to(HX1 - 10, y)
    setc(ctx, INK2, 0.6*a); ctx.set_line_width(3); ctx.stroke()
    for y in range(HY0 + 110, HY1 - 40, 120):
        for x in range(HX0 + 40, HX1 - 20, 60):
            ctx.arc(x, y - 12, 3, 0, 2*math.pi); setc(ctx, INK2, 0.6*a); ctx.fill()
    px, py = 510, 820
    ctx.arc(px, py, 70, 0, 2*math.pi); setc(ctx, HULLC, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(7); ctx.stroke()
    ctx.arc(px, py, 50, 0, 2*math.pi); setc(ctx, SPACE, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    ctx.arc(px - 14, py - 14, 9, 0, 2*math.pi); setc(ctx, CREAM, 0.5*a); ctx.fill()
    for k in range(8):
        an = k * math.pi / 4
        ctx.arc(px + 60*math.cos(an), py + 60*math.sin(an), 4, 0, 2*math.pi); setc(ctx, INK, a); ctx.fill()

def crew(ctx, t, a=1.0):
    """Simple faceless head-and-shoulders silhouette (not a character)."""
    cx, cy = CREW; cy += math.sin(t * 1.6) * 6
    ctx.move_to(cx - 62, cy + 120); ctx.curve_to(cx - 60, cy + 55, cx - 30, cy + 42, cx, cy + 42)
    ctx.curve_to(cx + 30, cy + 42, cx + 60, cy + 55, cx + 62, cy + 120); ctx.close_path()
    fill_stroke(ctx, FILL3, lw=5, alpha=a)
    ctx.arc(cx, cy, 32, 0, 2*math.pi); fill_stroke(ctx, FILL2, lw=5, alpha=a)

def electrolyzer(ctx, t, on):
    x, y, w, h = E_BOX
    rrect(ctx, x, y, w, h, 12); fill_stroke(ctx, PAPER, lw=5)
    rrect(ctx, x + 12, y + 40, w - 24, h - 52, 6); setc(ctx, hexc('#cfe8ef')); ctx.fill()
    # membrane between anode (left, O2) and cathode (right, H2)
    ctx.move_to(x + w/2, y + 40); ctx.line_to(x + w/2, y + h - 12)
    ctx.set_dash([8, 6]); setc(ctx, INK2); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    # electrodes
    for ex, col in ((x + 34, RED), (x + w - 34, INK2)):
        rrect(ctx, ex - 6, y + 52, 12, h - 76, 3); setc(ctx, col); ctx.fill()
    text_c(ctx, "+", x + 34, y + 30, 26, RED)
    ctx.rectangle(x + w - 42, y + 21, 16, 4); setc(ctx, INK2); ctx.fill()
    # bubbles rise (y decreases): O2 on the + side, twice as many H2 on the − side
    if on > 0:
        for side, n, col in ((0, 3, O2C), (1, 6, H2C)):
            bx = x + (52 if side == 0 else w - 52)
            for i in range(n):
                ph = (t * 0.9 + i / n) % 1
                yy = y + h - 20 - ph * (h - 70)
                ctx.arc(bx + math.sin(i*2.1 + t*3) * 8, yy, 6, 0, 2*math.pi)
                setc(ctx, col, on * (1 - ph*0.4)); ctx.fill_preserve(); setc(ctx, INK, on*0.6); ctx.set_line_width(1.5); ctx.stroke()
    rrect(ctx, x, y, w, h, 12); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()

def tank(ctx, t, level):
    x, y, w, h = T_BOX
    rrect(ctx, x, y, w, h, 14); fill_stroke(ctx, PAPER, lw=5)
    lh = (h - 24) * level
    ctx.save(); rrect(ctx, x + 10, y + 12, w - 20, h - 24, 8); ctx.clip()
    ctx.move_to(x, y + h - 12 - lh)
    for i in range(0, w + 1, 10):
        ctx.line_to(x + i, y + h - 12 - lh + math.sin(i/18 + t*3) * 3)
    ctx.line_to(x + w, y + h); ctx.line_to(x, y + h); ctx.close_path(); setc(ctx, WATERC, 0.85); ctx.fill()
    ctx.restore()
    text_c(ctx, "H2O", x + w/2, y + 44, 28, INK)

def scrubber(ctx, t, loaded, hot):
    x, y, w, h = Z_BOX
    rrect(ctx, x, y, w, h, 12); fill_stroke(ctx, lerpc(PAPER, hexc('#f6d0c0'), hot), lw=5)
    rnd = random.Random(5)
    k = 0
    for row in range(6):
        for col in range(6):
            bx = x + 24 + col * 22.5 + (row % 2) * 10; by = y + 36 + row * 24
            if bx > x + w - 18: continue
            ctx.arc(bx, by, 10, 0, 2*math.pi); fill_stroke(ctx, hexc('#f2dca0'), lw=2.5)
            if rnd.random() < loaded:     # trapped CO2 on this bead
                ctx.arc(bx + 3, by - 3, 4.5, 0, 2*math.pi); setc(ctx, CO2C); ctx.fill()
            k += 1
    rrect(ctx, x, y, w, h, 12); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()

def sabatier(ctx, t, hot):
    x, y, w, h = S_BOX
    rrect(ctx, x, y, w, h, 18); fill_stroke(ctx, lerpc(PAPER, hexc('#f3b7a4'), hot), lw=5)
    # catalyst bed stripes
    for i in range(4):
        rrect(ctx, x + 22, y + 46 + i * 26, w - 44, 12, 6); setc(ctx, lerpc(FILL3, RED, hot*0.6)); ctx.fill()
    if hot > 0:
        for i in range(3):   # heat rising from the hot reactor (upward = y decreases)
            wavy_arrow(ctx, x + 40 + i * 40, y + h - 8, x + 40 + i * 40, y + 20, t + i*0.3, RED, hot*0.55, amp=6, wl=30, lw=4, head=9)

# ---------------------------------------------------------------- state machine
def state(t):
    st = {}
    st['cut'] = ease((t - B(1) - 0.1) / 1.0)
    st['q'] = win(t, 0.3, B(1) + 0.3)
    st['on'] = ease((t - B(4)) / 0.8)                       # loop running from the electrolyzer beat
    st['sun'] = max(bw(t, 4) , 0.0)
    st['level'] = 0.35 + 0.4 * ease((t - B(3) - 0.5) / 3.5)
    st['drips'] = bw(t, 3)
    st['breath'] = ease((t - B(5) - 0.2) / 0.8)
    st['loaded'] = 0.15 + 0.55 * ease((t - B(5)) / 9.0)
    if t > B(8): st['loaded'] = lerp(0.7, 0.25, ease((t - B(8)) / 4.0))
    st['clean'] = ease((t - B(7) - 0.2) / 0.8)
    st['zoom_z'] = bw(t, 7)
    st['co2down'] = ease((t - B(9)) / 0.8)
    st['h2'] = ease((t - B(9) - 0.3) / 0.8)
    st['hot'] = ease((t - B(9)) / 1.0)
    st['ret'] = ease((t - B(10) - 0.3) / 0.8)
    st['ch4'] = ease((t - B(11) - 0.2) / 0.8)
    st['h_own'] = bw(t, 1)
    st['h_t'] = bw(t, 3); st['h_e'] = bw(t, 4); st['h_z'] = bw(t, 5) + bw(t, 7); st['h_s'] = bw(t, 9)
    st['h_vent'] = bw(t, 11)
    recap = bw(t, 14)
    st['l_t'] = bw(t, 3) + recap; st['l_e'] = bw(t, 4) + recap
    st['l_z'] = bw(t, 5) + recap; st['l_s'] = bw(t, 9) + recap
    st['half'] = bw(t, 12)
    return st

def draw(ctx, t, E):
    st = state(t)
    solar_panel(ctx, t, st['sun'] + 0.5 * bw(t, 14))
    hull(ctx, st['cut'])
    # pipes (drawn under the parts)
    pipe(ctx, P_CABLE, 1.0, lw=9, inner=ELEC)
    pipe(ctx, P_WATER_IN, 1.0, inner=hexc('#bfe3ef'))
    pipe(ctx, P_CO2_DOWN, 1.0, inner=hexc('#d9d6de'))
    pipe(ctx, P_H2, 1.0, inner=hexc('#f9d6b0'))
    pipe(ctx, P_WATER_RET, 1.0, inner=hexc('#bfe3ef'))
    pipe(ctx, P_CH4, 1.0, inner=hexc('#ddd0e8'))
    tank(ctx, t, st['level'])
    electrolyzer(ctx, t, st['on'])
    scrubber(ctx, t, st['loaded'], 0.0)
    sabatier(ctx, t, st['hot'])
    crew(ctx, t)
    # flows
    flow(ctx, P_CABLE, t, MUSTARD, st['on'], n=6, speed=160, r=5)
    flow(ctx, P_WATER_IN, t, WATERC, st['on'], n=3, speed=40)
    flow(ctx, P_O2, t, O2C, st['on'], n=9, speed=70, r=7)
    flow(ctx, P_BREATH, t, CO2C, st['breath'], n=8, speed=70, r=7)
    flow(ctx, P_CLEAN, t, O2C, st['clean'], n=5, speed=60, r=6)
    flow(ctx, P_CO2_DOWN, t, CO2C, st['co2down'], n=3, speed=40)
    flow(ctx, P_H2, t, H2C, st['h2'], n=9, speed=80)
    flow(ctx, P_WATER_RET, t, WATERC, st['ret'], n=7, speed=70)
    flow(ctx, P_CH4, t, CH4C, st['ch4'], n=4, speed=60)
    # methane puffs drifting away into space
    if st['ch4'] > 0:
        for i in range(4):
            ph = (t * 0.35 + i / 4) % 1
            ctx.arc(905 + ph * 110, 1180 - ph * 70, 10 + ph * 16, 0, 2*math.pi)
            setc(ctx, CH4C, st['ch4'] * 0.55 * (1 - ph)); ctx.fill()
    # water sources (beat 4): drops travel down into the tank
    if st['drips'] > 0:
        a = st['drips']
        for k, (lab, ly) in enumerate((("HUMIDITY", 900), ("SWEAT", 975), ("URINE", 1050))):
            tag(ctx, lab, 560, ly, WATERC, a, 22)
            path = [(470, ly), (400, ly), (370, 1150)]
            flow(ctx, path, t + k, WATERC, a, n=3, speed=70, r=6)
    # zoom on the zeolite bed (beat 8): CO2 stays in, O2 + N2 come out clean
    if st['zoom_z'] > 0:
        a = st['zoom_z']
        tag(ctx, "CO2 STAYS IN", 720, 790, CO2C, a, 22)
        tag(ctx, "O2 + N2 PASS", 560, 1000, O2C, a, 22)
    # question mark (hook)
    if st['q'] > 0:
        text_c(ctx, "?", 540, 520, 150, MUSTARD, True, 0, st['q'])
    # closed exterior (fades away)
    hull_closed(ctx, 1 - st['cut'])
    if st['q'] > 0:
        tag(ctx, "SEALED", 510, 930, INK, st['q'] * (1 - st['cut']), 26)
    # highlights
    highlight(ctx, 290, 1055, 120, 260, O2C, st['h_own'], t)
    if st['h_own'] > 0: tag(ctx, "H2O IN · O2 OUT", 560, 1060, O2C, st['h_own'], 26)
    highlight(ctx, 290, 1200, 110, 110, WATERC, st['h_t'], t)
    highlight(ctx, 290, 920, 115, 125, O2C, st['h_e'], t)
    highlight(ctx, 720, 920, 115, 125, CO2C, st['h_z'], t)
    highlight(ctx, 720, 1200, 110, 110, RED, st['h_s'], t)
    highlight(ctx, 880, 1190, 70, 50, CH4C, st['h_vent'], t)
    if st['h_vent'] > 0 or st['half'] > 0:
        tag(ctx, "CH4", 960, 1080, CH4C, max(st['h_vent'], st['half']), 26)
    if st['half'] > 0:
        tag(ctx, "HYDROGEN LOST", 860, 1400, CH4C, st['half'], 24)
        tag(ctx, "ONLY ABOUT HALF COMES BACK", 540, 500, MUSTARD, st['half'], 24)
    # numbered labels
    tag(ctx, "1 · WATER", 290, 1380, WATERC, clamp(st['l_t']))
    tag(ctx, "2 · ELECTROLYZER", 300, 1065, O2C, clamp(st['l_e']))
    tag(ctx, "3 · CO2 SCRUBBER", 710, 1065, INK2, clamp(st['l_z']))
    tag(ctx, "4 · SABATIER", 720, 1380, RED, clamp(st['l_s']))

# ---------------------------------------------------------------- inset cards
def _molecule(ctx, atoms, a):
    """atoms = [(x, y, r, color)] drawn with ink outline."""
    for x, y, r, c in atoms:
        ctx.arc(x, y, r, 0, 2*math.pi); fill_stroke(ctx, c, lw=3, alpha=a)

def co2_mol(ctx, x, y, a, s=1.0):      # O=C=O : C ink, O red
    _molecule(ctx, [(x - 20*s, y, 11*s, RED), (x + 20*s, y, 11*s, RED), (x, y, 12*s, INK2)], a)
def o2_mol(ctx, x, y, a, s=1.0):
    _molecule(ctx, [(x - 9*s, y, 11*s, RED), (x + 9*s, y, 11*s, RED)], a)
def n2_mol(ctx, x, y, a, s=1.0):
    _molecule(ctx, [(x - 9*s, y, 11*s, hexc('#6f8fb8')), (x + 9*s, y, 11*s, hexc('#6f8fb8'))], a)
def h2_mol(ctx, x, y, a, s=1.0):
    _molecule(ctx, [(x - 6*s, y, 8*s, WHITE), (x + 6*s, y, 8*s, WHITE)], a)
def h2o_mol(ctx, x, y, a, s=1.0):
    _molecule(ctx, [(x - 14*s, y + 10*s, 8*s, WHITE), (x + 14*s, y + 10*s, 8*s, WHITE), (x, y, 12*s, RED)], a)
def ch4_mol(ctx, x, y, a, s=1.0):
    _molecule(ctx, [(x - 16*s, y - 12*s, 8*s, WHITE), (x + 16*s, y - 12*s, 8*s, WHITE),
                    (x - 16*s, y + 12*s, 8*s, WHITE), (x + 16*s, y + 12*s, 8*s, WHITE), (x, y, 12*s, INK2)], a)

def card_elec(ctx, t, lt, a):
    card_frame(ctx, "THE TRICK: ELECTROLYSIS", a, "WATER + ELECTRICITY = OXYGEN + HYDROGEN", TEAL)
    # battery on top: + on the left, − on the right
    rrect(ctx, 490, 252, 100, 34, 6); fill_stroke(ctx, MUSTARD, lw=4, alpha=a)
    text_c(ctx, "+", 507, 278, 26, RED, True, 0, a); ctx.rectangle(565, 267, 16, 4); setc(ctx, INK, a); ctx.fill()
    for x0, x1 in ((490, 440), (590, 640)):
        ctx.move_to(x0, 269); ctx.line_to(x1, 269); ctx.line_to(x1, 330)
        setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    # water bath
    rrect(ctx, 340, 310, 400, 220, 14); fill_stroke(ctx, PAPER, lw=5, alpha=a)
    rrect(ctx, 350, 340, 380, 180, 8); setc(ctx, hexc('#bfe3ef'), a); ctx.fill()
    for ex, col in ((440, RED), (640, INK2)):
        rrect(ctx, ex - 8, 320, 16, 170, 4); setc(ctx, col, a); ctx.fill()
    # bubbles rise: O2 at + (left), twice as many H2 at − (right)
    for ex, n, col in ((440, 4, O2C), (640, 8, H2C)):
        for i in range(n):
            ph = (lt * 0.8 + i / n) % 1
            yy = 495 - ph * 150
            ctx.arc(ex + 22 + math.sin(i*1.7 + lt*4)*6, yy, 8, 0, 2*math.pi)
            setc(ctx, col, a); ctx.fill_preserve(); setc(ctx, INK, a*0.7); ctx.set_line_width(2); ctx.stroke()
    tag(ctx, "OXYGEN", 225, 420, O2C, a, 26)
    tag(ctx, "HYDROGEN", 852, 420, H2C, a, 26)
    straight_arrow(ctx, 300, 420, 420, 420, O2C, a, lw=4, head=10)
    straight_arrow(ctx, 760, 420, 670, 420, H2C, a, lw=4, head=10)

def card_zeo(ctx, t, lt, a):
    card_frame(ctx, "WHAT IS ZEOLITE?", a, "A CRYSTAL FULL OF MOLECULE-SIZED TUNNELS", INK2)
    # left: a bead and the crystal cage network inside it
    ctx.arc(190, 440, 48, 0, 2*math.pi); fill_stroke(ctx, hexc('#f2dca0'), lw=4, alpha=a)
    for (x0, y0, x1, y1) in ((225, 405, 290, 270), (225, 475, 290, 530)):
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); setc(ctx, INK2, a*0.7); ctx.set_line_width(2.5); ctx.stroke()
    ctx.save(); rrect(ctx, 290, 260, 230, 280, 14); ctx.clip()
    setc(ctx, hexc('#f7e9c4'), a); ctx.paint_with_alpha(a)
    R = 30
    for row in range(-1, 6):
        for col in range(-1, 6):
            cx = 290 + col * R * 1.73 + (row % 2) * R * 0.866; cy = 260 + row * R * 1.5
            ctx.new_sub_path()
            for k in range(7):
                an = math.pi/6 + k * math.pi/3
                (ctx.line_to)(cx + R*math.cos(an), cy + R*math.sin(an))
            setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
            for k in range(6):   # Si / Al / O atoms at the corners
                an = math.pi/6 + k * math.pi/3
                ctx.arc(cx + R*math.cos(an), cy + R*math.sin(an), 4, 0, 2*math.pi)
                setc(ctx, (RED if k % 2 else hexc('#6f8fb8')), a); ctx.fill()
            ctx.arc(cx, cy, 11, 0, 2*math.pi); setc(ctx, SPACE, a*0.85); ctx.fill()   # the tunnel
    ctx.restore()
    rrect(ctx, 290, 260, 230, 280, 14); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    # right: one tunnel seen from the side, air flowing left -> right
    y0, y1 = 330, 470
    for yy in (y0, y1):
        for i in range(12):
            ctx.arc(570 + i * 34, yy, 13, 0, 2*math.pi); fill_stroke(ctx, hexc('#f2dca0'), lw=3, alpha=a)
    straight_arrow(ctx, 560, 290, 700, 290, INK2, a, lw=4, head=10)
    text_c(ctx, "AIR IN", 770, 300, 22, INK2, True, 1, a)
    # O2 and N2 slip through; CO2 drifts to a wall and sticks there
    for i, kind in enumerate(("o2", "n2", "o2", "n2")):
        ph = (lt * 0.28 + i / 4) % 1
        x = 560 + ph * 400; y = 400 + math.sin(i*1.3 + lt*3) * 18
        (o2_mol if kind == "o2" else n2_mol)(ctx, x, y, a * clamp(min(ph, 1-ph) * 8), 0.85)
    for i, (sx, wall) in enumerate(((650, y0), (780, y1), (880, y0))):
        k = ease((lt - 0.4 - i * 0.9) / 1.2)
        x = lerp(560, sx, k); y = lerp(400, wall + (24 if wall == y0 else -24), k)
        if lt > 0.4 + i * 0.9: co2_mol(ctx, x, y, a, 0.8)
    text_c(ctx, "CO2 STICKS  ·  O2 + N2 PASS", 765, 522, 20, INK2, True, 1, a)

def card_heat(ctx, t, lt, a):
    card_frame(ctx, "HEAT = LET GO", a, "HOT BEADS RELEASE THEIR CO2", RED)
    heat = ease(lt / 1.5)
    rrect(ctx, 300, 330, 380, 150, 12); fill_stroke(ctx, lerpc(PAPER, hexc('#f6d0c0'), heat), lw=5, alpha=a)
    rnd = random.Random(9)
    for row in range(5):
        for col in range(13):
            bx = 322 + col * 27 + (row % 2) * 12; by = 352 + row * 27
            if bx > 662: continue
            ctx.arc(bx, by, 11, 0, 2*math.pi); fill_stroke(ctx, hexc('#f2dca0'), lw=2.5, alpha=a)
            # CO2 still stuck on the bead until its release time
            rel = 0.6 + rnd.random() * 3.0
            if lt < rel:
                ctx.arc(bx + 3, by - 3, 4.5, 0, 2*math.pi); setc(ctx, CO2C, a); ctx.fill()
    # heater under the bed, heat goes UP into it
    ctx.move_to(310, 510)
    for i in range(18): ctx.line_to(320 + i * 20, 498 if i % 2 else 520)
    setc(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
    for i in range(4):
        wavy_arrow(ctx, 360 + i * 90, 495, 360 + i * 90, 455, t + i*0.3, RED, a*heat, amp=5, wl=20, lw=4, head=8)
    # released CO2 leaves through the outlet on the right, towards the reactor
    ctx.move_to(680, 360); ctx.line_to(900, 360); setc(ctx, INK, a); ctx.set_line_width(14); ctx.stroke()
    ctx.move_to(680, 360); ctx.line_to(900, 360); setc(ctx, hexc('#d9d6de'), a); ctx.set_line_width(8); ctx.stroke()
    for i in range(5):
        ph = (lt * 0.5 + i / 5) % 1
        if lt > 0.8: co2_mol(ctx, 700 + ph * 200, 360, a * clamp(min(ph, 1 - ph) * 6), 0.6)
    text_c(ctx, "TO THE REACTOR", 790, 420, 22, INK2, True, 1, a)
    straight_arrow(ctx, 730, 450, 860, 450, INK2, a, lw=4, head=10)
    thermometer(ctx, 200, 500, 0.3 + 0.6 * heat, a, RED, 200)

def card_eq(ctx, t, lt, a):
    card_frame(ctx, "4 · THE SABATIER REACTION", a, None)
    text_c(ctx, "CO2 + 4 H2", 330, 580, 32, INK, True, 1.5, a)
    straight_arrow(ctx, 445, 569, 545, 569, INK, a, lw=5, head=11)
    text_c(ctx, "2 H2O + CH4", 685, 580, 32, INK, True, 1.5, a)
    y = 400
    co2_mol(ctx, 175, y, a, 1.3)
    text_c(ctx, "+", 245, y + 14, 40, INK, True, 0, a)
    for i, (dx, dy) in enumerate(((0, -45), (52, -45), (0, 45), (52, 45))):
        h2_mol(ctx, 295 + dx, y + dy, a, 1.3)
    k = ease((lt - 0.8) / 0.8)
    straight_arrow(ctx, 380, y, lerp(382, 530, k), y, RED, a * (k > 0), lw=6, head=14)
    if k > 0: text_c(ctx, "HOT + CATALYST", 458, y - 22, 20, RED, True, 0, a * k)
    k2 = ease((lt - 1.5) / 0.8)
    h2o_mol(ctx, 610, y - 50, a * k2, 1.3); h2o_mol(ctx, 610, y + 40, a * k2, 1.3)
    text_c(ctx, "+", 700, y + 14, 40, INK, True, 0, a * k2)
    ch4_mol(ctx, 800, y, a * k2, 1.3)
    text_c(ctx, "WATER", 610, 515, 22, WATERC, True, 1, a * k2)
    text_c(ctx, "METHANE", 800, 515, 22, CH4C, True, 1, a * k2)
    text_c(ctx, "C = BLACK  ·  O = RED  ·  H = WHITE", 540, 285, 20, INK2, True, 1, a)

def card_backup(ctx, t, lt, a):
    card_frame(ctx, "BACKUP", a, "CARGO SHIPS + OXYGEN CANDLES", MUSTARD)
    # cargo ship docking (moves right towards the port)
    k = ease(lt / 3.0)
    sx = lerp(150, 322, k)
    for dy in (-62, 62):
        rrect(ctx, sx - 40, 400 + dy - 14, 80, 28, 3); fill_stroke(ctx, PANEL, lw=3, alpha=a)
    rrect(ctx, sx - 50, 350, 110, 100, 14); fill_stroke(ctx, HULLC, lw=4, alpha=a)
    ctx.move_to(sx + 60, 360); ctx.line_to(sx + 88, 385); ctx.line_to(sx + 88, 415); ctx.line_to(sx + 60, 440); ctx.close_path()
    fill_stroke(ctx, FILL3, lw=4, alpha=a)
    text_c(ctx, "CARGO SHIP", sx + 10, 510, 20, INK2, True, 1, a)
    for lab, yy in (("H2O", 392), ("O2", 428)):
        text_c(ctx, lab, sx + 10, yy, 20, INK, True, 0, a)
    rrect(ctx, 420, 330, 60, 140, 8); fill_stroke(ctx, MUSTARD, lw=4, alpha=a)     # station port
    text_c(ctx, "ISS", 450, 510, 20, INK2, True, 1, a)
    # oxygen candle: canister, glowing core, O2 coming out of the top
    rrect(ctx, 690, 330, 110, 170, 14); fill_stroke(ctx, PAPER, lw=4, alpha=a)
    rrect(ctx, 715, 365, 60, 115, 8); setc(ctx, lerpc(MUSTARD, ORANGE, 0.5 + 0.5*math.sin(t*5)), a); ctx.fill()
    for i in range(4):
        ph = (lt * 0.7 + i / 4) % 1
        o2_mol(ctx, 745 + math.sin(i*2 + lt*3) * 20, 318 - ph * 55, a * (1 - ph), 0.7)
    text_c(ctx, "O2 CANDLE", 745, 532, 22, INK, True, 1, a)

CARDS = {'elec': card_elec, 'zeo': card_zeo, 'heat': card_heat, 'eq': card_eq, 'backup': card_backup}
