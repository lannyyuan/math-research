import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art, type P} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {petal} from '../art/geom';
import {C} from '../palette';

// 问号：一只胖胖的白兔子。侧面朝右，脚底在 (0,0)。高约 215（含耳朵）。
const build = () => {
  const earFar = new Art(11)
    .shape(petal([60, -126], [50, -214], 22, -5), C.fur, {w: 2.6, sk: 1})
    .shade(petal([62, -130], [54, -206], 11, -4), 0.5, C.nosePink);
  const earNear = new Art(12)
    .shape(petal([48, -128], [10, -206], 25, 7), C.fur, {w: 3, sk: 1})
    .shade(petal([46, -132], [16, -196], 12, 6), 0.55, C.nosePink)
    .shade(petal([44, -128], [24, -176], 10, 4), 0.32);
  const body = new Art(13);
  const bodyPts: P[] = [[-12, -112], [-56, -98], [-82, -62], [-72, -22], [-30, -4], [20, -6], [56, -26], [66, -62], [48, -100]];
  body.shape(bodyPts, C.fur, {w: 3.2, sk: 1, wobble: 1.4});
  body.shade([[-80, -60], [-72, -24], [-30, -6], [20, -8], [52, -30], [30, -34], [-20, -40], [-60, -50]], 0.4);
  body.guide(-10, -58, 70, 54, -0.25);
  // 后脚、前爪
  body.shape([[-34, -8], [-12, -18], [26, -15], [38, -6], [18, 3], [-28, 3]], C.fur, {w: 2.4});
  body.line([[22, -4], [26, -12]], {w: 1.8, taper: 0.5}).line([[31, -4], [34, -11]], {w: 1.8, taper: 0.5});
  body.shape([[40, -34], [60, -36], [68, -18], [52, -8], [38, -16]], C.fur, {w: 2.2});
  body.line([[58, -22], [60, -12]], {w: 1.5, taper: 0.4});
  // 尾巴
  body.shape([[-82, -76], [-98, -78], [-106, -62], [-96, -50], [-80, -52], [-76, -64]], C.fur, {w: 2.4});
  const head = new Art(14);
  const headPts: P[] = [[58, -136], [82, -128], [94, -108], [102, -94], [92, -78], [66, -68], [38, -80], [32, -108]];
  head.shape(headPts, C.fur, {w: 3, sk: 1, wobble: 1.2});
  head.shade([[34, -100], [40, -80], [66, -70], [88, -78], [70, -82], [52, -90]], 0.38);
  head.guide(66, -102, 36, 34, 0.1);
  // 鼻（偏紫的冷粉，只有一点点）
  head.fill([[97, -100], [106, -97], [104, -88], [96, -90]], C.nosePink, 0.95);
  head.line([[96, -100], [105, -97], [103, -89], [96, -90]], {w: 1.8, closed: true, taper: 0.3});
  head.line([[100, -88], [96, -80], [88, -79]], {w: 1.7, taper: 0.7});
  // 眼睛 + 腮
  head.fill([[76, -111], [84, -113], [86, -105], [78, -103]], C.ink, 1);
  head.line([[72, -116], [82, -118], [89, -112]], {w: 2, taper: 0.9});
  head.shade([[66, -92], [78, -94], [80, -84], [68, -80]], 0.3, C.nosePink);
  return {earFar: earFar.build(), earNear: earNear.build(), body: body.build(), head: head.build()};
};

export interface RabbitProps {
  x?: number; y?: number; s?: number; flip?: boolean;
  t0?: number; // 相位
  perk?: number; // 0~1 竖耳程度
  hop?: number; // 0~1 弹跳高度（外部驱动）
  squash?: number; // -1~1 压扁/拉长
  fear?: number; // 0~1 吓得耳朵贴背、缩成一团
  rot?: number;
}

export const Rabbit: React.FC<RabbitProps> = ({x = 0, y = 0, s = 1, flip = false, t0 = 0, perk = 0.7, hop = 0, squash = 0, fear = 0, rot = 0}) => {
  const A = useMemo(build, []);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const breathe = 1 + Math.sin(t * 2.3) * 0.012;
  const earTwitch = Math.sin(t * 5.1) * 3 + Math.sin(t * 1.7) * 4;
  const earBack = fear * 38 - perk * 6;
  const noseJig = Math.sin(t * 9) * 0.8;
  return (
    <g transform={`translate(${x} ${y - hop * 60}) scale(${flip ? -s : s} ${s}) rotate(${rot})`}>
      <g transform={`translate(0 0) scale(${1 - squash * 0.06} ${1 + squash * 0.1 * breathe})`}>
        <g transform={`rotate(${earBack - earTwitch * 0.7} 60 -126)`}>
          <ArtView a={A.earFar} filter="wc1" />
        </g>
        <ArtView a={A.body} filter="wc0" />
        <g transform={`translate(0 ${noseJig * 0.4}) rotate(${fear * -4} 40 -90)`}>
          <ArtView a={A.head} filter="wc2" />
        </g>
        <g transform={`rotate(${earBack * 1.15 + earTwitch} 48 -128)`}>
          <ArtView a={A.earNear} filter="wc1" />
        </g>
      </g>
    </g>
  );
};
