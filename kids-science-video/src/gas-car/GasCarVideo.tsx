import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS } from "../style/theme";
import { GAS_DRIVE, GAS_TL } from "./data";
import { GasCarOverlay } from "./Overlay";
import { GasCarSound } from "./Sound";
import { GasCarScene3D } from "./three/GasCarScene3D";

export type GasCarVideoProps = {
  /** false → no narration (subtitles stay) for live classroom explanation. */
  readonly narration: boolean;
};

export const GasCarVideo: React.FC<GasCarVideoProps> = ({ narration }) => {
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bgTop} 0%, ${COLORS.bgBottom} 100%)` }}>
      <GasCarScene3D tl={GAS_TL} drive={GAS_DRIVE} />
      <GasCarOverlay tl={GAS_TL} drive={GAS_DRIVE} />
      <GasCarSound tl={GAS_TL} narration={narration} />
    </AbsoluteFill>
  );
};
