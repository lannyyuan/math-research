import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Hazel, Bud} from './cast';
import {Bg, SceneWrap, Shot, useT, ramp, lerp, at} from './kit';

// 二、Bud 把棒球帽戴到雪人头上（从此 Bud 不戴帽子）；Grandad 在灯塔的冰台阶上摔倒，灯塔是暗的；Hazel 说她去城里取灯泡
const SNOW = {x: 1500, y: 925, s: 0.78};      // 雪人
const CAP_T0 = 2.4, CAP_T1 = 4.4;              // 帽子飞起、落到雪人头上的时间

const A: React.FC = () => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(1330, 540, 1.04)},
    {t: 7.6, ...at(1400, 540, 1.1)},
  ]);
  const u = ramp(t, CAP_T0, CAP_T1);
  const walk = ramp(t, 1.6, 2.6);
  const budX = lerp(1300, 1350, walk);
  // 帽子的轨迹：从 Bud 头上抛起，划个小弧线落到雪人头顶（Bud 精灵的帽子层和身体层锚点相同，所以起点就是 (Bud.x, Bud.y)）
  const capX = lerp(0, SNOW.x - 4 - (budX + 32), u);
  const capY = lerp(0, 582 - (905 - 312), u) - Math.sin(u * Math.PI) * 90;
  const onSnowman = ramp(t, CAP_T1 - 0.15, CAP_T1 + 0.25);
  return (
    <Stage cam={cam}>
      <Layer p={0.6}><Bg src="s1_far.jpg" w={2900} h={1080} /></Layer>
      <Layer p={1}>
        <Bg src="s1_near.png" w={2900} h={1080} />
        <GroundShadow x={SNOW.x} y={SNOW.y} rx={120} />
        <Sprite name="snowman" layers={['snowman', 'snowman_cap']} lo={[1, onSnowman]} x={SNOW.x} y={SNOW.y} s={SNOW.s} breathe={0} sway={0} />
        <GroundShadow x={1190} y={905} rx={90} />
        <GroundShadow x={budX} y={905} rx={90} />
        <Hazel x={1190} y={905} s={0.72} t0={1.2} />
        <Bud x={budX} y={905} s={0.68} head="bare" t0={0.4} />
        {/* 飞着的棒球帽：和 Bud 的精灵同一个锚点和缩放，叠在他头上 */}
        {u > 0 && onSnowman < 1 && (
          <Sprite name="bud_cap_side" x={budX + capX} y={905 + capY} s={0.68} rot={u * 18} breathe={0} sway={0} />
        )}
        {u === 0 && <Sprite name="bud_cap_side" x={budX} y={905} s={0.68} breathe={0.008} sway={0.5} t0={0.4} />}
      </Layer>
    </Stage>
  );
};

const B: React.FC = () => {
  const t = useT();
  const cam = useCam([
    {t: 7.0, ...at(1520, 520, 1.0)},
    {t: 9.8, ...at(1490, 790, 1.6)},
    {t: 13.0, ...at(1490, 790, 1.72)},
    {t: 16.0, ...at(1560, 250, 1.75)},
    {t: 19.4, ...at(1560, 240, 1.8)},
  ]);
  return (
    <Stage cam={cam}>
      <Layer p={0.55}><Bg src="lh_day_far.jpg" w={2900} h={1080} /></Layer>
      <Layer p={1}>
        <Bg src="lh_day_near.png" w={2900} h={1080} />
        <GroundShadow x={1430} y={950} rx={110} />
        <Sprite name="grandad_hurt" x={1430} y={950} s={0.7} breathe={0.01} sway={0.3} t0={0.5} />
      </Layer>
    </Stage>
  );
};

const Cc: React.FC = () => {
  const t = useT();
  const cam = useCam([
    {t: 18.5, ...at(1200, 540, 1.04)},
    {t: 25, ...at(760, 540, 1.04)},
  ]);
  const w = ramp(t, 19.2, 24.5);
  const hx = lerp(1260, 700, w);
  return (
    <Stage cam={cam}>
      <Layer p={0.6}><Bg src="s1_far.jpg" w={2900} h={1080} /></Layer>
      <Layer p={1}>
        <Bg src="s1_near.png" w={2900} h={1080} />
        {/* 背后的雪人戴着 Bud 的棒球帽 */}
        <GroundShadow x={SNOW.x} y={SNOW.y} rx={120} />
        <Sprite name="snowman" layers={['snowman', 'snowman_cap']} x={SNOW.x} y={SNOW.y} s={SNOW.s} breathe={0} sway={0} />
        <GroundShadow x={hx} y={905} rx={90} />
        <GroundShadow x={hx + 100} y={910} rx={90} />
        <Hazel x={hx} y={905} s={0.72} flip walk={w > 0 && w < 1 ? 5 : 0} t0={1} />
        <Bud x={hx + 100} y={910} s={0.68} head="bare" flip walk={w > 0 && w < 1 ? 5 : 0} t0={0.2} />
      </Layer>
    </Stage>
  );
};

export const S2: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  return (
    <SceneWrap len={len} bg="#8fa2c2">
      <Shot to={7.8}><A /></Shot>
      <Shot from={7.8} to={18.8}><B /></Shot>
      <Shot from={18.8}><Cc /></Shot>
      <div style={{position: 'absolute', inset: 0, background: `linear-gradient(rgba(36,52,96,0.28), rgba(36,52,96,0.12))`, pointerEvents: 'none'}} />
      <Snow amount={0.7 + 0.2 * ramp(t, 0, 20)} wind={0.14} />
    </SceneWrap>
  );
};
