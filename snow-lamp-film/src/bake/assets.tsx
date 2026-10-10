// 离线烘焙的大面积水彩层（天空、纸纹、树林剪影、雪地）。
// 每帧都现算全屏的 SVG 滤镜太慢，所以这些静态层先渲成图片，放进 public/baked/，影片里只做移动/缩放。
//   npm run bake        （= node scripts/bake.mjs）
import React from 'react';
import {C} from '../palette';
import {rng, vnoise, type P} from '../art/ink';

export interface Asset {
  w: number;
  h: number;
  format: 'png' | 'jpeg';
  Comp: React.FC;
}

const grain = (id: string, freq: string, oct: number, seed: number, matrix: string, extra?: React.ReactNode) => (
  <filter id={id} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency={freq} numOctaves={oct} seed={seed} />
    <feColorMatrix type="matrix" values={matrix} />
    {extra}
  </filter>
);

/** 天空：深靛蓝渐变 + 水彩的深浅斑驳 + 横向笔触 + 颗粒 */
const Sky: React.FC<{top: string; mid: string; low: string; haze: string; light?: boolean; seed?: number}> = ({top, mid, low, haze, light = false, seed = 3}) => {
  const W = 2304, H = 900;
  const hi = light ? '255 255 255' : '120 150 215';
  const [hr, hg, hb] = hi.split(' ').map((v) => (+v / 255).toFixed(3));
  const dk = light ? ['0.45', '0.62', '0.78'] : ['0.02', '0.04', '0.16'];
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      <defs>
        <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={top} />
          <stop offset="0.5" stopColor={mid} />
          <stop offset="0.82" stopColor={low} />
          <stop offset="1" stopColor={haze} />
        </linearGradient>
        {/* 浅色大斑块（颜料浮起） */}
        {grain('lightBlot', '0.0016 0.0034', 4, seed, `0 0 0 0 ${hr}  0 0 0 0 ${hg}  0 0 0 0 ${hb}  2.3 0 0 0 -0.98`)}
        {/* 深色大斑块（颜料沉积） */}
        {grain('darkBlot', '0.0022 0.0042', 4, seed + 5, `0 0 0 0 ${dk[0]}  0 0 0 0 ${dk[1]}  0 0 0 0 ${dk[2]}  -2.3 0 0 0 1.32`)}
        {/* 横向干笔触 */}
        {grain('streak', '0.0009 0.03', 3, seed + 9, `0 0 0 0 ${hr}  0 0 0 0 ${hg}  0 0 0 0 ${hb}  1.9 0 0 0 -0.86`)}
        {grain('streakD', '0.0012 0.045', 3, seed + 14, `0 0 0 0 ${dk[0]}  0 0 0 0 ${dk[1]}  0 0 0 0 ${dk[2]}  -1.9 0 0 0 1.12`)}
        {grain('paperGrain', '0.6', 2, seed + 2, `0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  1.6 0 0 0 -0.78`)}
      </defs>
      <rect width={W} height={H} fill="url(#sg)" />
      <rect width={W} height={H} filter="url(#lightBlot)" opacity={0.2} />
      <rect width={W} height={H} filter="url(#darkBlot)" opacity={0.32} />
      <rect width={W} height={H} filter="url(#streak)" opacity={0.07} />
      <rect width={W} height={H} filter="url(#streakD)" opacity={0.08} />
      <rect width={W} height={H} filter="url(#paperGrain)" opacity={light ? 0.1 : 0.07} />
    </svg>
  );
};

/** 纸张纹理：用 overlay 叠在全片上。中灰为底，有细颗粒、纤维、轻微四角压暗 */
const Paper: React.FC = () => {
  const W = 1920, H = 1080;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      <defs>
        <filter id="pg" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={3} seed={21} result="n" />
          <feColorMatrix in="n" type="matrix" values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 0 1" />
        </filter>
        <filter id="fib" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.28" numOctaves={3} seed={8} result="n" />
          <feColorMatrix in="n" type="matrix" values="0.5 0.5 0 0 0  0.5 0.5 0 0 0  0.5 0.5 0 0 0  0 0 0 0 1" />
        </filter>
        <filter id="fib2" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.3 0.01" numOctaves={3} seed={17} result="n" />
          <feColorMatrix in="n" type="matrix" values="0.5 0.5 0 0 0  0.5 0.5 0 0 0  0.5 0.5 0 0 0  0 0 0 0 1" />
        </filter>
        <filter id="cloud" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.003" numOctaves={3} seed={33} result="n" />
          <feColorMatrix in="n" type="matrix" values="0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0.33 0.33 0.33 0 0  0 0 0 0 1" />
        </filter>
        <radialGradient id="vig" cx="0.5" cy="0.5" r="0.75">
          <stop offset="0.55" stopColor="#808080" stopOpacity={0} />
          <stop offset="1" stopColor="#5e6580" stopOpacity={0.55} />
        </radialGradient>
      </defs>
      <rect width={W} height={H} fill="#808080" />
      <rect width={W} height={H} filter="url(#cloud)" opacity={0.4} />
      <rect width={W} height={H} filter="url(#pg)" opacity={0.4} />
      <rect width={W} height={H} filter="url(#fib)" opacity={0.12} style={{mixBlendMode: 'overlay'}} />
      <rect width={W} height={H} fill="url(#vig)" />
    </svg>
  );
};

/** 冷杉剪影林带。near=true 更高更深；haze 让根部融进雾里 */
const Trees: React.FC<{seed: number; w: number; h: number; color: string; minH: number; maxH: number; gap: number; blur: number; haze?: boolean; fade?: number}> = ({seed, w, h, color, minH, maxH, gap, blur, haze = true, fade = 0.9}) => {
  const r = rng(seed);
  const trees: string[] = [];
  let x = -40 + r() * 30;
  while (x < w + 60) {
    const th = minH + r() * (maxH - minH);
    const tw = th * (0.3 + r() * 0.14);
    const base = h - 6;
    const tiers = 4 + Math.floor(r() * 3);
    const pts: P[] = [[x, base - th]];
    for (let i = 1; i <= tiers; i++) {
      const u = i / tiers;
      const yy = base - th + th * Math.pow(u, 0.92);
      const ww = (tw / 2) * Math.pow(u, 0.8) * (0.9 + r() * 0.2);
      pts.push([x + ww, yy]);
      if (i < tiers) pts.push([x + ww * 0.42, yy - th * 0.045]);
    }
    pts.push([x + tw * 0.07, base], [x + tw * 0.07, base + 20], [x - tw * 0.07, base + 20], [x - tw * 0.07, base]);
    for (let i = tiers; i >= 1; i--) {
      const u = i / tiers;
      const yy = base - th + th * Math.pow(u, 0.92);
      const ww = (tw / 2) * Math.pow(u, 0.8) * (0.9 + r() * 0.2);
      if (i < tiers) pts.push([x - ww * 0.42, yy - th * 0.045]);
      pts.push([x - ww, yy]);
    }
    trees.push('M' + pts.map((p) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join('L') + 'Z');
    x += gap * (0.45 + r() * 1.1);
  }
  const n = vnoise(seed);
  const ridge = Array.from({length: Math.ceil(w / 60) + 2}, (_, i) => `${i * 60} ${(h - minH * 0.55 - (n(i * 0.35) + 1) * minH * 0.18).toFixed(1)}`);
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <filter id="tf" x="-2%" y="-5%" width="104%" height="110%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency={0.03} numOctaves={3} seed={seed} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={14} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={blur} result="b" />
          <feTurbulence type="fractalNoise" baseFrequency={0.07} numOctaves={3} seed={seed + 3} result="g" />
          <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.9 0 0 0 0.52" result="gA" />
          <feComposite in="b" in2="gA" operator="in" />
        </filter>
        <linearGradient id="mist" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#fff" />
          <stop offset="0.55" stopColor="#fff" />
          <stop offset="1" stopColor="#000" />
        </linearGradient>
        <mask id="mistMask"><rect width={w} height={h} fill="url(#mist)" /></mask>
      </defs>
      <g mask={haze ? 'url(#mistMask)' : undefined}>
        <g filter="url(#tf)" opacity={fade}>
          <path d={`M-20 ${h + 10}L${ridge.join('L')}L${w + 40} ${h + 10}Z`} fill={color} opacity={0.95} />
          {trees.map((d, i) => (
            <path key={i} d={d} fill={color} />
          ))}
        </g>
      </g>
    </svg>
  );
};

/** 雪地：近处白，远处带蓝灰；起伏的雪丘 + 淡淡的蓝灰阴影 */
const Snow: React.FC<{w: number; h: number; seed: number; amp?: number; shade?: number; tint?: string}> = ({w, h, seed, amp = 22, shade = 1, tint}) => {
  const n1 = vnoise(seed), n2 = vnoise(seed + 9);
  const top = 40;
  const ridge = Array.from({length: Math.ceil(w / 40) + 2}, (_, i) => {
    const x = i * 40;
    return [x, top + amp * n1(x / 520) + amp * 0.4 * n2(x / 170)] as P;
  });
  const ridgeD = ridge.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1].toFixed(1)}`).join('');
  const r = rng(seed + 4);
  const patches = Array.from({length: 14}, () => {
    const x = r() * w, y = top + 40 + r() * (h - top - 80);
    return {x, y, rx: 160 + r() * 420, ry: 10 + r() * 26};
  });
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <linearGradient id="sn" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={tint ?? '#b3c3e3'} />
          <stop offset="0.18" stopColor="#d9e4f4" />
          <stop offset="0.5" stopColor={C.snow} />
          <stop offset="1" stopColor={C.snowLit} />
        </linearGradient>
        <filter id="sw" x="-5%" y="-20%" width="110%" height="140%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.006 0.02" numOctaves={3} seed={seed} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={40} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={6} />
        </filter>
        <filter id="edge" x="-2%" y="-30%" width="104%" height="160%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves={3} seed={seed + 2} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={12} xChannelSelector="R" yChannelSelector="G" />
        </filter>
        <filter id="grainS" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.0035 0.012" numOctaves={4} seed={seed + 6} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.45  0 0 0 0 0.55  0 0 0 0 0.78  -2.2 0 0 0 1.0" />
        </filter>
        <clipPath id="gclip"><path d={`${ridgeD}L${w + 40} ${h}L-40 ${h}Z`} /></clipPath>
      </defs>
      <g filter="url(#edge)">
        <path d={`${ridgeD}L${w + 40} ${h}L-40 ${h}Z`} fill="url(#sn)" />
      </g>
      <g clipPath="url(#gclip)">
        {patches.map((p, i) => (
          <ellipse key={i} cx={p.x} cy={p.y} rx={p.rx} ry={p.ry} fill={C.snowDeep} opacity={0.13 * shade} filter="url(#sw)" />
        ))}
        <rect width={w} height={h} filter="url(#grainS)" opacity={0.2 * shade} />
        <path d={ridgeD} stroke={C.snowShade} strokeWidth={14} fill="none" opacity={0.5 * shade} filter="url(#sw)" />
      </g>
    </svg>
  );
};


/** 远山：尖尖的山顶（灯就挂在山顶），迎光面浅、背光面深，山脚融进雾里。山顶在图中 (1700, 62) */
const Mount: React.FC<{tone?: 'night' | 'dawn'}> = ({tone = 'night'}) => {
  const w = 3400, h = 800;
  const night = tone === 'night';
  const mass = night ? '#243b7a' : '#7f9fc4';
  const lit = night ? '#6f8bc4' : '#dbe8f4';
  const dark = night ? '#17265e' : '#5f81ad';
  const farC = night ? '#273d7c' : '#a9c3dc';
  const n = vnoise(77), n2 = vnoise(31);
  const raw: P[] = [[-40, 800], [-40, 700], [300, 650], [620, 562], [900, 500], [1150, 404], [1380, 272], [1530, 172], [1620, 110], [1700, 62], [1782, 112], [1880, 222], [2050, 332], [2300, 402], [2600, 520], [2950, 622], [3440, 690], [3440, 800]];
  const pts = raw.map((p, i) => [p[0] + n(i * 0.7) * 12, p[1] + (i > 0 && i < raw.length - 2 ? n2(i * 0.9) * 14 : 0)] as P);
  const D = 'M' + pts.map((p) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join('L') + 'Z';
  const farRidge = 'M-40 800L-40 600L260 540L520 470L820 410L1100 330L1300 300L1500 330L1860 380L2200 300L2500 360L2800 440L3100 470L3440 520L3440 800Z';
  const litFace = 'M1700 62L1620 110L1530 172L1380 272L1240 372L1420 360L1520 300L1580 250L1640 200L1690 150Z';
  const darkFace = 'M1700 62L1782 112L1880 222L2050 332L2300 402L2020 410L1880 330L1800 250L1740 170Z';
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <filter id="mf" x="-2%" y="-5%" width="104%" height="110%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency={0.012} numOctaves={3} seed={6} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={26} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={1.6} result="b" />
          <feTurbulence type="fractalNoise" baseFrequency={0.05} numOctaves={3} seed={9} result="g" />
          <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.5 0 0 0 0.8" result="gA" />
          <feComposite in="b" in2="gA" operator="in" />
        </filter>
        <linearGradient id="mfade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#fff" />
          <stop offset="0.62" stopColor="#fff" />
          <stop offset="1" stopColor="#000" />
        </linearGradient>
        <mask id="mmask"><rect width={w} height={h} fill="url(#mfade)" /></mask>
      </defs>
      <g mask="url(#mmask)">
        <g filter="url(#mf)">
          <path d={farRidge} fill={farC} opacity={0.7} />
          <path d={D} fill={mass} />
          <path d={litFace} fill={lit} opacity={0.26} />
          <path d={darkFace} fill={dark} opacity={0.6} />
        </g>
      </g>
    </svg>
  );
};

/** 画面两侧的近景冷杉剪影（压在最前面，做“框”，很深很暗） */
const FrameTrees: React.FC = () => {
  const w = 3000, h = 1000;
  const r = rng(61);
  const mk = (x: number, th: number, tw: number) => {
    const base = h - 4, tiers = 6;
    const pts: P[] = [[x, base - th]];
    for (let i = 1; i <= tiers; i++) {
      const u = i / tiers, yy = base - th + th * Math.pow(u, 0.92), ww = (tw / 2) * Math.pow(u, 0.8) * (0.92 + r() * 0.16);
      pts.push([x + ww, yy]);
      if (i < tiers) pts.push([x + ww * 0.4, yy - th * 0.04]);
    }
    pts.push([x + tw * 0.06, base + 30], [x - tw * 0.06, base + 30]);
    for (let i = tiers; i >= 1; i--) {
      const u = i / tiers, yy = base - th + th * Math.pow(u, 0.92), ww = (tw / 2) * Math.pow(u, 0.8) * (0.92 + r() * 0.16);
      if (i < tiers) pts.push([x - ww * 0.4, yy - th * 0.04]);
      pts.push([x - ww, yy]);
    }
    return 'M' + pts.map((p) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join('L') + 'Z';
  };
  const list = [mk(250, 980, 380), mk(500, 640, 250), mk(110, 700, 240), mk(2780, 940, 360), mk(2520, 560, 230)];
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <filter id="ff" x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency={0.03} numOctaves={3} seed={12} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={18} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={1.1} result="b" />
          <feTurbulence type="fractalNoise" baseFrequency={0.08} numOctaves={3} seed={4} result="g" />
          <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0.6 0 0 0 0.72" result="gA" />
          <feComposite in="b" in2="gA" operator="in" />
        </filter>
      </defs>
      <g filter="url(#ff)">
        {list.map((d, i) => (
          <path key={i} d={d} fill={i % 2 ? '#0c1438' : '#080e2c'} />
        ))}
      </g>
    </svg>
  );
};

/** 结冰的池塘：淡蓝的冰面、一道道高光、岸边的雪 */
const Pond: React.FC = () => {
  const w = 1600, h = 380;
  const rim: P[] = Array.from({length: 40}, (_, i) => {
    const a = (i / 40) * Math.PI * 2;
    const k = 1 + 0.05 * Math.sin(a * 3 + 1) + 0.04 * Math.sin(a * 5);
    return [w / 2 + Math.cos(a) * 700 * k, h / 2 + Math.sin(a) * 140 * k] as P;
  });
  const D = 'M' + rim.map((p) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join('L') + 'Z';
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <radialGradient id="ice" cx="0.5" cy="0.38" r="0.6">
          <stop offset="0" stopColor="#eaf4fc" />
          <stop offset="0.6" stopColor="#c3dcf0" />
          <stop offset="1" stopColor="#8fb1d6" />
        </radialGradient>
        <filter id="pf" x="-5%" y="-10%" width="110%" height="120%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency={0.012} numOctaves={3} seed={3} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={22} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={1.2} />
        </filter>
        <filter id="pg2" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.004 0.04" numOctaves={3} seed={11} />
          <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.4 0 0 0 -1.1" />
        </filter>
        <clipPath id="pc"><path d={D} /></clipPath>
      </defs>
      <g filter="url(#pf)">
        <path d={D} fill={C.snowShade} transform="translate(0 10)" opacity={0.7} />
        <path d={D} fill="url(#ice)" />
      </g>
      <g clipPath="url(#pc)">
        <rect width={w} height={h} filter="url(#pg2)" opacity={0.55} />
        <path d="M200 190C420 150 640 210 900 170S1300 200 1420 170" stroke="#ffffff" strokeWidth={5} fill="none" opacity={0.55} strokeLinecap="round" />
        <path d="M360 232C560 216 760 244 980 226" stroke="#ffffff" strokeWidth={3.5} fill="none" opacity={0.45} strokeLinecap="round" />
        <path d="M980 120C1100 108 1220 130 1340 116" stroke="#ffffff" strokeWidth={3} fill="none" opacity={0.5} strokeLinecap="round" />
      </g>
    </svg>
  );
};

/** 结冰的河：从远处蜿蜒到近处，越近越宽。河面是淡蓝的冰，两岸是雪。资产里 (0,0) 在地平线上 */
const River: React.FC = () => {
  const w = 1700, h = 540;
  // 左右岸线（资产坐标）：y -> [左, 右]
  const L: P[] = [[860, 0], [820, 100], [740, 210], [630, 330], [470, 540]];
  const R: P[] = [[930, 0], [980, 100], [1060, 210], [1190, 330], [1400, 540]];
  const edge = (pts: P[]) => pts.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1]}`).join('');
  const D = edge(L) + 'L' + R.slice().reverse().map((p) => `${p[0]} ${p[1]}`).join('L') + 'Z';
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <linearGradient id="rice" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#a9c4e2" />
          <stop offset="0.45" stopColor="#d4e6f6" />
          <stop offset="1" stopColor="#bcd6ee" />
        </linearGradient>
        <filter id="rf" x="-5%" y="-5%" width="110%" height="110%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency={0.012} numOctaves={3} seed={5} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={16} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={1.3} />
        </filter>
        <filter id="rg" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.006 0.05" numOctaves={3} seed={13} />
          <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.6 0 0 0 -1.2" />
        </filter>
        <clipPath id="rc"><path d={D} /></clipPath>
        <linearGradient id="rfade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#000" />
          <stop offset="0.14" stopColor="#fff" />
          <stop offset="1" stopColor="#fff" />
        </linearGradient>
        <mask id="rmask"><rect width={w} height={h} fill="url(#rfade)" /></mask>
      </defs>
      <g mask="url(#rmask)">
      <g filter="url(#rf)">
        <path d={D} fill={C.snowShade} transform="translate(0 8)" opacity={0.6} />
        <path d={D} fill="url(#rice)" />
      </g>
      <g clipPath="url(#rc)">
        <rect width={w} height={h} filter="url(#rg)" opacity={0.6} />
        <path d="M880 20C860 120 800 200 730 300S600 450 540 530" stroke="#fff" strokeWidth={5} fill="none" opacity={0.5} strokeLinecap="round" />
        <path d="M960 40C990 130 1040 230 1100 330S1220 470 1280 530" stroke="#fff" strokeWidth={4} fill="none" opacity={0.45} strokeLinecap="round" />
        <path d="M900 200C960 240 1020 250 1090 270" stroke="#fff" strokeWidth={3} fill="none" opacity={0.5} strokeLinecap="round" />
        <path d="M0 0" />
      </g>
      </g>
    </svg>
  );
};

/** 山洞：深靛蓝的岩壁，中间一个拱形洞口（透出外面的雪夜），下面是冷灰蓝的石头地面 */
const Cave: React.FC = () => {
  const w = 1920, h = 1080;
  const n = vnoise(42), n2 = vnoise(17);
  const arch: P[] = [];
  const N = 36;
  for (let i = 0; i <= N; i++) {
    const a = Math.PI + (i / N) * Math.PI; // 上半圆
    const k = 1 + 0.045 * n(i * 0.55) + 0.03 * n2(i * 1.3);
    arch.push([960 + Math.cos(a) * 590 * k, 700 + Math.sin(a) * 590 * 0.98 * k + n2(i) * 10] as P);
  }
  arch.unshift([360, 760]);
  arch.push([1560, 760]);
  const D = 'M' + arch.map((p) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join('L') + 'Z';
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <linearGradient id="rockG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#0a1030" />
          <stop offset="0.55" stopColor="#141d4a" />
          <stop offset="1" stopColor="#1c2858" />
        </linearGradient>
        <linearGradient id="floorG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#34457f" />
          <stop offset="0.5" stopColor="#222f65" />
          <stop offset="1" stopColor="#141d4a" />
        </linearGradient>
        <filter id="blotchL" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.004 0.007" numOctaves={4} seed={21} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.45  0 0 0 0 0.8  2.4 0 0 0 -1.05" />
        </filter>
        <filter id="blotchD" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.006 0.01" numOctaves={4} seed={29} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.02  0 0 0 0 0.03  0 0 0 0 0.12  -2.4 0 0 0 1.25" />
        </filter>
        <filter id="edgeW" x="-5%" y="-5%" width="110%" height="110%">
          <feTurbulence type="fractalNoise" baseFrequency={0.03} numOctaves={3} seed={8} result="n" />
          <feDisplacementMap in="SourceGraphic" in2="n" scale={26} xChannelSelector="R" yChannelSelector="G" />
        </filter>
        <mask id="holeMask">
          <rect width={w} height={h} fill="#fff" />
          <g filter="url(#edgeW)"><path d={D} fill="#000" /></g>
        </mask>
        <clipPath id="floorClip"><rect x={0} y={700} width={w} height={h - 700} /></clipPath>
      </defs>
      <g mask="url(#holeMask)">
        <rect width={w} height={h} fill="url(#rockG)" />
        <rect width={w} height={h} filter="url(#blotchL)" opacity={0.55} />
        <rect width={w} height={h} filter="url(#blotchD)" opacity={0.6} />
      </g>
      {/* 洞口边缘的冷色轮廓光 */}
      <g filter="url(#edgeW)" opacity={0.7}>
        <path d={D} fill="none" stroke="#7d96d2" strokeWidth={5} strokeLinejoin="round" opacity={0.55} />
        <path d={D} fill="none" stroke="#c9d8f6" strokeWidth={1.8} opacity={0.5} transform="translate(0 4)" />
      </g>
      {/* 地面 */}
      <g clipPath="url(#floorClip)">
        <g filter="url(#edgeW)">
          <rect x={-20} y={716} width={w + 40} height={h} fill="url(#floorG)" />
        </g>
        <rect x={0} y={700} width={w} height={h - 700} filter="url(#blotchL)" opacity={0.5} />
        <ellipse cx={960} cy={880} rx={760} ry={110} fill="#4a5c97" opacity={0.18} />
      </g>
    </svg>
  );
};

/** 春天的草地：和雪地同一条山脊线。cover=雪还盖着多少（1 全是雪 → 0 全绿），cover 小时开满白色小花 */
const Spring: React.FC<{cover: number; seed: number}> = ({cover, seed}) => {
  const w = 3400, h = 700, amp = 22, top = 40;
  const n1 = vnoise(2), n2 = vnoise(2 + 9);
  const ridge = Array.from({length: Math.ceil(w / 40) + 2}, (_, i) => {
    const x = i * 40;
    return [x, top + amp * n1(x / 520) + amp * 0.4 * n2(x / 170)] as P;
  });
  const ridgeD = ridge.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1].toFixed(1)}`).join('');
  const r = rng(seed);
  const patches = Array.from({length: 34}, () => ({x: r() * w, y: top + 20 + r() * (h - top - 60), rx: 90 + r() * 330, ry: 16 + r() * 46}));
  const blades = Array.from({length: 260}, () => {
    const x = r() * w, y = top + 30 + r() * (h - top - 50), hh = 8 + r() * 16;
    return `M${x.toFixed(0)} ${y.toFixed(0)}q${(r() * 6 - 3).toFixed(1)} ${(-hh * 0.6).toFixed(1)} ${(r() * 8 - 4).toFixed(1)} ${(-hh).toFixed(1)}`;
  });
  const flowers = cover < 0.3 ? Array.from({length: 70}, () => ({x: r() * w, y: top + 50 + r() * (h - top - 90), s: 0.6 + r() * 0.9, c: r() < 0.75 ? '#fbfdff' : '#d8c9ee'})) : [];
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <linearGradient id="gr" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#93cdb6" />
          <stop offset="0.25" stopColor="#6fb69e" />
          <stop offset="1" stopColor="#3f8a80" />
        </linearGradient>
        <filter id="edge2" x="-2%" y="-30%" width="104%" height="160%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves={3} seed={4} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={12} xChannelSelector="R" yChannelSelector="G" />
        </filter>
        <filter id="rag" x="-10%" y="-40%" width="120%" height="180%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.012 0.03" numOctaves={3} seed={seed} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={46} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={2} />
        </filter>
        <filter id="gb" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.004 0.014" numOctaves={4} seed={seed + 3} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.13  0 0 0 0 0.36  0 0 0 0 0.36  -2.2 0 0 0 1.05" />
        </filter>
        <filter id="gl" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.005 0.016" numOctaves={4} seed={seed + 8} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.75  0 0 0 0 0.95  0 0 0 0 0.8  2.4 0 0 0 -1.1" />
        </filter>
        <clipPath id="gc2"><path d={`${ridgeD}L${w + 40} ${h}L-40 ${h}Z`} /></clipPath>
      </defs>
      <g filter="url(#edge2)">
        <path d={`${ridgeD}L${w + 40} ${h}L-40 ${h}Z`} fill="url(#gr)" />
      </g>
      <g clipPath="url(#gc2)">
        <rect width={w} height={h} filter="url(#gb)" opacity={0.5} />
        <rect width={w} height={h} filter="url(#gl)" opacity={0.4} />
        <path d={blades.join('')} stroke="#2f7068" strokeWidth={2.2} fill="none" opacity={0.55} strokeLinecap="round" />
        {cover > 0.02
          ? patches.map((p, i) => (
              <g key={i} filter="url(#rag)">
                <ellipse cx={p.x} cy={p.y} rx={p.rx * cover * 1.25} ry={p.ry * cover * 1.25} fill="#2d5b66" opacity={0.28} transform="translate(2 6)" />
                <ellipse cx={p.x} cy={p.y} rx={p.rx * cover * 1.2} ry={p.ry * cover * 1.2} fill="#f6f9fe" />
                <ellipse cx={p.x} cy={p.y + p.ry * cover * 0.35} rx={p.rx * cover * 1.0} ry={p.ry * cover * 0.6} fill="#b6c7e6" opacity={0.5} />
              </g>
            ))
          : null}
        {flowers.map((f, i) => (
          <g key={i} transform={`translate(${f.x} ${f.y}) scale(${f.s})`}>
            {[0, 1, 2, 3, 4].map((k) => (
              <ellipse key={k} cx={0} cy={-7} rx={4.2} ry={6.4} fill={f.c} transform={`rotate(${k * 72})`} stroke="#9aaed6" strokeWidth={0.8} />
            ))}
            <circle r={2.6} fill="#c9d6f4" />
          </g>
        ))}
      </g>
    </svg>
  );
};

/** 山坡：雪地从左下爬到右上，到 x≈1550 变成平台。资产左上角在世界坐标 (0,700)；雪面 S(x)=770+0.26*max(0,1550-x) */
const Slope: React.FC = () => {
  const w = 3400, h = 900;
  const n1 = vnoise(12), n2 = vnoise(33);
  const S = (x: number) => 770 + 0.26 * Math.max(0, 1550 - x) + 14 * n1(x / 300) + 6 * n2(x / 90) - 700;
  const ridge = Array.from({length: Math.ceil(w / 30) + 2}, (_, i) => [i * 30, S(i * 30)] as P);
  const ridgeD = ridge.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1].toFixed(1)}`).join('');
  const r = rng(91);
  const patches = Array.from({length: 22}, () => {
    const x = r() * w;
    return {x, y: S(x) + 40 + r() * 260, rx: 140 + r() * 420, ry: 10 + r() * 30};
  });
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <linearGradient id="sl" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#dbe6f6" />
          <stop offset="0.2" stopColor={C.snow} />
          <stop offset="1" stopColor={C.snowLit} />
        </linearGradient>
        <filter id="sw3" x="-5%" y="-20%" width="110%" height="140%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.006 0.02" numOctaves={3} seed={5} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={40} xChannelSelector="R" yChannelSelector="G" result="d" />
          <feGaussianBlur in="d" stdDeviation={6} />
        </filter>
        <filter id="edge3" x="-2%" y="-10%" width="104%" height="120%">
          <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves={3} seed={6} result="warp" />
          <feDisplacementMap in="SourceGraphic" in2="warp" scale={10} xChannelSelector="R" yChannelSelector="G" />
        </filter>
        <clipPath id="slc"><path d={`${ridgeD}L${w + 30} ${h}L-30 ${h}Z`} /></clipPath>
      </defs>
      <g filter="url(#edge3)"><path d={`${ridgeD}L${w + 30} ${h}L-30 ${h}Z`} fill="url(#sl)" /></g>
      <g clipPath="url(#slc)">
        {patches.map((p, i) => <ellipse key={i} cx={p.x} cy={p.y} rx={p.rx} ry={p.ry} fill={C.snowDeep} opacity={0.14} filter="url(#sw3)" />)}
        <path d={ridgeD} stroke={C.snowShade} strokeWidth={16} fill="none" opacity={0.55} filter="url(#sw3)" />
      </g>
    </svg>
  );
};

/** 小石头的房间：冷蓝的墙和地板，中间留出一扇窗洞（窗外是雨夜和远处山顶的灯，画在窗洞后面） */
const Room: React.FC = () => {
  const w = 1920, h = 1080;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <linearGradient id="wallG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#2b3b7e" />
          <stop offset="0.7" stopColor="#3a4c92" />
          <stop offset="1" stopColor="#33448a" />
        </linearGradient>
        <linearGradient id="floorG2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#1a2458" />
          <stop offset="1" stopColor="#111a44" />
        </linearGradient>
        <filter id="wb" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.003 0.006" numOctaves={4} seed={14} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.4  0 0 0 0 0.5  0 0 0 0 0.85  2.2 0 0 0 -0.95" />
        </filter>
        <filter id="wd" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feTurbulence type="fractalNoise" baseFrequency="0.004 0.008" numOctaves={4} seed={19} />
          <feColorMatrix type="matrix" values="0 0 0 0 0.03  0 0 0 0 0.05  0 0 0 0 0.2  -2.2 0 0 0 1.1" />
        </filter>
        <mask id="winHole">
          <rect width={w} height={h} fill="#fff" />
          <rect x={690} y={160} width={400} height={450} fill="#000" />
        </mask>
      </defs>
      <g mask="url(#winHole)">
        <rect width={w} height={780} fill="url(#wallG)" />
        <rect width={w} height={780} filter="url(#wb)" opacity={0.18} />
        <rect width={w} height={780} filter="url(#wd)" opacity={0.18} />
        {Array.from({length: 9}, (_, r) => Array.from({length: 22}, (_, c) => <circle key={`${r}-${c}`} cx={c * 92 + (r % 2) * 46 + 20} cy={r * 88 + 40} r={3.2} fill="#9fb4e8" opacity={0.12} />))}
        {Array.from({length: 24}, (_, i) => <rect key={i} x={i * 84 + 20} y={0} width={3} height={770} fill="#6f86c8" opacity={0.07} />)}
        <rect y={760} width={w} height={26} fill="#34457f" />
        <rect y={786} width={w} height={h - 786} fill="url(#floorG2)" />
        {Array.from({length: 7}, (_, i) => <line key={i} x1={0} x2={w} y1={810 + i * 46} y2={810 + i * 46 + (i % 2) * 3} stroke="#2a3a78" strokeWidth={2} opacity={0.5} />)}
      </g>
    </svg>
  );
};

export const ASSETS: Record<string, Asset> = {
  paper: {w: 1920, h: 1080, format: 'jpeg', Comp: Paper},
  room: {w: 1920, h: 1080, format: 'png', Comp: Room},
  slope: {w: 3400, h: 900, format: 'png', Comp: Slope},
  'spring-1': {w: 3400, h: 700, format: 'png', Comp: () => <Spring cover={0.62} seed={3} />},
  'spring-2': {w: 3400, h: 700, format: 'png', Comp: () => <Spring cover={0.24} seed={3} />},
  'spring-3': {w: 3400, h: 700, format: 'png', Comp: () => <Spring cover={0} seed={3} />},
  cave: {w: 1920, h: 1080, format: 'png', Comp: Cave},
  river: {w: 1700, h: 540, format: 'png', Comp: River},
  pond: {w: 1600, h: 380, format: 'png', Comp: Pond},
  'trees-frame': {w: 3000, h: 1000, format: 'png', Comp: FrameTrees},
  'mount-night': {w: 3400, h: 800, format: 'png', Comp: () => <Mount tone="night" />},
  'mount-dawn': {w: 3400, h: 800, format: 'png', Comp: () => <Mount tone="dawn" />},
  'sky-night': {w: 2304, h: 900, format: 'jpeg', Comp: () => <Sky top={C.skyTop} mid={C.skyMid} low={C.skyLow} haze={C.skyHaze} />},
  'sky-dawn': {w: 2304, h: 900, format: 'jpeg', Comp: () => <Sky top="#7fa6cf" mid="#a9c8e0" low="#d3e5ee" haze="#eaf3f5" light seed={8} />},
  'trees-far': {w: 3400, h: 420, format: 'png', Comp: () => <Trees seed={5} w={3400} h={420} color="#1c2b5e" minH={120} maxH={250} gap={44} blur={1.8} fade={0.97} />},
  'trees-mid': {w: 3400, h: 520, format: 'png', Comp: () => <Trees seed={9} w={3400} h={520} color="#121d4a" minH={200} maxH={400} gap={84} blur={1.3} fade={1} />},
  'snow-a': {w: 3400, h: 700, format: 'png', Comp: () => <Snow w={3400} h={700} seed={2} />},
  'snow-b': {w: 3400, h: 700, format: 'png', Comp: () => <Snow w={3400} h={700} seed={7} amp={34} />},
};
