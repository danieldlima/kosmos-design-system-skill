import * as THREE from "three";
import type { BackgroundScene } from "../core/BackgroundScene";
import { palette } from "../utils/palette";
import { ndcToWorldPlane } from "../utils/ndc";
import { buildGlyphGeometries } from "./glyphs";
import {
  backgroundFragmentShader,
  backgroundVertexShader,
  glowFragmentShader,
  glowVertexShader,
} from "./scanShaders";

const GLYPH_COUNT = 130;
const FIELD_X = 18;
const FIELD_Y = 10;
const ATTENTION_RADIUS = 3.2;
const RESPONSE_LERP = 0.12;
const RING_POOL_SIZE = 5;
const RING_MAX_RADIUS = 5;
const RING_DURATION = 1.1;
const RING_BAND = 0.4;

const chumbo = new THREE.Color(palette.chumbo);
const concreto = new THREE.Color(palette.concreto);
const grafite = new THREE.Color(palette.grafite);
const urucum = new THREE.Color(palette.urucum);

interface GlyphInstance {
  group: THREE.Group;
  material: THREE.LineBasicMaterial;
  x: number;
  y: number;
  z: number;
  baseScale: number;
  angularVelocity: number;
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
 * Variante "Scan": campo de glifos técnicos em linha fina (radar, mira, onda,
 * viewfinder, grid...) espalhados como um painel de instrumentação. O ponteiro
 * projeta um glow que "acende" os glifos próximos; o clique dispara um anel de
 * radar que se expande e ativa os glifos que atravessa.
 */
export class ScanScene implements BackgroundScene {
  readonly object = new THREE.Group();

  private readonly glyphGeometries = buildGlyphGeometries();
  private readonly glyphs: GlyphInstance[] = [];
  private visibleCount = GLYPH_COUNT;

  private readonly background: THREE.Mesh;
  private readonly backgroundMaterial: THREE.ShaderMaterial;
  private readonly glow: THREE.Mesh;
  private readonly glowMaterial: THREE.ShaderMaterial;
  private readonly rings: RingPulse[] = [];

  private camera: THREE.PerspectiveCamera | null = null;
  private readonly pointerWorld = new THREE.Vector3(9999, 9999, 0);
  private elapsed = 0;

  constructor() {
    for (let i = 0; i < GLYPH_COUNT; i++) {
      const geometry = this.glyphGeometries[i % this.glyphGeometries.length];
      const material = new THREE.LineBasicMaterial({
        color: concreto,
        transparent: true,
        opacity: 0.45,
      });
      const line = new THREE.LineSegments(geometry, material);
      const group = new THREE.Group();
      group.add(line);

      const x = (Math.random() - 0.5) * FIELD_X * 2;
      const y = (Math.random() - 0.5) * FIELD_Y * 2;
      const z = (Math.random() - 0.5) * 2;
      const baseScale = 0.55 + Math.random() * 0.7;
      group.position.set(x, y, z);
      group.scale.setScalar(baseScale);
      group.rotation.z = Math.random() * Math.PI * 2;

      this.object.add(group);
      this.glyphs.push({
        group,
        material,
        x,
        y,
        z,
        baseScale,
        angularVelocity: (Math.random() - 0.5) * 0.3,
        attention: 0,
      });
    }

    this.backgroundMaterial = new THREE.ShaderMaterial({
      vertexShader: backgroundVertexShader,
      fragmentShader: backgroundFragmentShader,
      uniforms: {
        uBase: { value: chumbo.clone() },
        uWarmDelta: { value: urucum.clone().sub(chumbo).multiplyScalar(0.1) },
        uCoolDelta: { value: grafite.clone().sub(chumbo).multiplyScalar(0.16) },
        uTime: { value: 0 },
      },
      depthWrite: false,
    });
    this.background = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), this.backgroundMaterial);
    this.background.position.z = -8;
    this.object.add(this.background);

    this.glowMaterial = new THREE.ShaderMaterial({
      vertexShader: glowVertexShader,
      fragmentShader: glowFragmentShader,
      uniforms: {
        uColor: { value: urucum.clone() },
        uIntensity: { value: 0.55 },
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    });
    this.glow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), this.glowMaterial);
    this.glow.position.z = -0.3;
    this.glow.scale.setScalar(ATTENTION_RADIUS * 2.2);
    this.object.add(this.glow);

    const ringGeometry = new THREE.BufferGeometry();
    const ringPoints: number[] = [];
    const segments = 48;
    for (let i = 0; i < segments; i++) {
      const t = (i / segments) * Math.PI * 2;
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

  private updateGlyphs(dt: number): void {
    for (let i = 0; i < this.visibleCount; i++) {
      const glyph = this.glyphs[i];
      glyph.group.rotation.z += glyph.angularVelocity * dt;

      const dx = glyph.x - this.pointerWorld.x;
      const dy = glyph.y - this.pointerWorld.y;
      let target = Math.max(0, 1 - Math.hypot(dx, dy) / ATTENTION_RADIUS);

      for (const ring of this.rings) {
        if (!ring.active) continue;
        const age = this.elapsed - ring.startTime;
        const radius = (age / RING_DURATION) * RING_MAX_RADIUS;
        const distToOrigin = Math.hypot(glyph.x - ring.origin.x, glyph.y - ring.origin.y);
        const band = Math.abs(distToOrigin - radius);
        if (band < RING_BAND) {
          const decay = Math.max(0, 1 - age / RING_DURATION);
          target = Math.max(target, (1 - band / RING_BAND) * decay);
        }
      }

      glyph.attention += (target - glyph.attention) * RESPONSE_LERP;
      glyph.material.color.copy(concreto).lerp(urucum, glyph.attention);
      glyph.material.opacity = 0.4 + glyph.attention * 0.6;
      glyph.group.scale.setScalar(glyph.baseScale * (1 + glyph.attention * 0.35));
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
      const radius = 0.3 + t * (RING_MAX_RADIUS - 0.3);
      ring.mesh.position.copy(ring.origin);
      ring.mesh.scale.setScalar(radius);
      ring.material.opacity = 1 - t;
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
    this.backgroundMaterial.uniforms.uTime.value = this.elapsed;
    this.updateGlyphs(dt);
    this.updateRings();
  }

  resize(): void {
    if (!this.camera) return;
    const bg = this.frustumSizeAt(this.background.position.z);
    this.background.scale.set(bg.width, bg.height, 1);
  }

  degrade(): void {
    const next = Math.max(Math.floor(this.visibleCount * 0.7), 20);
    for (let i = next; i < this.visibleCount; i++) this.glyphs[i].group.visible = false;
    this.visibleCount = next;
  }

  dispose(): void {
    for (const geometry of this.glyphGeometries) geometry.dispose();
    for (const glyph of this.glyphs) glyph.material.dispose();
    this.background.geometry.dispose();
    this.backgroundMaterial.dispose();
    this.glow.geometry.dispose();
    this.glowMaterial.dispose();
    for (const ring of this.rings) ring.material.dispose();
    this.rings[0]?.mesh.geometry.dispose();
  }

  setCamera(camera: THREE.PerspectiveCamera): void {
    this.camera = camera;
  }
}
