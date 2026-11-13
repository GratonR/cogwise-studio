"""Cogwise episode: That hum is solid steel stretching 100 times a second.
One idea (magnetostriction): the silicon-steel core of a distribution transformer gets very slightly longer
whenever it is magnetized, WHICHEVER the direction of magnetization. Alternating current magnetizes it one way,
then the other, so the core stretches twice per cycle: 50 Hz mains -> 100 Hz hum (60 Hz -> 120 Hz in North America).
Order of size: a few parts per million -> a 1 m core grows ~3 µm (~0.0001 in); a hair is ~70 µm.

VIEW: front cross-section of a ground-mounted transformer box (front panel cut away). Screen y grows DOWN.
Core-type core: two vertical limbs + top/bottom yokes, laminated. Primary coil on the LEFT limb (many thin turns),
secondary on the RIGHT limb (fewer, thicker turns).
Current convention (phase + = current > 0): in each coil, wires on the left side of the limb = dot (out of
screen), wires on the right side = cross (into screen). With x right, physical y up, z out of screen this loop's
magnetic moment points physically UP (screen -y) -> primary drives flux UP the left limb, RIGHT along the top
yoke, DOWN the right limb, LEFT along the bottom yoke (clockwise on screen). Phase -: all reversed.
Secondary (load current) opposes the primary's MMF around the core, i.e. it also pushes "up" inside its own limb:
same dot/cross pattern at the same instant. The net (magnetizing) flux follows the primary.
Stretch = k * sin^2(phase): always >= rest length, two humps per current cycle.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="transformer-hum",
    title="That hum is solid steel stretching 100 times a second 🔊⚡ #Shorts",
    description=("The box down your street isn't buzzing with electricity: its steel core is stretching.\n\n"
                 "#Shorts #howthingswork #transformer #electricity #cogwise"),
    hashtags=["Shorts", "howthingswork", "transformer", "electricity", "engineering", "cogwise"],
    sources=[
        "https://hyperphysics.gsu.edu/hbase/Solids/magstrict.html",
        "https://electrical-engineering-portal.com/sources-of-sound-in-transformers",
        "https://en.wikipedia.org/wiki/Magnetostriction",
    ],
)

BEATS = [
    dict(dur=3.4, title="NOT A BUZZ", caption="The box down your street isn't buzzing."),
    dict(dur=5.4, title="THE SECRET", caption="Its steel core is stretching and shrinking, a hundred times every second."),
    dict(dur=5.6, title="1 · THE CORE", caption="Inside sits a core of thin silicon-steel sheets, stacked tight."),
    dict(dur=5.4, title="2 · THE COILS", caption="Two copper coils wrap around it, and alternating current flows through them."),
    dict(dur=6.2, title=None, caption="That current magnetizes the steel, and magnetized steel gets slightly longer. It's called magnetostriction.", card='stretch'),
    dict(dur=7.4, title="HOW MUCH?", caption="A one-metre core grows just a few thousandths of a millimetre, about a ten-thousandth of an inch."),
    dict(dur=5.6, title="TINY, BUT FAST", caption="Tiny, but over and over, the whole core pushes the air like a speaker."),
    dict(dur=7.4, title="3 · BOTH WAYS", caption="In Europe, the current swings back and forth fifty times a second."),
    dict(dur=5.8, title=None, caption="But steel stretches whichever way it's magnetized: twice per swing.", card='twice'),
    dict(dur=5.2, title="100 HZ", caption="Fifty swings, two stretches each: a steady hum at one hundred hertz."),
    dict(dur=6.6, title="USA: 120 HZ", caption="In North America it's sixty, so transformers hum at one hundred twenty."),
    dict(dur=6.4, title="STEEL THAT SINGS", caption="So that hum isn't electricity leaking. It's steel, breathing to the rhythm of your power."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
CX, CY = 540, 1010                     # core centre
CORE_W, CORE_H = 470, 560              # outer size at rest
LIMB = 74                              # limb / yoke thickness
BOX_X0, BOX_X1, BOX_Y0, BOX_Y1 = 170, 910, 610, 1420
PAD_Y = 1420
STRETCH_PX = 16                        # visual stretch (exaggerated ~x100 000)

STEEL = hexc('#8d949b'); STEEL_D = hexc('#5e656c'); STEEL_L = hexc('#b9bfc4')
COPPER = hexc('#c46f33'); COPPER_L = hexc('#e39a62')
BOXC = hexc('#7f9a83'); BOXC_D = hexc('#5d7662'); BOX_IN = hexc('#efe6d2')

AC_HZ = 0.45                           # visual current cycle (real: 50 Hz -> shown on the HUD)
def cur(t):
    """current, -1..1 (sine)."""
    return math.sin(2 * math.pi * AC_HZ * t)
def stretch(t):
    """0..1, sin^2 of the current: two humps per cycle, never negative."""
    return cur(t) ** 2

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['cut'] = clamp(ease((t - 0.05) / 0.5))                 # cut-away open from the start
    s['breath'] = max(clamp(ease(t / 0.4)), 0)                # core breathes from the first frame
    s['current'] = clamp(ease((t - B(3) - 0.1) / 0.6))        # current shown from beat 4
    s['waves'] = max(0.35 * bw(t, 0, 2), bw(t, 6, 12) * 0.9, 0.3 * (t > B(2)))
    s['sheets'] = bw(t, 2)                                    # laminations fan out
    s['tag_core'] = bw(t, 2)
    s['tag_coils'] = bw(t, 3)
    s['dim'] = bw(t, 5)
    s['tag_speaker'] = bw(t, 6)
    s['tag_both'] = bw(t, 7)
    s['recap'] = bw(t, 11)
    s['tag_notbuzz'] = bw(t, 0, 1)
    return s

def core_rect(t, s):
    d = STRETCH_PX * stretch(t) * s['breath']
    w, h = CORE_W + d, CORE_H + d
    return CX - w / 2, CY - h / 2, w, h

# ---------------------------------------------------------------- drawing helpers
def wire(ctx, x, y, r, out, a, col=COPPER, mark=True):
    """wire cross-section. out=True: dot (current out of screen); False: cross (into screen)."""
    ctx.arc(x, y, r, 0, 2 * math.pi); fill_stroke(ctx, col, lw=2.5, alpha=a)
    if not mark: return
    if out:
        ctx.arc(x, y, r * 0.34, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()
    else:
        d = r * 0.5
        ctx.move_to(x - d, y - d); ctx.line_to(x + d, y + d); ctx.move_to(x - d, y + d); ctx.line_to(x + d, y - d)
        setc(ctx, INK, a); ctx.set_line_width(2.5); ctx.stroke()

def chevron(ctx, x, y, ang, col, a, size=11):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    ctx.move_to(-size, -size * 0.8); ctx.line_to(size * 0.6, 0); ctx.line_to(-size, size * 0.8)
    setc(ctx, col, a); ctx.set_line_width(4); ctx.stroke(); ctx.restore()

def draw_box(ctx, t, s):
    # concrete pad
    rrect(ctx, BOX_X0 - 50, PAD_Y, BOX_X1 - BOX_X0 + 100, 60, 6); fill_stroke(ctx, FILL3, lw=5)
    # cooling fins on both sides
    for side in (-1, 1):
        x = BOX_X0 - 34 if side < 0 else BOX_X1
        for i in range(6):
            ctx.rectangle(x, 760 + i * 100, 34, 60); fill_stroke(ctx, BOXC_D, lw=3)
    # box body + roof
    rrect(ctx, BOX_X0, BOX_Y0, BOX_X1 - BOX_X0, BOX_Y1 - BOX_Y0, 10); fill_stroke(ctx, BOXC, lw=5)
    rrect(ctx, BOX_X0 - 24, BOX_Y0 - 30, BOX_X1 - BOX_X0 + 48, 40, 8); fill_stroke(ctx, BOXC_D, lw=5)
    # cut-away: inside (oil-filled tank, shown light)
    c = s['cut']
    ins = (BOX_X0 + 30, BOX_Y0 + 40, BOX_X1 - BOX_X0 - 60, BOX_Y1 - BOX_Y0 - 70)
    rrect(ctx, *ins, 8); fill_stroke(ctx, lerpc(BOXC, BOX_IN, c), lw=4)
    if c < 1:   # warning plate on the closed door
        a = 1 - c
        ctx.move_to(540, 900); ctx.line_to(600, 1010); ctx.line_to(480, 1010); ctx.close_path()
        fill_stroke(ctx, MUSTARD, lw=4, alpha=a)
    # bushings on the roof (HV left, LV right)
    for x, hgt in ((330, 70), (420, 70), (680, 50), (750, 50)):
        for k in range(3):
            rrect(ctx, x - 14 + k * 2, BOX_Y0 - 30 - hgt + k * hgt / 3, 28 - k * 4, hgt / 3, 5)
            fill_stroke(ctx, hexc('#a65a3a') if x < 540 else hexc('#c9c2b2'), lw=3)

def draw_core(ctx, t, s):
    x, y, w, h = core_rect(t, s)
    # outer shape minus window, drawn as limbs + yokes (laminations visible as thin lines)
    ctx.rectangle(x, y, w, h); ctx.rectangle(x + LIMB, y + LIMB, w - 2 * LIMB, h - 2 * LIMB)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    setc(ctx, STEEL); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    # lamination lines (follow each part's length)
    fan = s['sheets']
    for i in range(1, 7):
        o = i * LIMB / 7
        for (x0, y0, x1, y1) in ((x + o, y + LIMB, x + o, y + h - LIMB), (x + w - o, y + LIMB, x + w - o, y + h - LIMB),
                                 (x + LIMB, y + o, x + w - LIMB, y + o), (x + LIMB, y + h - o, x + w - LIMB, y + h - o)):
            ctx.move_to(x0, y0); ctx.line_to(x1, y1)
        setc(ctx, STEEL_D, 0.8); ctx.set_line_width(2); ctx.stroke()
    # beat 3: a pack of sheets fans out of the top yoke to show they are separate
    if fan > 0:
        for i in range(5):
            dy = -fan * (20 + i * 26)
            ang = -fan * 0.03 * (i + 1)
            ctx.save(); ctx.translate(CX, y + 8 + dy); ctx.rotate(ang)
            rrect(ctx, -w / 2 + 6, -5, w - 12, 10, 3); fill_stroke(ctx, STEEL_L, lw=2.5, alpha=fan)
            ctx.restore()
    return x, y, w, h

def draw_flux(ctx, t, s, x, y, w, h):
    a = s['current']
    if a <= 0: return
    c = cur(t); sg = 1 if c >= 0 else -1; k = abs(c)
    col = TEAL if sg > 0 else RED
    m = LIMB / 2
    # clockwise on screen in phase +: up left limb, right along top, down right limb, left along bottom
    P = [(x + m, y + h - m), (x + m, y + m), (x + w - m, y + m), (x + w - m, y + h - m), (x + m, y + h - m)]
    ctx.move_to(*P[0])
    for q in P[1:]: ctx.line_to(*q)
    setc(ctx, col, 0.7 * a * (0.3 + 0.7 * k)); ctx.set_line_width(4); ctx.set_dash([12, 8]); ctx.stroke(); ctx.set_dash([])
    for i in range(4):
        (x0, y0), (x1, y1) = P[i], P[i + 1]
        ang = math.atan2(y1 - y0, x1 - x0) + (0 if sg > 0 else math.pi)
        chevron(ctx, (x0 + x1) / 2, (y0 + y1) / 2, ang, col, a * (0.3 + 0.7 * k))

def coil_wires(x, y, w, h):
    """returns [(cx, cy, r, side)] side=-1 left of a limb, +1 right; coil 'P' left limb, 'S' right limb."""
    out = []
    y0, y1 = y + LIMB + 40, y + h - LIMB - 40
    # primary: 2 columns x 9 rows of thin wire on each side of the LEFT limb
    for col in range(2):
        for r in range(9):
            yy = lerp(y0, y1, r / 8)
            out.append(('P', x - 16 - col * 22, yy, 9, -1))
            out.append(('P', x + LIMB + 16 + col * 22, yy, 9, +1))
    # secondary: 1 column x 5 rows of thick wire on each side of the RIGHT limb
    for r in range(5):
        yy = lerp(y0 + 10, y1 - 10, r / 4)
        out.append(('S', x + w - LIMB - 20, yy, 16, -1))
        out.append(('S', x + w + 20, yy, 16, +1))
    return out

def draw_coils(ctx, t, s, x, y, w, h):
    a = s['current']; c = cur(t)
    glow = s['tag_coils']
    for (coil, wx, wy, r, side) in coil_wires(x, y, w, h):
        out = (side < 0) == (c >= 0)            # phase +: left side dot, right side cross
        col = lerpc(COPPER, COPPER_L, 0.6 * glow * (0.5 + 0.5 * math.sin(t * 6)))
        wire(ctx, wx, wy, r, out, 1.0, col, mark=(a > 0.05 and abs(c) > 0.12))
    # lead wires to the bushings (HV to primary, LV to secondary) with moving current dots
    leads = [((x - 38, y + LIMB + 30), (x - 38, BOX_Y0 + 60), (330, BOX_Y0 + 60), (330, BOX_Y0 - 10)),
             ((x + w + 20, y + LIMB + 22), (x + w + 20, BOX_Y0 + 70), (750, BOX_Y0 + 70), (750, BOX_Y0 - 10))]
    for L in leads:
        ctx.move_to(*L[0])
        for q in L[1:]: ctx.line_to(*q)
        setc(ctx, COPPER); ctx.set_line_width(6); ctx.stroke()
        if a > 0:
            # dots slide back and forth with the current (displacement ~ integral of the sine)
            seg = [(L[i], L[i + 1]) for i in range(len(L) - 1)]
            lens = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in seg]; tot = sum(lens)
            disp = -math.cos(2 * math.pi * AC_HZ * t) * 22
            for j in range(9):
                d = (j / 9 * tot + disp) % tot
                for (p0, p1), ln in zip(seg, lens):
                    if d <= ln:
                        u = d / ln; px, py = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
                        ctx.arc(px, py, 6, 0, 2 * math.pi); setc(ctx, MUSTARD, a); ctx.fill()
                        break
                    d -= ln

def draw_waves(ctx, t, s, x, y, w, h):
    a = s['waves']
    if a <= 0: return
    # sound fronts leave the box walls at the stretch rhythm (2 per current cycle)
    rate = 2 * AC_HZ
    for side in (-1, 1):
        bx = BOX_X0 - 40 if side < 0 else BOX_X1 + 40
        for n in range(3):
            u = (t * rate + n / 3) % 1
            r = 20 + u * 120
            cx = bx
            start = math.pi * 0.72 if side < 0 else -math.pi * 0.28
            if side < 0: ctx.arc(cx, CY, r, start, start + math.pi * 0.56)
            else: ctx.arc(cx, CY, r, start, start + math.pi * 0.56)
            setc(ctx, INK2, a * (1 - u)); ctx.set_line_width(5); ctx.stroke()

def draw_overlays(ctx, t, s, x, y, w, h):
    a = s['tag_notbuzz']
    if a > 0:
        highlight(ctx, CX, CY, w / 2 + 30, h / 2 + 30, RED, a, t)
        tag(ctx, "STEEL CORE: BREATHING", CX, 1360, RED, a, 26)
    a = s['tag_core']
    if a > 0:
        tag(ctx, "1 · SILICON-STEEL SHEETS", CX, 1360, INK, a, 26)
    a = s['tag_coils']
    if a > 0:
        tag(ctx, "2 · COPPER COILS", CX, 1360, INK, a, 26)
        tag(ctx, "PRIMARY", x + 10, y - 22, COPPER, a, 18)
        tag(ctx, "SECONDARY", x + w - 10, y - 22, COPPER, a, 18)
    a = s['dim']
    if a > 0:
        # dimension line along the top yoke: "1 m"
        yy = y - 40
        ctx.move_to(x, yy - 14); ctx.line_to(x, yy + 14); ctx.move_to(x + w, yy - 14); ctx.line_to(x + w, yy + 14)
        setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        straight_arrow(ctx, CX, yy, x + 4, yy, INK, a, lw=4, head=9); straight_arrow(ctx, CX, yy, x + w - 4, yy, INK, a, lw=4, head=9)
        tag(ctx, "1 m · 3.3 ft", CX, yy, INK, a, 22)
        # magnifier on the right end of the core
        mx, my, mr = 820, 470, 120
        ctx.move_to(x + w, y + 10); ctx.line_to(mx - mr * 0.6, my + mr * 0.8); setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(mx, my, mr, 0, 2 * math.pi); setc(ctx, CREAM, a); ctx.fill()
        ctx.save(); ctx.arc(mx, my, mr - 4, 0, 2 * math.pi); ctx.clip()
        # scale: 1 µm = 1.6 px. Hair 70 µm = 112 px wide. Core end grows 0..3 µm = 0..4.8 px
        g = 4.8 * stretch(t)
        RX = mx - 20                                                                          # rest position of the core end
        ctx.rectangle(mx - mr, my - 80, RX - (mx - mr) + g, 70); setc(ctx, STEEL); ctx.fill()  # core end (top half)
        ctx.rectangle(RX, my - 80, g, 70); setc(ctx, RED, a); ctx.fill()                      # the growth, in red
        ctx.move_to(RX, my - 95); ctx.line_to(RX, my + 75); setc(ctx, INK, a); ctx.set_dash([5, 4]); ctx.set_line_width(2); ctx.stroke(); ctx.set_dash([])
        ctx.rectangle(RX, my + 5, 112, 50); setc(ctx, hexc('#6b4d10'), 0.85 * a); ctx.fill()     # a hair, 70 µm wide, same scale
        ctx.restore()
        ctx.arc(mx, my, mr, 0, 2 * math.pi); setc(ctx, INK, a); ctx.set_line_width(8); ctx.stroke()
        ctx.move_to(mx + mr * 0.7, my + mr * 0.7); ctx.line_to(mx + mr * 1.15, my + mr * 1.15); ctx.set_line_width(18); ctx.stroke()
        tag(ctx, "HAIR ≈ 70 µm", mx + 40, my + mr + 26, hexc('#6b4d10'), a, 17)
        tag(ctx, "CORE +3 µm", mx - 10, my - mr - 26, RED, a, 18)
    a = s['tag_speaker']
    if a > 0:
        tag(ctx, "THE CORE PUSHES THE AIR", CX, 1360, INK, a, 26)
    a = s['tag_both']
    if a > 0:
        c = cur(t)
        tag(ctx, "3 · CURRENT: ONE WAY, THEN THE OTHER", CX, 1360, TEAL if c >= 0 else RED, a, 22)
    a = s['recap']
    if a > 0:
        tag(ctx, "1 · CORE", CX, y + LIMB / 2, INK, a, 20)
        tag(ctx, "2 · COILS", x - 20, y + h + 34, COPPER, a, 20)
        tag(ctx, "3 · 2 STRETCHES / CYCLE", CX, 1360, RED, a, 22)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    draw_box(ctx, t, s)
    x, y, w, h = core_rect(t, s)
    draw_coils(ctx, t, s, x, y, w, h)
    x, y, w, h = draw_core(ctx, t, s)
    draw_flux(ctx, t, s, x, y, w, h)
    draw_waves(ctx, t, s, x, y, w, h)
    draw_overlays(ctx, t, s, x, y, w, h)

# camera: start already close on the core (answer visible at once), wide for the coils, push on the magnifier
CAMKEYS = [(0, 540, 1010, 1.3),
           (B(1) + 0.2, 540, 990, 1.15),
           (B(2) + 0.1, 540, 900, 1.25),
           (B(3), 540, 980, 1.05),
           (B(5) + 0.1, 640, 820, 1.2),
           (B(6), 540, 1000, 1.0),
           (B(11), 540, 1000, 1.05)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)
ANCHOR = (540, 1300)

def draw_hud(ctx, t, E):
    a = bw(t, 1)
    if a > 0: hud(ctx, "CORE STRETCHES", "100 ×/s", "drawn ×100 000 bigger", a, RED, flash=0.4 * stretch(t), x=500, y=196, w=540)
    a = bw(t, 5)
    if a > 0: hud(ctx, "1 m CORE GROWS", "≈ 3 µm", "≈ 0.0001 in", a, RED, x=40, y=196, w=420)
    a = bw(t, 7)
    if a > 0:
        c = cur(t)
        hud(ctx, "EUROPE: MAINS CURRENT", "50 Hz", "+ / − / + / − …", a, TEAL if c >= 0 else RED, flash=0.4 * abs(c), x=500, y=196, w=540)
    a = bw(t, 9)
    if a > 0: hud(ctx, "HUM (EUROPE)", "50 × 2 = 100 Hz", "2 stretches per cycle", a, MUSTARD, flash=0.3 * stretch(t), x=270, y=196, w=540)
    a = bw(t, 10)
    if a > 0: hud(ctx, "HUM (NORTH AMERICA)", "60 × 2 = 120 Hz", "mains at 60 Hz", a, TEAL, flash=0.3 * stretch(t), x=270, y=196, w=540)

SFX = [(0.3, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(5) + 0.3, 'pop'),
       (B(6) + 0.3, 'pop'), (B(7) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_stretch(ctx, t, lt, a):
    card_frame(ctx, "A BAR OF STEEL", a, "MAGNETIZED EITHER WAY = LONGER", RED)
    c = cur(t); k = c * c
    L0 = 520; grow = 46 * k            # exaggerated
    x0 = 230; y0 = 360
    # coil around the bar (wire turns), field arrow along the bar, direction = sign of current
    ctx.rectangle(x0, y0 - 34, L0 + grow, 68); fill_stroke(ctx, STEEL, lw=5, alpha=a)
    for i in range(9):
        xx = x0 + 40 + i * 52
        ctx.move_to(xx, y0 - 46); ctx.line_to(xx + 18, y0 + 46); setc(ctx, COPPER, a); ctx.set_line_width(7); ctx.stroke()
    col = TEAL if c >= 0 else RED
    if abs(c) > 0.15:
        if c >= 0: straight_arrow(ctx, x0 + 120, y0 - 80, x0 + 420, y0 - 80, col, a * abs(c), lw=7, head=14)
        else: straight_arrow(ctx, x0 + 420, y0 - 80, x0 + 120, y0 - 80, col, a * abs(c), lw=7, head=14)
    text_c(ctx, "MAGNETIC FIELD", x0 + 270, y0 - 108, 22, col, True, 1, a * min(1, abs(c) * 2))
    # ruler under the bar, rest length mark
    ry = y0 + 70
    ctx.rectangle(x0, ry, 640, 34); fill_stroke(ctx, hexc('#f2e2b0'), lw=3, alpha=a)
    for i in range(33):
        xx = x0 + i * 20; hh = 18 if i % 5 == 0 else 10
        ctx.move_to(xx, ry); ctx.line_to(xx, ry + hh); setc(ctx, INK, a); ctx.set_line_width(2); ctx.stroke()
    ctx.move_to(x0 + L0, y0 - 60); ctx.line_to(x0 + L0, ry + 34); setc(ctx, INK, a); ctx.set_dash([8, 6]); ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    text_c(ctx, "REST", x0 + L0, ry + 62, 18, INK2, True, 1, a)
    if grow > 4: straight_arrow(ctx, x0 + L0, y0, x0 + L0 + grow + 4, y0, RED, a, lw=5, head=8)
    text_c(ctx, "×100 000", 880, 300, 20, INK2, True, 1, a)

def card_twice(ctx, t, lt, a):
    card_frame(ctx, "CURRENT vs CORE LENGTH", a, "2 STRETCHES PER CYCLE", RED)
    X0, X1 = 250, 930
    yc, A1 = 320, 52                 # current curve: centre line and amplitude
    yl, A2 = 500, 80                 # length curve: rest line (bottom), hump height
    period = 1 / AC_HZ
    span = 2 * period                # two cycles across the plot
    t0 = t - span * 0.5
    def px(tt): return X0 + (tt - t0) / span * (X1 - X0)
    # axes
    for yy in (yc, yl):
        ctx.move_to(X0, yy); ctx.line_to(X1, yy); setc(ctx, INK2, a); ctx.set_dash([6, 6]); ctx.set_line_width(2); ctx.stroke(); ctx.set_dash([])
    text_c(ctx, "CURRENT", 170, yc - 8, 20, INK, True, 1, a); text_c(ctx, "+ / −", 170, yc + 20, 18, INK2, True, 1, a)
    text_c(ctx, "LENGTH", 170, yl - 40, 20, INK, True, 1, a); text_c(ctx, "REST", 170, yl + 6, 18, INK2, True, 1, a)
    # current curve (screen up = positive)
    N = 160
    for i in range(N + 1):
        tt = t0 + span * i / N; xx = px(tt); yy = yc - A1 * cur(tt)
        (ctx.move_to if i == 0 else ctx.line_to)(xx, yy)
    setc(ctx, TEAL, a); ctx.set_line_width(5); ctx.stroke()
    # length curve: rest + hump for every peak AND every trough (never below rest)
    for i in range(N + 1):
        tt = t0 + span * i / N; xx = px(tt); yy = yl - A2 * stretch(tt)
        (ctx.move_to if i == 0 else ctx.line_to)(xx, yy)
    setc(ctx, RED, a); ctx.set_line_width(5); ctx.stroke()
    # playhead at "now"
    xn = px(t)
    ctx.move_to(xn, yc - 70); ctx.line_to(xn, yl + 14); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(xn, yc - A1 * cur(t), 9, 0, 2 * math.pi); setc(ctx, TEAL, a); ctx.fill()
    ctx.arc(xn, yl - A2 * stretch(t), 9, 0, 2 * math.pi); setc(ctx, RED, a); ctx.fill()

CARDS = {'stretch': card_stretch, 'twice': card_twice}
