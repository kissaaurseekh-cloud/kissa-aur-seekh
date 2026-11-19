import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from gart import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'key': 0.2, 'regret': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'key': 0.35, 'lesson': 0.5, 'done': 0.45}.get(sid, 0.2)
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

def bg_city(c, t, mood='day', dark=0.0):
    sky(c, mood)
    if mood == 'day':
        sun(c, 860, 230, 80)
        for i, (x0, y0, s) in enumerate([(150, 200, .9), (650, 380, .7)]):
            cloud(c, (x0 + t * 15) % (W + 300) - 150, y0, s)
    street(c, dark)

# ---------------- scenes ----------------
def s_hook(c, t, Tt, L):
    sky(c, 'storm')
    flash = max(0, 1 - abs(t - 0.6) / 0.12) + max(0, 1 - abs(t - 0.85) / 0.08)
    street(c, 0.5)
    house(c, W / 2, GY, 560, 420, wall='#B9A27A', roof='#6E3B2E', crooked=0.12, cracks=1.0, glow=0.6 + 0.4 * math.sin(t * 5))
    qa = ease((t - L[1][0]) / .4)
    if qa > 0:
        q = T('q', '?', 260, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
        draw_img(c, q, W / 2, 330 + math.sin(t * 4) * 12, qa, 0.9 + .1 * math.sin(t * 6))
    k = ease(t / .5)
    title = T('title', 'आख़िरी घर', 150, fill=(255, 244, 220, 255), stroke=(120, 30, 20, 255), sw=10)
    draw_img(c, title, W / 2, 190 if qa <= 0 else lerp(190, 150, qa), k, 0.8 + 0.2 * k)
    if flash > 0: c.drawRect(skia.Rect(0, 0, W, H), P(C('#FFFFFF', int(200 * clamp(flash)))))

def s_city(c, t, Tt, L):
    bg_city(c, t)
    for x, wl, rf, s in [(170, '#F7D08A', '#C0392B', .62), (540, '#A8D8C8', '#2E6E8E', .7), (910, '#F4B6A6', '#7A3E8E', .62)]:
        c.save(); c.translate(x, GY - 20); c.scale(s, s); house(c, 0, 0, 420, 360, wall=wl, roof=rf); c.restore()
    if after(L, 1, t, 0.3):
        for i, (x, y) in enumerate([(170, 760), (540, 700), (910, 760), (330, 850), (760, 830)]):
            sparkle(c, x, y, 26 + 10 * math.sin(t * 7 + i), clamp((t - L[1][0] - 0.3 - i * .1) / .2))
    ramu(c, 540, GY + 120, 0.95, 'proud', False, t, old=0.15, prop='trowel', look=(0, 0))
    if after(L, 0, t):
        k = lt(L, 0, t); n = int(lerp(1, 40, ease(k)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(700, 300, 1020, 470), 40, 40), P(C('#FFFFFF', 235)))
        num = T(('n', n), f'{n} साल', 84, fill=(200, 70, 30, 255), stroke=(0, 0, 0, 0), sw=0)
        draw_img(c, num, 860, 388)

def s_retire(c, t, Tt, L):
    bg_city(c, t)
    house(c, 760, GY - 30, 520, 420, wall='#F6E3B4', roof='#8E2C48')
    old = ease(t / 0.8)
    talk = sp(L, 1, t)
    ramu(c, 280, GY + 130, 0.85, 'sad' if after(L, 1, t, 1.6) else 'neutral', talk, t, old=old, stick=old > .6, look=(1, 0))
    seth(c, 800, GY + 130, 0.85, 'neutral', False, t, look=(-1, 0))
    if after(L, 1, t, 1.5):
        a = clamp((t - L[1][0] - 1.5) / .25)
        bubble(c, 330, 330, 230, 150, a, tail=(-1, 1))
        if a > .5: mini_family(c, 330, 420, 1.1)

def s_request(c, t, Tt, L):
    bg_city(c, t)
    house(c, 760, GY - 30, 520, 420, wall='#F6E3B4', roof='#8E2C48')
    rm = 'sad' if after(L, 2, t) else 'neutral'
    ramu(c, 280, GY + 130, 0.85, rm, False, t, old=1, stick=True, look=(1, 0))
    seth(c, 800, GY + 130, 0.85, 'sad', sp(L, 1, t), t, look=(-1, 0))
    if after(L, 1, t):
        a = ease((t - L[1][0]) / .3)
        one = T('one', '1', 200, fill=(255, 255, 255, 255), stroke=(140, 40, 60, 255), sw=10)
        draw_img(c, one, 800, 300, a if not after(L, 2, t) else clamp(1 - (t - L[2][0]) / .3), 0.7 + .3 * a)

def s_careless(c, t, Tt, L):
    bg_city(c, t)
    # half-built crooked wall at right
    prog = 0.15 + 0.35 * ease((t - L[2][0] + .3) / (L[2][1] - L[2][0] + .3)) + 0.12 * ease(lt(L, 3, t))
    crook = 0.12 * ease((t - L[2][0]) / 1.2)
    house(c, 760, GY, 460, 420, wall='#C9A27A', roof='#6E3B2E', prog=prog, crooked=crook, door='#6B5A4A')
    if after(L, 0, t):
        k = ease((t - L[0][0]) / .4); drop = (1 - k) * -500
        brick_pile(c, 200, GY + 40 + drop, True, 0.9)
        if sp(L, 0, t) and t > L[0][0] + .5:
            tag = T('tag', 'सस्ती!', 64, fill=(255, 255, 255, 255), stroke=(0, 0, 0, 0), sw=0)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(80, 870, 330, 970), 20, 20), P(C('#E53935')))
            draw_img(c, tag, 205, 920)
    if after(L, 1, t):
        cement_bag(c, 470, GY + 90, 0.8)
        sand_heap(c, 470, GY + 100, 0.4 + 0.6 * ease(lt(L, 1, t)), 0.9)
        if sp(L, 1, t):
            for i in range(14):
                yy = ((t * 2 + i / 14) % 1) * 260
                c.drawCircle(470 + math.sin(i * 3) * 10, GY - 160 + yy, 6, P(C('#E8C27A')))
    arm = 'shrug' if after(L, 3, t) else 'down'
    ramu(c, 470, GY + 150, 0.8, 'neutral' if not after(L, 3, t) else 'happy', False, t, old=1, arm=arm, look=(1, -0.3))
    if after(L, 3, t):
        a = clamp((t - L[3][0]) / .25)
        bubble(c, 540, 360, 360, 150, a, tail=(-1, 1))
        b = T('bub', 'क्या फ़र्क पड़ता है?', 64, fill=(60, 40, 20, 255), stroke=(0, 0, 0, 0), sw=0)
        draw_img(c, b, 540, 360, a)

def s_done(c, t, Tt, L):
    bg_city(c, t)
    k = ease(t / 0.7)
    house(c, W / 2, GY, 560, 440, wall='#E6C79A', roof='#8B3A2E', prog=lerp(0.7, 1.0, k), crooked=0.04)
    if after(L, 1, t, 0.6):
        cr = ease((t - L[1][0] - 0.6) / 0.7)
        shake = math.sin(t * 50) * 4 * cr
        c.save(); c.translate(shake, 0)
        house(c, W / 2, GY, 560, 440, wall='#E6C79A', roof='#8B3A2E', prog=1, crooked=0.04, cracks=cr, glow=cr)
        c.restore()
        c.drawRect(skia.Rect(0, 0, W, H), P(C('#200000', int(60 * cr))))
    ramu(c, 170, GY + 150, 0.62, 'neutral', False, t, old=1, look=(1, 0))

def s_key(c, t, Tt, L):
    bg_city(c, t)
    house(c, 540, GY - 60, 460, 360, wall='#E6C79A', roof='#8B3A2E', crooked=0.04)
    # Ramu walks in from left during line 0
    rx = lerp(90, 290, ease(lt(L, 0, t) * 1.2))
    d1 = L[1][1] - L[1][0]
    give = after(L, 1, t, d1 * .35)
    handed = after(L, 1, t, d1 * .75)
    rmood = 'shocked' if after(L, 2, t, .2) else ('happy' if handed else 'neutral')
    ramu(c, rx, GY + 160, 0.8, rmood, False, t, old=1, arm='out' if not give else 'down',
         prop='key' if not give or handed else None, look=(1, 0))
    seth(c, 800, GY + 160, 0.8, 'happy', sp(L, 2, t) or sp(L, 3, t), t, look=(-1, 0), arm='give' if give and not handed else 'down',
         prop='key' if give and not handed else None)
    if after(L, 2, t):
        z = ease((t - L[2][0]) / .5)
        c.drawRect(skia.Rect(0, 0, W, H), P(C('#000000', int(120 * z))))
        draw_key(c, W / 2, 560, lerp(0.8, 2.2, z), math.sin(t * 2) * .1, glow=z)
        for i in range(8):
            a = i * math.pi / 4 + t
            sparkle(c, W / 2 + math.cos(a) * 300, 560 + math.sin(a) * 220, 24, z)
        if after(L, 3, t):
            gift = T('gift', 'तोहफ़ा', 120, fill=(255, 236, 160, 255), stroke=(120, 60, 0, 255), sw=9)
            draw_img(c, gift, W / 2, 880, ease((t - L[3][0]) / .4))

def s_regret(c, t, Tt, L):
    sky(c, 'sad'); street(c, 0.3)
    house(c, 800, GY - 40, 420, 340, wall='#C9B08A', roof='#6E3B2E', crooked=0.06, cracks=1.0)
    shake = math.sin(t * 60) * 10 * clamp(1 - t / 1.2) if t < 1.2 else 0
    z = lerp(1.0, 1.35, ease(t / 1.5))
    c.save(); zoom(c, 330, 900, z)
    # crack in ground
    if t > .2:
        k = ease((t - .2) / .5)
        path = skia.Path(); path.moveTo(100, GY + 30); path.lineTo(100 + 120 * k, GY + 60); path.lineTo(100 + 220 * k, GY + 40); path.lineTo(100 + 380 * k, GY + 80)
        c.drawPath(path, P(C('#3A2A1E'), 10))
    ramu(c, 330, GY + 120, 0.9, 'shocked' if not after(L, 2, t) else 'sad', False, t, old=1,
         arm='face' if sp(L, 0, t) else 'down', shake=shake, tear=ease((t - L[2][0]) / .5) if after(L, 2, t) else 0)
    c.restore()
    if after(L, 1, t, .3):
        a = clamp((t - L[1][0] - .3) / .35)
        bubble(c, 760, 330, 270, 210, a, tail=(-1, 1))
        c.save(); c.translate(760, 470); c.scale(0.55, 0.55)
        house(c, 0, 0, 460, 380, wall='#FFE0A3', roof='#C0392B', prog=1)
        c.restore()
        for i in range(5): sparkle(c, 600 + i * 80, 160 + (i % 2) * 40, 18, a * (0.5 + 0.5 * math.sin(t * 6 + i)))

def s_lesson(c, t, Tt, L):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C('#F7A66B'), C('#FFE6B8')]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#FFF8EC', 240)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#E08A3C'), 7))
    draw_img(c, T('seekh', 'सीख', 130, fill=(200, 80, 30, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 350, ease((t - L[0][0] + .2) / .4))
    ys = [680, 1000]
    for i in range(1, len(L)):
        a = ease((t - L[i][0] + .15) / .4)
        if a <= 0: continue
        img = T(('ls', i), L[i][2], 64, maxw=820, fill=(70, 40, 20, 255), stroke=(0, 0, 0, 0), sw=0)
        draw_img(c, img, W / 2, ys[i - 1] + (1 - a) * 20, a)
    c.save(); c.translate(W / 2, 1720); c.scale(0.55, 0.55); house(c, 0, 0, 460, 380, wall='#FFE0A3', roof='#C0392B'); c.restore()

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
    bg_city(c, t)
    c.save(); c.translate(W / 2, GY); c.scale(0.62, 0.62); house(c, 0, 0, 480, 380, wall='#FFE0A3', roof='#C0392B'); c.restore()
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

FN = dict(hook=s_hook, city=s_city, retire=s_retire, request=s_request, careless=s_careless, done=s_done, key=s_key, regret=s_regret, lesson=s_lesson, outro=s_outro)

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
