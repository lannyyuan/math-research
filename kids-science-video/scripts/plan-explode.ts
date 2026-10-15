/**
 * Design helper for the exploded view: given desired on-screen positions for
 * each part (under the explode camera) solve the world offsets that keep each
 * part at its current viewing depth, then report outward-ness and ground
 * clearance. Output is pasted into src/gas-car/parts.ts.
 *   npx tsx scripts/plan-explode.ts
 */
import { Vector3 } from "three";
import { makeCamera, projectToScreen, type CamPose } from "../src/lib/camera";
import { CAR } from "../src/three/car/carLayout";
import { PARTS, type PartId } from "../src/gas-car/parts";

const W = 1920;
const H = 1080;
const pose: CamPose = JSON.parse(process.argv[2] ?? "null") ?? { pos: [3.4, 2.7, 6.4], target: [0.55, 0.75, 0], fov: 38 };
const cam = makeCamera(pose, W, H);

const minY: Record<PartId, number> = {
  fuelTank: 0.32, fuelLine: 0.29, block: 0.31, pistons: 0.47, crankshaft: 0.33, camValves: 0.66, sparkPlugs: 0.67,
  intake: 0.69, exhaustManifold: 0.5, exhaustPipe: 0.13, gearbox: 0.255, halfShafts: 0.33, radiator: 0.34, oil: 0.22, wheels: 0,
};

const targets: Partial<Record<PartId, [number, number]>> = JSON.parse(process.argv[3] ?? "{}");
const center = new Vector3(...CAR.center);

for (const id of Object.keys(PARTS) as PartId[]) {
  const a = new Vector3(...PARTS[id].anchor);
  const s = projectToScreen(cam, PARTS[id].anchor, W, H);
  let line = `${id.padEnd(16)} now (${s.x.toFixed(0)}, ${s.y.toFixed(0)})`;
  const tgt = targets[id];
  if (tgt) {
    // keep view depth: unproject target at the anchor's NDC z
    const ndc = a.clone().project(cam);
    let p = new Vector3((tgt[0] / W) * 2 - 1, -((tgt[1] / H) * 2 - 1), ndc.z).unproject(cam);
    const lift = 0.04 - minY[id]; // smallest allowed y-offset
    if (p.y - a.y < lift) {
      // would sink below the floor → slide along the same view ray towards the camera instead
      const far = new Vector3((tgt[0] / W) * 2 - 1, -((tgt[1] / H) * 2 - 1), 0.5).unproject(cam);
      const dir = far.sub(cam.position).normalize();
      const k = (a.y + lift - cam.position.y) / dir.y;
      p = cam.position.clone().add(dir.multiplyScalar(k));
    }
    const off = p.clone().sub(a);
    const radial = a.clone().sub(center);
    const cos = off.clone().normalize().dot(radial.clone().normalize());
    const clearance = minY[id] + off.y;
    line += `  → explode: [${off.x.toFixed(2)}, ${off.y.toFixed(2)}, ${off.z.toFixed(2)}]  angle ${(
      (Math.acos(cos) * 180) /
      Math.PI
    ).toFixed(0)}°  minY ${clearance.toFixed(2)}${cos <= 0 ? "  ✗ NOT OUTWARD" : ""}${clearance < 0.02 ? "  ✗ BELOW GROUND" : ""}`;
  }
  console.log(line);
}
