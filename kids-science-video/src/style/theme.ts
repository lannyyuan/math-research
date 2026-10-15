/**
 * Shared style constants for the whole kids-science series
 * (汽油车 / 电动车 videos reuse these so they look like one family).
 */
export const VIDEO = {
  width: 1920,
  height: 1080,
  fps: 30,
} as const;

export const FONT = {
  /** Playful display font for title / end cards. */
  display: "ZCOOL KuaiLe, Noto Sans SC, WenQuanYi Zen Hei, sans-serif",
  /** Clean, very readable font for labels and subtitles. */
  body: "Noto Sans SC, WenQuanYi Zen Hei, sans-serif",
} as const;

export const COLORS = {
  bgTop: "#FFFFFF",
  bgBottom: "#CFE6FF",
  ground: "#EAF4FF",
  groundLine: "#C3DBF2",
  shadow: "#5C7A99",

  ink: "#22324A",
  inkSoft: "#4A5E7A",
  white: "#FFFFFF",

  carOrange: "#FF8A1F",
  carOrangeDark: "#D96A06",
  carOrangeLight: "#FFB35C",
  window: "#BFE6FF",
  bumper: "#FFD3A3",
  headlight: "#FFF7D6",
  taillight: "#FF6B6B",
  eyeWhite: "#FFFFFF",
  pupil: "#22324A",
  cheek: "#FF9EB5",

  xrayTint: "#DCEFFF",
  xrayRim: "#FF9A3D",

  highlight: "#FFE14D",
  outline: "#2B3A55",

  tire: "#3A4150",
  rim: "#E3E9F0",
  hub: "#9AA7B5",

  metal: "#C9D3DE",
  metalDark: "#7D8B9B",
  steel: "#6F7E90",
  glass: "#B4D2F0",

  fuel: "#FFE14D",
  fuelTank: "#2FB5A0",
  fuelLine: "#D99A12",
  piston: "#D5DEE8",
  rod: "#8EA0B4",
  crank: "#5F6F82",
  cam: "#9B7DE0",
  valve: "#EEF2F7",
  plug: "#FFFFFF",
  plugCap: "#FF6FA0",
  spark: "#FFF4B0",
  intake: "#4FA3F0",
  exhaust: "#9C8577",
  exhaustGlow: "#FF9D3C",
  smoke: "#9AA3AE",
  gearbox: "#6CCB7A",
  gear: "#F2B33D",
  gearIdle: "#B3BDCB",
  shaft: "#5B6878",
  radiator: "#3D9BE9",
  coolWind: "#7FD3FF",
  oil: "#E39A2D",
  power: "#FF5A36",

  // ---- electric car (cool palette, mirrors the gasoline car) ----
  carGreen: "#36C46B",
  carGreenDark: "#1F9A4E",
  carGreenLight: "#86E2A8",
  bumperGreen: "#CFF5DC",
  xrayRimGreen: "#2FBF68",
  battery: "#2E9C6A",
  batteryModule: "#3FB57E",
  batteryGlow: "#7CF0A8",
  cell: "#D8F7E6",
  hvCable: "#FF8C2E",
  current: "#6FC8FF",
  controller: "#3D7BD9",
  controllerLed: "#8FE3FF",
  motorHousing: "#9CC3E6",
  stator: "#4A86B8",
  coilA: "#5CD0FF",
  coilB: "#6E8CFF",
  coilC: "#4FE0C8",
  magnetN: "#3E6FD8",
  magnetS: "#C9D6E6",
  speedLine: "#8FE3FF",
  reducer: "#7FB3D9",
  leaf: "#46C46E",
  cleanAir: "#A9EBC4",
} as const;

/** Visual weights used by the toon shading and the label/subtitle UI. */
export const SIZES = {
  outline: 0.006, // metres, inverted-hull outline thickness for small parts
  outlineBig: 0.014, // car body / wheels
  labelFont: 46,
  labelFontSmall: 36,
  subtitleFont: 50,
  titleFont: 112,
  safeMargin: 64,
} as const;

/** Easing presets in one place so every video moves the same way. */
export const MOTION = {
  labelPopSeconds: 0.35,
  camEase: [0.45, 0, 0.25, 1] as const,
} as const;
