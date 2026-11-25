cd /workspace/work/germ
for i in 0 1 2 3; do a=$((i*360)); b=$(((i+1)*360)); python3 film.py render $a $b /tmp/g_$i.mp4 & done; wait
for i in 0 1 2 3; do echo "file /tmp/g_$i.mp4"; done > /tmp/gl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/gl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/germ.mp4 && cp /tmp/germ.mp4 half_bacteria.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 half_bacteria.mp4
