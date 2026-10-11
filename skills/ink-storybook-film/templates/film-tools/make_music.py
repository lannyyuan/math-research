"""《雪地里的那盏灯》配乐：全部由本脚本用 numpy 合成（无采样、无外部素材）。
  python3 -I scripts/make_music.py  →  public/audio/score.wav（再用 ffmpeg 压成 m4a）
灯的动机（lamp motif）：A5 → D6 → F#6（升上去），尾音 E6 一闪。它在每次灯出现时回来。
"""
import json, math, os, sys
import numpy as np

SR = 44100
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tl = json.load(open(os.path.join(root, "src/timeline.json"), encoding="utf-8"))
starts, acc = {}, 0.0
for sc in tl["scenes"]:
    starts[sc["id"].split("-")[0]] = acc
    acc += sc["len"]
TOTAL = acc
S = starts  # S['s4'] = 场景起点（秒）
rng = np.random.default_rng(20261010)

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
def hz(name):
    n = NOTE[name[0]]
    i = 1
    if name[i] == "#": n += 1; i += 1
    elif name[i] == "b": n -= 1; i += 1
    octv = int(name[i:])
    return 440.0 * 2 ** ((n + 12 * (octv + 1) - 69) / 12)

N = int(TOTAL * SR) + SR * 6
L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)       # 干声（过混响）
AL = np.zeros(N, np.float32); AR = np.zeros(N, np.float32)     # 环境声（不过混响）

def add(buf2, y, t0, gain, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    y = y[: N - i0]
    gl = gain * math.cos((pan + 1) * math.pi / 4); gr = gain * math.sin((pan + 1) * math.pi / 4)
    buf2[0][i0:i0 + len(y)] += (y * gl).astype(np.float32)
    buf2[1][i0:i0 + len(y)] += (y * gr).astype(np.float32)

def T(dur): return np.arange(int(dur * SR)) / SR
def fade(y, a=0.004, r=0.05):
    n = len(y); na = max(1, int(a * SR)); nr = max(1, min(n, int(r * SR)))
    y[:na] *= np.linspace(0, 1, na); y[-nr:] *= np.linspace(1, 0, nr); return y

def bell(f, dur=3.0, k=1.0):
    """音乐盒/钟琴：几个非整数泛音，指数衰减"""
    t = T(dur); y = np.zeros_like(t)
    for r, a, d in ((1, 1.0, 1.9), (2.01, 0.38, 3.4), (3.97, 0.16, 5.2), (5.43, 0.07, 8.0)):
        y += a * np.sin(2 * np.pi * f * r * t) * np.exp(-d * k * t)
    return fade(y * 0.5)

def pluck(f, dur=1.6, bright=1.0):
    t = T(dur); y = np.zeros_like(t)
    for h in range(1, 9):
        y += (1.0 / h) * np.sin(2 * np.pi * f * h * t + 0.3 * h) * np.exp(-(1.8 + 1.7 * h * bright) * t)
    return fade(y * 0.55)

def pad(f, dur, vib=0.0):
    t = T(dur); y = np.zeros_like(t)
    for h, a in ((1, 1.0), (2, 0.5), (3, 0.26), (4, 0.14), (6, 0.06)):
        for det in (-0.0035, 0.0, 0.0035):
            ph = rng.uniform(0, 6.28)
            y += a * np.sin(2 * np.pi * f * h * (1 + det) * t + ph + vib * np.sin(2 * np.pi * 4.6 * t) / (h))
    y *= 0.12
    env = np.minimum(1, t / min(2.4, dur * 0.4)) * np.minimum(1, (dur - t) / min(3.0, dur * 0.5))
    return y * np.clip(env, 0, 1) * (0.92 + 0.08 * np.sin(2 * np.pi * 0.22 * t))

def flute(f, dur, vib=1.0):
    t = T(dur)
    ph = 2 * np.pi * f * t + 0.012 * vib * np.sin(2 * np.pi * 5.0 * t) * f / 100.0 * 3
    y = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    y += 0.02 * rng.standard_normal(len(t))
    env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / 0.4)
    return y * np.clip(env, 0, 1) * 0.35

def thud(f=70, dur=1.4):
    t = T(dur); y = np.sin(2 * np.pi * (f + 60 * np.exp(-14 * t)) * t) * np.exp(-3.8 * t)
    return fade(y * 0.9, 0.002, 0.2)

def bandnoise(n, lo, hi, seed=0):
    r = np.random.default_rng(seed)
    X = np.fft.rfft(r.standard_normal(n)); fr = np.fft.rfftfreq(n, 1 / SR)
    m = ((fr > lo) & (fr < hi)).astype(float)
    m = np.convolve(m, np.hanning(41) / np.hanning(41).sum(), mode="same")
    y = np.fft.irfft(X * m, n); return y / (np.abs(y).max() + 1e-9)

def chord(names, t0, dur, gain=1.0, pan=0.0, vib=0.0):
    for i, nm in enumerate(names):
        add((L, R), pad(hz(nm), dur, vib), t0, gain * 0.9, pan + (i - len(names) / 2) * 0.08)

def motif(t0, gain=1.0, oct_up=0, slow=1.0, tag=True):
    f = [hz("A5"), hz("D6"), hz("F#6")]
    for i, ff in enumerate(f):
        add((L, R), bell(ff * 2 ** oct_up, 3.2), t0 + i * 0.62 * slow, 0.5 * gain, -0.2 + 0.2 * i)
    if tag: add((L, R), bell(hz("E6") * 2 ** oct_up, 3.6), t0 + 2.3 * slow, 0.36 * gain, 0.25)

def arp(names, t0, step, count, gain=0.5, inst=pluck, pan=0.0):
    for i in range(count):
        add((L, R), inst(hz(names[i % len(names)]), 1.8), t0 + i * step, gain * (0.85 + 0.15 * ((i % 3) == 0)), pan + 0.3 * math.sin(i))

def lamp_twinkles(t0, count, gain=0.2, every=1.7):
    for i in range(count):
        n = ["F#6", "A6", "E6", "D6", "A6"][i % 5]
        add((L, R), bell(hz(n), 2.4), t0 + i * every + (0.3 * ((i * 7) % 3)), gain, ((i * 37) % 11) / 5.5 - 1)

# ───────────────── 片头 0~5 ─────────────────
chord(["B2", "F#3"], S["s0"], 7.0, 0.9)
motif(S["s0"] + 1.0, 0.8)

# ───────────────── 一、雪夜迷路（孤单、空旷）5~35.5 ─────────────────
t = S["s1"]
chord(["B2", "F#3", "D4"], t, 11, 0.9); chord(["G2", "D3", "B3"], t + 10, 10, 0.85); chord(["B2", "F#3", "A3", "D4"], t + 19, 12, 0.9)
for tt, nm in ((3.0, "F#5"), (6.0, "D5"), (9.6, "B4"), (13.0, "A4")):
    add((L, R), bell(hz(nm), 3.6), t + tt, 0.22, -0.3)
motif(t + 11.4, 1.0)                       # “远远的山顶上，有一点小小的光”
lamp_twinkles(t + 16.5, 6, 0.14, 2.1)
motif(t + 18.8, 0.8, slow=1.15)            # “那一定是我家的灯”
arp(["B3", "D4", "F#4", "A4"], t + 23.8, 0.9, 12, 0.18)  # 迈步
# ───────────────── 二、遇见问号（轻快）35.5~56.5 ─────────────────
t = S["s2"]
chord(["D3", "A3", "F#4"], t, 9, 0.7); chord(["G2", "D3", "B3"], t + 8, 7, 0.7); chord(["D3", "A3", "F#4"], t + 14, 9, 0.7)
add((L, R), pluck(hz("A5"), 0.8), t + 1.3, 0.34, 0.4); add((L, R), pluck(hz("B5"), 0.8), t + 1.6, 0.34, 0.5)   # 耳朵动
for tt, f in ((4.6, "D5"), (5.0, "F#5"), (6.1, "A5"), (6.5, "B5")):
    add((L, R), pluck(hz(f), 0.9), t + tt, 0.32, -0.2)
for i, tt in enumerate((7.5, 8.1, 8.9, 9.7)):    # 一串问题：升调“？”
    add((L, R), pluck(hz(["E5", "F#5", "G5", "A5"][i]), 1.0), t + tt, 0.3, 0.2 * i - 0.3)
for i in range(10):
    add((L, R), pluck(hz(["D4", "F#4", "A4", "F#4"][i % 4]), 1.2), t + 12.6 + i * 0.62, 0.2, -0.3)
motif(t + 18.2, 0.6)
# ───────────────── 三、遇见慢慢（缓慢、苍老）56.5~78.5 ─────────────────
t = S["s3"]
chord(["G2", "D3", "G3", "B3"], t, 12, 0.8); chord(["D3", "A3", "F#4"], t + 11, 12, 0.75)
for tt, nm, d in ((3.4, "G3", 3.0), (6.6, "B3", 3.0), (10.0, "A3", 3.5), (14.0, "G3", 4.0)):
    add((L, R), flute(hz(nm), d), t + tt, 0.5, -0.1)
add((L, R), bell(hz("B5"), 3), t + 7.2, 0.18, 0.3)
motif(t + 12.9, 0.7, slow=1.2)             # 壳上是一张地图
add((L, R), bell(hz("D6"), 3), t + 17.8, 0.3, 0.1); add((L, R), bell(hz("A5"), 3), t + 18.4, 0.26, -0.1)   # “我背着你”
# ───────────────── 四、冰河落水（紧张但不吓人）78.5~113.5 ─────────────────
t = S["s4"]
chord(["B1", "F#2", "B2"], t, 17, 1.1)                       # 低沉的长音
chord(["E3", "B3", "E4"], t + 0.5, 12, 0.35)                 # 空灵的 sus 和弦
for i in range(40):                                           # 轻轻的高音颤音，像冰面在屏息
    add((L, R), bell(hz(["F#6", "G6"][i % 2]), 1.2, 1.8), t + 2 + i * 0.55 + rng.uniform(0, 0.1), 0.05 + 0.001 * i, rng.uniform(-0.8, 0.8))
add((AL, AR), fade(bandnoise(int(1.6 * SR), 400, 2400, 3) * np.hanning(int(1.6 * SR)) ** 2) * 0.5, t + 3.8, 0.12)   # 冰裂的细响
for k, tt in enumerate((4.0, 4.5, 5.0)):                      # 啪——
    add((L, R), thud(190 - 20 * k, 0.5) * 0.4, t + tt, 0.35 - 0.08 * k)
add((L, R), thud(60, 1.8), t + 5.7, 0.9)                      # 落水
add((AL, AR), fade(bandnoise(int(1.8 * SR), 600, 6000, 9) * np.exp(-3.2 * T(1.8))) * 0.9, t + 5.7, 0.28)         # 水花
chord(["B1", "F#2", "A2"], t + 6.0, 11, 0.9)
for i in range(26):                                           # 兔子急促的小音
    add((L, R), pluck(hz(["F#5", "G5", "A5", "G5"][i % 4]), 0.5), t + 7.0 + i * 0.4 + rng.uniform(0, 0.05), 0.07, rng.uniform(-0.6, 0.6))
chord(["D3", "A3", "D4", "F#4"], t + 11.2, 14, 0.95)         # 白鹿走来：暖
add((L, R), flute(hz("A4"), 5.5, 1.2), t + 12.0, 0.5, 0.0); add((L, R), flute(hz("F#4"), 4.5, 1.2), t + 17.6, 0.45, 0.0)
arp(["D4", "F#4", "A4", "D5", "A4", "F#4"], t + 19.6, 0.5, 14, 0.25)   # 轻轻一抬
chord(["D3", "A3", "F#4"], t + 25, 11, 0.8); chord(["G3", "D4", "B4"], t + 30, 8, 0.6)
motif(t + 28.2, 0.6, slow=1.2)
# ───────────────── 五、火堆边（温暖、亲近）113.5~143.5 ─────────────────
t = S["s5"]
chord(["D3", "A3", "D4"], t + 2.8, 9, 0.8); chord(["B2", "F#3", "B3", "D4"], t + 11, 9, 0.8); chord(["G2", "D3", "G3", "B3"], t + 19, 6, 0.8); chord(["A2", "E3", "A3", "C#4"], t + 24, 7, 0.8)
arp(["D4", "A4", "F#4", "A4", "D5", "A4"], t + 3.2, 0.62, 40, 0.17, pluck, -0.2)
motif(t + 9.4, 0.7, slow=1.2); motif(t + 16.0, 0.55, slow=1.3, tag=False)
add((L, R), bell(hz("A5"), 3.5), t + 23.4, 0.3, 0.2); add((L, R), bell(hz("D6"), 3.5), t + 25.4, 0.3, -0.2)
# 火堆噼啪
crack = np.zeros(int(26 * SR), np.float32)
for _ in range(120):
    p = rng.uniform(0, 26); i0 = int(p * SR); d = rng.uniform(0.004, 0.02); n = int(d * SR)
    crack[i0:i0 + n] += (rng.standard_normal(n) * np.exp(-np.linspace(0, 6, n)) * rng.uniform(0.2, 1.0)).astype(np.float32)
add((AL, AR), crack, t + 3.0, 0.22, 0.0)
add((AL, AR), bandnoise(int(26 * SR), 150, 700, 11).astype(np.float32) * np.hanning(int(26 * SR)) ** 0.5, t + 3.0, 0.03)
# ───────────────── 六、帮小狼找到妈妈（先紧张后温柔）143.5~175 ─────────────────
t = S["s6"]
chord(["E2", "B2", "E3"], t, 10, 0.95)
for i in range(30):
    add((L, R), bell(hz(["G5", "F#5"][i % 2]), 1.2, 1.9), t + 2.2 + i * 0.5 + rng.uniform(0, 0.08), 0.045, rng.uniform(-0.7, 0.7))
add((L, R), thud(55, 1.8), t + 3.0, 0.8)
chord(["G2", "D3", "B3"], t + 8, 11, 0.8)
add((L, R), flute(hz("D5"), 4.0, 1.1), t + 9.5, 0.38, 0.1); add((L, R), flute(hz("B4"), 4.5, 1.1), t + 13.8, 0.38, 0.0)
chord(["E2", "B2", "G3"], t + 17.2, 8, 0.85)
for i in range(18):
    add((L, R), bell(hz(["B5", "A5"][i % 2]), 1.2, 1.9), t + 18 + i * 0.55, 0.04, rng.uniform(-0.7, 0.7))
chord(["G2", "D3", "G3", "B3"], t + 23.6, 8, 0.9); chord(["D3", "A3", "F#4"], t + 27.5, 6, 0.8)
motif(t + 24.8, 0.55, slow=1.25)
# ───────────────── 七、冰雪化开（明亮、流动）175~192 ─────────────────
t = S["s7"]
chord(["D3", "A3", "F#4", "A4"], t, 7, 0.8); chord(["A2", "E3", "A3", "C#4"], t + 6, 6, 0.75); chord(["B2", "F#3", "B3", "D4"], t + 11, 8, 0.75)
arp(["D4", "F#4", "A4", "D5", "F#5", "A5", "F#5", "D5"], t + 0.8, 0.28, 56, 0.2, pluck, 0.0)
motif(t + 10.3, 0.8, oct_up=0, slow=1.1)
for i in range(7):                                            # 鸟鸣
    tt = t + 2.0 + i * 2.1 + rng.uniform(0, 0.6)
    for j in range(3):
        f = rng.uniform(2800, 3600); tt2 = tt + j * 0.11; tt_ = T(0.09)
        add((AL, AR), np.sin(2 * np.pi * (f + 600 * tt_ / 0.09) * tt_) * np.hanning(len(tt_)) * 0.5, tt2, 0.05, rng.uniform(-0.8, 0.8))
add((AL, AR), bandnoise(int(17 * SR), 1500, 5500, 13).astype(np.float32) * np.linspace(0, 1, int(17 * SR)) * 0.5, t, 0.03)   # 流水
# ───────────────── 八、山顶（攀登 → 灯 → 光）192~228.5 ─────────────────
t = S["s8"]
chord(["B2", "F#3", "B3"], t, 12, 0.9)
for i in range(30):
    add((L, R), pluck(hz(["B3", "D4", "F#4", "A4"][i % 4]), 1.0), t + 0.8 + i * 0.7, 0.12, -0.2)
add((AL, AR), (bandnoise(int(12 * SR), 120, 600, 17) * np.hanning(int(12 * SR))).astype(np.float32), t, 0.07)    # 风
chord(["G2", "D3", "B3"], t + 11, 10, 0.9)
motif(t + 10.2, 1.0, slow=1.1)
chord(["D3", "A3", "D4", "F#4"], t + 20, 18, 1.0)
add((L, R), flute(hz("A4"), 5.0, 1.0), t + 15.5, 0.4, 0.0); add((L, R), flute(hz("F#4"), 5.5, 1.0), t + 22.0, 0.4, 0.0)
motif(t + 22.4, 0.5, slow=1.3, tag=False)
chord(["G3", "D4", "B4"], t + 28.6, 9, 0.9)
motif(t + 29.2, 1.0, oct_up=0, slow=1.3)
arp(["D4", "A4", "D5", "F#5", "A5", "F#5"], t + 30.0, 0.55, 14, 0.2, bell, 0.0)
# ───────────────── 九、告别（惦念而温柔）228.5~262.5 ─────────────────
t = S["s9"]
chord(["B2", "F#3", "B3", "D4"], t + 0.8, 9, 0.9); chord(["G2", "D3", "G3", "B3"], t + 8.6, 9, 0.85); chord(["D3", "A3", "D4", "F#4"], t + 16.8, 9, 0.85); chord(["A2", "E3", "A3", "C#4"], t + 25, 10, 0.8)
for tt, nm in ((2.0, "F#5"), (3.4, "D5"), (5.0, "B4"), (9.0, "D5"), (10.4, "B4"), (13.4, "A5"), (15.0, "F#5"), (19.4, "D6"), (21.0, "A5"), (25.4, "F#5"), (27.4, "D5"), (29.6, "A4")):
    add((L, R), bell(hz(nm), 4.0), t + tt, 0.26, 0.2 * math.sin(tt))
motif(t + 14.0, 0.7, slow=1.2); motif(t + 19.6, 0.7, slow=1.3)
chord(["D3", "A3", "F#4"], t + 30, 8, 0.6)
# ───────────────── 十、窗边的灯（摇篮曲）262.5~290.5 ─────────────────
t = S["s10"]
add((AL, AR), fade(bandnoise(int(0.35 * SR), 1500, 7000, 21) * np.exp(-9 * T(0.35))) * 0.8, t + 2.0, 0.12)        # 划火柴
chord(["D3", "A3", "F#4"], t + 3.0, 10, 0.8); chord(["G2", "D3", "B3"], t + 12, 8, 0.8); chord(["D3", "A3", "D4", "F#4"], t + 19.5, 12, 0.85)
motif(t + 3.4, 1.1, slow=1.3)                       # 灯点亮
mel = [("F#5", 6.8), ("A5", 7.6), ("D6", 8.6), ("B5", 9.9), ("A5", 10.8), ("F#5", 12.0), ("E5", 13.2), ("D5", 14.4),
       ("F#5", 16.0), ("A5", 17.0), ("B5", 18.2), ("A5", 19.4), ("F#5", 20.6), ("D5", 22.2), ("E5", 23.4), ("D5", 24.8)]
for nm, tt in mel:
    add((L, R), bell(hz(nm), 3.4), t + tt, 0.24, 0.3 * math.sin(tt))
lamp_twinkles(t + 15.0, 3, 0.15, 1.8)               # 远处山顶的光，一闪一闪
motif(t + 25.0, 0.6, slow=1.4)
add((L, R), bell(hz("D7"), 5.0), t + 27.2, 0.18, 0.0)
# 雨：从第 7 秒起，细细的
rain = bandnoise(int(22 * SR), 2500, 9000, 23).astype(np.float32)
add((AL, AR), rain * np.minimum(1, np.linspace(0, 3, len(rain))), t + 6.5, 0.04)
# 全片的风（夜里）
for sid, a, b in (("s1", 0, 30), ("s2", 0, 20), ("s3", 0, 21), ("s6", 0, 30)):
    n = int((b - a) * SR)
    wind = bandnoise(n, 100, 500, sum(map(ord, sid))).astype(np.float32) * (0.6 + 0.4 * np.sin(np.linspace(0, 9, n)))
    add((AL, AR), wind * np.hanning(n) ** 0.4, S[sid] + a, 0.035)

# ───────────────── 混响 + 母带 ─────────────────
def reverb(x, ir):
    n = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
def make_ir(seed, rt=3.2):
    r = np.random.default_rng(seed); n = int(rt * SR); tt = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-6.9 * tt / rt)
    ir = np.convolve(ir, np.hanning(9) / np.hanning(9).sum(), mode="same")      # 暗一点
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt((ir ** 2).sum())
wetL = reverb(L, make_ir(1)); wetR = reverb(R, make_ir(2))
outL = 0.62 * L + 0.55 * wetL + AL
outR = 0.62 * R + 0.55 * wetR + AR
out = np.stack([outL, outR], 1)[: int(TOTAL * SR)]
# 淡入淡出
fi, fo = int(1.2 * SR), int(4.0 * SR)
out[:fi] *= np.linspace(0, 1, fi)[:, None]; out[-fo:] *= np.linspace(1, 0, fo)[:, None]
# 去直流、温柔限幅、整体响度（很轻，字幕和画面才是主角）
out -= out.mean(0)
peak = np.abs(out).max(); out = np.tanh(out / peak * 1.4) / np.tanh(1.4) * 0.5
os.makedirs(os.path.join(root, "public/audio"), exist_ok=True)
import wave
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
with wave.open(os.path.join(root, "public/audio/score.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
rms = np.sqrt((out ** 2).mean()); print(f"时长 {len(out)/SR:.1f}s  峰值 {np.abs(out).max():.3f}  RMS {20*np.log10(rms):.1f} dBFS")
for k, v in S.items():
    seg = out[int(v * SR): int((v + 8) * SR)]
    print(k, f"{20*np.log10(np.sqrt((seg**2).mean()) + 1e-9):6.1f} dBFS (前8秒)")
