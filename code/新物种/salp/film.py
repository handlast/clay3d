# 《这只海樽只住在深海？》 film — every line has its own bespoke set (scenes.py). flat 2D, no outlines. BIG1 = 0 s, BIG2 from cues.
import sys, subprocess, math, random
from scenes import *

# ---------------- captions ----------------
HL = {"hook": "玻璃桶", "tail": "小跟班", "q": "这么深", "big2": "只住深海", "depth": "280 到 2200 米", "fifty": "近海面", "slow": "很慢", "chain": "克隆体", "twenty": "20 只", "twins": "双胞胎", "gemini": "双子", "robot": "20 多年前", "name": "新属", "end": "没名字"}
def subs(t, d):
    for a, b, s, key in SUBS:
        if a <= t < b:
            ee = E.enter_exit(t, max(a, 0), b, 0.3, 0.12, rise=18, s0=0.96)
            al = ee["alpha"] if a > 0 else (1 - pr(t, b - 0.12, b))
            if al <= 0.01: return
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70 + ee["dy"] * (a > 0)
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 46, 540 + w / 2, y0 + (n - 1) * 70 + 46, fill=A((6, 14, 26), 0.82 * al), r=22)
            hw = HL.get(key)
            for i, x in enumerate(ls):
                yy = y0 + i * 70
                if hw and hw in x:
                    j = x.index(hw); parts = [(x[:j], WHITE), (hw, GOLD), (x[j + len(hw):], WHITE)]
                    xx = 540 - d.tlen(x, 54, 1) / 2
                    for p_, c_ in parts:
                        if p_: d.text(xx, yy, p_, 54, A(c_, al), anchor="lm", k=1); xx += d.tlen(p_, 54, 1)
                else: d.text(540, yy, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)
    s2 = "新物种 · 深海玻璃海樽"; w2 = d.tlen(s2, 24, 1) + 36
    d.rect(540 - w2 / 2, 210, 540 + w2 / 2, 246, fill=A((15, 12, 26), 0.35), r=18); d.text(540, 228, s2, 24, A((240, 240, 230), 0.92), k=1)

SF = {n: globals()["s_" + n] for n in NAMES}
SECS = [(-1, T[NAMES[1]], s_hook, "hook")] + [(T[n], nxt(n), SF[n], n) for n in NAMES[1:]]
SECS = [(a, (99 if i == len(SECS) - 1 else b), f, n) for i, (a, b, f, n) in enumerate(SECS)]
HARD = {BIG1, BIG2}
def cam(t):
    z = 1.0 + 0.04 * pulse(t, [BIG1, BIG2], 3); cx, cy = 540, 900
    for a, b, f, n in SECS:
        if a <= t < b: z += 0.03 * eio(pr(t, max(a, 0), min(b, DUR))); break
    sx, sy = shake(t, 8 * pulse(t, [BIG1, BIG2], 5), 40)
    return z, cx + sx, cy + sy
def render_world(t, idx):
    img = Image.new("RGB", (W, H), (4, 10, 24)); d = D(img)
    SECS[idx][2](t, d)
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
XF = 0.3
def frame(t, fi=0, ui=True):
    idx = next(i for i, (a, b, f, n) in enumerate(SECS) if a <= t < b)
    img = render_world(t, idx)
    a = SECS[idx][0]
    if idx > 0 and a not in HARD and t < a + XF:
        prev = render_world(t, idx - 1)
        img = Image.blend(prev, img, E.ease_in_out_sine((t - a) / XF))
    d = D(img)
    for c in HARD:
        if c <= t < c + 0.1 and c > 0: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.55 * (1 - (t - c) / 0.1)))
    brand(t, d)
    if ui: subs(t, d)
    out = img.resize((OW, OH), Image.LANCZOS)
    out = E.vignette(out, 0.2); out = E.grain(out, 0.03, seed=fi)
    return out
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts), int(float(ts) * 30)).save(f"/tmp/sl_test_{float(ts):05.2f}.png")
    elif sys.argv[1] == "sheet":
        ts = [float(x) for x in sys.argv[3:]]
        fr = [frame(x, int(x * 30)) for x in ts]
        E.contact_sheet(fr, cols=4, thumb_w=400, labels=[f"{x:.1f}s" for x in ts]).save(sys.argv[2])
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS, i).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
