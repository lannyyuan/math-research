import React from 'react';
import {Img, staticFile} from 'remotion';
import {Stage, Layer} from '../fx/Stage';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {TurtleHead} from '../chars/Turtle';
import {OldMan} from '../chars/Others';
import {Cabin, OilLamp, OilCan} from '../fx/Cabin';
import {GroundShadow, BreathPuff} from '../fx/Bits';
import {vnoise} from '../art/ink';
import {Backdrop, SceneWrap, useT, ramp, lerp, hopAt, turnScale, GY} from './kit';

// 八、山顶：爬坡 → 白鹿驮着小石头上山 → 小木屋窗里的灯 → 守林人 → “灯不是家，是为迷路的人点的”
const n1 = vnoise(12), n2 = vnoise(33);
const surf = (x: number) => 770 + 0.26 * Math.max(0, 1550 - x) + 14 * n1(x / 300) + 6 * n2(x / 90); // 与烘焙的山坡一致
const CX = 2380, KC = 1.15; // 小木屋
const WIN: [number, number] = [CX - 111 * KC, GY - 109 * KC]; // 窗里那盏灯
const DOOR_X = CX + 93;

export const S8: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const walkA = (a: number, b: number) => ramp(t, a, a + 0.6) * (1 - ramp(t, b - 0.6, b));
  // —— 小石头：慢慢爬 → 坐下歇 → 被白鹿驮着走 → 下鹿，走到守林人面前 ——
  const riding = t >= 4.1 && t < 11.8;
  const sit = ramp(t, 2.3, 3.0) * (1 - ramp(t, 3.7, 4.1));
  // 鹿
  let dx: number;
  if (t < 2.4) dx = 980 + 20 * ramp(t, 0, 2.4);
  else if (t < 4.4) dx = lerp(1000, 1255, ramp(t, 2.4, 3.6));
  else dx = lerp(1255, 1900, ramp(t, 4.4, 11.4));
  const dWalk = (t < 2.2 ? 0.4 * walkA(0, 2.2) : 0) + (t >= 2.4 && t < 3.8 ? 0.8 : 0) + (t >= 4.4 && t < 11.6 ? 0.95 : 0);
  const kneel = ramp(t, 3.2, 3.9) * (1 - ramp(t, 4.2, 4.8));
  // 小石头（不在鹿背上时）
  const dis = ramp(t, 11.8, 12.6); // 跳下鹿
  const walkOff = ramp(t, 12.6, 16.4);
  let bx = t < 2.2 ? lerp(1130, 1190, ramp(t, 0, 2.2)) : 1190;
  if (t >= 11.8) bx = 1920 + (2330 - 1920) * walkOff;
  const bwalk = t < 2.2 ? 0.4 * walkA(0, 2.2) : t >= 12.6 && t < 16.4 ? 1.5 * (ramp(t, 12.6, 13.2) * (1 - ramp(t, 15.8, 16.4))) : 0;
  const byGround = t >= 11.8 ? GY : surf(bx);
  const hopY = Math.sin(Math.PI * dis) * 70 * (t < 12.6 ? 1 : 0);
  // 兔子
  const rx0 = t < 2.2 ? lerp(1180, 1240, ramp(t, 0, 2.2)) : 1240;
  const rx = t >= 11.8 ? 1990 + (2150 - 1990) * ramp(t, 12.8, 16.2) : rx0;
  const rhop = t >= 11.8 && t < 16.4 ? Math.abs(Math.sin(t * 4.4)) * 18 * (ramp(t, 12.4, 12.9) * (1 - ramp(t, 15.8, 16.4))) + Math.sin(Math.PI * dis) * 50 : t < 2.2 ? Math.abs(Math.sin(t * 5)) * 8 : 0;
  // —— 相机 ——
  const party = riding ? dx : t < 11.8 ? bx : bx;
  const camAx = party + 260, camAy = surf(party) - 210;
  const tB = ramp(t, 10.6, 14.5);
  let cx = lerp(camAx, 2280, tB), cy = lerp(camAy, 640, tB), cz = lerp(1.5, 1.28, tB);
  const zoomLamp = ramp(t, 21.0, 24.4) * (1 - ramp(t, 28.0, 31.6));
  cx = lerp(cx, WIN[0] + 30, zoomLamp); cy = lerp(cy, WIN[1] + 10, zoomLamp); cz = lerp(cz, 2.9, zoomLamp);
  const wide = ramp(t, 31.0, 34.8);
  cx = lerp(cx, 2200, wide); cy = lerp(cy, 580, wide); cz = lerp(cz, 1.0, wide);
  const cam = {x: cx - 960, y: cy - 540, z: cz};
  // —— 守林人：开门 → 站在门口 ——
  const oldVis = ramp(t, 10.6, 11.8);
  const oilT = ramp(t, 22.8, 24.4) * (1 - ramp(t, 26.8, 28.0));
  const lampGlow = 0.85 + 0.45 * ramp(t, 23.5, 25) + 0.3 * ramp(t, 29, 33);
  const wind = t < 11 ? 1 : 0.25;
    
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop horizon={720} far mid={false} ground={false} mount={false} />
        <Layer p={1}>
          <Img src={staticFile('baked/slope.png')} style={{position: 'absolute', left: 0, top: 700, width: 3400, height: 900}} />
          <svg width={3400} height={1700} style={{position: 'absolute', left: 0, top: 0}}>
            <ellipse cx={WIN[0]} cy={GY + 6} rx={420 * lampGlow + 700 * wide} ry={40 + 70 * wide} fill="url(#lampHalo)" opacity={0.55 + 0.25 * wide} />
            <circle cx={WIN[0]} cy={WIN[1]} r={160 + 620 * wide} fill="url(#lampHalo)" opacity={0.95 * wide} />
            <Cabin x={CX} y={GY + 4} s={KC} />
            <LampGlow x={WIN[0]} y={WIN[1]} r={14 * KC} glow={lampGlow} rays />
            {t > 20 ? <OilLamp x={WIN[0]} y={WIN[1] + 38} s={0.5} flame={0.9 + 0.5 * oilT} /> : null}
            {oilT > 0.02 ? <OilCan x={WIN[0] + 120 - oilT * 60} y={WIN[1] - 40} s={0.4} tip={oilT} /> : null}
            {/* 守林人 */}
            <g opacity={oldVis}>
              <GroundShadow x={DOOR_X} y={GY + 8} rx={60} />
              <g transform={`translate(${DOOR_X} ${GY + 2})`}>
                <OldMan x={0} y={0} s={0.62} flip nod={t > 15.4 && t < 22 ? 5 : 0} t0={1} />
              </g>
            </g>
            {/* 白鹿（驮人时，小石头和兔子是它的“背上物”） */}
            <GroundShadow x={dx} y={surf(dx) + 8} rx={150} />
            <g transform={`translate(0 ${surf(dx) - GY})`} style={{}}>
              <Deer x={dx} y={GY} s={0.7} walk={dWalk} kneel={kneel} headDown={t >= 16.5 && t < 21 ? 0.22 : 0.0} leaves={1} t0={2}>
                {riding ? (
                  <g>
                    <g transform="translate(-6 -332) scale(0.886)">
                      <Boy x={0} y={0} s={1} sit={0.95} head={-4} wind={1.2} showLegs>
                        <TurtleHead x={-42} y={-190} s={1.0} t0={2} />
                      </Boy>
                    </g>
                    <g transform="translate(96 -340)"><Rabbit x={0} y={0} s={0.72} perk={0.9} t0={3} /></g>
                  </g>
                ) : null}
              </Deer>
            </g>
            {/* 徒步/下鹿后的小石头和兔子 */}
            {!riding ? (
              <g>
                <GroundShadow x={bx} y={byGround + 6} rx={64} />
                <g transform={`translate(${bx} ${byGround - hopY})`}>
                  <Boy x={0} y={0} s={0.62} walk={bwalk} lean={t < 2.2 ? 14 : 0} head={t >= 16.4 && t < 22 ? 14 : 0} sit={sit} wind={wind * 1.6}>
                    <TurtleHead x={-42} y={-190} s={1.0} t0={2} />
                  </Boy>
                </g>
                <GroundShadow x={rx} y={(t >= 11.8 ? GY : surf(rx)) + 6} rx={44} />
                <g transform={`translate(${rx} ${(t >= 11.8 ? GY : surf(rx)) - rhop})`}>
                  <Rabbit x={0} y={0} s={0.6} perk={0.8} t0={3} />
                </g>
              </g>
            ) : null}
            <BreathPuff x={bx + 40} y={byGround - 130} s={0.7} />
          </svg>
        </Layer>
      </Stage>
    </SceneWrap>
  );
};
