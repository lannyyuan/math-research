import React from 'react';
import {Sprite, SpriteProps} from '../fx/Sprite';
import {HOUZI_RATIO} from '../palette';
import {ramp} from './kit';

/** 石娃的基准缩放（设定表像素 → 画面像素）：石娃高约 320 px，奶奶略高一点 */
export const KID_S = 0.84;
export const HOUZI_REL = (HOUZI_RATIO * 378) / 157;   // 龟甲相对石娃的缩放比：龟甲身高 = 石娃身高 × HOUZI_RATIO（三寸，约手掌大）

/** 精灵里的关键点（精灵像素，原点左上）；锚点 = 脚底 */
export const KP = {
  shiwa_front: {ax: 77, ay: 374, shL: [50, 124], shR: [106, 128], hL: [30, 248], hR: [128, 244], head: [77, 62], chest: [78, 170]},
  shiwa_side: {ax: 52.5, ay: 375, sh: [66, 126], hand: [90, 236], head: [64, 72], ear: [62, 80]},
  houzi_front: {ax: 58.5, ay: 152, eyes: [[37, 45], [62, 38]]},
  houzi_side: {ax: 45.5, ay: 147, eyes: [[42, 40]]},
};
/** 精灵关键点相对脚底的屏幕偏移 */
export const off = (name: keyof typeof KP, p: number[], s: number, flip = false) => {
  const k = KP[name] as any;
  return {dx: (p[0] - k.ax) * s * (flip ? -1 : 1), dy: (p[1] - k.ay) * s};
};

type Common = Omit<SpriteProps, 'name' | 'layers'>;

export const Shiwa: React.FC<Common & {view?: 'front' | 'side'}> = ({view = 'front', s = KID_S, ...r}) => <Sprite name={`shiwa_${view}`} s={s} {...r} />;

export const Nainai: React.FC<Common & {view?: 'front' | 'side'}> = ({view = 'front', s = KID_S * 1.03, ...r}) => (
  <Sprite name={`nainai_${view}`} layers={[`nainai_${view}`, `nainai_${view}_red`]} s={s} {...r} />
);

/** 龟甲：手掌大的石猴。kid 是同一个镜头里石娃的缩放（KID_S），龟甲的大小永远由它决定 */
export const Houzi: React.FC<Common & {kid?: number; view?: 'front' | 'side'; glow?: number}> = ({view = 'front', kid = KID_S, glow = 1, flip = false, children, ...r}) => {
  const s = kid * HOUZI_REL;
  const eyes = KP[`houzi_${view}` as const].eyes as number[][];
  return (
    <Sprite name={`houzi_${view}`} layers={[`houzi_${view}`, `houzi_${view}_eyes`]} s={s} flip={flip} breathe={0.012} v="lit" filter="brightness(0.92)" {...r}>
      {eyes.map((e, i) => {
        const o = off(`houzi_${view}` as any, e, s, flip);
        const R = 26 * s * 2.2;
        return <div key={i} style={{position: 'absolute', left: o.dx - R, top: o.dy - R, width: R * 2, height: R * 2, borderRadius: '50%', mixBlendMode: 'screen', opacity: 0.85 * glow, background: 'radial-gradient(circle, rgba(255,214,150,0.95) 0%, rgba(232,135,58,0.55) 22%, rgba(232,135,58,0.15) 50%, rgba(232,135,58,0) 72%)'}} />;
      })}
      {children}
    </Sprite>
  );
};
