---
name: web-pinyin-audio
description: 给中文网页/Web 应用加“点字看拼音、听发音”（pinyin hover + click-to-hear）：构建期给每个汉字标拼音（含多音字规则和审校表），同音共用一条真人音节录音（整本书约 850 条，而不是一字一个文件），运行期悬停显示带声调的拼音气泡、点击发声，单文件离线可用。当要给中文网页、绘本、识字/课文/儿童读物类 Web App 加汉字注音与点读时使用；不用于整句语音合成（TTS）或拼音输入法。
---

# web-pinyin-audio：中文网页的“点字看拼音、听发音”

**效果**：鼠标悬停在任意汉字上，字上方弹出带声调的拼音（如 `zhǎng`），点一下用真人录音念出来；触屏上轻点 = 显示 + 发声。默认“悬停只显示、点击才发声”。
**已在真实项目验证**：《小石猴点灯》绘本（17,180 个汉字）→ 847 种读音 → 846 条录音共 3.21 MB，单个 HTML 离线可用，99.87% 的字有真人发音。

## 三条硬规则（违反就是做错了）

1. **录音按“音节+声调”存，同音共用**（`zhang3.mp3`）。绝不一字一个文件；整个项目的录音文件数 ≈ 文本里不同读音的个数（几十到几百条）。
2. **页面文字一个字不能改**：只是把汉字包进 `<span class="hz" data-p="zhang3">长</span>`。验收时必须核对文字与原稿逐字相同。
3. **多音字必须审校；署名不能删**：读音是半自动的（pypinyin + 规则），要跑 review 过一遍；录音是 CC-BY-SA 3.0，页面里必须有“发音致谢”，并写明“已裁剪转码、轻声为模拟”。

## 约定与准备

- `SKILL` = 本文件所在目录；下面命令里的路径都相对它。可以在任意项目里使用，不要求这个 skill 装在特定位置。
- Python 3（在 3.12 上测过），`python -m pip install pypinyin`（必需）。**Windows 一律 `python -X utf8`**（否则中文文件按 gbk 解码失败）；Windows 的 `python3` 可能是应用商店占位符，用你的 venv 里的 python。
- `ffmpeg`：**仅当**录音库里没有需要的音节时才要（见下文“录音库”）。常见文本多数音节种子库里就有。
- Node + `playwright`：仅验收（浏览器自检）时要，在页面所在项目里 `npm i --no-save playwright`，浏览器路径用环境变量 `CHROME` 指定。
- 可选环境变量 `PINYIN_DRILL_DIR`：本机的 Pinyin_Drill_P0 目录（录音库缺音节时优先从这里取，只读）。

## A. 静态 HTML：一条命令

```bash
python -X utf8 $SKILL/scripts/wrap_html.py page.html -o page.pinyin.html --lib ./pinyin_clips [--rules my_rules.json]
```

- 汉字被包成 span；用到的录音 + `pinyin_hover.js/.css` 全部内联；`</body>` 前自动加“开关 + 发音致谢”。输出就是单文件。
- `--lib` 是**项目自己的录音库目录**（随项目提交）；多个页面用同一个库。
- 不会包：`script style title head code pre button a input…` 和带 `data-nopy` 的元素（要多跳过：`--skip-tags nav,footer`）。
- 然后做“多音字审校”和“验收”两节。

## B. JS 渲染的应用（SPA / 数据驱动）

读音在**构建期**标好，和文本一起放进数据；录音用 Python API 打包成 `window.__PYA`；渲染时把文本换成 span。完整步骤和代码见 `references/integration.md` §3。要点：

```python
from pinyin_annotate import Annotator            # sys.path 里加 $SKILL/scripts
from pinyin_clips import build_clips
ann = Annotator('my_rules.json')                 # 不传就用起步规则
py = ann.annotate('他长大了')                      # ['ta1','zhang3','da4','le5']，每个汉字一个
uris, report = build_clips({'zhang3', 'de5'}, 'pinyin_clips', neutral=ann.neutral)   # {id: 'data:audio/mpeg;base64,…'}
```

运行期：`PinyinHover.wrap(text, 'ta1 zhang3 da4 le5')` 生成 span，`PinyinHover.init({audio: window.__PYA, root, toggle})` 启动。参考实现（数据驱动的完整应用）：仓库 `stone-monkey-film/webapp/`。

## 多音字审校（别跳过）

```bash
python -X utf8 $SKILL/scripts/pinyin_annotate.py --review page.html other.txt --rules my_rules.json --out pinyin_review.md
python -X utf8 $SKILL/scripts/pinyin_annotate.py --rules my_rules.json "试一句话"     # 打印 字:拼音
```

逐条看 `pinyin_review.md`（多音字的全部上下文），不对就在规则文件里加一条并补一个单元测试。**不要把别的文章调出来的规则整套抄过来**——起步规则（`assets/rules.starter.json`）故意只放几条不会改错的；`references/polyphone-lessons.md` 有规则写法、审校流程，以及实测会误伤的例子（`校长`被读成 cháng 之类）。

## 录音库（同音共用、随项目提交）

`pinyin_clips.py` 给每个读音 id 按顺序找录音：项目库 `{lib}/{id}.mp3` → 本 skill 种子库 `assets/clips/clips.zip`（846 条，已处理好，**解出来放进项目库，不需要 ffmpeg**）→ Pinyin_Drill 真人录音 → 上游 audio-cmn 下载（后两者需要 ffmpeg 裁剪转码）。结果都落在项目库里，并记进 `{lib}/manifest.json`（来源 + SHA-256；库文件被改动会报错）。

- 单独跑：`python -X utf8 $SKILL/scripts/pinyin_clips.py --lib pinyin_clips --text page.html [--rules my_rules.json] [--emit-js pya.js] [--no-net]`
- **新生成的录音要和代码一起提交**；`unavailable`（上游也没有，如 `ju4`）页面里降级为系统语音或只显示拼音。
- 轻声（5 声，约占 8%）没有录音，用另一声截短渐弱**模拟**；想用真人轻声，直接把 mp3 放进库目录（见 `references/polyphone-lessons.md` §6）。

## 验收（交付前必须跑，并把结果写进报告）

```bash
python -X utf8 -m unittest discover -s $SKILL/tests              # skill 自身离线自检（14 条；有 ffmpeg + Drill 时多跑“现做新录音”那条）
CHROME=/path/to/chrome node $SKILL/scripts/qa_pinyin.mjs page.pinyin.html --source page.html \
     --cases 长大:0:zhǎng,走得快:1:de --allow-missing ju4          # 真浏览器：悬停/点击/开关/触屏/无报错/文字不变
```

`--cases 词:第几个字:期望拼音` 用来钉住你审过的多音字。QA 在读音不对时会失败（退出码 1）。**没有亲耳听过**就如实写“只验证了点击后播放确实开始”，不要写“发音正确”。

## 不要这样做

- 不要运行期 `fetch` 录音或联网取音（`file://` 会被拦；离线就废了）。录音一律内联。
- 不要在悬停时默认发声（自动播放策略下常常出不了声，还吵）；`auto:true` 仅作为用户设置项。
- 不要给 `<a>`/`<button>` 里的字包 span（点击会冲突）；不要改字、拆词、加标点。
- 不要声称读音“教材认证/100% 准确”：写成“pypinyin + N 条规则，已审校高频多音字”。
- 不要手拼录音路径/网址：读音 id 必须符合 `^[a-z]{1,6}[1-5]$`（`pinyin_clips.py` 已校验）。

## 目录

| 路径 | 作用 |
|---|---|
| `scripts/wrap_html.py` | 静态 HTML → 单文件成品（做法 A） |
| `scripts/pinyin_annotate.py` | 汉字 → 拼音 id；`--review` 多音字复核表 |
| `scripts/pinyin_clips.py` | 读音 id → 录音库 + data URI（`build_clips`） |
| `scripts/pinyin_hover.js` / `.css` | 运行期：气泡、点击播放（WebAudio）、系统语音兜底、开关；`PinyinHover.init/wrap/mark` |
| `scripts/qa_pinyin.mjs` | 真浏览器验收（通用） |
| `assets/rules.starter.json` | 起步多音字规则（保守） |
| `assets/clips/` | 种子录音库：`clips.zip`（846 个 mp3，一个文件）+ `manifest.json` + `ATTRIBUTION.md`（CC-BY-SA 3.0）；`pinyin_clips.py --pack-seed` 可重新打包 |
| `assets/demo.html` | 样例页（自检与示范用） |
| `tests/test_skill.py` | 离线单元测试 |
| `references/polyphone-lessons.md` | 规则写法、审校流程、误伤实例 |
| `references/integration.md` | 管线与决策理由、SPA 集成、无障碍与许可 |
| `references/example-rules-xiaoshihou.json` | 一本书调出来的 41 条规则（**范例，不要直接套用**） |

## 已知限制

- 每个文本节点单独标拼音：被行内标签劈开的词读音上下文会丢。
- 种子库约 850 个读音；其余音节需要 ffmpeg + Pinyin_Drill 或联网。
- 起步规则之外的多音字靠 pypinyin 默认值（已知会错的例子见 `references/polyphone-lessons.md` §4）。
- `.hz` 不可键盘聚焦（无障碍说明见 `references/integration.md` §4）。
