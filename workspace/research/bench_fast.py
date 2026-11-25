import sys, time, math, numpy as np, cv2
import clay_proto as cp, clay_fast as cf
PI, PF, GR, G0, G1 = cp.build()
CAM = np.array([0.0, 1.0, 3.2]); TGT = np.array([0.0, 0.62, 0.0]); FOV = math.radians(44)
L = np.array([-0.55, 0.75, 0.45]); L /= np.linalg.norm(L)
t = time.time(); r = cf.Renderer(16, 16); r.frame(CAM, TGT, FOV, L, PI, PF, GR, G0, G1); print('jit', round(time.time() - t, 1), flush=True)
for res in sys.argv[1:]:
    W, H = [int(v) for v in res.split('x')]
    r = cf.Renderer(W, H)
    t = time.time(); img, dep = r.frame(CAM, TGT, FOV, L, PI, PF, GR, G0, G1); dt = time.time() - t
    print(f'fast full {W}x{H}: {dt:.2f}s', flush=True)
    cv2.imwrite(f'fast_{W}x{H}.png', cp.post(img, dep, 3.15)[..., ::-1])
    # 脏矩形：中间那只猴子换了“定格拍”（boil seed），只重算它所在矩形
    sph = [(0.0, 0.62, 0.1, 0.75)]
    rect = cf.screen_rect(CAM, TGT, FOV, W, H, sph)
    t = time.time(); r.frame(CAM, TGT, FOV, L, PI, PF, GR, G0, G1, seed=1.0, rect=rect); dt2 = time.time() - t
    area = (rect[1] - rect[0]) * (rect[3] - rect[2]) / (W * H)
    print(f'  dirty rect {rect} area {area:.0%}: {dt2:.2f}s', flush=True)
