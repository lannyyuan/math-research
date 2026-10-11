import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {Boy} from '../chars/Boy';
import {LampGlow} from './Lamp';
import {C} from '../palette';

// 小石头心里的家：妈妈在窗边点的那盏小灯。画成一页绘本，边缘化进烟里。
const build = () => {
  const frame = new Art(301);
  frame.shape([[-78, -96], [78, -96], [78, 70], [-78, 70]], '#1f3472', {w: 3.4, sk: 1});
  frame.line([[0, -96], [0, 70]], {w: 3}).line([[-78, -14], [78, -14]], {w: 3});
  frame.line([[-90, 74], [90, 74]], {w: 5, taper: 0.3});
  const curtL = new Art(302);
  curtL.shape([[-96, -108], [-60, -108], [-52, -40], [-62, 70], [-96, 76]], '#5d78b8', {w: 2.6, sk: 1});
  curtL.line([[-84, -100], [-80, 70]], {w: 1.4, taper: 0.8}).line([[-70, -100], [-66, 60]], {w: 1.4, taper: 0.8});
  const curtR = new Art(303);
  curtR.shape([[96, -108], [60, -108], [52, -40], [62, 70], [96, 76]], '#5d78b8', {w: 2.6, sk: 1});
  curtR.line([[84, -100], [80, 70]], {w: 1.4, taper: 0.8}).line([[70, -100], [66, 60]], {w: 1.4, taper: 0.8});
  const lamp = new Art(304);
  lamp.shape([[-16, 72], [16, 72], [12, 58], [-12, 58]], '#3b4a85', {w: 2.2});
  lamp.shape([[-10, 58], [10, 58], [14, 34], [8, 24], [-8, 24], [-14, 34]], '#fff0b8', {w: 2.2, opacity: 0.9});
  return {frame: frame.build(), curtL: curtL.build(), curtR: curtR.build(), lamp: lamp.build()};
};

export const MemoryWindow: React.FC<{x: number; y: number; s?: number; appear: number; lampBoost?: number}> = ({x, y, s = 1, appear, lampBoost = 1}) => {
  const A = useMemo(build, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  if (appear <= 0.01) return null;
  const flakes = [[-50, -70, 3], [-20, -40, 2.4], [20, -76, 2.8], [46, -30, 2.2], [-40, 0, 2], [34, 6, 2.6]];
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`} opacity={appear}>
      <defs>
        <radialGradient id="memFade">
          <stop offset="0" stopColor="#fff" />
          <stop offset="0.74" stopColor="#fff" />
          <stop offset="1" stopColor="#000" />
        </radialGradient>
        <mask id="memMask"><circle r={178} fill="url(#memFade)" /></mask>
      </defs>
      <g mask="url(#memMask)">
        <circle r={178} fill="#e4ecfa" opacity={0.93} />
        <ArtView a={A.frame} filter="wc1" />
        {flakes.map(([fx, fy, r], i) => (
          <circle key={i} cx={fx + Math.sin(t * 0.8 + i) * 4} cy={fy + ((t * 12 + i * 20) % 40) - 20} r={r} fill="#f4f8ff" opacity={0.85} />
        ))}
        <ArtView a={A.curtL} filter="wc2" />
        <ArtView a={A.curtR} filter="wc2" />
        <ArtView a={A.lamp} filter="wc1" />
        <g transform="translate(0 38)">
          <LampGlow x={0} y={0} r={7} glow={0.9 * lampBoost} rays={false} />
        </g>
        <g transform="translate(-122 -96) scale(0.95)">
          <Boy variant="mom" s={0.62} flip armN={-60} head={4} wind={0} />
        </g>
      </g>
    </g>
  );
};
