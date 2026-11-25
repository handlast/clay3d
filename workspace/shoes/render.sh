cd /workspace/work/shoes
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1410
for i in 0 1 2 3; do a=$((i*353)); b=$(((i+1)*353)); [ $b -gt $NF ] && b=$NF; python3 film.py render $a $b /tmp/sh_$i.mp4 2>/tmp/sh_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/sh_$i.mp4"; done > /tmp/shl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/shl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/shoes.mp4 && cp /tmp/shoes.mp4 shoes.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 shoes.mp4
cat /tmp/sh_*.log
echo DONE
