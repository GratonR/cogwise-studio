"""Cogwise episode: Trains are coupled loosely on purpose.
One idea: the play (slack) in every coupler lets the locomotive start the cars ONE AT A TIME. A car standing still
needs several times more pull to get moving than to keep rolling, so the locomotive never has to break all
the cars loose at once: each car is already rolling when its slack runs out and it yanks the next one.

VIEW (screen coordinates, y grows DOWN): main stage = SIDE VIEW, train heading RIGHT (locomotive on the right,
cars trail off-screen to the LEFT = "a hundred cars").
  - Unit 0 = locomotive, units 1..N = cars. Each unit is known by its FRONT x (right end of the body).
  - Play p_i between unit i-1 (ahead) and unit i (behind): 0 = coupler heads touching (bunched), SL = stretched.
  - Kinematics are simulated once at import from the locomotive's path X(t): a car only moves when the play in
    front of it is used up (pulled) or closed (pushed). So when the locomotive pulls forward, car i starts exactly
    when the locomotive has gone i * SL: one car at a time, front to back.
  - Knuckle panel = TOP VIEW (seen from above), labelled as such; ahead = right, like the stage.
"""
import math, cairo
from cogwise.style import *

META = dict(
    slug="train-slack",
    title="Trains are coupled loosely on purpose 🚂 #Shorts",
    description=("The slack lets the locomotive start one car at a time.\n\n"
                 "#Shorts #howthingswork #trains #railway #cogwise"),
    hashtags=["Shorts", "howthingswork", "trains", "railway", "engineering", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Slack_action",
        "https://www.advanced-steam.org/ufaqs/rolling-resistance/",
        "https://en.wikipedia.org/wiki/Railway_coupling",
        "https://forum.trains.com/t/starting-a-freight-train/244078",
    ],
)

def _d(c, extra=0.0):
    return round(0.42 * len(c.split()) + 0.7 + extra, 1)

_B = [
    ("ON PURPOSE", "Every freight train is coupled loosely. On purpose.", None),
    ("THE SECRET", "That slack lets the locomotive start the cars one at a time, not all at once.", None),
    ("STUCK", "A car standing still is much harder to get moving than to keep rolling.", None),
    (None, "Starting can take about four times the pull of rolling slowly.", 'ratio'),
    ("1 · THE KNUCKLE", "Each car grabs the next with a steel knuckle, like two clasped hands.", None),
    ("2 · THE PLAY", "Those knuckles never fit tight. There's play, plus a spring box behind each one.", None),
    ("3 · BUNCHED UP", "So engineers often ease back first, squeezing all that slack together.", None),
    ("PULL", "Then they pull. Only the first car is jerked into motion.", None),
    ("ONE BY ONE", "A moment later, its own slack runs out, and it yanks the second car.", None),
    (None, "Clack, clack, clack. That sound running down the train is the slack running out.", 'wave'),
    ("JUST ONE CAR", "The locomotive never fights a hundred stuck cars at once. Just one, again and again.", None),
    ("LOOSE ON PURPOSE", "Coupled tight, the same engine might not budge the train at all.", None),
]
BEATS = [dict(dur=_d(c), title=ti, caption=c, card=k) for ti, c, k in _B]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- palette
STEEL = hexc('#9aa0a8'); STEEL_D = hexc('#5d6168'); STEEL_L = hexc('#c9cdd3')
BOX = [hexc('#b5523b'), hexc('#c98f2e'), hexc('#3f7f86'), hexc('#8c5a3c')]
LOCO = hexc('#2f6b5a'); LOCO_L = hexc('#4f8f7b')
GREEN = hexc('#3d8b4f')
BALLAST = hexc('#c9b99a')

# ---------------------------------------------------------------- geometry (side view)
RAIL_Y = 1010            # top of rail
WR = 19                  # wheel radius
WY = RAIL_Y - WR         # wheel centre
CPL_Y = 958              # coupler height
CPL = 0
SL = 24                  # play per coupler (exaggerated for the eye)
HT = 12                  # hook tip length
HW = 5                   # hook bar width (with outline)
H0 = SL + HT + HW        # see hook_pair(): tip touches the other upright exactly at play = SL
HY = [946, 953, 960, 967]  # rows: A shank, B tip, A tip, B shank (side view)
L_LOCO = 230
L_CAR = 170
N = 12                   # cars drawn (more are implied off-screen; the camera never reaches the last ones)
LENS = [L_LOCO] + [L_CAR] * N
GAP0 = H0 + 10           # body-to-body distance when bunched (play = 0); hooks never reach into a body
X0 = 690.0               # locomotive front at the start (train bunched)

# ---------------------------------------------------------------- locomotive path X(t)
A0, A1 = 0.05, B(2) - 0.5                 # first start (hook + secret): bunched -> stretched
NA = 8                                   # cars started in the hook (the others stay off-screen)
DA = NA * SL + 2
K0, K1 = B(6) + 0.4, B(7) - 0.3          # ease back: stretched -> bunched
DK = NA * SL
P0 = B(7) + 0.1; P1 = B(12) + 3          # the real start, one car at a time, steady speed
VP = SL / 2.8                            # one car every 2.8 s
DP = VP * (P1 - P0)

def _ramp(u, a=0.12):
    """0..1, linear with soft start and soft stop (constant speed in the middle)."""
    u = clamp(u)
    v = 1.0 / (1.0 - a)                    # peak speed
    if u < a: return 0.5 * v * u * u / a
    if u > 1 - a: return 1.0 - 0.5 * v * (1 - u) ** 2 / a
    return 0.5 * v * a + v * (u - a)

def loco_x(t):
    x = X0
    x += DA * _ramp((t - A0) / (A1 - A0), 0.04)
    x -= DK * _ramp((t - K0) / (K1 - K0))
    x += DP * _ramp((t - P0) / (P1 - P0), 0.02)
    return x

# ---------------------------------------------------------------- simulate once (design time)
DT = 1 / 60
T_END = B(12) + 5
_TAB = []                                 # list of (fronts tuple)
def _simulate():
    fr = [X0]
    for i in range(1, N + 1):
        fr.append(fr[i - 1] - LENS[i - 1] - GAP0)          # bunched
    n = int(T_END / DT) + 2
    for k in range(n):
        t = k * DT
        fr[0] = loco_x(t)
        for i in range(1, N + 1):
            rear = fr[i - 1] - LENS[i - 1]
            lo, hi = rear - GAP0 - SL, rear - GAP0
            fr[i] = min(max(fr[i], lo), hi)
        _TAB.append(tuple(fr))
_simulate()

def fronts(t):
    k = clamp(t / DT, 0, len(_TAB) - 2)
    i = int(k); f = k - i
    a, b = _TAB[i], _TAB[i + 1]
    return [a[j] + (b[j] - a[j]) * f for j in range(N + 1)]

def speeds(t):
    a = fronts(max(0, t - 0.05)); b = fronts(t + 0.05)
    return [(b[j] - a[j]) / 0.1 for j in range(N + 1)]

def play(fr, i):
    """Play between unit i-1 and unit i (0 = touching, SL = stretched)."""
    return fr[i - 1] - LENS[i - 1] - GAP0 - fr[i]

# start times of each car in the pull phase (car i moves once the locomotive has gone i * SL)
def _start_times(t0, t1, back=False):
    out = {}
    for k in range(int(t0 / DT), int(t1 / DT)):
        for i in range(1, N + 1):
            if i in out: continue
            if abs(_TAB[k + 1][i] - _TAB[k][i]) > 0.05:
                out[i] = k * DT
    return out
START_A = _start_times(A0, A1 + 0.5)
START_P = _start_times(P0, P1 + 0.5)

# ---------------------------------------------------------------- camera
def wave_cam(t):
    """During beats 8-10 the camera slides left along the train to follow the start wave."""
    if t < B(8): return loco_x(t) - 330
    done = [i for i, ts in START_P.items() if ts <= t]
    k = max(done) if done else 1
    fr = fronts(t)
    return fr[k] - L_CAR / 2 + 220

Z0 = 1.35

def CAM(t):
    """Follows the locomotive (front 330 px right of centre); zooms on the first coupler for beats 4-5;
    slides left along the train with the start wave for beats 8-10."""
    cx, cy, z = loco_x(t) - 330, 910, Z0
    fr4 = fronts(B(4) + 0.5)
    cxk = fr4[0] - L_LOCO - GAP0 / 2 - SL / 2
    k = ease(clamp((t - B(4) - 0.1) / 0.8)) * (1 - ease(clamp((t - B(6) - 0.1) / 0.8)))
    cx, cy, z = lerp(cx, cxk, k), lerp(cy, 945, k), lerp(z, 2.3, k)
    if B(8) <= t < B(11) + 0.8:
        u = ease(clamp((t - B(8)) / 1.0)) * (1 - ease(clamp((t - B(11)) / 0.8)))
        cx = lerp(cx, min(cx, _smooth_wave(t)), u)
    return cx, cy, z

def _smooth_wave(t):
    acc = 0.0; n = 0
    for k in range(-6, 7):
        acc += wave_cam(t + k * 0.12); n += 1
    return acc / n

# ---------------------------------------------------------------- drawing
def wheel(ctx, x, a=1.0, spin=0.0):
    ctx.arc(x, WY, WR, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=3, alpha=a)
    ctx.arc(x, WY, 7, 0, 2 * math.pi); fill_stroke(ctx, STEEL_L, lw=2, alpha=a)
    ctx.move_to(x + 7 * math.cos(spin), WY + 7 * math.sin(spin))
    ctx.line_to(x + (WR - 4) * math.cos(spin), WY + (WR - 4) * math.sin(spin))
    setc(ctx, STEEL_L, a); ctx.set_line_width(3); ctx.stroke()

def truck(ctx, xc, spin):
    ctx.rectangle(xc - 34, WY - 12, 68, 14); fill_stroke(ctx, INK2, lw=2)
    wheel(ctx, xc - 22, spin=spin); wheel(ctx, xc + 22, spin=spin)

def coupler(ctx, x_end, side, col=STEEL):
    """side = +1: sticks out to the right of x_end (front), -1: to the left (rear)."""
    x1 = x_end + side * CPL
    ctx.rectangle(min(x_end, x1 - side * 4), CPL_Y - 4, abs(x1 - side * 4 - x_end), 8); fill_stroke(ctx, STEEL_D, lw=2)
    hx = x1 - (6 if side > 0 else 0)
    ctx.rectangle(min(hx, x1), CPL_Y - 10, 6, 20); fill_stroke(ctx, col, lw=2.5)

def hook_pair(ctx, fb, ra, lw=4):
    """Coupler pair between a car (front at fb, BEHIND, left) and the unit ahead (rear at ra, right).
    Schematic interlocking knuckles, same geometry as the top-view panel. Each coupler is rigid:
    A's reach from fb = (GAP0 + H0) / 2 whatever the play. Play p = ra - fb - GAP0 in [0, SL].
    Pulled (p = SL): A's tip touches B's upright and B's tip touches A's upright."""
    p = ra - fb - GAP0
    c = (fb + ra) / 2; h = (H0 - p) / 2
    A = [(fb, HY[0]), (c + h, HY[0]), (c + h, HY[2]), (c + h - HT, HY[2])]
    Bp = [(ra, HY[3]), (c - h, HY[3]), (c - h, HY[1]), (c - h + HT, HY[1])]
    for pts, col in ((A, STEEL_D), (Bp, STEEL_L)):
        ctx.move_to(*pts[0])
        for q in pts[1:]: ctx.line_to(*q)
        ctx.set_line_join(cairo.LINE_JOIN_MITER); ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        setc(ctx, INK); ctx.set_line_width(lw + 2); ctx.stroke()
        ctx.move_to(*pts[0])
        for q in pts[1:]: ctx.line_to(*q)
        setc(ctx, col); ctx.set_line_width(lw); ctx.stroke()
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

def boxcar(ctx, i, xf, spin):
    xr = xf - L_CAR
    col = BOX[(i - 1) % len(BOX)]
    ctx.rectangle(xr + 4, 950, L_CAR - 8, 12); fill_stroke(ctx, INK2, lw=2)           # underframe
    rrect(ctx, xr + 2, 848, L_CAR - 4, 104, 6); fill_stroke(ctx, col, lw=4)          # body
    for k in range(1, 6):                                                             # ribs
        xx = xr + 2 + (L_CAR - 4) * k / 6
        ctx.move_to(xx, 854); ctx.line_to(xx, 946)
    setc(ctx, INK, 0.35); ctx.set_line_width(2); ctx.stroke()
    ctx.rectangle(xf - L_CAR / 2 - 22, 862, 44, 82); setc(ctx, INK, 0.22); ctx.fill()  # door
    truck(ctx, xr + 36, spin); truck(ctx, xf - 36, spin)

def locomotive(ctx, xf, spin):
    xr = xf - L_LOCO
    ctx.rectangle(xr + 2, 950, L_LOCO - 4, 14); fill_stroke(ctx, INK, lw=3)           # frame
    rrect(ctx, xr + 12, 878, L_LOCO - 110, 74, 6); fill_stroke(ctx, LOCO, lw=4)       # long hood
    for k in range(5):                                                                # grilles
        xx = xr + 26 + k * 20
        ctx.move_to(xx, 890); ctx.line_to(xx, 940)
    setc(ctx, INK, 0.35); ctx.set_line_width(3); ctx.stroke()
    rrect(ctx, xf - 98, 826, 62, 126, 6); fill_stroke(ctx, LOCO_L, lw=4)              # cab
    ctx.rectangle(xf - 88, 840, 42, 30); fill_stroke(ctx, hexc('#cfe3e6'), lw=3)       # window
    rrect(ctx, xf - 36, 898, 30, 54, 5); fill_stroke(ctx, LOCO, lw=4)                 # short nose
    ctx.arc(xf - 14, 912, 6, 0, 2 * math.pi); fill_stroke(ctx, MUSTARD, lw=2)        # headlight
    ctx.rectangle(xr + 2, 952, L_LOCO - 4, 5); setc(ctx, MUSTARD); ctx.fill()        # stripe
    truck(ctx, xr + 48, spin); truck(ctx, xf - 52, spin)

def track(ctx, t, x0=-2300, x1=1500):
    ctx.rectangle(x0, RAIL_Y + 8, x1 - x0, 34); setc(ctx, BALLAST); ctx.fill()
    for k in range(int((x1 - x0) / 34)):
        xx = x0 + k * 34
        ctx.rectangle(xx, RAIL_Y + 4, 20, 10); fill_stroke(ctx, hexc('#7a5a3c'), lw=1.5)
    ctx.rectangle(x0, RAIL_Y, x1 - x0, 6); fill_stroke(ctx, STEEL_D, lw=2)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    fr = fronts(t)
    track(ctx, t)
    for i in range(N, 0, -1):
        boxcar(ctx, i, fr[i], (fr[i] - X0) / WR)
    locomotive(ctx, fr[0], (fr[0] - X0) / WR)
    for i in range(1, N + 1):
        hook_pair(ctx, fr[i], fr[i - 1] - LENS[i - 1])
    overlays(ctx, t, fr)

def gap_mark(ctx, fr, i, a, col=RED, label=None, size=22):
    """Red bracket over the play between unit i-1 and unit i."""
    if a <= 0: return
    xa = fr[i]; xb = fr[i - 1] - LENS[i - 1]
    p = xb - xa
    y = CPL_Y - 30
    ctx.move_to(xa, y + 12); ctx.line_to(xa, y); ctx.line_to(max(xb, xa + 2), y); ctx.line_to(max(xb, xa + 2), y + 12)
    setc(ctx, col, a); ctx.set_line_width(4); ctx.stroke()
    if label:
        tag(ctx, label, (xa + xb) / 2, y - 112, col, a, size)

def overlays(ctx, t, fr):
    # hook + secret: the play opens one coupler after another
    a = win(t, 0.2, B(2), 0.3)
    if a > 0:
        for i in range(1, N + 1):
            ts = START_A.get(i, 99)
            g = clamp((t - (ts - 0.9)) / 0.4)          # bracket appears as that gap opens
            gap_mark(ctx, fr, i, a * g, RED)
        tag(ctx, "SLACK", fr[1] + 30, 760, RED, win(t, 0.6, B(1), 0.3), 30)
    a = bw(t, 1)
    if a > 0:
        v = speeds(t)
        for i in range(0, N + 1):
            if v[i] > 3 and fr[i] > -200:
                tag(ctx, "MOVING", fr[i] - LENS[i] / 2, 1080, GREEN, a, 22)
    # zoom on the first coupler (beats 4-5): the play between the bodies
    gap_mark(ctx, fr, 1, bw(t, 5), RED)
    # stuck
    a = bw(t, 2)
    if a > 0:
        xc = fr[1] - L_CAR / 2
        highlight(ctx, xc, WY, L_CAR / 2 + 10, 40, RED, a, t)
        tag(ctx, "STANDING STILL", xc, 790, RED, a, 26)
    # bunched (beat 6)
    a = bw(t, 6)
    if a > 0:
        straight_arrow(ctx, fr[0] - 40, 790, fr[0] - 150, 790, RED, a, lw=8, head=14)
        tag(ctx, "EASE BACK", fr[0] - 95, 735, RED, a, 24)
        for i in range(1, N + 1):
            p = play(fr, i)
            if p < 1.0:
                xa = (fr[i] + fr[i - 1] - LENS[i - 1]) / 2
                ctx.arc(xa, CPL_Y, 26, 0, 2 * math.pi); setc(ctx, TEAL, a); ctx.set_line_width(4); ctx.stroke()
        tag(ctx, "SLACK SQUEEZED OUT", fr[0] - 450, 1090, TEAL, a * clamp((t - B(6) - 1.5) / 0.5), 24)
    # pull: moving vs still
    a = max(bw(t, 7), bw(t, 8))
    if a > 0:
        v = speeds(t)
        for i in range(1, N + 1):
            if fr[i] < -1200: continue
            xc = fr[i] - L_CAR / 2
            if v[i] > 3:
                tag(ctx, "ROLLING", xc, 1085, GREEN, a, 22)
            else:
                tag(ctx, "STILL", xc, 1085, INK2, a, 22)
        straight_arrow(ctx, fr[0] - 120, 790, fr[0] + 10, 790, GREEN, a, lw=8, head=14)
    # the car being yanked right now (beats 7-10)
    a = max(bw(t, 7, 11), 0)
    if a > 0:
        for i, ts in START_P.items():
            lt = t - ts
            if -0.05 < lt < 1.1:
                xc = fr[i] - L_CAR / 2
                k = clamp(lt / 0.25)
                highlight(ctx, xc, 900, L_CAR / 2 + 8, 80, RED, a * (1 - ease(clamp((lt - 0.7) / 0.4))), t)
                if lt < 0.6:
                    text_c(ctx, "CLACK!", fr[i] + 12, 800 - 20 * k, 30, RED, True, 2, a * (1 - clamp((lt - 0.4) / 0.2)))
    a = bw(t, 10)
    if a > 0:
        cur = [i for i, ts in START_P.items() if ts <= t]
        k = max(cur) if cur else 1
        tag(ctx, "ONE CAR AT A TIME", CAM(t)[0], 680, RED, a, 26)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=180, w=960, h=320):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def _thick(ctx, pts, col, a, lw=22):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.set_line_join(cairo.LINE_JOIN_MITER)
    setc(ctx, INK, a); ctx.set_line_width(lw + 6); ctx.stroke()
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    setc(ctx, col, a); ctx.set_line_width(lw); ctx.stroke()
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

def spring_box(ctx, x0, x1, yc, a, squeeze=0.0):
    ctx.rectangle(x0, yc - 34, x1 - x0, 68); fill_stroke(ctx, FILL2, lw=3, alpha=a)
    n = 7; xa = x0 + 8; xb = x1 - 8 - squeeze
    ctx.move_to(xa, yc)
    for k in range(n * 2):
        ctx.line_to(xa + (xb - xa) * (k + 0.5) / (n * 2), yc + (22 if k % 2 == 0 else -22))
    ctx.line_to(xb, yc)
    setc(ctx, RED, a); ctx.set_line_width(4); ctx.stroke()

def knuckles(ctx, t, a, shift=0.0, springs=False):
    """TOP VIEW. Car behind = left (A), car ahead = right (B). Hooks interlock with play.
    shift > 0 pulls them apart (A left, B right): both hook contacts touch when shift = 13 (lines are 28 px wide)."""
    ym = 300
    sa = -shift; sb = shift
    xA = 560 + sa; xB = 450 + sb
    col = STEEL
    A = [(150 + sa, ym), (xA, ym), (xA, ym + 80), (xA - 70, ym + 80)]
    Bp = [(930 + sb, ym + 130), (xB, ym + 130), (xB, ym + 40), (xB + 70, ym + 40)]
    if springs:
        sq = 0.0
        spring_box(ctx, 120, 290, ym, a, sq)
        spring_box(ctx, 790, 960, ym + 130, a, sq)
        A[0] = (290 + sa, ym); Bp[0] = (790 + sb, ym + 130)
    _thick(ctx, A, col, a)
    _thick(ctx, Bp, STEEL_L, a)

def knuckle_panel(ctx, t, a):
    _panel(ctx, a)
    text_c(ctx, "SEEN FROM ABOVE", 540, 232, 24, INK2, True, 2, a)
    lt = t - B(4)
    knuckles(ctx, t, a, shift=13 * ease(clamp((lt - 1.2) / 0.8)))
    text_c(ctx, "CAR BEHIND", 210, 275, 20, INK, True, 1, a)
    text_c(ctx, "CAR AHEAD", 870, 470, 20, INK, True, 1, a)
    text_c(ctx, "KNUCKLES", 520, 480, 26, RED, True, 2, a)

def play_panel(ctx, t, a):
    _panel(ctx, a)
    text_c(ctx, "SEEN FROM ABOVE", 540, 232, 24, INK2, True, 2, a)
    lt = t - B(5)
    s = 6.5 - 6.5 * math.cos(lt * 2.4)       # free play: slides from touching (0) to pulled tight (13)
    knuckles(ctx, t, a, shift=s, springs=True)
    xa_tip = 490 - s; xb_up = 450 + s + 14   # hook tip of A, right face of B's upright
    gx = (xa_tip + xb_up) / 2
    highlight(ctx, gx, 380, 34, 30, RED, a, t)
    text_c(ctx, "PLAY", 345, 392, 30, RED, True, 2, a)
    text_c(ctx, "SPRING BOX", 205, 362, 20, RED, True, 1, a)
    text_c(ctx, "SPRING BOX", 875, 490, 20, RED, True, 1, a)

def recap_panel(ctx, t, a):
    _panel(ctx, a, y=185, h=200)
    text_c(ctx, "LOOSE = ONE CAR AT A TIME", 540, 262, 46, GREEN, True, 2, a)
    text_c(ctx, "TIGHT = ALL CARS AT ONCE", 540, 340, 40, RED, True, 2, a)

def draw_hud(ctx, t, E):
    a = win(t, B(4) + 0.2, B(5), 0.3)
    if a > 0: knuckle_panel(ctx, t, a)
    a = win(t, B(5) + 0.1, B(6), 0.3)
    if a > 0: play_panel(ctx, t, a)
    a = win(t, B(11) + 0.4, B(12) + 2, 0.3)
    if a > 0: recap_panel(ctx, t, a)

# ---------------------------------------------------------------- cards
def card_ratio(ctx, t, lt, a):
    card_frame(ctx, "PULL NEEDED, PER TONNE", a, "ABOUT 4× MORE TO START", RED)
    g = ease(clamp((lt - 0.3) / 1.2))
    x0 = 330; unit = 140
    text_c(ctx, "TO START", 215, 335, 26, INK, True, 1, a)
    rrect(ctx, x0, 300, unit * 4.0 * g, 52, 8); fill_stroke(ctx, RED, lw=3, alpha=a)
    text_c(ctx, "TO KEEP ROLLING", 215, 455, 22, INK, True, 1, a)
    rrect(ctx, x0, 420, unit * 1.0 * min(1, g * 4), 52, 8); fill_stroke(ctx, TEAL, lw=3, alpha=a)
    if g > 0.95:
        text_c(ctx, "≈ 4", x0 + unit * 4 + 50, 338, 30, RED, True, 1, a)
        text_c(ctx, "1", x0 + unit + 30, 458, 30, TEAL, True, 1, a)

def card_wave(ctx, t, lt, a):
    card_frame(ctx, "THE START, FRONT TO BACK", a, "EACH CLACK = ONE CAR STARTING", RED)
    n = 7; w = 96; gap = 14; y = 410
    xr = 940                                         # locomotive on the right
    ctx.rectangle(xr - 90, y - 50, 90, 60); fill_stroke(ctx, LOCO, lw=3, alpha=a)
    ctx.rectangle(xr - 34, y - 78, 30, 30); fill_stroke(ctx, LOCO_L, lw=3, alpha=a)
    for k in range(n):
        x1 = xr - 90 - gap - k * (w + gap)
        started = lt > 0.5 + k * 0.42
        sh = 6 if started else 0
        ctx.rectangle(x1 - w + sh, y - 44, w, 54); fill_stroke(ctx, BOX[k % 4], lw=3, alpha=a)
        for xx in (x1 - w + 18 + sh, x1 - 18 + sh):
            ctx.arc(xx, y + 18, 9, 0, 2 * math.pi); fill_stroke(ctx, STEEL_D, lw=2, alpha=a)
        lk = lt - (0.5 + k * 0.42)
        if 0 < lk < 0.7:
            text_c(ctx, "CLACK", x1 + gap / 2, y - 80 - 30 * lk, 22, RED, True, 1, a * (1 - lk / 0.7))
    ctx.move_to(130, y + 40); ctx.line_to(950, y + 40); setc(ctx, STEEL_D, a); ctx.set_line_width(4); ctx.stroke()
    straight_arrow(ctx, 700, 500, 250, 500, RED, a, lw=5, head=12)

CARDS = {'ratio': card_ratio, 'wave': card_wave}

SFX = ([(0.2, 'click')] + [(START_A[i], 'pop') for i in (1, 2, 3) if i in START_A]
       + [(B(2) + 0.3, 'pop'), (B(6) + 0.4, 'click')]
       + [(START_P[i], 'pop') for i in sorted(START_P) if i <= 6]
       + [(B(10) + 0.4, 'pop'), (B(11) + 0.5, 'pop')])
HUM = []
