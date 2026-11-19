import skia, math, random
W, H = 1920, 1080
GY = 600  # ground surface line

def C(h, a=255):
    h = h.lstrip('#')
    return skia.ColorSetARGB(int(a), int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t):
    t = clamp(t); return t * t * (3 - 2 * t)
def mixc(h1, h2, t, a=255):
    h1 = h1.lstrip('#'); h2 = h2.lstrip('#'); t = clamp(t)
    v = [int(lerp(int(h1[i:i+2], 16), int(h2[i:i+2], 16), t)) for i in (0, 2, 4)]
    return skia.ColorSetARGB(int(a), *v)

def P(color, stroke=None, cap=True, alpha=None):
    p = skia.Paint(AntiAlias=True, Color=color)
    if alpha is not None: p.setAlphaf(alpha)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

# ---------- sky / environment ----------
DAY = ('#7EC8F2', '#D8F0FF')
NIGHT = ('#142046', '#3A4A86')
DUSK = ('#F59E6B', '#FFE0A3')

def sky(c, night=0.0, dusk=0.0):
    top = DAY[0]; bot = DAY[1]
    def blend(a, b, t):
        a = a.lstrip('#'); b = b.lstrip('#')
        return '#' + ''.join('%02x' % int(lerp(int(a[i:i+2], 16), int(b[i:i+2], 16), clamp(t))) for i in (0, 2, 4))
    top = blend(top, DUSK[0], dusk); bot = blend(bot, DUSK[1], dusk)
    top = blend(top, NIGHT[0], night); bot = blend(bot, NIGHT[1], night)
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(0, GY)], [C(top), C(bot)]))
    c.drawRect(skia.Rect(0, 0, W, GY + 5), p)

def sun(c, x, y, r=70, a=1.0):
    g = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        skia.Point(x, y), r * 2.6, [C('#FFF3B0', int(150 * a)), C('#FFF3B0', 0)]))
    c.drawCircle(x, y, r * 2.6, g)
    c.drawCircle(x, y, r, P(C('#FFD34D', int(255 * a))))
    c.drawCircle(x - r * .25, y - r * .25, r * .55, P(C('#FFE68A', int(200 * a))))

def moon(c, x, y, r=50, a=1.0):
    c.drawCircle(x, y, r * 2, P(C('#C9D6FF', int(40 * a))))
    c.drawCircle(x, y, r, P(C('#F4F1DE', int(255 * a))))
    c.drawCircle(x + 14, y - 8, r * .22, P(C('#DAD6BE', int(255 * a))))
    c.drawCircle(x - 16, y + 14, r * .14, P(C('#DAD6BE', int(255 * a))))

random.seed(3)
STARS = [(random.uniform(0, W), random.uniform(0, GY - 120), random.uniform(1.5, 3.5)) for _ in range(90)]
def stars(c, a):
    if a <= 0: return
    for x, y, r in STARS: c.drawCircle(x, y, r, P(C('#FFFFFF', int(220 * a))))

def cloud(c, x, y, s=1.0, col='#FFFFFF', a=235):
    p = P(C(col, a))
    for dx, dy, r in [(-70, 10, 45), (-20, -15, 60), (45, -5, 50), (90, 15, 38), (10, 20, 50)]:
        c.drawCircle(x + dx * s, y + dy * s, r * s, p)

def hills(c, dark=0.0, dusk=0.0):
    base1 = mixc('#9FD67A', '#2C4A3A', dark); base2 = mixc('#7CC35E', '#24402F', dark)
    for col, pts, yb in [(base1, [(0, 470), (300, 400), (650, 470), (1000, 390), (1400, 460), (1700, 410), (1920, 450)], 0),
                         (base2, [(0, 540), (400, 490), (800, 545), (1200, 500), (1600, 540), (1920, 505)], 0)]:
        path = skia.Path(); path.moveTo(0, GY + 2); path.lineTo(*pts[0])
        for i in range(1, len(pts)):
            x0, y0 = pts[i - 1]; x1, y1 = pts[i]
            path.quadTo(x0 + (x1 - x0) / 2, min(y0, y1) - 25, x1, y1)
        path.lineTo(W, GY + 2); path.close()
        c.drawPath(path, P(col))

random.seed(7)
PEBBLES = [(random.uniform(0, W), random.uniform(GY + 70, H), random.uniform(5, 14), random.choice(['#8A5A3B', '#9B6B47', '#6E4630'])) for _ in range(70)]
def ground(c, dark=0.0):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, GY), skia.Point(0, H)], [mixc('#A86F45', '#4A3020', dark), mixc('#6B4026', '#2A1A10', dark)]))
    c.drawRect(skia.Rect(0, GY, W, H), p)
    # soil layer lines
    for i, yy in enumerate([760, 900, 1010]):
        path = skia.Path(); path.moveTo(0, yy)
        for x in range(0, W + 1, 240):
            path.quadTo(x + 120, yy + (14 if (x // 240) % 2 else -14), x + 240, yy)
        c.drawPath(path, P(mixc('#7B4B2E', '#3A2416', dark), 5, alpha=.55))
    for x, y, r, col in PEBBLES:
        c.drawOval(skia.Rect.MakeXYWH(x, y, r * 1.5, r), P(mixc(col, '#2A1A10', dark * .7)))
    # grass band
    c.drawRect(skia.Rect(0, GY - 4, W, GY + 26), P(mixc('#5DB346', '#22402A', dark)))
    gp = P(mixc('#4A9A38', '#1C3522', dark), 4)
    for x in range(0, W, 22):
        h = 14 + (x * 37 % 13)
        c.drawLine(x, GY + 6, x + 4, GY - h, gp)

# ---------- characters ----------
def seed(c, x, y, s=1.0, mood='happy', t=0.0, talk=False, rot=0.0, blink_off=0.0, look=(0, 0), closed=False):
    s = s * 1.3
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    body = skia.Path(); body.addOval(skia.Rect(-38, -50, 38, 50))
    c.drawOval(skia.Rect(-40, -52, 40, 52), P(C('#6A3E1E')))
    c.drawOval(skia.Rect(-36, -48, 36, 48), P(C('#C98A4B')))
    c.drawOval(skia.Rect(-26, -40, 4, -8), P(C('#E3AE72', 200)))
    # seed seam
    c.drawArc(skia.Rect(-10, -48, 30, 48), -80, 160, False, P(C('#9A6234'), 3))
    # cheeks
    c.drawCircle(-22, 12, 7, P(C('#F08A7A', 150))); c.drawCircle(22, 12, 7, P(C('#F08A7A', 150)))
    # eyes
    bl = ((t + blink_off) % 3.7) < 0.12
    lx, ly = look
    for ex in (-13, 13):
        if closed or bl:
            c.drawArc(skia.Rect(ex - 8, -8, ex + 8, 4), 20, 140, False, P(C('#2B1A0E'), 3.5))
        else:
            c.drawOval(skia.Rect(ex - 9, -14, ex + 9, 6), P(C('#FFFFFF')))
            c.drawCircle(ex + lx * 3, -3 + ly * 3, 5.5, P(C('#2B1A0E')))
            c.drawCircle(ex + lx * 3 + 2, -5 + ly * 3, 1.8, P(C('#FFFFFF')))
    # brows
    bp = P(C('#4A2A12'), 3.5)
    if mood == 'scared':
        c.drawLine(-21, -24, -6, -20, bp); c.drawLine(21, -24, 6, -20, bp)
        c.drawLine(-21, -24, -6, -28, bp) if False else None
    elif mood == 'sad':
        c.drawLine(-20, -19, -6, -24, bp); c.drawLine(20, -19, 6, -24, bp)
    # mouth
    mp = P(C('#4A1E10'), 3.5)
    open_ = (abs(math.sin(t * 13)) * 0.8 + 0.2) if talk else 0
    if mood == 'happy':
        if open_ > 0.25:
            c.drawOval(skia.Rect(-8, 12, 8, 14 + 12 * open_), P(C('#7A2A1A')))
        else:
            c.drawArc(skia.Rect(-10, 6, 10, 22), 20, 140, False, mp)
    elif mood == 'scared':
        if open_ > 0.25:
            c.drawOval(skia.Rect(-6, 13, 6, 15 + 10 * open_), P(C('#7A2A1A')))
        else:
            path = skia.Path(); path.moveTo(-10, 18)
            path.quadTo(-5, 13, 0, 18); path.quadTo(5, 23, 10, 18)
            c.drawPath(path, mp)
    else:
        c.drawArc(skia.Rect(-9, 16, 9, 28), 200, 140, False, mp)
    c.restore()

def roots(c, x, y, prog, s=1.0):
    if prog <= 0: return
    p = P(C('#E9D2A6'), 6 * s)
    p2 = P(C('#E9D2A6'), 3.5 * s)
    for ang, ln, w in [(0, 170, p), (-35, 120, p2), (35, 130, p2), (-60, 80, p2), (60, 90, p2)]:
        L = ln * s * clamp(prog * 1.3 - abs(ang) / 200)
        if L <= 0: continue
        a = math.radians(90 + ang)
        ex, ey = x + math.cos(a) * L, y + 62 + math.sin(a) * L
        path = skia.Path(); path.moveTo(x, y + 62)
        path.quadTo(x + (ex - x) * .3 + 15 * s, y + 62 + (ey - y) * .5, ex, ey)
        c.drawPath(path, w)

def leaf(c, x, y, ang, size, col='#5FBF4A'):
    c.save(); c.translate(x, y); c.rotate(ang)
    path = skia.Path(); path.moveTo(0, 0)
    path.quadTo(size * .5, -size * .45, size, 0); path.quadTo(size * .5, size * .45, 0, 0)
    c.drawPath(path, P(C(col)))
    c.drawLine(2, 0, size * .85, 0, P(C('#3F8F32'), 2))
    c.restore()

def plant(c, x, seed_y, growth, t=0.0, sway=1.0):
    """growth 0..1: 0-0.3 stem underground to surface; 0.3-1 above-ground up to ~330px"""
    if growth <= 0: return
    under = clamp(growth / 0.3)
    top_y = lerp(seed_y - 62, GY, under)
    above = 0 if growth < 0.3 else ease((growth - 0.3) / 0.7) * 330
    tip_y = top_y - above
    sw = math.sin(t * 1.6) * 8 * sway * (above / 330)
    tipx = x + sw
    width = 7 + 7 * clamp(growth)
    path = skia.Path(); path.moveTo(x, seed_y - 62)
    path.cubicTo(x - 10, lerp(seed_y - 62, tip_y, .4), tipx + 10, lerp(seed_y - 62, tip_y, .7), tipx, tip_y)
    c.drawPath(path, P(C('#4FA63B'), width))
    if growth > 0.22:
        # leaves along stem
        n = int(clamp((growth - 0.22) / 0.78) * 6) + 1
        for i in range(n):
            f = 1 - i / 6.5
            ly = lerp(GY if growth >= .3 else top_y, tip_y, f) if growth >= .3 else tip_y
            lx = lerp(x, tipx, f)
            size = (40 + 45 * clamp(growth)) * (0.7 + 0.3 * (1 - f)) * min(1, (growth - .22) * 4)
            if i == 0:
                leaf(c, lx, ly, -40 + sw, size * .8); leaf(c, lx, ly, -140 + sw, size * .8)
            else:
                side = 1 if i % 2 else -1
                leaf(c, lx, ly, (-25 if side > 0 else -155) + sw, size)

def tree(c, x, gy, s=1.0, t=0.0, fruit=1.0):
    c.save(); c.translate(x, gy); c.scale(s, s)
    # roots underground
    rp = P(C('#7A4B2A'), 14)
    for ang, ln in [(60, 160), (100, 200), (125, 150), (80, 130)]:
        a = math.radians(ang)
        path = skia.Path(); path.moveTo(0, 10)
        path.quadTo(math.cos(a) * ln * .5 + 20, 60, math.cos(a) * ln, math.sin(a) * ln)
        c.drawPath(path, rp)
    trunk = skia.Path()
    trunk.moveTo(-45, 10); trunk.quadTo(-30, -150, -25, -280); trunk.lineTo(25, -280); trunk.quadTo(30, -150, 45, 10); trunk.close()
    c.drawPath(trunk, P(C('#8B5A33')))
    c.drawLine(-5, -270, -70, -360, P(C('#8B5A33'), 22)); c.drawLine(5, -270, 80, -370, P(C('#8B5A33'), 22))
    sw = math.sin(t * 1.2) * 4
    for dx, dy, r, col in [(-150, -380, 120, '#3E9A3A'), (150, -390, 125, '#3E9A3A'), (0, -470, 150, '#46A842'),
                           (-90, -520, 110, '#52B54A'), (100, -520, 115, '#52B54A'), (0, -360, 120, '#4BAE44'),
                           (-200, -460, 85, '#46A842'), (210, -460, 85, '#46A842')]:
        c.drawCircle(dx + sw, dy, r, P(C(col)))
    for dx, dy, r in [(-60, -560, 40), (80, -560, 35), (-170, -470, 30)]:
        c.drawCircle(dx + sw, dy, r, P(C('#6CC85E', 160)))
    random.seed(11)
    for i in range(14):
        fx = random.uniform(-230, 230); fy = random.uniform(-600, -330)
        if (fx / 230) ** 2 + ((fy + 465) / 150) ** 2 > 1.4: continue
        k = clamp(fruit * 14 - i)
        if k <= 0: continue
        c.drawOval(skia.Rect.MakeXYWH(fx + sw - 14 * k, fy - 18 * k, 28 * k, 36 * k), P(C('#FFA62B')))
        c.drawCircle(fx + sw - 4 * k, fy - 8 * k, 5 * k, P(C('#FFD07A')))
    c.restore()

def hen(c, x, y, s=1.0, walk=0.0, head_dip=0.0, scratch=0.0, facing=-1):
    """y = feet position. facing -1 = looking left"""
    c.save(); c.translate(x, y); c.scale(s * facing * -1, s)  # draw facing left by default
    # legs
    lp = P(C('#F2A93B'), 7)
    sw = math.sin(walk) * 18
    k = math.sin(scratch) * 25 if scratch else 0
    c.drawLine(-15, -80, -15 + sw, 0, lp); c.drawLine(15, -80, 15 - sw + k, -abs(k) * .6, lp)
    for fx, fy in [(-15 + sw, 0), (15 - sw + k, -abs(k) * .6)]:
        c.drawLine(fx, fy, fx - 16, fy + 2, P(C('#F2A93B'), 5)); c.drawLine(fx, fy, fx + 10, fy + 3, P(C('#F2A93B'), 5))
    # tail
    for i, col in enumerate(['#C8452E', '#2F5F3A', '#E0B23A']):
        path = skia.Path(); path.moveTo(55, -130)
        path.quadTo(110 + i * 10, -230 + i * 25, 135 - i * 5, -120 + i * 10); path.quadTo(100, -120, 70, -105); path.close()
        c.drawPath(path, P(C(col)))
    # body
    c.drawOval(skia.Rect(-80, -175, 85, -70), P(C('#FFF6E8')))
    c.drawOval(skia.Rect(-80, -175, 85, -70), P(C('#D9C8B0'), 3))
    # wing
    wing = skia.Path(); wing.moveTo(-15, -140); wing.quadTo(55, -160, 60, -110); wing.quadTo(20, -85, -15, -140); wing.close()
    c.drawPath(wing, P(C('#EBDAC0')))
    # head (dips down for pecking)
    hx = -70; hy = lerp(-185, -40, head_dip)
    c.drawLine(-50, -150, hx + 10, hy + 15, P(C('#FFF6E8'), 40))
    c.drawCircle(hx, hy, 32, P(C('#FFF6E8')))
    for cx, cy, r in [(-10, -32, 11), (2, -36, 12), (14, -30, 10)]:
        c.drawCircle(hx + cx - 5, hy + cy + 4, r, P(C('#E5382C')))
    c.drawOval(skia.Rect(hx - 26, hy + 14, hx - 12, hy + 38), P(C('#E5382C')))
    beak = skia.Path(); beak.moveTo(hx - 26, hy - 6); beak.lineTo(hx - 54, hy + 4); beak.lineTo(hx - 26, hy + 12); beak.close()
    c.drawPath(beak, P(C('#F2A93B')))
    c.drawCircle(hx - 8, hy - 6, 6, P(C('#1E1E1E'))); c.drawCircle(hx - 6, hy - 8, 2, P(C('#FFFFFF')))
    c.restore()

def farmer(c, x, gy, arm=0.0, t=0.0):
    c.save(); c.translate(x, gy)
    # legs / dhoti
    c.drawRect(skia.Rect(-38, -150, 38, -10), P(C('#F4F0E6')))
    c.drawLine(-18, -12, -22, 0, P(C('#7A4A2C'), 14)); c.drawLine(18, -12, 22, 0, P(C('#7A4A2C'), 14))
    # kurta
    body = skia.Path(); body.moveTo(-55, -150); body.lineTo(-45, -310); body.quadTo(0, -330, 45, -310); body.lineTo(55, -150); body.close()
    c.drawPath(body, P(C('#3C7DBF')))
    # pouch
    c.drawLine(-40, -305, 35, -190, P(C('#7A4A2C'), 7))
    c.drawOval(skia.Rect(20, -205, 70, -155), P(C('#B9824E')))
    # head
    c.drawRect(skia.Rect(-12, -340, 12, -310), P(C('#9A6640')))
    c.drawCircle(0, -370, 42, P(C('#A86F48')))
    c.drawCircle(14, -375, 5, P(C('#2B1A0E'))); c.drawCircle(-12, -375, 5, P(C('#2B1A0E')))
    c.drawArc(skia.Rect(-14, -362, 16, -340), 20, 140, False, P(C('#4A1E10'), 4))
    c.drawLine(-22, -352, 22, -352, P(C('#3A2A20'), 6))  # moustache
    # turban
    c.drawOval(skia.Rect(-48, -430, 48, -380), P(C('#F28C28')))
    c.drawOval(skia.Rect(-40, -445, 40, -405), P(C('#F6A64A')))
    # arm: swings from -0.3 (back) to 1 (forward throw)
    a = math.radians(lerp(110, -20, arm))
    sx, sy = 35, -295
    ex, ey = sx + math.cos(a) * 130, sy + math.sin(a) * 130
    c.drawLine(sx, sy, ex, ey, P(C('#3C7DBF'), 28))
    c.drawCircle(ex, ey, 17, P(C('#A86F48')))
    c.restore()
    return (x + ex, gy + ey)

def bubble(c, x, y, r, a=1.0):
    p = P(C('#FFFFFF', int(240 * a)))
    c.drawCircle(x, y, r, p)
    c.drawCircle(x - r * .9, y + r * 1.05, r * .16, p); c.drawCircle(x - r * 1.2, y + r * 1.4, r * .1, p)
    c.drawCircle(x, y, r, P(C('#BFD3E6', int(255 * a)), 4))

def caterpillar(c, x, y, t, s=1.0):
    for i in range(5):
        c.drawCircle(x + (i - 2) * 26 * s, y + math.sin(t * 6 + i) * 6 * s, 18 * s, P(C('#7BC043' if i % 2 else '#62A834')))
    hx = x + 2.8 * 26 * s
    c.drawCircle(hx, y - 4 * s, 21 * s, P(C('#62A834')))
    c.drawCircle(hx + 6 * s, y - 10 * s, 5 * s, P(C('#1E1E1E')))
    path = skia.Path(); path.moveTo(hx + 8 * s, y + 4 * s); path.quadTo(hx + 16 * s, y + 10 * s, hx + 20 * s, y + 2 * s)
    c.drawPath(path, P(C('#1E1E1E'), 3))
    c.drawLine(hx, y - 22 * s, hx - 6 * s, y - 40 * s, P(C('#1E1E1E'), 3))

def wind(c, x, y, t, s=1.0):
    wp = P(C('#7FA6C8'), 7)
    for i, (dy, ln) in enumerate([(-35, 150), (0, 190), (35, 130)]):
        off = ((t * 220 + i * 60) % 80) - 40
        path = skia.Path(); path.moveTo(x - ln / 2 * s + off, y + dy * s)
        path.lineTo(x + ln / 2 * s + off - 30, y + dy * s)
        path.quadTo(x + ln / 2 * s + off, y + dy * s, x + ln / 2 * s + off, y + dy * s - 18 * s)
        c.drawPath(path, wp)

def clock(c, x, y, r, t):
    c.drawCircle(x, y, r, P(C('#FFF8E1'))); c.drawCircle(x, y, r, P(C('#C9A227'), 6))
    for i in range(12):
        a = i * math.pi / 6
        c.drawLine(x + math.cos(a) * r * .8, y + math.sin(a) * r * .8, x + math.cos(a) * r * .9, y + math.sin(a) * r * .9, P(C('#6B5A2A'), 4))
    a1 = t * 3; a2 = t * .4
    c.drawLine(x, y, x + math.cos(a1) * r * .7, y + math.sin(a1) * r * .7, P(C('#333333'), 4))
    c.drawLine(x, y, x + math.cos(a2) * r * .45, y + math.sin(a2) * r * .45, P(C('#333333'), 6))

random.seed(5)
DROPS = [(random.uniform(0, W), random.uniform(0, 1), random.uniform(0.8, 1.2)) for _ in range(160)]
def rain(c, t, a):
    if a <= 0: return
    p = P(C('#BFE3FF', int(200 * a)), 3)
    for x, ph, sp in DROPS:
        yy = ((ph + t * 1.6 * sp) % 1.0) * (GY + 40) - 40
        c.drawLine(x - yy * .08, yy, x - yy * .08 - 6, yy + 26, p)

def dirt_bits(c, x, y, t, a):
    if a <= 0: return
    random.seed(int(t * 8))
    for i in range(7):
        ph = (t * 3 + i / 7) % 1
        dx = (i - 3) * 22 + ph * 40 * (1 if i % 2 else -1)
        dy = -math.sin(ph * math.pi) * 80
        c.drawCircle(x + dx, y + dy, 7, P(C('#8A5A3B', int(255 * a))))
