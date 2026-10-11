import React from 'react';
import {WARM} from '../palette';

/** 柔和的暖色光晕（灯、窗、船灯、Bolts 的眼睛）。混合模式 screen，像光一样叠加。 */
export const Glow: React.FC<{x: number; y: number; r: number; opacity?: number; color?: string; core?: boolean}> = ({x, y, r, opacity = 1, color = WARM.mid, core = true}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity, mixBlendMode: 'screen', pointerEvents: 'none', background: `radial-gradient(circle at center, ${core ? '#fff6d2' : color} 0%, ${color} ${core ? 12 : 4}%, rgba(255,200,100,0.35) 30%, rgba(255,190,90,0.10) 55%, rgba(255,190,90,0) 72%)`}} />
);

/**
 * 灯塔的光柱：从 (x, y) 出发、朝 angle（度，0=向右）方向扩散的楔形光；length 光柱长度，spread 张角（度）。
 * 光柱是全片最亮的地方：中心近白，边缘渐隐成暖黄。
 */
export const Beam: React.FC<{x: number; y: number; angle: number; length?: number; spread?: number; opacity?: number; width?: number}> = ({x, y, angle, length = 1700, spread = 9, opacity = 1, width}) => {
  const half = (spread * Math.PI) / 360;
  const w = width ?? Math.tan(half) * length * 2;
  return (
    <div style={{position: 'absolute', left: x, top: y - w / 2, width: length, height: w, transformOrigin: '0 50%', transform: `rotate(${angle}deg)`, opacity, mixBlendMode: 'screen', pointerEvents: 'none'}}>
      <svg width={length} height={w} viewBox={`0 0 ${length} ${w}`} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
        <defs>
          <linearGradient id="beamL" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stopColor="#fff8dc" stopOpacity={0.95} />
            <stop offset="0.25" stopColor="#ffe9a0" stopOpacity={0.62} />
            <stop offset="0.7" stopColor="#ffd978" stopOpacity={0.28} />
            <stop offset="1" stopColor="#ffd978" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="beamV" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor="#000" stopOpacity={1} />
            <stop offset="0.5" stopColor="#fff" stopOpacity={1} />
            <stop offset="1" stopColor="#000" stopOpacity={1} />
          </linearGradient>
          <mask id="beamMask"><rect width={length} height={w} fill="url(#beamV)" /></mask>
          <filter id="beamBlur"><feGaussianBlur stdDeviation={Math.max(w * 0.04, 3)} /></filter>
        </defs>
        <g filter="url(#beamBlur)"><polygon points={`0,${w / 2 - 6} ${length},0 ${length},${w} 0,${w / 2 + 6}`} fill="url(#beamL)" mask="url(#beamMask)" /></g>
      </svg>
    </div>
  );
};

/** 冷白色的光（农舍的窗、床头灯、走廊的光）：同样是柔和的径向光晕，但偏冰蓝，不是暖色 */
export const CoolGlow: React.FC<{x: number; y: number; r: number; opacity?: number}> = ({x, y, r, opacity = 1}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity, mixBlendMode: 'screen', pointerEvents: 'none', background: 'radial-gradient(circle at center, #f4faff 0%, #d3e6ff 14%, rgba(170,205,250,0.38) 34%, rgba(150,190,245,0.12) 58%, rgba(150,190,245,0) 72%)'}} />
);

/** 亮着的窗（冷白）：一块发亮的小矩形 + 一圈光晕 */
export const LitWindow: React.FC<{x: number; y: number; w: number; h: number; opacity?: number}> = ({x, y, w, h, opacity = 1}) => (
  <div style={{position: 'absolute', left: x - w / 2, top: y - h / 2, width: w, height: h, opacity, background: '#f4faff', mixBlendMode: 'screen', boxShadow: '0 0 70px 36px rgba(180,215,255,0.55), 0 0 160px 80px rgba(150,190,245,0.25)', pointerEvents: 'none'}} />
);
