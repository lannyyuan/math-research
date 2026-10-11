import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {W, H} from '../palette';
import timeline from '../timeline.json';
import {schedule} from '../schedule.mjs';
import manifest from '../../public/bg/manifest.json';
import {useVariant} from '../fx/Variant';

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

/** 角色站在地面 y=gy（世界坐标）；镜头缩放 z 时，让脚底落在屏幕 y=fy（默认 820，字幕带的上沿是 845）：字幕带里不压角色 */
export const atg = (wx: number, z = 1, gy = 832, fy = 820) => at(wx, gy - (fy - H / 2) / z, z);

/** 场景外壳：开头结尾各有一小段缓缓的“墨色”过渡（没有闪白、没有硬切） */
export const SceneWrap: React.FC<{len: number; children: React.ReactNode; bg?: string; fadeIn?: number; fadeOut?: number}> = ({len, children, bg = '#0c1222', fadeIn = 20, fadeOut = 24}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const o = interpolate(f, [0, fadeIn, len * fps - fadeOut, len * fps - 1], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: bg}}>
      <div style={{position: 'absolute', inset: 0, opacity: o}}>{children}</div>
    </AbsoluteFill>
  );
};

type PlateInfo = {variants: string[]; ext: string; w: number; h: number};
const MF = manifest as unknown as Record<string, PlateInfo>;
export const plateInfo = (name: string) => MF[name];

/** 摆一张烘焙好的背景层（世界坐标）。按当前光照版本选文件；该版本不存在就用夜色版。w/h 默认取画布的实际尺寸。 */
export const Bg: React.FC<{name: string; x?: number; y?: number; w?: number; h?: number; opacity?: number; style?: React.CSSProperties; variant?: string}> = ({name, x = 0, y = 0, w, h, opacity = 1, style, variant}) => {
  const cur = useVariant();
  const info = MF[name];
  if (!info) return null;
  const v0 = variant ?? cur;
  const v = info.variants.includes(v0) ? v0 : info.variants.includes('night') ? 'night' : info.variants[0];
  return <Img src={staticFile(`bg/${name}_${v}.${info.ext}`)} style={{position: 'absolute', left: x, top: y, width: w ?? info.w, height: h ?? info.h, opacity, ...style}} />;
};

/** 整片的宣纸纹理（overlay）+ 四周轻轻压暗 */
export const PaperOverlay: React.FC = () => (
  <>
    <Img src={staticFile('bg/paper.jpg')} style={{position: 'absolute', left: 0, top: 0, width: W, height: H, mixBlendMode: 'soft-light', opacity: 0.9}} />
    <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 62%, rgba(10,12,24,0.30) 100%)', pointerEvents: 'none'}} />
  </>
);

/** 本场景里每条字幕的出现时间（场景内秒数）：动作和字幕按这个对齐 */
export const cuesOf = (id: string) => {
  const sc = (timeline as any).scenes.find((s: any) => s.id === id)!;
  return schedule(sc as any);
};

/** 场景里的一个“镜头”：from~to 秒之间可见，两头各用 fade 秒溶进溶出（慢叠化） */
export const Shot: React.FC<{from?: number; to?: number; fade?: number; children: React.ReactNode}> = ({from = 0, to = 999, fade = 1.0, children}) => {
  const t = useT();
  const o = (from <= 0 ? 1 : ramp(t, from - fade * 0.5, from + fade * 0.5)) * (to >= 900 ? 1 : 1 - ramp(t, to - fade * 0.5, to + fade * 0.5));
  if (o <= 0.001) return null;
  return <div style={{position: 'absolute', inset: 0, opacity: o}}>{children}</div>;
};

/** 一整片的颜色罩；mix-blend multiply */
export const Tint: React.FC<{color: string; o: number; blend?: React.CSSProperties['mixBlendMode']}> = ({color, o, blend = 'multiply'}) => (
  <div style={{position: 'absolute', inset: 0, background: color, opacity: o, mixBlendMode: blend, pointerEvents: 'none'}} />
);

/** 分段插值：keys = [[秒, 值], ...]，段与段之间缓入缓出，头尾保持不动。 */
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
