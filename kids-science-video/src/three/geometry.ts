/** Procedural geometry helpers — every shape in the videos is generated here, no external models. */
import {
  BufferGeometry,
  CatmullRomCurve3,
  CurvePath,
  CylinderGeometry,
  ExtrudeGeometry,
  LineCurve3,
  QuadraticBezierCurve3,
  Shape,
  SphereGeometry,
  TubeGeometry,
  Vector2,
  Vector3,
  CapsuleGeometry,
  TorusGeometry,
  Float32BufferAttribute,
} from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { mergeVertices } from "three/examples/jsm/utils/BufferGeometryUtils.js";

type V3 = readonly [number, number, number];

/** Cylinder whose axis runs along Z (all shafts in the transverse powertrain do). */
export const cylZ = (r: number, len: number, seg = 32, rTop?: number) =>
  new CylinderGeometry(rTop ?? r, r, len, seg).rotateX(Math.PI / 2);
export const cylX = (r: number, len: number, seg = 32) => new CylinderGeometry(r, r, len, seg).rotateZ(Math.PI / 2);
export const cylY = (r: number, len: number, seg = 32, rTop?: number) => new CylinderGeometry(rTop ?? r, r, len, seg);
export const capsuleZ = (r: number, len: number) => new CapsuleGeometry(r, len, 8, 24).rotateX(Math.PI / 2);
export const capsuleX = (r: number, len: number) => new CapsuleGeometry(r, len, 8, 24).rotateZ(Math.PI / 2);
export const sphere = (r: number, seg = 24) => new SphereGeometry(r, seg, Math.round(seg * 0.75));
export const rbox = (w: number, h: number, d: number, radius = 0.01) =>
  new RoundedBoxGeometry(w, h, d, 3, Math.min(radius, Math.min(w, h, d) / 2 - 1e-4));
export const torusZ = (R: number, r: number, arc = Math.PI * 2) => new TorusGeometry(R, r, 12, 48, arc);

/** Extrudes a 2D shape (XY plane) along Z, centred on z = 0. */
export const extrudeZ = (shape: Shape, depth: number, bevel = 0, bevelSeg = 2, curveSegments = 24, keepOutline = false) => {
  const g = new ExtrudeGeometry(shape, {
    depth: Math.max(1e-4, depth - 2 * bevel),
    bevelEnabled: bevel > 0,
    bevelThickness: bevel,
    bevelSize: bevel,
    // keepOutline: the bevel grows inwards so the silhouette equals the 2D shape
    bevelOffset: keepOutline ? -bevel : 0,
    bevelSegments: bevelSeg,
    curveSegments,
  });
  g.translate(0, 0, -(depth - 2 * bevel) / 2);
  return g;
};

/** Smooth-normal version (good for inverted-hull outlines on organic shapes). */
export const smoothNormals = (g: BufferGeometry) => {
  g.deleteAttribute("uv");
  const s = mergeVertices(g, 1e-4);
  s.computeVertexNormals();
  return s;
};

/** Spur gear with N teeth (module m), axis along Z, centred at origin. */
export const gearGeometry = (N: number, m: number, width: number, bevel = 0.0015) => {
  const rp = (m * N) / 2;
  const ra = rp + m * 0.9;
  const rr = rp - m * 1.05;
  const s = new Shape();
  const step = (Math.PI * 2) / N;
  for (let i = 0; i < N; i++) {
    const a = i * step;
    const pts: [number, number][] = [
      [rr, a - step * 0.5],
      [rr, a - step * 0.27],
      [ra, a - step * 0.14],
      [ra, a + step * 0.14],
      [rr, a + step * 0.27],
    ];
    pts.forEach(([r, ang], k) => {
      // angle measured from +Y towards +X (matches the crank convention)
      const x = r * Math.sin(ang);
      const y = r * Math.cos(ang);
      if (i === 0 && k === 0) s.moveTo(x, y);
      else s.lineTo(x, y);
    });
  }
  s.closePath();
  return extrudeZ(s, width, bevel, 1, 4);
};

/**
 * Cam lobe: radius(φ) = base + lift·cos²(πφ / 2w) inside ±w, else base.
 * φ is measured from the lobe nose; the nose points along +Y in local space.
 * The same function drives the valve lift, so cam and valve always touch.
 */
export const camProfile = (phi: number, base: number, lift: number, halfWidth: number) => {
  const a = Math.abs(phi);
  if (a >= halfWidth) return base;
  const c = Math.cos((Math.PI * a) / (2 * halfWidth));
  return base + lift * c * c;
};

export const camLobeGeometry = (base: number, lift: number, halfWidth: number, width: number) => {
  const s = new Shape();
  const n = 96;
  for (let i = 0; i <= n; i++) {
    const phi = -Math.PI + (i / n) * Math.PI * 2;
    const r = camProfile(phi, base, lift, halfWidth);
    const x = r * Math.sin(phi);
    const y = r * Math.cos(phi);
    if (i === 0) s.moveTo(x, y);
    else s.lineTo(x, y);
  }
  return extrudeZ(s, width, 0.001, 1, 4);
};

/** Polyline with rounded corners (no Catmull-Rom overshoot → pipes stay where we put them). */
export const roundedPath = (points: readonly V3[], radius: number) => {
  const p = points.map((q) => new Vector3(...q));
  const path = new CurvePath<Vector3>();
  let cur = p[0].clone();
  for (let i = 1; i < p.length - 1; i++) {
    const a = p[i - 1];
    const b = p[i];
    const c = p[i + 1];
    const inDir = b.clone().sub(a);
    const outDir = c.clone().sub(b);
    const r = Math.min(radius, inDir.length() / 2, outDir.length() / 2);
    const s = b.clone().sub(inDir.normalize().multiplyScalar(r));
    const e = b.clone().add(outDir.normalize().multiplyScalar(r));
    if (cur.distanceTo(s) > 1e-6) path.add(new LineCurve3(cur, s));
    path.add(new QuadraticBezierCurve3(s, b.clone(), e));
    cur = e;
  }
  path.add(new LineCurve3(cur, p[p.length - 1].clone()));
  return path;
};

export const tubeAlong = (points: readonly V3[], r: number, cornerRadius = 0.05, segments = 96) =>
  new TubeGeometry(roundedPath(points, cornerRadius), segments, r, 12, false);

export const smoothTube = (points: readonly V3[], r: number, segments = 96, closed = false) =>
  new TubeGeometry(
    new CatmullRomCurve3(points.map((q) => new Vector3(...q)), closed, "centripetal"),
    segments,
    r,
    12,
    closed,
  );

/** Belt around several pulleys (circles in the XY plane): convex hull of their outlines. */
export const beltLoop = (pulleys: readonly { x: number; y: number; r: number }[], z: number) => {
  const pts: Vector2[] = [];
  for (const p of pulleys)
    for (let i = 0; i < 72; i++) {
      const a = (i / 72) * Math.PI * 2;
      pts.push(new Vector2(p.x + p.r * Math.cos(a), p.y + p.r * Math.sin(a)));
    }
  // monotone-chain convex hull
  pts.sort((a, b) => a.x - b.x || a.y - b.y);
  const cross = (o: Vector2, a: Vector2, b: Vector2) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
  const lower: Vector2[] = [];
  for (const q of pts) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], q) <= 0) lower.pop();
    lower.push(q);
  }
  const upper: Vector2[] = [];
  for (let i = pts.length - 1; i >= 0; i--) {
    const q = pts[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], q) <= 0) upper.pop();
    upper.push(q);
  }
  const hull = lower.slice(0, -1).concat(upper.slice(0, -1));
  return hull.map((q) => [q.x, q.y, z] as V3);
};

/** Point + tangent along a rounded polyline at parameter u ∈ [0, 1] (arc-length). */
export const pathSampler = (points: readonly V3[], cornerRadius = 0.05) => {
  const path = roundedPath(points, cornerRadius);
  return (u: number): V3 => {
    const v = path.getPointAt(Math.min(1, Math.max(0, u)));
    return [v.x, v.y, v.z];
  };
};

/** Flat quad from 4 corner points (counter-clockwise seen from the front). */
export const quad = (a: V3, b: V3, c: V3, d: V3) => {
  const g = new BufferGeometry();
  const pos = new Float32Array([...a, ...b, ...c, ...a, ...c, ...d]);
  g.setAttribute("position", new Float32BufferAttribute(pos, 3));
  g.computeVertexNormals();
  return g;
};
