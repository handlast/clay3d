# Characters for 《章鱼越狱三步法》: octopus (common = coral red, maya = teal-brown), acrylic box with hole
import math, random
from fx import *
import easing as E

OCT = (236, 96, 92); OCT_D = (180, 58, 66); OCT_L = (255, 160, 140); SUCK = (255, 214, 196)
MAYA = (176, 128, 96); MAYA_D = (128, 86, 64); MAYA_L = (220, 176, 140)
SEA1 = (14, 70, 110); SEA2 = (4, 24, 48); ACR = (180, 230, 255); NAVYT = (22, 22, 40); GOLD = (255, 200, 60)
CART = (240, 240, 220); MINT = (110, 230, 170); SAND = (220, 190, 130); ROCKC = (90, 100, 120)
rr = random.Random(5)
BUBS = [(rr.uniform(0, 1080), rr.uniform(0, 1920), rr.uniform(4, 10), rr.uniform(0.3, 1)) for _ in range(40)]
def sea(d, t, top=SEA1, bot=SEA2, b=1.0):
    grad(d, top, bot)
    for x, y, r, sp in BUBS:
        yy = (y - t * 60 * sp) % 1980 - 30
        d.circ(x + 8 * math.sin(t + y), yy, r, outline=A((200, 235, 255), 0.25 * b * sp), w=3)

def crom(pts, n=8):
    """catmull-rom smoothing"""
    if len(pts) < 3: return pts
    P_ = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for j in range(n):
            u = j / n; u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u3) for k in range(2)))
    out.append(pts[-1]); return out
def arm(d, pts, w0, col, colL, a=1.0, sucker=True):
    pts = crom(pts, 10); n = len(pts)
    for i in range(n - 1):
        w = w0 * (1 - 0.85 * i / n)
        d.line([pts[i], pts[i + 1]], A(col, a), w)
        d.circ(pts[i + 1][0], pts[i + 1][1], w * 0.5, fill=A(col, a))
    if sucker:
        for i in range(3, n - 4, 5):
            w = w0 * (1 - 0.85 * i / n); d.circ(pts[i][0], pts[i][1] + w * 0.25, w * 0.22, fill=A(SUCK, 0.9 * a))

def mantle(d, x, y, s, t, col=OCT, colD=OCT_D, colL=OCT_L, mood="happy", a=1.0, sqx=1.0, sqy=1.0, look=0.0, face_=True, brainvis=0.0):
    """head + mantle (mantle bulb up-left behind head). (x,y)=head center"""
    br = 1 + 0.03 * math.sin(t * 2.5)
    mx, my = x - 60 * s * sqx, y - 110 * s * sqy
    d.ell(mx, my, 120 * s * sqx * br, 140 * s * sqy * br, A(colD, a))
    d.ell(mx - 6 * s, my - 6 * s, 112 * s * sqx * br, 132 * s * sqy * br, A(col, a))
    d.ell(mx - 50 * s * sqx, my - 60 * s * sqy, 34 * s * sqx, 22 * s * sqy, A(colL, 0.7 * a))
    for j in range(4): d.circ(mx + (-40 + j * 30) * s * sqx, my + (20 + 15 * (j % 2)) * s * sqy, 9 * s, fill=A(colD, 0.6 * a))
    d.ell(x, y, 100 * s * sqx, 80 * s * sqy, A(col, a))
    if brainvis > 0:
        d.ell(x, y - 6 * s, 70 * s * sqx, 34 * s * sqy, A(CART, 0.85 * brainvis * a))
        d.ell(x, y - 6 * s, 44 * s * sqx, 20 * s * sqy, A((255, 170, 190), 0.9 * brainvis * a))
    if face_:
        # big eyes on sides
        for sd in (-1, 1):
            ex = x + sd * 58 * s * sqx; ey = y - 18 * s * sqy
            d.ell(ex, ey, 30 * s * min(1, sqx * 1.2), 32 * s * sqy, A(WHITE, a))
            big = mood in ("scared", "scream")
            d.ell(ex + look * 8 * s, ey + 2 * s, (14 if not big else 9) * s * sqx, 16 * s * sqy, A(INK, a))
            d.circ(ex + look * 8 * s - 4 * s, ey - 5 * s, 4 * s, fill=A(WHITE, a))
        m = {"happy": "grin", "proud": "grin", "scared": "o", "scream": "scream", "sus": "flat", "chill": "smile", "sad": "flat", "dizzy": "wobble"}.get(mood, "smile")
        mouth(d, x, y + 34 * s * sqy, 60 * s * min(sqx, 1.2), m, a)
        if mood == "sus":
            for sd in (-1, 1): d.line([(x + sd * 40 * s, y - 60 * s), (x + sd * 80 * s, y - 52 * s - sd * 6 * s)], A(INK, a), 6 * s)
        if mood in ("scared", "scream"): d.ell(x + 100 * s, y - 70 * s, 8 * s, 13 * s, A(CYAN, a))

def octo(d, x, y, s, t, mood="happy", col=OCT, colD=OCT_D, colL=OCT_L, a=1.0, arms_to=None, sqx=1.0, sqy=1.0, look=0.0, brainvis=0.0, curl=1.0):
    """free octopus. arms_to: optional list of 8 explicit point-lists (paths from root)"""
    roots = [(x + (-80 + i * 23) * s * sqx, y + 50 * s * sqy) for i in range(8)]
    for i in range(8):
        if arms_to and arms_to[i]: pts = [roots[i]] + arms_to[i]
        else:
            ang = math.pi / 2 + (i - 3.5) * 0.32
            pts = [roots[i]]
            for j in range(1, 6):
                aa = ang + curl * 0.25 * j * (1 if i >= 4 else -1) * (1 + 0.3 * math.sin(t * 2 + i)) + 0.15 * math.sin(t * 3 + i + j)
                L = 46 * s
                px, py = pts[-1]; pts.append((px + math.cos(aa) * L, py + math.sin(aa) * L))
        arm(d, pts, 30 * s, colD if i % 2 else col, colL, a)
    mantle(d, x, y, s, t, col, colD, colL, mood, a, sqx, sqy, look, brainvis=brainvis)

# ---------- the box rig ----------
WX = 600            # wall x
HY = 900            # hole center y
def boxrig(d, t, hole=150, a=1.0, label=None):
    """acrylic box: interior to the left of wall WX. returns (top, bot) of hole"""
    x0, y0, y1 = 120, 520, 1280
    d.rect(x0, y0, WX, y1, fill=A(ACR, 0.10 * a), r=10)
    d.rect(x0, y0, x0 + 14, y1, fill=A(ACR, 0.6 * a)); d.rect(x0, y0, WX, y0 + 14, fill=A(ACR, 0.6 * a)); d.rect(x0, y1 - 14, WX, y1, fill=A(ACR, 0.6 * a))
    ht, hb = HY - hole / 2, HY + hole / 2
    d.rect(WX - 7, y0, WX + 7, ht, fill=A(ACR, 0.75 * a)); d.rect(WX - 7, hb, WX + 7, y1, fill=A(ACR, 0.75 * a))
    d.rect(x0 + 30, y0 + 40, x0 + 46, y1 - 60, fill=A(WHITE, 0.2 * a), r=8)
    return ht, hb

def escape(d, t, s=0.85, hole=150, ext=None, body=0.0, mood="happy", col=OCT, colD=OCT_D, colL=OCT_L, brainvis=0.0, look=0.0):
    """ext: 8 values 0..1 = how far each arm is out through the hole; body 0..1 = head passage (0 inside, 1 outside)"""
    ext = ext or [0] * 8
    hx = lerp(380, 830, E.ease_in_out_sine(body))
    hy = HY + 40 * s
    near = cl(1 - abs(hx - WX) / (110 * s))
    sqy = lerp(1.0, max(0.45, hole / (190 * s)), near); sqx = lerp(1.0, 1.0 / max(sqy, 0.6), near * 0.6)
    roots = [(hx + (-80 + i * 23) * s * sqx, hy + 50 * s * sqy) for i in range(8)]
    hole_pt = lambda i: (WX, HY + (i - 3.5) * hole / 10)
    for i in range(8):
        e = ext[i]; r0 = roots[i]
        inside = r0[0] < WX
        if inside:
            if e <= 0.01:   # curled inside, near body
                ang = math.pi / 2 + (i - 3.5) * 0.32 + 0.2 * math.sin(t * 3 + i)
                pts = [r0]
                for j in range(1, 6):
                    aa = ang + 0.25 * j * (1 if i >= 4 else -1) + 0.12 * math.sin(t * 3 + i + j)
                    px, py = pts[-1]; pts.append((px + math.cos(aa) * 44 * s, py + math.sin(aa) * 44 * s))
            else:
                hp = hole_pt(i); mid = ((r0[0] + hp[0]) / 2, (r0[1] + hp[1]) / 2 + 30 * s)
                tgt = (WX + 280 * e, HY + (i - 3.5) * 60 * e + 120 * e * math.sin(t * 2 + i) * 0.3)
                pts = [r0, mid, hp, ((hp[0] + tgt[0]) / 2, (hp[1] + tgt[1]) / 2), tgt]
        else:          # body is outside: arms not yet out trail back through the hole
            if e >= 0.99:
                ang = math.pi / 2 + (i - 3.5) * 0.32
                pts = [r0]
                for j in range(1, 6):
                    aa = ang + 0.22 * j * (1 if i >= 4 else -1) + 0.12 * math.sin(t * 3 + i + j)
                    px, py = pts[-1]; pts.append((px + math.cos(aa) * 44 * s, py + math.sin(aa) * 44 * s))
            else:
                hp = hole_pt(i); tail = (WX - 200 * (1 - body) - 40, HY + (i - 3.5) * 30)
                pts = [r0, ((r0[0] + hp[0]) / 2, (r0[1] + hp[1]) / 2), hp, tail]
        arm(d, pts, 26 * s, colD if i % 2 else col, colL, 1)
    mantle(d, hx, hy, s, t, col, colD, colL, mood, 1, sqx, sqy, look, brainvis=brainvis)
    return hx, hy

def bubble(d, x, y, s_, k, a=1.0, size=40, col=WHITE, tc=NAVYT):
    if k <= 0: return
    w = d.tlen(s_, size, 1) + 40; hh = size * 0.85
    sc = min(1, k)
    d.rect(x - w / 2 * sc, y - hh * sc, x + w / 2 * sc, y + hh * sc, fill=A(col, a), r=hh * sc)
    d.poly([(x - 14, y + hh * sc - 4), (x, y + hh * sc + 24 * sc), (x + 14, y + hh * sc - 4)], A(col, a))
    if sc > 0.6: d.text(x, y, s_, int(size * sc), A(tc, a), k=1)
