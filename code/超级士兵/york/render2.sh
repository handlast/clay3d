#!/bin/bash
# ./render2.sh i j ...  renders segments of 0..2169 split into 18 parts (run 2 at a time); ./render2.sh mux
cd /workspace/work/york; export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=18; SEG=$(( (NF + NS - 1) / NS ))
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/yk2_$i.mp4"; done > /tmp/yk2l.txt
  DD=$(python3 -c "print($NF/30)")
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/yk2l.txt -c copy /tmp/yk_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/yk_video.mp4 -i bgm.wav -i vo.wav -filter_complex \
   "[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t $DD -movflags +faststart /tmp/york_out.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/yk_video.mp4 -i bgm.wav -filter_complex "[1:a]aresample=44100,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t $DD -movflags +faststart /tmp/york_novo.mp4 || exit 1
  exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/yk2_$i.mp4 2>/tmp/yk2_$i.log & echo "pid $! seg $i"; done; wait
cat $(for i in "$@"; do echo /tmp/yk2_$i.log; done)
