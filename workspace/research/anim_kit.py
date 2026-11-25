import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30

# ---------- 1. timing ----------
def clamp01(x): return 0.0 if x < 0 else 1.0 if x > 1 else x
def lerp(a, b, u): return a + (b - a) * u
def smooth(t, k=10.0):                      # Manim rate_functions.smooth
    s = lambda x: 1 / (1 + math.exp(-x))
    e = s(-k / 2)
    return clamp01((s(k * (clamp01(t) - .5)) - e) / (1 - 2 * e))
def ease_io_cubic(t):
    t = clamp01(t); return 4*t**3 if t < .5 else 1 - (-2*t + 2)**3 / 2
def ease_out_back(t, c1=1.70158):
    t = clamp01(t); c3 = c1 + 1; return 1 + c3*(t-1)**3 + c1*(t-1)**2
def there_and_back(t):                     # Manim: 0→1→0
    if t < 0 or t > 1: return 0.0
    return smooth(2*t if t < .5 else 2*(1-t))
def squish(f, a, b):                        # Manim squish_rate_func
    return lambda t: f(0.0 if t < a else 1.0 if t > b else (t - a) / (b - a))
def spring(t, stiffness=100, damping=10, mass=1, clamp=False):
    """Remotion spring() 闭式解，0→1，t 单位秒。"""
    if t <= 0: return 0.0
    w0 = math.sqrt(stiffness / mass)
    z = damping / (2 * math.sqrt(stiffness * mass))
    if z < 1:
        w1 = w0 * math.sqrt(1 - z*z)
        x = 1 - math.exp(-z*w0*t) * (math.cos(w1*t) + z*w0/w1 * math.sin(w1*t))
    else:                                    # 临界阻尼（z>=1 时 Remotion 也走这支）
        x = 1 - math.exp(-w0*t) * (1 + w0*t)
    return min(x, 1.0) if clamp else x
def kf(t, times, values, easings=None):
    """Remotion interpolate 的多关键帧 + 两端 clamp。values 可为数或元组。"""
    if t <= times[0]: return values[0]
    if t >= times[-1]: return values[-1]
    i = max(j for j in range(len(times) - 1) if times[j] <= t)
    u = (t - times[i]) / (times[i+1] - times[i])
    u = (easings[i] if easings else ease_io_cubic)(u)
    a, b = values[i], values[i+1]
    if isinstance(a, tuple): return tuple(lerp(x, y, u) for x, y in zip(a, b))
    return lerp(a, b, u)

# ---------- 2. camera frame ----------
def to_screen(p, cam):
    z, cx, cy = cam                          # 与现有 film.py 的 cam() 返回顺序一致
    return ((p[0] - cx) * z + W / 2, (p[1] - cy) * z + H / 2)
def auto_frame(boxes, margin=80, zmin=1.0, zmax=1.08, safe=(180, 120, 900, 1440)):
    """Manim MovingCamera.auto_zoom 的 PIL 版：框住若干 bbox，只用安全区。"""
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    sw, sh = safe[2] - safe[0], safe[3] - safe[1]
    z = min(sw / (x1 - x0 + 2*margin), sh / (y1 - y0 + 2*margin))
    z = max(zmin, min(zmax, z))
    scx, scy = (safe[0] + safe[2]) / 2, (safe[1] + safe[3]) / 2
    cx = (x0 + x1) / 2 - (scx - W/2) / z
    cy = (y0 + y1) / 2 - (scy - H/2) / z
    return (z, cx, cy)

# ---------- 3. follow ----------
def build_follow_track(target_fn, dur, stiffness=40.0, dead=60.0):
    n = int(dur * FPS) + 1
    w0 = math.sqrt(stiffness); dt = 1 / FPS
    pos = np.array(target_fn(0.0), float); vel = np.zeros(2)
    out = np.zeros((n, 2))
    for i in range(n):
        tgt = np.array(target_fn(i * dt), float)
        d = tgt - pos
        dist = np.linalg.norm(d)
        goal = pos if dist < dead else tgt - d / dist * dead
        acc = w0*w0 * (goal - pos) - 2 * w0 * vel   # 临界阻尼 zeta=1
        vel += acc * dt; pos += vel * dt
        out[i] = pos
    return out

# ---------- 4. morph ----------
def resample(poly, n):
    p = np.asarray(poly, float); q = np.vstack([p, p[:1]])
    seg = np.linalg.norm(np.diff(q, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    s = np.linspace(0, cum[-1], n, endpoint=False)
    idx = np.searchsorted(cum, s, side='right') - 1
    u = ((s - cum[idx]) / np.maximum(seg[idx], 1e-9))[:, None]
    return q[idx] * (1 - u) + q[idx + 1] * u
def signed_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)
def align_shapes(a, b, n=180):
    A, B = resample(a, n), resample(b, n)
    if np.sign(signed_area(A)) != np.sign(signed_area(B)): B = B[::-1]
    k = min(range(n), key=lambda k: np.sum((A - np.roll(B, -k, 0))**2))
    return A, np.roll(B, -k, 0)
def morph(A, B, u, arc=0.0):
    if abs(arc) < 1e-3: return A + (B - A) * u
    v = B - A; c = A + v / 2 + np.stack([-v[:, 1], v[:, 0]], 1) / 2 / math.tan(arc / 2)
    ang = arc * u; ca, sa = math.cos(ang), math.sin(ang)
    r = A - c
    return c + np.stack([r[:, 0]*ca - r[:, 1]*sa, r[:, 0]*sa + r[:, 1]*ca], 1)

# ---------- 7. lagged ----------
def lagged(t, n, run_time, lag=0.15):
    """Manim AnimationGroup.build_animations_with_timings：总时长固定为 run_time。"""
    total = 1 + lag * (n - 1)
    d = run_time / total
    return [clamp01((t - i * lag * d) / d) for i in range(n)]

# ---------- 8. partial polyline ----------
def partial(points, a, b):
    p = np.asarray(points, float)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)]); L = cum[-1]
    def at(s):
        i = min(np.searchsorted(cum, s, side='right') - 1, len(seg) - 1)
        u = (s - cum[i]) / max(seg[i], 1e-9); return p[i] * (1 - u) + p[i+1] * u
    sa, sb = a * L, b * L
    mid = [tuple(p[i]) for i in range(len(p)) if sa < cum[i] < sb]
    return [tuple(at(sa))] + mid + [tuple(at(sb))]
def passing_bounds(u, tw=0.3):              # Manim ShowPassingFlash._get_bounds
    upper = u * (1 + tw); lower = upper - tw
    return max(lower, 0.0), min(upper, 1.0)

if __name__ == "__main__":
    print([round(spring(x/30), 3) for x in (0, 5, 10, 15, 30)])
    print(kf(1.5, [0, 1, 2], [(0, 0, 1.0), (100, 0, 1.05), (100, 50, 1.0)]))
    print(auto_frame([(300, 600, 700, 1100)]))
    tr = build_follow_track(lambda t: (540 + 300*math.sin(t), 960), 4)
    print(tr[::30].round(1))
    sq = [(0, 0), (200, 0), (200, 200), (0, 200)]
    circ = [(100 + 100*math.cos(a), 100 + 100*math.sin(a)) for a in np.linspace(0, 6.28, 60, endpoint=False)]
    A, B = align_shapes(sq, circ)
    print(morph(A, B, .5, arc=math.pi/2)[:2].round(1), morph(A, B, 1.0, arc=1.0)[0].round(1), B[0].round(1))
    print([round(x, 2) for x in lagged(0.5, 5, 1.0, 0.2)])
    print(partial([(0, 0), (100, 0), (100, 100)], 0, .75))
    print(passing_bounds(.5))
    # render smoke test
    img = Image.new("RGB", (W, H), (20, 24, 40)); d = ImageDraw.Draw(img, "RGBA")
    d.polygon([tuple(p) for p in morph(A, B, .5) + 400], fill=(255, 170, 60))
    img.resize((270, 480)).save("/tmp/smoke.png")
