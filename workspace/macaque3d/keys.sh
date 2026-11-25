#!/bin/bash
# 关键帧批量测试（后台）：./keys.sh t1 t2 ...
cd /workspace/work/macaque3d; export PYTHONPATH=/workspace/.pylib
flock /tmp/render.lock python3 film.py test "$@" > /tmp/mq_keys.log 2>&1
echo ALLDONE >> /tmp/mq_keys.log
