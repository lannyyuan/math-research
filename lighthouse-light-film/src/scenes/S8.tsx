import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Glow, Beam} from '../fx/Light';
import {Hazel, Bud, Bolts, Party} from './cast';
import {Bg, SceneWrap, Shot, Tint, useT, ramp, track, lerp, at, cuesOf} from './kit';

// 八、灯塔：高高的、黑黑的；Hazel 换上新灯泡——什么也没发生；发电机要电池——Bolts 说"用我的电池"，眼睛熄灭、再也不动；发动机轰地响起来；大灯亮了
const C = cuesOf('s8-lamp');
const LAMP_CX = 1200, LAMP_BY = 700;   // 灯室透镜的底座中心（与 bg_lamp.py 一致）
const SOCKET = {x: LAMP_CX, y: LAMP_BY - 135};
const GEN = {x: 1200, y: 860};
const LENS = [[-190, 22], [-205, -120], [-180, -330], [-110, -480], [0, -520], [110, -480], [180, -330], [205, -120], [190, 22]];

// ── 外景：夜里的暴风雪，灯塔又高又黑，一行人走过来 ──
const Outside: React.FC = () => {
  const t = useT();
  const x = track(t, [[0.3, 160], [6.2, 1240]]);
  const walking = t > 0.3 && t < 6.2;
  const cam = useCam([
    {t: 0, ...at(1000, 720, 1.1)},
    {t: 3.0, ...at(1140, 700, 1.1)},
    {t: 4.6, ...at(1480, 470, 1.18)},
    {t: 7.4, ...at(1560, 330, 1.28)},
  ]);
  return (
    <Stage cam={cam}>
      <Layer p={0.55}><Bg src="lh_night_far.jpg" w={2900} h={1080} /></Layer>
      <Layer p={1}>
        <Bg src="lh_night_near.png" w={2900} h={1080} />
        {[0, 58, 110, 180].map((d) => <GroundShadow key={d} x={x - d} y={948} rx={44} />)}
        <Party x={x} y={944} s={0.4} walking={walking} comet={{dx: 180}} bud={{dx: 58, head: 'bare', pocket: true}} bolts={{dx: 110, eyes: 1}} />
      </Layer>
    </Stage>
  );
};

// ── 灯室：透镜是黑的；Hazel 把新灯泡拧进灯座，什么也没发生 ──
const LampDark: React.FC = () => {
  const t = useT();
  const cam = useCam([{t: 7.0, ...at(1180, 600, 1.12)}, {t: 11.4, ...at(1200, 600, 1.2)}]);
  const put = ramp(t, 8.0, 9.1);
  const bx = lerp(1130, SOCKET.x, put), by = lerp(600, SOCKET.y - 24, put) - Math.sin(put * Math.PI) * 30;
  const shrug = t > 9.8 && t < 10.8 ? Math.sin((t - 9.8) * Math.PI) * 14 : 0;
  return (
    <Stage cam={cam}>
      <Layer p={0.9} w={2400}><Bg src="lamp_far.jpg" w={2400} h={1080} /></Layer>
      <Layer p={1} w={2400}>
        <Bg src="lamp_near.png" w={2400} h={1080} />
        <Sprite name="bulb" x={bx} y={by} s={0.62} breathe={0} sway={0} opacity={1} />
        <Bud view="front" x={840} y={838 - shrug} s={0.76} head="bare" pocket t0={0.3} />
        <Hazel view="front" x={1020} y={832} s={0.82} t0={0} />
        <Bolts view="front" x={700} y={846} s={0.86} eyes={1} />
      </Layer>
    </Stage>
  );
};

// ── 发电机房：Bolts 交出电池，眼睛熄灭；电池装进去，发动机轰地响起来 ──
const Puff: React.FC<{t: number; t0: number; x: number; y: number}> = ({t, t0, x, y}) => {
  const k = (t - t0) % 2.6;
  if (t < t0 || k < 0) return null;
  const u = k / 2.6;
  return <div style={{position: 'absolute', left: x - 30 - u * 20 + Math.sin(u * 5) * 14, top: y - u * 190, width: 90 + u * 130, height: 90 + u * 130, marginLeft: -(u * 65), borderRadius: '50%', background: 'radial-gradient(circle, rgba(232,238,250,0.95), rgba(200,212,236,0.0) 70%)', opacity: (1 - u) * 1.0}} />;
};

const Generator: React.FC = () => {
  const t = useT();
  const cam = useCam([{t: 10.6, ...at(1120, 600, 1.12)}, {t: 18.0, ...at(1200, 590, 1.18)}, {t: 23.6, ...at(1220, 580, 1.3)}]);
  const eyes = 1 - ramp(t, C[3].t, C[3].t + 2.0);
  // 电池：从 Bolts 胸口滑出 → Hazel 接过 → 放进发电机的电池仓
  const out = ramp(t, 11.8, 12.8), carry = ramp(t, 12.8, 14.6);
  const bx = lerp(640, 660, out) + (1305 - 660) * carry;
  const by = lerp(752, 760, out) + (735 - 760) * carry - Math.sin(carry * Math.PI) * 60;
  const shake = t > C[4].t ? Math.sin(t * 61) * 1.6 + Math.sin(t * 23) * 1.1 : 0;
  const hazelX = lerp(840, 1130, carry);
  const roar = ramp(t, C[4].t, C[4].t + 0.8);
  return (
    <Stage cam={cam}>
      <Layer p={0.9} w={2400}><Bg src="gen_far.jpg" w={2400} h={1080} /></Layer>
      <Layer p={1} w={2400}>
        <div style={{position: 'absolute', inset: 0, transform: `translate(${shake}px, ${shake * 0.6}px)`}}>
          <Bg src="gen_near.png" w={2400} h={1080} />
          {/* 排气管冒烟 */}
          {t > C[4].t && [0, 0.9, 1.8].map((d) => <Puff key={d} t={t} t0={C[4].t + d} x={1460} y={345} />)}
          <Bolts view="front" x={640} y={862} s={0.86} eyes={eyes} breathe={eyes > 0.5 ? 0.012 : 0} sway={eyes > 0.5 ? 0.8 : 0} />
          <Bud view="front" x={900} y={870} s={0.76} head="bare" pocket t0={0.3} />
          <Hazel view="side" x={hazelX} y={864} s={0.8} t0={0} />
          {t > 11.8 && <Sprite name="battery" x={bx} y={by} s={0.62 * (1 - 0.1 * carry)} breathe={0} sway={0} />}
        </div>
        {/* 电缆里的电：一粒粒冷白的光点沿着地上的线跑 */}
        {t > C[4].t + 0.4 && (
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', mixBlendMode: 'screen', opacity: roar}}>
            <path d="M 870 880 C 600 920 300 900 20 940" stroke="#cfe3ff" strokeWidth={5} fill="none" strokeLinecap="round" strokeDasharray="2 46" strokeDashoffset={-t * 220} />
          </svg>
        )}
      </Layer>
    </Stage>
  );
};

// ── 灯室：大灯亮了，光柱从透镜里射出去 ──
const LampLit: React.FC = () => {
  const t = useT();
  const T0 = C[5].t;
  const on = ramp(t, T0, T0 + 1.1);
  const flash = Math.max(0, 1 - Math.abs(t - (T0 + 0.5)) / 0.5) * 0.35;
  const sweep = Math.sin((t - T0) * 0.5) * 2.2;
  const cam = useCam([{t: 22.8, ...at(1200, 560, 1.12)}, {t: 29, ...at(1200, 520, 1.2)}]);
  const lens = LENS.map(([dx, dy]) => `${LAMP_CX + dx},${LAMP_BY + dy}`).join(' ');
  return (
    <Stage cam={cam}>
      <Layer p={0.9} w={2400}><Bg src="lamp_far.jpg" w={2400} h={1080} /></Layer>
      <Layer p={1} w={2400}>
        <Bg src="lamp_near.png" w={2400} h={1080} />
        <Sprite name="bulb" x={SOCKET.x} y={SOCKET.y - 24} s={0.62} breathe={0} sway={0} />
        {/* 透镜里亮起暖色的光 */}
        <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'screen', opacity: on, pointerEvents: 'none'}}>
          <defs>
            <radialGradient id="lensLit" cx="50%" cy="50%" r="55%">
              <stop offset="0" stopColor="#fffbe6" />
              <stop offset="0.35" stopColor="#ffe9a0" />
              <stop offset="1" stopColor="#f2b04a" />
            </radialGradient>
          </defs>
          <polygon points={lens} fill="url(#lensLit)" opacity={0.95} />
        </svg>
        {/* 棱镜的一圈圈线条（亮着的时候还能看清透镜的结构） */}
        <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'multiply', opacity: on * 0.55, pointerEvents: 'none'}}>
          {Array.from({length: 9}, (_, k) => {
            const y = LAMP_BY - 20 - k * 52;
            const half = 200 * (1 - Math.pow(k / 10, 2.2));
            return <path key={k} d={`M ${LAMP_CX - half} ${y} Q ${LAMP_CX} ${y + 26} ${LAMP_CX + half} ${y}`} stroke="#e8a94d" strokeWidth={3} fill="none" />;
          })}
          {Array.from({length: 9}, (_, j) => <line key={j} x1={LAMP_CX + (j - 4) * 46} y1={LAMP_BY} x2={LAMP_CX + (j - 4) * 30} y2={LAMP_BY - 480} stroke="#e8a94d" strokeWidth={2} opacity={0.6} />)}
        </svg>
        <Bud view="front" x={880} y={838} s={0.76} head="bare" pocket t0={0.3} />
        <Hazel view="front" x={1020} y={832} s={0.82} t0={0} />
        {/* 光：先是一团白热的光晕，然后向两边射出光柱——全片最亮的地方 */}
        <Glow x={LAMP_CX} y={LAMP_BY - 300} r={760} opacity={on * 0.9} />
        <Glow x={LAMP_CX} y={LAMP_BY - 300} r={260} opacity={on} />
        <Beam x={LAMP_CX} y={LAMP_BY - 300} angle={180 + sweep} length={1300} spread={13} opacity={on * 0.95} />
        <Beam x={LAMP_CX} y={LAMP_BY - 300} angle={0 - sweep} length={1300} spread={13} opacity={on * 0.95} />
      </Layer>
      <div style={{position: 'absolute', inset: 0, background: '#fff6d8', opacity: flash, mixBlendMode: 'screen', pointerEvents: 'none'}} />
    </Stage>
  );
};

export const S8: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  return (
    <SceneWrap len={len} bg="#0a1230">
      <Shot to={7.5} fade={0.9}><Outside /></Shot>
      <Shot from={7.5} to={11.0} fade={0.8}><LampDark /></Shot>
      <Shot from={11.0} to={23.4} fade={0.9}><Generator /></Shot>
      <Shot from={23.4} fade={1.0}><LampLit /></Shot>
      <Tint color="#6a7cb0" o={t < 23.4 ? 0.28 : 0.18} />
      {t < 7.6 && <Snow amount={0.9} wind={0.4} speed={1.3} color="236,242,255" />}
    </SceneWrap>
  );
};
