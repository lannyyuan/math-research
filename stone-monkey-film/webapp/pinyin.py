#!/usr/bin/env python3
"""汉字 → 拼音（构建期）。每个汉字一个读音，声调用数字：zhang3、de5（轻声=5）、nv3（ü 写作 v）。

  from pinyin import annotate;  annotate('他长大了')  →  ['ta1', 'zhang3', 'da4', 'le5']

流程：pypinyin（词语上下文，处理多音字、一/不变调）→ pinyin_overrides.json 的规则依次改写（得/着/地/落/长/种…）。
运行期网页里没有任何转换引擎，只查构建期写进数据的读音。

  python3 -X utf8 webapp/pinyin.py --review     重写 webapp/pinyin_review.md（全书多音字/规则命中处，供人工复核）
  python3 -X utf8 webapp/pinyin.py "要标注的句子"   打印标注结果
"""
import json, pathlib, re, sys, collections

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
HAN = re.compile('[一-鿿]')

try:
    from pypinyin import pinyin as _pinyin, Style
except ImportError:      # pragma: no cover
    sys.exit('缺少 pypinyin：请先 `python3 -m pip install pypinyin`')

_RULES = None


def rules():
    global _RULES
    if _RULES is None:
        spec = json.loads((HERE / 'pinyin_overrides.json').read_text('utf8'))
        out = []
        for r in spec['rules']:
            m = re.search('«(.)»', r['ctx'])
            if not m:
                raise ValueError(f"规则缺少 «字» 标记：{r['ctx']}")
            ctx = r['ctx']
            left, tgt, right = ctx[:m.start()], m.group(1), ctx[m.end():]
            # (?=left(?P<t>tgt)right) 用前瞻，重叠位置也能命中；命名组 t 就是要改的字（不打乱规则里 \1 之类的回溯编号）
            rx = re.compile(f'(?=(?:{left})(?P<t>{re.escape(tgt)})(?:{right}))')
            out.append((rx, r['py'], set(r.get('when') or []), r['ctx']))
        _RULES = out
        _RULES_META.update({'neutral': spec.get('neutral', {})})
    return _RULES


_RULES_META = {}


def neutral_spec():
    rules()
    return _RULES_META['neutral']


def annotate(text: str, trace=None) -> list:
    """text 里每个汉字（按出现顺序）一个读音。trace 传入 list 时，记录被规则改写的 (位置, 旧, 新, 规则)。"""
    pos = [i for i, ch in enumerate(text) if HAN.match(ch)]
    py = [None] * len(pos)
    idx = {p: k for k, p in enumerate(pos)}
    for m in re.finditer('[一-鿿]+', text):
        seg = m.group()
        got = _pinyin(seg, style=Style.TONE3, neutral_tone_with_five=True, v_to_u=False, strict=False)
        for k, (p,) in enumerate(got):
            s = p if re.search(r'\d$', p) else p + '5'     # 保险：没有声调数字的当轻声
            py[idx[m.start() + k]] = s
    for rx, new, when, desc in rules():
        for m in rx.finditer(text):
            at = m.start('t')
            k = idx.get(at)
            if k is None:
                continue
            if when and py[k] not in when:
                continue
            if py[k] != new:
                if trace is not None:
                    trace.append((at, py[k], new, desc))
                py[k] = new
    return py


# ───────────── 声调数字 → 带调符号（只用于审校/测试；网页里有同样的 JS 实现） ─────────────
_TONES = {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'v': 'ǖǘǚǜ'}


def mark(py: str) -> str:
    m = re.fullmatch(r'([a-z]+)([1-5])', py)
    if not m:
        return py
    s, t = m.group(1), int(m.group(2))
    if t == 5:
        return s.replace('v', 'ü')
    # 标调规则：a、e 优先；ou 标 o；其余标最后一个元音
    for pref in ('a', 'e'):
        if pref in s:
            i = s.index(pref)
            break
    else:
        if 'ou' in s:
            i = s.index('o')
        else:
            vs = [k for k, c in enumerate(s) if c in 'aeiouv']
            if not vs:
                return s
            i = vs[-1]
    c = s[i]
    s = s[:i] + _TONES[c][t - 1] + s[i + 1:]
    return s.replace('v', 'ü')


# ───────────── 审校报告 ─────────────
def book_paragraphs():
    """和 plan.py 一致：行首 # 丢弃；【…】之后是正文；章名也算。→ [(章, 文本)]"""
    out = []
    cur = ''
    for line in (ROOT / 'story' / 'book_source.txt').read_text('utf8').splitlines():
        if not line.strip() or line[0] == '#':
            continue
        if line[0] == '【':
            e = line.index('】')
            lab, body = line[1:e], line[e + 1:]
            if lab.startswith('附') or lab.startswith('封面'):
                continue
            if lab.startswith('增补') or (lab.startswith('第') and '分' in lab[:5]):
                cur = lab.split(' ')[0]
                out.append((cur, lab.split(' ', 1)[1] if ' ' in lab else ''))
                continue
        else:
            body = line
        out.append((cur, body))
    return out


def review(path=HERE / 'pinyin_review.md'):
    rows = collections.defaultdict(lambda: collections.defaultdict(list))
    traced = collections.defaultdict(lambda: collections.defaultdict(list))
    tot = 0
    for chap, text in book_paragraphs():
        tr = []
        py = annotate(text, tr)
        hz = [i for i, ch in enumerate(text) if HAN.match(ch)]
        for k, i in enumerate(hz):
            ctx = text[max(0, i - 4):i] + '【' + text[i] + '】' + text[i + 1:i + 5]
            rows[text[i]][py[k]].append(ctx.replace('\n', ''))
            tot += 1
        for at, old, new, desc in tr:
            traced[text[at]][(old, new, desc)].append(text[max(0, at - 4):at] + '【' + text[at] + '】' + text[at + 1:at + 5])
    poly = {c: v for c, v in rows.items() if len(v) > 1}
    lines = ['# 拼音读音复核表（自动生成，请勿手改）', '',
             f'全书汉字 {tot} 个；出现不止一种读音的字 {len(poly)} 个（下表全部列出）；被规则改写的字 {len(traced)} 个（后面单列）。',
             '改读音：编辑 `webapp/pinyin_overrides.json` 的规则，再运行 `python3 -X utf8 webapp/pinyin.py --review`。', '',
             '## 一、多音字（按出现次数）', '']
    for c in sorted(poly, key=lambda c: -sum(len(x) for x in poly[c].values())):
        lines.append(f'### {c}（' + '、'.join(f'{mark(p)} ×{len(v)}' for p, v in sorted(poly[c].items(), key=lambda kv: -len(kv[1]))) + '）')
        for p, v in sorted(poly[c].items(), key=lambda kv: -len(kv[1])):
            shown = v[:6]
            lines.append(f'- **{mark(p)}**：' + '　'.join(shown) + (f'　…共 {len(v)} 处' if len(v) > 6 else ''))
        lines.append('')
    lines += ['## 二、规则改写过的位置（pypinyin 默认值 → 规则结果）', '']
    for c in sorted(traced, key=lambda c: -sum(len(x) for x in traced[c].values())):
        for (old, new, desc), v in traced[c].items():
            lines.append(f'- **{c}** {mark(old)} → **{mark(new)}** ×{len(v)}　规则 `{desc}`　例：' + '　'.join(v[:4]))
    path.write_text('\n'.join(lines) + '\n', 'utf8')
    print(f'写出 {path}（多音字 {len(poly)} 个，规则改写 {sum(len(v) for t in traced.values() for v in t.values())} 处）')


if __name__ == '__main__':
    if '--review' in sys.argv:
        review()
    else:
        t = ' '.join(a for a in sys.argv[1:] if not a.startswith('--')) or '他长大了，老师教他背书。'
        py = annotate(t)
        print(' '.join(f'{c}:{mark(p)}' for c, p in zip([c for c in t if HAN.match(c)], py)))
