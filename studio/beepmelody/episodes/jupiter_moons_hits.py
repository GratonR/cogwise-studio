"""BeepMelody · Jupiter's moons · real lap times for the episode window (co-pilot step 3).
Positions of Io, Europa, Ganymede, Callisto from Meeus, Astronomical Algorithms ch. 44 (Lieske E5 theory),
via PyMeeus (pip install pymeeus). A "lap" = the moon crosses a fixed direction (the START LINE, +X of the
jovian equatorial frame at the start date, held fixed in space). Crossing times are linearly interpolated between 0.01-day samples.
Checks printed: mean lap time per moon vs the IMCCE sidereal period (jupiter_moons_draft.csv), and the Laplace
relation  L_Io - 3 L_Europa + 2 L_Ganymede = 180 deg  (the reason the three never line up on one side).

    python3 jupiter_moons_hits.py <out.csv> [start YYYY-MM-DD] [days]
"""
import sys, csv, math, os
import numpy as np
from pymeeus.JupiterMoons import JupiterMoons as J
from pymeeus.Epoch import Epoch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
Y, M, D = map(int, (sys.argv[2] if len(sys.argv) > 2 else "2026-11-16").split("-"))
DAYS = float(sys.argv[3]) if len(sys.argv) > 3 else 130.0
MOONS = ["Io", "Europa", "Ganymede", "Callisto"]
STEP = 0.01
e0 = Epoch(Y, M, D + 0.0)
ts = np.arange(0, DAYS + STEP, STEP)
XYZ = np.array([J.rectangular_positions_jovian_equatorial(e0 + float(t)) for t in ts])      # (n, 4, 3) in Jupiter radii
R = np.hypot(XYZ[:, :, 0], XYZ[:, :, 2]); H = XYZ[:, :, 1]
A = np.arctan2(XYZ[:, :, 2], XYZ[:, :, 0])
A = np.unwrap(A, axis=0)
# the frame's X axis follows Jupiter's heliocentric longitude (~0.08 deg/day): remove it so the START LINE is fixed in space
from pymeeus.Jupiter import Jupiter
LJ = np.unwrap(np.radians([Jupiter.geometric_heliocentric_position(e0 + float(t))[0]() for t in np.arange(0, DAYS + 2, 1.0)]))
A = A - (np.interp(ts, np.arange(0, DAYS + 2, 1.0), LJ) - LJ[0])[:, None]
np.savez_compressed(OUT.replace(".csv", "_pos.npz"), t=ts, ang=A, r=R, h=H)   # positions for the 3D scene
rows = []
for k, m in enumerate(MOONS):
    a = A[:, k]; n0 = math.floor(a[0] / (2 * math.pi))
    laps = np.floor(a / (2 * math.pi)) - n0
    for j in np.nonzero(np.diff(laps) > 0)[0]:
        target = (n0 + laps[j + 1]) * 2 * math.pi
        f = (target - a[j]) / (a[j + 1] - a[j])
        rows.append({"day": round(ts[j] + f * STEP, 4), "moon": m, "lap": int(laps[j + 1]),
                     "source": "Meeus ch.44 (Lieske E5) via PyMeeus; period checked vs IMCCE + NASA NSSDC"})
rows.sort(key=lambda r: r["day"])
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["day", "moon", "lap", "source"]); w.writeheader(); w.writerows(rows)
per = {r["moon"]: float(r["sidereal_period_d"]) for r in csv.DictReader(open(os.path.join(HERE, "jupiter_moons_draft.csv")))}
print("window", f"{Y}-{M:02d}-{D:02d}", "+", DAYS, "days ->", len(rows), "laps")
for m in MOONS:
    d = [r["day"] for r in rows if r["moon"] == m]
    mean = (d[-1] - d[0]) / (len(d) - 1) if len(d) > 1 else float("nan")
    print(f"{m:9s} laps {len(d):3d}  first day {d[0]:7.3f}  mean lap {mean:.4f} d  IMCCE {per[m]:.6f} d  diff {100*(mean/per[m]-1):+.3f} %")
lap = A[:, 0] - 3 * A[:, 1] + 2 * A[:, 2]
lap = (np.degrees(lap) % 360)
print("Laplace L1-3L2+2L3: min %.2f  max %.2f deg (theory: 180)" % (lap.min(), lap.max()))
