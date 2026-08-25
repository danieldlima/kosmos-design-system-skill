export const worldPlaneVertexShader = `
  varying vec2 vWorldXY;
  void main() {
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldXY = worldPosition.xy;
    gl_Position = projectionMatrix * viewMatrix * worldPosition;
  }
`;

/** Precise hairline grid, not a texture effect: two straight anti-aliased lines per
 * axis-repeat, mixed into the base at a low, constant opacity. Mirrors the brand's own
 * documented dark-surface recipe ("1 px line every 44–68 px at ~3.5% opacity") rather
 * than a stylized noise/dither pattern. No color mixing, no quantization — the grid stays
 * perfectly neutral (concreto on chumbo) so it reads as structure, not decoration. */
export const gridFragmentShader = `
  precision highp float;
  varying vec2 vWorldXY;
  uniform vec3 uBase;
  uniform vec3 uLine;
  uniform float uSpacing;
  uniform float uLineWidth;
  uniform float uOpacity;

  void main() {
    vec2 distToLine = abs(mod(vWorldXY + uSpacing * 0.5, uSpacing) - uSpacing * 0.5);
    float lineMask = 1.0 - smoothstep(0.0, uLineWidth, min(distToLine.x, distToLine.y));
    vec3 color = mix(uBase, uLine, lineMask * uOpacity);
    gl_FragColor = vec4(color, 1.0);
  }
`;

/** Small, restrained radial falloff — the pointer's focus glow and the click ring's
 * fill. Deliberately tight-radius: the brandbook treats urucum as "a reading accent,
 * used selectively, not an all-over fill," so this never grows past a small halo. */
export const glowFragmentShader = `
  precision mediump float;
  varying vec2 vUv;
  uniform vec3 uColor;
  uniform float uIntensity;

  void main() {
    vec2 centered = vUv - 0.5;
    float d = length(centered) * 2.0;
    float alpha = smoothstep(1.0, 0.0, d) * uIntensity;
    gl_FragColor = vec4(uColor, alpha);
  }
`;

export const glowVertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;
