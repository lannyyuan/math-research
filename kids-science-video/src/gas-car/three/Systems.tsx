/** Fuel, intake, exhaust, gearbox, half-shafts, cooling and lubrication systems. */
import React, { useMemo } from "react";
import { Color } from "three";
import { COLORS, SIZES } from "../../style/theme";
import { CAR } from "../../three/car/carLayout";
import { capsuleX, capsuleZ, cylY, cylZ, gearGeometry, rbox, sphere, torusZ, tubeAlong } from "../../three/geometry";
import { Glass } from "../../three/Glass";
import { makeGlow } from "../../three/materials";
import { Toon } from "../../three/Toon";
import {
  AIR_PIPE,
  CATALYST,
  ENG,
  EXHAUST_COLLECTOR,
  EXHAUST_PIPE,
  FAN,
  FUEL_LINE,
  FUEL_RAIL,
  GBX,
  INTAKE,
  LOWER_HOSE,
  MUFFLER,
  OUT_SHAFT,
  RADIATOR,
  TAILPIPE,
  TANK,
  UPPER_HOSE,
} from "../layout";
import { meshPhase } from "../mechanics";

type HL = { readonly highlight: number; readonly t: number };

const cylX = (r: number, len: number) => cylZ(r, len).rotateY(Math.PI / 2);

export const FuelTank: React.FC<HL> = ({ highlight, t }) => {
  const g = useMemo(
    () => ({
      tank: rbox(TANK.x1 - TANK.x0, TANK.y1 - TANK.y0, TANK.z1 - TANK.z0, 0.07),
      neck: tubeAlong(
        [
          [-1.0, 0.56, 0.4],
          [-1.25, 0.72, 0.6],
          [-1.55, 0.86, 0.8],
        ],
        0.028,
        0.08,
      ),
      cap: cylZ(0.055, 0.03, 24),
      pump: cylY(0.05, 0.1, 20),
    }),
    [],
  );
  return (
    <group>
      <Toon geometry={g.tank} color={COLORS.fuelTank} highlight={highlight} t={t} outline={0.01} position={[(TANK.x0 + TANK.x1) / 2, (TANK.y0 + TANK.y1) / 2, 0]} />
      <Toon geometry={g.pump} color="#1F8F7E" highlight={highlight} t={t} position={[-0.52, 0.62, 0.3]} />
      <Toon geometry={g.neck} color={COLORS.fuelTank} highlight={highlight} t={t} outlineMode="normal" />
      <Toon geometry={g.cap} color={COLORS.fuel} highlight={highlight} t={t} position={[-1.56, 0.865, 0.81]} />
    </group>
  );
};

export const FuelLine: React.FC<HL> = ({ highlight, t }) => {
  const g = useMemo(
    () => ({
      line: tubeAlong(FUEL_LINE, 0.011, 0.06),
      rail: cylZ(FUEL_RAIL.r, FUEL_RAIL.z1 - FUEL_RAIL.z0, 16),
      injector: cylY(0.0075, 0.06, 12),
    }),
    [],
  );
  return (
    <group>
      <Toon geometry={g.line} color={COLORS.fuelLine} highlight={highlight} t={t} outlineMode="normal" outline={0.004} />
      <Toon geometry={g.rail} color={COLORS.fuelLine} highlight={highlight} t={t} position={[FUEL_RAIL.x, FUEL_RAIL.y, (FUEL_RAIL.z0 + FUEL_RAIL.z1) / 2]} outline={0.004} />
      {ENG.cylZ.map((z) => (
        <Toon key={z} geometry={g.injector} color="#E7E0C8" highlight={highlight} t={t} position={[FUEL_RAIL.x, FUEL_RAIL.y - 0.035, z]} outline={0.003} />
      ))}
    </group>
  );
};

export const IntakeManifold: React.FC<HL> = ({ highlight, t }) => {
  const g = useMemo(
    () => ({
      plenum: capsuleZ(INTAKE.plenumR, INTAKE.z1 - INTAKE.z0 - INTAKE.plenumR),
      runners: ENG.cylZ.map((z) =>
        tubeAlong(
          [
            [ENG.x - ENG.headHalfX + 0.005, 0.718, z],
            [1.29, 0.718, z],
            [INTAKE.plenumX + 0.02, INTAKE.plenumY - 0.01, z],
          ],
          0.022,
          0.05,
          32,
        ),
      ),
      air: tubeAlong(AIR_PIPE, 0.034, 0.08, 64),
      mouth: torusZ(0.034, 0.008).rotateY(Math.PI / 2),
    }),
    [],
  );
  return (
    <group>
      <Toon geometry={g.plenum} color={COLORS.intake} highlight={highlight} t={t} position={[INTAKE.plenumX, INTAKE.plenumY, (INTAKE.z0 + INTAKE.z1) / 2]} />
      {g.runners.map((r, i) => (
        <Toon key={i} geometry={r} color={COLORS.intake} highlight={highlight} t={t} outlineMode="normal" outline={0.004} />
      ))}
      <Toon geometry={g.air} color="#7DBDF7" highlight={highlight} t={t} outlineMode="normal" outline={0.004} />
      <Toon geometry={g.mouth} color="#2F80D0" outline={0} position={[AIR_PIPE[AIR_PIPE.length - 1][0], AIR_PIPE[AIR_PIPE.length - 1][1], AIR_PIPE[AIR_PIPE.length - 1][2]]} />
    </group>
  );
};

export const ExhaustManifold: React.FC<HL & { readonly heat: number }> = ({ highlight, t, heat }) => {
  const g = useMemo(() => {
    const runnerPts = ENG.cylZ.map(
      (z) =>
        [
          [ENG.x + ENG.headHalfX - 0.005, 0.716, z],
          [1.675, 0.716, z],
          [1.725, 0.6, z + (EXHAUST_COLLECTOR[2] - z) * 0.6],
          [EXHAUST_COLLECTOR[0], EXHAUST_COLLECTOR[1] + 0.02, EXHAUST_COLLECTOR[2]],
        ] as const,
    );
    return {
      runners: runnerPts.map((p) => tubeAlong(p, 0.021, 0.05, 40)),
      halos: runnerPts.map((p) => tubeAlong(p, 0.034, 0.05, 40)),
      collector: sphere(0.042, 24),
    };
  }, []);
  const glow = useMemo(() => makeGlow(COLORS.exhaustGlow, 0.5), []);
  glow.opacity = 0.42 * heat * (0.85 + 0.15 * Math.sin(t * 5.1));
  const emissive = new Color(COLORS.exhaustGlow);
  return (
    <group>
      {g.runners.map((r, i) => (
        <Toon key={i} geometry={r} color={COLORS.exhaust} highlight={highlight * 0.6} t={t} outlineMode="normal" outline={0.004} emissive={`#${emissive.getHexString()}`} emissiveIntensity={0.85 * heat} />
      ))}
      <Toon geometry={g.collector} color={COLORS.exhaust} highlight={highlight * 0.6} t={t} position={EXHAUST_COLLECTOR} emissive={COLORS.exhaustGlow} emissiveIntensity={0.85 * heat} />
      {heat > 0.01 ? g.halos.map((h, i) => <mesh key={i} geometry={h} material={glow} renderOrder={31} />) : null}
    </group>
  );
};

export const ExhaustPipe: React.FC<HL & { readonly heat: number }> = ({ highlight, t, heat }) => {
  const g = useMemo(
    () => ({
      pipe: tubeAlong(EXHAUST_PIPE, 0.026, 0.12, 160),
      cat: capsuleX(CATALYST.r, CATALYST.x1 - CATALYST.x0 - CATALYST.r * 2),
      muffler: capsuleX(MUFFLER.r, MUFFLER.x1 - MUFFLER.x0 - MUFFLER.r * 2),
      tail: tubeAlong(TAILPIPE, 0.024, 0.01, 8),
      tip: cylX(0.03, 0.05),
    }),
    [],
  );
  return (
    <group>
      <Toon geometry={g.pipe} color={COLORS.exhaust} highlight={highlight} t={t} outlineMode="normal" outline={0.004} emissive={COLORS.exhaustGlow} emissiveIntensity={0.25 * heat} />
      <Toon geometry={g.cat} color="#B39C8C" highlight={highlight} t={t} position={[(CATALYST.x0 + CATALYST.x1) / 2, CATALYST.y, CATALYST.z]} emissive={COLORS.exhaustGlow} emissiveIntensity={0.3 * heat} />
      <Toon geometry={g.muffler} color="#B39C8C" highlight={highlight} t={t} position={[(MUFFLER.x0 + MUFFLER.x1) / 2, MUFFLER.y, MUFFLER.z]} />
      <Toon geometry={g.tail} color={COLORS.exhaust} highlight={highlight} t={t} outlineMode="normal" outline={0.004} />
      <Toon geometry={g.tip} color="#D9DEE5" highlight={highlight} t={t} position={[TAILPIPE[1][0] + 0.015, TAILPIPE[1][1], TAILPIPE[1][2]]} />
    </group>
  );
};

/**
 * 3-speed constant-mesh transaxle. Every output gear spins at its own mesh
 * speed; the sliding sleeve locks the selected one to the output shaft.
 */
export const Gearbox: React.FC<
  HL & { readonly theta: number; readonly wheel: number; readonly gear: number; readonly gearFrom: number; readonly shiftU: number }
> = ({ highlight, t, theta, wheel, gear, gearFrom, shiftU }) => {
  const h = GBX.housing;
  const lambda = Math.atan2(OUT_SHAFT.y - GBX.inY, OUT_SHAFT.x - GBX.inX);
  const lambdaF = Math.atan2(GBX.diffY - OUT_SHAFT.y, GBX.diffX - OUT_SHAFT.x);
  const g = useMemo(
    () => ({
      housing: rbox(h.x1 - h.x0, h.y1 - h.y0, h.z1 - h.z0, 0.06),
      inShaft: cylZ(0.012, 0.32, 16),
      outShaft: cylZ(0.012, 0.34, 16),
      gIn: GBX.gears.map((p) => gearGeometry(p.nIn, GBX.module, GBX.faceW)),
      gOut: GBX.gears.map((p) => gearGeometry(p.nOut, GBX.module, GBX.faceW)),
      pinion: gearGeometry(GBX.final.nPinion, GBX.finalModule, 0.03),
      ring: gearGeometry(GBX.final.nRing, GBX.finalModule, 0.026),
      diff: sphere(0.04, 24),
      sleeve: cylZ(0.024, 0.016, 24),
      clutch: cylZ(0.1, 0.012, 40),
      mark: cylZ(0.006, 0.004, 10),
    }),
    [h],
  );
  // phases so teeth interleave exactly
  const ph = GBX.gears.map((p) => meshPhase(lambda, p.nIn, p.nOut));
  const phF = meshPhase(lambdaF, GBX.final.nPinion, GBX.final.nRing);
  const outRot = wheel * (GBX.final.nRing / GBX.final.nPinion); // output shaft rotation.z
  const ringRot = -outRot * (GBX.final.nPinion / GBX.final.nRing) + phF; // = −wheel + phase
  // sleeves slide towards the engaged gear
  const s = shiftU;
  const sleeveA = (() => {
    // sleeve A serves 1st/2nd, sleeve B serves 3rd
    const neutralA = (GBX.gears[0].z + GBX.gears[1].z) / 2;
    const posFor = (k: number) => (k === 1 ? GBX.gears[0].z - 0.023 : k === 2 ? GBX.gears[1].z + 0.023 : neutralA);
    return posFor(gearFrom) + (posFor(gear) - posFor(gearFrom)) * s;
  })();
  const sleeveB = (() => {
    const neutralB = GBX.gears[2].z - 0.045;
    const posFor = (k: number) => (k === 3 ? GBX.gears[2].z - 0.023 : neutralB);
    return posFor(gearFrom) + (posFor(gear) - posFor(gearFrom)) * s;
  })();
  const engaged = s >= 0.5 ? gear : gearFrom;
  return (
    <group>
      <Glass geometry={g.housing} color={COLORS.gearbox} opacity={0.2} highlight={highlight * 0.5} t={t} position={[(h.x0 + h.x1) / 2, (h.y0 + h.y1) / 2, (h.z0 + h.z1) / 2]} />
      <Toon geometry={g.clutch} color="#C9A27A" highlight={highlight * 0.5} t={t} position={[GBX.inX, GBX.inY, -0.158]} rotation={[0, 0, -theta]} />
      <group position={[GBX.inX, GBX.inY, 0]} rotation={[0, 0, -theta]}>
        <Toon geometry={g.inShaft} color={COLORS.shaft} outline={0.003} position={[0, 0, -0.29]} />
        {GBX.gears.map((p, k) => (
          <Toon key={k} geometry={g.gIn[k]} color={engaged === k + 1 ? COLORS.gear : COLORS.gearIdle} highlight={highlight * (engaged === k + 1 ? 1 : 0)} t={t} position={[0, 0, p.z]} outline={0.003} />
        ))}
      </group>
      <group position={[OUT_SHAFT.x, OUT_SHAFT.y, 0]}>
        <group rotation={[0, 0, outRot]}>
          <Toon geometry={g.outShaft} color={COLORS.shaft} outline={0.003} position={[0, 0, -0.3]} />
          <Toon geometry={g.pinion} color={COLORS.gear} highlight={highlight} t={t} position={[0, 0, GBX.diffZ]} outline={0.003} />
          <Toon geometry={g.sleeve} color="#FF8A5B" highlight={highlight} t={t} position={[0, 0, sleeveA]} outline={0.003} />
          <Toon geometry={g.sleeve} color="#FF8A5B" highlight={highlight} t={t} position={[0, 0, sleeveB]} outline={0.003} />
          <Toon geometry={g.mark} color={COLORS.white} outline={0} position={[0, 0.02, sleeveA + 0.01]} />
        </group>
        {GBX.gears.map((p, k) => (
          <Toon
            key={k}
            geometry={g.gOut[k]}
            color={engaged === k + 1 ? COLORS.gear : COLORS.gearIdle}
            highlight={highlight * (engaged === k + 1 ? 1 : 0)}
            t={t}
            position={[0, 0, p.z]}
            rotation={[0, 0, theta * (p.nIn / p.nOut) + ph[k]]}
            outline={0.003}
          />
        ))}
      </group>
      <group position={[GBX.diffX, GBX.diffY, GBX.diffZ]} rotation={[0, 0, ringRot]}>
        <Toon geometry={g.ring} color={COLORS.gear} highlight={highlight} t={t} outline={0.003} />
        <Toon geometry={g.diff} color="#9AA9BA" highlight={highlight} t={t} position={[0, 0, -0.03]} />
      </group>
    </group>
  );
};

export const HalfShafts: React.FC<HL & { readonly wheel: number }> = ({ highlight, t, wheel }) => {
  const zL0 = GBX.diffZ - 0.045;
  const zL1 = -(CAR.trackHalf - 0.1);
  const zR0 = GBX.diffZ + 0.03;
  const zR1 = CAR.trackHalf - 0.1;
  const g = useMemo(
    () => ({
      left: cylZ(0.017, zL0 - zL1, 16),
      right: cylZ(0.017, zR1 - zR0, 16),
      boot: cylZ(0.035, 0.07, 20, 0.018),
      bootR: cylZ(0.018, 0.07, 20, 0.035),
      fin: rbox(0.012, 0.03, 0.04, 0.004),
    }),
    [zL0, zL1, zR0, zR1],
  );
  const rot = -wheel;
  return (
    <group position={[GBX.diffX, GBX.diffY, 0]}>
      <group rotation={[0, 0, rot]}>
        <Toon geometry={g.left} color={COLORS.shaft} highlight={highlight} t={t} position={[0, 0, (zL0 + zL1) / 2]} outline={0.003} />
        <Toon geometry={g.right} color={COLORS.shaft} highlight={highlight} t={t} position={[0, 0, (zR0 + zR1) / 2]} outline={0.003} />
        {[zL1 + 0.04, zL0 - 0.03].map((z) => (
          <Toon key={z} geometry={z < zL0 - 0.05 ? g.bootR : g.boot} color="#3E4654" highlight={highlight} t={t} position={[0, 0, z]} />
        ))}
        {[zR0 + 0.04, zR1 - 0.04].map((z, k) => (
          <Toon key={z} geometry={k === 0 ? g.bootR : g.boot} color="#3E4654" highlight={highlight} t={t} position={[0, 0, z]} />
        ))}
        {[-0.56, 0.0, 0.35].map((z) => (
          <Toon key={z} geometry={g.fin} color={COLORS.power} outline={0} position={[0, 0.02, z]} />
        ))}
      </group>
    </group>
  );
};

export const Radiator: React.FC<HL & { readonly fanAngle: number }> = ({ highlight, t, fanAngle }) => {
  const r = RADIATOR;
  const g = useMemo(
    () => ({
      core: rbox(r.thick, r.y1 - r.y0, r.z1 - r.z0 - 0.12, 0.01),
      tank: rbox(r.thick + 0.02, r.y1 - r.y0 + 0.02, 0.06, 0.015),
      fin: rbox(0.006, 0.006, r.z1 - r.z0 - 0.14, 0.002),
      upper: tubeAlong(UPPER_HOSE, 0.02, 0.08, 40),
      lower: tubeAlong(LOWER_HOSE, 0.02, 0.08, 40),
      hub: cylX(0.035, 0.05),
      blade: rbox(0.008, 0.15, 0.06, 0.008),
      shroud: torusZ(FAN.r + 0.012, 0.01).rotateY(Math.PI / 2),
    }),
    [r],
  );
  const fins = Array.from({ length: 9 }, (_, i) => r.y0 + 0.04 + (i * (r.y1 - r.y0 - 0.08)) / 8);
  return (
    <group>
      <Toon geometry={g.core} color={COLORS.radiator} highlight={highlight} t={t} position={[r.x, (r.y0 + r.y1) / 2, 0]} outline={0.006} />
      <Toon geometry={g.tank} color="#2A6FB0" highlight={highlight} t={t} position={[r.x, (r.y0 + r.y1) / 2, r.z0 + 0.03]} />
      <Toon geometry={g.tank} color="#2A6FB0" highlight={highlight} t={t} position={[r.x, (r.y0 + r.y1) / 2, r.z1 - 0.03]} />
      {fins.map((y) => (
        <Toon key={y} geometry={g.fin} color="#9FD3FF" outline={0} position={[r.x + r.thick / 2 + 0.002, y, 0]} />
      ))}
      <Toon geometry={g.upper} color="#3B4A5E" highlight={highlight} t={t} outlineMode="normal" outline={0.003} />
      <Toon geometry={g.lower} color="#3B4A5E" highlight={highlight} t={t} outlineMode="normal" outline={0.003} />
      <group position={[FAN.x, FAN.y, FAN.z]}>
        <Toon geometry={g.shroud} color="#4A5A70" outline={0} />
        <group rotation={[fanAngle, 0, 0]}>
          <Toon geometry={g.hub} color="#4A5A70" outline={0.003} />
          {[0, 1, 2, 3, 4].map((k) => (
            <group key={k} rotation={[(k / 5) * Math.PI * 2, 0, 0]}>
              <Toon geometry={g.blade} color="#6E8BAA" highlight={highlight * 0.5} t={t} position={[0, 0.095, 0]} rotation={[0.35, 0, 0]} outline={0.003} />
            </group>
          ))}
        </group>
      </group>
    </group>
  );
};

export const OilPan: React.FC<HL> = ({ highlight, t }) => {
  const g = useMemo(
    () => ({
      pan: rbox(0.2, ENG.crankcaseY0 - ENG.panY0, ENG.blockZ1 - ENG.blockZ0 - 0.02, 0.03),
      oil: rbox(0.18, 0.045, ENG.blockZ1 - ENG.blockZ0 - 0.05, 0.02),
      dipstick: tubeAlong(
        [
          [1.395, 0.27, 0.4],
          [1.35, 0.45, 0.47],
          [1.34, 0.86, 0.47],
        ],
        0.005,
        0.05,
        24,
      ),
      handle: torusZ(0.016, 0.005),
    }),
    [],
  );
  const midZ = (ENG.blockZ0 + ENG.blockZ1) / 2;
  return (
    <group>
      <Glass geometry={g.pan} color="#E6D3B3" opacity={0.3} highlight={highlight * 0.6} t={t} position={[ENG.x, (ENG.crankcaseY0 + ENG.panY0) / 2, midZ]} />
      <Toon geometry={g.oil} color={COLORS.oil} highlight={highlight} t={t} position={[ENG.x, ENG.panY0 + 0.03, midZ]} opacity={0.92} outline={0.003} />
      <Toon geometry={g.dipstick} color="#C9A04A" highlight={highlight} t={t} outline={0} />
      <Toon geometry={g.handle} color={COLORS.fuel} highlight={highlight} t={t} position={[1.34, 0.875, 0.47]} rotation={[0, Math.PI / 2, 0]} />
    </group>
  );
};

export const RearAxle: React.FC = () => {
  const g = useMemo(() => ({ beam: cylZ(0.03, CAR.trackHalf * 2 - 0.2, 16) }), []);
  return <Toon geometry={g.beam} color="#8A97A6" outline={SIZES.outline} position={[CAR.rearAxleX, CAR.wheelR - 0.02, 0]} />;
};
