import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gart import *   # W, H, GY, C, P, lerp, ease, clamp, sky, street, face, mouth, bubble, sparkle, draw_key, blend, sun, cloud

def man(c, x, gy, s=1.0, mood='neutral', talk=False, t=0.0, look=(0, 0), old=0.0, kurta='#4A90D9', pants='#3A3A4A',
        turban=None, staff=False, arm='down', skin='#B57A50', facing=1):
    s *= 1.15
    c.save(); c.translate(x, gy); c.scale(s * facing, s)
    c.drawRect(skia.Rect(-50, -230, 50, -20), P(C(pants)))
    c.drawLine(-22, -25, -26, 0, P(C(pants), 22)); c.drawLine(22, -25, 26, 0, P(C(pants), 22))
    c.drawOval(skia.Rect(-56, -12, -8, 6), P(C('#3A2A20'))); c.drawOval(skia.Rect(8, -12, 56, 6), P(C('#3A2A20')))
    k = skia.Path(); k.moveTo(-72, -200); k.lineTo(-60, -420); k.quadTo(0, -445, 60, -420); k.lineTo(72, -200); k.close()
    c.drawPath(k, P(C(kurta)))
    c.drawLine(0, -430, 0, -340, P(C('#000000', 40), 4))
    ap = P(C(kurta), 32)
    if arm == 'chin':
        c.drawLine(-60, -400, -30, -320, ap); c.drawLine(-30, -320, 10, -455, ap); c.drawCircle(14, -468, 20, P(C(skin)))
        c.drawLine(60, -400, 78, -250, ap); c.drawCircle(80, -238, 20, P(C(skin)))
    elif arm == 'point':
        c.drawLine(60, -400, 170, -380, ap); c.drawCircle(182, -380, 20, P(C(skin)))
        c.drawLine(-60, -400, -78, -250, ap); c.drawCircle(-80, -238, 20, P(C(skin)))
    else:
        c.drawLine(-60, -400, -78, -250, ap); c.drawCircle(-80, -238, 20, P(C(skin)))
        c.drawLine(60, -400, 78, -250, ap); c.drawCircle(80, -238, 20, P(C(skin)))
    if staff:
        c.drawLine(80, -238, 95, -520, P(C('#6B4226'), 10)); c.drawLine(95, -520, 120, -540, P(C('#9AA0A6'), 7))
    c.drawRect(skia.Rect(-16, -470, 16, -425), P(C(skin)))
    cy = -545
    hair = blend('#2A2420', '#D8D8D8', old)
    c.drawOval(skia.Rect(-76, cy - 84, 76, cy + 10), P(C(hair)))
    face(c, 0, cy, 70, skin, mood, talk, t, look)
    if turban:
        c.drawOval(skia.Rect(-82, cy - 115, 82, cy - 35), P(C(turban)))
        c.drawOval(skia.Rect(-64, cy - 132, 64, cy - 70), P(C(blend(turban, '#FFFFFF', .2))))
    else:
        c.drawOval(skia.Rect(-66, cy - 88, 66, cy - 42), P(C(hair)))
    if old > .3:
        m = skia.Path(); m.moveTo(-40, cy + 30); m.quadTo(-20, cy + 12, 0, cy + 24); m.quadTo(20, cy + 12, 40, cy + 30); m.quadTo(0, cy + 34, -40, cy + 30)
        c.drawPath(m, P(C(hair)))
    mouth(c, 0, cy + 36, 70, mood, talk, t)
    c.restore()

def elephant(c, x, gy, s=1.0, t=0.0, pull=0.0, sad=0.0, look=(-1, 0), ear_speed=1.0, blink_off=0.0, sit=0.0, tint=None):
    """side view, facing left. pull: 0..1 leaning right (straining against rope)."""
    body = tint or '#9AA3AD'; dark = blend(body, '#4A5058', .35); light = blend(body, '#FFFFFF', .25)
    c.save(); c.translate(x, gy); c.scale(s, s)
    lean = pull * 40 * (0.7 + 0.3 * math.sin(t * 14))
    c.translate(lean, 0)
    sy = sit * 90
    # legs (back legs at right)
    for lx, col in [(150, dark), (-120, dark), (190, body), (-80, body)]:
        top = -230 + sy * .2
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(lx - 42, top, lx + 42, -sit * 30), 30, 30), P(C(col)))
        for nx in (-22, 0, 22): c.drawCircle(lx + nx, -12 - sit * 30, 9, P(C('#F1E6D6')))
    # tail
    tp = skia.Path(); tp.moveTo(250, -330 + sy); tp.quadTo(300, -280 + sy + math.sin(t * 3) * 15, 285, -200 + sy)
    c.drawPath(tp, P(C(dark), 10)); c.drawCircle(285, -195 + sy, 12, P(C('#4A5058')))
    # body
    c.drawOval(skia.Rect(-210, -470 + sy, 270, -190 + sy), P(C(body)))
    c.drawOval(skia.Rect(-150, -455 + sy, 160, -380 + sy), P(C(light, 120)))
    # head
    hx, hy = -230, -400 + sy + sad * 25
    # ear (flaps)
    ef = math.sin(t * 2.5 * ear_speed) * 0.08
    c.save(); c.translate(hx + 75, hy - 15); c.scale(1 + ef, 1)
    c.drawOval(skia.Rect(-30, -120, 135, 135), P(C(dark)))
    c.drawOval(skia.Rect(-5, -95, 115, 115), P(C('#C9A3A8', 140)))
    c.restore()
    c.drawCircle(hx, hy, 130, P(C(body)))
    # trunk
    sw = math.sin(t * 1.8) * 20 * (1 - sad)
    tr = skia.Path(); tr.moveTo(hx - 110, hy + 20)
    if pull > .3:
        tr.cubicTo(hx - 210, hy + 40, hx - 260, hy - 60, hx - 300, hy - 140)
    else:
        tr.cubicTo(hx - 190, hy + 120, hx - 170 + sw, hy + 250, hx - 210 + sw, hy + 330 - sad * 40)
    c.drawPath(tr, P(C(body), 58))
    for i in range(5):
        f = 0.25 + i * 0.15
        if pull > .3:
            px, py = lerp(hx - 130, hx - 280, f), lerp(hy + 30, hy - 110, f)
        else:
            px, py = lerp(hx - 130, hx - 200 + sw, f), lerp(hy + 60, hy + 300, f)
        c.drawLine(px - 22, py, px + 22, py, P(C(dark, 120), 4))
    # tusk
    tk = skia.Path(); tk.moveTo(hx - 80, hy + 60); tk.quadTo(hx - 130, hy + 110, hx - 175, hy + 90); tk.quadTo(hx - 125, hy + 85, hx - 95, hy + 45); tk.close()
    c.drawPath(tk, P(C('#FFF8E8')))
    # eye
    ex, ey = hx - 55, hy - 30
    bl = ((t + blink_off) % 4.1) < .12
    if bl:
        c.drawLine(ex - 14, ey, ex + 14, ey, P(C('#2B1A0E'), 5))
    else:
        c.drawOval(skia.Rect(ex - 16, ey - 18, ex + 16, ey + 18), P(C('#FFFFFF')))
        c.drawCircle(ex + look[0] * 5, ey + look[1] * 5 + 3, 10, P(C('#2B1A0E')))
        c.drawCircle(ex + look[0] * 5 + 3, ey + look[1] * 5, 3, P(C('#FFFFFF')))
    bp = P(C('#4A5058'), 6)
    if sad > .3: c.drawLine(ex - 22, ey - 32, ex + 18, ey - 22, bp)
    elif pull > .3: c.drawLine(ex - 22, ey - 22, ex + 18, ey - 34, bp)
    c.drawCircle(hx - 20, hy + 40, 18, P(C('#E8A0A8', 100)))
    # strain drops
    if pull > .3:
        for i in range(3):
            ph = (t * 2 + i / 3) % 1
            c.drawOval(skia.Rect(hx + 40 + i * 30, hy - 160 - ph * 60, hx + 54 + i * 30, hy - 136 - ph * 60), P(C('#8FD3FF', int(255 * (1 - ph)))))
    c.restore()
    return (x + (190 + lean) * s, gy - 60 * s)   # rope point: back leg ankle

def peg(c, x, gy, s=1.0):
    c.save(); c.translate(x, gy); c.scale(s, s)
    c.drawRect(skia.Rect(-12, -70, 12, 20), P(C('#8B5A33')))
    c.drawOval(skia.Rect(-16, -82, 16, -64), P(C('#A06A3E')))
    c.drawOval(skia.Rect(-40, 8, 40, 26), P(C('#00000', 50)) if False else P(C('#000000', 40)))
    c.restore()
    return (x, gy - 40 * s)

def rope(c, a, b, slack=1.0, w=9, glow=0.0):
    p = skia.Path(); p.moveTo(*a)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 40 * slack
    p.quadTo(mx, my, *b)
    if glow > 0: c.drawPath(p, P(C('#FFD54F', int(180 * glow)), w + 18))
    c.drawPath(p, P(C('#C8A26A'), w))
    c.drawPath(p, P(C('#8A6A3A'), 2, cap=False))

def bunting(c, y, t):
    p = skia.Path(); p.moveTo(-20, y)
    p.quadTo(W / 2, y + 90, W + 20, y); c.drawPath(p, P(C('#6B4226'), 3))
    cols = ['#E53935', '#FDD835', '#43A047', '#1E88E5', '#FB8C00', '#8E24AA']
    for i in range(14):
        f = i / 13; xx = lerp(0, W, f); yy = y + 90 * 4 * f * (1 - f) * .5 * 2 * .5 + 4
        sw = math.sin(t * 3 + i) * 4
        tri = skia.Path(); tri.moveTo(xx - 26, yy); tri.lineTo(xx + 26, yy); tri.lineTo(xx + sw, yy + 56); tri.close()
        c.drawPath(tri, P(C(cols[i % 6])))

def tent(c, x, gy, s, c1, c2):
    c.save(); c.translate(x, gy); c.scale(s, s)
    c.drawRect(skia.Rect(-160, -220, 160, 0), P(C(c2)))
    for i in range(-160, 160, 64): c.drawRect(skia.Rect(i, -220, i + 32, 0), P(C(c1)))
    rf = skia.Path(); rf.moveTo(-200, -220); rf.lineTo(0, -380); rf.lineTo(200, -220); rf.close(); c.drawPath(rf, P(C(c1)))
    c.drawLine(0, -380, 0, -440, P(C('#6B4226'), 6))
    fl = skia.Path(); fl.moveTo(0, -440); fl.lineTo(50, -425); fl.lineTo(0, -410); fl.close(); c.drawPath(fl, P(C('#FDD835')))
    c.drawRect(skia.Rect(-45, -120, 45, 0), P(C('#3A2A20', 160)))
    c.restore()

def ferris(c, x, y, r, t, a=1.0):
    p = P(C('#B0BEC5', int(255 * a)), 6)
    c.drawCircle(x, y, r, p)
    for i in range(8):
        ang = t * .3 + i * math.pi / 4
        cx, cy = x + math.cos(ang) * r, y + math.sin(ang) * r
        c.drawLine(x, y, cx, cy, P(C('#B0BEC5', int(255 * a)), 3))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - 18, cy, cx + 18, cy + 26), 6, 6), P(C(['#E53935', '#FDD835', '#1E88E5', '#43A047'][i % 4], int(255 * a))))
    c.drawLine(x, y, x - r * .6, y + r * 1.4, p); c.drawLine(x, y, x + r * .6, y + r * 1.4, p)

def mela_bg(c, t, dark=0.0):
    sky(c, 'day'); sun(c, 900, 200, 70)
    cloud(c, (200 + t * 12) % (W + 300) - 150, 260, .8)
    ferris(c, 820, 640, 190, t, 0.9)
    tent(c, 200, GY, 0.95, '#E53935', '#FFF3E0'); tent(c, 640, GY, 0.75, '#1E88E5', '#FFF8E1')
    bunting(c, 120, t)
    street(c, dark)
