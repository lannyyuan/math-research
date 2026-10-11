import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {W, H} from '../palette';

// 雪一直在下：三层（远处小而慢，近处大而快、虚一点），风让雪斜着飘。
interface Flake {x: number; y: number; r: number; vy: number; ph: number; fq: number; amp: number; o: number; rank: number}
const rngf = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};
const make = (n: number, seed: number, r0: number, r1: number, v0: number, v1: number): Flake[] => {
  const r = rngf(seed);
  return Array.from({length: n}, (_, i) => ({x: r() * W, y: r() * (H + 40), r: r0 + r() * (r1 - r0), vy: v0 + r() * (v1 - v0), ph: r() * 6.28, fq: 0.25 + r() * 0.5, amp: 10 + r() * 26, o: 0.55 + r() * 0.4, rank: i / n}));
};
const layers = [make(120, 7, 1.1, 2.2, 26, 44), make(80, 8, 2, 3.6, 46, 72), make(30, 9, 4, 8, 80, 120)];

/** amount 0~1 雪量；wind 横向风（正=向右吹）；speed 下落速度倍数；color 雪的颜色（暗处的雪略带蓝灰） */
export const Snow: React.FC<{amount?: number; wind?: number; speed?: number; color?: string; t0?: number; blurBig?: boolean}> = ({amount = 1, wind = 0.1, speed = 1, color = '246,249,255', t0 = 0, blurBig = true}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const items = useMemo(() => layers, []);
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
      <defs>
        <radialGradient id="flakeSoft">
          <stop offset="0" stopColor={`rgb(${color})`} stopOpacity={0.95} />
          <stop offset="0.55" stopColor={`rgb(${color})`} stopOpacity={0.55} />
          <stop offset="1" stopColor={`rgb(${color})`} stopOpacity={0} />
        </radialGradient>
      </defs>
      {items.map((L, li) =>
        L.map((f, i) => {
          if (f.rank > amount) return null;
          const y = (((f.y + f.vy * speed * t) % (H + 40)) + H + 40) % (H + 40) - 20;
          const x = (((f.x + Math.sin(t * f.fq + f.ph) * f.amp + wind * t * (30 + li * 40) * speed) % (W + 60)) + W + 60) % (W + 60) - 30;
          return li === 2 && blurBig ? <circle key={`${li}-${i}`} cx={x} cy={y} r={f.r * 1.8} fill="url(#flakeSoft)" opacity={f.o * 0.8} /> : <circle key={`${li}-${i}`} cx={x} cy={y} r={f.r} fill={`rgb(${color})`} opacity={f.o} />;
        }),
      )}
    </svg>
  );
};
