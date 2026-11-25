# Cover 1080x1440: big1 scene (132 hands up) + 2-line title on top + bottom capsule. No outlines.
import sys; sys.argv = ["x"]
from film import *
img = Image.new("RGB", (W, H)); s_big1(5.6, img, D(img))
# cover the in-scene number with a dark top band
top = Image.new("L", (W, H), 0); tm = np.zeros((H, W), np.float32)
yy = np.arange(H)[:, None] / S; tm[:] = np.clip(1 - (yy - 760) / 300, 0, 1)
img.paste((12, 14, 18), (0, 0), Image.fromarray((tm * 255).astype(np.uint8), "L"))
crop = img.crop((0, int(P(380)), W, int(P(380 + 1440))))
d = D(crop)
d.text(540, 150, "不想打仗的他", 132, A(WHITE, 1), k=1)
d.text(540, 320, "让132人投降？", 132, A(AMBER, 1), k=1)
s = "超级士兵 No.02"; w = d.tlen(s, 56) + 110
d.rect(540 - w / 2, 1290, 540 + w / 2, 1380, fill=A((200, 50, 40), 0.96), r=45); d.text(540, 1335, s, 56, A(WHITE, 1))
out = crop.resize((1080, 1440), Image.LANCZOS); out = E.vignette(out, 0.25, 0.55)
out.save("/workspace/work/york/york_cover.png"); print(out.size)
