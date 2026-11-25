cd /workspace/work/neanderthal
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1410
for i in 0 1 2; do a=$((i*470)); b=$(((i+1)*470)); [ $b -gt $NF ] && b=$NF; python3 film.py render $a $b /tmp/ne_$i.mp4 2>/tmp/ne_$i.log & echo $! >> /tmp/ne_pids.txt; done; wait
for i in 0 1 2; do echo "file /tmp/ne_$i.mp4"; done > /tmp/nel.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/nel.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/neanderthal.mp4 && cp /tmp/neanderthal.mp4 neanderthal.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 neanderthal.mp4
cat /tmp/ne_*.log
echo DONE
