# HANDOVER — 《小石猴点灯》动画短片 + 绘本网页（交接文档）

> 分支：`claude/admiring-johnson-lf6etl`　工程目录：`stone-monkey-film/`（和 `lighthouse-light-film/`、`snow-lamp-film/`、`skills/ink-storybook-film/` 同级）
> 这份文档写给“在本地接手的 Claude Code”：先读完它，再动手。**额度紧张，原则：少铺开、先出成片、每完成一块就 `git commit && git push`。**

---

## 0. 一句话状态
影片 **约完成 55%**：时间线/字幕/配乐/工具箱/片头/第一部/第二部（江边）/第三部（海边）/第四部（前半）/第五部（城门）/尾声 已出图验证；**第六部整场没写**、第三~五部后半缺背景板和部分人物精灵；**还没有成片 MP4**；绘本网页管线已搭好（占位图版 1.8 MB 能构建），等图。

## 1. 任务书（原始要求，摘要）
- 做 4:30–5:00（建议 ≤ 4:55）、1920×1080、30fps 的手绘水彩动画短片《小石猴点灯》，给 6~8 岁孩子看；技术路线自选（我们用 Remotion）；**工程必须能重新渲染**；附 README，写明怎么重渲染 + 记录风格取舍（尤其暖色例外）。
- 美术基准：`ref/cover.png`（画风/色调/留白）、`ref/character-sheet.png`（角色/宝物造型）。
- 叙事：片头 → 一 天黑了 → 二 河边搭桥 → 三 海底的珍珠 → 四 西山的雪铃 → 五 北边的金鼓 → 六 点亮那盏灯 → 尾声（细节见 `story/film_source.txt`）。
- **字幕**：只能是原文**正文**的连续片段，一字不改（行首 `#`/`【` 是批注，不能当字幕）；≤2 行、每行 ≤18 字；停留 ≥1.5 s + 0.3 s/字；底部居中半透明墨色带；LXGW WenKai（霞鹜文楷，OFL）；角色/关键动作不进字幕带。
- 画风：松动墨线+飞白、透明水彩平涂+水渍边、宣纸纹理、每镜头 ≥1/3 留白；夜色色板 #1E2A44/#121A2E/#5A6B86/#EFE8D8/#2A2622；**暖色只允许**：宝珠光 #F3D98A、龟甲眼睛(火星色)、篝火/火种 #E8873A、奶奶红头绳/红布包 #B8382E、小姑娘红裙(小面积)，其余(金鼓/国王衣/神光)降饱和成灰金/土黄；灯亮后(六后半、尾声)解除夜色，可出红霞 #E9A38C/紫霞 #9C86B8。
- 龟甲手掌大小（≈石娃身高 0.135，设定表画大了，以这条为准）；老龙要慈眉、眼皮半垂、像刚睡醒、不能凶；新角色(老婆婆、红裙小姑娘、牧人+马、卫士、国王、守天门的神、凤凰…)同笔法、简单、冷色衣服；神穿白衣、头有淡光圈、手拿玉尺。
- 禁止：孙悟空符号(金箍/虎皮裙/筋斗云/桃子特写)、欧式建筑(城是中式城墙+城楼，塔是**九层**砖塔)、动漫大眼/3D/霓虹/厚涂、抄现成构图。落水/海底/老龙/爬塔/卫士长枪：安静温和，不吓人。
- 声音：自合成（古筝/箫/木鱼/风铃，鼓声在五、灯亮在六加强），不配旁白，音效点到为止。
- 自检（交付前必做）：从成片抽 ≥40 帧拼联系表，逐项核对 六部情节都在、字幕与原文逐字一致、暖色只在约定处、龟甲始终手掌大小、字幕带里没压角色。
- 另一个交付：**中文单文件绘本网页**，全文用 `story/book_source.txt`（加长版精简版）。
- 只有缺原文/缺图/环境做不下去才问用户，其余自己判断。

## 2. 已做的重要决策（别推翻）
1. **结尾字幕冲突**：任务书要求最后一句字幕是“下一个故事，等你来讲。”，但它在原文里只出现在 `【44】` 画面提示行里（不是正文）。我们照任务书做，作为**唯一显式例外**（`timeline.json` 里 `"exception": true`；`scripts/check-subtitles.mjs` 核对它确实原样出现在原文提示行里，且只允许一条）。README 与交付说明里要告诉用户。
2. 绘本全文文件章节顺序是乱的：网页按“分”的编号排序，增补一~四放在第六分之后、第七分之前（`webapp/plan.py` 顶部 `ORDER`）。交付时告知用户，可一键改。
3. 光是叙事主线：世界画两遍（夜色版 + 光照版），光照版用跟着宝珠走的圆形软蒙版叠上去（`src/fx/Light.tsx` 的 `Lit`；圆心用 `project(cam, p, x, y, 板宽, 板高)` 换成屏幕坐标）。宝珠光池半径≈330（“只照三尺”），进城门时放大到≈780，老龙吐珠时先“整座宫都亮”(≈1700) 再收回 330。
4. **字幕带安全**：镜头一律用 `atg(世界x, 缩放z)`（`src/scenes/kit.tsx`），让角色脚底落在屏幕 y≈820（带的上沿 845）；`CharsCtx` 三档（2 全画 / 1 不画角色 / 0 什么动的都不画）供 `scripts/audit_band.py` 和 `audit_warm.py` 使用。
5. 龟甲大小只在 `cast.tsx` 的 `Houzi` 一处决定（`HOUZI_RATIO=0.135`）；石娃基准缩放 `KID_S=0.84`(≈320px 高)，奶奶 ×1.03，成年人精灵按 ×0.7~0.8 缩到石娃的 ≈1.45 倍（卫士 `GUARD_S=0.7`，官员 0.8，牧人 0.78）。
6. 设定表修图在 `scripts/retouch.py`（老龙慈眉半垂眼、龟甲胸前裂纹），金鼓降饱和、奶奶红头绳单独成层(`nainai_*_red`)、龟甲眼睛单独成层(`houzi_*_eyes`) —— 全在 `scripts/make_sprites.py`；夜色版由 `scripts/make_night.py` 生成（可重复运行，新精灵登记进 `public/sprites/sprites.json` 后运行即可）。
7. 水墨转场用 `src/fx/InkIn.tsx` + `ShotStack.tsx`（显现图 `public/props/ink_{a,b,c,d}.png`，由 `scripts/make_ink_maps.py` 生成）。不用闪白/硬切。
8. 仓库里**提交了** `public/bg/*`（所有背景图，约 80 MB）和精灵，所以拉下来就能直接渲染，不必重画。

## 3. 怎么跑（本地）
```bash
cd stone-monkey-film
npm install                      # 需要网络；浏览器：REMOTION_BROWSER 指向 headless chromium（脚本里有默认路径，本机不同就设环境变量）
pip install numpy scipy opencv-python scikit-image pillow fonttools brotli
npm run check                    # 字幕检查（现在全绿：40 条，295 s = 4:55）
npx tsc --noEmit -p .            # 类型检查（现在干净）
npm run stills -- "Film:s1+13,s5+12" --scale=0.5   # 出静帧：场景id前缀+场景内秒数；结果在 out/stills/
python3 scripts/sheet.py out/sheet.png out/stills/a.png out/stills/b.png --cols=2 --w=900   # 联系表
npm run music                    # 重新合成配乐 → public/audio/score.m4a（已提交一份，约 60 s）
npm run render                   # 分场景渲染+拼接+配乐 → dist/xiaoshihou-dian-deng.mp4（约 1 小时；某场重渲=删 out/parts/<场景>.mp4）
npm run audit ; npm run audit:band   # 暖色审计 / 字幕带审计（写好未跑过）
```
场景起点（秒）：s0 0 · s1 10 · s2 58 · s3 98 · s4 142 · s5 183 · s6 225 · s7 279（总 295）。

## 4. 完成度
### 4.1 已完成并看过出图
| 部分 | 状态 |
|---|---|
| 工具箱 | `scripts/paint/{pt,cn,grade,ccommon,composite,make_paper}.py`（水墨水彩笔法、夜色/光照/晨光调色、保存板子+manifest） |
| 精灵 | 设定表抠图（石娃/龟甲/奶奶/大鱼/老龟/老龙 正侧面 + 宝珠/铜铃/火种/金鼓/银针），派生块（坐姿上身/腿、手臂/无臂身体 —— 无臂身体是平涂补色，略糙，只准备给敲鼓用） |
| 时间线/字幕/字体/配乐 | `src/timeline.json`、`schedule.mjs`、检查器、`public/fonts/WenKai-subtitle.woff2`、`scripts/make_music.py`（事件时间从字幕排程算出） |
| S0 片头 | 灰灯盘+书法片名从墨里洇出（片名字取自封面） |
| S1 第一部 | 白天山谷→灯灭→水墨洇开到村口→奶奶门口→耳贴怪石→裂石→龟甲蹦出；已出图验证，可再润色 |
| S2 第二部 | 灶间(A)、村口一步三回头(B) 已写但**灶间板子没画**（缺 `kitchen_*`、`bundle_red`）；江边(C) 已验证（断桥→低桥→高桥、水底大鱼、鱼跃）；缺 `plank` 精灵（扛木板那一下看不到木板） |
| S3 第三部 | 海边(A) 已验证（鳞片贴胸、海水让路）；B 海底(缺 `palace_mid/near`)、C/D/E（老龙/青石/吐珠，已写代码**未测**，缺 `hall_sea_*`、`spring_*`、`boulder/lever/flat_stone/scale`） |
| S4 第四部 | A 山路（缺 `oldwoman_sit_side`、`firewood`、`firewood_tied`）、B 霜林 已验证；C 雪山小屋（板子有）、D 小屋里(缺 `hut_in_*`)、E 小姑娘(有 `girl_side`) 已写**未测** |
| S5 第五部 | 城门 B 已验证；A 草原(缺 `grassland_*`、`horse_side`、`sheep`)、C 殿(缺 `hall_king_*`；有 `king_seated`/`official_*`)、D 爬塔(`pagoda_*` 有，1920×3400，层窗坐标待量)、E 塔顶(`pagoda_top_*` 有；敲鼓用 `shiwa_side_noarm`+`shiwa_side_arm`+`drum`) **均未写** |
| S7 尾声 | 完成并验证（四季树冠、日夜流转、石娃坐姿、龟甲哈欠、结尾字幕） |

### 4.2 没做（按优先级）
1. **S6 整场未写，且 `src/scenes/index.ts` 里没注册 `s6-lamp`**（现在渲染会缺这一场）。设计草案见 §6.2；`src/fx/LampLight.tsx`（碗→盆→车轮→满天的光）已写好。
2. 缺的背景板（规格与锚点见 `scripts/paint/PLATES.md`，是画师的“合同”）：`kitchen`、`palace_mid/near`(far 已有)、`hall_sea`、`spring`(+`spring_clear`)、`hut_in`(+`hut_in_clean`)、`grassland`、`hall_king`、`sky_gate`(+`cloud_road`+dawn 变体)、`volcano`、`lamp_sky`(+`wick_fixed`)。**省额度的替代**：板子不全时可复用现成板子 + 简单叠加（例如灶间/小屋内景/殿内都可以用一张“暗色木板墙+桌子”的简版；云海/火山/灯座可以用 `title_sky` 夜空 + 前景云台条）。
3. 缺的精灵（规格见 PLATES.md §4）：`oldwoman_sit_side`、`firewood`、`firewood_tied`、`horse_side`、`sheep`、`phoenix_a/b`、`bird_up/down`、`swallow_up/down`、`bundle_red`、`plank`、`rope_coil`、`bamboo_pole`、`bowl`、`scale`、`sack`、`spear`、`villager_carry`、`wick_fixed`、`boulder`、`lever`、`flat_stone`（`shrimp_guard` 可跳过）。已有：`girl_*`、`herder_*`、`guard_front`、`official_*`、`king_seated`、`god`、`villager1~4`、`kid1~3`、`girl_flower`。
4. 渲染成片 → 自检（联系表 ≥40 帧、`audit`、`audit:band`、龟甲尺寸目测）→ 修问题 → 复渲。
5. 绘本网页：见 §7。
6. 收尾：README 里把“成片 4 分 55 秒”等数字以实测为准；`skills/ink-storybook-film/` 补充（已有 `references/06-ink-wash-zh.md`，可再把 `templates/film-zh/` 同步一份最终代码）。

## 5. 场景内关键时间点（秒，场景内；来自字幕排程，场景代码用 `cuesOf('s1-dark')` 取）
```
s1  c0 1.5 · c1 7.0 · c2 14.6 · c3 20.7 · c4 28.3 · c5 34.1(裂缝 +1.6、破开 +3.4) · c6 40.8
s2  c0 1.2 · c1 7.3 · c2 14.0 · c3 21.0 · c4 26.8 · c5 33.5
s3  c0 4.0 · c1 11.3 · c2 17.4 · c3 22.9 · c4 29.3 · c5 34.5
s4  c0 1.2 · c1 7.9 · c2 15.2 · c3 21.3 · c4 26.8 · c5 34.1
s5  c0 1.2 · c1 7.9 · c2 14.9 · c3 22.2 · c4 30.4 · c5 36.2（“咚”在 c5+1.9 = 38.1，配乐按这个点放大鼓）
s6  c0 2.5 · c1 9.2 · c2 14.4 · c3 23.2 · c4 31.4 · c5 36.0（灯亮，配乐在 c5+0.3 起全曲最满） · c6 44.2
s7  c0 1.0 · c1 9.5（“下一个故事，等你来讲。”）
```
改 `timeline.json` 后：`npm run check` → `npm run music`（配乐事件会跟着变）→ 场景动作用 `cuesOf` 的地方自动跟。

## 6. 接着做（具体到场景）
### 6.1 S3/S4/S5 剩余镜头
代码骨架都在 `src/scenes/S3.tsx S4.tsx S5.tsx`（用 `ShotStack` 串镜头、`Lit` 做光池）。板子/精灵到位后：`npm run stills -- "Film:s3+14,s3+25,s3+36" --scale=0.5` 逐镜头看，调坐标。S5 还要补 A 草原（牧人+篝火+马，`Campfire`+`FireGlow` 池）、C 殿（国王坐宝座，官员两侧，石娃进殿）、D 爬塔（镜头沿 1920×3400 的塔身向上摇，宝珠光依次点亮九层的窗，光池跟着）、E 塔顶（石娃走到鼓前，近侧手臂 `shiwa_side_arm` 绕肩举起再落下，“咚”=一圈圈扩散的波纹 + 云缝裂开）。
### 6.2 S6（54 s）设计草案
- A 云海（0–13.8）：鼓声余响，云裂一道缝；守天门的神（`god`，白衣、淡灰金光环 #cfc29a、手拿玉尺）从光里出现；凤凰一对飞过；石娃把宝珠/铜铃/金鼓摆在云上；神一指，**云路**（`cloud_road`，一块块云石板连成的路，不是筋斗云）从左到右显现。
- B 火山（13.8–22.4）：石娃沿云路到南方火山，摇铃、鼓鸣，火山口的火苗跳起来变成一团飞进袋里（火种 #E8873A）。
- C 回家（22.4–31）：夜里的村口，奶奶（红头绳）在门口递红布包着的银针（c3 “拿去…针尖朝上，别扎手”）。
- D 灯座（30.4–44）：五样宝贝装进灯里（宝珠安灯座、雪铃挂灯边、金鼓放灯下、火种进灯芯），银针接好断掉的灯心（`wick_fixed` 淡入 + 小闪光，c4）；c5（36.0）点火：`LampLight` 从 0→1（碗→盆→车轮→满天，亮度压在 0.93 以下，**不要闪白**），同时用 `Lit` 的光池放大让整个世界显出“光照版”的颜色。
- E 晨光村口（43–54）：用“光从上往下泼”的渐变蒙版把 `dawn` 变体盖到夜色版上（不是水墨转场也可以）；霜化成露珠（闪烁的小白点）、鸟/燕子（`bird_*`/`swallow_*` 两帧扑翅）、孩子们跑出来（`kid1~3`、`girl_flower`）、奶奶（`nainai_front`）在人群里，c6 时给她脸颊一滴泪（SVG 水滴）。红霞/紫霞在这里和尾声允许出现（`village_*` 的 dawn 变体已有）。
- 别忘了在 `src/scenes/index.ts` 注册 `'s6-lamp': S6`。
### 6.3 渲染与自检
`npm run render`（先确保 tsc 干净、`npm run check` 全绿）。成片出来后：`node scripts/qa_frames.mjs dist/xiaoshihou-dian-deng.mp4 out/qa`（按字幕抽帧）+ `python3 scripts/sheet.py …` 拼 ≥40 帧联系表，逐项核对任务书“自检”五条；`npm run audit`、`npm run audit:band`。验收标准见 §1。
### 6.4 已知小问题（顺手修）
- 石娃肩上的龟甲眼睛光晕偏亮偏黄，可再降 `cast.tsx` 里 `Houzi` 的 glow；
- S1 白天山谷里茅屋太小太靠下；S0 灰灯盘可再亮一点；
- `public/sprites/sprites.json` 是被多个脚本读写的共享文件（曾有并行写入覆盖的风险）——并行作业后要核对键是否齐全（见 §4.2 清单）；
- 画师写的 `scripts/paint/chars_*.py`、`cn_people.py` 是人物精灵的来源；人物比我们的设定表手绘略平，属于“造型简单”范围内。

## 7. 绘本网页
- 位置：`webapp/`（`plan.py` 分页、`build.py` 打包、`app.js/app.css/template.html`、`qa.mjs` 真浏览器核对、`heroes.json` 配图表、`PLATES.md` 补充插图清单），成品 `dist/xiaoshihou-book.html`（占位图版，1.8 MB）。
- 构建/检查：`python3 -I webapp/build.py`、`node webapp/qa.mjs --shots=out/book_qa`（Playwright + 本机 Chromium，见 `webapp/qa.mjs` 里的路径）。**上一次并行任务被中断，没收到它的结案报告**：请先跑一遍 build + qa，确认 ①全文核对（页面文字 vs 独立抽取的原文，逐字相同）②桌面 1440×900 无需滚动的页 ③无控制台报错 ④章节顺序（§2.2）。
- 配图：`heroes.json` 里第一~第六分用影片干净帧 `cue/NN`（需先 `node scripts/storyboard_plan.mjs && node scripts/book_stills.mjs`，**这两个脚本是从英文版拷来的，要改成本片的场景/封面和 `plate/*` 清单**；封面直接用 `ref/cover.png`），第七分起用 16 个 `plate/*` 补充插图（`webapp/PLATES.md` 里每个 key 写了 `base:`（用哪块背景板）和 `chars:`（用哪些人物精灵））——用一个 Remotion `Plate` composition 拼出来（参考 `lighthouse-light-film/src/plates/Plate.tsx`、`scripts/book_stills.mjs`）。额度紧时可先用占位图交付网页、说明配图待补。

## 8. 省额度的建议
- 别再开很多并行子任务；先复用现成板子/精灵出成片，再补细节。
- 看图用 `--scale=0.5`，一次拼一张联系表；每个镜头只验证关键时刻。
- 渲染放最后；先 `FORCE` 都不要，只重渲改过的场景。
- 每个里程碑 `git add -A && git commit && git push -u origin claude/admiring-johnson-lf6etl`（提交信息末尾加 `Co-Authored-By: Claude … <noreply@anthropic.com>`）；**不要建 PR**（用户没要求）。

## 9. 目录速查
```
src/            Remotion：timeline.json · schedule.mjs · Film.tsx · palette.ts · fx/{Stage,Sprite,Light,InkIn,ShotStack,Water,Season,LampLight,Subtitle,Snow,Variant}.tsx · scenes/{kit,cast,S0..S7}.tsx（S6 缺）
scripts/        check-subtitles.mjs · render.sh · stills.mjs · scene_ranges.mjs · qa_frames.mjs · sheet.py · extract_sprites.py · retouch.py · make_sprites.py · make_night.py · make_cover_assets.py · make_ink_maps.py · make_music.py · audit_warm.py · audit_band.py · subset_font.py · paint_all.sh · paint/（工具箱 + bg_*.py + PLATES.md）
public/         fonts · audio(score.m4a) · sprites(+ sprites.json) · props(片名字、墨晕图) · bg(板子+manifest.json+paper.jpg)
story/          film_source.txt（字幕原文，唯一来源） · book_source.txt（绘本全文）
ref/            cover.png · character-sheet.png
webapp/ dist/ out/(ignored)
```
更详细的方法沉淀：`skills/ink-storybook-film/references/06-ink-wash-zh.md`。
