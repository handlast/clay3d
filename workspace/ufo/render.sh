cd /workspace/work/ufo
N=6120; P=4; S=$((N/P))
for i in 0 1 2 3; do a=$((i*S)); b=$(((i+1)*S)); python3 film.py render $a $b /tmp/uf_$i.mp4 2>/tmp/uf_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/uf_$i.mp4"; done > /tmp/ufl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/ufl.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/ufo.mp4 && cp /tmp/ufo.mp4 ufo_fbi.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 ufo_fbi.mp4
cat /tmp/uf_*.log
