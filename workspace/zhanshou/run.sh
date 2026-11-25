#!/bin/bash
cd /workspace/work/zhanshou; export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
N=1650; L=55; C=30; START=$(date +%s)
worker(){ while true; do
  el=$(( $(date +%s) - START )); [ $el -gt 900 ] && return
  i=""; for k in $(seq 0 $((C-1))); do n=$(printf %02d $k); if [ ! -f seg/s$n.done ] && mkdir seg/s$n.lock 2>/dev/null; then i=$k; break; fi; done
  [ -z "$i" ] && return
  n=$(printf %02d $i); python3 film.py render $((i*L)) $(((i+1)*L)) seg/s$n.mp4 2>seg/s$n.log && touch seg/s$n.done; rmdir seg/s$n.lock
done; }
worker & worker & wait
ls seg/*.done 2>/dev/null | wc -l
