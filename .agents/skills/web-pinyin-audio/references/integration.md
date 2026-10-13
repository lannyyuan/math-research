# 集成与设计说明

## 1. 管线（为什么长这样）

```
正文文本 ──pinyin_annotate──▶ 每个汉字一个读音 id（zhang3、de5…）──┬─▶ 页面：<span class="hz" data-p="zhang3">长</span>
                                                                  └─▶ 去重 ──pinyin_clips──▶ 录音库 {id}.mp3 ──base64──▶ window.__PYA
运行期（pinyin_hover.js）：悬停 .hz → 气泡显示 mark(data-p)；点击 → 播放 __PYA[data-p]；没有录音 → 系统中文语音 → 再没有就只显示拼音
```

决策与理由（来自《小石猴点灯》绘本的真实数字：17,180 个汉字）：

| 决策 | 理由 |
|---|---|
| **录音按“音节+声调”存，同音共用** | 17,180 个汉字只用到 847 种读音 → 846 条录音（3.21 MB，约 3.8 KB/条）。一字一个文件是 17,180 个，既浪费又没法维护。任何文本的上限也只有约 1,300 种“音节+声调”。 |
| 读音在**构建期**标好，运行期没有转换引擎 | 页面小、结果可审校、可测试；运行期不需要 pypinyin。 |
| 录音**内联成 data URI**（`window.__PYA`） | `file://` 下 `fetch` 本地文件会被浏览器拦；内联后单个 HTML 离线可用。体积预算：录音 base64 ≈ 1.33×。 |
| 解码用 `OfflineAudioContext`、播放用 `AudioContext` | 前者不受“必须先有用户手势”限制，可以提前解码；后者在第一次点击时才创建，符合浏览器自动播放策略。解码结果放 LRU（200 条）。 |
| **悬停只显示拼音，点击才发声**（默认） | 浏览器自动播放策略下悬停发声常常出不了声，还会在鼠标划过时一片噪音。`auto:true` 才悬停即发声，且要求页面已被点击过。 |
| 触屏：轻点 = 显示拼音 + 发声 | 触屏没有悬停。轻点汉字**不能**触发翻页/滚动等页面手势（自己的应用里要核对）。 |
| 库优先、随项目提交 | 同一份处理好的录音可复现；有库就不需要 ffmpeg、Pinyin_Drill 目录和网络。 |
| 缺录音的优雅降级 | 上游没有的音节（如 ju4）：系统中文语音念单字，没有语音就只显示拼音，不报错。 |

体积估算：`录音条数 ≈ 文本里不同读音数`；一条约 3.8 KB，base64 后约 5 KB。小应用（几百字）通常 100–300 条，不到 1.5 MB；整本书 850 条约 4.3 MB。

## 2. 做法 A：静态 HTML

```
python -X utf8 scripts/wrap_html.py page.html -o page.pinyin.html --lib ./pinyin_clips [--rules my_rules.json]
```

输出是单文件：汉字已包 span、录音与脚本样式已内联、末尾有“开关 + 发音致谢”区块。多页站点对每个页面各跑一次，**用同一个 `--lib`**（录音库在页面之间共用，每页只内联它用到的）。

不会包的元素：`script style title head code pre kbd samp template button select option input a iframe svg math noscript textarea`，以及带 `data-nopy` / `translate="no"` 的元素。要多跳过某些标签：`--skip-tags nav,footer`。

## 3. 做法 B：JS 渲染的应用（SPA、数据驱动）

文本在运行期才拼进 DOM 时，**读音仍然在构建期标好**，和文本一起放进数据：

1. 构建脚本里（Python）：
   ```python
   sys.path.insert(0, SKILL + '/scripts')
   from pinyin_annotate import Annotator
   from pinyin_clips import build_clips
   ann = Annotator('my_rules.json')            # 没有就用默认起步规则
   used = set()
   for item in items:                          # 每一段会显示的汉字文本（含标题、按钮上想要点读的字）
       py = ann.annotate(item['text'])
       assert len(py) == len(re.findall('[一-鿿]', item['text']))
       item['py'] = ' '.join(py); used.update(py)
   uris, report = build_clips(used, 'pinyin_clips', neutral=ann.neutral)
   # 把 uris 写进页面：<script>window.__PYA={...};</script>（或你的构建系统能内联的任何方式）
   ```
2. 渲染时把文本换成 span：原生 JS 用 `PinyinHover.wrap(text, py)`（返回字符串/`<span class="hz">` 数组，`el.append(...nodes)`）；React/Vue 等直接写 `<span className="hz" data-p={p}>{ch}</span>`（`py.split(' ')` 与汉字按顺序一一对应；非汉字原样输出）。**页面文字内容不得改变。**
3. 内联 `pinyin_hover.css`/`.js`，应用启动后 `const api = PinyinHover.init({audio: window.__PYA, root: appRoot, toggle: '#pyh-toggle'})`。事件是在 `root` 上委托的，之后新渲染的 `.hz` 自动生效。
4. 换页/路由切换时调用 `api.hide(); api.stop()`；想让点读更即时，翻页后 `api.preload(本页用到的 id)`。
5. 在应用的设置里放“点字看拼音（开/关）”和“发音致谢”（见 `scripts/wrap_html.py` 里的 `CREDIT` 文案）。
6. 参考实现（数据驱动的绘本，含设置面板、翻页预解码、系统语音兜底）：本仓库 `stone-monkey-film/webapp/` 的 `build.py`、`app_pinyin.js`、`pinyin_audio.py`、`qa_pinyin.mjs`。

## 4. 无障碍与已知限制

- `.hz` span 不可聚焦，键盘用户用不了点读；屏幕阅读器读正文不受影响（文字未改）。需要键盘支持的应用，请自己给目标元素加 `tabindex` 和 Enter 触发。
- 气泡的 `aria-hidden="true"`：它是视觉辅助；不要依赖它传达必要信息。
- 行内标签把一个词劈成两半时（`<b>长</b>大`），读音上下文会丢（静态页做法 A 每个文本节点单独标注）。
- 录音是单字音节发音，不含连读变调以外的语流音变；“一/不”的变调由 pypinyin 处理。
- 浏览器：现代 Chrome/Edge/Safari/Firefox。自动化测试时 Chromium 需要 `--autoplay-policy=no-user-gesture-required`（`qa_pinyin.mjs` 已带）。

## 5. 许可（别省）

录音是 CC-BY-SA 3.0（Chen Wang 王琛 / audio-cmn）：发布的页面里必须有署名、说明“已裁剪转码、轻声为模拟”，处理后的录音同样以 CC-BY-SA 3.0 共享。`wrap_html.py` 默认带了致谢区块；做法 B 请自己放进设置/页脚。详见 `../assets/clips/ATTRIBUTION.md`。
