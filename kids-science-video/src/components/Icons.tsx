/** Small flat SVG icons + cards used by the comparison / summary UI (all drawn in code). */
import React from "react";
import { COLORS, FONT } from "../style/theme";

export const BatteryIcon: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <rect x="14" y="26" width="66" height="48" rx="10" fill={COLORS.battery} stroke={COLORS.ink} strokeWidth="5" />
    <rect x="80" y="40" width="9" height="20" rx="3" fill={COLORS.ink} />
    <rect x="22" y="34" width="14" height="32" rx="4" fill={COLORS.batteryGlow} />
    <rect x="40" y="34" width="14" height="32" rx="4" fill={COLORS.batteryGlow} />
    <rect x="58" y="34" width="14" height="32" rx="4" fill={COLORS.batteryGlow} opacity="0.55" />
  </svg>
);

export const MotorIcon: React.FC<{ size: number; spin?: number }> = ({ size, spin = 0 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="36" fill={COLORS.motorHousing} stroke={COLORS.ink} strokeWidth="5" />
    <circle cx="50" cy="50" r="24" fill={COLORS.stator} />
    <g transform={`rotate(${spin} 50 50)`}>
      <path d="M50 30 A20 20 0 0 1 70 50 L50 50 Z" fill={COLORS.magnetN} />
      <path d="M50 70 A20 20 0 0 1 30 50 L50 50 Z" fill={COLORS.magnetN} />
      <path d="M70 50 A20 20 0 0 1 50 70 L50 50 Z" fill={COLORS.magnetS} />
      <path d="M30 50 A20 20 0 0 1 50 30 L50 50 Z" fill={COLORS.magnetS} />
    </g>
    <circle cx="50" cy="50" r="5" fill={COLORS.ink} />
  </svg>
);

export const ChipIcon: React.FC<{ size: number; blink?: number }> = ({ size, blink = 0 }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    {[30, 43, 56, 69].map((p) => (
      <g key={p}>
        <rect x={p - 3} y="10" width="6" height="14" rx="2" fill={COLORS.ink} />
        <rect x={p - 3} y="76" width="6" height="14" rx="2" fill={COLORS.ink} />
        <rect x="10" y={p - 3} width="14" height="6" rx="2" fill={COLORS.ink} />
        <rect x="76" y={p - 3} width="14" height="6" rx="2" fill={COLORS.ink} />
      </g>
    ))}
    <rect x="22" y="22" width="56" height="56" rx="10" fill={COLORS.controller} stroke={COLORS.ink} strokeWidth="5" />
    {[0, 1, 2].map((i) =>
      [0, 1, 2].map((k) => (
        <circle key={`${i}${k}`} cx={36 + i * 14} cy={36 + k * 14} r="4" fill={COLORS.controllerLed} opacity={(i + k + Math.floor(blink)) % 2 ? 1 : 0.35} />
      )),
    )}
  </svg>
);

export const LeafIcon: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M18 82 C20 40 48 16 86 14 C86 52 62 82 22 84 Z" fill={COLORS.leaf} stroke={COLORS.ink} strokeWidth="5" strokeLinejoin="round" />
    <path d="M24 78 C40 60 56 44 74 28" fill="none" stroke={COLORS.ink} strokeWidth="4" strokeLinecap="round" />
    <path d="M44 58 L42 44 M56 46 L58 34 M50 52 L62 54" stroke={COLORS.ink} strokeWidth="3" strokeLinecap="round" />
  </svg>
);

/** Side silhouette of the series' cartoon sedan. */
export const CarSilhouette: React.FC<{ width: number; color: string }> = ({ width, color }) => (
  <svg width={width} height={width * 0.42} viewBox="0 0 240 100">
    <path
      d="M16 74 L16 58 Q18 48 34 46 L74 42 L100 22 Q106 17 116 17 L158 17 Q168 17 176 25 L194 42 L220 46 Q234 49 234 62 L234 74 Z"
      fill={color}
      stroke={COLORS.ink}
      strokeWidth="5"
      strokeLinejoin="round"
    />
    <circle cx="66" cy="76" r="15" fill={COLORS.tire} stroke={COLORS.ink} strokeWidth="4" />
    <circle cx="184" cy="76" r="15" fill={COLORS.tire} stroke={COLORS.ink} strokeWidth="4" />
    <path d="M108 24 L156 24 Q164 24 170 32 L180 42 L104 42 Z" fill={COLORS.window} opacity="0.9" />
  </svg>
);

/** Rounded icon card with a caption; `pop` (0..1+) and `focus` (0..1) drive the zoom. */
export const IconCard: React.FC<{
  readonly icon: React.ReactNode;
  readonly label: string;
  readonly color: string;
  readonly pop: number;
  readonly focus: number;
}> = ({ icon, label, color, pop, focus }) => (
  <div
    style={{
      width: 168,
      height: 196,
      borderRadius: 30,
      background: COLORS.white,
      border: `6px solid ${color}`,
      boxShadow: focus > 0.05 ? `0 0 ${36 * focus}px ${color}` : "0 8px 20px rgba(34,50,74,0.16)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 4,
      opacity: Math.min(1, Math.max(0, pop) * 1.4),
      scale: String(Math.max(0, pop) * (1 + 0.28 * focus)),
      fontFamily: FONT.body,
      fontWeight: 900,
      fontSize: 40,
      color: COLORS.ink,
      boxSizing: "border-box",
    }}
  >
    {icon}
    {label}
  </div>
);
