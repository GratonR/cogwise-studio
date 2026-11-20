"""BeepMelody · Chocs de pi · retravail r1 (piste « medley ») : trois expériences, un seul pi.
Génère la liste d'événements des 3 actes (≈ 22 s chacun). Aucune valeur inventée :
- acte 1 : chocs de blocs, simulation exacte (pi_clacks_sim.sim), niveaux 1..5 (3, 31, 314, 3141, 31415) ;
  Galperin 2003 (doi:10.1070/RD2003v008n04ABEH000252) + arXiv:2004.14796.
- acte 2 : aiguilles de Buffon (longueur = écart des lattes), P(croise) = 2/pi, donc pi ≈ 2N/C ;
  Buffon 1777 (Essai d'arithmétique morale) + Badger 1994 (Mathematics Magazine 67(2):83-91) ; tirage pseudo-aléatoire graine fixe.
- acte 3 : fléchettes uniformes dans un carré, P(dans le quart de disque) = pi/4, donc pi ≈ 4·in/N ;
  méthode de Monte-Carlo (Metropolis & Ulam 1949, JASA 44(247):335-341) ; graine fixe.
Les actes 2 et 3 sont des SIMULATIONS : l'écran le dira (« simulation »)."""
import os, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "pi_clacks_sim.py")).read().split("for n in range")[0])

ACT = [(0.0, 22.0), (22.0, 44.0), (44.0, 66.0)]
BLOCK_LEVELS = [(1, 0.6, 2.4), (2, 2.6, 5.2), (3, 5.4, 8.9), (4, 9.1, 14.0), (5, 14.2, 21.4)]

def act1():
    ev = []
    for lv, a, b in BLOCK_LEVELS:
        r = 100 ** (lv - 1); w = 1 / math.sqrt(r); e = sim(r)
        if len(e) == 1: tau = np.array([0.5])
        else:
            tau = np.array([math.asinh((t - 2.0) / w) for t, _ in e])
            tau = (tau - tau[0]) / (tau[-1] - tau[0])
        for (t, k), u in zip(e, tau): ev.append(dict(t=a + u * (b - a), act=1, kind=k, level=lv))
    return ev

def accel_times(n, a, b, p=2.6):
    """n événements de a à b, de plus en plus serrés (densité ∝ temps^(p-1))."""
    u = (np.arange(1, n + 1) / n) ** (1 / p)
    return a + 0.4 + u * (b - a - 0.9)

def act2(n=1400, seed=27):
    rs = np.random.RandomState(seed); ev = []
    y = rs.uniform(0, 1, n); th = rs.uniform(0, math.pi, n)          # centre entre deux lattes (écart 1), angle
    half = 0.5 * np.sin(th)                                          # demi-projection, aiguille de longueur 1
    cross = (y - half < 0) | (y + half > 1)
    for t, c, yy, tt in zip(accel_times(n, *ACT[1]), cross, y, th):
        ev.append(dict(t=float(t), act=2, kind="x" if c else "o", y=float(yy), th=float(tt)))
    return ev

def act3(n=6000, seed=7):
    rs = np.random.RandomState(seed); ev = []
    x = rs.uniform(0, 1, n); y = rs.uniform(0, 1, n); inside = x * x + y * y <= 1
    for t, i, xx, yy in zip(accel_times(n, *ACT[2], p=3.0), inside, x, y):
        ev.append(dict(t=float(t), act=3, kind="in" if i else "out", x=float(xx), y=float(yy)))
    return ev

def events(): return act1() + act2() + act3()

if __name__ == "__main__":
    a2 = act2(); a3 = act3()
    C = sum(e["kind"] == "x" for e in a2); I = sum(e["kind"] == "in" for e in a3)
    print("acte1 chocs:", len(act1()))
    print("acte2 aiguilles:", len(a2), "croisent:", C, "pi ≈", 2 * len(a2) / C)
    print("acte3 fléchettes:", len(a3), "dedans:", I, "pi ≈", 4 * I / len(a3))
    for name, ev in (("a2", a2), ("a3", a3)):
        ts = np.array([e["t"] for e in ev]); print(name, "rate last 2s:", (ts > ts[-1] - 2).sum() / 2, "first 2s:", (ts < ts[0] + 2).sum() / 2)
