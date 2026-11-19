import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from hart import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'key': 0.2, 'regret': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'lesson': 0.5, 'realize': 0.4, 'baby': 0.35}.get(sid, 0.2)
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


TR = '#C9A0A0'
def flashback_tint(c, k):
    if k <= 0: return
    c.drawRect(skia.Rect(0, 0, W, H), P(C('#704214', int(55 * k))))
    g = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(skia.Point(W / 2, 800), 1100, [C('#000000', 0), C('#000000', int(110 * k))]))
    c.drawRect(skia.Rect(0, 0, W, H), g)

def s_hook(c, t, Tt, L):
    sky(c, 'dusk'); street(c, 0.4)
    z = lerp(1.0, 1.25, ease(t / Tt))
    c.save(); zoom(c, 560, 900, z)
    a = elephant(c, 500, GY + 60, 0.95, t, look=(1, .3))
    pb = peg(c, 900, GY + 60)
    rope(c, a, pb, 0.5, glow=0.6 + 0.4 * math.sin(t * 5))
    c.restore()
    title = T('title', 'हाथी और रस्सी', 130, fill=(255, 244, 220, 255), stroke=(90, 40, 20, 255), sw=10)
    k = ease(t / .5); draw_img(c, title, W / 2, 190, k, 0.85 + .15 * k)
    if after(L, 1, t, .3):
        q = T('q', '?', 220, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
        draw_img(c, q, W / 2, 400 + math.sin(t * 4) * 12, ease((t - L[1][0] - .3) / .3), 0.9 + .1 * math.sin(t * 6))

def s_mela(c, t, Tt, L):
    mela_bg(c, t)
    for i, (ex, s) in enumerate([(250, .5), (620, .55)]):
        a = elephant(c, ex, GY + 40, s, t + i, blink_off=i, look=(-1, 0))
        rope(c, a, peg(c, ex + 200, GY + 40, .7), .4, 5)
    mx = lerp(-150, 170, ease(t / 1.6))
    walk = math.sin(t * 9) * 6 if t < 1.6 else 0
    man(c, mx, GY + 200 + walk, 0.75, 'neutral' if not after(L, 1, t) else 'shocked', False, t, look=(1, 0))
    if after(L, 1, t, 1.6):
        k = ease((t - L[1][0] - 1.6) / .4)
        c.drawCircle(820, GY + 10, 90 * k, P(C('#FFEB3B', 230), 7))

def s_ask(c, t, Tt, L):
    mela_bg(c, t)
    a = elephant(c, 560, GY + 10, 0.62, t, look=(1, 0))
    rope(c, a, peg(c, 820, GY + 10, .8), .4)
    man(c, 230, GY + 230, 0.85, 'neutral', False, t, look=(1, 0), arm='point' if sp(L, 1, t) else 'down')
    man(c, 860, GY + 230, 0.85, 'neutral', False, t, look=(-1, 0), old=0.6, kurta='#E8D8B8', pants='#F3EFE4', turban='#C62828', staff=True, facing=-1)
    if after(L, 1, t):
        a_ = clamp((t - L[1][0]) / .25)
        bubble(c, 300, 330, 140, 110, a_, tail=(-1, 1))
        draw_img(c, T('qq', '?', 150, fill=(30, 90, 200, 255), stroke=(0, 0, 0, 0), sw=0), 300, 330, a_)

def s_answer(c, t, Tt, L):
    mela_bg(c, t)
    a = elephant(c, 560, GY + 10, 0.62, t, look=(1, 0))
    rope(c, a, peg(c, 820, GY + 10, .8), .4)
    man(c, 230, GY + 230, 0.85, 'neutral', False, t, look=(1, 0))
    man(c, 860, GY + 230, 0.85, 'happy', sp(L, 1, t), t, look=(-1, 0), old=0.6, kurta='#E8D8B8', pants='#F3EFE4', turban='#C62828', staff=True, facing=-1)
    if after(L, 1, t, .4):
        k = ease((t - L[1][0] - .4) / .5)
        c.save(); c.translate(W / 2, 470); c.scale(k, k)
        bubble(c, 0, 0, 260, 190, 1, tail=(1, 1))
        elephant(c, 30, 120, 0.33, t, tint=TR)
        c.restore()

def s_baby(c, t, Tt, L):
    sky(c, 'warm'); street(c, 0.2)
    gave = after(L, 1, t, .2)
    pull = 0.0 if gave else clamp((t - .3) / .3)
    a = elephant(c, 500, GY + 80, 0.6, t, pull=pull, sad=ease((t - L[1][0] - .2) / .6) if gave else 0, sit=ease((t - L[1][0] - .2) / .6) if gave else 0,
                 look=(1, 0) if not gave else (0, 1), ear_speed=3 if pull else 1)
    pb = peg(c, 860, GY + 80)
    rope(c, a, pb, 0.0 if pull > .2 else 0.6)
    if pull > .2:
        for i in range(3):
            c.drawLine(pb[0] + 26, pb[1] - 30 + i * 22, pb[0] + 56 + 10 * math.sin(t * 30 + i), pb[1] - 30 + i * 22, P(C('#FFFFFF', 180), 4))
    flashback_tint(c, 1)
    badge = T('past', 'कई साल पहले…', 70, fill=(255, 240, 210, 255), stroke=(60, 30, 10, 255), sw=6)
    draw_img(c, badge, W / 2, 230, ease(t / .4))

def s_now(c, t, Tt, L):
    mela_bg(c, t)
    a = elephant(c, 470, GY + 60, 0.85, t, look=(1, .5) if (t % 3) < 1.2 else (-1, 0))
    rope(c, a, peg(c, 900, GY + 60), .5)
    man(c, 880, GY + 250, 0.7, 'neutral', sp(L, 0, t), t, look=(-1, 0), old=0.6, kurta='#E8D8B8', pants='#F3EFE4', turban='#C62828', staff=True, facing=-1)
    draw_img(c, T('now', 'आज', 90, fill=(255, 255, 255, 255), stroke=(40, 80, 130, 255), sw=8), W / 2, 230, ease(t / .3))

def s_realize(c, t, Tt, L):
    mela_bg(c, t, 0.15)
    a = elephant(c, 560, GY + 30, 0.7, t, look=(1, 0))
    pb = peg(c, 900, GY + 30, .8)
    g = ease((t - L[1][0] - .6) / .5) if after(L, 1, t) else 0
    rope(c, a, pb, .4, glow=g)
    man(c, 190, GY + 240, 0.8, 'neutral', False, t, look=(1, -0.5), arm='chin')
    if g > 0:
        hx, hy = 560 - 230 * .7, GY + 30 - 400 * .7
        bubble(c, 640, 330, 300, 170, g, tail=(-1, 1))
        br = T('mind', 'सोच की रस्सी', 76, fill=(120, 60, 10, 255), stroke=(0, 0, 0, 0), sw=0)
        draw_img(c, br, 640, 330, g)
        p = skia.Path(); p.moveTo(hx, hy - 60); p.quadTo(hx + 150, hy - 250, 560, 470)
        c.drawPath(p, P(C('#FFD54F', int(200 * g)), 14))
        c.drawPath(p, P(C('#C8A26A', int(255 * g)), 6))

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
    elephant(c, W / 2 + 40, 1820, 0.5, t)

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
    mela_bg(c, t)
    elephant(c, W / 2 + 60, GY + 40, 0.55, t)
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

FN = dict(hook=s_hook, mela=s_mela, ask=s_ask, answer=s_answer, baby=s_baby, now=s_now, realize=s_realize, lesson=s_lesson, outro=s_outro)

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
