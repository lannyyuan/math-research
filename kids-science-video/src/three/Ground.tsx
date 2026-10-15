import React, { useMemo } from "react";
import { CircleGeometry, Color, PlaneGeometry, ShaderMaterial } from "three";
import { COLORS } from "../style/theme";

const groundMat = () =>
  new ShaderMaterial({
    uniforms: { uColor: { value: new Color(COLORS.ground) }, uLine: { value: new Color(COLORS.groundLine) }, uOffset: { value: 0 } },
    vertexShader: /* glsl */ `
      varying vec2 vXZ;
      void main() {
        vec4 wp = modelMatrix * vec4(position, 1.0);
        vXZ = wp.xz;
        gl_Position = projectionMatrix * viewMatrix * wp;
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uColor;
      uniform vec3 uLine;
      uniform float uOffset;
      varying vec2 vXZ;
      void main() {
        float r = length(vXZ * vec2(0.55, 1.0));
        float fade = 1.0 - smoothstep(4.0, 9.0, r);
        // road dashes scroll with the distance the car has driven
        float x = vXZ.x + uOffset;
        float dash = step(0.5, fract(x / 1.6)) * (1.0 - smoothstep(0.03, 0.05, abs(abs(vXZ.y) - 1.35)));
        vec3 col = mix(uColor, uLine, dash * 0.9);
        gl_FragColor = vec4(col, fade * 0.95);
        #include <colorspace_fragment>
      }`,
    transparent: true,
    depthWrite: false,
  });

const shadowMat = () =>
  new ShaderMaterial({
    uniforms: { uColor: { value: new Color(COLORS.shadow) }, uOpacity: { value: 0.28 } },
    vertexShader: /* glsl */ `
      varying vec2 vUv;
      void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uColor;
      uniform float uOpacity;
      varying vec2 vUv;
      void main() {
        float d = length((vUv - 0.5) * 2.0);
        float a = (1.0 - smoothstep(0.35, 1.0, d)) * uOpacity;
        gl_FragColor = vec4(uColor, a);
        #include <colorspace_fragment>
      }`,
    transparent: true,
    depthWrite: false,
  });

type Props = { readonly scroll: number; readonly shadowScale?: readonly [number, number] };

/** Soft floor disc with scrolling road dashes and a blob shadow under the car. */
export const Ground: React.FC<Props> = ({ scroll, shadowScale = [5.2, 2.3] }) => {
  const g = useMemo(() => ({ disc: new CircleGeometry(12, 96).rotateX(-Math.PI / 2), plane: new PlaneGeometry(1, 1).rotateX(-Math.PI / 2) }), []);
  const m = useMemo(() => ({ ground: groundMat(), shadow: shadowMat() }), []);
  m.ground.uniforms.uOffset.value = scroll;
  return (
    <group>
      <mesh geometry={g.disc} material={m.ground} renderOrder={-2} />
      <mesh geometry={g.plane} material={m.shadow} position={[0, 0.002, 0]} scale={[shadowScale[0], 1, shadowScale[1]]} renderOrder={-1} />
    </group>
  );
};
