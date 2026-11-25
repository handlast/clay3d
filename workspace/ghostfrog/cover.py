# 封面 3:4 1080×1440 — 复用 scenes 的绘制函数（大标题两行 + 中间主视觉 + 底部胶囊）
from film import *
CW, CH = 1080, 1440
img = Image.new("RGB", (int(CW * S), int(CH * S)), (20, 26, 24)); d = D(img)
grad(d, (22, 30, 30), (10, 14, 16), 0, CH)
litter_bed(d, 0.0, 3, 120, (-80, 0, 1160, 1500), 1, 0.35)
spot(d, 540, 880, 640, 1.2)
glow_disc(d, 540 - 74 * 2.1, 880 - 132 * 2.1, 200, IRED_L, 0.5); glow_disc(d, 540 + 74 * 2.1, 880 - 132 * 2.1, 200, IRED_L, 0.5)
ghostfrog(d, 540, 960, 2.1, 0.0, 1, "calm", blink=False, seed=0)
for (x, y, L, ang, c) in ((140, 1240, 260, 0.4, LITTER[1]), (930, 1220, 280, -0.5, LITTER[3]), (250, 640, 200, -0.8, LITTER[0]), (860, 620, 210, 0.7, LITTER[5])):
    leaf_shape(d, x, y, L, ang, c, 1)
s = "Vibe 知识大赏"; w = d.tlen(s, 30, 1) + 50
d.rect(540 - w / 2, 46, 540 + w / 2, 100, fill=A((15, 12, 26), 0.6), r=27); d.text(540, 73, s, 30, A(WHITE, 1), k=1)
d.rect(90, 130, 990, 430, fill=A((6, 14, 20), 0.66), r=40)
d.text(540, 210, "这只青蛙的眼睛", 96, A(WHITE, 1), k=1)
xx = 540 - d.tlen("上半红、下半铜绿？", 92, 1) / 2
for part, col in (("上半红", IRED_L), ("、", WHITE), ("下半铜绿", IBRZ_L), ("？", WHITE)):
    d.text(xx, 350, part, 92, A(col, 1), anchor="lm", k=1); xx += d.tlen(part, 92, 1)
d.rect(150, 1290, 930, 1400, fill=A((232, 62, 52), 1), r=55)
d.text(540, 1345, "今年刚命名的新物种：叶中幽灵", 44, A(WHITE, 1), k=1)
out = img.resize((CW, CH), Image.LANCZOS); out = E.vignette(out, 0.15)
out.save("cover.png"); print(out.size)
