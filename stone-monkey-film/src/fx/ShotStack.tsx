import React from 'react';
import {InkIn} from './InkIn';
import {ramp, useT} from '../scenes/kit';

export interface ShotDef {from: number; map?: 'a' | 'b' | 'c' | 'd'; wipe?: number; el: React.ReactNode}

/**
 * 一个场景里的镜头序列：第 i 个镜头在 from 秒起用水墨晕染（InkIn）盖到前一个镜头上；盖严之后，前一个镜头就不再渲染（省时间）。
 * 每个镜头自己用 useT()（场景内秒数）和 useCam。
 */
export const ShotStack: React.FC<{shots: ShotDef[]}> = ({shots}) => {
  const t = useT();
  return (
    <>
      {shots.map((s, i) => {
        const wipe = s.wipe ?? 1.9;
        const next = shots[i + 1]?.from ?? 1e9;
        const nextWipe = shots[i + 1]?.wipe ?? 1.9;
        if (t < s.from - 0.02 || t > next + nextWipe + 0.1) return null;
        const p = i === 0 ? 1 : ramp(t, s.from, s.from + wipe);
        return <InkIn key={i} p={p} map={s.map ?? 'a'}>{s.el}</InkIn>;
      })}
    </>
  );
};
