/** Small, pure animation helpers. Everything is a function of time → deterministic. */

export const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x);
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** 0 → 1 between a and b (clamped, linear). */
export const ramp = (t: number, a: number, b: number) => (b === a ? (t >= b ? 1 : 0) : clamp01((t - a) / (b - a)));

export const smooth = (x: number) => {
  const c = clamp01(x);
  return c * c * (3 - 2 * c);
};
export const smoother = (x: number) => {
  const c = clamp01(x);
  return c * c * c * (c * (c * 6 - 15) + 10);
};
export const easeOutBack = (x: number, s = 1.70158) => {
  const c = clamp01(x) - 1;
  return 1 + c * c * ((s + 1) * c + s);
};
export const easeOutCubic = (x: number) => 1 - Math.pow(1 - clamp01(x), 3);
export const easeInOutCubic = (x: number) => {
  const c = clamp01(x);
  return c < 0.5 ? 4 * c * c * c : 1 - Math.pow(-2 * c + 2, 3) / 2;
};

/** Fades in over [a, a+fin], holds, fades out over [b-fout, b]. */
export const window = (t: number, a: number, b: number, fin = 0.3, fout = 0.3) =>
  Math.min(smooth(ramp(t, a, a + fin)), 1 - smooth(ramp(t, b - fout, b)));

/** Gentle 0..1 breathing pulse driven only by time. */
export const pulse = (t: number, hz = 1.2) => 0.5 + 0.5 * Math.sin(t * Math.PI * 2 * hz);

/** Wraps angle into (-π, π]. */
export const wrapPi = (a: number) => {
  const twoPi = Math.PI * 2;
  let x = ((a + Math.PI) % twoPi + twoPi) % twoPi - Math.PI;
  if (x === -Math.PI) x = Math.PI;
  return x;
};
