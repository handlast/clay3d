#!/bin/bash
# usage: flock /tmp/render.lock ./render.sh a b  (NS=16 segments, 2 at a time) ; ./render.sh mux ; ./render.sh preview  (0-8 s)
cd /workspace/work/frog
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=16; SEG=$(( (NF + NS - 1) / NS ))
AF="[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]"
if [ "$1" = "pvseg" ]; then   # preview segments: pvseg <i0> <i1> <idx>
  python3 film.py render $2 $3 /tmp/fgpv_$4.mp4 2>/tmp/fgpv_$4.log & echo $! >> /tmp/fg_pids.txt; wait; cat /tmp/fgpv_$4.log; exit
fi
if [ "$1" = "pvmux" ]; then
  printf "file /tmp/fgpv_0.mp4\nfile /tmp/fgpv_1.mp4\n" > /tmp/fgpvl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/fgpvl.txt -c copy /tmp/fgpv_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/fgpv_video.mp4 -ss 0 -t 8 -i bgm.wav -ss 0 -t 8 -i vo.wav -filter_complex "$AF" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t 8 -movflags +faststart /tmp/frog_preview.mp4 && cp /tmp/frog_preview.mp4 frog_preview.mp4
  ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 frog_preview.mp4; exit
fi
if [ "$1" = "muxnv" ]; then   # no-voice version: BGM only
  ffmpeg -y -v error -i /tmp/fg_video.mp4 -i bgm.wav -filter_complex "[1:a]aresample=44100,loudnorm=I=-14.2:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/frog_novo.mp4 && cp /tmp/frog_novo.mp4 frog_novo.mp4
  ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 frog_novo.mp4; exit
fi
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/fg_$i.mp4"; done > /tmp/fgl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/fgl.txt -c copy /tmp/fg_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/fg_video.mp4 -i bgm.wav -i vo.wav -filter_complex "$AF" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/frog.mp4 && cp /tmp/frog.mp4 frog.mp4
  ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 frog.mp4; exit
fi
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  python3 film.py render $a $b /tmp/fg_$i.mp4 2>/tmp/fg_$i.log & echo $! >> /tmp/fg_pids.txt
done; wait
cat $(for i in "$@"; do echo /tmp/fg_$i.log; done)
