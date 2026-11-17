cd /workspace/work/sneeze
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
python3 music.py > /tmp/s_m.log 2>&1 &
for i in 0 1 2 3; do a=$((i*360)); b=$(((i+1)*360)); python3 film.py render $a $b /tmp/s_$i.mp4 2>/tmp/s_$i.log & done; wait
for i in 0 1 2 3; do echo "file /tmp/s_$i.mp4"; done > /tmp/sl.txt
ffmpeg -y -v error -f concat -safe 0 -i /tmp/sl.txt -i bgm.wav -c:v copy -af loudnorm=I=-13:TP=-1.5 -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart /tmp/sneeze.mp4 && cp /tmp/sneeze.mp4 sneeze.mp4 && ffprobe -v error -show_entries format=duration,size -of csv=p=0 sneeze.mp4
cat /tmp/s_m.log /tmp/s_*.log
