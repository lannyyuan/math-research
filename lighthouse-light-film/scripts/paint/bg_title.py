"""片头两侧的补边：封面是竖版的，左右用同样的靛蓝夜空 + 星星 + 细雪补满（不再用封面放大虚化，免得把灯光的暖色铺到两边去）。"""
from common import *


def main():
    L = Canvas(1920, 1080)
    L.rgb[:] = sky(1920, 1080, 'night', seed=51, horizon=1.2, blotch=0.35)
    L.a[:] = 1
    # 取封面最左/最右一列的平均颜色，让接缝处颜色一致
    cov = cv2.cvtColor(cv2.imread(str(OUT / 'cover.jpg')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    top = cov[:int(cov.shape[0] * 0.28), :int(cov.shape[1] * 0.06)].mean(axis=(0, 1))
    L.rgb *= (top / L.rgb[:200, 200:800].mean(axis=(0, 1)))[None, None, :] ** 0.8
    r = np.random.default_rng(2)
    for i in range(160):
        dots(L, [(r.uniform(0, 1920), r.uniform(0, 1080) ** 1.0, r.uniform(1.0, 2.2))], hexc('#dce6fa'), r.uniform(0.35, 0.9))
    L.rgb = np.clip(L.rgb, 0, 1)
    L.save(OUT / 'title_fill.jpg', jpg=True, q=92)


if __name__ == '__main__':
    main()
    print('ok')
