import React, {createContext, useContext} from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {W, H} from '../palette';

export interface Cam { x: number; y: number; z: number }
const CamCtx = createContext<Cam>({x: 0, y: 0, z: 1});

/** 镜头关键帧（t 为场景内秒数），之间用缓入缓出的正弦插值——慢推、慢移 */
export interface CamKey { t: number; x?: number; y?: number; z?: number }
export function useCam(keys: CamKey[]): Cam {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const ts = keys.map((k) => k.t);
  const ease = Easing.inOut(Easing.sin);
  const f = (key: 'x' | 'y' | 'z', d: number) =>
    interpolate(t, ts, keys.map((k) => k[key] ?? d), {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return {x: f('x', 0), y: f('y', 0), z: f('z', 1)};
}

export const Stage: React.FC<{cam: Cam; children: React.ReactNode}> = ({cam, children}) => (
  <CamCtx.Provider value={cam}>
    <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>{children}</div>
  </CamCtx.Provider>
);

/** 视差层：p=0 在无穷远（不随镜头平移），p=1 在角色所在的地面 */
/** w/h 是这一层画面的实际大小（像素）：镜头永远不会摇出画面边缘（边缘露出空白就是穿帮），所以平移量被限制在图的范围内 */
export const Layer: React.FC<{p: number; children: React.ReactNode; style?: React.CSSProperties; w?: number; h?: number}> = ({p, children, style, w = 2900, h = 1080}) => {
  const c = useContext(CamCtx);
  const zoom = 1 + (c.z - 1) * (0.45 + 0.55 * p);
  const clampT = (v: number, size: number, view: number) => {
    // 图经缩放后覆盖 [view/2 + (0 - view/2)·zoom + t, view/2 + (size - view/2)·zoom + t]；要求左边 ≤ 0、右边 ≥ view
    const lo = view - (view / 2 + (size - view / 2) * zoom);
    const hi = -(view / 2 - (view / 2) * zoom);
    return lo > hi ? (lo + hi) / 2 : Math.min(hi, Math.max(lo, v));
  };
  const tx = clampT(-c.x * p * zoom, w, W);
  const ty = clampT(-c.y * p * zoom, h, H);
  return (
    <div
      style={{
        position: 'absolute', left: 0, top: 0, width: W, height: H,
        transformOrigin: `${W / 2}px ${H / 2}px`,
        transform: `translate(${tx}px, ${ty}px) scale(${zoom})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const Fade: React.FC<{children: React.ReactNode; from?: number; to?: number; at: number; dur?: number}> = ({children, from = 0, to = 1, at, dur = 1}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const o = interpolate(frame / fps, [at, at + dur], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
  return <div style={{position: 'absolute', inset: 0, opacity: o}}>{children}</div>;
};
