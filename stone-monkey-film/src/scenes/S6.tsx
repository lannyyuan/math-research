import React from 'react';
import {Stage, Layer, useCam, project} from '../fx/Stage';
import {GroundShadow, Sprite} from '../fx/Sprite';
import {Lit, Pool, FireGlow} from '../fx/Light';
import {ShotStack} from '../fx/ShotStack';
import {LampLight} from '../fx/LampLight';
import {VariantCtx, Variant} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, track, at, atg, lerp, clamp01, cuesOf} from './kit';
import {Pair, Pearl, pearlPos, Rider, Nainai, KID_S, HORSE_S, SADDLE} from './cast';

// 第六部 点亮那盏灯：鼓声升到天上，云裂一道缝，守天门的神（白衣、金光、玉尺）→ 云路，石娃骑马向南 → 火山上摇铃击鼓，火苗变成火种飞进袋里
// → 回村，奶奶递出红布包着的银针 → 五样交给神，银针接好断心，点火，灯亮了（碗、盆、车轮、满天）→ 晨光村口，奶奶在人群里落泪
const C = cuesOf('s6-lamp');
const GY = 832;
const T_B = 13.8, T_C = 22.4, T_D = 30.2, T_E = 43.0;
const DOOR_X = 691;                    // 奶奶家的门（和第一部同一块村口板）
const LAMP = {x: 1450, dishY: 444};    // 灯盘中心（lamp_sky_near 上的灯座）

const roadY = (x: number) => 840 - 58 * Math.pow(clamp01((x - 250) / 2570), 1.2);   // 云路的路面
const bez = (a: number[], b: number[], c: number[], u: number) => [(1 - u) * (1 - u) * a[0] + 2 * (1 - u) * u * b[0] + u * u * c[0], (1 - u) * (1 - u) * a[1] + 2 * (1 - u) * u * b[1] + u * u * c[1]];
const bump = (u: number) => Math.sin(clamp01(u) * Math.PI);

const GodGlow: React.FC<{x: number; y: number; r: number; o: number}> = ({x, y, r, o}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity: o, mixBlendMode: 'screen', pointerEvents: 'none',
    background: 'radial-gradient(circle, rgba(223,212,172,0.7) 0%, rgba(207,194,154,0.35) 30%, rgba(207,194,154,0.1) 58%, rgba(207,194,154,0) 75%)'}} />
);

/** 马：站在路上或走，facing right 默认；flip = 朝左 */
const Horse: React.FC<{x: number; y: number; flip?: boolean; moving?: boolean; opacity?: number}> = ({x, y, flip = false, moving = false, opacity = 1}) => (
  <>
    <GroundShadow x={x} y={y + 4} rx={170} o={0.4 * opacity} />
    <Sprite name="horse_side" x={x} y={y} s={HORSE_S} flip={flip} walk={moving ? 4 : 0} opacity={opacity} breathe={0.006} sway={0.3} />
  </>
);

// ───────── 镜头 A：云海。云缝、守天门的神、凤凰；神一指，云路出现；石娃上马
const ShotA: React.FC = () => {
  const t = useT();
  const kx0 = track(t, [[0.2, 380], [2.0, 860]]);
  const walkingA = t > 0.2 && t < 2.0;
  const godO = ramp(t, C[0].t, C[0].t + 1.8);
  const road = ramp(t, 10.4, 12.6);
  const horseX = track(t, [[10.8, 160], [12.2, 700], [12.9, 700], [15.7, 1760]]);
  const hY = roadY(horseX) - 18;
  const mount = ramp(t, 12.4, 13.2);
  const riding = t >= 12.4;
  const bob = t > 13.2 ? -Math.abs(Math.sin(t * 5.2)) * 4 : 0;
  const hipX = lerp(kx0 + 4, horseX + SADDLE.dx, mount), hipY = lerp(GY + 4 - 118, hY + 4 + SADDLE.dy, mount) - bump(mount) * 46 + bob;
  const cam = useCam([{t: 0, ...atg(1080, 1.04)}, {t: 11, ...atg(1160, 1.08)}, {t: 15.7, ...atg(1620, 1.1)}]);
  // 三件宝摆在云上（宝珠、雪铃、金鼓），神说“还有两样”之后收起
  const put = [7.4, 8.0, 8.6].map((x) => ramp(t, x, x + 0.6));
  const gone = ramp(t, 10.0, 10.9);
  const hand = pearlPos(kx0, GY + 4, KID_S, false, 'side');
  const u1 = ramp(t, 7.2, 8.0), u2 = ramp(t, 10.0, 10.9);
  const REST = [940, GY - 34];
  const pearlPt = t < 10.0 ? [lerp(hand.x, REST[0], u1), lerp(hand.y, REST[1], u1) - bump(u1) * 60] : [lerp(REST[0], hand.x, u2), lerp(REST[1], hand.y, u2) - bump(u2) * 50];
  const phx = (a: number) => lerp(-200, 3000, clamp01((t - a) / 5.2));
  const flap = (Math.floor(t / 0.28) % 2) === 0;
  const gp = project(cam, 1, 1530, GY - 260, 2900, 1080);
  const pp = riding ? project(cam, 1, hipX + 51.5 * KID_S, hipY - 60 * KID_S, 2900, 1080) : project(cam, 1, pearlPt[0], pearlPt[1], 2900, 1080);
  const pools: Pool[] = [{x: pp.x, y: pp.y, r: 330 * pp.zoom, k: 'pearl'}, {x: gp.x, y: gp.y, r: 460 * gp.zoom * godO, k: 'none', o: 0.8 * godO}];
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="sky_gate_far" /></Layer>
      <Layer p={0.62}><Bg name="sky_gate_mid" /></Layer>
      <Layer p={1}>
        <Bg name="sky_gate_near" />
        <div style={{position: 'absolute', left: 0, top: 0, width: 2900, height: 1080, clipPath: `inset(0 ${100 - 100 * road}% 0 0)`}}><Bg name="cloud_road" /></div>
        <GodGlow x={1530} y={GY - 260} r={420} o={godO} />
        <GroundShadow x={1530} y={GY + 4} rx={150} o={0.4 * godO} />
        <Sprite name="god" x={1530} y={GY + 4} s={0.85} opacity={godO} breathe={0.008} sway={0.6} />
        {[0, 1].map((i) => {
          const x = phx(5.0 + i * 0.8), y = 250 + i * 70 + Math.sin(t * 1.3 + i) * 14;
          return x > -150 && x < 2950 ? <Sprite key={i} name={(flap !== (i === 1)) ? 'phoenix_a' : 'phoenix_b'} x={x} y={y} s={0.6} breathe={0} sway={0} /> : null;
        })}
        {t > 7.4 && t < 11.0 && (
          <>
            <Sprite name="bell" x={1010} y={GY + 2} s={0.34 * (0.6 + 0.4 * put[1])} opacity={put[1] * (1 - gone)} breathe={0} sway={0} v="lit" alwaysShow />
            <Sprite name="drum" x={1110} y={GY + 4} s={0.4 * (0.6 + 0.4 * put[2])} opacity={put[2] * (1 - gone)} breathe={0} sway={0} v="lit" alwaysShow />
          </>
        )}
        {!riding && <Pearl x={pearlPt[0]} y={pearlPt[1]} />}
        {riding && <Horse x={horseX} y={hY + bob} moving={t > 13.2 || (t > 10.8 && t < 12.2)} />}
        {riding ? <Rider hx={hipX} hy={hipY} legRot={lerp(0, -9, mount)} /> : (
          <>
            <GroundShadow x={kx0} y={GY + 6} rx={90} o={0.45} />
            <Pair x={kx0} y={GY + 4} walk={walkingA ? 6 : 0} />
          </>
        )}
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

// ───────── 镜头 B：南方火山。摇铃、鼓鸣，火苗跳起来，变成一团，飞进袋里——那是火种
const ShotB: React.FC = () => {
  const t = useT();
  const hX = track(t, [[T_B + 0.2, 560], [T_B + 2.4, 1080]]);
  const moving = t < T_B + 2.4;
  const hipX = hX + SADDLE.dx, hipY = GY + 4 + SADDLE.dy;
  const cam = useCam([{t: T_B, ...at(1250, 560, 1.0)}, {t: T_C + 1, ...at(1560, 560, 1.0)}]);
  const ring = [15.5, 16.4].map((a) => clamp01((t - a) / 1.6));
  const shake = t > 15.3 && t < 17.0 ? Math.sin(t * 40) * 3 : 0;
  const crater = [1900, 216];
  const grow = ramp(t, 16.4, 17.7);
  const fly = ramp(t, 17.7, 20.3);
  const pack = [hipX - 24 * KID_S, hipY - 66 * KID_S];
  const [fx, fy] = fly > 0 ? bez(crater, [1560, 70], pack, fly) : crater;
  const fs = lerp(0.14, 0.42, grow) * (fly > 0 ? lerp(1, 0.4, fly) : 1);
  const fo = ramp(t, 16.4, 16.9);
  const hold = ramp(t, 20.0, 20.5);           // 火种在袋里，袋口透一点光
  const hand = [hipX + 51.5 * KID_S, hipY - 60 * KID_S];
  const pp = project(cam, 1, hand[0], hand[1], 2900, 1080);
  const fp = project(cam, 1, fx, fy, 2900, 1080);
  const pools: Pool[] = [{x: pp.x, y: pp.y, r: 330 * pp.zoom, k: 'pearl'}, {x: fp.x, y: fp.y, r: 260 * fp.zoom * fo, k: 'fire', o: 0.9 * fo}];
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="volcano_far" /></Layer>
      <Layer p={0.62}><Bg name="volcano_mid" /></Layer>
      <Layer p={1}>
        <Bg name="volcano_near" />
        <Horse x={hX} y={GY + 4} moving={moving} />
        <Rider hx={hipX} hy={hipY} legRot={-9} />
        <Sprite name="bell" x={hand[0] + 6 + shake} y={hand[1] + 34} s={0.15} rot={shake * 2} breathe={0} sway={0} v="lit" alwaysShow opacity={ramp(t, 15.0, 15.4) * (1 - ramp(t, 17.2, 17.6))} />
        {fo > 0.02 && fly < 1 && <Sprite name="fire" x={fx} y={fy + 40 * fs} s={fs} opacity={fo} breathe={0} sway={1.2} v="lit" alwaysShow />}
        {hold > 0 && <FireGlow x={pack[0]} y={pack[1]} r={70} o={0.6 * hold} />}
      </Layer>
    </Stage>
  );
  const rp = project(cam, 1, hand[0] + 6, hand[1] + 30, 2900, 1080);
  return (
    <>
      <Lit world={world} pools={pools} />
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
        {ring.map((q, i) => (q <= 0 || q >= 1 ? null : (
          <circle key={i} cx={rp.x} cy={rp.y} r={(30 + q * 300) * rp.zoom} fill="none" stroke="#efe8d8" strokeWidth={3 * (1 - q) + 0.8} opacity={0.7 * (1 - q)} />
        )))}
        {[0, 0.5].map((d, i) => {                  // 鼓鸣：从火山脚下一圈圈传出去
          const q = (t - 16.2 - d) / 1.8;
          if (q <= 0 || q >= 1) return null;
          const dp = project(cam, 1, 1900, 800, 2900, 1080);
          return <ellipse key={i} cx={dp.x} cy={dp.y} rx={(80 + q * 700) * dp.zoom} ry={(20 + q * 120) * dp.zoom} fill="none" stroke="#efe8d8" strokeWidth={2.4 * (1 - q) + 0.6} opacity={0.5 * (1 - q)} />;
        })}
      </svg>
    </>
  );
};

// ───────── 镜头 C：夜里的村口。奶奶在门口，红布包着银针：“拿去。针尖朝上，别扎手。”
const ShotC: React.FC = () => {
  const t = useT();
  const tc = t - T_C;
  const horseX = track(tc, [[0.2, 1740], [1.6, 1080], [5.8, 1080], [8.0, 1980]]);
  const turn = ramp(tc, 5.75, 6.05);                               // 掉头：向左 → 向右（两个朝向淡入淡出）
  const dis = ramp(tc, 1.7, 2.5), mount = ramp(tc, 5.4, 5.75);
  const SX = 940;                                                  // 下马后石娃站的位置
  const standHip = [SX, GY + 4 - 118];
  const hipL = [horseX - SADDLE.dx, GY + 4 + SADDLE.dy];           // 朝左骑在马上的髋
  const bobR = tc > 6.1 ? -Math.abs(Math.sin(t * 5.2)) * 4 : 0;
  const hipR = [horseX + SADDLE.dx, GY + 4 + SADDLE.dy + bobR];
  const standing = tc >= 2.5 && tc < 5.4;
  const hipLeft = tc < 2.5 ? [lerp(hipL[0], standHip[0], dis), lerp(hipL[1], standHip[1], dis) - bump(dis) * 46] : [lerp(standHip[0], hipL[0], mount), lerp(standHip[1], hipL[1], mount) - bump(mount) * 46];
  const nx = track(tc, [[2.0, DOOR_X], [3.6, 830]]);
  const hand = pearlPos(SX, GY + 4, KID_S, true, 'side');
  const bundleP = ramp(tc, 3.6, 4.8);
  const bx = lerp(nx + 14, hand.x, bundleP), by = lerp(GY - 128, hand.y + 20, bundleP) - bump(bundleP) * 36;
  const bundleO = ramp(tc, 1.8, 2.3) * (1 - ramp(tc, 5.0, 5.4));
  const cam = useCam([{t: T_C, ...atg(1200, 1.12)}, {t: T_C + 4.5, ...atg(1000, 1.2)}, {t: T_D + 1, ...atg(1500, 1.14)}]);
  const heroPt = standing ? standHip : (tc < 5.75 ? hipLeft : hipR);
  const pearlPt = standing ? [hand.x, hand.y] : tc < 5.75 ? [hipLeft[0] - 51.5 * KID_S, hipLeft[1] - 60 * KID_S] : [hipR[0] + 51.5 * KID_S, hipR[1] - 60 * KID_S];
  const pp = project(cam, 1, pearlPt[0], pearlPt[1], 2900, 1080);
  const pools: Pool[] = [{x: pp.x, y: pp.y, r: 330 * pp.zoom, k: 'pearl'}];
  const face = tc < 5.9 ? 1 : -1;                                  // 朝左 = 袋子在右边（火种的光透出来）
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.35}><Bg name="village_far" /></Layer>
      <Layer p={0.65}><Bg name="village_mid" /></Layer>
      <Layer p={1}>
        <Bg name="village_near" />
        <GroundShadow x={nx} y={GY + 2} rx={100} o={0.45} />
        <Nainai x={nx} y={GY} t0={0.4} />
        <Horse x={horseX} y={GY + 4} flip moving={tc < 1.6} opacity={1 - turn} />
        {turn > 0 && <Horse x={horseX} y={GY + 4} moving={tc > 6.1} opacity={turn} />}
        {standing ? (
          <>
            <GroundShadow x={SX} y={GY + 6} rx={90} o={0.45} />
            <Pair x={SX} y={GY + 4} flip />
            <Pearl x={hand.x} y={hand.y} />
          </>
        ) : (
          <>
            <Rider hx={hipLeft[0]} hy={tc < 5.4 ? hipLeft[1] : hipLeft[1]} legRot={tc < 2.5 ? lerp(-9, 0, dis) : lerp(0, -9, mount)} flip opacity={1 - turn} />
            {turn > 0 && <Rider hx={hipR[0]} hy={hipR[1]} legRot={-9} opacity={turn} />}
          </>
        )}
        <FireGlow x={heroPt[0] + face * 24 * KID_S} y={heroPt[1] - 66 * KID_S} r={64} o={0.55} />
        <Sprite name="bundle_red" x={bx} y={by} s={0.4} opacity={bundleO} rot={bump(bundleP) * -10} breathe={0} sway={0} v="lit" alwaysShow />
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

// ───────── 镜头 D：天上的灯座。五样齐、灯芯接；“点火！”灯亮了——像碗，像盆，像车轮，最后亮得人睁不开眼
const ShotD: React.FC = () => {
  const t = useT();
  const kx = track(t, [[T_D + 0.2, 300], [T_D + 2.0, 760]]);
  const walking = t > T_D + 0.2 && t < T_D + 2.0;
  const cam = useCam([{t: T_D, ...atg(1080, 1.05)}, {t: T_E, ...atg(1160, 1.08)}]);
  const hand = pearlPos(kx, GY + 4, KID_S, false, 'side');
  // 五样依次飞进灯里：宝珠、雪铃、金鼓、火种；银针接好断心
  const fl = (a: number, d = 1.1) => ramp(t, a, a + d);
  const item = (from: number[], to: number[], u: number, arc: number) => [lerp(from[0], to[0], u), lerp(from[1], to[1], u) - bump(u) * arc];
  const pearlU = fl(30.9), bellU = fl(31.3), drumU = fl(31.7), fireU = fl(32.1), needleU = fl(32.8, 1.2);
  const [pearlX, pearlY] = item([hand.x, hand.y], [LAMP.x - 70, LAMP.dishY - 6], pearlU, 130);
  const [bellX, bellY] = item([hand.x + 6, hand.y + 30], [LAMP.x - 150, LAMP.dishY + 6], bellU, 150);
  const [drumX, drumY] = item([hand.x + 4, hand.y + 40], [LAMP.x + 120, LAMP.dishY + 10], drumU, 140);
  const [fireX, fireY0] = item([hand.x + 4, hand.y + 50], [LAMP.x + 10, LAMP.dishY + 8], fireU, 170);
  const [needleX, needleY] = item([hand.x + 10, hand.y + 20], [LAMP.x, LAMP.dishY - 26], needleU, 120);
  const wickO = ramp(t, 34.0, 34.7);
  const spark = bump(clamp01((t - 34.0) / 1.0));
  const ignite = ramp(t, 35.6, 36.3);                          // 火种跳进灯芯
  const fireNow = t < 35.6 ? [fireX, fireY0] : [lerp(LAMP.x + 10, LAMP.x + 2, ignite), lerp(LAMP.dishY + 8, LAMP.dishY - 150 * 0.7 - 6, ignite)];
  const k = ramp(t, 36.0, 42.8);
  const handDone = pearlU >= 1;
  const lp = project(cam, 1, LAMP.x, LAMP.dishY - 40, 2900, 1080);
  const rad = lerp(40, 3400, Math.pow(ramp(t, 36.2, 42.4), 1.1));
  const hp = project(cam, 1, hand.x, hand.y, 2900, 1080);
  const pools: Pool[] = [{x: hp.x, y: hp.y, r: 330 * hp.zoom, k: 'pearl', o: handDone ? 0.0 : 1}, {x: lp.x, y: lp.y, r: rad * lp.zoom, k: 'none'}];
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="lamp_sky_far" /></Layer>
      <Layer p={1}>
        <Bg name="lamp_sky_near" />
        <GroundShadow x={1100} y={GY + 4} rx={150} o={0.4} />
        <Sprite name="god" x={1100} y={GY + 4} s={0.85} breathe={0.008} sway={0.6} />
        <GroundShadow x={kx} y={GY + 6} rx={90} o={0.45} />
        <Pair x={kx} y={GY + 4} walk={walking ? 6 : 0} />
        {!handDone && <Pearl x={pearlU > 0 ? pearlX : hand.x} y={pearlU > 0 ? pearlY : hand.y} />}
        {handDone && <Pearl x={pearlX} y={pearlY} o={1} />}
        {bellU > 0 && <Sprite name="bell" x={bellX} y={bellY + 6} s={lerp(0.16, 0.3, bellU)} breathe={0} sway={0} v="lit" alwaysShow />}
        {drumU > 0 && <Sprite name="drum" x={drumX} y={drumY + 6} s={lerp(0.16, 0.3, drumU)} breathe={0} sway={0} v="lit" alwaysShow />}
        {wickO > 0 && <Sprite name="wick_fixed" x={LAMP.x} y={LAMP.dishY + 2} s={0.72} opacity={wickO} breathe={0} sway={0.5} v="lit" alwaysShow />}
        {needleU > 0 && needleU < 1 && <Sprite name="needle" x={needleX} y={needleY} s={0.16} rot={lerp(-40, -90, needleU)} breathe={0} sway={0} v="lit" alwaysShow />}
        {fireU > 0 && t < 36.4 && <Sprite name="fire" x={fireNow[0]} y={fireNow[1] + 20} s={0.18} breathe={0} sway={1.5} v="lit" alwaysShow />}
        {fireU > 0 && t < 36.4 && <FireGlow x={fireNow[0]} y={fireNow[1]} r={90} o={0.8} />}
      </Layer>
    </Stage>
  );
  return (
    <>
      <Lit world={world} pools={pools} />
      {spark > 0.01 && (
        <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', mixBlendMode: 'screen'}}>
          <g transform={`translate(${lp.x} ${lp.y - 10}) scale(${(0.6 + spark) * lp.zoom})`} opacity={spark}>
            <path d="M0 -34 L5 -5 L34 0 L5 5 L0 34 L-5 5 L-34 0 L-5 -5 Z" fill="#fbf6e4" />
          </g>
        </svg>
      )}
      <div style={{position: 'absolute', inset: 0, background: 'rgb(239,232,216)', mixBlendMode: 'screen', opacity: 0.3 * ramp(k, 0.55, 1.0), pointerEvents: 'none'}} />
      <LampLight x={lp.x} y={lp.y - 20} k={k} t={t} w={1920} h={1080} />
    </>
  );
};

// ───────── 镜头 E：晨光村口。光从上往下泼；霜化成露珠；鸟、孩子们；奶奶立在人群里，泪顺脸往下落
const FOLK: {n: string; x: number; s: number; flip?: boolean; at: number; t0: number}[] = [
  {n: 'villager1', x: 880, s: 0.88, at: 2.2, t0: 0.2}, {n: 'villager3', x: 1010, s: 0.95, at: 2.5, t0: 1.0}, {n: 'villager2', x: 1330, s: 0.85, flip: true, at: 2.8, t0: 0.6},
  {n: 'villager4', x: 1640, s: 0.9, flip: true, at: 3.0, t0: 1.6}, {n: 'kid3', x: 1440, s: 0.84, at: 3.4, t0: 0.4}, {n: 'kid2', x: 1530, s: 0.84, at: 3.6, t0: 0.9}, {n: 'girl_flower', x: 1760, s: 0.84, at: 4.0, t0: 0.0},
];
const ShotE: React.FC = () => {
  const t = useT();
  const te = t - T_E;
  const p = lerp(-15, 150, ramp(te, 0.2, 4.6));
  const grad = `linear-gradient(to bottom, #000 ${p - 30}%, transparent ${p}%)`;
  const cam = useCam([{t: T_E, ...atg(1300, 1.02)}, {t: 54, ...atg(1250, 1.12)}]);
  const kidRun = track(te, [[2.0, 730], [5.2, 1250]]);
  const kidO = ramp(te, 2.0, 2.6);
  const grandmaO = ramp(te, 2.0, 3.0);
  const tear = ramp(t, C[6].t + 0.6, C[6].t + 1.6) * (1 - ramp(t, C[6].t + 3.6, C[6].t + 4.4));
  const tearY = lerp(0, 44, ((t - C[6].t - 0.6) % 2.2) / 2.2);
  const nx = 1175, ns = KID_S * 1.03;
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.35}><Bg name="village_far" /></Layer>
      <Layer p={0.65}><Bg name="village_mid" /></Layer>
      <Layer p={1}>
        <Bg name="village_near" />
        {FOLK.map((f) => {
          const o = ramp(te, f.at, f.at + 0.8);
          const sw = f.n === 'girl_flower' ? Math.sin(t * 3) * 5 : 0;
          return o > 0.01 ? (
            <React.Fragment key={f.n}>
              <GroundShadow x={f.x} y={GY + 4} rx={70} o={0.4 * o} />
              <Sprite name={f.n} x={f.x} y={GY + 4} s={f.s} flip={f.flip} opacity={o} rot={sw} breathe={0.008} sway={0.6} t0={f.t0} />
            </React.Fragment>
          ) : null;
        })}
        {kidO > 0.01 && (
          <>
            <GroundShadow x={kidRun} y={GY + 4} rx={60} o={0.4 * kidO} />
            <Sprite name="kid1" x={kidRun} y={GY + 4 - Math.abs(Math.sin(t * 7)) * 8} s={0.84} opacity={kidO} breathe={0} sway={1} />
          </>
        )}
        <GroundShadow x={nx} y={GY + 4} rx={90} o={0.45 * grandmaO} />
        <Nainai x={nx} y={GY + 4} opacity={grandmaO} t0={0.4} />
        {tear > 0.01 && (
          <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
            <path transform={`translate(${nx + 13} ${GY + 4 - 316 * ns + tearY})`} d="M0 0 C3 7 6 11 0 17 C-6 11 -3 7 0 0 Z" fill="#dfe9ee" opacity={0.85 * tear} stroke="#8fa6b4" strokeWidth={0.8} />
          </svg>
        )}
      </Layer>
    </Stage>
  );
  // 露珠：霜化了，一颗颗往下掉
  const dew = Array.from({length: 36}, (_, i) => {
    const sd = (i * 7919) % 97 / 97, sd2 = (i * 104729) % 89 / 89;
    const x = 120 + sd * 1680, ph = (i * 0.37) % 1;
    const q = ((te * 0.5 + ph) % 1);
    return {x, y: 380 + sd2 * 380 + q * 90, o: Math.sin(q * Math.PI) * 0.8, r: 1.6 + (i % 3) * 0.8};
  });
  // 鸟：飞过来唱歌
  const birds = [0, 1, 2].map((i) => {
    const u = clamp01((te - 3.0 - i * 0.7) / 5.5);
    return {x: -80 + u * 2060, y: 250 + i * 60 + Math.sin(te * 1.5 + i) * 16, up: Math.floor((te + i * 0.1) / 0.22) % 2 === 0, sw: i === 2};
  });
  return (
    <>
      <VariantCtx.Provider value="night">{world('night')}</VariantCtx.Provider>
      <div style={{position: 'absolute', inset: 0, WebkitMaskImage: grad, maskImage: grad}}><VariantCtx.Provider value="dawn">{world('dawn')}</VariantCtx.Provider></div>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
        {ramp(te, 2.6, 3.6) > 0 && dew.map((d, i) => <circle key={i} cx={d.x} cy={d.y} r={d.r} fill="#f4f1e6" opacity={d.o * ramp(te, 2.6, 3.6) * 0.8} />)}
      </svg>
      <div style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
        {birds.map((b, i) => (b.x > -60 && b.x < 1980 ? (
          <div key={i} style={{position: 'absolute', left: b.x, top: b.y, width: 0, height: 0}}>
            <Sprite name={b.sw ? (b.up ? 'swallow_up' : 'swallow_down') : (b.up ? 'bird_up' : 'bird_down')} x={0} y={0} s={0.9} breathe={0} sway={0} v="dawn" alwaysShow />
          </div>
        ) : null))}
      </div>
    </>
  );
};

export const S6: React.FC<{len: number}> = ({len}) => {
  const shots = [
    {from: 0, el: <ShotA />},
    {from: T_B, map: 'b' as const, el: <ShotB />},
    {from: T_C, map: 'a' as const, el: <ShotC />},
    {from: T_D, map: 'c' as const, el: <ShotD />},
    {from: T_E, map: 'd' as const, el: <ShotE />, wipe: 2.4},
  ];
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night"><ShotStack shots={shots} /></VariantCtx.Provider>
    </SceneWrap>
  );
};
