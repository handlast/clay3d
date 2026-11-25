#!/bin/bash
# ./render.sh i j   renders segments i,j (90 frames each) in parallel; face segments at MS=2.0 (2x supersampling). ./render.sh mux
cd /workspace/work/murphy; export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=$(python3 -c "from cues import DUR; print(round(DUR*30))"); SEG=45; NS=$(( (NF + SEG - 1) / SEG ))
mkdir -p /tmp/mu_segs
if [ "$1" = "n" ]; then echo $NS; exit; fi
FACE=$(python3 -c "from cues import T,nxt; print(' '.join(f'{round(T[k]*30)}:{round(nxt(k)*30)}' for k in ('who','danger','scared')))")
if [ "$1" = "auto" ]; then   # render pending segments in pairs within a ~105 s budget (call under flock)
  T0=${CMD_T0:-$(date +%s)}; P=()
  for i in $(seq 0 $((NS-1))); do [ -f /tmp/mu_segs/s_$i.ok ] || P+=($i); done
  echo "pending ${#P[@]}"; k=0
  while [ $k -lt ${#P[@]} ]; do
    now=$(date +%s); a=$((${P[$k]}*SEG)); F=0; for r in $FACE; do fa=${r%:*}; fb=${r#*:}; [ $a -lt $((fb+11)) ] && [ $((a+2*SEG)) -gt $fa ] && F=1; done
    REM=$((112 - now + T0)); if [ $F = 1 ]; then E2=66; E1=44; else E2=52; E1=32; fi
    if [ $REM -gt $E2 ] && [ $((k+1)) -lt ${#P[@]} ]; then $0 ${P[$k]} ${P[$((k+1))]}; k=$((k+2))
    elif [ $REM -gt $E1 ]; then $0 ${P[$k]}; k=$((k+1))
    else break; fi
  done; exit
fi
if [ "$1" = "mux" ]; then
  for i in $(seq 0 $((NS-1))); do echo "file /tmp/mu_segs/s_$i.mp4"; done > /tmp/mu_list.txt
  DD=$(python3 -c "print($NF/30)")
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/mu_list.txt -c copy /tmp/mu_video.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/mu_video.mp4 -i bgm.wav -i vo.wav -filter_complex \
   "[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,highpass=f=80,volume=1.7,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.75[bg];[bg][vk]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350:makeup=1[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t $DD -movflags +faststart /tmp/murphy_out.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/mu_video.mp4 -i bgm.wav -filter_complex "[1:a]aresample=44100,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t $DD -movflags +faststart /tmp/murphy_novo.mp4 || exit 1
  exit
fi
FACE=$(python3 -c "from cues import T,nxt; print(' '.join(f'{round(T[k]*30)}:{round(nxt(k)*30)}' for k in ('who','danger','scared')))")
for i in "$@"; do a=$((i*SEG)); b=$(((i+1)*SEG)); [ $b -gt $NF ] && b=$NF
  [ -f /tmp/mu_segs/s_$i.ok ] && { echo "seg $i done"; continue; }
  MS=1.5; for r in $FACE; do fa=${r%:*}; fb=${r#*:}; if [ $a -lt $((fb+11)) ] && [ $b -gt $fa ]; then MS=2.0; fi; done
  ( MS=$MS python3 film.py render $a $b /tmp/mu_segs/s_$i.mp4 2>/tmp/mu_segs/s_$i.log && touch /tmp/mu_segs/s_$i.ok ) & echo "pid $! seg $i MS=$MS"
done; wait
cat $(for i in "$@"; do echo /tmp/mu_segs/s_$i.log; done) 2>/dev/null | tail -5
