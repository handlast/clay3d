# 连续帧小样：python3 strip.py out.png y0 y1 t1 t2 ...（裁出 y0–y1 横条，上下排列，标时间）——穿模自检用
import sys, cv2, numpy as np
out, y0, y1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); ts = sys.argv[4:]
ims = []
for t in ts:
    im = cv2.imread(f"tests/test_{float(t):05.2f}.png")[y0:y1]
    im = cv2.resize(im, (im.shape[1] * 3 // 5, im.shape[0] * 3 // 5), interpolation=cv2.INTER_AREA)
    cv2.putText(im, f"{float(t):.2f}s", (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    ims.append(im)
rows = [np.hstack(ims[i:i + 3]) for i in range(0, len(ims), 3)]
cv2.imwrite(out, np.vstack(rows)); print(out)
