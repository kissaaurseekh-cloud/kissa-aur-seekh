import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from mart import sparkle as _sp
from gnart import petals
from vart import *
from hart import man
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
        tail = {'outro': 0.5, 'lesson': 0.35, 'lakshmi': 0.45, 'fall': 0.35, 'curse': 0.3, 'throw': 0.25, 'hook': 0.1}.get(sid, 0.12)
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
        r = int(r1 + (r2 - r1) * angry * .55); g = int(g1 + (g2 - g1) * angry * .55); b = int(b1 + (b2 - b1) * angry * .55)
        return '#%02X%02X%02X' % (r, g, b)
    top, bot = mx('#4FA8E8'), mx('#FFE3A3')
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 1150)], [col(top), col(bot)]))
    c.drawRect(skia.Rect(0, 0, W, 1160), p)
    for k in range(5): c.drawCircle(540, 600, 120 + k * 50, P(C('#FFF6D0', int(40 * (1 - dim)))))
    for i, (cx, cy, s) in enumerate([(160, 420, 1.2), (880, 330, 1.0), (620, 180, .8), (300, 760, 1.0), (960, 700, .9)]):
        cloud(c, (cx + t * (10 + i * 3)) % 1300 - 110, cy, s, '#FFFFFF', int(200 * (1 - dim * .6)))
    # palace
    white, gold, shade = col(mx('#FFF8E7')), col(mx('#FFC93C')), col(mx('#E8C77A'))
    c.drawRect(skia.Rect(250, 760, 830, 1010), P(white))
    for i in range(7):
        px = 280 + i * 87
        c.drawRect(skia.Rect(px, 790, px + 26, 1010), P(shade))
    c.drawRect(skia.Rect(230, 735, 850, 770), P(gold))
    c.drawRect(skia.Rect(230, 990, 850, 1020), P(gold))
    c.drawArc(skia.Rect(400, 560, 680, 840), 180, 180, True, P(gold))
    c.drawRect(skia.Rect(530, 500, 550, 570), P(gold)); c.drawCircle(540, 495, 16, P(gold))
    for dx in (300, 780):
        c.drawArc(skia.Rect(dx - 70, 650, dx + 70, 790), 180, 180, True, P(gold))
        c.drawRect(skia.Rect(dx - 7, 610, dx + 7, 660), P(gold)); c.drawCircle(dx, 606, 10, P(gold))
    for dx in (250, 830):  # flags
        c.drawLine(dx, 735, dx, 640, P(col('#8D6E63'), 5))
        fl = skia.Path(); fl.moveTo(dx, 640); fl.lineTo(dx + 60, 655 + math.sin(t * 5 + dx) * 8); fl.lineTo(dx, 675); fl.close()
        c.drawPath(fl, P(col(mx('#FF7043'))))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(480, 880, 600, 1010), 60, 60), P(col(mx('#B07A2A'))))
    # cloud floor
    fp = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 1000), skia.Point(0, H)], [col(mx('#FFFDF5')), col(mx('#EADBC8'))]))
    c.drawRect(skia.Rect(0, 1040, W, H), fp)
    for i in range(12):
        cx = i * 100 - 20 + math.sin(t * .8 + i) * 6
        c.drawCircle(cx, 1050 + (i % 3) * 12, 70 + (i * 17) % 30, P(col(mx('#FFFFFF'))))
    for i in range(6):
        cx = (i * 210 + t * 20) % 1300 - 100
        c.drawOval(skia.Rect(cx - 110, 1230 + (i % 2) * 140, cx + 110, 1270 + (i % 2) * 140), P(C('#FFFFFF', int(120 * (1 - dim * .5)))))

def mala(c, x, y, r, t, glow=0.0, a=1.0, flat=1.0, spin=0.0):
    """divine flower garland (ring of white/pink/orange flowers)."""
    if a <= 0: return
    c.saveLayerAlpha(None, int(255 * clamp(a)))
    c.save(); c.translate(x, y); c.scale(1, flat)
    if glow > 0:
        for k in range(4): c.drawCircle(0, 0, r * (1.2 + k * .25), P(C('#FFF59D', int(50 * glow))))
    c.drawCircle(0, 0, r, P(C('#2E7D32'), max(3, r * .08)))
    n = 16
    for i in range(n):
        ang = i / n * math.tau + spin
        fx, fy = math.cos(ang) * r, math.sin(ang) * r
        colr = ['#FFFFFF', '#FF8F00', '#F06292', '#FFD54F'][i % 4]
        fr = r * .2
        for j in range(5):
            aa = j / 5 * math.tau + i
            c.drawCircle(fx + math.cos(aa) * fr * .55, fy + math.sin(aa) * fr * .55, fr * .55, P(C(colr)))
        c.drawCircle(fx, fy, fr * .35, P(C('#E65100' if colr == '#FFFFFF' else '#FFF59D')))
    # hanging tassel at bottom
    c.drawLine(0, r, 0, r * 1.45, P(C('#2E7D32'), max(3, r * .06)))
    c.drawCircle(0, r * 1.5, r * .16, P(C('#F06292')))
    c.restore(); c.restore()

def falling_petals(c, x, y, t, a=1.0, spread=300, n=14, seed=3):
    rnd = random.Random(seed)
    for i in range(n):
        ph = (t * .35 + rnd.random()) % 1
        px = x + (rnd.random() - .5) * spread + math.sin(t * 2 + i) * 20
        py = y + ph * 500
        c.drawOval(skia.Rect(px - 9, py - 5, px + 9, py + 5), P(C(['#FFFFFF', '#F48FB1', '#FFB74D'][i % 3], int(230 * a * (1 - ph)))))

def durvasa(c, x, gy, s=1.0, t=0.0, angry=0.0, talk=False, arm='down', facing=1, look=(0, 0)):
    """Rishi Durvasa: saffron robe, grey jata bun, white beard, tripundra tilak, rudraksha."""
    man(c, x, gy, s, 'neutral', talk, t, look, old=1.0, kurta='#E65100', pants='#FFB74D', arm=arm, skin='#C68B5A', facing=facing)
    k = s * 1.15; hx, hy = x, gy - 545 * k; r = 70 * k
    # jata bun
    c.drawCircle(hx, hy - 100 * k, 40 * k, P(C('#8C7F72'))); c.drawRect(skia.Rect(hx - 30 * k, hy - 80 * k, hx + 30 * k, hy - 68 * k), P(C('#5D4037')))
    # tilak (tripundra + dot)
    for i in range(3):
        c.drawLine(hx - 34 * k, hy - 52 * k + i * 9 * k, hx + 34 * k, hy - 52 * k + i * 9 * k, P(C('#FFFFFF'), 4 * k))
    c.drawCircle(hx, hy - 44 * k, 5 * k, P(C('#D50000')))
    # angry brows
    if angry > 0:
        ey = hy - r * .12; by = ey - r * .3
        bp = P(C('#3A2A20'), 7 * k)
        c.drawLine(hx - r * .62, by - 10 * k, hx - r * .15, by + 8 * k, bp); c.drawLine(hx + r * .62, by - 10 * k, hx + r * .15, by + 8 * k, bp)
    # white beard
    bd = skia.Path(); bd.moveTo(hx - 62 * k, hy + 10 * k); bd.quadTo(hx - 40 * k, hy + 150 * k, hx, hy + 175 * k)
    bd.quadTo(hx + 40 * k, hy + 150 * k, hx + 62 * k, hy + 10 * k); bd.quadTo(hx + 30 * k, hy + 62 * k, hx, hy + 58 * k)
    bd.quadTo(hx - 30 * k, hy + 62 * k, hx - 62 * k, hy + 10 * k); bd.close()
    c.drawPath(bd, P(C('#EDEDED')))
    if talk:
        o = abs(math.sin(t * 12)) * .8 + .2
        c.drawOval(skia.Rect(hx - 12 * k, hy + 40 * k, hx + 12 * k, hy + (46 + 16 * o) * k), P(C('#6A2414')))
    # rudraksha mala on chest
    for i in range(9):
        ang = math.radians(20 + i * 17.5)
        c.drawCircle(hx + math.cos(ang) * 48 * k, gy - 420 * k + math.sin(ang) * 60 * k, 6 * k, P(C('#6D3B1F')))

def indra(c, x, gy, s=1.0, t=0.0, mood='neutral', arm='down', facing=1, look=(0, 0), bow=0.0, talk=False):
    """Indra dev: golden mukut, gold & red clothes, vajra in the other hand."""
    c.save()
    if bow:
        c.translate(x, gy); c.rotate(-bow * facing); c.translate(-x, -gy)
    man(c, x, gy, s, mood, talk, t, look, kurta='#F2B233', pants='#C0392B', turban=None, arm=arm, skin='#E8B98A', facing=facing)
    k = s * 1.15; hx, hy = x, gy - 545 * k
    cr = skia.Path(); cr.moveTo(hx - 62 * k, hy - 55 * k); cr.lineTo(hx - 52 * k, hy - 150 * k); cr.lineTo(hx - 24 * k, hy - 120 * k)
    cr.lineTo(hx, hy - 205 * k); cr.lineTo(hx + 24 * k, hy - 120 * k); cr.lineTo(hx + 52 * k, hy - 150 * k); cr.lineTo(hx + 62 * k, hy - 55 * k); cr.close()
    c.drawPath(cr, P(C('#FFC107'))); c.drawPath(cr, P(C('#B8860B'), 3 * k))
    c.drawRect(skia.Rect(hx - 64 * k, hy - 75 * k, hx + 64 * k, hy - 55 * k), P(C('#E0A800')))
    c.drawCircle(hx, hy - 110 * k, 11 * k, P(C('#E53935'))); c.drawCircle(hx, hy - 66 * k, 7 * k, P(C('#1E88E5')))
    for sx in (-1, 1): c.drawCircle(hx + sx * 70 * k, hy + 22 * k, 9 * k, P(C('#FFC107')))
    # necklace
    c.drawArc(skia.Rect(hx - 45 * k, gy - 470 * k, hx + 45 * k, gy - 400 * k), 20, 140, False, P(C('#FFC107'), 6 * k))
    # vajra in the hand that is down (left side when facing right)
    if arm in ('point', 'down'):
        vx, vy = x - 80 * k * facing, gy - 238 * k
        g = P(C('#FFC107')); gd = P(C('#B8860B'), 3 * k)
        c.drawRect(skia.Rect(vx - 7 * k, vy - 70 * k, vx + 7 * k, vy + 70 * k), g)
        for sy in (-1, 1):
            pr = skia.Path(); pr.moveTo(vx - 26 * k, vy + sy * 60 * k); pr.lineTo(vx, vy + sy * 110 * k); pr.lineTo(vx + 26 * k, vy + sy * 60 * k)
            pr.quadTo(vx, vy + sy * 80 * k, vx - 26 * k, vy + sy * 60 * k); pr.close()
            c.drawPath(pr, g); c.drawPath(pr, gd)
        c.drawCircle(vx, vy, 14 * k, g)
    c.restore()

def hand_pt(x, gy, s, facing=1):
    k = s * 1.15; return x + 182 * k * facing, gy - 380 * k

def airavat(c, x, gy, s, t, trunk_up=False, look=(-1, 0), blink_off=0.0, mala_on=False, bob=0.0):
    """Airavat: Indra's white elephant with red-gold blanket and gold head ornament (faces left)."""
    gy = gy - bob
    rec = skia.PictureRecorder(); rc = rec.beginRecording(skia.Rect(0, 0, W, H))
    elephant(rc, x, gy, s, t, trunk_up=trunk_up, look=look, blink_off=blink_off, tint='#F3F1EC')
    pic = rec.finishRecordingAsPicture()
    # soft grey outline so the white elephant (and its trunk) reads against the white clouds
    op = skia.Paint(ImageFilter=skia.ImageFilters.Dilate(int(5 * s) + 2, int(5 * s) + 2), ColorFilter=skia.ColorFilters.Blend(C('#8A8F9C'), skia.BlendMode.kSrcIn))
    c.saveLayer(None, op); c.drawPicture(pic); c.restore()
    c.drawPicture(pic)
    c.save(); c.translate(x, gy); c.scale(s, s)
    bl = skia.RRect.MakeRectXY(skia.Rect(-30, -478, 200, -330), 26, 26)
    c.drawRRect(bl, P(C('#C62828'))); c.drawRRect(bl, P(C('#FFC107'), 10))
    for i in range(8): c.drawCircle(-10 + i * 30, -322, 9, P(C('#FFC107')))
    hx, hy = -230, -400
    hp = skia.Path(); hp.moveTo(hx - 70, hy - 95); hp.quadTo(hx, hy - 150, hx + 70, hy - 95); hp.lineTo(hx + 10, hy - 60); hp.close()
    c.drawPath(hp, P(C('#FFC107'))); c.drawCircle(hx, hy - 98, 14, P(C('#E53935')))
    c.drawLine(hx + 70, hy - 95, hx + 115, hy - 20, P(C('#FFC107'), 10))
    c.restore()
    if mala_on:
        mala(c, x - 215 * s, gy - 515 * s, 62 * s, t, glow=.6, flat=.55)

def trunk_tip(x, gy, s):
    return x - 530 * s, gy - 540 * s

def coin(c, x, y, r, a=1.0):
    c.drawCircle(x, y, r, P(C('#FFC107', int(255 * a)))); c.drawCircle(x, y, r * .7, P(C('#E0A000', int(255 * a)), max(2, r * .15)))

def lakshmi(c, x, gy, s=1.0, t=0.0, aura=0.0, a=1.0, coins=1.0):
    """Devi Lakshmi: red saree, gold crown, four arms (two holding lotuses), gold coins from her hand, standing on a lotus."""
    c.saveLayerAlpha(None, int(255 * clamp(a)))
    if aura > 0:
        for k in range(5): c.drawCircle(x, gy - 820 * s, (150 + k * 55) * s, P(C('#FFE082', int(55 * aura))))
        c.drawCircle(x, gy - 830 * s, 150 * s, P(C('#FFD54F', int(150 * aura)), 10 * s))
    skin = '#E7B488'
    c.save(); c.translate(x, gy); c.scale(s, s)
    for sx in (-1, 1):
        ap = P(C(skin), 28)
        c.drawLine(sx * 80, -650, sx * 175, -700, ap); c.drawLine(sx * 175, -700, sx * 200, -790, ap)
        c.drawCircle(sx * 200, -798, 20, P(C(skin)))
        for i in range(3): c.drawLine(sx * 186, -745 + i * 10, sx * 214, -745 + i * 10, P(C('#FFC107'), 5))
    c.restore()
    for sx in (-1, 1): lotus(c, x + sx * 205 * s, gy - 840 * s, 0.95 * s, glow=.3, t=t)
    parvati(c, x, gy, s, t, mood='happy')
    lotus(c, x, gy + 20 * s, 3.4 * s, glow=0.4, t=t)
    # gold coins pouring from the lower left hand
    if coins > 0:
        hxp, hyp = x - 122 * s, gy - 455 * s
        for i in range(9):
            ph = (t * .9 + i / 9) % 1
            coin(c, hxp + math.sin(i * 2.3) * 30 * s, hyp + ph * 380 * s, 15 * s, coins * (1 - ph))
    c.restore()

def qmarks(c, t, d=0.0):
    q = T('q', '?', 220, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
    a = ease((t - d) / .25)
    draw_img(c, q, 940, 600 + math.sin(t * 5) * 12, a, 0.75 + 0.25 * a)
    draw_img(c, q, 130, 1150 + math.sin(t * 5 + 1) * 12, a, 0.6 + 0.2 * a)

def label(c, key, txt, t, size=120, fill=(255, 240, 200, 255), stroke=(120, 50, 0, 255), y=210):
    a = ease((t + .1) / .2)
    draw_img(c, T(key, txt, size, fill=fill, stroke=stroke, sw=11), W / 2, y, a, 0.85 + .15 * a)

def hook_scene(c, t):
    """HOOK RULE: the mystery thing (Airavat holding the divine garland) fills the screen, bright, moving from frame 1."""
    swarg(c, t)
    light_rays(c, 260, 760, t, 0.8, col='#FFF3B0')
    x, gy, s = 990, 1590, 1.5
    bob = math.sin(t * 3) * 8
    airavat(c, x, gy, s, t, trunk_up=True, look=(-1, -1), blink_off=2.0, bob=bob)   # never blink on frame 1
    tx, ty = trunk_tip(x, gy - bob, s)
    mala(c, tx + 10, ty + 40, 120, t, glow=0.8 + 0.2 * math.sin(t * 6), spin=math.sin(t * 2) * .15)
    falling_petals(c, tx, ty + 100, t, 0.9, 260, 12)

def hook_title(c, t, a=1.0):
    """big question text, fully visible on frame 1 (no fade-in)."""
    draw_img(c, T('h1', 'माला से स्वर्ग', 120, fill=(255, 255, 255, 255), stroke=(20, 10, 40, 255), sw=12), W / 2, 240, a)
    draw_img(c, T('h2', 'कैसे छिना?', 150, fill=(255, 214, 64, 255), stroke=(110, 30, 0, 255), sw=13), W / 2, 400, a)

def s_hook(c, t, Tt, L):
    hook_scene(c, t)
    if globals().get('__name__') != 'cover': hook_title(c, t)   # the thumbnail gets its own big cover lines
    qmarks(c, t, 0.3)

def s_gift(c, t, Tt, L):
    swarg(c, t)
    a0, b0 = L[0][0], L[0][1]; d0 = b0 - a0
    s = 0.95
    dx, ix = 250, 820
    durvasa(c, dx, GROUND, s, t, arm='point', facing=1, look=(1, 0))
    indra(c, ix, GROUND, s, t, mood='happy', arm='point', facing=-1, look=(-1, 0))
    p0 = hand_pt(dx, GROUND, s, 1); p1 = hand_pt(ix, GROUND, s, -1)
    u = ease((t - a0 - d0 * .35) / (d0 * .35))
    mx_ = lerp(p0[0] + 40, p1[0] - 40, u); my_ = lerp(p0[1], p1[1], u) - math.sin(math.pi * u) * 160
    mala(c, mx_, my_ - 30, 70, t, glow=0.9, spin=t * .5)
    for i in range(8):
        ang = i * math.pi / 4 + t * 2
        sparkle(c, mx_ + math.cos(ang) * 120, my_ - 30 + math.sin(ang) * 110, 14, 0.5 + 0.5 * math.sin(t * 7 + i))
    label(c, 'dm', 'दिव्य माला', t, 120, fill=(255, 250, 220, 255), stroke=(150, 70, 0, 255))

def s_airavat(c, t, Tt, L):
    swarg(c, t)
    a0, b0 = L[0][0], L[0][1]; d0 = b0 - a0
    s = 0.95; ix = 220
    ex, egy, es = 790, GROUND, 0.85
    throw = a0 + d0 * .55
    indra(c, ix, GROUND, s, t, mood='happy', arm='point' if t < throw + .3 else 'down', facing=1, look=(1, -1))
    landed = t > throw + .5
    airavat(c, ex, egy, es, t, look=(-1, -1) if landed else (-1, 0), mala_on=landed)
    if not landed:
        p0 = hand_pt(ix, GROUND, s, 1)
        u = ease(clamp((t - throw) / .5))
        hx_, hy_ = ex - 215 * es, egy - 515 * es
        mx_ = lerp(p0[0] + 40, hx_, u); my_ = lerp(p0[1] - 20, hy_, u) - math.sin(math.pi * u) * 220
        mala(c, mx_, my_, lerp(70, 62 * es, u), t, glow=.8, flat=lerp(1, .55, u))
    label(c, 'gh', 'घमंड!', t, 140, fill=(255, 236, 180, 255), stroke=(150, 40, 0, 255))

def s_throw(c, t, Tt, L):
    swarg(c, t)
    a0, b0 = L[0][0], L[0][1]; d0 = b0 - a0
    x, gy, s = 720, GROUND, 1.0
    lift = a0 + d0 * .3; toss = a0 + d0 * .62
    up = lift <= t < toss + .15
    airavat(c, x, gy, s, t, trunk_up=up, look=(-1, -1) if up else (-1, 1), mala_on=t < lift)
    tx, ty = trunk_tip(x, gy, s)
    if up:
        mala(c, tx + 10, ty + 40, 70, t, glow=.5, spin=(t - lift) * 3)
    elif t >= toss + .15:
        u = clamp((t - toss - .15) / .45)
        gx, gyy = 230, 1300
        mx_ = lerp(tx + 10, gx, u); my_ = lerp(ty + 40, gyy, ease(u)) - math.sin(math.pi * u) * 120
        mala(c, mx_, my_, 70, t, glow=.4 * (1 - u), flat=lerp(1, .3, u), spin=u * 4)
        if u >= 1:
            k = clamp((t - toss - .6) / .8)
            for i in range(14):
                ang = i / 14 * math.tau
                px = gx + math.cos(ang) * 160 * ease(k); py = gyy - math.sin(ang) * 60 * ease(k) - 80 * math.sin(math.pi * k) * abs(math.sin(ang))
                c.drawOval(skia.Rect(px - 10, py - 6, px + 10, py + 6), P(C(['#FFFFFF', '#F48FB1', '#FFB74D'][i % 3], int(255 * (1 - k * .5)))))
    label(c, 'ar', 'ऐरावत!', t, 130, fill=(255, 255, 255, 255), stroke=(60, 60, 120, 255))

def s_curse(c, t, Tt, L):
    ang = clamp(t / .3)
    swarg(c, t, angry=ang)
    for k in range(5): c.drawCircle(540, 760, 260 + k * 70 + math.sin(t * 6) * 10, P(C('#FF5722', int(40 * ang))))
    shake = math.sin(t * 45) * 5
    mala(c, 250, 1320, 70, t, flat=.3, a=.9)
    durvasa(c, 560 + shake, GROUND, 1.25, t, angry=1, talk=sp(L, 0, t), arm='point', facing=-1)
    if t < .3: c.drawRect(skia.Rect(0, 0, W, H), P(C('#FFFFFF', int(150 * (1 - t / .3)))))
    label(c, 'sh', 'श्राप!', t, 170, fill=(255, 230, 200, 255), stroke=(170, 10, 10, 255), y=200)

def s_sorry(c, t, Tt, L):
    u = clamp(t / Tt)
    swarg(c, t, angry=1 - u * .6, dim=u * .3)
    dxp = lerp(260, 60, ease(u))
    durvasa(c, dxp, GROUND, 0.95, t, angry=1, facing=-1, look=(-1, 0))
    bow = 12 * ease(clamp(t / .5))
    indra(c, 700, GROUND, 1.0, t, mood='sad', arm='down', facing=-1, look=(-1, 1), bow=bow)
    label(c, 'mk', 'क्षमा करें!', t, 130, fill=(255, 245, 225, 255), stroke=(90, 40, 20, 255))

def s_lakshmi(c, t, Tt, L):
    a0, b0 = L[0][0], L[0][1]; d0 = b0 - a0
    u = ease(clamp((t - a0 - d0 * .3) / (Tt - a0 - d0 * .3)))
    swarg(c, t, dim=u * .85)
    light_rays(c, 540, lerp(820, 500, u), t, 0.7 * (1 - u * .6), col='#FFF3B0')
    gy = lerp(1330, 900, u); s = lerp(0.66, 0.42, u)
    lakshmi(c, 540, gy, s, t, aura=0.8, a=1 - clamp((u - .75) / .25) * .6, coins=1 - u)
    for i in range(10):
        ang = i * math.pi / 5 + t
        sparkle(c, 540 + math.cos(ang) * 380 * s / .66, gy - 450 * s + math.sin(ang) * 360 * s / .66, 16, (0.5 + 0.5 * math.sin(t * 6 + i)) * (1 - u * .5))
    label(c, 'dl', 'देवी लक्ष्मी', t, 120, fill=(255, 240, 200, 255), stroke=(170, 30, 30, 255), y=170)

def s_fall(c, t, Tt, L):
    swarg(c, t, dim=0.85)
    u = t / Tt
    for i, (x0, x1, s) in enumerate([(700, 1050, .62), (880, 1230, .55)]):
        deva(c, lerp(x0, x1, u) + math.sin(t * 14 + i) * 4, GROUND - abs(math.sin(t * 9 + i)) * 10, s, 'shocked', t, facing=1, look=(-1, 0))
    for i, (x0, x1, s) in enumerate([(-60, 320, .7), (-220, 140, .62)]):
        asura(c, lerp(x0, x1, u), GROUND - abs(math.sin(t * 8 + i)) * 8, s, 'neutral', t, arm='point', facing=1, look=(1, 0))
    label(c, 'sg', 'स्वर्ग गया!', t, 130, fill=(230, 235, 255, 255), stroke=(40, 30, 90, 255))

def s_lesson(c, t, Tt, L):
    """one-line seekh over a calm deity frame (no long text card)."""
    swarg(c, t)
    light_rays(c, 540, 900, t, 0.5, col='#FFFFFF')
    lakshmi(c, 540, 1330, 0.6, t, aura=0.7)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 70, 1020, 560), 40, 40), P(C('#FFF8EC', 235)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 70, 1020, 560), 40, 40), P(C('#B71C1C'), 6))
    draw_img(c, T('seekh', 'सीख', 100, fill=(183, 28, 28, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 160, 1)
    if len(L) > 1:
        a = ease((t - L[1][0] + .15) / .25)
        draw_img(c, T(('ls', 1), L[1][2], 64, maxw=860, fill=(40, 30, 60, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 380, a)

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
    c.save(); c.translate(W / 2, 560); c.scale(0.85 + 0.15 * k, 0.85 + 0.15 * k)
    press = L[0][0] + (L[0][1] - L[0][0]) * 0.7; done = t > press
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-330, -80, 330, 80), 80, 80), P(C('#7A7A7A' if done else '#E53935')))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-330, -80, 330, 80), 80, 80), P(C('#FFFFFF'), 6))
    icon(c, 'sub', -230, 0)
    c.restore()
    lab = 'SUBSCRIBED' if done else 'SUBSCRIBE'
    draw_img(c, T(('btn', lab), lab, 64, stroke=(0, 0, 0, 0), sw=0), W / 2 + 40, 564, k)
    if done and t < press + .6:
        q = (t - press) / .6
        for j in range(6):
            ang = j * math.pi / 3
            sparkle(c, W / 2 + 300 + math.cos(ang) * 90 * q, 560 + math.sin(ang) * 70 * q, 16, 1 - q)
    c.restore()
    # fade the button out in the last 0.3 s so the final frame == hook picture (seamless loop)
    hook_title(c, t, clamp((t - (Tt - 0.45)) / 0.3))

FN = dict(hook=s_hook, gift=s_gift, airavat=s_airavat, throw=s_throw, curse=s_curse, sorry=s_sorry, lakshmi=s_lakshmi, fall=s_fall, lesson=s_lesson, outro=s_outro)

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
