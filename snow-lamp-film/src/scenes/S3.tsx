import React from 'react';
import {Img, staticFile} from 'remotion';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Turtle, TurtleHead} from '../chars/Turtle';
import {GroundShadow, BreathPuff} from '../fx/Bits';
import {Backdrop, SceneWrap, FrameTrees, mountLamp, useT, ramp, lerp, hopAt, at, GY, HZ} from './kit';

// 三、遇见慢慢：池塘边的“大石头”动了 → 是一只很老很老的乌龟 → 壳上是一张地图 → “我背着你”
export const S3: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(960, 540, 1.0)},
    {t: 6, ...at(960, 560, 1.06)},
    {t: 8.8, ...at(930, 640, 1.28)},
    {t: 12.2, ...at(940, 650, 1.3)},
    {t: 14.6, ...at(1082, 722, 2.4)},
    {t: 17.0, ...at(1082, 722, 2.4)},
    {t: 19.4, ...at(900, 650, 1.3)},
    {t: 22, ...at(900, 640, 1.26)},
  ]);
  const MX = 1640, MB = HZ + 80, MK = 0.66;
  const lamp = mountLamp(MX, MB, MK);
  const TX = 1080;
  const bx = lerp(340, 880, ramp(t, 0, 8.6));
  const bw = ramp(t, 0, 0.8) * (1 - ramp(t, 7.6, 8.6));
  const rx0 = lerp(220, 790, ramp(t, 0, 8.6));
  const rh = hopAt(t, [{t0: 9.6, t1: 10.3, x0: 790, x1: 800, h: 28}], 790);
  const rx = t < 8.6 ? rx0 : rh.x;
  const rabbitHop = t < 8.6 ? Math.abs(Math.sin(t * 6)) * 14 * (1 - ramp(t, 7.8, 8.6)) : rh.lift;
  // 慢慢：雪盖着像石头 → 雪滑落 → 伸出头 → 被背进书包
  const snow = 1 - ramp(t, 3.4, 7.4) * 0.6 - ramp(t, 11.0, 13.4) * 0.4;
  const look = ramp(t, 4.0, 7.0);
  const carry = ramp(t, 17.4, 19.6);
  const tx = lerp(TX, 880 - 42 * 0.62 - 6, carry);
  const ty = lerp(GY - 4, GY - 190 * 0.62 - 6, carry) - Math.sin(Math.PI * carry) * 70;
  const ts = lerp(0.78, 0.2, carry);
  const bagHead = ramp(t, 19.0, 20.0);
  const lean = 16 * Math.sin(Math.PI * ramp(t, 17.0, 20.0));
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop mount={{cx: MX, k: MK, baseY: MB}} />
        <Layer p={0.16}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={7} />
          </svg>
        </Layer>
        <Layer p={0.92}>
          <Img src={staticFile('baked/pond.png')} style={{position: 'absolute', left: 1260, top: 590, width: 1100, height: 261}} />
        </Layer>
        <Layer p={1}>
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <GroundShadow x={TX} y={GY + 4} rx={150} o={carry < 0.5 ? 1 : 1 - (carry - 0.5) * 2} />
            {carry < 0.97 ? (
              <g transform={`translate(${tx} ${ty})`}>
                <Turtle x={0} y={0} s={ts} snow={snow} look={look} flip />
              </g>
            ) : null}
            <GroundShadow x={bx} y={GY + 6} rx={70} />
            <g transform={`translate(${bx} ${GY})`}>
              <Boy x={0} y={0} s={0.62} walk={bw} lean={lean} head={t > 5 ? 8 : 0} wind={0.4}>
                <TurtleHead x={-42} y={-190} s={1.0} up={(1 - bagHead) * 46} t0={2} />
              </Boy>
            </g>
            <GroundShadow x={rx} y={GY + 6} rx={46} o={1 - rabbitHop / 120} />
            <g transform={`translate(${rx} ${GY - rabbitHop})`}>
              <Rabbit x={0} y={0} s={0.6} perk={0.6} squash={rabbitHop / 30} t0={3} />
            </g>
            <BreathPuff x={bx + 40} y={GY - 140} s={0.7} />
          </svg>
        </Layer>
        {t < 2 || t > 20 ? <FrameTrees x={-70} /> : null}
      </Stage>
      <Snowfall horizon={HZ + 10} wind={0.1} />
    </SceneWrap>
  );
};
