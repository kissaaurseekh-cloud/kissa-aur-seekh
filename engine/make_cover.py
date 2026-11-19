import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
_HERE = os.path.dirname(os.path.abspath(__file__))
d, mod, sid, tt, l1, l2, out = sys.argv[1:8]
d = os.path.abspath(d); out = os.path.abspath(out)
os.chdir(d); sys.path.insert(0, d); sys.argv = ['x', 'none']
src = open(mod).read().split("if __name__")[0]
g = {'__file__': os.path.join(d, mod), '__name__': 'cover'}; exec(src, g)
tl = g['build_timeline'](); D = {s: (T_, L) for s, T_, L in tl}
skia = g['skia']; Tt, L = D[sid]
surf = skia.Surface(1080, 1920); c = surf.getCanvas(); g['FN'][sid](c, float(tt), Tt, L)
im = Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)).convert('RGB')
# dark gradient at bottom for text
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for y in range(1050, 1920): od.line([(0, y), (1080, y)], fill=(10, 6, 2, int(235 * min(1, (y - 1050) / 380))))
im = Image.alpha_composite(im.convert('RGBA'), ov)
dr = ImageDraw.Draw(im)
FB = os.path.join(_HERE, '..', 'assets', 'fonts', 'Hind-Bold.ttf')
def ctext(y, txt, size, fill, stroke, sw):
    f = ImageFont.truetype(FB, size, layout_engine=ImageFont.Layout.RAQM)
    while f.getlength(txt) > 1000: size -= 6; f = ImageFont.truetype(FB, size, layout_engine=ImageFont.Layout.RAQM)
    dr.text(((1080 - f.getlength(txt)) / 2, y), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
ctext(1240, l1, 120, (255, 255, 255), (0, 0, 0), 10)
ctext(1420, l2, 130, (255, 214, 64), (60, 20, 0), 11)
# channel badge
f = ImageFont.truetype(FB, 46, layout_engine=ImageFont.Layout.RAQM); bt = 'Kissa Aur Seekh'
w = f.getlength(bt) + 60
dr.rounded_rectangle([(1080 - w) / 2, 1640, (1080 + w) / 2, 1725], radius=40, fill=(229, 57, 53))
dr.text(((1080 - f.getlength(bt)) / 2, 1648), bt, font=f, fill=(255, 255, 255))
im.convert('RGB').save(out, quality=92)
