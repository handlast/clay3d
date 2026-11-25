from film import *
CW, CH = 1080, 1440
img = Image.new("RGB", (int(CW * S), int(CH * S)), BG); d = D(img)
grad(d, (24, 80, 64), (6, 20, 18), 0, CH)
rays(d, 1.0, (34, 110, 86), (10, 44, 34), 22, 540, 980)
glow(d, 540, 1000, 460, MINT, 0.6)
mimosa(d, 540, 1275, 245, 0.3, 0.0, "sus", look=0.7)
for x, y, r in ((170, 760, 0.9), (900, 820, 1.1)):
    d.text(x, y, "!", int(130 * r), A(WARN, 1), k=1)
for dy, txt, col, sz in ((250, "含羞草会记仇", WHITE, 150), (450, "记你28天", YEL, 190)):
    d.text(540 + 10, dy + 10, txt, sz, A(OL, 1), k=1); d.text(540, dy, txt, sz, A(col, 1), k=1)
d.rect(150, 1310, 930, 1410, fill=A(WARN, 1), r=50)
d.text(540, 1360, "摔它60次，它学会了无视", 54, A(WHITE, 1), k=1)
d.rect(40, 40, 290, 88, fill=A(WHITE, 0.92), r=24); d.text(165, 64, "Vibe 知识大赏", 26, A(BG, 1))
img.resize((CW, CH), Image.LANCZOS).save("cover.png")
