import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from mart import sparkle as _sp
from gnart import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'reveal': 0.25, 'mouse': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'lesson': 0.5, 'circle': 1.6, 'reveal': 0.9, 'think': 0.5, 'kartik': 0.5, 'hook': 0.3}.get(sid, 0.2)
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





GROUND = 1340

def parents(c, cx, gy, s, t, talk=False, smile=True):
    parvati(c, cx - 200 * s, gy, s, t, 'happy' if smile else 'neutral')
    shiv(c, cx + 170 * s, gy, s, t, smile=smile and not talk, talk=talk)

def ganesh_orbit(c, cx, gy, s, gs, rx, ry, th, t, draw_parents, hands='namaste', eyes='closed'):
    """Ganesh walking around the parents; th = angle (0 = in front)."""
    x = cx + rx * math.sin(th); y = gy + ry * math.cos(th)
    front = math.cos(th) >= 0
    k = gs * (0.85 + 0.15 * math.cos(th))
    bob = abs(math.sin(t * 7)) * 8
    if not front: ganesh(c, x, y - bob, k, t, eyes=eyes, hands=hands, aura=0.3)
    draw_parents()
    if front: ganesh(c, x, y - bob, k, t, eyes=eyes, hands=hands, aura=0.3)

def s_hook(c, t, Tt, L):
    cosmos(c, t, dawn=0.25)
    light_rays(c, 540, 1100, t, 0.35, col='#FFE7A8')
    # top: the earth, with a peacock flying round it
    globe(c, 540, 470, 118, t)
    th = t * 2.4
    px, py = 540 + 270 * math.cos(th), 470 + 95 * math.sin(th)
    orbit(c, 540, 470, 270, 95, 0, col='#B3E5FC', w=5)
    if math.sin(th) < 0: peacock(c, px, py, 0.16, t, 1, rider=True, facing=-1 if math.sin(th + 1.57) > 0 else 1)
    globe(c, 540, 470, 118, t) if math.sin(th) < 0 else None
    if math.sin(th) >= 0: peacock(c, px, py, 0.16, t, 1, rider=True, facing=-1 if math.sin(th + 1.57) > 0 else 1)
    # bottom: Ganesh ji circling his parents
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 1180), skia.Point(0, H)], [C('#E8F1FA'), C('#AFC4DA')]))
    c.drawRect(skia.Rect(0, 1190, W, H), p)
    orbit(c, 540, 1300, 380, 75, 0, col='#FFD54F', w=6)
    ganesh_orbit(c, 540, 1300, 0.5, 0.34, 380, 75, t * 1.6 + 1.98, t, lambda: parents(c, 540, 1300, 0.5, t))
    title = T('title', 'ये कैसी परिक्रमा?', 100, fill=(255, 244, 220, 255), stroke=(120, 40, 0, 255), sw=10)
    k = ease(t / .5); draw_img(c, title, W / 2, 170, k, 0.85 + .15 * k)
    if after(L, 0, t, 1.0):
        q = T('q', '?', 220, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
        a = ease((t - L[0][0] - 1.0) / .3)
        draw_img(c, q, 880, 700 + math.sin(t * 4) * 10, a, 0.7 + 0.3 * a)
        draw_img(c, q, 200, 700 + math.sin(t * 4 + 1) * 10, a, 0.6 + 0.2 * a)

def s_contest(c, t, Tt, L):
    kailash(c, t)
    parents(c, 360, GROUND, 0.62, t, talk=sp(L, 0, t) or sp(L, 1, t), smile=not (sp(L, 0, t) or sp(L, 1, t)))
    kartikeya(c, 735, GROUND, 0.52, t, 'happy', facing=-1, look=(-1, 0))
    ganesh(c, 945, GROUND, 0.38, t, look=(-1, 0))
    if after(L, 1, t, .2):
        a = ease((t - L[1][0] - .2) / .4)
        globe(c, 540, 330, 110 * a + 1, t, a)
        orbit(c, 540, 330, 230, 80, clamp((t - L[1][0] - .5) / (L[1][1] - L[1][0] - .5)) * 3 % 1.0001, col='#FFE082', w=7, a=a)
        n = min(3, 1 + int(clamp((t - L[1][0] - .5) / (L[1][1] - L[1][0] - .5)) * 3))
        draw_img(c, T(('ch', n), f'{n} चक्कर', 84, fill=(255, 240, 200, 255), stroke=(90, 40, 0, 255), sw=8), 860, 470, a)
    else:
        draw_img(c, T('ct', 'एक प्रतियोगिता', 92, fill=(255, 244, 220, 255), stroke=(60, 40, 120, 255), sw=9), W / 2, 230, ease((t - .2) / .3))

def s_kartik(c, t, Tt, L):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C('#F6A96B'), C('#FFE3B8')]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    k = t / Tt
    for i in range(6):
        cx = (900 - (t * 420 + i * 260)) % 1500 - 200
        cloud(c, cx, 400 + i * 160, 1.1 + (i % 2) * .4)
    for i in range(10):
        y = 500 + i * 70; x0 = (W - (t * 1400 + i * 211)) % (W + 400) - 200
        c.drawLine(x0, y, x0 + 160, y, P(C('#FFFFFF', 120), 5))
    x = lerp(420, 700, ease(k)); y = 880 - 120 * ease(k) + math.sin(t * 3) * 20
    peacock(c, x, y, 0.82, t, 1.0, rider=True, rider_mood='happy')
    a = ease((t - .2) / .3)
    draw_img(c, T('kt', 'कार्तिकेय जी', 104, fill=(255, 244, 220, 255), stroke=(140, 30, 30, 255), sw=10), W / 2, 190, a)
    if after(L, 0, t, (L[0][1] - L[0][0]) * .45):
        draw_img(c, T('mor', 'मोर पर सवार!', 76, fill=(200, 240, 255, 255), stroke=(10, 60, 120, 255), sw=8), W / 2, 310, ease((t - L[0][0] - (L[0][1] - L[0][0]) * .45) / .3))

def s_mouse(c, t, Tt, L):
    if not after(L, 1, t, -.05):
        kailash(c, t)
        ganesh(c, 400, GROUND, 0.62, t, look=(1, 1))
        mushak(c, 820, GROUND, 1.0, t, facing=-1, look_up=0.6)
        if after(L, 0, t, (L[0][1] - L[0][0]) * .55):
            draw_img(c, T('mu', 'एक छोटा सा मूषक', 88, fill=(255, 244, 220, 255), stroke=(80, 40, 20, 255), sw=9), W / 2, 230, ease((t - L[0][0] - (L[0][1] - L[0][0]) * .55) / .3))
    else:
        u = t - L[1][0]
        c.drawRect(skia.Rect(0, 0, W, H), P(C('#5B2A86')))
        cosmos(c, t)
        globe(c, 540, 820, 300, t)
        orbit(c, 540, 820, 400, 400, 0, col='#FFFFFF', w=5)
        th = math.pi * 1.1 + u * 0.05
        mushak(c, 540 + 400 * math.cos(th), 820 + 400 * math.sin(th) + 20, 0.28, t, facing=-1, walk=1)
        draw_img(c, T('bars', 'बरसों लग जाते!', 96, fill=(255, 230, 170, 255), stroke=(80, 30, 0, 255), sw=9), W / 2, 230, ease(u / .3))

def s_think(c, t, Tt, L):
    kailash(c, t)
    calm = after(L, 1, t)
    a = ease((t - L[1][0]) / 1.0) if calm else 0
    if a > 0: light_rays(c, 540, 880, t, a * .8, col='#FFE7A8')
    ganesh(c, 540, 1950, 1.12, t, eyes='closed' if calm else 'open', aura=0.2 + 0.8 * a)
    if calm:
        for i in range(8):
            ang = i * math.pi / 4 + t * 1.5
            _sp(c, 540 + math.cos(ang) * 380, 880 + math.sin(ang) * 300, 18, a * (0.5 + 0.5 * math.sin(t * 7 + i)), '#FFF59D')
        draw_img(c, T('shant', 'शांत मन से सोचा…', 88, fill=(255, 250, 230, 255), stroke=(110, 60, 0, 255), sw=9), W / 2, 210, a)
    else:
        draw_img(c, T('gh', 'घबराए नहीं', 96, fill=(255, 250, 230, 255), stroke=(110, 60, 0, 255), sw=9), W / 2, 210, ease((t - L[0][0] - .3) / .3))

def s_circle(c, t, Tt, L):
    kailash(c, t)
    st = L[0][0] + (L[0][1] - L[0][0]) * 0.3; en = Tt - 0.25
    pr = clamp((t - st) / (en - st))
    orbit(c, 540, 1300, 400, 85, pr * 3 % 1.0 if pr < 1 else 1, col='#FFD54F', w=8)
    ganesh_orbit(c, 540, 1300, 0.5, 0.34, 400, 85, pr * 3 * 2 * math.pi, t, lambda: parents(c, 540, 1300, 0.5, t))
    mushak(c, 90, GROUND, 0.5, t, facing=1)
    if pr > 0:
        n = min(3, 1 + int(pr * 3))
        draw_img(c, T(('cc', n), f'चक्कर {n}', 110, fill=(255, 240, 200, 255), stroke=(120, 50, 0, 255), sw=10), W / 2, 210, ease((t - st) / .3))
    else:
        draw_img(c, T('hj', 'हाथ जोड़कर…', 92, fill=(255, 240, 200, 255), stroke=(120, 50, 0, 255), sw=9), W / 2, 210, ease((t - .2) / .3))

def s_reveal(c, t, Tt, L):
    kailash(c, t)
    win = after(L, 2, t)
    w = ease((t - L[2][0] - .3) / .6) if win else 0
    if after(L, 1, t): light_rays(c, 640, 900, t, 0.4 + 0.4 * w, col='#FFE7A8')
    land = ease(t / 0.9)
    peacock(c, 230, lerp(800, 1180, land), 0.45, t, 1 - land, rider=True, rider_mood='shocked' if not after(L, 1, t) else 'happy')
    parents(c, 640, GROUND, 0.5, t, smile=True)
    ganesh(c, 960, GROUND, 0.36, t, eyes='happy' if win else 'open', talk=sp(L, 1, t), aura=0.3 + 0.7 * w, look=(-1, 0))
    mushak(c, 1010, GROUND + 2, 0.35, t, facing=-1)
    if not after(L, 1, t, -.05):
        draw_img(c, T('pa', 'गणेश जी पहले से यहाँ!', 80, fill=(255, 244, 220, 255), stroke=(90, 40, 0, 255), sw=9), W / 2, 220, ease((t - L[0][0] - .5) / .3))
    elif not win:
        a = ease((t - L[1][0] - .3) / .3)
        orbit(c, 640, 1300, 300, 70, 1, col='#FFD54F', w=7, a=a)
        draw_img(c, T('ms', 'माता-पिता = पूरा संसार', 82, fill=(255, 244, 220, 255), stroke=(150, 30, 30, 255), sw=9), W / 2, 220, a)
        globe(c, 640, 400, 70, t, a)
    else:
        petals(c, t, w)
        draw_img(c, T('vj', 'विजेता!', 160, fill=(255, 224, 100, 255), stroke=(140, 40, 0, 255), sw=12), W / 2, 230, w, 0.7 + 0.3 * w)

def s_lesson(c, t, Tt, L):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C('#F7B267'), C('#FFF1D6')]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#FFF8EC', 240)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#C2571A'), 7))
    draw_img(c, T('seekh', 'सीख', 130, fill=(190, 80, 20, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 350, ease((t - L[0][0] + .2) / .4))
    ys = [680, 1000]
    for i in range(1, len(L)):
        a = ease((t - L[i][0] + .15) / .4)
        if a <= 0: continue
        img = T(('ls', i), L[i][2], 64, maxw=820, fill=(60, 35, 20, 255), stroke=(0, 0, 0, 0), sw=0)
        draw_img(c, img, W / 2, ys[i - 1] + (1 - a) * 20, a)
    ganesh(c, W / 2, 2210, 0.52, t, eyes='happy', aura=0.3)

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
    kailash(c, t)
    ganesh(c, 540, 1340, 0.42, t, eyes='happy', aura=0.6)
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

FN = dict(hook=s_hook, contest=s_contest, kartik=s_kartik, mouse=s_mouse, think=s_think, circle=s_circle, reveal=s_reveal, lesson=s_lesson, outro=s_outro)

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
