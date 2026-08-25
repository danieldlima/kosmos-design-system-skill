import * as THREE from "three";

type Pt = [number, number];

function pushSeg(out: number[], a: Pt, b: Pt): void {
  out.push(a[0], a[1], 0, b[0], b[1], 0);
}

function pushPolyline(out: number[], pts: Pt[], closed = false): void {
  for (let i = 0; i < pts.length - 1; i++) pushSeg(out, pts[i], pts[i + 1]);
  if (closed) pushSeg(out, pts[pts.length - 1], pts[0]);
}

function ellipsePts(rx: number, ry: number, segments: number): Pt[] {
  const pts: Pt[] = [];
  for (let i = 0; i <= segments; i++) {
    const t = (i / segments) * Math.PI * 2;
    pts.push([Math.cos(t) * rx, Math.sin(t) * ry]);
  }
  return pts;
}

function makeGeometry(segments: number[]): THREE.BufferGeometry {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(segments, 3));
  return geometry;
}

function crosshair(): number[] {
  const out: number[] = [];
  pushSeg(out, [-0.5, 0], [0.5, 0]);
  pushSeg(out, [0, -0.5], [0, 0.5]);
  pushPolyline(out, [[-0.08, 0], [0, 0.08], [0.08, 0], [0, -0.08]], true);
  return out;
}

function radar(): number[] {
  const out: number[] = [];
  pushPolyline(out, ellipsePts(0.18, 0.18, 16), true);
  pushPolyline(out, ellipsePts(0.32, 0.32, 20), true);
  pushPolyline(out, ellipsePts(0.46, 0.46, 24), true);
  pushSeg(out, [0, 0.46], [0, 0.5]);
  pushSeg(out, [0.46, 0], [0.5, 0]);
  return out;
}

function sineWave(): number[] {
  const out: number[] = [];
  const pts: Pt[] = [];
  const steps = 20;
  for (let i = 0; i <= steps; i++) {
    const x = -0.5 + (i / steps) * 1.0;
    const y = 0.18 * Math.sin((x + 0.5) * 4 * Math.PI);
    pts.push([x, y]);
  }
  pushPolyline(out, pts);
  return out;
}

function zigzag(): number[] {
  const out: number[] = [];
  pushPolyline(out, [
    [-0.5, 0],
    [-0.3, 0.25],
    [-0.1, -0.2],
    [0.1, 0.25],
    [0.3, -0.2],
    [0.5, 0.1],
  ]);
  return out;
}

function sparkle(): number[] {
  const out: number[] = [];
  const arms = 8;
  for (let i = 0; i < arms; i++) {
    const angle = (i / arms) * Math.PI * 2;
    const length = i % 2 === 0 ? 0.5 : 0.32;
    pushSeg(out, [0, 0], [Math.cos(angle) * length, Math.sin(angle) * length]);
  }
  return out;
}

function viewfinder(): number[] {
  const out: number[] = [];
  const bracket = 0.18;
  for (const cx of [-0.5, 0.5]) {
    for (const cy of [-0.5, 0.5]) {
      const dx = cx > 0 ? -bracket : bracket;
      const dy = cy > 0 ? -bracket : bracket;
      pushSeg(out, [cx, cy], [cx + dx, cy]);
      pushSeg(out, [cx, cy], [cx, cy + dy]);
    }
  }
  pushPolyline(
    out,
    [
      [-0.15, -0.15],
      [0.15, -0.15],
      [0.15, 0.15],
      [-0.15, 0.15],
    ],
    true,
  );
  return out;
}

function ascendingBars(): number[] {
  const out: number[] = [];
  const xs = [-0.4, -0.2, 0, 0.2, 0.4];
  const heights = [0.2, 0.32, 0.44, 0.56, 0.68].map((h) => h * 0.75);
  xs.forEach((x, i) => pushSeg(out, [x, -0.5], [x, -0.5 + heights[i]]));
  return out;
}

function grid(): number[] {
  const out: number[] = [];
  pushSeg(out, [-0.17, -0.5], [-0.17, 0.5]);
  pushSeg(out, [0.17, -0.5], [0.17, 0.5]);
  pushSeg(out, [-0.5, -0.17], [0.5, -0.17]);
  pushSeg(out, [-0.5, 0.17], [0.5, 0.17]);
  const dot = ellipsePts(0.05, 0.05, 10).map(([x, y]): Pt => [x + 0.3, y + 0.3]);
  pushPolyline(out, dot, true);
  return out;
}

function globe(): number[] {
  const out: number[] = [];
  pushPolyline(out, ellipsePts(0.5, 0.5, 28), true);
  pushPolyline(out, ellipsePts(0.5, 0.16, 24), true);
  pushPolyline(out, ellipsePts(0.16, 0.5, 24), true);
  return out;
}

function octahedron(): number[] {
  const out: number[] = [];
  pushPolyline(
    out,
    [
      [0, 0.5],
      [0.5, 0],
      [0, -0.5],
      [-0.5, 0],
    ],
    true,
  );
  pushSeg(out, [0, 0.5], [0, -0.5]);
  pushSeg(out, [-0.5, 0], [0.5, 0]);
  return out;
}

/** Small library of thin-line technical glyphs (radar, waveform, viewfinder, etc.), each
 * built in a local -0.5..0.5 box on the XY plane. Instances share these geometries and
 * differ only by transform/material, so the count of on-screen icons stays cheap. */
export function buildGlyphGeometries(): THREE.BufferGeometry[] {
  return [
    crosshair,
    radar,
    sineWave,
    zigzag,
    sparkle,
    viewfinder,
    ascendingBars,
    grid,
    globe,
    octahedron,
  ].map((builder) => makeGeometry(builder()));
}
