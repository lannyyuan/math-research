import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {GroundShadow} from '../fx/Sprite';
import {Hazel, Bud} from './cast';
import {Bg, SceneWrap, useT, ramp, at} from './kit';

// 一、平安夜的早晨，海边的小村子在下雪：Hazel 和 Bud 站在坡上望着海湾；镜头慢慢摇向海面（爸爸的小船又小又远），最后停在对岸暗着的灯塔上
export const S1: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(980, 540, 1.0)},
    {t: 8, ...at(1060, 540, 1.02)},
    {t: 16, ...at(1280, 530, 1.05)},
    {t: 22, ...at(1470, 520, 1.07)},
    {t: len, ...at(1500, 520, 1.09)},
  ]);
  const gloom = 0.1 + 0.2 * ramp(t, 4, 24); // 暴风雪要来了：天色一点点沉下去
  return (
    <SceneWrap len={len} bg="#8fa2c2">
      <Stage cam={cam}>
        <Layer p={0.6}>
          <Bg src="s1_far.jpg" w={2900} h={1080} />
        </Layer>
        <Layer p={1}>
          <Bg src="s1_near.png" w={2900} h={1080} />
          <GroundShadow x={1130} y={900} rx={100} />
          <GroundShadow x={1020} y={906} rx={90} />
          <Bud x={1020} y={906} s={0.68} head="cap" t0={0.6} />
          <Hazel x={1130} y={900} s={0.72} t0={1} />
        </Layer>
      </Stage>
      <div style={{position: 'absolute', inset: 0, background: `linear-gradient(rgba(36,52,96,${gloom}), rgba(36,52,96,${gloom * 0.4}))`, pointerEvents: 'none'}} />
      <Snow amount={0.55 + 0.4 * ramp(t, 2, 22)} wind={0.12} />
    </SceneWrap>
  );
};
