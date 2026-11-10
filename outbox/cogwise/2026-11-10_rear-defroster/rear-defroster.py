"""Cogwise episode: Those lines on your back window are heaters.
One idea: every thin line on a rear window is a heating wire made of silver paste baked into the
inside face of the glass; current runs from one bus bar to the other across all lines at once
(parallel), the thin line's resistance turns current into heat (Joule), the ice melts in bands
outward from each line, and the bands meet. One scratched line = only its stripe stays frosty.

VIEW: the rear window seen FROM INSIDE the car (the lines are on the face we look at).
Screen coordinates: y grows DOWN.
Current (conventional, simplified): battery + -> defrost button -> LEFT bus bar (fed at its bottom)
-> up the left bar -> across every line LEFT -> RIGHT at the same time -> RIGHT bus bar -> down to ground.
Melting: frost clears first right on top of each line, then the clear band widens up AND down.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="rear-defroster",
    title="Those lines on your back window are heaters 🔥 #Shorts",
    description=("Every thin line on your rear window is a heater: silver baked into the glass, 12 volts, "
                 "and a little resistance.\n\n#Shorts #howthingswork #cars #winter #cogwise"),
    hashtags=["Shorts", "howthingswork", "cars", "winter", "engineering", "cogwise"],
    sources=[
        "https://engineerfix.com/what-are-the-lines-on-a-rear-windshield/",
        "https://www.scienceabc.com/eyeopeners/why-do-car-windows-have-patterns-on-them.html",
        "https://knowhow.napaonline.com/rear-car-defroster-work-can-repair/",
        "https://www.slashgear.com/2028585/how-car-rear-defroster-works-explained",
        "https://ownersmanual.kia.com/full_webhelp/MQ4A/2026/en_US/topics/t00336.html",
    ],
)

BEATS = [
    dict(dur=5.0, title="THOSE LINES?", caption="Those thin lines on your back window? Every one of them is a heater."),
    dict(dur=5.2, title="THE SECRET", caption="They're not wires. They're silver paste, printed onto the inside of the glass."),
    dict(dur=6.2, title=None, caption="At the factory, the glass goes into an oven, and the silver fuses into its surface.", card='oven'),
    dict(dur=4.8, title="1 · BUS BARS", caption="Down each side runs a wider strip of silver, called a bus bar."),
    dict(dur=5.4, title="2 · CURRENT IN", caption="Press the defrost button, and twelve volts from the battery feed one bar."),
    dict(dur=5.6, title="3 · ACROSS", caption="The current splits and runs across every line at once, to the other bar."),
    dict(dur=6.0, title=None, caption="Each line is thin, so it resists the current, and that resistance becomes heat.", card='resist'),
    dict(dur=7.4, title="MELT", caption="The glass climbs above zero Celsius, thirty-two Fahrenheit, and the ice melts outward from each line."),
    dict(dur=5.6, title="SPACING", caption="The lines are spaced just right, so their warm bands meet in the middle."),
    dict(dur=6.0, title="SIDE BY SIDE", caption="They're wired side by side, so one scratched line leaves just one frosty stripe."),
    dict(dur=4.6, title="RECAP", caption="Silver line plus current equals a heater you can see through."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry (window seen from inside)
GT, GB = 470, 1130                      # glass top / bottom y
TL, TR, BL, BR = 230, 850, 110, 970     # glass corners x (top-left, top-right, bottom-left, bottom-right)
def xl(y): return lerp(TL, BL, (y - GT) / (GB - GT))
def xr(y): return lerp(TR, BR, (y - GT) / (GB - GT))
BAR_IN, BAR_W = 16, 22                  # bus bar inset from the glass edge / width
N = 12
LY = [545 + i * 49 for i in range(N)]   # heating line y (545 .. 1084)
SP = 49                                 # line spacing
BROKEN = 6                              # line that gets scratched (beat 10)
GAP_X = 560

SILVER = hexc('#b9b2a6'); LINE_C = hexc('#8a5a3c'); BAR_C = hexc('#a7a096')
FROST = hexc('#f8fbfc'); GLASS = hexc('#bcd7e3'); TRIM = hexc('#3b3842'); TRIM2 = hexc('#55505d')
WIRE_C = hexc('#e4472f'); WIRE_G = hexc('#26232b')

def bar_x_left(y): return xl(y) + BAR_IN
def bar_x_right(y): return xr(y) - BAR_IN
def line_x0(y): return bar_x_left(y) + BAR_W
def line_x1(y): return bar_x_right(y) - BAR_W

# wires (direction = list order = conventional current)
BATT = (150, 1330, 150, 96)             # battery box x 150..300, y 1330..1426
FEED = [(262, 1330), (262, 1215), (150, 1215), (150, GB - 6)]   # battery + -> button -> left bar bottom
BUTTON = (262, 1270)
GROUND_W = [(950, GB - 6), (950, 1340)]                          # right bar bottom -> ground
GROUND_P = (950, 1350)

def path_len(P):
    return sum(math.dist(P[i - 1], P[i]) for i in range(1, len(P)))
def path_at(P, s):
    for i in range(1, len(P)):
        d = math.dist(P[i - 1], P[i])
        if s <= d:
            u = s / max(1e-6, d); return (lerp(P[i - 1][0], P[i][0], u), lerp(P[i - 1][1], P[i][1], u))
        s -= d
    return P[-1]

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['hook'] = win(t, 0.15, B(1) + 0.3, 0.3)                  # lines light up one by one in beat 1
    s['hook_k'] = clamp((t - 0.2) / 1.6)                        # how many lines are lit (top -> bottom)
    s['tag_heater'] = win(t, 0.5, B(1) + 0.2, 0.3)
    s['silver'] = bw(t, 1)
    s['bars'] = max(bw(t, 3), 0.6 * bw(t, 10))
    s['wires'] = clamp(ease((t - B(4) - 0.2) / 0.6))
    s['press'] = clamp((t - B(4) - 0.8) / 0.25)                 # button pressed at B(4)+0.8
    s['cur'] = clamp(ease((t - B(4) - 1.0) / 0.8))              # current flows in the feed wire
    s['cur_lines'] = clamp(ease((t - B(5) - 0.2) / 0.8))        # current across the lines
    s['heat'] = clamp(ease((t - B(6) - 0.4) / 1.5))             # lines warm up (glow)
    # clear-band half-width (fraction of half the spacing): starts in beat 8, bands meet in beat 9
    m = 0.0
    if t > B(7): m = 0.62 * ease((t - B(7)) / (B(8) - B(7)))
    if t > B(8): m = 0.62 + 0.48 * ease((t - B(8)) / 3.2)
    s['melt'] = m
    s['l_bars'] = max(bw(t, 3, 4), 0.0)
    s['l_in'] = bw(t, 4); s['l_across'] = bw(t, 5)
    s['broken'] = clamp(ease((t - B(9) - 0.2) / 0.6)) * (1 - clamp(ease((t - B(10) - 0.1) / 0.6)))
    s['recap'] = bw(t, 10)
    return s

# ---------------------------------------------------------------- drawing
def glass_path(ctx):
    ctx.move_to(TL, GT); ctx.line_to(TR, GT); ctx.line_to(BR, GB); ctx.line_to(BL, GB); ctx.close_path()

def draw_outside(ctx, t):
    """what you see through the glass: sky, a road and a tree line (kept very pale)"""
    ctx.save(); glass_path(ctx); ctx.clip()
    g = cairo.LinearGradient(0, GT, 0, GB)
    g.add_color_stop_rgb(0, *hexc('#6fa9c4')[:3]); g.add_color_stop_rgb(0.62, *hexc('#b7d6e3')[:3])
    g.add_color_stop_rgb(0.63, *hexc('#8f9ca3')[:3]); g.add_color_stop_rgb(1, *hexc('#6f7c84')[:3])
    ctx.set_source(g); ctx.paint()
    rnd = random.Random(3)
    for i in range(16):                     # tree line on the horizon
        x = 100 + i * 60 + rnd.uniform(-10, 10); r = rnd.uniform(26, 44)
        ctx.arc(x, GT + 0.62 * (GB - GT) - r * 0.5, r, 0, 2 * math.pi); setc(ctx, hexc('#4f7a6f'), 0.85); ctx.fill()
    ctx.move_to(540, GT + 0.63 * (GB - GT)); ctx.line_to(380, GB); ctx.line_to(700, GB); ctx.close_path()
    setc(ctx, hexc('#59646b'), 0.8); ctx.fill()
    ctx.restore()

def draw_frost(ctx, t, s):
    """frost layer on the glass; clear bands are cut out around each heating line."""
    ctx.push_group()
    glass_path(ctx); setc(ctx, FROST, 0.96); ctx.fill()
    rnd = random.Random(11)
    ctx.save(); glass_path(ctx); ctx.clip()
    for i in range(260):                    # frost crystals
        x = rnd.uniform(BL, BR); y = rnd.uniform(GT, GB); r = rnd.uniform(4, 11)
        for k in range(3):
            a = k * math.pi / 3 + rnd.random()
            ctx.move_to(x - r * math.cos(a), y - r * math.sin(a)); ctx.line_to(x + r * math.cos(a), y + r * math.sin(a))
        setc(ctx, hexc('#9fc3d3'), 0.8); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    # cut the clear bands (DEST_OUT removes frost) — soft edges with 3 passes
    m = s['melt']
    if m > 0:
        ctx.set_operator(cairo.OPERATOR_DEST_OUT)
        for i, y in enumerate(LY):
            if i == BROKEN and s['broken'] > 0: continue
            for k, (f, al) in enumerate(((1.0, 0.45), (0.8, 0.6), (0.6, 1.0))):
                hw = SP / 2 * m * f + 3
                ctx.rectangle(BL, y - hw, BR - BL, 2 * hw); setc(ctx, WHITE, al); ctx.fill()
        # above the top line and below the last line the heat also clears a band
        ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source(); ctx.paint()
    # the scratched line: its stripe stays frosty (neighbours still clear their own half)
    b = s['broken']
    if b > 0 and m > 0:
        y = LY[BROKEN]; hw = SP / 2 * max(0.0, 1.0 - 0.62) + SP * 0.22
        ctx.save(); glass_path(ctx); ctx.clip()
        ctx.rectangle(BL, y - hw, BR - BL, 2 * hw); setc(ctx, FROST, 0.96 * b); ctx.fill()
        rnd = random.Random(5)
        for i in range(40):
            x = rnd.uniform(BL, BR); yy = y + rnd.uniform(-hw + 4, hw - 4); r = rnd.uniform(4, 9)
            ctx.move_to(x - r, yy); ctx.line_to(x + r, yy); ctx.move_to(x, yy - r); ctx.line_to(x, yy + r)
            setc(ctx, hexc('#9fc3d3'), 0.8 * b); ctx.set_line_width(2); ctx.stroke()
        ctx.restore()

def draw_lines(ctx, t, s):
    for i, y in enumerate(LY):
        x0, x1 = line_x0(y), line_x1(y)
        lit = s['hook'] * clamp(s['hook_k'] * N - i)            # beat 1: lit one by one, top -> bottom
        heat = s['heat']
        if i == BROKEN: heat *= (1 - s['broken'])
        g = max(lit, heat)
        col = lerpc(LINE_C, RED, g)
        if g > 0:                                               # warm glow around the line
            setc(ctx, ORANGE, 0.28 * g); ctx.set_line_width(16)
            ctx.move_to(x0, y); ctx.line_to(x1, y); ctx.stroke()
        if i == BROKEN and s['broken'] > 0:
            gw = 26 * s['broken']
            for (a0, a1) in ((x0, GAP_X - gw / 2), (GAP_X + gw / 2, x1)):
                ctx.move_to(a0, y); ctx.line_to(a1, y); setc(ctx, col); ctx.set_line_width(5); ctx.stroke()
        else:
            ctx.move_to(x0, y); ctx.line_to(x1, y); setc(ctx, col); ctx.set_line_width(5); ctx.stroke()

def draw_bars(ctx, t, s):
    for side in (0, 1):
        if side == 0:
            p = [(bar_x_left(GT + 30), GT + 30), (bar_x_left(GT + 30) + BAR_W, GT + 30),
                 (bar_x_left(GB - 8) + BAR_W, GB - 8), (bar_x_left(GB - 8), GB - 8)]
        else:
            p = [(bar_x_right(GT + 30) - BAR_W, GT + 30), (bar_x_right(GT + 30), GT + 30),
                 (bar_x_right(GB - 8), GB - 8), (bar_x_right(GB - 8) - BAR_W, GB - 8)]
        ctx.move_to(*p[0])
        for q in p[1:]: ctx.line_to(*q)
        ctx.close_path(); fill_stroke(ctx, BAR_C, stroke=INK2, lw=2.5)

def draw_current(ctx, t, s):
    """yellow dots = current. Feed wire -> left bar (going UP) -> lines (LEFT -> RIGHT) -> right bar (DOWN) -> ground."""
    a = s['cur']
    if a <= 0: return
    def dot(x, y, al):
        ctx.arc(x, y, 6.5, 0, 2 * math.pi); setc(ctx, MUSTARD, al); ctx.fill_preserve()
        setc(ctx, INK, 0.5 * al); ctx.set_line_width(1.5); ctx.stroke()
    L = path_len(FEED)
    for k in range(8):
        sx = ((t * 160) + k * L / 8) % L; q = path_at(FEED, sx)
        if math.dist(q, BUTTON) > 44: dot(*q, a)            # hidden while passing through the button
    # up the left bar (from the bottom feed point)
    for k in range(10):
        u = ((t * 0.5) + k / 10) % 1
        y = lerp(GB - 10, LY[0], u); dot(bar_x_left(y) + BAR_W / 2, y, a * 0.9)
    al = s['cur_lines']
    if al <= 0: return
    for i, y in enumerate(LY):
        x0, x1 = line_x0(y), line_x1(y)
        for k in range(5):
            u = ((t * 0.32) + k / 5 + i * 0.07) % 1
            x = lerp(x0, x1, u)
            if i == BROKEN and s['broken'] > 0.5 and x > GAP_X - 14: continue   # no current past the scratch
            if i == BROKEN and s['broken'] > 0.5: continue                       # nor on the dead line at all
            dot(x, y, al)
    for k in range(10):                              # down the right bar to the ground tab
        u = ((t * 0.5) + k / 10) % 1
        y = lerp(LY[0], GB - 10, u); dot(bar_x_right(y) - BAR_W / 2, y, al * 0.9)
    L = path_len(GROUND_W)
    for k in range(3):
        sx = ((t * 160) + k * L / 3) % L; dot(*path_at(GROUND_W, sx), al)

def ground_symbol(ctx, x, y, a):
    for k, w in enumerate((40, 26, 12)):
        ctx.move_to(x - w / 2, y + k * 9); ctx.line_to(x + w / 2, y + k * 9)
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def defrost_icon(ctx, cx, cy, sc, col, a):
    """the rear-defrost symbol: a rounded rectangle with three wavy arrows going up"""
    rrect(ctx, cx - 22 * sc, cy - 4 * sc, 44 * sc, 26 * sc, 5 * sc); setc(ctx, col, a); ctx.set_line_width(3); ctx.stroke()
    for k in (-1, 0, 1):
        x = cx + k * 12 * sc
        ctx.move_to(x, cy + 14 * sc)
        ctx.curve_to(x + 5 * sc, cy + 8 * sc, x - 5 * sc, cy + 2 * sc, x, cy - 4 * sc)
        ctx.curve_to(x + 5 * sc, cy - 10 * sc, x - 5 * sc, cy - 14 * sc, x, cy - 20 * sc)
        setc(ctx, col, a); ctx.set_line_width(3); ctx.stroke()

def draw_wiring(ctx, t, s):
    a = s['wires']
    if a <= 0: return
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for P, col in ((FEED, WIRE_C), (GROUND_W, WIRE_G)):
        ctx.move_to(*P[0])
        for q in P[1:]: ctx.line_to(*q)
        setc(ctx, INK, a); ctx.set_line_width(11); ctx.stroke_preserve()
        setc(ctx, col, a); ctx.set_line_width(6); ctx.stroke()
    ground_symbol(ctx, *GROUND_P, a)
    # battery
    x, y, w, h = BATT
    rrect(ctx, x, y, w, h, 10); fill_stroke(ctx, hexc('#3b3842'), lw=4, alpha=a)
    rrect(ctx, x + 98, y - 14, 26, 16, 3); fill_stroke(ctx, RED, lw=3, alpha=a)      # + terminal (right)
    rrect(ctx, x + 26, y - 14, 26, 16, 3); fill_stroke(ctx, hexc('#9aa3ab'), lw=3, alpha=a)  # - terminal
    text_c(ctx, "12 V", x + w / 2, y + 62, 34, CREAM, True, 1, a)
    text_c(ctx, "+", x + 111, y + 30, 26, RED, True, 0, a); text_c(ctx, "−", x + 39, y + 30, 26, CREAM, True, 0, a)
    ctx.move_to(x + 39, y - 14); ctx.line_to(x + 39, y - 40); ctx.line_to(x - 30, y - 40); ctx.line_to(x - 30, y + 30)
    setc(ctx, WIRE_G, a); ctx.set_line_width(6); ctx.stroke()
    ground_symbol(ctx, x - 30, y + 36, a)
    # defrost button on the feed wire
    bx, by = BUTTON
    p = s['press']; dip = 4 * math.sin(math.pi * clamp(p))
    lit = clamp(p * 2)
    rrect(ctx, bx - 40, by - 36 + dip, 80, 72, 12)
    fill_stroke(ctx, lerpc(hexc('#efe9dc'), hexc('#fde3b0'), lit), lw=4, alpha=a)
    defrost_icon(ctx, bx, by + 2 + dip, 1.0, lerpc(INK2, ORANGE, lit), a)
    ctx.arc(bx + 26, by - 22 + dip, 5, 0, 2 * math.pi); setc(ctx, lerpc(INK2, ORANGE, lit), a); ctx.fill()

def draw_car(ctx, t, s):
    # interior trim around the glass (we look from inside)
    ctx.move_to(TL - 60, GT - 60); ctx.line_to(TR + 60, GT - 60); ctx.line_to(BR + 70, GB + 20)
    ctx.line_to(BL - 70, GB + 20); ctx.close_path(); fill_stroke(ctx, TRIM, lw=5)
    draw_outside(ctx, t)
    draw_frost(ctx, t, s)
    draw_bars(ctx, t, s)
    draw_lines(ctx, t, s)
    glass_path(ctx); setc(ctx, INK, 1); ctx.set_line_width(5); ctx.stroke()
    # glass reflection
    ctx.move_to(TR - 120, GT + 30); ctx.line_to(TR - 60, GT + 30); ctx.line_to(TR - 260, GB - 120)
    ctx.line_to(TR - 320, GB - 120); ctx.close_path(); setc(ctx, WHITE, 0.10); ctx.fill()
    # parcel shelf + seat backs (one prop)
    rrect(ctx, 40, GB + 10, 1000, 58, 12); fill_stroke(ctx, TRIM2, lw=5)
    draw_wiring(ctx, t, s)
    draw_current(ctx, t, s)

def draw_overlays(ctx, t, s):
    # beat 1: "HEATER" tags on the lines
    tag(ctx, "EVERY LINE = A HEATER", 540, 420, RED, s['tag_heater'], 28)
    # beat 2: zoomed tags
    a = s['silver']
    if a > 0:
        y = LY[3]
        highlight(ctx, 470, y, 120, 26, RED, a, t)
        tag(ctx, "SILVER PASTE", 470, y - 62, INK, a, 22)
        tag(ctx, "INSIDE FACE", 470, y + 62, TEAL, a, 20)
    # bus bars
    a = s['bars']
    if a > 0:
        highlight(ctx, bar_x_left(800) + BAR_W / 2, 800, 40, 330, MUSTARD, a, t)
        highlight(ctx, bar_x_right(800) - BAR_W / 2, 800, 40, 330, MUSTARD, a, t)
    tag(ctx, "1 · BUS BAR", 245, 415, MUSTARD, s['l_bars'], 24)
    tag(ctx, "1 · BUS BAR", 835, 415, MUSTARD, s['l_bars'], 24)
    tag(ctx, "2 · CURRENT IN", 430, 1290, RED, s['l_in'], 24)
    a = s['l_across']
    if a > 0:
        tag(ctx, "3 · ACROSS EVERY LINE", 540, 420, MUSTARD, a, 26)
        straight_arrow(ctx, 380, 470, 700, 470, MUSTARD, a, lw=6, head=14)
        tag(ctx, "GROUND", 950, 1430, INK, a, 22)
    # scratched line
    b = s['broken']
    if b > 0:
        y = LY[BROKEN]
        for d in (1, -1):
            ctx.move_to(GAP_X - 22, y - 22 * d); ctx.line_to(GAP_X + 22, y + 22 * d)
            setc(ctx, RED, b); ctx.set_line_width(7); ctx.stroke()
        tag(ctx, "SCRATCH", GAP_X, y - 62, RED, b, 22)
        tag(ctx, "1 FROSTY STRIPE", 300, y + 62, TEAL, b, 22)
    tag(ctx, "SILVER + CURRENT = HEATER", 540, 420, RED, s['recap'], 28)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    draw_car(ctx, t, s)
    draw_overlays(ctx, t, s)

# camera: wide from the 1st second, push in on one line for "silver paste", back out for the card
CAMKEYS = [(0, 540, 900, 1.0), (B(1) + 0.2, 470, LY[3], 1.9), (B(2) - 0.3, 540, 900, 1.0)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.8)

def draw_hud(ctx, t, E):
    a = win(t, B(4) + 1.0, B(5), 0.3)
    if a > 0: hud(ctx, "FROM THE BATTERY", "12 V", "button on", a, RED, x=520, y=196, w=520)
    a = bw(t, 7)
    if a > 0:
        hud(ctx, "GLASS", "> 0 °C · 32 °F", "the ice melts", a, ORANGE, x=440, y=196, w=600)

SFX = [(0.3, 'pop'), (B(1) + 0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(4) + 0.8, 'click'),
       (B(5) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_oven(ctx, t, lt, a):
    card_frame(ctx, "AT THE FACTORY: THE OVEN", a, "THE SILVER FUSES INTO THE GLASS", RED)
    # oven walls + glowing elements above and below the glass
    rrect(ctx, 150, 260, 780, 280, 14); fill_stroke(ctx, hexc('#efe4cd'), lw=4, alpha=a)
    for yy in (290, 510):
        ctx.move_to(190, yy)
        for k in range(14): ctx.line_to(190 + (k + 0.5) * 50, yy + (8 if k % 2 == 0 else -8))
        ctx.line_to(890, yy); setc(ctx, RED, a); ctx.set_line_width(6); ctx.stroke()
    # heat arrows toward the glass (top ones point DOWN, bottom ones point UP)
    for x in (260, 540, 820):
        wavy_arrow(ctx, x, 305, x, 360, t, ORANGE, a, amp=6, wl=24, lw=5, head=11)
        wavy_arrow(ctx, x, 495, x, 455, t, ORANGE, a, amp=6, wl=24, lw=5, head=11)
    # the glass in cross-section (inside face UP)
    gy0, gy1 = 395, 445
    ctx.rectangle(200, gy0, 680, gy1 - gy0); fill_stroke(ctx, GLASS, lw=4, alpha=a)
    # silver paste beads on the top (inside) face: tall grey paste -> sink in, turn shiny
    k = ease((lt - 1.0) / 3.0)
    for i in range(7):
        cx = 260 + i * 94
        h = lerp(16, 6, k); d = lerp(0, 6, k)            # height above surface / depth below
        rrect(ctx, cx - 18, gy0 - h, 36, h + d, 4)
        fill_stroke(ctx, lerpc(hexc('#9a958c'), hexc('#d9d4ca'), k), stroke=INK2, lw=2.5, alpha=a)
    text_c(ctx, "INSIDE FACE (UP)", 330, 380 - 6, 20, TEAL, True, 1, a)
    text_c(ctx, "SILVER PASTE", 760, 380 - 6, 20, INK, True, 1, a)

def card_resist(ctx, t, lt, a):
    card_frame(ctx, "ONE LINE, UP CLOSE", a, "RESISTANCE = HEAT", RED)
    y0, y1 = 395, 425
    g = clamp(lt / 2.5)
    rrect(ctx, 170, y0, 740, y1 - y0, 10)
    fill_stroke(ctx, lerpc(LINE_C, RED, g), lw=4, alpha=a)
    text_c(ctx, "+", 140, 420, 40, RED, True, 0, a); ground_symbol(ctx, 945, 400, a)
    # current dots squeeze through (left -> right) and bump; each bump flashes
    rnd = random.Random(7)
    for i in range(16):
        u = (lt * 0.18 + rnd.random()) % 1
        x = 180 + u * 720; y = (y0 + y1) / 2 + 8 * math.sin(lt * 9 + i * 1.7)
        ctx.arc(x, y, 7, 0, 2 * math.pi); setc(ctx, MUSTARD, a); ctx.fill_preserve()
        setc(ctx, INK, 0.5 * a); ctx.set_line_width(1.5); ctx.stroke()
        f = max(0.0, math.sin(lt * 7 + i * 2.3)) ** 6
        if f > 0.05:
            ctx.arc(x + 9, y, 12, 0, 2 * math.pi); setc(ctx, ORANGE, 0.6 * f * a); ctx.fill()
    straight_arrow(ctx, 200, 340, 420, 340, MUSTARD, a, lw=5, head=12)
    text_c(ctx, "CURRENT", 310, 318, 22, INK, True, 1, a)
    # heat leaves the line into the glass (up and down)
    for x in (540, 690, 840):
        wavy_arrow(ctx, x, y0 - 8, x, 300, t, RED, a * g, amp=6, wl=24, lw=5, head=11)
    for x in (250, 400, 550, 700, 850):
        wavy_arrow(ctx, x, y1 + 8, x, 530, t, RED, a * g, amp=6, wl=24, lw=5, head=11)

CARDS = {'oven': card_oven, 'resist': card_resist}
