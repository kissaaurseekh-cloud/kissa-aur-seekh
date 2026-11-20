import skia, math, random, sys, os
sys.path.insert(0, '/home/claude/kissa-aur-seekh/engine')
from gart import C, P, lerp, ease, clamp, mixc, blend, sun, cloud, face, mouth, ramu, seth, house, draw_key, bubble, sparkle, brick_pile, cement_bag, sand_heap, heart
from hart import man
from tart import boy

LW, LH, LGY = 1920, 1080, 900
SKY = {'day': ('#79C3F0', '#DDF2FF'), 'dusk': ('#3B3561', '#E88A5A'), 'storm': ('#1E2236', '#4A5068'),
       'warm': ('#F4A261', '#FFE3B3'), 'sad': ('#5B6C8C', '#B8C4D6'), 'rain': ('#3E4A60', '#7D8AA0'), 'morning': ('#9CCFF0', '#FFF1D6')}

def lsky(c, mood='day'):
    a, b = SKY[mood]
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, LGY)], [C(a), C(b)]))
    c.drawRect(skia.Rect(0, 0, LW, LGY + 5), p)

def lground(c, dark=0.0, wet=0.0):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, LGY), skia.Point(0, LH)],
        [mixc('#D9B382', '#4A3E32', dark), mixc('#B98D5E', '#30281F', dark)]))
    c.drawRect(skia.Rect(0, LGY, LW, LH), p)
    c.drawRect(skia.Rect(0, LGY - 6, LW, LGY + 12), P(mixc('#9C7B55', '#3A3028', dark)))
    random.seed(2)
    for i in range(60):
        x = random.uniform(0, LW); y = random.uniform(LGY + 30, LH)
        c.drawOval(skia.Rect.MakeXYWH(x, y, 16, 7), P(mixc('#A67C52', '#2E2620', dark), alpha=.6))
    if wet > 0:
        random.seed(6)
        for i in range(9):
            x = random.uniform(100, LW - 100); y = random.uniform(LGY + 40, LH - 60)
            c.drawOval(skia.Rect(x - 90, y - 14, x + 90, y + 14), P(C('#8FB3D0', int(150 * wet))))

def far_houses(c, dark=0.0, y=LGY):
    for i, (x, wl, rf) in enumerate([(120, '#F7D08A', '#C0392B'), (330, '#A8D8C8', '#2E6E8E'), (1650, '#F4B6A6', '#7A3E8E'), (1840, '#D7C4F0', '#5E3B8E')]):
        c.save(); c.translate(x, y); c.scale(0.42, 0.42)
        house(c, 0, 0, 420, 360, wall=wl if dark < .5 else blend(wl, '#2A2A3A', .55), roof=rf if dark < .5 else blend(rf, '#1A1A2A', .5))
        c.restore()

def rain(c, t, a=1.0, wind=0.25):
    if a <= 0: return
    random.seed(5)
    p = P(C('#C8DDF0', int(170 * a)), 3)
    for i in range(260):
        x0 = random.uniform(-200, LW); ph = random.random(); sp = random.uniform(0.8, 1.3)
        yy = ((ph + t * 1.5 * sp) % 1.0) * (LH + 60) - 60
        xx = x0 + yy * wind
        c.drawLine(xx, yy, xx + 34 * wind, yy + 34, p)

def flash(c, t, times, a=200):
    k = 0
    for tt in times: k = max(k, 1 - abs(t - tt) / 0.1)
    if k > 0: c.drawRect(skia.Rect(0, 0, LW, LH), P(C('#FFFFFF', int(a * k))))

def tint(c, col='#704214', a=60, vig=110):
    c.drawRect(skia.Rect(0, 0, LW, LH), P(C(col, a)))
    g = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(skia.Point(LW / 2, LH / 2), 1150, [C('#000000', 0), C('#000000', vig)]))
    c.drawRect(skia.Rect(0, 0, LW, LH), g)

def kamla(c, x, gy, s=1.0, mood='neutral', talk=False, t=0.0, look=(0, 0)):
    s *= 1.15
    c.save(); c.translate(x, gy); c.scale(s, s)
    skin = '#B57A50'
    sk = skia.Path(); sk.moveTo(-60, -250); sk.lineTo(-85, -5); sk.lineTo(85, -5); sk.lineTo(60, -250); sk.close()
    c.drawPath(sk, P(C('#2E7D5B')))
    c.drawRect(skia.Rect(-85, -40, 85, -12), P(C('#E0A526')))           # border
    c.drawOval(skia.Rect(-48, -14, -6, 4), P(C('#5A3A22'))); c.drawOval(skia.Rect(6, -14, 48, 4), P(C('#5A3A22')))
    bl = skia.Path(); bl.moveTo(-62, -250); bl.lineTo(-55, -410); bl.quadTo(0, -432, 55, -410); bl.lineTo(62, -250); bl.close()
    c.drawPath(bl, P(C('#C2185B')))
    pl = skia.Path(); pl.moveTo(-58, -415); pl.lineTo(40, -250); pl.lineTo(70, -255); pl.lineTo(10, -420); pl.close()
    c.drawPath(pl, P(C('#2E7D5B'))); c.drawLine(-58, -415, 40, -250, P(C('#E0A526'), 6))
    ap = P(C('#C2185B'), 28)
    c.drawLine(-55, -395, -78, -250, ap); c.drawCircle(-80, -238, 18, P(C(skin)))
    c.drawLine(55, -395, 78, -250, ap); c.drawCircle(80, -238, 18, P(C(skin)))
    c.drawRect(skia.Rect(-14, -462, 14, -420), P(C(skin)))
    cy = -530
    c.drawCircle(0, cy - 30, 76, P(C('#5E5A58')))           # grey hair
    c.drawCircle(0, cy - 70, 36, P(C('#5E5A58')))           # bun on top
    face(c, 0, cy, 66, skin, mood, talk, t, look, blink_off=0.8)
    c.drawOval(skia.Rect(-62, cy - 76, 62, cy - 30), P(C('#5E5A58')))
    c.drawCircle(0, cy - 30, 7, P(C('#D32F2F')))             # bindi
    mouth(c, 0, cy + 32, 66, mood, talk, t)
    c.restore()

def bucket(c, x, y, s=1.0, level=0.3):
    c.save(); c.translate(x, y); c.scale(s, s)
    b = skia.Path(); b.moveTo(-45, -80); b.lineTo(45, -80); b.lineTo(35, 0); b.lineTo(-35, 0); b.close()
    c.drawPath(b, P(C('#8E9AA6'))); c.drawOval(skia.Rect(-45, -88, 45, -72), P(C('#6E7A86')))
    c.drawOval(skia.Rect(-40, -86, 40, -74), P(C('#6EC1E4', int(255 * clamp(level * 2)))))
    c.drawArc(skia.Rect(-45, -130, 45, -40), 200, 140, False, P(C('#555555'), 4))
    c.restore()

def drips(c, x, y0, y1, t, a=1.0):
    for i in range(3):
        ph = (t * 1.4 + i / 3) % 1
        yy = lerp(y0, y1, ph)
        c.drawOval(skia.Rect(x - 7, yy, x + 7, yy + 20), P(C('#8FD3FF', int(230 * a))))

def cart(c, x, gy, s=1.0, t=0.0, moving=True):
    c.save(); c.translate(x, gy); c.scale(s, s)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-200, -190, 200, -90), 10, 10), P(C('#8B5A33')))
    c.drawRect(skia.Rect(-200, -200, 200, -186), P(C('#6B4226')))
    c.drawLine(-200, -140, -330, -110, P(C('#6B4226'), 12))
    brick_pile(c, 40, -180, False, 0.8)
    for wx in (-120, 120):
        c.save(); c.translate(wx, -70); c.rotate((t * 120 if moving else 0) % 360)
        c.drawCircle(0, 0, 70, P(C('#5A3A22'), 14))
        for k in range(6): c.drawLine(0, 0, math.cos(k) * 64, math.sin(k) * 64, P(C('#5A3A22'), 7))
        c.restore()
    c.restore()

def plumb(c, x, y, L, t):
    sw = math.sin(t * 2) * 6
    c.drawLine(x, y, x + sw, y + L, P(C('#F5F5F5'), 3))
    pb = skia.Path(); pb.moveTo(x + sw - 12, y + L); pb.lineTo(x + sw + 12, y + L); pb.lineTo(x + sw, y + L + 30); pb.close()
    c.drawPath(pb, P(C('#B0BEC5')))

def big_brick(c, cx, cy, w=900, h=300):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 18, 18), P(C('#B5532F')))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 18, 18), P(C('#7A3418'), 10))
    random.seed(4)
    for i in range(40):
        c.drawCircle(cx + random.uniform(-w / 2 + 20, w / 2 - 20), cy + random.uniform(-h / 2 + 20, h / 2 - 20), random.uniform(2, 5), P(C('#8A3A1C', 160)))
