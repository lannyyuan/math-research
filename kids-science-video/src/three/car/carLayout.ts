/**
 * Shared cartoon-sedan body dimensions (metres). Both the gasoline and the
 * electric video use this body, so the internals of each are laid out
 * against the same wheelbase / track / floor.
 * Axes: +X = car front (screen right in side view), +Y = up, +Z = car's right side.
 */
export const CAR = {
  length: 4.3,
  width: 1.8,
  floorY: 0.24,
  wheelR: 0.36,
  tireW: 0.24,
  frontAxleX: 1.32,
  rearAxleX: -1.33,
  trackHalf: 0.75,
  archR: 0.47,
  archCY: 0.3,
  cabinHalfW: 0.74,
  bodyHalfW: 0.9,
  center: [0, 0.62, 0] as const,
} as const;

export const WHEELS = [
  { id: "FL", x: CAR.frontAxleX, z: -CAR.trackHalf, driven: true },
  { id: "FR", x: CAR.frontAxleX, z: CAR.trackHalf, driven: true },
  { id: "RL", x: CAR.rearAxleX, z: -CAR.trackHalf, driven: false },
  { id: "RR", x: CAR.rearAxleX, z: CAR.trackHalf, driven: false },
] as const;
