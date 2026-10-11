# The Lighthouse Light — 3~5 分钟动画短片（英文字幕）

把英文儿童故事《The Lighthouse Light》做成的动画短片：**4 分 38 秒、1920×1080、30 fps、全片英文字幕**，观众 6~8 岁。
画风是手绘墨线 + 透明水彩 + 纸纹；夜空靛蓝、雪地白色带蓝灰阴影；暖色只留给灯塔光柱、港口和船上的灯、Bolts 的眼睛、Hazel 的红围巾、Comet 的红项圈。

- 成片：`dist/lighthouse-light.mp4`（H.264 + AAC）
- 源工程（Remotion + 一套 Python 水彩笔刷）：整个目录；一条命令重新渲染：`npm run render`

## 技术方案

| 部分 | 做法 |
|---|---|
| 角色 | 参考图（`ref/character-sheet.png`）按“和纸张底色的色差”分割成透明 PNG 精灵（5 个角色、正面 + 侧面），锚点在脚底。Bud 的三种头饰（棒球帽 / 毛线帽 / 光头）是把设定图里的帽子单独抠成图层，头发另补；Bolts 的“眼睛熄灭”版、Pebbles 只露头的版本也是图层。`scripts/extract_sprites.py → make_bud_variants.py → make_more_sprites.py → sprite_meta.py` |
| 背景 | 自己写的水彩笔刷（`scripts/paint/pt.py`：不规则边缘的水彩色块、可变粗细的墨线、排线、纸纹颗粒）画成 2~3 层视差图：`bg_s1.py`（村子）、`bg_lighthouse.py`、`bg_workshop.py`、`bg_town.py`、`bg_wild.py`（农场/河/悬崖）、`bg_lamp.py`（灯室、发电机房）、`bg_night.py`（海湾、码头）、`bg_home.py`（客厅、卧室）、`props*.py`（雪人、Mrs Mallet、Grandad、Dad、Mum、船……） |
| 动画 | Remotion（React）：慢推慢移的视差镜头（`src/fx/Stage.tsx`）、纸偶式的轻微呼吸/晃动（`Sprite.tsx`）、雪、光晕和光柱（`Light.tsx`）。每个场景一个组件（`src/scenes/S0..S10.tsx`），动作按字幕出现的时间对齐 |
| 字幕 | `src/timeline.json` 只放故事原文里的句子；`npm run check` 验证：每条都是原文的连续片段（统计附录不用）、停留时间 ≥ 1.3 s + 0.55 s×词数、≤ 2 行、总时长 3~5 分钟。`scripts/check_subtitle_fit.py` 用真字体量宽度，保证不出画面。字体 Andika（SIL OFL 1.1，随工程带许可文件） |
| 配乐 | `scripts/make_music.py` 用 numpy 自己合成（无任何外部素材）：冬夜小曲 + 灯塔动机（D–F♯–A–F♯，音乐盒音色），大灯亮起时全曲最满 |
| 渲染 | `scripts/render.sh`：分场景渲染（可只重渲某一场：删掉 `out/parts/<场景>.mp4`）→ 拼接 → 合上配乐 |

## 前后一致（全片只在一处决定）
- Bud 的头饰：`src/scenes/cast.tsx` 的 `<Bud head="cap|hat|bare" pocket>`。第 1~2 章戴棒球帽，第 2 章把它戴到雪人头上（S2）；农场里得到毛线帽（S5），Pebbles 爬进去后帽子装进口袋，从此 Bud 不戴帽子；悬崖上帽子掉出口袋又被 Hazel 救回口袋（S7）。
- Bolts 的眼睛：`<Bolts eyes={0..1}>`。S3 亮起；S8 给出电池后熄灭、一动不动；S10 早上 Mrs Mallet 装上新电池才亮。
- 灯塔：S8 Hazel 换灯泡（没反应）→ 发电机装上电池 → 大灯才亮；在此之前所有镜头里灯室都是黑的。

## 检查
```bash
npm run check                       # 字幕：原文片段 / 停留时间 / 总时长
python3 -I scripts/check_subtitle_fit.py   # 字幕宽度
npm run stills -- "Film:s8+24" --scale=0.5 # 看某一帧（场景id+场景内秒数）
npm run audit                       # 暖色审计：只出背景和光（不画角色），暖色像素标成洋红
```

## 绘本网页（单文件，英文，离线可读）
- 成品：`dist/lighthouse-light-book.html`（约 4.5 MB，图 / 字体 / 脚本全内联）：封面 → 135 页（全文 + 配图）→ 结尾；目录、分镜总览（46 个影片场景 + 补充插图）、放映模式、字号 / 纸色主题 / 朗读 / 全屏。
- 全文来自 `story/source.md`，不改一个字；每条影片字幕所在的页用该字幕的**无字幕干净画面**，影片没覆盖的章节（城里、城堡及城堡里面、游乐场、篷车、梦、春天）用 `src/plates/Plate.tsx` 补了同一画风的插图（背景在 `scripts/paint/bg_book.py`）。
- “Watch this scene in the film”：把 `lighthouse-light-720p.mp4`（或 `lighthouse-light.mp4`）放在 HTML 同一个文件夹里就能跳到那一幕；没有影片文件时页面会给出提示，其它功能不受影响。
- 重新生成（先装好 Chromium / Remotion，见上）：
```bash
npm run book:stills   # 分镜计划 + 干净画面 + 补充插图 → out/book_img/
npm run book          # 分页（webapp/plan.py）+ 配图（webapp/heroes.json）+ 全文校验 + 内联打包 → dist/lighthouse-light-book.html
npm run book:qa       # 真浏览器：逐页拼回全文逐字比对、溢出、控制台、多尺寸截图（out/book_qa/）
```
- 配图表 `webapp/heroes.json`（没有字幕的页按章节顺序取图，`fx/fy/z` 是取景中心和放大倍数）；每页行数上限在 `webapp/plan.py` 顶部（`CPL / CAP / SOFT_MAX`）。
- 注意：影片字幕的顺序必须和故事原文一致（`plan.py` 按故事顺序给字幕找锚点）。S3 里 “A long journey is better with a friend.” 一句原先排在 “The robot's eyes lit up” 之后，已改回原文顺序（`src/timeline.json` + `src/scenes/S3.tsx` 的动作时间随之调整）。
