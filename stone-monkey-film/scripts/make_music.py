#!/usr/bin/env python3
"""配乐（自己合成，无外部素材、无版权问题）：古筝、箫、木鱼、风铃、铜铃、鼓。
安静、留白多；D 宫五声音阶（D E F# A B）。“灯”的动机 D–F#–A–B–A 出现在片头、灯亮、尾声。
第五部的鼓声（“咚——”）和第六部灯亮的那一刻最强。
全部事件的时间都从 src/timeline.json 的字幕排程算出来（和 src/schedule.mjs 同一套规则），
场景里的动作（裂开、鼓响、灯亮……）用同样的“某条字幕 + 偏移”来定，所以改了时间线重跑一遍就对得上。
输出 public/audio/score.wav（44.1 kHz 立体声），纯 numpy + scipy。"""
import json, math, pathlib
import numpy as np
import wave
from scipy.signal import fftconvolve

SR = 44100
ROOT = pathlib.Path(__file__).resolve().parent.parent
tl = json.loads((ROOT / 'src/timeline.json').read_text())
FPS = tl['fps']

# ───────── 时间线：场景起点 + 每条字幕的出现时间（和 schedule.mjs 一致） ─────────
SC, CUE = {}, {}
s = 0.0
for sc in tl['scenes']:
    key = sc['id'].split('-')[0]
    SC[key] = s
    t = sc.get('lead', 1.5)
    cues = []
    for i, c in enumerate(sc['cues']):
        txt = ''.join(c['text'].split())
        d = c.get('d') or round(1.5 + 0.3 * len(txt) + 0.2, 2)
        if i > 0:
            t += c.get('gap', 0.5)
        if 'at' in c:
            t = c['at']
        cues.append((s + t, d))
        t += d
    CUE[key] = cues
    s += sc['len']
TOTAL = s
N = int(TOTAL * SR)
rng = np.random.default_rng(11)
DL = np.zeros(N, np.float32); DR = np.zeros(N, np.float32)      # 干声
WL = np.zeros(N, np.float32); WR = np.zeros(N, np.float32)      # 进混响的声音

NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hz(name):
    n = NOTE[name[0]]
    i = 1
    if name[i] == '#': n += 1; i += 1
    elif name[i] == 'b': n -= 1; i += 1
    return 440.0 * 2 ** ((n - 9 + (int(name[i:]) - 4) * 12) / 12)


def put(sig, t0, pan=0.5, gain=1.0, wet=0.3):
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0:
        return
    a, b = max(i0, 0), min(i0 + len(sig), N)
    seg = sig[a - i0:b - i0] * gain
    cl, cr = math.cos(pan * math.pi / 2), math.sin(pan * math.pi / 2)
    DL[a:b] += seg * cl * (1 - wet * 0.5); DR[a:b] += seg * cr * (1 - wet * 0.5)
    WL[a:b] += seg * cl * wet; WR[a:b] += seg * cr * wet


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def lp(x, fc):
    """一阶低通（向量化的分块递推）"""
    a = math.exp(-2 * math.pi * fc / SR)
    out = np.empty_like(x)
    y = 0.0
    blk = 4096
    for i in range(0, len(x), blk):
        seg = x[i:i + blk].astype(np.float64)
        n = len(seg)
        w = a ** np.arange(n, dtype=np.float64)
        c = np.convolve(seg, w)[:n] * (1 - a)
        out[i:i + n] = (c + (a ** (np.arange(n) + 1)) * y).astype(np.float32)
        y = float(out[i + n - 1])
    return out


def noise(dur, lo=200, hi=1200, amp=0.05):
    x = rng.standard_normal(int(dur * SR)).astype(np.float32)
    y = lp(x, hi) - lp(x, lo)
    y /= (np.abs(y).max() + 1e-9)
    return (y * amp).astype(np.float32)


def env_shape(sig, pts):
    t = np.arange(len(sig)) / SR
    ts, gs = zip(*pts)
    return (sig * np.interp(t, ts, gs)).astype(np.float32)


# ───────── 乐器 ─────────
def zheng(f, dur=3.2, amp=0.17, bend=0.0, bright=1.0):
    """古筝：拨弦，起音亮、有一点上滑（按音），谐波快速衰减。"""
    t = tt(dur)
    glide = 1 - bend * np.exp(-t * 28)       # 起音时从低半音左右滑上来
    ph = 2 * math.pi * np.cumsum(f * glide) / SR
    out = np.zeros_like(t)
    for k, (m, a, d) in enumerate([(1, 1.0, 1.5), (2, 0.55, 2.2), (3, 0.34, 3.2), (4, 0.2, 4.6), (5, 0.12, 6.0), (6, 0.07, 8.0)]):
        out += a * (bright if m > 2 else 1.0) * np.sin(ph * m + 0.4 * k) * np.exp(-t * d)
    click = rng.standard_normal(len(t)).astype(np.float32) * np.exp(-t * 90) * 0.12
    out = out + click
    out *= np.minimum(t / 0.003, 1)
    return (out * amp).astype(np.float32)


def xiao(f, dur=4.0, amp=0.11, vib=0.0045, breath=0.35, att=0.28, rel=0.8):
    """箫：气声很重的柔和长音，轻微的颤音。"""
    t = tt(dur)
    vibr = 1 + vib * np.sin(2 * math.pi * 4.8 * t) * np.minimum(t / 0.9, 1)
    ph = 2 * math.pi * np.cumsum(f * vibr) / SR
    out = np.sin(ph) + 0.18 * np.sin(2 * ph + 0.5) + 0.07 * np.sin(3 * ph + 1.0)
    nz = noise(dur, f * 1.5, f * 4.5, 1.0)
    out = out + breath * nz * (0.5 + 0.5 * np.minimum(t / 0.4, 1))
    env = np.minimum(t / att, 1) * np.minimum((dur - t) / rel, 1)
    return (out * np.clip(env, 0, 1) ** 1.3 * amp).astype(np.float32)


def muyu(amp=0.16, f=720.0):
    """木鱼：短促的木头声。"""
    t = tt(0.22)
    out = np.sin(2 * math.pi * f * t) * np.exp(-t * 38) + 0.5 * np.sin(2 * math.pi * f * 1.62 * t) * np.exp(-t * 55)
    out += rng.standard_normal(len(t)).astype(np.float32) * np.exp(-t * 160) * 0.3
    out *= np.minimum(t / 0.001, 1)
    return (out * amp).astype(np.float32)


def chime(f, dur=3.0, amp=0.05):
    """风铃：高而细的金属声，非整数倍的泛音。"""
    t = tt(dur)
    out = np.zeros_like(t)
    for m, a, d in [(1, 1.0, 1.7), (2.76, 0.4, 2.8), (5.4, 0.18, 5.0), (8.93, 0.07, 8.0)]:
        out += a * np.sin(2 * math.pi * f * m * t) * np.exp(-t * d)
    out *= np.minimum(t / 0.002, 1)
    return (out * amp).astype(np.float32)


def tinkle(t0, n=8, span=1.4, f0=1800.0, amp=0.04, pan0=0.3):
    for k in range(n):
        f = f0 * [1, 1.125, 1.335, 1.5, 1.68, 2.0][int(rng.integers(0, 6))] * (1 + 0.003 * rng.standard_normal())
        put(chime(f, 2.0, amp * rng.uniform(0.6, 1.0)), t0 + span * rng.random(), pan0 + 0.4 * rng.random(), wet=0.5)


def rbell(f=523.0, dur=5.0, amp=0.2):
    """铜铃（雪铃）：“当——”，温厚的金属声。"""
    t = tt(dur)
    out = np.zeros_like(t)
    for m, a, d in [(1, 1.0, 0.9), (2.0, 0.55, 1.4), (2.4, 0.3, 1.8), (3.0, 0.22, 2.3), (4.2, 0.12, 3.4), (5.9, 0.06, 5.0)]:
        out += a * np.sin(2 * math.pi * f * m * t + m) * np.exp(-t * d)
    out *= np.minimum(t / 0.002, 1)
    return (out * amp).astype(np.float32)


def drum(amp=0.9, dur=5.0):
    """大鼓：“咚——”。低频的鼓皮 + 一声闷响 + 长长的余音。"""
    t = tt(dur)
    f = 62 + 40 * np.exp(-t * 14)
    ph = 2 * math.pi * np.cumsum(f) / SR
    out = np.sin(ph) * np.exp(-t * 1.5) + 0.5 * np.sin(ph * 1.5 + 0.3) * np.exp(-t * 2.2) + 0.28 * np.sin(2 * math.pi * 190 * t) * np.exp(-t * 4.5)
    out += lp(rng.standard_normal(len(t)).astype(np.float32), 600) * np.exp(-t * 18) * 2.0
    out *= np.minimum(t / 0.004, 1)
    return (out * amp).astype(np.float32)


def thump(amp=0.2):
    """心跳 / 轻轻的低鼓。"""
    t = tt(0.4)
    f = 54 + 30 * np.exp(-t * 20)
    out = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return (out * amp).astype(np.float32)


def pad(f, dur, amp=0.06, att=2.0, rel=2.5, det=0.004):
    t = tt(dur)
    out = (np.sin(2 * math.pi * f * (1 + det) * t) + np.sin(2 * math.pi * f * (1 - det) * t + 1.1) + 0.3 * np.sin(2 * math.pi * f * 2 * t + 0.4)) / 2.3
    env = np.minimum(t / att, 1) * np.minimum((dur - t) / rel, 1)
    return (out * np.clip(env, 0, 1) ** 1.5 * amp).astype(np.float32)


def chord(names, t0, dur, amp=0.05, **kw):
    for k, nm in enumerate(names):
        put(pad(hz(nm), dur, amp=amp, **kw), t0, 0.5 + 0.22 * math.sin(k * 1.7), wet=0.4)


def bird(t0, f0=3200, amp=0.03, n=3, pan=0.5):
    for k in range(n):
        d = 0.09
        t = tt(d)
        f = f0 * (1 + 0.25 * rng.random()) * (1 + 0.35 * np.sin(math.pi * t / d))
        s_ = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.sin(math.pi * t / d) ** 1.5
        put(s_.astype(np.float32) * amp, t0 + k * 0.14 + 0.03 * rng.random(), pan, wet=0.3)


def water_bed(t0, dur, amp=0.03):
    n = noise(dur, 300, 2400, 1.0)
    n = n * (0.7 + 0.3 * np.sin(2 * math.pi * 0.31 * tt(dur) + 1.0))
    put(env_shape(n, [(0, 0), (1.5, 1), (dur - 1.5, 1), (dur, 0)]) * amp, t0, 0.5, wet=0.2)


def wind(t0, dur, amp=0.03, lo=120, hi=900):
    n = noise(dur, lo, hi, 1.0)
    n = n * (0.6 + 0.4 * np.sin(2 * math.pi * 0.11 * tt(dur) + 2.0))
    put(env_shape(n, [(0, 0), (min(2.0, dur / 3), 1), (dur - min(2.5, dur / 3), 1), (dur, 0)]) * amp, t0, 0.5, wet=0.15)


def rumble(t0, dur, amp=0.05):
    n = noise(dur, 25, 160, 1.0)
    put(env_shape(n, [(0, 0), (dur * 0.2, 1), (dur * 0.8, 0.8), (dur, 0)]) * amp, t0, 0.5, wet=0.1)


def crackle(t0, dur, amp=0.05, rate=14):
    for _ in range(int(dur * rate)):
        t = tt(0.03)
        s_ = rng.standard_normal(len(t)).astype(np.float32) * np.exp(-t * 160)
        put(s_ * amp * rng.uniform(0.3, 1.0), t0 + rng.random() * dur, 0.4 + 0.2 * rng.random(), wet=0.1)


# ───────── 音阶 / 动机 ─────────
PENT = ['D', 'E', 'F#', 'A', 'B']


def pent(i, octv=4):
    """五声音阶上的第 i 个音（i 可以为负或大于 4，自动跨八度）"""
    o = octv + i // 5
    return PENT[i % 5] + str(o)


MOTIF = ['D5', 'F#5', 'A5', 'B5', 'A5']


def motif(t0, step=0.7, amp=0.16, octave_shift=0, pan=0.5, bend=0.12):
    for k, nm in enumerate(MOTIF):
        f = hz(nm) * (2 ** octave_shift)
        put(zheng(f, 3.2, amp * (0.9 + 0.1 * (k == 2)), bend=bend), t0 + k * step, pan, wet=0.35)


def walk_pent(t0, dur, step, start=0, octv=4, amp=0.13, seed=0, pan=0.5, bend=0.08, drift=0.55):
    """在五声音阶上缓缓游走的古筝（随机游走 + 偏向上行/下行）。"""
    r = np.random.default_rng(seed)
    i = start
    t = t0
    while t < t0 + dur:
        put(zheng(hz(pent(i, octv)), 3.0, amp * r.uniform(0.75, 1.0), bend=bend), t, pan + 0.15 * math.sin(t), wet=0.35)
        i += int(r.choice([-2, -1, -1, 1, 1, 2], p=[0.1, 0.25, 0.15, 0.25, 0.15, 0.1]))
        i = max(-3, min(i, 7))
        t += step * r.choice([1, 1, 1, 1.5, 2])


def arp(t0, notes, step, amp=0.15, pan=0.5, bend=0.08, dur=3.0):
    for k, nm in enumerate(notes):
        put(zheng(hz(nm), dur, amp, bend=bend), t0 + k * step, pan + 0.1 * math.sin(k), wet=0.35)


def ev(sc, i, off=0.0):
    return CUE[sc][i][0] + off


S0, S1, S2, S3, S4, S5, S6, S7 = (SC[k] for k in ('s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7'))

# ═════════════ 片头：灰色的灯，墨里显出片名 ═════════════
chord(['D2', 'A2'], S0, 10.5, amp=0.06, att=3.0, rel=2.5)
put(chime(2349.0, 4.0, 0.05), S0 + 0.9, 0.7, wet=0.6)
put(zheng(hz('A4'), 4, 0.1, bend=0.1), S0 + 1.6, 0.4, wet=0.5)
put(xiao(hz('A4'), 6.5, amp=0.1, att=2.2, rel=1.6), S0 + 2.2, 0.5, wet=0.5)
put(zheng(hz('F#4'), 4, 0.1, bend=0.1), S0 + 4.2, 0.55, wet=0.5)
put(zheng(hz('D5'), 4, 0.09, bend=0.1), S0 + 6.4, 0.45, wet=0.55)
put(chime(2793.0, 4.0, 0.04), S0 + 7.1, 0.3, wet=0.6)

# ═════════════ 第一部 天黑了 ═════════════
# 白天：古筝缓缓游走 + 箫的长音
walk_pent(S1 + 0.8, 11.0, 0.82, start=1, octv=4, amp=0.13, seed=1)
put(xiao(hz('F#4'), 5.2, amp=0.09, att=1.2), S1 + 1.6, 0.5, wet=0.5)
put(xiao(hz('A4'), 5.2, amp=0.09, att=1.2), S1 + 6.8, 0.5, wet=0.5)
# 灯灭：古筝一串下行的琶音，然后什么都没有了
lampout = S1 + 11.4
arp(lampout, ['D6', 'B5', 'A5', 'F#5', 'E5', 'D5', 'B4', 'A4', 'F#4', 'D4'], 0.2, amp=0.12, dur=2.5, bend=0.0)
chord(['D2', 'A2'], S1 + 12.0, 18.0, amp=0.05, att=2.5, rel=2.5)
wind(S1 + 13.5, 24.0, amp=0.035)
# 夜里：稀疏的低音；奶奶：一声低低的箫
for k, tt_ in enumerate([16.0, 20.5, 24.8]):
    put(zheng(hz(['D3', 'A3', 'F#3'][k]), 4.0, 0.12, bend=0.06), S1 + tt_, 0.4, wet=0.5)
put(xiao(hz('E4'), 5.0, amp=0.08, att=0.8), ev('s1', 3, 1.5), 0.55, wet=0.5)
# 石头说话：心跳
for k in range(7):
    put(thump(0.22), ev('s1', 4, 0.2) + k * 1.0, 0.5, wet=0.2)
put(xiao(hz('D4'), 5.0, amp=0.07, att=0.9), ev('s1', 4, 0.4), 0.45, wet=0.55)
# 裂开：细碎的咔咔声，然后“叮”的一声，龟甲蹦出来
t_crack, t_burst = ev('s1', 5, 1.6), ev('s1', 5, 3.4)
crackle(t_crack, t_burst - t_crack, amp=0.06, rate=9)
put(rbell(hz('A5'), 4.0, 0.14), t_burst, 0.5, wet=0.5)
tinkle(t_burst + 0.1, n=9, span=1.6, f0=1900, amp=0.05)
arp(t_burst + 0.5, ['E6', 'F#6', 'A6', 'F#6', 'E6'], 0.12, amp=0.08, dur=1.8, bend=0.0)
chord(['D3', 'A3', 'F#4'], ev('s1', 6, -0.5), 8.0, amp=0.045, att=1.5, rel=3.0)
walk_pent(ev('s1', 6, 0.5), 5.0, 0.9, start=2, octv=4, amp=0.1, seed=3)

# ═════════════ 第二部 河边搭桥 ═════════════
chord(['D3', 'A3'], S2 + 0.2, 7.5, amp=0.05, att=1.2, rel=1.5)
put(xiao(hz('F#4'), 6.0, amp=0.08, att=1.0), S2 + 1.0, 0.5, wet=0.5)
arp(S2 + 3.5, ['D4', 'F#4', 'A4', 'B4'], 0.55, amp=0.1)
# 走路：木鱼
t = S2 + 8.0
while t < S2 + 21.0:
    put(muyu(0.1), t, 0.5, wet=0.2)
    t += 0.62
walk_pent(S2 + 8.0, 12.0, 0.9, start=0, octv=4, amp=0.1, seed=5)
water_bed(S2 + 13.0, 27.0, amp=0.05)
put(xiao(hz('E4'), 5.0, amp=0.07, att=1.0), ev('s2', 2, 0.5), 0.5, wet=0.55)
# 搭桥：有节奏的木鱼
t = ev('s2', 3, 0.0)
while t < ev('s2', 3, 6.5):
    put(muyu(0.14, 640), t, 0.45, wet=0.2)
    put(muyu(0.09, 860), t + 0.25, 0.55, wet=0.2)
    t += 0.5
arp(ev('s2', 3, 0.0), ['D4', 'A3', 'D4', 'F#4', 'A4', 'F#4'], 1.0, amp=0.09)
# 水底一双大眼：低低的箫 + 风铃
put(xiao(hz('D3'), 7.0, amp=0.1, att=1.8, rel=1.6), ev('s2', 4, 0.0), 0.5, wet=0.6)
tinkle(ev('s2', 4, 1.0), n=4, span=3.0, f0=1500, amp=0.03)
# 鱼跃起、送鳞片
put((noise(0.8, 300, 3000, 1.0) * np.exp(-tt(0.8) * 4.5)).astype(np.float32) * 0.2, ev('s2', 5, -1.4), 0.5, wet=0.3)
arp(ev('s2', 5, -1.0), ['F#5', 'A5', 'B5', 'D6'], 0.16, amp=0.1, dur=2.5, bend=0.0)
tinkle(ev('s2', 5, -0.8), n=10, span=2.4, f0=2000, amp=0.045)
chord(['D3', 'A3', 'F#4'], ev('s2', 5, 0.0), 8.0, amp=0.05, att=1.5, rel=2.5)

# ═════════════ 第三部 海底的珍珠 ═════════════
wind(S3 + 0.0, 12.0, amp=0.03, lo=80, hi=500)
water_bed(S3 + 0.5, 11.0, amp=0.05)
put(xiao(hz('A3'), 6.0, amp=0.08, att=1.5), S3 + 1.0, 0.5, wet=0.55)
# 水分开：一阵由低到高的轻轻的扫音
sweep = (noise(2.6, 400, 4000, 1.0) * np.sin(math.pi * tt(2.6) / 2.6) ** 2).astype(np.float32)
put(sweep * 0.12, ev('s3', 0, 2.5), 0.5, wet=0.4)
# 海底：混响很深的钟声，慢
for k, nm in enumerate(['A4', 'F#4', 'D4', 'E4', 'A4', 'B4']):
    put(chime(hz(nm) * 2, 4.0, 0.08), ev('s3', 1, -1.0) + k * 1.3, 0.3 + 0.4 * (k % 2), wet=0.7)
chord(['D2', 'A2', 'D3'], ev('s3', 1, -1.0), 20.0, amp=0.06, att=3.0, rel=3.0)
# 老龙：低沉的箫
put(xiao(hz('D3'), 8.0, amp=0.13, att=2.2, rel=1.8, breath=0.45), ev('s3', 2, -0.3), 0.5, wet=0.6)
# 撬石头：低低的木鱼敲击 + 水泡
for k in range(6):
    put(muyu(0.12, 520), ev('s3', 3, 1.0) + k * 0.75, 0.5, wet=0.3)
for k in range(14):
    f = 500 + 900 * rng.random()
    tb = tt(0.12)
    put((np.sin(2 * math.pi * f * tb * (1 + 1.5 * tb / 0.12)) * np.exp(-tb * 30) * 0.05).astype(np.float32), ev('s3', 3, 2.0) + rng.random() * 6, 0.3 + 0.4 * rng.random(), wet=0.4)
t_roll = ev('s3', 3, 5.2)
put(env_shape(noise(3.5, 100, 1500, 1.0), [(0, 0), (0.4, 1), (3.5, 0)]) * 0.12, t_roll, 0.5, wet=0.3)    # 清水涌出
put(rbell(hz('D5'), 4.0, 0.08), t_roll, 0.5, wet=0.5)
arp(t_roll + 0.4, ['D5', 'F#5', 'A5', 'B5', 'A5'], 0.22, amp=0.09, dur=2.5)
# 宝珠：玻璃一样的音，慢慢亮起来
t_pearl = ev('s3', 4, 1.2)
pearl_tone = sum(a * np.sin(2 * math.pi * f * tt(9.0)) for f, a in [(880, 1.0), (1320, 0.5), (1760, 0.35), (2640, 0.15)]) / 2.0
put(env_shape(pearl_tone.astype(np.float32), [(0, 0), (1.8, 1), (6.5, 0.8), (9.0, 0)]) * 0.06, t_pearl, 0.5, wet=0.6)
motif(t_pearl + 0.3, step=0.75, amp=0.13)
chord(['D3', 'A3', 'F#4', 'B4'], t_pearl, 11.0, amp=0.05, att=2.0, rel=3.0)

# ═════════════ 第四部 西山的雪铃 ═════════════
wind(S4 + 0.0, 40.0, amp=0.03, lo=100, hi=1100)
walk_pent(S4 + 0.6, 7.0, 0.95, start=1, octv=4, amp=0.1, seed=7)
chord(['D3', 'A3'], S4 + 0.5, 8.0, amp=0.045)
# 老奶奶捆柴：木鱼
for k in range(5):
    put(muyu(0.1, 700), ev('s4', 0, 1.0) + k * 0.8, 0.5, wet=0.2)
# 霜林：冰一样的细碎的高音
tinkle(ev('s4', 1, 0.0), n=14, span=7.0, f0=2300, amp=0.035)
put(xiao(hz('B3'), 7.0, amp=0.08, att=1.5), ev('s4', 1, 0.0), 0.5, wet=0.6)
# 雪山小屋
arp(ev('s4', 2, 0.0), ['A4', 'F#4', 'E4', 'D4'], 0.8, amp=0.09)
# 铜铃：“当——当——”
put(rbell(hz('G5'), 6.0, 0.20), ev('s4', 3, -0.8), 0.5, wet=0.5)
put(rbell(hz('G5'), 6.0, 0.16), ev('s4', 3, 1.4), 0.5, wet=0.5)
# 铃儿说“这话答得好”：温暖的和弦
chord(['G3', 'D4', 'B4'], ev('s4', 4, 0.0), 8.0, amp=0.05, att=1.5)
put(xiao(hz('B4'), 6.0, amp=0.08, att=1.2), ev('s4', 4, 0.5), 0.5, wet=0.5)
# 扫屋、擦鼓、铲雪：木鱼
for k in range(10):
    put(muyu(0.1, 600 + 80 * (k % 3)), ev('s4', 4, 8.0) + k * 0.55, 0.5, wet=0.2)
# 小姑娘端热汤：暖
arp(ev('s4', 5, 0.0), ['D4', 'F#4', 'A4', 'B4', 'A4', 'F#4'], 0.45, amp=0.1)
put(rbell(hz('D5'), 6.0, 0.14), ev('s4', 5, 4.2), 0.5, wet=0.5)

# ═════════════ 第五部 北边的金鼓 ═════════════
chord(['D2', 'A2'], S5 + 0.0, 12.0, amp=0.055, att=2.0)
put(xiao(hz('D4'), 3.5, amp=0.1, att=0.5), S5 + 0.8, 0.5, wet=0.5)
put(xiao(hz('E4'), 3.5, amp=0.1, att=0.5), S5 + 3.6, 0.5, wet=0.5)
put(xiao(hz('F#4'), 5.0, amp=0.1, att=0.5), S5 + 6.4, 0.5, wet=0.5)
crackle(S5 + 0.5, 7.0, amp=0.045, rate=8)                    # 篝火
for k in range(12):                                              # 马蹄：木鱼，轻
    put(muyu(0.07, 520), ev('s5', 0, 3.0) + k * 0.46, 0.5, wet=0.2)
# 城里：低低的鼓点，慢
for k in range(9):
    put(drum(0.22, 3.0), ev('s5', 1, 0.0) + k * 2.0, 0.5, wet=0.4)
tinkle(ev('s5', 2, 0.0), n=5, span=5.0, f0=1500, amp=0.03)
arp(ev('s5', 3, 0.0), ['D4', 'E4', 'F#4', 'A4'], 1.3, amp=0.09)
# 爬塔：一级一级往上走的古筝
steps = ['D4', 'E4', 'F#4', 'A4', 'B4', 'D5', 'E5', 'F#5', 'A5']
t0 = ev('s5', 4, 0.0)
for k, nm in enumerate(steps):
    put(zheng(hz(nm), 2.5, 0.09 + 0.012 * k, bend=0.0), t0 + k * 1.05, 0.5, wet=0.4)
wind(t0, 10.5, amp=0.04, lo=200, hi=1500)
# “咚——”：在“他抬起手。”读完之后
t_drum = ev('s5', 5, 1.9)
put(drum(0.95, 6.0), t_drum, 0.5, wet=0.55)
put(rbell(hz('D3'), 7.0, 0.1), t_drum + 0.02, 0.5, wet=0.6)
rumble(t_drum, 4.0, amp=0.08)

# ═════════════ 第六部 点亮那盏灯 ═════════════
put(drum(0.3, 5.0), S6 + 0.0, 0.5, wet=0.6)                     # 鼓声的回响
tinkle(S6 + 0.8, n=10, span=3.0, f0=2100, amp=0.035)
chord(['D3', 'A3', 'D4', 'F#4'], S6 + 2.0, 12.0, amp=0.05, att=3.0, rel=3.0)
put(xiao(hz('A4'), 8.0, amp=0.11, att=1.8), S6 + 3.0, 0.5, wet=0.6)    # 守天门的神
arp(ev('s6', 0, 1.0), ['D5', 'A4', 'F#4', 'A4'], 1.1, amp=0.08)
put(xiao(hz('E4'), 6.0, amp=0.07, att=1.0), ev('s6', 1, 0.0), 0.5, wet=0.6)     # 灯心断了
# 火山：低低的轰鸣 + 火苗的火星
rumble(ev('s6', 2, -1.5), 12.0, amp=0.07)
crackle(ev('s6', 2, 0.0), 6.0, amp=0.05, rate=10)
arp(ev('s6', 2, 5.0), ['A5', 'B5', 'D6', 'F#6', 'A6'], 0.1, amp=0.07, dur=1.6, bend=0.0)
# 回家：温暖
walk_pent(ev('s6', 3, -2.0), 10.0, 0.95, start=2, octv=4, amp=0.1, seed=9)
chord(['D3', 'A3', 'F#4'], ev('s6', 3, 0.0), 8.0, amp=0.05, att=1.5, rel=2.5)
# 银针接好断心：一线细细的高音
for k in range(8):
    put(chime(hz(pent(k % 5 + 5, 5)) * 1.0, 1.8, 0.045), ev('s6', 4, 0.2) + k * 0.28, 0.4 + 0.2 * (k % 2), wet=0.5)
# 灯亮了：像碗、像盆、像车轮——全曲最满
t_lit = ev('s6', 5, 0.3)
put(env_shape(noise(4.0, 200, 5000, 1.0), [(0, 0), (3.2, 1), (4.0, 0)]) * 0.05, t_lit - 1.0, 0.5, wet=0.4)
for k, nm in enumerate(['D3', 'A3', 'D4', 'F#4', 'A4', 'D5']):
    put(pad(hz(nm), 16.0, amp=0.07, att=3.2, rel=4.0), t_lit, 0.3 + 0.08 * k, wet=0.45)
motif(t_lit + 0.2, step=0.62, amp=0.17, octave_shift=0, pan=0.4)
motif(t_lit + 0.4, step=0.62, amp=0.12, octave_shift=1, pan=0.6)
put(rbell(hz('D5'), 8.0, 0.18), t_lit, 0.5, wet=0.5)
put(rbell(hz('A5'), 8.0, 0.12), t_lit + 1.2, 0.5, wet=0.5)
put(drum(0.6, 5.0), t_lit + 0.1, 0.5, wet=0.5)
tinkle(t_lit + 0.3, n=26, span=7.0, f0=2000, amp=0.05)
put(xiao(hz('D5'), 9.0, amp=0.12, att=2.4, rel=2.5), t_lit + 1.0, 0.5, wet=0.55)
# 鸟、燕子
for k in range(12):
    bird(t_lit + 5.5 + k * 1.15 + rng.random() * 0.4, f0=2800 + 800 * rng.random(), amp=0.03, n=int(rng.integers(2, 5)), pan=0.2 + 0.6 * rng.random())
walk_pent(t_lit + 5.0, 10.0, 0.8, start=3, octv=5, amp=0.1, seed=12)
put(xiao(hz('A4'), 7.0, amp=0.09, att=1.2), ev('s6', 6, 0.5), 0.5, wet=0.6)       # 奶奶流泪

# ═════════════ 尾声 ═════════════
chord(['D3', 'A3', 'F#4'], S7 + 0.0, 12.0, amp=0.05, att=1.5, rel=3.5)
for k in range(5):
    bird(S7 + 1.0 + k * 2.2, f0=3000, amp=0.02, n=2, pan=0.3 + 0.1 * k)
put(chime(2093.0, 4.0, 0.04), S7 + 2.0, 0.6, wet=0.6)
put(chime(1760.0, 4.0, 0.035), S7 + 4.5, 0.4, wet=0.6)
motif(S7 + 5.5, step=0.9, amp=0.12)
put(xiao(hz('D4'), 8.0, amp=0.1, att=2.0, rel=3.5), ev('s7', 1, 0.0), 0.5, wet=0.6)

# ═════════════ 混响 + 母带 ═════════════
ir_n = int(2.4 * SR)
ti = np.arange(ir_n) / SR
irL = (rng.standard_normal(ir_n) * np.exp(-ti * 2.1)).astype(np.float32)
irR = (rng.standard_normal(ir_n) * np.exp(-ti * 2.1)).astype(np.float32)
irL = lp(irL, 5200); irR = lp(irR, 5200)
irL[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR)); irR[:int(0.017 * SR)] *= np.linspace(0, 1, int(0.017 * SR))
wl = fftconvolve(WL, irL)[:N] * 0.085
wr = fftconvolve(WR, irR)[:N] * 0.085
outL = DL + wl
outR = DR + wr
# 开头结尾淡入淡出
fade = np.ones(N, np.float32)
fi, fo = int(1.2 * SR), int(3.5 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
outL *= fade; outR *= fade
peak = max(np.abs(outL).max(), np.abs(outR).max())
p99 = np.percentile(np.abs(np.concatenate([outL[::7], outR[::7]])), 99.5)
g = 0.62 / p99                      # 按“常见的响度”定增益，鼓和灯亮的高潮靠软限幅压住，不让它们把整首压得很小
outL = np.tanh(outL * g) * 0.92
outR = np.tanh(outR * g) * 0.92
pcm = np.stack([outL, outR], 1)
pcm = (np.clip(pcm, -1, 1) * 32000).astype(np.int16)
path = ROOT / 'public/audio/score.wav'
path.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(path), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('score.wav', round(TOTAL, 1), 's  peak', round(float(peak), 3))
print({k: round(v, 1) for k, v in SC.items()})
