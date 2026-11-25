"""easing.py — motion helpers for the Pillow frame-by-frame pipeline.

Pure functions of time (seconds), deterministic, no state between frames.
Distilled from: remotion-dev/skills (timing.md), haidrrrry/claude-remotion-skill
(theme.ts spring presets, exits, breathing, grain/vignette), jabezpauls/edu-video-generator
(closed-form springs.py, presets snappy/default/heavy/playful), Mort1d/motion-graphics-skills
(outExpo in / inExpo out, stagger 1/8-1/4 beat).

    from easing import spring, spring_u, ease_out_back, stagger, envelope, breathe, grain, vignette

Run `python3 easing.py` for the self-test.
"""
from __future__ import annotations

import math
from functools import lru_cache

# --------------------------------------------------------------------------- springs
# Remotion-style physical params (m x'' + c x' + k x = k). zeta = c / (2 sqrt(k m)).
PRESETS = {
    # from haidrrrry theme.ts
    "snappy": dict(stiffness=160, damping=14, mass=0.6),   # zeta~0.71, words/UI pops
    "smooth": dict(stiffness=90, damping=20, mass=1.0),    # zeta~1.05, big elements, no overshoot
    "bouncy": dict(stiffness=170, damping=11, mass=0.7),   # zeta~0.50, characters / playful
    # heavy: critically damped, for big type / keywords (type never bounces - Mort1d)
    "heavy": dict(stiffness=120, damping=2 * math.sqrt(120 * 1.0), mass=1.0),
    # punch-in from iart-ai retention-pacing.md (damping 13, stiffness 220)
    "punch": dict(stiffness=220, damping=13, mass=1.0),
}


def _p(preset, stiffness, damping, mass):
    if preset is not None:
        d = PRESETS[preset] if isinstance(preset, str) else preset
        return d["stiffness"], d["damping"], d.get("mass", 1.0)
    return stiffness, damping, mass


def spring(t, stiffness=170.0, damping=26.0, mass=1.0, preset=None):
    """Unit step response of a damped spring released at t=0 (seconds). 0 for t<=0, -> 1.

    Under-damped presets overshoot above 1 before settling (that is the point)."""
    if t <= 0:
        return 0.0
    k, c, m = _p(preset, stiffness, damping, mass)
    w0 = math.sqrt(k / m)
    z = c / (2.0 * math.sqrt(k * m))
    if z < 1.0 - 1e-9:
        wd = w0 * math.sqrt(1 - z * z)
        return 1 - math.exp(-z * w0 * t) * (math.cos(wd * t) + (z * w0 / wd) * math.sin(wd * t))
    if z <= 1.0 + 1e-9:
        return 1 - math.exp(-w0 * t) * (1 + w0 * t)
    wd = w0 * math.sqrt(z * z - 1)
    # numerically stable overdamped form
    r1, r2 = -w0 * (z - math.sqrt(z * z - 1)), -w0 * (z + math.sqrt(z * z - 1))
    return 1 + (r2 * math.exp(r1 * t) - r1 * math.exp(r2 * t)) / (r1 - r2)


@lru_cache(maxsize=64)
def settle_time(stiffness=170.0, damping=26.0, mass=1.0, eps=0.005, preset=None):
    """Seconds after which the spring stays within eps of 1 for good."""
    last, dt = 0.0, 0.002
    t = 0.0
    while t < 10.0:
        t += dt
        if abs(1 - spring(t, stiffness, damping, mass, preset)) >= eps:
            last = t
    return last


def spring_u(u, preset="snappy", eps=0.005):
    """Normalised spring: u in [0,1] -> value, exactly 0 at u=0 and exactly 1 at u=1.
    Stretch over any duration you like: spring_u((t - t0) / dur)."""
    if u <= 0:
        return 0.0
    if u >= 1:
        return 1.0
    T = settle_time(eps=eps, preset=preset)
    end = spring(T, preset=preset)
    return spring(u * T, preset=preset) / end


def spring_at(t, t0, a=0.0, b=1.0, preset="snappy"):
    """One spring from a to b released at t0 seconds, evaluated at t."""
    return a + (b - a) * spring(t - t0, preset=preset)


def track(t, keys, preset="smooth"):
    """Sum of springs: keys = [(t0, value0), (t1, value1), ...]. A retarget mid-move keeps
    its velocity (Mort1d track(), jabezpauls C.trk). Value before keys[0][0] = value0."""
    v = keys[0][1]
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        v += (vb - va) * spring(t - tb, preset=preset)
    return v


# --------------------------------------------------------------------------- eases (u in 0..1)
def clamp01(u):
    return 0.0 if u < 0 else 1.0 if u > 1 else u


def prog(t, t0, dur):
    """Clamped linear progress of t through [t0, t0+dur]. ALWAYS clamp (remotion timing.md)."""
    return clamp01((t - t0) / dur) if dur > 0 else float(t >= t0)


def ease_out_cubic(u):
    u = clamp01(u); return 1 - (1 - u) ** 3


def ease_in_cubic(u):
    u = clamp01(u); return u ** 3


def ease_out_expo(u):
    u = clamp01(u); return 1.0 if u >= 1 else 1 - 2 ** (-10 * u)


def ease_in_expo(u):
    u = clamp01(u); return 0.0 if u <= 0 else 2 ** (10 * u - 10)


def ease_in_out_sine(u):
    u = clamp01(u); return -(math.cos(math.pi * u) - 1) / 2


def ease_out_back(u, s=1.70158):
    """Overshoots ~10% (s=1.70158) then settles at 1. Bigger s = more overshoot."""
    u = clamp01(u)
    c3 = s + 1
    return 1 + c3 * (u - 1) ** 3 + s * (u - 1) ** 2


@lru_cache(maxsize=32)
def _back_s_for(amount):
    lo, hi = 0.0, 10.0
    for _ in range(50):
        s = (lo + hi) / 2
        pk = max(ease_out_back(i / 400, s) for i in range(401)) - 1
        lo, hi = (s, hi) if pk < amount else (lo, s)
    return (lo + hi) / 2


def overshoot(u, amount=0.12):
    """Ease-out that peaks at exactly 1+amount (0.12 = 12 %) then settles at 1."""
    return ease_out_back(u, _back_s_for(round(amount, 4)))


def perceptual_scale(u, s0, s1):
    """Interpolate scale geometrically so a zoom reads even (remotion 'perceptual-scale')."""
    s0 = max(s0, 1e-4)
    return s0 * (s1 / s0) ** u


def slam(t, t0, dur=0.28, s_from=1.7):
    """Slam-in scale: s_from -> 1 with a hair of overshoot (Mort1d slam ~1.7 -> 1)."""
    u = prog(t, t0, dur)
    return perceptual_scale(ease_out_back(u, 1.2), s_from, 1.0) if u < 1 else 1.0


# --------------------------------------------------------------------------- stagger / envelopes
def stagger(i, n, total, gap=None):
    """Start offset and duration for item i of n inside `total` seconds.
    gap=None -> gap = 0.25 * per-item duration (words 40-70 ms, lines 60-100 ms typical).
    Returns (start_offset, item_dur). Last item ends exactly at `total`."""
    if n <= 1:
        return 0.0, float(total)
    if gap is None:
        # solve total = d + (n-1)*0.25*d
        d = total / (1 + 0.25 * (n - 1))
        gap = 0.25 * d
    d = total - (n - 1) * gap
    if d <= 0:
        raise ValueError("stagger: gap too big for total")
    return i * gap, d


def envelope(t, t_in, t_out, d_in=0.35, d_out=None, ease_in=ease_out_expo, ease_out=ease_in_cubic):
    """0 -> 1 -> 0 visibility/progress: enters at t_in over d_in, leaves so it is fully gone at t_out.
    Exit is faster than entry by default (d_out = 0.5*d_in; haidrrrry: ~10 frames vs ~20)."""
    if d_out is None:
        d_out = 0.5 * d_in
    if t < t_in or t >= t_out:
        return 0.0
    a = ease_in(prog(t, t_in, d_in))
    b = 1 - ease_out(prog(t, t_out - d_out, d_out))
    return min(a, b)


def enter_exit(t, t_in, t_out, d_in=0.35, d_out=None, rise=40, s0=0.94, preset="snappy"):
    """Entrance animating 3 props together (opacity + y + scale) and a faster exit.
    Returns dict(alpha, dy, scale). alpha snaps on within ~4 frames (jabezpauls)."""
    if d_out is None:
        d_out = 0.5 * d_in
    if t < t_in or t >= t_out:
        return dict(alpha=0.0, dy=float(rise), scale=s0)
    p = spring_u(prog(t, t_in, d_in), preset)            # may overshoot
    alpha = clamp01(prog(t, t_in, min(d_in, 4 / 30)))
    q = ease_in_cubic(prog(t, t_out - d_out, d_out))      # accelerating away
    return dict(alpha=alpha * (1 - q), dy=rise * (1 - p) - rise * 0.8 * q, scale=s0 + (1 - s0) * p)


# --------------------------------------------------------------------------- idle / camera
def breathe(t, amp=0.015, hz=0.45, phase=0.0):
    """Idle scale multiplier 1 +- amp (haidrrrry: 1 + sin(frame/22)*0.015 at 30 fps ~ 0.22 Hz-0.45Hz)."""
    return 1.0 + amp * math.sin(2 * math.pi * hz * t + phase)


def bob(t, px=3.0, hz=0.32, phase=0.0):
    """Idle vertical float in px (haidrrrry: sin(frame/30)*3)."""
    return px * math.sin(2 * math.pi * hz * t + phase)


def _hash01(i, seed):
    x = math.sin(i * 12.9898 + seed * 78.233) * 43758.5453
    return x - math.floor(x)


def shake(t, t0, amp=8.0, dur=0.35, hz=24.0, seed=0):
    """Decaying deterministic shake (dx, dy) in px. OUR RULE: 8 px on the 2 big hits, 1.5 px max otherwise."""
    if t < t0 or t > t0 + dur:
        return 0.0, 0.0
    u = (t - t0) / dur
    decay = (1 - u) ** 2
    k = (t - t0) * hz
    i0 = int(k)
    f = k - i0
    def n(i, s):
        return _hash01(i, seed + s) * 2 - 1
    sx = n(i0, 1) * (1 - f) + n(i0 + 1, 1) * f
    sy = n(i0, 2) * (1 - f) + n(i0 + 1, 2) * f
    return amp * decay * sx, amp * decay * sy


def caption_dwell(text):
    """OUR RULE: on-screen read time >= max(1.5 s, chars / 4 s)."""
    n = len([c for c in text if not c.isspace()])
    return max(1.5, n / 4.0)


# --------------------------------------------------------------------------- PIL post layers
try:
    import numpy as np
    from PIL import Image
except Exception:  # pragma: no cover
    np = None
    Image = None


@lru_cache(maxsize=4)
def _noise_field(h, w, pad=256, base_seed=1234):
    """One cached full-size noise field (int8, sigma ~32) slightly larger than the frame."""
    rng = np.random.default_rng(base_seed)
    n = rng.standard_normal((h + pad, w + pad)).astype(np.float32) * 32.0
    return np.clip(n, -127, 127).astype(np.int8)


def grain(img, strength=0.035, seed=0, protect_black=True):
    """Monochrome film grain on a PIL RGB image, deterministic per seed (use seed=frame index).
    strength = noise sigma as fraction of 255 (0.03-0.05 subtle on dark grounds).
    Fast (~0.1 s at 1080x1920): slices a cached noise field at a seed-derived offset.
    protect_black: weaker grain in near-black so dark backgrounds stay clean."""
    img = img.convert("RGB")
    w, h = img.size
    pad = 256
    field = _noise_field(h, w, pad)
    ox = int(_hash01(seed, 7) * pad)
    oy = int(_hash01(seed, 11) * pad)
    n = field[oy:oy + h, ox:ox + w].astype(np.float32) * (strength * 255.0 / 32.0)
    a = np.asarray(img, dtype=np.int16)
    if protect_black:
        g = a[..., 1].astype(np.float32) * (1.0 / 255.0)
        n *= 0.35 + 0.65 * np.minimum(g * 2.0, 1.0)
    out = a + n.astype(np.int16)[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


@lru_cache(maxsize=4)
def _vignette_mask(w, h, inner, strength):
    y, x = np.ogrid[0:h, 0:w]
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    r = np.sqrt(nx * nx + ny * ny) / math.sqrt(2)          # 0 center, 1 corner
    u = np.clip((r - inner) / (1 - inner), 0, 1)
    u = u * u * (3 - 2 * u)                                 # smoothstep
    keep = 1 - strength * u                                 # multiply factor
    return Image.fromarray((keep * 255).astype(np.uint8), "L")


def vignette(img, strength=0.22, inner=0.56):
    """Darken edges (haidrrrry: radial transparent 56% -> rgba(0,0,0,.22)). Center untouched."""
    img = img.convert("RGB")
    m = _vignette_mask(img.width, img.height, inner, strength)
    black = Image.new("RGB", img.size, (0, 0, 0))
    return Image.composite(img, black, m)


def subframe_blur(draw_fn, t, fps=30, samples=4, shutter=0.5):
    """Motion blur by averaging `samples` renders across the shutter window before t
    (remotion HtmlInCanvasMotionBlur idea: shutterAngle 180 = 0.5 frame). draw_fn(t)->PIL RGB.
    Costs `samples`x render time: use only on whip/slam windows."""
    if samples <= 1 or shutter <= 0:
        return draw_fn(t)
    acc = None
    for k in range(samples):
        tk = t - shutter / fps * (k / (samples - 1))
        a = np.asarray(draw_fn(tk), dtype=np.float32)
        acc = a if acc is None else acc + a
    return Image.fromarray(np.clip(acc / samples + 0.5, 0, 255).astype(np.uint8), "RGB")


def contact_sheet(frames, cols=6, thumb_w=270, labels=None, bg=(20, 20, 24)):
    """Tile PIL frames into one sheet (thumb_w=270 ~ 1/4 of 1080 = 'phone view' check)."""
    from PIL import ImageDraw
    th = [f.convert("RGB").resize((thumb_w, int(f.height * thumb_w / f.width)), Image.LANCZOS) for f in frames]
    h = th[0].height
    rows = (len(th) + cols - 1) // cols
    pad = 6
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (h + pad + 22) + pad), bg)
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(th):
        x = pad + (i % cols) * (thumb_w + pad)
        y = pad + (i // cols) * (h + pad + 22)
        sheet.paste(im, (x, y + 22))
        if labels:
            d.text((x + 4, y + 4), str(labels[i]), fill=(230, 230, 230))
    return sheet


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    import time

    ok = 0
    def check(cond, msg):
        global ok
        assert cond, msg
        ok += 1

    # springs
    for name in PRESETS:
        check(spring(0, preset=name) == 0.0, f"{name} starts at 0")
        check(abs(spring(5, preset=name) - 1) < 1e-3, f"{name} settles to 1")
        check(spring_u(0, name) == 0.0 and spring_u(1, name) == 1.0, f"{name} spring_u endpoints")
    peak = lambda p: max(spring(i / 1000, preset=p) for i in range(3000))
    check(peak("bouncy") > 1.1, "bouncy overshoots >10%")
    check(peak("snappy") > 1.0, "snappy overshoots a hair")
    check(peak("heavy") <= 1.0 + 1e-9, "heavy never overshoots")
    check(peak("smooth") <= 1.0 + 1e-9, "smooth (overdamped) never overshoots")
    check(0.1 < settle_time(preset="snappy") < 1.0, f"snappy settles fast ({settle_time(preset='snappy'):.3f}s)")
    # monotone-ish start
    check(spring(0.01, preset="snappy") < spring(0.05, preset="snappy"), "spring rises")
    # track keeps continuity
    k = [(0, 0), (1.0, 100), (1.2, 50)]
    check(abs(track(0.999, k) - track(1.001, k)) < 1, "track continuous at retarget")
    check(abs(track(6, k) - 50) < 0.5, "track ends at last target")

    # eases
    for f in (ease_out_cubic, ease_in_cubic, ease_out_expo, ease_in_expo, ease_in_out_sine, ease_out_back, overshoot):
        check(abs(f(0)) < 1e-9 and abs(f(1) - 1) < 1e-9, f"{f.__name__} endpoints")
    check(max(ease_out_back(i / 100) for i in range(101)) > 1.05, "ease_out_back overshoots")
    check(max(overshoot(i / 100, 0.12) for i in range(101)) > 1.03, "overshoot overshoots")
    check(abs(perceptual_scale(0.5, 1, 4) - 2) < 1e-9, "perceptual scale geometric")
    check(slam(0, 0) > 1.6 and slam(1, 0) == 1.0, "slam 1.7 -> 1")

    # stagger
    s = [stagger(i, 5, 1.0) for i in range(5)]
    check(s[0][0] == 0 and abs(s[-1][0] + s[-1][1] - 1.0) < 1e-9, "stagger fits total")
    s2 = [stagger(i, 4, 0.8, gap=0.06) for i in range(4)]
    check(abs(s2[3][0] - 0.18) < 1e-9 and abs(s2[3][1] - 0.62) < 1e-9, "stagger with gap")
    try:
        stagger(0, 10, 0.3, gap=0.1); check(False, "stagger should raise")
    except ValueError:
        ok += 1

    # envelope: exit faster than entry
    check(envelope(0.99, 1, 3) == 0 and envelope(3.0, 1, 3) == 0, "envelope outside = 0")
    check(abs(envelope(2.0, 1, 3) - 1) < 1e-9, "envelope mid = 1")
    t_half_in = next(i / 1000 for i in range(1000, 3000) if envelope(i / 1000, 1, 3, 0.4) >= 0.5) - 1
    t_half_out = 3 - next(i / 1000 for i in range(2000, 3000) if envelope(i / 1000, 1, 3, 0.4) <= 0.5)
    check(t_half_out > 0 and t_half_in > 0, "envelope has both ramps")
    ee = enter_exit(1.5, 1, 3)
    check(ee["alpha"] == 1 and abs(ee["dy"]) < 2, "enter_exit settled")
    check(enter_exit(2.99, 1, 3)["alpha"] < 0.3, "enter_exit leaving")

    # breathe / shake / dwell
    vals = [breathe(i / 30) for i in range(300)]
    check(max(vals) <= 1.015 + 1e-9 and min(vals) >= 0.985 - 1e-9, "breathe bounded")
    check(shake(0.5, 0, 8)[0] == 0 and shake(-1, 0)[0] == 0, "shake ends")
    check(max(abs(shake(i / 300, 0, 8)[0]) for i in range(100)) <= 8, "shake <= amp")
    check(shake(0.1, 0, 8, seed=3) == shake(0.1, 0, 8, seed=3), "shake deterministic")
    check(caption_dwell("一二三") == 1.5 and caption_dwell("一" * 12) == 3.0, "dwell rule")

    # PIL layers on a 1080x1920 dark frame
    img = Image.new("RGB", (1080, 1920), (18, 20, 34))
    from PIL import ImageDraw
    ImageDraw.Draw(img).ellipse((340, 760, 740, 1160), fill=(230, 80, 60))
    t0 = time.time(); g = grain(img, 0.04, seed=5); tg = time.time() - t0
    t0 = time.time(); v = vignette(img); tv = time.time() - t0
    ga, ia = np.asarray(g, np.float32), np.asarray(img, np.float32)
    check(abs(ga.mean() - ia.mean()) < 1.5, "grain preserves mean")
    check(np.abs(ga - ia).mean() > 1.0, "grain adds noise")
    check(np.array_equal(np.asarray(grain(img, 0.04, 5)), np.asarray(g)), "grain deterministic")
    check(not np.array_equal(np.asarray(grain(img, 0.04, 6)), np.asarray(g)), "grain varies by seed")
    va = np.asarray(v, np.float32)
    check(np.allclose(va[960, 540], ia[960, 540], atol=1), "vignette keeps centre")
    check(va[5, 5].mean() < ia[5, 5].mean() * 0.85, "vignette darkens corner")
    # subframe blur and sheet
    def draw(tt):
        im = Image.new("RGB", (200, 100)); ImageDraw.Draw(im).rectangle((int(tt * 3000) % 150, 40, int(tt * 3000) % 150 + 20, 60), fill=(255, 255, 255)); return im
    b = subframe_blur(draw, 0.02, samples=4)
    check(np.asarray(b).max() < 255 and np.asarray(b).max() > 0, "subframe blur smears")
    sh = contact_sheet([img] * 7, cols=4, labels=[f"{i}s" for i in range(7)])
    check(sh.width > 1000, "contact sheet")
    print(f"easing.py self-test: {ok} checks passed | grain {tg*1000:.0f} ms, vignette {tv*1000:.0f} ms @1080x1920")
