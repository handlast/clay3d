import sys, glob
from PIL import Image
fs = sorted(glob.glob("test_*.png")); n = len(fs); cols = 5; rows = (n + cols - 1) // cols
tw, th = 324, 576
sh = Image.new("RGB", (cols * tw, rows * th), (0, 0, 0))
for i, f in enumerate(fs): sh.paste(Image.open(f).resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
sh.save(sys.argv[1] if len(sys.argv) > 1 else "sheet.png")
