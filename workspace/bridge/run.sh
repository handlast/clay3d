#!/bin/bash
cd /workspace/work/bridge; export PYTHONPATH=/workspace/.pylib:$PYTHONPATH
N=7200; C=60; L=120; START=$(date +%s)
pending=(); for i in $(seq 0 $((C-1))); do [ -f seg/s$(printf %02d $i).done ] || pending+=($i); done
idx=0
while [ $idx -lt ${#pending[@]} ]; do
  el=$(( $(date +%s) - START )); [ $el -gt 820 ] && break
  pids=()
  for k in 0 1; do
    [ $idx -ge ${#pending[@]} ] && break
    i=${pending[$idx]}; idx=$((idx+1)); f0=$((i*L)); f1=$(( (i+1)*L ))
    n=$(printf %02d $i)
    ( python3 film.py render $f0 $f1 seg/s$n.mp4 2>seg/s$n.log && touch seg/s$n.done ) & pids+=($!)
  done
  wait ${pids[@]}
done
ls seg/*.done 2>/dev/null | wc -l
