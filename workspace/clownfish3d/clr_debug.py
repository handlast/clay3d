import sys, numpy as np, film as Fm, clearance as CL, clay_proto as cp
name=sys.argv[1]; dirs={"up":(0,1,0),"+x":(1,0,0),"-x":(-1,0,0),"+z":(0,0,1),"-z":(0,0,-1),"up+x":(1,1,0),"up-x":(-1,1,0),"up+z":(0,1,1)}
for t in [float(x) for x in sys.argv[2:]]:
    Fm.run_shot(name, Fm.SF[name], t, apply=False)
    fish=list(Fm._FISH); skip=[f[0] for f in fish if f]+[Fm.REEF_LAST.get("bubbles",(0,0))]
    obs=CL.obstacles(skip); idx=[i for i,p in enumerate(cp.PRIMS) if p[1]==0 and not any(s[0]<=i<s[1] for s in skip)]
    for k,f in enumerate(fish):
        if not f: continue
        P=CL.hull_points(f[0]); d=CL.sdf(P,obs)
        if d.min()>=Fm.MARGIN: print(t,k,"ok",round(d.min(),3)); continue
        # which obstacle
        j=np.argmin(d); best=(9,None)
        for oi in range(len(obs["t"])):
            sub={kk:v[oi:oi+1] for kk,v in obs.items()}
            dd=CL.sdf(P[j:j+1],sub)[0]
            if dd<best[0]: best=(dd,oi)
        pr=cp.PRIMS[idx[best[1]]]
        print(t,k,"min",round(d.min(),3),"pt",np.round(P[j],2),"obs prim",idx[best[1]],pr[0],np.round(pr[2],2),np.round(pr[3],2),round(pr[4],3),
              {n:round(CL.need_lift(P,obs,Fm.MARGIN,v),3) for n,v in dirs.items()})
