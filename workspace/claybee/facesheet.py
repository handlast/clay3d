# 脸部 2× 自检拼图：python3 facesheet.py out.png（读 tests/face_*.png，每张缩到 360 高，带时间标签）
import sys, glob, cv2, numpy as np
fs = sorted(glob.glob("tests/face_*.png")); ims = []
for f in fs:
    im = cv2.imread(f); h = 360; im = cv2.resize(im, (int(im.shape[1] * h / im.shape[0]), h), interpolation=cv2.INTER_AREA)
    im = cv2.copyMakeBorder(im, 0, 30, 4, 4, cv2.BORDER_CONSTANT, value=(30, 24, 20))
    cv2.putText(im, f.split("_")[1], (8, 382), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2); ims.append(im)
rows, cur, w = [], [], 0
for im in ims:
    if w + im.shape[1] > 2000 and cur: rows.append(cur); cur, w = [], 0
    cur.append(im); w += im.shape[1]
rows.append(cur); W = max(sum(i.shape[1] for i in r) for r in rows)
out = np.vstack([np.hstack(r + [np.full((390, W - sum(i.shape[1] for i in r), 3), 30, np.uint8)]) for r in rows])
cv2.imwrite(sys.argv[1], out); print(sys.argv[1], out.shape)
