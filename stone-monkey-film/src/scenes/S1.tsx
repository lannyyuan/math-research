import React, {useContext} from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {GroundShadow} from '../fx/Sprite';
import {PaperGlow} from '../fx/Light';
import {InkIn} from '../fx/InkIn';
import {VariantCtx, Variant, CharsCtx} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, track, at, atg, lerp, cuesOf} from './kit';
import {Shiwa, Nainai, Houzi, KID_S, KP, off} from './cast';

// 第一部 天黑了：天上挂着一盏大灯（白天，灰金色的光）→ 灯灭 → 奶奶在门口，脸全白了 → 石娃把耳朵贴在老树下的怪石上 → 石头裂开，蹦出巴掌大的龟甲
const C = cuesOf('s1-dark');
const GY = 832;
const DOOR_X = 691;
const STONE = {x: 1960, top: 552, mouth: [1960, 745]};
const T_WIPE = 14.4;  // 灯灭之后，水墨洇开，转到村口

const Lamp: React.FC<{v: Variant}> = ({v}) => {
  const X = 1850, Y = 250;
  if (v === 'day') {
    return (
      <>
        <div style={{position: 'absolute', left: X - 520, top: Y - 520, width: 1040, height: 1040, borderRadius: '50%', mixBlendMode: 'screen', background: 'radial-gradient(circle, rgba(240,232,208,0.55) 0%, rgba(230,226,208,0.28) 25%, rgba(220,220,210,0.1) 50%, rgba(220,220,210,0) 70%)'}} />
        <div style={{position: 'absolute', left: X - 170, top: Y - 170, width: 340, height: 340, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,253,244,1) 0%, rgba(246,240,222,0.98) 52%, rgba(232,226,204,0.9) 74%, rgba(224,222,206,0) 100%)'}} />
      </>
    );
  }
  return <Bg name="lamp_dead" x={X - 220} y={Y - 220} w={440} h={440} />;
};

export const S1: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const show = useContext(CharsCtx);
  const night = ramp(t, 10.8, 14.2);       // 灯灭：白天 → 夜色
  // 镜头 A：远眺山谷（只有景）；镜头 B：村口（脚底始终在字幕带之上）
  const camA = useCam([{t: 0, ...at(1500, 540, 1.0)}, {t: T_WIPE + 2, ...at(1380, 548, 1.08)}]);
  const camB = useCam([
    {t: 0, ...atg(1250, 1.04)},
    {t: 17, ...atg(1250, 1.04)},
    {t: 20.6, ...atg(840, 1.22)},
    {t: 27.5, ...atg(850, 1.22)},
    {t: 33, ...atg(1730, 1.18)},
    {t: 36.5, ...atg(1860, 1.5)},
    {t: 40, ...atg(1880, 1.7)},
    {t: len, ...atg(1880, 1.95)},
  ]);

  // 石娃：从右边跑回家（14.8~20.4）→ 站在门口和奶奶说话 → 走到怪石边（28~33.5）→ 耳朵贴石头
  const kidX = t < 27.8 ? track(t, [[T_WIPE + 0.6, 1560], [20.4, 910]]) : track(t, [[28.3, 910], [33.6, 1838]]);
  const kidWalk = (t > T_WIPE + 0.6 && t < 20.4) || (t > 28.3 && t < 33.6);
  const faceLeft = t < 28.0;
  const lean = ramp(t, 33.6, 35.0) * 6;
  const nainaiO = ramp(t, 19.0, 20.6);
  const nainaiX = lerp(DOOR_X + 24, DOOR_X, ramp(t, 19.0, 20.8));
  const speak = ramp(t, C[4].t + 0.3, C[4].t + 1.2) * (1 - ramp(t, C[4].t + C[4].d - 1.5, C[4].t + C[4].d - 0.3));
  const tCrack = C[5].t + 1.6, tBurst = C[5].t + 3.4;
  const crack = ramp(t, tCrack, tCrack + 1.6);
  const burst = ramp(t, tBurst - 0.15, tBurst + 0.35) * (1 - ramp(t, tBurst + 0.5, tBurst + 2.4));
  const jump = ramp(t, tBurst, tBurst + 1.5);
  const sh = off('shiwa_side', KP.shiwa_side.sh, KID_S, false);
  const landX = 1838 + sh.dx + 2, landY = GY + 4 + sh.dy + 16;
  const hx = lerp(STONE.x, landX, jump), hy = lerp(STONE.top + 8, landY, jump) - Math.sin(jump * Math.PI) * 150;
  const houziO = ramp(t, tBurst - 0.05, tBurst + 0.12);
  const spin = jump < 1 ? jump * 330 : 0;
  const wipe = ramp(t, T_WIPE, T_WIPE + 2.0);

  const worldA = (v: Variant) => (
    <Stage cam={camA}>
      <Layer p={0.3}><Bg name="village_far" /><Lamp v={v} /></Layer>
      <Layer p={0.6}><Bg name="village_mid" /></Layer>
      <Layer p={1}><Bg name="village_near2" /></Layer>
    </Stage>
  );
  const worldB = (v: Variant) => (
    <Stage cam={camB}>
      <Layer p={0.35}><Bg name="village_far" /><Lamp v={v} /></Layer>
      <Layer p={0.65}><Bg name="village_mid" /></Layer>
      <Layer p={1}>
        <Bg name="village_near" />
        <PaperGlow x={STONE.mouth[0]} y={STONE.mouth[1] - 60} r={190} o={0.42 * speak + 0.8 * burst + 0.18 * crack} />
        {show && (
          <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0, mixBlendMode: 'screen', opacity: 0.9 * (1 - burst * 0.5)}}>
            <defs><filter id="cg"><feGaussianBlur stdDeviation="2.5" /></filter></defs>
            <g stroke="#e9e6da" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" fill="none" filter="url(#cg)"><path pathLength={100} strokeDasharray={100} strokeDashoffset={100 - 100 * crack} d="M1958 600 L1949 628 L1957 652 L1944 684 L1962 706 L1951 742 L1960 776 L1952 812" /></g>
            <g stroke="#f7f4ea" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" fill="none"><path pathLength={100} strokeDasharray={100} strokeDashoffset={100 - 100 * crack} d="M1958 600 L1949 628 L1957 652 L1944 684 L1962 706 L1951 742 L1960 776 L1952 812" /></g>
            <g stroke="#f7f4ea" strokeWidth={1.2} strokeLinecap="round" fill="none" opacity={crack}><path d="M1957 652 L1976 664 L1990 680" /><path d="M1944 684 L1930 700" /><path d="M1951 742 L1970 750" /></g>
          </svg>
        )}
        <GroundShadow x={DOOR_X} y={GY + 2} rx={110} o={0.45 * nainaiO} />
        <Nainai x={nainaiX} y={GY} opacity={nainaiO} t0={0.4} />
        <GroundShadow x={kidX} y={GY + 6} rx={90} o={0.5} />
        <Shiwa view="side" x={kidX} y={GY + 4} flip={faceLeft} walk={kidWalk ? 6 : 0} rot={lean * (faceLeft ? -1 : 1)} t0={0.2} />
        {houziO > 0.01 && <Houzi view="front" x={hx} y={hy} rot={spin} opacity={houziO} sway={jump < 1 ? 0 : 0.6} />}
      </Layer>
    </Stage>
  );

  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={30}>
      {/* 镜头 A：山谷 */}
      <VariantCtx.Provider value="night">{worldA('night')}</VariantCtx.Provider>
      {night < 0.999 && (
        <div style={{position: 'absolute', inset: 0, opacity: 1 - night}}>
          <VariantCtx.Provider value="day">{worldA('day')}</VariantCtx.Provider>
        </div>
      )}
      {/* 镜头 B：村口（水墨洇开） */}
      <InkIn p={wipe} map="a">
        <VariantCtx.Provider value="night">{worldB('night')}</VariantCtx.Provider>
      </InkIn>
      <Snow amount={0.3 * night} wind={0.05} speed={0.5} />
    </SceneWrap>
  );
};
