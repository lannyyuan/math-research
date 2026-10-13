import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {rng} from '../art/ink';
import {C} from '../palette';

// 火堆：暖色之二。柴是炭黑的靛色，石头是冷灰蓝；火焰是平涂的橙黄，一跳一跳。
const buildBase = () => {
  const a = new Art(101);
  a.shape([[-60, 4], [-50, -16], [-6, -26], [40, -18], [62, 2], [20, 14], [-30, 14]], C.stoneDark, {w: 2.6, opacity: 0.0});
  a.shape([[-64, -4], [-40, -22], [-24, -10], [-44, 4]], C.stone, {w: 2.4, sk: 1});
  a.shape([[30, -10], [58, -20], [76, -2], [52, 8]], C.stone, {w: 2.4});
  a.shape([[-82, 4], [-66, -10], [-52, 4], [-66, 12]], '#8392bd', {w: 2.2});
  a.shape([[60, 6], [80, -4], [94, 8], [78, 16]], '#7685b2', {w: 2.2});
  const logs = new Art(102);
  logs.shape([[-52, -4], [34, -34], [42, -24], [-44, 8]], '#1d2548', {w: 2.6});
  logs.shape([[48, -6], [-30, -34], [-38, -24], [40, 6]], '#27315c', {w: 2.6});
  return {base: a.build(), logs: logs.build()};
};

const flame = (cx: number, base: number, h: number, w: number, t: number, ph: number) => {
  const sway = Math.sin(t * 7 + ph) * w * 0.18 + Math.sin(t * 3.1 + ph * 2) * w * 0.12;
  const hh = h * (0.9 + 0.1 * Math.sin(t * 9 + ph));
  const tipX = cx + sway * 1.6, tipY = base - hh;
  return `M${cx - w / 2} ${base} C${cx - w * 0.62} ${base - hh * 0.4} ${cx - w * 0.1 + sway * 0.4} ${base - hh * 0.62} ${tipX} ${tipY} C${cx + w * 0.16 + sway * 0.4} ${base - hh * 0.6} ${cx + w * 0.62} ${base - hh * 0.38} ${cx + w / 2} ${base}Z`;
};

export const Fire: React.FC<{x: number; y: number; s?: number; t0?: number; glow?: number}> = ({x, y, s = 1, t0 = 0, glow = 1}) => {
  const A = useMemo(buildBase, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const sparks = useMemo(() => {
    const r = rng(5);
    return Array.from({length: 14}, () => ({x: (r() - 0.5) * 50, ph: r() * 5, sp: 26 + r() * 30, sz: 1.2 + r() * 1.8}));
  }, []);
  const flick = 0.92 + 0.08 * Math.sin(t * 11) + 0.04 * Math.sin(t * 5.3);
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ellipse cx={0} cy={0} rx={260 * flick} ry={90 * flick} fill="url(#fireGlow)" opacity={glow} />
      <ArtView a={A.base} filter="wc1" />
      <g filter="url(#wc1)">
        <path d={flame(-4, -12, 118, 66, t, 0)} fill={C.fireOuter} opacity={0.95} />
        <path d={flame(8, -10, 92, 50, t, 1.7)} fill={C.fireMid} opacity={0.95} />
        <path d={flame(0, -8, 62, 34, t, 3.1)} fill={C.fireCore} opacity={0.98} />
      </g>
      <ArtView a={A.logs} filter="wc2" />
      {sparks.map((p, i) => {
        const u = ((t * p.sp + p.ph * 40) % 150) / 150;
        return <circle key={i} cx={p.x + Math.sin(t * 2 + p.ph) * 14 * u} cy={-30 - u * 150} r={p.sz * (1 - u * 0.6)} fill={C.fireCore} opacity={(1 - u) * 0.9} />;
      })}
    </g>
  );
};
