import React from 'react';
import {Stage, Layer} from '../fx/Stage';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {Turtle, TurtleHead} from '../chars/Turtle';
import {Cabin} from '../fx/Cabin';
import {OldMan} from '../chars/Others';
import {GroundShadow} from '../fx/Bits';
import {Backdrop, SceneWrap, useT, ramp, lerp, turnScale, GY, HZ} from './kit';

// 九、和伙伴们告别：爸爸妈妈赶来紧紧抱住他 → “你还会回来吗？”拉勾 → 慢慢：“路……我已经记在……壳上了。” → 白鹿：“你也可以做别人的灯。” → 小石头跟着爸爸妈妈下山，朋友们的身影越来越小
const CX = 1900, KC = 1.1;
const DOOR_X = CX + 88;
const WIN: [number, number] = [CX - 111 * KC, GY - 109 * KC];

export const S9: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const dawn = 0.5 + 0.5 * ramp(t, 0, 30);
  // —— 镜头 ——
  let cx = 1150, cy = 610, cz = 1.14;
  const a = ramp(t, 6.5, 9.5);
  cx = lerp(cx, 1190, a); cy = lerp(cy, 640, a); cz = lerp(cz, 1.28, a);
  const sh = ramp(t, 12.2, 14.2) * (1 - ramp(t, 18.6, 20.4));
  cx = lerp(cx, 1238, sh); cy = lerp(cy, 712, sh); cz = lerp(cz, 2.45, sh);
  const b = ramp(t, 19.2, 20.6) * (1 - ramp(t, 24.0, 26.0));
  cx = lerp(cx, 1210, b); cy = lerp(cy, 650, b); cz = lerp(cz, 1.4, b);
  const out = ramp(t, 25.0, 34);
  cx = lerp(cx, 1200, out); cy = lerp(cy, 560, out); cz = lerp(cz, 0.9, out);
  const cam = {x: cx - 960, y: cy - 540, z: cz};

  // —— 爸爸妈妈和小石头：赶来 → 抱 → 站起来 → 下山 ——
  const run = ramp(t, 0, 1.8);
  const hug = ramp(t, 1.8, 2.8) * (1 - ramp(t, 6.4, 7.4));
  const momX = lerp(560, 880, run), dadX = lerp(480, 830, run);
  const runWalk = (1 - ramp(t, 1.0, 1.8)) * 1.6;
  const boyRun = ramp(t, 0, 1.6);
  const stand = ramp(t, 7.0, 8.2);
  const away = ramp(t, 25.4, 34);
  // 小石头：朝左跑去 → 被抱 → 转过身朝友们 → 最后转身下山
  const boyX0 = t < 1.8 ? lerp(1150, 960, boyRun) : 960;
  const stepFwd = ramp(t, 18.8, 19.8) * (1 - ramp(t, 24.0, 25.0));
  const boyX = t < 7 ? boyX0 : t < 25.4 ? lerp(960, 995, stand) + 125 * stepFwd : lerp(995, 330, away);
  const face = turnScale(t, [{at: 7.2, to: 1}, {at: 25.2, to: -1}, {at: 30.0, to: 1}, {at: 32.8, to: -1}], -1, 0.5);
  const wave = t >= 30.4 && t < 33;
  const boyWalk = t < 1.8 ? 1.4 * boyRun * (1 - ramp(t, 1.2, 1.8)) : t >= 25.6 ? 0.8 * ramp(t, 25.6, 26.6) : 0;
  const gz = (x: number) => GY - 130 * away * ramp(x, 1100, 350) * 0;
  // 爸妈：抱住后站起，陪在身边，最后一起下山
  const momNow = t < 7 ? momX : t < 25.4 ? lerp(880, 905, stand) : lerp(905, 250, away);
  const dadNow = t < 7 ? dadX : t < 25.4 ? lerp(830, 835, stand) : lerp(835, 170, away);
  const pWalk = t < 1.8 ? runWalk : t >= 25.8 ? 0.8 * ramp(t, 25.8, 26.8) : 0;
  const mSit = hug * (t < 7 ? 1 : 0);
  const pFace = turnScale(t, [{at: 25.2, to: -1}], 1, 0.5);
  const farK = lerp(1, 0.64, away), farLift = 70 * away;
  // —— 朋友们 ——
  const carry = ramp(t, 7.6, 9.4);
  const turtleX = lerp(995 - 42 * 0.62, 1235, carry);
  const turtleY = lerp(GY - 190 * 0.62, GY - 4, carry) - Math.sin(Math.PI * carry) * 60;
  const turtleOut = t >= 7.6;
  const headHide = ramp(t, 7.4, 8.0);
  const rabbitX = t < 8.2 ? 1330 : t < 9.4 ? lerp(1330, 1066, ramp(t, 8.4, 9.2)) : t < 13.6 ? 1066 : lerp(1066, 1128, ramp(t, 13.6, 14.4));
  const rhop = (t >= 8.4 && t < 9.2 ? Math.sin(Math.PI * ramp(t, 8.4, 9.2)) * 40 : 0) + (t >= 13.6 && t < 14.4 ? Math.sin(Math.PI * ramp(t, 13.6, 14.4)) * 40 : 0);
  const rabbitFace = turnScale(t, [{at: 0.1, to: -1}], -1, 0.3);
  const promise = ramp(t, 9.6, 10.6) * (1 - ramp(t, 12.4, 13.2));
  const kneel = promise;
  const dHead = ramp(t, 19.0, 20.4) * (1 - ramp(t, 22.6, 24.0)) * 0.84;
  const dx = 1400;
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop dawn={dawn} horizon={HZ} snow="snow-b" mount={false} far mid />
        <Layer p={1}>
          <svg width={3000} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <ellipse cx={WIN[0]} cy={GY + 6} rx={520} ry={50} fill="url(#lampHalo)" opacity={0.5} />
            <Cabin x={CX} y={GY + 4} s={KC} />
            <LampGlow x={WIN[0]} y={WIN[1]} r={13} glow={1.0} />
            {/* 白鹿 */}
            <GroundShadow x={dx} y={GY + 8} rx={150} />
            <Deer x={dx} y={GY} s={0.7} flip headDown={dHead} leaves={1} t0={2} />
            <g transform={`translate(${DOOR_X} ${GY + 2})`}><OldMan x={0} y={0} s={0.62} flip nod={4} t0={1} /></g>
          </svg>
          <svg width={3000} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            {/* 兔子 */}
            <GroundShadow x={rabbitX} y={GY + 6} rx={44} o={1 - rhop / 100} />
            <g transform={`translate(${rabbitX} ${GY - rhop}) scale(${rabbitFace} 1)`}>
              <Rabbit x={0} y={0} s={0.6} perk={0.15 + 0.7 * ramp(t, 13, 14.2)} t0={3} fear={0} />
            </g>
            {/* 拉勾：小石头的手和兔子的爪子勾在一起 */}
            {promise > 0.3 ? (
              <g transform={`translate(${(boyX + rabbitX) / 2 + 6} ${GY - 78})`} opacity={promise}>
                <ellipse cx={-4} cy={0} rx={9} ry={5} fill="none" stroke="#1a1f3f" strokeWidth={2.4} />
                <ellipse cx={5} cy={0} rx={9} ry={5} fill="none" stroke="#1a1f3f" strokeWidth={2.4} />
              </g>
            ) : null}
            {/* 慢慢 */}
            {turtleOut ? (
              <g transform={`translate(${turtleX} ${turtleY})`}>
                <Turtle x={0} y={0} s={lerp(0.2, 0.78, carry)} flip look={ramp(t, 13, 14)} mark={ramp(t, 13.4, 15.2) * (1 - ramp(t, 18.2, 19.2))} />
              </g>
            ) : null}
            {/* 爸爸妈妈 */}
            <g transform={`translate(${dadNow} ${GY - farLift}) scale(${pFace * farK} ${farK})`}>
              <GroundShadow x={0} y={8} rx={60} />
              <Boy x={0} y={0} s={0.95} variant="dad" walk={pWalk} lean={hug * 28 * (t < 7 ? 1 : 0)} armN={-80 * hug * (t < 7 ? 1 : 0)} armF={-70 * hug * (t < 7 ? 1 : 0)} head={hug * 10} />
            </g>
            <g transform={`translate(${momNow} ${GY - farLift}) scale(${pFace * farK} ${farK})`}>
              <GroundShadow x={0} y={8} rx={56} />
              <Boy x={0} y={0} s={0.85} variant="mom" walk={pWalk} sit={mSit * 0.9} lean={hug * 8} armN={-86 * hug * (t < 7 ? 1 : 0) + (t >= 8 && t < 25 ? -35 : 0)} head={hug * 8} />
            </g>
            {/* 小石头 */}
            <GroundShadow x={boyX} y={GY + 6 - farLift} rx={64 * farK} />
            <g transform={`translate(${boyX} ${GY - farLift}) scale(${face * farK} ${farK})`}>
              <Boy x={0} y={0} s={0.62} walk={boyWalk} armF={-70 * hug} lean={kneel * 28} head={hug * 6 + kneel * 8 + (t >= 25 ? 6 : 0)} wind={0.5} armN={wave ? -140 + Math.sin(t * 7) * 16 : -82 * hug}>
                {t < 7.6 ? <TurtleHead x={-42} y={-190} s={1.0} t0={2} /> : <TurtleHead x={-42} y={-190} s={1.0} t0={2} up={46} />}
              </Boy>
            </g>
          </svg>
        </Layer>
      </Stage>
    </SceneWrap>
  );
};
