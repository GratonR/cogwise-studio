"""THIS MELODY IS US — human population from 300 000 BC to 2026 on a pixel globe. Every bip = births, every boom = excess deaths."""
import sys, os, math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2
from v2 import (AW, AH, TW, TH, OW, OH, FPS, CREAM, YEL, RED, DIM, GREEN, text, panel, ease, eout, mix, shade, lerp, bg)
import pi as PIM
from pi import Ctx, warp, glitch_frame

FXK = float(os.environ.get("PI_FX", "0.8"))
FINAL = "boom"
STYLE = os.environ.get("POP_STYLE", "v1")
NEON = STYLE == "neon"
CINE = STYLE in ("cine", "neon")
DUCK = REVERB = RICH = True
RISE = False
GLOW = np.zeros((320, 180, 3))
OUTRO_DIGITS = []
RISER_T = None  # set after START
SCALE = [57, 60, 62, 64, 67, 69, 72, 74]   # region -> A minor pentatonic

# ================= geography =================
GW, GH = 720, 360
_land = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "geo", "land_clean.npy"))
LAND = _land.reshape(GH, 2, GW, 2).mean(axis=(1, 3)) > 0.5
LAT = (90 - (np.arange(GH) + 0.5) * 0.5)[:, None] * np.ones((1, GW))
LON = (-180 + (np.arange(GW) + 0.5) * 0.5)[None, :] * np.ones((GH, 1))
LAND &= LAT > -60
def box(la0, la1, lo0, lo1): return (LAT >= la0) & (LAT <= la1) & (LON >= lo0) & (LON <= lo1)

AFR, MENA, EUR, SAS, EAS, SEA, AME, OCE = range(8)
RNAMES = ["AFRICA", "N.AFRICA+M.EAST", "EUROPE+RUSSIA", "SOUTH ASIA", "EAST ASIA", "S.E. ASIA", "AMERICAS", "OCEANIA"]
REG = np.full((GH, GW), -1)
REG[LAND & (LON < -25)] = AME
REG[LAND & (LON >= -25) & (LON < 60) & (LAT < 20)] = AFR
REG[LAND & (LON >= -25) & (LON < 32) & (LAT >= 20) & (LAT < 37)] = MENA
REG[LAND & (LON >= 32) & (LON < 60) & (LAT >= 12) & (LAT < 42)] = MENA
REG[LAND & (LON >= 50) & (LON < 73) & (LAT >= 35) & (LAT < 50)] = MENA
REG[LAND & (LON >= -25) & (LON < 60) & (LAT >= 37) & (REG == -1)] = EUR
REG[LAND & (LON >= 26) & (LON < 45) & (LAT >= 36) & (LAT < 42)] = MENA
REG[LAND & (LON >= 60) & (LAT >= 50)] = EUR
REG[LAND & (LON >= 60) & (LON < 92) & (LAT >= 5) & (LAT < 37) & (REG == -1)] = SAS
REG[LAND & (LON >= 73) & (LON < 155) & (LAT >= 21) & (LAT < 50) & (REG == -1)] = EAS
REG[LAND & (LON >= 92) & (LON < 160) & (LAT >= -11) & (LAT < 21)] = SEA
REG[LAND & (LON >= 110) & (LAT < -11)] = OCE
REG[LAND & (LON >= 130) & (LAT < 0) & (LAT >= -11)] = OCE
REG[LAND & (LON >= 160)] = OCE
REG[LAND & box(18, 23, -161, -154)] = OCE
REG[LAND & (REG == -1)] = EUR

HAB = np.ones((GH, GW))
HAB[box(60, 84, -75, -10)] = 0.003                       # Greenland ice
HAB[np.abs(LAT) > 66] *= 0.06
def eblob(la, lo, sla, slo): return np.exp(-(((LAT - la) / sla) ** 2 + ((LON - lo) / slo) ** 2))
DES = np.maximum.reduce([eblob(23, 8, 6.5, 17), eblob(22, 47, 6, 9), eblob(42, 98, 4.5, 14), eblob(-25, 131, 6, 10),
                         eblob(-23, 20, 4, 4), eblob(28, 62, 4, 7), eblob(38, 60, 4, 8), eblob(-23, -69, 4, 2), eblob(33, -112, 4, 5)])
DES = np.clip(DES * 1.25, 0, 1)
HAB *= 1 - 0.96 * DES
HAB[box(22, 31.5, 30, 33)] = 3.0                          # Nile
HAB[box(55, 72, 60, 180)] *= 0.25                         # Siberia
HAB[box(50, 70, -170, -60)] *= 0.2                        # Canadian north
HAB *= LAND

def gauss(lat, lon, s):
    d2 = (LAT - lat) ** 2 + ((LON - lon) * np.cos(np.radians(lat))) ** 2
    return np.exp(-d2 / (2 * s * s))
HOT = [(8, 3, 2, 5), (9, 39, 2, 3), (-1, 33, 2, 4), (-4, 20, 1, 5), (-26, 28, 1, 4), (12, 8, 1.5, 4),
       (27, 31, 4, 1.5), (33, 44, 3, 3), (33, 36, 2, 2), (39, 33, 2, 3), (33, 52, 1.5, 4), (34, 0, 1.5, 4),
       (42, 13, 2, 3), (47, 2, 2, 4), (51, 10, 2, 4), (52, -1, 1.5, 2), (40, -4, 1.5, 3), (55, 38, 1.5, 4), (52, 20, 1.5, 3),
       (26, 82, 4, 4), (28, 70, 2, 3), (12, 78, 3, 4), (24, 90, 3, 2),
       (35, 114, 4, 4), (30, 115, 4, 4), (30, 104, 2.5, 3), (36, 138, 2, 2), (37, 127, 1.5, 2), (23, 113, 2, 2.5),
       (-7, 110, 3, 2), (16, 106, 2, 3), (15, 101, 2, 3), (13, 122, 1.5, 2), (20, 96, 1.5, 3),
       (19, -99, 3, 3), (-13, -72, 2, 3), (40, -77, 1.5, 4), (-22, -45, 1.5, 4), (36, -90, 1, 5), (5, -74, 1.5, 3),
       (-34, -60, 1, 3), (36, -119, 1, 3), (-34, 150, 1.5, 3), (-6, 145, 1, 3), (-38, 175, 1, 2)]
WH = 0.15 * HAB
for la, lo, a, s in HOT: WH += a * gauss(la, lo, s) * HAB
CITIES = [(35.7, 139.7), (28.6, 77.2), (31.2, 121.5), (23.8, 90.4), (-23.5, -46.6), (30.0, 31.2), (19.4, -99.1), (39.9, 116.4),
          (19.1, 72.9), (34.7, 135.5), (29.6, 106.5), (24.9, 67.0), (-4.3, 15.3), (6.5, 3.4), (41.0, 29.0), (-34.6, -58.4),
          (22.6, 88.4), (14.6, 121.0), (23.1, 113.3), (39.1, 117.2), (31.5, 74.3), (13.0, 77.6), (-22.9, -43.2), (22.5, 114.1),
          (55.8, 37.6), (13.1, 80.3), (4.7, -74.1), (48.9, 2.35), (-6.2, 106.8), (-12.0, -77.0), (13.8, 100.5), (17.4, 78.5),
          (37.6, 127.0), (51.5, -0.1), (35.7, 51.4), (41.9, -87.6), (40.7, -74.0), (34.1, -118.2), (10.8, 106.7), (-8.8, 13.2),
          (-26.2, 28.0), (24.7, 46.7), (33.3, 44.4), (-1.3, 36.8), (9.0, 38.7), (15.6, 32.5), (40.4, -3.7), (52.5, 13.4),
          (-33.9, 151.2), (-37.8, 145.0), (43.7, -79.4), (-33.4, -70.6), (12.0, 8.5), (5.3, -4.0), (-6.8, 39.3), (25.0, 121.5),
          (1.35, 103.8), (41.9, 12.5), (45.5, 9.2), (21.0, 105.8), (33.7, 73.0), (26.9, 80.9), (30.6, 114.3), (32.1, 118.8)]
WC = np.zeros((GH, GW))
for la, lo in CITIES: WC += gauss(la, lo, 0.7)
WC *= LAND

# ---- arrival of Homo sapiens (year, negative = BC) ----
def gdist(la, lo):
    p1, p2 = np.radians(LAT), math.radians(la)
    dl = np.radians(LON - lo)
    c = np.sin(p1) * math.sin(p2) + np.cos(p1) * math.cos(p2) * np.cos(dl)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))
ARR = np.full((GH, GW), 1e9)
africa = LAND & ((REG == AFR) | ((REG == MENA) & (LAT < 33) & (LON < 32)))
ARR[africa] = (-300000 + gdist(5, 37) * 1600)[africa]
eurasia = LAND & ~africa & (REG != AME) & (REG != OCE)
nodes = [(12.6, 43.3, -70000), (22, 55, -66000), (32, 35, -55000), (22, 75, -60000), (15, 100, -56000), (0, 110, -53000),
         (40, 25, -45000), (47, 5, -42000), (54, -2, -40000), (35, 110, -45000), (36, 138, -38000), (55, 90, -38000),
         (65, 140, -30000), (40, 65, -45000), (60, 30, -36000)]
acc = np.full((GH, GW), 1e9)
for la, lo, yr in nodes: acc = np.minimum(acc, yr + gdist(la, lo) * 140)
ARR[eurasia] = acc[eurasia]
sahul = LAND & (REG == OCE) & (LON < 160) & (LAT > -45)
acc = np.minimum(-50000 + gdist(-12, 133) * 120, -50000 + gdist(-6, 145) * 120)
ARR[sahul] = acc[sahul]
amer = LAND & (REG == AME)
acc = np.full((GH, GW), 1e9)
for la, lo, yr in [(65, -160, -16000), (55, -130, -15000), (40, -100, -14000), (15, -90, -13500), (0, -75, -13000), (-41, -73, -12500)]:
    acc = np.minimum(acc, yr + gdist(la, lo) * 60)
ARR[amer] = acc[amer]
ARR[LAND & box(59, 84, -75, -10)] = -2500                  # Greenland (Paleo-Inuit)
ARR[LAND & (LAT < -34) & (LON > 165)] = 1280               # New Zealand
ARR[LAND & box(-26, -12, 43, 51)] = 500                    # Madagascar
ARR[LAND & box(18, 23, -161, -154)] = 1000                 # Hawaii
ARR[LAND & box(63, 67, -25, -13)] = 874                    # Iceland
ARR[~LAND] = 1e9
NOISE = np.random.default_rng(3).random((GH, GW))

# ================= demography =================
WORLD = [(-300000, 0.1), (-70000, 1.0), (-50000, 2.0), (-10000, 4.0), (-8000, 5), (-5000, 5), (-4000, 7), (-3000, 14), (-2000, 27),
         (-1000, 50), (-500, 100), (-200, 150), (1, 230), (200, 250), (400, 210), (541, 210), (549, 195), (600, 200), (800, 224),
         (1000, 275), (1100, 310), (1200, 380), (1300, 432), (1346, 450), (1353, 370), (1400, 370), (1500, 460), (1600, 555),
         (1650, 545), (1700, 610), (1750, 790), (1800, 980), (1804, 1000), (1850, 1260), (1900, 1650), (1910, 1750), (1920, 1860),
         (1927, 2000), (1930, 2070), (1940, 2300), (1950, 2525), (1960, 3000), (1974, 4000), (1987, 5000), (1999, 6000),
         (2011, 7000), (2022, 8000), (2026, 8300)]
WY = np.array([a for a, _ in WORLD], float); WP = np.log(np.array([b for _, b in WORLD], float) * 1e6)
def world_pop(y): return float(np.exp(np.interp(y, WY, WP)))
SHARES = [(-10000, [.25, .10, .12, .15, .14, .08, .12, .04]), (-3000, [.12, .22, .14, .18, .20, .05, .08, .01]),
          (1, [.10, .12, .17, .26, .24, .04, .065, .005]), (1000, [.14, .09, .14, .27, .23, .05, .07, .005]),
          (1346, [.14, .07, .19, .22, .23, .06, .085, .004]), (1353, [.16, .06, .15, .25, .22, .065, .10, .005]),
          (1492, [.17, .06, .17, .23, .21, .06, .13, .004]), (1600, [.17, .06, .19, .25, .27, .06, .02, .003]),
          (1700, [.16, .05, .19, .26, .25, .06, .02, .003]), (1800, [.10, .04, .20, .21, .35, .05, .03, .002]),
          (1900, [.08, .03, .25, .18, .29, .06, .10, .004]), (1950, [.09, .04, .22, .19, .27, .07, .13, .005]),
          (2000, [.13, .06, .12, .23, .25, .08, .14, .005]), (2026, [.185, .07, .09, .25, .20, .085, .125, .006])]
SY = np.array([a for a, _ in SHARES], float); SS = np.array([b for _, b in SHARES], float)
def shares(y):
    s = np.array([np.interp(y, SY, SS[:, r]) for r in range(8)]); return s / s.sum()
def cbr(y): return float(np.interp(y, [1800, 1850, 1900, 1950, 1970, 1990, 2000, 2010, 2020, 2026],
                                   [.045, .040, .037, .037, .032, .026, .022, .020, .0175, .0165]))
CRISES = [  # y0, y1, excess deaths, region weights, title, figure
    (165, 180, 7.5e6, {EUR: .6, MENA: .4}, "ANTONINE PLAGUE", "5-10 M DEAD"),
    (541, 549, 25e6, {MENA: .5, EUR: .5}, "PLAGUE OF JUSTINIAN", "541-549 AD"),
    (1346, 1353, 100e6, {EUR: .4, MENA: .25, EAS: .25, AFR: .1}, "THE BLACK DEATH", "75-200 M DEAD"),
    (1492, 1600, 56e6, {AME: 1.0}, "THE GREAT DYING", "~56 M DEAD - 90%"),
    (1618, 1648, 6e6, {EUR: 1.0}, "THIRTY YEARS' WAR", "4.5-8 M DEAD"),
    (1845, 1850, 1e6, {EUR: 1.0}, "IRISH FAMINE", "~1 M DEAD"),
    (1850, 1864, 25e6, {EAS: 1.0}, "TAIPING REBELLION", "20-30 M DEAD"),
    (1914, 1918, 20e6, {EUR: .8, MENA: .1, AFR: .1}, "WORLD WAR I", "~20 M DEAD"),
    (1918, 1920, 50e6, {AFR: .1, EUR: .2, SAS: .4, EAS: .15, AME: .15}, "1918 FLU", "17-100 M DEAD"),
    (1939, 1945, 75e6, {EUR: .45, EAS: .4, SEA: .1, SAS: .05}, "WORLD WAR II", "70-85 M DEAD"),
    (1959, 1961, 30e6, {EAS: 1.0}, "GREAT CHINESE FAMINE", "15-55 M DEAD"),
    (2020, 2022, 7e6, {AFR: .05, EUR: .3, SAS: .2, EAS: .05, AME: .4}, "COVID-19", "~7 M REPORTED DEATHS")]
# year, lat, lon, title, detail   (dates: Wikipedia / standard references; "~" = approximate)
EVENTS = [
    (-300000, 31.9, -8.9, "JEBEL IRHOUD", "OLDEST HOMO SAPIENS FOSSILS"),
    (-233000, 5.0, 35.9, "OMO KIBISH", "ETHIOPIA ~233 000 YRS AGO"),
    (-73000, -34.4, 21.4, "BLOMBOS CAVE", "ENGRAVED OCHRE ~75 000 YRS AGO"),
    (-70000, 12.6, 43.3, "OUT OF AFRICA", "VIA BAB-EL-MANDEB"),
    (-60000, 22, 75, "SOUTH ASIA", "COASTAL ROUTE EAST"),
    (-50000, -12.4, 132.9, "AUSTRALIA", "BY 65 000-50 000 YRS AGO"),
    (-43000, 42.5, 23.5, "EUROPE", "~45 000 YRS AGO"),
    (-36000, 36.2, 138.2, "JAPAN", "~38 000 YRS AGO"),
    (-14000, 65.5, -165.0, "INTO THE AMERICAS", "VIA BERINGIA, 16 000+ YRS AGO"),
    (-12550, -41.5, -73.2, "MONTE VERDE", "CHILE ~14 500 YRS AGO"),
    (-9500, 36.5, 40.0, "FARMING BEGINS", "FERTILE CRESCENT ~9500 BC"),
    (-7000, 30.5, 112.5, "RICE & MILLET", "CHINA ~7000 BC"),
    (-6800, -5.8, 144.3, "KUK SWAMP", "NEW GUINEA FARMS ~7000 BC"),
    (-6500, 18.0, -99.0, "MAIZE", "MEXICO ~7000 BC"),
    (-4000, 31.3, 45.6, "URUK", "FIRST CITIES ~4000 BC"),
    (-3200, 31.3, 45.6, "WRITING", "CUNEIFORM ~3200 BC"),
    (-3100, 26.0, 32.0, "EGYPT UNIFIED", "~3100 BC"),
    (-2560, 30.0, 31.1, "GREAT PYRAMID", "GIZA ~2560 BC"),
    (-2500, 27.3, 68.1, "INDUS CITIES", "MOHENJO-DARO ~2500 BC"),
    (-1177, 35.0, 30.0, "BRONZE AGE COLLAPSE", "~1177 BC"),
    (-753, 41.9, 12.5, "ROME FOUNDED", "753 BC (BY TRADITION)"),
    (-221, 34.3, 108.9, "QIN UNIFIES CHINA", "221 BC"),
    (-27, 41.9, 12.5, "ROMAN EMPIRE", "27 BC"),
    (165, 41.9, 12.5, "ANTONINE PLAGUE", "165-180 AD"),
    (476, 41.9, 12.5, "FALL OF WESTERN ROME", "476 AD"),
    (541, 41.0, 29.0, "PLAGUE OF JUSTINIAN", "CONSTANTINOPLE 541"),
    (762, 33.3, 44.4, "BAGHDAD FOUNDED", "762 AD"),
    (793, 55.7, -1.8, "VIKING AGE", "LINDISFARNE 793"),
    (1000, 20.8, -156.3, "POLYNESIANS", "REACH HAWAII ~1000-1200"),
    (1100, 30.3, 120.2, "SONG CHINA", "100 MILLION PEOPLE"),
    (1206, 47.9, 106.9, "MONGOL EMPIRE", "1206"),
    (1280, -41.3, 174.8, "NEW ZEALAND", "SETTLED ~1280"),
    (1346, 45.0, 35.4, "THE BLACK DEATH", "CAFFA, CRIMEA 1346"),
    (1348, 48.9, 2.35, "PARIS, LONDON", "1348"),
    (1440, 50.0, 8.3, "PRINTING PRESS", "GUTENBERG ~1440"),
    (1492, 24.0, -74.5, "COLUMBUS", "12 OCT 1492"),
    (1520, 19.4, -99.1, "SMALLPOX", "TENOCHTITLAN 1520"),
    (1545, 19.4, -99.1, "COCOLIZTLI", "MEXICO 1545-1548"),
    (1618, 50.0, 10.0, "THIRTY YEARS' WAR", "1618-1648"),
    (1644, 39.9, 116.4, "MING -> QING", "1644"),
    (1769, 52.5, -1.9, "WATT STEAM ENGINE", "1769"),
    (1796, 51.7, -2.5, "FIRST VACCINE", "JENNER 1796"),
    (1845, 53.3, -8.0, "IRISH FAMINE", "1845-1852"),
    (1850, 32.0, 118.8, "TAIPING REBELLION", "1850-1864"),
    (1913, 49.5, 8.4, "HABER-BOSCH", "FERTILISER FEEDS BILLIONS"),
    (1914, 50.0, 3.0, "WORLD WAR I", "1914-1918"),
    (1918, 39.0, -96.0, "1918 FLU", "WORLDWIDE"),
    (1928, 51.5, -0.17, "PENICILLIN", "FLEMING 1928"),
    (1939, 52.2, 21.0, "WORLD WAR II", "1939-1945"),
    (1957, 45.9, 63.3, "SPUTNIK", "4 OCT 1957"),
    (1959, 34.0, 113.0, "GREAT CHINESE FAMINE", "1959-1961"),
    (1966, 30.9, 75.9, "GREEN REVOLUTION", "HIGH-YIELD CROPS, 1960s"),
    (1969, 28.5, -80.6, "MOON LANDING", "20 JUL 1969"),
    (2020, 30.6, 114.3, "COVID-19", "2020"),
    (2022, 14.6, 121.0, "8 BILLION", "15 NOV 2022 (UN)"),
    (2023, 28.6, 77.2, "INDIA PASSES CHINA", "MOST POPULOUS, 2023")]
def crisis_at(y):
    for c in CRISES:
        if c[0] <= y < c[1]: return c
    return None
def births(y):
    c = crisis_at(y); k = 0.85 if c and c[2] / (c[1] - c[0]) > 5e6 else 1.0
    return world_pop(y) * cbr(y) * k
def excess(y):
    c = crisis_at(y); return c[2] / (c[1] - c[0]) if c else 0.0
def urban(y): return float(np.interp(y, [1700, 1800, 1900, 1950, 2000, 2026], [0.03, 0.07, 0.16, 0.30, 0.47, 0.58]))

REGMASK = [(REG == r) for r in range(8)]
WPOST = [WH * m for m in REGMASK]; WCIT = [WC * m for m in REGMASK]
def density(y):
    occ = ARR <= y
    P = world_pop(y)
    wpre = HAB * occ
    Dpre = P * wpre / max(1e-9, wpre.sum())
    if y < -12000: return Dpre
    s = shares(y); u = urban(y); D = np.zeros((GH, GW))
    for r in range(8):
        w = WPOST[r] * occ; sw = w.sum()
        if sw <= 0: continue
        part = w / sw
        if u > 0.035:
            cw = WCIT[r] * occ; sc = cw.sum()
            if sc > 0: part = (1 - u) * part + u * cw / sc
        D += P * s[r] * part
    if y < -8000:
        k = (y + 12000) / 4000; D = (1 - k) * Dpre + k * D
    return D

# ================= timeline (time-warped per scene) =================
SC = [("intro", 8.0, [(-300000, 0), (-300000, 8.0)]),
      ("africa", 14.0, [(-300000, 0), (-233000, 3.5), (-73000, 11.5), (-70000, 14.0)]),
      ("spread", 22.0, [(-70000, 0), (-60000, 2.6), (-50000, 5.4), (-43000, 8.4), (-36000, 11.0), (-14000, 15.6), (-12550, 18.2), (-10000, 22.0)]),
      ("farming", 16.0, [(-10000, 0), (-9500, 1.6), (-7000, 4.4), (-6800, 6.2), (-6500, 7.9), (-4000, 11.0), (-3200, 13.8), (-3150, 16.0)]),
      ("antiquity", 22.0, [(-3150, 0), (-3100, 0.8), (-2560, 3.4), (-2500, 5.4), (-1177, 8.2), (-753, 10.6), (-221, 13.0), (-27, 15.3),
                           (165, 17.4), (476, 20.6), (500, 22.0)]),
      ("medieval", 18.0, [(500, 0), (541, 0.9), (549, 3.4), (762, 5.4), (793, 7.2), (1000, 9.4), (1100, 11.4), (1206, 13.6), (1280, 16.0), (1340, 18.0)]),
      ("plague", 14.0, [(1340, 0), (1346, 1.4), (1348, 4.2), (1353, 8.8), (1420, 14.0)]),
      ("newworld", 18.0, [(1420, 0), (1440, 1.4), (1492, 3.8), (1520, 6.4), (1545, 8.8), (1600, 11.4), (1618, 12.6), (1644, 15.2), (1700, 18.0)]),
      ("industry", 16.0, [(1700, 0), (1769, 2.4), (1796, 4.8), (1804, 6.6), (1845, 9.2), (1850, 10.8), (1864, 13.2), (1900, 16.0)]),
      ("wars", 18.0, [(1900, 0), (1913, 1.6), (1914, 3.0), (1918, 5.6), (1920, 7.6), (1928, 9.2), (1939, 11.0), (1945, 15.0), (1950, 18.0)]),
      ("boom", 26.0, [(1950, 0), (1957, 1.8), (1959, 3.4), (1961, 5.6), (1966, 7.4), (1969, 9.0), (1974, 10.8), (1987, 13.2), (1999, 15.6),
                      (2011, 18.0), (2020, 20.0), (2022, 22.6), (2023, 24.2), (2026, 26.0)]),
      ("outro", 12.0, [(2026, 0), (2026, 12.0)])]
SHORTD = {"intro": 3.2, "africa": 3.4, "spread": 5.2, "farming": 3.6, "antiquity": 5.0, "medieval": 4.0, "plague": 4.2,
          "newworld": 4.6, "industry": 4.0, "wars": 5.0, "boom": 8.2, "outro": 5.4}
SC = [(n, SHORTD[n], [(y, x * SHORTD[n] / d) for y, x in a]) for n, d, a in SC]
KEEP = {"JEBEL IRHOUD", "BLOMBOS CAVE", "OUT OF AFRICA", "AUSTRALIA", "EUROPE", "INTO THE AMERICAS", "FARMING BEGINS",
        "RICE & MILLET", "WRITING", "GREAT PYRAMID", "ROMAN EMPIRE", "FALL OF WESTERN ROME", "MONGOL EMPIRE", "THE BLACK DEATH",
        "PRINTING PRESS", "COLUMBUS", "SMALLPOX", "WATT STEAM ENGINE", "FIRST VACCINE", "HABER-BOSCH", "WORLD WAR I",
        "PENICILLIN", "WORLD WAR II", "MOON LANDING", "8 BILLION", "INDIA PASSES CHINA", "POLYNESIANS"}
EVENTS = [e for e in EVENTS if e[3] in KEEP]
START, acc_ = {}, 0.0
for n, d, _ in SC: START[n] = acc_; acc_ += d
TOTAL = acc_
DUR = {n: d for n, d, _ in SC}; ANCH = {n: a for n, _, a in SC}
NAMES = [n for n, _, _ in SC]
RISER_T = START["boom"] + 7.3
TITLES = {"intro": "THIS MELODY IS US", "africa": "HOMO SAPIENS", "spread": "OUT OF AFRICA", "farming": "FARMING",
          "antiquity": "ANTIQUITY", "medieval": "MIDDLE AGES", "plague": "THE BLACK DEATH", "newworld": "NEW WORLDS",
          "industry": "INDUSTRY", "wars": "WARS & PANDEMICS", "boom": "THE BOOM", "outro": "TODAY"}
def scene_at(T):
    for n, d, _ in SC:
        if START[n] <= T < START[n] + d: return n
    return NAMES[-1]
def year_at(T):
    n = scene_at(T); t = T - START[n]; a = ANCH[n]
    return float(np.interp(t, [x for _, x in a], [y for y, _ in a]))

def bip_rate(y): return min(52, 0.9 * (births(y) / 1.5e4) ** 0.47)
def bomb_rate(y): e = excess(y); return 0 if e <= 0 else min(70, 1.6 * (e / 1.5e4) ** 0.45)

def bpm(T):
    pts = [(0, 84), (START["spread"], 88), (START["farming"], 94), (START["antiquity"], 100), (START["medieval"], 104),
           (START["plague"], 104), (START["newworld"], 108), (START["industry"], 114), (START["wars"], 118), (START["boom"], 122),
           (START["outro"] - 0.5, 134), (START["outro"], 84), (TOTAL, 84)]
    return float(np.interp(T, [a for a, _ in pts], [b for _, b in pts]))
def beat_times(T):
    out, t = [], 0.0
    while t < T: out.append(t); t += 60 / bpm(t)
    return out

EV = []
def ev(t, kind, **kw): EV.append((t, kind, kw))
SCH = {"bips": [], "bombs": []}
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
DARK = [(50, 53, 57), (46, 50, 53), (45, 48, 52), (52, 56, 59)]
KICKS, SNARES, GL = [], [], []
MILES = []

def sample_cells(D, n, rng, mask=None):
    w = (D * mask).ravel() if mask is not None else D.ravel()
    s = w.sum()
    if s <= 0 or n <= 0: return []
    idx = rng.choice(w.size, size=n, p=w / s)
    return [(int(i // GW), int(i % GW)) for i in idx]

EVT = []   # (T, event)
def build():
    rng = np.random.default_rng(11)
    beats = beat_times(TOTAL)
    slots = []
    for b in beats:
        bl = 60 / bpm(b); slots += [b + k * bl / 8 for k in range(8)]       # 32nd-note grid
    accb = accd = 0.0
    for si in range(len(slots) - 1):
        T = slots[si]; dt = slots[si + 1] - T; y = year_at(T); sc = scene_at(T)
        if sc == "outro":
            to = T - START["outro"]
            rb = 4.0 * max(0, 1 - to / 2.5) + (40 if 3.4 < to < 3.45 else 0)
        else:
            rb = bip_rate(y)
        accb += rb * dt; nb = min(4, int(accb)); accb -= int(accb)
        rd = bomb_rate(y) if sc != "outro" else 0
        accd += rd * dt; nd = min(3, int(accd)); accd -= int(accd)
        if (nb or nd) and si % 1 == 0:
            D = density(y)
            for k, (i, j) in enumerate(sample_cells(D, nb, rng)):
                SCH["bips"].append((T, i, j)); ev(T, "bip", r=int(REG[i, j]), rate=rb, lon=float(LON[i, j]), pl=math.log10(world_pop(y)))
            if nd:
                c = crisis_at(y); m = np.zeros((GH, GW))
                for r, wgt in c[3].items(): m += REGMASK[r] * wgt
                for k, (i, j) in enumerate(sample_cells(D, nd, rng, m)):
                    SCH["bombs"].append((T, i, j)); ev(T, "bomb", rate=rd)
    SCH["bips"].sort(); SCH["bombs"].sort()
    # milestones / crises / events by scanning frames
    prev_y = None
    for f in range(int(round(TOTAL * FPS))):
        T = f / FPS; y = year_at(T)
        if prev_y is not None:
            for b, yy in enumerate([1804, 1927, 1960, 1974, 1987, 1999, 2011, 2022], 1):
                if prev_y < yy <= y: MILES.append((T, b, yy)); ev(T, "chime", lvl=min(5, b - 1)); ev(T, "kickhit")
            for c in CRISES:
                if prev_y < c[0] <= y and c[2] / (c[1] - c[0]) > 1e6: ev(T, "crisis")
            for e in EVENTS:
                if prev_y < e[0] <= y or (f == 1 and e[0] <= y): EVT.append((T, e)); ev(T, "chime", lvl=2)
        prev_y = y
    drums_and_glitches()

def drums_and_glitches():
    E = START["boom"]
    for bi, bt in enumerate(beat_times(START["outro"])):
        sc = scene_at(bt); bl = 60 / bpm(bt); pos = bi % 4; y = year_at(bt)
        crisis = crisis_at(y) is not None and excess(y) > 2e6
        prog = DARK if crisis else CHORDS
        ch = prog[(bi // 4) % 4]; root = ch[0] - 12
        early = sc in ("intro", "africa", "spread")
        if early:
            if pos % 2 == 0 and sc != "intro": ev(bt, "kick", v=0.30); ev(bt + bl * 0.28, "kick", v=0.20)
            if sc == "spread": ev(bt + bl / 2, "hat", v=0.03, open=False)
        elif crisis:
            if pos == 0: ev(bt, "kick", v=0.45)
            if pos == 2: ev(bt, "kick", v=0.3)
            if sc == "wars":
                for h in range(4): ev(bt + h * bl / 4, "snare", v=0.05 + 0.03 * (h % 2))
        else:
            ev(bt, "kick", v=0.45 if sc != "farming" else 0.36)
            if sc not in ("farming",) and pos in (1, 3): ev(bt, "snare", v=0.19)
            if sc == "boom" and bt > E + 5.6: ev(bt + bl / 2, "kick", v=0.3)
            if sc == "boom" and bt > E + 7.35:
                for h in range(4): ev(bt + h * bl / 4, "snare", v=0.06 + 0.12 * h / 3)
        if not early or sc == "spread":
            sub = 4 if sc in ("industry", "boom") else 2
            for h in range(sub):
                if early: break
                ev(bt + h * bl / sub, "hat", v=0.035 if h % 2 else 0.045, open=(h == sub // 2 and not crisis))
        for h in range(2):
            if (sc in ("intro", "africa")) and h == 1: continue
            m = root + (12 if (pos * 2 + h) % 4 == 3 and not crisis else 0)
            ev(bt + h * bl / 2, "bass", m=m, d=bl / 2 * 0.9, v=0.17 if not early else 0.11)
        if pos == 0: ev(bt, "pad", ch=ch, d=bl * 4)
    for t, k, kw in EV:
        if k in ("kick", "kickhit") and (k == "kickhit" or kw["v"] >= 0.36): KICKS.append(t)
        if k == "snare" and kw["v"] > 0.15: SNARES.append(t)
    KICKS.sort(); SNARES.sort()
    def bl_at(t): return 60 / bpm(t)
    def T_of(year):
        for f in range(int(TOTAL * FPS)):
            if year_at(f / FPS) >= year: return f / FPS
        return TOTAL
    for yr in (1346, 1492, 1914, 1939):
        t0 = T_of(yr); GL.append((t0 - 0.2, 0.2, "stutter", bl_at(t0) / 4))
    GL.append((T_of(1348) + 0.4, 0.2, "crush", 0))
    GL.append((T_of(1942), 0.2, "crush", 0))
    GL.append((START["boom"] + 7.0, 0.14, "stutter", bl_at(START["boom"] + 7.0) / 8))
    GL.append((START["outro"] - 0.45, 0.45, "tapestop", 0))
    GL.sort()

build()
EV.sort(key=lambda e: e[0])
BIPT = np.array([b[0] for b in SCH["bips"]]); BOMT = np.array([b[0] for b in SCH["bombs"]])
EVTT = np.array([e[0] for e in EVT])

# ================= rendering =================
def build_cam():
    cam = [(0.0, 120, 10, 60), (2.0, 40, 8, 76)]
    lon_prev = 40
    def add(t, lon, lat, R):
        nonlocal lon_prev
        lon = lon_prev + ((lon - lon_prev + 180) % 360 - 180); lon_prev = lon
        cam.append((t, lon, max(-35, min(52, lat)), R))
    ev_sorted = sorted(EVT, key=lambda e: e[0])
    for k, (t, e) in enumerate(ev_sorted):
        if t < 2.4: continue
        nxt = ev_sorted[k + 1][0] if k + 1 < len(ev_sorted) else t + 4
        y = e[0]; cr = crisis_at(y); big = cr is not None and cr[2] / (cr[1] - cr[0]) > 2e6
        R = 104 if big else (92 if e[3] not in ("8 BILLION",) else 80)
        add(t + 0.15, e[2] + 12, e[1] - 6, R)          # slightly offset so the target sits in the lit hemisphere
        if nxt - t > 1.6: add(nxt - 0.5, e[2] + 22, e[1] - 4, R - 8)
    add(START["outro"] + 0.5, lon_prev + 40, 18, 80); add(TOTAL, lon_prev + 60, 15, 72)
    cam.sort(key=lambda c: c[0])
    out = []
    for c in cam:
        if out and c[0] - out[-1][0] < 0.5: out[-1] = c
        else: out.append(c)
    return out
CAM = build_cam()
def camera(T):
    ts = [c[0] for c in CAM]
    i = max(0, min(len(CAM) - 2, int(np.searchsorted(ts, T, side="right") - 1)))
    a, b = CAM[i], CAM[i + 1]
    k = ease((T - a[0]) / max(1e-6, b[0] - a[0]))
    return tuple(lerp(a[j], b[j], k) for j in (1, 2, 3))

STARS = None
def space_bg():
    global STARS
    if STARS is None:
        a = np.zeros((AH, AW, 3), np.uint8); a[:] = (4, 6, 14)
        rng = np.random.default_rng(5)
        for _ in range(260):
            x, y = rng.integers(0, AW), rng.integers(0, AH); v = rng.integers(60, 230)
            a[y, x] = (v, v, min(255, v + 20))
        STARS = a
    return STARS

RAMP = (np.array([(80, 20, 120), (220, 40, 200), (80, 220, 255), (240, 255, 255)], float) if os.environ.get("POP_STYLE") == "neon"
        else np.array([(110, 50, 16), (226, 128, 36), (255, 206, 96), (255, 250, 220)], float))
def ramp(v):
    v = np.clip(v, 0, 1) * 3; i = np.minimum(2, v.astype(int)); f = (v - i)[..., None]
    return RAMP[i] * (1 - f) + RAMP[i + 1] * f

GCX, GCY = 90, 186
def globe(arr, T, D, lon0, lat0, R):
    R = max(10, R)
    x0, x1 = int(max(0, GCX - R - 2)), int(min(AW, GCX + R + 3)); y0, y1 = int(max(0, GCY - R - 2)), int(min(AH, GCY + R + 3))
    ys, xs = np.mgrid[y0:y1, x0:x1]
    X = (xs - GCX + 0.5) / R; Y = (GCY - ys - 0.5) / R
    rho2 = X * X + Y * Y; inside = rho2 <= 1
    rim = (rho2 > 1) & (rho2 <= (1 + 2.2 / R) ** 2)
    sub = arr[y0:y1, x0:x1]
    sub[rim] = (60, 110, 190)
    Xi, Yi = X[inside], Y[inside]; Z = np.sqrt(np.maximum(0, 1 - Xi * Xi - Yi * Yi))
    p0 = math.radians(lat0)
    lat = np.degrees(np.arcsin(np.clip(Z * math.sin(p0) + Yi * math.cos(p0), -1, 1)))
    lon = lon0 + np.degrees(np.arctan2(Xi, Z * math.cos(p0) - Yi * math.sin(p0)))
    lon = (lon + 180) % 360 - 180
    gi = np.clip(((90 - lat) / 0.5).astype(int), 0, GH - 1); gj = np.clip(((lon + 180) / 0.5).astype(int), 0, GW - 1)
    land = LAND[gi, gj] | (lat < -62)
    if CINE:
        sd = (-0.62 * Xi + 0.30 * Yi + 0.72 * Z)
        day = np.clip(sd * 3.5 + 0.35, 0, 1)
        light = (0.10 + 0.95 * day * np.clip(0.5 + 0.6 * sd, 0, 1.1))[:, None]
        twi = np.clip(1 - np.abs(sd + 0.08) * 7, 0, 1)[:, None]
    else:
        light = np.clip(0.45 + 0.75 * (-0.45 * Xi + 0.55 * Yi + 0.70 * Z), 0.25, 1.15)[:, None]
    ocean = (np.array([5, 8, 22], float) * (0.6 + 0.4 * light)) if NEON else np.array([20, 46, 96], float) * light
    hab = HAB[gi, gj]; des = DES[gi, gj][:, None]
    green = np.array([58, 92, 52], float); sand = np.array([150, 126, 78], float)
    lc = green * (1 - des) + sand * des
    if NEON: lc = np.array([22, 26, 48], float) * (1 - des) + np.array([40, 30, 52], float) * des
    lc = np.where((lat < -62)[:, None] | ((hab[:, None] < 0.01) & (des < 0.5)), np.array([196, 204, 214], float), lc)
    col = np.where(land[:, None], lc * light, ocean)
    if CINE and not NEON: col = col + twi * np.array([70, 26, 6]) * 0.6
    if NEON:   # glowing coastlines
        c2 = LAND[np.clip(gi + 1, 0, GH - 1), gj] ^ LAND[gi, np.clip(gj + 1, 0, GW - 1)] | (LAND[gi, gj] ^ LAND[np.clip(gi - 1, 0, GH - 1), gj])
        col = np.where(c2[:, None], np.array([40, 200, 220], float) * (0.45 + 0.55 * light), col)
    # dither ocean bands
    dd = ((xs[inside] + ys[inside]) % 2 == 0)[:, None]
    col = np.where(~land[:, None] & dd, col * 0.94, col)
    if D is not None:
        d = D[gi, gj]
        nz = NOISE[gi, gj]
        occd = DMEAN[0]
        p = np.minimum(np.clip(d / 260.0, 0, 1), np.clip((d / (2.2 * occd + 1e-9)) ** 1.4, 0, 1))
        lit = land & (d > 0) & (nz < p)
        lv = np.clip((np.log10(d + 1e-9) - 1.0) / 5.0, 0.04, 1) + (nz - 0.5) * 0.12
        a = np.clip(0.35 + lv * 1.6, 0, 1)[:, None]
        if CINE:
            nightk = (1 - day * 0.72)[:, None]
            a = a * nightk
            gl = np.where(lit[:, None], ramp(lv) * a * (0.5 + lv[:, None]), 0)
            gsub = GLOW[y0:y1, x0:x1]; gsub[inside] = gl
        col = np.where(lit[:, None], col * (1 - a) + ramp(lv) * a, col)
    sub_in = sub[inside].astype(float); sub[inside] = np.clip(col, 0, 255).astype(np.uint8)
    return lambda la, lo: project(la, lo, lon0, lat0, R)

def project(la, lo, lon0, lat0, R):
    p, p0 = math.radians(la), math.radians(lat0); dl = math.radians(lo - lon0)
    cosc = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(dl)
    if cosc < 0.05: return None
    x = math.cos(p) * math.sin(dl); y = math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(dl)
    return GCX + x * R, GCY - y * R

def fmt_year(y):
    y = int(round(y))
    if y < 0:
        a = -y
        return (f"{a // 1000} {a % 1000:03d} BC" if a >= 10000 else f"{a} BC")
    return f"{y} AD" if y < 1000 else str(y)
def fmt_pop(p, approx=False):
    if p >= 1e9: s = f"{p / 1e9:.2f} BILLION"
    elif p >= 1e6: s = f"{p / 1e6:.0f} MILLION" if p >= 1e7 else f"{p / 1e6:.1f} MILLION"
    else: s = f"{p / 1e3:.0f} 000"
    return s
def fmt_rate(b):
    return f"{b / 1e6:.0f} M" if b >= 1e7 else (f"{b / 1e6:.1f} M" if b >= 1e6 else f"{b / 1e3:.0f} K")

# precomputed population history for the chart (one point per video frame up to outro)
CHART_T = np.arange(0, START["outro"], 1 / FPS)
CHART_P = np.array([world_pop(year_at(t)) for t in CHART_T])
CHART_C = np.array([crisis_at(year_at(t)) is not None and excess(year_at(t)) > 2e6 for t in CHART_T])

def draw_chart(c, T):
    x0, x1, yb, h = 18, 162, 304, 30
    c.a.rectangle([x0 - 3, yb - h - 4, x1 + 3, yb + 3], fill=(8, 10, 20), outline=(40, 50, 80))
    for k in range(5, 11):   # log gridlines 100k .. 10B
        yy = yb - (k - 5) / 5 * h; c.a.line([x0, yy, x1, yy], fill=(18, 24, 44))
    n = min(len(CHART_T), int(T * FPS) + 1)
    if n < 2: return
    xs = x0 + (x1 - x0) * CHART_T[:n] / CHART_T[-1]
    ys = yb - (np.log10(CHART_P[:n]) - 5) / 5 * h
    for i in range(1, n):
        c.a.line([xs[i - 1], ys[i - 1], xs[i], ys[i]], fill=RED if CHART_C[i] else YEL)
    c.a.rectangle([xs[n - 1] - 1, ys[n - 1] - 1, xs[n - 1] + 1, ys[n - 1] + 1], fill=(255, 255, 230))
    text(c.t, x0 * 2, (yb - h - 4) * 2 - 18, "WORLD POPULATION (LOG)", fill=DIM)

DMEAN = [1.0]
def draw_world(c, T, show_chart=True):
    y = year_at(T); lon0, lat0, R = camera(T)
    arr = np.array(c.art)
    D = density(y) if T >= 1.6 else None
    if D is not None:
        m = D > 0; DMEAN[0] = float(D[m].mean()) if m.any() else 1.0
    proj = globe(arr, T, D, lon0, lat0, R)
    c.art = Image.fromarray(arr); c.a = ImageDraw.Draw(c.art)
    # births sparkle where they happen, deaths in red
    i0, i1 = np.searchsorted(BIPT, T - 0.12), np.searchsorted(BIPT, T + 1e-9)
    for k in range(i0, i1):
        tt, i, j = SCH["bips"][k]; p = proj(LAT[i, j], LON[i, j])
        if p is None: continue
        age = T - tt; x, yy = int(p[0]), int(p[1])
        if age < 0.04: c.a.line([x - 1, yy, x + 1, yy], fill=(255, 255, 255)); c.a.line([x, yy - 1, x, yy + 1], fill=(255, 255, 255))
        else: c.a.point((x, yy), fill=(255, 240, 180))
    i0, i1 = np.searchsorted(BOMT, T - 0.25), np.searchsorted(BOMT, T + 1e-9)
    for k in range(i0, i1):
        tt, i, j = SCH["bombs"][k]; p = proj(LAT[i, j], LON[i, j])
        if p is None: continue
        age = T - tt; x, yy = int(p[0]), int(p[1]); r = 1 + int(age * 16)
        c.a.ellipse([x - r, yy - r, x + r, yy + r], outline=(255, 60, 40) if age < 0.15 else (140, 30, 20))
    if CINE: cine_post(c, T, y, lon0, lat0, R)
    # event marker: expanding ring at the event location
    k = int(np.searchsorted(EVTT, T, side="right")) - 1
    if k >= 0 and T - EVTT[k] < 1.5:
        e = EVT[k][1]; p = proj(e[1], e[2])
        if p is not None:
            a = T - EVTT[k]
            for rr in (2 + (a * 14) % 10, 2 + (a * 14 + 5) % 10):
                c.a.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], outline=(255, 255, 255) if not NEON else (255, 80, 220))
            c.a.rectangle([p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1], fill=(255, 255, 255))
    if show_chart: draw_chart(c, T)
    return y

from PIL import ImageFilter
VIG = None
def cine_post(c, T, y, lon0, lat0, R):
    global VIG
    arr = np.array(c.art).astype(np.float32)
    # bloom of the city lights
    g = np.clip(GLOW, 0, 255).astype(np.uint8); GLOW[:] = 0
    gi = Image.fromarray(g)
    b1 = np.array(gi.filter(ImageFilter.GaussianBlur(1.6)), np.float32); b2 = np.array(gi.filter(ImageFilter.GaussianBlur(5)), np.float32)
    arr += b1 * 0.9 + b2 * 0.8
    # atmosphere halo
    if VIG is None:
        yy, xx = np.mgrid[0:AH, 0:AW]
        VIG = (1 - 0.55 * (((xx - AW / 2) / (AW * 0.75)) ** 2 + ((yy - AH / 2) / (AH * 0.62)) ** 2)).clip(0.35, 1)[..., None]
    yy, xx = np.mgrid[0:AH, 0:AW]
    d = np.sqrt((xx - GCX) ** 2 + (yy - GCY) ** 2) / R
    halo = np.clip(1 - (d - 1) / 0.16, 0, 1) * (d > 1)
    arr += halo[..., None] * (np.array([140, 40, 180], np.float32) if NEON else np.array([30, 70, 140], np.float32)) * 0.9
    # satellites after Sputnik (1957)
    if y > 1957:
        n = min(70, int((y - 1957) * 1.3) + 1)
        rng = np.random.default_rng(9)
        inc = rng.uniform(-1.2, 1.2, 70); ph0 = rng.uniform(0, 6.28, 70); rr = rng.uniform(1.12, 1.45, 70); sp = rng.uniform(0.5, 1.4, 70)
        for k in range(n):
            a = ph0[k] + T * sp[k]
            x3, y3, z3 = rr[k] * math.cos(a), rr[k] * math.sin(a) * math.sin(inc[k]), rr[k] * math.sin(a) * math.cos(inc[k])
            if z3 < 0 and x3 * x3 + y3 * y3 < 1: continue
            px, py = int(GCX + x3 * R), int(GCY - y3 * R)
            if 0 <= px < AW and 0 <= py < AH:
                v = 255 if int(T * 6 + k) % 3 else 140
                arr[py, px] = (v, v, v)
    # grade: teal shadows, warm highlights, vignette
    lum = (arr[..., 0] * 0.3 + arr[..., 1] * 0.59 + arr[..., 2] * 0.11)[..., None] / 255
    if not NEON: arr = arr * (1 - 0.18 * (1 - lum)) + (1 - lum) * np.array([0, 10, 18], np.float32) + lum * np.array([14, 4, -6], np.float32)
    arr *= VIG
    c.art = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); c.a = ImageDraw.Draw(c.art)
    # shooting star at each billion
    for (tm, b_, yy_) in MILES:
        q = (T - tm) / 0.5
        if 0 <= q < 1:
            x = 10 + q * 170; yv = 90 + q * 30
            for k in range(14):
                c.a.point((x - k * 2, yv - k * 0.35), fill=(255, 255, int(255 - k * 12)))

def header(c, T, y, title):
    P = world_pop(y); b = births(y)
    pre = y < -10000
    sub = ("POP  ~" + fmt_pop(P) + " ?") if pre else ("POP  " + fmt_pop(P))
    cr = crisis_at(y)
    falling = world_pop(y + 1) < P
    panel(c.t, title, fmt_year(y), sub, [CREAM] * 14, right=["BIRTHS", "/ YEAR", fmt_rate(b)],
          sub_col=RED if falling else CREAM)
    if cr and excess(y) > 2e6:
        w = 8 * max(len(cr[4]), len(cr[5])) + 20
        c.t.rectangle([180 - w / 2, 172, 180 + w / 2, 212], fill=(60, 10, 8)); c.t.rectangle([180 - w / 2, 172, 180 + w / 2, 173], fill=RED)
        text(c.t, 180, 172, cr[4], fill=(255, 120, 100), align="c"); text(c.t, 180, 190, cr[5], fill=CREAM, align="c")
    for (tm, b_, yy) in MILES:
        if 0 <= T - tm < 1.0:
            s = f"{b_} BILLION !"
            w = 16 * len(s) + 20
            c.t.rectangle([180 - w / 2, 170, 180 + w / 2, 214], fill=(30, 22, 6)); c.t.rectangle([180 - w / 2, 170, 180 + w / 2, 171], fill=YEL)
            text(c.t, 180, 170, s, size=40, fill=YEL, align="c")

def sc_generic(name):
    def f(t):
        T = START[name] + t
        c = Ctx(space_bg())
        y = draw_world(c, T)
        header(c, T, y, TITLES[name])
        k = int(np.searchsorted(EVTT, T, side="right")) - 1
        if k >= 0 and T - EVTT[k] < 1.6:
            e = EVT[k][1]; a = T - EVTT[k]
            n = int(min(len(e[3]), a * 40))
            w = 8 * max(len(e[3]), len(e[4])) + 24
            busy = (crisis_at(y) is not None and excess(y) > 2e6) or any(0 <= T - tm < 1.0 for tm, _, _ in MILES)
            yb = 266 if busy else 222
            c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 40], fill=(10, 6, 24)); c.t.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 1], fill=(255, 80, 220) if NEON else YEL)
            text(c.t, 180, yb + 1, e[3][:n], fill=CREAM, align="c")
            if a > 0.35: text(c.t, 180, yb + 19, e[4], fill=(120, 230, 255) if NEON else DIM, align="c")
        return c
    return f

def sc_intro(t):
    T = START["intro"] + t
    c = Ctx(space_bg())
    draw_world(c, T, show_chart=False)
    q = ease((t - 0.15) / 0.4)
    if q > 0:
        c.t.rectangle([30, 76, 252, 158], fill=(6, 7, 12))
        text(c.t, 40, 74, "THIS MELODY", size=40); text(c.t, 40, 112, "IS US" if t > 0.6 else "IS ", size=40)
    if t > 1.2: text(c.t, 180, 566, "EVERY BIP = PEOPLE BEING BORN", fill=CREAM, align="c")
    if t > 1.8: text(c.t, 180, 590, "EVERY BOOM = PEOPLE DYING TOO SOON", fill=(255, 120, 100), align="c")
    return c

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(space_bg())
    draw_world(c, T, show_chart=False)
    W = c.t
    W.rectangle([30, 60, 330, 170], fill=(6, 7, 12)); W.rectangle([30, 60, 330, 61], fill=YEL)
    text(W, 180, 64, "2026", fill=DIM, align="c")
    text(W, 180, 82, "8.3 BILLION", size=40, fill=CREAM, align="c")
    text(W, 180, 122, "ALIVE RIGHT NOW", fill=CREAM, align="c")
    if t > 1.2:
        W.rectangle([30, 470, 330, 560], fill=(6, 7, 12)); W.rectangle([30, 470, 330, 471], fill=(110, 76, 50))
        text(W, 180, 474, "~117 BILLION BORN", fill=YEL, align="c"); text(W, 180, 494, "SINCE THE DAWN OF OUR SPECIES", fill=CREAM, align="c")
        text(W, 180, 520, "(PRB ESTIMATE)", fill=DIM, align="c")
    if t > 3.0: text(W, 180, 590, "EVERY BIP WAS SOMEONE.", fill=CREAM, align="c")
    return c

SCENEFN = {n: sc_generic(n) for n in NAMES}
SCENEFN["intro"] = sc_intro; SCENEFN["outro"] = sc_outro

# ================= FX (stable crescendo engine + crisis tint) =================
def intensity(T): return 0.06 + 0.7 * ease(T / START["outro"]) ** 2.2
HOPS = None
def panel_hop(T):
    global HOPS
    if HOPS is None: HOPS = np.array(sorted([e[0] for e in EV if e[1] in ("chime",)] + KICKS))
    i = np.searchsorted(HOPS, T, side="right") - 1
    if i < 0: return 0
    d = T - HOPS[i]
    return int(round(-5 * FXK * intensity(T) * 1.5 * math.exp(-d / 0.08) * abs(math.cos(2 * math.pi * d / 0.2))))
def active_glitch(T):
    for g in GL:
        if g[0] <= T < g[0] + g[1]: return g
    return None
def fx(fr, T, name, t):
    I = intensity(T) * FXK
    ki = np.searchsorted(KICKS, T, side="right") - 1
    kp = math.exp(-(T - KICKS[ki]) / 0.07) if ki >= 0 else 0.0
    si = np.searchsorted(SNARES, T, side="right") - 1
    sp = math.exp(-(T - SNARES[si]) / 0.06) if si >= 0 else 0.0
    bi = np.searchsorted(BOMT, T, side="right") - 1
    bp = math.exp(-(T - BOMT[bi]) / 0.08) if bi >= 0 else 0.0
    if name == "outro": I *= 0.3
    push = 1.01 + 0.03 * I * ease(t / DUR[name])
    kd = (T - KICKS[ki]) if ki >= 0 else 9
    spring = math.exp(-kd / 0.11) * math.cos(2 * math.pi * kd / 0.17)
    zoom = push + kp * (0.01 + 0.03 * I)
    sd = (T - SNARES[si]) if si >= 0 else 9
    squash = math.exp(-sd / 0.09) * math.cos(2 * math.pi * sd / 0.14)
    zx = zoom * (1 - 0.02 * squash * I); zy = zoom * (1 + 0.04 * squash * I)
    rng = random.Random(int(T * 1000)); sh = sp * 10 * I + bp * 10
    dx = rng.uniform(-sh, sh); dy = -spring * (6 + 50 * I) + rng.uniform(-sh, sh)
    fr = warp(fr, zx, dx, dy, zy)
    split = int((sp * 12 + kp * 3) * max(0.0, I - 0.35) + bp * 6)
    if split > 0:
        out = fr.copy(); out[:, split:, 0] = fr[:, :-split, 0]; out[:, :-split, 2] = fr[:, split:, 2]; fr = out
    fl = kp * (10 + 30 * I)
    y = year_at(T)
    if crisis_at(y) is not None and excess(y) > 2e6:      # crisis: red pulse on each death boom
        f = fr.astype(np.int16); f[..., 0] += int(28 * bp + 10); f[..., 1] -= int(12 * bp); f[..., 2] -= int(12 * bp)
        fr = np.clip(f, 0, 255).astype(np.uint8)
    if fl > 1: fr = np.minimum(255, fr.astype(np.int16) + int(fl)).astype(np.uint8)
    for (tm, b_, yy) in MILES:
        if 0 <= T - tm < 0.12: fr = np.minimum(255, fr.astype(np.int16) + int(110 * (1 - (T - tm) / 0.12))).astype(np.uint8)
    return fr

GRAIN = [np.random.default_rng(k).integers(-6, 7, (OH // 3, OW // 3, 1)).repeat(3, 0).repeat(3, 1).astype(np.int16) for k in range(6)] if CINE else []
def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    g = active_glitch(T)
    if g and g[2] == "stutter":
        T2 = g[0] + ((T - g[0]) % g[3]); t = T2 - START[name]
        if t < 0: idx -= 1; name = NAMES[idx]; t = T2 - START[name]
    if g and g[2] == "tapestop":
        p = (T - g[0]) / g[1]; T2 = g[0] + g[1] * (p - p * p / 2); t = T2 - START[name]
        if t >= DUR[name]: t = DUR[name] - 1e-3
    c = SCENEFN[name](t)
    hop = panel_hop(START[name] + t)
    if hop:
        band = c.txt.crop((0, 60, TW, 162)); c.t.rectangle([0, 60, TW, 162], fill=(0, 0, 0, 0)); c.txt.alpha_composite(band, (0, 60 + hop))
    fr = v2.compose(c, t, idx)
    fr = fx(fr, T, name, t)
    if CINE:
        fr = fr.copy(); fr[1::3] = (fr[1::3] * 0.9).astype(np.uint8)
        gr = GRAIN[int(T * 24) % len(GRAIN)]
        fr = np.clip(fr.astype(np.int16) + gr, 0, 255).astype(np.uint8)
    if g: fr = glitch_frame(fr, T, g)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.2)) / 1.2)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    if name == "intro":
        f = 1 - ease(t / 0.6)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))): p.stdin.write(render_frame(idx, f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((360, 640), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    elif mode == "info":
        from collections import Counter
        print(TOTAL, Counter(k for _, k, _ in EV)); print("miles", [(round(a, 2), b, c) for a, b, c in MILES])
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        only = sys.argv[3:]
        idxs = [i for i, n in enumerate(NAMES) if not only or n in only]
        with Pool(2) as pool: print(pool.map(render_scene, [(i, out) for i in idxs]))
