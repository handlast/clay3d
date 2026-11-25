cd /workspace/work/drex
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
for i in 0 1 2 3; do a=$((i*353)); b=$(((i+1)*353)); python3 film.py render $a $b /tmp/dx_$i.mp4 2>/tmp/dx_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/dx_$i.mp4"; done > /tmp/dxl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/dxl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/drex.mp4 && cp /tmp/drex.mp4 drex.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 drex.mp4
cat /tmp/dx_*.log
