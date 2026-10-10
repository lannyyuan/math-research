import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Backdrop, SceneWrap, FrameTrees, mountLamp, useT, ramp} from './kit';
import timeline from '../timeline.json';

// 片头：山顶的灯在远处一闪一闪，雪缓缓落下，题目浮现
export const S0: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([{t: 0, x: 0, y: 40, z: 1}, {t: 5, x: 0, y: 10, z: 1.06}]);
  const lamp = mountLamp(960, 800, 0.56);
  const o = ramp(t, 0.8, 2.2) * (1 - ramp(t, 4.0, 4.9));
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop horizon={700} mount={{cx: 960, k: 0.56, baseY: 800}} />
        <Layer p={0.16}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={6} glow={0.5 + 0.5 * ramp(t, 0, 2)} />
          </svg>
        </Layer>
        <FrameTrees />
      </Stage>
      <Snowfall horizon={700} />
      <div style={{position: 'absolute', left: 0, top: 150, width: 1920, textAlign: 'center', opacity: o, fontFamily: 'WenKaiSub, serif', fontSize: 148, letterSpacing: 26, color: '#eef3ff', textShadow: '0 0 36px rgba(160,190,255,0.45), 0 3px 10px rgba(5,8,28,0.6)'}}>
        {timeline.title}
      </div>
    </SceneWrap>
  );
};
