import * as THREE from "three";
import type { BackgroundScene } from "../core/BackgroundScene";
import { palette } from "../utils/palette";
import { ndcToWorldPlane } from "../utils/ndc";

const CLUSTER_COUNT = 12;
const NODES_PER_CLUSTER = 12;
const TOTAL_NODES = CLUSTER_COUNT * NODES_PER_CLUSTER;

const INFLUENCE_RADIUS = 3.2;
const PUSH_STRENGTH = 0.9;
const RESPONSE_LERP = 0.12;
const IMPULSE_DURATION = 0.7;

const concreto = new THREE.Color(palette.concreto);
const urucum = new THREE.Color(palette.urucum);
const grafite = new THREE.Color(palette.grafite);

interface Impulse {
  position: THREE.Vector3;
  startTime: number;
}

/**
 * Variante "Machine": clusters de nós dispostos em círculo, girando como
 * engrenagens. O ponteiro empurra os nós próximos para fora da órbita; um
 * clique gera um pulso de repulsão que se propaga e decai com o tempo.
 */
export class MachineScene implements BackgroundScene {
  readonly object = new THREE.Group();

  private nodeCount = TOTAL_NODES;
  private renderCount = TOTAL_NODES;

  private readonly clusterCenters = new Float32Array(CLUSTER_COUNT * 3);
  private readonly clusterAngularVel = new Float32Array(CLUSTER_COUNT);
  private readonly clusterAngle = new Float32Array(CLUSTER_COUNT);

  private readonly nodeCluster = new Uint16Array(TOTAL_NODES);
  private readonly nodeBaseAngle = new Float32Array(TOTAL_NODES);
  private readonly nodeBaseRadius = new Float32Array(TOTAL_NODES);
  private readonly nodeOffset = new Float32Array(TOTAL_NODES);
  private readonly nodeOffsetTarget = new Float32Array(TOTAL_NODES);
  private readonly nodeColorMix = new Float32Array(TOTAL_NODES);
  private readonly nodePositions = new Float32Array(TOTAL_NODES * 3);

  private readonly instancedNodes: THREE.InstancedMesh;
  private readonly lines: THREE.LineSegments;
  private readonly linePositions: THREE.BufferAttribute;
  private readonly lineColors: THREE.BufferAttribute;

  private readonly dummy = new THREE.Object3D();
  private readonly pointerWorld = new THREE.Vector3();
  private readonly impulses: Impulse[] = [];
  private elapsed = 0;
  private camera: THREE.PerspectiveCamera | null = null;

  constructor() {
    this.setupClusters();
    this.setupNodes();

    const nodeGeometry = new THREE.IcosahedronGeometry(0.09, 0);
    const nodeMaterial = new THREE.MeshBasicMaterial({ color: concreto });
    this.instancedNodes = new THREE.InstancedMesh(nodeGeometry, nodeMaterial, TOTAL_NODES);
    this.instancedNodes.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this.instancedNodes.instanceColor = new THREE.InstancedBufferAttribute(
      new Float32Array(TOTAL_NODES * 3),
      3,
    );
    this.instancedNodes.instanceColor.setUsage(THREE.DynamicDrawUsage);

    const lineGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(TOTAL_NODES * 2 * 3);
    const colors = new Float32Array(TOTAL_NODES * 2 * 3);
    this.linePositions = new THREE.BufferAttribute(positions, 3).setUsage(
      THREE.DynamicDrawUsage,
    );
    this.lineColors = new THREE.BufferAttribute(colors, 3).setUsage(THREE.DynamicDrawUsage);
    lineGeometry.setAttribute("position", this.linePositions);
    lineGeometry.setAttribute("color", this.lineColors);
    const lineMaterial = new THREE.LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
    });
    this.lines = new THREE.LineSegments(lineGeometry, lineMaterial);

    this.object.add(this.lines, this.instancedNodes);
    this.computePositions(0);
    this.writeBuffers();
  }

  private setupClusters(): void {
    const cols = Math.ceil(Math.sqrt(CLUSTER_COUNT));
    const spacingX = 7.5;
    const spacingY = 5.5;
    for (let c = 0; c < CLUSTER_COUNT; c++) {
      const col = c % cols;
      const row = Math.floor(c / cols);
      const jitterX = (Math.random() - 0.5) * 1.5;
      const jitterY = (Math.random() - 0.5) * 1.5;
      this.clusterCenters[c * 3] = (col - (cols - 1) / 2) * spacingX + jitterX;
      this.clusterCenters[c * 3 + 1] = (row - (cols - 1) / 2) * spacingY + jitterY;
      this.clusterCenters[c * 3 + 2] = (Math.random() - 0.5) * 2;
      this.clusterAngularVel[c] = (Math.random() - 0.5) * 0.6 + (Math.random() < 0.5 ? -0.2 : 0.2);
      this.clusterAngle[c] = Math.random() * Math.PI * 2;
    }
  }

  private setupNodes(): void {
    let n = 0;
    for (let c = 0; c < CLUSTER_COUNT; c++) {
      for (let i = 0; i < NODES_PER_CLUSTER; i++) {
        this.nodeCluster[n] = c;
        this.nodeBaseAngle[n] = (i / NODES_PER_CLUSTER) * Math.PI * 2;
        this.nodeBaseRadius[n] = 1.1 + (i % 3) * 0.35;
        n++;
      }
    }
  }

  private computePositions(dt: number): void {
    this.elapsed += dt;
    for (let c = 0; c < CLUSTER_COUNT; c++) {
      this.clusterAngle[c] += this.clusterAngularVel[c] * dt;
    }

    for (let n = 0; n < this.nodeCount; n++) {
      const c = this.nodeCluster[n];
      const angle = this.clusterAngle[c] + this.nodeBaseAngle[n];
      const radius = this.nodeBaseRadius[n] + this.nodeOffset[n];
      const cx = this.clusterCenters[c * 3];
      const cy = this.clusterCenters[c * 3 + 1];
      const cz = this.clusterCenters[c * 3 + 2];

      this.nodePositions[n * 3] = cx + Math.cos(angle) * radius;
      this.nodePositions[n * 3 + 1] = cy + Math.sin(angle) * radius;
      this.nodePositions[n * 3 + 2] = cz;
    }
  }

  private updateInfluence(): void {
    const now = this.elapsed;

    for (let i = this.impulses.length - 1; i >= 0; i--) {
      if (now - this.impulses[i].startTime > IMPULSE_DURATION) this.impulses.splice(i, 1);
    }

    for (let n = 0; n < this.nodeCount; n++) {
      const px = this.nodePositions[n * 3];
      const py = this.nodePositions[n * 3 + 1];

      const dxPointer = px - this.pointerWorld.x;
      const dyPointer = py - this.pointerWorld.y;
      const distPointer = Math.hypot(dxPointer, dyPointer);
      let target = 0;
      if (distPointer < INFLUENCE_RADIUS) {
        target = PUSH_STRENGTH * (1 - distPointer / INFLUENCE_RADIUS);
      }

      for (const impulse of this.impulses) {
        const dx = px - impulse.position.x;
        const dy = py - impulse.position.y;
        const dist = Math.hypot(dx, dy);
        if (dist < INFLUENCE_RADIUS * 1.5) {
          const age = now - impulse.startTime;
          const decay = 1 - age / IMPULSE_DURATION;
          target += PUSH_STRENGTH * 1.8 * (1 - dist / (INFLUENCE_RADIUS * 1.5)) * decay;
        }
      }

      this.nodeOffsetTarget[n] = target;
      this.nodeOffset[n] += (this.nodeOffsetTarget[n] - this.nodeOffset[n]) * RESPONSE_LERP;
      this.nodeColorMix[n] += (Math.min(target, 1) - this.nodeColorMix[n]) * RESPONSE_LERP;
    }
  }

  private writeBuffers(): void {
    const mixColor = new THREE.Color();
    for (let n = 0; n < this.nodeCount; n++) {
      const c = this.nodeCluster[n];
      const px = this.nodePositions[n * 3];
      const py = this.nodePositions[n * 3 + 1];
      const pz = this.nodePositions[n * 3 + 2];

      this.dummy.position.set(px, py, pz);
      const scale = 1 + this.nodeColorMix[n] * 0.6;
      this.dummy.scale.setScalar(scale);
      this.dummy.updateMatrix();
      this.instancedNodes.setMatrixAt(n, this.dummy.matrix);

      mixColor.copy(concreto).lerp(urucum, this.nodeColorMix[n]);
      this.instancedNodes.setColorAt(n, mixColor);

      const cx = this.clusterCenters[c * 3];
      const cy = this.clusterCenters[c * 3 + 1];
      const cz = this.clusterCenters[c * 3 + 2];

      const base = n * 6;
      this.linePositions.array[base] = cx;
      this.linePositions.array[base + 1] = cy;
      this.linePositions.array[base + 2] = cz;
      this.linePositions.array[base + 3] = px;
      this.linePositions.array[base + 4] = py;
      this.linePositions.array[base + 5] = pz;

      this.lineColors.array[base] = grafite.r;
      this.lineColors.array[base + 1] = grafite.g;
      this.lineColors.array[base + 2] = grafite.b;
      this.lineColors.array[base + 3] = mixColor.r;
      this.lineColors.array[base + 4] = mixColor.g;
      this.lineColors.array[base + 5] = mixColor.b;
    }

    this.instancedNodes.count = this.renderCount;
    this.instancedNodes.instanceMatrix.needsUpdate = true;
    if (this.instancedNodes.instanceColor) this.instancedNodes.instanceColor.needsUpdate = true;
    this.linePositions.needsUpdate = true;
    this.lineColors.needsUpdate = true;
    this.lines.geometry.setDrawRange(0, this.renderCount * 2);
  }

  onPointerMove(ndc: THREE.Vector2): void {
    if (!this.camera) return;
    ndcToWorldPlane(ndc, this.camera, 0, this.pointerWorld);
  }

  onPointerDown(ndc: THREE.Vector2): void {
    if (!this.camera) return;
    const position = ndcToWorldPlane(ndc, this.camera, 0, new THREE.Vector3());
    this.impulses.push({ position, startTime: this.elapsed });
  }

  update(dt: number): void {
    this.computePositions(dt);
    this.updateInfluence();
    this.writeBuffers();
  }

  resize(): void {
    // Camera framing handles resize; node layout is world-space and camera-independent.
  }

  degrade(): void {
    this.renderCount = Math.max(Math.floor(this.renderCount * 0.7), NODES_PER_CLUSTER * 2);
  }

  dispose(): void {
    this.instancedNodes.geometry.dispose();
    (this.instancedNodes.material as THREE.Material).dispose();
    this.lines.geometry.dispose();
    (this.lines.material as THREE.Material).dispose();
  }

  /** Renderer injects its camera so the scene can unproject pointer NDC. */
  setCamera(camera: THREE.PerspectiveCamera): void {
    this.camera = camera;
  }
}
