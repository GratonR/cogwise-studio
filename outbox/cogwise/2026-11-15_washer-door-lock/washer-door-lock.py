"""Cogwise episode: Your washer makes you wait before the door opens. Some don't.
One idea: most washer door locks are THERMAL — a PTC ceramic pill heats a bimetal snap disc, the disc flips and
pushes a pin through the door hook; after the cycle the disc needs 1-2 min to cool before it flips back.
Contrast (beat 11): instant locks use an electromagnet and the control board checks the drum has stopped first.

VIEWS (screen coordinates, y grows DOWN):
  - beats 1 and 12: FRONT view of the washer. Door hinge on the LEFT, the lock block on the cabinet RIGHT of the door.
  - beats 2-11: SECTION of the lock block, seen from the front. Vertical stack, bottom to top:
      heater pill (y 1150-1205) -> bimetal disc (rim at y 1100) -> pin (vertical) -> door hook (horizontal, y 760-810).
    The hook comes in from the LEFT (door side) through the slot in the housing's left wall.
    Disc: top layer = metal that expands MORE (mustard), bottom = expands less (grey).
      cold: dome bows DOWN (centre y 1140, pin top y 830, below the hook = unlocked)
      hot : dome bows UP   (centre y 1060, pin top y 750, through the hook's eye = locked)
      -> the high-expansion layer is on the convex (outer) side when hot: correct bimetal physics.
    Switch: an arm fixed on the pin rises with it and touches the fixed contact (y 880) only when hot/locked.
  - beat 11: same housing, hook and pin; the disc + pill are replaced by an ELECTROMAGNET under the pin,
    which pulls the iron pin DOWN (out of the hook) in one click.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="washer-door-lock",
    title="Your washer makes you wait before the door opens. Some don't. 🔒 #Shorts",
    description=("That locked-door wait isn't a fault. It's a tiny heater cooling down.\n\n"
                 "#Shorts #howthingswork #appliances #washingmachine #cogwise"),
    hashtags=["Shorts", "howthingswork", "appliances", "washingmachine", "cogwise"],
    sources=[
        "https://www.whitegoodshelp.co.uk/?p=17895",
        "https://forum.whitegoodshelp.co.uk/questions/3194/washing-machine-door-locks-4851",
        "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4664429",
    ],
)

BEATS = [
    dict(dur=4.9, title="WAIT?", caption="Your washer makes you wait before the door opens. Some don't."),
    dict(dur=5.3, title="THE SECRET", caption="Most washer doors are locked by a tiny heater, not a motor."),
    dict(dur=5.7, title="1 · THE HEATER", caption="Inside the lock, a small ceramic pill heats up when the cycle starts."),
    dict(dur=4.9, title="2 · THE DISC", caption="Against it sits a disc made of two metals bonded together."),
    dict(dur=6.5, title=None, caption="One metal stretches more with heat, so the warm disc suddenly snaps the other way.", card='bimetal'),
    dict(dur=4.5, title="3 · THE PIN", caption="That snap pushes a pin into the door's hook. Locked."),
    dict(dur=5.7, title="SAFE TO FILL", caption="The same move closes a switch, so the machine can fill and spin."),
    dict(dur=6.9, title="THE WAIT", caption="At the end, the heater stops, but the disc needs a minute or two to cool."),
    dict(dur=4.9, title="UNLOCK", caption="Only then does it snap back and pull the pin out."),
    dict(dur=6.9, title=None, caption="Even in a power cut mid-spin, the heat keeps the door shut while the drum slows.", card='powercut'),
    dict(dur=7.3, title="NO WAITING", caption="If yours opens instantly with a click, that's an electromagnet, and the machine checks the drum first."),
    dict(dur=5.3, title="WAIT = HEAT", caption="So that wait isn't a fault. It's a tiny heater cooling down."),
]


ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

STEEL = hexc('#9aa3ab'); STEEL_D = hexc('#6d757c')
BRASS = MUSTARD
PILL_C = hexc('#d8cdb8'); HOT = hexc('#ff5a2a')
GLASS = hexc('#bfe3df'); DRUM = hexc('#c9ccd0')
COPPER = hexc('#c46d2e'); BLUE = hexc('#2f6fb3')

# ---------------------------------------------------------------- geometry (section)
HX0, HX1, HY0, HY1 = 200, 880, 600, 1300          # housing
PX = 470                                          # pin axis x
HOOK_Y0, HOOK_Y1 = 760, 810                       # hook bar
EYE_X0, EYE_X1 = 445, 495                         # hook eye
DISC_X0, DISC_X1, DISC_Y = 320, 620, 1100
PILL = (400, 1150, 140, 55)
CONTACT_Y = 880

# front view
WX, WY, WW, WH = 130, 430, 600, 980
DCX, DCY, DR = 430, 980, 230
LOCK = (690, 950, 36, 60)
SWX, SWY, SWW, SWH = 790, 1050, 250, 360

def smooth_step(t, t0, d=0.18):
    return ease(clamp((t - t0) / d))

def state(t):
    s = {}
    s['lit'] = smooth_step(t, 0.3)
    s['glow1'] = win(t, 1.0, B(1) + 0.4, 0.3)
    s['small_open'] = smooth_step(t, 2.6, 0.35)
    # zoom into the lock block (beat 2), back out to the washer (beat 12)
    s['zoom'] = ease(clamp((t - B(1) - 0.15) / 0.9))
    s['turn'] = clamp((t - B(1) - 0.5) / 0.6) * (1 - clamp((t - B(11) - 0.1) / 0.8))
    # heater: on from beat 2 (cycle running), off at beat 8; on again (hidden) never
    s['heat'] = smooth_step(t, B(1) + 0.6, 0.8) * (1 - smooth_step(t, B(7) + 0.5, 1.6))
    if t >= B(9): s['heat'] = 0.0
    # disc temperature (lags the heater), drives the colour of the disc
    s['dtemp'] = smooth_step(t, B(2) + 0.8, 2.5) * (1 - smooth_step(t, B(7) + 1.5, 4.0))
    # snap: flips UP at the start of beat 6, flips DOWN at the start of beat 9
    up = smooth_step(t, B(5) + 0.25, 0.12) * (1 - smooth_step(t, B(8) + 0.35, 0.12))
    # beat 10 (power cut): back to the locked, still-hot state, heater OFF
    pc = win(t, B(9) + 0.05, B(10) + 0.2, 0.25)
    s['pc'] = pc
    s['up'] = max(up, pc)
    if pc > 0: s['dtemp'] = max(s['dtemp'], 0.8 * pc)
    # hook: in the slot until unlock, slides out to the left after the unlock, back in for beat 10/11
    out9 = smooth_step(t, B(8) + 0.9, 0.6) * (1 - smooth_step(t, B(9) + 0.05, 0.25))
    out11 = smooth_step(t, B(10) + 3.8, 0.6)
    s['hook_out'] = max(out9, out11)
    # beat 11: electromagnet variant
    s['em'] = win(t, B(10) + 0.05, B(11) + 0.2, 0.3)
    s['em_pull'] = smooth_step(t, B(10) + 3.2, 0.10)
    s['em_on'] = win(t, B(10) + 3.1, B(10) + 4.6, 0.15)
    s['flow'] = win(t, B(6) + 0.3, B(7) + 0.5, 0.3)
    s['recap'] = win(t, B(11) + 0.9, B(12) + 2, 0.3)
    return s

# ---------------------------------------------------------------- small pieces
def padlock(ctx, x, y, sc, closed, col, a):
    if a <= 0: return
    w, h = 44 * sc, 34 * sc
    lift = 0 if closed else 12 * sc
    ctx.new_path()
    ctx.arc(x, y - h / 2 - lift, w * 0.32, math.pi, 2 * math.pi)
    setc(ctx, col, a); ctx.set_line_width(7 * sc); ctx.stroke()
    if not closed: pass
    rrect(ctx, x - w / 2, y - h / 2, w, h, 5 * sc); fill_stroke(ctx, col, lw=3 * sc, alpha=a)
    ctx.arc(x, y, 4 * sc, 0, 2 * math.pi); setc(ctx, INK, a); ctx.fill()

def washer(ctx, x, y, w, h, cx, cy, r, open_k, lit, t, a=1.0, lock=None):
    rrect(ctx, x, y, w, h, 22); fill_stroke(ctx, PAPER, lw=5, alpha=a)
    ph = h * 0.12
    rrect(ctx, x + 14, y + 14, w - 28, ph, 12); fill_stroke(ctx, FILL2, lw=3, alpha=a)
    kx = x + w * 0.25
    ctx.arc(kx, y + 14 + ph / 2, ph * 0.3, 0, 2 * math.pi); fill_stroke(ctx, FILL3, lw=3, alpha=a)
    # padlock light (red when locked)
    lx = x + w * 0.8; ly = y + 14 + ph / 2 + 4
    padlock(ctx, lx, ly, w / 600, lit > 0.5, lerpc(FILL3, RED, lit), a)
    # door opening (dark) + drum
    ctx.arc(cx, cy, r * 0.86, 0, 2 * math.pi); setc(ctx, INK2, a); ctx.fill()
    ctx.arc(cx, cy, r * 0.74, 0, 2 * math.pi); fill_stroke(ctx, DRUM, lw=3, alpha=a)
    rnd = random.Random(4)
    for i in range(14):
        an = rnd.uniform(0, 6.28); rr = rnd.uniform(0.2, 0.65) * r
        ctx.arc(cx + rr * math.cos(an), cy + rr * math.sin(an), r * 0.025, 0, 6.28); setc(ctx, INK2, 0.5 * a); ctx.fill()
    # the door, hinge on the LEFT: swings open by squashing toward the hinge
    k = 1 - 0.82 * open_k
    hx = cx - r
    ctx.save(); ctx.translate(hx, cy); ctx.scale(k, 1); ctx.translate(-hx, -cy)
    ctx.arc(cx, cy, r, 0, 2 * math.pi); fill_stroke(ctx, FILL3, lw=5, alpha=a)
    ctx.arc(cx, cy, r * 0.78, 0, 2 * math.pi); setc(ctx, GLASS, 0.75 * a * (1 - 0.5 * open_k)); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
    ctx.arc(cx - r * 0.3, cy - r * 0.3, r * 0.3, math.pi * 1.05, math.pi * 1.5); setc(ctx, WHITE, 0.6 * a); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()
    rrect(ctx, hx - 14, cy - 40, 22, 80, 6); fill_stroke(ctx, FILL3, lw=3, alpha=a)    # hinge
    if lock:
        lx0, ly0, lw_, lh = lock
        rrect(ctx, lx0, ly0, lw_, lh, 6); fill_stroke(ctx, FILL3, lw=3, alpha=a)

def front_view(ctx, t, s):
    k = 1 - ease(s['turn'])
    if k <= 0.01: return
    z = 1 + 3.5 * s['zoom'] * (1 if t < B(6) else 0)
    lx, ly = LOCK[0] + LOCK[2] / 2, LOCK[1] + LOCK[3] / 2
    ctx.push_group()
    ctx.save(); ctx.translate(lx, ly); ctx.scale(z, z); ctx.translate(-lx, -ly)
    washer(ctx, WX, WY, WW, WH, DCX, DCY, DR, 0, max(s['lit'], s['recap']), t, lock=LOCK)
    # the answer, visible from ~1 s: the lock block glows with heat
    g = s['glow1'] if t < B(6) else 0.6 * s['recap'] * (1 - clamp((t - B(11) - 2.5) / 1.5))
    if g > 0:
        ctx.arc(lx, ly, 34, 0, 6.28); setc(ctx, HOT, 0.55 * g); ctx.fill()
        for i in range(3):
            wavy_arrow(ctx, lx - 22 + i * 22, LOCK[1] - 8, lx - 22 + i * 22, LOCK[1] - 70, t, RED, g, amp=5, wl=24, lw=4, head=9)
    ctx.restore()
    if t < B(6):
        # second, smaller washer: opens straight away with a click
        washer(ctx, SWX, SWY, SWW, SWH, SWX + SWW / 2, SWY + 210, 85, s['small_open'], 0, t, a=1 - s['zoom'])
    ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
    if t < B(6):
        a1 = s['lit'] * (1 - s['zoom']) * k
        tag(ctx, "LOCKED", DCX, WY + WH + 45, RED, a1, 28)
        tag(ctx, "HEAT?", 760, 860, RED, s['glow1'] * (1 - s['zoom']) * k, 26)
        a2 = s['small_open'] * (1 - s['zoom']) * k
        tag(ctx, "CLICK · OPEN", SWX + SWW / 2, WY + WH + 45, TEAL, a2, 26)
    ra = s['recap'] * k
    if ra > 0:
        tag(ctx, "WAIT = HEAT", DCX, WY + WH + 45, RED, ra, 30)

# ---------------------------------------------------------------- section of the lock
def disc_mid(up):
    """y of the disc centre: cold bows DOWN (+40), hot bows UP (-40)."""
    return DISC_Y + lerp(40, -40, up)

def disc_path(ctx, h, off=0):
    # quadratic dome from rim to rim; mid y = DISC_Y + h  -> control y = DISC_Y + 2h
    x0, x1 = DISC_X0, DISC_X1; cx = (x0 + x1) / 2; cy = DISC_Y + 2 * h
    ctx.move_to(x0, DISC_Y + off)
    ctx.curve_to(x0 + (cx - x0) * 2 / 3, DISC_Y + off + (cy - DISC_Y) * 2 / 3,
                 x1 + (cx - x1) * 2 / 3, DISC_Y + off + (cy - DISC_Y) * 2 / 3, x1, DISC_Y + off)

def section(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.35) / 0.65))
    if a <= 0: return
    em = s['em']
    up = s['up']
    pin_top_th = disc_mid(up) - 310
    pin_top_em = lerp(750, 830, s['em_pull'])
    pin_top = lerp(pin_top_th, pin_top_em, em)
    ctx.push_group()
    # housing (cream box) with the hook slot on the LEFT wall
    rrect(ctx, HX0, HY0, HX1 - HX0, HY1 - HY0, 24); fill_stroke(ctx, FILL2, lw=6)
    ctx.rectangle(HX0 - 4, HOOK_Y0 - 12, 14, HOOK_Y1 - HOOK_Y0 + 24); setc(ctx, FILL2); ctx.fill()
    # pin guide
    for x0, x1 in ((395, PX - 18), (PX + 18, 545)):
        ctx.rectangle(x0, 860, x1 - x0, 40); fill_stroke(ctx, FILL3, lw=3)
    # door edge (left) and the hook
    ho = s['hook_out'] * 330
    ctx.save(); ctx.translate(-ho, 0)
    rrect(ctx, 30, 620, 90, 380, 14); fill_stroke(ctx, FILL3, lw=4)
    text_c(ctx, "DOOR", 75, 1040, 24, INK2, True, 2)
    ctx.new_path()
    ctx.rectangle(110, HOOK_Y0, 410, HOOK_Y1 - HOOK_Y0)
    ctx.rectangle(EYE_X1, HOOK_Y0 + 10, EYE_X0 - EYE_X1, HOOK_Y1 - HOOK_Y0 - 20)   # eye (reverse winding = hole)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); fill_stroke(ctx, STEEL, lw=4); ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.restore()
    # thermal parts (fade out in beat 11)
    ta = 1 - em
    if ta > 0:
        # heater pill: beige when cold, glowing red-orange when hot
        x, y, w, h = PILL
        rrect(ctx, x, y, w, h, h / 2); fill_stroke(ctx, lerpc(PILL_C, HOT, s['heat']), lw=4, alpha=ta)
        for yy in (y + 18, y + 37):   # wires to the right wall
            ctx.move_to(x + w, yy); ctx.line_to(HX1, yy); setc(ctx, COPPER, ta); ctx.set_line_width(5); ctx.stroke()
        # rim supports
        for xx in (DISC_X0, DISC_X1):
            rrect(ctx, xx - 26, DISC_Y - 6, 52, 40, 6); fill_stroke(ctx, FILL3, lw=3, alpha=ta)
        # bimetal disc: grey (expands less) below, mustard (expands more) on top
        hm = lerp(40, -40, up)
        warm = s['dtemp']
        disc_path(ctx, hm, 9); setc(ctx, lerpc(STEEL_D, hexc('#b0584a'), 0.5 * warm), ta); ctx.set_line_width(12); ctx.stroke()
        disc_path(ctx, hm, -3); setc(ctx, lerpc(BRASS, ORANGE, warm), ta); ctx.set_line_width(12); ctx.stroke()
        disc_path(ctx, hm, 3); setc(ctx, INK, 0.6 * ta); ctx.set_line_width(2); ctx.stroke()
    if em > 0:
        # electromagnet under the pin: iron core + copper windings, field lines when ON
        cx = PX
        rrect(ctx, cx - 110, 1090, 220, 170, 12); fill_stroke(ctx, FILL3, lw=4, alpha=em)
        ctx.rectangle(cx - 30, 1060, 60, 200); fill_stroke(ctx, STEEL_D, lw=3, alpha=em)
        for i in range(8):
            yy = 1100 + i * 19
            rrect(ctx, cx - 95, yy, 190, 15, 7); fill_stroke(ctx, COPPER, lw=2, alpha=em)
        ctx.rectangle(cx - 30, 1060, 60, 30); fill_stroke(ctx, STEEL_D, lw=3, alpha=em)
        for yy in (1140, 1200):
            ctx.move_to(cx + 110, yy); ctx.line_to(HX1, yy); setc(ctx, COPPER, em); ctx.set_line_width(5); ctx.stroke()
        on = s['em_on'] * em
        if on > 0:
            for k in range(3):
                ctx.save(); ctx.translate(PX, 1175); ctx.scale(150 + 40 * k, 115 + 28 * k)
                ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
                ctx.set_dash([10, 8]); setc(ctx, TEAL, on * (0.9 - 0.2 * k)); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    # pin (vertical rod) with the switch arm
    pin_bot = pin_top + 310 if em < 0.5 else 1060
    rrect(ctx, PX - 15, pin_top, 30, pin_bot - pin_top, 8); fill_stroke(ctx, STEEL_D if em > 0.5 else STEEL, lw=4)
    arm_y = pin_top + 140
    ctx.rectangle(PX + 15, arm_y - 6, 255, 14); fill_stroke(ctx, INK2, lw=2)
    ctx.arc(PX + 260, arm_y - 8, 9, 0, 6.28); fill_stroke(ctx, MUSTARD, lw=2)
    # fixed contact + wire to the machine (right)
    ctx.rectangle(PX + 230, CONTACT_Y - 22, HX1 - PX - 230, 12); fill_stroke(ctx, INK2, lw=2)
    ctx.move_to(HX1, CONTACT_Y - 16); ctx.line_to(1040, CONTACT_Y - 16); setc(ctx, COPPER); ctx.set_line_width(5); ctx.stroke()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    s['_pin_top'] = pin_top; s['_arm_y'] = arm_y

def overlays(ctx, t, s):
    a = ease(clamp((s['turn'] - 0.5) / 0.5))
    if a <= 0: return
    # heat waves from the pill into the disc (beats 3-7)
    ha = s['heat'] * (1 - s['em']) * a * (1 if t < B(7) + 1 else 0.5)
    if ha > 0.05:
        for i in range(3):
            x = PILL[0] + 30 + i * 40
            wavy_arrow(ctx, x, PILL[1] - 4, x, disc_mid(s['up']) + 18, t, RED, ha * 0.8, amp=4, wl=18, lw=3, head=8)
    # the wait: heat leaves the disc sideways
    ca = bw(t, 7) * a
    if ca > 0:
        for sgn in (-1, 1):
            x0 = 470 + sgn * 170
            wavy_arrow(ctx, x0, DISC_Y - 20, x0 + sgn * 150, DISC_Y - 100, t, ORANGE, ca * s['dtemp'] + 0.2 * ca, amp=6, wl=26, lw=4, head=11)
    a2 = bw(t, 1) * a
    if a2 > 0:
        highlight(ctx, PILL[0] + PILL[2] / 2, PILL[1] + PILL[3] / 2, 110, 55, RED, a2, t)
        tag(ctx, "TINY HEATER", PILL[0] + PILL[2] / 2, PILL[1] + 135, RED, a2, 28)
    a3 = bw(t, 2) * a
    if a3 > 0:
        highlight(ctx, PILL[0] + PILL[2] / 2, PILL[1] + PILL[3] / 2, 110, 55, RED, a3, t)
        tag(ctx, "1 · CERAMIC HEATER", PILL[0] + PILL[2] / 2, PILL[1] + 135, RED, a3, 28)
    a4 = bw(t, 3) * a
    if a4 > 0:
        highlight(ctx, 470, DISC_Y + 25, 185, 50, MUSTARD, a4, t)
        tag(ctx, "2 · DISC · TWO METALS", 470, PILL[1] + 135, INK, a4, 28)
    a6 = bw(t, 5) * a
    if a6 > 0:
        highlight(ctx, PX, (HOOK_Y0 + HOOK_Y1) / 2, 70, 60, RED, a6, t)
        tag(ctx, "3 · PIN IN THE HOOK", 330, 690, RED, a6, 26)
        padlock(ctx, 690, 690, 1.2, True, RED, a6 * smooth_step(t, B(5) + 0.4))
    a7 = bw(t, 6) * a
    if a7 > 0:
        highlight(ctx, PX + 255, CONTACT_Y - 14, 55, 40, TEAL, a7, t)
        tag(ctx, "SWITCH CLOSED", 690, 990, TEAL, a7, 26)
        tag(ctx, "FILL · SPIN", 960, 800, TEAL, a7 * s['flow'], 24)
        fa = s['flow'] * a
        for i in range(5):
            u = (t * 0.9 + i / 5) % 1
            ctx.arc(lerp(HX1, 1040, u), CONTACT_Y - 16, 7, 0, 6.28); setc(ctx, MUSTARD, fa); ctx.fill_preserve()
            setc(ctx, INK, fa); ctx.set_line_width(2); ctx.stroke()
    a8 = bw(t, 7) * a
    if a8 > 0:
        tag(ctx, "HEATER OFF", PILL[0] + PILL[2] / 2, PILL[1] + 135, INK, a8, 26)
        tag(ctx, "DISC STILL HOT", 470, 990, ORANGE, a8 * (1 - smooth_step(t, B(8) - 0.2, 0.3)), 26)
    a9 = bw(t, 8) * a
    if a9 > 0:
        tag(ctx, "SNAP BACK", 470, 990, TEAL, a9 * smooth_step(t, B(8) + 0.35), 26)
        tag(ctx, "PIN OUT · UNLOCKED", 330, 690, TEAL, a9 * smooth_step(t, B(8) + 0.9), 26)
    a10 = bw(t, 9) * a
    if a10 > 0:
        tag(ctx, "NO POWER · DISC STILL HOT", 540, PILL[1] + 135, RED, a10, 24)
        padlock(ctx, 690, 690, 1.2, True, RED, a10)
    a11 = bw(t, 10) * a
    if a11 > 0:
        tag(ctx, "ELECTROMAGNET", PX, 1330, TEAL, a11, 28)
        tag(ctx, "CLICK", 700, 990, TEAL, a11 * s['em_on'], 30)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    s = state(t)
    front_view(ctx, t, s)
    section(ctx, t, s)
    overlays(ctx, t, s)

# ---------------------------------------------------------------- HUD (top zone)
def _panel(ctx, a, x=60, y=175, w=960, h=300):
    rrect(ctx, x, y, w, h, 18); setc(ctx, CREAM, 0.97 * a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def _cross(ctx, cx, cy, r, a):
    ctx.move_to(cx - r, cy - r); ctx.line_to(cx + r, cy + r); ctx.move_to(cx + r, cy - r); ctx.line_to(cx - r, cy + r)
    setc(ctx, RED, a); ctx.set_line_width(12); ctx.stroke()

def not_a_motor(ctx, t, a):
    _panel(ctx, a)
    gear(ctx, 290, 310, 75, 55, 10, 20, FILL3, lw=4, rot=t * 0.5)
    text_c(ctx, "MOTOR", 290, 440, 26, INK, True, 1.5, a)
    _cross(ctx, 290, 310, 70, a * smooth_step(t, B(1) + 1.4, 0.25))
    k = smooth_step(t, B(1) + 2.0, 0.3) * a
    rrect(ctx, 700, 280, 160, 60, 30); fill_stroke(ctx, HOT, lw=4, alpha=k)
    for i in range(3):
        wavy_arrow(ctx, 740 + i * 40, 272, 740 + i * 40, 205, t, RED, k, amp=4, wl=20, lw=3, head=8)
    text_c(ctx, "TINY HEATER", 780, 440, 26, RED, True, 1.5, k)

def clock_panel(ctx, t, a):
    _panel(ctx, a)
    cx, cy, r = 300, 325, 105
    ctx.arc(cx, cy, r, 0, 6.28); fill_stroke(ctx, PAPER, lw=5, alpha=a)
    p = clamp((t - B(7) - 0.3) / (B(8) - B(7) - 0.6))
    ctx.move_to(cx, cy); ctx.arc(cx, cy, r - 12, -math.pi / 2, -math.pi / 2 + p * 2 * math.pi); ctx.close_path()
    setc(ctx, MUSTARD, 0.6 * a); ctx.fill()
    an = -math.pi / 2 + p * 2 * math.pi
    ctx.move_to(cx, cy); ctx.line_to(cx + (r - 20) * math.cos(an), cy + (r - 20) * math.sin(an))
    setc(ctx, INK, a); ctx.set_line_width(7); ctx.stroke()
    text_c(ctx, "1–2 MIN", 700, 320, 64, INK, True, 2, a)
    text_c(ctx, "TO COOL DOWN", 700, 385, 30, ORANGE, True, 2, a)

def drum_check(ctx, t, a):
    _panel(ctx, a)
    lt = t - B(10)
    w = 6 * (1 - clamp((lt - 0.4) / 1.6))
    ang = 6 * min(lt, 0.4) + (lt > 0.4) * (6 * 0.8 * (1 - (1 - clamp((lt - 0.4) / 1.6)) ** 2))
    cx, cy = 290, 320
    ctx.arc(cx, cy, 100, 0, 6.28); fill_stroke(ctx, DRUM, lw=5, alpha=a)
    for i in range(6):
        an = ang + i * math.pi / 3
        ctx.arc(cx + 62 * math.cos(an), cy + 62 * math.sin(an), 12, 0, 6.28); setc(ctx, INK2, a); ctx.fill()
    k = smooth_step(t, B(10) + 2.1, 0.3) * a
    text_c(ctx, "DRUM STOPPED", 700, 300, 40, INK, True, 2, a)
    text_c(ctx, "OK · THEN CLICK", 700, 370, 40, TEAL, True, 2, k)

def draw_hud(ctx, t, E):
    a = win(t, B(1) + 1.0, B(2), 0.3)
    if a > 0: not_a_motor(ctx, t, a)
    a = win(t, B(7) + 0.2, B(8) + 0.1, 0.3)
    if a > 0: clock_panel(ctx, t, a)
    a = win(t, B(10) + 0.2, B(11), 0.3)
    if a > 0: drum_check(ctx, t, a)

SFX = [(0.3, 'pop'), (1.0, 'pop'), (2.6, 'click'), (B(1) + 1.4, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'),
       (B(5) + 0.25, 'click'), (B(5) + 0.4, 'pop'), (B(6) + 0.3, 'pop'), (B(7) + 0.3, 'pop'),
       (B(8) + 0.35, 'click'), (B(10) + 2.1, 'pop'), (B(10) + 3.2, 'click'), (B(11) + 0.9, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def _dome(ctx, x0, x1, y, h, warm, a, lw=12):
    cx = (x0 + x1) / 2; cy = y + 2 * h
    def p(off):
        ctx.move_to(x0, y + off)
        ctx.curve_to(x0 + (cx - x0) * 2 / 3, y + off + (cy - y) * 2 / 3, x1 + (cx - x1) * 2 / 3, y + off + (cy - y) * 2 / 3, x1, y + off)
    p(9); setc(ctx, STEEL_D, a); ctx.set_line_width(lw); ctx.stroke()
    p(-3); setc(ctx, lerpc(BRASS, ORANGE, warm), a); ctx.set_line_width(lw); ctx.stroke()

def card_bimetal(ctx, t, lt, a):
    snap = smooth_step(lt, 3.6, 0.12)
    card_frame(ctx, "TWO METALS, ONE DISC", a, "WARM: SNAP!" if snap > 0.5 else "HEATING…", RED)
    warm = clamp((lt - 0.6) / 3.0)
    # before the snap the dome strains a little, then flips
    h = lerp(lerp(55, 42, warm), -55, snap)
    _dome(ctx, 260, 820, 410, h, warm, a, lw=16)
    for xx in (260, 820):
        rrect(ctx, xx - 30, 412, 60, 40, 6); fill_stroke(ctx, FILL3, lw=3, alpha=a)
    tag(ctx, "EXPANDS MORE", 540, 285, ORANGE, a, 24)
    tag(ctx, "EXPANDS LESS", 540, 530, STEEL_D, a, 24)
    straight_arrow(ctx, 540, 305, 540, 410 + h - 14, ORANGE, a * 0.8, lw=4, head=9)
    straight_arrow(ctx, 540, 508, 540, 410 + h + 22, STEEL_D, a * 0.8, lw=4, head=9)
    for i in range(3):
        x = 330 + i * 40
        wavy_arrow(ctx, x, 540, x, 470, lt, RED, a * warm, amp=4, wl=18, lw=3, head=8)

def card_powercut(ctx, t, lt, a):
    card_frame(ctx, "POWER CUT MID-SPIN", a, "DOOR STAYS LOCKED", RED)
    # unplugged
    p = smooth_step(lt, 0.3, 0.4)
    ctx.move_to(130, 400); ctx.line_to(200 - 30 * p, 400); setc(ctx, INK, a); ctx.set_line_width(8); ctx.stroke()
    rrect(ctx, 200 - 30 * p, 380, 40, 40, 6); fill_stroke(ctx, INK2, lw=3, alpha=a)
    rrect(ctx, 260, 370, 30, 60, 4); fill_stroke(ctx, FILL3, lw=3, alpha=a)
    text_c(ctx, "NO POWER", 210, 480, 22, RED, True, 1, a)
    # drum slowing down (angle grows ever more slowly)
    u = clamp(lt / 5.5); ang = 9 * (1 - (1 - u) ** 2)
    cx, cy = 540, 400
    ctx.arc(cx, cy, 95, 0, 6.28); fill_stroke(ctx, DRUM, lw=4, alpha=a)
    for i in range(6):
        an = ang * 2 + i * math.pi / 3
        ctx.arc(cx + 58 * math.cos(an), cy + 58 * math.sin(an), 11, 0, 6.28); setc(ctx, INK2, a); ctx.fill()
    text_c(ctx, "SLOWING…", cx, 525, 22, INK, True, 1, a)
    # padlock still closed + warm disc
    padlock(ctx, 820, 410, 2.0, True, RED, a)
    _dome(ctx, 740, 900, 480, -12, 0.8, a, lw=7)
    text_c(ctx, "STILL HOT", 820, 535, 22, ORANGE, True, 1, a)

CARDS = {'bimetal': card_bimetal, 'powercut': card_powercut}
