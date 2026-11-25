# Lock-friendly renderer: run as  timeout 118 flock -w 100 /tmp/render.lock python3 rchunk.py <cmd_start_epoch>
# Renders pending 20-frame chunks two at a time until ~108 s after the command started, then exits (lock released).
# Existing complete 100-frame segments /tmp/hw_<k>.mp4 (k in DONE100) are reused.  `python3 rchunk.py list` writes the concat list.
import sys, os, time, subprocess, json
os.chdir("/workspace/work/howler")
from cues import DUR
NF = round(DUR * 30); C = 20; SEG = 100
DONE100 = [k for k in range(24) if os.path.exists(f"/tmp/hw_{k}.ok")]
def covered(a): return (a // SEG) in DONE100
def chunks(): return [(a, min(a + C, NF)) for a in range(0, NF, C) if not covered(a)]
def okfile(a): return f"/tmp/hwc_{a:05d}.ok"
def nframes(p):
    try: return int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())
    except Exception: return -1
if sys.argv[1] == "list":
    out = []; a = 0
    while a < NF:
        if covered(a): out.append(f"file /tmp/hw_{a // SEG}.mp4"); a = (a // SEG + 1) * SEG
        else:
            assert os.path.exists(okfile(a)), f"missing chunk {a}"; out.append(f"file /tmp/hwc_{a:05d}.mp4"); a += C
    open("/tmp/hwl.txt", "w").write("\n".join(out) + "\n"); print(len(out), "pieces"); sys.exit()
if sys.argv[1] == "status":
    p = [c for c in chunks() if not os.path.exists(okfile(c[0]))]; print("pending chunks", len(p), "of", len(chunks())); sys.exit()
T0 = float(sys.argv[1]); per = 0.55 * C   # est. seconds per pair (2 cores)
env = dict(os.environ, PYTHONPATH="/workspace/.pylib:" + os.environ.get("PYTHONPATH", ""))
while True:
    todo = [c for c in chunks() if not os.path.exists(okfile(c[0]))]
    if not todo: print("ALL CHUNKS DONE"); break
    if time.time() - T0 + per > 110: break
    batch = todo[:2]; ps = []
    for a, b in batch:
        ps.append((a, b, subprocess.Popen(["python3", "film.py", "render", str(a), str(b), f"/tmp/hwc_{a:05d}.mp4"], env=env, stderr=subprocess.DEVNULL)))
    with open("/tmp/hw_pids.txt", "a") as f:
        for a, b, p in ps: f.write(f"{p.pid}\n")
    t1 = time.time()
    for a, b, p in ps:
        p.wait()
        if nframes(f"/tmp/hwc_{a:05d}.mp4") == b - a: open(okfile(a), "w").write("ok")
    per = max(per * 0.5, time.time() - t1) * 1.0
todo = [c for c in chunks() if not os.path.exists(okfile(c[0]))]
print("pending", len(todo), "elapsed", round(time.time() - T0, 1))
