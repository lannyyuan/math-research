# 儿童科普动画：汽油车 / 电动车的肚子里有什么？

Remotion + three.js（`@remotion/three`）制作的约 70 秒小学科普动画（1920×1080，30 fps），给 PPT 课堂播放。
同一工程随后会做对称的「电动车」视频，所以车模、X 光材质、高亮、爆炸视图、标签、字幕、卡片都是可复用组件，风格常量集中在一处。

## 交付物（`npm run render:*` 输出到 `out/`；已提交的副本在 `deliverables/`）

`deliverables/` 收录全部四个视频（MP4 约 38 MB、WMV 约 45 MB）与关键帧拼图。

| 文件 | 内容 |
|---|---|
| `gas-car_narrated.mp4` | 中文旁白 + 字幕 + 音效（H.264/AAC，PPT 2013+ 可直接插入） |
| `gas-car_subtitles-only.mp4` | 无旁白、保留中文字幕和音效，供老师现场讲解 |
| `gas-car_narrated.wmv` / `gas-car_subtitles-only.wmv` | 同上两版的 WMV（WMV8 + WMA2，任何 Windows 版 PowerPoint 都能播） |
| `electric-car_narrated.mp4` / `electric-car_subtitles-only.mp4` | 电动车版，两种版本同上 |
| `electric-car_*.wmv` | 电动车版 WMV |
| `keyframes.jpg` / `keyframes-ev.jpg` | 两部片子各 16 个分镜关键帧拼图，用于交付前目检 |

## 分镜（时间以旁白为准自动排布，当前总长 70.0 s）

| 时间 | 画面 | 标签 / 字幕 |
|---|---|---|
| 0–2 s | 标题卡 + 橙色卡通小车 | 汽油车的肚子里有什么？ |
| 2–12 s | 车身转 X 光；车尾油箱高亮；黄色油滴沿油管流到发动机油轨 | 油箱、油管 |
| 12–28 s | 镜头推近发动机剖面：活塞/连杆/曲轴联动，DOHC 凸轮轴开合气门，火花塞按 1-3-4-2 依次闪光（“砰”字正好对上一次点火） | 发动机 · 活塞 · 曲轴（+ 凸轮轴·气门、火花塞、气缸号与点火顺序面板） |
| 28–40 s | 三速常啮合变速箱 1→2→3 换挡，结合套滑动、啮合齿轮变金色；动力箭头经差速器、半轴流到两前轮，车轮转起来 | 变速箱、车轮（+ 档位面板） |
| 40–52 s | 散热器 + 蓝色冷风波纹；机油在油底壳与运动件间循环；排气歧管暖橙色发光，排气管冒灰色尾气 | 散热器 · 机油 · 排气管 |
| 52–68 s | 全车 X 光，14 组部件 + 4 个车轮沿远离车身中心的方向滑开成“零件云”，每个部件中文标签；计数器爬升到 ≈ 2000+；随后合拢复位，车开走 | 15 个部件名 + 会动的零件 ≈ 2000+ |
| 68–70 s | 车身恢复不透明，结束卡 + 笑脸小车 | 汽油车 = 复杂的小工厂 |

## 分工

* **three.js**（`src/three/`、`src/gas-car/three/`）：3D 场景——车身（toon ↔ X 光着色器）、全部动力系统几何体（代码生成，无外部模型/贴图/图片）、爆炸视图位移、镜头。
* **Remotion**（`src/components/`、`src/gas-car/Overlay.tsx`、`Sound.tsx`）：时间轴、标题/结束卡、中文标签（3D 锚点投影到屏幕 + 确定性避让布局）、字幕、计数器、面板、旁白与音效、最终渲染。

## 真实性与不变量（`npm run check` 自动验证）

* 机械联动：活塞位置由曲轴转角经连杆的曲柄滑块关系算出；连杆长度恒定；每缸在自己的压缩上止点点火，顺序 1-3-4-2；凸轮轴 = 曲轴转角/2（正时皮带两链轮齿数 18:36），气门升程直接由凸轮型线算出，只在本缸进/排气行程打开；挂档且离合结合时 发动机转速 = 档位比 × 主减速比 × 车轮转速。
* 布局：横置直列四缸、变速箱在左侧、半轴在前轴线上、油箱在后座下、排气沿地板到车尾、散热器在车头、油底壳在缸体下方。
* 爆炸视图：每个部件的位移方向与“车身中心→部件”方向夹角 < 90°，单调滑出；合拢后位移精确为 0。
* 标签：始终是面向镜头的 2D 卡片；逐帧检查互不重叠、不出画、不压字幕/面板/计数器、锚点都在画面内。
* 确定性：所有动画只由帧号驱动（曲轴角、车轮角等按帧积分预计算），无 `useFrame`、无实时时钟、无 `Math.random`；音效也按同一数据离线合成。
* 中文：随工程打包 GB2312 子集的 Noto Sans SC / 站酷快乐体（OFL），`scripts/check_glyphs.py` 检查屏幕上每个字都有字形。
* 时长：旁白长于分镜目标时自动拉长该段，总长强制在 60–80 s。

## 目录

```
src/
  style/theme.ts, fonts.ts       统一风格常量（颜色、字号、字体）
  lib/                           动画函数、镜头插值与投影、标签避让布局
  three/                         可复用 3D：Toon/Glass 材质、Fade 虚化、CarBody(X 光)、Wheel、Ground、效果层(油滴/动力箭头/冷风/尾气)
  components/                    可复用 2D：PartLabel/LabelLayer、Subtitle、Counter、BigTitle、ChipPanel/NumberTag
  gas-car/
    narration.json               旁白文案（按句）
    voice-timing.json            TTS 生成的逐句/逐字时间
    timeline.ts                  分镜 → 具体时间（以旁白为准）+ 镜头关键帧
    layout.ts / parts.ts         部件位置、中文名、爆炸位移
    mechanics.ts                 曲轴/活塞/凸轮/气门/点火/变速箱/车轮运动学
    state.ts, labels.ts          每帧场景状态、标签时间表
    three/                       发动机与各系统 3D 组件、场景总装
    Overlay.tsx, Sound.tsx       2D 叠加层、声音
scripts/
  build_fonts.py   tts.py   make-audio.ts   check-scene.ts   check_glyphs.py   plan-explode.ts   to-wmv.sh   keyframes.sh
```

## 复现

```bash
npm ci
pip install edge-tts fonttools brotli           # 仅在需要重做字体/旁白时
npm run fonts      # 可选：重建字体子集（已提交）
npm run tts        # 可选：重新合成旁白（已提交），需联网
npm run check      # 类型检查 + 不变量 + 字形
npm run render:narrated && npm run render:subtitles   # 无 GPU 环境使用 SwiftShader（见 remotion.config.ts）
npm run wmv && npm run keyframes
```

旁白：微软 Edge 在线神经语音 `zh-CN-XiaoxiaoNeural`（语速 −12%）。音效与发动机声全部由 `scripts/make-audio.ts` 用代码合成，发动机“嗡嗡”声的节拍来自与画面相同的点火时刻数据。

## 电动车版《电动车的肚子里有什么？》（72.0 s）

与汽油车成对播放用于“比一比”：同一车身比例、机位（标题/侧视/车尾/零件云/结束）、标签样式、字幕位置与卡片版式，只差颜色（绿色、冷色调）和内部结构。

| 时间 | 画面 | 标签 |
|---|---|---|
| 0–2 s | 标题卡 + 绿色小车 | 电动车的肚子里有什么？ |
| 2–14 s | 车身转 X 光，车底平铺电池包发绿光，12 个电芯模组逐格亮起 | 电池包 |
| 14–26 s | 前舱控制器指示灯像大脑一样闪烁；蓝色电流沿橙色高压线束从电池流向控制器（右上“电流方向”面板） | 控制器、高压线束 |
| 26–40 s | 电机剖面：电流进入定子，绕组按旋转磁场依次发光，永磁转子带速度线旋转，车开始走 | 电机、定子、转子 |
| 40–50 s | 单速减速器 11:55 一对齿轮啮合（转子 5 圈 → 车轮 1 圈），车轮平稳转动 | 单速减速器、车轮 |
| 50–60 s | 车尾：没有排气管，淡绿色干净空气 + 小叶子；插入“汽油车冒烟 vs 电动车不冒烟”剪影对比卡 | 没有尾气 |
| 60–70 s | 全车 X 光，只散开 7 个大块并带标签；电池/电机/电控三个图标随旁白依次放大；计数器 ≈ 20；合拢复位 | 7 个部件名 |
| 70–72 s | 结束卡 + 笑脸绿车 | 电动车 = 简单的三大件 |

**几何审计与拆装编排（方法借鉴 MIT 许可的 [anatomy](https://github.com/wheresryan22/anatomy) skill）**：`src/electric-car/shapes.ts` 登记每个部件的真实形状（盒、圆柱、管线、球），`src/lib/sdfAudit.ts` 用距离场采样测两两间隙，`npm run audit:ev` 在静止、拆开（要求块间 ≥1 cm 间隙）以及拆装全过程每一帧检查无穿模，并检查每根高压线都终止在贴合宿主表面的接头上、没有部件入地、每个大块只朝远离车身中心的方向走。拆装按真实顺序错开出发：车轮先沿轴退出 → 控制器上提 → 线束平行插接面抬出 → 电机沿轴拔出 → 左右半轴各自从差速器沿轴拔出 → 减速器 → 电池包；合拢是拆装过程的时间倒放（后走先回）。改造前审计在拆装途中查出 27 对部件穿模（电池扫过前轮 220 帧、电机轴/半轴切穿减速器壳等），改造后为 0。

不变量（`npx tsx scripts/check-scene-ev.ts`）：齿轮中心距 = 两分度圆半径和；转子转速恒为车轮 5 倍、两齿轮转向相反；电流只按 电池 → 控制器 → 电机 方向流动，电机转动时必有供电；爆炸方向背离车身中心、合拢后精确归零；标签不重叠、不出画、不压 UI。改动共享组件后用参考帧 MD5 验证汽油车输出未变。

## 做新车型时复用

`CarBody`、`Wheel`、`Ground`、`Toon/Glass/Fade`、效果层、`LabelLayer`、`Subtitle`、`Counter`、`BigTitle`、`ChipPanel` 以及 `lib/` 与 `theme.ts` 都不依赖汽油车；新建 `src/electric-car/`（narration / timeline / layout / parts / mechanics / three / Overlay / Sound）并在 `Root.tsx` 注册即可，`CAR` 尺寸共用以保证两部片子对称。
