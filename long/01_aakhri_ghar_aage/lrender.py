import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lart import *
from lscript import SCENES

FPS = 30
W, H = LW, LH
DUR = json.load(open('vo/durs.json'))
FB = '/home/claude/kissa-aur-seekh/assets/fonts/Hind-Bold.ttf'
LEAD = dict(storm=3.6, monsoon=2.6, newhouse=2.8, lesson=0.9, outro=0.5)
TAIL = dict(rebuild=6.5, newhouse=2.2, outro=1.6, storm=0.8, decision=1.6, village=1.4)

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        t = LEAD.get(sid, 1.0); L = []
        for i, item in enumerate(lines):
            txt = item[2] if len(item) > 2 else item[1]
            d = DUR[f'vo/{sid}_{i}.wav']; L.append((t, t + d, txt, f'vo/{sid}_{i}.wav', item[0])); t += d + 0.75
        tl.append((sid, t - 0.75 + TAIL.get(sid, 1.0), L))
    return tl

def text_img(txt, size, maxw=1500, fill=(255, 255, 255, 255), stroke=(20, 12, 6, 255), sw=6, box=False):
    f = ImageFont.truetype(FB, size, layout_engine=ImageFont.Layout.RAQM)
    words = txt.split(' '); lines = []; cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if f.getlength(test) > maxw and cur: lines.append(cur); cur = w
        else: cur = test
    lines.append(cur)
    lh = int(size * 1.4); wmax = int(max(f.getlength(l) for l in lines)) + sw * 2 + 10
    pad = 30 if box else 12
    img = Image.new('RGBA', (wmax + pad * 2, lh * len(lines) + pad * 2 - int(size * .15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if box: d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=26, fill=(15, 10, 6, 175))
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
    a, b, txt = L[idx][:3]
    end = min(b + 0.5, L[idx + 1][0] - 0.05) if idx + 1 < len(L) else b + 0.5
    if t > end: return
    img = T(('sub', txt), txt, 46, box=True, sw=0)
    k = clamp((t - a + 0.05) / 0.12)
    draw_img(c, img, W / 2, 1000 - img.height() / 2 + 40, min(k, clamp((end - t) / 0.12)))

def lt(L, i, t): return clamp((t - L[i][0]) / (L[i][1] - L[i][0]))
def sp(L, i, t): return L[i][0] <= t <= L[i][1]
def after(L, i, t, d=0): return t >= L[i][0] + d
def talk(L, t, i): return sp(L, i, t)

HX = 1320   # main house x
def weak_house(c, cracks=0.5, glow=0.0, t=0.0, dark=0.0, prog=1.0, crooked=0.08):
    wl = blend('#C9B08A', '#3A3A4A', dark); rf = blend('#6E3B2E', '#1E1A22', dark)
    house(c, HX, LGY, 560, 420, wall=wl, roof=rf, crooked=crooked, cracks=cracks, glow=glow, prog=prog)
def good_house(c, prog=1.0, dark=0.0, lit=0.0):
    house(c, HX, LGY, 560, 420, wall=blend('#FFE0A3', '#5A5060', dark), roof=blend('#C0392B', '#4A2228', dark), prog=prog)
    if lit > 0:
        for wx in (-168, 168):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(HX + wx - 45, LGY - 302, HX + wx + 45, LGY - 176), 8, 8), P(C('#FFD54F', int(200 * lit))))

def day_bg(c, t, mood='day', dark=0.0, wet=0.0, far=True):
    lsky(c, mood)
    if mood in ('day', 'morning', 'warm'):
        sun(c, 1700, 170, 70)
        for i, (x0, y0, s) in enumerate([(300, 160, .9), (1100, 120, .7), (800, 260, .6)]):
            cloud(c, (x0 + t * 14) % (LW + 300) - 150, y0, s)
    if far: far_houses(c, dark)
    lground(c, dark, wet)

# ---------------- scenes ----------------
def s_storm(c, t, Tt, L):
    lsky(c, 'storm'); far_houses(c, 0.8); lground(c, 0.6, 0.6)
    z = lerp(1.0, 1.12, ease(t / Tt))
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    weak_house(c, cracks=1.0, glow=0.4 + 0.3 * math.sin(t * 4), t=t, dark=0.45)
    c.restore()
    rain(c, t, 1.0); flash(c, t, [0.5, 0.75, 6.0])
    k = ease((t - 0.3) / 0.8); k2 = clamp((L[0][0] - 0.3 - t) / 0.4) if t < L[0][0] else 0
    if t < L[0][0] + 0.2:
        a = min(k, max(k2, 0)) if t > 0.3 else 0
        draw_img(c, T('title', 'आख़िरी घर', 150, fill=(255, 244, 220, 255), stroke=(120, 30, 20, 255), sw=10), W / 2, 380, a)
        draw_img(c, T('title2', 'आगे क्या हुआ?', 96, fill=(255, 214, 64, 255), stroke=(60, 20, 0, 255), sw=8), W / 2, 540, a)

def s_recap(c, t, Tt, L):
    if t < L[1][1] + 0.3:
        day_bg(c, t, 'day', far=False)
        for x, wl, rf, s in [(300, '#F7D08A', '#C0392B', .7), (700, '#A8D8C8', '#2E6E8E', .75), (1650, '#F4B6A6', '#7A3E8E', .7)]:
            c.save(); c.translate(x, LGY); c.scale(s, s); house(c, 0, 0, 420, 360, wall=wl, roof=rf); c.restore()
        if t < L[1][0]:
            ramu(c, 1150, LGY + 60, 0.72, 'proud', False, t, old=0.2, prop='trowel')
        else:
            k = lt(L, 1, t)
            house(c, 1250, LGY, 460, 380, wall='#C9A27A', roof='#6E3B2E', prog=0.2 + 0.7 * ease(k), crooked=0.1 * ease(k))
            brick_pile(c, 900, LGY + 20, True, 0.8)
            ramu(c, 1000, LGY + 60, 0.7, 'neutral', False, t, old=1, arm='shrug' if k > .6 else 'down')
        tint(c, '#704214', 70, 120)
        draw_img(c, T('pehle', 'पहले…', 70, fill=(255, 240, 210, 255), stroke=(60, 30, 10, 255), sw=6), 140, 80, 1)
    elif t < L[4][0]:
        day_bg(c, t, 'day')
        weak_house(c, cracks=0.0)
        give = after(L, 2, t, 0.3)
        ramu(c, 520, LGY + 60, 0.72, 'shocked' if after(L, 3, t, .3) else 'neutral', False, t, old=1, look=(1, 0), prop='key' if after(L, 3, t, 1.0) else None)
        seth(c, 860, LGY + 60, 0.72, 'happy', talk(L, t, 3), t, look=(-1, 0), arm='give' if give and not after(L, 3, t, 1.0) else 'down',
             prop='key' if give and not after(L, 3, t, 1.0) else None)
        tint(c, '#704214', 70, 120)
    else:
        lsky(c, 'storm'); far_houses(c, 0.8); lground(c, 0.6, 0.6)
        weak_house(c, cracks=1.0, dark=0.45); rain(c, t, 0.8)
        k = ease((t - L[4][0] - 1.8) / .5)
        draw_img(c, T('asli', 'असली कहानी अब शुरू होती है…', 84, fill=(255, 214, 64, 255), stroke=(60, 20, 0, 255), sw=8), W / 2, 260, k)

def s_movein(c, t, Tt, L):
    day_bg(c, t, 'day')
    weak_house(c, cracks=0.15)
    k = ease(t / 3.0); walk = math.sin(t * 8) * 5 if k < 1 else 0
    ramu(c, lerp(-100, 640, k), LGY + 60 + walk, 0.72, 'neutral', False, t, old=1, look=(1, 0))
    kamla(c, lerp(-300, 440, k), LGY + 60 - walk, 0.68, 'happy', False, t, look=(1, 0))
    hop = abs(math.sin(t * 6)) * 40 if after(L, 1, t) else 0
    boy(c, lerp(-200, 880, k), LGY + 90 - hop, 0.72, 'happy', talk(L, t, 1), t, look=(1, -0.3), arm='point' if after(L, 1, t) else 'down')
    if after(L, 1, t): sparkle(c, 980, 420, 26, 0.5 + 0.5 * math.sin(t * 7))

def s_breaking(c, t, Tt, L):
    day_bg(c, t, 'day')
    weak_house(c, cracks=0.5 + 0.4 * lt(L, 0, t))
    # falling plaster bits during line 0
    if sp(L, 0, t):
        for i in range(5):
            ph = ((t - L[0][0]) * 0.8 + i / 5) % 1
            c.drawRect(skia.Rect.MakeXYWH(HX - 150 + i * 70, LGY - 420 + ph * 420, 18, 12), P(C('#D9C29A', int(255 * (1 - ph)))))
    ramu(c, 560, LGY + 60, 0.72, 'sad' if after(L, 2, t) else 'neutral', False, t, old=1, look=(1, 0.6) if after(L, 3, t) else (1, 0))
    kamla(c, 860, LGY + 60, 0.68, 'sad', talk(L, t, 2), t, look=(-1, 0))

def s_monsoon(c, t, Tt, L):
    lsky(c, 'rain'); far_houses(c, 0.7); lground(c, 0.5, 1.0)
    for x in (300, 800, 1300, 1800): cloud(c, x, 90, 1.6, col='#6E7888', a=240)
    weak_house(c, cracks=0.6 + 0.4 * ease(lt(L, 1, t)), glow=0.3 * ease(lt(L, 1, t)), dark=0.35)
    for bx in (HX - 230, HX + 230):
        drips(c, bx, LGY - 420, LGY - 70, t); bucket(c, bx, LGY + 20, 0.9, 0.2 + 0.3 * clamp(t / Tt))
    boy(c, 760, LGY + 90, 0.72, 'sad', talk(L, t, 2), t, look=(1, -0.6))
    if after(L, 3, t):
        ramu(c, 480, LGY + 60, 0.72, 'sad', False, t, old=1, look=(1, 0.5))
    rain(c, t, 1.0, 0.35); flash(c, t, [1.2, 1.4, L[1][0] + 1.0])

def s_confess(c, t, Tt, L):
    day_bg(c, t, 'morning', wet=1.0)
    weak_house(c, cracks=1.0)
    c.drawRect(skia.Rect(300, LGY - 10, 1100, LGY + 30), P(C('#A08060')))      # doorstep
    ramu(c, 560, LGY + 60, 0.72, 'sad', talk(L, t, 0) or talk(L, t, 1) or talk(L, t, 3), t, old=1, look=(1, 0.3))
    boy(c, 860, LGY + 90, 0.72, 'neutral' if not after(L, 2, t) else 'sad', talk(L, t, 2), t, look=(-1, -0.4))
    if sp(L, 1, t):
        a = clamp((t - L[1][0]) / .3)
        bubble(c, 420, 260, 220, 120, a, tail=(1, 1))
        if a > .5: brick_pile(c, 400, 330, True, 0.6)

def s_decision(c, t, Tt, L):
    day_bg(c, t, 'warm', wet=0.4)
    weak_house(c, cracks=1.0)
    up = after(L, 0, t, 1.2)
    ramu(c, 620, LGY + 60, 0.74, 'proud' if after(L, 1, t) else 'neutral', talk(L, t, 1), t, old=1, look=(1, -0.2), prop='trowel' if up else None, arm='down')
    if up:
        k = ease((t - L[0][0] - 1.2) / .5)
        for i in range(8):
            a = i * math.pi / 4 + t
            sparkle(c, 700 + math.cos(a) * 120, 500 + math.sin(a) * 120, 18, k * (0.5 + 0.5 * math.sin(t * 6 + i)))
    if after(L, 2, t):
        hop = abs(math.sin(t * 6)) * 30
        boy(c, 900, LGY + 90 - hop, 0.72, 'happy', talk(L, t, 2), t, look=(-1, -0.4), arm='point')

def s_rebuild(c, t, Tt, L):
    day_bg(c, t * 3, 'day')
    # demolish first 1.5s of line 0, then rebuild across the scene
    d0 = L[0][0]
    if t < d0 + 1.5:
        weak_house(c, cracks=1.0, prog=lerp(1.0, 0.12, ease((t - d0) / 1.5)) if t > d0 else 1.0)
    else:
        k = ease((t - d0 - 1.5) / (Tt - d0 - 3.0))
        good_house(c, prog=lerp(0.12, 1.0, k))
    brick_pile(c, 1780, LGY + 20, False, 0.8); cement_bag(c, 980, LGY + 40, 0.7)
    rx = 820
    ramu(c, rx, LGY + 60, 0.72, 'proud', talk(L, t, 1), t, old=1, look=(1, -0.2), arm='out', prop='trowel')
    if sp(L, 1, t): plumb(c, rx + 0.72 * 1.15 * 170, LGY + 60 - 0.72 * 1.15 * 322, 260, t)
    hop = abs(math.sin(t * 5)) * 20
    boy(c, 520, LGY + 90 - hop, 0.7, 'happy', False, t, look=(1, -0.3))
    if after(L, 2, t):
        day = int(lerp(1, 20, ease((t - L[2][0]) / (Tt - L[2][0] - 1))))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(80, 60, 380, 190), 30, 30), P(C('#FFFFFF', 230)))
        draw_img(c, T(('day', day), f'दिन {day}', 72, fill=(200, 70, 30, 255), stroke=(0, 0, 0, 0), sw=0), 230, 128)

def s_village(c, t, Tt, L):
    day_bg(c, t, 'day', far=False)
    for x, wl, rf, s in [(250, '#F7D08A', '#C0392B', .62), (560, '#A8D8C8', '#2E6E8E', .62), (1800, '#F4B6A6', '#7A3E8E', .55)]:
        c.save(); c.translate(x, LGY); c.scale(s, s); house(c, 0, 0, 420, 360, wall=wl, roof=rf); c.restore()
    good_house(c, prog=0.8)
    if sp(L, 0, t) and t > L[0][0] + 3.5:
        for i, (x, y) in enumerate([(250, 560), (560, 560)]): sparkle(c, x, y, 26, 0.5 + 0.5 * math.sin(t * 6 + i))
    k = ease((t - 0.3) / 2.5)
    cols = [('#3C7DBF', None), ('#8E24AA', '#F28C28'), ('#43A047', None), ('#E65100', '#FFFFFF')]
    for i, (kc, tb) in enumerate(cols):
        x = lerp(-150 - i * 140, 380 + i * 150, k)
        man(c, x, LGY + 70 + math.sin(t * 8 + i) * (4 if k < 1 else 0), 0.62, 'happy', talk(L, t, 1) and i == 1, t, look=(1, 0), kurta=kc, turban=tb, old=0.3 * (i % 2))
    ramu(c, 1020, LGY + 60, 0.72, 'happy' if after(L, 1, t) else 'shocked', False, t, old=1, look=(-1, 0))
    if after(L, 2, t):
        ck = ease((t - L[2][0]) / 2.0)
        cart(c, lerp(2300, 1640, ck), LGY + 40, 0.9, t, ck < 1)
        if ck >= 1: seth(c, 1880, LGY + 60, 0.55, 'happy', False, t, look=(-1, 0))

def s_newhouse(c, t, Tt, L):
    close = after(L, 1, t, 1.0) and not after(L, 2, t, 2.0)
    lsky(c, 'rain'); far_houses(c, 0.6); lground(c, 0.45, 1.0)
    for x in (300, 900, 1500): cloud(c, x, 90, 1.5, col='#6E7888', a=230)
    good_house(c, dark=0.2, lit=1.0)
    ramu(c, 520, LGY + 60, 0.72, 'happy', talk(L, t, 2), t, old=1, look=(1, 0))
    kamla(c, 760, LGY + 60, 0.68, 'happy', False, t, look=(-1, 0))
    boy(c, 960, LGY + 90 - (abs(math.sin(t * 6)) * 30 if sp(L, 1, t) else 0), 0.72, 'happy', talk(L, t, 1), t, look=(-1, -0.3), arm='point' if sp(L, 1, t) else 'down')
    rain(c, t, 1.0, 0.3)
    if t < L[0][0]:
        k = ease(t / 1.5)
        draw_img(c, T('agla', 'एक साल बाद…', 80, fill=(255, 255, 255, 255), stroke=(20, 30, 60, 255), sw=8), W / 2, 200, k)
    if close:
        k = ease((t - L[1][0] - 1.0) / .5)
        c.drawRect(skia.Rect(0, 0, W, H), P(C('#000000', int(150 * k))))
        big_brick(c, W / 2, 440, 1000 * (0.8 + 0.2 * k), 320 * (0.8 + 0.2 * k))
        draw_img(c, T('brick', 'हर ईंट, अपने घर की तरह।', 84, fill=(255, 244, 220, 255), stroke=(90, 30, 10, 255), sw=6), W / 2, 440, k)

def s_lesson(c, t, Tt, L):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C('#F7A66B'), C('#FFE6B8')]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    c.save(); c.translate(1640, 1000); c.scale(0.7, 0.7); house(c, 0, 0, 460, 380, wall='#FFE0A3', roof='#C0392B'); c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(200, 90, 1380, 880), 46, 46), P(C('#FFF8EC', 240)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(200, 90, 1380, 880), 46, 46), P(C('#E08A3C'), 7))
    draw_img(c, T('seekh', 'सीख', 120, fill=(200, 80, 30, 255), stroke=(0, 0, 0, 0), sw=0), 790, 210, ease((t - L[0][0] + .2) / .4))
    for i, y in [(1, 440), (2, 700)]:
        a = ease((t - L[i][0] + .15) / .4)
        if a > 0:
            draw_img(c, T(('ls', i), L[i][2], 56, maxw=1050, fill=(70, 40, 20, 255), stroke=(0, 0, 0, 0), sw=0), 790, y + (1 - a) * 20, a)

def icon(c, kind, x, y, col='#FFFFFF'):
    p = P(C(col))
    if kind == 'like':
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 26, y - 6, x + 14, y + 30), 8, 8), p)
        c.drawRect(skia.Rect(x - 40, y - 4, x - 30, y + 30), p)
        th = skia.Path(); th.moveTo(x - 22, y - 4); th.lineTo(x - 6, y - 34); th.quadTo(x + 6, y - 36, x + 4, y - 20); th.lineTo(x, y - 6); th.close(); c.drawPath(th, p)
    elif kind == 'share':
        ar = skia.Path(); ar.moveTo(x - 34, y + 26); ar.quadTo(x - 30, y - 12, x + 6, y - 12); ar.lineTo(x + 6, y - 30); ar.lineTo(x + 38, y - 2)
        ar.lineTo(x + 6, y + 26); ar.lineTo(x + 6, y + 8); ar.quadTo(x - 18, y + 6, x - 34, y + 26); ar.close(); c.drawPath(ar, p)
    else:
        bl = skia.Path(); bl.moveTo(x - 28, y + 18); bl.quadTo(x - 22, y + 8, x - 22, y - 8); bl.quadTo(x - 20, y - 32, x, y - 32)
        bl.quadTo(x + 20, y - 32, x + 22, y - 8); bl.quadTo(x + 22, y + 8, x + 28, y + 18); bl.close()
        c.drawPath(bl, p); c.drawCircle(x, y + 26, 8, p); c.drawCircle(x, y - 36, 5, p)

def s_outro(c, t, Tt, L):
    day_bg(c, t, 'day')
    good_house(c)
    ramu(c, 400, LGY + 60, 0.62, 'happy', False, t, old=1); boy(c, 600, LGY + 90, 0.62, 'happy', False, t)
    if not after(L, 2, t, -.1):
        draw_img(c, T('o1', 'रोज़ ऐसी कहानियों के लिए', 76, fill=(255, 255, 255, 255), stroke=(40, 80, 130, 255), sw=8), 860, 110, ease(t / .35))
    else:
        draw_img(c, T('o2', 'मिलते हैं अगली कहानी में!', 76, fill=(255, 248, 225, 255), stroke=(110, 60, 20, 255), sw=8), 860, 110, ease((t - L[2][0] + .1) / .3))
    s1, e1 = L[1][0], L[1][1]; d = e1 - s1
    for i, (kind, label, col, f) in enumerate([('like', 'LIKE', '#1E88E5', .28), ('share', 'SHARE', '#43A047', .45), ('sub', 'SUBSCRIBE', '#E53935', .8)]):
        appear = ease((t - 0.2 - i * 0.18) / .3)
        if appear <= 0: continue
        press = s1 + d * f; done = t > press
        sc = appear * (1 + (0.04 * math.sin(t * 7 + i) if not done else 0))
        if press < t < press + .15: sc *= 0.9
        y = 250 + i * 150; cx = 860
        c.save(); c.translate(cx, y); c.scale(sc, sc)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-280, -60, 280, 60), 60, 60), P(C(col if not (done and kind == 'sub') else '#7A7A7A')))
        if done: c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-280, -60, 280, 60), 60, 60), P(C('#FFFFFF'), 6))
        icon(c, kind, -180, 0); c.restore()
        lab = label if not (done and kind == 'sub') else 'SUBSCRIBED'
        draw_img(c, T(('btn', lab), lab, 54, stroke=(0, 0, 0, 0), sw=0), cx + 40 * sc, y + 4, appear, sc)

FN = dict(storm=s_storm, recap=s_recap, movein=s_movein, breaking=s_breaking, monsoon=s_monsoon, confess=s_confess,
          decision=s_decision, rebuild=s_rebuild, village=s_village, newhouse=s_newhouse, lesson=s_lesson, outro=s_outro)

def frame(sid, t, Tt, L):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    FN[sid](c, t, Tt, L)
    if sid != 'lesson': subtitle(c, L, t)
    fade = min(clamp(t / .25), clamp((Tt - t) / .25)) if sid != 'storm' else min(clamp(t / 0.8), clamp((Tt - t) / .25))
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
        ims = []
        for sid, Tt, L in tl:
            pts = [L[0][0] + 0.8, L[-1][1] - 0.3] if len(L) < 3 else [L[0][0] + 0.8, L[len(L) // 2][0] + 1.0, L[-1][1] - 0.3]
            for tt in pts: ims.append(Image.fromarray(frame(sid, tt, Tt, L)).convert('RGB').resize((480, 270)))
        cols = 5; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (480 * cols, 270 * rows))
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 480, (i // cols) * 270))
        sheet.save('sheet.jpg', quality=82); print('total', sum(x[1] for x in tl))
    else:
        which = sys.argv[2:] or [s for s, _, _ in tl]
        for i, (sid, Tt, L) in enumerate(tl):
            if sid in which: print(sid, render_scene(i, sid, Tt, L), flush=True)
