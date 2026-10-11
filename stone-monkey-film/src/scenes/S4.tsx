import React, {useContext} from 'react';
import {Stage, Layer, useCam, project} from '../fx/Stage';
import {GroundShadow, Sprite} from '../fx/Sprite';
import {Lit, Pool, PaperGlow} from '../fx/Light';
import {ShotStack} from '../fx/ShotStack';
import {Snow} from '../fx/Snow';
import {VariantCtx, Variant, CharsCtx} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, track, at, atg, lerp, cuesOf} from './kit';
import {Shiwa, Houzi, Pair, Pearl, pearlPos, KID_S, KP, off} from './cast';

// 第四部 西山的雪铃：帮崖下的老婆婆捆柴 → 霜林 → 雪山上的小屋和老梅 → 铜铃开口问话 → 扫屋、铲雪，红裙小姑娘端来热汤 → 取到雪铃
const C = cuesOf('s4-snow');
const GY = 832;
const PEARL_R = 330;            // 宝珠只照三尺：光池的半径
const T_B = 7.3, T_C = 14.6, T_D = 20.6, T_E = 34.0;

/** 宝珠的光池（屏幕坐标）跟着石娃走：footX/footY 是石娃脚底的世界坐标 */
const usePool = (cam: ReturnType<typeof useCam>, footX: number, footY: number, w: number, h: number, flip = false, r = PEARL_R, o = 1): {pools: Pool[]; pw: {x: number; y: number}} => {
  const pw = pearlPos(footX, footY, KID_S, flip, 'side');
  const p = project(cam, 1, pw.x, pw.y, w, h);
  return {pools: [{x: p.x, y: p.y, r: r * p.zoom, k: 'pearl', o}], pw};
};

const Walker: React.FC<{x: number; y: number; flip?: boolean; walk?: number; kid?: number; pearl?: boolean; houzi?: boolean}> = ({x, y, flip = false, walk = 0, pearl = true, houzi = true}) => {
  const pw = pearlPos(x, y, KID_S, flip, 'side');
  return (
    <>
      <GroundShadow x={x} y={y + 2} rx={90} o={0.45} />
      <Pair x={x} y={y} flip={flip} walk={walk} houzi={houzi} />
      {pearl && <Pearl x={pw.x} y={pw.y} />}
    </>
  );
};

// ───────── 镜头 A：山边小路，老婆婆捆柴
const ShotA: React.FC = () => {
  const t = useT();
  const kx = track(t, [[0.4, 360], [4.2, 1260]]);
  const walking = t > 0.4 && t < 4.2;
  const cam = useCam([{t: 0, ...atg(620, 1.12)}, {t: 5, ...atg(1250, 1.2)}, {t: T_B + 1.5, ...atg(1330, 1.24)}]);
  const tied = ramp(t, 4.6, 5.6);       // 绳头绕两转，一拉便稳了
  const crouch = ramp(t, 4.0, 4.6) * (1 - ramp(t, 6.2, 6.8));
  const {pools} = usePool(cam, kx, GY + 4, 2900, 1080);
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="hill_far" /></Layer>
      <Layer p={0.62}><Bg name="hill_mid" /></Layer>
      <Layer p={1}>
        <Bg name="hill_near" />
        <GroundShadow x={1560} y={GY + 4} rx={120} o={0.45} />
        <Sprite name="oldwoman_sit_side" x={1600} y={GY + 4} s={0.84} breathe={0.01} sway={0.4} />
        <Sprite name="firewood" x={1440} y={GY + 6} s={0.8} opacity={1 - tied} breathe={0} sway={0} />
        <Sprite name="firewood_tied" x={1440} y={GY + 6} s={0.8} opacity={tied} breathe={0} sway={0} />
        <Walker x={kx} y={GY + 4} walk={walking ? 6 : 0} />
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

// ───────── 镜头 B：霜林
const ShotB: React.FC = () => {
  const t = useT();
  const kx = track(t, [[T_B + 0.5, 360], [T_C + 0.5, 2050]]);
  const cam = useCam([{t: T_B, ...atg(700, 1.15)}, {t: T_C + 1, ...atg(1900, 1.15)}]);
  const {pools} = usePool(cam, kx, GY + 4, 2900, 1080);
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="frost_forest_far" /></Layer>
      <Layer p={0.62}><Bg name="frost_forest_mid" /></Layer>
      <Layer p={1}>
        <Bg name="frost_forest_near" />
        <Walker x={kx} y={GY + 4} walk={6} />
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

export const S4: React.FC<{len: number}> = ({len}) => {
  const shots = [
    {from: 0, el: <ShotA />},
    {from: T_B, map: 'a' as const, el: <ShotB />},
  ];
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night"><ShotStack shots={shots} /></VariantCtx.Provider>
      <Snow amount={0.35} wind={0.06} speed={0.5} />
    </SceneWrap>
  );
};
