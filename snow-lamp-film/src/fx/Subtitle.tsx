import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from '../timeline.json';
import {schedule, sceneStarts} from '../schedule.mjs';
import {W} from '../palette';

// 字幕：只取原文里的句子。字大，停留时间按识字速度算（见 schedule.mjs / check-subtitles.mjs）
const starts = sceneStarts(timeline);
export const CUES = timeline.scenes.flatMap((sc, i) => schedule(sc).map((c) => ({...c, t: starts[i] + c.t})));

export const Subtitle: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const cue = CUES.find((c) => t >= c.t - 0.01 && t < c.t + c.d);
  if (!cue) return null;
  const o = interpolate(t, [cue.t, cue.t + 0.35, cue.t + cue.d - 0.35, cue.t + cue.d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lines = cue.text.split('\n');
  const two = lines.length > 1;
  return (
    <div style={{position: 'absolute', left: 0, bottom: two ? 50 : 74, width: W, display: 'flex', justifyContent: 'center', opacity: o, transform: `translateY(${(1 - o) * 8}px)`}}>
      <div
        style={{
          fontFamily: 'WenKaiSub, "LXGW WenKai", serif',
          fontSize: two ? 64 : 76,
          lineHeight: 1.32,
          letterSpacing: 5,
          color: '#f7f9ff',
          textAlign: 'center',
          padding: '16px 50px 20px',
          maxWidth: 1560,
          background: 'rgba(12,20,52,0.78)',
          borderRadius: '38px 30px 40px 28px / 30px 40px 28px 36px',
          boxShadow: '0 0 0 2px rgba(190,205,240,0.16), 0 8px 30px rgba(6,10,30,0.35)',
          textShadow: '0 2px 6px rgba(5,8,28,0.6)',
          whiteSpace: 'nowrap',
        }}
      >
        {lines.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>
    </div>
  );
};
