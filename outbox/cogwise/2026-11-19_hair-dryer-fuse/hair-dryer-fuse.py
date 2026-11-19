"""Cogwise episode: Your hair dryer can only overheat once.
One idea: behind the resettable bimetal thermostat sits a one-shot THERMAL FUSE (pellet-type thermal cutoff).
A solid chemical pellet holds a sliding contact against the lead; a spring is squeezed behind the contact.
At the rated temperature the pellet melts, the spring pushes the contact away from the lead: open circuit, for good.
It is the backup of the backup: it only acts when the thermostat fails (e.g. welded contacts).
Simplified model: real pellet TCOs use a main spring + a trip spring; we draw only the trip spring.

VIEWS (screen y grows DOWN):
- DRYER, side view cut away: air enters at the LEFT (rear grille), fan, then the heater coil, out of the nozzle on
  the RIGHT. Handle hangs DOWN under the barrel. Thermostat (bimetal) and fuse sit on TOP of the heater,
  wired in series: cord -> handle -> thermostat -> fuse -> coil.
- BIMETAL LOUPE: strip fixed at its LEFT end, contact under its free RIGHT end, touching a fixed contact below.
  Bottom layer (mustard) expands more -> when hot the strip curves UP (free end rises, screen y smaller) -> open.
- BIG FUSE, cut away, horizontal: closed can on the LEFT end (left lead crimped to it), pellet against that end,
  sliding contact (star) pressed against the tip of the RIGHT lead, spring squeezed between the contact and the
  ceramic bushing (right). Melt -> contact slides LEFT, away from the lead tip -> gap.
"""
import math, cairo
from cogwise.style import *

META = dict(
    slug="hair-dryer-fuse",
    title="Your hair dryer can only overheat once 🔥 #Shorts",
    description=("A tiny thermal fuse hides behind the heater. When it gets too hot, a pellet inside melts and the "
                 "circuit opens for good.\n\n#Shorts #howthingswork #hairdryer #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "hairdryer", "appliances", "engineering", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Thermal_cutoff",
        "https://nteinc.com/circuit_protect/axial-lead-thermal-cutoff.php",
        "https://www.globalspec.com/learnmore/electrical_electronic_components/electrical_distribution_protection_equipment/thermal_cutoffs_thermal_protectors",
        "https://fixitclub.com/small-appliances-repairs/hair-dryer-repair/",
    ],
)

BEATS = [
    dict(dur=4.9, title="ONLY ONCE", caption="Your hair dryer can overheat exactly once. Then it never turns on again."),
    dict(dur=4.1, title="THE SECRET", caption="The secret: a tiny thermal fuse that's built to melt."),
    dict(dur=4.8, title="THE HEATER", caption="Inside, a fan pushes air across a coil of wire glowing red-hot."),
    dict(dur=5.3, title="1 · THERMOSTAT", caption="Block the air, and a bimetal strip bends away and cuts the power."),
    dict(dur=4.9, title="IT RESETS", caption="When it cools down, the strip snaps back. The dryer works again."),
    dict(dur=5.6, title="2 · THERMAL FUSE", caption="Right behind it, wired in line, sits a little metal can: the thermal fuse."),
    dict(dur=5.0, title="INSIDE THE CAN", caption="Inside, a solid pellet holds a spring squeezed against a sliding contact."),
    dict(dur=4.2, title="THE MELT", caption="At its rated temperature, the pellet melts like candle wax."),
    dict(dur=5.0, title="OPEN FOR GOOD", caption="The spring pushes the contact away. The circuit is open, for good."),
    dict(dur=5.6, title=None, caption="It only acts if the thermostat fails, for example when its contacts weld shut.", card='weld'),
    dict(dur=6.2, title="THE SACRIFICE", caption="Then nothing stops the heat. So the fuse kills the dryer before a fire can start."),
    dict(dur=5.2, title="ONE TIME ONLY", caption="A dead dryer often means one blown fuse: one overheat, on purpose."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.05, B(j if j is not None else i + 1), f)

BODY = hexc('#8fcfc8'); BODY_D = hexc('#5fa9a2'); MICA = hexc('#efe0b0')
METAL = hexc('#cfd3d6'); METAL_D = hexc('#9aa1a6'); COPPER = hexc('#c9773a')
PELLET = MUSTARD; CERAMIC = WHITE; LINT = hexc('#b9b2a8')

def rnd(i, k=0):
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return x - math.floor(x)

# ---------------------------------------------------------------- dryer geometry
BX0, BX1, BY0, BY1 = 140.0, 830.0, 560.0, 820.0       # barrel (cut away)
CY = (BY0 + BY1) / 2                                    # 690
NOZ = [(830, 575), (960, 615), (960, 765), (830, 805)]  # nozzle (air out to the RIGHT)
FAN_X = 275.0
COIL_X0, COIL_X1 = 420.0, 780.0
THERMO = (500.0, 605.0)                                 # bimetal thermostat on top of the heater
FUSE = (655.0, 606.0)                                   # fuse centre on top of the heater
WIRE = [(345, 1265), (370, 1000), (395, 830), (420, 640), (470, 618), (530, 618), (610, 606),
        (700, 606), (760, 618), (780, 650)]             # cord -> handle -> thermostat -> fuse -> coil

def poly(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)

def path_pt(pts, u):
    L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + math.dist(a, b))
    d = u * L[-1]
    for i in range(len(pts) - 1):
        if d <= L[i + 1]:
            k = (d - L[i]) / max(1e-6, L[i + 1] - L[i])
            return lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)
    return pts[-1]

def heat_col(h):
    """coil colour: 0 = cold ink, 1 = red-hot, 1.5 = overheating (orange-yellow)."""
    if h <= 1: return lerpc(INK2, RED, h)
    return lerpc(RED, MUSTARD, clamp(h - 1, 0, 1) * 2)

def mini_fuse(ctx, x, y, a, melted=0.0, s=1.0):
    """small fuse can on top of the heater (axial, horizontal)."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -32, -13, 64, 26, 9); fill_stroke(ctx, METAL, lw=3.5, alpha=a)
    ctx.rectangle(20, -13, 12, 26); setc(ctx, CERAMIC, a); ctx.fill()
    if melted > 0:
        ctx.rectangle(-28, 4, 50 * melted, 6); setc(ctx, PELLET, a); ctx.fill()
    ctx.restore()

def dryer(ctx, t, a, power, air, heat, blocked=0.0, thermo_open=0.0, fuse_melt=0.0):
    if a <= 0: return
    # handle (hangs DOWN under the barrel)
    ctx.move_to(300, 800); ctx.line_to(450, 800); ctx.line_to(420, 1270); ctx.line_to(300, 1270); ctx.close_path()
    fill_stroke(ctx, BODY, lw=5, alpha=a)
    rrect(ctx, 400, 900, 30, 70, 10); fill_stroke(ctx, MUSTARD if power > 0.5 else FILL3, lw=3, alpha=a)  # switch
    # cord
    ctx.move_to(350, 1270); ctx.curve_to(350, 1360, 460, 1380, 560, 1440); setc(ctx, INK, a); ctx.set_line_width(9); ctx.stroke()
    # nozzle
    poly(ctx, NOZ); ctx.close_path(); fill_stroke(ctx, BODY_D, lw=5, alpha=a)
    # barrel outer shell + cut-away interior
    rrect(ctx, BX0, BY0, BX1 - BX0, BY1 - BY0, 40); fill_stroke(ctx, BODY, lw=5, alpha=a)
    rrect(ctx, BX0 + 22, BY0 + 22, BX1 - BX0 - 22, BY1 - BY0 - 44, 22); fill_stroke(ctx, PAPER, INK2, lw=3, alpha=a)
    ctx.rectangle(830, 595, 120, 150); setc(ctx, PAPER, a); ctx.fill()
    # rear grille (air comes IN here, on the LEFT)
    for k in range(7):
        y = BY0 + 45 + k * 28
        ctx.move_to(BX0 + 4, y); ctx.line_to(BX0 + 30, y)
    setc(ctx, INK, a); ctx.set_line_width(6); ctx.stroke()
    # motor + fan (fan seen from the side: blades as rotating spokes)
    rrect(ctx, 185, 650, 55, 80, 10); fill_stroke(ctx, METAL_D, lw=4, alpha=a)
    rot = FAN_ROT[0]
    for k in range(4):
        an = rot + k * math.pi / 2
        yy = CY + 100 * math.sin(an); ww = 6 + 14 * abs(math.cos(an))
        ctx.move_to(FAN_X - ww, CY); ctx.line_to(FAN_X - ww * 0.6, yy); ctx.line_to(FAN_X + ww * 0.6, yy); ctx.line_to(FAN_X + ww, CY)
        ctx.close_path(); fill_stroke(ctx, FILL3, lw=3, alpha=a)
    ctx.arc(FAN_X, CY, 14, 0, 2 * math.pi); fill_stroke(ctx, METAL_D, lw=3, alpha=a)
    # heater: mica board + coil spiral
    ctx.rectangle(COIL_X0, CY - 6, COIL_X1 - COIL_X0, 12); fill_stroke(ctx, MICA, lw=3, alpha=a)
    hc = heat_col(heat * power)
    n = 22
    for k in range(n):
        x = lerp(COIL_X0 + 8, COIL_X1 - 8, k / (n - 1))
        ctx.save(); ctx.translate(x, CY); ctx.scale(9, 62); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
        setc(ctx, hc, a); ctx.set_line_width(5); ctx.stroke()
    if heat * power > 0.3:
        g = clamp(heat * power - 0.3)
        rrect(ctx, COIL_X0 - 10, CY - 80, COIL_X1 - COIL_X0 + 20, 160, 30); setc(ctx, RED if heat < 1.1 else MUSTARD, a * 0.12 * g); ctx.fill()
    # wiring (series): cord -> switch -> thermostat -> fuse -> coil
    poly(ctx, WIRE); setc(ctx, COPPER, a); ctx.set_line_width(4); ctx.stroke()
    # thermostat (small bimetal block)
    tx, ty = THERMO
    rrect(ctx, tx - 34, ty - 12, 68, 24, 6); fill_stroke(ctx, FILL2, lw=3, alpha=a)
    lift = 10 * thermo_open
    ctx.move_to(tx - 26, ty - 2); ctx.line_to(tx + 26, ty - 2 - lift); setc(ctx, MUSTARD, a); ctx.set_line_width(5); ctx.stroke()
    mini_fuse(ctx, FUSE[0], FUSE[1], a, fuse_melt)
    # air particles: LEFT -> RIGHT
    if air > 0.02:
        for k in range(26):
            lane = 610 + 160 * rnd(k, 1)
            u = (rnd(k, 2) + t * 0.55 * air) % 1.0
            x = lerp(BX0 + 40, 1010, u)
            if FAN_X - 25 < x < FAN_X + 25: continue
            col = lerpc(TEAL, RED, clamp((x - COIL_X0) / (COIL_X1 - COIL_X0)) * heat * power)
            aa = a * air * (1 if x < 960 else clamp((1010 - x) / 50))
            straight_arrow(ctx, x - 26, lane, x, lane, col, aa, lw=4, head=7)
    if air > 0.3 and heat * power > 0.5:
        for k, y in enumerate((640, 690, 740)):
            wavy_arrow(ctx, 975, y, 1060, y, t + k, RED, a * air * 0.9, amp=6, wl=30, lw=5, head=11)
    # intake blocked (lint / towel)
    if blocked > 0:
        ctx.save(); ctx.translate(BX0 - 70 * (1 - blocked), 0)
        ctx.move_to(BX0 - 30, BY0 + 15)
        for j in range(12):
            ctx.line_to(BX0 - 30 + (8 if j % 2 else -6), BY0 + 15 + j * 21)
        ctx.line_to(BX0 + 34, BY1 - 15)
        for j in range(12):
            ctx.line_to(BX0 + 34 + (6 if j % 2 else -6), BY1 - 15 - j * 21)
        ctx.close_path(); fill_stroke(ctx, LINT, INK2, lw=3, alpha=a * blocked)
        ctx.restore()

FAN_ROT = [0.0]

# ---------------------------------------------------------------- bimetal loupe
LP = (735.0, 1120.0); LPR = 190.0

def loupe_frame(ctx, a, target, label):
    cx, cy = LP
    ctx.move_to(cx - LPR * 0.6, cy - LPR * 0.8); ctx.line_to(*target)
    setc(ctx, INK2, a); ctx.set_line_width(3); ctx.set_dash([10, 8]); ctx.stroke(); ctx.set_dash([])
    ctx.arc(cx, cy, LPR, 0, 2 * math.pi); setc(ctx, CREAM, 0.98 * a); ctx.fill()
    if label: text_c(ctx, label, cx, cy + LPR + 40, 22, INK2, True, 1.5, a)

def bimetal(ctx, cx, cy, s, a, bend, welded=False, strain=0.0):
    """strip fixed at the LEFT, free end RIGHT; bend 0..1 curves it UP (y smaller). Bottom layer expands more."""
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    ctx.rectangle(-170, -40, 50, 80); fill_stroke(ctx, FILL3, lw=4, alpha=a)                 # anchor (left)
    L = 260.0
    if welded: bend = 0.0
    lift = 70 * bend + 8 * strain * math.sin(cx + 0) * 0          # the free end rises by 'lift'
    def yc(u): return -lift * u * u                                   # curve up toward the free end
    for layer, col, off in ((0, METAL_D, -9), (1, MUSTARD, 9)):       # top = steel, bottom = expands more
        ctx.move_to(-120, off - 9)
        for j in range(1, 21):
            u = j / 20; ctx.line_to(-120 + L * u, yc(u) + off - 9)
        for j in range(20, -1, -1):
            u = j / 20; ctx.line_to(-120 + L * u, yc(u) + off + 9)
        ctx.close_path(); fill_stroke(ctx, col, lw=3, alpha=a)
    ex, ey = -120 + L, yc(1.0) + 18                                   # moving contact under the free end
    ctx.arc(ex - 12, ey + 8, 12, 0, 2 * math.pi); fill_stroke(ctx, COPPER, lw=3, alpha=a)
    ctx.rectangle(ex - 40, 66, 56, 26); fill_stroke(ctx, FILL3, lw=3, alpha=a)                 # fixed contact base
    ctx.arc(ex - 12, 54, 12, 0, 2 * math.pi); fill_stroke(ctx, COPPER, lw=3, alpha=a)          # fixed contact
    if welded:
        ctx.save(); ctx.translate(ex - 12, 40); ctx.scale(22, 16); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
        fill_stroke(ctx, hexc('#6f6a74'), lw=3, alpha=a)
    ctx.restore()
    return (cx + s * (ex - 12), cy + s * (ey + 8))

def loupe_thermo(ctx, t, a, bend, heat):
    if a <= 0: return
    loupe_frame(ctx, a, (THERMO[0] + 20, THERMO[1] + 16), "THERMOSTAT, ZOOMED")
    cx, cy = LP
    ctx.save(); ctx.arc(cx, cy, LPR - 4, 0, 2 * math.pi); ctx.clip()
    bimetal(ctx, cx + 10, cy + 10, 0.62, a, bend)
    if heat > 0.6:
        for k in range(3):
            wavy_arrow(ctx, cx - 80 + 70 * k, cy + 150, cx - 80 + 70 * k, cy + 70, t + k, RED, a * clamp(heat - 0.6) * 2, amp=6, wl=26, lw=4, head=9)
    ctx.restore()
    ctx.arc(cx, cy, LPR, 0, 2 * math.pi); setc(ctx, INK, a); ctx.set_line_width(9); ctx.stroke()

# ---------------------------------------------------------------- the big fuse (cut away)
def big_fuse(ctx, cx, cy, s, a, melt, t, current=0.0):
    """melt 0 solid .. 1 melted + contact moved away. Returns nothing."""
    if a <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s); ctx.translate(-540, -900)
    m1 = clamp(melt / 0.6)                   # pellet turning liquid
    mv = ease(clamp((melt - 0.45) / 0.55))   # contact sliding away
    # leads
    ctx.move_to(60, 900); ctx.line_to(230, 900); setc(ctx, METAL_D, a); ctx.set_line_width(14); ctx.stroke()
    ctx.move_to(855, 900); ctx.line_to(1020, 900); setc(ctx, METAL_D, a); ctx.set_line_width(14); ctx.stroke()
    # can (closed LEFT end, crimped to the left lead), cut open
    rrect(ctx, 220, 815, 640, 170, 22); fill_stroke(ctx, METAL, lw=5, alpha=a)
    ctx.rectangle(240, 838, 600, 124); setc(ctx, hexc('#f6efe0'), a); ctx.fill()
    # ceramic bushing (right) + lead going in
    ctx.rectangle(790, 832, 62, 136); fill_stroke(ctx, CERAMIC, lw=4, alpha=a)
    tip = 600.0
    ctx.move_to(tip, 900); ctx.line_to(855, 900); setc(ctx, METAL_D, a); ctx.set_line_width(14); ctx.stroke()
    # contact position (left face xc0 .. right face xc1)
    xc1 = lerp(tip, 345, mv); xc0 = xc1 - 30
    # pellet: solid block -> puddle
    pw = lerp(xc0 - 248, 0, m1)
    if pw > 2:
        rrect(ctx, 246, 846 + 40 * m1, pw, 108 - 40 * m1, 10); fill_stroke(ctx, PELLET, lw=4, alpha=a)
    if m1 > 0:
        ph = 6 + 18 * m1; pl = lerp(0, 420, m1)
        ctx.move_to(242, 962); ctx.line_to(242, 962 - ph)
        for j in range(9):
            ctx.line_to(242 + pl * (j + 1) / 9, 962 - ph * (1 - 0.5 * ((j + 1) / 9) ** 2) + 3 * math.sin(j * 1.7 + t * 3))
        ctx.line_to(242 + pl, 962); ctx.close_path(); setc(ctx, PELLET, a); ctx.fill()
    # sliding contact (star contact touching the can wall)
    ctx.rectangle(xc0, 842, 30, 116); fill_stroke(ctx, COPPER, lw=4, alpha=a)
    for y in (842, 958):
        ctx.move_to(xc0 - 6, y); ctx.line_to(xc1 + 6, y); setc(ctx, COPPER, a); ctx.set_line_width(6); ctx.stroke()
    # spring squeezed between contact (left) and bushing (right), around the lead
    sx0, sx1 = xc1 + 4, 788.0
    nco = 9
    ctx.move_to(sx0, 900)
    for j in range(nco * 2 + 1):
        x = lerp(sx0, sx1, j / (nco * 2)); y = 900 + (-46 if j % 2 else 46)
        ctx.line_to(x, y)
    ctx.line_to(sx1, 900); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    ctx.move_to(tip, 900); ctx.line_to(790, 900); setc(ctx, METAL_D, a); ctx.set_line_width(14); ctx.stroke()
    ctx.arc(tip, 900, 13, 0, 2 * math.pi); fill_stroke(ctx, COPPER, lw=3, alpha=a)          # lead tip (fixed)
    # current path (dots): left lead -> can wall -> contact -> lead tip -> right lead
    if current > 0 and mv < 0.05:
        pts = [(60, 900), (230, 900), (230, 830), (xc0 + 15, 830), (xc0 + 15, 900), (tip, 900), (1020, 900)]
        for k in range(14):
            u = (k / 14 + t * 0.35) % 1.0
            x, y = path_pt(pts, u)
            ctx.arc(x, y, 7, 0, 2 * math.pi); setc(ctx, MUSTARD, a * current); ctx.fill()
    ctx.restore()

def fuse_xy(cx, cy, s, x, y): return (cx + (x - 540) * s, cy + (y - 900) * s)

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['dryer'] = max(win(t, -1, B(6) + 0.1, 0.3), win(t, B(9) - 0.1, B(11) + 0.1, 0.3))
    s['fuse_big'] = win(t, B(6), B(9) + 0.1, 0.3)
    s['recap'] = win(t, B(11), B(12) + 4, 0.3)
    return s

def dryer_params(t):
    """power, air, heat, blocked, thermo_open, fuse_melt"""
    if t < B(1):
        if t < 2.7: return 1, 1, 1, 0, 0, 0
        k = clamp((t - 2.7) / 0.5)
        if t < 3.2: return 1, 1 - k, 1 + 0.5 * k, 0, 0, k
        return 0, 0, 0, 0, 0, 1.0
    if t < B(2): return 0, 0, 0, 0, 0, 1.0
    if t < B(3): return 1, ease(clamp((t - B(2)) / 0.6)), ease(clamp((t - B(2)) / 1.0)), 0, 0, 0
    if t < B(4):
        bl = ease(clamp((t - B(3) - 0.3) / 0.6))
        heat = 1 + 0.4 * clamp((t - B(3) - 0.8) / 1.6)
        op = ease(clamp((t - B(3) - 2.6) / 0.5))
        return 1 - op, 1 - bl * 0.92, heat, bl, op, 0
    if t < B(5):
        bl = 1 - ease(clamp((t - B(4) - 0.2) / 0.6))
        back = ease(clamp((t - B(4) - 2.0) / 0.3))
        heat = 1.4 - 0.4 * clamp((t - B(4)) / 1.5)
        return back, 0.08 + 0.92 * (1 - bl), heat, bl, 1 - back, 0
    if t < B(9): return 1, 1, 1, 0, 0, 0
    if t < B(10): return 1, 0.08, 1.4, 1, 0, 0
    # sacrifice: blocked, thermostat stuck, heat climbs, fuse melts, everything stops
    hk = clamp((t - B(10)) / 2.6)
    melt = ease(clamp((t - B(10) - 2.4) / 1.0))
    off = clamp((t - B(10) - 3.2) / 0.4)
    if t >= B(11): return 0, 0, 0, 1, 0, 1.0
    return 1 - off, 0.08 * (1 - off), 1.4 + 0.2 * hk, 1, 0, melt

def draw(ctx, t, E):
    s = state(t)
    p, air, heat, bl, op, fm = dryer_params(t)
    FAN_ROT[0] = t * 14 * max(air, 0.0)
    a = s['dryer']
    if a > 0:
        dryer(ctx, t, a, p, air, heat, bl, op, fm)
        # hook: the fuse, before 2 s
        if t < B(1) + 0.1:
            k = clamp((t - 0.5) / 0.3)
            highlight(ctx, FUSE[0], FUSE[1], 58, 40, RED, a * k, t)
            tag(ctx, "THIS PART MELTS ONCE", 640, 470, RED, a * k, 28)
            if t > 3.3:
                tag(ctx, "DEAD", 560, 1000, INK, a * clamp((t - 3.3) / 0.3), 32)
        if bw(t, 1) > 0:
            k = bw(t, 1)
            highlight(ctx, FUSE[0], FUSE[1], 58, 40, RED, a * k, t)
            tag(ctx, "THERMAL FUSE", 640, 470, RED, a * k, 28)
            if t > B(1) + 1.0:
                kk = clamp((t - B(1) - 1.0) / 0.4)
                big_fuse(ctx, 735, 1110, 0.42, a * k * kk, 0.0, t)
                tag(ctx, "BUILT TO MELT", 735, 1250, RED, a * k * kk, 26)
        ga = bw(t, 2)
        if ga > 0:
            tag(ctx, "FAN", FAN_X, 470, TEAL, ga * clamp((t - B(2) - 0.4) / 0.3), 26)
            tag(ctx, "HOT COIL", 600, 900, RED, ga * clamp((t - B(2) - 1.8) / 0.3), 26)
            tag(ctx, "AIR IN", 150, 900, TEAL, ga * clamp((t - B(2) - 0.4) / 0.3), 22)
        ta = win(t, B(3) + 0.05, B(5), 0.35)
        if ta > 0:
            highlight(ctx, THERMO[0], THERMO[1], 55, 36, MUSTARD, ta, t)
            tag(ctx, "1 · THERMOSTAT", 450, 470, INK, ta, 26)
            if bw(t, 3) > 0 and t > B(3) + 0.6:
                tag(ctx, "BLOCKED", 150, 900, RED, bw(t, 3) * clamp((t - B(3) - 0.6) / 0.3), 24)
            loupe_thermo(ctx, t, ta, op, heat)
            if op > 0.5 and t < B(4) + 2.0:
                tag(ctx, "POWER OFF", LP[0], LP[1] - LPR - 30, RED, ta * clamp((op - 0.5) * 3), 24)
            if t > B(4) + 2.1:
                tag(ctx, "RESET ✓", LP[0], LP[1] - LPR - 30, TEAL, ta * clamp((t - B(4) - 2.1) / 0.3), 26)
        fa = bw(t, 5)
        if fa > 0:
            highlight(ctx, FUSE[0], FUSE[1], 58, 40, RED, fa, t)
            tag(ctx, "2 · THERMAL FUSE", 690, 470, RED, fa, 26)
            tag(ctx, "IN LINE", 470, 1060, INK2, fa * clamp((t - B(5) - 1.0) / 0.3), 22)
            for k in range(18):
                u = (k / 18 + t * 0.3) % 1.0
                x, y = path_pt(WIRE, u)
                ctx.arc(x, y, 7, 0, 2 * math.pi); setc(ctx, MUSTARD, fa); ctx.fill()
            if t > B(5) + 1.6:
                kk = clamp((t - B(5) - 1.6) / 0.4)
                big_fuse(ctx, 735, 1110, 0.42, fa * kk, 0.0, t)
        # beat 9 (behind the card) + 10: thermostat stuck
        sa = win(t, B(9), B(11), 0.35)
        if sa > 0:
            tag(ctx, "STUCK SHUT", 450, 470, RED, sa, 26)
            highlight(ctx, THERMO[0], THERMO[1], 55, 36, RED, sa, t)
        xa = bw(t, 10)
        if xa > 0:
            thermometer(ctx, 950, 1250, clamp(0.5 + 0.5 * (t - B(10)) / 2.6), xa, RED)
            highlight(ctx, FUSE[0], FUSE[1], 58, 40, RED, xa, t)
            loupe_frame(ctx, xa, (FUSE[0] + 10, FUSE[1] + 18), "THE FUSE, ZOOMED")
            cx, cy = LP
            ctx.save(); ctx.arc(cx, cy, LPR - 4, 0, 2 * math.pi); ctx.clip()
            big_fuse(ctx, cx, cy, 0.42, xa, fm, t, current=1.0)
            ctx.restore()
            ctx.arc(cx, cy, LPR, 0, 2 * math.pi); setc(ctx, INK, xa); ctx.set_line_width(9); ctx.stroke()
            if t > B(10) + 3.6:
                tag(ctx, "NO FIRE", 560, 1000, TEAL, xa * clamp((t - B(10) - 3.6) / 0.3), 32)
    # big fuse scene (beats 6-8)
    a = s['fuse_big']
    if a > 0:
        melt = 0.0
        if t > B(7): melt = 0.6 * ease(clamp((t - B(7) - 0.6) / 2.6))
        if t > B(8): melt = 0.6 + 0.4 * clamp((t - B(8) - 0.2) / 1.6)
        cur = 1.0 if t < B(8) + 0.9 else 0.0
        big_fuse(ctx, 540, 900, 1.0, a, melt, t, current=cur)
        text_c(ctx, "THERMAL FUSE, CUT OPEN", 540, 720, 26, INK2, True, 2, a)
        la = bw(t, 6)
        if la > 0:
            tag(ctx, "PELLET", 340, 1080, MUSTARD, la * clamp((t - B(6) - 0.4) / 0.3), 26)
            straight_arrow(ctx, 340, 1050, 340, 975, MUSTARD, la * clamp((t - B(6) - 0.4) / 0.3), lw=4, head=9)
            tag(ctx, "SPRING", 700, 1080, INK, la * clamp((t - B(6) - 1.6) / 0.3), 26)
            straight_arrow(ctx, 700, 1050, 700, 960, INK, la * clamp((t - B(6) - 1.6) / 0.3), lw=4, head=9)
            tag(ctx, "SLIDING CONTACT", 560, 1180, COPPER, la * clamp((t - B(6) - 2.8) / 0.3), 24)
            straight_arrow(ctx, 590, 1150, 590, 975, COPPER, la * clamp((t - B(6) - 2.8) / 0.3), lw=4, head=9)
            tag(ctx, "CURRENT FLOWS", 540, 1300, TEAL, la * clamp((t - B(6) - 3.6) / 0.3), 24)
        ma = bw(t, 7)
        if ma > 0:
            thermometer(ctx, 950, 1260, clamp(0.3 + 0.7 * (t - B(7)) / 2.4), ma, RED)
            for k in range(4):
                x = 300 + 120 * k
                wavy_arrow(ctx, x, 1160, x, 1000, t + k, RED, ma, amp=8, wl=32, lw=5, head=12)
            if t > B(7) + 1.8:
                tag(ctx, "MELTS", 340, 1250, RED, ma * clamp((t - B(7) - 1.8) / 0.3), 28)
        oa = bw(t, 8)
        if oa > 0:
            mv = ease(clamp((melt - 0.45) / 0.55))
            if mv > 0.2:
                straight_arrow(ctx, 620, 1040, 400, 1040, RED, oa * clamp(mv * 2), lw=7, head=14)
                text_c(ctx, "PUSHED AWAY", 510, 1095, 24, RED, True, 1.5, oa * clamp(mv * 2))
            if mv > 0.8:
                k = clamp((mv - 0.8) * 5)
                highlight(ctx, 475, 900, 110, 70, RED, oa * k, t)
                tag(ctx, "GAP = NO CURRENT", 540, 1250, RED, oa * k, 26)
                tag(ctx, "FOREVER", 540, 1340, INK, oa * clamp((t - B(8) - 2.6) / 0.3), 30)
    # recap: before / after
    a = s['recap']
    if a > 0:
        big_fuse(ctx, 540, 640, 0.78, a, 0.0, t, current=1.0)
        big_fuse(ctx, 540, 1110, 0.78, a, 1.0, t)
        tag(ctx, "BEFORE", 540, 500, TEAL, a, 28)
        tag(ctx, "AFTER ONE OVERHEAT", 540, 970, RED, a * clamp((t - B(11) - 0.8) / 0.3), 28)
        if t > B(11) + 2.4:
            text_c(ctx, "ON PURPOSE", 540, 1330, 52, INK, True, 3, a * clamp((t - B(11) - 2.4) / 0.4))

def draw_set(ctx):
    pass

ANCHOR = (540, 1450)

SFX = [(0.5, 'pop'), (2.7, 'click'), (3.3, 'pop'), (B(1) + 1.0, 'pop'), (B(2) + 0.4, 'pop'), (B(2) + 1.8, 'pop'),
       (B(3) + 0.6, 'pop'), (B(3) + 2.6, 'click'), (B(4) + 2.0, 'click'), (B(5) + 0.1, 'pop'), (B(6) + 0.4, 'pop'),
       (B(6) + 1.6, 'pop'), (B(6) + 2.8, 'pop'), (B(7) + 1.8, 'pop'), (B(8) + 1.0, 'click'), (B(8) + 1.9, 'pop'),
       (B(10) + 3.2, 'click'), (B(10) + 3.6, 'pop'), (B(11) + 0.8, 'pop'), (B(11) + 2.4, 'pop')]
HUM = []

# ---------------------------------------------------------------- card
def card_weld(ctx, t, lt, a):
    card_frame(ctx, "IF THE THERMOSTAT FAILS", a, "CONTACTS WELDED: THE STRIP CAN'T OPEN", RED)
    # left: normal (opens when hot) ; right: welded (stays shut)
    bimetal(ctx, 330, 390, 0.52, a, 1.0 * ease(clamp((lt - 0.4) / 0.8)))
    text_c(ctx, "NORMAL: OPENS", 330, 520, 24, TEAL, True, 1, a)
    bimetal(ctx, 760, 390, 0.52, a, 0.0, welded=True)
    text_c(ctx, "WELDED: STAYS SHUT", 760, 520, 24, RED, True, 1, a)
    if lt > 1.2:
        for k in range(3):
            wavy_arrow(ctx, 700 + 50 * k, 300, 700 + 50 * k, 250, t + k, RED, a * clamp((lt - 1.2) / 0.3), amp=5, wl=20, lw=4, head=8)

CARDS = {'weld': card_weld}
