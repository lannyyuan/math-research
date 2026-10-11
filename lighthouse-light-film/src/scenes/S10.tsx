import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Glow, Beam, CoolGlow} from '../fx/Light';
import {Hazel, Bud, Bolts} from './cast';
import {Bg, SceneWrap, Shot, useT, ramp, track, lerp, at, cuesOf} from './kit';
import {W, H} from '../palette';

// 十、圣诞节早上：天晴了，Mrs Mallet 给 Bolts 装上新电池，他的眼睛亮起来（黄色、亮亮的）。晚上，Hazel 自己关掉了床头灯——房间黑了，可是不再可怕。
const C = cuesOf('s10-morning');
const FLOOR = 866;

/** 只在一块矩形里下雪（窗外）：把整屏的雪裁到窗框里 */
const WindowSnow: React.FC<{x: number; y: number; w: number; h: number; amount: number}> = ({x, y, w, h, amount}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, overflow: 'hidden', pointerEvents: 'none'}}>
    <div style={{position: 'absolute', left: -x, top: -y, width: W, height: H}}><Snow amount={amount} wind={0.1} speed={0.5} /></div>
  </div>
);

const Living: React.FC = () => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(1200, 560, 1.0)},
    {t: 6.5, ...at(1240, 580, 1.06)},
    {t: 8.4, ...at(1180, 610, 1.3)},
    {t: 13.2, ...at(1180, 600, 1.34)},
  ]);
  // Mrs Mallet 走进来，站到桌边
  const mx = track(t, [[2.4, -100], [6.0, 900]]);
  const mWalk = t > 2.4 && t < 6.0 ? 4 : 0;
  // 电池：从她手里到 Bolts 胸口
  const put = ramp(t, 7.4, 8.6);
  const handX = mx + 129, handY = FLOOR - 126;
  const bx = lerp(handX, 1180, put), by = lerp(handY, 560, put);
  const eyes = ramp(t, 8.8, 9.8);
  const hop = t > 9.8 && t < 10.5 ? Math.sin((t - 9.8) / 0.7 * Math.PI) * 14 : 0;
  // Hazel 跑过来抱 Bolts
  const hz = track(t, [[10.0, 1480], [11.6, 1318]]);
  const hug = ramp(t, 11.4, 12.4);
  const TABLE_S = 0.75, SURFACE = FLOOR - 210;
  return (
    <Stage cam={cam}>
      <Layer p={0.95} w={2400}>
        <Bg src="living_far.jpg" w={2400} h={1080} />
        <WindowSnow x={200} y={110} w={500} h={450} amount={0.22} />
      </Layer>
      <Layer p={1} w={2400}>
        <GroundShadow x={540} y={FLOOR} rx={200} o={0.3} />
        <Sprite name="grandad_chair" x={540} y={FLOOR} s={0.9} breathe={0.006} sway={0.2} t0={0.5} />
        <GroundShadow x={1180} y={FLOOR + 4} rx={230} o={0.3} />
        <Sprite name="table" x={1180} y={FLOOR + 2} s={TABLE_S} breathe={0} sway={0} />
        <GroundShadow x={1180} y={SURFACE + 2} rx={60} o={0.3} />
        <Bolts view="front" x={1180} y={SURFACE + 4 - hop} s={0.8} eyes={eyes} rot={-5 * hug} breathe={eyes > 0.5 ? 0.012 : 0} sway={eyes > 0.5 ? 0.7 : 0} />
        {t > 7.2 && t < 8.8 && <Sprite name="battery" x={bx} y={by} s={0.6} opacity={1 - ramp(t, 8.3, 8.8)} breathe={0} sway={0} />}
        <GroundShadow x={mx} y={FLOOR} rx={90} o={0.4} />
        <Sprite name="mallet" x={mx} y={FLOOR} s={0.86} walk={mWalk} breathe={0.01} sway={0.4} t0={0.5} />
        <GroundShadow x={1600} y={FLOOR + 6} rx={80} />
        <Bud view="front" x={1600} y={FLOOR + 6} s={0.7} head="bare" pocket t0={0.3} />
        <GroundShadow x={hz} y={FLOOR + 2} rx={85} />
        <Hazel view="front" x={hz} y={FLOOR + 2} s={0.74} rot={7 * hug} walk={t > 10.0 && t < 11.6 ? 5 : 0} t0={0} />
      </Layer>
    </Stage>
  );
};

const LAMP = {x: 1230, y: 575};
const WIN = {x: 1460, y: 130, w: 500, h: 430};
const LANTERN = {x: 380, y: 214};   // 窗内坐标

const Bedroom: React.FC = () => {
  const t = useT();
  const OFF = C[3].t + 2.5;        // 关灯的时刻（"No. You can turn it off."）
  const lampOn = t < OFF ? 1 : Math.max(0, 1 - (t - OFF) / 0.18);
  const dark = ramp(t, OFF, OFF + 1.4);
  const cam = useCam([{t: 12.4, ...at(1050, 560, 1.0)}, {t: 19.0, ...at(1010, 580, 1.1)}, {t: 34, ...at(1050, 560, 1.04)}]);
  // Hazel：先正面坐着，转向台灯（侧面），关灯
  const toSide = ramp(t, C[3].t + 0.4, C[3].t + 1.2);
  const lean = ramp(t, C[3].t + 1.4, OFF) * 7;
  const press = t > OFF - 0.2 && t < OFF + 0.4 ? 1 : 0;
  // Mum：站在门口（走廊的光从她身后照来）；说完话点点头，门慢慢关上、门口的光暗下去
  const nod = t > C[3].t + 3.0 && t < C[3].t + 4.2 ? Math.sin((t - C[3].t - 3.0) / 1.2 * Math.PI) * 3.5 : 0;
  const doorDark = ramp(t, C[3].t + 3.8, C[3].t + 5.0);
  const mumO = ramp(t, 12.9, 13.6) * (1 - ramp(t, C[3].t + 3.8, C[3].t + 4.8));
  // 灯塔的光柱每 9 秒扫过墙一次
  const ph = ((t + 3) % 9) / 9;
  const patchX = lerp(2500, -500, ph);
  const patchO = (0.14 + 0.2 * dark) * Math.sin(Math.PI * Math.min(1, Math.max(0, ph * 1.0))) ** 1.5;
  const sweepAng = 168 + 26 * Math.sin(t * 0.7);
  return (
    <>
      <Stage cam={cam}>
        <Layer p={0.95} w={2400}>
          <Bg src="bed_far.jpg" w={2400} h={1080} />
          <div style={{position: 'absolute', left: 90, top: 230, width: 240, height: 520, background: '#0d1636', opacity: doorDark * 0.9}} />
          <WindowSnow x={WIN.x} y={WIN.y} w={WIN.w} h={WIN.h} amount={0.2} />
        </Layer>
        <Layer p={1} w={2400}>
          <GroundShadow x={210} y={752} rx={80} o={0.0} />
          <Sprite name="mum" x={210} y={754} s={0.95} rot={nod} opacity={mumO} breathe={0.004} sway={0.2} />
          <Hazel view="front" x={730} y={868} s={0.8} opacity={1 - toSide} breathe={0.008} sway={0.4} t0={0} />
          <Hazel view="side" x={750 + lean * 3} y={868} s={0.8} rot={lean} opacity={toSide} breathe={0.008} sway={0.3} t0={0.4} />
          <Bg src="bed_near.png" w={2400} h={1080} />
        </Layer>
      </Stage>
      {/* 台灯的光：冷白，不是暖色。关灯：啪地灭掉。 */}
      <Stage cam={cam}>
        <Layer p={1} w={2400}>
          <CoolGlow x={LAMP.x} y={LAMP.y} r={520} opacity={0.55 * lampOn} />
          <CoolGlow x={LAMP.x} y={LAMP.y - 10} r={150} opacity={0.9 * lampOn} />
          {press > 0 && <div style={{position: 'absolute', left: LAMP.x - 90, top: LAMP.y + 160, width: 180, height: 14, background: '#f4faff', mixBlendMode: 'screen', opacity: 0.0}} />}
        </Layer>
      </Stage>
      {/* 灯一关，房间沉到深蓝里 */}
      <div style={{position: 'absolute', inset: 0, background: '#0c1538', opacity: 0.62 * dark, mixBlendMode: 'multiply', pointerEvents: 'none'}} />
      <div style={{position: 'absolute', inset: 0, background: '#0a1230', opacity: 0.18 * dark, pointerEvents: 'none'}} />
      {/* 窗外：远处的灯塔，灯室亮着（暖色），光柱在窗里扫来扫去 */}
      <Stage cam={cam}>
        <Layer p={0.95} w={2400}>
          <div style={{position: 'absolute', left: WIN.x, top: WIN.y, width: WIN.w, height: WIN.h, overflow: 'hidden', pointerEvents: 'none'}}>
            <Glow x={LANTERN.x} y={LANTERN.y} r={64} opacity={0.95} />
            <Beam x={LANTERN.x} y={LANTERN.y} angle={sweepAng} length={900} spread={5} opacity={0.9} />
          </div>
          {/* 光柱扫过墙：一条柔和的暖光带，从右往左慢慢滑过 */}
          <div style={{position: 'absolute', left: patchX, top: 60, width: 360, height: 900, transform: 'skewX(-18deg)', background: 'linear-gradient(90deg, rgba(255,226,150,0), rgba(255,226,150,0.9) 50%, rgba(255,226,150,0))', filter: 'blur(26px)', opacity: patchO, mixBlendMode: 'screen', pointerEvents: 'none'}} />
        </Layer>
      </Stage>
    </>
  );
};

export const S10: React.FC<{len: number}> = ({len}) => (
  <SceneWrap len={len} bg="#0a1230" fadeOut={84}>
    <Shot to={13.2} fade={1.3}><Living /></Shot>
    <Shot from={13.2} fade={1.3}><Bedroom /></Shot>
  </SceneWrap>
);
