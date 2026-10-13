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
export const Layer: React.FC<{p: number; children: React.ReactNode; style?: React.CSSProperties}> = ({p, children, style}) => {
  const c = useContext(CamCtx);
  const zoom = 1 + (c.z - 1) * (0.45 + 0.55 * p);
  return (
    <div
      style={{
        position: 'absolute', left: 0, top: 0, width: W, height: H,
        transformOrigin: `${W / 2}px ${H / 2}px`,
        transform: `translate(${-c.x * p * zoom}px, ${-c.y * p * zoom}px) scale(${zoom})`,
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
