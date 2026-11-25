# procedural ground textures (cached as .npy). Each texture = TS mm square, 2048 px, RGB float32 0..1
import numpy as np, os, cv2
HERE = os.path.dirname(os.path.abspath(__file__))
S = 2048

def fbm(seed, octaves=6, base=8):
    rng = np.random.default_rng(seed); out = np.zeros((S, S), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o
        g = rng.standard_normal((n, n)).astype(np.float32)
        g = np.tile(g, (3, 3)); g = cv2.resize(g, (S * 3, S * 3), interpolation=cv2.INTER_CUBIC)[S:2 * S, S:2 * S]
        out += g * amp; tot += amp; amp *= 0.55
    out /= tot; return (out - out.mean()) / (out.std() + 1e-6)

def grains(img, rng, n, rmin, rmax, cols, light=(-0.6, -0.7)):
    # realistic grains: colour layer + soft shadow + soft highlight + per-grain mottling
    sh = np.zeros((S, S), np.float32); hl = np.zeros((S, S), np.float32)
    for i in range(n):
        x, y = rng.uniform(0, S, 2); r = rng.uniform(rmin, rmax) * (1 + 0.6 * rng.random() ** 4); e = rng.uniform(0.55, 1.0); a = rng.uniform(0, 180)
        c = np.array(cols[rng.integers(len(cols))], np.float32) * rng.uniform(0.82, 1.1)
        c = c * 0.75 + c.mean() * 0.25
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                cx, cy = x + ox, y + oy
                if -rmax * 3 < cx < S + rmax * 3 and -rmax * 3 < cy < S + rmax * 3:
                    ax = (int(r * 4), int(r * e * 4))
                    cv2.ellipse(sh, (int((cx - light[0] * r * 0.5) * 4), int((cy - light[1] * r * 0.5) * 4)), (int(r * 4.4), int(r * e * 4.4)), a, 0, 360, 1.0, -1, cv2.LINE_AA, 2)
                    cv2.ellipse(img, (int(cx * 4), int(cy * 4)), ax, a, 0, 360, tuple(float(v) for v in c), -1, cv2.LINE_AA, 2)
                    cv2.ellipse(sh, (int(cx * 4), int(cy * 4)), ax, a, 0, 360, 0.0, -1, cv2.LINE_AA, 2)
                    cv2.ellipse(hl, (int((cx + light[0] * r * 0.4) * 4), int((cy + light[1] * r * 0.4) * 4)), (max(1, int(r * 2.0)), max(1, int(r * e * 1.6))), a, 0, 360, 1.0, -1, cv2.LINE_AA, 2)
    sh = cv2.GaussianBlur(sh, (0, 0), max(1.0, rmin * 0.6)); hl = cv2.GaussianBlur(hl, (0, 0), max(1.0, rmin * 0.5))
    img *= (1 - 0.45 * sh)[..., None]; img += 0.18 * hl[..., None]
    np.clip(img, 0, 1, out=img)

def finish(img, seed):
    rng = np.random.default_rng(seed)
    n = rng.standard_normal((S, S)).astype(np.float32)
    img += (0.035 * n + 0.02 * cv2.GaussianBlur(n, (0, 0), 1.5))[..., None]
    g = img.mean(2, keepdims=True); img[:] = g + (img - g) * 0.8
    np.clip(img, 0, 1, out=img)

def make(name):
    p = os.path.join(HERE, f"tex_{name}.npy")
    if os.path.exists(p): return np.load(p, mmap_mode="r")
    rng = np.random.default_rng(hash(name) % 1000)
    if name == "sand":      # TS = 60 mm: sand grains 0.2-1 mm => 7-34 px
        n1 = fbm(1); base = np.array([0.62, 0.53, 0.40]) + 0.05 * n1[..., None]
        img = np.clip(base, 0, 1).astype(np.float32)
        cols = [(0.78, 0.68, 0.52), (0.66, 0.56, 0.42), (0.52, 0.44, 0.34), (0.85, 0.80, 0.70), (0.45, 0.40, 0.36), (0.70, 0.52, 0.36)]
        grains(img, rng, 4000, 9, 20, cols); grains(img, rng, 16000, 4, 10, cols); grains(img, rng, 9000, 3, 7, cols); finish(img, 1)
    elif name == "soil":    # darker organic soil w/ pebbles & debris, TS = 80 mm
        n1 = fbm(2); n2 = fbm(3, base=32)
        base = np.array([0.36, 0.27, 0.19]) + 0.06 * n1[..., None] + 0.03 * n2[..., None]
        img = np.clip(base, 0, 1).astype(np.float32)
        cols = [(0.50, 0.40, 0.30), (0.40, 0.32, 0.25), (0.62, 0.55, 0.45), (0.30, 0.23, 0.17), (0.55, 0.45, 0.32)]
        grains(img, rng, 900, 8, 20, cols); grains(img, rng, 9000, 2, 7, cols); finish(img, 2)
        for i in range(260):       # dry twig/plant debris
            x, y = rng.uniform(0, S, 2); L = rng.uniform(20, 120); a = rng.uniform(0, np.pi)
            c = tuple(float(v) for v in np.array([0.42, 0.34, 0.24]) * rng.uniform(0.6, 1.0))
            cv2.line(img, (int(x), int(y)), (int(x + L * np.cos(a)), int(y + L * np.sin(a))), c, int(rng.integers(2, 6)), cv2.LINE_AA)
    elif name == "concrete":  # TS = 120 mm
        n1 = fbm(4); n2 = fbm(5, base=64)
        base = np.array([0.66, 0.65, 0.62]) + 0.04 * n1[..., None] + 0.035 * n2[..., None]
        img = np.clip(base, 0, 1).astype(np.float32)
        cols = [(0.55, 0.54, 0.52), (0.75, 0.74, 0.70), (0.45, 0.44, 0.43), (0.62, 0.58, 0.52)]
        grains(img, rng, 9000, 1.5, 5, cols); finish(img, 4)
        for i in range(1500):
            x, y = rng.uniform(0, S, 2); cv2.circle(img, (int(x), int(y)), int(rng.integers(1, 4)), (0.30, 0.30, 0.30), -1, cv2.LINE_AA)
    elif name == "mud":      # wet dark lake-shore mud, TS = 600 mm
        n1 = fbm(6, base=4); n2 = fbm(7, base=32)
        base = np.array([0.30, 0.25, 0.20]) + 0.025 * n1[..., None] + 0.03 * n2[..., None]
        img = np.clip(base, 0, 1).astype(np.float32)
        cols = [(0.40, 0.34, 0.27), (0.25, 0.21, 0.17), (0.48, 0.42, 0.34)]
        grains(img, rng, 4000, 1, 4, cols); finish(img, 6)
    img = np.ascontiguousarray(img, np.float32)
    np.save(p, img); return img

TS = {"sand": 60.0, "soil": 80.0, "concrete": 120.0, "mud": 600.0}
_PYR = {}
def pyr(name):
    if name not in _PYR:
        t = np.asarray(make(name)); L = [t]
        for s in (2.0, 5.0, 13.0):
            p = int(s * 4); tp = np.pad(t, ((p, p), (p, p), (0, 0)), mode="wrap")
            L.append(np.ascontiguousarray(cv2.GaussianBlur(tp, (0, 0), s)[p:-p, p:-p]))
        _PYR[name] = L
    return _PYR[name]

if __name__ == "__main__":
    import sys
    for n in sys.argv[1:]: make(n); print(n, "ok")
