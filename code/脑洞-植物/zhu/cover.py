from film import *
img = Image.new("RGBA", (W, H), PAPER + (255,)); d = D(img)
GY = 900
d.rect(0, GY, 1920, 1080, fill=A((228, 220, 198), 1))
# left: monoculture, sick
for i in range(9):
    plant(d, 60 + i * 95, GY, 380, True, 0.6, sick=0.9, seed=i)
# divider
d.line([(960, 560), (960, GY - 10)], A(INK2, 0.5), 3)
# right: mixed, healthy
pat = [1, 0, 0, 1, 0, 0, 1, 0, 0]
for i, tl in enumerate(pat):
    plant(d, 1010 + i * 100, GY, 420 if tl else 290, tl == 1, 0.6, seed=i + 20)
ground(d, 20, 1900, GY)
for x, y in [(230, 470), (470, 445), (690, 480), (360, 500)]: spore(d, x, y, 0.9, 6)
d.text(470, 980, "只种一种", 44, A(INK, 1)); d.text(1420, 980, "混着种", 44, A(GOLD, 1))
# title block
d.rect(660, 40, 1260, 92, fill=A(INK, 1), r=26)
d.text(960, 66, "Vibe 知识大赏", 34, A(PAPER, 1))
d.text(960, 215, "混  种", 190, A(INK, 1))
d.text(960, 380, "为什么混着种，庄稼就少生病？", 54, A(INK, 1))
d.text(1720, 230, "−94%", 80, A(GOLD, 1), lat=1); d.text(1720, 300, "病害", 36, A(GOLD, 1))
d.text(200, 230, "朱有勇", 52, A(INK2, 1)); d.text(200, 295, "Nature 2000", 30, A(INK2, 1), lat=2)
img.convert("RGB").resize((OW, OH), Image.LANCZOS).save("cover_16x9.png")
