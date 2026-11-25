# Characters for 《向日葵朝最暗的灯长》: sunflower seedling (sprout), blue LED lamps, top-down stage
import math, random
from fx import *
import easing as E

STEM = (120, 200, 90); STEM_D = (70, 150, 60); LEAF = (110, 210, 80); LEAF_D = (60, 160, 60); LEAF_L = (190, 245, 150)
SEEDC = (60, 50, 40); SOIL = (110, 76, 52); SOIL_D = (80, 54, 38); POT = (220, 120, 80); POT_D = (180, 90, 60)
BLUE = (90, 160, 255); BLUE_L = (180, 215, 255); NAVYT = (22, 22, 40); GOLD = (255, 200, 60); MINT = (110, 230, 170)
NIGHT1 = (20, 26, 52); NIGHT2 = (6, 8, 20)
rr = random.Random(9)
DUST = [(rr.uniform(0, 1080), rr.uniform(0, 1920), rr.uniform(2, 5), rr.uniform(0.3, 1)) for _ in range(40)]
def room(d, t, top=NIGHT1, bot=NIGHT2):
    grad(d, top, bot)
    for x, y, r, sp in DUST:
        yy = (y + t * 20 * sp) % 1980 - 30
        d.circ(x + 10 * math.sin(t * 0.7 + y), yy, r, fill=A((200, 210, 255), 0.18 * sp))

def glow(d, x, y, r, col, a=1.0, n=7):
    for i in range(n, 0, -1):
        d.circ(x, y, r * i / n, fill=A(col, a * 0.07))

def lamp(d, x, y, s, b, t, face=True, a=1.0, mood="happy", dirx=0, diry=1):
    """blue LED bulb; b = brightness 0..1. dirx/diry = where it shines (for the face look)"""
    if b > 0: glow(d, x, y, 260 * s * (0.5 + b), BLUE, a * (0.4 + 0.6 * b))
    d.rect(x - 34 * s, y + 60 * s, x + 34 * s, y + 110 * s, fill=A((150, 160, 180), a), r=10 * s)
    for j in range(3): d.line([(x - 34 * s, y + (72 + j * 14) * s), (x + 34 * s, y + (72 + j * 14) * s)], A((110, 120, 140), a), 4 * s)
    col = mix((70, 90, 130), BLUE_L, b)
    d.circ(x, y, 74 * s, fill=A(col, a))
    d.ell(x - 26 * s, y - 28 * s, 18 * s, 12 * s, A(WHITE, 0.6 * a))
    if face:
        lx = dirx * 6 * s; ly = diry * 6 * s
        for sd in (-1, 1):
            d.ell(x + sd * 22 * s + lx, y - 4 * s + ly, 8 * s, 11 * s, A(NAVYT, a))
        mouth(d, x + lx, y + 26 * s + ly, 34 * s, {"happy": "smile", "angry": "flat", "sad": "flat", "proud": "grin", "shout": "scream"}.get(mood, "smile"), a)
        if mood == "angry":
            for sd in (-1, 1): d.line([(x + sd * 10 * s, y - 26 * s), (x + sd * 34 * s, y - 34 * s)], A(NAVYT, a), 5 * s)

def mix(c1, c2, k): return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))

def sprout(d, x, y, s, t, lean=0.0, mood="happy", a=1.0, H=300, look=0.0, sway=1.0, pot=True):
    """side-view seedling. (x,y)=soil point; lean in radians (+ = right)."""
    if pot:
        d.poly([(x - 120 * s, y - 10 * s), (x + 120 * s, y - 10 * s), (x + 90 * s, y + 150 * s), (x - 90 * s, y + 150 * s)], A(POT, a))
        d.rect(x - 135 * s, y - 30 * s, x + 135 * s, y + 10 * s, fill=A(POT_D, a), r=10 * s)
        d.ell(x, y - 26 * s, 118 * s, 16 * s, A(SOIL, a))
    lean = lean + sway * 0.03 * math.sin(t * 1.3)
    n = 14; pts = [(x, y - 20 * s)]
    for i in range(1, n + 1):
        u = i / n; ang = -math.pi / 2 + lean * u ** 1.6
        px, py = pts[-1]; L = H * s / n
        pts.append((px + math.cos(ang) * L, py + math.sin(ang) * L))
    for i in range(n):
        w = 26 * s * (1 - 0.3 * i / n)
        d.line([pts[i], pts[i + 1]], A(STEM, a), w); d.circ(pts[i + 1][0], pts[i + 1][1], w / 2, fill=A(STEM, a))
    for i in range(2, n, 3):
        d.circ(pts[i][0] + 5 * s, pts[i][1], 4 * s, fill=A(LEAF_L, 0.5 * a))
    hx, hy = pts[-1]; ang = -math.pi / 2 + lean
    # cotyledons: two leaves forming a V around the face
    for sd in (-1, 1):
        la = ang + sd * 1.05
        cx_ = hx + math.cos(la) * 90 * s; cy_ = hy + math.sin(la) * 90 * s
        leafpoly = []
        for j in range(24):
            th = j / 24 * 2 * math.pi
            ex, ey = 100 * s * math.cos(th), 44 * s * math.sin(th)
            leafpoly.append((cx_ + ex * math.cos(la) - ey * math.sin(la), cy_ + ex * math.sin(la) + ey * math.cos(la)))
        d.poly(leafpoly, A(LEAF if sd > 0 else LEAF_D, a))
        d.line([(hx, hy), (hx + math.cos(la) * 170 * s, hy + math.sin(la) * 170 * s)], A(LEAF_L, 0.5 * a), 4 * s)
    # face on round head
    fx_, fy_ = hx + math.cos(ang) * 30 * s, hy + math.sin(ang) * 30 * s
    d.circ(fx_, fy_, 56 * s, fill=A(LEAF_L, a))
    for sd in (-1, 1):
        ex = fx_ + sd * 20 * s; ey = fy_ - 6 * s
        big = mood in ("scared", "confused")
        d.ell(ex, ey, 11 * s, 14 * s, A(WHITE, a))
        d.ell(ex + look * 4 * s, ey + 2 * s, (5 if big else 7) * s, (7 if big else 9) * s, A(NAVYT, a))
    m = {"happy": "smile", "proud": "grin", "confused": "wobble", "scared": "o", "chill": "smile", "sus": "flat", "wow": "o"}.get(mood, "smile")
    mouth(d, fx_, fy_ + 24 * s, 30 * s, m, a)
    if mood == "confused":
        d.text(fx_ + 80 * s, fy_ - 90 * s, "?", int(80 * s), A(GOLD, a), k=1)
    return hx, hy

def topview(d, t, lean_ang=None, lean_len=0.0, lamps=(), cx=540, cy=900, R=330, a=1.0):
    """top-down stage: pot circle center, lamps: list of (angle_deg, brightness, label). angle 0=right, 90=up(screen)"""
    d.circ(cx, cy, R, fill=A((40, 48, 80), 0.6 * a))
    d.circ(cx, cy, R, outline=A(WHITE, 0.15 * a), w=4)
    for ang, b, lab in lamps:
        r_ = math.radians(ang); lx, ly = cx + math.cos(r_) * (R + 60), cy - math.sin(r_) * (R + 60)
        for j in range(5):
            u = ((t * 0.8 + j / 5) % 1)
            px, py = lx - math.cos(r_) * u * R * 0.8, ly + math.sin(r_) * u * R * 0.8
            d.circ(px, py, 10 * (0.5 + b), fill=A(BLUE_L, a * b * (1 - u) * 0.8))
        lamp(d, lx, ly - 30, 0.55, b, t, face=False, a=a)
    d.circ(cx, cy, 90, fill=A(POT, a)); d.circ(cx, cy, 72, fill=A(SOIL, a))
    if lean_ang is not None:
        r_ = math.radians(lean_ang); hx, hy = cx + math.cos(r_) * lean_len, cy - math.sin(r_) * lean_len
        d.line([(cx, cy), (hx, hy)], A(STEM, a), 22)
    else: hx, hy = cx, cy
    for sd in (-1, 1): d.ell(hx + sd * 50, hy, 54, 26, A(LEAF if sd > 0 else LEAF_D, a))
    d.circ(hx, hy, 30, fill=A(LEAF_L, a))
    return hx, hy
