from PIL import Image
from base import *
import film as F
from toon import horse, goat
from chars import baby, flame, FIRE_L, HRED, HRED_D, INKB
from fx import rays, embers, glow
CW, CH = 1080, 1440
img = Image.new("RGB", (W, int(CH * S)), F.BG); d = D(img)
t = 0.9
rays(d, t, (150, 30, 20), (50, 8, 8), 22, 540, 900)
embers(d, t, FIRE_L, 1, 50)
for i in range(10): flame(d, 20 + i * 115, 1450, 300 + 80 * (i % 3), t, 0.9, i * 2.3)
# babies falling
for i in range(18):
    bx = 600 + (i % 6) * 75; by = 720 + (i // 6) * 100
    if i % 3 == 1: baby(d, bx, by + 60, 28, 0.35)
    else: baby(d, bx, by, 30)
horse(d, 330, 1050, 190, 0.12, "scream", 0, 1.0, look=(0.8, 0))
d.text(550, 168, "一句谣言", 130, A(INKB, 1), k=1); d.text(540, 160, "一句谣言", 130, A(WHITE, 1), k=1)
d.rect(110, 245, 970, 455, fill=A((20, 6, 6), 0.75), r=40)
d.text(552, 362, "少生46万", 190, A(HRED_D, 1), k=1); d.text(540, 350, "少生46万", 190, A((255, 222, 80), 1), k=1)
d.text(540, 520, "2026 双火马年 · 日本1966", 52, A(FIRE_L, 1), k=1)
d.rect(150, 1250, 930, 1360, fill=A(HRED, 1), r=55)
d.text(540, 1305, "现在，每一年都是丙午", 62, A(WHITE, 1), k=1)
d.rect(40, 40, 290, 88, fill=A(WHITE, 0.92), r=24); d.text(165, 64, "Vibe 知识大赏", 26, A(F.BG, 1))
img.resize((CW, CH), Image.LANCZOS).save("cover_v2.png")
