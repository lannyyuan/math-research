#!/usr/bin/env python3
"""把《小石猴点灯》做成一个“单文件”绘本网页：dist/xiaoshihou-book.html

  python3 -I webapp/build.py            # 没有图也能构建：缺的图自动生成水墨渐变占位图（写着“待配图：key”）
  python3 -I webapp/build.py --no-font  # 调试时跳过裁字体

流程：plan.py 分页 → heroes.json 配图（缺图用占位图）→ 全文核对（和“独立重新抽取的原文”逐字比对）→
      图转 WebP（1440 宽）→ 裁字体（霞鹜文楷 OFL，常规 + 粗体两个小子集）→ CSS/JS/数据/图/字体全部内联进 template.html。
产物不依赖任何外部文件（影片 xiaoshihou-dian-deng.mp4 / xiao-shi-hou-720p.mp4 放在旁边，点“看影片”就能播，没有也能读）。
图放在 out/book_img/{cue,plate,film}/*.png（film/cover.png = 封面；封面默认用 ref/cover.png）。
"""
import base64, io, json, math, pathlib, random, re, sys, zlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import plan as planmod                       # noqa: E402
from subset_font import subset_font, subset_ttf_bytes  # noqa: E402

IMG_DIR = ROOT / 'out' / 'book_img'
DIST = ROOT / 'dist'
OUT = HERE / 'out'
WIDTH = 1440        # 插图宽度（px）
QUALITY = 80
PH_W, PH_H = 960, 540   # 占位图尺寸（小，省体积）
FILM_FILES = ['xiaoshihou-dian-deng.mp4', 'xiao-shi-hou-720p.mp4']
KIND = {'cue': '影片画面', 'film': '影片画面', 'plate': '补充插图'}
NORM = re.compile(r'[\s“”"‘’\'「」·]')


def norm(t: str) -> str:
    return NORM.sub('', t)


# ───────────── 独立的“原文重新抽取”（故意不复用 plan.py 的解析代码，只用最朴素的逐行处理） ─────────────
def expected_by_chapter():
    """→ {章key: 标题 + 正文（未去引号/空白）}。行首 # 丢弃；【…】丢弃（`】` 之后的字是正文）；【封面】后的话不算；
       【附：…】整行丢弃（连同后面的裸行）；章标题的文字算章名。"""
    chap, skip, cur = {}, False, None
    for line in (ROOT / 'story' / 'book_source.txt').read_text('utf8').splitlines():
        if not line.strip() or line[0] == '#':
            continue
        body = line
        if line[0] == '【':
            end = line.index('】')
            label, body = line[1:end], line[end + 1:]
            if label.startswith('附'):
                skip = True
                continue
            skip = False
            if label.startswith('封面'):
                continue
            if label.startswith('增补') or (label.startswith('第') and '分' in label[:5]):
                cur = label.split(' ')[0]
                chap[cur] = label
                continue
        elif skip:
            continue
        chap[cur] += body
    return chap


# ───────────── 占位图 ─────────────
_ph_font_cache = {}


def _ph_font(size):
    if size not in _ph_font_cache:
        data, _ = subset_ttf_bytes('regular', set('待配图：') | {chr(i) for i in range(32, 127)})
        _ph_font_cache[size] = ImageFont.truetype(io.BytesIO(data), size)
    return _ph_font_cache[size]


def make_placeholder(key: str) -> Image.Image:
    """水墨风渐变占位图：夜空渐变 + 一团灯光 + 三层远山（每个 key 形状不同，方便看裁切）+ 薄雾 + “待配图：key”。"""
    rnd = random.Random(zlib.crc32(key.encode()))
    kind = key.split('/')[0]
    top, bot = {'cue': ((18, 26, 46), (52, 66, 92)), 'plate': ((30, 38, 52), (84, 90, 88)), 'film': ((22, 28, 44), (70, 74, 90))}.get(kind, ((24, 30, 46), (70, 76, 92)))
    W, H = PH_W, PH_H
    g = Image.linear_gradient('L').resize((W, H))
    img = Image.composite(Image.new('RGB', (W, H), bot), Image.new('RGB', (W, H), top), g)
    # 一团灯光（灰金）
    cx, cy, r = rnd.randint(int(W * .2), int(W * .8)), rnd.randint(int(H * .15), int(H * .42)), rnd.randint(50, 90)
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).ellipse((cx - r, cy - r, cx + r, cy + r), fill=170)
    glow = glow.filter(ImageFilter.GaussianBlur(r * .9))
    img = Image.composite(Image.new('RGB', (W, H), (207, 194, 154)), img, glow.point(lambda v: int(v * .55)))
    # 三层远山
    for layer, (col, base, amp, blur) in enumerate([((58, 70, 92), .56, 90, 6), ((38, 48, 68), .70, 110, 3), ((22, 29, 46), .86, 100, 1)]):
        ph = [rnd.uniform(0, 6.28) for _ in range(3)]
        fr = [rnd.uniform(1.2, 2.4), rnd.uniform(3, 5), rnd.uniform(7, 11)]
        pts = []
        for x in range(0, W + 20, 20):
            t = x / W
            y = H * base - amp * (.55 * math.sin(fr[0] * 6.28 * t + ph[0]) + .3 * math.sin(fr[1] * 6.28 * t + ph[1]) + .15 * math.sin(fr[2] * 6.28 * t + ph[2]))
            pts.append((x, y))
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).polygon(pts + [(W + 20, H), (0, H)], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(blur))
        img = Image.composite(Image.new('RGB', (W, H), col), img, m)
        # 山脚薄雾
        mist = Image.new('L', (W, H), 0)
        ImageDraw.Draw(mist).ellipse((-W * .1, H * (base + .02), W * 1.1, H * (base + .16)), fill=120)
        mist = mist.filter(ImageFilter.GaussianBlur(26))
        img = Image.composite(Image.new('RGB', (W, H), (205, 205, 198)), img, mist.point(lambda v: int(v * .30)))
    # 四角 + 中间的 key（裁切后也能看出取的是哪一块）
    d = ImageDraw.Draw(img)
    small, mid, big = _ph_font(15), _ph_font(24), _ph_font(54)
    for (x, y, anc) in [(14, 10, 'la'), (W - 14, 10, 'ra'), (14, H - 10, 'ld'), (W - 14, H - 10, 'rd')]:
        d.text((x, y), key, font=small, fill=(178, 176, 160), anchor=anc)
    d.text((W // 2, H // 2 - 10), key, font=big, fill=(150, 150, 140), anchor='mm')
    d.text((W // 2, H // 2 + 36), '待配图：' + key, font=mid, fill=(200, 192, 160), anchor='mm')
    # 淡淡的三分线，方便对 fx/fy
    for f in (1 / 3, 2 / 3):
        d.line([(W * f, 0), (W * f, H)], fill=(120, 124, 130), width=1)
        d.line([(0, H * f), (W, H * f)], fill=(120, 124, 130), width=1)
    return img


def load_image(key: str, file_override=None):
    """→ (PIL 图, 是否占位)。有图：out/book_img/<key>.png；没有：占位图。"""
    path = (ROOT / file_override) if file_override else (IMG_DIR / f'{key}.png')
    if path.exists():
        im = Image.open(path).convert('RGB')
        lum = ImageStat.Stat(im.convert('L')).mean[0]
        if lum < 50:   # 太暗的画面提一点亮度，不然在屏幕上只是一团黑
            im = im.point([int(255 * ((i / 255) ** 0.66)) for i in range(256)] * 3)
            print(f'  提亮 {key}（平均亮度 {lum:.0f}）')
        return im, False
    return make_placeholder(key), True


def to_webp_uri(im: Image.Image, width: int, quality: int, method=6):
    if im.width > width:
        im = im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=quality, method=method)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode(), buf.tell()


# ───────────── 主流程 ─────────────
def main():
    no_font = '--no-font' in sys.argv
    plan, _ = planmod.make_plan()
    OUT.mkdir(exist_ok=True)
    (OUT / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1), 'utf8')
    heroes = json.loads((HERE / 'heroes.json').read_text('utf8'))
    secs = plan['sections']

    # —— 章顺序
    print('章节顺序：' + ' → '.join(s['key'] for s in secs))

    # —— 配图：每页一个 hero
    per_sec = {}
    for p in plan['pages']:
        per_sec.setdefault(p['sec'], []).append(p)
    pages = []
    for p in plan['pages']:
        key = secs[p['sec']]['key']
        lst = (heroes.get('sections') or {}).get(key)
        if not lst:
            sys.exit(f'heroes.json 里没有“{key}”的图片列表（sections.{key}）')
        if p['seg'] is not None:
            e = lst[p['seg']]
        else:   # 没写 at：这一章的 m 页按顺序平均分给 L 张图
            m = len(per_sec[p['sec']])
            k = per_sec[p['sec']].index(p)
            e = lst[min(len(lst) - 1, k * len(lst) // m)]
        hero = {'fx': 0.5, 'fy': 0.55, 'z': 1, **{k: v for k, v in e.items() if k != 'at'}}
        kind = KIND.get(hero['img'].split('/')[0], '插图')
        hero['cap'] = f"{kind}：{hero['cap']}" if hero.get('cap') else kind
        hero.setdefault('alt', '')
        pages.append({'i': p['i'], 'sec': p['sec'], 'startsSec': p['startsSec'], 'han': p['han'], 'hero': hero,
                      'paras': [{'text': q['text'], 'cont': q['cont'], 'tag': q['tag']} for q in p['paras']]})

    # —— 全文核对：页面上的字（章名 + 正文，去掉空白、引号、·）== 独立重新抽取的原文（按 ORDER 排序）
    exp = expected_by_chapter()
    got = {s['key']: '' for s in secs}
    for pg in pages:
        s = secs[pg['sec']]
        if pg['startsSec']:
            got[s['key']] += s['no'] + s['name']
        got[s['key']] += ''.join(q['text'] for q in pg['paras'])
    ok = True
    for s in secs:
        a, b = norm(exp[s['key']]), norm(got[s['key']])
        if a != b:
            ok = False
            n = min(len(a), len(b))
            k = next((i for i in range(n) if a[i] != b[i]), n)
            print(f"全文核对失败：{s['key']} 第 {k} 个字起不一致\n  原文: {a[max(0, k - 10):k + 20]}\n  页面: {b[max(0, k - 10):k + 20]}")
    A = ''.join(norm(exp[s['key']]) for s in secs)
    B = ''.join(norm(got[s['key']]) for s in secs)
    if not ok or A != B:
        sys.exit(1)
    nhan = len(re.findall(r'[一-鿿]', A))
    print(f"全文核对通过：{len(A)} 个字（含章名与标点，不含引号/空白），其中汉字 {nhan}；{sum(len(pg['paras']) for pg in pages)} 个段落块，{len(pages)} 页")

    # —— 图 → WebP → base64
    cover = dict(heroes['cover'])
    cover_file = cover.pop('file', None)
    end = dict(heroes['end'])
    used = {}
    for pg in pages:
        used.setdefault(pg['hero']['img'], None)
    used.setdefault(end['img'], None)
    imgs, total, nph, missing = {}, 0, 0, []
    for key in sorted(used):
        im, ph = load_image(key)
        uri, nbytes = to_webp_uri(im, PH_W if ph else WIDTH, 62 if ph else QUALITY, 4 if ph else 6)
        imgs[key] = uri; total += nbytes
        if ph:
            nph += 1; missing.append(key)
    im, ph = load_image(cover['img'], cover_file)
    uri, nbytes = to_webp_uri(im, 1086, 86)
    imgs[cover['img']] = uri; total += nbytes
    if ph:
        nph += 1; missing.append(cover['img'])
    print(f"插图 {len(imgs)} 张（其中占位图 {nph} 张），WebP 共 {total / 1e6:.2f} MB")
    if missing:
        print('  缺图（用了占位图）：' + ' '.join(missing))

    data = {
        'title': '小石猴点灯',
        'tagline': plan['tagline'],
        'sections': [{'no': s['no'], 'name': s['name']} for s in secs],
        'pages': pages,
        'cover': cover, 'end': end,
        'filmFile': FILM_FILES,
    }

    # —— 字体：页面上出现过的所有字符（常规）；标题/按钮/封面标语用的字符（粗体）
    css = (HERE / 'app.css').read_text('utf8')
    js = (HERE / 'app.js').read_text('utf8')
    tpl = (HERE / 'template.html').read_text('utf8')
    strip_c = lambda s: re.sub(r'(?<![:\'"\w])//[^\n]*', '', re.sub(r'/\*.*?\*/', '', s, flags=re.S))
    ascii_set = {chr(i) for i in range(32, 127)}
    all_text = json.dumps(data, ensure_ascii=False) + strip_c(css) + strip_c(js) + tpl
    chars = {ch for ch in all_text if ord(ch) > 127} | ascii_set
    ui_text = strip_c(js) + tpl + data['title'] + data['tagline'] + ''.join(s['no'] + s['name'] for s in secs) + '全书完灯'
    bold_chars = {ch for ch in ui_text if ord(ch) > 127} | ascii_set
    fonts = {}
    if no_font:
        fonts = {'regular': '', 'bold': ''}
    else:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            for weight, cs in (('regular', chars), ('bold', bold_chars)):
                out = pathlib.Path(td) / f'wk-{weight}.woff2'
                miss = subset_font(weight, cs, out)
                if miss:
                    print(f'  （{weight}）字体里没有的字符：{"".join(miss)}')
                fonts[weight] = base64.b64encode(out.read_bytes()).decode()
                print(f'字体 {weight}: {out.stat().st_size / 1e3:.0f} KB，{len(cs)} 个字符')

    # —— 拼成一个 HTML
    def js_json(o):
        return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = (tpl.replace('{{CSS}}', css).replace('{{FONT_REGULAR}}', fonts['regular']).replace('{{FONT_BOLD}}', fonts['bold'])
            .replace('{{DATA}}', js_json(data)).replace('{{IMAGES}}', js_json(imgs)).replace('{{JS}}', js))
    DIST.mkdir(exist_ok=True)
    out = DIST / 'xiaoshihou-book.html'
    out.write_text(html, 'utf8')
    print(f'写出 {out}  {out.stat().st_size / 1e6:.2f} MB，{len(pages)} 页')


if __name__ == '__main__':
    main()
