import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import C, P, lerp, ease, clamp, mixc, sun, cloud
W, H = 1080, 1920
GY = 1180

def blend(a, b, t):
    a = a.lstrip('#'); b = b.lstrip('#')
    return '#' + ''.join('%02x' % int(lerp(int(a[i:i+2], 16), int(b[i:i+2], 16), clamp(t))) for i in (0, 2, 4))

def sky(c, mood='day', k=1.0):
    cols = {'day': ('#79C3F0', '#DDF2FF'), 'dusk': ('#3B3561', '#E88A5A'), 'storm': ('#2A2F45', '#6A6F8A'),
            'warm': ('#F4A261', '#FFE3B3'), 'sad': ('#5B6C8C', '#B8C4D6')}[mood]
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, GY)], [C(cols[0]), C(cols[1])]))
    c.drawRect(skia.Rect(0, 0, W, GY + 5), p)

def street(c, dark=0.0):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, GY), skia.Point(0, H)],
        [mixc('#D9B382', '#5A4A3A', dark), mixc('#B98D5E', '#3A3028', dark)]))
    c.drawRect(skia.Rect(0, GY, W, H), p)
    c.drawRect(skia.Rect(0, GY - 6, W, GY + 14), P(mixc('#9C7B55', '#3A3028', dark)))
    random.seed(2)
    for i in range(40):
        x = random.uniform(0, W); y = random.uniform(GY + 40, H)
        c.drawOval(skia.Rect.MakeXYWH(x, y, 14, 7), P(mixc('#A67C52', '#2E2620', dark), alpha=.6))

def house(c, x, gy, w=420, h=360, wall='#F2C57C', roof='#C0392B', prog=1.0, crooked=0.0, cracks=0.0, glow=0.0, t=0.0, bricks=True, door='#7A4A2C'):
    c.save(); c.translate(x, gy)
    if crooked: c.skew(-crooked, 0)
    wh = h * clamp(prog / 0.85)
    if wh > 0:
        c.save(); c.clipRect(skia.Rect(-w / 2, -wh, w / 2, 0))
        c.drawRect(skia.Rect(-w / 2, -h, w / 2, 0), P(C(wall)))
        if bricks:
            bp = P(C('#000000', 28), 2, cap=False)
            for r in range(int(h / 30) + 1):
                yy = -r * 30; c.drawLine(-w / 2, yy, w / 2, yy, bp)
                for bx in range(-int(w / 2) + (30 if r % 2 else 0), int(w / 2), 60):
                    c.drawLine(bx, yy, bx, yy - 30, bp)
        # windows + door
        for wx in (-w * .3, w * .3):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(wx - 45, -h * .72, wx + 45, -h * .42), 8, 8), P(C('#7FC8F8')))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(wx - 45, -h * .72, wx + 45, -h * .42), 8, 8), P(C('#6B4026'), 8))
            c.drawLine(wx, -h * .72, wx, -h * .42, P(C('#6B4026'), 6))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-50, -h * .5, 50, 0), 40, 40), P(C(door)))
        c.drawCircle(30, -h * .25, 7, P(C('#F2C14E')))
        c.restore()
        c.drawRect(skia.Rect(-w / 2, -wh, w / 2, 0), P(C('#000000', 40), 4))
    if prog > 0.85:
        k = ease((prog - 0.85) / 0.15)
        rf = skia.Path(); rf.moveTo(-w / 2 - 40, -h); rf.lineTo(0, -h - 190 * k); rf.lineTo(w / 2 + 40, -h); rf.close()
        c.drawPath(rf, P(C(roof)))
        c.drawPath(rf, P(C('#000000', 50), 4))
    if cracks > 0:
        random.seed(21)
        cp = P(C('#3A1F10', int(255 * clamp(cracks))), 5)
        for cx0, cy0 in [(-w * .38, -h * .9), (w * .15, -h * .85), (-w * .05, -h * .3), (w * .4, -h * .45)]:
            path = skia.Path(); path.moveTo(cx0, cy0); x0, y0 = cx0, cy0
            L = int(6 * clamp(cracks * 1.5))
            for i in range(L):
                x0 += random.uniform(-25, 25); y0 += random.uniform(18, 34); path.lineTo(x0, y0)
            c.drawPath(path, cp)
            if glow > 0: c.drawPath(path, P(C('#FF3B30', int(150 * glow)), 14))
    c.restore()

def face(c, cx, cy, r, skin, mood='neutral', talk=False, t=0.0, look=(0, 0), blink_off=0.0):
    c.drawCircle(cx, cy, r, P(C(skin)))
    c.drawCircle(cx - r * .95, cy + 5, r * .2, P(C(skin))); c.drawCircle(cx + r * .95, cy + 5, r * .2, P(C(skin)))
    bl = ((t + blink_off) % 3.9) < 0.12
    ey = cy - r * .12; lx, ly = look
    big = mood == 'shocked'
    for ex in (cx - r * .36, cx + r * .36):
        if bl and not big:
            c.drawLine(ex - 9, ey, ex + 9, ey, P(C('#2B1A0E'), 4))
        else:
            er = r * (.2 if big else .14)
            c.drawOval(skia.Rect(ex - er, ey - er * 1.1, ex + er, ey + er * 1.1), P(C('#FFFFFF')))
            c.drawCircle(ex + lx * er * .4, ey + ly * er * .4, er * (.45 if big else .6), P(C('#2B1A0E')))
            c.drawCircle(ex + lx * er * .4 + 3, ey + ly * er * .4 - 3, 2.5, P(C('#FFFFFF')))
    bp = P(C('#3A2A20'), 5)
    by = ey - r * .3
    if mood in ('sad',):
        c.drawLine(cx - r * .55, by + 6, cx - r * .2, by - 6, bp); c.drawLine(cx + r * .55, by + 6, cx + r * .2, by - 6, bp)
    elif big:
        c.drawLine(cx - r * .55, by - 12, cx - r * .2, by - 16, bp); c.drawLine(cx + r * .55, by - 12, cx + r * .2, by - 16, bp)
    else:
        c.drawLine(cx - r * .55, by, cx - r * .2, by - 4, bp); c.drawLine(cx + r * .55, by, cx + r * .2, by - 4, bp)
    c.drawCircle(cx - r * .55, cy + r * .2, r * .13, P(C('#E07A6A', 90))); c.drawCircle(cx + r * .55, cy + r * .2, r * .13, P(C('#E07A6A', 90)))
    c.drawPath(nose(cx, cy, r), P(C('#000000', 45), 4))
    return ey

def nose(cx, cy, r):
    p = skia.Path(); p.moveTo(cx, cy - r * .05); p.quadTo(cx + r * .12, cy + r * .15, cx - r * .02, cy + r * .2); return p

def mouth(c, cx, my, r, mood, talk, t):
    o = (abs(math.sin(t * 12)) * .8 + .2) if talk else 0
    mp = P(C('#5A1E10'), 5)
    if mood == 'shocked':
        c.drawOval(skia.Rect(cx - r * .14, my - r * .05, cx + r * .14, my + r * .3), P(C('#5A1E10')))
    elif o > .3:
        c.drawOval(skia.Rect(cx - r * .17, my, cx + r * .17, my + r * .08 + r * .22 * o), P(C('#6A2414')))
    elif mood in ('happy', 'proud'):
        c.drawArc(skia.Rect(cx - r * .3, my - r * .2, cx + r * .3, my + r * .2), 20, 140, False, mp)
    elif mood == 'sad':
        c.drawArc(skia.Rect(cx - r * .22, my + r * .02, cx + r * .22, my + r * .3), 200, 140, False, mp)
    else:
        c.drawLine(cx - r * .15, my + r * .08, cx + r * .15, my + r * .08, mp)

def ramu(c, x, gy, s=1.0, mood='neutral', talk=False, t=0.0, look=(0, 0), old=1.0, arm='down', prop=None, stick=False, tear=0.0, shake=0.0):
    s *= 1.15
    c.save(); c.translate(x + shake, gy); c.scale(s, s)
    skin = '#A8714A'
    # legs/dhoti
    c.drawRect(skia.Rect(-55, -230, 55, -20), P(C('#F3EFE4')))
    c.drawLine(-25, -25, -30, 0, P(C('#8A5A3B'), 18)); c.drawLine(25, -25, 30, 0, P(C('#8A5A3B'), 18))
    c.drawOval(skia.Rect(-58, -12, -10, 6), P(C('#4A3020'))); c.drawOval(skia.Rect(10, -12, 58, 6), P(C('#4A3020')))
    # kurta
    k = skia.Path(); k.moveTo(-75, -210); k.lineTo(-62, -420); k.quadTo(0, -445, 62, -420); k.lineTo(75, -210); k.close()
    c.drawPath(k, P(C('#E8D8B8')))
    c.drawLine(0, -430, 0, -330, P(C('#C8B48E'), 4))
    # gamchha
    g = skia.Path(); g.moveTo(-60, -420); g.quadTo(-20, -380, 40, -425); g.lineTo(55, -415); g.quadTo(-10, -360, -70, -395); g.close()
    c.drawPath(g, P(C('#D9534F')))
    # arms
    ap = P(C('#E8D8B8'), 34)
    if arm == 'shrug':
        c.drawLine(-62, -400, -120, -440, ap); c.drawLine(-120, -440, -150, -500, ap)
        c.drawLine(62, -400, 120, -440, ap); c.drawLine(120, -440, 150, -500, ap)
        c.drawCircle(-150, -510, 20, P(C(skin))); c.drawCircle(150, -510, 20, P(C(skin)))
    elif arm == 'out':
        c.drawLine(62, -400, 160, -330, ap); c.drawCircle(170, -322, 20, P(C(skin)))
        c.drawLine(-62, -400, -80, -250, ap); c.drawCircle(-82, -238, 20, P(C(skin)))
    elif arm == 'face':
        c.drawLine(-62, -400, -50, -470, ap); c.drawCircle(-45, -480, 20, P(C(skin)))
        c.drawLine(62, -400, 50, -470, ap); c.drawCircle(45, -480, 20, P(C(skin)))
    else:
        c.drawLine(-62, -400, -80, -250, ap); c.drawCircle(-82, -238, 20, P(C(skin)))
        c.drawLine(62, -400, 80, -250, ap); c.drawCircle(82, -238, 20, P(C(skin)))
    if prop == 'trowel':
        c.drawLine(82, -238, 100, -200, P(C('#7A4A2C'), 10))
        tr = skia.Path(); tr.moveTo(95, -205); tr.lineTo(150, -170); tr.lineTo(110, -150); tr.close(); c.drawPath(tr, P(C('#B0B8C0')))
    if prop == 'key':
        draw_key(c, 175, -322, 0.6, 0)
    if stick:
        c.drawLine(-82, -238, -100, 0, P(C('#6B4226'), 10))
    # neck/head
    c.drawRect(skia.Rect(-16, -470, 16, -425), P(C(skin)))
    hc = '#2E2A28' if old < .5 else '#F2F2F2'
    cy = -545
    c.drawOval(skia.Rect(-78, cy - 85, 78, cy + 20), P(C(blend('#2E2A28', '#E8E8E8', old))))
    ey = face(c, 0, cy, 72, skin, mood, talk, t, look)
    c.drawOval(skia.Rect(-60, cy - 90, 60, cy - 40), P(C(blend('#2E2A28', '#EDEDED', old))))  # hair/cap top
    # moustache
    mc = C(blend('#2E2A28', '#F5F5F5', old))
    m = skia.Path(); m.moveTo(-42, cy + 30); m.quadTo(-20, cy + 12, 0, cy + 24); m.quadTo(20, cy + 12, 42, cy + 30); m.quadTo(20, cy + 32, 0, cy + 30); m.quadTo(-20, cy + 32, -42, cy + 30)
    c.drawPath(m, P(mc))
    mouth(c, 0, cy + 36, 72, mood, talk, t)
    if old > .5:
        c.drawLine(-30, cy - 48, 30, cy - 48, P(C('#000000', 30), 3))  # wrinkle
    if tear > 0:
        for i, ex in enumerate((-26, 26)):
            ty = ey + 20 + ((t * 120 + i * 40) % 90) * clamp(tear)
            c.drawOval(skia.Rect(ex - 7, ty, ex + 7, ty + 18), P(C('#8FD3FF', int(230 * tear))))
    c.restore()

def seth(c, x, gy, s=1.0, mood='happy', talk=False, t=0.0, look=(0, 0), arm='down', prop=None):
    s *= 1.15
    c.save(); c.translate(x, gy); c.scale(s, s)
    skin = '#D9A06B'
    c.drawRect(skia.Rect(-60, -200, 60, -10), P(C('#FFFFFF')))
    c.drawOval(skia.Rect(-62, -14, -10, 6), P(C('#7A1F1F'))); c.drawOval(skia.Rect(10, -14, 62, 6), P(C('#7A1F1F')))
    c.drawOval(skia.Rect(-120, -460, 120, -170), P(C('#8E2C48')))   # belly kurta
    vest = skia.Path(); vest.moveTo(-100, -420); vest.quadTo(-125, -300, -95, -200); vest.lineTo(-35, -200); vest.lineTo(-25, -430); vest.close()
    c.drawPath(vest, P(C('#E0A526')))
    vest2 = skia.Path(); vest2.moveTo(100, -420); vest2.quadTo(125, -300, 95, -200); vest2.lineTo(35, -200); vest2.lineTo(25, -430); vest2.close()
    c.drawPath(vest2, P(C('#E0A526')))
    for i in range(4): c.drawCircle(0, -400 + i * 50, 7, P(C('#F7D774')))
    c.drawArc(skia.Rect(-45, -470, 45, -380), 20, 140, False, P(C('#F7D774'), 6))  # chain
    ap = P(C('#8E2C48'), 38)
    if arm == 'give':
        c.drawLine(-100, -400, -190, -330, ap); c.drawCircle(-200, -322, 22, P(C(skin)))
    else:
        c.drawLine(-100, -400, -130, -250, ap); c.drawCircle(-132, -236, 22, P(C(skin)))
    c.drawLine(100, -400, 130, -250, ap); c.drawCircle(132, -236, 22, P(C(skin)))
    if prop == 'key': draw_key(c, -205, -322, 0.6, 0)
    c.drawRect(skia.Rect(-18, -490, 18, -450), P(C(skin)))
    cy = -560
    ey = face(c, 0, cy, 78, skin, mood, talk, t, look, blink_off=1.7)
    # turban
    c.drawOval(skia.Rect(-88, cy - 120, 88, cy - 30), P(C('#F28C28')))
    c.drawOval(skia.Rect(-70, cy - 140, 70, cy - 70), P(C('#F6A64A')))
    c.drawCircle(0, cy - 75, 12, P(C('#E53935')))
    # big moustache
    m = skia.Path(); m.moveTo(-70, cy + 20); m.quadTo(-35, cy + 5, 0, cy + 26); m.quadTo(35, cy + 5, 70, cy + 20)
    m.quadTo(80, cy, 70, cy - 4); m.quadTo(40, cy + 30, 0, cy + 36); m.quadTo(-40, cy + 30, -70, cy - 4); m.quadTo(-80, cy, -70, cy + 20)
    c.drawPath(m, P(C('#2A1C14')))
    mouth(c, 0, cy + 42, 78, mood, talk, t)
    c.restore()

def draw_key(c, x, y, s=1.0, rot=0.0, glow=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    if glow > 0:
        g = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(skia.Point(0, 0), 220, [C('#FFF3B0', int(200 * glow)), C('#FFF3B0', 0)]))
        c.drawCircle(0, 0, 220, g)
    gp = P(C('#F2B632')); dp = P(C('#B8860B'), 6)
    c.drawCircle(-60, 0, 45, gp); c.drawCircle(-60, 0, 45, dp); c.drawCircle(-60, 0, 18, P(C('#FFF8E1')))
    c.drawRect(skia.Rect(-20, -12, 110, 12), gp)
    c.drawRect(skia.Rect(70, 12, 85, 40), gp); c.drawRect(skia.Rect(95, 12, 110, 32), gp)
    c.drawCircle(-72, -14, 10, P(C('#FFF3B0', 200)))
    c.restore()

def bubble(c, x, y, rw, rh, a=1.0, tail=(-1, 1)):
    p = P(C('#FFFFFF', int(245 * a)))
    c.drawOval(skia.Rect(x - rw, y - rh, x + rw, y + rh), p)
    c.drawCircle(x + tail[0] * rw * .55, y + rh * 1.15, 22, p); c.drawCircle(x + tail[0] * rw * .7, y + rh * 1.45, 13, p)
    c.drawOval(skia.Rect(x - rw, y - rh, x + rw, y + rh), P(C('#C9D6E3', int(255 * a)), 4))

def brick_pile(c, x, gy, cracked=True, s=1.0):
    c.save(); c.translate(x, gy); c.scale(s, s)
    for row in range(4):
        for i in range(4 - row):
            bx = -150 + i * 80 + row * 40; by = -45 - row * 42
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + 74, by + 38), 5, 5), P(C('#C0603A')))
            if cracked:
                path = skia.Path(); path.moveTo(bx + 20, by + 2); path.lineTo(bx + 32, by + 18); path.lineTo(bx + 26, by + 36)
                c.drawPath(path, P(C('#5A2A16'), 3))
    c.restore()

def cement_bag(c, x, gy, s=1.0):
    c.save(); c.translate(x, gy); c.scale(s, s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-80, -180, 80, 0), 25, 25), P(C('#D7D2C8')))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-80, -180, 80, 0), 25, 25), P(C('#9E978A'), 5))
    c.drawRect(skia.Rect(-55, -120, 55, -70), P(C('#9E978A')))
    c.restore()

def sand_heap(c, x, gy, k, s=1.0):
    if k <= 0: return
    c.save(); c.translate(x, gy); c.scale(s, s)
    p = skia.Path(); p.moveTo(-170 * k, 0); p.quadTo(0, -230 * k, 170 * k, 0); p.close()
    c.drawPath(p, P(C('#E8C27A')))
    random.seed(4)
    for i in range(25):
        c.drawCircle(random.uniform(-120, 120) * k, -random.uniform(10, 120) * k, 3, P(C('#C9A05A')))
    c.restore()

def sparkle(c, x, y, r, a=1.0, col='#FFF3B0'):
    if a <= 0: return
    p = skia.Path(); p.moveTo(x, y - r); p.quadTo(x, y, x + r, y); p.quadTo(x, y, x, y + r); p.quadTo(x, y, x - r, y); p.quadTo(x, y, x, y - r)
    c.drawPath(p, P(C(col, int(255 * a))))

def mini_family(c, x, y, s=1.0):
    for dx, hh, col in [(-60, 1.0, '#3C7DBF'), (0, .85, '#E91E63'), (55, .6, '#4CAF50')]:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x + dx * s - 22 * s, y - 70 * hh * s, x + dx * s + 22 * s, y), 12, 12), P(C(col)))
        c.drawCircle(x + dx * s, y - 70 * hh * s - 20 * s, 20 * s, P(C('#C68B5A')))
    c.drawPath(heart(x, y - 150 * s, 26 * s), P(C('#E53935')))

def heart(x, y, r):
    p = skia.Path(); p.moveTo(x, y + r)
    p.cubicTo(x - r * 2, y - r * .3, x - r * .8, y - r * 1.6, x, y - r * .5)
    p.cubicTo(x + r * .8, y - r * 1.6, x + r * 2, y - r * .3, x, y + r); return p
