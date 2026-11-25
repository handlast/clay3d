# Cover 1080x1440: German-POV burning M10 + big Murphy silhouette; 2-line title on top; bottom capsule. No outlines.
import sys; sys.argv = ["x"]
from film import *
t = T["waver"] + 4.6
img = Image.new("RGB", (W, H)); s_waver(t, img, D(img))
tm = np.zeros((H, W), np.float32); yy = np.arange(H)[:, None] / S; tm[:] = np.clip(1 - (yy - 560) / 200, 0, 1)
img.paste((12, 10, 14), (0, 0), Image.fromarray((tm * 255).astype(np.uint8), "L"))
crop = img.crop((0, int(P(230)), W, int(P(230 + 1440))))
d = D(crop)
d.text(540, 150, "19岁小个子", 132, A(WHITE, 1), k=1)
d.text(540, 320, "挡住6辆坦克？", 132, A(FIRE_L, 1), k=1)
s = "超级士兵 No.03"; w = d.tlen(s, 56) + 110
d.rect(540 - w / 2, 1290, 540 + w / 2, 1380, fill=A((200, 50, 40), 0.96), r=45); d.text(540, 1335, s, 56, A(WHITE, 1))
out = crop.resize((1080, 1440), Image.LANCZOS); out = E.vignette(out, 0.25, 0.55)
out.save("/workspace/work/murphy/murphy_cover.png"); print(out.size)
