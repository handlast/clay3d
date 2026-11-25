# 封面 3:4 1080×1440 — 复用 scenes 的绘制函数（大标题两行 + 中间主视觉 + 底部胶囊）
from film import *
CW, CH = 1080, 1440
img = Image.new("RGB", (int(CW * S), int(CH * S)), (20, 40, 30)); d = D(img)
jungle(d, 1.0, "dawn")
d.rect(-40, 1100, 1120, 1500, fill=A((14, 44, 40), 1))
branch(d, -40, 1150, 1120, 1130, 50, 1, 1.0, True, 8)
for i in range(8): d.circ(540, 800, 560 - i * 55, fill=A((255, 236, 170), 0.02 + 0.01 * i))
roar_waves(d, 330, 790, 1.0, 0.0, 2.0, (255, 240, 190), 0.9, -math.pi / 2, 70, 600, 0.25, 12)
roar_waves(d, 750, 800, 1.1, 0.0, 2.0, (255, 220, 200), 0.9, -math.pi / 2, 70, 600, 0.25, 12)
flying_leaves(d, 0.55, 0.0, 540, 760, 26, 1300, 1, 5, 2.4)
howler(d, 330, 980, 0.95, 0.3, 1, "gold", "roar", mouth=1.0, flip=1)
howler(d, 750, 990, 0.95, 0.9, 1, "red", "roar", mouth=1.0, flip=-1)
s = "Vibe 知识大赏"; w = d.tlen(s, 30, 1) + 50
d.rect(540 - w / 2, 46, 540 + w / 2, 100, fill=A((15, 12, 26), 0.6), r=27); d.text(540, 73, s, 30, A(WHITE, 1), k=1)
d.rect(90, 135, 990, 455, fill=A((6, 14, 26), 0.6), r=40)
d.text(540, 222, "陆地上最吵的动物", 100, A(WHITE, 1), k=1)
d.text(540, 362, "又多了 2 个新成员", 92, A(GOLD, 1), k=1)
for x, y in ((420, 600), (860, 620)):
    d.circ(x, y, 40, fill=A((240, 60, 70), 1)); d.text(x, y, "新", 40, A(WHITE, 1), k=1)
d.rect(140, 1250, 940, 1370, fill=A((232, 62, 52), 1), r=60)
d.text(540, 1310, "上一个吼猴新种，还是 1941 年！", 46, A(WHITE, 1), k=1)
out = img.resize((CW, CH), Image.LANCZOS); out = E.vignette(out, 0.15)
out.save("howler_cover.png"); print(out.size)
