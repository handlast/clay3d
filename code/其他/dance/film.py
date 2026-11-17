import math, random, sys, subprocess
from PIL import Image
from base import *
from cues import *

NAVY = (14, 14, 26); ORANGE = (255, 138, 36); ORANGE_L = (255, 196, 110); PINK = (255, 90, 170)
PURP = (130, 80, 255); LIME = (140, 240, 120); INKC = (40, 20, 10)
FLOOR = 1430

def glow(d, x, y, r, col, a, n=7):
    for i in range(n):
        k = 1 - i / n
        d.circ(x, y, r * (0.25 + 0.75 * k), fill=A(col, a * 0.15 * (1.2 - k * 0.6)))

def ik(hx, hy, fx, fy, L1, L2, bend):
    dx, dy = fx - hx, fy - hy; dist = min(math.hypot(dx, dy), L1 + L2 - 1)
    base = math.atan2(dy, dx)
    c = cl((L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist), -1, 1)
    ang = base - bend * math.acos(c)
    kx, ky = hx + L1 * math.cos(ang), hy + L1 * math.sin(ang)
    ux, uy = (fx - hx), (fy - hy); n = math.hypot(ux, uy) or 1
    if math.hypot(dx, dy) > L1 + L2 - 1: fx, fy = hx + ux / n * dist, hy + uy / n * dist
    return (kx, ky), (fx, fy)

def mode_at(t):
    if FREEZE <= t < HIT2: return "freeze"
    if 12.0 <= t < 18.0: return "pump"
    return "oj"

def pose(t):
    b = t / BEAT
    if mode_at(t) == "freeze": b = FREEZE / BEAT  # stuck on a beat-down pose
    hype = 1.25 if t >= HIT2 else 1.0
    i = math.floor(b); f = b - i; s = 1 if i % 2 == 0 else -1
    sw = -s * math.cos(math.pi * f)               # pendulum, continuous across beats
    lift = math.sin(math.pi * f)
    if mode_at(t) == "freeze": lift = 0.0; sw = 0.2
    hx = 540 - 38 * sw * hype
    hy = FLOOR - 330 + 26 * (1 - lift) - (30 * lift if t >= HIT2 else 0)
    lean = 22 * sw
    sh = (hx + lean, hy - 280)
    head = (sh[0] + lean * 0.4, sh[1] - 110 + 8 * math.sin(math.pi * 2 * f))
    J = {"hip": (hx, hy), "sh": sh, "head": head}
    # legs: the leg on side s kicks out with knee up, the other plants
    for side in (-1, 1):
        hpx = hx + side * 34
        if side == s and mode_at(t) != "freeze":
            fx = hpx + side * (60 + 120 * lift * hype); fy = FLOOR - 230 * lift * hype
            k, ft = ik(hpx, hy, fx, fy, 175, 175, -side)
        else:
            fx = 540 + side * 110 - 20 * sw; fy = FLOOR
            k, ft = ik(hpx, hy, fx, fy, 175, 175, -side * 0.6)
        J["leg%d" % side] = (k, ft)
    # arms
    m = mode_at(t)
    for side in (-1, 1):
        shx = sh[0] + side * 62; shy = sh[1] + 10
        if m == "oj":   # both arms swing together low in front, like a pendulum
            a1 = math.radians(90 - 62 * sw * hype); a2 = a1 - math.radians(38 * sw)
        elif m == "pump":  # alternate fist pumps overhead with the kick
            up = lift if side == s else 0.0
            a1 = math.radians(lerp(90 + side * 25, -90 + side * 22, up)); a2 = a1 - side * math.radians(35 * (1 - up))
        else:   # freeze: arms hanging, slightly out
            a1 = math.radians(90 - side * 12); a2 = a1
        el = (shx + 150 * math.cos(a1), shy + 150 * math.sin(a1))
        hd = (el[0] + 145 * math.cos(a2), el[1] + 145 * math.sin(a2))
        J["arm%d" % side] = ((shx, shy), el, hd)
    return J

def limb(d, pts, col, w, a=1.0):
    d.line(pts, A(col, a * 0.16), w * 2.4)   # soft glow, not an outline
    for x, y in pts: d.circ(x, y, w * 1.2, fill=A(col, a * 0.16))
    d.line(pts, A(col, a), w)
    for x, y in pts: d.circ(x, y, w / 2, fill=A(col, a))

def stick(d, t):
    J = pose(t); col = ORANGE; w = 30
    hx, hy = J["hip"]; glow(d, 540, FLOOR + 10, 260, ORANGE, 0.5 + 0.4 * pulse(t, beats(t), 6), 6)
    d.ell(540, FLOOR + 14, 220, 26, fill=A(ORANGE_L, 0.18))
    for side in (-1, 1):
        k, ft = J["leg%d" % side]; limb(d, [(hx + side * 34, hy), k, ft], col, w)
    limb(d, [(hx, hy), J["sh"]], col, w + 4)
    for side in (-1, 1): limb(d, list(J["arm%d" % side]), col, w)
    x, y = J["head"]; r = 78
    glow(d, x, y, r * 2.2, ORANGE, 0.6)
    d.circ(x, y, r, fill=A(col, 1)); d.circ(x - r * 0.35, y - r * 0.38, r * 0.22, fill=A(ORANGE_L, 0.8))
    m = mode_at(t)
    if m == "freeze":   # deadpan stare at the viewer
        for sx in (-1, 1): d.circ(x + sx * 26, y - 6, 9, fill=A(INKC, 1))
        d.line([(x - 22, y + 34), (x + 22, y + 34)], A(INKC, 1), 7)
    elif t >= HIT2:     # smug grin
        for sx in (-1, 1): d.arc(x + sx * 27, y - 2, 15, 13, 200, 340, A(INKC, 1), 7)
        d.d.chord((P(x - 34), P(y + 6), P(x + 34), P(y + 52)), 0, 180, fill=A(INKC, 1))
    else:
        for sx in (-1, 1): d.arc(x + sx * 27, y, 15, 13, 200, 340, A(INKC, 1), 7)
        d.arc(x, y + 18, 30, 22, 20, 160, A(INKC, 1), 7)

def beats(t):
    b = math.floor(t / BEAT); return [k * BEAT for k in range(max(0, b - 2), b + 1)]

def rays(d, t, c1, c2, n=16, cx=540, cy=1000, spin=0.25):
    for i in range(n):
        a0 = i / n * 2 * math.pi + t * spin; a1 = a0 + math.pi / n
        R = 2200
        d.poly([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], A(c1 if i % 2 else c2, 0.22))

def disco_floor(d, t, hues):
    bi = math.floor(t / BEAT)
    for row in range(7):
        y0 = FLOOR - 20 + row * 72; y1 = y0 + 70
        sc0 = 0.5 + row * 0.25; sc1 = sc0 + 0.25
        for c in range(-6, 6):
            x00 = 540 + c * 160 * sc0; x01 = 540 + (c + 1) * 160 * sc0
            x10 = 540 + c * 160 * sc1; x11 = 540 + (c + 1) * 160 * sc1
            on = (row * 3 + c * 7 + bi) % 4 == 0
            col = hues[(row + c + bi) % len(hues)]
            d.poly([(x00 + 4, y0 + 3), (x01 - 4, y0 + 3), (x11 - 4, y1 - 3), (x10 + 4, y1 - 3)], A(col, 0.7 if on else 0.12))

CODE = ["def dance(t):", "    knee = sin(t)    # 意义：无", "    arm = swing(t)   # 知识：0", "    return 扭()", "",
        "for 秒 in 你的时间:", "    浪费(秒)", "", "assert 有用 == False", "while True:", "    dance(t)", "# TODO: 加点知识（不加）"]

def bg(t, d):
    if t < 6.0:
        d.rect(0, 0, OW, OH, fill=A((20, 14, 40), 1))
        for k, c in ((0, ORANGE), (1, PINK)):   # two sweeping spotlights
            ang = math.sin(t * 1.3 + k * 2.4) * 0.5
            x = 540 + math.sin(ang) * 1400
            d.poly([(200 + k * 680, -20), (x - 260, FLOOR + 60), (x + 260, FLOOR + 60)], A(c, 0.12))
        disco_floor(d, t, [ORANGE, PINK, PURP, CYAN])
    elif t < 12.0:
        d.rect(0, 0, OW, OH, fill=A((30, 12, 34), 1)); rays(d, t, ORANGE, PURP, 18, spin=0.35)
        disco_floor(d, t, [ORANGE, YEL])
    elif t < 18.0:
        d.rect(0, 0, OW, OH, fill=A((8, 20, 18), 1))
        off = (t - 12.0) * 90
        for i in range(40):
            y = 260 + i * 62 - off % 62 - 0
            ln = CODE[(i + int(off // 62)) % len(CODE)]
            d.text(80, y, ln, 40, A(LIME, 0.22), anchor="lm")
        d.rect(0, FLOOR + 30, OW, OH, fill=A((20, 50, 40), 0.8))
    elif t < 24.0:
        d.rect(0, 0, OW, OH, fill=A((18, 40, 34), 1))   # chalkboard
        for j, eq in enumerate(["1 + 1 = 扭", "知识 × 0 = 0", "π = 3.14 扭"]):
            y = 270 + j * 85; d.text(540, y, eq, 52, A(WHITE, 0.35))
            k = ease(pr(t, 18.3 + j * 0.4, 18.6 + j * 0.4))
            if k > 0: d.line([(340, y), (340 + 400 * k, y)], A(RED_L, 0.85), 8)
        # knowledge progress bar stuck at 0
        k = 0.012 * max(0, math.sin(t * 5)) if t > 19 else 0
        d.text(160, 530, "知识进度", 44, A(WHITE, 0.9), anchor="lm", k=1)
        d.rect(160, 570, 760, 620, fill=A(WHITE, 0.16), r=25)
        d.rect(160, 570, 160 + max(28, 600 * k), 620, fill=A(LIME, 0.95), r=25)
        d.text(800, 595, "0%", 90, A(YEL, 1), anchor="lm", k=1)
        d.rect(0, FLOOR + 30, OW, OH, fill=A((40, 30, 24), 0.9))
    elif t < 26.0:
        d.rect(0, 0, OW, OH, fill=A((6, 6, 12), 1))
        d.poly([(470, -20), (610, -20), (900, FLOOR + 60), (180, FLOOR + 60)], A(WHITE, 0.07))
        d.ell(540, FLOOR + 30, 330, 50, fill=A(WHITE, 0.08))
    else:
        d.rect(0, 0, OW, OH, fill=A((26, 10, 30), 1)); rays(d, t, ORANGE, PINK, 22, spin=0.9)
        disco_floor(d, t, [ORANGE, PINK, YEL, CYAN, LIME])

def confetti(d, t, t0, n=90):
    rr = random.Random(3)
    for i in range(n):
        x0 = rr.uniform(0, OW); sp = rr.uniform(260, 520); ph = rr.uniform(0, 6.3); c = rr.choice([ORANGE, PINK, YEL, CYAN, LIME, PURP])
        u = t - t0 - rr.uniform(0, 4)
        if u < 0: continue
        y = -40 + (u * sp) % (OH + 80); x = x0 + 50 * math.sin(u * 3 + ph); a = u * 4 + ph
        w, h = 22 * abs(math.cos(a)) + 4, 12
        d.poly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2 + 4), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2 - 4)], A(c, 0.9))

def sparkles(d, t):
    for h in beats(t):
        u = (t - h) / 0.45
        if 0 <= u < 1 and not (FREEZE <= t < HIT2):
            rr = random.Random(int(h * 10))
            for j in range(10):
                ang = rr.uniform(0, 6.28); r = 120 + u * rr.uniform(200, 380)
                x = 540 + math.cos(ang) * r; y = FLOOR - 400 + math.sin(ang) * r * 0.8
                d.circ(x, y, 9 * (1 - u), fill=A(rr.choice([YEL, ORANGE_L, WHITE]), 1 - u))

def plus0(d, t):   # "+0 知识" pops out every 2 beats
    if FREEZE <= t < HIT2 or t < 3.0 or 6.0 <= t < 9.0 or HIT2 <= t < 29.5: return
    k = math.floor(t / (2 * BEAT)); t0 = k * 2 * BEAT; u = (t - t0) / 0.9
    if u < 1:
        J = pose(t0); x, y = J["head"]; x += (110 if k % 2 else -110)
        d.text(x, y - 90 - 120 * ease(u), "+0 知识", 48, A(YEL, 1 - u ** 2), k=1)

def bigword(t, d):
    for a, b, s, big in SUBS:
        if big and a <= t < b:
            k = back(pr(t, a, a + 0.25)); al = 1 - pr(t, b - 0.2, b)
            size = {"知识大赏": 170, "什么也不是": 150, "你气不气？": 180}[big] * (0.6 + 0.4 * k)
            col = {"知识大赏": YEL, "什么也不是": RED_L, "你气不气？": ORANGE}[big]
            jx = 6 * math.sin(t * 60) if big == "你气不气？" else 0
            glow(d, 540, 380, 360, col, 0.35 * al)
            d.text(540 + jx, 380, big, size, A(col, al), k=1)

def hud(t, d):
    if t >= 3.0 and not (18.0 <= t < 24.0):
        d.rect(50, 150, 410, 202, fill=A((255, 255, 255), 0.1), r=26)
        d.text(230, 176, f"你已浪费 {t:4.1f} 秒", 30, A(WHITE, 0.92))

def subs(t, d):
    for a, b, s, _ in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            lines = wrap(d, s, 58, 900)
            for j, ln in enumerate(lines):
                y = 1660 + (j - (len(lines) - 1) / 2) * 86; w = d.tlen(ln, 58)
                d.rect(540 - w / 2 - 24, y - 44, 540 + w / 2 + 24, y + 44, fill=A((8, 8, 18), 0.8 * al), r=16)
                d.text(540, y, ln, 58, A(WHITE, al))
            break

def brand(t, d):
    d.rect(50, 80, 300, 128, fill=A((255, 255, 255), 0.16), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(WHITE, 1))
    d.rect(760, 80, 1030, 128, fill=A(ORANGE, 0.95), r=24); d.text(895, 104, "知识含量 · 0", 26, A(NAVY, 1), k=1)

def cam(t):
    z = 1.0 + 0.018 * pulse(t, beats(t), 9)
    z += 0.1 * pulse(t, [HIT1, HIT2], 3)
    if FREEZE <= t < HIT2: z += 0.18 * eio(pr(t, FREEZE, HIT2 - 0.1))   # slow push-in on the deadpan stare
    amp = 22 * pulse(t, [HIT1, HIT2], 4) + 8 * pulse(t, [SCRATCH], 6)
    return z, 540 + amp * math.sin(t * 63), 1000 + amp * 0.6 * math.cos(t * 81)

def frame(t):
    img = Image.new("RGB", (W, H), NAVY); d = D(img)
    bg(t, d); sparkles(d, t)
    if t >= HIT2: confetti(d, t, HIT2)
    stick(d, t); plus0(d, t)
    z, cx, cy = cam(t); cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in SCENES[1:]:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.55 * (1 - (t - c) / 0.1)))
    bigword(t, d); hud(t, d); brand(t, d); subs(t, d)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))
    return img.resize((OW, OH), Image.LANCZOS)

if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.2f}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        last = None; errs = 0
        for i in range(i0, i1):
            try: last = frame(i / FPS).tobytes()
            except Exception as e: errs += 1; print('ERR', i, e, file=sys.stderr)
            if last: p.stdin.write(last)
        p.stdin.close(); p.wait(); print('errs', errs, file=sys.stderr)
