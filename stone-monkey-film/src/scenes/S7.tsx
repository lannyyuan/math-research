import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Snow} from '../fx/Snow';
import {SeasonTree, Falling} from '../fx/Season';
import {VariantCtx, Variant} from '../fx/Variant';
import {Bg, SceneWrap, useT, ramp, lerp, clamp01, atg, cuesOf} from './kit';
import {Houzi, KID_S} from './cast';

// 尾声：石娃坐在老树下，龟甲趴在他膝上打哈欠。太阳升起又落下，四季轮转。最后一句字幕：“下一个故事，等你来讲。”
const C = cuesOf('s7-epilogue');
const GY = 832;
const SEAT = {x: 2050, y: GY - 22};

/** 一天的时间 tod：0 清晨 → .25 正午 → .5 傍晚 → .75 夜 → 1 清晨 */
const todOf = (t: number) => (t < 2 ? 0 : t < 5 ? (t - 2) / 3 : t < 8 ? (t - 5) / 3 : 0);
/** 四季的权重（春 夏 秋 冬）：2~3.5 春，3.5~5 夏，5~6.5 秋，6.5~8 冬，之后回到春 */
const seasonsOf = (t: number): number[] => {
  const k = (a: number, b: number) => ramp(t, a, b);
  const sp = Math.max(k(2.0, 2.8) * (1 - k(3.5, 4.1)), k(8.1, 9.2));
  const su = k(3.4, 4.1) * (1 - k(5.0, 5.6));
  const au = k(4.9, 5.6) * (1 - k(6.5, 7.1));
  const wi = k(6.4, 7.1) * (1 - k(8.0, 8.6));
  return [sp, su, au, wi];
};

export const S7: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([{t: 0, ...atg(2020, 1.12)}, {t: 9, ...atg(2030, 1.16)}, {t: len, ...atg(2040, 1.32)}]);
  const tod = todOf(t);
  const dayK = tod <= 0.5 ? clamp01(Math.sin(2 * Math.PI * tod) * 1.1) : 0;
  const nightK = tod > 0.5 ? clamp01(-Math.sin(2 * Math.PI * tod) * 1.1) : 0;
  const w = seasonsOf(t);
  // 太阳：白天从左升到右落（tod 0~.5）
  const u = clamp01(tod * 2);
  const sunO = tod < 0.5 && tod > 0 ? Math.sin(Math.PI * u) ** 0.5 : t < 2 || t > 8 ? 0.0 : 0;
  const sunX = lerp(700, 2300, u), sunY = lerp(560, 560, u) - Math.sin(Math.PI * u) * 360;
  // 哈欠
  const yawn = ramp(t, 2.2, 3.0) * (1 - ramp(t, 4.0, 4.8));

  const world = (v: Variant) => (
    <Stage cam={cam}>
      <Layer p={0.3}>
        <Bg name="village_far" />
        {sunO > 0.01 && (
          <>
            <div style={{position: 'absolute', left: sunX - 360, top: sunY - 360, width: 720, height: 720, borderRadius: '50%', mixBlendMode: 'screen', opacity: sunO, background: 'radial-gradient(circle, rgba(246,236,212,0.6) 0%, rgba(233,163,140,0.22) 30%, rgba(233,163,140,0) 68%)'}} />
            <div style={{position: 'absolute', left: sunX - 120, top: sunY - 120, width: 240, height: 240, borderRadius: '50%', opacity: sunO, background: 'radial-gradient(circle, rgba(255,250,236,1) 0%, rgba(246,238,216,0.96) 55%, rgba(236,226,200,0) 100%)'}} />
          </>
        )}
      </Layer>
      <Layer p={0.65}><Bg name="village_mid" /></Layer>
      <Layer p={1}>
        <Bg name="village_near" />
        <SeasonTree cx={2160} cy={330} rx={330} ry={230} w={w} t={t} />
        <Falling w={w} t={t} />
        <GroundShadow x={SEAT.x - 20} y={GY + 4} rx={150} o={0.45} />
        {/* 石娃坐在树下：上身 + 腿（腿绕髋转到水平向前，脸朝左） */}
        <Sprite name="shiwa_side_leg" x={SEAT.x} y={SEAT.y} s={KID_S} flip rot={-84} breathe={0} sway={0} />
        <Sprite name="shiwa_side_up" x={SEAT.x} y={SEAT.y} s={KID_S} flip rot={3} breathe={0.01} sway={0.4} />
        <Houzi view="front" x={SEAT.x - 92} y={SEAT.y - 8} kid={KID_S} sway={0} glow={0.4 + 0.5 * (1 - yawn)}>
          {yawn > 0.02 && <div style={{position: 'absolute', left: -9 * yawn, top: -64 * 0.27 * 2.2 - 6, width: 18 * yawn, height: 14 * yawn, borderRadius: '50%', background: '#2a2622', opacity: 0.9}} />}
        </Houzi>
      </Layer>
    </Stage>
  );

  return (
    <SceneWrap len={len} fadeIn={36} fadeOut={44}>
      <VariantCtx.Provider value="dawn">{world('dawn')}</VariantCtx.Provider>
      {dayK > 0.01 && <div style={{position: 'absolute', inset: 0, opacity: dayK}}><VariantCtx.Provider value="day">{world('day')}</VariantCtx.Provider></div>}
      {nightK > 0.01 && <div style={{position: 'absolute', inset: 0, opacity: nightK}}><VariantCtx.Provider value="night">{world('night')}</VariantCtx.Provider></div>}
      <Snow amount={0.5 * w[3]} wind={0.04} speed={0.5} />
    </SceneWrap>
  );
};
