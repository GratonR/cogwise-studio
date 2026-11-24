"""BEEPMELODY — Geminids 2026, one night (13 -> 14 Dec 2026) seen from 40.0 N, 75.0 W (US East, EST = UT-5).
Model (written on screen as "MODEL"): expected Geminids per hour HR = ZHR(t) x sin(radiant altitude), perfect dark sky (LM 6.5),
counted only between astronomical dusk and dawn.
  ZHR(t) = 150 x 10^(-B |dLambda|), peak 14 Dec 2026 14:00 UT (lambda 262.2), B = 0.78 /deg  -> ZHR >= 100 for ~11 h (broad peak)
  sources: IMO 2026 Meteor Shower Calendar (ZHR 150, peak Dec 14 14h UT, ZHR >= 100 over 10-12 h, radiant 112 +33, 35 km/s);
           IGN Spain, astronomia.ign.es/en/geminidas (peak Dec 14 14h UT, broad ~12 h peak, up to 150/h, 35 km/s);
           HR = ZHR sin(h) : IMO observing method (zenith correction, gamma = 1).
  radiant RA 7h28m Dec +33 (J2000): IMO calendar 2026 + IMO Meteor Activity Outlook 13-19 Dec 2025 (07:28 +33).
  altitude, dusk/dawn, moonset, moon phase: PyEphem (VSOP87/ELP), cross-check: EarthSky (radiant highest ~2 a.m.),
  RMG / Farmers' Almanac (crescent moon sets ~9 p.m.), IGN (moon ~20 % lit).
    python3 geminids_data.py   -> geminids.csv (5-min rows)
"""
import ephem, math, csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
LAT, LON, TZ = "40", "-75", -5
ZHR_MAX, B = 150.0, 0.78
PEAK = ephem.Date("2026/12/14 14:00")
SRC = "IMO cal2026 + IGN (ZHR, peak); PyEphem radiant 7h28 +33 (IMO); HR=ZHR*sin(h)"

def observer(horizon="0"):
    o = ephem.Observer(); o.lat, o.lon, o.pressure, o.horizon = LAT, LON, 0, horizon; return o

def main():
    o = observer("-18"); o.date = "2026/12/13 20:00"
    dusk = o.next_setting(ephem.Sun(), use_center=True); dawn = o.next_rising(ephem.Sun(), use_center=True)
    om = observer("-0:34"); om.date = "2026/12/13 20:00"; moonset = om.next_setting(ephem.Moon())   # almanac: upper limb + refraction
    mo = ephem.Moon(); mo.compute("2026/12/14 01:00")
    rad = ephem.FixedBody(); rad._ra, rad._dec, rad._epoch = ephem.hours("7:28"), ephem.degrees("33"), ephem.J2000
    rows = []; cum = 0.0
    t0 = ephem.Date("2026/12/13 23:00")          # 18:00 EST
    for i in range(12 * 12 + 1):                 # every 5 min to 06:00 EST
        t = ephem.Date(t0 + i * 5 / 1440 + 1e-7)
        ob = observer(); ob.date = t; rad.compute(ob)
        alt = math.degrees(rad.alt); dl = abs(t - PEAK) * 360 / 365.2422
        zhr = ZHR_MAX * 10 ** (-B * dl)
        dark = dusk <= t < dawn
        hr = zhr * max(0.0, math.sin(rad.alt)) if dark else 0.0
        n = hr * 5 / 60; cum += n
        lt = ephem.Date(t + TZ / 24).datetime()
        rows.append(dict(time_ut=ephem.Date(t).datetime().strftime("%Y-%m-%d %H:%M"), local_est=lt.strftime("%Y-%m-%d %H:%M"),
                         radiant_alt_deg=f"{alt:.1f}", radiant_az_deg=f"{math.degrees(rad.az):.1f}", zhr_model=f"{zhr:.1f}",
                         dark=int(dark), expected_per_hour=f"{hr:.1f}", expected_in_5min=f"{n:.3f}", cumulative=f"{cum:.1f}", source=SRC))
    with open(os.path.join(HERE, "geminids.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    loc = lambda d: ephem.Date(d + TZ / 24).datetime().strftime("%H:%M")
    pk = max(rows, key=lambda r: float(r["expected_per_hour"]))
    hi = max(rows, key=lambda r: float(r["radiant_alt_deg"]))
    print("dusk", loc(dusk), "dawn", loc(dawn), "moonset", loc(moonset), "moon %", round(mo.phase, 1))
    print("peak rate", pk["local_est"], pk["expected_per_hour"], "| radiant highest", hi["local_est"], hi["radiant_alt_deg"])
    print("total expected", round(cum, 1))
if __name__ == "__main__": main()
