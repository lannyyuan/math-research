import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {TurtleHead} from '../chars/Turtle';
import {Wolf, Cub} from '../chars/Others';
import {GroundShadow, BreathPuff, Mound} from '../fx/Bits';
import {Backdrop, SceneWrap, FrameTrees, mountLamp, useT, ramp, lerp, hopAt, at, GY, HZ} from './kit';

// 六、帮小狼找到妈妈：松林里一只很小很小的狼 → 兔子吓得躲到身后 → 小石头把面包放在它面前 → 沿着脚印走 → 狼妈妈
const Paws: React.FC<{pts: [number, number][]}> = ({pts}) => (
  <g>
    {pts.map(([x, y], i) => (
      <g key={i} transform={`translate(${x} ${y}) rotate(${(i % 2 ? 4 : -4)})`} opacity={0.75}>
        <ellipse cx={0} cy={0} rx={5} ry={3.6} fill="#8da3cf" />
        {[-6, -2, 2, 6].map((d, k) => <circle key={k} cx={d} cy={-6 + (k % 3 === 1 ? -1.5 : 0)} r={1.6} fill="#8da3cf" />)}
      </g>
    ))}
  </g>
);

export const S6: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(560, 570, 1.0)},
    {t: 3.0, ...at(640, 580, 1.08)},
    {t: 6.5, ...at(700, 620, 1.3)},
    {t: 9.5, ...at(700, 630, 1.4)},
    {t: 12.6, ...at(880, 600, 1.12)},
    {t: 17.6, ...at(1180, 590, 1.04)},
    {t: 21.5, ...at(1300, 600, 1.18)},
    {t: 25, ...at(1330, 600, 1.12)},
    {t: 31.5, ...at(1420, 590, 1.08)},
  ]);
  const MX = 1700, MB = HZ + 70, MK = 0.62;
  const lamp = mountLamp(MX, MB, MK);

  // —— 小石头 ——
  const bx = t < 3 ? lerp(250, 480, ramp(t, 0, 3)) : t < 5.2 ? 480 : t < 8.4 ? lerp(480, 690, ramp(t, 5.2, 8.4)) : t < 12.2 ? 690 : lerp(690, 1090, ramp(t, 12.2, 18)) + (t > 25 ? 0 : 0);
  const bwalk = t < 3 ? ramp(t, 0, 0.7) * (1 - ramp(t, 2.4, 3)) : t < 8.4 ? ramp(t, 5.2, 6) * (1 - ramp(t, 7.6, 8.4)) : ramp(t, 12.2, 13) * (1 - ramp(t, 17.2, 18));
  const crouch = ramp(t, 7.6, 8.6) * (1 - ramp(t, 10.6, 11.4));
  const reach = ramp(t, 7.8, 8.8) * (1 - ramp(t, 10.0, 10.8));
  // —— 小狼 ——
  const cubDark = 1 - ramp(t, 5.0, 8.0) * 0.55;
  const cubWalk = t > 12.2;
  const cubX = t < 12.2 ? 770 : t < 18.6 ? lerp(770, 1010, ramp(t, 12.4, 18)) : t < 20.6 ? 1010 : t < 22.6 ? lerp(1010, 1330, ramp(t, 20.6, 22.6)) : t < 25.4 ? 1330 : lerp(1330, 2000, ramp(t, 25.4, 31));
  const cubSit = t < 12.2 || (t >= 18.6 && t < 20.6);
  const cubShiver = t < 8.6 ? 1 : 0;
  // —— 兔子：吓得躲到身后，慢慢探出头，最后和大家一起走 ——
  const rabbitFear = ramp(t, 3, 3.6) * (1 - ramp(t, 10.6, 12.4)) + ramp(t, 18.4, 19.2) * (1 - ramp(t, 24.6, 26)) * 0.8;
  const rh = hopAt(t, [{t0: 3.0, t1: 3.5, x0: 560, x1: 420, h: 60}], 560);
  const rx = t < 3 ? lerp(330, 560, ramp(t, 0, 3)) : t < 3.5 ? rh.x : t < 10.8 ? 420 : t < 12.4 ? lerp(420, 600, ramp(t, 10.8, 12.4)) : lerp(600, 960, ramp(t, 12.4, 18));
  const rlift = t < 3 ? Math.abs(Math.sin(t * 5.6)) * 14 : t < 3.5 ? rh.lift : t >= 12.4 && t < 18 ? Math.abs(Math.sin(t * 5.2)) * 12 : 0;
  const rjit = Math.sin(t * 40) * 1.8 * rabbitFear;
  // —— 白鹿：跟在后面 ——
  const dx = t < 3 ? lerp(70, 300, ramp(t, 0, 3)) : t < 10.4 ? 300 : t < 12.4 ? lerp(300, 420, ramp(t, 10.4, 12.4)) : lerp(420, 860, ramp(t, 12.4, 18));
  const dwalk = (t < 3 ? ramp(t, 0, 0.7) * (1 - ramp(t, 2.4, 3)) : 0) + (t >= 10.4 && t < 12.4 ? 0.8 : 0) + (t >= 12.4 && t < 18 ? 1 : 0);
  // —— 狼妈妈：站在雪坡上看着，慢慢走下来，点点头，带着小狼走 ——
  const mx = t < 19.2 ? 1760 : t < 23.4 ? lerp(1760, 1450, ramp(t, 19.4, 23.4)) : t < 25.4 ? 1450 : lerp(1450, 2100, ramp(t, 25.6, 31));
  const my = GY - 56 * (1 - ramp(t, 19.4, 23.4)) * (t < 25 ? 1 : 0);
  const mwalk = t >= 19.6 && t < 23.4 ? 0.7 : t >= 25.6 ? 0.9 : 0;
  const mnod = Math.sin(Math.PI * ramp(t, 23.6, 25.0)) * 1.0;
  const mvis = ramp(t, 17.2, 18.6);
  const pawsPts: [number, number][] = Array.from({length: 22}, (_, i) => [800 + i * 42, GY + 14 + (i % 2) * 6] as [number, number]).filter(([x]) => x < lerp(800, 1760, ramp(t, 10.0, 18.5)));
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop snow="snow-a" mount={{cx: MX, k: MK, baseY: MB}} />
        <Layer p={0.16}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={6.5} />
          </svg>
        </Layer>
        <FrameTrees p={0.75} x={1250} k={0.38} bottom={GY - 40} />
        <FrameTrees p={0.85} x={-100} k={0.42} bottom={GY - 22} />
        <Layer p={1}>
          <FrameTrees p={0} x={560} k={0.6} bottom={GY + 26} />
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <Mound x={1780} y={GY + 28} w={1000} h={170} seed={5} />
            <Paws pts={pawsPts} />
            <GroundShadow x={cubX} y={GY + 6} rx={40} />
            <g transform={`translate(${cubX} ${GY})`} style={{filter: `brightness(${cubDark})`}}>
              <Cub x={0} y={0} s={0.62} shiver={cubShiver} t0={1} headTilt={t > 8.4 && t < 10.8 ? 8 : 0} />
            </g>
            <GroundShadow x={dx} y={GY + 8} rx={150} />
            <Deer x={dx} y={GY} s={0.72} walk={dwalk} headDown={ramp(t, 10, 11) * (1 - ramp(t, 12, 13)) * 0.3} t0={2} />
            <GroundShadow x={rx} y={GY + 6} rx={44} o={1 - rlift / 120} />
            <g transform={`translate(${rx + rjit} ${GY - rlift})`}>
              <Rabbit x={0} y={0} s={0.6} perk={0.6} fear={rabbitFear} squash={rlift / 30} t0={4} />
            </g>
            <GroundShadow x={bx} y={GY + 6} rx={70} />
            <g transform={`translate(${bx} ${GY + crouch * 6})`}>
              <Boy x={0} y={0} s={0.62} walk={bwalk} lean={crouch * 24} head={crouch * 8} armN={-62 * reach} wind={0.4}>
                <TurtleHead x={-42} y={-190} s={1.0} t0={2} up={-(ramp(t, 12.4, 13.4) * (1 - ramp(t, 15.2, 16.4))) * 16} />
              </Boy>
            </g>
            {reach > 0.02 && t < 10.8 ? <ellipse cx={bx + 50 + reach * 8} cy={GY - 60 + crouch * 8} rx={11} ry={8} fill="#f6f9ff" stroke="#1a1f3f" strokeWidth={1.6} /> : null}
            <GroundShadow x={mx} y={my + 6} rx={130} o={mvis} />
            <g transform={`translate(${mx} ${my})`} opacity={mvis}>
              <Wolf x={0} y={0} s={0.62} walk={mwalk} headDown={mnod * 0.9} flip={t < 25.6} t0={3} />
            </g>
            <BreathPuff x={bx + 40} y={GY - 130} s={0.7} />
          </svg>
        </Layer>
      </Stage>
      <Snowfall horizon={HZ + 10} wind={0.12} />
    </SceneWrap>
  );
};
