import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import timeline from '../timeline.json';
import {schedule, sceneStarts, wrap} from '../schedule.mjs';
import {W, CREAM} from '../palette';
import './fonts';

// 字幕：只取故事原文里的句子。字大、停留时间按“刚学会读”的速度算（见 schedule.mjs / check-subtitles.mjs）
const starts = sceneStarts(timeline);
export const CUES = timeline.scenes.flatMap((sc, i) => schedule(sc).map((c: any) => ({...c, t: starts[i] + c.t})));

export const Subtitle: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const cue = CUES.find((c) => t >= c.t - 0.01 && t < c.t + c.d);
  if (!cue) return null;
  const o = interpolate(t, [cue.t, cue.t + 0.35, cue.t + cue.d - 0.35, cue.t + cue.d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lines = wrap(cue.text);
  const two = lines.length > 1;
  return (
    <div style={{position: 'absolute', left: 0, bottom: two ? 44 : 64, width: W, display: 'flex', justifyContent: 'center', opacity: o, transform: `translateY(${(1 - o) * 8}px)`}}>
      <div
        style={{
          fontFamily: 'AndikaSub, "Andika", sans-serif',
          fontWeight: 400,
          fontSize: two ? 60 : 68,
          lineHeight: 1.28,
          letterSpacing: 0.6,
          color: CREAM,
          textAlign: 'center',
          padding: '14px 46px 18px',
          maxWidth: 1620,
          background: 'rgba(14,24,58,0.80)',
          borderRadius: '34px 28px 36px 26px / 28px 36px 26px 32px',
          boxShadow: '0 0 0 2px rgba(190,205,240,0.16), 0 8px 30px rgba(6,10,30,0.35)',
          textShadow: '0 2px 6px rgba(5,8,28,0.6)',
          whiteSpace: 'nowrap',
        }}
      >
        {lines.map((l: string, i: number) => (
          <div key={i}>{l}</div>
        ))}
      </div>
    </div>
  );
};
