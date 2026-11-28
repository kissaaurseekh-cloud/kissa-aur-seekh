import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from mart import sparkle as _sp
from gnart import petals
from vart import *
from art import tree
from gart import face, mouth
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        # v2 pacing: voice starts on frame 1, tiny gaps; only the big moments get a breath
        lead = {'hook': 0.0}.get(sid, 0.05)
        gap = {'lesson': 0.15}.get(sid, 0.06)
        tail = {'outro': 0.5, 'lesson': 0.35, 'reveal': 0.6, 'strain': 0.3, 'lift': 0.25, 'order': 0.2, 'hook': 0.1}.get(sid, 0.12)
        t = lead; L = []
        for i, item in enumerate(lines):
            txt = item[2] if len(item) > 2 else item[1]
            d = DUR[f'vo/{sid}_{i}.wav']; L.append((t, t + d, txt, f'vo/{sid}_{i}.wav')); t += d + gap
        tl.append((sid, t - gap + tail, L))
    return tl

def text_img(txt, size, font=FB, maxw=920, fill=(255, 255, 255, 255), stroke=(20, 12, 6, 255), sw=6, box=False):
    f = ImageFont.truetype(font, size, layout_engine=ImageFont.Layout.RAQM)
    words = txt.split(' '); lines = []; cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if f.getlength(test) > maxw and cur: lines.append(cur); cur = w
        else: cur = test
    lines.append(cur)
    lh = int(size * 1.4); wmax = int(max(f.getlength(l) for l in lines)) + sw * 2 + 10
    pad = 34 if box else 12
    img = Image.new('RGBA', (wmax + pad * 2, lh * len(lines) + pad * 2 - int(size * .15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if box: d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=30, fill=(15, 10, 6, 175))
    for i, l in enumerate(lines):
        d.text((pad + (wmax - f.getlength(l)) / 2, pad + i * lh - int(size * .1)), l, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return skia.Image.fromarray(np.ascontiguousarray(np.array(img)), colorType=skia.kRGBA_8888_ColorType)

_cache = {}
def T(key, *a, **k):
    if key not in _cache: _cache[key] = text_img(*a, **k)
    return _cache[key]

def draw_img(c, img, cx, cy, alpha=1.0, scale=1.0):
    p = skia.Paint(AntiAlias=True); p.setAlphaf(clamp(alpha))
    w, h = img.width() * scale, img.height() * scale
    c.drawImageRect(img, skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear), p)

def subtitle(c, L, t):
    idx = None
    for i, it in enumerate(L):
        if t >= it[0] - 0.05: idx = i
    if idx is None: return
    a, b, txt, _ = L[idx]
    end = L[idx + 1][0] - 0.05 if idx + 1 < len(L) else b + 0.3
    if t > end: return
    img = T(('sub', txt), txt, 58, box=True, sw=0)
    k = clamp((t - a + 0.05) / 0.1)
    draw_img(c, img, W / 2, 1440, min(k, clamp((end - t) / 0.06) if idx + 1 == len(L) else 1), 0.94 + 0.06 * ease(k))

def lt(L, i, t): return clamp((t - L[i][0]) / (L[i][1] - L[i][0]))
def sp(L, i, t): return L[i][0] <= t <= L[i][1]
def after(L, i, t, d=0): return t >= L[i][0] + d

def zoom(c, cx, cy, z):
    c.translate(W / 2, 760); c.scale(z, z); c.translate(-cx, -cy)





GROUND = 1335

def swarg(c, t, dim=0.0, angry=0.0):
    """Swarg (Indra's heaven): sky, golden palace on clouds, cloud floor. dim -> grey (Lakshmi gone), angry -> red."""
    def col(h):
        cc = mixc(h, '#3A3D52', dim * 0.75)
        return cc
    def mx(h):  # hex mix for angry then dim
        r1 = int(h[1:3], 16); g1 = int(h[3:5], 16); b1 = int(h[5:7], 16)
        r2, g2, b2 = 0xC0, 0x30, 0x28

GROUND = 1335
BSKIN = '#C98B5B'      # Bhima
HFUR = '#E2632B'       # Hanuman ji (sindoor-orange)
HFACE = '#F6B27A'
OFUR = '#8E6A50'       # old monkey form (greyish brown)
OFACE = '#EBD3B4'

def forest(c, t, glow=0.0, dim=0.0):
    """Gandhamadan forest: sky, blue hills, trees, grass and a dirt path across the screen."""
    def col(h): return mixc(h, '#3A3D52', dim * .6)
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1150)], [col('#7CC8F2'), col('#E6F6DA')]))
    c.drawRect(skia.Rect(0, 0, W, 1200), p)
    for k in range(4): c.drawCircle(900, 260, 70 + k * 45, P(C('#FFF6C8', 50 if k else 255)))
    for i, (cx, cy, s) in enumerate([(150, 380, 1.0), (700, 470, .8), (420, 250, .7)]):
        cloud(c, (cx + t * (8 + i * 3)) % 1300 - 110, cy, s, '#FFFFFF', 210)
    for pts, cc in [([(0, 900), (180, 640), (360, 820), (560, 600), (780, 830), (960, 650), (1080, 760), (1080, 1000), (0, 1000)], '#8DB6D6'),
                    ([(0, 980), (220, 800), (420, 950), (650, 780), (900, 960), (1080, 840), (1080, 1100), (0, 1100)], '#6FA58F')]:
        pp = skia.Path(); pp.moveTo(*pts[0])
        for q in pts[1:]: pp.lineTo(*q)
        pp.close(); c.drawPath(pp, P(col(cc)))
    c.drawRect(skia.Rect(0, 1060, W, H), P(col('#6DBE4B')))
    c.save(); c.clipRect(skia.Rect(0, 0, W, 1098))
    for x, s in [(80, .75), (330, .6), (620, .7), (980, .8)]:
        tree(c, x, 1090, s, t, fruit=0.0)
    c.restore()
    # path
    pp = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 1180), skia.Point(0, H)], [col('#D9B07A'), col('#B98B55')]))
    path = skia.Path(); path.moveTo(0, 1200); path.quadTo(540, 1150, W, 1210); path.lineTo(W, H); path.lineTo(0, H); path.close()
    c.drawPath(path, pp)
    rnd = random.Random(4)
    for i in range(26):
        x = rnd.uniform(0, W); y = rnd.uniform(1250, 1900)
        c.drawOval(skia.Rect.MakeXYWH(x, y, 16, 8), P(mixc('#9C7446', '#3A3D52', dim * .6, 150)))
    for i in range(14):   # flowers on the grass edge
        x = i * 80 + 20; y = 1150 + (i % 3) * 14 + math.sin(t * 2 + i) * 3
        cc = ['#FF7043', '#FFD54F', '#F06292', '#FFFFFF'][i % 4]
        for j in range(5):
            a = j / 5 * math.tau
            c.drawCircle(x + math.cos(a) * 8, y + math.sin(a) * 8, 7, P(col(cc)))
        c.drawCircle(x, y, 5, P(C('#E65100')))
    if glow > 0:
        light_rays(c, 540, 760, t, glow, col='#FFE9A0')

def monkey_face(c, cx, cy, r, fur, fc, eyes='open', look=(0, 0), talk=False, t=0.0, old=False, smile=True, blink_off=0.0):
    for sx in (-1, 1):
        c.drawCircle(cx + sx * r * .98, cy - r * .02, r * .3, P(C(fur))); c.drawCircle(cx + sx * r * .98, cy - r * .02, r * .17, P(C(fc)))
    c.drawCircle(cx, cy, r, P(C(fur)))
    c.drawOval(skia.Rect(cx - r * .78, cy - r * .62, cx + r * .78, cy + r * .9), P(C(fc)))
    # brow ridge
    br = skia.Path(); br.moveTo(cx - r * .7, cy - r * .3); br.quadTo(cx - r * .35, cy - r * .62, cx, cy - r * .36)
    br.quadTo(cx + r * .35, cy - r * .62, cx + r * .7, cy - r * .3); br.quadTo(cx, cy - r * .5, cx - r * .7, cy - r * .3)
    c.drawPath(br, P(C('#EEEEEE' if old else blend(fur, '#3A1A08', .35))))
    ey = cy - r * .16; lx, ly = look
    bl = ((t + blink_off) % 3.7) < 0.12
    for sx in (-1, 1):
        ex = cx + sx * r * .33
        if eyes == 'closed' or bl:
            c.drawArc(skia.Rect(ex - r * .15, ey - r * .1, ex + r * .15, ey + r * .1), 10, 160, False, P(C('#3A1A08'), max(3, r * .05)))
        else:
            er = r * .15; hh = .55 if eyes == 'half' else 1.0
            c.drawOval(skia.Rect(ex - er, ey - er * 1.1 * hh, ex + er, ey + er * 1.1), P(C('#FFFFFF')))
            c.drawCircle(ex + lx * er * .35, ey + ly * er * .3 + (er * .3 if eyes == 'half' else 0), er * .6, P(C('#2B1A0E')))
            c.drawCircle(ex + lx * er * .35 + er * .2, ey + ly * er * .3 - er * .2, er * .18, P(C('#FFFFFF')))
            if eyes == 'half':
                c.drawLine(ex - er * 1.05, ey - er * .55, ex + er * 1.05, ey - er * .55, P(C(fc), er * .9))
    # muzzle (strong jaw = "hanu")
    mz = skia.Rect(cx - r * .58, cy + r * .08, cx + r * .58, cy + r * .95)
    c.drawOval(mz, P(C(blend(fc, '#FFFFFF', .25))))
    c.drawCircle(cx - r * .1, cy + r * .3, r * .05, P(C('#5A2A10'))); c.drawCircle(cx + r * .1, cy + r * .3, r * .05, P(C('#5A2A10')))
    my = cy + r * .58
    if talk:
        o = abs(math.sin(t * 12)) * .8 + .2
        c.drawOval(skia.Rect(cx - r * .2, my - r * .04, cx + r * .2, my + r * .06 + r * .2 * o), P(C('#6A2414')))
    elif smile:
        c.drawArc(skia.Rect(cx - r * .32, my - r * .2, cx + r * .32, my + r * .14), 20, 140, False, P(C('#6A2414'), max(3, r * .05)))
    else:
        c.drawLine(cx - r * .2, my, cx + r * .2, my, P(C('#6A2414'), max(3, r * .05)))
    if old:
        bd = skia.Path(); bd.moveTo(cx - r * .5, cy + r * .75); bd.quadTo(cx, cy + r * 1.35, cx + r * .5, cy + r * .75); bd.quadTo(cx, cy + r * .98, cx - r * .5, cy + r * .75)
        c.drawPath(bd, P(C('#F2F2F2')))

def tail_path(x0, y0, pts):
    p = skia.Path(); p.moveTo(x0, y0)
    for a in pts: p.cubicTo(*a)
    return p

def old_monkey(c, *a, **kw):
    """old monkey with a dark outline so he reads against the dirt path."""
    rec = skia.PictureRecorder(); rc = rec.beginRecording(skia.Rect(-W, -H, 2 * W, 2 * H))
    rc.setMatrix(c.getTotalMatrix())
    _old_monkey(rc, *a, **kw)
    pic = rec.finishRecordingAsPicture()
    c.save(); c.resetMatrix()
    op = skia.Paint(ImageFilter=skia.ImageFilters.Dilate(5, 5), ColorFilter=skia.ColorFilters.Blend(C('#3E2614'), skia.BlendMode.kSrcIn))
    c.saveLayer(None, op); c.drawPicture(pic); c.restore()
    c.drawPicture(pic); c.restore()

def _old_monkey(c, x, gy, s=1.0, t=0.0, grip=None, wob=0.0, talk=False, eyes='half', look=(1, 0), blink_off=0.0, tip_dx=260):
    """old monkey (Hanuman ji in disguise) lying on the path, head on his arm at the left, long tail to the right.
    grip = (gx, gy) where someone holds the tail (it is lifted there), else the tail lies on the ground."""
    k = s
    # tail first (behind the legs)
    rx, ry = x + 330 * k, gy - 95 * k
    if grip is None:
        gxp, gyp = x + 650 * k, gy - 22 * k
    else:
        gxp, gyp = grip
    gyp += math.sin(t * 40) * wob
    tipx, tipy = gxp + tip_dx * k, (gy - 30 * k if grip is None else gyp + 70 * k)
    tp = skia.Path(); tp.moveTo(rx, ry)
    tp.cubicTo(rx + 90 * k, ry + 10 * k, rx + 120 * k, gy - 18 * k, (rx + gxp) / 2 + 40 * k, gy - 20 * k)
    tp.cubicTo(gxp - 120 * k, gy - 22 * k, gxp - 60 * k, gyp, gxp, gyp)
    tp.cubicTo(gxp + 80 * k, gyp, tipx - 60 * k, tipy - 60 * k, tipx, tipy)
    c.drawPath(tp, P(C(blend(OFUR, '#2A1608', .45)), 46 * k)); c.drawPath(tp, P(C(OFUR), 34 * k))
    c.drawPath(tp, P(C(blend(OFUR, '#FFFFFF', .2)), 8 * k))
    c.drawCircle(tipx, tipy, 30 * k, P(C(blend(OFUR, '#2A1608', .3))))
    # legs (curled)
    c.drawOval(skia.Rect(x + 250 * k, gy - 150 * k, x + 400 * k, gy - 10 * k), P(C(blend(OFUR, '#000000', .08))))
    c.drawOval(skia.Rect(x + 360 * k, gy - 50 * k, x + 450 * k, gy), P(C(OFACE)))
    # body lying
    breath = math.sin(t * 2) * 4 * k
    c.drawOval(skia.Rect(x + 20 * k, gy - 200 * k - breath, x + 360 * k, gy - 10 * k), P(C(OFUR)))
    c.drawOval(skia.Rect(x + 70 * k, gy - 110 * k, x + 300 * k, gy - 20 * k), P(C(OFACE, 170)))
    # red cloth (langot) and a simple janeu
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x + 255 * k, gy - 175 * k, x + 290 * k, gy - 20 * k), 14 * k, 14 * k), P(C('#C62828')))
    # arm under head
    c.drawLine(x + 80 * k, gy - 60 * k, x - 40 * k, gy - 40 * k, P(C(OFUR), 42 * k))
    c.drawCircle(x - 50 * k, gy - 40 * k, 24 * k, P(C(OFACE)))
    monkey_face(c, x - 10 * k, gy - 170 * k, 105 * k, OFUR, OFACE, eyes, look, talk, t, old=True, blink_off=blink_off)

def bhima(c, x, gy, s=1.0, t=0.0, mood='neutral', arm='gada', facing=1, look=(0, 0), talk=False, lean=0.0, strain=0.0, blink_off=0.0, bow=0.0):
    """Bhima: big bare-chested warrior, yellow dhoti, red sash, gold mukut and armbands, gada. Feet at gy."""
    k = s * 1.15
    c.save(); c.translate(x, gy); c.scale(k * facing, k)
    if lean: c.rotate(lean)
    sk = blend(BSKIN, '#D2453A', strain * .35)
    # legs
    for lx in (-30, 30):
        c.drawLine(lx, -120, lx * 1.3, -8, P(C(BSKIN), 30))
        c.drawOval(skia.Rect(lx * 1.3 - 30, -16, lx * 1.3 + 30, 6), P(C('#6B4226')))
    # dhoti
    dh = skia.Path(); dh.moveTo(-80, -235); dh.lineTo(80, -235); dh.lineTo(100, -110); dh.quadTo(0, -90, -100, -110); dh.close()
    c.drawPath(dh, P(C('#F9A825'))); c.drawLine(-98, -112, 98, -112, P(C('#C62828'), 10))
    c.drawLine(0, -230, 6, -100, P(C('#E08E00'), 6))
    if bow: c.translate(0, -235); c.rotate(bow); c.translate(0, 235)
    def arm_line(sh, el, hd, front=True):
        ap = P(C(BSKIN), 38)
        c.drawLine(sh[0], sh[1], el[0], el[1], ap); c.drawLine(el[0], el[1], hd[0], hd[1], ap)
        c.drawLine(sh[0] + (el[0] - sh[0]) * .35 - 14, sh[1] + (el[1] - sh[1]) * .35, sh[0] + (el[0] - sh[0]) * .35 + 14, sh[1] + (el[1] - sh[1]) * .35, P(C('#FFC107'), 12))
        c.drawCircle(hd[0], hd[1], 23, P(C(BSKIN)))
    poses = {
        'down': (((-90, -410), (-108, -320), (-110, -230)), ((90, -410), (108, -320), (110, -230))),
        'gada': (((-90, -410), (-108, -320), (-110, -230)), ((90, -410), (130, -330), (112, -255))),
        'point': (((-90, -410), (-108, -320), (-110, -230)), ((90, -410), (170, -405), (232, -400))),
        'lift1': (((-90, -410), (-108, -320), (-110, -230)), ((90, -410), (160, -330), (205, -245))),
        'lift2': (((-90, -410), (30, -330), (150, -245)), ((90, -410), (165, -330), (205, -245))),
        'namaste': (((-90, -410), (-60, -310), (20, -385)), ((90, -410), (100, -310), (30, -385))),
        'touch': (((-90, -410), (40, -330), (140, -250)), ((90, -410), (160, -330), (200, -250))),
    }
    back, front = poses.get(arm, poses['down'])
    arm_line(*back)
    # torso (V shape, bare chest)
    tp = skia.Path(); tp.moveTo(-100, -430); tp.quadTo(0, -460, 100, -430); tp.lineTo(72, -225); tp.lineTo(-72, -225); tp.close()
    c.drawPath(tp, P(C(sk)))
    mp = P(C(blend(BSKIN, '#5A3010', .35)), 4)
    c.drawArc(skia.Rect(-70, -410, 0, -340), 20, 140, False, mp); c.drawArc(skia.Rect(0, -410, 70, -340), 20, 140, False, mp)
    for yy in (-320, -290, -260): c.drawLine(-20, yy, -6, yy, mp); c.drawLine(6, yy, 20, yy, mp)
    c.drawRect(skia.Rect(-76, -245, 76, -220), P(C('#C62828')))
    c.drawArc(skia.Rect(-48, -470, 48, -395), 20, 140, False, P(C('#FFC107'), 7))
    c.drawRect(skia.Rect(-18, -475, 18, -428), P(C(BSKIN)))
    # head
    cy = -545
    c.drawOval(skia.Rect(-80, cy - 80, 80, cy + 30), P(C('#1E1410')))
    ey = face(c, 0, cy, 70, sk, mood if mood != 'strain' else 'sad', False, t, look, blink_off)
    if mood == 'angry' or mood == 'strain':
        bp = P(C('#1E1410'), 8); by = cy - 12 - 22
        c.drawLine(-42, by - 10, -12, by + 6, bp); c.drawLine(42, by - 10, 12, by + 6, bp)
    # mustache
    mu = skia.Path(); mu.moveTo(-42, cy + 30); mu.quadTo(-20, cy + 14, 0, cy + 24); mu.quadTo(20, cy + 14, 42, cy + 30); mu.quadTo(0, cy + 32, -42, cy + 30)
    c.drawPath(mu, P(C('#1E1410')))
    if mood == 'strain':
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-22, cy + 36, 22, cy + 52), 5, 5), P(C('#FFFFFF')))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-22, cy + 36, 22, cy + 52), 5, 5), P(C('#5A1E10'), 3))
    else:
        mouth(c, 0, cy + 36, 70, {'angry': 'neutral'}.get(mood, mood), talk, t)
    # mukut
    cr = skia.Path(); cr.moveTo(-60, cy - 50); cr.lineTo(-50, cy - 130); cr.lineTo(-24, cy - 105); cr.lineTo(0, cy - 175); cr.lineTo(24, cy - 105)
    cr.lineTo(50, cy - 130); cr.lineTo(60, cy - 50); cr.close()
    c.drawPath(cr, P(C('#FFC107'))); c.drawPath(cr, P(C('#B8860B'), 3))
    c.drawRect(skia.Rect(-63, cy - 70, 63, cy - 50), P(C('#E0A800'))); c.drawCircle(0, cy - 100, 10, P(C('#E53935')))
    for sx in (-1, 1): c.drawCircle(sx * 70, cy + 22, 9, P(C('#FFC107')))
    if arm == 'gada':
        gada(c, 120, -470, -150, 1.0)
    arm_line(*front)
    if strain > 0:   # sweat drops
        for i in range(3):
            ph = (t * 1.6 + i / 3) % 1
            dx = [-80, 85, 60][i]; dy = cy - 40 + ph * 120
            d = skia.Path(); d.moveTo(dx, dy - 16); d.quadTo(dx + 10, dy, dx, dy + 6); d.quadTo(dx - 10, dy, dx, dy - 16)
            c.drawPath(d, P(C('#BDE8FF', int(230 * strain * (1 - ph)))))
    c.restore()

def bhima_hand(x, gy, s, facing, arm='lift1'):
    k = s * 1.15; hx, hy = {'lift1': (205, -245), 'lift2': (205, -245), 'touch': (200, -250)}[arm]
    return x + hx * k * facing, gy + hy * k

def hanuman(c, x, gy, s=1.0, t=0.0, aura=0.0, talk=False, look=(0, 0), bless=True, blink_off=0.0):
    """Shri Hanuman ji, front view, ~1260 tall at s=1 (mukut top ~gy-1260). Sindoor-orange body, red dhoti with
    gold border, yellow angavastra, janeu, gold mukut and kundal, gada in his left hand, right hand in abhaya mudra."""
    c.save(); c.translate(x, gy); c.scale(s, s)
    if aura > 0:
        for kk in range(5): c.drawCircle(0, -1020, 150 + kk * 55, P(C('#FFE082', int(55 * aura))))
        c.drawCircle(0, -1020, 160, P(C('#FFD54F', int(170 * aura)), 10))
    # tail (behind), curling up on his left
    sw = math.sin(t * 2) * 15
    tl = skia.Path(); tl.moveTo(60, -520); tl.cubicTo(260, -500, 330 + sw, -760, 260 + sw, -950)
    tl.cubicTo(230 + sw, -1040, 320 + sw, -1080, 340 + sw, -1010)
    c.drawPath(tl, P(C(blend(HFUR, '#7A2A08', .3)), 44)); c.drawPath(tl, P(C(HFUR), 34))
    # legs + feet
    for lx in (-55, 55):
        c.drawLine(lx, -220, lx * 1.2, -20, P(C(HFUR), 50))
        c.drawOval(skia.Rect(lx * 1.2 - 42, -30, lx * 1.2 + 42, 6), P(C(HFACE)))
        c.drawLine(lx * 1.2 - 22, -60, lx * 1.2 + 22, -60, P(C('#FFC107'), 8))
    # dhoti
    dh = skia.Path(); dh.moveTo(-150, -580); dh.lineTo(150, -580); dh.lineTo(190, -220); dh.quadTo(0, -190, -190, -220); dh.close()
    c.drawPath(dh, P(C('#D32F2F')))
    c.drawLine(-188, -222, 188, -222, P(C('#FFC107'), 14))
    c.drawLine(0, -575, 0, -210, P(C('#FFC107'), 10))
    c.drawRect(skia.Rect(-158, -600, 158, -560), P(C('#FFC107')))
    # torso
    tp = skia.Path(); tp.moveTo(-170, -890); tp.quadTo(0, -930, 170, -890); tp.lineTo(140, -585); tp.lineTo(-140, -585); tp.close()
    c.drawPath(tp, P(C(HFUR)))
    mp = P(C(blend(HFUR, '#6A2008', .4)), 5)
    c.drawArc(skia.Rect(-120, -870, 0, -760), 20, 140, False, mp); c.drawArc(skia.Rect(0, -870, 120, -760), 20, 140, False, mp)
    for yy in (-720, -680, -640): c.drawLine(-28, yy, -10, yy, mp); c.drawLine(10, yy, 28, yy, mp)
    c.drawLine(-120, -880, 110, -600, P(C('#FFFFFF'), 7))   # janeu
    # angavastra (yellow scarf) over shoulders
    an = skia.Path(); an.moveTo(-175, -880); an.quadTo(0, -800, 175, -880); an.lineTo(175, -850); an.quadTo(0, -770, -175, -850); an.close()
    c.drawPath(an, P(C('#FFB300')))
    c.drawLine(172, -860, 205, -640, P(C('#FFB300'), 26)); c.drawLine(-172, -860, -205, -640, P(C('#FFB300'), 26))
    # necklace
    c.drawArc(skia.Rect(-80, -960, 80, -840), 20, 140, False, P(C('#FFC107'), 9))
    for i in range(7):
        a = math.radians(30 + i * 20); c.drawCircle(math.cos(a) * 80, -900 + math.sin(a) * 60, 7, P(C('#E53935')))
    ap = P(C(HFUR), 52)
    # right hand (viewer left): abhaya mudra / blessing
    if bless:
        c.drawLine(-165, -870, -250, -730, ap); c.drawLine(-250, -730, -230, -860, ap)
        c.drawLine(-225, -805, -205, -805, P(C('#FFC107'), 14))
        palm = skia.RRect.MakeRectXY(skia.Rect(-268, -945, -196, -855), 30, 30); c.drawRRect(palm, P(C(HFACE)))
        for i in range(4): c.drawLine(-258 + i * 18, -940, -258 + i * 18, -965 + abs(i - 1.5) * 6, P(C(HFACE), 15))
        c.drawCircle(-232, -895, 9, P(C('#E53935')))
    else:
        c.drawLine(-165, -870, -230, -720, ap); c.drawLine(-230, -720, -235, -600, ap); c.drawCircle(-235, -590, 30, P(C(HFACE)))
    # left hand (viewer right) holding the gada
    c.drawLine(165, -870, 245, -730, ap); c.drawLine(245, -730, 250, -610, ap)
    c.drawLine(195, -795, 222, -790, P(C('#FFC107'), 14))
    gada(c, 255, -930, -480, 1.45)
    c.drawCircle(250, -605, 32, P(C(HFACE)))
    # neck + head
    c.drawRect(skia.Rect(-45, -960, 45, -900), P(C(HFUR)))
    monkey_face(c, 0, -1030, 115, HFUR, HFACE, 'open', look, talk, t, blink_off=blink_off)
    # tilak
    tk = skia.Path(); tk.moveTo(-14, -1085); tk.lineTo(0, -1140); tk.lineTo(14, -1085); tk.close()
    c.drawPath(tk, P(C('#D50000')))
    for sx in (-1, 1): c.drawCircle(sx * 115, -985, 14, P(C('#FFC107')))
    # mukut
    cy = -1030
    cr = skia.Path(); cr.moveTo(-95, cy - 80); cr.lineTo(-80, cy - 190); cr.lineTo(-40, cy - 160); cr.lineTo(0, cy - 250); cr.lineTo(40, cy - 160)
    cr.lineTo(80, cy - 190); cr.lineTo(95, cy - 80); cr.close()
    c.drawPath(cr, P(C('#FFC107'))); c.drawPath(cr, P(C('#B8860B'), 4))
    c.drawRect(skia.Rect(-100, cy - 112, 100, cy - 80), P(C('#E0A800')))
    c.drawCircle(0, cy - 150, 16, P(C('#E53935'))); c.drawCircle(-55, cy - 96, 9, P(C('#1E88E5'))); c.drawCircle(55, cy - 96, 9, P(C('#1E88E5')))
    c.restore()

def qmarks(c, t, d=0.0):
    q = T('q', '?', 220, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
    a = ease((t - d) / .25)
    draw_img(c, q, 560, 760 + math.sin(t * 5) * 12, a, 0.75 + 0.25 * a)
    draw_img(c, q, 140, 800 + math.sin(t * 5 + 1) * 12, a, 0.6 + 0.2 * a)

def label(c, key, txt, t, size=120, fill=(255, 240, 200, 255), stroke=(120, 50, 0, 255), y=210):
    a = ease((t + .1) / .2)
    draw_img(c, T(key, txt, size, fill=fill, stroke=stroke, sw=11), W / 2, y, a, 0.85 + .15 * a)

def hook_scene(c, t):
    """HOOK RULE: Bhima straining at the old monkey's tail fills the screen, bright, moving from frame 1."""
    forest(c, t)
    sh = math.sin(t * 38) * 5
    G = 1480; bx, bs = 830, 1.15
    hand = bhima_hand(bx + sh, G, bs, -1, 'lift2')
    old_monkey(c, 125, G, 1.02, t, grip=(hand[0], hand[1] + 6), wob=1.5, eyes='half', look=(1, 0), blink_off=2.0, tip_dx=30)
    bhima(c, bx + sh, G, bs, t, mood='strain', arm='lift2', facing=-1, look=(-1, 0), lean=-6, strain=1.0, blink_off=2.0)
    # strain lines around the grip
    for i in range(3):
        a = math.radians(200 + i * 40); r = 70 + 12 * math.sin(t * 20 + i)
        c.drawLine(hand[0] + math.cos(a) * r, hand[1] + math.sin(a) * r, hand[0] + math.cos(a) * (r + 40), hand[1] + math.sin(a) * (r + 40), P(C('#FFFFFF', 220), 7))

def hook_title(c, t, a=1.0):
    """big question text, fully visible on frame 1 (no fade-in)."""
    draw_img(c, T('h1', 'भीम से पूँछ', 130, fill=(255, 255, 255, 255), stroke=(20, 10, 40, 255), sw=12), W / 2, 230, a)
    draw_img(c, T('h2', 'क्यों नहीं उठी?', 140, fill=(255, 214, 64, 255), stroke=(110, 30, 0, 255), sw=13), W / 2, 400, a)

def s_hook(c, t, Tt, L):
    cover = globals().get('__name__') == 'cover'
    if cover:   # thumbnail: lift the picture so the tail + monkey sit above the cover text
        c.save(); c.translate(0, -300)
    hook_scene(c, t)
    if cover: c.restore()
    if globals().get('__name__') != 'cover': hook_title(c, t)
    qmarks(c, t, 0.3)

def s_path(c, t, Tt, L):
    forest(c, t)
    u = clamp(t / Tt)
    old_monkey(c, 135, GROUND, 1.0, t, eyes='closed', blink_off=2.0, tip_dx=150)
    bx = lerp(1020, 880, ease(u)); bob = abs(math.sin(t * 7)) * 10 * (1 - u)
    bhima(c, bx, GROUND - bob, 0.9, t, mood='neutral', arm='gada', facing=-1, look=(-1, 0))
    label(c, 'bb', 'बूढ़ा बंदर', t, 125, fill=(255, 245, 220, 255), stroke=(110, 60, 20, 255))

def s_order(c, t, Tt, L):
    forest(c, t)
    old_monkey(c, 125, GROUND, 0.85, t, eyes='half', look=(1, 0), tip_dx=120)
    sh = math.sin(t * 30) * 3 if sp(L, 0, t) else 0
    bhima(c, 790 + sh, GROUND, 1.05, t, mood='angry', arm='point', facing=-1, look=(-1, 0), talk=sp(L, 0, t))
    label(c, 'ht', 'हटो!', t, 170, fill=(255, 235, 210, 255), stroke=(170, 20, 10, 255), y=200)

def s_monkey(c, t, Tt, L):
    forest(c, t)
    c.save(); c.translate(540, 1200); c.scale(1.35, 1.35); c.translate(-540, -1200)
    old_monkey(c, 330, GROUND - 40, 1.0, t, talk=sp(L, 0, t), eyes='half', look=(1, 0), tip_dx=180)
    c.restore()
    label(c, 'pu', 'पूँछ हटाओ', t, 125, fill=(255, 245, 220, 255), stroke=(110, 60, 20, 255))

def s_lift(c, t, Tt, L):
    forest(c, t)
    a0, b0 = L[0][0], L[0][1]; d0 = b0 - a0
    grab = a0 + d0 * .3; shock = a0 + d0 * .62
    bx, bs = 820, 1.0
    hand = bhima_hand(bx, GROUND, bs, -1, 'lift1')
    held = t > grab
    wob = 2.0 if held else 0
    old_monkey(c, 125, GROUND, 0.95, t, grip=(hand[0], hand[1] + 6) if held else None, wob=wob, eyes='half', tip_dx=30 if held else 120)
    mood = 'shocked' if t > shock else 'happy'
    bhima(c, bx, GROUND, bs, t, mood=mood, arm='lift1' if held else 'gada', facing=-1, look=(-1, 1), lean=-3 if held else 0)
    label(c, 'eh', 'एक हाथ से', t, 125, fill=(255, 245, 220, 255), stroke=(120, 50, 0, 255))

def s_strain(c, t, Tt, L):
    forest(c, t)
    sh = math.sin(t * 42) * 6
    bx, bs = 800, 1.05
    hand = bhima_hand(bx + sh, GROUND, bs, -1, 'lift2')
    old_monkey(c, 125, GROUND, 1.0, t, grip=(hand[0], hand[1] + 6), wob=1.5, eyes='half', look=(1, 0), tip_dx=30)
    bhima(c, bx + sh, GROUND, bs, t, mood='strain', arm='lift2', facing=-1, look=(-1, 0), lean=-7 - 2 * math.sin(t * 3), strain=1.0)
    label(c, 'pz', 'पूरा ज़ोर!', t, 140, fill=(255, 235, 200, 255), stroke=(160, 40, 0, 255))

def s_reveal(c, t, Tt, L):
    u = ease(clamp(t / .5))
    forest(c, t, glow=1.0)
    for kk in range(4): c.drawCircle(540, 600, 250 + kk * 90, P(C('#FFF3B0', int(45 * u))))
    s = lerp(0.55, 0.82, u)
    hanuman(c, 460, GROUND - 10, s, t, aura=1.0, look=(.6, 0), bless=True)
    bhima(c, 900, GROUND, 0.75, t, mood='shocked', arm='down', facing=-1, look=(-1, -1))
    for i in range(10):
        ang = i * math.pi / 5 + t
        sparkle(c, 460 + math.cos(ang) * 400, 820 + math.sin(ang) * 380, 16, 0.5 + 0.5 * math.sin(t * 6 + i))
    if t < .25: c.drawRect(skia.Rect(0, 0, W, H), P(C('#FFFFFF', int(220 * (1 - t / .25)))))
    label(c, 'hj', 'हनुमान जी!', t, 135, fill=(255, 240, 200, 255), stroke=(170, 50, 0, 255), y=190)

def s_bow(c, t, Tt, L):
    forest(c, t, glow=0.6)
    u = ease(clamp(t / .6))
    hanuman(c, 350, GROUND - 10, 0.8, t, aura=0.8, look=(.8, .4), bless=True)
    bhima(c, 770, GROUND, 0.85, t, mood='happy', arm='namaste', facing=-1, look=(-1, 1), bow=-22 * u)
    for i in range(6):
        ph = (t * .7 + i / 6) % 1
        sparkle(c, 700 + math.sin(i * 2.1) * 120, 700 + ph * 450, 14, 1 - ph)
    label(c, 'as', 'आशीर्वाद', t, 130, fill=(255, 245, 220, 255), stroke=(150, 60, 0, 255), y=190)

def s_lesson(c, t, Tt, L):
    """one-line seekh over a calm deity frame (no long text card)."""
    forest(c, t, glow=0.5)
    hanuman(c, 540, GROUND - 10, 0.66, t, aura=0.7, look=(0, .3), bless=True)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 70, 1020, 470), 40, 40), P(C('#FFF8EC', 240)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 70, 1020, 470), 40, 40), P(C('#B71C1C'), 6))
    draw_img(c, T('seekh', 'सीख', 100, fill=(183, 28, 28, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 160, 1)
    if len(L) > 1:
        a = ease((t - L[1][0] + .15) / .25)
        draw_img(c, T(('ls', 1), L[1][2], 64, maxw=860, fill=(40, 30, 60, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 335, a)

def icon(c, kind, x, y, col='#FFFFFF'):
    p = P(C(col))
    if kind == 'like':
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 26, y - 6, x + 14, y + 30), 8, 8), p)
        c.drawRect(skia.Rect(x - 40, y - 4, x - 30, y + 30), p)
        th = skia.Path(); th.moveTo(x - 22, y - 4); th.lineTo(x - 6, y - 34); th.quadTo(x + 6, y - 36, x + 4, y - 20); th.lineTo(x, y - 6); th.close()
        c.drawPath(th, p)
    elif kind == 'share':
        ar = skia.Path(); ar.moveTo(x - 34, y + 26); ar.quadTo(x - 30, y - 12, x + 6, y - 12); ar.lineTo(x + 6, y - 30); ar.lineTo(x + 38, y - 2)
        ar.lineTo(x + 6, y + 26); ar.lineTo(x + 6, y + 8); ar.quadTo(x - 18, y + 6, x - 34, y + 26); ar.close()
        c.drawPath(ar, p)
    else:
        bl = skia.Path(); bl.moveTo(x - 28, y + 18); bl.quadTo(x - 22, y + 8, x - 22, y - 8); bl.quadTo(x - 20, y - 32, x, y - 32)
        bl.quadTo(x + 20, y - 32, x + 22, y - 8); bl.quadTo(x + 22, y + 8, x + 28, y + 18); bl.close()
        c.drawPath(bl, p); c.drawCircle(x, y + 26, 8, p); c.drawCircle(x, y - 36, 5, p)

def s_outro(c, t, Tt, L):
    """2-3 s outro drawn over the HOOK picture, so the video loops straight back into the question."""
    hook_scene(c, t)
    k = ease(t / .25) * clamp((Tt - 0.15 - t) / 0.3)   # button pops in, then fades out before the loop
    c.saveLayerAlpha(None, int(255 * k))
    c.save(); c.translate(W / 2, 320); c.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    press = L[0][0] + (L[0][1] - L[0][0]) * 0.7; done = t > press
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-330, -80, 330, 80), 80, 80), P(C('#7A7A7A' if done else '#E53935')))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-330, -80, 330, 80), 80, 80), P(C('#FFFFFF'), 6))
    icon(c, 'sub', -230, 0)
    c.restore()
    lab = 'SUBSCRIBED' if done else 'SUBSCRIBE'
    draw_img(c, T(('btn', lab), lab, 64, stroke=(0, 0, 0, 0), sw=0), W / 2 + 40, 324, k)
    if done and t < press + .6:
        q = (t - press) / .6
        for j in range(6):
            ang = j * math.pi / 3
            sparkle(c, W / 2 + 300 + math.cos(ang) * 90 * q, 320 + math.sin(ang) * 70 * q, 16, 1 - q)
    c.restore()
    # fade the button out in the last 0.3 s so the final frame == hook picture (seamless loop)
    hook_title(c, t, clamp((t - (Tt - 0.45)) / 0.3))

FN = dict(hook=s_hook, path=s_path, order=s_order, monkey=s_monkey, lift=s_lift, strain=s_strain, reveal=s_reveal, bow=s_bow, lesson=s_lesson, outro=s_outro)


def frame(sid, t, Tt, L):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    # v2: something always moves - punch-in on the hook, slow push-in on every other scene, hard cuts (no black fades)
    z = 1 + 0.10 * (1 - ease(t / 0.35)) if sid == 'hook' else 1 + 0.05 * t / max(Tt, .1)
    if sid == 'outro': z = 1.0
    c.save(); c.translate(W / 2, 800); c.scale(z, z); c.translate(-W / 2, -800)
    FN[sid](c, t, Tt, L)
    c.restore()
    if sid not in ('hook', 'lesson', 'outro'): subtitle(c, L, t)
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)

def render_scene(idx, sid, Tt, L):
    n = int(round(Tt * FPS)); tmp = f'out/tmp_{idx:02d}_{sid}.mp4'; fin = f'out/{idx:02d}_{sid}.mp4'
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(n): pr.stdin.write(frame(sid, i / FPS, Tt, L).tobytes())
    pr.stdin.close()
    if pr.wait() == 0: os.rename(tmp, fin)
    return n

if __name__ == '__main__':
    os.makedirs('out', exist_ok=True); tl = build_timeline()
    if sys.argv[1] == 'stills':
        os.makedirs('stills', exist_ok=True); ims = []
        for sid, Tt, L in tl:
            for tt in (L[0][0] + 0.8, L[-1][1] - 0.2):
                ims.append(Image.fromarray(frame(sid, tt, Tt, L)).convert('RGB').resize((270, 480)))
        sheet = Image.new('RGB', (270 * 5, 480 * 4))
        for i, im in enumerate(ims): sheet.paste(im, ((i % 5) * 270, (i // 5) * 480))
        sheet.save('sheet.jpg', quality=85); print('total', sum(x[1] for x in tl))
    else:
        which = sys.argv[2:] or [s for s, _, _ in tl]
        for i, (sid, Tt, L) in enumerate(tl):
            if sid in which: print(sid, render_scene(i, sid, Tt, L), flush=True)
