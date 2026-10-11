import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from '../timeline.json';
import {schedule} from '../schedule.mjs';
import {Layer} from '../fx/Stage';
import {W, H} from '../palette';

/** 版面：地平线 y、角色脚底 y。角色站在字幕带（y>860）上方 */
export const HZ = 560;
export const GY = 770;
/** 镜头对准世界坐标 (wx, wy)，缩放 z */
export const at = (wx: number, wy: number, z = 1) => ({x: wx - 960, y: wy - 540, z});

export const useT = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return f / fps;
};
export const cuesOf = (id: string) => schedule(timeline.scenes.find((s) => s.id === id)!);
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
/** 平滑过渡：t 从 a 到 b 之间，值从 0 平滑到 1 */
export const ramp = (t: number, a: number, b: number) => {
  const u = clamp01((t - a) / (b - a));
  return u * u * (3 - 2 * u);
};
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;

const img = (name: string, style: React.CSSProperties) => <Img src={staticFile(`baked/${name}`)} style={{position: 'absolute', ...style}} />;

/** 场景外壳：开头结尾各有一小段缓缓的明暗过渡（没有快切、没有花哨转场） */
export const SceneWrap: React.FC<{len: number; children: React.ReactNode; bg?: string}> = ({len, children, bg = '#070d28'}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const o = interpolate(f, [0, 20, len * fps - 26, len * fps - 1], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: bg}}>
      <div style={{position: 'absolute', inset: 0, opacity: o}}>{children}</div>
    </AbsoluteFill>
  );
};

/** 山：灯挂在山顶。cx 为山顶的横坐标，baseY 为山脚，k 为缩放。返回灯的位置 */
export const mountLamp = (cx: number, baseY: number, k: number): [number, number] => [cx, baseY - 800 * k + 70 * k];
export const Mountain: React.FC<{cx: number; baseY: number; k: number; tone?: 'night' | 'dawn'; opacity?: number}> = ({cx, baseY, k, tone = 'night', opacity = 1}) =>
  img(`mount-${tone}.png`, {left: cx - 1700 * k, top: baseY - 800 * k, width: 3400 * k, height: 800 * k, opacity});

export interface BackdropProps {
  dawn?: number; // 0 夜 → 1 破晓（天空渐变）
  horizon?: number;
  mount?: {cx: number; k: number; baseY?: number; tone?: 'night' | 'dawn'} | false;
  far?: boolean;
  mid?: boolean;
  snow?: 'snow-a' | 'snow-b';
  skyDx?: number;
  treesDx?: number;
  children?: React.ReactNode;
  tintTrees?: string; // 春天：给树林盖一层冷绿
  tintAmount?: number;
  ground?: boolean;
  underlay?: [string, string, string]; // 树林脚下的底色渐变（远、中两层共用：上、中、下）
  spring?: [number, number, number]; // 三档“雪化了”的地面，依次叠上去的不透明度
  mountFade?: boolean; // 山的左右边缘做渐隐（绘本插图里山不在画面边缘时，避免露出山图的矩形边）
}
/** 天空 → 远山 → 远林 → 近林 → 雪地。全部是预先烘焙好的水彩层，按视差随镜头移动 */
export const Backdrop: React.FC<BackdropProps> = ({dawn = 0, horizon = HZ, mount, far = true, mid = true, snow = 'snow-a', skyDx = 0, treesDx = 0, tintTrees, tintAmount = 0.55, spring, ground = true, underlay, mountFade = false}) => (
  <>
    <Layer p={0.06}>
      {img('sky-night.jpg', {left: -192 + skyDx, top: horizon - 810, width: 2304, height: 900, opacity: 1})}
      {dawn > 0.001 ? img('sky-dawn.jpg', {left: -192 + skyDx, top: horizon - 810, width: 2304, height: 900, opacity: dawn}) : null}
    </Layer>
    {mount ? (
      <Layer p={0.16} style={mountFade ? {WebkitMaskImage: 'linear-gradient(to right, transparent 0, #000 26%, #000 74%, transparent 100%)', maskImage: 'linear-gradient(to right, transparent 0, #000 26%, #000 74%, transparent 100%)', WebkitMaskSize: `${3400 * mount.k}px 100%`, maskSize: `${3400 * mount.k}px 100%`, WebkitMaskPosition: `${mount.cx - 1700 * mount.k}px 0`, maskPosition: `${mount.cx - 1700 * mount.k}px 0`, WebkitMaskRepeat: 'no-repeat', maskRepeat: 'no-repeat'} : undefined}>
        <Mountain cx={mount.cx} baseY={mount.baseY ?? horizon + 20} k={mount.k} tone="night" />
        {dawn > 0.01 ? <Mountain cx={mount.cx} baseY={mount.baseY ?? horizon + 20} k={mount.k} tone="dawn" opacity={dawn} /> : null}
      </Layer>
    ) : null}
    {far ? <Layer p={0.32}><div style={{position: 'absolute', left: -740, top: horizon + 10, width: 3400, height: 900, background: underlay ? `linear-gradient(${underlay[0]} 0, ${underlay[1]} 180px, ${underlay[2]} 420px)` : 'linear-gradient(#18265a 0, #2c4283 180px, #7f98cc 420px)'}} />{img('trees-far.png', {left: -740 + treesDx, top: horizon - 392, width: 3400, height: 420})}{tintTrees ? <div style={{position: 'absolute', left: -740, top: horizon - 392, width: 3400, height: 420, background: tintTrees, mixBlendMode: 'color', opacity: tintAmount, WebkitMaskImage: `url(${staticFile('baked/trees-far.png')})`, WebkitMaskSize: '3400px 420px', maskImage: `url(${staticFile('baked/trees-far.png')})`, maskSize: '3400px 420px'}} /> : null}</Layer> : null}
    {mid ? (
      <Layer p={0.55}>
        <div style={{position: 'absolute', left: -740, top: horizon + 22, width: 3400, height: 900, background: underlay ? `linear-gradient(${underlay[0]} 0, ${underlay[1]} 150px, ${underlay[2]} 380px)` : 'linear-gradient(#101a45 0, #213377 150px, #6b86c0 380px)'}} />
        {img('trees-mid.png', {left: -740 + treesDx * 1.4, top: horizon - 492, width: 3400, height: 520})}
        {tintTrees ? <div style={{position: 'absolute', left: -740, top: horizon - 492, width: 3400, height: 520, background: tintTrees, mixBlendMode: 'color', opacity: tintAmount, WebkitMaskImage: `url(${staticFile('baked/trees-mid.png')})`, WebkitMaskSize: '3400px 520px', maskImage: `url(${staticFile('baked/trees-mid.png')})`, maskSize: '3400px 520px'}} /> : null}
      </Layer>
    ) : null}
    {ground ? <Layer p={1}>
      {img(`${snow}.png`, {left: -740, top: horizon - 40, width: 3400, height: 700})}
      {spring
        ? (['spring-1', 'spring-2', 'spring-3'] as const).map((n, i) => (spring[i] > 0.005 ? <React.Fragment key={n}>{img(`${n}.png`, {left: -740, top: horizon - 40, width: 3400, height: 700, opacity: spring[i]})}</React.Fragment> : null))
        : null}
    </Layer> : null}
  </>
);

/** 前景两侧的深色树影（框） */
export const FrameTrees: React.FC<{p?: number; x?: number; k?: number; bottom?: number}> = ({p = 1.1, x = -60, k = 0.6, bottom = 1100}) => (
  <Layer p={p}>{img('trees-frame.png', {left: x, top: bottom - 1000 * k, width: 3000 * k, height: 1000 * k, WebkitMaskImage: 'linear-gradient(to bottom, #000 84%, transparent 99%)', maskImage: 'linear-gradient(to bottom, #000 84%, transparent 99%)'})}</Layer>
);

/** 整片的纸张纹理 + 四角压暗 */
export const PaperOverlay: React.FC = () => (
  <>
    <Img src={staticFile('baked/paper.jpg')} style={{position: 'absolute', left: 0, top: 0, width: W, height: H, mixBlendMode: 'overlay', opacity: 0.85}} />
  </>
);

export interface Hop { t0: number; t1: number; x0: number; x1: number; h: number }
/** 兔子的跳跃路径：每一跳是一条抛物线，其余时间蹲在原地。返回 x、离地高度、拉伸量、朝向 */
export const hopAt = (t: number, hops: Hop[], x0: number) => {
  let x = x0, lift = 0, stretch = 0, dir = 1, hopping = false;
  for (const h of hops) {
    if (t >= h.t1) { x = h.x1; dir = Math.sign(h.x1 - h.x0) || dir; continue; }
    if (t >= h.t0) {
      const u = (t - h.t0) / (h.t1 - h.t0);
      x = h.x0 + (h.x1 - h.x0) * u;
      lift = 4 * h.h * u * (1 - u);
      stretch = Math.sin(u * Math.PI) * 0.9;
      dir = Math.sign(h.x1 - h.x0) || dir;
      hopping = true;
    }
    break;
  }
  return {x, lift, stretch, dir, hopping};
};
/** 纸偶翻面：把 1/-1 的朝向做成中间经过 0 的平滑变化 */
export const turnScale = (t: number, flips: {at: number; to: 1 | -1}[], start: 1 | -1 = 1, dur = 0.5) => {
  let cur: number = start;
  for (const f of flips) {
    if (t < f.at) break;
    const u = ramp(t, f.at, f.at + dur);
    cur = lerp(cur, f.to, u);
    if (u >= 1) cur = f.to;
  }
  return cur;
};
