"""Essai néon 2 : sismographe. Les 100 séismes M8+ depuis 1900 (CSV vérifié de l'épisode quakes-m8 du 9 nov.).
Hauteur du pic = amplitude, qui est logarithmique : +1 de magnitude = amplitude ×10 (échelle de Richter / Mw).
M8.0 = 28 px ; M9.5 (Chili 1960) = 885 px. En haut : la carte du monde où chaque séisme s'allume."""
import csv, math, sys, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from neon import *

SRC = __file__.rsplit("/", 4)[0] + "/outbox/beepmelody/2026-11-09_quakes-m8/quakes_m8.csv"
Q = []
for r in csv.DictReader(open(SRC, encoding="utf-8")):
    y, m, d = map(int, r["date"].split("-")); yr = y + (m - 1) / 12 + (d - 1) / 365
    Q.append(dict(t=yr, mag=float(r["mag"]), lat=float(r["lat"]), lon=float(r["lon"]), label=r["label"], year=y))
Y0, Y1 = 1900.0, 2026.0
DUR_DATA = 25.0
DUR = DUR_DATA + 3.0
def t_of(yr): return (yr - Y0) / (Y1 - Y0) * DUR_DATA
for q in Q: q["at"] = t_of(q["t"])

BASE_Y = 1500; X_NOW = 860; PX_PER_S = 150      # la trace défile vers la gauche
MAP = (60, 330, 1020, 810)                     # carte équirectangulaire

def amp(mag): return 28 * 10 ** (mag - 8)
def col(mag):
    if mag >= 9.0: return (255, 70, 90)
    if mag >= 8.6: return (255, 150, 60)
    return (90, 220, 255)

def main(out):
    wr = Writer(out)
    audio = np.zeros((int((DUR + 4) * SR), 2))
    rng = np.random.default_rng(7)
    for q in Q:
        k = q["mag"] - 8.0
        note = 76 - int(round(k * 10))           # plus fort = plus grave
        place(audio, bell(mf(note), 1.2 + k * 3, 0.09 + 0.12 * k, 0.9), q["at"], max(-0.8, min(0.8, q["lon"] / 180)))
        if k >= 0.7:                              # grondement pour les géants
            n = int((1.5 + k * 2) * SR); t = np.arange(n) / SR
            noise = np.convolve(rng.standard_normal(n), np.ones(400) / 400, mode="same")
            rum = noise * np.exp(-t / (0.5 + k)) * (0.25 * k) * 6
            place(audio, rum, q["at"], 0)
    p = pad(DUR + 4, [33, 40, 45], 0.04); audio[:, 0] += p; audio[:, 1] += p
    audio = reverb(audio); audio /= max(1e-9, np.abs(audio).max()) / 0.9

    nf = int(DUR * FPS)
    for fi in range(nf):
        t = fi / FPS; fr = Frame(bg=(5, 5, 10))
        yr = min(Y1, Y0 + t / DUR_DATA * (Y1 - Y0))
        fr.text((W // 2, 150), "Wait for 1960", 84, (240, 240, 245))
        fr.text((W // 2, 232), "every magnitude 8+ earthquake since 1900", 34, (150, 155, 170), medium=True)
        # carte : grille + points
        x0, y0, x1, y1 = MAP
        for lon in range(-180, 181, 60):
            x = x0 + (lon + 180) / 360 * (x1 - x0); fr.db.line([(x, y0), (x, y1)], fill=(22, 24, 34), width=1)
        for lat in range(-60, 91, 30):
            y = y0 + (90 - lat) / 180 * (y1 - y0); fr.db.line([(x0, y), (x1, y)], fill=(22, 24, 34), width=1)
        for q in Q:
            if q["at"] > t: break
            x = x0 + (q["lon"] + 180) / 360 * (x1 - x0); y = y0 + (90 - q["lat"]) / 180 * (y1 - y0)
            age = t - q["at"]; fl = math.exp(-age * 2.5)
            c = col(q["mag"]); r = 4 + (q["mag"] - 8) * 6
            fr.dot((x, y), r + 18 * fl, tuple(int(v * (0.35 + 0.65 * fl)) for v in c), glow=0.4 + 1.2 * fl)
            if fl > 0.05: fr.circle((x, y), r + 90 * (1 - fl), tuple(int(v * fl) for v in c), 2)
        # sismographe
        fr.db.line([(0, BASE_Y), (W, BASE_Y)], fill=(25, 28, 38), width=1)
        pts = []; vis = [q for q in Q if q["at"] <= t and (t - q["at"]) * PX_PER_S < X_NOW + 40]
        xs = np.arange(0, X_NOW + 1, 3)
        ys = np.full(len(xs), float(BASE_Y))
        wob = 3 * np.sin(xs * 0.21 + t * 9) * np.sin(xs * 0.033 + t)
        ys += wob
        for q in vis:
            xq = X_NOW - (t - q["at"]) * PX_PER_S; A = min(amp(q["mag"]), 1180)
            env = np.exp(-np.abs(xs - xq) / (6 + (q["mag"] - 8) * 10))
            w = np.cos((xs - xq) * 0.35); w = np.where(w > 0, w, 0.18 * w)
            ys -= A * env * w * (xs <= X_NOW)
        ys = np.clip(ys, 300, BASE_Y + 90)
        pts = list(zip(xs.tolist(), ys.tolist()))
        fr.line(pts, (90, 220, 255), 3, glow=True)
        fr.dot((X_NOW, ys[-1]), 9, (220, 245, 255), glow=1.4)
        # étiquettes des géants
        for q in vis:
            if q["mag"] >= 8.8:
                xq = X_NOW - (t - q["at"]) * PX_PER_S; A = min(amp(q["mag"]), 1180)
                c = col(q["mag"]); ytop = max(860, BASE_Y - A - 40)
                fr.text((xq, ytop), f"M{q['mag']:.1f}  {q['label'].title()} {q['year']}", 26, c, medium=True, glow=True)
        # compteurs
        n = sum(1 for q in Q if q["at"] <= t)
        fr.text((70, 1720), f"{int(yr)}", 96, (230, 232, 240), anchor="lm")
        fr.text((1010, 1700), f"{n} quakes", 40, (180, 184, 200), anchor="rm", medium=True)
        fr.text((1010, 1750), "M ≥ 8.0", 28, (120, 124, 140), anchor="rm", medium=True)
        if t > DUR_DATA:
            k = min(1, (t - DUR_DATA) / 0.6)
            fr.text((W // 2, 1820), "Chile 1960: 32× the shaking of an M8.", 42, tuple(int(c * k) for c in (255, 120, 130)), glow=True)
        fr.text((W // 2, 1885), "data: USGS ComCat + NOAA NCEI · spike height = amplitude", 22, (90, 94, 110), medium=True)
        wr.add(fr.compose())
    wr.close(audio)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "essai_seismes.mp4")
