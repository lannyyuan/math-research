# 小石猴点灯 — 手绘水彩动画短片 + 单文件绘本网页

> ✅ **已完成**：成片 `dist/xiaoshihou-dian-deng.mp4` 和绘本网页 `dist/xiaoshihou-book.html` 都已出。接手/续做的交接说明见 [`HANDOVER.md`](HANDOVER.md)（里面“没做”的清单现已补完，仅作历史记录）。

把儿童故事《小石猴点灯》做成的 4~5 分钟手绘水彩动画短片（给 6~8 岁的孩子看），以及一个中文、单文件、离线可读的绘本网页（加长版全文）。

- 成片：`dist/xiaoshihou-dian-deng.mp4`（1920×1080，30 fps，H.264 + AAC，**4 分 55 秒（295.0 s）**，约 72.7 MB；`npm run render` 重渲，不进 git）
- 绘本网页：`dist/xiaoshihou-book.html`（单个 HTML，5.3 MB，186 页，57 张图——40 张影片画面 + 16 张补充插图 + 封面；图片 / 字体 / 脚本全部内联，离线可读；全文 20573 字，和原文逐字相同）
- 源工程（Remotion + 一套自己写的水墨水彩笔法）：整个目录，下面写了怎么重新渲染

## 美术基准
- 封面 `ref/cover.png`（画风、色调、留白的基准）、角色与道具设定表 `ref/character-sheet.png`（造型的基准）。
- 角色（石娃、龟甲、奶奶、大鱼、老龟、老龙）和宝物（宝珠、雪铃、火种、金鼓、银针）是直接从设定表里抠出来的透明精灵（`scripts/extract_sprites.py`，Lab 色差分割 + 填洞 + 去白边），按设定表的比例摆；
  设定表上没有的人物（老婆婆、小姑娘、牧人和马、卫士、国王、守天门的神、凤凰、孩子们……）和所有背景，是用 `scripts/paint/` 里的水墨水彩笔法（松动的墨线、透明水彩色块、飞白、皴擦、宣纸纹理）新画的。
- 夜色色板（第一部到灯亮之前）：深夜 #121A2E、靛蓝 #1E2A44、灰蓝 #5A6B86、纸白 #EFE8D8、墨 #2A2622。
- 光是叙事的主线：黑夜里宝珠只照亮周围三尺，光照到哪里，那里才有颜色，其余都沉在靛蓝里。实现：整个世界画两遍——夜色版（靛蓝）和“光照版”（柔和的自然色），光照版用一个跟着宝珠走的圆形软蒙版叠在夜色版上（`src/fx/Light.tsx` 的 `Lit`）。
- 灯亮之后（第六部后半到尾声）解除夜色色板，整体转成晨光，红霞 #E9A38C 和紫霞 #9C86B8 只在这时出现。

## 怎么重新渲染
```bash
npm install                                  # 装 Remotion 等依赖（需要网络）；浏览器用本机 Chromium
pip install numpy scipy opencv-python scikit-image pillow fonttools brotli
npm run check                                # 字幕检查：原文片段 / 行宽 / 停留时间 / 总时长
npm run font                                 # 裁字幕用的霞鹜文楷（OFL）→ public/fonts/WenKai-subtitle.woff2
npm run sprites                              # 设定表 → 透明精灵（含老龙慈眉修图、龟甲裂纹、夜色版）
npm run plates                               # 全部背景画板（scripts/paint/bg_*.py）
npm run music                                # 自己合成的配乐（古筝、箫、木鱼、风铃、铜铃、鼓）→ public/audio/score.m4a
npm run render                               # 分场景渲染 → 拼接 → 合上配乐 → dist/xiaoshihou-dian-deng.mp4
```
只重渲某一场：删掉 `out/parts/<场景>.mp4` 再 `npm run render`（`FORCE=1` 全部重来；`CONC=8` 改并发数）。看某一帧：`npm run stills -- "Film:s1+13,s5+30" --scale=0.5`（场景 id 前缀 + 场景内秒数）。

**Windows（Git Bash）备注**（本片就是在 Windows 11 上重渲出来的）：
- `REMOTION_BROWSER` 指向一个 headless chromium（脚本里的默认值是 Linux 路径），例如 Playwright 自带的 `…\ms-playwright\chromium_headless_shell-NNNN\chrome-headless-shell-win64\chrome-headless-shell.exe`。
- 要有 `python3` 命令：建一个 venv，把 `python.exe` 复制成 `python3.exe` 并放到 PATH 最前；`ffmpeg`/`ffprobe` 也在 PATH 里。
- Python 脚本读写中文文件，要用 UTF-8：`python3 -X utf8 -I scripts/make_music.py`、`python3 -X utf8 -I webapp/build.py`（`-I` 会忽略 `PYTHONUTF8` 环境变量，所以写 `-X utf8`）。`scripts/paint/` 下的板子/精灵脚本**不能**加 `-I`（它们要导入同目录的模块）。
- 绘本网页自检要 `playwright`（`npm i --no-save playwright`）和 `CHROME=…\chrome.exe`。

## 字幕
- `src/timeline.json` 是唯一数据源：每场的长度和每条字幕的文字；出现时间由 `src/schedule.mjs` 算（渲染、检查、配乐共用）。
- 字幕只取故事原文（`story/film_source.txt`）正文里的连续片段，一个字都不改；行首是 `#` 或 `【` 的是批注/画面提示，不能当字幕。最多两行，每行 ≤ 18 个字，停留 ≥ 1.5 秒 + 0.3 秒/字（标点也算一个字，再加 0.2 秒余量）。
- **唯一的例外**：结尾字幕“下一个故事，等你来讲。”——任务书指定它是最后一句字幕，但它在原文里只出现在 `【44】` 的画面提示行里（正文里没有）。时间线里用 `"exception": true` 标出，检查器会核对它确实一字不差地出现在原文里，并且只允许这一条例外。
- 字幕在画面底部居中，半透明墨色底带，霞鹜文楷（SIL OFL 1.1）。底带从画面 y=845 起：所有角色的脚底、关键动作都在这条线以上（镜头用 `atg()` 保证脚底落在 y≈820），`npm run audit:band` 逐条字幕核对。

## 风格取舍（任务书要求记录）
- **暖色的例外**：只有宝珠的光（#F3D98A）、龟甲的眼睛（火星色）、篝火和火种（#E8873A）、奶奶的红头绳和红布包（#B8382E）、小姑娘的红裙（面积很小）是暖色。其他一切（金鼓、国王的衣服、神的金光、窗里的光、灯、屋顶的草）都降了饱和度，往灰金/土黄/纸白走：设定表上的金鼓是高饱和的金黄 + 红穗子，抠出来后降到 46% 的饱和度；窗里的光画成纸白冷光。
- **暖色例外的补充**：除上面列的之外，只有两处额外的暖色——片头第一部开头那一小段“灯还亮着”的白天山谷（地面是沙土色，灯一灭就转成夜色），以及灯亮之后（第六部后半的晨光村口、尾声）的红霞 #E9A38C / 紫霞 #9C86B8；火山口的火苗（#E8873A）只画在火山口和山石边，克制。`npm run audit` 的结果就是这样：夜色段里洋红（暖色）像素只落在篝火、火种、红布包、红裙和光照里的木墙上。
- **人物的肤色**：石娃、奶奶的脸和手保留设定表上的肤色（夜色版里已降到灰暖），这是“人”本身的颜色，不算光源；在夜色版里整体压进靛蓝色带。
- **龟甲的大小**：设定表上画大了（石娃的 0.4 倍），影片里统一缩成石娃身高的 0.135 倍（三寸、手掌大），由 `src/scenes/cast.tsx` 的 `Houzi` 一处决定（`HOUZI_RATIO`）；特写镜头里靠推近让它看得清。
- **老龙**：设定表上的老龙眉头紧、眼神凶，任务书要求“慈眉，眼皮半垂，像刚睡醒，不能凶”，所以抠图之前在设定表上重画了眼皮、眉毛和嘴角（`scripts/retouch.py`），龟甲胸前也补了一道细裂纹。
- **云路不是筋斗云**：守天门的神指向远方，云海上显出一条由象牙色云石板连成的路，石娃骑着牧人送的马沿路走（马始终是一匹朴素的灰褐草原马，不是金色神骏）；没有金箍、虎皮裙、筋斗云、桃子特写。桃子没有进画面。
- **九层砖塔**：塔严格九层，数得清；城是中式城墙加城楼，没有尖顶塔楼。
- **字幕与图的分工**：字幕只引原文，画面补足原文里没有字幕的情节（比如落水、爬塔、四季轮转）。
- **结尾字幕是唯一的例外**：任务书指定最后一句字幕是“下一个故事，等你来讲。”，它在原文里只出现在 `【44】` 的画面提示行，不在正文里。我们照任务书做，在 `timeline.json` 里用 `"exception": true` 标出，`npm run check` 核对它确实一字不差地出现在原文里、且只允许这一条。
- **没有画的**：任务书里可选的虾兵（`shrimp_guard`）、挑担人（`villager_carry`）、麻袋、竹竿、绳圈、长枪单独精灵都没做（卫士精灵自带长枪；这些在片里用不到）。牧人先生那段（第五分里“戴帽背书柜的先生”）影片里没有，绘本里有文字、无图。
- **绘本章节顺序**：绘本网页用的是“加长版精简”文本（`story/book_source.txt`），文件里各分的出现顺序是乱的，网页按“分”的编号排序：第一、第三~第六分 → 增补一~四（放在第六分之后、第七分之前）→ 第七分 ~ 第十四分 → 第十六分 ~ 第二十一分。**原文本身没有“第二分”和“第十五分”，不补。** 顺序在 `webapp/plan.py` 顶部的 `ORDER`，一行就能改。
- **绘本配图**：第一~第六分用影片的干净帧（`cue/01–40`，`node scripts/book_stills.mjs --only=cue`，不带字幕），第七分起和四个增补用 16 张补充插图（`plate/*`，`src/plates/Plate.tsx`：现成背景板 + 现成人物精灵拼的小场景，`--only=plate`）。图和段落的对应在 `webapp/heroes.json`（`at` 写小标记或 `#段号`），换图/换取景只改这张表，再 `python3 -X utf8 -I webapp/build.py`。

## 目录
```
src/                 Remotion 工程：timeline.json（时间线）、schedule.mjs、Film.tsx、scenes/S0..S7.tsx（八段）、fx/（镜头、光、水墨转场、水、四季、灯光……）、plates/Plate.tsx（绘本补充插图 16 张）
scripts/             检查/渲染/抽帧/审计脚本、extract_sprites.py（设定表→精灵）、make_music.py（配乐）、paint/（水墨水彩笔法 + 各背景画板 + PLATES.md 画板清单）
public/              字体、配乐、精灵（sprites）、背景（bg）、片名书法字（props，取自封面）
story/               film_source.txt（影片字幕原文）、book_source.txt（绘本加长版全文）
ref/                 封面、设定表
webapp/              绘本网页：plan.py（分页）、build.py（打包）、app.js/css、qa.mjs（真浏览器核对）
dist/                成品
```

## 检查（交付前的自检）
```bash
npm run check                          # 字幕：原文片段 / 行宽 / 停留时间 / 总时长 4:30~5:00
npm run audit                          # 暖色审计：只出背景和光，暖色像素标成洋红，核对是不是只在允许的地方
npm run audit:band                     # 字幕带审计：每条字幕三个时刻，有角色/动作压进字幕带的会列出
node scripts/qa_frames.mjs dist/xiaoshihou-dian-deng.mp4 out/qa   # 从成片按字幕抽帧 → 联系表
```

## 自检结果（成片 + 网页）
- `npm run check`：40 条字幕全是原文片段（含 1 条指定例外），行宽/停留时间达标，总长 295 s = 4:55。
- 联系表：`node scripts/qa_frames.mjs dist/xiaoshihou-dian-deng.mp4 out/qa` 抽 40 帧（每条字幕一帧），六部情节（天黑了 → 河边搭桥 → 海底宝珠 → 雪铃 → 金鼓 → 点灯 → 尾声）都在，字幕清楚，龟甲始终是手掌大。
- `npm run audit`（暖色）：夜色段里暖色只在允许处（见上）。
- `npm run audit:band`（字幕带）：把能抬的都抬了（老龙脚下的影子、撬棍和青石的底边、大鱼的嘴、尾声树下的影子）；120 个检查时刻只剩 1 个提示（第二部“贴身上，水便不敢近你”，64 个像素的水里雪花粒子），不是角色。
- 声音：平均 −18.1 dB，峰值 −0.5 dB，不削波。
- 绘本网页：全文逐字相同（20573 字）；桌面 1440×900 没有需要滚动的页；无控制台报错；章节顺序按 `ORDER`。

## 点字看拼音、听发音（绘本网页）
- **用法**：鼠标放在正文（和章名）里任意一个汉字上 → 字上方弹出带声调的拼音；**点一下**用真人录音念出来。触屏：轻点 = 显示并发声。设置里可整体关闭，或打开“悬停即发声”（默认关）。
- **读音在构建期标好**（`webapp/pinyin.py`：`pypinyin` 带词语上下文 + `webapp/pinyin_overrides.json` 规则表），网页里没有转换引擎，只查表。助词“得/着/地”、“落/长/种/背/看/担”等 pypinyin 默认会错的字都在规则表里校正过；`python3 -X utf8 webapp/pinyin.py --review` 重写 `webapp/pinyin_review.md`（全书 53 个多音字 + 227 处规则改写的上下文，供人工复核）。单字试标：`python3 -X utf8 webapp/pinyin.py "他走得快"`。
- **音频：同音只存一条，一共 846 个文件，存在 `webapp/pinyin_clips/{音节}{声调}.mp3`（如 `zhang3.mp3`），随仓库提交。** 全书 17,180 个汉字只用到 847 种“音节+声调”，846 条共 ≈3.2 MB（每条 ≈4 KB），构建时内联进 HTML（`dist/xiaoshihou-book.html` 因此约 9.7 MB，仍是单文件、`file://` 离线可用）。**有这个库，构建不需要 ffmpeg、Pinyin_Drill 目录和网络**；库里缺的才按来源现做并存进库（要一起提交）：`Pinyin_Drill_P0` 的真人录音（807 条，只读，目录可用环境变量 `PINYIN_DRILL_DIR` 改）+ 上游 [hugolpz/audio-cmn](https://github.com/hugolpz/audio-cmn)（同一录音者、固定 revision）的 18 条。`webapp/pinyin_audio_manifest.json` 记“音节 → 来源 + 原始 SHA-256 + 库文件 SHA-256”，库文件被改动构建会报警。处理：裁首尾静音 → 单声道 22.05 kHz 32 kbps MP3。署名与修改说明见 `webapp/pinyin_clips/ATTRIBUTION.md`。
- **这套做法已抽成通用 skill**：`../.agents/skills/web-pinyin-audio/`（给别的中文网页/Web App 用；dsh、Codex 在本仓库内自动发现，入口是它的 `SKILL.md`）。书里的实现仍是自包含的参考实现，改动本书的规则/代码不会影响 skill，反之亦然。
- **轻声**（的/了/着/子/们…，占 8.1%）没有录音：取该音节现成录音里最接近“低而短”的一声（优先 3、4、2、1 声）截短到 0.30 s、尾部渐弱、降音量来**模拟**；这是近似，不是真轻声（致谢里已注明，规则在 `pinyin_overrides.json` 的 `neutral`，可逐字改本调）。**构建时没有人耳验收，请家长抽听。**
- **没有录音的**只有 `ju4`（22 处，上游也没有）：用系统自带的中文语音念单字，没有就只显示拼音。其余 99.87% 的汉字有真人发音。
- **许可**：录音 CC-BY-SA-3.0（Chen Wang 王琛），设置面板里有“发音致谢”，标明已裁剪转码；仅供识字参考，不是教材认证录音。
- **依赖**：构建要 `pip install pypinyin`；`ffmpeg` 只在录音库缺音节、要现做新录音时才需要；不想要这个功能：`python3 -X utf8 -I webapp/build.py --no-pinyin`。
- **自检**：`python3 -X utf8 -m unittest webapp/test_pinyin.py`（读音规则回归）；`CHROME=…/chrome.exe node webapp/qa_pinyin.mjs`（真浏览器：数据完整、悬停多音字按上下文显示、点击真的开始播放、标点没有气泡、开关生效、触屏轻点不翻页、无控制台报错）；`node webapp/qa.mjs` 仍要“全文逐字相同、桌面无滚动页、无控制台报错”。
- 设计文档：[`webapp/PRD_pinyin_hover.md`](webapp/PRD_pinyin_hover.md)。
