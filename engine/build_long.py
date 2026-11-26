"""Build a Sunday long video (16:9) and its teaser Short (9:16).

usage: python3 engine/build_long.py long/NN_slug

The folder needs: lscript.py, lrender.py, lmix.py, make_vo.py (copy from long/01_aakhri_ghar_aage and edit)
and meta.json with keys:
  long:   {title, description (may contain CHAPTERS), tags}
  teaser (OPTIONAL, no longer used): {title, description (contains LONG_URL), tags,
           scenes: [scene ids to cut], top: [line1, line2],
           end_line: spoken Hindi line, end_text: [big line, line 2, line 3]}
  thumb:  {scene, t, l1, l2}
  chapters: {scene_id: "Hinglish chapter name", ...}   (first scene must be included)
Writes long.mp4, long_hi.srt, thumbnail.jpg, teaser.mp4 into the folder and fills CHAPTERS in meta.json.
"""
import sys, os, json, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'engine'))
D = os.path.abspath(sys.argv[1]); os.chdir(D)
FB = os.path.join(ROOT, 'assets', 'fonts', 'Hind-Bold.ttf')
meta = json.load(open('meta.json'))
def run(cmd): print('>>', ' '.join(cmd), flush=True); subprocess.run(cmd, check=True)

os.makedirs('vo', exist_ok=True); os.makedirs('out', exist_ok=True)
run(['python3', 'make_vo.py'])
run(['python3', 'lrender.py', 'stills'])
g = {'__file__': os.path.join(D, 'lrender.py'), '__name__': 'x'}
sys.argv = ['x', 'none']; exec(open('lrender.py').read().split("if __name__")[0], g)
tl = g['build_timeline'](); FPS = g['FPS']
sids = [s for s, _, _ in tl]; half = len(sids) // 2
p = subprocess.Popen(['python3', 'lrender.py', 'video'] + sids[:half])
run(['python3', 'lrender.py', 'video'] + sids[half:]); assert p.wait() == 0
run(['python3', 'lmix.py'])
open('out/list.txt', 'w').write(''.join(f"file '{i:02d}_{s}.mp4'\n" for i, s in enumerate(sids)))
run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'out/list.txt', '-c', 'copy', 'out/video.mp4'])
run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'out/video.mp4', '-i', 'out/audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
     '-c:a', 'aac', '-b:a', '192k', '-shortest', 'long.mp4'])
# scene start times, chapters, subtitles
starts = {}; off = 0.0; srt = []; n = 0
def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
for sid, T, L in tl:
    starts[sid] = off
    for it in L:
        n += 1; srt.append(f"{n}\n{ts(off + it[0])} --> {ts(off + it[1] + 0.02)}\n{it[2]}\n")
    off += round(T * FPS) / FPS
open('long_hi.srt', 'w', encoding='utf-8').write("\n".join(srt))
ch = "\n".join(f"{int(starts[s])//60:02d}:{int(starts[s])%60:02d} {name}" for s, name in meta.get('chapters', {}).items() if s in starts)
meta['long']['description'] = meta['long']['description'].replace('CHAPTERS', ch)
meta['long_duration'] = off
# thumbnail (1280x720)
from PIL import Image, ImageDraw, ImageFont
import skia
th = meta['thumb']; Tt = dict((s, (T, L)) for s, T, L in tl)
surf = skia.Surface(1920, 1080); c = surf.getCanvas(); T_, L_ = Tt[th['scene']]
g['FN'][th['scene']](c, float(th['t']), T_, L_)
im = Image.fromarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)).convert('RGBA')
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
for x in range(1100): od.line([(x, 0), (x, 1080)], fill=(10, 6, 2, int(205 * max(0, 1 - x / 1100))))
im = Image.alpha_composite(im, ov); d = ImageDraw.Draw(im)
F = lambda s: ImageFont.truetype(FB, s, layout_engine=ImageFont.Layout.RAQM)
def fit(t, s, w=1000):
    f = F(s)
    while f.getlength(t) > w: s -= 6; f = F(s)
    return f
d.text((70, 150), th['l1'], font=fit(th['l1'], 170), fill=(255, 244, 220), stroke_width=12, stroke_fill=(120, 30, 20))
d.text((80, 420), th['l2'], font=fit(th['l2'], 120), fill=(255, 214, 64), stroke_width=10, stroke_fill=(60, 20, 0))
d.rounded_rectangle([80, 640, 600, 740], radius=45, fill=(229, 57, 53)); d.text((120, 650), 'पूरी कहानी', font=F(60), fill=(255, 255, 255))
im.convert('RGB').resize((1280, 720)).save('thumbnail.jpg', quality=92)
im.convert('RGB').resize((320, 180)).save('thumbnail_small.jpg', quality=90)   # how it looks in the feed: must still read
if 'teaser' not in meta:   # since Nov 2026 no teaser Short is made
    json.dump(meta, open('meta.json', 'w'), ensure_ascii=False, indent=1)
    print('DONE long', off); sys.exit(0)
# teaser (9:16): cut chosen scenes + end card
tz = meta['teaser']; a = starts[tz['scenes'][0]]
last = tz['scenes'][-1]; b = starts[last] + round(Tt[last][0] * FPS) / FPS - 0.2
def ctext(dr, y, t, s, fill, stroke, sw):
    f = fit(t, s); dr.text(((1080 - f.getlength(t)) / 2, y), t, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
ov = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
d.rounded_rectangle([60, 250, 1020, 560], radius=40, fill=(15, 10, 6, 190))
ctext(d, 270, tz['top'][0], 120, (255, 244, 220), (120, 30, 20), 8); ctext(d, 420, tz['top'][1], 96, (255, 214, 64), (60, 20, 0), 7)
d.rounded_rectangle([170, 1380, 910, 1490], radius=55, fill=(229, 57, 53)); ctext(d, 1392, 'पूरी कहानी नीचे लिंक पर', 58, (255, 255, 255), (0, 0, 0), 0)
d.polygon([(540, 1640), (470, 1560), (510, 1560), (510, 1500), (570, 1500), (570, 1560), (610, 1560)], fill=(255, 214, 64))
ov.save('out/overlay.png')
ec = Image.new('RGB', (1080, 1920)); d = ImageDraw.Draw(ec)
for y in range(1920): k = y / 1920; d.line([(0, y), (1080, y)], fill=(int(30 + 20 * k), int(34 + 20 * k), int(54 + 30 * k)))
et = tz['end_text']
ctext(d, 380, et[0], 130, (255, 214, 64), (60, 20, 0), 10)
for i, line in enumerate(et[1:]): ctext(d, 600 + i * 120, line, 84, (255, 255, 255), (0, 0, 0), 6)
d.rounded_rectangle([140, 960, 940, 1110], radius=75, fill=(229, 57, 53)); ctext(d, 982, 'पूरी कहानी देखिए', 80, (255, 255, 255), (0, 0, 0), 0)
d.polygon([(540, 1420), (440, 1290), (495, 1290), (495, 1170), (585, 1170), (585, 1290), (640, 1290)], fill=(255, 214, 64))
f = F(50); t = 'Kissa Aur Seekh'; w = f.getlength(t) + 70
d.rounded_rectangle([(1080 - w) / 2, 1600, (1080 + w) / 2, 1690], radius=45, fill=(229, 57, 53)); d.text(((1080 - f.getlength(t)) / 2, 1610), t, font=f, fill=(255, 255, 255))
ec.save('out/endcard.png')
from ai4b_tts import say
import soundfile as sf, numpy as np
wv, sr = say(tz['end_line'], 'female'); aa = np.abs(wv); ii = np.where(aa > 0.015)[0]; wv = wv[max(0, ii[0] - 400):ii[-1] + 1200]
sf.write('out/end_raw.wav', wv, sr)
run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'out/end_raw.wav', '-af', 'aresample=48000', '-ac', '2', 'out/end_vo.wav'])
run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{a:.2f}', '-to', f'{b:.2f}', '-i', 'long.mp4', '-i', 'out/overlay.png', '-filter_complex',
     "[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.12[bg];[b]scale=1440:-2,crop=1080:ih:150:0[fg];"
     "[bg][fg]overlay=0:(H-h)/2+20[v1];[v1][1:v]overlay=0:0,format=yuv420p,fade=t=in:st=0:d=0.3[v]",
     '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', 'out/t1.mp4'])
dur = sf.info('out/end_vo.wav').duration + 1.4
run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-framerate', '30', '-i', 'out/endcard.png', '-i', 'out/end_vo.wav', '-filter_complex',
     f"[0:v]format=yuv420p,fade=t=in:st=0:d=0.3,trim=duration={dur}[v];[1:a]adelay=400|400,apad[a]", '-map', '[v]', '-map', '[a]', '-t', f'{dur}',
     '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', 'out/t2.mp4'])
open('out/tl.txt', 'w').write("file 't1.mp4'\nfile 't2.mp4'\n")
run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'out/tl.txt', '-c', 'copy', 'teaser.mp4'])
json.dump(meta, open('meta.json', 'w'), ensure_ascii=False, indent=1)
print('DONE long', off, 'teaser', b - a + dur)
