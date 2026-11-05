"""Cogwise episode: How a universal motor works (series-wound, commutator, carbon brushes)."""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="universal-motor",
    title="Why your drill sparks: the universal motor ⚡",
    description=("Carbon brushes, a commutator and two windings in series: why the motor in your drill runs on AC or DC.\n\n"
                 "#Shorts #howthingswork #electricmotor #engineering #appliancerepair #cogwise"),
    hashtags=["Shorts", "howthingswork", "electricmotor", "engineering", "appliancerepair", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Universal_motor",
        "https://www.electricaleasy.com/2014/02/universal-motor-construction-working.html",
        "https://en.wikipedia.org/wiki/Commutator_(electric)",
        "https://en.wikipedia.org/wiki/Eddy_current",
    ],
)

BEATS = [
    dict(dur=4.5, title="WHY DOES IT SPARK?", caption="See the blue sparks through your drill's vents? Two little blocks of carbon are making them."),
    dict(dur=6.0, title="CARBON BRUSHES", caption="They're carbon brushes, spring-loaded in their holders, feeding a series-wound universal motor."),
    dict(dur=6.0, title="1 · STATOR", caption="The stator: two field windings around laminated steel poles, making a north and a south pole."),
    dict(dur=5.5, title=None, caption="AC drives eddy currents through solid iron and heats it. Thin insulated sheets block them.", card='lam'),
    dict(dur=5.0, title="2 · ARMATURE", caption="Inside spins the armature: a slotted, laminated core carrying copper coils."),
    dict(dur=5.5, title="3 · COMMUTATOR", caption="Every coil ends on copper segments of the commutator, insulated from each other by mica."),
    dict(dur=5.5, title="CURRENT PATH", caption="Current enters through one brush, flows through the armature conductors, and leaves by the other."),
    dict(dur=5.0, title="4 · TORQUE", caption="The armature field sits at ninety degrees to the stator field. That's where torque peaks."),
    dict(dur=5.5, title="COMMUTATION", caption="As it turns, the brushes ride onto the next segments, so the armature field never catches up."),
    dict(dur=5.5, title=None, caption="Each commutation breaks the current in a coil. Its inductance fights back with an arc: the blue spark.", card='arc'),
    dict(dur=6.0, title=None, caption="On AC, current flips a hundred times a second. In series, field and armature flip together.", card='ac'),
    dict(dur=5.5, title="NO LOAD = RUNAWAY", caption="With no load, the field weakens and speed soars past twenty thousand rpm."),
    dict(dur=5.0, title="5 · SUPPRESSION CAPACITOR", caption="All that arcing makes radio noise, so a suppression capacitor sits across the supply."),
    dict(dur=5.0, title="SERIES + COMMUTATOR = AC OR DC", caption="Series field, laminated iron, commutator and brushes: that's why it runs on AC or DC."),
    dict(dur=5.5, title="PRO TIP", caption="Tech tip: heavy sparking or a burning smell? Check brush length, and replace them in pairs."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
CX, CY = 540, 900
R_YO, R_YI = 455, 400          # stator yoke
R_SHOE = 300                   # pole face (air gap inside)
R_ARM, R_ARM_SLOT = 285, 250   # armature outer radius, conductor radius
R_COM = 125                    # commutator radius (front plane)
NSEG = 12
STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab'); STEEL_L = hexc('#e3e7ea')
COPPER = hexc('#c8743a'); COPPER_L = hexc('#e9a36a'); MICA = hexc('#6b4d10')
CARBON = hexc('#3a3740'); SPARK = hexc('#5aa9ff'); SPARK_W = hexc('#dff0ff')
NCOL = RED; SCOL = hexc('#3b7fd0'); GREEN = hexc('#4c9d6b')

def P(r, a):
    return CX + r * math.cos(a), CY + r * math.sin(a)

# ---- speed and angle (screen angles: +ve = CLOCKWISE on screen, y points down)
def omega(t):
    w = 0.55
    w = lerp(w, 0.22, bw(t, 8, 9, 0.6))                            # slow-mo for commutation
    w = lerp(w, 7.0, ease((t - B(11) - 0.4) / 2.5) * (1 - ease((t - B(12)) / 0.8)))  # runaway
    return w

def theta(t):
    n = 240; dt = t / n if t > 0 else 0; s = 0.0
    for i in range(n): s += omega((i + 0.5) * dt) * dt
    return s

def polarity(t):
    """+1: left pole N, right pole S, armature N on top. -1: everything flipped (AC half-cycle)."""
    if B(10) + 0.6 < t < B(11) - 0.2:
        return 1 if math.sin(2 * math.pi * (t - B(10) - 0.6) / 2.2) >= 0 else -1
    return 1

# ---------------------------------------------------------------- drawing
def draw_stator(ctx, t, st):
    # yoke ring
    ctx.arc(CX, CY, R_YO, 0, 2*math.pi); ctx.new_sub_path(); ctx.arc_negative(CX, CY, R_YI, 2*math.pi, 0)
    setc(ctx, STEEL); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # lamination hint lines on the yoke
    for k in range(48):
        a = 2 * math.pi * k / 48
        ctx.move_to(*P(R_YI + 8, a)); ctx.line_to(*P(R_YO - 8, a)); setc(ctx, STEEL_D, 0.6); ctx.set_line_width(2); ctx.stroke()
    pol = st['pol']
    for side in (-1, 1):          # -1 = left pole, +1 = right pole
        a0 = 0 if side > 0 else math.pi
        # pole body (rectangle) + shoe (arc)
        hw = 80
        x_in = CX + side * (R_SHOE + 25); x_out = CX + side * (R_YI + 6)
        ctx.rectangle(min(x_in, x_out), CY - hw, abs(x_out - x_in), 2 * hw)
        setc(ctx, STEEL); ctx.fill()
        sa = math.radians(52)
        ctx.arc(CX, CY, R_SHOE + 32, a0 - sa, a0 + sa); ctx.arc_negative(CX, CY, R_SHOE, a0 + sa, a0 - sa); ctx.close_path()
        setc(ctx, STEEL); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
        ctx.move_to(x_in, CY - hw); ctx.line_to(x_out, CY - hw); ctx.move_to(x_in, CY + hw); ctx.line_to(x_out, CY + hw)
        setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
        # field winding: copper bundles above and below the pole body
        for vs in (-1, 1):
            x0 = min(x_in, x_out) + 8; w = abs(x_out - x_in) - 16
            y0 = CY + vs * hw if vs > 0 else CY - hw - 62
            rrect(ctx, x0, y0, w, 62, 12); fill_stroke(ctx, lerpc(COPPER, COPPER_L, 0.5 * st['h_field']), lw=4)
            for k in range(1, 6):
                xx = x0 + w * k / 6
                ctx.move_to(xx, y0 + 6); ctx.line_to(xx, y0 + 56); setc(ctx, INK, 0.35); ctx.set_line_width(2); ctx.stroke()
        # pole letter
        is_n = (side < 0) == (pol > 0)
        col = NCOL if is_n else SCOL
        x_lab = CX + side * 360
        ctx.arc(x_lab, CY, 34, 0, 2*math.pi); fill_stroke(ctx, col, lw=4, alpha=st['poles'])
        text_c(ctx, "N" if is_n else "S", x_lab, CY + 15, 40, WHITE, True, 0, st['poles'])

def draw_armature(ctx, t, st):
    th = st['th']
    # laminated core with 12 open slots
    ctx.arc(CX, CY, R_ARM, 0, 2*math.pi); setc(ctx, lerpc(STEEL_L, TEAL_L, 0.35 * st['h_arm'])); ctx.fill_preserve()
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    for k in range(NSEG):
        a = th + 2 * math.pi * k / NSEG + math.pi / NSEG
        # slot (dark wedge) between teeth
        c = math.cos(a); s = math.sin(a)
        w = 22
        pts = [(R_ARM + 2, -w), (R_ARM_SLOT - 30, -w), (R_ARM_SLOT - 30, w), (R_ARM + 2, w)]
        ctx.move_to(CX + pts[0][0] * c - pts[0][1] * s, CY + pts[0][0] * s + pts[0][1] * c)
        for (r, o) in pts[1:]: ctx.line_to(CX + r * c - o * s, CY + r * s + o * c)
        ctx.close_path(); setc(ctx, PAPER); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
        # conductor in the slot
        x, y = P(R_ARM_SLOT, a)
        ctx.arc(x, y, 17, 0, 2*math.pi); fill_stroke(ctx, COPPER, lw=3)
        cur = st['cur']
        if cur > 0:
            rel = (x - CX) * st['pol']          # >0: right half (with + polarity)
            if abs(x - CX) > 32:                 # coils near the brush axis are being commutated: no symbol
                if rel > 0:                      # current INTO the screen (cross)
                    d = 9
                    ctx.move_to(x - d, y - d); ctx.line_to(x + d, y + d); ctx.move_to(x + d, y - d); ctx.line_to(x - d, y + d)
                    setc(ctx, INK, cur); ctx.set_line_width(4); ctx.stroke()
                else:                            # current OUT of the screen (dot)
                    ctx.arc(x, y, 6, 0, 2*math.pi); setc(ctx, INK, cur); ctx.fill()
    # shaft behind the commutator
    ctx.arc(CX, CY, 150, 0, 2*math.pi); setc(ctx, STEEL_D, 0.5); ctx.fill()

def draw_commutator(ctx, t, st):
    th = st['th']
    ctx.arc(CX, CY, R_COM, 0, 2*math.pi); setc(ctx, lerpc(COPPER, COPPER_L, 0.4 * st['h_com'])); ctx.fill_preserve()
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    for k in range(NSEG):
        a = th + 2 * math.pi * k / NSEG
        ctx.move_to(*P(42, a)); ctx.line_to(*P(R_COM, a)); setc(ctx, MICA); ctx.set_line_width(5); ctx.stroke()
    ctx.arc(CX, CY, 38, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=4)
    ctx.arc(CX, CY, 9, 0, 2*math.pi); setc(ctx, INK); ctx.fill()

BR_W, BR_L = 52, 78
def brush_geom(side, pull=0.0):
    """side -1 = top brush, +1 = bottom brush. returns inner (contact) y and outer y."""
    inner = CY + side * R_COM
    outer = inner + side * BR_L
    return inner + side * pull, outer + side * pull

def draw_brushes(ctx, t, st):
    for side in (-1, 1):
        pull = 0.0; wear = 0.0
        yi, yo = brush_geom(side)
        # holder (box) — front plane
        hy0 = yi + side * 18; hy1 = yo + side * 30
        rrect(ctx, CX - BR_W / 2 - 12, min(hy0, hy1), BR_W + 24, abs(hy1 - hy0), 6)
        fill_stroke(ctx, lerpc(FILL3, MUSTARD, 0.5 * st['h_br']), lw=4)
        # carbon block (possibly pulled out of the holder / worn short)
        L = BR_L * (1 - 0.55 * wear)
        b0 = yi + side * pull; b1 = b0 + side * L
        rrect(ctx, CX - BR_W / 2, min(b0, b1), BR_W, abs(b1 - b0), 5); fill_stroke(ctx, CARBON, lw=4)
        # spring (zig-zag) between block and holder end
        ys0 = b1; ys1 = hy1 - side * 4
        n = 8
        for i in range(n + 1):
            y = lerp(ys0, ys1, i / n); x = CX + (14 if i % 2 else -14) * (0 < i < n)
            (ctx.move_to if i == 0 else ctx.line_to)(x, y)
        setc(ctx, INK2); ctx.set_line_width(3); ctx.stroke()
        # pigtail lead out to the edge of the stator
        y_end = CY + side * (R_YI - 14)
        ctx.move_to(CX + 10, b1); ctx.curve_to(CX + 70, b1 + side * 30, CX + 40, y_end - side * 40, CX + 40, y_end)
        setc(ctx, COPPER); ctx.set_line_width(6); ctx.stroke()
        ctx.arc(CX + 40, y_end, 9, 0, 2*math.pi); fill_stroke(ctx, STEEL_D, lw=3)

def draw_sparks(ctx, t, st):
    a = st['spark']
    if a <= 0: return
    rnd = random.Random(int(t * 14))
    for side in (-1, 1):
        if rnd.random() < 0.25: continue
        yi, _ = brush_geom(side)
        # clockwise rotation: surface under the TOP brush moves right -> trailing edge = right;
        # under the BOTTOM brush it moves left -> trailing edge = left
        mv = 1 if side < 0 else -1
        x0 = CX + mv * BR_W / 2; y0 = yi
        for k in range(3):
            spread = rnd.uniform(0.1, 0.9)               # lift away from the commutator (outward)
            dx, dy = mv * math.cos(spread), side * math.sin(spread)
            L = rnd.uniform(20, 48)
            ctx.move_to(x0, y0)
            ctx.line_to(x0 + dx * L * 0.5 + rnd.uniform(-5, 5), y0 + dy * L * 0.5 + rnd.uniform(-5, 5))
            ctx.line_to(x0 + dx * L, y0 + dy * L)
            setc(ctx, SPARK, a); ctx.set_line_width(5); ctx.stroke()
        g = cairo.RadialGradient(x0, y0, 2, x0, y0, 42)
        g.add_color_stop_rgba(0, *SPARK_W[:3], 0.9 * a); g.add_color_stop_rgba(1, *SPARK[:3], 0)
        ctx.set_source(g); ctx.arc(x0, y0, 42, 0, 2*math.pi); ctx.fill()

def rot_arrow(ctx, r, a1, a2, color, alpha, lw=8):
    """curved arrow, clockwise on screen (angle increasing)."""
    if alpha <= 0: return
    ctx.arc(CX, CY, r, a1, a2); setc(ctx, color, alpha); ctx.set_line_width(lw); ctx.stroke()
    x, y = P(r, a2); dx, dy = -math.sin(a2), math.cos(a2)    # tangent, clockwise direction
    nx, ny = math.cos(a2), math.sin(a2); h = 20
    ctx.move_to(x + dx * h, y + dy * h); ctx.line_to(x - dx * 6 + nx * h * 0.8, y - dy * 6 + ny * h * 0.8)
    ctx.line_to(x - dx * 6 - nx * h * 0.8, y - dy * 6 - ny * h * 0.8); ctx.close_path(); setc(ctx, color, alpha); ctx.fill()

def draw_terminals(ctx, t, st):
    a = st['cap']
    x0, x1, y = 140, 300, 1390
    # supply leads + capacitor across them
    for x in (x0, x1):
        ctx.arc(x, y, 16, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=4)
    text_c(ctx, "AC IN", (x0 + x1) / 2, y + 52, 24, INK, True, 2, 1)
    if a > 0:
        ctx.move_to(x0, y - 16); ctx.line_to(x0, y - 80); ctx.line_to(206, y - 80)
        ctx.move_to(x1, y - 16); ctx.line_to(x1, y - 80); ctx.line_to(234, y - 80)
        setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        for xx in (206, 234):
            ctx.move_to(xx, y - 125); ctx.line_to(xx, y - 35); setc(ctx, TEAL, a); ctx.set_line_width(10); ctx.stroke()
        highlight(ctx, 220, y - 60, 120, 85, TEAL, st['l_cap'], t)

def draw_tacho(ctx, t, st):
    a = st['tacho']
    if a <= 0: return
    x, y, r = 900, 1350, 80
    ctx.arc(x, y, r, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=5, alpha=a)
    for k in range(9):
        ang = math.pi * (0.75 + 1.5 * k / 8)
        ctx.move_to(x + 0.8 * r * math.cos(ang), y + 0.8 * r * math.sin(ang)); ctx.line_to(x + r * math.cos(ang), y + r * math.sin(ang))
        setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    v = st['rpm'] / 30000
    ang = math.pi * (0.75 + 1.5 * clamp(v))
    ctx.move_to(x, y); ctx.line_to(x + 0.72 * r * math.cos(ang), y + 0.72 * r * math.sin(ang))
    setc(ctx, RED, a); ctx.set_line_width(6); ctx.stroke()
    text_c(ctx, "{:,} RPM".format(int(st['rpm'] / 500) * 500), x, y + r + 40, 26, RED, True, 1, a)

def draw_wear(ctx, t, st):
    a = st['wear']
    if a <= 0: return
    for x, L, lab, col in ((835, 190, "NEW", GREEN), (955, 95, "WORN", RED)):
        y1 = 560; y0 = y1 - L
        rrect(ctx, x - 32, y0, 64, L, 6); fill_stroke(ctx, CARBON, lw=4, alpha=a)
        ctx.move_to(x, y0); ctx.curve_to(x + 30, y0 - 40, x - 30, y0 - 60, x + 10, y0 - 90)
        setc(ctx, COPPER, a); ctx.set_line_width(6); ctx.stroke()
        text_c(ctx, lab, x, y1 + 40, 24, col, True, 2, a)
    # wear limit mark (same height on both)
    ym = 560 - 110
    ctx.move_to(785, ym); ctx.line_to(1005, ym); ctx.set_dash([10, 7])
    setc(ctx, RED, a); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    text_c(ctx, "WEAR LIMIT", 715, ym + 8, 22, RED, True, 1, a)

def draw_all(ctx, t, st):
    draw_stator(ctx, t, st)
    draw_armature(ctx, t, st)
    draw_commutator(ctx, t, st)
    draw_brushes(ctx, t, st)
    draw_sparks(ctx, t, st)
    draw_terminals(ctx, t, st)
    draw_tacho(ctx, t, st)
    draw_wear(ctx, t, st)
    pol = st['pol']
    # stator field: from the N pole to the S pole, straight across the armature
    if st['fstat'] > 0:
        xa, xb = (CX - 270, CX + 270) if pol > 0 else (CX + 270, CX - 270)
        straight_arrow(ctx, xa, CY, xb, CY, WHITE, st['fstat'], lw=16, head=24)
        straight_arrow(ctx, xa, CY, xb, CY, NCOL, st['fstat'], lw=8, head=18)
        tag(ctx, "STATOR FIELD", CX + (175 if pol > 0 else -175), CY + 50, NCOL, st['fstat'], 22)
    # armature field: along the brush axis, pointing to the armature's N pole
    if st['farm'] > 0:
        ya, yb = (CY + 230, CY - 230) if pol > 0 else (CY - 230, CY + 230)
        straight_arrow(ctx, CX - 70, ya, CX - 70, yb, WHITE, st['farm'], lw=16, head=24)
        straight_arrow(ctx, CX - 70, ya, CX - 70, yb, TEAL, st['farm'], lw=8, head=18)
        tag(ctx, "ARMATURE FIELD", CX - 260, CY + (-150 if pol > 0 else 150), TEAL, st['farm'], 22)
        for side, lab in ((-1, "N" if pol > 0 else "S"), (1, "S" if pol > 0 else "N")):
            col = NCOL if lab == "N" else SCOL
            px, py = CX + 75, CY + side * 180
            ctx.arc(px, py, 24, 0, 2*math.pi); fill_stroke(ctx, col, lw=3, alpha=st['farm'])
            text_c(ctx, lab, px, py + 10, 26, WHITE, True, 0, st['farm'])
    if st['ninety'] > 0:
        xx = CX - 70
        ctx.rectangle(xx, CY - 34, 34, 34); setc(ctx, WHITE, st['ninety']); ctx.fill_preserve()
        setc(ctx, INK, st['ninety']); ctx.set_line_width(4); ctx.stroke()
        tag(ctx, "90° = MAX TORQUE", CX, 1440, INK, st['ninety'], 28)
    rot_arrow(ctx, R_YO + 30, math.radians(-110), math.radians(-60), GREEN, st['rot'])
    rot_arrow(ctx, R_YO + 30, math.radians(70), math.radians(120), GREEN, st['rot'])
    # current flow dots: in at the top brush, out at the bottom brush
    if st['flow'] > 0:
        for side in (-1, 1):
            y_end = CY + side * (R_YO + 40); yi, yo = brush_geom(side); yo = yo + side * 30
            for k in range(3):
                u = (t * 0.9 + k / 3) % 1.0
                yy = lerp(y_end, yo, u) if side < 0 else lerp(yo, y_end, u)
                ctx.arc(CX + 40, yy, 10, 0, 2*math.pi); fill_stroke(ctx, MUSTARD, lw=2, alpha=st['flow'])
        ctx.move_to(CX + 40, CY - R_YI + 14); ctx.line_to(CX + 40, CY - R_YO - 40)
        ctx.move_to(CX + 40, CY + R_YI - 14); ctx.line_to(CX + 40, CY + R_YO + 40)
        setc(ctx, COPPER, st['flow']); ctx.set_line_width(6); ctx.stroke()
        straight_arrow(ctx, CX + 110, CY - R_YO - 60, CX + 110, CY - R_YO + 10, INK, st['flow'], lw=6, head=12)
        straight_arrow(ctx, CX + 110, CY + R_YO - 10, CX + 110, CY + R_YO + 60, INK, st['flow'], lw=6, head=12)
        text_c(ctx, "CURRENT IN", CX + 230, CY - R_YO - 20, 24, INK, True, 1, st['flow'])
        text_c(ctx, "CURRENT OUT", CX + 240, CY + R_YO + 40, 24, INK, True, 1, st['flow'])
    # highlights + tags
    highlight(ctx, CX, CY - R_COM - 50, 70, 80, MUSTARD, st['h_br'], t)
    highlight(ctx, CX, CY + R_COM + 50, 70, 80, MUSTARD, st['h_br'], t)
    highlight(ctx, CX, CY, R_COM + 18, R_COM + 18, ORANGE, st['h_com'], t)
    highlight(ctx, CX - 330, CY, 120, 200, TEAL, st['h_field'], t)
    highlight(ctx, CX + 330, CY, 120, 200, TEAL, st['h_field'], t)
    tag(ctx, "CARBON BRUSHES", CX, 375, INK, st['l_br'], 28)
    tag(ctx, "1 · STATOR · FIELD WINDINGS", CX, 1440, TEAL, st['l_field'], 28)
    tag(ctx, "2 · ARMATURE (ROTOR)", CX, 1440, TEAL, st['l_arm'], 28)
    tag(ctx, "3 · COMMUTATOR · MICA", CX, 1440, ORANGE, st['l_com'], 28)
    tag(ctx, "ARMATURE FIELD STAYS PUT", CX, 1440, TEAL, st['l_comm'], 28)
    tag(ctx, "SERIES FIELD + COMMUTATOR", CX, 375, INK, st['recap'], 28)
    tag(ctx, "CHECK LENGTH · REPLACE IN PAIRS", 640, 1450, GREEN, st['tip'], 26)

# ---------------------------------------------------------------- state machine
def state(t):
    st = {}
    st['th'] = theta(t)
    st['pol'] = polarity(t)
    st['poles'] = ease((t - B(2) - 0.3) / 0.8)
    st['h_br'] = bw(t, 1) + win(t, B(14) + 0.1, B(14) + 2.3)
    st['l_br'] = bw(t, 1)
    st['h_field'] = bw(t, 2)
    st['l_field'] = bw(t, 2)
    st['h_arm'] = bw(t, 4)
    st['l_arm'] = bw(t, 4)
    st['h_com'] = bw(t, 5) + bw(t, 8, 9)
    st['l_com'] = bw(t, 5)
    st['l_comm'] = win(t, B(8) + 1.2, B(9))
    st['cur'] = ease((t - B(6) - 0.4) / 0.8) * (1 - ease((t - B(11)) / 0.6)) + bw(t, 13, 14)
    st['flow'] = bw(t, 6)
    st['fstat'] = ease((t - B(7) - 0.2) / 0.6) * (1 - ease((t - B(11)) / 0.6)) + bw(t, 13, 14)
    st['farm'] = st['fstat']
    st['ninety'] = bw(t, 7)
    st['rot'] = ease((t - B(7) - 0.8) / 0.6) * (1 - ease((t - B(9)) / 0.5)) + win(t, B(10) + 0.6, B(11) - 0.1) + bw(t, 11, 12)
    st['spark'] = win(t, 0.0, B(1) + 0.6) + bw(t, 9, 10) + win(t, B(12) + 0.2, B(12) + 2.5) + win(t, B(14) + 0.2, B(14) + 2.3)
    st['cap'] = ease((t - B(12) - 0.4) / 0.6)
    st['l_cap'] = bw(t, 12)
    st['tacho'] = bw(t, 11)
    st['rpm'] = 3000 + 21000 * ease((t - B(11) - 0.4) / 2.8)
    st['recap'] = bw(t, 13)
    st['tip'] = win(t, B(14) + 2.3, B(15))
    st['wear'] = win(t, B(14) + 2.2, B(15))
    return st

SFX = [(B(0) + 0.3, 'sizzle'), (B(1) + 0.2, 'pop'), (B(2) + 0.2, 'pop'), (B(4) + 0.2, 'pop'), (B(5) + 0.2, 'pop'),
       (B(6) + 0.3, 'click'), (B(7) + 0.2, 'pop'), (B(8) + 1.2, 'click'), (B(11) + 0.4, 'whoosh'),
       (B(12) + 0.3, 'sizzle'), (B(12) + 0.6, 'pop'), (B(13) + 0.2, 'ding'), (B(14) + 2.2, 'click')]
HUM = [(0.0, B(15))]

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

# ---------------------------------------------------------------- cards
def card_lam(ctx, t, lt, a):
    card_frame(ctx, "WHY LAMINATED?", a, "SOLID = HOT  ·  SHEETS = COOL", TEAL)
    p = ease((lt - 0.3) / 0.8)
    # left: solid block, one big eddy loop around the flux
    x0, y0, w, h = 170, 280, 280, 230
    g = cairo.RadialGradient(x0 + w/2, y0 + h/2, 10, x0 + w/2, y0 + h/2, 180)
    g.add_color_stop_rgba(0, *RED[:3], 0.45 * a * p); g.add_color_stop_rgba(1, *RED[:3], 0)
    rrect(ctx, x0, y0, w, h, 6); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    ctx.set_source(g); ctx.rectangle(x0, y0, w, h); ctx.fill()
    ctx.save(); ctx.translate(x0 + w/2, y0 + h/2); ctx.scale(110, 85); ctx.arc(0, 0, 1, 0.3, 2*math.pi - 0.3); ctx.restore()
    setc(ctx, RED, a * p); ctx.set_line_width(6); ctx.stroke()
    # right: stack of thin insulated sheets, tiny loops
    x1 = 630
    n = 9; sw = w / n
    for i in range(n):
        rrect(ctx, x1 + i * sw + 2, y0, sw - 4, h, 3); fill_stroke(ctx, STEEL, lw=2, alpha=a)
        ctx.save(); ctx.translate(x1 + i * sw + sw / 2, y0 + h / 2); ctx.scale(sw * 0.25, 70); ctx.arc(0, 0, 1, 0.3, 2*math.pi - 0.3); ctx.restore()
        setc(ctx, RED, a * p * 0.8); ctx.set_line_width(3); ctx.stroke()
    # flux: into the face (cross symbol) on both
    for cx in (x0 + w/2, x1 + w/2):
        ctx.arc(cx, y0 + h/2, 18, 0, 2*math.pi); fill_stroke(ctx, WHITE, lw=3, alpha=a)
        ctx.move_to(cx - 9, y0 + h/2 - 9); ctx.line_to(cx + 9, y0 + h/2 + 9); ctx.move_to(cx + 9, y0 + h/2 - 9); ctx.line_to(cx - 9, y0 + h/2 + 9)
        setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    text_c(ctx, "AC FLUX", 540, 400, 22, INK, True, 1, a)

def card_arc(ctx, t, lt, a):
    card_frame(ctx, "WHY IT SPARKS", a, "COIL CURRENT CUT = INDUCTIVE ARC", SPARK)
    # unrolled commutator moving right under a fixed brush; contact breaks at the brush's right (trailing) edge
    speed = 90; segw = 120
    off = (lt * speed) % segw
    y = 440
    ctx.save(); ctx.rectangle(130, y - 10, 820, 80); ctx.clip()
    for k in range(-1, 9):
        x = 130 + k * segw + off
        rrect(ctx, x + 4, y, segw - 8, 60, 4); fill_stroke(ctx, COPPER, lw=3, alpha=a)
        ctx.rectangle(x - 4, y, 8, 60); setc(ctx, MICA, a); ctx.fill()
    ctx.restore()
    straight_arrow(ctx, 160, 530, 300, 530, INK, a, lw=4, head=10)
    text_c(ctx, "ROTATION", 380, 538, 20, INK, True, 1, a)
    bx0, bx1 = 470, 610
    rrect(ctx, bx0, 290, bx1 - bx0, 150, 6); fill_stroke(ctx, CARBON, lw=4, alpha=a)
    text_c(ctx, "BRUSH", (bx0 + bx1) / 2, 375, 24, WHITE, True, 2, a)
    # a mica gap crossing the trailing edge = coil current interrupted -> spark
    gaps = [130 + k * segw + off for k in range(-1, 9)]
    near = min(abs(g - bx1) for g in gaps)
    s = clamp(1 - near / 26)
    if s > 0:
        rnd = random.Random(int(lt * 20))
        for k in range(4):
            ang = rnd.uniform(-0.9, 0.2); L = rnd.uniform(25, 55)
            ctx.move_to(bx1, y); ctx.line_to(bx1 + math.cos(ang) * L * 0.5, y - 10 + math.sin(ang) * L * 0.5)
            ctx.line_to(bx1 + math.cos(ang) * L, y + math.sin(ang) * L)
            setc(ctx, SPARK, a * s); ctx.set_line_width(5); ctx.stroke()
        g = cairo.RadialGradient(bx1, y, 2, bx1, y, 60)
        g.add_color_stop_rgba(0, *SPARK_W[:3], 0.95 * a * s); g.add_color_stop_rgba(1, *SPARK[:3], 0)
        ctx.set_source(g); ctx.arc(bx1, y, 60, 0, 2*math.pi); ctx.fill()
    # inductor symbol (coil) with the formula
    for k in range(4):
        ctx.arc(760 + k * 34, 320, 17, math.pi, 2 * math.pi); setc(ctx, COPPER, a); ctx.set_line_width(6); ctx.stroke()
    text_c(ctx, "V = L · di/dt", 810, 380, 28, INK, True, 1, a)

def card_ac(ctx, t, lt, a):
    card_frame(ctx, "SAME DIRECTION ON AC", a, "BOTH FLIP = SAME TORQUE", GREEN)
    # sine wave, cursor in sync with the stage polarity
    x0, x1, ym, amp = 140, 520, 400, 90
    for i in range(101):
        x = lerp(x0, x1, i / 100); y = ym - amp * math.sin(2 * math.pi * 2 * i / 100)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(x0, ym); ctx.line_to(x1, ym); setc(ctx, INK2, a * 0.5); ctx.set_line_width(2); ctx.stroke()
    ph = clamp((lt - 0.6) / 2.2 % 1.0 if lt > 0.6 else 0)
    xc = lerp(x0, lerp(x0, x1, 0.5), ph); yc = ym - amp * math.sin(2 * math.pi * ph)
    ctx.arc(xc, yc, 12, 0, 2*math.pi); setc(ctx, RED, a); ctx.fill()
    pol = polarity(t)
    # mini motor: left/right poles + rotor arrow
    mx, my = 780, 400
    for side in (-1, 1):
        is_n = (side < 0) == (pol > 0)
        rrect(ctx, mx + side * 140 - 35, my - 60, 70, 120, 8); fill_stroke(ctx, NCOL if is_n else SCOL, lw=4, alpha=a)
        text_c(ctx, "N" if is_n else "S", mx + side * 140, my + 14, 40, WHITE, True, 0, a)
    ctx.arc(mx, my, 80, 0, 2*math.pi); fill_stroke(ctx, STEEL_L, lw=4, alpha=a)
    top = "N" if pol > 0 else "S"; bot = "S" if pol > 0 else "N"
    text_c(ctx, top, mx, my - 40, 30, NCOL if top == "N" else SCOL, True, 0, a)
    text_c(ctx, bot, mx, my + 64, 30, NCOL if bot == "N" else SCOL, True, 0, a)
    # clockwise arrow (always the same)
    r = 105; a1, a2 = math.radians(-120), math.radians(-60)
    ctx.arc(mx, my, r, a1, a2); setc(ctx, GREEN, a); ctx.set_line_width(7); ctx.stroke()
    x, y = mx + r * math.cos(a2), my + r * math.sin(a2); dx, dy = -math.sin(a2), math.cos(a2); nx, ny = math.cos(a2), math.sin(a2)
    ctx.move_to(x + dx * 18, y + dy * 18); ctx.line_to(x + nx * 15, y + ny * 15); ctx.line_to(x - nx * 15, y - ny * 15); ctx.close_path(); setc(ctx, GREEN, a); ctx.fill()

CARDS = {'lam': card_lam, 'arc': card_arc, 'ac': card_ac}
