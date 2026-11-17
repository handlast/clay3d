#!/bin/bash
# usage: ./render.sh <seg> [<seg> ...]  (NS segments, run 2 at a time) ; ./render.sh mux
cd /workspace/work/balrog
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=26; SEG=$(( (NF + NS - 1) / NS ))
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/br_$i.mp4"; done > /tmp/brl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/brl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/balrog.mp4 && cp /tmp/balrog.mp4 balrog.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 balrog.mp4
  exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/br_$i.mp4 2>/tmp/br_$i.log & echo $! >> /tmp/br_pids.txt
done; wait
cat $(for i in "$@"; do echo /tmp/br_$i.log; done)
