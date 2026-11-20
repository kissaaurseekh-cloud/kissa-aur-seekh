import numpy as np, soundfile as sf, sys
sys.argv=['x','none']
exec(open('lrender.py').read().split("if __name__")[0])
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
def thunder(ts,a=0.5):
    d=2.2; put(fx,noise_band(d,a,40)*np.exp(-tt(d)*1.8),ts); put(fx,kick(a*1.2,1.5,60,30,2),ts)
def rainbed(o,T,a=0.07):
    e=np.minimum(1,np.minimum(tt(T)/1.0,(T-tt(T))/1.0)); put(fx,noise_band(T,a,5)*e,o)
def drip(ts,a=0.1):
    t_=tt(0.12); f=900+1400*np.exp(-t_*40); put(fx,a*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t_*30),ts)
def birds(o,T,a=0.04):
    k=o+0.3
    while k<o+T-0.3:
        t_=tt(0.09); f=2800+900*np.sin(2*np.pi*12*t_)
        put(fx,a*np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t_/0.09),k); put(fx,a*0.8*np.sin(2*np.pi*np.cumsum(f*1.1)/SR)*np.sin(np.pi*t_/0.09),k+0.13)
        k+=rng.uniform(1.2,2.4)
prog=[(48,[60,64,67,72]),(43,[59,62,67,71]),(45,[57,60,64,69]),(41,[57,60,65,69])]
def warm(o,T,bpm=92,a=0.11,start=0,sh=True):
    for k,ts in steps(o,T,bpm):
        root,ch=prog[(k//8+start)%4]
        put(mus,marimba(ch[[0,1,2,3,2,1,2,3][k%8]],0.45,a),ts)
        if k%4==0: put(mus,bass(root,0.5,0.24),ts)
        if sh: put(mus,shaker(0.025 if k%2 else 0.015),ts)
def sadmel(o,T,notes,bpm=62,a=0.1):
    for k,ts in steps(o,T,bpm,1): put(mus,marimba(notes[k%len(notes)],1.3,a),ts)
def chords(o,T,seq,dur=2.0,a=0.045):
    k=0
    while k*dur<T:
        r,ch=seq[k%len(seq)]; put(mus,pad(ch,min(dur+0.4,T-k*dur+0.4),a),o+k*dur); put(mus,bass(r,1.2,0.26),o+k*dur); k+=1
o,T,L=S['storm']; rainbed(o,T,0.09); thunder(o+0.5); thunder(o+6.0,0.4)
put(mus,pad([38,45,50],T,0.05),o)
for k,ts in steps(o+0.6,T-0.6,70,1): put(mus,pluck([50,53,52,49][k%4],1.0,0.22),ts)
o,T,L=S['recap']
put(mus,pad([45,52,57,60],T,0.04),o); sadmel(o,T,[69,64,60,62,64,57],66,0.09)
for k in range(4): hammer(o+L[1][0]+0.3+k*0.4,0.18)
put(fx,riser(1.0,0.2),o+L[3][0]-1.0); put(fx,kick(0.6,1.0,90,35,3),o+L[3][0])
rainbed(o+L[4][0],T-L[4][0],0.07)
o,T,L=S['movein']; warm(o,T); birds(o,T)
o,T,L=S['breaking']
put(mus,pad([41,48,53,57],T,0.045),o); sadmel(o,T,[65,64,60,57],62,0.09)
for k in range(3): crack(o+L[0][0]+0.8+k*1.2,0.2)
o,T,L=S['monsoon']; rainbed(o,T,0.11); thunder(o+1.2); thunder(o+L[1][0]+1.0,0.4)
put(mus,pad([38,44,50],T,0.055),o)
for k in range(int(T/0.7)): drip(o+0.3+k*0.7,0.08)
for k in range(3): crack(o+L[1][0]+1.0+k*0.3,0.25)
o,T,L=S['confess']; birds(o,T,0.025)
put(mus,pad([45,48,52],T,0.045),o); sadmel(o,T,[76,72,69,71,72,67],58,0.09)
o,T,L=S['decision']
chords(o,T,[(45,[57,60,64,69]),(41,[53,57,60,65]),(43,[55,59,62,67]),(48,[52,55,60,64])],2.2)
put(fx,riser(1.0,0.2),o+L[0][0]+0.2); sparkle(o+L[0][0]+1.2,84,7,0.1)
o,T,L=S['rebuild']; warm(o,T,bpm=110,a=0.12); birds(o,T,0.03)
k=o+L[0][0]+1.7
while k<o+T-0.5: hammer(k,0.16); k+=rng.choice([0.5,0.7,0.9])
for k in range(3): thud(o+L[0][0]+0.3+k*0.4,0.35)
o,T,L=S['village']; warm(o,T,bpm=100,a=0.11,start=2); birds(o,T)
for k in range(6): put(fx,noise_band(0.06,0.05,3),o+0.3+k*0.4)
o,T,L=S['newhouse']; rainbed(o,T,0.08); thunder(o+0.6,0.3)
chords(o+L[0][0]-1.0,T-L[0][0]+1.0,[(41,[53,57,60,65]),(43,[55,59,62,67]),(48,[52,55,60,64]),(45,[57,60,64,69])],2.4)
sparkle(o+L[1][0]+1.0,84,7,0.12)
o,T,L=S['lesson']
put(mus,pad([48,52,55,60],T,0.035),o)
for it in L: put(fx,marimba(84,1.5,0.17)+marimba(91,1.5,0.07),o+it[0]-0.12)
for k,ts in steps(o,T,76,1): put(mus,marimba([60,64,67,72,67,64][k%6],0.8,0.08),ts)
o,T,L=S['outro']; warm(o,T,bpm=104,a=0.12)
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
