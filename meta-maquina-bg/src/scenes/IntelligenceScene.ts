import * as THREE from "three";
import type { BackgroundScene } from "../core/BackgroundScene";
import { palette, sampleInstitutoGradient } from "../utils/palette";
import { ndcToWorldPlane } from "../utils/ndc";

const PARTICLE_COUNT = 420;
const BOUNDS = { x: 16, y: 9, z: 4 };
const NEIGHBOR_RADIUS = 2.1;
const NEIGHBOR_RADIUS_SQ = NEIGHBOR_RADIUS * NEIGHBOR_RADIUS;
const CELL_SIZE = NEIGHBOR_RADIUS;
const REGRAPH_INTERVAL = 0.12; // seconds; the neighbor graph is not rebuilt every frame
const ATTENTION_RADIUS = 3.5;
const MAX_HOPS = 2;
const PULSE_DURATION = 1.4;

const grafite = new THREE.Color(palette.grafite);

interface Edge {
  a: number;
  b: number;
}

interface Pulse {
  origin: number; // particle index
  startTime: number;
}

/**
 * Variante "Intelligence": nuvem de partículas com drift tipo flow-field,
 * conectadas por um grafo de vizinhança recalculado periodicamente. O
 * ponteiro acende a "atenção" das partículas próximas; o clique dispara um
 * pulso que se propaga pelo grafo (1-2 saltos) com decaimento por distância.
 */
export class IntelligenceScene implements BackgroundScene {
  readonly object = new THREE.Group();

  private activeCount = PARTICLE_COUNT;
  private readonly positions = new Float32Array(PARTICLE_COUNT * 3);
  private readonly velocities = new Float32Array(PARTICLE_COUNT * 3);
  private readonly noiseSeed = new Float32Array(PARTICLE_COUNT * 3);
  private readonly attention = new Float32Array(PARTICLE_COUNT);

  private readonly points: THREE.Points;
  private readonly pointGeometry: THREE.BufferGeometry;
  private readonly pointColorAttr: THREE.BufferAttribute;

  private readonly lines: THREE.LineSegments;
  private readonly lineGeometry: THREE.BufferGeometry;
  private edges: Edge[] = [];
  private readonly grid = new Map<string, number[]>();

  private readonly pulses: Pulse[] = [];
  private readonly dummyColor = new THREE.Color();
  private readonly pointerWorld = new THREE.Vector3(0, 0, 0);
  private camera: THREE.PerspectiveCamera | null = null;
  private elapsed = 0;
  private timeSinceRegraph = 0;

  constructor() {
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      this.positions[i * 3] = (Math.random() - 0.5) * BOUNDS.x * 2;
      this.positions[i * 3 + 1] = (Math.random() - 0.5) * BOUNDS.y * 2;
      this.positions[i * 3 + 2] = (Math.random() - 0.5) * BOUNDS.z * 2;
      this.noiseSeed[i * 3] = Math.random() * 1000;
      this.noiseSeed[i * 3 + 1] = Math.random() * 1000;
      this.noiseSeed[i * 3 + 2] = Math.random() * 1000;
    }

    this.pointGeometry = new THREE.BufferGeometry();
    const positionAttr = new THREE.BufferAttribute(this.positions, 3).setUsage(
      THREE.DynamicDrawUsage,
    );
    this.pointColorAttr = new THREE.BufferAttribute(
      new Float32Array(PARTICLE_COUNT * 3),
      3,
    ).setUsage(THREE.DynamicDrawUsage);
    this.pointGeometry.setAttribute("position", positionAttr);
    this.pointGeometry.setAttribute("color", this.pointColorAttr);
    const pointMaterial = new THREE.PointsMaterial({
      size: 0.09,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      sizeAttenuation: true,
    });
    this.points = new THREE.Points(this.pointGeometry, pointMaterial);

    this.lineGeometry = new THREE.BufferGeometry();
    // Sized for a generous edge budget; actual draw range follows the live edge count.
    const maxEdges = PARTICLE_COUNT * 6;
    this.lineGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(new Float32Array(maxEdges * 2 * 3), 3).setUsage(
        THREE.DynamicDrawUsage,
      ),
    );
    this.lineGeometry.setAttribute(
      "color",
      new THREE.BufferAttribute(new Float32Array(maxEdges * 2 * 3), 3).setUsage(
        THREE.DynamicDrawUsage,
      ),
    );
    const lineMaterial = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.55,
    });
    this.lines = new THREE.LineSegments(this.lineGeometry, lineMaterial);

    this.object.add(this.lines, this.points);
    this.rebuildGraph();
    this.writeBuffers();
  }

  private cellKey(x: number, y: number, z: number): string {
    const cx = Math.floor(x / CELL_SIZE);
    const cy = Math.floor(y / CELL_SIZE);
    const cz = Math.floor(z / CELL_SIZE);
    return `${cx},${cy},${cz}`;
  }

  /** Spatial-hash neighbor search: O(n) instead of O(n^2) for the edge rebuild. */
  private rebuildGraph(): void {
    this.grid.clear();
    for (let i = 0; i < this.activeCount; i++) {
      const key = this.cellKey(this.positions[i * 3], this.positions[i * 3 + 1], this.positions[i * 3 + 2]);
      let bucket = this.grid.get(key);
      if (!bucket) {
        bucket = [];
        this.grid.set(key, bucket);
      }
      bucket.push(i);
    }

    const edges: Edge[] = [];
    const seen = new Set<string>();

    for (let i = 0; i < this.activeCount; i++) {
      const px = this.positions[i * 3];
      const py = this.positions[i * 3 + 1];
      const pz = this.positions[i * 3 + 2];
      const cx = Math.floor(px / CELL_SIZE);
      const cy = Math.floor(py / CELL_SIZE);
      const cz = Math.floor(pz / CELL_SIZE);

      for (let dx = -1; dx <= 1; dx++) {
        for (let dy = -1; dy <= 1; dy++) {
          for (let dz = -1; dz <= 1; dz++) {
            const bucket = this.grid.get(`${cx + dx},${cy + dy},${cz + dz}`);
            if (!bucket) continue;
            for (const j of bucket) {
              if (j <= i) continue;
              const ddx = px - this.positions[j * 3];
              const ddy = py - this.positions[j * 3 + 1];
              const ddz = pz - this.positions[j * 3 + 2];
              const distSq = ddx * ddx + ddy * ddy + ddz * ddz;
              if (distSq < NEIGHBOR_RADIUS_SQ) {
                const key = `${i}-${j}`;
                if (!seen.has(key)) {
                  seen.add(key);
                  edges.push({ a: i, b: j });
                }
              }
            }
          }
        }
      }
    }

    this.edges = edges;
  }

  private driftParticles(dt: number): void {
    this.elapsed += dt;
    const t = this.elapsed * 0.15;
    for (let i = 0; i < this.activeCount; i++) {
      const sx = this.noiseSeed[i * 3];
      const sy = this.noiseSeed[i * 3 + 1];
      const sz = this.noiseSeed[i * 3 + 2];

      // Cheap pseudo-flow-field: layered sines per particle seed, not real
      // simplex noise, but visually indistinguishable at this scale/cost.
      const vx = Math.sin(t + sx) * 0.4;
      const vy = Math.cos(t * 0.9 + sy) * 0.4;
      const vz = Math.sin(t * 0.7 + sz) * 0.25;

      this.velocities[i * 3] = vx;
      this.velocities[i * 3 + 1] = vy;
      this.velocities[i * 3 + 2] = vz;

      let px = this.positions[i * 3] + vx * dt;
      let py = this.positions[i * 3 + 1] + vy * dt;
      let pz = this.positions[i * 3 + 2] + vz * dt;

      if (px > BOUNDS.x) px = -BOUNDS.x;
      if (px < -BOUNDS.x) px = BOUNDS.x;
      if (py > BOUNDS.y) py = -BOUNDS.y;
      if (py < -BOUNDS.y) py = BOUNDS.y;
      if (pz > BOUNDS.z) pz = -BOUNDS.z;
      if (pz < -BOUNDS.z) pz = BOUNDS.z;

      this.positions[i * 3] = px;
      this.positions[i * 3 + 1] = py;
      this.positions[i * 3 + 2] = pz;
    }
  }

  private updateAttentionAndPulses(): void {
    for (let i = 0; i < this.activeCount; i++) {
      const dx = this.positions[i * 3] - this.pointerWorld.x;
      const dy = this.positions[i * 3 + 1] - this.pointerWorld.y;
      const dist = Math.hypot(dx, dy);
      const pointerAttention = dist < ATTENTION_RADIUS ? 1 - dist / ATTENTION_RADIUS : 0;
      this.attention[i] += (pointerAttention - this.attention[i]) * 0.1;
    }

    if (this.pulses.length === 0) return;

    const now = this.elapsed;
    for (let p = this.pulses.length - 1; p >= 0; p--) {
      if (now - this.pulses[p].startTime > PULSE_DURATION) this.pulses.splice(p, 1);
    }

    for (const pulse of this.pulses) {
      const age = now - pulse.startTime;
      const hopFrontier = this.bfsHops(pulse.origin, MAX_HOPS);
      for (const [index, hop] of hopFrontier) {
        const hopDelay = hop * 0.18;
        const localAge = age - hopDelay;
        if (localAge < 0) continue;
        const decay = Math.max(0, 1 - localAge / (PULSE_DURATION - hopDelay));
        this.attention[index] = Math.max(this.attention[index], decay);
      }
    }
  }

  private bfsHops(origin: number, maxHops: number): Map<number, number> {
    const hops = new Map<number, number>([[origin, 0]]);
    const adjacency = this.adjacencyFor(origin, maxHops);
    let frontier = [origin];
    for (let hop = 1; hop <= maxHops; hop++) {
      const next: number[] = [];
      for (const node of frontier) {
        for (const neighbor of adjacency.get(node) ?? []) {
          if (!hops.has(neighbor)) {
            hops.set(neighbor, hop);
            next.push(neighbor);
          }
        }
      }
      frontier = next;
    }
    return hops;
  }

  /** Builds a small local adjacency list on demand instead of maintaining a full one every frame. */
  private adjacencyFor(origin: number, maxHops: number): Map<number, number[]> {
    const relevant = new Set<number>([origin]);
    let frontierIds = [origin];
    const adjacency = new Map<number, number[]>();

    for (let hop = 0; hop < maxHops; hop++) {
      const nextFrontier: number[] = [];
      for (const edge of this.edges) {
        const touchesA = frontierIds.includes(edge.a);
        const touchesB = frontierIds.includes(edge.b);
        if (!touchesA && !touchesB) continue;

        if (!adjacency.has(edge.a)) adjacency.set(edge.a, []);
        if (!adjacency.has(edge.b)) adjacency.set(edge.b, []);
        adjacency.get(edge.a)!.push(edge.b);
        adjacency.get(edge.b)!.push(edge.a);

        if (touchesA && !relevant.has(edge.b)) {
          relevant.add(edge.b);
          nextFrontier.push(edge.b);
        }
        if (touchesB && !relevant.has(edge.a)) {
          relevant.add(edge.a);
          nextFrontier.push(edge.a);
        }
      }
      frontierIds = nextFrontier;
    }
    return adjacency;
  }

  private writeBuffers(): void {
    for (let i = 0; i < this.activeCount; i++) {
      this.dummyColor.copy(grafite).lerp(
        new THREE.Color(sampleInstitutoGradient(this.attention[i])),
        this.attention[i],
      );
      this.pointColorAttr.array[i * 3] = this.dummyColor.r;
      this.pointColorAttr.array[i * 3 + 1] = this.dummyColor.g;
      this.pointColorAttr.array[i * 3 + 2] = this.dummyColor.b;
    }

    const linePositions = this.lineGeometry.getAttribute("position") as THREE.BufferAttribute;
    const lineColors = this.lineGeometry.getAttribute("color") as THREE.BufferAttribute;
    const maxEdges = linePositions.count / 2;
    const edgeCount = Math.min(this.edges.length, maxEdges);

    for (let e = 0; e < edgeCount; e++) {
      const { a, b } = this.edges[e];
      const base = e * 6;
      linePositions.array[base] = this.positions[a * 3];
      linePositions.array[base + 1] = this.positions[a * 3 + 1];
      linePositions.array[base + 2] = this.positions[a * 3 + 2];
      linePositions.array[base + 3] = this.positions[b * 3];
      linePositions.array[base + 4] = this.positions[b * 3 + 1];
      linePositions.array[base + 5] = this.positions[b * 3 + 2];

      const edgeAttention = Math.max(this.attention[a], this.attention[b]);
      this.dummyColor.copy(grafite).lerp(
        new THREE.Color(sampleInstitutoGradient(edgeAttention)),
        edgeAttention,
      );
      lineColors.array[base] = this.dummyColor.r;
      lineColors.array[base + 1] = this.dummyColor.g;
      lineColors.array[base + 2] = this.dummyColor.b;
      lineColors.array[base + 3] = this.dummyColor.r;
      lineColors.array[base + 4] = this.dummyColor.g;
      lineColors.array[base + 5] = this.dummyColor.b;
    }

    this.lineGeometry.setDrawRange(0, edgeCount * 2);
    linePositions.needsUpdate = true;
    lineColors.needsUpdate = true;

    this.pointGeometry.setDrawRange(0, this.activeCount);
    (this.pointGeometry.getAttribute("position") as THREE.BufferAttribute).needsUpdate = true;
    this.pointColorAttr.needsUpdate = true;
  }

  private nearestParticle(world: THREE.Vector3): number {
    let best = 0;
    let bestDist = Infinity;
    for (let i = 0; i < this.activeCount; i++) {
      const dx = this.positions[i * 3] - world.x;
      const dy = this.positions[i * 3 + 1] - world.y;
      const dist = dx * dx + dy * dy;
      if (dist < bestDist) {
        bestDist = dist;
        best = i;
      }
    }
    return best;
  }

  setCamera(camera: THREE.PerspectiveCamera): void {
    this.camera = camera;
  }

  onPointerMove(ndc: THREE.Vector2): void {
    if (!this.camera) return;
    ndcToWorldPlane(ndc, this.camera, 0, this.pointerWorld);
  }

  onPointerDown(ndc: THREE.Vector2): void {
    if (!this.camera) return;
    const world = ndcToWorldPlane(ndc, this.camera, 0, new THREE.Vector3());
    const origin = this.nearestParticle(world);
    this.pulses.push({ origin, startTime: this.elapsed });
  }

  update(dt: number): void {
    this.driftParticles(dt);

    this.timeSinceRegraph += dt;
    if (this.timeSinceRegraph >= REGRAPH_INTERVAL) {
      this.timeSinceRegraph = 0;
      this.rebuildGraph();
    }

    this.updateAttentionAndPulses();
    this.writeBuffers();
  }

  resize(): void {
    // Particle field is world-space and camera-independent; nothing to recompute on resize.
  }

  degrade(): void {
    this.activeCount = Math.max(Math.floor(this.activeCount * 0.7), 60);
  }

  dispose(): void {
    this.pointGeometry.dispose();
    (this.points.material as THREE.Material).dispose();
    this.lineGeometry.dispose();
    (this.lines.material as THREE.Material).dispose();
  }
}
