from cues import SUBS, DUR
def ts(x):
    x = max(0, x); h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
out = []
for i, (a, b, s, k) in enumerate(SUBS):
    out.append(f"{i+1}\n{ts(a)} --> {ts(min(b, DUR))}\n{s.replace('|', chr(10))}\n")
open("claybee.srt", "w").write("\n".join(out)); print("\n".join(out))
