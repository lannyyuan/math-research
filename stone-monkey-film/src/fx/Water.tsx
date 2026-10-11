import React, {useContext} from 'react';
import {CharsCtx} from './Variant';

const rng = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

/** 水面的涟漪：一圈圈向外扩的椭圆线。p: 0~1 进度（外部给），n 圈 */
export const Ripple: React.FC<{x: number; y: number; r: number; p: number; n?: number; color?: string; flat?: number; o?: number}> = ({x, y, r, p, n = 3, color = '#dfe6ec', flat = 0.2, o = 1}) => {
  if (p <= 0 || p >= 1) return null;
  return (
    <svg width={2900} height={1500} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', overflow: 'visible'}}>
      {Array.from({length: n}, (_, i) => {
        const q = Math.max(0, Math.min(1, p * 1.25 - i * 0.18));
        if (q <= 0 || q >= 1) return null;
        const rx = r * (0.15 + q * 0.85);
        return <ellipse key={i} cx={x} cy={y} rx={rx} ry={rx * flat} fill="none" stroke={color} strokeWidth={2.4 * (1 - q) + 0.6} opacity={o * (1 - q) * 0.9} />;
      })}
    </svg>
  );
};

/** 水花：n 颗水珠按抛物线飞出去再落下。t: 自触发起的秒数 */
export const Splash: React.FC<{x: number; y: number; t: number; n?: number; power?: number; seed?: number; color?: string; size?: number}> = ({x, y, t, n = 22, power = 1, seed = 3, color = '#e8eef2', size = 1}) => {
  const show = useContext(CharsCtx) >= 2;
  if (!show || t <= 0 || t > 2.4) return null;
  const r = rng(seed);
  return (
    <svg width={2900} height={1500} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', overflow: 'visible'}}>
      {Array.from({length: n}, (_, i) => {
        const a = (-Math.PI / 2) + (r() - 0.5) * 1.5;
        const v = (260 + r() * 360) * power;
        const px = x + Math.cos(a) * v * t, py = y + Math.sin(a) * v * t + 0.5 * 900 * t * t;
        const rad = (2 + r() * 4.5) * size * (1 - t / 3);
        const o = Math.max(0, 1 - t / 2.2);
        return <circle key={i} cx={px} cy={py} r={Math.max(rad, 0.5)} fill={color} opacity={0.85 * o} />;
      })}
    </svg>
  );
};

/** 水泡：往上冒，轻轻晃 */
export const Bubbles: React.FC<{x: number; y: number; t: number; n?: number; spread?: number; rise?: number; seed?: number; o?: number}> = ({x, y, t, n = 14, spread = 120, rise = 360, seed = 5, o = 1}) => {
  const show = useContext(CharsCtx) >= 2;
  if (!show) return null;
  const r = rng(seed);
  return (
    <svg width={2900} height={1500} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', overflow: 'visible'}}>
      {Array.from({length: n}, (_, i) => {
        const bx = x + (r() - 0.5) * spread, ph = r() * 6, sp = 0.5 + r() * 0.7, rad = 2 + r() * 5, d = r() * 2.6;
        const u = ((t * sp + d) % 2.6) / 2.6;
        return <circle key={i} cx={bx + Math.sin(t * 2 + ph) * 6} cy={y - u * rise} r={rad} fill="none" stroke="#e2eaf0" strokeWidth={1.4} opacity={o * 0.7 * Math.sin(Math.PI * u)} />;
      })}
    </svg>
  );
};

/** 水的面纱：盖在“水里的东西”上面，只留一点轮廓和眼睛的光（水底一双大眼） */
export const WaterVeil: React.FC<{y0: number; y1: number; o?: number; color?: string}> = ({y0, y1, o = 0.55, color = '10,20,40'}) => (
  <div style={{position: 'absolute', left: 0, top: y0, width: 2900, height: y1 - y0, background: `linear-gradient(to bottom, rgba(${color},${o * 0.85}) 0%, rgba(${color},${o}) 100%)`, pointerEvents: 'none'}} />
);
