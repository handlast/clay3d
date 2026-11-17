cd /workspace/work/muppet
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1425
for i in 0 1 2; do a=$((i*475)); b=$(((i+1)*475)); [ $b -gt $NF ] && b=$NF; python3 film.py render $a $b /tmp/mp_$i.mp4 2>/tmp/mp_$i.log & done; wait
for i in 0 1 2; do echo "file /tmp/mp_$i.mp4"; done > /tmp/mpl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/mpl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/muppet.mp4 && cp /tmp/muppet.mp4 muppet.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 muppet.mp4
cat /tmp/mp_*.log
echo DONE
