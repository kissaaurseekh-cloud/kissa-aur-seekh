import os as _os, sys as _sys
_ENGINE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'engine')
_sys.path.insert(0, _ENGINE)
import skia, numpy as np, json, math, subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
from mart import sparkle as _sp
from sart import *
from script import SCENES

FPS = 30
DUR = json.load(open('vo/durs.json'))
FB = _os.path.join(_ENGINE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')

def build_timeline():
    tl = []
    for sid, lines in SCENES:
        lead = {'hook': 0.35, 'lesson': 0.2}.get(sid, 0.12)
        gap = {'lesson': 0.3, 'key': 0.2, 'regret': 0.2}.get(sid, 0.1)
        tail = {'outro': 0.9, 'lesson': 0.5, 'drink': 1.3, 'parvati': 0.4, 'blue': 0.8, 'poison': 0.4, 'think': 0.5}.get(sid, 0.2)
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





SY = 1250   # shore line

def shore(c, green=0.0):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, SY), skia.Point(0, H)], [C(blend('#6D5A4A', '#3E4A30', green)), C(blend('#3E3128', '#1E2616', green))]))
    c.drawRect(skia.Rect(0, SY, W, H), p)
    rnd = random.Random(4)
    for i in range(18):
        x = rnd.uniform(0, W); y = rnd.uniform(SY + 10, SY + 80)
        c.drawOval(skia.Rect(x - 40, y - 14, x + 40, y + 14), P(C('#00000', 40) if False else C('#2A211B', 70)))

def runner(c, kind, x, gy, s, t, mood, facing, arm='down', look=(0, 0), bob=True):
    y = gy - (abs(math.sin(t * 9 + x)) * 18 if bob else 0)
    (deva if kind == 'd' else asura)(c, x, y, s, mood, t, arm, facing, look)

def s_hook(c, t, Tt, L):
    cosmos(c, t, green=0.35)
    ocean(c, 1000, t, green=0.5, churn=0.6)
    poison_cloud(c, 540, 640, 340 + 15 * math.sin(t * 2), t)
    shore(c, 0.3)
    shiv_sil(c, 540, 1340, 0.52, t, a=ease(t / 0.6))
    run = clamp(t / Tt)
    for i, x0 in enumerate((260, 140)):
        runner(c, 'd', x0 - run * 260, 1340, 0.3, t + i, 'shocked', -1, look=(1, -1))
    for i, x0 in enumerate((820, 950)):
        runner(c, 'a', x0 + run * 260, 1340, 0.3, t + i, 'shocked', 1, look=(-1, -1))
    title = T('title', 'कौन पिएगा ज़हर?', 104, fill=(255, 244, 220, 255), stroke=(40, 10, 60, 255), sw=10)
    k = ease(t / .5); draw_img(c, title, W / 2, 180, k, 0.85 + .15 * k)
    if after(L, 1, t, .6):
        q = T('q', '?', 200, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
        draw_img(c, q, W / 2, 340 + math.sin(t * 4) * 10, ease((t - L[1][0] - .6) / .3))

def s_manthan(c, t, Tt, L):
    cosmos(c, t)
    ocean(c, 980, t, churn=1)
    pull = t * 3
    mandara(c, 540, 1180, 760, t, spin=t * .6)
    shore(c)
    vasuki(c, 540, 1180, 760, t, pull, lend=(150, 1150), rend=(930, 1150))
    for i, x in enumerate((70, 190, 310)):
        dx = math.sin(pull + i) * 14
        deva(c, x - dx, 1340, 0.34, 'neutral', t + i, 'point', 1, (1, 0))
    for i, x in enumerate((1010, 890, 770)):
        dx = math.sin(pull + i + math.pi) * 14
        asura(c, x + dx, 1340, 0.34, 'neutral', t + i, 'point', -1, (-1, 0))
    if t < 2.6:
        draw_img(c, T('sm', 'समुद्र मंथन', 110, fill=(255, 236, 170, 255), stroke=(60, 20, 80, 255), sw=9), W / 2, 200, ease(t / .3) * clamp((2.6 - t) / .3))
    else:
        draw_img(c, T('am', 'अमृत की खोज…', 90, fill=(255, 236, 170, 255), stroke=(60, 20, 80, 255), sw=8), W / 2, 200, ease((t - 2.6) / .3))

def s_poison(c, t, Tt, L):
    g = ease(t / Tt)
    cosmos(c, t, green=g)
    ocean(c, 980, t, green=0.4 + 0.6 * g, churn=1)
    mandara(c, 540, 1180, 760, t, spin=t * .2)
    rise = ease(t / 1.4)
    r = lerp(60, 330, rise) + (90 * ease((t - L[1][0]) / 1.5) if after(L, 1, t) else 0)
    poison_cloud(c, 540, lerp(1050, 560, rise), r, t)
    shore(c, g)
    if after(L, 0, t, .5):
        a = ease((t - L[0][0] - .5) / .25)
        draw_img(c, T('hal', 'हलाहल!', 140, fill=(200, 255, 120, 255), stroke=(20, 50, 10, 255), sw=11), W / 2, 200 + math.sin(t * 20) * 4 * a, a)
    if after(L, 1, t):
        rnd = random.Random(int(t * 10))
        for i in range(12):
            x = rnd.uniform(40, W - 40); y = rnd.uniform(1000, 1240)
            c.drawCircle(x, y, rnd.uniform(6, 14), P(C('#FF7043', 180)))
        c.drawRect(skia.Rect(0, 0, W, H), P(C('#1B5E20', int(60 * ease((t - L[1][0]) / 1.0)))))

def s_fear(c, t, Tt, L):
    cosmos(c, t, green=1)
    ocean(c, 980, t, green=1, churn=1)
    poison_cloud(c, 540, 560, 420, t)
    shore(c, 1)
    up = after(L, 1, t)
    k = ease(t / 1.0)
    look = (0, -1) if up else None
    for i, x0 in enumerate((330, 170)):
        runner(c, 'd', x0 - k * 90, 1360, 0.36, t + i, 'shocked', -1 if not up else 1, look=look or (1, 0), bob=not up)
    for i, x0 in enumerate((750, 910)):
        runner(c, 'a', x0 + k * 90, 1360, 0.36, t + i, 'shocked', 1 if not up else -1, look=look or (-1, 0), bob=not up)
    if up:
        a = ease((t - L[1][0] - (L[1][1] - L[1][0]) * .55) / .3)
        light_rays(c, 540, -80, t, a)
        draw_img(c, T('mah', 'महादेव!', 150, fill=(255, 245, 200, 255), stroke=(30, 60, 140, 255), sw=11), W / 2, 230, a, 0.8 + 0.2 * a)

def s_drink(c, t, Tt, L):
    cosmos(c, t, green=0.8)
    ocean(c, 1100, t, green=0.8)
    st = L[1][0]; dur = L[1][1] - st
    p1 = clamp((t - st) / (dur * .45)); p2 = clamp((t - st - dur * .45) / (dur * .3))
    cr = 300 * (1 - p1) if after(L, 1, t) else 300
    cx, cy = 820, 420
    poison_cloud(c, cx, cy, cr, t, 1 if cr > 5 else 0)
    hands = 'rest' if not after(L, 1, t) else ('cup' if p2 <= 0 else 'drink')
    shiv(c, 540, 1850, 0.95, t, hands=hands, cup=p1, throat_green=p2, aura=0.5, smile=hands == 'rest')
    if after(L, 1, t) and p2 <= 0:
        # stream from cloud into the bowl
        bx, by = 540, 1850 - 560 * 0.95
        for i in range(18):
            f = (i / 18 + t * 1.5) % 1
            x = lerp(cx, bx, f); y = lerp(cy, by, f) - math.sin(f * math.pi) * 160
            c.drawCircle(x, y, 18 - 8 * f, P(C('#76FF03', 200)))
    if not after(L, 1, t):
        draw_img(c, T('nk', 'न कोई सवाल, न कोई शर्त', 76, fill=(255, 255, 255, 255), stroke=(20, 30, 80, 255), sw=8), W / 2, 220, ease((t - L[0][0] - .3) / .3))

def s_parvati(c, t, Tt, L):
    cosmos(c, t, green=0.3)
    ocean(c, 1100, t, green=0.3)
    s = 0.9; gx, gy = 650, 1880
    tx, ty = gx, gy - 765 * s
    k = ease((t - .4) / .8)
    shiv(c, gx, gy, s, t, hands='down', throat_green=1 - 0.3 * k, aura=0.4, smile=False)
    hx = lerp(gx - 260, tx - 30, k); hy = lerp(gy - 450, ty, k)
    parvati(c, 270, gy, s, t, 'sad' if k < 1 else 'neutral', reach=(hx, hy))
    if k >= 1:
        for i in range(6):
            ang = i * math.pi / 3 + t * 2
            _sp(c, tx + math.cos(ang) * 90, ty + math.sin(ang) * 60, 16, 0.5 + 0.5 * math.sin(t * 8 + i), '#FFF59D')
    draw_img(c, T('mp', 'माता पार्वती', 100, fill=(255, 230, 230, 255), stroke=(120, 20, 30, 255), sw=9), W / 2, 220, ease(t / .3))

def s_blue(c, t, Tt, L):
    cosmos(c, t, green=0.0)
    b = ease((t - L[0][0] - 0.6) / ((L[0][1] - L[0][0]) * .8))
    light_rays(c, 540, 760, t, 0.3 + 0.7 * (1 if after(L, 1, t) else 0), col='#BBDEFB')
    shiv(c, 540, 2230, 1.6, t, hands='down', throat=b, throat_green=1 - b, aura=0.4 + 0.6 * b, smile=b > .9)
    if after(L, 1, t):
        a = ease((t - L[1][0] - 0.9) / .35)
        draw_img(c, T('nkt', 'नीलकंठ', 170, fill=(255, 224, 120, 255), stroke=(20, 50, 140, 255), sw=12), W / 2, 210, a, 0.7 + 0.3 * a)
        for i in range(10):
            _sp(c, 120 + i * 95, 340 + 40 * math.sin(i * 1.7 + t * 3), 18, a * (0.5 + 0.5 * math.sin(t * 7 + i)), '#FFF59D')

def s_think(c, t, Tt, L):
    c.drawRect(skia.Rect(0, 0, W / 2, H), P(C('#F6C76B')))
    c.drawRect(skia.Rect(W / 2, 0, W, H), P(C('#1F3A22')))
    c.drawLine(W / 2, 0, W / 2, H, P(C('#FFFFFF', 120), 6))
    amrit_kalash(c, 270, 900, 1.0, t)
    visha_bowl(c, 810, 900, 1.0, t)
    draw_img(c, T('amr', 'अमृत', 110, fill=(140, 60, 0, 255), stroke=(255, 240, 200, 255), sw=6), 270, 260, ease(t / .3))
    draw_img(c, T('vis', 'विष', 110, fill=(190, 255, 140, 255), stroke=(10, 40, 10, 255), sw=6), 810, 260, ease(t / .3))
    # crowd around amrit
    for i, (x, kind) in enumerate([(90, 'd'), (200, 'a'), (340, 'd'), (450, 'a')]):
        runner(c, kind, x, 1330, 0.26, t + i, 'happy', 1 if x < 270 else -1, arm='point', look=(1 if x < 270 else -1, -1), bob=True)
    if after(L, 1, t):
        a = ease((t - L[1][0]) / .4)
        draw_img(c, T('q2', '?', 180, fill=(255, 214, 64, 255), stroke=(60, 30, 0, 255), sw=9), 810, 600 + math.sin(t * 4) * 8, a)
        g = ease((t - L[1][0] - (L[1][1] - L[1][0]) * .6) / .5)
        if g > 0: shiv_sil(c, 810, 1330, 0.3, t, a=g, glow='#64B5F6')

def s_lesson(c, t, Tt, L):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C('#7FA8E0'), C('#E3F0FF')]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#FFF8EC', 240)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(70, 220, 1010, 1300), 46, 46), P(C('#2F5FB3'), 7))
    draw_img(c, T('seekh', 'सीख', 130, fill=(40, 80, 170, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 350, ease((t - L[0][0] + .2) / .4))
    ys = [680, 1000]
    for i in range(1, len(L)):
        a = ease((t - L[i][0] + .15) / .4)
        if a <= 0: continue
        img = T(('ls', i), L[i][2], 64, maxw=820, fill=(40, 40, 70, 255), stroke=(0, 0, 0, 0), sw=0)
        draw_img(c, img, W / 2, ys[i - 1] + (1 - a) * 20, a)
    shiv(c, W / 2, 2170, 0.48, t, throat=1, smile=True, aura=0.3)

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
    shiv(c, 540, 1600, 0.52, t, smile=True, aura=0.6)
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

FN = dict(hook=s_hook, manthan=s_manthan, poison=s_poison, fear=s_fear, drink=s_drink, parvati=s_parvati, blue=s_blue, think=s_think, lesson=s_lesson, outro=s_outro)

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
