import React, {useContext} from 'react';
import {Stage, Layer, useCam, project} from '../fx/Stage';
import {GroundShadow, Sprite} from '../fx/Sprite';
import {Lit, Pool} from '../fx/Light';
import {ShotStack} from '../fx/ShotStack';
import {Ripple, Bubbles} from '../fx/Water';
import {VariantCtx, Variant, CharsCtx} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, track, at, atg, lerp, cuesOf} from './kit';
import {Shiwa, Houzi, Pair, Pearl, pearlPos, KID_S, KP, off} from './cast';

// 第三部 海底的珍珠：鳞片贴在胸口，海水让出一条路 → 贝壳和珊瑚搭成的宫殿 → 老龙 → 青石压着泉眼，石娃用木棍把石头撬开 → 清泉涌出，老龙吐出宝珠
const C = cuesOf('s3-sea');
const GY = 832;
const T_B = 10.8, T_C = 17.0, T_D = 22.3, T_E = 29.0;

// ───────────── 镜头 A：海边。鳞片贴在胸口，海水分开，露出一条路
const ShotA: React.FC = () => {
  const t = useT();
  const cam = useCam([{t: 0, ...atg(1250, 1.0)}, {t: 7, ...atg(1500, 1.05)}, {t: 12, ...atg(2000, 1.05)}]);
  const x = t < 5.8 ? 1180 : track(t, [[5.8, 1180], [8.0, 1520], [12.0, 2150]]);
  const walking = t > 5.8;
  const scaleStick = ramp(t, 3.4, 5.2);           // 鳞片从手里贴到胸口
  const sc = off('shiwa_side', KP.shiwa_side.hand, KID_S, false);
  const ch = off('shiwa_side', [88, 170], KID_S, false);
  const sx = lerp(x + sc.dx + 10, x + ch.dx, scaleStick), sy = lerp(GY + sc.dy - 30, GY + ch.dy, scaleStick);
  const glow = ramp(t, 4.6, 6.0) * (1 - ramp(t, 9.0, 11.0) * 0.6);
  const cover = 1 - ramp(t, 6.2, 9.6);             // 盖住干路的海水慢慢分开
  return (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="shore_far" /></Layer>
      <Layer p={0.62}><Bg name="shore_mid" /></Layer>
      <Layer p={1}>
        <Bg name="shore_near" />
        <Bg name="shore_water_cover" opacity={cover} />
        <GroundShadow x={x} y={GY + 4} rx={90} o={0.5} />
        <Pair x={x} y={GY + 4} walk={walking ? 6 : 0} />
        <Sprite name="scale" x={sx} y={sy} s={0.36} rot={-20 * (1 - scaleStick)} opacity={ramp(t, 2.2, 3.0)} breathe={0.02} sway={0} v="lit" alwaysShow />
        <div style={{position: 'absolute', left: x + ch.dx - 70, top: GY + ch.dy - 70, width: 140, height: 140, borderRadius: '50%', mixBlendMode: 'screen', opacity: 0.55 * glow, background: 'radial-gradient(circle, rgba(215,232,245,0.95) 0%, rgba(170,200,230,0.35) 40%, rgba(170,200,230,0) 70%)'}} />
      </Layer>
    </Stage>
  );
};

// ───────────── 镜头 B：海底，朝宫殿走
const ShotB: React.FC = () => {
  const t = useT() - T_B;
  const cam = useCam([{t: T_B, ...atg(900, 1.0)}, {t: T_C + 1, ...atg(1500, 1.06)}]);
  const x = track(t, [[0.4, 520], [6.4, 1560]]);
  return (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="palace_far" /></Layer>
      <Layer p={0.62}><Bg name="palace_mid" /></Layer>
      <Layer p={1}>
        <Bg name="palace_near" />
        <GroundShadow x={x} y={GY + 4} rx={90} o={0.45} />
        <Pair x={x} y={GY + 4} walk={6} />
        <Bubbles x={x} y={GY - 200} t={t} n={10} spread={90} rise={260} seed={2} o={0.8} />
      </Layer>
    </Stage>
  );
};

// ───────────── 镜头 C：宫里很亮，老龙
const DRAGON = {x: 1500, s: 1.25};
const ShotC: React.FC = () => {
  const t = useT();
  const cam = useCam([{t: T_C, ...atg(1100, 1.08)}, {t: T_D + 1.5, ...atg(1300, 1.2)}]);
  const dragonO = ramp(t, T_C + 0.8, T_C + 3.0);
  const kx = track(t, [[T_C + 0.3, 500], [T_C + 3.6, 930]]);
  return (
    <Stage cam={cam}>
      <Layer p={0.4} w={2400}><Bg name="hall_sea_far" /></Layer>
      <Layer p={1} w={2400}>
        <Bg name="hall_sea_near" />
        <GroundShadow x={DRAGON.x} y={GY + 6} rx={230} o={0.4 * dragonO} />
        <Sprite name="dragon_front" x={DRAGON.x} y={GY + 12} s={DRAGON.s} opacity={dragonO} breathe={0.01} sway={0.9} />
        <GroundShadow x={kx} y={GY + 4} rx={90} o={0.45} />
        <Pair x={kx} y={GY + 4} walk={t < T_C + 3.6 ? 6 : 0} />
      </Layer>
    </Stage>
  );
};

// ───────────── 镜头 D：压着泉眼的青石，木棍撬石
const BOULDER = {x: 1500, s: 1.0};
const ShotD: React.FC = () => {
  const t = useT();
  const tt = t - T_D;
  const cam = useCam([{t: T_D, ...atg(1200, 1.1)}, {t: T_E - 1, ...atg(1500, 1.15)}]);
  const kx = track(tt, [[0.2, 650], [2.2, 1080]]);
  const walking = tt > 0.2 && tt < 2.2;
  const shake = tt > 2.6 && tt < 4.0 ? Math.sin(tt * 40) * 1.0 : 0;
  const leverIn = ramp(tt, 4.4, 5.0);
  const press = ramp(tt, 5.6, 6.4);                        // 压下去：青石撬起
  const roll = ramp(tt, 6.4, 7.4);                         // 滚到一旁
  const bRot = lerp(0, -14, press) + roll * 70;
  const bX = BOULDER.x + roll * 520;
  const spring = ramp(tt, 6.6, 8.4);
  return (
    <Stage cam={cam}>
      <Layer p={0.4}><Bg name="spring_far" /></Layer>
      <Layer p={1}>
        <Bg name="spring_near" />
        <Bg name="spring_clear" opacity={spring} />
        <Sprite name="boulder" x={bX + shake} y={GY + 6 - roll * 0} s={BOULDER.s} rot={bRot} pivot={[(1 - roll) * 260, 0]} breathe={0} sway={0} />
        <Sprite name="flat_stone" x={1300} y={GY + 6} s={0.7} opacity={leverIn} breathe={0} sway={0} />
        <Sprite name="lever" x={1290} y={GY - 6} s={0.62} rot={lerp(-48, -68, press)} opacity={leverIn} breathe={0} sway={0} />
        <GroundShadow x={kx} y={GY + 4} rx={90} o={0.45} />
        <Pair x={kx} y={GY + 4 + press * 8} walk={walking ? 6 : 0} rot={press * 8} />
        <Bubbles x={1520} y={GY} t={tt} n={22} spread={260} rise={300} o={spring} seed={9} />
        <Ripple x={1520} y={GY + 6} r={300} p={ramp(tt, 6.8, 10)} n={3} />
      </Layer>
    </Stage>
  );
};

// ───────────── 镜头 E：老龙吐出宝珠，整座宫都亮——然后“这珠只照三尺”
const ShotE: React.FC = () => {
  const t = useT();
  const te = t - T_E;
  const cam = useCam([{t: T_E, ...atg(1150, 1.12)}, {t: len0 - 1, ...atg(1100, 1.2)}]);
  const kx = te < 8.5 ? 1000 : track(te, [[8.5, 1000], [11.5, 640]]);
  const flipK = te > 8.5;
  const bow = ramp(te, 6.6, 7.4) * (1 - ramp(te, 7.8, 8.4));
  // 珠子：从龙口飞到石娃手里
  const fly = ramp(te, 2.0, 3.8);
  const mouth = {x: DRAGON.x - 10, y: GY - 330};
  const hand = pearlPos(kx, GY + 4, KID_S, false, 'side');
  const px = lerp(mouth.x, hand.x, fly), py = lerp(mouth.y, hand.y, fly) - Math.sin(fly * Math.PI) * 120;
  const pearlO = ramp(te, 1.8, 2.2);
  const pp = project(cam, 1, px, py, 2400, 1080);
  // 光池：先“整座宫都亮”，再收成“只照三尺”
  const big = ramp(te, 2.6, 5.0);
  const small = ramp(te, 6.0, 9.0);
  const r = lerp(120, 1700, big) * (1 - small) + 330 * small + 120 * (1 - big) * 0;
  const pools: Pool[] = pearlO > 0.02 ? [{x: pp.x, y: pp.y, r: Math.max(r, 60) * pp.zoom, k: 'pearl', o: pearlO}] : [];
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.4} w={2400}><Bg name="hall_sea_far" /></Layer>
      <Layer p={1} w={2400}>
        <Bg name="hall_sea_near" />
        <GroundShadow x={DRAGON.x} y={GY + 6} rx={230} o={0.4} />
        <Sprite name="dragon_front" x={DRAGON.x} y={GY + 12} s={DRAGON.s} breathe={0.01} sway={0.9} />
        <GroundShadow x={kx} y={GY + 4} rx={90} o={0.45} />
        <Pair x={kx} y={GY + 4} flip={flipK} rot={bow * 10} walk={te > 8.5 && te < 11.5 ? 6 : 0} />
        {pearlO > 0.02 && <Pearl x={px} y={py} o={pearlO} />}
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

let len0 = 44;

export const S3: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  len0 = len;
  const shots = [
    {from: 0, el: <ShotA />},
    {from: T_B, map: 'd' as const, el: <ShotB />},
    {from: T_C, map: 'b' as const, el: <ShotC />},
    {from: T_D, map: 'a' as const, el: <ShotD />},
    {from: T_E, map: 'c' as const, el: <ShotE />},
  ];
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night"><ShotStack shots={shots} /></VariantCtx.Provider>
    </SceneWrap>
  );
};
