import React from 'react';
import {Sprite, SpriteProps} from '../fx/Sprite';
import {Glow} from '../fx/Light';

type Common = Omit<SpriteProps, 'name' | 'layers'>;

export const Hazel: React.FC<Common & {view?: 'front' | 'side'}> = ({view = 'side', ...p}) => <Sprite name={`hazel_${view}`} {...p} />;

/**
 * Bud 的三种头饰（前后一致的关键，全片只在这里决定）：
 *   cap  — 棒球帽（第 1~2 章，之后给了雪人）
 *   hat  — 毛线帽（农场里得到的，戴在头上；Pebbles 爬进去之前）
 *   bare — 不戴帽子（第 2 章以后，以及 Pebbles 住进帽子以后的全程）
 * pocket：Pebbles 在毛线帽里，帽子装在 Bud 的口袋里（露出帽口和一张皱眉的小脸）
 */
export const Bud: React.FC<Common & {view?: 'front' | 'side'; head?: 'bare' | 'cap' | 'hat'; pocket?: boolean}> = ({view = 'side', head = 'bare', pocket = false, extra, ...p}) => {
  const base = `bud_${view}_bare`;
  const layers = head === 'bare' ? [base] : [base, head === 'cap' ? `bud_cap_${view}` : `bud_hat_${view}`];
  const pk = pocket ? [{name: 'pebbles_front', dx: view === 'front' ? 56 : 54, dy: -236, s: 0.55, clip: 0.34}] : [];
  return <Sprite name={base} layers={layers} extra={[...pk, ...(extra ?? [])]} {...p} />;
};

/** eyes: 0 = 熄灭（一动不动），1 = 亮着（黄色、亮亮的）；亮的时候眼睛处叠一团暖光。 */
export const Bolts: React.FC<Common & {view?: 'front' | 'side'; eyes?: number}> = ({view = 'front', eyes = 1, s = 0.7, children, ...p}) => {
  const on = `bolts_${view}`;
  const off = `bolts_${view}_off`;
  const eyePos = view === 'front' ? [[-24, -199], [25, -199]] : [[-42, -193]];
  return (
    <Sprite name={off} layers={[off, on]} lo={[1, eyes]} s={s} {...p}>
      {eyes > 0.02 && eyePos.map(([dx, dy], i) => <Glow key={i} x={dx * s} y={dy * s} r={44 * s * (0.8 + 0.3 * eyes)} opacity={0.75 * eyes} />)}
      {children}
    </Sprite>
  );
};

export const Comet: React.FC<Common & {view?: 'front' | 'side'}> = ({view = 'side', ...p}) => <Sprite name={`comet_${view}`} {...p} />;

/**
 * 一行人（Hazel、Bud、Bolts、Comet）：x 是 Hazel 的位置，face=1 朝右走、-1 朝左走。
 * Bolts 的侧面精灵原图朝左，朝右时翻转。偏移量保证每一镜的站位和队形一致。
 */
export const Party: React.FC<{
  x: number; y: number; face?: 1 | -1; walking?: boolean; t0?: number;
  bud?: {head?: 'bare' | 'cap' | 'hat'; pocket?: boolean; dx?: number; rot?: number; hide?: boolean};
  bolts?: {eyes?: number; dx?: number; hide?: boolean; view?: 'side' | 'front'};
  comet?: {dx?: number; hide?: boolean; rot?: number; y?: number} | false;
  hazel?: {hide?: boolean};
  s?: number;
}> = ({x, y, face = 1, walking = false, t0 = 0, bud = {}, bolts = {}, comet = false, hazel = {}, s = 0.72}) => {
  const f = face === -1;
  const w = walking ? 5 : 0;
  const bx = x - face * (bud.dx ?? 105);
  const ox = x - face * (bolts.dx ?? 200);
  const bview = bolts.view ?? 'side';
  return (
    <>
      {comet && !comet.hide ? <Comet x={x - face * (comet.dx ?? 330)} y={y - 2 + (comet.y ?? 0)} s={s} flip={f} walk={walking ? 6 : 0} rot={comet.rot} t0={t0 + 0.5} /> : null}
      {!bolts.hide ? <Bolts view={bview} x={ox} y={y + 8} s={s * 0.96} flip={bview === 'side' ? !f : f} eyes={bolts.eyes ?? 1} walk={walking ? 4 : 0} t0={t0 + 0.9} /> : null}
      {!bud.hide ? <Bud x={bx} y={y + 4} s={s * 0.945} flip={f} head={bud.head ?? 'bare'} pocket={bud.pocket ?? false} walk={w} rot={bud.rot} t0={t0 + 0.3} /> : null}
      {!hazel.hide ? <Hazel x={x} y={y} s={s} flip={f} walk={w} t0={t0} /> : null}
    </>
  );
};
