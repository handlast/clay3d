from film import *
CW, CH = 1080, 1440
img = Image.new("RGB", (int(CW*S), int(CH*S)), CREAM); d = D(img)
d.rect(380, 70, 700, 122, fill=INK+(255,), r=26); d.text(540, 96, "Vibe 知识大赏", 30, CREAM+(255,))
d.text(540, 225, "草莓为什么", 108, INK+(255,))
d.text(540, 355, "会长歪？", 120, BERRY_D+(255,))
# soft halo
for r, al in ((420, .10), (330, .12), (250, .14)): d.circ(540, 860, r, fill=A(GOLDL, al))
berry(d, 540, 600, 270, 567, 1.0, deform=1.0,
      lit=lambda i: 0 if i in DEFORM_SEEDS else 0.55, gray=lambda i: 1.0 if i in DEFORM_SEEDS else 0)
d.text(900, 1010, "没授上粉", 38, INK2+(255,)); d.line([(830, 990), (690, 950)], INK2+(255,), 3)
d.text(150, 690, "生长素", 38, GOLD+(255,)); d.line([(150, 715), (325, 760)], GOLD+(255,), 3)
d.rect(150, 1250, 930, 1350, fill=BERRY+(255,), r=50)
d.text(540, 1300, "答案藏在每一颗“籽”里", 52, (255,255,255,255))
img.resize((CW, CH), Image.LANCZOS).save("cover_3x4.png")
