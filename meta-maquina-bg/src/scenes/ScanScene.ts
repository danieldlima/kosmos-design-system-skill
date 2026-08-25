import * as THREE from "three";
import type { BackgroundScene } from "../core/BackgroundScene";
import { palette } from "../utils/palette";
import { ndcToWorldPlane } from "../utils/ndc";
import {
  glowFragmentShader,
  glowVertexShader,
  gridFragmentShader,
  worldPlaneVertexShader,
} from "./scanShaders";

// Every dimension here is a deliberate, disciplined grid: no randomized rotation, no
// per-instance jitter. Precision over ornament, per the brandbook's own composition
// rule ("hairline rules and precise edge alignment carry the structure").
const MINOR_SPACING = 1.5;
const MAJOR_STEP = 3; // a major node sits on every 3rd minor grid line
const FIELD_X = 18;
const FIELD_Y = 10;

const ATTENTION_RADIUS = 3.0;
const CONNECTOR_MAX = 4;
const RESPONSE_LERP = 0.14;

const RING_POOL_SIZE = 4;
const RING_MAX_RADIUS = 3.4;
const RING_DURATION = 0.9;
const RING_BAND = 0.3;

const ORBIT_RADII = [4.2, 6.6, 9.0, 11.4];
const ORBIT_PERIOD_SECONDS = [46, 36, 28, 24]; // slow ambient rings, per motion-grammar guidance

const chumbo = new THREE.Color(palette.chumbo);
const concreto = new THREE.Color(palette.concreto);
const urucum = new THREE.Color(palette.urucum);

interface MajorNode {
  mesh: THREE.LineLoop;
  material: THREE.LineBasicMaterial;
  x: number;
  y: number;
  attention: number;
}

interface RingPulse {
  origin: THREE.Vector3;
  startTime: number;
  active: boolean;
  mesh: THREE.LineLoop;
  material: THREE.LineBasicMaterial;
}

/**
 * Variante "Scan": um campo de coordenadas — grid de hairlines, nós alinhados à grade e
 * anéis orbitais finos, na linguagem que o brandbook já documenta para superfícies escuras
 * (hairlines precisas, urucum como acento seletivo, glow contido). O ponteiro acende os nós
 * próximos e traça conectores finos até eles; o clique dispara um anel que percorre a cena.
 */
export class ScanScene implements BackgroundScene {
  readonly object = new THREE.Group();

  private readonly background: THREE.Mesh;
  private readonly gridMaterial: THREE.ShaderMaterial;

  private readonly minorDots: THREE.InstancedMesh;
  private readonly majors: MajorNode[] = [];
  private readonly orbits: THREE.LineLoop[] = [];

  private readonly connectors: THREE.LineSegments;
  private readonly connectorPositions: THREE.BufferAttribute;

  private readonly glow: THREE.Mesh;
  private readonly glowMaterial: THREE.ShaderMaterial;
  private readonly rings: RingPulse[] = [];

  private camera: THREE.PerspectiveCamera | null = null;
  private readonly pointerWorld = new THREE.Vector3(9999, 9999, 0);
  private elapsed = 0;

  constructor() {
    this.gridMaterial = new THREE.ShaderMaterial({
      vertexShader: worldPlaneVertexShader,
      fragmentShader: gridFragmentShader,
      uniforms: {
        uBase: { value: chumbo.clone() },
        uLine: { value: concreto.clone() },
        uSpacing: { value: MINOR_SPACING },
        uLineWidth: { value: 0.012 },
        uOpacity: { value: 0.07 },
      },
      depthWrite: false,
    });
    this.background = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), this.gridMaterial);
    this.background.position.z = -6;
    this.object.add(this.background);

    // Minor grid points: one InstancedMesh, one draw call, purely structural (no
    // per-instance state) — the "many elements" budget goes here, not into ornament.
    const dotGeometry = new THREE.CircleGeometry(0.035, 8);
    const dotMaterial = new THREE.MeshBasicMaterial({
      color: concreto,
      transparent: true,
      opacity: 0.22,
    });
    const cols = Math.floor((FIELD_X * 2) / MINOR_SPACING);
    const rows = Math.floor((FIELD_Y * 2) / MINOR_SPACING);
    this.minorDots = new THREE.InstancedMesh(dotGeometry, dotMaterial, cols * rows);
    const dummy = new THREE.Object3D();
    let dotIndex = 0;
    for (let ix = 0; ix < cols; ix++) {
      for (let iy = 0; iy < rows; iy++) {
        const x = -FIELD_X + ix * MINOR_SPACING;
        const y = -FIELD_Y + iy * MINOR_SPACING;
        dummy.position.set(x, y, 0);
        dummy.updateMatrix();
        this.minorDots.setMatrixAt(dotIndex++, dummy.matrix);
      }
    }
    this.object.add(this.minorDots);

    // Major nodes: a thin ring outline, identical size, grid-snapped — the interactive
    // layer. Uniformity is the point; variety would read as decoration again.
    const ringSegments = 20;
    const nodeGeometry = new THREE.BufferGeometry();
    const nodePoints: number[] = [];
    for (let i = 0; i < ringSegments; i++) {
      const t = (i / ringSegments) * Math.PI * 2;
      nodePoints.push(Math.cos(t) * 0.11, Math.sin(t) * 0.11, 0);
    }
    nodeGeometry.setAttribute("position", new THREE.Float32BufferAttribute(nodePoints, 3));

    const majorSpacing = MINOR_SPACING * MAJOR_STEP;
    const majorCols = Math.floor((FIELD_X * 2) / majorSpacing);
    const majorRows = Math.floor((FIELD_Y * 2) / majorSpacing);
    for (let ix = 0; ix < majorCols; ix++) {
      for (let iy = 0; iy < majorRows; iy++) {
        const x = -FIELD_X + majorSpacing / 2 + ix * majorSpacing;
        const y = -FIELD_Y + majorSpacing / 2 + iy * majorSpacing;
        const material = new THREE.LineBasicMaterial({
          color: concreto,
          transparent: true,
          opacity: 0.55,
        });
        const mesh = new THREE.LineLoop(nodeGeometry, material);
        mesh.position.set(x, y, 0);
        this.object.add(mesh);
        this.majors.push({ mesh, material, x, y, attention: 0 });
      }
    }

    // Orbit rings: the brandbook's own "thin orbital lines, peripheral glow" motif —
    // slow, ambient, independent of the pointer.
    const orbitSegments = 96;
    const orbitPoints: number[] = [];
    for (let i = 0; i < orbitSegments; i++) {
      const t = (i / orbitSegments) * Math.PI * 2;
      orbitPoints.push(Math.cos(t), Math.sin(t), 0);
    }
    const orbitGeometry = new THREE.BufferGeometry();
    orbitGeometry.setAttribute("position", new THREE.Float32BufferAttribute(orbitPoints, 3));
    for (const radius of ORBIT_RADII) {
      const material = new THREE.LineBasicMaterial({
        color: concreto,
        transparent: true,
        opacity: 0.16,
      });
      const ring = new THREE.LineLoop(orbitGeometry, material);
      ring.scale.setScalar(radius);
      ring.position.z = -1;
      this.object.add(ring);
      this.orbits.push(ring);
    }

    // Connectors: thin hairlines from the pointer to the nearest active major nodes —
    // the expressive ramp's documented use as "thin progress rails, connectors, data-flow
    // paths," nothing more.
    const connectorGeometry = new THREE.BufferGeometry();
    this.connectorPositions = new THREE.BufferAttribute(
      new Float32Array(CONNECTOR_MAX * 2 * 3),
      3,
    ).setUsage(THREE.DynamicDrawUsage);
    connectorGeometry.setAttribute("position", this.connectorPositions);
    const connectorMaterial = new THREE.LineBasicMaterial({
      color: urucum,
      transparent: true,
      opacity: 0.5,
    });
    this.connectors = new THREE.LineSegments(connectorGeometry, connectorMaterial);
    this.connectors.geometry.setDrawRange(0, 0);
    this.object.add(this.connectors);

    // Pointer focus: a small, tight glow — urucum used as a selective reading accent,
    // never an all-over fill.
    this.glowMaterial = new THREE.ShaderMaterial({
      vertexShader: glowVertexShader,
      fragmentShader: glowFragmentShader,
      uniforms: {
        uColor: { value: urucum.clone() },
        uIntensity: { value: 0.4 },
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    this.glow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), this.glowMaterial);
    this.glow.position.z = -0.2;
    this.glow.scale.setScalar(ATTENTION_RADIUS * 1.1);
    this.object.add(this.glow);

    const ringGeometry = new THREE.BufferGeometry();
    const ringPoints: number[] = [];
    const clickRingSegments = 48;
    for (let i = 0; i < clickRingSegments; i++) {
      const t = (i / clickRingSegments) * Math.PI * 2;
      ringPoints.push(Math.cos(t), Math.sin(t), 0);
    }
    ringGeometry.setAttribute("position", new THREE.Float32BufferAttribute(ringPoints, 3));
    for (let i = 0; i < RING_POOL_SIZE; i++) {
      const material = new THREE.LineBasicMaterial({
        color: urucum,
        transparent: true,
        opacity: 0,
      });
      const mesh = new THREE.LineLoop(ringGeometry, material);
      mesh.visible = false;
      this.object.add(mesh);
      this.rings.push({ origin: new THREE.Vector3(), startTime: 0, active: false, mesh, material });
    }
  }

  private frustumSizeAt(z: number): { width: number; height: number } {
    if (!this.camera) return { width: 1, height: 1 };
    const distance = this.camera.position.z - z;
    const height = 2 * distance * Math.tan((this.camera.fov * Math.PI) / 360);
    return { width: height * this.camera.aspect, height };
  }

  private updateMajors(): void {
    for (const node of this.majors) {
      const dx = node.x - this.pointerWorld.x;
      const dy = node.y - this.pointerWorld.y;
      let target = Math.max(0, 1 - Math.hypot(dx, dy) / ATTENTION_RADIUS);

      for (const ring of this.rings) {
        if (!ring.active) continue;
        const age = this.elapsed - ring.startTime;
        const radius = (age / RING_DURATION) * RING_MAX_RADIUS;
        const distToOrigin = Math.hypot(node.x - ring.origin.x, node.y - ring.origin.y);
        const band = Math.abs(distToOrigin - radius);
        if (band < RING_BAND) {
          const decay = Math.max(0, 1 - age / RING_DURATION);
          target = Math.max(target, (1 - band / RING_BAND) * decay);
        }
      }

      node.attention += (target - node.attention) * RESPONSE_LERP;
      node.material.color.copy(concreto).lerp(urucum, node.attention);
      node.material.opacity = 0.4 + node.attention * 0.6;
      const scale = 1 + node.attention * 0.5;
      node.mesh.scale.setScalar(scale);
    }
  }

  private updateConnectors(): void {
    const withinRange = this.majors
      .map((node) => ({ node, dist: Math.hypot(node.x - this.pointerWorld.x, node.y - this.pointerWorld.y) }))
      .filter((entry) => entry.dist < ATTENTION_RADIUS)
      .sort((a, b) => a.dist - b.dist)
      .slice(0, CONNECTOR_MAX);

    for (let i = 0; i < withinRange.length; i++) {
      const { node } = withinRange[i];
      const base = i * 6;
      this.connectorPositions.array[base] = this.pointerWorld.x;
      this.connectorPositions.array[base + 1] = this.pointerWorld.y;
      this.connectorPositions.array[base + 2] = 0;
      this.connectorPositions.array[base + 3] = node.x;
      this.connectorPositions.array[base + 4] = node.y;
      this.connectorPositions.array[base + 5] = 0;
    }
    this.connectors.geometry.setDrawRange(0, withinRange.length * 2);
    this.connectorPositions.needsUpdate = true;
  }

  private updateOrbits(dt: number): void {
    for (let i = 0; i < this.orbits.length; i++) {
      const angularVelocity = (Math.PI * 2) / ORBIT_PERIOD_SECONDS[i % ORBIT_PERIOD_SECONDS.length];
      this.orbits[i].rotation.z += angularVelocity * dt * (i % 2 === 0 ? 1 : -1);
    }
  }

  private updateRings(): void {
    for (const ring of this.rings) {
      if (!ring.active) continue;
      const age = this.elapsed - ring.startTime;
      if (age > RING_DURATION) {
        ring.active = false;
        ring.mesh.visible = false;
        continue;
      }
      const t = age / RING_DURATION;
      const radius = 0.2 + t * (RING_MAX_RADIUS - 0.2);
      ring.mesh.position.copy(ring.origin);
      ring.mesh.scale.setScalar(radius);
      ring.material.opacity = (1 - t) * 0.6;
    }
  }

  onPointerMove(ndc: THREE.Vector2): void {
    if (!this.camera) return;
    ndcToWorldPlane(ndc, this.camera, 0, this.pointerWorld);
    this.glow.position.x = this.pointerWorld.x;
    this.glow.position.y = this.pointerWorld.y;
  }

  onPointerDown(ndc: THREE.Vector2): void {
    if (!this.camera) return;
    const world = ndcToWorldPlane(ndc, this.camera, 0, new THREE.Vector3());
    const ring = this.rings.reduce((oldest, r) => (r.startTime < oldest.startTime ? r : oldest));
    ring.origin.copy(world);
    ring.startTime = this.elapsed;
    ring.active = true;
    ring.mesh.visible = true;
  }

  update(dt: number): void {
    this.elapsed += dt;
    this.updateMajors();
    this.updateConnectors();
    this.updateOrbits(dt);
    this.updateRings();
  }

  resize(): void {
    if (!this.camera) return;
    const bg = this.frustumSizeAt(this.background.position.z);
    this.background.scale.set(bg.width, bg.height, 1);
  }

  degrade(): void {
    // The minor grid is a single draw call already; degrading further would break the
    // grid's continuity, so instead thin out the ambient orbit rings first.
    for (const ring of this.orbits.splice(1)) {
      this.object.remove(ring);
    }
  }

  dispose(): void {
    this.background.geometry.dispose();
    this.gridMaterial.dispose();
    this.minorDots.geometry.dispose();
    (this.minorDots.material as THREE.Material).dispose();
    for (const node of this.majors) node.material.dispose();
    if (this.majors[0]) this.majors[0].mesh.geometry.dispose();
    for (const ring of this.orbits) (ring.material as THREE.Material).dispose();
    if (this.orbits[0]) this.orbits[0].geometry.dispose();
    this.connectors.geometry.dispose();
    (this.connectors.material as THREE.Material).dispose();
    this.glow.geometry.dispose();
    this.glowMaterial.dispose();
    for (const ring of this.rings) ring.material.dispose();
    if (this.rings[0]) this.rings[0].mesh.geometry.dispose();
  }

  setCamera(camera: THREE.PerspectiveCamera): void {
    this.camera = camera;
  }
}
