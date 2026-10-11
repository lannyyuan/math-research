#!/usr/bin/env python3
"""读音规则的回归测试：python3 -X utf8 -m unittest webapp/test_pinyin.py
这些都是全书里 pypinyin 默认值会出错、后来用 pinyin_overrides.json 校对过的读音；改规则前后都应该是绿的。"""
import pathlib, re, sys, unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pinyin as P

HAN = re.compile('[一-鿿]')


def marked(text):
    return [P.mark(x) for x in P.annotate(text)]


class Rules(unittest.TestCase):
    def check(self, text, char, want, nth=0):
        """text 里第 nth 个 char 的读音 == want（带调符号；轻声不带符号）"""
        hz = [c for c in text if HAN.match(c)]
        idx = [i for i, c in enumerate(hz) if c == char][nth]
        self.assertEqual(marked(text)[idx], want, f'{text}：第 {nth + 1} 个“{char}”')

    def test_de(self):                     # 得：结构助词 / děi / dé
        self.check('他写得一笔好字', '得', 'de')
        self.check('跑得满头汗', '得', 'de')
        self.check('总得有人做', '得', 'děi')
        self.check('你们得当心', '得', 'děi')
        self.check('看他得了便宜', '得', 'dé')
        self.check('他认得了活物', '得', 'de')

    def test_zhe(self):                    # 着
        self.check('点着灯', '着', 'zhe')
        self.check('围着火堆吃东西', '着', 'zhe')
        self.check('老师戴着眼镜', '着', 'zhe')
        self.check('奶奶眯着眼看', '着', 'zhe')
        self.check('它睡着了', '着', 'zháo')
        self.check('别扎着手', '着', 'zháo')
        self.check('路上用得着', '着', 'zháo')

    def test_di(self):                     # 地：助词 de / 名词 dì
        self.check('只远远地看', '地', 'de')
        self.check('安安静静地走了', '地', 'de')
        self.check('一动不动地立着', '地', 'de')
        self.check('好奇地看他们', '地', 'de')
        self.check('他躺在草地上', '地', 'dì')
        self.check('这种地方', '地', 'dì')

    def test_misc(self):
        self.check('孩子慢慢长大', '长', 'zhǎng')
        self.check('他看见一条长街', '长', 'cháng')
        self.check('路走不长', '长', 'cháng')
        self.check('花草越种越多', '种', 'zhòng')
        self.check('这种地方', '种', 'zhǒng')
        self.check('大鱼看桥', '看', 'kān')
        self.check('她背起柜', '背', 'bēi')
        self.check('第四节背诗', '背', 'bèi')
        self.check('灯已经落下去', '落', 'luò')
        self.check('她数过塘里的鱼', '数', 'shǔ')
        self.check('还能挑半担水', '担', 'dàn')
        self.check('别担心', '担', 'dān')
        self.check('养鸭，还给猫备一只碗', '还', 'hái')
        self.check('已还给失主', '还', 'huán')
        self.check('谁都有第一次', '谁', 'shuí')
        self.check('不好意思', '思', 'si')

    def test_sandhi(self):                 # 一/不 变调（教材通行写法）
        self.check('下一个故事', '一', 'yí')
        self.check('送他一匹马', '一', 'yì')
        self.check('这是不对的', '不', 'bú')

    def test_neutral(self):
        self.check('我的书', '的', 'de')
        self.check('他走了', '了', 'le')
        self.check('石头', '头', 'tou', 0)

    def test_alignment(self):              # 每个汉字一个读音；标点不占位
        t = '“灯灭了，是灯心断了。”'
        self.assertEqual(len(P.annotate(t)), len([c for c in t if HAN.match(c)]))

    def test_mark(self):
        self.assertEqual(P.mark('zhang3'), 'zhǎng')
        self.assertEqual(P.mark('nv3'), 'nǚ')
        self.assertEqual(P.mark('lve4'), 'lüè')
        self.assertEqual(P.mark('liu2'), 'liú')
        self.assertEqual(P.mark('hui4'), 'huì')
        self.assertEqual(P.mark('gou3'), 'gǒu')
        self.assertEqual(P.mark('de5'), 'de')


if __name__ == '__main__':
    unittest.main()
