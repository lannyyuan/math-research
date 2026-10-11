import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {W, H} from '../palette';
import timeline from '../timeline.json';
import {schedule} from '../schedule.mjs';

export const useT = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return f / fps;
};
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const ramp = (t: number, a: number, b: number) => {
  const u = clamp01((t - a) / (b - a));
  return u * u * (3 - 2 * u);
};
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
/** 镜头对准世界坐标 (wx, wy)，缩放 z（世界坐标 = 1920×1080 的画面坐标系，起始镜头中心在 (960, 540)） */
export const at = (wx: number, wy: number, z = 1) => ({x: wx - W / 2, y: wy - H / 2, z});

/** 场景外壳：开头结尾各有一小段缓缓的明暗过渡（没有快切、没有花哨转场） */
export const SceneWrap: React.FC<{len: number; children: React.ReactNode; bg?: string; fadeIn?: number; fadeOut?: number}> = ({len, children, bg = '#0a1230', fadeIn = 24, fadeOut = 30}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const o = interpolate(f, [0, fadeIn, len * fps - fadeOut, len * fps - 1], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: bg}}>
      <div style={{position: 'absolute', inset: 0, opacity: o}}>{children}</div>
    </AbsoluteFill>
  );
};

/** 摆一张烘焙好的背景图（世界坐标），w/h 是它在画面里的大小 */
export const Bg: React.FC<{src: string; x?: number; y?: number; w: number; h: number; opacity?: number; style?: React.CSSProperties}> = ({src, x = 0, y = 0, w, h, opacity = 1, style}) => (
  <Img src={staticFile(`bg/${src}`)} style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity, ...style}} />
);

/** 整片的纸张纹理（overlay）+ 四周轻轻压暗 */
export const PaperOverlay: React.FC = () => (
  <>
    <Img src={staticFile('bg/paper.jpg')} style={{position: 'absolute', left: 0, top: 0, width: W, height: H, mixBlendMode: 'overlay', opacity: 0.8}} />
    <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 58%, rgba(6,10,30,0.28) 100%)', pointerEvents: 'none'}} />
  </>
);

/** 本场景里每条字幕的出现时间（场景内秒数）：动作和字幕按这个对齐 */
export const cuesOf = (id: string) => {
  const sc = timeline.scenes.find((s) => s.id === id)!;
  return schedule(sc as any);
};

/** 场景里的一个“镜头”：from~to 秒之间可见，两头各用 fade 秒溶进溶出（没有快切、没有花哨转场，只是慢慢的叠化） */
export const Shot: React.FC<{from?: number; to?: number; fade?: number; children: React.ReactNode}> = ({from = 0, to = 999, fade = 1.0, children}) => {
  const t = useT();
  const o = (from <= 0 ? 1 : ramp(t, from - fade * 0.5, from + fade * 0.5)) * (to >= 900 ? 1 : 1 - ramp(t, to - fade * 0.5, to + fade * 0.5));
  if (o <= 0.001) return null;
  return <div style={{position: 'absolute', inset: 0, opacity: o}}>{children}</div>;
};

/** 一整片的颜色罩（暮色 / 暴风雪的夜）；mix-blend multiply 让雪变成蓝灰而不是整体发灰 */
export const Tint: React.FC<{color: string; o: number; blend?: React.CSSProperties['mixBlendMode']}> = ({color, o, blend = 'multiply'}) => (
  <div style={{position: 'absolute', inset: 0, background: color, opacity: o, mixBlendMode: blend, pointerEvents: 'none'}} />
);

/** 牌子上的字（贴在世界坐标里的纸牌上）：站牌 / 车站的告示，字是故事里的原句 */
export const SignText: React.FC<{x: number; y: number; w: number; h: number; lines: string[]; size?: number; o?: number}> = ({x, y, w, h, lines, size = 38, o = 1}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', fontFamily: 'AndikaSub, Andika, sans-serif', fontWeight: 700, fontSize: size, lineHeight: 1.18, color: '#1d2447', textAlign: 'center', opacity: o, letterSpacing: 1}}>
    {lines.map((l, i) => <div key={i}>{l}</div>)}
  </div>
);

/** 分段插值：keys = [[秒, 值], ...]，段与段之间用缓入缓出，头尾保持不动。动作按字幕时间对齐时用。 */
export const track = (t: number, keys: [number, number][]) => {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [t0, v0] = keys[i - 1];
      const [t1, v1] = keys[i];
      return v0 + (v1 - v0) * ramp(t, t0, t1);
    }
  }
  return keys[keys.length - 1][1];
};
