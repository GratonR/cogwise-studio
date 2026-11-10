"""Cogwise episode: How does a lock know your key?  (pin tumbler lock)"""
import math, random, cairo
from cogwise.style import *

META = dict(
    slug="lock",
    title="How does a lock know it's YOUR key? 🔑",
    description=("Tiny spring-loaded pins and one invisible line: the pin tumbler lock in your front door, explained.\n\n"
                 "#Shorts #howthingswork #lock #key #engineering #cogwise"),
    hashtags=["Shorts", "howthingswork", "lock", "key", "engineering", "science", "cogwise"],
    sources=[
        "https://en.wikipedia.org/wiki/Pin_tumbler_lock",
        "https://www.britannica.com/technology/lock-security",
        "https://www.britannica.com/biography/Linus-Yale",
        "https://theengineeringmindset.com/how-padlocks-work/",
        "https://lockwiki.com/index.php/Pin-tumbler",
    ],
)

BEATS = [
    dict(dur=5.0, title="HOW DOES A LOCK KNOW YOUR KEY?", caption="How does a door lock know this key is yours, and not your neighbor's?"),
    dict(dur=5.0, title="TINY HIDDEN PINS", caption="The secret: tiny spring-loaded pins stop the lock from turning."),
    dict(dur=5.5, title=None, caption="It all happens on one invisible line, between a turning part and a fixed part.", card='shear'),
    dict(dur=5.0, title="1 · THE PLUG", caption="The plug is the cylinder your key turns, inside a fixed shell."),
    dict(dur=5.5, title="2 · THE PIN STACKS", caption="Each hole holds a stack: a key pin, a driver pin, and a spring."),
    dict(dur=5.5, title="3 · THE SPRINGS", caption="With no key, springs push the drivers across the line. Jammed!"),
    dict(dur=5.5, title="4 · THE KEY", caption="Your key's bumps and valleys lift each stack to a different height."),
    dict(dur=5.0, title=None, caption="The right key puts every gap exactly on the line, all at once.", card='cuts'),
    dict(dur=5.0, title="CLICK! IT TURNS", caption="Nothing crosses the line, so the plug turns and pulls back the bolt."),
    dict(dur=5.0, title=None, caption="Wrong key? One pin too high or too low, and nothing moves.", card='wrong'),
    dict(dur=5.5, title=None, caption="Surprise: ancient Egyptians used wooden pin locks about four thousand years ago!", card='egypt'),
    dict(dur=5.0, title="SHRUNK BY LINUS YALE", caption="Linus Yale Junior shrank it to pocket size in the 1860s."),
    dict(dur=5.0, title="THOUSANDS OF KEYS", caption="Five or six pins with several heights give thousands of different keys."),
    dict(dur=5.0, title="A KEY = A HEIGHT CODE", caption="So your key is a code: a row of heights only your lock understands."),
    dict(dur=5.5, title="PRO TIP", caption="Tech tip: stiff lock? Use graphite powder, not oil, which traps dust."),
]

ST = [0.0]
for _b in BEATS: ST.append(ST[-1] + _b['dur'])
def B(i): return ST[i]
def bw(t, i, j=None, f=0.35):            # window from beat i start to beat j start
    return win(t, B(i) + 0.1, B(j if j is not None else i + 1), f)

ANCHOR = (560, 1480)

# ---------------------------------------------------------------- geometry
SL = 880                     # shear line
FACE = 230                   # lock face (x of plug front)
SHELL = (200, 640, 780, 520) # x, y, w, h  -> 200..980, 640..1160
PLUG = (FACE, SL, 720, 190)  # 230..950, 880..1070
KW_TOP, KW_BOT = 905, 1045   # keyway
PX = [360, 480, 600, 720, 840]
LK = [55, 35, 70, 45, 60]    # key pin lengths
LD = 64                      # driver pin length
REST = 962                   # key-pin bottom without key
SPR_TOP = 672
KEYLEN = 700
BRASS = hexc('#e9b949'); BRASS_L = hexc('#f6d98a'); BRASS_D = hexc('#c9932a')
STEEL = hexc('#c9ced3'); PINC = hexc('#d9a441'); DRIVC = hexc('#9aa3ab')
GREEN = hexc('#4c9d6b')
CODE = [3, 1, 5, 2, 4]

def profile(k):
    """Top edge y of the key blade at key-local x k (0 = shoulder)."""
    if k < 0 or k > KEYLEN: return None
    y = KW_TOP
    for i, px in enumerate(PX):
        kx = px - FACE
        d = abs(k - kx)
        if d < 42:
            y = max(y, lerp(SL + LK[i], KW_TOP, d / 42))
    if k > KEYLEN - 50:
        y = max(y, lerp(KW_TOP, KW_BOT - 15, (k - (KEYLEN - 50)) / 50))
    return y

def key_offset(t):
    """Distance the key still has to travel (big = outside)."""
    s = B(6) + 0.6
    return 900 * (1 - ease((t - s) / 3.4))

def pin_bottoms(t, off):
    out = []
    for i, px in enumerate(PX):
        k = px - FACE + off
        p = profile(k) if off < 899 else None
        out.append(min(REST, p) if p is not None else REST)
    return out

def draw_spring(ctx, x, y0, y1, a=1.0):
    n = 7; w = 15
    ctx.move_to(x, y0)
    for j in range(1, 2*n):
        ctx.line_to(x + (w if j % 2 else -w), y0 + (y1 - y0) * j / (2*n))
    ctx.line_to(x, y1)
    setc(ctx, INK2, a); ctx.set_line_width(4); ctx.stroke()

def draw_key(ctx, off, a=1.0, x0=FACE):
    if a <= 0: return
    x = x0 - off
    # blade
    ctx.move_to(x, KW_BOT)
    ctx.line_to(x, KW_TOP)
    k = 0
    while k <= KEYLEN:
        ctx.line_to(x + k, profile(k)); k += 4
    ctx.line_to(x + KEYLEN, KW_BOT - 15); ctx.line_to(x + KEYLEN - 15, KW_BOT); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=4, alpha=a)
    ctx.move_to(x + 20, 1000); ctx.line_to(x + KEYLEN - 60, 1000)
    setc(ctx, INK2, 0.5 * a); ctx.set_line_width(3); ctx.stroke()
    # shoulder + bow
    rrect(ctx, x - 60, 925, 64, 110, 8); fill_stroke(ctx, STEEL, lw=4, alpha=a)
    ctx.arc(x - 120, 980, 72, 0, 2*math.pi); fill_stroke(ctx, STEEL, lw=5, alpha=a)
    ctx.arc(x - 140, 980, 18, 0, 2*math.pi); setc(ctx, WALL1, a); ctx.fill_preserve()
    setc(ctx, INK, a); ctx.set_line_width(4); ctx.stroke()

def draw_lock(ctx, t, st):
    sx, sy, sw, sh = SHELL
    turned = st['turn']
    # bolt + door frame (behind)
    bx = 760 - 150 * turned
    rrect(ctx, 990, 1180, 90, 300, 4); fill_stroke(ctx, hexc('#d9b98a'), lw=5)
    rrect(ctx, 1000, 1225, 60, 80, 4); setc(ctx, hexc('#8a6a3a')); ctx.fill()
    rrect(ctx, 560, 1170, 40, 70, 6); fill_stroke(ctx, BRASS_D, lw=4)                 # tailpiece
    rrect(ctx, bx, 1235, 300, 60, 8); fill_stroke(ctx, STEEL, lw=5)                  # bolt
    ctx.move_to(580, 1240); ctx.line_to(bx + 30, 1265); setc(ctx, INK, 1); ctx.set_line_width(6); ctx.stroke()
    # shell body
    rrect(ctx, sx, sy, sw, sh, 30); fill_stroke(ctx, BRASS, lw=6)
    # plug
    px, py, pw, ph = PLUG
    plugc = lerpc(BRASS_L, hexc('#cfe6c9'), turned * 0.8)
    rrect(ctx, px, py, pw, ph, 10); fill_stroke(ctx, plugc, lw=5)
    # keyway
    rrect(ctx, px, KW_TOP, pw - 30, KW_BOT - KW_TOP, 6); setc(ctx, hexc('#6b5a3a', 0.35)); ctx.fill()
    # chambers
    for x in PX:
        rrect(ctx, x - 24, SPR_TOP - 10, 48, KW_TOP - SPR_TOP + 10, 6); setc(ctx, hexc('#5b4a2a', 0.28)); ctx.fill()
    off = st['off']
    bots = pin_bottoms(t, off)
    draw_key(ctx, off, st['key'])
    # pins
    for i, x in enumerate(PX):
        kb = bots[i]; kt = kb - LK[i]
        db = kt; dt = db - LD
        lift = 0
        draw_spring(ctx, x, SPR_TOP, dt)
        rrect(ctx, x - 19, dt, 38, LD, 8); fill_stroke(ctx, DRIVC, lw=4)
        ctx.move_to(x - 19, kb - 10); ctx.line_to(x - 19, kt); ctx.line_to(x + 19, kt)
        ctx.line_to(x + 19, kb - 10); ctx.line_to(x, kb + 4); ctx.close_path()
        fill_stroke(ctx, PINC, lw=4)
        if st['code'] > 0:
            text_c(ctx, str(CODE[i]), x, 625, 44, RED, True, 0, st['code'])
    # shear line
    a = st['shear']
    if a > 0:
        ok = st['ok']
        col = lerpc(RED, GREEN, ok)
        ctx.move_to(sx + 10, SL); ctx.line_to(sx + sw - 10, SL)
        ctx.set_dash([18, 10]); setc(ctx, col, a); ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
        tag(ctx, "SHEAR LINE", 840, 1115, col, a * st['shear_tag'], 22)
        if st['jam'] > 0:
            for i, x in enumerate(PX):
                if bots[i] - LK[i] > SL + 2:
                    cross(ctx, x + 40, SL, RED, st['jam'])
    # closed cover (before the cut-away)
    cut = st['cut']
    if cut < 1:
        rrect(ctx, sx, sy, sw, sh, 30); setc(ctx, BRASS, 1 - cut); ctx.fill_preserve()
        setc(ctx, INK, 1 - cut); ctx.set_line_width(6); ctx.stroke()
        for i in range(5):
            ctx.move_to(sx + 40, sy + 70 + i*90); ctx.line_to(sx + sw - 40, sy + 70 + i*90)
            setc(ctx, BRASS_D, 0.5*(1 - cut)); ctx.set_line_width(4); ctx.stroke()
        text_c(ctx, "?", sx + sw/2, sy + sh/2 + 50, 150, INK, True, 0, (1 - cut) * 0.8)
    # highlights & tags
    highlight(ctx, 590, 975, 400, 115, TEAL, st['h_plug'], t)
    highlight(ctx, 600, 800, 300, 170, RED, st['h_pins'], t)
    highlight(ctx, 600, 715, 290, 70, ORANGE, st['h_spr'], t)
    highlight(ctx, 560, 975, 420, 90, COLD, st['h_key'], t)
    tag(ctx, "1 · THE PLUG", 640, 1115, TEAL, st['l_plug'])
    tag(ctx, "2 · PIN STACKS", 600, 590, RED, st['l_pins'])
    tag(ctx, "3 · SPRINGS", 860, 600, ORANGE, st['l_spr'])
    tag(ctx, "4 · THE KEY", 330, 1115, COLD, st['l_key'])
    if st['jamtag'] > 0: tag(ctx, "JAMMED!", 590, 1335, RED, st['jamtag'], 30)
    if st['click'] > 0:
        tag(ctx, "CLICK!", 300, 1335, GREEN, st['click'], 32)
        straight_arrow(ctx, 1000, 1400, 760, 1400, GREEN, st['click'] * 0.0)
    if st['open'] > 0: tag(ctx, "BOLT PULLED BACK", 760, 1390, GREEN, st['open'], 24)
    if st['ret'] > 0:
        ra = st['ret']
        ctx.arc(590, 975, 150, math.pi * 1.15, math.pi * 1.85)
        setc(ctx, GREEN, ra); ctx.set_line_width(7); ctx.stroke()
        ang = math.pi * 1.85
        hx, hy = 590 + 150*math.cos(ang), 975 + 150*math.sin(ang)
        ctx.move_to(hx + 4, hy - 22); ctx.line_to(hx + 20, hy + 6); ctx.line_to(hx - 10, hy + 6); ctx.close_path()
        setc(ctx, GREEN, ra); ctx.fill()
    if st['graph'] > 0:
        g = st['graph']
        rnd = random.Random(5)
        for i in range(40):
            x = 240 + rnd.random() * 680; y = 900 + ((t * 30 + rnd.random() * 160) % 160)
            ctx.arc(x, y, 3.5, 0, 2*math.pi); setc(ctx, INK2, g * 0.7); ctx.fill()
        tag(ctx, "GRAPHITE: YES", 330, 1335, GREEN, g, 28)
        tag(ctx, "OIL: NO", 760, 1335, RED, g, 28)

def cross(ctx, x, y, col, a, s=14):
    ctx.move_to(x - s, y - s); ctx.line_to(x + s, y + s); ctx.move_to(x + s, y - s); ctx.line_to(x - s, y + s)
    setc(ctx, col, a); ctx.set_line_width(6); ctx.stroke()

def check(ctx, x, y, col, a, s=14):
    ctx.move_to(x - s, y); ctx.line_to(x - s/3, y + s*0.8); ctx.line_to(x + s, y - s*0.8)
    setc(ctx, col, a); ctx.set_line_width(6); ctx.stroke()

# ---------------------------------------------------------------- state machine
def state(t):
    st = {}
    st['cut'] = ease((t - B(1) - 0.3) / 1.2)
    st['off'] = key_offset(t)
    st['key'] = 1.0 if t >= B(6) else 0.0
    st['turn'] = ease((t - B(8) - 0.8) / 1.0)
    st['shear'] = max(bw(t, 2, 3), bw(t, 5, 9), bw(t, 13, 14))
    st['shear_tag'] = max(bw(t, 2, 3), bw(t, 5, 6))
    st['ok'] = ease((t - B(7) + 0.2) / 0.5)
    st['jam'] = bw(t, 5, 6)
    st['jamtag'] = win(t, B(5) + 1.5, B(6))
    st['h_plug'] = bw(t, 3)
    st['h_pins'] = bw(t, 4)
    st['h_spr'] = bw(t, 5)
    st['h_key'] = win(t, B(6) + 3.8, B(7))
    st['l_plug'] = bw(t, 3) + bw(t, 13, 14)
    st['l_pins'] = bw(t, 4) + bw(t, 13, 14)
    st['l_spr'] = bw(t, 5) + bw(t, 13, 14)
    st['l_key'] = bw(t, 6) + bw(t, 13, 14)
    st['click'] = win(t, B(8) + 0.8, B(9))
    st['open'] = win(t, B(8) + 1.6, B(9))
    st['ret'] = win(t, B(8) + 0.6, B(8) + 2.4)
    st['code'] = bw(t, 12, 13)
    st['graph'] = bw(t, 14, 15)
    return st

SFX = [(B(1) + 0.4, 'whoosh'), (B(3) + 0.2, 'pop'), (B(4) + 0.2, 'pop'), (B(5) + 0.2, 'pop'),
       (B(6) + 0.2, 'pop'), (B(8) + 0.8, 'click'), (B(12) + 0.2, 'ding'),
       (B(13) + 0.2, 'pop'), (B(13) + 0.4, 'pop'), (B(13) + 0.6, 'pop'), (B(13) + 0.8, 'pop')]
HUM = []

def draw_set(ctx):
    window(ctx, 50, 260, 200, 300)

def draw(ctx, t, E):
    draw_lock(ctx, t, state(t))

# ---------------------------------------------------------------- cards
def mini_stack(ctx, x, y_sl, top_y, key_top, lk, a, w=40):
    """One pin stack in a card: key pin length lk sits on key_top."""
    kt = key_top - lk
    rrect(ctx, x - w/2, kt - 60, w, 60, 8); fill_stroke(ctx, DRIVC, lw=4, alpha=a)
    rrect(ctx, x - w/2, kt, w, lk, 8); fill_stroke(ctx, PINC, lw=4, alpha=a)
    draw_spring(ctx, x, top_y, kt - 60, a)
    return kt

def card_shear(ctx, t, lt, a):
    card_frame(ctx, "THE SHEAR LINE", a, "ONE PIN ACROSS THE LINE = LOCKED", RED)
    ok = ease((lt - 2.6) / 0.6)
    rrect(ctx, 150, 260, 780, 160, 12); fill_stroke(ctx, BRASS, lw=4, alpha=a)
    rrect(ctx, 150, 420, 780, 110, 12); fill_stroke(ctx, BRASS_L, lw=4, alpha=a)
    text_c(ctx, "FIXED SHELL", 300, 300, 24, INK, True, 1, a)
    text_c(ctx, "TURNING PLUG", 300, 505, 24, INK, True, 1, a)
    shift = 6 * math.sin(lt * 14) * (1 - ok)
    x = 620
    gap = lerp(470, 420, ok)
    rrect(ctx, x - 22, gap - 90, 44, 90, 8); fill_stroke(ctx, DRIVC, lw=4, alpha=a)
    rrect(ctx, x - 22 + shift, gap, 44, 520 - gap, 8); fill_stroke(ctx, PINC, lw=4, alpha=a)
    col = lerpc(RED, GREEN, ok)
    ctx.move_to(150, 420); ctx.line_to(930, 420); ctx.set_dash([16, 10]); setc(ctx, col, a)
    ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
    if ok < 0.5: cross(ctx, 720, 420, RED, a * (1 - 2*ok), 18)
    else: check(ctx, 720, 420, GREEN, a * (2*ok - 1), 18)

def key_card(ctx, lt, a, wrong):
    xs = [250, 395, 540, 685, 830]
    lks = [40, 20, 55, 30, 45]
    line = 360
    rrect(ctx, 140, 255, 800, line - 255, 10); fill_stroke(ctx, BRASS, lw=4, alpha=a)
    rrect(ctx, 140, line, 800, 175, 10); fill_stroke(ctx, BRASS_L, lw=4, alpha=a)
    errs = [0, 0, 0, 0, 0]
    if wrong: errs[2] = -28 * ease((lt - 1.0) / 0.6)
    # key profile
    ctx.move_to(140, 535)
    tops = []
    for i, x in enumerate(xs):
        tops.append(line + lks[i] + errs[i])
    ctx.line_to(140, 400)
    for i, x in enumerate(xs):
        ctx.line_to(x - 40, 400); ctx.line_to(x, tops[i]); ctx.line_to(x + 40, 400)
    ctx.line_to(940, 400); ctx.line_to(940, 535); ctx.close_path()
    fill_stroke(ctx, STEEL, lw=4, alpha=a)
    for i, x in enumerate(xs):
        kt = mini_stack(ctx, x, line, 262, tops[i], lks[i], a, 36)
    bad = wrong and lt > 1.4
    col = RED if bad else GREEN
    ctx.move_to(140, line); ctx.line_to(940, line); ctx.set_dash([16, 10]); setc(ctx, col, a)
    ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
    for i, x in enumerate(xs):
        if bad and i == 2: cross(ctx, x + 45, line, RED, a, 15)
        elif lt > 0.8 + i * 0.25: check(ctx, x + 45, line - 2, GREEN, a, 12)

def card_cuts(ctx, t, lt, a):
    card_frame(ctx, "THE RIGHT KEY", a, "EVERY GAP ON THE LINE = OPEN", GREEN)
    key_card(ctx, lt, a, False)

def card_wrong(ctx, t, lt, a):
    card_frame(ctx, "THE WRONG KEY", a, "ONE PIN OFF = STILL LOCKED", RED)
    key_card(ctx, lt, a, True)

WOOD = hexc('#c98b4a'); WOOD_L = hexc('#e2ae6d'); WOOD_D = hexc('#8a5a2b')
def card_egypt(ctx, t, lt, a):
    card_frame(ctx, "ANCIENT EGYPT", a, "WOODEN PIN LOCK • ~4,000 YEARS AGO", WOOD_D)
    # sun + pyramid motif
    ctx.move_to(150, 520); ctx.line_to(240, 380); ctx.line_to(330, 520); ctx.close_path()
    fill_stroke(ctx, MUSTARD, lw=4, alpha=a)
    ctx.arc(300, 300, 26, 0, 2*math.pi); setc(ctx, ORANGE, a); ctx.fill()
    # housing with falling pegs
    rrect(ctx, 470, 260, 300, 110, 8); fill_stroke(ctx, WOOD, lw=4, alpha=a)
    ky = lerp(540, 445, ease((lt - 0.6) / 1.6))
    slide = ease((lt - 3.0) / 1.0)
    # bolt
    bx = 380 + 140 * slide
    rrect(ctx, bx, 370, 520, 70, 8); fill_stroke(ctx, WOOD_L, lw=4, alpha=a)
    for j, x in enumerate((540, 620, 700)):
        py = min(345, ky - 75 - 70)
        rrect(ctx, x - 13, py, 26, 70, 5)
        fill_stroke(ctx, WOOD_D, lw=3, alpha=a)
    # key from below
    rrect(ctx, 500, ky, 360, 40, 6); fill_stroke(ctx, WOOD, lw=4, alpha=a)
    for x in (540, 620, 700):
        rrect(ctx, x - 9, ky - 75, 18, 77, 4); fill_stroke(ctx, WOOD, lw=3, alpha=a)
    straight_arrow(ctx, 920, 405, 960, 405, INK, a * slide)

CARDS = {'shear': card_shear, 'cuts': card_cuts, 'wrong': card_wrong, 'egypt': card_egypt}
