# Lock-friendly renderer: run as  timeout 118 flock -w 15 /tmp/render.lock python3 rchunk.py <cmd_start_epoch>
# Renders pending 20-frame chunks two at a time (2 cores) until ~108 s after the command started, then exits (lock released).
# `python3 rchunk.py status` / `python3 rchunk.py list` (writes /tmp/jfl.txt concat list). Only our own PIDs are recorded/killed.
import sys, os, time, subprocess
os.chdir("/workspace/work/jellyfrog")
from cues import DUR
NF = round(DUR * 30); C = 20
def chunks(): return [(a, min(a + C, NF)) for a in range(0, NF, C)]
def out(a): return f"/tmp/jfc_{a:05d}.mp4"
def okfile(a): return f"/tmp/jfc_{a:05d}.ok"
def nframes(p):
    try: return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())
    except Exception: return -1
if sys.argv[1] == "list":
    for a, b in chunks(): assert os.path.exists(okfile(a)), f"missing chunk {a}"
    open("/tmp/jfl.txt", "w").write("".join(f"file {out(a)}\n" for a, b in chunks())); print(len(chunks()), "pieces"); sys.exit()
if sys.argv[1] == "status":
    p = [c for c in chunks() if not os.path.exists(okfile(c[0]))]; print("pending chunks", len(p), "of", len(chunks())); sys.exit()
T0 = float(sys.argv[1]); per = 0.6 * C
env = dict(os.environ, PYTHONPATH="/workspace/.pylib:" + os.environ.get("PYTHONPATH", ""))
while True:
    todo = [c for c in chunks() if not os.path.exists(okfile(c[0]))]
    if not todo: print("ALL CHUNKS DONE"); break
    if time.time() - T0 + per > 108: break
    ps = []
    for a, b in todo[:2]:
        ps.append((a, b, subprocess.Popen(["python3", "film.py", "render", str(a), str(b), out(a)], env=env, stderr=subprocess.DEVNULL)))
    with open("/tmp/jf_pids.txt", "a") as f:
        for a, b, p in ps: f.write(f"{p.pid}\n")
    t1 = time.time()
    for a, b, p in ps:
        p.wait()
        if nframes(out(a)) == b - a: open(okfile(a), "w").write("ok")
    per = time.time() - t1
todo = [c for c in chunks() if not os.path.exists(okfile(c[0]))]
print("pending", len(todo), "elapsed", round(time.time() - T0, 1))
