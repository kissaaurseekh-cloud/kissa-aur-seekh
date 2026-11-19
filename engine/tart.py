import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hart import man
from gart import *

def garden(c, t, mood='day', dark=0.0):
    sky(c, mood)
    if mood == 'day': sun(c, 880, 220, 70)
    if mood != 'dusk':
        cloud(c, (180 + t * 12) % (W + 300) - 150, 280, .8)
    # back hedge + trees
    for x, r, col in [(120, 200, '#4E9A47'), (420, 170, '#5BAA4F'), (760, 210, '#4E9A47'), (1020, 180, '#5BAA4F')]:
        c.drawCircle(x, GY - 120, r, P(mixc(col, '#1E3A22', dark)))
    c.drawRect(skia.Rect(0, GY - 160, W, GY), P(mixc('#5DAF4E', '#1E3A22', dark)))
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, GY), skia.Point(0, H)], [mixc('#7CC35E', '#2A4A2E', dark), mixc('#5E9E46', '#1E3422', dark)]))
    c.drawRect(skia.Rect(0, GY, W, H), p)
    random.seed(9)
    for i in range(26):
        x = random.uniform(0, W); y = random.uniform(GY - 140, GY + 40)
        col = random.choice(['#E91E63', '#FFEB3B', '#FFFFFF', '#AB47BC', '#FF7043'])
        for k in range(5):
            a = k * 1.2566; c.drawCircle(x + math.cos(a) * 9, y + math.sin(a) * 9, 8, P(mixc(col, '#2A2A2A', dark * .7)))
        c.drawCircle(x, y, 5, P(C('#FFD54F')))

def branch(c, x0, y0, x1, y1, w=26):
    p = skia.Path(); p.moveTo(x0, y0); p.quadTo((x0 + x1) / 2, (y0 + y1) / 2 - 40, x1, y1)
    c.drawPath(p, P(C('#7A4E2D'), w))
    for f, side in [(.3, -1), (.6, 1), (.85, -1)]:
        lx = lerp(x0, x1, f); ly = lerp(y0, y1, f) - 30
        c.save(); c.translate(lx, ly); c.rotate(-60 * side)
        lf = skia.Path(); lf.moveTo(0, 0); lf.quadTo(50, -40, 120, 0); lf.quadTo(50, 40, 0, 0)
        c.drawPath(lf, P(C('#5FBF4A'))); c.drawLine(4, 0, 110, 0, P(C('#3F8F32'), 3)); c.restore()

def cocoon(c, x, y, s=1.0, t=0.0, wiggle=0.0, hole=0.0, peek=0.0, cut=0.0, strain=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawLine(0, -170, 0, -120, P(C('#D7CCC8'), 4))
    c.rotate(math.sin(t * 9) * 6 * wiggle)
    if cut > 0:
        for sx in (-1, 1):
            c.save(); c.rotate(sx * 18 * cut); c.translate(sx * 20 * cut, 0)
            half = skia.Path(); half.moveTo(0, -125); half.quadTo(sx * 75, -60, sx * 55, 60); half.quadTo(sx * 30, 115, 0, 120); half.close()
            c.drawPath(half, P(C('#A1B56C'))); c.drawPath(half, P(C('#6E8040'), 4))
            c.restore()
    else:
        body = skia.Path(); body.addOval(skia.Rect(-62, -125, 62, 125))
        c.drawPath(body, P(C('#A1B56C')))
        for i in range(6):
            yy = -95 + i * 36; c.drawArc(skia.Rect(-58, yy - 12, 58, yy + 12), 10, 160, False, P(C('#7F9450'), 4))
        c.drawPath(body, P(C('#6E8040'), 4))
        if hole > 0:
            c.drawOval(skia.Rect(-26 * hole, 84, 26 * hole, 122), P(C('#3E2A1A')))
            if peek > 0:
                # butterfly head pushing out
                hy = 112 + 18 * peek + math.sin(t * 14) * 5 * strain
                c.drawCircle(0, hy, 22, P(C('#3A2A3A')))
                c.drawCircle(-8, hy - 4, 6, P(C('#FFFFFF'))); c.drawCircle(8, hy - 4, 6, P(C('#FFFFFF')))
                c.drawCircle(-8, hy - 3, 3, P(C('#000000'))); c.drawCircle(8, hy - 3, 3, P(C('#000000')))
                c.drawLine(-8, hy + 16, -26, hy + 42, P(C('#3A2A3A'), 3)); c.drawLine(8, hy + 16, 26, hy + 42, P(C('#3A2A3A'), 3))
                if strain > 0:
                    for i in range(3):
                        ph = (t * 2 + i / 3) % 1
                        c.drawOval(skia.Rect(30 + i * 16, hy - 30 - ph * 30, 40 + i * 16, hy - 14 - ph * 30), P(C('#8FD3FF', int(255 * (1 - ph)))))
    c.restore()

def butterfly(c, x, y, s=1.0, t=0.0, flap=1.0, crumpled=0.0, mood='happy', rot=0.0, cols=('#FF8A00', '#FFB74D', '#6A1B9A')):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    f = 1.0 - flap * 0.65 * (0.5 + 0.5 * math.sin(t * 14)) if crumpled < .5 else 1.0 - 0.15 * (0.5 + 0.5 * math.sin(t * 5)) * flap
    wc1 = mixc(cols[0], '#A1887F', crumpled * .55); wc2 = mixc(cols[1], '#BCAAA4', crumpled * .55); edge = C(cols[2]) if crumpled < .5 else C('#616161')
    ws = lerp(1.0, 0.42, crumpled)
    cr = crumpled > .5
    for sx in (-1, 1):
        c.save(); c.scale(sx * f, 1)
        if cr: c.rotate(28); c.scale(0.62, 0.62)
        up = skia.Path(); up.moveTo(8, -10)
        up.cubicTo(60, -140, 200, -130, 180, -40); up.quadTo(150, 10, 8, 4); up.close()
        c.drawPath(up, P(wc1)); c.drawPath(up, P(edge, 6))
        lo = skia.Path(); lo.moveTo(8, 8)
        lo.cubicTo(120, 20, 150, 120, 70, 130); lo.quadTo(20, 120, 8, 8); lo.close()
        c.drawPath(lo, P(wc2)); c.drawPath(lo, P(edge, 6))
        if cr:
            wp = P(C('#5D4037', 200), 5)
            for (x0, y0, x1, y1) in [(40, -40, 150, -90), (60, -10, 170, -40), (30, 30, 110, 100), (20, -70, 90, -110)]:
                pth = skia.Path(); pth.moveTo(x0, y0); pth.lineTo((x0 + x1) / 2, (y0 + y1) / 2 + 14); pth.lineTo(x1, y1); c.drawPath(pth, wp)
        else:
            c.drawCircle(110, -60, 18, P(C('#FFFFFF', 200))); c.drawCircle(70, 70, 12, P(C('#FFFFFF', 180)))
        c.restore()
    bw = lerp(14, 26, crumpled)
    c.drawOval(skia.Rect(-bw, -40, bw, 90 + 20 * crumpled), P(C('#3A2A3A')))
    c.drawCircle(0, -58, 26, P(C('#3A2A3A')))
    c.drawLine(-8, -78, -40, -130, P(C('#3A2A3A'), 4)); c.drawLine(8, -78, 40, -130, P(C('#3A2A3A'), 4))
    c.drawCircle(-40, -130, 7, P(C('#3A2A3A'))); c.drawCircle(40, -130, 7, P(C('#3A2A3A')))
    for ex in (-10, 10):
        c.drawCircle(ex, -62, 8, P(C('#FFFFFF'))); c.drawCircle(ex, -60, 4, P(C('#000000')))
    mp = P(C('#FFFFFF'), 3)
    if mood == 'sad': c.drawArc(skia.Rect(-9, -48, 9, -36), 200, 140, False, mp)
    else: c.drawArc(skia.Rect(-9, -54, 9, -40), 20, 140, False, mp)
    c.restore()

def scissors(c, x, y, s=1.0, open_=0.5, rot=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    a = 18 * open_
    for sx, col in ((1, '#B0BEC5'), (-1, '#90A4AE')):
        c.save(); c.rotate(sx * a)
        bl = skia.Path(); bl.moveTo(0, 0); bl.lineTo(-170, sx * 10); bl.lineTo(-170, sx * -2); bl.close()
        c.drawPath(bl, P(C(col)))
        c.drawCircle(70, sx * 30, 34, P(C('#E53935'), 14))
        c.drawLine(0, 0, 45, sx * 22, P(C('#E53935'), 14))
        c.restore()
    c.drawCircle(0, 0, 8, P(C('#455A64')))
    c.restore()

def boy(c, x, gy, s=1.0, mood='neutral', talk=False, t=0.0, look=(0, 0), arm='down', facing=1):
    man(c, x, gy, s * 0.78, mood, talk, t, look, old=0, kurta='#E53935', pants='#37474F', arm=arm, skin='#C68B5A', facing=facing)

def dadaji(c, x, gy, s=1.0, mood='happy', talk=False, t=0.0, look=(0, 0), facing=-1):
    man(c, x, gy, s, mood, talk, t, look, old=1, kurta='#F5F5F5', pants='#E0E0E0', skin='#A8714A', facing=facing)
    hs = s * 1.15; hx, hy = x, gy - 545 * hs
    gp = P(C('#3A2A20'), 5)
    for ex in (-25, 25):
        c.drawCircle(hx + ex * hs, hy - 8 * hs, 20 * hs, gp)
    c.drawLine(hx - 5 * hs, hy - 8 * hs, hx + 5 * hs, hy - 8 * hs, gp)
