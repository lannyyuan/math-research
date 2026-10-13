import type {P} from './ink';

/** 叶形（耳朵、叶子、鹿耳）：从 base 到 tip，宽 w，bend 为弯曲量 */
export function petal(base: P, tip: P, w: number, bend = 0, n = 7): P[] {
  const dx = tip[0] - base[0], dy = tip[1] - base[1];
  const L = Math.hypot(dx, dy) || 1;
  const nx = -dy / L, ny = dx / L;
  const side = (sign: number) =>
    Array.from({length: n}, (_, i) => {
      const u = (i + 1) / (n + 1);
      const prof = Math.pow(Math.sin(Math.PI * Math.pow(u, 0.8)), 0.8) * (w / 2);
      const c = Math.sin(Math.PI * u) * bend;
      return [base[0] + dx * u + nx * (c + sign * prof), base[1] + dy * u + ny * (c + sign * prof)] as P;
    });
  return [base, ...side(1), tip, ...side(-1).reverse()];
}

export const add = (p: P, dx: number, dy: number): P => [p[0] + dx, p[1] + dy];
export const mir = (pts: P[], axisX = 0): P[] => pts.map(([x, y]) => [2 * axisX - x, y] as P);
export const sc = (pts: P[], k: number, ox = 0, oy = 0): P[] => pts.map(([x, y]) => [ox + (x - ox) * k, oy + (y - oy) * k] as P);

/** 锥形胶囊（四肢）：a→b，两端宽度 w0、w1，两端圆头 */
export function limb(a: P, b: P, w0: number, w1: number): P[] {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const L = Math.hypot(dx, dy) || 1;
  const ux = dx / L, uy = dy / L;
  const nx = -uy, ny = ux;
  const h0 = w0 / 2, h1 = w1 / 2;
  return [
    [a[0] - ux * h0 * 0.9, a[1] - uy * h0 * 0.9],
    [a[0] + nx * h0, a[1] + ny * h0],
    [(a[0] + b[0]) / 2 + nx * (h0 + h1) * 0.5, (a[1] + b[1]) / 2 + ny * (h0 + h1) * 0.5],
    [b[0] + nx * h1, b[1] + ny * h1],
    [b[0] + ux * h1 * 0.9, b[1] + uy * h1 * 0.9],
    [b[0] - nx * h1, b[1] - ny * h1],
    [(a[0] + b[0]) / 2 - nx * (h0 + h1) * 0.5, (a[1] + b[1]) / 2 - ny * (h0 + h1) * 0.5],
    [a[0] - nx * h0, a[1] - ny * h0],
  ] as P[];
}
