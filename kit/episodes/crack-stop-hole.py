"""Cogwise episode: To save this cracked part, you drill more of it away.
One idea: a crack is a notch with an almost-zero tip radius, so the stress piles up at its tip
(Inglis: the smaller the tip radius, the higher the peak stress) and the crack grows a little at
every load cycle. A round hole drilled just past the tip replaces that sharp tip by a round edge:
the peak drops to about 3x the average (Kirsch), so the crack has nothing left to grow from.

VIEW (screen coordinates, y grows DOWN): a flat plastic panel seen FACE-ON.
  - The panel is PULLED by its TOP and BOTTOM edges (grips): top arrows point UP (-y),
    bottom arrows point DOWN (+y) = tension along y.
  - The crack runs HORIZONTALLY from the LEFT edge, at y = YC, perpendicular to the pull
    (that is the direction a tension crack grows). Its mouth (left) is open, its tip (right) is sharp.
  - Force lines are VERTICAL (along the pull) and detour to the RIGHT of the crack tip / hole.
  - The drill is seen END-ON (its axis points at the viewer): a spinning disc with two cutting lips.
TIMELINE: beats 1-2 = the end state (crack tip at 640, hole drilled there).
  Beat 3 = "earlier": tip back at 520. Beat 8: three pulls, tip 520 -> 560 -> 600 -> 640.
  Beat 9: the hole is drilled at 640 (same place as the hook). Beat 12: pulled again, tip stays.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="crack-stop-hole",
    title="To save this cracked part, you drill more of it away 🔧 #Shorts",
    description=("A crack grows from its sharp tip. Take the sharp tip away and it stops.\n\n"
                 "#Shorts #howthingswork #engineering #diy #cogwise"),
    hashtags=["Shorts", "howthingswork", "engineering", "diy", "repair", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Stress_concentration",
        "https://blog.vibrationdata.com/?p=150185",
        "https://plasticranger.com/how-to-repair-acrylic-crack/",
        "https://www.nps.gov/inde/learn/historyculture/stories-libertybell.htm",
    ],
)

BEATS = [
    dict(dur=4.9, title="REMOVE MORE?", caption="To save this cracked part, you remove even more of it."),
    dict(dur=5.7, title="THE SECRET", caption="You drill a hole right at the crack's tip, and it stops growing."),
    dict(dur=5.3, title="THE PULL", caption="Every time this panel is pulled, force flows through it like water."),
    dict(dur=5.3, title="1 · AROUND THE CRACK", caption="The crack blocks that flow, so the force squeezes around its end."),
    dict(dur=5.3, title="THE TIP", caption="And a crack's end is incredibly sharp, almost no width at all."),
    dict(dur=5.7, title=None, caption="The sharper the corner, the more force piles up in one tiny spot.", card='corner'),
    dict(dur=5.3, title="DOZENS OF TIMES", caption="At that tip, the plastic carries dozens of times the average stress."),
    dict(dur=4.9, title="ONE STEP AT A TIME", caption="So it tears a little further, every single time it's pulled."),
    dict(dur=6.5, title="2 · THE HOLE", caption="Now drill a three millimetre hole, an eighth of an inch, just past the tip."),
    dict(dur=4.9, title="3 · ROUND EDGE", caption="The sharp point is gone, replaced by a wide, round edge."),
    dict(dur=6.1, title=None, caption="Force now flows smoothly around the hole, at only about three times the average.", card='around'),
    dict(dur=6.1, title="LESS IS MORE", caption="Less plastic, but no sharp tip. The crack has nothing left to grow from."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette / geometry
ACRYL = hexc('#cfe3ea'); ACRYL_E = hexc('#8fb3c2')
STEEL = hexc('#b9bec4'); STEEL_D = hexc('#7d848b')
GRIP = hexc('#3b3842')
PX0, PX1, PY0, PY1 = 180, 900, 540, 1300   # panel (left, right, top, bottom)
YC = 920                                    # crack line (y)
R_HOLE = 26                                 # hole radius (px) -> "3 mm · 1/8 in"
TIP_END = 640                               # final tip x (hook + after beat 8)
HCX = TIP_END + 10                          # hole centre: just past the tip

# ---------------------------------------------------------------- helpers
def pulse(t, t0, d=0.9):
    """one pull: 0 -> 1 -> 0 over d seconds from t0"""
    u = (t - t0) / d
    return math.sin(math.pi * u) ** 2 if 0 <= u <= 1 else 0.0

PULLS_8 = [B(7) + 0.3, B(7) + 1.8, B(7) + 3.3]          # three pulls in beat 8, each tears one notch
PULLS_12 = [B(11) + 0.4, B(11) + 1.9, B(11) + 3.4]      # three pulls in beat 12, nothing grows

def tip_x(t):
    if t < B(2) - 0.3:                                  # hook: end state, crack ticks 600 -> 640
        return lerp(600, TIP_END, ease(clamp((t - 0.35) / 0.4)))
    if t < B(7):                                        # "earlier"
        return 520
    x = 520
    for p in PULLS_8:                                   # one notch at the peak of each pull
        x += 40 * ease(clamp((t - p - 0.35) / 0.3))
    return x

def hole_k(t):
    """0 = no hole, 1 = hole fully drilled"""
    if t < B(2) - 0.3:
        return ease(clamp((t - (B(1) + 0.9)) / 1.2))
    if t < B(2) + 0.4:                                  # flashback: the hole fades out
        return 1 - ease(clamp((t - (B(2) - 0.3)) / 0.6))
    return ease(clamp((t - (B(8) + 1.3)) / 1.3))

def drill_a(t):
    """drill visibility (end-on bit)"""
    return max(win(t, 1.0, B(1) + 2.6, 0.4), win(t, B(8) + 0.2, B(8) + 3.4, 0.4))

def pull_amount(t):
    p = 0.0
    if B(2) <= t < B(7):                                # beats 3-7: a steady, gentle pull
        p = 0.55 + 0.25 * math.sin((t - B(2)) * 2.4)
    for q in PULLS_8 + PULLS_12:
        p = max(p, pulse(t, q))
    p = max(p, pulse(t, 0.2, 0.7))                       # hook tick
    return p

def show_lines(t):
    return clamp(ease((t - B(2) - 0.3) / 0.8)) * (1 - win(t, B(7) - 0.1, B(8) + 0.1, 0.3) * 0.75)

# ---------------------------------------------------------------- force-line field
def field_x(x0, y, xo, yc, x_lo, x_hi, p, sig0):
    """x of a vertical force line starting at x0, at height y, around an obstacle whose
    right-most point is xo (on the line y = yc). All lines get squeezed to the right of xo."""
    u = (x0 - x_lo) / (x_hi - x_lo)
    xm = xo + 10 + (x_hi - xo - 10) * (u ** p)
    d = xm - x0
    if d <= 0: return x0
    sig = sig0 + 0.2 * d
    return x0 + d * math.exp(-((y - yc) / sig) ** 2 / 2)

def force_lines(ctx, t, a, xo, yc, x_lo, x_hi, y0, y1, p, n, sig0=26, hot=1.0, lw=4, flow=True):
    if a <= 0: return
    for i in range(n):
        x0 = lerp(x_lo + 18, x_hi - 18, i / (n - 1))
        pts = []
        for k in range(61):
            y = lerp(y0, y1, k / 60)
            pts.append((field_x(x0, y, xo, yc, x_lo, x_hi, p, sig0), y))
        ctx.move_to(*pts[0])
        for q in pts[1:]: ctx.line_to(*q)
        # lines bent hard toward the tip are tinted red
        xm = field_x(x0, yc, xo, yc, x_lo, x_hi, p, sig0)
        heat = clamp(1 - (xm - xo) / 120) * hot
        setc(ctx, lerpc(TEAL, RED, heat), a * 0.9); ctx.set_line_width(lw)
        if flow:
            ctx.set_dash([22, 14], -(t * 60) % 36)       # dashes move DOWN (+y): the flow
        ctx.stroke(); ctx.set_dash([])

def hot_spot(ctx, x, y, r, a, col=RED):
    if a <= 0: return
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], 0.85 * a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()

# ---------------------------------------------------------------- the panel
def crack_path(ctx, x0, xt, yc, mouth, seed=3):
    """jagged V from the left edge x0 (open, half-width `mouth`) to the sharp tip xt"""
    rnd = random.Random(seed)
    n = max(4, int((xt - x0) / 22))
    jit = [rnd.uniform(-7, 7) for _ in range(n + 1)]
    top, bot = [], []
    for i in range(n + 1):
        u = i / n; x = lerp(x0, xt, u); w = mouth * (1 - u)
        yy = yc + jit[i] * (1 - u * 0.8)
        top.append((x, yy - w)); bot.append((x, yy + w))
    ctx.move_to(*top[0])
    for q in top[1:]: ctx.line_to(*q)
    for q in reversed(bot[:-1]): ctx.line_to(*q)
    ctx.close_path()

def drill(ctx, x, y, t, a, approach):
    """drill bit seen END-ON (axis toward the viewer), spinning"""
    if a <= 0: return
    s = lerp(1.35, 1.0, approach)
    r = (R_HOLE + 5) * s
    ctx.arc(x + 10, y + 12, r, 0, 2 * math.pi); setc(ctx, INK, 0.18 * a); ctx.fill()   # shadow
    ctx.arc(x, y, r, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    rot = t * 9
    for k in (0, math.pi):                              # two cutting lips / flutes
        ctx.save(); ctx.translate(x, y); ctx.rotate(rot + k)
        ctx.move_to(0, 0); ctx.curve_to(r * 0.3, -r * 0.6, r * 0.8, -r * 0.5, r * 0.98, -r * 0.1)
        ctx.line_to(r * 0.98, r * 0.2); ctx.curve_to(r * 0.6, -r * 0.1, r * 0.3, -r * 0.2, 0, 0)
        setc(ctx, STEEL_D, a); ctx.fill(); ctx.restore()
    ctx.arc(x, y, 4, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()

def panel(ctx, t, s):
    pl = s['pull']
    stretch = 6 * pl                                     # the panel gets a hair longer when pulled
    y0, y1 = PY0 - stretch, PY1 + stretch
    # grips (top and bottom)
    for gy in (y0 - 46, y1):
        rrect(ctx, PX0 - 30, gy, PX1 - PX0 + 60, 46, 8); fill_stroke(ctx, GRIP, lw=3)
        for bx in (PX0 + 30, (PX0 + PX1) / 2, PX1 - 30):
            ctx.arc(bx, gy + 23, 9, 0, 2 * math.pi); setc(ctx, STEEL); ctx.fill()
    # the panel
    ctx.rectangle(PX0, y0, PX1 - PX0, y1 - y0); fill_stroke(ctx, ACRYL, lw=5)
    for k in range(3):                                   # sheen
        ctx.move_to(PX0 + 520 + k * 60, y0 + 30); ctx.line_to(PX0 + 600 + k * 60, y0 + 30)
        ctx.line_to(PX0 + 380 + k * 60, y1 - 30); ctx.line_to(PX0 + 300 + k * 60, y1 - 30); ctx.close_path()
        setc(ctx, WHITE, 0.10); ctx.fill()
    # pull arrows: top one UP (-y), bottom one DOWN (+y) = tension
    pa = s['pull_arrows']
    if pa > 0:
        for x in (PX0 + 140, (PX0 + PX1) / 2, PX1 - 140):
            straight_arrow(ctx, x, y0 - 56, x, y0 - 56 - 90 - 30 * pl, RED, pa, lw=12, head=22)
            straight_arrow(ctx, x, y1 + 56, x, y1 + 56 + 90 + 30 * pl, RED, pa, lw=12, head=22)

    xt = s['tip']; hk = s['hole']
    # force lines (behind the crack): obstacle = crack tip, or the hole's right edge
    xo = lerp(xt, HCX + R_HOLE, hk)
    p = lerp(2.2, 1.25, hk); sig0 = lerp(26, 60, hk)
    force_lines(ctx, t, s['lines'], xo, YC, PX0, PX1, y0 + 8, y1 - 8, p, 15, sig0=sig0, hot=1 - 0.75 * hk)
    # stress hot spot: at the crack tip, or (paler) at the hole's edge
    hot_spot(ctx, xt + 4, YC, 70 + 20 * pl, s['hot'] * (1 - hk))
    hot_spot(ctx, HCX + R_HOLE, YC, 48, s['hot'] * hk * 0.45, ORANGE)
    # the crack (mouth opens a little more when pulled)
    crack_path(ctx, PX0 - 2, xt, YC, 9 + 8 * pl)
    setc(ctx, INK, 0.92); ctx.fill()
    # the hole (shows the paper behind) — drilled just past the tip
    if hk > 0:
        ctx.arc(HCX, YC, R_HOLE * hk, 0, 2 * math.pi)
        setc(ctx, WALL1); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # the drill, end-on, over the hole spot
    da = s['drill']
    if da > 0:
        drill(ctx, HCX, YC, t, da, s['approach'])

def state(t):
    s = {}
    s['tip'] = tip_x(t)
    s['hole'] = hole_k(t)
    s['drill'] = drill_a(t)
    s['approach'] = max(ease(clamp((t - 1.0) / 0.8)), ease(clamp((t - B(8) - 0.2) / 0.8)))
    s['pull'] = pull_amount(t)
    s['pull_arrows'] = max(bw(t, 2, 4), bw(t, 5), win(t, B(7), B(8), 0.3), win(t, B(11) + 0.1, B(12), 0.3))
    s['lines'] = show_lines(t) if t < B(11) else 0.6
    s['hot'] = max(0.35 * clamp(ease((t - B(3)) / 0.8)) * (1 if t < B(8) + 2 else 1), 0.0) if t >= B(3) else 0.0
    s['hot'] = max(s['hot'], bw(t, 5, 7))
    if B(2) - 0.3 > t: s['hot'] = 0.0
    return s

def overlays(ctx, t, s):
    a = win(t, 0.2, B(1), 0.3)
    tag(ctx, "CRACK", 300, YC - 80, RED, a, 26)
    a = win(t, B(1) + 2.0, B(2) - 0.3, 0.3)
    tag(ctx, "HOLE", HCX, YC + 90, RED, a, 26)
    tag(ctx, "STOPPED", 330, YC - 80, TEAL, a, 26)
    a = max(bw(t, 2, 4), bw(t, 7))
    tag(ctx, "EARLIER", 540, 440 - 70, INK, a, 24)
    a = bw(t, 3)
    if a > 0:
        highlight(ctx, s['tip'] + 30, YC, 90, 130, RED, a, t)
        tag(ctx, "SQUEEZED", s['tip'] + 150, YC + 190, RED, a, 24)
    a = bw(t, 4)
    if a > 0:
        tag(ctx, "TIP", s['tip'] + 40, YC - 46, RED, a, 20)
    a = bw(t, 7)
    if a > 0:
        n = sum(1 for p in PULLS_8 if t > p + 0.5)
        tag(ctx, f"+{n} STEP" + ("S" if n != 1 else ""), 760, YC - 110, RED, a * (1 if n else 0), 26)
    a = win(t, B(8) + 2.6, B(10), 0.3)
    tag(ctx, "Ø 3 mm · 1/8 in", HCX + 140, YC + 100, INK, a, 24)
    a = bw(t, 9)
    if a > 0:
        highlight(ctx, HCX, YC, R_HOLE + 18, R_HOLE + 18, MUSTARD, a, t)
        tag(ctx, "ROUND EDGE", HCX + 40, YC - 74, INK, a, 20)
    a = bw(t, 11)
    if a > 0:
        tag(ctx, "PULLED · NO GROWTH", 540, 470 - 60, TEAL, a, 26)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    panel(ctx, t, s)
    overlays(ctx, t, s)

# camera: push in on the tip ("THE TIP"), a bit on the hot spot, then on the round edge of the hole
CAMKEYS = [(0, 540, 900, 1.0), (0.9, 600, 920, 1.25), (B(2) - 0.4, 540, 900, 1.0),
           (B(4) + 0.1, 560, 860, 1.7), (B(5) - 0.5, 540, 900, 1.0),
           (B(6) + 0.1, 560, 880, 1.3), (B(7) - 0.2, 540, 900, 1.0),
           (B(9) + 0.1, HCX - 20, 860, 1.7), (B(10) - 0.5, 540, 900, 1.0)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)

def draw_hud(ctx, t, E):
    a = win(t, B(6) + 0.5, B(7), 0.3)
    if a > 0: hud(ctx, "STRESS AT THE TIP", "× 30+", "the average · and climbing", a, RED, x=520, y=196, w=520)
    a = win(t, B(8) + 0.6, B(9), 0.3)
    if a > 0: hud(ctx, "DRILL", "Ø 3 mm", "1/8 in · just past the tip", a, TEAL, x=520, y=196, w=520)

SFX = [(0.3, 'pop'), (B(1) + 1.0, 'click'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(4) + 0.3, 'pop'),
       (B(6) + 0.4, 'pop'), (B(8) + 1.4, 'click'), (B(9) + 0.3, 'pop'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def _mini(ctx, x0, x1, y0, y1, a):
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); fill_stroke(ctx, ACRYL, lw=4, alpha=a)

def card_corner(ctx, t, lt, a):
    card_frame(ctx, "SHARP CORNERS COLLECT FORCE", a, "ROUND = SPREAD OUT · SHARP = PILED UP", RED)
    yc = 400
    # left: round-ended notch from the left edge
    x0, x1 = 140, 500
    _mini(ctx, x0, x1, 262, 540, a)
    force_lines(ctx, t, a, 320 + 24, yc, x0, x1, 266, 536, 1.3, 7, sig0=40, hot=0.5, lw=3)
    hot_spot(ctx, 344, yc, 40, a * 0.35, ORANGE)
    ctx.move_to(x0 - 2, yc - 24); ctx.line_to(320, yc - 24); ctx.arc(320, yc, 24, -math.pi / 2, math.pi / 2)
    ctx.line_to(x0 - 2, yc + 24); ctx.close_path(); setc(ctx, INK, 0.92 * a); ctx.fill()
    text_c(ctx, "ROUND", 320, 258, 24, TEAL, True, 1, a)
    # right: sharp V notch, same depth
    x0, x1 = 580, 940
    _mini(ctx, x0, x1, 262, 540, a)
    force_lines(ctx, t, a, 784, yc, x0, x1, 266, 536, 2.3, 7, sig0=18, hot=1.0, lw=3)
    hot_spot(ctx, 788, yc, 56, a, RED)
    ctx.move_to(x0 - 2, yc - 24); ctx.line_to(784, yc); ctx.line_to(x0 - 2, yc + 24); ctx.close_path()
    setc(ctx, INK, 0.92 * a); ctx.fill()
    text_c(ctx, "SHARP", 760, 258, 24, RED, True, 1, a)

def card_around(ctx, t, lt, a):
    card_frame(ctx, "AROUND THE HOLE", a, "THE FORCE SPREADS OUT · ≈ ×3 AVERAGE", TEAL)
    x0, x1, yc = 260, 820, 400
    _mini(ctx, x0, x1, 262, 540, a)
    hx, r = 560, 40
    force_lines(ctx, t, a, hx + r, yc, x0, x1, 266, 536, 1.2, 11, sig0=60, hot=0.25, lw=3)
    hot_spot(ctx, hx + r, yc, 44, a * 0.4, ORANGE)
    crack_path(ctx, x0 - 2, hx - 6, yc, 8)
    setc(ctx, INK, 0.92 * a); ctx.fill()
    ctx.arc(hx, yc, r, 0, 2 * math.pi)
    setc(ctx, WALL1, a); ctx.fill_preserve(); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    # pull arrows on the mini panel (up at the top, down at the bottom)
    straight_arrow(ctx, 170, 330, 170, 280, RED, a, lw=7, head=14)
    straight_arrow(ctx, 170, 470, 170, 520, RED, a, lw=7, head=14)
    text_c(ctx, "×3", 900, 412, 40, ORANGE, True, 1, a)

CARDS = {'corner': card_corner, 'around': card_around}
