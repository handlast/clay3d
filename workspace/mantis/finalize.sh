#!/bin/bash
# re-encode video (<100 MB), remux both audio versions, normalize no-VO version, report
cd /workspace/work/mantis
ffmpeg -y -v error -i /tmp/mt_video.mp4 -c:v libx264 -preset veryfast -crf 24 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -an /tmp/mt_v2.mp4 || exit 1
ffmpeg -y -v error -i /tmp/mt_v2.mp4 -i mantis.mp4 -map 0:v -map 1:a -c copy -movflags +faststart /tmp/mantis_f.mp4 && cp /tmp/mantis_f.mp4 mantis.mp4
ffmpeg -y -v error -i /tmp/mt_v2.mp4 -i mantis_novo.mp4 -map 0:v -map 1:a -c:v copy -af "volume=1.5dB,alimiter=limit=0.84:level=false" -c:a aac -b:a 192k -movflags +faststart /tmp/mantis_novo_f.mp4 && cp /tmp/mantis_novo_f.mp4 mantis_novo.mp4
for f in mantis.mp4 mantis_novo.mp4; do echo $f; ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 $f; ffmpeg -i $f -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+I:|Peak:" | tail -2; done
