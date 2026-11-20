import math, sys, json
def sim(ratio, x1=1.0, x2=2.0, v2=-1.0, w=0.0):
    # small m=1 at x1 (left), big M=ratio at x2, wall at 0; point blocks
    m, M = 1.0, float(ratio); v1=0.0; t=0.0; ev=[]
    while True:
        # next times
        tb = (x2-x1)/(v1-v2) if v1>v2 else math.inf
        tw = -x1/v1 if v1<0 else math.inf
        if tb==math.inf and tw==math.inf: break
        if tb<tw:
            dt=tb; x1+=v1*dt; x2+=v2*dt; x1=x2=min(x1,x2) if False else x1
            x2=x1
            nv1=((m-M)*v1+2*M*v2)/(m+M); nv2=((M-m)*v2+2*m*v1)/(m+M); v1,v2=nv1,nv2; kind='b'
        else:
            dt=tw; x1=0.0; x2+=v2*dt; v1=-v1; kind='w'
        t+=dt; ev.append((t,kind))
        if v1>=0 and v2>=v1 and not (v1<0): 
            # no more collisions if both moving right and big faster or equal
            if v2>=v1: break
    return ev
for n in range(1,8):
    r=100**(n-1)
    th=math.atan(math.sqrt(1/r))
    f=math.ceil(math.pi/th)-1
    if n<=6:
        ev=sim(r); c=len(ev); tl=ev[-1][0]
    else: c=None; tl=None
    print(n, r, c, f, tl)
