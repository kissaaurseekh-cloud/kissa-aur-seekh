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
        # v2 pacing: voice starts on frame 1, tiny gaps; only the big moments get a breath
        lead = {'hook': 0.0}.get(sid, 0.05)
        gap = {'lesson': 0.15}.get(sid, 0.06)
        tail = {'outro': 0.5, 'lesson': 0.35, 'reveal': 0.6, 'lotus': 0.3, 'vishnu': 0.25, 'hook': 0.1}.get(sid, 0.12)
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

def qmarks(c, t, d=0.0):
    q = T('q', '?', 220, fill=(255, 214, 64, 255), stroke=(80, 40, 0, 255), sw=10)
    a = ease((t - d) / .25)
    draw_img(c, q, 930, 760 + math.sin(t * 5) * 12, a, 0.75 + 0.25 * a)
    draw_img(c, q, 140, 520 + math.sin(t * 5 + 1) * 12, a, 0.6 + 0.2 * a)

def hook_scene(c, t):
    """HOOK RULE: the mystery thing fills the screen, bright, moving from frame 1."""
    trikut(c, t, 'dusk')
    light_rays(c, 330, 640, t, 0.9, col='#FFE7A8')
    x, gy, s = 980, 1560, 1.5
    elephant(c, x, gy, s, t, trunk_up=True, look=(-1, -1), blink_off=2.0)   # never blink on frame 1
    tx, ty = trunk_tip(x, gy, s)
    lotus(c, tx, ty - 10, 1.7, glow=0.9 + 0.1 * math.sin(t * 6), t=t)
    water_front(c, 1330, t, 0.55, dark=0.1)

def hook_title(c, t, a=1.0):
    """big question text, fully visible on frame 1 (no fade-in)."""
    draw_img(c, T('h1', 'हाथी कमल से', 120, fill=(255, 255, 255, 255), stroke=(20, 10, 40, 255), sw=12), W / 2, 240, a)
    draw_img(c, T('h2', 'कैसे बचा?', 150, fill=(255, 214, 64, 255), stroke=(110, 30, 0, 255), sw=13), W / 2, 400, a)

def s_hook(c, t, Tt, L):
    hook_scene(c, t)
    hook_title(c, t)
    qmarks(c, t, 0.3)

def s_grab(c, t, Tt, L):
    trikut(c, t, 'day')
    x, gy, s = 600, GROUND, 0.9
    snap = L[0][0] + (L[0][1] - L[0][0]) * 0.4
    rise = ease((t - .05) / max(.1, snap - .05))
    shake = math.sin(t * 40) * 6 if t > snap else 0
    fam_el(c, 960, 1265, 0.42, t)
    elephant(c, x + shake, gy, s, t, pull=0.6 if t > snap else 0, look=(-1, 1) if t > snap else (-1, 0))
    if t <= snap:
        magar(c, 330, lerp(1300, 1185, rise), 1.0, t, open_=min(1, rise * 1.4))
    else:
        magar(c, 330, 1185, 1.0, t, open_=0.05)
        splash_drops(c, 520, 1190, (t - snap) / .9)
    water_front(c, 1195, t, 0.6)
    ripple(c, 470, 1205, (t * .8) % 1)
    a = ease((t - .05) / .2)
    draw_img(c, T('mg', 'मगरमच्छ!', 130, fill=(255, 235, 200, 255), stroke=(160, 20, 20, 255), sw=11), W / 2, 220, a, 0.8 + .2 * a)

def s_fight(c, t, Tt, L):
    trikut(c, t, 'day')
    sink = ease(t / Tt)
    x, gy, s = 600 - 60 * sink, GROUND + 70 * sink, 0.9
    fam_el(c, 990 - 40 * sink, 1262, 0.4, t, blink=.7)
    fam_el(c, 1080, 1290, 0.34, t, blink=1.9)
    elephant(c, x, gy, s, t, pull=1.0, look=(1, 0))
    magar(c, 330 - 60 * sink, 1185, 1.0, t, open_=0.05 + 0.04 * math.sin(t * 9))
    water_front(c, 1195, t, 0.6)
    ripple(c, 460, 1205, (t * 1.2) % 1); ripple(c, 760, 1210, (t * 1.2 + .5) % 1)
    draw_img(c, T('pt', 'पूरी ताक़त!', 110, fill=(255, 240, 200, 255), stroke=(120, 50, 0, 255), sw=10), W / 2, 220, ease(t / .2))

def s_tired(c, t, Tt, L):
    trikut(c, t, 'night')
    x, gy, s = 540, GROUND + 90, 0.9
    u = t / Tt
    fam_el(c, 930 + 420 * u, 1262, 0.4, t, facing=1, walk=1)
    fam_el(c, 1050 + 420 * u, 1290, 0.34, t, facing=1, walk=1)
    elephant(c, x, gy, s, t, sad=1.0, look=(1, 0), ear_speed=0.4)
    magar(c, 270, 1185, 1.0, t, open_=0.05)
    water_front(c, 1195, t, 0.62, dark=0.45)
    draw_img(c, T('ak', 'अकेला…', 120, fill=(220, 230, 255, 255), stroke=(30, 30, 80, 255), sw=10), W / 2, 220, ease(t / .2))

def s_lotus(c, t, Tt, L):
    trikut(c, t, 'night')
    d0 = L[0][1] - L[0][0]
    up = after(L, 0, t, d0 * 0.3)
    call = after(L, 0, t, d0 * 0.68)
    g = ease((t - L[0][0] - d0 * 0.68) / .4) if call else 0
    light_rays(c, 150, 600, t, 0.25 + 0.6 * g, col='#FFE7A8')
    x, gy, s = 650, GROUND + 60, 0.95
    elephant(c, x, gy, s, t, sad=0.0 if up else 0.5, trunk_up=up, look=(-1, -1))
    magar(c, 330, 1185, 1.0, t, open_=0.05)
    if up:
        tx, ty = trunk_tip(x, gy, s)
        lotus(c, tx, ty - 10, 1.0, glow=0.5 + 0.5 * g, t=t)
    else:
        lotus(c, 260, 1185, 0.9, glow=0.6, t=t)
    water_front(c, 1195, t, 0.62, dark=0.4)
    if call:
        draw_img(c, T('hn', 'हे नारायण!', 140, fill=(255, 224, 100, 255), stroke=(140, 40, 0, 255), sw=12), W / 2, 230, g, 0.7 + 0.3 * g)
    else:
        draw_img(c, T('kt', 'एक कमल…', 110, fill=(255, 220, 235, 255), stroke=(140, 20, 80, 255), sw=10), W / 2, 220, ease(t / .2))

def s_vishnu(c, t, Tt, L):
    trikut(c, t, 'divine')
    light_rays(c, 540, 700, t, 0.8, col='#FFFFFF')
    k = ease(t / 1.1)
    vishnu_garuda(c, lerp(980, 540, k), lerp(260, 1000, k), lerp(0.3, 0.6, k), t, 1.0, aura=0.6)
    for i in range(10):
        ang = i * math.pi / 5 + t
        sparkle(c, 540 + math.cos(ang) * 420, 760 + math.sin(ang) * 380, 18, 0.5 + 0.5 * math.sin(t * 6 + i))
    draw_img(c, T('bv', 'भगवान विष्णु', 110, fill=(255, 248, 220, 255), stroke=(30, 50, 140, 255), sw=10), W / 2, 170, ease(t / .2))

def s_reveal(c, t, Tt, L):
    d0 = L[0][1] - L[0][0]
    launch = L[0][0] + d0 * 0.1; hit = launch + 0.6
    free = ease((t - hit - .1) / .6) if t > hit else 0
    up = t > hit + 0.9
    trikut(c, t, 'night' if t < hit else 'divine')
    if t >= hit: light_rays(c, 300, 600, t, 0.5, col='#FFF3B0')
    vx, vy, vs = 300, 690, 0.42
    flying = launch <= t < hit
    vishnu_garuda(c, vx, vy + math.sin(t * 2) * 8, vs, t, 0.6, aura=0.5, chakra_on=not flying, bless=up)
    x, gy, s = 700, GROUND + 40 - 40 * free, 0.82
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
    if hit <= t < hit + .3:
        c.drawRect(skia.Rect(0, 0, W, H), P(C('#FFFFFF', int(200 * (1 - (t - hit) / .3)))))
    if t < hit:
        draw_img(c, T('sc', 'सुदर्शन चक्र', 110, fill=(255, 230, 150, 255), stroke=(140, 50, 0, 255), sw=10), W / 2, 200, ease(t / .2))
    else:
        petals(c, t, free)
        draw_img(c, T('mk', 'मुक्त!', 150, fill=(255, 244, 200, 255), stroke=(30, 110, 40, 255), sw=12), W / 2, 200, free, 0.7 + .3 * free)

def s_lesson(c, t, Tt, L):
    """one-line seekh over a calm deity frame (no long text card)."""
    trikut(c, t, 'divine')
    light_rays(c, 540, 900, t, 0.5, col='#FFFFFF')
    vishnu(c, 540, 1330, 0.62, t, aura=0.7, bless=True)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 70, 1020, 560), 40, 40), P(C('#FFF8EC', 235)))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(60, 70, 1020, 560), 40, 40), P(C('#1E5BD8'), 6))
    draw_img(c, T('seekh', 'सीख', 100, fill=(30, 80, 190, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 160, 1)
    if len(L) > 1:
        a = ease((t - L[1][0] + .15) / .25)
        draw_img(c, T(('ls', 1), L[1][2], 62, maxw=860, fill=(40, 30, 60, 255), stroke=(0, 0, 0, 0), sw=0), W / 2, 380, a)

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

FN = dict(hook=s_hook, grab=s_grab, fight=s_fight, tired=s_tired, lotus=s_lotus, vishnu=s_vishnu, reveal=s_reveal, lesson=s_lesson, outro=s_outro)

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
