"""Vishnu ji story art (vertical 1080x1920): vishnu (4 arms: shankh, chakra, gada, padma), garuda, vishnu_garuda,
chakra, magar (crocodile), lotus, trikut (mountain + lake background), water_front.
Uses elephant from hart.py and light_rays / cosmos from sart.py.
"""
import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sart import *
from hart import elephant

VSKIN = '#3F72D9'
VDARK = '#2A54AE'
PITA = '#FFC21A'
GOLD = '#FFC107'

def lotus(c, x, y, s=1.0, open_=1.0, glow=0.0, t=0.0):
    """pink lotus flower, centre (x, y)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    if glow > 0:
        for k in range(4): c.drawCircle(0, -10, 60 + k * 30, P(C('#FFF59D', int(45 * glow))))
    for lay, (n, L, col) in enumerate([(7, 70, '#F48FB1'), (5, 58, '#F06292'), (3, 44, '#FCE4EC')]):
        for i in range(n):
            ang = math.radians(-90 + (i - (n - 1) / 2) * (150 / max(1, n - 1)) * (0.45 + 0.55 * open_))
            c.save(); c.rotate(math.degrees(ang) + 90)
            pt = skia.Path(); pt.moveTo(0, 0); pt.quadTo(L * .45, -L * .55, 0, -L); pt.quadTo(-L * .45, -L * .55, 0, 0); pt.close()
            c.drawPath(pt, P(C(col))); c.drawPath(pt, P(C('#C2185B', 110), 2))
            c.restore()
    c.drawOval(skia.Rect(-22, -16, 22, 8), P(C('#FFD54F')))
    c.restore()

def lily_pad(c, x, y, r, col='#43A047'):
    p = skia.Path(); p.addOval(skia.Rect(x - r, y - r * .38, x + r, y + r * .38))
    cut = skia.Path(); cut.moveTo(x, y); cut.lineTo(x + r * 1.1, y - r * .1); cut.lineTo(x + r * 1.1, y + r * .25); cut.close()
    c.drawPath(skia.Op(p, cut, skia.PathOp.kDifference_PathOp), P(C(col) if isinstance(col, str) else col))

def chakra(c, x, y, r, t, a=1.0, spin=6.0):
    if a <= 0: return
    c.save(); c.translate(x, y); c.rotate(math.degrees(t * spin))
    c.drawCircle(0, 0, r * 1.7, P(C('#FFF59D', int(70 * a))))
    for i in range(12):                                     # flame teeth
        c.save(); c.rotate(i * 30)
        th = skia.Path(); th.moveTo(-r * .18, -r * .92); th.quadTo(r * .05, -r * 1.25, r * .24, -r * 1.32); th.quadTo(r * .12, -r * 1.05, r * .18, -r * .92); th.close()
        c.drawPath(th, P(C('#FF9800', int(255 * a))))
        c.restore()
    c.drawCircle(0, 0, r, P(C(GOLD, int(255 * a))))
    c.drawCircle(0, 0, r * .78, P(C('#FFE082', int(255 * a))))
    for i in range(8):
        ang = i * math.pi / 4
        c.drawLine(0, 0, math.cos(ang) * r * .78, math.sin(ang) * r * .78, P(C('#E65100', int(255 * a)), max(2, r * .08)))
    c.drawCircle(0, 0, r * .25, P(C('#E65100', int(255 * a))))
    c.drawCircle(0, 0, r * .12, P(C('#FFF8E1', int(255 * a))))
    c.restore()

def shankh(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-25)
    b = skia.Path(); b.moveTo(-40, -10); b.quadTo(-10, -60, 40, -40); b.quadTo(70, -10, 50, 30); b.quadTo(10, 45, -45, 15); b.close()
    c.drawPath(b, P(C('#FFFDF5'))); c.drawPath(b, P(C('#BCAAA4'), 3))
    tip = skia.Path(); tip.moveTo(-40, -10); tip.lineTo(-78, 2); tip.lineTo(-45, 15); tip.close()
    c.drawPath(tip, P(C('#F5EEE6'))); c.drawPath(tip, P(C('#BCAAA4'), 3))
    for k in range(3): c.drawArc(skia.Rect(-25 + k * 14, -35 + k * 4, 35 - k * 4, 25 - k * 4), 200, 200, False, P(C('#D7CCC8'), 3))
    c.drawOval(skia.Rect(20, -20, 52, 20), P(C('#F8BBD0')))
    c.restore()

def gada(c, x, ytop, ybot, s=1.0):
    c.drawLine(x, ytop, x, ybot, P(C('#C8962A'), 16 * s))
    for k in range(3): c.drawLine(x - 12 * s, ybot - 40 * s - k * 70 * s, x + 12 * s, ybot - 40 * s - k * 70 * s, P(C('#8D6E1E'), 6 * s))
    r = 58 * s
    c.drawCircle(x, ytop - r * .7, r, P(C(GOLD)))
    for k in range(-2, 3): c.drawLine(x + k * r * .35, ytop - r * 1.6, x + k * r * .35, ytop + r * .2, P(C('#E0A800'), 4 * s))
    c.drawCircle(x, ytop - r * .7, r, P(C('#B8860B'), 4 * s))
    c.drawCircle(x, ytop - r * 1.75, r * .22, P(C(GOLD)))
    c.drawRect(skia.Rect(x - r * .5, ytop - 6 * s, x + r * .5, ytop + 10 * s), P(C('#B8860B')))

def vishnu(c, x, gy, s=1.0, t=0.0, mood='calm', aura=0.0, chakra_on=True, talk=False, bless=False, look=(0, 0)):
    """Bhagwan Vishnu standing, front view, ~1120 tall at s=1 (crown top ~gy-1120). Feet at gy.
    Hands (viewer left = his right): upper chakra, upper-other shankh, lower padma (or blessing), lower gada."""
    c.save(); c.translate(x, gy); c.scale(s, s)
    cy = -860
    if aura > 0:
        for k in range(6): c.drawCircle(0, -700, 260 + k * 60, P(C('#FFF2B3', int(32 * aura))))
    # halo
    c.drawCircle(0, cy - 30, 175, P(C('#FFD54F', 150)))
    c.drawCircle(0, cy - 30, 175, P(C('#FFA000'), 8))
    for i in range(24):
        ang = i / 24 * math.tau
        c.drawLine(math.cos(ang) * 150, cy - 30 + math.sin(ang) * 150, math.cos(ang) * 172, cy - 30 + math.sin(ang) * 172, P(C('#FFF8E1'), 5))
    # gada (behind lower right arm)
    gada(c, 230, -640, -40)
    # hair falling on shoulders
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-115, cy - 40, 115, cy + 175), 60, 60), P(C('#1A1430')))
    sk = VSKIN
    # legs + feet
    c.drawLine(-42, -300, -48, -18, P(C(sk), 46)); c.drawLine(42, -300, 48, -18, P(C(sk), 46))
    c.drawOval(skia.Rect(-86, -24, -16, 6), P(C(sk))); c.drawOval(skia.Rect(16, -24, 86, 6), P(C(sk)))
    for sx in (-1, 1): c.drawLine(sx * 48 - 26, -40, sx * 48 + 26, -40, P(C(GOLD), 8))
    # pitambar dhoti
    dh = skia.Path(); dh.moveTo(-118, -480); dh.lineTo(118, -480); dh.lineTo(132, -110); dh.quadTo(60, -80, 20, -150)
    dh.lineTo(-20, -150); dh.quadTo(-60, -80, -132, -110); dh.close()
    c.drawPath(dh, P(C(PITA)))
    c.drawPath(dh, P(C('#E65100'), 5))
    for i in range(4): c.drawLine(-12 + i * 8, -470, -16 + i * 10, -160, P(C('#F0A000'), 4))
    c.drawLine(-70, -440, -95, -140, P(C('#F0A000'), 4)); c.drawLine(70, -440, 95, -140, P(C('#F0A000'), 4))
    # torso
    tor = skia.Path(); tor.moveTo(-122, -740); tor.quadTo(0, -770, 122, -740); tor.lineTo(104, -480); tor.lineTo(-104, -480); tor.close()
    c.drawPath(tor, P(C(sk)))
    c.drawLine(-60, -640, -20, -620, P(C('#000000', 30), 4)); c.drawLine(60, -640, 20, -620, P(C('#000000', 30), 4))
    c.drawRect(skia.Rect(-120, -500, 120, -470), P(C(GOLD)))                 # belt
    c.drawCircle(0, -485, 18, P(C('#E53935')))
    # yellow sash over left shoulder
    sa = skia.Path(); sa.moveTo(70, -745); sa.lineTo(118, -735); sa.lineTo(-80, -500); sa.lineTo(-112, -520); sa.close()
    c.drawPath(sa, P(C('#FFB300')))
    # neck
    c.drawRect(skia.Rect(-34, -800, 34, -730), P(C(sk)))
    # necklaces
    c.drawArc(skia.Rect(-70, -790, 70, -690), 15, 150, False, P(C(GOLD), 12))
    c.drawArc(skia.Rect(-90, -800, 90, -640), 15, 150, False, P(C(GOLD), 8))
    c.drawCircle(0, -642, 14, P(C('#E53935')))
    # vaijayanti mala (long garland)
    cols = ['#E53935', '#FFFFFF', '#FFC107', '#43A047']
    for i in range(23):
        u = i / 22
        mx = math.sin(u * math.pi * 2 - math.pi / 2) * 0 + (-100 + 200 * u)
        my = -745 + math.sin(u * math.pi) * 440
        c.drawCircle(mx * (1 - 0.3 * math.sin(u * math.pi)), my, 13, P(C(cols[i % 4])))
    # arms
    ap = P(C(sk), 40)
    band = lambda xx, yy: c.drawLine(xx - 22, yy, xx + 22, yy, P(C(GOLD), 8))
    # upper arms (raised): chakra (viewer left), shankh (viewer right)
    c.drawLine(-118, -735, -235, -760, ap); c.drawLine(-235, -760, -262, -905, ap)
    c.drawLine(118, -735, 235, -760, ap); c.drawLine(235, -760, 262, -905, ap)
    band(-180, -748); band(180, -748)
    c.drawCircle(-262, -915, 28, P(C(sk))); c.drawCircle(262, -915, 28, P(C(sk)))
    c.drawLine(-262, -935, -262, -965, P(C(sk), 14))                        # raised finger
    if chakra_on: chakra(c, -262, -1030, 58, t)
    shankh(c, 262, -950, 1.0)
    # lower arms
    c.drawLine(-110, -705, -190, -590, ap)
    if bless:
        c.drawLine(-190, -590, -170, -690, ap)
        palm = skia.Path(); palm.addRRect(skia.RRect.MakeRectXY(skia.Rect(-200, -770, -140, -680), 24, 24)); c.drawPath(palm, P(C(sk)))
    else:
        c.drawLine(-190, -590, -205, -495, ap); c.drawCircle(-205, -480, 26, P(C(sk)))
        c.drawLine(-205, -480, -215, -560, P(C('#2E7D32'), 8))
        lotus(c, -215, -560, 0.75)
    c.drawLine(110, -705, 190, -590, ap); c.drawLine(190, -590, 225, -500, ap); c.drawCircle(228, -488, 26, P(C(sk)))
    for xx, yy in ((-200, -545), (210, -548)): band(xx, yy)
    # head
    face(c, 0, cy, 88, sk, 'happy' if mood != 'calm' else 'neutral', False, t, look)
    # cover default brows/eyes look kind: soft smile
    if talk: mouth(c, 0, cy + 36, 88, 'neutral', True, t)
    else: c.drawArc(skia.Rect(-28, cy + 26, 28, cy + 60), 20, 140, False, P(C('#5A1E10'), 5))
    # tilak (urdhva pundra)
    c.drawLine(-14, cy - 30, -18, cy - 78, P(C('#FFF3C4'), 7)); c.drawLine(14, cy - 30, 18, cy - 78, P(C('#FFF3C4'), 7))
    c.drawArc(skia.Rect(-14, cy - 44, 14, cy - 20), 0, 180, False, P(C('#FFF3C4'), 7))
    c.drawLine(0, cy - 34, 0, cy - 78, P(C('#E53935'), 6))
    # makara kundal earrings
    for sx in (-1, 1):
        c.drawCircle(sx * 88, cy + 32, 18, P(C(GOLD))); c.drawCircle(sx * 88, cy + 58, 10, P(C(GOLD)))
    # hair line
    hp = skia.Path(); hp.moveTo(-90, cy - 8); hp.quadTo(-92, cy - 92, 0, cy - 86); hp.quadTo(92, cy - 92, 90, cy - 8); hp.quadTo(50, cy - 62, 0, cy - 60); hp.quadTo(-50, cy - 62, -90, cy - 8)
    c.drawPath(hp, P(C('#1A1430')))
    # kirit mukut (tall crown)
    cr = skia.Path(); cr.moveTo(-82, cy - 66); cr.lineTo(-62, cy - 240); cr.quadTo(0, cy - 290, 62, cy - 240); cr.lineTo(82, cy - 66); cr.quadTo(0, cy - 90, -82, cy - 66); cr.close()
    c.drawPath(cr, P(C(GOLD))); c.drawPath(cr, P(C('#B8860B'), 5))
    for yy in (cy - 110, cy - 170, cy - 228): c.drawLine(-75 + (cy - 66 - yy) * .1, yy, 75 - (cy - 66 - yy) * .1, yy, P(C('#E0A800'), 6))
    c.drawCircle(0, cy - 140, 20, P(C('#E53935'))); c.drawCircle(-40, cy - 140, 10, P(C('#43A047'))); c.drawCircle(40, cy - 140, 10, P(C('#43A047')))
    c.drawCircle(0, cy - 200, 13, P(C('#1E88E5')))
    sp_ = skia.Path(); sp_.moveTo(-16, cy - 268); sp_.lineTo(0, cy - 330); sp_.lineTo(16, cy - 268); sp_.close()
    c.drawPath(sp_, P(C(GOLD)))
    c.restore()

def garuda(c, x, y, s=1.0, t=0.0, flap=1.0, body=True, wings=True):
    """Garuda, front view; (x, y) = his chest. Wings span about +-560."""
    c.save(); c.translate(x, y); c.scale(s, s)
    ang = math.sin(t * 6) * 14 * flap
    if wings:
        for sx in (-1, 1):
            c.save(); c.translate(sx * 60, -120); c.rotate(-sx * ang)
            for lay, (L, col) in enumerate([(560, '#B71C1C'), (480, '#E65100'), (380, '#FFB300')]):
                w = skia.Path(); w.moveTo(0, -20)
                w.quadTo(sx * L * .5, -200 + lay * 30, sx * L, -150 + lay * 40)
                for k in range(6):
                    fx = sx * L * (1 - k * .15); fy = -150 + lay * 40 + 60 + k * 35
                    w.lineTo(fx, fy); w.lineTo(fx - sx * 30, fy - 40)
                w.lineTo(sx * 40, 120 - lay * 20); w.close()
                c.drawPath(w, P(C(col)))
            c.restore()
    if body:
        # tail feathers
        for k in range(-2, 3):
            tf = skia.Path(); tf.moveTo(k * 18, 200); tf.lineTo(k * 50 - 20, 360); tf.lineTo(k * 50 + 20, 360); tf.close()
            c.drawPath(tf, P(C('#E65100' if k % 2 else '#FFB300')))
        # body
        c.drawOval(skia.Rect(-110, -150, 110, 230), P(C('#2E7D32')))
        c.drawOval(skia.Rect(-80, -110, 80, 200), P(C('#FFCA28')))
        for k in range(4): c.drawArc(skia.Rect(-60, -70 + k * 55, 60, -10 + k * 55), 20, 140, False, P(C('#F9A825'), 4))
        # hands in namaste
        for sx in (-1, 1): c.drawLine(sx * 100, -90, sx * 30, -10, P(C('#E8B04A'), 30))
        nm = skia.Path(); nm.moveTo(-14, -10); nm.lineTo(0, -80); nm.lineTo(14, -10); nm.close(); c.drawPath(nm, P(C('#E8B04A')))
        # head (eagle)
        c.drawCircle(0, -205, 78, P(C('#F5F5F0')))
        c.drawCircle(0, -205, 78, P(C('#BDBDBD'), 3))
        bk = skia.Path(); bk.moveTo(-26, -200); bk.quadTo(0, -215, 26, -200); bk.quadTo(18, -150, 0, -130); bk.quadTo(-18, -150, -26, -200); bk.close()
        c.drawPath(bk, P(C('#FFA000'))); c.drawPath(bk, P(C('#BF6A00'), 3))
        for ex in (-34, 34):
            c.drawOval(skia.Rect(ex - 14, -246, ex + 14, -220), P(C('#FFFFFF')))
            c.drawCircle(ex, -232, 8, P(C('#3E2723')))
            c.drawLine(ex - 18, -254, ex + 14, -250 if ex < 0 else -258, P(C('#5D4037'), 5))
        # small crown
        gc = skia.Path(); gc.moveTo(-50, -268); gc.lineTo(-38, -320); gc.lineTo(-18, -290); gc.lineTo(0, -335); gc.lineTo(18, -290); gc.lineTo(38, -320); gc.lineTo(50, -268); gc.close()
        c.drawPath(gc, P(C(GOLD))); c.drawCircle(0, -300, 9, P(C('#E53935')))
    c.restore()

def vishnu_garuda(c, x, y, s=1.0, t=0.0, flap=1.0, aura=0.0, chakra_on=True, bless=False):
    """Vishnu ji seated on Garuda; (x, y) = Garuda's chest. About 1250 tall at s=1 (crown ~y-1430*s)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    if aura > 0:
        for k in range(6): c.drawCircle(0, -560, 340 + k * 70, P(C('#FFF2B3', int(30 * aura))))
    garuda(c, 0, 0, 1.0, t, flap, body=False)
    c.save(); c.clipRect(skia.Rect(-900, -2000, 900, -300))
    vishnu(c, 0, 120, 1.0, t, chakra_on=chakra_on, bless=bless)
    c.restore()
    # seated lap (pitambar) over Garuda's shoulders
    lap = skia.Path(); lap.moveTo(-130, -360); lap.lineTo(130, -360); lap.quadTo(260, -320, 250, -250); lap.lineTo(-250, -250); lap.quadTo(-260, -320, -130, -360); lap.close()
    c.drawPath(lap, P(C(PITA))); c.drawPath(lap, P(C('#E65100'), 5))
    for sx in (-1, 1):
        c.drawLine(sx * 230, -260, sx * 250, -120, P(C(VSKIN), 40))
        c.drawOval(skia.Rect(sx * 250 - 40, -130, sx * 250 + 40, -96), P(C(VSKIN)))
        c.drawLine(sx * 250 - 22, -140, sx * 250 + 22, -140, P(C(GOLD), 7))
    garuda(c, 0, 0, 1.0, t, flap, wings=False)
    c.restore()

def magar(c, x, y, s=1.0, t=0.0, open_=0.0, facing=1, glow=0.0, a=1.0):
    """crocodile head + back at the water surface; (x, y) = jaw hinge at water line. facing 1 = snout to the right."""
    if a <= 0: return
    c.save(); c.translate(x, y); c.scale(s * facing, s)
    if a < 1: c.saveLayerAlpha(None, int(255 * a))
    body = '#4E7D3A'; dark = '#355A26'; belly = '#C9C27A'
    # back with scutes going left, partly in water
    bk = skia.Path(); bk.moveTo(-40, -40); bk.quadTo(-200, -70, -420, -10); bk.lineTo(-420, 20); bk.lineTo(-40, 20); bk.close()
    c.drawPath(bk, P(C(body)))
    for i in range(7):
        sx = -80 - i * 50; sy = -50 + i * 5
        sc = skia.Path(); sc.moveTo(sx - 16, sy + 10); sc.lineTo(sx, sy - 20); sc.lineTo(sx + 16, sy + 10); sc.close()
        c.drawPath(sc, P(C(dark)))
    # lower jaw (rotates down)
    c.save(); c.rotate(open_ * 22)
    lj = skia.Path(); lj.moveTo(-20, 0); lj.lineTo(250, 4); lj.quadTo(270, 14, 250, 26); lj.lineTo(-10, 34); lj.close()
    c.drawPath(lj, P(C(belly)))
    for i in range(8):
        tx = 20 + i * 28; tp = skia.Path(); tp.moveTo(tx, 4); tp.lineTo(tx + 8, -10); tp.lineTo(tx + 16, 4); tp.close(); c.drawPath(tp, P(C('#FFFFFF')))
    c.restore()
    # upper jaw / head
    c.save(); c.rotate(-open_ * 14)
    uj = skia.Path(); uj.moveTo(-60, -50); uj.quadTo(40, -78, 120, -40); uj.lineTo(262, -22); uj.quadTo(285, -8, 262, 4); uj.lineTo(-30, 4); uj.close()
    c.drawPath(uj, P(C(body)))
    for i in range(8):
        tx = 20 + i * 28; tp = skia.Path(); tp.moveTo(tx, 2); tp.lineTo(tx + 8, 16); tp.lineTo(tx + 16, 2); tp.close(); c.drawPath(tp, P(C('#FFFFFF')))
    c.drawCircle(248, -26, 6, P(C(dark)))
    # eye bump
    c.drawOval(skia.Rect(-10, -96, 50, -44), P(C(body)))
    c.drawOval(skia.Rect(4, -84, 38, -58), P(C('#FFEB3B')))
    c.drawOval(skia.Rect(18, -82, 25, -60), P(C('#212121')))
    c.drawLine(-4, -92, 46, -78, P(C(dark), 6))
    for i in range(4): c.drawCircle(70 + i * 40, -40 + i * 3, 5, P(C(dark)))
    c.restore()
    if glow > 0:
        c.drawCircle(80, -20, 220, P(C('#FFF59D', int(160 * glow))))
    if a < 1: c.restore()
    c.restore()

def trikut(c, t, mood='day', k=1.0):
    """sky + three-peaked Trikut mountain + forest. Lake surface at WL."""
    cols = {'day': ('#6EC1F2', '#DDF3FF'), 'dusk': ('#3C3266', '#F29E6B'), 'night': ('#0E1433', '#2C3E78'),
            'divine': ('#F7B267', '#FFF1C9')}[mood]
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, WL)], [C(cols[0]), C(cols[1])]))
    c.drawRect(skia.Rect(0, 0, W, WL + 5), p)
    if mood == 'night':
        for i, (x, y, r) in enumerate(STARS2[:70]):
            if y < 800: c.drawCircle(x, y, r, P(C('#FFFFFF', int(170 * (0.5 + 0.5 * math.sin(t * 2 + i))))))
        c.drawCircle(930, 420, 55, P(C('#FFF8E1')))
    elif mood == 'day':
        c.drawCircle(920, 430, 60, P(C('#FFF3B0')))
        cloud(c, 250 + t * 12, 300, 1.1); cloud(c, 700 + t * 8, 420, 0.8)
    dk = {'day': 0, 'dusk': .35, 'night': .6, 'divine': .1}[mood]
    for x0, hgt, wd, col in [(-160, 560, 560, '#6E9F6A'), (560, 520, 620, '#6E9F6A'), (170, 760, 740, '#5C8E5A')]:
        m = skia.Path(); m.moveTo(x0, WL); m.lineTo(x0 + wd * .5, WL - hgt); m.lineTo(x0 + wd, WL); m.close()
        c.drawPath(m, P(mixc(col, '#0E1433', dk)))
        sn = skia.Path(); sn.moveTo(x0 + wd * .5, WL - hgt); sn.lineTo(x0 + wd * .5 - 50, WL - hgt + 90); sn.lineTo(x0 + wd * .5 + 50, WL - hgt + 90); sn.close()
        c.drawPath(sn, P(mixc('#E8F5E9', '#0E1433', dk)))
    for i in range(14):
        tx = i * 82 - 20; th = 120 + (i * 37) % 60
        c.drawCircle(tx, WL - th * .6, th * .45, P(mixc('#2E7D32' if i % 2 else '#388E3C', '#0E1433', dk)))
    # lake
    wp = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, WL), skia.Point(0, H)], [mixc('#4FA3C7', '#0E1433', dk * .8), mixc('#1F5F86', '#060A1C', dk * .8)]))
    c.drawRect(skia.Rect(0, WL, W, H), wp)
    for i in range(10):
        yy = WL + 30 + i * 60; xx = (i * 173 + t * 30) % 1200 - 100
        c.drawLine(xx, yy, xx + 120, yy, P(C('#FFFFFF', 50), 4))
    for (lx, ly, r) in ((90, WL + 40, 46), (980, WL + 60, 52), (860, WL + 20, 34)):
        lily_pad(c, lx, ly, r, mixc('#43A047', '#0E1433', dk))
    lotus(c, 120, WL + 20, 0.45); lotus(c, 950, WL + 40, 0.5)

WL = 1080   # water line (lake surface)

def water_front(c, y, t, a=0.62, dark=0.0):
    """semi transparent water in front of a wading character, top edge at y."""
    p = skia.Path(); p.moveTo(0, y)
    for i in range(0, 1101, 40): p.lineTo(i, y + math.sin(i * .03 + t * 3) * 8)
    p.lineTo(W, H); p.lineTo(0, H); p.close()
    c.drawPath(p, P(mixc('#2F86B5', '#0A1430', dark, int(255 * a))))
    c.drawPath(p, P(C('#E1F5FE', 150), 5))
    for i in range(6):
        xx = (i * 211 + t * 40) % 1200 - 60; yy = y + 50 + i * 45
        c.drawLine(xx, yy, xx + 90, yy, P(C('#FFFFFF', 60), 4))

def ripple(c, x, y, k, col='#E1F5FE'):
    for j in range(3):
        kk = (k + j / 3) % 1
        c.drawOval(skia.Rect(x - 60 - 160 * kk, y - 12 - 30 * kk, x + 60 + 160 * kk, y + 12 + 30 * kk), P(C(col, int(180 * (1 - kk))), 5))

def splash_drops(c, x, y, k, n=14, col='#E1F5FE'):
    if k <= 0 or k >= 1: return
    for i in range(n):
        ang = math.pi * (1.05 + .9 * i / (n - 1))
        d = 260 * k
        c.drawCircle(x + math.cos(ang) * d, y + math.sin(ang) * d * 1.2 + 500 * k * k, 14 * (1 - k) + 4, P(C(col, int(230 * (1 - k)))))
