#!/usr/bin/env bash
# Single render queue: renders + composes any video whose BLENDER_PROJECTS/<ID>/READY exists and whose FINAL is missing/outdated.
# Runs until no work remains for 4 consecutive hours. Log: PROJECT_TRACKER/render_queue.log
cd "$(dirname "$0")"
ROOT=..
LOG=$ROOT/PROJECT_TRACKER/render_queue.log
idle=0
while [ $idle -lt 240 ]; do
  did=0
  for ready in $(ls -tr $ROOT/BLENDER_PROJECTS/*/READY 2>/dev/null); do
    d=$(dirname $ready); id=$(basename $d)
    final=$ROOT/FINAL_VIDEOS/$id.mp4
    if [ ! -f "$final" ] || [ "$ready" -nt "$final" ]; then
      echo "$(date -u +%FT%TZ) START $id" >> $LOG
      if [ "$ready" -nt "$final" ] && [ -f "$final" ]; then rm -rf $ROOT/RENDERS/$id; fi
      python3 make_video.py $id timing >> $LOG 2>&1
      EGL_PLATFORM=surfaceless python3 make_video.py $id render --res 540 >> $LOG 2>&1
      python3 make_video.py $id compose >> $LOG 2>&1 && echo "$(date -u +%FT%TZ) DONE $id" >> $LOG || echo "$(date -u +%FT%TZ) COMPOSE_FAIL $id" >> $LOG
      touch -r $ready $final 2>/dev/null; touch $final 2>/dev/null
      did=1; break
    fi
  done
  if [ $did -eq 0 ]; then idle=$((idle+1)); sleep 60; else idle=0; fi
done
echo "$(date -u +%FT%TZ) QUEUE EXIT (idle)" >> $LOG
