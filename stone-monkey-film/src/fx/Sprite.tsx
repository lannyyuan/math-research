import React, {useContext} from 'react';
import {Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import meta from '../../public/sprites/sprites.json';
import {CharsCtx, useVariant} from './Variant';

type M = {w: number; h: number; ax: number; ay: number; night?: boolean};
const MT = meta as Record<string, M>;
export const spriteMeta = (n: string) => MT[n];

/** 精灵文件：夜色版本是 <name>_night.png（调色后的），其余用原色（再由 CSS 微调） */
export const spriteUrl = (n: string, v: string) => staticFile(`sprites/${n}${v === 'night' && MT[n]?.night !== false ? '_night' : ''}.png`);

export interface SpriteProps {
  name: string;
  layers?: string[]; // 从下到上叠放的图层（默认只有 name 自己）
  x: number; // 脚底中心的世界坐标
  y: number;
  s?: number;
  flip?: boolean;
  rot?: number; // 度，绕脚底
  breathe?: number;
  sway?: number;
  walk?: number;
  t0?: number;
  opacity?: number;
  style?: React.CSSProperties;
  filter?: string;
  children?: React.ReactNode; // 画在精灵坐标系里的东西（脚底为原点，未缩放）
  lo?: number[];
  clipBottom?: number;
  pivot?: [number, number]; // 旋转的支点（精灵像素，相对脚底锚点；默认脚底）
  extra?: {name: string; dx: number; dy: number; s?: number; rot?: number; opacity?: number; clip?: number; flip?: boolean}[];
  alwaysShow?: boolean; // 不受 chars=false 影响（背景里的东西）
}

/** 纸偶：把设定图抠出来的精灵摆在画面上，只做轻微的呼吸、晃动、走路颠簸（局部关节动作由叠加的小精灵/children 完成）。 */
export const Sprite: React.FC<SpriteProps> = ({name, layers, x, y, s = 0.7, flip = false, rot = 0, breathe = 0.008, sway = 0.5, walk = 0, t0 = 0, opacity = 1, style, filter, children, extra, clipBottom = 0, lo, pivot, alwaysShow}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const showChars = useContext(CharsCtx);
  const v = useVariant();
  if (!showChars && !alwaysShow) return null;
  const t = f / fps + t0;
  const m = MT[name];
  if (!m) return null;
  const br = 1 + breathe * Math.sin((t * 2 * Math.PI) / 3.8);
  const sw = sway * Math.sin((t * 2 * Math.PI) / 5.3);
  const bob = walk ? -Math.abs(Math.sin(t * Math.PI * 1.45)) * walk : 0;
  const lean = walk ? Math.sin(t * Math.PI * 1.45) * 0.9 : 0;
  const ls = layers ?? [name];
  const px = pivot ? pivot[0] * s : 0, py = pivot ? pivot[1] * s : 0;
  return (
    <div
      style={{
        position: 'absolute', left: x, top: y + bob, width: 0, height: 0, opacity,
        transform: `scale(${flip ? -1 : 1}, 1) translate(${px}px, ${py}px) rotate(${rot + sw + lean}deg) translate(${-px}px, ${-py}px) scale(1, ${br})`,
        transformOrigin: '0 0', filter, ...style,
      }}
    >
      {ls.map((n, li) => {
        const mm = MT[n] ?? m;
        return <Img key={n} src={spriteUrl(n, v)} style={{position: 'absolute', left: -m.ax * s, top: -m.ay * s, width: mm.w * s, height: mm.h * s, opacity: lo ? lo[li] : 1, clipPath: clipBottom ? `inset(0 0 ${clipBottom * 100}% 0)` : undefined}} />;
      })}
      {extra?.map((e) => {
        const em = MT[e.name];
        const es = (e.s ?? 1) * s;
        return (
          <Img key={e.name + e.dx} src={spriteUrl(e.name, v)}
            style={{position: 'absolute', left: e.dx * s - em.ax * es, top: e.dy * s - em.ay * es, width: em.w * es, height: em.h * es, opacity: e.opacity ?? 1, clipPath: e.clip ? `inset(0 0 ${e.clip * 100}% 0)` : undefined, transform: `rotate(${e.rot ?? 0}deg) scale(${e.flip ? -1 : 1}, 1)`, transformOrigin: `${em.ax * es}px ${em.ay * es}px`}} />
        );
      })}
      {children}
    </div>
  );
};

/** 脚下的软影（墨色，贴在地上） */
export const GroundShadow: React.FC<{x: number; y: number; rx: number; ry?: number; o?: number}> = ({x, y, rx, ry, o = 0.5}) => {
  const showChars = useContext(CharsCtx);
  if (!showChars) return null;
  return <div style={{position: 'absolute', left: x - rx, top: y - (ry ?? rx * 0.14), width: rx * 2, height: (ry ?? rx * 0.14) * 2, borderRadius: '50%', background: `radial-gradient(ellipse at center, rgba(20,24,40,${o}) 0%, rgba(20,24,40,${o * 0.5}) 50%, rgba(20,24,40,0) 100%)`}} />;
};
