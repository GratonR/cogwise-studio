"""Cogwise episode: The coldest part of a snow cannon is a puff of air.
One idea: tiny water drops can stay liquid (supercooled) below 0 °C; to freeze they need an ice nucleus.
The fan gun makes its own nuclei in the NUCLEATOR: a little water + compressed air; leaving the nozzle the air
expands suddenly and cools sharply, the water in the blast freezes into specks of ice (the seeds). The main nozzles
spray bigger drops, the fan throws everything high so the drops have hang time; a seed touches a drop on the way
down and the whole drop freezes around it -> machine snow = small frozen beads, not flakes.

VIEW: side view, fan gun on a short tower at LEFT, barrel aimed UP-RIGHT, plume arcs to the RIGHT onto the slope.
Screen y grows DOWN. Barrel frame: local +x = forward (toward the muzzle), local -y = the top of the barrel.
L2S maps local -> screen with cairo rotate(-ANG): forward = (cos, -sin) = right AND up on screen (nose up).
Air flows from the rear (fan, left) to the muzzle (right). Fan blades turn; in side view they foreshorten.
"""
import math, cairo
from cogwise.style import *

META = dict(
    slug="snow-cannon",
    title="The coldest part of a snow cannon is a puff of air ❄️ #Shorts",
    description=("Water drops can stay liquid below 0 °C. A snow cannon makes its own ice seeds with a puff of expanding air.\n\n"
                 "#Shorts #howthingswork #snow #skiing #science #cogwise"),
    hashtags=["Shorts", "howthingswork", "snow", "skiing", "science", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Snow_gun",
        "https://www.technoalpin.com/en-us/about-us/snowmaking-faqs/",
    ],
)

BEATS = [
    dict(dur=5.6, title="A PUFF OF AIR", caption="The coldest part of a snow cannon isn't the water. It's a puff of air."),
    dict(dur=5.4, title="STILL LIQUID", caption="Tiny water drops can stay liquid well below zero Celsius, thirty-two Fahrenheit."),
    dict(dur=5.4, title=None, caption="To freeze, they need a starting point: a seed of ice to grow on.", card='seed'),
    dict(dur=5.4, title="THE SEED MAKER", caption="So the cannon makes its own seeds, in a small nozzle called the nucleator."),
    dict(dur=4.4, title="WATER + AIR", caption="Inside, a little water is mixed with compressed air."),
    dict(dur=5.8, title=None, caption="As it leaves the nozzle, the air expands suddenly, and expanding air gets very cold.", card='expand'),
    dict(dur=5.6, title="ICE SEEDS", caption="The water caught in that blast freezes into specks of ice. Those are the seeds."),
    dict(dur=4.4, title="BIG DROPS", caption="Around it, the main nozzles spray much bigger drops."),
    dict(dur=5.8, title="THROWN HIGH", caption="The fan throws everything high into the cold air, so the drops have time to fall."),
    dict(dur=5.8, title="FROZEN IN FLIGHT", caption="On the way down, a seed touches a drop, and the whole drop freezes around it."),
    dict(dur=4.6, title="BEADS, NOT FLAKES", caption="That's why machine snow is tiny frozen beads, not flakes."),
    dict(dur=4.0, title="NO AIR, NO SNOW", caption="No puff of air, no seeds, no snow."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
ANG = 0.62                       # barrel elevation (rad), nose UP
CA, SA = math.cos(ANG), math.sin(ANG)
BC = (310.0, 990.0)              # barrel centre (screen)
HL, R = 170, 100                 # barrel half length, radius

def L2S(lx, ly):
    """barrel local -> screen.  local +x forward, local -y = top of the barrel."""
    return (BC[0] + lx * CA + ly * SA, BC[1] - lx * SA + ly * CA)

def ground_y(x): return 1400 + 0.05 * x

FAN_X = -95                      # fan plane (local x)
NUC = (186, -118)                # nucleator nozzle (local), on top of the front ring
P0 = L2S(230, 0)
P1 = (P0[0] + 520 * CA, P0[1] - 520 * SA)
P2 = (950.0, ground_y(950))
NS0 = L2S(250, -118)             # where the seeds leave the nucleator jet
NS1 = (P1[0] - 30, P1[1] - 40)

SNOW = WHITE; DROP = TEAL; ICE_E = hexc('#7d8fa0'); METAL = hexc('#d9d2c2'); METAL_D = hexc('#b9b09c')
WATER_L = TEAL; AIR_L = hexc('#8a8590')

def bez(p0, p1, p2, u):
    v = 1 - u
    return (v * v * p0[0] + 2 * u * v * p1[0] + u * u * p2[0], v * v * p0[1] + 2 * u * v * p1[1] + u * u * p2[1])

def bez_n(p0, p1, p2, u):
    """unit normal (pointing to the left of travel = 'above' the path while it climbs)."""
    dx = 2 * (1 - u) * (p1[0] - p0[0]) + 2 * u * (p2[0] - p1[0])
    dy = 2 * (1 - u) * (p1[1] - p0[1]) + 2 * u * (p2[1] - p1[1])
    L = math.hypot(dx, dy) or 1
    return (dy / L, -dx / L)

def rnd(i, k=0):
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return x - math.floor(x)

# ---------------------------------------------------------------- state
def freeze_on(t):        # drops freeze in flight (working cannon): beat 1 and from beat 10
    return max(1 - clamp((t - B(1) + 0.3) / 0.6), clamp((t - B(9) - 0.2) / 0.6))

def seeds_on(t):         # ice seeds visible
    return max(1 - clamp((t - B(1) + 0.3) / 0.6), clamp((t - B(6) - 0.3) / 0.6))

def jet_on(t):           # nucleator puff of air
    return max(1 - clamp((t - B(1) + 0.3) / 0.6), clamp((t - B(3) - 0.4) / 0.6))

def state(t):
    s = {}
    s['answer'] = win(t, 0.35, B(1), 0.3)
    s['liquid'] = bw(t, 1)
    s['nuc'] = bw(t, 3, 5)
    s['feeds'] = bw(t, 4)
    s['seeds'] = bw(t, 6)
    s['nozzles'] = bw(t, 7)
    s['fan'] = bw(t, 8)
    s['freeze'] = bw(t, 9)
    s['loupe'] = bw(t, 10)
    s['recap'] = bw(t, 11, 12)
    return s

def pile_h(t):
    grow = min(t, B(1)) + max(0.0, t - B(9) - 0.4)
    return 34 + 9 * grow

# ---------------------------------------------------------------- drawing helpers
def star(ctx, x, y, r, a, fill=SNOW, edge=INK):
    if a <= 0: return
    ctx.move_to(x, y - r)
    for k in range(1, 8):
        ang = -math.pi / 2 + k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.38
        ctx.line_to(x + rr * math.cos(ang), y + rr * math.sin(ang))
    ctx.close_path(); setc(ctx, fill, a); ctx.fill_preserve(); setc(ctx, edge, a); ctx.set_line_width(1.6); ctx.stroke()

def drop(ctx, x, y, r, a, frozen=0.0):
    if a <= 0: return
    col = lerpc(DROP, SNOW, frozen)
    ctx.arc(x, y, r, 0, 2 * math.pi); setc(ctx, col, a); ctx.fill_preserve()
    setc(ctx, lerpc(INK, ICE_E, frozen), a); ctx.set_line_width(1.8); ctx.stroke()

def flake(ctx, x, y, r, a, col=INK):
    for k in range(6):
        ang = k * math.pi / 3
        ex, ey = x + r * math.cos(ang), y + r * math.sin(ang)
        ctx.move_to(x, y); ctx.line_to(ex, ey)
        for sgn in (-1, 1):
            mx, my = x + 0.6 * r * math.cos(ang), y + 0.6 * r * math.sin(ang)
            ctx.move_to(mx, my); ctx.line_to(mx + 0.3 * r * math.cos(ang + sgn * 0.8), my + 0.3 * r * math.sin(ang + sgn * 0.8))
    setc(ctx, col, a); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()

# ---------------------------------------------------------------- scene parts
def draw_ground(ctx, t):
    ctx.move_to(-200, ground_y(-200))
    ctx.line_to(1300, ground_y(1300)); ctx.line_to(1300, 1520); ctx.line_to(-200, 1520); ctx.close_path()
    setc(ctx, SNOW); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # snow pile under the landing zone (grows only while the drops freeze)
    h = pile_h(t); cx = P2[0]; w = 70 + 1.6 * h
    gy = ground_y(cx)
    ctx.move_to(cx - w, gy + 4)
    ctx.curve_to(cx - w * 0.5, gy - h * 0.2, cx - w * 0.4, gy - h, cx, gy - h)
    ctx.curve_to(cx + w * 0.4, gy - h, cx + w * 0.5, gy - h * 0.2, cx + w, gy + 4)
    ctx.close_path(); setc(ctx, SNOW); ctx.fill_preserve(); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    for k in range(10):
        x = cx - w * 0.6 + w * 1.2 * rnd(k, 3); y = gy - h * 0.3 * rnd(k, 4) - 6
        ctx.arc(x, y, 3, 0, 2 * math.pi); setc(ctx, ICE_E, 0.6); ctx.fill()

def draw_tower(ctx, t):
    px, py = L2S(-30, 75)
    gy = ground_y(px)
    for dx in (-70, 70):                                     # two legs of the stand
        ctx.move_to(px, py + 120); ctx.line_to(px + dx, gy + 6)
    setc(ctx, INK); ctx.set_line_width(9); ctx.stroke()
    ctx.rectangle(px - 13, py, 26, gy - py); fill_stroke(ctx, METAL_D, lw=4)
    ctx.arc(px, py, 18, 0, 2 * math.pi); fill_stroke(ctx, METAL, lw=4)
    # supply hoses (water + air) running up the pole to the back of the barrel
    for k, (col, dx) in enumerate(((WATER_L, -22), (AIR_L, -34))):
        ex, ey = L2S(-HL + 6, -R - 8 - 10 * k)
        ctx.move_to(px + dx, gy)
        ctx.curve_to(px + dx - 10, py + 120, ex - 120, ey + 150, ex - 4, ey)
        setc(ctx, col); ctx.set_line_width(7); ctx.stroke()

def draw_barrel(ctx, t, s):
    ctx.save(); ctx.translate(*BC); ctx.rotate(-ANG)
    # interior (cut-away)
    ctx.rectangle(-HL, -R, 2 * HL, 2 * R); setc(ctx, PAPER, 0.9); ctx.fill()
    # air flow inside the barrel: rear -> muzzle
    for k in range(3):
        y = -50 + 50 * k
        wavy_arrow(ctx, -55, y, 140, y, t, TEAL_L, 0.55 + 0.45 * s['fan'], amp=6, wl=40, lw=4, head=11)
    # motor + fan
    rrect(ctx, -HL + 14, -26, 56, 52, 8); fill_stroke(ctx, INK2, lw=4)
    ctx.rectangle(-HL + 70, -6, FAN_X - (-HL + 70), 12); fill_stroke(ctx, METAL_D, lw=3)
    w = 14.0                                                  # rad/s: the fan turns all the time
    for k in range(3):
        ph = t * w + k * 2 * math.pi / 3
        L = 86 * math.cos(ph); tw = 10 * math.sin(ph)          # side view: the blade foreshortens
        ctx.move_to(FAN_X - 8, 0); ctx.line_to(FAN_X - 8 + tw, L); ctx.line_to(FAN_X + 8 + tw, L); ctx.line_to(FAN_X + 8, 0)
        ctx.close_path(); fill_stroke(ctx, MUSTARD if s['fan'] > 0 else METAL, lw=3)
    rrect(ctx, FAN_X - 12, -16, 24, 32, 6); fill_stroke(ctx, METAL, lw=3)
    # rear grille
    for k in range(7):
        y = -R + 14 + k * (2 * R - 28) / 6
        ctx.move_to(-HL, y); ctx.line_to(-HL + 10, y)
    setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(-HL, -R); ctx.line_to(-HL, R); ctx.set_line_width(4); ctx.stroke()
    # barrel walls (top and bottom, cut)
    for y0 in (-R - 14, R):
        ctx.rectangle(-HL, y0, 2 * HL, 14); fill_stroke(ctx, METAL, lw=4)
    # front ring with the main water nozzles
    rrect(ctx, HL - 4, -R - 14, 16, 2 * R + 28, 5); fill_stroke(ctx, METAL_D, lw=4)
    hl = s['nozzles']
    for k in range(5):
        y = -80 + 40 * k
        rrect(ctx, HL + 10, y - 7, 16, 14, 3); fill_stroke(ctx, lerpc(TEAL, TEAL, 1), lw=3)
        if hl > 0:
            ctx.arc(HL + 18, y, 13 + 3 * math.sin(t * 6), 0, 2 * math.pi); setc(ctx, TEAL, 0.25 * hl); ctx.fill()
    # feed lines on top of the barrel: water (teal) and compressed air (grey) to the nucleator
    fa = s['feeds']
    for k, (col, y) in enumerate(((WATER_L, -R - 22), (AIR_L, -R - 32))):
        ctx.move_to(-HL + 6, y); ctx.line_to(NUC[0] - 10, y if k == 0 else y); ctx.line_to(NUC[0] - 10, NUC[1])
        setc(ctx, col); ctx.set_line_width(7 + 3 * fa); ctx.stroke()
    # nucleator nozzle (small mustard nozzle on top of the ring)
    nx, ny = NUC
    ctx.move_to(nx - 18, ny - 13); ctx.line_to(nx + 14, ny - 7); ctx.line_to(nx + 14, ny + 7); ctx.line_to(nx - 18, ny + 13)
    ctx.close_path(); fill_stroke(ctx, MUSTARD, lw=4)
    if fa > 0:   # pulses travelling along the feeds toward the nozzle (rear -> front)
        for k, (col, y) in enumerate(((WATER_L, -R - 22), (AIR_L, -R - 32))):
            for j in range(4):
                u = ((t * 0.9 + j / 4 + k * 0.12) % 1.0)
                x = lerp(-HL + 10, NUC[0] - 14, u)
                ctx.arc(x, y, 6, 0, 2 * math.pi); setc(ctx, WHITE if k else hexc('#bfe6e1'), fa); ctx.fill()
    ctx.restore()

def draw_jet(ctx, t, s):
    """nucleator puff: compressed air expanding in a short cone, carrying the seeds forward."""
    a = jet_on(t)
    if a <= 0: return
    ctx.save(); ctx.translate(*BC); ctx.rotate(-ANG)
    nx, ny = NUC
    ctx.move_to(nx + 14, ny - 6); ctx.line_to(nx + 110, ny - 34); ctx.line_to(nx + 110, ny + 34); ctx.line_to(nx + 14, ny + 6)
    ctx.close_path(); setc(ctx, WHITE, 0.75 * a); ctx.fill_preserve(); setc(ctx, AIR_L, 0.6 * a); ctx.set_line_width(2); ctx.stroke()
    for j in range(14):
        u = (t * 1.6 + rnd(j, 1)) % 1.0
        x = nx + 16 + 96 * u; y = ny + (rnd(j, 2) - 0.5) * 2 * (6 + 28 * u)
        ctx.arc(x, y, 3, 0, 2 * math.pi); setc(ctx, AIR_L, a * (1 - u) * 0.9); ctx.fill()
    ctx.restore()

def draw_plume(ctx, t, s):
    fz = freeze_on(t); sd = seeds_on(t)
    # soft mist along the path
    for wdt, al in ((190, 0.06), (120, 0.07), (60, 0.08)):
        ctx.move_to(*P0); ctx.curve_to(P0[0] + (P1[0] - P0[0]) * 2 / 3, P0[1] + (P1[1] - P0[1]) * 2 / 3,
                                        P2[0] + (P1[0] - P2[0]) * 2 / 3, P2[1] + (P1[1] - P2[1]) * 2 / 3, *P2)
        setc(ctx, TEAL_L, al); ctx.set_line_width(wdt); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    TRAV = 2.8
    seeds = []
    for i in range(26):          # ice seeds from the nucleator (they ride the same air stream)
        u = (t / TRAV * 1.1 + rnd(i, 7)) % 1.0
        x, y = bez(NS0, NS1, P2, u); nx, ny = bez_n(NS0, NS1, P2, u)
        o = (rnd(i, 8) - 0.5) * 2 * (20 + 110 * u)
        x += nx * o; y += ny * o
        aa = sd * clamp(u / 0.06) * clamp((1 - u) / 0.08)
        seeds.append((x, y, u))
        star(ctx, x, y, 7, aa)
    for i in range(64):          # main water drops
        u = (t / TRAV + rnd(i, 1)) % 1.0
        x, y = bez(P0, P1, P2, u); nx, ny = bez_n(P0, P1, P2, u)
        o = (rnd(i, 2) - 0.5) * 2 * (75 + 70 * u)
        x += nx * o; y += ny * o
        uf = 0.38 + 0.3 * rnd(i, 5)                        # where this drop meets a seed
        fr = fz * clamp((u - uf) / 0.05)
        aa = clamp(u / 0.04) * clamp((1 - u) / 0.06)
        drop(ctx, x, y, 6.5 + 2.5 * rnd(i, 6), aa, fr)
        if fz > 0 and 0 < u - uf < 0.07:                    # the freezing flash
            k = (u - uf) / 0.07
            ctx.arc(x, y, 8 + 16 * k, 0, 2 * math.pi); setc(ctx, WHITE, fz * (1 - k) * aa); ctx.set_line_width(3); ctx.stroke()

def draw_props(ctx, t, s):
    a = s['liquid']
    if a > 0:
        tx, ty = 560, 1385
        thermometer(ctx, tx, ty, 0.18, a)
        tag(ctx, "−5 °C · 23 °F", tx, ty - 215, TEAL, a, 24)
        # one big drop falling slowly, staying liquid
        lt = t - B(1)
        dx, dy = 800, 1000 + 18 * lt
        ctx.move_to(dx, dy - 52); ctx.curve_to(dx + 18, dy - 22, dx + 34, dy - 6, dx + 34, dy + 14)
        ctx.arc(dx, dy + 14, 34, 0, math.pi); ctx.curve_to(dx - 34, dy - 6, dx - 18, dy - 22, dx, dy - 52)
        ctx.close_path(); fill_stroke(ctx, DROP, lw=4, alpha=a)
        ctx.arc(dx - 12, dy + 4, 7, 0, 2 * math.pi); setc(ctx, WHITE, 0.8 * a); ctx.fill()
        tag(ctx, "STILL LIQUID", dx, dy + 105, TEAL, a, 24)

def draw_loupe(ctx, t, s):
    a = s['loupe']
    if a <= 0: return
    cx, cy, r = 600, 1150, 165
    ctx.move_to(cx + r * 0.72, cy + r * 0.72); ctx.line_to(cx + r * 1.15, cy + r * 1.15)
    setc(ctx, INK, a); ctx.set_line_width(22); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.arc(cx, cy, r, 0, 2 * math.pi); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(10); ctx.stroke()
    # left: a frozen bead (round, glassy)
    bx, by = cx - 68, cy - 10
    ctx.arc(bx, by, 46, 0, 2 * math.pi); fill_stroke(ctx, SNOW, ICE_E, lw=5, alpha=a)
    ctx.arc(bx - 14, by - 14, 10, 0, 2 * math.pi); setc(ctx, TEAL_L, 0.7 * a); ctx.fill()
    text_c(ctx, "BEAD", bx, by + 88, 22, TEAL, True, 1.5, a)
    # right: a star flake, crossed out
    fx, fy = cx + 72, cy - 10
    flake(ctx, fx, fy, 44, a * 0.75, INK2)
    k = clamp((t - B(10) - 0.9) / 0.5)
    if k > 0:
        ctx.move_to(fx - 50, fy - 50); ctx.line_to(fx - 50 + 100 * k, fy - 50 + 100 * k)
        ctx.move_to(fx + 50, fy - 50); ctx.line_to(fx + 50 - 100 * k, fy - 50 + 100 * k)
        setc(ctx, RED, a); ctx.set_line_width(9); ctx.stroke()
    text_c(ctx, "FLAKE", fx, fy + 88, 22, RED, True, 1.5, a)

def overlays(ctx, t, s):
    nx, ny = L2S(*NUC)
    jx, jy = L2S(NUC[0] + 80, NUC[1])
    a = s['answer']
    if a > 0:
        highlight(ctx, jx, jy, 80, 58, RED, a, t)
        straight_arrow(ctx, jx - 150, jy - 170, jx - 30, jy - 55, RED, a, lw=7, head=14)
        tag(ctx, "PUFF OF AIR", jx - 170, jy - 205, RED, a, 26)
    a = s['nuc']
    if a > 0:
        highlight(ctx, nx + 10, ny - 4, 58, 44, MUSTARD, a, t)
        tag(ctx, "1 · NUCLEATOR", nx - 120, ny - 120, INK, a, 24)
        ctx.move_to(nx - 60, ny - 98); ctx.line_to(nx - 12, ny - 22); setc(ctx, INK, a); ctx.set_line_width(3); ctx.stroke()
    a = s['feeds']
    if a > 0:
        wx, wy = L2S(-40, -R - 22); ax_, ay_ = L2S(-40, -R - 32)
        tag(ctx, "WATER", wx - 10, wy + 120, TEAL, a, 22)
        ctx.move_to(wx - 4, wy + 98); ctx.line_to(wx + 2, wy + 6); setc(ctx, TEAL, a); ctx.set_line_width(3); ctx.stroke()
        tag(ctx, "COMPRESSED AIR", ax_ + 60, ay_ - 110, INK2, a, 22)
        ctx.move_to(ax_ + 40, ay_ - 88); ctx.line_to(ax_ + 4, ay_ - 8); setc(ctx, INK2, a); ctx.set_line_width(3); ctx.stroke()
    a = s['seeds']
    if a > 0:
        sx, sy = bez(NS0, NS1, P2, 0.12)
        highlight(ctx, sx, sy, 90, 70, TEAL, a, t)
        tag(ctx, "SEEDS", sx + 30, sy - 115, TEAL, a, 26)
        star(ctx, sx - 52, sy - 115, 12, a)
    a = s['nozzles']
    if a > 0:
        fx, fy = L2S(HL + 20, 60)
        tag(ctx, "2 · WATER NOZZLES", fx + 150, fy + 150, TEAL, a, 24)
        ctx.move_to(fx + 110, fy + 128); ctx.line_to(fx + 12, fy + 10); setc(ctx, TEAL, a); ctx.set_line_width(3); ctx.stroke()
        tag(ctx, "BIG DROPS", bez(P0, P1, P2, 0.22)[0] + 40, bez(P0, P1, P2, 0.22)[1] + 150, TEAL, a, 22)
    a = s['fan']
    if a > 0:
        fx, fy = L2S(FAN_X, 0)
        highlight(ctx, fx, fy, 70, 100, MUSTARD, a, t)
        tag(ctx, "3 · FAN", fx - 20, fy + 190, INK, a, 24)
        # 'high' arrow along the trajectory
        pts = [bez(P0, P1, P2, u) for u in (0.04, 0.12, 0.2, 0.28)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            pass
        x0, y0 = bez(P0, P1, P2, 0.05); x1, y1 = bez(P0, P1, P2, 0.24)
        straight_arrow(ctx, x0, y0 - 150, x1, y1 - 150, RED, a, lw=7, head=14)
        tag(ctx, "HIGH, COLD AIR", x1 + 40, y1 - 220, RED, a, 22)
    a = s['freeze']
    if a > 0:
        hx, hy = bez(P0, P1, P2, 0.62)
        highlight(ctx, hx, hy, 150, 140, TEAL, a, t)
        tag(ctx, "SEED + DROP = ICE", hx - 200, hy + 210, INK, a, 24)
    a = s['loupe']
    if a > 0:
        tag(ctx, "MACHINE SNOW", P2[0] - 20, ground_y(P2[0]) - pile_h(t) - 50, INK, a, 22)
    a = s['recap']
    if a > 0:
        for k, (w, x) in enumerate((("AIR", 250), ("SEEDS", 540), ("SNOW", 830))):
            tag(ctx, w, x, 430, RED, a, 34)
        straight_arrow(ctx, 322, 430, 448, 430, RED, a, lw=6, head=12)
        straight_arrow(ctx, 632, 430, 748, 430, RED, a, lw=6, head=12)

def draw(ctx, t, E):
    s = state(t)
    draw_ground(ctx, t)
    draw_tower(ctx, t)
    draw_plume(ctx, t, s)
    draw_barrel(ctx, t, s)
    draw_jet(ctx, t, s)
    draw_props(ctx, t, s)
    draw_loupe(ctx, t, s)
    overlays(ctx, t, s)

def draw_set(ctx):
    pass

CAMKEYS = [(0, 520, 900, 1.3),
           (B(1) - 0.1, 610, 1010, 1.0),
           (B(3), 420, 860, 1.75),
           (B(6), 520, 830, 1.45),
           (B(7), 470, 930, 1.35),
           (B(8), 560, 960, 0.95),
           (B(9), 720, 1010, 1.12),
           (B(10), 700, 1060, 1.05),
           (B(11), 560, 930, 0.95)]
def CAM(t): return cam_track(CAMKEYS, t, move=0.7)
ANCHOR = (540, 1450)

SFX = [(0.4, 'pop'), (B(1) + 0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(4) + 0.3, 'pop'), (B(6) + 0.3, 'pop'),
       (B(7) + 0.3, 'pop'), (B(8) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(10) + 0.9, 'click'), (B(11) + 0.3, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_seed(ctx, t, lt, a):
    card_frame(ctx, "A SEED OF ICE", a, "ICE GROWS FROM A SEED", TEAL)
    # left: no seed -> stays liquid
    lx, ly, r = 330, 405, 78
    ctx.arc(lx, ly, r, 0, 2 * math.pi); fill_stroke(ctx, DROP, lw=5, alpha=a)
    ctx.arc(lx - 26, ly - 26, 14, 0, 2 * math.pi); setc(ctx, WHITE, 0.7 * a); ctx.fill()
    text_c(ctx, "NO SEED: LIQUID", lx, ly + 120, 22, TEAL, True, 1, a)
    text_c(ctx, "−5 °C · 23 °F", 540, 300, 22, INK2, True, 1, a)
    # right: a seed touches it -> freezes from the contact point
    rx, ry = 750, 405
    k = ease(clamp((lt - 0.4) / 1.0))                   # seed flies in from the upper right
    sx = lerp(rx + 210, rx + r * 0.7, k); sy = lerp(ry - 150, ry - r * 0.7, k)
    f = ease(clamp((lt - 1.5) / 1.6))                   # freezing front radius (from the contact point)
    ctx.arc(rx, ry, r, 0, 2 * math.pi); fill_stroke(ctx, DROP, lw=5, alpha=a)
    if f > 0:
        ctx.save(); ctx.arc(rx, ry, r - 2, 0, 2 * math.pi); ctx.clip()
        ctx.arc(rx + r * 0.7, ry - r * 0.7, f * 2.1 * r, 0, 2 * math.pi); setc(ctx, SNOW, a); ctx.fill()
        ctx.restore()
        ctx.arc(rx, ry, r, 0, 2 * math.pi); setc(ctx, lerpc(INK, ICE_E, f), a); ctx.set_line_width(5); ctx.stroke()
    star(ctx, sx, sy, 16, a)
    text_c(ctx, "SEED", sx + 46, sy - 18, 20, INK2, True, 1, a * (1 - f))
    text_c(ctx, "ICE" if f > 0.6 else "+ SEED", rx, ry + 120, 22, TEAL if f > 0.6 else INK2, True, 1, a)

def card_expand(ctx, t, lt, a):
    card_frame(ctx, "AIR EXPANDS, AIR GETS COLD", a, "AIR SPREADS OUT = AIR COOLS", TEAL)
    # nozzle drawn horizontally: air comes in from the LEFT, leaves on the RIGHT
    y = 410; x0, x1 = 150, 470
    ctx.move_to(x0, y - 60); ctx.line_to(x1 - 60, y - 60); ctx.line_to(x1, y - 16)
    ctx.move_to(x0, y + 60); ctx.line_to(x1 - 60, y + 60); ctx.line_to(x1, y + 16)
    setc(ctx, INK, a); ctx.set_line_width(8); ctx.stroke()
    text_c(ctx, "COMPRESSED AIR", 230, 316, 20, INK2, True, 1, a)
    # water drip entering from the top
    ctx.move_to(390, 290); ctx.line_to(390, y - 62); setc(ctx, TEAL, a); ctx.set_line_width(8); ctx.stroke()
    text_c(ctx, "WATER", 450, 300, 20, TEAL, True, 1, a)
    # packed air dots moving right inside the nozzle
    for j in range(22):
        u = (lt * 0.5 + rnd(j, 1)) % 1.0
        xx = lerp(x0 + 10, x1 - 10, u); yy = y + (rnd(j, 2) - 0.5) * lerp(100, 26, clamp((xx - (x1 - 60)) / 60))
        ctx.arc(xx, yy, 5, 0, 2 * math.pi); setc(ctx, AIR_L, a); ctx.fill()
    # outside: the same air spreads out (cone) = expansion
    for j in range(30):
        u = (lt * 0.45 + rnd(j, 3)) % 1.0
        xx = x1 + 6 + 330 * u; yy = y + (rnd(j, 4) - 0.5) * (24 + 230 * u)
        ctx.arc(xx, yy, 4, 0, 2 * math.pi); setc(ctx, AIR_L, a * (1 - u * 0.6)); ctx.fill()
        if lt > 2.6 and rnd(j, 5) < 0.4 and u > 0.45:
            star(ctx, xx, yy + 8, 7, a * clamp((lt - 2.6) / 0.5))
    straight_arrow(ctx, x1 + 40, y - 110, x1 + 250, y - 150, TEAL, a, lw=5, head=10)
    straight_arrow(ctx, x1 + 40, y + 110, x1 + 250, y + 150, TEAL, a, lw=5, head=10)
    # thermometer: the level drops as the air leaves
    lev = lerp(0.6, 0.12, ease(clamp((lt - 0.8) / 2.0)))
    thermometer(ctx, 905, 500, lev, a, TEAL, h=200)
    text_c(ctx, "COLD", 905, 286, 22, TEAL, True, 1, a * clamp((lt - 1.8) / 0.5))

CARDS = {'seed': card_seed, 'expand': card_expand}
