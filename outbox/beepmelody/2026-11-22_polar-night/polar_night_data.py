import datetime as dt, ephem, csv
from astral import LocationInfo, Observer
from astral.sun import daylight, sun
import math
C={'tromso':(69.6492,18.9553),'quito':(-0.2299,-78.5249)}
def eph(lat,lon,d):
    o=ephem.Observer();o.lat=str(lat);o.lon=str(lon);o.pressure=0;o.horizon='-0:34'
    o.date=ephem.Date(dt.datetime(d.year,d.month,d.day)) ; s=ephem.Sun()
    # day length within UTC-local-noon-centred window: use local solar day
    noon=dt.datetime(d.year,d.month,d.day,12)-dt.timedelta(hours=lon/15)
    start=noon-dt.timedelta(hours=12); end=noon+dt.timedelta(hours=12)
    # sample altitude each 30s, count minutes with upper limb above horizon
    n=0;t=start;step=dt.timedelta(seconds=30)
    while t<end:
        o.date=ephem.Date(t); s.compute(o)
        if s.alt> math.radians(-0.8333): n+=1
        t+=step
    return n*30/3600
def ast(lat,lon,d):
    ob=Observer(latitude=lat,longitude=lon)
    try:
        sr,ss=daylight(ob,d)
        return (ss-sr).total_seconds()/3600
    except ValueError as e:
        return 0.0 if 'below' in str(e) or 'never' in str(e).lower() and 'rise' in str(e) else str(e)
d0=dt.date(2026,9,23)
w=csv.writer(open('daylen.csv','w'));w.writerow(['date','tromso_h_ephem','tromso_h_astral','quito_h_ephem','quito_h_astral'])
for i in range(365):
    d=d0+dt.timedelta(i)
    w.writerow([d,round(eph(*C['tromso'],d),3),ast(*C['tromso'],d) if True else '',round(eph(*C['quito'],d),3),round(ast(*C['quito'],d),3)])
