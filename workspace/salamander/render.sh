cd /workspace/work/salamander
export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
NF=1398
for i in 0 1 2; do a=$((i*466)); b=$(((i+1)*466)); [ $b -gt $NF ] && b=$NF; python3 film.py render $a $b /tmp/sa_$i.mp4 2>/tmp/sa_$i.log & done; wait
for i in 0 1 2; do echo "file /tmp/sa_$i.mp4"; done > /tmp/sal.txt
cat /tmp/sa_*.log
echo DONE > /tmp/sa_done
