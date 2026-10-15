import { ThreeCanvas } from "@remotion/three";
import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ramp, smooth } from "../../lib/anim";
import { COLORS } from "../../style/theme";
import { CameraRig } from "../../three/CameraRig";
import { CarBody } from "../../three/car/CarBody";
import { CAR, WHEELS } from "../../three/car/carLayout";
import { Wheel } from "../../three/car/Wheel";
import { FlowDots, PowerArrows, Puffs, WindWaves } from "../../three/effects/Effects";
import { Fade } from "../../three/Fade";
import { Ground } from "../../three/Ground";
import { ENG, FUEL_LINE, GBX, OIL_PATH, OUT_SHAFT, RADIATOR, TAILPIPE } from "../layout";
import type { Drive } from "../mechanics";
import type { PartId } from "../parts";
import { WHEEL_EXPLODE } from "../parts";
import { cameraPose, explodeOffset, sceneState } from "../state";
import type { Timeline } from "../timeline";
import { CamsAndValves, Crankshaft, EngineBlock, Pistons, SparkPlugs } from "./Engine";
import {
  ExhaustManifold,
  ExhaustPipe,
  FuelLine,
  FuelTank,
  Gearbox,
  HalfShafts,
  IntakeManifold,
  OilPan,
  Radiator,
  RearAxle,
} from "./Systems";

type V3 = readonly [number, number, number];

/** Exploded-view offset + ghosting for one registered part. */
const Ex: React.FC<{ readonly id: PartId; readonly e: number; readonly ghost: number; readonly children: React.ReactNode }> = ({
  id,
  e,
  ghost,
  children,
}) => {
  const o = explodeOffset(id, e);
  return (
    <group position={[o[0], o[1], o[2]]}>
      <Fade value={ghost}>{children}</Fade>
    </group>
  );
};

export const GasCarScene3D: React.FC<{ readonly tl: Timeline; readonly drive: Drive }> = ({ tl, drive }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const st = sceneState(tl, drive, frame);
  const pose = cameraPose(tl, st.t);
  const { theta, omegaE, wheel } = st.drive;
  const e = st.explode;
  const t = st.t;

  // power path: crank → engaged gear pair → output shaft → differential → both half-shafts
  const engaged = st.drive.shiftU >= 0.5 ? st.drive.gear : st.drive.gearFrom;
  const gz = engaged > 0 ? GBX.gears[engaged - 1].z : GBX.gears[0].z;
  const powerPaths = useMemo(() => {
    const common: V3[] = [
      [ENG.x, ENG.crankY + 0.07, 0.3],
      [ENG.x, ENG.crankY + 0.07, gz],
      [OUT_SHAFT.x, OUT_SHAFT.y + 0.07, gz],
      [OUT_SHAFT.x, OUT_SHAFT.y + 0.07, GBX.diffZ],
      [GBX.diffX, GBX.diffY + 0.06, GBX.diffZ],
    ];
    return {
      left: [...common, [GBX.diffX, GBX.diffY + 0.06, -CAR.trackHalf + 0.05]] as V3[],
      right: [...common, [GBX.diffX, GBX.diffY + 0.06, GBX.diffZ + 0.2], [GBX.diffX, GBX.diffY + 0.06, CAR.trackHalf - 0.05]] as V3[],
    };
  }, [gz]);

  const fanAngle = Math.PI * 2 * 2.2 * Math.max(0, t - tl.ev.radiatorHL) * smooth(ramp(t, tl.ev.radiatorHL, tl.ev.radiatorHL + 1));
  const pengEmph = Math.max(0, 1 - Math.abs(t - tl.ev.peng) / 0.35);
  // arrows scale with how far the camera is pulled back (close-up → small)
  const arrowSize = 0.012 + 0.024 * smooth(ramp(t, tl.ev.wheelsShow, tl.ev.wheelsShow + 1.6));

  return (
    <ThreeCanvas width={width} height={height} flat gl={{ antialias: true, alpha: true }} style={{ position: "absolute", inset: 0 }}>
      <CameraRig pose={pose} />
      <ambientLight intensity={1.15} />
      <hemisphereLight args={["#ffffff", "#bcd6ef", 0.9]} />
      <directionalLight position={[3, 7, 5]} intensity={1.9} />
      <directionalLight position={[-4, 3, -3]} intensity={0.5} />

      <Ground scroll={st.drive.dist} />

      {/* ---- fuel ---- */}
      <Ex id="fuelTank" e={e} ghost={st.ghost.fuelTank}>
        <FuelTank highlight={st.hl.fuelTank} t={t} />
      </Ex>
      <Ex id="fuelLine" e={e} ghost={st.ghost.fuelLine}>
        <FuelLine highlight={st.hl.fuelLine} t={t} />
        <FlowDots path={FUEL_LINE} time={st.fuelFlow} speed={0.95} spacing={0.28} color={COLORS.fuel} size={0.036} opacity={st.fuelVis} />
      </Ex>

      {/* ---- engine ---- */}
      <Ex id="block" e={e} ghost={st.ghost.block}>
        <EngineBlock highlight={st.hl.block} t={t} beltOpacity={1 - smooth(e * 4)} theta={theta} />
      </Ex>
      <Ex id="pistons" e={e} ghost={st.ghost.pistons}>
        <Pistons theta={theta} omegaE={omegaE} t={t} highlight={st.hl.pistons} />
      </Ex>
      <Ex id="crankshaft" e={e} ghost={st.ghost.crankshaft}>
        <Crankshaft theta={theta} omegaE={omegaE} t={t} highlight={st.hl.crankshaft} />
      </Ex>
      <Ex id="camValves" e={e} ghost={st.ghost.camValves}>
        <CamsAndValves theta={theta} omegaE={omegaE} t={t} highlight={st.hl.camValves} />
      </Ex>
      <Ex id="sparkPlugs" e={e} ghost={st.ghost.sparkPlugs}>
        <SparkPlugs
          theta={theta}
          omegaE={omegaE}
          t={t}
          highlight={st.hl.sparkPlugs}
          emphasis={pengEmph}
          onTop={t >= tl.seg.engine.start && t < tl.seg.gearbox.start}
        />
      </Ex>
      <Ex id="intake" e={e} ghost={st.ghost.intake}>
        <IntakeManifold highlight={st.hl.intake} t={t} />
      </Ex>
      <Ex id="exhaustManifold" e={e} ghost={st.ghost.exhaustManifold}>
        <ExhaustManifold highlight={st.hl.exhaustManifold} t={t} heat={st.exhaustHeat} />
      </Ex>
      <Ex id="exhaustPipe" e={e} ghost={st.ghost.exhaustPipe}>
        <ExhaustPipe highlight={st.hl.exhaustPipe} t={t} heat={st.exhaustHeat} />
        <Puffs at={TAILPIPE[1]} time={t} amount={st.puffs} />
      </Ex>
      <Ex id="oil" e={e} ghost={st.ghost.oil}>
        <OilPan highlight={st.hl.oil} t={t} />
      </Ex>
      <FlowDots path={OIL_PATH} time={st.oilFlow} speed={0.75} spacing={0.11} color="#FFB13B" size={0.02} opacity={st.oilVis * (1 - smooth(e * 5))} loop />

      {/* ---- drivetrain ---- */}
      <Ex id="gearbox" e={e} ghost={st.ghost.gearbox}>
        <Gearbox
          highlight={st.hl.gearbox}
          t={t}
          theta={theta}
          wheel={wheel}
          gear={st.drive.gear}
          gearFrom={st.drive.gearFrom}
          shiftU={st.drive.shiftU}
        />
      </Ex>
      <Ex id="halfShafts" e={e} ghost={st.ghost.halfShafts}>
        <HalfShafts highlight={st.hl.halfShafts} t={t} wheel={wheel} />
      </Ex>
      <PowerArrows path={powerPaths.left} time={t} opacity={st.powerArrows * (1 - e)} size={arrowSize} spacing={arrowSize * 4.5} />
      <PowerArrows path={powerPaths.right} time={t} opacity={st.powerArrows * (1 - e)} size={arrowSize} spacing={arrowSize * 4.5} />

      {/* ---- cooling ---- */}
      <Ex id="radiator" e={e} ghost={st.ghost.radiator}>
        <Radiator highlight={st.hl.radiator} t={t} fanAngle={fanAngle} />
        <WindWaves at={[RADIATOR.x + 0.32, (RADIATOR.y0 + RADIATOR.y1) / 2, 0]} time={t} amount={st.wind} />
      </Ex>

      <RearAxle />
      {WHEELS.map((w) => {
        const o = WHEEL_EXPLODE[w.id];
        return (
          <Fade key={w.id} value={w.id === "FL" ? st.ghost.wheelFL : w.id === "FR" ? st.ghost.wheelFR : 1}>
          <Wheel
            position={[w.x + o[0] * e, CAR.wheelR + o[1] * e, w.z + o[2] * e]}
            side={w.z > 0 ? 1 : -1}
            angle={wheel}
            highlight={w.driven ? st.hl.wheels : st.hl.wheels * 0.3}
            t={t}
          />
          </Fade>
        );
      })}

      <CarBody xray={st.xray} smile={0.35 + 0.65 * st.smile} t={t} />
    </ThreeCanvas>
  );
};
