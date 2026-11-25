cd /workspace/work/dance
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
for i in 0 1 2 3; do a=$((i*240)); b=$(((i+1)*240)); python3 film.py render $a $b /tmp/d_$i.mp4 2>/tmp/d_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/d_$i.mp4"; done > /tmp/dl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/dl.txt -i bgm.wav -c:v copy -af loudnorm=I=-13:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/dance.mp4 && cp /tmp/dance.mp4 dance.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 dance.mp4
cat /tmp/d_*.log
