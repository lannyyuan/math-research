import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {rng} from '../art/ink';
import {W, H} from '../palette';

// 全片都在下雪：三层雪花，远处小而慢，近处大而快，缓慢飘落。
interface Flake { x: number; y: number; r: number; vy: number; ph: number; fq: number; amp: number; o: number; rank: number }
const make = (n: number, seed: number, r0: number, r1: number, v0: number, v1: number): Flake[] => {
  const r = rng(seed);
  return Array.from({length: n}, (_, i) => ({
    x: r() * W, y: r() * (H + 40), r: r0 + r() * (r1 - r0), vy: v0 + r() * (v1 - v0),
    ph: r() * 6.28, fq: 0.25 + r() * 0.5, amp: 10 + r() * 26, o: 0.55 + r() * 0.4, rank: i / n,
  }));
};
const layers = [make(110, 7, 1.2, 2.2, 28, 46), make(80, 8, 2, 3.4, 48, 74), make(34, 9, 3.6, 6.4, 78, 118)];
const mix = (a: [number, number, number], b: [number, number, number], k: number) => a.map((v, i) => Math.round(v + (b[i] - v) * k));

/** amount：0~1 雪量；horizon：地平线 y，雪花飘到雪地上时染成淡淡的蓝灰，才看得见 */
export const Snowfall: React.FC<{amount?: number; wind?: number; horizon?: number; t0?: number; groundTint?: boolean}> = ({amount = 1, wind = 0, horizon = 620, t0 = 0, groundTint = true}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const items = useMemo(() => layers, []);
  const white: [number, number, number] = [246, 249, 255];
  const grey: [number, number, number] = [150, 168, 208];
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>
      {items.map((L, li) =>
        L.map((f, i) => {
          if (f.rank > amount) return null;
          const y = (((f.y + f.vy * t) % (H + 40)) + H + 40) % (H + 40) - 20;
          const x = (((f.x + Math.sin(t * f.fq + f.ph) * f.amp + wind * t * (14 + li * 12)) % (W + 60)) + W + 60) % (W + 60) - 30;
          const k = groundTint ? Math.max(0, Math.min(1, (y - horizon + 30) / 120)) : 0;
          const [cr, cg, cb] = mix(white, grey, k * (li === 2 ? 0.7 : 1));
          const op = f.o * (k > 0 ? 0.62 + 0.3 * (1 - k) : 1);
          return li === 2 ? (
            <circle key={`${li}-${i}`} cx={x} cy={y} r={f.r * 1.9} fill="url(#flakeG)" opacity={op * 0.85} style={{mixBlendMode: k > 0.5 ? 'normal' : 'normal'}} />
          ) : (
            <circle key={`${li}-${i}`} cx={x} cy={y} r={f.r} fill={`rgb(${cr},${cg},${cb})`} opacity={op} />
          );
        }),
      )}
    </svg>
  );
};
