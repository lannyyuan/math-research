#!/usr/bin/env python3
"""Pagination plan for the picture-book web app: cut the whole story (story/source.md, up to the first "---") into pages,
each page paired with one picture.

 in   story/source.md, out/storyboard_plan.json (one entry per film subtitle, see scripts/storyboard_plan.mjs)
 out  webapp/out/plan.json

Rules
 1. Every film subtitle is an "anchor" in the story text; the page that holds it uses that subtitle's clean film frame as its picture.
    (Two subtitles inside one sentence share a page.)
 2. A page starts at the beginning of the paragraph that holds the anchor (or at the sentence, if an earlier anchor is in the same paragraph).
 3. If the text between two anchors is too long for one screen it is cut at paragraph / sentence boundaries into several pages.
 4. Not one word is lost, repeated or reordered; build.py checks this again.
"""
import json, re, sys, math, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'webapp' / 'out'
OUT.mkdir(parents=True, exist_ok=True)

CPL = 44          # characters per line of the text panel at 1440x900 (Andika is wide)
CAP = 14.2        # target number of lines per page (incl. paragraph gaps and the chapter title)
SOFT_MAX = 15.8   # only force a split above this
MIN_STUB = 16     # a fragment before an anchor with fewer words than this is merged into the anchor's page

NORM = re.compile(r'[\s“”"‘’\']')
norm = lambda t: NORM.sub('', t)
words = lambda t: len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", t))


def curly(par: str) -> str:
    """ASCII quotes -> typographic quotes (display only, no word changes). " alternates per paragraph; ' is an apostrophe unless it opens a quote."""
    out, op = [], True
    for i, ch in enumerate(par):
        if ch == '"':
            out.append('“' if op else '”'); op = not op
        elif ch == "'":
            prev = par[i - 1] if i else ' '
            out.append('‘' if (not prev.isalnum() and prev not in '.,!?”’') else '’')
        else:
            out.append(ch)
    return ''.join(out)


def parse():
    raw = (ROOT / 'story/source.md').read_text(encoding='utf8').split('\n')
    lines = []
    for l in raw:
        if re.match(r'^---\s*$', l):
            break                       # the statistics appendix after "---" is not part of the story
        lines.append(l)
    secs, blocks, cur = [], [], []
    sec, title = -1, ''

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
            m = re.match(r'(Chapter \d+|Epilogue):\s*(.+)$', l[3:].strip())
            no = m.group(1)
            secs.append({'no': no, 'short': no.split()[-1] if no.startswith('Chapter') else 'Epi', 'name': m.group(2).strip(), 'raw': l[3:].strip()})
            continue
        if not l.strip():
            flush(); continue
        cur.append((i, l))
    flush()
    return title, secs, blocks


SENT = re.compile(r'(?<=[.!?])([”’]*)\s+(?=[“‘A-Z0-9])')


def sentences(text: str):
    parts, pos = [], 0
    for m in SENT.finditer(text):
        parts.append(text[pos:m.end(1)])
        pos = m.end()
    parts.append(text[pos:])
    return [p for p in parts if p.strip()]


LONG = 250   # sentences longer than this (lists of things in the story) may be cut at a comma so that no page is a wall of text


def chunks(sn: str):
    """Cut a very long sentence at commas / semicolons / colons into pieces of roughly LONG*0.62 characters."""
    if len(sn) <= LONG:
        return [sn]
    n = math.ceil(len(sn) / (LONG * 0.62))
    cuts = [m.end() for m in re.finditer(r'[,;:]\s+', sn)]
    out, last = [], 0
    for j in range(1, n):
        want = len(sn) * j / n
        c = min((x for x in cuts if x > last + 40 and x < len(sn) - 40), key=lambda x: abs(x - want), default=None)
        if c is None:
            break
        out.append(sn[last:c].strip()); last = c
    out.append(sn[last:].strip())
    return [o for o in out if o]


def build_units(blocks):
    units = []
    for bi, b in enumerate(blocks):
        txt = ' '.join(curly(l) for l in b['lines'])
        k = 0
        for sn in sentences(txt):
            for piece in chunks(sn):
                units.append({'blk': bi, 'sec': b['sec'], 'text': piece, 'k': k, 'line': b['line']})
                k += 1
    return units


def main():
    title, secs, blocks = parse()
    units = build_units(blocks)
    for u in units:
        u['n'] = words(u['text'])
    total = sum(u['n'] for u in units)

    sp = json.loads((ROOT / 'out/storyboard_plan.json').read_text(encoding='utf8'))   # entry 0 = title card
    cues = [dict(p, no=i) for i, p in enumerate(sp) if i > 0]
    anchors, start = {}, 0
    for c in cues:
        t = norm(c['text'])
        hit = next((i for i in range(start, len(units)) if t in norm(units[i]['text'])), None)
        if hit is None:   # the subtitle spans two neighbouring sentences
            hit = next((i for i in range(start, len(units) - 1) if units[i]['blk'] == units[i + 1]['blk'] and t in norm(units[i]['text'] + units[i + 1]['text'])), None)
        if hit is None:
            sys.exit(f"subtitle {c['no']} not found in the story after unit {start}: {c['text']}")
        anchors[c['no']] = hit
        start = hit

    cuts = {0}
    for no, ui in sorted(anchors.items(), key=lambda kv: kv[1]):
        blk = units[ui]['blk']
        s = ui
        while s > 0 and units[s - 1]['blk'] == blk:
            s -= 1
        prior = [a for a in anchors.values() if units[a]['blk'] == blk and a < ui]
        cuts.add(ui if prior else s)
    for i, u in enumerate(units):
        if i == 0 or units[i - 1]['sec'] != u['sec']:
            cuts.add(i)
    cl = sorted(cuts)
    spans = [(c, cl[k + 1] if k + 1 < len(cl) else len(units)) for k, c in enumerate(cl)]
    merged, k = [], 0
    while k < len(spans):
        a, b = spans[k]
        has_anchor = any(a <= ui < b for ui in anchors.values())
        if words_between(units, a, b) < MIN_STUB and not has_anchor and k + 1 < len(spans) and units[spans[k + 1][0]]['sec'] == units[a]['sec']:
            spans[k + 1] = (a, spans[k + 1][1]); k += 1; continue
        merged.append((a, b)); k += 1

    pages_u = []
    for a, b in merged:
        n = lines_between(units, a, b)
        if n <= SOFT_MAX:
            pages_u.append((a, b)); continue
        pages_u.extend(split_span(units, a, b))

    pages = []
    for pi, (a, b) in enumerate(pages_u):
        here = [no for no, ui in anchors.items() if a <= ui < b]
        starts = a == 0 or units[a - 1]['sec'] != units[a]['sec']
        paras, last = [], None
        for ui in range(a, b):
            u = units[ui]
            if u['blk'] != last:
                paras.append({'kind': 'p', 'cont': u['k'] != 0, 'text': ''}); last = u['blk']
            paras[-1]['text'] += (' ' if paras[-1]['text'] else '') + u['text']
        pages.append({'i': pi + 1, 'sec': units[a]['sec'], 'startsSec': bool(starts), 'cues': sorted(here), 'w': words_between(units, a, b),
                      'u': [a, b], 'paras': paras, 'endsMid': bool(b < len(units) and units[b]['blk'] == units[b - 1]['blk'])})

    plan = {
        'title': title,
        'sections': secs,
        'cues': [{'no': c['no'], 'scene': c['scene'], 'sceneName': c['sceneName'], 'idx': c['idx'], 'text': c['text'], 'tc': c['tc'], 'frame': c['frame'], 't': c['t']} for c in cues],
        'titleCard': {'frame': sp[0]['frame'], 'tc': sp[0]['tc']},
        'pages': pages,
        'totalWords': total,
    }
    (OUT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding='utf8')
    print(f'{total} words, {len(pages)} pages')
    for p in pages:
        sec = secs[p['sec']]
        head = f"{sec['no']}: {sec['name']}" if p['startsSec'] else ''
        print(f"{p['i']:3d}  {p['w']:4d}w {lines_between(units, *p['u']):5.1f} lines  cues {p['cues']!s:12}  {head}")


def split_span(units, a, b):
    """Cut units[a:b] into pages of at most SOFT_MAX lines, as even as possible, preferring paragraph boundaries."""
    n = lines_between(units, a, b)
    for k in range(max(2, math.ceil(n / CAP)), 14):
        cuts, last, ok = [], a, True
        for j in range(1, k):
            rest = lines_between(units, last, b, head=False if cuts else None)
            target = rest / (k - j + 1)
            best, bc = None, 1e9
            for e in range(last + 1, b):
                ln = lines_between(units, last, e, head=False if cuts else None)
                if ln > SOFT_MAX:
                    break
                cost = abs(ln - target) - (1.6 if units[e]['blk'] != units[e - 1]['blk'] else 0)
                if cost < bc:
                    best, bc = e, cost
            if best is None:
                ok = False; break
            cuts.append(best); last = best
        if not ok:
            continue
        pts = [a] + cuts + [b]
        if all(lines_between(units, x, y, head=(x == a and None)) <= SOFT_MAX + 0.01 for x, y in zip(pts, pts[1:])):
            return list(zip(pts, pts[1:]))
    pts = [a, b]
    return [(a, b)]


def words_between(units, a, b):
    return sum(u['n'] for u in units[a:b])


def lines_between(units, a, b, head=None):
    """Rough line count of units[a:b] on one page: per paragraph ceil(chars / CPL) + 0.5 line gap; a chapter title adds 3.2 lines."""
    if head is None:
        head = a == 0 or units[a - 1]['sec'] != units[a]['sec']
    total = 3.2 if head else 0.0
    i = a
    while i < b:
        blk, j, txt = units[i]['blk'], i, ''
        while j < b and units[j]['blk'] == blk:
            txt += (' ' if txt else '') + units[j]['text']; j += 1
        total += math.ceil(len(txt) / CPL) + 0.5
        i = j
    return total


if __name__ == '__main__':
    main()
