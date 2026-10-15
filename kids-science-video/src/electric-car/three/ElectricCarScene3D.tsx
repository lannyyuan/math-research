import { ThreeCanvas } from "@remotion/three";
import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { HalfShafts, RearAxle } from "../../gas-car/three/Systems";
import { COLORS } from "../../style/theme";
import { CameraRig } from "../../three/CameraRig";
import { CarBody } from "../../three/car/CarBody";
import { CAR, WHEELS } from "../../three/car/carLayout";
import { Wheel } from "../../three/car/Wheel";
import { CurrentFlow, WindWaves } from "../../three/effects/Effects";
import { Fade } from "../../three/Fade";
import { Ground } from "../../three/Ground";
import { DC_CABLES, PHASE_CABLES, RED, TAIL_SPOT } from "../layout";
import type { EvDrive } from "../mechanics";
import { EV_WHEEL_EXPLODE, type EvPartId } from "../parts";
import { evCameraPose, evExplodeOffset, evState } from "../state";
import type { EvTimeline } from "../timeline";
import { BatteryPack, Controller, Harness, Motor, Reducer } from "./Drive";

const Ex: React.FC<{ readonly id: EvPartId; readonly e: number; readonly ghost: number; readonly children: React.ReactNode }> = ({
  id,
  e,
  ghost,
  children,
}) => {
  const o = evExplodeOffset(id, e);
  return (
    <group position={[o[0], o[1], o[2]]}>
      <Fade value={ghost}>{children}</Fade>
    </group>
  );
};

export const ElectricCarScene3D: React.FC<{ readonly tl: EvTimeline; readonly drive: EvDrive }> = ({ tl, drive }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const st = evState(tl, drive, frame);
  const pose = evCameraPose(tl, st.t);
  const { wheel, rotor } = st.drive;
  const e = st.explode;
  const t = st.t;
  // current pulses glide a bit faster when the motor is working harder
  const flowTime = t * (1 + 0.6 * st.drive.power);

  return (
    <ThreeCanvas width={width} height={height} flat gl={{ antialias: true, alpha: true }} style={{ position: "absolute", inset: 0 }}>
      <CameraRig pose={pose} />
      <ambientLight intensity={1.15} />
      <hemisphereLight args={["#ffffff", "#bcd6ef", 0.9]} />
      <directionalLight position={[3, 7, 5]} intensity={1.9} />
      <directionalLight position={[-4, 3, -3]} intensity={0.5} />

      <Ground scroll={st.drive.dist} />

      <Ex id="battery" e={e} ghost={st.ghost.battery}>
        <BatteryPack highlight={st.hl.battery} t={t} modules={st.modules} glow={st.batteryGlow} />
      </Ex>
      <Ex id="harness" e={e} ghost={st.ghost.harness}>
        <Harness highlight={st.hl.harness} t={t} />
        {/* power always flows battery → controller → motor */}
        {DC_CABLES.map((p, i) => (
          <CurrentFlow key={`dc${i}`} path={p} time={flowTime + i * 0.11} amount={st.dcCurrent * (1 - e)} />
        ))}
        {PHASE_CABLES.map((p, i) => (
          <CurrentFlow key={`ac${i}`} path={p} time={flowTime + i * 0.07} amount={st.acCurrent * (1 - e)} spacing={0.12} size={0.013} />
        ))}
      </Ex>
      <Ex id="controller" e={e} ghost={st.ghost.controller}>
        <Controller highlight={st.hl.controller} t={t} activity={st.ctrlActivity} />
      </Ex>
      <Ex id="motor" e={e} ghost={st.ghost.motor}>
        <Motor highlight={st.hl.motor} t={t} rotor={rotor} current={st.acCurrent} speedLines={st.speedLines} />
      </Ex>
      <Ex id="reducer" e={e} ghost={st.ghost.reducer}>
        <Reducer highlight={st.hl.reducer} t={t} rotor={rotor} wheel={wheel} />
      </Ex>
      <Ex id="halfShafts" e={e} ghost={st.ghost.halfShafts}>
        <HalfShafts highlight={st.hl.halfShafts} t={t} wheel={wheel} diffZ={RED.gearZ} diffX={RED.diffX} diffY={RED.diffY} />
      </Ex>

      <WindWaves at={[TAIL_SPOT[0] - 0.75, 0.42, TAIL_SPOT[2] + 0.25]} time={t * 0.6} amount={0.7 * st.cleanAir} color={COLORS.cleanAir} />

      <RearAxle />
      {WHEELS.map((w) => {
        const o = EV_WHEEL_EXPLODE[w.id];
        return (
          <Fade key={w.id} value={w.id === "FL" ? st.ghost.wheelFL : w.id === "FR" ? st.ghost.wheelFR : 1}>
            <Wheel
              position={[w.x + o[0] * e, CAR.wheelR + o[1] * e, w.z + o[2] * e]}
              side={w.z > 0 ? 1 : -1}
              angle={wheel}
              highlight={w.driven ? st.hl.wheels : st.hl.wheels * 0.3}
              t={t}
              hubColor={COLORS.carGreenLight}
              dotColor={COLORS.carGreen}
            />
          </Fade>
        );
      })}

      <CarBody color={COLORS.carGreen} rim={COLORS.xrayRimGreen} bumper={COLORS.bumperGreen} xray={st.xray} smile={0.35 + 0.65 * st.smile} t={t} />
    </ThreeCanvas>
  );
};
