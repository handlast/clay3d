#!/bin/bash
# usage: ./render.sh <seg> [<seg> ...]   (16 segments of 1410 frames, run 2 at a time)  ;  ./render.sh mux
cd /workspace/work/trapdoor
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1410; NS=16; SEG=$(( (NF + NS - 1) / NS ))
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/td_$i.mp4"; done > /tmp/tdl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/tdl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/trapdoor.mp4 && cp /tmp/trapdoor.mp4 trapdoor.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 trapdoor.mp4
  exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/td_$i.mp4 2>/tmp/td_$i.log & echo $! >> /tmp/td_pids.txt
done; wait
cat $(for i in "$@"; do echo /tmp/td_$i.log; done)
