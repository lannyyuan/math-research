#!/usr/bin/env bash
# 重画全部背景画板（scripts/paint/bg_*.py），输出到 public/bg/ 并写 manifest.json
set -euo pipefail
cd "$(dirname "$0")/paint"
python3 make_paper.py
for f in bg_title.py bg_props.py bg_village.py bg_*.py; do
  [ "$f" = "bg_test.py" ] && continue
  echo "== $f"; python3 "$f"
done
