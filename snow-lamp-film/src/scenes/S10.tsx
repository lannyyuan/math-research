import React, {useMemo} from 'react';
import {Img, staticFile} from 'remotion';
import {Stage, Layer} from '../fx/Stage';
import {LampGlow} from '../fx/Lamp';
import {Boy} from '../chars/Boy';
import {Rabbit} from '../chars/Rabbit';
import {Deer} from '../chars/Deer';
import {Turtle} from '../chars/Turtle';
import {OilLamp} from '../fx/Cabin';
import {Art, rng} from '../art/ink';
import {ArtView} from '../art/ArtView';
import {GroundShadow} from '../fx/Bits';
import {Mountain, SceneWrap, useT, ramp, lerp} from './kit';

// 十、小石头在自己的窗边点灯：划火柴 → 点亮小灯 → 把画着朋友们的画贴在窗上 → 远处山顶也有一点光，一闪一闪 → 他微笑着闭上了眼睛
const FY = 818; // 屋里地板上，脚底的 y
const WX = 690, WY = 160, WW = 400, WH = 450; // 窗洞
const LAMP: [number, number] = [902, 612];

const buildFurniture = () => {
  const frame = new Art(601);
  frame.line([[WX - 14, WY - 14], [WX + WW + 14, WY - 14], [WX + WW + 14, WY + WH + 14], [WX - 14, WY + WH + 14]], {w: 7, closed: true, sk: 1});
  frame.line([[WX + WW / 2, WY - 10], [WX + WW / 2, WY + WH + 10]], {w: 5}).line([[WX - 10, WY + WH / 2 - 20], [WX + WW + 10, WY + WH / 2 - 20]], {w: 5});
  const sill = new Art(602);
  sill.shape([[WX - 50, WY + WH + 12], [WX + WW + 50, WY + WH + 12], [WX + WW + 56, WY + WH + 40], [WX - 56, WY + WH + 40]], '#4a5c97', {w: 3.2, sk: 1});
  sill.shade([[WX - 56, WY + WH + 30], [WX + WW + 56, WY + WH + 30], [WX + WW + 56, WY + WH + 40], [WX - 56, WY + WH + 40]], 0.4, '#1d2760');
  const cl = new Art(603);
  cl.shape([[WX - 150, WY - 40], [WX - 20, WY - 40], [WX - 8, WY + 150], [WX - 40, WY + 330], [WX - 20, WY + WH + 40], [WX - 150, WY + WH + 40]], '#5a74b6', {w: 3, sk: 1});
  cl.shade([[WX - 150, WY + 200], [WX - 40, WY + 330], [WX - 20, WY + WH + 40], [WX - 150, WY + WH + 40]], 0.35, '#1d2760');
  for (const x of [-120, -88, -56]) cl.line([[WX + x, WY - 30], [WX + x + 10, WY + 200], [WX + x - 4, WY + WH + 30]], {w: 1.6, taper: 0.8, broken: 0.2});
  const cr = new Art(604);
  cr.shape([[WX + WW + 150, WY - 40], [WX + WW + 20, WY - 40], [WX + WW + 8, WY + 150], [WX + WW + 40, WY + 330], [WX + WW + 20, WY + WH + 40], [WX + WW + 150, WY + WH + 40]], '#5a74b6', {w: 3, sk: 1});
  cr.shade([[WX + WW + 150, WY + 200], [WX + WW + 40, WY + 330], [WX + WW + 20, WY + WH + 40], [WX + WW + 150, WY + WH + 40]], 0.35, '#1d2760');
  for (const x of [120, 88, 56]) cr.line([[WX + WW + x, WY - 30], [WX + WW + x - 10, WY + 200], [WX + WW + x + 4, WY + WH + 30]], {w: 1.6, taper: 0.8, broken: 0.2});
  // 床
  const bed = new Art(605);
  bed.shape([[1200, 700], [1236, 700], [1236, 872], [1200, 872]], '#27346c', {w: 3});
  bed.shape([[1226, 800], [1860, 800], [1860, 850], [1226, 850]], '#35468a', {w: 3, sk: 1});
  bed.shade([[1226, 836], [1860, 836], [1860, 850], [1226, 850]], 0.4, '#1d2760');
  bed.shape([[1250, 770], [1396, 764], [1410, 800], [1250, 802]], '#f3f7ff', {w: 2.8, sk: 1}); // 枕头
  bed.shade([[1250, 788], [1410, 786], [1410, 800], [1250, 802]], 0.3);
  const blanket = new Art(606);
  blanket.shape([[1360, 806], [1420, 756], [1560, 742], [1700, 748], [1860, 770], [1862, 850], [1360, 850]], '#9db3de', {w: 3.2, sk: 1, wobble: 1.5});
  blanket.shade([[1360, 830], [1600, 820], [1862, 826], [1862, 850], [1360, 850]], 0.34, '#3b4f95');
  blanket.line([[1440, 770], [1520, 790], [1470, 840]], {w: 1.6, taper: 0.8, broken: 0.25}).line([[1620, 756], [1700, 790], [1650, 842]], {w: 1.6, taper: 0.8, broken: 0.25});
  // 挂钩上的红围巾（全片三处暖色之一，这里只有一小条）
  const hook = new Art(607);
  hook.line([[300, 500], [300, 520]], {w: 4});
  hook.shape([[286, 520], [316, 520], [322, 640], [300, 660], [280, 640]], '#c8323e', {w: 2.8});
  // 画：纸上三个朋友
  const paper = new Art(608);
  paper.shape([[0, 0], [130, -4], [134, 170], [-2, 172]], '#f8faff', {w: 2.8, sk: 1, wobble: 1.2});
  return {frame: frame.build(), sill: sill.build(), cl: cl.build(), cr: cr.build(), bed: bed.build(), blanket: blanket.build(), hook: hook.build(), paper: paper.build()};
};

export const S10: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const A = useMemo(buildFurniture, []);
  const drops = useMemo(() => {
    const r = rng(77);
    return Array.from({length: 16}, () => ({x: WX + 14 + r() * (WW - 28), y: WY + 14 + r() * (WH - 40), r: 3 + r() * 5, sp: 3 + r() * 6}));
  }, []);
  const streaks = useMemo(() => {
    const r = rng(78);
    return Array.from({length: 26}, () => ({x: WX + r() * WW, y: r() * 600, l: 26 + r() * 40, sp: 420 + r() * 260}));
  }, []);
  // —— 镜头：先看小石头和窗，再看窗外的光，再看他睡着，最后回到窗边的灯 ——
  const win = ramp(t, 14.4, 16.4) * (1 - ramp(t, 21.8, 23.6));
  const bedC = ramp(t, 22.0, 24.0) * (1 - ramp(t, 26.0, 27.6));
  let cx = lerp(960, 905, ramp(t, 0, 8)), cy = lerp(540, 520, ramp(t, 0, 8)), cz = lerp(1.0, 1.1, ramp(t, 0, 8));
  cx = lerp(cx, 902, win); cy = lerp(cy, 440, win); cz = lerp(cz, 1.65, win);
  cx = lerp(cx, 1470, bedC); cy = lerp(cy, 770, bedC); cz = lerp(cz, 2.2, bedC);
  const back = ramp(t, 26.0, 27.8);
  cx = lerp(cx, 902, back); cy = lerp(cy, 500, back); cz = lerp(cz, 1.5, back);
  const cam = {x: cx - 960, y: cy - 540, z: cz};
  // —— 火柴与小灯 ——
  const match = ramp(t, 1.8, 2.4) * (1 - ramp(t, 3.4, 3.8));
  const flame = ramp(t, 3.2, 4.8);
  const lit = ramp(t, 3.2, 5.6);
  // —— 小石头 ——
  const toBed = ramp(t, 12.4, 14.6);
  const lay = ramp(t, 14.6, 15.6);
  const bx = t < 12.4 ? 832 : lerp(832, 1300, toBed);
  const walk = ramp(t, 12.4, 13.0) * (1 - ramp(t, 14.0, 14.6)) * 0.8;
  const armUp = ramp(t, 1.4, 2.0) * (1 - ramp(t, 3.8, 4.4)) * 130 + ramp(t, 5.8, 6.6) * (1 - ramp(t, 9.0, 9.8)) * 80;
  const paperIn = ramp(t, 6.0, 7.0);
  const paperFly = ramp(t, 8.2, 9.6);
  const px = lerp(bx + 38, 736, paperFly), py = lerp(FY - 160, 330, paperFly);
  const paperOn = t >= 6.0;
  const eyes = ramp(t, 24.0, 25.4);
  const head = t < 1.6 ? -4 : t > 6 && t < 12 ? -8 : 0;
  // —— 妈妈 ——
  const momVis = ramp(t, 4.0, 5.0) * (1 - ramp(t, 13.2, 14.4));
  return (
    <SceneWrap len={len}>
      <Stage cam={cam}>
        {/* 窗外：雨夜、远处的山，山顶那一点光 */}
        <Layer p={0.9}>
          <Img src={staticFile('baked/sky-night.jpg')} style={{position: 'absolute', left: -192, top: -160, width: 2304, height: 900}} />
          <Mountain cx={905} baseY={590} k={0.3} tone="night" />
          <div style={{position: 'absolute', left: 640, top: 540, width: 520, height: 120, background: 'linear-gradient(#0f1a44, #1a2a66)'}} />
          <Img src={staticFile('baked/trees-far.png')} style={{position: 'absolute', left: 90, top: 410, width: 1700, height: 210, opacity: 0.95}} />
        </Layer>
        <Layer p={0.9}>
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <LampGlow x={905} y={339 + 20} r={4.6} glow={0.9} t0={0.5} />
          </svg>
        </Layer>
        <Layer p={1}>
          <Img src={staticFile('baked/room.png')} style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080}} />
          <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
            <defs>
              <clipPath id="winClip"><rect x={WX} y={WY} width={WW} height={WH} /></clipPath>
              <radialGradient id="roomGlow">
                <stop offset="0" stopColor="#ffcb62" stopOpacity={0.55} />
                <stop offset="0.5" stopColor="#ff9d3a" stopOpacity={0.16} />
                <stop offset="1" stopColor="#ff9d3a" stopOpacity={0} />
              </radialGradient>
            </defs>
            {/* 窗玻璃：雨丝 + 水汽凝成的小水珠 */}
            <g clipPath="url(#winClip)">
              <rect x={WX} y={WY} width={WW} height={WH} fill="#c9d9f5" opacity={0.08} />
              {streaks.map((s, i) => {
                const y = ((s.y + t * s.sp) % (WH + 120)) - 60 + WY;
                return <line key={i} x1={s.x} y1={y} x2={s.x - s.l * 0.22} y2={y + s.l} stroke="#e4eeff" strokeWidth={1.6} opacity={0.38} />;
              })}
              {drops.map((d, i) => {
                const y = WY + 14 + ((d.y - WY - 14 + t * d.sp) % (WH - 30));
                return (
                  <g key={i}>
                    <ellipse cx={d.x} cy={y} rx={d.r} ry={d.r * 1.25} fill="#dce8ff" opacity={0.3} />
                    <ellipse cx={d.x - d.r * 0.3} cy={y - d.r * 0.4} rx={d.r * 0.3} ry={d.r * 0.4} fill="#ffffff" opacity={0.7} />
                  </g>
                );
              })}
            </g>
            <ArtView a={A.cl} filter="wc2" />
            <ArtView a={A.cr} filter="wc2" />
            <ArtView a={A.frame} filter="wc1" sk={0.35} />
            <ArtView a={A.sill} filter="wc1" />
            {/* 小灯：点亮后，暖光洒在窗台、墙和画上 */}
            <ellipse cx={LAMP[0]} cy={LAMP[1] - 20} rx={560 * lit} ry={420 * lit} fill="url(#roomGlow)" opacity={0.95} />
            <OilLamp x={LAMP[0]} y={LAMP[1]} s={0.36} flame={flame * (0.9 + 0.1 * Math.sin(t * 7))} />
            <LampGlow x={LAMP[0]} y={LAMP[1] - 38} r={9} glow={lit * 0.9} rays={false} />
            {/* 床 */}
            <ArtView a={A.bed} filter="wc1" />
            {/* 门口的妈妈 */}
            <g opacity={momVis}>
              <rect x={70} y={300} width={200} height={FY - 288} fill="#0f1740" opacity={0.7} />
              <GroundShadow x={170} y={FY + 6} rx={70} />
              <g transform={`translate(170 ${FY - 6})`}><Boy x={0} y={0} s={1.0} variant="mom" head={t > 11 && t < 13 ? 6 : 0} armN={t > 10.5 && t < 13 ? -60 + Math.sin(t * 6) * 14 : -8} wind={0} /></g>
            </g>
            {/* 小石头 */}
            {lay < 0.5 ? (
              <g>
                <GroundShadow x={bx} y={FY + 6} rx={70} o={1 - lay * 2} />
                <g transform={`translate(${bx} ${FY - lay * 40}) rotate(${-90 * lay})`}>
                  <Boy x={0} y={0} s={0.85} walk={walk} armN={-armUp} head={head} variant="boy" wind={0.2} eyes={eyes} />
                </g>
              </g>
            ) : (
              <g transform={`translate(1568 ${790}) rotate(-90)`}>
                <Boy x={0} y={0} s={0.85} variant="boy" showLegs head={4} eyes={eyes} wind={0} showPack={false} />
              </g>
            )}
            <ArtView a={A.blanket} filter="wc1" />
            {/* 火柴 */}
            {match > 0.02 ? (
              <g opacity={match} transform={`translate(${bx + 52} ${FY - 188}) rotate(${-30})`}>
                <line x1={0} y1={0} x2={22} y2={0} stroke="#1a1f3f" strokeWidth={3} strokeLinecap="round" />
                <ellipse cx={-5} cy={0} rx={7} ry={4.5} fill="#ff9f40" />
                <ellipse cx={-5} cy={0} rx={3.6} ry={2.4} fill="#fff0b8" />
              </g>
            ) : null}
            {/* 画着问号、慢慢和白鹿的画 */}
            {paperOn ? (
              <g transform={`translate(${paperFly > 0 ? px : bx + 36} ${paperFly > 0 ? py : FY - 168}) rotate(${lerp(-8, -3, paperFly)}) scale(${lerp(0.9, 0.78, paperFly)})`} opacity={paperIn}>
                <ArtView a={A.paper} filter="wc2" />
                <g transform="translate(24 128)"><Rabbit x={0} y={0} s={0.2} perk={0.5} t0={1} /></g>
                <g transform="translate(66 128)"><Turtle x={0} y={0} s={0.13} flip t0={1} /></g>
                <g transform="translate(106 128)"><Deer x={0} y={0} s={0.1} flip leaves={1} t0={1} /></g>
              </g>
            ) : null}
          </svg>
        </Layer>
      </Stage>
      <div style={{position: 'absolute', inset: 0, background: `rgba(4,7,26,${0.55 * (1 - lit)})`, pointerEvents: 'none'}} />
    </SceneWrap>
  );
};
