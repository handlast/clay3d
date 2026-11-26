# compress /tmp/bf_video.mp4 in parts (crf 26) within the lock budget: python3 enc.py <cmd_start_epoch> | enc.py join
import sys, os, time, subprocess
from cues import DUR
NF = round(DUR * 30); NP = 10; per = (NF + NP - 1) // NP
def part(i): return f"/tmp/bf_vs_{i}.mp4"
def ok(i): return os.path.exists(part(i) + ".ok")
if sys.argv[1] == "join":
    open("/tmp/bf_vsl.txt", "w").write("".join(f"file {part(i)}\n" for i in range(NP)))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "/tmp/bf_vsl.txt", "-c", "copy", "/tmp/bf_video_s.mp4"], check=True); sys.exit()
T0 = float(sys.argv[1]); est = 20
for i in range(NP):
    if ok(i): continue
    if time.time() - T0 + est > 112: break
    a = i * per; n = min(per, NF - a); t1 = time.time()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a / 30:.4f}", "-i", "/tmp/bf_video.mp4", "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "26", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", part(i)], check=True)
    c = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", part(i)], capture_output=True, text=True).stdout.strip()
    if c == str(n): open(part(i) + ".ok", "w").write("ok")
    est = max(est, time.time() - t1)
print("parts ok:", sum(ok(i) for i in range(NP)), "/", NP, "elapsed", round(time.time() - T0, 1))
