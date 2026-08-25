// Ordered (Bayer 4x4) dithering, expressed as an explicit branch table instead of
// dynamic array/matrix indexing — keeps the shader portable across WebGL1/ANGLE
// backends that don't reliably support dynamic indexing in the fragment stage.
const BAYER_LOOKUP = `
float bayerDither(vec2 p) {
  float x = mod(p.x, 4.0);
  float y = mod(p.y, 4.0);
  float index = x + y * 4.0;
  if (index < 0.5) return 0.0 / 16.0;
  if (index < 1.5) return 8.0 / 16.0;
  if (index < 2.5) return 2.0 / 16.0;
  if (index < 3.5) return 10.0 / 16.0;
  if (index < 4.5) return 12.0 / 16.0;
  if (index < 5.5) return 4.0 / 16.0;
  if (index < 6.5) return 14.0 / 16.0;
  if (index < 7.5) return 6.0 / 16.0;
  if (index < 8.5) return 3.0 / 16.0;
  if (index < 9.5) return 11.0 / 16.0;
  if (index < 10.5) return 1.0 / 16.0;
  if (index < 11.5) return 9.0 / 16.0;
  if (index < 12.5) return 15.0 / 16.0;
  if (index < 13.5) return 7.0 / 16.0;
  if (index < 14.5) return 13.0 / 16.0;
  return 5.0 / 16.0;
}
`;

export const backgroundVertexShader = `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

/** Subtle dithered duotone: a slow diagonal gradient nudges chumbo toward a warm or
 * cool delta by only a few percent, and a monochromatic Bayer-dithered noise (same
 * offset on all three channels, so it never fringes into a stray hue) gives it a
 * faint technical grain. Deliberately restrained — this is a backdrop, the glyph
 * field carries the composition. Per-channel quantization was tried first and
 * produced visible color fringing (each channel rounding independently); a single
 * shared noise value avoids that entirely. */
export const backgroundFragmentShader = `
  precision mediump float;
  varying vec2 vUv;
  uniform vec3 uBase;
  uniform vec3 uWarmDelta;
  uniform vec3 uCoolDelta;
  uniform float uTime;

  ${BAYER_LOOKUP}

  void main() {
    vec2 diag = vUv - 0.5;
    float t = clamp(dot(diag, normalize(vec2(1.0, -0.6))) + 0.5 + sin(uTime * 0.05) * 0.04, 0.0, 1.0);
    vec3 delta = mix(uWarmDelta, uCoolDelta, t);

    vec2 pixelPos = floor(gl_FragCoord.xy / 4.0);
    float noise = (bayerDither(pixelPos) - 0.5) * 0.05;

    vec3 color = uBase + delta + vec3(noise);
    gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
  }
`;

export const glowVertexShader = backgroundVertexShader;

/** Soft radial falloff sprite used for the pointer "scan" glow and the click pulse
 * ring's inner fill. Additive-blended so it reads as light, not a flat disc. */
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
