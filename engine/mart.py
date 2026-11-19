import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gart import *

def room(c, t, morning=0.0, moon_f=0.3):
    wall = mixc('#2B3A5C', '#F3D9A4', morning)
    c.drawRect(skia.Rect(0, 0, W, H), P(wall))
    # window
    wx, wy = 760, 300
    c.drawRect(skia.Rect(wx - 160, wy - 150, wx + 160, wy + 150), P(mixc('#0E1838', '#9AD4F5', morning)))
    if morning < .6:
        mx = lerp(wx - 120, wx + 120, moon_f); my = wy - 40 - math.sin(moon_f * math.pi) * 60
        c.drawCircle(mx, my, 40, P(C('#F4F1DE', int(255 * (1 - morning)))))
        for i in range(8): c.drawCircle(wx - 140 + i * 40, wy - 120 + (i * 53 % 90), 3, P(C('#FFFFFF', int(200 * (1 - morning)))))
    else:
        sun(c, wx + 60, wy + 40, 50, (morning - .6) / .4)
    c.drawRect(skia.Rect(wx - 160, wy - 150, wx + 160, wy + 150), P(C('#6B4226'), 16))
    c.drawLine(wx, wy - 150, wx, wy + 150, P(C('#6B4226'), 10)); c.drawLine(wx - 160, wy, wx + 160, wy, P(C('#6B4226'), 10))
    # floor
    c.drawRect(skia.Rect(0, 1240, W, H), P(mixc('#3A2C22', '#B98D5E', morning)))
    c.drawRect(skia.Rect(0, 1232, W, 1250), P(mixc('#2A1E16', '#8A6440', morning)))
    # lantern glow (night)
    if morning < 1:
        lx, ly = 200, 330
        g = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(skia.Point(lx, ly), 520, [C('#FFC107', int(90 * (1 - morning))), C('#FFC107', 0)]))
        c.drawCircle(lx, ly, 520, g)
        c.drawLine(lx, 160, lx, 260, P(C('#555555'), 4))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(lx - 40, 260, lx + 40, 380), 14, 14), P(C('#8D6E63')))
        c.drawOval(skia.Rect(lx - 22, 285, lx + 22, 355), P(C('#FFD54F', int(255 * (1 - morning * .7)))))

POT_OUT = None
def pot_path(cx, top, w, h):
    p = skia.Path()
    p.moveTo(cx - w * .42, top); p.lineTo(cx + w * .42, top)
    p.cubicTo(cx + w * .42, top + h * .18, cx + w * .62, top + h * .3, cx + w * .58, top + h * .62)
    p.cubicTo(cx + w * .54, top + h * .95, cx + w * .25, top + h, cx, top + h)
    p.cubicTo(cx - w * .25, top + h, cx - w * .54, top + h * .95, cx - w * .58, top + h * .62)
    p.cubicTo(cx - w * .62, top + h * .3, cx - w * .42, top + h * .18, cx - w * .42, top)
    p.close(); return p

def big_pot(c, cx, top, w, h, milk_y, butter=0.0, t=0.0, churn=0.0, draw_front=None):
    outer = pot_path(cx, top, w, h)
    c.drawPath(outer, P(C('#B5782E')))
    inner = pot_path(cx, top + 18, w - 50, h - 40)
    c.drawPath(inner, P(C('#5A3A1A')))
    c.drawPath(outer, P(C('#7A4E1E'), 8))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - w * .46, top - 26, cx + w * .46, top + 18), 20, 20), P(C('#C98B3A')))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - w * .46, top - 26, cx + w * .46, top + 18), 20, 20), P(C('#7A4E1E'), 6))
    return inner

def milk(c, inner, milk_y, t, churn=0.0, butter=0.0, alpha=195):
    c.save(); c.clipPath(inner, doAntiAlias=True)
    wave = skia.Path(); wave.moveTo(0, milk_y)
    for x in range(0, W + 1, 40):
        wave.lineTo(x, milk_y + math.sin(x * .03 + t * 3) * (6 + 10 * churn))
    wave.lineTo(W, H); wave.lineTo(0, H); wave.close()
    c.drawPath(wave, P(mixc('#FFFFFF', '#FFF3C4', butter * .5, alpha)))
    if churn > 0:
        for i in range(8):
            a = t * 3 + i
            c.drawArc(skia.Rect(540 - 200 + i * 20, milk_y + 60 + i * 30, 540 + 200 - i * 20, milk_y + 120 + i * 30), a * 40, 120, False, P(C('#E0E0E0', int(160 * churn)), 5))
    if butter > 0:
        random.seed(3)
        for i in range(int(30 * butter)):
            bx = random.uniform(300, 780); by = milk_y + random.uniform(-10, 40)
            r = random.uniform(14, 40) * (0.4 + butter)
            c.drawCircle(bx, by, r, P(C('#FFE082')))
        if butter > .8:
            c.drawOval(skia.Rect(330, milk_y - 40, 750, milk_y + 70), P(C('#FFD54F')))
            c.drawOval(skia.Rect(380, milk_y - 30, 600, milk_y + 10), P(C('#FFF59D', 200)))
    c.restore()

def frog(c, x, y, s=1.0, mood='happy', talk=False, t=0.0, kick=0.0, look=(0, 0), col='#5CB85C', det=False, closed=False, rot=0.0, legs_out=0.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    dark = blend(col, '#1E3A1E', .35); belly = blend(col, '#FFFFFF', .55)
    # back legs
    k = math.sin(t * 16) * kick
    for sx in (-1, 1):
        kk = k * sx
        c.save(); c.translate(sx * 60, 60)
        c.drawLine(0, 0, sx * 70, 50 + 40 * kk + 40 * legs_out, P(C(dark), 30))
        c.drawLine(sx * 70, 50 + 40 * kk + 40 * legs_out, sx * 30, 110 + 50 * kk + 60 * legs_out, P(C(dark), 24))
        c.drawOval(skia.Rect(sx * 30 - 34, 100 + 50 * kk + 60 * legs_out, sx * 30 + 34, 126 + 50 * kk + 60 * legs_out), P(C(dark)))
        c.restore()
    c.drawOval(skia.Rect(-110, -60, 110, 110), P(C(col)))
    c.drawOval(skia.Rect(-70, 10, 70, 105), P(C(belly)))
    # front arms
    for sx in (-1, 1):
        c.drawLine(sx * 70, 40, sx * 95, 95 - 20 * k * sx, P(C(col), 22))
    # eyes on top
    for sx in (-1, 1):
        ex = sx * 52
        c.drawCircle(ex, -62, 44, P(C(col)))
        if closed or ((t + (0.9 if col != '#5CB85C' else 0)) % 3.8) < .12:
            c.drawArc(skia.Rect(ex - 26, -76, ex + 26, -50), 20, 140, False, P(C('#1E1E1E'), 5))
        else:
            c.drawCircle(ex, -64, 32, P(C('#FFFFFF')))
            c.drawCircle(ex + look[0] * 9, -64 + look[1] * 9, 16, P(C('#1E1E1E')))
            c.drawCircle(ex + look[0] * 9 + 5, -69 + look[1] * 9, 5, P(C('#FFFFFF')))
        bp = P(C('#1E3A1E'), 7)
        if det: c.drawLine(ex - sx * 30, -112, ex + sx * 26, -100, bp)
        elif mood == 'sad': c.drawLine(ex - sx * 30, -98, ex + sx * 26, -110, bp)
    c.drawCircle(-62, 20, 14, P(C('#F08A7A', 130))); c.drawCircle(62, 20, 14, P(C('#F08A7A', 130)))
    o = (abs(math.sin(t * 12)) * .8 + .2) if talk else 0
    mp = P(C('#1E3A1E'), 6)
    if o > .3: c.drawOval(skia.Rect(-30, 4, 30, 10 + 34 * o), P(C('#7A2A2A')))
    elif mood == 'happy' or det: c.drawArc(skia.Rect(-55, -20, 55, 30), 25, 130, False, mp)
    elif mood == 'sad': c.drawArc(skia.Rect(-35, 12, 35, 44), 205, 130, False, mp)
    elif mood == 'shocked': c.drawOval(skia.Rect(-18, 0, 18, 36), P(C('#7A2A2A')))
    else: c.drawLine(-30, 12, 30, 12, mp)
    c.restore()

def splash(c, x, y, k, col='#FFFFFF'):
    if k <= 0 or k >= 1: return
    for i in range(10):
        a = math.pi + i / 9 * math.pi
        r = 40 + 200 * k
        c.drawCircle(x + math.cos(a) * r, y + math.sin(a) * r * .8 - 120 * math.sin(k * math.pi), 16 * (1 - k), P(C(col)))

def bubbles(c, x, y, t, a=1.0):
    for i in range(6):
        ph = (t * 0.8 + i / 6) % 1
        c.drawCircle(x + math.sin(i * 2 + t) * 30, y - ph * 260, 8 + i % 3 * 4, P(C('#FFFFFF', int(200 * a * (1 - ph))), 3))
