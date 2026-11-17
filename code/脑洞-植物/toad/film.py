import sys, subprocess
from doodle import *
from cues import *
TOAD = (156, 128, 78); TOAD_L = (196, 168, 108); TOAD_D = (118, 94, 56); BELLY = (238, 220, 172)
SICK = (130, 180, 90); ORG = (250, 150, 40); ELY = (44, 52, 84); SPOT = (255, 210, 70); SLIME = (180, 230, 140)
STEAM = (255, 255, 255); HOTC = (255, 236, 120); PINK = (240, 120, 130); RED2 = (220, 60, 50); STOM = (236, 150, 150)

def toad(d, x, y, s, t, mood="ok", mo=0.0, bulge=0.0, sick=0.0, glowk=0.0, a=1.0):
    br = 1 + 0.02 * math.sin(t * 3)
    body = mix(TOAD, SICK, sick); lite = mix(TOAD_L, (180, 220, 140), sick); dark = mix(TOAD_D, (90, 140, 70), sick)
    d.ell(x, y + 6, s * 1.15, s * 0.16, A((60, 50, 30), 0.18 * a))
    for sx in (-1, 1):  # back legs
        d.ell(x + sx * s * 0.95, y - s * 0.25, s * 0.42, s * 0.3, A(dark, a))
        d.ell(x + sx * s * 1.15, y - s * 0.03, s * 0.32, s * 0.09, A(dark, a))
    d.ell(x, y - s * 0.55, s * 1.0 * br, s * 0.62 * br, A(body, a))
    d.ell(x - s * 0.25, y - s * 0.85, s * 0.45, s * 0.18, A(lite, 0.6 * a))
    d.ell(x, y - s * 0.3 + bulge * s * 0.05, s * (0.62 + 0.25 * bulge), s * (0.32 + 0.18 * bulge), A(BELLY, a))
    for i, (wx, wy, wr) in enumerate([(-.6, -.75, .07), (.55, -.8, .06), (-.75, -.45, .05), (.75, -.5, .07), (.3, -1.0, .05), (-.35, -1.02, .05), (.0, -.95, .04)]):
        d.circ(x + wx * s, y + wy * s, wr * s, fill=A(lite, a)); d.circ(x + wx * s - wr * s * 0.3, y + wy * s - wr * s * 0.3, wr * s * 0.35, fill=A(WHITE, 0.35 * a))
    if glowk > 0:
        glow(d, x, y - s * 0.4, s * 0.9, HOTC, glowk * a, 7); d.circ(x, y - s * 0.4, s * 0.18 * glowk, fill=A(WHITE, 0.8 * glowk * a))
    for sx in (-1, 1):  # front legs
        d.ell(x + sx * s * 0.45, y - s * 0.02, s * 0.2, s * 0.08, A(dark, a))
    for sx in (-1, 1):  # eyes
        ex, ey = x + sx * s * 0.45, y - s * 1.05
        d.circ(ex, ey, s * 0.25, fill=A(body, a)); d.circ(ex - s * 0.06, ey - s * 0.08, s * 0.08, fill=A(lite, 0.6 * a))
        if mood == "gulp":
            d.arc(ex, ey + s * 0.02, s * 0.15, s * 0.1, 200, 340, A(INK, a), s * 0.035)
        elif mood == "sick":
            for k in range(3): d.arc(ex, ey, s * (0.05 + 0.045 * k), s * (0.05 + 0.045 * k), (t * 400 + k * 90) % 360, (t * 400 + k * 90) % 360 + 250, A(INK, a), s * 0.025)
        else:
            big = 1.2 if mood == "shock" else 1.0
            d.circ(ex, ey, s * 0.17 * big, fill=A((232, 182, 58), a))
            d.ell(ex, ey, s * 0.12 * big, s * (0.05 if mood != "shock" else 0.11), A(INK, a))
            d.circ(ex - s * 0.05, ey - s * 0.06, s * 0.035, fill=A(WHITE, a))
    my = y - s * 0.62
    if mo > 0:
        d.ell(x, my + s * 0.12 * mo, s * 0.62, s * 0.3 * mo, A((120, 30, 40), a))
        d.ell(x, my + s * 0.22 * mo, s * 0.32, s * 0.12 * mo, A(PINK, a))
    else:
        if mood == "sick": d.line([(x - s * 0.6 + i * s * 0.2, my + (s * 0.04 if i % 2 else -s * 0.04)) for i in range(7)], A(INK, a), s * 0.035)
        else: d.arc(x, my - s * 0.25, s * 0.68, s * 0.3, 25, 155, A(INK, a), s * 0.035)
    if sick > 0.5:
        d.ell(x + s * 0.95, y - s * 1.1, s * 0.06, s * 0.1, A(CYAN, a))

def rot(cx, cy, ang, dx, dy):
    c, s_ = math.cos(ang), math.sin(ang); return (cx + dx * c - dy * s_, cy + dx * s_ + dy * c)
def beetle(d, x, y, s, t, ang=0.0, mood="ok", slime=0.0, walk=0.0, a=1.0):
    """top view, head points toward ang (0 = right)."""
    R = lambda dx, dy: rot(x, y, ang, dx * s, dy * s)
    for k, ox in enumerate((-0.35, 0.05, 0.4)):
        for sy in (-1, 1):
            ph = math.sin(t * 22 + k * 2 + (sy > 0) * 3) * walk * 0.15
            p0 = R(ox, sy * 0.25); p1 = R(ox + 0.15 + ph, sy * 0.6); p2 = R(ox - 0.05 + ph, sy * 0.85)
            d.line([p0, p1, p2], A((120, 70, 30), a), max(3, s * 0.07))
    for sy in (-1, 1): d.line([R(0.95, sy * 0.1), R(1.3, sy * 0.35), R(1.45, sy * 0.3)], A((120, 70, 30), a), max(2, s * 0.05))
    pts = [R(-0.95 * math.cos(u), 0.5 * math.sin(u)) for u in [i * math.pi / 20 for i in range(41)]]
    pts = [R(-0.2 + 0.75 * math.cos(u), 0.5 * math.sin(u)) for u in [i * math.pi / 20 for i in range(41)]]
    d.poly(pts, A(ELY, a))
    d.poly([R(-0.2 + 0.6 * math.cos(u), -0.18 + 0.2 * math.sin(u)) for u in [i * math.pi / 10 for i in range(21)]], A((90, 100, 150), 0.6 * a))
    for dx, dy in ((-0.5, -0.25), (-0.5, 0.25), (0.05, -0.28), (0.05, 0.28)):
        px, py = R(dx, dy); d.circ(px, py, s * 0.11, fill=A(SPOT, a))
    px, py = R(0.62, 0); d.circ(px, py, s * 0.22, fill=A(ORG, a))
    hx, hy = R(0.9, 0); d.circ(hx, hy, s * 0.22, fill=A(ORG, a)); d.circ(hx - s * 0.06, hy - s * 0.08, s * 0.07, fill=A(WHITE, 0.5 * a))
    for sy in (-1, 1):
        ex, ey = R(0.98, sy * 0.12)
        if mood == "dizzy":
            d.line([(ex - s * .06, ey - s * .06), (ex + s * .06, ey + s * .06)], A(INK, a), s * 0.03); d.line([(ex - s * .06, ey + s * .06), (ex + s * .06, ey - s * .06)], A(INK, a), s * 0.03)
        elif mood == "proud":
            d.arc(ex, ey + s * 0.03, s * 0.07, s * 0.06, 200, 340, A(INK, a), s * 0.03)
        else:
            d.circ(ex, ey, s * (0.09 if mood != "shock" else 0.11), fill=A(WHITE, a)); d.circ(ex + s * 0.02, ey, s * 0.045, fill=A(INK, a))
    if slime > 0:
        for i in range(7):
            sx_, sy_ = R(-0.6 + i * 0.25, 0.4 * math.sin(i * 2.1)); d.circ(sx_, sy_ + 6 * math.sin(t * 3 + i), s * 0.1, fill=A(SLIME, 0.55 * slime * a))
        for i in range(3):
            dx_, dy_ = R(-0.3 + i * 0.4, 0.5); dl = s * (0.2 + 0.15 * ((t * 1.5 + i * 0.3) % 1))
            d.line([(dx_, dy_), (dx_, dy_ + dl)], A(SLIME, 0.7 * slime * a), s * 0.06)
def spray(d, x, y, ang, L, t, k=1.0):
    if k <= 0: return
    ex, ey = x + math.cos(ang) * L, y + math.sin(ang) * L
    for i in range(9):
        u = i / 8; px, py = lerp(x, ex, u), lerp(y, ey, u)
        glow(d, px, py, 40 + 90 * u, HOTC, 0.4 * k, 4)
    d.line([(x, y), (ex, ey)], A(HOTC, k), 22); d.line([(x, y), (ex, ey)], A(WHITE, k), 8)
    for i in range(8):
        u = ((t * 2 + i / 8) % 1); px = ex + math.cos(ang + (i - 4) * 0.25) * 140 * u; py = ey + math.sin(ang + (i - 4) * 0.25) * 140 * u - 120 * u
        d.circ(px, py, 20 + 50 * u, fill=A(STEAM, 0.5 * k * (1 - u)))

def bang_txt(d, t, t0, x, y, s="砰！", size=150, col=RED2, life=0.8):
    if not (t0 <= t < t0 + life): return
    k = back(pr(t, t0, t0 + 0.15)); fade = 1 - pr(t, t0 + life - 0.3, t0 + life)
    glow(d, x, y, size * 1.5 * k, HOTC, 0.8 * fade, 6)
    for i in range(12):
        an = i * math.pi / 6 + 0.2; r0, r1 = size * 0.7 * k, size * (1.1 + 0.2 * (i % 2)) * k
        d.line([(x + math.cos(an) * r0, y + math.sin(an) * r0), (x + math.cos(an) * r1, y + math.sin(an) * r1)], A(ORG, fade), 10)
    d.text(x, y, s, int(size * (0.5 + 0.5 * k)) + 1, A(col, fade), k=1)

def ground(d, t):
    paper(d, t)
    d.ell(540, 1460, 620, 70, A((170, 200, 130), 0.5))
    for i in range(9):
        gx = 140 + i * 100; ink(d, [(gx, 1470), (gx + 10, 1420)], t, (90, 150, 80), 7, 0.8, 500 + i)

def tongue(d, x0, y0, x1, y1, u, w=34):
    if u <= 0: return
    ex, ey = lerp(x0, x1, u), lerp(y0, y1, u)
    d.line([(x0, y0), (ex, ey)], A(PINK, 1), w); d.circ(ex, ey, w * 0.9, fill=A(PINK, 1))

def s_hook(t, d):
    ground(d, t)
    tx, ty, ts = 540, 1450, 330
    out = pr(t, HOOK_HIT - 0.1, HOOK_HIT + 0.05) * (1 - pr(t, HOOK_HIT + 0.15, GULP - 0.1))
    gulp = GULP <= t < BANG0
    mood = "gulp" if gulp else ("shock" if t >= BANG0 else "ok")
    bump = math.exp(-max(0, t - BANG0) * 3) if t >= BANG0 else 0
    toad(d, tx, ty + 8 * math.sin(t * 50) * bump, ts, t, mood, mo=out * 0.6, bulge=0.3 if t > GULP else 0, glowk=pulse(t, [BANG0, BANG0 + 0.45], 4))
    if t < HOOK_HIT + 0.15:
        bx, by = 760, 940
        beetle(d, bx, by, 90, t, ang=math.pi * 1.0, walk=1.0, mood="ok")
    else:
        u = out; bx, by = lerp(540, 760, u), lerp(1250, 940, u)
        tongue(d, 540, 1250, 760, 940, u)
        if t < GULP - 0.05: beetle(d, bx, by, 90, t, ang=math.pi, mood="shock")
    bang_txt(d, t, BANG0, 540, 1180, "砰！", 170)
    bang_txt(d, t, BANG0 + 0.45, 640, 1120, "砰！", 120)
    dtext(d, 540, 320, "如果被吞进肚子", 112, INKC, 1, t, 1)
    k = pop(t, BANG0 + 0.2)
    if k > 0: d.text(540, 500, "还能活着出来？", int(110 * (0.6 + 0.4 * k)) + 1, A(RED2, min(1, k * 1.5)), k=1)

def s_who(t, d):
    paper(d, t)
    for i in range(14):  # warm rays
        an = t * 0.3 + i * math.pi / 7; d.poly([(540, 1050), (540 + math.cos(an) * 1400, 1050 + math.sin(an) * 1400), (540 + math.cos(an + 0.12) * 1400, 1050 + math.sin(an + 0.12) * 1400)], A((255, 220, 140), 0.25))
    k = pop(t, WHO_HIT)
    if t < MIX:
        s_ = 230 * max(0.01, k)
        beetle(d, 540, 1050, s_, t, ang=-math.pi / 2, mood="proud")
        dtext(d, 540, 330, "屁步甲", 140, INKC, min(1, k * 1.5), t, 3)
        dtext(d, 540, 500, "Bombardier beetle", 56, (150, 100, 40), min(1, k * 1.5), t, 4)
        if t > WHO_HIT + 0.6:
            dtext(d, 540, 1440, "屁股 = 炮台", 72, RED2, ease(pr(t, WHO_HIT + 0.6, WHO_HIT + 0.9)), t, 5)
    else:
        # cutaway of chemical chamber
        u = pr(t, MIX, MIX_HIT)
        for j, (nm, col, x0) in enumerate((("对苯二酚", (120, 200, 240), 260), ("过氧化氢", (180, 240, 160), 820))):
            box(d, x0 - 140, 820, x0 + 140, 1120, t, INKC, 8, 1, 700 + j, fill=mix(WHITE, col, 0.4))
            lvl = 1 - u * 0.8 if t < MIX_HIT else 0.2
            d.rect(x0 - 128, 1108 - 270 * lvl, x0 + 128, 1108, fill=A(col, 1), r=10)
            dtext(d, x0, 760, nm, 52, INKC, 1, t, 710 + j)
            if t < MIX_HIT:
                for b in range(5):
                    by = 1100 - ((t * 1.5 + b * 0.2) % 1) * 280 * lvl
                    d.circ(x0 + (b - 2) * 40, by, 10, fill=A(WHITE, 0.6))
                fx_ = lerp(x0, 540, u); d.circ(fx_, 1250, 30, fill=A(col, 0.9))
        ring(d, 540, 1300, 120, t, INKC, 9, 1, 720, fill=(250, 220, 200))
        dtext(d, 540, 1300, "反应室", 40, INKC, 1, t, 721)
        bang_txt(d, t, MIX_HIT, 540, 1300, "炸！", 200, RED2, 1.4)
        dtext(d, 540, 400, "A + B = 爆炸", 100, INKC, 1, t, 722)

def thermo(d, t, x, y, k):
    d.rect(x - 34, y - 420, x + 34, y + 20, fill=A(WHITE, 1), r=34); d.circ(x, y + 60, 70, fill=A(WHITE, 1))
    d.circ(x, y + 60, 54, fill=A(RED2, 1)); d.rect(x - 18, y - 400 * k, x + 18, y + 40, fill=A(RED2, 1), r=18)
    for j in range(6): d.line([(x + 40, y - j * 75), (x + 70, y - j * 75)], A(INKC, 0.7), 5)

def s_spray(t, d):
    paper(d, t)
    if t < LAB:
        bx, by = 300, 1150
        beetle(d, bx, by, 150, t, ang=math.pi, mood="proud" if t > SPRAY_HIT else "ok")
        k = pr(t, SPRAY_HIT - 0.1, SPRAY_HIT) * (1 - pr(t, SPRAY_HIT + 1.6, SPRAY_HIT + 2.0))
        spray(d, bx + 150, by, -0.15 + 0.08 * math.sin(t * 9), 520, t, k)
        kk = pr(t, SPRAY_HIT, SPRAY_HIT + 0.9)
        thermo(d, t, 880, 1000, ease(kk))
        n = int(100 * ease(kk))
        if t > SPRAY_HIT: d.text(560, 480, f"近 {n}°C", int(220 * (0.6 + 0.4 * pop(t, SPRAY_HIT))) + 1, A(RED2, 1), k=1)
        dtext(d, 560, 300, "喷出来的毒液", 76, INKC, 1, t, 30)
    else:
        # lab: Kobe 2018
        d.rect(0, 0, OW, OH, fill=A((230, 240, 250), 0.6))
        box(d, 160, 900, 920, 1450, t, (120, 160, 200), 10, 1, 800, fill=(220, 236, 248))
        d.rect(172, 1300, 908, 1438, fill=A((190, 170, 120), 1))
        toad(d, 400, 1330, 150, t, "ok"); toad(d, 720, 1330, 120, t, "ok", a=1)
        k = pop(t, LAB_HIT)
        dtext(d, 540, 330, "2018 · 日本神户大学", 76, INKC, min(1, k * 1.5), t, 31)
        dtext(d, 540, 480, "把它喂给蟾蜍", 96, RED2, min(1, k * 1.5), t, 32)
        dtext(d, 400, 1500, "日本蟾蜍", 40, INKC, 1, t, 33); dtext(d, 720, 1500, "溪流蟾蜍", 40, INKC, 1, t, 34)
        if t > LAB_HIT + 0.8:
            bxx = 540 + 50 * math.sin(t * 2); beetle(d, bxx, 820 + (t - LAB_HIT) * 40, 60, t, ang=math.pi / 2, mood="shock")

def s_swal(t, d):
    ground(d, t)
    tx, ty, ts = 540, 1450, 360
    out = pr(t, SWAL_HIT - 0.1, SWAL_HIT + 0.05) * (1 - pr(t, SWAL_HIT + 0.2, SWAL_HIT + 0.5))
    gul = SWAL_HIT + 0.5 <= t
    toad(d, tx, ty, ts, t, "gulp" if SWAL_HIT + 0.5 <= t < SWAL_HIT + 1.3 else "ok", mo=out * 0.6, bulge=0.3 if gul else 0)
    if t < SWAL_HIT: beetle(d, 540, 900, 80, t, ang=-math.pi / 2, walk=1)
    elif t < SWAL_HIT + 0.5:
        u = out; tongue(d, 540, 1230, 540, 900, u); beetle(d, 540, lerp(1230, 900, u), 80, t, ang=-math.pi / 2, mood="shock")
    k = pop(t, SWAL_HIT + 0.5)
    if k > 0: d.text(540, 420, "咕咚", int(200 * (0.6 + 0.4 * k)) + 1, A(INKC, min(1, k * 1.5)), k=1)
    if t > SWAL_HIT + 1.3: dtext(d, 540, 600, "100% 一口吞", 76, RED2, ease(pr(t, SWAL_HIT + 1.3, SWAL_HIT + 1.6)), t, 40)

def s_inside(t, d):
    d.rect(0, 0, OW, OH, fill=A((60, 30, 40), 1))
    for i in range(10):  # stomach folds
        d.arc(540, 1050, 520 - i * 18, 620 - i * 22, 0, 360, A((170, 70, 80), 0.25), 14)
    d.ell(540, 1050, 420, 520, A(STOM, 1)); d.ell(540, 1150, 380, 300, A((210, 230, 120), 0.35))
    for i in range(8):
        u = (t * 0.4 + i / 8) % 1; d.circ(300 + i * 70, 1300 - u * 400, 10 + i % 3 * 5, fill=A((230, 255, 160), 0.5 * (1 - u)))
    p = pulse(t, BANGS, 6)
    bx, by = 540 + 20 * math.sin(t * 9) * p, 1080
    beetle(d, bx, by, 150, t, ang=-math.pi / 2, mood="ok" if p < 0.3 else "proud", slime=0.6)
    for b in BANGS:
        k = pr(t, b, b + 0.05) * (1 - pr(t, b + 0.35, b + 0.55)); spray(d, bx, by + 150, math.pi / 2 + (BANGS.index(b) - 1) * 0.5, 300, t, k)
    for j, b in enumerate(BANGS): bang_txt(d, t, b, [380, 720, 540][j], [700, 760, 640][j], "砰！", 120 + j * 25)
    dtext(d, 540, 300, "胃里开炮", 110, (255, 230, 120), 1, t, 50)
    if p > 0: d.rect(0, 0, OW, OH, fill=A(HOTC, 0.25 * p))

def s_vomit(t, d):
    ground(d, t)
    tx, ty, ts = 540, 1450, 360
    pre = t < VOMIT_HIT
    if pre:
        sick = pr(t, VOMIT, VOMIT_HIT)
        toad(d, tx + 10 * math.sin(t * 40) * sick, ty, ts, t, "sick", bulge=0.3 + 0.2 * math.sin(t * 20), sick=sick)
    else:
        u = pr(t, VOMIT_HIT, VOMIT_HIT + 0.3)
        toad(d, tx, ty, ts, t, "sick", mo=1.0 * (1 - pr(t, VOMIT_HIT + 1.5, VOMIT_HIT + 2.0)), sick=1 - pr(t, VOMIT_HIT + 1, VOMIT_HIT + 3))
        if t < VOMIT_HIT + 1.5:  # everted stomach pouch
            d.ell(tx, ty - ts * 0.45, ts * 0.32 * u, ts * 0.22 * u, A(STOM, 1))
        fl = pr(t, VOMIT_HIT, VOMIT_HIT + 0.8)
        bx = lerp(540, 820, fl); by = lerp(1230, 1380, fl) - math.sin(fl * math.pi) * 420
        beetle(d, bx, by, 95, t, ang=fl * 7 if fl < 1 else 0.2, mood="dizzy" if t < VOMIT_HIT + 1.6 else "proud", slime=1.0, walk=1.0 if t > VOMIT_HIT + 1.6 else 0)
        for i in range(12):
            sx_ = 540 + (i - 6) * 40 * fl * 3; sy_ = 1230 - math.sin(fl * math.pi) * 300 * ((i % 4) / 4 + 0.5) + fl * 100
            if fl < 1: d.circ(sx_, sy_, 16, fill=A(SLIME, 0.7 * (1 - fl)))
        k = pop(t, VOMIT_HIT)
        d.text(540, 440, "呕！", int(260 * (0.6 + 0.4 * k)) + 1, A((90, 170, 70), min(1, k * 1.5)), k=1)

def s_stat(t, d):
    paper(d, t)
    n = int(43 * ease(pr(t, STAT_HIT, STAT_HIT + 1.6)))
    for i in range(100):
        r_, c_ = divmod(i, 10); x = 225 + c_ * 70; y = 780 + r_ * 70
        on = i < n
        col = (100, 180, 80) if on else (200, 185, 150)
        d.ell(x, y, 26, 20, A(col, 1)); d.circ(x - 10, y - 16, 8, fill=A(col, 1)); d.circ(x + 10, y - 16, 8, fill=A(col, 1))
        d.circ(x - 10, y - 17, 3.5, fill=A(INK, 1)); d.circ(x + 10, y - 17, 3.5, fill=A(INK, 1))
        if on: d.ell(x, y + 6, 8, 6 * (1 + 0.3 * math.sin(t * 10 + i)), A((120, 30, 40), 1))
    k = pop(t, STAT_HIT)
    d.text(540, 430, f"{n}%", int(260 * (0.6 + 0.4 * k)) + 1, A((80, 160, 60), 1), k=1)
    dtext(d, 540, 600, "的蟾蜍吐了", 70, INKC, 1, t, 60)

def s_clock(t, d):
    paper(d, t)
    m = 107 * ease(pr(t, CLOCK + 0.3, CLOCK_HIT))
    cx, cy, r = 540, 1080, 300
    d.circ(cx, cy, r + 20, fill=A((90, 120, 180), 1)); d.circ(cx, cy, r, fill=A(WHITE, 1))
    d.d.pieslice((P(cx - r), P(cy - r), P(cx + r), P(cy + r)), -90, -90 + 360 * (m / 120), fill=A(STOM, 0.8))
    for j in range(12):
        an = j * math.pi / 6; d.line([(cx + math.cos(an) * r * 0.85, cy + math.sin(an) * r * 0.85), (cx + math.cos(an) * r * 0.95, cy + math.sin(an) * r * 0.95)], A(INKC, 1), 8)
    an = -math.pi / 2 + 2 * math.pi * m / 60; d.line([(cx, cy), (cx + math.cos(an) * r * 0.8, cy + math.sin(an) * r * 0.8)], A(RED2, 1), 12)
    d.circ(cx, cy, 18, fill=A(INKC, 1))
    beetle(d, cx, cy + 150, 70, t, ang=-math.pi / 2, mood="ok", slime=0.8)
    k = pop(t, CLOCK_HIT)
    d.text(540, 440, f"{int(m)} 分钟", int(190 * (0.7 + 0.3 * max(k, 0.0 if t < CLOCK_HIT else 1))) + 1, A(RED2 if t >= CLOCK_HIT else INKC, 1), k=1)
    dtext(d, 540, 280, "泡在胃酸里", 70, INKC, 1, t, 70)
    dtext(d, 540, 1520, "最快 12 分钟就被吐出", 50, INKC, 0.85, t, 71)

def s_alive(t, d):
    ground(d, t)
    if t < 33.0:
        x = lerp(200, 860, pr(t, ALIVE, 33.0))
        beetle(d, x, 1300, 110, t, ang=0, mood="proud", slime=1 - pr(t, ALIVE, 32.5), walk=1)
        k = pop(t, ALIVE_HIT)
        d.text(540, 460, "全都活着", int(170 * (0.6 + 0.4 * k)) + 1, A((80, 160, 60), min(1, k * 1.5)), k=1)
        dtext(d, 540, 700, "16 / 16", 90, INKC, ease(pr(t, ALIVE_HIT + 0.5, ALIVE_HIT + 0.8)), t, 80)
        for j in range(16):
            dtext(d, 230 + (j % 8) * 88, 880 + (j // 8) * 90, "✓" if False else "活", 52, (80, 160, 60), ease(pr(t, ALIVE_HIT + 0.6 + j * 0.06, ALIVE_HIT + 0.8 + j * 0.06)), t, 81 + j)
    else:
        n = int(562 * ease(pr(t, OLD_HIT - 0.2, OLD_HIT + 1.0)))
        beetle(d, 540, 1200, 160, t, ang=-math.pi / 2, mood="proud")
        # tiny party hat + cake candles
        d.poly([(540, 920), (500, 1010), (580, 1010)], A((240, 90, 120), 1)); d.circ(540, 915, 14, fill=A(SPOT, 1))
        k = pop(t, OLD_HIT)
        d.text(540, 480, f"+{n} 天", int(200 * (0.6 + 0.4 * k)) + 1, A(RED2, 1), k=1)
        dtext(d, 540, 300, "最长寿的那只", 70, INKC, 1, t, 99)
        for i in range(18):
            u = ((t - OLD_HIT) * 0.6 + i / 18) % 1
            if t > OLD_HIT: d.rect(80 + (i * 61) % 920, 700 + u * 900, 80 + (i * 61) % 920 + 18, 700 + u * 900 + 30, fill=A([RED2, SPOT, CYAN, (120, 200, 90)][i % 4], 1 - u))

def s_ctrl(t, d):
    paper(d, t)
    for j, (x0, armed) in enumerate(((290, True), (790, False))):
        box(d, x0 - 210, 760, x0 + 210, 1480, t, INKC, 8, 1, 900 + j, fill=(255, 250, 240) if armed else (238, 232, 222))
        dtext(d, x0, 830, "带炮弹" if armed else "炮弹耗光", 54, (80, 160, 60) if armed else RED2, 1, t, 905 + j)
        # tank gauge
        lvl = 1 if armed else 0.05
        d.rect(x0 - 110, 900, x0 + 110, 960, fill=A((220, 215, 200), 1), r=20); d.rect(x0 - 110, 900, x0 - 110 + 220 * lvl, 960, fill=A(HOTC if armed else RED2, 1), r=20)
        al = 1 if armed else 1 - pr(t, CTRL_HIT + 0.6, CTRL_HIT + 1.8)
        beetle(d, x0, 1200, 90, t, ang=-math.pi / 2, mood="proud" if armed else "shock", a=al, slime=0.3)
        if not armed and t > CTRL_HIT + 0.6:
            for i in range(10):
                u = pr(t, CTRL_HIT + 0.6 + i * 0.05, CTRL_HIT + 2.2); d.circ(x0 + (i - 5) * 18, 1200 + u * 150, 10 * (1 - u) + 1, fill=A((210, 230, 120), 0.8 * (1 - u)))
        d.text(x0, 1400, "多数逃出" if armed else "约 5% 吐出", 50, A(INKC, ease(pr(t, CTRL_HIT + 1.0, CTRL_HIT + 1.3))), k=1)
    k = pop(t, CTRL_HIT)
    d.text(540, 440, "炮弹 = 门票", int(150 * (0.6 + 0.4 * k)) + 1, A(INKC, min(1, k * 1.5)), k=1)

def s_size(t, d):
    ground(d, t)
    k = pop(t, SIZE_HIT)
    toad(d, 300, 1420, 170, t, "sick" if t > SIZE_HIT + 1.0 else "ok", sick=pr(t, SIZE_HIT + 0.8, SIZE_HIT + 1.6))
    beetle(d, 300, 1120, 90, t, ang=-math.pi / 2, mood="proud")
    toad(d, 780, 1440, 300, t, "ok")
    beetle(d, 780, 980, 45, t, ang=-math.pi / 2, mood="shock")
    d.text(540, 380, "大小很关键", int(140 * (0.6 + 0.4 * k)) + 1, A(INKC, min(1, k * 1.5)), k=1)
    dtext(d, 300, 1530, "小蟾蜍 + 大甲虫 = 吐", 40, (80, 160, 60), ease(pr(t, SIZE_HIT + 1.2, SIZE_HIT + 1.5)), t, 1001)
    dtext(d, 780, 1530, "大蟾蜍 + 小甲虫 = 难", 40, RED2, ease(pr(t, SIZE_HIT + 2.0, SIZE_HIT + 2.3)), t, 1002)

def bubble(d, x, y, s, side, col, tcol, a, size=50):
    w = d.tlen(s, size) + 70; x0 = x - w if side > 0 else x
    d.rect(x0, y - size * 1.1, x0 + w, y + size * 1.1, fill=A(col, a), r=40); d.text(x0 + w / 2, y, s, size, A(tcol, a), k=1)
def s_end(t, d):
    paper(d, t)
    d.rect(0, 160, 1080, 260, fill=A(INKC, 1)); d.text(540, 210, "同学群（48）", 44, A(WHITE, 0.95), k=1)
    d.text(540, 380, "明天这样说 ↓", 80, A(RED2, ease(pr(t, OUTRO, OUTRO + 0.3))), k=1)
    G = ((120, 220, 120), (20, 40, 20))
    if t > BUB1: bubble(d, 1010, 620, "有种虫被蟾蜍吞了还能出来", 1, *G, min(1, pop(t, BUB1)), 50)
    if t > BUB1 + 0.6: bubble(d, 1010, 800, "在胃里放了个近 100 度的炮", 1, *G, min(1, pop(t, BUB1 + 0.6)), 50)
    if t > BUB2: bubble(d, 70, 990, "那我被吞了咋办", -1, (90, 100, 130), WHITE, min(1, pop(t, BUB2)), 54)
    if t > BUB2 + 0.7: bubble(d, 1010, 1170, "先确认你是屁步甲", 1, *G, min(1, pop(t, BUB2 + 0.7)), 54)
    if t > BUB2 + 0.7: beetle(d, 540, 1420, 100, t, ang=-math.pi / 2, mood="proud")
    d.text(540, 1780, "Sugiura & Sato 2018, Biology Letters 14:20170647", 26, A(INKC, 0.75), k=0)
    d.text(540, 1815, "Aneshansley et al. 1969, Science 165:61", 26, A(INKC, 0.75), k=0)
    if t > DUR - 0.4: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.4, DUR)))

def brand2(t, d):
    d.rect(50, 80, 300, 128, fill=A(INKC, 0.95), r=24); d.text(175, 104, "Vibe 知识大赏", 26, A(WHITE, 1))
    d.rect(740, 80, 1030, 128, fill=A((240, 170, 40), 1), r=24); d.text(885, 104, "脑洞系列 · 如果", 26, A(INKC, 1))

SECS = [(0, HOOK_END, s_hook), (WHO, SPRAY, s_who), (SPRAY, SWAL, s_spray), (SWAL, INSIDE, s_swal), (INSIDE, VOMIT, s_inside), (VOMIT, STAT, s_vomit),
        (STAT, CLOCK, s_stat), (CLOCK, ALIVE, s_clock), (ALIVE, CTRL, s_alive), (CTRL, SIZE, s_ctrl), (SIZE, OUTRO, s_size), (OUTRO, 99, s_end)]
CUTS = [HOOK_END, MIX, SPRAY, LAB, SWAL, INSIDE, VOMIT, STAT, CLOCK, ALIVE, 33.0, CTRL, SIZE, OUTRO]
def cam(t):
    z = 1.0 + 0.07 * pulse(t, HITS, 7)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    amp = 26 * pulse(t, [BANG0, VOMIT_HIT, MIX_HIT] + BANGS, 4) + 8 * pulse(t, HITS, 6)
    sx, sy = shake(t, amp, 61)
    return z, 540 + sx, 960 + sy
def frame(t):
    img = Image.new("RGB", (W, H), PAPER); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.08: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.5 * (1 - (t - c) / 0.08)))
    if SILENCES[0][0] <= t < SILENCES[0][1]: d.rect(0, 0, OW, OH, fill=A((40, 50, 90), 0.45))
    brand2(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"test_{float(ts):05.1f}.png")
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
