import React from 'react';

/**
 * 天上那盏灯亮起来：像碗、像盆、像车轮，最后亮得人睁不开眼。
 * 全部是 mix-blend screen 的柔光（宝珠的灰金 #F3D98A，核心近白），不闪白——亮度被压在 0.93 以下。
 * k: 0~1 的总进度；stage 由它分段：碗(0~.28) → 盆(.28~.58) → 车轮(.58~.85) → 满天(.85~1)
 */
const seg = (k: number, a: number, b: number) => Math.max(0, Math.min(1, (k - a) / (b - a)));
export const LampLight: React.FC<{x: number; y: number; k: number; t: number; w?: number; h?: number}> = ({x, y, k, t, w = 2900, h = 1080}) => {
  if (k <= 0.001) return null;
  const bowl = seg(k, 0, 0.28), basin = seg(k, 0.26, 0.58), wheel = seg(k, 0.56, 0.86), all = seg(k, 0.84, 1);
  const flick = 1 + 0.03 * Math.sin(t * 11) + 0.02 * Math.sin(t * 17.3);
  const R_bowl = 60 + 150 * bowl, R_basin = 150 + 260 * basin, R_wheel = 300 + 330 * wheel, R_all = 700 + 1900 * all;
  const glow = (r: number, o: number, key: string, flat = 1) => (
    <div key={key} style={{position: 'absolute', left: x - r, top: y - r * flat, width: r * 2, height: r * 2 * flat, borderRadius: '50%', opacity: Math.min(o, 0.93), mixBlendMode: 'screen', pointerEvents: 'none',
      background: 'radial-gradient(ellipse at center, rgba(255,251,236,0.95) 0%, rgba(243,217,138,0.6) 14%, rgba(236,214,150,0.28) 38%, rgba(230,212,160,0.1) 62%, rgba(230,212,160,0) 78%)'}} />
  );
  // 车轮：放射的细光条（旋转的辐条）
  const spokes = Array.from({length: 16}, (_, i) => i);
  return (
    <>
      {all > 0 && glow(R_all, 0.55 * all * flick, 'all')}
      {wheel > 0 && glow(R_wheel, 0.75 * wheel * flick, 'wheel')}
      {wheel > 0 && (
        <svg width={w} height={h} style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'screen', pointerEvents: 'none', opacity: 0.55 * wheel * (1 - all * 0.7)}}>
          <g transform={`translate(${x} ${y}) rotate(${t * 6})`}>
            <circle r={R_wheel * 0.62} fill="none" stroke="#f5e6b0" strokeWidth={3} opacity={0.6} />
            <circle r={R_wheel * 0.4} fill="none" stroke="#f5e6b0" strokeWidth={2} opacity={0.5} />
            {spokes.map((i) => <line key={i} x1={0} y1={0} x2={R_wheel * 0.66 * Math.cos((i * Math.PI) / 8)} y2={R_wheel * 0.66 * Math.sin((i * Math.PI) / 8)} stroke="#f5e6b0" strokeWidth={2} opacity={0.5} />)}
          </g>
        </svg>
      )}
      {basin > 0 && glow(R_basin, 0.85 * basin * flick, 'basin', 0.78)}
      {bowl > 0 && glow(R_bowl, 0.95 * bowl * flick, 'bowl', 0.62)}
    </>
  );
};
