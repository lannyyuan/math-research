import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art, type P} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {C} from '../palette';

/** 小溪：从远处蜿蜒而来，越近越宽，水面有一闪一闪的亮光在流动 */
export const Stream: React.FC<{pts: P[]; widths: number[]; reveal: number}> = ({pts, widths, reveal}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1]}`).join('');
  const n = pts.length;
  const segs = pts.slice(0, -1).map((p, i) => ({a: p, b: pts[i + 1], w: widths[i]}));
  return (
    <g opacity={reveal}>
      {segs.map((s, i) => (
        <line key={i} x1={s.a[0]} y1={s.a[1]} x2={s.b[0]} y2={s.b[1]} stroke="#7fa9d8" strokeWidth={s.w * reveal} strokeLinecap="round" opacity={0.95} />
      ))}
      {segs.map((s, i) => (
        <line key={`h${i}`} x1={s.a[0]} y1={s.a[1] - s.w * 0.12} x2={s.b[0]} y2={s.b[1] - s.w * 0.12} stroke="#d7eafb" strokeWidth={s.w * 0.45 * reveal} strokeLinecap="round" opacity={0.7} />
      ))}
      <path d={d} fill="none" stroke="#ffffff" strokeWidth={3} strokeLinecap="round" strokeDasharray="14 46" strokeDashoffset={-t * 60} opacity={0.85} />
      <path d={d} fill="none" stroke="#ffffff" strokeWidth={2} strokeLinecap="round" strokeDasharray="8 70" strokeDashoffset={-t * 38 - 30} opacity={0.7} transform="translate(0 6)" />
      <circle cx={pts[n - 1][0]} cy={pts[n - 1][1]} r={1} fill="none" />
    </g>
  );
};

/** 大雁：一字/人字形，翅膀一扇一扇 */
export const Geese: React.FC<{x: number; y: number; s?: number; speed?: number; t0?: number}> = ({x, y, s = 1, speed = 70, t0 = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const offs: P[] = [[0, 0], [-46, 20], [-46, -20], [-92, 40], [-92, -40], [-138, 60], [-138, -60]];
  return (
    <g transform={`translate(${x + speed * t} ${y + Math.sin(t * 0.5) * 6}) scale(${s})`}>
      {offs.map(([ox, oy], i) => {
        const flap = Math.sin(t * 5 + i * 0.7) * 26;
        return (
          <g key={i} transform={`translate(${ox} ${oy + Math.sin(t * 2 + i) * 3})`} fill="#2a3d76" opacity={0.88}>
            <path d="M-4 0C8 -2 18 2 24 6C14 4 4 4 -4 3Z" />
            <g transform={`rotate(${-flap} 0 0)`}><path d="M0 0C-4 -14 -10 -20 -22 -24C-14 -14 -10 -6 -6 2Z" /></g>
            <g transform={`rotate(${flap * 0.6} 0 0)`}><path d="M0 0C-2 12 -8 18 -18 20C-12 12 -8 6 -4 0Z" opacity={0.7} /></g>
          </g>
        );
      })}
    </g>
  );
};

/** 小石头脱下来的棉衣：搭在鹿背上（局部坐标：以鹿背中心为原点） */
const buildJacket = () => {
  const a = new Art(401);
  a.shape([[-60, -6], [-30, -22], [10, -24], [50, -8], [62, 20], [56, 56], [40, 70], [10, 74], [-20, 72], [-46, 64], [-62, 30]], C.jacket, {w: 3, sk: 1, wobble: 1.4});
  a.shade([[-62, 28], [-46, 64], [-20, 72], [10, 74], [40, 70], [20, 50], [-20, 46]], 0.4, '#1d2760');
  a.line([[-56, 18], [-10, 22], [56, 16]], {w: 1.5, taper: 0.8, broken: 0.2});
  a.line([[-56, 44], [0, 48], [58, 42]], {w: 1.5, taper: 0.8, broken: 0.2});
  a.line([[0, -20], [0, 72]], {w: 1.4, taper: 0.6});
  // 两只袖子垂在两侧
  a.shape([[-62, 6], [-86, 34], [-90, 70], [-70, 74], [-58, 40]], C.jacket, {w: 2.6});
  a.shape([[62, 6], [86, 34], [90, 70], [70, 74], [58, 40]], C.jacketShade, {w: 2.6});
  return a.build();
};
export const JacketDrape: React.FC<{x?: number; y?: number; s?: number; rot?: number}> = ({x = 0, y = 0, s = 1, rot = 0}) => {
  const A = useMemo(buildJacket, []);
  return (
    <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`}>
      <ArtView a={A} filter="wc1" />
    </g>
  );
};
