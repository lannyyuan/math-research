#!/usr/bin/env bash
# PowerPoint-compatible WMV (Windows Media Video 8 + WMA2) from the rendered MP4s.
# WMV plays in every PowerPoint version on Windows without extra codecs.
set -euo pipefail
for f in "$@"; do
  out="${f%.mp4}.wmv"
  ffmpeg -hide_banner -loglevel error -y -i "$f" \
    -c:v wmv2 -b:v 5M -maxrate 7M -bufsize 10M -g 30 -pix_fmt yuv420p \
    -c:a wmav2 -b:a 160k -ar 44100 -ac 2 \
    "$out"
  echo "wrote $out ($(du -h "$out" | cut -f1))"
done
