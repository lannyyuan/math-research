import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {TurtleHead} from '../chars/Turtle';
import {Stream, Geese, JacketDrape} from '../fx/Spring';
import {GroundShadow} from '../fx/Bits';
import {Backdrop, SceneWrap, mountLamp, useT, ramp, lerp, at, GY, HZ} from './kit';

// 七、冰雪化开：雪停了，天亮了，雪水流成小溪，大雁归来，小石头把棉衣搭在白鹿背上；山顶的灯近了一点
export const S7: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const pause = Math.max(0, Math.min(t - 3.4, 2.8));
  const bx = 420 + 40 * (t - pause);
  const walk = 0.7 * (1 - ramp(t, 3.0, 3.5) * (1 - ramp(t, 6.2, 6.7)));
  const dx = bx - 170;
  const cam = useCam([
    {t: 0, ...at(700, 560, 1.0)},
    {t: 9, ...at(1000, 560, 1.04)},
    {t: 10.2, ...at(1100, 520, 1.06)},
    {t: 14, ...at(1260, 470, 1.1)},
    {t: 17, ...at(1280, 480, 1.1)},
  ]);
  const dawn = ramp(t, 0, 9);
  const spring: [number, number, number] = [ramp(t, 0.4, 3.6), ramp(t, 3.6, 7.2), ramp(t, 7.2, 11)];
  const MX = 1560, MB = HZ + 92, MK = 0.74;
  const lamp = mountLamp(MX, MB, MK);
  // 棉衣：脱下 → 抛到鹿背 → 搭着
  const throwU = ramp(t, 4.6, 5.8);
  const jacketOn = t >= 5.8;
  const variant = t < 4.4 ? 'boy' : 'shirt';
  const raise = Math.sin(Math.PI * ramp(t, 3.7, 4.9)) * 0.55;
  const backX = dx - 20 * 0.72, backY = GY - 346 * 0.72;
  const jx = lerp(bx + 8, backX, throwU), jy = lerp(GY - 112, backY - 4, throwU) - Math.sin(Math.PI * throwU) * 90;
  const rx = bx + 150 + Math.sin(t * 0.7) * 10;
  const rhop = Math.abs(Math.sin(t * 3.2)) * 20;
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop dawn={dawn} snow="snow-a" spring={spring} tintTrees="#2f8a80" tintAmount={0.62 * ramp(t, 2, 10)} underlay={['#16314f', '#2d6a6c', '#6aa89a']} mount={{cx: MX, k: MK, baseY: MB}} />
        <Layer p={0.16}>
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={7.5} glow={0.8} />
            <Geese x={-300} y={160} s={1.0} speed={78} t0={-2} />
            <Geese x={-200} y={230} s={0.7} speed={64} t0={4} />
          </svg>
        </Layer>
        <Layer p={0.92}>
          <svg width={2600} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <Stream pts={[[200, 604], [520, 618], [860, 612], [1180, 630], [1520, 652], [1860, 676], [2220, 702]]} widths={[10, 14, 18, 24, 34, 50]} reveal={ramp(t, 2.0, 6.0)} />
            <ellipse cx={2300} cy={705} rx={420} ry={34} fill="#86b0dc" opacity={0.9 * ramp(t, 3.0, 7.0)} />
            <ellipse cx={2300} cy={700} rx={380} ry={16} fill="#d7eafb" opacity={0.6 * ramp(t, 3.0, 7.0)} />
          </svg>
        </Layer>
        <Layer p={1}>
          <svg width={2600} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <GroundShadow x={dx} y={GY + 8} rx={150} />
            <Deer x={dx} y={GY} s={0.72} walk={walk} leaves={ramp(t, 2, 9)} t0={2}>
              {jacketOn ? <JacketDrape x={-18} y={-340} s={0.8} rot={-4} /> : null}
            </Deer>
            <GroundShadow x={rx} y={GY + 6} rx={44} o={1 - rhop / 100} />
            <g transform={`translate(${rx} ${GY - rhop})`}><Rabbit x={0} y={0} s={0.6} perk={0.9} squash={rhop / 25} t0={3} /></g>
            <GroundShadow x={bx} y={GY + 6} rx={64} />
            <g transform={`translate(${bx} ${GY})`}>
              <Boy x={0} y={0} s={0.62} variant={variant} walk={walk} raise={raise} head={-4} wind={0.7}>
                <TurtleHead x={-42} y={-190} s={1.0} t0={2} />
              </Boy>
            </g>
            {t >= 4.6 && !jacketOn ? <JacketDrape x={jx} y={jy} s={0.8} rot={throwU * -200} /> : null}
          </svg>
        </Layer>
      </Stage>
      <Snowfall amount={1 - ramp(t, 0, 6.5)} horizon={HZ + 10} wind={0.1} />
    </SceneWrap>
  );
};
