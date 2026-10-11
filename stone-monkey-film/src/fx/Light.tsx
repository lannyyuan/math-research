import React, {useContext} from 'react';
import {CharsCtx, VariantCtx, Variant} from './Variant';

/** 光池：{x,y 屏幕坐标, r 半径(px), kind} —— 光照到哪里，那里才有颜色，其余都沉在靛蓝里 */
export interface Pool {x: number; y: number; r: number; k?: 'pearl' | 'sand' | 'fire'; o?: number}

/** 宝珠的光：奶白的核 + 灰金的晕（#F3D98A），不刺眼。mix-blend screen。 */
export const PearlGlow: React.FC<{x: number; y: number; r: number; o?: number; core?: number}> = ({x, y, r, o = 1, core = 1}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity: o, mixBlendMode: 'screen', pointerEvents: 'none',
    background: `radial-gradient(circle at center, rgba(255,250,232,${0.95 * core}) 0%, rgba(243,217,138,${0.55 * core}) 10%, rgba(243,217,138,0.28) 28%, rgba(223,200,140,0.10) 55%, rgba(223,200,140,0) 72%)`}} />
);
/** 星星的灰（沙）的光：冷白、很小 */
export const SandGlow: React.FC<{x: number; y: number; r: number; o?: number}> = ({x, y, r, o = 1}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity: o, mixBlendMode: 'screen', pointerEvents: 'none',
    background: 'radial-gradient(circle at center, rgba(248,250,255,0.95) 0%, rgba(205,222,245,0.4) 14%, rgba(170,195,235,0.14) 40%, rgba(170,195,235,0) 70%)'}} />
);
/** 篝火 / 火种的光：#E8873A */
export const FireGlow: React.FC<{x: number; y: number; r: number; o?: number}> = ({x, y, r, o = 1}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity: o, mixBlendMode: 'screen', pointerEvents: 'none',
    background: 'radial-gradient(circle at center, rgba(255,226,170,0.9) 0%, rgba(232,135,58,0.5) 14%, rgba(232,135,58,0.18) 38%, rgba(232,135,58,0) 70%)'}} />
);
/** 窗里的冷白光（纸白，不是暖色） */
export const PaperGlow: React.FC<{x: number; y: number; r: number; o?: number}> = ({x, y, r, o = 1}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity: o, mixBlendMode: 'screen', pointerEvents: 'none',
    background: 'radial-gradient(circle at center, rgba(239,232,216,0.85) 0%, rgba(220,226,232,0.3) 22%, rgba(190,205,225,0.1) 50%, rgba(190,205,225,0) 72%)'}} />
);

const maskOf = (pools: Pool[]) => pools.map((p) => `radial-gradient(circle at ${p.x}px ${p.y}px, rgba(0,0,0,${p.o ?? 1}) 0px, rgba(0,0,0,${(p.o ?? 1) * 0.92}) ${p.r * 0.42}px, rgba(0,0,0,${(p.o ?? 1) * 0.5}) ${p.r * 0.72}px, rgba(0,0,0,0) ${p.r}px)`).join(',');

/**
 * 两遍着色：先画夜色版本的整个世界；再把“被光照到的版本”(lit) 用若干个圆形软蒙版叠上去。
 * world(v) 是一个函数：给定光照版本，返回整个世界（Stage + 角色 + 道具）。pools 是屏幕坐标里的光池。
 */
export const Lit: React.FC<{world: (v: Variant) => React.ReactNode; pools: Pool[]; base?: Variant}> = ({world, pools, base = 'night'}) => {
  const showChars = useContext(CharsCtx);
  const live = pools.filter((p) => p.r > 2 && (p.o ?? 1) > 0.01);
  const m = live.length ? maskOf(live) : '';
  return (
    <>
      <VariantCtx.Provider value={base}>{world(base)}</VariantCtx.Provider>
      {live.length > 0 && (
        <div style={{position: 'absolute', inset: 0, WebkitMaskImage: m, maskImage: m, WebkitMaskComposite: 'source-over', maskComposite: 'add', WebkitMaskRepeat: 'no-repeat', maskRepeat: 'no-repeat'} as React.CSSProperties}>
          <VariantCtx.Provider value="lit">{world('lit')}</VariantCtx.Provider>
        </div>
      )}
      {live.map((p, i) => (p.k === 'sand' ? <SandGlow key={i} x={p.x} y={p.y} r={p.r * 0.55} o={(p.o ?? 1) * 0.8} /> : p.k === 'fire' ? <FireGlow key={i} x={p.x} y={p.y} r={p.r * 0.8} o={p.o ?? 1} /> : <PearlGlow key={i} x={p.x} y={p.y} r={p.r * 0.5} o={0.8 * (p.o ?? 1)} />))}
    </>
  );
};
