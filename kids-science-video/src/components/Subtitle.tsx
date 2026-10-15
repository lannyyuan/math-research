import React from "react";
import { COLORS, FONT, SIZES } from "../style/theme";

/** Bottom-centre subtitle pill. `appear` 0..1 drives a gentle rise + fade. */
export const Subtitle: React.FC<{ readonly text: string; readonly appear: number; readonly bottom?: number }> = ({
  text,
  appear,
  bottom = 54,
}) => {
  if (appear <= 0.001) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom,
        display: "flex",
        justifyContent: "center",
        opacity: appear,
        translate: `0px ${(1 - appear) * 18}px`,
      }}
    >
      <div
        style={{
          maxWidth: 1560,
          padding: "16px 44px 18px",
          borderRadius: 999,
          background: "rgba(255,255,255,0.94)",
          border: `5px solid ${COLORS.carOrange}`,
          boxShadow: "0 8px 22px rgba(34,50,74,0.16)",
          fontFamily: FONT.body,
          fontWeight: 700,
          fontSize: SIZES.subtitleFont,
          lineHeight: 1.25,
          color: COLORS.ink,
          textAlign: "center",
          letterSpacing: 1,
        }}
      >
        {text}
      </div>
    </div>
  );
};
