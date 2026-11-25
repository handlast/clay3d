import numpy as np
W,H=96,54
res={}
for name in ['dz_info','bit_yiwai','iwanau_luck']:
    a=np.fromfile(name+'.gray4.raw',dtype=np.uint8).reshape(-1,H,W).astype(np.int16)
    n=len(a); dur=n/4
    lag=4  # 1 s
    ch=np.zeros(n)
    for i in range(lag,n):
        ch[i]=(np.abs(a[i]-a[i-lag])>25).mean()
    mean=a.reshape(n,-1).mean(1)
    print('==',name,'dur',dur,'pct50/90/99 change',np.percentile(ch,[50,90,99]).round(3))
    for th in (0.02,0.04,0.08):
        beats=[];last=-9
        for i in range(1,n-1):
            t=i/4
            if ch[i]>=th and ch[i]>=ch[i-1] and ch[i]>=ch[i+1] and t-last>=1.5:
                beats.append(t);last=t
        gaps=np.diff([0]+beats+[dur])
        print(f' th{th}: beats={len(beats)} avg_interval={dur/(len(beats)+1):.2f}s median_gap={np.median(gaps):.2f} first3s={[b for b in beats if b<=3]} first15s={[b for b in beats if b<=15]}')
    # quiet stretches: frames with change<0.005 for >=3s
    q=ch<0.005; runs=[];s=None
    for i,v in enumerate(q):
        if v and s is None: s=i
        if (not v or i==n-1) and s is not None:
            if (i-s)/4>=3: runs.append((s/4,(i-s)/4))
            s=None
    print(' static>=3s runs:',len(runs),'total',sum(r[1] for r in runs),'s; longest',max([r[1] for r in runs] or [0]))
    print(' mean luma median',np.median(mean).round(1))
    np.save(name+'.change.npy',ch)
