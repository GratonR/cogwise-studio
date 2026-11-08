"""3 BeepMelody music directions, all programmed: same event list -> notes. numpy only."""
import numpy as np, wave, sys, subprocess
from scipy.signal import lfilter
SR=44100; DUR=22.0
rng=np.random.default_rng(3)
def T(d): return np.arange(int(d*SR))/SR
def mf(m): return 440*2**((m-69)/12)
def lp(x,a): return lfilter([a],[1,a-1],x)
def hp(x,a): return x-lp(x,a)
def env(t,a=.004,dec=.1,s=.3,d=None,r=.03):
    e=np.where(t<a,t/a,s+(1-s)*np.exp(-(t-a)/dec))
    if d is not None: e=e*np.clip((d-t)/r,0,1)
    return e
class Mix:
    def __init__(s): s.L=np.zeros(int((DUR+2)*SR)); s.R=s.L.copy()
    def put(s,x,t,pan=0.0,g=1.0):
        i=int(t*SR); x=x[:len(s.L)-i]*g
        s.L[i:i+len(x)]+=x*(1-max(pan,0)); s.R[i:i+len(x)]+=x*(1+min(pan,0))
    def out(s,path):
        y=np.stack([s.L,s.R],1); y=y[:int(DUR*SR)]
        fade=np.clip((DUR-T(DUR))/1.0,0,1)[:,None]; y*=fade
        y/=np.abs(y).max()+1e-9; y=(y*0.89*32767).astype(np.int16)
        with wave.open(path+'.wav','wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(y.tobytes())
        subprocess.run(['ffmpeg','-v','error','-y','-i',path+'.wav','-b:a','192k',path+'.mp3'],check=True)

# same data for all three: 26 events, value grows ~exponentially, last one = record
N=26; times=np.linspace(1.5,18.5,N)**1.0
times=1.5+17*(np.linspace(0,1,N)**0.75)        # events get denser toward the end
vals=np.exp(np.linspace(0,1,N)*np.log(1000))*(1+0.15*rng.standard_normal(N)); vals=np.maximum.accumulate(vals)
def deg(v,scale,base,span=2):   # value -> scale degree (log), span octaves
    k=int(np.log(v)/np.log(1000)*(len(scale)*span-1)); return base+scale[k%len(scale)]+12*(k//len(scale))

def sq(f,d,duty=.5): t=T(d); return np.where((t*f)%1<duty,1.,-1.),t
def tri(f,d): t=T(d); return 2*np.abs(2*((t*f)%1)-1)-1,t
def saw(f,d,det=0): t=T(d); return sum(2*((t*f*(1+k*det))%1)-1 for k in (-1,0,1))/3,t
def noise(d): return rng.standard_normal(int(d*SR)),T(d)

# ---------- A: chiptune 8-bit, 128 BPM ----------
def A():
    m=Mix(); bpm=128; b=60/bpm; PENTA=[0,3,5,7,10]
    prog=[48,44,46,43]                    # Cm Ab Bb G
    nb=int(DUR/b)
    for i in range(nb):
        t=i*b; root=prog[(i//8)%4]
        w,tt=tri(mf(root-12 if i%2==0 else root),b*.9); m.put(w*env(tt,dec=.2,s=.6,d=b*.9)*.22,t)
        if i%2==0: n,tt=noise(.12); f=np.sin(2*np.pi*np.cumsum(120*np.exp(-tt*25)+40)/SR); m.put(f*np.exp(-tt*25)*.45,t)
        else: n,tt=noise(.1); m.put(hp(n,.3)*np.exp(-tt*35)*.18,t)
        n,tt=noise(.03); m.put(hp(n,.7)*np.exp(-tt*150)*.07,t+b/2,.3)
    for k,(t,v) in enumerate(zip(times,vals)):
        note=deg(v,PENTA,60); last=k==N-1; d=.9 if last else .16
        w,tt=sq(mf(note),d,.25 if k%2 else .125); m.put(lp(w*env(tt,dec=.06 if not last else .5,s=.4,d=d),.5)*.16,t,-.2)
        m.put(lp(w*env(tt,dec=.06,s=.4,d=d),.5)*.05,t+3*b/4,.4)      # echo
        if last:
            for j,n2 in enumerate([note,note+7,note+12,note+19]):
                w,tt=sq(mf(n2),.12,.5); m.put(w*env(tt,dec=.05,s=.3,d=.12)*.1,t+j*.06)
    m.out('A_chiptune')

# ---------- B: synthwave neon, 100 BPM ----------
def B():
    m=Mix(); bpm=100; b=60/bpm; MIN=[0,2,3,5,7,8,10]
    prog=[(45,48,52),(41,45,48),(43,47,50),(40,43,47)]   # Am F G Em
    bar=4*b
    for j in range(int(DUR/bar)+1):
        ch=prog[j%4]; t0=j*bar
        for n in ch:                                  # pad
            w,tt=saw(mf(n+12),bar,.006); e=np.minimum(tt/.6,1)*np.clip((bar-tt)/.3,0,1)
            m.put(lp(w,.06)*e*.07,t0,(n%3-1)*.4)
        for i in range(16):                           # 16th arp
            n=ch[i%3]+12*(1+(i//3)%2); w,tt=saw(mf(n+12),b/4*.8,.004)
            m.put(lp(w*env(tt,dec=.05,s=.1,d=b/4*.8),.12)*.06,t0+i*b/4,.5 if i%2 else -.5)
        w,tt=saw(mf(ch[0]-12),bar,.003)               # bass, 8ths
        for i in range(8): m.put(lp(w[:int(b/2*SR)]*env(tt[:int(b/2*SR)],dec=.12,s=.5,d=b/2*.9),.08)*.25,t0+i*b/2)
        for i in range(4):                            # drums: kick 1&3, gated snare 2&4
            t=t0+i*b
            if i%2==0: n,tt=noise(.25); m.put(np.sin(2*np.pi*np.cumsum(100*np.exp(-tt*18)+45)/SR)*np.exp(-tt*10)*.5,t)
            else: n,tt=noise(.25); m.put(lp(n,.4)*(tt<.18)*np.exp(-tt*4)*.16,t)
    for k,(t,v) in enumerate(zip(times,vals)):        # events = FM bell
        note=deg(v,MIN,69,1.5); d=1.2; tt=T(d); f=mf(note)
        bell=np.sin(2*np.pi*f*tt+2.5*np.exp(-tt*6)*np.sin(2*np.pi*f*3.5*tt))*np.exp(-tt*(2 if k==N-1 else 5))
        m.put(bell*.13,t,(k%5-2)*.2); m.put(bell*.04,t+.36,.6)
    m.out('B_synthwave')

# ---------- C: cinematic tension, tempo 70 -> 150 ----------
def C():
    m=Mix(); D=[0,1,5,7,8]                           # phrygian-ish, dark
    tt=T(DUR); 
    for n,g in ((38,.12),(45,.08),(50,.05)):          # drone that swells
        w=sum(np.sin(2*np.pi*mf(n)*(1+d)*tt) for d in (-.002,0,.002))/3
        m.put(lp(w,.05)*g*(0.3+0.7*tt/DUR),0)
    t=0.5; 
    while t<18.6:                                     # heartbeat kick, accelerating
        bpm=70+80*(t/18.6)**1.5; b=60/bpm
        for off,g in ((0,.55),(.18*b,.3)):
            n,t2=noise(.3); m.put(np.sin(2*np.pi*np.cumsum(70*np.exp(-t2*20)+38)/SR)*np.exp(-t2*9)*g,t+off)
        t+=b
    rs=T(3.0); n=rng.standard_normal(len(rs))         # riser before the record
    m.put(lp(hp(n,.2),.25)*(rs/3)**2*.035,16.0)
    for k,(t,v) in enumerate(zip(times,vals)):        # events = glassy pluck
        note=deg(v,D,62,2); d=.8; t2=T(d); f=mf(note)
        x=(np.sin(2*np.pi*f*t2)+.4*np.sin(2*np.pi*2*f*t2)+.2*np.sin(2*np.pi*3.01*f*t2))*np.exp(-t2*6)
        m.put(x*.2,t,(k%3-1)*.4); m.put(x*.06,t+.45,-(k%3-1)*.4)
    t=times[-1]; n,t2=noise(3)                        # impact + low boom on the record
    m.put(lp(lp(n,.05),.05)*np.exp(-t2*2.5)*.5,t); m.put(np.sin(2*np.pi*np.cumsum(60*np.exp(-t2*3)+30)/SR)*np.exp(-t2*1.2)*.6,t)
    for n2 in (62,69,74,77): x=np.sin(2*np.pi*mf(n2)*T(3))*np.exp(-T(3)*1.2); m.put(x*.07,t)
    m.out('C_cinematique')
C()
