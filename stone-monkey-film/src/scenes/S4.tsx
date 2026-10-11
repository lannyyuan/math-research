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

// ───────── 镜头 C：雪山小屋、老梅（宝珠的光照到时，才看见那朵小白花）
const ShotC: React.FC = () => {
  const t = useT();
  const kx = track(t, [[T_C + 0.4, 520], [T_C + 6.0, 1640]]);
  const cam = useCam([{t: T_C, ...atg(900, 1.12)}, {t: T_C + 6.5, ...atg(1500, 1.1)}, {t: T_D + 1.5, ...atg(1650, 1.12)}]);
  const {pools} = usePool(cam, kx, GY + 4, 2900, 1080);
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="snow_hut_far" /></Layer>
      <Layer p={0.62}><Bg name="snow_hut_mid" /></Layer>
      <Layer p={1}>
        <Bg name="snow_hut_near" />
        <Walker x={kx} y={GY + 4} walk={t < T_C + 6.0 ? 6 : 0} />
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

// ───────── 镜头 D：小屋里，铜铃开口问话；扫屋、擦鼓、刷桌
const BELL = {x: 1200, y: 692, s: 0.5};
const ShotD: React.FC = () => {
  const t = useT();
  const tt = t - T_D;
  const kx = track(tt, [[0.3, 480], [3.0, 900], [10.2, 900], [12.4, 1000]]);
  const walking = tt > 0.3 && tt < 3.0;
  const cam = useCam([{t: T_D, ...atg(900, 1.14)}, {t: T_E, ...atg(1050, 1.2)}]);
  const ring1 = ramp(t, C[3].t - 0.6, C[3].t + 2.6), ring2 = ramp(t, C[3].t + 1.6, C[3].t + 4.4);
  const shake = (t > C[3].t - 0.5 && t < C[3].t + 1.2) ? Math.sin(t * 38) * 2.2 : 0;
  const clean = ramp(t, C[4].t + 4.0, C[4].t + 6.4);
  const take = ramp(t, C[4].t + 6.2, C[4].t + 7.4);          // 铃儿跳进他的手心
  const hand = pearlPos(kx, GY + 4, KID_S, false, 'side');
  const bx = lerp(BELL.x, hand.x + 8, take), by = lerp(BELL.y, hand.y + 40, take) - Math.sin(take * Math.PI) * 90, bs = lerp(BELL.s, 0.2, take);
  const {pools} = usePool(cam, kx, GY + 4, 2400, 1080, false, lerp(330, 560, ramp(t, C[3].t, C[3].t + 3)));
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.5} w={2400}><Bg name="hut_in_far" /></Layer>
      <Layer p={1} w={2400}>
        <Bg name="hut_in_near" />
        <Bg name="hut_in_clean" opacity={clean} />
        <Sprite name="bell" x={bx + shake} y={by} s={bs} rot={shake * 0.8} breathe={0} sway={0} />
        <Walker x={kx} y={GY + 4} walk={walking ? 6 : 0} />
      </Layer>
    </Stage>
  );
  return (
    <>
      <Lit world={world} pools={pools} />
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
        {[ring1, ring2].map((q, i) => {
          if (q <= 0 || q >= 1) return null;
          const p = project(cam, 1, BELL.x, BELL.y - 70, 2400, 1080);
          return [0, 1, 2].map((j) => {
            const qq = Math.max(0, Math.min(1, q * 1.2 - j * 0.15));
            if (qq <= 0 || qq >= 1) return null;
            return <circle key={`${i}${j}`} cx={p.x} cy={p.y} r={(40 + qq * 240) * p.zoom} fill="none" stroke="#efe8d8" strokeWidth={3 * (1 - qq) + 0.6} opacity={0.7 * (1 - qq)} />;
          });
        })}
      </svg>
    </>
  );
};

// ───────── 镜头 E：门前的雪铲开了，红裙小姑娘端着热汤跑来
const ShotE: React.FC = () => {
  const t = useT();
  const te = t - T_E;
  const kx = 1640;
  const gx = track(te, [[0.4, 2650], [3.6, 2060]]);
  const cam = useCam([{t: T_E, ...atg(1700, 1.12)}, {t: len1, ...atg(1850, 1.2)}]);
  const {pools} = usePool(cam, kx, GY + 4, 2900, 1080, false, 360);
  const gp = project(cam, 1, gx, GY - 140, 2900, 1080);
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="snow_hut_far" /></Layer>
      <Layer p={0.62}><Bg name="snow_hut_mid" /></Layer>
      <Layer p={1}>
        <Bg name="snow_hut_near_clear" />
        <GroundShadow x={gx} y={GY + 4} rx={60} o={0.45} />
        <Sprite name="girl_side" x={gx} y={GY + 4} s={0.84} flip walk={te > 0.4 && te < 3.6 ? 5 : 0} />
        <Walker x={kx} y={GY + 4} />
        <Sprite name="bell" x={kx - 20} y={GY - 120} s={0.16} breathe={0} sway={2} />
      </Layer>
    </Stage>
  );
  // 小姑娘的红裙：她走进光里才有颜色，所以她身上也带一小团光
  const extra: Pool[] = [{x: gp.x, y: gp.y, r: 190 * gp.zoom, k: 'pearl', o: 0.55 * ramp(te, 1.2, 3.0)}];
  return <Lit world={world} pools={[...pools, ...extra]} />;
};

let len1 = 41;

export const S4: React.FC<{len: number}> = ({len}) => {
  len1 = len;
  const shots = [
    {from: 0, el: <ShotA />},
    {from: T_B, map: 'a' as const, el: <ShotB />},
    {from: T_C, map: 'c' as const, el: <ShotC />},
    {from: T_D, map: 'b' as const, el: <ShotD />},
    {from: T_E, map: 'd' as const, el: <ShotE />},
  ];
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night"><ShotStack shots={shots} /></VariantCtx.Provider>
      <Snow amount={0.35} wind={0.06} speed={0.5} />
    </SceneWrap>
  );
};
