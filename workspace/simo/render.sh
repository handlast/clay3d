#!/bin/bash
# usage: ./render.sh <seg> [<seg> ...]  (NS segments, run 2 at a time) ; ./render.sh mux
cd /workspace/work/simo
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=30; SEG=$(( (NF + NS - 1) / NS ))
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/sm_$i.mp4"; done > /tmp/sml.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/sml.txt -i bgm.wav -c:v copy -af loudnorm=I=-15:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/simo.mp4 && cp /tmp/simo.mp4 simo.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 simo.mp4
  exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/sm_$i.mp4 2>/tmp/sm_$i.log & echo $! >> /tmp/sm_pids.txt
done; wait
cat $(for i in "$@"; do echo /tmp/sm_$i.log; done)
