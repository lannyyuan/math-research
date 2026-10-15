import React from "react";
import { AbsoluteFill } from "remotion";
import { COLORS } from "../style/theme";
import { EV_DRIVE, EV_TL } from "./data";
import { ElectricCarOverlay } from "./Overlay";
import { ElectricCarSound } from "./Sound";
import { ElectricCarScene3D } from "./three/ElectricCarScene3D";

export type ElectricCarVideoProps = { readonly narration: boolean };

export const ElectricCarVideo: React.FC<ElectricCarVideoProps> = ({ narration }) => (
  <AbsoluteFill style={{ background: `linear-gradient(180deg, ${COLORS.bgTop} 0%, ${COLORS.bgBottom} 100%)` }}>
    <ElectricCarScene3D tl={EV_TL} drive={EV_DRIVE} />
    <ElectricCarOverlay tl={EV_TL} drive={EV_DRIVE} />
    <ElectricCarSound tl={EV_TL} narration={narration} />
  </AbsoluteFill>
);
