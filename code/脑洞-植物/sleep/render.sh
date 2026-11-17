cd /workspace/work/sleep
for i in 0 1 2 3; do a=$((i*360)); b=$(((i+1)*360)); python3 film.py render $a $b /tmp/s_$i.mp4 & done; wait
for i in 0 1 2 3; do echo "file /tmp/s_$i.mp4"; done > /tmp/sl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/sl.txt -i bgm.wav -c:v copy -af loudnorm=I=-13:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/sleep.mp4 && cp /tmp/sleep.mp4 no_sleep_11days.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 no_sleep_11days.mp4
