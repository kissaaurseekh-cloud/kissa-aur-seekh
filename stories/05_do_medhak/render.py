import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from mart import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'key': 0.2, 'regret': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'lesson': 0.5, 'sink': 0.7, 'night': 0.8, 'butter': 0.7, 'fall': 0.5}.get(sid, 0.2)
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




F2 = '#7CB342'   # second (brave) frog colour
CX, TOP, PW, PH = 540, 520, 900, 760
MY = 720

def potscene(c, t, morning=0.0, moon_f=0.3, frogs=(), churn=0.0, butter=0.0, my=MY):
    room(c, t, morning, moon_f)
    inner = big_pot(c, CX, TOP, PW, PH, my)
    for f in frogs: f()
    milk(c, inner, my, t, churn, butter)

def s_hook(c, t, Tt, L):
    potscene(c, t, frogs=[lambda: frog(c, 390, MY - 40, 0.75, 'sad', t=t, kick=.5), lambda: frog(c, 690, MY - 40, 0.75, 'happy', t=t, kick=1, col=F2, look=(-1, 0))])
    title = T('title', 'दो मेंढक', 150, fill=(255, 244, 220, 255), stroke=(30, 80, 30, 255), sw=10)
    k = ease(t / .5); draw_img(c, title, W / 2, 190, k, 0.85 + .15 * k)
    if after(L, 1, t, .5):
        q = T('q', '?', 200, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
        draw_img(c, q, W / 2, 380 + math.sin(t * 4) * 10, ease((t - L[1][0] - .5) / .3))

def s_fall(c, t, Tt, L):
    room(c, t)
    c.drawRect(skia.Rect(0, 780, 420, 810), P(C('#6B4226')))          # shelf
    inner = big_pot(c, 700, 860, 620, 420, 960)
    jump = L[1][0] + 0.5
    for i, (col, x0) in enumerate([('#5CB85C', 120), (F2, 300)]):
        if t < jump + i * .15:
            hop = abs(math.sin(t * 4 + i)) * 60
            frog(c, x0, 700 - hop, 0.5, 'happy', t=t, col=col, look=(1, 0))
        else:
            f = clamp((t - jump - i * .15) / .7)
            if f < 1:
                x = lerp(x0, 640 + i * 120, f); y = lerp(700, 980, f) - math.sin(f * math.pi) * 260
                frog(c, x, y, 0.5, 'shocked', t=t, col=col, rot=f * 200, legs_out=1)
            else:
                frog(c, 640 + i * 120, 975, 0.5, 'shocked', t=t, col=col, kick=1)
    milk(c, inner, 980, t)
    for i in range(2): splash(c, 640 + i * 120, 980, (t - jump - .7 - i * .15) / .6)
    if after(L, 1, t, .5) and t < jump + 1.5:
        draw_img(c, T('chh', 'छपाक!', 110, fill=(255, 255, 255, 255), stroke=(30, 60, 120, 255), sw=9), 700, 640, ease((t - jump - .6) / .2))

def s_swim(c, t, Tt, L):
    slide = 0.0
    if sp(L, 0, t):
        ph = (t * 0.9) % 1; slide = math.sin(ph * math.pi)
    potscene(c, t, frogs=[lambda: frog(c, 330 - slide * 20, MY - 40 - slide * 120, 0.75, 'shocked', t=t, kick=1, look=(-1, -1)),
                          lambda: frog(c, 720, MY - 40, 0.75, 'neutral', t=t, kick=1, col=F2, look=(1, -1))])
    if sp(L, 0, t):
        draw_img(c, T('slip', 'चिकनी दीवार!', 80, fill=(255, 255, 255, 255), stroke=(120, 40, 20, 255), sw=8), W / 2, 330, ease((t - L[0][0]) / .3))
        for i in range(3): c.drawLine(130, 560 + i * 50, 170, 640 + i * 50, P(C('#FFFFFF', 160), 5))

def s_giveup(c, t, Tt, L):
    stop = after(L, 2, t, .4)
    potscene(c, t, frogs=[lambda: frog(c, 360, MY - 40 + (6 if stop else 0), 0.8, 'sad', sp(L, 1, t), t, kick=0 if stop else .4, look=(1, .3), closed=stop),
                          lambda: frog(c, 720, MY - 40, 0.75, 'shocked' if stop else 'neutral', t=t, kick=1, col=F2, look=(-1, 0))])

def s_sink(c, t, Tt, L):
    d = ease(t / (Tt * .85))
    potscene(c, t, frogs=[lambda: frog(c, 360, MY - 40 + d * 330, 0.8, 'sad', t=t, closed=True, rot=d * 20),
                          lambda: frog(c, 720, MY - 40, 0.75, 'sad', t=t, kick=1, col=F2, look=(-1, 1))])
    bubbles(c, 360, MY - 10, t, 1 - d * .5)
    c.drawRect(skia.Rect(0, 0, W, H), P(C('#000020', 60)))

def s_keep(c, t, Tt, L):
    det = after(L, 0, t, 1.6)
    potscene(c, t, frogs=[lambda: frog(c, 540, MY - 40, 0.95, 'sad' if not det else 'happy', sp(L, 1, t), t, kick=0.6 if not det else 1.3, col=F2, det=det, look=(0, -1))])
    if det:
        a = ease((t - L[0][0] - 1.6) / .4)
        for i in range(8):
            ang = i * math.pi / 4 + t * 2
            sparkle(c, 540 + math.cos(ang) * 230, MY - 60 + math.sin(ang) * 150, 26, a * (0.5 + 0.5 * math.sin(t * 8 + i)), '#FFD54F')

def s_night(c, t, Tt, L):
    mf = clamp(t / Tt)
    potscene(c, t * 2, morning=0.0, moon_f=mf, churn=1, butter=0.35 * mf,
             frogs=[lambda: frog(c, 540, MY - 40, 0.9, 'neutral', t=t * 1.3, kick=1.5, col=F2, det=True, look=(0, -1))])
    draw_img(c, T('raat', 'पूरी रात…', 90, fill=(255, 255, 255, 255), stroke=(20, 30, 80, 255), sw=8), W / 2, 200, ease(t / .3))

def s_butter(c, t, Tt, L):
    m = ease(t / 1.2)
    b = lerp(0.4, 1.0, ease(lt(L, 0, t) * 1.2))
    jt = L[1][0] + (L[1][1] - L[1][0]) * .55
    def fr():
        if t < L[1][0]:
            frog(c, 540, MY - 40, 0.9, 'shocked' if b > .8 else 'neutral', t=t, kick=1 - b * .8, col=F2, look=(0, 1))
        elif t < jt:
            frog(c, 540, MY - 70, 0.9, 'happy', t=t, col=F2, look=(1, -1))
        else:
            f = clamp((t - jt) / .7)
            x = lerp(540, 980, f); y = lerp(MY - 70, 1200, f) - math.sin(f * math.pi) * 520
            frog(c, x, y, 0.9, 'happy', t=t, col=F2, rot=f * 20, legs_out=1 - f)
    room(c, t, m)
    inner = big_pot(c, CX, TOP, PW, PH, MY)
    milk(c, inner, MY, t, 0, b)
    fr()
    if b > .85 and t < L[1][0] + .5:
        draw_img(c, T('makh', 'मक्खन!', 110, fill=(255, 236, 140, 255), stroke=(120, 80, 0, 255), sw=9), W / 2, 330, ease((t - L[0][0] - (L[0][1] - L[0][0]) * .6) / .3))
    if t > jt + .7:
        for i in range(6): sparkle(c, 820 + i * 40, 900 + (i % 2) * 60, 22, 0.5 + 0.5 * math.sin(t * 7 + i))

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
    frog(c, W / 2, 1740, 0.75, 'happy', t=t)

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
    room(c, t, morning=1.0)
    frog(c, 540, 1120 - abs(math.sin(t * 3)) * 80, 0.8, 'happy', t=t)
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

FN = dict(hook=s_hook, fall=s_fall, swim=s_swim, giveup=s_giveup, sink=s_sink, keep=s_keep, night=s_night, butter=s_butter, lesson=s_lesson, outro=s_outro)

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
