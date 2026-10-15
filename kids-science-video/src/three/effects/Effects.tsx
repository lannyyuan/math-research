/** Reusable, frame-driven effect layers: flowing droplets, power arrows, cool-air ripples, exhaust puffs. */
import React, { useMemo } from "react";
import { Quaternion, Vector3 } from "three";
import { COLORS } from "../../style/theme";
import { roundedPath, sphere, torusZ } from "../geometry";
import { makeGlow, makeToon } from "../materials";
import { ConeGeometry } from "three";

type V3 = readonly [number, number, number];

/**
 * Droplets travelling along a pipe. `time` = seconds since the flow started.
 * The first droplet leaves the source at time 0; new ones follow every `spacing` metres.
 */
export const FlowDots: React.FC<{
  readonly path: readonly V3[];
  readonly time: number;
  readonly speed: number;
  readonly spacing: number;
  readonly color: string;
  readonly size: number;
  readonly opacity: number;
  readonly loop?: boolean;
}> = ({ path, time, speed, spacing, color, size, opacity, loop = false }) => {
  const curve = useMemo(() => roundedPath(path, 0.05), [path]);
  const len = useMemo(() => curve.getLength(), [curve]);
  const geo = useMemo(() => sphere(1, 16), []);
  const mat = useMemo(() => makeToon(color, 0.999), [color]);
  mat.opacity = opacity;
  if (time < 0 || opacity <= 0.01) return null;
  const travelled = time * speed;
  const count = Math.ceil(len / spacing) + 1;
  const dots: React.ReactNode[] = [];
  for (let k = 0; k < count + 40; k++) {
    let s = travelled - k * spacing;
    if (s < 0) break;
    if (loop) s %= len;
    else if (s > len) continue;
    const p = curve.getPointAt(s / len);
    const tan = curve.getTangentAt(s / len);
    // grow in at the source, shrink at the destination
    const grow = Math.min(1, s / 0.12, (len - s) / 0.12);
    dots.push(
      <group key={k} position={[p.x, p.y, p.z]} quaternion={new Quaternion().setFromUnitVectors(new Vector3(0, 1, 0), tan)}>
        <mesh geometry={geo} material={mat} scale={[size * grow, size * 1.35 * grow, size * grow]} renderOrder={12} />
      </group>,
    );
    if (dots.length > 60) break;
  }
  return <group>{dots}</group>;
};

/** Chevron arrows streaming along a path (power flow). */
export const PowerArrows: React.FC<{
  readonly path: readonly V3[];
  readonly time: number;
  readonly opacity: number;
  readonly speed?: number;
  readonly spacing?: number;
  readonly size?: number;
}> = ({ path, time, opacity, speed = 0.45, spacing = 0.14, size = 0.04 }) => {
  const curve = useMemo(() => roundedPath(path, 0.04), [path]);
  const len = useMemo(() => curve.getLength(), [curve]);
  const geo = useMemo(() => new ConeGeometry(1, 1.6, 20), []);
  // arrows are a diagram overlay: drawn on top so the power path is never hidden
  const mat = useMemo(() => {
    const m = makeGlow(COLORS.power, 1);
    m.depthTest = false;
    return m;
  }, []);
  const core = useMemo(() => {
    const m = makeToon(COLORS.power, 0.999);
    m.depthTest = false;
    return m;
  }, []);
  if (opacity <= 0.01) return null;
  mat.opacity = 0.35 * opacity;
  core.opacity = opacity;
  const n = Math.floor(len / spacing);
  const off = (time * speed) % spacing;
  const items: React.ReactNode[] = [];
  for (let k = 0; k <= n; k++) {
    const s = k * spacing + off;
    if (s > len) break;
    const u = s / len;
    const p = curve.getPointAt(u);
    const tan = curve.getTangentAt(u);
    const q = new Quaternion().setFromUnitVectors(new Vector3(0, 1, 0), tan);
    const edge = Math.min(1, s / 0.08, (len - s) / 0.08);
    items.push(
      <group key={k} position={[p.x, p.y, p.z]} quaternion={q} scale={size * edge}>
        <mesh geometry={geo} material={core} renderOrder={32} />
        <mesh geometry={geo} material={mat} scale={1.35} renderOrder={33} />
      </group>,
    );
  }
  return <group>{items}</group>;
};

/** Light-blue "(((" ripples of cool air flowing into the radiator (towards −X). */
export const WindWaves: React.FC<{ readonly at: V3; readonly time: number; readonly amount: number; readonly color?: string }> = ({
  at,
  time,
  amount,
  color = COLORS.coolWind,
}) => {
  const R = 0.2;
  const arc = Math.PI * 0.6;
  // arc in the XY plane, apex pointing to −X (the direction the air travels)
  const geo = useMemo(() => torusZ(R, 0.014, arc).rotateZ(Math.PI - arc / 2), [arc]);
  const mats = useMemo(() => Array.from({ length: 4 }, () => makeToon(color, 0.999)), [color]);
  if (amount <= 0.01) return null;
  const waves: React.ReactNode[] = [];
  for (let k = 0; k < mats.length; k++) {
    const u = (time * 0.75 + k / mats.length) % 1;
    const x = at[0] + 0.7 * (1 - u);
    mats[k].opacity = 0.9 * amount * Math.sin(Math.PI * u);
    for (const dz of [-0.36, 0, 0.36]) {
      waves.push(
        <mesh key={`${k}_${dz}`} geometry={geo} material={mats[k]} position={[x + R, at[1], at[2] + dz]} renderOrder={34} />,
      );
    }
  }
  return <group>{waves}</group>;
};

/** Soft grey exhaust puffs drifting backwards from the tailpipe. */
export const Puffs: React.FC<{ readonly at: V3; readonly time: number; readonly amount: number }> = ({ at, time, amount }) => {
  const geo = useMemo(() => sphere(1, 20), []);
  const mats = useMemo(() => Array.from({ length: 6 }, () => makeToon(COLORS.smoke, 0.999)), []);
  if (amount <= 0.01) return null;
  return (
    <group>
      {mats.map((m, k) => {
        const u = (time * 0.55 + k / mats.length) % 1;
        m.opacity = amount * 0.75 * (1 - u) * Math.min(1, u * 8);
        const s = 0.045 + 0.16 * u;
        return (
          <mesh
            key={k}
            geometry={geo}
            material={m}
            position={[at[0] - 0.05 - 0.75 * u, at[1] + 0.03 + 0.22 * u * u, at[2] + 0.04 * Math.sin(k * 2.1)]}
            scale={[s * 1.2, s, s]}
            renderOrder={35}
          />
        );
      })}
    </group>
  );
};

/**
 * Soft blue "current" pulses gliding along a cable (comet: bright head, fading tail).
 * Always drawn on top like a diagram overlay; direction = path order.
 */
export const CurrentFlow: React.FC<{
  readonly path: readonly V3[];
  readonly time: number;
  readonly amount: number;
  readonly speed?: number;
  readonly spacing?: number;
  readonly size?: number;
  readonly color?: string;
}> = ({ path, time, amount, speed = 0.7, spacing = 0.22, size = 0.011, color = COLORS.current }) => {
  const curve = useMemo(() => roundedPath(path, 0.05), [path]);
  const len = useMemo(() => curve.getLength(), [curve]);
  const geo = useMemo(() => sphere(1, 14), []);
  const mats = useMemo(
    () =>
      [0.85, 0.5, 0.28, 0.14].map((o) => {
        const m = makeGlow(color, o);
        m.depthTest = false;
        return m;
      }),
    [color],
  );
  const core = useMemo(() => {
    const m = makeGlow("#FFFFFF", 0.9);
    m.depthTest = false;
    return m;
  }, []);
  if (amount <= 0.01) return null;
  mats.forEach((m, k) => (m.opacity = [0.85, 0.5, 0.28, 0.14][k] * amount));
  core.opacity = 0.55 * amount;
  const off = (time * speed) % spacing;
  const items: React.ReactNode[] = [];
  for (let s0 = off; s0 < len; s0 += spacing) {
    for (let k = 0; k < 4; k++) {
      const s = s0 - k * size * 1.6;
      if (s < 0) continue;
      const p = curve.getPointAt(s / len);
      const edge = Math.min(1, s / 0.06, (len - s) / 0.06);
      const r = size * (1 - k * 0.18) * edge;
      items.push(<mesh key={`${s0.toFixed(4)}_${k}`} geometry={geo} material={mats[k]} position={[p.x, p.y, p.z]} scale={r * 1.6} renderOrder={36} />);
      if (k === 0) items.push(<mesh key={`${s0.toFixed(4)}_c`} geometry={geo} material={core} position={[p.x, p.y, p.z]} scale={r * 0.45} renderOrder={37} />);
    }
  }
  return <group>{items}</group>;
};
