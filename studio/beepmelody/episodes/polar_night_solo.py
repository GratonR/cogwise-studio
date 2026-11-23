"""BEEPMELODY — 48 Days of Night. Then 68 Days of Day.  (polar-night, rework: Tromsø only)
365 days (23 Sep 2026 -> 22 Sep 2027) of daylight in Tromsø (69.65 N), equinox to equinox.
Every day = one note (co-pilot rework step 2 = A · « Marimba claire », 84 BPM): the marimba falls and shortens with
the day, goes silent for the 48 days without sunrise (aurora shimmer only), comes back, and under the midnight sun
(68 days) the same top note is held. Pitch = hours of daylight (0 h low -> 24 h high). Clock: 6 days per second.
Angle B (mirror): two equal banners « 48 DAYS OF NIGHT » / « 68 DAYS OF DAY », big counter 0 H -> 24 H.
Scene: full screen Tromsø (fjord, bridge, houses, snow, aurora, the sun's path of the day), frame follows day/night.
Data: polar_night_draft.csv (computed PyEphem + NOAA/astral, cross-checked visittromso.no).

    python3 polar_night_solo.py info out | at out <T> ... | audio out/music.wav | render out | final out x.mp4
Env: PN_COUNTER=bottom (default, counter on the snow) | top (counter under the HUD, bigger)
"""
import sys, os, math, random, subprocess, csv, datetime as dt
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx

FXK = float(os.environ.get("PI_FX", "0.5"))
VARIANT = "clear"
COUNTER = os.environ.get("PN_COUNTER", "bottom")

# ================= data =================
ROWS = list(csv.DictReader(open(os.path.join(HERE, "polar_night_draft.csv"))))
DAYS = [dt.date.fromisoformat(r["date"]) for r in ROWS]
HT = [float(r["tromso_daylight_h"]) for r in ROWS]
N = len(ROWS); assert N == 365
LAT_T = 69.6492
def decl(d):
    n = d.timetuple().tm_yday
    return -23.44 * math.cos(2 * math.pi / 365 * (n + 10))
DEC = [decl(d) for d in DAYS]
ZERO = [i for i in range(N) if HT[i] == 0]
FULL = [i for i in range(N) if HT[i] >= 24]
assert len(ZERO) == 48 and len(FULL) == 68
def rate(a, b):   # minutes of daylight gained per day between two dates (from the CSV)
    ia, ib = DAYS.index(dt.date.fromisoformat(a)), DAYS.index(dt.date.fromisoformat(b))
    return (HT[ib] - HT[ia]) * 60 / (ib - ia), ia, ib
R_FALL, IF0, IF1 = rate("2026-10-15", "2026-11-15")     # -9.8 min/day
R_SPR, IS0, IS1 = rate("2027-03-02", "2027-04-01")      # +8.6 min/day

# ================= clock =================
D = 1 / 6.0
T0 = 0.60
def tday(i): return T0 + i * D
T_END = tday(N - 1) + 0.9
OUTRO = 5.4
TOTAL = T_END + OUTRO
def day_f(T): return min(N - 1.0, max(0.0, (T - T0) / D))
def day_i(T): return int(day_f(T) + 1e-6)
CUTS = [0, tday(55), tday(130), tday(205), tday(280), T_END, TOTAL]
NAMES = ["a", "b", "c", "d", "e", "outro"]
START = {n: CUTS[k] for k, n in enumerate(NAMES)}
DUR = {n: CUTS[k + 1] - CUTS[k] for k, n in enumerate(NAMES)}

def hm(h):
    if h >= 24: return "24 H"
    mins = int(round(h * 60)); return f"{mins // 60} H {mins % 60:02d} MIN" if mins >= 60 else f"{mins} MIN"
def fdate(d): return f"{d.day} {d.strftime('%b').upper()} {d.year}"

# ================= palette =================
CREAM, WHITE = (255, 249, 236), (255, 255, 255)
INK, INK2 = (40, 44, 62), (110, 116, 140)
CORAL, CORAL2 = (230, 96, 70), (190, 70, 50)
GOLD, GOLD2 = (240, 170, 50), (196, 130, 30)
SUN = (255, 214, 90)
AUR = [(90, 230, 160), (120, 250, 190), (160, 120, 240)]
if True:
    FRAME = (238, 232, 220); HUDBG = CREAM; HUDINK = INK; HUDINK2 = INK2
def mixc(a, b, t): t = max(0, min(1, t)); return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))
# ---- day/night frame (Guillaume, step 3: « cadre jour nuit au fil de la vidéo ») ----
LIGHT = dict(FRAME=(238, 232, 220), HUDBG=CREAM, HUDINK=INK, HUDINK2=INK2)
DARK = dict(FRAME=(22, 26, 48), HUDBG=(34, 40, 66), HUDINK=(236, 232, 220), HUDINK2=(150, 158, 190))
GLOW = dict(FRAME=(250, 232, 190), HUDBG=(255, 246, 222), HUDINK=INK, HUDINK2=INK2)   # midnight sun: warm golden frame
def light_level(T, H=None):
    """0 = night, 1 = day, 2 = midnight sun — smoothed over ±4 days so the frame fades instead of blinking"""
    H = HT if H is None else H
    f = (T - T0) / D; lo, hi = int(max(0, f - 4)), int(min(N - 1, f + 4))
    v = sum(H[i] for i in range(lo, hi + 1)) / (hi - lo + 1)
    return min(1, v / 12) + max(0, (v - 18) / 6)
def theme_at(lv):
    if lv <= 1:
        t = lv; tb = 1.0 if t > 0.5 else 0.0     # boxes switch at once (sky fades): never a grey box with grey text
        out = {"FRAME": mixc(DARK["FRAME"], LIGHT["FRAME"], t), "HUDBG": mixc(DARK["HUDBG"], LIGHT["HUDBG"], tb)}
        ink = LIGHT if t > 0.5 else DARK
    else:
        t = lv - 1; out = {k: mixc(LIGHT[k], GLOW[k], t) for k in ("FRAME", "HUDBG")}; ink = LIGHT
    out["HUDINK"], out["HUDINK2"] = ink["HUDINK"], ink["HUDINK2"]; return out
def set_theme(th):
    global FRAME, HUDBG, HUDINK, HUDINK2
    FRAME, HUDBG, HUDINK, HUDINK2 = th["FRAME"], th["HUDBG"], th["HUDINK"], th["HUDINK2"]
DAY_TOP, DAY_BOT = (120, 186, 236), (206, 232, 250)
NIGHT_TOP, NIGHT_BOT = (14, 20, 52), (36, 50, 96)

# ================= music plan (rework step 2 = A · Marimba claire, 84 BPM, one voice) =================
MAJ = [0, 2, 4, 5, 7, 9, 11]
def pitch(h):
    k = int(round(h / 24 * 21)); return 50 + 12 * (k // 7) + MAJ[k % 7]
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
BEAT = 60 / 84
def build():
    b = 0.0; k = 0
    while b < T_END + 2.0:
        ev(b, "hat", v=0.05 if b < T_END else 0.02)
        if k % 4 == 0: ev(b, "bass", m=[38, 43, 45, 38][(k // 4) % 4], d=BEAT * 3.6, v=0.06)
        b += BEAT; k += 1
    run = None
    for i in range(N):
        t = tday(i)
        if 0 < HT[i] < 24: ev(t, "marimba", m=pitch(HT[i]) + 12, h=HT[i], v=0.24)
        elif HT[i] >= 24:
            ev(t, "tick", m=pitch(24) + 12, v=0.05)
            if run is None: run = t
        if run is not None and (HT[i] < 24 or i == N - 1):
            ev(run, "hold", m=pitch(24), d=t - run, v=0.10); run = None
    z0, z1 = tday(ZERO[0]), tday(ZERO[-1]) + D
    ev(z0, "aurora", d=z1 - z0, v=0.03)
    for j, iv in enumerate([0, 4, 7, 12, 16]):
        ev(tday(N - 1) + 0.15 + j * 0.12, "marimba", m=pitch(HT[-1]) + iv, h=8, v=0.14)
    ev(T_END, "pad", m=pitch(HT[-1]) - 12, d=4.0, v=0.08)
    EV.sort(key=lambda e: e[0])
build()

# ================= drawing =================
Y0 = 22            # art: sky top (under the HUD)
HZ = 140           # art: horizon
Y1 = 262           # art: bottom of the scene (graph box starts at text y 540)

def sky(img_arr, y0, y1, top, bot):
    for y in range(y0, y1):
        f = (y - y0) / max(1, y1 - y0); img_arr[y, :] = mixc(top, bot, f)

def sun_path(d, x0, x1, hz, hpx, h, dec, lat, col):
    """the sun's path for that day: x = hour (midnight .. noon .. midnight), y = altitude above the horizon"""
    if h <= 0: return None
    noon = max(90 - abs(lat - dec), 1.5 + 0.6 * min(h, 6))   # refraction: a short day still shows a low sun
    pts = []
    if h >= 24:
        mid = dec - (90 - lat)
        for k in range(61):
            H = -math.pi + 2 * math.pi * k / 60
            a = mid + (noon - mid) * (1 + math.cos(H)) / 2; pts.append((x0 + (x1 - x0) * k / 60, hz - a / 90 * hpx))
    else:
        H0 = math.pi * h / 24
        for k in range(41):
            H = -H0 + 2 * H0 * k / 40
            a = noon * (math.cos(H) - math.cos(H0)) / (1 - math.cos(H0))
            xm = (x0 + x1) / 2 + (x1 - x0) / 2 * H / math.pi
            pts.append((xm, hz - a / 90 * hpx))
    for p, q in zip(pts, pts[1:]):
        d.line([p, q], fill=col)
    return (x0 + x1) / 2, hz - noon / 90 * hpx

_HOUSES = [(6 + k * 12 + (k % 3), 4 + (k * 7) % 5, k) for k in range(14)]
def draw_tromso(img, T):
    i = day_i(T); h = HT[i]; a = np.array(img)
    hz = HZ; dl = min(1, h / 10)
    sky(a, Y0, hz + 1, mixc(NIGHT_TOP, DAY_TOP, dl), mixc(NIGHT_BOT, DAY_BOT, dl))
    img = Image.fromarray(a); d = ImageDraw.Draw(img)
    if h == 0:                                                        # aurora curtains during the polar night
        for s in range(60):
            sx, sy = (s * 37) % AW, Y0 + 2 + (s * 53) % 100
            if (s + int(T * 4)) % 5: d.point((sx, sy), fill=(220, 226, 255))
        for c in range(3):
            for x in range(0, AW):
                yy = Y0 + 26 + 10 * c + 10 * math.sin(x / 15 + T * 1.6 + c) + 4 * math.sin(x / 6 - T * 2.3)
                ln = 14 + 9 * math.sin(x / 10 + T + c * 2)
                if (x + c) % 2 == 0: d.line([x, yy, x, yy + ln], fill=mixc(NIGHT_TOP, AUR[c], 0.6 - 0.15 * c))
    mt = mixc((50, 60, 92), (120, 136, 170), dl)
    d.polygon([(0, hz), (0, hz - 12), (22, hz - 20), (40, hz - 9), (62, hz - 24), (90, hz - 7), (118, hz - 19), (150, hz - 6), (180, hz - 16), (180, hz)], fill=mt)
    snow = DAYS[i].month in (11, 12, 1, 2, 3, 4) or (DAYS[i].month == 10 and DAYS[i].day > 20) or (DAYS[i].month == 5 and DAYS[i].day < 10)
    for px, py in [(22, hz - 20), (62, hz - 24), (118, hz - 19)]:
        d.polygon([(px - 6, py + 6), (px, py), (px + 6, py + 6)], fill=(236, 240, 250))
    sp = sun_path(d, 6, AW - 6, hz, 210, h, DEC[i], LAT_T, mixc((200, 120, 80), (255, 236, 170), dl))
    if sp:
        sx, sy = sp
        if sy < hz - 2: d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=SUN)
    water = mixc((20, 30, 64), (90, 150, 200), dl)
    d.rectangle([0, hz, AW, hz + 22], fill=water)
    for x in range(0, AW, 6): d.point((x + int(T * 6) % 6, hz + 6 + (x // 6) % 4 * 4), fill=mixc(water, WHITE, 0.3))
    d.line([14, hz + 3, 166, hz + 3], fill=mixc((80, 80, 90), (220, 220, 220), dl))   # the bridge
    for x in range(24, 166, 24): d.line([x, hz + 3, x, hz + 20], fill=mixc((80, 80, 90), (200, 200, 200), dl))
    g0 = hz + 22
    d.rectangle([0, g0, AW, Y1], fill=(240, 244, 250) if snow else (96, 140, 84))
    dark = h < 6
    for hx, hh, k in _HOUSES:
        col = [(200, 70, 60), (230, 200, 120), (90, 120, 170), (240, 240, 230)][k % 4]
        yb = g0 + 52
        d.rectangle([hx, yb - 12 - hh, hx + 10, yb], fill=col)
        d.polygon([(hx - 1, yb - 12 - hh), (hx + 5, yb - 18 - hh), (hx + 11, yb - 12 - hh)], fill=(60, 50, 60))
        d.rectangle([hx + 3, yb - 8 - hh // 2, hx + 5, yb - 6 - hh // 2], fill=(255, 220, 120) if dark else (60, 70, 90))
    return img

def graph(c, T):
    W = c.t; x0, x1, yb, yt = 40, 330, 630, 590
    W.rectangle([16, 540, 344, 636], fill=HUDBG)
    text(W, 180, 546, "EVERY NOTE = ONE DAY OF SUNLIGHT", fill=HUDINK, align="c")
    for hh in (0, 12, 24):
        y = yb - hh / 24 * (yb - yt); W.rectangle([x0, y, x1, y], fill=mixc(HUDBG, HUDINK2, 0.4))
    text(W, 36, yt - 6, "24H", fill=HUDINK2, align="r"); text(W, 36, yb - 14, "0H", fill=HUDINK2, align="r")
    k = day_i(T)
    for i in range(0, k + 1):
        x = x0 + (x1 - x0) * i / (N - 1); y = yb - HT[i] / 24 * (yb - yt)
        W.rectangle([x, y - 1, x, y], fill=GOLD2 if HT[i] >= 24 else CORAL)
    x = x0 + (x1 - x0) * day_f(T) / (N - 1); W.rectangle([x, yt - 2, x + 1, yb], fill=HUDINK)

def counter(c, T):
    """big counter 0 H -> 24 H with a gauge (angle B: the counter climbs from night to day)"""
    W = c.t; i = day_i(T); h = HT[i]; age = T - tday(i)
    y = 448 if COUNTER == "bottom" else 50
    W.rectangle([16, y, 344, y + 84], fill=HUDBG); W.rectangle([16, y, 19, y + 84], fill=CORAL if h < 24 else GOLD2)
    text(W, 28, y + 3, "TROMSO, NORWAY  69.6° N", fill=HUDINK2)
    big = "NO SUNRISE" if h == 0 else "NO SUNSET" if h >= 24 else hm(h)
    col = (CORAL if h < 24 else GOLD2) if 0 <= age < 0.06 else HUDINK
    text(W, 28, y + 20, big, size=40, fill=col)
    text(W, 336, y + 26, "OF DAYLIGHT" if 0 < h < 24 else "24 H OF SUN" if h else "0 H OF SUN", fill=HUDINK2, align="r")
    gx0, gx1, gy = 28, 332, y + 66                                   # gauge 0 H .. 24 H
    W.rectangle([gx0, gy, gx1, gy + 7], fill=mixc(HUDBG, HUDINK2, 0.35))
    if h > 0: W.rectangle([gx0, gy, gx0 + (gx1 - gx0) * h / 24, gy + 7], fill=GOLD2 if h >= 24 else CORAL)
    W.rectangle([(gx0 + gx1) / 2, gy - 2, (gx0 + gx1) / 2, gy + 9], fill=HUDINK2)

def banner_box(W, yb, tt, sub, big, a, col=CORAL):
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    hgt = (62 if big else 42) if sub else (44 if big else 24)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + hgt], fill=HUDBG)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=HUDINK, align="c")
        if sub and a > 0.25: text(W, 180, yb + 40, sub, fill=col, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=HUDINK, align="c")
        if sub and a > 0.25: text(W, 180, yb + 21, sub, fill=col, align="c")

Z0, Z1, F0, F1 = ZERO[0], ZERO[-1], FULL[0], FULL[-1]
BY = 292 if COUNTER == "bottom" else 300      # banners over the fjord / snow, under the sun's path
def short(d): return fdate(d)[:-5]
BANNERS = [   # t0, t1, title, sub, big, colour, y
    (tday(IF0), tday(IF1), f"-{abs(R_FALL):.1f} MIN EVERY DAY", f"{short(DAYS[IF0])} TO {short(DAYS[IF1])}", False, CORAL, BY),
    (tday(Z0) + 0.02, tday(Z0) + 2.4, "48 DAYS OF NIGHT", f"{short(DAYS[Z0])} TO {short(DAYS[Z1])}", True, CORAL, BY),
    (tday(Z0) + 3.0, tday(Z1) + D, "THE SUN NEVER RISES", "ONLY THE AURORA", False, CORAL, BY),
    (tday(Z1 + 1), tday(Z1 + 1) + 1.6, "THE SUN IS BACK", f"{short(DAYS[Z1 + 1])}: {hm(HT[Z1 + 1])}", False, GOLD2, BY),
    (tday(IS0), tday(IS1), f"+{R_SPR:.1f} MIN EVERY DAY", f"{short(DAYS[IS0])} TO {short(DAYS[IS1])}", False, GOLD2, BY),
    (tday(F0) + 0.02, tday(F0) + 2.4, "68 DAYS OF DAY", f"{short(DAYS[F0])} TO {short(DAYS[F1])}", True, GOLD2, BY),
    (tday(F0) + 3.0, tday(F1) + D, "THE SUN NEVER SETS", "ONE LONG NOTE", False, GOLD2, BY),
    (tday(N - 1), T_END, "BACK TO 12 H", f"{short(DAYS[-1])}: {hm(HT[-1])}", False, GOLD2, BY),
]
def banner(c, T):
    for t0, t1, tt, sub, big, col, y in BANNERS:
        if t0 <= T < t1: banner_box(c.t, y, tt, sub, big, T - t0, col)

def hud(c, T):
    W = c.t; i = day_i(T)
    W.rectangle([16, 14, 344, 40], fill=HUDBG); W.rectangle([16, 40, 344, 41], fill=HUDINK)
    text(W, 24, 17, "DAYLIGHT, SUNRISE TO SUNSET", fill=HUDINK2)
    text(W, 336, 17, fdate(DAYS[i]), fill=HUDINK, align="r")

def frame(T):
    set_theme(theme_at(light_level(T)))
    a = np.zeros((AH, AW, 3), np.uint8); a[:] = FRAME
    img = draw_tromso(Image.fromarray(a), T)
    c = Ctx(np.array(img))
    counter(c, T); graph(c, T)
    return c

def sc_days(name):
    def f(t):
        T = START[name] + t; c = frame(min(T, tday(N - 1))); W = c.t
        if T < 3.4:
            y = 140 if COUNTER == "top" else 50
            W.rectangle([16, 14, 344, 41], fill=HUDBG); W.rectangle([16, 14, 344, 16], fill=HUDINK)
            text(W, 180, 19, "EVERY NOTE = ONE DAY OF SUNLIGHT", fill=HUDINK2, align="c")
            W.rectangle([16, y, 344, y + 92], fill=HUDBG); W.rectangle([16, y, 344, y + 2], fill=CORAL)
            text(W, 28, y + 6, "48 DAYS OF NIGHT.", size=40, fill=CORAL)
            if T > 0.6: text(W, 28, y + 46, "THEN 68 DAYS OF DAY.", size=40, fill=GOLD2)
        else:
            hud(c, T)
        banner(c, T)
        return c
    return f

def sc_outro(t):
    T = T_END + t; c = frame(tday(N - 1)); W = c.t
    W.rectangle([16, 40, 344, 330], fill=HUDBG); W.rectangle([16, 40, 344, 42], fill=GOLD)
    text(W, 180, 52, "ONE YEAR IN TROMSO, NORWAY", fill=HUDINK2, align="c")
    if t > 0.2:
        text(W, 180, 76, "48 DAYS", size=40, fill=CORAL, align="c")
        text(W, 180, 116, "WITHOUT A SUNRISE", fill=HUDINK, align="c")
    if t > 0.8:
        text(W, 180, 146, "68 DAYS", size=40, fill=GOLD2, align="c")
        text(W, 180, 186, "WITHOUT A SUNSET", fill=HUDINK, align="c")
    if t > 1.5: text(W, 180, 222, "WHICH ONE COULD YOU HANDLE?", fill=CORAL, align="c")
    if t > 2.0:
        text(W, 180, 260, "DATA: SUNRISE-SUNSET COMPUTED (NOAA", fill=HUDINK2, align="c")
        text(W, 180, 278, "ALGORITHM), CHECKED: VISITTROMSO.NO,", fill=HUDINK2, align="c")
        text(W, 180, 296, "TIMEANDDATE.COM. SEA HORIZON.", fill=HUDINK2, align="c")
    return c

SCENEFN = {n: sc_days(n) for n in NAMES[:-1]}; SCENEFN["outro"] = sc_outro

def compose_light(c):
    art = np.array(c.art); big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt); tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

MOMENTS = [tday(Z0), tday(Z1 + 1), tday(F0)]
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    fr = compose_light(SCENEFN[name](t))
    for m in MOMENTS:
        if 0 <= T - m < 0.2:
            a = T - m; s = int(round(6 * FXK * math.exp(-a / 0.06) * math.sin(a * 90))); fr = np.roll(fr, s, axis=0)
    if name == "outro":
        f = ease((t - (DUR[name] - 0.8)) / 0.8)
        if f > 0: fr = (fr * (1 - f) + np.array(FRAME) * f).astype(np.uint8)
    if name == "a":
        f = 1 - ease(t / 0.2)
        if f > 0: fr = (fr * (1 - f) + np.array(CREAM) * f).astype(np.uint8)
    return fr

# ================= audio (rework mood A · Marimba claire, 84 BPM) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    def lowpass(x, fc, o=2):
        b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
    def highpass(x, fc, o=2):
        b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
    def env(n, a, dec):
        t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t * dec)
    def marimba(f, dur, dec):
        n = int(dur * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 25)) * env(n, .001, dec)
    def softsynth(f, dur, dec, a=.02):
        n = int(dur * SR); t = np.arange(n) / SR
        s = sum(np.sin(2 * np.pi * f * d * t) for d in (.997, 1.003)) / 2 + .15 * np.sin(2 * np.pi * 2 * f * t)
        return s * env(n, a, dec)
    rng = np.random.RandomState(4)
    n = int((TOTAL + 2.0) * SR); L = np.zeros(n); R = np.zeros(n)
    def put(t, x, pan=0.0):
        i = int(t * SR)
        if i >= n or i < 0: return
        j = min(n, i + len(x)); L[i:j] += x[:j - i] * (1 - pan) ** .5 * .9; R[i:j] += x[:j - i] * (1 + pan) ** .5 * .9
    for t, k, kw in EV:
        v = kw.get("v", .2)
        if k == "hat":
            m_ = int(.05 * SR); put(t, v * highpass(rng.randn(m_), 5000) * np.exp(-np.arange(m_) / SR * 60), -.3)
        elif k == "bass":
            put(t, v * lowpass(softsynth(mtof(kw["m"]), kw["d"], 1.2, .05), 500))
        elif k == "quito":
            put(t, v * softsynth(mtof(kw["m"]), .3, 8), .25)
        elif k == "marimba":
            put(t, v * marimba(mtof(kw["m"]), .6, max(3.0, 12 - 1.2 * min(kw["h"], 8))), -.25)
        elif k == "tick":
            put(t, v * marimba(mtof(kw["m"]), .15, 30), -.25)
        elif k == "hold":
            d = kw["d"]; m_ = int((d + .6) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .3) * np.clip((d + .5 - tt) / .5, 0, 1)
            x = softsynth(mtof(kw["m"]), d + .6, 0, .3) * (1 + .15 * np.sin(2 * np.pi * 4.5 * tt))
            put(t, v * lowpass(x * e, 3000), -.25)
        elif k == "aurora":
            d = kw["d"]; m_ = int((d + 1.2) * SR); tt = np.arange(m_) / SR
            a = sum(np.sin(2 * np.pi * mtof(mm) * tt + 2 * np.sin(2 * np.pi * .3 * tt + mm)) for mm in (81, 85, 88)) / 3
            e = np.clip(tt / 1.2, 0, 1) * np.clip((d + 1.0 - tt) / 1.0, 0, 1)
            put(t, v * a * (.6 + .4 * np.sin(2 * np.pi * .7 * tt)) * e)
        elif k == "pad":
            d = kw["d"]; m_ = int((d + .5) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / .4) * np.clip((d + .4 - tt) / .6, 0, 1)
            put(t, v * sum(softsynth(mtof(kw["m"] + iv), d + .5, 0, .4) for iv in (0, 7, 12, 16)) / 2 * e)
    def reverb(x, mix=.35):
        out = x.copy()
        for dl, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16), (.613, .11), (.83, .07)]:
            k_ = int(dl * SR); out[k_:] += g * .6 * x[:-k_]
        return (1 - mix) * x + mix * lowpass(out, 4000)
    L = reverb(np.tanh(L * 1.4) / 1.4); R = reverb(np.roll(np.tanh(R * 1.4) / 1.4, int(.011 * SR)))
    tt = np.arange(n) / SR; fade = np.clip((TOTAL - tt) / 1.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max()); st = np.stack([L, R], 1) / mx * .89
    wavfile.write(path, SR, (st * 32767).astype(np.int16)); print(path, round(n / SR, 2), "s")

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    nf = int(round((START[name] + dur) * FPS)) - int(round(START[name] * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    f0 = int(round(START[name] * FPS))
    for f in range(nf): p.stdin.write(render_frame(idx, max(0.0, (f0 + f) / FPS - START[name])).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio":
        render_audio(out); sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(DUR[n], 2) for n in NAMES}, Counter(k for _, k, _ in EV))
        print("silent", ZERO[0], DAYS[ZERO[0]], round(tday(ZERO[0]), 2), "->", DAYS[ZERO[-1]], "| midnight sun", DAYS[FULL[0]], round(tday(FULL[0]), 2), "->", DAYS[FULL[-1]], "| rates", round(R_FALL, 1), round(R_SPR, 1))
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(min(6, os.cpu_count() or 3)) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
