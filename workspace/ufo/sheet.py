import sys, glob
from PIL import Image, ImageDraw
fs = sys.argv[2:]; cols = 6; w, h = 270, 480
sh = Image.new("RGB", (cols * w, ((len(fs) + cols - 1) // cols) * h), (255, 0, 255))
for i, f in enumerate(fs):
    im = Image.open(f).resize((w, h)); d = ImageDraw.Draw(im)
    d.line([(45, 0), (45, h)], fill=(255, 0, 0)); d.line([(225, 0), (225, h)], fill=(255, 0, 0)); d.line([(0, 360), (w, 360)], fill=(255, 0, 0))
    d.text((5, 5), f[5:-4], fill=(255, 255, 0)); sh.paste(im, ((i % cols) * w, (i // cols) * h))
sh.save(sys.argv[1])
