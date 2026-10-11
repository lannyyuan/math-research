import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art, type P} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {petal, limb} from '../art/geom';
import {C} from '../palette';

// ───────── 守林人：白头发、白胡子、冷灰蓝的长外套，拄着拐棍。正面，脚底 (0,0)，高约 330 ─────────
const buildOldMan = () => {
  const a = new Art(71);
  // 外套
  a.shape([[-46, -250], [0, -262], [46, -250], [60, -190], [70, -100], [78, -22], [0, -12], [-78, -22], [-68, -100], [-58, -190]], C.coatTeal, {w: 3.2, sk: 1, wobble: 1.6});
  a.shade([[-58, -190], [-68, -100], [-78, -22], [-40, -18], [-34, -100], [-30, -190]], 0.4, '#1d2760');
  a.line([[0, -256], [2, -130], [0, -16]], {w: 1.8, taper: 0.5});
  a.line([[-50, -150], [-20, -146]], {w: 1.4}).line([[50, -150], [20, -146]], {w: 1.4});
  a.shape([[-30, -92], [-8, -90], [-6, -66], [-30, -68]], C.stoneDark, {w: 1.6, opacity: 0.8}); // 口袋
  // 手臂
  const arm = new Art(72);
  arm.shape(limb([-48, -244], [-70, -140], 26, 20), C.coatTeal, {w: 2.6});
  arm.shape([[-80, -146], [-60, -148], [-58, -128], [-78, -126]], C.paper, {w: 1.8});
  arm.shape(limb([48, -244], [66, -140], 26, 20), C.coatTeal, {w: 2.6});
  arm.shape([[58, -146], [78, -144], [80, -126], [60, -128]], C.paper, {w: 1.8});
  // 拐棍
  const cane = new Art(73);
  cane.line([[-72, -22], [-74, -90], [-72, -150], [-60, -176], [-44, -170]], {w: 3.4, taper: 0.4});
  // 头
  const head = new Art(74);
  head.shape([[-30, -300], [-24, -330], [0, -342], [24, -330], [30, -300], [24, -268], [0, -254], [-24, -268]], C.paper, {w: 2.8, sk: 1, wobble: 1.3});
  head.shade([[-28, -296], [-24, -268], [0, -256], [-14, -280]], 0.22);
  // 白头发 + 冷灰蓝毛线帽
  head.shape([[-40, -312], [-30, -346], [0, -362], [30, -346], [40, -312], [34, -296], [26, -318], [0, -326], [-26, -318], [-34, -296]], '#6f86b2', {w: 2.8});
  head.shape([[-46, -290], [-36, -308], [-32, -280], [-40, -270]], '#ffffff', {w: 2});
  head.shape([[46, -290], [36, -308], [32, -280], [40, -270]], '#ffffff', {w: 2});
  // 眉、眼（笑眯眯）、鼻
  head.line([[-20, -306], [-8, -308]], {w: 3, taper: 0.8}).line([[8, -308], [20, -306]], {w: 3, taper: 0.8});
  head.line([[-18, -298], [-12, -295], [-6, -298]], {w: 1.8, taper: 0.7}).line([[6, -298], [12, -295], [18, -298]], {w: 1.8, taper: 0.7});
  head.shape([[-4, -296], [4, -296], [6, -282], [0, -278], [-6, -282]], C.paper, {w: 1.6});
  head.shade([[-24, -284], [-12, -286], [-14, -276], [-24, -276]], 0.25, C.shade);
  // 大白胡子
  head.shape([[-30, -286], [-24, -262], [-30, -230], [-16, -196], [0, -180], [16, -196], [30, -230], [24, -262], [30, -286], [14, -274], [0, -270], [-14, -274]], '#fbfdff', {w: 2.8, sk: 1});
  head.shade([[-30, -232], [-16, -198], [0, -184], [14, -198], [0, -214], [-18, -222]], 0.32);
  head.line([[-12, -250], [-8, -214], [-4, -192]], {w: 1.2, taper: 0.8, broken: 0.3}).line([[10, -246], [8, -214], [4, -194]], {w: 1.2, taper: 0.8, broken: 0.3});
  return {body: a.build(), arm: arm.build(), cane: cane.build(), head: head.build()};
};
export const OldMan: React.FC<{x?: number; y?: number; s?: number; flip?: boolean; t0?: number; nod?: number}> = ({x = 0, y = 0, s = 1, flip = false, t0 = 0, nod = 0}) => {
  const A = useMemo(buildOldMan, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const br = 1 + Math.sin(t * 1.6) * 0.006;
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ArtView a={A.cane} filter="wc1" />
      <g transform={`scale(1 ${br})`}>
        <ArtView a={A.body} filter="wc0" />
        <ArtView a={A.arm} filter="wc1" />
        <g transform={`translate(0 -256) scale(1.22) rotate(${nod + Math.sin(t * 0.7) * 1.5}) translate(0 256)`}>
          <ArtView a={A.head} filter="wc2" />
        </g>
      </g>
    </g>
  );
};

// ───────── 狼妈妈：灰蓝色的大狼，眼神温柔，朝右，脚底 (0,0)，肩高约 175 ─────────
const buildWolf = () => {
  const body = new Art(81);
  body.fill([[-112, -152], [-80, -172], [-20, -176], [50, -174], [96, -160], [118, -130], [106, -108], [70, -102], [10, -106], [-50, -110], [-100, -116], [-122, -134]], C.wolf);
  body.shade([[-120, -130], [-100, -116], [-50, -110], [10, -106], [70, -102], [106, -108], [60, -118], [-40, -122], [-100, -126]], 0.34, C.wolfShade);
  body.shade([[-100, -170], [-30, -176], [40, -174], [0, -158], [-70, -156]], 0.22, '#d6def0');
  body.guide(0, -140, 112, 44, 0);
  body.line([[-122, -134], [-114, -154], [-80, -174], [-20, -178], [50, -176], [96, -162]], {w: 3.2, sk: 1, wobble: 1.6, taper: 0.5});
  body.line([[-122, -134], [-100, -116], [-50, -110], [10, -106], [70, -102], [106, -108]], {w: 3, taper: 0.5, wobble: 1.4});
  const tail = new Art(82);
  tail.shape(petal([-118, -138], [-186, -62], 44, 12), C.wolf, {w: 2.8, sk: 1});
  tail.shade(petal([-124, -130], [-178, -70], 22, 10), 0.3, C.wolfShade);
  tail.line([[-150, -110], [-140, -100]], {w: 1.2, taper: 0.7}).line([[-166, -90], [-154, -82]], {w: 1.2, taper: 0.7});
  // 头 + 粗脖子连在一起；鼻子朝右微微向下
  const head = new Art(83);
  head.shape([[86, -168], [112, -200], [146, -226], [182, -232], [208, -214], [234, -194], [242, -180], [228, -170], [200, -172], [170, -164], [140, -146], [110, -128], [96, -140]], C.wolf, {w: 3, sk: 1, wobble: 1.3});
  head.shade([[110, -130], [140, -148], [170, -166], [200, -174], [228, -172], [202, -184], [170, -176], [136, -166]], 0.3, '#d6def0');
  head.shade([[112, -200], [98, -160], [96, -142], [126, -160], [132, -196]], 0.3, C.wolfShade);
  head.guide(180, -200, 56, 40, 0.3);
  head.fill([[234, -192], [248, -188], [246, -176], [232, -180]], C.ink, 1);
  head.fill([[186, -208], [200, -212], [204, -198], [190, -196]], C.ink, 1);
  head.fill([[192, -208], [197, -209], [198, -203], [193, -203]], '#ffffff', 0.9);
  head.line([[180, -218], [198, -224], [212, -212]], {w: 1.8, taper: 0.9});
  head.line([[228, -171], [206, -174], [188, -180]], {w: 1.5, taper: 0.8});
  head.line([[100, -176], [108, -168], [102, -158], [110, -148]], {w: 1.4, taper: 0.6}); // 颈毛
  const ear = new Art(84);
  ear.shape(petal([156, -226], [148, -282], 36, -4), C.wolf, {w: 2.6, sk: 1});
  ear.shade(petal([156, -228], [150, -272], 18, -3), 0.4, C.nosePink);
  const leg = (seed: number, pts: P[], color: string) => new Art(seed).shape(pts, color, {w: 2.6}).build();
  return {
    body: body.build(), tail: tail.build(), head: head.build(), ear: ear.build(),
    foreN: leg(85, [[72, -112], [102, -112], [98, -40], [102, 0], [68, 0], [78, -40]], C.wolf),
    foreF: leg(86, [[100, -110], [126, -110], [120, -40], [124, 0], [96, 0], [106, -40]], C.wolfShade),
    hindN: leg(87, [[-112, -122], [-72, -122], [-64, -60], [-78, -36], [-72, 0], [-106, 0], [-102, -36], [-118, -60]], C.wolf),
    hindF: leg(88, [[-82, -120], [-46, -120], [-40, -60], [-52, -36], [-48, 0], [-78, 0], [-76, -36], [-90, -60]], C.wolfShade),
  };
};
export const Wolf: React.FC<{x?: number; y?: number; s?: number; flip?: boolean; walk?: number; headDown?: number; t0?: number}> = ({x = 0, y = 0, s = 1, flip = false, walk = 0, headDown = 0, t0 = 0}) => {
  const A = useMemo(buildWolf, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const ph = t * Math.PI * 2 * 0.9;
  const sw = Math.sin(ph) * 14 * walk;
  const br = 1 + Math.sin(t * 1.8) * 0.01;
  return (
    <g transform={`translate(${x} ${y - Math.abs(Math.sin(ph)) * 3 * walk}) scale(${flip ? -s : s} ${s})`}>
      <g transform={`rotate(${-sw} -64 -120)`}><ArtView a={A.hindF} filter="wc2" /></g>
      <g transform={`rotate(${sw} 112 -110)`}><ArtView a={A.foreF} filter="wc2" /></g>
      <g transform={`rotate(${Math.sin(t * 1.2) * 3} -124 -134)`}><ArtView a={A.tail} filter="wc1" /></g>
      <g transform={`scale(1 ${br})`}>
        <ArtView a={A.body} filter="wc0" />
        <g transform={`rotate(${headDown * 26} 100 -160)`}>
          <ArtView a={A.head} filter="wc2" />
          <g transform={`rotate(${Math.sin(t * 2.3) * 3} 156 -226)`}><ArtView a={A.ear} filter="wc1" /></g>
        </g>
      </g>
      <g transform={`rotate(${-sw} -92 -122)`}><ArtView a={A.hindN} filter="wc1" /></g>
      <g transform={`rotate(${sw} 86 -112)`}><ArtView a={A.foreN} filter="wc1" /></g>
    </g>
  );
};

// ───────── 小狼：很小很小，圆圆的大眼睛，身上落着雪，发抖。坐姿，朝右，脚底 (0,0)，高约 120 ─────────
const buildCub = () => {
  const a = new Art(91);
  a.shape([[-34, -4], [-42, -44], [-22, -78], [14, -82], [38, -52], [34, -4], [0, 4]], C.wolf, {w: 2.8, sk: 1});
  a.shade([[-40, -20], [-34, -4], [0, 4], [34, -4], [30, -22], [0, -16]], 0.34, C.wolfShade);
  a.shape(petal([-34, -30], [-70, -14], 30, 6), C.wolf, {w: 2.2}); // 尾巴
  a.shape([[-8, -4], [8, -4], [10, 4], [-12, 4]], C.wolfShade, {w: 1.8, opacity: 0.7}); // 前脚
  const head = new Art(92);
  head.shape([[-18, -100], [-4, -126], [22, -132], [46, -118], [58, -96], [54, -78], [30, -70], [2, -74], [-16, -86]], C.wolf, {w: 2.8, sk: 1, wobble: 1.2});
  head.shade([[-8, -80], [2, -74], [30, -70], [54, -80], [30, -86], [8, -84]], 0.3, '#d6def0');
  head.shape(petal([-8, -122], [-18, -156], 24, -3), C.wolf, {w: 2.2});
  head.shape(petal([24, -128], [36, -160], 24, 3), C.wolf, {w: 2.2});
  head.fill([[50, -98], [60, -96], [58, -88], [49, -90]], C.ink, 1);
  head.fill([[26, -108], [38, -110], [40, -98], [28, -96]], C.ink, 1);
  head.fill([[30, -108], [34, -109], [35, -104], [31, -104]], '#ffffff', 0.95);
  head.line([[22, -116], [36, -120], [44, -112]], {w: 1.6, taper: 0.9});
  head.line([[56, -82], [42, -80], [32, -84]], {w: 1.3, taper: 0.8});
  const snow = new Art(93);
  snow.shape([[-30, -64], [-12, -84], [14, -84], [30, -60], [14, -66], [-6, -62], [-20, -68]], '#f8faff', {w: 1.6});
  snow.shape([[-10, -128], [8, -136], [26, -130], [14, -124], [0, -126]], '#f8faff', {w: 1.4});
  return {body: a.build(), head: head.build(), snow: snow.build()};
};
export const Cub: React.FC<{x?: number; y?: number; s?: number; flip?: boolean; shiver?: number; t0?: number; headTilt?: number}> = ({x = 0, y = 0, s = 1, flip = false, shiver = 1, t0 = 0, headTilt = 0}) => {
  const A = useMemo(buildCub, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const jx = Math.sin(t * 38) * 1.3 * shiver;
  return (
    <g transform={`translate(${x + jx} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ArtView a={A.body} filter="wc1" />
      <g transform={`rotate(${headTilt + Math.sin(t * 1.4) * 2} 10 -80)`}>
        <ArtView a={A.head} filter="wc2" />
        <ArtView a={A.snow} filter="wc2" sk={0} />
      </g>
    </g>
  );
};
