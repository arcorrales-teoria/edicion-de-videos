import wave, json, subprocess, numpy as np
from edit8 import SEGS, OFF, TOTAL
with wave.open('src48.wav') as w: sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).reshape(-1,2).astype(np.float32)/32768
FADE = int(0.012*sr)             # cuts now sit on quiet points -> short equal-power fades, no borrowed tails
out=np.zeros((int(TOTAL*sr)+4*sr,2),np.float32)
ramp=np.sin(np.linspace(0,np.pi/2,FADE))[:,None]
_F=np.fft.rfftfreq(480,1/sr); _band=(_F>80)&(_F<600)
def _vb(t):
    s_=x[int(t*sr):int(t*sr)+480].mean(1) if x.ndim==2 else x[int(t*sr):int(t*sr)+480]
    return 20*np.log10(np.sqrt((np.abs(np.fft.rfft(s_*np.hanning(480)))[_band]**2).mean())+1e-9)
FLOOR=-4.8
for i,((a,b),o) in enumerate(zip(SEGS,OFF)):
    y=x[int(a*sr):int(b*sr)].copy()
    if i>0:
        fi = int(0.025*sr) if _vb(a)-FLOOR>4 else FADE          # voiced start -> slightly longer fade-in
        y[:fi]*=np.sin(np.linspace(0,np.pi/2,fi))[:,None]
    if i<len(SEGS)-1:
        fo = int(0.07*sr) if _vb(b-0.01)-FLOOR>4 else FADE      # voiced tail -> natural 70 ms decay inside the take
        y[-fo:]*=(0.5*(1+np.cos(np.linspace(0,np.pi,fo))))[:,None]
    d0=int(o*sr); out[d0:d0+len(y)]+=y
out=out[:int(TOTAL*sr)]
n=int(0.25*sr); out[-n:]*=np.linspace(1,0,n)[:,None]
with wave.open('voice_raw.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
run=lambda a: subprocess.run(a,capture_output=True,text=True)
run(['ffmpeg','-v','error','-y','-i','voice_raw.wav','-af','highpass=f=80,afftdn=nr=8:nf=-45:tn=1','-c:a','pcm_s16le','voice_dn.wav'])
r=run(['ffmpeg','-i','voice_dn.wav','-af','loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
af=(f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
    f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
run(['ffmpeg','-v','error','-y','-i','voice_dn.wav','-af',af+',atempo=1.1','-ar','48000','-c:a','pcm_s16le','voice_s16.wav'])
print('voice built (1.1x)')
