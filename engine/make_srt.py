import sys, os
d, mod, out = sys.argv[1:4]
d = os.path.abspath(d); out = os.path.abspath(out)
os.chdir(d); sys.path.insert(0, d); sys.argv = ['x', 'none']
g = {'__file__': os.path.join(d, mod), '__name__': 'srt'}
exec(open(mod).read().split("if __name__")[0], g)
tl = g['build_timeline'](); FPS = g['FPS']
def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
off = 0.0; n = 0; lines = []
for sid, T, L in tl:
    for it in L:
        a, b, txt = it[0], it[1], it[2]
        n += 1; lines.append(f"{n}\n{ts(off + a)} --> {ts(off + b + 0.02)}\n{txt}\n")
    off += round(T * FPS) / FPS
open(out, 'w', encoding='utf-8').write("\n".join(lines))
print(out, n)
