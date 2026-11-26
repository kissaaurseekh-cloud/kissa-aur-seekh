import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from mart import sparkle as _sp
from gnart import petals
from vart import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'reveal': 0.3, 'lotus': 0.2, 'tired': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'lesson': 0.5, 'reveal': 1.0, 'lotus': 0.6, 'vishnu': 0.6, 'grab': 0.4, 'hook': 0.3}.get(sid, 0.2)
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
FAM = '#A79A92'

def trunk_tip(x, gy, s, sad=0.0):
    return x - 530 * s, gy + (-540 + sad * 25) * s

def fam_el(c, x, gy, s, t, facing=-1, walk=0.0, blink=0.0):
    """family elephant; facing -1 = left (default drawing), 1 = right (mirrored)."""
    bob = abs(math.sin(t * 6)) * 6 * walk
    if facing == -1:
        elephant(c, x, gy - bob, s, t, tint=FAM, blink_off=blink)
    else:
        c.save(); c.translate(x, 0); c.scale(-1, 1)
        elephant(c, 0, gy - bob, s, t, tint=FAM, blink_off=blink)
        c.restore()

def qmarks(c, t, L, d=1.0):
    if after(L, 0, t, d):
        q = T('q', '?', 220, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
        a = ease((t - L[0][0] - d) / .3)
        draw_img(c, q, 900, 620 + math.sin(t * 4) * 10, a, 0.7 + 0.3 * a)
        draw_img(c, q, 520, 520 + math.sin(t * 4 + 1) * 10, a, 0.55 + 0.2 * a)

def s_hook(c, t, Tt, L):
    trikut(c, t, 'night')
    light_rays(c, 150, 760, t, 0.55, col='#FFE7A8')
    x, gy, s = 650, GROUND, 0.95
    magar(c, 330, 1185, 0.8, t, open_=0.15, a=0.55)
    elephant(c, x, gy, s, t, trunk_up=True, look=(-1, -1))
    tx, ty = trunk_tip(x, gy, s)
    lotus(c, tx, ty - 10, 1.0, glow=0.8 + 0.2 * math.sin(t * 5), t=t)
    water_front(c, 1190, t, 0.62, dark=0.4)
    title = T('title', 'हाथी और कमल?', 104, fill=(255, 244, 220, 255), stroke=(120, 40, 0, 255), sw=10)
    k = ease(t / .5); draw_img(c, title, W / 2, 170, k, 0.85 + .15 * k)
    qmarks(c, t, L, 1.0)

def s_lake(c, t, Tt, L):
    trikut(c, t, 'day')
    x, gy, s = 560, GROUND, 0.9
    fam_el(c, 930, 1265, 0.42, t, blink=1.3)
    fam_el(c, 1050, 1290, 0.36, t, blink=2.1)
    elephant(c, x, gy, s, t, look=(-1, 0))
    water_front(c, 1195, t, 0.6)
    for i, xx in enumerate((300, 880)): ripple(c, xx, 1205, (t * .5 + i * .4) % 1)
    if not after(L, 1, t, -.05):
        a = ease((t - .15) / .35)
        draw_img(c, T('gj', 'गजेंद्र', 130, fill=(255, 244, 220, 255), stroke=(110, 50, 0, 255), sw=11), W / 2, 200, a)
        draw_img(c, T('raja', 'हाथियों का राजा', 76, fill=(255, 255, 255, 255), stroke=(30, 70, 120, 255), sw=8), W / 2, 330, ease((t - .5) / .35))
    else:
        draw_img(c, T('sar', 'सरोवर में…', 100, fill=(255, 255, 255, 255), stroke=(20, 70, 120, 255), sw=9), W / 2, 210, ease((t - L[1][0]) / .3))

def s_grab(c, t, Tt, L):
    trikut(c, t, 'day')
    x, gy, s = 600, GROUND, 0.9
    snap = L[0][0] + (L[0][1] - L[0][0]) * 0.45
    rise = ease((t - L[0][0] - .2) / (snap - L[0][0] - .2))
    shake = math.sin(t * 40) * 6 if t > snap else 0
    fam_el(c, 960, 1265, 0.42, t)
    elephant(c, x + shake, gy, s, t, pull=0.6 if t > snap else 0, look=(-1, 1) if t > snap else (-1, 0))
    if t <= snap:
        op = clamp((t - L[0][0]) / (snap - L[0][0]) * 1.6)
        magar(c, 330, lerp(1300, 1185, rise), 1.0, t, open_=op if op < 1 else 1)
    else:
        magar(c, 330, 1185, 1.0, t, open_=0.05)
        splash_drops(c, 520, 1190, (t - snap) / .9)
    water_front(c, 1195, t, 0.6)
    ripple(c, 470, 1205, (t * .8) % 1)
    if t > snap:
        a = ease((t - snap) / .25)
        draw_img(c, T('mg', 'मगरमच्छ!', 130, fill=(255, 235, 200, 255), stroke=(160, 20, 20, 255), sw=11), W / 2, 220, a, 0.8 + .2 * a)

def s_fight(c, t, Tt, L):
    trikut(c, t, 'day')
    sink = ease((t - L[1][0]) / (Tt - L[1][0])) if after(L, 1, t) else 0
    x, gy, s = 600 - 60 * sink, GROUND + 70 * sink, 0.9
    fam_el(c, 990 - 40 * sink, 1262, 0.4, t, blink=.7)
    fam_el(c, 1080, 1290, 0.34, t, blink=1.9)
    elephant(c, x, gy, s, t, pull=1.0, look=(1, 0))
    magar(c, 330 - 60 * sink, 1185, 1.0, t, open_=0.05 + 0.04 * math.sin(t * 9))
    water_front(c, 1195, t, 0.6)
    ripple(c, 460, 1205, (t * 1.2) % 1); ripple(c, 760, 1210, (t * 1.2 + .5) % 1)
    if not after(L, 1, t, -.05):
        draw_img(c, T('pt', 'पूरी ताक़त!', 110, fill=(255, 240, 200, 255), stroke=(120, 50, 0, 255), sw=10), W / 2, 220, ease((t - .2) / .3))
    else:
        draw_img(c, T('gp', 'गहरे पानी में…', 100, fill=(220, 240, 255, 255), stroke=(10, 50, 110, 255), sw=9), W / 2, 220, ease((t - L[1][0]) / .3))

def s_tired(c, t, Tt, L):
    late = after(L, 1, t)
    trikut(c, t, 'dusk' if not late else 'night')
    x, gy, s = 540, GROUND + 90, 0.9
    if late:
        u = (t - L[1][0]) / (Tt - L[1][0])
        fam_el(c, 930 + 420 * u, 1262, 0.4, t, facing=1, walk=1)
        fam_el(c, 1050 + 420 * u, 1290, 0.34, t, facing=1, walk=1)
    else:
        fam_el(c, 940, 1262, 0.4, t); fam_el(c, 1060, 1290, 0.34, t)
    elephant(c, x, gy, s, t, sad=1.0 if late else 0.6, pull=0.0, look=(0, 1), ear_speed=0.4)
    magar(c, 270, 1185, 1.0, t, open_=0.05)
    water_front(c, 1195, t, 0.62, dark=0.45 if late else 0.2)
    if not late:
        draw_img(c, T('bs', 'बहुत समय बीत गया…', 86, fill=(255, 244, 220, 255), stroke=(80, 40, 60, 255), sw=9), W / 2, 220, ease((t - .2) / .3))
        # sun going down quickly
        k = clamp(t / max(.1, L[0][1]))
        c.drawCircle(lerp(860, 900, k), lerp(380, 900, k), 60, P(C('#FFB74D', 230)))
    else:
        draw_img(c, T('tk', 'ताक़त ख़त्म…', 104, fill=(220, 230, 255, 255), stroke=(30, 30, 80, 255), sw=9), W / 2, 220, ease((t - L[1][0]) / .3))

def s_lotus(c, t, Tt, L):
    trikut(c, t, 'night')
    up = after(L, 1, t, (L[1][1] - L[1][0]) * 0.25)
    call = after(L, 1, t, (L[1][1] - L[1][0]) * 0.62)
    g = ease((t - L[1][0] - (L[1][1] - L[1][0]) * 0.62) / .6) if call else 0
    light_rays(c, 150, 600, t, 0.25 + 0.6 * g, col='#FFE7A8')
    x, gy, s = 650, GROUND + 60, 0.95
    elephant(c, x, gy, s, t, sad=0.0 if up else 0.5, trunk_up=up, look=(-1, -1))
    magar(c, 330, 1185, 1.0, t, open_=0.05)
    if up:
        tx, ty = trunk_tip(x, gy, s)
        lotus(c, tx, ty - 10, 1.0, glow=0.5 + 0.5 * g, t=t)
    else:
        lotus(c, 260, 1185, 0.9, glow=0.4 + 0.3 * math.sin(t * 4), t=t)
    water_front(c, 1195, t, 0.62, dark=0.4)
    if not after(L, 1, t, -.05):
        draw_img(c, T('vy', 'भगवान विष्णु याद आए', 80, fill=(255, 244, 220, 255), stroke=(30, 50, 130, 255), sw=9), W / 2, 220, ease((t - L[0][0] - .5) / .3))
    elif call:
        draw_img(c, T('hn', 'हे नारायण!', 140, fill=(255, 224, 100, 255), stroke=(140, 40, 0, 255), sw=12), W / 2, 230, g, 0.7 + 0.3 * g)
    else:
        draw_img(c, T('kt', 'एक कमल…', 100, fill=(255, 220, 235, 255), stroke=(140, 20, 80, 255), sw=9), W / 2, 220, ease((t - L[1][0]) / .3))

def s_vishnu(c, t, Tt, L):
    trikut(c, t, 'divine')
    light_rays(c, 540, 700, t, 0.8, col='#FFFFFF')
    k = ease(t / 1.6)
    vishnu_garuda(c, lerp(980, 540, k), lerp(260, 1000, k), lerp(0.3, 0.6, k), t, 1.0, aura=0.6)
    for i in range(10):
        ang = i * math.pi / 5 + t
        sparkle(c, 540 + math.cos(ang) * 420, 760 + math.sin(ang) * 380, 18, 0.5 + 0.5 * math.sin(t * 6 + i))
    draw_img(c, T('bv', 'भगवान विष्णु', 110, fill=(255, 248, 220, 255), stroke=(30, 50, 140, 255), sw=10), W / 2, 170, ease((t - .3) / .3))
    if after(L, 0, t, (L[0][1] - L[0][0]) * 0.4):
        draw_img(c, T('gr', 'गरुड़ पर सवार', 72, fill=(255, 235, 190, 255), stroke=(130, 40, 0, 255), sw=8), W / 2, 285, ease((t - L[0][0] - (L[0][1] - L[0][0]) * .4) / .3))

def s_reveal(c, t, Tt, L):
    d0 = L[0][1] - L[0][0]
    launch = L[0][0] + d0 * 0.3; hit = launch + 0.8
    free = ease((t - hit - .2) / .8) if t > hit else 0
    trikut(c, t, 'night' if t < hit else 'divine')
    if t >= hit: light_rays(c, 300, 600, t, 0.5, col='#FFF3B0')
    vx, vy, vs = 300, 690, 0.42
    flying = launch <= t < hit
    vishnu_garuda(c, vx, vy + math.sin(t * 2) * 8, vs, t, 0.6, aura=0.5, chakra_on=not flying, bless=after(L, 1, t))
    x, gy, s = 700, GROUND + 40 - 40 * free, 0.82
    up = after(L, 1, t)
    elephant(c, x, gy, s, t, pull=1.0 if t < hit else 0, trunk_up=up, look=(-1, -1) if up else (-1, 0))
    if t < hit + 0.6:
        magar(c, 330, 1185, 1.0, t, open_=0.05 + 0.5 * free, glow=clamp(1 - (t - hit) / .6) if t > hit else 0, a=1 - clamp((t - hit) / .6) if t > hit else 1)
    if up:
        tx, ty = trunk_tip(x, gy, s)
        lotus(c, tx, ty - 10, 0.9, glow=0.8, t=t)
    water_front(c, 1195, t, 0.6, dark=0.35 if t < hit else 0.0)
    if flying:
        u = (t - launch) / (hit - launch)
        hx, hy = vx - 262 * vs, vy + (-1030 + 120) * vs
        def bz(k):
            k = ease(k); ex, ey = 360, 1120; qx, qy = 30, 900
            return ((1 - k) ** 2 * hx + 2 * (1 - k) * k * qx + k * k * ex, (1 - k) ** 2 * hy + 2 * (1 - k) * k * qy + k * k * ey)
        for j in range(1, 5): chakra(c, *bz(max(0, u - j * .06)), 40, t, 0.25)
        chakra(c, *bz(u), 46, t, 1.0, spin=14)
    if hit <= t < hit + .35:
        c.drawRect(skia.Rect(0, 0, W, H), P(C('#FFFFFF', int(200 * (1 - (t - hit) / .35)))))
    if t < launch:
        draw_img(c, T('sc', 'सुदर्शन चक्र', 110, fill=(255, 230, 150, 255), stroke=(140, 50, 0, 255), sw=10), W / 2, 200, ease((t - .1) / .3))
    elif t >= hit and not up:
        draw_img(c, T('mk', 'मुक्त!', 150, fill=(255, 244, 200, 255), stroke=(30, 110, 40, 255), sw=12), W / 2, 200, free, 0.7 + .3 * free)
    elif up:
        a = ease((t - L[1][0]) / .3)
        petals(c, t, a)
        draw_img(c, T('sp', 'सच्चे मन की पुकार', 86, fill=(255, 244, 220, 255), stroke=(140, 30, 30, 255), sw=9), W / 2, 150, a)

def s_lesson(c, t, Tt, L):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C('#8EC5FC'), C('#FFF1D6')]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#FFF8EC', 240)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#1E5BD8'), 7))
    draw_img(c, T('seekh', 'सीख', 130, fill=(30, 80, 190, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 350, ease((t - L[0][0] + .2) / .4))
    ys = [680, 1000]
    for i in range(1, len(L)):
        a = ease((t - L[i][0] + .15) / .4)
        if a <= 0: continue
        img = T(('ls', i), L[i][2], 64, maxw=820, fill=(40, 30, 60, 255), stroke=(0, 0, 0, 0), sw=0)
        draw_img(c, img, W / 2, ys[i - 1] + (1 - a) * 20, a)
    vishnu(c, W / 2, 2300, 0.55, t, bless=True)

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
    trikut(c, t, 'divine')
    light_rays(c, 540, 1100, t, 0.4, col='#FFFFFF')
    vishnu(c, 540, 1330, 0.4, t, aura=0.6, bless=True)
    lotus(c, 540, 1335, 1.5)
    water_front(c, 1350, t, 0.5)
    if not after(L, 2, t, -.1):
        draw_img(c, T('o1', 'रोज़ ऐसी कहानियों के लिए', 82, fill=(255, 255, 255, 255), stroke=(40, 80, 130, 255), sw=8), W / 2, 220, ease(t / .35))
    else:
        draw_img(c, T('o2', 'मिलते हैं अगली कहानी में!', 76, fill=(255, 248, 225, 255), stroke=(110, 60, 20, 255), sw=8), W / 2, 220, ease((t - L[2][0] + .1) / .3))
    s1, e1 = L[1][0], L[1][1]; d = e1 - s1
    btns = [('like', 'LIKE', '#1E88E5', .28), ('share', 'SHARE', '#43A047', .45), ('sub', 'SUBSCRIBE', '#E53935', .8)]
    for i, (kind, label, col, f) in enumerate(btns):
        appear = ease((t - 0.2 - i * 0.18) / .3)
        if appear <= 0: continue
        press = s1 + d * f
        done = t > press
        sc = appear * (1 + (0.04 * math.sin(t * 7 + i) if not done else 0))
        if press < t < press + .15: sc *= 0.9
        if press + .15 <= t < press + .35: sc *= 1.08
        y = 430 + i * 175
        c.save(); c.translate(W / 2, y); c.scale(sc, sc)
        fill = col if not (done and kind == 'sub') else '#7A7A7A'
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-300, -68, 300, 68), 68, 68), P(C(fill)))
        if done: c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-300, -68, 300, 68), 68, 68), P(C('#FFFFFF'), 6))
        icon(c, kind, -190, 0)
        c.restore()
        lab = label if not (done and kind == 'sub') else 'SUBSCRIBED'
        draw_img(c, T(('btn', lab), lab, 60, stroke=(0, 0, 0, 0), sw=0), W / 2 + 40 * sc, y + 4, appear, sc)
        if done and t < press + .6:
            k = (t - press) / .6
            for j in range(6):
                ang = j * math.pi / 3
                sparkle(c, W / 2 + 250 + math.cos(ang) * 90 * k, y + math.sin(ang) * 70 * k, 16, 1 - k)

FN = dict(hook=s_hook, lake=s_lake, grab=s_grab, fight=s_fight, tired=s_tired, lotus=s_lotus, vishnu=s_vishnu, reveal=s_reveal, lesson=s_lesson, outro=s_outro)

def frame(sid, t, Tt, L):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    FN[sid](c, t, Tt, L)
    if sid != 'lesson': subtitle(c, L, t)
    fade = min(clamp(t / .08), clamp((Tt - t) / .08)) if sid != 'hook' else clamp((Tt - t) / .12)
    if fade < 1: c.drawRect(skia.Rect(0, 0, W, H), P(C('#000000', int(255 * (1 - fade)))))
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
