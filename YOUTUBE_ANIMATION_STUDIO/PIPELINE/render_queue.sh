#!/usr/bin/env bash
# Single render queue: renders + composes any video whose BLENDER_PROJECTS/<ID>/READY exists and whose FINAL is missing/outdated.
# A failure writes BLENDER_PROJECTS/<ID>/FAILED (skipped until READY is touched again). Exits after 4 idle hours.
# Log: PROJECT_TRACKER/render_queue.log
cd "$(dirname "$0")"
ROOT=..
LOG=$ROOT/PROJECT_TRACKER/render_queue.log
idle=0
while [ $idle -lt 240 ]; do
  did=0
  for ready in $(ls -tr $ROOT/BLENDER_PROJECTS/*/READY 2>/dev/null); do
    d=$(dirname $ready); id=$(basename $d)
    final=$ROOT/FINAL_VIDEOS/$id.mp4
    # videos claimed by the GitHub Actions render farm are skipped here (PROJECT_TRACKER/ci_claimed.txt, one ID per line)
    [ -f $ROOT/PROJECT_TRACKER/ci_claimed.txt ] && grep -qx "$id" $ROOT/PROJECT_TRACKER/ci_claimed.txt && continue
    [ -f $d/FAILED ] && [ $d/FAILED -nt $ready ] && continue
    if [ ! -s "$final" ] || [ "$ready" -nt "$final" ]; then
      echo "$(date -u +%FT%TZ) START $id" >> $LOG
      if [ -s "$final" ]; then rm -rf $ROOT/RENDERS/$id; fi
      python3 make_video.py $id timing >> $LOG 2>&1
      EGL_PLATFORM=surfaceless python3 make_video.py $id render --res 540 >> $LOG 2>&1
      if ls $ROOT/QUALITY_CONTROL/$id/render_error_*.log >/dev/null 2>&1 && [ "$(find $ROOT/QUALITY_CONTROL/$id -name 'render_error_*.log' -newer $ready | head -1)" ]; then
        echo "$(date -u +%FT%TZ) RENDER_FAIL $id" >> $LOG; date > $d/FAILED; did=1; break
      fi
      if python3 make_video.py $id compose >> $LOG 2>&1 && [ -s "$final" ]; then
        python3 qc_check.py $id > /dev/null 2>> $LOG
        echo "$(date -u +%FT%TZ) DONE $id" >> $LOG
      else
        echo "$(date -u +%FT%TZ) COMPOSE_FAIL $id" >> $LOG; date > $d/FAILED
      fi
      did=1; break
    fi
  done
  if [ $did -eq 0 ]; then idle=$((idle+1)); sleep 60; else idle=0; fi
done
echo "$(date -u +%FT%TZ) QUEUE EXIT (idle)" >> $LOG
