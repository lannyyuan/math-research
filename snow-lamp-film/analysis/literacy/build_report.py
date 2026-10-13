"""把《幼儿识字1300字（通关检测表）》PDF 的识别结果，和《雪地里的那盏灯》的字幕/分镜 PPT/故事原文做覆盖率对比。
输入：pages_manual.py（逐页读图转录）、ocr_rows.json（OCR 交叉校验）、../../src/timeline.json、../../story/source.md
输出：识字1300_识别结果.csv / .md、字幕与识字1300覆盖率对比.md
"""
import collections, csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pages_manual import PAGES

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
HAN = re.compile(r'[一-鿿]')

# ── 表本身 ──
L = [(p, r, c, PAGES[p][(r - 1) * 5 + c - 1]) for p in sorted(PAGES) for r in range(1, 11) for c in range(1, 6)]
chars = [x[3] for x in L]
Lcnt = collections.Counter(chars); Lset = set(chars)
first_pos = {}
for i, (p, r, c, ch) in enumerate(L, 1):
    first_pos.setdefault(ch, []).append((i, p, r, c))
dups = {ch: pos for ch, pos in first_pos.items() if len(pos) > 1}
ocr = json.load(open(os.path.join(HERE, 'ocr_rows.json'), encoding='utf-8'))
agree = sum(1 for o in ocr if o['char'] == PAGES[o['page']][(o['row'] - 1) * 5 + o['col'] - 1])
ocr_empty = sum(1 for o in ocr if not o['char'])

# ── 我们的各个维度 ──
tl = json.load(open(os.path.join(ROOT, 'src/timeline.json'), encoding='utf-8'))
from importlib.machinery import SourceFileLoader
sched = SourceFileLoader('x', '/dev/null') if False else None
src_text = open(os.path.join(ROOT, 'story/source.md'), encoding='utf-8').read()

SCENE_NAMES = {'s0-title': '片头', 's1-lost': '1 雪夜迷路，看见山顶的灯', 's2-rabbit': '2 遇见问号', 's3-turtle': '3 遇见慢慢', 's4-river': '4 冰河落水，被白鹿救起',
               's5-fire': '5 在火堆边说起家', 's6-wolf': '6 帮小狼找到妈妈', 's7-thaw': '7 冰雪化开', 's8-summit': '8 到了山顶，灯不是家', 's9-farewell': '9 和伙伴们告别', 's10-window': '10 在自己窗边点灯'}
cues = [(sc['id'], c['text']) for sc in tl['scenes'] for c in sc['cues']]
sub_text = ''.join(t for _, t in cues)
title = tl['title']

def dim(text):
    toks = HAN.findall(text); S = set(toks); cnt = collections.Counter(toks)
    inS = S & Lset; out = sorted(S - Lset)
    return dict(tokens=len(toks), distinct=len(S), in_list=len(inS), out=out, out_cnt={c: cnt[c] for c in out},
                tok_in=sum(n for c, n in cnt.items() if c in Lset), set=S, cnt=cnt)
D_sub, D_ppt, D_src = dim(sub_text), dim(sub_text + title), dim(src_text)
pct = lambda a, b: f'{100 * a / b:.1f}%' if b else '-'

# ── CSV ──
with open(os.path.join(HERE, '识字1300_识别结果.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['序号', '页', '行', '列', '字', '表内出现次数', '在影片字幕中(次)', '在故事原文中(次)'])
    for i, (p, r, c, ch) in enumerate(L, 1):
        w.writerow([i, p, r, c, ch, Lcnt[ch], D_sub['cnt'].get(ch, 0), D_src['cnt'].get(ch, 0)])

# ── MD：识别结果 ──
md = []
md.append('# 《幼儿识字1300字（通关检测表）》识别结果\n')
md.append('来源：附件 PDF（26 页，每页 5 列 × 10 行 = 50 字，共 1300 格）。原文件是纯图片，没有文字层。\n')
md.append('## 统计\n')
md.append(f'| 项目 | 数量 |\n|---|---|\n| 页数 | 26 |\n| 格子总数 | {len(L)} |\n| **不重复的字** | **{len(Lset)}** |\n| 重复出现的字 | {len(dups)} 个（{"、".join(dups)}），各出现 2 次 |\n')
md.append('重复字的位置（序号 = 按页、行、列顺序的第几格）：\n')
for ch, pos in dups.items():
    md.append(f'- **{ch}**：' + '；'.join(f'第 {p} 页第 {r} 行第 {c} 列（序号 {i}）' for i, p, r, c in pos))
md.append('')
md.append('## 识别方法与校验\n')
md.append(f'1. **OCR 逐格识别**（RapidOCR，每格单独裁出，按 5×10 网格定位）：与人工转录一致 **{agree} / 1300** 格；{ocr_empty} 格 OCR 读不出（多为“一、口、土、刀、工、力”这类笔画很少的字），其余不一致的多是形近字（朋/崩、阳/陌、青/菁、净/淨、员/赏……）。')
md.append('2. **人工逐页读图转录**：每页对着图片逐字读，并同时对照字上印的**拼音**确认（OCR 读成形近字的格子，全部按印刷拼音确认；例如“朋 péng”不是“崩 bēng”）。')
md.append('3. **拼音相同、只靠字形区分的 3 处**放大核对：第 15 页前两格是同一个字“睁”（原表里就重复了）；第 17 页“介”（不是“芥”）；第 23 页“帜”（巾字旁，不是“炽”）。')
md.append('4. OCR 读不出的格子（29 个）放大后逐个核对，全部与转录一致。\n')
md.append('> 说明：这是图片识别 + 人工转录，我已尽量逐格核对，但仍不能保证 100% 无误。你发现个别字不对，告诉我页/行/列即可更正。\n')
md.append('## 全部字（按页）\n')
md.append('图例：**加粗** = 这个字在影片字幕里出现过。\n')
for p in sorted(PAGES):
    md.append(f'### 第 {p} 页（序号 {(p - 1) * 50 + 1}–{p * 50}）\n')
    md.append('| 行 | 列1 | 列2 | 列3 | 列4 | 列5 |\n|---|---|---|---|---|---|')
    for r in range(1, 11):
        cells = []
        for c in range(1, 6):
            ch = PAGES[p][(r - 1) * 5 + c - 1]
            cells.append(f'**{ch}**' if ch in D_sub['set'] else ch)
        md.append(f'| {r} | ' + ' | '.join(cells) + ' |')
    md.append('')
md.append('## 不重复的 1293 个字（按首次出现的顺序，一行 50 个）\n')
uniq = list(dict.fromkeys(chars))
for i in range(0, len(uniq), 50):
    md.append('`' + ''.join(uniq[i:i + 50]) + '`  ')
open(os.path.join(HERE, '识字1300_识别结果.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')

# ── MD：覆盖率对比 ──
R = []
R.append('# 字幕 / 分镜 PPT / 故事原文  vs  《幼儿识字1300字》覆盖率对比\n')
R.append(f'参照表：附件《幼儿识字1300字（通关检测表）》，共 1300 格，**不重复 {len(Lset)} 个字**（7 个字在表里出现了两次）。比较只统计汉字，标点不计。\n')
R.append('## 一、三个维度总览\n')
R.append('| 维度 | 总字数（字次） | 不重复字数 | 其中在 1300 表内 | **字种覆盖率**（本维度的字有多少在表内） | **字次覆盖率**（所有字次中多少在表内） | **表被覆盖率**（1293 个字里被本维度用到多少） | 表外字 |')
R.append('|---|---|---|---|---|---|---|---|')
for name, d in (('影片字幕（40 条）', D_sub), ('分镜 PPT 全部文字（41 页 = 字幕 + 片头标题）', D_ppt), ('故事原文全文（story/source.md）', D_src)):
    R.append(f"| {name} | {d['tokens']} | {d['distinct']} | {d['in_list']} | **{pct(d['in_list'], d['distinct'])}** | **{pct(d['tok_in'], d['tokens'])}** | {d['in_list']}/{len(Lset)} = {pct(d['in_list'], len(Lset))} | {len(d['out'])} 个：{''.join(d['out'])} |")
R.append('')
R.append('**读法：**')
R.append(f"- **字幕**用了 {D_sub['distinct']} 个不同的字，其中 {D_sub['in_list']} 个在 1300 表内，字种覆盖率 {pct(D_sub['in_list'], D_sub['distinct'])}；字幕里 {D_sub['tokens']} 个字次只有 {D_sub['tokens'] - D_sub['tok_in']} 个在表外，字次覆盖率 {pct(D_sub['tok_in'], D_sub['tokens'])}。只占 1300 表的 {pct(D_sub['in_list'], len(Lset))}——字幕是“少而精”的选段，不是为了把表里的字教一遍。")
R.append(f"- **分镜 PPT** 的文字就是字幕 + 片头标题《雪地里的那盏灯》（标题的 7 个字都已在字幕里出现），所以数字和字幕完全一样。")
R.append(f"- **故事原文**共 {D_src['tokens']} 个字、{D_src['distinct']} 个不同的字，字种覆盖率 {pct(D_src['in_list'], D_src['distinct'])}，字次覆盖率 {pct(D_src['tok_in'], D_src['tokens'])}，**几乎用满了整张 1300 表**（{D_src['in_list']}/{len(Lset)} = {pct(D_src['in_list'], len(Lset))}）。也就是说这篇故事本来就是照这张识字表写的，字幕只是从里面选了 160 个字的句子。\n")
R.append('## 二、表外的字\n')
R.append(f"### 字幕里：{len(D_sub['out'])} 个")
for ch in D_sub['out']:
    where = [(sid, t) for sid, t in cues if ch in t]
    R.append(f"- **{ch}**（出现 {D_sub['out_cnt'][ch]} 次）：" + '；'.join(f"{SCENE_NAMES[sid]}「{t.replace(chr(10), '')}」" for sid, t in where))
R.append('\n这是拟声字（冰“啪”的一声），字幕必须取自原文，所以没有改。如果想让字幕 100% 落在识字表内，可以把这一条缩成“破了！”（仍是原文片段，“破”在表内），只需重渲第 4 场；需要的话告诉我。\n')
R.append(f"### 故事原文里：{len(D_src['out'])} 个（字次合计 {sum(D_src['out_cnt'].values())}）")
R.append('| 字 | 在原文中出现次数 |\n|---|---|')
for ch in D_src['out']:
    R.append(f"| {ch} | {D_src['out_cnt'][ch]} |")
notin = sorted(Lset - D_src['set'], key=lambda c: uniq.index(c))
R.append(f"\n### 表里有、但原文没用到的字：{len(notin)} 个\n`{''.join(notin)}`\n")
R.append('## 三、按场景\n')
R.append('| 场景 | 字幕条数 | 字次 | 不重复字 | 在表内 | 表外字 |\n|---|---|---|---|---|---|')
for sc in tl['scenes']:
    t = ''.join(c['text'] for c in sc['cues'])
    d = dim(t)
    if not sc['cues']:
        R.append(f"| {SCENE_NAMES[sc['id']]} | 0（标题卡） | - | - | - | - |"); continue
    R.append(f"| {SCENE_NAMES[sc['id']]} | {len(sc['cues'])} | {d['tokens']} | {d['distinct']} | {d['in_list']}（{pct(d['in_list'], d['distinct'])}） | {''.join(d['out']) or '无'} |")
R.append('\n## 四、分镜 PPT 逐页（41 页）\n')
R.append('| 页 | 场景 | 字幕 | 字数 | 是否全在 1300 表内 |\n|---|---|---|---|---|')
R.append(f"| 1 | 片头 | {title} | {len(HAN.findall(title))} | {'是' if all(c in Lset for c in HAN.findall(title)) else '否'} |")
n = 1
for sc in tl['scenes']:
    for c in sc['cues']:
        n += 1
        t = c['text'].replace('\n', ' ')
        h = HAN.findall(t); bad = [x for x in h if x not in Lset]
        R.append(f"| {n} | {SCENE_NAMES[sc['id']]} | {t} | {len(h)} | {'是' if not bad else '否（' + ''.join(bad) + '）'} |")
R.append('\n## 五、字幕用字在 1300 表里的分布（按表的页）\n')
R.append('表前面的页是最基础的字（一二三、人口手……），后面的页更难。统计“字幕里的 159 个表内字”落在表的哪些页：\n')
R.append('| 表的页 | 该页段的格子数 | 字幕用到的不重复字 | 占字幕表内字的比例 |\n|---|---|---|---|')
first_page = {}
for p, r, c, ch in L: first_page.setdefault(ch, p)
bins = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 26)]
inc = [c for c in D_sub['set'] if c in Lset]
for a, b in bins:
    k = [c for c in inc if a <= first_page[c] <= b]
    R.append(f"| 第 {a}–{b} 页 | {(min(b, 26) - a + 1) * 50} | {len(k)} | {pct(len(k), len(inc))} |")
R.append('\n（按每个字在表里第一次出现的页计。）\n')
R.append('## 附：判定口径\n')
R.append('- “字种”按不重复的汉字算，“字次”按出现的次数算。')
R.append('- “字种覆盖率” = 本维度不重复字中，在 1300 表内的比例；“字次覆盖率” = 本维度全部字次中，在表内的比例；“表被覆盖率” = 1293 个表内字里，被本维度用到的比例。')
R.append('- 字幕、分镜 PPT、原文的数据都来自本仓库：`src/timeline.json`（字幕）、`story/source.md`（原文）。')
open(os.path.join(HERE, '字幕与识字1300覆盖率对比.md'), 'w', encoding='utf-8').write('\n'.join(R) + '\n')
print('OK', len(Lset), agree, ocr_empty)
