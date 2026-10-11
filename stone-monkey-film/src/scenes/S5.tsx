import React, {useContext} from 'react';
import {Stage, Layer, useCam, project} from '../fx/Stage';
import {GroundShadow, Sprite} from '../fx/Sprite';
import {Lit, Pool, PaperGlow, FireGlow} from '../fx/Light';
import {ShotStack} from '../fx/ShotStack';
import {Snow} from '../fx/Snow';
import {VariantCtx, Variant, CharsCtx} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, track, at, atg, lerp, cuesOf} from './kit';
import {Shiwa, Houzi, Pair, Pearl, pearlPos, Campfire, KID_S, KP, off} from './cast';

// 第五部 北边的金鼓：草原上的牧人和篝火，牧人送马 → 主城的城门和卫士，宝珠的光照在城墙上，人群围过来 → 殿上国王 → 爬九层塔，“咚——”
const C = cuesOf('s5-drum');
const GY = 832;
const T_B = 7.4, T_C = 21.4, T_D = 29.6, T_E = 36.0;
const GUARD_S = 0.7, OFFICIAL_S = 0.8, HERDER_S = 0.78;

const usePool = (cam: ReturnType<typeof useCam>, footX: number, footY: number, w: number, h: number, flip = false, r = 330, o = 1): Pool[] => {
  const pw = pearlPos(footX, footY, KID_S, flip, 'side');
  const p = project(cam, 1, pw.x, pw.y, w, h);
  return [{x: p.x, y: p.y, r: r * p.zoom, k: 'pearl', o}];
};
const Hero: React.FC<{x: number; y: number; flip?: boolean; walk?: number; pearl?: boolean}> = ({x, y, flip = false, walk = 0, pearl = true}) => {
  const pw = pearlPos(x, y, KID_S, flip, 'side');
  return (
    <>
      <GroundShadow x={x} y={y + 2} rx={90} o={0.45} />
      <Pair x={x} y={y} flip={flip} walk={walk} />
      {pearl && <Pearl x={pw.x} y={pw.y} />}
    </>
  );
};

// ───────── 镜头 B：主城的城门。卫士拦路，宝珠的光照在城墙上，人群围过来
const ShotB: React.FC = () => {
  const t = useT();
  const kx = track(t, [[T_B + 0.6, 380], [T_B + 4.2, 1010]]);
  const walking = t > T_B + 0.6 && t < T_B + 4.2;
  const cam = useCam([{t: T_B, ...atg(760, 1.12)}, {t: T_B + 5, ...atg(1250, 1.1)}, {t: T_B + 10, ...atg(1500, 1.06)}, {t: T_C + 1.5, ...atg(1650, 1.06)}]);
  // 光池：先只照三尺，然后“光照在墙上”——慢慢扩大
  const r = lerp(330, 780, ramp(t, C[1].t + 0.6, C[1].t + 4.0));
  const pools = usePool(cam, kx, GY + 4, 2900, 1080, false, r);
  const crowd = ramp(t, C[2].t - 2.2, C[2].t + 0.6);
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="gate_far" /></Layer>
      <Layer p={0.62}><Bg name="gate_mid" /></Layer>
      <Layer p={1}>
        <Bg name="gate_near" />
        <GroundShadow x={1290} y={GY + 4} rx={80} o={0.45} />
        <Sprite name="guard_front" x={1290} y={GY + 4} s={GUARD_S} breathe={0.006} sway={0.3} />
        <GroundShadow x={1710} y={GY + 4} rx={80} o={0.45} />
        <Sprite name="guard_front" x={1710} y={GY + 4} s={GUARD_S} flip breathe={0.006} sway={0.3} t0={1.7} />
        <Hero x={kx} y={GY + 4} walk={walking ? 6 : 0} />
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

export const S5: React.FC<{len: number}> = ({len}) => {
  const shots = [{from: 0, el: <ShotB />}];
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night"><ShotStack shots={shots} /></VariantCtx.Provider>
      <Snow amount={0.3} wind={0.06} speed={0.5} />
    </SceneWrap>
  );
};
