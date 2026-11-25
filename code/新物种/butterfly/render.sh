#!/bin/bash
# 《蝴蝶》render/mux.  Frames: `timeout 118 flock -w 15 /tmp/render.lock python3 rchunk.py $(date +%s)` (repeat until ALL CHUNKS DONE)
#   ./render.sh mux     concat chunks + BGM + 云健 VO (sidechain duck, loudnorm -15 LUFS) -> /tmp then copy back
#   ./render.sh muxnv   no-voice version (BGM only)
#   ./render.sh small   compressed *_s.mp4 versions (crf 27) when > 60 MB
#   ./render.sh check   frames / duration / loudness
cd /workspace/work/butterfly
export PYTHONPATH=/workspace/.pylib
AF="[2:a]aresample=44100,pan=stereo|c0=c0|c1=c0,volume=1.6,asplit=2[vk][vm];[1:a]aresample=44100,volume=0.8[bg];[bg][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[duck];[duck][vm]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]"
DURS=$(python3 -c "from cues import DUR; print(DUR)")
probe() { ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -show_entries format=duration,size -of csv=p=0 "$1"; }
case "$1" in
  mux)
    python3 rchunk.py list || exit 1
    ffmpeg -y -v error -f concat -safe 0 -i /tmp/bfl.txt -c copy /tmp/bf_video.mp4 || exit 1
    ffmpeg -y -v error -i /tmp/bf_video.mp4 -i bgm.wav -i vo.wav -filter_complex "$AF" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t $DURS -movflags +faststart /tmp/butterfly.mp4 && cp /tmp/butterfly.mp4 butterfly.mp4
    probe butterfly.mp4 ;;
  muxnv)
    ffmpeg -y -v error -i /tmp/bf_video.mp4 -i bgm.wav -filter_complex "[1:a]aresample=44100,loudnorm=I=-15:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -t $DURS -movflags +faststart /tmp/butterfly_novo.mp4 && cp /tmp/butterfly_novo.mp4 butterfly_novo.mp4
    probe butterfly_novo.mp4 ;;
  check)
    for f in butterfly.mp4 butterfly_novo.mp4 butterfly_s.mp4 butterfly_novo_s.mp4; do [ -f $f ] || continue; echo "$f $(probe $f)"; ffmpeg -nostats -i $f -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1; done ;;
esac
