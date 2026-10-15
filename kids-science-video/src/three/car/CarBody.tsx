/**
 * Reusable cartoon sedan body. `xray` 0 → opaque toon, 1 → see-through
 * fresnel "X-ray" glass so the powertrain inside is visible. Used by both the
 * gasoline and the electric car videos.
 */
import React, { useMemo } from "react";
import { Color, CylinderGeometry, DoubleSide, Shape } from "three";
import { COLORS } from "../../style/theme";
import { capsuleZ, extrudeZ, quad, smoothNormals, sphere, torusZ } from "../geometry";
import { makeBodyMaterial, makeToon, setBodyXray } from "../materials";
import { CAR } from "./carLayout";

type Props = {
  readonly color?: string;
  /** X-ray rim colour (defaults to the gasoline car's orange). */
  readonly rim?: string;
  readonly bumper?: string;
  readonly xray: number;
  /** 0 = gentle smile, 1 = big happy smile. */
  readonly smile: number;
  readonly t: number;
};

/** Bottom outline: flat floor that blends into the wheel arches with smooth fillets. */
const bottomY = (x: number) => {
  const arch = (ax: number) => {
    const d = x - ax;
    return Math.abs(d) < CAR.archR ? CAR.archCY + Math.sqrt(CAR.archR ** 2 - d * d) : -1;
  };
  const a = Math.max(arch(CAR.frontAxleX), arch(CAR.rearAxleX));
  const k = 0.06; // fillet softness
  const f = CAR.floorY;
  return (a + f + Math.sqrt((a - f) * (a - f) + k * k)) / 2;
};

const lowerShape = () => {
  const s = new Shape();
  s.moveTo(-2.0, bottomY(-2.0));
  for (let x = -1.98; x <= 1.98 + 1e-6; x += 0.02) s.lineTo(x, bottomY(x));
  s.quadraticCurveTo(2.16, 0.25, 2.17, 0.45);
  s.lineTo(2.17, 0.66);
  s.quadraticCurveTo(2.16, 0.87, 1.95, 0.91);
  s.quadraticCurveTo(1.5, 0.99, 1.0, 1.03);
  s.lineTo(-1.55, 1.05);
  s.quadraticCurveTo(-2.1, 1.03, -2.16, 0.88);
  s.lineTo(-2.17, 0.45);
  s.quadraticCurveTo(-2.16, 0.25, -2.0, bottomY(-2.0));
  return s;
};

const cabinShape = () => {
  const c = new Shape();
  c.moveTo(1.06, 0.98);
  c.quadraticCurveTo(0.62, 1.24, 0.3, 1.46);
  c.quadraticCurveTo(0.16, 1.53, -0.1, 1.53);
  c.lineTo(-0.72, 1.52);
  c.quadraticCurveTo(-0.95, 1.51, -1.08, 1.41);
  c.quadraticCurveTo(-1.36, 1.2, -1.6, 0.98);
  c.lineTo(1.06, 0.98);
  return c;
};

const windowShapes = () => {
  const front = new Shape();
  front.moveTo(0.9, 1.08);
  front.quadraticCurveTo(0.55, 1.28, 0.28, 1.42);
  front.lineTo(-0.16, 1.44);
  front.lineTo(-0.16, 1.08);
  front.lineTo(0.9, 1.08);
  const rear = new Shape();
  rear.moveTo(-0.3, 1.08);
  rear.lineTo(-0.3, 1.44);
  rear.lineTo(-0.72, 1.43);
  rear.quadraticCurveTo(-0.92, 1.42, -1.02, 1.34);
  rear.lineTo(-1.38, 1.08);
  rear.lineTo(-0.3, 1.08);
  return [front, rear];
};

export const CarBody: React.FC<Props> = ({ color = COLORS.carOrange, rim = COLORS.xrayRim, bumper = COLORS.bumper, xray, smile, t }) => {
  const geo = useMemo(() => {
    const lower = smoothNormals(extrudeZ(lowerShape(), CAR.bodyHalfW * 2, 0.13, 5, 48, true));
    const cabin = smoothNormals(extrudeZ(cabinShape(), CAR.cabinHalfW * 2, 0.12, 5, 32, true));
    const [wf, wr] = windowShapes();
    const winF = extrudeZ(wf, 0.012, 0, 1, 24);
    const winR = extrudeZ(wr, 0.012, 0, 1, 24);
    const windshield = quad([1.03, 1.02, -0.6], [1.03, 1.02, 0.6], [0.36, 1.44, 0.6], [0.36, 1.44, -0.6]);
    const rearGlass = quad([-1.06, 1.42, -0.58], [-1.06, 1.42, 0.58], [-1.5, 1.06, 0.58], [-1.5, 1.06, -0.58]);
    const bumper = capsuleZ(0.085, 1.52);
    const light = sphere(0.09);
    const eye = sphere(0.13, 32);
    const pupil = sphere(0.06, 24);
    const cheek = sphere(0.06, 20);
    // inner wheel-well liners so you can't see through the arches
    const well = new CylinderGeometry(CAR.archR - 0.02, CAR.archR - 0.02, 0.34, 40, 1, true, Math.PI - 1.5, 3.0).rotateX(Math.PI / 2);
    return { lower, cabin, winF, winR, windshield, rearGlass, bumper, light, eye, pupil, cheek, well };
  }, []);

  const mats = useMemo(
    () => ({
      body: makeBodyMaterial(color, rim),
      window: makeBodyMaterial(COLORS.window, "#8CCBFF"),
      bumper: makeBodyMaterial(bumper, rim),
      head: makeBodyMaterial(COLORS.headlight, "#FFE9A8"),
      tail: makeBodyMaterial(COLORS.taillight, "#FF9C9C"),
      well: makeBodyMaterial("#4A4F5C", rim === COLORS.xrayRim ? "#FFB061" : rim),
      eye: makeToon(COLORS.eyeWhite),
      pupil: makeToon(COLORS.pupil),
      cheek: makeToon(COLORS.cheek),
      mouth: makeToon(COLORS.ink),
    }),
    [color, rim, bumper],
  );
  for (const m of [mats.body, mats.window, mats.bumper, mats.head, mats.tail]) setBodyXray(m, xray);
  setBodyXray(mats.well, Math.min(1, xray * 1.4), 1 - xray);
  mats.well.side = DoubleSide;
  // face features fade away in X-ray mode
  const face = 1 - Math.min(1, xray * 1.6);
  for (const m of [mats.eye, mats.pupil, mats.cheek, mats.mouth]) {
    m.transparent = face < 1;
    m.opacity = face;
    m.depthWrite = face >= 1;
  }
  mats.head.uniforms.uEmissive.value = new Color(0.08, 0.07, 0.02);

  // smile: arc grows and curls up as `smile` → 1
  const arc = 1.3 + 1.1 * smile;
  const mouthGeo = useMemo(() => torusZ(0.2 - 0.03 * Math.round(smile * 4) / 4, 0.028, arc), [arc, smile]);
  // blink (deterministic, from time)
  const blinkPhase = (t % 3.2) / 3.2;
  const blink = blinkPhase > 0.94 ? 0.15 : 1;
  const z = (s: number) => s * 0.33;
  const visibleFace = face > 0.01;

  return (
    <group>
      <mesh geometry={geo.lower} material={mats.body} renderOrder={20} />
      <mesh geometry={geo.cabin} material={mats.body} renderOrder={20} />
      {[CAR.frontAxleX, CAR.rearAxleX].flatMap((x) =>
        [1, -1].map((s) => (
          <mesh key={`w${x}${s}`} geometry={geo.well} material={mats.well} position={[x, CAR.archCY, s * (CAR.bodyHalfW - 0.2)]} renderOrder={19} />
        )),
      )}
      {[1, -1].map((s) => (
        <group key={s} position={[0, 0, s * (CAR.cabinHalfW + 0.004)]}>
          <mesh geometry={geo.winF} material={mats.window} renderOrder={21} />
          <mesh geometry={geo.winR} material={mats.window} renderOrder={21} />
        </group>
      ))}
      <mesh geometry={geo.windshield} material={mats.window} renderOrder={21} position={[0.02, 0.025, 0]} />
      <mesh geometry={geo.rearGlass} material={mats.window} renderOrder={21} position={[-0.02, 0.025, 0]} />
      <mesh geometry={geo.bumper} material={mats.bumper} position={[2.13, 0.32, 0]} renderOrder={21} />
      <mesh geometry={geo.bumper} material={mats.bumper} position={[-2.13, 0.32, 0]} renderOrder={21} />
      {[1, -1].map((s) => (
        <group key={`l${s}`}>
          <mesh geometry={geo.light} material={mats.head} position={[2.1, 0.74, s * 0.6]} scale={[0.6, 0.8, 1.2]} renderOrder={21} />
          <mesh geometry={geo.light} material={mats.tail} position={[-2.13, 0.84, s * 0.62]} scale={[0.5, 0.7, 1.1]} renderOrder={21} />
        </group>
      ))}
      {visibleFace ? (
        <group>
          {/* eyes on the windshield */}
          {[1, -1].map((s) => (
            <group key={`e${s}`} position={[0.74, 1.235, z(s)]} rotation={[0, 0, 0.98]}>
              <mesh geometry={geo.eye} material={mats.eye} scale={[0.25, 1, 0.85 * blink]} rotation={[0, 0, 0]} />
              <mesh geometry={geo.pupil} material={mats.pupil} position={[0.03, 0.035, s * 0.015]} scale={[0.4, 1, 1 * blink]} />
            </group>
          ))}
          {/* smile on the grille */}
          <mesh
            geometry={mouthGeo}
            material={mats.mouth}
            position={[2.175, 0.7, 0]}
            rotation={[0, Math.PI / 2, -Math.PI / 2 - arc / 2]}
          />
          {[1, -1].map((s) => (
            <mesh key={`c${s}`} geometry={geo.cheek} material={mats.cheek} position={[2.16, 0.6, s * 0.4]} scale={[0.3, 0.7, 1]} />
          ))}
        </group>
      ) : null}
    </group>
  );
};
