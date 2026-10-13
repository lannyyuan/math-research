import React from 'react';
import {Img, staticFile} from 'remotion';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {TurtleHead} from '../chars/Turtle';
import {GroundShadow, BreathPuff, Mist, IceCracks, WaterHole, Splash} from '../fx/Bits';
import {Backdrop, SceneWrap, mountLamp, useT, ramp, lerp, hopAt, turnScale, at, GY, HZ} from './kit';

// 四、冰河落水，被白鹿救起：冰裂 → 落水 → 兔子急得拉围巾 → 白鹿从雪雾里走来 → 用角钩住书包带，轻轻托起
export const S4: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(900, 560, 1.0)},
    {t: 5.5, ...at(960, 600, 1.06)},
    {t: 6.4, ...at(990, 690, 1.45)},
    {t: 10.6, ...at(990, 690, 1.65)},
    {t: 13.2, ...at(1120, 620, 1.12)},
    {t: 18, ...at(1140, 650, 1.22)},
    {t: 24, ...at(1170, 650, 1.28)},
    {t: 35, ...at(1240, 660, 1.42)},
  ]);
  const MX = 1700, MB = HZ + 70, MK = 0.66;
  const lamp = mountLamp(MX, MB, MK);
  const XR = 100;
  const HX = 1000; // 冰窟窿中心
  const WL = GY + 8; // 水面线

  // —— 小石头 ——
  const walking = t < 3.9;
  let bx = walking ? lerp(700, HX, ramp(t, 0.2, 3.9)) : HX;
  const sink = ramp(t, 5.6, 6.5) * 92 + ramp(t, 6.5, 19) * 14 + (t > 6.4 && t < 19.6 ? Math.sin(t * 1.7) * 5 : 0);
  let by = GY + (t < 19.6 ? sink : 0);
  let tilt = 0;
  const lift1 = ramp(t, 19.8, 22.6), lift2 = ramp(t, 22.8, 24.6);
  if (t >= 19.6) {
    const fx = lerp(HX, 1186, lift1);
    bx = fx; // 抬起、移到岸上
    by = lerp(GY + 106, GY - 100, lift1) - 36 * Math.sin(Math.PI * lift1);
    by = lerp(by, GY, lift2);
    tilt = Math.sin(t * 1.6) * 4 * (1 - lift2) - 8 * lift1 * (1 - lift2);
  }
  const hang = ramp(t, 19.8, 20.8) * (1 - ramp(t, 24.0, 25.0));
  const raise = t < 19.6 ? ramp(t, 5.9, 6.6) : (1 - ramp(t, 19.6, 20.4)) * 0;
  const sit = ramp(t, 24.8, 26.4);
  const bface = turnScale(t, [{at: 24.4, to: -1}], 1, 0.5);
  const head = t < 5.6 ? ramp(t, 3.9, 4.6) * 14 : t < 19.6 ? -8 : 0;
  const walkAmt = walking ? ramp(t, 0.2, 0.9) * (1 - ramp(t, 3.4, 3.9)) : 0;

  // —— 兔子：在冰边急得跳，拉着围巾 ——
  const hopsA = [{t0: 2.4, t1: 3.0, x0: 560, x1: 700, h: 36}, {t0: 3.4, t1: 4.0, x0: 700, x1: 850, h: 36}];
  const rh = hopAt(t, hopsA, 520);
  let rx = t < 2.4 ? lerp(380, 520, ramp(t, 0, 2.4)) : rh.x;
  let rlift = t < 2.4 ? Math.abs(Math.sin(t * 5)) * 16 : rh.lift;
  let rfear = ramp(t, 4.0, 4.8);
  let rrot = 0;
  let rflip = 1;
  if (t >= 5.6 && t < 25.4) {
    rx = 868 + Math.sin(t * 2.6) * 10;
    rlift = Math.abs(Math.sin(t * 6.5)) * 46 * (1 - ramp(t, 17, 19)) + Math.abs(Math.sin(t * 3)) * 6;
    rrot = -14 + Math.sin(t * 6.5) * 6;
  }
  if (t >= 25.4) {
    const u = ramp(t, 25.4, 26.6);
    rx = lerp(868, 1138, u);
    rlift = Math.sin(Math.PI * u) * 70;
    rfear = 0;
    rflip = -1;
  }
  const rabbitScaleX = t >= 25.4 ? -1 : 1;
  const onLap = t >= 26.6;
  void rflip;

  // —— 白鹿：从雪雾里走来 ——
  const DX = lerp(1900, 1330, ramp(t, 11.2, 16.0));
  const dWalk = ramp(t, 11.2, 12.2) * (1 - ramp(t, 14.8, 16.2));
  const kneel = ramp(t, 16.2, 18.4) * (1 - ramp(t, 24.2, 25.2));
  const lie = ramp(t, 24.4, 26.6);
  const headDown = ramp(t, 17.0, 19.6) * 0.82 * (1 - ramp(t, 19.8, 22.6) * 0.9) + ramp(t, 24, 26.5) * 0.1;
  const mistO = 1 - ramp(t, 11.5, 15.5) * 0.75;
  const mistItems = [
    {x: 1700, y: 650, rx: 520, ry: 190}, {x: 2000, y: 700, rx: 560, ry: 200}, {x: 1450, y: 600, rx: 420, ry: 150}, {x: 1850, y: 560, rx: 480, ry: 170},
  ];
  const holeOpen = ramp(t, 5.5, 6.3);
  const crackReveal = ramp(t, 3.7, 5.4);
  const scarfRibbon = t >= 6.2 && t < 19.8;
  const ribbon = scarfRibbon
    ? `M${HX - 12} ${GY - 100 + sink * 0.2} Q${(HX + rx) / 2} ${GY - 40 + Math.sin(t * 6) * 8} ${rx + 40} ${GY - 78 - rlift * 0.3}`
    : '';
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop snow="snow-b" mount={{cx: MX, k: MK, baseY: MB}} />
        <Layer p={0.16}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={7} />
          </svg>
        </Layer>
        <Layer p={1}>
          <Img src={staticFile('baked/river.png')} style={{position: 'absolute', left: XR, top: HZ, width: 1700, height: 540}} />
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <IceCracks x={HX} y={GY + 4} reveal={crackReveal} />
            <WaterHole x={HX} y={GY + 8} open={holeOpen} t={t} />
            <Splash x={HX} y={GY} age={(t - 5.7) / 1.4} />
            {/* 白鹿（先藏在雾后面） */}
            <GroundShadow x={DX} y={GY + 6} rx={190} o={ramp(t, 11.5, 14)} />
            {t > 11 ? <Deer x={DX} y={GY} s={0.9} flip walk={dWalk} kneel={kneel} lie={lie} headDown={headDown} t0={1} /> : null}
            <GroundShadow x={rx} y={GY + 6} rx={46} o={1 - rlift / 120} />
            <g transform={`translate(${rx} ${GY - (onLap ? 0 : rlift)}) scale(${rabbitScaleX} 1)`} opacity={onLap ? 0 : 1}>
              <Rabbit x={0} y={0} s={0.62} perk={0.7} fear={rfear} rot={rrot} squash={rlift / 50} t0={3} />
            </g>
            {scarfRibbon ? (
              <path d={ribbon} stroke={'#c8323e'} strokeWidth={7} fill="none" strokeLinecap="round" opacity={ramp(t, 6.2, 7) * (1 - ramp(t, 19, 19.8))} />
            ) : null}
            {/* 小石头：落水后用水面线裁掉水下的部分 */}
            <defs>
              <clipPath id="aboveWater"><rect x={0} y={0} width={2400} height={WL} /></clipPath>
            </defs>
            <g clipPath={t < 19.7 && t > 5.5 ? 'url(#aboveWater)' : undefined}>
              {!(t > 5.5 && t < 19.7) ? <GroundShadow x={bx} y={GY + 6} rx={70} o={hang > 0.5 ? 0.3 : 1} /> : null}
              <g transform={`translate(${bx} ${by}) scale(${bface} 1)`}>
                <Boy x={0} y={0} s={0.62} walk={walkAmt} head={head} raise={raise} hang={hang} sit={sit} tilt={tilt} wind={t > 5.6 && t < 19.6 ? 1.6 : 0.5}>
                  <TurtleHead x={-42} y={-190} s={1.0} t0={2} />
                </Boy>
              </g>
            </g>
            {t > 5.8 && t < 19.7 ? <ellipse cx={bx} cy={WL + 10} rx={92} ry={22} fill="#35599a" opacity={0.78} /> : null}
            {t > 6 && t < 19.7 ? <ellipse cx={bx} cy={WL + 4} rx={96 + Math.sin(t * 3) * 5} ry={19} fill="none" stroke="#eaf3ff" strokeWidth={2.4} opacity={0.7} /> : null}
            {onLap ? (
              <g transform={`translate(${bx - 40} ${GY - 30 - Math.sin(Math.PI * ramp(t, 26.6, 27.2)) * 8}) scale(-1 1)`}>
                <Rabbit x={0} y={0} s={0.5} perk={0.5} t0={3} />
              </g>
            ) : null}
            {t < 5.6 || t > 24 ? <BreathPuff x={bx + 40 * bface} y={by - 140} s={0.7} dir={bface} /> : null}
          </svg>
        </Layer>
        <Layer p={0.95}>
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <Mist items={mistItems} t={t} opacity={mistO} />
          </svg>
        </Layer>
      </Stage>
      <Snowfall horizon={HZ + 10} wind={0.12} />
    </SceneWrap>
  );
};
