/**
 * Exploded-view planner for the electric car (same method as plan-explode.ts):
 * desired screen spot [x, y, closer] → world offset, where `closer` (0..1) slides
 * the part along its view ray towards the camera so big blocks read bigger.
 *   npx tsx scripts/plan-explode-ev.ts '{"motor":[1450,420,0.3]}'
 */
import { Vector3 } from "three";
import { makeCamera, projectToScreen, type CamPose } from "../src/lib/camera";
import { CAR } from "../src/three/car/carLayout";
import { EV_PARTS, type EvPartId } from "../src/electric-car/parts";

const W = 1920;
const H = 1080;
const pose: CamPose = { pos: [3.85, 2.75, 6.3], target: [1.0, 0.78, 0.0], fov: 36 };
const cam = makeCamera(pose, W, H);
const minY: Record<EvPartId, number> = { battery: 0.255, harness: 0.32, controller: 0.645, motor: 0.35, reducer: 0.205, halfShafts: 0.34, wheels: 0 };
const targets: Partial<Record<EvPartId, [number, number, number]>> = JSON.parse(process.argv[2] ?? "{}");
const center = new Vector3(...CAR.center);
for (const id of Object.keys(EV_PARTS) as EvPartId[]) {
  const a = new Vector3(...EV_PARTS[id].anchor);
  const s = projectToScreen(cam, EV_PARTS[id].anchor, W, H);
  let line = `${id.padEnd(11)} now (${s.x.toFixed(0)}, ${s.y.toFixed(0)})`;
  const tg = targets[id];
  if (tg) {
    const ndc = a.clone().project(cam);
    const far = new Vector3((tg[0] / W) * 2 - 1, -((tg[1] / H) * 2 - 1), ndc.z).unproject(cam);
    let p = cam.position.clone().lerp(far, 1 - tg[2]);
    const lift = 0.04 - minY[id];
    if (p.y - a.y < lift) {
      const dir = far.clone().sub(cam.position).normalize();
      p = cam.position.clone().add(dir.multiplyScalar((a.y + lift - cam.position.y) / dir.y));
    }
    const off = p.clone().sub(a);
    const cos = off.clone().normalize().dot(a.clone().sub(center).normalize());
    line += `  → [${off.x.toFixed(2)}, ${off.y.toFixed(2)}, ${off.z.toFixed(2)}] angle ${((Math.acos(cos) * 180) / Math.PI).toFixed(0)}°${cos <= 0 ? " ✗ NOT OUTWARD" : ""}`;
  }
  console.log(line);
}
