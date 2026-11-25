#!/bin/bash
# 《动物打工人 No.03》渲染脚本（2026-11-16 v2：穿模约束 clear_track.json 已接入 film.py）
#   ./render.sh part i         渲第 i 段（8 帧，flock /tmp/render.lock，timeout 115 s）→ /tmp/cf8_i.mp4，并拷到 segs/
#   ./render.sh bg             后台驱动：等 /workspace/work/york/ALLDONE 出现 → 逐段渲染全片（每段一条命令，已完成的跳过，失败重试 1 次）
#   ./render.sh status         已完成段数
#   ./render.sh mux            拼接 + 两版音轨（成片含云健旁白 / 无旁白版），先写 /tmp 再拷回；核对帧数与响度
cd /workspace/work/clownfish3d
export PYTHONPATH=/workspace/.pylib
SEG=8
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=$(( (NF + SEG - 1) / SEG ))
mkdir -p segs
seg_ok() { [ -s segs/cf8_$1.mp4 ] && [ -f segs/cf8_$1.ok ]; }
if [ "$1" = "part" ]; then
  i=$2; seg_ok $i && { echo "seg $i done"; exit 0; }
  a=$((i*SEG)); b=$(( (i+1)*SEG )); [ $b -gt $NF ] && b=$NF
  flock -w ${LOCKW:-15} /tmp/render.lock timeout ${PYT:-100} python3 film.py render $a $b /tmp/cf8_$i.mp4 > /tmp/cf8_$i.log 2>&1
  n=$(ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -of csv=p=0 /tmp/cf8_$i.mp4 2>/dev/null)
  if [ "$n" = "$((b-a))" ]; then cp /tmp/cf8_$i.mp4 segs/cf8_$i.mp4 && touch segs/cf8_$i.ok; echo "seg $i ok ($n)"; else echo "seg $i FAIL ($n)"; tail -2 /tmp/cf8_$i.log; exit 1; fi
  exit 0
fi
if [ "$1" = "bg" ]; then
  while [ ! -f /workspace/work/york/ALLDONE ]; do sleep 30; done
  echo "york ALLDONE seen $(date -u)" >> segs/driver.log
  fails=0
  for i in $(seq 0 $((NS-1))); do
    seg_ok $i && continue
    ./render.sh part $i >> segs/driver.log 2>&1 || { sleep 3; ./render.sh part $i >> segs/driver.log 2>&1 || fails=$((fails+1)); }
    [ $fails -ge 3 ] && { echo "STOP: 3 segments failed twice" >> segs/driver.log; exit 1; }
    sleep 1
  done
  echo "RENDER_DONE $(date -u)" >> segs/driver.log
  exit 0
fi
if [ "$1" = "status" ]; then
  c=0; for i in $(seq 0 $((NS-1))); do seg_ok $i && c=$((c+1)); done; echo "$c / $NS"; exit 0
fi
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do seg_ok $i || { echo "missing seg $i"; exit 1; }; echo "file $PWD/segs/cf8_$i.mp4"; done > /tmp/cfl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/cfl.txt -c copy /tmp/cf_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/cf_video.mp4 -i bgm.wav -i vo.wav -filter_complex \
   "[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 20 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/cf_final.mp4 && cp /tmp/cf_final.mp4 clownfish.mp4
  ffmpeg -y -v error -i /tmp/cf_final.mp4 -i bgm.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-15:TP=-1.5:LRA=11 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/cf_novo.mp4 && cp /tmp/cf_novo.mp4 clownfish_novo.mp4
  for f in clownfish.mp4 clownfish_novo.mp4; do echo $f; ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 $f; ffmpeg -i $f -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:|Peak:" | tail -2; done
fi
