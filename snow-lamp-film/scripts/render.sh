#!/usr/bin/env bash
# 渲染成片：按场景分段渲染（可只重渲某一场：删掉 out/parts/<场景>.mp4 再运行，或 FORCE=1 全部重来），
# 然后拼接并合上配乐，输出 dist/snow-lamp.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
BROWSER="${REMOTION_BROWSER:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}"
mkdir -p out/parts dist
[ -f public/audio/score.m4a ] || { python3 -I scripts/make_music.py && ffmpeg -y -loglevel error -i public/audio/score.wav -c:a aac -b:a 160k public/audio/score.m4a; }
node scripts/scene_ranges.mjs > out/ranges.txt
: > out/parts.txt
while read -r id a b; do
  if [ ! -f "out/parts/$id.mp4" ] || [ -n "${FORCE:-}" ]; then
    echo "== 渲染 $id  帧 $a-$b"
    npx remotion render src/index.ts Film "out/parts/$id.mp4" --frames="$a-$b" --muted --codec=h264 --crf=18 \
      --jpeg-quality=96 --concurrency="${CONC:-4}" --browser-executable="$BROWSER"
  fi
  echo "file '$PWD/out/parts/$id.mp4'" >> out/parts.txt
done < out/ranges.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i out/parts.txt -c copy out/video-silent.mp4
# 第二段编码：分场景的中间文件用 crf 18（约 300 MB），成片再压到约 50 MB（画面几乎看不出差别），并合上配乐
ffmpeg -y -loglevel error -i out/video-silent.mp4 -i public/audio/score.m4a -c:v libx264 -crf "${FINAL_CRF:-27}" -preset medium \
  -pix_fmt yuv420p -c:a copy -shortest -movflags +faststart dist/snow-lamp.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 dist/snow-lamp.mp4
