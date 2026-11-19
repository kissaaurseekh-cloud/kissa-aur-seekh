import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from part import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'key': 0.2, 'regret': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'lesson': 0.5, 'twist': 0.5, 'flowers': 0.3}.get(sid, 0.2)
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
    cx = min(max(cx, W / 2 / z), W - W / 2 / z); cy = min(max(cy, 760 / z), H - (H - 760) / z)
    c.translate(W / 2, 760); c.scale(z, z); c.translate(-cx, -cy)



FEET = 1270
def L_POT(s=0.95): return (540 - 300 * s * 1.1, FEET - 432 * s * 1.1 + 230 * s * 1.1)

def s_hook(c, t, Tt, L):
    village(c, t, 'dusk', dry=0.3)
    fl = ease((t - L[1][0] - 1.0) / 1.0) if after(L, 1, t, 1.0) else 0
    random.seed(5)
    for i in range(16):
        ang = i / 16 * math.pi * 2; rr = 300 + (i % 3) * 50
        flower(c, 540 + math.cos(ang) * rr, 1080 + abs(math.sin(ang)) * 160, 1.3, ['#E91E63', '#FFEB3B', '#AB47BC', '#FF7043'][i % 4], clamp(fl * 1.6 - i / 16 * .6), t)
    pot(c, 540, 860 + math.sin(t * 2) * 8, 2.3, True, 'shocked' if fl > .3 else 'sad', t=t, drip=1, tear=1 if fl < .3 else 0)
    title = T('title', 'टूटा घड़ा', 140, fill=(255, 244, 220, 255), stroke=(110, 40, 20, 255), sw=10)
    k = ease(t / .5); draw_img(c, title, W / 2, 190, k, 0.85 + .15 * k)
    if fl > 0:
        for i in range(6): sparkle(c, 200 + i * 135, 420 + (i % 2) * 60, 24, fl * (0.5 + 0.5 * math.sin(t * 6 + i)))

def s_intro(c, t, Tt, L):
    village(c, t, dry=0.6)
    raghu(c, 540, FEET, 0.95, 'happy', False, t, pots=dict(left=dict(cracked=True), right=dict(mood='happy')))
    if after(L, 1, t, 1.8):
        k = ease((t - L[1][0] - 1.8) / .3); px, py = L_POT()
        c.drawCircle(px + 40, py, 140 * k, P(C('#FFEB3B', 230), 8))

def s_walk(c, t, Tt, L):
    village(c, t, scroll=-t * 0.35, dry=0.6)
    bob = math.sin(t * 8) * 7
    raghu(c, 540, FEET, 0.95, 'neutral', False, t, bob=bob, look=(0, -0.3),
          pots=dict(left=dict(cracked=True, mood='sad', drip=1), right=dict(mood='proud' if after(L, 1, t) else 'happy')))
    if after(L, 1, t, .3):
        px = 540 + 300 * 0.95 * 1.1; py = L_POT()[1]
        for i in range(4): sparkle(c, px - 90 + i * 60, py - 170 - (i % 2) * 30, 18, 0.6 + 0.4 * math.sin(t * 6 + i))

def s_sad(c, t, Tt, L):
    px, py = L_POT()
    c.save(); z = lerp(1.0, 1.7, ease(t / 1.0)); zoom(c, px + 60, py - 40, z)
    village(c, t, 'sad' if after(L, 1, t) else 'day', dry=0.6)
    raghu(c, 540, FEET, 0.95, 'sad' if after(L, 1, t, 1.5) else 'neutral', False, t, look=(-1, 0.3),
          pots=dict(left=dict(cracked=True, mood='sad', talk=sp(L, 1, t), tear=1, look=(1, -0.5)), right=dict(mood='neutral')))
    c.restore()

def s_reply(c, t, Tt, L):
    px, py = L_POT()
    c.save(); z = lerp(1.7, 1.2, ease(t / 0.8)); zoom(c, 400, 760, z)
    village(c, t, dry=0.6)
    raghu(c, 540, FEET, 0.95, 'happy', sp(L, 1, t), t, look=(-1, 0.3),
          pots=dict(left=dict(cracked=True, mood='sad', look=(1, -0.5)), right=dict(mood='neutral')))
    c.restore()
    if after(L, 1, t, .6):
        a = clamp((t - L[1][0] - .6) / .3)
        bubble(c, 540, 300, 300, 130, a, tail=(1, 1))
        draw_img(c, T('look', 'रास्ते के किनारे… 👀'.replace(' 👀', ''), 66, fill=(60, 40, 20, 255), stroke=(0, 0, 0, 0), sw=0), 540, 300, a)

def s_flowers(c, t, Tt, L):
    village(c, t, scroll=-t * 0.3, dry=1.0)
    k = ease(lt(L, 0, t) * 1.15)
    flowers(c, k, t)
    bob = math.sin(t * 8) * 7
    raghu(c, 540, FEET, 0.95, 'happy', False, t, bob=bob, look=(-1, 0.4),
          pots=dict(left=dict(cracked=True, mood='shocked' if k < .9 else 'happy', drip=1, look=(-1, 0.5)), right=dict(mood='neutral', look=(1, 0.5))))
    if after(L, 1, t):
        a = ease((t - L[1][0]) / .3)
        c.drawCircle(860, 1250, 150 * a, P(C('#FF7043', 200), 7))
    for i in range(5): sparkle(c, 90 + (i % 2) * 120, 900 + i * 110, 22, k * (0.5 + 0.5 * math.sin(t * 6 + i)))

def s_twist(c, t, Tt, L):
    village(c, t, 'warm', scroll=-t * 0.2, dry=1.0)
    flowers(c, 1.0, t, 0)
    bob = math.sin(t * 6) * 5
    raghu(c, 540, FEET, 0.95, 'happy', True if (sp(L, 0, t) or sp(L, 1, t)) else False, t, bob=bob, look=(-1, 0.3),
          pots=dict(left=dict(cracked=True, mood='happy', drip=1, tear=0.6 if after(L, 1, t) else 0, look=(1, -0.5)), right=dict(mood='neutral')))
    if sp(L, 0, t) and t > L[0][0] + 1.6:
        for i in range(10):
            ph = (t * 1.2 + i / 10) % 1
            c.drawCircle(60 + (i * 37) % 300, 760 + ph * 700, 9, P(C('#6B4226', int(255 * (1 - ph)))))
    if after(L, 1, t):
        a = ease((t - L[1][0]) / .4)
        for i in range(8): sparkle(c, 70 + (i % 3) * 110, 820 + i * 95, 26, a * (0.5 + 0.5 * math.sin(t * 5 + i)))
        hs = (0.9 + 0.1 * math.sin(t * 5)) * a; c.drawPath(heart(540, 330, 70 * hs), P(C('#E91E63'))); c.drawPath(heart(540, 330, 70 * hs), P(C('#FFFFFF'), 6))

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
    pot(c, W / 2, 1760, 0.9, True, 'happy', t=t)

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
    village(c, t, dry=1.0); flowers(c, 1.0, t, 0)
    pot(c, W / 2, 1150, 1.0, True, 'happy', t=t)
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

FN = dict(hook=s_hook, intro=s_intro, walk=s_walk, sad=s_sad, reply=s_reply, flowers=s_flowers, twist=s_twist, lesson=s_lesson, outro=s_outro)

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
