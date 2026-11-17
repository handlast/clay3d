cd /workspace/work/milktea
S=1155
for i in 0 1 2 3; do a=$((i*S)); b=$(((i+1)*S)); python3 mfilm.py render $a $b /tmp/m_$i.mp4 2>/tmp/m_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/m_$i.mp4"; done > /tmp/ml.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/ml.txt -i bgm.wav -c:v copy -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/milktea.mp4 && cp /tmp/milktea.mp4 milktea.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 milktea.mp4
cat /tmp/m_*.log
