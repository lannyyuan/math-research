#!/usr/bin/env python3
"""拼音发音音频（构建期）：全书用到的“音节+声调”，**同音只存一条**，不是一字一个文件。

录音库：webapp/pinyin_clips/{id}.mp3（id 如 zhang3、de5），已处理好、随仓库保存，构建时**优先直接用**——
有库就不需要 ffmpeg、也不需要 Pinyin_Drill 目录和网络。库里缺的才按下面的来源生成，并存进库（记得一起提交）。
来源（只在库里缺录音时才用，按顺序）：
  1. Pinyin_Drill_P0 的真人录音  <DRILL>/human-audio-downloads/audio/cmn-{id}.mp3   （环境变量 PINYIN_DRILL_DIR 可改目录；只读）
  2. 上游 hugolpz/audio-cmn（固定 revision）的同名录音，下载到 out/pinyin_audio/src/ 缓存（out/ 不进 git）
处理：裁掉首尾静音 → 单声道 22.05 kHz、32 kbps MP3（单条约 4 KB）→ 存库 → 构建时 base64 内联进网页。
webapp/pinyin_audio_manifest.json 记每个 id 的来源、原始 MP3 的 SHA-256、库里文件的 SHA-256：库文件被改动会报警。
轻声（5 声）没有录音：取该音节现成录音里“最接近低而短”的一声，截短到 0.30 s、尾部渐弱、降音量，模拟轻声（规则见 pinyin_overrides.json 的 neutral）。
想换掉某一条（比如换成真人录的轻声）：直接替换库里的文件，并从清单里删掉那一条的记录，再构建。

录音：Chen Wang 王琛（Wang Chen, Lopez Hugo, Vion Nicolas），CC-BY-SA-3.0，https://github.com/hugolpz/audio-cmn；署名与修改说明见 pinyin_clips/ATTRIBUTION.md
"""
import base64, hashlib, json, os, pathlib, shutil, subprocess, sys, urllib.request, urllib.error

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DRILL = pathlib.Path(os.environ.get('PINYIN_DRILL_DIR', 'D:/Users/lanny/playground/KunKun-study/Pinyin_Drill_P0'))
REV = 'ff9ed3d0c631195bd2c06f39450f3264c7124040'
UPSTREAM = 'https://raw.githubusercontent.com/hugolpz/audio-cmn/{rev}/64k/syllabs/cmn-{id}.mp3'
CACHE = ROOT / 'out' / 'pinyin_audio'
LIB = HERE / 'pinyin_clips'
MANIFEST = HERE / 'pinyin_audio_manifest.json'
VER = 'v1'      # 处理参数变了就改这里，缓存会失效

TRIM = ('silenceremove=start_periods=1:start_silence=0.03:start_threshold=-42dB,areverse,'
        'silenceremove=start_periods=1:start_silence=0.05:start_threshold=-42dB,areverse,'
        'afade=t=in:d=0.006,areverse,afade=t=in:d=0.04,areverse')
ENC = ['-ac', '1', '-ar', '22050', '-c:a', 'libmp3lame', '-b:a', '32k']
NEUTRAL_LEN, NEUTRAL_FADE, NEUTRAL_GAIN = 0.30, 0.13, 0.85
NOTE = ('构建拼音发音用到的录音清单。clips：音节 id → 来源(drill=Pinyin_Drill_P0，upstream=hugolpz/audio-cmn，manual=手工放入) '
        '+ 原始 MP3 的 SHA-256(sha256) + 处理后存在 pinyin_clips/ 里的文件的 SHA-256(clip_sha256)；neutral：模拟的轻声 id → 底本音节 + 库文件的 SHA-256。')


def _ffmpeg():
    exe = shutil.which('ffmpeg')
    if not exe:
        sys.exit('找不到 ffmpeg（库 pinyin_clips/ 里缺录音，需要它来裁剪/转码）。请把 ffmpeg 放进 PATH，或把缺的 mp3 补进库，或用 --no-pinyin 构建不带发音的版本。')
    return exe


def _run(args):
    """最后一个参数是输出文件：先写 .part 再换名，中途失败不会留下半截文件（缓存里的半截文件会被当成好的，最后进到库里）"""
    dest = pathlib.Path(args[-1])
    part = dest.with_name(dest.name + '.part')
    try:
        subprocess.run([_ffmpeg(), '-y', '-loglevel', 'error', *args[:-1], '-f', 'mp3', str(part)], check=True)
        os.replace(part, dest)
    finally:
        part.unlink(missing_ok=True)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _source(i: str, man: dict, log, net=True):
    """→ (bytes, 'drill'|'upstream') 或 (None, None)；上游明确没有（404）时 → (None, '404')；net=False 时只看本地（Drill 目录和缓存）"""
    f = DRILL / 'human-audio-downloads' / 'audio' / f'cmn-{i}.mp3'
    if f.exists():
        return f.read_bytes(), 'drill'
    c = CACHE / 'src' / f'cmn-{i}.mp3'
    if c.exists():
        return c.read_bytes(), 'upstream'
    if not net:
        return None, None
    try:
        req = urllib.request.Request(UPSTREAM.format(rev=REV, id=i), headers={'User-Agent': 'xiaoshihou-book-build'})
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


def _clip(i: str, src: bytes) -> pathlib.Path:
    out = CACHE / 'clip' / f'{i}-{_sha(src)[:8]}-{VER}.mp3'
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE / 'tmp' / f'{i}.mp3'
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(src)
        _run(['-i', str(tmp), '-af', TRIM, *ENC, str(out)])
    return out


def _neutral_clip(i: str, base_id: str, base_clip: pathlib.Path) -> pathlib.Path:
    out = CACHE / 'clip' / f'{i}-{base_id}-{_sha(base_clip.read_bytes())[:8]}-{VER}.mp3'
    if not out.exists():
        _run(['-i', str(base_clip), '-t', f'{NEUTRAL_LEN}',
              '-af', f'afade=t=out:st={NEUTRAL_LEN - NEUTRAL_FADE}:d={NEUTRAL_FADE},volume={NEUTRAL_GAIN}', *ENC, str(out)])
    return out


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


def build(ids, neutral_spec, log=print):
    """ids：全书用到的拼音 id 集合（zhang3、de5…）。→ (clips {id: dataURI}, report)"""
    man = json.loads(MANIFEST.read_text('utf8')) if MANIFEST.exists() else {}
    man_clips = man.setdefault('clips', {})
    man_neu = man.setdefault('neutral', {})
    unavail = set(man.get('unavailable', []))
    normal = sorted(i for i in ids if not i.endswith('5'))
    neutral = sorted(i for i in ids if i.endswith('5'))
    prefer = neutral_spec.get('prefer', [3, 4, 2, 1])
    indiv = neutral_spec.get('individual', {})
    out, srcs, missing, neutral_map = {}, {}, [], {}
    made = {}                      # 本次从来源现做的片（含只用来做轻声底本的）
    changed = False
    generated = 0

    def in_lib(i, entry):
        """库里有这条就用它（并核对清单里的 SHA-256；清单里没记就收编）。→ Path | None"""
        nonlocal changed
        f = LIB / f'{i}.mp3'
        if not f.exists():
            return None
        h = _sha(f.read_bytes())
        old = entry.get('clip_sha256')
        if old and old != h:
            sys.exit(f'库里的 pinyin_clips/{i}.mp3 和清单里记的不一样（{old[:12]} → {h[:12]}）。若是有意更换，请先从 pinyin_audio_manifest.json 删掉 {i} 的记录。')
        if not old:
            entry['clip_sha256'] = h
            entry.setdefault('src', 'manual')
            changed = True
        return f

    def store(i, produced: pathlib.Path, entry):
        """把现做的片存进库，记 SHA-256"""
        nonlocal changed, generated
        LIB.mkdir(exist_ok=True)
        dst = LIB / f'{i}.mp3'
        shutil.copyfile(produced, dst)
        entry['clip_sha256'] = _sha(dst.read_bytes())
        changed = True
        generated += 1
        return dst

    def get(i, net=True):
        """从来源取一条录音并处理成片（放 out/ 缓存）；记进清单（原始内容变了就报警）。→ 成功与否"""
        nonlocal changed
        if i in made:
            return True
        if i in unavail:
            return False
        data, where = _source(i, man, log, net)
        if data is None:
            if where == '404':                     # 上游确实没有：记下来，以后不再联网去问
                unavail.add(i)
                man['unavailable'] = sorted(unavail)
                changed = True
            return False
        h = _sha(data)
        old = man_clips.get(i)
        if old and old.get('sha256') and old['sha256'] != h:
            sys.exit(f'录音 {i} 的内容和清单里记的不一样（{old["sha256"][:12]} → {h[:12]}）。若是有意更换，请先从 pinyin_audio_manifest.json 删掉这一条。')
        if not old or not old.get('sha256'):
            man_clips.setdefault(i, {}).update({'src': where, 'sha256': h})
            changed = True
        made[i] = _clip(i, data)
        return True

    for i in normal:
        entry = man_clips.get(i, {})
        f = in_lib(i, entry)
        if f is None and get(i):
            entry = man_clips[i]
            f = store(i, made[i], entry)
        if f is None:
            missing.append(i)
            continue
        man_clips[i] = entry
        out[i], srcs[i] = f, entry.get('src')
    def base_clip(c, net):
        """轻声底本：全书已有的这条 > 库里的 > 从来源现做"""
        if c in out:
            return out[c]
        if (LIB / f'{c}.mp3').exists():
            return LIB / f'{c}.mp3'
        return made[c] if get(c, net) else None

    for n in neutral:
        entry = man_neu.get(n, {})
        f = in_lib(n, entry)
        if f is None:
            syl = n[:-1]
            cands = [indiv[n]] if n in indiv else [f'{syl}{t}' for t in prefer]
            # 先看本地已有的（库、Drill 目录、缓存），都没有再联网
            base = bc = None
            for net in (False, True):
                base = next((c for c in cands if base_clip(c, net)), None)
                if base:
                    bc = base_clip(base, net)
                    break
            if base is None:
                missing.append(n)
                continue
            f = store(n, _neutral_clip(n, base, bc), entry)
            entry['base'] = base
        man_neu[n] = entry
        out[n] = f
        neutral_map[n] = entry.get('base')
    if changed:
        man['_说明'] = NOTE
        man['upstream'] = {'repo': 'https://github.com/hugolpz/audio-cmn', 'revision': REV, 'url': UPSTREAM, 'license': 'CC-BY-SA-3.0', 'recordist': 'Chen Wang 王琛'}
        MANIFEST.write_text(_dump(man), 'utf8')
        log('  已更新 pinyin_audio_manifest.json' + (f'，并新增 {generated} 条到 pinyin_clips/（记得一起提交）' if generated else ''))
    uri = {k: 'data:audio/mpeg;base64,' + base64.b64encode(v.read_bytes()).decode() for k, v in out.items()}
    size = sum(v.stat().st_size for v in out.values())
    report = {'clips': len(out), 'bytes': size, 'missing': missing, 'neutral': neutral_map, 'generated': generated,
              'from_drill': sum(1 for k in out if srcs.get(k) == 'drill'), 'from_upstream': sum(1 for k in out if srcs.get(k) == 'upstream')}
    return uri, report
