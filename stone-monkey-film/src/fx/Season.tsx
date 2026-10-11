import React, {useMemo} from 'react';

const rng = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

/** 四季的树冠：老树的枝头上长出花 / 叶 / 黄叶，冬天落雪。w = [春, 夏, 秋, 冬] 的权重（0~1）。 */
export const SeasonTree: React.FC<{cx: number; cy: number; rx: number; ry: number; w: number[]; t: number}> = ({cx, cy, rx, ry, w, t}) => {
  const blobs = useMemo(() => {
    const r = rng(77);
    return Array.from({length: 300}, (_, i) => {
      const a = r() * Math.PI * 2, d = Math.sqrt(r());
      const big = i < 22;
      return {x: cx + Math.cos(a) * rx * d, y: cy + Math.sin(a) * ry * d * (a > Math.PI ? 0.75 : 1), s: big ? 38 + r() * 34 : 4 + r() * 9, k: r(), ph: r() * 6, big};
    });
  }, [cx, cy, rx, ry]);
  const [sp, su, au, wi] = w;
  const col = (b: {k: number}) => {
    // 春：灰粉的桃花；夏：灰绿；秋：灰金/土黄；
    if (sp >= su && sp >= au) return b.k < 0.5 ? '#d8b4b2' : '#cfa6a6';
    if (su >= au) return b.k < 0.5 ? '#7f9a82' : '#6d8a73';
    return b.k < 0.5 ? '#b9a06c' : '#a98a58';
  };
  const dens = Math.max(sp * 0.75, su * 1.0, au * 0.8);
  return (
    <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
      <defs><filter id="bl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9" /></filter></defs>
      {blobs.map((b, i) => {
        const keep = b.k < dens;
        if (!keep) return null;
        const o = Math.min(1, dens * 1.2) * (b.big ? 0.22 : 0.78) * (1 - 0.25 * b.k);
        return <ellipse key={i} cx={b.x + Math.sin(t * 0.8 + b.ph) * 2} cy={b.y} rx={b.s} ry={b.s * (sp > 0.5 ? 0.8 : 0.62)} fill={col(b)} opacity={o} filter={b.big ? 'url(#bl)' : undefined} />;
      })}
      {/* 冬：枝头的雪 */}
      {wi > 0.05 && blobs.filter((b) => b.k < 0.5 && !b.big).map((b, i) => <ellipse key={'w' + i} cx={b.x} cy={b.y - 4} rx={b.s * 0.7} ry={3.2} fill="#f2f0ea" opacity={wi * 0.8} />)}
    </svg>
  );
};

/** 飘落的东西：花瓣（春）/ 黄叶（秋）/ 雪（冬）。kind 的权重同上 */
export const Falling: React.FC<{w: number[]; t: number; x0?: number; x1?: number; y0?: number; y1?: number}> = ({w, t, x0 = 1500, x1 = 2800, y0 = 120, y1 = 860}) => {
  const items = useMemo(() => {
    const r = rng(31);
    return Array.from({length: 60}, () => ({x: x0 + r() * (x1 - x0), ph: r() * 6, sp: 28 + r() * 40, sz: 3 + r() * 5, k: r(), dr: 20 + r() * 60}));
  }, [x0, x1]);
  const [sp, su, au, wi] = w;
  const kind = sp > 0.3 ? 'petal' : au > 0.3 ? 'leaf' : wi > 0.3 ? 'snow' : 'none';
  if (kind === 'none') return null;
  const amt = Math.max(sp, au, wi);
  const fill = kind === 'petal' ? '#e6d2cf' : kind === 'leaf' ? '#b9a06c' : '#f4f2ec';
  return (
    <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none'}}>
      {items.map((it, i) => {
        if (it.k > amt) return null;
        const H = y1 - y0;
        const y = y0 + ((it.ph * 100 + t * it.sp) % H);
        const x = it.x + Math.sin(t * 0.9 + it.ph) * it.dr;
        const rx = (kind === 'snow' ? it.sz * 0.5 : it.sz) * 0.6;
        return <ellipse key={i} cx={x} cy={y} rx={rx} ry={rx * (kind === 'leaf' ? 0.6 : 0.5)} fill={fill} opacity={0.8 * amt} transform={`rotate(${(t * 60 + it.ph * 50) % 360} ${x} ${y})`} />;
      })}
    </svg>
  );
};
