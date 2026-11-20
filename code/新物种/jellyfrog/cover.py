# 封面 3:4 1080×1440 — 复用 scenes 的绘制函数（上方两行大标题 + 中间主视觉 + 底部胶囊）
from film import *
CW, CH = 1080, 1440
img = Image.new("RGB", (int(CW * S), int(CH * S)), (12, 40, 46)); d = D(img)
grad(d, (14, 52, 60), (6, 18, 24), 0, CH)
mist(d, 0.0, 1.2, 700, 6)
branch(d, -40, 660, 1120, 600, 36, 1, 0.0, 6, 4)
d.line([(560, 640), (560, 730)], A(BRANCH_L, 1), 12)
for sd in (-1, 1): leaf_shape(d, 560 + sd * 70, 705, 170, -1.57 + sd * 1.0, LEAFG_L, 1)
jelly(d, 560, 975, 240, 1.3, 1, 18, 0.92, 3, 1.0, 0.6, 1, 1.4)
jfrog(d, 860, 535, 0.6, 0.0, 1, "happy", look=-0.8, blink=False, seed=0.2)
s = "Vibe 知识大赏"; w = d.tlen(s, 30, 1) + 50
d.rect(540 - w / 2, 40, 540 + w / 2, 94, fill=A((15, 12, 26), 0.6), r=27); d.text(540, 67, s, 30, A(WHITE, 1), k=1)
d.rect(90, 118, 990, 400, fill=A((6, 14, 20), 0.66), r=40)
d.text(540, 196, "这只飞蛙的宝宝", 96, A(WHITE, 1), k=1)
xx = 540 - d.tlen("住在果冻里？", 104, 1) / 2
for part, col in (("住在", WHITE), ("果冻", GEL_L), ("里？", WHITE)):
    d.text(xx, 330, part, 104, A(col, 1), anchor="lm", k=1); xx += d.tlen(part, 104, 1)
d.rect(150, 1250, 930, 1360, fill=A((232, 62, 52), 1), r=55)
d.text(540, 1305, "印尼高山新物种：苏拉威西飞蛙", 44, A(WHITE, 1), k=1)
out = img.resize((CW, CH), Image.LANCZOS); out = E.vignette(out, 0.15)
out.save("cover.png"); print(out.size)
