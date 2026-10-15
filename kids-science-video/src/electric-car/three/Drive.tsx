/** Electric drivetrain parts: battery pack, HV harness, controller, motor, single-speed reducer. */
import React, { useMemo } from "react";
import { BufferGeometry, Shape } from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { COLORS, SIZES } from "../../style/theme";
import { cylY, cylZ, extrudeZ, gearGeometry, rbox, sphere, torusZ, tubeAlong } from "../../three/geometry";
import { Glass } from "../../three/Glass";
import { makeGlow, makeToon } from "../../three/materials";
import { Toon } from "../../three/Toon";
import { meshPhase } from "../../gas-car/mechanics";
import { CHARGE_CABLE, CHARGE_PORT, CTRL, DC_CABLES, MODULES, MOTOR, PACK, PHASE_CABLES, RED, TERMINAL } from "../layout";

type HL = { readonly highlight: number; readonly t: number };

// ---------------------------------------------------------------- battery
export const BatteryPack: React.FC<HL & { readonly modules: number[]; readonly glow: number }> = ({ highlight, t, modules, glow }) => {
  const g = useMemo(() => {
    const m0 = MODULES[0];
    const cells: BufferGeometry[] = [];
    const nx = 4;
    const nz = 5;
    for (let i = 0; i < nx; i++)
      for (let k = 0; k < nz; k++) {
        const c = cylY(0.019, 0.014, 14);
        c.deleteAttribute("uv");
        c.translate(-m0.w / 2 + (m0.w / nx) * (i + 0.5), 0.007, -m0.d / 2 + (m0.d / nz) * (k + 0.5));
        cells.push(c);
      }
    return {
      tray: rbox(PACK.x1 - PACK.x0, 0.035, PACK.z1 - PACK.z0, 0.015),
      lid: rbox(PACK.x1 - PACK.x0, PACK.y1 - PACK.y0, PACK.z1 - PACK.z0, 0.03),
      module: rbox(m0.w, 0.085, m0.d, 0.012),
      cells: mergeGeometries(cells),
      glowBox: rbox(PACK.x1 - PACK.x0 + 0.06, PACK.y1 - PACK.y0 + 0.05, PACK.z1 - PACK.z0 + 0.06, 0.05),
      junction: rbox(0.08, 0.07, 0.16, 0.015),
    };
  }, []);
  const glowMat = useMemo(() => makeGlow(COLORS.batteryGlow, 0.3), []);
  glowMat.opacity = 0.16 * glow * (0.8 + 0.2 * Math.sin(t * 4));
  const cx = (PACK.x0 + PACK.x1) / 2;
  const modY = PACK.y0 + 0.035 + 0.0425;
  return (
    <group>
      <Toon geometry={g.tray} color="#1F6E4C" highlight={highlight} t={t} position={[cx, PACK.y0 + 0.0175, 0]} outline={SIZES.outline} />
      {MODULES.map((m, i) => {
        const lit = modules[i] ?? 0;
        return (
          <group key={i} position={[m.x, modY, m.z]}>
            <Toon geometry={g.module} color="#2A7F59" highlight={highlight * 0.6} t={t} emissive={COLORS.batteryGlow} emissiveIntensity={0.85 * lit} outline={0.004} />
            <Toon geometry={g.cells} color="#9CD9B9" outline={0} position={[0, 0.0425, 0]} emissive="#E8FFF2" emissiveIntensity={0.75 * lit} />
          </group>
        );
      })}
      <Glass geometry={g.lid} color="#9EE6C0" opacity={0.18} highlight={highlight} t={t} position={[cx, (PACK.y0 + PACK.y1) / 2, 0]} />
      <Toon geometry={g.junction} color="#2B7D58" highlight={highlight} t={t} position={[PACK.x1 + 0.01, 0.335, 0.15]} />
      {glow > 0.01 ? <mesh geometry={g.glowBox} material={glowMat} position={[cx, (PACK.y0 + PACK.y1) / 2, 0]} renderOrder={30} /> : null}
    </group>
  );
};

// ---------------------------------------------------------------- harness
export const Harness: React.FC<HL> = ({ highlight, t }) => {
  const g = useMemo(
    () => ({
      dc: DC_CABLES.map((p) => tubeAlong(p, 0.013, 0.05, 64)),
      phase: PHASE_CABLES.map((p) => tubeAlong(p, 0.011, 0.04, 32)),
      charge: tubeAlong(CHARGE_CABLE, 0.012, 0.08, 48),
      port: cylZ(0.055, 0.03, 24),
      plug: cylZ(0.03, 0.02, 20),
    }),
    [],
  );
  return (
    <group>
      {g.dc.map((geo, i) => (
        <Toon key={`d${i}`} geometry={geo} color={COLORS.hvCable} highlight={highlight} t={t} outlineMode="normal" outline={0.004} />
      ))}
      {g.phase.map((geo, i) => (
        <Toon key={`p${i}`} geometry={geo} color={COLORS.hvCable} highlight={highlight} t={t} outlineMode="normal" outline={0.003} />
      ))}
      <Toon geometry={g.charge} color={COLORS.hvCable} highlight={highlight} t={t} outlineMode="normal" outline={0.004} />
      <Toon geometry={g.port} color={COLORS.controller} highlight={highlight} t={t} position={CHARGE_PORT} />
      <Toon geometry={g.plug} color={COLORS.controllerLed} outline={0} position={[CHARGE_PORT[0], CHARGE_PORT[1], CHARGE_PORT[2] + 0.02]} />
    </group>
  );
};

// ---------------------------------------------------------------- controller ("brain")
const hash = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
export const Controller: React.FC<HL & { readonly activity: number }> = ({ highlight, t, activity }) => {
  const g = useMemo(
    () => ({
      box: rbox(CTRL.x1 - CTRL.x0, CTRL.y1 - CTRL.y0, CTRL.z1 - CTRL.z0, 0.035),
      fin: rbox(0.012, 0.02, CTRL.z1 - CTRL.z0 - 0.08, 0.005),
      led: cylY(0.012, 0.008, 12),
      halo: sphere(1, 12),
    }),
    [],
  );
  const halo = useMemo(() => makeGlow(COLORS.controllerLed, 1), []);
  const cx = (CTRL.x0 + CTRL.x1) / 2;
  // a little "thinking" pattern: LEDs flicker deterministically from the frame time
  const tick = Math.floor(t * 9);
  const leds: { x: number; z: number; on: number }[] = [];
  for (let i = 0; i < 3; i++)
    for (let k = 0; k < 6; k++) {
      const on = activity * (hash(tick * 31 + i * 7 + k) > 0.45 ? 1 : 0.15);
      leds.push({ x: CTRL.x0 + 0.08 + i * 0.1, z: CTRL.z0 + 0.07 + k * 0.092, on });
    }
  halo.opacity = 0.5 * activity;
  return (
    <group>
      <Toon geometry={g.box} color={COLORS.controller} highlight={highlight} t={t} position={[cx, (CTRL.y0 + CTRL.y1) / 2, 0]} outline={0.006} emissive={COLORS.controllerLed} emissiveIntensity={0.12 * activity} />
      {[0, 1, 2, 3].map((k) => (
        <Toon key={k} geometry={g.fin} color="#2D5FAF" outline={0} position={[CTRL.x1 - 0.04 - k * 0.025, CTRL.y1 + 0.004, 0]} />
      ))}
      {leds.map((l, i) => (
        <group key={i}>
          <Toon geometry={g.led} color={l.on > 0.5 ? COLORS.controllerLed : "#5C86C9"} outline={0} position={[l.x, CTRL.y1 + 0.004, l.z]} emissive={COLORS.controllerLed} emissiveIntensity={l.on} />
          {l.on > 0.5 ? <mesh geometry={g.halo} material={halo} position={[l.x, CTRL.y1 + 0.01, l.z]} scale={0.022} renderOrder={31} /> : null}
        </group>
      ))}
    </group>
  );
};

// ---------------------------------------------------------------- motor
const statorShape = () => {
  const s = new Shape();
  const n = MOTOR.slots;
  const rOut = MOTOR.statorR;
  const rYoke = 0.094;
  const rTooth = 0.074;
  const half = (Math.PI / n) * 0.42;
  const step = (2 * Math.PI) / n;
  s.absarc(0, 0, rOut, 0, Math.PI * 2, false);
  const hole = new Shape();
  for (let i = 0; i < n; i++) {
    const a = i * step;
    const pts: [number, number][] = [
      [rYoke, a - step / 2],
      [rYoke, a - half],
      [rTooth, a - half * 1.15],
      [rTooth, a + half * 1.15],
      [rYoke, a + half],
    ];
    pts.forEach(([r, ang], k) => {
      const x = r * Math.cos(ang);
      const y = r * Math.sin(ang);
      if (i === 0 && k === 0) hole.moveTo(x, y);
      else hole.lineTo(x, y);
    });
  }
  hole.closePath();
  s.holes.push(hole);
  return s;
};
const magnetShape = (a0: number, a1: number, r0: number, r1: number) => {
  const s = new Shape();
  s.absarc(0, 0, r1, a0, a1, false);
  s.absarc(0, 0, r0, a1, a0, true);
  s.closePath();
  return s;
};

export const Motor: React.FC<HL & { readonly rotor: number; readonly current: number; readonly speedLines: number }> = ({
  highlight,
  t,
  rotor,
  current,
  speedLines,
}) => {
  const len = MOTOR.z1 - MOTOR.z0;
  const cz = (MOTOR.z0 + MOTOR.z1) / 2;
  const coreLen = len - 0.13;
  const g = useMemo(() => {
    const n = MOTOR.slots;
    const pp = MOTOR.polePairs;
    const mags = Array.from({ length: pp * 2 }, (_, k) => {
      const a0 = (k * 2 * Math.PI) / (pp * 2) + 0.08;
      const a1 = ((k + 1) * 2 * Math.PI) / (pp * 2) - 0.08;
      return extrudeZ(magnetShape(a0, a1, MOTOR.rotorR - 0.012, MOTOR.rotorR), coreLen - 0.01, 0, 1, 16);
    });
    return {
      housing: cylZ(MOTOR.r, len, 48),
      endCap: cylZ(MOTOR.r - 0.005, 0.02, 48),
      stator: extrudeZ(statorShape(), coreLen, 0.002, 1, 48),
      coil: rbox(0.03, 0.022, coreLen + 0.03, 0.01),
      rotor: cylZ(MOTOR.rotorR - 0.012, coreLen, 40),
      mags,
      shaft: cylZ(0.016, MOTOR.z1 + 0.05 - (RED.gearZ - 0.03), 20),
      terminal: rbox(0.05, 0.035, 0.22, 0.01),
      speed: torusZ(MOTOR.r + 0.03, 0.009, 1.05),
      speed2: torusZ(MOTOR.r + 0.055, 0.007, 0.7),
      slots: Array.from({ length: n }, (_, i) => (i * 2 * Math.PI) / n),
    };
  }, [coreLen, len]);
  const speedMats = useMemo(() => [0, 1, 2].map(() => makeToon(COLORS.speedLine, 0.999)), []);
  speedMats.forEach((m) => (m.opacity = 0.85 * speedLines));
  const coilColors = [COLORS.coilA, COLORS.coilB, COLORS.coilC];
  const pp = MOTOR.polePairs;
  return (
    <group position={[MOTOR.x, MOTOR.y, 0]}>
      <Glass geometry={g.housing} color={COLORS.motorHousing} opacity={0.2} highlight={highlight} t={t} position={[0, 0, cz]} />
      <Toon geometry={g.stator} color={COLORS.stator} highlight={highlight} t={t} position={[0, 0, cz]} outline={0.003} />
      {g.slots.map((a, i) => {
        // field rotates with the rotor (leading it by 90° electrical) → coils light up in a turning pattern
        const field = Math.max(0, Math.cos(pp * (rotor - a) + Math.PI / 2));
        const glow = current * field;
        const r = 0.084;
        return (
          <Toon
            key={i}
            geometry={g.coil}
            color="#2D5E8C"
            highlight={highlight * 0.3}
            t={t}
            position={[r * Math.cos(a), r * Math.sin(a), cz]}
            rotation={[0, 0, a]}
            emissive={coilColors[i % 3]}
            emissiveIntensity={1.1 * glow}
            outline={0.002}
          />
        );
      })}
      <group rotation={[0, 0, rotor]}>
        <Toon geometry={g.rotor} color="#8FA3B8" highlight={highlight} t={t} position={[0, 0, cz]} outline={0.003} />
        {g.mags.map((m, k) => (
          <Toon key={k} geometry={m} color={k % 2 === 0 ? COLORS.magnetN : COLORS.magnetS} highlight={highlight} t={t} position={[0, 0, cz]} outline={0.002} />
        ))}
        <Toon geometry={g.shaft} color={COLORS.shaft} outline={0.003} position={[0, 0, (MOTOR.z1 + 0.05 + RED.gearZ - 0.03) / 2]} />
      </group>
      <Toon geometry={g.terminal} color="#3E5F86" highlight={highlight * 0.5} t={t} position={[TERMINAL.x - MOTOR.x, TERMINAL.y - MOTOR.y, 0.14]} rotation={[0, 0, -Math.PI / 4]} />
      {speedLines > 0.01
        ? speedMats.map((m, k) => (
            <group key={k} position={[0, 0, MOTOR.z1 + 0.035]} rotation={[0, 0, rotor + (k * 2 * Math.PI) / 3]}>
              <mesh geometry={g.speed} material={m} renderOrder={34} />
              <mesh geometry={g.speed2} material={m} rotation={[0, 0, -0.25]} renderOrder={34} />
            </group>
          ))
        : null}
    </group>
  );
};

// ---------------------------------------------------------------- single-speed reducer
export const Reducer: React.FC<HL & { readonly rotor: number; readonly wheel: number }> = ({ highlight, t, rotor, wheel }) => {
  const h = RED.housing;
  const g = useMemo(
    () => ({
      housing: rbox(h.x1 - h.x0, h.y1 - h.y0, h.z1 - h.z0, 0.06),
      pinion: gearGeometry(RED.nPinion, RED.module, RED.faceW),
      gear: gearGeometry(RED.nGear, RED.module, RED.faceW - 0.006),
      diff: sphere(0.045, 24),
      hub: cylZ(0.05, RED.faceW + 0.02, 28),
      mark: cylZ(0.008, 0.005, 12),
    }),
    [h],
  );
  const lambda = Math.atan2(RED.diffY - MOTOR.y, RED.diffX - MOTOR.x);
  const phase = meshPhase(lambda, RED.nPinion, RED.nGear);
  // pinion turns with the rotor; the big gear turns the other way, RATIO times slower (= −wheel)
  const gearRot = -rotor * (RED.nPinion / RED.nGear) + phase;
  void wheel;
  return (
    <group>
      <Glass geometry={g.housing} color={COLORS.reducer} opacity={0.2} highlight={highlight * 0.5} t={t} position={[(h.x0 + h.x1) / 2, (h.y0 + h.y1) / 2, (h.z0 + h.z1) / 2]} />
      <group position={[MOTOR.x, MOTOR.y, RED.gearZ]} rotation={[0, 0, rotor]}>
        <Toon geometry={g.pinion} color="#7FD3F5" highlight={highlight} t={t} outline={0.003} />
        <Toon geometry={g.mark} color={COLORS.power} outline={0} position={[0, 0.018, RED.faceW / 2 + 0.003]} />
      </group>
      <group position={[RED.diffX, RED.diffY, RED.gearZ]} rotation={[0, 0, gearRot]}>
        <Toon geometry={g.gear} color="#5FA8E0" highlight={highlight} t={t} outline={0.003} />
        <Toon geometry={g.hub} color="#9AB4CC" outline={0.003} />
        <Toon geometry={g.mark} color={COLORS.power} outline={0} position={[0, 0.115, RED.faceW / 2]} />
        <Toon geometry={g.diff} color="#9AA9BA" highlight={highlight} t={t} position={[0, 0, -0.045]} />
      </group>
    </group>
  );
};

