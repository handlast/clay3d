"""渲染前/后防闪烁检查（2026-11-14，起因：《断桥》蚂蚁突然消失/出现、场景闪烁）

用法
  1) 代码静态扫描:   python3 popcheck.py lint  film.py scene.py world.py
  2) 实体数量跳变:   在作品目录里  python3 -c "import popcheck,film; popcheck.count_jumps(film.bridge_crowd, 60, 200)"
  3) 成片亮度突跳:   python3 popcheck.py video out.mp4 [cut秒,cut秒,...]
任何一项有输出，先解释或修掉再全片渲染。
"""
import re, sys, subprocess

LINT = [
    (r"\.any\(\)\s*:\s*return", "近裁剪面全有全无：一个点穿过镜头整物体消失。改成逐段裁剪，或按距离渐隐(alpha)，并把整条镜头轨迹离物体留足距离"),
    (r"%\s*\d+\s*==\s*0", "按 i%N 抽掉实体：若和时间阈值(t>xx)连用，会在一帧内整批消失。改成每个实体有自己的消失时间并 0.3–0.5s 渐隐/走出画面"),
    (r"default_rng\(\s*fi\s*\)|default_rng\(\s*int\(t", "每帧重新随机：位置逐帧乱跳=闪烁。随机只用于生成固定种子，用 t 连续驱动"),
    (r"fi\s*%\s*\d+", "噪声/纹理按 fi%N 循环：低帧数循环会被看成频闪。用连续流动噪声或更长循环"),
    (r"zc\s*[<>]\s*fogd\s*\*", "按距离硬裁剪：裁剪点必须在雾已完全遮住之后(fade≈0)，否则远处物体跳出"),
    (r"s_\[[01]\]\s*[<>]\s*-?\s*W|s_\[[01]\]\s*[<>]\s*H", "屏幕外剔除：边距要大于物体最大投影尺寸，否则边缘物体会切掉"),
]

def lint(files):
    hit = 0
    for f in files:
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            for pat, why in LINT:
                if re.search(pat, line):
                    hit += 1; print(f"{f}:{n}: {line.strip()[:110]}\n    -> {why}")
    print(f"lint: {hit} 处需要确认")

def count_jumps(fn, t0, t1, fps=30, thr=3, expect=()):
    """fn(t)->实体列表。相邻帧数量变化 >=thr 即报告（expect 里的秒数是有意为之，可忽略）"""
    prev = None; out = []
    for k in range(int((t1 - t0) * fps)):
        t = t0 + k / fps; n = len(fn(t))
        if prev is not None and abs(n - prev) >= thr and not any(abs(t - e) < 0.05 for e in expect):
            out.append((round(t, 2), n - prev))
        prev = n
    for t, d in out: print(f"count jump at {t:.2f}s: {d:+d}")
    print(f"count_jumps: {len(out)} 处"); return out

def video(path, cuts=()):
    """整帧平均亮度单帧突跳（排除镜头切点 cuts）"""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=160:90", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32)
    y = g.mean((1, 2)); d = np.abs(y[1:-1] - 0.5 * (y[:-2] + y[2:]))
    bad = [(i + 1) / 30 for i in np.nonzero(d > 3.0)[0] if not any(abs((i + 1) / 30 - c) < 0.07 for c in cuts)]
    for t in bad: print(f"luma blip at {t:.2f}s")
    print(f"video: {len(bad)} 处")

if __name__ == "__main__":
    if sys.argv[1] == "lint": lint(sys.argv[2:])
    elif sys.argv[1] == "video": video(sys.argv[2], [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else ())
