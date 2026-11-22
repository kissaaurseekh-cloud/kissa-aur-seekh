import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from tart import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'key': 0.2, 'regret': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'lesson': 0.5, 'never': 0.9, 'cut': 0.4, 'dadaji': 0.4}.get(sid, 0.2)
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



COLS = [('#29B6F6', '#81D4FA', '#01579B'), ('#EC407A', '#F8BBD0', '#880E4F'), ('#FFEE58', '#FFF59D', '#F57F17')]
def flyers(c, t, n=3, a=1.0, y0=380):
    for i in range(n):
        x = (t * 160 + i * 380) % (W + 300) - 150; y = y0 + i * 70 + math.sin(t * 2 + i) * 40
        butterfly(c, x, y, 0.4, t + i * .3, cols=COLS[i % 3], rot=15)

def s_hook(c, t, Tt, L):
    garden(c, t, 'dusk', 0.5)
    branch(c, -40, 1080, 900, 1010, 40)
    butterfly(c, 560, 940, 1.6, t, crumpled=1, mood='sad', flap=0.6)
    if after(L, 1, t, .2): flyers(c, t, 3, y0=480)
    title = T('title', 'तितली और कोकून', 120, fill=(255, 244, 220, 255), stroke=(110, 40, 80, 255), sw=10)
    k = ease(t / .5); draw_img(c, title, W / 2, 190, k, 0.85 + .15 * k)
    if after(L, 1, t, .3):
        q = T('q', '?', 220, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
        draw_img(c, q, W / 2, 400 + math.sin(t * 4) * 12, ease((t - L[1][0] - .3) / .3), 0.9 + .1 * math.sin(t * 6))

def s_garden(c, t, Tt, L):
    garden(c, t)
    branch(c, 1120, 640, 640, 720, 30)
    cocoon(c, 760, 860, 0.55, t, wiggle=1 if after(L, 1, t) else 0.2)
    bx = lerp(-120, 300, ease(t / 1.4)); walk = math.sin(t * 9) * 5 if t < 1.4 else 0
    boy(c, bx, GY + 260 + walk, 1.0, 'shocked' if after(L, 0, t, 1.4) else 'neutral', False, t, look=(1, -0.6), arm='point' if after(L, 1, t) else 'down')
    if after(L, 0, t, 1.2):
        k = ease((t - L[0][0] - 1.2) / .3); c.drawCircle(760, 860, 120 * k, P(C('#FFEB3B', 230), 8))

def s_struggle(c, t, Tt, L):
    garden(c, t)
    branch(c, 1200, 420, -100, 470, 46)
    cocoon(c, 540, 820, 1.5, t, wiggle=1, hole=1, peek=0.5 + 0.2 * math.sin(t * 3), strain=1)
    k = ease((t) / .4)
    bubble(c, 230, 340, 130, 120, k); clock(c, 230, 340, 80, t * 3) if False else None
    c.drawCircle(230, 340, 80, P(C('#FFF8E1'))); c.drawCircle(230, 340, 80, P(C('#C9A227'), 6))
    c.drawLine(230, 340, 230 + math.cos(t * 6) * 56, 340 + math.sin(t * 6) * 56, P(C('#333333'), 5))
    c.drawLine(230, 340, 230 + math.cos(t * .5) * 36, 340 + math.sin(t * .5) * 36, P(C('#333333'), 7))
    if after(L, 1, t):
        k = ease((t - L[1][0]) / .4)
        boy(c, lerp(1300, 900, k), GY + 420, 1.3, 'sad', False, t, look=(-1, -0.5), facing=-1)

def s_cut(c, t, Tt, L):
    garden(c, t)
    branch(c, 1200, 420, -100, 470, 46)
    snip = L[0][0] + (L[0][1] - L[0][0]) * .7
    cutk = ease((t - snip) / .3)
    cocoon(c, 540, 820, 1.5, t, wiggle=0.3 if cutk == 0 else 0, hole=1, peek=0.5, cut=cutk)
    if t < snip + .5:
        sx = lerp(1150, 640, ease((t - .2) / 1.0)); op = 0.9 if t < snip else 0.0
        if snip - .25 < t < snip: op = lerp(0.9, 0, (t - snip + .25) / .25)
        scissors(c, sx, 980, 1.4, op, -10)
    if cutk > 0:
        fall = ease((t - snip - .1) / .6)
        butterfly(c, 540, lerp(900, 1110, fall), 0.9, t, crumpled=1, mood='happy' if after(L, 1, t) else 'sad', flap=0.3)
        c.drawRect(skia.Rect(240, 1150, 840, 1175), P(C('#5FBF4A')))
    boy(c, 960, GY + 440, 1.3, 'happy' if after(L, 1, t) else 'neutral', False, t, look=(-1, -0.3), facing=-1)

def s_wait(c, t, Tt, L):
    garden(c, t)
    c.drawOval(skia.Rect(140, 1080, 940, 1200), P(C('#5FBF4A')))
    butterfly(c, 540, 1010, 1.5, t, crumpled=1, mood='sad', flap=0.4)
    if sp(L, 0, t):
        k = ease((t - L[0][0]) / .4)
        c.drawCircle(540, 1000, 230 * k, P(C('#FF7043', 220), 7))
    if after(L, 1, t):
        k = ease((t - L[1][0]) / .4)
        boy(c, lerp(1250, 900, k), GY + 360, 1.2, 'happy', False, t, look=(-1, 0.4), facing=-1)
        bubble(c, 720, 330, 140, 120, k)
        c.drawCircle(720, 330, 80, P(C('#FFF8E1'))); c.drawCircle(720, 330, 80, P(C('#C9A227'), 6))
        c.drawLine(720, 330, 720 + math.cos(t * 6) * 56, 330 + math.sin(t * 6) * 56, P(C('#333333'), 5))

def s_never(c, t, Tt, L):
    garden(c, t, 'sad', 0.25)
    c.drawOval(skia.Rect(140, 1080, 940, 1200), P(C('#4E8F42')))
    hop = abs(math.sin(t * 2.2)) * 60 if t < Tt - .8 else 0
    butterfly(c, 540, 1010 - hop, 1.4, t, crumpled=1, mood='sad', flap=1.0, rot=math.sin(t * 2.2) * 8)
    flyers(c, t, 3, y0=360)

def s_dadaji(c, t, Tt, L):
    garden(c, t)
    dadaji(c, 780, GY + 260, 1.0, 'happy', sp(L, 1, t) or sp(L, 2, t), t, look=(-1, 0.2))
    boy(c, 290, GY + 300, 1.0, 'sad' if after(L, 2, t) else 'neutral', False, t, look=(1, -0.5))
    if after(L, 1, t, .3):
        k = clamp((t - L[1][0] - .3) / .3)
        bubble(c, 540, 330, 330, 210, k, tail=(1, 1))
        if k > .5:
            c.save(); c.clipRect(skia.Rect(220, 130, 860, 530))
            sq = 0.5 + 0.5 * math.sin(t * 6)
            c.drawRect(skia.Rect(500, 220, 580, 440), P(C('#A1B56C')))
            butterfly(c, 540 + sq * 20, 330, 0.55, t, flap=0.2, rot=90 - sq * 10)
            for i in range(3): sparkle(c, 680 + i * 50, 260 + i * 60, 18, 0.5 + 0.5 * math.sin(t * 7 + i))
            c.restore()

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
    butterfly(c, W / 2, 1720, 0.6, t)

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
    garden(c, t)
    [butterfly(c, 540 + math.sin(t * .8 + i * 2) * 330, 1000 + math.cos(t * 1.1 + i) * 90, 0.45, t + i, cols=[('#FF8A00', '#FFB74D', '#6A1B9A'), ('#29B6F6', '#81D4FA', '#01579B'), ('#EC407A', '#F8BBD0', '#880E4F')][i]) for i in range(3)]
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

FN = dict(hook=s_hook, garden=s_garden, struggle=s_struggle, cut=s_cut, wait=s_wait, never=s_never, dadaji=s_dadaji, lesson=s_lesson, outro=s_outro)

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
