import React from 'react';
import {Stage, Layer, useCam} from '../fx/Stage';
import {Snow} from '../fx/Snow';
import {Sprite, GroundShadow} from '../fx/Sprite';
import {Hazel, Bud, Bolts, Comet} from './cast';
import {Bg, SceneWrap, Tint, useT, ramp, track, lerp, at, cuesOf} from './kit';

// 六、结冰的河：冰面"咔嚓"一声裂了，Bud 掉进黑黑冷冷的水里；Hazel 把梯子平推到冰上，用绳子拴住 Bud，Comet 一拉——Bud 被救上来，湿淋淋、发着抖
const C = cuesOf('s6-ice');
const HOLE = {x: 1430, y: 858};
const GY = 850;
const HS = 0.9;                  // 冰窟窿的缩放
const BS = 0.68;                 // Bud 缩放
const BH = 522 * BS;             // Bud 精灵高度

const ROPE = '#4b4440';

// 绳子：一条带点下垂的墨线
const Rope: React.FC<{x0: number; y0: number; x1: number; y1: number; o?: number; draw?: number; sag?: number}> = ({x0, y0, x1, y1, o = 1, draw = 1, sag = 24}) => {
  const mx = (x0 + x1) / 2, my = (y0 + y1) / 2 + sag * (1 - draw * 0.0);
  const ex = x0 + (x1 - x0) * draw, ey = y0 + (y1 - y0) * draw;
  return (
    <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0, opacity: o, pointerEvents: 'none'}}>
      <path d={`M ${x0} ${y0} Q ${(x0 + ex) / 2} ${(y0 + ey) / 2 + sag * draw} ${ex} ${ey}`} stroke={ROPE} strokeWidth={5} fill="none" strokeLinecap="round" />
      <path d={`M ${x0} ${y0 - 2} Q ${(x0 + ex) / 2} ${(y0 + ey) / 2 + sag * draw - 2} ${ex} ${ey - 2}`} stroke="#8c8480" strokeWidth={1.4} fill="none" strokeLinecap="round" opacity={0.6} />
    </svg>
  );
};

// 冰面的裂纹：从 Bud 脚下向四周长出来
const CRACKS = [
  [[0, 0], [-60, 14], [-130, 6], [-210, 26], [-300, 18]],
  [[0, 0], [70, -12], [150, 4], [230, -14], [330, 4]],
  [[0, 0], [-20, 40], [-70, 70], [-100, 110]],
  [[0, 0], [40, 30], [90, 60], [150, 70]],
  [[0, 0], [10, -40], [-30, -70], [-60, -100]],
  [[-130, 6], [-170, -26], [-230, -40]],
  [[150, 4], [200, 40], [270, 54]],
];
const Cracks: React.FC<{u: number; x: number; y: number}> = ({u, x, y}) => (
  <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
    {CRACKS.map((pts, i) => {
      const pth = pts.map(([px, py], k) => `${k ? 'L' : 'M'} ${x + px} ${y + py * 0.55}`).join(' ');
      return <path key={i} d={pth} stroke="#1d2a55" strokeWidth={3.2} fill="none" strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - u} opacity={0.75} />;
    })}
  </svg>
);

// 水花：几滴白点，抛物线飞起落下
const Splash: React.FC<{t: number; t0: number; x: number; y: number}> = ({t, t0, x, y}) => {
  const k = t - t0;
  if (k < 0 || k > 1.6) return null;
  return (
    <>
      {Array.from({length: 14}, (_, i) => {
        const a = (i / 14) * Math.PI - Math.PI;
        const vx = Math.cos(a) * (60 + (i % 4) * 22), vy = -150 - (i % 5) * 34;
        const px = x + vx * k * 0.9, py = y + vy * k + 260 * k * k;
        return <div key={i} style={{position: 'absolute', left: px, top: py, width: 9, height: 9, borderRadius: 9, background: '#eef5ff', opacity: Math.max(0, 1 - k / 1.6)}} />;
      })}
    </>
  );
};

export const S6: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const cam = useCam([
    {t: 0, ...at(1260, 580, 1.1)},
    {t: 3.0, ...at(1330, 620, 1.2)},
    {t: 5.0, ...at(1380, 660, 1.35)},
    {t: 10.0, ...at(1330, 660, 1.33)},
    {t: 13.5, ...at(1250, 650, 1.25)},
    {t: 17.0, ...at(1150, 650, 1.25)},
    {t: 20.4, ...at(900, 650, 1.32)},
    {t: len, ...at(860, 650, 1.35)},
  ]);

  // ── Bud ──
  const run = ramp(t, 0, 1.0);
  const sink = ramp(t, 2.3, 3.7);             // 0~1：掉进去
  const inWater = t >= 2.3 && t < 16.6;
  const hole = ramp(t, 2.2, 2.9);
  const c = 0.55 * sink;                       // 被水盖住的比例
  const budX = t < 2.3 ? lerp(1300, 1430, run) : HOLE.x;
  const bob = Math.sin(t * 2.2) * 3;
  const budY = inWater ? HOLE.y - 10 + c * BH + bob : GY;
  const lying = t >= 16.4 && t < 20.4;
  const pull = ramp(t, 17.2, 20.0);
  const lyingX = lerp(1580, 1020, pull);
  const standing = t >= 20.2;
  const shiver = standing ? Math.sin(t * 40) * 2.2 : 0;
  const wet = t >= 2.9;
  const wetFilter = wet ? 'brightness(0.8) saturate(0.8) hue-rotate(-6deg)' : undefined;

  // ── Hazel ──
  const onLadder = t >= 11.2 && t < 16.8;
  const hazelStand = t < 11.0 ? lerp(1020, 1130, ramp(t, 0, 1.2)) : 1130;
  const hazelLieX = track(t, [[11.4, 880], [14.6, 1060], [15.2, 1060], [16.7, 880]]);
  const hazelPull = t >= 16.8 && t < 20.2;
  const hazelBackStand = t >= 16.8;
  // ── 梯子、绳子 ──
  const ladderX = track(t, [[10.5, 700], [11.6, 1170]]);
  const ladderO = ramp(t, 10.3, 10.8);
  const ropeDraw = ramp(t, 13.0, 14.2);
  const cometX = t < 17.0 ? 860 : t < 20.2 ? lerp(860, 660, ramp(t, 17.2, 20.0)) : 640;
  const cometFace = t >= 16.6 ? -1 : 1;
  const lean = t >= 17.2 && t < 20.2 ? -9 : 0;
  const boltsX = 980;
  const ropeBudX = lying ? lyingX - 280 : HOLE.x - 30;
  const ropeBudY = lying ? GY + 10 : HOLE.y - 60 + c * BH * 0.4;

  return (
    <SceneWrap len={len} bg="#5a6c92">
      <Stage cam={cam}>
        <Layer p={0.6}><Bg src="ice_far.jpg" w={2900} h={1080} /></Layer>
        <Layer p={1}>
          <Bg src="ice_near.png" w={2900} h={1080} />
          {/* 裂纹 + 冰窟窿 */}
          <Cracks u={ramp(t, 1.0, 2.4)} x={t < 2.3 ? lerp(1300, 1430, run) : HOLE.x} y={HOLE.y + 6} />
          <Sprite name="ice_hole_back" x={HOLE.x} y={HOLE.y + 60 * HS * 0} s={HS} opacity={hole} breathe={0} sway={0} style={{marginTop: 0}} />
          {/* 站在冰上的角色（在窟窿后面的先画） */}
          <GroundShadow x={cometX} y={GY + 6} rx={90} />
          <Comet x={cometX} y={GY + 4} s={0.72} flip={cometFace === -1} rot={lean} walk={t > 17.2 && t < 20 ? 3 : 0} t0={0.5} />
          <GroundShadow x={boltsX} y={GY + 10} rx={60} />
          <Bolts view="side" x={boltsX} y={GY + 10} s={0.69} flip eyes={1} />
          {/* 梯子（平放在冰上，推过去） */}
          <Sprite name="ladder" x={ladderX} y={GY + 32} s={0.9} opacity={ladderO} breathe={0} sway={0} />
          {/* Hazel：站着 / 趴在梯子上爬 / 回到岸边 */}
          {hazelPull && <><GroundShadow x={930} y={GY} rx={85} /><Hazel x={930} y={GY} s={0.72} rot={-5} breathe={0.01} sway={0} /></>}
          {!onLadder && !hazelBackStand && <><GroundShadow x={hazelStand} y={GY} rx={85} /><Hazel x={hazelStand} y={GY} s={0.72} t0={0.3} walk={t < 1.2 ? 5 : 0} /></>}
          {onLadder && <Sprite name="hazel_side" x={hazelLieX} y={GY + 24} s={0.64} rot={90} breathe={0.004} sway={0.4} />}
          {/* Bud：跑过冰面 → 掉进窟窿（只露出上半身）→ 趴在梯子上被拉回 → 站在岸边发抖 */}
          {!lying && !standing && (
            <>
              {!inWater && <GroundShadow x={budX} y={GY} rx={80} />}
              <Bud view="front" x={budX} y={budY} s={BS} head="bare" pocket={!inWater} clipBottom={inWater ? c : 0} rot={inWater ? -3 + Math.sin(t * 1.7) * 2 : 0} walk={t < 1.0 ? 5 : 0} filter={wetFilter} t0={0.3} />
            </>
          )}
          {lying && <Sprite name="bud_side_bare" x={lyingX} y={GY + 22} s={BS} rot={-90} filter={wetFilter} opacity={ramp(t, 16.4, 16.9)} breathe={0.004} sway={0.3} />}
          {standing && (
            <>
              <GroundShadow x={800} y={GY + 4} rx={80} />
              <Bud view="front" x={800 + shiver} y={GY + 4} s={BS} head="bare" pocket filter={wetFilter} breathe={0.012} sway={0} />
              <GroundShadow x={690} y={GY} rx={85} />
              <Hazel view="front" x={690} y={GY} s={0.72} t0={0.3} />
            </>
          )}
          {/* 窟窿前沿（盖在 Bud 的腰上） */}
          <Sprite name="ice_hole_front" x={HOLE.x} y={HOLE.y + 4} s={HS} opacity={hole * (1 - ramp(t, 16.4, 16.9))} breathe={0} sway={0} />
          {inWater && <Splash t={t} t0={2.4} x={HOLE.x} y={HOLE.y - 40} />}
          {/* 绳子：Hazel 把它拴在 Bud 身上，另一头系在 Comet 身上 */}
          {t > 13.0 && t < 20.2 && <Rope x0={ropeBudX} y0={ropeBudY} x1={cometX + (cometFace === -1 ? -22 : 22)} y1={GY - 80} draw={ropeDraw} sag={14 + 20 * (1 - ramp(t, 17.2, 17.8))} />}
        </Layer>
      </Stage>
      <Tint color="#9fb0d8" o={0.32} />
      <Snow amount={0.85} wind={0.18} />
    </SceneWrap>
  );
};
