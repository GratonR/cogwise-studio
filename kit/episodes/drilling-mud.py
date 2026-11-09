"""Cogwise episode: Drillers read mud to see 3 km down.
One idea: drilling mud is a conveyor belt from the bottom of the hole. Pumped DOWN inside the drill
pipe, out through the bit, it climbs back UP the annulus (gap between pipe and rock) carrying the chips
the bit just cut, and gas from the rock. At the surface, people read it: chips (shale shaker, microscope,
UV fluorescence = oil) and gas (gas trap + detector, C1..C5). Gas jump + glowing chips = an oil show.

CUT-AWAY SIDE VIEW. Screen coordinates: y grows DOWN.
Mud loop (arrows follow it): pump (left, surface) -> hose -> top drive -> DOWN inside the pipe (blue, clean)
-> out of the bit jets at the bottom -> UP both sides of the annulus (brown, with chips + gas bubbles)
-> bell nipple at the surface -> flowline to the RIGHT -> gas trap (on the flowline) -> shaker screen:
chips walk off the right end into the cuttings box, mud falls DOWN through the screen into the pit.
Oil-bearing layer = the bottom stratum, which the bit reaches at the oil show.
"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="drilling-mud",
    title="Drillers read mud to see 3 km down 🛢️",
    description=("Nobody can see three kilometers underground. The drilling mud carries the bottom of the hole "
                 "back up, and people at the surface read it.\n\n#Shorts #howthingswork #drilling #oilandgas #cogwise"),
    hashtags=["Shorts", "howthingswork", "drilling", "oilandgas", "engineering", "cogwise"],
    sources=[
        "https://www.drillingmanual.com/functions-of-drilling-fluids/",
        "https://www.rigzone.com/insights/how-it-works-3/how-is-mud-logging-conducted-during-drilling-operations-427/",
        "https://spec2000.net/log-data-acquisition/logging-mud-logging-and-mud-gas-logging-mwd.htm",
        "https://ogj.com/home/article/17230128/gasdetection-technology-improves-reservoir-interpretation",
    ],
)

BEATS = [
    dict(dur=5.6, title="3 KM DOWN", caption="Nobody can see three kilometers underground. So drillers read what the mud brings up."),
    dict(dur=5.4, title="THE SECRET", caption="The secret: this mud is a conveyor belt from the bottom of the hole."),
    dict(dur=5.2, title="DOWN THE PIPE", caption="Pumps push it down inside the drill pipe and out through the bit's jets."),
    dict(dur=6.0, title="UP THE GAP", caption="Then it climbs back up around the pipe, carrying the chips the bit just cut."),
    dict(dur=5.6, title="THE LONG RIDE", caption="From three kilometers, nearly two miles down, that trip up can take a whole hour."),
    dict(dur=6.0, title="1 · SHAKER", caption="At the top, a shaking screen catches the chips, and a geologist names the rock under a microscope."),
    dict(dur=4.4, title=None, caption="Under ultraviolet light, rock that holds oil starts to glow.", card='uv'),
    dict(dur=5.6, title="2 · GAS TRAP", caption="Gas rides up too. A spinning beater in a gas trap shakes it loose."),
    dict(dur=4.6, title=None, caption="A detector counts it, methane to pentane, every minute or two.", card='gas'),
    dict(dur=5.6, title="OIL SHOW", caption="A sudden jump in gas, plus glowing chips? Drillers call that an oil show."),
    dict(dur=5.4, title="RECAP", caption="Mud goes down, rock and gas come up. The hole reports on itself, meter by meter."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

# ---------------------------------------------------------------- geometry
GROUND = 560                       # surface line
HL, HR = 470, 610                  # hole walls
PL, PR = 522, 558                  # drill pipe walls
PC = (PL + PR) / 2                 # pipe centre x = 540
BIT_Y = 1400                       # top of the bit
BOT = 1452                         # bottom of the hole
TOPD = (480, 330, 120, 50)         # top drive box
PUMP = (110, 440, 170, 90)         # mud pump x 110..280 y 440..530
BELL = (452, 500, 176, 60)         # bell nipple x 452..628, y 500..560
FLOW_Y = 520                       # flowline height
TRAP = (668, 488, 70, 64)          # gas trap box x 668..738
SCR = (760, 470, 190)              # shaker screen: x0, y at x0, length (slight uphill to the right)
PIT = (752, 560, 200, 70)          # mud pit under the shaker (sunk into the ground)
DET = (800, 316, 150, 70)          # gas detector box
STRATA = [(560, 760, hexc('#e8d9b8')), (760, 930, hexc('#d9c7a3')), (930, 1110, hexc('#e4cfae')),
          (1110, 1290, hexc('#cdb994')), (1290, 1470, hexc('#c9a95a'))]   # last = oil-bearing sandstone

MUD_DN = hexc('#5aa7c9'); MUD_UP = hexc('#8a5a32'); CHIP = hexc('#6d6a66'); STEEL = hexc('#c9ced3')
GLOW = hexc('#ffe14a'); GAS = hexc('#cfe9e6')

def shaker_y(x):                   # screen line: rises 3° to the right (chips "walk" uphill, mud drains)
    x0, y0, L = SCR
    return y0 - (x - x0) * math.tan(math.radians(3))

# ---------------------------------------------------------------- state
def state(t):
    s = {}
    s['flow'] = t
    s['tag_mud'] = win(t, 0.3, B(1) + 0.3, 0.3)
    s['h_up'] = max(bw(t, 1), bw(t, 3))
    s['h_down'] = bw(t, 2)
    s['l_pipe'] = bw(t, 2, 4)
    s['l_gap'] = bw(t, 3, 5)
    s['depth'] = max(win(t, 0.2, B(1), 0.3), bw(t, 4))
    s['h_shaker'] = bw(t, 5); s['l_shaker'] = bw(t, 5, 7)
    s['scope'] = bw(t, 5, 7)
    s['h_trap'] = bw(t, 7); s['l_trap'] = bw(t, 7, 9)
    s['det'] = clamp(ease((t - B(7)) / 0.6))
    s['gasline'] = s['det']
    s['show'] = clamp(ease((t - B(9)) / 0.8)) * (1 - clamp((t - B(10) - 0.3) / 0.6) * 0.0)
    s['l_show'] = bw(t, 9)
    s['bubbles'] = 0.35 + 0.65 * max(bw(t, 7, 9), s['show'])
    s['recap'] = bw(t, 10)
    s['bitdepth'] = BIT_Y + 18 * clamp((t - B(8)) / (B(9) + 0.6 - B(8)))   # bit cuts into the oil layer
    return s

# ---------------------------------------------------------------- helpers
def chip(ctx, x, y, r, rot, col=CHIP, a=1.0, glow=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.move_to(-r, -r * 0.4); ctx.line_to(-r * 0.2, -r * 0.8); ctx.line_to(r, -r * 0.3)
    ctx.line_to(r * 0.6, r * 0.7); ctx.line_to(-r * 0.7, r * 0.6); ctx.close_path(); ctx.restore()
    if glow > 0:
        setc(ctx, lerpc(col, GLOW, glow), a); ctx.fill_preserve()
    else:
        setc(ctx, col, a); ctx.fill_preserve()
    setc(ctx, INK, 0.55 * a); ctx.set_line_width(1.5); ctx.stroke()

def bubble(ctx, x, y, r, a):
    ctx.arc(x, y, r, 0, 2 * math.pi); setc(ctx, GAS, 0.85 * a); ctx.fill_preserve()
    setc(ctx, INK2, 0.7 * a); ctx.set_line_width(2); ctx.stroke()

def chevron(ctx, x, y, ang, col, a=1.0, s=12):
    ctx.save(); ctx.translate(x, y); ctx.rotate(math.radians(ang))
    ctx.move_to(-s * 0.7, -s); ctx.line_to(s * 0.5, 0); ctx.line_to(-s * 0.7, s)
    setc(ctx, col, a); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke(); ctx.restore()

# ---------------------------------------------------------------- parts
def draw_ground(ctx, t, s):
    for (y0, y1, col) in STRATA:
        ctx.rectangle(140, y0, 800, y1 - y0); setc(ctx, col); ctx.fill()
        ctx.move_to(140, y1); ctx.line_to(940, y1); setc(ctx, INK2, 0.35); ctx.set_line_width(2); ctx.stroke()
    rnd = random.Random(3)                       # rock texture
    for i in range(140):
        x = rnd.uniform(150, 930); y = rnd.uniform(GROUND + 10, 1460)
        if HL - 12 < x < HR + 12: continue
        ctx.arc(x, y, rnd.uniform(1.5, 3.5), 0, 2 * math.pi); setc(ctx, INK2, 0.3); ctx.fill()
    # oil in the bottom layer: dark specks between grains
    for i in range(40):
        x = rnd.uniform(150, 930); y = rnd.uniform(1300, 1462)
        if HL - 12 < x < HR + 12: continue
        ctx.arc(x, y, rnd.uniform(3, 6), 0, 2 * math.pi); setc(ctx, hexc('#3b2a12'), 0.55); ctx.fill()
    ctx.rectangle(140, GROUND, 800, 910); setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    ctx.move_to(60, GROUND); ctx.line_to(1020, GROUND); setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()

def draw_hole(ctx, t, s):
    # bore (annulus filled with returning mud)
    ctx.rectangle(HL, GROUND, HR - HL, BOT - GROUND); setc(ctx, MUD_UP, 0.9); ctx.fill()
    ctx.move_to(HL, GROUND); ctx.line_to(HL, BOT); ctx.line_to(HR, BOT); ctx.line_to(HR, GROUND)
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    bd = s['bitdepth']
    # chips + gas going UP both annulus sides (y decreases with time)
    rnd = random.Random(7)
    for side in (0, 1):
        x0, x1 = (HL + 6, PL - 6) if side == 0 else (PR + 6, HR - 6)
        for i in range(26):
            ph = (rnd.random() + s['flow'] * 0.16) % 1
            y = BOT - 30 - ph * (BOT - 30 - BELL[1] - 10)
            x = lerp(x0, x1, rnd.random())
            g = s['show'] * (1 if (i % 4 == 0 and ph < 0.85) else 0)
            chip(ctx, x, y, rnd.uniform(5, 8), rnd.random() * 6 + t, a=1.0, glow=g)
        nb = int(6 + 14 * s['bubbles'])
        for i in range(nb):
            ph = (rnd.random() + s['flow'] * 0.2) % 1
            y = BOT - 30 - ph * (BOT - 40 - GROUND)
            x = lerp(x0 + 4, x1 - 4, rnd.random())
            bubble(ctx, x, y, 4 + 2 * rnd.random(), s['bubbles'])
    # up chevrons in the annulus
    for y in (1250, 1000, 750):
        chevron(ctx, (HL + PL) / 2, y, -90, hexc('#f3e3c6'), 0.9, 10)
        chevron(ctx, (PR + HR) / 2, y, -90, hexc('#f3e3c6'), 0.9, 10)
    # drill pipe (cut open: clean mud going DOWN inside)
    ctx.rectangle(PL, TOPD[1] + TOPD[3], PR - PL, bd - TOPD[1] - TOPD[3]); fill_stroke(ctx, STEEL, lw=4)
    ctx.rectangle(PL + 7, TOPD[1] + TOPD[3], PR - PL - 14, bd - TOPD[1] - TOPD[3]); setc(ctx, MUD_DN); ctx.fill()
    for i in range(14):
        ph = (i / 14 + s['flow'] * 0.22) % 1
        y = TOPD[1] + TOPD[3] + ph * (bd - TOPD[1] - TOPD[3])
        ctx.arc(PC, y, 5, 0, 2 * math.pi); setc(ctx, WHITE, 0.8); ctx.fill()
    for y in (700, 950, 1200):
        chevron(ctx, PC, y, 90, WHITE, 0.95, 9)
    # bit (tri-cone) + jets
    ctx.move_to(PL - 6, bd); ctx.line_to(PR + 6, bd); ctx.line_to(HR - 10, bd + 22); ctx.line_to(HR - 18, BOT - 4)
    ctx.line_to(HL + 18, BOT - 4); ctx.line_to(HL + 10, bd + 22); ctx.close_path(); fill_stroke(ctx, hexc('#7d7f86'), lw=4)
    for k in range(5):
        x = HL + 26 + k * (HR - HL - 52) / 4
        for m in range(3):
            ctx.move_to(x - 6 + m * 6, BOT - 4); ctx.line_to(x - 3 + m * 6, BOT - 12)
            setc(ctx, INK, 0.7); ctx.set_line_width(2); ctx.stroke()
    # jets: short blue spurts down out of the bit, turning to go up the sides
    ph = (t * 3) % 1
    for d in (-1, 1):
        ctx.move_to(PC + d * 18, bd + 30); ctx.curve_to(PC + d * 30, BOT + 2, PC + d * 52, BOT - 2, PC + d * 60, bd + 6)
        setc(ctx, MUD_DN, 0.8); ctx.set_line_width(5); ctx.set_dash([10, 8], -ph * 18); ctx.stroke(); ctx.set_dash([])

def draw_surface(ctx, t, s):
    # bell nipple around the pipe at the surface
    x, y, w, h = BELL
    rrect(ctx, x, y, w, h, 6); fill_stroke(ctx, hexc('#b8bec4'), lw=5)
    rrect(ctx, HL, y + 6, HR - HL, h - 6, 3); setc(ctx, MUD_UP); ctx.fill()
    ctx.rectangle(PL, y - 4, PR - PL, h + 4); fill_stroke(ctx, STEEL, lw=3)
    ctx.rectangle(PL + 7, y - 4, PR - PL - 14, h + 4); setc(ctx, MUD_DN); ctx.fill()
    # pipe above ground up to the top drive
    tx, ty, tw, th = TOPD
    rrect(ctx, tx, ty, tw, th, 8); fill_stroke(ctx, MUSTARD, lw=5)
    text_c(ctx, "TOP DRIVE", tx + tw / 2, ty + 33, 18, INK, True, 1)
    # mud pump + hose to the top drive
    px, py, pw, ph = PUMP
    rrect(ctx, px, py, pw, ph, 10); fill_stroke(ctx, hexc('#2f7d86'), lw=5)
    for k in range(3):
        ctx.arc(px + 40 + k * 45, py + 45, 14, 0, 2 * math.pi); fill_stroke(ctx, STEEL, lw=3)
    cr = s['flow'] * 6
    for k in range(3):
        ctx.move_to(px + 40 + k * 45, py + 45)
        ctx.line_to(px + 40 + k * 45 + 11 * math.cos(cr + k * 2.1), py + 45 + 11 * math.sin(cr + k * 2.1))
        setc(ctx, INK); ctx.set_line_width(3); ctx.stroke()
    rrect(ctx, px + 10, py + ph, 30, GROUND - py - ph, 2); setc(ctx, INK2); ctx.fill()
    rrect(ctx, px + pw - 40, py + ph, 30, GROUND - py - ph, 2); setc(ctx, INK2); ctx.fill()
    hose = [(px + pw, py + 30), (360, py + 30), (360, ty + 25), (tx, ty + 25)]
    for lw, col in ((20, INK), (12, MUD_DN)):
        ctx.move_to(*hose[0])
        for p in hose[1:]: ctx.line_to(*p)
        setc(ctx, col); ctx.set_line_width(lw); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    chevron(ctx, 320, py + 30, 0, WHITE, 1, 8); chevron(ctx, 360, 420, -90, WHITE, 1, 8); chevron(ctx, 430, ty + 25, 0, WHITE, 1, 8)
    # flowline: bell nipple -> gas trap -> shaker (slopes slightly DOWN to the right, y grows)
    fl = [(x + w, FLOW_Y + 10), (TRAP[0], FLOW_Y + 14), (TRAP[0] + TRAP[2], FLOW_Y + 16), (SCR[0] + 8, shaker_y(SCR[0] + 8) - 6)]
    for lw, col in ((24, INK), (16, MUD_UP)):
        ctx.move_to(*fl[0])
        for p in fl[1:]: ctx.line_to(*p)
        setc(ctx, col); ctx.set_line_width(lw); ctx.stroke()
    chevron(ctx, 648, FLOW_Y + 12, 0, hexc('#f3e3c6'), 1, 8)
    # gas trap with spinning beater
    gx, gy, gw, gh = TRAP
    rrect(ctx, gx, gy, gw, gh, 8); fill_stroke(ctx, hexc('#e3ddd0'), lw=4)
    ctx.rectangle(gx + 6, gy + gh * 0.45, gw - 12, gh * 0.5); setc(ctx, MUD_UP, 0.85); ctx.fill()
    ctx.move_to(gx + gw / 2, gy - 18); ctx.line_to(gx + gw / 2, gy + gh * 0.7); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    sp = s['flow'] * 9
    for k in range(2):
        ww = 22 * math.cos(sp + k * math.pi / 2)
        ctx.move_to(gx + gw / 2 - ww, gy + gh * 0.7); ctx.line_to(gx + gw / 2 + ww, gy + gh * 0.7)
        setc(ctx, RED); ctx.set_line_width(6); ctx.stroke()
    rrect(ctx, gx + gw / 2 - 14, gy - 34, 28, 18, 4); fill_stroke(ctx, hexc('#5f6a73'), lw=3)   # motor
    # gas line from the trap UP to the detector
    a = s['gasline']
    if a > 0:
        dx, dy, dw, dh = DET
        ln = [(gx + gw - 10, gy + 6), (gx + gw - 10, dy + dh / 2), (dx, dy + dh / 2)]
        ctx.move_to(*ln[0])
        for p in ln[1:]: ctx.line_to(*p)
        setc(ctx, INK2, a); ctx.set_line_width(5); ctx.stroke()
        for i in range(4):
            u = (i / 4 + t * 0.6) % 1
            if u < 0.5: p = (ln[0][0], lerp(ln[0][1], ln[1][1], u / 0.5))
            else: p = (lerp(ln[1][0], ln[2][0], (u - 0.5) / 0.5), ln[1][1])
            bubble(ctx, p[0], p[1], 6, a)
        rrect(ctx, dx, dy, dw, dh, 8); fill_stroke(ctx, hexc('#2f3540'), lw=4, alpha=a)
        rrect(ctx, dx + 10, dy + 10, dw - 20, dh - 20, 4); setc(ctx, hexc('#cfe9b8'), a); ctx.fill()
        # live trace: low and flat, jumps at the oil show
        ctx.move_to(dx + 14, dy + dh - 16)
        for k in range(30):
            xx = dx + 14 + k * (dw - 28) / 29
            hgt = 6 + 3 * math.sin(k * 1.7 + t * 4)
            if k > 18: hgt += 30 * s['show']
            ctx.line_to(xx, dy + dh - 16 - hgt)
        setc(ctx, hexc('#1d5a2a'), a); ctx.set_line_width(3); ctx.stroke()
    # mud pit (sunk into the ground under the shaker)
    mx, my, mw, mh = PIT
    ctx.rectangle(mx, my, mw, mh); setc(ctx, hexc('#efe4cd')); ctx.fill()
    ctx.rectangle(mx + 6, my + 18, mw - 12, mh - 24); setc(ctx, MUD_UP, 0.85); ctx.fill()
    ctx.move_to(mx, my); ctx.line_to(mx, my + mh); ctx.line_to(mx + mw, my + mh); ctx.line_to(mx + mw, my)
    setc(ctx, INK); ctx.set_line_width(5); ctx.stroke()
    # shaker: legs, vibrating screen, mud dripping DOWN through it, chips walking off the right end
    x0, y0, L = SCR
    vib = 3 * math.sin(t * 50)
    for lx in (x0 + 20, x0 + L - 20):
        ctx.move_to(lx, shaker_y(lx) + 10); ctx.line_to(lx, my); setc(ctx, INK2); ctx.set_line_width(8); ctx.stroke()
    ctx.save(); ctx.translate(0, vib)
    ctx.move_to(x0, shaker_y(x0)); ctx.line_to(x0 + L, shaker_y(x0 + L))
    setc(ctx, INK); ctx.set_line_width(10); ctx.stroke()
    ctx.move_to(x0, shaker_y(x0)); ctx.line_to(x0 + L, shaker_y(x0 + L))
    setc(ctx, STEEL); ctx.set_line_width(5); ctx.set_dash([4, 4]); ctx.stroke(); ctx.set_dash([])
    rnd = random.Random(11)
    for i in range(9):
        u = (rnd.random() + t * 0.35) % 1
        xx = x0 + 10 + u * (L - 10)
        chip(ctx, xx, shaker_y(xx) - 9, 7, i + t, glow=s['show'] * (1 if i % 3 == 0 else 0))
    ctx.restore()
    for i in range(6):                     # mud drips DOWN through the screen (y grows)
        ph = (i / 6 + t * 1.3) % 1
        xx = x0 + 20 + i * 28
        ctx.arc(xx, shaker_y(xx) + 10 + ph * (my + 18 - shaker_y(xx) - 10), 4, 0, 2 * math.pi)
        setc(ctx, MUD_UP); ctx.fill()
    # chips fall off the right end into the cuttings box
    cbx = x0 + L + 4
    rrect(ctx, cbx, 500, 56, 60, 4); fill_stroke(ctx, hexc('#d6cbb4'), lw=4)
    for i in range(3):
        ph = (i / 3 + t * 0.9) % 1
        chip(ctx, cbx + 14 + i * 10, shaker_y(x0 + L) + ph * (510 - shaker_y(x0 + L)), 6, t + i)
    # microscope on top of the detector side (the geologist's bench)
    a = s['scope']
    if a > 0:
        mx2, my2 = 982, 462
        rrect(ctx, mx2 - 26, my2 + 26, 52, 12, 3); fill_stroke(ctx, INK2, lw=3, alpha=a)
        ctx.move_to(mx2 + 18, my2 + 26); ctx.curve_to(mx2 + 34, my2, mx2 + 30, my2 - 30, mx2 + 10, my2 - 40)
        setc(ctx, INK, a); ctx.set_line_width(8); ctx.stroke()
        ctx.save(); ctx.translate(mx2 - 2, my2 - 30); ctx.rotate(math.radians(-25))
        rrect(ctx, -10, -36, 20, 56, 5); fill_stroke(ctx, STEEL, lw=3, alpha=a); ctx.restore()

def draw_scene(ctx, t, s):
    draw_ground(ctx, t, s)
    draw_hole(ctx, t, s)
    draw_surface(ctx, t, s)
    # depth ruler (right)
    a = s['depth']
    if a > 0:
        ctx.move_to(975, GROUND); ctx.line_to(975, BOT); setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()
        for y in (GROUND, BOT):
            ctx.move_to(960, y); ctx.line_to(990, y); setc(ctx, INK, a); ctx.stroke()
        ctx.save(); ctx.translate(1010, (GROUND + BOT) / 2); ctx.rotate(-math.pi / 2)
        text_c(ctx, "3 km · 1.9 mi", 0, 10, 30, RED, True, 1, a); ctx.restore()
    # highlights
    highlight(ctx, (HL + PL) / 2, 1000, 40, 300, MUSTARD, s['h_up'], t)
    highlight(ctx, (PR + HR) / 2, 1000, 40, 300, MUSTARD, s['h_up'], t)
    highlight(ctx, PC, 950, 30, 360, TEAL, s['h_down'], t)
    highlight(ctx, SCR[0] + SCR[2] / 2, 470, 120, 50, RED, s['h_shaker'], t)
    highlight(ctx, TRAP[0] + TRAP[2] / 2, TRAP[1] + 20, 60, 60, RED, s['h_trap'], t)
    # tags
    tag(ctx, "ROCK CHIPS", 790, 1250, MUD_UP, s['tag_mud'], 24)
    tag(ctx, "DOWN THE PIPE", 300, 820, TEAL, s['l_pipe'], 26)
    tag(ctx, "UP THE GAP + CHIPS", 760, 1000, MUD_UP, s['l_gap'], 26)
    tag(ctx, "1 · SHAKER", 850, 640, RED, s['l_shaker'])
    tag(ctx, "2 · GAS TRAP", 640, 440, RED, s['l_trap'])
    tag(ctx, "OIL LAYER", 290, 1380, hexc('#6b4d10'), s['l_show'])
    tag(ctx, "GAS DETECTOR", 875, 290, TEAL, s['det'] * (1 - max(s['recap'], s['l_show'])), 22)
    tag(ctx, "MUD GOES DOWN", 300, 820, TEAL, s['recap'], 30)
    tag(ctx, "ROCK + GAS COME UP", 760, 1000, MUD_UP, s['recap'], 30)

def draw_set(ctx):
    pass

def draw(ctx, t, E):
    draw_scene(ctx, t, state(t))

# camera: open tight on the annulus near the bottom (chips riding up), then pull back to the whole well
CAMKEYS = [(0, 680, 1180, 1.9), (2.0, 540, 840, 0.98), (B(5), 780, 560, 1.55), (B(6), 540, 840, 0.98),
           (B(7), 700, 470, 1.6), (B(9), 540, 840, 0.98)]
def CAM(t): return cam_track(CAMKEYS, t, move=1.2)

def draw_hud(ctx, t, E):
    a = bw(t, 4)
    if a > 0: hud(ctx, "TRIP UP", "≈ 1 HOUR", "3 km · 1.9 mi of mud", a, RED, x=40, y=196, w=520)
    a = bw(t, 9)
    if a > 0: hud(ctx, "GAS", "JUMPS", "+ glowing chips", a, RED, x=40, y=196, w=520)

SFX = [(0.3, 'pop'), (B(2) + 0.3, 'pop'), (B(3) + 0.3, 'pop'), (B(5) + 0.3, 'pop'),
       (B(7) + 0.3, 'pop'), (B(9) + 0.3, 'pop'), (B(10) + 0.3, 'pop'), (B(10) + 0.6, 'pop')]
HUM = []

# ---------------------------------------------------------------- cards
def card_uv(ctx, t, lt, a):
    card_frame(ctx, "CHIPS UNDER UV LIGHT", a, "OIL IN THE ROCK = IT GLOWS", MUSTARD)
    ctx.rectangle(130, 260, 820, 270); setc(ctx, hexc('#1c1830'), a); ctx.fill()
    # UV lamp at the top
    rrect(ctx, 420, 262, 240, 22, 6); fill_stroke(ctx, hexc('#8c6be0'), lw=3, alpha=a)
    g = cairo.LinearGradient(0, 284, 0, 520)
    g.add_color_stop_rgba(0, 0.55, 0.42, 0.88, 0.35 * a); g.add_color_stop_rgba(1, 0.55, 0.42, 0.88, 0)
    ctx.set_source(g); ctx.move_to(420, 284); ctx.line_to(660, 284); ctx.line_to(860, 520); ctx.line_to(220, 520)
    ctx.close_path(); ctx.fill()
    rnd = random.Random(21)
    k = clamp((lt - 0.8) / 1.0)
    for i in range(16):
        x = 220 + (i % 8) * 90 + rnd.uniform(-15, 15); y = 400 + (i // 8) * 70 + rnd.uniform(-10, 10)
        oily = i in (5, 11)
        chip(ctx, x, y, 22, rnd.random() * 6, col=hexc('#77736e'), a=a, glow=(k if oily else 0))
        if oily and k > 0:
            ctx.arc(x, y, 40, 0, 2 * math.pi); setc(ctx, GLOW, 0.25 * k * a); ctx.fill()
    text_c(ctx, "PLAIN ROCK: DARK", 330, 520, 22, WHITE, True, 1, a * 0.9)
    text_c(ctx, "OIL: GLOWS YELLOW", 760, 520, 22, GLOW, True, 1, a * k)

def card_gas(ctx, t, lt, a):
    card_frame(ctx, "GAS DETECTOR, EVERY 1–2 MIN", a, "METHANE TO PENTANE · C1 TO C5", TEAL)
    ctx.rectangle(150, 270, 780, 240); setc(ctx, hexc('#fbfbf2'), a); ctx.fill()
    for i in range(1, 12):
        x = 150 + i * 65
        ctx.move_to(x, 270); ctx.line_to(x, 510); setc(ctx, hexc('#9fd1a8'), 0.6 * a); ctx.set_line_width(1); ctx.stroke()
    for j in range(1, 6):
        y = 270 + j * 40
        ctx.move_to(150, y); ctx.line_to(930, y); setc(ctx, hexc('#9fd1a8'), 0.6 * a); ctx.set_line_width(1); ctx.stroke()
    # 5 peaks, lightest gas first (methane biggest), drawn left -> right over time
    peaks = [(250, 190, "C1"), (390, 120, "C2"), (520, 80, "C3"), (650, 55, "C4"), (790, 35, "C5")]
    prog = clamp(lt / 3.0)
    ctx.move_to(160, 500)
    xmax = 160 + prog * 760
    xx = 160
    while xx < xmax:
        y = 500
        for (px, h, _) in peaks:
            y -= h * math.exp(-((xx - px) / 18) ** 2)
        ctx.line_to(xx, y); xx += 4
    setc(ctx, hexc('#1d5a2a'), a); ctx.set_line_width(4); ctx.stroke()
    for (px, h, lab) in peaks:
        if xmax > px + 20:
            text_c(ctx, lab, px, 500 - h - 14, 24, INK, True, 1, a)

CARDS = {'uv': card_uv, 'gas': card_gas}
