import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art, rng, type P} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {petal} from '../art/geom';
import {C} from '../palette';

// 白鹿：巨大、温柔。鹿角是两棵小树；耳朵大而圆，尾巴短短上翘；不是马，也没有翅膀。
// 朝右，脚底在 (0,0)；站立时肩高约 345，鹿角顶约 740。
interface Br { pts: P[]; w: number }
/** 把鹿角长成一棵小树：主干 → 分枝 → 小枝 */
function antlerTree(seed: number, origin: P, ang: number, len: number, w: number, depth = 3): {br: Br[]; tips: P[]} {
  const rnd = rng(seed);
  const br: Br[] = [];
  const tips: P[] = [];
  const grow = (p: P, a: number, L: number, ww: number, d: number, bend: number) => {
    const steps = 4;
    const pts: P[] = [p];
    let cur = p, aa = a;
    for (let i = 1; i <= steps; i++) {
      aa += bend + (rnd() - 0.5) * 0.18;
      cur = [cur[0] + (Math.cos(aa) * L) / steps, cur[1] + (Math.sin(aa) * L) / steps];
      pts.push(cur);
    }
    br.push({pts, w: ww});
    if (d > 0) {
      for (const t of d === depth ? [0.36, 0.68] : [0.55]) {
        const idx = Math.round(t * steps);
        const base = pts[idx];
        for (const sgn of [-1, 1]) {
          if (d === depth && t > 0.6 && sgn > 0 && rnd() < 0.25) continue;
          grow(base, aa + sgn * (0.55 + rnd() * 0.3), L * (0.66 - t * 0.14), ww * 0.62, d - 1, sgn * -0.05);
        }
      }
    } else tips.push(cur);
    if (d > 0) tips.push(cur);
  };
  grow(origin, ang, len, w, depth, 0.04);
  return {br, tips};
}

const build = () => {
  // 躯干：身体 + 脖子连成一个轮廓（只填色，墨线单独画开放线，肩颈处不出现分隔线）
  const body = new Art(51);
  body.fill([[84, -338], [20, -350], [-60, -346], [-126, -330], [-170, -300], [-184, -250], [-162, -204], [-110, -182], [-40, -172], [40, -174], [100, -194], [134, -250], [124, -306]], C.fur);
  body.shade([[-170, -214], [-110, -184], [-40, -176], [40, -178], [100, -198], [64, -216], [-40, -218], [-130, -228]], 0.36);
  body.shade([[-184, -252], [-172, -300], [-140, -326], [-160, -276]], 0.22);
  body.guide(52, -262, 72, 86, 0.1);
  body.guide(-120, -256, 76, 84, -0.1);
  body.line([[-184, -250], [-178, -296], [-136, -330], [-60, -346], [20, -350], [84, -338]], {w: 3.6, sk: 2, wobble: 1.8, taper: 0.5});
  body.line([[-184, -250], [-168, -206], [-112, -182], [-40, -172], [40, -174], [100, -194], [134, -250]], {w: 3.4, sk: 1, wobble: 1.6, taper: 0.5});
  body.line([[-26, -250], [-6, -236], [18, -250]], {w: 1.2, taper: 0.9, broken: 0.3});
  const tail = new Art(52);
  tail.shape(petal([-176, -276], [-212, -314], 28, 6), C.fur, {w: 2.6, sk: 1});

  // 脖子 + 颈毛（以肩为轴，可以低头）
  const neck = new Art(53);
  neck.fill([[60, -332], [100, -374], [136, -424], [170, -470], [206, -498], [244, -456], [222, -410], [194, -368], [170, -326], [152, -292], [140, -256], [100, -290]], C.fur);
  neck.shade([[244, -456], [222, -410], [194, -368], [170, -326], [152, -292], [140, -256], [166, -290], [196, -336], [222, -392]], 0.34);
  neck.line([[80, -346], [106, -380], [138, -428], [172, -470], [206, -498]], {w: 3.4, sk: 1, wobble: 1.4, taper: 0.5});
  const throat: P[] = [[240, -456], [222, -410], [194, -368], [170, -326], [152, -292], [140, -256]];
  neck.line(throat, {w: 2.8, wobble: 1.2, taper: 0.6});
  const ruff: P[] = [[236, -440], [222, -420], [232, -404], [208, -394], [218, -372], [192, -362], [200, -340], [174, -330], [180, -308], [154, -298], [160, -276], [138, -268]];
  neck.line(ruff, {w: 2, taper: 0.5});
  neck.shade([[236, -440], [208, -394], [192, -362], [174, -330], [154, -298], [138, -268], [150, -310], [182, -360]], 0.2);

  // 头
  const head = new Art(54);
  head.shape([[212, -490], [250, -506], [284, -492], [314, -460], [332, -434], [336, -416], [322, -404], [292, -402], [262, -414], [232, -430], [212, -456]], C.fur, {w: 3.2, sk: 1, wobble: 1.4});
  head.shade([[232, -430], [262, -414], [292, -404], [320, -406], [296, -420], [262, -426]], 0.34);
  head.guide(268, -454, 58, 52, 0.4);
  head.shape([[324, -422], [338, -420], [338, -408], [326, -406]], '#34406e', {w: 1.6});
  head.line([[318, -410], [292, -410], [272, -420]], {w: 1.7, taper: 0.8});
  head.fill([[264, -452], [280, -456], [288, -442], [272, -438]], C.ink, 1);
  head.fill([[271, -452], [276, -453], [277, -447], [272, -447]], '#ffffff', 0.9);
  head.line([[260, -458], [278, -464], [294, -452]], {w: 2, taper: 0.9});
  head.line([[260, -458], [254, -462]], {w: 1.4, taper: 0.5}).line([[265, -461], [261, -468]], {w: 1.4, taper: 0.5});
  head.shade([[272, -436], [294, -434], [298, -418], [278, -420]], 0.26, C.nosePink);
  const earN = new Art(55);
  earN.shape(petal([232, -494], [172, -532], 50, 9), C.fur, {w: 2.8, sk: 1});
  earN.shade(petal([228, -496], [184, -524], 26, 7), 0.42, C.nosePink);
  const earF = new Art(56);
  earF.shape(petal([254, -502], [276, -568], 44, -7), C.fur, {w: 2.6});
  earF.shade(petal([256, -506], [274, -556], 22, -5), 0.42, C.nosePink);

  // 鹿角：两棵小树（近的深些、粗些；远的淡些）
  const mkAntler = (seed: number, origin: P, ang: number, len: number, w: number, ghost: boolean) => {
    const a = new Art(seed);
    const {br, tips} = antlerTree(seed, origin, ang, len, w, 2);
    for (const b of br) {
      a.wash(b.pts, b.w * 2.4, C.antlerWash, ghost ? 0.7 : 0.95);
      a.line(b.pts, {w: Math.max(1.2, b.w * 0.55), taper: 0.5, broken: 0.05, sk: 0});
    }
    for (const t of tips) a.fill([[t[0] - 5, t[1] + 1], [t[0], t[1] - 7], [t[0] + 5, t[1] + 1], [t[0], t[1] + 5]], '#fbfdff', 0.95);
    return {a, tips};
  };
  const aN = mkAntler(57, [244, -500], -Math.PI / 2 - 0.12, 120, 6, false);
  const aF = mkAntler(58, [272, -500], -Math.PI / 2 + 0.1, 110, 5, true);
  const leaves = new Art(59);
  for (const t of [...aN.tips, ...aF.tips]) {
    leaves.shape(petal([t[0], t[1] + 2], [t[0] - 15, t[1] - 18], 12, 3), C.grass, {w: 1.1, opacity: 0.95});
    leaves.shape(petal([t[0], t[1] + 2], [t[0] + 15, t[1] - 16], 12, -3), C.moss, {w: 1.1, opacity: 0.95});
  }

  // 趴下时折在胸前的前腿
  const fold = new Art(64);
  fold.shape([[34, -52], [112, -50], [148, -36], [154, -14], [130, -4], [46, -6], [20, -24]], C.fur, {w: 2.8, sk: 1});
  fold.shade([[30, -22], [46, -8], [130, -6], [152, -16], [100, -26]], 0.34);
  fold.shape([[134, -22], [156, -20], [158, -4], [134, -4]], '#34406e', {w: 1.6});
  // 腿：细长，鹿蹄是深蓝灰
  const leg = (seed: number, pts: P[], hoof: P[], color: string, w: number) => {
    const a = new Art(seed);
    a.shape(pts, color, {w, sk: 0});
    a.shape(hoof, '#34406e', {w: 1.6});
    return a.build();
  };
  const foreN = leg(60, [[66, -214], [108, -214], [102, -134], [98, -80], [102, -22], [108, 0], [84, 0], [88, -22], [88, -80], [86, -134]], [[84, -16], [108, -16], [110, 0], [84, 0]], C.fur, 3);
  const foreF = leg(61, [[104, -212], [144, -212], [138, -134], [134, -80], [138, -22], [144, 0], [120, 0], [122, -22], [122, -80], [120, -134]], [[120, -16], [144, -16], [146, 0], [120, 0]], C.snowShade, 2.4);
  const hindN = leg(62, [[-172, -230], [-112, -230], [-100, -170], [-112, -118], [-104, -78], [-98, -22], [-94, 0], [-120, 0], [-120, -22], [-128, -78], [-150, -118], [-158, -170]], [[-120, -16], [-94, -16], [-92, 0], [-120, 0]], C.fur, 3);
  const hindF = leg(63, [[-130, -228], [-80, -228], [-68, -170], [-80, -118], [-72, -78], [-66, -22], [-62, 0], [-88, 0], [-88, -22], [-96, -78], [-116, -118], [-124, -170]], [[-88, -16], [-62, -16], [-60, 0], [-88, 0]], C.snowShade, 2.4);
  return {
    body: body.build(), tail: tail.build(), neck: neck.build(), head: head.build(), earN: earN.build(), earF: earF.build(),
    antlerN: aN.a.build(), antlerF: aF.a.build(), leaves: leaves.build(), foreN, foreF, hindN, hindF, fold: fold.build(),
  };
};

const ramp01 = (x: number) => Math.max(0, Math.min(1, x));
export interface DeerProps {
  x?: number; y?: number; s?: number; flip?: boolean;
  walk?: number; // 0~1 走路幅度
  headDown?: number; // 0~1 低头（以肩为轴）
  leaves?: number; // 0~1 鹿角发新叶
  t0?: number;
  tilt?: number;
  lie?: number; // 0~1 趴下（腿折起，身体落到地上）
  kneel?: number; // 0~1 前腿跪下、身体前倾（像鞠躬）
  children?: React.ReactNode; // 搭在鹿背上的东西（局部坐标）
}
export const Deer: React.FC<DeerProps> = ({x = 0, y = 0, s = 1, flip = false, walk = 0, headDown = 0, leaves = 0, t0 = 0, tilt = 0, lie = 0, kneel = 0, children}) => {
  const A = useMemo(build, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const ph = t * 2 * Math.PI * 0.75;
  const sw = Math.sin(ph) * 15 * walk;
  const breathe = 1 + Math.sin(t * 1.5) * 0.008;
  const bob = -Math.abs(Math.sin(ph)) * 4 * walk;
  const ear = Math.sin(t * 1.9) * 3 + Math.sin(t * 0.6) * 4;
  const kLeg = 1 - 0.7 * lie; // 腿折起后的长度比例
  const drop = 210 * (1 - kLeg);
  const kFore = kLeg * (1 - 0.42 * kneel);
  const bow = kneel * 15; // 前倾
  const legT = (hx: number, hy: number, k: number, rot: number) => `translate(0 ${210 * (1 - kLeg)}) translate(${hx} ${hy}) rotate(${rot}) scale(1 ${k}) translate(${-hx} ${-hy})`;
  return (
    <g transform={`translate(${x} ${y + bob}) scale(${flip ? -s : s} ${s}) rotate(${tilt})`}>
      <g transform={legT(-100, -224, kLeg, -sw)}><ArtView a={A.hindF} filter="wc2" /></g>
      <g transform={`rotate(${bow} -120 0) ${legT(124, -212, kFore, sw)}`}><ArtView a={A.foreF} filter="wc2" /></g>
      <g transform={`rotate(${bow} -120 0) translate(0 ${drop})`}>
        <g transform={`scale(1 ${breathe})`}>
          <ArtView a={A.tail} filter="wc1" />
          <ArtView a={A.body} filter="wc0" />
          {children}
          <g transform={`rotate(${headDown * 52} 96 -300)`}>
            <g transform="translate(206 -492) scale(1.16) translate(-206 492)">
              <ArtView a={A.antlerF} filter="wc1" sk={0.3} />
              <g transform={`rotate(${ear * 0.6} 254 -502)`}><ArtView a={A.earF} filter="wc1" /></g>
            </g>
            <ArtView a={A.neck} filter="wc0" />
            <g transform="translate(206 -492) scale(1.16) translate(-206 492)">
              <ArtView a={A.head} filter="wc2" />
              <ArtView a={A.antlerN} filter="wc1" />
              {leaves > 0.02 ? (
                <g opacity={leaves} transform={`scale(${0.3 + leaves * 0.7})`} style={{transformOrigin: '244px -640px'}}>
                  <ArtView a={A.leaves} filter="wc1" sk={0} />
                </g>
              ) : null}
              <g transform={`rotate(${ear} 232 -494)`}><ArtView a={A.earN} filter="wc1" /></g>
            </g>
          </g>
        </g>
      </g>
      {lie > 0.5 ? <g opacity={ramp01((lie - 0.5) * 2)}><ArtView a={A.fold} filter="wc1" /></g> : null}
      <g transform={legT(-120, -226, kLeg, sw)}><ArtView a={A.hindN} filter="wc1" /></g>
      <g transform={`rotate(${bow} -120 0) ${legT(88, -212, kFore, -sw)}`}><ArtView a={A.foreN} filter="wc1" /></g>
    </g>
  );
};
