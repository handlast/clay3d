cd /workspace/work/bonobo
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1410
for i in 0 1 2; do a=$((i*470)); b=$(((i+1)*470)); [ $b -gt $NF ] && b=$NF; python3 film.py render $a $b /tmp/bo_$i.mp4 2>/tmp/bo_$i.log & done; wait
for i in 0 1 2; do echo "file /tmp/bo_$i.mp4"; done > /tmp/bol.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/bol.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/bonobo.mp4 && cp /tmp/bonobo.mp4 bonobo.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 bonobo.mp4
cat /tmp/bo_*.log
echo DONE
