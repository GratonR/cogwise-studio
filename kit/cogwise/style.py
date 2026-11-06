"""Cogwise visual language: vintage-manual palette, fonts, drawing primitives, brand marks.

Canvas is 1080x1920 (9:16). Layout zones (keep episodes inside them):
  - title strip     y   60..170   (hidden while an inset card is shown)
  - card zone       y  150..610   (inset "zoom" cards)
  - stage           y  300..1500  (the explained object; foreground scales to 0.78 when a card shows)
  - floor           y 1500..1650
  - caption band    y 1650..1920  (engine draws captions + disclaimer)
"""
import cairo, math, random

W, H, FPS = 1080, 1920, 30
FONT = "Lora"                 # titles, tags, card text
CAPTION_FONT = "Inter Bold"   # burned-in captions
SANS = "Inter"

def hexc(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)

# ---- palette (vintage manual: cream paper, ink, riso red / mustard / teal)
INK    = hexc('#26232b')   # outlines, text
INK2   = hexc('#5a5560')   # secondary lines
PAPER  = hexc('#fbf5e8')   # light fills (objects)
CREAM  = hexc('#fbf5e8')   # card background
WALL1  = hexc('#f4ead6'); WALL2 = hexc('#efe2c8')
FILL2  = hexc('#efe4cd'); FILL3 = hexc('#e2d3b5')
TEAL   = hexc('#1f8a8a'); TEAL_L = hexc('#8fcfc8')
COLD   = hexc('#1f8a8a'); VAPOR = hexc('#7cc4bd')
ORANGE = hexc('#f2902b'); RED = hexc('#e4472f'); MUSTARD = hexc('#f2b134')
FLOOR  = hexc('#26232b'); BAND = hexc('#f2b134'); BAND_EDGE = hexc('#e4472f')
DISC   = hexc('#6b4d10'); CARD_B = hexc('#26232b')
WHITE  = hexc('#ffffff')
# compatibility aliases used by older episode code
SLATE, SLATE2 = INK, INK2

OUTRO = "Cogwise: how things work. Follow for the next one!"
DISCLAIMER = "Simplified educational model • not a repair guide"

# ---- math helpers
def lerp(a, b, t): return a + (b - a) * t
def lerpc(c1, c2, t): return tuple(lerp(c1[i], c2[i], t) for i in range(4))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t):
    t = clamp(t); return t * t * (3 - 2 * t)
def win(t, a, b, fade=0.35):
    """1 inside [a,b], smooth fades at both edges, 0 outside."""
    if t < a or t > b: return 0.0
    return ease(min((t - a) / fade, (b - t) / fade, 1.0))

# ---- drawing primitives
def setc(ctx, c, alpha=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], c[3] * alpha)

def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi/2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi/2)
    ctx.arc(x + r, y + h - r, r, math.pi/2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3*math.pi/2)
    ctx.close_path()

def fill_stroke(ctx, fill, stroke=INK, lw=5, alpha=1.0):
    setc(ctx, fill, alpha); ctx.fill_preserve()
    setc(ctx, stroke, alpha); ctx.set_line_width(lw); ctx.stroke()

def font(ctx, size, bold=True, face=None):
    ctx.select_font_face(face or FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def spaced_width(ctx, s, sp):
    return sum(ctx.text_extents(ch).x_advance for ch in s) + sp * (len(s) - 1)

def text_c(ctx, s, cx, y, size, color, bold=True, sp=0, alpha=1.0, fontname=None):
    """Centered text with optional letter spacing. y is the baseline."""
    font(ctx, size, bold, fontname)
    w = spaced_width(ctx, s, sp); x = cx - w / 2
    setc(ctx, color, alpha)
    for ch in s:
        ctx.move_to(x, y); ctx.show_text(ch)
        x += ctx.text_extents(ch).x_advance + sp
    ctx.new_path()

def wavy_arrow(ctx, x0, y0, x1, y1, t, color, alpha=1.0, amp=10, wl=46, lw=6, head=16):
    """Animated heat/energy arrow (wave travels with t)."""
    if alpha <= 0: return
    L = math.dist((x0, y0), (x1, y1)); ang = math.atan2(y1-y0, x1-x0)
    ctx.save(); ctx.translate(x0, y0); ctx.rotate(ang)
    n = 40
    for i in range(n + 1):
        x = (L - head) * i / n
        env = math.sin(math.pi * i / n) ** 0.6
        y = amp * env * math.sin(2*math.pi*x/wl - t*8)
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    setc(ctx, color, alpha); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.move_to(L, 0); ctx.line_to(L - head*1.3, -head*0.8); ctx.line_to(L - head*1.3, head*0.8); ctx.close_path()
    setc(ctx, color, alpha); ctx.fill()
    ctx.restore()

def straight_arrow(ctx, x0, y0, x1, y1, color, alpha=1.0, lw=6, head=14):
    if alpha <= 0: return
    ang = math.atan2(y1-y0, x1-x0)
    ctx.move_to(x0, y0); ctx.line_to(x1 - math.cos(ang)*head, y1 - math.sin(ang)*head)
    setc(ctx, color, alpha); ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    ctx.save(); ctx.translate(x1, y1); ctx.rotate(ang)
    ctx.move_to(0, 0); ctx.line_to(-head*1.4, -head*0.85); ctx.line_to(-head*1.4, head*0.85); ctx.close_path()
    setc(ctx, color, alpha); ctx.fill(); ctx.restore()

def tag(ctx, text, x, y, color, alpha=1.0, size=26):
    """Pill label pointing out a part ('1 · EVAPORATOR')."""
    if alpha <= 0: return
    font(ctx, size, True); sp = 1.5
    w = spaced_width(ctx, text, sp) + 32; h = size + 20
    rrect(ctx, x - w/2, y - h/2, w, h, h/2)
    setc(ctx, CREAM, 0.95*alpha); ctx.fill_preserve()
    setc(ctx, color, alpha); ctx.set_line_width(3); ctx.stroke()
    text_c(ctx, text, x, y + size*0.36, size, color, True, sp, alpha)

def highlight(ctx, cx, cy, rx, ry, color, a, t):
    """Pulsing dashed ellipse around the part being explained."""
    if a <= 0: return
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(rx, ry); ctx.arc(0, 0, 1, 0, 2*math.pi); ctx.restore()
    setc(ctx, color, a * (0.10 + 0.08*pulse)); ctx.fill_preserve()
    ctx.set_dash([14, 10]); setc(ctx, color, a); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])

def card_frame(ctx, title, alpha, label=None, label_col=TEAL):
    """Inset 'zoom' card in the top zone. Draw the card's diagram inside x 110..970, y 250..540."""
    rrect(ctx, 90, 150, 900, 460, 26)
    setc(ctx, CREAM, 0.97*alpha); ctx.fill_preserve()
    setc(ctx, CARD_B, alpha); ctx.set_line_width(4); ctx.stroke()
    text_c(ctx, title, 540, 218, 38, INK, True, 2, alpha)
    if label:
        text_c(ctx, label, 540, 580, 32, label_col, True, 1.5, alpha)

def thermometer(ctx, x, y, level, a, color=COLD, h=170):
    rrect(ctx, x - 14, y - h, 28, h, 14); fill_stroke(ctx, WHITE, lw=4, alpha=a)
    ctx.arc(x, y + 6, 22, 0, 2*math.pi); fill_stroke(ctx, color, lw=4, alpha=a)
    hh = (h - 20) * level
    rrect(ctx, x - 6, y - hh, 12, hh + 6, 6); setc(ctx, color, a); ctx.fill()

# ---- base set (wall, floor, caption band, grain). Episodes add their props on top.
def base_set(ctx):
    g = cairo.LinearGradient(0, 0, 0, 1510)
    g.add_color_stop_rgb(0, *WALL1[:3]); g.add_color_stop_rgb(1, *WALL2[:3])
    ctx.set_source(g); ctx.rectangle(0, 0, W, 1510); ctx.fill()
    setc(ctx, FLOOR); ctx.rectangle(0, 1500, W, 150); ctx.fill()
    setc(ctx, hexc('#d9c39b')); ctx.rectangle(0, 1478, W, 22); ctx.fill()
    setc(ctx, BAND); ctx.rectangle(0, 1650, W, H-1650); ctx.fill()
    setc(ctx, BAND_EDGE); ctx.rectangle(0, 1650, W, 6); ctx.fill()
    text_c(ctx, DISCLAIMER, W/2, 1880, 24, DISC, bold=False)

def grain(ctx, seed=1):
    rnd = random.Random(seed)
    for i in range(26000):
        x, y = rnd.random()*W, rnd.random()*H
        ctx.rectangle(x, y, 1.8, 1.8); ctx.set_source_rgba(0.15, 0.13, 0.17, 0.045); ctx.fill()
    for i in range(1800):
        x, y = rnd.random()*W, rnd.random()*H
        ctx.rectangle(x, y, 2.4, 2.4); ctx.set_source_rgba(1, 1, 1, 0.12); ctx.fill()

def window(ctx, wx=50, wy=300, ww=220, wh=330):
    """Optional backdrop prop: window with sun + hills (brand motif)."""
    ctx.save(); rrect(ctx, wx, wy, ww, wh, 10); ctx.clip()
    g2 = cairo.LinearGradient(0, wy, 0, wy+wh)
    g2.add_color_stop_rgb(0, *hexc('#f6e7c3')[:3]); g2.add_color_stop_rgb(1, *hexc('#efd6a3')[:3])
    ctx.set_source(g2); ctx.paint()
    ctx.arc(wx+160, wy+80, 30, 0, 2*math.pi); setc(ctx, MUSTARD); ctx.fill()
    for dx, dy, r in [(0, 0, 16), (18, -8, 20), (38, 0, 15)]:
        ctx.arc(wx+60+dx, wy+110+dy, r, 0, 2*math.pi); setc(ctx, WHITE); ctx.fill()
    ctx.move_to(wx, wy+260); ctx.curve_to(wx+60, wy+180, wx+120, wy+190, wx+ww, wy+250)
    ctx.line_to(wx+ww, wy+wh); ctx.line_to(wx, wy+wh); ctx.close_path(); setc(ctx, hexc('#7fb7a4')); ctx.fill()
    ctx.move_to(wx, wy+290); ctx.curve_to(wx+80, wy+240, wx+150, wy+260, wx+ww, wy+280)
    ctx.line_to(wx+ww, wy+wh); ctx.line_to(wx, wy+wh); ctx.close_path(); setc(ctx, hexc('#4f9a8a')); ctx.fill()
    ctx.restore()
    rrect(ctx, wx, wy, ww, wh, 10); setc(ctx, INK); ctx.set_line_width(6); ctx.stroke()
    ctx.move_to(wx+ww/2, wy); ctx.line_to(wx+ww/2, wy+wh); ctx.move_to(wx, wy+wh/2); ctx.line_to(wx+ww, wy+wh/2)
    ctx.set_line_width(5); ctx.stroke()
    rrect(ctx, wx-14, wy+wh, ww+28, 16, 5); fill_stroke(ctx, PAPER, lw=4)

def counter(ctx, x=20, w=270):
    """Optional backdrop prop: low cabinet with countertop."""
    rrect(ctx, x, 1150, w, 26, 6); fill_stroke(ctx, FILL3, lw=5)
    rrect(ctx, x+12, 1176, w-24, 324, 4); fill_stroke(ctx, PAPER, lw=5)
    ctx.move_to(x+135, 1190); ctx.line_to(x+135, 1486); setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    for kx in (x+118, x+152):
        rrect(ctx, kx-4, 1240, 8, 50, 4); setc(ctx, INK); ctx.fill()

# ---- title & captions
def title(ctx, s, a):
    if a > 0: text_c(ctx, s, W/2, 128, 40, INK, True, 2.5, a)

def _wrap(ctx, text, maxw):
    words = text.split(); lines = []; cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if ctx.text_extents(test).x_advance > maxw and cur:
            lines.append(cur); cur = w
        else: cur = test
    lines.append(cur)
    return lines

def caption(ctx, text, a):
    if a <= 0 or not text: return
    ctx.select_font_face(CAPTION_FONT, 0, 0)
    for size in (46, 42, 38, 34):            # shrink until it fits on 2 lines
        ctx.set_font_size(size); lines = _wrap(ctx, text, 920)
        if len(lines) <= 2: break
    lh = size * 1.35
    y0 = 1752 - (len(lines) - 1) * lh / 2
    ctx.new_path()
    for i, ln in enumerate(lines):
        w = ctx.text_extents(ln).x_advance
        ctx.move_to(W/2 - w/2, y0 + i*lh); ctx.text_path(ln)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    setc(ctx, INK, a); ctx.set_line_width(9); ctx.stroke_preserve()
    setc(ctx, WHITE, a); ctx.fill()

# ---- brand marks
def gear(ctx, cx, cy, ro, ri, teeth, hole, fill, lw=6, rot=0, ink=INK):
    ctx.new_path(); n = teeth * 4
    for i in range(n + 1):
        a = rot + 2*math.pi*i/n
        r = ro if (i % 4) in (1, 2) else ri
        (ctx.move_to if i == 0 else ctx.line_to)(cx + r*math.cos(a), cy + r*math.sin(a))
    ctx.close_path()
    ctx.new_sub_path(); ctx.arc_negative(cx, cy, hole, 2*math.pi, 0)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    setc(ctx, fill); ctx.fill_preserve()
    setc(ctx, ink); ctx.set_line_width(lw); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)

def owl(ctx, cx, cy, s):
    """Cogwise owl mascot (cog eyes). ~ 300*s px wide, 330*s px tall, centred on (cx, cy)."""
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    for sx in (-1, 1):
        ctx.move_to(sx*70, -95); ctx.line_to(sx*112, -150); ctx.line_to(sx*118, -70); ctx.close_path()
        fill_stroke(ctx, TEAL, lw=7)
    ctx.move_to(0, -120); ctx.curve_to(110, -120, 140, -20, 130, 60)
    ctx.curve_to(120, 150, 60, 175, 0, 175); ctx.curve_to(-60, 175, -120, 150, -130, 60)
    ctx.curve_to(-140, -20, -110, -120, 0, -120); ctx.close_path(); fill_stroke(ctx, TEAL, lw=8)
    ctx.move_to(0, 40); ctx.curve_to(70, 40, 85, 160, 0, 165); ctx.curve_to(-85, 160, -70, 40, 0, 40)
    fill_stroke(ctx, PAPER, lw=6)
    for i, yy in enumerate((85, 115, 140)):
        for xx in ((-20, 20) if i != 1 else (-35, 0, 35)):
            ctx.move_to(xx-10, yy); ctx.curve_to(xx-5, yy+10, xx+5, yy+10, xx+10, yy)
            setc(ctx, INK); ctx.set_line_width(4); ctx.stroke()
    for sx in (-1, 1):
        gear(ctx, sx*55, -30, 58, 46, 10, 0.01, MUSTARD, lw=6, rot=sx*0.2)
        ctx.new_path(); ctx.arc(sx*55, -30, 30, 0, 2*math.pi); fill_stroke(ctx, PAPER, lw=5)
        ctx.arc(sx*55 + 6, -26, 14, 0, 2*math.pi); setc(ctx, INK); ctx.fill()
        ctx.arc(sx*55 + 11, -32, 4, 0, 2*math.pi); setc(ctx, WHITE); ctx.fill()
    ctx.move_to(-16, 12); ctx.line_to(16, 12); ctx.line_to(0, 40); ctx.close_path(); fill_stroke(ctx, RED, lw=5)
    ctx.restore()

def wordmark(ctx, cx, cy, size, tagline=True):
    """COGWISE with the O as a red cog, mustard rule and 'HOW THINGS WORK'."""
    font(ctx, size, True)
    wc = ctx.text_extents("C").x_advance; wg = ctx.text_extents("GWISE").x_advance
    go = size*0.36; gw = go*2 + size*0.06
    total = wc + gw + wg; x = cx - total/2
    setc(ctx, INK); ctx.move_to(x, cy); ctx.show_text("C"); x += wc
    gear(ctx, x + gw/2, cy - size*0.35, go, go*0.8, 9, go*0.36, RED, lw=size*0.055, rot=0.15)
    x += gw
    font(ctx, size, True); setc(ctx, INK); ctx.move_to(x, cy); ctx.show_text("GWISE"); ctx.new_path()
    if tagline:
        ctx.rectangle(cx - total/2, cy + size*0.22, total, size*0.07); setc(ctx, MUSTARD); ctx.fill()
        text_c(ctx, "HOW THINGS WORK", cx, cy + size*0.62, size*0.24, INK, True, size*0.06, fontname=SANS)

def end_card(ctx, t, a):
    """Owl + wordmark, drawn by the engine over the last (brand) beat."""
    if a <= 0: return
    ctx.push_group()
    owl(ctx, 540, 215 + math.sin(t*4)*5, 0.5)
    wordmark(ctx, 560, 425, 86)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


# ---- micro-beat format (R&D 2026-11): HUD counter, big word pops, corner mark
def corner_mark(ctx):
    """Small COGWISE mark top-right, used when an episode has no outro (loop format)."""
    ctx.push_group(); wordmark(ctx, 900, 92, 34, tagline=False); ctx.pop_group_to_source(); ctx.paint_with_alpha(0.85)

def hud(ctx, label, value, sub=None, a=1.0, color=None, flash=0.0, x=40, y=150, w=520):
    """Ink 'counter' box top-left: small label, BIG value, optional sub line. flash 0..1 tints the value."""
    if a <= 0: return
    color = color or MUSTARD
    h = 150 if sub else 118
    rrect(ctx, x, y, w, h, 14); setc(ctx, INK, 0.92 * a); ctx.fill_preserve()
    setc(ctx, color, a); ctx.set_line_width(3); ctx.stroke()
    ctx.select_font_face(SANS, 0, 1); ctx.set_font_size(24); setc(ctx, CREAM, a)
    ctx.move_to(x + 22, y + 38); ctx.show_text(label)
    ctx.select_font_face(CAPTION_FONT, 0, 0); ctx.set_font_size(64)
    setc(ctx, lerpc(CREAM, color, clamp(0.35 + flash)), a); ctx.move_to(x + 20, y + 104); ctx.show_text(value)
    if sub:
        ctx.select_font_face(SANS, 0, 1); ctx.set_font_size(24); setc(ctx, color, a)
        ctx.move_to(x + 22, y + 138); ctx.show_text(sub)
    ctx.new_path()

def pop_word(ctx, text, lt, dur, color=None, cx=None, cy=760, size=150):
    """Big word that pops in (overshoot), holds, and fades. lt = local time since it appeared."""
    if lt < 0 or lt > dur: return
    color = color or RED
    k = clamp(lt / 0.22); s = 1 + 0.25 * math.sin(k * math.pi) if k < 1 else 1.0
    s *= lerp(0.6, 1.0, ease(k))
    a = ease(k) * (1 - ease((lt - dur + 0.25) / 0.25))
    cx = W / 2 if cx is None else cx
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    ctx.select_font_face(CAPTION_FONT, 0, 0); ctx.set_font_size(size)
    e = ctx.text_extents(text); ctx.move_to(-e.x_advance / 2, size * 0.36); ctx.text_path(text)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND); setc(ctx, INK, a); ctx.set_line_width(16); ctx.stroke_preserve()
    setc(ctx, color, a); ctx.fill(); ctx.restore()

def cam_track(keys, t, move=0.7):
    """keys = [(t, cx, cy, zoom), ...] sorted: from time t the camera glides (eased, `move` s) to that framing."""
    pos = keys[0][1:]
    for i in range(1, len(keys)):
        if t < keys[i][0]: break
        u = ease(clamp((t - keys[i][0]) / move))
        pos = tuple(lerp(pos[j], keys[i][1 + j], u) for j in range(3))
    return pos
