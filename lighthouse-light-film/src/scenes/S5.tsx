import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {CoolGlow, LitWindow} from '../fx/Light';
import {Hazel, Bud, Bolts, Comet} from './cast';
import {Bg, SceneWrap, Tint, useT, ramp, track, at, cuesOf} from './kit';

// 五、农场避雪：透过雪看见一盏冷白的灯；农场的大婶给了 Bud 一顶带绒球的毛线帽；落叶堆在动——刺猬 Pebbles 爬进了那顶帽子（从此帽子装在 Bud 的口袋里，Bud 不再戴帽子）
const C = cuesOf('s5-farm');
const GY = 905;
const PILE = {x: 640, y: 905};
const FARMER = {x: 1490, y: 850};
const HAT_S = 0.68;

export const S5: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const hazelX = track(t, [[0.2, 420], [6.8, 1240]]);
  const walkingIn = t > 0.2 && t < 6.8;
  const budFaceLeft = t > 14.6;
  const budX = t < 14.0 ? hazelX - 110 : track(t, [[14.0, 1130], [16.4, 770]]);
  const budWalk = (t > 0.2 && t < 6.8) || (t > 14.0 && t < 16.4);
  const boltsX = t < 14.0 ? hazelX - 205 : 1010;
  const cometX = t < 14.0 ? hazelX - 335 : 880;
  const cam = useCam([
    {t: 0, ...at(1230, 540, 1.0)},
    {t: 6.8, ...at(1400, 540, 1.04)},
    {t: 13.8, ...at(1380, 540, 1.04)},
    {t: 16.0, ...at(900, 560, 1.12)},
    {t: len, ...at(880, 570, 1.18)},
  ]);

  // 冷白的农舍灯：第 1 秒起慢慢亮起来，微微闪
  const lamp = ramp(t, 0.6, 2.4) * (0.92 + 0.08 * Math.sin(t * 5.3));
  // 大婶：从门口走出来，站到 Bud 面前，递帽子
  const farmerX = track(t, [[7.0, 2080], [9.2, FARMER.x]]);
  const farmerWalk = t > 7.0 && t < 9.2 ? 4 : 0;
  const farmerO = ramp(t, 6.8, 7.2) * (1 - ramp(t, 13.0, 14.2));

  // 帽子（带绒球的毛线帽）：9.4~11.2 从大婶手里飞到 Bud 头上，19.5~20.6 又被摘下放到落叶堆旁
  const handX = FARMER.x - 64, handY = FARMER.y - 160;            // 大婶递出的手
  const headX = (bx: number, face: number) => bx + face * 11, headY = GY + 4 - 298 * HAT_S;
  const give = ramp(t, 9.4, 11.2);
  const giveX = handX + (headX(budX, 1) - handX) * give;
  const giveY = handY + (headY - handY) * give - Math.sin(give * Math.PI) * 70;
  const giveS = 0.4 + (HAT_S - 0.4) * give;
  const budHead: 'bare' | 'hat' = t >= 11.2 && t < 19.5 ? 'hat' : 'bare';

  // 落叶堆在动：先抖，然后 Pebbles 从里面探出头
  const shake = t > C[2].t - 0.3 && t < 21 ? Math.sin(t * 26) * 2.6 * (1 - ramp(t, 17.6, 19.0) * 0.7) : 0;
  const peek = ramp(t, 17.0, 18.6);
  const pebblesTopO = 1 - ramp(t, 20.0, 20.8);

  // Bud 摘下帽子，Pebbles 爬进去
  const drop = ramp(t, 19.5, 20.6);
  const hatDropX = headX(budX, -1) + (PILE.x + 78 - headX(budX, -1)) * drop;
  const hatDropY = headY + (GY - 28 - headY) * drop - Math.sin(drop * Math.PI) * 40;
  const hatDropS = HAT_S + (0.55 - HAT_S) * drop;
  const hatO = 1 - ramp(t, 20.2, 21.0);
  const inHatO = ramp(t, 20.2, 21.0);
  // 21.4~22.8：Bud 把帽子（里面是 Pebbles）塞进口袋
  const stuff = ramp(t, 21.4, 22.8);
  const pocketX = budX - 54 * 0.68, pocketY = GY + 4 - 236 * 0.68;
  const pkX = PILE.x + 78 + (pocketX - PILE.x - 78) * stuff;
  const pkY = GY - 6 + (pocketY - GY + 6) * stuff;
  const pkS = 0.55 + (0.374 - 0.55) * stuff;
  const pocket = t >= 22.9;
  const budRot = t > 17.0 && t < 21.3 ? -7 : 0;

  return (
    <SceneWrap len={len} bg="#5a6c92">
      <Stage cam={cam}>
        <Layer p={0.6}><Bg src="farm_far.jpg" w={2900} h={1080} /></Layer>
        <Layer p={1}>
          <Bg src="farm_near.png" w={2900} h={1080} />
          {/* 农舍的窗：冷白的光（不是暖色） */}
          <LitWindow x={1792} y={681} w={69} h={78} opacity={lamp} />
          <LitWindow x={1971} y={681} w={69} h={78} opacity={lamp * 0.9} />
          <CoolGlow x={1880} y={700} r={420 * lamp + 1} opacity={0.5 * lamp} />
          {/* Pebbles 先藏在落叶堆后面，探出头 */}
          <Sprite name="pebbles_front_top" x={PILE.x + 6} y={PILE.y - 84 - peek * 46} s={0.72 * 0.85} opacity={Math.min(peek * 3, 1) * pebblesTopO} breathe={0.01} sway={0} />
          <Sprite name="leaf_pile" x={PILE.x + shake} y={PILE.y} s={0.95} breathe={0} sway={0} />
          {/* 角色（从后到前） */}
          <GroundShadow x={cometX} y={GY} rx={90} />
          <GroundShadow x={boltsX} y={GY + 8} rx={60} />
          <GroundShadow x={budX} y={GY + 4} rx={80} />
          <GroundShadow x={hazelX} y={GY} rx={85} />
          <Comet x={cometX} y={GY - 2} s={0.72} walk={walkingIn ? 6 : 0} t0={0.5} />
          <Bolts view="side" x={boltsX} y={GY + 8} s={0.69} flip eyes={1} walk={walkingIn ? 4 : 0} t0={0.9} />
          <Bud x={budX} y={GY + 4} s={HAT_S} flip={budFaceLeft} head={budHead} pocket={pocket} walk={budWalk ? 5 : 0} rot={budRot} t0={0.3} />
          <Hazel x={hazelX} y={GY} s={0.72} walk={walkingIn ? 5 : 0} flip={budFaceLeft} t0={0} />
          {/* 大婶 */}
          <GroundShadow x={farmerX} y={FARMER.y} rx={90} o={0.4 * farmerO} />
          <Sprite name="farmer" x={farmerX} y={FARMER.y} s={0.8} walk={farmerWalk} opacity={farmerO} breathe={0.008} sway={0.4} t0={0.2} />
          {/* 飞着的帽子 */}
          {t > 9.4 && t < 11.2 && <Sprite name="bud_hat_side" x={giveX - 16 * giveS} y={giveY + 438 * giveS} s={giveS} rot={give * 10} breathe={0} sway={0} />}
          {t > 19.5 && t < 21.0 && <Sprite name="bud_hat_side" x={hatDropX + 16 * hatDropS} y={hatDropY + 438 * hatDropS} flip s={hatDropS} opacity={hatO} breathe={0} sway={0} />}
          {t > 20.2 && t < 22.9 && <Sprite name="pebbles_front" x={pkX} y={pkY} s={pkS} opacity={inHatO} clipBottom={0.34 * stuff} breathe={0.01} sway={0} />}
        </Layer>
      </Stage>
      <Tint color="#9fb0d8" o={0.12 + 0.28 * ramp(t, 0, len)} />
      <Snow amount={0.85} wind={0.2} />
    </SceneWrap>
  );
};
