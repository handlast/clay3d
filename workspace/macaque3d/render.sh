#!/bin/bash
# 后台全片渲染：setsid nohup ./render.sh run &   （每段 64 帧，跑完的段会跳过；可重入）
# ./render.sh mux   合成两版音轨
cd /workspace/work/macaque3d
export PYTHONPATH=/workspace/.pylib
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); SEG=64; NS=$(( (NF + SEG - 1) / SEG ))
if [ "$1" = "run" ]; then
  for i in $(seq 0 $((NS-1))); do
    [ -f /tmp/mq_seg_$i.ok ] && continue
    a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
    flock /tmp/render.lock python3 film.py render $a $b /tmp/mq_seg_$i.mp4 > /tmp/mq_seg_$i.log 2>&1 && touch /tmp/mq_seg_$i.ok
    echo "seg $i $(date +%T)" >> /tmp/mq_progress.log
  done
  echo ALLDONE >> /tmp/mq_progress.log; exit
fi
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/mq_seg_$i.mp4"; done > /tmp/mql.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/mql.txt -c copy /tmp/mq_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/mq_video.mp4 -i bgm.wav -i vo.wav -filter_complex \
   "[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 22 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/mq_final.mp4 && cp /tmp/mq_final.mp4 macaque.mp4
  ffmpeg -y -v error -i /tmp/mq_final.mp4 -i bgm.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-15:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/mq_novo.mp4 && cp /tmp/mq_novo.mp4 macaque_novo.mp4
  for f in macaque.mp4 macaque_novo.mp4; do echo $f; ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 $f; ffmpeg -i $f -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:|Peak:" | tail -2; done
fi
