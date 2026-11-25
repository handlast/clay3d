import sys, subprocess
from chars import *
from cues import *

def ground(d, y, col=SAND, col2=SAND_D):
    d.rect(-50, y, OW + 50, OH + 50, fill=A(col, 1)); d.rect(-50, y, OW + 50, y + 18, fill=A(col2, 0.5))
    for i in range(14):
        xx = (i * 157) % 1100; yy = y + 60 + (i * 89) % 600
        d.ell(xx, yy, 40 + i % 3 * 20, 6, A(col2, 0.5))
def dustpuff(d, x, y, t, t0, s=1.0, col=(240, 222, 180)):
    u = t - t0
    if u < 0 or u > 0.8: return
    for i in range(7):
        ang = math.pi + i * math.pi / 6; rr = 40 * s + u * 260 * s
        d.circ(x + math.cos(ang) * rr, y + math.sin(ang) * rr * 0.35, 40 * s * (1 - u / 0.8) + 8, fill=A(col, 0.8 * (1 - u / 0.8)))
def bigtxt(d, t, t0, s, y, size, col, a=1.0): stamp(d, t, t0, s, 540, y, size, col, a)
def hearts_up(d, t, t0, x, y, n=4, a=1.0):
    u = t - t0
    if u < 0 or u > 1.6: return
    for i in range(n):
        heart(d, x + (i - n / 2) * 50 + 20 * math.sin(t * 4 + i), y - u * 220 - i * 30, 22 + 6 * (i % 2), PINK, a * (1 - u / 1.6))

def desert_bg(d, top, bot, gy, t, mtn=True, pyr=True, pyc=(PYR, PYR_D)):
    grad(d, top, bot)
    if mtn:
        mountain(d, 240, gy, 520, 380, col=mix((150, 160, 186), top, 0.35)); mountain(d, 880, gy, 620, 460, col=mix((150, 160, 186), top, 0.35))
    if pyr:
        pyramid(d, 330, gy + 10, 420, 300, lit=pyc[0], sh=pyc[1]); pyramid(d, 740, gy + 10, 560, 400, lit=pyc[0], sh=pyc[1])
    ground(d, gy)

# ---------------- scenes ----------------
def hook_shot(d, t, t0, night=False):
    """statue lasers the UFO in front of the moon. Used for the hook (t0=0.4) and the callback (t0=20.0)."""
    if night:
        grad(d, (40, 30, 70), (230, 120, 70))
        if t >= t0: rays(d, t, (255, 140, 60), (200, 70, 50), n=20, cx=420, cy=700)
    else:
        grad(d, (252, 236, 196), (234, 200, 146))
        if t >= t0: rays(d, t, (255, 226, 160), (246, 206, 140), n=20, cx=400, cy=700)
    moon(d, 400, 700, 280, 1)
    desert_bg_lite(d, 1130, night)
    hx = 830; hy = 720 if not night else lerp(880, 720, ease(pr(t, t0 - 0.6, t0 + 0.15)))
    statue(d, hx, hy, 150, t, eo=1, eglow=0.4 + 0.6 * (t >= t0) if t < t0 + 1.2 else 0.5, mood="angry")
    if night: d.rect(-50, 1180, OW + 50, OH, fill=A((200, 150, 110), 1))
    ux = lerp(-220, 400, ease(pr(t, -0.2 if not night else t0 - 1.0, t0))) if t < t0 else 400
    if t < t0 + 0.12: ufo(d, ux, 660 + 8 * math.sin(t * 7), 130, t, face=True)
    if not night:
        for i, (bx, by, bs) in enumerate(((180, 330, 46), (930, 300, 40))): ufo(d, bx + 10 * math.sin(t * 2 + i), by, bs, t)
    if t >= t0: laser(d, hx - 28, hy - 27, 400, 660, t, a=1 - pr(t, t0 + 0.9, t0 + 1.3), k=ease(pr(t, t0, t0 + 0.06)))
    explosion(d, 400, 660, t, t0 + 0.05, 170)
def desert_bg_lite(d, gy, night):
    mc = (150, 140, 170) if night else (190, 186, 196); pc = ((200, 140, 90), (150, 96, 70)) if night else (PYR, PYR_D)
    mountain(d, 180, gy, 460, 330, col=mc); mountain(d, 600, gy, 520, 300, col=mc)
    pyramid(d, 300, gy + 10, 380, 260, lit=pc[0], sh=pc[1]); pyramid(d, 560, gy + 10, 460, 340, lit=pc[0], sh=pc[1])
    ground(d, gy, (226, 180, 120) if night else SAND)

def s_hook(t, d):
    hook_shot(d, t, HOOK_HIT)
    if t < HOOK_HIT:
        d.text(540, 330, "滋——", int(110 + 60 * pr(t, -0.2, HOOK_HIT)), A(LAZ, 1), k=1)
    else:
        bigtxt(d, t, HOOK_HIT, "历史课", 290, 150, (220, 56, 40))
        bigtxt(d, t, HOOK_HIT + 0.08, "没讲的一天", 435, 120, NAVYT)
    if t >= CLOCK_IN:   # rewind clock slides in during the tape stop
        u = ease(pr(t, CLOCK_IN, CLOCK_IN + 0.18)); cx = lerp(1400, 540, u)
        d.rect(0, 0, OW, OH, fill=A((30, 50, 120), 0.35 * u))
        clock(d, cx, 860, 230, t * 3, spin=-14)
        tag(d, cx, 1150, "倒回 3 小时前", (240, 110, 70), u, 56, WHITE)

def s_rewind(t, d):
    grad(d, (16, 30, 90), (40, 100, 210))
    for i in range(16):  # rewind streaks
        yy = (i * 131 - t * 2600) % 2100 - 100; d.rect(-50, yy, OW + 50, yy + 10 + i % 3 * 6, fill=A((160, 220, 255), 0.18))
    portal(d, 540, 700, 330, t)
    ground(d, 1150, (120, 150, 210), (90, 120, 190))
    clock(d, 870, 330, 70, t * 3, spin=-14, a=0.9)
    rew_icon(d, 300, 300, 50, (255, 230, 120)); tag(d, 520, 300, "3 小时前", (255, 230, 120), 1, 52)
    if t >= POD:
        u = pr(t, POD, POD_LAND); s_ = lerp(30, 150, ease(u)); y = lerp(700, 1040, u * u)
        if t >= POD_LAND: s_ = 150 * (1 + 0.1 * math.exp(-(t - POD_LAND) * 10) * math.sin((t - POD_LAND) * 40)); y = 1040
        capsule(d, 540, y, s_, door=ease(pr(t, DOOR_OPEN, DOOR_OPEN + 0.25)), eyes=1 if t >= DOOR_OPEN else 0, flame=0.0)
        dustpuff(d, 540, 1120, t, POD_LAND, 1.2, (170, 200, 240))
    if t >= STEP:
        for i, sd in enumerate((-1, 1)):
            k = ease(pr(t, STEP + i * 0.12, STEP + i * 0.12 + 0.35)); x = lerp(600, 540 + sd * 170, k); y = lerp(1000, 880, k) - math.sin(k * math.pi) * 120
            hold = t >= HANDS
            hand = (540 + sd * 70, 880 + 1.75 * 66) if hold else None
            alien(d, x, y, 66, t, mood="love" if hold else "chill", handL=hand if sd > 0 else None, handR=hand if sd < 0 else None, sq=0.03 * math.sin(t * 6))
        if t >= HANDS: heart(d, 540, 940 - 40 * ease(pr(t, HANDS, HANDS + 0.3)), 40 * popk(t, HANDS), PINK)

def couple(d, x, y, s, t, mood="happy", walk=0.0, gap=1.55, stick=0.0, flag_=False, stick_a=1.0):
    xl, xr = x - gap * s, x + gap * s
    mid = (x, y + 1.85 * s)
    hr = (xr + 0.9 * s + stick * 0.8 * s, y + 1.1 * s - stick * 1.6 * s) if stick > 0 else None
    alien(d, xl, y + math.sin(walk * 6.28) * 0.05 * s, s, t, mood, handR=mid, walk=walk)
    alien(d, xr, y + math.sin(walk * 6.28 + 2) * 0.05 * s, s, t, mood, handL=mid, handR=hr, walk=walk + 0.5)
    if stick > 0 and stick_a > 0:
        tx, ty = hr[0] + 0.9 * s * stick, hr[1] - 2.6 * s * stick
        d.line([hr, (tx, ty)], A((210, 210, 220), stick_a), 0.06 * s); phone(d, tx, ty, 0.35 * s, stick_a)
        return tx, ty
    return None

def s_date(t, d):
    desert_bg(d, (255, 214, 120), (246, 170, 80), 1080, t)
    glow(d, 240, 420, 200, (255, 250, 200), 0.9); d.circ(240, 420, 90, fill=A((255, 248, 210), 1))
    wk = pr(t, DATE, POSE); x = lerp(300, 520, ease(wk))
    st = ease(pr(t, POSE, POSE + 0.3))
    couple(d, x, 860, 70, t, "happy" if t < SNAP else "love", walk=t * 1.6 if t < POSE else 0, stick=st)
    hearts_up(d, t, HEART1, x, 760)
    if t >= SNAP:
        k = popk(t, SNAP + 0.1)
        if k > 0:
            px, py = 540, 420
            d.rect(px - 200 * k, py - 170 * k, px + 200 * k, py + 170 * k, fill=A(WHITE, 1), r=10)
            d.rect(px - 180 * k, py - 150 * k, px + 180 * k, py + 110 * k, fill=A((255, 200, 110), 1))
            if k > 0.8:
                pyramid(d, px + 60, py + 110, 220, 180); alien(d, px - 90, py + 20, 42, t, "happy", body=False); alien(d, px - 10, py + 30, 42, t, "happy", body=False)
                heart(d, px + 120, py - 100, 20, PINK)
    flash(d, t, [SNAP], WHITE, 0.8)

def s_flag(t, d):
    desert_bg(d, (250, 236, 204), (240, 214, 170), 1000, t, mtn=False, pyc=((236, 206, 150), (212, 176, 120)))
    pl = ease(pr(t, PLANT - 0.25, PLANT))
    fx_, fy = 330, lerp(780, 1060, pl)
    flag(d, fx_, fy, 150, t)
    dustpuff(d, fx_, 1060, t, PLANT, 1.3)
    if t >= PLANT: d.ell(fx_, 1060, 90, 16, A(SAND_D, 1))
    mood = "chill" if t < PLANT else "proud"
    alien(d, 560, 800, 74, t, mood, handL=(fx_ + 8, lerp(fy - 300, 820, pl * 0)) if t < PLANT else (fx_ + 8, 900), sq=0.04 * pulse(t, [PLANT], 6))
    alien(d, 760, 820, 70, t, mood, handL=(640, 950))
    bubble(d, 760, 520, "这块地，我们的了！", 1, WHITE, NAVYT, popk(t, CLAIM), 44)

def s_dino(t, d):
    grad(d, (150, 200, 130), (236, 214, 150))
    mountain(d, 200, 1100, 500, 420, col=(140, 170, 160)); mountain(d, 900, 1100, 520, 380, col=(140, 170, 160))
    pk = ease(pr(t, PEEK, PEEK + 0.45)); hy = lerp(1000, 560, pk)
    jaw = 0.0
    if t >= ROAR: jaw = ease(pr(t, ROAR, ROAR + 0.15)) * (1 - pr(t, ROAR + 0.9, ROAR + 1.1))
    trex(d, 770, hy, 120, t, mood="angry" if t >= ROAR and t < WAIT else ("sus" if t >= WAIT else "chill"), jaw=jaw, look=(-1, 0.4), body=True)
    pyramid(d, 470, 1130, 820, 620)
    ground(d, 1100)
    if t >= ROAR and jaw > 0.3:
        for j in range(3):
            u = (t - ROAR) * 2 + j * 0.3
            d.arc(650, hy + 20, 60 + (u % 1) * 260, 40 + (u % 1) * 200, 120, 240, A(WHITE, 0.7 * (1 - u % 1)), 10)
    sc = t >= ROAR
    has = t < STEAL
    jump = 40 * math.exp(-max(0, t - ROAR) * 6) * (t >= ROAR)
    couple(d, 330, 900 - jump, 60, t, "scared" if sc else "happy", stick=1.0 if has else 0)
    if t >= PTERO:
        u = pr(t, PTERO, STEAL); v = pr(t, STEAL, STEAL + 1.2)
        if t < STEAL: px, py = lerp(1150, 520, ease(u)), lerp(260, 640, ease(u))
        else: px, py = lerp(520, -220, ease(v)), lerp(640, 560, v)
        ptero(d, px, py, 110, t, flap=t * 14, mood="smug", carry=t >= STEAL)
    if t >= WAIT:
        tag(d, 420, 690, "古埃及 · 约 4500 年前", (240, 180, 70), popk(t, WAIT + 0.1), 34)
        tag(d, 720, 800, "恐龙 · 6600 万年前", (110, 176, 90), popk(t, WAIT + 0.2), 34, WHITE)
    bigtxt(d, t, WAIT, "等等，", 280, 110, NAVYT)
    bigtxt(d, t, WAIT + 0.06, "时间线不对啊", 410, 100, (220, 56, 40))

def s_pharaoh(t, d):
    if t < AIM:
        rays(d, t, (230, 80, 60), (180, 36, 40), n=18, cx=540, cy=820)
        ground(d, 1150, (200, 120, 100), (170, 90, 80))
        u = pr(t, PHARAOH, LAND); y = lerp(-300, 760, u * u)
        sq = 0.12 * math.exp(-max(0, t - LAND) * 8) if t >= LAND else -0.05
        alien(d, 540, y, 100, t, "angry", pharaoh=True, sq=sq, handL=(420, y + 180), handR=(470, y + 200))
        blaster(d, 470, y + 200, 90, face=-1, charge=0.3, t=t)
        dustpuff(d, 540, 1040, t, LAND, 1.6, (240, 170, 150))
        tag(d, 540, 300, "法老外星人", GOLD, popk(t, LAND), 60, NAVYT)
        return
    # VS split
    d.poly([(-50, -50), (620, -50), (460, OH + 50), (-50, OH + 50)], A((60, 150, 210), 1))
    d.poly([(620, -50), (OW + 50, -50), (OW + 50, OH + 50), (460, OH + 50)], A((214, 50, 50), 1))
    lv = sum(1 for g in GLARE if t >= g); esc = 1 + 0.08 * lv
    for i in range(10):
        yy = (i * 200 + t * 900) % 2100 - 100; d.line([(-50, yy), (480, yy)], A(WHITE, 0.08), 6); d.line([(560, yy + 60), (OW + 50, yy + 60)], A(WHITE, 0.08), 6)
    alien(d, 300, 860, 120 * esc, t, "angry", brow=0.6 + 0.3 * lv, body=False)
    trex(d, 300, 1180, 80, t, "angry", jaw=0.3 * (lv > 1), body=False, look=(1, 0))
    alien(d, 780, 860, 120 * esc, t, "angry", pharaoh=True, brow=0.6 + 0.3 * lv, body=False)
    blaster(d, 830, 1130, 90, face=-1, charge=0.3 + 0.25 * lv, t=t)
    for g in GLARE:  # lightning clash between the faces
        if t >= g:
            r2 = random.Random(int(t * 20)); pts = [(470, 780)]
            for j in range(6): pts.append((470 + (j + 1) * 22 + r2.uniform(-10, 10), 780 + r2.uniform(-40, 40)))
            d.line(pts, A(YEL, 0.9), 10); break
    stamp(d, t, AIM, "VS", 540, 520, 170, YEL)

def s_fleet(t, d):
    grad(d, (34, 24, 74), (130, 70, 120))
    moon(d, 300, 420, 140, 0.9)
    for i in range(30): d.circ((i * 173) % 1080, (i * 97) % 900, 2 + i % 3, fill=A(WHITE, 0.5 + 0.4 * math.sin(t * 3 + i)))
    alarm = 0.5 + 0.5 * math.sin((t - FLEET) * math.pi / BEAT)
    d.rect(0, 0, OW, OH, fill=A((255, 40, 40), 0.1 * alarm))
    for i, (bx, by, bs) in enumerate(((220, 330, 50), (860, 300, 46), (700, 420, 34))): ufo(d, bx + 10 * math.sin(t * 2 + i), by, bs, t)
    for i, h in enumerate(FLEET_HITS):
        if t >= h:
            k = ease(pr(t, h, h + 0.4)); x = [380, 760, 560][i]; y = lerp(-150, [600, 640, 760][i], k)
            ufo(d, x, y + 8 * math.sin(t * 3 + i), [90, 100, 130][i], t, face=True, beam=k * 0.9)
    d.rect(-50, 1150, OW + 50, OH, fill=A((70, 40, 80), 1))
    pyramid(d, 220, 1160, 300, 200, lit=(110, 70, 110), sh=(80, 50, 90)); pyramid(d, 880, 1160, 340, 240, lit=(110, 70, 110), sh=(80, 50, 90))
    alien(d, 300, 1020, 50, t, "scared", look=0)
    alien(d, 420, 1020, 50, t, "scared")
    alien(d, 760, 1010, 56, t, "scared", pharaoh=True)
    trex(d, 580, 1050, 60, t, "up", look=(0, -1), body=False)

def s_wake(t, d):
    grad(d, (20, 24, 60), (70, 64, 110))
    moon(d, 820, 380, 120, 0.8)
    for i in range(30): d.circ((i * 173) % 1080, (i * 97) % 900, 2 + i % 3, fill=A(WHITE, 0.6))
    eo = ease(pr(t, SIL0 + 0.08, BIG2 - 0.06))
    statue(d, 540, 860, 230, t, eo=eo, eglow=0.8 * eo, mood="calm", body=False)
    d.ell(540, 1260, 760, 160, A((150, 120, 100), 1)); d.rect(-50, 1260, OW + 50, OH, fill=A((150, 120, 100), 1))
    for i in range(6):  # sand trickling off the hat
        u = (t * 1.5 + i / 6) % 1; d.circ(440 + i * 40, 560 + u * 300, 5, fill=A((200, 170, 130), 0.8 * (1 - u)))

def s_blast(t, d):
    hook_shot(d, t, BIG2, night=True)
    stamp(d, t, BIG2 + 0.05, "原来是他！", 540, 330, 130, YEL)

def s_fall(t, d):
    grad(d, (250, 160, 70), (190, 60, 50))
    for i in range(30): d.circ((i * 173) % 1080, (i * 97) % 700, 2, fill=A((255, 240, 200), 0.5))
    earth(d, 540, 1180, 330, t)
    trex(d, 540, 790, 34, t, "up", look=(0.3, -1), body=True)
    for i, h in enumerate(TRAILS + [FALL]):
        if t >= h - 0.6:
            u = (t - (h - 0.6)) / 2.6; sx = [940, 860, 1020, 760][i]; sy = [-60, -120, 0, -100][i]
            x = lerp(sx, [620, 420, 700, 520][i], u); y = lerp(sy, 900, u)
            if u < 1: fireball(d, x, y, [40, 30, 34, 50][i], t, 0.5, 0.86)
    d.text(540, 300, "残骸 → 地球", 70, A(WHITE, popk(t, FALL + 0.2)), k=1)

def s_extinct(t, d):
    grad(d, (250, 120, 60), (240, 190, 120))
    fb = pr(t, EXTINCT, SELFIE); fx_, fy = lerp(900, 760, fb), lerp(250, 470, fb)
    fireball(d, fx_, fy, 90 + 40 * fb, t, 0.55, 0.83)
    ground(d, 1120, (200, 150, 100), (170, 120, 80))
    lu = ease(pr(t, LOOKUP, LOOKUP + 0.3))
    sauropod(d, 720, 980, 110, t, look_up=lu)
    trex(d, 330, 820, 90, t, "up" if lu > 0.5 else "chill", look=(0.6 * lu, -lu), body=True)
    ptero(d, 560, 700, 70, t, flap=t * 10, mood="chill")
    for x_, y_ in ((330, 720), (700, 640)):
        if lu > 0.5: d.text(x_, y_, "……", 56, A(NAVYT, popk(t, LOOKUP + 0.1)), k=1)
    bigtxt(d, t, Q_HIT, "恐龙灭绝", 290, 150, NAVYT)
    bigtxt(d, t, Q_HIT + 0.08, "的真相？", 440, 120, WHITE)
    tag(d, 540, 550, "纯属虚构", (30, 24, 50), popk(t, Q_HIT + 0.3), 36, WHITE)

def selfie_group(d, t, x0, y0, x1, y1):
    d.rect(x0, y0, x1, y1, fill=A((250, 150, 70), 1))
    d.rect(x0, y0, x1, y0 + (y1 - y0) * 0.35, fill=A((240, 110, 70), 1))
    fireball(d, x1 - 130, y0 + 140, 70, t, 0.55, 0.83)
    pyramid(d, x0 + 150, y0 + (y1 - y0) * 0.62, 260, 200)
    statue(d, x1 - 120, y0 + 360, 70, t, eo=1, mood="angry", body=False)
    trex(d, x0 + 430, y0 + 420, 80, t, "scared", jaw=0.7, body=False, look=(0, -1))
    alien(d, x0 + 130, y0 + 640, 80, t, "scream", body=False)
    alien(d, x0 + 330, y0 + 660, 80, t, "scream", body=False)
    alien(d, x0 + 520, y0 + 650, 84, t, "scream", pharaoh=True, body=False)
def s_selfie(t, d):
    grad(d, (60, 40, 70), (150, 70, 70))
    tt = min(t, FREEZE)
    fr = ease(pr(t, FREEZE, FREEZE + 0.3))
    x0, y0, x1, y1 = 220, 340, 860, 1080
    if fr <= 0:
        d.rect(x0 - 25, y0 - 40, x1 + 25, y1 + 40, fill=A((36, 40, 58), 1), r=60)
    else:
        d.rect(x0 - 30 * fr, y0 - 30 * fr, x1 + 30 * fr, y1 + 140 * fr, fill=A(WHITE, 1), r=8)
    selfie_group(d, tt, x0, y0, x1, y1)
    if fr <= 0:
        d.circ(540, y1 + 22, 12, fill=A((80, 84, 100), 1))
        if t < CLICK: d.circ(540, y1 - 60, 40, fill=A(WHITE, 0.7 + 0.3 * math.sin(t * 8)))
        ptero(d, 540, 250 + 6 * math.sin(t * 8), 70, t, flap=t * 12, mood="smug")
    else:
        d.text(540, y1 + 75, "全员合照 · 古埃及 × 白垩纪", 40, A(NAVYT, fr), k=1)
    flash(d, t, [CLICK], WHITE, 1.0)
    stamp(d, t, CLICK, "咔嚓！", 540, 280, 100, YEL)

def s_stone(t, d):
    grad(d, (196, 214, 244), (244, 222, 190))
    pyramid(d, 200, 1120, 360, 260); pyramid(d, 930, 1120, 380, 280)
    ground(d, 1110)
    busted = t >= BUSTED
    gray = 0.6 * ease(pr(t, BUSTED, BUSTED + 0.3))
    shiv = 2 * math.sin(t * 60) * (t >= BUSTED) * (1 - pr(t, BUSTED, BUSTED + 0.6))
    peek = 0.0
    if WHISTLE <= t < STARE: peek = 0.6 if (t - WHISTLE) % 0.9 < 0.35 else 0
    statue(d, 540 + shiv, 560, 150, t, eo=peek if not busted else 0.0, mood="whistle" if t >= WHISTLE and not busted else "calm", gray=gray)
    if t >= WHISTLE and not busted:
        for i in range(3):
            u = ((t - WHISTLE) * 0.8 + i / 3) % 1; note(d, 640 + u * 140, 600 - u * 220, 34, NAVYT, 1 - u)
    if t >= WHISTLE: sweat(d, 680, 480, 30, 1)
    tag(d, 540, 300, "（假装是石头）", WHITE, popk(t, WHISTLE), 44)
    if t >= STARE:
        k = ease(pr(t, STARE, STARE + 0.35)); yb = lerp(1500, 1110, k)
        alien(d, 260, yb, 80, t, "flat", body=False); alien(d, 820, yb, 84, t, "flat", pharaoh=True, body=False)
        trex(d, 560, yb + 40, 70, t, "sus", body=False)
    bubble(d, 300, 960, "就是你吧", -1, WHITE, NAVYT, popk(t, BUSTED), 40)
    if busted:
        for j in range(3): d.line([(470 + j * 60, 640 + j * 50), (490 + j * 60, 700 + j * 50), (470 + j * 60, 740 + j * 50)], A((90, 90, 100), gray), 5)

ANS = "被石像国王用激光|打下来的飞碟砸的"
def s_exam(t, d):
    grad(d, (70, 160, 160), (40, 100, 116))
    d.rect(-50, 1250, OW + 50, OH, fill=A((180, 120, 70), 1))
    d.rect(212, 296, 874, 1206, fill=A((0, 0, 0), 0.15), r=10)
    d.rect(200, 280, 860, 1190, fill=A((252, 250, 242), 1), r=10)
    for i in range(10): d.line([(240, 560 + i * 62), (820, 560 + i * 62)], A((180, 200, 230), 0.6), 3)
    d.text(530, 360, "历史考试", 64, A(NAVYT, 1), k=1)
    d.text(250, 440, "姓名：外星人", 36, A((90, 90, 110), 1), anchor="lm", k=0)
    d.text(250, 520, "1. 恐龙为什么灭绝？", 44, A(NAVYT, 1), anchor="lm", k=1)
    n = int(len(ANS.replace("|", "")) * pr(t, WRITE, REDX - 0.3)); shown = 0
    for li, line in enumerate(ANS.split("|")):
        s = line[:max(0, n - shown)]; shown += len(line)
        if s: d.text(250, 620 + li * 80, s, 48, A((40, 80, 200), 1), anchor="lm", k=0)
    if WRITE <= t < REDX:
        px = 250 + d.tlen(ANS.split("|")[0 if n <= 8 else 1][:n if n <= 8 else n - 8], 48) + 10; py = 620 + (0 if n <= 8 else 80)
        d.line([(px, py), (px + 60, py - 140)], A((250, 200, 60), 1), 18); d.poly([(px - 6, py - 10), (px + 4, py + 12), (px + 12, py - 4)], A((240, 200, 160), 1))
    k = ease(pr(t, REDX, REDX + 0.25))
    if k > 0: cross(d, 520, 660, 190, k, (230, 40, 40))
    if t >= REDX2:
        kk = popk(t, REDX2); d.circ(760, 420, 80 * kk, outline=A((230, 40, 40), 1), w=10)
        d.text(760, 420, "0", int(110 * kk), A((230, 40, 40), 1), k=1)
        d.text(530, 900, "别瞎编！", int(64 * kk), A((230, 40, 40), 1), k=1)
    tag(d, 530, 1060, "纯属虚构", (30, 24, 50), popk(t, REDX2 + 0.3), 36, WHITE)
def cross(d, x, y, s, k, col, a=1.0):
    if k <= 0: return
    d.line([(x - s, y - s), (x - s + 2 * s * min(1, k * 2), y - s + 2 * s * min(1, k * 2))], A(col, a), s * 0.16)
    if k > 0.5: d.line([(x + s, y - s), (x + s - 2 * s * (k - 0.5) * 2, y - s + 2 * s * (k - 0.5) * 2)], A(col, a), s * 0.16)

def s_end(t, d):
    grad(d, (40, 50, 100), (170, 120, 140))
    moon(d, 300, 720, 150, 1)
    for i in range(30): d.circ((i * 173) % 1080, (i * 97) % 800, 2 + i % 2, fill=A(WHITE, 0.5 + 0.3 * math.sin(t * 2 + i)))
    pyramid(d, 260, 1130, 380, 280, lit=(170, 120, 120), sh=(120, 80, 100)); pyramid(d, 560, 1130, 300, 200, lit=(170, 120, 120), sh=(120, 80, 100))
    ground(d, 1120, (150, 110, 110), (120, 90, 100))
    wink = 1.0 if WINK <= t < WINK + 0.6 else 0.0
    statue(d, 790, 760, 90, t, eo=0.0 if wink == 0 else 1.0, wink=0 if wink == 0 else 1.0, mood="calm", eglow=0.3 * wink)
    if wink: star(d, 760, 720, 22, YEL, 1, rot=t * 3)
    u = pr(t, OUTRO, DUR); couple(d, lerp(470, 300, u), 990, 34, t, "love", walk=t * 1.5)
    px = lerp(-150, 1250, pr(t, OUTRO + 0.5, DUR)); ptero(d, px, 600 + 20 * math.sin(t * 2), 50, t, flap=t * 10, carry=True)
    stamp(d, t, FINAL, "纯属虚构", 540, 310, 120, (255, 220, 120))
    d.text(540, 440, "历史考试千万别这么写", int(56 * popk(t, FINAL + 0.25)) + 1, A(WHITE, popk(t, FINAL + 0.25)), k=1)
    if t > DUR - 0.5: d.rect(0, 0, OW, OH, fill=A((0, 0, 0), pr(t, DUR - 0.5, DUR)))

def subs(t, d):
    if SIL0 <= t < BIG2: return
    for a, b, s in SUBS:
        if a <= t < b:
            al = ease(pr(t, a, a + 0.1)) * (1 - pr(t, b - 0.08, b))
            ls = s.split("|"); n = len(ls); y0 = 1350 - (n - 1) * 70
            w = max(d.tlen(x, 54, 1) for x in ls) + 44
            d.rect(540 - w / 2, y0 - 44, 540 + w / 2, y0 + (n - 1) * 70 + 44, fill=A((15, 12, 26), 0.82 * al), r=22)
            for i, x in enumerate(ls): d.text(540, y0 + i * 70, x, 54, A(WHITE, al), k=1)
            break
def brand(t, d):
    s = "Vibe 知识大赏 · 娱乐加更"; w = d.tlen(s, 28, 1) + 50
    d.rect(540 - w / 2, 150, 540 + w / 2, 200, fill=A((15, 12, 26), 0.55), r=25); d.text(540, 175, s, 28, A(WHITE, 1), k=1)

SECS = [(-1, REWIND, s_hook), (REWIND, DATE, s_rewind), (DATE, FLAG, s_date), (FLAG, DINO, s_flag), (DINO, PHARAOH, s_dino),
        (PHARAOH, FLEET, s_pharaoh), (FLEET, SIL0, s_fleet), (SIL0, BIG2, s_wake), (BIG2, FALL, s_blast), (FALL, EXTINCT, s_fall),
        (EXTINCT, SELFIE, s_extinct), (SELFIE, STONE, s_selfie), (STONE, EXAM, s_stone), (EXAM, OUTRO, s_exam), (OUTRO, 99, s_end)]
def cam(t):
    z = 1.0 + 0.015 * pulse(t, HITS, 7) + 0.04 * pulse(t, [HOOK_HIT, BIG2], 3)
    for a, b in RISERS:
        if a <= t < b: z += 0.08 * eio(pr(t, a, b))
    if HOOK_STOP <= t < REWIND: z += 0.04 * pr(t, HOOK_STOP, REWIND)
    if SIL0 <= t < BIG2: z += 0.06 * eio(pr(t, SIL0, BIG2))
    amp = 8 * pulse(t, [HOOK_HIT, BIG2], 5) + 1.5 * pulse(t, HITS, 8)
    sx, sy = shake(t, amp, 40)
    return z, 540 + sx, 900 + sy
def frame(t):
    img = Image.new("RGB", (W, H), (30, 20, 50)); d = D(img)
    for a, b, sf in SECS:
        if a <= t < b: sf(t, d); break
    z, cx, cy = cam(t)
    cw, ch = W / z, H / z
    x0 = cl(P(cx) - cw / 2, 0, W - cw); y0 = cl(P(cy) - ch / 2, 0, H - ch)
    img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)); d = D(img)
    for c in CUTS:
        if c <= t < c + 0.1: d.rect(0, 0, OW, OH, fill=A(WHITE, 0.6 * (1 - (t - c) / 0.1)))
    brand(t, d); subs(t, d)
    return img.resize((OW, OH), Image.LANCZOS)
if __name__ == "__main__":
    if sys.argv[1] == "test":
        for ts in sys.argv[2:]: frame(float(ts)).save(f"/tmp/al_test_{float(ts):05.2f}.png")
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
