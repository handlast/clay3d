#!/bin/bash
# 《动物打工人 No.04》渲染脚本（照 clownfish3d/render.sh）
#   ./render.sh part i     渲第 i 段（8 帧；flock /tmp/render.lock 等锁上限 LOCKW 秒，python 超时 PYT 秒）→ /tmp/cb8_i.mp4，核帧数后拷到 segs/
#   ./render.sh bg         后台驱动：逐段渲染全片（已完成跳过，失败重试 1 次；拿不到锁就等 20 s 重排），写 segs/driver.log 与 segs/driver.pid
#   ./render.sh status     已完成段数
#   ./render.sh mux        拼接 + 两版音轨（含云健旁白 / 无旁白），先写 /tmp 再拷回；核对帧数与响度
cd /workspace/work/claybee
export PYTHONPATH=/workspace/.pylib
SEG=8
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); NS=$(( (NF + SEG - 1) / SEG ))
mkdir -p segs
seg_ok() { [ -s segs/cb8_$1.mp4 ] && [ -f segs/cb8_$1.ok ]; }
if [ "$1" = "part" ]; then
  i=$2; seg_ok $i && { echo "seg $i done"; exit 0; }
  a=$((i*SEG)); b=$(( (i+1)*SEG )); [ $b -gt $NF ] && b=$NF
  flock -w ${LOCKW:-60} /tmp/render.lock timeout ${PYT:-300} python3 film.py render $a $b /tmp/cb8_$i.mp4 > /tmp/cb8_$i.log 2>&1
  rc=$?
  [ $rc -eq 1 ] && grep -q . /tmp/cb8_$i.log || true
  n=$(ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -of csv=p=0 /tmp/cb8_$i.mp4 2>/dev/null)
  if [ "$n" = "$((b-a))" ]; then cp /tmp/cb8_$i.mp4 segs/cb8_$i.mp4 && touch segs/cb8_$i.ok; echo "seg $i ok ($n) $(date -u +%H:%M:%S)"; else echo "seg $i FAIL rc=$rc ($n)"; tail -2 /tmp/cb8_$i.log; exit 1; fi
  exit 0
fi
if [ "$1" = "bg" ]; then
  echo $$ > segs/driver.pid
  echo "start $(date -u)" >> segs/driver.log
  fails=0
  for i in $(seq 0 $((NS-1))); do
    seg_ok $i && continue
    ./render.sh part $i >> segs/driver.log 2>&1 || { sleep 20; ./render.sh part $i >> segs/driver.log 2>&1 || fails=$((fails+1)); }
    [ $fails -ge 3 ] && { echo "STOP: 3 segments failed twice" >> segs/driver.log; exit 1; }
  done
  echo "RENDER_DONE $(date -u)" >> segs/driver.log
  exit 0
fi
if [ "$1" = "status" ]; then
  c=0; for i in $(seq 0 $((NS-1))); do seg_ok $i && c=$((c+1)); done; echo "$c / $NS"; exit 0
fi
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do seg_ok $i || { echo "missing seg $i"; exit 1; }; echo "file $PWD/segs/cb8_$i.mp4"; done > /tmp/cbl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/cbl.txt -c copy /tmp/cb_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/cb_video.mp4 -i bgm.wav -i vo.wav -filter_complex \
   "[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 20 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/cb_final.mp4 && cp /tmp/cb_final.mp4 claybee.mp4
  ffmpeg -y -v error -i /tmp/cb_final.mp4 -i bgm.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-15:TP=-1.5:LRA=11 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/cb_novo.mp4 && cp /tmp/cb_novo.mp4 claybee_novo.mp4
  for f in claybee claybee_novo; do
    ffmpeg -y -v error -i /tmp/cb_$( [ $f = claybee ] && echo final || echo novo ).mp4 -c:v libx264 -preset medium -crf 24 -maxrate 3.5M -bufsize 7M -pix_fmt yuv420p -c:a copy -movflags +faststart /tmp/${f}_s.mp4 && cp /tmp/${f}_s.mp4 ${f}_s.mp4
  done
  for f in claybee.mp4 claybee_novo.mp4 claybee_s.mp4 claybee_novo_s.mp4; do echo $f; ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 $f; ffmpeg -i $f -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:|Peak:" | tail -2; done
fi
