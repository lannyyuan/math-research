# 04 · 可选交付：分镜 PPT、字表覆盖率、交付大文件

## 1. 分镜 PPT（一条字幕一页）

```bash
node scripts/storyboard_plan.mjs        # → out/storyboard_plan.json（片头 1 张 + 每条字幕 1 张，取字幕停留 70% 处）
node scripts/stills.mjs …                # 按计划取帧（带字幕的成片画面，scale=1）→ 转 JPEG 放 out/ppt_jpg/NN.jpg
node scripts/make_storyboard.mjs         # → dist/<名>-storyboard.pptx（41 页，约 13 MB）
```

- pptxgenjs：`LAYOUT_WIDE`（13.333 × 7.5 英寸）；每页一张全幅图，背景深靛蓝；
- **按场景分节**（`addSection` + `sectionTitle`），备注里写“分镜号 / 场景 / 时间码 / 字幕”，图有 `altText`；
- 数“有一行字的画面有多少张”= 字幕条数 + 片头 = 41；≤50 页就直接生成交付；
- 验收：pptx 技能的 `scripts/office/validate.py` + `soffice.py --convert-to pdf` 渲染抽检几页；
- 想更精致的版式（章节页、统计页）再做；本项目的 PPT 就是“画面册”，因为字幕已经在画面里。

> 网页绘本里的“分镜总览 + 放映”就是这份 PPT 的网页版，且每张都能跳到对应的书页。

## 2. 识字表覆盖率分析（`analysis/literacy/`）

场景：用户给一份识字表（如《幼儿识字 1300 字》的 PDF），要统计字幕/全文覆盖了多少。

1. **把表变成文字**：PDF 是图片 → OCR + 人工转写（见 03 的“识字表”一节）；输出 CSV（UTF-8 BOM，Excel 直接开）和 MD；
2. **三个口径**（都只算汉字）：
   - **字种覆盖率** = 本维度用到的不同字里，有多少在表内；
   - **字次覆盖率** = 本维度的所有字次里，有多少在表内；
   - **表被覆盖率** = 表里有多少个字被本维度用到；
3. **对比维度**：影片字幕 / 分镜 PPT 全部文字 / 故事原文全文；再按场景、按 PPT 页逐项列出，并单独列出“表外字”和“表里有但原文没用到的字”；
4. 参考结果（《雪地里的那盏灯》 vs 识字 1300）：表 1300 格、1293 个不同的字（7 个字出现两次）；字幕 403 字次 / 160 字种，159 字种在表内（99.4%），只有“啪”在表外，覆盖表的 12.3%；全文 11,356 字次 / 1293 字种，1285 在表内（99.4%），覆盖表的 99.4%，表外 8 个（啪嗡圈洲滨系绍铺），表里没用到 8 个（坪吾质稀稠与革丹）；
5. 想让字幕 100% 落在表内：把含“啪”的那条缩成原文里更短的片段（“破了！”），**只重渲那一场**（删 `out/parts/s4-river.mp4` 再 `npm run render`）。

## 3. 交付大文件

| 情况 | 做法 |
|---|---|
| 文件 ≤ 30 MiB（绘本网页 3.9 MB、PPT 13 MB、CSV/MD） | 直接用 `SendUserFile` 发 |
| 成片 61 MB > 30 MiB | ① 推到仓库；② 另发一个 720p 小副本：`ffmpeg -i dist/x.mp4 -vf scale=1280:-2 -c:v libx264 -crf 29 -c:a aac -b:a 96k -movflags +faststart x-720p.mp4`（约 21 MB）；③ 给 `gh` 命令拉原版 |
| 用户问“怎么下载” | 给完整命令（下面） |

```bash
# 只下载成片（单文件）
gh api -H "Accept: application/vnd.github.raw" \
  "repos/OWNER/REPO/contents/snow-lamp-film/dist/snow-lamp.mp4?ref=BRANCH" > snow-lamp.mp4

# 把整个项目目录（源工程 + 成片 + 绘本 + PPT）拉回来：只要这一个文件夹
gh repo clone OWNER/REPO -- --branch BRANCH --depth 1 --filter=blob:none --sparse
cd REPO && git sparse-checkout set snow-lamp-film skills/ink-storybook-film
```

- 大文件（>25 MB）走 `contents` 接口要用 `raw` 的 Accept 头；
- 绘本网页和影片放在**同一个文件夹**，网页里的“看影片里的这一幕”就能直接播放。

## 4. 提交与分支

- 在任务指定的分支上开发和推送（`git push -u origin <branch>`）；**不要**自己开 PR，除非用户明确要求；
- 提交说明写清楚做了什么；产物（`dist/*.html`、`dist/*.pptx`、`dist/*.mp4`）可以入库，中间文件（`out/`、`webapp/out/`、`node_modules/`）不入库（`.gitignore`）。
