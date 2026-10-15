import React, { useMemo } from "react";
import { BufferGeometry, Color, EdgesGeometry, LineBasicMaterial, Vector3 } from "three";
import { COLORS } from "../style/theme";
import { useFade } from "./Fade";
import { applyHighlight, makeOutline, makeToon } from "./materials";

type V3 = readonly [number, number, number];

type Props = {
  readonly geometry: BufferGeometry;
  readonly color: string;
  readonly opacity: number;
  readonly highlight?: number;
  readonly t?: number;
  readonly position?: V3;
  readonly edges?: boolean;
  readonly renderOrder?: number;
};

/** See-through "cut-away" casing (engine block, gearbox housing…) with crisp edge lines. */
export const Glass: React.FC<Props> = ({ geometry, color, opacity, highlight = 0, t = 0, position, edges = true, renderOrder = 5 }) => {
  const mat = useMemo(() => {
    const m = makeToon(color, opacity);
    m.transparent = true;
    m.depthWrite = false;
    return m;
  }, [color, opacity]);
  const box = useMemo(() => {
    geometry.computeBoundingBox();
    const b = geometry.boundingBox!;
    return { c: b.getCenter(new Vector3()), h: b.getSize(new Vector3()).multiplyScalar(0.5) };
  }, [geometry]);
  const out = useMemo(() => {
    const m = makeOutline("scale", box.c, box.h, 0.004);
    m.depthWrite = false;
    return m;
  }, [box]);
  const edgeGeo = useMemo(() => (edges ? new EdgesGeometry(geometry, 35) : null), [geometry, edges]);
  const lineMat = useMemo(
    () => new LineBasicMaterial({ color: new Color(COLORS.outline), transparent: true, opacity: 0.55, depthWrite: false }),
    [],
  );
  const fade = useFade();
  applyHighlight(mat, highlight * 0.6, t);
  mat.opacity = Math.min(0.85, opacity + 0.12 * highlight) * fade;
  out.uniforms.uOpacity.value = (0.45 + 0.45 * highlight) * fade;
  lineMat.opacity = (0.5 + 0.4 * highlight) * fade;
  lineMat.color.set(highlight > 0.05 ? "#F08A00" : COLORS.outline);
  out.uniforms.uColor.value.set(highlight > 0.05 ? "#FF9F1C" : COLORS.outline);
  return (
    <group position={position ? [...position] : undefined}>
      <mesh geometry={geometry} material={mat} renderOrder={renderOrder} />
      {edgeGeo ? <lineSegments geometry={edgeGeo} material={lineMat} renderOrder={renderOrder} /> : null}
    </group>
  );
};
