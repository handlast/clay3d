cd /workspace/work/ufo
N=4620; S=1155
for i in 0 1 2 3; do a=$((i*S)); b=$(((i+1)*S)); python3 film2.py render $a $b /tmp/u2_$i.mp4 2>/tmp/u2_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/u2_$i.mp4"; done > /tmp/u2l.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/u2l.txt -i bgm2.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/ufo2.mp4 && cp /tmp/ufo2.mp4 ufo_fbi_v2.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 ufo_fbi_v2.mp4
cat /tmp/u2_*.log
