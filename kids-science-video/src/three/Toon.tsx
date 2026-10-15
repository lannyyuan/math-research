import React, { useMemo } from "react";
import { BufferGeometry, Color, Euler, Vector3 } from "three";
import { COLORS, SIZES } from "../style/theme";
import { useFade } from "./Fade";
import { applyHighlight, makeOutline, makeToon, type OutlineMode } from "./materials";

type V3 = readonly [number, number, number];

export type ToonProps = {
  readonly geometry: BufferGeometry;
  readonly color: string;
  /** 0..1 highlight glow. */
  readonly highlight?: number;
  /** Seconds — only used to drive the highlight breathing. */
  readonly t?: number;
  readonly opacity?: number;
  readonly outline?: number;
  readonly outlineMode?: OutlineMode;
  readonly emissive?: string;
  readonly emissiveIntensity?: number;
  readonly position?: V3;
  readonly rotation?: V3;
  readonly scale?: V3 | number;
  readonly renderOrder?: number;
  readonly visible?: boolean;
};

const HL_OUTLINE = new Color("#FF9F1C");
const BASE_OUTLINE = new Color(COLORS.outline);

/** A toon-shaded mesh with a cartoon outline and the shared highlight behaviour. */
export const Toon: React.FC<ToonProps> = ({
  geometry,
  color,
  highlight = 0,
  t = 0,
  opacity = 1,
  outline = SIZES.outline,
  outlineMode = "scale",
  emissive,
  emissiveIntensity = 1,
  position,
  rotation,
  scale,
  renderOrder,
  visible = true,
}) => {
  const fade = useFade();
  const alpha = opacity * fade;
  const mat = useMemo(() => {
    const m = makeToon(color);
    m.transparent = true; // opacity is animated (ghosting); depthWrite stays on while opaque
    return m;
  }, [color]);
  mat.opacity = alpha;
  mat.depthWrite = alpha >= 0.99;
  const box = useMemo(() => {
    geometry.computeBoundingBox();
    const b = geometry.boundingBox!;
    return { c: b.getCenter(new Vector3()), h: b.getSize(new Vector3()).multiplyScalar(0.5) };
  }, [geometry]);
  const outMat = useMemo(
    () => makeOutline(outlineMode, box.c, box.h, outline),
    [outlineMode, box, outline],
  );

  const base = emissive ? new Color(emissive).multiplyScalar(emissiveIntensity) : undefined;
  applyHighlight(mat, highlight, t, base);
  outMat.uniforms.uColor.value.copy(BASE_OUTLINE).lerp(HL_OUTLINE, Math.min(1, highlight));
  outMat.uniforms.uThickness.value = outline * (1 + 1.2 * highlight);
  outMat.uniforms.uOpacity.value = alpha < 1 ? alpha * 0.9 : 1;
  outMat.depthWrite = alpha >= 0.99;

  const rot = rotation ? new Euler(...rotation) : undefined;
  const sc: [number, number, number] | undefined =
    scale === undefined ? undefined : typeof scale === "number" ? [scale, scale, scale] : [...scale];
  return (
    <group position={position ? [...position] : undefined} rotation={rot} scale={sc} visible={visible && alpha > 0.005}>
      <mesh geometry={geometry} material={mat} renderOrder={renderOrder} />
      {outline > 0 ? <mesh geometry={geometry} material={outMat} renderOrder={renderOrder} /> : null}
    </group>
  );
};
