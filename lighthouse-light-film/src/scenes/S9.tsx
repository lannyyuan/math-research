import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Glow, Beam} from '../fx/Light';
import {Hazel, Bud, Bolts, Comet} from './cast';
import {Bg, SceneWrap, Shot, Tint, useT, ramp, track, lerp, at, cuesOf} from './kit';

// 九、暴风雪过去的夜里：灯塔的光柱扫过海湾；远处一点小小的光回应了；船一艘艘顺着光回港；Dad 的船靠岸，他走上码头抱住 Hazel 和 Bud
const C = cuesOf('s9-boats');
const BAY_LANTERN = {x: 2300, y: 264};
const DOCK_LANTERN = {x: 2380, y: 245};

const Bay: React.FC = () => {
  const t = useT();
  const cam = useCam([{t: 0, ...at(1900, 540, 1.0)}, {t: 6.0, ...at(1860, 540, 1.0)}, {t: 13.8, ...at(1150, 540, 1.06)}]);
  const sweep = 186 + 8 * Math.sin(t * 0.55);
  // 远处的小光：一闪一闪，像在回答
  const blink = t > 2.0 ? ramp(t, 2.0, 2.6) * (0.55 + 0.45 * Math.sin((t - 2.0) * 3.4) ** 2) : 0;
  const boat = (x0: number, x1: number, y: number, s: number, t0: number, k: number, name = 'boat_s') => {
    const u = ramp(t, t0, 14.5);
    const o = ramp(t, t0, t0 + 1.4);
    const x = lerp(x0, x1, u);
    const bob = Math.sin(t * 1.3 + k) * 3;
    return (
      <React.Fragment key={k}>
        <Sprite name={name} x={x} y={y + bob} s={s} opacity={o} breathe={0} sway={1.2} t0={k} />
        <Glow x={x - (name === 'boat_dad' ? 13 : 7.6) * s} y={y + bob - (name === 'boat_dad' ? 119 : 68) * s} r={(name === 'boat_dad' ? 150 : 110) * s} opacity={0.75 * o} />
      </React.Fragment>
    );
  };
  return (
    <Stage cam={cam}>
      <Layer p={0.6}>
        <Bg src="bay_far.jpg" w={2900} h={1080} />
        {/* 灯塔：灯室一直亮着，光柱缓缓扫过海面 */}
        <Glow x={BAY_LANTERN.x} y={BAY_LANTERN.y} r={230} opacity={0.95} />
        <Beam x={BAY_LANTERN.x} y={BAY_LANTERN.y} angle={sweep} length={2000} spread={7} opacity={0.9} />
        <Beam x={BAY_LANTERN.x} y={BAY_LANTERN.y} angle={sweep + 180} length={500} spread={5} opacity={0.35} />
        {/* 港口的灯 */}
        {[180, 640, 1100].map((x, i) => <Glow key={x} x={x} y={526} r={110 + 6 * Math.sin(t * 2 + i)} opacity={0.75} />)}
        <Glow x={1330} y={484} r={46} opacity={blink} />
        {t > 7 && (
          <>
            {boat(2750, 1450, 590, 0.62, 7.0, 1)}
            {boat(3000, 1700, 640, 0.78, 7.6, 2)}
            {boat(3250, 2000, 560, 0.5, 7.2, 3)}
            {boat(3500, 1900, 600, 0.55, 9.6, 4, 'boat_dad')}
          </>
        )}
      </Layer>
      <Layer p={1}><Bg src="bay_near.png" w={2900} h={1080} /></Layer>
    </Stage>
  );
};

const Dock: React.FC = () => {
  const t = useT();
  const cam = useCam([
    {t: 13.0, ...at(1300, 640, 1.12)},
    {t: 17.0, ...at(1600, 650, 1.3)},
    {t: 22.0, ...at(1760, 620, 1.18)},
    {t: 28, ...at(1860, 560, 1.0)},
  ]);
  const sweep = 190 + 9 * Math.sin(t * 0.6);
  // Dad 的船靠岸
  const boatX = track(t, [[13.0, 2700], [17.0, 1930]]);
  const boatBob = Math.sin(t * 1.4) * 3;
  // Dad：站在船上 → 走上码头 → 张开手臂
  const dadStep = ramp(t, 15.6, 17.6);
  const dadX = lerp(1960, 1710, dadStep);
  const dadY = lerp(742, 884, dadStep);
  const dadS = lerp(0.62, 0.9, dadStep);
  const dadO = ramp(t, 15.2, 15.8);
  // 孩子们跑过去
  const run = ramp(t, 17.2, 19.0);
  const hazelX = lerp(1010, 1668, run), budX = lerp(880, 1572, run);
  const hug = ramp(t, 19.0, 19.8);
  return (
    <Stage cam={cam}>
      <Layer p={0.6}>
        <Bg src="dock_far.jpg" w={2900} h={1080} />
        <Glow x={DOCK_LANTERN.x} y={DOCK_LANTERN.y} r={230} opacity={0.95} />
        <Beam x={DOCK_LANTERN.x} y={DOCK_LANTERN.y} angle={sweep} length={2200} spread={7} opacity={0.85} />
        {[[300, 560], [460, 556], [620, 562], [1500, 560], [1650, 560]].map(([x, y], i) => <Glow key={i} x={x} y={y} r={44} opacity={0.5} />)}
      </Layer>
      <Layer p={0.9}>
        <Sprite name="boat_dad" x={boatX} y={748 + boatBob} s={1.0} breathe={0} sway={0.6} />
        <Glow x={boatX - 13} y={748 + boatBob - 119} r={170} opacity={0.8} />
      </Layer>
      <Layer p={1}>
        <Bg src="dock_near.png" w={2900} h={1080} />
        <GroundShadow x={dadX} y={dadY} rx={110 * dadS} o={0.45 * dadO} />
        <Sprite name="dad" x={dadX} y={dadY} s={dadS} opacity={dadO} breathe={0.006} sway={0.3} />
        {/* 左边：Comet 和一动不动的 Bolts（眼睛熄着）一直陪着 */}
        <GroundShadow x={470} y={890} rx={90} />
        <Comet x={470} y={888} s={0.72} t0={0.5} />
        <GroundShadow x={640} y={896} rx={60} />
        <Bolts view="front" x={640} y={896} s={0.86} eyes={0} breathe={0} sway={0} />
        <GroundShadow x={budX} y={878} rx={80} />
        <GroundShadow x={hazelX} y={872} rx={85} />
        <Bud x={budX} y={878} s={0.7} head="bare" pocket walk={run > 0 && run < 1 ? 6 : 0} t0={0.3} />
        <Hazel x={hazelX} y={872} s={0.74} walk={run > 0 && run < 1 ? 6 : 0} t0={0} />
      </Layer>
    </Stage>
  );
};

export const S9: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  return (
    <SceneWrap len={len} bg="#0a1230">
      <Shot to={13.6} fade={1.2}><Bay /></Shot>
      <Shot from={13.6} fade={1.2}><Dock /></Shot>
      <Tint color="#6a7cb0" o={0.12} />
      <Snow amount={ramp(t, 0, 12) < 1 ? 0.45 - 0.3 * ramp(t, 0, 12) : 0.12} wind={0.1} color="236,242,255" />
    </SceneWrap>
  );
};
