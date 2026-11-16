"""Cogwise episode: Your oven locks you out, then turns grease into ash (pyrolytic self-cleaning).
One idea: pyrolysis — heat alone (~500 °C / 932 °F) breaks grease's carbon-hydrogen chains; the pieces leave
as smoke, steam and CO2 through a vent, what can't burn stays as grey ash. The door lock is the condition for it.

VIEW (screen coordinates, y grows DOWN): SIDE SECTION of a built-in oven. The FRONT of the oven faces LEFT.
  - door on the LEFT (x 210-290), three vertical glass panes, handle further left; door top catch at y ~545.
  - cavity x 300-830, y 620-1250; insulation (hatched) on top, back (right) and bottom, 50 px thick.
  - grill element just under the cavity ceiling (zigzag, y ~660); bottom element under the floor (y ~1275).
  - cooling channel above the cavity, y 420-510: air comes in at the BACK (right, x 900) and leaves at the
    FRONT (left, x 200, above the door). The tangential fan sits in it (x 600); thermal fuse at x 470.
  - cavity vent: a tube from the cavity ceiling at x 770 up into the channel: fumes go UP, then LEFT with the air.
  - motorized latch between channel and insulation (y 515-565): a hook slides LEFT into the door's top catch.
  - fan rotor turns counter-clockwise on screen (top moving LEFT = the way the air goes).
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="oven-self-clean",
    title="Your oven locks you out, then turns grease into ash 🔥 #Shorts",
    description=("That locked door isn't a glitch. It's how your oven burns itself clean.\n\n"
                 "#Shorts #howthingswork #appliances #oven #cogwise"),
    hashtags=["Shorts", "howthingswork", "appliances", "oven", "cogwise"],
    sources=[
        "https://www.haier-europe.com/fr_FR/blogs/news/pyrolyse-four-comment-fonctionne",
        "https://www.appliancepartspros.com/b/?p=875",
        "https://www.appliancepartspros.com/b/?p=11628",
        "https://en.wikipedia.org/wiki/Self-cleaning_oven",
    ],
)

BEATS = [
    dict(dur=6.2, title="WAIT, WHAT?", caption="Press one button and your oven locks itself shut, then turns grease into ash."),
    dict(dur=5.0, title="THE SECRET", caption="It's called pyrolysis: cleaning with heat alone, no chemicals, no scrubbing."),
    dict(dur=5.0, title="500 °C · 932 °F", caption="The cavity climbs to five hundred Celsius, nine hundred thirty Fahrenheit."),
    dict(dur=5.0, title="1 · THE LOCK", caption="Before it gets that hot, a motorized latch locks the door."),
    dict(dur=6.2, title=None, caption="Grease is long chains of carbon and hydrogen. At this heat, they snap apart.", card='chains'),
    dict(dur=5.4, title="2 · THE VENT", caption="The pieces escape through a vent as smoke, steam and carbon dioxide."),
    dict(dur=6.6, title="3 · THE ASH", caption="What can't burn stays behind: a thin grey ash you wipe off with a cloth."),
    dict(dur=4.6, title="THE WALLS", caption="Thick insulation and a triple-glazed door keep that heat inside."),
    dict(dur=6.2, title="THE FAN", caption="Under the controls, a fan blows the whole time, for up to three hours."),
    dict(dur=7.4, title=None, caption="The door stays locked until it cools to about two hundred fifty Celsius, four hundred eighty Fahrenheit.", card='cool'),
    dict(dur=6.6, title="HARD ON PARTS", caption="It's tough on the oven too: a tired fan or thermal fuse can give up."),
    dict(dur=5.8, title="LOCK + HEAT = ASH", caption="So the lock isn't a glitch. It's how your oven burns itself clean."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)
def sst(t, t0, d=0.18):
    return ease(clamp((t - t0) / d))

STEEL = hexc('#9aa3ab'); STEEL_D = hexc('#6d757c')
GLASS = hexc('#bfe3df'); HOT = hexc('#ff5a2a')
GREASE = hexc('#b07a2a'); ASH = hexc('#b8b2a7')
CAV = hexc('#3a3640'); CAV_HOT = hexc('#5a2f22')
INSUL = hexc('#f3d98a'); COPPER = hexc('#c46d2e')

# ---------------------------------------------------------------- geometry
BX0, BX1, BY0, BY1 = 200, 910, 400, 1380      # oven body
CH_Y0, CH_Y1 = 420, 510                       # cooling channel
CX0, CX1, CY0, CY1 = 300, 830, 620, 1250      # cavity (inside)
INS = 50                                      # insulation thickness
DX0, DX1, DY0, DY1 = 210, 290, 520, 1330      # door
LATCH_Y = 543                                 # hook centre line
FAN = (600, 465, 34)
FUSE = (470, 492)
VENT_X = 770

SPOTS = [  # (x, y, rx, ry) grease on the back wall, floor, ceiling and door glass (inner side)
    (814, 760, 16, 38), (812, 930, 18, 50), (815, 1110, 15, 34),
    (430, 1236, 50, 14), (590, 1237, 62, 13), (735, 1236, 42, 14),
    (520, 636, 36, 12), (690, 635, 28, 11),
]

def state(t):
    s = {}
    # beat 1: preview (lock, heat, grease -> ash); beat 2: the stage resets
    reset = sst(t, B(1) + 0.15, 0.4)
    pre_lock = sst(t, 0.5, 0.15) * (1 - reset)
    pre_heat = 0.75 * sst(t, 0.7, 0.8) * (1 - reset)
    pre_ash = sst(t, 1.0, 0.8) * (1 - reset)
    # the real cycle: lock at the very start of beat 3, heat ramps after it
    lock = sst(t, B(2) + 0.2, 0.15) * (1 - sst(t, B(9) + 4.6, 0.15))
    lock = max(lock, sst(t, B(11) + 0.3, 0.15))
    heat = sst(t, B(2) + 0.8, 3.2)
    cool = clamp((t - B(9) - 0.4) / 4.2)
    heat = heat * (1 - 0.55 * cool)
    if t >= B(10): heat = 0.45 * (1 - sst(t, B(10) + 4.5, 1.0))
    if t >= B(11): heat = 0.6 * sst(t, B(11) + 0.4, 0.6)
    s['lock'] = max(pre_lock, lock)
    s['heat'] = max(pre_heat, heat)
    ash = sst(t, B(4), B(6) + 1.2 - B(4))
    s['ash'] = max(pre_ash, ash)
    s['fumes'] = win(t, B(4) + 0.5, B(7) + 0.4, 0.5)
    # fan: runs once the cycle starts; slows and stutters in beat 11
    s['fan_on'] = sst(t, B(2) + 0.3, 0.5)
    s['air'] = win(t, B(8) + 0.2, B(10) + 0.4, 0.4)
    s['tired'] = win(t, B(10) + 0.3, B(11) + 0.1, 0.4)
    # zooms: beat 4 on the latch, beat 11 on the channel
    s['zl'] = win(t, B(3) + 0.05, B(4) + 0.3, 0.6)
    s['zf'] = win(t, B(10) + 0.05, B(11) + 0.2, 0.6)
    return s

def fan_angle(t):
    """Integrated angle: steady speed, slower in beat 11. Negative = counter-clockwise on screen."""
    def ang(u):
        a = -9.0 * max(0.0, u - (B(2) + 0.3))
        if u > B(10) + 0.5:
            v = min(u, B(11) + 0.2) - (B(10) + 0.5)
            a += 9.0 * 0.75 * v          # 75 % slower: a tired fan
        return a
    return ang(t)

# ---------------------------------------------------------------- pieces
def padlock(ctx, x, y, sc, closed, col, a):
    if a <= 0: return
    w, h = 44 * sc, 34 * sc
    lift = 0 if closed else 14 * sc
    ctx.new_path()
    ctx.arc(x, y - h / 2 - lift, w * 0.32, math.pi, 2 * math.pi)
    ctx.line_to(x + w * 0.32, y - h / 2)
    ctx.move_to(x - w * 0.32, y - h / 2 - lift); ctx.line_to(x - w * 0.32, y - h / 2 - (lift if not closed else 0))
    setc(ctx, col, a); ctx.set_line_width(7 * sc); ctx.stroke()
    rrect(ctx, x - w / 2, y - h / 2, w, h, 5 * sc); fill_stroke(ctx, col, lw=3 * sc, alpha=a)
    ctx.arc(x, y, 4 * sc, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()

def hatch(ctx, x, y, w, h, a):
    ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
    setc(ctx, INSUL, a); ctx.paint_with_alpha(1) if False else None
    ctx.rectangle(x, y, w, h); setc(ctx, INSUL, a); ctx.fill()
    step = 18
    for k in range(-int(h), int(w) + int(h), step):
        ctx.move_to(x + k, y + h); ctx.line_to(x + k + h, y)
    setc(ctx, hexc('#c9a24a'), a); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    ctx.rectangle(x, y, w, h); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()

def rotor(ctx, cx, cy, r, ang, a, col=PAPER):
    ctx.arc(cx, cy, r, 0, 2 * math.pi); fill_stroke(ctx, col, lw=4, alpha=a)
    for i in range(10):
        an = ang + i * 2 * math.pi / 10
        x0, y0 = cx + r * 0.35 * math.cos(an), cy + r * 0.35 * math.sin(an)
        x1, y1 = cx + r * 0.95 * math.cos(an + 0.5), cy + r * 0.95 * math.sin(an + 0.5)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1)
    setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(cx, cy, r * 0.22, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)

def fumes_path(u):
    """u in [0,1]: from the cavity up the vent, then LEFT along the channel and out the front."""
    pts = [(VENT_X, CY0 + 60), (VENT_X, CH_Y0 + 55), (BX0 - 10, CH_Y0 + 45), (120, CH_Y0 + 5)]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(3)]
    L = sum(seg) * u
    for i in range(3):
        if L <= seg[i] or i == 2:
            k = clamp(L / seg[i]); p, q = pts[i], pts[i + 1]
            return lerp(p[0], q[0], k), lerp(p[1], q[1], k)
        L -= seg[i]

def oven(ctx, t, s):
    heat, ash, lock = s['heat'], s['ash'], s['lock']
    # body
    rrect(ctx, BX0, BY0, BX1 - BX0, BY1 - BY0, 14); fill_stroke(ctx, FILL2, lw=6)
    # cooling channel (open at the back right and at the front left)
    ctx.rectangle(BX0 + 3, CH_Y0, BX1 - BX0 - 6, CH_Y1 - CH_Y0); setc(ctx, WALL1); ctx.fill()
    ctx.move_to(BX0 + 30, CH_Y0); ctx.line_to(BX1 - 3, CH_Y0)
    ctx.move_to(BX0 + 90, CH_Y1); ctx.line_to(BX1 - 3, CH_Y1)
    setc(ctx, INK2); ctx.set_line_width(3); ctx.stroke()
    ctx.rectangle(BX0 - 4, CH_Y0 + 10, 10, CH_Y1 - CH_Y0 - 30); setc(ctx, WALL1); ctx.fill()     # front slot
    ctx.rectangle(BX1 - 7, CH_Y0 + 10, 10, CH_Y1 - CH_Y0 - 20); setc(ctx, WALL1); ctx.fill()     # back intake
    for yy in range(CH_Y0 + 16, CH_Y1 - 6, 14):                                                  # intake grille
        ctx.move_to(BX1 - 8, yy); ctx.line_to(BX1 + 2, yy)
    setc(ctx, INK2); ctx.set_line_width(2); ctx.stroke()
    # control panel face (front = left) above the door
    rrect(ctx, BX0 - 16, BY0 + 4, 26, CH_Y0 - BY0 - 2, 6); fill_stroke(ctx, FILL3, lw=3)
    # insulation: top, back, bottom
    hatch(ctx, CX0, CY0 - INS, CX1 + INS - CX0, INS, 1)
    hatch(ctx, CX1, CY0, INS, CY1 - CY0, 1)
    hatch(ctx, CX0, CY1, CX1 + INS - CX0, INS, 1)
    # cavity
    ctx.rectangle(CX0, CY0, CX1 - CX0, CY1 - CY0); fill_stroke(ctx, lerpc(CAV, CAV_HOT, heat), lw=4)
    # glow of the hot cavity
    if heat > 0.05:
        g = cairo.RadialGradient(565, 935, 40, 565, 935, 360)
        g.add_color_stop_rgba(0, 1.0, 0.45, 0.15, 0.30 * heat); g.add_color_stop_rgba(1, 1.0, 0.35, 0.1, 0.0)
        ctx.rectangle(CX0, CY0, CX1 - CX0, CY1 - CY0); ctx.set_source(g); ctx.fill()
    # vent tube through the top insulation into the channel
    ctx.rectangle(VENT_X - 14, CH_Y1 - 2, 28, CY0 - CH_Y1 + 4); fill_stroke(ctx, STEEL, lw=3)
    ctx.rectangle(VENT_X - 7, CH_Y1, 14, CY0 - CH_Y1 + 2); setc(ctx, CAV); ctx.fill()
    # shelf supports
    for yy in (850, 1030):
        ctx.move_to(CX1 - 4, yy); ctx.line_to(CX1 - 24, yy); setc(ctx, STEEL); ctx.set_line_width(6); ctx.stroke()
    # grill element (zigzag under the ceiling) and bottom element (tube sections under the floor)
    ecol = lerpc(STEEL_D, HOT, heat)
    ctx.move_to(CX0 + 50, 650)
    for i in range(12):
        ctx.line_to(CX0 + 50 + (i + 0.5) * 36, 672 if i % 2 == 0 else 650)
    ctx.line_to(CX1 - 40, 650)
    setc(ctx, ecol); ctx.set_line_width(9); ctx.stroke()
    for i in range(8):
        ctx.arc(CX0 + 70 + i * 58, CY1 + 24, 9, 0, 6.28); fill_stroke(ctx, ecol, lw=2)
    # grease spots -> ash
    for (x, y, rx, ry) in SPOTS:
        k = 1 - 0.35 * ash
        ctx.save(); ctx.translate(x, y); ctx.scale(rx * k, ry * k); ctx.arc(0, 0, 1, 0, 6.28); ctx.restore()
        setc(ctx, lerpc(GREASE, ASH, ash)); ctx.fill()
    # door (left): frame + 3 panes, handle further left
    rrect(ctx, DX0, DY0, DX1 - DX0, DY1 - DY0, 10); fill_stroke(ctx, FILL3, lw=5)
    for x in (228, 250, 272):
        ctx.rectangle(x - 4, 600, 8, 660); fill_stroke(ctx, GLASS, lw=2)
    ctx.move_to(DX0, 560); ctx.line_to(170, 560); ctx.line_to(170, 640); ctx.line_to(DX0, 640)
    setc(ctx, INK); ctx.set_line_width(8); ctx.stroke()
    # door seal
    for yy in (CY0 + 8, CY1 - 8):
        ctx.arc(DX1 + 6, yy, 7, 0, 6.28); setc(ctx, INK2); ctx.fill()
    # door top catch (notch on the door's inner side)
    ctx.rectangle(DX1 - 26, LATCH_Y - 12, 26, 24); setc(ctx, INK2); ctx.fill()
    # motorized latch: motor box + gear, hook slides LEFT into the catch when locked
    rrect(ctx, 330, 518, 80, 48, 6); fill_stroke(ctx, FILL3, lw=3)
    gear(ctx, 370, 542, 18, 13, 8, 5, MUSTARD, lw=2, rot=-t * 3 * (sst(t, B(2) + 0.1, 0.1) - sst(t, B(2) + 0.4, 0.1)))
    hx = lerp(DX1 + 14, DX1 - 20, lock)
    ctx.rectangle(hx, LATCH_Y - 6, 330 - hx, 12); fill_stroke(ctx, lerpc(STEEL, RED, lock), lw=2)
    ctx.rectangle(hx, LATCH_Y - 6, 8, 16); fill_stroke(ctx, lerpc(STEEL, RED, lock), lw=2)
    # cooling fan + thermal fuse in the channel
    fx, fy, fr = FAN
    rrect(ctx, fx - 48, CH_Y0 + 4, 96, CH_Y1 - CH_Y0 - 8, 10); setc(ctx, FILL3); ctx.fill()
    rotor(ctx, fx, fy, fr, fan_angle(t), 1)
    ux, uy = FUSE
    tired = s['tired']
    ctx.move_to(ux - 34, uy); ctx.line_to(ux + 34, uy); setc(ctx, COPPER); ctx.set_line_width(3); ctx.stroke()
    rrect(ctx, ux - 18, uy - 8, 36, 16, 8); fill_stroke(ctx, lerpc(WHITE, HOT, 0.9 * tired * (0.6 + 0.4 * math.sin(t * 6))), lw=2)

def heat_arrows(ctx, t, s):
    a = s['heat']
    if a < 0.1: return
    for i in range(4):
        x = CX0 + 90 + i * 120
        wavy_arrow(ctx, x, 690, x + 10, 800, t, ORANGE, 0.85 * a, amp=5, wl=24, lw=4, head=10)
        wavy_arrow(ctx, x + 30, CY1 - 16, x + 30, CY1 - 120, t, RED, 0.85 * a, amp=5, wl=24, lw=4, head=10)

def fumes(ctx, t, s):
    a = s['fumes']
    if a <= 0: return
    rnd = random.Random(7)
    for i in range(16):
        ph = rnd.random(); kind = i % 3
        u = (t * 0.22 + ph) % 1
        x, y = fumes_path(u)
        x += 5 * math.sin(t * 3 + i);
        fade = min(1, u * 8) * min(1, (1 - u) * 6)
        if kind == 0:   # smoke
            ctx.arc(x, y, 10 + 6 * u, 0, 6.28); setc(ctx, STEEL_D, 0.7 * a * fade); ctx.fill()
        elif kind == 1: # steam
            ctx.arc(x, y, 7, 0, 6.28); setc(ctx, VAPOR, 0.9 * a * fade); ctx.fill()
        else:           # CO2
            ctx.arc(x, y, 8, 0, 6.28); setc(ctx, WHITE, 0.9 * a * fade); ctx.fill_preserve()
            setc(ctx, INK2, 0.8 * a * fade); ctx.set_line_width(2); ctx.stroke()
    # rising from the grease to the vent mouth
    for i in range(6):
        u = (t * 0.5 + i / 6) % 1
        x0 = SPOTS[i][0] if i < 6 else 600
        x = lerp(min(x0, 790), VENT_X, u); y = lerp(SPOTS[i][1] - 20, CY0 + 50, u)
        ctx.arc(x, y, 7, 0, 6.28); setc(ctx, STEEL, 0.6 * a * (1 - u)); ctx.fill()

def airflow(ctx, t, s):
    a = max(s['air'], 0.5 * s['tired'])
    if a <= 0: return
    for k in range(3):
        u = ((t * 0.35 + k / 3) % 1)
        x = lerp(BX1 + 40, BX0 - 70, u)
        straight_arrow(ctx, x + 70, CH_Y0 + 25 + 18 * k, x, CH_Y0 + 25 + 18 * k, TEAL, a * min(1, (1 - u) * 5) * min(1, u * 5), lw=4, head=9)

def stage_xf(ctx, s):
    """Zoom: beat 4 on the latch, beat 11 on the channel."""
    zl, zf = ease(s['zl']), ease(s['zf'])
    if zl > 0:
        px, py, z, tx, ty = 330, 545, 2.3, 520, 760
        k = zl
    elif zf > 0:
        px, py, z, tx, ty = 540, 470, 1.8, 540, 700
        k = zf
    else:
        return
    ctx.translate(lerp(px, tx, k), lerp(py, ty, k)); ctx.scale(lerp(1, z, k), lerp(1, z, k)); ctx.translate(-px, -py)

def draw_set(ctx):
    pass

def CAM(t):
    """Camera (engine clips the stage to y < 1500): beat 4 on the latch, beat 11 on the channel."""
    s = state(t)
    zl, zf = ease(s['zl']), ease(s['zf'])
    if zl > 0: return lerp(540, 380, zl), lerp(900, 650, zl), lerp(1, 1.9, zl)
    if zf > 0: return lerp(540, 560, zf), lerp(900, 560, zf), lerp(1, 1.6, zf)
    return 540, 900, 1.0

def draw(ctx, t, E):
    s = state(t)
    oven(ctx, t, s)
    heat_arrows(ctx, t, s)
    fumes(ctx, t, s)
    airflow(ctx, t, s)

def labels(ctx, t, s):
    # beat 1
    a = win(t, 0.6, B(1) + 0.1, 0.25)
    tag(ctx, "LOCKED", 330, 1430, RED, a * sst(t, 0.6), 28)
    padlock(ctx, 150, 470, 1.1, True, RED, a * sst(t, 0.6))
    tag(ctx, "GREASE TO ASH", 700, 1430, INK, a * sst(t, 1.2), 28)
    # beat 3
    a = bw(t, 2)
    if a > 0:
        tag(ctx, "LOCKED", 150, 1430, RED, a, 26)
        highlight(ctx, 565, 660, 280, 40, RED, a * sst(t, B(2) + 1.0), t)
        tag(ctx, "HEATING ELEMENTS", 640, 1430, RED, a * sst(t, B(2) + 1.0), 26)
    # beat 4 (zoomed on the latch)
    a = bw(t, 3)
    if a > 0:
        tag(ctx, "1 · MOTORIZED LATCH", 420, 560, RED, a * sst(t, B(3) + 0.5), 30)
        tag(ctx, "DOOR", 200, 1050, INK, a * sst(t, B(3) + 0.5), 26)
        tag(ctx, "MOTOR", 760, 690, INK, a * sst(t, B(3) + 0.5), 26)
        tag(ctx, "HOOK IN THE DOOR", 420, 820, RED, a * sst(t, B(3) + 0.9), 24)
    # beat 6
    a = bw(t, 5)
    if a > 0:
        highlight(ctx, VENT_X, 565, 40, 70, TEAL, a, t)
        tag(ctx, "2 · VENT", 930, 640, TEAL, a, 28)
        tag(ctx, "SMOKE · STEAM · CO2", 540, 1430, INK, a * sst(t, B(5) + 0.6), 26)
    # beat 7
    a = bw(t, 6)
    if a > 0:
        highlight(ctx, 585, 1240, 210, 34, INK2, a, t)
        tag(ctx, "3 · GREY ASH", 585, 1430, INK, a, 28)
    # beat 8
    a = bw(t, 7)
    if a > 0:
        highlight(ctx, 855, 935, 50, 330, MUSTARD, a, t)
        highlight(ctx, 250, 930, 50, 340, TEAL, a * sst(t, B(7) + 1.2), t)
        tag(ctx, "INSULATION", 880, 1430, INK, a, 26)
        tag(ctx, "3 GLASS PANES", 250, 1430, TEAL, a * sst(t, B(7) + 1.2), 26)
        for yy in (800, 1080):
            wavy_arrow(ctx, 760, yy, 815, yy, t, ORANGE, a * 0.8, amp=4, wl=18, lw=3, head=8)
            wavy_arrow(ctx, 815, yy + 40, 760, yy + 40, t, ORANGE, a * 0.8, amp=4, wl=18, lw=3, head=8)
    # beat 9
    a = bw(t, 8)
    if a > 0:
        highlight(ctx, FAN[0], FAN[1], 62, 50, TEAL, a, t)
        tag(ctx, "COOLING FAN", 600, 1430, TEAL, a, 28)
        tag(ctx, "AIR IN", 990, 470, TEAL, a * sst(t, B(8) + 0.6), 20)
    # beat 11 (zoomed on the channel)
    a = bw(t, 10)
    if a > 0:
        tag(ctx, "TIRED FAN", 640, 600, INK, a * sst(t, B(10) + 0.5), 28)
        tag(ctx, "THERMAL FUSE", 470, 985, RED, a * sst(t, B(10) + 2.4), 28)
    # beat 12
    a = win(t, B(11) + 0.6, B(12) + 2.0, 0.3)
    if a > 0:
        tag(ctx, "LOCK + HEAT = ASH", 560, 1430, RED, a, 30)

# ---------------------------------------------------------------- HUD (top zone, y 175-375: above the oven)
def _panel(ctx, a, x=60, y=180, w=960, h=195):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def hud_secret(ctx, t, a):
    _panel(ctx, a)
    k = sst(t, B(1) + 0.4, 0.4)
    text_c(ctx, "PYROLYSIS", 380, 300, 74, RED, True, 6, a * k)
    text_c(ctx, "HEAT ONLY", 380, 350, 26, INK, True, 3, a * k)
    # sponge, then crossed out
    rrect(ctx, 760, 235, 140, 80, 14); fill_stroke(ctx, MUSTARD, lw=4, alpha=a)
    rrect(ctx, 760, 295, 140, 20, 6); fill_stroke(ctx, TEAL, lw=3, alpha=a)
    c = a * sst(t, B(1) + 1.6, 0.25)
    ctx.move_to(740, 225); ctx.line_to(920, 330); ctx.move_to(920, 225); ctx.line_to(740, 330)
    setc(ctx, RED, c); ctx.set_line_width(11); ctx.stroke()

def hud_temp(ctx, t, a, s):
    _panel(ctx, a)
    lev = clamp(s['heat'])
    x0, x1, y = 130, 640, 290
    rrect(ctx, x0, y - 18, x1 - x0, 36, 18); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    rrect(ctx, x0 + 6, y - 12, (x1 - x0 - 12) * lev, 24, 12); setc(ctx, lerpc(ORANGE, RED, lev), a); ctx.fill()
    temp = int(round((20 + 480 * lev) / 10) * 10)
    text_c(ctx, f"{temp} °C", 830, 285, 58, RED, True, 2, a)
    text_c(ctx, f"{int(round((temp * 9 / 5 + 32) / 2) * 2)} °F", 830, 340, 32, INK, True, 2, a)
    text_c(ctx, "20 °C", x0 + 30, 345, 22, INK2, True, 1, a)
    text_c(ctx, "500 °C", x1 - 40, 345, 22, RED, True, 1, a)

def hud_cloth(ctx, t, a):
    _panel(ctx, a)
    lt = t - B(6)
    w = sst(t, B(6) + 2.6, 2.2)
    # grey ash strip on a surface, wiped from left to right
    ctx.rectangle(130, 320, 820, 24); fill_stroke(ctx, FILL3, lw=3, alpha=a)
    rnd = random.Random(3)
    for i in range(60):
        x = 140 + rnd.random() * 800
        if (x - 140) / 800 < w: continue
        ctx.arc(x, 312 - rnd.random() * 8, 4 + rnd.random() * 4, 0, 6.28); setc(ctx, ASH, a); ctx.fill()
    cx = 140 + 800 * w
    rrect(ctx, cx - 70, 240, 140, 70, 16); fill_stroke(ctx, TEAL_L, lw=4, alpha=a * sst(t, B(6) + 2.2, 0.3))
    text_c(ctx, "WIPE", cx, 286, 28, INK, True, 2, a * sst(t, B(6) + 2.2, 0.3))

def hud_clock(ctx, t, a):
    _panel(ctx, a)
    cx, cy, r = 260, 278, 78
    p = clamp((t - B(8) - 0.3) / (B(9) - B(8) - 0.8))
    ctx.arc(cx, cy, r, 0, 6.28); fill_stroke(ctx, PAPER, lw=5, alpha=a)
    ctx.move_to(cx, cy); ctx.arc(cx, cy, r - 10, -math.pi / 2, -math.pi / 2 + p * 2 * math.pi); ctx.close_path()
    setc(ctx, MUSTARD, 0.6 * a); ctx.fill()
    an = -math.pi / 2 + p * 2 * math.pi
    ctx.move_to(cx, cy); ctx.line_to(cx + (r - 16) * math.cos(an), cy + (r - 16) * math.sin(an))
    setc(ctx, INK, a); ctx.set_line_width(6); ctx.stroke()
    text_c(ctx, "1 H 30 – 3 H", 680, 285, 60, INK, True, 2, a)
    text_c(ctx, "FAN ALWAYS ON", 680, 340, 28, TEAL, True, 2, a)

def hud_recap(ctx, t, a):
    _panel(ctx, a)
    k1, k2, k3 = (sst(t, B(11) + d, 0.25) for d in (0.3, 1.0, 1.7))
    padlock(ctx, 210, 290, 2.0, True, RED, a * k1)
    text_c(ctx, "+", 370, 305, 70, INK, True, 0, a * k2)
    for i in range(3):
        wavy_arrow(ctx, 480 + i * 40, 345, 480 + i * 40, 235, t, RED, a * k2, amp=5, wl=22, lw=4, head=10)
    text_c(ctx, "=", 680, 305, 70, INK, True, 0, a * k3)
    rnd = random.Random(5)
    for i in range(22):
        ctx.arc(790 + rnd.random() * 130, 330 - rnd.random() * 40 * rnd.random(), 5 + rnd.random() * 4, 0, 6.28)
        setc(ctx, ASH, a * k3); ctx.fill()
    text_c(ctx, "ASH", 855, 270, 34, INK2, True, 3, a * k3)

def draw_hud(ctx, t, E):
    s = state(t)
    labels(ctx, t, s)
    a = win(t, B(1) + 0.2, B(2) + 0.05, 0.3)
    if a > 0: hud_secret(ctx, t, a)
    a = win(t, B(2) + 0.6, B(3) + 0.05, 0.3)
    if a > 0: hud_temp(ctx, t, a, s)
    a = win(t, B(6) + 1.8, B(7) + 0.05, 0.3)
    if a > 0: hud_cloth(ctx, t, a)
    a = win(t, B(8) + 0.2, B(9) + 0.05, 0.3)
    if a > 0: hud_clock(ctx, t, a)
    a = win(t, B(11) + 0.2, B(12) + 2.0, 0.3)
    if a > 0: hud_recap(ctx, t, a)

SFX = [(0.5, 'click'), (1.2, 'pop'), (B(1) + 0.4, 'pop'), (B(1) + 1.6, 'pop'), (B(2) + 0.2, 'click'),
       (B(2) + 1.0, 'pop'), (B(3) + 0.5, 'pop'), (B(5) + 0.2, 'pop'), (B(6) + 0.2, 'pop'), (B(6) + 2.2, 'pop'),
       (B(7) + 0.2, 'pop'), (B(7) + 1.2, 'pop'), (B(8) + 0.2, 'pop'), (B(10) + 0.5, 'pop'), (B(10) + 2.4, 'pop'),
       (B(11) + 0.3, 'click'), (B(11) + 1.0, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_chains(ctx, t, lt, a):
    snap = sst(lt, 3.2, 0.15)
    card_frame(ctx, "GREASE = C–H CHAINS", a, "500 °C: THEY SNAP!" if snap > 0.5 else "LONG CHAIN", RED if snap > 0.5 else INK)
    n = 9
    rnd = random.Random(11)
    off = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(n)]
    drift = clamp((lt - 3.2) / 2.0)
    shake = 3 * clamp((lt - 1.5) / 1.7) * (1 - snap)
    pos = []
    for i in range(n):
        x = 180 + i * 90; y = 400 + (24 if i % 2 else -24)
        g = i // 3   # three fragments
        x += (g - 1) * 70 * drift + off[i][0] * 4 * drift
        y += off[g][1] * 60 * drift
        x += shake * math.sin(lt * 40 + i); y += shake * math.cos(lt * 37 + i)
        pos.append((x, y))
    for i in range(n - 1):
        if snap > 0.5 and i in (2, 5): continue
        ctx.move_to(*pos[i]); ctx.line_to(*pos[i + 1]); setc(ctx, INK, a); ctx.set_line_width(6); ctx.stroke()
    for i, (x, y) in enumerate(pos):
        for sgn in (-1, 1):
            hx, hy = x, y + sgn * 62
            ctx.move_to(x, y); ctx.line_to(hx, hy); setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
            ctx.arc(hx, hy, 15, 0, 6.28); fill_stroke(ctx, WHITE, lw=3, alpha=a)
            text_c(ctx, "H", hx, hy + 7, 18, INK, True, 0, a)
        ctx.arc(x, y, 26, 0, 6.28); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
        text_c(ctx, "C", x, y + 9, 24, WHITE, True, 0, a)
    if snap > 0:
        for (xx) in (0.5 * (pos[2][0] + pos[3][0]), 0.5 * (pos[5][0] + pos[6][0])):
            ctx.save(); ctx.translate(xx, 400)
            for k in range(8):
                an = k * math.pi / 4
                ctx.move_to(14 * math.cos(an), 14 * math.sin(an)); ctx.line_to(34 * math.cos(an), 34 * math.sin(an))
            setc(ctx, ORANGE, a * snap * (1 - drift * 0.7)); ctx.set_line_width(4); ctx.stroke(); ctx.restore()

def card_cool(ctx, t, lt, a):
    card_frame(ctx, "COOLING DOWN", a, "UNLOCKS AT ~250 °C · 480 °F", TEAL)
    u = clamp((lt - 0.4) / 4.0)
    temp = lerp(500, 250, u)
    x, y0, y1 = 300, 495, 255
    rrect(ctx, x - 20, y1, 40, y0 - y1, 20); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    ctx.arc(x, y0 + 14, 30, 0, 6.28); fill_stroke(ctx, lerpc(TEAL, RED, (temp - 250) / 250), lw=4, alpha=a)
    lev = (temp - 20) / 480
    hh = (y0 - y1 - 16) * lev
    rrect(ctx, x - 11, y0 - hh, 22, hh + 10, 11); setc(ctx, lerpc(TEAL, RED, (temp - 250) / 250), a); ctx.fill()
    yl = y0 - (y0 - y1 - 16) * (230 / 480)
    ctx.move_to(x + 26, yl); ctx.line_to(x + 60, yl); setc(ctx, TEAL, a); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "250", x + 100, yl + 9, 26, TEAL, True, 1, a)
    text_c(ctx, f"{int(round(temp / 10) * 10)} °C", 560, 400, 56, INK, True, 2, a)
    opened = sst(lt, 4.6, 0.2)
    padlock(ctx, 800, 410, 2.6, opened < 0.5, lerpc(RED, TEAL, opened), a)

CARDS = {'chains': card_chains, 'cool': card_cool}
