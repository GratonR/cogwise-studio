"""Cogwise episode: A coin battery makes drain cleaner inside your body.
One idea: a swallowed coin battery does not poison by leaking. Wedged in the wet food pipe, the tissue closes the
circuit between its two faces, and at the MINUS face water is electrolysed: 2 H2O + 2 e- -> H2 + 2 OH-.
The hydroxide (= lye, the active part of drain cleaner) builds up against the tissue on the minus ("narrow") side.

VIEW (screen coordinates, y grows DOWN): a LONGITUDINAL section of the food pipe, vertical, top = towards the mouth.
  - left wall x ~300-500, right wall x ~570-770, collapsed lumen in between; both walls bulge around the battery.
  - the battery is seen EDGE-ON, standing upright (lodged flat across the pipe):
      + can (the wide face, full height) on the LEFT, x 470-570, y 810-1170;
      - cap (the narrower face) protrudes on the RIGHT, x 570-598, y 845-1135, with a dark gasket ring between.
  - conventional current: out of the + face into the LEFT wall, round the top and bottom ends of the battery
    through the wet lining, into the RIGHT wall and back into the - face (arrows + -> -).
  - electrons leave the - face into the right wall: hydrogen bubbles rise (go UP, -y), hydroxide (lye) stays and the
    red burn spreads from the - face OUTWARD into the right wall (x increasing), layer by layer. The + side stays clean.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="coin-battery-lye",
    title="A coin battery makes drain cleaner inside your body 🔋 #Shorts",
    description=("This battery isn't leaking. It's making lye, from the water in your own body.\n\n"
                 "#Shorts #howthingswork #battery #science #cogwise"),
    hashtags=["Shorts", "howthingswork", "battery", "science", "chemistry", "cogwise"],
    sources=[
        "https://www.poison.org/battery/mechanism-of-injury",
        "https://litfl.com/button-battery-update-3-0/",
        "https://www.wsbtv.com/news/trending/recall-alert-229k-portfolios-other-tools-recalled/2QIYV4OMPBDODLJB2ZAWWKLMKM/",
    ],
)

BEATS = [
    dict(dur=5.0, title="NOT A LEAK", caption="This battery isn't leaking. It's making lye, the stuff in drain cleaner."),
    dict(dur=4.8, title="THE SECRET", caption="And it makes it from the water in your own body."),
    dict(dur=5.6, title="TWO FACES", caption="A coin battery has two faces: plus on one side, minus on the other."),
    dict(dur=5.0, title="1 · THE THROAT", caption="Stuck in a child's throat, both faces touch the wet lining."),
    dict(dur=5.4, title="2 · THE CIRCUIT", caption="That wet tissue conducts, so current flows from one face to the other."),
    dict(dur=5.6, title="3 · THE MINUS SIDE", caption="On the minus side, electrons split water into hydrogen gas and hydroxide."),
    dict(dur=5.6, title=None, caption="Hydroxide is lye. It piles up right against the tissue, on that narrow side.", card='lye'),
    dict(dur=5.0, title="4 · THE BURN", caption="It eats tissue the way drain cleaner eats a hair clog."),
    dict(dur=6.0, title=None, caption="In animal tests, burns begin within fifteen minutes. A hole can form in two hours.", card='clock'),
    dict(dur=5.6, title="THREE VOLTS", caption="Lithium coin cells push three volts, twice a double-A, so they work faster."),
    dict(dur=4.8, title="DEAD? NOT QUITE", caption="A dead one still has enough voltage to keep making lye."),
    dict(dur=6.2, title="CELL + WET = LYE", caption="Battery plus wet tissue equals a tiny lye factory. That's why many remotes screw the battery shut."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3):
    return ease(clamp((t - t0) / d))

# ---------------------------------------------------------------- palette
TISSUE = hexc('#f1c1ae'); TISSUE_D = hexc('#d99a85'); MUCOSA = hexc('#f6d3c4')
STEEL = hexc('#b9c0c6'); STEEL_D = hexc('#7d858c'); GASKET = hexc('#3b3842')
WATER = hexc('#8fcfc8'); LYE = hexc('#b0306a'); LYE_L = hexc('#e08ab0')
SPARK = MUSTARD

# ---------------------------------------------------------------- geometry
PY0, PY1 = 470, 1490                     # pipe drawn from y 470 to 1490
BY0, BY1 = 810, 1170                     # battery top / bottom
BYC = (BY0 + BY1) / 2                    # 990
PX0, PX1 = 470, 570                      # + can (wide face on the LEFT at x 470)
MX1 = 598                                # - cap face (RIGHT) x
MY0, MY1 = 845, 1135                     # - cap is narrower
LIN, RIN = 505, 565                      # collapsed lumen edges away from the battery
WALL = 200                               # wall thickness

def bump(y):
    """1 alongside the battery, smooth taper 70 px above/below."""
    if BY0 <= y <= BY1: return 1.0
    d = (BY0 - y) if y < BY0 else (y - BY1)
    return 0.5 + 0.5 * math.cos(math.pi * clamp(d / 70))

def left_in(y):  return LIN - (LIN - PX0) * bump(y)          # 505 -> 470
def right_in(y): return RIN + (MX1 - RIN) * bump(y)          # 565 -> 598

YS = [PY0 + i * 10 for i in range((PY1 - PY0) // 10 + 1)]

def wall_path(ctx, inner, sign, off0=0, off1=WALL):
    """Closed path of a wall band between inner+sign*off0 and inner+sign*off1."""
    ctx.new_path()
    ctx.move_to(inner(YS[0]) + sign * off0, YS[0])
    for y in YS[1:]: ctx.line_to(inner(y) + sign * off0, y)
    for y in reversed(YS): ctx.line_to(inner(y) + sign * off1, y)
    ctx.close_path()

def edge_path(ctx, inner, sign, off):
    ctx.new_path(); ctx.move_to(inner(YS[0]) + sign * off, YS[0])
    for y in YS[1:]: ctx.line_to(inner(y) + sign * off, y)

# ---------------------------------------------------------------- current path (+ face -> round the ends -> - face)
def loop_pts(top=True):
    s = -1 if top else 1
    yb = BY0 if top else BY1
    pts = []
    # down/up the left wall from the + face centre region to beyond the battery end, across, back on the right
    for k in range(9): pts.append((PX0 - 16, lerp(BYC + s * 40, yb + s * 10, k / 8)))
    for k in range(1, 16):
        a = math.pi + math.pi * k / 15          # half circle over the end of the battery
        cx, cy, r = (PX0 - 16 + MX1 + 16) / 2, yb + s * 10, (MX1 + 16 - (PX0 - 16)) / 2
        pts.append((cx + r * math.cos(a), cy + s * r * 0.55 * (-math.sin(a))))   # top: bulges UP (-y), bottom: DOWN
    for k in range(1, 9): pts.append((MX1 + 16, lerp(yb + s * 10, BYC + s * 40, k / 8)))
    return pts

class Path:
    def __init__(self, pts):
        self.p = pts; self.L = [0.0]
        for a, b in zip(pts, pts[1:]): self.L.append(self.L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    def at(self, u):
        d = clamp(u) * self.L[-1]
        for i in range(1, len(self.L)):
            if self.L[i] >= d:
                k = (d - self.L[i - 1]) / max(1e-6, self.L[i] - self.L[i - 1])
                a, b = self.p[i - 1], self.p[i]
                return (lerp(a[0], b[0], k), lerp(a[1], b[1], k))
        return self.p[-1]

PTOP, PBOT = Path(loop_pts(True)), Path(loop_pts(False))

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['zoom'] = 1 - ease(clamp((t - B(1) - 0.1) / 1.4))        # hook: close-up on the minus face
    s['prev'] = win(t, 0.2, B(2) + 0.2, 0.4)                     # preview of bubbles + lye in the hook
    s['wet'] = win(t, B(1) + 0.4, B(4) + 0.3, 0.4)               # wet lining highlighted
    s['current'] = clamp((t - B(4) - 0.2) / 0.6) if t < B(11) + 3 else 1.0
    s['react'] = sstep(t, B(5) + 0.4, 0.6)                       # electrolysis on the minus side
    # burn depth (px into the right wall): preview 34 in the hook, then grows from beat 6 on
    prev = 34 * s['prev']
    grow = 30 * sstep(t, B(5) + 1.2, 3.0) + 60 * sstep(t, B(7) + 0.2, 4.2) + 60 * sstep(t, B(8) + 0.3, 5.0)
    s['burn'] = max(prev, grow)
    return s

def bubbles(ctx, t, a):
    if a <= 0: return
    rnd = random.Random(3)
    for i in range(26):
        y0 = rnd.uniform(MY0 + 10, MY1 - 10); ph = rnd.random(); sp = rnd.uniform(0.35, 0.6)
        x0 = MX1 + rnd.uniform(4, 22); r = rnd.uniform(4, 9)
        u = (ph + t * sp) % 1
        y = y0 - 150 * u
        if y < BY0 - 60: continue
        x = x0 + 6 * math.sin(u * 9 + i)
        aa = a * (1 - u)
        ctx.arc(x, y, r, 0, 6.28); setc(ctx, WHITE, 0.85 * aa); ctx.fill_preserve()
        setc(ctx, INK, aa); ctx.set_line_width(2); ctx.stroke()

def burn(ctx, t, depth):
    """Lye burn: red stain in the RIGHT wall, from the minus face outward (x increasing)."""
    if depth <= 1: return
    rnd = random.Random(11)
    ctx.save()
    wall_path(ctx, right_in, +1); ctx.clip()
    ctx.new_path()
    ys = [MY0 - 25 + i * 8 for i in range(int((MY1 - MY0 + 50) / 8) + 1)]
    ctx.move_to(MX1, ys[0])
    for y in ys:
        taper = 1 - ((y - BYC) / ((MY1 - MY0) / 2 + 25)) ** 2
        ctx.line_to(MX1 + depth * max(0.15, taper) * (0.9 + 0.15 * math.sin(y * 0.09 + 1.7)), y)
    ctx.line_to(MX1, ys[-1]); ctx.close_path()
    g = cairo.LinearGradient(MX1, 0, MX1 + depth + 20, 0)
    g.add_color_stop_rgba(0, *LYE[:3], 0.85); g.add_color_stop_rgba(1, *LYE_L[:3], 0.35)
    ctx.set_source(g); ctx.fill()
    # hydroxide dots in the stain
    for i in range(int(depth * 0.5)):
        y = rnd.uniform(MY0, MY1); x = MX1 + rnd.uniform(3, depth * 0.95)
        ctx.arc(x, y, 3.2, 0, 6.28); setc(ctx, WHITE, 0.6); ctx.fill()
    ctx.restore()

def battery(ctx, t, s):
    # + can: wide, full height, on the left
    rrect(ctx, PX0, BY0, PX1 - PX0 + 8, BY1 - BY0, 10); fill_stroke(ctx, STEEL, lw=5)
    for k in range(3):                                         # can shine
        ctx.move_to(PX0 + 22 + k * 22, BY0 + 30); ctx.line_to(PX0 + 22 + k * 22, BY1 - 30)
        setc(ctx, WHITE, 0.5 - 0.12 * k); ctx.set_line_width(6); ctx.stroke()
    # gasket ring + narrower - cap on the right
    ctx.rectangle(PX1 - 4, MY0 - 18, 14, MY1 - MY0 + 36); setc(ctx, GASKET); ctx.fill()
    rrect(ctx, PX1 + 6, MY0, MX1 - PX1 - 6, MY1 - MY0, 6); fill_stroke(ctx, STEEL_D, lw=4)
    text_c(ctx, "+", PX0 + 50, BYC + 22, 64, INK, True)
    text_c(ctx, "−", MX1 - 12, BYC + 16, 44, PAPER, True)

def stage(ctx, t, s):
    # walls (muscle outside, mucosa inside)
    for inner, sign in ((left_in, -1), (right_in, +1)):
        wall_path(ctx, inner, sign); setc(ctx, TISSUE); ctx.fill()
        wall_path(ctx, inner, sign, 0, 46); setc(ctx, MUCOSA); ctx.fill()
        edge_path(ctx, inner, sign, 46); setc(ctx, TISSUE_D); ctx.set_line_width(3); ctx.set_dash([12, 8]); ctx.stroke(); ctx.set_dash([])
        edge_path(ctx, inner, sign, 110); setc(ctx, TISSUE_D, 0.6); ctx.set_line_width(2); ctx.set_dash([6, 10]); ctx.stroke(); ctx.set_dash([])
        edge_path(ctx, inner, sign, WALL); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # collapsed lumen (dark slit) above / below the battery
    ctx.new_path(); ctx.move_to(left_in(YS[0]), YS[0])
    for y in YS[1:]: ctx.line_to(left_in(y), y)
    for y in reversed(YS): ctx.line_to(right_in(y), y)
    ctx.close_path(); setc(ctx, FILL3); ctx.fill()
    # wet lining: teal film on both inner surfaces
    wa = 0.55 + 0.45 * s['wet']
    for inner, sign in ((left_in, -1), (right_in, +1)):
        edge_path(ctx, inner, sign, 3); setc(ctx, TEAL, wa); ctx.set_line_width(6 + 4 * s['wet']); ctx.stroke()
    burn(ctx, t, s['burn'])
    battery(ctx, t, s)
    bubbles(ctx, t, max(s['prev'], s['react']))
    current(ctx, t, s['current'])

def current(ctx, t, a):
    if a <= 0: return
    for P in (PTOP, PBOT):
        ctx.new_path(); ctx.move_to(*P.p[0])
        for p in P.p[1:]: ctx.line_to(*p)
        setc(ctx, SPARK, 0.35 * a); ctx.set_line_width(5); ctx.set_dash([10, 10]); ctx.stroke(); ctx.set_dash([])
        n = 9
        for i in range(n):
            u = (i / n + t * 0.28) % 1                       # + face -> - face
            x, y = P.at(u); x2, y2 = P.at(min(1, u + 0.02))
            ang = math.atan2(y2 - y, x2 - x)
            ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
            ctx.move_to(9, 0); ctx.line_to(-7, -7); ctx.line_to(-7, 7); ctx.close_path()
            setc(ctx, SPARK, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(2); ctx.stroke()
            ctx.restore()

SC, SCX, SCY, SOX, SOY = 1.4, 534, 990, 540, 930     # stage drawn 1.4x around the battery

def S(x, y):
    """Stage coords -> screen coords (for labels drawn outside the stage transform)."""
    return (SOX + (x - SCX) * SC, SOY + (y - SCY) * SC)

def overlays(ctx, t, s):
    a = win(t, 0.5, B(1) + 0.4, 0.3)
    if a > 0:
        tag(ctx, "LYE", 880, 760, LYE, a, 44)
    a = bw(t, 1)
    if a > 0:
        tag(ctx, "WATER IN THE LINING", 540, 1400, TEAL, a * sstep(t, B(1) + 1.2), 26)
    a = bw(t, 2)
    if a > 0:
        tag(ctx, "PLUS", *S(440, 720), INK, a, 28)
        tag(ctx, "MINUS", *S(640, 720), LYE, a * sstep(t, B(2) + 2.2), 28)
    a = bw(t, 3)
    if a > 0:
        tag(ctx, "THROAT · FOOD PIPE", 540, 1400, INK, a, 26)
        highlight(ctx, *S(PX0 - 4, BYC), 34, 270, TEAL, a, t)
        highlight(ctx, *S(MX1 + 4, BYC), 34, 230, TEAL, a * sstep(t, B(3) + 1.6), t)
    a = bw(t, 4)
    if a > 0:
        tag(ctx, "CURRENT · PLUS TO MINUS", 540, 1400, INK, a, 26)
    a = bw(t, 5)
    if a > 0:
        tag(ctx, "HYDROGEN GAS", *S(700, 760), INK, a * sstep(t, B(5) + 1.2), 24)
        tag(ctx, "HYDROXIDE", *S(730, 1220), LYE, a * sstep(t, B(5) + 3.0), 24)
    a = bw(t, 7)
    if a > 0:
        tag(ctx, "LAYER BY LAYER", 810, 1400, LYE, a * sstep(t, B(7) + 0.8), 24)
        tag(ctx, "PLUS SIDE: CLEAN", 260, 1400, INK2, a * sstep(t, B(7) + 2.4), 22)
    a = bw(t, 10)
    if a > 0:
        tag(ctx, "STILL MAKING LYE", 540, 1400, LYE, a * sstep(t, B(10) + 1.6), 26)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    z = 1 + 0.8 * ease(s['zoom'])
    c = S(MX1 + 40, BYC)
    ctx.save()
    ctx.rectangle(0, 180, 1080, 1320); ctx.clip()
    if z > 1.001:
        k = (z - 1) / 0.8
        tx, ty = lerp(c[0], 540, k), lerp(c[1], 900, k)
        ctx.translate(tx, ty); ctx.scale(z, z); ctx.translate(-c[0], -c[1])
    ctx.translate(SOX, SOY); ctx.scale(SC, SC); ctx.translate(-SCX, -SCY)
    stage(ctx, t, s)
    ctx.restore()
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=175, w=960, h=290):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def coin_face(ctx, cx, cy, r, plus, a):
    ctx.arc(cx, cy, r, 0, 6.28); fill_stroke(ctx, STEEL, lw=5, alpha=a)
    if plus:
        text_c(ctx, "CR2032", cx, cy - 18, 26, INK2, True, 2, a)
        text_c(ctx, "3V", cx, cy + 16, 24, INK2, True, 2, a)
        text_c(ctx, "+", cx, cy + 74, 54, INK, True, 0, a)
    else:
        ctx.arc(cx, cy, r - 4, 0, 6.28); setc(ctx, GASKET, a); ctx.fill()
        ctx.arc(cx, cy, r * 0.74, 0, 6.28); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)
        text_c(ctx, "−", cx, cy + 22, 64, PAPER, True, 0, a)

def faces_panel(ctx, t, a):
    _panel(ctx, a)
    coin_face(ctx, 280, 305, 105, True, a)
    k = a * sstep(t, B(2) + 2.2, 0.4)
    coin_face(ctx, 760, 305, 105, False, k)
    text_c(ctx, "PLUS · WIDE", 280, 448, 24, INK, True, 1.5, a)
    text_c(ctx, "MINUS · NARROW", 760, 448, 24, LYE, True, 1.5, k)
    text_c(ctx, "20 mm", 520, 312, 26, INK2, True, 1.5, a)

def volts_panel(ctx, t, a):
    _panel(ctx, a)
    # double-A: 1.5 V bar ; coin cell: 3 V bar, twice as tall
    base = 430
    rrect(ctx, 190, 225, 70, 190, 10); fill_stroke(ctx, MUSTARD, lw=4, alpha=a)
    rrect(ctx, 210, 212, 30, 14, 4); fill_stroke(ctx, STEEL, lw=3, alpha=a)
    text_c(ctx, "AA", 225, 335, 26, INK, True, 1, a)
    ctx.arc(225, 455, 0, 0, 1)
    k = sstep(t, B(9) + 0.6, 0.8)
    for x, v, col, lab in ((390, 1.5, TEAL, "1.5 V"), (560, 3.0, RED, "3 V")):
        h = 60 * v * (k if v > 2 else 1)
        ctx.rectangle(x - 45, base - h, 90, h); fill_stroke(ctx, col, lw=4, alpha=a)
        text_c(ctx, lab, x, base - h - 14, 32, col, True, 1, a)
    ctx.arc(790, 320, 80, 0, 6.28); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    text_c(ctx, "3V", 790, 334, 40, INK, True, 1, a)
    text_c(ctx, "2X THE PUSH", 790, 445, 28, RED, True, 1.5, a * sstep(t, B(9) + 2.0))

def dead_panel(ctx, t, a):
    _panel(ctx, a)
    # remote: low-battery icon
    rrect(ctx, 140, 195, 150, 225, 30); fill_stroke(ctx, INK2, lw=4, alpha=a)
    rrect(ctx, 165, 225, 100, 50, 8); fill_stroke(ctx, PAPER, lw=3, alpha=a)
    rrect(ctx, 180, 238, 60, 24, 4); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(240, 245, 8, 10); setc(ctx, INK, a); ctx.fill()
    blink = 0.5 + 0.5 * math.sin(t * 8)
    ctx.rectangle(184, 242, 10, 16); setc(ctx, RED, a * blink); ctx.fill()
    for i in range(3):
        for j in range(2):
            ctx.arc(190 + j * 50, 310 + i * 36, 11, 0, 6.28); fill_stroke(ctx, FILL3, lw=2, alpha=a)
    text_c(ctx, "“DEAD”", 215, 450, 24, RED, True, 1, a)
    # meter on the cell
    k = a * sstep(t, B(10) + 0.8, 0.4)
    rrect(ctx, 420, 215, 300, 190, 18); fill_stroke(ctx, PAPER, lw=4, alpha=k)
    ctx.new_path(); ctx.arc(570, 380, 120, math.pi * 1.15, math.pi * 1.85); setc(ctx, INK2, k); ctx.set_line_width(4); ctx.stroke()
    ang = math.pi * (1.15 + 0.7 * (1.3 / 3.0) * sstep(t, B(10) + 1.0, 0.9))
    straight_arrow(ctx, 570, 380, 570 + 105 * math.cos(ang), 380 + 105 * math.sin(ang), RED, k, lw=5, head=10)
    text_c(ctx, "~1.3 V", 870, 300, 54, RED, True, 1, k)
    text_c(ctx, "STILL ENOUGH", 870, 360, 24, INK, True, 1.5, k)

def recap_panel(ctx, t, a):
    _panel(ctx, a)
    k2 = sstep(t, B(11) + 3.0, 0.5)
    a1 = a * (1 - k2)
    if a1 > 0:
        ctx.arc(190, 320, 70, 0, 6.28); fill_stroke(ctx, STEEL, lw=4, alpha=a1)
        text_c(ctx, "+", 330, 345, 70, INK, True, 0, a1)
        ctx.move_to(470, 250); ctx.curve_to(500, 300, 530, 330, 530, 360)
        ctx.arc(470, 360, 60, 0, math.pi); ctx.curve_to(410, 330, 440, 300, 470, 250)
        setc(ctx, WATER, a1); ctx.fill_preserve(); setc(ctx, INK, a1); ctx.set_line_width(4); ctx.stroke()
        text_c(ctx, "=", 640, 345, 70, INK, True, 0, a1)
        text_c(ctx, "LYE", 820, 350, 84, LYE, True, 3, a1)
    a2 = a * k2
    if a2 > 0:
        # back of a remote: battery door held by a screw
        rrect(ctx, 250, 195, 420, 255, 40); fill_stroke(ctx, INK2, lw=4, alpha=a2)
        ctx.arc(460, 325, 80, 0, 6.28); fill_stroke(ctx, FILL3, lw=4, alpha=a2)
        ctx.arc(460, 325, 18, 0, 6.28); fill_stroke(ctx, STEEL, lw=3, alpha=a2)
        rot = 2.5 * sstep(t, B(11) + 3.3, 1.0)
        ctx.save(); ctx.translate(460, 325); ctx.rotate(rot)
        ctx.move_to(-11, 0); ctx.line_to(11, 0); ctx.move_to(0, -11); ctx.line_to(0, 11)
        setc(ctx, INK, a2); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
        highlight(ctx, 460, 325, 40, 40, RED, a2, t)
        text_c(ctx, "SCREWED SHUT", 845, 335, 30, RED, True, 1.5, a2)

def draw_hud(ctx, t, E):
    a = win(t, B(2) + 0.2, B(3), 0.3)
    if a > 0: faces_panel(ctx, t, a)
    a = win(t, B(9) + 0.2, B(10), 0.3)
    if a > 0: volts_panel(ctx, t, a)
    a = win(t, B(10) + 0.2, B(11), 0.3)
    if a > 0: dead_panel(ctx, t, a)
    a = win(t, B(11) + 0.3, B(12) + 0.4, 0.3)
    if a > 0: recap_panel(ctx, t, a)

SFX = [(0.5, 'pop'), (B(1) + 1.2, 'pop'), (B(2) + 0.3, 'pop'), (B(2) + 2.2, 'pop'), (B(3) + 0.3, 'pop'),
       (B(4) + 0.2, 'click'), (B(5) + 1.2, 'pop'), (B(5) + 3.0, 'pop'), (B(7) + 0.8, 'pop'), (B(7) + 2.4, 'pop'),
       (B(9) + 0.6, 'pop'), (B(9) + 2.0, 'pop'), (B(10) + 0.8, 'click'), (B(10) + 1.6, 'pop'),
       (B(11) + 0.3, 'pop'), (B(11) + 3.3, 'click')]
HUM = []

# ---------------------------------------------------------------- cards
def h2o(ctx, x, y, a, r=26, oh=False):
    """Water molecule (O + 2 H); oh=True: hydroxide (O + 1 H), drawn in the lye colour."""
    col = LYE if oh else TEAL
    ctx.arc(x, y, r, 0, 6.28); setc(ctx, col, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    hs = [(-0.9,)] if oh else [(-0.9,), (0.9,)]
    for (ang,) in hs:
        hx, hy = x + r * 1.05 * math.cos(ang - math.pi / 2), y + r * 1.05 * math.sin(ang - math.pi / 2)
        ctx.arc(hx, hy, r * 0.5, 0, 6.28); setc(ctx, PAPER, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(2.5); ctx.stroke()

def card_lye(ctx, t, lt, a):
    card_frame(ctx, "THE MINUS FACE", a, "WATER SPLITS: HYDROGEN GAS + LYE", LYE)
    # minus plate on the left
    rrect(ctx, 130, 265, 46, 270, 8); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)
    text_c(ctx, "−", 153, 412, 54, PAPER, True, 0, a)
    rnd = random.Random(5)
    # electrons leave the plate (to the right)
    for i in range(6):
        u = (i / 6 + lt * 0.6) % 1
        x = lerp(190, 300, u); y = 290 + i * 42
        ctx.arc(x, y, 9, 0, 6.28); setc(ctx, MUSTARD, a * (1 - u)); ctx.fill_preserve(); setc(ctx, INK, a * (1 - u)); ctx.set_line_width(2); ctx.stroke()
    # water molecules drifting in; near the plate they split
    for i in range(5):
        y = 300 + i * 52
        h2o(ctx, 560 + (i % 2) * 70, y, a, 22)
    # hydroxide piling up against the plate (grows with lt)
    n = int(clamp(lt / 4.0) * 12) + 2
    for i in range(n):
        h2o(ctx, 215 + (i % 3) * 46, 300 + (i // 3) * 52, a, 18, oh=True)
    # hydrogen bubbles rising (UP)
    for i in range(5):
        u = (i / 5 + lt * 0.5) % 1
        x = 360 + (i % 3) * 30; y = 520 - 260 * u
        ctx.arc(x, y, 12, 0, 6.28); setc(ctx, WHITE, a * (1 - u)); ctx.fill_preserve(); setc(ctx, INK, a * (1 - u)); ctx.set_line_width(2); ctx.stroke()
    straight_arrow(ctx, 470, 470, 470, 290, INK2, a, lw=4, head=10)
    text_c(ctx, "H2 GAS", 470, 272, 24, INK, True, 1, a)
    text_c(ctx, "WATER", 680, 272, 24, TEAL, True, 1.5, a)
    text_c(ctx, "OH- = LYE", 820, 360, 34, LYE, True, 1.5, a)
    text_c(ctx, "STAYS ON THE TISSUE", 820, 410, 22, INK, True, 1.5, a * sstep(lt, 1.6, 0.3))

def card_clock(ctx, t, lt, a):
    card_frame(ctx, "HOW FAST?", a, "IN ANIMAL TESTS", INK2)
    cx, cy, r = 300, 395, 130
    ctx.arc(cx, cy, r, 0, 6.28); fill_stroke(ctx, PAPER, lw=5, alpha=a)
    frac = clamp(lt / 4.5)                                  # 0 -> 2 hours of the clock dial
    mins = 120 * frac
    # filled sector = elapsed time (clockwise on screen = increasing angle)
    h_end = -math.pi / 2 + 2 * math.pi * (mins / 720)
    ctx.move_to(cx, cy); ctx.arc(cx, cy, r - 10, -math.pi / 2, -math.pi / 2 + 2 * math.pi * min(1, mins / 60) if mins < 60 else 3 * math.pi / 2)
    ctx.close_path(); setc(ctx, RED, 0.2 * a); ctx.fill()
    for k in range(12):
        ang = -math.pi / 2 + k * math.pi / 6
        ctx.move_to(cx + (r - 22) * math.cos(ang), cy + (r - 22) * math.sin(ang))
        ctx.line_to(cx + (r - 8) * math.cos(ang), cy + (r - 8) * math.sin(ang))
        setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    m_ang = -math.pi / 2 + 2 * math.pi * (mins / 60)
    straight_arrow(ctx, cx, cy, cx + 100 * math.cos(m_ang), cy + 100 * math.sin(m_ang), INK, a, lw=6, head=10)
    straight_arrow(ctx, cx, cy, cx + 60 * math.cos(h_end), cy + 60 * math.sin(h_end), INK, a, lw=8, head=10)
    ctx.arc(cx, cy, 9, 0, 6.28); setc(ctx, INK, a); ctx.fill()
    text_c(ctx, f"{int(mins // 60)} h {int(mins % 60):02d}", 680, 300, 56, INK, True, 2, a)
    k1 = a * clamp((mins - 15) / 5)
    text_c(ctx, "15 MIN · BURNS BEGIN", 680, 380, 28, LYE, True, 1.5, k1)
    k2 = a * clamp((mins - 115) / 5)
    text_c(ctx, "2 H · A HOLE CAN FORM", 680, 450, 30, RED, True, 1.5, k2)

CARDS = {'lye': card_lye, 'clock': card_clock}
