import React from 'react';
import {Img, staticFile} from 'remotion';
import {W, H} from '../palette';
import {Glow} from '../fx/Light';
import {Snow} from '../fx/Snow';
import {SceneWrap, useT, lerp, ramp} from './kit';

// 片头：封面直接当书名画面（封面是竖版的，左右用封面自己虚化放大后的画面补满）。灯塔的灯在轻轻地呼吸。
const CW = 1086, CH = 1448;
export const S0: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const z = lerp(1.0, 1.05, t / len);
  const s = H / CH; // 封面按画面高度缩放
  const cw = CW * s;
  const left = (W - cw) / 2;
  const pulse = 0.82 + 0.18 * Math.sin(t * 2.6);
  return (
    <SceneWrap len={len} fadeIn={24} fadeOut={36}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: '50% 45%'}}>
        <Img src={staticFile('bg/title_fill.jpg')} style={{position: 'absolute', left: 0, top: 0, width: W, height: H}} />
        <Img src={staticFile('bg/cover.jpg')} style={{position: 'absolute', left, top: 0, width: cw, height: H, WebkitMaskImage: 'linear-gradient(90deg, transparent 0, #000 5%, #000 95%, transparent 100%)', maskImage: 'linear-gradient(90deg, transparent 0, #000 5%, #000 95%, transparent 100%)'}} />
        <Glow x={left + 785 * s} y={518 * s} r={90} opacity={0.5 * pulse * ramp(t, 0.5, 2)} />
      </div>
      <Snow amount={0.7} wind={0.06} />
    </SceneWrap>
  );
};
