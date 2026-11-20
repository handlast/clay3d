# contact sheet：python3 sheet.py out.png t1 t2 ...（读 tests/test_*.png，4 列，带时间与镜号标签）
import sys, cv2, numpy as np
from cues import NAMES, T
out = sys.argv[1]; ts = sys.argv[2:]
def key(t):
    t = float(t); k = NAMES[0]
    for n in NAMES:
        if T[n] <= t + 1e-6: k = n
    return k
ims = []
for t in ts:
    im = cv2.resize(cv2.imread(f"tests/test_{float(t):05.2f}.png"), (432, 768), interpolation=cv2.INTER_AREA)
    im = cv2.copyMakeBorder(im, 0, 44, 6, 6, cv2.BORDER_CONSTANT, value=(30, 24, 20))
    cv2.putText(im, f"{float(t):.1f}s  {key(t)}", (14, 800), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (240, 240, 240), 2, cv2.LINE_AA)
    ims.append(im)
while len(ims) % 4: ims.append(np.full_like(ims[0], 30))
rows = [np.hstack(ims[i:i + 4]) for i in range(0, len(ims), 4)]
cv2.imwrite(out, np.vstack(rows)); print(out)
