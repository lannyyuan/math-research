import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art, type P} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {C} from '../palette';
import {LampGlow} from '../fx/Lamp';

// 慢慢：很老很老的乌龟。壳上的花纹是一张地图。

/** 在书包里只露出头：原点在书包口中央 */
const buildHead = () => {
  const a = new Art(41);
  // 脖子（皱皱的）+ 头
  a.shape([[-14, 4], [-12, -22], [-4, -38], [12, -46], [30, -44], [38, -34], [34, -24], [22, -20], [14, -10], [14, 4]], C.shellB, {w: 2.6, sk: 1});
  a.shade([[-12, -4], [-10, -22], [-2, -30], [8, -14], [10, 2]], 0.35);
  a.line([[-8, -12], [8, -14]], {w: 1.2, taper: 0.8}).line([[-9, -22], [5, -25]], {w: 1.2, taper: 0.8});
  // 眼：半闭，老老的，眉毛长长垂下
  a.line([[20, -41], [27, -39], [33, -41]], {w: 2, taper: 0.7});
  a.line([[16, -46], [28, -48], [38, -42]], {w: 1.6, taper: 0.9});
  // 嘴、鼻孔
  a.line([[24, -28], [32, -27], [38, -31]], {w: 1.5, taper: 0.7});
  a.fill([[37, -37], [40, -37], [40, -34], [37, -34]], C.ink, 0.9);
  return a.build();
};
export const TurtleHead: React.FC<{x?: number; y?: number; s?: number; t0?: number; up?: number}> = ({x = 0, y = 0, s = 1, t0 = 0, up = 0}) => {
  const A = useMemo(buildHead, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const nod = Math.sin(t * 0.9) * 4;
  const rise = Math.sin(t * 0.6) * 1.5 + up;
  return (
    <g transform={`translate(${x} ${y + rise}) scale(${s})`}>
      <g transform={`rotate(${nod} 0 0)`}>
        <ArtView a={A} filter="wc2" />
      </g>
    </g>
  );
};

/** 整只乌龟，原点在脚底中央，朝右。snow=1 时壳上落满雪，像一块大石头 */
const buildFull = () => {
  const shellPts: P[] = [[-108, -12], [-104, -58], [-80, -98], [-40, -120], [10, -126], [58, -114], [92, -84], [108, -44], [112, -12]];
  const legs = new Art(42);
  legs.shape([[-76, -22], [-38, -22], [-34, 2], [-80, 2]], C.shellB, {w: 2.4});
  legs.shape([[66, -22], [100, -24], [106, 2], [62, 2]], C.shellB, {w: 2.4});
  legs.line([[-70, -2], [-66, -10]], {w: 1.2}).line([[78, -2], [82, -10]], {w: 1.2});
  const far = new Art(43);
  far.shape([[-40, -20], [-6, -20], [-4, 0], [-44, 0]], C.shellMap, {w: 2, opacity: 0.7});
  far.shape([[28, -20], [58, -20], [62, 0], [24, 0]], C.shellMap, {w: 2, opacity: 0.7});
  far.shape([[-112, -16], [-134, -8], [-120, -2]], C.shellB, {w: 1.8});

  const shell = new Art(44);
  shell.shape(shellPts, C.shellA, {w: 3.4, sk: 1, wobble: 1.6});
  shell.guide(0, -62, 112, 66, 0);
  // 地图：陆地块、河流、山、虚线路线
  shell.fill([[-80, -84], [-40, -108], [0, -102], [-8, -70], [-48, -62]], C.shellB, 0.9);
  shell.fill([[16, -104], [54, -98], [76, -66], [38, -52], [14, -74]], C.shellB, 0.85);
  shell.fill([[-96, -46], [-64, -54], [-54, -28], [-90, -24]], C.shellB, 0.8);
  shell.fill([[30, -44], [66, -48], [80, -26], [42, -22]], '#8fb7b2', 0.8);
  shell.shade([[-100, -30], [-96, -56], [-60, -50], [-30, -30], [20, -26], [60, -24], [100, -30], [108, -14], [-104, -14]], 0.3, C.shellMap);
  shell.line([[-58, -108], [-34, -82], [-8, -70], [14, -50], [28, -32], [34, -14]], {w: 2.2, taper: 0.6}); // 河
  shell.line([[-74, -72], [-68, -86], [-62, -72]], {w: 1.6, taper: 0.4}).line([[-58, -70], [-52, -84], [-45, -70]], {w: 1.6, taper: 0.4});
  shell.line([[40, -86], [47, -100], [54, -86]], {w: 1.6, taper: 0.4});
  shell.line([[-90, -34], [-70, -42], [-50, -30], [-20, -48], [10, -62], [40, -90], [64, -80]], {w: 1.5, taper: 0.3, broken: 0.7}); // 路线（断断续续）
  shell.line([[-96, -38], [-84, -30]], {w: 1.6}).line([[-96, -30], [-84, -38]], {w: 1.6}); // 起点叉
  // 壳缝（浅浅的）
  shell.line([[-20, -124], [-14, -90], [-24, -48]], {w: 1, taper: 0.5, broken: 0.4}).line([[40, -118], [44, -80], [34, -40]], {w: 1, taper: 0.5, broken: 0.4});
  shell.line([[-108, -14], [112, -14]], {w: 2.4, taper: 0.4});

  const head = new Art(45);
  head.shape([[104, -44], [118, -72], [142, -84], [166, -76], [178, -60], [170, -46], [146, -42], [124, -34]], C.shellB, {w: 2.8, sk: 1});
  head.shade([[110, -44], [124, -36], [148, -42], [166, -48], [150, -56], [124, -52]], 0.34);
  head.line([[114, -62], [128, -66]], {w: 1.1, taper: 0.8}).line([[112, -52], [126, -56]], {w: 1.1, taper: 0.8});
  head.line([[148, -68], [156, -66], [162, -69]], {w: 2, taper: 0.7});
  head.line([[142, -76], [154, -79], [166, -72]], {w: 1.5, taper: 0.9});
  head.line([[152, -52], [164, -52], [172, -55]], {w: 1.4, taper: 0.7});
  head.fill([[172, -64], [175, -64], [175, -61], [172, -61]], C.ink, 0.9);

  // 雪帽
  const snow = new Art(46);
  snow.shape([[-104, -54], [-84, -98], [-42, -122], [10, -130], [58, -118], [94, -86], [86, -76], [66, -86], [46, -78], [18, -86], [-14, -78], [-48, -88], [-76, -70], [-98, -70]], '#f8faff', {w: 2.6, sk: 1});
  snow.shade([[-98, -64], [-76, -72], [-48, -88], [-14, -80], [18, -88], [46, -80], [66, -88], [86, -78], [70, -96], [10, -110], [-60, -100]], 0.34);
  return {legs: legs.build(), far: far.build(), shell: shell.build(), head: head.build(), snow: snow.build()};
};

export interface TurtleProps {x?: number; y?: number; s?: number; flip?: boolean; snow?: number; look?: number; t0?: number; mark?: number}
export const Turtle: React.FC<TurtleProps> = ({x = 0, y = 0, s = 1, flip = false, snow = 0, look = 0, t0 = 0, mark = 0}) => {
  const A = useMemo(buildFull, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const nod = Math.sin(t * 0.8) * 3 - look * 6;
  const breathe = 1 + Math.sin(t * 1.4) * 0.008;
  return (
    <g transform={`translate(${x} ${y}) scale(${flip ? -s : s} ${s})`}>
      <ArtView a={A.far} filter="wc2" />
      <g transform={`scale(1 ${breathe})`}>
        <ArtView a={A.legs} filter="wc1" />
        <ArtView a={A.shell} filter="wc0" />
        {mark > 0.01 ? <LampGlow x={64} y={-82} r={3.2} glow={mark} rays={false} t0={t0} /> : null}
        <g transform={`translate(${2 + look * 8} 0) rotate(${nod} 108 -44) translate(108 -44) scale(1.35) translate(-108 44)`}>
          <ArtView a={A.head} filter="wc2" />
        </g>
        {snow > 0.02 ? (
          <g transform={`translate(${(1 - snow) * 90} ${(1 - snow) * 70}) rotate(${(1 - snow) * 24} 60 -100)`} opacity={Math.min(1, snow * 1.6)}>
            <ArtView a={A.snow} filter="wc2" />
          </g>
        ) : null}
      </g>
    </g>
  );
};
