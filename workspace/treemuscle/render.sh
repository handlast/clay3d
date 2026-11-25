#!/bin/bash
# usage: ./render.sh <seg> [<seg> ...]  (NS segments, run 2 at a time) ; ./render.sh mux
cd /workspace/work/treemuscle
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=26; SEG=$(( (NF + NS - 1) / NS ))
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/tm_$i.mp4"; done > /tmp/tml.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/tml.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/treemuscle.mp4 && cp /tmp/treemuscle.mp4 treemuscle.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 treemuscle.mp4
  exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/tm_$i.mp4 2>/tmp/tm_$i.log & echo $! >> /tmp/tm_pids.txt
done; wait
cat $(for i in "$@"; do echo /tmp/tm_$i.log; done)
