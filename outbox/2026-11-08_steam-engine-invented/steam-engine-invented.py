"""Cogwise episode: Your stuck pot lid started the steam engine (series "How you accidentally invented...").
SIDE VIEW, cut-away. Screen coordinates: x grows RIGHT, y grows DOWN.
Physics:
  POT: steam under the lid condenses (steam ~1,600x the volume of its water) -> partial vacuum under the lid
       -> outside air presses the lid DOWN onto the rim: it sticks.
  TUBE (Papin, 1690): water boiled at the bottom of an open-top tube; steam lifts the piston UP; a latch holds it.
       Fire removed -> steam condenses -> vacuum under the piston. Latch released -> air pushes the piston DOWN.
       Rope from the piston rod goes UP, over two pulleys, DOWN to a bucket: piston DOWN <=> bucket UP.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="steam-engine-invented",
    title="Your stuck pot lid started the steam engine 🍲",
    description=("That pot lid that sticks as it cools is the trick behind the first piston steam engine: steam makes a vacuum, the air does the work.\n\n"
                 "#Shorts #howthingswork #steamengine #physics #history #cogwise"),
    hashtags=["Shorts", "howthingswork", "steamengine", "physics", "history", "cogwise"],
    sources=[
        "https://web.physics.ucsb.edu/~lecturedemonstrations/Composer/Pages/48.27.html",
        "https://gracesguide.co.uk/Denis_Papin",
        "https://en.wikipedia.org/wiki/History_of_the_steam_engine",
        "https://en.wikipedia.org/wiki/Newcomen_atmospheric_engine",
        "https://www.britannica.com/biography/Denis-Papin",
    ],
)

BEATS = [
    dict(dur=5.4, title="THE STUCK LID", caption="That pot lid that sticks when it cools? That's how the steam engine started."),
    dict(dur=4.2, title="THE SECRET", caption="Inside, the steam turns back into a few drops of water."),
    dict(dur=5.2, title="A VACUUM", caption="Steam takes up over a thousand times more room, so almost nothing is left."),
    dict(dur=3.8, title="AIR PUSHES", caption="Now the air outside presses the lid down. It's stuck."),
    dict(dur=7.6, title=None, caption="Air presses about one kilo on every square centimetre: up to three hundred kilos on this lid. Seven hundred pounds.", card='force'),
    dict(dur=5.4, title="1 · PISTON", caption="Now swap the lid for a piston in a tall tube, roped to a bucket."),
    dict(dur=5.6, title="2 · HEAT", caption="Boil a little water underneath. Steam lifts the piston, and a latch holds it."),
    dict(dur=5.4, title="3 · COOL", caption="Take away the fire. The steam turns back to water and leaves a vacuum."),
    dict(dur=5.4, title="4 · AIR STROKE", caption="Release the latch. The air slams the piston down, and the bucket shoots up."),
    dict(dur=4.4, title="WHO PUSHED?", caption="No steam pushed that bucket. The weight of the air did."),
    dict(dur=5.8, title="PAPIN · 1690", caption="Denis Papin built exactly this in 1690. Newcomen scaled it up to pump flooded mines."),
    dict(dur=5.4, title="RECAP", caption="Steam makes the vacuum. Air does the work. It all started with a lid."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.3):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

ANCHOR = (540, 1500)

# ---------------------------------------------------------------- palette extras
STEEL = hexc('#b9c0c6'); STEEL_D = hexc('#7b838a'); STEEL_L = hexc('#dde2e6')
IRON_D = hexc('#4f565c')
WOOD = hexc('#b07a42'); WOOD_D = hexc('#7d5228')
STEAM = hexc('#e9eef0'); WATER = hexc('#4a90c8'); WATER_D = hexc('#2f6c9e')
ROPE = hexc('#c9a46a')
AIR = RED

# ---------------------------------------------------------------- geometry (screen: y DOWN)
IX0, IX1 = 395, 685            # inner walls (290 px ~ 20 cm)
WALL = 16
BOT = 1254                     # inner bottom
POT_TOP, TUBE_TOP = 1050, 600  # wall top: pot / tall tube
LID_Y = 1036                   # lid underside sits on the rim
P_H = 30                       # piston thickness
PY_UP, PY_DN = 640, 1190       # piston top y: latched up / resting down on the water
ROD_L = 130
CXR = 540                      # rod / rope axis
P1, P2, PR = (570, 400), (880, 400), 30
BX = P2[0] + PR                # 910: bucket rope axis
WELL = (835, 985, 1180)        # well x0, x1, rim y
LATCH_PIV = (697, 585); LATCH_L = 142

def bucket_y(py):              # rope length conserved: piston DOWN -> bucket UP
    return 1390 + PY_UP - py

def track(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, ease((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]

M0 = B(5)                      # morph pot -> tube
C11 = B(10)                    # second stroke during beat 11

def state(t):
    s = {}
    s['m'] = clamp((t - M0 - 0.1) / 1.4)
    m = s['m']
    # --- fire
    s['fire'] = (win(t, B(1) + 0.1, B(1) + 1.9, 0.2) + win(t, B(6) + 0.2, B(7) + 0.2, 0.3)
                 + win(t, C11 + 0.1, C11 + 2.3, 0.3))
    # --- steam under the lid / piston (0..1) and condensed drops (0..1)
    s['steam'] = track(t, [(0, 0.9), (0.1, 0.9), (0.7, 0), (B(1) + 0.2, 0), (B(1) + 1.5, 1), (B(1) + 2.0, 1), (B(2) - 0.4, 0),
                           (B(6) + 0.6, 0), (B(6) + 1.6, 1), (B(7) + 0.6, 1), (B(8) - 1.2, 0),
                           (C11 + 0.3, 0), (C11 + 1.2, 1), (C11 + 2.4, 1), (C11 + 3.6, 0)])
    s['drops'] = track(t, [(0, 0.2), (0.2, 0.2), (1.1, 1), (B(1) + 0.2, 1), (B(1) + 1.2, 0), (B(1) + 2.0, 0), (B(2) - 0.4, 1),
                           (M0, 1), (M0 + 1.2, 0),
                           (B(7) + 0.6, 0), (B(8) - 1.2, 1), (C11 + 0.3, 1), (C11 + 1.0, 0), (C11 + 2.4, 0), (C11 + 3.6, 1)])
    s['cold'] = win(t, 0.5, B(1) + 0.2, 0.3) + win(t, B(2) - 0.6, M0, 0.3) + win(t, B(7) + 0.8, B(8) + 1.4, 0.3) \
        + win(t, C11 + 2.6, C11 + 4.3, 0.3)
    # --- air arrows
    s['arrows'] = (win(t, 0.35, B(1) - 0.2, 0.25) + win(t, B(3) + 0.05, B(4) - 0.1, 0.3)
                   + win(t, B(8) + 0.6, B(10) - 0.2, 0.3) + win(t, C11 + 3.6, B(12) + 2, 0.3))
    s['dip'] = 5 * (win(t, 0.4, B(1), 0.3) + win(t, B(3), B(4), 0.3))
    s['tug'] = max(0.0, math.sin((t - B(3) - 0.8) * 9)) * win(t, B(3) + 0.8, B(4) - 0.3, 0.1)   # lid twitches, can't lift
    # --- piston (tube phase)
    s['py'] = track(t, [(M0, PY_DN), (B(6) + 1.2, PY_DN), (B(7) - 1.0, PY_UP), (B(8) + 0.8, PY_UP), (B(8) + 1.3, PY_DN),
                        (C11 + 0.6, PY_DN), (C11 + 2.2, PY_UP), (C11 + 3.6, PY_UP), (C11 + 4.0, PY_DN)])
    s['latch'] = track(t, [(0, 1), (B(7) - 1.2, 1), (B(7) - 0.8, 0), (B(8) + 0.45, 0), (B(8) + 0.75, 1),
                           (C11 + 2.0, 1), (C11 + 2.4, 0), (C11 + 3.3, 0), (C11 + 3.6, 1)])   # 0 = engaged, 1 = lifted
    s['vac'] = win(t, B(2) + 0.1, B(4), 0.3) + win(t, B(8) - 1.0, B(8) + 0.8, 0.3)
    py = s['py']
    ds = py - track(t - 0.15, [(M0, PY_DN), (B(6) + 1.2, PY_DN), (B(7) - 1.0, PY_UP), (B(8) + 0.8, PY_UP), (B(8) + 1.3, PY_DN),
                               (C11 + 0.6, PY_DN), (C11 + 2.2, PY_UP), (C11 + 3.6, PY_UP), (C11 + 4.0, PY_DN)])
    s['rising'] = clamp(ds / 30)          # bucket rising (piston going down)
    # --- highlights / tags
    s['h_drops'] = bw(t, 1)
    s['h_lid'] = bw(t, 3)
    s['h_fire'] = bw(t, 6)
    s['h_cold'] = bw(t, 7)
    s['h_latch'] = bw(t, 8)
    s['h_bucket'] = bw(t, 9)
    s['l_drops'] = bw(t, 1)
    s['l_ratio'] = bw(t, 2)
    s['l_stuck'] = bw(t, 3)
    s['l_piston'] = bw(t, 5)
    s['l_rope'] = bw(t, 5)
    s['l_steam'] = bw(t, 6)
    s['l_latch'] = bw(t, 6) + bw(t, 8)
    s['l_vac'] = bw(t, 7)
    s['l_air'] = bw(t, 8) + bw(t, 9)
    s['l_papin'] = bw(t, 10)
    s['l_newc'] = win(t, B(10) + 2.4, B(11), 0.3)
    s['l_recap'] = win(t, B(11) + 0.1, B(12) + 2, 0.3)
    return s

# ---------------------------------------------------------------- drawing
def draw_stove(ctx, t, st):
    # cabinet + hob
    ctx.rectangle(250, 1345, 580, 155); fill_stroke(ctx, WOOD, lw=5)
    for x in (443, 637):
        ctx.move_to(x, 1345); ctx.line_to(x, 1500); setc(ctx, WOOD_D, 0.7); ctx.set_line_width(3); ctx.stroke()
    rrect(ctx, 240, 1318, 600, 30, 6); fill_stroke(ctx, IRON_D, lw=5)
    # burner head
    rrect(ctx, 440, 1298, 200, 22, 6); fill_stroke(ctx, STEEL_D, lw=4)
    # pan supports
    for x in (420, 650):
        ctx.rectangle(x, 1272, 12, 48); fill_stroke(ctx, IRON_D, lw=3)
    f = clamp(st['fire'])
    if f > 0.02:
        rnd = random.Random(int(t * 14))
        for k in range(8):
            fx = 455 + k * 24; fh = (16 + rnd.random() * 12) * f
            ctx.move_to(fx - 8, 1300); ctx.curve_to(fx - 6, 1300 - fh * 0.6, fx, 1300 - fh, fx + 1, 1300 - fh)
            ctx.curve_to(fx + 4, 1300 - fh * 0.6, fx + 8, 1294, fx + 8, 1300); ctx.close_path()
            setc(ctx, hexc('#3d7fd6') if k % 2 else ORANGE, 0.95 * f); ctx.fill()

def wall_top(st):
    return lerp(POT_TOP, TUBE_TOP, ease(st['m']))

def draw_vessel_inside(ctx, t, st):
    m = st['m']; wt = wall_top(st)
    top = lerp(LID_Y + 4, st['py'] + P_H, ease(m)) if m > 0 else LID_Y + 4
    if m > 0.5: top = st['py'] + P_H
    # interior
    ctx.rectangle(IX0, wt, IX1 - IX0, BOT - wt); setc(ctx, WALL1); ctx.fill()
    if st['cold'] > 0:
        ctx.rectangle(IX0, top, IX1 - IX0, BOT - top); setc(ctx, COLD, 0.2 * clamp(st['cold'])); ctx.fill()
    # water layer at the bottom of the tube
    wl = 30 * ease(m)
    if wl > 0.5:
        ctx.rectangle(IX0, BOT - wl, IX1 - IX0, wl); setc(ctx, WATER, 0.9); ctx.fill()
        if st['fire'] > 0.1:
            for k in range(7):
                bx = IX0 + 25 + k * 40; by = BOT - ((t * 50 + k * 13) % max(4, wl))
                ctx.arc(bx, by, 5, 0, 2 * math.pi); setc(ctx, WHITE, 0.8 * clamp(st['fire'])); ctx.fill()
    # pot: a little soup / water at the bottom (pot phase)
    if m < 1:
        ctx.rectangle(IX0, BOT - 34, IX1 - IX0, 34); setc(ctx, WATER, 0.9 * (1 - m)); ctx.fill()
    floor = BOT - max(wl, 34 * (1 - m))
    # steam
    sv = st['steam']
    if sv > 0.01 and floor > top:
        ctx.save(); ctx.rectangle(IX0, top, IX1 - IX0, floor - top); ctx.clip()
        setc(ctx, STEAM, 0.55 * sv); ctx.paint()
        rnd = random.Random(7)
        for k in range(16):
            bx = rnd.uniform(IX0 + 12, IX1 - 12); by = rnd.uniform(top + 10, floor - 6)
            r = (15 + rnd.random() * 14) * (0.3 + 0.7 * sv)
            ctx.arc(bx + 6 * math.sin(t * 2 + k), by, r, 0, 2 * math.pi); setc(ctx, WHITE, 0.75 * sv); ctx.fill()
        ctx.restore()
    # condensed drops on the walls + underside
    d = st['drops']
    if d > 0.02:
        rnd = random.Random(3)
        for k in range(10):
            side = k % 2
            x = IX0 + 9 if side == 0 else IX1 - 9
            y = lerp(top + 20, floor - 20, rnd.random())
            ctx.arc(x, y, 6 * d, 0, 2 * math.pi); setc(ctx, WATER, 0.95); ctx.fill()
        for k in range(6):
            ctx.arc(IX0 + 30 + k * 46, top + 8, 5 * d, 0, 2 * math.pi); setc(ctx, WATER, 0.95); ctx.fill()
    if st['vac'] > 0.01 and floor - top > 80:
        text_c(ctx, "VACUUM", (IX0 + IX1) / 2, (top + floor) / 2 + 10, 30, INK, True, 2, clamp(st['vac']))

def draw_vessel_walls(ctx, t, st):
    m = st['m']; wt = wall_top(st)
    for x in (IX0 - WALL, IX1):
        ctx.rectangle(x, wt, WALL, BOT - wt + 16); fill_stroke(ctx, STEEL, lw=4)
    ctx.rectangle(IX0 - WALL, BOT, IX1 - IX0 + 2 * WALL, 16); fill_stroke(ctx, STEEL_D, lw=4)
    # saucepan handle (fades out as it becomes a tube)
    a = 1 - ease(m)
    if a > 0.01:
        rrect(ctx, IX1 + WALL - 4, 1078, 220, 26, 12); fill_stroke(ctx, IRON_D, lw=4, alpha=a)
        ctx.arc(IX1 + WALL + 196, 1091, 6, 0, 2 * math.pi); setc(ctx, WALL1, a); ctx.fill()

def draw_lid(ctx, t, st):
    a = 1 - ease(clamp(st['m'] * 1.6))
    if a <= 0.01: return
    y = LID_Y + st['dip'] - 6 * st['tug']
    cx = (IX0 + IX1) / 2
    ctx.move_to(IX0 - 30, y + 14); ctx.line_to(IX0 - 30, y + 4)
    ctx.curve_to(IX0 + 20, y - 52, IX1 - 20, y - 52, IX1 + 30, y + 4); ctx.line_to(IX1 + 30, y + 14); ctx.close_path()
    fill_stroke(ctx, STEEL_L, lw=5, alpha=a)
    rrect(ctx, cx - 30, y - 62, 60, 26, 10); fill_stroke(ctx, IRON_D, lw=4, alpha=a)

def draw_piston(ctx, t, st):
    a = ease(clamp(st['m'] * 1.6 - 0.6))
    if a <= 0.01: return
    py = st['py']
    ctx.rectangle(IX0 + 2, py, IX1 - IX0 - 4, P_H); fill_stroke(ctx, IRON_D, lw=4, alpha=a)
    ctx.rectangle(CXR - 8, py - ROD_L, 16, ROD_L); fill_stroke(ctx, STEEL_L, lw=3, alpha=a)
    # collar the latch catches
    rrect(ctx, CXR - 18, py - 78, 36, 14, 4); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)

def draw_latch(ctx, t, st):
    a = ease(clamp(st['m'] * 1.6 - 0.6))
    if a <= 0.01: return
    px, py0 = LATCH_PIV
    ctx.rectangle(IX1 + 2, py0 - 8, 12, TUBE_TOP - py0 + 8); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    phi = 1.05 * st['latch']
    tx = px - LATCH_L * math.cos(phi); ty = py0 - LATCH_L * math.sin(phi)
    ctx.move_to(px, py0); ctx.line_to(tx, ty)
    setc(ctx, INK, a); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.move_to(px, py0); ctx.line_to(tx, ty)
    setc(ctx, RED, a); ctx.set_line_width(8); ctx.stroke(); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.arc(px, py0, 9, 0, 2 * math.pi); fill_stroke(ctx, STEEL_L, lw=3, alpha=a)

def draw_rig(ctx, t, st):
    a = ease(clamp((st['m'] - 0.3) / 0.7))
    if a <= 0.01: return
    # overhead timber + hangers
    ctx.rectangle(500, 322, 470, 26); fill_stroke(ctx, WOOD, lw=5, alpha=a)
    for p in (P1, P2):
        ctx.move_to(p[0], 348); ctx.line_to(p[0], p[1]); setc(ctx, INK, a); ctx.set_line_width(5); ctx.stroke()
    # well
    x0, x1, ry = WELL
    ctx.rectangle(x0, ry, 18, 1500 - ry); fill_stroke(ctx, hexc('#c9876a'), lw=4, alpha=a)
    ctx.rectangle(x1 - 18, ry, 18, 1500 - ry); fill_stroke(ctx, hexc('#c9876a'), lw=4, alpha=a)
    ctx.rectangle(x0 + 18, ry, x1 - x0 - 36, 1500 - ry); setc(ctx, hexc('#3e3a42'), a); ctx.fill()
    ctx.rectangle(x0 + 18, 1400, x1 - x0 - 36, 100); setc(ctx, WATER, 0.9 * a); ctx.fill()
    text_c(ctx, "WELL", (x0 + x1) / 2, ry - 16, 20, WATER_D, True, 2, a)
    # rope: rod top -> up -> over P1 -> over P2 -> down to the bucket
    py = st['py']; rt = py - ROD_L; by = bucket_y(py)
    ctx.move_to(CXR, rt); ctx.line_to(P1[0] - PR, P1[1])
    ctx.arc(P1[0], P1[1], PR, math.pi, 1.5 * math.pi)
    ctx.line_to(P2[0], P2[1] - PR)
    ctx.arc(P2[0], P2[1], PR, 1.5 * math.pi, 2 * math.pi)
    ctx.line_to(BX, by)
    setc(ctx, INK, a); ctx.set_line_width(9); ctx.stroke_preserve()
    setc(ctx, ROPE, a); ctx.set_line_width(5); ctx.stroke()
    # pulleys (spin with the rope)
    ang = -(py - PY_DN) / PR
    for p in (P1, P2):
        ctx.arc(p[0], p[1], PR, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=4, alpha=a)
        for k in range(3):
            q = ang + k * 2 * math.pi / 3
            ctx.move_to(p[0], p[1]); ctx.line_to(p[0] + (PR - 6) * math.cos(q), p[1] + (PR - 6) * math.sin(q))
            setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
        ctx.arc(p[0], p[1], 6, 0, 2 * math.pi); fill_stroke(ctx, IRON_D, lw=2, alpha=a)
    # bucket (full of water)
    bw_, bh = 96, 92
    ctx.move_to(BX - 30, by + 6); ctx.curve_to(BX - 30, by - 20, BX + 30, by - 20, BX + 30, by + 6)
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    ctx.move_to(BX - bw_ / 2, by + 6); ctx.line_to(BX - bw_ / 2 + 10, by + 6 + bh); ctx.line_to(BX + bw_ / 2 - 10, by + 6 + bh)
    ctx.line_to(BX + bw_ / 2, by + 6); ctx.close_path(); fill_stroke(ctx, WOOD, lw=5, alpha=a)
    ctx.rectangle(BX - bw_ / 2 + 5, by + 12, bw_ - 10, 14); setc(ctx, WATER, 0.9 * a); ctx.fill()
    for yy in (by + 40, by + 70):
        ctx.move_to(BX - bw_ / 2 + 6, yy); ctx.line_to(BX + bw_ / 2 - 6, yy); setc(ctx, WOOD_D, a); ctx.set_line_width(4); ctx.stroke()
    # drips while it rises
    r = st['rising']
    if r > 0.05:
        for k in range(3):
            u = (t * 3 + k / 3) % 1.0
            ctx.arc(BX - 20 + k * 20, by + bh + 14 + 60 * u, 5, 0, 2 * math.pi); setc(ctx, WATER, r * (1 - u)); ctx.fill()

def draw_air(ctx, t, st):
    a = clamp(st['arrows'])
    if a <= 0: return
    m = st['m']
    if m < 0.5:
        y1 = LID_Y + st['dip'] - 56; ys = (430, 485, 540, 595, 650)
        for i, x in enumerate(ys):
            L = 1.0 if i % 2 == 0 else 0.8
            straight_arrow(ctx, x, y1 - 150 * L - 10 * math.sin(t * 6 + i), x, y1 + (8 if i == 2 else 18), AIR, a,
                           lw=9 if L == 1.0 else 6, head=18 if L == 1.0 else 13)
        text_c(ctx, "AIR", 780, 985, 34, AIR, True, 3, a)
    else:
        py = st['py']
        for i, x in enumerate((430, 485, 595, 650)):
            L = 1.0 if i in (0, 3) else 0.8
            y1 = py - 6; y0 = min(y1 - 70, TUBE_TOP - 150 * L) - 8 * math.sin(t * 6 + i)
            straight_arrow(ctx, x, y0, x, y1, AIR, a, lw=9 if L == 1.0 else 6, head=18 if L == 1.0 else 13)

def draw_all(ctx, t, st):
    draw_rig(ctx, t, st)
    draw_stove(ctx, t, st)
    draw_vessel_inside(ctx, t, st)
    draw_vessel_walls(ctx, t, st)
    draw_lid(ctx, t, st)
    draw_piston(ctx, t, st)
    draw_latch(ctx, t, st)
    draw_air(ctx, t, st)
    # highlights
    highlight(ctx, IX0 + 10, 1150, 60, 110, COLD, st['h_drops'], t)
    highlight(ctx, 540, LID_Y - 20, 210, 60, RED, st['h_lid'], t)
    highlight(ctx, 540, 1295, 130, 40, ORANGE, st['h_fire'], t)
    highlight(ctx, 540, (st['py'] + BOT) / 2, 170, max(40, (BOT - st['py']) / 2), COLD, st['h_cold'], t)
    highlight(ctx, 630, 585, 90, 40, RED, st['h_latch'], t)
    highlight(ctx, BX, bucket_y(st['py']) + 50, 80, 80, MUSTARD, st['h_bucket'], t)
    # tags
    tag(ctx, "WATER DROPS", 300, 960, COLD, st['l_drops'])
    tag(ctx, "STEAM ≈ 1,600 × WATER", 540, 890, INK, st['l_ratio'])
    tag(ctx, "STUCK", 820, 1010, RED, st['l_stuck'])
    tag(ctx, "PISTON", 250, st['py'] + 15, INK, st['l_piston'])
    tag(ctx, "ROPE + BUCKET", 760, 470, WOOD_D, st['l_rope'])
    tag(ctx, "STEAM LIFTS", 240, 900, RED, st['l_steam'])
    tag(ctx, "LATCH", 790, 560, RED, st['l_latch'])
    tag(ctx, "NO FIRE", 250, 1180, COLD, st['l_vac'])
    tag(ctx, "AIR PUSHES", 300, 520, AIR, st['l_air'] * (1 - st['l_recap']))
    tag(ctx, "PAPIN · 1690", 300, 520, INK, st['l_papin'])
    tag(ctx, "NEWCOMEN 1712 · MINES", 300, 1150, INK, st['l_newc'])
    tag(ctx, "STEAM = VACUUM", 250, 1180, INK, st['l_recap'])
    tag(ctx, "AIR = WORK", 300, 520, AIR, st['l_recap'])

POT = (560, 1110, 1.3)
OVER = (580, 910, 0.98)
CAMKEYS = [(0, *POT),
           (B(2), 555, 1130, 1.38),
           (B(4), *POT),
           (M0 + 0.2, *OVER),
           (B(6), 560, 980, 1.08),
           (B(8), *OVER),
           (B(9), *OVER)]
def CAM(t): return cam_track(CAMKEYS, t)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_all(ctx, t, state(t))

def draw_hud(ctx, t, E):
    pop_word(ctx, "STUCK!", t - 0.8, 1.7, RED, cx=540, cy=640, size=130)
    pop_word(ctx, "AIR!", t - (B(8) + 1.0), 1.5, RED, cx=210, cy=900, size=120)

SFX = [(0.8, 'pop'), (B(1) + 0.3, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'),
       (B(5) + 0.4, 'pop'), (B(6) + 0.3, 'click'), (B(7) - 0.8, 'click'), (B(7) + 0.3, 'click'),
       (B(8) + 0.5, 'click'), (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- card
def card_force(ctx, t, lt, a):
    card_frame(ctx, "AIR IS HEAVY", a, None)
    k1 = ease((lt - 0.1) / 0.6)
    sx, sy = 270, 470
    ctx.rectangle(sx - 45, sy, 90, 18); fill_stroke(ctx, STEEL_L, lw=4, alpha=a * k1)
    text_c(ctx, "1 cm²", sx, sy + 52, 26, INK, True, 1, a * k1)
    wy = lerp(250, sy - 70, ease((lt - 0.2) / 0.5))
    rrect(ctx, sx - 40, wy, 80, 70, 8); fill_stroke(ctx, INK2, lw=4, alpha=a * k1)
    text_c(ctx, "1 kg", sx, wy + 45, 26, WHITE, True, 1, a * k1)
    straight_arrow(ctx, sx + 70, 300, sx + 70, sy - 6, AIR, a * k1, lw=6, head=12)
    # right: the lid, 20 cm (8 in) across, seen at an angle
    k2 = ease((lt - 2.0) / 0.6)
    px, pyc = 720, 430
    ctx.save(); ctx.translate(px, pyc); ctx.scale(1, 0.32); ctx.arc(0, 0, 160, 0, 2 * math.pi); ctx.restore()
    fill_stroke(ctx, STEEL_L, lw=4, alpha=a * k2)
    rrect(ctx, px - 22, pyc - 26, 44, 22, 8); fill_stroke(ctx, IRON_D, lw=3, alpha=a * k2)
    for i in range(7):
        ax = px - 140 + i * 46.7
        straight_arrow(ctx, ax, 262, ax, pyc - 34 + abs(i - 3) * 5, AIR, a * k2, lw=5, head=11)
    ctx.move_to(px - 160, pyc + 74); ctx.line_to(px + 160, pyc + 74); setc(ctx, INK, a * k2); ctx.set_line_width(3); ctx.stroke()
    text_c(ctx, "Ø 20 cm · 8 in", px, pyc + 108, 24, INK, True, 1, a * k2)
    k3 = ease((lt - 3.6) / 0.5)
    text_c(ctx, "up to ≈ 300 kg · 700 lb", 540, 585, 38, AIR, True, 1.5, a * k3)
    text_c(ctx, "≈ 1 kg / cm² · 14.7 lb / in²", 540, 585, 30, TEAL, True, 1.5, a * k1 * (1 - k3))

CARDS = {'force': card_force}
