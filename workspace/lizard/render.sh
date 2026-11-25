cd /workspace/work/lizard
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1380
for i in 0 1 2 3; do a=$((i*NF/4)); b=$(((i+1)*NF/4)); python3 film.py render $a $b /tmp/lz_$i.mp4 2>/tmp/lz_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/lz_$i.mp4"; done > /tmp/lzl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/lzl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/lizard.mp4 && cp /tmp/lizard.mp4 lizard.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 lizard.mp4
cat /tmp/lz_*.log
echo DONE
