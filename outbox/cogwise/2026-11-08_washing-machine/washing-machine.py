"""Cogwise episode: Your washing machine is full of concrete.
One idea: the suspended tub carries ~25 kg of concrete so the spin's off-balance tug only makes it wobble.

FRONT VIEW, cut away (front panel removed). Screen coordinates: y grows DOWN, so an increasing
angle theta in (cos theta, sin theta) turns CLOCKWISE on screen.
Physics used for the picture: above the suspension's resonance (true at full spin), the tub and the
lump orbit around their common centre of mass, so the tub centre is displaced OPPOSITE the lump, by
about m_lump * r / M_tub. The tug (force on the tub, through the drum's shaft) points TOWARD the lump.
More mass M -> smaller orbit: that is the whole episode.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="washing-machine",
    title="Your washing machine is full of concrete 🧱",
    description=("About 25 kg (55 lb) of concrete rides on the drum so the spin cycle only wobbles.\n\n"
                 "#Shorts #howthingswork #washingmachine #appliances #cogwise"),
    hashtags=["Shorts", "howthingswork", "washingmachine", "appliances", "engineering", "cogwise"],
    sources=[
        "https://www.whitegoodshelp.co.uk/device-replace-concrete-weight-washing-machines/",
        "https://newatlas.com/plastic-counterweight-washing-machine-concrete/50769",
        "https://www.whitegoodshelp.co.uk/how-does-drum-capacity-affect-spin-efficiency/",
        "https://www.whitegoodshelp.co.uk/?p=15804",
    ],
)

BEATS = [
    dict(dur=6.0, title="HIDDEN CONCRETE", caption="There are about twenty-five kilos of concrete inside your washing machine. Fifty-five pounds."),
    dict(dur=5.0, title="TWO BLOCKS", caption="Under the lid: one block on the tub's top, another at its front."),
    dict(dur=6.4, title="THE TUB HANGS", caption="Because the tub isn't bolted down. It hangs on springs and sits on shock absorbers."),
    dict(dur=4.6, title="FULL SPIN", caption="At full spin, the drum turns about fourteen hundred times a minute."),
    dict(dur=5.4, title="THE LUMP", caption="But wet clothes never spread evenly. One side of the drum is always heavier."),
    dict(dur=5.4, title="OFF BALANCE", caption="That lump swings around and tugs the tub sideways, over twenty times a second."),
    dict(dur=6.0, title=None, caption="Heavy things are hard to shake, so concrete turns a hard tug into a wobble.", card='mass'),
    dict(dur=5.6, title="SPRINGS + DAMPERS", caption="The springs let the tub float, and the shock absorbers soak up what's left."),
    dict(dur=5.4, title="WITHOUT IT", caption="Without that weight, the whole machine would hop and walk across your floor."),
    dict(dur=5.4, title="WHY CONCRETE", caption="Why concrete? It's cheap, dense, and does nothing but sit there being heavy."),
    dict(dur=6.0, title=None, caption="Modern plastic tubs are lighter than old steel ones, so concrete adds the weight back.", card='tubs'),
    dict(dur=4.6, title="CONCRETE = CALM", caption="So the calmest part of your washer is a block of concrete."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
CAB = (200, 430, 680, 1030)              # cabinet x, y, w, h -> 200..880, 430..1460
TC = (540, 1010)                         # tub centre at rest
TUB_R, DRUM_R, DOOR_R = 300, 250, 150
TOPB = (-130, -372, 260, 66)             # top block, relative to tub centre (x, y, w, h)
FRONT_A = (math.radians(28), math.radians(152))   # front block: lower crescent (sin > 0 = below centre)
FRONT_R = (258, 300)
SPR_TOP = [(262, 470), (818, 470)]       # spring hooks on the cabinet top
SPR_ANG = [math.radians(-150), math.radians(-30)]   # attach points on the tub (upper left / upper right)
DMP_BOT = [(300, 1430), (780, 1430)]     # damper feet on the cabinet base
DMP_ANG = [math.radians(122), math.radians(58)]     # attach points on the tub (lower left / lower right)

CONC = hexc('#a7a39b'); CONC_D = hexc('#7e7a73'); STEEL = hexc('#c9ced3'); STEEL_D = hexc('#9aa3ab')
CABC = hexc('#f4f1ea'); TUBC = hexc('#dfe3e1'); DRUMC = hexc('#eef0ee'); CLOTH = hexc('#8fcfc8')
LUMP = hexc('#e4472f')

# ---------------------------------------------------------------- drum angle (integrated speed)
def omega(t):
    """visual drum speed, rad/s (positive = clockwise on screen)."""
    if t < B(3): return 1.6                                   # slow tumble
    if t < B(4): return lerp(1.6, 30.0, ease((t - B(3)) / 2.2))  # spin-up to "1400 rpm" (blurred)
    if t < B(4) + 0.8: return lerp(30.0, 3.4, ease((t - B(4)) / 0.8))  # cut to slow motion
    if t < B(8): return 3.4
    if t < B(9): return 4.2
    return 3.0
_DT = 0.01
_PHI = [0.0]
for _i in range(int(ST[-1] / _DT) + 400):
    _PHI.append(_PHI[-1] + omega(_i * _DT) * _DT)
def phi(t):
    k = clamp(t / _DT, 0, len(_PHI) - 2); i = int(k)
    return lerp(_PHI[i], _PHI[i + 1], k - i)

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['open'] = ease(t / 0.9)                                 # front panel slides away in the 1st second
    s['blocks_hl'] = win(t, 0.6, B(2), 0.3)
    s['l_top'] = max(bw(t, 1, 3), bw(t, 9, 10), bw(t, 11, 12))
    s['l_front'] = s['l_top']
    s['l_spr'] = max(bw(t, 2), bw(t, 7), bw(t, 11, 12))
    s['l_dmp'] = s['l_spr']
    s['gap'] = bw(t, 2)                                       # "not bolted": show the free gap
    s['h_spr'] = bw(t, 7); s['h_dmp'] = bw(t, 7)
    s['h_blocks2'] = bw(t, 9)
    s['spin'] = win(t, B(3) + 0.3, B(4) + 0.5, 0.3)           # motion blur
    s['ring'] = ease((t - B(3) - 0.2) / 0.8)                  # clothes pinned to the drum wall
    s['lump'] = ease((t - B(4) - 0.3) / 0.8)
    s['slowmo'] = win(t, B(4) + 0.6, B(9), 0.3)
    s['force'] = max(bw(t, 5, 6), bw(t, 7, 9))
    s['l_heavy'] = bw(t, 4)
    # orbit amplitude of the tub (px): bigger without the blocks
    no_blocks = win(t, B(8) + 0.2, B(9), 0.6)
    s['noblocks'] = no_blocks
    amp = 0.0
    if t > B(4) + 0.6: amp = 9.0 * ease((t - B(4) - 0.6) / 1.0)
    amp = lerp(amp, 46.0, no_blocks)
    if t > B(11): amp = lerp(amp, 4.0, ease((t - B(11)) / 1.0))
    th = phi(t) + 0.6                                         # lump angle (screen, clockwise)
    s['th'] = th
    s['off'] = (-amp * math.cos(th) * s['lump'], -amp * math.sin(th) * s['lump'])   # OPPOSITE the lump
    # the whole machine hops and walks (only without the blocks)
    lt = t - B(8) - 0.5
    if no_blocks > 0 and lt > 0:
        hop = abs(math.sin(math.pi * lt / 0.45))
        walk = 14.0 * (lt / 0.45)
        s['cab'] = (walk * no_blocks, -16.0 * hop * no_blocks)
    else:
        s['cab'] = (0.0, 0.0)
    s['ghost'] = no_blocks
    return s

# ---------------------------------------------------------------- parts
def spring(ctx, x0, y0, x1, y1, a, coils=9, w=18, col=INK):
    L = math.dist((x0, y0), (x1, y1)); ang = math.atan2(y1 - y0, x1 - x0)
    ctx.save(); ctx.translate(x0, y0); ctx.rotate(ang)
    ctx.move_to(0, 0); ctx.line_to(18, 0)
    n = coils * 2
    for i in range(n + 1):
        x = 18 + (L - 36) * i / n
        ctx.line_to(x, w if i % 2 else -w)
    ctx.line_to(L, 0)
    setc(ctx, col, a); ctx.set_line_width(6); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.restore()

def damper(ctx, xb, yb, xt, yt, a):
    """shock absorber: body (cylinder) on the cabinet base, rod up to the tub."""
    L = math.dist((xb, yb), (xt, yt)); ang = math.atan2(yt - yb, xt - xb)
    ctx.save(); ctx.translate(xb, yb); ctx.rotate(ang)
    body = 120
    ctx.move_to(body - 6, 0); ctx.line_to(L, 0); setc(ctx, INK, a); ctx.set_line_width(14); ctx.stroke()
    ctx.move_to(body - 6, 0); ctx.line_to(L, 0); setc(ctx, STEEL, a); ctx.set_line_width(7); ctx.stroke()
    rrect(ctx, 0, -20, body, 40, 10); fill_stroke(ctx, hexc('#5f6a73'), lw=5, alpha=a)
    ctx.restore()
    ctx.arc(xb, yb, 9, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)
    ctx.arc(xt, yt, 9, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)

def concrete(ctx, a=1.0, dashed=False):
    """fill the current path as a concrete block (or dashed 'missing' outline)."""
    if dashed:
        ctx.set_dash([12, 9]); setc(ctx, CONC_D, a); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
        return
    ctx.save(); ctx.clip_preserve()
    x0, y0, x1, y1 = ctx.fill_extents()
    setc(ctx, CONC, a); ctx.fill_preserve()
    path = ctx.copy_path()
    rnd = random.Random(7)
    ctx.new_path()
    for _ in range(int((x1 - x0) * (y1 - y0) / 500)):
        ctx.arc(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(1.5, 3.5), 0, 2 * math.pi)
        setc(ctx, CONC_D, a * 0.7); ctx.fill()
    ctx.restore()
    ctx.new_path(); ctx.append_path(path)
    setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()

def front_block_path(ctx, cx, cy):
    a0, a1 = FRONT_A; r0, r1 = FRONT_R
    ctx.new_path(); ctx.arc(cx, cy, r1, a0, a1); ctx.arc_negative(cx, cy, r0, a1, a0); ctx.close_path()

def draw_drum(ctx, cx, cy, t, s):
    # drum (inner, perforated, turns)
    ctx.arc(cx, cy, DRUM_R, 0, 2 * math.pi); fill_stroke(ctx, DRUMC, lw=5)
    ph = phi(t)
    rnd = random.Random(3)
    for k in range(40):
        aa = ph + k * 2 * math.pi / 40; rr = DRUM_R - 22 - 30 * (k % 2)
        ctx.arc(cx + rr * math.cos(aa), cy + rr * math.sin(aa), 4, 0, 2 * math.pi); setc(ctx, STEEL_D); ctx.fill()
    # laundry: a pile in the bottom (tumble), then pinned to the wall as a ring
    ring = s['ring']
    if ring < 1:
        ctx.save(); ctx.arc(cx, cy, DRUM_R - 6, 0, 2 * math.pi); ctx.clip()
        rnd = random.Random(11)
        for i in range(16):
            px = cx + rnd.uniform(-150, 150) + 12 * math.sin(t * 1.6 + i)
            py = cy + DRUM_R - rnd.uniform(30, 110) + 6 * math.cos(t * 1.6 + i)
            ctx.arc(px, py, rnd.uniform(26, 40), 0, 2 * math.pi); setc(ctx, CLOTH, 1 - ring); ctx.fill_preserve()
            setc(ctx, INK2, 0.6 * (1 - ring)); ctx.set_line_width(2); ctx.stroke()
        ctx.restore()
    if ring > 0:
        ctx.new_path(); ctx.arc(cx, cy, DRUM_R - 8, 0, 2 * math.pi); ctx.arc_negative(cx, cy, DRUM_R - 38, 2 * math.pi, 0)
        setc(ctx, CLOTH, ring); ctx.fill()
    # lifters (3 paddles, turn with the drum)
    for k in range(3):
        aa = ph + k * 2 * math.pi / 3
        ctx.save(); ctx.translate(cx + (DRUM_R - 26) * math.cos(aa), cy + (DRUM_R - 26) * math.sin(aa)); ctx.rotate(aa)
        rrect(ctx, -22, -16, 44, 32, 8); fill_stroke(ctx, STEEL, lw=4); ctx.restore()
    # the lump (heavy side), at angle th
    if s['lump'] > 0:
        th = s['th']; rr = DRUM_R - 40
        lx, ly = cx + rr * math.cos(th), cy + rr * math.sin(th)
        ctx.arc(lx, ly, 46 * s['lump'], 0, 2 * math.pi); fill_stroke(ctx, LUMP, lw=4, alpha=s['lump'])
        for j in range(3):
            ctx.arc(lx + 18 * math.cos(th + j * 2), ly + 18 * math.sin(th + j * 2), 9, 0, 2 * math.pi)
            setc(ctx, hexc('#b8321f'), s['lump']); ctx.fill()
    # motion blur at full spin
    if s['spin'] > 0:
        for k in range(10):
            a0 = ph * 0.37 + k * 0.63
            ctx.arc(cx, cy, DRUM_R - 20 - k * 18, a0, a0 + 1.6)
            setc(ctx, INK2, 0.35 * s['spin']); ctx.set_line_width(4); ctx.stroke()
    # hub
    ctx.arc(cx, cy, 20, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=4)

def draw_machine(ctx, t, s):
    cxo, cyo = s['cab']
    x, y, w, h = CAB
    # ghost: where the machine should stand
    if s['ghost'] > 0:
        rrect(ctx, x, y, w, h, 18); ctx.set_dash([14, 10]); setc(ctx, INK2, s['ghost'])
        ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    ctx.save(); ctx.translate(cxo, cyo)
    # feet
    for fx in (x + 60, x + w - 60):
        rrect(ctx, fx - 30, y + h - 4, 60, 40, 6); fill_stroke(ctx, hexc('#5f6a73'), lw=4)
    # cabinet (cut away: back wall visible)
    rrect(ctx, x, y, w, h, 18); fill_stroke(ctx, CABC, lw=6)
    rrect(ctx, x + 18, y + 18, w - 36, h - 36, 10); setc(ctx, hexc('#e6e1d6')); ctx.fill()
    # worktop / lid
    rrect(ctx, x - 6, y - 26, w + 12, 34, 8); fill_stroke(ctx, hexc('#e9e4da'), lw=5)

    ox, oy = s['off']; cx, cy = TC[0] + ox, TC[1] + oy
    # springs (cabinet top -> upper sides of the tub), stretched by the tub's motion
    for (hx, hy), aa in zip(SPR_TOP, SPR_ANG):
        px, py = cx + (TUB_R - 6) * math.cos(aa), cy + (TUB_R - 6) * math.sin(aa)
        spring(ctx, hx, hy, px, py, 1.0)
        ctx.arc(hx, hy, 9, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=4)
    # dampers (cabinet base -> lower sides of the tub)
    for (bx, by), aa in zip(DMP_BOT, DMP_ANG):
        px, py = cx + (TUB_R - 6) * math.cos(aa), cy + (TUB_R - 6) * math.sin(aa)
        damper(ctx, bx, by, px, py, 1.0)
    # gap shown when "not bolted down"
    if s['gap'] > 0:
        ctx.arc(cx, cy, TUB_R + 26, 0, 2 * math.pi); ctx.set_dash([10, 10]); setc(ctx, TEAL, s['gap'])
        ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    # tub (outer, still)
    ctx.arc(cx, cy, TUB_R, 0, 2 * math.pi); fill_stroke(ctx, TUBC, lw=6)
    draw_drum(ctx, cx, cy, t, s)
    # door seal ring (porthole) - front face cut away, keep its outline
    ctx.arc(cx, cy, DOOR_R, 0, 2 * math.pi); ctx.set_dash([8, 8]); setc(ctx, INK2, 0.7); ctx.set_line_width(3)
    ctx.stroke(); ctx.set_dash([])
    # concrete: top block (on top of the tub) + front block (lower crescent on the front rim)
    nb = s['noblocks']
    tx, ty, tw, th_ = TOPB
    for bxx in (cx + tx + 30, cx + tx + tw - 30):            # brackets bolting the block to the tub
        ctx.rectangle(bxx - 8, cy + ty + th_ - 4, 16, 28); fill_stroke(ctx, STEEL_D, lw=3)
    rrect(ctx, cx + tx, cy + ty, tw, th_, 8); concrete(ctx, 1 - nb)
    if nb > 0: rrect(ctx, cx + tx, cy + ty, tw, th_, 8); concrete(ctx, nb, dashed=True)
    front_block_path(ctx, cx, cy); concrete(ctx, 1 - nb)
    if nb > 0: front_block_path(ctx, cx, cy); concrete(ctx, nb, dashed=True)

    # tug (force on the tub, through the shaft) points TOWARD the lump
    if s['force'] > 0 and s['lump'] > 0:
        th = s['th']; L = 130 + 40 * nb
        straight_arrow(ctx, cx, cy, cx + L * math.cos(th), cy + L * math.sin(th), RED, s['force'], lw=10, head=20)
    # rotation sense (clockwise on screen), drawn outside the tub upper-right
    ra = max(s['slowmo'], s['spin'])
    if ra > 0:
        ctx.arc(cx, cy, TUB_R + 48, math.radians(-75), math.radians(-25)); setc(ctx, INK, ra); ctx.set_line_width(6); ctx.stroke()
        e = math.radians(-25); ex, ey = cx + (TUB_R + 48) * math.cos(e), cy + (TUB_R + 48) * math.sin(e)
        straight_arrow(ctx, ex - 14 * math.cos(e + math.pi / 2), ey - 14 * math.sin(e + math.pi / 2), ex, ey, INK, ra, lw=6, head=14)

    # highlights
    highlight(ctx, cx, cy + ty + th_ / 2, tw / 2 + 40, th_ / 2 + 30, MUSTARD, max(s['blocks_hl'], s['h_blocks2']), t)
    highlight(ctx, cx, cy + 250, 210, 70, MUSTARD, max(s['blocks_hl'], s['h_blocks2']), t)
    for (hx, hy), aa in zip(SPR_TOP, SPR_ANG):
        px, py = cx + TUB_R * math.cos(aa), cy + TUB_R * math.sin(aa)
        highlight(ctx, (hx + px) / 2, (hy + py) / 2, 50, 200, TEAL, s['h_spr'], t)
    for (bx, by), aa in zip(DMP_BOT, DMP_ANG):
        px, py = cx + TUB_R * math.cos(aa), cy + TUB_R * math.sin(aa)
        highlight(ctx, (bx + px) / 2, (by + py) / 2, 60, 110, ORANGE, s['h_dmp'], t)
    ctx.restore()

    # tags (not shaken)
    tag(ctx, "1 · TOP BLOCK", 540, 590, MUSTARD, s['l_top'])
    tag(ctx, "2 · FRONT BLOCK", 540, 1358, MUSTARD, s['l_front'])
    tag(ctx, "3 · SPRINGS", 175, 640, TEAL, s['l_spr'])
    tag(ctx, "4 · DAMPERS", 905, 1395, ORANGE, s['l_dmp'])
    tag(ctx, "NOT BOLTED", 905, 760, TEAL, s['gap'])
    tag(ctx, "HEAVY SIDE", 905, 860, RED, s['l_heavy'])
    tag(ctx, "SLOW MOTION", 960, 1160, INK2, s['slowmo'] * (1 - s['noblocks']), 22)
    if s['ghost'] > 0:
        tag(ctx, "NO CONCRETE", 540, 590, RED, s['ghost'])

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_machine(ctx, t, state(t))

CAMKEYS = [(0, 540, 960, 1.0)]
def CAM(t): return cam_track(CAMKEYS, t)

def draw_hud(ctx, t, E):
    s = state(t)
    # 1st second: the front panel slides off to the left, revealing the inside
    if s['open'] < 1:
        x, y, w, h = CAB; dx = -900 * s['open']
        rrect(ctx, x + dx, y, w, h, 18); fill_stroke(ctx, CABC, lw=6)
        ctx.arc(TC[0] + dx, TC[1], 210, 0, 2 * math.pi); fill_stroke(ctx, hexc('#d6dadd'), lw=6)
        ctx.arc(TC[0] + dx, TC[1], 160, 0, 2 * math.pi); fill_stroke(ctx, hexc('#bcd7dc'), lw=5)
        rrect(ctx, x + 40 + dx, y + 30, 260, 70, 10); fill_stroke(ctx, hexc('#e9e4da'), lw=4)
    a0 = win(t, 0.5, B(1), 0.3)
    if a0 > 0: hud(ctx, "HIDDEN CONCRETE", "≈ 25 kg · 55 lb", None, a0, MUSTARD, x=520, y=196, w=520)
    a3 = bw(t, 3)
    if a3 > 0:
        rpm = round(lerp(0, 1400, ease((t - B(3)) / 2.2)) / 10) * 10
        hud(ctx, "DRUM SPEED", f"{rpm:,} rpm".replace(",", " "), None, a3, TEAL, x=520, y=196, w=520)
    a5 = bw(t, 5)
    if a5 > 0: hud(ctx, "AT 1 400 rpm", "≈ 23 tugs / s", "every turn, one tug", a5, RED, x=520, y=196, w=520)
    a9 = bw(t, 9)
    if a9 > 0: hud(ctx, "WHY CONCRETE?", "cheap · dense", "and it just sits there", a9, MUSTARD, x=520, y=196, w=520)

SFX = [(0.5, 'pop'), (B(1) + 0.3, 'pop'), (B(1) + 1.6, 'pop'), (B(2) + 0.3, 'pop'), (B(2) + 2.4, 'pop'),
       (B(3) + 0.2, 'click'), (B(4) + 0.4, 'pop'), (B(5) + 0.3, 'pop'), (B(7) + 0.3, 'pop'),
       (B(8) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(11) + 0.2, 'ding')]
HUM = []

# ---------------------------------------------------------------- cards
def _mini_tub(ctx, cx, cy, th, amp, a, heavy, lt):
    """tub centre orbits OPPOSITE the lump (common centre of mass), radius amp."""
    ox, oy = -amp * math.cos(th), -amp * math.sin(th)
    # orbit trail of the tub centre
    ctx.arc(cx, cy, max(amp, 1), 0, 2 * math.pi); ctx.set_dash([6, 6]); setc(ctx, INK2, a)
    ctx.set_line_width(3); ctx.stroke(); ctx.set_dash([])
    tx, ty = cx + ox, cy + oy
    ctx.arc(tx, ty, 78, 0, 2 * math.pi); fill_stroke(ctx, TUBC, lw=4, alpha=a)
    ctx.arc(tx, ty, 62, 0, 2 * math.pi); fill_stroke(ctx, DRUMC, lw=3, alpha=a)
    if heavy:
        rrect(ctx, tx - 50, ty - 112, 100, 30, 6); concrete(ctx, a)
        ctx.new_path(); ctx.arc(tx, ty, 92, math.radians(35), math.radians(145))
        ctx.arc_negative(tx, ty, 80, math.radians(145), math.radians(35)); ctx.close_path(); concrete(ctx, a)
    lx, ly = tx + 46 * math.cos(th), ty + 46 * math.sin(th)
    ctx.arc(lx, ly, 15, 0, 2 * math.pi); fill_stroke(ctx, LUMP, lw=3, alpha=a)
    straight_arrow(ctx, tx, ty, tx + 70 * math.cos(th), ty + 70 * math.sin(th), RED, a, lw=6, head=12)
    ctx.arc(cx, cy, 4, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()

def card_mass(ctx, t, lt, a):
    card_frame(ctx, "SAME TUG, DIFFERENT MASS", a, "MORE MASS = SMALLER WOBBLE", RED)
    th = 3.0 * lt + 0.6                                   # clockwise, same lump in both
    _mini_tub(ctx, 300, 410, th, 34, a, False, lt)
    _mini_tub(ctx, 780, 410, th, 7, a, True, lt)
    text_c(ctx, "LIGHT TUB", 300, 540, 26, INK, True, 1.5, a)
    text_c(ctx, "TUB + CONCRETE", 780, 540, 26, INK, True, 1.5, a)

def card_tubs(ctx, t, lt, a):
    card_frame(ctx, "WHERE THE WEIGHT CAME FROM", a, "PLASTIC TUB + CONCRETE = SAME HEAVY TUB", MUSTARD)
    g = ease((lt - 1.4) / 1.0)
    # old: enamelled steel tub, thick wall
    ctx.arc(300, 400, 100, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=4, alpha=a)
    ctx.arc(300, 400, 78, 0, 2 * math.pi); fill_stroke(ctx, DRUMC, lw=3, alpha=a)
    text_c(ctx, "OLD STEEL TUB", 300, 540, 26, INK, True, 1.5, a)
    # new: thin plastic tub, concrete drops on
    ctx.arc(780, 410, 92, 0, 2 * math.pi); fill_stroke(ctx, hexc('#f1ece0'), lw=4, alpha=a)
    ctx.arc(780, 410, 84, 0, 2 * math.pi); fill_stroke(ctx, DRUMC, lw=2, alpha=a)
    yb = lerp(250, 300, g)
    rrect(ctx, 720, yb - 18, 120, 26, 6); concrete(ctx, a * max(0.25, g))
    ctx.new_path(); ctx.arc(780, 410, 104, math.radians(35), math.radians(145))
    ctx.arc_negative(780, 410, 94, math.radians(145), math.radians(35)); ctx.close_path(); concrete(ctx, a * g)
    text_c(ctx, "PLASTIC TUB", 780, 540, 26, INK, True, 1.5, a)
    straight_arrow(ctx, 450, 400, 610, 400, INK2, a, lw=5, head=12)
    text_c(ctx, "today", 530, 380, 24, INK2, False, 1, a)

CARDS = {'mass': card_mass, 'tubs': card_tubs}
