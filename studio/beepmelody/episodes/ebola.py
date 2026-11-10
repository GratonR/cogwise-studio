"""BEEPMELODY — 1976: A RIVER CALLED EBOLA. Every human Ebola disease outbreak since 1976 (53 events, CDC + WHO,
2026 DRC Bundibugyo outbreak to 3 Nov 2026, WHO DON625). One outbreak = one note, pitch = log(cases),
species = timbre (Zaire: muted bell, Sudan: low hollow tone, Bundibugyo / Tai Forest: glassy tone).
Mood chosen in co-pilot step 2: dark & slow, 64 BPM, D minor drone, heartbeat on every beat, muted bells.
Picture: dark map of Africa (outbreaks as red pulses), log chart of cases by year, sober palette.

    python3 ebola.py info out | preview out <scene>:<s> ... | at out <T> ... | audio out/music.wav | render out | final out x.mp4
"""
import sys, os, math, random, subprocess, csv
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, text, ease, lerp)
from pi import Ctx, warp

FXK = float(os.environ.get("PI_FX", "0.8"))

# ================= data =================
REC = list(csv.DictReader(open(os.path.join(HERE, "ebola.csv"))))
# map position of each outbreak (approx. epicentre; out-of-frame ones are pinned to the map edge)
POS = {
    ("1976", "Sudan"): (4.6, 28.3), ("1976", "DR Congo (Yambuku)"): (2.8, 22.2), ("1976", "United Kingdom (lab)"): (51.1, -1.7),
    ("1977", "DR Congo"): (2.9, 19.3), ("1979", "Sudan"): (4.6, 28.3), ("1994", "Gabon"): (1.4, 12.8),
    ("1994", "Côte d'Ivoire"): (5.8, -7.1), ("1995", "DR Congo (Kikwit)"): (-5.0, 18.8), ("1996", "Gabon (Jan-Apr)"): (0.8, 13.3),
    ("1996", "Gabon (Jul-Dec)"): (-0.1, 11.9), ("1996", "South Africa"): (-26.2, 28.0), ("1996", "Russia (lab)"): (56.3, 38.1),
    ("2000", "Uganda (Gulu)"): (2.8, 32.3), ("2001", "Gabon"): (1.0, 13.9), ("2001", "Rep. of the Congo"): (0.4, 14.7),
    ("2003", "Rep. of the Congo (Jan-Apr)"): (-0.1, 14.5), ("2003", "Rep. of the Congo (Nov-Dec)"): (0.4, 14.7),
    ("2004", "Sudan"): (4.6, 28.4), ("2004", "Russia (lab)"): (54.9, 83.2), ("2005", "Rep. of the Congo"): (0.0, 14.9),
    ("2007", "DR Congo"): (-5.2, 21.3), ("2007", "Uganda"): (0.7, 30.1), ("2008", "DR Congo"): (-5.0, 21.0),
    ("2011", "Uganda"): (0.8, 32.5), ("2012", "Uganda (Jun)"): (0.8, 31.1), ("2012", "DR Congo"): (2.8, 27.6),
    ("2012", "Uganda (Nov)"): (0.8, 32.5), ("2014", "Guinea, Liberia, Sierra Leone"): (8.6, -10.1), ("2014", "Nigeria"): (6.5, 3.4),
    ("2014", "Senegal"): (14.7, -17.4), ("2014", "Mali"): (12.6, -8.0), ("2014", "United States"): (32.8, -96.8),
    ("2014", "Spain"): (40.4, -3.7), ("2014", "United Kingdom"): (55.9, -4.3), ("2014", "Italy"): (39.2, 9.1),
    ("2014", "DR Congo"): (-0.3, 20.9), ("2017", "DR Congo"): (3.4, 23.9), ("2018", "DR Congo (Equateur)"): (-0.75, 18.1),
    ("2018", "DR Congo + Uganda (Kivu)"): (0.5, 29.5), ("2020", "DR Congo (Equateur)"): (0.05, 18.3),
    ("2021", "DR Congo (Feb-May)"): (0.1, 29.3), ("2021", "Guinea"): (7.75, -8.8), ("2021", "DR Congo (Oct-Dec)"): (0.5, 29.5),
    ("2022", "DR Congo (Apr-Jul)"): (0.05, 18.3), ("2022", "DR Congo (Aug-Sep)"): (0.5, 29.5), ("2022", "Uganda"): (0.56, 31.4),
    ("2025", "Uganda"): (0.35, 32.6), ("2025", "DR Congo (Kasai)"): (-4.6, 21.0), ("2026", "Uganda"): (0.35, 32.6),
    ("2026", "France (imported)"): (48.9, 2.3), ("2026", "Kenya"): (-1.3, 36.8), ("2026", "Nigeria (imported)"): (6.5, 3.4),
    ("2026", "DR Congo (ongoing)"): (1.56, 30.25),
}
DISPLAY = {"Guinea, Liberia, Sierra Leone": "GUINEA · LIBERIA · SIERRA LEONE", "DR Congo + Uganda (Kivu)": "DR CONGO + UGANDA · KIVU",
           "DR Congo (ongoing)": "DR CONGO · ITURI (ONGOING)"}
for r in REC:
    r["y"] = int(r["year"]); r["c"] = int(r["cases"]); r["dd"] = int(r["deaths"])
    r["la"], r["lo"] = POS[(r["year"], r["label"])]
    r["name"] = DISPLAY.get(r["label"], r["label"].upper())
N = len(REC)

# ================= palette (dark, sober) =================
BG = (14, 14, 20)
INK = (236, 228, 214)
INK2 = (150, 142, 136)
DIM = (86, 80, 82)
SEA = (20, 22, 32)
SEA2 = (24, 26, 38)
LAND = (52, 44, 44)
LAND2 = (78, 64, 60)
RED = (214, 58, 52)
AMBER = (226, 150, 64)
PALE = (240, 196, 196)
TEAL = (110, 186, 176)
if os.environ.get("BM_PALETTE") == "light":                 # co-pilot step 3 variant: paper map
    BG, INK, INK2, DIM = (252, 248, 238), (34, 44, 78), (92, 104, 140), (150, 150, 160)
    SEA, SEA2, LAND, LAND2 = (214, 233, 244), (200, 224, 240), (238, 226, 196), (216, 200, 160)
    RED, AMBER, PALE, TEAL = (204, 52, 48), (214, 130, 30), (150, 70, 160), (40, 140, 130)
SPC = {"Zaire": RED, "Sudan": AMBER, "Bundibugyo": PALE, "Taï Forest": TEAL}
SPNAME = {"Zaire": "ZAIRE VIRUS", "Sudan": "SUDAN VIRUS", "Bundibugyo": "BUNDIBUGYO VIRUS", "Taï Forest": "TAÏ FOREST VIRUS"}

# ================= timeline (64 BPM, on the beat / half-beat) =================
BPM = 64.0
BEAT = 60.0 / BPM
INTRO_B = 4
def gap_beats(i):
    a, b = REC[i - 1], REC[i]
    dy = b["y"] - a["y"]
    if i == N - 1: return 3                         # breath before the ongoing outbreak
    if dy == 0: return 0.5
    if dy >= 10: return 6                          # 1979 -> 1994: 15 years of silence
    if dy >= 3: return 2
    return 1.5
GAPS_B = [gap_beats(i) for i in range(1, N)]
HOLD_B, OUTRO_B = 5, 9
RT = [INTRO_B * BEAT]
for g in GAPS_B: RT.append(RT[-1] + g * BEAT)
T_FINAL = RT[-1]
TOTAL = T_FINAL + (HOLD_B + OUTRO_B) * BEAT
def first_year(y): return next(i for i, r in enumerate(REC) if r["y"] >= y)
I1994, I2014, I2017 = first_year(1994), first_year(2014), first_year(2017)
SC = [("intro", RT[0]), ("early", RT[I1994] - RT[0]), ("return", RT[I2014] - RT[I1994]), ("westafrica", RT[I2017] - RT[I2014]),
      ("recent", T_FINAL + HOLD_B * BEAT - RT[I2017]), ("outro", OUTRO_B * BEAT)]
START, acc_ = {}, 0.0
for n, d in SC: START[n] = acc_; acc_ += d
DUR = dict(SC); NAMES = [n for n, _ in SC]

def rec_index(T):
    k = -1
    for i, t in enumerate(RT):
        if T >= t: k = i
    return k

# ================= music plan =================
SCALE = [50, 53, 55, 57, 60, 62, 65, 67, 69, 72, 74, 77]     # D minor pentatonic-ish, D3..F5
LO, HI = 0.0, math.log10(30000)
def lvl(c): return (math.log10(max(1, c)) - LO) / (HI - LO)
def pitch(i): return SCALE[int(round(lvl(REC[i]["c"]) * (len(SCALE) - 1)))]
CHORDS = [(38, 45, 50), (34, 41, 46), (31, 38, 43), (33, 40, 45)]  # Dm  Bb  Gm  A (drone roots)
EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
def build():
    nb = int(round(TOTAL / BEAT)) + 1
    ev(0.05, "dbell", m=62, v=0.35, sp="Zaire")
    for b in range(nb):
        t = b * BEAT; bar, pos = divmod(b, 4)
        if pos == 0 and t < TOTAL - 0.5: ev(t, "drone", ch=CHORDS[(bar // 2) % 4] if t < T_FINAL else CHORDS[0], d=4 * BEAT, v=0.20)
        if RT[0] - 2 * BEAT <= t < TOTAL - 2 * BEAT:
            k = rec_index(t); loud = 0.0
            if k >= 0 and REC[k]["c"] >= 1000 and t - RT[k] < 6 * BEAT: loud = 0.12
            ev(t, "heart", v=0.30 + loud)
    for i, t in enumerate(RT):
        r = REC[i]
        ev(t, "dbell", m=pitch(i), v=0.30 + 0.35 * lvl(r["c"]), sp=r["species"])
        if r["c"] >= 1000: ev(t, "boom", v=0.30 + 0.25 * (lvl(r["c"]) - 0.6) / 0.4)
    for k, d in enumerate([0, 3, 7, 12]):                      # slow falling chime after the ongoing outbreak
        ev(T_FINAL + (k + 1) * BEAT, "dbell", m=74 - d, v=0.22, sp="Bundibugyo")
    EV.sort(key=lambda e: e[0])
build()
HEARTS = sorted(t for t, k, _ in EV if k == "heart")

# ================= map (Africa, equirectangular) =================
LON0, LON1, LAT0, LAT1 = -20.0, 55.0, 28.0, -28.0
MX0, MX1, MY0 = 0, AW, 94
PXD = (MX1 - MX0) / (LON1 - LON0)
MY1 = MY0 + (LAT0 - LAT1) * PXD
def map_xy(la, lo):
    x = MX0 + (lo - LON0) * PXD; y = MY0 + (LAT0 - la) * PXD
    out = not (MX0 + 2 <= x <= MX1 - 3 and MY0 + 2 <= y <= MY1 - 3)
    return min(MX1 - 4, max(MX0 + 3, x)), min(MY1 - 4, max(MY0 + 3, y)), out
_land = np.load(os.path.join(ENGINE, "..", "geo", "land_clean.npy"))
def _land_at(la, lo):
    iy = int(np.clip((90.0 - la) * 4, 0, 719)); ix = int(np.clip(((lo + 180.0) % 360.0) * 4, 0, 1439))
    return _land[max(0, iy - 1):iy + 2, max(0, ix - 1):ix + 2].mean() > 0.4
def _map_img():
    a = np.zeros((AH, AW, 3), np.uint8); a[:] = BG
    for y in range(int(MY0), int(math.ceil(MY1))):
        la = LAT0 - (y + 0.5 - MY0) / PXD
        for x in range(MX0, MX1):
            lo = LON0 + (x + 0.5 - MX0) / PXD
            a[y, x] = LAND if _land_at(la, lo) else (SEA if (x + y) % 7 else SEA2)
    L = (a == np.array(LAND)).all(-1)
    edge = L & ~(np.roll(L, 1, 0) & np.roll(L, -1, 0) & np.roll(L, 1, 1) & np.roll(L, -1, 1))
    a[edge] = LAND2
    return a
MAP = _map_img()

# ================= chart (year x cases, log) =================
CX0, CX1, CY0, CY1 = 24, 172, 250, 284
def cx(y): return CX0 + (y + 0.5 - 1975.0) / (2027.0 - 1975.0) * (CX1 - CX0)
def cy(c): return CY1 - lvl(c) * (CY1 - CY0)

def fmt(n): return f"{n:,}"

# ================= drawing =================
def ring(d, x, y, r, col): d.ellipse([x - r, y - r, x + r, y + r], outline=col)

def draw_map(c, T):
    c.art = Image.fromarray(MAP.copy()); c.a = ImageDraw.Draw(c.art); d = c.a; W = c.t
    d.line([0, int(MY0) - 1, AW, int(MY0) - 1], fill=DIM); d.line([0, int(MY1), AW, int(MY1)], fill=DIM)
    k = rec_index(T)
    for i in range(k + 1):
        r = REC[i]; x, y, out = map_xy(r["la"], r["lo"]); age = T - RT[i]
        rad = 0.6 + lvl(r["c"]) * 4.2
        col = SPC[r["species"]]
        if age > 2.0: col = tuple(int(v * 0.55 + b * 0.45) for v, b in zip(col, LAND))
        if out:                                              # outside the map: small arrow on the edge
            d.polygon([(x, y - 2), (x - 2, y + 1), (x + 2, y + 1)] if y < MY0 + 6 else [(x - 2, y), (x + 1, y - 2), (x + 1, y + 2)], fill=col)
        elif rad < 1.2: d.point((int(x), int(y)), fill=col); d.point((int(x) + 1, int(y)), fill=col)
        else: d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col)
        if 0 <= age < 1.4:
            span = 5 + lvl(r["c"]) * 26
            for j in range(3):
                a = age - j * 0.16
                if 0 <= a < 1.0: ring(d, x, y, 2 + a / 1.0 * span, INK if a < 0.2 else SPC[r["species"]])
    if k >= 0 and T - RT[k] < 2.2:
        r = REC[k]; x, y, out = map_xy(r["la"], r["lo"])
        lab = r["name"]; tx = int(x * 2); ty = int(y * 2) - 26
        w = 8 * len(lab); tx = max(4 + w // 2, min(356 - w // 2, tx))
        if ty < int(MY0 * 2) + 4: ty = int(y * 2) + 12
        W.rectangle([tx - w // 2 - 3, ty - 1, tx + w // 2 + 2, ty + 19], fill=BG)
        text(W, tx, ty, lab, fill=INK, align="c")

def draw_chart(c, T):
    d = c.a; W = c.t; k = rec_index(T)
    d.rectangle([0, int(MY1) + 1, AW, AH], fill=BG)
    for v, lab in ((1, "1"), (100, "100"), (10000, "10K")):
        y = cy(v)
        for x in range(CX0, CX1, 3): d.point((x, int(y)), fill=tuple((a + b) // 2 for a, b in zip(BG, DIM)))
        text(W, CX0 * 2 - 6, int(y * 2) - 10, lab, fill=INK2, align="r")
    d.line([CX0, CY1 + 2, CX1, CY1 + 2], fill=DIM)
    for yr in (1976, 2000, 2026):
        x = cx(yr); d.line([x, CY1 + 2, x, CY1 + 4], fill=DIM)
        text(W, int(x * 2) + (14 if yr == 2026 else 0), int((CY1 + 5) * 2), str(yr), fill=INK2, align="r" if yr == 2026 else "c")
    text(W, CX0 * 2 - 6, int(CY0 * 2) - 30, "CASES PER OUTBREAK (LOG)", fill=INK2)
    for i in range(k + 1):
        r = REC[i]; x = int(round(cx(r["y"]))); y = cy(r["c"]); age = T - RT[i]
        col = SPC[r["species"]] if age < 2.0 else tuple(int(v * 0.6) for v in SPC[r["species"]])
        d.line([x, CY1, x, int(y)], fill=col)
        d.rectangle([x - 1, int(y) - 1, x + 1, int(y) + 1], fill=col if age > 0.15 else INK)
    if 0 <= k < N - 1 and REC[k]["y"] == 1979 and T - RT[k] > 1.2:     # the silence, drawn as it passes
        f = min(1.0, (T - RT[k] - 1.2) / (GAPS_B[k] * BEAT - 1.2))
        x0 = cx(1979.6); x1 = lerp(x0, cx(1993.4), f)
        for x in range(int(x0), int(x1), 2): d.point((x, CY1), fill=INK2)

def hud(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([16, 18, 344, 122], fill=BG); W.rectangle([16, 18, 344, 19], fill=DIM); W.rectangle([16, 121, 344, 122], fill=DIM)
    if k < 0: return
    r = REC[k]; age = T - RT[k]; col = SPC[r["species"]]
    text(W, 28, 22, "CASES", fill=INK2)
    text(W, 28, 44, fmt(r["c"]), size=40, fill=col if age < 0.25 else INK)
    text(W, 28, 92, f"DEATHS {fmt(r['dd'])}" + (" (TO 3 NOV)" if k == N - 1 else ""), fill=INK2)
    text(W, 334, 44, r["year"], size=40, fill=INK, align="r")
    text(W, 334, 92, f"#{k + 1} / {N}", fill=INK2, align="r")
    W.rectangle([16, 128, 344, 172], fill=BG); W.rectangle([16, 128, 19, 172], fill=col)
    n = int(min(60, age * 70))
    text(W, 28, 131, r["name"][:max(0, n)], fill=INK)
    if age > 0.12: text(W, 28, 151, SPNAME[r["species"]], fill=col)

def legend(c, T):
    W = c.t; k = rec_index(T)
    W.rectangle([0, 598, 360, 640], fill=BG); W.rectangle([0, 598, 360, 599], fill=DIM)
    text(W, 10, 600, "EVERY NOTE = ONE OUTBREAK", fill=INK2)
    for j, (sp, lab) in enumerate((("Zaire", "ZAIRE"), ("Sudan", "SUDAN"), ("Bundibugyo", "BUNDIB."), ("Taï Forest", "TAÏ F."))):
        cnt = sum(1 for i in range(k + 1) if REC[i]["species"] == sp)
        x = 16 + j * 86
        W.rectangle([x - 6, 625, x - 1, 630], fill=SPC[sp])
        text(W, x + 2, 617, f"{lab} {cnt}", fill=INK)

def ilab(y, lab): return next(i for i, r in enumerate(REC) if r["year"] == y and r["label"] == lab)
BANNERS = {ilab("1976", "DR Congo (Yambuku)"): ("YAMBUKU · 1976", "THE VIRUS IS NAMED AFTER A NEARBY RIVER", False),
           ilab("1994", "Gabon"): ("15 YEARS OF SILENCE", "THEN IT CAME BACK", False),
           ilab("1995", "DR Congo (Kikwit)"): ("KIKWIT · 315 CASES", "A CITY OUTBREAK", False),
           ilab("2014", "Guinea, Liberia, Sierra Leone"): ("28,610 CASES", "WEST AFRICA 2014-16 · THE BIGGEST", True),
           ilab("2014", "United States"): ("IT CROSSED THE OCEAN", "4 CASES IN THE USA", False),
           ilab("2018", "DR Congo + Uganda (Kivu)"): ("3,470 CASES", "KIVU, DR CONGO · 2018-20", True),
           N - 1: ("STILL GOING", "10,668 CASES · 2ND BIGGEST EVER", True)}
BKEYS = sorted(BANNERS)
I1979 = next(i for i, r in enumerate(REC) if r["y"] == 1979)
def banner(c, T):
    k = rec_index(T); W = c.t; yb = 392
    if k == I1979 and T - RT[k] > 1.0:                     # the silence, counted out loud
        span = RT[k + 1] - RT[k] - 1.0
        yr = min(1993, 1980 + int((T - RT[k] - 1.0) / span * 14))
        W.rectangle([60, yb, 300, yb + 42], fill=BG); W.rectangle([60, yb, 300, yb + 2], fill=DIM)
        text(W, 180, yb + 3, "NO OUTBREAK", fill=INK, align="c")
        text(W, 180, yb + 21, f"1980 ... {yr}", fill=INK2, align="c")
        return
    js = [j for j in BKEYS if j <= k]
    if not js: return
    k = js[-1]; a = T - RT[k]
    nxt = [RT[j] for j in BKEYS if j > k]
    hold = HOLD_B * BEAT if k == N - 1 else min(3.2, (nxt[0] - RT[k] - 0.2) if nxt else 3.2)
    if not (0.1 < a < hold): return
    tt, sub, big = BANNERS[k]
    w = (16 if big else 8) * len(tt) + 30; w = max(w, 8 * len(sub) + 30)
    col = SPC[REC[k]["species"]]
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + (62 if big else 42)], fill=BG)
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 2], fill=col)
    W.rectangle([180 - w / 2, yb + (61 if big else 41), 180 + w / 2, yb + (62 if big else 42)], fill=DIM)
    if big:
        text(W, 180, yb + 4, tt, size=40, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 40, sub, fill=col, align="c")
    else:
        text(W, 180, yb + 3, tt, fill=INK, align="c")
        if sub and a > 0.3: text(W, 180, yb + 21, sub, fill=col, align="c")

def frame_ctx(T):
    c = Ctx(np.zeros((AH, AW, 3), np.uint8))
    draw_map(c, T); draw_chart(c, T); legend(c, T)
    return c

def sc_intro(t):
    T = t; c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 172], fill=BG); W.rectangle([16, 18, 344, 19], fill=DIM); W.rectangle([16, 171, 344, 172], fill=DIM)
    text(W, 28, 26, "1976: A RIVER", size=40, fill=INK)
    if t > 0.4: text(W, 28, 64, "CALLED EBOLA", size=40, fill=RED)
    if t > 1.2: text(W, 28, 112, "EVERY NOTE = ONE OUTBREAK", fill=INK2)
    if t > 1.9: text(W, 28, 140, "MORE CASES = HIGHER NOTE", fill=INK)
    if t > 2.4:
        W.rectangle([60, 392, 300, 434], fill=BG); W.rectangle([60, 392, 300, 394], fill=RED)
        text(W, 180, 395, f"ALL {N} OUTBREAKS IN HUMANS", fill=INK, align="c")
        text(W, 180, 414, "1976 TO 2026", fill=INK2, align="c")
    return c

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = frame_ctx(T); hud(c, T); banner(c, T)
        return c
    return f

def sc_outro(t):
    T = START["outro"] + t
    c = frame_ctx(T); W = c.t
    W.rectangle([16, 18, 344, 330], fill=BG); W.rectangle([16, 18, 344, 20], fill=RED)
    text(W, 180, 28, f"{N} OUTBREAKS", size=40, fill=INK, align="c")
    text(W, 180, 70, "1976 TO 2026", fill=INK2, align="c")
    tot_c = sum(r["c"] for r in REC); tot_d = sum(r["dd"] for r in REC)
    rows = [("BIGGEST", "28,610", "CASES · WEST AFRICA 2014-16"), ("ALL OUTBREAKS", fmt(tot_c), f"CASES · {fmt(tot_d)} DEATHS"),
            ("STILL GOING", "DR CONGO", "BUNDIBUGYO VIRUS · 2026")]
    for j, (a, b, s) in enumerate(rows):
        if t > 0.5 + j * 0.9:
            y = 104 + j * 64
            text(W, 30, y + 6, a, fill=RED); text(W, 330, y - 4, b, size=40, fill=INK, align="r")
            text(W, 330, y + 34, s, fill=INK2, align="r")
    if t > 3.6: text(W, 180, 300, "WHICH NOTE HIT YOU HARDEST?", fill=AMBER, align="c")
    if t > 4.4:
        W.rectangle([10, 512, 350, 597], fill=BG)
        text(W, 180, 522, "DATA: CDC, WHO, ECDC, UKHSA.", fill=INK2, align="c")
        text(W, 180, 542, "CONFIRMED + PROBABLE CASES.", fill=INK2, align="c")
        text(W, 180, 562, "2026 DRC: CONFIRMED, TO 3 NOV 2026", fill=INK2, align="c")
    return c

SCENEFN = {"intro": sc_intro, "early": sc_main("early"), "return": sc_main("return"), "westafrica": sc_main("westafrica"),
           "recent": sc_main("recent"), "outro": sc_outro}

def compose(c):
    art = np.array(c.art)
    big = np.repeat(np.repeat(art, 6, 0), 6, 1)
    tx = np.array(c.txt)
    tb = np.repeat(np.repeat(tx, 3, 0), 3, 1)
    al = tb[..., 3:4].astype(np.float32) / 255
    return (big * (1 - al) + tb[..., :3] * al).astype(np.uint8)

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    random.seed(int(T * 1000))
    c = SCENEFN[name](t)
    fr = compose(c)
    hi = np.searchsorted(HEARTS, T, side="right") - 1
    kp = math.exp(-(T - HEARTS[hi]) / 0.10) if hi >= 0 else 0.0
    z = 1.0 + 0.006 * kp * FXK
    k = rec_index(T); dx = dy = 0.0
    if k >= 0 and REC[k]["c"] >= 1000 and 0 <= T - RT[k] < 0.7:
        a = T - RT[k]; amp = 14 * lvl(REC[k]["c"]) * FXK * math.exp(-a / 0.22)
        dx = amp * math.sin(a * 60); dy = amp * 0.5 * math.cos(a * 45); z = max(z, 1.015)
    if z > 1.0005 or dx or dy: fr = warp(fr, z, dx, dy, z)
    if k >= 0 and 0 <= T - RT[k] < 0.10:
        fr = np.minimum(255, fr.astype(np.int16) + int(26 * FXK * (1 - (T - RT[k]) / 0.10))).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.0)) / 1.0)
        if f > 0: fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.3)
        if f > 0: fr = (fr * (1 - f) + np.array(BG) * f).astype(np.uint8)
    return fr

# ================= audio (mood A: dark & slow) =================
SR = 44100
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def env(n, a, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def render_audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    n = int((TOTAL + 3.0) * SR)
    L = np.zeros(n); R = np.zeros(n); fx = np.zeros(n)
    rng = np.random.default_rng(7)
    def add(buf, i, x):
        j = min(n, i + len(x));
        if i < n: buf[i:j] += x[:j - i]
    def put(t, x, pan=0.0, send=0.0):
        i = int(t * SR)
        add(L, i, x * (1 - pan) ** 0.5 * 0.9); add(R, i, x * (1 + pan) ** 0.5 * 0.9)
        if send: add(fx, i, x * send)
    for t, k, kw in EV:
        v = kw.get("v", 0.3)
        if k == "drone":
            d = kw["d"]; m_ = int((d + 1.2) * SR); tt = np.arange(m_) / SR
            e = np.minimum(1, tt / 1.0) * np.clip((d + 1.2 - tt) / 1.2, 0, 1)
            x = np.zeros(m_)
            for j, m in enumerate(kw["ch"]):
                f = mtof(m); g = (1.0, 0.55, 0.35)[j]
                x += g * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 1.004 * tt + j))
            b, a = butter(2, 520 / (SR / 2)); x = lfilter(b, a, x) * e
            put(t, x * v * 0.5, pan=0.0, send=0.15)
        elif k == "heart":
            for off, g in ((0.0, 1.0), (0.24, 0.62)):
                m_ = int(0.28 * SR); tt = np.arange(m_) / SR
                f = 52 * np.exp(-tt * 9) + 36
                put(t + off, g * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 13) * v)
        elif k == "dbell":
            m_ = int(2.6 * SR); tt = np.arange(m_) / SR; f = mtof(kw["m"]); sp = kw["sp"]
            if sp == "Zaire":
                x = np.sin(2*np.pi*f*tt) + .4*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*6) + .2*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*12)
                b, a = butter(2, 2400 / (SR / 2)); x = lfilter(b, a, x); pan = -0.25
            elif sp == "Sudan":
                x = np.sin(2*np.pi*f/2*tt) + .5*np.sin(2*np.pi*f*tt) + .15*np.sin(2*np.pi*f*1.5*tt)*np.exp(-tt*3); pan = 0.25
            else:
                x = np.sin(2*np.pi*f*tt) + .3*np.sin(2*np.pi*f*3*tt)*np.exp(-tt*8); pan = 0.0
            x = x * env(m_, 0.004, 0.75)
            put(t, x * v * 0.55, pan=pan, send=0.45)
        elif k == "boom":
            m_ = int(2.0 * SR); tt = np.arange(m_) / SR
            ph = 2 * np.pi * np.cumsum(30 + 34 * np.exp(-tt / 0.15)) / SR
            b, a_ = butter(2, 160 / (SR / 2)); nz = lfilter(b, a_, rng.standard_normal(m_)) * env(m_, 0.004, 0.35) * 0.5
            put(t, (np.sin(ph) * env(m_, 0.005, 0.7) + nz) * v, send=0.1)
    def reverb(x):
        out = x.copy()
        for d, g in [(0.083, .5), (0.127, .42), (0.191, .35), (0.263, .28), (0.347, .22), (0.461, .16), (0.613, .11), (0.83, .07), (1.1, .05)]:
            k = int(d * SR); out[k:] += g * 0.7 * x[:-k]
        return out
    b, a = butter(1, 3500 / (SR / 2))
    wet = lfilter(b, a, reverb(fx)) * 0.55
    L += wet; R += np.roll(wet, 400)
    tt = np.arange(n) / SR
    fade = np.clip((TOTAL + 1.0 - tt) / 2.5, 0, 1); L *= fade; R *= fade
    mx = max(np.abs(L).max(), np.abs(R).max())
    st = np.stack([L, R], 1) / mx * 0.89
    wavfile.write(path, SR, (st * 32767).astype(np.int16))
    print(path, round(n / SR, 2), "s")

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
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.LANCZOS).save(f"{out}/{name}_{tt}.png")
    elif mode == "at":
        for x in sys.argv[3:]:
            T = float(x); idx = max(i for i, n in enumerate(NAMES) if START[n] <= T)
            Image.fromarray(render_frame(idx, T - START[NAMES[idx]])).resize((540, 960), Image.LANCZOS).save(f"{out}/t{T:05.1f}.png")
    elif mode == "info":
        from collections import Counter
        print(round(TOTAL, 2), {n: round(d, 2) for n, d in SC}, Counter(k for _, k, _ in EV))
        print([(REC[i]["year"], REC[i]["label"], REC[i]["c"], round(t, 2), pitch(i)) for i, t in enumerate(RT)])
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
