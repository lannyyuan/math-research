import React, {useMemo} from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Defs, ArtView} from '../art/ArtView';
import {Art, rng, type P} from '../art/ink';
import {Stage, Layer} from '../fx/Stage';
import {Snowfall} from '../fx/Snowfall';
import {LampGlow} from '../fx/Lamp';
import {Fire} from '../fx/Fire';
import {GroundShadow, QuestionMark} from '../fx/Bits';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {Turtle, TurtleHead} from '../chars/Turtle';
import {Backdrop, FrameTrees, PaperOverlay, mountLamp} from '../scenes/kit';
import {C, W, H} from '../palette';
import '../fx/fonts';

// 绘本网页用的“补充插图”：影片里没有出现、但原文里有的章节（影子、问号的问题、农夫伯伯的小院、雪人、
// 古城墙、学校、大海、星星、白鹿的心事、森林里的比赛）。同一套画笔、同一套角色，只是换了场景。
// 渲染：node scripts/stills.mjs Plate:0@'{"which":"snowman"}' --scale=1 --out=out/book_plates

const CAM = {x: 0, y: 0, z: 1};
const SIL = '#121a45';
const SILD = '#0a1030';
/** 把多边形的每条边加密，水彩的平滑曲线才不会把直角抹圆（房子、墙需要直角） */
const dense = (pts: P[], step = 30): P[] => {
  const out: P[] = [];
  pts.forEach((a, i) => {
    const b = pts[(i + 1) % pts.length];
    const n = Math.max(1, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / step));
    for (let k = 0; k < n; k++) out.push([a[0] + ((b[0] - a[0]) * k) / n, a[1] + ((b[1] - a[1]) * k) / n]);
  });
  return out;
};

/** 一幅插图的外壳：天空/远林/雪地 + 内容 + 飘雪 + 纸纹。mount=山顶那盏灯（画面里始终有一点光） */
const Wrap: React.FC<{
  children: React.ReactNode;
  dawn?: number;
  horizon?: number;
  mount?: {cx: number; k: number; baseY?: number} | false;
  tint?: string; // 整体罩一层（multiply）
  dark?: number;
  snow?: number;
  snowWind?: number;
  frame?: {p?: number; x?: number; k?: number; bottom?: number} | false;
  under?: React.ReactNode; // 画在角色之下、地面之上（影子、脚印等）
  skyExtra?: React.ReactNode;
}> = ({children, dawn = 0, horizon = 560, mount, tint, dark = 0, snow = 1, snowWind = 0.05, frame = {}, under, skyExtra}) => {
  const m = mount === undefined ? {cx: 1500, k: 0.46, baseY: horizon + 20} : mount;
  const lamp = m ? mountLamp(m.cx, m.baseY ?? horizon + 20, m.k) : null;
  return (
    <AbsoluteFill style={{background: '#050a22'}}>
      <Defs />
      <Stage cam={CAM}>
        <Backdrop horizon={horizon} dawn={dawn} mount={m ? {cx: m.cx, k: m.k, baseY: m.baseY ?? horizon + 20} : false} mountFade far mid />
        {skyExtra}
        {tint ? <div style={{position: 'absolute', inset: 0, background: tint, mixBlendMode: 'multiply'}} /> : null}
        {lamp ? (
          <Layer p={0.16}>
            <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
              <LampGlow x={lamp[0]} y={lamp[1]} r={5} glow={dawn > 0.5 ? 0.6 : 1} />
            </svg>
          </Layer>
        ) : null}
        <Layer p={1}>
          <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>
            {under}
            {children}
          </svg>
          <div style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
            <Snowfall amount={snow} wind={snowWind} horizon={horizon + 60} />
          </div>
        </Layer>
        {frame === false ? null : <FrameTrees {...{p: 1.1, x: -60, k: 0.66, bottom: 1120, ...frame}} />}
      </Stage>
      {dark > 0 ? <div style={{position: 'absolute', inset: 0, background: `rgba(4,7,26,${dark})`}} /> : null}
      <PaperOverlay />
    </AbsoluteFill>
  );
};

const flat = (a: Art) => <ArtView a={a.build()} filter="wc0" sk={0} />;

/* ───────────── 小道具：动物剪影 ───────────── */
const critter = (kind: 'owl' | 'crow' | 'squirrel' | 'fox', seed: number) => {
  const a = new Art(seed);
  const o = {w: 2.2, taper: 0.4, sk: 0} as const;
  if (kind === 'owl') {
    a.shape([[-34, -70], [-28, -98], [-14, -84], [0, -88], [14, -84], [28, -98], [34, -70], [40, -30], [34, 10], [16, 34], [0, 38], [-16, 34], [-34, 10], [-40, -30]], SIL, o);
    a.line([[-16, 36], [-18, 52]], {w: 3}).line([[16, 36], [18, 52]], {w: 3});
  } else if (kind === 'crow') {
    a.shape([[-60, -18], [-40, -38], [-8, -44], [18, -36], [30, -20], [20, -4], [-10, 6], [-44, 4], [-72, -4]], SIL, o);
    a.shape([[-60, -12], [-104, 4], [-98, 14], [-56, 0]], SIL, o);
    a.shape([[18, -44], [32, -56], [48, -46], [48, -30], [30, -26]], SIL, o);
    a.shape([[46, -42], [70, -34], [46, -30]], SILD, o);
    a.line([[-20, 4], [-22, 22]], {w: 2.4}).line([[0, 2], [-2, 22]], {w: 2.4});
    a.line([[-110, 24], [-20, 20], [60, 26]], {w: 5, taper: 0.5});
  } else if (kind === 'squirrel') {
    a.shape([[-26, -6], [-34, -52], [-10, -78], [20, -70], [34, -40], [26, -6]], SIL, o);
    a.shape([[14, -80], [26, -104], [44, -96], [52, -78], [40, -66], [22, -66]], SIL, o);
    a.shape([[22, -102], [26, -118], [34, -100]], SIL, o);
    a.shape([[-26, -20], [-62, -44], [-72, -92], [-54, -138], [-30, -130], [-38, -92], [-18, -52]], SIL, o);
    a.shape([[26, -50], [40, -44], [38, -34], [24, -38]], SILD, o);
  } else {
    a.shape([[-40, 0], [-34, -56], [-4, -88], [28, -72], [44, 0]], SIL, o);
    a.shape([[8, -96], [20, -128], [32, -106], [48, -134], [58, -100], [88, -88], [58, -76], [24, -76]], SIL, o);
    a.shape([[-40, -8], [-92, -16], [-116, -50], [-94, -66], [-62, -42], [-36, -30]], SIL, o);
    a.fill([[-110, -48], [-94, -62], [-88, -52], [-104, -40]], '#d9e4fa', 0.9);
  }
  return a.build();
};
const Critter: React.FC<{kind: 'owl' | 'crow' | 'squirrel' | 'fox'; x: number; y: number; s?: number; flip?: boolean; seed?: number; eyes?: boolean}> = ({kind, x, y, s = 1, flip = false, seed = 1, eyes = true}) => {
  const A = useMemo(() => critter(kind, seed), [kind, seed]);
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ArtView a={A} filter="wc1" sk={0} inkColor={SILD} dx={1.5} dy={1.5} />
      {kind === 'owl' && eyes ? (
        <>
          <circle cx={-13} cy={-68} r={8} fill="#e9f0ff" /><circle cx={13} cy={-68} r={8} fill="#e9f0ff" />
          <circle cx={-13} cy={-67} r={3.4} fill={SILD} /><circle cx={13} cy={-67} r={3.4} fill={SILD} />
        </>
      ) : null}
      {kind === 'crow' && eyes ? <circle cx={36} cy={-40} r={2.6} fill="#e9f0ff" /> : null}
      {kind === 'squirrel' && eyes ? <circle cx={38} cy={-84} r={2.4} fill="#e9f0ff" /> : null}
      {kind === 'fox' && eyes ? <circle cx={52} cy={-92} r={2.6} fill="#e9f0ff" /> : null}
    </g>
  );
};

/** 黑暗里一对亮晶晶的眼睛（不画动物，只让人知道“有很多小动物来了”） */
const EyePair: React.FC<{x: number; y: number; s?: number; o?: number}> = ({x, y, s = 1, o = 0.9}) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} opacity={o}>
    <ellipse cx={-9} cy={0} rx={4.6} ry={5.6} fill="#dce8ff" /><ellipse cx={9} cy={0} rx={4.6} ry={5.6} fill="#dce8ff" />
    <circle cx={-9} cy={0} r={2} fill={SILD} /><circle cx={9} cy={0} r={2} fill={SILD} />
  </g>
);

/* ───────────── 小道具：雪人 ───────────── */
const buildSnowman = () => {
  const a = new Art(701);
  const ring = (cx: number, cy: number, rx: number, ry: number, n = 16): P[] => Array.from({length: n}, (_, i) => [cx + Math.cos((i / n) * 6.283) * rx, cy + Math.sin((i / n) * 6.283) * ry] as P);
  a.shape(ring(0, -96, 112, 98), '#f8faff', {w: 3.4, sk: 1, wobble: 1.6});
  a.shade([[-100, -80], [-92, -40], [-52, -4], [10, 0], [64, -18], [90, -50], [40, -40], [-20, -44], [-70, -64]], 0.42);
  a.shape(ring(0, -250, 74, 68), '#f8faff', {w: 3.2, sk: 1, wobble: 1.4});
  a.shade([[-68, -236], [-58, -204], [-20, -184], [36, -190], [66, -214], [20, -214], [-30, -218]], 0.4);
  a.guide(0, -96, 112, 98, 0.1).guide(0, -250, 74, 68, -0.1);
  // 眼睛（小石子）、鼻子、红叶子做的嘴
  a.fill(ring(-24, -262, 7, 8, 8), SILD, 1).fill(ring(26, -264, 7, 8, 8), SILD, 1);
  a.shape([[-2, -246], [58, -236], [-2, -230]], '#dfe9fb', {w: 2.2, taper: 0.5});
  a.line([[-26, -222], [-10, -212], [14, -210], [30, -222]], {w: 3, taper: 0.5});
  // 纽扣
  a.fill(ring(0, -150, 6, 6, 8), SILD, 1).fill(ring(0, -108, 6, 6, 8), SILD, 1).fill(ring(0, -66, 6, 6, 8), SILD, 1);
  // 树枝手臂
  const arms = new Art(702);
  arms.line([[-96, -170], [-170, -214], [-210, -250]], {w: 5, taper: 0.5}).line([[-170, -214], [-196, -204]], {w: 3.4, taper: 0.5}).line([[-176, -218], [-182, -246]], {w: 3.2, taper: 0.5});
  arms.line([[96, -170], [166, -196], [214, -176]], {w: 5, taper: 0.5}).line([[166, -196], [188, -226]], {w: 3.2, taper: 0.5}).line([[190, -184], [208, -204]], {w: 3.2, taper: 0.5});
  // 围巾：冷色（红围巾只有小石头有）
  const sc = new Art(703);
  sc.shape([[-62, -200], [-30, -188], [30, -188], [64, -202], [70, -184], [30, -166], [-30, -166], [-66, -182]], '#8ea6d6', {w: 3, sk: 1});
  sc.shape([[34, -172], [62, -170], [70, -112], [46, -108]], '#8ea6d6', {w: 2.6});
  sc.line([[-40, -186], [-36, -168]], {w: 2, taper: 0.6}).line([[0, -186], [2, -167]], {w: 2, taper: 0.6}).line([[40, -186], [42, -168]], {w: 2, taper: 0.6});
  sc.shade([[-60, -184], [-30, -170], [30, -170], [62, -184], [30, -178], [-30, -178]], 0.4);
  // 头顶一根羽毛
  const f = new Art(704);
  f.shape([[0, -314], [14, -350], [30, -392], [26, -430], [10, -396], [-2, -352]], '#e9f0ff', {w: 2.4, sk: 0});
  f.line([[0, -314], [22, -420]], {w: 2, taper: 0.5});
  return {body: a.build(), arms: arms.build(), scarf: sc.build(), feather: f.build()};
};
const Snowman: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => {
  const A = useMemo(buildSnowman, []);
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ArtView a={A.arms} filter="wc2" sk={0} />
      <ArtView a={A.body} filter="wc0" />
      <ArtView a={A.scarf} filter="wc1" />
      <ArtView a={A.feather} filter="wc1" sk={0} />
    </g>
  );
};

/* ───────────── 小道具：农家小院 ───────────── */
const buildFarm = () => {
  const wall = new Art(801);
  wall.shape(dense([[-210, 0], [210, 0], [210, -190], [-210, -190]], 26), '#d3dff4', {w: 3.8, sk: 1, wobble: 1.2});
  wall.shade([[-210, -40], [210, -40], [210, 0], [-210, 0]], 0.5, '#4a5a8c');
  wall.shade([[150, -190], [210, -190], [210, 0], [172, 0]], 0.4);
  wall.line([[-214, 2], [214, 2]], {w: 5, taper: 0.3});
  const roof = new Art(802);
  roof.shape(dense([[-296, -134], [-254, -146], [-196, -246], [-120, -268], [120, -268], [196, -246], [254, -146], [296, -134], [268, -120], [-268, -120]], 30), '#4f5f93', {w: 3.4, sk: 1});
  roof.shade([[-250, -128], [250, -128], [262, -121], [-262, -121]], 0.5, '#1b2560');
  for (const y of [-160, -190, -220, -248]) roof.line([[-230 + (y + 160) * -0.28, y], [0, y - 4], [230 - (y + 160) * -0.28, y]], {w: 1.5, taper: 0.6, broken: 0.35});
  for (let x = -200; x <= 200; x += 40) roof.line([[x, -170], [x * 0.9, -258]], {w: 1.2, taper: 0.6, broken: 0.45});
  roof.shape([[-190, -246], [-120, -270], [120, -270], [190, -246], [168, -238], [60, -252], [-60, -252], [-168, -238]], '#f8faff', {w: 2.4, sk: 1});
  roof.shape([[-290, -132], [-250, -144], [-232, -136]], '#f8faff', {w: 2}).shape([[290, -132], [250, -144], [232, -136]], '#f8faff', {w: 2});
  const door = new Art(803);
  door.shape(dense([[50, 0], [134, 0], [134, -126], [50, -126]], 22), '#27346b', {w: 3.2, sk: 1});
  door.line([[92, -126], [92, 0]], {w: 2.2}).line([[122, -64], [127, -64]], {w: 3.4, taper: 0.2});
  const win = new Art(804);
  win.shape(dense([[-160, -112], [-66, -112], [-66, -50], [-160, -50]], 20), '#cfdcf3', {w: 3.4, sk: 1});
  win.line([[-113, -112], [-113, -50]], {w: 2.6}).line([[-160, -81], [-66, -81]], {w: 2.6});
  win.line([[-166, -46], [-60, -46]], {w: 5, taper: 0.3});
  // 一串一串的玉米（冷奶白色，不画黄色）
  const corn = new Art(805);
  for (const x of [-30, -8, 14]) corn.shape([[x - 7, -118], [x + 7, -118], [x + 5, -78], [x, -64], [x - 5, -78]], '#f2f5fd', {w: 1.8});
  const chim = new Art(806);
  chim.shape([[110, -272], [150, -272], [150, -200], [110, -210]], '#53638f', {w: 2.6});
  chim.shape([[104, -280], [156, -280], [152, -268], [108, -268]], '#f8faff', {w: 2});
  // 草垛
  const hay = new Art(807);
  hay.shape([[-90, 0], [-80, -62], [-40, -100], [20, -108], [70, -82], [92, -30], [96, 0]], '#cdd9f1', {w: 3.2, sk: 1});
  hay.shade([[-86, -10], [-74, -56], [-40, -90], [-6, -60], [-30, -20]], 0.35);
  hay.line([[-60, -20], [-40, -70]], {w: 1.4, broken: 0.3}).line([[-20, -12], [0, -86]], {w: 1.4, broken: 0.3}).line([[30, -10], [48, -64]], {w: 1.4, broken: 0.3}).line([[60, -8], [70, -46]], {w: 1.4, broken: 0.3});
  hay.shape([[-70, -80], [-30, -108], [30, -116], [74, -96], [30, -90], [-30, -84]], '#f8faff', {w: 2.2});
  // 篱笆
  const fence = new Art(808);
  for (let i = 0; i < 12; i++) {
    const x = -330 + i * 60;
    fence.shape([[x - 4, 0], [x + 4, 0], [x + 4, -70], [x, -80], [x - 4, -70]], '#c9d6f0', {w: 2});
  }
  fence.line([[-340, -52], [340, -54]], {w: 4, taper: 0.3}).line([[-340, -24], [340, -26]], {w: 4, taper: 0.3});
  fence.wash([[-338, -58], [338, -60]], 7, '#f8faff', 0.95);
  // 老桑树：冬天只有枝，枝上压着雪
  const tree = new Art(809);
  tree.line([[0, 0], [-6, -90], [4, -170], [-8, -240]], {w: 26, taper: 0.45, wobble: 3, sk: 1});
  tree.line([[-4, -170], [-70, -230], [-130, -250]], {w: 11, taper: 0.4}).line([[0, -190], [64, -250], [120, -262]], {w: 11, taper: 0.4});
  tree.line([[-8, -236], [-30, -300], [-24, -340]], {w: 9, taper: 0.4}).line([[-8, -240], [30, -300], [60, -318]], {w: 8, taper: 0.4});
  tree.line([[-90, -236], [-120, -290]], {w: 5, taper: 0.4}).line([[80, -254], [112, -300]], {w: 5, taper: 0.4});
  tree.line([[-130, -250], [-170, -250]], {w: 4, taper: 0.4}).line([[120, -262], [160, -250]], {w: 4, taper: 0.4});
  tree.wash([[-130, -254], [-70, -234], [-4, -176]], 8, '#f8faff', 0.95).wash([[0, -194], [64, -254], [120, -266]], 8, '#f8faff', 0.95);
  // 水井
  const well = new Art(810);
  well.shape([[-54, 0], [54, 0], [50, -52], [-50, -52]], '#c5d2ee', {w: 2.6, sk: 1});
  well.line([[-54, -26], [54, -26]], {w: 1.4, broken: 0.3});
  well.line([[-50, -52], [-50, -128]], {w: 5}).line([[50, -52], [50, -128]], {w: 5});
  well.shape([[-70, -126], [0, -166], [70, -126], [58, -120], [0, -150], [-58, -120]], '#6a7aac', {w: 2.6});
  well.shape([[-60, -128], [0, -160], [60, -128], [0, -140]], '#f8faff', {w: 1.8});
  return {wall: wall.build(), roof: roof.build(), door: door.build(), win: win.build(), corn: corn.build(), chim: chim.build(), hay: hay.build(), fence: fence.build(), tree: tree.build(), well: well.build()};
};
const Farm: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => {
  const A = useMemo(buildFarm, []);
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      {[0, 1, 2, 3].map((i) => {
        const u = (t * 0.16 + i / 4) % 1;
        return <ellipse key={i} cx={130 + u * 70 + Math.sin(t + i) * 8} cy={-330 - u * 160} rx={14 + u * 26} ry={10 + u * 18} fill="#e3ebfa" opacity={(1 - u) * 0.62} />;
      })}
      <g transform="translate(0 -40)"><ArtView a={A.chim} filter="wc1" /></g>
      <ArtView a={A.wall} filter="wc0" />
      <ArtView a={A.door} filter="wc1" />
      <ArtView a={A.win} filter="wc1" />
      <ArtView a={A.corn} filter="wc1" sk={0} />
      <g transform="translate(0 -40)"><ArtView a={A.roof} filter="wc2" /></g>
    </g>
  );
};

/* ───────────── 小道具：古城墙 ───────────── */
const buildWall = () => {
  const a = new Art(901);
  const top = -150;
  const pts: P[] = [[-520, 0], [-520, top]];
  for (let x = -520; x < 520; x += 80) pts.push([x, top - 34], [x + 40, top - 34], [x + 40, top], [x + 80, top]);
  pts.push([520, 0]);
  a.shape(pts, '#9fb0d6', {w: 3.4, sk: 1, wobble: 1.8});
  a.line([[-524, 2], [524, 2]], {w: 5, taper: 0.3});
  for (let y = -30; y > top; y -= 30) a.line([[-516, y], [516, y + 2]], {w: 1.5, taper: 0.5, broken: 0.25});
  for (let r = 0; r < 5; r++) for (let x = -480 + (r % 2) * 40; x < 500; x += 80) a.line([[x, -30 - r * 30], [x + 2, -58 - r * 30]], {w: 1.3, taper: 0.5, broken: 0.3});
  // 城门洞
  a.shape([[-60, 0], [-60, -96], [-30, -126], [30, -126], [60, -96], [60, 0]], '#1b2660', {w: 3.2, sk: 1});
  // 一座古塔
  const tower = new Art(902);
  const tx = 330;
  for (let k = 0; k < 4; k++) {
    const y0 = top - k * 70, w = 74 - k * 10;
    tower.shape([[tx - w, y0], [tx + w, y0], [tx + w - 8, y0 - 54], [tx - w + 8, y0 - 54]], '#8fa2cf', {w: 2.6, sk: 1});
    tower.shape([[tx - w - 26, y0 - 54], [tx + w + 26, y0 - 54], [tx + w + 6, y0 - 70], [tx - w - 6, y0 - 70]], '#4a5a8c', {w: 2.4});
    tower.line([[tx - w - 26, y0 - 54], [tx - w - 40, y0 - 62]], {w: 2}).line([[tx + w + 26, y0 - 54], [tx + w + 40, y0 - 62]], {w: 2});
  }
  tower.line([[tx, top - 280], [tx, top - 330]], {w: 3, taper: 0.4});
  // 墙头和墙缝里的小草（青绿）
  const grass = new Art(903);
  for (let i = 0; i < 26; i++) {
    const x = -500 + i * 40 + ((i * 17) % 13), y = top - 34 + (i % 2) * 34;
    grass.line([[x, y], [x - 6, y - 16 - (i % 3) * 5]], {w: 2.4, taper: 0.4}).line([[x, y], [x + 4, y - 20 - (i % 4) * 4]], {w: 2.4, taper: 0.4});
    grass.wash([[x, y], [x + 2, y - 18]], 4, C.moss, 0.9);
  }
  return {wall: a.build(), tower: tower.build(), grass: grass.build()};
};
const OldWall: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => {
  const A = useMemo(buildWall, []);
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <ArtView a={A.tower} filter="wc2" />
      <ArtView a={A.wall} filter="wc0" />
      <ArtView a={A.grass} filter="wc1" sk={0} />
    </g>
  );
};

/* ───────────── 星空：星星、银河、月牙、流星 ───────────── */
const StarSky: React.FC<{shoot?: boolean}> = ({shoot = true}) => {
  const stars = useMemo(() => {
    const r = rng(77);
    return Array.from({length: 190}, () => ({x: r() * W, y: r() * 500, r: 0.7 + r() * 2.1, o: 0.35 + r() * 0.65, big: r() > 0.93}));
  }, []);
  return (
    <Layer p={0.06}>
      <div style={{position: 'absolute', left: -200, top: 120, width: 2400, height: 210, transform: 'rotate(-14deg)', background: 'radial-gradient(ellipse at 50% 50%, rgba(205,222,255,0.5) 0, rgba(205,222,255,0.22) 38%, rgba(205,222,255,0) 70%)', filter: 'blur(26px)'}} />
      <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
        {stars.map((s, i) => (s.big ? (
          <g key={i} transform={`translate(${s.x} ${s.y})`} opacity={s.o}>
            <path d="M0 -13 Q1.6 -1.6 13 0 Q1.6 1.6 0 13 Q-1.6 1.6 -13 0 Q-1.6 -1.6 0 -13Z" fill="#f4f8ff" />
          </g>
        ) : <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#f4f8ff" opacity={s.o} />))}
        {/* 弯弯的月亮 */}
        <g transform="translate(1590 150)">
          <circle r={86} fill="url(#flakeG)" opacity={0.45} />
          <path d="M0 -44 A44 44 0 1 0 0 44 A34 40 0 1 1 0 -44Z" fill="#f4f8ff" />
        </g>
        {shoot ? (
          <g>
            <defs>
              <linearGradient id="shootG" x1="1" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#ffffff" stopOpacity={0.95} />
                <stop offset="1" stopColor="#ffffff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <path d="M1080 150 L860 300 L866 304 L1086 156Z" fill="url(#shootG)" />
            <circle cx={1082} cy={152} r={6} fill="#ffffff" />
            <circle cx={1082} cy={152} r={16} fill="url(#flakeG)" />
          </g>
        ) : null}
      </svg>
    </Layer>
  );
};

/* ───────────── 记忆圆窗：学校、大海（讲故事的人心里的画面） ───────────── */
const buildSchool = () => {
  const a = new Art(1001);
  a.shape(dense([[-150, 56], [150, 56], [150, -30], [-150, -30]], 24), '#b4c5e8', {w: 3.2, sk: 1});
  a.shape(dense([[-50, -30], [50, -30], [50, -90], [-50, -90]], 24), '#a3b6e0', {w: 3.2, sk: 1});
  a.shape(dense([[-62, -90], [0, -126], [62, -90]], 20), '#4f5f93', {w: 3});
  for (let r = 0; r < 2; r++) for (let c = 0; c < 6; c++) {
    if (c === 2 || c === 3) continue;
    const x = -134 + c * 46 + (c > 3 ? 0 : 0), y = -16 + r * 36;
    a.shape(dense([[x, y], [x + 26, y], [x + 26, y + 22], [x, y + 22]], 13), '#5d78b8', {w: 2});
  }
  a.shape(dense([[-18, 56], [18, 56], [18, 12], [-18, 12]], 14), '#27346b', {w: 2.4});
  a.shape(Array.from({length: 12}, (_, i) => [Math.cos((i / 12) * 6.283) * 14, -62 + Math.sin((i / 12) * 6.283) * 14] as P), '#f4f8ff', {w: 2});
  a.line([[0, -62], [0, -72]], {w: 1.8}).line([[0, -62], [8, -60]], {w: 1.8});
  // 旗杆 + 旗（冷色）
  const flag = new Art(1002);
  flag.line([[-178, 62], [-178, -118]], {w: 4, taper: 0.3});
  flag.shape(dense([[-176, -116], [-122, -108], [-128, -86], [-176, -90]], 16), '#e9f0ff', {w: 2.2});
  // 孩子们（小剪影）
  const kids = new Art(1003);
  for (const [x, c] of [[-70, '#7d96c4'], [-30, '#5d78b8'], [14, '#8ea6d6'], [54, '#44527f']] as [number, string][]) {
    kids.shape([[x - 8, 58], [x + 8, 58], [x + 7, 32], [x - 7, 32]], c, {w: 1.8});
    kids.shape(Array.from({length: 8}, (_, i) => [x + Math.cos((i / 8) * 6.283) * 8, 24 + Math.sin((i / 8) * 6.283) * 8] as P), '#f4f8ff', {w: 1.8});
  }
  const bush = new Art(1004);
  for (const x of [-140, 112, 138]) bush.shape([[x - 22, 60], [x - 16, 42], [x, 36], [x + 16, 44], [x + 22, 60]], C.moss, {w: 2.2});
  return {a: a.build(), flag: flag.build(), kids: kids.build(), bush: bush.build()};
};
const buildSea = () => {
  const a = new Art(1101);
  // 大海：几层波浪
  a.fill([[-190, -20], [190, -20], [190, 80], [-190, 80]], '#9fc3e4', 1);
  a.fill([[-190, 14], [190, 14], [190, 80], [-190, 80]], '#6a96cc', 0.85);
  a.fill([[-190, 46], [190, 46], [190, 80], [-190, 80]], '#4c78b4', 0.8);
  for (const [y, k] of [[-6, 0], [18, 1], [42, 2], [64, 3]] as [number, number][]) {
    const p: P[] = [];
    for (let x = -180; x <= 180; x += 30) p.push([x, y + Math.sin((x + k * 40) / 28) * 6]);
    a.line(p, {w: 2.4, taper: 0.6, broken: 0.2});
  }
  // 太阳（冷白）
  a.fill(Array.from({length: 12}, (_, i) => [96 + Math.cos((i / 12) * 6.283) * 26, -74 + Math.sin((i / 12) * 6.283) * 26] as P), '#f4f8ff', 0.95);
  const boat = new Art(1102);
  boat.shape([[-54, 18], [54, 18], [38, 40], [-38, 40]], '#44527f', {w: 2.6, sk: 1});
  boat.line([[0, 18], [0, -66]], {w: 3});
  boat.shape([[4, -62], [4, 10], [48, 10]], '#f4f8ff', {w: 2.4, sk: 1});
  boat.shape([[-4, -50], [-4, 10], [-38, 10]], '#dbe5f8', {w: 2.2});
  const birds = new Art(1103);
  for (const [x, y] of [[-110, -80], [-70, -104], [-30, -70]] as [number, number][]) birds.line([[x - 16, y + 6], [x - 6, y - 4], [x, y + 2], [x + 6, y - 4], [x + 16, y + 6]], {w: 2.4, taper: 0.6});
  return {a: a.build(), boat: boat.build(), birds: birds.build()};
};
const Medallion: React.FC<{x: number; y: number; r?: number; kind: 'school' | 'sea'; id: string}> = ({x, y, r = 200, kind, id}) => {
  const S = useMemo(buildSchool, []);
  const Sea = useMemo(buildSea, []);
  const k = r / 178;
  return (
    <g transform={`translate(${x} ${y}) scale(${k})`}>
      <defs>
        <radialGradient id={`${id}F`}><stop offset="0" stopColor="#fff" /><stop offset="0.74" stopColor="#fff" /><stop offset="1" stopColor="#000" /></radialGradient>
        <mask id={`${id}M`}><circle r={178} fill={`url(#${id}F)`} /></mask>
      </defs>
      <g mask={`url(#${id}M)`}>
        <circle r={178} fill={kind === 'sea' ? '#d9e8fb' : '#e4ecfa'} opacity={0.96} />
        {kind === 'school' ? (
          <g transform="translate(8 6) scale(0.86)">
            <ArtView a={S.a} filter="wc1" />
            <ArtView a={S.bush} filter="wc2" sk={0} />
            <ArtView a={S.flag} filter="wc1" sk={0} />
            <ArtView a={S.kids} filter="wc1" sk={0} />
          </g>
        ) : (
          <g transform="translate(0 10)">
            <ArtView a={Sea.a} filter="wc2" sk={0.3} />
            <g transform="translate(-10 -4)"><ArtView a={Sea.boat} filter="wc1" /></g>
            <ArtView a={Sea.birds} filter="wc1" sk={0} />
          </g>
        )}
      </g>
    </g>
  );
};

const BIRD = (() => {
  // 老鹰：几笔粗粗的飞鸟，像画里的“M”
  const a = new Art(1230);
  a.line([[-110, 6], [-60, -34], [-6, -8], [0, -4], [6, -8], [60, -34], [110, 6]], {w: 11, taper: 0.35, wobble: 1});
  a.fill([[-6, -10], [6, -10], [8, 8], [0, 14], [-8, 8]], SIL, 1);
  return a.build();
})();
const BRANCH = (() => {
  const a = new Art(1231);
  a.line([[-60, 20], [60, 6], [180, 14], [260, -10]], {w: 9, taper: 0.4, wobble: 1.5});
  a.line([[180, 14], [220, 36]], {w: 5, taper: 0.4}).line([[60, 6], [30, -24]], {w: 5, taper: 0.4});
  return a.build();
})();

/* ───────────── 各幅插图 ───────────── */
const Shadows: React.FC = () => {
  const longShadow = useMemo(() => {
    const a = new Art(1201);
    a.fill([[300, 700], [880, 760], [1500, 700], [1180, 790], [520, 800]], '#26356f', 0.3);
    a.fill([[120, 780], [700, 820], [1100, 790], [640, 870]], '#26356f', 0.36);
    a.fill([[1180, 720], [1800, 690], [1860, 760], [1300, 800]], '#26356f', 0.4);
    return a;
  }, []);
  const owl = useMemo(() => critter('owl', 1210), []);
  return (
    <Wrap mount={{cx: 1580, k: 0.4}} tint="#8c9ed6" dark={0.2} frame={{k: 0.78, bottom: 1130}} under={flat(longShadow)}>
      <GroundShadow x={950} y={868} rx={150} />
      <Rabbit x={760} y={868} s={0.82} fear={1} t0={2} />
      <Boy x={1000} y={862} s={0.95} head={-3} wind={0.4}>
        <TurtleHead x={-42} y={-190} s={1} t0={1} />
      </Boy>
      <g transform="translate(300 330)">
        <ArtView a={BRANCH} filter="wc1" sk={0} inkColor={SILD} />
        <Critter kind="owl" x={96} y={-12} s={1.35} seed={11} />
      </g>
      <EyePair x={340} y={610} s={0.8} o={0.7} />
      <EyePair x={1700} y={640} s={0.6} o={0.6} />
    </Wrap>
  );
};

const QMark: React.FC<{x: number; y: number; s?: number; rot?: number}> = ({x, y, s = 1, rot = 0}) => (
  <text x={x} y={y} fontFamily="WenKaiSub, serif" fontSize={64 * s} fill="#3a4a86" stroke="#f4f8ff" strokeWidth={4} paintOrder="stroke" transform={`rotate(${rot} ${x} ${y})`} filter="url(#inkRough)">？</text>
);
const Questions: React.FC = () => (
  <Wrap dawn={0.85} mount={{cx: 1500, k: 0.44}} snow={0.55}>
    <GroundShadow x={780} y={872} rx={130} />
    <GroundShadow x={1500} y={880} rx={90} />
    {/* 小石头在雪地上一笔一画写下的“问号” */}
    <g transform="translate(940 930) skewX(-18) scale(1 0.52)" opacity={0.92}>
      <text x={0} y={0} fontFamily="WenKaiSub, serif" fontSize={190} fill="#7189c2" stroke="#3f5391" strokeWidth={3} letterSpacing={44} filter="url(#inkRough)">问号</text>
    </g>
    <Boy x={760} y={866} s={0.94} sit={1} head={16} armN={40} lean={8} wind={0.4}>
      <TurtleHead x={-42} y={-190} s={1} t0={3} />
    </Boy>
    <Rabbit x={1500} y={880} s={0.98} perk={1} t0={1} />
    <QMark x={1530} y={690} s={2.2} rot={-8} />
    <QMark x={1400} y={620} s={1.6} rot={10} />
    <QMark x={1670} y={650} s={1.3} rot={14} />
  </Wrap>
);

const FarmPlate: React.FC = () => {
  const F = useMemo(buildFarm, []);
  return (
    <Wrap dawn={1} mount={{cx: 420, k: 0.36}} snow={0.25} frame={false}>
      <GroundShadow x={1330} y={726} rx={300} ry={20} />
      <Farm x={1330} y={724} s={1.1} />
      <g transform="translate(1790 730) scale(0.95)"><ArtView a={F.tree} filter="wc2" /></g>
      <g transform="translate(1000 740) scale(1)"><ArtView a={F.hay} filter="wc1" /></g>
      <g transform="translate(1630 756) scale(0.62)"><ArtView a={F.well} filter="wc1" /></g>
      <g transform="translate(1120 792) scale(0.5)"><ArtView a={F.fence} filter="wc1" sk={0.4} /></g>
      <GroundShadow x={540} y={868} rx={170} />
      <Deer x={470} y={864} s={0.88} walk={0.5} headDown={0.1} t0={1}>
        <g transform="translate(-30 -250)"><Turtle s={0.3} x={0} y={0} t0={2} /></g>
      </Deer>
      <Boy x={760} y={870} s={0.92} walk={0.8} t0={0.4} wind={0.5} />
      <Rabbit x={930} y={878} s={0.8} perk={0.8} t0={2} />
    </Wrap>
  );
};

const SnowmanPlate: React.FC = () => (
  <Wrap dawn={0.7} mount={{cx: 1620, k: 0.42}} snow={0.35} frame={{}}>
    <GroundShadow x={980} y={850} rx={190} ry={22} />
    <Snowman x={980} y={846} s={1.05} />
    <Rabbit x={985} y={426} s={0.36} perk={1} t0={1} />
    <GroundShadow x={520} y={868} rx={150} />
    <Deer x={540} y={866} s={0.82} headDown={0.22} t0={1} />
    <GroundShadow x={1420} y={866} rx={90} />
    <Boy x={1420} y={864} s={0.86} flip armN={-70} head={-4} wind={0.5}>
      <TurtleHead x={-42} y={-190} s={1} t0={2} />
    </Boy>
    <Turtle x={1240} y={884} s={0.5} flip look={1} t0={1} />
  </Wrap>
);

const WallPlate: React.FC = () => (
  <Wrap dawn={0.35} mount={{cx: 1700, k: 0.4}} snow={0.7} frame={{}}>
    <g opacity={0.95}><OldWall x={640} y={650} s={1.15} /></g>
    <GroundShadow x={700} y={874} rx={110} />
    <Rabbit x={760} y={880} s={0.8} perk={0.9} flip t0={1} />
    <Boy x={960} y={872} s={0.92} walk={0.8} t0={0.3} wind={0.5}>
      <TurtleHead x={-42} y={-190} s={1} t0={1} />
    </Boy>
    <GroundShadow x={1500} y={870} rx={170} />
    <Deer x={1480} y={868} s={0.84} flip headDown={0.18} t0={2} />
  </Wrap>
);

const CavePlate: React.FC = () => {
  const f = useCurrentFrame();
  void f;
  return (
    <AbsoluteFill style={{background: '#050a22'}}>
      <Defs />
      <Stage cam={CAM}>
        <Backdrop horizon={500} mount={{cx: 1280, k: 0.46, baseY: 560}} far mid />
        <div style={{position: 'absolute', inset: 0, background: '#8aa3da', mixBlendMode: 'multiply'}} />
        <Layer p={0.16}>
          <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={mountLamp(1280, 560, 0.46)[0]} y={mountLamp(1280, 560, 0.46)[1]} r={5.5} />
          </svg>
        </Layer>
        <Layer p={1}>
          <div style={{position: 'absolute', inset: 0, clipPath: 'ellipse(560px 300px at 960px 400px)'}}>
            <Snowfall horizon={520} wind={0.08} />
          </div>
          <Img src={staticFile('baked/cave.png')} style={{position: 'absolute', left: 0, top: 0, width: W, height: H}} />
          <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
            <Medallion x={480} y={350} r={235} kind="school" id="mSch" />
            <GroundShadow x={780} y={848} rx={110} />
            <GroundShadow x={1260} y={848} rx={230} />
            <Fire x={965} y={846} s={1.15} glow={1} />
            <g transform="translate(740 840)">
              <Boy x={0} y={0} s={0.7} sit={1} head={-4} wind={0.3}>
                <TurtleHead x={-42} y={-190} s={1.0} t0={1} />
              </Boy>
            </g>
            <g transform="translate(860 836)"><Rabbit x={0} y={0} s={0.62} perk={1} t0={5} /></g>
            <Deer x={1330} y={840} s={0.8} flip lie={1} headDown={0.1} t0={2} />
          </svg>
        </Layer>
      </Stage>
    </AbsoluteFill>
  );
};

const SeaPlate: React.FC = () => (
  <Wrap mount={{cx: 1640, k: 0.4}} tint="#9db0e0" snow={0.6}>
    <Medallion x={700} y={320} r={250} kind="sea" id="mSea" />
    <GroundShadow x={1330} y={868} rx={190} />
    <Deer x={1370} y={868} s={0.9} flip headDown={0.05} t0={1} />
    <GroundShadow x={880} y={882} rx={90} />
    <Boy x={860} y={876} s={0.86} sit={1} head={-10} wind={0.3}>
      <TurtleHead x={-42} y={-190} s={1} t0={2} />
    </Boy>
    <Rabbit x={1060} y={888} s={0.72} perk={1} t0={3} />
  </Wrap>
);

const StarsPlate: React.FC = () => (
  <Wrap mount={{cx: 560, k: 0.4}} snow={0.12} skyExtra={<StarSky />} frame={{}}>
    <GroundShadow x={1010} y={876} rx={380} ry={26} />
    <Rabbit x={640} y={880} s={0.8} perk={1} flip={false} rot={-8} t0={1} />
    <Boy x={860} y={874} s={0.9} sit={1} head={-26} lean={-14} armN={20} wind={0.3}>
      <TurtleHead x={-42} y={-190} s={1} t0={2} />
    </Boy>
    <Deer x={1380} y={878} s={0.88} lie={1} headDown={-0.1} t0={2} />
  </Wrap>
);

const DeerNightPlate: React.FC = () => (
  <Wrap mount={{cx: 330, k: 0.44}} dark={0.14} snow={1} snowWind={0.12} frame={{}}>
    <GroundShadow x={1180} y={870} rx={190} />
    <Deer x={1250} y={866} s={1.12} flip headDown={0} t0={1} />
    <GroundShadow x={880} y={874} rx={80} />
    <Boy x={900} y={870} s={0.9} sit={1} head={6} lean={4} wind={0.3} />
    <Rabbit x={1500} y={886} s={0.62} fear={1} t0={4} />
    <Turtle x={1640} y={894} s={0.44} snow={1} t0={3} />
  </Wrap>
);

const Stump: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => {
  const A = useMemo(() => {
    const a = new Art(1301);
    a.shape([[-40, 0], [-34, -50], [34, -50], [42, 0]], '#53649b', {w: 2.8, sk: 1});
    a.shade([[-40, -10], [-34, -46], [0, -44], [-10, -8]], 0.4, '#1b2560');
    a.shape([[-38, -50], [-30, -62], [30, -62], [38, -50]], '#f8faff', {w: 2.2});
    return a.build();
  }, []);
  return <g transform={`translate(${x} ${y}) scale(${s})`}><ArtView a={A} filter="wc1" /></g>;
};
const ContestPlate: React.FC = () => (
  <Wrap mount={{cx: 1500, k: 0.4}} dark={0.1} snow={0.5}>
    {/* 林子边上，赶来看白鹿的小动物们（只有剪影） */}
    <GroundShadow x={330} y={706} rx={80} ry={10} o={0.7} />
    <Critter kind="fox" x={330} y={700} s={1.3} seed={3} />
    <Stump x={600} y={760} s={1.1} />
    <Critter kind="squirrel" x={600} y={700} s={1.2} seed={4} />
    <Stump x={1600} y={770} s={1.2} />
    <Critter kind="owl" x={1600} y={712} s={1.25} seed={5} />
    <g transform="translate(1420 250) scale(1.2)"><ArtView a={BIRD} filter="wc1" sk={0} inkColor={SILD} /></g>
    <g transform="translate(620 340) scale(0.6)"><ArtView a={BIRD} filter="wc1" sk={0} inkColor={SILD} /></g>
    <EyePair x={170} y={600} s={0.9} />
    <EyePair x={1010} y={590} s={0.8} o={0.8} />
    <EyePair x={1380} y={604} s={0.7} o={0.7} />
    <GroundShadow x={1000} y={874} rx={250} />
    <Rabbit x={650} y={890} s={0.84} perk={1} t0={1} />
    <Boy x={830} y={880} s={0.92} head={-3} wind={0.4}>
      <TurtleHead x={-42} y={-190} s={1} t0={2} />
    </Boy>
    <Deer x={1230} y={876} s={0.94} flip headDown={0.02} t0={3} />
  </Wrap>
);

const PLATES: Record<string, React.FC> = {
  shadows: Shadows, questions: Questions, farm: FarmPlate, snowman: SnowmanPlate, wall: WallPlate,
  school: CavePlate, sea: SeaPlate, stars: StarsPlate, deernight: DeerNightPlate, contest: ContestPlate,
};
export const PLATE_IDS = Object.keys(PLATES);
export const Plate: React.FC<{which: string}> = ({which}) => {
  const P_ = PLATES[which] ?? Shadows;
  return <P_ />;
};
