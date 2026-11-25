# 脸部放大对比：旧管线（720×1280 整帧 + 放大 + 全局景深/柔光，No.01 猕猴的做法） vs 新管线（脸部 2× 超采样 + 脸不进景深/柔光）
# python3 facecmp.py out.png t:key t:key ...   key = 镜头 anchors 里的角色名
import sys, math, numpy as np, cv2
import film as Fm, world as Wd
from world import cp, cf
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; rows = []
fnt = ImageFont.truetype(Fm.FONTS[1], 30)
for arg in sys.argv[2:]:
    ts, key = arg.split(":"); t = float(ts)
    idx = Fm.shot_at(t); cam, tgt, fpt, an = Fm.SECS[idx][2](t)
    PI, PF, GR, G0, G1 = Wd.arr()
    focus = float(np.linalg.norm(cam - np.asarray(fpt)))
    img = np.zeros((720 * 16 // 9, 720, 3)); dep = np.zeros((1280, 720))
    cp.render(720, 1280, 0, 720, 0, 1280, cam, tgt, Fm.FOV, Fm.LIGHT, PI, PF, GR, G0, G1, img, dep, Fm.FLAGS, 0.0)
    old = cp.post(img, dep, focus)                                   # 旧：整帧放大 + 景深/柔光不避脸
    up, du, mask, info = cf.render_faces(720, 1280, 1080, 1920, cam, tgt, Fm.FOV, Fm.LIGHT, PI, PF, GR, G0, G1, Fm.FLAGS, 0.0, Fm.faces_of(an))
    new = cf.post_faces(up, du, focus, mask, fog=Fm.FOG)
    b = cf.face_box(an[key]["face"], an[key]["face_r"], cam, tgt, Fm.FOV, 1080, 1920)
    crops = [cf.face_crop(x, b, 2) for x in (old, new)]
    h = min(c.shape[0] for c in crops); crops = [c[:h] for c in crops]
    rows.append(crops)
CW = max(r[0].shape[1] for r in rows)
def padw(c): return np.pad(c, ((0, 0), (0, CW - c.shape[1]), (0, 0)), constant_values=255)
blocks = []
for r in rows:
    blocks.append(np.hstack([padw(r[0]), np.full((r[0].shape[0], 16, 3), 255, np.uint8), padw(r[1])]))
    blocks.append(np.full((16, 2 * CW + 16, 3), 255, np.uint8))
W = 2 * CW + 16
im = Image.fromarray(np.vstack([np.full((60, W, 3), 255, np.uint8)] + blocks)); d = ImageDraw.Draw(im)
d.text((20, 14), "旧：720p 整帧放大 + 全局景深/柔光", font=fnt, fill=(180, 40, 40))
d.text((CW + 36, 14), "新：脸部 2× 超采样，脸不进景深/柔光", font=fnt, fill=(30, 120, 60))
im.save(out); print(out, im.size)
