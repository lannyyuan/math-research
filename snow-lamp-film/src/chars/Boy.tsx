import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Art, type P} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {limb} from '../art/geom';
import {C} from '../palette';

// 小石头：7 岁男孩。侧面朝右，脚底 (0,0)，身高约 280（含头发）。
// 冷色棉衣 + 红围巾（全片唯一的暖色角色细节）+ 背着书包。
export type Variant = 'boy' | 'shirt' | 'dad' | 'mom';
// 红围巾只有小石头有；大人的围巾是冷色
const V: Record<Variant, {jacket: string; shade: string; pants: string; hair: string; scarf: string | null; scarfShade: string; headK: number; skirt?: boolean; pack: boolean}> = {
  boy: {jacket: C.jacket, shade: C.jacketShade, pants: C.pants, hair: C.hair, scarf: C.scarf, scarfShade: C.scarfShade, headK: 1, pack: true},
  shirt: {jacket: '#9fb2da', shade: '#7d92c4', pants: C.pants, hair: C.hair, scarf: C.scarf, scarfShade: C.scarfShade, headK: 1, pack: true},
  dad: {jacket: '#3d6a78', shade: '#2b4f5e', pants: '#232c52', hair: '#1b2140', scarf: '#9fb2da', scarfShade: '#6f86b2', headK: 0.78, pack: false},
  mom: {jacket: '#7d96c4', shade: '#5b73a6', pants: '#4a5a8c', hair: '#242a4d', scarf: '#e4ebf8', scarfShade: '#9fb0d4', headK: 0.78, skirt: true, pack: false},
};
const cache: Partial<Record<Variant, ReturnType<typeof build>>> = {};
const get = (v: Variant) => (cache[v] ??= build(v));

function build(variant: Variant) {
  const cfg = V[variant];
  const pack = new Art(21);
  pack.shape([[-72, -184], [-46, -198], [-14, -190], [-8, -150], [-12, -104], [-40, -92], [-70, -100], [-78, -142]], C.bag, {w: 3, sk: 1});
  pack.shade([[-76, -140], [-70, -102], [-40, -94], [-12, -106], [-16, -126], [-50, -120]], 0.45);
  pack.line([[-44, -168], [-42, -104]], {w: 1.6, taper: 0.6});
  pack.shape([[-14, -184], [-6, -172], [-4, -128], [4, -108], [-8, -104], [-16, -124]], C.bagShade, {w: 2, opacity: 0.0}); // 肩带轮廓由躯干处理
  const packFlap = new Art(22);
  packFlap.shape([[-74, -180], [-46, -196], [-12, -188], [-14, -158], [-44, -150], [-72, -156]], C.bagShade, {w: 2.8, sk: 1});
  packFlap.line([[-62, -168], [-30, -172]], {w: 1.4, taper: 0.7});
  packFlap.fill([[-34, -156], [-26, -156], [-26, -146], [-34, -146]], '#c9d6ef', 0.9);

  const torso = new Art(23);
  torso.shape([[-22, -196], [10, -203], [36, -192], [46, -160], [44, -118], [36, -88], [8, -82], [-18, -86], [-26, -120], [-28, -166]], cfg.jacket, {w: 3, sk: 1, wobble: 1.4});
  torso.shade([[-28, -150], [-26, -120], [-18, -86], [8, -82], [30, -88], [8, -104], [-6, -140]], 0.4, '#1d2760');
  torso.line([[-24, -152], [12, -146], [44, -150]], {w: 1.5, taper: 0.8, broken: 0.2});
  torso.line([[-25, -122], [10, -116], [44, -120]], {w: 1.5, taper: 0.8, broken: 0.2});
  torso.line([[40, -188], [39, -140], [36, -92]], {w: 1.5, taper: 0.7});
  torso.line([[-6, -186], [-2, -150], [-4, -108]], {w: 1.8, taper: 0.7}); // 书包肩带
  torso.guide(10, -142, 36, 56, 0.05);

  const legN = new Art(24);
  legN.shape(limb([8, -92], [10, -16], 25, 19), cfg.pants, {w: 2.6, sk: 1});
  legN.shape([[-8, -18], [26, -18], [38, -8], [40, 0], [-8, 2]], '#1d2548', {w: 2.4});
  const legF = new Art(25);
  legF.shape(limb([4, -92], [2, -16], 24, 18), cfg.shade, {w: 2.4});
  legF.shape([[-14, -18], [20, -18], [32, -8], [34, 0], [-14, 2]], '#151b3d', {w: 2.2});

  const armN = new Art(26);
  armN.shape(limb([6, -178], [20, -116], 22, 18), cfg.jacket, {w: 2.6, sk: 1});
  armN.shade([[0, -170], [6, -130], [18, -118], [14, -150]], 0.3, '#1d2760');
  armN.shape([[12, -116], [28, -118], [32, -104], [20, -98], [10, -104]], '#31406e', {w: 2.2});
  const armF = new Art(27);
  armF.shape(limb([4, -178], [14, -116], 21, 17), cfg.shade, {w: 2.4});
  armF.shape([[6, -116], [22, -118], [26, -104], [14, -98], [4, -104]], '#222c58', {w: 2});

  const scarf = new Art(28);
  scarf.shape([[-14, -194], [18, -206], [46, -197], [52, -183], [38, -172], [6, -171], [-14, -178]], cfg.scarf ?? '#ffffff', {w: 3, sk: 1});
  scarf.shade([[-12, -180], [6, -172], [38, -174], [24, -184], [0, -186]], 0.45, cfg.scarfShade);
  scarf.line([[8, -198], [14, -176]], {w: 1.6, taper: 0.8}).line([[28, -200], [34, -178]], {w: 1.6, taper: 0.8});
  const tail = new Art(29);
  tail.shape([[-8, -190], [-34, -192], [-62, -186], [-88, -176], [-86, -164], [-60, -170], [-32, -176], [-6, -176]], cfg.scarf ?? '#ffffff', {w: 2.6, sk: 1});
  tail.shade([[-30, -178], [-58, -172], [-84, -168], [-70, -176]], 0.45, cfg.scarfShade);
  tail.line([[-50, -184], [-72, -175]], {w: 1.2, taper: 0.8});
  const head = new Art(30);
  // 圆圆的小脸，朝右
  head.shape([[-16, -236], [-6, -262], [18, -276], [46, -268], [60, -246], [66, -228], [60, -214], [50, -200], [34, -192], [12, -196], [-6, -210], [-16, -224]], C.paper, {w: 3, sk: 1, wobble: 1.3});
  head.shade([[-6, -212], [12, -197], [34, -193], [50, -202], [26, -206], [8, -208]], 0.3);
  head.guide(22, -234, 42, 44, 0.1);
  // 头发：只盖住头顶和后脑，刘海斜着扫过额头
  head.shape([[-20, -232], [-12, -266], [16, -282], [46, -274], [58, -256], [44, -262], [30, -254], [16, -246], [4, -234], [-6, -214], [-17, -216]], cfg.hair, {w: 3, sk: 1});
  head.line([[28, -280], [34, -296], [44, -290]], {w: 2.6, taper: 0.8});
  head.line([[40, -266], [26, -256], [12, -246]], {w: 1.3, taper: 0.8});
  // 脸：大一点的眼睛、眉毛、小鼻子、嘴、腮
  head.fill([[34, -236], [42, -238], [44, -228], [35, -226]], C.ink, 1);
  head.fill([[37, -235], [39.5, -236], [39.5, -233], [37, -233]], '#ffffff', 0.9);
  head.line([[30, -246], [41, -250], [50, -245]], {w: 2, taper: 0.9});
  head.line([[64, -230], [70, -224], [63, -221]], {w: 1.7, taper: 0.6});
  head.line([[46, -208], [54, -211], [57, -208]], {w: 1.6, taper: 0.8});
  head.shape([[2, -234], [11, -238], [16, -227], [7, -220]], C.paper, {w: 1.8});
  head.shade([[40, -224], [54, -226], [54, -214], [42, -213]], 0.28, C.shade);
  const skirt = new Art(31);
  if (cfg.skirt) skirt.shape([[-24, -100], [40, -100], [58, -40], [50, -26], [-34, -26], [-40, -50]], cfg.jacket, {w: 2.6, sk: 1});
  return {
    skirt: skirt.build(), pack: pack.build(), packFlap: packFlap.build(), torso: torso.build(), legN: legN.build(), legF: legF.build(),
    armN: armN.build(), armF: armF.build(), scarf: scarf.build(), tail: tail.build(), head: head.build(),
  };
}

export interface BoyPose {
  lean?: number; head?: number; armN?: number; armF?: number; legN?: number; legF?: number;
  bob?: number; // 上下起伏
}
export interface BoyProps extends BoyPose {
  x?: number; y?: number; s?: number; flip?: boolean;
  walk?: number; // 0~1 走路幅度（自动按帧摆腿）
  wind?: number; // 围巾飘动
  t0?: number;
  showPack?: boolean; showLegs?: boolean; variant?: Variant;
  tilt?: number;
  eyes?: number; // 0 睁眼 → 1 闭眼
  sit?: number; // 0~1 坐下（腿伸向前方）
  hang?: number; // 0~1 被提着：手脚耷拉
  raise?: number; // 0~1 双手高举呼救
  children?: React.ReactNode; // 画在背包里露头的乌龟等（局部坐标）
}

export const Boy: React.FC<BoyProps> = ({x = 0, y = 0, s = 1, flip = false, walk = 0, wind = 1, t0 = 0, lean: leanIn = 0, head = 0, armN: armNIn = 0, armF: armFIn = 0, legN: legNIn = 0, legF: legFIn = 0, bob = 0, showPack = true, showLegs = true, tilt = 0, variant = 'boy', sit = 0, hang = 0, raise = 0, eyes = 0, children}) => {
  const A = get(variant);
  const cfg = V[variant];
  let lean = leanIn, armN = armNIn, armF = armFIn, legN = legNIn, legF = legFIn;
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps + t0;
  const ph = t * 2 * Math.PI * 1.35; // 步频约 1.35Hz
  const sw = Math.sin(ph) * 22 * walk;
  const breathe = Math.sin(t * 2.2) * 0.012;
  const bobY = (-Math.abs(Math.sin(ph)) * 5 * walk) + bob;
  const flail = Math.sin(t * 8.5) * 14 * raise;
  legN += -88 * sit + hang * 10; legF += -84 * sit - hang * 6;
  armN += -40 * sit - raise * 150 + flail + hang * 12; armF += -50 * sit - raise * 160 - flail - hang * 8;
  lean += -3 * sit;
  const flutter = Math.sin(t * 3.1) * 5 * wind + Math.sin(t * 7.3) * 2 * wind;
  return (
    <g transform={`translate(${x} ${y + bobY}) scale(${flip ? -s : s} ${s}) rotate(${tilt}) translate(0 ${sit * 76})`}>
      {showPack && cfg.pack ? (
        <g transform={`rotate(${lean * 0.5} 0 -100)`}>
          <ArtView a={A.pack} filter="wc1" />
          {children}
          <ArtView a={A.packFlap} filter="wc1" />
        </g>
      ) : null}
      {showLegs ? (
        <g transform={`rotate(${legF - sw} 4 -92)`}>
          <ArtView a={A.legF} filter="wc2" />
        </g>
      ) : null}
      <g transform={`rotate(${armF + sw * 0.9} 4 -178)`}>
        <ArtView a={A.armF} filter="wc2" />
      </g>
      <g transform={`rotate(${lean} 8 -90) scale(1 ${1 + breathe})`}>
        {cfg.scarf && variant !== 'dad' && variant !== 'mom' ? (
          <g transform={`rotate(${flutter} -8 -184)`}>
            <ArtView a={A.tail} filter="wc0" />
          </g>
        ) : null}
        {cfg.skirt ? <ArtView a={A.skirt} filter="wc1" /> : null}
        <ArtView a={A.torso} filter="wc0" />
        <ArtView a={A.scarf} filter="wc1" />
        <g transform={`translate(10 -196) scale(${cfg.headK}) translate(-10 196) rotate(${head + Math.sin(t * 1.3) * 1.2} 10 -196)`}>
          <ArtView a={A.head} filter="wc2" />
          {eyes > 0.02 ? (
            <g opacity={Math.min(1, eyes * 1.4)}>
              <ellipse cx={39} cy={-231} rx={9} ry={8} fill={C.paper} />
              <path d="M31 -232 Q39 -226 47 -232" fill="none" stroke={C.ink} strokeWidth={2.4} strokeLinecap="round" />
            </g>
          ) : null}
        </g>
        <g transform={`rotate(${armN - sw * 0.9} 6 -178)`}>
          <ArtView a={A.armN} filter="wc1" />
        </g>
      </g>
      {showLegs ? (
        <g transform={`rotate(${legN + sw} 8 -92)`}>
          <ArtView a={A.legN} filter="wc1" />
        </g>
      ) : null}
    </g>
  );
};
