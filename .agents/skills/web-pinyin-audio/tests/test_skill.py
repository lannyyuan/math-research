#!/usr/bin/env python3
"""skill 的离线自检（不需要浏览器、网络、ffmpeg）：
    python3 -X utf8 -m unittest discover -s <skill>/tests -v        （先 pip install pypinyin）
带 ffmpeg + Pinyin_Drill 目录的机器上，还会多跑一条“现做新录音”的用例；否则那条自动跳过。
"""
import json, os, pathlib, re, shutil, sys, tempfile, unittest

SKILL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / 'scripts'))
import pinyin_annotate as pa, pinyin_clips as pc, wrap_html as wh

DEMO = (SKILL / 'assets' / 'demo.html').read_text('utf8')


class Annotate(unittest.TestCase):
    def setUp(self):
        self.a = pa.Annotator()

    def test_starter_rules(self):
        t = lambda s: [pa.mark(x) for x in self.a.annotate(s)]
        self.assertEqual(t('慢慢地走')[2], 'de')            # 叠词+地 → 助词，轻声
        self.assertEqual(t('安安静静地走')[4], 'de')
        self.assertEqual(t('土地很大')[1], 'dì')            # 名词的地不动
        self.assertEqual(t('谁来了')[0], 'shuí')            # 录音库没有 shei2
        self.assertEqual(t('长长的桥')[:2], ['cháng', 'cháng'])   # pypinyin 默认给 cháng zhǎng

    def test_alignment_and_punctuation(self):
        s = '“灯灭了，是灯心断了。”'
        self.assertEqual(len(self.a.annotate(s)), len(re.findall('[\u4e00-\u9fff]', s)))
        self.assertEqual(self.a.annotate('abc，123'), [])

    def test_mark(self):
        for pid, want in [('zhang3', 'zhǎng'), ('nv3', 'nǚ'), ('lve4', 'lüè'), ('liu2', 'liú'), ('hui4', 'huì'), ('gou3', 'gǒu'), ('de5', 'de'), ('ou1', 'ōu')]:
            self.assertEqual(pa.mark(pid), want)

    def test_custom_rules_and_trace(self):
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / 'r.json'
            f.write_text(json.dumps({'rules': [{'ctx': '大«长»', 'py': 'chang4'}]}), 'utf8')   # 故意写一个 pypinyin 绝不会给的值，便于断言
            tr = []
            py = pa.Annotator(f).annotate('大长今', tr)
            self.assertEqual(py[1], 'chang4')
            self.assertEqual([(t[1], t[2]) for t in tr][0][1], 'chang4')
            f.write_text(json.dumps({'rules': [{'ctx': '没有标记', 'py': 'a1'}]}), 'utf8')
            with self.assertRaises(ValueError):
                pa.Annotator(f)


class Wrap(unittest.TestCase):
    def setUp(self):
        self.a = pa.Annotator()
        self.out, self.ids, self.n = wh.wrap(DEMO, self.a)

    def test_text_unchanged(self):
        stripped = re.sub(r'<span class="hz" data-p="[a-z]+[1-5]">(.)</span>', r'\1', self.out)
        self.assertEqual(stripped, DEMO)                    # 去掉 span 就是原稿：一个字节都没多

    def test_skipped_areas_untouched(self):
        self.assertIn('<code>长大了</code>', self.out)
        self.assertIn('<button type="button">开始学习</button>', self.out)
        self.assertIn('<a href="#x">更多故事</a>', self.out)
        self.assertIn('<p data-nopy>这一段带 data-nopy，不标拼音。</p>', self.out)
        self.assertIn('window.demoMarker = "脚本里的汉字不会被改：长大";', self.out)
        self.assertIn('<title>小石猴识字课（样例）</title>', self.out)
        self.assertIn('&amp;', self.out)
        self.assertIn('<br/>', self.out)
        self.assertIn('<!-- 这一页用来演示和自检', self.out)

    def test_wrapped_and_readings(self):
        self.assertIn('<span class="hz" data-p="de5">地</span>', self.out)
        self.assertIn('<span class="hz" data-p="zhang3">长</span>', self.out)    # 长大
        self.assertIn('<span class="hz" data-p="chang2">长</span>', self.out)    # 长长的桥
        self.assertEqual(self.n, len(re.findall(r'class="hz"', self.out)))
        self.assertTrue(all(re.fullmatch(r'[a-z]+[1-5]', i) for i in self.ids))

    def test_refuse_double_wrap(self):
        with self.assertRaises(ValueError):
            wh.wrap(self.out, self.a)

    def test_text_nodes(self):
        nodes = wh.text_nodes(DEMO)
        self.assertTrue(any('慢慢地走' in t for t in nodes))
        self.assertFalse(any('长大了' == t for t in nodes))   # <code> 里的不收

    def test_embed(self):
        html = wh.embed(self.out, {'a1': 'data:audio/mpeg;base64,AA=='})
        self.assertEqual(html.count('</body>'), 1)
        self.assertIn('window.__PYA={"a1"', html)
        self.assertIn('PinyinHover.init(', html)
        self.assertIn('id="pyh-css"', html)
        self.assertIn('CC-BY-SA 3.0', html)
        self.assertNotIn('class="pyh-note"', wh.embed(self.out, {}, credit=False))
        self.assertIn('class="pyh-note"', html)


class Clips(unittest.TestCase):
    def test_from_seed_and_library(self):
        ids = {'zhang3', 'de5', 'ta1', 'nv3'}
        with tempfile.TemporaryDirectory() as d:
            lib = pathlib.Path(d) / 'lib'
            uris, rep = pc.build_clips(ids, lib, drill='Z:/none', net=False)
            self.assertEqual((rep['from_seed'], rep['from_lib'], rep['generated'], rep['missing']), (4, 0, 0, []))
            self.assertTrue(all(u.startswith('data:audio/mpeg;base64,') for u in uris.values()))
            man = json.loads((lib / 'manifest.json').read_text('utf8'))
            self.assertEqual(set(man['clips']) | set(man['neutral']), ids)
            self.assertIn('base', man['neutral']['de5'])
            _, rep2 = pc.build_clips(ids, lib, drill='Z:/none', net=False)
            self.assertEqual((rep2['from_lib'], rep2['from_seed']), (4, 0))
            (lib / 'ta1.mp3').write_bytes(b'tampered')          # 库文件被改动 → 报错，不会悄悄用
            with self.assertRaises(SystemExit):
                pc.build_clips(ids, lib, drill='Z:/none', net=False)

    def test_pack_seed_roundtrip(self):
        ids = {'zhang3', 'de5', 'ta1'}
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            uris, _ = pc.build_clips(ids, d / 'lib', drill='Z:/none', net=False)
            self.assertEqual(pc.pack_seed(d / 'lib', out=d / 'seed2'), 3)
            self.assertEqual(pc.seed_ids(d / 'seed2'), ids)
            uris2, rep = pc.build_clips(ids, d / 'lib2', seed=d / 'seed2', drill='Z:/none', net=False)
            self.assertEqual((uris2, rep['from_seed']), (uris, 3))          # 重新打包的种子库 → 同样的录音
            pc.pack_seed(d / 'lib', out=d / 'seed3')
            self.assertEqual((d / 'seed2' / 'clips.zip').read_bytes(), (d / 'seed3' / 'clips.zip').read_bytes())   # 可重复生成

    def test_missing_and_bad_ids(self):
        with tempfile.TemporaryDirectory() as d:
            _, rep = pc.build_clips({'ju4', 'ta1'}, pathlib.Path(d) / 'lib', drill='Z:/none', net=False)
            self.assertEqual(rep['missing'], ['ju4'])            # 没有录音：报告出来，不崩
            for bad in ['../x1', 'zhang', 'a6', 'ZHANG3', 'a1/../b2']:
                with self.assertRaises(ValueError):
                    pc.build_clips({bad}, pathlib.Path(d) / 'lib2', net=False)

    @unittest.skipUnless(shutil.which('ffmpeg') and (pc.DRILL / 'human-audio-downloads' / 'audio').exists(), '需要 ffmpeg 和 Pinyin_Drill 目录')
    def test_generate_new_clip(self):
        have = pc.seed_ids()
        # 找一个种子库里既没有本调、也没有对应轻声的音节
        new = next(p.stem[4:] for p in sorted((pc.DRILL / 'human-audio-downloads' / 'audio').glob('cmn-*.mp3'))
                   if re.fullmatch(r'[a-z]+[1-4]', p.stem[4:]) and p.stem[4:] not in have and p.stem[4:-1] + '5' not in have)
        with tempfile.TemporaryDirectory() as d:
            lib = pathlib.Path(d) / 'lib'
            uris, rep = pc.build_clips({new, new[:-1] + '5'}, lib, net=False)
            self.assertEqual(rep['generated'], 2, rep)
            for i in (new, new[:-1] + '5'):
                self.assertTrue(500 < (lib / f'{i}.mp3').stat().st_size < 30000)
            self.assertFalse(list(lib.glob('*.part')))


if __name__ == '__main__':
    unittest.main()
