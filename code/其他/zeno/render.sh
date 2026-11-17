cd /workspace/work/zeno
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
for i in 0 1 2 3; do a=$((i*375)); b=$(((i+1)*375)); python3 film.py render $a $b /tmp/z_$i.mp4 2>/tmp/z_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/z_$i.mp4"; done > /tmp/zl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/zl.txt -i bgm.wav -c:v copy -af loudnorm=I=-13:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/zeno.mp4 && cp /tmp/zeno.mp4 zeno_tortoise.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 zeno_tortoise.mp4
cat /tmp/z_*.log
