import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art, type P} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {C} from '../palette';

// 守林人的小木屋。墙是冷灰蓝的圆木（不用棕色），屋顶压着厚厚的雪，窗里挂着那盏老油灯。
const buildCabin = () => {
  const wall = new Art(501);
  wall.shape([[-190, 0], [190, 0], [190, -190], [-190, -190]], '#3a4a86', {w: 3.4, sk: 1, wobble: 1.5});
  wall.shade([[-190, -40], [190, -40], [190, 0], [-190, 0]], 0.4, '#1b2560');
  for (let y = -30; y > -190; y -= 31) wall.line([[-188, y], [188, y + 2]], {w: 1.6, taper: 0.5, broken: 0.2});
  wall.line([[-190, -190], [-190, 0]], {w: 4}).line([[190, -190], [190, 0]], {w: 4});
  const roof = new Art(502);
  roof.shape([[-240, -172], [0, -340], [240, -172], [216, -160], [0, -298], [-216, -160]], '#f8faff', {w: 3.2, sk: 1});
  roof.shade([[-216, -160], [0, -298], [216, -160], [190, -156], [0, -272], [-190, -156]], 0.38);
  roof.line([[-216, -160], [-190, -168]], {w: 2}).line([[216, -160], [190, -168]], {w: 2});
  const door = new Art(503);
  door.shape([[40, 0], [122, 0], [122, -172], [40, -172]], '#10183f', {w: 3, sk: 1});
  door.shape([[122, 0], [162, -14], [162, -178], [122, -172]], '#2b3a76', {w: 2.6});
  door.line([[140, -80], [146, -80]], {w: 3, taper: 0.2});
  const win = new Art(504);
  win.shape([[-164, -152], [-58, -152], [-58, -66], [-164, -66]], '#fff3c4', {w: 3.4, sk: 1, opacity: 0.0});
  win.line([[-164, -152], [-58, -152], [-58, -66], [-164, -66]], {w: 3.6, closed: true}).line([[-111, -152], [-111, -66]], {w: 2.6}).line([[-164, -109], [-58, -109]], {w: 2.6});
  win.line([[-172, -62], [-50, -62]], {w: 5, taper: 0.3});
  const chim = new Art(505);
  chim.shape([[108, -296], [148, -296], [148, -222], [108, -230]], '#33437a', {w: 2.6});
  chim.shape([[102, -304], [154, -304], [150, -292], [106, -292]], '#f8faff', {w: 2});
  return {wall: wall.build(), roof: roof.build(), door: door.build(), win: win.build(), chim: chim.build()};
};

export const Cabin: React.FC<{x: number; y: number; s?: number; doorOpen?: number; lamp?: number}> = ({x, y, s = 1, doorOpen = 1, lamp = 1}) => {
  const A = useMemo(buildCabin, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      {/* 烟囱的烟：冷灰白，慢慢飘 */}
      {[0, 1, 2, 3].map((i) => {
        const u = ((t * 0.18 + i / 4) % 1);
        return <ellipse key={i} cx={128 + u * 60 + Math.sin(t + i) * 8} cy={-310 - u * 150} rx={14 + u * 26} ry={10 + u * 18} fill="#dbe5f7" opacity={(1 - u) * 0.5} />;
      })}
      <ArtView a={A.chim} filter="wc1" />
      <ArtView a={A.wall} filter="wc0" />
      <ArtView a={A.door} filter="wc1" />
      <ArtView a={A.win} filter="wc1" />
      <ArtView a={A.roof} filter="wc2" />
    </g>
  );
};

/** 老油灯特写：玻璃罩 + 灯芯 + 火苗（暖色，全片会发光的那一盏） */
const buildLamp = () => {
  const a = new Art(511);
  a.shape([[-34, -22], [34, -22], [44, 0], [-44, 0]], '#3b4a85', {w: 2.8, sk: 1});
  a.shape([[-26, -34], [26, -34], [30, -22], [-30, -22]], '#2a376c', {w: 2.4});
  a.shape([[-30, -128], [-36, -74], [-28, -34], [28, -34], [36, -74], [30, -128], [14, -158], [-14, -158]], '#fff4cc', {w: 3, sk: 1, opacity: 0.35});
  a.line([[-8, -34], [-6, -52]], {w: 3, taper: 0.4}).line([[8, -34], [6, -52]], {w: 3, taper: 0.4});
  a.line([[-14, -160], [-10, -176], [10, -176], [14, -160]], {w: 2.6, taper: 0.4});
  a.line([[0, -176], [0, -214]], {w: 2.4, taper: 0.4});
  return a.build();
};
export const OilLamp: React.FC<{x: number; y: number; s?: number; flame?: number}> = ({x, y, s = 1, flame = 1}) => {
  const A = useMemo(buildLamp, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const fl = (0.9 + 0.1 * Math.sin(t * 9) + 0.05 * Math.sin(t * 4.3)) * flame;
  const sway = Math.sin(t * 6) * 2.5;
  const fpath = `M0 -52 C${-16} ${-70} ${-14 + sway} ${-100 * fl} ${sway * 1.6} ${-124 * fl} C${14 + sway} ${-100 * fl} ${16} ${-70} 0 -52Z`;
  return (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <circle cx={0} cy={-84} r={150 * (0.7 + 0.3 * Math.min(1.3, flame))} fill="url(#lampMid)" opacity={0.75 * Math.min(1, flame)} />
      <ArtView a={A} filter="wc1" />
      <g filter="url(#wc1)">
        <path d={fpath} fill={C.lampOuter} opacity={0.95} />
        <path d={`M0 -54 C-9 -68 ${-7 + sway} ${-86 * fl} ${sway} ${-102 * fl} C${8 + sway} ${-86 * fl} 9 -68 0 -54Z`} fill={C.lampMid} />
        <path d={`M0 -56 C-4 -64 -3 -74 ${sway * 0.5} -82 C3 -74 4 -64 0 -56Z`} fill={C.lampCore} />
      </g>
    </g>
  );
};

/** 加灯油的小油壶（深蓝灰），细细一线灯油 */
export const OilCan: React.FC<{x: number; y: number; s?: number; tip?: number}> = ({x, y, s = 1, tip = 0}) => (
  <g transform={`translate(${x} ${y}) scale(${s}) rotate(${-tip * 38})`}>
    <path d="M0 0L80 -4L86 -30L10 -32Z" fill="#3b4a85" stroke="#1a1f3f" strokeWidth={3} strokeLinejoin="round" />
    <path d="M0 -4L-46 -26L-40 -34L6 -14Z" fill="#3b4a85" stroke="#1a1f3f" strokeWidth={3} strokeLinejoin="round" />
    <path d="M84 -26C100 -28 108 -42 100 -50" fill="none" stroke="#1a1f3f" strokeWidth={4} strokeLinecap="round" />
    <rect x={20} y={-26} width={30} height={14} fill="#6f86b2" opacity={0.6} />
  </g>
);
