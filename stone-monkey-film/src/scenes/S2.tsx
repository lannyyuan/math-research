import React, {useContext} from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {GroundShadow, Sprite} from '../fx/Sprite';
import {PaperGlow} from '../fx/Light';
import {InkIn} from '../fx/InkIn';
import {Ripple, Splash, Bubbles, WaterVeil} from '../fx/Water';
import {VariantCtx, CharsCtx} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, track, at, atg, lerp, cuesOf} from './kit';
import {Shiwa, Nainai, Houzi, Pair, KID_S, KP, off} from './cast';

// 第二部 河边搭桥：奶奶包针（红布包）→ 石娃一步三回头 → 断桥 → 两人搬竹板、捆绳 → 水底一双大眼，大鱼摆尾 → 桥加高，大鱼送鳞片
const C = cuesOf('s2-bridge');
const GY = 832;
const T_B = 6.9;    // 灶间 → 村口（水墨洇开）
const T_C = 13.4;   // 村口 → 江边

export const S2: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const show = useContext(CharsCtx) >= 2;

  // ───────── 镜头 A：灶间。奶奶在桌后包针，递给石娃
  const camA = useCam([{t: 0, ...atg(1220, 1.22)}, {t: T_B + 1.5, ...atg(1300, 1.3)}]);
  const wrap = ramp(t, 0.8, 3.6);                                  // 红布一层层包上去
  const give = ramp(t, 4.4, 6.2);                                  // 递给石娃
  const bx = lerp(912, 1560, give), by = lerp(716, 690, give) - Math.sin(give * Math.PI) * 40;
  const bundleO = ramp(t, 0.5, 1.0) * (1 - ramp(t, 6.0, 6.7));
  const bundleRot = (1 - wrap) * Math.sin(t * 9) * 8 + give * 6;

  // ───────── 镜头 B：村口，石娃一步三回头
  const camB = useCam([{t: 0, ...atg(900, 1.15)}, {t: T_B + 7, ...atg(1750, 1.15)}]);
  // 石娃的位置：走 → 停下回头 → 走 → 回头 → 走 → 回头 → 走
  const walkB = (tt: number) => {
    const keys: [number, number][] = [[7.3, 910], [8.6, 1100], [9.2, 1100], [10.3, 1300], [10.9, 1300], [12.0, 1500], [12.6, 1500], [14.0, 1800]];
    return track(tt, keys);
  };
  const kidBx = walkB(t);
  const pauseB = (t > 8.6 && t < 9.4) || (t > 10.3 && t < 11.1) || (t > 12.0 && t < 12.9);
  const lookBack = pauseB;       // 回头：脸朝左（朝家的方向）
  const walkingB = t > 7.3 && t < 14.0 && !pauseB;

  // ───────── 镜头 C：江边
  const camC = useCam([
    {t: 0, ...at(900, 760, 1.0)},
    {t: 20, ...at(1250, 700, 1.04)},
    {t: 26, ...at(1300, 760, 1.1)},
    {t: 28.5, ...at(1450, 1010, 1.12)},
    {t: 33.0, ...at(1450, 1010, 1.12)},
    {t: 36.5, ...at(1500, 800, 1.1)},
    {t: len, ...at(1700, 780, 1.08)},
  ]);
  // 石娃的位置（世界坐标，左岸 x<1080，桥 x1080~1820）
  const kidCx = t < C[3].t - 0.6 ? track(t, [[T_C + 0.6, 260], [C[2].t + 0.8, 990]])
    : track(t, [[C[3].t - 0.6, 990], [C[3].t + 0.9, 760], [C[3].t + 2.6, 790], [C[3].t + 4.6, 1380], [C[4].t - 0.5, 1380], [C[5].t + 3.4, 1380], [len - 1.5, 1700]]);
  const kidCwalk = (t > T_C + 0.6 && t < C[2].t + 0.8) || (t > C[3].t - 0.6 && t < C[3].t + 0.9) || (t > C[3].t + 2.6 && t < C[3].t + 4.6) || t > len - 4.0;
  const faceLeftC = t > C[3].t - 0.4 && t < C[3].t + 1.2;
  // 桥：断 → 低 → 高
  const bridgeLow = ramp(t, C[3].t + 2.2, C[3].t + 4.2);
  const bridgeHigh = ramp(t, C[4].t + 0.6, C[4].t + 4.2);
  const bridgeBroken = 1 - bridgeLow;
  // 木板：从材料堆被扛到桥上
  const plankCarry = t > C[3].t + 0.9 && t < C[3].t + 4.6;
  // 大鱼：水底的眼（C[4]），摆尾，跃出水面（C[5] 开头）
  const fishEyes = ramp(t, C[4].t + 0.2, C[4].t + 1.6) * (1 - ramp(t, C[5].t - 0.4, C[5].t + 0.3));
  const leap = ramp(t, C[5].t - 0.6, C[5].t + 1.8);
  const fishX = lerp(1300, 1560, leap), fishY = lerp(1330, 1250, leap) - Math.sin(leap * Math.PI) * 520;
  const fishRot = lerp(-25, 40, leap);
  const fishSideO = ramp(t, C[5].t - 0.7, C[5].t - 0.4) * (1 - ramp(t, C[5].t + 1.8, C[5].t + 2.2));
  const scaleFly = ramp(t, C[5].t + 1.0, C[5].t + 2.6);
  const kidSh = off('shiwa_side', KP.shiwa_side.hand, KID_S, false);
  const scX = lerp(fishX, kidCx + kidSh.dx + 20, scaleFly), scY = lerp(fishY, GY + kidSh.dy - 60, scaleFly) - Math.sin(scaleFly * Math.PI) * 60;
  const scaleO = ramp(t, C[5].t + 0.9, C[5].t + 1.3);
  const sinceLeap = t - (C[5].t + 0.9);

  const wipeB = ramp(t, T_B - 0.4, T_B + 1.6);
  const wipeC = ramp(t, T_C - 0.6, T_C + 1.6);

  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      <VariantCtx.Provider value="night">
        {/* A：灶间 */}
        <Stage cam={camA}>
          <Layer p={0.4} w={2400}><Bg name="kitchen_far" /></Layer>
          <Layer p={1} w={2400}>
            <Nainai x={905} y={GY} t0={0.3} />
            <Bg name="kitchen_near" />
            <PaperGlow x={1780} y={470} r={260} o={0.4} />
            <GroundShadow x={1620} y={GY + 4} rx={90} o={0.5} />
            <Shiwa view="side" x={1620} y={GY + 4} flip t0={0.2} />
            <Sprite name="bundle_red" x={bx} y={by} s={0.5 * (0.55 + 0.45 * wrap)} rot={bundleRot} opacity={bundleO} breathe={0} sway={0} v="lit" alwaysShow />
          </Layer>
        </Stage>
        {/* B：村口 */}
        <InkIn p={wipeB} map="b">
          <Stage cam={camB}>
            <Layer p={0.35}><Bg name="village_far" /></Layer>
            <Layer p={0.65}><Bg name="village_mid" /></Layer>
            <Layer p={1}>
              <Bg name="village_near" />
              <GroundShadow x={691} y={GY + 2} rx={110} o={0.45} />
              <Nainai x={691} y={GY} t0={0.4} />
              <GroundShadow x={kidBx} y={GY + 6} rx={90} o={0.5} />
              <Pair x={kidBx} y={GY + 4} flip={lookBack} walk={walkingB ? 6 : 0} t0={0.2} />
            </Layer>
          </Stage>
        </InkIn>
        {/* C：江边 */}
        <InkIn p={wipeC} map="c">
          <Stage cam={camC}>
            <Layer p={0.3} w={2900} h={1500}><Bg name="river_far" /></Layer>
            <Layer p={0.62} w={2900} h={1500}><Bg name="river_mid" /></Layer>
            <Layer p={1} w={2900} h={1500}>
              <Bg name="river_near" />
              <Bg name="river_bridge_broken" opacity={bridgeBroken} />
              <Bg name="river_bridge_low" opacity={bridgeLow * (1 - bridgeHigh)} />
              <Bg name="river_bridge_high" opacity={bridgeHigh} />
              {/* 大鱼在水里：先是一双眼（盖着水的面纱），再跃出水面 */}
              <div style={{position: 'absolute', inset: 0, opacity: fishEyes}}>
                <Sprite name="fish_front" x={1300} y={1295} s={1.25} breathe={0.01} sway={1.2} alwaysShow />
                <WaterVeil y0={1180} y1={1500} o={0.55} />
              </div>
              <Ripple x={1300} y={1190} r={170} p={ramp(t, C[4].t + 0.2, C[4].t + 3.5)} n={3} />
              <Ripple x={1500} y={1190} r={240} p={ramp(t, C[5].t + 1.6, C[5].t + 4.4)} n={4} />
              <Splash x={1560} y={1210} t={t - (C[5].t - 0.1)} n={26} power={1.1} seed={4} />
              {fishSideO > 0.01 && <Sprite name="fish_side" x={fishX} y={fishY} s={1.2} rot={fishRot} opacity={fishSideO} breathe={0} sway={0} alwaysShow />}
              {scaleO > 0.01 && <Sprite name="scale" x={scX} y={scY} s={0.5} opacity={scaleO * (1 - ramp(t, C[5].t + 2.5, C[5].t + 3.0))} breathe={0.02} sway={4} v="lit" alwaysShow />}
              <GroundShadow x={kidCx} y={GY + 6} rx={90} o={0.45} />
              <Pair x={kidCx} y={GY + 4} flip={faceLeftC} walk={kidCwalk ? 6 : 0} t0={0.2} />
              {plankCarry && <Sprite name="plank" x={kidCx - 4} y={GY - 262} s={0.62} rot={-12} breathe={0} sway={0} alwaysShow />}
            </Layer>
          </Stage>
        </InkIn>
      </VariantCtx.Provider>
      <Snow amount={0.25} wind={0.05} speed={0.5} />
    </SceneWrap>
  );
};
