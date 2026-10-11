"""各画板共用：保存（夜色 / 光照 / 白天 / 晨光 多个版本 + manifest + 预览）。"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cn import *
import grade
import cv2

ROOT = pathlib.Path(__file__).resolve().parents[2]
BG = ROOT / 'public/bg'
BG.mkdir(parents=True, exist_ok=True)
PREV = pathlib.Path('/tmp/claude-0/-home-user-math-research/747091a3-a05e-575b-b1ac-cb27e1adeb12/scratchpad/prev')
PREV.mkdir(parents=True, exist_ok=True)

VAR = {
    'night': lambda rgb, g=0.7, k=0.2: grade.night(rgb, keep=k, gain=g),
    'lit': lambda rgb: grade.lit(rgb),
    'day': lambda rgb: grade.lit(rgb, sat=0.75, gain=1.1, tint=(1.04, 1.0, 0.93)),
    'dawn': lambda rgb: grade.dawn(rgb),
}


def save_plate(name, L, variants=('night', 'lit'), ext=None, gain=0.7, keep=0.2, overrides=None, wc=True):
    """L 是中性淡彩画布。ext 默认：不透明的存 jpg，有透明的存 png。"""
    if wc:
        import zlib
        watercolorize(L, seed=zlib.crc32(name.encode()) % 1000)
    opaque = float(L.a.min()) > 0.999
    ext = ext or ('jpg' if opaque else 'png')
    mf_path = BG / 'manifest.json'
    mf = json.loads(mf_path.read_text()) if mf_path.exists() else {}
    got = []
    for v in variants:
        if overrides and v in overrides:
            C = overrides[v]
        else:
            C = Canvas(L.w, L.h)
            C.rgb = (VAR[v](L.rgb, gain, keep) if v == 'night' else VAR[v](L.rgb)).astype(F)
            C.a = L.a.copy()
        C.save(BG / f'{name}_{v}.{ext}', jpg=(ext == 'jpg'), q=92)
        got.append(v)
    mf[name] = {'variants': got, 'ext': ext, 'w': L.w, 'h': L.h}
    mf_path.write_text(json.dumps(mf, indent=1))
    # 预览：夜色版 / 光照版 并排缩小
    tiles = []
    for v in got[:2]:
        im = cv2.imread(str(BG / f'{name}_{v}.{ext}'), cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 4:
            a = im[..., 3:4] / 255.0
            bgc = np.full_like(im[..., :3], 120)
            im = (im[..., :3] * a + bgc * (1 - a)).astype(np.uint8)
        tiles.append(cv2.resize(im, (L.w // 3, L.h // 3), interpolation=cv2.INTER_AREA))
    cv2.imwrite(str(PREV / f'{name}.jpg'), np.vstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('saved', name, got, ext, (L.w, L.h))
