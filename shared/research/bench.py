import sys, time, math, numpy as np
sys.argv=[sys.argv[0]]+sys.argv[1:]
import clay_proto as cp
PI, PF, GR, G0, G1 = cp.build()
CAM = np.array([0.0, 1.0, 3.2]); TGT = np.array([0.0, 0.62, 0.0])
L = np.array([-0.55, 0.75, 0.45]); L /= np.linalg.norm(L)
def run(w,h,fl,name,x0=0,x1=None,y0=0,y1=None):
    x1 = w if x1 is None else x1; y1 = h if y1 is None else y1
    img=np.zeros((h,w,3)); dep=np.zeros((h,w))
    t=time.time(); cp.render(w,h,x0,x1,y0,y1,CAM,TGT,math.radians(44),L,PI,PF,GR,G0,G1,img,dep,np.array(fl,np.int64),0.0)
    dt=time.time()-t; print(f"{name:28s} {w}x{h} rows{y0}-{y1}: {dt:.2f}s", flush=True); return img,dep,dt
t=time.time(); run(8,8,[1]*7,'warm'); print('jit/warm',round(time.time()-t,1))
mode=sys.argv[1]
W,H=[int(v) for v in sys.argv[2].split('x')]
if mode=='ablate':
    base=[1,1,1,1,1,1,1]
    run(W,H,base,'full')
    names=['noshadow','noao','nodetail','nosss','nocull','norelax','central6']
    for k,n in enumerate(names):
        f=list(base); f[k]=0; run(W,H,f,n)
    run(W,H,[0,0,0,0,1,1,1],'geo+normal only')
elif mode=='full':
    img,dep,dt=run(W,H,[1]*7,'full')
    import cv2; cv2.imwrite(f'bench_{W}x{H}.png', cp.post(img,dep,3.15)[..., ::-1])
elif mode=='rows':   # 估算大分辨率：只渲染一段行再外推
    y0,y1=[int(v) for v in sys.argv[3].split('-')]
    run(W,H,[1]*7,'full',y0=y0,y1=y1)
