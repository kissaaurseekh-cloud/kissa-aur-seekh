import sys, json, numpy as np, soundfile as sf, subprocess
import os as _o; sys.path.insert(0,_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'..','..','engine')); from ai4b_tts import say
from lscript import SCENES
out={}
for sid,lines in SCENES:
    for i,item in enumerate(lines):
        spk,txt=item[0],item[1]
        w,sr=say(txt,'female' if spk=='F' else 'male')
        a=np.abs(w); idx=np.where(a>0.015)[0]; w=w[max(0,idx[0]-400):idx[-1]+1200]
        sf.write('raw.wav',w,sr)
        f=f'vo/{sid}_{i}.wav'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i','raw.wav','-af','atempo=0.97,aresample=24000',f],check=True)
        d=sf.info(f).duration; out[f]=d; print(f,round(d,2),flush=True)
json.dump(out,open('vo/durs.json','w')); print('speech',sum(out.values()))
