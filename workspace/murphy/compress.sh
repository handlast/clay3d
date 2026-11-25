#!/bin/bash
# ./compress.sh i  -> encode video chunk i (of 4) at crf 25 ; ./compress.sh mux
cd /workspace/work/murphy; NF=2308; C=$(( (NF + 3) / 4 ))
if [ "$1" = "mux" ]; then
  for i in 0 1 2 3; do echo "file /tmp/mu_c_$i.mp4"; done > /tmp/mu_cl.txt
  ffmpeg -y -v error -f concat -safe 0 -i /tmp/mu_cl.txt -c copy /tmp/mu_cv.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/mu_cv.mp4 -i murphy_final.mp4 -map 0:v -map 1:a -c copy -movflags +faststart /tmp/murphy_final_s.mp4 || exit 1
  ffmpeg -y -v error -i /tmp/mu_cv.mp4 -i murphy_final_novo.mp4 -map 0:v -map 1:a -c copy -movflags +faststart /tmp/murphy_final_novo_s.mp4 || exit 1
  cp /tmp/murphy_final_s.mp4 /tmp/murphy_final_novo_s.mp4 . ; exit
fi
for i in "$@"; do a=$((i*C)); n=$C; [ $((a+n)) -gt $NF ] && n=$((NF-a))
  ffmpeg -y -v error -i murphy_final_novo.mp4 -vf "select=between(n\,$a\,$((a+n-1))),setpts=N/30/TB" -an -frames:v $n -r 30 -c:v libx264 -preset medium -crf 25 -pix_fmt yuv420p /tmp/mu_c_$i.mp4 && echo ok $i
done
