"""Essai néon 1 : les orbites comme polyrythme. Chaque tour complet d'une planète = une note.
Données : périodes orbitales sidérales, NASA Planetary Fact Sheet (nssdc.gsfc.nasa.gov/planetary/factsheet).
Échelle : 1 année terrestre = 2 s. Jupiter boucle son tour à 23,7 s → c'est la chute de la vidéo."""
import math, sys, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from neon import *

PL = [  # nom, période (jours), couleur, note MIDI, rayon d'orbite à l'écran (pas à l'échelle)
    ("Mercury", 87.97, "#8EE8FF", 84, 120),
    ("Venus", 224.70, "#FFD166", 81, 190),
    ("Earth", 365.26, "#3DDC97", 76, 260),
    ("Mars", 686.98, "#FF5A4E", 72, 330),
    ("Jupiter", 4332.59, "#C77DFF", 48, 440),
]
YEAR_S = 2.0
TJ = 4332.59 / 365.26 * YEAR_S          # 23,72 s
DUR = TJ + 3.2
CX, CY = W // 2, 860
LANE_Y0, LANE_H = 1420, 64

def period_s(d): return d / 365.26 * YEAR_S
def hits(d):
    p = period_s(d); n = int(DUR / p); return [p * (k + 1) for k in range(n) if p * (k + 1) <= TJ + 0.01]

H_ = {name: hits(d) for name, d, *_ in PL}

def main(out):
    wr = Writer(out)
    audio = np.zeros((int((DUR + 2) * SR), 2))
    for i, (name, d, col, note, r) in enumerate(PL):
        for t in H_[name]:
            if name == "Jupiter":
                for n in (36, 48, 55, 60, 64): place(audio, bell(mf(n), 6.0, 0.16, 1.2), t, 0)
            else:
                place(audio, bell(mf(note), 1.4 if i < 2 else 2.0, 0.11 + 0.03 * i, 0.8), t, (-0.6, 0.6, -0.25, 0.3)[i])
    p = pad(DUR + 2, [36, 43, 48]); audio[:, 0] += p; audio[:, 1] += p
    audio = reverb(audio); audio /= max(1e-9, np.abs(audio).max()) / 0.9

    nf = int(DUR * FPS)
    for fi in range(nf):
        t = fi / FPS; fr = Frame()
        # titre
        fr.text((W // 2, 180), "Wait for Jupiter", 84, (240, 240, 245), glow=False)
        fr.text((W // 2, 262), "every orbit is a note · 1 Earth year = 2 s", 34, (150, 155, 170), medium=True)
        # soleil
        fr.dot((CX, CY), 26, (255, 196, 90), glow=1.2)
        # ligne de départ (midi)
        fr.line([(CX, CY - 470), (CX, CY - 90)], (60, 64, 80), 2, glow=False)
        for i, (name, d, colh, note, r) in enumerate(PL):
            col = hexrgb(colh); per = period_s(d)
            done = [h for h in H_[name] if h <= t]
            flash = math.exp(-(t - done[-1]) * 5) if done else 0.0
            if name == "Jupiter" and t > TJ: flash = max(flash, 0.35)
            dim = tuple(int(c * (0.22 + 0.5 * flash)) for c in col)
            fr.circle((CX, CY), r, dim, 2, glow=flash > 0.05)
            a = 2 * math.pi * (min(t, TJ) / per if name == "Jupiter" else t / per)
            # traînée
            for k in range(14):
                ak = a - k * 0.05 * (1 + 2.5 / (1 + per))
                x, y = CX + r * math.sin(ak), CY - r * math.cos(ak)
                fr.dot((x, y), max(2, 11 - k * 0.7), tuple(int(c * (1 - k / 14) * 0.6) for c in col), glow=0.4 * (1 - k / 14))
            x, y = CX + r * math.sin(a), CY - r * math.cos(a)
            fr.dot((x, y), 13 if name != "Jupiter" else 19, col, glow=1.0 + flash)
            # couloir du bas
            ly = LANE_Y0 + i * LANE_H
            fr.text((70, ly), name, 30, col, anchor="lm", medium=True)
            fr.db.line([(250, ly), (1010, ly)], fill=(30, 33, 44), width=2)
            span = 6.0
            for h in done:
                if t - h < span:
                    xx = 1010 - (t - h) / span * 760
                    hh = 26 if name != "Jupiter" else 40
                    fr.line([(xx, ly + hh / 2), (xx, ly - hh / 2)], col, 4, glow=True)
            cnt = len(done)
            fr.text((1010, ly - 34), f"×{cnt}", 24, tuple(int(c * 0.8) for c in col), anchor="rm", medium=True)
        # compteur
        yrs = min(t, TJ) / YEAR_S
        fr.text((W // 2, 1340), f"{yrs:5.1f} Earth years", 40, (205, 208, 220), medium=True)
        if t > TJ:
            k = min(1, (t - TJ) / 0.6)
            fr.text((W // 2, 1790), "Jupiter: 1 lap. Mercury: 49.", 46, tuple(int(c * k) for c in (230, 190, 255)), glow=True)
        fr.text((W // 2, 1870), "data: NASA Planetary Fact Sheet · orbits not to scale", 22, (90, 94, 110), medium=True)
        wr.add(fr.compose())
    wr.close(audio)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "essai_planetes.mp4")
