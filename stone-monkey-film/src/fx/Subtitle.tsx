import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from '../timeline.json';
import {schedule, sceneStarts, wrap} from '../schedule.mjs';
import {W} from '../palette';
import './fonts';

// 字幕：只取原文里的句子；底部居中，半透明的墨色底带；字大。停留时间见 schedule.mjs / check-subtitles.mjs
const starts = sceneStarts(timeline as any);
export const CUES = (timeline as any).scenes.flatMap((sc: any, i: number) => schedule(sc).map((c: any) => ({...c, t: starts[i] + c.t, scene: sc.id})));

export const Subtitle: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const cue = CUES.find((c: any) => t >= c.t - 0.01 && t < c.t + c.d);
  if (!cue) return null;
  const o = interpolate(t, [cue.t, cue.t + 0.4, cue.t + cue.d - 0.4, cue.t + cue.d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lines = wrap(cue.text);
  const two = lines.length > 1;
  const size = 62, lh = 1.34;
  const bandH = (two ? 2 : 1) * size * lh + 54;
  return (
    <div style={{position: 'absolute', left: 0, bottom: 0, width: W, height: bandH + 16, opacity: o}}>
      {/* 半透明的墨色底带：上沿渐隐，像一笔淡墨 */}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: bandH + 16, background: 'linear-gradient(to top, rgba(28,24,24,0.74) 0%, rgba(28,24,24,0.70) 78%, rgba(28,24,24,0) 100%)'}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 28, display: 'flex', justifyContent: 'center'}}>
        <div style={{fontFamily: 'WenKaiSub, "LXGW WenKai", serif', fontSize: size, lineHeight: lh, letterSpacing: 6, color: '#f6efdc', textAlign: 'center', textShadow: '0 2px 8px rgba(10,8,8,0.7)', whiteSpace: 'nowrap'}}>
          {lines.map((l: string, i: number) => <div key={i}>{l}</div>)}
        </div>
      </div>
    </div>
  );
};
