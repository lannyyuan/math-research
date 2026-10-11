---
name: ink-storybook-film
description: 把一篇儿童故事做成「水彩手绘风动画短片（MP4，4–5 分钟，字幕只取原文，自制配乐）」，再用同一套画面做成「单文件绘本网页（全文 + 插图 + 分镜总览，离线可读）」。适用于：用 Remotion + SVG 程序化画手绘动画、字幕必须逐字来自原文、给 6–8 岁识字孩子做分级阅读材料、需要可重新渲染的源工程。Use when asked to turn a children's story into a hand-drawn/watercolor animated short plus a single-HTML picture-book reader, with verbatim subtitles and reproducible source.
---

# 水彩手绘风故事短片 + 单文件绘本网页

参考实现：[`snow-lamp-film/`](../../snow-lamp-film/)（《雪地里的那盏灯》，4 分 50 秒，99 页绘本，一个 3.9 MB 的 HTML）。
本技能把“怎么做出来的”写成可以照着重做的方法；`templates/` 里是从参考实现里拎出来的通用工具和代码，`references/` 里是每一步的细节和踩过的坑。

> 有“角色设定图 + 封面”的任务（造型以设定图为准）：先读 `references/05-reference-sheet-sprites.md`（纸偶精灵 + 水彩背景的做法，参考实现 `lighthouse-light-film/`）。

## 什么时候用

- 用户给一篇儿童故事（文字稿），要一部**短动画**，风格是手绘/水彩/墨线，并且字幕要**只用原文**；
- 用户要**可重新渲染的源工程**（不是一次性导出的视频）；
- 用户想要把同一个故事做成**能读全文的绘本**（网页/PPT），并且和影片画面一一对应；
- 面向识字阶段的孩子：字大、停留久、字表覆盖可统计。

不适合：真人/3D/写实风、需要口型同步和对白配音的片子、长片（> 10 分钟，程序化手绘的渲染成本会爆）。

## 产出物

| 产出 | 文件 | 说明 |
|---|---|---|
| 成片 | `dist/<名>.mp4` | 1920×1080、30fps、H.264+AAC，约 60 MB（crf 27） |
| 源工程 | `src/ scripts/ story/ public/` | Remotion + React + SVG；`node scripts/...` 可重新渲染 |
| 分镜 PPT（可选） | `dist/<名>-storyboard.pptx` | 每条字幕一页，按场景分节，备注里有时间码 |
| 绘本网页 | `dist/<名>-book.html` | 单文件，图/字体/脚本全内联；封面→正文→结尾 + 目录 + 分镜总览 + 放映 |
| 识字表覆盖率（可选） | `analysis/literacy/` | 字幕 / 全文 与“识字 1300”之类字表的覆盖率对比 |
| 方法文档 | 本目录 | 你正在读的这份 |

## 先确认的前提（缺了才问，别的自己定）

1. 故事原文文件（`story/source.md`）：字幕和绘本全文都从它来，**不改一个字**；
2. 要几个情节点、必须按什么顺序（决定场景表）；
3. 目标时长（决定 `timeline.json` 的总长，默认 4:00–5:00）；
4. 配色约束（例如“暖色只留给灯、火、围巾”），以及参考图只能参考气质、不能照抄；
5. 沙箱里能不能下载 Chrome / 字体（本项目里 GitHub release 和 Chrome 商店被拦，npm / jsdelivr / PyPI 能用 → 字体用 npm 包 `lxgw-wenkai-webfont`，浏览器用本机 Chromium，见 `references/03-lessons-and-pitfalls.md`）。

## 总流程（10 步）

| # | 步骤 | 做什么 | 产物 / 检查 | 细节 |
|---|---|---|---|---|
| 1 | 拆情节 | 把必须的情节点排成场景表，每场 17–37 秒；挑每场最关键的原句当字幕 | `src/timeline.json`（唯一数据源） | 01 §1 |
| 2 | 字幕检查器 | 字幕必须是原文的连续片段；停留 ≥ 1.6 s + 0.3 s×字数；≤18 字/行、≤2 行；总长 240–300 s | `node scripts/check-subtitles.mjs` 全绿 | 01 §2 |
| 3 | 画法引擎 | 变宽墨线 + 起稿线 + 偏移水彩色块 + 蓝灰阴影层 + 纸纹；静态大背景烘焙成图 | `src/art/ ink.ts ArtView.tsx`，`public/baked/` | 01 §3 |
| 4 | 角色 | 纸偶式（部件 + 关节旋转 + 参数），每个角色一个组件 | `src/chars/*` | 01 §4 |
| 5 | 场景 + 镜头 | 视差层 + 关键帧缓动镜头，角色动作极少；固定地平线和脚底线，给字幕留出底部带 | `src/scenes/S*.tsx` | 01 §5 |
| 6 | 字体 + 配乐 | 开源字体裁成小文件；配乐用 numpy 自己合成 | `public/fonts/`，`public/audio/score.m4a` | 01 §6 |
| 7 | 渲染 | 按场景分段渲染 → 拼接 → 二次压缩并合音轨 | `bash scripts/render.sh` → `dist/*.mp4` | 01 §7 |
| 8 | 成片验收 | 抽 40+ 帧做联系表；暖色审计；字幕边界；音量 | 全部通过才算完 | 01 §8 |
| 9 | 绘本网页 | 出不带字幕的干净画面；补几张影片里没有的插图；分页；内联打包；真浏览器逐页核对全文 | `dist/*-book.html` | 02 |
| 10 | 交付 | 文件不大就直接发；大文件给 `gh` 命令；把用过的方法写回这份文档 | — | 04 |

## 快速上手（照着参考实现重做另一个故事）

```bash
# 0. 复制工程骨架
cp -r snow-lamp-film my-story-film && cd my-story-film && npm ci
pip install fonttools brotli pillow numpy            # 裁字体 / 合成配乐 / 图片转 WebP

# 1. 换故事：story/source.md、src/timeline.json、src/scenes/S*.tsx、角色
node scripts/check-subtitles.mjs                    # 字幕检查（要全绿）
npx remotion studio                                  # 边画边看

# 2. 成片
npm run bake && npm run music && npm run font
bash scripts/render.sh                               # → dist/*.mp4
python3 -I scripts/audit_warm.py out/audit           # 暖色审计

# 3. 绘本网页
npm run book:stills                                  # 干净画面 + 补充插图 → out/book_img/
python3 webapp/build.py                              # → dist/*-book.html
node webapp/qa.mjs --all                             # 真浏览器逐页核对 + 截图
```

`templates/` 里的东西怎么用：

- `templates/film-tools/` — 字幕调度/检查、渲染脚本、取帧脚本、暖色审计、配乐合成示例、PPT 分镜生成、`timeline.example.json`；
- `templates/engine/` — 画法引擎（`art/ink.ts`、`ArtView.tsx`、`geom.ts`）、镜头（`Stage.tsx`）、字幕组件、`Film.tsx`/`Root.tsx` 骨架、`Plates.example.tsx`（补充插图的写法）；
- `templates/webapp/` — 绘本网页的分页、配图、打包、字体裁剪、自动检查，`heroes.example.json` 是配图表示例。

> `templates/` 是从 `snow-lamp-film/` 同步过来的副本；改了工程里的工具后运行 `scripts/sync_from_project.sh` 同步。

## 质量门槛（全部满足才收工）

- [ ] 成片 4–5 分钟；每个必须的情节点都在，顺序对；
- [ ] 每条字幕都是原文的连续片段；字大、停留够；字幕完全在画面内；
- [ ] 抽帧联系表：风格统一；暖色只出现在约定的几处（审计脚本给出比例）；
- [ ] 角色不压在字幕带里；紧张的场面（落水、狼）不吓人；
- [ ] 绘本：全文逐页拼回去和原文**逐字相同**（`qa.mjs` 在真浏览器里做）；
- [ ] 绘本：桌面 / 平板竖屏 / 手机竖屏 / 手机横屏都没有横向溢出、没有控制台报错；
- [ ] 版权：字体开源（OFL），配乐自制，画面不照抄参考图；
- [ ] 文档：README 写清楚怎么重新渲染；这份技能文档更新到最新。

## 判断力备忘（不用问用户，自己定）

- 冲突时的取舍要写进 README“判断记录”：例如“红围巾只给主角，其他衣服全用冷色，与‘暖色只有三处’冲突时取后者”；
- 字幕太长就**缩成原文里更短的片段**，不要改写；字幕里的拟声字如果不在字表里，只在用户要求 100% 字表覆盖时才换片段；
- 绘本里影片没有的章节，用**同一套角色 + 同一套画笔**补插图（`Plates.tsx`），不要换风格；
- 每次改完先看图（联系表）再继续；不要在没看到画面的情况下堆参数。

## 目录

```
skills/ink-storybook-film/
├── SKILL.md                        ← 本文件
├── references/
│   ├── 01-film-pipeline.md         ← 做 MP4 的全过程（含参数、公式、验收）
│   ├── 02-webapp-pipeline.md       ← 做单文件绘本网页的全过程
│   ├── 03-lessons-and-pitfalls.md  ← 踩过的坑和修法（环境、渲染、版式、交付）
│   ├── 04-optional-deliverables.md ← 分镜 PPT、字表覆盖率、交付大文件
│   └── 05-reference-sheet-sprites.md ← 有“角色设定图 + 封面”时：抠精灵、图层状态、水彩背景、字幕只用原文、暖色审计
├── templates/{film-tools,engine,webapp}/
└── scripts/sync_from_project.sh
```
