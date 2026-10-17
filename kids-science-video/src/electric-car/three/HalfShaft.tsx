/** One half-shaft with its CV boots (the EV pulls each out of the differential separately). */
import React, { useMemo } from "react";
import { COLORS } from "../../style/theme";
import { CAR } from "../../three/car/carLayout";
import { cylZ, rbox } from "../../three/geometry";
import { Toon } from "../../three/Toon";
import { RED } from "../layout";

export const HalfShaft: React.FC<{ readonly side: "left" | "right"; readonly wheel: number; readonly highlight: number; readonly t: number }> = ({
  side,
  wheel,
  highlight,
  t,
}) => {
  // same dimensions as the gasoline car's half-shafts (and as electric-car/shapes.ts)
  const z0 = side === "left" ? RED.gearZ - 0.045 : RED.gearZ + 0.03;
  const z1 = side === "left" ? -(CAR.trackHalf - 0.1) : CAR.trackHalf - 0.1;
  const inner = side === "left" ? z0 - 0.03 : z0 + 0.04;
  const outer = side === "left" ? z1 + 0.04 : z1 - 0.04;
  const g = useMemo(
    () => ({
      shaft: cylZ(0.017, Math.abs(z1 - z0), 16),
      bootIn: side === "left" ? cylZ(0.035, 0.07, 20, 0.018) : cylZ(0.018, 0.07, 20, 0.035),
      bootOut: side === "left" ? cylZ(0.018, 0.07, 20, 0.035) : cylZ(0.035, 0.07, 20, 0.018),
      fin: rbox(0.012, 0.03, 0.04, 0.004),
    }),
    [side, z0, z1],
  );
  return (
    <group position={[RED.diffX, RED.diffY, 0]} rotation={[0, 0, -wheel]}>
      <Toon geometry={g.shaft} color={COLORS.shaft} highlight={highlight} t={t} position={[0, 0, (z0 + z1) / 2]} outline={0.003} />
      <Toon geometry={g.bootIn} color="#3E4654" highlight={highlight} t={t} position={[0, 0, inner]} />
      <Toon geometry={g.bootOut} color="#3E4654" highlight={highlight} t={t} position={[0, 0, outer]} />
      <Toon geometry={g.fin} color={COLORS.power} outline={0} position={[0, 0.02, (z0 + z1) / 2]} />
    </group>
  );
};
