"""BeepMelody · EVERY BIRTH — 4 babies are born every second. Watch where.
Real time: 132.11 M births in 2023 (UN WPP 2024) = 4.19 per second. Every beep = one baby, drawn as a Poisson
process (seeded) and placed in a country with probability = its share of 2023 births (every_birth_countries.csv);
the remaining ~19 % go to the rest of the world on a population-density proxy map. Globe = engine pop4.py (imported, unmodified).
Usage (from studio/this-melody-is/engine, PYTHONPATH=../../beepmelody/episodes):
  python3 every_birth.py info out | preview <out> <scene>:<t> ... | audio <wav> | render <out> | final <out> <name>.mp4"""
import sys, os, math, csv, random, subprocess
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "..", "this-melody-is", "engine")
sys.path.insert(0, ENGINE)
os.environ.setdefault("POP_STYLE", "v1")
import v2
from v2 import AW, AH, TW, TH, OW, OH, FPS, CREAM, YEL, RED, DIM, text, ease, lerp
import pop4 as P4          # globe(), project(), LAND/LAT/LON/WH/REG maps, space_bg()
from pi import Ctx

# ================= data =================
RATE = 132110264 / (365 * 86400)        # 4.189 births / s (UN WPP 2024, year 2023)
RCOL = {"asia": (255, 206, 96), "africa": (255, 128, 64), "europe": (110, 190, 255), "americas": (120, 235, 140), "oceania": (220, 130, 255)}
RNAME = {"asia": "ASIA", "africa": "AFRICA", "europe": "EUROPE", "americas": "AMERICAS", "oceania": "OCEANIA"}
RORDER = ["asia", "africa", "americas", "europe", "oceania"]
P4REG = {P4.AFR: "africa", P4.MENA: "asia", P4.EUR: "europe", P4.SAS: "asia", P4.EAS: "asia", P4.SEA: "asia", P4.AME: "americas", P4.OCE: "oceania"}
CTRY = []
for r in csv.DictReader(open(os.path.join(HERE, "every_birth_countries.csv"))):
    CTRY.append(r)
GH, GW = P4.GH, P4.GW
LAT, LON, LAND = P4.LAT, P4.LON, P4.LAND
# cell weights per listed country: land cells near the centroid, weighted by the density proxy (+ floor)
listed = [c for c in CTRY if c["lat"]]
dist = np.full((len(listed), GH, GW), 1e9)
for k, c in enumerate(listed):
    la, lo, s = float(c["lat"]), float(c["lon"]), float(c["spread_deg"])
    d = np.sqrt((LAT - la) ** 2 + ((LON - lo) * np.cos(np.radians(la))) ** 2) / s
    dist[k] = d
owner = np.argmin(dist, 0); dmin = np.min(dist, 0)
claimed = LAND & (dmin < 1.6)
W_C, REG_C = [], []
for k, c in enumerate(listed):
    m = claimed & (owner == k)
    w = (P4.WH + 0.05) * m * np.exp(-dist[k] ** 2)
    if w.sum() == 0: w = (dist[k] == dist[k].min()).astype(float)
    W_C.append((w / w.sum()).ravel()); REG_C.append(c["region"])
rest = (P4.WH * LAND * ~claimed).ravel(); rest = rest / rest.sum()
CB = np.array([float(c["births_2023"]) for c in CTRY]); CP = CB / CB.sum()
NAMEC = [c["country"] for c in CTRY]

# ================= timeline =================
SC = [("intro", 5.0), ("india", 11.0), ("china", 10.0), ("africa", 12.0), ("americas", 11.0), ("world", 8.0), ("outro", 9.5)]
START, acc = {}, 0.0
for n, d in SC: START[n] = acc; acc += d
TOTAL = acc; DUR = dict(SC); NAMES = [n for n, _ in SC]
T_END_BIRTHS = TOTAL - 1.4
def scene_at(T):
    for n, d in SC:
        if START[n] <= T < START[n] + d: return n
    return NAMES[-1]

# births: Poisson process in real time
rng = np.random.default_rng(2023)
BT = []; t = 0.55
while True:
    t += rng.exponential(1 / RATE)
    if t > T_END_BIRTHS: break
    BT.append(t)
BT = np.array(BT)
BC = rng.choice(len(CTRY), size=len(BT), p=CP)
BIRTHS = []   # (t, i, j, region, country)
for tt, k in zip(BT, BC):
    if CTRY[k]["lat"]:
        cell = rng.choice(GH * GW, p=W_C[k]); reg = CTRY[k]["region"]
    else:
        cell = rng.choice(GH * GW, p=rest); reg = P4REG.get(int(P4.REG.ravel()[cell]), "asia")
    i, j = divmod(int(cell), GW)
    BIRTHS.append((float(tt), i, j, reg, NAMEC[k]))
NB = len(BIRTHS)
def count_at(T): return int(np.searchsorted(BT, T, side="right"))

# camera keyframes (time, lon, lat, R)
CAM = [(0.0, 55, 12, 64), (START["india"] - 0.4, 60, 14, 70), (START["india"] + 1.2, 80, 20, 86), (START["china"] - 0.6, 88, 20, 84),
       (START["china"] + 1.0, 108, 28, 86), (START["africa"] - 0.8, 100, 22, 80), (START["africa"] + 1.2, 18, 4, 86),
       (START["americas"] - 0.8, 0, 6, 82), (START["americas"] + 1.4, -82, 18, 82), (START["world"] - 0.6, -70, 15, 80),
       (START["world"] + 2.5, 20, 12, 68), (START["outro"], 50, 14, 66), (TOTAL, 75, 14, 62)]
def camera(T):
    ts = [c[0] for c in CAM]
    i = max(0, min(len(CAM) - 2, int(np.searchsorted(ts, T, side="right") - 1)))
    a, b = CAM[i], CAM[i + 1]; k = ease((T - a[0]) / max(1e-6, b[0] - a[0]))
    return tuple(lerp(a[j], b[j], k) for j in (1, 2, 3))

# banners: (scene, line1, line2, highlight country, pin lat/lon)
BANNERS = {
    "india":    ("1 IN 6 BABIES", "IS BORN IN INDIA", "India", (22.5, 79)),
    "china":    ("CHINA: 1 IN 15", "~9 MILLION BABIES A YEAR", "China", (31, 113)),
    "africa":   ("NIGERIA: 1 IN 18", "DR CONGO: MORE THAN THE USA", "Nigeria", (9, 8)),
    "americas": ("USA: ~1 IN 36", "3.6 MILLION BABIES A YEAR", "United States", (38, -92)),
    "world":    ("~362 000 BABIES", "EVERY DAY", None, None),
}
MILE_T = {n: START[n] + 0.6 for n in BANNERS}

# ================= rendering =================
def draw_globe(c, T):
    lon0, lat0, R = camera(T)
    arr = np.array(c.art)
    proj = P4.globe(arr, T, None, lon0, lat0, R)
    c.art = Image.fromarray(arr); c.a = ImageDraw.Draw(c.art)
    n = count_at(T)
    for k in range(n):
        tt, i, j, reg, _ = BIRTHS[k]
        p = proj(LAT[i, j], LON[i, j])
        if p is None: continue
        age = T - tt; x, y = int(p[0]), int(p[1]); col = RCOL[reg]
        if age < 0.10:
            c.a.line([x - 2, y, x + 2, y], fill=(255, 255, 255)); c.a.line([x, y - 2, x, y + 2], fill=(255, 255, 255))
        elif age < 0.6:
            r = 1 + int(age * 7)
            c.a.ellipse([x - r, y - r, x + r, y + r], outline=tuple(int(v * (1 - age)) for v in col))
            c.a.point((x, y), fill=col)
        else:
            k2 = max(0.7, 1 - (age - 0.6) / 40)
            dim = tuple(int(v * k2 * 0.45) for v in col)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): c.a.point((x + dx, y + dy), fill=dim)
            c.a.point((x, y), fill=tuple(min(255, int(v * k2 * 1.1)) for v in col))
    return proj

def hud(c, T):
    n = count_at(T)
    W = c.t
    W.rectangle([28, 62, 332, 150], fill=(8, 10, 22)); W.rectangle([28, 62, 332, 63], fill=YEL); W.rectangle([28, 149, 332, 150], fill=(60, 70, 110))
    text(W, 38, 64, "BORN SINCE YOU PRESSED PLAY", fill=DIM)
    text(W, 38, 84, f"{n}", size=40, fill=CREAM)
    text(W, 322, 88, "4.2 / SECOND", fill=YEL, align="r")
    text(W, 322, 106, "REAL TIME", fill=DIM, align="r")
    text(W, 38, 126, "EVERY BEEP = ONE BABY", fill=CREAM)

def tally(c, T):
    """bottom strip: where the beeps of this video were born, by region (counts of what you heard)."""
    n = count_at(T)
    W = c.t; x0, x1, y0 = 28, 332, 560
    W.rectangle([x0, y0 - 22, x1, y0 + 52], fill=(8, 10, 22))
    text(W, x0 + 8, y0 - 22, "WHERE THEY WERE BORN", fill=DIM)
    if n == 0: return
    cnt = {r: 0 for r in RORDER}
    for k in range(n): cnt[BIRTHS[k][3]] += 1
    x = x0 + 8; span = x1 - x0 - 16
    for r in RORDER:
        w = span * cnt[r] / n
        if w >= 1: W.rectangle([x, y0, x + w - 1, y0 + 10], fill=RCOL[r])
        x += w
    for row, regs in enumerate((RORDER[:2], RORDER[2:])):
        items = [f"{RNAME[r]} {cnt[r]}" for r in regs]
        tot = sum(8 * len(s) for s in items) + 16 * (len(items) - 1); lx = 180 - tot / 2
        for r, s in zip(regs, items):
            text(W, lx, y0 + 14 + row * 18, s, fill=RCOL[r]); lx += 8 * len(s) + 16

def banner(c, T, name, proj):
    if name not in BANNERS: return
    a = T - MILE_T[name]
    if a < 0 or a > 6.5: return
    l1, l2, ctry, pin = BANNERS[name]
    W = c.t
    w = 8 * max(len(l1), len(l2)) + 28
    if len(l1) * 16 + 28 <= 320: big = True; w = max(w, 16 * len(l1) + 28)
    else: big = False
    yb = 166
    h = 64 if big else 44
    W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + h], fill=(30, 22, 6)); W.rectangle([180 - w / 2, yb, 180 + w / 2, yb + 1], fill=YEL)
    nchar = int(min(len(l1), a * 40))
    if big: text(W, 180, yb + 2, l1[:nchar], size=40, fill=YEL, align="c")
    else: text(W, 180, yb + 2, l1[:nchar], fill=YEL, align="c")
    if a > 0.4: text(W, 180, yb + (42 if big else 22), l2, fill=CREAM, align="c")
    if pin and proj:
        p = proj(*pin)
        if p is not None:
            rr = 4 + (a * 14) % 9
            c.a.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], outline=(255, 255, 255))

def sc_main(name):
    def f(t):
        T = START[name] + t
        c = Ctx(P4.space_bg())
        proj = draw_globe(c, T)
        hud(c, T); tally(c, T); banner(c, T, name, proj)
        return c
    return f

def sc_intro(t):
    T = t
    c = Ctx(P4.space_bg())
    draw_globe(c, T)
    W = c.t
    if t > 0.15:
        W.rectangle([28, 62, 332, 150], fill=(8, 10, 22)); W.rectangle([28, 62, 332, 63], fill=YEL)
        text(W, 180, 70, "4 BABIES ARE BORN", size=40, fill=CREAM, align="c")
        text(W, 180, 108, "EVERY SECOND", size=40, fill=YEL, align="c")
    if t > 1.3: text(W, 180, 548, "EVERY BEEP = ONE BABY", size=40 if t < 4.2 else 20, fill=CREAM, align="c")
    if t > 2.4: text(W, 180, 594, "IN REAL TIME. WATCH WHERE.", fill=YEL, align="c")
    return c

def sc_outro(t):
    T = START["outro"] + t
    c = Ctx(P4.space_bg())
    draw_globe(c, T)
    W = c.t; n = count_at(T)
    W.rectangle([28, 62, 332, 170], fill=(8, 10, 22)); W.rectangle([28, 62, 332, 63], fill=YEL)
    text(W, 180, 66, "WHILE YOU WATCHED", fill=DIM, align="c")
    text(W, 180, 86, f"{n} BABIES", size=40, fill=CREAM, align="c")
    text(W, 180, 128, "WERE BORN", fill=CREAM, align="c")
    tally(c, T)
    if t > 2.2:
        W.rectangle([28, 176, 332, 222], fill=(8, 10, 22))
        text(W, 180, 178, "132 MILLION IN 2023", fill=YEL, align="c")
        text(W, 180, 198, "DATA: UN WPP 2024 (EST.)", fill=DIM, align="c")
    if t > 4.6: text(W, 180, 506, "EVERY BEEP WAS SOMEONE.", fill=CREAM, align="c")
    return c

SCENEFN = {n: sc_main(n) for n in NAMES}
SCENEFN["intro"] = sc_intro; SCENEFN["outro"] = sc_outro

def fx(fr, T):
    k = int(np.searchsorted(BT, T, side="right")) - 1
    if k >= 0 and T - BT[k] < 0.06:
        fr = np.minimum(255, fr.astype(np.int16) + 10).astype(np.uint8)
    for n, tm in MILE_T.items():
        if 0 <= T - tm < 0.12: fr = np.minimum(255, fr.astype(np.int16) + int(70 * (1 - (T - tm) / 0.12))).astype(np.uint8)
    return fr

def render_frame(idx, t):
    name = NAMES[idx]; T = START[name] + t
    c = SCENEFN[name](t)
    fr = v2.compose(c, t, idx)
    fr = fx(fr, T)
    if name == "intro":
        f = 1 - ease(t / 0.5)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    if name == "outro":
        f = ease((t - (DUR[name] - 1.2)) / 1.2)
        if f > 0: fr = (fr * (1 - f)).astype(np.uint8)
    return fr

def render_scene(args):
    idx, out = args; name = NAMES[idx]; dur = DUR[name]
    tmp, fin = f"{out}/{idx:02d}_{name}.tmp.mp4", f"{out}/{idx:02d}_{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(round(dur * FPS))): p.stdin.write(render_frame(idx, f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, fin); return fin

# ================= music (mood C, chosen at co-pilot step 2): 128 BPM chiptune =================
# one birth = one square-wave bip at its exact time (not quantised); region = register + pulse width.
REGOFF = {"africa": 0, "asia": 12, "americas": 19, "europe": 24, "oceania": 28}
def audio(path):
    from scipy.io import wavfile
    from scipy.signal import butter, lfilter
    SR = 44100; N = int(TOTAL * SR); L = np.zeros(N)
    def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
    def env(n, a, d): tt = np.arange(n) / SR; return np.minimum(1, tt / max(a, 1e-4)) * np.exp(-tt / d)
    def lowpass(x, fc, o=2): b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
    def put(t, sig, g=1.0):
        i = int(t * SR); j = min(N, i + len(sig))
        if 0 <= i < N: L[i:j] += g * sig[:j - i]
    def noise(b, dur, fc, dec, g, seed):
        n = int(dur * SR); put(b, g * lowpass(np.random.RandomState(seed).randn(n), fc) * np.exp(-np.arange(n) / SR * dec))
    def square(f, n, duty):
        tt = np.arange(n) / SR; return np.where((tt * f) % 1 < duty, 1.0, -1.0)
    bpm = 128; beat = 60 / bpm; bar = 4 * beat
    T_OUT = START["outro"]; T_STOP = T_OUT + 2.2          # drums stop when the final numbers land
    t = np.arange(N) / SR
    pad = sum(np.sin(2 * np.pi * mtof(m) * d * t) for m in (48, 55, 60, 63) for d in (.995, 1.005)) * .008
    L += lowpass(pad, 2000) * np.minimum(1, t / 1.5)
    roots = [36, 44, 46, 43]                               # Cm – Ab – Bb – G
    for k, b in enumerate(np.arange(0, TOTAL - 1.0, bar)):
        if b >= T_STOP: break
        for q in range(8):
            n = int(.2 * SR); tt = np.arange(n) / SR; f = mtof(roots[k % 4] + 12 * (q % 2))
            put(b + q * beat / 2, .14 * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 6))
    for k, b in enumerate(np.arange(0, T_STOP, beat)):
        full = b >= START["india"] - 0.05
        if k % 2 == 0: noise(b, .08, 1200, 40, .16, k)
        elif full: noise(b, .1, 5000, 30, .09, k)
        if full: noise(b + beat / 2, .03, 9000, 150, .03, 70 + k)
        if START["world"] <= b < T_OUT:                    # build-up: 16th hats before the outro
            for q in (1, 3): noise(b + q * beat / 4, .02, 9000, 200, .022, 140 + k + q)
    for name, tm in MILE_T.items():                        # milestone = cymbal swell
        noise(tm, 1.2, 7000, 3.5, .07, 300 + int(tm))
    rs = np.random.RandomState(2023)
    for tm, i, j, reg, _ in BIRTHS:
        f = mtof(51 + REGOFF[reg] + [0, 2, 4, 7, 9][rs.randint(5)]); n = int(.35 * SR)
        s = square(f, n, .125 if reg in ("asia", "africa") else .25) * env(n, .001, .09)
        put(tm, .09 * s); put(tm + .75 * beat, .035 * s)  # 3/4-beat echo
    # last bip -> rising arpeggio (root, 5th, octave, 12th) then a held chord
    ta = BIRTHS[-1][0] + 0.3
    for q, m in enumerate((60, 67, 72, 79)):
        n = int(.5 * SR); put(ta + q * beat / 2, .08 * square(mtof(m), n, .25) * env(n, .002, .2))
    n = int(3.0 * SR); tt = np.arange(n) / SR
    put(ta + 2 * beat, .05 * sum(np.sin(2 * np.pi * mtof(m) * tt) for m in (48, 55, 60, 63)) * np.exp(-tt * 1.1))
    out = L.copy()                                         # small room
    for d, g in [(.083, .5), (.127, .42), (.191, .35), (.263, .28), (.347, .22), (.461, .16)]:
        k = int(d * SR); out[k:] += g * .6 * L[:-k]
    x = .8 * L + .2 * lowpass(out, 4000)
    fade = int(1.2 * SR); x[-fade:] *= np.linspace(1, 0, fade)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    st = np.stack([x, np.roll(x, int(.011 * SR)) * .97], 1)
    wavfile.write(path, SR, (st * 32767).astype(np.int16))

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "audio":
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); audio(out); sys.exit()
    if mode == "info":
        from collections import Counter
        print("TOTAL", TOTAL, "births", NB, Counter(b[3] for b in BIRTHS))
        cc = Counter(b[4] for b in BIRTHS); print(cc.most_common(8))
        for n in NAMES: print(n, round(START[n], 2), count_at(START[n]))
        sys.exit()
    os.makedirs(out, exist_ok=True)
    if mode == "preview":
        for x in sys.argv[3:]:
            name, tt = x.split(":")
            Image.fromarray(render_frame(NAMES.index(name), float(tt))).resize((540, 960), Image.NEAREST).save(f"{out}/{name}_{tt}.png")
    elif mode == "final":
        names = sorted(f for f in os.listdir(out) if f[0].isdigit() and f.endswith(".mp4") and "tmp" not in f)
        open(f"{out}/list.txt", "w").write("".join(f"file '{n}'\n" for n in names))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-i", f"{out}/music.wav",
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{out}/{sys.argv[3]}"], check=True)
    else:
        from multiprocessing import Pool
        with Pool(3) as pool: print(pool.map(render_scene, [(i, out) for i in range(len(NAMES))]))
