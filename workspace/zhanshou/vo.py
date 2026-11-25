import subprocess, json, numpy as np, soundfile as sf, os
from cues import LINES, DUR
SR=48000; os.makedirs('vox/lines',exist_ok=True)
out=np.zeros(int(DUR*SR)); rep=[]
for i,(k,s,a,b) in enumerate(LINES):
    if k!='N': continue
    mp=f'vox/lines/{i}.mp3'; wv=f'vox/lines/{i}.wav'
    if not os.path.exists(wv):
        subprocess.run(['python3','-m','edge_tts','--voice','zh-CN-YunjianNeural','--rate=-5%','--text',s,'--write-media',mp],check=True,timeout=60)
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i',mp,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse','-ar',str(SR),'-ac','1',wv],check=True)
    x,_=sf.read(wv); L=len(x)/SR; room=b-a
    if L>room-0.05:
        tempo=min(1.25,L/(room-0.1)); subprocess.run(['ffmpeg','-loglevel','error','-y','-i',wv,'-af',f'atempo={tempo:.3f}',wv+'.t.wav'],check=True); x,_=sf.read(wv+'.t.wav'); L=len(x)/SR
    st=int((a+0.1)*SR); n=min(len(x),len(out)-st); out[st:st+n]+=x[:n]; rep.append(f'{a:5.1f}-{b:5.1f} room {room:.2f} voice {L:.2f} {s}')
sf.write('vo.wav',out,SR); print('\n'.join(rep))
