#!/bin/bash
# usage: ./render.sh <seg> [<seg> ...]   (16 segments of 1260 frames, run 2 at a time)  ;  ./render.sh mux
cd /workspace/work/aliens
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1260; NS=16; SEG=$(( (NF + NS - 1) / NS ))
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/al_$i.mp4"; done > /tmp/all.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/all.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/aliens.mp4 && cp /tmp/aliens.mp4 aliens.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 aliens.mp4
  exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/al_$i.mp4 2>/tmp/al_$i.log & echo $! >> /tmp/al_pids.txt
done; wait
cat $(for i in "$@"; do echo /tmp/al_$i.log; done)
