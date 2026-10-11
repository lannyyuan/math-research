import React, {createContext, useContext} from 'react';
import {Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import meta from '../../public/sprites/sprites.json';
import propMeta from '../../public/props/props.json';

type M = {w: number; h: number; ax: number; ay: number};
const SM = meta as Record<string, M>;
const PM = propMeta as Record<string, M>;
// 角色精灵在 public/sprites/，配角和道具在 public/props/；这样两种都能用同一个 <Sprite>
const MT: Record<string, M> = {...PM, ...SM};
const urlOf = (n: string) => staticFile(`${SM[n] ? 'sprites' : 'props'}/${n}.png`);
export const spriteMeta = (n: string) => MT[n];

/** 审计用：chars=false 时不画设定图里的五个角色（只留背景、道具和光），用来检查"暖色只出现在允许的地方" */
export const CharsCtx = createContext(true);
const isChar = (n: string) => /^(hazel|bud|bolts|comet|pebbles)_/.test(n);

export interface SpriteProps {
  name: string; // 决定尺寸和脚底锚点的精灵名
  layers?: string[]; // 从下到上叠放的图层（默认只有 name 自己）：Bud = [身体, 帽子/棒球帽]
  x: number; // 脚底中心的屏幕/世界坐标
  y: number;
  s?: number; // 缩放（精灵像素 → 画面像素）
  flip?: boolean;
  rot?: number; // 度，绕脚底
  breathe?: number; // 呼吸幅度（0.01 ≈ 1%）
  sway?: number; // 轻微晃动（度）
  walk?: number; // 走路的颠簸（像素）
  t0?: number;
  opacity?: number;
  style?: React.CSSProperties;
  filter?: string;
  children?: React.ReactNode; // 画在精灵坐标系里的东西（脚底为原点）
  lo?: number[]; // 每个图层各自的不透明度（和 layers 一一对应）：Bolts 的眼睛亮/灭的叠化
  clipBottom?: number; // 0~1：把精灵底部这一截藏起来（Bud 掉进冰窟窿、Hazel 坐在被子里）
  extra?: {name: string; dx: number; dy: number; s?: number; rot?: number; opacity?: number; clip?: number}[]; // 额外叠在精灵上的小精灵（口袋里的 Pebbles……），坐标是精灵像素，相对脚底锚点
}

/** 纸偶：把设定图抠出来的精灵摆在画面上，只做轻微的呼吸、晃动、走路颠簸。 */
export const Sprite: React.FC<SpriteProps> = ({name, layers, x, y, s = 0.7, flip = false, rot = 0, breathe = 0.008, sway = 0.5, walk = 0, t0 = 0, opacity = 1, style, filter, children, extra, clipBottom = 0, lo}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const showChars = useContext(CharsCtx);
  if (!showChars && isChar(name)) return null;
  const t = f / fps + t0;
  const m = MT[name];
  const br = 1 + breathe * Math.sin((t * 2 * Math.PI) / 3.8);
  const sw = sway * Math.sin((t * 2 * Math.PI) / 5.3);
  const bob = walk ? -Math.abs(Math.sin(t * Math.PI * 1.45)) * walk : 0;
  const lean = walk ? Math.sin(t * Math.PI * 1.45) * 0.9 : 0;
  const ls = layers ?? [name];
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y + bob,
        width: 0,
        height: 0,
        opacity,
        transform: `scale(${flip ? -1 : 1}, 1) rotate(${rot + sw + lean}deg) scale(1, ${br})`,
        transformOrigin: '0 0',
        filter,
        ...style,
      }}
    >
      {ls.map((n, li) => {
        const mm = MT[n];
        return <Img key={n} src={urlOf(n)} style={{position: 'absolute', left: -m.ax * s, top: -m.ay * s, width: mm.w * s, height: mm.h * s, opacity: lo ? lo[li] : 1, clipPath: clipBottom ? `inset(0 0 ${clipBottom * 100}% 0)` : undefined}} />;
      })}
      {extra?.map((e) => {
        const em = MT[e.name];
        const es = (e.s ?? 1) * s;
        return (
          <Img
            key={e.name + e.dx}
            src={urlOf(e.name)}
            style={{position: 'absolute', left: e.dx * s - em.ax * es, top: e.dy * s - em.ay * es, width: em.w * es, height: em.h * es, opacity: e.opacity ?? 1, clipPath: e.clip ? `inset(0 0 ${e.clip * 100}% 0)` : undefined, transform: `rotate(${e.rot ?? 0}deg)`, transformOrigin: `${em.ax * es}px ${em.ay * es}px`}}
          />
        );
      })}
      {children}
    </div>
  );
};

/** 脚下的软阴影（蓝灰色，贴在雪地上） */
export const GroundShadow: React.FC<{x: number; y: number; rx: number; ry?: number; o?: number}> = ({x, y, rx, ry, o = 0.5}) => (
  <div style={{position: 'absolute', left: x - rx, top: y - (ry ?? rx * 0.14), width: rx * 2, height: (ry ?? rx * 0.14) * 2, borderRadius: '50%', background: `radial-gradient(ellipse at center, rgba(70,90,140,${o}) 0%, rgba(80,100,150,${o * 0.5}) 50%, rgba(90,110,160,0) 100%)`}} />
);
