import numpy as np, soundfile as sf, sys
sys.argv=['x','none']
exec(open('render.py').read().split("if __name__")[0])
SR=24000; rng=np.random.default_rng(9)
tl=build_timeline()
total=sum(round(T_*FPS)/FPS for _,T_,_ in tl); N=int(total*SR)+2*SR
voice=np.zeros(N); mus=np.zeros(N); fx=np.zeros(N)
off=0.0; S={}
for sid,T_,L in tl:
    S[sid]=(off,round(T_*FPS)/FPS,L)
    for it in L:
        s,_=sf.read(it[3]); i=int((off+it[0])*SR); voice[i:i+len(s)]+=s
    off+=round(T_*FPS)/FPS
def put(buf,x,ts,g=1.0):
    i=int(ts*SR)
    if i<0: x=x[-i:]; i=0
    n=min(len(x),N-i)
    if n>0: buf[i:i+n]+=g*x[:n]
def tt(d): return np.arange(int(d*SR))/SR
def hz(m): return 440*2**((m-69)/12)
def pluck(m,d=0.6,a=0.3):
    f=hz(m); P=max(2,int(SR/f)); n=int(d*SR); out=np.zeros(n+P)
    out[:P]=np.convolve(rng.uniform(-1,1,P),np.ones(3)/3,'same')
    for i in range(P,n,P):
        seg=out[i-P:i]; out[i:i+P]=(0.5*(seg+np.roll(seg,-1))*0.994)[:len(out[i:i+P])]
    o=out[:n]; return a*o*np.exp(-tt(d)*3)
def marimba(m,d=0.5,a=0.2):
    f=hz(m); t=tt(d)
    return a*(np.sin(2*np.pi*f*t)*np.exp(-t*7)+0.3*np.sin(2*np.pi*f*4*t)*np.exp(-t*30))*np.minimum(1,t*400)
def bass(m,d=0.4,a=0.25):
    f=hz(m); t=tt(d); return a*(np.sin(2*np.pi*f*t)+0.25*np.sin(4*np.pi*f*t))*np.exp(-t*4)*np.minimum(1,t*200)
def kick(a=0.5,d=0.3,f0=130,f1=45,k=14):
    t=tt(d); f=f1+(f0-f1)*np.exp(-t*25); return a*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*k)
def shaker(a=0.05):
    x=np.diff(rng.standard_normal(int(.05*SR)+1)); return a*x*np.exp(-tt(.05)*70)
def tick(a=0.12,f=2500):
    t=tt(.03); return a*(np.sin(2*np.pi*f*t)+0.5*rng.standard_normal(len(t)))*np.exp(-t*160)
def pad(ms,d,a=0.05):
    t=tt(d); env=np.minimum(1,np.minimum(t/0.6,(d-t)/0.6))
    return a*env*sum(np.sin(2*np.pi*hz(m)*t)+0.4*np.sin(2*np.pi*hz(m)*1.003*t+1) for m in ms)
def noise_band(d,a,win):
    return a*np.convolve(rng.standard_normal(int(d*SR)),np.ones(win)/win,'same')
def whoosh(d=0.55,a=0.35):
    t=tt(d); env=np.sin(np.pi*t/d)**2
    lo=noise_band(d,1,6); hi=np.diff(np.concatenate([[0],lo]))*4
    mixf=t/d; return a*env*(lo*(1-mixf)+hi*mixf)
def riser(d=1.2,a=0.25):
    t=tt(d); f=200+600*(t/d)**2
    return a*(t/d)**2*(0.5*np.sin(2*np.pi*np.cumsum(f)/SR)+noise_band(d,1.5,4))
def stinger():
    x=kick(0.9,1.4,90,35,3); x[:int(1.2*SR)]+=noise_band(1.2,0.25,3)*np.exp(-tt(1.2)*4)
    for m in (38,39,45,50): x[:int(1.0*SR)]+=pluck(m,1.0,0.25)
    return x
def bwomp():
    t=tt(.6); f=320*np.exp(-t*3); return 0.3*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3)
def sparkle(t0,base=84,n=7,a=0.08):
    for k in range(n): put(mus,marimba(base+[0,4,7,12,16,19,24][k%7],0.5,a),t0+k*0.07)
def heartbeat(t0,a=0.6):
    put(mus,kick(a,0.25,70,40,18),t0); put(mus,kick(a*0.7,0.25,65,38,18),t0+0.17)

def steps(o,T,bpm,sub=2):
    b=60/bpm/sub; k=0
    while k*b<T-0.05: yield k,o+k*b; k+=1


def hammer(ts,a=0.25):
    put(fx,kick(a,0.12,900,500,45),ts); put(fx,tick(a*0.6,3200),ts)
def thud(ts,a=0.4): put(fx,kick(a,0.25,160,60,16),ts)
def crack(ts,a=0.3):
    for k in range(5): put(fx,noise_band(0.05,a,1)*np.exp(-tt(0.05)*60),ts+k*0.05+rng.uniform(0,.03))
def thunder(ts):
    d=2.2; put(fx,noise_band(d,0.5,40)*np.exp(-tt(d)*1.8),ts); put(fx,kick(0.6,1.5,60,30,2),ts)
prog=[(48,[60,64,67,72]),(43,[59,62,67,71]),(45,[57,60,64,69]),(41,[57,60,65,69])]
def warm(o,T,bpm=96,a=0.13,start=0,sh=True):
    for k,ts in steps(o,T,bpm):
        root,ch=prog[(k//8+start)%4]
        put(mus,marimba(ch[[0,1,2,3,2,1,2,3][k%8]],0.45,a),ts)
        if k%4==0: put(mus,bass(root,0.5,0.26),ts)
        if sh: put(mus,shaker(0.03 if k%2 else 0.018),ts)
def trumpet(ts,a=0.18,d=0.9):
    t_=tt(d); f=330+120*np.sin(np.pi*t_/d)+8*np.sin(2*np.pi*6*t_)
    ph=np.cumsum(f)/SR; saw=2*(ph%1)-1
    x=np.convolve(saw,np.ones(4)/4,'same')*np.sin(np.pi*t_/d)**0.5
    put(fx,a*x,ts)
def crowd(o,T,a=0.03):
    put(fx,noise_band(T,a,60)*np.minimum(1,tt(T)*2),o)
def creak(ts,a=0.12):
    t_=tt(0.35); f=180+60*np.sin(2*np.pi*3*t_); put(fx,a*np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t_*6)*0.5,ts)
def drip_snd(ts,a=0.12):
    t_=tt(0.12); f=900+1400*np.exp(-t_*40); put(fx,a*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t_*30),ts)
def birds(o,T,a=0.05):
    k=o+0.3
    while k<o+T-0.3:
        t_=tt(0.09); f=2800+900*np.sin(2*np.pi*12*t_); put(fx,a*np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t_/0.09),k)
        put(fx,a*0.8*np.sin(2*np.pi*np.cumsum(f*1.1)/SR)*np.sin(np.pi*t_/0.09),k+0.13); k+=rng.uniform(0.9,1.8)
def walk_drips(o,T):
    k=o+0.2
    while k<o+T: drip_snd(k,0.08); k+=0.55
def snip(ts,a=0.35):
    put(fx,noise_band(0.06,a,1)*np.exp(-tt(0.06)*50),ts); put(fx,tick(a*0.8,5200),ts+0.01)
def flutter(ts,d=0.8,a=0.05):
    t_=tt(d); put(fx,a*noise_band(d,1,2)*(0.5+0.5*np.sign(np.sin(2*np.pi*18*t_)))*np.sin(np.pi*t_/d),ts)
o,T,L=S['hook']
put(mus,pad([45,52,57,60],T,0.05),o)
for k,ts in steps(o+0.2,T-0.2,76,1): put(mus,pluck([69,64,60,62][k%4],1.0,0.2),ts)
flutter(o+L[1][0]+0.2,1.5)
o,T,L=S['garden']; warm(o,T,bpm=100); birds(o,T)
o,T,L=S['struggle']
put(mus,pad([38,45,50],T,0.05),o)
hb=o+0.2
while hb<o+T-0.3: heartbeat(hb,0.4); hb+=0.7
for k in range(10): put(fx,tick(0.07,1800 if k%2 else 2400),o+k*0.4)
o,T,L=S['cut']
for k,ts in steps(o,T,120):
    if k%2==0: put(mus,pluck([52,55][k//2%2],0.3,0.2),ts)
s0=o+L[0][0]+(L[0][1]-L[0][0])*.7
snip(s0-0.35); snip(s0)
put(fx,bwomp(),s0+0.25)
o,T,L=S['wait']
put(mus,pad([48,52,55],T,0.04),o)
for k,ts in steps(o,T,70,1): put(mus,marimba([72,74,76,74][k%4],1.0,0.1),ts)
for k in range(8): put(fx,tick(0.08,2200 if k%2 else 1700),o+L[1][0]+k*0.5)
o,T,L=S['never']
put(mus,pad([45,48,52],T,0.055),o)
for k,ts in steps(o,T,60,1): put(mus,marimba([76,72,69,64][k%4],1.4,0.12),ts)
for k in range(3): put(fx,kick(0.25,0.2,200,90,18),o+0.35+k*1.43)
flutter(o+0.3,2.5,0.04)
o,T,L=S['dadaji']
put(mus,pad([48,52,55,60],T,0.04),o)
for k,ts in steps(o,T,80,1): put(mus,marimba([60,64,67,72,67,64][k%6],0.9,0.09),ts)
put(fx,riser(1.0,0.2),o+L[1][0]-0.6); sparkle(o+L[1][0]+0.4,84,7,0.08)
o,T,L=S['lesson']
put(mus,pad([48,52,55,60],T,0.035),o)
for it in L: put(fx,marimba(84,1.5,0.17)+marimba(91,1.5,0.07),o+it[0]-0.12)
for k,ts in steps(o,T,76,1): put(mus,marimba([60,64,67,72,67,64][k%6],0.8,0.08),ts)
o,T,L=S['outro']; warm(o,T,bpm=112,a=0.14)
s1,e1=L[1][0],L[1][1]
for f,nt in ((.28,88),(.45,91),(.8,96)):
    pr=o+s1+(e1-s1)*f; put(fx,tick(0.3,1500),pr); put(fx,marimba(nt,1,0.2)+marimba(nt+7,1,0.1),pr+0.08)
for sid in list(S)[1:]: put(fx,whoosh(0.45,0.25),S[sid][0]-0.25)
t=np.arange(N)/SR
env=np.convolve(np.abs(voice),np.ones(SR//5)/(SR//5),'same')
duck=1-0.5*np.clip(env/0.025,0,1)
fade=np.clip(t/0.2,0,1)*np.clip((total-t)/1.2,0,1)
mix=voice*1.15+mus*duck*fade*1.1+fx*0.85
mix=np.tanh(mix*1.1)/np.tanh(1.1); mix=mix/np.max(np.abs(mix))*0.95
sf.write('out/audio.wav',mix[:int(total*SR)],SR); print('total',total)
