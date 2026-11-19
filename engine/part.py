import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gart import *   # W, H, GY, C, P, lerp, ease, clamp, sky, face, mouth, bubble, sparkle, blend, sun, cloud

HZ = 700  # horizon
PL = lambda y: lerp(470, 40, (y - HZ) / (H - HZ))    # path left edge x at y
PR = lambda y: lerp(610, 1040, (y - HZ) / (H - HZ))  # path right edge

def village(c, t, mood='day', scroll=0.0, dry=0.6):
    sky(c, mood)
    if mood == 'day': sun(c, 860, 230, 70)
    if mood in ('day', 'warm'):
        for i, (x0, y0, s) in enumerate([(160, 260, .8), (700, 420, .6)]):
            cloud(c, (x0 + t * 12) % (W + 300) - 150, y0, s)
    # far hills + river
    hp = skia.Path(); hp.moveTo(0, HZ); hp.quadTo(250, 540, 520, 640); hp.quadTo(800, 520, 1080, 620); hp.lineTo(1080, HZ); hp.close()
    c.drawPath(hp, P(C('#8CC27A' if mood != 'dusk' else '#4E6B52')))
    c.drawRect(skia.Rect(0, HZ - 28, W, HZ + 6), P(C('#6EC1E4' if mood != 'dusk' else '#3E6A8A')))
    for i in range(6):
        x = (i * 190 + t * 40) % (W + 100) - 50
        c.drawLine(x, HZ - 14, x + 50, HZ - 14, P(C('#FFFFFF', 150), 3))
    # fields left (green) / right (dry)
    c.drawRect(skia.Rect(0, HZ, W, H), P(C('#8DBF5E')))
    rp = skia.Path(); rp.moveTo(540, HZ); rp.lineTo(W, HZ); rp.lineTo(W, H); rp.lineTo(PR(H), H); rp.close()
    c.drawPath(rp, P(mixc('#8DBF5E', '#C9A86A', dry)))
    # huts far
    for hx, s in [(140, .55), (930, .5)]:
        c.save(); c.translate(hx, HZ + 30); c.scale(s, s)
        c.drawRect(skia.Rect(-80, -110, 80, 0), P(C('#D9B382')))
        rf = skia.Path(); rf.moveTo(-110, -105); rf.lineTo(0, -190); rf.lineTo(110, -105); rf.close(); c.drawPath(rf, P(C('#A0522D')))
        c.drawRect(skia.Rect(-20, -60, 20, 0), P(C('#5A3A22')))
        c.restore()
    # path
    pp = skia.Path(); pp.moveTo(PL(HZ), HZ); pp.lineTo(PR(HZ), HZ); pp.lineTo(PR(H), H); pp.lineTo(PL(H), H); pp.close()
    c.drawPath(pp, P(C('#D8B47E')))
    random.seed(8)
    for i in range(40):
        f = ((random.random() + scroll) % 1.0) ** 1.6
        y = lerp(HZ + 10, H, f); x = lerp(PL(y) + 30, PR(y) - 30, random.random())
        r = 4 + 14 * f
        c.drawOval(skia.Rect(x - r * 1.5, y - r * .6, x + r * 1.5, y + r * .6), P(C('#B9925E', 160)))
    if dry > 0.3:
        random.seed(13)
        cp = P(C('#8A6A3A', int(200 * dry)), 3)
        for i in range(18):
            f = random.random() ** 1.3; y = lerp(HZ + 30, H, f); x = lerp(PR(y) + 20, W, random.random())
            path = skia.Path(); path.moveTo(x, y)
            for k in range(4): x += random.uniform(-25, 25) * (0.5 + f); y += random.uniform(-6, 10) * (0.5 + f); path.lineTo(x, y)
            c.drawPath(path, cp)

def flower(c, x, y, s, col, grow=1.0, t=0.0):
    if grow <= 0: return
    g = ease(grow); s = s * g
    c.drawLine(x, y, x, y - 60 * s, P(C('#3E8E41'), max(2, 6 * s)))
    c.save(); c.translate(x, y - 60 * s); c.rotate(math.sin(t * 2 + x) * 6)
    for i in range(5):
        a = i * 72 * math.pi / 180
        c.drawCircle(math.cos(a) * 16 * s, math.sin(a) * 16 * s, 14 * s, P(C(col)))
    c.drawCircle(0, 0, 10 * s, P(C('#FFD54F')))
    c.restore()

random.seed(31)
FLOWERS = []
for i in range(46):
    f = random.random() ** 1.2; y = lerp(HZ + 20, H - 20, f)
    x = lerp(PL(y) - 18 - 160 * f, PL(y) - 6, random.random())
    FLOWERS.append((x, y, 0.4 + 1.4 * f, random.choice(['#E91E63', '#FF7043', '#AB47BC', '#FFEB3B', '#FFFFFF', '#42A5F5']), random.random()))
FLOWERS.sort(key=lambda z: z[1])
def flowers(c, k, t, spread=0.6):
    for x, y, s, col, d in FLOWERS:
        flower(c, x, y, s, col, clamp((k - d * spread) / 0.35), t)

def pot(c, x, y, s=1.0, cracked=False, mood='neutral', talk=False, t=0.0, drip=0.0, tear=0.0, look=(0, 0)):
    c.save(); c.translate(x, y); c.scale(s, s)
    body = '#C8693E'; dark = '#9A4A28'
    c.drawOval(skia.Rect(-95, -80, 95, 105), P(C(body)))
    c.drawRect(skia.Rect(-45, -115, 45, -70), P(C(body)))
    c.drawOval(skia.Rect(-62, -135, 62, -105), P(C(dark)))
    c.drawOval(skia.Rect(-48, -130, 48, -112), P(C('#4A2A16')))
    c.drawArc(skia.Rect(-88, -20, 88, 50), 20, 140, False, P(C('#E8A070'), 5))
    c.drawOval(skia.Rect(-70, -60, -20, -10), P(C('#E89A6A', 120)))
    # face
    ey = -10; bl = ((t + (1.3 if cracked else 0)) % 3.6) < .12
    for ex in (-30, 30):
        if bl: c.drawLine(ex - 10, ey, ex + 10, ey, P(C('#2B1A0E'), 4))
        else:
            c.drawOval(skia.Rect(ex - 13, ey - 15, ex + 13, ey + 15), P(C('#FFFFFF')))
            c.drawCircle(ex + look[0] * 4, ey + 2 + look[1] * 4, 7, P(C('#2B1A0E')))
            c.drawCircle(ex + look[0] * 4 + 3, ey - 1 + look[1] * 4, 2.5, P(C('#FFFFFF')))
    bp = P(C('#4A2A16'), 5)
    if mood == 'sad':
        c.drawLine(-44, -26, -18, -34, bp); c.drawLine(44, -26, 18, -34, bp)
    elif mood == 'proud':
        c.drawLine(-44, -36, -16, -30, bp); c.drawLine(44, -36, 16, -30, bp)
        c.drawLine(-44, ey - 2, -16, ey - 2, P(C(body), 9)); c.drawLine(16, ey - 2, 44, ey - 2, P(C(body), 9))  # half-lidded smug
    elif mood == 'shocked':
        c.drawLine(-44, -40, -16, -44, bp); c.drawLine(44, -40, 16, -44, bp)
    c.drawCircle(-50, 22, 11, P(C('#F08A7A', 140))); c.drawCircle(50, 22, 11, P(C('#F08A7A', 140)))
    mp = P(C('#4A1E10'), 5)
    o = (abs(math.sin(t * 12)) * .8 + .2) if talk else 0
    if o > .3: c.drawOval(skia.Rect(-12, 26, 12, 30 + 22 * o), P(C('#6A2414')))
    elif mood in ('happy', 'proud'): c.drawArc(skia.Rect(-22, 10, 22, 40), 20, 140, False, mp)
    elif mood == 'shocked': c.drawOval(skia.Rect(-12, 24, 12, 50), P(C('#6A2414')))
    elif mood == 'sad': c.drawArc(skia.Rect(-18, 30, 18, 52), 200, 140, False, mp)
    else: c.drawLine(-12, 36, 12, 36, mp)
    if cracked:
        cr = skia.Path(); cr.moveTo(30, -70); cr.lineTo(48, -30); cr.lineTo(36, 0); cr.lineTo(58, 40); cr.lineTo(50, 80)
        c.drawPath(cr, P(C('#3A1A0A'), 6))
        if drip > 0:
            for i in range(4):
                ph = (t * 1.8 + i / 4) % 1
                c.drawOval(skia.Rect(46, 82 + ph * 190, 62, 104 + ph * 190), P(C('#6EC1E4', int(255 * drip * (1 - ph * .6)))))
    if tear > 0:
        for i, ex in enumerate((-30, 30)):
            ty = ey + 16 + ((t * 110 + i * 35) % 70)
            c.drawOval(skia.Rect(ex - 6, ty, ex + 6, ty + 16), P(C('#8FD3FF', int(230 * tear))))
    c.restore()

def raghu(c, x, gy, s=1.0, mood='neutral', talk=False, t=0.0, look=(0, 0), bob=0.0, pots=None, sow=0.0):
    """front view, carrying pole on shoulders. pots: dict(left=..., right=...) kwargs for pot()"""
    s *= 1.1
    c.save(); c.translate(x, gy + bob); c.scale(s, s)
    skin = '#A8714A'
    c.drawRect(skia.Rect(-55, -230, 55, -20), P(C('#F3EFE4')))
    c.drawLine(-25, -25, -30, 0, P(C('#8A5A3B'), 18)); c.drawLine(25, -25, 30, 0, P(C('#8A5A3B'), 18))
    k = skia.Path(); k.moveTo(-75, -210); k.lineTo(-64, -420); k.quadTo(0, -445, 64, -420); k.lineTo(75, -210); k.close()
    c.drawPath(k, P(C('#E9A23B')))
    c.drawLine(0, -430, 0, -330, P(C('#000000', 40), 4))
    # pole
    c.drawLine(-330, -432, 330, -432, P(C('#9C7A3C'), 16))
    ap = P(C('#E9A23B'), 32)
    c.drawLine(-62, -405, -120, -440, ap); c.drawCircle(-125, -440, 19, P(C(skin)))
    if sow > 0:
        c.drawLine(62, -405, 120, -330, ap); c.drawCircle(126, -322, 19, P(C(skin)))
    else:
        c.drawLine(62, -405, 120, -440, ap); c.drawCircle(125, -440, 19, P(C(skin)))
    c.drawRect(skia.Rect(-16, -470, 16, -425), P(C(skin)))
    cy = -545
    c.drawOval(skia.Rect(-76, cy - 84, 76, cy + 10), P(C('#2A2420')))
    face(c, 0, cy, 70, skin, mood, talk, t, look)
    c.drawOval(skia.Rect(-80, cy - 112, 80, cy - 40), P(C('#FFFFFF')))           # white pagdi
    c.drawOval(skia.Rect(-60, cy - 128, 60, cy - 72), P(C('#F2F2F2')))
    m = skia.Path(); m.moveTo(-38, cy + 30); m.quadTo(-18, cy + 14, 0, cy + 24); m.quadTo(18, cy + 14, 38, cy + 30); m.quadTo(0, cy + 34, -38, cy + 30)
    c.drawPath(m, P(C('#2A2420')))
    mouth(c, 0, cy + 36, 70, mood, talk, t)
    c.restore()
    # ropes + pots (drawn in screen space so pot scale is independent)
    if pots:
        for side, kw in pots.items():
            sx = -1 if side == 'left' else 1
            px = x + sx * 300 * s; py = gy + bob - 432 * s
            sw = math.sin(t * 4 + sx) * 4 * (1 if bob else 0)
            potc = (px + sw, py + 230 * s)
            c.drawLine(px, py, potc[0] - 40 * s, potc[1] - 120 * s, P(C('#6B4226'), 4))
            c.drawLine(px, py, potc[0] + 40 * s, potc[1] - 120 * s, P(C('#6B4226'), 4))
            pot(c, potc[0], potc[1], 0.85 * s, t=t, **kw)
