#!/bin/bash
# renders pending chunks two at a time until time budget is used
cd /workspace/work/border; export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
N=4575; C=30; L=$(( (N + C - 1) / C )); START=$(date +%s)
pending=(); for i in $(seq 0 $((C-1))); do [ -f seg/s$(printf %02d $i).done ] || pending+=($i); done
idx=0
while [ $idx -lt ${#pending[@]} ]; do
  el=$(( $(date +%s) - START )); [ $el -gt 1100 ] && break
  pids=()
  for k in $(seq 1 $(nproc)); do
    [ $idx -ge ${#pending[@]} ] && break
    i=${pending[$idx]}; idx=$((idx+1)); f0=$((i*L)); f1=$(( (i+1)*L )); [ $f1 -gt $N ] && f1=$N
    n=$(printf %02d $i)
    ( python3 film.py render $f0 $f1 seg/s$n.mp4 && touch seg/s$n.done ) & pids+=($!)
  done
  wait ${pids[@]}
done
ls seg/*.done 2>/dev/null | wc -l
