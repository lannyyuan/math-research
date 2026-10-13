#!/usr/bin/env python3
"""把《雪地里的那盏灯》做成一个“单文件”绘本网页：dist/snow-lamp-book.html

  python3 webapp/build.py            # 需要先有 out/book_img/（node scripts/book_stills.mjs）
  python3 webapp/build.py --no-font  # 调试时跳过裁字体

流程：plan.py 分页 → heroes.json 配图 → 核对“全文一个字不少、顺序不乱” → 插图转 WebP →
      裁字体（霞鹜文楷 OFL）→ 把 CSS/JS/数据/图片/字体全部内联进 template.html。
产物不依赖任何外部文件（影片 snow-lamp.mp4 放在旁边就能点“看这一幕”，没有也能读）。
"""
import base64, io, json, pathlib, re, subprocess, sys, tempfile
from PIL import Image, ImageStat

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
IMG_DIR = ROOT / 'out' / 'book_img'
DIST = ROOT / 'dist'
sys.path.insert(0, str(HERE))
from subset_font import subset_font  # noqa: E402

WIDTH = 1440        # 插图宽度（px）
QUALITY = 80
NORM = re.compile(r'[\s“”"‘’\'「」]')
HAN = re.compile(r'[一-鿿]')


def norm(t: str) -> str:
    return NORM.sub('', t)


def highlight(text: str, cue_text: str):
    """在段落文字里找影片字幕那一句的位置（忽略引号和空白），返回 (起, 止)。"""
    idx = [i for i, ch in enumerate(text) if not NORM.match(ch)]
    flat = ''.join(text[i] for i in idx)
    t = norm(cue_text).strip('，、；：')
    pos = flat.find(t)
    if pos < 0:
        return None
    return idx[pos], idx[pos + len(t) - 1] + 1


def tc_seconds(tc: str) -> int:
    m, s = tc.split(':')
    return int(m) * 60 + int(s)


def main():
    no_font = '--no-font' in sys.argv
    subprocess.run([sys.executable, str(HERE / 'plan.py')], check=True, stdout=subprocess.DEVNULL)
    plan = json.loads((OUT / 'plan.json').read_text('utf8'))
    heroes = json.loads((HERE / 'heroes.json').read_text('utf8'))
    cues = {c['no']: c for c in plan['cues']}

    # —— 页
    pages, used = [], set()
    ordinal = {}
    nocue_count = {}
    for q in plan['pages']:
        if not q['cues']:
            nm = plan['sections'][q['sec']]['no']
            nocue_count[nm] = nocue_count.get(nm, 0) + 1
    for p in plan['pages']:
        paras = []
        for q in p['paras']:
            if q['kind'] == 'p':
                segs, text = [], q['text']
                spans = []
                for no in p['cues']:
                    r = highlight(text, cues[no]['text'])
                    if r:
                        spans.append((r[0], r[1], no))
                spans.sort()
                pos = 0
                for a, b, no in spans:
                    if a > pos:
                        segs.append([text[pos:a], 0])
                    segs.append([text[a:b], no])
                    pos = b
                if pos < len(text):
                    segs.append([text[pos:], 0])
                paras.append({'k': 'p', 'cont': q['cont'], 'segs': segs})
            else:
                paras.append({'k': q['kind'], 'lines': q['lines']})
        marked = {s[1] for q in paras if q['k'] == 'p' for s in q['segs'] if s[1]}
        missing = set(p['cues']) - marked
        if missing:
            sys.exit(f"第 {p['i']} 页：字幕 {sorted(missing)} 没能在原文段落里标出来")
        cue_no = p['cues'][0] if p['cues'] else None
        if cue_no:
            c = cues[cue_no]
            hero = {'img': f'cue/{cue_no:02d}', 'fx': 0.5, 'fy': 0.55, 'z': 1,
                    'cap': f"分镜 {cue_no}/40　{c['sceneName']}　影片 {c['tc']}",
                    'alt': f"影片画面：{c['sceneName']}。字幕：{c['text'].replace(chr(10), '')}"}
        else:
            no = plan['sections'][p['sec']]['no']
            lst = heroes['sections'].get(no)
            k = ordinal.get(no, 0)
            ordinal[no] = k + 1
            if lst:
                # 这一章里没有字幕的 m 页，按顺序平均分给 L 张插图（相邻几页共用一张，翻页时画面不动，只换字）
                m_total = nocue_count[no]
                hero = {'z': 1, 'fx': 0.5, 'fy': 0.55, **lst[min(len(lst) - 1, k * len(lst) // m_total)]}
            elif pages and pages[-1]['sec'] == p['sec']:
                # 这一章没配插图：沿用上一页的画面，只换个取景（放大一点、换个位置）
                prev = pages[-1]['hero']
                hero = {**prev, 'z': 1.55 if prev.get('z', 1) < 1.3 else 1.0, 'fx': 0.5 + (0.12 if k % 2 else -0.12), 'fy': 0.62}
                print(f"  提示：第 {p['i']} 页（{no}）沿用上一页的画面；可在 heroes.json 的 sections 里给“{no}”单独配插图")
            else:
                sys.exit(f"第 {p['i']} 页（{no}）没有字幕画面，也没有在 heroes.json 的 sections 里给“{no}”配插图")
        hero.setdefault('z', 1)
        used.add(hero['img'])
        pages.append({'i': p['i'], 'sec': p['sec'], 'startsSec': p['startsSec'], 'han': p['han'], 'cues': p['cues'],
                      'endsMid': p.get('endsMid', False), 'hero': hero, 'paras': paras})

    # —— 核对：全文一个字不少、不重复、顺序不乱
    src = ''.join(l for l in (ROOT / 'story/source.md').read_text('utf8').split('\n') if l.strip() and not l.startswith('#'))
    got = ''
    for pg in pages:
        for q in pg['paras']:
            got += ''.join(s[0] for s in q['segs']) if q['k'] == 'p' else ''.join(q['lines'])
    if norm(src) != norm(got):
        n = min(len(norm(src)), len(norm(got)))
        k = next((i for i in range(n) if norm(src)[i] != norm(got)[i]), n)
        sys.exit(f"全文核对失败：第 {k} 个字起不一致\n原文: {norm(src)[k-10:k+20]}\n页面: {norm(got)[k-10:k+20]}")
    print(f"全文核对通过：{len(norm(src))} 个字（含标点），{sum(1 for pg in pages for q in pg['paras'] for _ in [0])} 个段落块，{len(pages)} 页")

    # —— 分镜（影片里的 41 个画面，影片顺序）
    page_of_cue = {no: pg['i'] for pg in pages for no in pg['cues']}
    scenes, seen = [], {}
    scenes.append({'id': 's0-title', 'name': '片头', 'cues': []})
    for no in sorted(cues):
        c = cues[no]
        if c['scene'] not in seen:
            seen[c['scene']] = {'id': c['scene'], 'name': c['sceneName'], 'cues': []}
            scenes.append(seen[c['scene']])
        seen[c['scene']]['cues'].append(no)
    cue_list = [{'no': no, 'scene': cues[no]['scene'], 'text': cues[no]['text'], 'tc': cues[no]['tc'],
                 'sec': tc_seconds(cues[no]['tc']), 'page': page_of_cue[no]} for no in sorted(cues)]
    used.add('cue/00')
    for no in cues:
        used.add(f'cue/{no:02d}')  # 分镜总览里 41 张全都要
    used.add(heroes['cover']['img']); used.add(heroes['end']['img'])

    data = {
        'title': plan['title'],
        'sections': [{'no': s['no'], 'name': s['name']} for s in plan['sections']],
        'pages': pages,
        'cues': cue_list,
        'scenes': scenes,
        'titleCard': {'tc': plan['titleCard']['tc'], 'sec': tc_seconds(plan['titleCard']['tc'])},
        'cover': heroes['cover'], 'end': heroes['end'],
        'filmFile': 'snow-lamp.mp4',
    }

    # —— 插图 → WebP → base64
    imgs = {}
    total = 0
    for key in sorted(used):
        src_png = IMG_DIR / f'{key}.png'
        if not src_png.exists():
            sys.exit(f'缺插图 {src_png}（先运行 node scripts/book_stills.mjs）')
        im = Image.open(src_png).convert('RGB')
        lum = ImageStat.Stat(im.convert('L')).mean[0]
        if lum < 50:   # 太暗的画面（比如还没点灯的小房间）提一点亮度，不然在屏幕上只是一团黑
            im = im.point([int(255 * ((i / 255) ** 0.66)) for i in range(256)] * 3)
            print(f'  提亮 {key}（平均亮度 {lum:.0f}）')
        im = im.resize((WIDTH, round(WIDTH * im.height / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=QUALITY, method=6)
        total += buf.tell()
        imgs[key] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    print(f'插图 {len(imgs)} 张，WebP 共 {total/1e6:.1f} MB')

    # —— 字体
    css = (HERE / 'app.css').read_text('utf8')
    js = (HERE / 'app.js').read_text('utf8')
    tpl = (HERE / 'template.html').read_text('utf8')
    all_text = json.dumps(data, ensure_ascii=False) + css + js + tpl
    chars = {ch for ch in all_text if ord(ch) > 127} | {chr(i) for i in range(32, 127)}
    ui_chars = {ch for ch in js + tpl + ''.join(s['no'] + s['name'] for s in plan['sections']) + plan['title'] + '补充插图影片画面分镜' if ord(ch) > 127} | {chr(i) for i in range(32, 127)}
    fonts = {}
    if no_font:
        fonts = {'regular': '', 'bold': ''}
    else:
        tmp = pathlib.Path(tempfile.mkdtemp())
        for weight, cs in (('regular', chars), ('bold', ui_chars)):
            out = tmp / f'wk-{weight}.woff2'
            miss = subset_font(weight, cs, out)
            if miss:
                print(f'  （{weight}）字体里没有的字符：{"".join(miss)}')
            fonts[weight] = base64.b64encode(out.read_bytes()).decode()
            print(f'字体 {weight}: {out.stat().st_size/1e3:.0f} KB，{len(cs)} 个字符')

    # —— 拼成一个 HTML
    def js_json(o):
        return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = (tpl
            .replace('{{CSS}}', css)
            .replace('{{FONT_REGULAR}}', fonts['regular'])
            .replace('{{FONT_BOLD}}', fonts['bold'])
            .replace('{{DATA}}', js_json(data))
            .replace('{{IMAGES}}', js_json(imgs))
            .replace('{{JS}}', js))
    DIST.mkdir(exist_ok=True)
    out = DIST / 'snow-lamp-book.html'
    out.write_text(html, 'utf8')
    print(f'写出 {out}  {out.stat().st_size/1e6:.1f} MB')


if __name__ == '__main__':
    main()
