import React, {useMemo} from 'react';
import {Img, staticFile} from 'remotion';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Fire} from '../fx/Fire';
import {MemoryWindow} from '../fx/Memory';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {TurtleHead} from '../chars/Turtle';
import {GroundShadow} from '../fx/Bits';
import {Art} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {Backdrop, SceneWrap, mountLamp, useT, ramp, at} from './kit';

// 五、火堆边说起家：山洞里点起火 → 小石头说起妈妈在窗边点的那盏小灯 → 眼睛里有了泪光
const FY = 840; // 洞里地面上，角色脚底的 y
const wallArt = () => {
  const a = new Art(311);
  const o = {w: 2.4, taper: 0.5, broken: 0.25, sk: 0} as const;
  // 左壁：一头长角的鹿，几颗星
  a.line([[-60, 20], [-50, -6], [-20, -14], [20, -10], [44, 4], [40, 40]], o).line([[44, 4], [62, -30], [84, -34], [96, -24]], o).line([[84, -34], [78, -70], [92, -92]], o).line([[78, -62], [60, -84]], o).line([[-40, 22], [-42, 62]], o).line([[30, 36], [30, 64]], o);
  a.line([[-90, -110], [-86, -102]], {...o, w: 3}).line([[-30, -130], [-26, -122]], {...o, w: 3}).line([[40, -118], [44, -110]], {...o, w: 3});
  const b = new Art(312);
  // 右壁：三个手拉手的小人 + 一只手印
  for (const x of [-50, 0, 50]) b.line([[x, 10], [x, 60]], o).line([[x - 16, 30], [x, 22], [x + 16, 30]], o).line([[x, 60], [x - 10, 90]], o).line([[x, 60], [x + 10, 90]], o);
  b.line([[-34, 30], [-16, 30]], o).line([[16, 30], [34, 30]], o);
  b.line([[-30, -70], [-20, -100], [-10, -70], [0, -102], [10, -68], [20, -98], [30, -62], [40, -86], [36, -40], [10, -30], [-24, -40], [-30, -70]], {...o, w: 2});
  return {a: a.build(), b: b.build()};
};

export const S5: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const W_ = useMemo(wallArt, []);
  const cam = useCam([
    {t: 0, ...at(960, 560, 1.0)},
    {t: 12, ...at(940, 580, 1.1)},
    {t: 22, ...at(860, 640, 1.34)},
    {t: 30, ...at(850, 660, 1.4)},
  ]);
  const MX = 1040, MB = 560, MK = 0.46;
  const lamp = mountLamp(MX, MB, MK);
  const lit = ramp(t, 2.6, 6.0); // 火着起来
  const dark = 0.7 * (1 - lit);
  const strike = t > 1.0 && t < 3.0;
  const memory = ramp(t, 8.6, 10.4) * (1 - ramp(t, 22, 23.6));
  const lampBoost = 0.7 + 0.5 * ramp(t, 15.4, 17) ;
  const nod = ramp(t, 23.4, 24.2) * (1 - ramp(t, 24.4, 25.4)) * 10;
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop horizon={500} mount={{cx: MX, k: MK, baseY: MB}} far mid />
        <div style={{position: 'absolute', inset: 0, background: '#8aa3da', mixBlendMode: 'multiply'}} />
        <Layer p={0.16}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={5.5} />
          </svg>
        </Layer>
        <Layer p={1}>
          <div style={{position: 'absolute', inset: 0, clipPath: 'ellipse(560px 300px at 960px 400px)'}}>
            <Snowfall horizon={520} wind={0.08} />
          </div>
          <Img src={staticFile('baked/cave.png')} style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080}} />
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <g transform="translate(230 400)" opacity={0.55 * lit}><ArtView a={W_.a} filter="wc1" inkColor="#c8d8f6" sk={0} fillOpacity={0} /></g>
            <g transform="translate(1690 380)" opacity={0.55 * lit}><ArtView a={W_.b} filter="wc1" inkColor="#c8d8f6" sk={0} fillOpacity={0} /></g>
            <MemoryWindow x={420} y={330} s={1.0} appear={memory} lampBoost={lampBoost} />
            <GroundShadow x={780} y={FY + 8} rx={110} />
            <GroundShadow x={1260} y={FY + 8} rx={230} />
            <Fire x={965} y={FY + 6} s={1.15 * (0.2 + 0.8 * lit)} glow={lit} />
            <g transform={`translate(740 ${FY})`}>
              <Boy x={0} y={0} s={0.7} sit={1} head={nod + 3} lean={0} wind={0.3}>
                <TurtleHead x={-42} y={-190} s={1.0} t0={1} />
              </Boy>
            </g>
            <g transform={`translate(860 ${FY - 4})`}>
              <Rabbit x={0} y={0} s={0.62} perk={0.6} t0={5} />
            </g>
            <Deer x={1330} y={FY} s={0.8} flip lie={1} headDown={0.16} t0={2} />
            {strike ? (
              <g>
                {[0, 1, 2, 3, 4, 5].map((i) => {
                  const u = ((t * 3 + i * 0.17) % 0.5) / 0.5;
                  return <circle key={i} cx={880 + i * 6 + u * 14} cy={FY - 30 - u * 36 + i * 3} r={2.4 * (1 - u)} fill="#ffe9a8" opacity={1 - u} />;
                })}
              </g>
            ) : null}
          </svg>
        </Layer>
      </Stage>
      <div style={{position: 'absolute', inset: 0, background: `rgba(4,7,26,${dark})`}} />
    </SceneWrap>
  );
};
