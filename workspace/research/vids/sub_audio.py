import numpy as np
W,H=96,54
cfg={'dz_info':(48,53),'bit_yiwai':(40,53),'iwanau_luck':(42,50)}
for name,(r0,r1) in cfg.items():
    a=np.fromfile(name+'.gray4.raw',dtype=np.uint8).reshape(-1,H,W).astype(np.int16)
    band=a[:,r0:r1,20:76]
    n=len(a); dur=n/4
    ch=np.array([0]+[(np.abs(band[i]-band[i-1])>30).mean() for i in range(1,n)])
    ev=[];last=-9
    for i in range(1,n-1):
        t=i/4
        if ch[i]>0.03 and ch[i]>=ch[i-1] and ch[i]>=ch[i+1] and t-last>=1.0: ev.append(t);last=t
    print('==',name,'subtitle-band change events',len(ev),'-> ~lines',len(ev)//2,'approx sec/line',round(dur/max(1,len(ev)//2),2))
    # audio
    x=np.fromfile(name+'.pcm',dtype=np.int16).astype(np.float32)/32768
    hop=4000 # 0.5s
    rms=np.array([np.sqrt((x[i:i+hop]**2).mean()+1e-12) for i in range(0,len(x)-hop,hop)])
    db=20*np.log10(rms)
    jump=np.diff(db)
    idx=np.argsort(jump)[::-1][:6]
    print('  loudness median dB',round(float(np.median(db)),1),'max',round(float(db.max()),1))
    print('  biggest +jumps (t, +dB, level):',[(round((i+1)*0.5,1),round(float(jump[i]),1),round(float(db[i+1]),1)) for i in sorted(idx)])
    # quiet gaps (< median-15dB) >=1s
    q=db<np.median(db)-15; runs=[];s=None
    for i,v in enumerate(q):
        if v and s is None: s=i
        if (not v or i==len(q)-1) and s is not None:
            if (i-s)*0.5>=1: runs.append((s*0.5,(i-s)*0.5))
            s=None
    print('  near-silent gaps>=1s:',runs[:10])
    print('  first 3s levels dB:',[round(float(v),1) for v in db[:6]])
