import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {GroundShadow, Footprints, BreathPuff, QuestionMark, Mound} from '../fx/Bits';
import {Backdrop, SceneWrap, FrameTrees, mountLamp, useT, ramp, hopAt, turnScale, at, GY, HZ} from './kit';

// 二、遇见问号：雪里两只长耳朵在动 → 跳出来 → 一串问题 → 一起上路
export const S2: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(960, 540, 1.0)},
    {t: 11, ...at(930, 550, 1.03)},
    {t: 13.2, ...at(760, 620, 1.2)},
    {t: 18.6, ...at(780, 620, 1.2)},
    {t: 21, ...at(1000, 570, 1.06)},
  ]);
  const MX = 1480, MB = HZ + 70, MK = 0.6;
  const lamp = mountLamp(MX, MB, MK);
  const bx = t < 7 ? 90 + 80 * t : t < 18.8 ? 90 + 80 * 7 : 650 + 70 * ramp(t, 18.8, 20.2) * (t - 18.8);
  const bw = t < 7 ? ramp(t, 0, 0.8) * (1 - ramp(t, 6.2, 7)) : ramp(t, 18.8, 19.8);
  const hops = [
    {t0: 4.6, t1: 5.5, x0: 1060, x1: 920, h: 90},
    {t0: 6.1, t1: 6.8, x0: 920, x1: 820, h: 50},
    {t0: 7.5, t1: 8.0, x0: 820, x1: 820, h: 46},
    {t0: 8.4, t1: 8.9, x0: 820, x1: 820, h: 46},
    {t0: 12.0, t1: 12.8, x0: 820, x1: 744, h: 56},
    ...[0, 1, 2, 3, 4].map((i) => ({t0: 19.2 + i * 0.55, t1: 19.7 + i * 0.55, x0: 744 + i * 24, x1: 768 + i * 24, h: 30})),
  ];
  const r = hopAt(t, hops, 1060);
  const hidden = t < 4.6;
  const rabbitY = hidden ? GY + 22 : GY - r.lift;
  const face = turnScale(t, [{at: 4.7, to: -1}, {at: 8.9, to: -1}, {at: 12.6, to: 1}], 1, 0.35);
  const q = (t0: number) => (t - t0) / 2.8;
  const landings = hops.filter((h) => h.t1 < t && h.h > 40).map((h) => h.x1);
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        <Backdrop mount={{cx: MX, k: MK, baseY: MB}} />
        <Layer p={0.16}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={lamp[0]} y={lamp[1]} r={6.5} />
          </svg>
        </Layer>
        <Layer p={1}>
          <svg width={2400} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <Footprints pts={Array.from({length: 24}, (_, i) => [100 + i * 56, GY + 8 + (i % 2) * 7] as [number, number]).filter(([x]) => x < bx - 30)} s={0.85} fade={0.25} />
            <Footprints pts={landings.flatMap((x) => [[x - 14, GY + 8], [x + 14, GY + 10]] as [number, number][])} s={0.4} fade={0.2} />
            <GroundShadow x={bx} y={GY + 6} rx={70} />
            <g transform={`translate(${bx} ${GY})`}>
              <Boy x={0} y={0} s={0.62} walk={bw} head={t > 7.2 && t < 18 ? 5 : 0} wind={0.5} />
            </g>
            <BreathPuff x={bx + 40} y={GY - 140} s={0.7} />
            {!hidden ? <GroundShadow x={r.x} y={GY + 6} rx={50} o={1 - r.lift / 140} /> : null}
            <g transform={`translate(${r.x} ${rabbitY}) scale(${face} 1)`}>
              <Rabbit x={0} y={0} s={0.64} perk={0.9} squash={r.stretch * 0.6} t0={1} />
            </g>
            {t < 6.4 ? <Mound x={1060} y={GY + 12} w={250} h={80} seed={2} /> : null}
            {[7.5, 8.1, 8.9, 9.7].map((t0, i) => (q(t0) >= 0 && q(t0) <= 1 ? <QuestionMark key={i} x={r.x - 40 + i * 28} y={GY - 170} s={1.7} age={q(t0)} rot={(i - 1.5) * 8} /> : null))}
          </svg>
        </Layer>
        <FrameTrees x={-40} k={0.5} />
      </Stage>
      <Snowfall horizon={HZ + 10} wind={0.15} />
    </SceneWrap>
  );
};
