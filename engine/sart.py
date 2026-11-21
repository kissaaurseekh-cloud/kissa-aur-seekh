"""Shiv ji / mythology art for vertical (1080x1920) stories.
cosmos, ocean, mandara (mountain), vasuki (serpent), deva, asura, shiv, parvati, poison_cloud, kailash, amrit_kalash.
"""
import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gart import *
from hart import man

STARS2 = [(random.Random(i).uniform(0, 1080), random.Random(i + 99).uniform(0, 1150), random.Random(i + 7).uniform(1.5, 4)) for i in range(120)]

def cosmos(c, t, green=0.0, dawn=0.0):
    top = mixc(blend('#140B33', '#0B2A1E', green), '#F6A96B', dawn)
    bot = mixc(blend('#5B2A86', '#2E7D32', green * .8), '#FFE2B0', dawn)
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1150)], [top, bot]))
    c.drawRect(skia.Rect(0, 0, W, 1200), p)
    a = 1 - dawn
    for i, (x, y, r) in enumerate(STARS2):
        tw = 0.5 + 0.5 * math.sin(t * 2.3 + i)
        c.drawCircle(x, y, r, P(C('#FFFFFF', int(200 * a * (0.4 + 0.6 * tw)))))

def ocean(c, y0, t, green=0.0, churn=0.0, dark=0.0):
    top = blend(blend('#2C6FB7', '#3FA34D', green), '#0E1A2E', dark)
    bot = blend(blend('#0D2F5E', '#123D1C', green), '#05080F', dark)
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, H)], [C(top), C(bot)]))
    c.drawRect(skia.Rect(0, y0, W, H), p)
    for row in range(7):
        yy = y0 + 30 + row * (60 + row * 18)
        amp = 10 + row * 3 + churn * 10
        path = skia.Path(); path.moveTo(0, yy)
        for x in range(0, W + 40, 40):
            path.lineTo(x, yy + math.sin(x / 70 + t * (2 + churn * 3) + row) * amp)
        c.drawPath(path, P(C('#FFFFFF', 55 - row * 5), 5))

def mandara(c, x, by, h, t, spin=0.0, glow=0.0):
    """mountain standing in the ocean; by = waterline, h = height. spin moves the rock stripes."""
    top = by - h
    m = skia.Path(); m.moveTo(x - 210, by + 40); m.lineTo(x - 70, top + 40); m.quadTo(x, top - 20, x + 70, top + 40); m.lineTo(x + 210, by + 40); m.close()
    c.drawPath(m, P(C('#7B5A3E')))
    c.save(); c.clipPath(m, skia.ClipOp.kIntersect, True)
    for i in range(-6, 8):
        sx = x + ((i * 70 + spin * 300) % 980) - 490
        c.drawLine(sx, top, sx - 60, by + 40, P(C('#5E4330'), 18))
    c.drawRect(skia.Rect(x - 220, top - 30, x + 220, top + 110), P(C('#5E8D3E')))  # green top
    c.restore()
    c.drawPath(m, P(C('#4A3424'), 6))
    if glow > 0:
        c.drawCircle(x, top + 20, 120, P(C('#FFF3B0', int(90 * glow))))

def vasuki(c, x, by, h, t, pull=0.0, lend=None, rend=None):
    """serpent wrapped round the mountain; tail goes left (devas), head right (asuras)."""
    col, dark, belly = '#3E9B4F', '#25693A', '#C8E6A0'
    for k in range(4):
        yy = by - h * (0.25 + k * 0.17)
        wdt = 190 - k * 30
        c.drawArc(skia.Rect(x - wdt, yy - 26, x + wdt, yy + 26), 0, 180, False, P(C(col), 30))
    ry = by - h * 0.25
    sway = math.sin(pull) * 25
    # body to the left
    lp = skia.Path(); lp.moveTo(x - 180, ry); lx, ly = lend or (x - 600, ry + 10)
    lp.cubicTo(x - 320, ry + 30 + sway, lx + 140, ly - 20 - sway, lx, ly)
    c.drawPath(lp, P(C(col), 30)); c.drawPath(lp, P(C(dark), 4))
    # body to the right with head
    rp = skia.Path(); rp.moveTo(x + 180, ry); rx, ry2 = rend or (x + 600, ry - 10)
    rp.cubicTo(x + 320, ry + 30 - sway, rx - 140, ry2 - 20 + sway, rx, ry2)
    c.drawPath(rp, P(C(col), 30)); c.drawPath(rp, P(C(dark), 4))
    snake_head(c, rx + 30, ry2 + 10, 0.6)

def snake_head(c, x, y, s=1.0, flip=1):
    c.save(); c.translate(x, y); c.scale(s * flip, s)
    hood = skia.Path(); hood.moveTo(0, 30); hood.cubicTo(-70, 10, -60, -80, 0, -90); hood.cubicTo(60, -80, 70, 10, 0, 30)
    c.drawPath(hood, P(C('#3E9B4F'))); c.drawPath(hood, P(C('#25693A'), 4))
    c.drawOval(skia.Rect(-22, -60, 22, 10), P(C('#C8E6A0')))
    c.drawCircle(-14, -66, 6, P(C('#FFEB3B'))); c.drawCircle(14, -66, 6, P(C('#FFEB3B')))
    c.drawCircle(-14, -66, 2.5, P(C('#000000'))); c.drawCircle(14, -66, 2.5, P(C('#000000')))
    c.restore()

def deva(c, x, gy, s=0.6, mood='neutral', t=0.0, arm='down', facing=1, look=(0, 0)):
    man(c, x, gy, s, mood, False, t, look, kurta='#F2B233', pants='#C0392B', turban='#FFD54F', arm=arm, skin='#E8B98A', facing=facing)
    # little gold crown tip
    k = s * 1.15; hx = x; hy = gy - 680 * k
    tri = skia.Path(); tri.moveTo(hx - 28 * k, hy + 20 * k); tri.lineTo(hx, hy - 40 * k); tri.lineTo(hx + 28 * k, hy + 20 * k); tri.close()
    c.drawPath(tri, P(C('#FFC107'))); c.drawCircle(hx, hy - 4 * k, 9 * k, P(C('#E53935')))

def asura(c, x, gy, s=0.6, mood='neutral', t=0.0, arm='down', facing=1, look=(0, 0)):
    man(c, x, gy, s, mood, False, t, look, kurta='#5E2A6E', pants='#2B2B3A', turban=None, arm=arm, skin='#9C6B5A', facing=facing)
    k = s * 1.15; hy = gy - 625 * k
    for sx in (-1, 1):
        hp = skia.Path(); hp.moveTo(x + sx * 40 * k, hy); hp.quadTo(x + sx * 80 * k, hy - 40 * k, x + sx * 70 * k, hy - 85 * k)
        hp.quadTo(x + sx * 58 * k, hy - 40 * k, x + sx * 20 * k, hy + 6 * k); hp.close()
        c.drawPath(hp, P(C('#EDE3D1')))

def poison_cloud(c, x, y, r, t, a=1.0):
    if r <= 1 or a <= 0: return
    c.drawCircle(x, y, r * 1.35, P(C('#76FF03', int(40 * a))))
    rnd = random.Random(3)
    for i in range(14):
        ang = i / 14 * math.tau + t * 0.6 * (1 if i % 2 else -1)
        d = r * (0.35 + 0.35 * rnd.random())
        rr = r * (0.38 + 0.2 * rnd.random()) * (1 + 0.06 * math.sin(t * 3 + i))
        col = ['#1B5E20', '#33691E', '#4A148C', '#2E7D32'][i % 4]
        c.drawCircle(x + math.cos(ang) * d, y + math.sin(ang) * d * 0.8, rr, P(C(col, int(235 * a))))
    for i in range(10):
        ang = i / 10 * math.tau - t * 1.2
        c.drawCircle(x + math.cos(ang) * r * .55, y + math.sin(ang) * r * .45, r * .12, P(C('#B2FF59', int(150 * a))))
    c.drawCircle(x, y, r * .35, P(C('#CCFF90', int(110 * a))))

def light_rays(c, x, y, t, a=1.0, col='#FFF3B0', n=14, L=1400):
    if a <= 0: return
    for i in range(n):
        ang = i / n * math.tau + t * 0.15
        p = skia.Path(); p.moveTo(x, y)
        p.lineTo(x + math.cos(ang - .05) * L, y + math.sin(ang - .05) * L); p.lineTo(x + math.cos(ang + .05) * L, y + math.sin(ang + .05) * L); p.close()
        c.drawPath(p, P(C(col, int(55 * a))))

SKIN = '#E9D8C4'     # ash-smeared skin
BLUE = '#1E5BD8'

def shiv(c, x, gy, s=1.0, t=0.0, eyes='calm', smile=True, hands='rest', cup=0.0, throat=0.0, throat_green=0.0, aura=0.0, talk=False, sil=0.0):
    """Shiv ji standing; about 900 units tall at s=1. Feet at gy.
    hands: 'rest' (blessing + trishul) | 'cup' (bowl at chest, cup = poison amount) | 'drink' (bowl at mouth).
    throat: 0..1 blue, throat_green: green glow (poison inside). sil: 0..1 dark silhouette."""
    c.save(); c.translate(x, gy); c.scale(s, s)
    if aura > 0:
        for k in range(5): c.drawCircle(0, -620, 300 + k * 60, P(C('#9FD3FF', int(30 * aura))))
    skin = SKIN
    # trishul behind
    if hands == 'rest':
        c.drawLine(190, -40, 190, -1060, P(C('#8D6E63'), 14))
        tr = P(C('#B0BEC5'), 12)
        c.drawLine(190, -1060, 190, -1160, tr)
        c.drawArc(skia.Rect(130, -1150, 250, -1040), 0, 180, False, tr)
        c.drawLine(130, -1095, 130, -1140, tr); c.drawLine(250, -1095, 250, -1140, tr)
        # damru
        d = skia.Path(); d.moveTo(160, -1010); d.lineTo(220, -1010); d.lineTo(196, -980); d.lineTo(220, -950); d.lineTo(160, -950); d.lineTo(184, -980); d.close()
        c.drawPath(d, P(C('#A1887F'))); c.drawPath(d, P(C('#5D4037'), 3))
    # legs + tiger skin
    c.drawLine(-40, -260, -46, -10, P(C(skin), 46)); c.drawLine(40, -260, 46, -10, P(C(skin), 46))
    c.drawOval(skia.Rect(-80, -20, -14, 6), P(C(skin))); c.drawOval(skia.Rect(14, -20, 80, 6), P(C(skin)))
    dh = skia.Path(); dh.moveTo(-110, -450); dh.lineTo(110, -450); dh.lineTo(130, -230); dh.quadTo(0, -200, -130, -230); dh.close()
    c.drawPath(dh, P(C('#F39C34')))
    c.save(); c.clipPath(dh, skia.ClipOp.kIntersect, True)
    for i in range(7):
        sx = -110 + i * 36
        st = skia.Path(); st.moveTo(sx, -450); st.quadTo(sx + 18, -380, sx - 4, -300); st.quadTo(sx + 6, -360, sx - 8, -450); st.close()
        c.drawPath(st, P(C('#3E2723')))
    c.restore()
    # torso
    tor = skia.Path(); tor.moveTo(-120, -730); tor.quadTo(0, -760, 120, -730); tor.lineTo(100, -450); tor.lineTo(-100, -450); tor.close()
    c.drawPath(tor, P(C(skin)))
    c.drawLine(-60, -620, -20, -600, P(C('#000000', 25), 4)); c.drawLine(60, -620, 20, -600, P(C('#000000', 25), 4))
    # rudraksha mala
    for i in range(15):
        a = math.pi * (0.1 + 0.8 * i / 14)
        c.drawCircle(math.cos(a) * 95, -735 + math.sin(a) * 150, 10, P(C('#6D3B1F')))
    # neck + throat
    c.drawRect(skia.Rect(-34, -800, 34, -720), P(C(skin)))
    if throat_green > 0:
        c.drawCircle(0, -765, 70, P(C('#76FF03', int(90 * throat_green))))
        c.drawOval(skia.Rect(-34, -790, 34, -735), P(C('#43A047', int(200 * throat_green))))
    if throat > 0:
        c.drawCircle(0, -765, 60 + 30 * throat, P(C('#64B5F6', int(110 * throat))))
        c.drawOval(skia.Rect(-36, -800, 36, -728), P(C(BLUE, int(255 * throat))))
        c.drawOval(skia.Rect(-20, -790, 0, -760), P(C('#90CAF9', int(160 * throat))))
    # neck snake
    nsp = skia.Path(); nsp.moveTo(-90, -720); nsp.quadTo(0, -690, 90, -720)
    c.drawPath(nsp, P(C('#3E9B4F'), 16))
    snake_head(c, 104, -730, 0.45)
    # arms
    ap = P(C(skin), 40)
    if hands == 'rest':
        c.drawLine(-115, -715, -175, -560, ap); c.drawLine(-175, -560, -150, -700, ap)
        c.drawCircle(-150, -720, 30, P(C(skin)))            # blessing palm
        c.drawLine(115, -715, 175, -560, ap); c.drawLine(175, -560, 190, -560, ap); c.drawCircle(190, -560, 26, P(C(skin)))
    elif hands == 'down':
        c.drawLine(-115, -715, -150, -470, ap); c.drawCircle(-152, -455, 26, P(C(skin)))
        c.drawLine(115, -715, 150, -470, ap); c.drawCircle(152, -455, 26, P(C(skin)))
    else:
        by = -560 if hands == 'cup' else -850
        bx = 0
        c.drawLine(-115, -715, -120, by + 40 if hands == 'cup' else -640, ap); c.drawLine(-120, by + 40 if hands == 'cup' else -640, bx - 40, by + 20, ap)
        c.drawLine(115, -715, 120, by + 40 if hands == 'cup' else -640, ap); c.drawLine(120, by + 40 if hands == 'cup' else -640, bx + 40, by + 20, ap)
        bowl = skia.Path(); bowl.moveTo(bx - 75, by); bowl.quadTo(bx, by + 70, bx + 75, by); bowl.close()
        if hands == 'drink': bowl = None
        elif cup > 0:
            c.drawCircle(bx, by - 10, 70 * cup + 20, P(C('#76FF03', int(70 * cup))))
            c.drawOval(skia.Rect(bx - 66, by - 16, bx + 66, by + 14), P(C('#33691E', int(255 * min(1, cup * 2)))))
        if bowl is not None: c.drawPath(bowl, P(C(skin))); c.drawPath(bowl, P(C('#B59A80'), 3))
    # head
    cy = -900
    # hair behind (long locks)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-105, cy - 40, 105, cy + 140), 50, 50), P(C('#2B1D14')))
    if hands != 'drink':
        face(c, 0, cy, 92, skin, 'neutral', False, t, (0, 0)) if eyes == 'open' else None
        if eyes == 'calm':
            c.drawCircle(0, cy, 92, P(C(skin)))
            c.drawCircle(-88, cy + 5, 18, P(C(skin))); c.drawCircle(88, cy + 5, 18, P(C(skin)))
            for ex in (-33, 33):
                c.drawArc(skia.Rect(ex - 18, cy - 22, ex + 18, cy + 2), 20, 140, False, P(C('#2B1A0E'), 5))
            c.drawPath(nose(0, cy, 92), P(C('#000000', 45), 4))
        if smile:
            c.drawArc(skia.Rect(-26, cy + 30, 26, cy + 58), 20, 140, False, P(C('#7A3A2A'), 5))
        elif talk:
            mouth(c, 0, cy + 38, 92, 'neutral', True, t)
        else:
            c.drawLine(-16, cy + 48, 16, cy + 48, P(C('#7A3A2A'), 5))
    else:
        c.drawCircle(0, cy, 92, P(C(skin)))
        c.drawCircle(-88, cy + 5, 18, P(C(skin))); c.drawCircle(88, cy + 5, 18, P(C(skin)))
        for ex in (-33, 33):
            c.drawArc(skia.Rect(ex - 18, cy - 22, ex + 18, cy + 2), 20, 140, False, P(C('#2B1A0E'), 5))
    # tripund + third eye
    for i in range(3):
        c.drawLine(-46, cy - 52 + i * 11, 46, cy - 52 + i * 11, P(C('#F5F5F5'), 6))
    c.drawOval(skia.Rect(-7, cy - 70, 7, cy - 38), P(C('#C62828')))
    # jata (bun) + crescent moon + hair band
    c.drawOval(skia.Rect(-96, cy - 110, 96, cy - 50), P(C('#2B1D14')))
    c.drawOval(skia.Rect(-62, cy - 240, 62, cy - 90), P(C('#2B1D14')))
    for i in range(3): c.drawArc(skia.Rect(-55, cy - 225 + i * 40, 55, cy - 175 + i * 40), 200, 140, False, P(C('#4A3426'), 5))
    c.drawRect(skia.Rect(-64, cy - 112, 64, cy - 98), P(C('#C8A24A')))
    moon = skia.Path(); moon.addCircle(-48, cy - 205, 32)
    cut = skia.Path(); cut.addCircle(-36, cy - 215, 28)
    moon = skia.Op(moon, cut, skia.PathOp.kDifference_PathOp)
    c.drawPath(moon, P(C('#FFF8E1')))
    # ganga spray
    for i in range(4): c.drawCircle(30 + i * 10, cy - 250 - i * 16, 8 - i, P(C('#B3E5FC')))
    if hands == 'drink':
        c.save(); c.translate(0, cy + 62); c.rotate(-12)
        c.drawCircle(0, -10, 60, P(C('#76FF03', 60)))
        bw = skia.Path(); bw.moveTo(-80, -10); bw.quadTo(0, 70, 80, -10); bw.close()
        c.drawOval(skia.Rect(-78, -26, 78, 6), P(C('#33691E')))
        c.drawPath(bw, P(C(skin))); c.drawPath(bw, P(C('#B59A80'), 3))
        c.restore()
        c.drawCircle(-95, cy + 70, 26, P(C(skin))); c.drawCircle(95, cy + 70, 26, P(C(skin)))
    c.restore()

def shiv_sil(c, x, gy, s, t, a=1.0, glow='#7FDBFF'):
    """mysterious silhouette version (hook): draw normal then cover with a dark layer inside its own bounds."""
    rec = skia.PictureRecorder(); cc = rec.beginRecording(skia.Rect(0, 0, W, H))
    shiv(cc, x, gy, s, t)
    pic = rec.finishRecordingAsPicture()
    # glow outline: draw blurred bright copy, then dark copy
    p = skia.Paint(ImageFilter=skia.ImageFilters.Blur(18, 18), ColorFilter=skia.ColorFilters.Blend(C(glow, int(255 * a)), skia.BlendMode.kSrcIn))
    c.saveLayer(None, p); c.drawPicture(pic); c.restore()
    p2 = skia.Paint(ColorFilter=skia.ColorFilters.Blend(C('#0A0820', int(255 * a)), skia.BlendMode.kSrcIn))
    c.saveLayer(None, p2); c.drawPicture(pic); c.restore()

def parvati(c, x, gy, s=1.0, t=0.0, mood='neutral', reach=None, talk=False, facing=1):
    """Mata Parvati standing ~820 tall; reach=(wx, wy) world point her right hand touches (facing right)."""
    skin = '#E7B488'
    c.save(); c.translate(x, gy); c.scale(s * facing, s)
    # long hair behind
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-95, -880, 95, -520), 70, 70), P(C('#1E140E')))
    # saree skirt
    sk = skia.Path(); sk.moveTo(-90, -430); sk.lineTo(90, -430); sk.lineTo(140, 0); sk.lineTo(-140, 0); sk.close()
    c.drawPath(sk, P(C('#C62828')))
    c.drawRect(skia.Rect(-140, -30, 140, 0), P(C('#FFC107')))
    for i in range(4): c.drawLine(-60 + i * 40, -420, -80 + i * 50, -40, P(C('#8E1B1B'), 4))
    # blouse / torso
    tor = skia.Path(); tor.moveTo(-95, -680); tor.quadTo(0, -705, 95, -680); tor.lineTo(85, -430); tor.lineTo(-85, -430); tor.close()
    c.drawPath(tor, P(C('#E53935')))
    pal = skia.Path(); pal.moveTo(-95, -680); pal.lineTo(-40, -680); pal.lineTo(90, -440); pal.lineTo(40, -430); pal.close()
    c.drawPath(pal, P(C('#B71C1C'))); c.drawLine(-40, -680, 90, -440, P(C('#FFC107'), 8))
    # necklace
    c.drawArc(skia.Rect(-55, -725, 55, -640), 20, 140, False, P(C('#FFC107'), 8))
    c.drawRect(skia.Rect(-26, -740, 26, -680), P(C(skin)))
    ap = P(C(skin), 32)
    # left arm down
    c.drawLine(-90, -665, -120, -480, ap); c.drawCircle(-122, -466, 20, P(C(skin)))
    for i in range(3): c.drawLine(-138, -505 + i * 10, -104, -505 + i * 10, P(C('#FFC107'), 5))
    # right arm: down or reaching
    if reach is None:
        c.drawLine(90, -665, 120, -480, ap); c.drawCircle(122, -466, 20, P(C(skin)))
    else:
        wx, wy = reach
        lx = (wx - x) / (s * facing); ly = (wy - gy) / s
        ex, ey = (90 + lx) / 2 + 10, (-665 + ly) / 2 + 60
        c.drawLine(90, -665, ex, ey, ap); c.drawLine(ex, ey, lx - 18, ly, ap)
        c.drawCircle(lx - 10, ly, 24, P(C(skin)))
        for i in range(3): c.drawLine(ex + (lx - ex) * .55 - 6 + i * 9, ey + (ly - ey) * .55 - 16, ex + (lx - ex) * .55 - 6 + i * 9, ey + (ly - ey) * .55 + 16, P(C('#FFC107'), 5))
    # head
    cy = -830
    face(c, 0, cy, 80, skin, mood, False, t, (1, 0) if reach else (0, 0))
    mouth(c, 0, cy + 30, 80, mood, talk, t)
    c.drawCircle(0, cy - 50, 9, P(C('#D50000')))
    c.drawCircle(-40, cy + 10, 6, P(C('#FFC107'), 3))       # nose ring
    # hair top + crown
    hp = skia.Path(); hp.moveTo(-84, cy - 5); hp.quadTo(-90, cy - 100, 0, cy - 92); hp.quadTo(90, cy - 100, 84, cy - 5); hp.quadTo(40, cy - 70, 0, cy - 62); hp.quadTo(-40, cy - 70, -84, cy - 5)
    c.drawPath(hp, P(C('#1E140E')))
    cr = skia.Path(); cr.moveTo(-50, cy - 86); cr.lineTo(-30, cy - 140); cr.lineTo(-10, cy - 100); cr.lineTo(0, cy - 150); cr.lineTo(10, cy - 100); cr.lineTo(30, cy - 140); cr.lineTo(50, cy - 86); cr.close()
    c.drawPath(cr, P(C('#FFC107'))); c.drawCircle(0, cy - 112, 9, P(C('#E53935')))
    for sx in (-1, 1): c.drawCircle(sx * 82, cy + 28, 10, P(C('#FFC107')))
    c.restore()

def kailash(c, t, dawn=1.0):
    cosmos(c, t, dawn=dawn)
    sun_y = 760
    c.drawCircle(540, sun_y, 120, P(C('#FFF1C1', 200)))
    for x0, hgt, col in [(-100, 520, '#8FA7C8'), (300, 700, '#A9BEDB'), (700, 560, '#8FA7C8')]:
        m = skia.Path(); m.moveTo(x0, 1250); m.lineTo(x0 + 260, 1250 - hgt); m.lineTo(x0 + 520, 1250); m.close()
        c.drawPath(m, P(C(col)))
        cap = skia.Path(); cap.moveTo(x0 + 260 - 70, 1250 - hgt + 110); cap.lineTo(x0 + 260, 1250 - hgt); cap.lineTo(x0 + 260 + 70, 1250 - hgt + 110)
        cap.quadTo(x0 + 260, 1250 - hgt + 80, x0 + 260 - 70, 1250 - hgt + 110); c.drawPath(cap, P(C('#FFFFFF')))
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 1240), skia.Point(0, H)], [C('#E8F1FA'), C('#B9CCE0')]))
    c.drawRect(skia.Rect(0, 1240, W, H), p)

def amrit_kalash(c, x, y, s=1.0, t=0.0, glow=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if glow > 0: c.drawCircle(0, -40, 150, P(C('#FFE082', int(90 * glow))))
    body = skia.Path(); body.addOval(skia.Rect(-90, -110, 90, 70)); c.drawPath(body, P(C('#FFB300')))
    c.drawRect(skia.Rect(-40, -160, 40, -100), P(C('#FFB300')))
    c.drawOval(skia.Rect(-60, -180, 60, -145), P(C('#FFCA28')))
    c.drawLine(-90, -20, 90, -20, P(C('#E65100'), 6))
    for i in range(5): c.drawCircle(-50 + i * 25, -192 - 6 * math.sin(t * 3 + i), 10, P(C('#FFF59D')))
    c.restore()

def visha_bowl(c, x, y, s=1.0, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, -30, 140, P(C('#76FF03', 60)))
    b = skia.Path(); b.moveTo(-110, -40); b.quadTo(0, 110, 110, -40); b.close(); c.drawPath(b, P(C('#5D4037')))
    c.drawOval(skia.Rect(-110, -60, 110, -20), P(C('#33691E')))
    for i in range(4):
        yy = -80 - ((t * 60 + i * 40) % 160)
        c.drawCircle(-40 + i * 27, yy, 14 - ((t * 60 + i * 40) % 160) / 20, P(C('#9CCC65', 180)))
    c.restore()
