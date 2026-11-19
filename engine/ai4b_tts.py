import sys, re, numpy as np, soundfile as sf
from TTS.utils.synthesizer import Synthesizer
import os
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','models','ai4b','hi')+'/'
syn=Synthesizer(tts_checkpoint=B+'fastpitch/best_model.pth', tts_config_path=B+'fastpitch/config_fixed.json',
    tts_speakers_file=B+'fastpitch/speakers.pth', vocoder_checkpoint=B+'hifigan/best_model.pth',
    vocoder_config=B+'hifigan/config.json', use_cuda=False)
def clean(t):
    t=t.replace('।','.').replace('…',',').replace('"','').replace('!','!').replace('—',',')
    return re.sub(r'\s+',' ',t).strip()
def say(text, spk='female'):
    w=syn.tts(clean(text), speaker_name=spk, split_sentences=True)
    return np.array(w,dtype=np.float32), syn.output_sample_rate
if __name__=='__main__':
    for spk in ('female','male'):
        w,sr=say("रामू एक मिस्त्री था। चालीस साल से वो, सेठ धनराज के लिए घर बनाता आ रहा था।",spk)
        sf.write(f'test_ai4b_{spk}.wav',w,sr); print(spk,len(w)/sr,sr)
