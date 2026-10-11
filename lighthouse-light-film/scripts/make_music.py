#!/usr/bin/env python3
"""配乐（自己合成，无外部素材、无版权问题）：温柔的冬夜小曲 + 灯塔动机（D–F#–A–F#，音乐盒的音色）。
结构跟着 src/timeline.json 的场景走；大灯亮起（S8 第 23.5 秒）是全曲最亮、最满的一刻。
输出 public/audio/score.wav（44.1 kHz 立体声）。纯 numpy，不需要任何音源。"""
import json, math, pathlib
import numpy as np
import wave

SR = 44100
ROOT = pathlib.Path(__file__).resolve().parent.parent
tl = json.loads((ROOT / 'src/timeline.json').read_text())
starts, s = {}, 0
for sc in tl['scenes']:
    starts[sc['id'].split('-')[0]] = s   # 's0', 's1', ...
    s += sc['len']
TOTAL = s
N = int(TOTAL * SR)
L = np.zeros(N, np.float32)
R = np.zeros(N, np.float32)
rng = np.random.default_rng(7)

NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hz(name):
    """'D4' / 'F#5' / 'Bb3' → 频率"""
    n = NOTE[name[0]]
    i = 1
    if name[i] == '#': n += 1; i += 1
    elif name[i] == 'b': n -= 1; i += 1
    octave = int(name[i:])
    return 440.0 * 2 ** ((n - 9 + (octave - 4) * 12) / 12)


def put(sig, t0, pan=0.5, gain=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0:
        return
    a, b = max(i0, 0), min(i0 + len(sig), N)
    seg = sig[a - i0:b - i0] * gain
    L[a:b] += seg * math.cos(pan * math.pi / 2)
    R[a:b] += seg * math.sin(pan * math.pi / 2)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def bell(f, dur=3.5, amp=0.18):
    """音乐盒 / 钟琴：基音 + 非整数倍的泛音，各自指数衰减。"""
    t = tt(dur)
    out = np.zeros_like(t)
    for k, (m, a, d) in enumerate([(1, 1.0, 1.6), (2.76, 0.35, 2.6), (5.4, 0.12, 5.0), (8.9, 0.05, 8.0)]):
        out += a * np.sin(2 * math.pi * f * m * t) * np.exp(-t * d)
    out *= np.minimum(t / 0.003, 1)
    return (out * amp).astype(np.float32)


def pluck(f, dur=2.0, amp=0.16):
    """钢琴一样柔和的拨弦：几个谐波，快衰减。"""
    t = tt(dur)
    out = np.zeros_like(t)
    for k, (m, a, d) in enumerate([(1, 1.0, 2.2), (2, 0.5, 3.0), (3, 0.25, 4.5), (4, 0.12, 6.0), (5, 0.06, 8.0)]):
        out += a * np.sin(2 * math.pi * f * m * t + 0.3 * k) * np.exp(-t * d)
    out *= np.minimum(t / 0.006, 1)
    return (out * amp).astype(np.float32)


def pad(f, dur, amp=0.07, att=1.6, rel=2.0, det=0.004):
    """暖暖的铺底：两条略微走音的正弦 + 八度，慢起慢落。"""
    t = tt(dur)
    out = (np.sin(2 * math.pi * f * (1 + det) * t) + np.sin(2 * math.pi * f * (1 - det) * t + 1.1) + 0.35 * np.sin(2 * math.pi * f * 2 * t + 0.4)) / 2.35
    env = np.minimum(t / att, 1) * np.minimum((dur - t) / rel, 1)
    return (out * np.clip(env, 0, 1) ** 1.5 * amp).astype(np.float32)


def chord(names, t0, dur, amp=0.06, pan_w=0.25, **kw):
    for k, nm in enumerate(names):
        put(pad(hz(nm), dur, amp=amp, **kw), t0, 0.5 + pan_w * math.sin(k * 1.7))


def noise(dur, lo=200, hi=1200, amp=0.05):
    """滤过的噪声：风 / 引擎的低吼。用一阶滤波叠出带通。"""
    x = rng.standard_normal(int(dur * SR)).astype(np.float32)
    def lp(sig, fc):
        a = math.exp(-2 * math.pi * fc / SR)
        out = np.empty_like(sig); y = 0.0
        # 向量化的递推：分块用 lfilter 等价写法
        from numpy import cumsum
        return _lp(sig, a)
    y = _lp(x, math.exp(-2 * math.pi * hi / SR)) - _lp(x, math.exp(-2 * math.pi * lo / SR))
    y /= (np.abs(y).max() + 1e-9)
    return (y * amp).astype(np.float32)


def _lp(x, a):
    # y[n] = (1-a) x[n] + a y[n-1]；用分段递推加速
    out = np.empty_like(x)
    y = 0.0
    blk = 4096
    for i in range(0, len(x), blk):
        seg = x[i:i + blk]
        # 在块内用 scipy 风格的递推展开
        n = len(seg)
        w = a ** np.arange(n, dtype=np.float64)
        # 卷积：y = (1-a) * conv(seg, w) + a^(k+1) y0
        c = np.convolve(seg.astype(np.float64), w)[:n] * (1 - a)
        out[i:i + n] = (c + (a ** (np.arange(n) + 1)) * y).astype(np.float32)
        y = float(out[i + n - 1])
    return out


def shaped(sig, points):
    """按 (时间, 增益) 折线给一段信号加包络"""
    t = np.arange(len(sig)) / SR
    ts, gs = zip(*points)
    return (sig * np.interp(t, ts, gs)).astype(np.float32)


# ───────── 和弦 / 音阶 ─────────
D_ = ['D3', 'A3', 'D4', 'F#4']
Bm = ['B2', 'F#3', 'B3', 'D4']
G_ = ['G2', 'D3', 'G3', 'B3']
A_ = ['A2', 'E3', 'A3', 'C#4']
Em = ['E3', 'B3', 'E4', 'G4']
Dsus = ['D3', 'A3', 'E4', 'A4']
MOTIF = ['D5', 'F#5', 'A5', 'F#5']      # 灯塔动机
PENT = ['D4', 'E4', 'F#4', 'A4', 'B4', 'D5', 'E5', 'F#5', 'A5']


def loop(prog, t0, beats_per_chord=4, bpm=60, n=4, arp=True, amp=0.055, melody=None, mel_amp=0.12):
    """按和弦走向铺底 + 分解和弦（慢）。"""
    beat = 60.0 / bpm
    for k in range(n):
        ch = prog[k % len(prog)]
        t = t0 + k * beats_per_chord * beat
        chord(ch, t, beats_per_chord * beat + 1.0, amp=amp)
        if arp:
            seq = [ch[0], ch[2], ch[3], ch[1] if len(ch) > 3 else ch[1]]
            for j, nm in enumerate(seq):
                nm2 = nm[:-1] + str(int(nm[-1]) + 1) if j % 2 else nm
                put(pluck(hz(nm2), 2.0, 0.07), t + j * beat, 0.35 + 0.3 * (j % 2))
        if melody:
            for (off, nm, d) in melody[k % len(melody)]:
                put(pluck(hz(nm), d, mel_amp), t + off * beat, 0.6)


def motif(t0, amp=0.16, oct_up=0, gap=0.7):
    for j, nm in enumerate(MOTIF):
        nm2 = nm[:-1] + str(int(nm[-1]) + oct_up)
        put(bell(hz(nm2), 4.0, amp), t0 + j * gap, 0.6 + 0.1 * math.sin(j))


def ping(t0, amp=0.2):
    """Bolts 的「Beep. Bleep. Ping!」"""
    for j, nm in enumerate(['A5', 'D6', 'F#6']):
        put(bell(hz(nm), 1.6, amp), t0 + j * 0.28, 0.5)


# ───────── 各场景 ─────────
S = lambda k, off=0.0: starts[k] + off

# S0 片头：一个长长的 Dsus，灯塔动机在灯光亮起时出现
chord(Dsus, S('s0'), 7.0, amp=0.06, att=2.0)
motif(S('s0', 1.3), 0.18, gap=0.85)

# S1 平安夜的早晨：慢慢的钢琴 + 铺底，越到后面越沉（暴风雪要来了）
loop([D_, Bm, G_, A_], S('s1'), n=7, bpm=60, amp=0.05, melody=[[(0, 'F#5', 3)], [(2, 'D5', 3)], [(0, 'B4', 3)], [(1, 'E5', 3)]])
chord(Em, S('s1', 22), 7.0, amp=0.04)
motif(S('s1', 24), 0.1, gap=1.0)

# S2 Grandad 摔倒：忧一点
loop([Bm, G_, Em, A_], S('s2'), n=6, bpm=56, amp=0.05, melody=[[(0, 'D5', 3)], [(2, 'B4', 3)], [(0, 'G4', 3)], [(1, 'A4', 3)]])
put(bell(hz('A4'), 4.0, 0.12), S('s2', 14.2), 0.6)       # "So the lighthouse is dark," 一个孤单的音
put(bell(hz('E4'), 4.0, 0.10), S('s2', 15.4), 0.4)

# S3 修理铺：俏皮的拨弦，Bolts 的眼睛亮起（Beep. Bleep. Ping!）
for k in range(26):
    nm = PENT[(k * 3 + (k // 4)) % len(PENT)]
    put(pluck(hz(nm), 1.0, 0.09), S('s3', 0.4 + k * 0.9), 0.3 + 0.4 * (k % 2))
for j, ch in enumerate([D_, G_, D_, A_] * 2):
    chord(ch, S('s3', j * 3.2), 4.0, amp=0.045)
ping(S('s3', 15.0))
motif(S('s3', 19.4), 0.12, gap=0.8)

# S4 走路：轻轻的脚步（拨弦打点）+ 小调；Comet 出现时加一个钟琴
for k in range(40):
    put(pluck(hz('D3' if k % 4 == 0 else ('A3' if k % 4 == 2 else 'F#3')), 0.7, 0.07), S('s4', 0.6 + k * 0.66), 0.5)
for j, ch in enumerate([Bm, G_, D_, A_] * 2):
    chord(ch, S('s4', j * 3.4), 4.2, amp=0.045)
for j, nm in enumerate(['B4', 'D5', 'F#5', 'E5', 'D5', 'B4']):
    put(bell(hz(nm), 2.5, 0.11), S('s4', 14.7 + j * 0.9), 0.65)
put(bell(hz('D5'), 3.0, 0.10), S('s4', 22.6), 0.6)

# S5 农场：暖一点；灯光出现（高音钟）；递帽子；Pebbles（小小的、有点倔的低音）
loop([G_, D_, Em, A_], S('s5'), n=6, bpm=60, amp=0.055, melody=[[(0, 'B4', 3)], [(0, 'A4', 3)], [(0, 'G4', 3)], [(0, 'E5', 3)]])
motif(S('s5', 1.2), 0.1, gap=1.1)
for j, nm in enumerate(['G5', 'B5', 'D6']):
    put(bell(hz(nm), 2.5, 0.12), S('s5', 9.6 + j * 0.3), 0.55)
for j in range(4):
    put(pluck(hz('D3'), 0.5, 0.12), S('s5', 15.0 + j * 0.45), 0.4)
for j, nm in enumerate(['G5', 'F#5', 'E5']):
    put(bell(hz(nm), 2.5, 0.10), S('s5', 19.6 + j * 0.5), 0.6)

# S6 冰：低沉的和弦 + 心跳；咔嚓；水花；拉！；松一口气
chord(['E2', 'B2', 'E3', 'G3'], S('s6'), 16.0, amp=0.06, att=0.8)
chord(['G2', 'D3', 'G3', 'B3'], S('s6', 16.5), 8.5, amp=0.06, att=1.0)
crack = shaped(noise(0.5, 1800, 7000, 0.7), [(0, 1), (0.06, 0.8), (0.5, 0)])
put(crack, S('s6', 1.0), 0.5)
put(crack * 0.8, S('s6', 1.3), 0.4)
put(shaped(noise(1.4, 100, 900, 0.45), [(0, 0), (0.1, 1), (1.4, 0)]), S('s6', 2.5), 0.5)      # 水花
for k in range(18):   # 心跳：越来越近
    put(shaped(np.sin(2 * math.pi * 62 * tt(0.35)).astype(np.float32), [(0, 0), (0.02, 1), (0.35, 0)]) * (0.10 + 0.012 * k), S('s6', 4.0 + k * 0.96), 0.5)
for j, nm in enumerate(['E4', 'G4', 'B4']):
    put(bell(hz(nm), 3.0, 0.08), S('s6', 11.0 + j * 1.3), 0.4)
put(bell(hz('B4'), 2.0, 0.16), S('s6', 17.2), 0.5)      # "Comet! Pull!"
chord(['D3', 'A3', 'D4', 'F#4'], S('s6', 20.4), 6.0, amp=0.08, att=1.0)
motif(S('s6', 20.8), 0.12, gap=0.9)

# S7 悬崖暴风雪：风声 + 低沉的铺底；帽子掉下去（下行的音）；抓住了；"我们当然回来了"（G 大调的暖）
wind = noise(26.5, 200, 1800, 0.30)
wind = shaped(wind, [(0, 0.0), (2, 0.7), (11, 1.0), (16, 0.7), (21, 0.25), (26, 0.0)])
put(wind, S('s7'), 0.5)
chord(['E2', 'B2', 'E3', 'G3'], S('s7'), 12.0, amp=0.06, att=1.2)
chord(['D3', 'A3', 'C4', 'F#4'], S('s7', 11.0), 8.0, amp=0.055, att=1.0)
for j, nm in enumerate(['B5', 'G5', 'E5', 'B4']):
    put(bell(hz(nm), 2.5, 0.12), S('s7', 6.4 + j * 0.45), 0.5)
chord(G_, S('s7', 18.6), 8.0, amp=0.075, att=0.9)
chord(D_, S('s7', 21.4), 6.0, amp=0.06, att=0.9)
motif(S('s7', 19.4), 0.12, gap=0.9)

# S8 灯塔：低低的暗；"Nothing happened."的静；Bolts 的摇篮曲；引擎低吼；然后——大灯亮了（全曲最亮）
chord(['D2', 'A2', 'D3'], S('s8'), 8.0, amp=0.065, att=1.0)
for j, nm in enumerate(['A4', 'F#4', 'D4']):
    put(bell(hz(nm), 3.0, 0.08), S('s8', 3.0 + j * 1.2), 0.35)
chord(['B2', 'F#3', 'B3', 'D4'], S('s8', 11.0), 6.5, amp=0.05, att=1.0)
for j, nm in enumerate(['D6', 'B5', 'A5', 'F#5']):    # "Goodnight, friends," 音乐盒摇篮曲
    put(bell(hz(nm), 3.5, 0.17), S('s8', 15.0 + j * 0.8), 0.55)
eng = np.sin(2 * math.pi * 41 * tt(7.0)) * 0.5 + 0.35 * np.sign(np.sin(2 * math.pi * 20.5 * tt(7.0))) * 0.3
eng = eng * (0.6 + 0.4 * np.sin(2 * math.pi * 11 * tt(7.0)))
eng = (eng + noise(7.0, 60, 400, 0.4)).astype(np.float32)
put(shaped(eng, [(0, 0), (0.6, 1.0), (4.0, 1.0), (5.0, 0.5), (7.0, 0)]) * 0.34, S('s8', 18.4), 0.5)
# 大灯亮起：满满的 D 大调 + 琶音 + 光芒
T = S('s8', 23.5)
chord(['D2', 'A2', 'D3', 'F#3'], T, 11.0, amp=0.11, att=0.5, rel=3.0)
chord(['D3', 'A3', 'D4', 'F#4', 'A4'], T, 11.0, amp=0.09, att=0.9, rel=3.0)
for j, nm in enumerate(['D4', 'F#4', 'A4', 'D5', 'F#5', 'A5', 'D6']):
    put(bell(hz(nm), 4.0, 0.2), T + 0.1 + j * 0.2, 0.3 + 0.07 * j)
motif(T + 2.2, 0.2, oct_up=0, gap=0.6)
motif(T + 5.0, 0.12, oct_up=1, gap=0.6)

# S9 回港：动机变成主旋律，温暖、安定；船队用拨弦，爸爸上岸（拥抱处和弦最满）
loop([D_, G_, A_, D_, Bm, G_, A_, D_], S('s9'), n=8, bpm=56, amp=0.065, melody=[[(0, 'A5', 3), (2, 'F#5', 3)], [(0, 'G5', 3), (2, 'B5', 3)], [(0, 'E5', 3), (2, 'A5', 3)], [(0, 'F#5', 4)]], mel_amp=0.09)
for j, nm in enumerate(['A4', 'D5', 'F#5']):
    put(bell(hz(nm), 3.0, 0.1), S('s9', 2.0 + j * 0.9), 0.45)    # 小小的光在回答
for k in range(7):
    put(pluck(hz(PENT[(k * 2) % len(PENT)]), 1.4, 0.08), S('s9', 8.0 + k * 0.95), 0.3 + 0.07 * k)
chord(['D3', 'A3', 'D4', 'F#4', 'A4'], S('s9', 17.4), 10.0, amp=0.08, att=1.0, rel=3.0)
motif(S('s9', 19.0), 0.15, gap=0.8)
put(bell(hz('D5'), 6.0, 0.14), S('s9', 23.4), 0.5)

# S10 圣诞早上 → 晚上：快乐的小音乐盒 → 摇篮曲 → 一个长长的、安静的结尾
CAROL = ['D5', 'D5', 'A5', 'A5', 'B5', 'B5', 'A5', 'G5', 'G5', 'F#5', 'F#5', 'E5', 'E5', 'D5']
for k, nm in enumerate(CAROL):
    put(bell(hz(nm), 2.5, 0.10), S('s10', 0.8 + k * 0.62), 0.55)
loop([D_, G_, D_, A_], S('s10'), n=4, bpm=70, amp=0.05, arp=True)
ping(S('s10', 8.8), 0.2)
chord(D_, S('s10', 9.5), 5.0, amp=0.07, att=0.6)
# 晚上：三拍子摇篮曲（越来越稀）
LULL = [('F#5', 0), ('A5', 1), ('D6', 2), ('B5', 3), ('A5', 4), ('F#5', 5), ('G5', 6), ('E5', 7), ('D5', 8)]
for j, (nm, k) in enumerate(LULL):
    put(bell(hz(nm), 3.5, 0.12 * (1 - 0.06 * k)), S('s10', 13.4 + k * 1.15), 0.5)
chord(['B2', 'F#3', 'B3', 'D4'], S('s10', 13.0), 9.0, amp=0.055, att=1.2)
chord(['G2', 'D3', 'G3', 'B3'], S('s10', 21.0), 6.0, amp=0.05, att=1.0)
put(shaped(noise(0.08, 800, 6000, 0.5), [(0, 1), (0.08, 0)]), S('s10', 21.5), 0.5)     # 关灯的"啪嗒"
chord(['D2', 'A2', 'D3', 'A3'], S('s10', 23.0), 11.5, amp=0.06, att=2.0, rel=4.5)
motif(S('s10', 25.5), 0.13, gap=1.2)        # 最后一次灯塔动机，轻轻的
put(bell(hz('D6'), 8.0, 0.10), S('s10', 31.0), 0.5)

# ───────── 母带：混响感（几条延时）→ 限幅 → 淡入淡出 ─────────
def echo(x, delays=(0.17, 0.31, 0.53), gains=(0.32, 0.22, 0.14)):
    y = x.copy()
    for d, g in zip(delays, gains):
        k = int(d * SR)
        y[k:] += x[:-k] * g
    return y

L = echo(L); R = echo(R, delays=(0.21, 0.37, 0.59))
mx = max(np.abs(L).max(), np.abs(R).max())
g = 0.75 / mx
fade = np.minimum(np.arange(N) / (1.5 * SR), 1) * np.minimum((N - np.arange(N)) / (3.0 * SR), 1)
L = np.tanh(L * g * 1.1) * fade; R = np.tanh(R * g * 1.1) * fade
pcm = (np.stack([L, R], 1) * 32767 * 0.9).astype(np.int16)
out = ROOT / 'public/audio'
out.mkdir(parents=True, exist_ok=True)
with wave.open(str(out / 'score.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('score.wav', round(TOTAL), 's', round(float(np.sqrt((pcm.astype(np.float32) / 32767) ** 2).mean() ** 0.5), 3))
