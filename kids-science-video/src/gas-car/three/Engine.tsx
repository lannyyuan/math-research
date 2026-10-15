/**
 * Inline-4 DOHC engine, transverse. Every moving part is placed from the crank
 * angle θ: pistons by the slider-crank relation, cams at θ/2, valves by the
 * actual cam-lobe profile, sparks only at each cylinder's own firing point.
 */
import React, { useMemo } from "react";
import { Shape } from "three";
import { COLORS, SIZES } from "../../style/theme";
import {
  beltLoop,
  camLobeGeometry,
  cylY,
  cylZ,
  extrudeZ,
  gearGeometry,
  rbox,
  smoothTube,
  sphere,
  torusZ,
} from "../../three/geometry";
import { Glass } from "../../three/Glass";
import { makeGlow } from "../../three/materials";
import { Toon } from "../../three/Toon";
import { ENG } from "../layout";
import {
  CAM_HALF_WIDTH,
  crankPin,
  lobeAngle,
  pistonPinY,
  PIN_PHASE,
  sparkFlash,
  valveLift,
} from "../mechanics";

type Common = { readonly theta: number; readonly omegaE: number; readonly t: number };

const blockMidX = ENG.x;
const blockLenZ = ENG.blockZ1 - ENG.blockZ0;
const blockMidZ = (ENG.blockZ0 + ENG.blockZ1) / 2;

/** Valve geometry: unit direction from cam centre to valve head, and its length. */
const valveAxis = (kind: "intake" | "exhaust") => {
  const s = kind === "intake" ? -1 : 1;
  const camX = ENG.x + s * ENG.camDX;
  const headX = ENG.x + s * ENG.valveDX;
  const dx = headX - camX;
  const dy = ENG.chamberTopY - ENG.camY;
  const len = Math.hypot(dx, dy);
  return { camX, ux: dx / len, uy: dy / len, len, angle: Math.atan2(dx, dy) };
};
export const VALVES = { intake: valveAxis("intake"), exhaust: valveAxis("exhaust") };

export const EngineBlock: React.FC<{ readonly highlight: number; readonly t: number; readonly beltOpacity: number; readonly theta: number }> = ({
  highlight,
  t,
  beltOpacity,
  theta,
}) => {
  const g = useMemo(
    () => ({
      block: rbox(ENG.blockHalfX * 2, ENG.deckY - ENG.crankcaseY0, blockLenZ, 0.02),
      head: rbox(ENG.headHalfX * 2, ENG.headTopY - ENG.deckY, blockLenZ, 0.015),
      cover: rbox(0.2, ENG.coverTopY - ENG.headTopY, blockLenZ - 0.03, 0.03),
      liner: cylY(ENG.boreR + 0.004, ENG.deckY - 0.49, 32),
      belt: smoothTube(
        beltLoop(
          [
            { x: ENG.x, y: ENG.crankY, r: ENG.crankSprocketR + 0.006 },
            { x: ENG.x - ENG.camDX, y: ENG.camY, r: ENG.camSprocketR + 0.006 },
            { x: ENG.x + ENG.camDX, y: ENG.camY, r: ENG.camSprocketR + 0.006 },
          ],
          ENG.beltZ,
        ),
        0.006,
        160,
        true,
      ),
      tensioner: cylZ(0.018, 0.02),
    }),
    [],
  );
  return (
    <group>
      <Glass geometry={g.block} color={COLORS.glass} opacity={0.26} highlight={highlight} t={t} position={[blockMidX, (ENG.deckY + ENG.crankcaseY0) / 2, blockMidZ]} />
      <Glass geometry={g.head} color="#9DB9DA" opacity={0.24} highlight={highlight} t={t} position={[blockMidX, (ENG.headTopY + ENG.deckY) / 2, blockMidZ]} />
      <Glass geometry={g.cover} color="#B9CCE6" opacity={0.16} highlight={highlight} t={t} position={[blockMidX, (ENG.coverTopY + ENG.headTopY) / 2, blockMidZ - 0.015]} />
      {ENG.cylZ.map((z) => (
        <Glass key={z} geometry={g.liner} color="#CFE0F2" opacity={0.18} edges={false} highlight={highlight * 0.5} t={t} position={[ENG.x, (ENG.deckY + 0.49) / 2, z]} />
      ))}
      {beltOpacity > 0.01 ? (
        <group>
          <Toon geometry={g.belt} color="#3B4658" outline={0} opacity={beltOpacity} />
          <Toon geometry={g.tensioner} color={COLORS.metal} outline={SIZES.outline} opacity={beltOpacity} position={[ENG.x + 0.075, 0.6, ENG.beltZ]} rotation={[0, 0, theta]} />
        </group>
      ) : null}
    </group>
  );
};

export const Pistons: React.FC<Common & { readonly highlight: number }> = ({ theta, highlight, t }) => {
  const g = useMemo(
    () => ({
      piston: cylY(ENG.boreR - 0.002, ENG.pistonH, 32),
      ring: torusZ(ENG.boreR - 0.0015, 0.0025).rotateX(Math.PI / 2),
      pin: cylZ(0.011, 0.07, 16),
      rod: rbox(0.024, ENG.rod, 0.026, 0.008),
      bigEnd: cylZ(0.03, 0.03, 28),
      smallEnd: cylZ(0.017, 0.028, 20),
    }),
    [],
  );
  return (
    <group>
      {ENG.cylZ.map((z, i) => {
        const pinY = pistonPinY(theta, i);
        const cp = crankPin(theta, i);
        const dx = ENG.x - cp.x;
        const dy = pinY - cp.y;
        const crownY = pinY + ENG.pinToCrown;
        const pcY = crownY - ENG.pistonH / 2;
        return (
          <group key={z}>
            <Toon geometry={g.piston} color={COLORS.piston} highlight={highlight} t={t} position={[ENG.x, pcY, z]} />
            <Toon geometry={g.ring} color={COLORS.metalDark} outline={0} position={[ENG.x, crownY - 0.012, z]} />
            <Toon geometry={g.ring} color={COLORS.metalDark} outline={0} position={[ENG.x, crownY - 0.024, z]} />
            <Toon geometry={g.pin} color={COLORS.metalDark} outline={0} position={[ENG.x, pinY, z]} />
            <Toon
              geometry={g.rod}
              color={COLORS.rod}
              highlight={highlight}
              t={t}
              position={[(ENG.x + cp.x) / 2, (pinY + cp.y) / 2, z]}
              rotation={[0, 0, Math.atan2(-dx, dy)]}
            />
            <Toon geometry={g.smallEnd} color={COLORS.rod} highlight={highlight} t={t} position={[ENG.x, pinY, z]} />
            <Toon geometry={g.bigEnd} color={COLORS.rod} highlight={highlight} t={t} position={[cp.x, cp.y, z]} />
          </group>
        );
      })}
    </group>
  );
};

const webShape = () => {
  const r = ENG.throw;
  const s = new Shape();
  const a0 = (215 * Math.PI) / 180;
  const a1 = (325 * Math.PI) / 180;
  const cw = 0.066;
  s.moveTo(0.03, 0);
  s.lineTo(0.03, r);
  s.absarc(0, r, 0.03, 0, Math.PI, false);
  s.lineTo(-0.03, 0);
  s.lineTo(cw * Math.cos(a0), cw * Math.sin(a0));
  s.absarc(0, 0, cw, a0, a1, false);
  s.lineTo(0.03, 0);
  return s;
};

export const Crankshaft: React.FC<Common & { readonly highlight: number }> = ({ theta, highlight, t }) => {
  const g = useMemo(() => {
    const zs = [...ENG.cylZ].sort((a, b) => a - b);
    const journals: { z: number; len: number }[] = [];
    let prev = -0.15;
    for (const z of zs) {
      journals.push({ z: (prev + z - 0.04) / 2, len: z - 0.04 - prev });
      prev = z + 0.04;
    }
    journals.push({ z: (prev + ENG.beltZ + 0.04) / 2, len: ENG.beltZ + 0.04 - prev });
    return {
      web: extrudeZ(webShape(), 0.014, 0.002, 1, 20),
      pin: cylZ(0.02, 0.056, 20),
      journal: cylZ(0.021, 1, 20),
      journals,
      flywheel: gearGeometry(60, 0.004, 0.022, 0.001),
      flyDisc: cylZ(0.105, 0.024, 48),
      sprocket: gearGeometry(18, (2 * ENG.crankSprocketR) / 18, 0.016, 0.001),
      pulley: cylZ(0.05, 0.02, 36),
      mark: cylZ(0.008, 0.006, 12),
    };
  }, []);
  return (
    <group position={[ENG.x, ENG.crankY, 0]} rotation={[0, 0, -theta]}>
      {g.journals.map((j) => (
        <Toon key={j.z} geometry={g.journal} color={COLORS.crank} highlight={highlight} t={t} position={[0, 0, j.z]} scale={[1, 1, j.len]} outline={0.004} />
      ))}
      {ENG.cylZ.map((z, i) => (
        <group key={z} rotation={[0, 0, -PIN_PHASE[i]]}>
          <Toon geometry={g.web} color={COLORS.crank} highlight={highlight} t={t} position={[0, 0, z - 0.034]} />
          <Toon geometry={g.web} color={COLORS.crank} highlight={highlight} t={t} position={[0, 0, z + 0.034]} />
          <Toon geometry={g.pin} color="#8796A8" highlight={highlight} t={t} position={[0, ENG.throw, z]} />
        </group>
      ))}
      <Toon geometry={g.flywheel} color="#7C8A9B" highlight={highlight} t={t} position={[0, 0, ENG.flywheelZ]} />
      <Toon geometry={g.flyDisc} color="#97A4B4" outline={0} position={[0, 0, ENG.flywheelZ]} />
      <Toon geometry={g.mark} color={COLORS.highlight} outline={0} position={[0, 0.085, ENG.flywheelZ + 0.014]} />
      <Toon geometry={g.sprocket} color="#AEB9C7" highlight={highlight} t={t} position={[0, 0, ENG.beltZ]} />
      <Toon geometry={g.mark} color={COLORS.power} outline={0} position={[0, 0.024, ENG.beltZ + 0.01]} />
      <Toon geometry={g.pulley} color="#5B6878" outline={0.004} position={[0, 0, ENG.beltZ + 0.035]} />
    </group>
  );
};

export const CamsAndValves: React.FC<Common & { readonly highlight: number }> = ({ theta, highlight, t }) => {
  const g = useMemo(
    () => ({
      shaft: cylZ(0.011, ENG.beltZ + 0.13, 16),
      lobe: camLobeGeometry(ENG.camBaseR, ENG.camLift, CAM_HALF_WIDTH, 0.022),
      sprocket: gearGeometry(36, (2 * ENG.camSprocketR) / 36, 0.016, 0.001),
      mark: cylZ(0.009, 0.006, 12),
      stem: cylY(0.0042, 1, 10),
      head: cylY(ENG.valveHeadR, 0.006, 24, ENG.valveHeadR * 0.55),
      bucket: cylY(0.012, 0.016, 18),
      spring: cylY(0.0095, 1, 16),
    }),
    [],
  );
  const camAngle = theta / 2; // timing belt 1:2
  return (
    <group>
      {(["intake", "exhaust"] as const).map((kind) => {
        const v = VALVES[kind];
        // lobe at local angle β points at world angle β + θ/2 (rotation.z = −θ/2)
        return (
          <group key={kind}>
            <group position={[v.camX, ENG.camY, 0]} rotation={[0, 0, -camAngle]}>
              <Toon geometry={g.shaft} color={COLORS.cam} highlight={highlight} t={t} position={[0, 0, (ENG.beltZ - 0.14) / 2 + 0.005]} outline={0.003} />
              {ENG.cylZ.map((z, i) => (
                <Toon
                  key={z}
                  geometry={g.lobe}
                  color={COLORS.cam}
                  highlight={highlight}
                  t={t}
                  position={[0, 0, z]}
                  rotation={[0, 0, -lobeAngle(i, kind, v.angle)]}
                />
              ))}
              <Toon geometry={g.sprocket} color="#C3B2F0" highlight={highlight} t={t} position={[0, 0, ENG.beltZ]} />
              <Toon geometry={g.mark} color={COLORS.power} outline={0} position={[0, 0.05, ENG.beltZ + 0.01]} />
            </group>
            {ENG.cylZ.map((z, i) => {
              const lift = valveLift(theta, i, kind);
              const top = ENG.camBaseR + lift; // distance cam centre → bucket top
              const stemLen = v.len - ENG.camBaseR - 0.003; // constant: the whole valve moves by `lift`
              const along = (d: number): [number, number, number] => [v.camX + v.ux * d, ENG.camY + v.uy * d, z];
              return (
                <group key={z}>
                  <Toon geometry={g.bucket} color="#DCE3EC" highlight={highlight} t={t} position={along(top + 0.008)} rotation={[0, 0, -v.angle + Math.PI]} outline={0.003} />
                  <Toon geometry={g.spring} color="#9FB0C4" outline={0} opacity={0.75} position={along(top + 0.03)} rotation={[0, 0, -v.angle + Math.PI]} scale={[1, 0.035, 1]} />
                  <Toon geometry={g.stem} color={COLORS.valve} outline={0} position={along(top + stemLen / 2)} rotation={[0, 0, -v.angle + Math.PI]} scale={[1, stemLen, 1]} />
                  <Toon geometry={g.head} color={kind === "intake" ? "#CFE6FF" : "#F2D9C6"} highlight={highlight} t={t} position={along(v.len + lift - 0.003)} rotation={[0, 0, -v.angle + Math.PI]} outline={0.003} />
                </group>
              );
            })}
          </group>
        );
      })}
    </group>
  );
};

export const SparkPlugs: React.FC<Common & { readonly highlight: number; readonly emphasis: number; readonly onTop: boolean }> = ({
  theta,
  omegaE,
  highlight,
  t,
  emphasis,
  onTop,
}) => {
  const g = useMemo(
    () => ({
      insulator: cylY(0.0095, 0.15, 16),
      body: cylY(0.012, 0.028, 6),
      tip: cylY(0.0035, 0.01, 8),
      cap: cylY(0.017, 0.07, 20),
      glow: sphere(1, 20),
    }),
    [],
  );
  const glow = useMemo(() => {
    const hot = makeGlow(COLORS.spark, 1);
    const soft = makeGlow("#FFC56B", 0.9);
    return { hot, soft };
  }, []);
  // in the engine close-up the little combustion flash must not hide behind valves/cams
  glow.hot.depthTest = !onTop;
  glow.soft.depthTest = !onTop;
  return (
    <group>
      {ENG.cylZ.map((z, i) => {
        const f = sparkFlash(theta, i, omegaE);
        return (
          <group key={z}>
            <Toon geometry={g.tip} color="#B8C2CE" outline={0} position={[ENG.x, ENG.chamberTopY - 0.002, z]} />
            <Toon geometry={g.body} color="#AEB8C4" highlight={highlight} t={t} position={[ENG.x, ENG.chamberTopY + 0.016, z]} outline={0.003} />
            <Toon geometry={g.insulator} color={COLORS.plug} highlight={highlight} t={t} position={[ENG.x, ENG.chamberTopY + 0.105, z]} outline={0.003} />
            <Toon geometry={g.cap} color={COLORS.plugCap} highlight={Math.max(highlight, f)} t={t} position={[ENG.x, ENG.coverTopY + 0.02, z]} />
            {f > 0.01 ? (
              <group>
                {/* tiny bright spark at the electrode + a short soft flash in the chamber */}
                <mesh geometry={g.glow} material={glow.hot} position={[ENG.x, ENG.chamberTopY - 0.008, z]} scale={0.012 + 0.012 * f * (1 + emphasis)} renderOrder={30} />
                <mesh
                  geometry={g.glow}
                  material={glow.soft}
                  position={[ENG.x, ENG.chamberTopY - 0.016, z]}
                  scale={[0.058 * f * (1 + 0.3 * emphasis), 0.026 * f + 0.004, 0.058 * f * (1 + 0.3 * emphasis)]}
                  renderOrder={30}
                />
              </group>
            ) : null}
          </group>
        );
      })}
    </group>
  );
};
