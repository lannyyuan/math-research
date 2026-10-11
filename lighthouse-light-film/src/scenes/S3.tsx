import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Snow} from '../fx/Snow';
import {Hazel, Bud, Bolts} from './cast';
import {Bg, SceneWrap, useT, ramp, lerp, at, cuesOf} from './kit';

// 三、城里 Mrs Mallet 的修理铺：灯泡像甜瓜一样大；机器人 Bolts 的眼睛亮起来（黄色、亮亮的）；"一段长路有朋友更好"——Bolts 跟他们走
const C = cuesOf('s3-bolts');
const BENCH_Y = 745;     // 工作台面
const FLOOR_Y = 862;     // 地板上角色的脚

export const S3: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(900, 540, 1.0)},
    {t: 5.5, ...at(1200, 560, 1.15)},
    {t: 7.2, ...at(1130, 580, 1.2)},
    {t: 13.5, ...at(1040, 590, 1.28)},
    {t: 18.5, ...at(1060, 580, 1.2)},
    {t: 22.0, ...at(840, 570, 1.05)},
    {t: len, ...at(640, 560, 1.02)},
  ]);
  // 角色走进来
  const enter = ramp(t, 0.0, 2.2);
  // 最后 Bolts 跳下台面，跟着他们往外走
  const hop = ramp(t, 20.2, 21.6);
  const leave = ramp(t, 22.6, 25.4);
  const hx = lerp(-120, 640, enter) - leave * 560;
  const bx = lerp(-230, 530, enter) - leave * 560;
  const eyes = ramp(t, C[1].t + 0.9, C[1].t + 2.0);
  const boltsX = lerp(1050, 780, hop) - leave * 560;
  const boltsY = lerp(BENCH_Y, FLOOR_Y, hop) - Math.sin(hop * Math.PI) * 70;
  const talk = t > C[2].t && t < C[2].t + C[2].d ? 0.03 : 0.008;
  return (
    <SceneWrap len={len} bg="#445273">
      <Stage cam={cam}>
        <Layer p={0.92} w={2400}><Bg src="workshop_far.jpg" w={2400} h={1080} /></Layer>
        <Layer p={1} w={2400}>
          <GroundShadow x={1350} y={850} rx={110} o={0.25} />
          <Sprite name="mallet" x={1350} y={852} s={0.86} breathe={0.01} sway={0.4} t0={0.5} />
          <Bg src="workshop_near.png" w={2400} h={1080} />
          {/* 台面上：大灯泡（和盒子）、Bolts */}
          <Sprite name="bulb_box" x={1790} y={BENCH_Y} s={0.78} breathe={0} sway={0} />
          {hop < 1 ? (
            <>
              <GroundShadow x={boltsX} y={boltsY} rx={60} o={0.35} />
              <Bolts view="front" x={boltsX} y={boltsY} s={0.86} eyes={eyes} breathe={talk} sway={0.8} />
            </>
          ) : null}
          <GroundShadow x={hx} y={FLOOR_Y} rx={90} />
          <GroundShadow x={bx} y={FLOOR_Y + 6} rx={90} />
          <Hazel x={hx} y={FLOOR_Y} s={0.74} walk={enter < 1 || leave > 0 ? 5 : 0} flip={leave > 0} t0={1} />
          <Bud x={bx} y={FLOOR_Y + 6} s={0.7} head="bare" walk={enter < 1 || leave > 0 ? 5 : 0} flip={leave > 0} t0={0.3} />
          {hop >= 1 ? (
            <>
              <GroundShadow x={boltsX} y={FLOOR_Y} rx={60} o={0.35} />
              {leave > 0 ? <Bolts view="side" x={boltsX} y={FLOOR_Y} s={0.86} eyes={1} walk={4} /> : <Bolts view="front" x={boltsX} y={FLOOR_Y} s={0.86} eyes={1} />}
            </>
          ) : null}
        </Layer>
      </Stage>
      <Snow amount={0.12} wind={0.1} />
    </SceneWrap>
  );
};
