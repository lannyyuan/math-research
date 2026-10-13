import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

/** 那盏灯：全片唯一会发光的暖色。一闪一闪，缓缓呼吸。r 为灯芯半径（像素） */
export const LampGlow: React.FC<{x: number; y: number; r?: number; glow?: number; t0?: number; rays?: boolean}> = ({x, y, r = 8, glow = 1, t0 = 0, rays = true}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const tw = 0.74 + 0.26 * Math.pow(Math.sin(t * 2.2), 2) + 0.05 * Math.sin(t * 9.1);
  const br = 0.94 + 0.06 * Math.sin(t * 1.3);
  const a = glow * tw;
  return (
    <g transform={`translate(${x} ${y})`}>
      <circle r={r * 15 * br} fill="url(#lampHalo)" opacity={a * 0.9} />
      <circle r={r * 5.2 * br} fill="url(#lampMid)" opacity={a} />
      {rays ? (
        <g opacity={a * 0.85} transform={`rotate(${Math.sin(t * 0.7) * 6})`}>
          <rect x={-r * 9} y={-r * 0.34} width={r * 18} height={r * 0.68} fill="url(#lampRayH)" />
          <rect x={-r * 0.34} y={-r * 9} width={r * 0.68} height={r * 18} fill="url(#lampRayH)" transform="rotate(90)" />
        </g>
      ) : null}
      <circle r={r * 1.9} fill="url(#lampCore)" opacity={Math.min(1, a * 1.1)} />
    </g>
  );
};
