import re,sys,statistics as st
def load(f):
    ts=[];sc=[]
    t=None
    for line in open(f):
        m=re.search(r'pts_time:([\d.]+)',line)
        if m: t=float(m.group(1)); continue
        m=re.search(r'scene_score=([\d.]+)',line)
        if m and t is not None: ts.append(t); sc.append(float(m.group(1)))
    return ts,sc
for name,dur in [('dz_info',300.01),('bit_yiwai',164.0),('iwanau_luck',130.0)]:
    ts,sc=load(name+'.scores.txt')
    print('==',name,len(ts))
    for th in (0.4,0.3,0.2,0.12):
        cuts=[];last=-9
        for t,s in zip(ts,sc):
            if s>=th and t-last>=0.4: cuts.append(t); last=t
        n=len(cuts)+1
        print(f' th{th}: cuts={len(cuts)} shots={n} ASL={dur/n:.2f}s  first10s={[round(c,1) for c in cuts if c<10]}')
    # write cuts at 0.2
    cuts=[];last=-9
    for t,s in zip(ts,sc):
        if s>=0.2 and t-last>=0.4: cuts.append((round(t,2),round(s,2))); last=t
    open(name+'.cuts02.txt','w').write('\n'.join(f'{a}\t{b}' for a,b in cuts))
