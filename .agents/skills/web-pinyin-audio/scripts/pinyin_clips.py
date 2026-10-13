#!/usr/bin/env python3
"""拼音发音录音库（构建期）：每个“音节+声调”只存一条（zhang3.mp3），同音共用——不是一字一个文件。

  from pinyin_clips import build_clips
  uris, report = build_clips({'zhang3', 'de5', 'ta1'}, lib='pinyin_clips')    # uris = {id: 'data:audio/mpeg;base64,…'}

库 lib/ 是项目自己的目录，里面是处理好的 `{id}.mp3` 和 `manifest.json`，**随项目提交**。每个 id 按这个顺序找录音：
  1. lib/{id}.mp3                      项目里已有的（核对清单里的 SHA-256；被改动会报错）
  2. 本 skill 的种子库 assets/clips/clips.zip（846 条，已处理好）→ 解出来放进 lib/     不需要 ffmpeg
  3. Pinyin_Drill 的真人录音  <PINYIN_DRILL_DIR>/human-audio-downloads/audio/cmn-{id}.mp3   （环境变量，只读；没有就跳过）
  4. 上游 hugolpz/audio-cmn（固定 revision）下载                                         （联网；--no-net 禁用）
  3、4 取到的原始录音要用 ffmpeg 处理：裁首尾静音 → 单声道 22.05 kHz、32 kbps MP3（约 4 KB）→ 存进 lib/。
轻声（5 声）没有录音：取该音节另一声的录音截短到 0.30 s、尾部渐弱、降音量来模拟（规则见 neutral 参数，默认 prefer=[3,4,2,1]）。
上游也没有的音节（404）记进清单的 unavailable，以后不再联网去问；页面里那几个字只显示拼音（或用系统语音）。

命令行（Windows 请用 `python -X utf8`）：
  pinyin_clips.py --lib pinyin_clips --ids zhang3,de5,ta1 [--emit-json pya.json | --emit-js pya.js] [--no-net]
  pinyin_clips.py --lib pinyin_clips --text a.txt b.html [--rules my_rules.json] [--emit-js pya.js]    先标拼音再取录音
  pinyin_clips.py --pack-seed 某个录音库目录 [--manifest 清单.json]     维护用：把一个录音库重新打包成本 skill 的种子库（clips.zip + manifest.json）

录音：Chen Wang 王琛（Wang Chen, Lopez Hugo, Vion Nicolas），CC-BY-SA-3.0，https://github.com/hugolpz/audio-cmn ——
发布时必须在页面里署名并说明“已裁剪转码、轻声为模拟”（pinyin_hover 的 credit 区块已写好），详见 assets/clips/ATTRIBUTION.md。
"""
import base64, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, urllib.request, urllib.error, zipfile

HERE = pathlib.Path(__file__).resolve().parent
SEED = HERE.parent / 'assets' / 'clips'
DRILL = pathlib.Path(os.environ.get('PINYIN_DRILL_DIR', 'D:/Users/lanny/playground/KunKun-study/Pinyin_Drill_P0'))
REV = 'ff9ed3d0c631195bd2c06f39450f3264c7124040'
UPSTREAM = 'https://raw.githubusercontent.com/hugolpz/audio-cmn/{rev}/64k/syllabs/cmn-{id}.mp3'
CACHE = pathlib.Path(tempfile.gettempdir()) / 'web-pinyin-audio-cache'


class _Seed:
    """种子库：assets/clips/clips.zip（只含 {id}.mp3，一个文件，省得 skill 目录里躺几百个文件；也认目录里散放的 mp3）+ manifest.json"""

    def __init__(self, d):
        self.dir = pathlib.Path(d)
        z = self.dir / 'clips.zip'
        self.zip = zipfile.ZipFile(z) if z.exists() else None
        self.names = {n[:-4] for n in self.zip.namelist() if n.endswith('.mp3')} if self.zip else set()
        self.names |= {f.stem for f in self.dir.glob('*.mp3')}
        m = self.dir / 'manifest.json'
        self.man = json.loads(m.read_text('utf8')) if m.exists() else {}

    def read(self, i):
        f = self.dir / f'{i}.mp3'
        return f.read_bytes() if f.exists() else self.zip.read(f'{i}.mp3')

    def path(self, i):
        """给 ffmpeg 当输入的真实文件（zip 里的先解到缓存目录）"""
        f = self.dir / f'{i}.mp3'
        if f.exists():
            return f
        out = CACHE / 'seed' / f'{i}.mp3'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(self.zip.read(f'{i}.mp3'))
        return out


def seed_ids(seed=SEED):
    """种子库里有哪些读音 id"""
    return _Seed(seed).names


ID_RE = re.compile(r'[a-z]{1,6}[1-5]')           # 音节+声调；id 会拼进文件路径和网址，必须先校验

TRIM = ('silenceremove=start_periods=1:start_silence=0.03:start_threshold=-42dB,areverse,'
        'silenceremove=start_periods=1:start_silence=0.05:start_threshold=-42dB,areverse,'
        'afade=t=in:d=0.006,areverse,afade=t=in:d=0.04,areverse')
ENC = ['-ac', '1', '-ar', '22050', '-c:a', 'libmp3lame', '-b:a', '32k']
NEUTRAL_LEN, NEUTRAL_FADE, NEUTRAL_GAIN = 0.30, 0.13, 0.85
NOTE = ('录音清单。clips：音节 id → 来源 src(drill=Pinyin_Drill，upstream=hugolpz/audio-cmn，manual=手工放入) + 原始 MP3 的 SHA-256(sha256) '
        '+ 本目录文件的 SHA-256(clip_sha256)；neutral：模拟的轻声 id → 底本音节 base + 本目录文件的 SHA-256；unavailable：上游也没有的音节。')


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _ffmpeg():
    exe = shutil.which('ffmpeg')
    if not exe:
        sys.exit('找不到 ffmpeg：这些音节不在项目库和种子库里，需要 ffmpeg 来裁剪/转码。请把 ffmpeg 放进 PATH，或把处理好的 {id}.mp3 直接放进库目录。')
    return exe


def _run(args, dest):
    """ffmpeg 输出先写 .part，成功再换名：中途失败不会在库里留下半截文件"""
    part = pathlib.Path(str(dest) + '.part')
    try:
        subprocess.run([_ffmpeg(), '-y', '-loglevel', 'error', *args, '-f', 'mp3', str(part)], check=True)
        os.replace(part, dest)
    finally:
        part.unlink(missing_ok=True)


def _dump(man: dict) -> str:
    """清单一条一行（好读、好 diff）"""
    j = lambda v: json.dumps(v, ensure_ascii=False)
    lines = ['{']
    for k, v in man.items():
        if k not in ('clips', 'neutral'):
            lines.append(f' {j(k)}: {j(v)},')
    for sec in ('clips', 'neutral'):
        items = sorted(man.get(sec, {}).items())
        lines.append(f' "{sec}": {{')
        lines += [f'  {j(k)}: {j(v)}' + (',' if n < len(items) - 1 else '') for n, (k, v) in enumerate(items)]
        lines.append(' }' + (',' if sec == 'clips' else ''))
    lines.append('}')
    return '\n'.join(lines) + '\n'


def _source(i, drill, net, log):
    """→ (bytes, 'drill'|'upstream') / (None, '404' 上游确实没有) / (None, None)"""
    f = pathlib.Path(drill) / 'human-audio-downloads' / 'audio' / f'cmn-{i}.mp3'
    if f.exists():
        return f.read_bytes(), 'drill'
    c = CACHE / 'src' / f'cmn-{i}.mp3'
    if c.exists():
        return c.read_bytes(), 'upstream'
    if not net:
        return None, None
    try:
        req = urllib.request.Request(UPSTREAM.format(rev=REV, id=i), headers={'User-Agent': 'web-pinyin-audio'})
        data = urllib.request.urlopen(req, timeout=30).read()
    except urllib.error.HTTPError as e:
        log(f'  没有录音 {i}（{str(e)[:40]}）')
        return None, ('404' if e.code == 404 else None)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        log(f'  没有录音 {i}（{str(e)[:40]}）')
        return None, None
    c.parent.mkdir(parents=True, exist_ok=True)
    c.write_bytes(data)
    return data, 'upstream'


def build_clips(ids, lib, *, neutral=None, seed=SEED, drill=DRILL, net=True, log=print):
    """ids：要用到的拼音 id 集合。→ ({id: dataURI}, report)。lib 目录和 manifest.json 会被创建/更新（记得提交）。"""
    lib = pathlib.Path(lib)
    lib.mkdir(parents=True, exist_ok=True)
    mpath = lib / 'manifest.json'
    man = json.loads(mpath.read_text('utf8')) if mpath.exists() else {}
    clips, neu = man.setdefault('clips', {}), man.setdefault('neutral', {})
    seed = _Seed(seed) if seed and pathlib.Path(seed).exists() else None
    sman = seed.man if seed else {}
    unavail = set(man.get('unavailable', [])) | set(sman.get('unavailable', []))      # 种子库已知上游也没有的（如 ju4）：不再联网去问
    neutral = neutral or {}
    prefer, indiv = neutral.get('prefer', [3, 4, 2, 1]), neutral.get('individual', {})
    ids = set(ids)
    bad = sorted(i for i in ids if not ID_RE.fullmatch(i))
    if bad:
        raise ValueError(f'不是“音节+声调数字”的读音 id：{bad[:5]}')
    st = {'from_lib': 0, 'from_seed': 0, 'generated': 0, 'changed': False}
    out, srcs, missing, neutral_map, tmp = {}, {}, [], {}, {}

    def existing(i, sec):
        """项目库有就用（核对 SHA；清单里没记就收编）；没有再看种子库（复制进库）。→ Path | None"""
        table = man[sec]
        ent = table.get(i, {})
        f = lib / f'{i}.mp3'
        if f.exists():
            h = _sha(f.read_bytes())
            if ent.get('clip_sha256') and ent['clip_sha256'] != h:
                sys.exit(f'{f} 和清单里记的不一样（{ent["clip_sha256"][:12]} → {h[:12]}）。若是有意更换，请先从 {mpath} 删掉 {i} 的记录。')
            if not ent.get('clip_sha256'):            # 清单里没记：当作手工放入的，登记下来
                table[i] = dict(ent, clip_sha256=h)
                if sec == 'clips':
                    table[i].setdefault('src', 'manual')
                st['changed'] = True
            st['from_lib'] += 1
            return f
        if seed and i in seed.names:
            sent = sman.get(sec, {}).get(i, {})
            data = seed.read(i)
            h = _sha(data)
            if sent.get('clip_sha256') and sent['clip_sha256'] != h:
                sys.exit(f'种子库里的 {i}.mp3 和它的清单对不上（文件损坏？）')
            part = f.with_name(f.name + '.part')            # 先写 .part 再换名：中途中断不会留下被当成“手工放入”的半截文件
            part.write_bytes(data)
            os.replace(part, f)
            table[i] = dict(sent, clip_sha256=h)
            st['changed'] = True
            st['from_seed'] += 1
            return f
        return None

    def raw(i, net_ok=True):
        """从来源取原始录音并核对/登记。→ bytes | None"""
        if i in unavail:
            return None
        data, where = _source(i, drill, net and net_ok, log)
        if data is None:
            if where == '404':
                unavail.add(i)
                man['unavailable'] = sorted(unavail)
                st['changed'] = True
            return None
        h = _sha(data)
        ent = clips.setdefault(i, {})
        if ent.get('sha256') and ent['sha256'] != h:
            sys.exit(f'录音 {i} 的内容和清单里记的不一样（{ent["sha256"][:12]} → {h[:12]}）。若是有意更换，请先从清单删掉这一条。')
        ent.update({'src': where, 'sha256': h})
        st['changed'] = True
        return data

    def process(i, data, dest):
        src = CACHE / 'tmp' / f'{i}.mp3'
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_bytes(data)
        _run(['-i', str(src), '-af', TRIM, *ENC], dest)

    def base_clip(c, net_ok):
        """轻声底本：本次已用的 > 项目库 > 种子库（只读，不复制进项目库）> 从来源现做到临时目录（也不进库）"""
        if c in out:
            return out[c]
        if (lib / f'{c}.mp3').exists():
            return lib / f'{c}.mp3'
        if seed and c in seed.names:
            return seed.path(c)
        if c not in tmp:
            data = raw(c, net_ok)
            if data is None:
                return None
            tmp[c] = CACHE / 'base' / f'{c}.mp3'
            tmp[c].parent.mkdir(parents=True, exist_ok=True)
            process(c, data, tmp[c])
        return tmp[c]

    normal = sorted(i for i in ids if not i.endswith('5'))
    for i in normal:
        f = existing(i, 'clips')
        if f is None:
            data = raw(i)
            if data is not None:
                f = lib / f'{i}.mp3'
                process(i, data, f)
                clips[i]['clip_sha256'] = _sha(f.read_bytes())
                st['generated'] += 1
        if f is None:
            missing.append(i)
            continue
        out[i], srcs[i] = f, clips.get(i, {}).get('src')
    for n in sorted(i for i in ids if i.endswith('5')):
        f = existing(n, 'neutral')
        if f is None:
            cands = [indiv[n]] if n in indiv else [f'{n[:-1]}{t}' for t in prefer]
            base = bclip = None
            for net_ok in (False, True):            # 先用本地已有的，实在没有再联网
                for c in cands:
                    bclip = base_clip(c, net_ok)
                    if bclip:
                        base = c
                        break
                if base:
                    break
            if base is None:
                missing.append(n)
                continue
            f = lib / f'{n}.mp3'
            _run(['-i', str(bclip), '-t', f'{NEUTRAL_LEN}', '-af', f'afade=t=out:st={NEUTRAL_LEN - NEUTRAL_FADE}:d={NEUTRAL_FADE},volume={NEUTRAL_GAIN}', *ENC], f)
            neu[n] = {'base': base, 'clip_sha256': _sha(f.read_bytes())}
            st['generated'] += 1
            st['changed'] = True
        out[n] = f
        neutral_map[n] = neu.get(n, {}).get('base')
    if st['changed']:
        man['_说明'] = NOTE
        man['upstream'] = {'repo': 'https://github.com/hugolpz/audio-cmn', 'revision': REV, 'url': UPSTREAM, 'license': 'CC-BY-SA-3.0', 'recordist': 'Chen Wang 王琛'}
        mpath.write_text(_dump(man), 'utf8')
    uris = {k: 'data:audio/mpeg;base64,' + base64.b64encode(v.read_bytes()).decode() for k, v in out.items()}
    report = {'ids': len(ids), 'clips': len(out), 'bytes': sum(v.stat().st_size for v in out.values()), 'missing': missing, 'neutral': neutral_map,
              'from_lib': st['from_lib'], 'from_seed': st['from_seed'], 'generated': st['generated']}
    return uris, report


def pack_seed(lib, manifest=None, out=SEED):
    """维护用：把一个录音库（目录里的 {id}.mp3 + 清单）打包成种子库 out/clips.zip + out/manifest.json（可重复生成：固定时间戳、按名字排序）"""
    lib, out = pathlib.Path(lib), pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(lib.glob('*.mp3'))
    with zipfile.ZipFile(out / 'clips.zip', 'w', zipfile.ZIP_STORED) as z:       # mp3 已经压缩过，不再压
        for f in files:
            z.writestr(zipfile.ZipInfo(f.name, (1980, 1, 1, 0, 0, 0)), f.read_bytes())
    mp = pathlib.Path(manifest) if manifest else lib / 'manifest.json'
    man = json.loads(mp.read_text('utf8'))
    man['_说明'] = NOTE
    (out / 'manifest.json').write_text(_dump(man), 'utf8')
    return len(files)


def _main(argv):
    def opt(name):
        if name in argv:
            i = argv.index(name)
            v = argv[i + 1]
            del argv[i:i + 2]
            return v
    pack, manifest = opt('--pack-seed'), opt('--manifest')
    if pack:
        print(f'已打包 {pack_seed(pack, manifest)} 条 → {SEED}')
        return
    lib, ids_arg, emit_json, emit_js, rules = opt('--lib'), opt('--ids'), opt('--emit-json'), opt('--emit-js'), opt('--rules')
    net = '--no-net' not in argv
    if not lib:
        sys.exit(__doc__)
    sys.path.insert(0, str(HERE))
    ids, neutral = set(), None
    if '--text' in argv:
        import pinyin_annotate as pa
        ann = pa.Annotator(rules)
        neutral = ann.neutral
        for f in argv[argv.index('--text') + 1:]:
            if f.startswith('--'):
                break
            for t in pa.load_paragraphs(f):
                ids.update(ann.annotate(t))
    if ids_arg:
        ids.update(x for x in ids_arg.split(',') if x)
    if not ids:
        sys.exit('没有读音 id：用 --ids zhang3,de5 或 --text FILE')
    uris, rep = build_clips(ids, lib, neutral=neutral, net=net)
    print(f"{rep['ids']} 种读音 → {rep['clips']} 条录音 {rep['bytes'] / 1e6:.2f} MB（项目库已有 {rep['from_lib']}，种子库复制 {rep['from_seed']}，新生成 {rep['generated']}，轻声模拟 {len(rep['neutral'])}）")
    if rep['missing']:
        print('缺录音（页面上只显示拼音）：' + ' '.join(rep['missing']))
    if emit_json:
        pathlib.Path(emit_json).write_text(json.dumps(uris, ensure_ascii=False), 'utf8')
    if emit_js:
        pathlib.Path(emit_js).write_text('window.__PYA=' + json.dumps(uris, ensure_ascii=False) + ';\n', 'utf8')


if __name__ == '__main__':
    _main(sys.argv[1:])
