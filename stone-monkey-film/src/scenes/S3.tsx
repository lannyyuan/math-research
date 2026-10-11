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

export const S3: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const shots = [
    {from: 0, el: <ShotA />},
    {from: T_B, map: 'd' as const, el: <ShotB />},
  ];
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night"><ShotStack shots={shots} /></VariantCtx.Provider>
    </SceneWrap>
  );
};
