# 定格感演示：24fps 输出、每 2 帧更新一次（on twos）；每拍：表面噪声换 seed + 图元微抖 + 相机微晃 + 灯光微闪
import time, math, numpy as np, cv2, subprocess
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine'))
import clay_proto as cp, clay_fast as cf
PI, PF0, GR, G0, G1 = cp.build()
FOV = math.radians(44); L0 = np.array([-0.55, 0.75, 0.45]); L0 /= np.linalg.norm(L0)
W, H = 540, 960; r = cf.Renderer(W, H)
rng = np.random.default_rng(7)
frames = []; t0 = time.time()
for pose in range(6):                       # 6 拍 × 2 = 12 帧 = 0.5 秒
    PF = PF0.copy()
    PF[:, 0:3] += rng.normal(0, 0.0012, (len(PF), 3)) * (PI[:, 2:3] > 0)   # 墙地不抖
    PF[PI[:, 0] == 0, 3:6] *= 1 + rng.normal(0, 0.006, (int((PI[:, 0] == 0).sum()), 3)) * (PI[PI[:, 0] == 0, 2:3] > 0)
    cam = np.array([0.0, 1.0, 3.2]) + rng.normal(0, 0.004, 3)
    tgt = np.array([0.0, 0.62, 0.0]) + rng.normal(0, 0.002, 3)
    img, dep = r.frame(cam, tgt, FOV, L0, PI, PF, GR, G0, G1, seed=float(pose))
    out = cp.post(img * (1 + rng.normal(0, 0.015)), dep, 3.15)
    frames += [out, out]                    # on twos
print('6 poses rendered in', round(time.time() - t0, 1), 's')
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '24', '-i', '-',
                      '-pix_fmt', 'yuv420p', '-crf', '20', 'boil_demo.mp4'], stdin=subprocess.PIPE)
for f in frames: p.stdin.write(f.tobytes())
p.stdin.close(); p.wait()
cv2.imwrite('boil_diff.png', np.clip(np.abs(frames[0].astype(int) - frames[2].astype(int)) * 6, 0, 255).astype(np.uint8)[::2, ::2])
