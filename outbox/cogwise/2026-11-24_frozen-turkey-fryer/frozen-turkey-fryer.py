"""Cogwise episode: A frozen turkey can turn a fryer into a fireball.
One idea: the fire starts with the hidden ICE, not the oil. Frying oil (~180 C / 350 F) is almost twice the boiling
point of water. Ice touching it melts and flashes to steam (~1,700 x its volume). The steam forms UNDER the oil and
lifts it like a piston: the oil foams over the rim, runs DOWN the outside of the pot onto the burner flame, ignites.

VIEW (screen coordinates, y grows DOWN): one stockpot in vertical section on an outdoor propane burner stand.
  - Pot rim at y = RIM (720), inner bottom at y = 1270. Burner ring BELOW the pot (y ~1345); its flames point UP
    (tips at smaller y), under the pot bottom.
  - Turkey hangs ABOVE the pot on a lifting rod (centre y 560), legs up, then is LOWERED (y increases) into the oil.
  - Turkey drawn in section: skin, dark cavity in the middle holding ice crystals; frost specks on the skin.
  - Steam bubbles are born on the turkey (where the ice is) and RISE (y decreases) to the oil surface.
  - Oil level y = oil_y(t) RISES (y decreases) as steam pushes up, reaches the rim, spills OVER the rim and runs
    DOWN (y increases) along the OUTSIDE of both walls to the burner. Fire flames grow UPWARD from the burner.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="frozen-turkey-fryer",
    title="A frozen turkey can turn a fryer into a fireball 🦃 #Shorts",
    description=("The fire doesn't start with the oil. It starts with the ice hidden inside the bird.\n\n"
                 "#Shorts #howthingswork #thanksgiving #turkeyfryer #physics"),
    hashtags=["Shorts", "howthingswork", "thanksgiving", "turkeyfryer", "physics"],
    sources=[
        "https://www.scientificamerican.com/article/why-frozen-turkeys-explode-when-deep-fried/",
        "https://www.pbs.org/newshour/science/why-do-frozen-turkeys-explode-when-deep-fried",
        "https://cpsc.gov/Newsroom/News-Releases/2026/Put-Safety-on-the-Menu-Consumer-Product-Safety-Commission-Offers-Safe-Cooking-Tips-for-a-Joyful-Holiday-Season",
        "https://www.cpsc.gov/Newsroom/News-Releases/2004/CPSC-Issues-Safety-Tips-for-Turkey-Fryers",
    ],
)

BEATS = [
    dict(dur=5.6, title="STILL FROZEN", caption="This turkey is still frozen. Drop it in hot oil, and the pot erupts."),
    dict(dur=5.0, title="THE SECRET", caption="The fire doesn't start with the oil. It starts with hidden ice."),
    dict(dur=5.6, title="1 · THE OIL", caption="Frying oil runs at about one hundred eighty Celsius, three hundred fifty Fahrenheit."),
    dict(dur=5.4, title="TWICE AS HOT", caption="Water boils at one hundred Celsius. That oil is almost twice as hot."),
    dict(dur=5.4, title="2 · THE ICE", caption="A frozen turkey hides ice in its skin and deep inside its cavity."),
    dict(dur=5.2, title="FLASH TO STEAM", caption="When that ice hits the oil, it melts and boils almost instantly."),
    dict(dur=5.0, title=None, caption="One cup of water makes about seventeen hundred cups of steam.", card='expand'),
    dict(dur=5.6, title="3 · THE PISTON", caption="All that steam forms under the oil and has to push its way up."),
    dict(dur=5.6, title="OVERFLOW", caption="The bubbles lift the oil like a piston, and it foams over the rim."),
    dict(dur=5.2, title="ON THE FLAME", caption="Hot oil runs down the sides, straight onto the burner's open flame."),
    dict(dur=4.8, title="FIREBALL", caption="It ignites, and a pot of burning oil becomes a fireball."),
    dict(dur=6.2, title="ICE + OIL = FIRE", caption="So the fireball doesn't come from the oil. It comes from the water hiding in the bird."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sstep(t, t0, d=0.3): return ease(clamp((t - t0) / d))

STEEL = hexc('#b9c1c8'); STEEL_D = hexc('#7f8a94')
OIL = hexc('#e9b44c'); OIL_D = hexc('#b9822a'); OIL_FOAM = hexc('#f7e2a6')
STEAM = hexc('#fbf6ea')
SKIN = hexc('#f0cfae'); SKIN_D = hexc('#c99a78'); CAVITY = hexc('#a8705a')
ICE = hexc('#cfeaf7'); ICE_D = hexc('#5aa6cf')
BASE = hexc('#3d3a36')
FL_Y = hexc('#f7d24a')

# ---------------------------------------------------------------- geometry
RIM = 720                       # top of the pot walls
BOT = 1290                      # outer bottom of the pot
XO_L, XO_R = 270, 810           # outer walls
WT = 20
XI_L, XI_R = XO_L + WT, XO_R - WT
IN_BOT = BOT - WT
BURN_Y = 1345                   # burner ring (below the pot)
TX = 540                        # turkey x
HANG_Y, DIP_Y = 560, 1080       # turkey centre: hanging / in the oil
RX, RY = 150, 108               # turkey body half-axes

# ---------------------------------------------------------------- state over time
def reset(t):
    """1 during the beat-1 preview, falls to 0 at B(1) (everything returns to the starting state)."""
    return 1 - sstep(t, B(1), 0.5) if t < B(2) else 0.0

def turkey_y(t):
    if t < B(2):
        y = lerp(HANG_Y, DIP_Y, sstep(t, 0.15, 0.45))
        return lerp(HANG_Y, y, reset(t))
    return lerp(HANG_Y, DIP_Y, sstep(t, B(5) + 0.3, 1.2))

def oil_y(t):
    """Oil surface (y DOWN): 960 before the turkey, rises (smaller y) as steam pushes it up."""
    if t < B(2):
        y = lerp(960, 690, sstep(t, 0.55, 0.45))
        return lerp(960, y, reset(t))
    y = lerp(960, 925, sstep(t, B(5) + 0.6, 0.8))
    y = lerp(y, 770, sstep(t, B(7) + 0.4, 4.0))
    y = lerp(y, 690, sstep(t, B(8) + 0.3, 1.2))
    return y

def spill(t):
    """0..1: how far the overflow has run down the outside of the pot (rim -> burner)."""
    if t < B(2):
        return sstep(t, 0.85, 0.4) * reset(t)
    return ease(clamp((t - (B(8) + 1.4)) / (B(9) + 1.4 - (B(8) + 1.4))))

def fire(t):
    """0 = normal burner flame, 1 = fireball."""
    if t < B(2):
        return sstep(t, 1.15, 0.4) * reset(t)
    f = 0.32 * sstep(t, B(9) + 1.5, 0.5) + 0.68 * sstep(t, B(10) + 0.3, 0.8)
    return f * (1 - 0.42 * sstep(t, B(11) + 0.5, 1.0))

def ice(t):
    """amount of ice left on / in the turkey."""
    if t < B(2): return 1.0
    return 1 - 0.85 * sstep(t, B(5) + 1.2, B(9) - B(5))

def submerged(t):
    return turkey_y(t) - 40 > oil_y(t)

def emission(t):
    if not submerged(t): return 0
    if t < B(2): return 70
    return lerp(28, 75, sstep(t, B(5) + 1.4, 6.0)) * (1 - 0.5 * sstep(t, B(11), 2.0))

# ---------------------------------------------------------------- bubbles
_r = random.Random(11)
SLOTS = [(_r.uniform(0, 1), _r.uniform(0, 1), _r.uniform(0, 1)) for _ in range(5000)]
RISE = 300.0

def bubble_list(t):
    out = []
    dt = 1 / 40.0
    for i in range(max(int((t - 2.5) / dt), 0), int(t / dt) + 1):
        tb = i * dt
        if tb > t: break
        u, ua, us = SLOTS[i % len(SLOTS)]
        if u > emission(tb) * dt: continue
        cy = turkey_y(tb)
        an = lerp(0.15, math.pi - 0.15, ua)               # lower half of the body + sides
        if us < 0.35:                                       # some from the cavity (dark centre)
            x0, y0 = TX + (ua - 0.5) * 120, cy + 5
        else:
            x0, y0 = TX + math.cos(an) * RX * 0.95, cy + math.sin(an) * RY * 0.6 - 30
        speed = RISE * (0.8 + 0.5 * us)
        y = y0 - speed * (t - tb)
        x = x0 + 10 * math.sin(tb * 7 + (t - tb) * 6)
        r = 6 + 9 * us * (1 + 0.6 * clamp((t - tb) / 1.2))
        top = oil_y(t) + 8
        if y > top:
            out.append((x, y, r, 'rise', 0.0))
        else:
            te = tb + (y0 - top) / speed
            age = t - te
            if 0 <= age < 0.3: out.append((x, top, r, 'pop', age))
    return out

def draw_bubble(ctx, x, y, r, st, age):
    if st == 'rise':
        ctx.arc(x, y, r, 0, 6.28); setc(ctx, STEAM, 0.92); ctx.fill_preserve()
        setc(ctx, INK, 0.8); ctx.set_line_width(2.5); ctx.stroke()
        ctx.arc(x - r * 0.35, y - r * 0.35, r * 0.25, 0, 6.28); setc(ctx, WHITE); ctx.fill()
    else:
        k = age / 0.3
        ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.4)
        ctx.arc(0, 0, r + 22 * k, 0, 6.28); ctx.restore()
        setc(ctx, INK2, 0.6 * (1 - k)); ctx.set_line_width(2.5); ctx.stroke()

# ---------------------------------------------------------------- turkey
def turkey_body_path(ctx, cx, cy):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(RX, RY); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()

def turkey(ctx, cx, cy, t, ia):
    # lifting rod + hook (comes from above, holds the bird through the cavity)
    ctx.move_to(cx, 200); ctx.line_to(cx, cy + 10)
    setc(ctx, INK); ctx.set_line_width(12); ctx.stroke()
    setc(ctx, STEEL_D); ctx.set_line_width(6); ctx.move_to(cx, 200); ctx.line_to(cx, cy + 10); ctx.stroke()
    # drumsticks pointing UP (legs up), bone knobs at the top
    for s in (-1, 1):
        x0, y0, x1, y1 = cx + s * 70, cy - 55, cx + s * 112, cy - 165
        ctx.move_to(x0, y0); ctx.line_to(x1, y1)
        setc(ctx, INK); ctx.set_line_width(62); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
        ctx.move_to(x0, y0); ctx.line_to(x1, y1)
        setc(ctx, SKIN); ctx.set_line_width(52); ctx.stroke()
        for dx in (-9, 9):
            ctx.arc(x1 + s * 6 + dx, y1 - 32, 11, 0, 6.28); fill_stroke(ctx, WHITE, lw=3)
        ctx.rectangle(x1 + s * 6 - 8, y1 - 34, 16, 26); setc(ctx, WHITE); ctx.fill()
    # body (section)
    turkey_body_path(ctx, cx, cy); fill_stroke(ctx, SKIN, lw=5)
    # cavity
    ctx.save(); ctx.translate(cx, cy + 6); ctx.scale(86, 58); ctx.arc(0, 0, 1, 0, 6.28); ctx.restore()
    fill_stroke(ctx, CAVITY, lw=4)
    # ice crystals inside the cavity (shrink as they melt)
    rr = random.Random(3)
    for j in range(7):
        px = cx + rr.uniform(-58, 58); py = cy + 6 + rr.uniform(-30, 30); s = rr.uniform(14, 24) * ia
        if s < 2: continue
        ctx.move_to(px, py - s); ctx.line_to(px + s * 0.8, py - s * 0.2); ctx.line_to(px + s * 0.5, py + s * 0.8)
        ctx.line_to(px - s * 0.6, py + s * 0.7); ctx.line_to(px - s * 0.85, py - s * 0.25); ctx.close_path()
        setc(ctx, ICE, min(1, ia * 1.5)); ctx.fill_preserve(); setc(ctx, ICE_D, min(1, ia * 1.5)); ctx.set_line_width(2.5); ctx.stroke()
    # frost specks on the skin
    rr = random.Random(5)
    for j in range(26):
        an = rr.uniform(0, 6.28); k = rr.uniform(0.72, 0.95)
        px = cx + math.cos(an) * RX * k; py = cy + math.sin(an) * RY * k
        if abs(px - cx) < 95 and abs(py - cy - 6) < 64: continue
        ctx.arc(px, py, rr.uniform(3, 6), 0, 6.28); setc(ctx, ICE_D, 0.8 * ia); ctx.fill()
        ctx.arc(px - 1, py - 1, 2, 0, 6.28); setc(ctx, WHITE, ia); ctx.fill()

# ---------------------------------------------------------------- burner, flames
def flame(ctx, x, yb, w, h, t, ph, a=1.0):
    """One flame tongue: base at (x, yb), tip UP at yb - h."""
    if h < 2 or a <= 0: return
    sway = 0.18 * w * math.sin(t * 9 + ph)
    for col, k in ((RED, 1.0), (ORANGE, 0.72), (FL_Y, 0.42)):
        ww, hh = w * k, h * k
        ctx.move_to(x - ww / 2, yb)
        ctx.curve_to(x - ww / 2, yb - hh * 0.45, x + sway - ww * 0.15, yb - hh * 0.7, x + sway * 1.6, yb - hh)
        ctx.curve_to(x + sway + ww * 0.15, yb - hh * 0.7, x + ww / 2, yb - hh * 0.45, x + ww / 2, yb)
        ctx.close_path(); setc(ctx, col, a); ctx.fill()

def burner(ctx, t):
    # stand legs + ring
    for x0, x1 in ((300, 250), (780, 830)):
        ctx.move_to(x0, BOT + 10); ctx.line_to(x1, 1500); setc(ctx, BASE); ctx.set_line_width(16); ctx.stroke()
    ctx.move_to(250, BOT + 6); ctx.line_to(830, BOT + 6); setc(ctx, BASE); ctx.set_line_width(14); ctx.stroke()
    # gas hose to the left
    ctx.move_to(380, BURN_Y + 16); ctx.curve_to(200, BURN_Y + 30, 140, 1480, 0, 1490)
    setc(ctx, INK); ctx.set_line_width(14); ctx.stroke()
    # burner head
    rrect(ctx, 380, BURN_Y, 320, 30, 10); fill_stroke(ctx, BASE, lw=4)
    # normal gas flames under the pot (blue-ish small, tips UP towards the pot bottom)
    for i in range(7):
        x = 405 + i * 45
        h = 40 + 6 * math.sin(t * 11 + i)
        ctx.move_to(x - 12, BURN_Y); ctx.curve_to(x - 12, BURN_Y - h * 0.5, x, BURN_Y - h * 0.8, x, BURN_Y - h)
        ctx.curve_to(x, BURN_Y - h * 0.8, x + 12, BURN_Y - h * 0.5, x + 12, BURN_Y); ctx.close_path()
        setc(ctx, hexc('#3f7fc8'), 0.9); ctx.fill()

def flame_sheet(ctx, x0, x1, yb, h, t, seed, a=1.0, n=5, lean=0.0):
    """One continuous sheet of fire: base along y = yb from x0 to x1 (soft rounded bottom),
    n tongues whose tips point UP (smaller y). Three nested layers red > orange > yellow, ink outline.
    lean > 0 bends the tips to the right (screen x)."""
    if h < 4 or a <= 0.01 or x1 - x0 < 8: return
    rr = random.Random(seed)
    tips = [(rr.uniform(0.75, 1.0), rr.uniform(0, 6.28), rr.uniform(-0.25, 0.25)) for _ in range(n)]
    def path(k, inset):
        xa, xb = x0 + inset, x1 - inset
        w = (xb - xa) / n
        ctx.move_to(xa, yb)
        for i, (hk, ph, jit) in enumerate(tips):
            u = (i + 0.5) / n
            env = 0.45 + 0.55 * math.sin(math.pi * u)
            hh = h * k * hk * env * (1 + 0.07 * math.sin(t * 8 + ph))
            xc = xa + (i + 0.5 + jit * 0.5) * w
            sway = w * (0.22 * math.sin(t * 6.5 + ph) + lean)
            xv = xa + (i + 1) * w
            yv = yb - hh * 0.28
            ctx.curve_to(xc - w * 0.45, yb - hh * 0.35, xc - w * 0.15 + sway * 0.5, yb - hh * 0.75, xc + sway, yb - hh)
            ctx.curve_to(xc + w * 0.1 + sway * 0.5, yb - hh * 0.7, xc + w * 0.4, yb - hh * 0.4,
                         xv if i < n - 1 else xb, yv if i < n - 1 else yb)
        ctx.curve_to(xb, yb + 14 * k, xa, yb + 14 * k, xa, yb)   # soft bottom
        ctx.close_path()
    path(1.0, 0); setc(ctx, RED, a); ctx.fill_preserve()
    setc(ctx, INK, 0.85 * a); ctx.set_line_width(3.5); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ins = (x1 - x0) * 0.12
    path(0.72, ins); setc(ctx, ORANGE, a); ctx.fill()
    path(0.45, ins * 2.2); setc(ctx, FL_Y, a); ctx.fill()

def fireball(ctx, t, f):
    """Burning oil: fire sits where the oil is -- the puddle on the burner, the streams on both outer walls,
    then the oil surface in the pot. Every flame grows UP from its base."""
    if f <= 0.01: return
    g = min(1.0, f / 0.32)                       # ground fire comes first
    flame_sheet(ctx, 330, 750, BURN_Y + 26, 110 * g + 120 * f, t, 21, n=7)
    # sheets climbing the outside of both walls (where the oil ran down)
    hw = (220 + 320 * f) * f
    flame_sheet(ctx, XO_L - 105, XO_L + 50, BURN_Y + 10, hw, t, 22, n=2, lean=-0.08)
    flame_sheet(ctx, XO_R - 50, XO_R + 105, BURN_Y + 10, hw, t, 23, n=2, lean=0.08)
    if f > 0.45:                                 # the oil surface itself catches: the ball above the pot
        k = ease(clamp((f - 0.45) / 0.55))
        yb = oil_y(t) - 4
        flame_sheet(ctx, lerp(540 - 120, XO_L - 30, k), lerp(540 + 120, XO_R + 30, k), yb,
                    440 * k + 60, t, 24, n=6)

# ---------------------------------------------------------------- pot + oil
def pot(ctx, t):
    yo = oil_y(t)
    cy = turkey_y(t)
    # oil inside
    ctx.save(); ctx.rectangle(XI_L, RIM - 40, XI_R - XI_L, IN_BOT - RIM + 40); ctx.clip()
    ctx.rectangle(XI_L, yo, XI_R - XI_L, IN_BOT - yo); setc(ctx, OIL); ctx.fill()
    g = cairo.LinearGradient(0, yo, 0, IN_BOT)
    g.add_color_stop_rgba(0, *OIL[:3], 0); g.add_color_stop_rgba(1, *OIL_D[:3], 0.45)
    ctx.rectangle(XI_L, yo, XI_R - XI_L, IN_BOT - yo); ctx.set_source(g); ctx.fill()
    ctx.restore()
    # heat waves in the oil during the oil beats
    h = bw(t, 2, 4)
    for i, x in enumerate((360, 720)):
        wavy_arrow(ctx, x, 1240, x, 1040, t + i, ORANGE, h, amp=8, wl=36, lw=5, head=12)
    # turkey (in front of the back wall), oil tint over its submerged part
    turkey(ctx, TX, cy, t, ice(t))
    if yo < cy + RY:
        ctx.save(); ctx.rectangle(XI_L, yo, XI_R - XI_L, IN_BOT - yo); ctx.clip()
        turkey_body_path(ctx, TX, cy); setc(ctx, OIL, 0.35); ctx.fill()
        ctx.restore()
    # bubbles
    ctx.save(); ctx.rectangle(XI_L, RIM - 60, XI_R - XI_L, IN_BOT - RIM + 60); ctx.clip()
    for (x, y, r, st, age) in bubble_list(t):
        draw_bubble(ctx, x, y, r, st, age)
    ctx.restore()
    # surface line + foam when it is boiling hard
    foam = clamp((emission(t) - 20) / 40)
    ctx.move_to(XI_L, yo); ctx.line_to(XI_R, yo); setc(ctx, OIL_D); ctx.set_line_width(5); ctx.stroke()
    if foam > 0:
        rr = random.Random(int(t * 12))
        for i in range(22):
            x = lerp(XI_L + 10, XI_R - 10, i / 21) + rr.uniform(-6, 6)
            r = rr.uniform(9, 17) * foam
            ctx.arc(x, yo - 2, r, 0, 6.28); setc(ctx, OIL_FOAM, 0.95); ctx.fill_preserve()
            setc(ctx, OIL_D, 0.7); ctx.set_line_width(2); ctx.stroke()
    # walls (section) + bottom
    for x0 in (XO_L, XI_R):
        ctx.rectangle(x0, RIM, WT, BOT - RIM); fill_stroke(ctx, STEEL, lw=4)
    ctx.rectangle(XO_L, IN_BOT, XO_R - XO_L, WT); fill_stroke(ctx, STEEL, lw=4)
    # handles
    for s in (-1, 1):
        x = XO_L if s < 0 else XO_R
        ctx.move_to(x, RIM + 40); ctx.curve_to(x + s * 50, RIM + 40, x + s * 50, RIM + 90, x, RIM + 90)
        setc(ctx, INK); ctx.set_line_width(10); ctx.stroke()
    # overflow over the rim and down the OUTSIDE of both walls (gravity: y increases)
    s = spill(t)
    if s > 0:
        y_end = lerp(RIM, BURN_Y + 10, s)
        for side in (-1, 1):
            xw = XO_L - 9 if side < 0 else XO_R + 9
            xl = XI_L + 15 if side < 0 else XI_R - 15
            # lip of foam flowing over the rim
            ctx.move_to(xl, RIM - 8); ctx.curve_to(xl, RIM - 40, xw, RIM - 40, xw, RIM + 10)
            setc(ctx, OIL_D); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
            ctx.move_to(xl, RIM - 8); ctx.curve_to(xl, RIM - 40, xw, RIM - 40, xw, RIM + 10)
            setc(ctx, OIL); ctx.set_line_width(18); ctx.stroke()
            # stream down the wall, then inward along the stand to the burner
            ctx.move_to(xw, RIM + 10); ctx.line_to(xw, min(y_end, BOT))
            if y_end > BOT:
                xb = lerp(xw, 400 if side < 0 else 680, clamp((y_end - BOT) / (BURN_Y + 10 - BOT)))
                ctx.line_to(xb, y_end)
            setc(ctx, OIL_D); ctx.set_line_width(20); ctx.stroke_preserve()
            setc(ctx, OIL); ctx.set_line_width(12); ctx.stroke()
            # drip at the front of the stream
            ctx.arc(xw if y_end <= BOT else xb, y_end + 6, 9, 0, 6.28); setc(ctx, OIL); ctx.fill()

# ---------------------------------------------------------------- labels
def labels(ctx, t):
    # beat 1 (preview)
    tag(ctx, "FROZEN SOLID", 540, 330, ICE_D, sstep(t, 0.05, 0.25) * (1 - sstep(t, 1.05, 0.2)), 30)
    tag(ctx, "FIRE!", 540, 330, RED, sstep(t, 1.3, 0.2) * (1 - sstep(t, B(1) - 0.2, 0.3)), 34)
    # beat 2: hidden ice
    a = bw(t, 1) * sstep(t, B(1) + 1.6, 0.3)
    highlight(ctx, TX, HANG_Y + 6, 120, 90, ICE_D, a, t)
    tag(ctx, "HIDDEN ICE", 540, 330, ICE_D, a, 30)
    # beat 3: oil temperature
    a = bw(t, 2) * sstep(t, B(2) + 0.5, 0.3)
    tag(ctx, "1 · OIL ≈ 180 °C · 350 °F", 540, 1110, RED, a, 30)
    # beat 4: water boils at 100
    a = bw(t, 3) * sstep(t, B(3) + 0.3, 0.3)
    tag(ctx, "WATER BOILS AT 100 °C · 212 °F", 540, 1060, ICE_D, a, 26)
    tag(ctx, "OIL ≈ 2× HOTTER", 540, 1160, RED, bw(t, 3) * sstep(t, B(3) + 2.6, 0.3), 30)
    # beat 6: flash to steam
    a = bw(t, 5) * sstep(t, B(5) + 1.6, 0.3)
    tag(ctx, "ICE TURNS TO STEAM", 540, 640, INK, a, 30)
    # beat 8: piston
    a = bw(t, 7) * sstep(t, B(7) + 0.6, 0.3)
    tag(ctx, "3 · STEAM PUSHES THE OIL UP", 540, 640, TEAL, a, 26)
    k = bw(t, 7, 9) * sstep(t, B(7) + 0.6, 0.3)
    for x in (380, 700):
        straight_arrow(ctx, x, oil_y(t) + 150, x, oil_y(t) + 30, TEAL, k, lw=8, head=16)
    # beat 9: overflow
    a = bw(t, 8) * sstep(t, B(8) + 1.4, 0.3)
    tag(ctx, "OVER THE RIM", 540, 560, OIL_D, a, 30)
    # beat 10: on the flame
    a = bw(t, 9) * sstep(t, B(9) + 1.4, 0.3)
    tag(ctx, "OIL ON THE FLAME", 540, 1440, RED, a, 28)
    # beat 11: fireball
    a = bw(t, 10) * sstep(t, B(10) + 0.6, 0.3)
    tag(ctx, "FIREBALL", 540, 330, RED, a, 34)

def recap(ctx, t):
    a0 = sstep(t, B(11) + 0.3, 0.3)
    if a0 <= 0: return
    tag(ctx, "ICE + 180 °C OIL", 540, 330, ICE_D, a0, 30)
    tag(ctx, "= 1,700× STEAM", 540, 410, TEAL, sstep(t, B(11) + 1.5, 0.3), 30)
    tag(ctx, "= OIL ON THE FLAME", 540, 490, RED, sstep(t, B(11) + 2.8, 0.3), 30)

def zoom_tags(ctx, t):
    """beat 5 (zoomed on the hanging turkey): screen-space tags."""
    a = bw(t, 4)
    if a <= 0: return
    tag(ctx, "2 · ICE IN THE CAVITY", 540, 1240, ICE_D, a * sstep(t, B(4) + 2.4, 0.3), 30)
    tag(ctx, "FROST ON THE SKIN", 540, 330, ICE_D, a * sstep(t, B(4) + 0.8, 0.3), 30)

# ---------------------------------------------------------------- assembly
def draw_set(ctx):
    pass

def draw(ctx, t, E):
    burner(ctx, t)
    pot(ctx, t)
    fireball(ctx, t, fire(t))
    labels(ctx, t)

CAM_KEYS = [(0, 540, 900, 1.0), (B(4) + 0.1, 540, 590, 1.7), (B(5) - 0.2, 540, 900, 1.0)]
def CAM(t):
    return cam_track(CAM_KEYS, t, 0.8)

def draw_hud(ctx, t, E):
    zoom_tags(ctx, t)
    recap(ctx, t)

# ---------------------------------------------------------------- card
def card_expand(ctx, t, lt, a):
    card_frame(ctx, "WATER INTO STEAM", a, "≈ 1,700 × MORE VOLUME", RED)
    # the single drop: one square, ringed
    x0, y0, p = 200, 395, 8
    ctx.rectangle(x0 - 3.5, y0 - 3.5, 7, 7); setc(ctx, ICE_D, a); ctx.fill()
    ctx.arc(x0, y0, 22, 0, 6.28); setc(ctx, ICE_D, a); ctx.set_line_width(3); ctx.stroke()
    text_c(ctx, "1 CUP", x0, y0 + 60, 24, ICE_D, True, 2, a)
    text_c(ctx, "WATER", x0, y0 + 88, 20, INK2, True, 2, a)
    straight_arrow(ctx, 250, y0, 320, y0, INK, a * sstep(lt, 0.3, 0.3), lw=5, head=10)
    # the steam: 65 x 26 squares = 1,690 cups, filling column by column
    cols, rows = 65, 26
    gx, gy = 410, y0 - rows * p / 2
    n = int(cols * rows * ease(clamp((lt - 0.5) / 2.6)))
    for i in range(n):
        c, r = i // rows, i % rows
        ctx.rectangle(gx + c * p, gy + r * p, 7, 7)
    setc(ctx, STEAM, a); ctx.fill_preserve(); setc(ctx, INK2, a * 0.8); ctx.set_line_width(0.8); ctx.stroke()
    text_c(ctx, f"{n:,} CUPS OF STEAM", gx + cols * p / 2, gy - 16, 22, INK, True, 2, a * sstep(lt, 0.5, 0.3))

CARDS = {'expand': card_expand}

SFX = [(0.05, 'pop'), (1.3, 'pop'), (B(1) + 1.6, 'pop'), (B(2) + 0.5, 'pop'), (B(3) + 0.3, 'pop'),
       (B(3) + 2.6, 'pop'), (B(4) + 0.8, 'pop'), (B(4) + 2.4, 'pop'), (B(5) + 1.6, 'pop'), (B(7) + 0.6, 'pop'),
       (B(8) + 1.4, 'pop'), (B(9) + 1.4, 'pop'), (B(10) + 0.6, 'pop'), (B(11) + 0.3, 'pop'), (B(11) + 1.5, 'pop'),
       (B(11) + 2.8, 'pop')]
HUM = []
