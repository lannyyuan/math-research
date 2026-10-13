import json, re, unicodedata, sys, collections
from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR
from pypinyin import pinyin, Style

eng = RapidOCR()
CX = [75, 215, 355, 493, 633]
RY = [208 + 80 * k for k in range(10)]
HAN = re.compile(r'[一-鿿]')

def tight(gray, box, thr=140, pad=4):
    img = gray.crop(box); a = np.array(img); ys, xs = np.where(a < thr)
    if len(ys) == 0: return None
    return img.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(img.width, xs.max() + pad + 1), min(img.height, ys.max() + pad + 1)))

def tile(g, n=3, H=64, gap=24):
    w = max(1, int(g.width * H / g.height)); g = g.resize((w, H), Image.LANCZOS)
    c = Image.new('L', (n * (w + gap) + gap, H + 24), 255)
    for i in range(n): c.paste(g, (gap + i * (w + gap), 12))
    return np.array(c.convert('RGB'))[:, :, ::-1]

def norm_py(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch)).lower().replace('ü', 'u').replace('v', 'u')
    return re.sub('[^a-z]', '', s)

def ed(a, b):
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[-1]

cells = []; imgs = []; pimgs = []
for pg in range(1, 27):
    gray = Image.open(f'pg/p-{pg:02d}.png').convert('L'); S = gray.width / 750
    for ri, r in enumerate(RY):
        for ci, c in enumerate(CX):
            g = tight(gray, (int((c - 36) * S), int((r - 24) * S), int((c + 36) * S), int((r + 40) * S)))
            p = tight(gray, (int((c - 60) * S), int((r - 46) * S), int((c + 60) * S), int((r - 17) * S)), thr=150, pad=3)
            cells.append({'page': pg, 'row': ri + 1, 'col': ci + 1})
            imgs.append(tile(g) if g is not None else None)
            pimgs.append(tile(p, n=2, H=48) if p is not None else None)

def run(batch):
    out = [None] * len(batch); idx = [i for i, b in enumerate(batch) if b is not None]
    for s in range(0, len(idx), 64):
        sub = idx[s:s + 64]
        res, _ = eng.text_recognizer([batch[i] for i in sub])
        for i, (t, c) in zip(sub, res): out[i] = (t, float(c))
    return out

cres = run(imgs); pres = run(pimgs)
for x, cr, pr in zip(cells, cres, pres):
    txt = cr[0] if cr else ''
    hs = HAN.findall(txt)
    x['raw'] = txt
    if hs:
        ch, k = collections.Counter(hs).most_common(1)[0]
        x['char'] = ch; x['votes'] = k
    else:
        x['char'] = ''; x['votes'] = 0
    x['conf'] = round(cr[1], 3) if cr else 0.0
    x['py_ocr'] = pr[0] if pr else ''
    got = norm_py(x['py_ocr'])
    cands = {norm_py(p) for p in sum(pinyin(x['char'], style=Style.NORMAL, heteronym=True), [])} if x['char'] else set()
    x['py_ok'] = bool(cands) and bool(got) and (got in cands or any(ed(got, c) <= 1 for c in cands))
json.dump(cells, open('ocr_rows.json', 'w'), ensure_ascii=False)
ok = [x for x in cells if x['char'] and x['votes'] >= 2 and x['py_ok']]
print('cells', len(cells), '| confident (>=2 votes & pinyin ok):', len(ok), '| need review:', len(cells) - len(ok))
print('empty:', sum(1 for x in cells if not x['char']))
