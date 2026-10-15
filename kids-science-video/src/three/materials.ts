import {
  AdditiveBlending,
  BackSide,
  Color,
  DataTexture,
  FrontSide,
  MeshBasicMaterial,
  MeshToonMaterial,
  NearestFilter,
  RedFormat,
  ShaderMaterial,
  Vector3,
} from "three";
import { COLORS } from "../style/theme";

/** 3-step toon ramp, generated in code (no image files). */
let ramp: DataTexture | null = null;
export const toonRamp = () => {
  if (!ramp) {
    ramp = new DataTexture(new Uint8Array([150, 205, 255]), 3, 1, RedFormat);
    ramp.minFilter = NearestFilter;
    ramp.magFilter = NearestFilter;
    ramp.generateMipmaps = false;
    ramp.needsUpdate = true;
  }
  return ramp;
};

export const makeToon = (color: string, opacity = 1) =>
  new MeshToonMaterial({
    color: new Color(color),
    gradientMap: toonRamp(),
    transparent: opacity < 1,
    opacity,
    depthWrite: opacity >= 1,
  });

const HL = new Color(COLORS.highlight);
const BLACK = new Color(0, 0, 0);
const tmp = new Color();

/**
 * Shared highlight look: the part brightens in its own colour (hue kept so it
 * stays recognisable) with a little warm glow; Toon/Glass also thicken and
 * warm the outline.
 */
export const applyHighlight = (m: MeshToonMaterial, h: number, t: number, baseEmissive?: Color) => {
  const k = h * (0.8 + 0.2 * Math.sin(t * Math.PI * 2 * 1.6));
  m.emissive.copy(baseEmissive ?? BLACK);
  tmp.copy(m.color).multiplyScalar(0.42 * k);
  m.emissive.add(tmp);
  tmp.copy(HL).multiplyScalar(0.1 * k);
  m.emissive.add(tmp);
};

// ---------------------------------------------------------------------------
// Inverted-hull outline
// ---------------------------------------------------------------------------
const outlineVert = /* glsl */ `
uniform float uThickness;
uniform float uMode;
uniform vec3 uCenter;
uniform vec3 uHalf;
void main() {
  vec3 p = position;
  if (uMode < 0.5) {
    p += normalize(normal) * uThickness;
  } else {
    vec3 d = p - uCenter;
    p = uCenter + d * (vec3(1.0) + uThickness / max(uHalf, vec3(1e-4)));
  }
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}`;
const outlineFrag = /* glsl */ `
uniform vec3 uColor;
uniform float uOpacity;
void main() {
  gl_FragColor = vec4(uColor, uOpacity);
  #include <colorspace_fragment>
}`;

export type OutlineMode = "normal" | "scale";

export const makeOutline = (mode: OutlineMode, center: Vector3, half: Vector3, thickness: number) =>
  new ShaderMaterial({
    uniforms: {
      uThickness: { value: thickness },
      uMode: { value: mode === "normal" ? 0 : 1 },
      uCenter: { value: center.clone() },
      uHalf: { value: half.clone() },
      uColor: { value: new Color(COLORS.outline) },
      uOpacity: { value: 1 },
    },
    vertexShader: outlineVert,
    fragmentShader: outlineFrag,
    side: BackSide,
    transparent: true,
  });

// ---------------------------------------------------------------------------
// Car body: toon when solid, fresnel "X-ray" glass when uX → 1
// ---------------------------------------------------------------------------
const bodyVert = /* glsl */ `
varying vec3 vN;
varying vec3 vV;
void main() {
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  vN = normalize(normalMatrix * normal);
  vV = normalize(-mv.xyz);
  gl_Position = projectionMatrix * mv;
}`;
const bodyFrag = /* glsl */ `
uniform vec3 uColor;
uniform vec3 uTint;
uniform vec3 uRim;
uniform vec3 uLight;
uniform float uX;
uniform float uOpacity;
uniform vec3 uEmissive;
varying vec3 vN;
varying vec3 vV;
void main() {
  vec3 n = normalize(vN);
  float ndl = dot(n, normalize(uLight));
  float band = ndl > 0.45 ? 1.0 : (ndl > -0.1 ? 0.84 : 0.7);
  vec3 solid = uColor * band + uEmissive;
  float fr = pow(1.0 - clamp(abs(dot(n, normalize(vV))), 0.0, 1.0), 3.0);
  vec3 xr = mix(uTint, uRim, smoothstep(0.05, 0.7, fr));
  vec3 col = mix(solid, xr, uX);
  float a = mix(1.0, 0.03 + 0.55 * fr, uX);
  gl_FragColor = vec4(col, a * uOpacity);
  #include <colorspace_fragment>
}`;

export const makeBodyMaterial = (color: string, rim: string = COLORS.xrayRim) =>
  new ShaderMaterial({
    uniforms: {
      uColor: { value: new Color(color) },
      uTint: { value: new Color(COLORS.xrayTint) },
      uRim: { value: new Color(rim) },
      uLight: { value: new Vector3(0.35, 0.8, 0.5) },
      uX: { value: 0 },
      uOpacity: { value: 1 },
      uEmissive: { value: new Color(0, 0, 0) },
    },
    vertexShader: bodyVert,
    fragmentShader: bodyFrag,
    transparent: true,
    side: FrontSide,
  });

export const setBodyXray = (m: ShaderMaterial, x: number, opacity = 1) => {
  m.uniforms.uX.value = x;
  m.uniforms.uOpacity.value = opacity;
  m.depthWrite = x < 0.001 && opacity >= 1;
};

/** Soft additive glow (spark flash, hot manifold halo, power arrows). */
export const makeGlow = (color: string, opacity = 1) =>
  new MeshBasicMaterial({
    color: new Color(color),
    transparent: true,
    opacity,
    depthWrite: false,
    blending: AdditiveBlending,
    toneMapped: false,
  });
