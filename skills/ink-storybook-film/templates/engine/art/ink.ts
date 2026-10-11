// 手绘墨线工具：把点列变成「粗细有变化、断断续续、带起稿辅助线」的笔触。
export type P = [number, number];

/** 确定性伪随机（同一个 seed 每次渲染都一样，画面不会抖） */
export const rng = (seed: number) => {
  let a = seed | 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

/** 平滑一维噪声，值域约 [-1,1] */
export const vnoise = (seed: number) => {
  const r = rng(seed * 9973 + 17);
  const tab = Array.from({length: 512}, () => r() * 2 - 1);
  return (x: number) => {
    const i = Math.floor(x);
    const f = x - i;
    const u = f * f * (3 - 2 * f);
    const a = tab[((i % 512) + 512) % 512];
    const b = tab[(((i + 1) % 512) + 512) % 512];
    return a + (b - a) * u;
  };
};

const fx = (n: number) => Math.round(n * 10) / 10;

/** Catmull-Rom 样条，按 step 取点 */
export function spline(pts: P[], step = 3, closed = false): P[] {
  const n = pts.length;
  if (n < 3) {
    if (n === 2) {
      const d = Math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]);
      const m = Math.max(2, Math.ceil(d / step));
      return Array.from({length: m + 1}, (_, k) => [pts[0][0] + ((pts[1][0] - pts[0][0]) * k) / m, pts[0][1] + ((pts[1][1] - pts[0][1]) * k) / m] as P);
    }
    return pts.slice();
  }
  const get = (i: number): P => (closed ? pts[((i % n) + n) % n] : pts[Math.max(0, Math.min(n - 1, i))]);
  const out: P[] = [];
  const segs = closed ? n : n - 1;
  for (let i = 0; i < segs; i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    const d = Math.hypot(p2[0] - p1[0], p2[1] - p1[1]);
    const m = Math.max(2, Math.ceil(d / step));
    for (let k = 0; k < m; k++) {
      const t = k / m, t2 = t * t, t3 = t2 * t;
      const c = (a: number, b: number, cc: number, dd: number) => 0.5 * (2 * b + (-a + cc) * t + (2 * a - 5 * b + 4 * cc - dd) * t2 + (-a + 3 * b - 3 * cc + dd) * t3);
      out.push([c(p0[0], p1[0], p2[0], p3[0]), c(p0[1], p1[1], p2[1], p3[1])]);
    }
  }
  if (!closed) out.push(pts[n - 1]);
  return out;
}

export interface InkOpts {
  w?: number; // 基础线宽
  seed?: number;
  wobble?: number; // 手抖：垂直方向的缓慢偏移（像素）
  broken?: number; // 0~1，断笔程度
  taper?: number; // 0~1，两端收细程度
  closed?: boolean; // 闭合线：收笔时多画过头一点
  step?: number;
}

/** 变宽墨线 → 一个 path 的 d（多个多边形拼在一起） */
export function ink(pts: P[], o: InkOpts = {}): string {
  const {w = 3, seed = 1, wobble = 1.1, broken = 0, taper = 0.7, closed = false, step = 3} = o;
  let sp = spline(pts, step, closed);
  if (closed) {
    const extra = sp.slice(1, Math.max(3, Math.floor(sp.length * 0.07)));
    sp = sp.concat([sp[0]], extra.map((p) => [p[0] + 0.8, p[1] + 0.8] as P));
  }
  const N = sp.length;
  if (N < 3) return '';
  const s = new Array<number>(N).fill(0);
  for (let i = 1; i < N; i++) s[i] = s[i - 1] + Math.hypot(sp[i][0] - sp[i - 1][0], sp[i][1] - sp[i - 1][1]);
  const L = s[N - 1] || 1;
  const nW = vnoise(seed), nS = vnoise(seed + 41), nB = vnoise(seed + 83), nP = vnoise(seed + 127);
  const gapT = 1 - broken * 1.5;
  const vis = (i: number) => !(broken > 0 && nB(s[i] * 0.03) > gapT && s[i] > 6 && s[i] < L - 6);
  const smooth = (e0: number, e1: number, x: number) => {
    const t = Math.max(0, Math.min(1, (x - e0) / (e1 - e0)));
    return t * t * (3 - 2 * t);
  };
  const L2: P[] = [], R2: P[] = [], width: number[] = [];
  for (let i = 0; i < N; i++) {
    const a = sp[Math.max(0, i - 1)], b = sp[Math.min(N - 1, i + 1)];
    let tx = b[0] - a[0], ty = b[1] - a[1];
    const tl = Math.hypot(tx, ty) || 1;
    tx /= tl; ty /= tl;
    const nx = -ty, ny = tx;
    const u = s[i] / L;
    const pr = smooth(0, Math.min(0.2, 22 / L), u) * smooth(1, Math.max(0.8, 1 - 22 / L), u);
    const prof = 1 - taper + taper * pr;
    // 粗细：低频起伏 + 偶尔一次“压笔”变粗 + 下行笔画略重（像毛笔/钢笔的压力）
    const press = 0.55 + 0.45 * (1 + nW(s[i] * 0.022)) + 0.75 * Math.max(0, nP(s[i] * 0.013 + 5)) + 0.22 * Math.max(0, ty);
    const wi = Math.max(0.3, w * prof * press * 0.8);
    const off = wobble * nS(s[i] * 0.018);
    const cx = sp[i][0] + nx * off, cy = sp[i][1] + ny * off;
    L2.push([cx + (nx * wi) / 2, cy + (ny * wi) / 2]);
    R2.push([cx - (nx * wi) / 2, cy - (ny * wi) / 2]);
    width.push(wi);
  }
  let d = '';
  let i = 0;
  while (i < N) {
    if (!vis(i)) { i++; continue; }
    let j = i;
    while (j + 1 < N && vis(j + 1)) j++;
    if (j - i >= 3) {
      d += `M${fx(L2[i][0])} ${fx(L2[i][1])}`;
      for (let k = i + 1; k <= j; k++) d += `L${fx(L2[k][0])} ${fx(L2[k][1])}`;
      for (let k = j; k >= i; k--) d += `L${fx(R2[k][0])} ${fx(R2[k][1])}`;
      d += 'Z';
    }
    i = j + 1;
  }
  return d;
}

export interface SketchOpts {
  seed?: number;
  n?: number; // 辅助线条数
  off?: number; // 偏离轮廓的距离
  ext?: number; // 两端出头的长度
  w?: number;
  closed?: boolean;
}

/** 起稿辅助线：沿轮廓重复画几遍，偏一点、出头一点，更细更淡 */
export function sketch(pts: P[], o: SketchOpts = {}): string {
  const {seed = 1, n = 1, off = 2.6, ext = 9, w = 1.15, closed = false} = o;
  let d = '';
  for (let j = 0; j < n; j++) {
    const nx = vnoise(seed + j * 31 + 3), ny = vnoise(seed + j * 57 + 11);
    let q: P[] = pts.map((p, i) => [p[0] + nx(i * 0.6) * off, p[1] + ny(i * 0.6) * off] as P);
    if (!closed && q.length >= 2) {
      const a = q[0], b = q[1], c = q[q.length - 2], e = q[q.length - 1];
      const la = Math.hypot(a[0] - b[0], a[1] - b[1]) || 1, le = Math.hypot(e[0] - c[0], e[1] - c[1]) || 1;
      q = [[a[0] + ((a[0] - b[0]) / la) * ext, a[1] + ((a[1] - b[1]) / la) * ext], ...q, [e[0] + ((e[0] - c[0]) / le) * ext, e[1] + ((e[1] - c[1]) / le) * ext]];
    }
    d += ink(q, {w, seed: seed + j * 13, wobble: 1.6, broken: 0.28, taper: 0.9, closed, step: 4});
  }
  return d;
}

/** 椭圆点列（辅助圆） */
export function ellipse(cx: number, cy: number, rx: number, ry: number, rot = 0, n = 14): P[] {
  const c = Math.cos(rot), s = Math.sin(rot);
  return Array.from({length: n}, (_, i) => {
    const a = (i / n) * Math.PI * 2;
    const x = Math.cos(a) * rx, y = Math.sin(a) * ry;
    return [cx + x * c - y * s, cy + x * s + y * c] as P;
  });
}

/** 闭合平滑区域 → path d（水彩填色用） */
export function blob(pts: P[], closed = true): string {
  const sp = spline(pts, 5, closed);
  return sp.map((p, i) => `${i ? 'L' : 'M'}${fx(p[0])} ${fx(p[1])}`).join('') + (closed ? 'Z' : '');
}

export interface FillSpec { d: string; color: string; opacity?: number; shade?: boolean }

/** 一块图形的构造器：先摆填色，再加墨线，最后 build 出三层 path */
export class Art {
  fills: FillSpec[] = [];
  inkD: string[] = [];
  sketchD: string[] = [];
  private k = 0;
  constructor(public seed = 1) {}
  /** 水彩填色（闭合） */
  fill(pts: P[], color: string, opacity = 1) {
    this.fills.push({d: blob(pts), color, opacity});
    return this;
  }
  /** 阴影：淡淡的蓝灰 */
  shade(pts: P[], opacity = 0.38, color = '#6b80b4') {
    this.fills.push({d: blob(pts), color, opacity, shade: true});
    return this;
  }
  /** 墨线 */
  line(pts: P[], o: InkOpts & {sk?: number} = {}) {
    const sd = this.seed * 100 + this.k++ * 7;
    this.inkD.push(ink(pts, {seed: sd, broken: 0.12, ...o}));
    if (o.sk) this.sketchD.push(sketch(pts, {seed: sd + 3, n: o.sk, closed: o.closed}));
    return this;
  }
  /** 闭合的外轮廓 = 填色 + 墨线 */
  shape(pts: P[], color: string, o: InkOpts & {sk?: number; opacity?: number} = {}) {
    this.fill(pts, color, o.opacity ?? 1);
    return this.line(pts, {closed: true, ...o});
  }
  /** 宽笔触的淡彩（粗树枝、围巾边等）：用 ink 多边形当填色 */
  wash(pts: P[], w: number, color: string, opacity = 1, o: InkOpts = {}) {
    const sd = this.seed * 100 + this.k++ * 7;
    this.fills.push({d: ink(pts, {seed: sd, w, taper: 0.45, wobble: 0.6, ...o}), color, opacity});
    return this;
  }
  /** 起稿辅助圆 */
  guide(cx: number, cy: number, rx: number, ry: number, rot = 0) {
    const sd = this.seed * 100 + this.k++ * 7;
    this.sketchD.push(sketch(ellipse(cx, cy, rx, ry, rot), {seed: sd, n: 1, closed: true, off: 3, w: 1}));
    return this;
  }
  build() {
    return {fills: this.fills, ink: this.inkD.join(''), sketch: this.sketchD.join('')};
  }
}
