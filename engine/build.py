"""Build one story end to end.
usage: python3 engine/build.py stories/NN_name "cover line 1" "cover line 2" [hook_time]
Writes videos/NN_name.mp4 (with 0.5 s cover at the end) and videos/NN_name_cover.jpg
"""
import sys, os, subprocess, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
story = os.path.abspath(sys.argv[1]); l1, l2 = sys.argv[2], sys.argv[3]
hook_t = sys.argv[4] if len(sys.argv) > 4 else '1.5'
name = os.path.basename(story.rstrip('/'))
def run(cmd, cwd=story):
    print('>>', ' '.join(cmd), flush=True); subprocess.run(cmd, cwd=cwd, check=True)
spec = importlib.util.spec_from_file_location('script', os.path.join(story, 'script.py'))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sids = [s for s, _ in m.SCENES]
os.makedirs(os.path.join(story, 'vo'), exist_ok=True); os.makedirs(os.path.join(story, 'out'), exist_ok=True)
run(['python3', 'make_vo.py'])
run(['python3', 'render.py', 'stills'])
half = len(sids) // 2
p1 = subprocess.Popen(['python3', 'render.py', 'video'] + sids[:half], cwd=story)
run(['python3', 'render.py', 'video'] + sids[half:])
assert p1.wait() == 0
run(['python3', 'mix.py'])
out = os.path.join(story, 'out')
with open(os.path.join(out, 'list.txt'), 'w') as f:
    for i, s in enumerate(sids): f.write(f"file '{i:02d}_{s}.mp4'\n")
    f.write("file 'cover.mp4'\n")
vid = os.path.join(ROOT, 'videos'); os.makedirs(vid, exist_ok=True)
cover = os.path.join(vid, f'{name}_cover.jpg')
run(['python3', os.path.join(ROOT, 'engine', 'make_cover.py'), story, 'render.py', sids[0], hook_t, l1, l2, cover])
run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', cover, '-vf', 'format=yuv420p,loop=-1:1,trim=duration=0.5',
     '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', 'cover.mp4'], cwd=out)
run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'video.mp4'], cwd=out)
final = os.path.join(vid, f'{name}.mp4')
run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'video.mp4', '-i', 'audio.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
     '-af', 'apad', '-c:a', 'aac', '-b:a', '192k', '-shortest', final], cwd=out)
run(['python3', os.path.join(ROOT, 'engine', 'make_srt.py'), story, 'render.py', os.path.join(vid, f'{name}_hi.srt')])
print('DONE', final, cover)
