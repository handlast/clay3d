cd /workspace/work/bun
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
for i in 0 1 2 3; do a=$((i*360)); b=$(((i+1)*360)); python3 film.py render $a $b /tmp/bn_$i.mp4 2>/tmp/bn_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/bn_$i.mp4"; done > /tmp/bnl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/bnl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/bun.mp4 && cp /tmp/bun.mp4 bun.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 bun.mp4
cat /tmp/bn_*.log
