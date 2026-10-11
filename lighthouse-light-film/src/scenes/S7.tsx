import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Hazel, Bud, Bolts, Comet} from './cast';
import {Bg, SceneWrap, Tint, useT, ramp, track, at, cuesOf} from './kit';

// 七、悬崖边的暴风雪：Bud 口袋里装着 Pebbles 的毛线帽被风吹出来，滚到悬崖边、掉到下面的窄台上；Hazel 趴下爬到崖边，手指抓住了帽子，把 Pebbles 救了回来
const C = cuesOf('s7-cliff');
const GY = 852;
const EDGE = 2010;
const LEDGE = {x: EDGE + 44, y: 884};

export const S7: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  // 队伍：走（0.2~5.0）→ 帽子被吹走，Bud 追了几步 → 站住 → Hazel 趴下爬到崖边
  const hx = track(t, [[0.2, 300], [5.0, 1500], [5.6, 1500], [8.6, 1700], [11.0, 1700]]);
  const walking = t < 5.0 || (t > 5.6 && t < 8.6);
  const budX = t < 5.6 ? hx - 105 : track(t, [[5.6, hx - 105], [8.4, 1720], [11.0, 1720], [12.4, 1440]]);
  const budWalk = t < 5.0 || (t > 5.8 && t < 8.4) || (t > 11.0 && t < 12.4);
  const lean = t < 9 ? 4 : 0;               // 迎着风，身体前倾
  const boltsX = t < 5.6 ? hx - 205 : 1380;
  const cometX = t < 5.6 ? hx - 335 : 1250;

  // 帽子（里面是 Pebbles）：5.6 从口袋里飞出 → 被风吹着跳、滚 → 9.6 掉到崖下的窄台上 → 12.8~16 Hazel 抓住 → 带回来 → 19~21 交还 Bud
  const hatStartX = 1500 - 105 + 37, hatStartY = GY + 4 - 236 * 0.68;
  const hatX = track(t, [[5.6, hatStartX], [7.6, 1800], [8.8, 1990], [9.7, LEDGE.x]]);
  const hatY0 = track(t, [[5.6, hatStartY], [6.3, hatStartY - 120], [7.7, GY - 6], [8.0, GY - 26], [8.5, GY - 4], [8.9, GY - 2], [9.7, LEDGE.y]]);
  const crawlX = track(t, [[11.0, 1640], [12.8, 1672], [15.2, 1672], [17.0, 1500]]);
  const lying = t >= 11.0 && t < 17.6;
  const reach = ramp(t, 12.8, 14.4) * (1 - ramp(t, 15.3, 16.6));
  const handHome = {x: crawlX + 296, y: GY + 18};
  const handFar = {x: LEDGE.x - 6, y: LEDGE.y - 22};
  const hand = {x: handHome.x + (handFar.x - handHome.x) * reach, y: handHome.y + (handFar.y - handHome.y) * reach};
  // 手把帽子提上来
  const carried = t >= 15.3;
  const give = ramp(t, 19.2, 21.0);
  const hazelStandX = 1600;
  const heldX = hazelStandX + 46, heldY = GY - 150;
  const pocketX = 1440 + 37, pocketY = GY + 4 - 236 * 0.68;
  let hx2 = hatX, hy2 = hatY0, hs = 0.55, hrot = 0;
  if (t < 5.6) { hs = 0.374; }
  else if (t < 9.7) { hs = track(t, [[5.6, 0.374], [6.2, 0.6]]); hrot = ramp(t, 5.8, 9.5) * 560; }
  else if (t < 15.3) { hs = 0.6; hrot = 560 + Math.sin(t * 3) * 3; }
  else if (t < 17.8) { hx2 = hand.x; hy2 = hand.y + 6; hs = 0.6; hrot = 560; }
  else { hx2 = heldX + (pocketX - heldX) * give; hy2 = heldY + (pocketY - heldY) * give; hs = 0.6 + (0.374 - 0.6) * give; hrot = 560 * (1 - give); }
  const hatShown = t >= 5.6 && t < 21.1;
  const pocket = t < 5.6 || t >= 21.1;
  const hazelStandNow = t >= 17.6;
  const hazelPre = t < 11.0;

  const cam = useCam([
    {t: 0, ...at(980, 600, 1.15)},
    {t: 5.0, ...at(1650, 620, 1.15)},
    {t: 8.0, ...at(1790, 650, 1.25)},
    {t: 9.6, ...at(1930, 720, 1.5)},
    {t: 12.6, ...at(1930, 738, 1.6)},
    {t: 15.6, ...at(1930, 738, 1.6)},
    {t: 17.8, ...at(1720, 650, 1.3)},
    {t: len, ...at(1560, 620, 1.25)},
  ]);

  return (
    <SceneWrap len={len} bg="#10204a">
      <Stage cam={cam}>
        <Layer p={0.6}><Bg src="cliff_far.jpg" w={2900} h={1080} /></Layer>
        <Layer p={1}>
          <Bg src="cliff_near.png" w={2900} h={1080} />
          <GroundShadow x={cometX} y={GY + 6} rx={90} />
          <GroundShadow x={boltsX} y={GY + 12} rx={60} />
          <GroundShadow x={budX} y={GY + 6} rx={80} />
          <Comet x={cometX} y={GY + 4} s={0.72} walk={walking ? 6 : 0} rot={lean} t0={0.5} />
          <Bolts view="side" x={boltsX} y={GY + 10} s={0.69} flip eyes={1} walk={walking ? 4 : 0} t0={0.9} />
          <Bud x={budX} y={GY + 6} s={0.68} head="bare" pocket={pocket} walk={budWalk ? 5 : 0} rot={t < 5.6 ? lean : t < 11 ? 6 : 0} t0={0.3} />
          {hazelPre && <><GroundShadow x={hx} y={GY} rx={85} /><Hazel x={hx} y={GY} s={0.72} walk={walking ? 5 : 0} rot={lean} t0={0} /></>}
          {lying && <><GroundShadow x={crawlX + 150} y={GY + 14} rx={190} o={0.4} /><Sprite name="hazel_side" x={crawlX} y={GY + 6} s={0.66} rot={90} breathe={0.004} sway={0.3} opacity={ramp(t, 11.0, 11.5) * (1 - ramp(t, 17.2, 17.6))} /></>}
          {hazelStandNow && <><GroundShadow x={hazelStandX} y={GY} rx={85} /><Hazel x={hazelStandX} y={GY} s={0.72} t0={0} opacity={ramp(t, 17.4, 17.9)} /></>}
          {/* Hazel 的手臂：从崖边伸下去，手指握住帽子（外套的绿 + 小手） */}
          {reach > 0.01 && (
            <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
              <line x1={handHome.x - 16} y1={handHome.y - 8} x2={hand.x} y2={hand.y} stroke="#4d6a5a" strokeWidth={28} strokeLinecap="round" />
              <line x1={handHome.x - 16} y1={handHome.y - 8} x2={hand.x} y2={hand.y} stroke="#1d2447" strokeWidth={28} strokeLinecap="round" opacity={0.0} />
              <circle cx={hand.x + 2} cy={hand.y + 4} r={15} fill="#efdccf" stroke="#6c5a58" strokeWidth={1.4} />
            </svg>
          )}
          {hatShown && <Sprite name="pebbles_front" x={hx2} y={hy2} s={hs} rot={hrot} clipBottom={t < 6.0 ? 0.34 * (1 - ramp(t, 5.6, 6.0)) : 0} breathe={0.01} sway={0} />}
        </Layer>
      </Stage>
      <Tint color="#7384b4" o={0.4} />
      <Snow amount={1} wind={0.55} speed={1.5} color="236,242,255" />
    </SceneWrap>
  );
};
