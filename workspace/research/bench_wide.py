import sys, time, math, numpy as np, cv2
import clay_proto as cp, clay_fast as cf
PI, PF, GR, G0, G1 = cp.build()
L = np.array([-0.55, 0.75, 0.45]); L /= np.linalg.norm(L); FOV = math.radians(44)
r = cf.Renderer(16, 16); r.frame(np.array([0., 1, 3.2]), np.array([0., .62, 0]), FOV, L, PI, PF, GR, G0, G1)
mode = sys.argv[1]
if mode == 'big':
    CAM = np.array([0.0, 1.0, 3.2]); TGT = np.array([0.0, 0.62, 0.0])
    r = cf.Renderer(1080, 1920); t = time.time(); img, dep = r.frame(CAM, TGT, FOV, L, PI, PF, GR, G0, G1)
    print('fast full 1080x1920 tight:', round(time.time() - t, 2)); t = time.time(); o = cp.post(img, dep, 3.15); print('post', round(time.time() - t, 2))
    cv2.imwrite('fast_1080x1920.png', o[..., ::-1])
else:
    W, H = 720, 1280
    CAM = np.array([0.0, 1.6, 5.5]); TGT = np.array([0.0, 0.6, 0.0])
    r = cf.Renderer(W, H); t = time.time(); img, dep = r.frame(CAM, TGT, FOV, L, PI, PF, GR, G0, G1)
    print('wide full 720x1280:', round(time.time() - t, 2))
    cv2.imwrite('wide_720x1280.png', cp.post(img, dep, 5.4)[..., ::-1])
    for name, sph in (('one monkey', [(0.0, 0.62, 0.1, 0.75)]), ('three monkeys', [(-0.62, .62, 0, .75), (0, .62, .1, .75), (.62, .62, 0, .75)])):
        rect = cf.screen_rect(CAM, TGT, FOV, W, H, sph)
        t = time.time(); r.frame(CAM, TGT, FOV, L, PI, PF, GR, G0, G1, seed=1.0, rect=rect)
        area = (rect[1] - rect[0]) * (rect[3] - rect[2]) / (W * H)
        print(f'  {name}: rect {rect} area {area:.0%}: {time.time() - t:.2f}s')
