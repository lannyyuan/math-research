#!/usr/bin/env bash
# Key-frame self check: grabs one frame per storyboard beat from a rendered MP4 and tiles them
# into a contact sheet for a visual review (composition, readability, no clipping).
#   bash scripts/keyframes.sh out/gas-car_narrated.mp4 out/keyframes.jpg
set -euo pipefail
in="$1"
out="${2:-out/keyframes.jpg}"
tmp="$(mktemp -d)"
# seconds: title, tank label, fuel flow, engine label, 砰 spark, pistons, crank+extras,
# gearbox 1st, power to wheels, radiator, oil, exhaust, exploded+labels, counter done, merged, end card
times=(1.0 3.4 6.5 15.0 18.85 20.5 24.8 30.5 33.6 41.5 44.5 48.0 57.0 59.8 64.5 69.5)
i=0
for t in "${times[@]}"; do
  ffmpeg -hide_banner -loglevel error -y -ss "$t" -i "$in" -frames:v 1 -q:v 3 "$tmp/$(printf %02d $i).jpg"
  i=$((i + 1))
done
montage "$tmp"/*.jpg -tile 4x4 -geometry 640x360+6+6 -background "#22324A" "$out"
rm -rf "$tmp"
echo "wrote $out"
