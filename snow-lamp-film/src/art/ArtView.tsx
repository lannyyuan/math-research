import React from 'react';
import {C} from '../palette';
import type {Art} from './ink';

export type Built = ReturnType<Art['build']>;

/** 全片共用的 SVG 滤镜（放在画面里一次即可） */
export const Defs: React.FC = () => (
  <svg width={0} height={0} style={{position: 'absolute'}} aria-hidden>
    <defs>
      {/* 水彩平涂（底色：颗粒很轻，保持不透明；ws：阴影层，颗粒重、边缘积色明显） */}
      {[0, 1, 2].map((v) => (
        <React.Fragment key={v}>
          {[false, true].map((shade) => (
            <filter key={String(shade)} id={`${shade ? 'ws' : 'wc'}${v}`} x="-12%" y="-12%" width="124%" height="124%" colorInterpolationFilters="sRGB">
              <feTurbulence type="fractalNoise" baseFrequency={0.016 + v * 0.007} numOctaves={2} seed={11 + v * 9} result="warp" />
              <feDisplacementMap in="SourceGraphic" in2="warp" scale={9 + v * 2} xChannelSelector="R" yChannelSelector="G" result="shape" />
              <feTurbulence type="fractalNoise" baseFrequency={shade ? 0.3 : 0.2} numOctaves={2} seed={5 + v} result="grain" />
              <feColorMatrix in="grain" type="matrix" values={shade ? '0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.7 0 0 0 0.52' : '0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.25 0 0 0 0.9'} result="grainA" />
              <feComposite in="shape" in2="grainA" operator="in" result="tex" />
              <feMorphology in="shape" operator="erode" radius={shade ? 2.2 : 1.4} result="inner" />
              <feComposite in="shape" in2="inner" operator="out" result="rim" />
              <feColorMatrix in="rim" type="matrix" values={`0.72 0 0 0 0  0 0.74 0 0 0  0 0 0.86 0 0  0 0 0 ${shade ? 0.55 : 0.42} 0`} result="rimDark" />
              <feMerge>
                <feMergeNode in="tex" />
                <feMergeNode in="rimDark" />
              </feMerge>
            </filter>
          ))}
        </React.Fragment>
      ))}
      {/* 墨线边缘微微毛糙，像墨水洇在纸上 */}
      <filter id="inkRough" x="-5%" y="-5%" width="110%" height="110%">
        <feTurbulence type="fractalNoise" baseFrequency={0.55} numOctaves={2} seed={3} result="n" />
        <feDisplacementMap in="SourceGraphic" in2="n" scale={1.7} xChannelSelector="R" yChannelSelector="G" />
      </filter>
      {/* 灯光：全片唯一发光的暖色 */}
      <radialGradient id="lampHalo">
        <stop offset="0" stopColor="#ffcb62" stopOpacity={0.5} />
        <stop offset="0.35" stopColor="#ff9d3a" stopOpacity={0.2} />
        <stop offset="1" stopColor="#ff9d3a" stopOpacity={0} />
      </radialGradient>
      <radialGradient id="lampMid">
        <stop offset="0" stopColor="#ffe9a8" stopOpacity={0.95} />
        <stop offset="0.45" stopColor="#ffcb62" stopOpacity={0.55} />
        <stop offset="1" stopColor="#ffcb62" stopOpacity={0} />
      </radialGradient>
      <radialGradient id="lampCore">
        <stop offset="0" stopColor="#fffbe6" stopOpacity={1} />
        <stop offset="0.55" stopColor="#fff0b8" stopOpacity={0.95} />
        <stop offset="1" stopColor="#ffe08a" stopOpacity={0} />
      </radialGradient>
      <linearGradient id="lampRayH" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0" stopColor="#ffe9a8" stopOpacity={0} />
        <stop offset="0.5" stopColor="#fff6d0" stopOpacity={0.9} />
        <stop offset="1" stopColor="#ffe9a8" stopOpacity={0} />
      </linearGradient>
      <radialGradient id="fireGlow">
        <stop offset="0" stopColor="#ff9f40" stopOpacity={0.34} />
        <stop offset="0.5" stopColor="#ff9f40" stopOpacity={0.1} />
        <stop offset="1" stopColor="#ff9f40" stopOpacity={0} />
      </radialGradient>
      <radialGradient id="shadowG">
        <stop offset="0" stopColor="#5f74a8" stopOpacity={0.5} />
        <stop offset="0.6" stopColor="#6b80b4" stopOpacity={0.25} />
        <stop offset="1" stopColor="#6b80b4" stopOpacity={0} />
      </radialGradient>
      <radialGradient id="mistG">
        <stop offset="0" stopColor="#dfe9fb" stopOpacity={0.85} />
        <stop offset="0.55" stopColor="#c6d6f2" stopOpacity={0.45} />
        <stop offset="1" stopColor="#c6d6f2" stopOpacity={0} />
      </radialGradient>
      <radialGradient id="flakeG">
        <stop offset="0" stopColor="#ffffff" stopOpacity={0.95} />
        <stop offset="0.6" stopColor="#f2f6ff" stopOpacity={0.7} />
        <stop offset="1" stopColor="#f2f6ff" stopOpacity={0} />
      </radialGradient>
      {/* 大块、较软的水彩（雪堆、远山等） */}
      <filter id="wcSoft" x="-10%" y="-10%" width="120%" height="120%" colorInterpolationFilters="sRGB">
        <feTurbulence type="fractalNoise" baseFrequency={0.01} numOctaves={3} seed={4} result="warp" />
        <feDisplacementMap in="SourceGraphic" in2="warp" scale={24} xChannelSelector="R" yChannelSelector="G" result="shape" />
        <feGaussianBlur in="shape" stdDeviation={1.2} />
      </filter>
    </defs>
  </svg>
);

interface Props {
  a: Built;
  dx?: number; // 颜色溢出线外的偏移
  dy?: number;
  filter?: string;
  inkColor?: string;
  sk?: number; // 辅助线浓度
  fillOpacity?: number;
}

/** 渲染一块手绘图形：水彩（偏移）→ 辅助线 → 墨线 */
export const ArtView: React.FC<Props> = ({a, dx = 3.5, dy = 3, filter = 'wc0', inkColor = C.ink, sk = 0.5, fillOpacity = 1}) => {
  const base = a.fills.filter((f) => !f.shade);
  const shades = a.fills.filter((f) => f.shade);
  const sf = filter.replace('wc', 'ws');
  return (
    <g>
      <g filter={`url(#${filter})`} transform={`translate(${dx} ${dy})`} opacity={fillOpacity}>
        {base.map((f, i) => (
          <path key={i} d={f.d} fill={f.color} opacity={f.opacity ?? 1} />
        ))}
      </g>
      {shades.length ? (
        <g filter={`url(#${sf})`} transform={`translate(${dx * 0.6} ${dy * 0.6})`} opacity={fillOpacity}>
          {shades.map((f, i) => (
            <path key={i} d={f.d} fill={f.color} opacity={f.opacity ?? 1} />
          ))}
        </g>
      ) : null}
      {a.sketch ? <path d={a.sketch} fill={C.graphite} opacity={sk} /> : null}
      <path d={a.ink} fill={inkColor} filter="url(#inkRough)" />
    </g>
  );
};
