import React from 'react';
import {Stage, Layer, useCam, project} from '../fx/Stage';
import {GroundShadow, Sprite} from '../fx/Sprite';
import {Lit, Pool, PaperGlow} from '../fx/Light';
import {ShotStack} from '../fx/ShotStack';
import {Snow} from '../fx/Snow';
import {VariantCtx, Variant} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, track, at, atg, lerp, cuesOf} from './kit';
import {Houzi, Pair, Pearl, pearlPos, Campfire, Rider, KID_S, HORSE_S, SADDLE} from './cast';

// 第五部 北边的金鼓：草原上的牧人和篝火，牧人送马 → 主城的城门和卫士，宝珠的光照在城墙上，人群围过来 → 殿上国王 → 爬九层塔，“咚——”
const C = cuesOf('s5-drum');
const GY = 832;
const T_B = 7.4, T_C = 21.4, T_D = 29.6, T_E = 36.0;
const GUARD_S = 0.7, OFFICIAL_S = 0.8, HERDER_S = 0.78, KING_S = 0.85;
const HIT = C[5].t + 1.9;            // “咚”的那一刻（场景内秒数）

/** 宝珠的光池（屏幕坐标）跟着石娃走：footX/footY 是石娃脚底的世界坐标 */
const usePool = (cam: ReturnType<typeof useCam>, footX: number, footY: number, w: number, h: number, flip = false, r = 330, o = 1, kid = KID_S): Pool[] => {
  const pw = pearlPos(footX, footY, kid, flip, 'side');
  const p = project(cam, 1, pw.x, pw.y, w, h);
  return [{x: p.x, y: p.y, r: r * p.zoom, k: 'pearl', o}];
};
const Hero: React.FC<{x: number; y: number; flip?: boolean; walk?: number; pearl?: boolean; kid?: number}> = ({x, y, flip = false, walk = 0, pearl = true, kid = KID_S}) => {
  const pw = pearlPos(x, y, kid, flip, 'side');
  return (
    <>
      <GroundShadow x={x} y={y + 2} rx={90 * (kid / KID_S)} o={0.45} />
      <Pair x={x} y={y} flip={flip} walk={walk} kid={kid} />
      {pearl && <Pearl x={pw.x} y={pw.y} kid={kid} />}
    </>
  );
};

// ───────── 镜头 A：草原，牧人和篝火。牧人叹气，送他一匹马，扶他上去
const ShotA: React.FC = () => {
  const t = useT();
  const kx = track(t, [[0.5, 300], [3.0, 1030], [3.6, 1030], [5.0, 1560]]);
  const herderX = track(t, [[3.2, 1190], [4.6, 1640]]);
  const mount = ramp(t, 5.0, 5.9);
  const horseX = track(t, [[5.9, 1760], [7.8, 2060]]);
  const moving = t > 5.9;
  const cam = useCam([{t: 0, ...atg(850, 1.1)}, {t: 4.5, ...atg(1350, 1.16)}, {t: T_B + 1.0, ...atg(1760, 1.2)}]);
  const bob = moving ? -Math.abs(Math.sin(t * 5.2)) * 4 : 0;
  // 上马：髋从站着的高度升到鞍子上，腿从垂直摆成朝前的骑姿
  const sx = horseX + SADDLE.dx, sy = GY + 4 + SADDLE.dy;
  const hipX = lerp(kx + 4, sx, mount), hipY = lerp(GY + 4 - 118, sy, mount) - Math.sin(mount * Math.PI) * 46 + bob;
  const mounted = t > 5.0;
  const walking = (t > 0.5 && t < 3.0) || (t > 3.6 && t < 5.0);
  const pearlP = pearlPos(kx, GY + 4, KID_S, false, 'side');
  const pearlX = mounted ? hipX + 51.5 * KID_S : pearlP.x, pearlY = mounted ? hipY - 60 * KID_S : pearlP.y;
  const pp = project(cam, 1, pearlX, pearlY, 2900, 1080);
  const fp = project(cam, 1, 1250, GY - 70, 2900, 1080);
  const pools: Pool[] = [{x: pp.x, y: pp.y, r: 330 * pp.zoom, k: 'pearl'}, {x: fp.x, y: fp.y, r: 300 * fp.zoom, k: 'fire', o: 0.95}];
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}><Bg name="grassland_far" /></Layer>
      <Layer p={0.62}><Bg name="grassland_mid" /></Layer>
      <Layer p={1}>
        <Bg name="grassland_near" />
        <Campfire x={1250} y={GY + 2} s={0.6} t={t} />
        <GroundShadow x={herderX} y={GY + 4} rx={100} o={0.45} />
        <Sprite name="herder_front" x={herderX} y={GY + 4} s={HERDER_S} breathe={0.006} sway={0.3} />
        <GroundShadow x={horseX} y={GY + 6} rx={190} o={0.45} />
        <Sprite name="horse_side" x={horseX} y={GY + 4 + bob} s={HORSE_S} breathe={0.006} sway={0.3} />
        {mounted ? <Rider hx={hipX} hy={hipY} legRot={lerp(0, -9, mount)} /> : <Hero x={kx} y={GY + 4} walk={walking ? 6 : 0} />}
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

// ───────── 镜头 B：主城的城门。卫士拦路，宝珠的光照在城墙上，人群围过来
const CROWD: {n: string; x: number; s: number; flip?: boolean; t0: number}[] = [
  {n: 'villager1', x: 640, s: 0.88, t0: 0.3}, {n: 'villager3', x: 760, s: 0.95, t0: 1.1}, {n: 'kid1', x: 1150, s: 0.84, t0: 0.7},
  {n: 'villager2', x: 1215, s: 0.85, flip: true, t0: 2.0}, {n: 'villager4', x: 1790, s: 0.9, flip: true, t0: 1.4}, {n: 'kid3', x: 1880, s: 0.84, flip: true, t0: 0.2},
];
const ShotB: React.FC = () => {
  const t = useT();
  const kx = track(t, [[T_B + 0.6, 420], [T_B + 4.2, 1010]]);
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
        <GroundShadow x={240} y={GY + 6} rx={180} o={0.4} />
        <Sprite name="horse_side" x={240} y={GY + 4} s={HORSE_S} breathe={0.006} sway={0.3} />
        <GroundShadow x={1290} y={GY + 4} rx={80} o={0.45} />
        <Sprite name="guard_front" x={1290} y={GY + 4} s={GUARD_S} breathe={0.006} sway={0.3} />
        <GroundShadow x={1710} y={GY + 4} rx={80} o={0.45} />
        <Sprite name="guard_front" x={1710} y={GY + 4} s={GUARD_S} flip breathe={0.006} sway={0.3} t0={1.7} />
        {CROWD.map((c, i) => {
          const o = ramp(t, C[2].t - 2.2 + i * 0.28, C[2].t - 1.2 + i * 0.28) * crowd * 1.0;
          const dx = (1 - ramp(t, C[2].t - 2.2 + i * 0.28, C[2].t + 0.6 + i * 0.28)) * (c.x < 1400 ? -60 : 60);     // 从两边慢慢聚过来
          return o > 0.01 ? (
            <React.Fragment key={c.n}>
              <GroundShadow x={c.x + dx} y={GY + 4} rx={70} o={0.4 * o} />
              <Sprite name={c.n} x={c.x + dx} y={GY + 4} s={c.s} flip={c.flip} opacity={o} breathe={0.008} sway={0.5} t0={c.t0} />
            </React.Fragment>
          ) : null;
        })}
        <Hero x={kx} y={GY + 4} walk={walking ? 6 : 0} />
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

// ───────── 镜头 C：殿上。国王坐在宝座上，官员两侧，石娃进殿
const ShotC: React.FC = () => {
  const t = useT();
  const tc = t - T_C;
  const kx = track(tc, [[0.4, 260], [4.4, 960]]);
  const walking = tc > 0.4 && tc < 4.4;
  const cam = useCam([{t: T_C, ...atg(760, 1.06)}, {t: T_C + 4.5, ...atg(1000, 1.14)}, {t: T_D + 1.5, ...atg(1100, 1.16)}]);
  const r = lerp(330, 760, ramp(tc, 1.0, 4.0));           // 进了殿，光照亮了殿上的人
  const pools = usePool(cam, kx, GY + 4, 2400, 1080, false, r);
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.5} w={2400}><Bg name="hall_king_far" /></Layer>
      <Layer p={1} w={2400}>
        <Bg name="hall_king_near" />
        <Sprite name="king_seated" x={1200} y={640} s={KING_S} breathe={0.006} sway={0.2} />
        <GroundShadow x={560} y={GY + 4} rx={80} o={0.45} />
        <Sprite name="official_front" x={560} y={GY + 4} s={OFFICIAL_S} breathe={0.006} sway={0.3} />
        <GroundShadow x={1840} y={GY + 4} rx={80} o={0.45} />
        <Sprite name="official_front" x={1840} y={GY + 4} s={OFFICIAL_S} flip breathe={0.006} sway={0.3} t0={1.3} />
        <Hero x={kx} y={GY + 4} walk={walking ? 6 : 0} />
      </Layer>
    </Stage>
  );
  return <Lit world={world} pools={pools} />;
};

// ───────── 镜头 D：爬九层塔。镜头沿塔身向上摇，宝珠的光依次点亮九层的窗
const TIER_H = (k: number) => 306 - 5.25 * k;
const tierBottom = (k: number) => { let y = 3230; for (let j = 0; j < k; j++) y -= TIER_H(j); return y; };
const winY = (k: number) => tierBottom(k) - TIER_H(k) * 0.5;
const ShotD: React.FC = () => {
  const t = useT();
  const td = t - T_D;
  const kf = track(t, [[T_D + 0.3, 0], [T_E - 0.4, 8.6]]);            // 爬到第几层（小数）
  const k0 = Math.min(Math.floor(kf), 8), fr = kf - k0;
  const zig = (x: number) => { const m = ((x % 2) + 2) % 2; return (m < 1 ? m : 2 - m) * 2 - 1; };   // 三角波 -1..1
  const hx = 960 + 250 * zig(kf * 1.0 + 0.5);
  const fe = fr * fr * (3 - 2 * fr);
  const hy = lerp(tierBottom(k0), tierBottom(k0 + 1), fe) - 6;
  const cam = at(960, hy - 292, 1.04);        // 相机跟着石娃走，脚底落在屏幕 y≈830（字幕带的上沿是 845）
  const KS = 0.26;
  const pools = usePool(cam, hx, hy, 1920, 3400, false, 300, 1, KS);
  const wind = (t * 900) % 1400;
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3} w={1920} h={3400}><Bg name="pagoda_far" /></Layer>
      <Layer p={0.62} w={1920} h={3400}><Bg name="pagoda_mid" /></Layer>
      <Layer p={1} w={1920} h={3400}>
        <Bg name="pagoda_near" />
        {Array.from({length: 9}, (_, k) => {
          const o = ramp(kf, k - 0.5, k + 0.3);
          return o > 0.01 ? <PaperGlow key={k} x={960} y={winY(k)} r={92} o={0.9 * o} /> : null;
        })}
        <Hero x={hx} y={hy} walk={4} kid={KS} />
      </Layer>
    </Stage>
  );
  return (
    <>
      <Lit world={world} pools={pools} />
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', opacity: 0.4 * ramp(td, 0.5, 1.5)}}>
        {[160, 420, 700, 1200, 1500, 1760].map((x, i) => {
          const y = ((wind * (0.7 + (i % 3) * 0.25) + i * 230) % 1300) - 150;
          return <line key={i} x1={x} y1={y} x2={x - 6} y2={y + 120} stroke="#efe8d8" strokeWidth={1.8} strokeLinecap="round" opacity={0.5} />;
        })}
      </svg>
    </>
  );
};

// ───────── 镜头 E：塔顶。石娃走到鼓前，举起手，“咚——”，波纹一圈圈扩开，云缝裂开
const DRUM = {x: 1200, y: GY - 120 + 6, s: 0.95};
const ShotE: React.FC = () => {
  const t = useT();
  const te = t - T_E;
  const th = HIT - T_E;                                   // 击鼓的时刻（镜头内秒数）
  const kx = track(te, [[0.3, 560], [1.4, 960]]);
  const walking = te > 0.3 && te < 1.4;
  const raise = ramp(te, th - 1.3, th - 0.2);
  const slap = ramp(te, th - 0.2, th) * (1 - ramp(te, th + 0.1, th + 1.4) * 0.8);
  const armRot = -105 * raise + 38 * slap;
  const after = Math.max(0, te - th);
  const pulse = te >= th ? Math.exp(-after * 1.6) : 0;
  const cam = useCam([{t: T_E, ...atg(960, 1.16)}, {t: HIT, ...atg(1040, 1.24)}, {t: 99, ...atg(1100, 1.3)}]);
  const pools = usePool(cam, kx, GY + 4, 2400, 1080, false, 330 + 260 * pulse);
  const sh = pearlPos(kx, GY + 4, KID_S, false, 'side');
  const seam = ramp(te, th + 0.5, th + 3.8);
  const dp = project(cam, 1, DRUM.x, DRUM.y - 142 * DRUM.s, 2400, 1080);
  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3} w={2400}><Bg name="pagoda_top_far" /></Layer>
      <Layer p={1} w={2400}>
        <Bg name="pagoda_top_near" />
        <Sprite name="drum" x={DRUM.x} y={DRUM.y} s={DRUM.s * (1 + 0.012 * pulse)} breathe={0} sway={0} />
        <GroundShadow x={kx} y={GY + 4} rx={90} o={0.45} />
        <Sprite name="shiwa_side_noarm" x={kx} y={GY + 4} s={KID_S} walk={walking ? 6 : 0} breathe={0.008} sway={0.3} />
        <Houzi view="side" kid={KID_S} x={kx + 13.5 * KID_S + 2} y={GY + 4 - 249 * KID_S + 14} flip sway={0.5} walk={walking ? 6 : 0} />
        <Sprite name="shiwa_side_arm" x={kx + 13.5 * KID_S} y={GY + 4 - 249 * KID_S + 14 * KID_S} s={KID_S} rot={armRot} breathe={0} sway={0} />
        <Pearl x={sh.x} y={sh.y} />
      </Layer>
    </Stage>
  );
  return (
    <>
      <Lit world={world} pools={pools} />
      {/* 云缝：天上裂开一道淡淡的灰金的缝 */}
      <div style={{position: 'absolute', left: 1180, top: 60, width: 24 + 70 * seam, height: 60 + 330 * seam, borderRadius: '50%', transform: 'rotate(8deg)', opacity: 0.9 * seam, mixBlendMode: 'screen', pointerEvents: 'none',
        background: 'radial-gradient(ellipse at center, rgba(223,210,168,0.95) 0%, rgba(207,194,154,0.55) 35%, rgba(207,194,154,0) 72%)'}} />
      {/* “咚”：一圈圈扩散的波纹 */}
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
        {[0, 0.28, 0.56, 0.84].map((d, i) => {
          const q = (after - d) / 2.4;
          if (te < th || q <= 0 || q >= 1) return null;
          return <circle key={i} cx={dp.x} cy={dp.y} r={(60 + q * 1100) * dp.zoom} fill="none" stroke="#efe8d8" strokeWidth={4 * (1 - q) + 0.8} opacity={0.75 * (1 - q)} />;
        })}
      </svg>
    </>
  );
};

export const S5: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const indoor = ramp(t, T_C - 0.4, T_C + 0.9) * (1 - ramp(t, T_D - 0.6, T_D + 0.4));      // 殿里不下雪
  const shots = [
    {from: 0, el: <ShotA />},
    {from: T_B, map: 'a' as const, el: <ShotB />},
    {from: T_C, map: 'c' as const, el: <ShotC />},
    {from: T_D, map: 'd' as const, el: <ShotD />},
    {from: T_E, map: 'b' as const, el: <ShotE />},
  ];
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night"><ShotStack shots={shots} /></VariantCtx.Provider>
      <Snow amount={0.3 * (1 - indoor)} wind={0.06} speed={0.5} />
    </SceneWrap>
  );
};
