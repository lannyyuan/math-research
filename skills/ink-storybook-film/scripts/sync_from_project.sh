#!/usr/bin/env bash
# 把参考实现（snow-lamp-film）里最新的通用工具同步到本技能的 templates/（模板跟着工程走，避免文档和代码对不上）
set -euo pipefail
cd "$(dirname "$0")/../../.."
S=skills/ink-storybook-film; P=${1:-snow-lamp-film}
cp $P/webapp/{app.css,app.js,template.html,plan.py,build.py,subset_font.py,qa.mjs,.gitignore} $S/templates/webapp/
cp $P/webapp/heroes.json $S/templates/webapp/heroes.example.json
cp $P/src/schedule.mjs $P/scripts/{check-subtitles.mjs,audit_warm.py,render.sh,stills.mjs,scene_ranges.mjs,storyboard_plan.mjs,make_storyboard.mjs,book_stills.mjs,subset_font.py,contact.py,bake.mjs,make_music.py} $S/templates/film-tools/
cp $P/src/timeline.json $S/templates/film-tools/timeline.example.json
mkdir -p $S/templates/engine/art $S/templates/engine/fx
cp $P/src/art/{ink.ts,ArtView.tsx,geom.ts} $S/templates/engine/art/
cp $P/src/fx/{Stage.tsx,Subtitle.tsx,fonts.ts,Snowfall.tsx} $S/templates/engine/fx/
cp $P/src/scenes/kit.tsx $P/src/palette.ts $P/src/Film.tsx $P/src/Root.tsx $S/templates/engine/
cp $P/src/plates/Plates.tsx $S/templates/engine/Plates.example.tsx
cp $P/package.json $S/templates/engine/package.example.json
cp $P/tsconfig.json $S/templates/engine/
echo "已同步 $P → $S/templates"
