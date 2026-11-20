# edge-tts 云健 −5%（jellyfrog），逐句生成并去首尾静音，写 vox/durs.json；`python3 vo.py mix` 按 cues 摆放成 vo.wav（每句起点 +0.1 s，不加速）
import subprocess, json, os, sys, numpy as np, soundfile as sf
from lines import LINES
SR = 48000; os.makedirs("vox", exist_ok=True)
def gen():
    durs = {}
    for k, sub, vo, ex in LINES:
        mp, wv = f"vox/{k}.mp3", f"vox/{k}.wav"
        meta = f"vox/{k}.txt"
        if not (os.path.exists(wv) and os.path.exists(meta) and open(meta).read() == vo):
            for tr in range(3):
                try:
                    subprocess.run(["python3", "-m", "edge_tts", "--voice", "zh-CN-YunjianNeural", "--rate=-5%", "--text", vo, "--write-media", mp], check=True, timeout=60); break
                except Exception as e: print("retry", k, e)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mp, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse", "-ar", str(SR), "-ac", "1", wv], check=True)
            open(meta, "w").write(vo)
        x, _ = sf.read(wv); durs[k] = round(len(x) / SR, 3)
    json.dump(durs, open("vox/durs.json", "w"), ensure_ascii=False, indent=1); print(durs)
def mix():
    from cues import T, DUR, VOFF
    out = np.zeros(int(DUR * SR))
    for k, sub, vo, ex in LINES:
        x, _ = sf.read(f"vox/{k}.wav"); st = int((T[k] + VOFF[k]) * SR); n = min(len(x), len(out) - st); out[st:st + n] += x[:n]
    sf.write("vo.wav", out, SR); print("vo.wav", DUR)
if __name__ == "__main__":
    mix() if len(sys.argv) > 1 and sys.argv[1] == "mix" else gen()
