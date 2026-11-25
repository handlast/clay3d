cd /workspace/work/braess
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
for i in 0 1 2 3; do a=$((i*364)); b=$(((i+1)*364)); python3 film.py render $a $b /tmp/b_$i.mp4 2>/tmp/b_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/b_$i.mp4"; done > /tmp/bl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/bl.txt -i bgm.wav -c:v copy -af loudnorm=I=-13:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/braess.mp4 && cp /tmp/braess.mp4 braess.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 braess.mp4
cat /tmp/b_*.log
