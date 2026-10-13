import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {GroundShadow, Footprints, BreathPuff} from '../fx/Bits';
import {Backdrop, SceneWrap, FrameTrees, mountLamp, useT, ramp, at, GY, HZ} from './kit';

// 一、雪夜迷路：一个人站在大森林里 → 回头看脚印被雪盖住 → 看见山顶的灯 → 朝着灯走
export const S1: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(930, 540, 1.0)},
    {t: 9, ...at(960, 540, 1.06)},
    {t: 11.4, ...at(1000, 530, 1.06)},
    {t: 16, ...at(1190, 360, 1.2)},
    {t: 19.5, ...at(1130, 470, 1.12)},
    {t: 24, ...at(1100, 530, 1.06)},
    {t: 30.5, ...at(1480, 540, 1.04)},
  ]);
  const MX = 1250, MB = HZ + 60, MK = 0.5;
  const lamp = mountLamp(MX, MB, MK);
  const bx0 = 520;
  const walkU = ramp(t, 23.0, 24.8);
  const bx = bx0 + (t < 23 ? 0 : 74 * (t - 23 - 0.9 * (1 - walkU)));
  const turnLeft = ramp(t, 3.2, 3.9) * (1 - ramp(t, 6.4, 7.1));
  const sx = 1 - 2 * turnLeft; // 1 面向右，-1 面向左；中间经过 0，像纸偶翻面
  const headLook = -9 * ramp(t, 12.4, 14) * (1 - ramp(t, 22.5, 23.2)) + 8 * ramp(t, 8.6, 10) * (1 - ramp(t, 11, 12));
  const walk = ramp(t, 23, 24.2);
  const prints = Array.from({length: 9}, (_, i) => [bx0 - 540 + i * 58, GY + 8 + (i % 2) * 7] as [number, number]);
  const trail = Array.from({length: 24}, (_, i) => [bx0 + 60 + i * 52, GY + 8 + (i % 2) * 7] as [number, number]).filter(([x]) => x < bx - 20);
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop mount={{cx: MX, k: MK, baseY: MB}} />
        <Layer p={0.16}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={5.5} glow={0.35 + 0.65 * ramp(t, 9, 13)} />
          </svg>
        </Layer>
        <Layer p={1}>
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <Footprints pts={prints} s={0.8} fade={ramp(t, 4, 15) * 0.9} />
            <Footprints pts={trail} s={0.8} fade={ramp(t, 24, 30) * 0.5} />
            <GroundShadow x={bx} y={GY + 6} rx={64} />
            <g transform={`translate(${bx} ${GY}) scale(${sx} 1)`}>
              <Boy x={0} y={0} s={0.5} walk={walk} head={headLook} wind={0.6} />
            </g>
            <BreathPuff x={bx + 34 * sx} y={GY - 120} s={0.6} dir={sx} />
          </svg>
        </Layer>
        <FrameTrees x={-40} k={0.5} />
      </Stage>
      <Snowfall horizon={HZ + 10} wind={0.15} />
    </SceneWrap>
  );
};
