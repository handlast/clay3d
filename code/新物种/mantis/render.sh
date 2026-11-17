#!/bin/bash
# usage: ./render.sh <seg> [<seg>]   (NS segments, run 2 at a time, always via: flock /tmp/render.lock ./render.sh a b) ; ./render.sh mux
cd /workspace/work/mantis
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=16; SEG=$(( (NF + NS - 1) / NS ))
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/mt_$i.mp4"; done > /tmp/mtl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/mtl.txt -c copy /tmp/mt_video.mp4 || exit 1
  # voice-over version: BGM ducked by the narration (sidechaincompress thr 0.03, 6:1)
  ffmpeg -y -v error -i /tmp/mt_video.mp4 -i bgm.wav -i vo.wav -filter_complex \
   "[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/mantis.mp4 && cp /tmp/mantis.mp4 mantis.mp4
  ffmpeg -y -v error -i /tmp/mt_video.mp4 -i bgm.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-15:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/mantis_novo.mp4 && cp /tmp/mantis_novo.mp4 mantis_novo.mp4
  for f in mantis.mp4 mantis_novo.mp4; do ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 $f; done
  exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/mt_$i.mp4 2>/tmp/mt_$i.log & echo $! >> /tmp/mt_pids.txt
done; wait
cat $(for i in "$@"; do echo /tmp/mt_$i.log; done)
