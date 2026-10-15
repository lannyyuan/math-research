/** Per-frame EV scene state — pure function of (timeline, frame), shared by 3D, overlay and checks. */
import { ramp, smooth, smoother, window } from "../lib/anim";
import { cameraAt } from "../lib/camera";
import { MODULES } from "./layout";
import type { EvDrive, EvDriveState } from "./mechanics";
import { EV_PART_IDS, EV_PARTS, EV_WHEEL_EXPLODE, type EvPartId } from "./parts";
import type { EvTimeline } from "./timeline";

type V3 = readonly [number, number, number];

export type EvSceneState = {
  t: number;
  frame: number;
  drive: EvDriveState;
  xray: number;
  hl: Record<EvPartId, number>;
  explode: number;
  /** 0..1 per cell module, lit one after another. */
  modules: number[];
  batteryGlow: number;
  /** Blue current: DC battery → controller, and controller → motor phases. */
  dcCurrent: number;
  acCurrent: number;
  ctrlActivity: number;
  speedLines: number;
  cleanAir: number;
  smile: number;
  ghost: Record<EvPartId | "wheelFL" | "wheelFR", number>;
};

export const evState = (tl: EvTimeline, drive: EvDrive, frame: number): EvSceneState => {
  const t = frame / tl.fps;
  const { ev, seg } = tl;
  const C = seg.controller.start;
  const M = seg.motor.start;
  const R = seg.reducer.start;
  const Q = seg.rear.start;
  const X = seg.explode.start;
  const d = drive.at(frame);

  const xray = smooth(ramp(t, ev.xrayOn[0], ev.xrayOn[1])) * (1 - smooth(ramp(t, ev.xrayOff[0], ev.xrayOff[1])));
  const explode =
    smoother(ramp(t, ev.explodeOut[0], ev.explodeOut[1])) * (1 - smoother(ramp(t, ev.merge[0], ev.merge[1])));
  const explodeGlow = 0.3 * window(t, ev.labelsIn, ev.labelsOut + 0.3, 0.5, 0.5);
  const hl = {} as Record<EvPartId, number>;
  const set = (id: EvPartId, v: number) => (hl[id] = Math.min(1, Math.max(v, explodeGlow)));
  set("battery", window(t, ev.batteryHL, C + 0.6, 0.35, 0.6));
  set("harness", 0.8 * window(t, ev.harnessLabel - 0.2, M + 0.6, 0.3, 0.5));
  set("controller", window(t, ev.controllerHL, M + 0.6, 0.3, 0.5));
  set("motor", window(t, ev.motorHL, R + 0.4, 0.3, 0.5));
  set("reducer", window(t, ev.reducerHL, Q + 0.3, 0.3, 0.5));
  set("halfShafts", window(t, ev.wheelsShow, Q + 0.3, 0.3, 0.5));
  set("wheels", window(t, ev.wheelsShow, Q + 0.3, 0.3, 0.5));

  const span = ev.modulesLit[1] - ev.modulesLit[0];
  const per = span / (MODULES.length + 2);
  const lit = MODULES.map((m) => smooth(ramp(t, ev.modulesLit[0] + m.order * per, ev.modulesLit[0] + (m.order + 1.4) * per)));
  // modules stay softly lit (charged) once they have lit up, and dim back to normal after the battery segment
  const keep = 1 - 0.75 * smooth(ramp(t, C + 0.2, C + 1.2));
  const modules = lit.map((v) => v * keep);
  const batteryGlow = window(t, ev.batteryHL, C + 1.2, 0.5, 0.8);

  const running = d.omegaW > 0.01 ? 1 : 0;
  const dcCurrent = Math.max(window(t, ev.dcCurrent, M + 0.8, 0.5, 0.6) * (t < M ? 1 : 0.6), running * window(t, ev.driveStart - 0.3, X + 0.5, 0.3, 0.5));
  const acCurrent = running * window(t, ev.driveStart - 0.3, X + 0.5, 0.3, 0.5) * (0.5 + 0.5 * d.power);
  const ctrlActivity = Math.max(window(t, ev.controllerHL, M + 1.0, 0.3, 0.5), acCurrent);

  const fCtrl = window(t, C + 0.8, M + 0.6, 0.8, 0.8);
  const fMotor = window(t, M + 0.6, R + 0.5, 0.9, 0.8);
  const fRed = window(t, R + 0.3, ev.wheelsShow + 0.6, 0.8, 0.7);
  const g = {} as EvSceneState["ghost"];
  for (const id of EV_PART_IDS) g[id] = 1;
  g.wheelFR = 1 - Math.max(0.5 * fCtrl, 0.85 * fMotor, 0.6 * fRed);
  g.wheelFL = 1 - Math.max(0.85 * fRed, 0.4 * fMotor);
  g.controller = 1 - Math.max(0.7 * fMotor, 0.65 * fRed);
  g.harness = 1 - Math.max(0.4 * fMotor, 0.5 * fRed);
  g.motor = 1 - 0.55 * fRed;
  g.battery = 1 - 0.3 * fMotor;

  return {
    t,
    frame,
    drive: d,
    xray,
    hl,
    explode,
    modules,
    batteryGlow,
    dcCurrent,
    acCurrent,
    ctrlActivity,
    speedLines: Math.min(1, d.omegaR / 1.5) * (1 - explode),
    cleanAir: window(t, ev.noExhaust, X + 0.4, 0.5, 0.6),
    smile: smooth(ramp(t, ev.smile, ev.smile + 0.6)),
    ghost: g,
  };
};

export const evCameraPose = (tl: EvTimeline, t: number) => cameraAt(tl.camKeys, t);

export const evExplodeOffset = (id: EvPartId, e: number): V3 => {
  const o = EV_PARTS[id].explode;
  return [o[0] * e, o[1] * e, o[2] * e];
};
export const evLabelAnchor = (id: EvPartId, e: number): V3 => {
  const a = EV_PARTS[id].anchor;
  const o = id === "wheels" ? EV_WHEEL_EXPLODE.FR : EV_PARTS[id].explode;
  return [a[0] + o[0] * e, a[1] + o[1] * e, a[2] + o[2] * e];
};
