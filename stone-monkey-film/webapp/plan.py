#!/usr/bin/env python3
"""《小石猴点灯》绘本网页的分页计划：story/book_source.txt（加长版，几段拼起来的）→ 章节 → 页。

  输入  story/book_source.txt、webapp/heroes.json（可选：每章第 2、3… 张图的 at 决定在哪里换图、同时是硬分页点）
  输出  webapp/out/plan.json

book_source.txt 的规则（解析器 parse_source() 处理）
 1. 行首 `#`：批注，丢弃。空行丢弃。
 2. 行首 `【…】`：
      - `【第X分 …】` / `【增补X · …】`：章标题（章名在“分”的编号上，X 是中文数字）；
      - `【封面】…`：`】` 之后的话是封面标语，不进正文；
      - `【附：…】`：故事用字表，后面什么都没有，整行丢弃（它之后、下一个 `【` 之前的裸行也一并丢弃）；
      - 其余 `【12】…` / `【99 · 春游】…` / `【地下1】…`：`】` 之后的文字是正文（一个自然段）；`·` 后面的名字（春游…）
        是该段前面一个很小的灰色小标签（纯数字不显示；与章名重复的不显示）。小标签不算正文。
 3. 其余每个非批注行 = 一个自然段，原样保持，不改一个字、不增删标点（显示用的 ASCII 引号配成弯引号除外）。
 4. 章节在文件里的出现顺序是乱的，绘本按下面的 ORDER 排（缺第二、第十五，不补）。
"""
import json, math, pathlib, re, sys

# —— 章节顺序（按“分”的编号；增补一~四放在第六分之后、第七分之前）。要换顺序就改这里。
ORDER = [
    '第一分', '第三分', '第四分', '第五分', '第六分',
    '增补一', '增补二', '增补三', '增补四',
    '第七分', '第八分', '第九分', '第十分', '第十一分',
    '第十二分', '第十三分', '第十四分',
    '第十六分', '第十七分', '第十八分', '第十九分', '第二十分', '第二十一分',
]

# —— 分页常数（1440×900 桌面下，文字区一行约放 CPL 个字，一页目标 CAP 行）。QA 里会列出需要滚动的页，据此微调。
CPL = 24          # 一行能放多少个字符（含标点；考虑了避头尾，比理论值略小）
CAP = 12.6        # 一页的目标行数（含段间距、章名占的行）
SOFT_MAX = 14.2   # 超过这个行数就必须再切
HEAD_LINES = 3.9  # 章名（小字章号 + 大字章名 + 小灯分隔线）占几行
GAP = 0.5         # 段间距（行）
INDENT = 2        # 段首缩进（字）

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'story' / 'book_source.txt'
HEROES = ROOT / 'webapp' / 'heroes.json'
OUT = ROOT / 'webapp' / 'out'

CHAP_RE = re.compile(r'^(第[一二三四五六七八九十]+分|增补[一二三四五六七八九十]+)\s*(?:·\s*)?(.*)$')
HAN = re.compile(r'[一-鿿]')
han = lambda t: len(HAN.findall(t))


# ───────────────────────── 解析 ─────────────────────────
def curly(par: str) -> str:
    """ASCII 直引号 → 成对的弯引号（只改显示，不改字；逐字符一一对应）。"""
    out, op = [], True
    for ch in par:
        if ch == '"':
            out.append('“' if op else '”'); op = not op
        else:
            out.append(ch)
    s = ''.join(out)
    res, op = [], True
    for ch in s:
        if ch == "'":
            res.append('‘' if op else '’'); op = not op
        else:
            res.append(ch)
    return ''.join(res)


def parse_mark(label: str):
    """'99 · 春游' → ('99','春游')；'117 · 物' → ('117','物')；'地下1' → ('地下1','地下')；'12' → ('12','')。"""
    parts = [s.strip() for s in label.split('·')]
    first = parts[0]
    if re.fullmatch(r'\d+', first):
        return first, ' · '.join(parts[1:])
    return first, re.sub(r'\d+$', '', first)


def parse_source(path=SRC):
    """→ (tagline, chapters)；chapters 按文件里的出现顺序，每章 {key,no,name,raw,paras:[{text,mid,tag}]}。"""
    tagline, chapters, cur, skipping, dropped = '', [], None, False, 0
    for ln, line in enumerate(path.read_text(encoding='utf8').split('\n'), 1):
        line = line.rstrip('\r')
        if not line.strip() or line.startswith('#'):
            continue
        mid, tag = '', ''
        if line.startswith('【'):
            j = line.find('】')
            if j < 0:
                sys.exit(f'{path.name}:{ln} 行首有【但没有】: {line[:40]}')
            label, rest = line[1:j].strip(), line[j + 1:]
            m = CHAP_RE.match(label)
            if m:
                cur = {'key': m.group(1), 'no': m.group(1), 'name': m.group(2).strip(), 'raw': label, 'paras': []}
                chapters.append(cur); skipping = False
                if rest.strip():
                    sys.exit(f'{path.name}:{ln} 章标题行后面还有文字: {rest[:30]}')
                continue
            if label.startswith('附：') or label.startswith('附:'):
                skipping = True; continue
            skipping = False
            if label.startswith('封面'):
                tagline = rest.strip(); continue
            if not rest.strip():
                print(f'  提示：{path.name}:{ln} 【{label}】后面没有文字，当作批注丢弃')
                continue
            text = rest
            mid, tag = parse_mark(label)
        else:
            if skipping:
                dropped += 1; continue
            text = line
        if cur is None:
            sys.exit(f'{path.name}:{ln} 出现在任何章标题之前: {text[:30]}')
        cur['paras'].append({'text': curly(text), 'mid': mid, 'tag': tag})
    if dropped:
        print(f'  提示：“附：故事用字表”之后丢弃了 {dropped} 行裸文字')
    for c in chapters:
        for p in c['paras']:
            if p['tag'] and p['tag'] in c['name']:
                p['tag'] = ''          # 与章名重复（如 增补三 · 地下 里的【地下1】）就不显示
    return tagline, chapters


def ordered(chapters):
    """按 ORDER 排序，并检查：文件里的章都在 ORDER 里、ORDER 里的章都在文件里、没有重复。"""
    by = {}
    for c in chapters:
        if c['key'] in by:
            sys.exit(f"章“{c['key']}”在文件里出现了两次")
        by[c['key']] = c
    extra = [k for k in by if k not in ORDER]
    miss = [k for k in ORDER if k not in by]
    if extra:
        sys.exit(f'文件里有 ORDER 没列的章: {extra}（请加进 plan.py 顶部的 ORDER）')
    if miss:
        sys.exit(f'ORDER 里有但文件里没有的章: {miss}')
    return [by[k] for k in ORDER]


# ───────────────────────── 切句 ─────────────────────────
def sentences(text: str):
    """按 。！？ 切句；引号收尾留在前一句；“…” 里面的句号不切（一句引语不拆开）。"""
    out, buf, depth, i, n = [], '', 0, 0, len(text)
    while i < n:
        ch = text[i]; buf += ch; i += 1
        if ch == '“': depth += 1
        elif ch == '”': depth = max(0, depth - 1)
        split = False
        if depth == 0:
            if ch in '。！？':
                while i < n and text[i] in '’」）”':   # 收尾的引号/括号跟着前一句（含跨段引语里落单的 ”）
                    buf += text[i]; i += 1
                split = True
            elif ch == '”' and len(buf) >= 2 and buf[-2] in '。！？…':
                split = True
        if split:
            out.append(buf); buf = ''
    if buf:
        out.append(buf)
    return out


def build_units(chap):
    units = []
    for pi, p in enumerate(chap['paras']):
        for k, sn in enumerate(sentences(p['text'])):
            units.append({'pi': pi, 'k': k, 'text': sn, 'n': han(sn)})
    return units


# ───────────────────────── 行数估算 ─────────────────────────
def lines_between(chap, units, a, b, head=False):
    """估算 units[a:b] 排成一页要占多少行：每段 ceil((字数+缩进+小标签)/每行字数) + 段间距；章首另加章名。"""
    total = HEAD_LINES if head else 0.0
    i = a
    while i < b:
        pi, j, n = units[i]['pi'], i, 0
        while j < b and units[j]['pi'] == pi:
            n += len(units[j]['text']); j += 1
        first = units[i]['k'] == 0
        tag = chap['paras'][pi]['tag']
        extra = (INDENT if first else 0) + ((len(tag) * 0.62 + 1.0) if (tag and first) else 0)
        total += math.ceil((n + extra) / CPL) + GAP
        i = j
    return total


def cut_penalty(chap, units, x):
    """在 units[x-1] | units[x] 之间切开要付的“代价”：段落边界最便宜，句子中间贵，冒号引出的下文尽量不拆开。"""
    prev, cur = units[x - 1], units[x]
    pen = 0.0
    if cur['pi'] == prev['pi']:
        pen += 2.6                                     # 切在段落中间（句号处）
    else:
        if cur['k'] == 0 and chap['paras'][cur['pi']]['mid']:
            pen -= 0.3                                 # 刚好是一个“小节”的开头：最好
    last = prev['text'].rstrip('”’」）')
    if last.endswith(('：', '——', '，', '；')):
        pen += 2.4                                     # 上一句是引出下文的（“他问：”“有一长串：”）
    return pen


def split_span(chap, units, a, b, head):
    """把 units[a:b] 切成最少的几页，每页 ≤ SOFT_MAX 行；在这个页数下让各页行数尽量均匀、切点尽量落在段落/小节边界。"""
    n = b - a
    L = lambda x, y: lines_between(chap, units, x, y, head=(head and x == a))
    total = L(a, b)
    if total <= SOFT_MAX:
        return [(a, b)]
    INF = 1e9
    for k in range(max(2, math.ceil(total / SOFT_MAX)), n + 1):
        mean = total / k
        # dp[j][i]：把 units[a:i] 切成 j 页的最小代价
        dp = [[INF] * (n + 1) for _ in range(k + 1)]
        bk = [[-1] * (n + 1) for _ in range(k + 1)]
        dp[0][0] = 0.0
        for j in range(1, k + 1):
            for i in range(j, n + 1):
                for s in range(j - 1, i):
                    if dp[j - 1][s] >= INF:
                        continue
                    ln = L(a + s, a + i)
                    if ln > SOFT_MAX:
                        continue
                    c = dp[j - 1][s] + (ln - mean) ** 2 * 0.35 + (cut_penalty(chap, units, a + s) if s else 0.0)
                    if c < dp[j][i]:
                        dp[j][i], bk[j][i] = c, s
        if dp[k][n] < INF:
            cuts, i = [], n
            for j in range(k, 0, -1):
                s = bk[j][i]; cuts.append((a + s, a + i)); i = s
            return cuts[::-1]
    return [(a, b)]


# ───────────────────────── 配图表里的“换图点” ─────────────────────────
def load_hero_cuts(chap, heroes):
    """heroes.json 里这一章的图片列表若每一项（第 2 项起）都有 at，则 at 指向的段落开头是硬分页点。
       at: "104"（小标记【104 · 农忙】）/ "地下2"（【地下2】）/ "#7"（本章第 7 段）。→ 段落序号列表（第 1 项从 0 开始）。"""
    lst = (heroes.get('sections') or {}).get(chap['key'])
    if not lst or len(lst) < 2:
        return None
    ats = [e.get('at') for e in lst[1:]]
    if not any(ats):
        return None
    if not all(ats):
        sys.exit(f"heroes.json 里“{chap['key']}”：第 2 项起要么都写 at，要么都不写（现在只有一部分写了）")
    out = [0]
    for e in lst[1:]:
        at = str(e['at'])
        if at.startswith('#'):
            pi = int(at[1:]) - 1
        else:
            pis = [i for i, p in enumerate(chap['paras']) if p['mid'] == at]
            if not pis:
                sys.exit(f"heroes.json 里“{chap['key']}”的 at \"{at}\" 在这一章里找不到对应的小标记")
            pi = pis[0]
        if not (0 < pi < len(chap['paras'])) or pi <= out[-1]:
            sys.exit(f"heroes.json 里“{chap['key']}”的 at \"{at}\"（第 {pi + 1} 段）必须在前一张图之后、且不是本章第 1 段")
        out.append(pi)
    return out


# ───────────────────────── 主流程 ─────────────────────────
def make_plan():
    tagline, chs = parse_source()
    chs = ordered(chs)
    heroes = json.loads(HEROES.read_text('utf8')) if HEROES.exists() else {}
    pages, report = [], []
    for si, c in enumerate(chs):
        units = build_units(c)
        cuts = load_hero_cuts(c, heroes)
        segs = []                                    # (a, b, seg序号 或 None)
        if cuts:
            starts = [next(i for i, u in enumerate(units) if u['pi'] == pi) for pi in cuts]
            for sidx, a in enumerate(starts):
                b = starts[sidx + 1] if sidx + 1 < len(starts) else len(units)
                segs.append((a, b, sidx))
        else:
            segs.append((0, len(units), None))
        for a, b, sidx in segs:
            for x, y in split_span(c, units, a, b, head=(a == 0)):
                paras, last = [], None
                for ui in range(x, y):
                    u = units[ui]
                    if u['pi'] != last:
                        p = c['paras'][u['pi']]
                        paras.append({'text': '', 'cont': u['k'] != 0, 'tag': p['tag'] if u['k'] == 0 else '', 'mid': p['mid']})
                        last = u['pi']
                    paras[-1]['text'] += u['text']
                pg = {'i': len(pages) + 1, 'sec': si, 'startsSec': x == 0, 'han': sum(u['n'] for u in units[x:y]),
                      'paras': paras, 'seg': sidx}
                pages.append(pg)
                report.append((pg['i'], c['key'], pg['han'], lines_between(c, units, x, y, head=(x == 0)),
                               [p['mid'] for p in paras if p['mid'] and not p['cont']], sidx))
    plan = {
        'tagline': tagline,
        'sections': [{'key': c['key'], 'no': c['no'], 'name': c['name'], 'raw': c['raw']} for c in chs],
        'pages': pages,
        'totalHan': sum(p['han'] for p in pages),
    }
    return plan, report


def main():
    plan, report = make_plan()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1), 'utf8')
    print(f"汉字 {plan['totalHan']}，{len(plan['sections'])} 章，共 {len(plan['pages'])} 页")
    if '-q' in sys.argv:
        return
    for i, key, n, ln, beats, seg in report:
        print(f"{i:3d}  {key:6s} {n:4d}字 {ln:5.1f}行  图#{'-' if seg is None else seg}  小节 {','.join(beats)}")


if __name__ == '__main__':
    main()
