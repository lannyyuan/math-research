/**
 * Geometric audit (method adapted from the MIT-licensed "anatomy" skill's kit/audit.mjs):
 * every part records its true shape; signed distance fields measure the clearance
 * between parts of different assemblies; rigid per-assembly offsets are replayed for
 * every frame, so a pass-through at rest, apart or in mid-flight is found, not guessed.
 */
type V3 = readonly [number, number, number];

export type Shape =
  | { kind: "box"; name: string; group: string; c: V3; h: V3 }
  | { kind: "cyl"; name: string; group: string; a: V3; b: V3; r: number }
  | { kind: "capsule"; name: string; group: string; a: V3; b: V3; r: number }
  | { kind: "sphere"; name: string; group: string; c: V3; r: number };

const sub = (a: V3, b: V3): [number, number, number] => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a: V3, b: V3): [number, number, number] => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const scale = (a: V3, k: number): [number, number, number] => [a[0] * k, a[1] * k, a[2] * k];

/** Signed distance from p to the shape translated by `off` (negative = inside). */
export const sdf = (s: Shape, p: V3, off: V3 = [0, 0, 0]): number => {
  const q0 = sub(p, off);
  switch (s.kind) {
    case "sphere":
      return len(sub(q0, s.c)) - s.r;
    case "box": {
      const d = sub(q0, s.c).map((v, i) => Math.abs(v) - s.h[i]) as [number, number, number];
      const out = Math.hypot(Math.max(d[0], 0), Math.max(d[1], 0), Math.max(d[2], 0));
      return out + Math.min(Math.max(d[0], d[1], d[2]), 0);
    }
    case "capsule": {
      const pa = sub(q0, s.a);
      const ba = sub(s.b, s.a);
      const t = Math.max(0, Math.min(1, dot(pa, ba) / dot(ba, ba)));
      return len(sub(pa, scale(ba, t))) - s.r;
    }
    case "cyl": {
      // capped cylinder (Inigo Quilez)
      const ba = sub(s.b, s.a);
      const pa = sub(q0, s.a);
      const baba = dot(ba, ba);
      const paba = dot(pa, ba);
      const x = len(sub(scale(pa, baba), scale(ba, paba))) - s.r * baba;
      const y = Math.abs(paba - baba * 0.5) - baba * 0.5;
      const x2 = x * x;
      const y2 = y * y * baba;
      const d = Math.max(x, y) < 0 ? -Math.min(x2, y2) : (x > 0 ? x2 : 0) + (y > 0 ? y2 : 0);
      return (Math.sign(d) * Math.sqrt(Math.abs(d))) / baba;
    }
  }
};

export const bounds = (s: Shape): { min: V3; max: V3 } => {
  switch (s.kind) {
    case "sphere":
      return { min: sub(s.c, [s.r, s.r, s.r]), max: add(s.c, [s.r, s.r, s.r]) };
    case "box":
      return { min: sub(s.c, s.h), max: add(s.c, s.h) };
    default: {
      const r = s.r;
      return {
        min: [Math.min(s.a[0], s.b[0]) - r, Math.min(s.a[1], s.b[1]) - r, Math.min(s.a[2], s.b[2]) - r],
        max: [Math.max(s.a[0], s.b[0]) + r, Math.max(s.a[1], s.b[1]) + r, Math.max(s.a[2], s.b[2]) + r],
      };
    }
  }
};

const orthoBasis = (d: V3): [V3, V3] => {
  const n = scale(d, 1 / len(d));
  const t: V3 = Math.abs(n[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
  const u0 = sub(t, scale(n, dot(t, n)));
  const u = scale(u0, 1 / len(u0));
  const v: V3 = [n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0]];
  return [u, v];
};

/** Points on the shape's surface, about `step` apart. */
export const surfacePoints = (s: Shape, step = 0.02): V3[] => {
  const pts: V3[] = [];
  if (s.kind === "sphere") {
    const n = Math.max(6, Math.ceil((Math.PI * s.r) / step));
    for (let i = 0; i <= n; i++) {
      const th = (i / n) * Math.PI;
      const m = Math.max(1, Math.ceil((2 * Math.PI * s.r * Math.sin(th)) / step));
      for (let k = 0; k < m; k++) {
        const ph = (k / m) * 2 * Math.PI;
        pts.push(add(s.c, [s.r * Math.sin(th) * Math.cos(ph), s.r * Math.cos(th), s.r * Math.sin(th) * Math.sin(ph)]));
      }
    }
  } else if (s.kind === "box") {
    for (let axis = 0; axis < 3; axis++)
      for (const sign of [-1, 1]) {
        const a1 = (axis + 1) % 3;
        const a2 = (axis + 2) % 3;
        const n1 = Math.max(1, Math.ceil((2 * s.h[a1]) / step));
        const n2 = Math.max(1, Math.ceil((2 * s.h[a2]) / step));
        for (let i = 0; i <= n1; i++)
          for (let k = 0; k <= n2; k++) {
            const p = [0, 0, 0];
            p[axis] = s.c[axis] + sign * s.h[axis];
            p[a1] = s.c[a1] - s.h[a1] + (2 * s.h[a1] * i) / n1;
            p[a2] = s.c[a2] - s.h[a2] + (2 * s.h[a2] * k) / n2;
            pts.push(p as unknown as V3);
          }
      }
  } else {
    const axis = sub(s.b, s.a);
    const L = len(axis);
    const [u, v] = orthoBasis(axis);
    const nl = Math.max(1, Math.ceil(L / step));
    const nc = Math.max(8, Math.ceil((2 * Math.PI * s.r) / step));
    for (let i = 0; i <= nl; i++) {
      const c = add(s.a, scale(axis, i / nl));
      for (let k = 0; k < nc; k++) {
        const ph = (k / nc) * 2 * Math.PI;
        pts.push(add(c, add(scale(u, s.r * Math.cos(ph)), scale(v, s.r * Math.sin(ph)))));
      }
    }
    // end discs (flat for cylinders, hemispheres for capsules)
    const nr = Math.max(1, Math.ceil(s.r / step));
    for (const [end, dir] of [
      [s.a, -1],
      [s.b, 1],
    ] as const)
      for (let j = 0; j <= nr; j++) {
        const rr = (s.r * j) / nr;
        const m = Math.max(1, Math.ceil((2 * Math.PI * rr) / step));
        for (let k = 0; k < m; k++) {
          const ph = (k / m) * 2 * Math.PI;
          const h = s.kind === "capsule" ? Math.sqrt(Math.max(0, s.r * s.r - rr * rr)) * dir : 0;
          pts.push(add(add(end, scale(axis, h / L)), add(scale(u, rr * Math.cos(ph)), scale(v, rr * Math.sin(ph)))));
        }
      }
  }
  return pts;
};

/** A tube (polyline) becomes one capsule per segment. */
export const tubeShapes = (name: string, group: string, pts: readonly V3[], r: number): Shape[] =>
  pts.slice(1).map((b, i) => ({ kind: "capsule", name: `${name}#${i}`, group, a: pts[i], b, r }));

export type Mount = { a: string; b: string; axis?: V3 };

export type Prepared = { shape: Shape; pts: V3[]; box: { min: V3; max: V3 } };
export const prepare = (shapes: readonly Shape[], step = 0.02): Prepared[] =>
  shapes.map((shape) => ({ shape, pts: surfacePoints(shape, step), box: bounds(shape) }));

const overlapBoxes = (a: { min: V3; max: V3 }, oa: V3, b: { min: V3; max: V3 }, ob: V3, m: number) =>
  a.min[0] + oa[0] - m <= b.max[0] + ob[0] && a.max[0] + oa[0] + m >= b.min[0] + ob[0] &&
  a.min[1] + oa[1] - m <= b.max[1] + ob[1] && a.max[1] + oa[1] + m >= b.min[1] + ob[1] &&
  a.min[2] + oa[2] - m <= b.max[2] + ob[2] && a.max[2] + oa[2] + m >= b.min[2] + ob[2];

/** Minimum signed clearance between two shapes under per-group offsets (≈ −depth when they interpenetrate). */
export const clearance = (A: Prepared, oa: V3, B: Prepared, ob: V3, margin = 0.05) => {
  if (!overlapBoxes(A.box, oa, B.box, ob, margin)) return Infinity;
  let m = Infinity;
  for (const p of A.pts) m = Math.min(m, sdf(B.shape, add(p, oa), ob));
  for (const p of B.pts) m = Math.min(m, sdf(A.shape, add(p, ob), oa));
  return m;
};

const baseName = (n: string) => n.split("#")[0];
export const mountFor = (mounts: readonly Mount[], a: string, b: string) =>
  mounts.find((m) => (m.a === baseName(a) && m.b === baseName(b)) || (m.a === baseName(b) && m.b === baseName(a)));

/** Is the relative motion of a mount pair along its slide axis (or zero)? */
export const slidesAlong = (rel: V3, axis?: V3) => {
  const l = len(rel);
  if (l < 1e-6) return true;
  if (!axis) return false;
  const n = scale(axis, 1 / len(axis));
  return len(sub(rel, scale(n, dot(rel, n)))) < 1e-4;
};

export type Violation = { a: string; b: string; depth: number; at: string };

/**
 * Checks one pose: every pair of shapes from different groups must not interpenetrate
 * (more than `tol`), unless it is a declared mount and the two groups are either home
 * relative to each other or sliding apart along the mount's axis.
 */
export const checkPose = (P: readonly Prepared[], offsets: (group: string) => V3, mounts: readonly Mount[], at: string, tol = 0.004) => {
  const out: Violation[] = [];
  for (let i = 0; i < P.length; i++)
    for (let j = i + 1; j < P.length; j++) {
      const A = P[i];
      const B = P[j];
      if (A.shape.group === B.shape.group) continue;
      const oa = offsets(A.shape.group);
      const ob = offsets(B.shape.group);
      const c = clearance(A, oa, B, ob);
      if (c >= -tol) continue;
      const m = mountFor(mounts, A.shape.name, B.shape.name);
      if (m && slidesAlong(sub(oa, ob), m.axis)) continue;
      out.push({ a: A.shape.name, b: B.shape.name, depth: -c, at });
    }
  return out;
};

export const vec = { add, sub, dot, len, scale };
