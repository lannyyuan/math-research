# 03 · 踩过的坑和修法

按“先撞到的”顺序，每条：现象 → 原因 → 修法。下次先扫一遍，能省不少时间。

## 环境与工具

| 现象 | 原因 / 修法 |
|---|---|
| 沙箱里下载不了 Chrome / GitHub release | 被拦。用本机 `/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell`（环境变量 `REMOTION_BROWSER`）；字体用 npm 包 `lxgw-wenkai-webfont`（npm / jsdelivr / PyPI 能用） |
| 新会话里 `import fontTools` 失败 | pip 包不跟着容器走。每次先 `pip install fonttools brotli pillow numpy` |
| `node scripts/stills.mjs Film:s3+2.8,5.5` 第二帧是“第 5 帧” | 逗号分隔后每一项单独解析，**每一项都要带场景前缀**：`Film:s3+2.8,s3+5.5` |
| `pkill -f stills.mjs` 把自己的 shell 也杀了（退出码 144） | 命令行里含这个字符串。用 `ps` 找 PID 再 `kill PID` |
| 长任务（整片渲染、40 张图）被工具超时打断 | 用 `nohup … &` 或 `node -e "spawn(..., {detached:true}).unref()"` 放后台，再轮询日志；Remotion 打印的“Memory reported by CGroup…”只是提示，不是错误 |
| `while read … ffmpeg` 循环只处理了第一行 | ffmpeg 吃掉了 stdin。加 `-nostdin` |
| 配乐听不到 | 只能查电平：平均/峰值、每 10 秒响度、有无静音空隙、有无削波。README 里如实写“没法听” |
| `tsc` 报错：`FontFaceSet.add` 类型、`calculateMetadata` 的 props 类型、条件里多余的比较 | 加类型断言 / 去掉多余比较；每次大改后跑 `npx tsc --noEmit -p .` |

## 画面（程序化水彩墨线）

| 现象 | 原因 / 修法 |
|---|---|
| 字幕互相叠、字幕盖过场景结尾 | 改成基于 `gap` 的调度（`schedule.mjs`），检查器强制 ≥0.3 s 间隙并检查不越过场景结尾；字幕太长就缩成更短的原文片段，场景时长按检查器给的下限调 |
| 角色站进字幕带 | 固定版面：`HZ=560`，脚底 `GY=770`，字幕带 y>860；两行字幕改 64 px / 底边 50 px，个别场景把脚底再抬到 818 |
| 镜头对不准 / 反了 | 用 `at(wx, wy, z)` 指镜头对准的世界坐标，别手算平移的正负号 |
| 倾斜镜头时地平线下出现深色带 | 给远/中林下面垫一层渐变底（`underlay`） |
| 给林子上色（春天）时颜色染到天空 | 用 CSS `mask-image` 把色层限制在树的 alpha 里 |
| 林子底边被平切 | 底边用 mask 渐隐 |
| 乌龟头朝向/位置反了 | 局部坐标里 `+ up` 的符号写反；脱离书包时不要再加偏移 |
| 山洞外面泛白 | 洞外整体罩一层 multiply 的冷蓝（`#8aa3da`） |
| 妈妈的围巾尾巴冒出来 | 大人的围巾尾巴隐藏（红围巾只属于主角） |
| 矩形（房子、城墙）画出来像鸡蛋 | `blob()` 用样条平滑，4 个角点会被抹圆。把每条边加密（`dense()`） |
| 白天的天空上露出山图的矩形边 | 山图左右边缘要渐隐（`Backdrop` 的 `mountFade`，用 CSS mask 限定在山图的方框里） |
| 封面上出现两个题目 | 片头帧里已经画了题目。封面取题目还没浮现的那一帧（`s0 + 0.75 s`） |
| 补充插图里前景树落在角色身上 | `FrameTrees` 宽度 `3000×k`，`k≈0.66`（再加 x=-60）才刚好把树放在两侧 |
| 动物画不过来 | 只画剪影（深靛蓝 + 一点浅色的眼睛/尾巴尖），再加成对的眼睛；效果好且风格统一 |
| 蝙蝠一样的“猫头鹰” | 翅膀轮廓别做锯齿；换成栖在树枝上的剪影 + 大眼睛 |
| 成片 306 MB | 分场景用 crf 18 渲，最后一遍 x264 crf 27 → 61 MB，看不出差别 |
| 交付通道只有 30 MiB | 另给 720p crf 29 的小副本（21 MB）+ 一条 `gh` 命令拉原版（见 04） |

## 分页与网页

| 现象 | 原因 / 修法 |
|---|---|
| 对话章一页要滚 1000+ 像素 | 按汉字数分页不行：每个短段落至少占一行加段间距。改成按**版面行数**估算（`lines_between`），页数自动增加 |
| 按“版面重量”分页分出 107–110 页，每页很薄 | 容量估得太保守。以真实屏幕上的行数和每行字数为准（`CPL=25, CAP=13.4`），再对着截图校准 |
| 配图表按页号写，改了分页就全乱 | 配图表按**章**写，每章没有字幕的页按顺序平均分配 |
| 相邻几页同一幅图，翻页时图也闪一下 | 图相同就保留 `.pic`，只换文字卡片 |
| QA 里“有图没加载”全是红的 | 误报：放映层里有个没有 `src` 的 `<img>`。检查时过滤掉没有 `src` 的 |
| QA 里 `page.click('mark.film')` 超时 | 页号变了，那页没有字幕。样例页按**字幕号 / 章名**动态取，不写死页号 |
| `page.evaluate(() => go(N + 1))` 报 `N is not defined` | 浏览器里看不到 Node 变量。当参数传进去 |
| `history.replaceState` 在 `file://` 下可能抛错 | 包 try/catch；`localStorage` 同理 |
| 文字挤在一起、引号后面有空隙 | 全角标点的正常现象（`？”`）；两端对齐 + 字距别太大（`letter-spacing .03em`） |
| 字体子集化时一堆 `feat/morx/FFTM NOT subset` | 只是警告，无害 |
| 单引号 `‘ ’` 没有字形 | 回退到系统字体，无碍 |
| 手机上封面题目折成两行 | `font-size: clamp(28px, 9.6vw, 128px)`，下限别设太高 |
| 暗图（还没点灯的房间）在屏幕上一团黑 | 构建时对平均亮度 <50 的图做 gamma 提亮 |
| Python 管道里 `| head` 报 BrokenPipeError | 只是 `print` 被截断，`plan.json` 已写完，无害；脚本里用 `subprocess` 调就不会出现 |

## 识字表（PDF 是图片）

| 现象 | 修法 |
|---|---|
| 扫描版 PDF 没有文字层 | OCR（RapidOCR）。整页识别会把相邻格子合并，要**按格切成一行一行**再识别；识别率约 90%，所以最后用**人工逐页转写 + OCR 与拼音交叉核对**，容易混的字（炽/帜）按印刷拼音和放大图判定；在输出文件里说明“OCR + 人工，不保证 100%” |

## 交付

| 现象 | 修法 |
|---|---|
| Stop hook：仓库里有未提交的文件 | 提交并推到指定分支（`git push -u origin <branch>`；网络错误才重试，2/4/8/16 s） |
| pptxgenjs 没装 | `npm i --save-dev --save-exact pptxgenjs`；生成后用 pptx 技能的 `validate.py` + LibreOffice 渲染抽检 |
| 用户问“怎么把原版高清拉回来” | 给 `gh api … Accept: application/vnd.github.raw` 或 `gh repo clone … --sparse` 的完整命令（见 04） |
