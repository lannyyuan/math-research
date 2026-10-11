#!/usr/bin/env python3
"""拼音发音音频（构建期）：全书用到的“音节+声调”，**同音只打包一条**，不是一字一个文件。

来源（按顺序）：
  1. Pinyin_Drill_P0 的真人录音  <DRILL>/human-audio-downloads/audio/cmn-{id}.mp3   （环境变量 PINYIN_DRILL_DIR 可改目录；只读，不修改它）
  2. 上游 hugolpz/audio-cmn（固定 revision）的同名录音，下载到 out/pinyin_audio/src/ 缓存（out/ 不进 git）
处理：裁掉首尾静音 → 单声道 22.05 kHz、32 kbps MP3（单条约 4 KB）→ base64 内联进网页。仓库里**不存任何音频文件**，只存
webapp/pinyin_audio_manifest.json（音节 id → 来源 + SHA-256），保证别的机器上能复现、且换了文件会报警。
轻声（5 声）没有录音：取该音节现成录音里“最接近低而短”的一声，截短到 0.30 s、尾部渐弱、降音量，模拟轻声（规则见 pinyin_overrides.json 的 neutral）。

录音：Chen Wang 王琛（Wang Chen, Lopez Hugo, Vion Nicolas），CC-BY-SA-3.0，https://github.com/hugolpz/audio-cmn
"""
import base64, hashlib, json, os, pathlib, shutil, subprocess, sys, urllib.request, urllib.error

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DRILL = pathlib.Path(os.environ.get('PINYIN_DRILL_DIR', 'D:/Users/lanny/playground/KunKun-study/Pinyin_Drill_P0'))
REV = 'ff9ed3d0c631195bd2c06f39450f3264c7124040'
UPSTREAM = 'https://raw.githubusercontent.com/hugolpz/audio-cmn/{rev}/64k/syllabs/cmn-{id}.mp3'
CACHE = ROOT / 'out' / 'pinyin_audio'
MANIFEST = HERE / 'pinyin_audio_manifest.json'
VER = 'v1'      # 处理参数变了就改这里，缓存会失效

TRIM = ('silenceremove=start_periods=1:start_silence=0.03:start_threshold=-42dB,areverse,'
        'silenceremove=start_periods=1:start_silence=0.05:start_threshold=-42dB,areverse,'
        'afade=t=in:d=0.006,areverse,afade=t=in:d=0.04,areverse')
ENC = ['-ac', '1', '-ar', '22050', '-c:a', 'libmp3lame', '-b:a', '32k']
NEUTRAL_LEN, NEUTRAL_FADE, NEUTRAL_GAIN = 0.30, 0.13, 0.85


def _ffmpeg():
    exe = shutil.which('ffmpeg')
    if not exe:
        sys.exit('找不到 ffmpeg（拼音发音需要它来裁剪/转码）。请把 ffmpeg 放进 PATH，或用 --no-pinyin 构建不带发音的版本。')
    return exe


def _run(args):
    subprocess.run([_ffmpeg(), '-y', '-loglevel', 'error', *args], check=True)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _source(i: str, man: dict, log, net=True):
    """→ (bytes, 'drill'|'upstream') 或 (None, None)；net=False 时只看本地（Drill 目录和缓存）"""
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


def build(ids, neutral_spec, log=print):
    """ids：全书用到的拼音 id 集合（zhang3、de5…）。→ (clips {id: dataURI}, report)"""
    man = json.loads(MANIFEST.read_text('utf8')) if MANIFEST.exists() else {'clips': {}}
    man_clips = man.setdefault('clips', {})
    normal = sorted(i for i in ids if not i.endswith('5'))
    neutral = sorted(i for i in ids if i.endswith('5'))
    prefer = neutral_spec.get('prefer', [3, 4, 2, 1])
    indiv = neutral_spec.get('individual', {})
    clips, srcs, missing, changed = {}, {}, [], False
    made = {}

    def get(i, net=True):
        """取一条录音并处理成片；记进清单（内容变了就报警）。→ 成功与否"""
        nonlocal changed
        if i in made:
            return True
        data, where = _source(i, man, log, net)
        if data is None:
            return False
        h = _sha(data)
        old = man_clips.get(i)
        if old and old['sha256'] != h:
            sys.exit(f'录音 {i} 的内容和清单里记的不一样（{old["sha256"][:12]} → {h[:12]}）。若是有意更换，请先从 pinyin_audio_manifest.json 删掉这一条。')
        if not old:
            man_clips[i] = {'sha256': h, 'src': where}
            changed = True
        made[i] = _clip(i, data)
        srcs[i] = where
        return True

    for i in normal:
        get(i)
    base_of = {}
    for n in neutral:
        syl = n[:-1]
        cands = [indiv[n]] if n in indiv else [f'{syl}{t}' for t in prefer]
        # 先看本地已有的（Drill 目录/缓存），都没有再联网
        base = next((c for c in cands if get(c, net=False)), None) or next((c for c in cands if get(c, net=True)), None)
        base_of[n] = base
    out = {}
    for i in normal:
        if i in made:
            out[i] = made[i]
        else:
            missing.append(i)
    neutral_map = {}
    for n in neutral:
        base = base_of.get(n)
        if base is None or base not in made:
            missing.append(n)
            continue
        out[n] = _neutral_clip(n, base, made[base])
        neutral_map[n] = base
    if changed:
        man['_说明'] = '构建拼音发音用到的真人录音清单：音节 id → 来源(drill=Pinyin_Drill_P0，upstream=hugolpz/audio-cmn) + 原始 MP3 的 SHA-256。录音本身不进仓库。'
        man['upstream'] = {'repo': 'https://github.com/hugolpz/audio-cmn', 'revision': REV, 'url': UPSTREAM, 'license': 'CC-BY-SA-3.0', 'recordist': 'Chen Wang 王琛'}
        man['clips'] = dict(sorted(man_clips.items()))
        MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=1) + '\n', 'utf8')
        log('  已更新 pinyin_audio_manifest.json')
    uri = {k: 'data:audio/mpeg;base64,' + base64.b64encode(v.read_bytes()).decode() for k, v in out.items()}
    size = sum(v.stat().st_size for v in out.values())
    report = {'clips': len(out), 'bytes': size, 'missing': missing, 'neutral': neutral_map,
              'from_drill': sum(1 for k in out if srcs.get(k) == 'drill'), 'from_upstream': sum(1 for k in out if srcs.get(k) == 'upstream')}
    return uri, report
