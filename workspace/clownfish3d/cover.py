# 封面 3:4 1080×1440：复用 film 的 3D 镜头（big2：戴安全帽的小丑鱼 + 白化海葵，已套穿模约束），大标题两行 + 系列胶囊 + 底部红色悬念胶囊
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film as F
from PIL import Image
t = F.BIG2 + 1.2; fi = int(round(t * 30)); fi -= fi % 2
idx = F.shot_at(t)
img, ct, an, info = F.render3d(F.SECS[idx][2], fi / 30, fi // 2)
pil = Image.fromarray(img); d = F.D(pil); P = lambda p: F.project(p, ct)
fx, fy = P(an["F"]["top"])
Y0 = int(min(max(fy - 560, 0), 1920 - 1440))
pil = pil.crop((0, Y0, 1080, Y0 + 1440)); d = F.D(pil)
d.rect(60, 50, 1020, 400, F.A(F.DARK, 0.5), r=50)
d.text(540, 145, "家生病了，", 118, F.A(F.WHITE, 1))
d.text(540, 300, "小丑鱼加班守家？", 112, F.A(F.GOLD, 1))
s = "动物打工人 No.03"; w = d.tlen(s, 34) + 60
d.rect(540 - w / 2, 1200, 540 + w / 2, 1256, F.A((10, 24, 40), 0.6), r=28); d.text(540, 1228, s, 34, F.A(F.WHITE, 1))
d.rect(150, 1290, 930, 1390, F.A(F.RED, 1), r=50)
d.text(540, 1340, "可同事之间，吵架多了215%", 46, F.A(F.WHITE, 1))
pil.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.png")); print(pil.size, Y0, info)
