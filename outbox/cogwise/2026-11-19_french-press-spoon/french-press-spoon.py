"""Cogwise episode: 5.9 million coffee makers were recalled because of a spoon.
One idea: glass doesn't break where it's thin, it breaks where it's scratched. A metal spoon scrapes the inside of
the carafe and leaves an invisible scratch with a sharp tip. Any pull on the glass (plunger pressure, a cold rinse of
hot glass) crowds around that tip, so the stress there is many times higher; glass can't yield, the tip creeps deeper,
until the crack runs around the wall and the carafe opens, full of water at ~93 °C (200 °F).
News hook: CPSC recall 27-055 (29 Oct 2026), 5.9 M Bodum presses, 70 breakage reports, 48 burns; the free fix is a
plastic spoon (softer than glass: it cannot scratch it).

VIEW (screen coordinates, y grows DOWN): main stage = SIDE CUT-AWAY of a French press, open side toward us.
  - Glass carafe = two vertical walls x GL..GL+W_G (left) and GR-W_G..GR (right), bottom y BOT, rim y RIM.
  - Coffee (brown) fills from LVL down to BOT. The lid sits on the rim; the rod goes UP to the knob.
    Pressing = the filter disc moves DOWN (y increases) through the coffee.
  - Pressure arrows: from the coffee OUTWARD into the walls (left wall: arrow points left; right wall: right).
  - The scratch is on the INSIDE face of the LEFT wall at y SY (the face that touches the coffee, x = GL+W_G).
    The crack starts there and runs across the front of the glass to the right wall (= around the wall).
  - Cold rinse: the carafe is empty and hot (orange walls); cold water falls DOWN from the top into it,
    the inside face turns blue and shrinks: small arrows along the inside face pointing toward each other.
  - Flow panel / tip card = CROSS-SECTION through the wall, the inside face on TOP, outside face at the bottom.
    The pull arrows at both ends point OUTWARD (tension along the wall). The scratch is a V notch coming
    DOWN from the inside face; the force lines dip under its tip and crowd together just below it.
  - Scrape card = looking straight at the inside face; the spoon edge slides left -> right and leaves a fine line.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="french-press-spoon",
    title="5.9 million coffee makers were recalled because of a spoon ☕ #Shorts",
    description=("Glass rarely breaks where it's thin. It breaks where it's scratched.\n\n"
                 "#Shorts #howthingswork #coffee #frenchpress #cogwise"),
    hashtags=["Shorts", "howthingswork", "coffee", "frenchpress", "cogwise"],
    sources=[
        "https://www.cpsc.gov/Recalls/2027/Bodum-USA-Recalls-5-9-Million-French-Press-Coffee-Makers-with-Replaceable-Glass-Carafes-Due-to-Risk-of-Serious-Burn-Injury",
        "https://www.foodnetwork.com/fn-dish/news/bodum-recall-french-press-coffee-makers",
        "https://www.medicaldaily.com/bodum-french-press-recall-burn-reports-plastic-spoon-480699",
        "https://saint-gobain-glass.co.uk/document/the-strength-of-glass",
        "https://www.britglass.org.uk/knowledge-base/digital-library-and-information-services/crack-initiation-important-understanding",
    ],
)

def _d(c, extra=0.0):
    return round(0.42 * len(c.split()) + 0.7 + extra, 1)

_B = [
    ("RECALLED", "Five point nine million French presses just got recalled. The fix? A plastic spoon.", None),
    ("THE SECRET", "Glass rarely breaks where it's thin. It breaks where it's scratched.", None),
    (None, "A metal spoon's hard edge scrapes the inside of the glass as you stir.", 'scrape'),
    ("1 · THE SCRATCH", "It leaves a scratch too fine to see, ending in a razor-sharp tip.", None),
    ("2 · THE PULL", "Press the plunger, and the coffee pushes outward. The glass wall stretches.", None),
    ("FORCE LINES", "Picture that stretch as lines running through the glass. The scratch cuts them.", None),
    (None, "They crowd around its tip, so the pull there gets many times stronger.", 'tip'),
    ("3 · THE CRACK", "Glass can't bend to soften that peak, so the tip creeps deeper.", None),
    ("HOT, THEN COLD", "Rinse it cold while it's still hot, and the inside shrinks first. Another pull.", None),
    ("BURST", "One day it runs around the wall, and out pours water at ninety-three Celsius, two hundred Fahrenheit.", None),
    ("THE RECALL", "Seventy reported breaks, forty-eight burns. So owners get a free plastic spoon.", None),
    ("SOFTER THAN GLASS", "Plastic is softer than glass. It can't cut the tip that starts a crack.", None),
]
BEATS = [dict(dur=_d(c), title=ti, caption=c, card=k) for ti, c, k in _B]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.4):
    return ease(clamp((t - t0) / d))

# ---------------------------------------------------------------- palette
GLASS = hexc('#cfe7ee'); GLASS_E = hexc('#7fb3c4')
COFFEE = hexc('#5a3820'); COFFEE_L = hexc('#7a5032'); CREMA = hexc('#b98a55')
STEEL = hexc('#9aa0a8'); STEEL_D = hexc('#5d6168'); STEEL_L = hexc('#d4d8dd')
PLAST = hexc('#f6f1e4'); PLAST_E = hexc('#b9ae94')
WATER = hexc('#3d8fd6'); WATER_L = hexc('#9cc8ee')
HOT = hexc('#f2902b')
GREEN = hexc('#3d8b4f')

# ---------------------------------------------------------------- geometry (side cut-away)
GL, GR = 345, 735      # outer faces of the glass walls
W_G = 16               # wall thickness (exaggerated)
RIM, BOT = 720, 1395   # top rim and bottom of the carafe
LVL = 800              # coffee level
SY = 1110              # scratch height on the LEFT wall (inside face x = GL + W_G)
SX = GL + W_G
LID_Y = 680            # lid top
F_TOP, F_BOT = 800, 1230
ROD = 575              # rod length: knob rides down with the filter, ends just above the lid

def state(t):
    s = {}
    s['press'] = ease(clamp((t - B(4) - 0.3) / (BEATS[4]['dur'] - 0.8))) if t < B(8) else 1.0
    # coffee shown except during the cold rinse and after the burst
    s['coffee'] = 1.0 - win(t, B(8), B(9), 0.3)
    s['plunger'] = 1.0 - max(win(t, B(8), B(9), 0.3), win(t, B(11), B(12) + 3, 0.3))
    s['empty_hot'] = win(t, B(8), B(9), 0.3)
    s['recall'] = win(t, 0.0, B(1), 0.3)
    s['plastic_fix'] = win(t, 0.3, B(1), 0.25)
    s['metal'] = win(t, B(1), B(3), 0.3)
    s['scratch'] = sstep(t, B(1) + 1.6, 0.6) if t < B(10) else 0.0
    s['scr_hi'] = max(bw(t, 1), bw(t, 3))
    s['push'] = bw(t, 4, 6)
    s['crack'] = 0.0
    if B(7) <= t < B(9):
        s['crack'] = 0.06 + 0.10 * ease(clamp((t - B(7) - 0.5) / 2.5)) + (0.06 * ease(clamp((t - B(8) - 1.5) / 2.0)) if t > B(8) else 0)
    elif B(9) <= t < B(10):
        s['crack'] = 0.22 + 0.78 * ease(clamp((t - B(9) - 0.3) / 1.6))
    s['spill'] = clamp((t - B(9) - 1.6) / 1.0) if B(9) <= t < B(10) + 0.3 else 0.0
    s['spill_a'] = win(t, B(9), B(10), 0.3)
    s['cold'] = bw(t, 8)
    s['plastic_stir'] = win(t, B(11), B(12) + 3, 0.3)
    s['fresh'] = win(t, B(10), B(12) + 3, 0.3)
    return s

# ---------------------------------------------------------------- spoon
def spoon(ctx, x, y, ang, a, metal=True, scale=1.0):
    """Spoon with its bowl centred at (x, y); handle along angle `ang` (radians, screen coords) from the bowl."""
    if a <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(scale, scale)
    fill = STEEL_L if metal else PLAST
    edge = STEEL_D if metal else PLAST_E
    ctx.push_group()
    # handle (along +x of the local frame)
    ctx.move_to(30, -7); ctx.line_to(330, -11); ctx.line_to(340, 0); ctx.line_to(330, 11); ctx.line_to(30, 7); ctx.close_path()
    fill_stroke(ctx, fill, lw=4)
    # bowl
    ctx.save(); ctx.scale(42, 26); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
    fill_stroke(ctx, fill, lw=4)
    ctx.save(); ctx.scale(30, 16); ctx.arc(-4 / 30, -3 / 16, 1, math.pi * 1.1, math.pi * 1.7); ctx.restore()
    setc(ctx, WHITE, 0.8); ctx.set_line_width(4); ctx.stroke()
    if metal:
        ctx.move_to(120, -4); ctx.line_to(300, -6); setc(ctx, WHITE, 0.7); ctx.set_line_width(3); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()

# ---------------------------------------------------------------- press
def crack_path(f):
    """Points of the crack, from the scratch (inside face of the left wall) across the front to the right wall."""
    rnd = random.Random(7)
    xs = [SX - 2]; ys = [SY]
    x = SX - 2
    while x < GR + 2:
        x += 22
        xs.append(min(x, GR + 2)); ys.append(SY + rnd.uniform(-14, 14))
    n = len(xs)
    k = max(2, int(round(f * (n - 1))) + 1)
    pts = list(zip(xs[:k], ys[:k]))
    if f < 0.05:
        pts = [(SX - 2, SY), (SX - 2 - W_G * 0.9 * clamp(f / 0.05) , SY + 3)]
    return pts

def press(ctx, t, s):
    p = s['press']
    # frame: base band + handle on the right
    ctx.rectangle(GL - 14, BOT - 70, GR - GL + 28, 74); fill_stroke(ctx, STEEL, lw=4)
    ctx.move_to(GR + 14, 820); ctx.curve_to(GR + 140, 820, GR + 140, 1220, GR + 14, 1220)
    ctx.line_to(GR + 14, 1170); ctx.curve_to(GR + 95, 1170, GR + 95, 870, GR + 14, 870); ctx.close_path()
    fill_stroke(ctx, STEEL_D, lw=4)
    ctx.rectangle(GR, 800, 22, 440); fill_stroke(ctx, STEEL, lw=3)
    # inside of the glass (light)
    ctx.rectangle(GL + W_G, RIM, GR - GL - 2 * W_G, BOT - RIM)
    setc(ctx, GLASS, 0.35); ctx.fill()
    # coffee
    if s['coffee'] > 0:
        ctx.rectangle(GL + W_G, LVL, GR - GL - 2 * W_G, BOT - LVL)
        g = cairo.LinearGradient(0, LVL, 0, BOT)
        g.add_color_stop_rgb(0, *COFFEE_L[:3]); g.add_color_stop_rgb(1, *COFFEE[:3])
        ctx.push_group(); ctx.set_source(g); ctx.fill()
        ctx.rectangle(GL + W_G, LVL, GR - GL - 2 * W_G, 10); setc(ctx, CREMA); ctx.fill()
        # grounds below the filter
        fy = F_TOP + (F_BOT - F_TOP) * p
        rnd = random.Random(3)
        for _ in range(160):
            gx = rnd.uniform(GL + W_G + 6, GR - W_G - 6)
            gy = rnd.uniform(max(fy + 12, BOT - 250 + 200 * p), BOT - 8)
            ctx.arc(gx, gy, rnd.uniform(2, 4.5), 0, 2 * math.pi)
        setc(ctx, hexc('#3a2414')); ctx.fill()
        ctx.pop_group_to_source(); ctx.paint_with_alpha(s['coffee'])
    # walls (glass), hot tint during the rinse
    wall_c = lerpc(GLASS, HOT, 0.65 * s['empty_hot'])
    for x in (GL, GR - W_G):
        ctx.rectangle(x, RIM, W_G, BOT - RIM); fill_stroke(ctx, wall_c, GLASS_E, lw=3)
    ctx.rectangle(GL, BOT - 6, GR - GL, 6); setc(ctx, GLASS_E); ctx.fill()
    for x in (GL + 4, GR - W_G + 4):
        ctx.move_to(x, RIM + 30); ctx.line_to(x, RIM + 260); setc(ctx, WHITE, 0.8); ctx.set_line_width(3); ctx.stroke()
    # plunger: rod, filter disc, lid, knob
    pa = s['plunger']
    if pa <= 0: return
    ctx.push_group()
    fy = F_TOP + (F_BOT - F_TOP) * p
    rod_top = fy - ROD
    ctx.rectangle(533, rod_top, 14, fy - rod_top); fill_stroke(ctx, STEEL, lw=3)
    if True:
        ctx.rectangle(GL + W_G + 2, fy - 8, GR - GL - 2 * W_G - 4, 16); fill_stroke(ctx, STEEL_L, lw=3)
        for k in range(14):
            x = GL + W_G + 16 + k * 25
            ctx.move_to(x, fy - 6); ctx.line_to(x, fy + 6)
        setc(ctx, STEEL_D); ctx.set_line_width(2); ctx.stroke()
    ctx.rectangle(GL - 18, LID_Y, GR - GL + 36, 42); fill_stroke(ctx, STEEL, lw=4)
    ctx.move_to(GL - 18, LID_Y + 40); ctx.line_to(GL - 46, LID_Y + 64); ctx.line_to(GL - 18, LID_Y + 64); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=3)
    kx = 540
    ctx.arc(kx, rod_top - 26, 34, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=4)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(pa)

def scratch_mark(ctx, t, a):
    """The scratch on the inside face of the left wall: a short red notch going INTO the wall (toward -x)."""
    if a <= 0: return
    ctx.move_to(SX + 1, SY - 9); ctx.line_to(SX - 9, SY); ctx.line_to(SX + 1, SY + 9)
    setc(ctx, RED, a); ctx.set_line_width(4); ctx.stroke()

def crack(ctx, t, f, a=1.0):
    if f <= 0 or a <= 0: return
    pts = crack_path(f)
    ctx.move_to(*pts[0])
    for q in pts[1:]: ctx.line_to(*q)
    setc(ctx, WHITE, a); ctx.set_line_width(8); ctx.stroke_preserve()
    setc(ctx, INK, a); ctx.set_line_width(3.5); ctx.stroke()

def spill(ctx, t, u, a):
    """Hot water jets out of the crack on both sides, drops fall, steam rises."""
    if a <= 0 or u <= 0: return
    for side in (-1, 1):
        x0 = GL - 2 if side < 0 else GR + 2
        L = 150 * u
        ctx.move_to(x0, SY)
        ctx.curve_to(x0 + side * L * 0.6, SY - 10, x0 + side * L, SY + 60 * u, x0 + side * L * 1.05, SY + 230 * u)
        setc(ctx, WATER, a); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        for k in range(5):
            ph = (t * 1.4 + k * 0.2) % 1.0
            dx = x0 + side * (L * 0.9 + 20 * k / 5)
            dy = SY + 120 * u + 260 * ph
            ctx.arc(dx, dy, 8, 0, 2 * math.pi); setc(ctx, WATER_L, a * (1 - ph)); ctx.fill()
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1.0
            wx = x0 + side * (40 + 30 * k)
            wavy_arrow(ctx, wx, SY - 20, wx, SY - 20 - 110 * (0.4 + ph), t + k, WHITE, a * (1 - ph) * 0.9, amp=7, wl=36, lw=5, head=0)
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)

def cold_rinse(ctx, t, a):
    if a <= 0: return
    lt = t - B(8)
    # stream falling DOWN into the open carafe
    top = LID_Y - 120
    ctx.move_to(520, top); ctx.line_to(520, BOT - 30)
    setc(ctx, WATER, a); ctx.set_line_width(22); ctx.stroke()
    for k in range(6):
        ph = (lt * 1.2 + k / 6) % 1.0
        ctx.arc(520 + 6 * math.sin(k), top + (BOT - top) * ph, 6, 0, 2 * math.pi); setc(ctx, WATER_L, a); ctx.fill()
    # inside faces turn cold (blue) and shrink: arrows along the inside face pointing toward each other
    c = sstep(t, B(8) + 1.2, 0.8)
    for x in (GL + W_G, GR - W_G):
        ctx.move_to(x, RIM + 20); ctx.line_to(x, BOT - 20); setc(ctx, WATER, a * c); ctx.set_line_width(7); ctx.stroke()
    for x in (GL + W_G + 22, GR - W_G - 22):
        for y0, y1 in ((SY - 160, SY - 40), (SY + 160, SY + 40)):
            straight_arrow(ctx, x, y0, x, y1, WATER, a * c, lw=5, head=10)

def push_arrows(ctx, t, a):
    """Coffee pushes OUTWARD on the walls while the plunger goes down."""
    if a <= 0: return
    for k, y in enumerate((900, 1010, 1120, 1230, 1330)):
        pul = 8 * math.sin(t * 6 + k)
        straight_arrow(ctx, 450, y, SX + 6 + pul * 0.3, y, RED, a, lw=6, head=12)
        straight_arrow(ctx, 630, y, GR - W_G - 6 - pul * 0.3, y, RED, a, lw=6, head=12)

def draw_set(ctx):
    pass

def CAM(t):
    return 540, 930, 1.0

def draw(ctx, t, E):
    s = state(t)
    press(ctx, t, s)
    scratch_mark(ctx, t, s['scratch'] * (1 - s['empty_hot'] * 0.0))
    crack(ctx, t, s['crack'], 1.0)
    cold_rinse(ctx, t, s['cold'])
    push_arrows(ctx, t, s['push'])
    spill(ctx, t, s['spill'], s['spill_a'])
    # metal spoon stirring, scraping the left wall (beats 1-2)
    a = s['metal']
    if a > 0:
        lt = t - B(1)
        yy = SY + 40 * math.sin(lt * 3.2)
        spoon(ctx, SX + 44, yy, -1.2, a, metal=True)
    # plastic spoon: the fix (beat 0, outside the press) and stirring at the end (beat 11)
    a = s['plastic_fix']
    if a > 0:
        pop = ease(clamp((t - 0.3) / 0.4))
        spoon(ctx, 935, 1150, -1.62, a, metal=False, scale=0.55 + 0.35 * pop)
    a = s['plastic_stir']
    if a > 0:
        lt = t - B(11)
        yy = SY + 40 * math.sin(lt * 3.2)
        spoon(ctx, SX + 44, yy, -1.2, a, metal=False)
    overlays(ctx, t, s)

def stamp(ctx, text, x, y, a, size=64, ang=-0.18, col=RED):
    if a <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    font(ctx, size, True); w = spaced_width(ctx, text, 3) + 50
    rrect(ctx, -w / 2, -size * 0.75, w, size * 1.5, 10)
    setc(ctx, CREAM, 0.85 * a); ctx.fill_preserve()
    setc(ctx, col, a); ctx.set_line_width(7); ctx.stroke()
    text_c(ctx, text, 0, size * 0.36, size, col, True, 3, a)
    ctx.restore()

def overlays(ctx, t, s):
    a = s['recall']
    if a > 0:
        sa = a * sstep(t, 0.15, 0.3)
        stamp(ctx, "RECALLED", 540, 900, sa)
        tag(ctx, "5.9 MILLION", 540, 1030, RED, a * sstep(t, 0.6, 0.3), 34)
    a = s['plastic_fix']
    if a > 0:
        tag(ctx, "THE FIX", 930, 1300, GREEN, a * sstep(t, 1.0, 0.3), 30)
    a = bw(t, 1)
    if a > 0:
        tag(ctx, "WHERE IT BREAKS", 540, 1450, RED, a, 28)
    a = s['scr_hi']
    if a > 0:
        highlight(ctx, SX - 4, SY, 46, 46, RED, a * s['scratch'], t)
        if t > B(3):
            tag(ctx, "SCRATCH · INSIDE FACE", 300, 1270, RED, a, 26)
            straight_arrow(ctx, 260, 1240, SX - 18, SY + 22, RED, a, lw=4, head=10)
    a = s['push']
    if a > 0:
        tag(ctx, "PUSHES OUTWARD", 540, 1450, RED, a, 28)
    a = bw(t, 7)
    if a > 0:
        highlight(ctx, SX - 4, SY, 60, 46, RED, a, t)
        tag(ctx, "CRACK GROWS", 300, 1270, RED, a, 28)
    a = s['cold']
    if a > 0:
        tag(ctx, "HOT GLASS", 230, 760, HOT, a, 26)
        tag(ctx, "COLD WATER", 770, 520, WATER, a * sstep(t, B(8) + 0.3), 26)
        tag(ctx, "INSIDE SHRINKS", 540, 1450, WATER, a * sstep(t, B(8) + 1.4), 28)
    a = s['spill_a']
    if a > 0:
        tag(ctx, "93 °C · 200 °F", 540, 1450, RED, a * sstep(t, B(9) + 2.0), 32)
    a = bw(t, 11)
    if a > 0:
        tag(ctx, "NO SCRATCH", 300, 1270, GREEN, a * sstep(t, B(11) + 0.8), 28)

# ---------------------------------------------------------------- force lines (cross-section of the wall)
def force_lines(ctx, t, a, x0, x1, ys, T, notch, xc, D, hw, n=9, w=None, lw=4, col=TEAL):
    """Lines along a glass slab (inside face at ys on TOP, thickness T). With a notch of depth D at xc,
    the lines dip under its tip and crowd just below it."""
    w = w or hw * 1.6
    for i in range(n):
        u = (i + 0.6) / (n + 0.2)
        pts = []
        for k in range(121):
            x = x0 + (x1 - x0) * k / 120
            g = math.exp(-((x - xc) / w) ** 2) * notch
            dn = D / T
            u2 = dn + (1 - dn) * (u ** 1.7)       # crowd near the tip
            uu = u + (u2 - u) * g
            pts.append((x, ys + T * uu))
        ctx.move_to(*pts[0])
        for q in pts[1:]: ctx.line_to(*q)
        setc(ctx, col, a); ctx.set_line_width(lw); ctx.stroke()

def slab(ctx, a, x0, x1, ys, T, notch, xc, D, hw):
    ctx.move_to(x0, ys)
    if notch > 0:
        d = D * notch
        ctx.line_to(xc - hw, ys); ctx.line_to(xc, ys + d); ctx.line_to(xc + hw, ys)
    ctx.line_to(x1, ys); ctx.line_to(x1, ys + T); ctx.line_to(x0, ys + T); ctx.close_path()
    fill_stroke(ctx, GLASS, GLASS_E, lw=4, alpha=a)

def _panel(ctx, a, x=60, y=180, w=960, h=330):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def flow_panel(ctx, t, a):
    _panel(ctx, a)
    x0, x1, ys, T = 200, 880, 270, 150
    xc, D, hw = 540, 80, 22
    nt = sstep(t, B(5) + 2.6, 0.8)
    slab(ctx, a, x0, x1, ys, T, nt, xc, D, hw)
    force_lines(ctx, t, a, x0 + 6, x1 - 6, ys, T, nt, xc, D, hw)
    straight_arrow(ctx, x0 - 10, ys + T / 2, x0 - 110, ys + T / 2, RED, a, lw=8, head=16)
    straight_arrow(ctx, x1 + 10, ys + T / 2, x1 + 110, ys + T / 2, RED, a, lw=8, head=16)
    text_c(ctx, "INSIDE", 200, 250, 20, INK, True, 1, a)
    text_c(ctx, "OUTSIDE", 210, 448, 20, INK, True, 1, a)
    text_c(ctx, "PULL", 110, 320, 22, RED, True, 1, a)
    text_c(ctx, "PULL", 970, 320, 22, RED, True, 1, a)
    if nt > 0.5:
        text_c(ctx, "SCRATCH", xc + 110, ys - 8, 22, RED, True, 1, a * nt)
    text_c(ctx, "THE WALL, CUT OPEN", 540, 488, 26, INK, True, 2, a)

def card_tip(ctx, t, lt, a):
    card_frame(ctx, "AT THE TIP · ZOOMED IN", a, "THE PULL PILES UP HERE", RED)
    x0, x1, ys, T = 130, 950, 262, 270
    xc, D, hw = 540, 150, 34
    slab(ctx, a, x0, x1, ys, T, 1.0, xc, D, hw)
    force_lines(ctx, t, a, x0 + 6, x1 - 6, ys, T, 1.0, xc, D, hw, n=11, w=170, lw=4)
    p = 0.5 + 0.5 * math.sin(lt * 6)
    gl = cairo.RadialGradient(xc, ys + D, 2, xc, ys + D, 60)
    gl.add_color_stop_rgba(0, *RED[:3], 0.7 * a); gl.add_color_stop_rgba(1, *RED[:3], 0)
    ctx.arc(xc, ys + D, 60 + 8 * p, 0, 2 * math.pi); ctx.set_source(gl); ctx.fill()
    tag(ctx, "TIP", xc + 150, ys + D - 50, RED, a, 24)
    text_c(ctx, "INSIDE", 190, 250, 18, INK, True, 1, a)

def card_scrape(ctx, t, lt, a):
    """Looking straight at the inside face of the glass: the spoon edge slides left -> right and leaves a fine line."""
    card_frame(ctx, "INSIDE THE GLASS · ZOOMED IN", a, "THE EDGE LEAVES A LINE", RED)
    ctx.rectangle(130, 260, 820, 270); fill_stroke(ctx, GLASS, GLASS_E, lw=4, alpha=a)
    for k in range(4):
        ctx.move_to(170 + k * 210, 280); ctx.line_to(230 + k * 210, 500); setc(ctx, WHITE, 0.5 * a); ctx.set_line_width(3); ctx.stroke()
    m = ease(clamp((lt - 0.4) / 2.6))
    ex = 200 + 650 * m
    ctx.move_to(200, 400)
    rnd = random.Random(5)
    x = 200
    while x < ex:
        x = min(ex, x + 18); ctx.line_to(x, 400 + rnd.uniform(-2.5, 2.5))
    setc(ctx, WHITE, a); ctx.set_line_width(5); ctx.stroke_preserve()
    setc(ctx, RED, a); ctx.set_line_width(2); ctx.stroke()
    # spoon edge (seen edge-on) pressing on the face
    ctx.save(); ctx.translate(ex, 400); ctx.rotate(-0.5); ctx.scale(0.7, 0.7)
    ctx.move_to(-10, 0); ctx.curve_to(-30, -60, 30, -150, 120, -200); ctx.line_to(140, -180)
    ctx.curve_to(60, -130, 20, -60, 10, 0); ctx.close_path()
    fill_stroke(ctx, STEEL_L, STEEL_D, lw=4, alpha=a)
    ctx.restore()
    straight_arrow(ctx, ex + 40, 470, ex + 120, 470, INK, a * (1 - m), lw=5, head=10)

def recall_panel(ctx, t, a):
    _panel(ctx, a, y=185, h=230)
    text_c(ctx, "70 BREAKS · 48 BURNS", 540, 270, 54, RED, True, 3, a)
    text_c(ctx, "FREE FIX: A PLASTIC SPOON", 540, 345, 38, GREEN, True, 2, a * sstep(t, B(10) + 2.4))
    text_c(ctx, "CPSC RECALL · OCT 2026", 540, 393, 22, INK, True, 2, a)

def recap_panel(ctx, t, a):
    _panel(ctx, a, y=185, h=190)
    text_c(ctx, "NO SCRATCH = NO CRACK", 540, 265, 54, INK, True, 3, a)
    text_c(ctx, "PLASTIC IS SOFTER THAN GLASS", 540, 335, 32, GREEN, True, 2, a)

def draw_hud(ctx, t, E):
    a = win(t, B(5) + 0.2, B(6), 0.3)
    if a > 0: flow_panel(ctx, t, a)
    a = win(t, B(10) + 0.3, B(11), 0.3)
    if a > 0: recall_panel(ctx, t, a)
    a = win(t, B(11) + 0.4, B(12) + 2, 0.3)
    if a > 0: recap_panel(ctx, t, a)

SFX = [(0.2, 'click'), (0.6, 'pop'), (1.0, 'pop'), (B(1) + 0.3, 'pop'), (B(3) + 0.3, 'pop'),
       (B(4) + 0.3, 'click'), (B(5) + 0.3, 'pop'), (B(7) + 0.3, 'pop'), (B(8) + 0.3, 'pop'),
       (B(9) + 0.3, 'pop'), (B(10) + 0.4, 'pop'), (B(11) + 0.4, 'pop')]
HUM = []

CARDS = {'scrape': card_scrape, 'tip': card_tip}
