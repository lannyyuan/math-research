import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Party, Comet} from './cast';
import {Bg, SceneWrap, Shot, SignText, Tint, useT, ramp, lerp, at, cuesOf} from './kit';
import {GroundShadow} from '../fx/Sprite';

// 四、城里：公交停了（站牌 "NO BUSES TODAY. SNOW."）、火车也停了（"No trains today."）→ 走回去；路上小驯鹿 Comet 在后面跟了上来
const C = cuesOf('s4-walk');
const SIGN_BUS = [1110, 560, 340, 150];
const SIGN_TRAIN = [2010, 520, 300, 120];

const Town: React.FC = () => {
  const t = useT();
  // 队伍的位置（Hazel）：走进镜头 → 停在站牌前读 → 走到车站 → 读 → 继续往右走出城
  const x =
    t < 2.0 ? lerp(300, 900, ramp(t, 0, 2.0))
    : t < 5.3 ? 900
    : t < 8.2 ? lerp(900, 1880, ramp(t, 5.3, 8.2))
    : t < 9.8 ? 1880
    : lerp(1880, 2700, ramp(t, 9.8, 13.0));
  const walking = t < 2.0 || (t > 5.3 && t < 8.2) || t > 9.8;
  const cam = useCam([
    {t: 0, ...at(820, 540, 1.05)},
    {t: 4.8, ...at(1000, 540, 1.1)},
    {t: 8.4, ...at(1860, 540, 1.1)},
    {t: 12, ...at(1960, 540, 1.04)},
    {t: 14, ...at(1960, 540, 1.04)},
  ]);
  return (
    <Stage cam={cam}>
      <Layer p={0.6}><Bg src="town_far.jpg" w={2900} h={1080} /></Layer>
      <Layer p={1}>
        <Bg src="town_near.png" w={2900} h={1080} />
        <SignText x={SIGN_BUS[0]} y={SIGN_BUS[1]} w={SIGN_BUS[2]} h={SIGN_BUS[3]} lines={['NO BUSES', 'TODAY. SNOW.']} size={36} o={ramp(t, 0.8, 1.6)} />
        <SignText x={SIGN_TRAIN[0]} y={SIGN_TRAIN[1]} w={SIGN_TRAIN[2]} h={SIGN_TRAIN[3]} lines={['No trains', 'today.']} size={36} />
        {[0, 105, 200, 330].map((d) => <GroundShadow key={d} x={x - d} y={904} rx={80} />)}
        <Party x={x} y={900} walking={walking} comet={false} bud={{head: 'bare', pocket: false}} />
      </Layer>
    </Stage>
  );
};

const Country: React.FC = () => {
  const t = useT();
  // 队伍朝右走；到 21 秒左右停下回头看 Comet
  const x = lerp(520, 1980, ramp(t, 11.5, 21.0));
  const walking = t > 11.5 && t < 21.0;
  const stop = ramp(t, 21.0, 21.4);
  const camx = lerp(900, 1750, ramp(t, 11.5, 22));
  const cam = useCam([
    {t: 11.5, ...at(camx, 540, 1.05)},
    {t: 26.5, ...at(1750, 540, 1.1)},
  ]);
  // 队伍在 camx 附近：用 camx 当镜头中心；这里让镜头跟随 x
  const cam2 = {x: lerp(0, 1, 0), y: 0, z: 1};
  void cam2;
  // Comet 从左边跑上来
  const cx = lerp(-200, x - 380, ramp(t, 14.6, 19.5));
  const cometWalk = t > 14.6 && t < 21.4 ? 6 : 0;
  const settle = ramp(t, 20.6, 22.2);
  const cometX = lerp(cx, x - 300, settle);
  const nod = t > C[4].t && t < C[4].t + 2.4 ? Math.sin((t - C[4].t) * 7) * 5 : 0;
  const face = t > 21.2 ? -1 : 1;
  return (
    <Stage cam={{...cam, x: camx - 960 + (t > 21 ? 0 : 0), y: 0}}>
      <Layer p={0.6}><Bg src="country_far.jpg" w={2900} h={1080} /></Layer>
      <Layer p={1}>
        <Bg src="country_near.png" w={2900} h={1080} />
        {[0, 105, 200].map((d) => <GroundShadow key={d} x={x - d} y={898} rx={80} />)}
        <GroundShadow x={cometX} y={898} rx={90} />
        <Party x={x} y={895} walking={walking} face={face === -1 ? -1 : 1} bud={{head: 'bare', pocket: false, dx: 105}} comet={false} />
        <Comet x={cometX} y={896} s={0.72} walk={cometWalk} rot={nod} t0={0.5} />
      </Layer>
    </Stage>
  );
};

export const S4: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  return (
    <SceneWrap len={len} bg="#6c7ea4">
      <Shot to={12.6}><Town /></Shot>
      <Shot from={12.6}><Country /></Shot>
      <Tint color="#a9b9de" o={0.18 + 0.25 * ramp(t, 0, len)} />
      <Snow amount={0.8} wind={0.16} />
    </SceneWrap>
  );
};
