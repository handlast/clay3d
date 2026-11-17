# 封面 3:4 1080×1440：复用 film 的 3D 镜头（理毛 + 围观猴 + 爱心），大标题两行 + 底部红色胶囊
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film as F
from PIL import Image
t = 4.4; fi = int(t * 30); fi -= fi % 2
idx = F.shot_at(t)
img, ct, an = F.render3d(F.SECS[idx][2], fi / 30, fi // 2)
pil = Image.fromarray(img); d = F.D(pil); P = lambda p: F.project(p, ct)
g1 = P(an["G1"]["top"]); g2 = P(an["G2"]["top"]); mx, my = (g1[0] + g2[0]) / 2, min(g1[1], g2[1]) - 30
for j in range(9):
    import math
    ang = -math.pi / 2 + (j - 4) * 0.42; rr = 170
    F.heart(d, mx + math.cos(ang) * rr, my + 40 + math.sin(ang) * rr, 26, F.PINK, 0.95)
wx, wy = P(an["W"]["head"]); F.dashed(d, (wx + 30, wy - 20), (mx, my + 110), F.GOLD, 0.9, 7, 22, 1.0)
Y0 = 240
pil = pil.crop((0, Y0, 1080, Y0 + 1440)); d = F.D(pil)
d.rect(60, 50, 1020, 400, F.A(F.DARK, 0.5), r=50)
d.text(540, 145, "爱看朋友的猴子", 118, F.A(F.WHITE, 1))
d.text(540, 300, "后来地位更高？", 118, F.A(F.GOLD, 1))
s = "动物打工人 No.01"; w = d.tlen(s, 34) + 60
d.rect(540 - w / 2, 1200, 540 + w / 2, 1256, F.A((20, 16, 30), 0.6), r=28); d.text(540, 1228, s, 34, F.A(F.WHITE, 1))
d.rect(150, 1290, 930, 1390, F.A(F.RED, 1), r=50)
d.text(540, 1340, "围观也分两种：吵架 vs 好朋友", 46, F.A(F.WHITE, 1))
pil.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.png")); print(pil.size)
