#!/bin/bash
cd /workspace/work/clownfish3d; export PYTHONPATH=/workspace/.pylib
while ! grep -q TESTS_DONE tests_log.txt; do sleep 5; done
run() { flock /tmp/render.lock timeout 115 python3 film.py faces "$@"; }
run 1.6 14.0 17.0 57.5
run 1.0 1.07 1.13 1.2 1.27 1.33
echo TESTS2_DONE
