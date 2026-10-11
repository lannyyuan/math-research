#!/usr/bin/env python3
"""静态 HTML → 带“点字看拼音、听发音”的单文件 HTML（构建期，一条命令）。

  wrap_html.py page.html -o page.pinyin.html [--lib pinyin_clips] [--rules my_rules.json] [--no-audio] [--no-credit] [--skip-tags a,b]

做三件事：
  1. 给每个汉字标拼音，把汉字包成 <span class="hz" data-p="zhang3">长</span>（只加标签，页面文字一个字不改）
  2. 把用到的“音节+声调”录音（同音共用）打包成 window.__PYA，连同 pinyin_hover.js / .css 一起内联进页面 → 单文件、file:// 离线可用
  3. 在 </body> 前加一小块说明（开关 + 发音致谢；CC-BY-SA 要求署名，别删，想换样式可以改 CSS）
不会包的地方：<script> <style> <title> <head> <code> <pre> <button> <a> <input>… 以及带 data-nopy 的元素里面的字。
限制：每个文本节点单独标拼音，被行内标签（<b>、<span>…）切开的词读音上下文会丢，别把一个词拆在两个标签里。
需要 pypinyin；录音取自本 skill 的种子库/项目 lib，缺的才要 ffmpeg（见 pinyin_clips.py）。Windows 请用 `python -X utf8`。
如果页面是 JS 渲染的（SPA），不要用本脚本：见 SKILL.md“B. JS 渲染的应用”。
"""
import json, pathlib, re, sys
from html.parser import HTMLParser

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
HAN = re.compile('[一-鿿]')
SKIP_TAGS = {'script', 'style', 'textarea', 'title', 'head', 'noscript', 'svg', 'math', 'code', 'pre', 'kbd', 'samp', 'template',
             'button', 'select', 'option', 'input', 'a', 'iframe'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

CREDIT = ('<aside class="pyh-note" data-nopy><span>汉字可点：悬停看拼音，点一下听发音。</span>'
          '<button type="button" id="pyh-toggle">关闭拼音</button>'
          '<details><summary>发音致谢</summary><p>真人录音：Chen Wang 王琛（<a href="https://github.com/hugolpz/audio-cmn" target="_blank" rel="noopener">audio-cmn</a>），'
          '<a href="https://creativecommons.org/licenses/by-sa/3.0/" target="_blank" rel="noopener">CC-BY-SA 3.0</a>；已裁剪静音并转码，轻声为模拟。'
          '仅供识字参考，不是教材认证录音。</p></details></aside>')


class _Walker(HTMLParser):
    """原样回写整份 HTML（标签文本逐字保留），只在不被跳过的文本里把汉字包起来。ann=None 时只收集文本。"""

    def __init__(self, ann=None, skip_tags=()):
        super().__init__(convert_charrefs=False)
        self.ann, self.skip_tags = ann, SKIP_TAGS | set(skip_tags)
        self.out, self.stack, self.ids, self.texts, self.nhan = [], [], set(), [], 0

    @property
    def skipping(self):
        return any(s for _, s in self.stack)

    def handle_starttag(self, tag, attrs):
        self.out.append(self.get_starttag_text())
        if tag in VOID:
            return
        names = {k: (v or '') for k, v in attrs}
        self.stack.append((tag, tag in self.skip_tags or 'data-nopy' in names or names.get('translate') == 'no'))

    def handle_startendtag(self, tag, attrs):
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.out.append(f'</{tag}>')
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k][0] == tag:
                del self.stack[k:]
                break

    def handle_data(self, data):
        if self.skipping or not HAN.search(data):
            self.out.append(data)
            return
        self.texts.append(data)
        if self.ann is None:
            self.out.append(data)
            return
        py = self.ann.annotate(data)
        self.ids.update(py)
        k, parts = 0, []
        for ch in data:
            if HAN.match(ch):
                parts.append(f'<span class="hz" data-p="{py[k]}">{ch}</span>')
                k += 1
            else:
                parts.append(ch)
        self.nhan += k
        self.out.append(''.join(parts))

    def handle_entityref(self, name):
        self.out.append(f'&{name};')

    def handle_charref(self, name):
        self.out.append(f'&#{name};')

    def handle_comment(self, data):
        self.out.append(f'<!--{data}-->')

    def handle_decl(self, decl):
        self.out.append(f'<!{decl}>')

    def handle_pi(self, data):
        self.out.append(f'<?{data}>')

    def unknown_decl(self, data):
        self.out.append(f'<![{data}]>')


def text_nodes(html_text):
    """会被标拼音的文本节点（含汉字的）→ list[str]"""
    w = _Walker()
    w.feed(html_text)
    w.close()
    return w.texts


def wrap(html_text, ann, skip_tags=()):
    """→ (新 HTML, 用到的读音 id 集合, 汉字个数)"""
    if 'class="hz"' in html_text and 'data-p=' in html_text:
        raise ValueError('这份 HTML 已经包过汉字了（有 class="hz" data-p=…），请从原稿重新生成')
    w = _Walker(ann, skip_tags)
    w.feed(html_text)
    w.close()
    return ''.join(w.out), w.ids, w.nhan


def embed(html_text, uris, credit=True):
    """把 CSS、录音、运行期脚本内联进去（</head> 前放样式；</body> 前放说明和脚本）"""
    css = (HERE / 'pinyin_hover.css').read_text('utf8')
    js = (HERE / 'pinyin_hover.js').read_text('utf8')
    style = f'<style id="pyh-css">\n{css}</style>\n'
    html_text, n = re.subn(r'</head>', lambda m: style + '</head>', html_text, count=1, flags=re.I)
    if not n:
        html_text = style + html_text
    tail = (CREDIT + '\n' if credit else '') + \
        '<script>window.__PYA=' + json.dumps(uris, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';</script>\n' + \
        f'<script>\n{js}</script>\n<script>PinyinHover.init({{audio: window.__PYA, toggle: "#pyh-toggle"}});</script>\n'
    html_text, n = re.subn(r'</body>', lambda m: tail + '</body>', html_text, count=1, flags=re.I)
    return html_text if n else html_text + tail


def _main(argv):
    def opt(name, default=None):
        if name in argv:
            i = argv.index(name)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
        return default
    out, lib, rules, skip = opt('-o'), opt('--lib', 'pinyin_clips'), opt('--rules'), opt('--skip-tags', '')
    no_audio, no_credit = '--no-audio' in argv, '--no-credit' in argv
    files = [a for a in argv if not a.startswith('--')]
    if len(files) != 1 or not out:
        sys.exit(__doc__)
    import pinyin_annotate as pa, pinyin_clips as pc
    ann = pa.Annotator(rules)
    src = pathlib.Path(files[0]).read_text('utf8')
    new, ids, nhan = wrap(src, ann, [t for t in skip.split(',') if t])
    uris, rep = ({}, None) if no_audio else pc.build_clips(ids, lib, neutral=ann.neutral)
    new = embed(new, uris, credit=not no_credit)
    pathlib.Path(out).write_text(new, 'utf8')
    msg = f'{nhan} 个汉字 → {len(ids)} 种读音'
    if rep:
        msg += f"；录音 {rep['clips']} 条 {rep['bytes'] / 1e6:.2f} MB（项目库 {rep['from_lib']}，种子库 {rep['from_seed']}，新生成 {rep['generated']}）"
        if rep['missing']:
            msg += '；缺录音：' + ' '.join(rep['missing'])
    print(f'写出 {out}（{len(new) / 1e6:.2f} MB）：{msg}')


if __name__ == '__main__':
    _main(sys.argv[1:])
