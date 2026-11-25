cd /workspace/work/hag
for i in 0 1 2 3; do a=$((i*360)); b=$(((i+1)*360)); python3 film.py render $a $b /tmp/h_$i.mp4 & done; wait
for i in 0 1 2 3; do echo "file /tmp/h_$i.mp4"; done > /tmp/hl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/hl.txt -i bgm.wav -c:v copy -af loudnorm=I=-13:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/hag.mp4 && cp /tmp/hag.mp4 hagfish_knot_v2.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 hagfish_knot_v2.mp4
