# 封面 3:4 1080×1440：复用 film 的 3D 镜头（big2：热成像下趴在宝宝身上的雄蜂，胸口白热），大标题两行 + 系列胶囊 + 底部红色悬念胶囊
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film as F
from PIL import Image
t = F.BIG2 + 1.8; fi = int(round(t * 30)); fi -= fi % 2
idx = F.shot_at(t)
img, ct, an, info = F.render3d(F.SECS[idx][2], fi / 30, fi // 2)
pil = Image.fromarray(img); P = lambda p: F.project(p, ct)
fx, fy = P(an["M"]["top"])
Y0 = int(min(max(fy - 470, 0), 1920 - 1440))
pil = pil.crop((0, Y0, 1080, Y0 + 1440)); d = F.D(pil)
d.rect(60, 50, 1020, 400, F.A((40, 10, 30), 0.55), r=50)
d.text(540, 145, "被嫌只会吃白饭", 116, F.A(F.WHITE, 1))
d.text(540, 300, "雄熊蜂半夜在干嘛？", 104, F.A(F.GOLD, 1))
s = "动物打工人 No.04"; w = d.tlen(s, 34) + 60
d.rect(540 - w / 2, 1180, 540 + w / 2, 1236, F.A((40, 26, 12), 0.6), r=28); d.text(540, 1208, s, 34, F.A(F.WHITE, 1))
d.rect(170, 1272, 910, 1372, F.A(F.RED, 1), r=50)
d.text(540, 1322, "胸口升到 34.8℃，在孵宝宝", 46, F.A(F.WHITE, 1))
pil.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.png")); print(pil.size, Y0, info)
