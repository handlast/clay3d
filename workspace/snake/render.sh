cd /workspace/work/snake
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1384
for i in 0 1 2; do a=$((i*NF/3)); b=$(((i+1)*NF/3)); python3 film.py render $a $b /tmp/sn_$i.mp4 2>/tmp/sn_$i.log & done; wait
for i in 0 1 2; do echo "file /tmp/sn_$i.mp4"; done > /tmp/snl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/snl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/snake.mp4 && cp /tmp/snake.mp4 snake.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 snake.mp4
cat /tmp/sn_*.log
echo DONE
