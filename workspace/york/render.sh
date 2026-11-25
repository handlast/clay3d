#!/bin/bash
# usage: ./render.sh F0 F1 SEG...   renders [F0,F1) split into 8 parts; pass part indices (run 2 at a time); ./render.sh mux F0 F1
cd /workspace/work/york; export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
if [ "$1" = "mux" ]; then
  F0=$2; F1=$3; for i in $(seq 0 7); do echo "file /tmp/yk_$i.mp4"; done > /tmp/ykl.txt
  SS=$(python3 -c "print($F0/30)"); DD=$(python3 -c "print(($F1-$F0)/30)")
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/ykl.txt -c copy /tmp/yk_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/yk_video.mp4 -ss $SS -t $DD -i bgm.wav -ss $SS -t $DD -i vo.wav -filter_complex \
   "[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t $DD -movflags +faststart /tmp/york_out.mp4 || exit 1
  exit
fi
F0=$1; F1=$2; shift 2; N=$((F1-F0)); SEG=$(( (N + 7) / 8 ))
for i in "$@"; do a=$((F0+i*SEG)); b=$((F0+(i+1)*SEG)); [ $b -gt $F1 ] && b=$F1
  python3 film.py render $a $b /tmp/yk_$i.mp4 2>/tmp/yk_$i.log & done; wait
cat $(for i in "$@"; do echo /tmp/yk_$i.log; done)
