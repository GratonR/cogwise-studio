"""BeepMelody · supermoons — data builder (step 1).
Every full moon 1900-2027 with the Earth-Moon centre distance at the instant of full moon.
Primary: JPL DE421 via Skyfield (skyfield-data package). Cross-check: PyEphem (ELP lunar theory),
max diff 2.9 km. Spot-checked against F. Espenak's 'Full Moon at Perigee' tables (astropixels.com),
diff <= 4 km (2025-2027 rows identical to the minute).
Criteria flagged per row:
  espenak90 : relative distance >= 0.90 between the orbit's apogee and perigee (Espenak / Nolle 1979)
  tad360    : distance < 360,000 km (timeanddate.com)
  close3568 : distance <= 356,800 km (Espenak 'Closest Full Moon Perigees' list)
usage: python3 supermoons_data.py   -> writes supermoons_draft.csv next to this file
"""
import os, csv, warnings
import numpy as np
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = ("JPL DE421 (Skyfield) ; cross-check PyEphem ; Espenak astropixels.com/ephemeris/moon/fullperigee1901.html "
       "+ fullperigee2001.html")

def main():
    import skyfield_data, ephem
    from skyfield.api import load_file, load
    from skyfield import almanac
    from skyfield.searchlib import find_minima, find_maxima
    eph = load_file(os.path.join(skyfield_data.get_skyfield_data_path(), "de421.bsp"))
    ts = load.timescale(builtin=True)
    E, M = eph["earth"], eph["moon"]
    t0, t1 = ts.utc(1900, 1, 2), ts.utc(2027, 3, 31)
    t, ph = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    fm = t[ph == 2]
    dist = lambda tt: (M - E).at(tt).distance().km
    dist.step_days = 1.0
    tp, dp = find_minima(t0, t1, dist); ta, da = find_maxima(t0, t1, dist)
    d = dist(fm)
    rows = []
    for ti, di in zip(fm, d):
        j = ti.tt
        k = int(np.argmin(abs(tp.tt - j))); ka = int(np.argmin(abs(ta.tt - j)))
        rel = (da[ka] - di) / (da[ka] - dp[k])
        utc = ti.utc_strftime("%Y-%m-%d %H:%M")
        m = ephem.Moon(); m.compute(ephem.Date(utc.replace("-", "/")))
        de = m.earth_distance * ephem.meters_per_au / 1000
        rows.append(dict(full_moon_utc=utc, dist_km=round(di, 1), dist_km_pyephem=round(de, 1),
                         perigee_km=round(dp[k], 1), apogee_km=round(da[ka], 1), rel_dist=round(rel, 4),
                         espenak90=int(rel >= 0.9), tad360=int(di < 360000), close3568=int(di <= 356800),
                         source=SRC))
    out = os.path.join(HERE, "supermoons_draft.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(out, len(rows))

if __name__ == "__main__":
    main()
