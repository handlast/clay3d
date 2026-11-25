# C. 像素游戏风：180×320 低分辨率无抗锯齿绘制 → 最近邻 ×6；UI 文字用 fontmode=1 半分辨率渲染再 ×2/×3 放大（像素字）
import time, math
from PIL import Image, ImageDraw
from common import *

LW, LH, K = 180, 320, 6
k = 1 / K
PALP = dict(fur=(176, 112, 64), fur_dark=(122, 74, 44), fur_light=(222, 178, 120), face=(248, 160, 150),
            skin=(232, 136, 126), blush=(255, 110, 130), ink=(44, 28, 40), white=(255, 255, 255), mouth=(160, 40, 60))

def dither(d, box, c1, c2):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            d.point((x, y), fill=c1 if (x + y) % 2 else c2)

def px_heart(d, x, y, col):   # 7×6 像素心
    pat = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
    for j, row in enumerate(pat):
        for i, ch in enumerate(row):
            if ch == "X": d.point((x + i - 3, y + j - 3), fill=col)
def px_anger(d, x, y, col):
    pat = [".X...X.", "XX...XX", ".......", ".......", "XX...XX", ".X...X."]
    for j, row in enumerate(pat):
        for i, ch in enumerate(row):
            if ch == "X": d.point((x + i - 3, y + j - 3), fill=col)
def px_bang(d, x, y, col):
    for xx in (x - 2, x + 2):
        d.rectangle((xx, y - 4, xx, y + 1), fill=col); d.point((xx, y + 3), fill=col)
FACES = {  # 小尺寸角色手工像素五官（.=透明 k=墨 w=白 m=嘴红）
    "happy": ["..........", "..k....k..", ".k.k..k.k.", "..........", "...k..k...", "....kk....", ".........."],
    "angry": ["kk......kk", ".kk....kk.", "..k....k..", ".kk....kk.", "..........", "...mmmm...", "...mwwm...", "...mmmm..."],
}
def stamp_face(d, cx, cy, expr, look=1):
    pat = FACES["happy" if expr == "happy" else "angry"]; h = len(pat); w = len(pat[0])
    col = dict(k=(44, 28, 40), w=(255, 255, 255), m=(160, 40, 60))
    for j, row in enumerate(pat):
        for i, ch in enumerate(row):
            if ch in col: d.point((cx - w // 2 + i, cy - 3 + j), fill=col[ch])

def bubble(d, x, y, w, h, col=(255, 255, 255), tail=1):
    d.rectangle((x - w // 2 + 1, y - h // 2, x + w // 2 - 1, y + h // 2), fill=col)
    d.rectangle((x - w // 2, y - h // 2 + 1, x + w // 2, y + h // 2 - 1), fill=col)
    d.polygon([(x - 2 * tail, y + h // 2), (x + 1 * tail, y + h // 2), (x - 3 * tail, y + h // 2 + 3)], fill=col)

def low_scene():
    im = Image.new("RGB", (LW, LH), (60, 64, 110)); d = ImageDraw.Draw(im)
    # 墙：两色抖动的浅紫墙 + 踢脚线；地板：棋盘格
    d.rectangle((0, 0, LW, 150), fill=(150, 170, 214))
    for y in range(0, 150, 10): d.line((0, y, LW, y), fill=(140, 160, 206))
    d.rectangle((0, 148, LW, 151), fill=(96, 104, 160))
    for j in range(16):
        for i in range(19):
            c = (204, 170, 120) if (i + j) % 2 else (190, 154, 106)
            d.rectangle((i * 10 - 5, 151 + j * 10, i * 10 + 4, 160 + j * 10), fill=c)
    # 窗户
    d.rectangle((50, 50, 130, 92), fill=(232, 236, 250)); d.rectangle((52, 52, 128, 90), fill=(110, 196, 240))
    dither(d, (52, 76, 128, 90), (110, 196, 240), (150, 214, 246))
    d.rectangle((89, 52, 90, 90), fill=(232, 236, 250)); d.rectangle((52, 70, 128, 71), fill=(232, 236, 250))
    d.rectangle((60, 58, 72, 61), fill=(255, 255, 255)); d.rectangle((63, 56, 69, 58), fill=(255, 255, 255))
    d.rectangle((112, 56, 118, 62), fill=(255, 220, 90))
    # 挂钟、白板、盆栽
    d.ellipse((34, 56, 44, 66), fill=(250, 250, 250)); d.line((39, 61, 39, 58), fill=(44, 28, 40)); d.line((39, 61, 41, 61), fill=(44, 28, 40))
    d.rectangle((140, 70, 152, 86), fill=(70, 160, 90)); d.rectangle((137, 74, 155, 82), fill=(90, 184, 104))
    d.rectangle((141, 86, 151, 98), fill=(220, 110, 80))
    # 后排工位桌（猴子坐在桌前地上）
    for x0 in (30, 100):
        d.rectangle((x0, 112, x0 + 52, 118), fill=(120, 82, 60)); d.rectangle((x0 + 2, 118, x0 + 4, 140), fill=(96, 64, 48)); d.rectangle((x0 + 48, 118, x0 + 50, 140), fill=(96, 64, 48))
        d.rectangle((x0 + 14, 98, x0 + 34, 111), fill=(70, 74, 100)); d.rectangle((x0 + 16, 100, x0 + 32, 109), fill=(120, 230, 210))
        d.rectangle((x0 + 22, 111, x0 + 26, 112), fill=(70, 74, 100))
    # 香蕉
    d.rectangle((86, 147, 94, 148), fill=(255, 220, 70)); d.point((85, 146), fill=(255, 220, 70)); d.point((95, 146), fill=(255, 220, 70))
    # 角色（低分辨率直接画）
    for name, pose, expr, x, y, s, fl, lx in CAST:
        if name == "peeker": continue
        P = [p for p in monkey_prims(pose, expr, lx, 0.6) if p["r"] not in ("ink", "white", "mouth")]
        draw_prims(d, P, x, y, s, fl, pal=PALP, k=k)
        stamp_face(d, round(x * k), round(y * k), expr, fl * (1 if lx >= 0 else -1))
    pk = [c for c in CAST if c[0] == "peeker"][0]; P = monkey_prims(pk[1], pk[2], pk[7])
    draw_prims(d, P, pk[3], pk[4], pk[5], pk[6], pal=PALP, k=k, groups=("head", "face"))
    # 前景隔板
    d.rectangle((25, 192, 155, 330), fill=(84, 150, 170)); d.rectangle((25, 192, 155, 196), fill=(130, 196, 210))
    for x in range(30, 155, 8): d.line((x, 200, x, 330), fill=(78, 140, 160))
    draw_prims(d, P, pk[3], pk[4], pk[5], pk[6], pal=PALP, k=k, groups=("hands",))
    # 头顶表情泡泡
    bubble(d, 57, 95, 13, 10); px_heart(d, 57, 95, (240, 70, 110))
    bubble(d, 122, 95, 13, 10); px_anger(d, 122, 95, (230, 50, 60))
    bubble(d, 145, 98, 11, 10, tail=-1); px_bang(d, 145, 98, (230, 50, 60))
    bubble(d, 113, 150, 15, 11, tail=-1); px_heart(d, 110, 150, (240, 70, 110)); d.point((115, 148), fill=(44, 28, 40)); d.point((116, 147), fill=(44, 28, 40)); d.point((116, 151), fill=(44, 28, 40)); d.point((116, 149), fill=(44, 28, 40))
    # 选中光标（指向理毛二猴）
    return im

def pix_text(img, xy, s, sz, fill, scale=2, anchor="mm", black=True):
    """像素字：在 1/scale 分辨率下无抗锯齿渲染，再最近邻放大贴回"""
    f = font(sz // scale, black)
    w = int(f.getlength(s)) + 4; h = sz // scale + 8
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); md.fontmode = "1"
    md.text((2, h // 2), s, font=f, fill=255, anchor="lm")
    m = m.resize((w * scale, h * scale), Image.NEAREST)
    x, y = xy
    if anchor == "mm": x -= w * scale // 2
    y -= h * scale // 2
    img.paste(Image.new("RGB", m.size, fill), (int(x), int(y)), m)
    return w * scale

def frame(t=0.0):
    img = low_scene().resize((W, H), Image.NEAREST)
    d = ImageDraw.Draw(img, "RGBA")
    # 品牌胶囊（像素方角）
    w = int(tlen("Vibe 知识大赏", 30, True)) + 60
    d.rectangle((540 - w // 2, 114, 540 + w // 2, 174), fill=(255, 255, 255)); d.rectangle((540 - w // 2 + 6, 108, 540 + w // 2 - 6, 180), fill=(255, 255, 255))
    pix_text(img, (540, 145), "Vibe 知识大赏", 32, (40, 34, 80))
    pix_text(img, (540, 212), "动物打工人 No.01", 26, (255, 255, 255), black=False)
    # 任务提示条
    d.rectangle((186, 252, 894, 330), fill=(28, 30, 64, 230)); d.rectangle((186, 252, 198, 330), fill=(255, 200, 70))
    pix_text(img, (222, 278), "任务", 28, (255, 200, 70), anchor="lm")
    pix_text(img, (300, 278), "观察同事关系", 28, (255, 255, 255), anchor="lm")
    pix_text(img, (222, 312), "吵架 1/1", 22, (150, 230, 160), anchor="lm", black=False)
    pix_text(img, (420, 312), "好朋友 0/1", 22, (255, 140, 170), anchor="lm", black=False)
    for i in range(10):   # 进度格
        d.rectangle((650 + i * 22, 300, 666 + i * 22, 322), fill=(255, 140, 170) if i < 4 else (70, 72, 110))
    # 对话框式字幕（方角 + 浅色边框 + ▼）
    lines = SUB; y0 = 1350 - 70
    d.rectangle((174, y0 - 52, 906, 1350 + 52), fill=(28, 30, 64, 235))
    d.rectangle((174, y0 - 52, 906, 1350 + 52), outline=(170, 190, 240), width=6)
    d.rectangle((174, y0 - 96, 330, y0 - 52), fill=(255, 200, 70))
    pix_text(img, (252, y0 - 73), "探头猴", 26, (40, 34, 80))
    for i, ln in enumerate(lines):
        pix_text(img, (540, y0 + i * 70), ln, 54, (255, 255, 255))
    d.polygon([(870, 1380), (886, 1380), (878, 1390)], fill=(255, 200, 70))
    return img

if __name__ == "__main__":
    t0 = time.time(); im = frame(); print("C frame sec", round(time.time() - t0, 3))
    im.save("/workspace/work/styles/C_pixel.png")
