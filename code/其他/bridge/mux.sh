#!/bin/bash
set -e
cd /workspace/work/bridge
./run.sh
n=$(ls seg/*.done | wc -l); [ "$n" -eq 60 ] || { echo "only $n"; exit 1; }
ls seg/s*.mp4 | sort | sed "s/^/file '\/workspace\/work\/bridge\//;s/$/'/" > /tmp/br_list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/br_list.txt -c copy /tmp/br_v.mp4
ffmpeg -y -loglevel error -i music.wav -i sfx.wav -filter_complex "[0][1]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000" -ac 2 -t 240 /tmp/br_a.wav
ffmpeg -y -loglevel error -i /tmp/br_v.mp4 -i /tmp/br_a.wav -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart /tmp/duanqiao.mp4
cp /tmp/duanqiao.mp4 duanqiao.mp4
python3 - <<'P'
from cues import SUBS
def ts(x):
    h=int(x//3600);m=int(x%3600//60);s=x%60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s-int(s))*1000)):03d}"
with open('duanqiao.srt','w') as f:
    for i,(t,a,b) in enumerate(SUBS,1): f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
bad=[(t,b-a) for t,a,b in SUBS if b-a<max(1.5,len(t)/4)]
print("SHORT",bad)
P
ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of csv=p=0 duanqiao.mp4
ffmpeg -i duanqiao.mp4 -af ebur128 -f null - 2>&1 | grep -A1 "Integrated" | tail -2
ls -la duanqiao.mp4
