from film import *
CW, CH = 1080, 1440; Y0 = 170
img = Image.new("RGB", (W, H), BG); d = D(img)
bush(d, 0.4, camo=0.35, wig=0.25, face="smug", eyes=1.0, front_a=1.0, part=0.15, glowk=0.6, blush=0.6)
bx, by = butt_point(MX, MY, MS, 0.25)
d.circ(bx, by, 150, outline=A(GOLD, 1), w=12)
img = img.crop((0, int(P(Y0)), W, int(P(Y0 + CH)))); d = D(img)
d.rect(0, 0, CW, 420, fill=A((6, 20, 20), 0.55))
d.text(540, 150, "这里藏着一只螳螂", 104, A(WHITE, 1), k=1)
d.text(540, 300, "你能找到吗？", 150, A(GOLD, 1), k=1)
d.rect(150, 1300, 930, 1400, fill=A((232, 62, 52), 1), r=50)
d.text(540, 1350, "9800万年前，它把屁股扮成叶子", 46, A(WHITE, 1), k=1)
d.rect(415, 1220, 665, 1268, fill=A(WHITE, 0.92), r=24); d.text(540, 1244, "Vibe 知识大赏", 26, A(NAVYT, 1), k=1)
img.resize((CW, CH), Image.LANCZOS).save("cover.png")
