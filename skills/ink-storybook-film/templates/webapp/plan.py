#!/usr/bin/env python3
"""绘本网页的分页计划：把故事全文 (story/source.md) 切成“页”，每页对应一张画面。

输入  story/source.md、src/timeline.json、src/schedule.mjs 算出的字幕时间（out/storyboard_plan.json）
输出  webapp/out/plan.json   每页：章节、文字块、对应的影片字幕/分镜号、插图键

规则（详见 skill 文档 references/webapp-pipeline.md）
 1. 每条影片字幕（分镜 PPT 的一页）在原文里的位置是“锚点”，那一页的插图就是这条字幕的画面（不带字幕的干净帧）。
 2. 页从“锚点所在段落的开头”开始（同一段里有两条字幕时，第二页从那条字幕所在的句子开始）。
 3. 两个锚点之间如果文字太长，就按段落平均切成几页，插上“补充插图”（见 heroes.py）。
 4. 全文一个字都不丢、不重复、不乱序；build.py 会再核对一遍。
"""
import json, re, sys, math, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'webapp' / 'out'
OUT.mkdir(parents=True, exist_ok=True)

CPL = 25          # 1440×900 下文字区一行大约能放多少个字符（含标点）
CAP = 13.4        # 一页的目标行数（含段间距、章名占的行）；1440×900 上基本不用滚动
SOFT_MAX = 15.6   # 超过这个行数才强行再切
MIN_STUB = 95     # 锚点前面不足这么多字的“碎片”并进锚点那一页

HAN = re.compile(r'[一-鿿]')
norm = lambda t: re.sub(r'[\s“”"‘’\'「」]', '', t)
han = lambda t: len(HAN.findall(t))


def curly(par: str) -> str:
    """ASCII 引号 → 成对的弯引号（只改显示，不改字）。"""
    out, op = [], True
    for ch in par:
        if ch == '"':
            out.append('“' if op else '”'); op = not op
        else:
            out.append(ch)
    s = ''.join(out)
    # 单引号只出现在双引号里面（嵌套）
    res, op = [], True
    for ch in s:
        if ch == "'":
            res.append('‘' if op else '’'); op = not op
        else:
            res.append(ch)
    return ''.join(res)


def parse():
    lines = (ROOT / 'story/source.md').read_text(encoding='utf8').split('\n')
    secs, blocks, cur = [], [], []   # blocks: dict(sec, lines[], line_no)
    sec = -1
    title = ''
    def flush():
        nonlocal cur
        if cur:
            blocks.append({'sec': sec, 'lines': [l for _, l in cur], 'line': cur[0][0]})
            cur = []
    for i, l in enumerate(lines, 1):
        if l.startswith('# '):
            title = l[2:].strip(); continue
        if l.startswith('## '):
            flush(); sec += 1
            name = l[3:].strip()
            m = re.match(r'(第[一二三四五六七八九十]+节|开头|尾声)[　 ]+(.+)', name)
            secs.append({'no': m.group(1), 'name': m.group(2), 'raw': name})
            continue
        if not l.strip():
            flush(); continue
        cur.append((i, l))
    flush()
    return title, secs, blocks


SPLIT = re.compile(r'(?<=[。！？])(?![”’"\'])|(?<=[。！？][”’"\'])')


def sentences(text: str):
    """按句号等切句；引号收尾留在前一句。"""
    parts, buf, i = [], '', 0
    while i < len(text):
        ch = text[i]; buf += ch
        if ch in '。！？':
            j = i + 1
            while j < len(text) and text[j] in '"\'”’':
                buf += text[j]; j += 1
            i = j - 1
            parts.append(buf); buf = ''
        i += 1
    if buf: parts.append(buf)
    return parts


def build_units(blocks):
    """单位 = 句子（普通段落）或整行（诗、问题列表）；记住它属于哪个段落。"""
    units = []
    for bi, b in enumerate(blocks):
        if len(b['lines']) > 1:
            kind = 'poem' if b['lines'][0].startswith('雪花') else 'list'
            for k, l in enumerate(b['lines']):
                units.append({'blk': bi, 'sec': b['sec'], 'text': l, 'kind': kind, 'k': k, 'line': b['line'] + k})
        else:
            for k, sn in enumerate(sentences(b['lines'][0])):
                units.append({'blk': bi, 'sec': b['sec'], 'text': sn, 'kind': 'p', 'k': k, 'line': b['line']})
    return units


def main():
    title, secs, blocks = parse()
    units = build_units(blocks)
    for u in units:
        u['n'] = han(u['text'])
    total_han = sum(u['n'] for u in units)

    # —— 影片字幕 → 锚点
    sp = json.loads((ROOT / 'out/storyboard_plan.json').read_text(encoding='utf8'))   # 第 0 条是片头
    cues = [p for p in sp if p['scene'] != 's0-title']
    anchors = {}   # cue no(1..40) -> unit index
    for no, c in enumerate(cues, 1):
        t = norm(c['text']).strip('，、；：')
        hit = [i for i, u in enumerate(units) if t in norm(u['text'])]
        if not hit:  # 字幕跨了两个句子：把相邻两句拼起来找
            hit = [i for i in range(len(units) - 1) if units[i]['sec'] == units[i + 1]['sec'] and t in norm(units[i]['text'] + units[i + 1]['text'])]
        if len(hit) != 1:
            sys.exit(f'字幕 {no} 在原文里找到 {len(hit)} 处: {c["text"]}')
        anchors[no] = hit[0]

    # —— 切点
    cuts = {0}
    for no, ui in sorted(anchors.items(), key=lambda kv: kv[1]):
        blk = units[ui]['blk']
        start = ui
        while start > 0 and units[start - 1]['blk'] == blk:
            start -= 1
        # 同一段里已经有别的锚点在前面 → 从本锚点所在句开始
        prior = [a for a in anchors.values() if units[a]['blk'] == blk and a < ui]
        cut = ui if prior else start
        cuts.add(cut)   # 每条影片字幕都单独成页（一页一画面）；短页没关系，绘本本来就有字很少的页
    for i, u in enumerate(units):   # 章首也是切点（章名要在页首）
        if i == 0 or units[i - 1]['sec'] != u['sec']:
            cuts.add(i)
    # 章首与第一个锚点之间的碎片：并进锚点页（去掉章首切点以外的碎片切点）
    cl = sorted(cuts)
    final = []
    for k, c in enumerate(cl):
        nxt = cl[k + 1] if k + 1 < len(cl) else len(units)
        final.append((c, nxt))
    # 太短的页并入下一页（但不跨章，除非那一页是章首后紧跟锚点页）
    merged = []
    k = 0
    while k < len(final):
        a, b = final[k]
        n = han_between(units, a, b)
        has_anchor = any(a <= ui < b for ui in anchors.values())
        if n < MIN_STUB and not has_anchor and k + 1 < len(final) and units[final[k + 1][0]]['sec'] == units[a]['sec']:
            final[k + 1] = (a, final[k + 1][1]); k += 1; continue
        merged.append((a, b)); k += 1
    final = merged

    # —— 太长的跨度：按段落（实在不行按句）平均切开
    pages_u = []
    for a, b in final:
        n = lines_between(units, a, b)
        if n <= SOFT_MAX:
            pages_u.append((a, b)); continue
        k = max(2, math.ceil(n / CAP))
        # 候选切点：段落边界（块边界），其次句子边界
        bounds = [i for i in range(a + 1, b) if units[i]['blk'] != units[i - 1]['blk']]
        cum = lambda i: lines_between(units, a, i, head=units[a]['k'] == 0 and (a == 0 or units[a - 1]['sec'] != units[a]['sec']))
        chosen, last = [], a
        for j in range(1, k):
            target = n * j / k
            pool = [x for x in bounds if x > last]
            if not pool:
                pool = [i for i in range(last + 1, b)]
            # 选离目标最近、且不让两头太短的切点
            best = min(pool, key=lambda x: abs(cum(x) - target))
            # 如果最近的段落边界太远（段落本身很长），改用句子边界
            if abs(cum(best) - target) > CAP * 0.4:
                sent = [i for i in range(last + 1, b) if units[i]['kind'] == 'p']
                if sent:
                    best = min(sent, key=lambda x: abs(cum(x) - target))
            chosen.append(best); last = best
        pts = [a] + chosen + [b]
        for x, y in zip(pts, pts[1:]):
            if y > x:
                pages_u.append((x, y))

    # —— 出页
    pages = []
    for pi, (a, b) in enumerate(pages_u):
        cues_here = [no for no, ui in anchors.items() if a <= ui < b]
        secs_here = []
        for i in range(a, b):
            s = units[i]['sec']
            if not secs_here or secs_here[-1] != s: secs_here.append(s)
        starts_sec = a == 0 or units[a - 1]['sec'] != units[a]['sec']
        pages.append({
            'i': pi + 1,
            'sec': units[a]['sec'],
            'startsSec': bool(starts_sec),
            'cues': sorted(cues_here),
            'han': han_between(units, a, b),
            'u': [a, b],
            'paras': [],
        })

    # 引号配对：对原始块整体配对，再按单位切回去
    fix_quotes(pages, units, blocks)

    plan = {
        'title': title,
        'sections': secs,
        'cues': [{'no': no, 'scene': c['scene'], 'sceneName': c['sceneName'], 'idx': c.get('idx'), 'text': c['text'], 'tc': c['tc'], 'frame': c['frame'], 't': c['t']} for no, c in enumerate(cues, 1)],
        'titleCard': {'frame': sp[0]['frame'], 'tc': sp[0]['tc']},
        'pages': pages,
        'totalHan': total_han,
    }
    (OUT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding='utf8')
    # 报告
    print(f'汉字 {total_han}，共 {len(pages)} 页')
    for p in pages:
        sec = secs[p['sec']]
        head = f"{sec['no']} {sec['name']}" if p['startsSec'] else ''
        print(f"{p['i']:3d}  {p['han']:4d}字 {lines_between(units, *p['u']):5.1f}行  锚点{p['cues']!s:12}  {head}")


def han_between(units, a, b):
    return sum(u['n'] for u in units[a:b])


def lines_between(units, a, b, head=None):
    """粗略估算 units[a:b] 排成一页要占多少行：每段 ceil((字数+缩进)/每行字数) + 0.45 行段间距；章首另加章名的 3.4 行。"""
    if head is None:
        head = a == 0 or units[a - 1]['sec'] != units[a]['sec']
    total = 3.4 if head else 0.0
    i = a
    while i < b:
        blk = units[i]['blk']
        j, txt = i, ''
        while j < b and units[j]['blk'] == blk:
            if units[j]['kind'] != 'p':
                total += math.ceil(len(units[j]['text']) / CPL) + (0.9 if units[j]['k'] == 0 else 0)
            else:
                txt += units[j]['text']
            j += 1
        if txt:
            total += math.ceil((len(txt) + (2 if units[i]['k'] == 0 else 0)) / CPL) + 0.45
        i = j
    return total


def fix_quotes(pages, units, blocks):
    """把 ASCII 引号按“块”成对换成弯引号：先对整块配对，再把结果按单位长度切回去。"""
    # 块内字符串配对
    conv = {}
    for bi, b in enumerate(blocks):
        for k, l in enumerate(b['lines']):
            conv[(bi, k)] = curly(l)
    # 重新生成每页文字：单位 -> 转换后的文字
    ucur = {}
    for bi, b in enumerate(blocks):
        if len(b['lines']) > 1:
            continue
        full = conv[(bi, 0)]
        # 按句子切回（弯引号不影响句子切分点，因为我们逐字符对应）
        raw = b['lines'][0]
        sents = sentences(raw)
        pos = 0
        for k, sn in enumerate(sents):
            ucur[(bi, k)] = full[pos:pos + len(sn)]
            pos += len(sn)
    for p in pages:
        a, b = p['u']
        paras, last = [], None
        for ui in range(a, b):
            u = units[ui]
            if u['blk'] != last:
                paras.append({'kind': u['kind'], 'cont': u['k'] != 0, 'text': '', 'lines': []})
                last = u['blk']
            q = paras[-1]
            if u['kind'] == 'p':
                q['text'] += ucur[(u['blk'], u['k'])]
            else:
                q['lines'].append(conv[(u['blk'], u['k'])])
        # 下一页的续段：标记这一页是不是在段落中间结束
        endmid = b < len(units) and units[b]['blk'] == units[b - 1]['blk']
        p['paras'] = paras
        p['endsMid'] = bool(endmid)


if __name__ == '__main__':
    main()
