import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
import {Art, ink} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {C} from '../palette';
import type {P} from '../art/ink';

/** 角色脚下的蓝灰影子 */
export const GroundShadow: React.FC<{x: number; y: number; rx: number; ry?: number; o?: number}> = ({x, y, rx, ry, o = 1}) => (
  <ellipse cx={x} cy={y} rx={rx} ry={ry ?? rx * 0.14} fill="url(#shadowG)" opacity={o} />
);

/** 脚印：一对一对的小椭圆，雪慢慢把它们盖住（age 0→1 变淡） */
export const Footprints: React.FC<{pts: [number, number][]; s?: number; fade?: number}> = ({pts, s = 1, fade = 0}) => (
  <g opacity={1 - fade}>
    {pts.map(([x, y], i) => (
      <g key={i} transform={`translate(${x} ${y}) scale(${s})`}>
        <ellipse cx={0} cy={0} rx={13} ry={4.2} fill={C.snowDeep} opacity={0.55} />
        <ellipse cx={-1} cy={-1} rx={11} ry={3} fill={C.snowLit} opacity={0.65} />
      </g>
    ))}
  </g>
);

/** 呼出的白气：冷夜里每个角色嘴边一小团 */
export const BreathPuff: React.FC<{x: number; y: number; t0?: number; s?: number; dir?: number; color?: string}> = ({x, y, t0 = 0, s = 1, dir = 1, color = '#e9f0ff'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const u = (t % 3.2) / 3.2;
  const o = interpolate(u, [0, 0.15, 1], [0, 0.55, 0]);
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} opacity={o}>
      <ellipse cx={dir * u * 34} cy={-u * 20} rx={6 + u * 18} ry={4 + u * 12} fill={color} />
      <ellipse cx={dir * (u * 22 + 10)} cy={-u * 12 - 4} rx={4 + u * 10} ry={3 + u * 7} fill={color} />
    </g>
  );
};

/** 手绘的问号（问号兔子的标志，用墨线画，不是字体） */
const qBuilt = (() => {
  const a = new Art(111);
  a.line([[-10, -20], [-6, -34], [8, -38], [18, -28], [14, -14], [2, -6], [0, 6]], {w: 4.4, taper: 0.5, broken: 0});
  a.fill([[-4, 16], [4, 14], [6, 22], [-2, 24]], C.ink, 1);
  a.fill([[-4, 16], [4, 14], [6, 22], [-2, 24]], C.ink, 1);
  return a.build();
})();
export const QuestionMark: React.FC<{x: number; y: number; s?: number; age: number; rot?: number}> = ({x, y, s = 1, age, rot = 0}) => {
  const o = interpolate(age, [0, 0.12, 0.7, 1], [0, 1, 0.85, 0]);
  const rise = age * 70;
  return (
    <g transform={`translate(${x + Math.sin(age * 6) * 8} ${y - rise}) rotate(${rot}) scale(${s * (0.6 + age * 0.5)})`} opacity={o}>
      <path d={qBuilt.ink} fill="#e9f0ff" stroke="#e9f0ff" strokeWidth={0.5} />
      <path d={qBuilt.ink} fill={C.inkSoft} opacity={0.0} />
    </g>
  );
};
export const _unused = ink;

/** 雪堆：白色水彩 + 蓝灰阴影，几笔断断续续的墨线 */
export const Mound: React.FC<{x: number; y: number; w?: number; h?: number; seed?: number}> = ({x, y, w = 260, h = 76, seed = 1}) => {
  const A = useMemo(() => {
    const a = new Art(200 + seed);
    a.fill([[-w / 2, 0], [-w * 0.36, -h * 0.55], [-w * 0.1, -h * 0.95], [w * 0.14, -h], [w * 0.38, -h * 0.5], [w / 2, 0], [0, h * 0.12]], '#f9fbff', 1);
    a.shade([[-w / 2, 0], [-w * 0.3, -h * 0.2], [0, -h * 0.12], [w * 0.3, -h * 0.2], [w / 2, 0], [0, h * 0.12]], 0.4);
    a.line([[-w * 0.34, -h * 0.55], [-w * 0.1, -h * 0.92], [w * 0.14, -h * 0.96], [w * 0.34, -h * 0.55]], {w: 2.2, broken: 0.35, taper: 0.8, sk: 1});
    return a.build();
  }, [w, h, seed]);
  return (
    <g transform={`translate(${x} ${y})`}>
      <ArtView a={A} filter="wc1" />
    </g>
  );
};

/** 雪雾：几团大而软的蓝白色雾，缓缓飘 */
export const Mist: React.FC<{items: {x: number; y: number; rx: number; ry: number; o?: number}[]; t: number; opacity?: number}> = ({items, t, opacity = 1}) => (
  <g opacity={opacity}>
    {items.map((m, i) => (
      <ellipse key={i} cx={m.x + Math.sin(t * 0.25 + i) * 40} cy={m.y + Math.sin(t * 0.18 + i * 2) * 8} rx={m.rx} ry={m.ry} fill="url(#mistG)" opacity={m.o ?? 1} />
    ))}
  </g>
);

/** 冰上的裂纹：从中心向四周辐射，带分叉。用椭圆裁剪随时间“长出来” */
const crackPaths = (() => {
  const a = new Art(333);
  const arms: P2[][] = [
    [[0, 0], [60, -4], [130, 2], [210, -6]],
    [[0, 0], [-70, 6], [-140, -2], [-230, 8]],
    [[0, 0], [30, 10], [80, 22], [120, 30]],
    [[0, 0], [-40, 12], [-90, 26], [-130, 34]],
    [[0, 0], [20, -12], [60, -26], [90, -38]],
    [[0, 0], [-30, -10], [-70, -24], [-110, -34]],
    [[70, -2], [100, 14], [150, 24]],
    [[-90, 2], [-120, -14], [-170, -22]],
    [[130, 2], [160, -16], [200, -24]],
  ];
  for (const arm of arms) a.line(arm as P[], {w: 2.4, taper: 0.4, broken: 0.1, wobble: 2});
  return a.build();
})();
type P2 = [number, number];
export const IceCracks: React.FC<{x: number; y: number; reveal: number; s?: number}> = ({x, y, reveal, s = 1}) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <defs>
      <clipPath id="crackClip"><ellipse cx={0} cy={0} rx={Math.max(1, 240 * reveal)} ry={Math.max(1, 60 * reveal)} /></clipPath>
    </defs>
    <g clipPath="url(#crackClip)">
      <path d={crackPaths.ink} fill="#f6fbff" opacity={0.9} transform="translate(1.5 2)" />
      <path d={crackPaths.ink} fill="#456a9e" opacity={0.9} />
    </g>
  </g>
);

/** 冰窟窿：深蓝的水、碎冰边、一圈圈波纹 */
export const WaterHole: React.FC<{x: number; y: number; open: number; t: number; rx?: number}> = ({x, y, open, t, rx = 112}) => {
  const k = open;
  if (k <= 0.01) return null;
  return (
    <g transform={`translate(${x} ${y})`}>
      <ellipse cx={0} cy={0} rx={rx * k + 14} ry={(rx * 0.24) * k + 5} fill="#e9f3fc" opacity={0.9} />
      <ellipse cx={0} cy={0} rx={rx * k} ry={rx * 0.24 * k} fill="#2e5192" />
      <ellipse cx={0} cy={2} rx={rx * k * 0.78} ry={rx * 0.17 * k} fill="#223f7a" opacity={0.9} />
      {[0, 1, 2].map((i) => {
        const u = ((t * 0.55 + i / 3) % 1);
        return <ellipse key={i} cx={0} cy={2} rx={rx * k * (0.5 + u * 0.7)} ry={rx * 0.22 * k * (0.5 + u * 0.7)} fill="none" stroke="#e8f2ff" strokeWidth={2.4} opacity={(1 - u) * 0.8} />;
      })}
    </g>
  );
};

/** 碎冰与水花：一瞬间向上溅起，慢慢落下 */
export const Splash: React.FC<{x: number; y: number; age: number}> = ({x, y, age}) => {
  if (age <= 0 || age >= 1) return null;
  const shards = [[-60, 90], [-30, 120], [10, 140], [40, 110], [70, 80], [-80, 60], [90, 50]];
  return (
    <g transform={`translate(${x} ${y})`} opacity={1 - age}>
      {shards.map(([vx, vy], i) => {
        const px = vx * age * 1.2, py = -(vy * age - 150 * age * age);
        return <polygon key={i} points="0,-6 8,4 -7,5" transform={`translate(${px} ${py}) rotate(${age * 240 + i * 50})`} fill="#f3f9ff" stroke="#6c8fc4" strokeWidth={1.4} />;
      })}
      {[0, 1, 2, 3, 4].map((i) => (
        <circle key={i} cx={(i - 2) * 22 * (0.6 + age)} cy={-30 * Math.sin(age * 3) - i * 3} r={5 - age * 3} fill="#dcecff" opacity={0.85} />
      ))}
    </g>
  );
};
