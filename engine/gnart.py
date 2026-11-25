"""Ganesh ji story art (vertical 1080x1920): ganesh, kartikeya, peacock (mor), mushak (mouse), globe (prithvi).
Uses shiv / parvati / kailash / cosmos / light_rays from sart.py.
"""
import skia, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sart import *

GSKIN = '#F4A57E'
GDARK = '#D9805C'
GOLD = '#FFC107'

def _taper(c, pts, r0, r1, col):
    """tapered tube along a list of points (circles of decreasing radius)."""
    n = len(pts) - 1
    p = P(C(col))
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 4))
        for k in range(steps):
            f = (i + k / steps) / n
            c.drawCircle(lerp(x0, x1, k / steps), lerp(y0, y1, k / steps), lerp(r0, r1, f), p)

def _bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        u = i / n; a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; cc = 3 * (1 - u) * u * u; d = u ** 3
        out.append((a * p0[0] + b * p1[0] + cc * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + cc * p2[1] + d * p3[1]))
    return out

def modak(c, x, y, r=22):
    m = skia.Path(); m.moveTo(x, y - r * 1.5); m.quadTo(x + r * 1.2, y - r * .2, x + r, y + r * .6); m.quadTo(x, y + r * 1.1, x - r, y + r * .6)
    m.quadTo(x - r * 1.2, y - r * .2, x, y - r * 1.5); m.close()
    c.drawPath(m, P(C('#FFF3D6'))); c.drawPath(m, P(C('#D9B77A'), 3))
    for k in (-1, 0, 1): c.drawLine(x + k * r * .45, y + r * .7, x + k * r * .2, y - r * 1.1, P(C('#E3C48E'), 2))

def ganesh(c, x, gy, s=1.0, t=0.0, eyes='open', hands='bless', aura=0.0, look=(0, 0), talk=False):
    """Ganesh ji, front view, ~1100 tall at s=1 (crown top at gy-1120). hands: 'bless' | 'namaste'.
    eyes: 'open' | 'closed' | 'happy'."""
    c.save(); c.translate(x, gy); c.scale(s, s)
    if aura > 0:
        for k in range(6): c.drawCircle(0, -820, 230 + k * 55, P(C('#FFE082', int(34 * aura))))
        c.drawCircle(0, -880, 250, P(C('#FFD54F', int(60 * aura)), 10))
    # upper arms + attributes (behind body)
    ap = P(C(GSKIN), 42)
    c.drawLine(-140, -700, -230, -800, ap); c.drawLine(-230, -800, -255, -905, ap)
    c.drawCircle(-258, -915, 28, P(C(GSKIN)))
    # parashu (axe) in upper right hand (viewer left)
    c.drawLine(-258, -790, -258, -1060, P(C('#8D5A3B'), 12))
    ax = skia.Path(); ax.moveTo(-262, -1050); ax.quadTo(-350, -1070, -360, -1000); ax.quadTo(-330, -1010, -262, -985); ax.close()
    c.drawPath(ax, P(C('#CFD8DC'))); c.drawPath(ax, P(C('#78909C'), 4))
    c.drawLine(140, -700, 230, -800, ap); c.drawLine(230, -800, 255, -905, ap)
    c.drawCircle(258, -915, 28, P(C(GSKIN)))
    # pasha (noose) in upper left hand
    c.drawOval(skia.Rect(222, -1035, 300, -945), P(C('#E65100'), 8))
    c.drawLine(262, -890, 275, -820, P(C('#E65100'), 8))
    for sx in (-1, 1):
        for i in range(2): c.drawLine(sx * 242 - 18, -880 + i * 12, sx * 242 + 18, -880 + i * 12, P(C(GOLD), 5))
    # legs / feet
    c.drawOval(skia.Rect(-150, -40, -30, 8), P(C(GSKIN))); c.drawOval(skia.Rect(30, -40, 150, 8), P(C(GSKIN)))
    for sx in (-1, 1): c.drawLine(sx * 60 - 30, -28, sx * 60 + 30, -28, P(C(GOLD), 6))
    # dhoti
    dh = skia.Path(); dh.moveTo(-175, -390); dh.lineTo(175, -390); dh.lineTo(165, -30); dh.quadTo(90, -10, 10, -40); dh.lineTo(-10, -40); dh.quadTo(-90, -10, -165, -30); dh.close()
    c.drawPath(dh, P(C('#FFC21A')))
    c.drawLine(-160, -40, -15, -45, P(C('#D32F2F'), 12)); c.drawLine(15, -45, 160, -40, P(C('#D32F2F'), 12))
    for i in range(3): c.drawLine(-60 + i * 60, -380, -70 + i * 70, -60, P(C('#E0A000'), 4))
    # belly + chest
    c.drawOval(skia.Rect(-165, -790, 165, -560), P(C(GSKIN)))
    c.drawOval(skia.Rect(-200, -660, 200, -330), P(C(GSKIN)))
    c.drawArc(skia.Rect(-14, -470, 14, -448), 0, 180, False, P(C(GDARK), 4))
    c.drawOval(skia.Rect(-120, -620, 40, -520), P(C('#FFFFFF', 30)))
    # red sash at waist
    sa = skia.Path(); sa.moveTo(-190, -405); sa.quadTo(0, -360, 190, -405); sa.lineTo(185, -360); sa.quadTo(0, -320, -185, -360); sa.close()
    c.drawPath(sa, P(C('#C62828')))
    c.drawCircle(0, -350, 16, P(C(GOLD)))
    # sacred thread
    th = skia.Path(); th.moveTo(-120, -770); th.quadTo(30, -560, 150, -420)
    c.drawPath(th, P(C('#FFF8E1'), 6))
    # lower arms
    if hands == 'namaste':
        c.drawLine(-160, -720, -175, -540, ap); c.drawLine(160, -720, 175, -540, ap)
    else:
        # abhaya (blessing) in lower right hand (viewer left)
        c.drawLine(-165, -720, -230, -560, ap); c.drawLine(-230, -560, -230, -640, ap)
        pl = skia.Path(); pl.addRRect(skia.RRect.MakeRectXY(skia.Rect(-262, -720, -198, -630), 26, 26)); c.drawPath(pl, P(C(GSKIN)))
        for i in range(3): c.drawLine(-245 + i * 16, -720, -245 + i * 16, -705, P(C(GDARK), 3))
        c.drawCircle(-230, -675, 7, P(C('#D32F2F')))
        c.drawLine(-246, -590, -214, -590, P(C(GOLD), 7))
        # modak bowl in lower left hand
        c.drawLine(165, -720, 230, -560, ap); c.drawLine(230, -560, 230, -545, ap)
        bw = skia.Path(); bw.moveTo(160, -560); bw.quadTo(230, -480, 300, -560); bw.close()
        modak(c, 205, -585, 20); modak(c, 255, -585, 20); modak(c, 230, -610, 20)
        c.drawPath(bw, P(C(GOLD))); c.drawPath(bw, P(C('#B8860B'), 3))
    # necklace
    c.drawArc(skia.Rect(-120, -820, 120, -660), 20, 140, False, P(C(GOLD), 10))
    c.drawCircle(0, -662, 14, P(C('#D32F2F'))); c.drawCircle(0, -662, 14, P(C(GOLD), 4))
    # ---- head ----
    hy = -880
    ef = math.sin(t * 2.2) * 0.06
    for sx in (-1, 1):
        c.save(); c.translate(sx * 120, hy + 10); c.scale(1 + ef, 1)
        c.drawOval(skia.Rect(-110 if sx < 0 else -20, -120, 20 if sx < 0 else 110, 130), P(C(GSKIN)))
        c.drawOval(skia.Rect(-90 if sx < 0 else -5, -95, 5 if sx < 0 else 90, 105), P(C('#F7B9A6')))
        c.drawOval(skia.Rect(-110 if sx < 0 else -20, -120, 20 if sx < 0 else 110, 130), P(C(GDARK), 4))
        c.restore()
    c.drawCircle(0, hy, 130, P(C(GSKIN)))
    c.drawOval(skia.Rect(-110, hy - 120, 110, hy + 20), P(C('#FFFFFF', 22)))
    # tusks: his right (viewer left) broken, left whole
    tk = skia.Path(); tk.moveTo(-58, hy + 70); tk.quadTo(-80, hy + 100, -86, hy + 118); tk.lineTo(-62, hy + 112); tk.quadTo(-52, hy + 92, -40, hy + 74); tk.close()
    c.drawPath(tk, P(C('#FFF8E8'))); c.drawPath(tk, P(C('#CDBFA6'), 2))
    tk2 = skia.Path(); tk2.moveTo(58, hy + 70); tk2.quadTo(110, hy + 130, 120, hy + 190); tk2.quadTo(88, hy + 140, 40, hy + 76); tk2.close()
    c.drawPath(tk2, P(C('#FFF8E8'))); c.drawPath(tk2, P(C('#CDBFA6'), 2))
    # trunk: down the middle, curling to viewer right
    sw = math.sin(t * 1.6) * 8
    pts = _bez((0, hy + 20), (-10, hy + 150), (-30, hy + 260), (30 + sw, hy + 300), 20) + _bez((30 + sw, hy + 300), (80 + sw, hy + 320), (110 + sw, hy + 270), (90 + sw, hy + 240), 10)[1:]
    _taper(c, pts, 63, 20, GDARK)
    _taper(c, pts, 58, 16, GSKIN)
    for i in range(3, 14, 2):
        px, py = pts[i]
        rr = lerp(58, 16, i / (len(pts) - 1))
        c.drawArc(skia.Rect(px - rr * .8, py - 8, px + rr * .8, py + 8), 20, 140, False, P(C(GDARK, 140), 3))
    # eyes
    for ex in (-52, 52):
        ey = hy - 18
        if eyes == 'closed' or ((t % 4.3) < .12 and eyes == 'open'):
            c.drawArc(skia.Rect(ex - 18, ey - 10, ex + 18, ey + 10), 20, 140, False, P(C('#3A1E10'), 5))
        elif eyes == 'happy':
            c.drawArc(skia.Rect(ex - 18, ey - 4, ex + 18, ey + 18), 200, 140, False, P(C('#3A1E10'), 5))
        else:
            c.drawOval(skia.Rect(ex - 17, ey - 15, ex + 17, ey + 15), P(C('#FFFFFF')))
            c.drawCircle(ex + look[0] * 5, ey + look[1] * 5 + 2, 10, P(C('#2B1A0E')))
            c.drawCircle(ex + look[0] * 5 + 3, ey + look[1] * 5 - 2, 3, P(C('#FFFFFF')))
        c.drawArc(skia.Rect(ex - 22, ey - 36, ex + 22, ey - 14), 200, 140, False, P(C('#5A2E1A'), 5))
    # smile at trunk base
    if talk and abs(math.sin(t * 12)) > .4:
        c.drawOval(skia.Rect(-58, hy + 58, -30, hy + 80), P(C('#7A2E1A')))
    else:
        c.drawArc(skia.Rect(-70, hy + 40, -26, hy + 76), 30, 120, False, P(C('#7A2E1A'), 5))
        c.drawArc(skia.Rect(26, hy + 40, 70, hy + 76), 30, 120, False, P(C('#7A2E1A'), 5))
    c.drawCircle(-80, hy + 30, 16, P(C('#E57373', 80))); c.drawCircle(80, hy + 30, 16, P(C('#E57373', 80)))
    # tilak
    tl = skia.Path(); tl.moveTo(0, hy - 120); tl.quadTo(16, hy - 85, 0, hy - 60); tl.quadTo(-16, hy - 85, 0, hy - 120); tl.close()
    c.drawPath(tl, P(C('#D32F2F')))
    for i in range(3): c.drawLine(-46, hy - 100 + i * 12, -20, hy - 100 + i * 12, P(C('#FFFFFF'), 5)); c.drawLine(20, hy - 100 + i * 12, 46, hy - 100 + i * 12, P(C('#FFFFFF'), 5))
    # crown (mukut)
    cr = skia.Path(); cr.moveTo(-100, hy - 105); cr.lineTo(-80, hy - 190); cr.lineTo(-48, hy - 215); cr.lineTo(-30, hy - 280)
    cr.lineTo(0, hy - 320); cr.lineTo(30, hy - 280); cr.lineTo(48, hy - 215); cr.lineTo(80, hy - 190); cr.lineTo(100, hy - 105); cr.quadTo(0, hy - 130, -100, hy - 105); cr.close()
    c.drawPath(cr, P(C(GOLD))); c.drawPath(cr, P(C('#B8860B'), 4))
    c.drawLine(-92, hy - 120, 92, hy - 120, P(C('#E65100'), 10))
    for jx, jy, col in ((0, hy - 200, '#D32F2F'), (-55, hy - 160, '#2E7D32'), (55, hy - 160, '#2E7D32'), (0, hy - 270, '#1565C0')):
        c.drawCircle(jx, jy, 13, P(C(col))); c.drawCircle(jx - 4, jy - 4, 4, P(C('#FFFFFF', 160)))
    c.drawCircle(0, hy - 330, 12, P(C(GOLD)))
    if hands == 'namaste':
        c.drawLine(-175, -540, -40, -505, ap); c.drawLine(175, -540, 40, -505, ap)
        pm = skia.Path(); pm.moveTo(0, -600); pm.quadTo(40, -545, 28, -470); pm.lineTo(-28, -470); pm.quadTo(-40, -545, 0, -600); pm.close()
        c.drawPath(pm, P(C(GSKIN))); c.drawPath(pm, P(C(GDARK), 3)); c.drawLine(0, -590, 0, -475, P(C(GDARK), 3))
        for sx in (-1, 1): c.drawLine(sx * 70, -528, sx * 76, -495, P(C(GOLD), 7))
    c.restore()

KSKIN = '#F1BE8E'

def _kartik_upper(c, s, t, mood, talk, spear=True, look=(0, 0), wave=False):
    """draws torso + head with waist at (0,0) in local coords (facing right)."""
    # spear (vel) behind, held in front hand
    if spear:
        c.drawLine(120, 60, 150, -560, P(C('#8D6E63'), 12))
        vl = skia.Path(); vl.moveTo(150, -560); vl.quadTo(195, -620, 152, -700); vl.quadTo(108, -620, 150, -560); vl.close()
        c.drawPath(vl, P(C('#ECEFF1'))); c.drawPath(vl, P(C('#90A4AE'), 4))
        c.drawRect(skia.Rect(132, -575, 168, -555), P(C(GOLD)))
    tor = skia.Path(); tor.moveTo(-80, -260); tor.quadTo(0, -282, 80, -260); tor.lineTo(64, 0); tor.lineTo(-64, 0); tor.close()
    c.drawPath(tor, P(C(KSKIN)))
    c.drawArc(skia.Rect(-60, -300, 60, -170), 20, 140, False, P(C(GOLD), 9))
    th = skia.Path(); th.moveTo(-70, -250); th.quadTo(10, -120, 60, -10); c.drawPath(th, P(C('#FFF8E1'), 5))
    ap = P(C(KSKIN), 30)
    c.drawLine(-75, -245, -100, -90, ap); c.drawCircle(-102, -78, 20, P(C(KSKIN)))
    if wave:
        c.drawLine(75, -245, 160, -330, ap); c.drawCircle(168, -340, 20, P(C(KSKIN)))
    else:
        c.drawLine(75, -245, 118, -120, ap); c.drawLine(118, -120, 128, -90, ap); c.drawCircle(130, -80, 20, P(C(KSKIN)))
    for sx, yy in ((-1, -120), (1, -150)): c.drawLine(sx * 100 - 16 * sx, yy, sx * 100 + 16 * sx, yy, P(C(GOLD), 6))
    c.drawRect(skia.Rect(-20, -320, 20, -270), P(C(KSKIN)))
    cy = -390
    c.drawOval(skia.Rect(-74, cy - 78, 74, cy + 20), P(C('#1E140E')))
    face(c, 0, cy, 70, KSKIN, mood, talk, t, look)
    mouth(c, 0, cy + 36, 70, mood, talk, t)
    c.drawLine(0, cy - 52, 0, cy - 34, P(C('#D32F2F'), 6))
    cr = skia.Path(); cr.moveTo(-62, cy - 50); cr.lineTo(-50, cy - 120); cr.lineTo(-20, cy - 95); cr.lineTo(0, cy - 150); cr.lineTo(20, cy - 95); cr.lineTo(50, cy - 120); cr.lineTo(62, cy - 50); cr.quadTo(0, cy - 70, -62, cy - 50); cr.close()
    c.drawPath(cr, P(C(GOLD))); c.drawPath(cr, P(C('#B8860B'), 3)); c.drawCircle(0, cy - 90, 9, P(C('#D32F2F')))
    for sx in (-1, 1): c.drawCircle(sx * 70, cy + 22, 9, P(C(GOLD)))

def kartikeya(c, x, gy, s=1.0, t=0.0, mood='neutral', facing=1, talk=False, spear=True, look=(0, 0), wave=False):
    """Kartikeya ji standing, ~ 860 tall at s=1 (feet at gy)."""
    c.save(); c.translate(x, gy); c.scale(s * facing, s)
    c.drawOval(skia.Rect(-70, -16, -10, 8), P(C(KSKIN))); c.drawOval(skia.Rect(10, -16, 70, 8), P(C(KSKIN)))
    dh = skia.Path(); dh.moveTo(-70, -430); dh.lineTo(70, -430); dh.lineTo(80, -20); dh.lineTo(8, -20); dh.lineTo(0, -200); dh.lineTo(-8, -20); dh.lineTo(-80, -20); dh.close()
    c.drawPath(dh, P(C('#D32F2F'))); c.drawLine(-80, -24, 80, -24, P(C(GOLD), 8))
    c.translate(0, -430)
    _kartik_upper(c, s, t, mood, talk, spear, look, wave)
    c.restore()

def peacock(c, x, y, s=1.0, t=0.0, flap=1.0, rider=False, rider_mood='happy', facing=1, tail_open=0.0):
    """Mor (peacock), side view facing right; body centre at (x, y). ~ 900 wide with train at s=1.
    rider=True draws Kartikeya ji sitting on its back."""
    c.save(); c.translate(x, y); c.scale(s * facing, s)
    # train (tail) streaming left
    rnd = random.Random(3)
    for i in range(11):
        a = math.radians(lerp(-8, 8, i / 10)) - tail_open * math.radians(lerp(-60, 60, i / 10))
        L_ = 640 - abs(i - 5) * 22
        wv = math.sin(t * 3 + i) * 10
        ex, ey = -60 - math.cos(a) * L_, 10 - math.sin(a) * L_ * .9 + wv
        c.drawLine(-60, 10, ex, ey, P(C('#2E7D32'), 8))
        for k in range(3):
            f = 0.45 + k * 0.25
            px, py = lerp(-60, ex, f), lerp(10, ey, f)
            c.drawOval(skia.Rect(px - 34, py - 24, px + 34, py + 24), P(C('#43A047')))
            c.drawOval(skia.Rect(px - 20, py - 15, px + 20, py + 15), P(C('#FFC107')))
            c.drawOval(skia.Rect(px - 13, py - 10, px + 13, py + 10), P(C('#00897B')))
            c.drawCircle(px, py, 6, P(C('#0D47A1')))
    # far wing
    fl = math.sin(t * 9) * 40 * flap
    wg = skia.Path(); wg.moveTo(-40, -30); wg.quadTo(20, -180 - fl, 140, -150 - fl * 1.4); wg.quadTo(90, -60, 40, -20); wg.close()
    c.drawPath(wg, P(C('#8D6E63')))
    # body
    c.drawOval(skia.Rect(-120, -70, 130, 80), P(C('#1565C0')))
    c.drawOval(skia.Rect(-90, -40, 60, 60), P(C('#1E88E5')))
    # legs
    c.drawLine(10, 70, 0, 150, P(C('#BCAAA4'), 8)); c.drawLine(50, 70, 60, 150, P(C('#BCAAA4'), 8))
    # neck + head
    nk = skia.Path(); nk.moveTo(70, -30); nk.quadTo(150, -80, 150, -200); nk.lineTo(190, -205); nk.quadTo(190, -60, 120, 20); nk.close()
    c.drawPath(nk, P(C('#1565C0')))
    c.drawCircle(172, -220, 34, P(C('#1565C0')))
    bk = skia.Path(); bk.moveTo(198, -228); bk.lineTo(236, -214); bk.lineTo(198, -206); bk.close(); c.drawPath(bk, P(C('#FFB300')))
    c.drawCircle(180, -226, 9, P(C('#FFFFFF'))); c.drawCircle(183, -226, 5, P(C('#111111')))
    c.drawLine(176, -212, 196, -216, P(C('#FFFFFF'), 4))
    for i in range(3):
        c.drawLine(165 - i * 8, -252, 160 - i * 14, -300, P(C('#1565C0'), 3)); c.drawCircle(160 - i * 14, -302, 7, P(C('#1E88E5')))
    wg2 = skia.Path(); wg2.moveTo(-60, -10); wg2.quadTo(-10, -150 - fl * 1.2, 110, -120 - fl * 1.6); wg2.quadTo(70, -10, 20, 20); wg2.close()
    if rider:
        wg2 = skia.Path(); wg2.moveTo(-90, 10); wg2.quadTo(-150, -110 - fl * 1.2, -40, -100 - fl * 1.4); wg2.quadTo(-20, -20, 0, 30); wg2.close()
    c.drawPath(wg2, P(C('#A1887F'))); c.drawPath(wg2, P(C('#6D4C41'), 3))
    if rider:
        c.save(); c.translate(0, -50); c.scale(0.62, 0.62)
        lg = skia.Path(); lg.moveTo(-60, 0); lg.lineTo(70, -10); lg.lineTo(90, 80); lg.lineTo(40, 90); lg.lineTo(30, 30); lg.lineTo(-50, 30); lg.close()
        c.drawPath(lg, P(C('#D32F2F'))); c.drawOval(skia.Rect(30, 80, 100, 104), P(C(KSKIN)))
        _kartik_upper(c, 1, t, rider_mood, False, True, (1, 0))
        c.restore()
    c.restore()

def mushak(c, x, gy, s=1.0, t=0.0, facing=1, walk=0.0, look_up=0.0, modak_=True):
    """Mooshak (mouse), side view facing right, ~180 tall at s=1, feet at gy."""
    c.save(); c.translate(x, gy); c.scale(s * facing, s)
    b = math.sin(t * 18) * 6 * walk
    tl = skia.Path(); tl.moveTo(-90, -50); tl.quadTo(-180, -40 + b, -200, -110); c.drawPath(tl, P(C('#E8A0A0'), 7))
    for lx in (-50, 40): c.drawLine(lx, -30, lx + b, 0, P(C('#E8A0A0'), 10))
    c.drawOval(skia.Rect(-110, -150, 80, -20), P(C('#8D8D99')))
    c.drawOval(skia.Rect(-80, -120, 40, -40), P(C('#A3A3AE')))
    hx, hy = 80, -110 - look_up * 30
    c.drawCircle(hx - 10, hy - 50, 34, P(C('#8D8D99'))); c.drawCircle(hx - 10, hy - 50, 20, P(C('#F3B6C0')))
    hd = skia.Path(); hd.moveTo(hx - 50, hy - 40); hd.quadTo(hx + 10, hy - 70, hx + 80, hy + 6); hd.quadTo(hx + 20, hy + 40, hx - 50, hy + 30); hd.close()
    c.drawPath(hd, P(C('#8D8D99')))
    c.drawCircle(hx + 80, hy + 4, 10, P(C('#E57373')))
    c.drawCircle(hx + 22, hy - 16, 9, P(C('#111111'))); c.drawCircle(hx + 25, hy - 19, 3, P(C('#FFFFFF')))
    for k in (-1, 0, 1): c.drawLine(hx + 60, hy + 8, hx + 110, hy + 8 + k * 14, P(C('#555555'), 2))
    if modak_: modak(c, hx + 30, hy + 50, 18)
    c.restore()

def globe(c, x, y, r, t=0.0, a=1.0):
    """prithvi (earth) seen from space."""
    c.saveLayer(None, skia.Paint(Alphaf=clamp(a)))
    c.drawCircle(x, y, r + 14, P(C('#90CAF9', 90)))
    c.drawCircle(x, y, r, P(C('#1E88E5')))
    c.save(); pth = skia.Path(); pth.addCircle(x, y, r); c.clipPath(pth, skia.ClipOp.kIntersect, True)
    off = (t * 30) % (r * 4)
    for k in range(3):
        bx = x - r * 2 + off + k * r * 1.4 - r * 2
        for dx in (0, r * 4):
            cx_ = bx + dx
            m = skia.Path(); m.moveTo(cx_, y - r * .6); m.quadTo(cx_ + r * .5, y - r * .7, cx_ + r * .45, y - r * .1); m.quadTo(cx_ + r * .2, y + r * .5, cx_ - r * .05, y + r * .3); m.quadTo(cx_ - r * .3, y - r * .2, cx_, y - r * .6)
            c.drawPath(m, P(C('#43A047')))
    c.drawCircle(x + r * .35, y + r * .35, r * 1.05, P(C('#0D47A1', 70)))
    c.restore()
    c.drawCircle(x - r * .35, y - r * .4, r * .25, P(C('#FFFFFF', 60)))
    c.restore()

def orbit(c, x, y, rx, ry, prog, col='#FFE082', w=8, a=1.0):
    """dashed orbit ellipse; prog 0..1 how much of the path is lit."""
    ov = skia.Rect(x - rx, y - ry, x + rx, y + ry)
    p = P(C(col, int(90 * a)), w); p.setPathEffect(skia.DashPathEffect.Make([22, 18], 0))
    c.drawOval(ov, p)
    if prog > 0: c.drawArc(ov, 90, 360 * min(prog, 1), False, P(C(col, int(255 * a)), w))

def petals(c, t, a=1.0, seed=5, n=40):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W); sp_ = rnd.uniform(120, 260); ph = rnd.uniform(0, 3000)
        y = (ph + t * sp_) % (H * .8) - 60; x = x0 + math.sin(t * 2 + i) * 30
        col = rnd.choice(['#FF7043', '#FFB300', '#F06292', '#FFEB3B'])
        c.save(); c.translate(x, y); c.rotate(t * 90 + i * 30)
        c.drawOval(skia.Rect(-14, -8, 14, 8), P(C(col, int(230 * a)))); c.restore()
