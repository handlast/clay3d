import sys, glob
from PIL import Image, ImageDraw
fs = sorted(glob.glob("/tmp/wl_test_*.png")); n = len(fs); cols = 6; rows = (n + cols - 1) // cols
tw, th = 360, 640
sh = Image.new("RGB", (cols * tw, rows * th), (255, 255, 255)); dr = ImageDraw.Draw(sh)
for i, f in enumerate(fs):
    im = Image.open(f).resize((tw, th)); x, y = (i % cols) * tw, (i // cols) * th; sh.paste(im, (x, y))
    # safe zone guide
    dr.rectangle((x + 180/3, y, x + 900/3, y + 1440/3), outline=(255, 0, 255)); dr.text((x + 5, y + 5), f[5:10], fill=(255, 0, 0))
sh.save(sys.argv[1] if len(sys.argv) > 1 else "sheet.png")
