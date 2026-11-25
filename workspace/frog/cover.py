# 封面 3:4 1080×1440 — 复用 film/scenes 的绘制函数
from film import *
CW, CH = 1080, 1440
img = Image.new("RGB", (int(CW * S), int(CH * S)), (10, 20, 24)); d = D(img)
rainforest(d, 1.3, 0.5, 1.0)
for i in range(8): d.circ(540, 860, 520 - i * 50, fill=A((90, 220, 240), 0.02 + 0.01 * i))
frog(d, 540, 860, 1.25, 1.3, 1, "shock", xray=1, shells=3)
zap(d, 540, 900, 0.35, 0.0, SHELL, 380)
s = "Vibe 知识大赏"; w = d.tlen(s, 30, 1) + 50
d.rect(540 - w / 2, 50, 540 + w / 2, 104, fill=A((15, 12, 26), 0.6), r=27); d.text(540, 77, s, 30, A(WHITE, 1), k=1)
d.rect(110, 150, 970, 420, fill=A((6, 14, 26), 0.55), r=40)
d.text(540, 225, "3 厘米小蛙", 112, A(WHITE, 1), k=1)
d.text(540, 345, "肚里藏着 3 个蜗牛壳", 74, A(SHELL_L, 1), k=1)
d.rect(150, 1180, 930, 1300, fill=A((232, 62, 52), 1), r=60)
d.text(540, 1240, "它是第一只吃蜗牛的蛙吗？", 54, A(WHITE, 1), k=1)
out = img.resize((CW, CH), Image.LANCZOS); out = E.vignette(out, 0.15)
out.save("frog_cover.png"); print(out.size)
