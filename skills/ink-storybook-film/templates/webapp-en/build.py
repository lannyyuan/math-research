#!/usr/bin/env python3
"""Build The Lighthouse Light as ONE self-contained HTML picture book: dist/lighthouse-light-book.html

  python3 webapp/build.py            # needs out/book_img/ first (node scripts/storyboard_plan.mjs && node scripts/book_stills.mjs)

Steps: plan.py paginates -> heroes.json assigns pictures -> check that the story text is complete and in order ->
       pictures to WebP -> embed the font (Andika, SIL OFL) -> inline CSS / JS / data / pictures / font into template.html.
The result needs no other file (put lighthouse-light-720p.mp4 next to it and the "Watch this scene" buttons play the film).
"""
import base64, io, json, pathlib, re, subprocess, sys
from PIL import Image, ImageStat

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'out'
IMG_DIR = ROOT / 'out' / 'book_img'
DIST = ROOT / 'dist'
FONTS = ROOT / 'public' / 'fonts'

WIDTH = 1440        # picture width (px)
QUALITY = 80
NORM = re.compile(r'[\s“”"‘’\']')


def norm(t: str) -> str:
    return NORM.sub('', t)


def highlight(text: str, cue_text: str):
    """Find the subtitle inside a paragraph (ignoring quotes and spaces); return (start, end) or None."""
    idx = [i for i, ch in enumerate(text) if not NORM.match(ch)]
    flat = ''.join(text[i] for i in idx)
    t = norm(cue_text).strip(',;:')
    pos = flat.find(t)
    if pos < 0:
        return None
    return idx[pos], idx[pos + len(t) - 1] + 1


def tc_seconds(tc: str) -> int:
    m, s = tc.split(':')
    return int(m) * 60 + int(s)


def main():
    subprocess.run([sys.executable, str(HERE / 'plan.py')], check=True, stdout=subprocess.DEVNULL)
    plan = json.loads((OUT / 'plan.json').read_text('utf8'))
    heroes = json.loads((HERE / 'heroes.json').read_text('utf8'))
    cues = {c['no']: c for c in plan['cues']}
    nsc = len(cues)

    pages, used, ordinal, nocue = [], set(), {}, {}
    for q in plan['pages']:
        if not q['cues']:
            nm = plan['sections'][q['sec']]['no']
            nocue[nm] = nocue.get(nm, 0) + 1
    for p in plan['pages']:
        paras = []
        for q in p['paras']:
            segs, text, spans = [], q['text'], []
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
        marked = {s[1] for q in paras for s in q['segs'] if s[1]}
        missing = set(p['cues']) - marked
        if missing:
            sys.exit(f"page {p['i']}: subtitle(s) {sorted(missing)} could not be marked in the text")
        if p['cues']:
            c = cues[p['cues'][0]]
            hero = {'img': f"cue/{p['cues'][0]:02d}", 'fx': 0.5, 'fy': 0.55, 'z': 1,
                    'cap': f"From the film  ·  scene {p['cues'][0]}/{nsc}  ·  {c['tc']}",
                    'alt': f"Picture from the film: {c['sceneName']}. Subtitle: {c['text']}"}
        else:
            no = plan['sections'][p['sec']]['no']
            lst = heroes['sections'].get(no)
            k = ordinal.get(no, 0)
            ordinal[no] = k + 1
            if lst:
                # the m cue-less pages of a chapter share its L pictures in order (neighbours share a picture: only the text turns)
                hero = {'z': 1, 'fx': 0.5, 'fy': 0.55, **lst[min(len(lst) - 1, k * len(lst) // nocue[no])]}
            elif pages and pages[-1]['sec'] == p['sec']:
                prev = pages[-1]['hero']
                hero = {**prev, 'z': 1.55 if prev.get('z', 1) < 1.3 else 1.0, 'fx': 0.5 + (0.12 if k % 2 else -0.12), 'fy': 0.62}
                print(f"  note: page {p['i']} ({no}) reuses the previous picture; add pictures for \"{no}\" in heroes.json")
            else:
                sys.exit(f"page {p['i']} ({no}) has no film frame and no entry in heroes.json sections")
        hero.setdefault('z', 1)
        used.add(hero['img'])
        pages.append({'i': p['i'], 'sec': p['sec'], 'startsSec': p['startsSec'], 'w': p['w'], 'cues': p['cues'],
                      'endsMid': p.get('endsMid', False), 'hero': hero, 'paras': paras})

    # —— the whole story, in order, nothing lost or repeated
    raw = (ROOT / 'story/source.md').read_text('utf8').split('\n')
    cut = next((i for i, l in enumerate(raw) if re.match(r'^---\s*$', l)), len(raw))
    src = ''.join(l for l in raw[:cut] if l.strip() and not l.startswith('#'))
    got = ''.join(s[0] for pg in pages for q in pg['paras'] for s in q['segs'])
    if norm(src) != norm(got):
        n = min(len(norm(src)), len(norm(got)))
        k = next((i for i in range(n) if norm(src)[i] != norm(got)[i]), n)
        sys.exit(f"text check failed at character {k}\nstory: {norm(src)[k-12:k+24]}\npages: {norm(got)[k-12:k+24]}")
    print(f"text check passed: {len(norm(src))} characters (without spaces/quotes), {sum(len(pg['paras']) for pg in pages)} paragraph pieces, {len(pages)} pages")

    # —— storyboard (all film pictures with subtitles, in film order)
    page_of_cue = {no: pg['i'] for pg in pages for no in pg['cues']}
    scenes, seen = [{'id': 's0-title', 'name': 'Title', 'cues': []}], {}
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
        used.add(f'cue/{no:02d}')
    used.add(heroes['cover']['img']); used.add(heroes['end']['img'])

    data = {
        'title': plan['title'],
        'sections': [{'no': s['no'], 'short': s['short'], 'name': s['name']} for s in plan['sections']],
        'pages': pages, 'cues': cue_list, 'scenes': scenes,
        'titleCard': {'tc': plan['titleCard']['tc'], 'sec': tc_seconds(plan['titleCard']['tc'])},
        'cover': heroes['cover'], 'end': heroes['end'],
        'filmFile': ['lighthouse-light-720p.mp4', 'lighthouse-light.mp4'],
    }

    # —— pictures -> WebP -> base64
    imgs, total = {}, 0
    for key in sorted(used):
        png = IMG_DIR / f'{key}.png'
        if not png.exists():
            sys.exit(f'missing picture {png} (run node scripts/book_stills.mjs)')
        im = Image.open(png).convert('RGB')
        lum = ImageStat.Stat(im.convert('L')).mean[0]
        if lum < 50:   # very dark pictures get a little lift, otherwise they are just a black rectangle on a screen
            im = im.point([int(255 * ((i / 255) ** 0.66)) for i in range(256)] * 3)
            print(f'  brightened {key} (mean luminance {lum:.0f})')
        im = im.resize((WIDTH, round(WIDTH * im.height / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=QUALITY, method=6)
        total += buf.tell()
        imgs[key] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    print(f'{len(imgs)} pictures, {total/1e6:.1f} MB of WebP')

    # —— font (Andika, SIL OFL 1.1; the Latin subset already covers the quotes, dashes and é used in the story)
    fonts = {w: base64.b64encode((FONTS / f'andika-latin-{n}-normal.woff2').read_bytes()).decode() for w, n in (('regular', 400), ('bold', 700))}

    css = (HERE / 'app.css').read_text('utf8')
    js = (HERE / 'app.js').read_text('utf8')
    tpl = (HERE / 'template.html').read_text('utf8')

    def js_json(o):
        return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = (tpl.replace('{{CSS}}', css).replace('{{FONT_REGULAR}}', fonts['regular']).replace('{{FONT_BOLD}}', fonts['bold'])
            .replace('{{DATA}}', js_json(data)).replace('{{IMAGES}}', js_json(imgs)).replace('{{JS}}', js))
    DIST.mkdir(exist_ok=True)
    out = DIST / 'lighthouse-light-book.html'
    out.write_text(html, 'utf8')
    print(f'wrote {out}  {out.stat().st_size/1e6:.1f} MB')


if __name__ == '__main__':
    main()
