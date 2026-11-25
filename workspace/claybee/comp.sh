#!/bin/bash
cd /workspace/work/claybee
for f in claybee claybee_novo; do
  src=/tmp/cb_$( [ $f = claybee ] && echo final || echo novo ).mp4
  ffmpeg -y -v error -i $src -c:v libx264 -preset medium -crf 24 -maxrate 3.5M -bufsize 7M -pix_fmt yuv420p -c:a copy -movflags +faststart /tmp/${f}_s.mp4 && cp /tmp/${f}_s.mp4 ${f}_s.mp4
done
echo COMP_DONE > /tmp/comp.done
