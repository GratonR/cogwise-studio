"""Cogwise episode: Your kettle goes quiet right before it boils.
One idea: the roar is steam bubbles collapsing. They are born on the hot element at the bottom, rise into water
that is still below 100 C, condense and implode with a tiny crack. Once the whole column is at 100 C they survive
to the surface and pop softly: the cracking stops, the noise drops, the rolling boil begins.

VIEW (screen coordinates, y grows DOWN): one kettle in vertical section.
  - Element (coil) at the BOTTOM of the water (y ~1330). Water surface at y = SURF (680).
  - Hot water = ORANGE, BELOW the boundary y = yb(t); cold water (< 100 C) = BLUE, ABOVE it (y < yb).
  - Bubbles are born on the element and RISE (y decreases). A bubble that crosses ABOVE yb (into blue water)
    collapses: shrinks + crack star + small sound ring. When yb reaches the surface, bubbles pop AT the surface.
  - Noise meter (bar, left = quiet, right = loud) at the top of the stage, y ~ 360.
  - Spout on the LEFT, handle on the RIGHT, power base below.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="kettle-quiet",
    title="Your kettle goes quiet right before it boils 🫖 #Shorts",
    description=("That roar isn't boiling. It's thousands of steam bubbles collapsing in water that's still too cold.\n\n"
                 "#Shorts #howthingswork #kettle #physics #cogwise"),
    hashtags=["Shorts", "howthingswork", "kettle", "physics", "cogwise"],
    sources=[
        "https://www.thenakedscientists.com/articles/questions/why-water-loudest-just-it-boils",
        "https://www.scienceabc.com/nature/why-is-water-loudest-just-before-it-boils.html",
        "https://thenakedscientists.com/articles/questions/why-does-kettle-get-louder-water-heats-then-quieter-it-reaches-boiling-point",
        "https://archive.imascientist.org.uk/laserj12-zone/question/why-does-a-kettle-get-quieter-before-boiling/index.html",
    ],
)

BEATS = [
    dict(dur=5.4, title="QUIET?", caption="Your kettle goes quiet right before it boils. That's your signal it's almost ready."),
    dict(dur=4.6, title="THE SECRET", caption="That loud roar isn't boiling. It's thousands of tiny bubbles collapsing."),
    dict(dur=5.0, title="1 · THE ELEMENT", caption="The heating element sits at the bottom, so the bottom water heats first."),
    dict(dur=5.0, title="STEAM BUBBLES", caption="Right on the hot metal, water flashes into tiny bubbles of steam."),
    dict(dur=6.0, title="COLD TOP", caption="But the water higher up is still below one hundred Celsius, two hundred twelve Fahrenheit."),
    dict(dur=5.6, title="2 · THE COLLAPSE", caption="As a bubble rises into that cooler water, its steam turns back into liquid."),
    dict(dur=6.0, title=None, caption="The bubble vanishes in a split second, and the water slams shut with a tiny crack.", card='crack'),
    dict(dur=4.8, title="THE ROAR", caption="Thousands of those cracks every second make the roar you hear."),
    dict(dur=5.2, title="3 · HOT ALL THE WAY", caption="Then the heat spreads, until the whole kettle reaches one hundred Celsius."),
    dict(dur=6.0, title="NO MORE CRACKS", caption="Now nothing cools the bubbles. They rise all the way up and pop softly at the top."),
    dict(dur=5.0, title="THE HUSH", caption="The cracking stops, the noise drops, and the rolling boil begins."),
    dict(dur=5.8, title="LOUD = HEATING", caption="So a loud kettle is still heating. A quiet one is hot all the way up."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3): return ease(clamp((t - t0) / d))

STEEL = hexc('#b9c1c8'); STEEL_D = hexc('#7f8a94')
COLDW = hexc('#8fc6e6'); HOTW = hexc('#f4b26a')
STEAM = hexc('#fbf6ea')
BASE = hexc('#3d3a36')

# ---------------------------------------------------------------- geometry
SURF = 680                     # water surface
Y_TOP, Y_BOT = 560, 1400       # kettle body (outer)
XL_T, XR_T = 345, 735          # outer edges at the top
XL_B, XR_B = 255, 825          # outer edges at the bottom
WT = 22                        # wall thickness (drawn)
EL_Y = 1335                    # element (coil) centre line
EL_X0, EL_X1 = 320, 760

def wall_x(side, y):
    u = (y - Y_TOP) / (Y_BOT - Y_TOP)
    return lerp(XL_T, XL_B, u) if side < 0 else lerp(XR_T, XR_B, u)

def inner(side, y): return wall_x(side, y) - side * WT

# ---------------------------------------------------------------- state over time
def yb(t):
    """Hot/cold boundary: water BELOW this y is at 100 C (orange), above is cooler (blue)."""
    if t < B(1):                                   # preview: heat fills the kettle in the first 2 s
        return lerp(1060, SURF - 10, sstep(t, 0.5, 1.6))
    if t < B(2):                                   # back to the noisy state
        return lerp(SURF - 10, 1060, sstep(t, B(1), 0.6))
    if t < B(8):                                   # the story from the start: bottom heats first
        y = lerp(1060, EL_Y + 40, sstep(t, B(2), 0.5))
        y = lerp(y, 1240, sstep(t, B(2) + 1.2, 3.0))
        y = lerp(y, 1110, sstep(t, B(4) + 0.4, 3.5))
        return y
    return lerp(1110, SURF - 10, sstep(t, B(8) + 0.5, 3.8))   # beat 9: hot all the way

def emission(t):
    """Bubbles per second from the element."""
    if t < B(1): return 26
    if t < B(2): return 26
    if t < B(3) + 0.4: return 0
    if t < B(7): return lerp(6, 22, sstep(t, B(3) + 0.4, 6.0))
    return 30

def heating(t):
    return 0.0 if B(2) - 0.05 < t < B(2) + 0.6 else 1.0

NOISE_KEYS = [(0, 0.85), (0.9, 0.85), (2.2, 0.22), (B(1), 0.22), (B(1) + 0.6, 0.85), (B(2), 0.85),
              (B(2) + 0.6, 0.04), (B(3) + 0.8, 0.06), (B(4) + 0.4, 0.38), (B(5), 0.5), (B(7), 0.62),
              (B(7) + 1.2, 0.96), (B(8) + 2.2, 0.96), (B(9) + 0.6, 0.45), (B(10) + 0.6, 0.18), (99, 0.18)]
def noise(t):
    k = NOISE_KEYS
    for i in range(1, len(k)):
        if t < k[i][0]:
            u = ease((t - k[i-1][0]) / (k[i][0] - k[i-1][0]))
            v = lerp(k[i-1][1], k[i][1], u)
            break
    else:
        v = k[-1][1]
    return clamp(v + 0.04 * v * math.sin(t * 23) * math.sin(t * 7.3))

# ---------------------------------------------------------------- bubbles
_r = random.Random(7)
SLOTS = [(_r.uniform(0, 1), _r.uniform(0, 1), _r.uniform(0, 1)) for _ in range(4000)]
RISE = 330.0                   # px / s (stylised)

def bubble_list(t):
    """Yield (x, y, r, state, age) for live bubbles. state: 'rise' | 'pop' (surface) | 'crack' (collapse)."""
    out = []
    # integrate emission backwards over the last 3 s with a fixed slot grid
    dt = 1 / 32.0
    i0 = int((t - 3.0) / dt)
    for i in range(max(i0, 0), int(t / dt) + 1):
        tb = i * dt
        if tb > t: break
        p_emit = emission(tb) * dt
        u, ux, us = SLOTS[i % len(SLOTS)]
        if u > p_emit: continue
        x = lerp(EL_X0 + 20, EL_X1 - 20, ux) + 14 * math.sin(tb * 3)
        speed = RISE * (0.8 + 0.5 * us)
        r0 = 7 + 6 * us
        # walk the path to find where it ends
        tau, y, ended = tb, EL_Y - 16, None
        while tau < t:
            tau2 = min(t, tau + 0.04)
            y -= speed * (tau2 - tau); tau = tau2
            if y < yb(tau) - 4 and y > SURF + 10:
                ended = ('crack', tau, y); break
            if y <= SURF + 10:
                ended = ('pop', tau, SURF + 10); break
        life = tau - tb
        r = r0 * (1 + 0.6 * clamp(life / 1.5))
        if ended is None:
            out.append((x, y, r, 'rise', 0.0))
        else:
            kind, te, ye = ended
            age = t - te
            if age < 0.35:
                out.append((x + 6 * math.sin(te * 9), ye, r, kind, age))
    return out

def draw_bubble(ctx, x, y, r, st, age, a=1.0):
    if st == 'rise':
        ctx.arc(x, y, r, 0, 6.28); setc(ctx, STEAM, 0.9 * a); ctx.fill_preserve()
        setc(ctx, INK, 0.8 * a); ctx.set_line_width(2.5); ctx.stroke()
        ctx.arc(x - r * 0.35, y - r * 0.35, r * 0.25, 0, 6.28); setc(ctx, WHITE, a); ctx.fill()
    elif st == 'crack':
        k = age / 0.35
        rr = r * (1 - ease(clamp(k * 2.5)))
        if rr > 0.5:
            ctx.arc(x, y, rr, 0, 6.28); setc(ctx, STEAM, a); ctx.fill_preserve()
            setc(ctx, INK, a); ctx.set_line_width(2); ctx.stroke()
        s = 6 + 16 * ease(k)
        for j in range(6):
            an = j * math.pi / 3 + 0.3
            ctx.move_to(x + math.cos(an) * s * 0.35, y + math.sin(an) * s * 0.35)
            ctx.line_to(x + math.cos(an) * s, y + math.sin(an) * s)
        setc(ctx, RED, a * (1 - k)); ctx.set_line_width(3.5); ctx.stroke()
        ctx.arc(x, y, 8 + 34 * k, 0, 6.28); setc(ctx, INK, 0.5 * a * (1 - k)); ctx.set_line_width(2); ctx.stroke()
    else:  # pop at the surface: soft ring
        k = age / 0.35
        ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.35)
        ctx.arc(0, 0, r + 20 * k, 0, 6.28); ctx.restore()
        setc(ctx, INK2, 0.6 * a * (1 - k)); ctx.set_line_width(2.5); ctx.stroke()

# ---------------------------------------------------------------- drawing
def water_path(ctx, y0, y1):
    ctx.move_to(inner(-1, y0), y0); ctx.line_to(inner(1, y0), y0)
    ctx.line_to(inner(1, y1), y1); ctx.line_to(inner(-1, y1), y1); ctx.close_path()

def kettle(ctx, t):
    # power base
    rrect(ctx, 210, Y_BOT + 8, 660, 62, 18); fill_stroke(ctx, BASE, lw=4)
    ctx.arc(780, Y_BOT + 39, 9, 0, 6.28); setc(ctx, RED if heating(t) > 0.5 else INK2); ctx.fill()
    # handle (right)
    ctx.new_path(); ctx.move_to(XR_T - 10, 640); ctx.curve_to(960, 600, 990, 1160, wall_x(1, 1210) - 6, 1210)
    setc(ctx, INK); ctx.set_line_width(46); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke_preserve()
    setc(ctx, BASE); ctx.set_line_width(36); ctx.stroke()
    # spout (left), drawn as a sectioned tube opening up-left
    ctx.move_to(wall_x(-1, 900), 900); ctx.line_to(170, 640); ctx.line_to(215, 610); ctx.line_to(wall_x(-1, 760) + 4, 760)
    ctx.close_path(); fill_stroke(ctx, STEEL, lw=4)
    # water: hot (below yb) orange, cold (above) blue, soft gradient band
    y_b = yb(t)
    ctx.save(); water_path(ctx, SURF, Y_BOT - WT); ctx.clip()
    ctx.rectangle(0, SURF, 1080, 900); setc(ctx, COLDW); ctx.fill()
    g = cairo.LinearGradient(0, y_b - 70, 0, y_b + 70)
    g.add_color_stop_rgba(0, *COLDW[:3], 1); g.add_color_stop_rgba(1, *HOTW[:3], 1)
    ctx.rectangle(0, y_b - 70, 1080, 140); ctx.set_source(g); ctx.fill()
    ctx.rectangle(0, y_b + 70, 1080, 1000); setc(ctx, HOTW); ctx.fill()
    # heat rising from the element
    h = heating(t) * (0.55 if t >= B(2) else 0.0) * (1 - bw(t, 6) * 0.6)
    if h > 0:
        for i, x in enumerate((380, 540, 700)):
            wavy_arrow(ctx, x, EL_Y - 40, x, EL_Y - 200, t + i, ORANGE, h * bw(t, 2, 5), amp=8, wl=36, lw=5, head=12)
    # bubbles
    for (x, y, r, st, age) in bubble_list(t):
        draw_bubble(ctx, x, y, r, st, age)
    ctx.restore()
    # surface line
    ctx.move_to(inner(-1, SURF), SURF); ctx.line_to(inner(1, SURF), SURF)
    setc(ctx, hexc('#4f90b8')); ctx.set_line_width(5); ctx.stroke()
    # element coil at the bottom
    glow = heating(t)
    ctx.new_path()
    n = 9
    for i in range(n * 16 + 1):
        u = i / (n * 16)
        x = lerp(EL_X0, EL_X1, u)
        y = EL_Y + 14 * math.sin(u * n * 2 * math.pi)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    setc(ctx, INK); ctx.set_line_width(20); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke_preserve()
    setc(ctx, lerpc(STEEL_D, RED, glow)); ctx.set_line_width(12); ctx.stroke()
    # walls (section): left & right bands + bottom
    for side in (-1, 1):
        ctx.move_to(wall_x(side, Y_TOP), Y_TOP); ctx.line_to(wall_x(side, Y_BOT), Y_BOT)
        ctx.line_to(inner(side, Y_BOT), Y_BOT); ctx.line_to(inner(side, Y_TOP), Y_TOP); ctx.close_path()
        fill_stroke(ctx, STEEL, lw=4)
    ctx.rectangle(XL_B, Y_BOT - WT, XR_B - XL_B, WT); fill_stroke(ctx, STEEL, lw=4)
    # lid
    ctx.move_to(XL_T - 12, Y_TOP); ctx.curve_to(420, 470, 660, 470, XR_T + 12, Y_TOP); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=4)
    rrect(ctx, 505, 468, 70, 30, 10); fill_stroke(ctx, BASE, lw=4)

def meter(ctx, t, a=1.0):
    if a <= 0: return
    x0, x1, y, h = 270, 870, 360, 34
    text_c(ctx, "NOISE", 190, y + 12, 28, INK, True, 2, a)
    rrect(ctx, x0, y - h / 2, x1 - x0, h, h / 2); fill_stroke(ctx, CREAM, lw=4, alpha=a)
    v = noise(t)
    if v > 0.01:
        col = lerpc(TEAL, RED, clamp((v - 0.3) / 0.6))
        rrect(ctx, x0 + 5, y - h / 2 + 5, (x1 - x0 - 10) * v, h - 10, (h - 10) / 2); setc(ctx, col, a); ctx.fill()
    text_c(ctx, "QUIET", x0 + 40, y + 52, 20, INK2, True, 2, a)
    text_c(ctx, "LOUD", x1 - 34, y + 52, 20, INK2, True, 2, a)

def labels(ctx, t):
    y_b = yb(t)
    # beat 1: preview
    a = sstep(t, 0.3, 0.3) * (1 - sstep(t, 1.6, 0.3))
    tag(ctx, "CRACKLING", 540, 1000, RED, a, 30)
    a = sstep(t, 2.4, 0.3) * (1 - sstep(t, B(1) - 0.2, 0.3))
    tag(ctx, "QUIET = ALMOST BOILING", 540, 1000, TEAL, a, 30)
    # beat 2: collapsing bubbles
    a = bw(t, 1) * sstep(t, B(1) + 0.9, 0.3)
    tag(ctx, "BUBBLES COLLAPSING", 540, 1000, RED, a, 30)
    # beat 3: element
    a = bw(t, 2) * sstep(t, B(2) + 0.6, 0.3)
    highlight(ctx, 540, EL_Y, 260, 46, RED, a, t)
    tag(ctx, "1 · HEATING ELEMENT", 540, EL_Y - 110, RED, a, 28)
    # beat 4: steam bubbles
    a = bw(t, 3) * sstep(t, B(3) + 1.0, 0.3)
    tag(ctx, "STEAM", 540, EL_Y - 110, INK, a, 30)
    # beat 5: temperatures
    a = bw(t, 4) * sstep(t, B(4) + 0.5, 0.3)
    tag(ctx, "BELOW 100 °C · 212 °F", 540, 850, TEAL, a, 30)
    tag(ctx, "100 °C · 212 °F", 540, min(y_b + 110, 1250), ORANGE, bw(t, 4) * sstep(t, B(4) + 1.6, 0.3), 26)
    # beat 8: roar
    a = bw(t, 7) * sstep(t, B(7) + 0.5, 0.3)
    tag(ctx, "THOUSANDS PER SECOND", 540, 850, RED, a, 28)
    # beat 9: hot all the way
    a = bw(t, 8) * sstep(t, B(8) + 0.4, 0.3)
    tag(ctx, "3 · HEAT SPREADS UP", 540, 850, ORANGE, a * (1 - sstep(t, B(8) + 3.6, 0.3)), 28)
    tag(ctx, "100 °C TOP TO BOTTOM", 540, 850, ORANGE, bw(t, 8) * sstep(t, B(8) + 3.9, 0.3), 28)
    # beat 10: soft pops
    a = bw(t, 9) * sstep(t, B(9) + 1.6, 0.3)
    tag(ctx, "POP · SOFTLY", 540, 620, INK, a, 28)
    # beat 11: hush
    a = bw(t, 10) * sstep(t, B(10) + 0.8, 0.3)
    tag(ctx, "NO CRACKS", 540, 1000, TEAL, a, 30)
    # beat 12: recap
    a = sstep(t, B(11) + 0.3, 0.3)
    tag(ctx, "LOUD = STILL HEATING", 540, 1000, RED, a * (1 - sstep(t, B(11) + 2.7, 0.3)), 30)
    tag(ctx, "QUIET = HOT ALL THE WAY", 540, 1000, TEAL, sstep(t, B(11) + 3.0, 0.3), 30)

# hero bubble (beat 6): one bubble rises slowly from the element into the blue water and shrinks
HX = 540
def hero(ctx, t):
    a = bw(t, 5)
    if a <= 0: return
    lt = t - B(5)
    y_b = yb(t)
    y = lerp(EL_Y - 30, y_b - 170, ease(clamp(lt / 3.2)))
    r = 30 * (1 - 0.75 * sstep(lt, 2.6, 2.0))
    ctx.arc(HX, y, r, 0, 6.28); setc(ctx, STEAM, a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(HX - r * 0.35, y - r * 0.35, r * 0.25, 0, 6.28); setc(ctx, WHITE, a); ctx.fill()
    k = a * sstep(lt, 2.4, 0.4)
    for j in range(5):                      # condensing droplets on the bubble wall
        an = j * 1.25 + lt
        ctx.arc(HX + math.cos(an) * (r + 10), y + math.sin(an) * (r + 10), 4, 0, 6.28); setc(ctx, hexc('#3a78a8'), k); ctx.fill()

def hero_tags(ctx, t):
    a = bw(t, 5)
    if a <= 0: return
    tag(ctx, "2 · STEAM TURNS TO WATER", 540, 520, TEAL, a * sstep(t, B(5) + 2.4, 0.3), 30)
    tag(ctx, "STEAM BUBBLE", 540, 520, INK, a * sstep(t, B(5) + 0.4, 0.3) * (1 - sstep(t, B(5) + 2.2, 0.2)), 30)

# ---------------------------------------------------------------- assembly
def draw_set(ctx):
    pass

def draw(ctx, t, E):
    meter(ctx, t, 1 - win(t, B(6) - 0.3, B(7) + 0.1, 0.3))
    kettle(ctx, t)
    hero(ctx, t)
    labels(ctx, t)

CAM_KEYS = [(0, 540, 900, 1.0), (B(5) + 0.1, 540, 1080, 1.6), (B(6) - 0.2, 540, 900, 1.0)]
def CAM(t):
    return cam_track(CAM_KEYS, t, 0.8)

def draw_hud(ctx, t, E):
    hero_tags(ctx, t)

# ---------------------------------------------------------------- card
def card_crack(ctx, t, lt, a):
    card_frame(ctx, "ONE BUBBLE, ONE CRACK", a, "COLLAPSE = CRACK", RED)
    ctx.rectangle(130, 260, 820, 270); setc(ctx, COLDW, a); ctx.fill()
    cx, cy = 540, 395
    k = ease(clamp((lt - 0.5) / 1.6))                     # shrink
    r = 95 * (1 - k)
    if r > 1:
        ctx.arc(cx, cy, r, 0, 6.28); setc(ctx, STEAM, a); ctx.fill_preserve()
        setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        text_c(ctx, "STEAM", cx, cy + 10, 26 * max(r / 95, 0.4), INK2, True, 1, a * (1 - k))
    # water rushing inward (arrows point TO the centre)
    ka = a * sstep(lt, 0.6, 0.3) * (1 - sstep(lt, 2.2, 0.2))
    for j in range(8):
        an = j * math.pi / 4
        r0, r1 = max(r, 10) + 70, max(r, 10) + 12
        straight_arrow(ctx, cx + math.cos(an) * r0, cy + math.sin(an) * r0 * 0.95,
                       cx + math.cos(an) * r1, cy + math.sin(an) * r1 * 0.95, hexc('#2f6fa0'), ka, lw=5, head=10)
    text_c(ctx, "WATER", 230, 300, 24, hexc('#2f6fa0'), True, 2, a * sstep(lt, 0.6, 0.3))
    # crack + sound rings
    c = sstep(lt, 2.1, 0.15)
    if c > 0:
        s = 26 + 30 * ease(clamp((lt - 2.1) / 0.4))
        for j in range(8):
            an = j * math.pi / 4 + 0.2
            ctx.move_to(cx + math.cos(an) * s * 0.3, cy + math.sin(an) * s * 0.3)
            ctx.line_to(cx + math.cos(an) * s, cy + math.sin(an) * s)
        setc(ctx, RED, a * c); ctx.set_line_width(6); ctx.stroke()
        for j in range(3):
            rr = ((lt - 2.1) * 160 + j * 60) % 180 + 40
            ctx.arc(cx, cy, rr, 0, 6.28); setc(ctx, INK, a * c * (1 - rr / 220) * 0.7); ctx.set_line_width(3); ctx.stroke()
        text_c(ctx, "CRACK!", 830, 330, 34, RED, True, 2, a * c)

CARDS = {'crack': card_crack}

SFX = [(0.3, 'pop'), (2.4, 'pop'), (B(1) + 0.9, 'pop'), (B(2) + 0.6, 'click'), (B(3) + 1.0, 'pop'),
       (B(4) + 0.5, 'pop'), (B(5) + 0.4, 'pop'), (B(5) + 2.4, 'pop'), (B(7) + 0.5, 'pop'),
       (B(8) + 0.4, 'pop'), (B(9) + 1.6, 'pop'), (B(10) + 0.8, 'pop'), (B(11) + 0.3, 'pop'), (B(11) + 3.0, 'pop')]
HUM = []
