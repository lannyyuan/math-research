import { PerspectiveCamera, Vector3 } from "three";
import { easeInOutCubic, lerp } from "./anim";

export type Vec3 = readonly [number, number, number];

export type CamPose = {
  readonly pos: Vec3;
  readonly target: Vec3;
  readonly fov: number;
};

/** A keyframe: the camera reaches `pose` at time `t` (seconds) and eases from the previous key. */
export type CamKey = { readonly t: number; readonly pose: CamPose };

const mix3 = (a: Vec3, b: Vec3, u: number): Vec3 => [lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u)];

/** Pure function of time — used by both the three.js scene and the 2D label overlay. */
export const cameraAt = (keys: readonly CamKey[], t: number): CamPose => {
  if (t <= keys[0].t) return keys[0].pose;
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i];
    const b = keys[i + 1];
    if (t <= b.t) {
      const u = easeInOutCubic((t - a.t) / Math.max(1e-6, b.t - a.t));
      return {
        pos: mix3(a.pose.pos, b.pose.pos, u),
        target: mix3(a.pose.target, b.pose.target, u),
        fov: lerp(a.pose.fov, b.pose.fov, u),
      };
    }
  }
  return keys[keys.length - 1].pose;
};

export const makeCamera = (pose: CamPose, width: number, height: number): PerspectiveCamera => {
  const cam = new PerspectiveCamera(pose.fov, width / height, 0.05, 200);
  cam.position.set(...pose.pos);
  cam.up.set(0, 1, 0);
  cam.lookAt(new Vector3(...pose.target));
  cam.updateProjectionMatrix();
  cam.updateMatrixWorld(true);
  return cam;
};

/** World point → pixel coordinates (top-left origin). `visible` is false behind the camera. */
export const projectToScreen = (
  cam: PerspectiveCamera,
  p: Vec3,
  width: number,
  height: number,
): { x: number; y: number; visible: boolean } => {
  const v = new Vector3(...p).project(cam);
  return {
    x: (v.x * 0.5 + 0.5) * width,
    y: (-v.y * 0.5 + 0.5) * height,
    visible: v.z < 1 && v.z > -1,
  };
};
