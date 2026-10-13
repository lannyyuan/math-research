#!/usr/bin/env python3
"""汉字 → 拼音 id（构建期）。每个汉字一个读音，声调用数字：zhang3、de5（轻声=5）、nv3（ü 写作 v）。

  from pinyin_annotate import Annotator, mark
  a = Annotator()                      # 默认规则 assets/rules.starter.json；项目自己的规则：Annotator('my_rules.json')
  a.annotate('他长大了')               # → ['ta1', 'zhang3', 'da4', 'le5']
  mark('zhang3')                       # → 'zhǎng'

流程：pypinyin（带词语上下文，处理多音字、一/不变调）→ 规则文件按顺序改写。运行期网页里没有任何转换引擎，只查构建期写进页面的读音。

命令行（Windows 请用 `python -X utf8`）：
  pinyin_annotate.py "要标注的句子"                         打印 字:拼音
  pinyin_annotate.py --file a.txt [--rules r.json] --json   a.txt 每行一段（.html 则取文本节点）→ JSON [{"text","py"}]
  pinyin_annotate.py --review a.txt b.html [--rules r.json] [--out review.md]   写多音字复核表（人工/代理逐条过一遍）
"""
import collections, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
STARTER = HERE.parent / 'assets' / 'rules.starter.json'
HAN = re.compile('[一-鿿]')
HAN_RUN = re.compile('[一-鿿]+')

try:
    from pypinyin import pinyin as _pinyin, Style
except ImportError:      # pragma: no cover
    sys.exit('缺少 pypinyin：请先运行  python3 -m pip install pypinyin')


class Annotator:
    def __init__(self, rules_path=None):
        spec = json.loads(pathlib.Path(rules_path or STARTER).read_text('utf8'))
        self.neutral = spec.get('neutral', {})
        self.rules = []
        for r in spec.get('rules', []):
            m = re.search('«(.)»', r['ctx'])
            if not m:
                raise ValueError(f"规则缺少 «字» 标记：{r['ctx']}")
            left, tgt, right = r['ctx'][:m.start()], m.group(1), r['ctx'][m.end():]
            # 用前瞻，重叠位置也能命中；命名组 t 就是要改的字（不会打乱规则里 \1 之类的回溯编号）
            rx = re.compile(f'(?=(?:{left})(?P<t>{re.escape(tgt)})(?:{right}))')
            self.rules.append((rx, r['py'], set(r.get('when') or []), r['ctx']))

    def annotate(self, text: str, trace=None) -> list:
        """text 里每个汉字（按出现顺序）一个读音。trace 传入 list 时，记录被规则改写的 (位置, 旧, 新, 规则)。"""
        pos = [i for i, ch in enumerate(text) if HAN.match(ch)]
        py = [None] * len(pos)
        idx = {p: k for k, p in enumerate(pos)}
        for m in HAN_RUN.finditer(text):
            got = _pinyin(m.group(), style=Style.TONE3, neutral_tone_with_five=True, v_to_u=False, strict=False)
            for k, (p,) in enumerate(got):
                py[idx[m.start() + k]] = p if re.search(r'\d$', p) else p + '5'     # 保险：没有声调数字的当轻声
        for rx, new, when, desc in self.rules:
            for m in rx.finditer(text):
                at = m.start('t')
                k = idx.get(at)
                if k is None or (when and py[k] not in when):
                    continue
                if py[k] != new:
                    if trace is not None:
                        trace.append((at, py[k], new, desc))
                    py[k] = new
        return py


# ───────────── 声调数字 → 带调符号（审校/测试用；网页里 pinyin_hover.js 有同样的实现） ─────────────
_TONES = {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'v': 'ǖǘǚǜ'}


def mark(py: str) -> str:
    m = re.fullmatch(r'([a-z]+)([1-5])', py)
    if not m:
        return py
    s, t = m.group(1), int(m.group(2))
    if t == 5:
        return s.replace('v', 'ü')
    for pref in ('a', 'e'):                 # 标调规则：a、e 优先；ou 标 o；其余标最后一个元音
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
    return (s[:i] + _TONES[s[i]][t - 1] + s[i + 1:]).replace('v', 'ü')


# ───────────── 多音字复核表 ─────────────
def review(items, annotator, path, title='拼音读音复核表'):
    """items：[(分组名, 文本)]。把出现不止一种读音的字、被规则改写过的位置都列出来，供人工/代理逐条核对。"""
    rows = collections.defaultdict(lambda: collections.defaultdict(list))
    traced = collections.defaultdict(lambda: collections.defaultdict(list))
    total = 0
    for _group, text in items:
        tr = []
        py = annotator.annotate(text, tr)
        for k, i in enumerate([i for i, ch in enumerate(text) if HAN.match(ch)]):
            ctx = text[max(0, i - 4):i] + '【' + text[i] + '】' + text[i + 1:i + 5]
            rows[text[i]][py[k]].append(ctx.replace('\n', ''))
            total += 1
        for at, old, new, desc in tr:
            traced[text[at]][(old, new, desc)].append(text[max(0, at - 4):at] + '【' + text[at] + '】' + text[at + 1:at + 5])
    poly = {c: v for c, v in rows.items() if len(v) > 1}
    lines = [f'# {title}（自动生成，请勿手改）', '',
             f'汉字 {total} 个；出现不止一种读音的字 {len(poly)} 个（下表全部列出）；被规则改写的字 {len(traced)} 个（后面单列）。',
             '用法：逐条看“上下文 → 读音”对不对；不对就在规则文件里加一条（或改一条），重跑本命令；改完把典型例句加进单元测试。', '',
             '## 一、多音字（按出现次数）', '']
    for c in sorted(poly, key=lambda c: -sum(len(x) for x in poly[c].values())):
        by = sorted(poly[c].items(), key=lambda kv: -len(kv[1]))
        lines.append(f'### {c}（' + '、'.join(f'{mark(p)} ×{len(v)}' for p, v in by) + '）')
        for p, v in by:
            lines.append(f'- **{mark(p)}**：' + '　'.join(v[:6]) + (f'　…共 {len(v)} 处' if len(v) > 6 else ''))
        lines.append('')
    lines += ['## 二、规则改写过的位置（pypinyin 默认值 → 规则结果）', '']
    for c in sorted(traced, key=lambda c: -sum(len(x) for x in traced[c].values())):
        for (old, new, desc), v in traced[c].items():
            lines.append(f'- **{c}** {mark(old)} → **{mark(new)}** ×{len(v)}　规则 `{desc}`　例：' + '　'.join(v[:4]))
    pathlib.Path(path).write_text('\n'.join(lines) + '\n', 'utf8')
    return {'han': total, 'polyphones': len(poly), 'rewritten': sum(len(v) for t in traced.values() for v in t.values())}


def load_paragraphs(path):
    """.html/.htm → 各文本节点；其他 → 每个非空行一段"""
    p = pathlib.Path(path)
    raw = p.read_text('utf8')
    if p.suffix.lower() in ('.html', '.htm'):
        import wrap_html
        return wrap_html.text_nodes(raw)
    return [ln for ln in raw.splitlines() if ln.strip()]


def _main(argv):
    def opt(name, default=None):
        if name in argv:
            i = argv.index(name)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return default
    rules = opt('--rules')
    out = opt('--out')
    as_json = '--json' in argv
    argv = [a for a in argv if a != '--json']
    sys.path.insert(0, str(HERE))
    ann = Annotator(rules)
    if '--review' in argv:
        files = [a for a in argv if not a.startswith('--')]
        items = [(f, t) for f in files for t in load_paragraphs(f)]
        out = out or 'pinyin_review.md'
        print(f'写出 {out}：', review(items, ann, out))
    elif '--file' in argv:
        paras = load_paragraphs(argv[argv.index('--file') + 1])
        rows = [{'text': t, 'py': ' '.join(ann.annotate(t))} for t in paras]
        print(json.dumps(rows, ensure_ascii=False, indent=1) if as_json else '\n'.join(f"{r['text']}\n  {r['py']}" for r in rows))
    else:
        t = ' '.join(a for a in argv if not a.startswith('--')) or '他长大了，老师教他背书。'
        print(' '.join(f'{c}:{mark(p)}' for c, p in zip([c for c in t if HAN.match(c)], ann.annotate(t))))


if __name__ == '__main__':
    _main(sys.argv[1:])
