"""Cogwise episode: Wrap this tape the wrong way and it unwinds itself.
One idea: a turning fitting does not slide over PTFE tape, its threads rub the tape and DRAG it in the fitting's
direction of rotation. Wrapped against that turn, the loose end faces the oncoming threads, gets caught, peels back and
rolls into a rope (the spiral leak tunnel stays open). Wrapped with the turn, the same rub pulls every layer tighter.
Seen from the pipe's open end, a right-hand fitting goes on clockwise, so the tape is wrapped clockwise.
Context (spoken): threads never touch perfectly -> one spiral leak path; PTFE fills it and lubricates (threads go deeper).

VIEW (screen coordinates, y grows DOWN): main stage = END VIEW, looking straight at the pipe's open end.
  - Pipe = disc centred (CX, CY), bore radius R_B, thread crests at R_P. Tape layers just outside R_P, nut bore outside.
  - Screen-clockwise = INCREASING cairo angle (because y is down). The fitting (hex nut) turns clockwise: phi grows.
  - Tape laid from angle TH0 going dir * s: dir = +1 clockwise (right), dir = -1 counter-clockwise (wrong).
    The loose end is at s = S. Its cut edge faces direction dir.
    dir = -1: the edge faces the -angle side = the side the nut's teeth come FROM -> caught, peeled, dragged +angle.
    dir = +1: the teeth arrive over the laid tape and slide off the edge -> the rub pulls the layers tighter (+angle).
  - Peel card = the top of the pipe unrolled flat: outside is UP, clockwise = toward +x (right).
    Wrong-way strip: loose end on the LEFT, teeth move RIGHT, the rope rolls RIGHT over the strip.
  - Tunnel panel = side view of the threaded end (open end on the RIGHT); the drop zigzags along the helix
    (front of the thread solid, back dashed) and drips out on the right.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="thread-tape",
    title="Wrap this tape the wrong way and it unwinds itself 🔧 #Shorts",
    description=("The fitting doesn't slide over the tape. It drags it.\n\n"
                 "#Shorts #howthingswork #plumbing #diy #cogwise"),
    hashtags=["Shorts", "howthingswork", "plumbing", "diy", "home", "cogwise"],
    sources=[
        "https://blog.supplyhouse.com/how-to-use-ptfe-tape-and-thread-sealant-the-right-way/",
        "https://bobvila.com/interior/how-to-use-plumbers-tape",
        "https://www.lowes.com/n/how-to/use-plumbers-tape",
        "https://www.slashgear.com/1867536/pipe-thread-teflon-tape-leak-mistake",
    ],
)

def _d(c, extra=0.0):
    return round(0.42 * len(c.split()) + 0.7 + extra, 1)

_B = [
    ("THE WRONG WAY", "Wrap this tape the wrong way, and the fitting unwinds it for you.", None),
    ("THE SECRET", "A turning fitting doesn't just slide over the tape. It drags the tape along with it.", None),
    (None, "Even screwed tight, metal threads never touch perfectly. Tiny gaps remain.", 'gap'),
    ("1 · THE TUNNEL", "Those gaps form one spiral tunnel around the pipe, and water follows it out.", None),
    ("2 · THE TAPE", "This tape is PTFE, the slippery plastic on non-stick pans, thinner than paper.", None),
    ("PLUGGED", "Squashed into the threads, it plugs the tunnel, and lets them slide deeper.", None),
    ("3 · THE DRAG", "But as you turn the fitting, its threads rub the tape and pull it around.", None),
    ("WRAPPED BACKWARDS", "Wrapped against that turn, the loose end faces the threads. They catch it.", None),
    (None, "The tape peels back, rolls into a little rope, and the tunnel stays open.", 'peel'),
    ("WRAPPED RIGHT", "Wrapped with the turn, that same rub pulls every layer tighter instead.", None),
    ("CLOCKWISE", "Looking at the pipe's open end, that means clockwise, the way the fitting goes on.", None),
    ("SAME WAY", "The fitting always drags the tape its way. So wrap it that way too.", None),
]
BEATS = [dict(dur=_d(c), title=ti, caption=c, card=k) for ti, c, k in _B]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette
STEEL = hexc('#9aa0a8'); STEEL_D = hexc('#5d6168'); STEEL_L = hexc('#c9cdd3')
BRASS = hexc('#d9a441'); BRASS_D = hexc('#9c7222'); BRASS_L = hexc('#efcb7a')
TAPE = hexc('#ffffff'); TAPE_E = hexc('#9aa3ad')
WATER = hexc('#2f6fb3'); WATER_L = hexc('#8fb8e0')
GREEN = hexc('#3d8b4f')

# ---------------------------------------------------------------- geometry (end view)
CX, CY = 540, 1010
R_B = 128          # bore
R_P = 196          # thread crests of the pipe
LAYER = 7.0        # one tape layer (px, exaggerated)
R_N = R_P + 46     # nut bore (teeth reach inward)
R_HEX = 330        # hex nut vertex radius
TH0 = -math.pi / 2 # where the wrap starts (top)
TURNS = 3.5

def phi_of(t):
    """Nut rotation angle (clockwise = increasing). Turns during beats 0, 1, 6-9, 11."""
    on = [(0.2, B(1) - 0.2), (B(1) + 0.3, B(2) - 0.2), (B(6) + 0.2, B(10) - 0.2), (B(11) + 0.2, B(12) + 3)]
    acc = 0.0
    for a, b in on:
        if t > a: acc += min(t, b) - a
    return acc * 0.9

def state(t):
    s = {}
    s['nut'] = max(win(t, -1, B(2), 0.3), win(t, B(6), B(10), 0.3), win(t, B(11), B(12) + 3, 0.3))
    s['turning'] = 1.0 if (0.2 < t < B(2) - 0.2) or (B(6) + 0.2 < t < B(10) - 0.2) or t > B(11) + 0.2 else 0.0
    # wrong-way tape: hook (beat 0) and beats 7-8
    s['wrong'] = max(win(t, -1, B(1), 0.3), win(t, B(7), B(9), 0.35))
    if t < B(1):
        s['peel'] = ease(clamp((t - 0.5) / 3.6))
    else:
        s['peel'] = ease(clamp((t - B(7) - 1.2) / (B(9) - B(7) - 2.0)))
    # right-way tape: beat 1, 4-6, 9-12
    s['right'] = max(win(t, B(1), B(2), 0.3), win(t, B(4), B(7), 0.35), win(t, B(9), B(12) + 3, 0.35))
    # length laid (in turns) for the right-way tape: wrapped live by the roll on beats 4 and 10
    if B(4) <= t < B(5):
        s['laid'] = TURNS * ease(clamp((t - B(4) - 0.4) / (BEATS[4]['dur'] - 0.8)))
    elif B(10) <= t < B(11):
        s['laid'] = TURNS * ease(clamp((t - B(10) - 0.4) / (BEATS[10]['dur'] - 0.8)))
    else:
        s['laid'] = TURNS
    s['roll'] = max(win(t, B(4), B(5), 0.3), win(t, B(10), B(11), 0.3))
    s['squeeze'] = ease(clamp((t - B(9) - 0.8) / 2.5)) if t < B(10) else (1.0 if t > B(11) else 0.0)
    s['threads'] = 1.0
    s['endview'] = bw(t, 0, 2)
    s['drag'] = max(bw(t, 1), bw(t, 6))
    s['tape_tag'] = bw(t, 4)
    s['loose'] = bw(t, 7)
    s['wrong_tag'] = win(t, 1.4, B(1), 0.3)
    s['tight'] = win(t, B(9) + 0.6, B(10), 0.3)
    s['cw'] = win(t, B(10) + 0.3, B(11), 0.3)
    s['same'] = win(t, B(11) + 0.3, B(12) + 3, 0.3)
    return s

def P(r, ang):
    return CX + r * math.cos(ang), CY + r * math.sin(ang)

# ---------------------------------------------------------------- pipe (end view)
def pipe(ctx, t):
    # thread crests ring (rough, ticks) + body + bore
    ctx.arc(CX, CY, R_P, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=4)
    for i in range(72):                       # thread texture
        a = 2 * math.pi * i / 72
        x0, y0 = P(R_P - 14, a); x1, y1 = P(R_P - 2, a + 0.03)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1)
    setc(ctx, STEEL_D); ctx.set_line_width(2.5); ctx.stroke()
    ctx.arc(CX, CY, R_B, 0, 2 * math.pi)
    g = cairo.RadialGradient(CX, CY - 30, 10, CX, CY, R_B)
    g.add_color_stop_rgb(0, 0.20, 0.19, 0.22); g.add_color_stop_rgb(1, 0.36, 0.35, 0.38)
    ctx.set_source(g); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(CX - 40, CY - 50, 46, math.pi * 1.05, math.pi * 1.45); setc(ctx, WHITE, 0.25); ctx.set_line_width(6); ctx.stroke()

# ---------------------------------------------------------------- tape (spiral)
def spiral_pts(dirn, s0, s1, squeeze, n_per_turn=90):
    pts = []
    lay = LAYER * (1 - 0.45 * squeeze)
    n = max(2, int(abs(s1 - s0) * n_per_turn))
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n          # in turns
        r = R_P + 1 + lay * s
        pts.append(P(r, TH0 + dirn * 2 * math.pi * s))
    return pts, lay

def tape(ctx, t, dirn, laid, peel, squeeze, a):
    """Spiral of tape from s=0 to s=laid (turns). peel (0..1) = fraction of the outer turns lifted off by the nut."""
    if a <= 0 or laid <= 0.01: return
    lifted = 1.6 * peel                         # turns peeled back into a rope
    s_end = max(0.05, laid - lifted)
    ctx.push_group()
    pts, lay = spiral_pts(dirn, 0, s_end, squeeze)
    # white band: stroke the spiral thick (layers overlap into one band), then a thin edge line per layer
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    setc(ctx, TAPE); ctx.set_line_width(lay + 3); ctx.stroke()
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    setc(ctx, TAPE_E); ctx.set_line_width(1.4); ctx.stroke()
    # loose end: cut edge (radial ink tick) at s_end, slightly proud
    ang_e = TH0 + dirn * 2 * math.pi * s_end
    r_e = R_P + 1 + lay * s_end
    x0, y0 = P(r_e - 5, ang_e); x1, y1 = P(r_e + 6, ang_e)
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    if peel > 0.02:
        # rope: the peeled tape bunched up, dragged clockwise (+angle) by the nut from the attach point
        span = 0.3 + 1.3 * peel                  # radians of rope along the bore
        thick = 10 + 16 * peel
        rr = r_e + thick / 2 + 2
        n = 40
        ctx.new_path()
        for i in range(n + 1):
            u = i / n
            ang = ang_e + span * u
            wob = 2.5 * math.sin(u * 22 + t * 6)
            (ctx.move_to if i == 0 else ctx.line_to)(*P(rr + wob, ang))
        setc(ctx, INK); ctx.set_line_width(thick + 4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke_preserve()
        setc(ctx, TAPE); ctx.set_line_width(thick); ctx.stroke()
        for k in range(5):                       # crumple marks
            ang = ang_e + span * (0.15 + 0.17 * k)
            xa, ya = P(rr - thick / 2 + 1, ang); xb, yb = P(rr + thick / 2 - 1, ang + 0.04)
            ctx.move_to(xa, ya); ctx.line_to(xb, yb)
        setc(ctx, TAPE_E); ctx.set_line_width(2); ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

def tape_roll(ctx, t, dirn, laid, squeeze, a):
    """Roll of tape orbiting the pipe while laying the spiral (beats 4 and 10)."""
    if a <= 0 or laid >= TURNS - 0.01: return
    lay = LAYER * (1 - 0.45 * squeeze)
    ang = TH0 + dirn * 2 * math.pi * laid
    xe, ye = P(R_P + 1 + lay * laid, ang)
    rx, ry = P(R_P + 105, ang + dirn * 0.55)
    ctx.move_to(xe, ye); ctx.line_to(rx, ry); setc(ctx, TAPE_E, a); ctx.set_line_width(7); ctx.stroke()
    ctx.move_to(xe, ye); ctx.line_to(rx, ry); setc(ctx, TAPE, a); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(rx, ry, 44, 0, 2 * math.pi); fill_stroke(ctx, TAPE, lw=4, alpha=a)
    ctx.arc(rx, ry, 20, 0, 2 * math.pi); fill_stroke(ctx, MUSTARD, lw=3, alpha=a)

# ---------------------------------------------------------------- nut (end view, cut at the threads)
def nut(ctx, t, phi, a):
    if a <= 0: return
    ctx.push_group()
    ctx.new_path()
    for i in range(6):
        x, y = P(R_HEX, phi + math.pi / 6 + i * math.pi / 3)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    ctx.close_path()
    ctx.new_sub_path(); ctx.arc_negative(CX, CY, R_N, 2 * math.pi, 0)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    g = cairo.LinearGradient(CX - R_HEX, CY - R_HEX, CX + R_HEX, CY + R_HEX)
    g.add_color_stop_rgb(0, *BRASS_L[:3]); g.add_color_stop_rgb(1, *BRASS[:3])
    ctx.set_source(g); ctx.fill_preserve()
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    # inner thread teeth (point inward, rotate with the nut)
    for i in range(40):
        a0 = phi + 2 * math.pi * i / 40
        x0, y0 = P(R_N + 1, a0 - 0.06); x1, y1 = P(R_N - 12, a0); x2, y2 = P(R_N + 1, a0 + 0.06)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.line_to(x2, y2); ctx.close_path()
    setc(ctx, BRASS_D); ctx.fill()
    # marker dot so the rotation reads
    mx, my = P(R_HEX - 50, phi - math.pi / 2)
    ctx.arc(mx, my, 13, 0, 2 * math.pi); fill_stroke(ctx, RED, lw=3)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)

def turn_arrow(ctx, t, a, r=R_HEX + 45, a0=-2.2, a1=-0.9, label="TURN", col=RED, lw=9):
    """Clockwise arc arrow (cairo angle increasing = clockwise on screen)."""
    if a <= 0: return
    ctx.arc(CX, CY, r, a0, a1); setc(ctx, col, a); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    hx, hy = P(r, a1)
    tang = a1 + math.pi / 2                       # direction of travel for increasing angle
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(tang)
    ctx.move_to(14, 0); ctx.line_to(-14, -16); ctx.line_to(-14, 16); ctx.close_path()
    setc(ctx, col, a); ctx.fill(); ctx.restore()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    if label:
        lx, ly = P(r + 55, (a0 + a1) / 2)
        tag(ctx, label, lx, ly, col, a, 26)

def drag_arrows(ctx, t, a, col=RED, n=6, r=None):
    """Short tangent arrows on the tape pointing clockwise (+angle): the rub pulls the tape around."""
    if a <= 0: return
    r = r or R_P + 12
    for k in range(n):
        a0 = -0.5 + 2 * math.pi * k / n + (t * 0.6) % (2 * math.pi / n)
        x0, y0 = P(r, a0); x1, y1 = P(r, a0 + 0.32)
        ctx.arc(CX, CY, r, a0, a0 + 0.26); setc(ctx, col, a); ctx.set_line_width(6); ctx.stroke()
        tang = a0 + 0.32 + math.pi / 2
        ctx.save(); ctx.translate(x1, y1); ctx.rotate(tang)
        ctx.move_to(6, 0); ctx.line_to(-12, -10); ctx.line_to(-12, 10); ctx.close_path()
        setc(ctx, col, a); ctx.fill(); ctx.restore()

def draw_set(ctx):
    pass

def CAM(t):
    return 540, 930, 1.3

def draw(ctx, t, E):
    s = state(t)
    phi = phi_of(t)
    pipe(ctx, t)
    # wrong-way tape (counter-clockwise wrap), peeled by the nut
    tape(ctx, t, -1, TURNS, s['peel'], 0.0, s['wrong'])
    # right-way tape (clockwise wrap)
    tape(ctx, t, +1, s['laid'], 0.0, s['squeeze'], s['right'])
    tape_roll(ctx, t, +1, s['laid'], s['squeeze'], s['roll'])
    nut(ctx, t, phi, s['nut'])
    overlays(ctx, t, s, phi)

def overlays(ctx, t, s, phi):
    turn_arrow(ctx, t, s['nut'] * s['turning'] * (1 - s['cw']))
    a = s['endview']
    if a > 0:
        tag(ctx, "PIPE END VIEW", 280, 650, INK, a, 24)
    a = s['wrong_tag']
    if a > 0:
        highlight(ctx, *P(R_P + 30, TH0 - 2 * math.pi * (TURNS - 1.6 * s['peel']) + 0.4), 80, 70, RED, a, t)
        tag(ctx, "IT UNWINDS", 540, 1340, RED, a, 30)
    drag_arrows(ctx, t, s['drag'] * (1 - s['wrong']))
    if s['drag'] > 0:
        tag(ctx, "DRAGGED", 540, 1340, RED, s['drag'] * (1 - s['wrong']), 28)
    a = s['tape_tag']
    if a > 0:
        tag(ctx, "PTFE TAPE", 800, 700, INK, a, 28)
        straight_arrow(ctx, 760, 730, *P(R_P + 14, -1.05), INK, a, lw=4, head=10)
    a = s['loose']
    if a > 0:
        ang_e = TH0 - 2 * math.pi * (TURNS - 1.6 * s['peel'])
        highlight(ctx, *P(R_P + 14, ang_e), 46, 46, RED, a, t)
        tag(ctx, "LOOSE END", 300, 700, RED, a, 28)
        tag(ctx, "FACES THE TEETH", 540, 1340, RED, a, 26)
    a = s['tight']
    if a > 0:
        drag_arrows(ctx, t, a, GREEN)
        tag(ctx, "PULLED TIGHTER", 540, 1340, GREEN, a, 28)
    a = s['cw']
    if a > 0:
        turn_arrow(ctx, t, a, r=R_HEX - 20, a0=-2.6, a1=-0.5, label=None, col=GREEN, lw=11)
        tag(ctx, "CLOCKWISE", 540, 630, GREEN, a, 32)
        tag(ctx, "SEEN FROM THE OPEN END", 540, 1345, INK, a, 24)
    a = s['same']
    if a > 0:
        drag_arrows(ctx, t, a, GREEN)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=180, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def thread_profile(ctx, a, x0, x1, ym, pitch, fill_tape=0.0, gap=True):
    """Side profile of meshing threads: male teeth from below (steel), female teeth from above (brass).
    Truncated crests/roots leave small triangular gaps (dark) -> filled white by the tape when fill_tape > 0."""
    h = pitch * 0.55
    n = int((x1 - x0) / pitch)
    # female (top)
    ctx.move_to(x0, ym - h - 40)
    for i in range(n):
        x = x0 + i * pitch
        ctx.line_to(x, ym - h); ctx.line_to(x + pitch / 2 - 10, ym + h - 14); ctx.line_to(x + pitch / 2 + 10, ym + h - 14)
    ctx.line_to(x0 + n * pitch, ym - h); ctx.line_to(x0 + n * pitch, ym - h - 40); ctx.close_path()
    fill_stroke(ctx, BRASS, lw=3, alpha=a)
    # male (bottom)
    ctx.move_to(x0, ym + h + 40)
    for i in range(n):
        x = x0 + i * pitch
        ctx.line_to(x - 10 if i else x, ym - h + 14); ctx.line_to(x + 10, ym - h + 14) if i else None
        ctx.line_to(x + pitch / 2, ym + h)
    ctx.line_to(x0 + n * pitch, ym - h + 14); ctx.line_to(x0 + n * pitch, ym + h + 40); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=3, alpha=a)
    # gaps: at the female root (top) and at the male root (bottom)
    for i in range(n):
        x = x0 + i * pitch
        for (gx, gy, sg) in ((x, ym - h, -1), (x + pitch / 2, ym + h, 1)):
            if gx <= x0 + 2: continue
            ctx.move_to(gx - 10, gy - sg * 14); ctx.line_to(gx, gy + sg * 1); ctx.line_to(gx + 10, gy - sg * 14); ctx.close_path()
            if fill_tape > 0:
                setc(ctx, lerpc(INK, TAPE, fill_tape), a); ctx.fill_preserve()
                setc(ctx, TAPE_E, a * fill_tape); ctx.set_line_width(2); ctx.stroke()
            elif gap:
                setc(ctx, INK, a); ctx.fill()

def tunnel_panel(ctx, t, a):
    """Beat 3: side view of the threaded end, the drop follows the helix (front solid, back dashed), drips right."""
    _panel(ctx, a)
    x0, x1, y0, y1 = 140, 820, 250, 410
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    pitch = 68; sl = 26
    xs = [x0 + 20 + k * pitch for k in range(10)]
    for x in xs:
        if x + sl > x1: break
        ctx.move_to(x, y0); ctx.line_to(x + sl, y1)
    setc(ctx, STEEL_D, a); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "OPEN END", 900, 300, 22, INK, True, 1, a)
    straight_arrow(ctx, 880, 320, 840, 330, INK, a, lw=3, head=8)
    # helix path for the drop: front segment down (x -> x+sl), back segment up (x+sl -> x+pitch)
    lt = t - B(3) - 0.3
    u = clamp(lt / (BEATS[3]['dur'] - 0.6)) * 8.0
    k = int(u); f = u - k
    for j in range(min(k + 1, 9)):
        xa = xs[0] + j * pitch
        ff = 1.0 if j < k else f
        if ff <= 0: continue
        if ff <= 0.5:
            g = ff / 0.5
            ctx.move_to(xa + 5, y0); ctx.line_to(xa + 5 + sl * g, y0 + (y1 - y0) * g)
            setc(ctx, WATER, a); ctx.set_line_width(7); ctx.stroke()
        else:
            ctx.move_to(xa + 5, y0); ctx.line_to(xa + 5 + sl, y1); setc(ctx, WATER, a); ctx.set_line_width(7); ctx.stroke()
            g = (ff - 0.5) / 0.5
            ctx.set_dash([8, 8])
            ctx.move_to(xa + 5 + sl, y1); ctx.line_to(xa + 5 + sl + (pitch - sl) * g, y1 - (y1 - y0) * g)
            setc(ctx, WATER, 0.45 * a); ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
    # the drop at the head of the path
    j = min(k, 8); ff = f if k < 8 else 1.0
    xa = xs[0] + j * pitch
    if ff <= 0.5:
        dx, dy = xa + 5 + sl * ff / 0.5, y0 + (y1 - y0) * ff / 0.5
    else:
        g = (ff - 0.5) / 0.5; dx, dy = xa + 5 + sl + (pitch - sl) * g, y1 - (y1 - y0) * g
    if u < 8:
        ctx.arc(dx, dy, 12, 0, 2 * math.pi); fill_stroke(ctx, WATER_L, WATER, lw=3, alpha=a)
    else:
        dd = clamp((lt - (BEATS[3]['dur'] - 0.6)) / 0.8)
        ctx.arc(x1 + 20, y1 + 10 + 40 * dd, 12, 0, 2 * math.pi); fill_stroke(ctx, WATER_L, WATER, lw=3, alpha=a)
    text_c(ctx, "ONE SPIRAL TUNNEL", 480, 455, 30, WATER, True, 2, a)

def plug_panel(ctx, t, a):
    """Beat 5: the same profile, gaps filled white by the tape; slippery -> threads go deeper."""
    _panel(ctx, a)
    f = ease(clamp((t - B(5) - 0.4) / 1.2))
    thread_profile(ctx, a, 120, 820, 330, 70, fill_tape=f)
    text_c(ctx, "TAPE FILLS THE GAPS", 470, 455, 28, INK, True, 2, a)
    d = ease(clamp((t - B(5) - 2.0) / 1.0))
    if d > 0:
        straight_arrow(ctx, 900, 330, 900 - 60 * d, 330, RED, a * d, lw=7, head=14)
        text_c(ctx, "DEEPER", 900, 280, 24, RED, True, 1, a * d)

def recap_panel(ctx, t, a):
    _panel(ctx, a, y=185, h=190)
    text_c(ctx, "TURN WAY = WRAP WAY", 540, 265, 54, INK, True, 3, a)
    text_c(ctx, "CLOCKWISE FROM THE END", 540, 335, 36, GREEN, True, 3, a)

def draw_hud(ctx, t, E):
    a = win(t, B(3) + 0.2, B(4), 0.3)
    if a > 0: tunnel_panel(ctx, t, a)
    a = win(t, B(5) + 0.2, B(6), 0.3)
    if a > 0: plug_panel(ctx, t, a)
    a = win(t, B(11) + 0.4, B(12) + 2, 0.3)
    if a > 0: recap_panel(ctx, t, a)

SFX = [(0.2, 'click'), (1.4, 'pop'), (B(1) + 0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(4) + 0.3, 'pop'),
       (B(5) + 0.3, 'pop'), (B(6) + 0.2, 'click'), (B(7) + 0.3, 'pop'), (B(9) + 0.6, 'pop'),
       (B(10) + 0.3, 'pop'), (B(11) + 0.4, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_gap(ctx, t, lt, a):
    card_frame(ctx, "SCREWED TIGHT · ZOOMED IN", a, "METAL NEVER FITS PERFECTLY", RED)
    thread_profile(ctx, a, 150, 930, 390, 78)
    p = 0.5 + 0.5 * math.sin(lt * 5)
    for gx, gy in ((150 + 78 * 3, 390 - 37), (150 + 78 * 5.5, 390 + 37)):
        ctx.arc(gx, gy, 26, 0, 2 * math.pi); setc(ctx, RED, a * (0.6 + 0.4 * p)); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, "FITTING", 200, 290, 20, BRASS_D, True, 1, a)
    text_c(ctx, "PIPE", 190, 510, 20, STEEL_D, True, 1, a)
    text_c(ctx, "GAP", 150 + 78 * 3, 300, 24, RED, True, 1, a)

def card_peel(ctx, t, lt, a):
    """Top of the pipe unrolled flat: outside UP, clockwise = +x. Wrong-way strip: loose end on the LEFT.
    Teeth move right, catch the left edge, and roll the tape into a rope that travels right over the strip."""
    card_frame(ctx, "WRAPPED BACKWARDS · UNROLLED", a, "CAUGHT · PEELED · ROLLED UP", RED)
    ys = 445                      # pipe surface (outside is up)
    ctx.rectangle(130, ys, 820, 70); fill_stroke(ctx, STEEL, lw=3, alpha=a)
    for k in range(16):
        x = 140 + k * 52
        ctx.move_to(x, ys + 6); ctx.line_to(x + 18, ys + 64)
    setc(ctx, STEEL_D, a); ctx.set_line_width(2.5); ctx.stroke()
    text_c(ctx, "PIPE", 905, ys + 45, 20, INK, True, 1, a)
    x_end0, x_far = 260, 930
    th = 14
    m = ease(clamp((lt - 1.0) / 3.2))
    xr = x_end0 + 380 * m                        # where the rope is now
    rad = 9 + 34 * math.sqrt(m)
    # remaining flat tape from the rope to the far end
    ctx.rectangle(xr, ys - th, x_far - xr, th); fill_stroke(ctx, TAPE, TAPE_E, lw=2, alpha=a)
    text_c(ctx, "TAPE", 800, ys - 26, 20, INK2, True, 1, a)
    if m < 0.03:
        # loose end lifted a little: the first tooth hooks under it
        ctx.move_to(x_end0, ys - th); ctx.line_to(x_end0 - 26, ys - th - 30)
        setc(ctx, TAPE_E, a); ctx.set_line_width(th + 3); ctx.stroke()
        ctx.move_to(x_end0, ys - th); ctx.line_to(x_end0 - 26, ys - th - 30)
        setc(ctx, TAPE, a); ctx.set_line_width(th - 2); ctx.stroke()
        tag(ctx, "LOOSE END", x_end0 - 90, ys - 62, RED, a, 22)
    else:
        cy = ys - th - rad
        ctx.arc(xr, cy, rad, 0, 2 * math.pi); fill_stroke(ctx, TAPE, INK, lw=3, alpha=a)
        for k in range(3):
            ctx.arc(xr, cy, rad * (0.28 + 0.22 * k), lt * 4 + k, lt * 4 + k + 4)
            setc(ctx, TAPE_E, a); ctx.set_line_width(2.5); ctx.stroke()
        # rolling direction: the rope travels right (clockwise)
        straight_arrow(ctx, xr + rad + 14, cy, xr + rad + 70, cy, RED, a, lw=6, head=12)
    # fitting with its teeth, moving right (clockwise), tips just above the tape
    tip = ys - th - 2 * (9 + 34) + 4
    ctx.rectangle(110, 255, 860, tip - 255 - 34); fill_stroke(ctx, BRASS, lw=3, alpha=a)
    shift = (lt * 70) % 60
    for k in range(17):
        x = 90 + k * 60 + shift
        if x < 130 or x > 950: continue
        ctx.move_to(x - 18, tip - 34); ctx.line_to(x, tip); ctx.line_to(x + 18, tip - 34); ctx.close_path()
        fill_stroke(ctx, BRASS, lw=3, alpha=a)
    straight_arrow(ctx, 400, 282, 640, 282, RED, a, lw=8, head=16)
    text_c(ctx, "FITTING TURNS", 790, 292, 24, INK, True, 1, a)

CARDS = {'gap': card_gap, 'peel': card_peel}
