import numpy as np, wave
sr=44100; D=34.0; n=int(sr*D); t=np.arange(n)/sr
out=np.zeros(n)
ch=[[220,261.6,329.6],[174.6,220,261.6],[196,261.6,329.6],[196,246.9,293.7]]
for i in range(9):
    s=int(i*4*sr); e=min(n,int((i+1)*4*sr)+sr)
    if s>=n: break
    tt=t[s:e]-t[s]; env=np.minimum(tt/1.2,1)*np.exp(-np.maximum(tt-4,0)*2)
    for f in ch[i%4]:
        out[s:e]+=0.05*env*(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt))
for k in np.arange(9.25,13.4,.42):
    s=int(k*sr); L=int(.05*sr); tt=np.arange(L)/sr
    out[s:s+L]+=0.25*np.sin(2*np.pi*1200*tt)*np.exp(-tt*80)
out*=np.minimum(1,(D-t)/1.0)
out=np.clip(out,-1,1)
w=wave.open('bed.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
