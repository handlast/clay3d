import time, numpy as np, cv2, math
from world import *
t0=time.time()
cam=Cam(0,-14,3.2,9, focus=14.5, aperture=1.0)
img,dep=ground(cam, lambda gx,gz:[("soil",1.0)], sky=(0.55,0.6,0.55), fogd=700)
t1=time.time()
sm=np.zeros((H,W),np.float32)
ant_shadow(sm,cam,0,0,math.radians(-100))
sm=cv2.GaussianBlur(sm,(0,0),9); img*=(1-0.5*sm)[...,None]
rng=np.random.default_rng(1)
objs=[]
for i in range(60): objs.append(('p',rng.uniform(-60,60),rng.uniform(0,150),rng.uniform(0.4,3)))
for i in range(80): objs.append(('b',rng.uniform(-150,150),rng.uniform(15,300),0))
objs.sort(key=lambda o:-(o[2]))
for o in objs:
    if o[0]=='p': pebble(img,cam,o[1],o[2],o[3],(0.5,0.42,0.34))
    else: blade(img,cam,o[1],o[2],rng.uniform(30,90),rng.uniform(2,5),rng.uniform(-0.5,0.5),rng.uniform(0,6.28),(0.30,0.42,0.18))
root(img,cam,[(x, 2+3*math.sin(x/20), 60+0.2*x) for x in np.linspace(-80,80,60)], [4]*60,(0.40,0.30,0.22))
ant(img,cam,0,0,math.radians(-100),phase=0.3,ant_a=0.5,ant_b=1.2)
t2=time.time()
img=dof(img,dep,cam)
img=grade(img,sat=0.9,warm=0.02); img=grain(img,0)
t3=time.time()
print(t1-t0,t2-t1,t3-t2)
cv2.imwrite('/tmp/b_t1.jpg',(np.clip(img,0,1)[...,::-1]*255).astype('uint8'))
