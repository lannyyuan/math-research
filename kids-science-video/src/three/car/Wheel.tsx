import React, { useMemo } from "react";
import { COLORS, SIZES } from "../../style/theme";
import { cylZ, rbox, torusZ } from "../geometry";
import { Toon } from "../Toon";
import { CAR } from "./carLayout";

type Props = {
  readonly position: readonly [number, number, number];
  /** +1 for wheels on the car's right side (+Z), −1 for the left side. */
  readonly side: 1 | -1;
  /** Road-wheel roll angle (radians, forward positive). */
  readonly angle: number;
  readonly highlight?: number;
  readonly t: number;
  readonly hubColor?: string;
  readonly dotColor?: string;
};

/** Cartoon wheel: chunky tyre, 5-spoke rim, coloured hub dot so rotation is easy to see. */
export const Wheel: React.FC<Props> = ({
  position,
  side,
  angle,
  highlight = 0,
  t,
  hubColor = COLORS.carOrangeLight,
  dotColor = COLORS.carOrange,
}) => {
  const g = useMemo(() => {
    const tubeR = 0.095;
    return {
      tire: torusZ(CAR.wheelR - tubeR, tubeR),
      tireCore: cylZ(CAR.wheelR - 0.02, 0.16, 40),
      rim: cylZ(0.2, 0.13, 36),
      spoke: rbox(0.05, 0.17, 0.03, 0.012),
      hub: cylZ(0.055, 0.15, 24),
      dot: cylZ(0.035, 0.02, 20),
    };
  }, []);
  const outer = side * 0.07;
  return (
    <group position={[...position]} rotation={[0, 0, -angle]}>
      <Toon geometry={g.tire} color={COLORS.tire} outline={SIZES.outlineBig} outlineMode="normal" highlight={highlight} t={t} />
      <Toon geometry={g.tireCore} color={COLORS.tire} outline={0} highlight={highlight} t={t} />
      <Toon geometry={g.rim} color={COLORS.rim} outline={SIZES.outline} highlight={highlight} t={t} />
      {[0, 1, 2, 3, 4].map((k) => {
        const a = (k / 5) * Math.PI * 2;
        return (
          <Toon
            key={k}
            geometry={g.spoke}
            color={COLORS.hub}
            outline={0}
            position={[Math.sin(a) * 0.105, Math.cos(a) * 0.105, outer]}
            rotation={[0, 0, -a]}
          />
        );
      })}
      <Toon geometry={g.hub} color={hubColor} outline={SIZES.outline} position={[0, 0, outer * 0.6]} />
      <Toon geometry={g.dot} color={dotColor} outline={0} position={[0, 0.16, outer + side * 0.005]} />
    </group>
  );
};
